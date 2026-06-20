import type { Answer, FullAnswer, LlmOnlyAnswer } from "@/lib/types";
import { Seal } from "./Seal";
import { ShareTable } from "./ShareTable";

const KIND_AR: Record<string, string> = { normal: "قسمة عادية", awl: "عَوْل", radd: "ردّ" };

function SectionLabel({ children }: { children: React.ReactNode }) {
  return <div className="label text-brass rule-brass mb-3">{children}</div>;
}

export function AnswerLedger({ answer }: { answer: Answer }) {
  return answer.mode === "full" ? <FullView a={answer} /> : <AblationView a={answer} />;
}

function FullView({ a }: { a: FullAnswer }) {
  const status = a.verified ? "verified" : "review";
  return (
    <div className="space-y-7">
      <div className="flex items-start justify-between gap-4">
        <div>
          <SectionLabel>distribution · {a.distribution_kind}</SectionLabel>
          <div className="font-arabic text-ink-soft text-lg" dir="rtl">
            التركة:{" "}
            <span className="font-mono text-ink tnum">
              {a.estate.toLocaleString("en-US")} {a.currency}
            </span>
            <span className="mx-2 text-brass">·</span>
            {KIND_AR[a.distribution_kind] ?? a.distribution_kind}
          </div>
        </div>
        <Seal status={status} />
      </div>

      <ShareTable shares={a.shares} />

      {a.distribution_note && (
        <p className="font-arabic text-ink-soft text-base border-r-2 border-brass pr-3" dir="rtl">
          {a.distribution_note}
        </p>
      )}

      {!a.verified && a.verification.issues.length > 0 && (
        <div className="border border-mismatch/40 bg-mismatch/5 p-3">
          <div className="label text-mismatch mb-1.5">verifier flagged</div>
          <ul className="space-y-1">
            {a.verification.issues.map((i, n) => (
              <li key={n} className="font-mono text-sm text-ink">— {i}</li>
            ))}
          </ul>
        </div>
      )}

      <div>
        <SectionLabel>الحكم الشرعي · Islamic-RAG</SectionLabel>
        <p className="font-arabic text-lg leading-[2.1] text-ink" dir="rtl">
          {a.ruling}
        </p>
      </div>

      {a.citations.length > 0 && (
        <div>
          <SectionLabel>المصادر · citations</SectionLabel>
          <ul className="space-y-2" dir="rtl">
            {a.citations.map((c, n) => (
              <li key={n} className="flex gap-2 items-start">
                <span className="label text-brass mt-1.5 shrink-0">{c.source}</span>
                <span className="font-arabic text-ink leading-loose">«{c.text}»</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function AblationView({ a }: { a: LlmOnlyAnswer }) {
  const ls = a.llm_shares;
  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <SectionLabel>llm-only · no verifier</SectionLabel>
          <p className="font-arabic text-mismatch text-lg" dir="rtl">{a.warning}</p>
        </div>
        <Seal status="unverified" />
      </div>

      <div className="border border-line p-4 bg-paper-deep/30">
        {ls.blocked ? (
          <p className="font-mono text-sm text-mismatch">blocked — {ls.detail}</p>
        ) : ls.parsed ? (
          <pre className="font-mono text-sm text-ink whitespace-pre-wrap">
            {JSON.stringify(ls.parsed, null, 2)}
          </pre>
        ) : (
          <p className="font-arabic text-lg leading-loose text-ink" dir="rtl">{ls.raw}</p>
        )}
      </div>

      <p className="font-mono text-xs text-ink-soft">
        No deterministic calculator or verifier ran — toggle back to the verified pipeline to
        cross-check this against ground truth.
      </p>
    </div>
  );
}
