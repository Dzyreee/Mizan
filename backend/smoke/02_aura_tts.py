"""Smoke test: Aura TTS + RE-VERIFY the available voices (the prior project's voice
list is treated as unconfirmed for Iqra). Produces _out/02_tts.wav.
Run: python smoke/02_aura_tts.py
"""
import _common as c
from app.fanar.client import httpx_client
from app.fanar.models import AURA_TTS

TEXT = "مرحبا يا صغيري، هيا نقرأ معًا."  # "Hello little one, let's read together."
OUT_AUDIO = c.OUT / "02_tts.mp3"   # Aura TTS returns MP3, not WAV (Phase 0 finding)


def main() -> None:
    print(f"[02] Aura TTS, model={AURA_TTS!r}")
    with httpx_client() as cl:
        # Re-verify the voice catalogue.
        r = cl.get("/audio/voices")
        print(f"  GET /audio/voices -> {r.status_code}")
        if r.status_code == 200:
            voices = r.json()
            c.dump("02_voices", voices)
            print(f"  voices payload: {str(voices)[:300]}")
        else:
            print(f"  (voices listing not at /audio/voices: {r.text[:150]})")

        # Synthesize one Arabic line.
        r = cl.post("/audio/speech",
                    json={"model": AURA_TTS, "voice": "Noor", "input": TEXT})
        if r.status_code == 200 and r.content:
            OUT_AUDIO.write_bytes(r.content)
            c.ok(f"voice='Noor' wrote {len(r.content)} bytes -> {OUT_AUDIO}")
        else:
            c.fail(f"TTS failed: {r.status_code} {r.text[:200]}")


if __name__ == "__main__":
    main()
