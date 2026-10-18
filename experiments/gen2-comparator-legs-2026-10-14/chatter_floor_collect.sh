#!/bin/zsh
# Chatter-floor re-measure (frozen prereg §8.1 rung 1): bc-collect the
# three Gen 2 comparator legs on the g2cmp band (seeds 905001-905030,
# world_seed = seed_base + r, ci = 0), count the message-head labels
# per rollout, keep only the small histogram JSON. Shards of 5
# rollouts x 6 run in parallel; raw shards are scratch, deleted after
# counting. Usage: chatter_floor_collect.sh <scratch-dir>
set -e
ROOT=${0:a:h:h:h}
LEGS=${0:a:h}
BC=$ROOT/experiments/tools/bc-collect/target/release/bc-collect
SCRATCH=${1:?scratch dir required}/chatter-floor
OUT=$LEGS/results-raw/chatter-floor
mkdir -p $OUT
for SIZE in 20 40 100; do
  echo "== leg $SIZE $(date -u +%H:%M:%SZ)"
  rm -rf $SCRATCH; mkdir -p $SCRATCH
  for J in 0 1 2 3 4 5; do
    $BC --config $LEGS/g2leg-$SIZE.toml --rollouts 5 --ticks 20000 \
        --seed-base $((905001 + 5 * J)) --out-dir $SCRATCH/shard-$J \
        > $SCRATCH/shard-$J.log 2>&1 &
  done
  wait
  $ROOT/experiments/exp-006-character-gen/.venv/bin/python - "$SCRATCH" "$OUT/leg-$SIZE.json" <<'PY'
import json, sys
from pathlib import Path
import numpy as np
scratch, out = Path(sys.argv[1]), Path(sys.argv[2])
rows = []
for shard in sorted(scratch.glob("shard-*/")):
    for rdir in sorted(shard.glob("config-00-rollout-*")):
        meta = json.load(open(rdir / "meta.json"))
        m = np.load(rdir / "label_msg.npy")
        hist = np.bincount(m, minlength=16).tolist()
        assert sum(hist) == len(m)
        rows.append({"world_seed": meta["world_seed"], "rows": len(m),
                     "decisions": meta["decisions"],
                     "mask_mismatch": meta["mask_mismatch"],
                     "msg_hist": hist})
rows.sort(key=lambda r: r["world_seed"])
seeds = [r["world_seed"] for r in rows]
assert seeds == list(range(905001, 905031)), seeds
json.dump({"head_kinds_note": "index 0 = Silent, k+1 = HEAD_KINDS[k]; "
           "mew 3, purr 6, chirp 13, trill 14, ekekek 15, here 9-12",
           "band": "g2cmp 905001-905030", "ticks": 20000,
           "rollouts": rows}, open(out, "w"), indent=1)
tot = sum(r["rows"] for r in rows)
free = sum(sum(r["msg_hist"][k] for k in (3, 6, 13, 14, 15)) for r in rows)
print(f"leg done: {len(rows)} rollouts, {tot} rows, free-register {free}")
PY
done
rm -rf $SCRATCH
echo "== all legs done $(date -u +%H:%M:%SZ)"
