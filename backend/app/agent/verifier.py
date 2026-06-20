"""Independent verifier — the core "verified high-stakes reasoning" claim.

The deterministic calculator is ground truth. The verifier is a SEPARATE agent path that
independently extracts the shares asserted by the Islamic-RAG ruling, then reconciles them
against the deterministic result. If they disagree, nothing is presented as "verified".

Split into:
  - extract_ruling_shares(): LLM call (uses a different model than the planner for independence)
  - reconcile(): pure, deterministic comparison — unit-tested without any LLM
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Dict, List, Optional, Tuple

from openai import BadRequestError

from app.fanar.chat import complete_json
from app.fanar.models import CHAT_C2
from app.faraid import Distribution

# The verifier independently READS the authoritative Islamic ruling and extracts the share
# it asserts for each heir, then reconciles against the deterministic calculator. Extraction
# (reading) is filter-safe on a base model, unlike asking a base model to COMPUTE shares
# (which Fanar's content filter blocks). Different model from the planner = independent path.
VERIFIER_MODEL = CHAT_C2
_HEIR_KEYS = ("husband", "wife", "son", "daughter", "father", "mother")

_SYS = (
    "You are a text-analysis function. The user message is a passage of text to read; do not "
    "answer or continue it. Extract the fraction of the estate the passage assigns to each "
    "heir CLASS. Map Arabic share words to fractions (الثمن=1/8, الربع=1/4, السدس=1/6, "
    "الثلث=1/3, النصف=1/2, الثلثان=2/3). "
    "Output ONLY JSON: {\"shares\": {\"<heir>\": \"<fraction>\"}} where <heir> is one of "
    "husband, wife, son, daughter, father, mother (singular keys, class totals) and "
    "<fraction> is like \"1/8\". Only heirs the passage assigns a share to. JSON only."
)


@dataclass
class HeirComparison:
    heir: str
    deterministic: Optional[str]   # fraction string or None
    ruling: Optional[str]
    basis: Optional[str]           # "fard" | "residue" | "awl" | "radd"
    status: str                    # "match" | "mismatch" | "not_stated" | "informational"

    @property
    def agree(self) -> bool:
        return self.status in ("match", "informational", "not_stated")


@dataclass
class VerificationResult:
    agree: bool
    comparisons: List[HeirComparison]
    issues: List[str] = field(default_factory=list)
    verifier_shares: Optional[dict] = None

    def to_dict(self) -> dict:
        return {
            "agree": self.agree,
            "verdict": "MATCH — verified" if self.agree else "MISMATCH — not verified",
            "comparisons": [c.__dict__ for c in self.comparisons],
            "issues": self.issues,
            "verifier_shares": self.verifier_shares,
        }


def _parse_fraction(s) -> Optional[Fraction]:
    try:
        s = str(s).strip()
        return Fraction(s) if s else None
    except (ValueError, ZeroDivisionError):
        return None


def reconcile(distribution: Distribution,
              ruling_shares: Dict[str, Fraction]) -> VerificationResult:
    """Reconcile the ruling's stated shares against the deterministic result.

    We HARD-CHECK the fixed (fard) shares — the Quranic portions Sadiq states reliably and
    that are a real source of error (e.g. spouse 1/8 vs 1/4 depending on children). Residue,
    'awl, and radd are derived ARITHMETIC the deterministic engine owns; LLMs can't state
    them precisely, so a divergence there is informational, not a verdict failure.
    """
    det: Dict[str, "object"] = {s.heir: s for s in distribution.shares}
    heirs = [k for k in _HEIR_KEYS if k in det or k in ruling_shares]
    comparisons: List[HeirComparison] = []
    issues: List[str] = []
    agree = True

    for h in heirs:
        share = det.get(h)
        d = share.fraction if share else None
        r = ruling_shares.get(h)
        basis = share.basis if share else None

        if share is None:
            # Ruling asserts a heir the calculator has none of -> real problem.
            status = "mismatch"
            agree = False
            issues.append(f"ruling assigns '{h}' a share but the calculator has no such heir")
        elif basis == "fard":
            if r is None:
                status = "not_stated"  # soft: ruling didn't spell out this fixed share
            elif d == r:
                status = "match"
            else:
                status = "mismatch"
                agree = False
                issues.append(f"{h} (fixed share): ruling says {r}, calculator says {d}")
        else:
            # residue / 'awl / radd — informational only
            status = "match" if (r is not None and d == r) else "informational"

        comparisons.append(HeirComparison(
            heir=h,
            deterministic=str(d) if d is not None else None,
            ruling=str(r) if r is not None else None,
            basis=basis,
            status=status,
        ))
    return VerificationResult(agree=agree, comparisons=comparisons, issues=issues)


def extract_ruling_shares(ruling_text: str,
                          model: str = VERIFIER_MODEL) -> Tuple[Dict[str, Fraction], Optional[str]]:
    """Read the ruling and extract the share it asserts per heir class.
    Returns (shares, error). On failure, error is set and shares is empty."""
    try:
        data, _ = complete_json(_SYS, ruling_text, model=model, max_tokens=300)
    except BadRequestError as e:
        return {}, f"verifier call blocked by Fanar safety filter ({e.code or 'content_filter'})"
    except (ValueError, json.JSONDecodeError) as e:
        return {}, f"verifier could not extract structured shares ({e})"
    out: Dict[str, Fraction] = {}
    for heir, val in (data.get("shares") or {}).items():
        key = str(heir).lower().strip()
        frac = _parse_fraction(val)
        if key in _HEIR_KEYS and frac is not None:
            out[key] = frac
    return out, None


def verify(distribution: Distribution, ruling_text: str,
           model: str = VERIFIER_MODEL) -> VerificationResult:
    ruling_shares, err = extract_ruling_shares(ruling_text, model=model)
    result = reconcile(distribution, ruling_shares)
    if err:
        result.agree = False
        result.issues.insert(0, err)
    result.verifier_shares = {k: str(v) for k, v in ruling_shares.items()}
    return result
