# Research: Contagion Membership Dial + Charge-Aware Ladder (spec 045)

All Technical Context unknowns resolved. Sources: the 044 implementation
(merged main 74537e4), `behavior/selection.rs` + `behavior/needs_driven.rs`
(the scripted chooser), `config/mod.rs`, the smoke design doc
(`experiments/edge-avoidance-smoke-design-2026-08-31.md` @ 9d258b6), and
needflow (`cuddle-economy-model/RESULTS.md` §Bidirectional, Experiments'
lane).

## D1 — Where the membership dial lives

**Decision**: `[water] contagion_membership`, a two-variant serde enum
`ContagionMembership { OptionA, Bidirectional }` on `WaterConfig`, TOML
values `"option_a"` / `"bidirectional"`, `#[serde(default,
skip_serializing_if = "ContagionMembership::is_option_a")]`.

**Rationale**: It parameterizes the 044 charge, whose whole surface is
`[water]`; skip-at-default is the house stamp-preservation idiom
(`f32_is_zero` precedent), and `WaterConfig` is `deny_unknown_fields`, so
an explicit-default TOML arm plus a stamp-absence guard prove
byte-identity exactly as 044 did. Enum, not bool: the owner's future
ruling may add variants (e.g. a radius rule), and the two names match the
record's vocabulary.

**Alternatives**: a bool `bidirectional = false` (loses the vocabulary
and forecloses variants); a `[behavior]` home (wrong table — this is
engine law, not chooser preference).

## D2 — The engine branch (who pays)

**Decision**: the branch lives entirely in the `contagious` set
construction in `advance_needs` (`world.rs`). Today's filter admits a dry
cat when its OWN activity names a wet partner AND `is_available_friend`.
Under `bidirectional`, additionally admit a dry cat when some WET cat's
activity names it AND `is_available_friend(wet, dry)` holds. Concretely:
pre-collect `wet_namers: BTreeMap<named_dry_id, wet_id>` from wet cats'
`Activity::partner()`, then extend the existing dry-cat filter with the
membership check. The charge arm, ceiling gate, wet exemption, and
occupancy arm are untouched.

**Rationale**: `contagious` is a `BTreeSet`, so a cat admitted by both
roles (or referenced by two wet cats) appears once — FR-003's
one-charge-per-tick cap falls out of the existing data structure with no
new code. Adjacency reuses the one predicate the owner ruled canonical
(`is_available_friend`, 044 amendment). No new state, no RNG, no
iteration-order sensitivity (BTree everywhere, matching 044's
order-independence note).

**Alternatives**: charging inside the wet cat's own arm (double-visits
the pair and re-opens the both-pay confusion finding 8 closed); a
separate bidirectional set (two sets to keep disjoint for no benefit).

## D3 — The ladder gate

**Decision**: `[behavior] contagion_aware_ladder`, bool, default `false`,
`#[serde(default, skip_serializing_if = "bool_is_false")]` (small helper
beside `f32_is_zero`). When false, every 045 chooser seam returns its
current value untouched — the exposure helper is not called.

**Rationale**: the chooser's dials all live in `[behavior]`
(`urgency_weight`, `tile_cost`, `water_step_cost`, spec-042 weights);
lab configs flip one bool per arm. Gate-off short-circuits BEFORE any
arithmetic so `false` is structurally byte-identical, provable by the
same seeded-run equality test 043 used for its gate.

**Alternatives**: a scalar weight (dose-response is the factor's job —
arm E cranks `contagion_factor`, not the ladder; a second scalar
confounds the smoke); auto-on when factor > 0 (breaks arm B, the
negative control, which needs factor 1.0 with a charge-BLIND ladder).

## D4 — The exposure value shape (scene-total, per the clarification)

**Decision**: one shared helper in `behavior/selection.rs`:

```text
expected_scene_exposure(ctx, kind, partner) =
    Σ over members who would PAY under the active membership rule:
        min( rate(payer) × E_ticks(kind),
             max(0, bath_gain_ceiling − payer.bath) )
where rate(payer) = contagion_factor × bath_gain × bath_ratio(payer)
```

Payer set per membership: `option_a` — the dry namer only (the deciding
cat, iff it is dry and the partner is wet); `bidirectional` — any dry
member of the candidate scene whose counterpart is wet, either role.
The result is subtracted from the candidate's value in score points
(need-pressure units — the same currency `scored()` already mixes with
`tile_cost × distance`).

**Rationale**: this is needflow's shape (charge × expected scene-ticks
against the payer's bath) made deterministic in-engine; the ceiling cap
mirrors the pre-charge gate so the ladder never prices exposure the
engine cannot collect; scene-total is the owner's clarified ruling
(egocentric pricing would make arms C and D choose identically).
`bath_ratio(payer)` uses the payer's own trait ratio — the same per-cat
ratio the charge draws — so the ladder and the felt price stay one
coherent preference (the `bath_ratio` doc's existing principle).

**Experiments review (DONE 2026-08-31)**: scene-total, the ceiling cap,
`bath_ratio` coherence, and the gate-not-auto-on-with-factor all
confirmed as-is; they independently verified the voiding claim (under
both rules the initiator pays iff dry-with-wet-partner, so egocentric C
and D are literally identical — the contrast is 100% the partner's
charge). Three adjustments folded: D5's duration basis (midpoint →
min), D6 site 3's value side (scene-total, groomer's cuddle relief
included), and the wet-now disclosure below.

**Wet-now disclosure (Experiments review point 3 — no code change)**:
the helper prices only candidates wet at DECISION time. Measured wet
windows are dominated by MID-SCENE waterline crossings, which the
ladder neither charges for (a dry partner stepping in) nor discounts (a
wet partner stepping out). Smoke consequence, mirrored in the smoke
design doc's readout section: arms C/D can express avoidance of WET
partners, not anticipatory avoidance of water's-edge loiterers — the
water-adjacent-share readout is expected to move less than the
cross-waterline-adjacency readout, and a flat water-adjacent share is
NOT evidence the charge produces no edge behavior.

## D5 — Expected scene duration (amended per Experiments review 2026-08-31)

**Decision**: `E_ticks(kind)` = the **`min`** of the existing
`[durations]` `DurationBounds` for the scene's activity kind — play →
`durations.play`, cuddle/rest → `durations.cuddle`, co-sleep →
`durations.sleep`, grooming → the grooming activity's governing bounds
(mapping verified against the activity code at implementation; if
grooming has no bounds entry, fall back to the short-activity default
and record it in the config doc comment).

**Rationale**: the horizon must match the basis the chooser's other
duration-anchored terms use, or exposure is systematically overweighted
against relief (Experiments review point 1: a midpoint basis over play
bounds [min, max] overweights by mid/min — up to 3× at the default
[2, 5]-shape bounds — and would manufacture avoidance the priced
economy doesn't imply). Two anchors agree on `min`: needflow values
relief over MIN duration, and the chooser's one existing
duration-anchored term (`expected_wait`, selection.rs — "exact only for
scenes that actually hold their minimum") reads `bounds.min`. The
selection score's relief term itself carries no duration weighting
(pressure is the value proxy), so `min` is adopted from those two
precedents rather than matched to a relief horizon that doesn't exist —
disclosed rather than silently chosen. Still config-grounded,
deterministic, zero new dials. `min` UNDERestimates scenes that run
past their minimum — a conservative bias for a cost weight (never
manufactures avoidance), disclosed; arm E's cranked factor swamps it.

**Alternatives**: midpoint `(min+max)/2` (rejected per the review —
overweights exposure relative to every duration basis actually in use);
a new per-kind expected-ticks config table (four new dials for a
lab-only weight); measured `mlen` constants baked into code (magic
numbers — Article VI violation); per-candidate survival modeling
(speculative machinery, CLAUDE.md rule 2).

## D6 — Ladder injection sites (three, all behind the gate)

**Decision**:

1. **`selection::scored()`** — for needs whose relief is a partnered
   scene (`ReliefSource::Playmate`, `ReliefSource::Friend`): subtract
   `expected_scene_exposure` for the concrete candidate the score
   already priced (the playmate from the shared scan; the
   `nearest_friend` for cuddle).
2. **`selection::play_score()`** — candidate ranking: subtract each
   candidate's exposure so a dry playmate outranks an otherwise-equal
   wet one (this is where positional avoidance becomes learnable).
3. **The groom seam (`needs_driven::groom_response`)** — before
   committing to groom, compare the scene's exposure against the
   scene's TOTAL value (Experiments review point 2: cost is
   scene-total, so value must be too): the groomee's bath pressure PLUS
   the groomer's expected cuddle relief from the same scene (partnered
   groom pays the groomer `groom_cuddle_relief` — the Clementine
   mechanism, currently 2.0 on the serving world), both in need-points.
   Decline only when exposure exceeds that sum; comparing against the
   groomee's bath alone would over-decline net-positive grooms and
   collapse arm D's groom mix for the wrong reason. Under
   `bidirectional` this is the seam that lets a wet groomer spare a dry
   friend — the D-vs-C contrast for groom scenes.

**Rationale**: (1) and (2) are the two existing pricing sites and must
agree (the 004 agreement rule the module documents); (3) is the only
initiation path for grooming-another, and without it the bidirectional
arm's largest charge channel (grooming absorbs most of the re-priced
charge, per Experiments) would be invisible to the teacher. Declining a
groom is a CHOICE change, not a legality change — the action stays
legal; the built-in advisor just proposes something else (Article IV:
behaviors propose, the engine disposes — unchanged).

**Alternatives**: pricing only selection (loses per-candidate and groom
contrasts); pricing inside `priced_travel` (exposure is not a travel
cost; would leak into non-scene walks).

## D7 — Boot log

**Decision**: extend the armed-contagion boot line (`cloudkitty-server`
main.rs) to name the membership rule: "waterline contagion armed
(option_a: the dry namer pays / bidirectional: any dry member pays)…";
the disabled line is unchanged. One additional line states the ladder
gate only when `contagion_aware_ladder = true` (silence at default keeps
the served boot log byte-identical).

**Rationale**: the boot log is the ruled on-box evidence at flip time
(044 F-9); a future membership flip must be as legible as the factor
flip.

## D8 — Validation & budget

**Decision**: enum parse failure is serde's job (unknown variant error
already names the legal values — verify the message in a test; wrap
with a clearer message only if serde's is opaque). `validate_water`
gains NO new budget arithmetic: bidirectional changes who pays, not the
per-cat per-tick maximum (one charge, same magnitude, same ceiling
gate), so the 044 headroom law `ceiling + gain × max_ratio ×
max(1, factor) < safeguard` stands verbatim — asserted by a doc note
and a test arm showing the same config accepts/rejects identically
under both membership values. `contagion_aware_ladder` needs no bounds
(bool).

**Rationale**: FR-008; the budget's worst case is a single cat's single
tick, which membership cannot move (FR-003).

## D9 — Delivery discipline

**Decision**: 044's bar verbatim — red-first evidence for every new
assertion recorded in a redden-list; stamp + golden + explicit≡absent
proofs; both config sweeps; same-seed determinism arms for both dials;
no auto-merge, CI watched explicitly (the dispatch bug recurred on
#334 — expect to nudge).
