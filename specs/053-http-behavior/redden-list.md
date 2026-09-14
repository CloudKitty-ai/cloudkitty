# 053 redden list — rule-5/rule-6 ledger

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

- (T025 red observed): see below after the run.
