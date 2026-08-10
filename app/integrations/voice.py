"""
Professional voice module — server-side speech for the Ceyloria widget.

TTS: Microsoft Edge neural voices via edge-tts (free, no key, ~400ms latency).
STT: faster-whisper (tiny int8) — cached in memory, fast on CPU for short clips.
"""
import io

import edge_tts

# Language → neural voice (professional, natural)
VOICES = {
    "en": "en-US-JennyNeural",
    "ru": "ru-RU-SvetlanaNeural",
    "de": "de-DE-KatjaNeural",
    "fr": "fr-FR-DeniseNeural",
    "si": "si-LK-SameeraNeural",
    "ta": "ta-IN-PallaviNeural",
    "zh": "zh-CN-XiaoxiaoNeural",
}

_MODELS: dict[str, "object"] = {}


def _get_whisper():
    """Lazy-load tiny int8 Whisper once — stays warm in memory (~75MB)."""
    if "whisper" not in _MODELS:
        from faster_whisper import WhisperModel

        _MODELS["whisper"] = WhisperModel("tiny", device="cpu", compute_type="int8")
    return _MODELS["whisper"]


async def synthesize(text: str, language: str = "en") -> bytes:
    """Convert text to MP3 audio bytes using Edge neural voices."""
    voice = VOICES.get(language, VOICES["en"])
    communicate = edge_tts.Communicate(text, voice=voice, rate="+0%")
    buf = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            buf.write(chunk["data"])
    return buf.getvalue()


def transcribe(audio_bytes: bytes, language: str = "en") -> dict:
    """Transcribe audio (wav/mp3/ogg/webm) to text via Whisper.

    Returns {"text": ..., "confidence": float, "clear": bool}
    """
    model = _get_whisper()
    segments, info = model.transcribe(
        io.BytesIO(audio_bytes),
        language=language if language in ("en", "ru") else None,
        beam_size=1,
        vad_filter=True,
    )
    text = "".join(seg.text for seg in segments).strip()

    # Heuristic clarity check: too short or mostly silence → unclear
    avg_logprob = getattr(info, "avg_logprob", 0) or 0
    confidence = max(0.0, min(1.0, (avg_logprob + 1.0) / 2.0))
    word_count = len(text.split())
    clear = word_count >= 2 and confidence >= 0.35
    return {"text": text, "confidence": round(confidence, 3), "clear": clear}
