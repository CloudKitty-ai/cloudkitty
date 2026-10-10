# Contract: Target-Side Consent Gate (FR-005; ruling eb9e860b)

## Placement

A consent step immediately after `action::validate` in BOTH apply
paths: `run_applied_phases_from_decisions` (world.rs:352-376) and
`apply_slot_verdict` (world.rs:580-595). NOT inside
`action::validate` itself: `legal_action_mask` replays `validate` on
the fog snapshot (cloudkitty-rl/src/mask.rs:59-72), and a
target-need check there would leak hidden state through the mask —
the mask MUST stay consent-blind (ruling item 4: refusal anticipation
is emergent, never handed to the seat).

## Predicate

For a conscripting proposal only (`Play{Kitty{target}}` — Rest, Sleep
and Groom bind nobody, action.rs:379-395):

```
line = config.consent_line_for(target)        // per-kitty, world fallback
line <= 0.0            → gate open (short-circuit; Config::default passes untouched)
top  = top_non_play(target)                   // target's OWN needs — legal (rule 12)
refuse ⇔ top > line && top > target.needs.get(Play)   // spec 047 semantics, strict >
```

The predicate is spec 047's, moved target-side and re-keyed to the
per-kitty line; the `> play` clause is retained (the ruling's
one-sentence summary describes, not redefines — research R3, flagged
to the owner).

## Refusal semantics

- Proposal downgrades to Idle at the gate; `enforce_durations` and
  `absorbed` semantics unchanged (a mid-scene proposer keeps its
  scene).
- `RefusalEvent` stamped with new `RefusalReason::ConsentDeclined`
  (wire name `consent_declined`); events.rs enum change — census and
  trace tools in the experiments lane read this enum (relayed, rule
  3).
- Observability to the proposer (FR-005): the proposal fails — its
  activity stays Idle / its scene continues; the refusal stamp is in
  `refusal_log` (never engine-read, events.rs:59-62). No observation
  cell changes (058 wall).

## What is deleted

Proposer-side consent, entirely: selection.rs:564 (via
`choose_consenting`), :618 (`scored_playmate`'s filter), :929 (via
`take_what_is_here_consenting`); the `_consenting` variants collapse
into the plain forms; `consent_blocks` leaves the behavior layer;
`top_non_play` survives only inside the engine gate.

## Guards (rule 6 — sorted before running)

Must go RED (guards of the changed behavior, rewritten after their
red is observed): `a_serious_playful_cat_honors_the_consent_line`,
`an_adjacent_burdened_friend_is_not_batted_into_a_game`,
`blocking_the_only_playmate_may_buy_solo_play…` (playful.rs:156-240),
`needs_driven_opportunism_ignores_the_consent_line`
(needs_driven.rs:688-720 — its premise is repealed by the ruling).

Must stay GREEN: `evolution_golden` (consent 0), the mask tests, the
schema pins, `every_builtin_declines_a_snapshot_dead_scene`.

New guards owed (each through `scripts/mutate.sh --expect`): the gate
refuses at the target's per-kitty line (not the world line); the gate
is invisible to `legal_action_mask` (mask output identical for hidden
target-need extremes); the refusal stamps `consent_declined`; a
line ≤ 0 world is byte-identical to pre-059 at consent sites.
