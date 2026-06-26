"use client";
import type { ButtonHTMLAttributes } from "react";

type Variant = "primary" | "accent" | "white";
type Size = "md" | "lg";

const VARIANTS: Record<Variant, string> = {
  primary: "bg-brand text-white border-brand-dark hover:brightness-105",
  accent: "bg-accent text-white border-accent-dark hover:brightness-105",
  white: "bg-white text-ink border-sky-200 hover:bg-sky-50",
};

const SIZES: Record<Size, string> = {
  md: "px-5 py-3 text-base rounded-2xl border-b-4",
  lg: "px-7 py-4 text-lg rounded-[1.25rem] border-b-[6px]",
};

// Signature claymorphic "pressed" pill: solid fill + darker bottom edge that
// collapses on :active (translateY) for a 3D press. Big tap target, bold label.
export function PressButton({
  variant = "primary",
  size = "lg",
  fullWidth,
  className = "",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: Variant;
  size?: Size;
  fullWidth?: boolean;
}) {
  return (
    <button
      {...props}
      className={[
        "inline-flex select-none items-center justify-center gap-2 font-extrabold tracking-tight",
        "cursor-pointer transition-[transform,filter,background-color] duration-150 ease-out",
        "active:translate-y-[3px] active:border-b-2",
        "disabled:cursor-not-allowed disabled:opacity-50 disabled:active:translate-y-0 disabled:active:border-b-[6px]",
        "focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-brand/30",
        SIZES[size],
        VARIANTS[variant],
        fullWidth ? "w-full" : "",
        className,
      ].join(" ")}
    />
  );
}
