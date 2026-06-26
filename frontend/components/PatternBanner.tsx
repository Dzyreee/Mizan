"use client";
import type { Diagnosis } from "@/lib/types";
import { useLang } from "./LanguageProvider";
import { CheckIcon, SparklesIcon, SpinnerIcon, ShieldIcon } from "./icons";

export function PatternBanner({
  diagnosis,
  generating,
}: {
  diagnosis: Diagnosis;
  generating: boolean;
}) {
  const { t } = useLang();
  const pattern = diagnosis.patterns?.[0]?.label ?? diagnosis.focus;
  return (
    <section className="overflow-hidden rounded-3xl border border-accent/30 bg-gradient-to-l from-accent/10 via-brand/10 to-brand/5 p-5 shadow-soft animate-fade-in-up">
      <div className="flex items-start gap-3">
        <span className="grid h-10 w-10 shrink-0 place-items-center rounded-2xl bg-brand text-white">
          <CheckIcon className="h-5 w-5" />
        </span>
        <div className="min-w-0 flex-1">
          <div className="text-xs font-semibold uppercase tracking-wide text-brand">{t("pattern_detected")}</div>
          <p className="mt-0.5 text-lg font-bold text-ink">{pattern}</p>

          <div className="mt-2 flex flex-wrap items-center gap-1.5">
            <span className="text-xs text-slate-500">{t("sounds_focus")}</span>
            {diagnosis.weak_sounds.map((s) => (
              <span key={s} className="chip bg-white font-bold text-accent">{s}</span>
            ))}
          </div>

          {diagnosis.encouragement && (
            <p className="mt-2 text-sm text-slate-600">{diagnosis.encouragement}</p>
          )}

          {generating ? (
            <div className="mt-3 inline-flex items-center gap-2 rounded-full bg-white/80 px-3 py-1.5 text-sm font-semibold text-brand animate-pulse-glow">
              <SpinnerIcon className="h-4 w-4" />
              {t("generating")}
            </div>
          ) : (
            <div className="mt-3 inline-flex items-center gap-2 text-sm font-semibold text-emerald-600">
              <SparklesIcon className="h-4 w-4" />
              {t("exercise_ready")}
            </div>
          )}
        </div>
      </div>

      {diagnosis.specialist_note && (
        <p className="mt-3 flex items-start gap-2 rounded-xl bg-white/70 p-2.5 text-xs text-slate-500">
          <ShieldIcon className="mt-0.5 h-4 w-4 shrink-0 text-slate-400" />
          {diagnosis.specialist_note}
        </p>
      )}
    </section>
  );
}
