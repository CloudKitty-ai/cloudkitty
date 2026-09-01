# Spec 044 redden list

Every assertion added by this spec, proven red via the exact bug it
catches (CLAUDE.md rules 5/6), then restored to green.

**Baseline (T001)**: `cargo test --workspace` at c3db7bc (branch merged
with origin/main d06b6d6): **737 passed, 0 failed**. Default-config
stamp (`engine_defaults_sha256`):
`6c73f89443671d5acc06a1e029c28c94856e3404396c231ee559026c98f07687`
— must be unmoved at both commits. Git status clean.

| assertion | injected bug | predicted failure | observed red | restored green |
|---|---|---|---|---|
| T003 stamp guard: `!json.contains("contagion_factor")` (default) + sibling explicit-zero test | field written before it existed; then `skip_serializing_if` removed from the field | first: compile fail E0609; then: both tests red with `"contagion_factor":0.0` visible in the stamp JSON | ✅ E0609 ×4; then both tests panicked showing the leaked key | ✅ 84/0 config tests |
| T003 `contagion_factor_zero_parses_equal_to_absent` | (covered by the same compile-fail red; the `absent` arm carries a `[water]` table without the key, so a dropped `default` attr would red here) | compile fail E0609 | ✅ E0609 | ✅ green |
| T009 `contagion_widens_the_headroom_budget_only_above_factor_one` (reject at factor 5.0 on the default world; blame the 2x cat at factor 3.0) | run before T010's widening; then post-T010, `factor.max(1.0)` replaced with `1.0` | both times: `unwrap_err` panics on Ok at the factor-5.0 arm (un-widened budget accepts 60 + 17.5 vs 75) | ✅ panicked at mod.rs:1894 pre-T010 and again under the injection — identical failure, the exact bug the assertion exists to catch | ✅ 85/0 |
| T004 bounds tests (NaN/±∞/−1 rejected, also with `bath_gain = 0`) | run before T006's bounds check existed; then bounds check moved AFTER the `gain == 0` early return | first: `unwrap_err` panics on Ok (no check); then: only the wet-fur-off arm reds | ✅ panicked at the reject arm pre-T006; post-injection panicked at mod.rs:1892 (the `bath_gain = 0` arm) exactly | ✅ 84/0 |
