"""Clerk Authentication Integration for Multi-Tenant SaaS."""

import httpx
import logging
from typing import Optional, Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)


class ClerkClient:
    """Clerk API client for authentication and organization management."""

    def __init__(self):
        self.api_key = settings.CLERK_API_KEY
        self.base_url = "https://api.clerk.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def verify_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Verify Clerk session token and return session info."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    f"{self.base_url}/sessions/verify",
                    headers=self.headers,
                    json={"session_token": session_token}
                )
                if resp.status_code == 200:
                    return resp.json()
                logger.warning(f"Clerk session verification failed: {resp.status_code} - {resp.text}")
                return None
        except Exception as e:
            logger.error(f"Clerk session verification error: {e}")
            return None

    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user details from Clerk."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{self.base_url}/users/{user_id}",
                    headers=self.headers
                )
                if resp.status_code == 200:
                    return resp.json()
                return None
        except Exception as e:
            logger.error(f"Clerk get user error: {e}")
            return None

    async def get_organization(self, org_id: str) -> Optional[Dict[str, Any]]:
        """Get organization details from Clerk."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{self.base_url}/organizations/{org_id}",
                    headers=self.headers
                )
                if resp.status_code == 200:
                    return resp.json()
                return None
        except Exception as e:
            logger.error(f"Clerk get organization error: {e}")
            return None

    async def create_organization(self, name: str, slug: str, created_by: str) -> Optional[Dict[str, Any]]:
        """Create a Clerk organization for a new tenant."""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    f"{self.base_url}/organizations",
                    headers=self.headers,
                    json={
                        "name": name,
                        "slug": slug,
                        "created_by": created_by,
                    }
                )
                if resp.status_code in (200, 201):
                    return resp.json()
                logger.error(f"Clerk create organization failed: {resp.status_code} - {resp.text}")
                return None
        except Exception as e:
            logger.error(f"Clerk create organization error: {e}")
            return None

    async def add_user_to_organization(self, org_id: str, user_id: str, role: str = "admin") -> bool:
        """Add a user to a Clerk organization."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    f"{self.base_url}/organizations/{org_id}/memberships",
                    headers=self.headers,
                    json={"user_id": user_id, "role": role}
                )
                return resp.status_code in (200, 201)
        except Exception as e:
            logger.error(f"Clerk add user to organization error: {e}")
            return False

    async def sync_user_metadata(self, user_id: str, public_metadata: Dict = None, private_metadata: Dict = None) -> bool:
        """Sync user metadata with Clerk."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                payload = {}
                if public_metadata:
                    payload["public_metadata"] = public_metadata
                if private_metadata:
                    payload["private_metadata"] = private_metadata
                
                if not payload:
                    return True
                
                resp = await client.patch(
                    f"{self.base_url}/users/{user_id}",
                    headers=self.headers,
                    json=payload
                )
                return resp.status_code == 200
        except Exception as e:
            logger.error(f"Clerk sync user metadata error: {e}")
            return False


class ClerkWebhookHandler:
    """Handle Clerk webhook events for user/organization sync."""

    def __init__(self, clerk_client: ClerkClient):
        self.clerk = clerk_client

    async def handle_user_created(self, data: Dict) -> bool:
        """Handle user.created webhook."""
        user_data = data.get("data", {})
        clerk_id = user_data.get("id")
        email = user_data.get("email_addresses", [{}])[0].get("email_address")
        full_name = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
        
        # The tenant assignment would need to be determined from context
        # This is typically handled via organization membership
        logger.info(f"Clerk user created: {clerk_id} ({email})")
        return True

    async def handle_organization_created(self, data: Dict) -> bool:
        """Handle organization.created webhook."""
        org_data = data.get("data", {})
        org_id = org_data.get("id")
        org_slug = org_data.get("slug")
        name = org_data.get("name")
        
        logger.info(f"Clerk organization created: {org_id} ({org_slug})")
        return True

    async def handle_organization_membership_created(self, data: Dict) -> bool:
        """Handle user added to organization."""
        membership = data.get("data", {})
        org_id = membership.get("organization", {}).get("id")
        user_id = membership.get("public_user_data", {}).get("user_id")
        role = membership.get("role", "member")
        
        logger.info(f"User {user_id} added to org {org_id} as {role}")
        
        # Sync tenant membership in our database
        # This would typically create/update User record with tenant_id
        return True

    async def handle_session_created(self, data: Dict) -> bool:
        """Handle session.created webhook - can be used for analytics."""
        return True


# Singleton instances
clerk_client = ClerkClient()
clerk_webhook = ClerkWebhookHandler(clerk_client)