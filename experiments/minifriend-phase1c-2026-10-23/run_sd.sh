#!/usr/bin/env bash
# The Phase 1c SD runs (DECLARATION.md §Head + §Addendum: widths 8 / 16 /
# 32 × seeds 1, 2, 3) in parallel on the Phase 1 arc venv, trained on the
# L + W + G + P1..P5 train worlds (MINIFRIEND_ARC = this directory →
# split.json and results-raw/ here). Width 32 is the declared over-cap
# probe (--over-cap). A run with done.json is skipped; a run whose
# trainer is alive is skipped (the width-16 runs were launched before
# the addendum, without --hidden, three threads each).
#
#   WIDTHS="8 32" THREADS=2 caffeinate -s nohup ./run_sd.sh > results-raw/heads/run-sizes.log 2>&1 &
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
P1="$HERE/../minifriend-phase1-2026-10-22"
V="$P1/.venv"
export MINIFRIEND_ARC="$HERE"
WIDTHS=${WIDTHS:-"8 16 32"}
THREADS=${THREADS:-3}
mkdir -p "$HERE/results-raw/heads"

alive() {  # $1 seed, $2 width: a live trainer for that run (per process; the pre-addendum width-16 form carries no --hidden)
  local pid a
  for pid in $(pgrep -f "sd_head.py --seed $1 "); do
    a=$(ps -o args= -p "$pid")
    case "$2" in
      16) grep -q -- "--hidden 16 " <<< "$a" && return 0; grep -q -- "--hidden" <<< "$a" || return 0 ;;
      *)  grep -q -- "--hidden $2 " <<< "$a" && return 0 ;;
    esac
  done
  return 1
}

runs=()
echo "== SD start $(date -u +%FT%TZ) widths [$WIDTHS] threads $THREADS"
for h in $WIDTHS; do
  extra=""; [ "$h" = 32 ] && extra="--over-cap"
  for seed in 1 2 3; do
    if [ "$h" = 16 ]; then run="SD-s$seed"; else run="SD-h$h-s$seed"; fi
    if [ -f "$HERE/results-raw/heads/$run/done.json" ]; then echo "skip $run (done)"; continue; fi
    if alive "$seed" "$h"; then echo "skip $run (running)"; continue; fi
    runs+=("$run")
    VIRTUAL_ENV="$V" "$V/bin/python3" -B "$HERE/sd_head.py" --seed "$seed" --hidden "$h" $extra --threads "$THREADS" \
        > "$HERE/results-raw/heads/train-$run.log" 2>&1 &
  done
done
wait
echo "== SD end $(date -u +%FT%TZ)"
for run in "${runs[@]}"; do echo "$run: $(tail -n 1 "$HERE/results-raw/heads/train-$run.log")"; done
