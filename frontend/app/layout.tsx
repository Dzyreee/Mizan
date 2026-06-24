import type { Metadata } from "next";
import { Baloo_Bhaijaan_2, Tajawal } from "next/font/google";
import "./globals.css";

const display = Baloo_Bhaijaan_2({
  subsets: ["arabic"],
  weight: ["500", "600", "700", "800"],
  variable: "--font-display",
  display: "swap",
});

const body = Tajawal({
  subsets: ["arabic"],
  weight: ["400", "500", "700"],
  variable: "--font-body",
  display: "swap",
});

export const metadata: Metadata = {
  title: "نغمي · Naghami — رفيق القراءة",
  description:
    "أداة داعمة لتعليم القراءة العربية للأطفال: تستمع، تحلّل، وتولّد تمارين مخصصة. ليست أداة تشخيص.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ar" dir="rtl" className={`${display.variable} ${body.variable}`}>
      <body>{children}</body>
    </html>
  );
}
