#!/usr/bin/env bash
# The three Phase 1c SD runs (DECLARATION.md §Head: seeds 1, 2, 3) in
# parallel on the Phase 1 arc venv, three torch threads each, trained on
# the L + W + G + P1..P5 train worlds (MINIFRIEND_ARC = this directory →
# split.json and results-raw/ here).
#
#   caffeinate -s nohup ./run_sd.sh > results-raw/heads/run-all.log 2>&1 &
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
P1="$HERE/../minifriend-phase1-2026-10-22"
V="$P1/.venv"
export MINIFRIEND_ARC="$HERE"
mkdir -p "$HERE/results-raw/heads"
echo "== SD start $(date -u +%FT%TZ)"
for seed in 1 2 3; do
  run="SD-s$seed"
  if [ -f "$HERE/results-raw/heads/$run/done.json" ]; then echo "skip $run (done)"; continue; fi
  VIRTUAL_ENV="$V" "$V/bin/python3" -B "$HERE/sd_head.py" --seed "$seed" --threads 3 \
      > "$HERE/results-raw/heads/train-$run.log" 2>&1 &
done
wait
echo "== SD end $(date -u +%FT%TZ)"
for seed in 1 2 3; do echo "SD-s$seed: $(tail -n 1 "$HERE/results-raw/heads/train-SD-s$seed.log")"; done
