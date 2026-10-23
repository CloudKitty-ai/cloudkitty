#!/usr/bin/env bash
# The eighteen Phase 1b head runs (DECLARATION.md §Heads: widths 12 / 24 /
# 48 × NF / DR × seeds 1, 2, 3; the pair shares its seed; width 48 is the
# declared over-cap probe), six at a time on the Phase 1 arc venv, three
# torch threads each, trained on L + W + G + P1..P5 train worlds
# (MINIFRIEND_ARC = this directory → split.json and results-raw/ here).
#
#   caffeinate -s nohup ./run_heads.sh > results-raw/heads/run-all.log 2>&1 &
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
P1="$HERE/../minifriend-phase1-2026-10-22"
V="$P1/.venv"
export MINIFRIEND_ARC="$HERE"
mkdir -p "$HERE/results-raw/heads"
echo "== heads start $(date -u +%FT%TZ)"
for h in 12 24 48; do
  extra=""; [ "$h" = 48 ] && extra="--over-cap"
  for head in NF DR; do
    for seed in 1 2 3; do
      run="$head-h$h-s$seed"
      if [ -f "$HERE/results-raw/heads/$run/done.json" ]; then echo "skip $run (done)"; continue; fi
      VIRTUAL_ENV="$V" "$V/bin/python3" -B "$P1/train_heads.py" --head "$head" --seed "$seed" --hidden "$h" $extra --threads 3 \
          > "$HERE/results-raw/heads/train-$run.log" 2>&1 &
    done
  done
  wait
  echo "== width $h done $(date -u +%FT%TZ)"
done
echo "== heads end $(date -u +%FT%TZ)"
for h in 12 24 48; do for head in NF DR; do for seed in 1 2 3; do
  echo "$head-h$h-s$seed: $(tail -n 1 "$HERE/results-raw/heads/train-$head-h$h-s$seed.log")"
done; done; done
