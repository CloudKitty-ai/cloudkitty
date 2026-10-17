# Contract: Provenance Stamp (FR-009, FR-010, FR-012)

Surface: `experiments/tools/bc-collect`'s per-rollout `meta.json`
(Experiments' lane — the implementation PR carries a `cross-lane:` reason
citing their requirements note, which asks for exactly this).

## New fields

Written on EVERY run (knob on or off):

```json
"engine_commit": "4a5b6c…40-hex…[-dirty]",
"starts_law_version": 1,
```

- `engine_commit`: the workspace git commit bc-collect was built from,
  embedded at build time (`build.rs`); `-dirty` appended when the build tree
  had uncommitted changes; `"unknown"` when git was unavailable at build.
  This is the engine's identity too — bc-collect compiles the engine crates
  from the same tree. Matches the intent of the cert harness's
  `binding_engine` stamp (which reads `cloudkitty.ENGINE_COMMIT` and today
  gets `None`; giving the binding a real `ENGINE_COMMIT` is a reported
  follow-up for Experiments, not this spec's scope).
- `starts_law_version`: `cloudkitty_core::starts::STARTS_LAW_VERSION`. A
  draw-law change bumps it in the same commit (FR-012); a stable version
  under a changed law is the break this field exists to make impossible to
  miss.

Written when the knob is on (the FR-010 echo), kitty-id ascending, straight
from the same `starts::draw` call the world was built from:

```json
"starts": [
  {"kitty": 1, "x": 4,  "y": 0,  "category": "edge_ring", "drawn": true},
  {"kitty": 2, "x": 12, "y": 9,  "category": "interior",  "drawn": true},
  {"kitty": 3, "x": 0,  "y": 0,  "category": "corner",    "drawn": false}
]
```

- `category` is the engine's own draw record (for explicit kitties, the
  geometric classification of the pinned tile); `drawn: false` marks
  explicit-coordinate kitties.
- Knob off: the `starts` field is absent (metas stay shaped as today plus the
  two identity fields).

## Invariants (SC-006)

- Echoed (x, y) per kitty equals the tick-0 world-state readback exactly.
- Each echoed category equals an independent geometric classification of the
  position (coverage_read.py's definitions).
- Additive-only: no existing meta.json key changes name, type, or meaning;
  existing readers that ignore unknown keys keep working. The field names
  above are contract for the corpus readers — a rename is a breaking change
  and takes a spec touch plus a relay to Experiments before it lands (the 061
  §3 precedent).
