"""Naghami FastAPI backend.

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

app = FastAPI(title="Naghami API",
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
    return {"status": "ok", "service": "naghami"}


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
    recording — Aura STT transcribes it) OR a `transcript` string (offline/testing).
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


@app.get("/progress")
def progress_endpoint(child_id: str):
    """Cross-session progress for a child: per-sound trend (improving/declining/flat with
    the accuracy series) plus overall accuracy/WPM series."""
    profile = load_profile(child_id)
    if profile is None:
        raise HTTPException(status_code=404, detail=f"No profile for child_id '{child_id}'.")
    return build_progress(profile)


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
