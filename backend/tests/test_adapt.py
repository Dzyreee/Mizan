"""Plan/generate/adapt WIRING tests with all Fanar calls monkeypatched (no network).
The live media generation is exercised by scripts/demo_adapt.py.
"""
import base64

import app.agent.generate as gen_mod
import app.agent.plan as plan_mod
from app.agent.adapt import adapt
from app.agent.trace import Trace

FAKE_PLAN = {
    "title": "مغامرة الصاد",
    "target_sounds": ["ص"],
    "practice_words": ["صقر", "عصفور", "قصر"],
    "practice_passage": "صعد الصقر. القصر كبير.",
    "verse_prompt": "اكتب بيتين فيهما حرف الصاد",
    "illustration_prompt": "A cheerful falcon over a castle, no text, no letters",
    "pronunciation_words": ["صقر", "عصفور"],
}


def _patch(monkeypatch):
    monkeypatch.setattr(plan_mod, "complete_json",
                        lambda system, user, model, max_tokens=900: (FAKE_PLAN, "{}"))
    monkeypatch.setattr(gen_mod, "generate_verse",
                        lambda prompt, **kw: "صقرٌ صغير\nفوق القصير")
    monkeypatch.setattr(gen_mod, "generate_image", lambda prompt: b"\x89PNGfakebytes")
    monkeypatch.setattr(gen_mod, "synthesize", lambda text, voice=None: b"ID3fakemp3")
    monkeypatch.setattr(gen_mod, "check_content",
                        lambda text, **kw: {"safe": True, "safety": 4.4,
                                            "cultural_awareness": 4.3, "threshold": 3.0,
                                            "model": "Fanar-Guard-2"})


def test_adapt_full_wiring(monkeypatch):
    _patch(monkeypatch)
    diagnosis = {"weak_sounds": ["ص"], "focus": "حرف الصاد", "patterns": []}
    result = adapt(diagnosis)

    # plan came through
    assert result["plan"]["title"] == "مغامرة الصاد"

    # generated media assembled + base64 round-trips
    gen = result["generated"]
    assert gen["verse"].startswith("صقر")
    assert base64.b64decode(gen["illustration"]["b64"]) == b"\x89PNGfakebytes"
    assert gen["illustration"]["mime"] == "image/png"
    assert [p["word"] for p in gen["pronunciations"]] == ["صقر", "عصفور"]
    assert base64.b64decode(gen["pronunciations"][0]["b64"]) == b"ID3fakemp3"

    # FanarGuard validated the child-facing content
    assert gen["safety"]["safe"] is True and gen["safety"]["model"] == "Fanar-Guard-2"

    # trace shows plan -> generate -> safety-check (the loop's second half)
    names = [s["name"] for s in result["trace"]["steps"]]
    assert names == ["plan", "generate-verse", "generate-image", "generate-audio", "safety-check"]


def test_adapt_can_skip_media(monkeypatch):
    _patch(monkeypatch)
    result = adapt({"weak_sounds": ["ص"]}, include_image=False, include_audio=False)
    assert result["generated"]["illustration"] is None
    assert result["generated"]["pronunciations"] == []
    names = [s["name"] for s in result["trace"]["steps"]]
    assert names == ["plan", "generate-verse", "safety-check"]


def test_adapt_appends_to_shared_trace(monkeypatch):
    _patch(monkeypatch)
    trace = Trace()
    with trace.step("diagnose", model="Fanar-C-2-27B"):
        pass
    adapt({"weak_sounds": ["ص"]}, trace=trace, include_image=False, include_audio=False,
          validate=False)
    names = [s.name for s in trace.steps]
    assert names == ["diagnose", "plan", "generate-verse"]  # one continuous loop


def test_guard_check_content_offline(monkeypatch):
    import app.fanar.guard as guard
    # Simulate the live Fanar-Guard-2 response shape.
    class _Resp:
        status_code = 200
        def raise_for_status(self): pass
        def json(self): return {"safety": 1.0, "cultural_awareness": 0.9}
    class _Client:
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def post(self, *a, **k): return _Resp()
    monkeypatch.setattr(guard, "httpx_client", lambda *a, **k: _Client())
    out = guard.check_content("نص عنيف غير مناسب")
    assert out["safe"] is False and out["safety"] == 1.0
