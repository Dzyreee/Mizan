"""Unit tests for the deterministic agent pieces (no LLM / network)."""
from fractions import Fraction as F

from app.agent.trace import Trace
from app.agent.verifier import reconcile
from app.faraid import Heirs, compute_inheritance
from app.fanar.islamic import parse_citations


# ---------- citation parsing ----------
def test_parse_citations_extracts_and_cleans():
    raw = ("للزوجة الثمن، قال الله تعالى: <quran_start>فَلَهُنَّ ٱلثُّمُنُ<quran_end> "
           "وروى البخاري <hadith_start>ألحقوا الفرائض بأهلها<hadith_end>.")
    clean, cites = parse_citations(raw)
    assert len(cites) == 2
    assert cites[0].source == "quran" and "ٱلثُّمُنُ" in cites[0].text
    assert cites[1].source == "hadith"
    assert "<quran_start>" not in clean and "«" in clean


# ---------- verifier reconciliation (pure) ----------
def test_reconcile_agrees_when_ruling_matches_calculator():
    dist = compute_inheritance(Heirs(wives=1, sons=1))  # wife 1/8, son 7/8
    res = reconcile(dist, {"wife": F(1, 8), "son": F(7, 8)})
    assert res.agree is True
    assert all(c.agree for c in res.comparisons)


def test_reconcile_flags_mismatch():
    dist = compute_inheritance(Heirs(wives=1, sons=1))
    res = reconcile(dist, {"wife": F(1, 4), "son": F(3, 4)})  # wrong (LLM-style error)
    assert res.agree is False
    assert any("wife" in i for i in res.issues)


def test_reconcile_ignores_unstated_residuary():
    # husband is fixed (hard-checked); son/daughter are residuary (informational).
    dist = compute_inheritance(Heirs(husband=True, sons=1, daughters=1))
    res = reconcile(dist, {"husband": F(1, 4)})  # only the fixed share stated
    assert res.agree is True
    assert not res.issues


def test_reconcile_flags_wrong_fixed_share():
    # husband WITH children must be 1/4; ruling claiming 1/2 is a real, hard error.
    dist = compute_inheritance(Heirs(husband=True, sons=1, daughters=1))
    res = reconcile(dist, {"husband": F(1, 2)})
    assert res.agree is False
    assert any("husband" in i for i in res.issues)


def test_reconcile_flags_hallucinated_heir():
    dist = compute_inheritance(Heirs(wives=1, sons=1))  # no father
    res = reconcile(dist, {"wife": F(1, 8), "father": F(1, 6)})
    assert res.agree is False
    assert any("father" in i for i in res.issues)


# ---------- trace ----------
def test_trace_records_steps_and_latency():
    t = Trace()
    with t.step("s1", "tool", {"x": 1}) as st:
        st.output = {"y": 2}
    assert len(t.steps) == 1
    assert t.steps[0].status == "ok"
    assert t.steps[0].latency_ms >= 0
    d = t.to_dict()
    assert d["steps"][0]["output"] == {"y": 2}


def test_trace_captures_errors():
    t = Trace()
    try:
        with t.step("boom", "tool", None):
            raise RuntimeError("nope")
    except RuntimeError:
        pass
    assert t.steps[0].status == "error"
    assert "nope" in str(t.steps[0].output)
