# exp-004 design inputs — working notes

**Status: WORKING NOTES, not a design.** Collected 2026-08-07 while
exp-003 was closing out. Nothing here is registered, decided, or costed.
When exp-004's prereg is written, each item is adopted (and cited),
consciously rejected, or deferred — nothing silently dropped. Precedent:
[exp-003-design-inputs.md](exp-003-design-inputs.md).

**The owner's stated priority: the meow rework, ASAP.** Everything else
below is secondary and mostly fits around it.

---

## 1. Meows — the reason exp-004 exists

Owner's framing: meow is *"the main vector for sharing kitty state"*, and
it should carry more signal and possibly cost less.

### The vocabulary gap, and why the obvious explanation is half right

`MessageKind::for_need` (`crates/cloudkitty-core/src/meow.rs`) returns a
message for Eat, Drink, Play and Cuddle, and **`None` for Sleep and
Bath**. `LEARNED_MEOWS` is 6 of the 7 kinds; `WaitForMe` is
engine-reserved for the yield rule and nothing else may spend it.

The owner's first reading was that Sleep and Bath are satisfiable solo,
so a message buys little. **That holds for Sleep and breaks for Bath.**

Verified in `action.rs`:

```rust
Activity::Grooming { target } => match target {
    None => lower_need(world, kitty_id, NeedKind::Bath, groom_relief),
    Some(friend) => {
        lower_need(world, friend,   NeedKind::Bath,   groom_relief);
        lower_need(world, kitty_id, NeedKind::Cuddle, cuddle_relief);
    }
},
```

**Another cat can relieve your Bath need by grooming you**, and the two
parties are paid in *different currencies* — the groomed gets Bath, the
groomer gets Cuddle.

How the three social actions actually pay out:

| action | actor gets | partner gets | partner bound? |
|---|---|---|---|
| `Sleeping { with }` | Sleep **+ Cuddle** | Cuddle | no — "a companion, never a conscript" |
| `Resting { with }` | Cuddle | Cuddle | **yes** — duet, same clock |
| `Grooming { target }` | **Cuddle** | **Bath** | no — target stays free |

Grooming is the only cross-currency action in the engine, and the only
one where the actor gets nothing for their own primary need. That makes
it **self-enforcing**: a groomer isn't doing a favour, they're being paid
in a currency they wanted. A wet cat is advertising a trade, not begging.

And there is no way to advertise it.

### The rule that actually predicts the current vocabulary

Not "solo-satisfiable" — eat, drink and play are all solo-satisfiable and
all have messages. What the four existing messages share is that
**another cat can change your outcome**. By that rule Bath belongs in the
set and Sleep does not, which is exactly the observed discrepancy.

Worth deciding explicitly which rule exp-004 adopts, because it
determines whether the change is "add `WantBath`" or "add messages for
everything and treat the channel as state broadcast."

### It has already cost us

- exp-003 was entirely about wet fur. **A wet cat cannot say it is wet**,
  and cannot request the one action that fixes it.
- **`GroomKitty` is completely absent from dataset v3** (classes 13/14/15
  empty). Scripted cats never groom each other, so the reciprocal trade
  the engine implements has never once occurred in demonstrator data. The
  BC clone cannot imitate it; PPO would have to discover the action *and*
  the coordination, with no channel to coordinate through.

### Cost, and who actually pays it

`cloudkitty.toml [meow]`: *"learned kitties are governed by the turn cost
alone."* `courtesy_ticks` (10), `urgent_courtesy_ticks` (5) and
`urgent_need_threshold` (75) bind **scripted behaviours only**. So for a
policy a meow costs exactly one action's opportunity cost, and "make it
cheaper" means changing **what a meow displaces** — letting it ride
alongside another action rather than replacing one.

### Bandwidth is probably not the constraint

The digest is `LEARNED_MEOWS.len() * 3` = **18 of 183 observation
values**, roughly 10% of everything a policy sees. Check what those three
values per kind encode before adding more: the limitation may be
*content* (kind only — no intensity, no addressee, no "I am heading
there") rather than capacity.

### The channel is empirically dead

- dataset v3: **3,892 channel decisions in 1.9M (0.2%)**, over only 3 of
  6 kinds.
- BC clone predicts meows at **0.0000** accuracy.
- PPO did not discover it in 20M ticks: greedy `meow/1k` 0.01–0.41 across
  all nine exp-003 candidates.
- **F-011**: meow restraint is a reward-structure equilibrium, not an
  engine guarantee. **F-012**: channel use is context-dependent — measure
  in policy company, never solo.

### A legible success criterion

If the rework works, **cats groom each other**: Bath and Cuddle both
fall, and action classes 13–15 (currently dead) come alive. That is far
more legible than "meow rate went up", and it is measurable with existing
instruments.

### Constraint

Anything touching the digest **bumps the observation schema** → another
generation wall → warm starts voided. So `WantBath` and "make meows
cheaper" are the *same* wall and want one spec, not two. Batch every
schema-level change exp-004 needs, as 026/027 were.

Engine work is **Product's, spec-first**.

---

## 2. Other knobs, with recommendations

**Potential-based shaping — implemented, never enabled.**
`Φ(s) = −coefficient × (active distress entries / roster)`, FR-009,
`enabled: false` in every config we have ever run. Dense where the team
reward is slow and diffuse (F-013 puts teammate credit in a 50–200 tick
band), aimed at exactly our failure mode, and **provably
policy-invariant** — it changes the learning signal, not the optimum.
Recommend a **registered arm** (on vs off) rather than a default: the
invariance is about the optimum, so "does it help in finite time" is
precisely what needs measuring. Two things to settle: the **coefficient**
(nothing registered) and the **γ** — `ShapingConfig::gamma` defaults to
**1.0** while training runs 0.998/0.995, and the proof needs them
matched. Left alone the guarantee silently degrades to approximate.
No engine or schema change; it is a `[rl.reward.shaping]` block.

**Chow/scarcity stratification in the family.** Config only. The single
chow tile that moved incident runs 9/60 → 1/60 makes contention the
best-evidenced mechanism we have. Tension to state rather than ignore:
**F-014 found scarcity hurts or does nothing for cooperative signal** —
that was about the *served* world, and using it as a *training* axis is a
different claim, but we are buying robustness and may be paying signal.

**Mixing — decide it, do not default it.** exp-002 falsified H1 (mixing
bought ≤ +0.0009 and cost 0.004–0.015); exp-003's self-play arm beat both
mixed arms on water, welfare and Nash simultaneously; and F-017 suggests
a *cost*. Two generations, no benefit. Either drop it or keep one arm to
close it out cleanly.

**Sampled selection — measure, do not adopt.** Cheap and tempting, but it
fixes a problem the served world does not have: at the deployed 2-of-4
composition the world shows **zero** distress under greedy. Costs:
certification does not transfer (every §9.1 number is greedy), it is not
a clean win even where it helps (incidents 92/270 → 69/270, three
candidates worse), and it is a registered condition, not a toggle (issue
#70). **Proposed test, ~20 min**: §9.1 water band + deployed-composition
probe under `--sample`, compared against greedy. Not yet run.

**Symmetry-breaking machinery — do not build.** The owner intends
heterogeneous agents (different models per seat) eventually, which
dissolves the symmetry problem at the root. What survives heterogeneity:
contention itself (two *different* models still want the same tile), and
the fact that until several models exist every all-policy evaluation
seats copies. So **fix the gate, not the policy** — and note the meow
work *is* the durable version of this investment, since signalling helps
heterogeneous agents where a per-seat identity feature would not.

**New architectures — parked.** The artifact contract pins a stateless
forward pass and `artifact_version` 1, so recurrence arrives as a format
change that validates itself. Naming already anticipates it
(`e007-lstm-s1`).

---

## 3. Failure-mode understanding carried forward

**The collapse is a self-interaction failure, and largely a symmetry
artifact (F-017).**

- At **one** policy seat, 8/9 exp-003 candidates score `max_distress_age`
  0. The policies are individually fine; the *population* fails.
- Under `--sample`, `floor_touches` **108,584 → 0** and worst distress
  **16,027 → 1,020**. Four identical deterministic policies pick the same
  action, converge on the same tile and deadlock.
- **Mixed arms improve 26× under sampling; self-play arms get slightly
  worse** — self-play already trained under self-contention and learned
  to break symmetry behaviourally.
- **exp-002 replicates the mixing gradient out-of-sample**: median
  distress M0 **0.0** → M33 **6.0** → M67 **28.5**, zero-rate 67% → 44%
  → 17%.
- The failing need is always **eat**, drink second — contested
  consumables. Cuddle and bath never appear in a healthy candidate.

**`all-policy` is not a shipping condition.** The served world seats
**two** policies among two scripted cats. §9.2 gates a population that
never runs.

**§9.2 needs respecifying, and it is blocking certification today.** It
admitted none of nine. Failures are **bimodal with two orders of
magnitude between the populations** — six candidates at 3–212
threshold-ticks per 100,000, three with multi-need saturation. Design any
replacement against **exp-002's 22 candidates as well as exp-003's 9**; a
criterion tuned only on the run that motivated it is how you get a gate
that admits your favourite.

---

## 4. Methodology lessons worth not relearning

- **`max_distress_age == 0` measures the seed band as much as the
  policy.** Three independent signs: §9.2 admitting none of nine; the
  bimodal split; and a screen that voided itself because the *control*
  showed 241-tick distress on a band where the same artifact on the same
  world had scored zero.
- **Relative bounds transfer across worlds; absolute ones rot.** exp-002's
  "in-water ≤ 3.0%" became unsatisfiable when the baseline moved to
  3.44%. Bounds expressed as multiples of `B`, re-measured per world,
  survived both the 11-tile lake retrofit and the 24×24 → 20×20 move —
  twice rescuing a correct answer from an absolute threshold.
- **The welfare margin was 24× too loose.** Control seed-to-seed sd
  0.00114 → SE of a 30-seed mean 0.00021; the flat 0.005 two screens used
  is 24× that, which is why they "spent" 76% and 86% of an allowance
  while nowhere near a real effect. Derive it: 0.002 ≈ 10× SE.
- **Element density is a visual metric, not a welfare one.** The 20×20
  world is 16% "busier" by density and the cats are measurably better off
  in it. Walk distances track welfare better but also misled (chow +12%
  farther, welfare improved). Measure welfare; do not infer it.
- **Two mechanisms proposed and refuted — do not resurrect.** (a) "The
  3.5/60 dial pushes Bath to distress" — structurally impossible; the
  same inequality that makes the safeguard unreachable by water makes 90
  unreachable. (b) "Distress is cuddle-driven because policies never
  meow" — an artifact of an underpowered probe; on the real worst seeds
  cuddle is 0.7% pooled and zero for six of nine.
- **Rebuild the Python binding after every engine change.** It was
  reporting observation schema 1 three commits after the engine moved.

---

## 5. Open decisions

- Meow: which rule — "another cat can change your outcome" (add
  `WantBath`) or "broadcast state" (messages for everything)?
- Meow: cheaper how — ride-along with another action, or a lower turn
  cost?
- Shaping: coefficient by pilot, or a registered value with
  justification?
- Mixing: drop outright, or one arm to close it out?
- Sampling: run the 20-minute measurement, or leave greedy alone?
- §9.2: respecify now (it blocks certification) or fold into exp-004's
  prereg?
