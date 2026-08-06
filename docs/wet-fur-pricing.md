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

The rule itself: `ceiling + gain × max_admissible_bath_ratio < 75`,
enforced at config load (`config/validate.rs::validate_water`) and
re-proven at runtime (`tests/water_safeguard.rs`). At 3.5/60 the
maximum admissible bath ratio is ~4.28 (it was ~16.7 at 1.5/50) — a
roster cat more than ~4.3× as fastidious as baseline is a config error,
not a distress event waiting to happen.

## Where the law lives

- Mechanism + behavioral pins: `specs/024-wet-fur-batch/` (skirt-short,
  swim-long scenarios; the no-distress-from-swimming guarantee).
- Dial values + generation-2 context: `specs/026-in-water-obs/`.
- Enforcement: `config/validate.rs` (load), `tests/water_safeguard.rs`
  (runtime re-proof), the frozen `evals/v1` exams (certification).
- Config commentary: `cloudkitty.toml` `[water]`, which cites the
  60-roofline rationale.
