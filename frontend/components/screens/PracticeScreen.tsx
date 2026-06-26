"use client";
import { motion } from "framer-motion";

import { useApp } from "@/components/AppProvider";
import { Mascot } from "@/components/Mascot";
import { PressButton } from "@/components/ui/PressButton";
import { useLang } from "@/components/LanguageProvider";
import { MusicIcon, SpinnerIcon, XIcon } from "@/components/icons";

export function PracticeScreen() {
  const { t } = useLang();
  const { adapt, busyAdapt, note, poemImage, finishLesson, go } = useApp();

  const loading = busyAdapt || !adapt;
  const sounds = adapt?.plan.target_sounds ?? [];
  const poem = adapt?.generated.verse || adapt?.plan.practice_passage || "";

  return (
    <div className="mx-auto flex min-h-dvh w-full max-w-md flex-col px-5 pb-10 pt-6 md:max-w-3xl">
      {/* header */}
      <div className="flex items-center justify-between">
        <button
          type="button"
          onClick={() => go("path")}
          aria-label={t("back_to_path")}
          className="grid h-10 w-10 cursor-pointer place-items-center rounded-2xl border-2 border-sky-100 bg-white text-slate-400 transition-colors hover:text-brand"
        >
          <XIcon className="h-5 w-5" />
        </button>
        <span className="inline-flex items-center gap-1.5 font-display text-xl font-extrabold text-ink">
          <MusicIcon className="h-5 w-5 text-accent" />
          {t("poem_title")}
        </span>
        <span className="h-10 w-10" />
      </div>

      {loading ? (
        <div className="flex flex-1 flex-col items-center justify-center gap-4 text-center">
          <Mascot size={120} mood="happy" />
          <p className="inline-flex items-center gap-2 text-base font-bold text-slate-500">
            <SpinnerIcon className="h-5 w-5" />
            {note ?? t("composing_poem")}
          </p>
        </div>
      ) : (
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-5 flex-1 space-y-5"
        >
          {/* WHY — the differentiator: poem built from the child's weak sounds */}
          <div className="mx-auto max-w-xl text-center">
            {sounds.length > 0 ? (
              <>
                <p className="text-base font-bold text-slate-500">{t("poem_why")}</p>
                <div className="mt-2 flex flex-wrap justify-center gap-2">
                  {sounds.map((s) => (
                    <span
                      key={s}
                      dir="rtl"
                      className="grid h-11 min-w-11 place-items-center rounded-2xl border-b-4 border-accent-dark bg-accent px-2 font-display text-xl font-extrabold text-white"
                    >
                      {s}
                    </span>
                  ))}
                </div>
              </>
            ) : (
              <p className="text-base font-bold text-slate-500">{t("poem_why_generic")}</p>
            )}
          </div>

          {/* HERO — poem + Fanar-picked image in ONE card, side-by-side on desktop */}
          {poem && (
            <motion.div
              initial={{ scale: 0.96, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ type: "spring", stiffness: 220, damping: 20 }}
              className={`card overflow-hidden border-2 border-accent/40 ${poemImage ? "md:grid md:grid-cols-2" : ""}`}
            >
              {poemImage && (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={poemImage}
                  alt={adapt!.plan.title || t("poem_title")}
                  className="h-48 w-full object-cover md:h-full md:min-h-[18rem]"
                />
              )}
              <div className="flex flex-col items-center justify-center bg-gradient-to-b from-accent/10 to-white p-6 md:p-8">
                <p
                  dir="rtl"
                  className="whitespace-pre-line text-center font-display text-2xl font-extrabold leading-[2.9rem] text-ink md:text-3xl md:leading-[3.4rem]"
                >
                  {poem}
                </p>
                <p className="mt-4 text-[0.7rem] font-bold uppercase tracking-wide text-accent-dark/70">
                  {t("verse_label")}
                </p>
              </div>
            </motion.div>
          )}
        </motion.div>
      )}

      <div className="mx-auto mt-6 w-full max-w-md">
        <PressButton variant="accent" fullWidth disabled={loading} onClick={finishLesson}>
          {t("finish_lesson")}
        </PressButton>
      </div>
    </div>
  );
}
