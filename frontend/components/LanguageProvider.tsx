"use client";
import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { dirOf, type Lang, type StringKey, translate } from "@/lib/i18n";

interface LangCtx {
  lang: Lang;
  dir: "rtl" | "ltr";
  setLang: (l: Lang) => void;
  toggle: () => void;
  t: (key: StringKey) => string;
}

const Ctx = createContext<LangCtx | null>(null);

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [lang, setLangState] = useState<Lang>("ar");

  // Restore saved choice on mount.
  useEffect(() => {
    const saved = localStorage.getItem("naghami-lang") as Lang | null;
    if (saved === "ar" || saved === "en") setLangState(saved);
  }, []);

  // Reflect language on <html> and persist.
  useEffect(() => {
    document.documentElement.lang = lang;
    document.documentElement.dir = dirOf(lang);
    localStorage.setItem("naghami-lang", lang);
  }, [lang]);

  const setLang = (l: Lang) => setLangState(l);
  const toggle = () => setLangState((p) => (p === "ar" ? "en" : "ar"));
  const t = (key: StringKey) => translate(lang, key);

  return (
    <Ctx.Provider value={{ lang, dir: dirOf(lang), setLang, toggle, t }}>
      {children}
    </Ctx.Provider>
  );
}

export function useLang(): LangCtx {
  const v = useContext(Ctx);
  if (!v) throw new Error("useLang must be used within LanguageProvider");
  return v;
}
