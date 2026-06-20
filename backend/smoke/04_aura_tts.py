"""Smoke test: Aura text-to-speech (Arabic). Produces _out/04_tts.wav, which 05_aura_stt
reads back for a round-trip check. Run: python smoke/04_aura_tts.py

Tries the OpenAI-SDK audio.speech shape first; if Fanar's endpoint differs, the live
run will show the error and we switch to the discovered shape via httpx.
"""
import _common as c

from app.fanar.client import openai_client
from app.fanar.models import AURA_TTS

TEXT = "السلام عليكم، هذه تجربة صوتية لنظام ميزان لحساب المواريث."
OUT_AUDIO = c.OUT / "04_tts.wav"


def main() -> None:
    print(f"[04] Aura TTS — model={AURA_TTS!r}")
    client = openai_client()
    try:
        with client.audio.speech.with_streaming_response.create(
            model=AURA_TTS,
            voice="Noor",   # Arabic voices: Noor/Huda/Radwa (F), Jasim/Hamad/Abdulrahman (M)
            input=TEXT,
        ) as resp:
            resp.stream_to_file(OUT_AUDIO)
        size = OUT_AUDIO.stat().st_size
        if size > 0:
            c.ok(f"wrote {size} bytes -> {OUT_AUDIO}")
        else:
            c.fail("audio file is empty")
    except Exception as e:  # noqa: BLE001
        c.fail(f"OpenAI-SDK speech shape failed: {e}")
        print("    -> record the correct TTS endpoint/shape, then switch this to httpx.")


if __name__ == "__main__":
    main()
