"""Mizan FastAPI app. Run: uvicorn app.api:app --reload (from backend/)."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.agent.orchestrator import solve

app = FastAPI(title="Mizan API", version="0.2.0")

# Allow the Next.js dev frontend to call us.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class SolveRequest(BaseModel):
    question: str
    verify: bool = True  # set false for the LLM-only ablation


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.post("/solve")
def solve_endpoint(req: SolveRequest) -> dict:
    answer, trace = solve(req.question, verify_pipeline=req.verify)
    return {"answer": answer, "trace": trace.to_dict()}
