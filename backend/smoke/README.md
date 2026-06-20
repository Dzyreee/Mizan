# Phase 0 smoke tests

One tiny script per Fanar capability. They confirm each model works and capture the
real request/response shapes (written to `_out/*.json`) so we can fill `FANAR_NOTES.md`.

## Prerequisites
- `backend/.env` has a valid `FANAR_API_KEY`.
- **Network that can reach `api.fanar.qa`.** On some WiFi the domain is blocked at the
  network layer (returns `403` via Google's edge before auth). If you see that, switch
  to a 5G hotspot.

## Run everything
```bash
cd backend
bash smoke/run_all.sh
```

## Or run individually
```bash
cd backend
.venv/bin/python smoke/00_list_models.py   # discover real model IDs FIRST
.venv/bin/python smoke/01_chat.py
.venv/bin/python smoke/02_tool_calling.py  # native function calling vs JSON fallback
.venv/bin/python smoke/03_sadiq_islamic.py
.venv/bin/python smoke/04_aura_tts.py      # writes _out/04_tts.wav
.venv/bin/python smoke/05_aura_stt.py      # transcribes that wav (run 04 first)
.venv/bin/python smoke/06_oryx_ig.py
.venv/bin/python smoke/07_shaheen_translate.py
```

## Order matters
`00` first (model IDs feed everything). `05` reads the audio that `04` produces.

## After running
1. Open `smoke/_out/models.json` and reconcile real IDs into `app/fanar/models.py`.
2. Record endpoints + request/response shapes in `../../FANAR_NOTES.md`.
3. Note any surprises (missing models, non-OpenAI shapes, tool-calling support).
