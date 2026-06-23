"""Smoke test: Oryx-IG Arabic-aware image generation. Saves the result to _out/.
Used later only for a DECORATIVE certificate banner, never for legal Arabic text
(HARD RULE 4). Run: python smoke/06_oryx_ig.py
"""
import base64

import _common as c

from app.fanar.client import openai_client
from app.fanar.models import ORYX_IG

PROMPT = "An elegant Islamic geometric ornamental header banner, gold on deep green, symmetrical arabesque, no text."


def main() -> None:
    print(f"[06] Oryx-IG image generation — model={ORYX_IG!r}")
    client = openai_client()
    try:
        resp = client.images.generate(model=ORYX_IG, prompt=PROMPT, n=1)
        c.dump("06_oryx_ig", resp.model_dump())
        item = resp.data[0]
        if getattr(item, "b64_json", None):
            out = c.OUT / "06_oryx_ig.png"
            out.write_bytes(base64.b64decode(item.b64_json))
            c.ok(f"image (b64) saved -> {out}")
        elif getattr(item, "url", None):
            c.ok(f"image URL returned: {item.url}")
        else:
            c.fail("response had neither b64_json nor url — see _out/06_oryx_ig.json")
    except Exception as e:  # noqa: BLE001
        c.fail(f"images.generate shape failed: {e}")
        print("    -> record the correct image endpoint/shape, then adapt.")


if __name__ == "__main__":
    main()
