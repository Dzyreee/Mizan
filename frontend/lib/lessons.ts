// Hardcoded lesson list = the path nodes. No backend lesson concept exists (Phase 5
// gamification is mocked client-side). Difficulty RAMPS with level: early levels are a
// short easy sentence; later levels are longer multi-sentence passages with harder,
// less-common words. `demoMisread` = what the demo "child" reads (deliberate miscues
// that survive Aura normalization) so the no-mic demo produces a coherent diagnosis.
//
// The reading-screen illustration is NOT stored per lesson — Fanar picks the best match
// from the shared library (see lib/library.ts) at runtime via a fast text call.

export interface Lesson {
  id: number;
  /** Short kid-facing node title (Arabic). */
  title: string;
  passage: string;
  demoMisread: string;
}

export const LESSONS: Lesson[] = [
  // L1 — very short, easy
  {
    id: 1,
    title: "المدرسة",
    passage: "ذهب الولد إلى المدرسة",
    demoMisread: "ذهب الولد إلى الحديقة",
  },
  // L2 — short
  {
    id: 2,
    title: "الكرة",
    passage: "تلعب البنت بالكرة في الحديقة",
    demoMisread: "تلعب البنت بالكرة في البيت",
  },
  // L3 — one longer sentence
  {
    id: 3,
    title: "القصة",
    passage: "يقرأ الطفل قصة جميلة قبل النوم كل ليلة",
    demoMisread: "يقرأ الطفل قصة جميلة بعد النوم",
  },
  // L4 — two short sentences
  {
    id: 4,
    title: "الصباح",
    passage: "استيقظ أحمد مبكرا في الصباح. غسل وجهه وذهب إلى المدرسة.",
    demoMisread: "استيقظ أحمد متأخرا في الصباح. غسل وجهه وذهب إلى البيت.",
  },
  // L5 — two sentences, harder words
  {
    id: 5,
    title: "الطيور",
    passage: "تحب الطيور الصغيرة أن تغرد فوق الأشجار. تطير بعيدا في السماء الزرقاء الواسعة.",
    demoMisread: "تحب الطيور الصغيرة أن تطير فوق الأشجار. تطير بعيدا في السماء الواسعة.",
  },
  // L6 — three sentences, hardest / less-common vocabulary
  {
    id: 6,
    title: "الخريف",
    passage:
      "في فصل الخريف تتساقط أوراق الأشجار الذهبية. يجري الأطفال فرحين بين الحدائق الخضراء. يجمعون الأوراق الملونة ويضحكون بسعادة.",
    demoMisread:
      "في فصل الخريف تتساقط أوراق الأشجار. يجري الأطفال بين الحدائق الخضراء. يجمعون الأوراق ويضحكون.",
  },
];

export const lessonById = (id: number | null): Lesson | undefined =>
  LESSONS.find((l) => l.id === id);
