#!/bin/bash
# Act-head ladder — six heads (B5, B15 x seeds 1-3), three at a time, skip-if-done, into the act arc's heads store; then the four reads.
set -u
C=/Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-act-ladder-2026-11-04
ACT=/Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-act-2026-11-03
A=/Users/elizabethkelly/ai/cloudkitty/experiments/needy-set-2026-10-28
export VIRTUAL_ENV=$A/.venv
PY=$A/.venv/bin/python3
mkdir -p $C/reads
jobs_list=()
for arm in B5 B15; do
  for seed in 1 2 3; do
    if [ -f "$ACT/results-raw/heads/$arm-s$seed/done.json" ]; then echo "== $arm-s$seed done, skip"; continue; fi
    jobs_list+=("$arm $seed")
  done
done
if [ ${#jobs_list[@]} -gt 0 ]; then
  printf '%s\n' "${jobs_list[@]}" | xargs -P 3 -L 1 bash -c 'arm=$0; seed=$1; echo "== start $arm-s$seed $(date -u +%H:%M:%S)"; '"$PY"' -B '"$C"'/ladder_act.py train --arm $arm --seed $seed --threads 3 > '"$ACT"'/results-raw/heads/$arm-s$seed.log 2>&1; echo "== exit $? $arm-s$seed $(date -u +%H:%M:%S)"'
fi
echo "== training done $(date -u +%H:%M:%S)"
for cmd in accuracy fit reliability curve; do
  out="$cmd"; [ "$cmd" = fit ] && out=temperature
  "$PY" -B "$C/ladder_act.py" "$cmd" --out "$C/reads/$out.json" --md --quiet > "$C/reads/$out.md" 2> "$C/reads/$out.err" || { echo "== $cmd FAILED"; exit 1; }
  echo "== $cmd done $(date -u +%H:%M:%S)"
done
echo "== all done $(date -u +%H:%M:%S)"
