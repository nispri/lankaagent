# Widget Embed Snippet — Copy/Paste for Pilot Partner

## Option A: Floating Toggle Button (Recommended)
*Paste before `</body>` on every page where widget should appear.*

```html
<!-- LANKAAGENT CHAT WIDGET — FLOATING TOGGLE -->
<div id="chat-widget-container" style="position: fixed; bottom: 24px; right: 24px; z-index: 9999; width: 380px; height: 550px; display: none;">
  <iframe
    id="chat-widget-iframe"
    src="https://cycling-handwash-oversweet.ngrok-free.dev/widget/iframe/{TENANT_SLUG}"
    style="width: 100%; height: 100%; border: none; border-radius: 16px; box-shadow: 0 8px 40px rgba(0,0,0,0.15); background: white;"
    title="{BRAND_NAME} AI Concierge"
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
    background: {PRIMARY_COLOR};
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
    iframe.src = iframe.src; // reload on reopen
  } else {
    container.style.display = 'block';
    openIcon.style.display = 'none';
    closeIcon.style.display = 'block';
    toggle.setAttribute('aria-label', 'Close chat');
  }
}

// Close when clicking outside
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
</script>
<!-- END LANKAAGENT CHAT WIDGET -->
```

---

## Option B: Inline Embed (Fixed Position)
*Use if you want the chat permanently visible in a page section.*

```html
<!-- LANKAAGENT CHAT WIDGET — INLINE EMBED -->
<div style="width: 100%; max-width: 420px; margin: 2rem auto;">
  <iframe
    src="https://cycling-handwash-oversweet.ngrok-free.dev/widget/iframe/{TENANT_SLUG}"
    style="width: 100%; height: 600px; border: none; border-radius: 16px; box-shadow: 0 4px 24px rgba(0,0,0,0.1); background: white;"
    title="{BRAND_NAME} AI Concierge"
    allow="microphone">
  </iframe>
</div>
<!-- END LANKAAGENT CHAT WIDGET -->
```

---

## Option C: Direct Page Link (No Embed)
*Share as a standalone chat page — useful for WhatsApp/email campaigns.*

```
https://cycling-handwash-oversweet.ngrok-free.dev/widget/{TENANT_SLUG}
```

---

## Placeholder Values to Replace

| Placeholder | Example | Source |
|-------------|---------|--------|
| `{TENANT_SLUG}` | `ceyloria-holidays` | Provided after tenant creation |
| `{BRAND_NAME}` | `Ceyloria Holidays` | Branding questionnaire |
| `{PRIMARY_COLOR}` | `#e94560` | Branding questionnaire (hex) |

---

## Quick Test After Embedding

1. Open the page in incognito/private browser
2. Click the floating button (bottom-right)
3. Verify:
   - [ ] Iframe loads with your branding (colors, logo, welcome message)
   - [ ] Type "Hello" → get AI response in <3 seconds
   - [ ] Try voice input (mic button) if enabled
   - [ ] Switch language → response translates
   - [ ] Close/reopen → widget reloads cleanly

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Widget shows "Tenant not found" | Verify `{TENANT_SLUG}` matches exactly (case-sensitive) |
| Colors don't match | Clear browser cache; branding updates take ~30s to propagate |
| Mic button missing | Ensure `allow="microphone"` on iframe; HTTPS required for mic |
| Widget doesn't open | Check z-index conflicts; ensure no `overflow: hidden` on parent |
| Mobile layout broken | Test on phone; iframe is responsive but container needs `width: 100%` |

---

## Production Migration (Post-Pilot)

When pilot converts to paid, we'll migrate to your custom domain:

```html
<!-- PRODUCTION VERSION (after custom domain setup) -->
src="https://widget.{YOUR_DOMAIN}/widget/iframe/{TENANT_SLUG}"
```

- SSL certificate managed by LankaAgent
- No code changes needed — just update the `src` URL
- Ngrok URL continues working as fallback