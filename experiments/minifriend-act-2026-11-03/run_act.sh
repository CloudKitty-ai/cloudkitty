#!/bin/bash
# Act predictor Phase 1 — twelve heads (four arms x three seeds), three at a time, skip-if-done, the needy arc's venv.
set -u
C=/Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-act-2026-11-03
A=/Users/elizabethkelly/ai/cloudkitty/experiments/needy-set-2026-10-28
export VIRTUAL_ENV=$A/.venv
PY=$A/.venv/bin/python3
mkdir -p $C/results-raw/heads
jobs_list=()
for arm in A B10 B20 B30; do
  for seed in 1 2 3; do
    if [ -f "$C/results-raw/heads/$arm-s$seed/done.json" ]; then echo "== $arm-s$seed done, skip"; continue; fi
    jobs_list+=("$arm $seed")
  done
done
printf '%s\n' "${jobs_list[@]}" | xargs -P 3 -L 1 bash -c 'arm=$0; seed=$1; echo "== start $arm-s$seed $(date -u +%H:%M:%S)"; '"$PY"' -B '"$C"'/train_act.py --arm $arm --seed $seed --threads 3 > '"$C"'/results-raw/heads/$arm-s$seed.log 2>&1; echo "== exit $? $arm-s$seed $(date -u +%H:%M:%S)"'
echo "== all done $(date -u +%H:%M:%S)"
