#!/usr/bin/env bash
# Mixed-roster test driver (MIXED-DECLARATION.md): the three
# seat-balanced rosters through run_legs at 20 and 40 (scouts-first at
# 40, F-053 1000 abort per world, LEG STOP per roster). A stopped
# roster does not stop the other two; every stop is printed for the
# owner and never resumed without her word.
set -uo pipefail
cd "$(dirname "$0")"
LEGS=../gen2-comparator-legs-2026-10-14
PY=../exp-006-character-gen/.venv/bin/python
stopped=()
for s in g2-mix1 g2-mix2 g2-mix3; do
  echo "== seating $s start $(date -u +%FT%TZ)"
  if "$PY" "$LEGS/run_legs.py" \
      --config-20 "$LEGS/g2leg-20.toml" \
      --config-40 "$LEGS/g2leg-40.toml" \
      --config-100 "$LEGS/g2leg-100.toml" \
      --only 20,40 --band g2cmp --seeds 30 --ticks 20000 --workers 6 \
      --seating "$s" --out-dir "results-raw/$s"; then
    echo "== seating $s done $(date -u +%FT%TZ)"
  else
    echo "== seating $s STOPPED rc=$? $(date -u +%FT%TZ): remaining legs of this roster not run; owner-routed"
    stopped+=("$s")
  fi
done
echo "== mixed test done $(date -u +%FT%TZ); stopped: ${stopped[*]:-none}"
