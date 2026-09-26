#!/usr/bin/env bash
# Reward-shape screen batteries (PREREG §Reads): per arm, the five swap
# legs + all-arm, 30 x 20k, eval band, package world.
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=experiments/exp-006-character-gen/.venv/bin/python
H=experiments/fog-gen1-cert/cert_harness_fog.py
S=experiments/reward-shape-screen-2026-09-24
export CERT_ARTS=$S/artifacts
CFG=experiments/beam-world-screen-2026-09-19/package.toml
OUT=$S/results-raw/battery
for SLOT in hard-s1 hard-s2 cvx-s1 cvx-s2 lam-s1 lam-s2; do
  echo "== $SLOT $(date -u +%FT%TZ)"
  for I in 0 1 2 3 4; do
    $PY $H gen1-A eval --seeds 30 --ticks 20000 --workers 6 --config $CFG --out-dir $OUT/$SLOT --seat $I=ppo:$SLOT
  done
  $PY $H gen1-A eval --seeds 30 --ticks 20000 --workers 6 --config $CFG --out-dir $OUT/$SLOT \
    --seat 0=ppo:$SLOT --seat 1=ppo:$SLOT --seat 2=ppo:$SLOT --seat 3=ppo:$SLOT --seat 4=ppo:$SLOT
done
echo "== all batteries done $(date -u +%FT%TZ)"
