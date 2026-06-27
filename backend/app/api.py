"""Iqra FastAPI backend.

Run from backend/:  .venv/bin/uvicorn app.api:app --reload --port 8000
"""
from __future__ import annotations

import os
import tempfile
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.agent.adapt import adapt
from app.agent.assess import assess
from app.memory import build_progress, load_profile, record_session

app = FastAPI(title="Iqra API",
              description="Adaptive Arabic reading-support tutor for children.")

# Dev-friendly CORS for the Next.js frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "iqra"}


@app.post("/assess")
async def assess_endpoint(
    target_text: str = Form(...),
    audio: Optional[UploadFile] = File(None),
    transcript: Optional[str] = Form(None),
    duration_sec: Optional[float] = Form(None),
    child_id: Optional[str] = Form(None),
    child_name: Optional[str] = Form(None),
):
    """Assess a reading attempt.

    Send multipart form-data with `target_text` plus EITHER an `audio` file (the child's
    recording, Aura STT transcribes it) OR a `transcript` string (offline/testing).
    If `child_id` is given, the session is recorded to that child's profile for progress
    tracking. Returns transcript, deterministic error map, the Fanar diagnosis, the trace,
    and (when recorded) `recorded: true`.
    """
    if audio is None and not transcript:
        raise HTTPException(status_code=400,
                            detail="Provide an 'audio' file or a 'transcript'.")

    audio_path = None
    try:
        if audio is not None:
            suffix = os.path.splitext(audio.filename or "")[1] or ".mp3"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(await audio.read())
                audio_path = tmp.name
        try:
            result = assess(target_text, audio_path=audio_path, transcript=transcript,
                            duration_sec=duration_sec)
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=502, detail=f"Assessment failed: {exc}")
    finally:
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)

    # Persist the session for cross-session progress (deterministic per-sound accuracy).
    if child_id:
        em = result["error_map"]
        weak = (result.get("diagnosis") or {}).get("weak_sounds") or []
        record_session(
            child_id,
            target_text=target_text,
            transcript=result["transcript"],
            words=em["words"],
            accuracy_pct=em["accuracy_pct"],
            wpm=em["wpm"],
            miscue_counts=em["counts"],
            weak_sounds=weak,
            name=child_name or "",
        )
        result["recorded"] = True
    return result


class AdaptRequest(BaseModel):
    diagnosis: dict
    include_image: bool = True
    include_audio: bool = True


class Candidate(BaseModel):
    id: str
    description: str


class PickRequest(BaseModel):
    text: str
    candidates: list[Candidate]


class SpeakRequest(BaseModel):
    text: str


@app.post("/speak")
def speak_endpoint(req: SpeakRequest):
    """Aura TTS for arbitrary text → base64 MP3 (`{b64, mime}`). Used for the Diwan
    full-verse playback and the per-word reading hints (lazy, on tap)."""
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Provide text.")
    import base64
    from app.fanar.tts import synthesize
    try:
        audio = synthesize(req.text)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Speech failed: {exc}")
    return {"b64": base64.b64encode(audio).decode(), "mime": "audio/mpeg"}


@app.post("/pick-illustration")
def pick_illustration_endpoint(req: PickRequest):
    """Fanar picks the most relevant pre-generated illustration for `text` from the given
    `candidates` (each {id, description}). Fast text call, no image generation. Returns the
    chosen `{id}` (falls back to the first candidate on any model error)."""
    if not req.candidates:
        raise HTTPException(status_code=400, detail="Provide candidates.")
    from app.agent.pick_image import pick_image
    chosen = pick_image(req.text, [c.model_dump() for c in req.candidates])
    return {"id": chosen}


@app.get("/progress")
def progress_endpoint(child_id: str):
    """Cross-session progress for a child: per-sound trend (improving/declining/flat with
    the accuracy series) plus overall accuracy/WPM series."""
    profile = load_profile(child_id)
    if profile is None:
        raise HTTPException(status_code=404, detail=f"No profile for child_id '{child_id}'.")
    return build_progress(profile)


def _arabic_summary(prog: dict) -> str:
    parts = [f"{prog['name']} أكمل {prog['sessions_count']} جلسات قراءة."]
    for s in prog["sounds"]:
        trend = "تحسّن" if s["delta"] > 0 else "تراجع" if s["delta"] < 0 else "ثبات"
        parts.append(f"حرف «{s['sound']}»: من {s['first']}٪ إلى {s['latest']}٪ ({trend}).")
    return " ".join(parts)


@app.get("/progress/summary")
def progress_summary_endpoint(child_id: str, lang: str = "ar"):
    """A short progress summary for a parent. `lang=en` uses Shaheen to translate it for
    non-Arabic-speaking (expat) parents."""
    profile = load_profile(child_id)
    if profile is None:
        raise HTTPException(status_code=404, detail=f"No profile for child_id '{child_id}'.")
    ar = _arabic_summary(build_progress(profile))
    if lang == "en":
        from app.fanar.translate import translate
        try:
            return {"child_id": child_id, "lang": "en", "summary": translate(ar),
                    "summary_ar": ar}
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=502, detail=f"Translation failed: {exc}")
    return {"child_id": child_id, "lang": "ar", "summary": ar}


@app.post("/read-page")
async def read_page_endpoint(image: UploadFile = File(...)):
    """Stretch: set the target passage from a photographed book page (Oryx-IVU OCR).
    Returns the Arabic text read from the image."""
    from app.fanar.vision import read_image
    data = await image.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty image upload.")
    try:
        text = read_image(data, mime=image.content_type or "image/png")
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Page read failed: {exc}")
    return {"target_text": text}


@app.post("/adapt")
def adapt_endpoint(req: AdaptRequest):
    """Generate a targeted exercise from a diagnosis (the `diagnosis` object returned by
    /assess). Returns the plan, generated media (verse + base64 illustration + base64
    pronunciation audio), and the trace."""
    if not req.diagnosis:
        raise HTTPException(status_code=400, detail="Provide a 'diagnosis' object.")
    try:
        return adapt(req.diagnosis, include_image=req.include_image,
                     include_audio=req.include_audio)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Adapt failed: {exc}")
