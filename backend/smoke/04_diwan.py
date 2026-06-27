"""Smoke test + DISCOVERY: Diwan poetry generation.

Diwan was not used by the prior project and is not in GET /v1/models, so we try a
prioritized list of candidate ids against the chat endpoint, and for the first that
works we generate a short, child-friendly verse LOADED with a target sound (the
emphatic letter ص), which is exactly Iqra's use case. Records the winning id +
output so FANAR_NOTES.md and models.DIWAN can be updated.

Run: python smoke/04_diwan.py
"""
import _common as c
from app.fanar.client import openai_client

CANDIDATES = ["Fanar-Diwan", "Diwan", "Fanar-Diwan-1", "Fanar-Poetry", "Fanar"]

# Iqra-style prompt: kid verse drilling a weak sound.
PROMPT = (
    "اكتب بيتين من الشعر العربي البسيط لطفل عمره ٧ سنوات، "
    "بإيقاع واضح، وأكثِر من حرف الصاد (ص) في الكلمات، "
    "عن عصفور صغير في الصباح."
)


def main() -> None:
    print("[04] Diwan poetry, discovering a working model id")
    client = openai_client()
    winner = None
    for mid in CANDIDATES:
        try:
            resp = client.chat.completions.create(
                model=mid,
                messages=[{"role": "user", "content": PROMPT}],
                max_tokens=300, temperature=0.7,
            )
        except Exception as e:  # noqa: BLE001
            print(f"  model={mid!r:16} -> ERROR {str(e)[:90]}")
            continue
        text = (resp.choices[0].message.content or "").strip()
        print(f"  model={mid!r:16} -> OK ({len(text)} chars)")
        if text and winner is None:
            winner = mid
            c.dump(f"04_diwan_{mid}", resp.model_dump())
            print("  --- verse ---")
            for line in text.splitlines():
                print("    " + line)
    if winner:
        c.ok(f"Diwan-capable model id = {winner!r}  (set models.DIWAN to this)")
    else:
        c.fail("no candidate produced a verse, widen CANDIDATES / check 00b_probe output")


if __name__ == "__main__":
    main()
