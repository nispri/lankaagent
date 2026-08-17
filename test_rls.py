import sys
sys.path.insert(0, "/app")
from app.core.config import settings
from app.core.database import async_session_factory
from app.models import tenant
import asyncio

async def verify():
    async with async_session_factory() as session:
        # Create a test tenant
        test_tenant = tenant.Tenant(
            slug="test-tenant",
            name="Test Tenant",
            domain="test.ceyloria.com",
            branding={"primary_color": "#e94560"},
            settings={"language": "en"}
        )
        session.add(test_tenant)
        await session.commit()
        await session.refresh(test_tenant)
        
        # Create a test user
        import uuid
        test_user = tenant.User(
            clerk_id="test_clerk_123",
            tenant_id=test_tenant.id,
            email="test@test.com",
            full_name="Test User",
            role="admin"
        )
        session.add(test_user)
        await session.commit()
        await session.refresh(test_user)
        
        # Test RLS - set tenant context and query
        from sqlalchemy import text
        await session.execute(text(f"SET LOCAL app.current_tenant_id = '{test_tenant.id}'"))
        
        # Query should only return this tenant data
        result = await session.execute(text("SELECT * FROM tenants"))
        tenants = result.fetchall()
        print("Tenants visible:", len(tenants))
        
        result = await session.execute(text("SELECT * FROM users"))
        users = result.fetchall()
        print("Users visible:", len(users))
        
        # Test without tenant context - should see nothing due to RLS
        await session.execute(text("SET LOCAL app.current_tenant_id = '00000000-0000-0000-0000-000000000000'"))
        result = await session.execute(text("SELECT * FROM tenants"))
        tenants = result.fetchall()
        print("Tenants visible without context:", len(tenants))
        
        print("RLS verification complete!")

import asyncio
asyncio.run(verify())
