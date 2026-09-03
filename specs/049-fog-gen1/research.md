# Research: Fog Gen 1 — the 3.0 observation wall (spec 049)

No `[NEEDS CLARIFICATION]` markers remain (Q1 and Q2 owner-ruled 2026-09-02, three draft flags ruled 2026-09-03). This file records the plan-level design decisions the implementation rests on, each verified against HEAD `0f99d09` (branch) / main `6bf9186`.

## R1 — One fog view, one enforcement point

- **Decision**: add `WorldSnapshot::fog_for(kitty_id, radius) -> FogView` in `cloudkitty-core`. `FogView` wraps a filtered `WorldSnapshot` (kitties and elements inside the observer's disc, `recent_meows` whole, width/height/tick unchanged) plus `roster: Vec<KittyId>` (ids only, ascending) and `observer: KittyId`. It derefs to `WorldSnapshot`, so every existing accessor (`others`, `elements_of`, `critters`, `kitty`, `element_at`, `kitties`) is already fogged. `DecisionContext.world` becomes `Arc<FogView>`; `decision_jobs` builds one per kitty from the shared start-of-tick snapshot; the plugin `DecisionRequest.world` is the view's snapshot (same JSON shape, fogged contents); `encode_observation`, `TargetTable::build`, `legal_action_mask` and `legal_message_mask` take the view.
- **Rationale**: FR-021 demands structural enforcement. The snapshot is read in twelve places across `needs_driven.rs` / `selection.rs` and by the encoder; filtering at the source makes drift impossible and keeps the "read-only by construction" doctrine of `DecisionContext`. The roster travels with the view because by-id permanent rows (FR-011) need every friend's id even when the friend is unseen and silent; ids are not knowledge.
- **Private state stripped**: friend records in the view have `memory` and `explore_heading` reset to default — a friend's mind is not observable (imitability principle). Pre-existing fields on friend records (`announce_armed`, cooldowns, pursuit) already leak today and are out of this spec's scope; recorded per rule 3.
- **Alternatives considered**: per-call visibility checks at each read site (rejected: twelve sites, drift-prone, no structural guarantee); a new context type without `Deref` (rejected: touches every behaviour line for no gain); putting `roster` on `WorldSnapshot` itself (rejected: `WorldSnapshot` is the save/wire shape; a serde-skipped field would be empty on deserialised snapshots).

## R2 — The mask still probes the law, now over the view

- **Decision**: `legal_action_mask` builds its probe world from the fog view's snapshot; `legal_message_mask` probes `message_legal` over the view. A new `mask_oracle` guard asserts, over random worlds, that the activity mask computed on the view equals the mask computed on the full snapshot.
- **Rationale**: every menu action is local (moves are one tile; partnered actions need Manhattan ≤ 1; eat/drink need adjacency), so nothing outside the disc can change a verdict at r ≥ 2 — and the equivalence guard proves it rather than assuming it. Enforcement at apply time still reads the live world, so a mask-legal action stays exactly as enforceable as today.
- **Alternatives considered**: keep the mask on the full snapshot (rejected: the mask would then encode knowledge the observation does not carry — a policy could learn "row k is legal" as a proxy for "cat k is adjacent" only from the mask; harmless today, but it breaks the one-information-set principle).

## R3 — Memory lives on the kitty, updates in the environment phase

- **Decision**: `Kitty.memory: ElementMemory` = `[Option<MemorySlot>; 5]` in `ElementType::ALL` order, `MemorySlot { pos, last_seen: u64 }`. `World::update_memories(config)` runs as the last step of `environment_phase` (after `safeguard`), per kitty per kind: nearest visible element of the kind (Manhattan, ties by lower id) → overwrite with `last_seen = tick`; else if the remembered tile is inside the disc → clear; else keep; then the optional timeout. Serialised with the kitty (no shim — the wall is `--fresh`).
- **Rationale**: the next tick's snapshot must carry the memory every decider reads (Article V: decide against the frozen snapshot). Placing the update after the environment resolves means the memory reflects the world the cat will see next tick — the same moment its `pos` and the elements are frozen. No RNG. Chow is presence-only because an emptied bowl expires in the same phase (`element.rs:108`), so no snapshot ever holds one.
- **Alternatives considered**: updating at observation time (rejected: the observation must stay a pure function of the snapshot; encoding would mutate state); a separate memory table on `World` keyed by kitty (rejected: the kitty is the natural owner and the save format is being broken anyway).

## R4 — Heard-unseen friends are a reduction over `recent_meows`, not state

- **Decision**: `Meow` gains `pos: Position` (stamped at emission). `FogView::heard_unseen()` returns, for each roster friend not visible, its freshest audible meow inside the digest window (`tick − m.tick < digest_window_ticks`, own meows excluded) as `(id, pos, tick)`. The encoder's heard-row position, the scripted friend-targeting candidate set, and the want law's "heard at a known position" clause all call this one helper.
- **Rationale**: owner ruling (coverage pass): no cat memory in Gen 1; the position is the meow's, not the cat's. One helper keeps the three consumers from drifting (048's one-shared-definition precedent).

## R5 — Start-of-tick meows only: same-tick replies cannot exist

- **Decision**: every meow-derived rule — heard positions (R4), "matching want audible" in the here law and the reply stamp, the digest cells, the answers-me bits — reads only meows with `m.tick < tick`. Enforcement runs mid-tick against the live buffer (world.rs:376, after earlier turns applied), so `message_legal` and `emit_message` filter the buffer by tick rather than trusting its contents.
- **Rationale**: owner ruling 2 ("latency floor one tick; id order never matters"). Without the filter a later-id cat could reply to an earlier-id cat's same-tick want at enforcement while the mask (probing the start-of-tick snapshot) said otherwise — a divergence that would *speak*, not merely silence, violating the spec-033 review's divergence doctrine (Finding 5: divergence may only ever silence).
- **Retention**: `recent_meows` is pruned at `recent_window_ticks` today (world.rs:1167, and a buffer-length test at :1909); both move to `digest_window_ticks` (30). The cooldown map on the kitty (`meow_cooldowns`) keeps using `recent_window_ticks`.

## R6 — `message_legal` grows a view parameter; want law is one predicate

- **Decision**: `message_legal(kitty, kind, tick, config, view: &LawView)` where `LawView` is what both the mask (fog view) and enforcement (live world filtered for the emitter) can produce: visible elements, visible kitties, roster, start-of-tick meows. Want tier: `armed ∧ top_need(kind) ∧ !known_relief(kind, view)`; `known_relief` per kind: eat/drink → visible element or memory slot present; cuddle/bath → an *available* friend visible or heard-unseen (availability = the existing partner-availability predicate); play → the cuddle/bath clause ∧ no critter visible or remembered (bug or greeble slot); sleep → no knowledge gate. `announce()` keeps calling `message_legal` (it already does), so the scripted want and the mask share the predicate by construction.
- **Rationale**: FR-036's "ONE predicate"; the enumerated-arms style of spec 033 (a kind without a tier is a compile error).
- **Alternatives considered**: a separate `want_legal` helper called from both (rejected: two entry points invite a parallel definition).

## R7 — Here law and the reply stamp share one condition

- **Decision**: `reply_condition(kind, view, tick)` = matching want from another cat audible (start-of-tick, inside the window) ∧ referent visible from the speaker. Here tier legality = `cooldown ∧ vocabulary ∧ (adjacent(referent) ∨ reply_condition)`. `emit_message` stamps `reply = reply_condition` for here kinds (false otherwise) and `pos = kitty.pos`. Pairs are a const table `WANT_HERE_PAIRS: [(WantEat, HereFood), (WantDrink, HereWater), (WantSleep, HereSunbeam), (WantPlay, HereCritter)]` in `meow.rs`, used by legality, the stamp, the answers-me encoder, and the scripted ladder.
- **Rationale**: owner ruling 2; stamp and trigger are separate by design (an ambient here landing while a want is audible is a reply) — sharing the *condition* while keeping the *trigger* in the behaviour is exactly that separation.

## R8 — Row state and the by-id fill

- **Decision**: `TargetTable::build` for kitties becomes roster order (ids ascending, `None` for surplus rows); `fill_slots` with target priority stays for critters and stays *present* for kitties (dead path at roster ≤ slots + 1, owner: keep inert). Row state per friend: `Seen` (in view), `Heard` (in `heard_unseen()`), `Silent`. The encoder emits per state: Seen → all 62; Heard → dx/dy/dist to the meow position, message block (22–61) live, everything else 0 (`present` 0); Silent → 62 zeros.
- **Rationale**: FR-011–FR-014; the pointer heads and `PlayKitty(row)` need stable naming; the tokenizer is indifferent to row order.
- **Validation**: roster > kitty_slots + 1 is refused in `load_configs_from_str` (the dual-surface loader every tool uses) and at server boot, naming both numbers. Lab rosters below five leave vacant rows.

## R9 — Exploration heading: engine-recorded from the applied Move

- **Decision**: `Kitty.explore_heading: Option<Direction>`, written by the engine on every applied `Move { direction }` (in `action::apply`), never by a behaviour. The built-in explore step: if the heading is `None` or the wall ahead is within `radius` (`distance_to_wall(pos, heading) ≤ radius`, integer arithmetic on bounds), redraw once from `ctx.rng` among directions that are neither the reverse nor wall-within-radius, falling back to any non-reverse, then the current heading; then propose one step in the heading through the existing step rule.
- **Rationale**: behaviours are read-only by construction (`DecisionContext` doc, world.rs:641) and the decision seam carries only `(action, message)` — a behaviour cannot write cat state directly, and widening the seam for a scripted-only need would touch the policy codec. Recording the applied move gives the ruled "one field of cat state" with the ruled redraw rule intact. **Consequence the spec must carry**: a water-avoiding sidestep or a navigation move also sets the heading, so after a refuted memory the cat continues the way it was walking, and a sidestep rotates the heading (the spec's "a sidestep moves the cat, not the heading" edge-case line — a Product assumption, not an owner ruling — is amended to match; see spec Edge Cases).
- **RNG shape**: draws only on redraw, from the per-kitty dealt seed; the master stream is untouched; at a world-covering radius with the served minimums exploration never triggers (FR-024's byte-identical action stream holds).
- **Alternatives considered**: heading as behaviour-local state (impossible: behaviours are stateless `Arc<dyn Behavior>` shared across kitties); a new `Decision` field (rejected: seam/codec change for a scripted-only need).

## R10 — Scripted targeting over visible ∪ remembered / visible ∪ heard

- **Decision**: `priced_nearest_element(ctx, kind)` scans `view.elements_of(kind)` ∪ the memory slot for `kind` (as a phantom position with `id = u32::MAX` so ties resolve to real elements); `seek_element` walks to the winner; when the remembered tile is inside the disc and empty the engine has already cleared the slot (R3), so the next decision finds neither visible nor remembered and takes the explore step — "on the same ladder that tick" holds because the memory clears in the environment phase *before* the tick on which the tile is first visible. Friend scans (`nearest_viable_playmate`, `adjacent_friend`/cuddle targets, `groom_response`) take `view.others()` ∪ `heard_unseen()` positions; on arrival (target position inside the disc) with the friend not visible, the candidate is dropped that tick.
- **Rationale**: owner ruling ii. Cheap: the memory is five slots; heard-unseen is at most four entries.

## R11 — Config surface and validation

- **Decision**: new `[vision]` table (`radius: u32`, `memory_timeout_ticks: u64`), required section; `[meow] digest_window_ticks: u64` new key beside `recent_window_ticks` (cooldown; doc rewritten); `[behavior] reply_intensity_floor: Option<f32>`; `[rl.observation] kitty_slots` default 4. `validate_vision`: r ≥ 2 (FR-edge: adjacency and the spec-012 Manhattan-2 yield rule). `validate_meow`: `digest_window_ticks` a positive integer multiple of `recent_window_ticks`. `validate_behavior`: floor in [0, 1] when set. Section-absence defaults deleted on the 13 + 4 tables (rl / plugins / watchdog stay `ForeignTable`); seven retired-key `Option` fields and rejectors deleted; `Config::default()` (the stamp source) gains the new keys with the served defaults → `[stamp]` moves once.
- **Rationale**: FR-002, FR-008, FR-017, FR-030–FR-031, FR-043; owner-ruled placements.
- **Keeping `recent_window_ticks`'s name**: the retired `[meow] cooldown_ticks` is deleted in the same change; reviving it with a new meaning would defeat the migration note, and exp-004/F-034 tooling references the existing key.

## R12 — Schema bump, tokenizer, expansion, evals

- **Decision**: `OBSERVATION_SCHEMA_VERSION` 4 → 5; `schema_four_pins.rs` becomes `schema_five_pins.rs` asserting 404 / 39 / 20 / 55 / v5 / kitty_slots 4 literally (the 033 pattern). `attn.rs::token_layout` drops the message-kind group (type rows 22 → 7: self, kitty, chow, water, sunbeam, critter, clock); widths derive. The v3 artifact *format* is unchanged (header-authoritative; blob length derives from widths), so no artifact-version bump. `expand.rs` keeps its source generation pinned at obs 3 and refuses obs-5 targets by the existing pin compare. `evals/v2` = the six v1 designs written complete against 3.0 with a new manifest; `evals/v1` joins the exclusions; both sweeps' "frozen exams are in the sweep" assertion retargets to `evals/v2`; `kitty-eval --suite` default follows.
- **Rationale**: FR-025–FR-028, FR-033; ROADMAP principle 5 (codec frozen); spec 035's tool proves placement for one source generation only.

## R13 — Goldens, stamp, and the byte-identity proof

- **Decision**: the three golden-family pins regenerate once from one run at the end of the arc with the justification in each file's doctrine comment (fog at r = 5 is an intentional dynamics move). The defaults-stamp test moves by exactly the new keys — proven by diffing the serialised defaults before/after (recorded in the redden list). FR-024/SC-004 get a dedicated 20k-tick seeded diff: served roster all-scripted, `[vision] radius` = world-covering, reply floor unset, `announce_here` 0, actions compared tick by tick against the pre-fog engine's stream captured at the branch base; messages compared with the want-law exemption only.
- **Rationale**: house practice (spec 048's golden regeneration note; the four-pin lesson from cycle A of its redden list).

## R14 — Migration of 65 configs

- **Decision**: a one-off script (`experiments/tools/complete_config_3.py`, Python, stdlib `tomllib` + a minimal writer, or a `cargo run --bin` helper if TOML round-tripping proves lossy) that inserts every missing required section with the engine defaults as serialised by `Config::default()`, preserving existing keys and comments where the file is hand-maintained (served, training, clowder tiny-world get hand edits; generated families get the script). Result-backing families (exp-004 pilot/rebaseline, prereg families) go to `config-sweep-exclusions.txt` with a one-line reason each.
- **Rationale**: FR-034; the sweeps are the reddening points and must be green on the branch.
