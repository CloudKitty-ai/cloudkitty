#!/usr/bin/env bash
# The Phase 2 battery legs (DECLARATION.md §6 R-1, §13 step 5; her word): one seating through run_legs.py on the
# arc venv, every seat's acts recorded for the replay reads, the F-053 abort armed, scouts first at 40 and 100.
#
#   experiments/minifriend-phase2-2026-11-06/run_legs_p2.sh <seating> [--only 20,40] [--workers 6]
#
# seatings: p2u-<arm>-s<k> (uniform per seed), p2r-<arm> (roster-shaped), g2-rot2-perm1 / g2-rot2-perm2 (the
# roster bar's two trunk legs, step 2b, 20×20 only). Output: results-raw/legs/<seating>/{scouts,legs}/size<N>/.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
A="$ROOT/experiments/minifriend-phase2-2026-11-06"
LEGS="$ROOT/experiments/gen2-comparator-legs-2026-10-14"
SEATING="${1:?seating}"
shift || true
cd "$ROOT"
mkdir -p "$A/results-raw/legs/$SEATING"
LOG="$A/results-raw/legs/$SEATING/run.log"
echo "== $SEATING $(date -u +%Y-%m-%dT%H:%M:%SZ) HEAD $(git rev-parse --short HEAD)" >> "$LOG"
VIRTUAL_ENV="$A/.venv" caffeinate -s "$A/.venv/bin/python3" -B "$LEGS/run_legs.py" \
  --config-20 "$LEGS/g2leg-20.toml" --config-40 "$LEGS/g2leg-40.toml" --config-100 "$LEGS/g2leg-100.toml" \
  --band g2cmp --seeds 30 --ticks 20000 --workers 6 --seating "$SEATING" --record --python "$A/.venv/bin/python3" \
  --out-dir "$A/results-raw/legs/$SEATING" "$@" 2>&1 | tee -a "$LOG"
