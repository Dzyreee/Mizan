"""ADAPT: the adaptive action that closes the loop — plan a targeted exercise from the
diagnosis, then generate it (verse + art + audio). Records both steps in the Trace.
"""
from __future__ import annotations

from typing import Optional

from app.agent.generate import generate_exercise
from app.agent.plan import plan_exercise
from app.agent.trace import Trace


def adapt(
    diagnosis: dict,
    trace: Optional[Trace] = None,
    include_image: bool = True,
    include_audio: bool = True,
    validate: bool = True,
) -> dict:
    """diagnosis -> {plan, generated, trace}. Pass a shared `trace` to append onto an
    existing assess+diagnose trace (one continuous loop). `validate` runs FanarGuard on
    the child-facing content."""
    trace = trace or Trace()
    plan = plan_exercise(diagnosis, trace=trace)
    generated = generate_exercise(plan, trace=trace, include_image=include_image,
                                  include_audio=include_audio, validate=validate)
    return {"plan": plan, "generated": generated, "trace": trace.to_dict()}
