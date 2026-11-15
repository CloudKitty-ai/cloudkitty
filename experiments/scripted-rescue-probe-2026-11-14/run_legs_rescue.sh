#!/usr/bin/env bash
# The scripted-rescue probe's legs (DECLARATION.md §4, §13 step 3; her word 2026-11-15, call 5): one overlay seating
# at one size through run_legs.py on the Phase 2 arc venv. Scouts first (3 worlds; an abort stops that leg and goes to
# her), the F-053 abort armed, every seat's acts recorded with the overlay's own arrays (rescue.Overlay.arrays).
#
#   experiments/scripted-rescue-probe-2026-11-14/run_legs_rescue.sh <rescue-T|rescue-P|rescue-O> <40|100> [--workers 6]
#
# Output: results-raw/legs/<seating>/{scouts,legs}/size<N>/ under this arc (gitignored, never deleted).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
A="$ROOT/experiments/minifriend-phase2-2026-11-06"
LEGS="$ROOT/experiments/gen2-comparator-legs-2026-10-14"
P="$ROOT/experiments/scripted-rescue-probe-2026-11-14"
SEATING="${1:?seating}"
SIZE="${2:?size}"
shift 2
case "$SEATING" in rescue-T|rescue-P|rescue-O) ;; *) echo "not an overlay seating: $SEATING" >&2; exit 2 ;; esac
case "$SIZE" in 40|100) ;; *) echo "the probe's sizes are 40 and 100: $SIZE" >&2; exit 2 ;; esac
cd "$ROOT"
mkdir -p "$P/results-raw/legs/$SEATING"
LOG="$P/results-raw/legs/$SEATING/run.log"
echo "== $SEATING size $SIZE $(date -u +%Y-%m-%dT%H:%M:%SZ) HEAD $(git rev-parse --short HEAD)" >> "$LOG"
OMP_NUM_THREADS=1 VIRTUAL_ENV="$A/.venv" caffeinate -s "$A/.venv/bin/python3" -B "$LEGS/run_legs.py" \
  --config-20 "$LEGS/g2leg-20.toml" --config-40 "$LEGS/g2leg-40.toml" --config-100 "$LEGS/g2leg-100.toml" \
  --band g2cmp --seeds 30 --ticks 20000 --workers 6 --seating "$SEATING" --record --python "$A/.venv/bin/python3" \
  --out-dir "$P/results-raw/legs/$SEATING" --only "$SIZE" "$@" 2>&1 | tee -a "$LOG"
