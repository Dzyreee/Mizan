"""Quick visual demo of the engine. Run from backend/:  python -m app.engine

Uses the Phase 0 faithfulness scenario so you can see the engine catch exactly the
miscues that survived Aura's normalization.
"""
from app.engine import analyze
from app.engine.errormap import ST_CORRECT

# Colour helpers (fall back to plain text if the terminal is dumb).
_C = {"correct": "\033[92m", "substitution": "\033[91m", "omission": "\033[93m",
      "reset": "\033[0m", "dim": "\033[2m"}


def _show(title, target, transcript, **kw):
    em = analyze(target, transcript, **kw)
    print(f"\n=== {title} ===")
    print(f"  target    : {target}")
    print(f"  transcript: {transcript}")
    # Per-word highlight.
    rendered = []
    for w in em.words:
        c = _C.get(w.status, "")
        mark = w.target if w.status == ST_CORRECT else f"{w.target}"
        rendered.append(f"{c}{mark}{_C['reset']}")
    print("  reading   : " + " ".join(rendered))
    if em.extras:
        print("  extra     : " + ", ".join(f"{e.word} ({e.type})" for e in em.extras))
    print(f"  accuracy  : {em.accuracy_pct}%  ({em.correct_words}/{em.total_target_words})")
    if em.wpm is not None:
        print(f"  speed     : {em.wpm} wpm  ({em.wcpm} wcpm)")
    if em.timestamps_available:
        print(f"  hesitations: {[(h.before_word, h.gap_sec) for h in em.hesitations]}")
    print(f"  miscues   : {em.counts or '{}'}")


def main():
    print("Iqra engine demo, legend: "
          f"{_C['correct']}correct{_C['reset']} "
          f"{_C['substitution']}substitution{_C['reset']} "
          f"{_C['omission']}omission{_C['reset']}")

    _show("Phase 0 faithfulness scenario (real-word miscues survive)",
          "ذهب الولد إلى المدرسة في الصباح",
          "ذهب الورد إلى المدرسة في المساء")

    _show("Omission + self-correction",
          "قطتي الصغيرة تحب اللعب",
          "قطتي الصغيرة تحب",
          duration_sec=10.0)

    _show("Repetition with timing + a long hesitation",
          "البيت كبير وجميل",
          "البيت البيت كبير وجميل",
          word_timestamps=[
              {"word": "البيت", "start": 0.0, "end": 0.6},
              {"word": "البيت", "start": 0.7, "end": 1.3},
              {"word": "كبير", "start": 3.0, "end": 3.6},   # ~1.7s pause before this
              {"word": "وجميل", "start": 3.7, "end": 4.4},
          ])


if __name__ == "__main__":
    main()
