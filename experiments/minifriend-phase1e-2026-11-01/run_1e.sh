#!/usr/bin/env bash
# Phase 1e §11 step 4: the three retrained heads in parallel (3 torch
# threads each), then their three probes; skip-if-done; the needy arc's
# venv (BINDING.md there: ENGINE_COMMIT 5928b7ca, torch 2.13.0).
#
#   caffeinate -s nohup ./run_1e.sh > results-raw/heads/run-all.log 2>&1 &
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
A="$HERE/../needy-set-2026-10-28"
V="$A/.venv"
THREADS=${THREADS:-3}
mkdir -p "$HERE/results-raw/heads" "$HERE/results-raw/probe"
echo "== heads start $(date -u +%FT%TZ)"
for seed in 1 2 3; do
  run="NF1e-h24-s$seed"
  if [ -f "$HERE/results-raw/heads/$run/done.json" ]; then echo "skip $run (done)"; continue; fi
  VIRTUAL_ENV="$V" "$V/bin/python3" -B "$HERE/train_1e.py" --seed "$seed" --threads "$THREADS" \
      > "$HERE/results-raw/heads/train-$run.log" 2>&1 &
done
wait
echo "== heads end $(date -u +%FT%TZ)"
for seed in 1 2 3; do
  run="NF1e-h24-s$seed"
  if [ -f "$HERE/results-raw/probe/$run+p/done.json" ]; then echo "skip $run+p (done)"; continue; fi
  VIRTUAL_ENV="$V" "$V/bin/python3" -B "$HERE/probe_1e.py" --seed "$seed" --threads "$THREADS" \
      > "$HERE/results-raw/probe/fit-$run.log" 2>&1 &
done
wait
echo "== probes end $(date -u +%FT%TZ)"
for seed in 1 2 3; do
  echo "NF1e-h24-s$seed: $(tail -n 1 "$HERE/results-raw/heads/train-NF1e-h24-s$seed.log")"
  echo "NF1e-h24-s$seed+p: $(tail -n 1 "$HERE/results-raw/probe/fit-NF1e-h24-s$seed.log")"
done
