#!/usr/bin/env bash
# World-size screen collection (PREREG.md, frozen 2026-09-24).
# Pilot first (runtime only, outputs not read for claims), then Set A
# (size x hearing at d=1) and Set B (density ladder, intact hearing).
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=experiments/exp-006-character-gen/.venv/bin/python
H=experiments/fog-gen1-cert/cert_harness_fog.py
W=experiments/world-size-screen-2026-09-24
OUT=$W/results-raw/battery

r_for() {  # median heard distance from the recorded probe, rounded to int
  $PY - "$W/results-raw/r-probe-$1.json" <<'EOF'
import json, sys
print(round(json.load(open(sys.argv[1]))["median"]))
EOF
}

echo "== pilot size100 1x20000 $(date -u +%FT%TZ)"
T0=$SECONDS
$PY $H gen1-A wsize --seeds 1 --ticks 20000 --workers 1 --config $W/size100.toml --out-dir $W/results-raw/pilot
PILOT=$((SECONDS - T0))
echo "== pilot took ${PILOT}s"
W100=6
if [ $PILOT -gt 2700 ]; then W100=3; echo "== pilot over 45 min: size100 legs at 3 workers (prereg pilot rule)"; fi

for S in 28 40 100; do
  R=$(r_for $S)
  WK=6; [ "$S" = 100 ] && WK=$W100
  D=$OUT/size$S
  echo "== setA size$S R=$R workers=$WK $(date -u +%FT%TZ)"
  $PY $H scripted wsize --seeds 30 --ticks 20000 --workers $WK --config $W/size$S.toml --out-dir $D
  $PY $H gen1-A   wsize --seeds 30 --ticks 20000 --workers $WK --config $W/size$S.toml --out-dir $D
  $PY $H gen1-A   wsize --seeds 30 --ticks 20000 --workers $WK --config $W/size$S.toml --out-dir $D --deaf dir --dir-r $R
  $PY $H gen1-A   wsize --seeds 30 --ticks 20000 --workers $WK --config $W/size$S.toml --out-dir $D --deaf rows
done

for C in size40-d2 size40-d4 size100-d2 size100-d4; do
  WK=6; case $C in size100*) WK=$W100;; esac
  D=$OUT/$C
  echo "== setB $C workers=$WK $(date -u +%FT%TZ)"
  $PY $H scripted wsize --seeds 30 --ticks 20000 --workers $WK --config $W/$C.toml --out-dir $D
  $PY $H gen1-A   wsize --seeds 30 --ticks 20000 --workers $WK --config $W/$C.toml --out-dir $D
done
echo "== all legs done $(date -u +%FT%TZ)"
