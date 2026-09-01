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

**Experiments review**: this section is the value model their handoff
reserved review on; sent for review at plan time. The cap and the
duration source (D5) are the two knobs they are most likely to adjust.

## D5 — Expected scene duration

**Decision**: `E_ticks(kind)` = the midpoint `(min + max) / 2` of the
existing `[durations]` `DurationBounds` for the scene's activity kind —
play → `durations.play`, cuddle/rest → `durations.cuddle`, co-sleep →
`durations.sleep`, grooming → the grooming activity's governing bounds
(mapping verified against the activity code at implementation; if
grooming has no bounds entry, fall back to the short-activity default
and record it in the config doc comment).

**Rationale**: grounded in what the engine actually enforces, already
config-surfaced, deterministic, and adds ZERO new dials. It
overestimates scenes ended early by prune (partner walks off) — an
acceptable bias for a choice weight, disclosed to Experiments; the
smoke's positive control (arm E) cranks the factor far past any
duration-bias sensitivity.

**Alternatives**: a new per-kind expected-ticks config table (four new
dials to justify and validate for a lab-only weight); measured `mlen`
constants baked into code (magic numbers — Article VI violation);
per-candidate survival modeling (speculative machinery, CLAUDE.md
rule 2).

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
   committing to groom, compare the scene's exposure against the value
   grooming delivers (the groomee's bath pressure); decline when
   exposure exceeds value. Under `bidirectional` this is the seam that
   lets a wet groomer spare a dry friend — the D-vs-C contrast for
   groom scenes.

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
