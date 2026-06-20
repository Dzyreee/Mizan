// A balance/scale glyph — drawn, not an emoji. "Mizan" = scales.
export function ScaleGlyph({ className = "" }: { className?: string }) {
  return (
    <svg viewBox="0 0 48 48" className={className} fill="none" aria-hidden>
      <g stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
        <path d="M24 7v30" />
        <path d="M14 41h20" />
        <path d="M8 14h32" />
        <circle cx="24" cy="9" r="2.2" fill="currentColor" stroke="none" />
        {/* left pan */}
        <path d="M8 14l-5 9h10l-5-9Z" />
        <path d="M3 23a5 5 0 0 0 10 0" />
        {/* right pan */}
        <path d="M40 14l-5 9h10l-5-9Z" />
        <path d="M35 23a5 5 0 0 0 10 0" />
      </g>
    </svg>
  );
}

export function Wordmark() {
  return (
    <div className="flex items-center gap-3">
      <ScaleGlyph className="w-7 h-7 text-brass" />
      <div className="leading-none">
        <div className="flex items-baseline gap-2">
          <span className="font-arabic text-2xl text-ink">ميزان</span>
          <span
            className="font-mono text-ink-soft"
            style={{ fontSize: "0.62rem", letterSpacing: "0.34em" }}
          >
            MIZAN
          </span>
        </div>
        <div className="label text-brass mt-1">verified inheritance</div>
      </div>
    </div>
  );
}
