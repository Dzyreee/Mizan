"use client";
import { motion } from "framer-motion";

import { useApp } from "@/components/AppProvider";
import { Mascot } from "@/components/Mascot";
import { useLang } from "@/components/LanguageProvider";
import {
  FlameIcon,
  GearIcon,
  LockIcon,
  StarIcon,
  TrendingUpIcon,
} from "@/components/icons";

// Gentle serpentine offset so the trail winds like a game map.
const offsetFor = (i: number) => Math.round(Math.sin(i * 0.9) * 58);

export function PathScreen() {
  const { t, lang, toggle } = useLang();
  const { lessons, nodeState, openNode, game, go } = useApp();

  const progressBtn = (
    <button
      type="button"
      onClick={() => go("progress")}
      className="flex w-full cursor-pointer items-center justify-center gap-2 rounded-2xl border-2 border-sky-100 bg-white py-3.5 text-lg font-extrabold text-brand transition-colors hover:bg-sky-50"
    >
      <TrendingUpIcon className="h-5 w-5" />
      {t("my_progress")}
    </button>
  );

  return (
    <div className="mx-auto w-full max-w-md px-5 pb-10 pt-6 md:max-w-2xl lg:max-w-5xl">
      {/* Top stats */}
      <div className="flex items-center justify-between">
        <span className="chip bg-accent/15 text-base text-accent-dark">
          <FlameIcon className="h-5 w-5 text-accent" fill="currentColor" />
          {game.streak}
          <span className="font-bold">{t("streak_label")}</span>
        </span>
        <div className="flex items-center gap-2">
          <span className="chip bg-amber-50 text-base text-accent-dark">
            <StarIcon className="h-5 w-5 text-accent" fill="currentColor" />
            {game.stars}
          </span>
          <button
            type="button"
            onClick={toggle}
            aria-label="Switch language"
            className="grid h-10 w-10 cursor-pointer place-items-center rounded-2xl border-2 border-sky-100 bg-white text-sm font-extrabold text-slate-500 transition-colors hover:text-brand"
          >
            {lang === "ar" ? "EN" : "ع"}
          </button>
          <button
            type="button"
            onClick={() => go("trace")}
            aria-label={t("judge_view")}
            className="grid h-10 w-10 cursor-pointer place-items-center rounded-2xl border-2 border-sky-100 bg-white text-slate-400 transition-colors hover:text-brand"
          >
            <GearIcon className="h-5 w-5" />
          </button>
        </div>
      </div>

      <div className="lg:mt-2 lg:grid lg:grid-cols-[320px_1fr] lg:gap-10">
        {/* Left rail (stacks above the trail on mobile) */}
        <aside className="mt-4 space-y-4 lg:sticky lg:top-6 lg:self-start">
          <div className="flex items-end gap-3">
            <Mascot size={88} mood="happy" />
            <div className="relative mb-3 flex-1 rounded-[1.25rem] border-2 border-sky-100 bg-white px-4 py-3 shadow-soft">
              <p className="font-display text-xl font-extrabold text-ink">{t("greet")}</p>
              <p className="text-base text-slate-500">{t("lets_read")}</p>
            </div>
          </div>
          <div className="hidden lg:block">{progressBtn}</div>
        </aside>

        {/* Winding lesson path */}
        <div className="relative mt-6 flex flex-col items-center gap-7 lg:mt-0 lg:pt-2">
          {lessons.map((l, i) => {
            const state = nodeState(l.id);
            const locked = state === "locked";
            const current = state === "current";
            const done = state === "completed";
            return (
              <div
                key={l.id}
                className="flex flex-col items-center gap-1.5"
                style={{ transform: `translateX(${offsetFor(i)}px)` }}
              >
                {current && (
                  <motion.span
                    initial={{ y: 4, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    className="rounded-full bg-brand px-3 py-1 text-xs font-extrabold text-white shadow-soft"
                  >
                    {t("start")}
                  </motion.span>
                )}
                <motion.button
                  type="button"
                  disabled={locked}
                  whileHover={locked ? undefined : { scale: 1.06 }}
                  whileTap={locked ? undefined : { scale: 0.9 }}
                  onClick={() => !locked && openNode(l.id)}
                  aria-label={`${l.title}${locked ? ` — ${t("locked_hint")}` : ""}`}
                  className={[
                    "grid h-20 w-20 place-items-center rounded-full border-b-[6px] transition-colors",
                    current ? "animate-pulse-glow" : "",
                    done
                      ? "border-brand-dark bg-brand text-white"
                      : current
                        ? "border-accent-dark bg-accent text-white"
                        : "cursor-not-allowed border-slate-300 bg-slate-200 text-slate-400",
                  ].join(" ")}
                >
                  {done ? (
                    <StarIcon className="h-9 w-9" fill="currentColor" />
                  ) : current ? (
                    <span className="font-display text-2xl font-extrabold">{l.id}</span>
                  ) : (
                    <LockIcon className="h-7 w-7" />
                  )}
                </motion.button>
                <span className={`text-sm font-bold ${locked ? "text-slate-400" : "text-ink"}`}>
                  {l.title}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Progress entry — mobile only (in the rail on desktop) */}
      <div className="mt-8 lg:hidden">{progressBtn}</div>
    </div>
  );
}
