"""Smoke test: how does the planner get STRUCTURED output from Fanar?

Phase 0 findings drive Phase 2's planner design:
  - The agentic models (Fanar-Agentic, Fanar-Sadiq-Agentic) are NOT authorized for our key.
  - Plain `Fanar` ignores the OpenAI `tools` param and answers as RAG.
So we evaluate the realistic path: JSON-structured output from an authorized chat model.
We test a NEUTRAL extraction prompt (avoids the Islamic-RAG hijack that fires on faraid
wording) on a couple of models and report which reliably returns parseable JSON.

Run: python smoke/02_tool_calling.py
"""
import json

import _common as c
from openai import BadRequestError

from app.fanar.client import openai_client
from app.fanar.models import CHAT, CHAT_C2

# Neutral, non-religious extraction so Islamic-RAG steering doesn't hijack the reply.
SYS = ('You are a parser. Output ONLY a JSON object, no prose, no markdown. '
       'Schema: {"estate": number, "spouse": "husband"|"wife"|"none", '
       '"sons": integer, "daughters": integer}')
USER = "A man died leaving a wife, two sons and one daughter. The estate is 120000."


def try_native_tools() -> bool:
    """Quick check whether `tools` produces tool_calls on the default model (expected: no)."""
    client = openai_client()
    try:
        resp = client.chat.completions.create(
            model=CHAT,
            messages=[{"role": "user", "content": USER}],
            tools=[{"type": "function", "function": {"name": "extract", "parameters": {"type": "object"}}}],
            tool_choice="auto",
        )
    except BadRequestError as e:
        c.fail(f"`tools` param rejected by {CHAT}: {e}")
        return False
    calls = getattr(resp.choices[0].message, "tool_calls", None)
    if calls:
        c.ok(f"NATIVE tool_calls work on {CHAT} (unexpected!) -> {calls[0].function.name}")
        return True
    c.fail(f"{CHAT} ignored `tools` (no tool_calls) — use JSON path")
    return False


def try_json(model: str) -> bool:
    client = openai_client()
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": SYS}, {"role": "user", "content": USER}],
        max_tokens=200,
    )
    raw = resp.choices[0].message.content or ""
    c.dump(f"02_json_{model}", resp.model_dump())
    snippet = raw[raw.find("{"): raw.rfind("}") + 1]
    try:
        parsed = json.loads(snippet)
        c.ok(f"{model}: JSON parses -> {parsed}")
        return True
    except Exception as e:  # noqa: BLE001
        c.fail(f"{model}: JSON did not parse ({e}); raw[:160]={raw[:160]!r}")
        return False


def main() -> None:
    print("[02] structured-output strategy probe")
    print("  - native tools on default model:")
    try_native_tools()
    print("  - JSON-structured-output fallback:")
    for m in (CHAT, CHAT_C2):
        try_json(m)


if __name__ == "__main__":
    main()
