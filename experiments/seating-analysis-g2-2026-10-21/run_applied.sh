#!/usr/bin/env bash
# Amendment 1 re-collection (DECLARATION.md): the scripted reference, then
# rot2, on 905001-905005 x 20,000 with the applied-action streams, five
# worlds in parallel per roster, into results-raw/applied/<roster>/ (one
# level down, so the rotation's results-raw/*/ globs never see them). The
# scripted roster (no covered minds) runs first and must pass the
# same-world check before rot2 runs; any mismatch stops the driver.
set -u
cd "$(dirname "$0")"
export VIRTUAL_ENV=../exp-006-character-gen/.venv
PY=$VIRTUAL_ENV/bin/python
for roster in scripted g2-rot2; do
  echo "== $roster start $(date -u +%FT%TZ)"
  pids=()
  for s in 905001 905002 905003 905004 905005; do
    $PY -B seating_collect_g2.py --seating $roster --seed $s --ticks 20000 \
      --out results-raw/applied/$roster/streams-$s.npz & pids+=($!)
  done
  rc=0; for p in "${pids[@]}"; do wait "$p" || rc=1; done
  [ $rc -eq 0 ] || { echo "== $roster FAILED: a collector exited nonzero; stopping"; exit 1; }
  $PY -B same_world.py $roster || { echo "== $roster STOPPED: same-world check failed; owner-routed"; exit 1; }
  echo "== $roster done $(date -u +%FT%TZ)"
done
echo "== all done"
