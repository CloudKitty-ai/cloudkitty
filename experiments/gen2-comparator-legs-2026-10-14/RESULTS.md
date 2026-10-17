# Gen 2 scripted comparator legs — realized numbers (§7 pin input)

Freeze sitting 2026-10-17. Battery shape per the ruled §7: 30 seeds
(band `g2cmp`, 905001–905030) × 20,000 ticks, scripted seating, per-seed
engine-drawn starts (`[starts]` 25% edge ring / 5% corner — the pencil
shares; the share-timing re-run rule governs if the freeze pins
different finals). Scouts-first on the displaced sizes (3 worlds each,
F-053 1,000-tick stop armed), per K§5 + the coverage amendment.
Configs: `g2leg-{20,40,100}.toml` (derive_leg_configs.py), under the
VISION LAW (owner ruled 2026-10-17: ≤10 → 3, 11–39 → 4 base, 40–79 →
5, ≥80 → 6; served 20×20 byte-untouched).

## Realized table (the law's legs — the §7 pin)

| leg | vision | team happiness (mean over 30 seeds) | per-seed range | worst-streak mean / max | F-053 events |
|---|---|---|---|---|---|
| 20×20 | 4 (base) | 81.921 | [80.409, 82.712] | 178 / 401 | none |
| 40×40 | 5 | 81.634 | [80.640, 82.320] | 197 / 626 | none |
| 100×100 | 6 | 76.623 | [73.754, 80.416] | 443 / 716 | none |

Scouts, law legs: size40 (298, 55, 262), size100 (361, 413, 334) —
all clean. Raws: `results-raw/legs/size20/` (the law's 20×20 — the
original run; its config is the law's, byte-identical),
`results-raw/vision5-40/legs/size40/`,
`results-raw/vision-law-100/legs/size100/` (gitignored, never delete).
Provenance note: the 40×40 law raws record the probe toml's hash
(`results-raw/g2leg-40-vision5.toml`), which parses equal to
`g2leg-40.toml` — the bytes differ only in one comment.

## The vision-4 record (superseded for the pin; kept as the finding)

The first full run used vision 4 at every size:

| leg | team happiness | per-seed range | worst-streak mean / max | F-053 |
|---|---|---|---|---|
| 40×40 @ v4 | 80.341 | [78.566, 82.030] | 257 / 570 | none |
| 100×100 @ v4 | 72.814 | [68.808, 75.440] | 556 / 1000 | seed 905029 ABORTED at tick 5,807 |

Paired law-vs-v4 deltas (same 30 seeds): 40×40 +1.294 (28/30
positive, range [−0.690, +3.303]); 100×100 +3.809 (28/30, range
[−0.231, +9.319]). Raws: `results-raw/legs/size40/`,
`results-raw/legs/size100/`, scouts under `results-raw/scouts/`.

### The 905029 finding (vision 4, 100×100)

The abort was not placement variance and not social dispersion, both
measured from the trace re-capture
(`results-raw/forensic-905029/`, deterministic from `seed 905029` on
the v4 config):

- The roster CONVERGED within ~1,000 ticks (closest-pair Manhattan
  distance mean 1.1–1.9 per 1,000-tick bucket — the single closest
  pair, not each cat's nearest neighbour; all-pair mean 4–16) and
  partnered scenes ran throughout (2,745 partnered-rest, 702
  kitty-play, 667 groom-other kitty-ticks over 6,000 ticks) — the
  shipped distance-closers (global hearing + answer rungs) worked.
- There were NO food deserts: chow count pinned at exactly 150 every
  sampled tick; nearest-bowl Manhattan distance from any cat (full
  scan, all 30,000 kitty-ticks) median 9, p90 14, worst moment of the
  whole run 23 (hungry-only, eat > 50: median 10, max 22).
- But only 16.3% of kitty-ticks had a bowl inside the Euclidean
  4-radius vision disc (33.7% within 6): the pod lived in a
  consumption-dug local
  hole (five cats drain 5-serving bowls; respawns land anywhere) it
  could not see out of. Distress by kind: eat 4,989, cuddle 3,996,
  drink 2,418, sleep 2,053 kitty-ticks; eating intake decayed
  36 → 24 kitty-ticks per 1,000 as the abort neared.
- Single-seed vision probes on this world (6,000 ticks): v4 eat
  distress 4,989 / happiness 69.66 / streak 1,085; v5 597 / 78.49 /
  191; v6 25 / 81.10 / 66; v8 1,258 / 78.55 / 365 (the v8 row is the
  single-seed trajectory lottery, not a curve). Intake totals barely
  move (182–216): the v4 failure was latency, not total supply.
- Under the law (v6, full 20k run): this seed finishes at happiness
  77.35, worst streak 362.

## Reference reads (not pins)

Vision 5 on the served 20×20, same 30 seeds, paired: +0.746 (26/30
positive, range [−0.518, +2.175]), streak mean 178 → 105. Measured
and set aside: the served world keeps radius 4 — the Gen 1 fog law
and the comms-pressure thesis are worth the ~0.75 scripted-roster
happiness price (owner's law keeps 20×20 at base). Raw:
`results-raw/vision5-20/legs/size20/`.

## Regeneration

### Collect

```sh
cd /Users/elizabethkelly/ai/cloudkitty/experiments/gen2-comparator-legs-2026-10-14
python3 -B derive_leg_configs.py   # writes g2leg-{20,40,100}.toml, checks + engine loads
caffeinate -s python3 -B run_legs.py --config-20 g2leg-20.toml --config-40 g2leg-40.toml \
    --config-100 g2leg-100.toml --band g2cmp --seeds 30 --ticks 20000 --workers 6 \
    --out-dir results-raw/REGEN
# ~15 min for the full battery on an M-class laptop; scouts gate the
# displaced sizes automatically. The engine start draw is seed-keyed
# (062 draw-law v1), so a re-run reproduces the same worlds given the
# same binary. The forensic trace re-capture:
../tools/bc-collect/target/release/bc-collect --config g2leg-100.toml --rollouts 1 \
    --ticks 6000 --seed-base 905029 --out-dir OUT --trace   # (v4 variant needs radius=4)
```

### Read

```sh
cd /Users/elizabethkelly/ai/cloudkitty/experiments/gen2-comparator-legs-2026-10-14
# Per-leg jsonl: row 1 provenance, then one row per seed. Table cells:
# team happiness = mean over seeds of mean(mean_happiness); range over
# the same per-seed means; streaks = max_distress_age mean/max.
python3 -c "
import json, statistics
for name, path in [('20x20 law', 'results-raw/legs/size20/scripted-g2cmp-30x20000.jsonl'),
                   ('40x40 law', 'results-raw/vision5-40/legs/size40/scripted-g2cmp-30x20000.jsonl'),
                   ('100x100 law', 'results-raw/vision-law-100/legs/size100/scripted-g2cmp-30x20000.jsonl'),
                   ('40x40 v4', 'results-raw/legs/size40/scripted-g2cmp-30x20000.jsonl'),
                   ('100x100 v4', 'results-raw/legs/size100/scripted-g2cmp-30x20000.jsonl')]:
    rows = [json.loads(l) for l in open(path).read().splitlines()[1:]]
    team = [statistics.mean(r['mean_happiness']) for r in rows]
    m = [r['max_distress_age'] for r in rows]
    print(name, round(statistics.mean(team), 3), [round(min(team), 3), round(max(team), 3)],
          round(statistics.mean(m)), max(m), [r['seed'] for r in rows if r['max_distress_age'] >= 1000])
"  # ~5 s
```
