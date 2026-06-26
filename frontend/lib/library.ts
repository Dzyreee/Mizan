// Pre-generated illustration library. Generate the PNGs ONCE with
// backend/scripts/gen_library.py (Oryx-IG) → frontend/public/library/<id>.png. At runtime
// Fanar picks the best-matching image for a passage/poem (a fast text call) — no live
// image generation. The Arabic `description` is what Fanar matches against.

export interface LibraryImage {
  id: string;
  src: string;
  description: string;
}

export const LIBRARY: LibraryImage[] = [
  { id: "school", src: "/library/school.png", description: "طفل يذهب إلى المدرسة حاملاً حقيبته" },
  { id: "park", src: "/library/park.png", description: "أطفال يلعبون بالكرة في حديقة خضراء" },
  { id: "cat", src: "/library/cat.png", description: "قطة صغيرة تشرب الحليب في البيت" },
  { id: "bedtime", src: "/library/bedtime.png", description: "طفل يقرأ قصة في سريره قبل النوم ليلاً" },
  { id: "birds", src: "/library/birds.png", description: "طيور صغيرة تغرّد فوق أغصان الأشجار في سماء زرقاء" },
  { id: "autumn", src: "/library/autumn.png", description: "أطفال يلعبون بين أوراق الخريف المتساقطة" },
  { id: "sea", src: "/library/sea.png", description: "أطفال يسبحون في البحر الأزرق في الصيف" },
  { id: "family", src: "/library/family.png", description: "عائلة سعيدة تتناول الطعام معاً" },
  { id: "sun", src: "/library/sun.png", description: "شمس مشرقة فوق التلال الخضراء في الصباح" },
  { id: "rain", src: "/library/rain.png", description: "طفل يحمل مظلة تحت المطر" },
  { id: "garden", src: "/library/garden.png", description: "طفل يسقي أزهاراً ملونة في حديقة" },
  { id: "music", src: "/library/music.png", description: "طفل يغني بفرح مع نوتات موسيقية" },
];

export const libraryCandidates = (): { id: string; description: string }[] =>
  LIBRARY.map(({ id, description }) => ({ id, description }));

export const librarySrc = (id: string | null): string | null =>
  LIBRARY.find((l) => l.id === id)?.src ?? null;
