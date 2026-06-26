"use client";
import { useState } from "react";
import { motion } from "framer-motion";

import { useApp } from "@/components/AppProvider";
import { MicButton } from "@/components/MicButton";
import { PressButton } from "@/components/ui/PressButton";
import { useLang } from "@/components/LanguageProvider";
import { BookIcon, PlayIcon, XIcon } from "@/components/icons";
import type { AlignedWord } from "@/lib/types";

// Illustration chosen by Fanar from the static library. Fills its grid cell (generous on
// desktop). Friendly placeholder while the pick is in flight or the file is missing.
function LessonImage({ src, alt }: { src: string | null; alt: string }) {
  const [broken, setBroken] = useState(false);
  if (!src || broken) {
    return (
      <div className="grid h-44 w-full place-items-center bg-gradient-to-b from-sky-100/70 to-white md:h-full md:min-h-[18rem]">
        <BookIcon className="h-12 w-12 text-brand/40" />
      </div>
    );
  }
  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={src}
      alt={alt}
      onError={() => setBroken(true)}
      className="h-44 w-full object-cover md:h-full md:min-h-[18rem]"
    />
  );
}

function Word({ w }: { w: AlignedWord }) {
  const struggled = w.status === "substitution" || w.status === "omission";
  return (
    <span
      className={
        struggled
          ? "rounded-lg bg-accent/15 px-1.5 text-accent-dark underline decoration-accent decoration-wavy decoration-2 underline-offset-4"
          : "text-ink"
      }
    >
      {w.target}
    </span>
  );
}

export function SessionScreen() {
  const { t } = useLang();
  const { activeLesson, assess, busyAssess, note, sessionImage, runAudio, runDemo, toResults, go } =
    useApp();
  if (!activeLesson) return null;

  const words = assess?.error_map.words ?? null;

  return (
    <div className="mx-auto w-full max-w-md px-5 pb-10 pt-6 md:max-w-3xl">
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
        <span className="font-display text-xl font-extrabold text-ink">{activeLesson.title}</span>
        <span className="h-10 w-10" />
      </div>

      <p className="mt-5 text-center text-base font-bold text-slate-500">{t("read_aloud")}</p>

      {/* reading card — image beside the passage (stacks on mobile) */}
      <motion.div layout className="card mt-3 overflow-hidden md:grid md:grid-cols-2">
        <LessonImage key={activeLesson.id} src={sessionImage} alt={activeLesson.title} />
        <div className="flex items-center justify-center p-6 md:p-8">
          <p dir="rtl" className="text-center font-display text-3xl leading-[2.7rem] text-ink md:text-4xl md:leading-[3.4rem]">
            {words
              ? words.map((w, i) => (
                  <span key={w.index}>
                    <Word w={w} />
                    {i < words.length - 1 ? " " : ""}
                  </span>
                ))
              : activeLesson.passage}
          </p>
        </div>
      </motion.div>

      {note && (
        <p className="mt-4 rounded-2xl border-2 border-amber-200 bg-amber-50 px-4 py-2 text-center text-sm font-bold text-amber-700">
          {note}
        </p>
      )}

      {/* controls */}
      <div className="mx-auto mt-6 max-w-md">
        {assess ? (
          <PressButton variant="accent" fullWidth onClick={toResults}>
            {t("continue")}
          </PressButton>
        ) : (
          <div className="flex flex-col items-center gap-4">
            <MicButton busy={busyAssess} onRecorded={runAudio} />
            <button
              type="button"
              onClick={runDemo}
              disabled={busyAssess}
              className="inline-flex cursor-pointer items-center gap-1.5 text-base font-bold text-brand underline-offset-4 hover:underline disabled:opacity-50"
            >
              <PlayIcon className="h-4 w-4" />
              {t("demo_button")}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
