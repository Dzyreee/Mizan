"""Per-child memory + deterministic progress (no network)."""
import app.memory.store as store
from app.engine import analyze
from app.memory import build_progress, load_profile, record_session
from app.memory.progress import per_sound_accuracy


def test_per_sound_accuracy_counts_only_words_with_the_sound():
    em = analyze("صعد الصقر فوق الصخرة", "سعد السقر فوق الصخرة")  # 2 of 3 ص-words wrong
    words = em.to_dict()["words"]
    info = per_sound_accuracy(words, "ص")
    assert info == {"accuracy": 33.3, "n_words": 3, "n_correct": 1}
    # A sound that never appears in the passage isn't charted.
    assert per_sound_accuracy(words, "ز") is None


def test_record_and_load_round_trip(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "DATA_DIR", tmp_path)
    em = analyze("صعد الصقر", "سعد الصقر", duration_sec=12.0)
    record_session("kid1", target_text="صعد الصقر", transcript="سعد الصقر",
                   words=em.to_dict()["words"], accuracy_pct=em.accuracy_pct, wpm=em.wpm,
                   miscue_counts=em.counts, weak_sounds=["ص"], name="نور")
    p = load_profile("kid1")
    assert p is not None and p.name == "نور"
    assert len(p.sessions) == 1
    assert p.sessions[0].per_sound["ص"]["n_words"] == 2
    assert load_profile("nobody") is None


def test_progress_trend_improves_across_sessions(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "DATA_DIR", tmp_path)
    target = "صعد الصقر فوق الصخرة ورأى البحر"
    reads = [
        ("2026-06-10", "سعد السقر فوق الصخرة وراء البحر"),
        ("2026-06-17", "صعد السقر فوق الصخرة ورأى البحر"),
        ("2026-06-24", "صعد الصقر فوق الصخرة ورأى البحر"),
    ]
    for date, transcript in reads:
        em = analyze(target, transcript)
        record_session("kid2", target_text=target, transcript=transcript,
                       words=em.to_dict()["words"], accuracy_pct=em.accuracy_pct,
                       wpm=em.wpm, miscue_counts=em.counts, weak_sounds=["ص", "ر"], date=date)

    prog = build_progress(load_profile("kid2"))
    assert prog["sessions_count"] == 3
    sad = next(s for s in prog["sounds"] if s["sound"] == "ص")
    assert [pt["accuracy"] for pt in sad["series"]] == [33.3, 66.7, 100.0]
    assert sad["trend"] == "improving" and sad["delta"] == 66.7
    ra = next(s for s in prog["sounds"] if s["sound"] == "ر")
    assert [pt["accuracy"] for pt in ra["series"]] == [50.0, 75.0, 100.0]


def test_progress_endpoint(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "DATA_DIR", tmp_path)
    em = analyze("صعد الصقر", "صعد الصقر")
    record_session("kid3", target_text="صعد الصقر", transcript="صعد الصقر",
                   words=em.to_dict()["words"], accuracy_pct=em.accuracy_pct, wpm=em.wpm,
                   miscue_counts=em.counts, weak_sounds=["ص"], name="سارة")

    from fastapi.testclient import TestClient
    from app.api import app
    c = TestClient(app)
    r = c.get("/progress", params={"child_id": "kid3"})
    assert r.status_code == 200 and r.json()["name"] == "سارة"
    assert c.get("/progress", params={"child_id": "ghost"}).status_code == 404
