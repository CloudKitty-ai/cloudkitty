#!/bin/bash
# R-7 (deviations entry 33; her word 2026-11-11 "Let's run the block read"): read_blocks.py over p2u-both-s1's three
# recorded uniform legs, then the score. Dump-only, zero covered cost. Skips a leg whose JSON exists.
#   experiments/gen2-trunk-continuation-2026-11-10/run_r7.sh
set -u
K="$(cd "$(dirname "$0")" && pwd)"
A="$K/../minifriend-phase2-2026-11-06"
LOGS="$K/reads/r7/logs"; mkdir -p "$LOGS"
one() {
  size="$1"; out="$K/reads/r7/p2u-both-s1-$size.json"
  [ -s "$out" ] && { echo "skip $size"; return 0; }
  OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 VIRTUAL_ENV="$A/.venv" "$A/.venv/bin/python3" -B "$K/read_blocks.py" \
    leg "$size" --out "$out" > "$LOGS/leg-$size.log" 2>&1
  echo "done $size rc=$?"
}
export -f one; export A K LOGS
printf '20\n40\n100\n' | xargs -P 3 -L 1 bash -c 'one "$@"' _
OMP_NUM_THREADS=1 VIRTUAL_ENV="$A/.venv" "$A/.venv/bin/python3" -B "$K/read_blocks.py" score --dir "$K/reads/r7" --out "$K/reads/r7/score.json" --md
echo "== r7 all done rc=$?"
