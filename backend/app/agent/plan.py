"""PLAN step: Fanar-27B turns the diagnosis into a concrete, targeted exercise spec
(JSON output) — what words/passage/verse/illustration/audio to produce for the child's
weak sounds. The actual media is produced by generate.py.
"""
from __future__ import annotations

import json
from typing import Optional

from app.fanar.chat import complete_json
from app.fanar.models import CHAT_27B

SYSTEM = (
    "You are an expert Arabic early-reading teacher designing a FUN practice exercise "
    "for a child aged 6-8, targeting specific weak sounds/letters from a diagnosis.\n\n"
    "Rules:\n"
    "1. All child-facing text in simple, correct Modern Standard Arabic — playful, positive, "
    "fully age-appropriate. No scary, sad, religious, or violent themes.\n"
    "2. LOAD the words/passage with the TARGET sounds so the child practices them a lot.\n"
    "3. The illustration prompt MUST be in ENGLISH, describe one cheerful simple scene, and "
    "MUST end with 'no text, no letters' (the image model can't render Arabic reliably).\n"
    "4. Output ONLY a JSON object — no prose, no markdown.\n\n"
    "JSON schema:\n"
    "{\n"
    '  "title": "<short playful Arabic title>",\n'
    '  "target_sounds": ["<the letters/features being drilled>"],\n'
    '  "practice_words": ["<6 short Arabic words rich in the target sounds>"],\n'
    '  "practice_passage": "<2 short simple Arabic sentences using those words>",\n'
    '  "verse_prompt": "<Arabic instruction to a poet: write 2-4 playful rhythmic lines for '
    'a young child, loaded with the target sounds, on a fun friendly topic>",\n'
    '  "illustration_prompt": "<English; one cheerful simple child-friendly scene; end with '
    'no text, no letters>",\n'
    '  "pronunciation_words": ["<3-4 of the hardest words to model aloud>"]\n'
    "}"
)


def plan_exercise(diagnosis: dict, trace=None, model: str = CHAT_27B) -> dict:
    """Produce a structured exercise plan targeting the diagnosis's weak sounds."""
    seed = {
        "weak_sounds": diagnosis.get("weak_sounds") or [],
        "focus": diagnosis.get("focus") or "",
        "patterns": diagnosis.get("patterns") or [],
    }
    user = "Design a targeted practice exercise for this diagnosis:\n" + json.dumps(
        seed, ensure_ascii=False, indent=2)

    def run() -> dict:
        parsed, _raw = complete_json(SYSTEM, user, model=model, max_tokens=900)
        return parsed

    if trace is None:
        return run()

    with trace.step("plan", model=model, input=seed,
                    summary="Fanar-27B plans a targeted exercise") as st:
        plan = run()
        st.set_output(
            plan,
            summary=f"Planned '{plan.get('title', 'exercise')}' for sounds {plan.get('target_sounds')}",
        )
    return plan
