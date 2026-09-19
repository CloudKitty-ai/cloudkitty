# Beam-world screen: sleep relief, beam relief, beam lifetime, beam count — prereg, 2026-09-19

Declared before collection. Owner's word 2026-09-19 ("Start tier 1"):
while Gen 2 is hashed out, sweep the world laws the beam package moves
and read how they change beam sleep on the served composition. Two
seatings run on every variant: the scripted roster (the `needs_driven`
teacher at four seats, `playful` at Biscuit's, as `anchor-b3.toml`
seats them) and the frozen Gen 1 roster (gen1-A, the five served
artifacts). Report-only for the frozen minds; the teacher's numbers are
the corpus read the Gen 2 collection was going to make anyway (the
owner agreed 2026-09-19 that the teacher's in-beam share on the new
corpus is read before any training). F-042, F-043, F-045, F-047 are the
findings this rests on.

## What can and cannot move

The scripted teacher walks to the priced-nearest beam whenever the walk
costs `sunbeam_reach` (8) or less and naps on the spot otherwise
(`selection.rs` `sunbeam_worth_walking`); the relief numbers never enter
that choice. The frozen minds cannot re-learn a price (doctrine rule 9).
So on both seatings, lifetime and count are the levers that can move
placement, and the two relief knobs can move only nap length, need
levels and welfare, and placement through those indirectly. This is
stated up front so the relief half of the grid is read for what it
can show.

## Variants

`derive_configs.py`: `fog-gen1-cert/anchor-b3.toml` with exactly five
keys moved and nothing else (guard `test_derive_configs.py`):

| key | anchor | levels |
|---|---|---|
| `actions.sleep_relief` (off-beam) | 5.0 | 5.0, 3.0 |
| `actions.sleep_relief_sunbeam` | 7.0 | 7.0, 10.0 |
| `elements.sunbeam.ttl` | 300 | 300, 3000 |
| `elements.sunbeam.min` (the count the world holds) | 4 | 5, 6, 7 |
| `elements.sunbeam.max` (inert for the world) | 5 | min + 1 |

2 × 2 × 2 × 3 = 24 variants, named `s{sleep}-b{beam}-t{ttl}-n{count}`,
written to `results-raw/configs/` (uncommitted; SHA-256 list appended
below once derived). The anchor itself (count 4, ttl 300, 5 / 7) is the
reference and already has both seatings on the same band in
`fog-gen1-cert/results-raw/battery/` (`scripted-eval-30x20000.jsonl`,
`gen1-A-c0-eval-30x20000.jsonl`); those legs predate the beam block, so
the anchor is re-run here for the beam numbers. 25 configs.

## Runs

`fog-gen1-cert/cert_harness_fog.py SEATING eval --config VARIANT`, 30
seeds × 20,000 ticks, served clock (clock input pinned to 0, the
deployed condition), 6 workers, one out-dir per variant
(`run_screen.sh`). Seeds 870001–870030, the shared eval band of the
battery convention; the same 30 seeds in every variant and seating by
design (paired reads), no new band claimed. 50 legs, about 3 minutes
each on this machine.

## Measures (the harness's `beam` block, added 2026-09-19; guard `test_beam_metrics.py` on a recorded payload)

Per seat and pooled over the roster, summed over seeds:

- **in-beam share** = ticks asleep on a beam tile / ticks asleep. The
  headline.
- **conducted share** = ticks asleep off-beam beside a direct partner
  who is on a beam / ticks asleep (the spec-031 case, read from the
  state's partner slot without the engine's settled check, so an upper
  bound on conduction).
- **start distance** = Chebyshev distance from a sleep start's tile to
  the nearest beam in the world, bins 0 / 1 / 2 / 3-or-more, shares of
  starts. The F-047 read used the nearest *visible* beam; this one is
  the world's, so the two are not the same number.
- **start need** = the sleep need at a sleep start, binned < 5, 5–10,
  10–20, 20–40, ≥ 40 (shares of starts), and its mean. The rule 4 read
  is a shift of this distribution toward the low bins between variants
  of the same seating, not an absolute threshold: the roster keeps its
  needs low (live means 5–7) and starts naps early by habit, so a
  fixed line would count ordinary naps as farming (seen in the 400-tick
  smoke, where nearly every start sat under 20).
- **sleep share** = ticks asleep / ticks (nap length under a slower
  floor).
- Welfare, verbatim from the harness: mean happiness per seat,
  `nash_state`, `low_share`, `floor_touches`, `max_distress_age`.

Reader `screen_read.py` (written while the legs run; the measures and
rules are fixed here) tabulates every variant against the anchor.

## Predictions

1. **Teacher placement follows lifetime and count, not relief.** The
   scripted roster's pooled in-beam share rises from ttl 300 to 3000
   at every count, and from 5 to 7 beams at every lifetime; between
   the two relief levels at fixed ttl and count it moves by less than
   0.03. Direction of size: ttl > count.
2. **The package corner clears the corpus bar.** At s3-b7-t3000-n6 the
   teacher's pooled in-beam share is at or above 0.40 (the bar the
   owner agreed to pin for the pre-training corpus read). If it is
   under 0.40 there, count 7 or a longer lifetime is the fix before the
   Gen 2 collection, and this screen says which.
3. **The frozen minds move less than the teacher, and only with
   lifetime and count.** gen1-A's pooled in-beam share stays under
   0.15 on every variant (anchor 0.04–0.05); its relief-only contrasts
   move by less than 0.02. Rule 9 in numbers.
4. **Floor 3 costs welfare on the frozen roster but crosses no line.**
   With `sleep_relief` 3 the gen1-A roster mean happiness drops by
   under 1.5 points against the same variant at 5, sleep share rises
   (about 1.5× on off-beam naps), and no seed reaches distress age 150
   (F-043's line).
5. **Farming does not appear.** On each seating, no variant's share of
   starts under sleep need 5 exceeds the anchor's by more than 10
   points, and the mean start need moves by less than 5; a variant past
   either is flagged for the rule 4 discussion on #390. The frozen
   minds cannot learn to farm here (rule 9), so the reading that
   matters is the teacher's, and the teacher's nap trigger is a need
   threshold, so the prediction is that neither seating moves.

## Decision rules

- Prediction 2 decides the count question the owner has open on #390
  only in the negative: a corpus under 0.40 at count 6 with the package
  moves the count or the lifetime; at or above it, the count stays her
  visual call.
- A frozen-roster seed with distress age ≥ 150 on any variant is
  reported by name (variant, seat, seed) and the variant is marked; it
  does not stop the screen.
- Nothing here changes the served world; deploying any of it is the
  owner's word.

## Doctrine check (DESIGN-DOCTRINE.md)

- Rule 2 (prices are physics): the four knobs are states of the world,
  which is why the package exists; the screen reads them as such.
- Rule 4 (unfarmable first): the farming share is declared and read
  before any charm reading.
- Rule 9 (frozen models cannot answer a reprice): the frozen-mind half
  is report-only; the teacher half is the corpus read. No number here
  is a claim about what a Gen 2 clone will learn.
- Rule 10 (two-layer welfare gates, noise is never a bar): the 0.40 bar
  is a corpus-content bar on the teacher's own behaviour, not a welfare
  reading.
- Rules 1, 3, 5, 6, 7, 8: checked, moved nothing.

## Not in this screen

Whether a clone learns to seek beams under floor 3 (tier 2: re-record,
clone, PPO); anything on the Gen 2 observation; the client's sky.

## Derived config SHA-256 (results-raw/configs/, uncommitted; the anchor copied there as `s5-b7-t300-n4.toml`)

- anchor `782f969065541b3083923c1fac526f9574b592e34846246ac95a928db599c8ff`
- s5-b7-t300-n5 `b39b02c2692538db95f78ac7075c9d337877efe8a6653275ca69540a1e2bde34`
- s5-b7-t300-n6 `162aa3c42397425152714a68d36077abc9f7a5846a98599c95262aa31770a37d`
- s5-b7-t300-n7 `04c01065cd9d82c3c0191418663440e9bb1134a4b01b6cf8faa6461abac9fdda`
- s5-b7-t3000-n5 `388703a2a7329b28427b4a8bb46dc6bdc1e9d05af241c5a3638131acc07692bc`
- s5-b7-t3000-n6 `4f7cb1420379305593ba4e20ac096dcc2e8ef7e22c782a4600129208d21e4196`
- s5-b7-t3000-n7 `2f27232e3c62e42013170f79dd6535a59560ddafbfdb8cf7c968bbac478b5532`
- s5-b10-t300-n5 `857ff0c34055c63e985949d5f062c2c1cc31fe5759ab614c279c6d33aba4a16e`
- s5-b10-t300-n6 `37cfabdc4c76ca862f9e632aec61f679d8a32e3d1b27df96825d47156766034c`
- s5-b10-t300-n7 `268983d787c6f2ed23a3b69a801d16e8b7fc2166b81f3836b1a8910cb828581d`
- s5-b10-t3000-n5 `143e4c7c1c1d76641e9adaea1e366b164cf8a7d124fe46a53d0b8b3cc9e0a63a`
- s5-b10-t3000-n6 `185b5b95dde800aa763f8baa5b50c9bba12db72c1695399ec9083edd64675552`
- s5-b10-t3000-n7 `4bfae5f07f0b5680fbae098a9e6cdfb575e505ce8d0d290c76dc9cb5e8fb795c`
- s3-b7-t300-n5 `0e8b8dc69d90acf8cffed93c7b91d48e56a39f9c1f91315523f1b569566b65f4`
- s3-b7-t300-n6 `0dd0d1629f793265558b13daac28ad6b2a8cfc366a2ae0ecc42de6eb4c6218f8`
- s3-b7-t300-n7 `aef7ff23d711a17051753bd9372ef6e939eb014ab2265ff18ef17fe5bb13ab22`
- s3-b7-t3000-n5 `0f482ac4f0b39467d942f12782ea1c6df3d4ce4ae2d136a6f9139a18486c9c18`
- s3-b7-t3000-n6 `7c33560a900e2a73a31252e7df901d0fc10d4987bd825bec6fb4446abfef41b5`
- s3-b7-t3000-n7 `a4c58e668447134518aec8fcb06cbd1a037ef536ff86634d897b1157d058fe4e`
- s3-b10-t300-n5 `6a54bd7291cf8357d03578a103e1130d6b2a86888192b84a8523af1dd86a1dcc`
- s3-b10-t300-n6 `7a8c706b92ef8cd80d014e670f3bc5a65cf6c400d83f342ac854c407143df9ac`
- s3-b10-t300-n7 `a7e29d0f12f3233d0395befc636be98c8c0fe673f353d0f7ddb4b41925ca495e`
- s3-b10-t3000-n5 `db9e4152d7ccc6b8d2f99c87ba650a9c450e6573502f1fce5b4712dc849d96c7`
- s3-b10-t3000-n6 `4f4f5984981507d447e2bfe4bf3fab5da5d11eb78e26d6629af8ae403d689ed8`
- s3-b10-t3000-n7 `8044ffda979b1683de6028894d8fac19a003ab611097032768b651d7bfc854fb`
