# Implementation Plan: Fog Gen 1 — the 3.0 observation wall

**Branch**: `049-fog-gen1` | **Date**: 2026-09-03 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/049-fog-gen1/spec.md` (48 FRs, 8 user stories, 13 SCs; every clarification owner-ruled, no markers; post-plan clarify folded 2026-09-03).

## Summary

Narrow every cat's view to a Euclidean disc (`dx² + dy² ≤ r²`, integer), keep hearing global, and give each cat a one-slot-per-element-kind memory that is refuted on sight — the same view for policies, built-in behaviours, and external advisors, enforced by construction through one per-kitty **fog view** that is the only world any decider or encoder ever receives. Ride the wall with the owner-ruled bundle: four permanent by-id kitty rows; the meow digest moved onto those rows as per-speaker (recency, rate, want-intensity) cells with the global digest deleted; scene age and a neighbour-in-water bit; a knowledge-gated want law, a widened here law, an engine-stamped `reply`/`pos` on every meow, answers-me bits, and the scripted reply ladder; persistent-heading exploration for a blind scripted cat; and the 3.0 config hygiene (section-absence defaults, seven retired keys, snapshot shims all deleted; `evals/v2` cut; every live config migrated). Observation schema 4 → 5, **exactly 404 floats** at the served config, menu 39, logit budget 55; plugin wire 2 → 3. Post-plan clarify (2026-09-03, four owner rulings, timeline @ 138a289) folded: heard friends drive built-in targeting but never the social want gate (which reads "no idle friend in view"); the exploration heading is engine-recorded from any applied move; the distress-gated intervention is its own 3.0 spec before the cutover, not here; the plugin wire version bumps.

Technical approach: the engine already derives every width from `observe.rs` block constants and `ObservationConfig`, so the layout work is extending the block constants and the encoder loops and letting `block_widths()` / `observation_len()` / `token_layout()` / `ActionCodec::v2` move the tokenizer, codec, mask and Python surface automatically, with the schema pin test asserting each derived number literally. The behavioural work is four engine seams — the fog view (`WorldSnapshot::fog_for`), the per-tick memory update in the environment phase, `message_legal` restructured for the want/here tiers over the fog view, and `emit_message` stamping `pos`/`reply` — plus the built-in ladder (`announce` → reply ladder, `seek_element` → remembered tile / exploration, friend targeting over visible ∪ heard). The hygiene work is deletion with a migration note and a config-completion pass over 65 files.

## Technical Context

**Language/Version**: Rust, toolchain pinned by `rust-toolchain.toml` (no change); Python 3.11 for the binding tests and the migration/re-baseline scripts (existing venvs).

**Primary Dependencies**: existing workspace only — `cloudkitty-core` (kitty state, snapshot, law, behaviours, config), `cloudkitty-rl` (observation, codec, mask, tokenizer, artifact loading, eval suite), `cloudkitty-server` (boot validation, API additive fields), `cloudkitty-py` (constants and `observation_len` re-exported, unchanged code). No new crates, no new external dependencies.

**Storage**: world snapshot JSON (save/restore) gains `memory`, `explore_heading` on kitties and `pos`, `reply` on meows; pre-3.0 saves do not load (`--fresh` cutover, owner-ruled). No database.

**Testing**: `cargo test --workspace --no-fail-fast` (baseline count recorded at cycle 0 of the redden list; last known main count 817/0 at spec 048), fmt + clippy CI-exact, property tests (visibility, memory, want/here/reply law, mask-equivalence on the fog view), the golden family (evolution golden, strip witness, run_json golden — all three regenerate with justification: fog is an intentional dynamics move), the defaults-stamp test (moves: new keys with defaults — `[stamp]` claimed), the two config sweeps + `evals/v2` freeze guard, `binding_continuity.py` re-baseline, pytest surface (obs space shape derives), PettingZoo conformance.

**Target Platform**: unchanged (server binary on the Linux box; dev on macOS). No deploy in this arc — cutover is step 7's `update.sh --fresh`.

**Project Type**: Rust workspace — engine crates + serving binary + Python binding.

**Performance Goals**: per tick, five fog views (filter ~30 entities each) and five memory updates (5 kinds × ~25 elements) — O(roster × entities), negligible against decision dispatch. Observation 225 → 404 floats and v3 tokens 30 → 16 (message-kind tokens gone, kitty rows +1): forward cost moves by the widths only. No per-tick allocation growth beyond the views.

**Constraints**: determinism preserved (memory update and law are pure functions of state; exploration draws come from the cat's own `DecisionRng` and only on redraw; no new master-RNG draws); Article V tick order unchanged (memory updates inside the environment phase); mask-oracle doctrine kept (the message mask still probes `message_legal`, the activity mask still probes `validate`, both now over the fog view, with a new equivalence guard); one-serialization posture (the API gains fields, changes none); `HEAD_KINDS`, `ACTION_SCHEMA_VERSION`, `MASK_SCHEMA_VERSION`, `GLOBAL_STATE_SCHEMA_VERSION` frozen.

**Scale/Scope**: ~14 Rust source files across three crates, four config-file edits, 65 TOML migrations (scripted), `evals/v2` (six files + manifest), three living docs (`encodings.md`, `meows.md`, `plugins.md` note) + CHANGELOG, the migration note, `binding_continuity` reference record, and the redden list. Roughly 2× spec 033's footprint.

## Constitution Check

*GATE: evaluated pre-Phase-0 and re-checked post-design — PASS, no violations.*

- **Article I (Kitties Cannot Suffer)**: needs stay bounded; no new negative state. The safeguard stays existence-based (FR-047, owner ruling i) — Article I's "must exist and be reachable" is untouched; fog changes what a cat *knows*, not what the world *provides*. Memory and exploration exist precisely so the scripted anchors do not starve under fog (US5). PASS.
- **Article II (Cannot Die)**: no population mechanic touched. PASS.
- **Article III (Cannot Be Alone)**: roster untouched; the new roster-vs-slots check (FR-011) refuses rosters *above* slots + 1 and never below 2. PASS.
- **Article IV (Engine Is the Law)**: every new law lives in the engine — visibility in the fog view, want/here legality in `message_legal`, the reply stamp in `emit_message`, memory in the environment phase. Behaviours still only propose; an illegal want or here downgrades to Silent exactly as today. The fog view makes "behaviours know only what the engine shows them" structural (FR-021), strengthening Article IV's information boundary for external advisors too. PASS.
- **Article V (Server-Authoritative, Deterministic)**: memory update is a pure function of the resolved world, inserted into phase 3; meow stamps are pure functions of the emitter's state and the start-of-tick meow buffer; exploration redraws use the dealt per-kitty `DecisionRng`, so the master stream is unchanged in shape; tick order unchanged; same seed + config + ticks → same world including memory (SC-006). The schema bump is the sanctioned generation-gate mechanism. PASS.
- **Article VI (Spec-First, Test-Guarded)**: this plan follows the spec; every new constant is configuration with a documented default (`[vision] radius`, `memory_timeout_ticks`, `[meow] digest_window_ticks`, `[behavior] reply_intensity_floor`) except the two frozen normalisers (H = 24, staleness 40), which the spec freezes deliberately with reasons and which are guarded by literal pins; the property suite (Articles I–III) stays a required CI gate and gains fog-era guards. PASS.

**Complexity Tracking**: no violations to justify.

## Project Structure

### Documentation (this feature)

```text
specs/049-fog-gen1/
├── spec.md              # 8 US / 48 FRs / 13 SCs — owner-ruled, no markers
├── plan.md              # This file
├── research.md          # Phase 0: R1–R16 design decisions with rationale
├── data-model.md        # Phase 1: state, config, view and schema entities
├── quickstart.md        # Phase 1: validation guide (build, pins, property runs, smoke)
├── contracts/
│   ├── observation-v5.md      # THE normative layout: offsets, masks, widths, pins
│   ├── meow-law-v5.md         # want/here legality, reply stamp, scripted ladder, keys
│   └── config-3.0-migration.md # removed keys, formerly-optional sections, new keys
├── checklists/requirements.md
├── redden-list.md       # implementation-time: red-first cycle record (house standard)
└── tasks.md             # Phase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
crates/cloudkitty-core/src/
├── kitty.rs           # Kitty += memory: ElementMemory, explore_heading: Option<Direction>;
│                      #   seven restore shims + Pursuit.improved_at default DELETED
├── element.rs         # (no change; ElementType::ALL is the memory kind order)
├── meow.rs            # Meow += pos, reply; intensity serde default DELETED (eighth shim);
│                      #   message_legal restructured: want tier
│                      #   (armed ∧ top need ∧ no known relief) and here tier
│                      #   (adjacent ∨ (matching want audible ∧ referent visible)),
│                      #   both over a FogView; heard_unseen() helper; want↔here pairs
├── world.rs           # WorldSnapshot::fog_for(kitty, radius) → FogView; recent_meows
│                      #   retention = digest_window_ticks; update_memories() in the
│                      #   environment phase; explore_heading written on applied Move;
│                      #   enforcement calls message_legal over the live fog view
├── action.rs          # emit_message stamps pos + reply (start-of-tick meows only); PROPOSAL_WIRE_VERSION 2 → 3 (R15)
├── grid.rs            # Position::euclid_sq / visible_from(r) (integer)
├── config/mod.rs      # VisionConfig {radius, memory_timeout_ticks}; MeowConfig +=
│                      #   digest_window_ticks (recent_window_ticks doc rewritten);
│                      #   BehaviorConfig += reply_intensity_floor: Option<f32>;
│                      #   13 + 4 #[serde(default)] section shims DELETED; seven
│                      #   retired-key Option fields DELETED; ElementRule.max comment fixed
├── config/validate.rs # validate_vision (r ≥ 2); validate_meow (window = k × cooldown,
│                      #   k ≥ 1; floor ∈ [0,1]); seven rejectors + tests DELETED
├── behavior/mod.rs    # DecisionContext.world: Arc<FogView>; decision_jobs builds one
│                      #   view per kitty; announce() → the reply ladder
│                      #   (WaitForMe > {reply, own want} > ambient here > Silent)
├── behavior/needs_driven.rs  # seek_element: visible ∪ remembered tile → explore;
│                      #   groom_response walks to last-meow pos; explore(ctx)
├── behavior/selection.rs     # priced_nearest_element over visible ∪ remembered;
│                      #   playmate / friend scans over visible ∪ heard-unseen
├── behavior/script.rs # DecisionRequest.world = the fog view's snapshot (plugins fogged); v = 3
├── spawn.rs           # (no change — FR-047)
└── test_support.rs    # decision_context builds through the fog view

crates/cloudkitty-rl/src/
├── observe.rs         # OBSERVATION_SCHEMA_VERSION 4→5; SELF_BLOCK 34→85, KITTY_SLOT
│                      #   20→62; MEOW_DIGEST deleted; by-id permanent rows (fill rule
│                      #   for kitties: roster order, R1 displacement kept inert for
│                      #   critters/never reachable for kitties); row-state masking;
│                      #   memory / scene-age / water-bit / message-block / intensity /
│                      #   answers-me encoders; block_widths += memory, msg widths
├── config.rs          # kitty_slots default 3→4; roster ≤ kitty_slots+1 check in the
│                      #   dual-surface loader (load_configs_from_str)
├── attn.rs            # token_layout: msg group removed (type rows 22→7); widths derive
├── codec.rs / mask.rs # no rule change; menu 34→39 and mask 50→55 derive; the mask
│                      #   probes over the fog view
├── global_state.rs    # unchanged (unfogged, v1)
├── expand.rs          # refuses obs schema 5 targets (source generation pinned)
├── suite.rs           # evals/v2 manifest
└── bin/kitty-eval.rs  # --suite default evals/v2

crates/cloudkitty-rl/tests/
├── schema_four_pins.rs → schema_five_pins.rs   # 404 / 39 / 20 / 55 / v5 literal pins
├── mask_oracle.rs     # + fog-view ≡ full-snapshot mask equivalence
├── shipped_configs_rl.rs, ../cloudkitty-core/tests/shipped_configs.rs  # evals/v2 assertion
└── (new) fog_visibility.rs, fog_memory.rs, meow_law_fog.rs  # property + scenario guards

crates/cloudkitty-server/src/
├── lib.rs             # boot: roster-vs-slots refusal message; "vision radius r" boot line
└── api.rs             # no change (Kitty/Meow serialize additively)

Config + records
├── cloudkitty.toml, training.toml, clowder/tiny-world.toml, evals/v2/*.toml (+manifest)
├── 65 in-scope tomls (scripted completion pass) / config-sweep-exclusions.txt (+ evals/v1, result-backing families)
├── docs/encodings.md (schema 5), docs/meows.md (law under fog, digest), docs/plugins.md (fogged world note)
├── CHANGELOG.md (Unreleased: [obs-schema] [world-fresh] [stamp])
├── experiments/exp-006-character-gen/binding_continuity.py (3.0 reference record, all-scripted seating)
└── specs/049-fog-gen1/contracts/config-3.0-migration.md (the migration note)
```

**Structure Decision**: single Rust workspace, existing crate boundaries; the fog view lives in `cloudkitty-core` because it is engine law (behaviours and plugins consume it) and `cloudkitty-rl` encodes from it. No new crate, no new binary.

## Test plan (rule 5/6 — sorted before running)

Guards that MUST go red under the named mutation, at the cheapest layer, before being trusted (recorded in `redden-list.md` with predictions written first, `cargo test --workspace --no-fail-fast`, count re-read after every restore, commit before every cycle):

| Guard family | Layer | Mutation that must redden it |
|---|---|---|
| Visibility disc (SC-002) | core property test over random worlds/radii | `≤` → `<` on the edge; Euclidean → Manhattan |
| Fog view leaks nothing (FR-021) | core: instrumented context read-recorder | drop the element filter in `fog_for` |
| Mask equivalence on the fog view | rl `mask_oracle` | compute the mask on the full snapshot for one entry |
| Memory update rules (SC-003) | core property test | skip the refute branch; nearest → farthest; clear on every tick |
| Memory persists + determinism (SC-006) | core `snapshot_resume` + `determinism` | zero memory on restore |
| By-id rows / row-state masks (US2) | rl `observe` unit tests | sort rows by distance; mask needs on seen rows |
| Digest recency/rate/intensity (US3) | rl unit tests with staged meows | rate denominator → window; intensity → 0 |
| Answers-me bit + stale-at-meow position (FR-012/041) | rl unit tests | use live pos; drop the "want before here" ordering |
| Want law (SC-010) | core property test over staged worlds | drop the top-need clause; drop the memory clause; drop the critter clause for play; let a heard-unseen friend silence `want_cuddle`; count a mid-scene visible friend as idle |
| Built-in friend targeting over heard-unseen (FR-022) | core behaviour tests | filter heard candidates by true state; keep the target on arrival with the friend asleep |
| Plugin wire version (FR-048, SC-013) | core plugin e2e | leave the constant at 2 |
| Here law + reply stamp (SC-010) | core unit + property | stamp reply on adjacency alone; count same-tick wants |
| Scripted reply ladder (US8) | core behaviour tests | pick lowest intensity; ignore floor; bypass cooldown |
| Reply floor unset = byte-identical (SC-011) | core golden-style run diff | fire replies with floor None |
| Exploration redraw rule (FR-023, SC-012) | core behaviour tests + seeded first-sight trial | redraw every tick; allow reverse |
| Actions identical at world-covering r (SC-004) | core 20k-tick seeded diff vs pre-fog pin | filter elements at infinite r |
| Schema pins (SC-001) | rl `schema_five_pins` | any width constant ±1 |
| Schema-4 artifact refused (SC-008) | rl `artifact_v3_reject` / server `policy_v3_kitty` | skip the pin compare |
| Config strictness (SC-007) | core config tests + both sweeps | re-add one `#[serde(default)]` |
| Pre-3.0 meow entry refused (FR-032) | core `snapshot_resume` inverse guard, one literal per required field | re-add the `intensity` default |
| Roster vs slots (FR-011) | rl config + server boot test | `>` → `>=` |
| Radius floor / window multiple / floor range | core validate tests | off-by-one each |

Kept behaviour that must stay green: every scripted scenario at a world-covering radius (action stream), the stamp test moving ONLY by the new keys (assert by diffing the serialized defaults), invariants proptest, welfare longrun at r = 5 (records, does not gate), determinism, turn-order fairness, joint-action parity, plugin e2e (now over the fogged request, asserting v = 3), the refuse-unknown-version fallback guard, `water_safeguard.rs` at r = 5 (FR-047: the safeguard stays existence-based under fog).

## Sequencing inside the arc

1. Fog view + visibility + memory (US1, US5 core) — behind the config key, world-covering radius = old behaviour, so the suite stays green until the encoder moves.
2. Observation schema 5 (US2–US4, FR-025–FR-028) + pins + tokenizer + docs/encodings.
3. Meow law, stamps, digest fields, answers-me (US7) — `message_legal` over the fog view.
4. Scripted ladder, exploration, targeting over remembered/heard (US5 rest, US8).
5. 3.0 config hygiene + migrations + evals/v2 + migration note (US6).
6. Goldens regenerated with justification; `binding_continuity` 3.0 reference record; CHANGELOG; redden list closed; review.

Each step lands green on the branch; the golden family is regenerated once, at step 6, from one run.
