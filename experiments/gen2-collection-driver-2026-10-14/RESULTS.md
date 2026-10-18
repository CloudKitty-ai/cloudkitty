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
  COMPOSITION (traced re-run of rollout 00, deterministic, 424
  skipped rows): 261 are applied groom-with-kitty-target, activity
  states grooming 257 / idle 166 / resting 1 — i.e. mostly
  mid-scene groom continuation ticks the engine carries while the
  solo-context mask no longer offers the entry; the rest are
  scattered moves/idles/chases. Scene-START rows are mask-legal
  and kept, so the corpus still demonstrates initiation; the
  student never needs the excluded continuation labels (activity
  state carries scenes at deployment). Re-check at the 100-rollout
  read that the per-class rates stay uniform — divergence would be
  a between-arm corpus bias for the three-leg comparison.

## Full collection, 100 rollouts (2026-10-18)

Same frozen shape, 100 rollouts × 20k ticks (launched directly after
the starts check per her "Starts check first" sequencing). Raws:
`results-raw/full-100/` (manifest, configs, r00–r99, placement.json,
coverage.json). THIS is the trunk-BC corpus.

- Classes (exact-count law at 100): **60 served / 12 enrichment /
  28 traits** — as pinned (mix 0.6/0.12/0.28). Enrichment consents
  12 draws in [20.417, 24.351] ⊂ [20,25]. Realized start shares
  0.190 edge / 0.038 corner over 500 draws (pilot read 0.300/0.067;
  both bracket the pencil thresholds 0.25/0.05, seed-keyed draw).
  Decisions 9,960,292; dropped 0 (100/100 rollout lines).
- **Placement bar (S§6, pre-PPO gate): PASS** — pooled in-beam
  sleep share **0.4341** ≥ 0.40, over 680,725 sleep ticks
  (`results-raw/full-100/placement.json`; pilot read 0.4254).
- **Here-word density pin (F-034, pre-PPO re-check): PASS** —
  here-kinds are **17.23%** of decisions vs the 8.18% fluent anchor
  (pilot 17.10%). By kind: food 3.92%, water 4.61%, critter 1.77%,
  sunbeam 6.93%.
- Coverage read: pooled edge-ring visit share 0.0508, corner 0.0009
  over 10,000,000 kitty-ticks (pilot 0.0577/0.0012; uniform 20×20
  would read 0.19/0.01). No bar; the frozen remedy keys on placement
  + density, both PASS.
- mask-mismatch 39,708/9,960,292 = **0.399%** (pilot 0.406%).
  **Per-class uniformity re-check (flagged at the pilot): PASS** —
  enrichment 0.478%, served 0.408%, traits 0.346%, each within
  0.015 points of its pilot value (0.463/0.419/0.348); same ordering,
  no divergence, so no between-arm corpus bias for the three-leg
  comparison from this exclusion class.
- **Starts check, leg B on this manifest: PASS 100/100** — every
  rollout's manifest starts/categories, config x/y, and enrichment
  consent line re-derived exactly from the manifest draw_seed
  (`starts_check.py --manifest results-raw/full-100/manifest.json`).

All pre-PPO gates pass; no deviations — `gen2-deviations.md` stays
empty. Regeneration: the pilot fences below with
`results-raw/pilot-30` → `results-raw/full-100`, `--rollouts 100`,
`range(30)` → `range(100)`.

## Starts check (banked at the 062 merge; owner "Starts check first")

`starts_check.py`, two independent legs, all PASS 2026-10-18:

- ENGINE LAW: pure-Python port of draw-law v1 (own ChaCha8,
  rand_chacha 0.3 semantics) is BYTE-EXACT against the engine-emitted
  golden vectors — all 3 cases, raw u64 streams and final positions —
  and matches the live engine's knob-on starts echo position-for-
  position on g2leg-20 at seeds 905001/905013/905029 (recorded metas:
  `results-raw/fixture-starts-echo/`, never delete). This validates
  the mechanism the comparator legs and future PPO episodes draw
  under (SC-005's independent-port expectation met a second time).
- DRIVER DRAW: the pilot's 30 driver-drawn rollouts re-derived from
  the manifest's draw_seed by replaying collect_corpus's exact RNG
  order (class permutation → per-rollout starts → class draws):
  manifest starts/categories, the explicit x/y in every rollout
  config, and the enrichment consent lines all match.

Guard: `test_starts_check.py` (6 tests incl. the explicit-consumes-
zero-draws law property and two tamper-sensitivity self-tests);
3 mutate cycles RED CONFIRMED (ChaCha rounds 4→3 → "u64 stream
diverges"; `v1 >> 11` → `>> 10` → "positions differ"; dropped
permutation replay → "re-derived draw differs"; the first cycle
re-ran isolated to its target test after a wrong-reason red).

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
# Mask-mismatch composition (~2 min): traced re-run of rollout 00, then
# diff (tick,kitty) pairs in the trace against the kept corpus rows and
# read each skipped pair's last_action/activity from the post-apply
# snapshot:
#   bc-collect --config results-raw/pilot-30/configs/rollout-00.toml \
#       --rollouts 1 --ticks 20000 --seed-base 910001 --out-dir SCRATCH --trace
#   (kept = zip(tick.npy, kitty.npy); missing pairs -> trace.jsonl rows;
#    expect 424 skipped, 261 groom-with-target, states grooming 257 /
#    idle 166 / resting 1)
```
