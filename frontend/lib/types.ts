// Types mirroring the Naghami FastAPI backend payloads.

export type WordStatus = "correct" | "substitution" | "omission";

export interface AlignedWord {
  index: number;
  target: string;
  status: WordStatus;
  spoken: string | null;
}

export interface ExtraWord {
  type: "insertion" | "repetition" | "self_correction";
  word: string;
  after_target_index: number;
}

export interface Hesitation {
  before_index: number;
  before_word: string;
  gap_sec: number;
}

export interface ErrorMap {
  target_text: string;
  transcript_text: string;
  words: AlignedWord[];
  extras: ExtraWord[];
  miscues: { type: string; target_word: string | null; spoken_word: string | null; note: string }[];
  counts: Record<string, number>;
  total_target_words: number;
  correct_words: number;
  accuracy_pct: number;
  transcript_words: number;
  duration_sec: number | null;
  wpm: number | null;
  wcpm: number | null;
  timestamps_available: boolean;
  hesitations: Hesitation[];
}

export interface DiagnosisPattern {
  label: string;
  evidence: string;
  confidence: string;
}

export interface Diagnosis {
  patterns: DiagnosisPattern[];
  weak_sounds: string[];
  focus: string;
  encouragement: string;
  specialist_note: string;
  _safety_scrubbed?: boolean;
}

export interface TraceStep {
  name: string;
  model: string;
  latency_ms: number;
  summary: string;
  input: unknown;
  output: unknown;
  status: "ok" | "error";
  error: string | null;
}

export interface Trace {
  steps: TraceStep[];
  total_latency_ms: number;
}

export interface AssessResult {
  target_text: string;
  transcript: string;
  error_map: ErrorMap;
  diagnosis: Diagnosis | null;
  trace: Trace;
  recorded?: boolean;
}

export interface ExercisePlan {
  title: string;
  target_sounds: string[];
  practice_words: string[];
  practice_passage: string;
  verse_prompt: string;
  illustration_prompt: string;
  pronunciation_words: string[];
}

export interface Pronunciation {
  word: string;
  b64: string;
  mime: string;
  bytes: number;
}

export interface GeneratedExercise {
  verse: string | null;
  illustration: { b64: string; mime: string; bytes: number } | null;
  pronunciations: Pronunciation[];
}

export interface AdaptResult {
  plan: ExercisePlan;
  generated: GeneratedExercise;
  trace: Trace;
}

export interface SoundProgress {
  sound: string;
  series: { date: string; accuracy: number; n_words: number }[];
  first: number;
  latest: number;
  delta: number;
  trend: "improving" | "declining" | "flat";
  sessions: number;
}

export interface Progress {
  child_id: string;
  name: string;
  sessions_count: number;
  sounds: SoundProgress[];
  overall: { date: string; accuracy: number; wpm: number | null }[];
}
