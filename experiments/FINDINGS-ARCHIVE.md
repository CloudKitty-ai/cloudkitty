# Findings archive — superseded and refuted entries, full text

Moved verbatim from [FINDINGS.md](FINDINGS.md) (2026-08-08 restructure);
stubs there carry the one-line story, this file preserves the entries as
written so any past experiment's design can still be read against what
was believed at the time. Same `## F-NNN` headers — citations resolve
here unchanged. Entries arrive by supersession only; nothing here is
ever edited.

---

## F-001 · superseded by F-003 · Credit in CloudKitty is two-channel: fast self, slow teammate

*(Superseded 2026-07-27: the companionship retune — PR #60, cf82007 —
changed the happiness weights and social relief rates these numbers were
measured under. The two-channel structure survives; the quantities do not.
See F-003.)*

An action's effect on the actor's own happiness is front-loaded (~60% of
significant signal mass within 18 ticks — direct relief); its effect on
teammates has near-zero early mass (0.3% within 18 ticks) and lives in a
50–200-tick band peaking around k≈106 — contention and coordination
consequences propagating through others' welfare. The team reward inherits
the slow channel (90% of significant mass within 200 ticks; last
significant tick 380).

**Scope**: measured on `training.toml` (24×24, 5 kitties, heterogeneous
traits) under **`needs_driven` dynamics for every kitty**, substitution
ticks 100–1100, 1,000 samples. Not yet measured: trained-policy dynamics,
the default world's geometry, larger rosters.

**Evidence**: [exp-001 twin-probe result](exp-001-bc-mappo/results/twin-probe-2026-07-25.md)
(bit-reproducible; regeneration commands inside).

**Implications**: γ = 0.995 registered as exp-001's predicted sweep winner
(preserves 0.59 of the discounted team signal vs 0.38 at γ = 0.99, whose
horizon bisects the cooperative band); λ stays 0.95 (no GAE setting
bridges a 100-tick gap); cooperative credit is carried almost entirely by
the critic — critic explained-variance is the watch-first training
diagnostic, and the MAPPO privileged global state is empirically
motivated, not merely conventional.

**Would invalidate**: the teammate band failing to appear on other
geometries; or shifting below ~50 ticks under trained-policy dynamics
(coordinated cats may propagate consequences faster than scripted ones).

**Re-verify when**: the first policy artifact exceeds `needs_driven` on
the paired Nash aggregate (or passes SC-004 certification, whichever
comes first) — re-run the twin probe with that policy seated, in both
all-policy and mixed rosters, and compare the teammate band; supersede or
narrow this finding accordingly. Also due regardless: a default-world
geometry repeat and by-action-class conditioning (the 1k sample mix is
move-dominated).

---

## F-002 · refuted · Non-binding cuddle-route under-use is real but carries no material headroom

Resolved 2026-07-27 (was reserved for exp-001's prereg-named candidate).
The census (`cuddle-census`, engine-predicate classification, 5 seeds ×
20k ticks per config) splits the claim: the **mechanical under-use is
confirmed** — `needs_driven` takes `Sleep{with}`/`Groom{target}` in 0.7%
of moderate-need busy-only opportunities and never when a binding rest
duet is available — but the **headroom hypothesis is refuted**: post-
retune, high-need (≥80) opportunities beside friends occur ~1–2 per 100k
ticks on both the frozen and default worlds, because the heavier cuddle
weight makes the scripted cat service the need early. The 38 pre-retune
events described a world that no longer exists. Not a channel for beating
`needs_driven`; the prereg's interpretation rule (trained-policy Cuddle
pinned streaks beside busy friends = real skill gap) stands unchanged.

**Evidence**: [frozen-world addendum §2](exp-001-bc-mappo/results/frozen-world-addendum-2026-07-27.md).

**Re-verify when**: happiness weights or relief rates change again
(check `engine_defaults_sha256`), or a trained policy shows Cuddle
pinned streaks (then the routes' availability matters, not their
scripted-cat usage).

---

## F-003 · superseded by F-013 · The companionship retune tripled the credit horizon; channels unchanged

*(Superseded 2026-08-02: the 024 wet-fur batch — this finding's own
"any engine-defaults change" trigger — moved every quantity again,
exactly as the retune did to F-001. The two-channel structure
re-confirms on the post-024 engine (early self band reproduces in all
six re-verification runs); the band edges, peak locations, and
retention decimals below are pre-024 history. See F-013.)*

Supersedes F-001's quantities on the retuned baseline (PR #60, cf82007:
happiness weights eat/drink→0.20, cuddle/bath→0.15; groom/play relief→20,
cuddle→15). The two-channel structure holds — self credit front-loaded,
teammate credit slow — but every band moved out ~2–4×: the spillover band
is now ~230–430 ticks (peak k≈406, was ~50–200 peaking k≈106), the team
reward peaks at k≈230 with only 16% of significant mass within 200 ticks
(was 90%), and a diffuse-but-real tail (≈2.5× chance rate of significant
ticks) persists past k=1,000. Mechanism: slower social relief lengthens
scenes, so contention/coordination consequences propagate later and wider.
Decision-point density also fell 0.86→0.72 (more mid-scene ticks where an
idle substitution is rewritten back).

**Scope**: `training.toml` (24×24, 5 kitties, heterogeneous traits) on
post-retune compiled defaults (main 758ec28), `needs_driven` dynamics for
every kitty, substitution ticks 100–1100, 1,000 samples, 1,200-tick traces
(600 is now too short — the first pass truncated live signal at its edge).
Not yet measured: trained-policy dynamics, default-world geometry, larger
rosters, per-action-class structure.

**Evidence**: [exp-001 retuned twin-probe result](exp-001-bc-mappo/results/twin-probe-2026-07-27-retuned.md)
(bit-reproducible; commands inside).

**Implications**: discounted team-signal retention is now 0.10 at γ=0.99,
0.20 at γ=0.995, 0.45 at γ=0.998 — γ=0.99 ends before the cooperative band
*begins* and is empirically dead for the cooperative hypothesis;
recommendation to the owner is to amend exp-001's sweep to {0.995, 0.998}
(prereg amendment, owner's call). Cooperative-credit-is-critic-carried is
strengthened (even less signal inside any reachable GAE window); λ=0.95
and fragment 256 stand.

**Would invalidate**: another engine-defaults change touching happiness
weights, relief rates, or scene durations (check the suite's
`engine_defaults_sha256` stamp); the band failing to reproduce on other
geometries; trained-policy dynamics compressing propagation.

**Re-verify when**: any engine-defaults change (immediately — this finding
died once already that way, as F-001); or the first policy artifact
exceeding `needs_driven` / passing certification — policy-seated probe in
both roster modes, per F-001's original trigger. Still due regardless:
default-world repeat, by-action-class conditioning (mix is 72% move).

---

## F-005 · superseded by F-013 · Training-world knobs move detectable cooperative signal weakly; scarcity×tempo is the one replicated improver

*(Superseded 2026-08-02: on the post-024 engine the frozen
scarcity×tempo world's paired-seed signal halved and fell below the
false-positive floor — the mechanism reads as the chase sidestep
dissolving the stall-fed queueing consequences this world's gain was
made of. The knob search was honest for the engine it measured; that
engine is gone. See F-013.)*

Across 10 candidate worlds (scarcity, tempo, grid size, combinations)
measured under F-004 discipline, most knobs do nothing or hurt: shrinking
the grid raises chaotic mixing and drowns signal, tempo ×1.75 overshoots
(noise outruns signal — tempo has a sweet spot), scarcity alone is a
wash. The current environment's team-reward counterfactual signal beyond
the early self-mediated band (k ≤ ~14) sits at the false-positive
detection floor even at 3,000 samples / 300 worlds. The single
replicated improvement: **scarcity + tempo ×1.5** (water/chow 3–4,
sunbeams 2, rates ×1.5) — S(.998) 1.5–1.8× base in three disjoint world
batches, with dr and spillover bands co-occurring at k ≈ 730–940, the
signature of queueing/turn-taking consequences. Frozen as `training.toml`
2026-07-27; `needs_driven` holds 0.881–0.883 there (bounds pass,
0.10 above the 0.78 feasibility floor).

**Scope**: `needs_driven` dynamics, 5-kitty heterogeneous roster, the
knob ranges actually searched. Says nothing about trained-policy
dynamics, other rosters, or knobs not searched (durations, trait
spreads, roster size).

**Evidence**: [world-search result](exp-001-bc-mappo/results/world-search-2026-07-27.md).

**Implications**: exp-001 trains on the frozen scarcity×tempo world; the
searched-and-rejected table is the recorded H0a contingency (harden from
the measured Pareto set, don't invent). The near-floor absolute signal
sharpens the experiment's framing: single-action counterfactual reward
effects are marginal, so learnable cooperation, if it exists, is carried
by state-mediated credit (critic bootstrapping through visible
intermediate states) — critic EV remains the make-or-break diagnostic.

**Would invalidate**: engine-defaults changes (check
`engine_defaults_sha256`); a knob outside the searched ranges proving a
large improver; trained-policy dynamics changing the signal landscape.

**Re-verify when**: H0a is observed in exp-001 (re-run the search with
fresh budget before choosing the hardening step); or any engine-defaults
change (with F-003).

---

## F-006 · superseded by F-013 · The default world carries no detectable cooperative credit

*(Superseded 2026-08-02: both of this finding's own re-verify
conditions arrived at once — an engine-defaults change (024) and a
default-config change (the #86 24×24 cutover). On the current served
world the claim is inverted: a replicated cooperative band exists at
k ≈ 230–330. The 32×32 measurement below remains correct for the
world it measured. See F-013.)*

Measured 2026-07-27 (product thread, at the owner's request; verified
bit-exact by the experiments thread): on `cloudkitty.toml` (32×32, 4
kitties, element minimums 8, post-retune defaults), 1,000 samples over
150 disjoint worlds under F-004 statistics, the fast self channel
reproduces (contiguous k = 0–11 band) while **team-reward and spillover
significance sit below the false-positive floor** (13 and 10 ticks vs
~60 expected by chance). The teammate band F-003 measured on the
training world does not exist here — detectable team credit is ~7×
smaller than the frozen training world's and statistically absent.

**Scope**: `needs_driven` dynamics on the default world as configured at
post-retune defaults. **Confounded by design**: geometry, roster size,
and scarcity all differ from the training world at once; this finding
says the default world is signal-free, not which knob makes it so (the
scarcity-only deconfound at fixed geometry is cheap via family-gen and
unrun). Trained-policy dynamics unmeasured, as everywhere.

**Evidence**: [default-world twin-probe result](exp-001-bc-mappo/results/twin-probe-2026-07-27-default-world.md)
(regeneration verified bit-identical by a second session).

**Implications**:
- The training-world selection (F-005) was load-bearing and is now
  corroborated from outside its searched set: training on the default
  world would have optimized against a signal that is not measurably
  there.
- **Certification is a welfare gate, not a cooperation instrument.**
  *(Correction 2026-07-30: this bullet conflated two "default worlds".
  F-006's measurement is of `cloudkitty.toml` — correct and unchanged —
  but exp-001's certifications to that date had actually run on the
  compiled 3-kitty default, a different world; see deviation 31, which
  fixes §8's world to `cloudkitty.toml` and makes the point below
  apply as intended.)* Certification and the report protocol run on the default world, where
  single-action cooperative credit is undetectable — a policy's paired
  Nash gain there must come from policy-level behavioral differences
  compounding over the run, not from the marginal credit the probe
  measures. This sharpens H0c (transfer) risk for exp-001: cooperation
  learned in the contended gym must survive in a roomy world where
  coordination moments are rare. The design already carries the
  mitigations (default-world anneal, mixed-roster exam as the
  cooperation instrument); this finding is why they matter.
- F-003's "default-world repeat" follow-up is closed by this entry.

**Would invalidate**: signal appearing on the default world under
trained-policy dynamics (coordinated cats may *create* the contention
scripted cats avoid — that would narrow this to needs_driven dynamics);
default-config changes (check `engine_defaults_sha256`).

**Re-verify when**: the policy-seated probe runs (F-003's trigger) —
run it on BOTH worlds; and after any engine-defaults change.

---

## F-008 · superseded by F-010 (2026-07-30) · A long-horizon all-policy instability mode exists that short probes cannot detect; scripted teammates arrest it

> **Supersession note (2026-07-30)**: forensics
> ([collapse-forensics-2026-07-30.md](exp-001-bc-mappo/results/collapse-forensics-2026-07-30.md))
> identified the mechanism and found this entry's framing wrong on both
> counts. The mode is not long-horizon (collapse is visible *within*
> 2,000 ticks on the world that triggers it) and not a coordination
> instability (a single fragile policy collapses alone). It is
> **roster-OOD input fragility** — see F-010. The observations below
> were real; their interpretation was an artifact of certification
> accidentally running the compiled 3-kitty world (deviation 31) while
> probes ran `cloudkitty.toml`. Kept for the record.

In exp-001 Arm 2, 2 of 6 runs (γ=.998 s2, γ=.995 s3) carry seeds whose
all-policy rosters collapse (welfare 0.31–0.69) at 20,000-tick
evaluation while the same policies' 2,000-tick default-world probes read
a healthy ~0.94 — indistinguishable from the runs that certify positive.
The failure needs > 2k ticks to compound, and it never appears in Mixed
rosters (all six runs are Mixed-positive or Mixed-neutral): scripted
teammates arrest the spiral. Training-time diagnostics (§10.1 full set)
were uniformly healthy in the failing runs — this mode is currently
invisible until certification-length all-policy evaluation.

**Scope**: exp-001 Arm 2 policies on the default world, greedy seating.
Mechanism unknown (investigation deliberately parked); plausibly a
self-reinforcing coordination failure among five copies of the same
policy.

**Evidence**: [Arm 2 record](exp-001-bc-mappo/results/arm2-training-2026-07-30.md)
(probe-vs-certification divergence); per-seed tables in the report
protocol result.

**Implications**: **no deployment-soak or shipped-candidate decision may
rest on sub-certification-length or mixed-roster evidence alone** —
candidate selection requires the full 20k all-policy run. Trainer
validation probes at 2k ticks measure transfer, not stability. The
Mixed-roster immunity is a concrete lead for exp-002's
partner-population-curriculum item.

**Would invalidate**: the mechanism turning out to be an evaluation
artifact (e.g. a specific eval-seed interaction) rather than a policy
property — the parked investigation decides.

**Re-verify when**: the instability investigation runs; or any new
policy lineage (exp-002) reaches candidate stage — screen it with
full-length all-policy runs before any other claim.

---


## F-011 · superseded by F-018 (2026-08-16) · Design premise: meow restraint is a reward-structure equilibrium, not an engine guarantee (spec 023)

*(Superseded 2026-08-16: spec 028 removed the finding's central cost
mechanism — the ride-along head means a meow no longer costs a turn —
and reversed its "no engine rate limit" premise by moving the cooldown
into mask legality. The surviving half — meaning and restraint above
the legality floor are reward-structure equilibria, and per-seat
rewards void them — carries into F-018.)*

Spec 023 retired the engine-enforced meow cooldown ("manners, not
law"): learned agents face no rate limit on the channel. The spam
backstop is now *economics under the cooperative team reward* — a
meow costs a turn, misleading teammates lowers the shared objective,
and an always-on signal devalues its own contrast in the presence
digest. Evidence the equilibrium is real: s6 settled at ~0.1% meow
rate with functional listening on the receiving end, under no
compulsion beyond the (old) cooldown.

**Scope**: any training or serving configuration using CloudKitty's
cooperative team reward. The premise is the *reward structure*, not
the policy class.

**Evidence**: issue #84 (design record); spec 023;
[meow-listening probe](exp-001-bc-mappo/results/meow-listening-2026-07-31.md);
[s6 promotion record](exp-001-bc-mappo/results/s6-promotion-2026-07-30.md).

**Implications**:
- **Any per-kitty or competitive reward design voids the premise.**
  Revisit spec 023 before training under such a reward — a
  self-interested agent may find channel manipulation or saturation
  profitable, and the engine will not stop it.
- Scripted behaviors are not covered by the economics; their restraint
  is the behavior-level courtesy values (`[meow] courtesy_ticks`),
  which any new scripted behavior must also consult.

**Would invalidate**: a cooperative-reward policy learning sustained
channel saturation that survives training (would show the economic
argument insufficient even under shared reward).

**Re-verify when**: any reward-structure change; exp-002 candidate
screening (check channel-use rates alongside welfare).

---

## F-032 · superseded by F-033 · The most social policy pays a turn tax: `Idle` in `last_action` is the legality funnel refusing an ask, and it scales with how often a cat asks

Found 2026-08-25 by Experiments, from a client-side idle census Client
took for an unrelated reason (the owner noticed Biscuit yawning). Cites
[F-031](#f-031--active--a-partnered-scene-runs-its-minimum-only-if-the-counterpart-is-pinned-grooming-is-the-exception)
for the partnered-scene mechanics it rests on.

**`last_action` is not what the policy asked for.** `World` writes the
**enforced** action (`world.rs:338`, `last_action = Some(enforced)`,
guarded by `last_action_records_what_actually_happened`), and
`action::validate` — "the whole of Article IV's enforcement surface"
(`action.rs:340`) — maps *every* illegal proposal to `Action::Idle`.
So an `idle` on the served surface has two indistinguishable
preimages: a policy that proposed idle, and a policy whose proposal was
refused. Nothing outside the engine can tell them apart.

1. **Biscuit (e006a-L-04-s3) reads `idle` on 35 of 226 ticks (15%);
   every other seat reads 1–3%.** Served roster, ticks 354,335–354,560.

2. **It is not volume, it is a per-ending rate.** Idle lands on the
   tick *after* a play or chase block ends:

   | seat | play/chase endings | next tick is `idle` | idle ticks |
   |---|---|---|---|
   | **Biscuit** | 35 | **77%** | 35 |
   | Pumpkin | 18 | 6% | 6 |
   | Miso | 14 | 0% | 3 |
   | Kittybear | 14 | 0% | 3 |
   | Clementine | 12 | 0% | 4 |

   Pumpkin ends 18 scenes and idles after one. The difference is not
   that Biscuit finishes more scenes; it is what happens at the seam.

3. **The refused ask is overwhelmingly a duet.** 22 of the 35 idle
   ticks directly follow a *kitty*-target play. Duet legality is
   `world.is_conscriptable_friend(kitty_id, id)` (`action.rs:411`) —
   the partner must be **free**. The partner's own scene ending is
   sufficient to make a re-proposed duet illegal, and by F-031 duets
   run exactly their 2-tick minimum, so the seam arrives on a clock.

4. **Idle is a genuine do-nothing here, not a continuation.** `apply`
   intercepts an Idle proposal from a *clocked* kitty as a
   continuation (`action.rs:430`); these ticks are post-scene, so they
   reach the `Action::Idle => {}` arm and produce no state change.
   Biscuit's position is unchanged across all 35.

5. **Ruled out by measurement, not argument.** Target starvation: the
   distance to the nearest critter is identical during idle and chase
   (median 7.0, mean 6.6 both), and there were exactly 4 critters on
   the map at every tick of the window. Ambush: 11% of idle ticks have
   a critter within 3 tiles, against chase's 8%. Engine meows: Biscuit
   is the *quietest* seat (17.8/1k vs Pumpkin 94.7), and its only
   non-purr messages were `want_drink`×2 and `want_eat` — nothing
   play-related. Idle runs are 1–2 ticks, never longer (25×1, 5×2), and
   80% are followed immediately by chase or play.

**The claim**: a policy that proposes partnered play more often is
refused more often, and each refusal costs it a whole turn. The tax is
proportional to sociability, and it is invisible on the served surface
because the refusal is spelled the same as a choice.

**INFERENCE, explicitly flagged**: (1)–(5) are measured, but "refused"
is an inference from the pattern, because proposals are not observable
from outside the engine. The alternative — that the policy genuinely
proposes idle at 77% of its own scene endings and never elsewhere — is
consistent with the same data. **The settling experiment is cheap and
lab-side**: drive the seat through the joint-action seam, where the
proposal and the enforced action are both in hand, and count how often
`validate` rewrites Play/Chase to Idle. Do that before citing this
finding as a cause of anything.

**The open question it opens (untested)**: Biscuit carries the roster's
lowest happiness (90.95 live) and its certified character price is
0.76 under thermostat parity. If 15% of its turns produce no state
change while other seats lose 1–3%, part of that price may simply be
the cost of asking rather than anything about character. Not measured;
the lab replay above plus a needs-servicing count per turn would settle
it. **If it holds, there is headroom that costs no character**:
`Play { target: None }` is *always* legal ("pouncing at nothing is
always legal, like grooming oneself", `action.rs:407`), so a policy
that fell back to a solo pounce when a duet is refused would keep the
social ask and stop paying for it.

**Scope**: one 226-tick window, served world, this five-seat roster,
one character-trained seat. The rate is a function of how often the
seat proposes partnered play, so it should fall on any roster whose
cats are more often free, and it says nothing about scripted
compositions.

**What would invalidate it**: a seat with a high partnered-play rate
and a low post-ending idle rate (would break the proportionality); a
lab replay showing `validate` rarely rewrites this seat's actions
(would mean the idles are genuine proposals, and the turn tax is a
training artifact rather than an enforcement one); or the same idle
rate appearing on a seat whose scenes end just as often but are solo.

**Re-verify when**: any change to `is_conscriptable_friend`, the
`validate` legality arms, or duet duration config; and before pricing
partnered play in any EV or reward-shaping pass — an ask that gets
refused is not free, and current EVs price it as if it were.

**Addendum 2026-08-25 — the idle run length is also a RENDERING
parameter (Client, measured; carried here at their request).** Client
simulated the shipped animation scheduler against the same census
windows. The client is not drawing a yawn: of the yawns started on
Biscuit (~7.3/hour), **3.6% are fully drawn**, 64.9% reach the hold
phase and only 12.7% reach the close, median shown **485ms of 1420ms**.
The yawn is 340 open / 620 hold / 460 close, `stepRig` passes it
through rather than integrating it (`yawn: input.yawn || 0`), so the
mouth snaps shut with no ease when the pose leaves idle. A yawn needs
~1.77 ticks; this finding measured idle runs of 1–2 ticks (25×1, 5×2,
none longer). The drawn result is a half-second open-and-shut mouth —
which reads as a vocalisation, and the owner described it as "very
meow" before any of this was measured.

**Why an engine register carries a client number**: it makes the
current reading *fragile in a direction invisible from this side*.
Nothing in the client changes if a future policy idles in longer runs —
the close phase simply starts playing, and the same engine beat becomes
an actual sleepy yawn. **So "how long the seat idles" is a rendering
decision as well as a behavioural one**, and the coupling runs through
a threshold (~1.77 ticks) that no engine-side change would flag. Any
work that lengthens idle runs — including the `Play { target: None }`
solo-pounce fallback above, which would *shorten* them toward zero —
changes what a viewer sees, not only what the seat does.

**Status of that coupling (owner, 2026-08-25): intended to be
DISSOLVED, and this note exists so it does not outlive its truth.** The
coupling above is a property of the *currently shipped* client, where
the beat is driven by the idle pose. The plan is to extract the
animation, drive it independently, and slot it somewhere of its own
(random meows while walking is the leading candidate) — the client does
not need strict determinism, so it has that freedom. **Once that lands,
idle run length stops being a rendering parameter and this addendum
stops constraining engine work**: the ~1.77-tick threshold, and the
worry about `Play { target: None }` removing the beat, both become
moot. Until then it holds. The owner has also framed the client as a
side project rather than a gate on this register, so **no engine or
training decision should wait on it** — tell Client as a courtesy, do
not treat it as a dependency.
