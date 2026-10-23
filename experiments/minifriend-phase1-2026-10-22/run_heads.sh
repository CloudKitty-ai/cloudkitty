#!/usr/bin/env bash
# The six Phase 1 head runs (DECLARATION.md §Two heads: NF and DR × seeds
# 1, 2, 3; the pair shares its seed), in parallel on the arc venv, three
# torch threads each. Logs beside each run's artifacts.
#
#   caffeinate -s nohup ./run_heads.sh > results-raw/heads/run-all.log 2>&1 &
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
V="$HERE/.venv"
mkdir -p "$HERE/results-raw/heads"
echo "== heads start $(date -u +%FT%TZ)"
for head in NF DR; do
  for seed in 1 2 3; do
    if [ -f "$HERE/results-raw/heads/$head-s$seed/done.json" ]; then echo "skip $head-s$seed (done)"; continue; fi
    VIRTUAL_ENV="$V" "$V/bin/python3" -B "$HERE/train_heads.py" --head "$head" --seed "$seed" --threads 3 \
        > "$HERE/results-raw/heads/train-$head-s$seed.log" 2>&1 &
  done
done
wait
echo "== heads end $(date -u +%FT%TZ)"
for head in NF DR; do for seed in 1 2 3; do
  echo "$head-s$seed: $(tail -n 1 "$HERE/results-raw/heads/train-$head-s$seed.log")"
done; done
