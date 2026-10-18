# Contract: the friend-ward drift law

The deterministic selection law the engine implements when
`[behavior] friend_ward_drift = true`. This is the document
Experiments reads to interpret the flag-on arm of the 100×100 A/B;
flag-off behavior is, by FR-002, today's engine bit-for-bit and needs
no contract.

## Definitions

- **Known friend**: another roster member that is (a) visible in the
  cat's fogged snapshot, at its visible position, or (b) unseen but
  audible via a stamp within the digest window whose kind is a
  law-named want or here word, at the stamp's position. Free-register
  kinds, Purr, and WaitForMe never qualify, and a fresher
  non-qualifying meow neither places a friend nor hides that friend's
  older qualifying stamp.
- **Nearest known friend**: the known friend minimizing
  `(manhattan(me, pos), id)`. May be `None`.
- **Gate** `G`: `friend_ward_gate` (default 10, Manhattan tiles).
- **Detour bound** `B`: `friend_ward_detour` (default 4.0, priced-cost
  tiles).
- **Fires**: flag on ∧ nearest known friend exists at distance > `G`.

When the drift does not fire, every site below behaves exactly as
flag-off.

## Site 1 — priced element selection (relief targets)

Applies wherever the shared priced selection chooses among same-kind
relief candidates (elements and sunbeams; score side and walk side are
the same law, so they always agree).

1. Candidates and priced costs are computed exactly as today (visible
   elements plus the remembered slot; fog-era beam occupancy filter
   unchanged).
2. `min_cost` = cheapest candidate's priced cost.
3. Band = candidates with `cost ≤ min_cost + B`, further capped by the
   caller's acceptance bound where one exists (the sunbeam walk's
   `sunbeam_reach`): a candidate failing the bound is never in the
   band. The drift changes WHICH option wins, never WHETHER relief or
   walking happens.
4. Winner = band minimum by
   `(manhattan(candidate_pos, friend_pos), cost, id)`, cost compared
   by `total_cmp`. The fallback `(cost, id)` ordering inside
   friend-distance ties is today's ordering, so the remembered slot
   (id `u32::MAX`) still loses ties to a real sighting.

Consequences pinned: with one candidate, with `B = 0` and distinct
costs, or with every rival outside the band, the winner equals
flag-off's winner. Adjacency use of an element ("use it if adjacent")
precedes selection, unchanged.

## Site 2 — idle potter

When the potter fires (the cadence rule upstream is untouched: same
pressure threshold, same `gen_bool` draw):

- Drift fires ⇒ the action is one step toward the nearest known
  friend's position through the existing step rule (occupied-tile and
  water-avoiding sidesteps); the uniform direction draw is skipped.
- Otherwise ⇒ today's uniform random direction.

## RNG declaration

Flag off: RNG consumption is bit-identical to today's engine. Flag on:
the potter's direction draw is skipped on steered ticks — the flag-on
stream lawfully diverges from flag-off, deterministically per
seed+config (Article V holds in both arms). Seed-paired A/B compares
arms at equal seeds, not equal streams.

## Out of scope (pinned)

The blind lattice-tour search (`explore`), cuddle/playmate/groom
target selection, the heard-unseen helper's existing consumers, and
every ladder rung above target selection: scene continuation,
opportunism, groom response, cue answers, the luxury line.
