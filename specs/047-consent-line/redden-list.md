# Redden list: spec 047 consent_line

Every guard shown red first (CLAUDE.md rules 5/6). Format per cycle:
prediction → observed red → revert/implement → green. Suite counts READ
after every run.

## Baseline (T002)

- Branch tip at baseline: 26c9c23 (spec artifacts only).
- `cargo test --workspace`: **793 passed / 0 failed** (64 suites) — the
  post-046 main count, as expected.
- Evolution golden + defaults stamp: green (inside the 793).

| # | Guard | Injected bug / staged state | Predicted red | Observed | Green after |
|---|-------|-----------------------------|---------------|----------|-------------|
| 1 | T005 tie pins (predicate) | both `>` mutated to `>=` in `consent_blocks` | exactly the two tie pins (at-the-line, play-ties-top); blocked + default pins stay green | as predicted: 2 failed, 2 passed | mutation reverted, 4/4 green |
| 2 | T006 ranking guards (site 1) | pre-implementation red: guards written before site 1 wired | the two BLOCKED assertions red (drops-over-line, score-on blocked half); under-line + play-on-top green | as predicted: drops test + score-on test failed, kept cases passed | site 1 wired (T007), lib 448/0 |
| 3 | T008 critter guard | gate misapplied to the critter arm (`.filter(consent_line <= 0.0)` on critters) | ONLY this guard red — every pre-existing critter test runs at line 0.0 and stays green | as predicted: 1 failed, 448 passed | mutation reverted, lib 449/0 |
| 4 | T009 get-serious guard (site 2) | pre-implementation red: guard written before `choose_consenting` existed | red with the cat chasing the burdened friend | as predicted: `left: Chase(Kitty{2})` vs `right: play_solo` | site 2 wired (T010), lib 450/0 |
| 5 | T011 opportunism guard (site 3) | pre-implementation red: guard written before the consenting `take_what_is_here` existed | red with the friend batted into a game | as predicted: `left: Play{Some(Kitty{2})}` vs `right: play_solo` | site 3 wired (T012), lib 451/0 |
| 6a | T013 audit: site 1 removed | ranking filter dropped from `scored_playmate` | **predicted 2 red** (ranking-drops, score-on) | **3 red — prediction MISSED by one**: T011's opportunism guard also red, legitimately — it asserts the WHOLE decision, and with opportunism declining, the fallback traverses the (now ungated) ranking. Defense in depth, not vacuity; the two site-1-specific guards red as required | filter restored, lib 451/0 |
| 6b | T013 audit: site 2 removed | `playful.rs` pointed back at classic `choose` | ONLY the get-serious guard red | as predicted: exactly 1 failed (450 passed) | restored |
| 6c | T013 audit: site 3 removed | `playful.rs` pointed back at classic `take_what_is_here` | ONLY the opportunism guard red (opportunism fires before the gated ranking is reached) | as predicted: exactly 1 failed (450 passed) | restored, lib 451/0 |
| 7 | T014 identity witnesses | `Default` temporarily 30.0 | defaults-stamp assertion + evolution golden BOTH red (Biscuit is playful in the default config, so the gate runs in the golden world) | as predicted, plus the 046 strip witness red too (the world itself diverged — consistent) | reverted to 0.0; stamp + golden green, pins UNMOVED |
| 8 | T015 doctrine guard | classic `take_what_is_here` entry temporarily passed `consent: true` | ONLY the needs_driven doctrine guard red | as predicted: exactly 1 failed (451 passed) | reverted, lib 452/0 |
| 9 | T016 validation row | poison-table row added BEFORE the validate.rs entry | red: NaN/inf/−1 in `consent_line` accepted (nothing rejects) | as predicted: poison test failed at the expect_err | validate.rs entry added, lib 452/0 |

## Final gate (T020/T021)

- `cargo fmt --all --check`: clean. `cargo clippy --workspace --all-targets -- -D warnings`: clean.
- Suite trajectory: **793/0 (baseline) → 805/0** (64 suites) — 12 new
  tests: 4 predicate pins, 3 ranking trio, 1 score-on, 1 critter, 1
  get-serious, 1 opportunism, 1 needs_driven doctrine; the stamp guard and
  the 042 poison table were EXTENDED in place (no new test fn).
- Quickstart §§1–4 walked as written; two stale test filters in §1/§2
  fixed to the real target/test names during the walk.
- Golden pin + defaults stamp: UNMOVED on the finished branch (cycle 7
  proved both CAN red).
