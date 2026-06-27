# اقرأ · Iqra, an adaptive Arabic reading tutor for children

> **Iqra is a reading-SUPPORT tool, not a diagnostic tool.** It helps every child
> practice and improves reading, and it can surface early error *patterns* for a parent to
> discuss with a professional. It never claims to diagnose dyslexia or any condition, never
> outputs a clinical label, and never tells a parent their child "has" anything. Flags are
> always phrased as *"patterns worth checking with a specialist."*

Built for the **Fanar Hackathon 2026**. A child reads a known passage aloud; Iqra
transcribes the reading, compares it against the known target text to find exactly which
words and sounds they struggled with, diagnoses the pattern, then generates a targeted,
illustrated practice exercise for those sounds and models the correct pronunciation. Over
multiple sessions it tracks whether the child improves on their weak sounds.

---

## 1. Problem statement

Early reading difficulties are common, but specialist assessment is scarce, expensive, and
intimidating, especially in Arabic, with its emphatic consonants (ص ض ط ظ), short-vowel
diacritics, and rich morphology. Parents have no everyday way to know *which sounds* their
child struggles with, or whether practice is helping.

Iqra gives every child fun, targeted reading practice **and** gives parents an honest,
non-clinical view of recurring error patterns over time, the kind of concrete signal that
makes a conversation with a specialist productive, without ever pretending to be one.

## 2. Why the core works with **zero training data**

This is a **read-aloud task against a KNOWN target text**, so we need no trained model and no
labelled dataset. The target passage *is* the ground truth. We transcribe the child, align the
transcript to the target, and **every mismatch is a measurable reading error**. That
deterministic alignment is the foundation of the whole app.

## 3. Solution architecture

```
                ┌──────────────── child reads aloud ────────────────┐
                │                                                    ▼
   target text  │   ╔════════════╗   transcript   ╔═══════════════════════════╗
  (ground truth)─┼──▶║  Aura STT  ║──────────────▶ ║  DETERMINISTIC ENGINE     ║
                │   ╚════════════╝                 ║  (pure Python, no LLM)    ║
                │                                   ║  align · classify miscues ║
                │                                   ║  accuracy · WPM · pauses  ║
                │                                   ╚═════════════╤═════════════╝
                │                                      error map  │
                │   ╔════════════╗   "pattern"                    ▼
                │   ║ Fanar-27B  ║◀──────────  DIAGNOSE  (JSON, honest-framed)
                │   ╚═════╤══════╝
                │   plan  ▼
                │   ╔════════════╗   ╔══════════╗   ╔══════════╗   ╔════════════╗
                └──▶║ Fanar-27B  ║──▶║  Diwan*  ║   ║ Oryx-IG  ║   ║  Aura TTS  ║
                    ║   (plan)   ║   ║  verse   ║   ║   art    ║   ║ pronounce  ║
                    ╚════════════╝   ╚════╤═════╝   ╚════╤═════╝   ╚═════╦══════╝
                                          └──── FanarGuard validates ────╝
                                                  (child-safe content)
```

**The separation is the design (HARD RULE):** the deterministic engine *owns* the error map;
the LLM only *reasons on top of it* (diagnose / plan). The alignment and miscue classification
are never done by an LLM, they're pure, unit-tested Python. This makes Iqra auditable and
keeps error detection trustworthy.

### Repository layout
```
backend/
  app/
    engine/      # ★ deterministic alignment + miscue engine (pure Python, no LLM)
    fanar/       # one module per Fanar model: stt, tts, chat, diwan, image, guard,
                 #   translate (Shaheen), vision (Oryx-IVU), each demoable in isolation
    agent/       # assess, diagnose, plan, generate, adapt, pick_image, trace (agentic loop)
    memory/      # per-child JSON profiles + deterministic per-sound progress
    api.py       # FastAPI: /assess /adapt /speak /pick-illustration /progress /read-page /health
  scripts/       # one-off tooling: gen_library (Oryx-IG art), seed_progress, demo_*
  eval/          # evaluation harness → findings.json + REPORT.md
  smoke/         # Fanar discovery + faithfulness scripts
  tests/         # 36 unit/integration tests (pytest, no network)
frontend/        # Next.js (App Router) + Tailwind — multi-screen kids web app (RTL, AR/EN)
  components/    #   screens (Path/Session/Results/Practice/Progress/Trace) + Jad mascot + UI
  public/
    library/     #   pre-generated illustration library (Fanar picks the best match at runtime)
    jad-images/  #   the Jad mascot art set
FANAR_NOTES.md   # every discovered Fanar API fact, shape, and quirk
docs/            # design specs (incl. the Phase 5 kids-app redesign)
```

### Frontend experience (what the judges click through)

A single-page **Next.js** app styled as a friendly, **Duolingo-inspired** kids' app — original
visuals, mascot (**Jad**), and a "Playful Sky" palette. Arabic-first **RTL** with a one-tap **EN**
toggle, fully **responsive** (mobile → tablet → desktop). No login; one demo child ("Layla, 7").
Six animated screens:

1. **Path** — a winding level map (done = star, current pulses, future locked) with a streak chip,
   a **Level badge** (level + progress bar), stars, and the mascot greeting.
2. **Session** — the child reads a passage aloud (mic) or runs a no-mic **demo**. The passage sits
   in one card **beside its illustration**. Each word is **tappable for a pronunciation hint**
   (Aura TTS), capped at 2 per lesson so it never reads the whole line for them.
3. **Results** — accuracy, words/min, and the tricky sounds. A good read fires **confetti + a
   cheering mascot**; a struggle shows a gentle, never-negative "let's practice together" state.
4. **Practice** — a Diwan-style **verse built from the child's weak sounds**, shown beside a
   matching illustration, with a **full-verse play** button (the reward).
5. **Progress** — per-sound improvement chart across sessions (real `/progress` data) + streak /
   sessions / stars tiles.
6. **How it works** (hidden) — the full **agent trace**: every step's model, latency, and I/O.

**Illustrations** use the pre-generated `public/library` set; at runtime Fanar **picks** the
best-matching image for the passage/verse (a fast text call), with a deterministic keyword
fallback so images still match if the model is offline. The UI degrades gracefully — it renders
from sample data with the backend off and never blocks on a single failed call.

## 4. Agentic workflow design

One reading attempt flows through a single, **fully-traced** pipeline. Every step records its
model, latency, input, and output, so the whole reasoning process is inspectable in the UI (no
black box):

| Step | Owner | What it does |
|------|-------|--------------|
| **transcribe** | Aura STT | child audio → transcript |
| **align** | deterministic engine | transcript vs target → error map (miscues, accuracy, WPM) |
| **diagnose** | Fanar-C-2-27B (JSON) | names the *pattern* + the weak sounds to target |
| **plan** | Fanar-C-2-27B (JSON) | designs a targeted exercise for those sounds |
| **generate-verse** | Diwan → Fanar | a short verse loaded with the weak sounds |
| **generate-image** | Oryx-IG | a decorative illustration |
| **generate-audio** | Aura TTS | models the hard words for the child to imitate |
| **safety-check** | FanarGuard | validates all child-facing text before it's shown |

Native tool-calling is **not authorized** on our key (Phase 0 finding), so every LLM step uses
**strict-JSON structured output**, parsed deterministically.

## 5. Use of Fanar models + external tools

| Fanar model | Role in Iqra | Notes |
|-------------|-----------------|-------|
| `Fanar-Aura-STT-1` | transcribe the child's reading (core input) | no usable timestamps → WPM from local audio |
| `Fanar-C-2-27B` | diagnose pattern + plan exercise | JSON output; honest-framing prompt + code-level scrub |
| `Fanar` | practice **verse** (Diwan fallback) | **no Diwan model exists on the key**, see §7 |
| `Fanar-Oryx-IG-2` | pre-generate the illustration **library**; Fanar then *picks* the best match per text | decorative only, cannot render exact Arabic letters |
| `Fanar-Aura-TTS-2` | pronounce hard words | returns **MP3** (not WAV); 10 named voices |
| `Fanar-Guard-2` | validate child-facing content | `safety` + `cultural_awareness` scores (0–5) |
| `Fanar-Shaheen-MT-1` | English progress summary for expat parents | `/translations` endpoint |
| `Fanar-Oryx-IVU-2` | read target text from a photographed book page | OpenAI vision shape |

**External tools / stack:** Python **FastAPI** backend; the **`openai`** SDK pointed at the
Fanar base URL (`https://api.fanar.qa/v1`) plus raw **`httpx`** for the non-OpenAI-shaped
endpoints; **pytest** for the engine; **Next.js (App Router) + Tailwind** for the frontend
(RTL Arabic, **Baloo Bhaijaan 2** + **Tajawal** fonts). The API key lives only in
`backend/.env` (gitignored) and is loaded at runtime, never hardcoded, never printed.

## 6. Evaluation results

Run `cd backend && .venv/bin/python -m eval.harness` → `eval/REPORT.md` + `eval/findings.json`.

| Question | Finding |
|----------|---------|
| **Does Aura preserve a child's reading errors?** | **MIXED.** Real-word miscues (substitutions/omissions/insertions) are preserved; **non-word mispronunciations (emphatic ص↔س etc.) are normalized** to the nearest valid word. → the engine trusts word-level miscues and treats fine phonetic errors as low-confidence, corroborated by timing. |
| **How does Aura handle higher-pitched (child-like) speech?** | Clear synthetic speech round-trips equally well across higher- (female) and lower-pitched (male) voices (≈0-pt spread). **Caveat:** real 6–8-yo speech (high F0 + disfluency) wasn't available, a recommendation to Fanar below. |
| **Was the Diwan/Fanar verse age-appropriate?** | Yes, FanarGuard safety ≈ **4.5/5**, an LLM judge rated reading level **"easy"** and appropriate. The Fanar fallback can drift to advanced vocabulary without tight prompting (we cap length + demand simple words). |
| **Did Oryx-IG render the target Arabic letters?** | **No.** Asked for the letter ص, it produced "الله"-style calligraphy; **Oryx-IVU read it back as `الله` / `ب`**, Oryx-IG can't render specific letterforms. We therefore render *all* reading text in the app's font layer and use Oryx-IG for decoration only. |

## 7. Concrete recommendations for improving Fanar

1. **Expose the Diwan poetry model via the API.** It's advertised in the Fanar family but is
   absent from `/models`, every endpoint enum, and has no route (`/diwan` → 404). Poetry-with-
   meter is ideal for children's phonics; the chat fallback works but lacks metrical control.
2. **Add a verbatim / disabled-LM mode + per-word confidence to Aura STT.** Its language model
   "fixes" non-word mispronunciations, which *hides* exactly the emphatic/letter errors a
   reading tutor needs to see.
3. **Populate Aura STT timestamps.** `verbose_json` + `timestamp_granularities` is accepted but
   returns empty `words`/`segments`/`duration`, forcing client-side timing for WPM/hesitations.
4. **Publish Aura accuracy on children's speech** (high pitch, disfluency, invented words), the
   population this kind of app serves.
5. **Document the bespoke endpoints.** `/models` uses key `models` not `data`; `/translations`
   and `/moderations` are non-OpenAI shapes; `Fanar-Guard-2` needs a prompt/response pair. These
   cost real discovery time (see `FANAR_NOTES.md`).
6. **Unblock onboarding:** `api.fanar.qa` returns a confusing pre-auth `403` (HTML, `via: google`)
   on some networks, looks like an auth bug but is a network block (needs VPN/hotspot).

## 8. Setup & run

**Prerequisites:** Python 3.11+, Node 18+, a Fanar API key, and network access to `api.fanar.qa`
(VPN/5G hotspot if your WiFi returns a pre-auth 403). Put your key in `backend/.env` (see below) —
it is the only secret, is gitignored, and is never printed.

### Option A — Docker (one command)
```bash
cp backend/.env.example backend/.env     # add your FANAR_API_KEY
docker compose up --build                # frontend → http://localhost:3000, backend → :8000
```
> Note: on macOS a host VPN may not route Docker traffic to `api.fanar.qa`. If the backend logs
> 403s, run it on the host instead (Option B).

### Option B — Run locally
```bash
# ── backend ──
cd backend
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # then put your FANAR_API_KEY in .env
pytest                          # 36 tests, no network
uvicorn app.api:app --reload --port 8000

# ── frontend (new terminal) ──
cd frontend
npm install
npm run dev                     # http://localhost:3000
```

The UI renders fully from sample data even with the backend off; the mic and **عرض توضيحي**
(demo) buttons call the live backend when it's running. Optional one-off scripts:

```bash
cd backend && . .venv/bin/activate
python -m scripts.seed_progress         # seed the demo child's progress history
python -m scripts.gen_library           # (re)generate the illustration library via Oryx-IG
```

### Endpoints
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/assess` | audio/transcript → error map + diagnosis + trace (records session if `child_id`) |
| POST | `/adapt` | diagnosis → planned exercise (verse + art + audio) + FanarGuard + trace |
| POST | `/speak` | text → base64 MP3 (Aura TTS) — full-verse playback + per-word reading hints |
| POST | `/pick-illustration` | text + candidates → best-match library image id (Fanar pick, keyword fallback) |
| GET | `/progress?child_id=` | per-sound trend across sessions |
| GET | `/progress/summary?child_id=&lang=en` | parent summary (Shaheen translates to English) |
| POST | `/read-page` | photo of a book page → target text (Oryx-IVU) |
| GET | `/health` | liveness |

## 9. Hard rules honored
1. API key only in `backend/.env`, gitignored, never printed. · 2. Model IDs/shapes confirmed
live, not assumed (`FANAR_NOTES.md`). · 3. Alignment/miscue classification is deterministic
Python, never an LLM. · 4. JSON structured output (native tools unavailable). · 5. Honest
framing + FanarGuard validation of child-facing content. · 6. Each Fanar model in its own module.
