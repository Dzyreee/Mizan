"""Smoke test: Shaheen Arabic->English translation.

Public sources show a dedicated, non-OpenAI-shaped endpoint: POST /v1/translations
with model 'Fanar-Shaheen-MT-1'. The exact body keys are unconfirmed, so we try the
most likely shape and log the raw response to correct it on the live run.
Run: python smoke/07_shaheen_translate.py
"""
import _common as c

from app.fanar.client import httpx_client
from app.fanar.models import SHAHEEN

ARABIC = "نصيب الزوجة الثمن، ونصيب الابن ضعف نصيب البنت."

# Candidate body — CONFIRM keys against the live response / docs.
BODY = {
    "model": SHAHEEN,
    "text": ARABIC,
    "langpair": "ar-en",   # alt candidates: source_lang/target_lang, src/tgt
}


def main() -> None:
    print(f"[07] Shaheen translation — model={SHAHEEN!r}  POST /translations")
    with httpx_client() as client:
        resp = client.post("/translations", json=BODY)
        print(f"  HTTP {resp.status_code}")
        try:
            data = resp.json()
            c.dump("07_shaheen_translate", data)
            print("  --- raw json ---")
            print("  ", data)
            if resp.status_code == 200:
                c.ok("translations endpoint responded 200 — confirm output key in _out/")
            else:
                c.fail("non-200 — adjust body keys (langpair vs source/target_lang) and retry")
        except Exception:  # noqa: BLE001
            c.fail("non-JSON response")
            print("  ", resp.text[:300])


if __name__ == "__main__":
    main()
