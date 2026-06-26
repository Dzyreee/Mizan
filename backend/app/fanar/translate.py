"""Shaheen translation: give expat (non-Arabic-speaking) parents an English summary of
their child's progress.

POST /translations (bespoke, NOT OpenAI-shaped): {model, text, langpair} -> {text}.
"""
from __future__ import annotations

from app.fanar.client import httpx_client
from app.fanar.models import SHAHEEN


def translate(text: str, langpair: str = "ar-en", model: str = SHAHEEN) -> str:
    """Translate `text` (default Arabic -> English). Returns the translated string."""
    if not (text or "").strip():
        return ""
    with httpx_client(timeout=30) as cl:
        r = cl.post("/translations",
                    json={"model": model, "text": text, "langpair": langpair})
        r.raise_for_status()
        return (r.json().get("text") or "").strip()
