"""JSON-file persistence for per-child profiles (one file per child)."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import date as _date
from pathlib import Path
from typing import List, Optional, Sequence

# backend/data/profiles/<child_id>.json
DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "profiles"


@dataclass
class Session:
    date: str
    target_text: str
    transcript: str
    accuracy_pct: float
    wpm: Optional[float]
    miscue_counts: dict
    weak_sounds: list
    per_sound: dict           # {sound: {"accuracy","n_words","n_correct"}}


@dataclass
class Profile:
    child_id: str
    name: str
    created_at: str
    sessions: List[Session] = field(default_factory=list)


def _today() -> str:
    return _date.today().isoformat()


def _path(child_id: str) -> Path:
    return DATA_DIR / f"{child_id}.json"


def load_profile(child_id: str) -> Optional[Profile]:
    p = _path(child_id)
    if not p.exists():
        return None
    raw = json.loads(p.read_text(encoding="utf-8"))
    return Profile(
        child_id=raw["child_id"],
        name=raw.get("name", ""),
        created_at=raw.get("created_at", ""),
        sessions=[Session(**s) for s in raw.get("sessions", [])],
    )


def save_profile(profile: Profile) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    p = _path(profile.child_id)
    p.write_text(json.dumps(asdict(profile), ensure_ascii=False, indent=2), encoding="utf-8")
    return p


def record_session(
    child_id: str,
    *,
    target_text: str,
    transcript: str,
    words: Sequence,
    accuracy_pct: float,
    wpm: Optional[float],
    miscue_counts: dict,
    weak_sounds: Sequence[str],
    name: str = "",
    date: Optional[str] = None,
) -> Profile:
    """Append one reading session to the child's profile (creating it if new) and persist.
    `words` is the error map's target-aligned word list (each has target + status)."""
    from app.memory.progress import per_sound_map  # local import avoids a cycle

    profile = load_profile(child_id) or Profile(child_id=child_id, name=name,
                                                created_at=_today())
    if name and not profile.name:
        profile.name = name

    profile.sessions.append(Session(
        date=date or _today(),
        target_text=target_text,
        transcript=transcript,
        accuracy_pct=accuracy_pct,
        wpm=wpm,
        miscue_counts=miscue_counts,
        weak_sounds=list(weak_sounds),
        per_sound=per_sound_map(words, weak_sounds),
    ))
    save_profile(profile)
    return profile
