#!/usr/bin/env bash
# Phase B driver (ROSTER-DECLARATION.md): each new network seated five
# times through run_legs at 20 and 40 (scouts-first at 40, F-053 1000
# abort per world, LEG STOP per roster). A network is seated only if
# its final records stop_reason plateau or cap; a welfare-stopped run
# is skipped and owner-routed. A stopped roster does not stop the
# others; every stop is printed for the owner, never resumed without
# her word.
set -uo pipefail
cd "$(dirname "$0")"
LEGS=../gen2-comparator-legs-2026-10-14
ARTS=../gen2-trunk-training-2026-10-18/artifacts
PY=../exp-006-character-gen/.venv/bin/python
stopped=()
for n in s5 s6 s7; do
  s="g2-$n"
  final="$ARTS/ppo-g2-trunk-$n/policy-final.pt"
  if ! "$PY" -c "import sys, torch; ck = torch.load(sys.argv[1], map_location='cpu', weights_only=True); sys.exit(0 if ck['stop_reason'] in ('plateau', 'cap') else 3)" "$final" 2>/dev/null; then
    echo "== seating $s SKIPPED $(date -u +%FT%TZ): no eligible final (missing, or a welfare stop); owner-routed"
    stopped+=("$s")
    continue
  fi
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
echo "== phase B done $(date -u +%FT%TZ); stopped or skipped: ${stopped[*]:-none}"
