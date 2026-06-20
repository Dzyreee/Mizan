"""Smoke test: Aura speech-to-text (Arabic). Transcribes the clip produced by 04_aura_tts
(round-trip), so run 04 first. Run: python smoke/05_aura_stt.py
"""
import _common as c

from app.fanar.client import openai_client
from app.fanar.models import AURA_STT

IN_AUDIO = c.OUT / "04_tts.wav"


def main() -> None:
    print(f"[05] Aura STT — model={AURA_STT!r}")
    if not IN_AUDIO.exists():
        c.fail(f"no input audio at {IN_AUDIO} — run smoke/04_aura_tts.py first")
        return
    client = openai_client()
    try:
        with IN_AUDIO.open("rb") as f:
            resp = client.audio.transcriptions.create(model=AURA_STT, file=f)
        text = getattr(resp, "text", None) or str(resp)
        c.dump("05_aura_stt", resp.model_dump() if hasattr(resp, "model_dump") else {"text": text})
        print("  --- transcript ---")
        print("  " + text)
        c.ok("transcription returned text") if text.strip() else c.fail("empty transcript")
    except Exception as e:  # noqa: BLE001
        c.fail(f"OpenAI-SDK transcription shape failed: {e}")
        print("    -> record the correct STT endpoint/shape, then switch this to httpx.")


if __name__ == "__main__":
    main()
