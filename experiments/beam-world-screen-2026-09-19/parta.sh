#!/usr/bin/env bash
# Tier 2 Part A at probe 1 (PREREG-tier2 §PPO): schema_check on a held-out package trace with each
# arm's first probe dump as --policy-trace, once artifacts/ppo-fog-<slot>/probe-u49.npz exists.
# Usage: parta.sh [slot ...]   (default: all four)
set -uo pipefail
D=experiments/beam-world-screen-2026-09-19
PY=experiments/exp-006-character-gen/.venv/bin/python
TRACE=$D/results-raw/tier2/bc-corpus-pkg/flat/config-00-rollout-03
for slot in "${@:-pkg-s1 pkg-s2 floor5-s1 floor5-s2}"; do
  p=$D/artifacts/ppo-fog-$slot/probe-u49.npz
  [ -f "$p" ] || { echo "$slot: no probe-u49.npz yet"; continue; }
  $PY experiments/fog-gen1-shakeout/schema_check.py "$TRACE" --declared-constant experiments/fog-gen1-cert/declared_constant.json \
    --policy-trace "$p" --json "$D/results-raw/tier2/parta-$slot.json" > "$D/results-raw/tier2/logs/parta-$slot.log" 2>&1
  echo "$slot: $(tail -n 1 "$D/results-raw/tier2/logs/parta-$slot.log")"
done
