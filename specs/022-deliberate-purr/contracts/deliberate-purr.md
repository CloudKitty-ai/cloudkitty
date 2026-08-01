# Contract: Deliberate Purr & Quiet Motor (spec 022; FR-001..FR-015)

The purr surfaces after this change, as behavior visible to advisors,
policies, the API, and certification instruments. Companion contract: spec
023 owns meow-cooldown retirement; the two land in one engine batch, so no
released engine exposes an intermediate state.

## Row 38 — the deliberate purr

```text
wire:   {"action": "meow", "message": "purr"}     (unchanged encoding)
menu:   index 38 of 40                            (unchanged; no codec bump)
```

| Situation at proposal | Validation | Effect at apply |
|---|---|---|
| Earned, not purring | legal | turn consumed; duration drawn (apply phase, fair order); purr phase starts (`purring_until`, `purring_duration` set); one announcement recorded directly — never swallowed |
| Earned, not purring, motor cooldown active | legal | same as above — the deliberate purr ignores the motor cooldown ("choice beats reflex", FR-005) |
| Earned, already purring (either origin) | legal | silent no-op: turn consumed, no draw, no announcement, no state change (FR-006) |
| Unearned | **illegal** → `Idle` (Article IV) | never reaches apply; policy mask row 38 is off (derives from `validate()` — no carve-outs, per spec 014 encodings contract) |

Earned rule, identical for both origins and never diverging (FR-003):
`happiness > thresholds.purr || happiness_rose`.

Legacy `{"action":"purr"}` (pre-011 vocabulary): still refused → `Idle`.

## The motor (spontaneous purr phase)

- Start condition unchanged: earned ∧ `tick ≥ purr_cooldown_until`, checked
  in the purr phase in stable kitty-id order.
- Start draws, in order: duration (`min_ticks..=max_ticks`, one draw even
  when equal), then announce (`gen_bool(announce_probability)`, one draw
  regardless of value — FR-011 shape rule).
- Announcing start: `Meow(Purr)` recorded directly. Silent start: nothing
  recorded. **Neither stamps the Purr message cooldown** — the stamp is
  deleted (FR-008; 023 handoff).
- End (either origin, purr phase, stable order): factor drawn uniformly
  from `[cooldown_factor_min, cooldown_factor_max]` (one draw even when
  equal), then `purr_cooldown_until = tick + ⌈factor × duration⌉`;
  `duration` is the stored `purring_duration`, or `min_ticks` for a
  pre-022 snapshot's in-flight purr (FR-012 convention).

## Draw table (Article V pin, FR-011)

| Moment | Phase | Order | Draws (in order) |
|---|---|---|---|
| Deliberate start | action apply | fair apply order | duration |
| Spontaneous start | purr phase | stable kitty-id order | duration, announce |
| End (either origin) | purr phase | stable kitty-id order | factor |
| Deliberate no-op | action apply | — | none |

Config values change draw outcomes, never draw count or order. A kitty that
starts deliberately at apply is already purring by the purr phase, so the
motor cannot double-start it the same tick.

## Config schema (`[purr]`)

```toml
[purr]
min_ticks = 8                  # duration draw bounds, both origins
max_ticks = 13
announce_probability = 0.0     # spontaneous-start announce chance [0,1]
cooldown_factor_min = 1.75     # per-end factor draw bounds (> 0, min <= max)
cooldown_factor_max = 2.75     #   motor rest = ceil(factor x duration)
# cooldown_ticks — RETIRED (spec 022): naming it fails the load with an
# error citing the replacement pair. Never silently ignored.
```

The served `cloudkitty.toml` updates in this same change-set (it pins the
retired key today; the repo config must always load — the issue-#76 world
stamp hashes it).

## Amendments to standing contracts (land with this change, FR-015)

- spec 011 spec.md: "purring is never an action" → purring remains
  engine-owned state; *initiation by choice* now exists via row 38 (dated
  amendment).
- spec 001 data-model.md: "Meow: always legal; the cooldown decides whether
  it is audible" → purr row earned-gated (this spec); the cooldown clause
  is deleted by spec 023 (dated amendment, both pointers).
- spec 014 contracts/encodings.md: mask note — row 38 legal iff earned;
  mask shape/width and the no-carve-outs guard unchanged.

## Guarding tests bound to this contract

1. Earned deliberate purr: starts phase, one announcement, turn consumed;
   duration within bounds (US1-1).
2. Deliberate under motor cooldown still starts (US1-2).
3. Already-purring no-op: no draw (p-stream equality), no announcement,
   turn consumed (US1-3).
4. Unearned: `validate()` → `Idle`; mask row 38 off; mask never all-zero
   (US1-4).
5. Every purr earned — property test over randomized configs/behaviors
   (SC-003).
6. Silent motor: default config, starts at unchanged cadence, zero
   announcements, no stamp (US2-1); `p` strictly between 0 and 1 announces
   per-draw (US2-2).
7. p-invariance: same seed, `p` = 0 vs 1 → identical purr start/end
   sequences (FR-011 shape rule).
8. Factor cooldown: stamp = ⌈factor × duration⌉, factor within bounds,
   seeded-reproducible; equal bounds → fixed factor (US3-1).
9. SC-004 occupancy: within ±2pp of 1/(1 + mean factor bounds) over
   ≥20k ticks, across duration/factor configs sharing the 2.25 midpoint.
10. Retired knob: config naming `cooldown_ticks` fails to load, error names
    replacements (US3-3); new validation rows reject out-of-range values.
11. Determinism: same seed/config/ticks → identical world incl. purrs;
    mid-purr save/restore equality; pre-022 snapshot fixture restores under
    the min_ticks convention (SC-006, FR-012).
12. SC-005 compatibility: existing `cloudkitty-rl` shape/harness tests pass
    unchanged (observation width, menu size 40, mask width, kind count).
