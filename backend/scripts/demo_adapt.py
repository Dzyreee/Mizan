"""CLI demo of the FULL agentic loop, on one continuous trace:

    assess (Aura STT) -> diagnose (Fanar-27B) -> plan (Fanar-27B)
                      -> generate (Diwan verse + Oryx-IG art + Aura TTS)

Self-contained (needs VPN): synthesizes a misread reading, runs everything, prints the
unified trace, and saves the illustration + pronunciation clips to smoke/_out/.

    cd backend && .venv/bin/python -m scripts.demo_adapt
    cd backend && .venv/bin/python -m scripts.demo_adapt --no-image   # faster
"""
from __future__ import annotations

import argparse
import base64
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agent.adapt import adapt          # noqa: E402
from app.agent.assess import assess        # noqa: E402
from app.agent.trace import Trace          # noqa: E402

TARGET = "ذهب الولد الصغير إلى المدرسة في الصباح"
MISREAD = "ذهب الورد إلى المدرسة في المساء"
OUT = Path(__file__).resolve().parents[1] / "smoke" / "_out"


def _save(b64: str, path: Path) -> None:
    path.write_bytes(base64.b64decode(b64))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-image", action="store_true", help="skip Oryx-IG (faster)")
    ap.add_argument("--no-audio", action="store_true", help="skip Aura TTS clips")
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)

    trace = Trace()  # one trace threaded through the whole loop

    # 1-2-3) assess + diagnose (synthesize a misread first so STT has audio).
    from app.fanar.tts import synthesize
    audio = Path(tempfile.gettempdir()) / "naghami_loop.mp3"
    audio.write_bytes(synthesize(MISREAD, voice="Noor"))
    assessment = assess(TARGET, audio_path=audio, trace=trace)
    diagnosis = assessment["diagnosis"]

    # 4-5) plan + generate (same trace).
    result = adapt(diagnosis, trace=trace,
                   include_image=not args.no_image, include_audio=not args.no_audio)
    plan, gen = result["plan"], result["generated"]

    # ---- unified trace ----
    print("\n══════════ AGENT TRACE (full loop) ══════════")
    for i, s in enumerate(trace.to_dict()["steps"], 1):
        flag = "" if s["status"] == "ok" else f"  !! {s['error']}"
        print(f"[{i}] {s['name']:15} {s['model']:28} {s['latency_ms']:>6} ms{flag}")
        print(f"     → {s['summary']}")
    print(f"    total: {trace.to_dict()['total_latency_ms']} ms")

    # ---- assessment ----
    em = assessment["error_map"]
    print("\n══════════ ASSESS ══════════")
    print(f"  target    : {TARGET}")
    print(f"  transcript: {assessment['transcript']}")
    print(f"  accuracy  : {em['accuracy_pct']}%  miscues {em['counts']}")
    print(f"  weak sounds (diagnosis): {diagnosis.get('weak_sounds')}")

    # ---- generated exercise ----
    print("\n══════════ ADAPTIVE EXERCISE ══════════")
    print(f"  title          : {plan.get('title')}")
    print(f"  target sounds  : {plan.get('target_sounds')}")
    print(f"  practice words : {plan.get('practice_words')}")
    print(f"  practice text  : {plan.get('practice_passage')}")
    print("  --- Diwan/Fanar verse ---")
    for line in (gen["verse"] or "").splitlines():
        print("    " + line)

    if gen.get("illustration"):
        p = OUT / "adapt_illustration.png"
        _save(gen["illustration"]["b64"], p)
        print(f"  illustration   : saved {p} ({gen['illustration']['bytes']} bytes)")
    for i, pr in enumerate(gen.get("pronunciations", []), 1):
        p = OUT / f"adapt_word_{i}.mp3"
        _save(pr["b64"], p)
        print(f"  pronounce '{pr['word']}' : saved {p} ({pr['bytes']} bytes)")


if __name__ == "__main__":
    main()
