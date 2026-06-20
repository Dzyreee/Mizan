"""The agent trace — every plan/tool/verify step with its inputs, outputs, and latency.

This is the data the right-hand "Agent Trace" panel renders, and how judges see the
agentic behavior. The orchestrator records steps via the `step()` context manager so
timing is automatic.
"""
from __future__ import annotations

import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Iterator, List, Optional


@dataclass
class Step:
    name: str
    kind: str                      # "plan" | "tool" | "ruling" | "verify" | "answer"
    input: Any
    output: Any = None
    model: Optional[str] = None    # Fanar model used, if any
    status: str = "ok"             # "ok" | "error" | "mismatch"
    latency_ms: int = 0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "kind": self.kind,
            "model": self.model,
            "status": self.status,
            "latency_ms": self.latency_ms,
            "input": self.input,
            "output": self.output,
        }


class Trace:
    def __init__(self) -> None:
        self.steps: List[Step] = []

    @contextmanager
    def step(self, name: str, kind: str, input: Any,
             model: Optional[str] = None) -> Iterator[Step]:
        s = Step(name=name, kind=kind, input=input, model=model)
        t0 = time.perf_counter()
        try:
            yield s
        except Exception as e:  # noqa: BLE001 — record the failure into the trace, then re-raise
            s.status = "error"
            s.output = {"error": repr(e)}
            raise
        finally:
            s.latency_ms = int((time.perf_counter() - t0) * 1000)
            self.steps.append(s)

    def total_latency_ms(self) -> int:
        return sum(s.latency_ms for s in self.steps)

    def to_dict(self) -> dict:
        return {
            "steps": [s.to_dict() for s in self.steps],
            "total_latency_ms": self.total_latency_ms(),
        }

    def render(self) -> str:
        icons = {"ok": "✅", "error": "❌", "mismatch": "⚠️"}
        lines = ["", "┌─ AGENT TRACE " + "─" * 50]
        for i, s in enumerate(self.steps, 1):
            tag = f"[{s.kind}]"
            model = f" · {s.model}" if s.model else ""
            lines.append(f"│ {i}. {icons.get(s.status,'•')} {s.name} {tag}{model}  ({s.latency_ms} ms)")
        lines.append(f"└─ total {self.total_latency_ms()} ms " + "─" * 44)
        return "\n".join(lines)
