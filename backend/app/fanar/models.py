"""Fanar model IDs — single source of truth. ✅ CONFIRMED via live discovery (Phase 0).

Discovered from GET /v1/models + invalid-model 422 enum probes on 2026-06-20.
Note: GET /v1/models lists 11 models, but the chat endpoint also accepts 3 extra
routing ids not in that list: Fanar-Agentic, Islamic-RAG, Fanar-Sadiq-Agentic.
"""
from __future__ import annotations

# --- Chat / planner ---
CHAT = "Fanar"                  # default chat; RAG-steered, does NOT emit tool_calls
CHAT_AGENTIC = "Fanar-Agentic"  # agentic variant — use for native tool/function calling
CHAT_SMALL = "Fanar-S-1-7B"     # small/fast
CHAT_C1 = "Fanar-C-1-8.7B"      # base chat 8.7B
CHAT_C2 = "Fanar-C-2-27B"       # base chat 27B (largest)

# --- Islamic rulings (Fanar-Sadiq family) ---
ISLAMIC = "Islamic-RAG"             # ✅ returns inline <quran_start>..<quran_end> citations
SADIQ = "Fanar-Sadiq"               # alt Islamic model
SADIQ_AGENTIC = "Fanar-Sadiq-Agentic"  # agentic Sadiq (built-in inheritance/zakat tool?)

# --- Aura speech ---
AURA_STT = "Fanar-Aura-STT-1"        # ✅ speech-to-text
AURA_STT_LF = "Fanar-Aura-STT-LF-1"  # long-form STT (hours-long audio)
AURA_TTS = "Fanar-Aura-TTS-2"        # ✅ text-to-speech (was wrongly TTS-1-S)
SADIQ_TTS = "Fanar-Sadiq-TTS-1"      # Sadiq-voiced TTS (alt)

# --- Oryx multimodal ---
ORYX_IG = "Fanar-Oryx-IG-2"          # ✅ image generation (was wrongly IG-1)
ORYX_IVU = "Fanar-Oryx-IVU-2"        # image/video understanding (via chat endpoint)

# --- Shaheen translation (POST /translations, NOT /chat) ---
SHAHEEN = "Fanar-Shaheen-MT-1"       # ✅ output in response "text" field
