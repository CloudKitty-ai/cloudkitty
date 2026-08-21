# Chase census, re-run: critter play economics on the current engine

Owner's ask 2026-08-21 ("if our welfare optimized models aren't even
opportunistically playing with bugs, we've clearly mispriced that
reward"). Instrument: `experiments/tools/twin-probe` `chase-census`
(the 2026-08-02 tool, rebuilt clean against the current engine),
10 seeds × 20k on the certification world — behaviors as configured
(needs_driven ×5) and a Biscuit-playful variant
(`configs/phase1-cutover-playfulbiscuit.toml`) for the skilled-hunter
rows. Raw: `results-raw/chase-census-{needsdriven,playful}.txt`.
Relief semantics verified in `action.rs`: relief lands per tick of
the Playing scene; duets pay BOTH parties per tick.

## Measured difficulty (vs the 2026-08-02 census)

| chaser | target | ticks/catch | catch rate | scene len | 08-02 |
|---|---|---|---|---|---|
| needs_driven | bug | 5.8 | 32.9% | 1.6 | 5.9 / 38% |
| needs_driven | greeble | 8.3 | 23.5% | 1.5 | 9.0 / 26% |
| playful | bug | 2.1 | 77.9% | 3.3 | 2.4 / 77% |
| playful | greeble | 6.2 | 42.2% | 2.1 | 6.9 / 43% |

Field: bug 3.0, greeble 1.0. Solo play: zero starts, both behaviors
(unchanged). **The catch physics survived the wall almost untouched —
the economy did not drift; the optimizer changed.**

## Effective value per invested tick (current stickers 10/20/25/35)

| path | EV/tick |
|---|---|
| duet @ needs_driven | 16.1 self / **32.2 team** |
| **bug @ playful skill** | **15.9** |
| greeble @ playful skill | 12.8 |
| duet @ playful | 12.3 self / 24.7 team |
| solo | 10.0 |
| greeble @ needs_driven skill | 9.1 |
| **bug @ needs_driven skill** | **7.9** |

## Two structural findings

1. **The dominance is the pair-payment, not the price.** For a
   SELF-interested skilled hunter, bugs already sit at duet parity
   (15.9 vs 12.3–16.1 self). What buries them is the team term:
   duets pay both parties, so a team-reward optimizer sees 24.7–32.2
   against the bug's 15.9 — a 1.6–2.0× gap that no plausible sticker
   closes (team parity needs bug ≈ 40–50, at or past the 2×cat guard,
   with grind risk on a 300-tick respawn).
2. **The skill moat: bug-hunting is EV-negative until you are good at
   it.** At unpracticed (needs_driven-grade) catch skill, the bug
   pays 7.9 — BELOW solo's 10. A welfare optimizer exploring from
   zero skill reads bugs as a bad deal on every rollout, so the
   gradient never points toward the practice that would make them a
   good deal. Zero critter play in every E arm and e004 is not a
   preference; it is a local optimum the pricing digs. This also
   explains why the character pays so well for its skill: playful's
   77.9% catch rate is a trained asset the economy never lets a
   welfare-learner acquire.

## The dial, quantified (Experiments' input; the spec and the values
are the owner's)

The owner's target — "optimal models learn to play at least a
little; partnered play predominates, but not quite to this degree" —
translates to: unskilled bug EV must clear solo (the gradient
exists), skilled bug EV should land between self-duet and team-duet
(opportunistic, never dominant). Sticker arithmetic:

- **bug 25 → ~32–35**: unskilled EV 10.1–11.1 (crosses solo),
  skilled EV 20.3–22.2 (between self-duet 12–16 and team-duet
  25–32). The corridor the owner described.
- greeble 35 → ≤ 40 (the 2×cat guard's edge): unskilled 10.4,
  skilled 14.6 — same shape, jackpot stays a thrill.
- Alternatives that move EV without stickers: catch-rate/scene-length
  mechanics (pounce reach, chase patience, bug evasion) — same
  corridor reachable, different feel; a per-chase-tick relief would
  price the hunt itself (new mechanic, spec-first).

Scope: scripted-company census (F-012 — policy-company duet
economics differ; the served world cosleeps and piles far more, so
partner availability is if anything HIGHER in policy company,
strengthening finding 1). Any repricing is a world-economics change:
re-baseline before anything freezes against it (the pre-exp-003
lesson), and it re-prices the Biscuit character tax downstream —
a world where optimal minds hunt a little shrinks the measured
~6.7 full-venue price toward the owner's original −3.0 intuition.
