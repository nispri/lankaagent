#!/usr/bin/env python3
"""
LankaAgent Tenant Provisioning Helper

Usage:
    python provision_tenant.py --branding pilot2_branding.json --output pilot2_widget.html
    python provision_tenant.py --slug "new-operator" --name "New Operator" --color "#1a73e8"

Reads branding questionnaire JSON, creates tenant via API, outputs ready-to-paste widget snippet.
"""

import argparse
import json
import sys
import os
from pathlib import Path
from typing import Optional

import httpx


API_BASE = os.environ.get("LANKAAGENT_API", "http://localhost:8000")
NGROK_BASE = os.environ.get("NGROK_BASE", "https://cycling-handwash-oversweet.ngrok-free.dev")


def create_tenant(
    slug: str,
    name: str,
    domain: Optional[str] = None,
    branding: Optional[dict] = None,
    settings: Optional[dict] = None,
) -> dict:
    """Create tenant via API."""
    url = f"{API_BASE}/api/v1/tenants"
    payload = {
        "slug": slug,
        "name": name,
        "domain": domain,
        "branding": branding or {},
        "settings": settings or {},
    }
    
    with httpx.Client(timeout=30.0) as client:
        resp = client.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()


def get_tenant_branding(slug: str) -> dict:
    """Fetch tenant branding config."""
    url = f"{API_BASE}/api/v1/tenants/{slug}/branding"
    with httpx.Client(timeout=10.0) as client:
        resp = client.get(url)
        resp.raise_for_status()
        return resp.json()


def get_tenant_config(slug: str) -> dict:
    """Fetch full tenant config."""
    url = f"{API_BASE}/api/v1/tenants/{slug}/config"
    with httpx.Client(timeout=10.0) as client:
        resp = client.get(url)
        resp.raise_for_status()
        return resp.json()


def generate_widget_snippet(
    tenant_slug: str,
    brand_name: str,
    primary_color: str,
    use_ngrok: bool = True,
) -> str:
    """Generate floating widget embed snippet."""
    base_url = NGROK_BASE if use_ngrok else f"https://widget.{tenant_slug}.com"
    
    # JavaScript code with braces that need escaping in f-strings
    js_code = """
function toggleChatWidget() {
  const container = document.getElementById('chat-widget-container');
  const toggle = document.getElementById('chat-widget-toggle');
  const openIcon = document.getElementById('chat-open-icon');
  const closeIcon = document.getElementById('chat-close-icon');
  const iframe = document.getElementById('chat-widget-iframe');

  const isOpen = container.style.display !== 'none';

  if (isOpen) {
    container.style.display = 'none';
    openIcon.style.display = 'block';
    closeIcon.style.display = 'none';
    toggle.setAttribute('aria-label', 'Chat with our AI concierge');
    iframe.src = iframe.src;
  } else {
    container.style.display = 'block';
    openIcon.style.display = 'none';
    closeIcon.style.display = 'block';
    toggle.setAttribute('aria-label', 'Close chat');
  }
}

document.addEventListener('click', function(e) {
  const container = document.getElementById('chat-widget-container');
  const toggle = document.getElementById('chat-widget-toggle');
  if (container.style.display !== 'none' && !container.contains(e.target) && !toggle.contains(e.target)) {
    container.style.display = 'none';
    document.getElementById('chat-open-icon').style.display = 'block';
    document.getElementById('chat-close-icon').style.display = 'none';
    toggle.setAttribute('aria-label', 'Chat with our AI concierge');
  }
});
"""
    
    # Build HTML parts separately to avoid f-string brace issues
    html_head = f'''<!-- LANKAAGENT CHAT WIDGET — FLOATING TOGGLE (AUTO-GENERATED) -->
<div id="chat-widget-container" style="position: fixed; bottom: 24px; right: 24px; z-index: 9999; width: 380px; height: 550px; display: none;">
  <iframe
    id="chat-widget-iframe"
    src="{base_url}/widget/iframe/{tenant_slug}"
    style="width: 100%; height: 100%; border: none; border-radius: 16px; box-shadow: 0 8px 40px rgba(0,0,0,0.15); background: white;"
    title="{brand_name} AI Concierge"
    allow="microphone">
  </iframe>
</div>
<button
  id="chat-widget-toggle"
  onclick="toggleChatWidget()"
  aria-label="Chat with our AI concierge"
  style="
    position: fixed;
    bottom: 24px;
    right: 24px;
    z-index: 10000;
    width: 64px;
    height: 64px;
    border-radius: 50%;
    background: {primary_color};
    border: none;
    cursor: pointer;
    box-shadow: 0 8px 30px rgba(0,0,0,.15);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all .3s ease;
  ">
  <svg id="chat-open-icon" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
  </svg>
  <svg id="chat-close-icon" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display: none;">
    <line x1="18" y1="6" x2="6" y2="18"></line>
    <line x1="6" y1="6" x2="18" y2="18"></line>
  </svg>
</button>

<script>
'''

    html_tail = '''
</script>
<!-- END LANKAAGENT CHAT WIDGET -->'''
    
    return html_head + js_code + html_tail


def load_branding_json(path: str) -> dict:
    """Load branding questionnaire JSON."""
    with open(path, 'r') as f:
        return json.load(f)


def branding_to_tenant_payload(branding: dict) -> tuple[dict, dict]:
    """Convert branding questionnaire format to tenant API payload."""
    # Branding fields
    tenant_branding = {
        "primary_color": branding.get("primary_color", "#e94560"),
        "secondary_color": branding.get("secondary_color", "#0F4C44"),
        "logo_url": branding.get("logo_url"),
        "favicon_url": branding.get("favicon_url"),
        "company_name": branding.get("company_name"),
        "welcome_message": branding.get("welcome_message"),
        "subtitle": branding.get("subtitle", "AI Travel Concierge"),
        "placeholder": branding.get("placeholder", "Type your message... or use the mic"),
        "font_family": branding.get("font_family", "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"),
        "border_radius": branding.get("border_radius", "16px"),
        "chat_position": branding.get("chat_position", "bottom-right"),
    }
    # Remove None values
    tenant_branding = {k: v for k, v in tenant_branding.items() if v is not None}
    
    # Settings fields
    tenant_settings = {
        "default_language": branding.get("default_language", "en"),
        "voice_enabled": branding.get("voice_enabled", True),
        "multilingual": branding.get("multilingual", True),
        "wellness_upsell": branding.get("wellness_upsell", True),
        "lead_capture": branding.get("lead_capture", True),
        "mcp_enabled": branding.get("mcp_enabled", True),
    }
    
    return tenant_branding, tenant_settings


def main():
    parser = argparse.ArgumentParser(description="Provision LankaAgent tenant + generate widget snippet")
    
    # Input methods
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--branding", help="Path to branding questionnaire JSON")
    input_group.add_argument("--slug", help="Tenant slug (for manual mode)")
    
    # Manual mode args
    parser.add_argument("--name", help="Company name (manual mode)")
    parser.add_argument("--color", help="Primary color hex (manual mode)", default="#e94560")
    parser.add_argument("--domain", help="Custom domain (optional)")
    parser.add_argument("--lang", help="Default language", default="en")
    
    # Output
    parser.add_argument("--output", help="Output widget HTML file")
    parser.add_argument("--use-production-url", action="store_true", help="Use custom domain instead of ngrok")
    
    args = parser.parse_args()
    
    try:
        if args.branding:
            # Load from questionnaire JSON
            print(f"Loading branding from {args.branding}...")
            bq = load_branding_json(args.branding)
            
            slug = bq.get("tenant_slug") or bq.get("company_name", "").lower().replace(" ", "-")
            name = bq.get("company_name") or bq.get("brand_name") or slug
            domain = bq.get("website")
            
            branding_dict, settings_dict = branding_to_tenant_payload(bq)
            primary_color = branding_dict.get("primary_color", "#e94560")
            brand_name = branding_dict.get("company_name") or name
            
        else:
            # Manual mode
            if not args.name:
                parser.error("--name required when using --slug")
            slug = args.slug
            name = args.name
            domain = args.domain
            branding_dict = {
                "primary_color": args.color,
                "company_name": name,
            }
            settings_dict = {"default_language": args.lang}
            primary_color = args.color
            brand_name = name
        
        print(f"Creating tenant: {name} ({slug})...")
        tenant = create_tenant(slug, name, domain, branding_dict, settings_dict)
        print(f"Tenant created: {tenant.get('id')}")
        
        # Verify branding
        print("Verifying branding config...")
        branding = get_tenant_branding(slug)
        config = get_tenant_config(slug)
        print(f"Branding verified: {branding.get('company_name')}")
        
        # Generate widget
        print("Generating widget snippet...")
        snippet = generate_widget_snippet(
            tenant_slug=slug,
            brand_name=brand_name,
            primary_color=primary_color,
            use_ngrok=not args.use_production_url,
        )
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(snippet)
            print(f"Widget snippet saved to {args.output}")
        else:
            print("\n" + "="*60)
            print("WIDGET SNIPPET (copy/paste before </body>):")
            print("="*60)
            print(snippet)
            print("="*60)
        
        # Summary
        print(f"\nTENANT SUMMARY")
        print(f"   Slug: {slug}")
        print(f"   Name: {name}")
        print(f"   Widget URL: {NGROK_BASE}/widget/iframe/{slug}")
        print(f"   Config API: {API_BASE}/api/v1/tenants/{slug}/config")
        print(f"   Branding API: {API_BASE}/api/v1/tenants/{slug}/branding")
        print(f"   Direct Chat: {NGROK_BASE}/widget/{slug}")
        
        return 0
        
    except httpx.HTTPStatusError as e:
        print(f"API Error ({e.response.status_code}): {e.response.text}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())