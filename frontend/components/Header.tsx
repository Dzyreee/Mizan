"use client";
import { useLang } from "./LanguageProvider";
import { BookIcon, ShieldIcon } from "./icons";
import type { Lang } from "@/lib/i18n";

export function Header({ online }: { online: boolean | null }) {
  const { t, lang, setLang } = useLang();
  return (
    <header className="flex flex-wrap items-center justify-between gap-4">
      <div className="flex items-center gap-3">
        <div className="grid h-12 w-12 place-items-center rounded-2xl bg-brand text-white shadow-soft">
          <BookIcon className="h-6 w-6" />
        </div>
        <div>
          <h1 className="text-2xl font-extrabold leading-none text-ink">
            اقرأ <span className="text-base font-semibold text-brand mono">Iqra</span>
          </h1>
          <p className="mt-1 text-sm text-slate-600">{t("tagline")}</p>
        </div>
      </div>

      <div className="flex items-center gap-2">
        {/* Language toggle */}
        <div className="flex overflow-hidden rounded-full border border-indigo-200 bg-white text-xs font-semibold">
          {(["ar", "en"] as Lang[]).map((l) => (
            <button
              key={l}
              onClick={() => setLang(l)}
              className={`cursor-pointer px-3 py-1.5 transition-colors duration-200 ${
                lang === l ? "bg-brand text-white" : "text-slate-500 hover:text-brand"
              }`}
              aria-pressed={lang === l}
            >
              {l === "ar" ? "العربية" : "EN"}
            </button>
          ))}
        </div>

        <span className="chip border border-emerald-200 bg-emerald-50 text-emerald-700">
          <ShieldIcon className="h-4 w-4" />
          {t("support_badge")}
        </span>
        <span className="chip border border-slate-200 bg-white text-slate-600">
          <span
            className={`h-2 w-2 rounded-full ${
              online === null ? "bg-slate-300" : online ? "bg-emerald-500" : "bg-amber-400"
            }`}
          />
          {online === null ? "…" : online ? t("status_online") : t("status_demo")}
        </span>
      </div>
    </header>
  );
}
