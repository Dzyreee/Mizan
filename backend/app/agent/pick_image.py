"""Fanar picks the most relevant pre-generated illustration for a piece of text.

Replaces slow live image generation: instead of generating art per poem/passage at
runtime, we keep a fixed library of pre-generated illustrations and ask the Fanar chat
model to choose the best match — a fast text call. JSON-only output (native tool-calling
is unavailable to our key, Phase 0 finding). Degrades to the first candidate on any error
so the reading flow never blocks on this.
"""
from __future__ import annotations

from app.fanar.chat import complete_json

_SYSTEM = (
    "You match a short Arabic children's text to the most relevant illustration. "
    "You are given the text and a list of images, each with an id and an Arabic "
    "description. Pick the SINGLE best-matching image. "
    'Return ONLY JSON: {"id": "<one id from the list>"}. No prose, no extra keys.'
)


def pick_image(text: str, candidates: list[dict]) -> str:
    """Return the id of the best-matching candidate. Falls back to the first on any issue."""
    if not candidates:
        raise ValueError("No candidates provided.")
    ids = [c["id"] for c in candidates]
    listing = "\n".join(f"- id={c['id']}: {c['description']}" for c in candidates)
    user = f"Text:\n{text}\n\nImages:\n{listing}"
    try:
        parsed, _raw = complete_json(_SYSTEM, user, max_tokens=60)
        choice = str(parsed.get("id", "")).strip()
        return choice if choice in ids else ids[0]
    except Exception:  # noqa: BLE001
        return ids[0]
