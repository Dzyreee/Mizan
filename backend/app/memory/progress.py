"""Deterministic per-sound progress measurement.

A "sound" is an Arabic letter (e.g. ص, ر). Its accuracy in one session = the share of
TARGET words containing that letter that the child read correctly. Tracked across
sessions, this is the rising/falling trend the progress view shows.
"""
from __future__ import annotations

from typing import List, Optional, Sequence

from app.engine.errormap import ST_CORRECT
from app.engine.text import normalize_word


def _target(word) -> str:
    return word["target"] if isinstance(word, dict) else word.target


def _status(word) -> str:
    return word["status"] if isinstance(word, dict) else word.status


def per_sound_accuracy(words: Sequence, sound: str) -> Optional[dict]:
    """Accuracy on target words containing `sound`. Returns None if the sound doesn't
    appear in this passage (so it isn't charted for that session)."""
    key = normalize_word(sound)
    if not key:
        return None
    relevant = [w for w in words if key in normalize_word(_target(w))]
    if not relevant:
        return None
    correct = sum(1 for w in relevant if _status(w) == ST_CORRECT)
    return {"accuracy": round(100.0 * correct / len(relevant), 1),
            "n_words": len(relevant), "n_correct": correct}


def per_sound_map(words: Sequence, sounds: Sequence[str]) -> dict:
    """{sound: accuracy_info} for the sounds that actually occur in the passage."""
    out = {}
    for s in sounds:
        info = per_sound_accuracy(words, s)
        if info is not None:
            out[s] = info
    return out


def build_progress(profile) -> dict:
    """Assemble the cross-session trend per tracked sound, plus overall series."""
    tracked: List[str] = []
    for sess in profile.sessions:
        for snd in sess.weak_sounds:
            if snd not in tracked:
                tracked.append(snd)

    sounds = []
    for snd in tracked:
        series = [
            {"date": s.date, "accuracy": s.per_sound[snd]["accuracy"],
             "n_words": s.per_sound[snd]["n_words"]}
            for s in profile.sessions if snd in s.per_sound
        ]
        if not series:
            continue
        first, latest = series[0]["accuracy"], series[-1]["accuracy"]
        delta = round(latest - first, 1)
        trend = "improving" if delta > 0 else "declining" if delta < 0 else "flat"
        sounds.append({
            "sound": snd, "series": series, "first": first, "latest": latest,
            "delta": delta, "trend": trend, "sessions": len(series),
        })

    overall = [{"date": s.date, "accuracy": s.accuracy_pct, "wpm": s.wpm}
               for s in profile.sessions]

    return {
        "child_id": profile.child_id,
        "name": profile.name,
        "sessions_count": len(profile.sessions),
        "sounds": sounds,
        "overall": overall,
    }
