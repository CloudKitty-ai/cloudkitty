#!/usr/bin/env bash
# Fog-era deafening ablation collection (prereg.md this directory).
# Four sequential legs, same band (deaf = 900101), same out-dir.
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=experiments/exp-006-character-gen/.venv/bin/python
H=experiments/fog-gen1-cert/cert_harness_fog.py
OUT=experiments/fog-deafening-2026-09-23/results-raw/battery
for ARM in "" want here all; do
  echo "== arm ${ARM:-intact} $(date -u +%FT%TZ)"
  if [ -z "$ARM" ]; then
    $PY $H gen1-A deaf --seeds 30 --ticks 20000 --workers 6 --out-dir "$OUT"
  else
    $PY $H gen1-A deaf --seeds 30 --ticks 20000 --workers 6 --out-dir "$OUT" --deaf "$ARM"
  fi
done
echo "== all arms done $(date -u +%FT%TZ)"
