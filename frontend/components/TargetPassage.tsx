"use client";
import type { AlignedWord } from "@/lib/types";

const LEGEND = [
  { key: "correct", label: "صحيحة", cls: "text-ink" },
  { key: "substitution", label: "مُستبدَلة", cls: "text-substitution" },
  { key: "omission", label: "محذوفة", cls: "text-omission" },
];

function WordChip({ w }: { w: AlignedWord }) {
  if (w.status === "correct") {
    return <span className="rounded-lg px-1.5 py-0.5 text-ink">{w.target}</span>;
  }
  if (w.status === "substitution") {
    return (
      <span className="group relative inline-flex flex-col items-center">
        <span className="rounded-lg bg-rose-50 px-1.5 py-0.5 text-substitution underline decoration-wavy decoration-2 underline-offset-4">
          {w.target}
        </span>
        {w.spoken && (
          <span className="mono text-[0.6rem] leading-tight text-substitution/80">{w.spoken}</span>
        )}
      </span>
    );
  }
  // omission
  return (
    <span className="rounded-lg bg-amber-50 px-1.5 py-0.5 text-omission line-through decoration-2 opacity-80">
      {w.target}
    </span>
  );
}

export function TargetPassage({
  target,
  words,
}: {
  target: string;
  words: AlignedWord[] | null;
}) {
  return (
    <div>
      <div
        dir="rtl"
        className="rounded-2xl bg-indigo-50/50 p-5 text-2xl leading-[2.6rem] tracking-wide"
      >
        {words ? (
          <span className="flex flex-wrap items-end gap-x-1.5 gap-y-3">
            {words.map((w) => (
              <WordChip key={w.index} w={w} />
            ))}
          </span>
        ) : (
          <span className="text-ink">{target}</span>
        )}
      </div>

      {words && (
        <div className="mt-3 flex flex-wrap items-center gap-3 text-xs text-slate-500">
          {LEGEND.map((l) => (
            <span key={l.key} className="inline-flex items-center gap-1.5">
              <span className={`text-base font-bold ${l.cls}`}>أ</span>
              {l.label}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
