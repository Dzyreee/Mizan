"""One-time generator for the shared illustration library (Oryx-IG).

Generates a small fixed set of kid-friendly scenes and saves them to
frontend/public/library/<id>.png. At runtime Fanar PICKS the best-matching image for a
passage/poem (a fast text call) — so this slow generation only ever runs once. Re-run only
if you change the library list below (keep ids in sync with frontend/lib/library.ts).

    cd backend && .venv/bin/python -m scripts.gen_library
    cd backend && .venv/bin/python -m scripts.gen_library --only school sea autumn
    cd backend && .venv/bin/python -m scripts.gen_library --force   # overwrite

Needs the Fanar key in .env + VPN. Oryx-IG renders DECORATIVE art only — the prompt
forbids text/letters (Arabic letterforms are unreliable).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.fanar.image import generate_image  # noqa: E402

OUT_DIR = Path(__file__).resolve().parents[2] / "frontend" / "public" / "library"

# id -> English scene prompt. ids must match frontend/lib/library.ts.
LIBRARY = {
    "school": "a young child walking to school with a backpack",
    "park": "children playing with a ball in a green park",
    "cat": "a small cat drinking milk at home",
    "bedtime": "a child reading a storybook in bed at night",
    "birds": "small birds singing on tree branches in a blue sky",
    "autumn": "children playing among falling golden autumn leaves",
    "sea": "children swimming at a blue beach in summer",
    "family": "a happy family eating a meal together at a table",
    "sun": "a bright sun rising over green hills in the morning",
    "rain": "a child holding an umbrella in the rain",
    "garden": "a child watering colorful flowers in a garden",
    "music": "a child singing happily with music notes floating around",
}

PROMPT = (
    "Simple, friendly children's book illustration of: {scene}. "
    "Flat soft colors, rounded shapes, cheerful, light sky-blue palette, "
    "white background, no text, no letters, no words."
)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*", help="only these library ids")
    ap.add_argument("--force", action="store_true", help="overwrite existing files")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ids = args.only or list(LIBRARY)
    for i in ids:
        if i not in LIBRARY:
            print(f"! unknown id '{i}' — skip")
            continue
        out = OUT_DIR / f"{i}.png"
        if out.exists() and not args.force:
            print(f"· {i}.png exists — skip (use --force to redo)")
            continue
        print(f"… generating {i}.png  ({LIBRARY[i]})")
        png = generate_image(PROMPT.format(scene=LIBRARY[i]))
        out.write_bytes(png)
        print(f"✓ wrote {out}  ({len(png)} bytes)")
    print("done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
