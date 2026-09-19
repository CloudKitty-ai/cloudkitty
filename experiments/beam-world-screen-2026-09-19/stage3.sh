#!/usr/bin/env bash
# Tier 2, stage 3: the reads (PREREG-tier2 §Reads). Per arm on its own world: five swap legs
# (the arm into each gen1-A seat) and the all-arm roster, 30 seeds x 20k on the shared eval
# band, served clock, the harness's beam block. Skip-if-done. Then tier2_read.py.
# Launch: caffeinate -s nohup bash experiments/beam-world-screen-2026-09-19/stage3.sh > .../results-raw/tier2/stage3.log 2>&1 &
set -uo pipefail
D=experiments/beam-world-screen-2026-09-19
R=$D/results-raw/tier2; A=$D/artifacts
PY=experiments/exp-006-character-gen/.venv/bin/python
H=experiments/fog-gen1-cert/cert_harness_fog.py
echo "== stage3 start $(date -u +%FT%TZ) head $(git rev-parse --short HEAD)"
for slot in pkg-s1 pkg-s2 floor5-s1 floor5-s2; do
  [ -f "$A/ppo-fog-$slot/policy-final.pt" ] || { echo "no final artifact for $slot, skipped"; continue; }
  case $slot in pkg-*) world=$D/package.toml;; floor5-*) world=$D/floor5.toml;; esac
  out=$R/battery/$slot; mkdir -p "$out"
  for k in 0 1 2 3 4; do
    f="$out/gen1-A_s$k-$slot-c0-eval-30x20000.jsonl"
    if [ -f "$f" ] && [ "$(wc -l < "$f")" -ge 31 ]; then echo "skip $slot seat $k"; continue; fi
    echo "== $slot into seat $k $(date -u +%FT%TZ)"
    CERT_ARTS=$A $PY $H gen1-A eval --config "$world" --workers 6 --seat "$k=ppo:$slot" --out-dir "$out" > "$out/seat$k.log" 2>&1; tail -n 1 "$out/seat$k.log"
  done
  f="$out/gen1-A_s0-$slot"_s1-"$slot"_s2-"$slot"_s3-"$slot"_s4-"$slot-c0-eval-30x20000.jsonl"
  if [ -f "$f" ] && [ "$(wc -l < "$f")" -ge 31 ]; then echo "skip $slot all-arm"; else
    echo "== $slot all-arm $(date -u +%FT%TZ)"
    CERT_ARTS=$A $PY $H gen1-A eval --config "$world" --workers 6 --seat "0=ppo:$slot" --seat "1=ppo:$slot" --seat "2=ppo:$slot" --seat "3=ppo:$slot" --seat "4=ppo:$slot" --out-dir "$out" > "$out/all.log" 2>&1; tail -n 1 "$out/all.log"
  fi
done
echo "== read $(date -u +%FT%TZ)"
$PY $D/tier2_read.py "$R/battery" "$D/results-raw/battery" --out "$R/tier2-read.json"
echo "== stage3 done $(date -u +%FT%TZ)"
