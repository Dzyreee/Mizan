"""Planner: turn a natural-language (Gulf Arabic) inheritance question into a structured
case — the heirs and the estate. Uses strict-JSON output on a base chat model.

We deliberately use a base chat model (Fanar-C-2-27B) and a neutral "extractor" framing
to avoid the Islamic-RAG hijack: when `Fanar` sees faraid wording it tends to answer with
a fatwa and ignore format instructions (Phase 0 finding). Extraction must stay mechanical.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from app.fanar.chat import complete_json
from app.fanar.models import CHAT_C2
from app.faraid import Heirs

PLANNER_MODEL = CHAT_C2

_SYS = (
    "You are a data extraction function for inheritance questions. "
    "Read the user's scenario and output ONLY a JSON object — no prose, no markdown, "
    "no religious ruling, no explanation. Schema:\n"
    '{"estate": number, "currency": string, '
    '"spouse": "husband" | "wife" | "none", "wives": integer, '
    '"sons": integer, "daughters": integer, "father": boolean, "mother": boolean}\n'
    "Rules: 'spouse' is from the deceased's perspective (a dead man leaves a wife; a dead "
    "woman leaves a husband). 'wives' is the number of surviving wives (0 if none/husband). "
    "Use 0 or false for absent heirs. If the estate value is not given, use 0. "
    "Default currency to \"QAR\" if unstated."
)


@dataclass
class PlannedCase:
    heirs: Heirs
    estate: float
    currency: str
    raw_extract: dict


def plan(question: str, model: str = PLANNER_MODEL) -> Tuple[PlannedCase, str]:
    data, raw = complete_json(_SYS, question, model=model)
    spouse = (data.get("spouse") or "none").lower()
    wives = int(data.get("wives") or 0)
    if spouse == "wife" and wives == 0:
        wives = 1  # "a wife" with no explicit count
    heirs = Heirs(
        husband=(spouse == "husband"),
        wives=wives if spouse != "husband" else 0,
        sons=int(data.get("sons") or 0),
        daughters=int(data.get("daughters") or 0),
        father=bool(data.get("father")),
        mother=bool(data.get("mother")),
    )
    case = PlannedCase(
        heirs=heirs,
        estate=float(data.get("estate") or 0),
        currency=str(data.get("currency") or "QAR"),
        raw_extract=data,
    )
    return case, raw
