#!/usr/bin/env bash
# The continuation's battery legs (DECLARATION.md §6 R-1; her word): Phase 2's run_legs_p2.sh with this arc's
# out-dir (Phase 2's results-raw is hash-stamped and takes no new file): one cont-s<k> seating through run_legs.py
# on the Phase 2 arc venv, every seat's acts recorded, the F-053 abort armed, scouts first at 40 and 100.
#   experiments/gen2-trunk-continuation-2026-11-10/run_legs_cont.sh <cont-s1|cont-s2|cont-s4> [--only 20,40] [--workers 6]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
K="$ROOT/experiments/gen2-trunk-continuation-2026-11-10"
A="$ROOT/experiments/minifriend-phase2-2026-11-06"
LEGS="$ROOT/experiments/gen2-comparator-legs-2026-10-14"
SEATING="${1:?seating}"
shift || true
cd "$ROOT"
mkdir -p "$K/results-raw/legs/$SEATING"
LOG="$K/results-raw/legs/$SEATING/run.log"
echo "== $SEATING $(date -u +%Y-%m-%dT%H:%M:%SZ) HEAD $(git rev-parse --short HEAD)" >> "$LOG"
VIRTUAL_ENV="$A/.venv" caffeinate -s "$A/.venv/bin/python3" -B "$LEGS/run_legs.py" \
  --config-20 "$LEGS/g2leg-20.toml" --config-40 "$LEGS/g2leg-40.toml" --config-100 "$LEGS/g2leg-100.toml" \
  --band g2cmp --seeds 30 --ticks 20000 --workers 6 --seating "$SEATING" --record --python "$A/.venv/bin/python3" \
  --out-dir "$K/results-raw/legs/$SEATING" "$@" 2>&1 | tee -a "$LOG"
