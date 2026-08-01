# Contract: The Meow Channel After Enforcement (spec 023; FR-001..FR-011)

Companion to spec 022's contracts/deliberate-purr.md; one engine batch, no
released intermediate state.

## Emission

- Every validated `Action::Meow` **emits**: recorded in `recent_meows`,
  visible to digests and viewers, stamping per-kind bookkeeping (with the
  urgent rule applied at stamp time). No state consults can suppress it.
- Turn cost: the whole turn, always (unchanged).
- Purr-kind exception: `Meow(Purr)` is spec 022's deliberate purr (never
  reaches `emit_meow`); purr starts stamp no bookkeeping — guarded here.
- Wait-for-me stays off the learned menu (spec 012 reservation) and out of
  `LEARNED_MEOWS`; its proposal path is the third courtesy emitter below.

## Courtesy (behavior-layer, voluntary, binds no advisor)

| Emitter | Rule |
|---|---|
| Urgent needs announcer | consult `can_meow` before proposing (existing) |
| Playful play announcer | consult before the announce coin (existing) |
| Approach-etiquette yield | **new consult**: on courtesy the yield is a silent stand (`Idle`) — turn spent standing, tick-parity anti-orbit guarantee intact |

Intervals: base `courtesy_ticks` = 10 (= digest window: refresh-on-expiry,
no dead air, no stacking); `urgent_courtesy_ticks` = 5 at/above the
unchanged urgency threshold — urgency rides the digest decay envelope, no
engine rule.

## Config schema (`[meow]`)

```toml
[meow]
courtesy_ticks = 10          # scripted manners: how long a built-in waits
urgent_courtesy_ticks = 5    #   before repeating a kind (urgent: sooner).
                             #   Consulted by scripted behaviors; the engine
                             #   enforces nothing — agents are governed by
                             #   the turn cost (spec 023).
urgent_need_threshold = 75.0 # unchanged
recent_window_ticks = 10     # unchanged
# cooldown_ticks / urgent_cooldown_ticks — RETIRED (spec 023): naming
# either fails the load with an error citing its replacement.
```

Partial `[meow]` tables are legal and default-filled (posture aligned with
`[purr]`, research D2). Served `cloudkitty.toml` renames in the same
change-set.

## Doctrine amendments landing with this change (FR-008)

- spec 001 data-model.md: "the cooldown decides whether it is audible" —
  deleted; legal means heard (except 022's earned-gated purr row). Shared
  annotation with 022 (one dated note, both pointers).
- spec 012 spec.md: "if the word is on its base cooldown the meow is
  lawfully silent" → the yield consults courtesy and stands silently; the
  progress guarantee is the stand.

## Guarding tests bound to this contract

1. Same-kind repeat meow on consecutive ticks **emits** both times —
   replaces `meows_on_cooldown_are_silently_dropped` (SC-007; the old
   assertion's retirement noted in the test doc comment).
2. Emission always stamps: bookkeeping timestamp advances on every emitted
   meow, urgent rule applied at stamp time (US1-3).
3. Worst-case chatty advisor bounded: digest presence clamped, recent
   record pruned to window (US1-2; existing clamp/prune tests extended).
4. SC-003 spacing invariant: per-kitty per-kind emission gaps ≥ applicable
   courtesy interval for scripted rosters over long randomized runs,
   including a forced approach-dance (WaitForMe) scenario.
5. Yield on courtesy = silent stand: dance still progresses (tick-parity),
   no WaitForMe emission inside the courtesy interval (US2-4; re-baselines
   selection.rs yield tests).
6. Retired keys: configs naming `cooldown_ticks` / `urgent_cooldown_ticks`
   fail to load naming replacements; partial `[meow]` table default-fills;
   urgent > base rejected (US3-1/2 scenarios).
7. Purr stamps nothing: no purr start (either origin) touches bookkeeping
   (US3-3; guards the 022 handoff from this side).
8. Legacy snapshot with stamped cooldowns restores and runs; a scripted
   kitty's next consult respects the restored stamp (US3-4).
9. SC-004 compatibility gate: `cloudkitty-rl` suite passes with zero
   modifications (shapes identical).
10. SC-005/SC-006: determinism suite green; healthy-baseline welfare bounds
    hold on the new engine.
