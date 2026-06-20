// Verdict shown as a wax-seal stamp rather than a generic pill.
type Status = "verified" | "review" | "unverified";

const COPY: Record<Status, { ar: string; en: string; ring: string; ink: string }> = {
  verified: { ar: "موثّق", en: "VERIFIED", ring: "border-verified", ink: "text-verified" },
  review: { ar: "مراجعة", en: "NEEDS REVIEW", ring: "border-mismatch", ink: "text-mismatch" },
  unverified: { ar: "غير موثّق", en: "UNVERIFIED", ring: "border-ink-soft", ink: "text-ink-soft" },
};

export function Seal({ status }: { status: Status }) {
  const c = COPY[status];
  return (
    <div
      className={`shrink-0 w-[88px] h-[88px] rounded-full border-2 ${c.ring} ${c.ink}
        flex flex-col items-center justify-center text-center select-none`}
      style={{ rotate: "-7deg", boxShadow: "inset 0 0 0 1px rgba(0,0,0,0.06)" }}
    >
      <span className="font-arabic text-xl leading-none">{c.ar}</span>
      <span className="font-mono mt-1.5" style={{ fontSize: "0.5rem", letterSpacing: "0.18em" }}>
        {c.en}
      </span>
    </div>
  );
}
