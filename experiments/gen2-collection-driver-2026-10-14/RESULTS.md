# Gen 2 collection — realized reads

## Pilot, 30 rollouts (owner "Start the pilot", 2026-10-17)

Frozen-prereg shape (`gen2-prereg-2026-10-17.md` §4/§10.2): base =
`gen2-world-draft-2026-10-15.toml` (vocab-armed), 30 rollouts × 20k
ticks, driver defaults = the ruled dials. Raws:
`results-raw/pilot-30/` (manifest, per-rollout configs, r00–r29).

- Classes (exact-count law at 30): 18 served / 4 enrichment /
  8 traits. Enrichment consent drawn per-episode in [20,25]
  (e.g. 22.669); served/traits base 0. Realized start shares
  0.300 edge / 0.067 corner (pencil 0.25/0.05, seed-keyed engine
  draw). Decisions 2,987,861; dropped 0.
- **Placement bar (S§6, pre-PPO gate): PASS** — pooled in-beam
  sleep share **0.4254** ≥ 0.40, over 206,614 sleep ticks
  (`results-raw/pilot-30/placement.json`, placement_read.py).
- **Here-word density pin (F-034, pre-PPO re-check): PASS** —
  here-kinds are **17.10%** of decisions, more than double the
  8.18% fluent anchor (mute side was 5.56%). By kind: food 3.86%,
  water 4.61%, critter 1.77%, sunbeam 6.87%.
- Coverage read (declared §9 instrument): pooled edge-ring VISIT
  share 0.0577, corner 0.0012 over 3,000,000 kitty-ticks (uniform
  20×20 would read 0.19/0.01 — the roster converges inward;
  `results-raw/pilot-30/coverage.json`).
- mask-mismatch 12,139/2,987,861 = **0.406%** (rows excluded from
  the corpus by construction — bc-collect's joint-resolution class:
  the applied action was legal jointly but the solo-context mask
  ruled it out, "not a clean label"). Uniform across classes
  (enrichment 0.463%, served 0.419%, traits 0.348%), so it is
  structural, not consent-driven. Known companions: msg_downgraded
  present, proposed-inexpressible per the #459 header pricing.

## Regeneration

### Collect

```sh
cd /Users/elizabethkelly/ai/cloudkitty/experiments/gen2-collection-driver-2026-10-14
caffeinate -s python3 -B collect_corpus.py \
    --base-config ../gen2-world-draft-2026-10-15.toml \
    --out-dir results-raw/pilot-30 --rollouts 30 --jobs 6   # ~20 min
```

### Read

```sh
cd /Users/elizabethkelly/ai/cloudkitty/experiments/gen2-collection-driver-2026-10-14
# Placement (~10 s): pooled share + bar.
python3 -B ../gen2-corpus-reads-2026-10-13/placement_read.py \
    results-raw/pilot-30/r*/config-00-rollout-00 \
    --out results-raw/pilot-30/placement.json
# Coverage (~30 s): pooled edge/corner visit shares.
python3 -B ../gen2-corpus-reads-2026-10-13/coverage_read.py \
    pooled=results-raw/pilot-30 --out results-raw/pilot-30/coverage.json
# Here-word density + mask-mismatch + classes (~10 s):
../exp-006-character-gen/.venv/bin/python -c "
import numpy as np, json, collections
man = json.load(open('results-raw/pilot-30/manifest.json'))
cls = {r['rollout']: r['class'] for r in man['rollouts']}
tot = here = 0; per = {k: 0 for k in range(9, 13)}
agg = collections.defaultdict(lambda: [0, 0])
for i in range(30):
    m = np.load(f'results-raw/pilot-30/r{i:02d}/config-00-rollout-00/label_msg.npy')
    meta = json.load(open(f'results-raw/pilot-30/r{i:02d}/config-00-rollout-00/meta.json'))
    tot += len(m); here += int(((m >= 9) & (m <= 12)).sum())
    for k in per: per[k] += int((m == k).sum())
    agg[cls[i]][0] += meta['mask_mismatch']; agg[cls[i]][1] += meta['decisions']
print('decisions', tot, 'here %.2f%%' % (100 * here / tot),
      {k: round(100 * v / tot, 2) for k, v in per.items()})
print({c: '%d/%d=%.3f%%' % (mm, n, 100 * mm / n) for c, (mm, n) in sorted(agg.items())},
      'classes', dict(collections.Counter(cls.values())))
"
# here-kind labels: msg head indices 9-12 = HereFood/HereWater/
# HereCritter/HereSunbeam (observe.rs HEAD_KINDS, Silent = 0).
```
