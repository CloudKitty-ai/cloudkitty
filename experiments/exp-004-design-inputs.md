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
Bath**. `LEARNED_MEOWS` is 6 of the 7 kinds; `WaitForMe` is reserved
for the yield rule — by menu construction (policies can't select it)
and scripted convention, **not** engine law: `validate` accepts any
non-Purr meow from any proposal source. If exp-004 restructures the
vocabulary, that asymmetry belongs in the spec.

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

### Bandwidth is not the constraint — content is (now verified)

The digest is `LEARNED_MEOWS.len() * 3` = **18 of 183 observation
values**, roughly 10% of everything a policy sees. What the three
values per kind actually encode (`observe.rs:331-359`): a
recency-weighted presence — the freshest heard meow of that kind,
`1 − age/window`, window 10 ticks, own meows excluded — plus the
relative position `(dx, dy)` of the *nearest* current emitter. So the
channel already carries recency and direction, but **no intensity, no
addressee, no emitter identity** — and with two same-kind emitters the
presence and the position can describe *different cats*.

Three engine facts that sharpen the design space:

- **Meows are a global broadcast.** The digest filters by kind and
  self-exclusion only — no range, no falloff. A `WantBath` meow would
  be heard grid-wide for 10 ticks, and the digest already hands a
  responder the direction to walk. Grooming requires adjacency and a
  free target, so that navigation signal is exactly what a responder
  needs.
- **The emitter is blind to its own signal.** Own meows are excluded
  from the digest and the forward pass is stateless, so a policy
  cannot know it already asked. Repeating a request costs a full turn
  each time, with no observable state to amortize against — the
  strongest argument for the ride-along form of "cheaper".
- **Purr is already a gated meow** (`purr_earned` gates its mask row) —
  standing precedent if exp-004 wants a conditionally-legal message.

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

### Cost and spam — the resolved shape (owner discussion, 2026-08-08)

The turn cost is not buying anything. In signaling theory, cost keeps
signals honest **when interests conflict**; CloudKitty's reward is the
team welfare aggregate at p = 0, so interests are aligned, nobody
profits from lying about being wet, and cheap talk is stable (the
emergent-communication literature gets informative protocols from
completely free channels in cooperative settings). The turn cost is
pure friction — and exp-003 measured the friction winning: 0.2% of the
dataset, BC 0.0000, meow/1k 0.01–0.41. **Zero the marginal cost;
prevent spam mechanically, not motivationally.**

What spam would actually harm, and where each harm is properly fixed:

- **Observation pollution — already bounded by the digest.** Presence is
  a max over recency; a cat meowing every tick produces a *constant*,
  and constants carry no information — gradients learn to ignore them.
  Spam neuters the spammer, not the world.
- **Occlusion is the real channel harm** (freshest/nearest collapse
  lets one nearby chatterbox mask a distant genuine signaler) — and it
  is a *digest* defect, not a price defect; a turn cost wouldn't fix it
  either. Fix it in the digest while the schema is open.
- **UX** (client renders meows) — a rate problem; the cooldown handles
  it.

The mechanism package:

1. **Ride-along emission: the action becomes (activity, message).** Two
   output heads on the shared trunk — activity (menu minus the six Meow
   rows, 40→34) and message (Silent + kinds) — instead of a 34×7 joint
   menu. Factored policy: log-probs, entropy, KL all sum across heads;
   one shared advantage credits both; BC becomes two masked CEs
   (dataset v4 grows a `label_msg` column). Full generation wall
   (action schema, mask schema, artifact_version) — already being paid.
   **Determinism care**: `DecisionRng` deals ONE u64 per kitty per
   tick; sample both heads by splitting that u64 (two u32s), never by
   drawing twice from the master stream. Do NOT implement cheap meows
   as a free extra decision in the same tick — variable decision counts
   break the determinism contract and bc-collect row alignment.
2. **Grounded legality — the Purr pattern generalized.** `WantBath`
   legal only while Bath is actually above an announce threshold (with
   hysteresis), as `Purr` already requires `purr_earned`. This converts
   the channel from cheap talk to *certified state* — and dissolves the
   spam/signal distinction: "meow whenever legal" then IS the honest
   broadcast the owner asked for, not spam.
3. **Cooldown via the mask — courtesy for everyone.** `can_meow` /
   `courtesy_ticks` already exist engine-side but bind scripted cats
   only; wire them into the message-head mask. Setting cooldown =
   `recent_window_ticks` (both already 10) means one cat holds at most
   one live digest entry — occlusion shrinks to a corner case — and a
   dark mask row is a mechanical patch for the blind emitter: it
   *cannot* wastefully repeat what it cannot remember asking.
4. **Digest fixes in the same schema bump**: presence and direction
   must describe the same cat; optionally add an intensity value per
   kind — trustworthy now, because emission is grounded.

**Anti-recommendation: no per-meow reward penalty.** F-011 says
restraint is already a reward equilibrium — the channel's problem is
too much restraint. A penalty is the dead-channel medicine that
produced meow/1k 0.01. Spam control lives in the mask and digest, where
it cannot distort what the reward teaches. Expect training-time
babbling from the entropy bonus and welcome it (it exercises the
channel so listeners have correlations to learn); convergence behavior
is what the F-012-compliant measurement judges.

### The demonstrator plan (before BC v4)

**Cosleeping needs routing, not a boost — verified 2026-08-08.**
`apply_sleep_relief`: sleeper gets `sleep_relief` 5 (8 in sunbeam), and
with a partner adjacent **both** cats get `cuddle_relief` 15/tick; two
mutual co-sleepers each collect 5 sleep + 30 cuddle/tick — strictly
better than a rest duet on every axis, and non-binding. "Available"
means **adjacent, full stop** (`world.rs:1078`; co-sleep and grooming
deliberately skip the conscriptable check — spec-021 doctrine, busy
neighbors are lawful relief, `docs/cuddle-relief-semantics.md`). The
companion can eat, groom, or just stand there and still be paid; grants
stop the tick they step away (test:
`a_departed_cosleeping_partner_stops_granting_cuddles`). Yet dataset v3
shows **co-sleep at 5.6% of sleep decisions** (9,353 vs 157,282 solo),
because `needs_driven` prefers sunbeams and only offers
`with: adjacent_friend` as a fallback when no sunbeam is worth walking
to — cats trade a 15+15 mutual payout for a +3 sunbeam bonus. The fix
is the napper's routing alone (walk to a friend when cuddle is real;
sunbeam when it isn't); the friend needs no behavior change at all.
This weakens the case that `WantSleep` is load-bearing — it remains a
policy-side coordination aid (a policy can't see where friends are),
and its scripted response is the cheapest favor in the game (stand
nearby, keep your errand, collect 15/tick).

**WantBath is the load-bearing kind, and it demonstrates a trade, not a
request.** Bath is self-satisfiable at the *same* relief (`GroomSelf`
20, 140k decisions in v3), so a needy scripted cat self-grooms before
anyone answers. The rule that fills GroomKitty 13–15 is on the
**responder**: "my cuddle need is real + someone meowed WantBath → walk
over and groom them" (15 cuddle to me, 20 bath to them, they stay
free). The groomer initiates because the groomer is the one being paid.

**Imitability principle — write it into the spec**: scripted responders
must key on the **meow**, not on privileged need-reading. Scripted
behaviors can see other cats' needs directly; policies see only the
digest. Only when the demonstrated chain (need rises → meow → friend
approaches → groom) is a function of the policy's own observation space
can BC clone it.

**Consequences to budget**: new scripted behavior moves `B` — full
re-baseline before the exp-004 prereg freeze (re-baseline first, never
freeze first). Water metrics will shift too: scripted grooming is part
of F-016's wet-fur feedback loop, and a groom-response channel gives
bath relief a second path; the relative-B construction absorbs it.

**Order of work**: (1) the batched schema spec — message head,
`WantBath` (+`WantSleep` if adopted), grounded masks, cooldown-for-all,
digest fixes — Product's, spec-first; (2) scripted updates in the same
generation: bath-announce emission, meow-keyed groom response, cosleep
routing preference; (3) re-baseline `B`; (4) collect dataset v4 —
GroomKitty 13–15 and the new meow rows must be nonzero **by
construction**, checkable the day collection finishes.

### Cosleep credit: pricing presence (owner review, 2026-08-08 — UNDECIDED)

The owner is not sold on "just standing gives full credit" as built.
Two corrections that sharpen what the mechanism actually is, before the
options: the credit is **directed** (only the companion the sleeper
*named* is paid; passersby get nothing) and **self-limiting** (relief
clamps at zero — no banking, no farming beyond real need). The genuinely
degenerate part is the **schedule**: cuddle rises 0.4/tick and relieves
at 15/tick of contact, so one serviced tick erases ~37 ticks of
accumulation and a need at 60 clears in four. Companionship is
economically *instantaneous* — duration, the thing that would make
staying a commitment, is irrelevant. The mechanism is defensible; the
pricing makes presence trivial.

⚠️ **Shared-dial trap**: `cuddle_relief` is one dial feeding three
flows — the grooming actor's payment (`action.rs:705`), the rest duet
(740–741), and cosleep (783/789). Any cosleep-specific retune needs its
**own dial** or it silently drags the grooming trade and rest duets
along (the F-016 coupling, again).

Options, judged on: learnability (a contingent decision with gradient
inside F-013's 50–200-tick credit band), legibility (F-015
class-conditioned attribution), the non-conscription doctrine (spec
021), robustness to degenerate attractors (F-017), product feel, cost.

| option | shape | for | against |
|---|---|---|---|
| **A. status quo** | adjacency = full 15/tick | cheap; passive comfort is cat-real; "stay" is technically learnable | instantaneous pricing → the learned behavior is drive-by adjacency, not companionship; nothing ever needs communication |
| **B. drip** | new dial, ~2–3/tick for a passive companion | flooring a real need takes ~20–30 ticks of *sustained* presence; dense per-tick RL gradient; cheapest real fix | another dial to price (hence the pilot below) |
| **C. tiered** | drip passive, full/bonus when **mutual** (both sleeping/resting adjacent, each by own choice) | manufactures a true coordination problem without conscripting anyone — **the payoff that gives the meow channel something to do** | two dials; mutual-rate attractors need checking |
| **D. mutual-only cliff** | no credit unless both engage | "honest" reciprocity | **rejected**: re-creates the coordination cost that killed the meow channel (scripted cats can't synchronize — that's *why* cosleep is 5.6%); demonstrator goes quiet; violates 021's spirit |
| **E. contact ramp** | warmth accrues over consecutive adjacent ticks | most realistic | per-pair contact clocks = engine state + snapshot schema growth; B approximates it at a fraction of the cost — **parked** |

Attractors and feedbacks to check, not assume:

- **Nap-pile catatonia** (F-017 lens): if mutual cosleep is strictly
  best, do four copies converge to a pile? Bounded — sleep services
  neither eat nor drink and the Nash-mean welfare punishes neglect —so
  the likely attractor is "pile except when hungry," i.e. cats. Measure
  it.
- **Partner-selection symmetry**: identical copies may all name the
  same popular companion. Harmless for cosleep (availability is
  non-exclusive); worth one look in the data.
- Every option moves `B` and re-prices the cuddle economy grooming
  competes in — F-016 says expect the feedback to surprise.

**Recommendation (not a decision): B + C with dedicated dials** — a
cosleep drip for the passive companion, the full rate reserved for
mutual engagement, plus the demonstrator routing change above. Fixes
the instantaneous-presence degeneracy, keeps 021's doctrine and the
passive-comfort realism, gives RL a dense gradient, and creates the
coordination payoff communication needs.

**Dial-pricing pilot (agreed 2026-08-08, pre-freeze, scripted-only).**
F-016's instrument: 10 seeds × 20k, paired across identical seeds,
served world. Sweep drip ∈ {1, 2, 3, 5, 15 = control} × mutual bonus
{off, on}, with the routing change held constant. Record: cosleep rate
and **mean contact duration**, mutual-vs-passive share, cuddle
time-above-threshold, welfare, and the water/grooming metrics (the
F-016 feedback check). This prices the dials; it does not certify
anything — policy-side effects are measured later, in policy company
(F-012), class-conditioned (F-015).

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
a clean win even where it helps (incidents 92/270 → 69/270; two
candidates worsen by worst distress, three by incident count — different
sets), and it is a registered condition, not a toggle (issue
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

- At **one** policy seat, **7/9** exp-003 candidates score
  `max_distress_age` 0 (the two exceptions, both mixed-arm, score 32 and
  194 — mild, not collapse; an earlier draft said 8/9, conflating this
  with H3's welfare count). The policies are individually fine; the
  *population* fails. The deployed winner is also the **only** candidate
  of nine at zero on shape-iii — stronger support for this specific
  deployment than the docs emphasized.
- Under `--sample`, `floor_touches` **108,584 → 0** and worst distress
  **16,027 → 1,020**. Four identical deterministic policies pick the same
  action, converge on the same tile and deadlock.
- **Mixed arms improve 26× under sampling; self-play arms get slightly
  worse** — self-play already trained under self-contention and learned
  to break symmetry behaviourally.
- **exp-002 replicates the mixing gradient out-of-sample**: median
  distress M0 **0.0** → M33 **6.0** → M67 **28.5**, zero-rate 67% → 44%
  → 17%.
- **Eat** leads the failing needs in every §9.2 probe, drink usually
  second — the contested consumables dominate the failure mode. (Not
  "always": one healthy candidate's second need is bath.)

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
- **F-015's re-verify trigger has fired and is unserviced**: its class
  amplitudes/densities were measured pre-026/027. exp-004's first
  twin-probe run re-measures class-conditioned credit (and re-derives
  F-004's world-count bar) before any probe-based claim.

---

## 5. Open decisions

- ~~Meow: cheaper how?~~ **Resolved 2026-08-08: ride-along** — the
  action becomes (activity, message), two heads, zero marginal cost;
  restraint moves to grounded legality + cooldown in the message mask
  (see §1, "Cost and spam"). A lower turn cost was rejected (still
  friction, still a dead channel) and so was a reward penalty (F-011).
- Meow: which rule — "another cat can change your outcome" (add
  `WantBath`) or "broadcast state" (messages for everything)? Current
  lean: `WantBath` is load-bearing either way; grounding makes the
  broadcast reading cheap to add later.
- Meow: is `WantSleep` in the batch? Routing alone fixes the scripted
  co-sleep deficit; the kind only aids policy-side coordination. Cheap
  while the wall is open, but not load-bearing.
- Meow: announce threshold + hysteresis values for grounded legality;
  cooldown = `recent_window_ticks` (10) or its own dial?
- Digest: add the per-kind intensity value while the schema is open?
- Cosleep credit: adopt B + C (drip + mutual tier, dedicated dials) or
  drip alone? Drip value and mutual rate come from the agreed
  dial-pricing pilot (§1), not from judgment.
- Shaping: coefficient by pilot, or a registered value with
  justification?
- Mixing: drop outright, or one arm to close it out?
- Sampling: run the 20-minute measurement, or leave greedy alone?
- §9.2: respecify now (it blocks certification) or fold into exp-004's
  prereg?
