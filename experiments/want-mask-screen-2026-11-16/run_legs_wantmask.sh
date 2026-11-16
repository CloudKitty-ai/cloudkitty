#!/usr/bin/env bash
# The want-mask screen's legs (DECLARATION.md §4, §13 step 3; her word 2026-11-16, entry 40 ruling 6): one masked
# seating at 40×40 through run_legs.py on the Phase 2 arc venv. Its 3-world scout first (an abort stops the leg and
# goes to her), the F-053 abort armed, every seat's acts recorded.
#
#   experiments/want-mask-screen-2026-11-16/run_legs_wantmask.sh <wantmask-nohead-s1|wantmask-truth-s1> [--workers 6]
#
# Output: results-raw/legs/<seating>/{scouts,legs}/size40/ under this arc (gitignored, never deleted).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
A="$ROOT/experiments/minifriend-phase2-2026-11-06"
LEGS="$ROOT/experiments/gen2-comparator-legs-2026-10-14"
W="$ROOT/experiments/want-mask-screen-2026-11-16"
SEATING="${1:?seating}"
shift
case "$SEATING" in wantmask-nohead-s1|wantmask-truth-s1) ;; *) echo "not a wantmask seating: $SEATING" >&2; exit 2 ;; esac
cd "$ROOT"
mkdir -p "$W/results-raw/legs/$SEATING"
LOG="$W/results-raw/legs/$SEATING/run.log"
echo "== $SEATING size 40 $(date -u +%Y-%m-%dT%H:%M:%SZ) HEAD $(git rev-parse --short HEAD)" >> "$LOG"
OMP_NUM_THREADS=1 VIRTUAL_ENV="$A/.venv" caffeinate -s "$A/.venv/bin/python3" -B "$LEGS/run_legs.py" \
  --config-20 "$LEGS/g2leg-20.toml" --config-40 "$LEGS/g2leg-40.toml" --config-100 "$LEGS/g2leg-100.toml" \
  --band g2cmp --seeds 30 --ticks 20000 --workers 6 --seating "$SEATING" --record --python "$A/.venv/bin/python3" \
  --out-dir "$W/results-raw/legs/$SEATING" --only 40 "$@" 2>&1 | tee -a "$LOG"
