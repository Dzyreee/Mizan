"use client";
import { useEffect, useMemo, useState } from "react";

import { AgentTrace } from "@/components/AgentTrace";
import { ExerciseCard } from "@/components/ExerciseCard";
import { Header } from "@/components/Header";
import { MicButton } from "@/components/MicButton";
import { PatternBanner } from "@/components/PatternBanner";
import { ProgressChart } from "@/components/ProgressChart";
import { StatCards } from "@/components/StatCards";
import { TargetPassage } from "@/components/TargetPassage";
import { PlayIcon, SparklesIcon } from "@/components/icons";
import * as api from "@/lib/api";
import { SAMPLE_TARGET, sampleAdapt, sampleAssess, sampleProgress } from "@/lib/sample";
import type { AdaptResult, AssessResult, Progress } from "@/lib/types";

// What the demo "child" reads (3 deliberate miscues that survive Aura normalization).
const DEMO_MISREAD = "ذهب الورد إلى المدرسة في المساء";

export default function Page() {
  const [online, setOnline] = useState<boolean | null>(null);
  const [target] = useState(SAMPLE_TARGET);
  const [assess, setAssess] = useState<AssessResult | null>(sampleAssess);
  const [adapt, setAdapt] = useState<AdaptResult | null>(sampleAdapt);
  const [progress, setProgress] = useState<Progress | null>(sampleProgress);
  const [busyAssess, setBusyAssess] = useState(false);
  const [busyAdapt, setBusyAdapt] = useState(false);
  const [note, setNote] = useState<string | null>(null);

  useEffect(() => {
    api.health().then((ok) => {
      setOnline(ok);
      if (ok) api.getProgress().then(setProgress).catch(() => {});
    });
  }, []);

  const traceSteps = useMemo(
    () => [...(assess?.trace.steps ?? []), ...(adapt?.trace.steps ?? [])],
    [assess, adapt],
  );
  const totalMs =
    (assess?.trace.total_latency_ms ?? 0) + (adapt?.trace.total_latency_ms ?? 0);

  async function runPipeline(getAssessment: () => Promise<AssessResult>) {
    setNote(null);
    setBusyAssess(true);
    setAdapt(null);
    try {
      const a = await getAssessment();
      setAssess(a);
      setBusyAssess(false);
      if (a.diagnosis) {
        setBusyAdapt(true);
        const ad = await api.adapt(a.diagnosis);
        setAdapt(ad);
      }
    } catch (e) {
      setNote(`تعذّر الاتصال بالخادم — يُعرض مثال توضيحي. (${(e as Error).message})`);
      setAssess(sampleAssess);
      setAdapt(sampleAdapt);
    } finally {
      setBusyAssess(false);
      setBusyAdapt(false);
    }
  }

  const runDemo = () => runPipeline(() => api.assessTranscript(target, DEMO_MISREAD));
  const onRecorded = (blob: Blob) => runPipeline(() => api.assessAudio(target, blob));
  const reset = () => {
    setAssess(null);
    setAdapt(null);
    setNote(null);
  };

  const busy = busyAssess || busyAdapt;

  return (
    <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6">
      <Header online={online} />

      {note && (
        <p className="mt-4 rounded-xl border border-amber-200 bg-amber-50 px-4 py-2 text-sm text-amber-700">
          {note}
        </p>
      )}

      <div className="mt-6 grid gap-6 lg:grid-cols-[1.45fr_1fr]">
        {/* ── Reading session ── */}
        <div className="space-y-5">
          <section className="card p-5">
            <div className="mb-3 flex items-center justify-between">
              <h2 className="text-lg font-bold text-ink">جلسة القراءة</h2>
              {assess && (
                <button
                  onClick={reset}
                  className="cursor-pointer text-xs font-medium text-slate-400 transition-colors hover:text-brand"
                >
                  إعادة تعيين
                </button>
              )}
            </div>

            <TargetPassage target={target} words={assess?.error_map.words ?? null} />

            <div className="mt-5 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
              <MicButton busy={busy} onRecorded={onRecorded} />
              <span className="text-sm text-slate-400">أو</span>
              <button
                onClick={runDemo}
                disabled={busy}
                className="inline-flex cursor-pointer items-center gap-2 rounded-full bg-brand px-5 py-3 font-semibold text-white shadow-soft transition-colors duration-200 hover:bg-brand-dark disabled:cursor-not-allowed disabled:opacity-60"
              >
                <PlayIcon className="h-4 w-4" />
                عرض توضيحي
              </button>
            </div>

            {assess && (
              <div className="mt-5">
                <StatCards em={assess.error_map} />
              </div>
            )}
          </section>

          {assess?.diagnosis && (
            <PatternBanner diagnosis={assess.diagnosis} generating={busyAdapt} />
          )}

          {adapt && <ExerciseCard adapt={adapt} />}

          {!assess && (
            <p className="flex items-center gap-2 rounded-2xl border border-dashed border-indigo-200 bg-white/60 p-4 text-sm text-slate-500">
              <SparklesIcon className="h-4 w-4 text-brand" />
              اضغط على الميكروفون ليقرأ الطفل النص، أو جرّب «عرض توضيحي» لرؤية الدورة كاملة.
            </p>
          )}
        </div>

        {/* ── Agent trace + progress ── */}
        <div className="space-y-5">
          <AgentTrace steps={traceSteps} totalMs={totalMs} activeName={busyAdapt ? "plan" : null} />
          {progress && <ProgressChart progress={progress} />}
        </div>
      </div>

      <footer className="mt-8 text-center text-xs text-slate-400">
        نَغَمي أداة لدعم القراءة فقط. الأنماط المعروضة للممارسة، وليست تشخيصاً طبياً —
        راجِع أخصائياً إذا استمرت.
      </footer>
    </main>
  );
}
