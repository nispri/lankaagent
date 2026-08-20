"""LankaAgent Chat Widget — Embeddable Chat Widget for Websites"""
import json

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

router = APIRouter()
templates = Jinja2Templates(directory="app/integrations/chat_widget/templates")

# Session storage: Redis primary (24h TTL), in-memory fallback if Redis is down.
# The in-memory dict keeps working during Redis outages so guests are never blocked.
_conversations: dict[str, list[dict[str, str]]] = {}
_SESSION_TTL = 24 * 60 * 60  # 24-hour context window per SPEC Sprint 1


async def _load_history(session_id: str) -> list[dict[str, str]]:
    """Load conversation history — Redis first, in-memory fallback."""
    try:
        from app.core.redis import redis_client

        raw = await redis_client.get(f"session:{session_id}")
        if raw:
            data = json.loads(raw)
            return data if isinstance(data, list) else []
        return _conversations.get(session_id, [])
    except Exception:
        # Redis unavailable — fall back to in-memory so the guest is never blocked
        return _conversations.get(session_id, [])


async def _save_history(session_id: str, history: list[dict[str, str]]) -> None:
    """Save conversation history — Redis with 24h TTL, in-memory fallback."""
    _conversations[session_id] = history
    try:
        from app.core.redis import redis_client

        await redis_client.set(
            f"session:{session_id}", json.dumps(history), ex=_SESSION_TTL
        )
    except Exception:
        pass  # in-memory copy already saved; Redis will re-sync on next load


class ChatMessage(BaseModel):
    message: str
    language: str = "en"
    session_id: str | None = None
    tenant_slug: str | None = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    language: str = "en"


@router.get("/embed", response_class=HTMLResponse)
async def embed_widget(request: Request) -> HTMLResponse:  # noqa: ARG001
    """Embeddable chat widget for websites (page-level, with toggle button)"""
    from fastapi.responses import HTMLResponse

    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ceyloria Holidays - Chat Widget</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: transparent; }

        .chat-widget {
            position: fixed;
            bottom: 24px;
            right: 24px;
            z-index: 9999;
            font-family: inherit;
        }

        .chat-toggle {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: #e94560;
            border: none;
            cursor: pointer;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            display: flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.2s, box-shadow 0.2s;
            z-index: 10000;
        }

        .chat-toggle:hover {
            transform: scale(1.05);
            box-shadow: 0 6px 28px rgba(0,0,0,0.2);
        }

        .chat-toggle svg {
            width: 28px;
            height: 28px;
            color: white;
        }

        .chat-toggle .close-icon { display: none; }
        .chat-widget.open .chat-toggle .open-icon { display: none; }
        .chat-widget.open .chat-toggle .close-icon { display: block; }

        .chat-window {
            position: absolute;
            bottom: 80px;
            right: 0;
            width: 380px;
            height: 550px;
            background: white;
            border-radius: 16px;
            box-shadow: 0 8px 40px rgba(0,0,0,0.15);
            display: none;
            flex-direction: column;
            overflow: hidden;
            border: 1px solid rgba(0,0,0,0.08);
        }

        .chat-widget.open .chat-window {
            display: flex;
            animation: slideUp 0.3s ease;
        }

        @keyframes slideUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .chat-header {
            background: #e94560;
            color: white;
            padding: 16px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .chat-header-info h3 {
            font-size: 16px;
            font-weight: 600;
            margin: 0;
        }

        .chat-header-info p {
            font-size: 12px;
            opacity: 0.9;
            margin: 2px 0 0;
        }

        .chat-header-actions button {
            background: none;
            border: none;
            color: white;
            cursor: pointer;
            padding: 8px;
            border-radius: 8px;
            transition: background 0.2s;
        }

        .chat-header-actions button:hover {
            background: rgba(255,255,255,0.15);
        }

        .chat-header-actions .voice-toggle.on svg {
                    color: #7CFC9A;
                }

                .chat-header-actions .voice-toggle:not(.on) svg {
                    color: rgba(255,255,255,0.4);
                }

                /* Language selector dropdown */
                .language-selector {
                    position: absolute;
                    top: 100%;
                    right: 0;
                    background: white;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                    min-width: 160px;
                    display: none;
                    z-index: 10001;
                    overflow: hidden;
                    border-radius: 8px;
                }

                .language-selector.open { display: block; }

                .language-option {
                    padding: 10px 16px;
                    cursor: pointer;
                    font-size: 14px;
                    color: #333;
                    transition: background 0.15s;
                }

                .language-option:hover {
                    background: #f5f5f5;
                }

        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 12px;
            background: #f8f9fa;
        }

        .message {
            max-width: 80%;
            padding: 12px 16px;
            border-radius: 16px;
            font-size: 14px;
            line-height: 1.5;
            animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .message.bot {
            background: white;
            border-radius: 16px 16px 16px 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            align-self: flex-start;
        }

        .message.user {
            background: #e94560;
            color: white;
            border-radius: 16px 16px 4px 16px;
            align-self: flex-end;
        }

        .message.system {
            background: #fff3cd;
            color: #856404;
            font-size: 12px;
            border-radius: 8px;
            align-self: center;
            max-width: 90%;
        }

        .message-time {
            font-size: 10px;
            opacity: 0.6;
            margin-top: 4px;
            text-align: right;
        }

        .message.bot .message-time { text-align: left; }

        .typing-indicator {
            display: flex;
            gap: 4px;
            padding: 8px 16px;
        }

        .typing-indicator span {
            width: 8px;
            height: 8px;
            background: #e94560;
            border-radius: 50%;
            animation: bounce 1.4s infinite ease-in-out;
        }

        .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
        .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }

        .chat-input-area {
            padding: 12px 16px;
            background: white;
            border-top: 1px solid #eee;
            display: flex;
            gap: 8px;
            align-items: flex-end;
        }

        .chat-input-wrapper {
            flex: 1;
            position: relative;
        }

        .chat-input {
            width: 100%;
            border: 1px solid #e0e0e0;
            border-radius: 24px;
            padding: 12px 48px 12px 16px;
            font-size: 14px;
            outline: none;
            resize: none;
            max-height: 120px;
            font-family: inherit;
            transition: border-color 0.2s;
        }

        .chat-input:focus {
            border-color: #e94560;
        }

        .send-button {
            width: 44px;
            height: 44px;
            border-radius: 50%;
            background: #e94560;
            border: none;
            color: white;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.2s, background 0.2s;
            flex-shrink: 0;
        }

        .send-button:hover {
            transform: scale(1.05);
        }

        .send-button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .mic-button {
            width: 44px;
            height: 44px;
            border-radius: 50%;
            background: var(--teal-700, #0F4C44);
            border: none;
            color: white;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.2s, background 0.2s;
            flex-shrink: 0;
        }

        .mic-button:hover {
            transform: scale(1.05);
        }

        .mic-button.listening {
            background: #e94560;
            animation: pulse 1.2s ease-in-out infinite;
        }

        @keyframes pulse {
            0%, 100% { box-shadow: 0 0 0 0 rgba(233, 69, 96, 0.5); }
            50% { box-shadow: 0 0 0 12px rgba(233, 69, 96, 0); }
        }

        @media (max-width: 480px) {
            .chat-window {
                width: 100vw;
                height: 100vh;
                bottom: 0;
                right: 0;
                border-radius: 16px 16px 0 0;
            }

            .chat-toggle {
                bottom: 16px;
                right: 16px;
            }

            .chat-window {
                bottom: 72px;
            }
        }
    </style>
</head>
<body>
    <div class="chat-widget" id="chatWidget">
        <button class="chat-toggle" id="chatToggle" aria-label="Open chat">
            <svg class="open-icon" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
            <svg class="close-icon" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
        </button>

        <div class="chat-window" id="chatWindow">
            <div class="chat-header">
                <div class="chat-header-info">
                    <h3>Ceyloria Holidays</h3>
                    <p>AI Travel Concierge</p>
                </div>
                <div class="chat-header-actions">
                    <button id="voiceToggle" aria-label="Toggle voice replies" title="Voice replies: ON" class="voice-toggle on">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                            <path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path>
                            <path d="M19.07 4.93a10 10 0 0 1 0 14.14"></path>
                        </svg>
                    </button>
                    <button id="languageBtn" aria-label="Change language" title="Language">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="12" cy="12" r="10"></circle>
                            <line x1="2" y1="12" x2="22" y2="12"></line>
                            <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
                        </svg>
                    </button>
                    <button id="closeChat" aria-label="Close chat">
                                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                                <line x1="18" y1="6" x2="6" y2="18"></line>
                                                <line x1="6" y1="6" x2="18" y2="18"></line>
                                            </svg>
                                        </button>
                                    </div>

                                    <!-- Language Selector Dropdown -->
                                    <div class="language-selector" id="languageSelector">
                                        <div class="language-option" data-lang="en">🇬🇧 English</div>
                                        <div class="language-option" data-lang="ru">🇷🇺 Русский</div>
                                        <div class="language-option" data-lang="de">🇩🇪 Deutsch</div>
                                        <div class="language-option" data-lang="fr">🇫🇷 Français</div>
                                        <div class="language-option" data-lang="zh">🇨🇳 中文</div>
                                        <div class="language-option" data-lang="si">🇱🇰 සිංහල</div>
                                        <div class="language-option" data-lang="ta">🇱🇰 தமிழ்</div>
                                    </div>
                                </div>

                                <div class="chat-messages" id="chatMessages">
                <div class="message bot">
                    <div>Hello! 🇱🇰 Welcome to Ceyloria Holidays! How can I help you plan your Sri Lanka trip?</div>
                    <div class="message-time">Just now</div>
                </div>
            </div>

            <div class="typing-indicator" id="typingIndicator" style="display: none;">
                <span></span><span></span><span></span>
            </div>

            <div class="chat-input-area">
                <div class="chat-input-wrapper">
                    <textarea
                        class="chat-input"
                        id="chatInput"
                        placeholder="Type your message... or use the mic"
                        rows="1"
                        aria-label="Type your message"
                    ></textarea>
                </div>
                <button class="mic-button" id="micButton" aria-label="Voice input" title="Speak your message">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                        <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                        <line x1="12" y1="19" x2="12" y2="23"></line>
                        <line x1="8" y1="23" x2="16" y2="23"></line>
                    </svg>
                </button>
                <button class="send-button" id="sendButton" aria-label="Send message">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="22" y1="2" x2="11" y2="13"></line>
                        <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                    </svg>
                </button>
            </div>
        </div>
    </div>

    <script>
        (function() {
            const widget = document.getElementById('chatWidget');
            const toggle = document.getElementById('chatToggle');
            const window = document.getElementById('chatWindow');
            const closeBtn = document.getElementById('closeChat');
            const input = document.getElementById('chatInput');
            const sendBtn = document.getElementById('sendButton');
            const messages = document.getElementById('chatMessages');
            const typing = document.getElementById('typingIndicator');

            const config = {
                apiBase: '/widget',
                tenantSlug: 'ceyloria-holidays',
                primaryColor: '#e94560',
                welcomeMessage: 'Hello! 🇱🇰 Welcome to Ceyloria Holidays! How can I help you plan your Sri Lanka trip?',
    """
    return HTMLResponse(content=html_content)


@router.get("/iframe/{tenant_slug}", response_class=HTMLResponse)
async def iframe_widget(request: Request, tenant_slug: str) -> HTMLResponse:
    """Iframe-embeddable chat window (always open, no outer toggle)"""
    from app.core.database import async_session_factory
    from app.models import get_tenant_by_slug

    async with async_session_factory() as db:
        tenant = await get_tenant_by_slug(db, tenant_slug)

        if not tenant:
            # Fallback to default if tenant not found
            return templates.TemplateResponse(
                request=request,
                name="widget_embed.html",
                context={
                    "tenant_slug": tenant_slug,
                    "api_base": "/api/v1",
                    "widget_title": "Ceyloria Holidays",
                    "widget_subtitle": "AI Travel Concierge",
                    "welcome_message": "Hello! 🇱🇰 Welcome to Ceyloria Holidays! How can I help you plan your Sri Lanka trip?",
                    "placeholder": "Type your message... or use the mic",
                    "primary_color": "#e94560",
                },
            )

        branding = tenant.branding or {}

        # Extract individual values (without request - it goes as first param)
        context = {
            "tenant_slug": tenant_slug,
            "api_base": "/api/v1",
            "widget_title": tenant.name,
            "widget_subtitle": branding.get("subtitle", "AI Travel Concierge"),
            "welcome_message": branding.get("welcome_message", f"Hello! 🇱🇰 Welcome to {tenant.name}! How can I help you plan your Sri Lanka trip?"),
            "placeholder": branding.get("placeholder", "Type your message... or use the mic"),
            "primary_color": branding.get("primary_color", "#e94560"),
        }

        return templates.TemplateResponse(
            request=request,
            name="widget_embed.html",
            context=context,
        )


@router.get("/{tenant_slug}", response_class=HTMLResponse)
async def tenant_widget(request: Request, tenant_slug: str) -> HTMLResponse:
    """Tenant-specific embeddable chat widget with dynamic branding"""
    from app.core.database import async_session_factory
    from app.models import get_tenant_by_slug

    async with async_session_factory() as db:
        tenant = await get_tenant_by_slug(db, tenant_slug)

        if not tenant:
            # Fallback to default if tenant not found
            return templates.TemplateResponse(
                request=request,
                name="widget_embed.html",
                context={
                    "tenant_slug": tenant_slug,
                    "api_base": "/widget",
                    "widget_title": "Ceyloria Holidays",
                    "widget_subtitle": "AI Travel Concierge",
                    "welcome_message": "Hello! 🇱🇰 Welcome to Ceyloria Holidays! How can I help you plan your Sri Lanka trip?",
                    "placeholder": "Type your message... or use the mic",
                    "primary_color": "#e94560",
                },
            )

        branding = tenant.branding or {}

        # Extract individual values
        context = {
            "tenant_slug": tenant_slug,
            "api_base": "/widget",
            "widget_title": tenant.name,
            "widget_subtitle": branding.get("subtitle", "AI Travel Concierge"),
            "welcome_message": branding.get("welcome_message", f"Hello! 🇱🇰 Welcome to {tenant.name}! How can I help you plan your Sri Lanka trip?"),
            "placeholder": branding.get("placeholder", "Type your message... or use the mic"),
            "primary_color": branding.get("primary_color", "#e94560"),
        }

        return templates.TemplateResponse(
            request=request,
            name="widget_embed.html",
            context=context,
        )


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(message: ChatMessage):
    """Chat endpoint for widget."""
    from app.integrations.llm_chat import get_engine
    from app.core.database import async_session_factory
    from app.models import get_tenant_by_slug

    engine = get_engine()

    # Load history
    session_id = message.session_id or f"session_{int(__import__('time').time())}"
    history = await _load_history(session_id)

    # Build tenant-aware system context if tenant_slug provided
    tenant_context = None
    if message.tenant_slug:
        async with async_session_factory() as db:
            tenant = await get_tenant_by_slug(db, message.tenant_slug)
            if tenant:
                branding = tenant.branding or {}
                company_name = tenant.name
                welcome_msg = branding.get("welcome_message", f"Hello! 🇱🇰 Welcome to {company_name}! How can I help you plan your Sri Lanka trip?")
                tenant_context = f"You are the AI concierge for {company_name}. {welcome_msg} Your responses should reflect this brand identity."

    # Get response from engine with tenant context
    if tenant_context and history and history[0].get("role") == "system":
        # Replace existing system message
        history[0]["content"] = tenant_context
    elif tenant_context:
        # Prepend system context
        history = [{"role": "system", "content": tenant_context}] + history

    result = await engine.chat(message.message, message.language, history, tenant_context=tenant_context)

    # Save updated history
    new_history = history + [
        {"role": "user", "content": message.message},
        {"role": "assistant", "content": result},
    ]
    await _save_history(session_id, new_history)

    return ChatResponse(response=result, session_id=session_id, language=message.language)


@router.post("/stt")
async def speech_to_text(request: Request):
    """Transcribe uploaded audio (wav/mp3/ogg/webm) to text."""
    from app.integrations.voice import transcribe

    audio_bytes = await request.body()
    if not audio_bytes:
        return {"text": ""}
    language = request.query_params.get("language", "en")
    try:
        return transcribe(audio_bytes, language)
    except Exception:
        logger = __import__("logging").getLogger("lankaagent")
        logger.exception("STT failed")
        return {"text": "", "confidence": 0.0, "clear": False, "error": "transcription_failed"}


@router.post("/tts")
async def text_to_speech(request: Request):
    """Convert text to speech audio."""
    import json as _json
    body = await request.body()
    try:
        data = _json.loads(body) if body else {}
    except Exception:
        data = {}
    text = data.get("text", "")
    language = data.get("language", "en")
    if not text:
        return {"audio_url": "", "error": "no_text"}
    try:
        from app.integrations.voice import synthesize
        audio_url = await synthesize(text, language)
        return {"audio_url": audio_url}
    except Exception:
        logger = __import__("logging").getLogger("lankaagent")
        logger.exception("TTS failed")
        return {"audio_url": "", "error": "synthesis_failed"}


@router.get("/config")
async def widget_config():
    """Widget configuration endpoint."""
    return {
        "api_base": "/widget",
        "widget_endpoint": "/widget/chat",
        "supported_languages": ["en", "ru", "de", "fr", "zh", "si", "ta"],
        "default_language": "en",
    }