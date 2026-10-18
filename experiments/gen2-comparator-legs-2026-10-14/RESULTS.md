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

## Bin-anchor read (owner "Agreed", 2026-10-17): what 45/70/90 name in Gen 2

The semantic anchor of the doctrine bin edges, recorded pre-freeze so
the banked Gen 3 re-anchor obligation
(`gen3-roadmap-inputs-2026-10-04.md` addendum 3) has a committed Gen 2
reference. Scout seeds 905001–905003 per size, 20k ticks, law
configs, traced; flags are the engine's own `in_distress` lists
(edge = `thresholds.distress` 90), never re-derived. 300,000
kitty-ticks per size. Raws: `results-raw/bin-anchor/anchor-{size}.json`
(traces regenerate deterministically; not kept).

| leg | occ <45 / 45–70 / >70 | flagged share | flagged hap median (p10–p90) | flagged <45 / <70 | P(flag·hap<45) | P(flag·hap>70) |
|---|---|---|---|---|---|---|
| 20×20 | 0.668% / 4.20% / 95.13% | 0.99% | 42.0 (25.6–57.1) | 59.1% / 99.7% | 0.876 | 0.0000 |
| 40×40 | 0.787% / 5.32% / 93.89% | 1.24% | 41.1 (22.5–60.6) | 60.7% / 98.6% | 0.955 | 0.0002 |
| 100×100 | 5.570% / 19.00% / 75.43% | 10.72% | 45.6 (23.9–64.9) | 48.6% / 96.9% | 0.935 | 0.0045 |

The anchor in one sentence: **70 is the distress ceiling** (96.9–99.7%
of flagged kitty-ticks sit below it, and essentially no flagged tick
lives above it — P(flag | hap > 70) ≤ 0.0045), **45 marks the graver
half** (48.6–60.7% of flagged ticks below it; a sub-45 tick is flagged
with probability 0.876–0.955), and unflagged mass below 45 is
negligible (0.036–0.403%). Flag composition is cuddle/eat-dominated
(cuddle 1,447/2,743/20,845 and eat 1,205/2,078/18,273 flag kitty-ticks
by size; bath nearly absent at 0/53/259). Unflagged happiness median
83.2/82.9/80.5. The Gen 3 re-anchor re-runs `bin_anchor.py` on the
Gen 3 engine and bridges per the banked obligation.

## Friend-ward drift screen (spec 063, owner kickoff "Let's build it
and see what happiness delta it produces on 100x100")

Both arms fresh on the landed binary (merge 0b2d216f, binding rebuilt
+ 5 smoke tests, bc-collect rebuilt), g2cmp band 30×20k, scouts-first,
law config. On arm = `g2leg-100.toml` + `friend_ward_drift = true` in
`[behavior]` (deep-diff: exactly that key; dials at defaults G=10,
B=4.0). Law for the arm: `specs/063-friend-ward-drift/contracts/drift-law.md`.

| arm | team happiness | per-seed range | worst-streak mean / max | F-053 |
|---|---|---|---|---|
| flag off | 76.623 | [73.754, 80.416] | 443 / 716 | none |
| flag on | 76.811 | [73.752, 79.857] | 451 / 839 | none |

Seed-paired delta (on − off): mean **+0.188**, 14/30 positive, range
[−5.200, +4.263], sd 2.266, mean/sem 0.45 — a NULL at this power. The
flag reshuffles trajectories rather than shifting them: 20/30 seeds
move by more than a point in one direction or the other (the
trajectory lottery), netting ~zero. Distress mass agrees: dist_ticks
paired delta −80 per seed (15/30 positive), low_share(<45) 3.815% off
vs 3.714% on. No F-053 events in either arm; the declared
knowledge-flip residual produced no streak at the line (on-arm worst
839). The off arm reproduces the recorded law-leg row EXACTLY
(76.623 [73.754, 80.416], 443/716) — behavioral confirmation that the
0b2d216f rebuild left flag-off untouched. Scouts: off (361, 413, 334),
on (417, 496, 356), all clean. Raws: `results-raw/fwd-screen/`
({off,on}/legs/size100 + scouts, run.log, the on-arm toml).

### The v4 variant (owner ask 2026-10-17: "Can we run the test with
vision 4 and see if it helps there?")

Same paired screen at radius 4 (the pre-law constraint regime), both
arms fresh on the landed binary, configs deep-diff-checked (off =
law config with only radius 6 → 4; on = that + the flag):

| arm | team happiness | per-seed range | worst-streak mean / max | F-053 |
|---|---|---|---|---|
| v4 off | 72.814 | [68.808, 75.440] | 556 / 1000 | seed 905029 ABORTED at tick 5,807 |
| v4 on | 72.501 | [68.954, 75.963] | 536 / 866 | none |

The off arm reproduces the recorded v4 leg EXACTLY, abort included.
The headline is the tail, not the mean: **the flag rescues 905029** —
no abort, worst streak 1000 → 472, seed happiness 72.938 over the
full 20k (the off arm's 69.651 is a 5,807-tick mean, so that pair's
delta is truncation-confounded). Mean effect stays null-to-slightly-
negative: paired delta −0.313 (14/30 positive, sd 1.925, mean/sem
−0.89; excluding the confounded 905029 pair, −0.437), low_share
6.605% → 6.630%. Worst-streak tail compresses (max 1000-abort → 866,
mean 556 → 536). Scouts clean both arms (off worst 794, on worst
544). Read: at v4 the drift does exactly what Candidate 3 was
designed to do — pull relief choices toward the pod in the
consumption-shadow failure mode — buying tail welfare, not mean
happiness; under the vision law that failure mode is already gone and
the flag is a null. Raws: `results-raw/fwd-screen-v4/`.

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
# Bin-anchor collect (~15 min; traces to scratch, JSON to results-raw/bin-anchor/):
caffeinate -s python3 -B bin_anchor.py --scratch /tmp/bin-anchor-traces
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
# Friend-ward screen read (~1 s): every cell of the screen table + the paired stats.
python3 -c "
import json, statistics, math
def load(p):
    return {r['seed']: r for r in (json.loads(l) for l in open(p).read().splitlines()[1:])}
off = load('results-raw/fwd-screen/off/legs/size100/scripted-g2cmp-30x20000.jsonl')
on  = load('results-raw/fwd-screen/on/legs/size100/scripted-g2cmp-30x20000.jsonl')
assert set(off) == set(on) and len(off) == 30
team = lambda r: statistics.mean(r['mean_happiness'])
for name, arm in (('off', off), ('on', on)):
    t = [team(arm[s]) for s in sorted(arm)]
    m = [arm[s]['max_distress_age'] for s in sorted(arm)]
    print(name, round(statistics.mean(t), 3), [round(min(t), 3), round(max(t), 3)],
          round(statistics.mean(m)), max(m), sum(x >= 1000 for x in m))
d = [team(on[s]) - team(off[s]) for s in sorted(off)]
sd = statistics.stdev(d)
print('delta %+.3f pos %d/30 [%+.3f, %+.3f] sd %.3f mean/sem %.2f gt1 %d/30' %
      (statistics.mean(d), sum(x > 0 for x in d), min(d), max(d), sd,
       statistics.mean(d) / (sd / math.sqrt(30)), sum(abs(x) > 1 for x in d)))
dd = [sum(on[s]['dist_ticks']) - sum(off[s]['dist_ticks']) for s in sorted(off)]
lo = [v for s in sorted(off) for v in off[s]['low_share']]
ln = [v for s in sorted(off) for v in on[s]['low_share']]
print('dist_ticks delta mean %+.0f pos %d/30; low_share off %.3f%% on %.3f%%' %
      (statistics.mean(dd), sum(x > 0 for x in dd),
       statistics.mean(lo) * 100, statistics.mean(ln) * 100))
"
# v4 variant read (~1 s): same recipe on results-raw/fwd-screen-v4/{off,on};
# plus the 905029 pair and the excluding-905029 delta:
python3 -c "
import json, statistics
def load(p):
    return {r['seed']: r for r in (json.loads(l) for l in open(p).read().splitlines()[1:])}
off = load('results-raw/fwd-screen-v4/off/legs/size100/scripted-g2cmp-30x20000.jsonl')
on  = load('results-raw/fwd-screen-v4/on/legs/size100/scripted-g2cmp-30x20000.jsonl')
team = lambda r: statistics.mean(r['mean_happiness'])
print('905029 off', round(team(off[905029]), 3), off[905029]['max_distress_age'], off[905029].get('aborted_streak'))
print('905029 on ', round(team(on[905029]), 3), on[905029]['max_distress_age'], on[905029].get('aborted_streak'))
d = {s: team(on[s]) - team(off[s]) for s in sorted(off)}
print('delta excl 905029: %+.3f' % statistics.mean([v for s, v in d.items() if s != 905029]))
"
# Bin-anchor read (~1 s): every cell of the anchor table from the JSON.
python3 -c "
import json
for s in (20, 40, 100):
    d = json.load(open(f'results-raw/bin-anchor/anchor-{s}.json'))
    o, f, nf = d['occupancy_share'], d['flag'], d['noflag']
    print(s, d['kitty_ticks'],
          ['%.3f' % (o[b]*100) for b in ('lt45','b45_70','gt70')],
          '%.2f' % (f['share']*100), '%.1f' % f['hap_median'],
          '%.1f/%.1f' % (f['hap_p10'], f['hap_p90']),
          '%.1f/%.1f' % (f['share_lt45']*100, f['share_lt70']*100),
          '%.4f/%.4f' % (d['p_flag_given_lt45'], d['p_flag_given_gt70']),
          '%.3f' % (nf['share_lt45']*100), '%.1f' % nf['hap_median'],
          d['flag_ticks_by_need'])
"
```
