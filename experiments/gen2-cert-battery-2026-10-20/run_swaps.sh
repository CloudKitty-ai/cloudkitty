#!/usr/bin/env bash
# Swaps digest driver (SWAPS-DECLARATION.md): for each alternate named on
# the command line (s8 s9 s10), five 20x20 legs through run_legs, one per
# seat of the certified roster rot2, band g2cmp 30x20k, F-053 1000 stop
# armed, each leg gated on its own rows. Refuses an alternate whose
# policy-final.pt does not exist (a halted seed contributes no legs).
# A leg stop SystemExits run_legs and set -e stops this driver.
set -euo pipefail
cd "$(dirname "$0")"
LEGS=../gen2-comparator-legs-2026-10-14
PY=../exp-006-character-gen/.venv/bin/python
ART=../gen2-trunk-training-2026-10-18/artifacts
[ $# -ge 1 ] || { echo "usage: run_swaps.sh <net> [<net> ...]   (e.g. s8 s9)" >&2; exit 2; }
for n in "$@"; do
  [ -f "$ART/ppo-g2-trunk-$n/policy-final.pt" ] || { echo "run_swaps: trunk-$n has no policy-final.pt (not completed)" >&2; exit 3; }
done
for n in "$@"; do
  for k in 0 1 2 3 4; do
    s="g2-rot2-swap$k-$n"
    echo "== seating $s start $(date -u +%FT%TZ)"
    "$PY" "$LEGS/run_legs.py" \
      --config-20 "$LEGS/g2leg-20.toml" \
      --config-40 "$LEGS/g2leg-40.toml" \
      --config-100 "$LEGS/g2leg-100.toml" \
      --band g2cmp --seeds 30 --ticks 20000 --workers 6 --only 20 \
      --seating "$s" --out-dir "results-raw/swaps/$s"
    echo "== seating $s done $(date -u +%FT%TZ)"
  done
done
echo "== swaps done $(date -u +%FT%TZ)"
