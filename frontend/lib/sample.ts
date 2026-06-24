// Realistic sample payloads (shaped exactly like the backend) so the UI renders fully
// populated for offline development/screenshots. Replaced by live data on interaction.
import type { AdaptResult, AssessResult, Progress } from "./types";

export const SAMPLE_TARGET = "ذهب الولد الصغير إلى المدرسة في الصباح";

export const sampleAssess: AssessResult = {
  target_text: SAMPLE_TARGET,
  transcript: "ذَهَبَ الوَردُ إلى المَدرَسَةِ في المَساء",
  error_map: {
    target_text: SAMPLE_TARGET,
    transcript_text: "ذَهَبَ الوَردُ إلى المَدرَسَةِ في المَساء",
    words: [
      { index: 0, target: "ذهب", status: "correct", spoken: "ذَهَبَ" },
      { index: 1, target: "الولد", status: "substitution", spoken: "الوَردُ" },
      { index: 2, target: "الصغير", status: "omission", spoken: null },
      { index: 3, target: "إلى", status: "correct", spoken: "إلى" },
      { index: 4, target: "المدرسة", status: "correct", spoken: "المَدرَسَةِ" },
      { index: 5, target: "في", status: "correct", spoken: "في" },
      { index: 6, target: "الصباح", status: "substitution", spoken: "المَساء" },
    ],
    extras: [],
    miscues: [
      { type: "substitution", target_word: "الولد", spoken_word: "الوَردُ", note: "" },
      { type: "omission", target_word: "الصغير", spoken_word: null, note: "" },
      { type: "substitution", target_word: "الصباح", spoken_word: "المَساء", note: "" },
    ],
    counts: { substitution: 2, omission: 1 },
    total_target_words: 7,
    correct_words: 4,
    accuracy_pct: 57.1,
    transcript_words: 6,
    duration_sec: 24.0,
    wpm: 15.0,
    wcpm: 10.0,
    timestamps_available: false,
    hesitations: [],
  },
  diagnosis: {
    patterns: [
      {
        label: "استبدال كلمات بأخرى مشابهة في الشكل",
        evidence: "قرأ «الولد» كأنها «الورد»",
        confidence: "high",
      },
      { label: "حذف بعض الكلمات من الجملة", evidence: "حُذفت كلمة «الصغير»", confidence: "medium" },
    ],
    weak_sounds: ["ص", "نهايات الكلمات"],
    focus: "التدرب على نهايات الكلمات وحرف الصاد",
    encouragement: "قراءة رائعة يا بطل! لنتدرب معًا على بعض الكلمات الممتعة.",
    specialist_note: "",
  },
  trace: {
    steps: [
      {
        name: "transcribe",
        model: "Fanar-Aura-STT-1",
        latency_ms: 1948,
        summary: "Transcribed 6 words",
        input: { audio_file: "reading.webm" },
        output: { transcript: "ذَهَبَ الوَردُ إلى المَدرَسَةِ في المَساء" },
        status: "ok",
        error: null,
      },
      {
        name: "align",
        model: "deterministic-engine",
        latency_ms: 0,
        summary: "Accuracy 57.1% — miscues {'omission': 1, 'substitution': 2}",
        input: null,
        output: { accuracy_pct: 57.1, miscue_counts: { substitution: 2, omission: 1 } },
        status: "ok",
        error: null,
      },
      {
        name: "diagnose",
        model: "Fanar-C-2-27B",
        latency_ms: 7698,
        summary: "Pattern: استبدال كلمات بأخرى مشابهة في الشكل",
        input: null,
        output: null,
        status: "ok",
        error: null,
      },
    ],
    total_latency_ms: 9646,
  },
  recorded: true,
};

export const sampleAdapt: AdaptResult = {
  plan: {
    title: "رحلة الصبي الصغير إلى الحديقة",
    target_sounds: ["ص", "نهايات الكلمات"],
    practice_words: ["صغير", "حديقة", "ورود", "شمس", "طريق", "بيت"],
    practice_passage: "ذهب الصبي الصغير إلى الحديقة ليرى الورود تحت الشمس. سار في الطريق وعاد إلى بيته.",
    verse_prompt: "",
    illustration_prompt: "",
    pronunciation_words: ["صغير", "حديقة", "شمس"],
  },
  generated: {
    verse:
      "في الغابةِ الخضراءِ لعِبنا وصِدنا،\nطائرًا جميلًا فوق الأغصانِ صادَقنا.\nنهرٌ صافٍ يجري بين الصخورِ صادِحًا،\nومغامراتٌ لا تنتهي فيها نلعبُ ونهتفُ!",
    illustration: null,
    pronunciations: [
      { word: "صغير", b64: "", mime: "audio/mpeg", bytes: 4848 },
      { word: "حديقة", b64: "", mime: "audio/mpeg", bytes: 5496 },
      { word: "شمس", b64: "", mime: "audio/mpeg", bytes: 4872 },
    ],
  },
  trace: {
    steps: [
      { name: "plan", model: "Fanar-C-2-27B", latency_ms: 6564, summary: "Planned 'رحلة الصبي الصغير إلى الحديقة'", input: null, output: null, status: "ok", error: null },
      { name: "generate-verse", model: "Fanar", latency_ms: 32527, summary: "Verse: 22 words", input: null, output: null, status: "ok", error: null },
      { name: "generate-image", model: "Fanar-Oryx-IG-2", latency_ms: 14845, summary: "Illustration: PNG", input: null, output: null, status: "ok", error: null },
      { name: "generate-audio", model: "Fanar-Aura-TTS-2", latency_ms: 3897, summary: "3 pronunciation clips", input: null, output: null, status: "ok", error: null },
    ],
    total_latency_ms: 57833,
  },
};

export const sampleProgress: Progress = {
  child_id: "demo-child",
  name: "ليان",
  sessions_count: 3,
  sounds: [
    {
      sound: "ص",
      series: [
        { date: "2026-06-10", accuracy: 33.3, n_words: 3 },
        { date: "2026-06-17", accuracy: 66.7, n_words: 3 },
        { date: "2026-06-24", accuracy: 100.0, n_words: 3 },
      ],
      first: 33.3,
      latest: 100.0,
      delta: 66.7,
      trend: "improving",
      sessions: 3,
    },
    {
      sound: "ر",
      series: [
        { date: "2026-06-10", accuracy: 50.0, n_words: 4 },
        { date: "2026-06-17", accuracy: 75.0, n_words: 4 },
        { date: "2026-06-24", accuracy: 100.0, n_words: 4 },
      ],
      first: 50.0,
      latest: 100.0,
      delta: 50.0,
      trend: "improving",
      sessions: 3,
    },
  ],
  overall: [
    { date: "2026-06-10", accuracy: 50.0, wpm: 10.0 },
    { date: "2026-06-17", accuracy: 83.3, wpm: 12.0 },
    { date: "2026-06-24", accuracy: 100.0, wpm: 15.0 },
  ],
};
