#!/usr/bin/env bash
# The true-needs arm's battery legs (DECLARATION.md §6 R-1 and size scouts, §13 step 4; her word "Yes as drafted."):
# Phase 2's run_legs_p2.sh with this arc's out-dir (Phase 2's results-raw is hash-stamped). One seating through
# run_legs.py on the Phase 2 arc venv, every seat's acts recorded, the F-053 abort armed, a 3-world scout before
# the 40×40 leg.
#
#   run_legs_truth.sh <p2u-truth-s1-u3906|p2u-truth-s1>            leg 20, scout 40, leg 40
#   run_legs_truth.sh <seating> scout100                            the 3-world 100×100 scout ALONE (§6: no 100×100
#                                                                   leg is declared, so run_legs.py's scout-then-leg
#                                                                   is not used; the command is its scout stage's)
# Output: results-raw/legs/<seating>/{scouts,legs}/size<N>/ under this arc (gitignored, never deleted).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
A="$ROOT/experiments/minifriend-phase2-2026-11-06"
LEGS="$ROOT/experiments/gen2-comparator-legs-2026-10-14"
T="$ROOT/experiments/minifriend-true-needs-arm-2026-11-14"
SEATING="${1:?seating}"
MODE="${2:-legs}"
case "$SEATING" in p2u-truth-s1-u3906|p2u-truth-s1) ;; *) echo "not a true-needs seating: $SEATING" >&2; exit 2 ;; esac
cd "$ROOT"
OUT="$T/results-raw/legs/$SEATING"
mkdir -p "$OUT"
LOG="$OUT/run.log"
echo "== $SEATING $MODE $(date -u +%Y-%m-%dT%H:%M:%SZ) HEAD $(git rev-parse --short HEAD)" >> "$LOG"
export OMP_NUM_THREADS=1 VIRTUAL_ENV="$A/.venv"
if [ "$MODE" = scout100 ]; then
  caffeinate -s "$A/.venv/bin/python3" -B "$ROOT/experiments/fog-gen1-cert/cert_harness_fog.py" "$SEATING" g2cmp \
    --seeds 3 --ticks 20000 --workers 3 --config "$LEGS/g2leg-100.toml" --out-dir "$OUT/scouts/size100" \
    --abort-streak 1000 --record-dir "$OUT/scouts/size100/acts" 2>&1 | tee -a "$LOG"
elif [ "$MODE" = legs ]; then
  caffeinate -s "$A/.venv/bin/python3" -B "$LEGS/run_legs.py" \
    --config-20 "$LEGS/g2leg-20.toml" --config-40 "$LEGS/g2leg-40.toml" --config-100 "$LEGS/g2leg-100.toml" \
    --band g2cmp --seeds 30 --ticks 20000 --workers 6 --seating "$SEATING" --record --python "$A/.venv/bin/python3" \
    --out-dir "$OUT" --only 20,40 2>&1 | tee -a "$LOG"
else
  echo "mode is legs or scout100, not $MODE" >&2; exit 2
fi
