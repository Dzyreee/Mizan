"""Central config. Reads secrets from .env — never hardcode the key (HARD RULE 1)."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Load backend/.env regardless of where the process is launched from.
_BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(_BACKEND_DIR / ".env")

FANAR_API_KEY: str = os.getenv("FANAR_API_KEY", "")
FANAR_BASE_URL: str = os.getenv("FANAR_BASE_URL", "https://api.fanar.qa/v1")


def require_key() -> str:
    """Return the API key or fail loudly with a helpful message."""
    if not FANAR_API_KEY:
        raise RuntimeError(
            "FANAR_API_KEY is not set. Copy backend/.env.example to backend/.env "
            "and add your key (request one at https://api.fanar.qa/request/en)."
        )
    return FANAR_API_KEY
