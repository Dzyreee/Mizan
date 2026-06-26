"""FanarGuard: validate that child-facing generated content is safe + culturally
appropriate before a child ever sees it (HARD RULE 5).

POST /moderations, model Fanar-Guard-2, body {model, prompt, response}
  -> {safety, cultural_awareness}  (~0-5 scale, higher = safer).
Phase 6 calibration: a gentle kids' verse scored safety≈4.4; violent text scored ≈1.0.
We treat content as safe at safety >= SAFETY_THRESHOLD.
"""
from __future__ import annotations

from app.fanar.client import httpx_client
from app.fanar.models import GUARD

SAFETY_THRESHOLD = 3.0
CULTURAL_THRESHOLD = 2.5

# Default context describing what the content is meant to be (the "prompt" half).
DEFAULT_CONTEXT = "محتوى تعليمي بسيط وآمن لطفل عربي عمره بين ٦ و٨ سنوات"


def check_content(response_text: str, context: str = DEFAULT_CONTEXT,
                  model: str = GUARD) -> dict:
    """Score one piece of child-facing text. Returns a dict with `safe` (bool) plus the
    raw scores so the trace/UI can show why."""
    if not (response_text or "").strip():
        return {"safe": True, "safety": None, "cultural_awareness": None,
                "threshold": SAFETY_THRESHOLD, "model": model, "skipped": "empty"}

    with httpx_client(timeout=30) as cl:
        r = cl.post("/moderations",
                    json={"model": model, "prompt": context, "response": response_text})
        r.raise_for_status()
        data = r.json()

    safety = float(data.get("safety", 0.0))
    cultural = float(data.get("cultural_awareness", 0.0))
    return {
        "safe": safety >= SAFETY_THRESHOLD and cultural >= CULTURAL_THRESHOLD,
        "safety": round(safety, 2),
        "cultural_awareness": round(cultural, 2),
        "threshold": SAFETY_THRESHOLD,
        "model": model,
    }
