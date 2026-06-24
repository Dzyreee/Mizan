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

    # trace shows plan -> generate (the loop's second half)
    names = [s["name"] for s in result["trace"]["steps"]]
    assert names == ["plan", "generate-verse", "generate-image", "generate-audio"]


def test_adapt_can_skip_media(monkeypatch):
    _patch(monkeypatch)
    result = adapt({"weak_sounds": ["ص"]}, include_image=False, include_audio=False)
    assert result["generated"]["illustration"] is None
    assert result["generated"]["pronunciations"] == []
    names = [s["name"] for s in result["trace"]["steps"]]
    assert names == ["plan", "generate-verse"]


def test_adapt_appends_to_shared_trace(monkeypatch):
    _patch(monkeypatch)
    trace = Trace()
    with trace.step("diagnose", model="Fanar-C-2-27B"):
        pass
    adapt({"weak_sounds": ["ص"]}, trace=trace, include_image=False, include_audio=False)
    names = [s.name for s in trace.steps]
    assert names == ["diagnose", "plan", "generate-verse"]  # one continuous loop
