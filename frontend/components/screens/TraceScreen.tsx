"use client";
import { useApp } from "@/components/AppProvider";
import { AgentTrace } from "@/components/AgentTrace";
import { useLang } from "@/components/LanguageProvider";
import { XIcon } from "@/components/icons";

// Hidden "How it works" view (for judges): the live agent trace, moved out of the
// kid-facing flow. Reuses the existing AgentTrace renderer.
export function TraceScreen() {
  const { t } = useLang();
  const { assess, adapt, go } = useApp();

  const steps = [...(assess?.trace.steps ?? []), ...(adapt?.trace.steps ?? [])];
  const totalMs =
    (assess?.trace.total_latency_ms ?? 0) + (adapt?.trace.total_latency_ms ?? 0);

  return (
    <div className="mx-auto flex min-h-dvh w-full max-w-md flex-col px-5 pb-10 pt-6 md:max-w-2xl">
      <div className="flex items-center justify-between">
        <button
          type="button"
          onClick={() => go("path")}
          aria-label={t("back_to_path")}
          className="grid h-10 w-10 cursor-pointer place-items-center rounded-2xl border-2 border-sky-100 bg-white text-slate-400 transition-colors hover:text-brand"
        >
          <XIcon className="h-5 w-5" />
        </button>
        <span className="font-display text-xl font-extrabold text-ink">{t("judge_view")}</span>
        <span className="h-10 w-10" />
      </div>

      <p className="mt-3 mb-3 text-center text-sm text-slate-500">{t("judge_sub")}</p>

      <AgentTrace steps={steps} totalMs={totalMs} />
    </div>
  );
}
