# Spec 045 redden list

Every assertion added by this spec, proven red via the exact bug it
catches (CLAUDE.md rules 5/6), then restored to green.

**Baseline (T001)**: `cargo test --workspace` at the branch tip
(045-contagion-membership off main 74537e4): **750 passed, 0 failed**.
Default-config stamp (`engine_defaults_sha256`):
`6c73f89443671d5acc06a1e029c28c94856e3404396c231ee559026c98f07687`
— must be unmoved at both commits. Git status clean.

| assertion | injected bug | predicted failure | observed red | restored green |
|---|---|---|---|---|
| T004 stamp guard: `!json.contains("contagion_membership")` | `skip_serializing_if` removed from the membership field | stamp test reds with the key visible in the default JSON | ✅ panicked at mod.rs:2717, `"contagion_membership":"option_a"` visible in the stamp JSON | ✅ 88/0 config tests |
| T004 stamp guard: `!json.contains("contagion_aware_ladder")` | `skip_serializing_if` removed from the ladder field | stamp test reds with the key visible | ✅ panicked at mod.rs:2721, `contagion_aware_ladder leaked into the stamp` | ✅ 88/0 |
| T005 unknown-value rejection names both legal values + T004 explicit-`"option_a"` ≡ absent | `#[serde(rename = "optionA")]` on the OptionA variant (the TOML vocabulary drifting from the record's — the exact bug the message assertion exists to catch) | unknown-value test reds (serde's menu says `optionA`, not `option_a`); the explicit-default parse arm reds too (`"option_a"` no longer parses) | ✅ both FAILED: "error must name option_a: TOML parse error…" at mod.rs:2809; parse-equality panicked at mod.rs:2780 | ✅ 88/0; serde's native unknown-variant message names both values — no wrapper needed (research D8) |
| T004 `contagion_aware_ladder = false` ≡ absent | (red channel shared with the ladder skip-attr cycle above — the absent arm carries a `[behavior]` table without the key, so a dropped `default` attr would red at parse) | key visible / parse fail | ✅ via the shared cycle | ✅ green |

**Commit 1 gate (T006)**: full workspace suite **753 passed, 0 failed**
(baseline 750 + 3 new config tests). Stamp re-read post-surface:
`6c73f894…f07687` byte-equal to baseline. Deviation from research D3
recorded: no new `bool_is_false` helper — the ladder field reuses the
in-tree bool skip idiom `std::ops::Not::not` (the `pounce` field's,
039-D5), per CLAUDE.md rule 2 (existing helper first).

## US1 cycles (T007–T014)

| assertion | injected bug | predicted failure | observed red | restored green |
|---|---|---|---|---|
| T007 per-kind referenced-cat differential (resting/co-sleeping/grooming: bidi − option_a = exactly one charge; namer's rise membership-blind) | natural red: run before T010 (engine still option_a-only) | differential 0, expected 3.5 | ✅ "resting: referenced dry cat's differential is 0, expected exactly one charge 3.5" at waterline_contagion.rs:600 | ✅ 11/0 post-T010 |
| T008 multi-payer (two wet groomers, one dry cat, exactly ONE charge over baseline) | same natural red, pre-T010 | added 0, expected 3.5 | ✅ "two wet groomers must add exactly ONE charge (3.5)…, added 0" at :732 | ✅ 11/0 |
| T007b play reciprocity (dry member pays once under either rule — the BTreeSet one-charge cap from the double-admission side) | kept-behavior arm, green pre-AND-post T010 by design (dry member already a member by own-naming); its charge arithmetic shares 044 T014's recorded red | — | green both sides (rule 6 must-pass) | ✅ |
| T009 kept exemptions under bidirectional (non-adjacent referenced, wet member, both-dry, both-wet) | rule-6 must-pass pile: green before AND after T010 | — | verified green pre-T010 and post-T010 | ✅ |
| T011 referenced-role adjacency (unit layer, mid-tick): wet namer two tiles off charges nothing; adjacent positive control pays | `is_available_friend(w.id, k.id)` deleted from the bidirectional arm | non-adjacent arm reds with ambient+charge instead of ambient | ✅ "a referenced cat no longer adjacent to its wet namer must not charge: bath moved 3.7, ambient is 0.2" at world.rs:3291 | ✅ 1/0, restored |
| T012 budget membership-invariance (FR-008: 044's accept/reject configs identical under both membership values) | natural channel: asserts the recorded option_a outcomes hold verbatim under `bidirectional` — a divergence (someone teaching validate_water to price membership) is the exact bug | divergence panics naming the membership | green first run (invariance holds — the assertion's red channel is the divergence it forbids) | ✅ 89/0 config tests |
| T014a bidirectional same-seed determinism (500 ticks, factor 1.0) | ⚠ NO honest red — 044 T017's caveat carries verbatim: the arm draws no RNG by construction; any injected draw shifts both same-seed runs identically. Kept as the in-tree pin against future platform/order nondeterminism. Recorded per rule 6, not hidden. | — | — | ✅ green |
| T014b mask equality (FR-007 armed: charged cat's legal-action + message masks equal its uncharged option_a twin's at the same tick, with a divergence guard proving the charge landed) | fake legality hook injected into `action::validate` (Rest refused whenever membership = bidirectional) | the action-mask equality reds for kitty 1 | ✅ "kitty 1: the membership dial moved the legal-action mask (FR-007)" at mask.rs:216 | ✅ 6/0 mask tests, injection removed |


## US3 (T015–T017)

**T015**: `evolution_golden` passes unregenerated (1/0). Stamp guard
tests green in-suite; stamp re-read at commit 1 was byte-equal and no
config-surface change has landed since (re-asserted again at T028).

**T016** `explicit_default_dials_are_byte_identical_to_absent` (500-tick
seeded run, both dials explicit vs absent, through TOML): red channel
shares the recorded T004/T005 skip-attr and rename cycles — the run
halves compare provably-equal configs (044 T017 precedent, recorded not
hidden).

**T017**: full workspace suite **762 passed, 0 failed** (753 + 9 new:
T007 ×1, play reciprocity, T008, T009, T011, T012, T014a, T014b, T016).
`git status`: zero edits to any TOML — served config untouched.

## US2 cycles (T018–T025)

| assertion | injected bug | predicted failure | observed red | restored green |
|---|---|---|---|---|
| T018 exposure helper unit arms (payer sets per membership, ceiling cap, E_ticks = bounds.min per kind incl. grooming→durations.bath, payer's own bath_ratio, gate short-circuits) | natural red: tests written before the helper existed | compile fail E0425 | ✅ E0425 ×5 (`cannot find function expected_scene_exposure`) — 044 T003 precedent, compile fail counts | ✅ 5/5 post-T019 |
| T020 scored() seam (exposed cuddle scores exactly one scene-exposure below its dry twin; gate off ⇒ identical AND equal to the hand-computed pre-045 formula) | natural red: test written before the seam | dry − wet = 0, expected 10.5 | ✅ "exposed cuddle must score exactly one scene-exposure below its twin: dry 39, wet 39" | ✅ 117/0 behavior tests |
| T021 play_score() seam (dry playmate outranks equal wet twin at factor 1.0; classic tie-break stands at factor 0.0 with gate on) | natural red: seam absent | wet id 2 wins both arms | ✅ "armed: the dry twin must outrank the wet one — left: Kitty 2, right: Kitty 3" | ✅ 118/0 |
| T022 groom seam (wet groomer declines iff exposure > groomee bath + groom_cuddle_relief; net-positive groom proposed; option_a prices zero) + groom-path enumeration recorded in the test doc | natural red 1: seam absent — cranked-factor groom still proposed. Bonus red 2 (staging bug caught by the CEILING CAP): first staging used groomee bath 95 > ceiling 60 ⇒ headroom 0 ⇒ exposure 0 ⇒ never declines — exactly the never-price-what-cannot-be-collected law working; restaged at bath 10 | assert_ne fails: Groom{2} == Groom{2} | ✅ observed twice (pre-seam and at the over-ceiling staging) | ✅ 119/0 |
| T023 gate-on + factor 0.0 ≡ gate off (500-tick seeded run) | `factor.max(1.0)` injected into the helper's rate (the borrowed validate_water idiom — prices at factor 0) | ⚠ the 500-tick equality STAYED GREEN under the injection on this seed (test_config world never flips a choice) — vacuous alone, recorded per rule 6, kept as the seeded integration pin. The honest guard: `exposure_is_zero_before_any_arithmetic_when_gated_off`'s factor-0 arm | ✅ the unit arm panicked "left: 10.5, right: 0.0" under the same injection | ✅ restored, behavior 119/0 |
| T025a armed-ladder determinism (500 ticks × both memberships) | ⚠ NO honest red — the 044 T017 caveat, third occurrence; recorded not hidden | — | — | ✅ green |
| T025b ladder-gate mask equality (FR-007 armed case, Article IV: gate on vs off, exposed scene, both masks both cats) | fake legality hook in `action::validate` (Rest refused whenever the ladder gate is on) | action-mask equality reds for kitty 1 | ✅ "kitty 1: the ladder gate moved the legal-action mask (FR-007 armed case)" at mask.rs:281 | ✅ 7/0 mask tests, injection removed |

**Boot log (T013/T024, quickstart §6)**: armed contagion line names the
membership in both states; ladder line present ONLY with the gate on;
default boot log carries neither (verified live against lab TOMLs).

**Post-US2 suite**: **773 passed, 0 failed** (762 + 11 new).

## Final gate (T028)

`cargo clippy --workspace` 0 warnings; `cargo fmt --check` clean.
Full workspace suite **773 passed, 0 failed** — baseline 750 + 3
(Phase 2) + 9 (US1/US3) + 11 (US2), arithmetic exact. Stamp re-read at
commit 2: `6c73f894…f07687` byte-equal to baseline; `evolution_golden`
passes unregenerated. Served TOMLs untouched. Every Phase 3/5 assertion
above carries a recorded cycle; the three no-honest-red caveats
(T014a, T023 seeded arm, T025a) are recorded, not hidden.

## Post-review follow-up cycles (Experiments-ruled 2026-09-01)

| assertion | injected bug / red channel | predicted failure | observed red | restored green |
|---|---|---|---|---|
| Ruling 1: reciprocal play pays under option_a from either role (+ play prices identically under both memberships) | natural red: arm written before the `reciprocal` branch | exposure 0, expected 7 | ✅ "reciprocal play: the dry partner is a namer under option_a and its charge is the scene's cost: 0" | ✅ 119/0 |
| Ruling 4: engine-faithful step-with-overshoot cap (headroom + one charge below the ceiling; 0 at/past it; mid-range untouched) | natural red: test rewritten against the old headroom clamp | got 2, expected 5.5 | ✅ "near the ceiling the engine still collects the overshoot charge: expected 5.5, got 2" | ✅ 119/0 |
| Ruling 3 (seam 4): sleepy cat declines a wet cosleep companion iff exposure > own cuddle + companion's tier relief; net-positive still named; gate off inert | natural red: test written before the seam | Sleep{Some(2)} at cranked factor, expected Sleep{None} | ✅ assert_eq failed: left Sleep{Some(2)}, right Sleep{None} | ✅ 120/0 |
| Ruling 6: the groom decline bar TRACKS the configured `groom_cuddle_relief` (dial-sensitivity arm; smoke pins its own 0.5) | natural channel: same scene flips net-positive at relief 130 — a bar hardcoding the default would stay declined | decline persists under the generous dial | green first run (bar reads config, as ruled) | ✅ |
| T023 REWORKED (rule 6: the seeded 500-tick arm was vacuous): controlled needs-driven world with a ~5-point cuddle-vs-eat gap inside one exposure; arm 1 = divergence control (gate on ≠ off at factor 2), arm 2 = gate-on factor-0 ≡ gate-off | the borrowed `max(1, factor)` idiom re-injected into the helper | arm 2 reds (a factor-0 exposure of 10.5 flips the choice) | ✅ "an armed ladder with no charge to price must change nothing" FAILED under the injection — the sensitivity the old arm lacked | ✅ restored, 15/15 |
| Ladder mask test de-vacuitized: ONE snapshot, gate-on vs gate-off CONFIGS (masks are pure fns of (snapshot, config) — the bool is the only varying input) | red channel: the recorded fake-legality-hook injection (gate-read in validate) reds it directly | — | (carried from the recorded T025b cycle) | ✅ 7/0 mask tests |
| Shared `Config::contagion_charge` (engine arm + ladder read ONE formula) | pure refactor — 15/15 contagion integration green unchanged proves byte-identity of the engine arm | — | — | ✅ |
| T012 disclosure note (review below-cut): `membership_never_moves_the_budget` was never seen red — its channel is the divergence it forbids (recorded in its US1 row; restated here so the caveat list is complete: FOUR no-honest-red arms total — T012, T014a, T025a, and the retired seeded T023 arm now replaced by a sensitive one) | — | — | — | — |

Boot log re-verified live after the message fix (rule text now in the
MESSAGE, not only the field): armed option_a / armed bidirectional /
default all correct; ladder line only when the gate is on.
