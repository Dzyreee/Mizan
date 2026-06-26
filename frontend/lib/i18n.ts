// Lightweight bilingual UI strings. Only the UI CHROME is translated — the Arabic
// learning content (passage, verse, weak sounds) always stays Arabic RTL.

export type Lang = "ar" | "en";

export const LANGS: Lang[] = ["ar", "en"];

export const dirOf = (lang: Lang): "rtl" | "ltr" => (lang === "ar" ? "rtl" : "ltr");

const STRINGS = {
  // Header
  tagline: { ar: "رفيق القراءة الذكي للأطفال", en: "Smart reading companion for kids" },
  support_badge: {
    ar: "أداة دعم للقراءة — ليست أداة تشخيص",
    en: "A reading-support tool — not a diagnostic tool",
  },
  status_online: { ar: "متصل", en: "Online" },
  status_demo: { ar: "وضع العرض", en: "Demo mode" },

  // Reading session
  reading_session: { ar: "جلسة القراءة", en: "Reading session" },
  reset: { ar: "إعادة تعيين", en: "Reset" },
  next_sentence: { ar: "جملة جديدة", en: "Next sentence" },
  or: { ar: "أو", en: "or" },
  demo_button: { ar: "عرض توضيحي", en: "Run demo" },
  mic_idle: { ar: "اضغط لقراءة النص", en: "Tap to read the passage" },
  mic_listening: { ar: "يستمع… اضغط للإيقاف", en: "Listening… tap to stop" },
  mic_analyzing: { ar: "جارٍ التحليل…", en: "Analyzing…" },
  mic_denied: {
    ar: "تعذّر الوصول للميكروفون — جرّب «عرض توضيحي»",
    en: "Microphone unavailable — try “Run demo”",
  },
  mic_aria_start: { ar: "ابدأ تسجيل القراءة", en: "Start recording the reading" },
  mic_aria_stop: { ar: "إيقاف التسجيل", en: "Stop recording" },
  offline_note: {
    ar: "تعذّر الاتصال بالخادم — يُعرض مثال توضيحي.",
    en: "Couldn’t reach the server — showing a sample.",
  },
  empty_hint: {
    ar: "اضغط على الميكروفون ليقرأ الطفل النص، أو جرّب «عرض توضيحي» لرؤية الدورة كاملة.",
    en: "Tap the mic to have the child read, or try “Run demo” to see the full loop.",
  },
  footer: {
    ar: "نَغَمي أداة لدعم القراءة فقط. الأنماط المعروضة للممارسة، وليست تشخيصاً طبياً — راجِع أخصائياً إذا استمرت.",
    en: "Naghami is a reading-support tool only. The patterns shown are for practice, not a medical diagnosis — consult a specialist if they persist.",
  },

  // Passage legend
  legend_correct: { ar: "صحيحة", en: "Correct" },
  legend_substitution: { ar: "مُستبدَلة", en: "Substitution" },
  legend_omission: { ar: "محذوفة", en: "Omission" },

  // Stat cards
  stat_accuracy: { ar: "الدقّة", en: "Accuracy" },
  stat_speed: { ar: "سرعة القراءة", en: "Reading speed" },
  stat_speed_sub: { ar: "كلمة/دقيقة", en: "words/min" },
  stat_notes: { ar: "الملاحظات", en: "Notes" },
  stat_notes_sub: { ar: "نقاط للتدرّب", en: "to practice" },
  of: { ar: "من", en: "of" },
  words_unit: { ar: "كلمة", en: "words" },

  // Pattern banner
  pattern_detected: { ar: "تم اكتشاف النمط", en: "Pattern detected" },
  sounds_focus: { ar: "أصوات للتركيز:", en: "Sounds to focus on:" },
  generating: {
    ar: "يُولّد تمريناً مخصّصاً لهذه الأصوات…",
    en: "Generating targeted practice for these sounds…",
  },
  exercise_ready: { ar: "تمرين مخصّص جاهز بالأسفل", en: "Targeted exercise ready below" },

  // Exercise card
  exercise_title_fallback: { ar: "تمرين مخصّص", en: "Targeted exercise" },
  illustration_placeholder: {
    ar: "رسم Oryx-IG يظهر هنا في العرض المباشر",
    en: "Oryx-IG art appears here in the live demo",
  },
  practice_text: { ar: "نص التدريب", en: "Practice text" },
  listen_repeat: { ar: "استمع وكرّر (نطق Aura)", en: "Listen & repeat (Aura voice)" },
  verse_label: { ar: "قصيدة للتدرّب (Diwan → Fanar)", en: "Practice verse (Diwan → Fanar)" },

  // Agent trace
  trace_title: { ar: "مسار الوكيل الذكي", en: "Agent trace" },
  trace_empty: {
    ar: "سيظهر تسلسل الخطوات هنا أثناء التحليل…",
    en: "Steps will appear here during analysis…",
  },
  step_transcribe: { ar: "النسخ الصوتي", en: "Transcribe" },
  step_align: { ar: "المحاذاة (محرّك حتمي)", en: "Align (deterministic engine)" },
  step_diagnose: { ar: "تشخيص النمط", en: "Diagnose pattern" },
  step_plan: { ar: "تخطيط التمرين", en: "Plan exercise" },
  "step_generate-verse": { ar: "توليد القصيدة", en: "Generate verse" },
  "step_generate-image": { ar: "توليد الرسم", en: "Generate art" },
  "step_generate-audio": { ar: "نطق الكلمات", en: "Pronounce words" },
  "step_safety-check": { ar: "فحص السلامة (FanarGuard)", en: "Safety check (FanarGuard)" },

  // Progress
  progress_title: { ar: "التقدّم عبر الجلسات", en: "Progress across sessions" },
  sessions_label: { ar: "جلسات", en: "sessions" },
  improving: { ar: "في تحسّن", en: "improving" },
  letter_label: { ar: "حرف", en: "Letter" },

  // Phase 5 — multi-screen kids flow
  child_name: { ar: "ليلى", en: "Layla" },
  child_age: { ar: "٧ سنوات", en: "Age 7" },
  greet: { ar: "مرحباً يا ليلى!", en: "Hi Layla!" },
  lets_read: { ar: "هيا نقرأ اليوم", en: "Let's read today" },
  start: { ar: "ابدأ", en: "Start" },
  locked_hint: { ar: "أكمل الدرس السابق أولاً", en: "Finish the previous lesson first" },
  streak_label: { ar: "أيام", en: "day streak" },
  stars_label: { ar: "نجمة", en: "stars" },
  my_progress: { ar: "تقدّمي", en: "My progress" },
  back_to_path: { ar: "العودة للخريطة", en: "Back to map" },
  read_aloud: { ar: "اقرأ الجملة بصوت واضح", en: "Read the sentence out loud" },
  continue: { ar: "متابعة", en: "Continue" },
  great_job: { ar: "أحسنت يا بطل!", en: "Amazing!" },
  keep_practicing: { ar: "لنتدرّب على هذا معاً!", en: "Let's practice together!" },
  tricky_sounds: { ar: "أصوات لنلعب بها", en: "Sounds to play with" },
  no_tricky: { ar: "قراءة مثالية! لا أصوات صعبة", en: "Perfect reading! No tricky sounds" },
  poem_title: { ar: "قصيدتك المخصّصة", en: "Your practice poem" },
  poem_why: {
    ar: "صُنعت من الأصوات التي تتدرّب عليها:",
    en: "Made from the sounds you're practicing:",
  },
  poem_why_generic: {
    ar: "قصيدة صنعها الذكاء لتقوية قراءتك",
    en: "An AI-made poem to strengthen your reading",
  },
  composing_poem: { ar: "نؤلّف قصيدتك…", en: "Composing your poem…" },
  poem_support: { ar: "استمع وكرّر لتتقن النطق", en: "Listen & repeat to master it" },
  finish_lesson: { ar: "تدرّبت! أنهِ الدرس", en: "Done practicing!" },
  judge_view: { ar: "كيف يعمل", en: "How it works" },
  judge_sub: { ar: "مسار الوكيل الذكي — للقُضاة", en: "Live agent trace — for judges" },

  // Level / difficulty indicator (separate from the streak)
  level_label: { ar: "المستوى", en: "Level" },

  // TTS — Diwan full playback (reward) vs. per-word reading hints
  play_verse: { ar: "استمع للقصيدة", en: "Play the verse" },
  playing: { ar: "يُشغّل…", en: "Playing…" },
  tap_hint_help: { ar: "اضغط على كلمة لسماعها", en: "Tap a word to hear it" },
  hints_left: { ar: "تلميح متبقٍ", en: "hints left" },
  hints_used: {
    ar: "استخدمت كل تلميحاتك! اقرأها بنفسك الآن.",
    en: "You've used your hints! Now read it yourself.",
  },
  practice_words_label: {
    ar: "كلمات للتدرّب · اضغط لسماعها",
    en: "Practice words · tap to hear",
  },
  focus_label: { ar: "نتدرّب على:", en: "Working on:" },
} as const;

export type StringKey = keyof typeof STRINGS;

export function translate(lang: Lang, key: StringKey): string {
  return STRINGS[key][lang];
}
