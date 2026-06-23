"""Phase 0 discovery: list every model the key can see. Run: python smoke/00_list_models.py"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.fanar.client import httpx_client


def main() -> None:
    # NOTE: Fanar's /v1/models is NOT OpenAI-shaped — payload key is "models", not "data",
    # so the openai SDK's models.list() returns None. Use a raw GET.
    with httpx_client() as client:
        body = client.get("/models").json()
    rows = sorted((m["id"] for m in body.get("models", [])), key=str.lower)
    print(f"Discovered {len(rows)} models:\n")
    for mid in rows:
        print(f"  - {mid}")
    out = Path(__file__).parent / "_out"
    out.mkdir(exist_ok=True)
    (out / "models.json").write_text(json.dumps(body, indent=2, ensure_ascii=False))
    print(f"\nRaw payload written to {out / 'models.json'}")


if __name__ == "__main__":
    main()
