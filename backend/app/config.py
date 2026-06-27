"""Runtime configuration. The Fanar API key lives ONLY in backend/.env (gitignored)
and is loaded here at runtime. It is never hardcoded and never printed (HARD RULE 1).
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# backend/.env holds FANAR_API_KEY (+ optional FANAR_BASE_URL). override=True so editing
# .env and reloading actually picks up the new value (otherwise an already-loaded key
# sticks for the life of the process and a hot --reload silently keeps the stale key).
_BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(_BACKEND_DIR / ".env", override=True)

FANAR_BASE_URL = os.environ.get("FANAR_BASE_URL", "https://api.fanar.qa/v1")


def require_key() -> str:
    """Return the Fanar API key or raise a clear, secret-free error.

    Strips surrounding whitespace/quotes so a stray trailing space pasted into .env
    can't cause a confusing 401 (the key body still has to be valid)."""
    key = (os.environ.get("FANAR_API_KEY") or "").strip().strip('"').strip("'")
    if not key:
        raise RuntimeError(
            "FANAR_API_KEY is not set. Copy backend/.env.example to backend/.env "
            "and add your key (request one at https://api.fanar.qa/request/en)."
        )
    return key
