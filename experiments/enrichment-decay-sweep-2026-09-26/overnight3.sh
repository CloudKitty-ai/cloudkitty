#!/usr/bin/env bash
# Stage B driver (PREREG-B.md frozen 2026-09-27): eleven arms in three
# waves (4+4+3), then eleven battery legs. Launch:
#   nohup caffeinate -s bash experiments/enrichment-decay-sweep-2026-09-26/overnight3.sh \
#     > experiments/enrichment-decay-sweep-2026-09-26/results-raw/overnight3.log 2>&1 &
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=experiments/exp-006-character-gen/.venv/bin/python
S=experiments/enrichment-decay-sweep-2026-09-26
TR=$S/trainer/train_ppo_enrich2b.py
H=experiments/fog-gen1-cert/cert_harness_fog.py
CFG=experiments/beam-world-screen-2026-09-19/package.toml
LOGS=$S/results-raw/train-logs
mkdir -p "$LOGS"

WAVE1="b06-s1 b06-s2 b06-s3 b10-s1"
WAVE2="b10-s2 b10-s3 b14-s1 b14-s2"
WAVE3="b14-s3 ag10-s1 ag10-s2"
N=1
for WAVE in "$WAVE1" "$WAVE2" "$WAVE3"; do
  echo "== waveB$N $(date -u +%FT%TZ)"
  for SLOT in $WAVE; do
    OMP_NUM_THREADS=2 nice caffeinate -s $PY $TR --slot $SLOT \
      --futility-bar 0.80 --futility-probes 5 > "$LOGS/$SLOT.log" 2>&1 &
    echo "launched $SLOT pid $!"
  done
  wait
  echo "== waveB$N done $(date -u +%FT%TZ)"
  N=$((N+1))
done

echo "== batteryB $(date -u +%FT%TZ)"
export CERT_ARTS=$S/artifacts
OUT=$S/results-raw/battery
for SLOT in b06-s1 b06-s2 b06-s3 b10-s1 b10-s2 b10-s3 b14-s1 b14-s2 b14-s3 ag10-s1 ag10-s2; do
  $PY $H gen1-A eval --seeds 30 --ticks 20000 --workers 6 --config $CFG \
    --out-dir $OUT/$SLOT --abort-streak 1000 \
    --seat 0=ppo:$SLOT --seat 1=ppo:$SLOT --seat 2=ppo:$SLOT --seat 3=ppo:$SLOT --seat 4=ppo:$SLOT
done
echo "== batteryB done $(date -u +%FT%TZ)"
echo "== overnight3 done $(date -u +%FT%TZ)"
