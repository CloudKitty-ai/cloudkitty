#!/usr/bin/env bash
# Cross-world cost reads (DECLARATION.md, 2026-09-26): nine battery
# legs, sequential, gentle beside the stage-A training waves.
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=experiments/exp-006-character-gen/.venv/bin/python
H=experiments/fog-gen1-cert/cert_harness_fog.py
BEAM=experiments/beam-world-screen-2026-09-19
RS=experiments/reward-shape-screen-2026-09-24
OUT=experiments/cross-world-cost-reads-2026-09-26/results-raw

echo "== sg15 on floor-0 $(date -u +%FT%TZ)"
for S in sg15-s1 sg15-s2; do
  CERT_ARTS=$BEAM/artifacts $PY $H gen1-A eval --seeds 30 --ticks 20000 --workers 4 \
    --config $BEAM/package.toml --out-dir $OUT/$S-on-floor0 --abort-streak 1000 \
    --seat 0=ppo:$S --seat 1=ppo:$S --seat 2=ppo:$S --seat 3=ppo:$S --seat 4=ppo:$S
done

echo "== gen1-A on floor-15 $(date -u +%FT%TZ)"
CERT_ARTS=$BEAM/artifacts $PY $H gen1-A eval --seeds 30 --ticks 20000 --workers 4 \
  --config $BEAM/shallow-15.toml --out-dir $OUT/gen1-A-on-floor15 --abort-streak 1000

echo "== shaped arms on floor-15 $(date -u +%FT%TZ)"
for S in hard-s1 hard-s2 cvx-s1 cvx-s2 lam-s1 lam-s2; do
  CERT_ARTS=$RS/artifacts $PY $H gen1-A eval --seeds 30 --ticks 20000 --workers 4 \
    --config $BEAM/shallow-15.toml --out-dir $OUT/$S-on-floor15 --abort-streak 1000 \
    --seat 0=ppo:$S --seat 1=ppo:$S --seat 2=ppo:$S --seat 3=ppo:$S --seat 4=ppo:$S
done
echo "== cross-reads done $(date -u +%FT%TZ)"
