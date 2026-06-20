// Mirrors the backend /solve response (app/agent/orchestrator.py).

export type Basis = "fard" | "residue" | "awl" | "radd";

export interface ShareRow {
  heir: string;
  count: number;
  fraction: string;
  ratio: string;
  each: string;
  basis: Basis;
  amount_total: number;
  amount_each: number;
  currency: string;
}

export interface Citation {
  source: "quran" | "hadith" | string;
  text: string;
}

export interface HeirComparison {
  heir: string;
  deterministic: string | null;
  ruling: string | null;
  basis: Basis | null;
  status: "match" | "mismatch" | "not_stated" | "informational";
}

export interface Verification {
  agree: boolean;
  verdict: string;
  comparisons: HeirComparison[];
  issues: string[];
  verifier_shares: Record<string, string> | null;
}

export interface FullAnswer {
  mode: "full";
  verified: boolean;
  verdict: string;
  heirs: Record<string, number | boolean>;
  estate: number;
  currency: string;
  distribution_kind: "normal" | "awl" | "radd";
  distribution_note: string | null;
  shares: ShareRow[];
  ruling: string;
  citations: Citation[];
  verification: Verification;
}

export interface LlmOnlyAnswer {
  mode: "llm_only";
  verified: false;
  warning: string;
  heirs: Record<string, number | boolean>;
  estate: number;
  currency: string;
  llm_shares: {
    blocked?: boolean;
    detail?: string;
    parsed?: Record<string, unknown> | null;
    raw?: string;
  };
}

export type Answer = FullAnswer | LlmOnlyAnswer;

export interface TraceStep {
  name: string;
  kind: "plan" | "tool" | "ruling" | "verify" | "answer";
  model: string | null;
  status: "ok" | "error" | "mismatch";
  latency_ms: number;
  input: unknown;
  output: unknown;
}

export interface Trace {
  steps: TraceStep[];
  total_latency_ms: number;
}

export interface SolveResponse {
  answer: Answer;
  trace: Trace;
}
