# Tasks: Randomized Starts

**Input**: Design documents from `specs/062-randomized-starts/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included — the spec is test-guarded throughout (SC-001..006), and house
rule 5 requires every guard red-first via `scripts/mutate.sh --expect <prediction>`
with the prediction declared BEFORE the run. Rule-5 tasks are listed explicitly;
no guard counts as done until its red cycle passed for the right reason.

**Organization**: Grouped by user story. US1 = the draw law (P1), US2 = baseline
attribution (P2), US3 = provenance (P3, cross-lane into Experiments' bc-collect).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: parallelizable (different files, no dependency on an incomplete task)
- All paths relative to the worktree root `~/ai/cloudkitty-randomized-starts`

---

## Phase 1: Setup

**Purpose**: bring the branch current and make the tree mutate.sh-clean.

- [ ] T001 Merge `origin/main` into `product/randomized-starts` (fetch first; merge, NEVER rebase — main has moved past 0c40d8bb through #453, #452, and 84a74a75), then `cargo test --workspace` to confirm a green baseline
- [ ] T002 Commit the 062 design artifacts `specs/062-randomized-starts/` (spec, plan, research, data-model, quickstart, contracts/, this file) — mutate.sh compares files against HEAD, so implementation files must land on top of a committed tree

**Checkpoint**: branch current, baseline green, tree clean.

---

## Phase 2: Foundational (blocking all stories)

**Purpose**: the config surface and the starts module's types — every story
parses `[starts]` and speaks `DrawnStart`.

- [ ] T003 Add `StartsConfig` (`edge_ring_share: f64`, `corner_share: f64`, `deny_unknown_fields`) and `Config.starts: Option<StartsConfig>` with `#[serde(default, skip_serializing_if = "Option::is_none")]` in `crates/cloudkitty-core/src/config/mod.rs` per data-model.md
- [ ] T004 Change `KittyConfig.x/y` to `Option<u32>` (`default`, `skip_serializing_if`) in `crates/cloudkitty-core/src/config/mod.rs`; `KittyConfig::new` keeps `u32` params and wraps `Some` (research R2 — no call-site sweep); fix any direct-field construction sites the compiler names
- [ ] T005 Append `validate_starts()` as position 19 in `Config::validate()` in `crates/cloudkitty-core/src/config/mod.rs`: share bounds [0,1], `corner_share ≤ edge_ring_share`, table-present ⇒ both dimensions ≥ 3 — error wording per contracts/config-surface.md §3 (spec-020 order contract: append, never reorder)
- [ ] T006 Add roster-slot (position 2) checks in `crates/cloudkitty-core/src/config/mod.rs`: exactly one of x/y set → error naming the kitty (always); knob off + missing coords → error naming the kitty and that `[starts]` is absent (fires only on newly-parseable input, so no existing config's first-failing message changes)
- [ ] T007 [P] Create `crates/cloudkitty-core/src/starts.rs` skeleton + `pub mod starts` in `crates/cloudkitty-core/src/lib.rs`: `StartCategory` (Corner|EdgeRing|Interior, serde `"corner"|"edge_ring"|"interior"`), `DrawnStart {kitty, position, category, drawn}`, `StartsError` (Display names category, drawn count, capacity), `pub const STARTS_LAW_VERSION: u32 = 1`
- [ ] T008 Config-surface guard tests in `crates/cloudkitty-core/src/config/mod.rs` (or its test module): `[starts]` parses; each §3 validation row rejects with the named field; unknown key rejected; mixed explicit+drawn config legal; knob-off missing-x/y rejected naming the kitty. Rule-5 red each guard via `scripts/mutate.sh --expect <prediction>` (prediction declared first)
- [ ] T009 Knob-off serialization invariance check: run the existing defaults-stamp test (`engine_defaults_sha256`, `crates/cloudkitty-rl/.../suite.rs`) and the full config suite — both must pass UNTOUCHED (SC-004's serialization half; if the stamp moves, the Option/skip wiring is wrong — fix the wiring, never re-cut the stamp)

**Checkpoint**: knob parses and validates; knob-off world byte-identical in
config space; `starts` types compile. Stories can begin.

---

## Phase 3: User Story 1 — A world draws its own starts, lawfully (P1) 🎯 MVP

**Goal**: the versioned draw law in the engine's one build site.

**Independent Test**: many-seed sweep from one share-enabled config — every
start in-bounds, unique, lawfully categorized by an independent classifier,
realized shares within binomial tolerance; any seed rebuilt = identical
positions (quickstart §2).

- [ ] T010 [US1] Implement `starts::draw(config) -> Result<Vec<DrawnStart>, StartsError>` in `crates/cloudkitty-core/src/starts.rs` exactly per contracts/draw-law-v1.md: 32-byte sub-stream seed (seed LE ∥ `ck-starts-v1` ∥ zeros) into `ChaCha8Rng::from_seed`; per drawn kitty (id ascending) v1→category via `(v1>>11)×2⁻⁵³` against the shares, v2→`free[v2 mod len]` over the canonical row-major free list; explicit kitties consume zero draws, tiles pre-marked occupied; exhaustion = `StartsError`
- [ ] T011 [US1] Add `World::try_generate(&Config) -> Result<World, StartsError>` in `crates/cloudkitty-core/src/world.rs`; `World::generate` delegates + `expect`s (signature frozen, 68 call sites untouched); knob on resolves positions via `starts::draw`, knob off takes today's explicit path unchanged
- [ ] T012 [P] [US1] Determinism tests in `crates/cloudkitty-core/src/starts.rs` tests: same (config, seed) drawn twice → identical positions; `[[kitty]]` file-order reorder → identical positions per id (acceptance 1 & 3)
- [ ] T013 [P] [US1] Sweep test (SC-001/SC-002) in `crates/cloudkitty-core/src/starts.rs` tests: many seeds, every start in-bounds + unique; category verified by an IN-TEST independent classifier (coverage_read.py's geometry re-stated, not calling the draw's own classifier); realized shares within binomial tolerance
- [ ] T014 [P] [US1] Exhaustion test: roster larger than a category's capacity (e.g. corner_share 1.0, 5 kitties) → error naming the category, the drawn count, and the capacity — never spilling into another category
- [ ] T015 [P] [US1] Mixed-config test: explicit kitty's tile never drawn (occupied); adding/removing an explicit kitty does NOT shift any drawn kitty's position (zero draws consumed — draw-law §4 property)
- [ ] T016 [US1] Golden vectors (SC-005 enabler): an engine test emits `specs/062-randomized-starts/contracts/golden-draws.json` (recorded real payloads — seed, dims, shares, roster → raw u64 sequence + final kitty/x/y/category list) and a sibling assertion pins the committed file byte-stable; commit the emitted file
- [ ] T017 [US1] Rule-5 red cycles for every US1 guard via `scripts/mutate.sh --expect <prediction>`, one mutation per guard at the cheapest layer (e.g. flip category comparison, skip occupied-marking, swap v1/v2, perturb seed layout byte), each prediction declared before its run; rule 6: sort the pile — must-fail list red, must-pass pile read and green

**Checkpoint**: the law exists, is pinned by goldens, and every guard has seen
its red. MVP complete.

---

## Phase 4: User Story 2 — The baseline stays attributable (P2)

**Goal**: stream isolation proven, knob-off surface untouched.

**Independent Test**: knob-on vs knob-off-with-explicit-starts-equal, same
seed, full horizon → byte-identical; whole existing suite green untouched
(quickstart §§1, 3).

- [ ] T018 [US2] SC-003 integration test `crates/cloudkitty-core/tests/starts_baseline_identity.rs`: build knob-on world on seed S, read drawn starts, build knob-off config with those starts explicit, run BOTH a full horizon; assert snapshots byte-equal every tick, element history included
- [ ] T019 [US2] Rule-5 red for SC-003 via `scripts/mutate.sh --expect`: mutation makes `draw` consume one u64 from the MASTER world stream; predict failure at first element divergence (the baseline-attribution trap made flesh — this red is the feature's load-bearing proof)
- [ ] T020 [US2] SC-004 full gate in the worktree: `cargo test --workspace`, `cargo clippy --all-targets -- -D warnings`, `cargo test -p cloudkitty-rl --test shipped_configs_rl` — all green with `git status` showing ONLY this feature's files (zero golden/pin/shipped-config re-cuts)

**Checkpoint**: divergence attribution guaranteed; existing surface untouched.

---

## Phase 5: User Story 3 — A trace ties to its draw law (P3, cross-lane)

**Goal**: bc-collect meta.json carries engine identity + per-kitty draw echo.
Cross-lane into `experiments/tools/bc-collect` — the PR body carries a literal
`cross-lane:` reason citing `experiments/gen2-randomized-starts-requirements-2026-10-15.md`
(their note asks for exactly this).

**Independent Test**: one collection run → meta.json has `engine_commit` (real
SHA), `starts_law_version == 1`, `starts` echo matching tick-0 readback
(quickstart §5).

- [ ] T021 [P] [US3] Add `experiments/tools/bc-collect/build.rs`: embed workspace git SHA as `cargo:rustc-env`, `-dirty` from an engine-scoped `git status --porcelain` probe, `"unknown"` without git, probe failure fails TOWARD `-dirty`, rerun-if-changed on sources + `{git-dir}/HEAD` + common-dir `refs/heads`/`packed-refs` — mirror the merged `crates/cloudkitty-py/build.rs` (#452, final form 66a8eb6d) with paths adjusted for bc-collect's manifest dir
- [ ] T022 [US3] Extend meta.json in `experiments/tools/bc-collect/src/main.rs`: `engine_commit` + `starts_law_version` on EVERY run; `starts` echo array (kitty-id ascending, `{kitty, x, y, category, drawn}`) when the knob is on, from the SAME `starts::draw` call — field names and absence-when-off per contracts/provenance.md (additive-only; no existing key moves)
- [ ] T023 [US3] SC-006 test (engine-side, in `crates/cloudkitty-core` tests or bc-collect's): the echo equals tick-0 world-state readback exactly, and each echoed category equals an independent geometric classification of the position
- [ ] T024 [US3] Rule-5 reds for US3 guards via `scripts/mutate.sh --expect`: e.g. echo built from a second draw call with a perturbed tag (prediction: echo ≠ tick-0), law-version stamp zeroed (prediction: `starts_law_version` assert fails), each declared first

**Checkpoint**: a corpus is auditable back to its law.

---

## Phase 6: Polish & PR

- [ ] T025 Run quickstart.md §§1–5 end to end in the worktree and record each outcome (the quickstart is the feature's validation guide; a failing section reopens its task)
- [ ] T026 Self-check the frozen surfaces one last time: `World::generate` signature, `Config::fingerprint()`, validate() positions 1–18, `engine_defaults_sha256` — all byte-untouched; confirm no new root `.toml` appeared (toolchain-pin trap)
- [ ] T027 Push `product/randomized-starts`, read `gh pr view --json files` against expectation, open the PR with the `cross-lane:` reason (T021/T022 paths), self-review comment, Monitor CI then verify `gh pr checks` directly — merge only on her word

---

## Dependencies & Execution Order

- **Phase 1 → 2 → 3 → 4 → 5 → 6** is the safe serial order.
- Phase 2 blocks all stories (every story parses the knob and uses the types).
- US1 (Phase 3) blocks US2's T018 (it compares against the draw) and US3's
  T022/T023 (the echo calls `starts::draw`). T021 (build.rs) is independent of
  US1 and may run any time after Phase 1.
- Within phases, [P] tasks touch different files/tests and may run together;
  mutate.sh cycles (T008, T017, T019, T024) are serial — never two cycles or
  tree edits while one runs (house rule).

### Parallel opportunities

- Phase 2: T007 alongside T003–T006 (different files).
- Phase 3: T012, T013, T014, T015 together once T010–T011 land.
- Phase 5: T021 alongside anything (new file, no deps beyond Phase 1).

---

## Implementation Strategy

**MVP = Phases 1–3** (US1): the ruled mechanism itself, pinned by goldens and
reds. US2 (Phase 4) is the attribution proof and the gate everything rides on
— in practice it ships in the same PR, since SC-003's red (T019) is the
feature's central verification. US3 (Phase 5) is separable in principle but
the requirements note asks for it and the cross-lane reason is already
written; one PR carrying all three stories is the expected shape, with
checkpoints validated in order.

## Notes

- Spec-first house rule satisfied: spec → plan → tasks, all committed before
  implementation (T002).
- Doctrine check (rule 8) lives in spec.md §Design-doctrine check — done
  pre-plan; nothing re-opens here.
- Served configs never gain `[starts]` in this feature (spec doctrine rule 8
  note); turning it on served is a separate deploy ruling.
