import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Playful indigo + energetic orange (design-system: kids/education).
        brand: {
          DEFAULT: "#4F46E5",
          light: "#818CF8",
          dark: "#3730A3",
        },
        accent: { DEFAULT: "#F97316", light: "#FB923C" },
        ink: "#1E1B4B",
        canvas: "#EEF2FF",
        // Miscue semantics (also used by the highlighter + legend).
        correct: "#059669",
        substitution: "#E11D48",
        omission: "#D97706",
        extra: "#7C3AED",
      },
      fontFamily: {
        display: ["var(--font-display)", "system-ui", "sans-serif"],
        body: ["var(--font-body)", "system-ui", "sans-serif"],
      },
      boxShadow: {
        soft: "0 1px 2px rgba(30,27,75,0.04), 0 8px 24px rgba(79,70,229,0.08)",
        glow: "0 0 0 4px rgba(249,115,22,0.18)",
      },
      keyframes: {
        "pulse-glow": {
          "0%, 100%": { boxShadow: "0 0 0 0 rgba(249,115,22,0.5)" },
          "50%": { boxShadow: "0 0 0 10px rgba(249,115,22,0)" },
        },
        "grow-up": {
          from: { transform: "scaleY(0)", opacity: "0" },
          to: { transform: "scaleY(1)", opacity: "1" },
        },
        "fade-in-up": {
          from: { opacity: "0", transform: "translateY(8px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        "pulse-glow": "pulse-glow 1.6s ease-in-out infinite",
        "grow-up": "grow-up 700ms cubic-bezier(0.22,1,0.36,1) both",
        "fade-in-up": "fade-in-up 350ms ease-out both",
      },
    },
  },
  plugins: [],
};

export default config;
