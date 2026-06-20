import type { Metadata } from "next";
import { Amiri, Fraunces, IBM_Plex_Mono } from "next/font/google";
import "./globals.css";

const amiri = Amiri({
  variable: "--ff-amiri",
  subsets: ["arabic"],
  weight: ["400", "700"],
});
const fraunces = Fraunces({
  variable: "--ff-fraunces",
  subsets: ["latin"],
});
const plex = IBM_Plex_Mono({
  variable: "--ff-plex",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
});

export const metadata: Metadata = {
  title: "Mizan — ميزان · verified inheritance",
  description:
    "A voice-first, self-verifying agent for Islamic inheritance (faraid), powered by Fanar.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html
      lang="ar"
      className={`${amiri.variable} ${fraunces.variable} ${plex.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
