"use client";

import { useState } from "react";

const EXAMPLES = [
  "توفي رجل وترك زوجة وابنين وبنتاً، والتركة 120000 ريال",
  "توفيت امرأة وتركت زوجاً وبنتين وأماً، والتركة 26000 ريال",
  "توفي رجل وترك زوجة وبنتاً وأماً، والتركة 48000 ريال",
];

export function Composer({
  onSubmit,
  loading,
  verify,
  setVerify,
}: {
  onSubmit: (q: string) => void;
  loading: boolean;
  verify: boolean;
  setVerify: (v: boolean) => void;
}) {
  const [q, setQ] = useState("");

  function submit() {
    if (q.trim() && !loading) onSubmit(q.trim());
  }

  return (
    <div className="border border-line bg-paper-deep/40">
      <div className="flex items-stretch">
        {/* Mic — voice arrives in Phase 4 */}
        <button
          type="button"
          title="الإدخال الصوتي — قريباً (Aura)"
          className="shrink-0 w-14 border-l border-line text-ink-soft hover:text-brass
            flex items-center justify-center transition-colors"
        >
          <svg viewBox="0 0 24 24" className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="1.6">
            <rect x="9" y="3" width="6" height="11" rx="3" />
            <path d="M5 11a7 7 0 0 0 14 0M12 18v3" strokeLinecap="round" />
          </svg>
        </button>

        <textarea
          dir="rtl"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) submit();
          }}
          rows={2}
          placeholder="اكتب سؤال الميراث بالعربية… مثال: توفي رجل وترك زوجة وابنين وبنتاً"
          className="flex-1 bg-transparent resize-none px-4 py-3 font-arabic text-xl
            text-ink placeholder:text-ink-soft/60 outline-none"
        />
      </div>

      <div className="flex items-center justify-between border-t border-line px-3 py-2 gap-3">
        {/* Verify / ablation toggle */}
        <button
          type="button"
          onClick={() => setVerify(!verify)}
          className="group flex items-center gap-2"
          title="بدّل بين المسار الموثّق ومسار النموذج وحده"
        >
          <span
            className={`relative w-9 h-5 rounded-full border transition-colors ${
              verify ? "bg-verified/15 border-verified" : "bg-mismatch/10 border-mismatch"
            }`}
          >
            <span
              className={`absolute top-0.5 w-3.5 h-3.5 rounded-full transition-all ${
                verify ? "left-[18px] bg-verified" : "left-0.5 bg-mismatch"
              }`}
            />
          </span>
          <span className="label text-ink-soft group-hover:text-ink">
            {verify ? "verified pipeline" : "llm-only (ablation)"}
          </span>
        </button>

        <button
          type="button"
          onClick={submit}
          disabled={loading || !q.trim()}
          className="px-5 py-1.5 bg-ink text-paper font-arabic text-lg
            disabled:opacity-40 disabled:cursor-not-allowed hover:bg-maroon transition-colors"
        >
          {loading ? "…يحسب" : "احسب"}
        </button>
      </div>

      <div className="flex flex-wrap gap-1.5 px-3 pb-3" dir="rtl">
        {EXAMPLES.map((ex) => (
          <button
            key={ex}
            type="button"
            onClick={() => setQ(ex)}
            className="font-arabic text-sm text-ink-soft hover:text-brass border border-line
              hover:border-brass px-2.5 py-1 transition-colors"
          >
            {ex.length > 34 ? ex.slice(0, 34) + "…" : ex}
          </button>
        ))}
      </div>
    </div>
  );
}
