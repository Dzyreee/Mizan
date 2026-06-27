"""Fanar picks the most relevant pre-generated illustration for a piece of text.

Replaces slow live image generation: instead of generating art per poem/passage at
runtime, we keep a fixed library of pre-generated illustrations and ask the Fanar chat
model to choose the best match, a fast text call. JSON-only output (native tool-calling
is unavailable to our key, Phase 0 finding). Degrades to the first candidate on any error
so the reading flow never blocks on this.
"""
from __future__ import annotations

import re

from app.fanar.chat import complete_json

_SYSTEM = (
    "You match a short Arabic children's text to the most relevant illustration. "
    "You are given the text and a list of images, each with an id and an Arabic "
    "description. Pick the SINGLE best-matching image. "
    'Return ONLY JSON: {"id": "<one id from the list>"}. No prose, no extra keys.'
)

# Very common Arabic function words — ignored so matching keys on real content nouns.
_STOP = {"في", "إلى", "على", "من", "عن", "مع", "هذا", "هذه", "ذلك", "التي", "الذي",
         "كل", "قد", "أن", "إن", "ما", "لا", "هو", "هي", "أو", "ثم", "كان", "كانت"}


def _tokens(s: str) -> set[str]:
    """Arabic content tokens, with the definite article «ال» stripped so المدرسة≈مدرسة."""
    out = set()
    for w in re.findall(r"[؀-ۿ]+", s):
        if w.startswith("ال") and len(w) > 4:
            w = w[2:]
        if len(w) >= 3 and w not in _STOP:
            out.add(w)
    return out


def _keyword_pick(text: str, candidates: list[dict], ids: list[str]) -> str:
    """Deterministic fallback when Fanar is unavailable: choose the candidate whose
    description shares the most content words with the text. Ties keep list order."""
    tt = _tokens(text)
    best_id, best_score = ids[0], 0
    for c in candidates:
        score = len(tt & _tokens(c.get("description", "")))
        if score > best_score:
            best_id, best_score = c["id"], score
    return best_id


def pick_image(text: str, candidates: list[dict]) -> str:
    """Return the id of the best-matching candidate. Uses Fanar to pick; on any Fanar
    error degrades to deterministic keyword matching (never blocks the reading flow)."""
    if not candidates:
        raise ValueError("No candidates provided.")
    ids = [c["id"] for c in candidates]
    listing = "\n".join(f"- id={c['id']}: {c['description']}" for c in candidates)
    user = f"Text:\n{text}\n\nImages:\n{listing}"
    try:
        parsed, _raw = complete_json(_SYSTEM, user, max_tokens=60)
        choice = str(parsed.get("id", "")).strip()
        return choice if choice in ids else _keyword_pick(text, candidates, ids)
    except Exception:  # noqa: BLE001
        return _keyword_pick(text, candidates, ids)
