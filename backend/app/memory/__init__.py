"""Per-child memory + cross-session progress.

Profiles persist locally as JSON (one file per child). Progress on each weak sound is
computed DETERMINISTICALLY from the engine's error maps — accuracy on the target words
that contain that sound — so "is the child improving on ص?" is a real measurement, not
an LLM opinion (consistent with HARD RULE 3).
"""
from .progress import build_progress, per_sound_accuracy, per_sound_map
from .store import Profile, Session, load_profile, record_session, save_profile

__all__ = [
    "Profile",
    "Session",
    "load_profile",
    "save_profile",
    "record_session",
    "build_progress",
    "per_sound_map",
    "per_sound_accuracy",
]
