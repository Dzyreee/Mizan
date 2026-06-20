#!/usr/bin/env bash
# Run the full Phase 0 discovery + smoke suite in order.
# Must be run on a network that can reach api.fanar.qa (e.g. 5G hotspot).
# Usage: bash smoke/run_all.sh   (from the backend/ directory)
set -u
PY="$(dirname "$0")/../.venv/bin/python"
cd "$(dirname "$0")/.." || exit 1

scripts=(
  smoke/00_list_models.py
  smoke/01_chat.py
  smoke/02_tool_calling.py
  smoke/03_sadiq_islamic.py
  smoke/04_aura_tts.py
  smoke/05_aura_stt.py
  smoke/06_oryx_ig.py
  smoke/07_shaheen_translate.py
)

for s in "${scripts[@]}"; do
  echo ""
  echo "════════════════════════════════════════════════════════"
  "$PY" "$s"
  echo "  (exit=$?)"
done
echo ""
echo "Done. Raw payloads are in smoke/_out/ — use them to fill FANAR_NOTES.md."
