#!/usr/bin/env bash
# Enrichment-bonus screen: the overnight driver (PREREG frozen
# 2026-09-26). Four arms in parallel (tier-5 pattern: 2 threads each,
# nice), then the five battery legs. Launch:
#   nohup caffeinate -s bash experiments/enrichment-bonus-screen-2026-09-26/overnight.sh \
#     > experiments/enrichment-bonus-screen-2026-09-26/results-raw/overnight.log 2>&1 &
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=experiments/exp-006-character-gen/.venv/bin/python
S=experiments/enrichment-bonus-screen-2026-09-26
TR=$S/trainer/train_ppo_enrich.py
H=experiments/fog-gen1-cert/cert_harness_fog.py
CFG=experiments/beam-world-screen-2026-09-19/package.toml
LOGS=$S/results-raw/train-logs
mkdir -p "$LOGS"

echo "== arms $(date -u +%FT%TZ)"
for SLOT in bonus-s1 bonus-s2 bonus-lo-s1 bonus-lo-s2; do
  OMP_NUM_THREADS=2 nice caffeinate -s $PY $TR --slot $SLOT \
    --futility-bar 0.80 --futility-probes 5 > "$LOGS/$SLOT.log" 2>&1 &
  echo "launched $SLOT pid $!"
done
wait
echo "== arms done $(date -u +%FT%TZ)"

echo "== battery $(date -u +%FT%TZ)"
export CERT_ARTS=$S/artifacts
OUT=$S/results-raw/battery
# The fresh gen1-A comparator leg (play baselines; PREREG §Instrument).
$PY $H gen1-A eval --seeds 30 --ticks 20000 --workers 6 --config $CFG \
  --out-dir $OUT/gen1-A --abort-streak 1000
for SLOT in bonus-s1 bonus-s2 bonus-lo-s1 bonus-lo-s2; do
  $PY $H gen1-A eval --seeds 30 --ticks 20000 --workers 6 --config $CFG \
    --out-dir $OUT/$SLOT --abort-streak 1000 \
    --seat 0=ppo:$SLOT --seat 1=ppo:$SLOT --seat 2=ppo:$SLOT --seat 3=ppo:$SLOT --seat 4=ppo:$SLOT
done
echo "== battery done $(date -u +%FT%TZ)"
echo "== overnight done $(date -u +%FT%TZ)"
