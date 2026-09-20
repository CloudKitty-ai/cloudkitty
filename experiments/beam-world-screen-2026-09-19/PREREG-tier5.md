# Beam-world screen, tier 5: shallow ground sleep, floors 10 / 15 / 20 / 25 — prereg, 2026-09-20

Declared before the engine change lands and before any leg runs.
Owner's word 2026-09-20: "Shallow ground sounds good. Let's try
10/15/20/25." The world law is Product's to build
(`HANDOVER-product-shallow-ground-2026-09-20.md`); this file fixes what
Experiments runs on it and what counts as the answer. The config key is
written here as `actions.sleep_floor_off_beam` and follows Product's
name when the spec lands; nothing else in this file depends on the
name.

## The question

Tier 2 showed β 0.04 PPO removes beam seeking the corpus put into the
clone, and the addendum showed why: for a mind that naps at need 7–9, a
beam changes nothing about a nap. Under shallow ground a ground nap
leaves the need at the floor and only a beam clears it, so the tile
changes every nap's outcome. Does beam seeking then survive the
fine-tune, and at which floor?

## Worlds

`package.toml` (tier 2's world: floor-3 off-beam rate, beam 7, six
beams, lifetime 3,000) with the one new key at 10, 15, 20, 25:
`shallow-10.toml` … `shallow-25.toml`, derived by `derive_configs`
extended with the key (guard `test_derive_configs.py` extended: exactly
the package keys plus this one moved), SHA-256s appended here at
derivation.

## Arms (eight, `trainer/train_ppo_beam.py` extended)

| slot | floor | init | β | seed | run index |
|---|---|---|---|---|---|
| sg10-s1 / sg10-s2 | 10 | pkg-vocab | 0.04 | 1 / 2 | 45 / 46 |
| sg15-s1 / sg15-s2 | 15 | pkg-vocab | 0.04 | 1 / 2 | 47 / 48 |
| sg20-s1 / sg20-s2 | 20 | pkg-vocab | 0.04 | 1 / 2 | 49 / 50 |
| sg25-s1 / sg25-s2 | 25 | pkg-vocab | 0.04 | 1 / 2 | 51 / 52 |

The init is tier 2's package clone (placement 0.511 before PPO; bars
PASS). No new corpus: the teacher's beam walk is reach-gated and does
not read relief, so its rows would not change, and reusing the clone
isolates the world change, the beam-price screen's design. Critic: the
B3 critic, reused as tier 2 did. Episode seed bands = run index × 20M +
100M: **1,000,000,000–1,159,999,999** (ledger row added). Everything
else the shakeout trainer verbatim: all-policy, 12 worlds, plateau and
welfare stop rules, probes every 50 updates on the arm's own world,
the 20M cap, Part A at probe 1. Eight arms at 2 threads under `nice`
and `caffeinate`, one night.

## Reads

Per floor: the scripted teacher and gen1-A on the floor world (tier 1's
legs, 30 × 20k, the comparators and the world's own welfare under the
floor), then per arm the tier 2 swap legs (the arm into each gen1-A
seat, 30 × 20k) and the all-arm roster. Measures: placement and tick
share (the arm's own seat), warm share, welfare (happiness, Nash,
distress ages and crossings by name), sleep share, nap length on and
off beams, start-need bins, and meow rates per kind (`want_sleep`,
`here_sunbeam`) from the message head, read the way tier 1's meow
census was.

## Predictions

1. **The floor is felt.** On each floor world the teacher's and
   gen1-A's off-beam naps run longer than 6 ticks (the early end waits
   for the reachable floor as the handover asks) and mean sleep need
   at nap start rises with the floor; gen1-A happiness on the floor
   world drops by more than 0.3 at floor 20 and above (ground sleepers
   stay a little tired), which is the price the arms are trained to
   escape.
2. **Beam seeking survives where the floor bites.** Swap-leg placement
   in the arm's own seat ≥ 0.15 on both seeds at floor 20 and 25; the
   probe series stays above 0.30 through the leash's relaxation
   (2.5–4.6 M ticks, where tier 2's arms lost it). At floor 10 the
   floor sits under the minds' own start need and placement ends under
   0.10 like tier 2's; floor 15 is the unpredicted middle.
3. **The arms are happier than the frozen minds on the same floor
   world**, by at least the happiness the floor took from gen1-A in
   prediction 1, with Nash at or above gen1-A's.
4. **Meows.** `want_sleep` per 1k cat-ticks rises with the floor on
   every seating and jumps between 15 and 20 (the announce threshold);
   `here_sunbeam` replies follow. Reported, no line.
5. **No farming, no new distress.** Start-need bins move up, not down;
   crossings by name.

## Decision rules

- Prediction 2 holding at floor 20 or 25 is the finding: the beam
  matters to a mind once the tile changes the nap's outcome, and the
  Gen 2 world gets a floor (which one is the owner's, read against
  predictions 1, 3 and 4). It goes to #390 and the Gen 2 shelf, with a
  teacher re-record under rule 9 before the Gen 2 collection.
- Prediction 2 failing at every floor means the mechanism is not the
  one this tier names; the two shelved laws (a tiredness gate, restless
  ground) come back to the owner.
- Nothing here deploys; the served world keeps floor 0.

## Doctrine check

Rule 2 (prices are physics): a colder ground is a state of the world;
no reward term (rule 1). Rule 4: sleeping on a beam when rested gains
nothing under a floor; the farming read is declared. Rule 7: the world
that values beam sleep is built before the behaviour is asked for.
Rule 8: at floors ≥ 20 the want channel carries a real fact (where rest
is); read, not scripted (rule 6). Rule 9: the arms are retrained; the
teacher re-record is owed before Gen 2, not before this screen (the
teacher's rows do not read relief). Rule 10: placement lines are on 30
× 20k pooled over five seatings; welfare reads are against gen1-A on
the same world and seeds.

## Floor worlds, derived 2026-09-20 (key `actions.sleep_floor_off_beam`, pinned by spec 056 D2)

- shallow-10 `fb0db42bef389f865db244b3d6695d39bf0e9a2840537419409ee72d5afb2e15`
- shallow-15 `40951d94f765b7f71329525a4792f59fc4e04c4c89a53d760421699d34710bc1`
- shallow-20 `6f680de37e802b9240129bb87d4d8de1f11b398bc25c5ad1aace6fee2d72be7a`
- shallow-25 `a025f8d03e10d626ba4dc6b55e244e930556b894c57a55da064cd6bb92466c03`
