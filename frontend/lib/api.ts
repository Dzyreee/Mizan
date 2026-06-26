// Thin client for the Naghami FastAPI backend.
import type { AdaptResult, AssessResult, Diagnosis, Progress } from "./types";

export const API_BASE =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://localhost:8000";

export const DEMO_CHILD_ID = "demo-child";

async function asJson<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = `${res.status}`;
    try {
      detail = (await res.json()).detail ?? detail;
    } catch {
      /* ignore */
    }
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return res.json() as Promise<T>;
}

export async function health(): Promise<boolean> {
  try {
    const r = await fetch(`${API_BASE}/health`, { cache: "no-store" });
    return r.ok;
  } catch {
    return false;
  }
}

/** Assess from a recorded audio blob (real child flow). */
export function assessAudio(
  targetText: string,
  audio: Blob,
  childId?: string,
  childName?: string,
): Promise<AssessResult> {
  const fd = new FormData();
  fd.append("target_text", targetText);
  fd.append("audio", audio, "reading.webm");
  if (childId) fd.append("child_id", childId);
  if (childName) fd.append("child_name", childName);
  return fetch(`${API_BASE}/assess`, { method: "POST", body: fd }).then(asJson<AssessResult>);
}

/** Assess from a transcript (demo / no-mic flow). */
export function assessTranscript(
  targetText: string,
  transcript: string,
  childId?: string,
  childName?: string,
): Promise<AssessResult> {
  const fd = new FormData();
  fd.append("target_text", targetText);
  fd.append("transcript", transcript);
  if (childId) fd.append("child_id", childId);
  if (childName) fd.append("child_name", childName);
  return fetch(`${API_BASE}/assess`, { method: "POST", body: fd }).then(asJson<AssessResult>);
}

export function adapt(
  diagnosis: Diagnosis,
  opts: { includeImage?: boolean; includeAudio?: boolean } = {},
): Promise<AdaptResult> {
  return fetch(`${API_BASE}/adapt`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      diagnosis,
      include_image: opts.includeImage ?? true,
      include_audio: opts.includeAudio ?? true,
    }),
  }).then(asJson<AdaptResult>);
}

/** Fanar picks the most relevant pre-generated illustration for `text`. */
export function pickIllustration(
  text: string,
  candidates: { id: string; description: string }[],
): Promise<{ id: string }> {
  return fetch(`${API_BASE}/pick-illustration`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, candidates }),
  }).then(asJson<{ id: string }>);
}

export function getProgress(childId = DEMO_CHILD_ID): Promise<Progress> {
  return fetch(`${API_BASE}/progress?child_id=${encodeURIComponent(childId)}`, {
    cache: "no-store",
  }).then(asJson<Progress>);
}
