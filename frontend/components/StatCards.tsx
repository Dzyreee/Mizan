import type { ErrorMap } from "@/lib/types";
import { CheckIcon, GaugeIcon, BookIcon } from "./icons";

function accuracyTone(pct: number) {
  if (pct >= 85) return "text-emerald-600";
  if (pct >= 60) return "text-amber-600";
  return "text-rose-600";
}

export function StatCards({ em }: { em: ErrorMap }) {
  const miscues = Object.values(em.counts).reduce((a, b) => a + b, 0);
  const cards = [
    {
      label: "الدقّة",
      value: `${em.accuracy_pct}%`,
      sub: `${em.correct_words} من ${em.total_target_words} كلمة`,
      icon: <CheckIcon className="h-5 w-5" />,
      tone: accuracyTone(em.accuracy_pct),
    },
    {
      label: "سرعة القراءة",
      value: em.wpm != null ? `${em.wpm}` : "—",
      sub: "كلمة/دقيقة",
      icon: <GaugeIcon className="h-5 w-5" />,
      tone: "text-brand",
    },
    {
      label: "الملاحظات",
      value: `${miscues}`,
      sub: "نقاط للتدرّب",
      icon: <BookIcon className="h-5 w-5" />,
      tone: "text-accent",
    },
  ];
  return (
    <div className="grid grid-cols-3 gap-3">
      {cards.map((c) => (
        <div key={c.label} className="rounded-2xl border border-indigo-100/70 bg-white p-4 shadow-soft">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium text-slate-500">{c.label}</span>
            <span className={c.tone}>{c.icon}</span>
          </div>
          <div className={`mt-1 text-3xl font-extrabold ${c.tone}`}>{c.value}</div>
          <div className="text-xs text-slate-400">{c.sub}</div>
        </div>
      ))}
    </div>
  );
}
