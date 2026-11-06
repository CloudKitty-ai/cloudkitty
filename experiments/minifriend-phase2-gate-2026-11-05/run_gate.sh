#!/usr/bin/env bash
# The Phase 2 entry gate's four reads in order (DECLARATION.md §11). Zero collection: every read walks recorded worlds; the
# act read replays them on the pinned binding. Run from anywhere; absolute paths.
set -u
A=/Users/elizabethkelly/ai/cloudkitty/experiments/needy-set-2026-10-28
C=/Users/elizabethkelly/ai/cloudkitty/experiments/minifriend-phase2-gate-2026-11-05
PY="env VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B"
mkdir -p "$C/reads"
for cmd in sample act needs verdict; do
  echo "== $cmd start $(date -u +%H:%M:%S)"
  $PY "$C/gate_screen.py" "$cmd" --out "$C/reads/$cmd.json" --md > "$C/reads/$cmd.md" 2> "$C/reads/$cmd.err"
  echo "== $cmd exit $? $(date -u +%H:%M:%S)"
done
echo "== all done $(date -u +%H:%M:%S)"
