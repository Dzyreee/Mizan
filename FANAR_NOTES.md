# FANAR_NOTES — discovered API facts & findings

> Phase 0 discovery completed **2026-06-20** against a live key. ✅ = confirmed working
> from a smoke test. Model IDs live in `backend/app/fanar/models.py`.

## Connection
| Item | Value |
|------|-------|
| Base URL | `https://api.fanar.qa/v1` |
| Auth | `Authorization: Bearer $FANAR_API_KEY` |
| Compatibility | **Mostly** OpenAI-compatible (chat/images/audio via `openai` SDK). Exceptions below. |
| Request access | https://api.fanar.qa/request/en |

### ⚠️ Network finding
`api.fanar.qa` is blocked on the dev's home WiFi → **HTTP 403** (HTML, `via: 1.1 google`,
served before auth). Not an auth problem. **Fix: use a 5G hotspot.** Flag in README as an
onboarding gotcha.

### ⚠️ Authorization finding
Our key is **NOT authorized** for the agentic models (`Fanar-Agentic`, `Fanar-Sadiq-Agentic`)
→ `422 "Model not authorized"`. These are the native tool-calling models, so **native
function calling is unavailable to us**. Planner must use JSON-structured output (works, see below).

---

## Models

### Listed by `GET /v1/models` (11)
`Fanar` · `Fanar-C-1-8.7B` · `Fanar-C-2-27B` · `Fanar-S-1-7B` · `Fanar-Sadiq` ·
`Fanar-Oryx-IVU-2` · `Fanar-Shaheen-MT-1` · `Fanar-Aura-STT-1` · `Fanar-Aura-STT-LF-1` ·
`Fanar-Aura-TTS-2` · `Fanar-Oryx-IG-2`

### Extra routing ids accepted by `/chat/completions` but NOT in the list
(found via invalid-model 422 enum probe): `Fanar-Agentic`, `Islamic-RAG`,
`Fanar-Sadiq-Agentic`. → Always probe the endpoint's enum, don't trust `/models` alone.

### Role mapping (what we use)
| Capability | Model ID | Status |
|------------|----------|--------|
| Chat / planner | `Fanar` (or `Fanar-C-2-27B`) | ✅ |
| Structured extraction | `Fanar` via JSON output | ✅ (no native tools) |
| Islamic ruling + citations | `Islamic-RAG` (alt `Fanar-Sadiq`) | ✅ |
| Speech-to-text | `Fanar-Aura-STT-1` (long-form: `-LF-1`) | ✅ |
| Text-to-speech | `Fanar-Aura-TTS-2` | ✅ |
| Image generation | `Fanar-Oryx-IG-2` | ✅ |
| Image/video understanding | `Fanar-Oryx-IVU-2` (chat endpoint) | not smoke-tested |
| Translation | `Fanar-Shaheen-MT-1` | ✅ |

---

## Endpoint shapes (confirmed)

### `GET /v1/models` — ⚠️ NOT OpenAI-shaped
Response key is **`models`**, not `data`: `{"id": "...", "models": [{"id","object","created","owned_by"}]}`.
The `openai` SDK `models.list()` returns `None` here — use a raw GET (see `00_list_models.py`).

### `POST /v1/chat/completions` — OpenAI shape ✅
Standard `{model, messages, max_tokens}` → `choices[0].message.content`. Arabic round-trips fine.
- **Native tools:** `Fanar` accepts the `tools` param but **never emits `tool_calls`** (answers as prose).
- **JSON fallback ✅:** with a system prompt demanding a JSON object, both `Fanar` and
  `Fanar-C-2-27B` return clean parseable JSON — *on a neutral prompt*.
- **RAG hijack gotcha:** faraid-worded prompts to `Fanar` get auto-answered as an Islamic
  ruling (with `<quran_start>` citations) and ignore JSON instructions. → For deterministic
  extraction, phrase the planner prompt neutrally / in English, not as a fatwa question.

### Islamic — `POST /v1/chat/completions`, model `Islamic-RAG` ✅
Returns a ruling with **inline citation tags** `<quran_start>…<quran_end>` in `content`
(not a separate citations field). Parse those tags out for the trace panel.
We never trust its numbers (HARD RULE 3) — calculator is ground truth.

### TTS — `POST /v1/audio/speech` ✅
Body `{model: "Fanar-Aura-TTS-2", voice: <name>, input: <text>}` → binary audio (WAV, ~37 KB for one sentence).
- **Voices are PROPER NAMES**, listed at `GET /v1/audio/voices`. Generic strings ("female", "default") 422.
- Arabic voices: **Noor, Huda, Radwa** (F) · **Jasim, Hamad, Abdulrahman** (M). English: Amelia, Harry, Jake, Emily.

### STT — `POST /v1/audio/transcriptions` ✅ (OpenAI shape)
`audio.transcriptions.create(model="Fanar-Aura-STT-1", file=...)` → `.text`.
Round-trip (TTS→STT) reproduced the Arabic sentence correctly (with diacritics).

### Image gen — `POST /v1/images/generations` ✅ (OpenAI shape)
`images.generate(model="Fanar-Oryx-IG-2", prompt=..., n=1)` → `data[0].b64_json`
(returns base64, not URL). One 1024×1024 PNG ≈ **2.4 MB** (~3.2 MB as b64 over the wire).
Per HARD RULE 4: decorative banner only, never legal Arabic text.

### Translation — `POST /v1/translations` ✅ ⚠️ NOT OpenAI-shaped
Body `{model: "Fanar-Shaheen-MT-1", text: <ar>, langpair: "ar-en"}` →
`{"id": "...", "text": "<english>"}`. Use raw httpx, not the SDK.

---

## Data usage (for the 3 GB mobile budget)
Full smoke run ≈ **3.5 MB**, almost entirely the one image gen (~3.2 MB). Text/audio calls
are KB-scale. Image regeneration is the only thing to watch when iterating.

## Surprises / limitations log (feeds Phase 5 "improve Fanar" recommendations)
1. **403 network block** on some WiFi (pre-auth) — confusing for onboarding.
2. **`/models` uses `models` not `data`** — breaks OpenAI SDK `models.list()`.
3. **`/translations` is a bespoke endpoint** — not OpenAI-shaped.
4. **Agentic / native-tool models gated** behind authorization our key lacks → must hand-roll
   JSON structured output for the planner.
5. **Islamic-RAG hijack:** the default `Fanar` model silently switches to fatwa-mode on
   inheritance wording, overriding format instructions — a real risk for a faraid app; we
   isolate deterministic extraction from the ruling call to avoid it.
6. Citations are **inline tags**, not structured fields — needs parsing.
7. **Content-safety filter blocks share COMPUTATION** (400 `content_filter`, `param:response`)
   when a base chat model is asked to compute inheritance shares — even with neutral wording.
   Reading/EXTRACTING shares from text is fine. → verifier must read Sadiq's stated shares,
   not compute its own; computation stays in the deterministic engine.
8. **Islamic-RAG gender bias:** for "a woman died leaving a husband", the ruling defaulted to
   the common "man leaves a wife" framing and assigned a *wife* a share. Our verifier caught it
   (flagged a heir the calculator doesn't have) — a live demonstration of the verifier's value.
9. **'awl/radd shares are not LLM-verifiable.** Only fixed (fard) shares can be reconciled
   against the ruling; the proportional 'awl/radd arithmetic is owned solely by the unit-tested
   deterministic engine. The verifier hard-checks fard, treats residue/'awl/radd as informational.
