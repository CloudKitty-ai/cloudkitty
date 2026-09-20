# Contract: `actions.sleep_floor_off_beam` (spec 056)

The one external surface this feature adds. Name FROZEN by the owner's
clarify pass (2026-09-20) — Experiments' PREREG-tier5.md wires to it.

## TOML

```toml
[actions]
# Off-beam sleep relieves the sleep need only down to this floor; a
# sunbeam, or conducted warmth beside a mutual partner on one (spec 031),
# clears it fully. 0 (the default) is the pre-056 law.
sleep_floor_off_beam = 0.0
```

- Absent key = 0.0 = pre-056 law, byte-for-byte (FR-001/FR-007).
- Accepted: finite f32, `0 ≤ value < [thresholds] distress` (the configured
  threshold). Anything else: startup `ConfigError` naming
  `[actions] sleep_floor_off_beam`, the offending value, and the bound —
  never a clamp.

## `GET /settings` (spec 052)

The key joins the key-settings block: served value, engine default, and
membership in the settings lists, rendered like its `[actions]` siblings
in the boot log and the endpoint. No other API change.

## Explicitly not changed

The plugin wire (docs/plugins.md), the snapshot schema, the observation
encoding, the client, every other `[actions]` dial, and every shipped or
frozen toml file.
