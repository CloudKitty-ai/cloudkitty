# Research: Shallow ground sleep (spec 056)

No NEEDS CLARIFICATION markers remained after the owner's clarify pass
(D1, D2, and the distress bound all confirmed 2026-09-20). Decisions
below close the plan-level choices.

## R1 — Key type and default mechanics

- **Decision**: `sleep_floor_off_beam: f32` on `ActionsConfig`, with
  `#[serde(default)]` (0.0) and 0.0 in the `Default` impl.
- **Rationale**: needs and every relief dial are f32; fractional floors
  are legal per the spec's assumptions. `#[serde(default)]` makes every
  existing toml parse unchanged — the FR-001 "no file edited" claim.
- **Alternatives considered**: `Option<f32>` (spec-050 shape) — rejected:
  050 needed absent-vs-0 to mean different rules; here absent and 0 are
  the same law, so a plain default is simpler and `/settings` shows one
  number.

## R2 — Validation home

- **Decision**: two checks in `config/validate.rs`: the key joins the
  `[actions]` finite/≥0 sweep (~line 746), and one cross-field check
  `floor < [thresholds] distress` beside the existing cross-section checks.
- **Rationale**: the sweep rows are single-key by construction; the
  bound reads another section, so it cannot live in the sweep. The
  configured threshold (owner-confirmed) means the check reads
  `config.thresholds.distress`, never 90.
- **Alternatives considered**: clamping — forbidden by FR-006 (reject,
  never clamp).

## R3 — The shared warmth predicate

- **Decision**: extract the spec-031 circumstance (own tile sunbeam, or
  mutual partner on a sunbeam) into one `World` helper; both
  `apply_sleep_relief` (rate choice + floor escape) and
  `resolve_activity_ends` (finished level) call it.
- **Rationale**: the spec's edge case demands one predicate that can
  never drift into two; `resolve_activity_ends` has `&self` world access
  and the sleeper's duet partner, so the helper needs only
  (kitty, partner).
- **Alternatives considered**: recomputing inline in world.rs — rejected
  as the exact drift the spec forbids; caching warmth on the activity —
  rejected, the escape is per-tick circumstance (US2 scenario 3).

## R4 — Shape of the default-0 equivalence proof (FR-007 / SC-001)

- **Decision**: three layers, no new golden files: (a) every existing
  sleep/cosleep/conduction test runs at floor 0 untouched — the unit
  proof; (b) one explicit test pins a floor-0 nap's end tick equal to
  today's law; (c) Experiments' acceptance run (pinned seed, action for
  action against the served toml) is the world-level proof, per their
  handover.
- **Rationale**: house precedent (spec 050 "absent = the old rule");
  the cheapest layer that exercises the claim (rule 5's third lie —
  wrong layer — cuts the other way here: the law is per-tick relief, so
  unit tests on the relief and end functions ARE the right layer, with
  the seam check as belt-and-braces).
- **Alternatives considered**: recording new fixture streams
  (fog_continuity-style) — rejected: no observation stream changes; the
  changelog entry carries no compatibility marker and the equivalence
  run is that claim's evidence.

## R5 — Where the doc line lands

- **Decision**: one comment line in `cloudkitty.toml` `[actions]` beside
  `sleep_relief_sunbeam` naming the key, its default, and the law; the
  key registered in `settings.rs` (spec 052) so `GET /settings` and the
  boot log serve it.
- **Rationale**: the handover's acceptance list names exactly these two
  surfaces; `docs/plugins.md` is NOT touched (no wire change).
