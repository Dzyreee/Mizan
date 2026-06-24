"""Bank a demo child's progress so the rising trend is visible without any Fanar calls.

Deterministic (no VPN): the same short passage is read three times, two weeks apart, with
fewer errors each time. Per-sound accuracy on ص and ر is computed by the engine and
persisted. Re-runnable (it resets the demo profile first).

    cd backend && .venv/bin/python -m scripts.seed_progress
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.engine import analyze                                  # noqa: E402
from app.memory import build_progress, load_profile            # noqa: E402
from app.memory.store import _path, record_session             # noqa: E402

CHILD_ID = "demo-child"
NAME = "ليان"
TARGET = "صعد الصقر فوق الصخرة ورأى البحر"
WEAK_SOUNDS = ["ص", "ر"]

# (date, what the child actually read, reading duration in seconds) — improving over time.
SESSIONS = [
    ("2026-06-10", "سعد السقر فوق الصخرة وراء البحر", 36.0),   # many ص/ر errors
    ("2026-06-17", "صعد السقر فوق الصخرة ورأى البحر", 30.0),   # fewer
    ("2026-06-24", "صعد الصقر فوق الصخرة ورأى البحر", 24.0),   # clean read
]


def main() -> None:
    p = _path(CHILD_ID)
    if p.exists():
        p.unlink()  # reset so re-running doesn't duplicate sessions

    for date, transcript, duration in SESSIONS:
        em = analyze(TARGET, transcript, duration_sec=duration)
        record_session(
            CHILD_ID,
            target_text=TARGET,
            transcript=transcript,
            words=em.to_dict()["words"],
            accuracy_pct=em.accuracy_pct,
            wpm=em.wpm,
            miscue_counts=em.counts,
            weak_sounds=WEAK_SOUNDS,
            name=NAME,
            date=date,
        )

    progress = build_progress(load_profile(CHILD_ID))
    print(f"Seeded '{NAME}' ({CHILD_ID}) with {progress['sessions_count']} sessions → {p}\n")
    for s in progress["sounds"]:
        series = " → ".join(f"{pt['accuracy']}%" for pt in s["series"])
        print(f"  sound {s['sound']}: {series}   ({s['trend']}, +{s['delta']})")
    print("\nFull progress payload:")
    print(json.dumps(progress, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
