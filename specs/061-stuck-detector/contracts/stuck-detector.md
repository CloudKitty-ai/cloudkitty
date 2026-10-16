# Contracts: Stuck Detector

Three externally visible surfaces. Everything else is module-internal.

## 1. Configuration table (`[stuck_detector]` in the server TOML)

```toml
# All keys optional; absent table = these defaults (shipped dark).
[stuck_detector]
mode = "off"        # "off" | "observe" | "enforce"
window = 30         # ticks; >= 2
armed_line = 75.0   # need value; in (0, 100]
radius = 1          # Manhattan confinement radius; >= 1 (1 = replay-verified)
recent_fires = 256  # status ring capacity; >= 1
```

- Unknown keys are a load-time error (`deny_unknown_fields`), as for
  `[watchdog]`.
- Invalid values are a load-time error with the offending key named.
- The table is a foreign table to the engine config: present in the
  file, invisible to the engine, never serialized by it
  (`engine_defaults_sha256` unchanged — guarded by the extended leak
  test).
- `/settings` renders the live values under pinned key names.

## 2. Status endpoint (`GET /stuck`)

JSON, the `/welfare` conventions (snake_case, stable field names —
pinned by test):

```json
{
  "mode": "enforce",
  "window": 30,
  "armed_line": 75.0,
  "radius": 1,
  "per_seat": [
    {"kitty": 1, "name": "Biscuit", "enforced": 2, "observed": 0}
  ],
  "armed": [
    {"kitty": 1, "name": "Biscuit", "confined": 12,
     "hottest_need": "eat", "streak": 9}
  ],
  "recent": [
    {
      "tick": 4412, "kitty": 1, "name": "Biscuit", "mode": "enforce",
      "window": 30, "anchor": [18, 0], "confined_span": 31,
      "armed_need": "eat", "need_value": 83.0,
      "proposal_replaced": {"activity": "MoveE", "message": null},
      "substitute": {"activity": "MoveN", "message": "WantEat"}
    }
  ]
}
```

- `per_seat` and `armed` list every tracked (mind-class) seat, including
  zero-count ones; scripted seats never appear (FR-003, SC-005).
- `recent` is bounded (`recent_fires`), newest last; every record
  carries every field (SC-003 — no nulls except a genuinely absent
  message).
- With `mode = "off"` the endpoint still serves config echo and empty
  collections (the surface exists dark, FR-009).

## 3. Fire log row (the corpus-readable record, FR-011)

One structured tracing event per fire — target `cloudkitty_server::stuck`,
level WARN (`enforce`) / INFO (`observe`) — carrying the same
attribution as a `recent` entry, FLATTENED to exactly these structured
field names (not interpolated prose): `kitty`, `name`, `tick`, `mode`,
`window`, `anchor_x`, `anchor_y`, `confined_span`, `armed_need`,
`need_value`, `proposal_replaced`, `replaced_message`, `substitute`,
`substitute_message`. An absent message is the empty string, rendered
as a bare `key=` (JSON `null` exists only on the `/stuck` surface); an
inner advisor that yielded no proposal flattens to
`proposal_replaced=none`.

A real captured line (the rendering-shapes test in `stuck.rs` pins
every shape below; corrected 2026-10-15 after Experiments' report —
the original example showed value shapes the formatter never emitted):

```text
WARN cloudkitty_server::stuck: stuck fire kitty=2 name="Mr Whiskers" tick=4412 mode="enforce" window=30 anchor_x=4 anchor_y=7 confined_span=31 armed_need=Eat need_value=83.19999694824219 proposal_replaced=Sleep { with: Some(3) } replaced_message=WantEat substitute=Move { direction: East } substitute_message=
```

Value rendering rules (what a consumer must parse):

- `name` and `mode` are the only QUOTED fields. `name` is quoted
  because a config may give a kitty a spaced name (owner 2026-10-15;
  before that date served logs rendered it unquoted — a reader of
  pre-change logs handles both).
- Everything else is unquoted. Action values (`proposal_replaced`,
  `substitute`) render in the engine's debug shape, WITH spaces and
  braces: `Idle`, `Move { direction: East }`, `Sleep { with: Some(3) }`.
  Never split a line on whitespace; the FIXED FIELD ORDER above is the
  parse anchor (every boundary is ` <known_key>=`).
- `armed_need` is the need's bare kind name (`Eat`, `Sleep`, …);
  message values are bare kind names (`WantEat`).
- `need_value` is the f64 widened from the engine's f32, full
  precision (`83.19999694824219`), with a trailing `.0` on whole
  numbers.
- As served, lines carry ANSI escapes even when piped (the formatter's
  default); strip them before parsing.

These names are the contract (the corpus INVESTIGATE-row consumer and
the Gen 2 battery re-read parse them); a rename — or any change to the
rendering rules above — is a breaking change and takes a spec touch
plus a relay to Experiments before it lands.

## Invariants across all surfaces

- Off ⇒ zero tracking, zero records, zero behavior change; the paired
  worlds (detector constructed-and-off vs absent — mind seats are
  wrapped even when off, so the pairing exercises the real forwarding
  path) are byte-identical over thousands of ticks (watchdog
  non-interference template).
- Observe ⇒ records only; on a budgetless run the applied decisions and
  the master RNG sequence are tick-for-tick identical to off (FR-008
  extension). On the served path the record computation spends time
  inside the seat's decision budget — a stated residual, not a
  divergence in applied state.
- Enforce ⇒ the only divergence from observe is the applied action on
  fire ticks; replays of the same seed/config/deterministic seats
  reproduce identical fire sequences and substitutes (SC-004).
- No surface ever shows a scripted seat (SC-005).
