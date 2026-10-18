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
- **Known-friend set**: every known friend's position (visible, or
  fenced stamp). **Friend key** of a position: min over the set of the
  Manhattan distance to it (ruled 2026-10-17, review 2: keying on THE
  cat's-nearest friend let the key flip as the cat walked).
- **Fires** (per site, ruled 2026-10-17): flag on ∧ the set is
  non-empty ∧ the gate reading exceeds `G` — Site 1 reads the CHEAPEST
  candidate's friend key; Site 2 reads the cat's distance to its
  nearest known friend.
- **Stability invariant**: under fixed knowledge every Site 1 ranking
  input is fixed per candidate — the cheapest-wins state is absorbing
  and a fired target only switches to a strictly better key, so
  walking alone never oscillates the choice. Knowledge changes (a
  friend crossing the vision-disc edge, a stamp expiring) are a
  DECLARED residual the screen prices; at served radius 4 the relief
  gate cannot fire from visible knowledge alone, the 100×100 legs
  (radius 5/6) are exposed.

When the drift does not fire, every site below behaves exactly as
flag-off.

## Site 1 — priced element selection (relief targets)

Applies wherever the shared priced selection chooses among same-kind
relief candidates (elements and sunbeams; score side and walk side are
the same law, so they always agree).

1. Candidates and priced costs are computed exactly as today (visible
   elements plus the remembered slot; fog-era beam occupancy filter
   unchanged).
2. `min_cost` = cheapest candidate's priced cost (ties by id, as
   today). The gate reads here: the cheapest candidate's friend key
   ≤ `G` ⇒ the cheapest wins exactly as flag-off.
3. Band = candidates with `cost ≤ min_cost + B`, further capped by the
   caller's acceptance bound where one exists (the sunbeam walk's
   `sunbeam_reach`): a candidate failing the bound is never in the
   band. The drift changes WHICH option wins, never WHETHER relief or
   walking happens.
4. Winner = band minimum by `(friend key of the candidate, cost, id)`,
   cost compared by `total_cmp`. The fallback `(cost, id)` ordering
   inside key ties is today's ordering, so the remembered slot (id
   `u32::MAX`) still loses ties to a real sighting.

Consequences pinned: with one candidate, with `B = 0` and distinct
costs, or with every rival outside the band, the winner equals
flag-off's winner. Adjacency use of an element ("use it if adjacent")
precedes selection, unchanged.

**Scoring consequence (ruled 2026-10-17, review 1 HIGH-2)**: the
scored side charges the drift winner's REAL priced cost (honest
pricing; the 004/019 score/walk invariants hold exactly). A need's
score therefore sits at most `tile_cost × B` below its flag-off value,
and a near-tie need ordering may flip within that bound. This is the
drift's declared influence on the ladder, priced for the 100×100
screen; nothing above the scored selection moves.

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
