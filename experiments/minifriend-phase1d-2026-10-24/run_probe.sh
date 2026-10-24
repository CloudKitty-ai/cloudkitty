#!/bin/bash
# The six probe fits (DECLARATION.md §Run order step 3): NF-h24 and DR-h24,
# seeds 1–3, in parallel, THREADS torch threads each; skip-if-done.
#   caffeinate -s nohup ./run_probe.sh > results-raw/probe/run.log 2>&1 &
set -u
cd "$(dirname "$0")"
A=../minifriend-phase1-2026-10-22
THREADS=${THREADS:-3}
mkdir -p results-raw/probe
for base in NF-h24-s1 NF-h24-s2 NF-h24-s3 DR-h24-s1 DR-h24-s2 DR-h24-s3; do
  if [ -f "results-raw/probe/$base+p/done.json" ]; then echo "skip $base (done)"; continue; fi
  MINIFRIEND_ARC=$PWD VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/python3 -B grave_probe.py --base "$base" --threads "$THREADS" \
    > "results-raw/probe/fit-$base.log" 2>&1 &
done
wait
echo "all probes finished $(date -u +%FT%TZ)"
