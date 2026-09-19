#!/usr/bin/env bash
# Tier 2, stage 1: the package corpus (bc-collect, 40 x 20k, seeds 1092001-1092040, held-out
# 03/13/23/33 with --trace, nine blocks in parallel), the flat view, the lesson clone (strip,
# then teach), the BC bars (proposed and applied want source) and Part A on the held-out traces.
# Launch: caffeinate -s nohup bash experiments/beam-world-screen-2026-09-19/stage1.sh > .../results-raw/tier2/stage1.log 2>&1 &
set -uo pipefail
D=experiments/beam-world-screen-2026-09-19
R=$D/results-raw/tier2; C=$R/bc-corpus-pkg; L=$R/logs
mkdir -p "$C" "$R/clones" "$L"
PY=experiments/exp-006-character-gen/.venv/bin/python
BC=experiments/tools/bc-collect/target/release/bc-collect
TR=experiments/fog-gen1-shakeout/trainer
CFG=$D/package.toml; BASE=1092001; THREADS=${THREADS:-12}
echo "== stage1 start $(date -u +%FT%TZ) head $(git rev-parse --short HEAD) bc-collect $(shasum -a 256 $BC | cut -c1-16)"

# block  rollouts  first-index  trace
BLOCKS="00-02:3:0:0 03:1:3:1 04-12:9:4:0 13:1:13:1 14-22:9:14:0 23:1:23:1 24-32:9:24:0 33:1:33:1 34-39:6:34:0"
if [ ! -e "$C/flat" ]; then
  for b in $BLOCKS; do
    IFS=: read -r name n first trace <<< "$b"
    out="$C/idx$name"; [ -d "$out" ] && { echo "skip collect idx$name"; continue; }
    t=""; [ "$trace" = 1 ] && t="--trace"
    nice -n 19 "$BC" --config "$CFG" --rollouts "$n" --ticks 20000 --seed-base $((BASE + first)) $t --out-dir "$out" > "$L/collect-idx$name.log" 2>&1 &
  done
  wait
  echo "== collected $(date -u +%FT%TZ)"
  mkdir -p "$C/flat"
  for b in $BLOCKS; do
    IFS=: read -r name n first trace <<< "$b"
    k=0
    for r in $(ls "$C/idx$name" | sort); do
      ln -s "../idx$name/$r" "$C/flat/config-00-rollout-$(printf %02d $((first + k)))"; k=$((k + 1))
    done
  done
fi
$PY - "$C/flat" <<'EOF'
import json, sys, pathlib
flat = pathlib.Path(sys.argv[1]); dirs = sorted(p for p in flat.iterdir() if (p / "meta.json").exists())
seeds = [json.load(open(p / "meta.json"))["world_seed"] for p in dirs]
shas = {json.load(open(p / "meta.json"))["config_sha256"] for p in dirs}
traced = [p.name[-2:] for p in dirs if json.load(open(p / "meta.json")).get("trace")]
dec = sum(json.load(open(p / "meta.json"))["decisions"] for p in dirs)
assert len(dirs) == 40 and len(set(seeds)) == 40 and min(seeds) == 1092001 and max(seeds) == 1092040, (len(dirs), min(seeds), max(seeds))
assert len(shas) == 1, shas
assert traced == ["03", "13", "23", "33"], traced
print("flat view ok: 40 rollouts, seeds 1092001-1092040, config sha", shas.pop()[:16], "traced", traced, "decisions", dec)
EOF
[ $? -eq 0 ] || { echo "== FLAT VIEW CHECK FAILED"; exit 1; }

if [ ! -f "$R/clones/pkg-strip/pkg-strip.pt" ]; then
  echo "== strip $(date -u +%FT%TZ)"
  nice -n 10 $PY $TR/train_vocab_fog.py --stage strip --name pkg-strip --data-root "$C/flat" --out-dir "$R/clones/pkg-strip" --threads "$THREADS" > "$L/strip.log" 2>&1
  tail -n 1 "$L/strip.log"
fi
if [ ! -f "$R/clones/pkg-vocab/pkg-vocab.pt" ]; then
  echo "== teach $(date -u +%FT%TZ)"
  nice -n 10 $PY $TR/train_vocab_fog.py --stage teach --init "$R/clones/pkg-strip/pkg-strip.pt" --name pkg-vocab --data-root "$C/flat" --out-dir "$R/clones/pkg-vocab" --threads "$THREADS" > "$L/teach.log" 2>&1
  tail -n 1 "$L/teach.log"
fi
echo "== bars $(date -u +%FT%TZ)"
$PY $TR/readout_fog.py --clone "$R/clones/pkg-vocab/pkg-vocab.pt" --data-root "$C/flat" --want-source proposed --out "$R/clones/pkg-vocab/bars-proposed.json" > "$L/bars-proposed.log" 2>&1; tail -n 2 "$L/bars-proposed.log"
$PY $TR/readout_fog.py --clone "$R/clones/pkg-vocab/pkg-vocab.pt" --data-root "$C/flat" --want-source applied --out "$R/clones/pkg-vocab/bars.json" > "$L/bars-applied.log" 2>&1; tail -n 1 "$L/bars-applied.log"
echo "== part A on the held-out traces $(date -u +%FT%TZ)"
for nn in 03 13 23 33; do
  $PY experiments/fog-gen1-shakeout/schema_check.py "$C/flat/config-00-rollout-$nn" --declared-constant experiments/fog-gen1-cert/declared_constant.json --json "$R/schema-check-$nn.json" > "$L/schema-check-$nn.log" 2>&1; tail -n 1 "$L/schema-check-$nn.log"
done
echo "== stage1 done $(date -u +%FT%TZ)"
