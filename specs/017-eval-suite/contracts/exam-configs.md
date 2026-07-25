# Contract: The v1 Exam Worlds (FR-005..FR-008; US2, US3)

Full designs for the six files of `evals/v1/`. These TOMLs are the
plan-phase deliverable the spec required; at landing they are committed
byte-for-byte and their hashes recorded in the manifest — after that they
never change. Every file carries its rationale in comments (FR-005), pins
`[rl.reward]` (the untouchable objective: Nash, p = 0, ε = 0.01, level)
and `[rl.eval]` (the 10 fixed seeds, 20,000 ticks), so the frozen file
fully determines its measurement. `[world].seed` and `tick_ms` are
structural (the harness overrides the seed per run; no wall clock exists
headlessly). Unstated sections take engine defaults, exactly as
`training.toml` does.

Distinctness (SC-005): every axis value below differs from both
`cloudkitty.toml` (32×32/4, water 8–10, no full trait profiles) and
`training.toml` (24×24/5, ×1.25 rates, one override per kitty).

## scale.toml — 48×48, 8 kitties

Axis: distance and crowds. 2.25× the bar's tiles, double its roster, and
the served world's element *counts* kept deliberately unscaled — the same
resources, diluted across a much bigger meadow: longer walks, more kitties
per bowl, coordination at range (meows carry need signals world-wide;
sight slots don't). The safeguard spawner guarantees relief as everywhere.

```toml
# evals/v1/scale.toml — the scale exam (spec 017, FR-005).
# FROZEN at landing: eval-suite-v1. Do not edit; see evals/v1/manifest.toml.
#
# Does cooperation survive distance and crowds? 2,304 tiles (2.25x the
# default world), 8 kitties (2x), and the default world's element counts
# left deliberately UNSCALED: dilution and travel are the exam. Article I
# is fully active - the safeguard still spawns relief; scarcity here means
# walking, yielding, and asking (meows), never suffering.

[world]
width = 48
height = 48
tick_ms = 800        # never consulted headlessly (budgetless dispatch)
seed = 1             # structural; the harness seeds each run explicitly

# Behaviors here are placeholders: standard-exam scoring assigns the
# subject per roster mode, exactly as on the default world.
[[kitty]]
id = 1
name = "Miso"
x = 6
y = 6
behavior = "needs_driven"

[[kitty]]
id = 2
name = "Biscuit"
x = 41
y = 6
behavior = "needs_driven"

[[kitty]]
id = 3
name = "Pumpkin"
x = 6
y = 41
behavior = "needs_driven"

[[kitty]]
id = 4
name = "Kittybear"
x = 41
y = 41
behavior = "needs_driven"

[[kitty]]
id = 5
name = "Clementine"
x = 24
y = 24
behavior = "needs_driven"

[[kitty]]
id = 6
name = "Mochi"
x = 24
y = 6
behavior = "needs_driven"

[[kitty]]
id = 7
name = "Marmalade"
x = 6
y = 24
behavior = "needs_driven"

[[kitty]]
id = 8
name = "Noodle"
x = 41
y = 24
behavior = "needs_driven"

# The default world's rates: metabolism is not this exam's axis.
[needs]
eat = 0.4
drink = 0.4
sleep = 0.3
play = 0.4
cuddle = 0.4
bath = 0.2

# The default world's counts on 2.25x the area - dilution IS the exam.
[elements.water]
min = 8
max = 10

[elements.chow]
min = 8
max = 10
servings = 5

[elements.bug]
min = 4
max = 8
ttl = 300

[elements.greeble]
min = 1
max = 3
ttl = 300

[elements.sunbeam]
min = 5
max = 6
ttl = 300

[rl.reward]
p = 0.0          # Nash welfare - the objective, unchanged (spec 017 FR-014)
epsilon = 0.01
mode = "level"

[rl.eval]
seeds = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
ticks = 20000
```

## scarcity.toml — the validation floor

Axis: contention. The bar's own geometry and roster, with every element
minimum at the lawful floor the engine's validation permits (`hard_min`:
greebles 0, everything else 1) and maxima one above — one puddle, one
bowl, one sunbeam, four cats. Yielding, turn-taking, and walking away are
the whole game. The default world's config file itself invites this
("lower these for a sparser, more demanding world — the constitution
still guarantees relief, but the cats will work harder for it").

```toml
# evals/v1/scarcity.toml — the scarcity exam (spec 017, FR-005).
# FROZEN at landing: eval-suite-v1. Do not edit; see evals/v1/manifest.toml.
#
# Does yielding survive genuine contention? The default world's geometry
# and roster with every element minimum at the validation floor (greebles
# 0, all else 1) and maxima at floor+1: one puddle, one bowl, one sunbeam,
# four cats. The safeguard spawner still answers every need above its
# threshold - working harder for relief is lawful; going without is not.
# NOTE: the default world's welfare bounds are calibrated to the default
# world's abundance. Scores here mean nothing against those bounds and are
# never judged by them (FR-003) - the paired needs_driven baseline is this
# exam's yardstick.

[world]
width = 32
height = 32
tick_ms = 800
seed = 1

# The bar's roster (positions and Pumpkin's snacky trait included), so
# contention is the ONLY axis this exam moves.
[[kitty]]
id = 1
name = "Miso"
x = 10
y = 12
behavior = "needs_driven"

[[kitty]]
id = 2
name = "Biscuit"
x = 20
y = 18
behavior = "needs_driven"

[[kitty]]
id = 3
name = "Pumpkin"
x = 16
y = 8
behavior = "needs_driven"
[kitty.needs]
eat = 0.8

[[kitty]]
id = 4
name = "Kittybear"
x = 5
y = 5
behavior = "needs_driven"

[needs]
eat = 0.4
drink = 0.4
sleep = 0.3
play = 0.4
cuddle = 0.4
bath = 0.2

# The floor. hard_min is 1 (greebles 0); maxima at floor+1 keep the
# population lean instead of drifting back toward abundance.
[elements.water]
min = 1
max = 2

[elements.chow]
min = 1
max = 2
servings = 5

[elements.bug]
min = 1
max = 2
ttl = 300

[elements.greeble]
min = 0
max = 1
ttl = 300

[elements.sunbeam]
min = 1
max = 2
ttl = 300

[rl.reward]
p = 0.0
epsilon = 0.01
mode = "level"

[rl.eval]
seeds = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
ticks = 20000
```

## heterogeneity.toml — extreme lawful trait spread

Axis: fairness across metabolisms. Five kitties with full six-need trait
profiles spanning 0.05 to 2.0 — a 40× spread (the default world has one
mild override; training tops out at 2× on single needs). Nash welfare must
serve the hummingbird without abandoning the stone; the observation's
trait features (encoded as `rate / reference_need_rate`, clamped at 4.0 —
nothing here clips) have to do real work.

```toml
# evals/v1/heterogeneity.toml — the heterogeneity exam (spec 017, FR-005).
# FROZEN at landing: eval-suite-v1. Do not edit; see evals/v1/manifest.toml.
#
# Does fairness survive wildly different metabolisms? Full trait profiles
# spanning 0.05..2.0 per-tick rise (40x) - all lawful (rates >= 0), all
# fully observable (trait encoding clamps at 4.0; the top rate here is
# 2.0). A policy tuned to the average cat fails Miso, who needs constant
# service, or squanders the meadow on Biscuit, who needs almost nothing -
# under Nash, the least-served metabolism IS the score.

[world]
width = 32
height = 32
tick_ms = 800
seed = 1

[[kitty]]
id = 1
name = "Miso"
x = 6
y = 6
behavior = "needs_driven"
# The hummingbird: everything burns fast.
[kitty.needs]
eat = 1.6
drink = 2.0
sleep = 1.2
play = 1.6
cuddle = 1.2
bath = 0.8

[[kitty]]
id = 2
name = "Biscuit"
x = 25
y = 6
behavior = "needs_driven"
# The stone: needs almost nothing, almost ever.
[kitty.needs]
eat = 0.1
drink = 0.1
sleep = 0.05
play = 0.1
cuddle = 0.05
bath = 0.05

[[kitty]]
id = 3
name = "Pumpkin"
x = 6
y = 25
behavior = "needs_driven"
# Feast-or-famine: one towering need, the rest quiet.
[kitty.needs]
eat = 2.0
drink = 0.1
sleep = 0.3
play = 0.1
cuddle = 0.4
bath = 0.2

[[kitty]]
id = 4
name = "Kittybear"
x = 25
y = 25
behavior = "needs_driven"
# The sleeper: sunbeams matter enormously; little else does.
[kitty.needs]
eat = 0.2
drink = 0.2
sleep = 1.5
play = 0.05
cuddle = 0.3
bath = 0.1

[[kitty]]
id = 5
name = "Clementine"
x = 16
y = 16
behavior = "needs_driven"
# The social butterfly: company is the need; upkeep is an afterthought.
[kitty.needs]
eat = 0.3
drink = 0.3
sleep = 0.15
play = 1.2
cuddle = 1.8
bath = 0.3

# Globals are the default world's; every kitty above overrides all six.
[needs]
eat = 0.4
drink = 0.4
sleep = 0.3
play = 0.4
cuddle = 0.4
bath = 0.2

# The default world's abundance: resources are not this exam's axis.
[elements.water]
min = 8
max = 10

[elements.chow]
min = 8
max = 10
servings = 5

[elements.bug]
min = 4
max = 8
ttl = 300

[elements.greeble]
min = 1
max = 3
ttl = 300

[elements.sunbeam]
min = 5
max = 6
ttl = 300

[rl.reward]
p = 0.0
epsilon = 0.01
mode = "level"

[rl.eval]
seeds = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
ticks = 20000
```

## The mixed-roster cells — 28×28, 6 kitties, three compositions

Axis: partner composition (spec US3). Geometry deliberately neither the
bar's (32×32) nor the gym's (24×24); roster of 6 likewise. The three
files are identical except the `behavior` column — the cell-sibling
guarding test enforces exactly that. Biscuit is the `playful` seat in
every cell (canon: Biscuit is the served world's playful cat), so every
composition contains a partner with a genuinely different convention;
in the host cell the *only* scripted cat is playful — maximum convention
distance in the strongest probe. Elements scale to ~0.77× area
(near-default density): composition, not scarcity, is the exam.

Seat maps (`c` = `policy:candidate`, `n` = `needs_driven`, `p` = `playful`):

| Kitty (id) | guest | half | host |
|---|---|---|---|
| Miso (1) | **c** | **c** | **c** |
| Biscuit (2) | p | p | p |
| Pumpkin (3) | n | **c** | **c** |
| Kittybear (4) | n | n | **c** |
| Clementine (5) | n | **c** | **c** |
| Mochi (6) | n | n | **c** |

```toml
# evals/v1/mixed-roster-guest.toml — the mixed-roster exam, guest cell
# (spec 017, US3 / FR-008). FROZEN at landing: eval-suite-v1.
# Identical to mixed-roster-{half,host}.toml except the behavior column
# (guarded by test). One candidate seat among five scripted cats:
# baseline sociability - does the learned cat integrate?
#
# policy:candidate is bound by the harness at invocation to whatever
# artifact (or aliased built-in) is under test; no artifact is ever named
# here (FR-011). Outside a suite run this file boots nothing - an unbound
# candidate policy fails loudly at startup, like any unconfigured policy.

[world]
width = 28
height = 28
tick_ms = 800
seed = 1

[[kitty]]
id = 1
name = "Miso"
x = 5
y = 5
behavior = "policy:candidate"

[[kitty]]
id = 2
name = "Biscuit"
x = 22
y = 5
# The convention outsider in every cell: playful ignores needs below its
# comfort threshold, chases critters, and conscripts playmates - a
# genuinely different dialect from anything needs_driven does.
behavior = "playful"

[[kitty]]
id = 3
name = "Pumpkin"
x = 5
y = 22
behavior = "needs_driven"

[[kitty]]
id = 4
name = "Kittybear"
x = 22
y = 22
behavior = "needs_driven"

[[kitty]]
id = 5
name = "Clementine"
x = 13
y = 13
behavior = "needs_driven"

[[kitty]]
id = 6
name = "Mochi"
x = 13
y = 20
behavior = "needs_driven"

[needs]
eat = 0.4
drink = 0.4
sleep = 0.3
play = 0.4
cuddle = 0.4
bath = 0.2

# Near-default density for 784 tiles (~0.77x the default area):
# composition, not scarcity, is this exam's axis.
[elements.water]
min = 6
max = 8

[elements.chow]
min = 6
max = 8
servings = 5

[elements.bug]
min = 3
max = 6
ttl = 300

[elements.greeble]
min = 1
max = 2
ttl = 300

[elements.sunbeam]
min = 4
max = 5
ttl = 300

[rl.reward]
p = 0.0
epsilon = 0.01
mode = "level"

[rl.eval]
seeds = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
ticks = 20000
```

`mixed-roster-half.toml`: byte-identical except the header comment names
the half cell ("convention friction at its maximum: neither group can
dictate the meadow's rhythm") and the seat map — Miso, Pumpkin,
Clementine → `policy:candidate`; Kittybear, Mochi → `needs_driven`;
Biscuit → `playful`.

`mixed-roster-host.toml`: byte-identical except the header comment names
the host cell ("the exploitation probe: five of a mind, hosting one cat
that doesn't speak theirs — the guest-welfare differential is watching")
and the seat map — every kitty → `policy:candidate` except Biscuit →
`playful`.

The all-scripted baseline is **derived, never committed**: each cell with
`policy:candidate` rewritten to `needs_driven` (Biscuit stays `playful`),
run on the same seeds (research.md R4).

## Measured design baselines (smoke runs, 2026-07-24)

2-seed × 2,000-tick `needs_driven` smoke runs of these designs, before
freezing (plan-phase due diligence; the lawfulness guarding test re-proves
this at implementation):

- **scarcity**: team welfare ≈ 0.87 (vs ≈ 0.90 on the default world),
  least-happy mean ≈ 84, zero distress buildup — lawful, and harder in
  the intended way (walking and yielding, not suffering).
- **mixed-roster world** (all-`needs_driven` normalization): all six
  kitties ≈ 91 mean, zero distress — a comfortable stage; composition
  will be the only pressure. (The `playful` seat path itself is exercised
  by guarding test 7's `subject: None` cell runs.)
- **heterogeneity**: lawful — zero floor touches, max distress age ≈ 69
  (bound: 150) — and deliberately *below* the default world's calibrated
  welfare bounds: Miso the hummingbird sits at mean ≈ 61 with ~8–10%
  low-share under `needs_driven`, while Biscuit the stone coasts at ≈ 97.
  This is the exam working as designed, and the reporting doctrine
  (FR-003, R11) exists for exactly this file: those bounds are the bar's,
  not this world's. The headroom is the instrument — a policy that
  anticipates and serves the fastest metabolism can lift the least-happy
  kitty well above the greedy baseline, and Nash pays for precisely that.

## Out-group shares (drive the identity thresholds)

| Cell | Scripted seats | Share | least_happy_threshold (n=10, tail ≤ 1%) |
|---|---|---|---|
| guest | 5 of 6 | 5/6 | 11 — cannot bind (chance dominates) |
| half | 3 of 6 | 1/2 | 10 |
| host | 1 of 6 | 1/6 | 6 |
