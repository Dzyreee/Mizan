"""Aura STT: transcribe the child reading aloud. This is the core input to Iqra.

Endpoint is OpenAI-shaped: client.audio.transcriptions.create(model=..., file=...).
The transcript is fed VERBATIM into the deterministic alignment engine, so we must
NOT post-process / "clean" it here, preserving the child's actual reading is the
whole point (see the Phase 0 faithfulness gate).
"""
from __future__ import annotations

from pathlib import Path
from typing import Union

from app.fanar.client import openai_client
from app.fanar.models import AURA_STT


def transcribe(audio_path: Union[str, Path], model: str = AURA_STT) -> str:
    """Transcribe an audio file to text via Aura STT. Returns the raw transcript."""
    with open(audio_path, "rb") as f:
        resp = openai_client().audio.transcriptions.create(model=model, file=f)
    return (getattr(resp, "text", None) or "").strip()
