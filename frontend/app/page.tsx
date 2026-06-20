"use client";

import { useState } from "react";
import { AnswerLedger } from "@/components/AnswerLedger";
import { Composer } from "@/components/Composer";
import { TracePanel } from "@/components/TracePanel";
import { Wordmark } from "@/components/Logo";
import { solve } from "@/lib/api";
import { SAMPLE } from "@/lib/sample";
import type { SolveResponse } from "@/lib/types";

export default function Home() {
  const [data, setData] = useState<SolveResponse>(SAMPLE);
  const [isSample, setIsSample] = useState(true);
  const [loading, setLoading] = useState(false);
  const [verify, setVerify] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function run(q: string) {
    setLoading(true);
    setError(null);
    try {
      const res = await solve(q, verify);
      setData(res);
      setIsSample(false);
    } catch (e) {
      setError(e instanceof Error ? e.message : "request failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex flex-col h-screen">
      {/* Header — spans the beam */}
      <header className="flex items-center justify-between px-5 py-3 border-b border-line bg-paper">
        <Wordmark />
        <div className="text-right leading-tight">
          <div className="label text-ink-soft">powered by</div>
          <div className="font-mono text-sm text-maroon tracking-[0.2em]">FANAR · QCRI</div>
        </div>
      </header>

      {loading && (
        <div className="h-0.5 bg-brass/30 overflow-hidden">
          <div className="h-full w-1/3 bg-brass animate-[pulse-dot_1s_ease-in-out_infinite]" />
        </div>
      )}

      <div className="flex-1 flex flex-col lg:flex-row min-h-0">
        {/* LEFT PAN — the ledger */}
        <section className="paper-grain lg:w-[56%] flex flex-col min-h-0 order-2 lg:order-1">
          <div className="p-5 border-b border-line">
            <Composer onSubmit={run} loading={loading} verify={verify} setVerify={setVerify} />
            {isSample && (
              <p className="label text-ink-soft mt-2">showing a sample result — ask a question to run live</p>
            )}
            {error && (
              <p className="font-mono text-xs text-mismatch mt-2">
                {error} — is the backend running at {process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}?
              </p>
            )}
          </div>
          <div className="flex-1 overflow-auto p-6">
            <AnswerLedger answer={data.answer} />
          </div>
        </section>

        {/* the brass balance-beam + RIGHT PAN — the instrument */}
        <section className="lg:w-[44%] min-h-0 order-1 lg:order-2 border-b-2 lg:border-b-0 lg:border-l-2 border-brass">
          <TracePanel trace={data.trace} live={loading} />
        </section>
      </div>
    </main>
  );
}
