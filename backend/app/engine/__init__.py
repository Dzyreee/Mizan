"""Iqra deterministic read-aloud engine (HARD RULE 3: pure Python, NO LLM).

Given a KNOWN target passage and a transcript of the child reading it, this package
computes a fully deterministic error map: word-level alignment, miscue classification
(substitution / omission / insertion / repetition / self-correction), accuracy %,
reading speed (WPM / WCPM), and long-hesitation locations.

The target text is the ground truth, so no trained model or labelled data is needed, every mismatch against the target is a measurable reading error.

Public API:
    from app.engine import analyze
    error_map = analyze(target_text, transcript_text,
                        duration_sec=..., word_timestamps=...)
"""
from .core import DEFAULT_HESITATION_SEC, analyze
from .errormap import AlignedWord, ErrorMap, Hesitation, Miscue

__all__ = [
    "analyze",
    "ErrorMap",
    "Miscue",
    "AlignedWord",
    "Hesitation",
    "DEFAULT_HESITATION_SEC",
]
