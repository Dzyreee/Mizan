"""Smoke test: Fanar chat completion (the planner LLM).

Confirms basic chat works and that Arabic round-trips. Run: python smoke/01_chat.py
"""
import _common as c

from app.fanar.client import openai_client
from app.fanar.models import CHAT


def main() -> None:
    print(f"[01] chat completion — model={CHAT!r}")
    client = openai_client()
    resp = client.chat.completions.create(
        model=CHAT,
        messages=[
            {"role": "system", "content": "You are a concise assistant. Reply in Arabic."},
            {"role": "user", "content": "في جملة واحدة، ما هو علم الفرائض؟"},
        ],
        max_tokens=200,
    )
    text = resp.choices[0].message.content
    c.dump("01_chat", resp.model_dump())
    print("  --- reply ---")
    print("  " + (text or "").replace("\n", "\n  "))
    if text and text.strip():
        c.ok("chat completion returned text")
    else:
        c.fail("empty completion")


if __name__ == "__main__":
    main()
