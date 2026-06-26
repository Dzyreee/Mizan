"""Phase 6 offline tests: Shaheen translate wiring + the Arabic progress summary endpoint.
Live FanarGuard/Shaheen/IVU behaviour is exercised by eval/harness.py and api smoke calls.
"""
import app.fanar.translate as translate_mod
import app.memory.store as store
from app.engine import analyze
from app.memory import record_session


def test_translate_offline(monkeypatch):
    class _Resp:
        def raise_for_status(self): pass
        def json(self): return {"text": "Layan improved."}

    class _Client:
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def post(self, *a, **k): return _Resp()

    monkeypatch.setattr(translate_mod, "httpx_client", lambda *a, **k: _Client())
    assert translate_mod.translate("ليان تحسّنت.") == "Layan improved."
    assert translate_mod.translate("") == ""        # empty short-circuits (no call)


def test_progress_summary_endpoint_arabic(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "DATA_DIR", tmp_path)
    target = "صعد الصقر فوق الصخرة"
    for date, tr in [("2026-06-10", "سعد الصقر فوق الصخرة"),
                     ("2026-06-17", "صعد الصقر فوق الصخرة")]:
        em = analyze(target, tr)
        record_session("k", target_text=target, transcript=tr, words=em.to_dict()["words"],
                       accuracy_pct=em.accuracy_pct, wpm=em.wpm, miscue_counts=em.counts,
                       weak_sounds=["ص"], name="نور", date=date)

    from fastapi.testclient import TestClient
    from app.api import app
    j = TestClient(app).get("/progress/summary", params={"child_id": "k"}).json()
    assert j["lang"] == "ar"
    assert "نور" in j["summary"] and "ص" in j["summary"]
