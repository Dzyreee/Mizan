"""Find valid TTS voices + correct request shape. Tries voice-listing endpoints and
a few candidate voice names against both TTS models."""
import _common as c
from app.fanar.client import httpx_client
from app.fanar.models import AURA_TTS, SADIQ_TTS


def main():
    with httpx_client() as cl:
        for path in ("/audio/voices", "/voices", "/audio/speech/voices"):
            r = cl.get(path)
            print(f"GET {path} -> {r.status_code}: {r.text[:200]}")

        # Candidate voices against both TTS models; capture any 422 enum hint.
        candidates = ["ar-QA-female", "female", "male", "ar-female", "Aura", "default", "1"]
        for model in (AURA_TTS, SADIQ_TTS):
            for v in candidates:
                r = cl.post("/audio/speech", json={"model": model, "voice": v, "input": "اختبار"})
                tag = "OK" if r.status_code == 200 else r.text[:160]
                print(f"POST /audio/speech model={model} voice={v!r} -> {r.status_code} {tag}")
                if r.status_code == 200:
                    print("   ^^ WORKING voice found")
                    return


if __name__ == "__main__":
    main()
