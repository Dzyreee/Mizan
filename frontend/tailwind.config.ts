import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // "Playful Sky" — one calm primary (sky) + one celebratory accent (orange).
        // `dark` shades drive the claymorphic "pressed" bottom-edge on buttons/nodes.
        brand: {
          DEFAULT: "#1CB0F6", // primary: buttons, path, primary actions
          light: "#6FCBF9",
          dark: "#1690CE", // pressed bottom-shadow / borders
        },
        accent: {
          DEFAULT: "#FF9600", // streaks, stars, celebrations
          light: "#FFB23E",
          dark: "#E07E00",
        },
        ink: "#1A2B4C", // text
        canvas: "#F7FAFC", // background
        // Reading feedback (icon/underline always paired — never color alone).
        correct: "#22C55E",
        substitution: "#FB7185",
        omission: "#FF9600",
        extra: "#A78BFA",
      },
      fontFamily: {
        display: ["var(--font-display)", "system-ui", "sans-serif"],
        body: ["var(--font-body)", "system-ui", "sans-serif"],
      },
      boxShadow: {
        // Claymorphic double shadow: tight contact + soft sky bloom.
        soft: "0 1px 2px rgba(26,43,76,0.05), 0 10px 28px rgba(28,176,246,0.10)",
        clay: "0 6px 0 rgba(22,144,206,0.0), 0 12px 30px rgba(28,176,246,0.18)",
        glow: "0 0 0 4px rgba(255,150,0,0.20)",
      },
      keyframes: {
        "pulse-glow": {
          "0%, 100%": { boxShadow: "0 0 0 0 rgba(28,176,246,0.45)" },
          "50%": { boxShadow: "0 0 0 12px rgba(28,176,246,0)" },
        },
        "grow-up": {
          from: { transform: "scaleY(0)", opacity: "0" },
          to: { transform: "scaleY(1)", opacity: "1" },
        },
        "fade-in-up": {
          from: { opacity: "0", transform: "translateY(8px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        bob: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-6px)" },
        },
        pop: {
          "0%": { transform: "scale(0.6)", opacity: "0" },
          "70%": { transform: "scale(1.12)", opacity: "1" },
          "100%": { transform: "scale(1)" },
        },
      },
      animation: {
        "pulse-glow": "pulse-glow 1.7s ease-in-out infinite",
        "grow-up": "grow-up 700ms cubic-bezier(0.22,1,0.36,1) both",
        "fade-in-up": "fade-in-up 350ms ease-out both",
        bob: "bob 2.6s ease-in-out infinite",
        pop: "pop 420ms cubic-bezier(0.22,1,0.36,1) both",
      },
    },
  },
  plugins: [],
};

export default config;
