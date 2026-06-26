"use client";

// "Naghami bird" — an ORIGINAL singing-bird mascot (نغمي = "my melody"). Built from
// plain SVG shapes in the Playful Sky palette. Not a copy of any existing mascot.
// mood: idle (gentle bob) · happy (open beak + notes) · cheer (wings up + notes).

type Mood = "idle" | "happy" | "cheer";

export function Mascot({
  size = 120,
  mood = "idle",
  className = "",
}: {
  size?: number;
  mood?: Mood;
  className?: string;
}) {
  const singing = mood !== "idle";
  return (
    <div
      className={`${mood === "idle" ? "animate-bob" : "animate-pop"} ${className}`}
      style={{ width: size, height: size }}
      aria-hidden="true"
    >
      <svg viewBox="0 0 120 120" width={size} height={size} fill="none">
        {/* shadow */}
        <ellipse cx="60" cy="108" rx="26" ry="5" fill="#1A2B4C" opacity="0.08" />

        {/* tail */}
        <path d="M20 64c-8 2-13 9-12 16 6-1 12-4 16-9z" fill="#1690CE" />

        {/* body */}
        <ellipse cx="62" cy="64" rx="34" ry="36" fill="#1CB0F6" />
        {/* belly */}
        <ellipse cx="58" cy="74" rx="20" ry="22" fill="#EAF7FF" />

        {/* wing (lifts when cheering) */}
        <path
          d={
            mood === "cheer"
              ? "M86 40c10-6 18-4 20 2-3 7-12 12-22 12z"
              : "M84 58c9 0 16 5 17 12-7 3-16 1-21-6z"
          }
          fill="#1690CE"
        />

        {/* head tuft / melody feather */}
        <path d="M60 18c2-7 8-10 13-8-1 6-5 11-10 13z" fill="#FF9600" />

        {/* eye */}
        <circle cx="72" cy="52" r="7" fill="#fff" />
        <circle cx="74" cy="52" r="3.6" fill="#1A2B4C" />
        <circle cx="75.4" cy="50.6" r="1.2" fill="#fff" />

        {/* cheek */}
        <circle cx="64" cy="62" r="4.5" fill="#FF9600" opacity="0.28" />

        {/* beak — opens when singing */}
        {singing ? (
          <>
            <path d="M88 56l12-3-8 7z" fill="#FF9600" />
            <path d="M88 60l11 3-8 1z" fill="#E07E00" />
          </>
        ) : (
          <path d="M88 57l12-2-10 7z" fill="#FF9600" />
        )}

        {/* little feet */}
        <path d="M54 99v7M66 99v7" stroke="#E07E00" strokeWidth="3" strokeLinecap="round" />

        {/* floating melody notes when singing */}
        {singing && (
          <g fill="#FF9600">
            <circle cx="104" cy="30" r="3.5" />
            <rect x="106" y="16" width="2.4" height="14" rx="1" />
            <circle cx="96" cy="14" r="2.6" />
            <rect x="97.5" y="4" width="2" height="10" rx="1" />
          </g>
        )}
      </svg>
    </div>
  );
}
