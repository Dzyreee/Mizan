"""DIAGNOSE step: Fanar-27B names the reading PATTERN by reasoning over the engine's
deterministic error map (JSON output). It does NOT recompute anything (HARD RULE 3).

Honest framing is enforced in the system prompt AND defended in code: Iqra is a
reading-SUPPORT tool, never a diagnostic one, no clinical labels, ever.
"""
from __future__ import annotations

import json
import re
from typing import List, Optional

from app.engine.errormap import (
    OMISSION,
    REPETITION,
    SELF_CORRECTION,
    SUBSTITUTION,
    ErrorMap,
)
from app.fanar.chat import complete_json
from app.fanar.models import CHAT_27B

# Words/phrases that must never appear in child/parent-facing output (defense in depth).
_FORBIDDEN = re.compile(
    r"\b(dyslexi\w*|disorder|disease|diagnos\w*|adhd|autis\w*|disab\w*|"
    r"عسر القراءة|اضطراب|مرض|تشخيص|إعاقة|توحد)\b",
    re.IGNORECASE,
)

SYSTEM = (
    "You are a warm, encouraging Arabic reading COACH for children aged 6-8. "
    "You receive a DETERMINISTIC error report from one read-aloud session (already "
    "computed by a separate engine, never recompute or invent numbers). Your job is to "
    "name the READING PATTERN and the specific sounds/letters to practice next.\n\n"
    "ABSOLUTE RULES, this is reading SUPPORT, NOT diagnosis:\n"
    "1. Never name or imply any medical or clinical condition (no 'dyslexia', 'disorder', "
    "'diagnosis', etc.). Never say the child 'has' anything.\n"
    "2. Frame every concern as 'a pattern worth practicing', and only suggest a specialist "
    "with: 'worth checking with a specialist if it continues'.\n"
    "3. Be specific and base EVERY claim only on the provided data. Be kind.\n"
    "4. Write the content fields in simple Arabic.\n"
    "5. Output ONLY a JSON object, no prose, no markdown.\n\n"
    "JSON schema:\n"
    "{\n"
    '  "patterns": [ {"label": "<short Arabic phrase>", "evidence": "<from the data>", '
    '"confidence": "low|medium|high"} ],\n'
    '  "weak_sounds": ["<Arabic letter or feature, e.g. \\u0635 or \\u0646\\u0647\\u0627\\u064a\\u0627\\u062a \\u0627\\u0644\\u0643\\u0644\\u0645\\u0627\\u062a>"],\n'
    '  "focus": "<the single most useful thing to practice next, Arabic>",\n'
    '  "encouragement": "<one warm Arabic sentence for the child>",\n'
    '  "specialist_note": "<empty string, or a gentle Arabic note: worth checking if it persists>"\n'
    "}"
)


def summarize_error_map(em: ErrorMap) -> dict:
    """Compact, factual view of the error map handed to the LLM (the ground truth)."""
    def words(kind: str) -> List[dict]:
        if kind == SUBSTITUTION:
            return [{"expected": m.target_word, "read_as": m.spoken_word}
                    for m in em.miscues if m.type == SUBSTITUTION]
        return [m.target_word or m.spoken_word for m in em.miscues if m.type == kind]

    return {
        "accuracy_pct": em.accuracy_pct,
        "total_words": em.total_target_words,
        "correct_words": em.correct_words,
        "words_per_minute": em.wpm,
        "miscue_counts": em.counts,
        "substitutions": words(SUBSTITUTION),
        "omissions": words(OMISSION),
        "repetitions": words(REPETITION),
        "self_corrections": words(SELF_CORRECTION),
        "long_hesitations": [{"before_word": h.before_word, "gap_sec": h.gap_sec}
                             for h in em.hesitations],
    }


def _scrub(diagnosis: dict) -> dict:
    """Last-line defense: blank out any forbidden clinical wording that slipped through."""
    flagged = False

    def clean(s):
        nonlocal flagged
        if isinstance(s, str) and _FORBIDDEN.search(s):
            flagged = True
            return _FORBIDDEN.sub("…", s)
        return s

    for key in ("focus", "encouragement", "specialist_note"):
        if key in diagnosis:
            diagnosis[key] = clean(diagnosis[key])
    for p in diagnosis.get("patterns", []) or []:
        if isinstance(p, dict):
            p["label"] = clean(p.get("label"))
            p["evidence"] = clean(p.get("evidence"))
    diagnosis["_safety_scrubbed"] = flagged
    return diagnosis


def _headline(diagnosis: dict) -> str:
    pats = diagnosis.get("patterns") or []
    if pats and isinstance(pats[0], dict):
        return pats[0].get("label", "نمط قراءة")
    return diagnosis.get("focus", "تم تحليل القراءة")


def diagnose(em: ErrorMap, trace=None, model: str = CHAT_27B) -> dict:
    """Return a structured, honest-framed diagnosis of the reading pattern."""
    facts = summarize_error_map(em)
    user = ("Reading-session error report (deterministic, do not recompute):\n"
            + json.dumps(facts, ensure_ascii=False, indent=2))

    def run() -> dict:
        parsed, _raw = complete_json(SYSTEM, user, model=model, max_tokens=700)
        return _scrub(parsed)

    if trace is None:
        return run()

    with trace.step("diagnose", model=model, input=facts,
                    summary="Fanar-27B reasons over the error map to name the pattern") as st:
        diagnosis = run()
        st.set_output(diagnosis, summary=f"Pattern: {_headline(diagnosis)}")
    return diagnosis
