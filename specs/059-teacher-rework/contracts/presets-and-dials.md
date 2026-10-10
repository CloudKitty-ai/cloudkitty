# Contract: Presets and Dials (FR-001, FR-002, FR-003, FR-004)

THE citable preset→dial table (FR-002). A config naming `playful` or
`needs_driven` resolves to the Teacher with exactly these frozen
settings; `teacher` is the Gen 2 collection seat.

## The table

| | `needs_driven` | `playful` | `teacher` |
|---|---|---|---|
| wander rung | **on** | off | on |
| groom_response rung | **on** | off | on |
| luxury rung | off | **on** | on |
| cue-answer rungs (US3) | off | off | **on** — implementation finding 2026-10-10: a fourth toggle, forced by the same byte-equality argument as the other three (today's brains never answer, so the compat presets must not either) |
| need-rate multipliers | world/`[needs]` fallback | same | same (Gen 2: drawn per cat) |
| comfort slack | world `[behavior] comfort_slack` fallback (default 0 ticks) | same — **0, NOT a playful_comfort equivalent** (research R2) | same (drawn) |
| consent line | world `[behavior] consent_line` fallback — enforced TARGET-side (ruling eb9e860b) | same | same (drawn) |
| favourite weights | 0 (accessor fallback) | 0 | 0 (drawn) |

Rung toggles are compatibility shims, not identity: never drawn, never
observed, only these three rows exist. Per-kitty `[[kitty]]` dial
overrides beat every fallback (existing accessor semantics,
config/mod.rs:1502-1544).

## Byte-equality bar (SC-001)

- `evolution_golden` (Config::default(), consent 0): byte-identical,
  UNCHANGED fixture — proves both presets where consent is inert.
- Stream recorder (R6b) on served `cloudkitty.toml` and
  `experiments/fog-gen1-cert/anchor-b3.toml`: per-tick action +
  message digests, old brain vs preset, equal at every tick EXCEPT
  ticks the FR-015 fire counter marks consent-moved. The c30 anchor
  stays the certification reference with those divergences declared.
- Binding surface: `ParallelEnv(control=...)` accepts the same three
  strings plus `teacher`; `--control-brain` (cert_harness_fog.py:474)
  and kitty-eval `--brain` resolve via the same registry.

## Dial semantics (where each dial acts)

- **need rates** (`need_rate_for`): world need tick only
  (world.rs:1109) — the teacher reads pressures that already embody
  them; no second read site.
- **comfort slack** (`slack_cell_for`, core — research R5): gates
  luxury ENTRY only: `now − last_relief_tick ≥ cell × 40`. Exit stays
  the `weighted_pressure ≥ playful_comfort` line. They never compose
  into one trigger.
- **consent line** (`consent_line_for`): read by the ENGINE at the
  apply slot for the TARGET (contracts/consent-gate.md). No
  behavior-layer read anywhere.
- **favourite weights** (`favourite_weight_for`): multiplies the VALUE
  side of the shared selection score for ITS need kind —
  `(pressure + urgency term) × (1 + w)`, w ∈ [0,1], costs untouched.
  Implementation finding 2026-10-10: applied to every kind (the dial
  struct carries all six and the observation shows all six — a
  partnered-only read would leave four observed dials dead), which
  contains "tips among partnered activities of equal relief value" as
  the FR-004 case. All-zero multiplies by exactly 1.0: bit-identical
  to the unweighted pass.
