import type { SolveResponse } from "./types";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function solve(
  question: string,
  verify: boolean,
): Promise<SolveResponse> {
  const res = await fetch(`${API}/solve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, verify }),
  });
  if (!res.ok) {
    const detail = await res.text().catch(() => "");
    throw new Error(`Backend ${res.status}: ${detail.slice(0, 200)}`);
  }
  return res.json();
}
