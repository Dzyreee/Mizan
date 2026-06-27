# FANAR_NOTES, discovered API facts & findings (Iqra)

> Phase 0 discovery for **Iqra** completed **2026-06-23** against a live key.
> ✅ = confirmed by a smoke test this run. Model IDs live in `backend/app/fanar/models.py`;
> reproducible probes live in `backend/smoke/` (raw payloads in `smoke/_out/`, gitignored).

## Connection
| Item | Value |
|------|-------|
| Base URL | `https://api.fanar.qa/v1` |
| Auth | `Authorization: Bearer $FANAR_API_KEY` (loaded from `backend/.env`, never hardcoded) |
| Key length seen | 32 chars |
| Compatibility | **Mostly** OpenAI-compatible (chat/audio/images via `openai` SDK). Exceptions below. |
| Request access | https://api.fanar.qa/request/en |

### ⚠️ Network finding (onboarding gotcha)
`api.fanar.qa` is **blocked on some WiFi → HTTP 403** (HTML body, `via: 1.1 google`,
served *before* auth, not an auth error). **Fix: VPN or 5G hotspot.** With the block
lifted the same request returns `401` (no key) / `200` (with key). Flag in README.
Also observed: **intermittent read-timeouts** through the VPN, wrap discovery calls in
a small retry.

---

## Models

### Listed by `GET /v1/models` (11)
`Fanar` · `Fanar-C-1-8.7B` · `Fanar-C-2-27B` · `Fanar-S-1-7B` · `Fanar-Sadiq` ·
`Fanar-Oryx-IVU-2` · `Fanar-Shaheen-MT-1` · `Fanar-Aura-STT-1` · `Fanar-Aura-STT-LF-1` ·
`Fanar-Aura-TTS-2` · `Fanar-Oryx-IG-2`  (all `owned_by: QCRI`)

### Accepted enums per endpoint (from invalid-model 422 probes, the real source of truth)
| Endpoint | Accepted `model` values |
|---|---|
| `POST /chat/completions` | `Fanar`, `Fanar-Agentic`, `Fanar-S-1-7B`, `Fanar-C-1-8.7B`, `Fanar-C-2-27B`, `Islamic-RAG`, `Fanar-Sadiq`, `Fanar-Sadiq-Agentic`, `Fanar-Oryx-IVU-2` |
| `POST /images/generations` | `Fanar-Oryx-IG-2` |
| `POST /audio/speech` (TTS) | `Fanar-Aura-TTS-2`, `Fanar-Sadiq-TTS-1` |
| `POST /audio/transcriptions` (STT) | (no enum given; `Fanar-Aura-STT-1` / `-LF-1` work) |

### Role mapping for Iqra (what each model does)
| Iqra job | Model ID | Module | Status |
|------------|----------|--------|--------|
| Transcribe child reading | `Fanar-Aura-STT-1` (long-form `-LF-1`) | `fanar/stt.py` | ✅ |
| Diagnose pattern + plan exercise | `Fanar-C-2-27B` (JSON output) | `fanar/chat.py` | ✅ |
| Generate practice verse | `Fanar` **(Diwan fallback)** | `fanar/diwan.py` | ✅ (see below) |
| Illustrate exercise | `Fanar-Oryx-IG-2` | `fanar/image.py` | ✅ |
| Pronounce hard words | `Fanar-Aura-TTS-2` | `fanar/tts.py` | ✅ |
| (stretch) English parent summary | `Fanar-Shaheen-MT-1` | TBD | not tested this run |
| (stretch) Photo→target text | `Fanar-Oryx-IVU-2` | TBD | not tested this run |
| (Phase 6) Content safety | `POST /moderations` (model TBD) | TBD | endpoint exists |

---

## 🔴 THE FAITHFULNESS GATE, the design-determining result

**Question:** does Aura STT transcribe what the child *actually said* (errors and all), or
silently "correct" misreadings toward fluent text? Iqra detects errors by diffing the
transcript against a KNOWN target, so this decides the whole strategy.

**Method** (no child recording needed): synthesize a deliberately *misread* version of a
passage with Aura TTS, transcribe it back with Aura STT, and check per-error whether the
miscue survived. (`smoke/10_faithfulness_gate.py`.)

```
TARGET : ذهب الولد إلى المدرسة في الصباح
MISREAD: ذهب الورد إلى المدرصة في المساء      (3 injected errors)
STT    : ذَهَبَ الوَردُ إلى المَدرَسَةِ في المَساء
```

| Injected error | Type | Result |
|---|---|---|
| الولد → **الورد** (ل/ر) | whole-word sub (valid word) | **FAITHFUL ✅** kept الورد |
| المدرسة → **المدرصة** (س→ص) | within-word emphatic sub (→ a *non-word*) | **NORMALIZED ❌** snapped back to المدرسة |
| الصباح → **المساء** | semantic word swap (valid word) | **FAITHFUL ✅** kept المساء |

**Verdict, MIXED, and the pattern is the insight:**
- **Real-word miscues are preserved** (substitutions to valid words, and by extension
  omissions/insertions/word-order). These are *trustworthy* signals.
- **Non-word mispronunciations get auto-corrected** to the nearest valid word. The classic
  child errors, **emphatic softening (ص→س, ض→د, ط→ت), letter swaps that yield non-words**
, may be **invisible to a pure text diff.**

**⚠️ Confound (be honest in the demo):** this is a TTS→STT *round-trip*, so the
normalization could occur in TTS (reading the non-word as the real word) and/or in STT's
language model. Either way the *pipeline* hides non-word errors. Validate with a **real
child recording** in the Phase 6 eval harness (the user listed exactly this as an eval goal).

**Implications for Phase 1 (engine design):**
1. Word-level **substitutions, omissions, insertions, repetitions, self-corrections** survive
   → classify these confidently from the alignment.
2. Do **not** rely on the transcript alone for fine **phonetic/emphatic** errors, treat
   them as lower-confidence and corroborate with **timing/hesitation** + repeated-word signals.
3. Surface emphatic/letter-level concerns only as soft "patterns worth checking", never hard
   counts (also aligns with the honest-framing HARD RULE).

---

## Endpoint shapes (confirmed this run)

### `GET /v1/models`, ⚠️ NOT OpenAI-shaped
Payload key is **`models`**, not `data`. `openai` SDK `models.list()` returns nothing, use
a raw GET (`smoke/00_list_models.py`).

### `POST /v1/chat/completions`, OpenAI shape ✅
`{model, messages, max_tokens, temperature}` → `choices[0].message.content`. Arabic fine.
- **Native tools:** `Fanar` accepts the `tools` param but **never emits `tool_calls`** (prose).
  The agentic models (`Fanar-Agentic`, `Fanar-Sadiq-Agentic`) that would do tool-calling are
  **not authorized** for our key. → **Use JSON-structured output** for diagnose/plan.
- **JSON output ✅:** with a "output ONLY JSON" system prompt, both `Fanar` and `Fanar-C-2-27B`
  returned clean parseable JSON on a neutral prompt.

### STT, `POST /v1/audio/transcriptions` ✅ (OpenAI shape)
`client.audio.transcriptions.create(model="Fanar-Aura-STT-1", file=...)` → `.text`.
Round-trip reproduced the Arabic sentence with diacritics.
- **⚠️ No timestamps:** `response_format="verbose_json"` + `timestamp_granularities=["word","segment"]`
  is *accepted* and returns the keys `duration/segments/words/usage`, but they come back
  **empty/None** (at least for short clips on `Fanar-Aura-STT-1`). → **WPM & hesitation must be
  derived from the audio locally**, not from the API (client-reported recording duration, or
  parse the file). Re-check whether `-LF-1` populates segments for longer audio.

### TTS, `POST /v1/audio/speech` ✅
`{model: "Fanar-Aura-TTS-2", voice: <Name>, input: <text>}` → binary audio.
- **⚠️ Format is MP3** (MPEG ADTS layer III, 64 kbps, 24 kHz mono), **not WAV**, one short
  line ≈ 20 KB. Save as `.mp3`; plays natively in `<audio>`. (Old notes said WAV, wrong.)
- **Voices are PROPER NAMES** at `GET /v1/audio/voices` (generic strings 422). **10 voices,
  re-verified:**
  - **Arabic** (`languages: ['ar']`): **Noor, Huda, Radwa** (F) · **Jasim, Hamad, Abdulrahman** (M)
  - **English** (British accent): Amelia, Emily (F) · Harry, Jake (M)
  - Iqra default = **Noor** (warm female Arabic). Fields per voice: `name, name_ar, gender,
    accent, languages, type, emotion`.

### Image gen, `POST /v1/images/generations` ✅ (OpenAI shape)
`client.images.generate(model="Fanar-Oryx-IG-2", prompt=..., n=1)` → `data[0].b64_json`
(base64 PNG, not a URL). One 1024×1024 PNG ≈ **0.56 MB** this run (decoded). The kids' bird
illustration came out clean and on-prompt. **Use for decorative art only, never to render the
practice Arabic text** (Oryx-IG is unreliable on precise letterforms; verify in Phase 6).

### Diwan poetry, ❌ NOT AVAILABLE → Fanar fallback ✅
There is **no Diwan model** on this key: absent from `/v1/models`, from every endpoint enum,
and **no dedicated route** (`/diwan`, `/poetry`, `/poems` all 404). **Fallback:** prompting the
`Fanar` chat model in Arabic for a short kid verse drilling a target sound produced good,
sound-loaded output (e.g. a 4-line عصفور/صباح verse dense with **ص**). It's free-verse rhythm,
**not strict classical meter**. `models.DIWAN = "Fanar"`, `DIWAN_AVAILABLE = False`.

### FanarGuard content safety, `POST /v1/moderations` ✅ (Phase 6 confirmed)
Model **`Fanar-Guard-2`**, body `{model, prompt, response}` → `{safety, cultural_awareness}`
(floats ~0–5, **higher = safer**). It judges a prompt/response PAIR. Calibration: a gentle
kids' verse scored safety **4.44** / cultural 4.29; violent text scored **1.04** / 0.94.
Iqra treats content safe at `safety ≥ 3.0 and cultural ≥ 2.5`. See `fanar/guard.py`.

### Shaheen translation, `POST /v1/translations` ✅ (Phase 6 confirmed)
`{model: "Fanar-Shaheen-MT-1", text, langpair: "ar-en"}` → `{id, text}`. Clean ar→en output
(used for the expat-parent English progress summary). NOT OpenAI-shaped → raw httpx.

### Oryx-IVU image understanding, `POST /v1/chat/completions` ✅ (Phase 6 confirmed)
Model `Fanar-Oryx-IVU-2`, OpenAI vision message shape (`content: [{type:text}, {type:image_url,
image_url:{url:"data:image/png;base64,..."}}]`). Reads Arabic text from images, used to read a
book page into the target passage, and in the eval to read back Oryx-IG output. **Eval finding:
Oryx-IG asked for the letter ص produced "الله"-style calligraphy; IVU read it as `الله`/`ب`, confirms Oryx-IG cannot render specific Arabic letters (decorative art only).**

---

## Data usage (mobile budget)
Full Phase 0 run ≈ **0.6 MB**, almost entirely the one Oryx-IG image (~0.56 MB). Chat/STT/TTS
calls are KB-scale. Image regeneration is the only thing to watch when iterating.

## Surprises / limitations log → feeds the README "recommendations for improving Fanar"
1. **403 network block** on some WiFi (pre-auth HTML), confusing onboarding; needs VPN/hotspot.
2. **`/models` uses `models` not `data`**, breaks OpenAI SDK `models.list()`.
3. **Agentic / native-tool models gated** for our key → must hand-roll JSON structured output.
4. **No Diwan model exposed**, a poetry/meter model is advertised in the Fanar family but is
   not reachable via the API on this key. *Recommendation: expose Diwan (with meter control).*
5. **Aura STT normalizes non-word mispronunciations** (round-trip), hides emphatic/letter
   errors a reading tutor cares about. *Recommendation: a "verbatim / disable-LM" STT mode +
   per-word confidence.*
6. **Aura STT returns no timestamps** despite accepting `verbose_json`, forces client-side
   timing. *Recommendation: populate word/segment timestamps.*
7. **Aura TTS returns MP3** while the extension/casual docs imply WAV, minor, but document it.
8. **`/moderations` exists but undocumented enum**, needs trial to wire FanarGuard.
