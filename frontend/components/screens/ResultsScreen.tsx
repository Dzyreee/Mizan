"use client";
import { useEffect } from "react";
import { motion } from "framer-motion";

import { useApp } from "@/components/AppProvider";
import { Mascot } from "@/components/Mascot";
import { PressButton } from "@/components/ui/PressButton";
import { useLang } from "@/components/LanguageProvider";
import { GaugeIcon, BoltIcon } from "@/components/icons";

const GOOD = 70; // accuracy % threshold for a celebration

async function celebrate() {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  // Browser-only — loaded on demand so it never runs during SSR.
  const confetti = (await import("canvas-confetti")).default;
  const sky = ["#1CB0F6", "#6FCBF9"];
  const origin = { y: 0.6 };
  confetti({ origin, particleCount: 36, spread: 60, colors: ["#FF9600", ...sky] });
  confetti({ origin, particleCount: 30, spread: 90, decay: 0.92, scalar: 1.1, colors: ["#FF9600", "#FFB23E"] });
  confetti({ origin, particleCount: 24, spread: 120, startVelocity: 35, colors: sky });
}

export function ResultsScreen() {
  const { t } = useLang();
  const { assess, toPractice } = useApp();
  const em = assess?.error_map;
  const good = (em?.accuracy_pct ?? 0) >= GOOD;
  const sounds = assess?.diagnosis?.weak_sounds ?? [];

  useEffect(() => {
    if (good) void celebrate();
  }, [good]);

  if (!assess || !em) return null;

  return (
    <div className="mx-auto flex min-h-dvh w-full max-w-md flex-col items-center px-5 pb-8 pt-10 text-center md:max-w-lg">
      <Mascot size={132} mood={good ? "cheer" : "happy"} />

      <motion.h1
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ type: "spring", stiffness: 260, damping: 18 }}
        className="mt-4 font-display text-3xl font-extrabold text-ink"
      >
        {good ? t("great_job") : t("keep_practicing")}
      </motion.h1>

      {/* stat tiles */}
      <div className="mt-6 grid w-full grid-cols-2 gap-3">
        <div className="card flex flex-col items-center gap-1 p-4">
          <GaugeIcon className="h-6 w-6 text-brand" />
          <span className="font-display text-3xl font-extrabold text-ink">
            {Math.round(em.accuracy_pct)}%
          </span>
          <span className="text-xs font-bold text-slate-500">{t("stat_accuracy")}</span>
        </div>
        <div className="card flex flex-col items-center gap-1 p-4">
          <BoltIcon className="h-6 w-6 text-accent" />
          <span className="font-display text-3xl font-extrabold text-ink">
            {em.wpm != null ? Math.round(em.wpm) : "—"}
          </span>
          <span className="text-xs font-bold text-slate-500">{t("stat_speed_sub")}</span>
        </div>
      </div>

      {/* tricky sounds */}
      <div className="card mt-3 w-full p-4">
        <p className="text-sm font-bold text-slate-500">
          {sounds.length ? t("tricky_sounds") : t("no_tricky")}
        </p>
        {sounds.length > 0 && (
          <div className="mt-3 flex flex-wrap justify-center gap-2">
            {sounds.map((s) => (
              <span
                key={s}
                dir="rtl"
                className="grid h-12 min-w-12 place-items-center rounded-2xl border-b-4 border-accent-dark bg-accent px-2 font-display text-xl font-extrabold text-white"
              >
                {s}
              </span>
            ))}
          </div>
        )}
        {assess.diagnosis?.encouragement && (
          <p dir="rtl" className="mt-3 text-sm leading-relaxed text-slate-600">
            {assess.diagnosis.encouragement}
          </p>
        )}
      </div>

      <div className="mt-auto w-full pt-6">
        <PressButton variant="primary" fullWidth onClick={toPractice}>
          {t("continue")}
        </PressButton>
      </div>
    </div>
  );
}
