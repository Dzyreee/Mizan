"""Fanar model IDs for Naghami — single source of truth.

Most IDs were confirmed via live discovery on 2026-06-20 (salvaged from a prior
project). Items marked ⚠️ TBD were NOT used before and MUST be confirmed live in
Naghami's Phase 0 (see smoke/00b_probe.py, smoke/02_aura_tts.py, smoke/04_diwan.py):
  - DIWAN model id (not present in GET /v1/models)
  - TTS voice names (re-verified against GET /v1/audio/voices)
"""
from __future__ import annotations

# --- Chat / reasoning: diagnose the error pattern + plan the next exercise ---
# JSON-structured output only (native tool-calling is gated for our key — Phase 0 finding).
CHAT = "Fanar"               # default chat (RAG-steered); emits prose, no tool_calls
CHAT_27B = "Fanar-C-2-27B"   # largest base chat — primary for diagnosis/planning
CHAT_SMALL = "Fanar-S-1-7B"  # small/fast fallback

# --- Aura speech ---
AURA_STT = "Fanar-Aura-STT-1"        # transcribe the child reading aloud (core input)
AURA_STT_LF = "Fanar-Aura-STT-LF-1"  # long-form variant (hours-long audio)
AURA_TTS = "Fanar-Aura-TTS-2"        # pronounce the hard words for the child to imitate

# --- Diwan: generate practice verse loaded with the child's weak sounds ---
# ⚠️ Phase 0 FINDING (2026-06-23): there is NO Diwan model on this key — absent from
# GET /v1/models, from every endpoint's accepted enum, and there is no dedicated route
# (/diwan, /poetry -> 404). FALLBACK: the Fanar chat model writes kid-appropriate,
# sound-loaded Arabic verse (free-verse rhythm, not strict classical meter). See
# smoke/04_diwan.py. Becomes a "recommendation for Fanar": expose Diwan via the API.
DIWAN = "Fanar"          # fallback verse generator (real Diwan model unavailable)
DIWAN_AVAILABLE = False  # flip to True only if a real Diwan model is ever exposed

# --- Oryx multimodal ---
ORYX_IG = "Fanar-Oryx-IG-2"    # illustrate the practice exercises
ORYX_IVU = "Fanar-Oryx-IVU-2"  # (stretch) set target text from a photographed book page

# --- Shaheen translation (POST /translations, bespoke shape) ---
SHAHEEN = "Fanar-Shaheen-MT-1"  # (stretch) English progress summary for expat parents

# --- FanarGuard / content safety: validate child-facing generated content (Phase 6) ---
# ✅ Phase 6 FINDING (2026-06-24): POST /moderations, model "Fanar-Guard-2", body
# {model, prompt, response} -> {safety, cultural_awareness} scores (~0-5, higher=safer).
# Safe kids verse scored 4.44; violent text scored 1.04. See fanar/guard.py.
GUARD = "Fanar-Guard-2"
