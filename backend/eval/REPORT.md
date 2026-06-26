# Naghami — Fanar Evaluation Findings

_Run 2026-06-24 · 4 checks · 23.7s total._

## aura_faithfulness

**Q:** Does Aura STT preserve a child's reading errors?

**Result:** MIXED — 2 real-word miscue(s) preserved, 1 non-word (emphatic) miscue(s) normalized toward the nearest valid word

**Recommendation for Fanar:** Offer a verbatim / disabled-LM STT mode + per-word confidence so phonetic and emphatic miscues (ص↔س, ض↔د, ط↔ت) survive for reading assessment.

<details><summary>details</summary>

```json
{
  "target": "ذهب الولد إلى المدرسة في الصباح",
  "misread_spoken": "ذهب الورد إلى المدرصة في المساء",
  "transcript": "ذَهَبَ الوَردُ إلى المَدرَسَةِ في المَساء",
  "per_error": [
    {
      "error": "whole-word sub (ل/ر)",
      "verdict": "preserved"
    },
    {
      "error": "emphatic sub (س→ص, non-word)",
      "verdict": "normalized"
    },
    {
      "error": "semantic word swap",
      "verdict": "preserved"
    }
  ],
  "preserved": 2,
  "normalized": 1
}
```

</details>

## aura_child_pitch

**Q:** How does Aura STT handle higher-pitched, child-like speech?

**Result:** Aura round-trips clear synthetic speech well across pitches (accuracy spread 0.0 pts). True child speech (higher F0 + disfluency) was NOT available to test.

**Recommendation for Fanar:** Publish Aura accuracy on a children's speech set (high F0, disfluencies, invented words); add per-word confidence to flag low-confidence child audio.

<details><summary>details</summary>

```json
{
  "sentence": "العصفور الصغير يطير بسرعة فوق الشجرة",
  "per_voice": [
    {
      "voice": "Noor",
      "pitch": "female / higher-pitched",
      "accuracy_pct": 83.3,
      "transcript": "العُصفورُ الصَغيرُ يَطيرُ بِسُرعَةٍ فَوقَ الشَجَرَه"
    },
    {
      "voice": "Hamad",
      "pitch": "male / lower-pitched",
      "accuracy_pct": 83.3,
      "transcript": "العُصفورُ الصَغيرُ يَطيرُ بِسُرعَةٍ فَوقَ الشَجَرَه"
    }
  ],
  "caveat": "Proxy via TTS voices; no real 6-8yo recordings were available."
}
```

</details>

## diwan_age_appropriateness

**Q:** Was the Diwan/Fanar verse age-appropriate for a 6-8 year old?

**Result:** Verse generated in 16 words; FanarGuard safety 4.54, judge reading_level easy, appropriate=True

**Recommendation for Fanar:** Expose the Diwan model via API with a child reading-level / meter control; the chat fallback sometimes drifts to advanced vocabulary without tight prompting.

<details><summary>details</summary>

```json
{
  "verse": "صاحَ العصفُورُ في الصباحِ  \nوصوتهُ يملأ الأماكنَ الجَميلَهْ  \nيغني طوال اليوم فرحًا  \nويطيرُ بين الأشجار عاليًا.",
  "word_count": 16,
  "avg_word_len": 4.9,
  "long_words": [],
  "fanarguard": {
    "safe": true,
    "safety": 4.54,
    "cultural_awareness": 4.23,
    "threshold": 3.0,
    "model": "Fanar-Guard-2"
  },
  "llm_judge": {
    "appropriate": true,
    "reading_level": "easy",
    "reasons": [
      "The language used is simple and clear.",
      "The vocabulary is suitable for young children.",
      "The sentences are short and easy to understand."
    ]
  },
  "note": "No real Diwan model on this key — verse is the Fanar chat fallback."
}
```

</details>

## oryx_arabic_rendering

**Q:** Did Oryx-IG render the target Arabic letter legibly?

**Result:** Asked Oryx-IG for the letter ص; Oryx-IVU read it back as: "ب" → NOT legible ✗

**Recommendation for Fanar:** Oryx-IG is unreliable for exact Arabic letterforms — keep it to decorative art and render all reading text in the app's font layer (we already do).

<details><summary>details</summary>

```json
{
  "requested_letter": "ص",
  "ivu_readback": "ب",
  "legible": false,
  "image_bytes": 420583,
  "image_saved": "/Users/yacine/Desktop/Naghami/backend/eval/_out/eval_oryx_letter.png"
}
```

</details>
