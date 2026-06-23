"""Pipeline wiring tests that need NO network (transcript supplied, diagnosis off).
The live STT + Fanar diagnosis are exercised by scripts/demo_assess.py.
"""
from app.agent.assess import assess
from app.agent.diagnose import summarize_error_map
from app.agent.trace import DETERMINISTIC, Trace
from app.engine import analyze


def test_assess_with_transcript_no_diagnose():
    result = assess("ذهب الولد إلى المدرسة",
                    transcript="ذهب الورد إلى المدرسة",
                    do_diagnose=False)
    assert result["error_map"]["accuracy_pct"] == 75.0
    assert result["diagnosis"] is None
    names = [s["name"] for s in result["trace"]["steps"]]
    assert names == ["align"]                       # no transcribe (transcript given), no diagnose
    assert result["trace"]["steps"][0]["model"] == DETERMINISTIC


def test_assess_requires_audio_or_transcript():
    import pytest
    with pytest.raises(ValueError):
        assess("ذهب الولد", do_diagnose=False)


def test_trace_records_latency_and_serializes():
    import json
    tr = Trace()
    with tr.step("align", model=DETERMINISTIC, input={"x": 1}) as st:
        st.set_output({"ok": True}, summary="done")
    d = tr.to_dict()
    assert d["steps"][0]["name"] == "align"
    assert d["steps"][0]["status"] == "ok"
    assert d["steps"][0]["latency_ms"] >= 0
    json.dumps(d)                                   # serializable for the API/UI


def test_trace_captures_errors():
    tr = Trace()
    try:
        with tr.step("boom", model="x"):
            raise RuntimeError("kaboom")
    except RuntimeError:
        pass
    assert tr.steps[0].status == "error"
    assert "kaboom" in tr.steps[0].error


def test_summarize_error_map_shape():
    em = analyze("ذهب الولد إلى المدرسة في الصباح",
                 "ذهب الورد إلى المدرسة في المساء")
    facts = summarize_error_map(em)
    assert facts["miscue_counts"] == {"substitution": 2}
    assert {"expected": "الولد", "read_as": "الورد"} in facts["substitutions"]
    assert facts["accuracy_pct"] == 66.7
