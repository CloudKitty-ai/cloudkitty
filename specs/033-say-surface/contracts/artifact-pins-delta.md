# Contract Delta: Artifact Schema Pins (amends spec 030)

**Base contracts**: `specs/030-artifact-v3/contracts/policy-artifact-v3.md`
and `forward-v3.md`. Loader machinery, header shape, blob module order,
determinism tier, and version-set semantics are ALL unchanged; this delta
turns the pins and records the derived-dimension consequences.

## What turns

- Engine expectations become `observation_schema = 4`, `action_schema = 3`,
  `mask_schema = 2 → 3`. Any artifact (v2 or v3 FORMAT) pinning the old
  values is refused at startup with the existing error shape, naming the
  artifact path, the pin, and the expected value. Nothing is refused "by
  shape accident."
- `SUPPORTED_VERSIONS` stays `{2, 3}`: artifact FORMAT and schema
  generation are independent axes. A v2-format (MLP) artifact declaring the
  new schemas is loadable; every PRE-wall artifact of either format is not.

## Derived dimensions under schema 4 (header-authoritative, as before)

- Observation length: 225 (digest widened to 15 kinds × 4; kitty slots
  remain 3 — a schema constant, not roster-derived).
- v3 token layout: msg-kind group becomes 15 tokens × width 4; all other
  groups unchanged (self 1×34, kitty 3×20, chow 2×5, water 2×4, sunbeam
  2×6, critter 4×10, clock 1×1).
- Heads: dense 11 (unchanged), kitty-pointer 5 verbs × 3 slots
  (unchanged), critter-pointer 2 verbs × 4 slots (unchanged), message head
  16. Total logits 50.
- v2-format (flat MLP) input dim under schema 4: 225; output dim: 50.
- Blob module order (v3 format): unchanged from spec 030's contract; only
  the msg embedding's token count and the msg head's width move, both
  derived from the header + slot config exactly as before.

## Parity gate (FR-013)

`crates/cloudkitty-rl/tests/fixtures/oracle.ckpolicy` + `oracle.parity` are
replaced in place with an export at the new layout: parity rows are
`u32 n_rows, u32 obs_len (225), u32 logit_len (50)` then rows of
obs++logits `<f4` — same format, new widths. ≥ 100 rows including
vacancy-stress and rows where new kinds (reserves especially) are
never-legal. Tolerance unchanged: ≤ 1e-4 max abs logit error, exact greedy
activity argmax. Exported by Experiments via `export_oracle_v3.py` (the
certified path) at the mid-arc handshake; the pin-turn commits and the
fixture swap land in the same CI window so the always-on gate never crosses
red.

## Proposal wire (plugins, spec 016 surface)

`PROPOSAL_WIRE_VERSION` 1 → 2: `follow_me` is no longer an accepted message
kind name (now `mew`); `here_food`, `here_water`, `here_critter`,
`here_sunbeam`, `chirp`, `trill`, `ekekek` join the accepted set (legality
still enforced engine-side — a plugin proposing a disabled or ungrounded
kind gets the Silent downgrade, never an error). `docs/plugins.md` is
updated in the same PR.
