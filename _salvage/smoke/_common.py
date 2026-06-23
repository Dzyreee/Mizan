"""Shared helpers for smoke scripts: path setup, output dir, pretty result logging."""
import json
import sys
from pathlib import Path

# Make `app...` importable when running `python smoke/XX.py` from backend/.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

OUT = Path(__file__).parent / "_out"
OUT.mkdir(exist_ok=True)


def dump(name: str, payload) -> Path:
    """Write a raw response payload to _out/<name>.json for recording in FANAR_NOTES.md."""
    path = OUT / f"{name}.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str))
    return path


def ok(msg: str) -> None:
    print(f"  ✅ {msg}")


def fail(msg: str) -> None:
    print(f"  ❌ {msg}")
