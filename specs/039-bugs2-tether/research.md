# Research: Bugs 2.0 — the roam-cell tether

Seven decisions. Each names its in-repo precedent; nothing here is
novel machinery.

## D1 — The partition is integer division; ragged edges are free

**Decision**: A tile's cell is `(x / N, y / N)` with the world origin
as anchor. Two positions share a cell iff both quotient pairs match.

**Rationale**: This single arithmetic fact delivers every geometry
requirement at once. On 20×20 with N=4 it yields exactly the 25 clean
cells the owner adopted. On 26×26 the far columns (x = 24, 25) and
rows (y = 24, 25) form quotient-index-6 strips automatically — the
4×2, 2×4, and 2×2 remainder cells of US2, with no edge-case code. A
world smaller than N in a dimension puts every tile at quotient 0:
one cell, US2 scenario 3, also free. Every tile has exactly one
quotient pair, so "every tile in exactly one cell" is not a property
to test into existence, only to document (the test asserts it anyway,
cheaply, because rule 6 does not take arithmetic's word for it).

**Alternatives considered**: an anchor-at-spawn radius tether needs a
persisted anchor field on `Element` (snapshot surgery, migration
questions, FR-007 violated); a centered/floating cell breaks
statelessness the same way. Both rejected in the brainstorm and by
the owner's "4x4 grid" framing.

## D2 — The check rides the Bug arm, after the direction draw

**Decision**: In `move_critters` (world.rs), the `ElementKind::Bug`
arm draws its direction exactly as today, computes the destination,
and skips the step when the destination's cell differs from the
current cell — before/instead of the occupancy walk in
`try_step_element`. Greebles' arm is untouched.

**Rationale**: FR-003 requires the outward draw to be a *lost step,
never a redraw*, and FR-009 requires draw-count preservation. Placing
the check after the same single `rng.choose` call preserves the
stream shape exactly: one draw per moving bug per moving tick,
tether or no tether. Putting the constraint inside `try_step_element`
would thread a bug-only concern through a helper greebles share —
spec 024's blocked-chase comment records the house preference for
keeping per-kind rules at the call site that owns them.

**Alternatives considered**: filtering the direction set before the
draw (changes draw distribution and, at corners, draw counts —
violates FR-003's "never compensated"); a generic constraint
parameter on `try_step_element` (speculative generality, CLAUDE.md
rule 2 — nothing else needs it).

## D3 — `roam_cell: Option<u32>` on `ElementRule`, honored for bugs, refused elsewhere

**Decision**: The config field lives on `ElementRule` (the per-type
table all five elements share), `#[serde(default)]`, absent = `None`
= unbounded. It is *honored* only in the Bug arm and *refused* by
validation when set on any other element type, with the field and
value named.

**Rationale**: `servings: Option<u32>` ("Chow only") is the exact
precedent for a per-type optional on the shared rule struct. It is,
however, silently ignored on non-chow types — pre-strictness-era
behavior. Since PR #114 the config culture refuses what it will not
honor (`deny_unknown_fields`; spec 034's refuse-rowless FR-007), so
`roam_cell` on a greeble or sunbeam is a load-time error, not a
no-op: a config line that does nothing is a lie waiting to be
believed. The divergence from the `servings` precedent is deliberate
and this paragraph is its record.

**Validation bounds**: `Some(0)` and `Some(1)` are refused (a 1-cell
tether silently immobilizes every bug — spec US3 scenario 3);
`Some(n) for n ≥ 2` is legal, including n larger than the world
(US2 scenario 3 makes it well-defined). Precedent for the refusal
shape: the existing `ttl = 0` refusal in validate.rs, which names
the field and value.

## D4 — Lifetimes change in the served toml only; engine defaults untouched

**Decision**: `cloudkitty.toml` sets `[elements.bug] ttl = 600` and
`[elements.greeble] ttl = 600` (owner's symmetry ruling, 2026-08-21).
The engine `Default` impl keeps `Some(300)` for both.

**Rationale**: The served world is configured by its toml, not by
engine defaults; the phase-1 cutover just re-established this
pattern (the certification config carried every world value
explicitly). Changing the Default impl would move
`engine_defaults_sha256` and force baseline re-derivations for no
behavioral gain — the stamp is a compatibility axis, not a tuning
surface.

## D5 — Stamp neutrality via `skip_serializing_if`, guarded by the existing stamp test

**Decision**: The new field is declared
`#[serde(default, skip_serializing_if = "Option::is_none")]` so the
default Config's JSON serialization — which `engine_defaults_sha256`
hashes (config/mod.rs:91) — is byte-identical before and after this
change.

**Rationale**: `ElementRule.ttl` today has no `skip_serializing_if`,
so the default JSON already carries its keys; *adding* a field
without skip would add `roam_cell` keys to that JSON and move the
stamp ([stamp] marker, baselines re-derive) for a field that is None
everywhere in the defaults. Skip-if-none makes the addition
invisible to the hash. **Rule 6 verification comes free**: the
existing stamp test (config/mod.rs ~2119) pins the hash — declare
the field wrong and that test goes red; it is the assertion aimed at
exactly this line.

## D6 — Inertness is proven by a golden evolution digest generated on main

**Decision**: SC-002's "identical to the pre-change engine" is
operationalized as a pinned constant: on current `main` (87236c5,
the phase-1 merge), run a seeded world (tether unconfigured) for
10,000 ticks and record a digest of the final world state; the
branch asserts the same run reproduces that digest bit-for-bit. The
constant lands in the test with its provenance in a comment.

**Rationale**: A flag-absent code-path argument ("the check is
inside `if let Some`") is inspection, not proof — rule 6 demands the
assertion that fails when neutrality breaks. The pinned-constant
pattern is the house's own: spec 035's `EXPECTED_O4_SHAS` pinned
cross-machine artifact bytes the same way. The digest reuses the
world's serialized snapshot form (already deterministic and stable —
Article V) hashed with sha256; no new digest machinery.

**Alternatives considered**: running both engines in one test
(impossible — the pre-change engine isn't in the build); statistical
similarity (weaker than the spec's "identical"; rejected).

## D7 — CHANGELOG markers: none claimed, and the claim is earned

**Decision**: The Unreleased entry carries no compatibility markers.
Prose states what was proven neutral: fingerprint unmoved (FR-007 —
w/h/seed/kitty-ids only, verified at the phase-1 cutover), stamp
unmoved (D5, test-pinned), no schema movement, flag-absent evolution
byte-identical (D6, test-pinned). The served ttl/tether values change
the served world's *future*, which the entry says in words — that is
a world-content change, not a compatibility break; existing saves
load and continue (mid-life adoption, spec edge case).

**Rationale**: changelog practice records "a MISSING marker is a
claim — call out changes proven neutral." D5 and D6 are the proofs;
the entry cites them rather than hedging with markers that would
falsely promise breakage.

## Precedent notes for the implementer

- `bug_moves_this_tick` (element.rs:126) is untouched — cadence is
  the schedule's job, the tether is the destination's.
- The occupancy rule in `try_step_element` (world.rs:807) is
  untouched — boundary loss and occupancy loss are the same *kind*
  of outcome reached by different judges, and the cadence test
  counts them together against the attempt schedule.
- Experiments' census tool patch (expiry-abandon tagging) is landed
  and verified at e39079e on their side; the acceptance grid is
  runnable against any build of this branch — no tooling wait.
