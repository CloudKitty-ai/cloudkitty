#!/bin/bash
# Dead-or-held probe (PREREG-C.md, frozen 2026-09-30): one wave of 4
# arms, then the l14 battery legs exactly as stage B's (same harness
# flags; o14 legs need probe_eval_o14.py and run at readout).
# Launch:
#   nohup caffeinate -s bash experiments/enrichment-decay-sweep-2026-09-26/overnight4.sh \
#     > experiments/enrichment-decay-sweep-2026-09-26/results-raw/overnight4.log 2>&1 &
# Never edit while running.
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=experiments/exp-006-character-gen/.venv/bin/python
S=experiments/enrichment-decay-sweep-2026-09-26
TR=$S/trainer/train_ppo_enrich2c.py
H=experiments/fog-gen1-cert/cert_harness_fog.py
CFG=experiments/beam-world-screen-2026-09-19/package.toml
mkdir -p $S/results-raw/train-logs
echo "== waveC1 $(date -u +%FT%TZ)"
pids=()
for SLOT in l14-s1 l14-s2 o14-s1 o14-s2; do
  OMP_NUM_THREADS=2 nice $PY $TR --slot $SLOT --futility-bar 0.80 --futility-probes 5 \
    >> $S/results-raw/train-logs/$SLOT.log 2>&1 &
  pids+=($!)
done
wait "${pids[@]}"
echo "== waveC1 done $(date -u +%FT%TZ)"
echo "== batteryC-l14 $(date -u +%FT%TZ)"
export CERT_ARTS=$S/artifacts
OUT=$S/results-raw/battery
for SLOT in l14-s1 l14-s2; do
  $PY $H gen1-A eval --seeds 30 --ticks 20000 --workers 6 --config $CFG \
    --out-dir $OUT/$SLOT --abort-streak 1000 \
    --seat 0=ppo:$SLOT --seat 1=ppo:$SLOT --seat 2=ppo:$SLOT --seat 3=ppo:$SLOT --seat 4=ppo:$SLOT
done
echo "== batteryC-l14 done $(date -u +%FT%TZ)"
echo "== overnight4 done $(date -u +%FT%TZ)"
