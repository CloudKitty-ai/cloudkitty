#!/usr/bin/env bash
# Tier 2, stage 2: the clone-only placement read (PREREG-tier2 prediction 2), then the four PPO
# arms in parallel. Run after stage 1's bars are read (a miss goes to the owner first).
# Launch: caffeinate -s nohup bash experiments/beam-world-screen-2026-09-19/stage2.sh > .../results-raw/tier2/stage2.log 2>&1 &
set -uo pipefail
D=experiments/beam-world-screen-2026-09-19
R=$D/results-raw/tier2; A=$D/artifacts; mkdir -p "$A" "$R/pass-logs" "$R/battery/clone"
PY=experiments/exp-006-character-gen/.venv/bin/python
CLONE=$R/clones/pkg-vocab/pkg-vocab.pt
[ -f "$CLONE" ] || { echo "no clone at $CLONE"; exit 1; }
echo "== stage2 start $(date -u +%FT%TZ) head $(git rev-parse --short HEAD)"

# the clone as a harness artifact: artifacts/ppo-fog-pkg-clone/policy-final.pt -> the .pt ({"hyper","state_dict"}, the trainer's own format)
mkdir -p "$A/ppo-fog-pkg-clone"; ln -sf "$(cd "$(dirname "$CLONE")" && pwd)/$(basename "$CLONE")" "$A/ppo-fog-pkg-clone/policy-final.pt"
if [ ! -f "$R/battery/clone/done" ]; then
  echo "== clone placement read (5 seeds x 20k, clone at all five seats, package world) $(date -u +%FT%TZ)"
  CERT_ARTS=$A $PY experiments/fog-gen1-cert/cert_harness_fog.py gen1-A eval --config $D/package.toml --seeds 5 --workers 5 \
    --seat 0=ppo:pkg-clone --seat 1=ppo:pkg-clone --seat 2=ppo:pkg-clone --seat 3=ppo:pkg-clone --seat 4=ppo:pkg-clone \
    --out-dir "$R/battery/clone" > "$R/battery/clone/harness.log" 2>&1 && touch "$R/battery/clone/done"
  tail -n 1 "$R/battery/clone/harness.log"
  $PY - "$R/battery/clone" <<'EOF'
import json, sys, pathlib
sys.path.insert(0, "experiments/beam-world-screen-2026-09-19"); import screen_read as S
f = next(pathlib.Path(sys.argv[1]).glob("*.jsonl")); head, rows = S.load_rows(f); a = S.aggregate(rows)
print("clone placement %.3f tick-share %.3f (%d seeds) nash %.3f hap %.2f" % (a["pooled"]["start_dist"][0], a["pooled"]["in_beam"], a["seeds"], a["pooled"]["nash_state"], a["pooled"]["happiness"]))
EOF
fi

echo "== PPO arms $(date -u +%FT%TZ)"
for slot in pkg-s1 pkg-s2 floor5-s1 floor5-s2; do
  if [ -f "$A/ppo-fog-$slot/policy-final.pt" ]; then echo "skip $slot (final exists)"; continue; fi
  nice -n 19 $PY $D/trainer/train_ppo_beam.py --slot "$slot" --threads 4 > "$R/pass-logs/$slot.log" 2>&1 &
  echo "launched $slot pid $!"
done
wait
echo "== stage2 done $(date -u +%FT%TZ)"
for slot in pkg-s1 pkg-s2 floor5-s1 floor5-s2; do echo "$slot: $(tail -n 1 "$R/pass-logs/$slot.log")"; done
