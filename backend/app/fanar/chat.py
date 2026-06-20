"""Thin chat wrappers over the Fanar chat endpoint, incl. JSON-structured output.

Native function calling is unavailable to our key (Phase 0 finding), so the planner
and verifier get structured data via strict-JSON prompts parsed here.
"""
from __future__ import annotations

import json
import re
from typing import Tuple

from app.fanar.client import openai_client
from app.fanar.models import CHAT

_JSON_OBJ = re.compile(r"\{.*\}", re.DOTALL)


def chat(messages: list, model: str = CHAT, max_tokens: int = 800,
         temperature: float = 0.0) -> str:
    """Single chat completion -> assistant text."""
    resp = openai_client().chat.completions.create(
        model=model, messages=messages, max_tokens=max_tokens, temperature=temperature,
    )
    return resp.choices[0].message.content or ""


def complete_json(system: str, user: str, model: str, max_tokens: int = 400) -> Tuple[dict, str]:
    """Ask for a JSON object and parse the first {...} block. Returns (parsed, raw_text)."""
    raw = chat(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        model=model, max_tokens=max_tokens,
    )
    m = _JSON_OBJ.search(raw)
    if not m:
        raise ValueError(f"No JSON object found in model output: {raw[:200]!r}")
    return json.loads(m.group(0)), raw
