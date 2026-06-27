# Iqra Phase 5 Redesign, Design Spec

Date: 2026-06-26
Status: Built (v1 shipped); **Revision 2 (4 refinements), implemented 2026-06-26**

### Revision 2, implementation status
- **R1 Responsive**, ✅ implemented (real breakpoints on every screen; multi-column on md/lg).
  Build + runtime render confirmed; visual screenshot pass @375/768/1280 still recommended.
- **R2 TTS**, ✅ implemented. Backend `POST /speak`; frontend `api.speak` + `useSpeak` hook.
  Practice = full-verse play button (reward). Session = per-word tappable hints, `HINT_LIMIT = 2`,
  greys out + "you've used your hints" after the limit, resets per node.
- **R3 Image+text one card, side-by-side**, ✅ implemented (Session + Practice).
- **R4 Polish + level + micro + confetti**, ✅ implemented. New `LevelBadge` (level + filled bar)
  on Path and Session, separate from the streak. Confetti fires on good Results (≥70%); micro-
  interactions on buttons, path nodes, and tappable words.

## Goal

Redesign the Iqra frontend to feel like a real consumer kids' app (Duolingo as
**structural/interaction** inspiration only, original visuals, mascot, palette). Multi-screen
flow, no auth, one hardcoded child profile ("Layla, age 7"). Wire to existing backend
endpoints `/assess`, `/adapt`, `/progress` (+ small new Fanar-backed helpers, see below).

## Decisions (locked with user)

1. **Single-page animated views.** One Next.js route; a `screen` state machine in an
   `AppProvider`; `framer-motion <AnimatePresence>` transitions. Results held in React context.
2. **Gamification mocked client-side** in `localStorage` (path nodes, completed/locked, streak,
   stars, level). Real diagnosis (`/assess`) + per-sound progress (`/progress`) from backend.
3. **Deps**: `framer-motion` + `canvas-confetti` (user runs `npm install`).
4. **Commits**: engineer does NOT commit; user commits from VS Code.
5. **Illustrations: no live image gen.** Fixed library (`lib/library.ts`, `public/library/*.png`
   generated once via `scripts/gen_library.py`); at runtime Fanar PICKS the best match via
   `POST /pick-illustration` (fast text call). `/adapt` called with `include_image:false`.

## Color palette, "Playful Sky" (unchanged)

Primary `#1CB0F6` (+ dark `#1690CE`) · Accent `#FF9600` · Background `#F7FAFC` · Text `#1A2B4C`.
Fonts: Baloo Bhaijaan 2 (display) + Tajawal (body). RTL/Arabic-first with EN toggle.

---

# Revision 2, the 4 refinements

## R1. Responsive layout (do FIRST, gates everything else)

The current screens render as a fixed `max-w-md` mobile column, a centered phone-sized box with
empty desktop margins. Replace with genuine responsive layouts using real breakpoints
(`sm 640 / md 768 / lg 1024 / xl 1280`):

- **Containers grow**: mobile `max-w-md` → tablet `max-w-2xl/3xl` → desktop wider, content using
  the space (not a stretched phone).
- **Multi-column where it helps** (md+): image beside text (not stacked), stat tiles in a row,
  Path with a side rail (level/streak/mascot) instead of a lone centered trail, Progress as
  tiles + chart side by side.
- **Mobile stays single-column.**
- **Verification gate:** build + Playwright screenshots at **375 / 768 / 1280** and confirm each
  screen genuinely reflows (uses the sandbox `distDir` build/serve workaround). This happens
  BEFORE the other refinements. Also confirm confetti (R4) in the same pass.

## R2. Text-to-speech, different rules for the reading sentence vs. the Diwan verse

New backend helper: **`POST /speak {text}` → `{b64, mime}`** (Aura TTS of arbitrary text, via
`app.fanar.tts.synthesize`). Lazy, called on tap, with a small loading state. ⚠️ backend-touching.

**CONFIRMED with user:**
- **Reading sentence (Session screen):** **NO full read-aloud button** (would let the child skip
  reading it). Instead each word of the reading passage is individually tappable; a tap plays ONLY
  that word via `/speak`, as a hint. **Hint limit 1–2 per lesson**, tracked client-side: after the
  limit, remaining words grey out with a friendly "you've used your hints!" message. Resets when a
  new node opens.
- **Diwan verse (Practice screen, the reward):** a full **"play whole verse"** button → `/speak`
  on the entire verse. Full playback is fine, it's the reward.

`/adapt` now also called with `include_audio:false` (per-word pre-gen no longer needed, verse +
hint audio are lazy via `/speak`), keeping `/adapt` fast (verse text only).

## R3. Image size & layout, images are content, not decoration

Anywhere an Oryx-IG illustration appears (Practice verse card; Session reading card):

- Image + its related text live in **ONE card** (not two stacked elements).
- Inside: **side-by-side** on tablet/desktop (image one side, text the other), **stacked** on
  mobile. Image takes a **generous share** of the card (roughly 40–50% on desktop), not a thumbnail.

## R4. Child-friendly polish + level indicator + interactivity + confetti

- **Polish (6–9 yr tone):** softer/rounder shapes throughout, gentle shadows (no harsh edges),
  **bigger/friendlier BODY type** (raise base body size + line-height, not just headings), playful
  supporting SVG icons. Keep Playful Sky.
- **Difficulty/level indicator:** a `LevelBadge`, "المستوى N / Level N" + a small filled bar
  (progress = completed nodes / total), shown on **Path and Session**, visually **separate from
  the streak counter**, so current level + progress read at a glance. (Level = current node index.)
- **More micro-interactions:** framer-motion `whileHover` (subtle scale ~1.03) + `whileTap`
  (bounce/scale ~0.95) on buttons, path nodes, and tappable words, Duolingo-spirit, not static.
- **Confetti:** confirm it FIRES on a good Results outcome (accuracy ≥ threshold), confetti +
  cheering mascot + bright framing, and is **clearly distinct** from the gentle, never-negative
  encouraging state (no confetti, calm mascot, warm "let's practice together"). Verified in R1's
  screenshot pass.

---

## Screens (updated)

1. **Path**, winding node trail; current pulses, done = star, future locked. Top: streak chip +
   **LevelBadge** (separate) + mascot greeting; gear (trace) + EN toggle + progress entry. Desktop:
   side rail uses the width.
2. **Session**, reading card = **image beside the Arabic passage** (R3), big pressed mic, no-mic
   demo. The passage words are **individually tappable hints (1–2 limit, no full readout)** (R2);
   after assess, struggled words highlighted; pill Continue. LevelBadge in header.
3. **Results**, accuracy %, WPM, tricky sounds. Good → **confetti + cheer** (R4); struggle →
   gentle encouragement. Continue → Practice.
4. **Practice**, Diwan as the HERO (NOT a "bonus/reward"): **verse card** = Diwan verse +
   Fanar-picked image **side by side** (R3) + **full-verse play** button (R2) + weak-sound chips
   explaining the targeting. Done → mark node complete, bump streak/stars/level → Path.
5. **Progress**, per-sound chart (real `/progress`) + streak/sessions/stars tiles; desktop 2-col.
6. **How it works (hidden)**, agent trace (assess/diagnose/plan/generate, model, latency).

## Backend changes (flagged, per the hard rule)

- `POST /pick-illustration {text, candidates}` → `{id}` (already shipped, `app/agent/pick_image.py`).
- **NEW `POST /speak {text}` → `{b64, mime}`** (Aura TTS via `app/fanar/tts.synthesize`), for R2.
- `/adapt` called with `include_image:false` + `include_audio:false` (existing params; no code change).

## Out of scope

Auth, real persistence beyond localStorage, multi-child, backend pipeline rewrites.
