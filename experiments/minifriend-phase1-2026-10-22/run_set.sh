#!/usr/bin/env bash
# Sets W and G (DECLARATION.md §Data, §Welfare): the certified roster
# rot2 on g2leg-20-<SET>.toml (the served 20×20 config plus spec 065
# [initial_needs]: W every need drawn in {0, 90}, 6,000 ticks; G {60, 95},
# 4,000 ticks), F-053 stop armed (abort streak 1000), observations
# saved. SCOUTS FIRST: the band's first three worlds run alone and
# check_set.py must report no abort before the rest are launched. Runs
# on the ARC venv/binding (BINDING.md).
#
#   run_set.sh W 1095401 1095402 1095403                       # scouts
#   printf '%s\n' 10954{04..25} | xargs -P 5 -n 1 ./run_set.sh W   # the rest
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(cd "$HERE/../.." && pwd)
V="$HERE/.venv"
COLLECT="$REPO/experiments/seating-analysis-g2-2026-10-21/seating_collect_g2.py"
SET=$1; shift
case "$SET" in
  W) TICKS=6000 ;;
  G) TICKS=4000 ;;
  *) echo "set must be W or G" >&2; exit 2 ;;
esac
CONFIG="$HERE/g2leg-20-$SET.toml"
OUT="$HERE/results-raw/$SET"
mkdir -p "$OUT"
for seed in "$@"; do
  if [ -f "$OUT/streams-$seed.npz" ]; then echo "skip $seed (done)"; continue; fi
  echo "== $SET $seed start $(date -u +%FT%TZ)" | tee -a "$OUT/run-$seed.log"
  VIRTUAL_ENV="$V" "$V/bin/python3" -B "$COLLECT" --seating g2-rot2 --seed "$seed" \
      --ticks "$TICKS" --abort-streak 1000 --config "$CONFIG" --save-obs \
      --out "$OUT/streams-$seed.npz" 2>&1 | tee -a "$OUT/run-$seed.log"
  echo "== $SET $seed end $(date -u +%FT%TZ)" | tee -a "$OUT/run-$seed.log"
done
