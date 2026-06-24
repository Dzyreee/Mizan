"""ASSESS pipeline: audio (or transcript) -> Aura STT -> deterministic engine ->
Fanar diagnosis, with every step recorded in a Trace.

    audio ──(Aura STT)──> transcript ──(engine)──> error map ──(Fanar-27B)──> diagnosis
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional, Sequence, Union

from app.agent.diagnose import diagnose as diagnose_step
from app.agent.trace import DETERMINISTIC, Trace
from app.engine import analyze
from app.fanar.models import AURA_STT
from app.fanar.stt import transcribe


def assess(
    target_text: str,
    audio_path: Optional[Union[str, Path]] = None,
    transcript: Optional[str] = None,
    duration_sec: Optional[float] = None,
    word_timestamps: Optional[Sequence[dict]] = None,
    do_diagnose: bool = True,
    trace: Optional[Trace] = None,
) -> dict:
    """Run the assess+diagnose pipeline.

    Provide EITHER `audio_path` (real flow: Aura STT transcribes) OR `transcript`
    (test/offline flow: skip STT). Pass a shared `trace` to compose with adapt() into
    one continuous loop. Returns target/transcript/error_map/diagnosis/trace.
    """
    if transcript is None and audio_path is None:
        raise ValueError("assess() needs either audio_path or transcript")

    trace = trace or Trace()

    # 1) Transcribe (Aura STT) — skipped when a transcript is supplied directly.
    if transcript is None:
        with trace.step("transcribe", model=AURA_STT,
                        input={"audio_file": str(audio_path)},
                        summary="Aura STT transcribes the child's reading") as st:
            transcript = transcribe(audio_path)
            st.set_output({"transcript": transcript},
                          summary=f"Transcribed {len(transcript.split())} words")

    # 2) Align + classify (pure Python, deterministic — HARD RULE 3).
    with trace.step("align", model=DETERMINISTIC,
                    input={"target": target_text, "transcript": transcript},
                    summary="Deterministic alignment + miscue classification") as st:
        em = analyze(target_text, transcript, duration_sec=duration_sec,
                     word_timestamps=word_timestamps)
        st.set_output(
            {"accuracy_pct": em.accuracy_pct, "miscue_counts": em.counts,
             "correct": em.correct_words, "total": em.total_target_words},
            summary=f"Accuracy {em.accuracy_pct}% — miscues {em.counts or '{}'}",
        )

    # 3) Diagnose the pattern (Fanar-27B, JSON output).
    diagnosis = diagnose_step(em, trace=trace) if do_diagnose else None

    return {
        "target_text": target_text,
        "transcript": transcript,
        "error_map": em.to_dict(),
        "diagnosis": diagnosis,
        "trace": trace.to_dict(),
    }
