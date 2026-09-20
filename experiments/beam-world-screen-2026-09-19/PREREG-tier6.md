# Beam-world screen, tier 6: beam count 5 / 6 / 7 / 8 under floor 15 — prereg, 2026-09-20

Declared before any leg runs. Owner's word 2026-09-20: "Let's screen
count 5,6,7,8", after ruling the Gen 2 floor at 15 (#390) and flagging
that under a floor the welfare curve becomes a function of beam density
(GEN2-INPUTS shelf). This tier reads that curve for the count knob, so
#390 (c) is ruled on numbers rather than on placement alone.

## The question

At floor 0, count moved the teacher's placement and nothing else (tier
1: frozen minds ignored count and relief). Under floor 15 full sleep
relief needs beam access, so count should now set welfare for a mind
that uses beams and still move nothing for one that does not. How much
welfare does each extra beam buy a learned mind, where does the gain go
flat, and does a mind trained at one count carry across counts without
retraining?

## Worlds

The package world at floor 15 (`shallow-15.toml`, count 6) with the
count moved to 5, 7 and 8: `count-5.toml`, `count-7.toml`,
`count-8.toml`, derived by `derive_configs.derive(anchor, 3.0, 7.0,
3000, n, 15)` (the `max` key follows at n+1, inert). Committed with
these SHA-256s; the trainer checks its derivation against them:

- count-5 `666fa01b8373320a846400aefe9d9285e4bef4412538e3cf1d9e2936d13e4900`
- count-7 `8a5b30e843eb414247b9aeb58a642295b08de97ce1684c9e1208cc35c4f5e0f9`
- count-8 `80e9143682c3074c21eafc78296a50eca6be698ea37ac50a7391557927fd8c3d`
- count 6 = `shallow-15` `40951d94f765b7f71329525a4792f59fc4e04c4c89a53d760421699d34710bc1` (PREREG-tier5)

## Arms (six new, `trainer/train_ppo_beam.py` extended)

| slot | count | init | β | seed | run index |
|---|---|---|---|---|---|
| cnt5-s1 / cnt5-s2 | 5 | pkg-vocab | 0.04 | 1 / 2 | 53 / 54 |
| cnt7-s1 / cnt7-s2 | 7 | pkg-vocab | 0.04 | 1 / 2 | 55 / 56 |
| cnt8-s1 / cnt8-s2 | 8 | pkg-vocab | 0.04 | 1 / 2 | 57 / 58 |

Count 6 is tier 5's sg15-s1 / sg15-s2 (run indices 47 / 48), reused as
trained; their swap legs and all-arm roster on `shallow-15` are tier 5's
files. Everything else as tier 5: the package clone init (no new
corpus, the teacher's walk does not read count beyond its reach gate),
the B3 critic, the shakeout trainer verbatim, plateau and welfare stop
rules, the 20M cap. Episode seed bands = run index × 20M + 100M:
**1,160,000,000–1,279,999,999** (ledger row added). Six arms at 2
threads under `nice` and `caffeinate`, one night.

## Reads

Per count: the scripted teacher and gen1-A on the count world (30 ×
20k; count 6 from tier 5), each new arm into each gen1-A seat (five
swap legs, 30 × 20k) and the all-arm roster, the measures tier 5 read
(placement, tick share, warm share, conducted, happiness, Nash, sleep
share, start-need bins, distress ages and crossings by name, meow
rates). Plus a **transfer read** that costs no training: the count-6
arms (sg15-s1 / s2) seated all-arm on the count-5, 7 and 8 worlds, 30 ×
20k, read beside the retrained arms on the same worlds.

## Predictions

1. **Welfare rises with count for a learned mind, and the gain
   shrinks.** All-arm happiness orders 5 < 6 < 7 < 8 on both seeds; the
   5→6 gain exceeds the 7→8 gain; count 8 sits within 1.0 of the
   floor-0 all-arm level (91.9–92.3) and count 5 more than 1.5 under
   it. Nash orders the same way.
2. **Frozen minds do not feel the count.** gen1-A happiness across the
   four count worlds spans under 0.3 (they nap into the floor on any
   tile; tier 1's flatness carries into the floored world). The teacher's
   placement rises with count (reach-gated walk, tier 1) while its
   happiness stays flat.
3. **Placement rises with count, and no count loses it.** Arm own-seat
   placement ≥ 0.15 on both seeds at every count; the all-arm placement
   orders with count. Conducted cosleep share falls with count (a beam
   of one's own beats a neighbour's).
4. **Transfer holds.** The count-6 arms on the 5 / 7 / 8 worlds land
   within 0.5 happiness and 0.10 placement of the arms retrained there.
   Count is a change in what the policy sees (beam slots), not in what an
   action is worth, so rule 9's "frozen models cannot answer a reprice"
   is not expected to bite; if it does (a gap past both lines on a
   count), that is the finding and future count screens need retraining.
5. **No farming, no new distress.** Start-need bins do not move down;
   all-arm crossings by name reported; distress across counts is read as
   noise unless it orders with count on both seeds.

## Decision rules

- The count is the owner's (#390 (c)), read against prediction 1: the
  line Experiments offers is the smallest count whose gain to the next
  count sits inside the two-seed spread at that count. Prediction 4
  holding means the count can be moved at the Gen 2 collection without a
  new screen; failing means any count change retrains.
- Prediction 2 failing (frozen welfare moving with count) means the
  density effect is not the beam-access mechanism this tier names;
  reported, no rule.
- Nothing deploys; the served world keeps floor 0 and its count.

## Doctrine check

Rule 2: count is a state of the world, no reward term (rule 1). Rule 7:
the world that values the walk (floor 15) is in place; this tier reads
its density. Rule 9: the arms are retrained per count, and the
transfer read tests the boundary of that rule for a knob that changes
observation, not price, declared as prediction 4. Rule 10: two seeds
per count, welfare against gen1-A on the same world and seeds; a gap
inside the seed spread is no ordering.
