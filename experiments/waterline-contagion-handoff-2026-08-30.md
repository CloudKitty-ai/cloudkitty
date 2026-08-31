# Handoff: waterline contagion enablement (owner-ruled, factor 1.0)
## (2026-08-30, Experiments → Product)

The owner ruled 2026-08-30: the waterline contagion mechanism is IN for
Gen 1 at factor 1.0. This is the engine half; the `KITTY_SLOT`
neighbour-in-water float stays wall-gated and is not part of this ask.
Doctrine and pricing: `ROADMAP.md` §pre-fog schema-break bundle;
`cuddle-economy-model/RESULTS.md` §Post-041 (welfare-benign at every
factor tried up to 1.0; grooming absorbs the charge).

## The mechanism (owner's redesign, 2026-08-26/27)

A dry cat in a partnered scene (all four paired kinds) with an in-water
partner receives the wet-fur charge as if in water:

- charge = `factor × water.bath_gain × bath_ratio(self)` per tick — the
  cat's OWN ratio, mirroring the occupancy charge at `world.rs:894-906`;
- same `bath_gain_ceiling` gate, on the pre-charge value;
- one new config factor, **inert at 0.0** so the launch is
  byte-identical (house pattern); the flip to 1.0 is a config change at
  its own deploy;
- **no wet timer** (owner-ruled): in water = wet, out = dry;
- the dry member only — the wet member already pays occupancy, so no
  cat pays both in one tick and the per-tick worst case is unchanged;
- prices, not prohibitions: nothing touches legality or the refusal
  seam.

## Must ride the same spec

**`validate_water` headroom re-check.** The current budget is stated
occupancy-only. Expected to pass — the dry-member-only rule keeps the
single-tick maximum where it was — but the budget needs re-stating with
contagion in it (ROADMAP's standing spec item, ~2× worst-case exposure
vs the occupancy-only framing).

## Sequencing (owner's, via the ruling)

1. Merge inert at 0.0 whenever ready — safe alongside anything.
2. The FLIP to 1.0 waits for the 041 deploy + soak to complete, then
   goes out as its own deploy with its own G6-style soak. Never the
   same deploy as 041: the post-041 census reads against the pre-041
   baseline and both changes move the groom mix.
3. The here-word density screen must finish collection before the
   factor goes nonzero on any surface it collects from (inert merge is
   harmless to it).

Open at flip time (owner, not blocking this spec): whether the banked
scripted-anchor probe runs first for per-seat tails — needflow priced
at `bath_ratio` 1 while real seats span 0.5–2.0×.

## Acceptance

- Factor 0.0: byte-identical world stream vs pre-merge (018–020
  practice).
- Factor > 0: a dry cat in each of the four paired kinds with an
  in-water partner accrues the charge; gated at the ceiling; a wet cat
  never pays it on top of occupancy.
- `validate_water` re-check green on the served config and both config
  sweeps.
