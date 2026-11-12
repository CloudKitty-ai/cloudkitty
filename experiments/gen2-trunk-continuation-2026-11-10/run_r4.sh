#!/bin/bash
# R-4 (DECLARATION §6; her word 2026-11-11 "3) Yes"): read_cells_by_size.py over Phase 2's ten recorded head-arm
# uniform legs, the no-head fence on two worlds of each no-head uniform leg, then the score. Dump-only, zero covered
# cost. Skips a leg whose JSON exists. ~35-55 min per leg; WORKERS legs at once, one torch thread each.
#   experiments/gen2-trunk-continuation-2026-11-10/run_r4.sh [WORKERS=8]
set -u
K="$(cd "$(dirname "$0")" && pwd)"
A="$K/../minifriend-phase2-2026-11-06"
W="${1:-8}"
LOGS="$K/results-raw/r4-logs"; mkdir -p "$LOGS" "$K/reads/r4"
LEGS="leg p2u-act15-s1 20
leg p2u-act15-s1 40
leg p2u-act15-s1 100
leg p2u-act15-s2 20
leg p2u-act15-s2 40
leg p2u-act15-s4 20
leg p2u-act15-s4 40
leg p2u-both-s1 20
leg p2u-both-s1 40
leg p2u-both-s1 100
fence p2u-nohead-s1 20
fence p2u-nohead-s1 40
fence p2u-nohead-s1 100
fence p2u-nohead-s2 20
fence p2u-nohead-s2 40
fence p2u-nohead-s4 20
fence p2u-nohead-s4 40"
one() {
  kind="$1"; seating="$2"; size="$3"
  if [ "$kind" = fence ]; then out="$K/reads/r4/fence-$seating-$size.json"; extra="--seeds 905001,905002"; else out="$K/reads/r4/$seating-$size.json"; extra=""; fi
  [ -s "$out" ] && { echo "skip $kind $seating $size"; return 0; }
  OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 VIRTUAL_ENV="$A/.venv" "$A/.venv/bin/python3" -B "$K/read_cells_by_size.py" \
    leg "$seating" "$size" $extra --out "$out" > "$LOGS/$kind-$seating-$size.log" 2>&1
  echo "done $kind $seating $size rc=$?"
}
export -f one; export A K LOGS
echo "$LEGS" | xargs -P "$W" -L 1 bash -c 'one "$@"' _
OMP_NUM_THREADS=1 VIRTUAL_ENV="$A/.venv" "$A/.venv/bin/python3" -B "$K/read_cells_by_size.py" score --dir "$K/reads/r4" --out "$K/reads/r4/score.json" --md
echo "== r4 all done rc=$?"
