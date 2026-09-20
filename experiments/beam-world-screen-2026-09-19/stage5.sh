#!/usr/bin/env bash
# Tier 5 (PREREG-tier5.md), one command once spec 056 is on main and the lab binding is rebuilt:
#   comparators  : scripted + gen1-A on each floor world (30 x 20k, the harness beam block)
#   arms         : eight PPO arms from the package clone, in parallel (2 threads each)
#   reads        : per arm, five swap legs + the all-arm roster on its floor world
# Skip-if-done at every step. Launch: caffeinate -s nohup bash experiments/beam-world-screen-2026-09-19/stage5.sh > .../results-raw/tier5/stage5.log 2>&1 &
set -uo pipefail
D=experiments/beam-world-screen-2026-09-19; R=$D/results-raw/tier5; A=$D/artifacts
PY=experiments/exp-006-character-gen/.venv/bin/python; H=experiments/fog-gen1-cert/cert_harness_fog.py
mkdir -p "$R/battery" "$R/pass-logs" "$D/results-raw/configs"
$PY - <<'PYEOF'
import sys, hashlib, re; sys.path.insert(0, "experiments/beam-world-screen-2026-09-19"); import derive_configs as D
a = D.ANCHOR.read_text(); pre = open("experiments/beam-world-screen-2026-09-19/PREREG-tier5.md").read()
for f in (10, 15, 20, 25):
    p = f"experiments/beam-world-screen-2026-09-19/results-raw/configs/shallow-{f}.toml"; open(p, "w").write(D.derive(a, 3.0, 7.0, 3000, 6, f))
    sha = hashlib.sha256(open(p, "rb").read()).hexdigest(); assert f"- shallow-{f} `{sha}`" in pre, (f, sha)
print("floor worlds derived and match the prereg shas")
PYEOF
echo "== tier5 start $(date -u +%FT%TZ) head $(git rev-parse --short HEAD) binding $($PY -c 'import cloudkitty;print(getattr(cloudkitty,"ENGINE_COMMIT",None))')"
for f in 10 15 20 25; do
  w=$D/results-raw/configs/shallow-$f.toml; out=$R/battery/shallow-$f; mkdir -p "$out"
  for seating in scripted gen1-A; do
    fn="$out/$seating-eval-30x20000.jsonl"; [ "$seating" = gen1-A ] && fn="$out/gen1-A-c0-eval-30x20000.jsonl"
    if [ -f "$fn" ] && [ "$(wc -l < "$fn")" -ge 31 ]; then echo "skip comparator $f $seating"; continue; fi
    echo "== comparator floor $f $seating $(date -u +%FT%TZ)"
    CERT_ARTS=$A $PY $H "$seating" eval --config "$w" --workers 6 --out-dir "$out" > "$out/$seating.log" 2>&1; tail -n 1 "$out/$seating.log"
  done
done
echo "== arms $(date -u +%FT%TZ)"
for slot in sg10-s1 sg10-s2 sg15-s1 sg15-s2 sg20-s1 sg20-s2 sg25-s1 sg25-s2; do
  if [ -f "$A/ppo-fog-$slot/policy-final.pt" ]; then echo "skip $slot (final exists)"; continue; fi
  nice -n 19 $PY $D/trainer/train_ppo_beam.py --slot "$slot" --threads 2 > "$R/pass-logs/$slot.log" 2>&1 &
  echo "launched $slot pid $!"
done
wait
for slot in sg10-s1 sg10-s2 sg15-s1 sg15-s2 sg20-s1 sg20-s2 sg25-s1 sg25-s2; do echo "$slot: $(grep -iE 'PLATEAU|STOP RULE' "$R/pass-logs/$slot.log" | tail -n 1 | cut -c1-80)"; done
echo "== reads $(date -u +%FT%TZ)"
for slot in sg10-s1 sg10-s2 sg15-s1 sg15-s2 sg20-s1 sg20-s2 sg25-s1 sg25-s2; do
  [ -f "$A/ppo-fog-$slot/policy-final.pt" ] || { echo "no final for $slot"; continue; }
  f=${slot#sg}; f=${f%-s*}; w=$D/results-raw/configs/shallow-$f.toml; out=$R/battery/$slot; mkdir -p "$out"
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
echo "== tier5 done $(date -u +%FT%TZ)"
