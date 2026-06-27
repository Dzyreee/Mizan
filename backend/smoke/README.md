# Fanar smoke + discovery suite (Phase 0)

Tiny scripts that prove each Fanar capability Iqra needs and discover the unknowns.
Findings are written up in the repo-root `FANAR_NOTES.md`; raw payloads land in
`_out/` (gitignored).

**Prereqs:** VPN/5G hotspot reaching `api.fanar.qa` (it's blocked on some WiFi),
`backend/.env` with `FANAR_API_KEY`, and `backend/.venv` with deps installed.

```bash
cd backend
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
bash smoke/run_all.sh          # or run individual scripts below
```

| Script | Proves / discovers |
|---|---|
| `00_list_models.py` | `GET /models` (key: `models`, not `data`); lists visible models |
| `00b_probe.py` | invalid-model 422 enum probe; **hunts the Diwan + FanarGuard ids** |
| `01_chat_json.py` | native tool-calling unavailable -> **JSON output** works for diagnose/plan |
| `02_aura_tts.py` | Aura TTS + **re-verifies voice names** (`GET /audio/voices`) |
| `03_aura_stt.py` | Aura STT round-trip of the TTS clip |
| `04_diwan.py` | **discovers the Diwan model id** + generates a kid verse drilling a sound |
| `05_oryx_ig.py` | Oryx-IG illustration (decorative, no in-image Arabic text) |
| `10_faithfulness_gate.py` | **THE CRITICAL TEST**, does Aura preserve reading errors or normalize them? |
