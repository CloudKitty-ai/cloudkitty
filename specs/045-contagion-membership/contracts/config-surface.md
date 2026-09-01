# Config Surface Contract: spec 045

The feature's only external interface is the TOML config (both dials)
plus one boot-log line (observability). No API, schema, or event
changes.

## `[water] contagion_membership`

```toml
[water]
bath_gain = 3.5
contagion_factor = 1.0
contagion_membership = "bidirectional"   # or "option_a" (the default)
```

- **Accepted values**: `"option_a"`, `"bidirectional"`. Anything else →
  load-time rejection whose message names both legal values.
- **Absent**: identical to `"option_a"`, which is identical to the
  shipped 044 engine — bit-for-bit (stamp `engine_defaults_sha256`
  unmoved; explicit `"option_a"` parses equal to absent; seeded runs
  byte-identical).
- **Semantics** (only when `contagion_factor > 0` and `bath_gain > 0`):
  - `option_a`: a dry cat pays the contagion charge iff its OWN
    activity names a partner who is on water AND currently adjacent.
  - `bidirectional`: a dry cat pays iff EITHER its own activity names a
    wet adjacent partner OR a wet adjacent cat's activity names it.
  - Both: at most one charge per cat per tick; wet cats pay occupancy
    only; formula, ceiling gate, and the four paired kinds unchanged
    from 044.
- **Interaction**: orthogonal to `contagion_factor` (membership selects
  payers; the factor sizes the charge). With factor 0.0 the setting is
  inert. The `validate_water` headroom budget is membership-independent
  (same config must accept/reject identically under both values).

## `[behavior] contagion_aware_ladder`

```toml
[behavior]
contagion_aware_ladder = true   # default: false
```

- **Accepted values**: TOML boolean.
- **Absent / false**: scripted choice byte-identical to the current
  engine (structural short-circuit, seeded-run equality test).
- **True**: the built-in chooser subtracts each candidate partnered
  scene's expected contagion exposure (scene-total under the active
  membership rule; see `research.md` D4–D6) at the selection score, the
  playmate ranking, and the groom-initiation seam. Proposals only —
  legality, masks, and refusal untouched.
- **Interaction**: with `contagion_factor = 0.0`, exposure is 0 and
  choice is byte-identical to the gate being off (asserted). The
  exposure always follows the ACTIVE membership setting.

## Boot log (observability contract)

- Contagion armed: the existing line now names the membership rule,
  e.g. `waterline contagion armed (factor 1, membership option_a: the
  dry namer pays) ...` / `... membership bidirectional: any dry member
  pays ...`.
- Contagion disabled: line unchanged from 044.
- Ladder: one line emitted ONLY when `contagion_aware_ladder = true`;
  at default the served boot log is byte-identical to today's.

## Out of contract

- The served deployment TOML sets neither key as part of this feature
  (lab-use until the owner's membership ruling).
- No `/world`, `/events`, or python-surface changes.
