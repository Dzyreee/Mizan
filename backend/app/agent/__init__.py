"""Iqra agent layer: the verifiable pipeline that turns a child's reading into an
assessment, a diagnosis, and (Phase 3) an adaptive exercise, each step recorded in a
structured Trace so the whole reasoning process is inspectable in the UI.

Separation of concerns (HARD RULE 3): the deterministic engine owns the error map;
the LLM only reasons ON TOP of it (diagnose/plan). Every LLM call is JSON-structured
(native tool-calling is unavailable on our key, Phase 0).
"""
