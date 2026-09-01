# Wet-fur pricing: the water charge and how its dials were derived

Durable record of the design reasoning behind `[water] bath_gain` and
`bath_gain_ceiling` — the arithmetic lived only in `BACKLOG.md` until
2026-08-06, and the backlog is for future work, not doctrine. Mechanism
shipped as spec 024 (2026-08-01); dials re-set by spec 026 (2026-08-05).
The specs hold the requirements; this page holds the *why* behind the
numbers, in one place, at the values that actually shipped.

## The charge law (spec 024)

Occupying a water tile charges the **bath need** by `bath_gain` per
tick, scaled per cat by its own bath rise rate relative to the world
baseline (`gain × bath_rise / 0.2`), and only while bath is below
`bath_gain_ceiling`. Happiness = 100 − weighted needs, so the price is
real to every decider through one door: scripted ladders feel it as
need pressure, learned policies as reward. One per-tick knob prices
both crossing and lounging; drinking stays free (Article I — the
puddle as relief destination is never frustrated).

**Hard doctrine (owner, 2026-07-31): water is a cost, never a wall.**
Every water tile stays passable; a kitty surrounded by water can always
swim out. Pinned by spec 010's wade tests and 024's charge law; any
future water mechanic inherits the constraint. Article I's relief
guarantees assume it.

## The original derivation (owner, 2026-07-31 — dial 1.5, ceiling 50)

Calibration target: one wet tile ≈ the pain of a ~4-tick detour
(matching `water_step_cost = 4.0`, the effort the scripted pathfinder
already imagined). The arithmetic, with order-of-magnitude error bars:

- A spike of S bath points persists ~150 ticks (half a groom cycle).
- At happiness weight 0.15: `0.15 × S × 150 ≈ 22.5·S` happiness·ticks
  of integrated cost per wet tick.
- A 2-tile detour around a 1-tile puddle costs ~25 happiness·ticks.
- So **S ≈ 1.0 is the single-tile indifference point**; 1.5 puts cats
  strictly on the skirt-the-puddle side while still swimming when
  detours are long — slightly-averse-but-willing, the catlike setting.

Legible framing: 1.0 = 5× the ambient bath rise (0.2/tick). Graceful
failure in both directions: too strong just looks like the old scripted
skirting; too weak preserves a quirk already ruled livable. The ceiling
(then 50) exists so voluntary pond-lounging can never carry bath toward
the safeguard line — certification hygiene by construction.

## The shipped dials (spec 026, owner 2026-08-05 — **3.5 / 60**)

The owner raised the charge for exp-003: a higher gain and ceiling mean
more accumulated happiness cost per swim, i.e. more signal for PPO to
learn not to lounge in water. The first pick was 3.5/65; **65 fell to
frozen-exam arithmetic**. `evals/v1/heterogeneity.toml` seats a 4×-bath
cat whose per-tick charge is 14, and frozen exams can never be edited:
`65 + 14 = 79 ≥ 75` (the safeguard threshold) fails the
certification-hygiene rule. `60 + 14 = 74` is the exact roofline that
exam permits, so **60 it is** — a live-design decision constrained by a
frozen artifact, recorded in spec 026's Clarifications.

The rule itself:
`ceiling + gain × max_admissible_bath_ratio × max(1, contagion_factor) < 75`,
enforced at config load (`config/validate.rs::validate_water`) and
re-proven at runtime (`tests/water_safeguard.rs`, both charge sources).
Spec 044 (waterline contagion) added the `max(1, contagion_factor)`
term: a dry cat whose own activity names an adjacent in-water partner
pays `factor × gain × bath_ratio` under the same ceiling — the dry and
wet member never both pay, so at factor ≤ 1 occupancy remains the
worst case and the arithmetic is unchanged. At 3.5/60 and factor ≤ 1
the maximum admissible bath ratio is ~4.28 (it was ~16.7 at 1.5/50) —
a roster cat more than ~4.3× as fastidious as baseline is a config
error, not a distress event waiting to happen. Above factor 1 the
contagion charge is the worst case and the admissible ratio shrinks to
`(75 − ceiling) / (gain × factor)`; note
`experiments/tools/family-gen` asserts the ~4.28 occupancy-era bound
and would need the same widening before any factor > 1 ever ships.

## Membership: who pays the contagion charge (spec 045)

`[water] contagion_membership` parameterizes the 044 charge's payer
set. `"option_a"` (the default, absent ≡ shipped 044 byte-identical):
only the dry cat whose OWN activity names a wet adjacent partner pays.
`"bidirectional"` (a lab dial for the water's-edge avoidance smoke,
owner-directed 2026-08-31): the other role is admitted too — a dry cat
that a wet adjacent cat's activity names (an idle groomee, say) also
pays, **either role, dry members only**. Everything else is 044 law
verbatim: same formula, same pre-charge ceiling gate, same wet-member
exemption, same current-adjacency requirement (`is_available_friend`,
checked against the actual namer), and at most **one charge per cat per
tick** however many roles or wet namers admit it (structural — the
membership set is a `BTreeSet`). Membership moves *who* pays, never the
per-cat per-tick maximum, so the budget rule above stands verbatim
under both values — asserted by a membership-invariance test arm, not
assumed. An unknown TOML value refuses the config naming both legal
values. The armed boot-log line names the active rule.

## The charge-aware ladder (spec 045, lab-only)

`[behavior] contagion_aware_ladder` (bool, default false): when on, the
built-in chooser prices a candidate partnered scene's **expected
contagion exposure** into its existing scores — scene-total under the
active membership rule (owner-clarified: egocentric pricing would make
the smoke's C and D arms choose identically), in bath need-points, the
score's existing currency:

`Σ over payers: 0 if payer.bath ≥ ceiling, else min(charge(payer) ×
E_ticks(kind), headroom + one full charge)` — with `charge` read from
`Config::contagion_charge`, the ONE formula the engine's charge arm
shares, and the cap engine-faithful to the pre-charge gate's documented
overshoot (Experiments ruling 2026-09-01; a headroom-only clamp
under-priced exactly the near-ceiling cats)

`E_ticks` is the scene's configured **minimum** duration
(`Activity::bounds`, the one activity→duration authority; grooming
reads `durations.bath`) — the same horizon as the chooser's
`expected_wait` and needflow's relief model, a conservative weight that
never manufactures avoidance.
Four seams, all behind the gate: the partnered-relief score
(`selection::scored`), per-candidate play ranking
(`selection::play_score` — a dry playmate outranks an equal wet one;
reachable only from the Playful behavior, and its 1:1
need-points-per-tile currency is a deliberate disclosed ruling), the
groom response (declines only when exposure exceeds the scene's total
value: the groomee's bath pressure plus the groomer's own expected
`groom_cuddle_relief`), and the cosleep friend-pick (a companion whose
exposure exceeds the decider's cuddle pressure plus the companion's
tier relief is skipped — the cat still naps, just not against wet fur).
Every decline is a choice, never a refusal; legality is untouched
(Article IV). Payer-set note: play is reciprocal, so its dry member
pays under BOTH membership rules — play carries no membership contrast
by design (Experiments ruling 2026-09-01). Scope disclosure: only partners wet at DECISION
time are priced — mid-scene waterline crossings are neither charged nor
discounted (research.md D4's wet-now disclosure; the smoke's readout
section carries the consequence). Off ⇒ every seam short-circuits
before any arithmetic: structurally byte-identical, and deliberately
NOT auto-on with the factor (smoke arm B needs an armed charge under a
charge-blind ladder). When armed, one extra boot-log line says so.

Gen 1 flip note (operational): `contagion_factor` has an engine
default of 0.0, is skipped from serialization at 0.0, and is outside
the snapshot fingerprint — the served `cloudkitty.toml` has no
`[water]` table today, so the flip *creates* one. `WaterConfig` is
`deny_unknown_fields`: after the flip, rolling back to a pre-044
binary also requires deleting the key from the config, or the old
binary refuses to boot. The dial's live value is legible in exactly
one place on the box: the "waterline contagion" boot-log line.

## Where the law lives

- Mechanism + behavioral pins: `specs/024-wet-fur-batch/` (skirt-short,
  swim-long scenarios; the no-distress-from-swimming guarantee).
- Dial values + generation-2 context: `specs/026-in-water-obs/`.
- Enforcement: `config/validate.rs` (load), `tests/water_safeguard.rs`
  (runtime re-proof), the frozen `evals/v1` exams (certification).
- Contagion mechanism + armed pins: `specs/044-waterline-contagion/`,
  `world.rs::advance_needs` (the charge arm),
  `tests/waterline_contagion.rs` (armed behavior).
- Membership dial + charge-aware ladder: `specs/045-contagion-membership/`,
  `world.rs::advance_needs` (the bidirectional arm of the membership
  set), `behavior/selection.rs::expected_scene_exposure` (the exposure
  law + the scored/play seams),
  `behavior/needs_driven.rs::groom_response` (the groom seam — the one
  kitty-groom initiation path), `tests/waterline_contagion.rs`
  (membership differentials), `cloudkitty-rl/src/mask.rs` tests
  (FR-007: neither dial ever moves a legality mask).
- Config commentary: `cloudkitty.toml` `[water]`, which cites the
  60-roofline rationale.
