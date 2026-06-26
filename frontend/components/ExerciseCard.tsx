"use client";
import type { AdaptResult } from "@/lib/types";
import { useLang } from "./LanguageProvider";
import { PlayIcon, SparklesIcon } from "./icons";

function playB64(b64: string, mime: string) {
  if (!b64) return;
  new Audio(`data:${mime};base64,${b64}`).play().catch(() => {});
}

export function ExerciseCard({ adapt }: { adapt: AdaptResult }) {
  const { t } = useLang();
  const { plan, generated } = adapt;
  const illoSrc = generated.illustration
    ? `data:${generated.illustration.mime};base64,${generated.illustration.b64}`
    : null;

  return (
    <section className="card overflow-hidden animate-fade-in-up">
      <div className="flex items-center gap-2 bg-gradient-to-l from-accent/15 to-brand/15 px-5 py-3">
        <SparklesIcon className="h-5 w-5 text-accent" />
        <h3 className="font-bold text-ink">{plan.title || t("exercise_title_fallback")}</h3>
        <div className="ms-auto flex gap-1">
          {plan.target_sounds?.map((s) => (
            <span key={s} className="chip bg-white/70 font-bold text-brand">
              {s}
            </span>
          ))}
        </div>
      </div>

      <div className="grid gap-4 p-5 sm:grid-cols-[160px_1fr]">
        {/* Illustration (Oryx-IG) */}
        <div className="grid h-40 place-items-center overflow-hidden rounded-2xl border border-indigo-100 bg-indigo-50/60">
          {illoSrc ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={illoSrc} alt={t("exercise_title_fallback")} className="h-full w-full object-cover" />
          ) : (
            <div className="px-3 text-center text-xs text-slate-400">
              <SparklesIcon className="mx-auto mb-1 h-6 w-6 text-brand/40" />
              {t("illustration_placeholder")}
            </div>
          )}
        </div>

        <div className="space-y-3">
          {/* Practice passage */}
          {plan.practice_passage && (
            <div>
              <div className="mb-1 text-xs font-medium text-slate-400">{t("practice_text")}</div>
              <p dir="rtl" className="text-lg leading-loose text-ink">
                {plan.practice_passage}
              </p>
            </div>
          )}

          {/* Pronunciation chips (Aura TTS) */}
          {generated.pronunciations.length > 0 && (
            <div>
              <div className="mb-1.5 text-xs font-medium text-slate-400">
                {t("listen_repeat")}
              </div>
              <div className="flex flex-wrap gap-2">
                {generated.pronunciations.map((p) => (
                  <button
                    key={p.word}
                    type="button"
                    onClick={() => playB64(p.b64, p.mime)}
                    disabled={!p.b64}
                    className="chip cursor-pointer border border-brand/30 bg-white text-brand transition-colors duration-200 hover:bg-brand hover:text-white disabled:cursor-default disabled:opacity-60 disabled:hover:bg-white disabled:hover:text-brand"
                  >
                    <PlayIcon className="h-3.5 w-3.5" />
                    {p.word}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Diwan verse */}
      {generated.verse && (
        <div className="mx-5 mb-5 rounded-2xl border border-amber-100 bg-amber-50/50 p-4">
          <div className="mb-1 text-xs font-medium text-amber-700/80">{t("verse_label")}</div>
          <p dir="rtl" className="whitespace-pre-line text-center font-display text-lg leading-loose text-ink">
            {generated.verse}
          </p>
        </div>
      )}
    </section>
  );
}
