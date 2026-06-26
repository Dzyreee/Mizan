"use client";
import { useApp } from "@/components/AppProvider";
import { Mascot } from "@/components/Mascot";
import { ProgressChart } from "@/components/ProgressChart";
import { useLang } from "@/components/LanguageProvider";
import { BookIcon, FlameIcon, StarIcon, XIcon } from "@/components/icons";

export function ProgressScreen() {
  const { t } = useLang();
  const { progress, game, go } = useApp();

  const sessions = progress?.sessions_count ?? 0;
  const display = progress ? { ...progress, name: t("child_name") } : null;

  const tiles = [
    { icon: <FlameIcon className="h-6 w-6 text-accent" fill="currentColor" />, value: game.streak, label: t("streak_label") },
    { icon: <BookIcon className="h-6 w-6 text-brand" />, value: sessions, label: t("sessions_label") },
    { icon: <StarIcon className="h-6 w-6 text-accent" fill="currentColor" />, value: game.stars, label: t("stars_label") },
  ];

  return (
    <div className="mx-auto flex min-h-dvh w-full max-w-md flex-col px-5 pb-10 pt-6 lg:max-w-4xl">
      <div className="flex items-center justify-between">
        <button
          type="button"
          onClick={() => go("path")}
          aria-label={t("back_to_path")}
          className="grid h-10 w-10 cursor-pointer place-items-center rounded-2xl border-2 border-sky-100 bg-white text-slate-400 transition-colors hover:text-brand"
        >
          <XIcon className="h-5 w-5" />
        </button>
        <span className="font-display text-xl font-extrabold text-ink">{t("my_progress")}</span>
        <span className="h-10 w-10" />
      </div>

      <div className="mt-4 lg:grid lg:grid-cols-2 lg:gap-6 lg:items-start">
        {/* left: profile + tiles */}
        <div className="space-y-3">
          <div className="flex items-center gap-3 rounded-[1.5rem] border-2 border-sky-100 bg-white p-4 shadow-soft">
            <Mascot size={64} mood="happy" />
            <div>
              <p className="font-display text-2xl font-extrabold text-ink">{t("child_name")}</p>
              <p className="text-base font-bold text-slate-500">{t("child_age")}</p>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3">
            {tiles.map((tile, i) => (
              <div key={i} className="card flex flex-col items-center gap-1 p-3">
                {tile.icon}
                <span className="font-display text-2xl font-extrabold text-ink">{tile.value}</span>
                <span className="text-center text-xs font-bold text-slate-500">{tile.label}</span>
              </div>
            ))}
          </div>
        </div>

        {/* right: per-sound improvement chart */}
        {display && (
          <div className="mt-3 lg:mt-0">
            <ProgressChart progress={display} />
          </div>
        )}
      </div>
    </div>
  );
}
