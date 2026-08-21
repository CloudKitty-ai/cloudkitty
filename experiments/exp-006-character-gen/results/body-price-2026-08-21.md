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

## CORRECTION AND COMPLETION (same day): there is no body tax —
## there is a character price, and the body is an expression knob

The table above was missing the one controller that defines the
character: `playful` behavior itself (the demonstration generator).
Measured at Biscuit on both configs (engine-native, 5 seeds × 20k;
single-seed activity/need profiles traced):

| controller | playful body | flat body |
|---|---|---|
| playful behavior (THE CHARACTER) | **79.72** | **79.57** |
| scripted needs_driven | 90.64 | 90.86 |
| e004 / attn (policy) | 94.88 / 95.67 | 94.67 / 95.52 |
| clone (learned Biscuit) | 80.43 | 91.82 |

Every native controller is body-invariant. The character pays a
constant **~11-point lifestyle price in any body**: playful behavior
is opportunity-gated (plays when comfortable and something chaseable
exists), keeps play over-serviced 3× (need mean 2.5–4.6, play 21–22%
of all ticks in BOTH bodies) and lets eat/drink/sleep sit at 25–29.
needs_driven in the same playful body plays 4% of ticks, 65%
partnered (full 20/tick relief), and holds every need at 6–11 — a
closed-loop allocator services a doubled play rate almost for free.
The playful-body reading matches the banked collection-world anchor
(79.64) across worlds.

The clone is the ONLY body-sensitive mind, and that sensitivity is
now legible as **character expression, not body cost**: in the
playful body it inhabits the demonstration distribution and IS
Biscuit (80.43 ≈ 79.72, need profile matching); in the flat body the
demo-sparse low-play states let it drift thermostat-ward (plays 7%,
reads 91.82 — cheap because diluted). The −11.39 recorded above as
"body tax" is the expression delta. Consequences:

- **The differential-body-tax bar arithmetic above dissolves** —
  there is no body tax to adjust for. The real object is the
  exchange LINE from full character (79.7, dose ∞) to no character
  (94.9, e004): the owner's price picks a point. Measured points:
  clone 80.4 · L-04-s1 88.2 (G3-grade venue) · L-05s 88.8–89.2 ·
  L-04-s2 90.4 (0.7× venue) · e004 94.9.
- **The A-floor (scripted parity 90.64) is anchored to a
  non-character controller.** Parity with the character's own native
  expression is 79.7, which everything clears. The floor question is
  therefore really "how much needs-thermostat must Biscuit's mind
  contain" — a sanctuary-values question, now cleanly posed.
- **The two-sheet world was measuring diluted character** — the old
  G2d readings (−0.85) priced a half-expressed Biscuit; the
  certification world evokes the full one. And the fingerprint
  subj-hap column's 4/4 rank prediction is explained: both
  instruments measure expression level.
- PPO under the leash is an interpolation machine on this line:
  welfare pulls thermostat-ward, KL pulls Biscuit-ward, dose sets
  the mix, and the G3 venue floors pin the expensive end (solo and
  critter play relieve at half the partnered rate, so the
  character's signature venue costs double the time per unit
  relief). Register-note candidate: a trait body is an expression
  knob for imitation-learned minds, not a cost knob; character
  price is controller-constant and body-invariant.

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
