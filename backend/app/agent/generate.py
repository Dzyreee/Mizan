"""GENERATE step: turn the plan into media —
  - a Diwan verse loaded with the weak sounds (Diwan unavailable -> Fanar fallback),
  - an Oryx-IG illustration,
  - Aura TTS audio modelling the hard words.

Images/audio are returned base64-encoded so the frontend can render them directly as
data URIs. Each Fanar model lives in its own module (HARD RULE 6); this just composes
them and records a trace step per model.
"""
from __future__ import annotations

import base64
from typing import Optional

from app.agent.trace import Trace
from app.fanar.diwan import generate_verse
from app.fanar.image import generate_image
from app.fanar.models import AURA_TTS, DIWAN, ORYX_IG
from app.fanar.tts import DEFAULT_VOICE, synthesize

MAX_PRONUNCIATION_WORDS = 5


def _b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def generate_exercise(
    plan: dict,
    trace: Optional[Trace] = None,
    include_image: bool = True,
    include_audio: bool = True,
    voice: str = DEFAULT_VOICE,
) -> dict:
    """Produce verse + illustration + pronunciation audio from a plan."""
    trace = trace or Trace()
    out: dict = {"verse": None, "illustration": None, "pronunciations": []}

    # 1) Verse (Diwan -> Fanar fallback). Keep it SHORT + simple: long/advanced verse is
    # both off-target for a 6-8 year old and slow to generate.
    target_sounds = plan.get("target_sounds") or []
    base_prompt = plan.get("verse_prompt") or (
        "اكتب أبياتاً بسيطة ومرحة لطفل صغير، أكثِر فيها من الحروف: " + " ".join(target_sounds))
    verse_prompt = (base_prompt +
                    " — اجعلها أربعة أسطر قصيرة فقط، بكلمات سهلة جداً ومألوفة لطفلٍ عمره ٦ سنوات.")
    with trace.step("generate-verse", model=DIWAN,
                    input={"prompt": verse_prompt},
                    summary="Diwan unavailable → Fanar writes a short verse loaded with the weak sounds") as st:
        out["verse"] = generate_verse(verse_prompt, max_tokens=200)
        st.set_output({"verse": out["verse"]},
                      summary=f"Verse: {len((out['verse'] or '').split())} words")

    # 2) Illustration (Oryx-IG) — the slow/heavy one; optional.
    if include_image:
        illo_prompt = plan.get("illustration_prompt") or (
            "A cheerful simple flat-style children's illustration, soft colors, no text, no letters.")
        with trace.step("generate-image", model=ORYX_IG,
                        input={"prompt": illo_prompt},
                        summary="Oryx-IG illustrates the exercise") as st:
            png = generate_image(illo_prompt)
            out["illustration"] = {"b64": _b64(png), "mime": "image/png", "bytes": len(png)}
            st.set_output({"bytes": len(png), "mime": "image/png"},
                          summary=f"Illustration: {len(png)} byte PNG")

    # 3) Pronunciation audio (Aura TTS) — model each hard word.
    if include_audio:
        words = [w for w in (plan.get("pronunciation_words") or []) if w][:MAX_PRONUNCIATION_WORDS]
        with trace.step("generate-audio", model=AURA_TTS,
                        input={"words": words, "voice": voice},
                        summary="Aura TTS models the hard words for the child to imitate") as st:
            for w in words:
                mp3 = synthesize(w, voice=voice)
                out["pronunciations"].append(
                    {"word": w, "b64": _b64(mp3), "mime": "audio/mpeg", "bytes": len(mp3)})
            st.set_output({"count": len(out["pronunciations"]), "words": words},
                          summary=f"{len(out['pronunciations'])} pronunciation clips")

    return out
