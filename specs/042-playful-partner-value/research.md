# Phase 0 Research: Playful 2.0 — partner-value play selection

No NEEDS CLARIFICATION markers survive the clarify session (three
rulings + the staleness question, all in spec.md §Clarifications).
Sources: the design note (`experiments/biscuit3-design-note-2026-08-26.md`
@ e489d4b, levers 1–2), F-033, the two banked measurement docs, and
in-session verification of every cited code surface (2026-08-29, on
this branch's base e489d4b).

## D1 — SUPERSEDED 2026-08-30 (review #1): a separate scored pick, playful-only

The original D1 rewired `nearest_viable_playmate` in place — but that
function is shared: `choose`'s play arm (:47), `score` (:82),
`travel_distance` (:107), and `play_action` (:335) all consume it,
and NeedsDriven's play scoring rides `choose`. Rewiring it leaked the
gate and score into non-playful cats (a sweep confounder byte-identity
testing structurally cannot catch, since the dials are inert at
defaults). Now: the classic pick is restored dial-blind for every
shared path, and the playful behavior's play step calls its own
`scored_playmate` via `scored_play_action`. This also preserves the
`play_action_with`/`play_travel_distance` mirror (review #6): busy
targets never reach the shared paths, so the one new
`play_action_with` branch is unreachable from them.

## D1-original — Rework the body of `nearest_viable_playmate`, keep its shape

**Decision**: the scored ranking replaces the internals of
`selection::nearest_viable_playmate` (`behavior/selection.rs:247`),
keeping the `(ctx) -> Option<(TargetRef, Position)>` signature so all
three call sites (`choose`'s play arm :47, `play_travel_distance`
:223→:107, `play_action` :335) inherit the new pick unchanged.

**Rationale**: one selection surface, no parallel pick; the callers
already treat the result as "the playmate worth having".

**Alternatives**: a new fn beside the old (rejected — two sources of
truth for the same question); moving selection into `playful.rs`
(rejected — the shared `selection` module is the house home for
target choice, and needs_driven's play path uses the same fns).

## D2 — Candidate admission: busy friends enter only when `w_value > 0` (now spec FR-012)

**2026-08-30 amendments**: promoted to spec FR-012 (review #8 — it was
plan-only). Known dial-space hazard, documented not coded (review #3):
at `w_value > 0` with `w_busy = 0`, waiting is free — an adjacent
mid-scene friend can win every re-scan and absorb the game in
solo-play-beside for its whole scene while a free friend nearby goes
unchased. `w_busy` is the counterweight and the sweep prices it; the
toml/contract guidance says to raise them together. `t_partner`'s
identity is NO BAR (review #2): the eligibility test applies only when
the threshold is raised above zero, so negative values under live
`w_serious`/`w_busy` stay ranking costs, never vetoes.

**Decision**: free friends and critters are always candidates
(exactly today's set); a mid-scene friend is admitted to the ranking
iff `w_value > 0.0`. Admitted busy friends still pass the eligibility
filter (D3) like anyone.

**Rationale**: byte-identity at defaults is otherwise impossible — at
all-zero dials a busy adjacent friend would enter as "nearest body"
(score −distance) and displace today's pick, and `play_action_with`
would sit beside it in solo play where today the cat chases the next
free target. With the value term dead there is no anticipatory signal
to act on, so keying admission on `w_value` turns the feature on
exactly when its input exists.

**Alternatives**: always admit busy friends (rejected — breaks
SC-001); a dedicated admission flag dial (rejected — a 13th dial that
can contradict `w_value`; nothing speculative).

## D3 — Eligibility filter (clarify ruling 1)

**Decision**: friends are filtered before ranking: all friends are
ineligible when own `play_need < t_self`; a friend is ineligible when
its value `< t_partner`. The pick is the best-scoring of eligible
friends + critters; no eligible candidate at all → the existing
`None` path (solo backstop in `play_action_with`).

**Rationale**: owner-ratified — thresholds define who is worth
bothering; order-independent; a nearby low-value friend can never
veto partner play by out-scoring on distance.

## D4 — Score arithmetic and the total order

**Decision** (all f32):
- `value = play_need − w_busy·expected_wait − w_serious·top_non_play_pressure`
  (clarify ruling 2: seriousness reads the max pressure over
  eat/drink/sleep/cuddle/bath — play never counts against a
  candidate).
- friend `score = w_value·value − distance`; critter
  `score = critter_appeal − distance` (clarify ruling 3: standalone,
  unscaled).
- `expected_wait` = `(scene_min − elapsed).max(0)` in ticks, from the
  partner's `ActivityClock` and
  `Activity::bounds(&config.actions.durations).min`; 0 for a free
  friend. **A heuristic, not a promise** (review #7): `elapsed` is
  the inclusive F-031 count (`tick − started + 1`); a boundless
  activity (bounds `None`) waits 0; and only held-min scenes (true
  play duets) honor the estimate exactly — prunable scenes may end
  sooner, rest degrades to solo instead of ending. `w_busy` prices
  the estimate; the sweep prices `w_busy`.
- Ordering: `max` by `score` via `f32::total_cmp`, ties by the
  existing ascending `(manhattan_distance, tag 0=critter/1=friend,
  id)` — today's exact `min_by_key` order, moved behind the score. At
  defaults every candidate scores exactly `−distance` (small-int f32
  conversion is exact), so the order — including the
  critter-beats-friend tie — is bit-for-bit today's.

**Rationale**: FR-001/002/007; determinism with no NaN (validation
D7) and no new tie semantics.

## D5 — Busy-adjacent resolves to solo play, never propose, never idle

**Decision**: `play_action_with` (`selection.rs:340`) gains one rule:
an adjacent kitty target that is mid-scene yields `play_solo()` for
the tick instead of `Action::play_with` (which validate would
downgrade to Idle — a wasted turn) — the "waiting is spent playing"
edge case. Chase toward a non-adjacent busy friend is unchanged
`Action::Chase` (legal toward any kitty).

**Rationale**: FR-003 (gated/blocked ticks resolve to play, never
idle), FR-004 (no proposal until free — behavior-side, with the
engine's downgrade still behind it as defense in depth).

**Alternatives**: propose-and-let-validate-downgrade (rejected — a
knowingly wasted turn every waiting tick, and it books an Idle into
`last_action`); waiting via `wait_for_them` (rejected — that is the
approach-etiquette yield for mutual walks, not a play posture).

## D6 — Comfort weights: nested struct, trigger-only

**Decision**: `BehaviorConfig` gains
`#[serde(default, skip_serializing_if = "ComfortWeights::is_identity")]
comfort_weight: ComfortWeights` — six f32 fields (eat, drink, sleep,
play, cuddle, bath), each `default = 1.0`. `playful.rs:56-64` changes
from `highest_pressure() >= comfort` to
`max over NeedKind::ALL of weight(kind)·pressure(kind) >= comfort`.
The need identity was already discarded there (`(_, pressure)`), so
the weights move only the trigger — `selection::choose` after getting
serious is untouched (verified in-session; spec US2/AC4).

**Rationale**: FR-005; the measured lopsided gap (eat 35–52 peaks vs
routine bath 30–40) makes a global comfort a blunt tool.

## D7 — Validation

**Decision**: appended inside the existing `validate_behavior`
(spec-020 section order untouched): the three `w_*` and both `t_*`
must be finite and ≥ 0; the six comfort weights must be finite and
**strictly positive** (2026-08-30, review #5 — zero would disable
that need's trigger); `critter_appeal` must be finite (either sign — "less appealing than baseline" is a
meaningful sweep direction). Errors name `[behavior] <field>` /
`[behavior.comfort_weight] <need>`.

**Rationale**: FR-007 (no NaN enters the order); negative weights and
thresholds have no meaning (identity is 0/1.0), negative appeal does.

## D8 — Serialization: skip-at-identity keeps the stamp unmoved

**Decision**: every new field carries
`skip_serializing_if` at its identity value (0.0 / all-1.0), the
spec-039 pounce discipline (`config/mod.rs` pounce field comment).
`engine_defaults_sha256` therefore does NOT move — no re-baseline
debt. The served `cloudkitty.toml` gains only a commented
documentation block (the `[elements]` placement-dials pattern); no
keys, byte-level served-config churn zero.

**Rationale**: unlike 041 there is no value movement to carry; a
stamp move would be pure noise. Lab sweep configs set the dials
explicitly.

## D9 — Test strategy (rules 5/6)

**Must stay green (kept behavior — the headline pile)**: the entire
selection/playful battery at defaults (`selection.rs` tests :401+,
`playful.rs` tests, `approach_etiquette.rs`, behavior_variation),
`golden_evolution_flag_absent_10k_ticks` (pin `7b361b2a…` — must-green
here, NOT a regenerate), both shipped-config sweeps, defaults-stamp
tests (stamp unmoved — `any_default_moving_moves_the_stamp` keeps
passing via its live-dial probe), Article I–V property suites.

**New guards, each shown red first** (predict the failure before
running):
- value ranking: distant high-need friend beats adjacent zero-need
  one at `w_value > 0` (red: distance pick chooses the adjacent).
- eligibility: zero-need adjacent friend below `t_partner` → critter/
  solo instead of play_with (red: distance pick bothers it).
- `t_self`: own need below threshold → no friend bothered.
- seriousness cost: candidate with high eat pressure penalized at
  `w_serious > 0`; equal-play-pressure candidate NOT penalized for
  its play pressure (the non-play rule).
- wait cost: mid-scene candidate outranked at `w_busy > 0` where a
  free equal candidate exists; admitted at all only when
  `w_value > 0` (the D2 admission guard — red direction: at defaults
  a busy adjacent friend must NOT be picked).
- busy-adjacent fallback: adjacent mid-scene best pick → `play_solo`,
  never `play_with`, never `Idle`.
- critter appeal standalone: raising `w_value` alone moves no critter
  rank; raising `critter_appeal` alone moves only critters.
- comfort weights, both directions (spec US2/AC1-2): weighted
  crossing where unweighted wouldn't trip, and staying playful where
  unweighted would.
- identity guards: all-defaults selection equals today's pick on a
  staged mixed field (friends + critters + ties); all-1.0 weights
  reproduce the unweighted serious/playful decision on a pressure
  sweep.
- validation: nan/negative red-first per dial (extend the
  `[behavior]` validation test table).

**Known coupling to watch**: `solo_play_reach`/`urgent` interplay in
`play_action_with` (:344-350) — the scored pick must not change the
far-away-and-urgent solo rule; `should_wait_for` etiquette unchanged
on chase paths; opportunism (`take_what_is_here` → `adjacent_playmate`
:371) deliberately untouched (pre-existing busy-adjacency semantics —
out of scope, rule 3).
