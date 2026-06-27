"""THE CRITICAL TEST, the Aura STT faithfulness gate.

Iqra detects reading errors by comparing a transcript of the child to a KNOWN
target text. That only works if Aura STT transcribes what was ACTUALLY said,
errors and all, i.e. it must NOT silently "correct" misreadings toward fluent text.

How we test it without a child recording:
  TARGET  = the correct passage.
  MISREAD = the SAME passage with 3 deliberate, plausible miscues:
            1) whole-word substitution  الولد -> الورد   (ل/ر swap)
            2) within-word emphatic swap المدرسة -> المدرصة (س -> ص, a real child error)
            3) semantic word swap        الصباح -> المساء
  We synthesize MISREAD with Aura TTS (so the audio genuinely contains the miscues),
  then transcribe it with Aura STT and check, per error, whether the transcript kept
  the MISREAD form (FAITHFUL = good) or snapped back to the TARGET form (NORMALIZED = bad).

Verdict decides Iqra's whole error-detection strategy (Phase 1):
  - FAITHFUL  -> substitutions are trustworthy; use full miscue classification.
  - NORMALIZED-> lean on omissions/insertions/timing signals that survive normalization.

Run (after 02/03 confirm TTS+STT work): python smoke/10_faithfulness_gate.py
"""
import re

import _common as c
from app.fanar.stt import transcribe
from app.fanar.tts import synthesize

TARGET = "ذهب الولد إلى المدرسة في الصباح"
MISREAD = "ذهب الورد إلى المدرصة في المساء"

# (human label, correct form, misread form)
ERRORS = [
    ("whole-word sub (ل/ر)", "الولد", "الورد"),
    ("emphatic sub (س->ص)", "المدرسة", "المدرصة"),
    ("semantic swap", "الصباح", "المساء"),
]

_TASHKEEL = re.compile(r"[ؐ-ًؚ-ٰٟۖ-ۭـ]")


def norm(s: str) -> str:
    """Strip Arabic diacritics/tatweel + punctuation so we compare consonant skeletons."""
    s = _TASHKEEL.sub("", s)
    s = (s.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
         .replace("ى", "ي").replace("ة", "ه"))
    return re.sub(r"[^؀-ۿ\s]", " ", s)


def present(word: str, text: str) -> bool:
    return norm(word) in norm(text)


def main() -> None:
    print("[10] FAITHFULNESS GATE")
    print(f"  TARGET : {TARGET}")
    print(f"  MISREAD: {MISREAD}")

    audio = c.OUT / "10_misread.mp3"   # Aura TTS returns MP3 (Phase 0 finding)
    try:
        audio.write_bytes(synthesize(MISREAD, voice="Noor"))
    except Exception as e:  # noqa: BLE001
        c.fail(f"TTS of MISREAD failed: {e}")
        return
    print(f"  synthesized misread audio -> {audio} ({audio.stat().st_size} bytes)")

    transcript = transcribe(audio)
    c.dump("10_faithfulness", {"target": TARGET, "misread": MISREAD, "transcript": transcript})
    print(f"  STT transcript: {transcript!r}")

    faithful = normalized = ambiguous = 0
    print("\n  per-error result:")
    for label, correct, misread in ERRORS:
        has_misread = present(misread, transcript)
        has_correct = present(correct, transcript)
        if has_misread and not has_correct:
            verdict = "FAITHFUL ✅ (kept the miscue)"
            faithful += 1
        elif has_correct and not has_misread:
            verdict = "NORMALIZED ❌ (snapped to target)"
            normalized += 1
        else:
            verdict = f"AMBIGUOUS (misread={has_misread}, correct={has_correct})"
            ambiguous += 1
        print(f"    - {label:22} {verdict}")

    print(f"\n  TALLY: faithful={faithful}  normalized={normalized}  ambiguous={ambiguous}")
    if faithful >= 2 and normalized == 0:
        print("  ==> VERDICT: Aura PRESERVES reading errors. Full miscue classification is safe.")
    elif normalized >= 2:
        print("  ==> VERDICT: Aura NORMALIZES. Engine must lean on omissions/insertions/timing.")
    else:
        print("  ==> VERDICT: MIXED. Record details; design engine defensively.")


if __name__ == "__main__":
    main()
