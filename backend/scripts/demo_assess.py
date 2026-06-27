"""CLI demo of the assess+diagnose pipeline, with the Agent Trace printed.

Self-contained (needs VPN): it synthesizes a deliberately *misread* reading with Aura
TTS, then runs the REAL pipeline on that audio, Aura STT -> engine -> Fanar diagnosis.

    cd backend && .venv/bin/python -m scripts.demo_assess
    cd backend && .venv/bin/python -m scripts.demo_assess --audio path/to/child.mp3 \
                     --target "ذهب الولد إلى المدرسة"
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agent.assess import assess  # noqa: E402

# Target passage, and a misread rendition (real-word subs + a dropped word) that
# survives Aura's normalization (Phase 0): الولد→الورد, الصباح→المساء, omit الصغير.
DEMO_TARGET = "ذهب الولد الصغير إلى المدرسة في الصباح"
DEMO_MISREAD = "ذهب الورد إلى المدرسة في المساء"


def _print_trace(result: dict) -> None:
    print("\n────────── AGENT TRACE ──────────")
    for i, step in enumerate(result["trace"]["steps"], 1):
        flag = "" if step["status"] == "ok" else f"  !! {step['error']}"
        print(f"[{i}] {step['name']:11} ({step['model']})  {step['latency_ms']} ms{flag}")
        print(f"      → {step['summary']}")
    print(f"    total: {result['trace']['total_latency_ms']} ms")


def _print_summary(result: dict) -> None:
    em = result["error_map"]
    print("\n────────── RESULT ──────────")
    print(f"  target    : {result['target_text']}")
    print(f"  transcript: {result['transcript']}")
    print(f"  accuracy  : {em['accuracy_pct']}%  ({em['correct_words']}/{em['total_target_words']})")
    print(f"  miscues   : {em['counts'] or '{}'}")
    dx = result.get("diagnosis") or {}
    print("\n────────── DIAGNOSIS (Fanar-27B) ──────────")
    for p in dx.get("patterns", []):
        print(f"  • {p.get('label')}  [{p.get('confidence')}], {p.get('evidence')}")
    print(f"  weak sounds : {dx.get('weak_sounds')}")
    print(f"  focus       : {dx.get('focus')}")
    print(f"  encourage   : {dx.get('encouragement')}")
    if dx.get("specialist_note"):
        print(f"  note        : {dx.get('specialist_note')}")
    if dx.get("_safety_scrubbed"):
        print("  ⚠️  safety filter scrubbed forbidden wording from the model output")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", help="child reading recording (mp3/wav). Omit for self-contained demo.")
    ap.add_argument("--target", default=DEMO_TARGET)
    ap.add_argument("--json", action="store_true", help="dump the full result as JSON")
    args = ap.parse_args()

    if args.audio:
        result = assess(args.target, audio_path=args.audio)
    else:
        # Self-contained: synthesize the misread audio first.
        from app.fanar.tts import synthesize
        print(f"Synthesizing a misread of: {args.target}")
        print(f"  (spoken as)            : {DEMO_MISREAD}")
        audio = Path(tempfile.gettempdir()) / "iqra_demo_misread.mp3"
        audio.write_bytes(synthesize(DEMO_MISREAD, voice="Noor"))
        print(f"  wrote {audio} ({audio.stat().st_size} bytes)")
        result = assess(args.target, audio_path=audio)

    _print_trace(result)
    _print_summary(result)
    if args.json:
        print("\n────────── FULL JSON ──────────")
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
