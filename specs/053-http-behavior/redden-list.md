# 053 redden list — rule-5/rule-6 ledger + review record

## T032 fresh-eyes review (2026-09-14, adversarial agent on the full diff)

Eight findings, all triaged; resolutions in the review-fixes commit and
research.md §Review amendments:

1. **HIGH, verified — seat-class span entirely unguarded** (three
   surviving mutants: drop `.instrument`, swap `as_str` arms, discard
   the class at registration). FIXED: dedicated capture test
   `tests/seat_class_log.rs` (own binary — tracing's process-global
   callsite cache races parallel scoped subscribers; first draft in the
   shared binary flaked exactly that way) pins registration + exchange
   lines carrying the DECLARED value, both classes. Post-commit mutate
   cycles below. ACCEPTED sub-gap, documented in plugins.md: core
   dispatch's bench warning fires below the wrapper and carries no
   class.
2. **MED-HIGH, verified — shared-entry semantics had zero coverage**
   (every test was single-kitty; only the breaker test used the
   budgeted path). FIXED: `one_shared_entry_advises_two_kitties` (50
   ticks, per-kitty attribution, one exchange per kitty per tick) and
   `a_shared_entry_cools_down_for_both_kitties` (shared Dead state:
   sibling doesn't exchange against a tainted channel; shared
   recovery). Budgeted-path mutex contention under abandoned threads
   remains exercised only by the breaker test — accepted, inherited
   script-transport shape.
3. **MED, verified — io-thread-spawn-failure path killed the child but
   not its group.** FIXED: same killpg lines as Drop.
4. **MED, verified — process_group(0) detached plugins from SIGTERM**
   (only SIGINT triggered graceful shutdown; supervisors orphan plugin
   groups). FIXED: main.rs handles SIGTERM alongside SIGINT (unix).
5. **MED, verified — TooLarge/Desynced teardown charged a 20-tick
   cooldown for a provably-clean channel** (reply consumed, connection
   dropped; the script rationale doesn't transfer — no stream exists).
   FIXED: no taint for either; only TimedOut/ChannelGone tear down.
   Contract, data-model, docs tables amended; tests rewritten to the
   no-cooldown contract (the old cooldown assertions are the rule-6
   red: they fail against the new code by construction).
6. **LOW-MED, plausible — reqwest's equal timeout racing the engine
   deadline** (a miss classified Transport/no-taint instead of
   TimedOut). FIXED: client timer = 2× deadline; engine always wins.
7. **LOW, verified — client-build failure left Running over a dead
   thread** (one wasted mis-classified decision). FIXED: io_loop logs
   and drops the channel without sending → first exchange reads
   ChannelGone → immediate cooldown.
8. **LOW, verified — example-brain test leaked python3 on panic.**
   FIXED: KillOnDrop guard. (The grandchild pid-reuse note is a
   false-RED direction — accepted.)

Reviewer confirmed sound: killpg-before-reap ordering, non-200 body
handling, redirect-guard non-vacuity, seed-draw ordering, SC-005
structure (`Config.plugins` never serializes, so a remote endpoint
can't learn a sibling's URL), docs-locator mutant behavior. Doc nit
(demo comment "rest" vs idle) fixed.


Every mutate cycle: prediction first, observed outcome after. All via
`scripts/mutate.sh --expect` unless a stated reason says hand-rolled.

## Phase 2 — shared parser extraction (T006)

- **Cycle 1** (`exchange.rs`: correlation check inverted,
  `tick != expect` → `tick == expect`). Prediction: plugin_e2e's
  well-behaved attribution test red at "the plugin's decision is
  attributed to it" (valid replies now classed Desynced → fallback).
  Observed: RED CONFIRMED, exactly that assertion, tick 1; restore ==
  baseline (7 passed).
- **Cycle 2** (`exchange.rs`: `deny_unknown_fields` removed). Prediction:
  red at "an extra envelope field is a bad envelope". Observed: RED
  CONFIRMED; restore == baseline (4 passed). NOTE: this guard did not
  exist before this arc — docs promised the strictness but nothing
  reddened on it (pre-existing gap, rule 3/5: guard added with the moved
  code in the T006-prep commit, 013b16e-adjacent).

## Phase 3/4 — US1+US2 (T014, T019)

- **T014a: DROPPED, vacuous by design (stated reason).** The planned
  mutant (seed draw moved behind the liveness check) is engine-
  unobservable: dispatch RESEEDS the DecisionRng from the dealt seed
  before running the fallback (`rng.rs::reseed`, spec 014 review — "a
  failed advisor's partial draws must never shift the fallback's
  stream"), so the draw's placement cannot move any world byte. The
  constraint the plan carried from script.rs is enforced upstream by
  reseed, which spec 014's own tests guard. The unconditional build is
  kept for shape parity with script.rs.
- **T014b** (lib.rs: missing-class check defaulted to Scripted).
  Prediction: `a_url_entry_without_a_class_is_a_startup_error` red at
  unwrap_err. Observed: RED CONFIRMED.
- **T014c** (lib.rs: url entries registered as ScriptBehavior). FIRST
  RUN VACUOUS — the e2e suite hand-built HttpBehavior, so the
  registration path's transport selection had no guard. Guard added
  (`a_url_entry_registered_from_config_drives_a_kitty`), committed,
  cycle re-run. Prediction: red at "attributed through the
  config-registered transport". Observed: RED CONFIRMED.
- **T014d** (http_behavior.rs: SeatClassed forwards only `decide`).
  Prediction: full-day test red at attribution (decide → unreachable →
  crashed-advisor fallback). Observed: RED CONFIRMED.
- **T019a** (`if taint {` → `if false {`: nothing tears down).
  Prediction: oversized/late-reply/wrong-echo reds ("does not exchange
  during cooldown" / "never surfaces"). Observed: RED CONFIRMED.
- **T019b** (body-cap check neutered). Prediction: oversized red at
  cooldown assertion. Observed: RED CONFIRMED.
- **T019c** (accept wrong statuses). FIRST RUN VACUOUS — the 200-only
  rule is two-layer (io thread reads no non-200 body; exchange refuses
  the status), each layer masking the other's single mutant. New guard
  `a_valid_envelope_on_a_wrong_status_is_still_refused` + the honest
  mutant disables BOTH layers. Prediction: red at "wrong status is
  still refused". Observed: RED CONFIRMED.
- **T019d** (redirect Policy::none removed). Prediction: red at "the
  redirect target is never contacted" (socket-level connection counter
  — added because the parser-level hits counter would have been blind
  to reqwest's bodyless redirected GET). Observed: RED CONFIRMED.

## Rule-6 sort — the one existing-behavior change (T024)

Sorted before running, the kill path change (`process_group(0)` +
`killpg`):

- **must-go-red** (against today's single `child.kill()`): the new
  `the_kill_ends_the_whole_process_group` — sh backgrounds a sleeping
  grandchild, echoes its pid, blocks; after `drop(child)` the grandchild
  must be ESRCH within 5s. Prediction: red at "the grandchild survives
  the kill" (a clean assertion failure, not a hang — the poll is
  bounded), because kill() signals only the direct child.
- **must-stay-green** (re-read, not just re-run): script.rs unit tests
  (`a_decision_request_serializes_with_the_documented_shape` — no spawn;
  `a_reply_cut_off_mid_line_is_an_io_death...` — sh exits by itself,
  group kill moot; `a_silent_wedge_is_cut_off_by_the_exchange_deadline`
  — asserts drop is PROMPT: killpg is synchronous signal delivery, no
  new blocking); the whole plugin_e2e suite (python children, no
  grandchildren holding stdout; relaunch cycles unaffected — the group
  dies where the child alone died before); docs_examples (no processes).
  Read: none of them observes a grandchild, so the only behavior that
  moves is the one the red test pins.

- **T025 red observed as predicted**: "the grandchild survives the
  kill: the process group was not ended", clean assertion failure at
  the 5s bound (5.05s run). Wrinkle recorded: with a 600s grandchild
  the cargo harness ALSO hung waiting on the inherited stderr pipe —
  the stranding bug in miniature; the fixture's sleep was shortened to
  30s so the un-fixed red stays a bounded clean failure.
- **T026 green**: script suite 8/8 (group-kill test now 0.63s — the
  group dies, pipes close) + plugin_e2e 7/7 (must-stay-green pile).
- **T026 mutate re-proof** (killpg line removed, post-commit).
  Prediction: red at "the grandchild survives the kill". Observed: RED
  CONFIRMED, restore == baseline.

## Phase 5 — docs (T023)

- **T023** (docs/plugins.md: documented `url` key renamed `uri`).
  First run red for the WRONG REASON — the test's block locator keyed
  on `url = ` and failed before the parse assertion; locator re-keyed
  on the stable plugin name, committed, re-run. Prediction: red at
  "the documented declaration parses" (deny_unknown_fields refuses
  `uri`). Observed: RED CONFIRMED.
