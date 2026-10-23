#!/usr/bin/env bash
# Set L (DECLARATION.md §Data): the certified roster rot2 on the lived
# g2cmp worlds, g2leg-20.toml as served, 20,000 ticks, F-053 stop armed
# (abort streak 1000), observations saved. Runs on the ARC venv/binding
# (BINDING.md), never the Gen 2 lab venv.
#
#   run_L.sh 905001                 # the first world, checked before the rest
#   printf '%s\n' 9050{02..10} | xargs -P 5 -n 1 ./run_L.sh
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(cd "$HERE/../.." && pwd)
V="$HERE/.venv"
COLLECT="$REPO/experiments/seating-analysis-g2-2026-10-21/seating_collect_g2.py"
CONFIG="$REPO/experiments/gen2-comparator-legs-2026-10-14/g2leg-20.toml"
OUT="$HERE/results-raw/L"
mkdir -p "$OUT"
for seed in "$@"; do
  if [ -f "$OUT/streams-$seed.npz" ]; then echo "skip $seed (done)"; continue; fi
  echo "== L $seed start $(date -u +%FT%TZ)" | tee -a "$OUT/run-$seed.log"
  VIRTUAL_ENV="$V" "$V/bin/python3" -B "$COLLECT" --seating g2-rot2 --seed "$seed" \
      --ticks 20000 --abort-streak 1000 --config "$CONFIG" --save-obs \
      --out "$OUT/streams-$seed.npz" 2>&1 | tee -a "$OUT/run-$seed.log"
  echo "== L $seed end $(date -u +%FT%TZ)" | tee -a "$OUT/run-$seed.log"
done
