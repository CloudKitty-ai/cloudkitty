#!/usr/bin/env bash
# The after-the-fact reads on the recorded legs (DECLARATION.md §6 R-1 … R-5; §15 Regeneration's Read fence is
# built from these lines). Each reader writes --out JSON (+ .md where it summarises); nothing here collects.
#
#   experiments/minifriend-phase2-2026-11-06/run_reads.sh [sizes=20,40,100]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
A="$ROOT/experiments/minifriend-phase2-2026-11-06"
PY="$A/.venv/bin/python3"
SIZES="${1:-20,40,100}"
cd "$ROOT"
export VIRTUAL_ENV="$A/.venv"
mkdir -p "$A/reads/r2" "$A/reads/r4" "$A/reads/r5"
# R-1: the welfare rule's read (edge statistics, paired deltas, the §8.1 clause, P38–P40)
# P2_ARMS (default all three) narrows the arms read; P2_SKIP (an egrep pattern on seating names) skips legs — set by
# deviations entry 29 (C): act10 dropped, so P2_ARMS=act15,nohead P2_SKIP=act10 for the Phase 2 result.
"$PY" -B "$A/read_r1.py" --out "$A/reads/r1.json" --md --sizes "$SIZES" --arms "${P2_ARMS:-act15,act10,nohead}"
# R-2 / R-3 records per recorded leg (one replay per world; the trunk uniform legs must be re-recorded by
# run_legs_p2.sh g2-s<k> for the arm-vs-trunk episode reads at each size)
for size in ${SIZES//,/ }; do
  for d in "$A"/results-raw/legs/*/legs/size$size; do
    [ -d "$d/acts" ] || continue
    seating="$(basename "$(dirname "$(dirname "$d")")")"
    if [ -n "${P2_SKIP:-}" ] && echo "$seating" | grep -qE "$P2_SKIP"; then echo "skip $seating (P2_SKIP=$P2_SKIP)"; continue; fi
    [ -f "$A/reads/r2/episodes-$seating-$size.json" ] || "$PY" -B "$A/read_r2.py" episodes --seating "$seating" --size "$size"
    case "$seating" in
      p2u-*|p2r-*)
        [ -f "$A/reads/r4/$seating-$size.json" ] || "$PY" -B "$A/read_r4.py" leg --seating "$seating" --size "$size"
        [ -f "$A/reads/r5/$seating-$size.json" ] || "$PY" -B "$A/read_r5.py" leg --seating "$seating" --size "$size"
        ;;
    esac
  done
done
"$PY" -B "$A/read_r2.py" score --out "$A/reads/r2.json" --md
"$PY" -B "$A/read_r4.py" score --out "$A/reads/r4.json" --md
"$PY" -B "$A/read_r5.py" score --out "$A/reads/r5.json" --md
# Entry 27's reading grammar on each recorded canary leg (both-s<k>): the needs head on the leg (R-4 extended, one
# replay per world), then the one-seed score (R-1a vs act15 / trunk, R-2a / R-2b, the needs trajectory, P45–P47)
for d in "$A"/results-raw/legs/p2u-both-s*/legs/size20; do
  [ -d "$d/acts" ] || continue
  seating="$(basename "$(dirname "$(dirname "$d")")")"
  k="${seating##*-s}"
  mkdir -p "$A/reads/canary"
  [ -f "$A/reads/canary/needs-leg-$seating-20.json" ] || "$PY" -B "$A/read_canary.py" needs-leg --seating "$seating" --size 20
  "$PY" -B "$A/read_canary.py" score --seed "$k" --size 20 --out "$A/reads/canary-s$k.json" --md
done
