# Chase/catch census: critter play economics (spec input, per-target play relief)

**Date**: 2026-08-02 · **Engine**: main @ `6d955ab` · **Tool**:
`experiments/tools/twin-probe/src/bin/chase-census.rs` (pursuits and
catches read from the engine's own tick records) · **Runs**: 10 seeds
× 20k ticks each on the exp-002 family base and the served
`cloudkitty.toml` (numbers agree; family-base values quoted).

Input to the owner-proposed per-target play-relief split
(solo < cat < bug < greeble; candidate values 10 / 20 / 25 / 35) and
its registered guards.

## Measured difficulty

| Chaser | Target | chase-ticks/catch | catch rate | play-scene mean len |
|---|---|---|---|---|
| needs_driven | bug | 5.9 | 38% | 1.6 |
| needs_driven | greeble | **9.0** | 26% | 1.4 |
| playful | bug | 2.4 | 77% | 3.2 |
| playful | greeble | **6.9** | 43% | 2.1 |

- **Greebles are 1.5× (needs_driven) to 2.9× (playful) harder per
  catch than bugs**, and 4× scarcer on the field (mean 1.0 vs 4.0 —
  finding one costs travel on top).
- Duets: abundant (needs_driven 18.0k starts / playful 6.6k over 200k
  ticks), mean scene 2.6–4.3 ticks.
- **Solo play never occurs in scripted worlds** (0 starts, both
  behaviors, both worlds — the ladder always finds a real target), so
  `solo_play_relief = 10` only shapes learner edge cases. Free to set.

## Expected value per invested tick (candidate values 10/20/25/35)

EV = catch-rate-adjusted relief per (chase + scene) tick:

| Path | EV/tick |
|---|---|
| duet (cat 20, both parties, once engaged) | 20 self / **40 team** |
| bug hunt, playful skill | ≈ 14 |
| solo (always available) | 10 |
| greeble hunt, playful skill | ≈ 8 |
| bug hunt, needs_driven skill | ≈ 5 |
| greeble hunt, needs_driven skill | ≈ 5 |

Three consequences, all favorable to the proposal:

1. **No grind exploit.** At greeble = 35 the chase overhead keeps
   greeble EV *below* bugs and duets for every measured skill level —
   the jackpot is a thrill, not a strategy. (EV parity with bugs for
   a playful-skill chaser would need greeble ≈ 70, which the 2×cat
   guard forbids anyway. The guard and the measured difficulty agree
   with each other.)
2. **The temptation is real but in-the-moment**: during a scene the
   greeble pays 35/tick vs the duet's 20/tick — a genuine short-term
   defection lure — while EV over the whole hunt still favors social
   play. Exactly the social-dilemma shape wanted: myopic deciders
   defect, far-sighted ones cooperate.
3. **Duets stay team-optimal with margin** (40 team vs any critter
   path), so WantPlay recruitment *gains* value under the split.

## Recommended spec numbers (Experiments' input; Product owns the spec)

```
solo_play_relief    = 10   # last resort (owner), never taken by scripted cats
play_relief_kitty   = 20   # unchanged from today's play_relief
play_relief_bug     = 25
play_relief_greeble = 35
```

Executable guards to register in the spec (spec-020-style validation):
- ordering: `solo < kitty < bug < greeble`;
- ceiling: `greeble < 2 × kitty` (team-optimality of the duet — cross
  it and cats *should* ignore each other; the meow economy dies).

Post-change checks (Experiments runs them, ~1 hr total): probe
re-verification + class probe (prediction: play/chase class rises off
its 0.1× floor — the falsifiable point of the change), dial-rule
anchors, family regen, dataset v2 recollection, welfare bounds.

## Post-025 re-check (2026-08-03, engine `0fd551d`)

Re-run after the split landed with the proposed values (10/20/25/35,
spec 025). Scripted cadence held within trajectory noise —
needs_driven 6.2/8.2 chase-ticks/catch (bug/greeble, was 5.9/9.0),
playful 2.4/7.1 (was 2.4/6.9), duet starts within 1%, solo play
still zero starts in 400k world-ticks — confirming the registered
fact that no behavior-layer code reads relief magnitudes. The EV
table above therefore still describes the shipped economy; the
guards (ordering, greeble < 2×kitty) are live in `validate_actions`.

## Reproduce

```
cargo build --release --manifest-path experiments/tools/twin-probe/Cargo.toml
./experiments/tools/twin-probe/target/release/chase-census \
  experiments/exp-002-mixed-population/family/base.toml 20000 1,2,3,4,5,6,7,8,9,10
./experiments/tools/twin-probe/target/release/chase-census cloudkitty.toml 20000 1,2,3,4,5,6,7,8,9,10
```
