#!/usr/bin/env bash
# Tier 6 (PREREG-tier6.md), one command on main with the lab binding rebuilt from it:
#   comparators  : scripted + gen1-A on count-5/7/8 at floor 15 (30 x 20k); count 6 = tier 5's shallow-15 battery
#   arms         : six PPO arms (cnt5/7/8 x s1/s2) from the package clone, in parallel (2 threads each)
#   reads        : per new arm, five swap legs + the all-arm roster on its count world;
#                  transfer: the count-6 arms (sg15-s1/s2) all-arm on count-5/7/8
# Skip-if-done at every step. Launch: caffeinate -s nohup bash experiments/beam-world-screen-2026-09-19/stage6.sh > .../results-raw/tier6/stage6.log 2>&1 &
set -uo pipefail
D=experiments/beam-world-screen-2026-09-19; R=$D/results-raw/tier6; A=$D/artifacts
PY=experiments/exp-006-character-gen/.venv/bin/python; H=experiments/fog-gen1-cert/cert_harness_fog.py
mkdir -p "$R/battery" "$R/pass-logs"
$PY - <<'PYEOF'
import sys, hashlib; sys.path.insert(0, "experiments/beam-world-screen-2026-09-19"); import derive_configs as D
a = D.ANCHOR.read_text(); pre = open("experiments/beam-world-screen-2026-09-19/PREREG-tier6.md").read()
for n in (5, 7, 8):
    t = D.derive(a, 3.0, 7.0, 3000, n, 15); p = f"experiments/beam-world-screen-2026-09-19/count-{n}.toml"
    assert open(p).read() == t, p
    sha = hashlib.sha256(t.encode()).hexdigest(); assert f"- count-{n} `{sha}`" in pre, (n, sha)
print("count worlds match the committed files and the prereg shas")
PYEOF
echo "== tier6 start $(date -u +%FT%TZ) head $(git rev-parse --short HEAD) binding $($PY -c 'import cloudkitty;print(getattr(cloudkitty,"ENGINE_COMMIT",None))')"
for n in 5 7 8; do
  w=$D/count-$n.toml; out=$R/battery/count-$n; mkdir -p "$out"
  for seating in scripted gen1-A; do
    fn="$out/$seating-eval-30x20000.jsonl"; [ "$seating" = gen1-A ] && fn="$out/gen1-A-c0-eval-30x20000.jsonl"
    if [ -f "$fn" ] && [ "$(wc -l < "$fn")" -ge 31 ]; then echo "skip comparator $n $seating"; continue; fi
    echo "== comparator count $n $seating $(date -u +%FT%TZ)"
    CERT_ARTS=$A $PY $H "$seating" eval --config "$w" --workers 6 --out-dir "$out" > "$out/$seating.log" 2>&1; tail -n 1 "$out/$seating.log"
  done
done
SLOTS="cnt5-s1 cnt5-s2 cnt7-s1 cnt7-s2 cnt8-s1 cnt8-s2"
echo "== arms $(date -u +%FT%TZ)"
for slot in $SLOTS; do
  if [ -f "$A/ppo-fog-$slot/policy-final.pt" ]; then echo "skip $slot (final exists)"; continue; fi
  nice -n 19 $PY $D/trainer/train_ppo_beam.py --slot "$slot" --threads 2 > "$R/pass-logs/$slot.log" 2>&1 &
  echo "launched $slot pid $!"
done
wait
for slot in $SLOTS; do echo "$slot: $(grep -iE 'PLATEAU|STOP RULE' "$R/pass-logs/$slot.log" | tail -n 1 | cut -c1-80)"; done
echo "== reads $(date -u +%FT%TZ)"
for slot in $SLOTS; do
  [ -f "$A/ppo-fog-$slot/policy-final.pt" ] || { echo "no final for $slot"; continue; }
  n=${slot#cnt}; n=${n%-s*}; w=$D/count-$n.toml; out=$R/battery/$slot; mkdir -p "$out"
  for k in 0 1 2 3 4; do
    fn="$out/gen1-A_s$k-$slot-c0-eval-30x20000.jsonl"
    if [ -f "$fn" ] && [ "$(wc -l < "$fn")" -ge 31 ]; then echo "skip $slot seat $k"; continue; fi
    echo "== $slot into seat $k $(date -u +%FT%TZ)"
    CERT_ARTS=$A $PY $H gen1-A eval --config "$w" --workers 6 --seat "$k=ppo:$slot" --out-dir "$out" > "$out/seat$k.log" 2>&1; tail -n 1 "$out/seat$k.log"
  done
  fn="$out/gen1-A_s0-$slot"_s1-"$slot"_s2-"$slot"_s3-"$slot"_s4-"$slot-c0-eval-30x20000.jsonl"
  if [ -f "$fn" ] && [ "$(wc -l < "$fn")" -ge 31 ]; then echo "skip $slot all-arm"; else
    echo "== $slot all-arm $(date -u +%FT%TZ)"
    CERT_ARTS=$A $PY $H gen1-A eval --config "$w" --workers 6 --seat "0=ppo:$slot" --seat "1=ppo:$slot" --seat "2=ppo:$slot" --seat "3=ppo:$slot" --seat "4=ppo:$slot" --out-dir "$out" > "$out/all.log" 2>&1; tail -n 1 "$out/all.log"
  fi
done
echo "== transfer $(date -u +%FT%TZ)"
for slot in sg15-s1 sg15-s2; do
  for n in 5 7 8; do
    w=$D/count-$n.toml; out=$R/battery/transfer-$slot-count-$n; mkdir -p "$out"
    fn="$out/gen1-A_s0-$slot"_s1-"$slot"_s2-"$slot"_s3-"$slot"_s4-"$slot-c0-eval-30x20000.jsonl"
    if [ -f "$fn" ] && [ "$(wc -l < "$fn")" -ge 31 ]; then echo "skip transfer $slot count $n"; continue; fi
    echo "== transfer $slot all-arm on count $n $(date -u +%FT%TZ)"
    CERT_ARTS=$A $PY $H gen1-A eval --config "$w" --workers 6 --seat "0=ppo:$slot" --seat "1=ppo:$slot" --seat "2=ppo:$slot" --seat "3=ppo:$slot" --seat "4=ppo:$slot" --out-dir "$out" > "$out/all.log" 2>&1; tail -n 1 "$out/all.log"
  done
done
echo "== tier6 done $(date -u +%FT%TZ)"
