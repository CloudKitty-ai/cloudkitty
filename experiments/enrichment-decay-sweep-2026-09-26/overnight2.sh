#!/usr/bin/env bash
# Enrichment-decay sweep, stage A driver (PREREG frozen 2026-09-26).
# Two waves of four arms (one seed of every corner first), then the
# nine battery legs. Launch:
#   nohup caffeinate -s bash experiments/enrichment-decay-sweep-2026-09-26/overnight2.sh \
#     > experiments/enrichment-decay-sweep-2026-09-26/results-raw/overnight2.log 2>&1 &
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=experiments/exp-006-character-gen/.venv/bin/python
S=experiments/enrichment-decay-sweep-2026-09-26
TR=$S/trainer/train_ppo_enrich2.py
H=experiments/fog-gen1-cert/cert_harness_fog.py
CFG=experiments/beam-world-screen-2026-09-19/package.toml
LOGS=$S/results-raw/train-logs
mkdir -p "$LOGS"

for WAVE in 1 2; do
  echo "== wave$WAVE $(date -u +%FT%TZ)"
  for CORNER in d25-250 d25-1000 d100-250 d100-1000; do
    SLOT=$CORNER-s$WAVE
    OMP_NUM_THREADS=2 nice caffeinate -s $PY $TR --slot $SLOT \
      --futility-bar 0.80 --futility-probes 5 > "$LOGS/$SLOT.log" 2>&1 &
    echo "launched $SLOT pid $!"
  done
  wait
  echo "== wave$WAVE done $(date -u +%FT%TZ)"
done

echo "== battery $(date -u +%FT%TZ)"
export CERT_ARTS=$S/artifacts
OUT=$S/results-raw/battery
# The fresh gen1-A comparator leg with the needs block (PREREG §Instrument).
$PY $H gen1-A eval --seeds 30 --ticks 20000 --workers 6 --config $CFG \
  --out-dir $OUT/gen1-A --abort-streak 1000
for CORNER in d25-250 d25-1000 d100-250 d100-1000; do
  for SEED in 1 2; do
    SLOT=$CORNER-s$SEED
    $PY $H gen1-A eval --seeds 30 --ticks 20000 --workers 6 --config $CFG \
      --out-dir $OUT/$SLOT --abort-streak 1000 \
      --seat 0=ppo:$SLOT --seat 1=ppo:$SLOT --seat 2=ppo:$SLOT --seat 3=ppo:$SLOT --seat 4=ppo:$SLOT
  done
done
echo "== battery done $(date -u +%FT%TZ)"
echo "== overnight2 done $(date -u +%FT%TZ)"
