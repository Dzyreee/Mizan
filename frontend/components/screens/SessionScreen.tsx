"use client";
import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";

import { useApp } from "@/components/AppProvider";
import { MicButton } from "@/components/MicButton";
import { PressButton } from "@/components/ui/PressButton";
import { LevelBadge } from "@/components/ui/LevelBadge";
import { useLang } from "@/components/LanguageProvider";
import { useSpeak } from "@/components/useSpeak";
import { BookIcon, PlayIcon, VolumeIcon, XIcon } from "@/components/icons";

// A tap on a word plays ONLY that word (Aura TTS) as a hint — never the whole sentence,
// so the child still reads it themselves. Capped per lesson to keep it a hint.
const HINT_LIMIT = 2;

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

export function SessionScreen() {
  const { t } = useLang();
  const {
    activeLesson,
    lessons,
    game,
    assess,
    busyAssess,
    note,
    sessionImage,
    runAudio,
    runDemo,
    toResults,
    go,
  } = useApp();
  const { speak, pending } = useSpeak();

  const [hintsUsed, setHintsUsed] = useState(0);
  // Hints reset every time a new node opens.
  useEffect(() => setHintsUsed(0), [activeLesson?.id]);

  const aligned = assess?.error_map.words ?? null;

  // One tappable word list, whether we're pre-reading (raw passage) or post-assess
  // (aligned words, struggled ones flagged).
  const words = useMemo(() => {
    if (aligned) {
      return aligned.map((w) => ({
        key: String(w.index),
        text: w.target,
        struggled: w.status === "substitution" || w.status === "omission",
      }));
    }
    if (!activeLesson) return [];
    return activeLesson.passage
      .split(/\s+/)
      .filter(Boolean)
      .map((text, i) => ({ key: `p${i}`, text, struggled: false }));
  }, [aligned, activeLesson]);

  if (!activeLesson) return null;

  const hintsLeft = HINT_LIMIT - hintsUsed;
  const canHint = hintsLeft > 0;
  const level = Math.min(game.completed.length + 1, lessons.length);

  const onWord = (text: string, key: string) => {
    if (!canHint) return;
    setHintsUsed((n) => n + 1);
    void speak(text, key);
  };

  return (
    <div className="mx-auto w-full max-w-md px-5 pb-10 pt-6 md:max-w-3xl lg:max-w-5xl xl:max-w-6xl">
      {/* header */}
      <div className="flex items-center justify-between gap-2">
        <button
          type="button"
          onClick={() => go("path")}
          aria-label={t("back_to_path")}
          className="grid h-10 w-10 shrink-0 cursor-pointer place-items-center rounded-2xl border-2 border-sky-100 bg-white text-slate-400 transition-colors hover:text-brand"
        >
          <XIcon className="h-5 w-5" />
        </button>
        <span className="truncate font-display text-xl font-extrabold text-ink">
          {activeLesson.title}
        </span>
        <LevelBadge level={level} completed={game.completed.length} total={lessons.length} />
      </div>

      <p className="mt-5 text-center text-base font-bold text-slate-500">{t("read_aloud")}</p>

      {/* reading card — image beside the passage (stacks on mobile) */}
      <motion.div layout className="card mt-3 overflow-hidden md:grid md:grid-cols-2">
        <LessonImage key={activeLesson.id} src={sessionImage} alt={activeLesson.title} />
        <div className="flex flex-col items-center justify-center p-6 md:p-8">
          <div
            dir="rtl"
            className="flex flex-wrap items-center justify-center gap-x-1 gap-y-2 text-center font-display text-3xl leading-[2.7rem] md:text-4xl md:leading-[3.4rem]"
          >
            {words.map((w) => {
              const loading = pending === w.key;
              return (
                <motion.button
                  key={w.key}
                  type="button"
                  onClick={() => onWord(w.text, w.key)}
                  disabled={!canHint}
                  whileTap={canHint ? { scale: 0.88 } : undefined}
                  aria-label={canHint ? `${t("tap_hint_help")}: ${w.text}` : w.text}
                  className={[
                    "rounded-xl px-1.5 transition-colors",
                    w.struggled
                      ? "bg-accent/15 text-accent-dark underline decoration-accent decoration-wavy decoration-2 underline-offset-4"
                      : canHint
                        ? "text-ink"
                        : "text-slate-400",
                    canHint ? "cursor-pointer hover:bg-brand/10" : "cursor-default",
                    loading ? "bg-brand/15" : "",
                  ].join(" ")}
                >
                  {w.text}
                </motion.button>
              );
            })}
          </div>

          {/* hint meter — encourages a tap, then a friendly stop */}
          <p className="mt-4 inline-flex items-center gap-1.5 text-sm font-bold text-slate-500">
            {canHint ? (
              <>
                <VolumeIcon className="h-4 w-4 text-brand" />
                {t("tap_hint_help")} · {hintsLeft} {t("hints_left")}
              </>
            ) : (
              t("hints_used")
            )}
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
