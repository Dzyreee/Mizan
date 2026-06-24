"use client";
import type { TraceStep } from "@/lib/types";
import { BoltIcon } from "./icons";

const STEP_META: Record<string, { label: string; tone: string }> = {
  transcribe: { label: "النسخ الصوتي", tone: "bg-sky-100 text-sky-700" },
  align: { label: "المحاذاة (محرّك حتمي)", tone: "bg-slate-100 text-slate-700" },
  diagnose: { label: "تشخيص النمط", tone: "bg-violet-100 text-violet-700" },
  plan: { label: "تخطيط التمرين", tone: "bg-indigo-100 text-indigo-700" },
  "generate-verse": { label: "توليد القصيدة", tone: "bg-amber-100 text-amber-700" },
  "generate-image": { label: "توليد الرسم", tone: "bg-pink-100 text-pink-700" },
  "generate-audio": { label: "نطق الكلمات", tone: "bg-emerald-100 text-emerald-700" },
};

export function AgentTrace({
  steps,
  totalMs,
  activeName,
}: {
  steps: TraceStep[];
  totalMs: number;
  activeName?: string | null;
}) {
  return (
    <section className="card p-5">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-bold text-ink">مسار الوكيل الذكي</h2>
        {totalMs > 0 && (
          <span className="chip bg-slate-100 text-slate-600">
            <BoltIcon className="h-3.5 w-3.5" /> <span className="mono">{totalMs} ms</span>
          </span>
        )}
      </div>

      <ol className="relative space-y-3 ps-5">
        <span className="absolute inset-y-1 start-[7px] w-px bg-indigo-100" aria-hidden />
        {steps.map((s, i) => {
          const meta = STEP_META[s.name] ?? { label: s.name, tone: "bg-slate-100 text-slate-700" };
          const active = activeName === s.name;
          const isError = s.status === "error";
          return (
            <li key={`${s.name}-${i}`} className="relative animate-fade-in-up">
              <span
                className={`absolute -start-[1.07rem] top-1.5 h-3.5 w-3.5 rounded-full border-2 border-white ${
                  isError ? "bg-rose-500" : active ? "bg-accent animate-pulse-glow" : "bg-brand"
                }`}
                aria-hidden
              />
              <div className="rounded-xl border border-indigo-100/70 bg-white/70 p-3">
                <div className="flex items-center justify-between gap-2">
                  <span className="font-semibold text-ink">{meta.label}</span>
                  <span className="mono text-[0.65rem] text-slate-400">{s.latency_ms} ms</span>
                </div>
                <div className="mt-1.5 flex items-center gap-2">
                  <span className={`chip ${meta.tone} mono text-[0.65rem]`}>{s.model}</span>
                </div>
                <p
                  dir="auto"
                  className={`mt-1.5 text-xs leading-relaxed ${isError ? "text-rose-600" : "text-slate-500"}`}
                >
                  {isError ? s.error : s.summary}
                </p>
              </div>
            </li>
          );
        })}
        {steps.length === 0 && (
          <li className="text-sm text-slate-400">سيظهر تسلسل الخطوات هنا أثناء التحليل…</li>
        )}
      </ol>
    </section>
  );
}
