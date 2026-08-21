# Body-price cells: what the Playful sheet costs each mind class

Owner's B (budget re-derivation), 2026-08-21. Paired cells at the
Biscuit seat: certification world (`phase1-cutover.toml`, sha
`64ca2b9a…`) vs the same world with only Biscuit's sheet removed
(`phase1-cutover-flatbiscuit.toml`, sha `55733bba…`, semantic-diff
verified). Eval band 870001–030 × 20k × 30 seeds per cell. Scripted
cells via kitty-eval (anchor convention); policy cells via
cert_harness6 in each class's natural composition (e004 in reference
company, clone/attn in §6 candidate company). Raw:
`results-raw/bodyprice/`, on-cells for scripted/e004 banked from
`results-raw/d003/`.

## The tax table (Biscuit-seat happiness, body on − off)

| class | body ON | body OFF | tax | worst mda on/off |
|---|---|---|---|---|
| scripted needs_driven | 90.64 | 90.86 | **−0.21** | 0 / 0 |
| e004-a1-s2 (incumbent) | 94.88 | 94.67 | **+0.21** | 8 / 24 |
| **clone-anchor (character, dose ∞)** | **80.43** | 91.82 | **−11.39** | **163** / 55 |
| attn-a1-s1 (generic policy) | 95.67 | 95.52 | +0.15 | 14 / 0 |

## Diagnosis (the owner's model-vs-pricing question, answered)

1. **The sheet's pricing held.** Scripted pays −0.21 for the Playful
   body — the design-time verification read +0.21; both are parity-
   band readings. The exchange table did not drift for the class it
   priced. Mispricing is ruled out.
2. **Welfare-optimized policies are body-insensitive** (e004 +0.21,
   attn +0.15): they absorb a doubled play rise-rate without cost.
   The old-world assumption behind the −3.0 bar was true for them
   and only them.
3. **The character class pays ~11 points.** The clone — pure
   imitation of demonstration Biscuit, the leash's zero point —
   drops 91.82 → 80.43 in the Playful body, with a 163-tick
   constitutional-scale streak in one seed. Imitation reproduces the
   demonstrated play *rate*; needs_driven adapts to the required
   rate. That gap is the tax, and it was invisible to the original
   pricing because this carrier class did not exist when the table
   was built. (Cross-check: the fingerprint world's banked scripted
   playful Biscuit read 79.64 — the collection family also carries
   the Playful body; the instruments agree.)
4. **The L candidates are therefore mid-recovery, not simply
   failing**: from the class zero point 80.43, L-04-s1 recovers +7.8
   while holding G3 venue (88.19); L-04-s2 recovers +9.9 by
   shedding 30% of venue (90.38). PPO buys back most of the
   character tax; the last ~2 points and the venue trade against
   each other.

## Bar arithmetic per fair-tax anchor (character price −3.0 as
declared; A-floor = scripted parity 90.64 underneath)

| anchor | bar | effective (with A-floor) | candidates clearing |
|---|---|---|---|
| e004's tax (status quo) | 94.88 − 3.0 = 91.88 | 91.88 | none (best 90.38) |
| scripted's tax | 94.88 − 0.42 − 3.0 = 91.46 | 91.46 | none |
| clone's tax | 94.88 − 11.60 − 3.0 = 80.28 | **90.64** (floor binds) | none; L-04-s2 −0.26, G3-failing |

Every principled anchor lands the effective bar in a narrow band
[90.64, 91.88], and the generation's G3 passer sits 2.45 below its
bottom. The re-derivation clarifies rather than rescues: **the
tension is not the budget's frame — it is between the G3 venue
definition and any welfare bar at or above scripted parity.** The
measured price of Biscuit on this world: ~6.7 happiness at full
venue (G3-grade), ~4.5 at 0.7× venue. The declared −3.0 was priced
on a world where the incumbent carried no body tax; the character's
actual market price is above it at every measured retention level.

## What this puts in the owner's hands

- Whether −3.0 survives as the character price now that the price
  list is real (a re-affirmation or a re-declaration, either way
  D-numbered);
- whether scripted parity (A) is the floor — noting L-04-s2 misses
  it by 0.26 while failing G3, and the s1↔s2 spread shows the seed
  lottery moves the Biscuit seat by ~2.2 points, so further L-04
  seeds sample a real distribution;
- the character-definition and body dials (G3 venue floors, play
  0.8) remain the levers that move the frontier itself rather than
  the bar. No verdict changes here; everything stays benched.
