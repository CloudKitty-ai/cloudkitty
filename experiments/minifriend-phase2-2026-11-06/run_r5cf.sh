#!/bin/bash
# Deviations entry 30 (her word 2026-11-10 "1-3 approved", item 2): diag_r5_counterfactual.py over EVERY recorded
# act15 / both leg (mode B, the arm's own cells) and every no-head leg (mode A, a B15 shadow head). Dump-only: one
# replay per world, no world served, zero covered cost. Skips a leg whose JSON exists. act10 legs are left out (arm
# dropped by ruling (C)). ~35 min per 20x20 / 40x40 leg, longer at 100x100; WORKERS legs at once, one torch thread each.
#   experiments/minifriend-phase2-2026-11-06/run_r5cf.sh [WORKERS=8]
set -u
A="$(cd "$(dirname "$0")" && pwd)"
W="${1:-8}"
LOGS="$A/reads/r5cf/logs"; mkdir -p "$LOGS" "$A/reads/r5cf"   # ignored; never under results-raw (its raw-dir hash is stamped)
LEGS="B p2u-act15-s1 20
B p2u-act15-s1 40
B p2u-act15-s1 100
B p2u-act15-s2 20
B p2u-act15-s2 40
B p2u-act15-s4 20
B p2u-act15-s4 40
B p2r-act15 20
B p2r-act15 40
B p2u-both-s1 20
B p2u-both-s1 40
B p2u-both-s1 100
A p2u-nohead-s1 20
A p2u-nohead-s1 40
A p2u-nohead-s1 100
A p2u-nohead-s2 20
A p2u-nohead-s2 40
A p2u-nohead-s4 20
A p2u-nohead-s4 40
A p2r-nohead 20
A p2r-nohead 40"
one() {
  mode="$1"; seating="$2"; size="$3"; out="$A/reads/r5cf/$mode-$seating-$size.json"
  [ -s "$out" ] && { echo "skip $mode $seating $size"; return 0; }
  OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 VIRTUAL_ENV="$A/.venv" "$A/.venv/bin/python3" -B "$A/diag_r5_counterfactual.py" \
    "$seating" "$size" "$mode" --out "$out" --md > "$LOGS/$mode-$seating-$size.log" 2>&1
  echo "done $mode $seating $size rc=$?"
}
export -f one; export A LOGS
echo "$LEGS" | xargs -P "$W" -L 1 bash -c 'one "$@"' _
echo "== r5cf all done"
