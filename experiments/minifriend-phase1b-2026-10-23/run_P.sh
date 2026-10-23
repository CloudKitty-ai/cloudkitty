#!/usr/bin/env bash
# Set P_k (DECLARATION.md §Data, §Welfare): the certified roster rot2 on
# g2leg-20-P<k>.toml (the served 20×20 config plus spec 065 per-kitty
# initial needs: kitty k ALONE starts with every need drawn in {60, 95};
# the other four at the served default), 4,000 ticks, F-053 stop armed
# (abort streak 1000), observations saved. SCOUTS FIRST: one world per
# friend (the first seed of each block) runs alone and check_P.py must
# report no abort before the rest are launched. Runs on the Phase 1 arc
# venv/binding (../minifriend-phase1-2026-10-22/BINDING.md; same engine).
#
#   for k in 1 2 3 4 5; do ./run_P.sh $k $((1095451 + 20*(k-1))); done     # scouts
#   printf '%s\n' 10954{52..70} | xargs -P 5 -n 1 ./run_P.sh 1              # the rest of P1, etc.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(cd "$HERE/../.." && pwd)
P1="$REPO/experiments/minifriend-phase1-2026-10-22"
V="$P1/.venv"
COLLECT="$REPO/experiments/seating-analysis-g2-2026-10-21/seating_collect_g2.py"
K=$1; shift
case "$K" in 1|2|3|4|5) ;; *) echo "k must be 1..5 (the grave kitty's id)" >&2; exit 2 ;; esac
TICKS=4000
CONFIG="$HERE/g2leg-20-P$K.toml"
OUT="$HERE/results-raw/P$K"
mkdir -p "$OUT"
for seed in "$@"; do
  if [ -f "$OUT/streams-$seed.npz" ]; then echo "skip $seed (done)"; continue; fi
  echo "== P$K $seed start $(date -u +%FT%TZ)" | tee -a "$OUT/run-$seed.log"
  VIRTUAL_ENV="$V" "$V/bin/python3" -B "$COLLECT" --seating g2-rot2 --seed "$seed" \
      --ticks "$TICKS" --abort-streak 1000 --config "$CONFIG" --save-obs \
      --out "$OUT/streams-$seed.npz" 2>&1 | tee -a "$OUT/run-$seed.log"
  echo "== P$K $seed end $(date -u +%FT%TZ)" | tee -a "$OUT/run-$seed.log"
done
