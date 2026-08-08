# Contract: encodings v2 — menu, message head, digest, mask, artifact, seam

Successor to specs/014-multi-agent-rl/contracts/encodings.md (which stays
frozen as the v1 record). Everything here is normative for generation 3
(observation schema 3 / action schema 2 / mask schema 2 / artifact version 2).
Indices are never repurposed within a schema version; growth only by version
bump.

## Action menu v2 — 34 entries (default slots: kitty_slots=3, critter_slots=4)

Identical to menu v1 with rows 33–38 (the six Meow rows) **removed** and Idle
renumbered:

| index | entry |
|---|---|
| 0–32 | exactly menu v1 rows 0–32 (movement, waits, eat/drink, chases, play, groom, rest/sleep variants, per-slot targets — unchanged order) |
| 33 | Idle |

The six meow actions are inexpressible in the activity menu; the message head
is the only way to meow. `Action::Meow` proposals from external advisors parse
and validate-fail (lawful degradation, Purr precedent).

## Message head v1 — 9 entries

| index | message | legality (engine `message_legal`) |
|---|---|---|
| 0 | Silent | **always legal** (structural never-all-zero) |
| 1 | want_eat | armed(Eat) ∧ cooldown clear |
| 2 | want_drink | armed(Drink) ∧ cooldown clear |
| 3 | follow_me | cooldown clear |
| 4 | want_play | armed(Play) ∧ cooldown clear |
| 5 | want_cuddle | armed(Cuddle) ∧ cooldown clear |
| 6 | purr | purr_earned ∧ tick ≥ purr_cooldown_until |
| 7 | want_bath | armed(Bath) ∧ cooldown clear |
| 8 | want_sleep | armed(Sleep) ∧ cooldown clear |

- armed(need): hysteresis state per data-model (`announce_threshold` /
  `announce_hysteresis` dials).
- cooldown: per cat **per kind**, `tick + recent_window_ticks` stamped at each
  emission of that kind (clarified 2026-08-08).
- `wait_for_me` has **no index**: engine-reserved, emitted only by the yield
  rule; scripted deciders may carry it in `Decision.message`, policies cannot
  express it.
- An illegal proposed message resolves to Silent; the paired activity is
  unaffected.

## Meow digest v3 — 32 observation values

Per kind in `HEAD_KINDS` order
(`want_eat, want_drink, follow_me, want_play, want_cuddle, purr, want_bath,
want_sleep`), 4 values describing the **single freshest audible emitter** of
that kind (self-excluded; tie-break lower kitty id); zeros when none:

| offset | value |
|---|---|
| +0 | recency `(1 − age/recent_window_ticks).clamp(0,1)` |
| +1 | dx to that emitter, / width |
| +2 | dy to that emitter, / height |
| +3 | intensity stamped at emission (want-kinds: grounding need /100; purr/follow_me: 0.0) |

Digest position in the observation: unchanged (after element slots, before the
episode clock). Default-slot observation length: **197**.

## Mask — schema 2

Serialized as one vector: `[activity mask (menu_len) | message mask (9)]`,
width 43 at default slots. Both halves are pure oracles over engine law
(`validate` / `message_legal`); neither half is ever all-zero (activity:
FR-018 structural guarantee; message: Silent always legal). Dataset meta
records both widths.

## Artifact v2

Container unchanged (magic `CKPOLICY`, u32 header len, JSON header, f32 blob).
Header: `artifact_version: 2`, schemas `{observation: 3, action: 2, mask: 2}`.
New validation rule: final layer out-width == `menu_len + message_head_len`
(43). Logits `[0..menu_len)` = activity head, `[menu_len..)` = message head.
Selection: per-head masked argmax (greedy) or per-head masked softmax sampling
with the two uniforms derived from splitting one `DecisionRng` u64
(hi u32 → activity, lo u32 → message). v1 artifacts fail loudly at
`artifact_version`.

## Seam records

`Decision { activity: Action, message: Option<MessageKind> }` crosses the seam
everywhere a bare `Action` did. `KittyTickRecord` carries
`proposed`/`validated`/`applied` activities (as today) plus
`proposed_message`/`applied_message`; an illegal message shows as
proposed ≠ applied (Silent) with no separate provenance. Exporter contract:
`label` from the applied activity via `ActionCodec::v2::encode`, `label_msg`
from the applied message via `MessageCodec::encode` (Silent = 0). Seam types
stay `pub`; downstream tool recompiles are Experiments'.

## Config surface (wire keys)

```toml
[meow]                        # exactly three keys
recent_window_ticks = 10      # audibility window AND per-kind mask cooldown
announce_threshold = 30.0     # want-kind grounding threshold
announce_hysteresis = 5.0     # re-mask at threshold - hysteresis

[actions]
cosleep_drip_relief = 15.0    # passive companion tier (both parties)
cosleep_mutual_relief = 15.0  # mutual tier: partner Sleeping/Resting adjacent

[behavior]
cuddle_real_threshold = 15.0  # scripted groom-response + cosleep-routing gate
```

Retired with loud, named errors: `[meow] courtesy_ticks`,
`urgent_courtesy_ticks`, `urgent_need_threshold` (spec 028), joining the
spec-023 sentinels. `[purr]` untouched. `GET /config` reflects all of the
above additively.

## Compatibility claims

- Pre-028 **world snapshots load and run** (all new fields serde-defaulted;
  new enum variants only extend). Pinned by the committed fixture test.
- Pre-028 **policy artifacts refuse loudly** (artifact_version, then schema
  mismatches — byte-frozen error text unchanged in style).
- Configs carrying retired `[meow]` keys **refuse loudly** with migration text.
- `engine_defaults_sha256` **moves by design**; changelog markers
  `[obs-schema]`, `[rng-sequence]`, `[stamp]` — deliberately not
  `[world-fresh]`.
