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


class ChatResponse(BaseModel):
    response: str
    session_id: str
    language: str = "en"


@router.get("/embed", response_class=HTMLResponse)
async def embed_widget(request: Request) -> HTMLResponse:  # noqa: ARG001
    """Embeddable chat widget for websites"""
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
                placeholder: 'Type your message... or use the mic',
                voiceOutput: true
            };

            let sessionId = 'session_' + Math.random().toString(36).substr(2, 9);
            let currentLanguage = 'en';
            let isProcessing = false;

            function toggleChat() {
                widget.classList.toggle('open');
                if (widget.classList.contains('open')) {
                    input.focus();
                }
            }

            toggle.addEventListener('click', toggleChat);
            closeBtn.addEventListener('click', toggleChat);

            function addMessage(content, isUser = false, lang = 'en') {
                const div = document.createElement('div');
                div.className = 'message ' + (isUser ? 'user' : 'bot');
                const time = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
                div.innerHTML = content + (isUser ? '' : '<div class="message-time">' + lang.toUpperCase() + ' • ' + time + '</div>');
                chatMessages.appendChild(div);
                chatMessages.scrollTop = chatMessages.scrollHeight;
                // Speak AI replies aloud (voice output)
                if (!isUser && config.voiceOutput) {
                    speak(content, lang);
                }
            }

            /* ── TEXT-TO-SPEECH (server-side Edge neural voice) ── */
            const voiceToggleBtn = document.getElementById('voiceToggle');
            let voiceOutputEnabled = true;   // default ON
            let audioPlayer = new Audio();

            function speak(text, lang) {
                if (!voiceOutputEnabled) return;
                try {
                    audioPlayer.pause();
                    audioPlayer.src = '/widget/tts?text=' + encodeURIComponent(text) + '&language=' + encodeURIComponent(lang || 'en');
                    audioPlayer.play().catch(e => console.warn('TTS play failed:', e));
                } catch (e) {
                    console.warn('TTS failed:', e);
                }
            }

            // Speaker toggle (header)
            if (voiceToggleBtn) {
                voiceToggleBtn.addEventListener('click', () => {
                    voiceOutputEnabled = !voiceOutputEnabled;
                    voiceToggleBtn.classList.toggle('on', voiceOutputEnabled);
                    voiceToggleBtn.title = voiceOutputEnabled ? 'Voice replies: ON' : 'Voice replies: OFF';
                    if (!voiceOutputEnabled) audioPlayer.pause();
                });
            }

            function showTyping() {
                typing.style.display = 'flex';
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }

            function hideTyping() {
                typing.style.display = 'none';
            }

            async function sendMessage() {
                const text = input.value.trim();
                if (!text || isProcessing) return;

                isProcessing = true;
                sendBtn.disabled = true;

                addMessage(text, true);
                input.value = '';
                input.style.height = 'auto';
                showTyping();

                try {
                    const response = await fetch('/widget/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            message: text,
                            language: currentLanguage,
                            session_id: sessionId
                        })
                    });

                    const data = await response.json();
                    hideTyping();
                    addMessage(data.response, false, data.language || 'en');
                } catch (error) {
                    hideTyping();
                    addMessage('Sorry, I encountered an error. Please try again.', 'bot');
                } finally {
                    isProcessing = false;
                    sendBtn.disabled = false;
                }
            }

            sendBtn.addEventListener('click', sendMessage);

            /* ── VOICE INPUT (MediaRecorder → server Whisper STT) ── */
            const micBtn = document.getElementById('micButton');
            let mediaRecorder = null;
            let audioChunks = [];
            let isListening = false;

            async function startRecording() {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
                    audioChunks = [];
                    mediaRecorder.ondataavailable = e => { if (e.data.size > 0) audioChunks.push(e.data); };
                    mediaRecorder.onstop = async () => {
                        stream.getTracks().forEach(t => t.stop());
                        const blob = new Blob(audioChunks, { type: 'audio/webm' });
                        await transcribeAudio(blob);
                    };
                    mediaRecorder.start();
                    isListening = true;
                    micBtn.classList.add('listening');
                    micBtn.title = 'Listening... click to stop';
                } catch (e) {
                    console.error('Mic error:', e);
                    let msg = 'Could not access the microphone. Please allow mic access in your browser settings.';
                    if (e && e.name === 'NotAllowedError') {
                        msg = 'Microphone access was denied. Click the lock icon in the address bar → Site settings → allow Microphone, then refresh and try again.';
                    } else if (e && e.name === 'NotFoundError') {
                        msg = 'No microphone was found. Please connect a mic and try again.';
                    } else if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                        msg = 'This browser does not support voice input. Please use Chrome or Edge.';
                    }
                    addMessage(msg, 'bot');
                    stopListening();
                }
            }

            async function transcribeAudio(blob) {
                showTyping();
                try {
                    // Send raw audio bytes (not multipart) so the server can decode directly
                    const resp = await fetch('/widget/stt?language=en', {
                        method: 'POST',
                        headers: { 'Content-Type': 'audio/webm' },
                        body: blob
                    });
                    const data = await resp.json();
                    hideTyping();
                    const transcript = (data.text || '').trim();
                    const isClear = data.clear !== false && transcript.length >= 2;

                    if (!isClear) {
                        // Voice unclear → Anuki asks a clarifying question (server persona rule 8)
                        sendVoiceClarify();
                        return;
                    }
                    if (transcript) {
                        input.value = transcript;
                        sendMessage();
                    }
                } catch (e) {
                    hideTyping();
                    console.error('STT error:', e);
                    addMessage('Sorry, I did not quite catch that. Could you repeat a little more clearly?', 'bot');
                }
            }

            async function sendVoiceClarify() {
                // Ask Anuki (LLM) for a polite clarifying question — keeps persona & language consistent
                try {
                    const resp = await fetch('/widget/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            message: '[Unclear voice input - please ask the guest to repeat their request more clearly, in one short polite sentence]',
                            language: currentLanguage,
                            session_id: sessionId
                        })
                    });
                    const data = await resp.json();
                    addMessage(data.response || 'I am sorry, I did not quite catch that. Could you say it again, please?', false, data.language || 'en');
                } catch (e) {
                    addMessage('I am sorry, I did not quite catch that. Could you say it again, please?', 'bot');
                }
            }

            function stopListening() {
                isListening = false;
                micBtn.classList.remove('listening');
                micBtn.title = 'Speak your message';
                if (mediaRecorder && mediaRecorder.state !== 'inactive') {
                    mediaRecorder.stop();
                }
            }

            micBtn.addEventListener('click', () => {
                if (isListening) {
                    stopListening();
                } else {
                    startRecording();
                }
            });

            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                }
            });

            input.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = Math.min(this.scrollHeight, 120) + 'px';
            });

            if (widget.classList.contains('open')) {
                input.focus();
            }
        })();
    </script>
</body>
</html>
"""

    return HTMLResponse(content=html_content)



@router.post("/chat", response_model=dict)
async def chat_endpoint(message: dict) -> dict:
    """Real AI chat endpoint — OpenRouter LLM with tour knowledge + session memory"""
    from app.integrations.llm_chat import get_engine

    message_text = message.get("message", "")
    language = message.get("language", "en")
    session_id = message.get("session_id") or f"anon-{hash(message_text) % 100000}"

    # Conversation memory per session (Redis with 24h TTL; in-memory fallback)
    history = await _load_history(session_id)

    engine = get_engine()
    reply = await engine.chat(message_text, language=language, history=history)

    # Guard against empty replies — never leave the guest hanging
    if not reply or not reply.strip():
        reply = "I'm sorry, I didn't quite catch that. Could you say it again, please?"

    # Store this turn
    history.append({"role": "user", "content": message_text})
    history.append({"role": "assistant", "content": reply})
    if len(history) > 20:
        history = history[-20:]
    await _save_history(session_id, history)

    # Simple language detect for the widget label
    lang = "ru" if any(ord(c) > 1024 for c in message_text) else "en"
    return {"response": reply, "language": lang, "session_id": session_id}


@router.get("/config")
async def widget_config() -> dict:
    """Widget configuration"""
    return {
        "api_base": "/api/v1",
        "widget_endpoint": "/widget/chat",
        "supported_languages": ["en", "ru", "de", "fr", "zh", "si", "ta"],
        "default_language": "en",
    }


@router.get("/tts")
async def text_to_speech(text: str, language: str = "en"):
    """Convert text to MP3 audio (Edge neural voice)."""
    from app.integrations.voice import synthesize
    from fastapi.responses import Response

    audio = await synthesize(text, language)
    return Response(
        content=audio,
        media_type="audio/mpeg",
        headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no"},
    )


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

@router.get("/{tenant_slug}", response_class=HTMLResponse)
async def tenant_widget(request: Request, tenant_slug: str) -> HTMLResponse:
    """Tenant-specific widget"""
    return templates.TemplateResponse(
        "widget_embed.html",
        {
            "request": request,
            "tenant_slug": tenant_slug,
            "api_base": "/api/v1",
            "widget_title": "Ceyloria Holidays",
            "widget_subtitle": "AI Travel Concierge",
            "welcome_message": "Hello! 🇱🇰 Welcome to Ceyloria Holidays! How can I help you plan your Sri Lanka trip?",
            "placeholder": "Type your message...",
            "primary_color": "#e94560",
        },
    )

