import type { Metadata } from "next";
import { Baloo_Bhaijaan_2, Tajawal } from "next/font/google";
import "./globals.css";
import { LanguageProvider } from "@/components/LanguageProvider";
import { AppProvider } from "@/components/AppProvider";

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
  title: "نغمي · Naghami — reading companion",
  description:
    "Adaptive Arabic reading-support tutor for children. Listens, analyzes, generates targeted practice. Not a diagnostic tool.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  // `lang`/`dir` default to Arabic for SSR; LanguageProvider updates them on the client.
  return (
    <html lang="ar" dir="rtl" className={`${display.variable} ${body.variable}`}>
      <body>
        <LanguageProvider>
          <AppProvider>{children}</AppProvider>
        </LanguageProvider>
      </body>
    </html>
  );
}
