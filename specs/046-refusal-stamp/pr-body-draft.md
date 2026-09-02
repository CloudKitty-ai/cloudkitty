# PR body draft: spec 046 — Refusal Stamp

Records every Article IV refusal — a non-Idle proposal `action::validate`
resolves to Idle — into a bounded ring on the `World`, each event carrying
the kitty, the proposal **verbatim** (targets included), the tick, and an
`absorbed` flag from the enforcement outcome (Experiments ruling (b),
2026-09-01: `absorbed == false` rows are the taxed ticks; census
definition quoted in the spec). Ring sized by `[events] refusal_retention`
(default 6,000 — see the review section), served at `GET /events/refusal`
as `{capacity, events}`, recorded once in the shared apply pipeline so
both tick drivers stamp identical streams.

Additive delivery proven:

- Dynamics byte-identical: the 10k-tick evolution digest with the new
  `refusal_log` key stripped equals the 041 pin exactly (RNG and all
  sibling state included); golden regenerated per its own doctrine with
  the witness recorded in `specs/046-refusal-stamp/redden-list.md`.
- `engine_defaults_sha256` unmoved (skip-at-default, guard test).
- Pre-046 saves resume: `persist::load_and_validate` re-stamps the ring's
  capacity from config (retention is configuration, the behavior
  re-stamp doctrine).
- 22 red-first cycles + live emit-proof payload in `redden-list.md`.
  Suite 774 → 792, nothing lost.

## Review-medium fixes (2026-09-01, findings 2/4/6/7/8)

- **Ring re-sized 4,000 → 6,000** (finding 2): absorbed refusals share
  the ring's slots with taxed ones — measured ~0.38/tick combined on the
  scripted default world (taxed 1,586 / absorbed 2,414 at saturation), so
  4,000 covered only ~10.4k ticks of the ≥15k census window. New
  ring-observing guard `default_ring_covers_the_baseline_window_under_
  absorbed_load` (red at 4,000 before the raise); floor test re-derived
  to ≥ 5,700. Still a floor per FR-004 — Experiments re-derives by config
  at the first live baseline. ⚠ Experiments ruled the original 4,000
  (explicitly with the absorbed term unmeasured); the raise honors their
  floor but should be relayed.
- **Capacity envelope** (finding 4): `/events/refusal` now serves
  `{capacity, events}` (the `/welfare` threshold precedent) so a wrapped
  window is tellable from a short history — `/config` omits the knob at
  its default. Contract + quickstart amended.
- **Strip witness in-tree** (finding 6): the golden continuity claim is
  now a running test (`golden_strip_witness_refusal_ring_is_the_only_
  delta`, string-level strip — a `Value` round-trip reorders keys). It
  earned its keep immediately: the 6,000 raise moved the full pin
  (capacity integer) while the witness stayed green.
- **Docs** (finding 7): `/events/refusal` row in the README endpoint
  table; `refusal_retention = 6000` row in the shipped `cloudkitty.toml`.
- **Typed endpoint test** (finding 8): the integration test now
  deserializes the served list as `Vec<RefusalEvent>` (absorbed's
  presence proven by the deserialize itself) and got its first redden
  rows (cycles 18–19).

Findings 3 and 5 were then fixed on the owner's ruling (cycles 20–22):

- **Sibling-ring re-stamp** (finding 3): the load-path capacity re-stamp
  now covers all three rings (`distress`, `activity_log`, `refusal_log`)
  — a retention edit reaches every ring on resume instead of silently
  losing to the persisted capacity. Semantics note: shrinking a
  retention now trims that ring's oldest events on the next resume;
  that is what "retention is configuration" means. No-op on the
  deployed box today (both sibling retentions have only ever been their
  defaults).
- **Publish-path reuse** (finding 5): `Published` reuses the previous
  tick's refusal-window `Arc` when the ring is unchanged, witnessed by
  (length, newest tick) — sufficient because the sim loop is the sole
  writer and `record` stamps the strictly-increasing current tick,
  including the saturated-rotation case a length-only witness misses.
  A quiet tick is now a pointer copy instead of a ~192 KB reclone, and
  raising `refusal_retention` no longer scales the per-tick publish
  cost.

Finding 1 (absorbed semantics) was relayed to Experiments, who ruled
**(a): keep the implemented formula** — `absorbed = (enforced != Idle)`
IS the census meaning ("the kitty was mid-scene and the scene
continued"), because the taxed count reproduces F-033's idle-tick
definition: a past-minimum refusal kept a need-relieving scene, so its
cost is proposal quality (the absorbed rows' step-4/H6 evidence), not
welfare. Prose corrected everywhere (docstrings, recording-site comment,
CHANGELOG, contract — including the already-satisfied-scene blind spot,
report-only), and the ruling is pinned by
`a_refusal_past_the_scene_minimum_is_still_absorbed` (cycle 23: a
ruling-(b) drift injection reds only this test — the review's
"indistinguishable mechanisms" gap, closed).

Open with Experiments (does not gate this PR): the event does not carry
the enforced outcome's kind; their baseline wants to read absorbed rows
by enforced activity kind. Awaiting their word on adding an `enforced`
field vs. correlating another way.

## Reported, not fixed (CLAUDE.md rule 3)

*(The sibling-ring capacity gap originally reported here was fixed on
the owner's ruling at the review-medium pass — see finding 3 above.)*

## Spec-artifact deviations (recorded during implement)

- T018 lives in `persist.rs` tests, not `core/tests/snapshot_resume.rs`:
  core tests cannot import the server crate (dependency direction).
- T020's "golden passes unregenerated" was unsatisfiable as written for
  an additive world field; replaced by the strip-witness proof above.
  SC-003 (byte-identical kitty traces) holds — the witness proves more.
- Contract examples updated to the REAL wire tag (`"action"`, not the
  provisional `"kind"`), pinned by the emit-proof test.
