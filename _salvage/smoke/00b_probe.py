"""Discovery probe: see /models shape, and use invalid-model 422s to enumerate valid
model IDs per endpoint (the API lists allowed enum values in the error)."""
import json

import _common as c
from app.fanar.client import httpx_client


def section(t):
    print(f"\n=== {t} ===")


def main():
    with httpx_client() as cl:
        section("GET /models (raw)")
        r = cl.get("/models")
        print("HTTP", r.status_code)
        try:
            body = r.json()
            c.dump("00b_models_raw", body)
            print(json.dumps(body, ensure_ascii=False)[:800])
        except Exception:
            print(r.text[:500])

        # Invalid-model probes — the 422 enum reveals valid ids for each endpoint.
        probes = {
            "chat/completions": {"model": "__x__", "messages": [{"role": "user", "content": "hi"}]},
            "images/generations": {"model": "__x__", "prompt": "x"},
            "audio/translations": {"model": "__x__"},
        }
        for path, payload in probes.items():
            section(f"POST /{path}  (invalid-model probe)")
            r = cl.post("/" + path, json=payload)
            print("HTTP", r.status_code)
            print(r.text[:400])


if __name__ == "__main__":
    main()
