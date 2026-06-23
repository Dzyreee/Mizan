"""Smoke test: Fanar-Sadiq / Islamic rulings model.

Asks a faraid question and inspects whether the response carries sourced citations
(Quran/Hadith) and/or the built-in inheritance tool output. We do NOT trust its math
(HARD RULE 3) — we only want the ruling + sources. Run: python smoke/03_sadiq_islamic.py
"""
import _common as c

from app.fanar.client import openai_client
from app.fanar.models import ISLAMIC


def main() -> None:
    print(f"[03] Islamic/Sadiq ruling — model={ISLAMIC!r}")
    client = openai_client()
    resp = client.chat.completions.create(
        model=ISLAMIC,
        messages=[{
            "role": "user",
            "content": "ما نصيب الزوجة والابن والبنت في الميراث حسب الشريعة؟ اذكر المصادر.",
        }],
        max_tokens=500,
    )
    payload = resp.model_dump()
    c.dump("03_sadiq_islamic", payload)
    text = resp.choices[0].message.content or ""
    print("  --- ruling ---")
    print("  " + text[:600].replace("\n", "\n  "))
    # Sadiq is documented to attach attribution; surface whatever extra fields exist.
    extra = {k: v for k, v in payload["choices"][0].items() if k not in ("message", "index", "finish_reason")}
    if extra:
        print("  --- extra choice fields (possible citations) ---")
        print("  ", extra)
    if text.strip():
        c.ok("Sadiq returned a ruling — INSPECT _out/03_sadiq_islamic.json for citation shape")
    else:
        c.fail("empty ruling")


if __name__ == "__main__":
    main()
