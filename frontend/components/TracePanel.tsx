"use client";

import { useState } from "react";
import type { Trace, TraceStep } from "@/lib/types";

const STATUS_COLOR: Record<string, string> = {
  ok: "bg-verified",
  mismatch: "bg-mismatch",
  error: "bg-mismatch",
};

const KIND_LABEL: Record<string, string> = {
  plan: "PLAN",
  tool: "TOOL",
  ruling: "RULING",
  verify: "VERIFY",
  answer: "ANSWER",
};

function StepRow({ step, index, live }: { step: TraceStep; index: number; live: boolean }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="border-b border-grid">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center gap-3 py-3 px-1 text-left hover:bg-instrument-soft transition-colors"
      >
        <span className="font-mono text-bone-dim text-xs w-5 shrink-0">{index + 1}</span>
        <span
          className={`w-2 h-2 shrink-0 ${STATUS_COLOR[step.status] ?? "bg-bone-dim"} ${
            live ? "pulse-dot" : ""
          }`}
        />
        <span className="flex-1 min-w-0">
          <span className="block font-mono text-sm text-bone truncate">{step.name}</span>
          <span className="block font-mono text-[0.62rem] text-bone-dim tracking-wider mt-0.5">
            {KIND_LABEL[step.kind] ?? step.kind}
            {step.model ? ` · ${step.model}` : ""}
          </span>
        </span>
        <span className="font-mono text-xs text-brass-soft tnum shrink-0">{step.latency_ms} ms</span>
      </button>

      {open && (
        <div className="px-9 pb-3 space-y-2">
          <IO label="input" value={step.input} />
          <IO label="output" value={step.output} />
        </div>
      )}
    </div>
  );
}

function IO({ label, value }: { label: string; value: unknown }) {
  return (
    <div>
      <div className="font-mono text-[0.6rem] tracking-widest text-bone-dim uppercase mb-1">{label}</div>
      <pre className="font-mono text-xs text-bone/85 whitespace-pre-wrap break-words bg-instrument-soft border border-grid p-2 max-h-44 overflow-auto instrument-scroll">
        {typeof value === "string" ? value : JSON.stringify(value, null, 2)}
      </pre>
    </div>
  );
}

export function TracePanel({ trace, live = false }: { trace: Trace | null; live?: boolean }) {
  return (
    <div className="instrument-grid h-full flex flex-col text-bone">
      <div className="flex items-center justify-between px-4 py-3 border-b border-grid">
        <div className="flex items-center gap-2">
          <span className="font-mono text-xs tracking-[0.22em] text-bone">AGENT TRACE</span>
          {live && <span className="w-1.5 h-1.5 bg-verified pulse-dot" />}
        </div>
        <span className="font-mono text-xs text-brass-soft tnum">
          {trace ? `${trace.total_latency_ms} ms total` : "—"}
        </span>
      </div>

      <div className="flex-1 overflow-auto instrument-scroll px-3">
        {!trace || trace.steps.length === 0 ? (
          <div className="h-full flex items-center justify-center">
            <p className="font-mono text-xs text-bone-dim text-center max-w-[14rem] leading-relaxed">
              the plan, every tool call, and the verifier verdict appear here as the agent runs.
            </p>
          </div>
        ) : (
          <>
            {trace.steps.map((s, i) => (
              <StepRow key={i} step={s} index={i} live={live && i === trace.steps.length - 1} />
            ))}
            <VerdictBanner trace={trace} />
          </>
        )}
      </div>
    </div>
  );
}

function VerdictBanner({ trace }: { trace: Trace }) {
  const verify = trace.steps.find((s) => s.kind === "verify");
  if (!verify) return null;
  const agree = verify.status === "ok";
  return (
    <div
      className={`mt-4 mb-3 mx-1 px-3 py-2 border ${
        agree ? "border-verified text-verified" : "border-mismatch text-mismatch"
      }`}
    >
      <div className="font-mono text-[0.6rem] tracking-widest uppercase mb-0.5">verifier verdict</div>
      <div className="font-mono text-sm">
        {agree ? "MATCH — generator and verifier agree" : "MISMATCH — withheld for human review"}
      </div>
    </div>
  );
}
