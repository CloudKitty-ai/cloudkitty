# Research: Gen 2 Observation Schema Bump (spec 058)

Phase 0 output. Every plan-time unknown from the spec resolved, with
decision / rationale / alternatives. Ground truth read from the
worktree at origin/main 3d24af73; the field-read sweep over
`crates/cloudkitty-core/src/behavior/` was delegated (rule 9) and its
citations re-checked at the quoted sites.

## R1. Distance metric — Manhattan throughout

- **Decision**: d = |dx| + |dy| for every distance and bearing cell;
  bearing = the L1 unit pair (dx/d, dy/d), zero-distance pinned to
  (0, 0).
- **Rationale**: ruled form's "/40 in native walk-cost units"; every
  decision consumer is Manhattan (movement N/E/S/W, meow audibility
  `meow.rs:420`, all schema-5 observation distance cells, the
  normative slot-fill `sort_by_proximity`); Experiments confirmed
  2026-10-09 that F-052/F-053 evidence is metric-agnostic and was
  collected under schema 5's Manhattan cells. Owner's question
  resolved in-session 2026-10-09.
- **Alternatives**: Euclidean (true unit vector; rejected — mixes
  metrics with every consumer, and visibility membership already
  rides the presence bit); mixed Euclidean-bearing/Manhattan-magnitude
  (rejected — two metrics in one cell group).

## R2. Hidden friend fields — removed, not zeroed

- **Decision**: the five hidden needs and happiness have NO cells in
  the v6 kitty row; the leak audit (FR-007a) is a layout enumeration.
- **Rationale**: the strips ruling's "come out" form; removal makes a
  leak structurally impossible and shrinks the row; a zeroed cell is
  a cell a refactor can silently re-fill.
- **Alternatives**: keep-at-zero (rejected: weaker guarantee, dead
  cells; the e_col reserve is the one deliberate exception, with an
  inertness proof instead).

## R3. View-hole strip list (FR-011) — happiness only

- **Decision**: the only row cell stripped as a pure view hole is
  `happiness`. All other remaining row cells have live behavior-rule
  reads or are digest/world facts the visibility ruling keeps.
- **Rationale**: delegated sweep over every `Kitty` field reachable
  through `FogView` found behavior rules read exactly: `id`, `pos`,
  `needs` (Play, Bath, top-non-Play), `activity`, `activity_clock`.
  `happiness` has zero non-test read sites outside the encoder. The
  five non-bath need cells leave via the visibility ruling (R2), not
  as view holes; bath stays (S§1 amendment). Scene age stays (the
  `activity_clock` proxy — `expected_wait`, `is_in_progress` reads);
  water/sunbeam bits stay (world facts, `partner_wet`
  selection.rs:367, `warm_occupant` needs_driven.rs:624); message
  block, want intensities, answers-me stay (digest — visible by
  ruling); partner flag and is-my-target stay (activity/pursuit
  reads).
- **Alternatives**: none viable — the list is an enumeration, not a
  choice.

## R4. Waypoint-direction cells — 2 cells, self block, pure derivation

- **Decision**: two cells in the self block: the L1 unit bearing from
  `me.pos` to `Lattice::for_world(w, h, vision.radius)
  .waypoint(me.explore_waypoint)`; (0, 0) when standing on it. No
  distance cell, no present bit.
- **Rationale**: GEN2-INPUTS rules "add the direction to the waypoint
  as observation cells" — direction only. The `Lattice` is stateless
  and rebuilt from config (sweep §3), the observer's own
  `explore_waypoint` index is never blanked by `fog_for`, and the
  tour always exists — there is no "no waypoint" state, so a present
  bit encodes nothing. "Stop" is pos == waypoint, which (0, 0)
  carries.
- **Alternatives**: bearing + magnitude like other entities (rejected:
  the ruling asked for direction; the waypoint is a route hint, not
  an entity — magnitude would invite distance-keyed behaviors the
  exploration rule itself does not have).

## R5. Identity block — extend the existing traits cells; config is
the one home

- **Decision**: the identity block is 14 cells replacing the six
  trait cells in place: need-rate multipliers (6, existing
  `need_rate_for / reference_need_rate` clamp [0,4]), comfort slack
  (1, ticks / 40, clamped at 1), consent line (1, /100), per-source
  favourite weights (6, one per NeedKind, raw [0,1], one-hot in the
  single-source case, all-zero = no favourite). Each new dial gets a
  per-kitty roster override with a world default, the exact
  `need_rate_for` pattern (config/mod.rs:1440). The observation
  encoder and (in spec 059) the parameterized teacher read the SAME
  accessors — one home for the dials.
- **Rationale**: the six need-rate multipliers ALREADY exist as the
  self-block traits (sweep §4) — the ruling's identity block is an
  extension, not a parallel block. Routing the teacher through the
  same accessors later is what makes the identity input honest: the
  cat sees the dials its own teacher ran on.
- **Alternatives**: encode from today's global `behavior.consent_line`
  / `playful_comfort` without per-kitty plumbing (rejected: cells
  would be roster-constant and spec 059 would immediately re-plumb —
  two touches for one); defer all three dials to 059 (rejected: the
  schema wall is HERE; 059 must not need a second bump).
- **Normalizers**: slack /40 joins the frozen-literal family (a time
  quantity, same scale discipline as staleness); consent /100 (a
  need-level); favourite raw. All frozen literals per FR-002's
  pattern.

## R6. Visibility enforced at the encoder, not FogView

- **Decision**: 058 removes hidden fields from the ENCODED row;
  `FogView` keeps exposing full friend state to scripted rules.
- **Rationale**: trained minds only ever see the encoded vector, which
  is what the Gen 2 hidden-needs claim scopes to. The scripted
  teacher's reads of hidden needs are spec 059's rule-5 audit (bath
  reads stay — S§2); gutting FogView here would break
  `needs_driven`/`selection` before 059 lands and tangle the two
  specs' diffs.
- **Alternatives**: type-level hiding in FogView (stronger; deferred —
  059 can tighten after its audit decides which reads remain legal).
- **Reported, not fixed (CLAUDE.md rule 3)**: the plugin advisor wire
  (`script.rs:104`) serializes visible friends' FULL state (all six
  needs, happiness) to external plugins — a surface outside the
  observation vector and outside this spec. Flagged to the owner in
  the plan report; any Gen 2 claim about hidden needs scopes to
  trained seats, not plugin advisors, until that wire is ruled on.

## R7. Which schema versions bump

- **Decision**: OBSERVATION 5 → 6. GLOBAL_STATE 1 → 2 (each kitty's
  block gains the +8 identity extension; the critic must see the
  dials — FR-009/CTDE). ACTION and MASK hold at their versions
  (menu and mask semantics untouched; mask legality reads the
  engine, not the observation layout — sweep §2 consumers).
- **Rationale**: version ids are per-contract; only the two whose
  layout moves may bump (changelog/compat discipline).
- **Global state details**: KEEPS its episode clock (the critic is
  training-only and finite-horizon value legitimately reads time;
  the clock pathology was actor-side limit cycles — K§2's ruling
  names the observation input). KEEPS x/width-normalized positions
  (training runs at the served 20×20 only by ruled staging; the
  critic is discarded at serving, so size-entanglement buys nothing
  to fix in this wall). Both decisions recorded in the contract.

## R8. Column map — derived from the encoder's constants, v5 pinned
against its existing oracle

- **Decision**: a `schema_map` module in `cloudkitty-rl`:
  `column_map(version) -> Result<&'static Map>` with named cells for
  v5 and v6. v6 entries are BUILT from the same offset constants the
  encoder uses (never restated literals); v5 entries are a literal
  historical table validated by a test against `schema_five_pins.rs`'
  asserted numbers. Unknown version or name = error. The map also
  carries the action-menu names for action codec v2 (the table
  codec.rs documents), so readers stop hardcoding `ACT_PLAY = 14`.
  The Python binding exports the whole map as a dict alongside the
  existing `*_SCHEMA_VERSION` constants.
- **Rationale**: FR-015; "one source" discipline — a map restating
  offsets by hand is a second home that rots. v5 cannot be derived
  (the encoder will compute v6), so it is pinned literal + oracle
  test instead.
- **Alternatives**: generate the map from the contract doc (rejected:
  docs are not compiled); Python-side map in `experiments/`
  (rejected: that is the lane the map exists to protect, and it
  would not be versioned with the schema).

## R9. Clock removal mechanics

- **Decision**: the observation loses its clock cell; `encode()`
  loses the `episode_clock` parameter; `behavior::served_clock` and
  the serving-side plumbing that fed it are removed (their only
  consumer was this cell). Global state keeps its own clock (R7).
- **Rationale**: K§2 "the cell comes out"; dead parameters invite
  reconnection.

## R10. Dirt reserve — 2 cells at the self-block end, e_col proof bar

- **Decision**: two cells appended at the END of the self block,
  always 0.0 until armed by a future config flag that does not exist
  yet. Inertness proof: the F-058/e_col bar — a test asserts
  encodings are bit-identical with the cells present-at-zero vs the
  baseline layout with them absent is NOT testable post-bump (the
  layout includes them); the honest check-1 form is: (a) the cells
  read exactly 0.0 over randomized states, and (b) a policy forward
  pass is bit-identical under any perturbation of upstream dirt
  state (no engine path writes them), pinned by a grep-level test
  that no encoder path can write the reserve range plus the runtime
  zero assertion over the property suite.
- **Rationale**: S§2 rider 2; e_col precedent (F-058: "additive,
  bit-identical to stock at zero, validated pre-freeze").
- **Placement**: end of self block, not end of vector — the dirt
  compartments are SELF bath-state; the e_col pattern appends to the
  owning block so arming never moves another block's offsets.
  (e_col itself sat at the vector end because it was the only
  addition; the principle is "append where you belong".)

## R11. Vocabulary flags — no engine change, existing oracle

- **Decision**: no code change. The Gen 2 training world config arms
  trill + ekekek; `vocabulary_flags.rs::flags_never_move_a_single_
  layout_number` already pins layout identity across flag settings
  and `HEAD_KINDS` has carried both kinds since spec 033. Implement
  step verifies the test exercises the armed direction and adds the
  config note to the contract.
- **Rationale**: FR-017; S§7 ("flags gate legality only").

## R12. Heard rows under the new layout

- **Decision**: a heard row carries: present 0, the four spatial
  cells (bearing + two magnitudes) to the last audible meow
  position, bath 0 (not known by hearing — hearing carries the
  digest, not coat state), activity/partner/target/water/sunbeam/
  scene-age masked as today, message block + want intensities +
  answers-me live.
- **Rationale**: FR-012 precedent (schema 5 heard rows) carried into
  the new spatial cells; bath is sight-and-scent grounded (S§1) and
  a heard-only friend is outside both.
- **Note**: FR-001a applies to heard rows too — a last-meow position
  can be far outside the vision disc (digest window reaches
  radius + m), so heard-row distances exceed r routinely; the no-
  clamp pin covers them.
