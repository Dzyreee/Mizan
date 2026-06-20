import type { SolveResponse } from "./types";

// A real verified result (man → wife + 2 sons + daughter, 120000 QAR), so the UI
// renders complete without the backend running. Replaced by live data on submit.
export const SAMPLE_QUESTION =
  "توفي رجل وترك زوجة وابنين وبنتاً، والتركة 120000 ريال";

export const SAMPLE: SolveResponse = {
  answer: {
    mode: "full",
    verified: true,
    verdict: "MATCH — verified",
    heirs: { husband: false, wives: 1, sons: 2, daughters: 1, father: false, mother: false },
    estate: 120000,
    currency: "ريال",
    distribution_kind: "normal",
    distribution_note: null,
    shares: [
      { heir: "wife", count: 1, fraction: "1/8", ratio: "5/40", each: "1/8", basis: "fard", amount_total: 15000, amount_each: 15000, currency: "ريال" },
      { heir: "son", count: 2, fraction: "7/10", ratio: "28/40", each: "7/20", basis: "residue", amount_total: 84000, amount_each: 42000, currency: "ريال" },
      { heir: "daughter", count: 1, fraction: "7/40", ratio: "7/40", each: "7/40", basis: "residue", amount_total: 21000, amount_each: 21000, currency: "ريال" },
    ],
    ruling:
      "الحمد لله والصلاة والسلام على رسول الله وعلى آله وصحبه، أما بعد: فإذا توفي الرجل وترك زوجة وابنين وبنتاً، فإن لزوجته الثمن من التركة؛ لقول الله تعالى: «فَإِن كَانَ لَكُمْ وَلَدٌ فَلَهُنَّ ٱلثُّمُنُ مِمَّا تَرَكْتُم»، والباقي بعد نصيب الزوجة يقسم بين الأبناء والبنت للذكر مثل حظ الأنثيين؛ لقوله تعالى: «يُوصِيكُمُ ٱللَّهُ فِىٓ أَوْلَٰدِكُمْ لِلذَّكَرِ مِثْلُ حَظِّ ٱلْأُنثَيَيْنِ».",
    citations: [
      { source: "quran", text: "فَإِن كَانَ لَكُمْ وَلَدٌ فَلَهُنَّ ٱلثُّمُنُ مِمَّا تَرَكْتُم — النساء ١٢" },
      { source: "quran", text: "لِلذَّكَرِ مِثْلُ حَظِّ ٱلْأُنثَيَيْنِ — النساء ١١" },
    ],
    verification: {
      agree: true,
      verdict: "MATCH — verified",
      comparisons: [
        { heir: "wife", deterministic: "1/8", ruling: "1/8", basis: "fard", status: "match" },
        { heir: "son", deterministic: "7/10", ruling: null, basis: "residue", status: "informational" },
        { heir: "daughter", deterministic: "7/40", ruling: null, basis: "residue", status: "informational" },
      ],
      issues: [],
      verifier_shares: { wife: "1/8" },
    },
  },
  trace: {
    total_latency_ms: 17273,
    steps: [
      { name: "Plan: extract heirs & estate", kind: "plan", model: "Fanar-C-2-27B", status: "ok", latency_ms: 4378, input: SAMPLE_QUESTION, output: { heirs: { wives: 1, sons: 2, daughters: 1 }, estate: 120000, currency: "ريال" } },
      { name: "Tool: deterministic faraid calculator", kind: "tool", model: null, status: "ok", latency_ms: 0, input: { wives: 1, sons: 2, daughters: 1 }, output: { kind: "normal", base: 40 } },
      { name: "Tool: Islamic-RAG ruling + citations", kind: "ruling", model: "Islamic-RAG", status: "ok", latency_ms: 10796, input: SAMPLE_QUESTION, output: { citations: 2 } },
      { name: "Verifier: reconcile ruling shares vs deterministic", kind: "verify", model: "Fanar-C-2-27B", status: "ok", latency_ms: 2099, input: { deterministic: "wife 1/8 …" }, output: { agree: true, verdict: "MATCH — verified" } },
    ],
  },
};
