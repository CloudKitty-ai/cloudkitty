# Contract: Observation Generation 2 and the Cross-Generation Refusal

The two external contracts this feature changes. "External" here means:
consumed by trained artifacts, by the trainer's Python surface, or by
the operator reading a boot failure — everything that outlives any one
binary.

## C1 — Observation layout, generation 2

- The layout is the one in `data-model.md` §1; the module doc of the
  observation codec is its normative in-repo statement and MUST be
  updated in the same change as the code (they are one artifact).
- The version constant `OBSERVATION_SCHEMA_VERSION = 2` and the
  default-slot length 183 are a single compiled pair. Any future
  change to either is, by definition, generation 3.
- The in-water flag is **tile-derived**: 1.0 iff a water element
  occupies the observing kitty's tile in the start-of-tick snapshot.
  It is independent of the kitty's activity, of the `[water]` pricing
  dials (a wet-fur-disabled world still reports wet cats), and of the
  nearest-water element slots. The in-sunbeam flag beside it remains
  **activity-derived** (sleeping-in-sunbeam); the asymmetry is
  deliberate and documented where the layout is documented.
- The python surface (`cloudkitty.OBSERVATION_SCHEMA_VERSION`)
  re-exports the compiled constant; consumers MUST read it rather
  than pinning 2, exactly as they should not have pinned 1.

## C2 — Artifact acceptance

A binary accepts an artifact iff **all** existing gates pass; this
feature changes no gate logic, only the compiled expectations:

| Gate | Gen-2 binary expectation |
|---|---|
| `observation_schema` | = 2 |
| first layer input width | = compiled `observation_len` (183 @ default slots) |
| `action_schema` / `mask_schema` / version / magic / activation / blob size | unchanged |

The schema gate and the width gate remain **independent**: each MUST
reject a generation-1 artifact on its own (a mis-built artifact could
pass one and fail the other).

## C3 — The refusal message (the legibility contract)

When either gate fails, the surfaced error — at server boot and from
kitty-eval alike — MUST let a reader with no context answer all four:

1. **Which file**: the artifact path (today attached by the
   registration layer's context: `[rl.policy.<name>].artifact (<path>)`).
2. **Which seat**: the policy name being resolved (same context line).
3. **What disagrees**: found vs expected — schema numbers for the
   schema gate; widths for the width gate, with the note that a width
   mismatch against the compiled observation size ordinarily means the
   artifact predates the binary's observation generation.
4. **What to do**: an artifact trained for this binary's generation is
   required — re-train; no conversion or compatibility mode exists.

The refusal MUST be symmetric: a generation-2 artifact under a
generation-1 binary produces the same four answers with the numbers
reversed. The failure remains fail-fast: boot aborts with nonzero
status, no partial or degraded world (Article IV posture).

## C4 — What is explicitly NOT contracted

- No dual-schema loading, no artifact conversion, no fallback seat
  when an artifact is refused (a refused artifact is a config error,
  the unknown-behavior-name doctrine).
- The served box's behavior before the post-exp-003 rollout: it runs
  a generation-1 binary with generation-1 artifacts and never meets
  these gates.
- `GET /config` continues to omit all `[rl.*]` content; nothing in
  this feature adds artifact facts to the served config surface.
