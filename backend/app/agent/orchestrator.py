"""Orchestrator: the agentic pipeline that the trace panel visualizes.

FULL mode (verified):
    plan -> deterministic calculator -> Islamic-RAG ruling -> independent verifier -> answer
    The answer is only marked `verified` when the verifier reconciles ruling == calculator.

LLM_ONLY mode (ablation):
    plan -> ask the LLM to compute shares directly. No calculator, no verifier.
    This is the toggle for demonstrating the LLM getting 'awl/radd wrong while the full
    pipeline gets it right.
"""
from __future__ import annotations

import json
import re
from fractions import Fraction
from typing import Tuple

from openai import BadRequestError

from app.agent.planner import PLANNER_MODEL, plan
from app.agent.trace import Trace
from app.agent.verifier import VERIFIER_MODEL, verify
from app.fanar.chat import chat
from app.fanar.islamic import get_ruling
from app.fanar.models import CHAT, ISLAMIC
from app.faraid import Distribution, compute_inheritance


def _money(estate: float, frac: Fraction) -> float:
    return round(estate * float(frac), 2)


def _amounts(distribution: Distribution, estate: float, currency: str) -> list:
    rows = []
    for s in distribution.shares:
        rows.append({
            "heir": s.heir,
            "count": s.count,
            "fraction": str(s.fraction),
            "ratio": s.as_ratio(distribution.base),
            "each": str(s.each),
            "basis": s.basis,
            "amount_total": _money(estate, s.fraction),
            "amount_each": _money(estate, s.each),
            "currency": currency,
        })
    return rows


_LLM_ONLY_SYS = (
    "You are an inheritance assistant. Given the scenario, compute each heir's share of the "
    "estate, correctly accounting for 'awl and radd. Output ONLY JSON: "
    '{"shares": {"<heir>": {"fraction": "x/y", "amount": number}}, "explanation": "..."}'
)
_JSON_OBJ = re.compile(r"\{.*\}", re.DOTALL)


def _llm_only_shares(question: str) -> dict:
    """Ablation: let the LLM compute directly. Resilient to prose / safety-filter blocks so
    the demo always shows whatever (possibly wrong) answer the model gives."""
    try:
        raw = chat([{"role": "system", "content": _LLM_ONLY_SYS},
                    {"role": "user", "content": question}], model=CHAT, max_tokens=600)
    except BadRequestError as e:
        return {"blocked": True, "detail": f"Fanar safety filter ({e.code or 'content_filter'})"}
    m = _JSON_OBJ.search(raw)
    if m:
        try:
            return {"parsed": json.loads(m.group(0)), "raw": raw}
        except json.JSONDecodeError:
            pass
    return {"parsed": None, "raw": raw}  # model answered in prose — show it as-is


def solve(question: str, verify_pipeline: bool = True) -> Tuple[dict, Trace]:
    trace = Trace()

    # 1) PLAN — extract heirs & estate
    with trace.step("Plan: extract heirs & estate", "plan", question, model=PLANNER_MODEL) as st:
        case, _ = plan(question)
        st.output = {"heirs": case.heirs.__dict__, "estate": case.estate, "currency": case.currency}

    # --- Ablation: LLM-only, no calculator/verifier ---
    if not verify_pipeline:
        with trace.step("LLM-only computation (no calculator, no verifier)", "tool",
                        {"heirs": case.heirs.__dict__, "estate": case.estate}, model=CHAT) as st:
            llm_shares = _llm_only_shares(question)
            st.output = llm_shares
        answer = {
            "mode": "llm_only",
            "verified": False,
            "warning": "Ablation mode: shares are the LLM's own arithmetic, NOT verified.",
            "heirs": case.heirs.__dict__,
            "estate": case.estate,
            "currency": case.currency,
            "llm_shares": llm_shares,
        }
        return answer, trace

    # 2) TOOL — deterministic calculator (ground truth)
    with trace.step("Tool: deterministic faraid calculator", "tool", case.heirs.__dict__) as st:
        dist = compute_inheritance(case.heirs)
        st.output = dist.to_dict()

    # 3) RULING — Islamic-RAG sourced ruling
    with trace.step("Tool: Islamic-RAG ruling + citations", "ruling", question, model=ISLAMIC) as st:
        clean, citations, raw_ruling = get_ruling(question)
        st.output = {"ruling": clean, "citations": [c.to_dict() for c in citations]}

    # 4) VERIFY — reconcile the ruling's stated shares against the deterministic result
    with trace.step("Verifier: reconcile ruling shares vs deterministic", "verify",
                    {"deterministic": dist.to_dict()}, model=VERIFIER_MODEL) as st:
        vres = verify(dist, raw_ruling)
        st.status = "ok" if vres.agree else "mismatch"
        st.output = vres.to_dict()

    # 5) ANSWER — compose only-if-verified
    answer = {
        "mode": "full",
        "verified": vres.agree,
        "verdict": "MATCH — verified" if vres.agree else "MISMATCH — needs human review",
        "heirs": case.heirs.__dict__,
        "estate": case.estate,
        "currency": case.currency,
        "distribution_kind": dist.kind,
        "distribution_note": dist.note,
        "shares": _amounts(dist, case.estate, case.currency),
        "ruling": clean,
        "citations": [c.to_dict() for c in citations],
        "verification": vres.to_dict(),
    }
    return answer, trace
