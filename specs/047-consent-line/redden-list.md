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
