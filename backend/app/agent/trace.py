"""A structured, serializable Trace of the pipeline, model used, latency, input and
output for every step. This is what the frontend's live "Agent Trace" panel renders,
and what makes Iqra auditable rather than a black box.
"""
from __future__ import annotations

import json
import time
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from typing import Any, Iterator, List, Optional

# Marker for steps computed in pure Python (no model).
DETERMINISTIC = "deterministic-engine"


def _short(value: Any, limit: int = 800) -> Any:
    """Keep payloads small/serializable for the trace panel."""
    if value is None or isinstance(value, (int, float, bool)):
        return value
    if isinstance(value, str):
        return value if len(value) <= limit else value[:limit] + "…"
    try:
        s = json.dumps(value, ensure_ascii=False, default=str)
    except TypeError:
        s = str(value)
    if len(s) <= limit:
        # round-trip so the panel gets structured data, not a string, when possible
        try:
            return json.loads(s)
        except (json.JSONDecodeError, TypeError):
            return s
    return s[:limit] + "…"


@dataclass
class TraceStep:
    name: str
    model: str
    latency_ms: int = 0
    summary: str = ""
    input: Any = None
    output: Any = None
    status: str = "ok"            # ok | error
    error: Optional[str] = None

    def set_output(self, output: Any, summary: str = "") -> None:
        self.output = _short(output)
        if summary:
            self.summary = summary


@dataclass
class Trace:
    steps: List[TraceStep] = field(default_factory=list)

    @contextmanager
    def step(self, name: str, model: str, input: Any = None,
             summary: str = "") -> Iterator[TraceStep]:
        """Time a pipeline step, capture its output, and record errors without losing
        the partial trace. Usage:

            with trace.step("transcribe", model=AURA_STT, input=...) as st:
                result = do_work()
                st.set_output(result, summary="...")
        """
        st = TraceStep(name=name, model=model, input=_short(input), summary=summary)
        start = time.perf_counter()
        try:
            yield st
        except Exception as exc:  # noqa: BLE001, record then re-raise
            st.status = "error"
            st.error = str(exc)
            st.latency_ms = int((time.perf_counter() - start) * 1000)
            self.steps.append(st)
            raise
        st.latency_ms = int((time.perf_counter() - start) * 1000)
        self.steps.append(st)

    def to_dict(self) -> dict:
        return {
            "steps": [asdict(s) for s in self.steps],
            "total_latency_ms": sum(s.latency_ms for s in self.steps),
        }
