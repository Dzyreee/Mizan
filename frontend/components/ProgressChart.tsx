"use client";
import type { Progress, SoundProgress } from "@/lib/types";
import { useLang } from "./LanguageProvider";
import { TrendingUpIcon } from "./icons";

const PALETTE = ["#4F46E5", "#F97316", "#059669", "#7C3AED"];
const W = 320, H = 160, PADL = 28, PADR = 12, PADT = 12, PADB = 24;

function shortDate(iso: string) {
  const [, m, d] = iso.split("-");
  return `${Number(d)}/${Number(m)}`;
}

function x(i: number, n: number) {
  return n <= 1 ? PADL : PADL + (i / (n - 1)) * (W - PADL - PADR);
}
function y(acc: number) {
  return PADT + (1 - acc / 100) * (H - PADT - PADB);
}

function Line({ s, color }: { s: SoundProgress; color: string }) {
  const n = s.series.length;
  const pts = s.series.map((p, i) => `${x(i, n)},${y(p.accuracy)}`).join(" ");
  return (
    <g>
      <polyline points={pts} fill="none" stroke={color} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
      {s.series.map((p, i) => (
        <circle key={i} cx={x(i, n)} cy={y(p.accuracy)} r="3.5" fill="white" stroke={color} strokeWidth="2.5" />
      ))}
    </g>
  );
}

export function ProgressChart({ progress }: { progress: Progress }) {
  const { t } = useLang();
  const sounds = progress.sounds;
  const dates = progress.overall.map((o) => o.date);

  return (
    <section className="card p-5 animate-fade-in-up">
      <div className="mb-3 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-ink">{t("progress_title")}</h2>
          <p className="text-xs text-slate-500">
            {progress.name} · {progress.sessions_count} {t("sessions_label")}
          </p>
        </div>
        <span className="chip bg-emerald-50 text-emerald-700">
          <TrendingUpIcon className="h-4 w-4" /> {t("improving")}
        </span>
      </div>

      {/* Per-sound delta highlights (the wow beat) */}
      <div className="mb-3 grid grid-cols-2 gap-2">
        {sounds.map((s, i) => (
          <div
            key={s.sound}
            className="flex items-center gap-3 rounded-2xl border border-indigo-100/70 bg-white p-3"
          >
            <span
              className="grid h-10 w-10 place-items-center rounded-xl text-xl font-extrabold text-white"
              style={{ backgroundColor: PALETTE[i % PALETTE.length] }}
            >
              {s.sound}
            </span>
            <div className="min-w-0">
              <div className="flex items-baseline gap-1.5">
                <span className="text-2xl font-extrabold text-ink">{s.latest}%</span>
                {s.delta > 0 && (
                  <span className="inline-flex items-center gap-0.5 text-xs font-bold text-emerald-600">
                    <TrendingUpIcon className="h-3.5 w-3.5" />+{s.delta}
                  </span>
                )}
              </div>
              <div className="mono text-[0.65rem] text-slate-400">
                {s.series.map((p) => `${p.accuracy}%`).join(" → ")}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Line chart (LTR: time →, rising up-right = good) */}
      <div dir="ltr" className="rounded-2xl bg-indigo-50/40 p-2">
        <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label="مخطط التقدّم">
          {[0, 50, 100].map((g) => (
            <g key={g}>
              <line x1={PADL} x2={W - PADR} y1={y(g)} y2={y(g)} stroke="#C7D2FE" strokeWidth="1" strokeDasharray="3 4" />
              <text x={PADL - 6} y={y(g) + 3} textAnchor="end" fontSize="8" fill="#94A3B8">{g}</text>
            </g>
          ))}
          {dates.map((d, i) => (
            <text key={d} x={x(i, dates.length)} y={H - 8} textAnchor="middle" fontSize="8" fill="#94A3B8" className="mono">
              {shortDate(d)}
            </text>
          ))}
          {sounds.map((s, i) => (
            <Line key={s.sound} s={s} color={PALETTE[i % PALETTE.length]} />
          ))}
        </svg>
      </div>

      <div className="mt-2 flex flex-wrap gap-3 text-xs text-slate-500">
        {sounds.map((s, i) => (
          <span key={s.sound} className="inline-flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: PALETTE[i % PALETTE.length] }} />
            {t("letter_label")} «{s.sound}»
          </span>
        ))}
      </div>
    </section>
  );
}
