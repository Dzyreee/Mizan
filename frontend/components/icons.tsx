// Small Lucide-style SVG icon set (no emojis — design-system rule).
import type { SVGProps } from "react";

function Svg(props: SVGProps<SVGSVGElement>) {
  return (
    <svg
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      {...props}
    />
  );
}

export const MicIcon = (p: SVGProps<SVGSVGElement>) => (
  <Svg {...p}>
    <rect x="9" y="2" width="6" height="12" rx="3" />
    <path d="M5 10v1a7 7 0 0 0 14 0v-1" />
    <path d="M12 18v4" />
  </Svg>
);

export const StopIcon = (p: SVGProps<SVGSVGElement>) => (
  <Svg {...p}>
    <rect x="6" y="6" width="12" height="12" rx="2" />
  </Svg>
);

export const PlayIcon = (p: SVGProps<SVGSVGElement>) => (
  <Svg {...p}>
    <path d="M6 4l14 8-14 8V4z" />
  </Svg>
);

export const SparklesIcon = (p: SVGProps<SVGSVGElement>) => (
  <Svg {...p}>
    <path d="M12 3l1.8 4.7L18.5 9.5 13.8 11.3 12 16l-1.8-4.7L5.5 9.5l4.7-1.8L12 3z" />
    <path d="M19 14l.7 1.8 1.8.7-1.8.7L19 19l-.7-1.8-1.8-.7 1.8-.7L19 14z" />
  </Svg>
);

export const WandIcon = (p: SVGProps<SVGSVGElement>) => (
  <Svg {...p}>
    <path d="M15 4V2" />
    <path d="M15 10V8" />
    <path d="M12.5 6.5h-2" />
    <path d="M19.5 6.5h-2" />
    <path d="m3 21 9-9" />
    <path d="m12.5 6.5 5 5" />
  </Svg>
);

export const CheckIcon = (p: SVGProps<SVGSVGElement>) => (
  <Svg {...p}>
    <path d="M20 6 9 17l-5-5" />
  </Svg>
);

export const TrendingUpIcon = (p: SVGProps<SVGSVGElement>) => (
  <Svg {...p}>
    <path d="M22 7 13.5 15.5 8.5 10.5 2 17" />
    <path d="M16 7h6v6" />
  </Svg>
);

export const BoltIcon = (p: SVGProps<SVGSVGElement>) => (
  <Svg {...p}>
    <path d="M13 2 3 14h8l-1 8 10-12h-8l1-8z" />
  </Svg>
);

export const ShieldIcon = (p: SVGProps<SVGSVGElement>) => (
  <Svg {...p}>
    <path d="M12 2 5 5v6c0 4.5 3 8 7 9 4-1 7-4.5 7-9V5l-7-3z" />
    <path d="M9 12l2 2 4-4" />
  </Svg>
);

export const BookIcon = (p: SVGProps<SVGSVGElement>) => (
  <Svg {...p}>
    <path d="M4 5a2 2 0 0 1 2-2h7v16H6a2 2 0 0 0-2 2V5z" />
    <path d="M20 5a2 2 0 0 0-2-2h-5v16h5a2 2 0 0 1 2 2V5z" />
  </Svg>
);

export const GaugeIcon = (p: SVGProps<SVGSVGElement>) => (
  <Svg {...p}>
    <path d="M12 14l4-4" />
    <path d="M3.5 18a9 9 0 1 1 17 0" />
  </Svg>
);

export const SpinnerIcon = (p: SVGProps<SVGSVGElement>) => (
  <Svg {...p} className={`animate-spin ${p.className ?? ""}`}>
    <path d="M12 3a9 9 0 1 0 9 9" />
  </Svg>
);
