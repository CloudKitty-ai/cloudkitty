# Needy set: mid-world grave onsets for the frozen probe (declaration 2026-10-28; DRAFT for the owner's ruling)

Owner's words. Kickoff, 2026-10-28, to two questions put together
(whether the P0 monitor's pass 1 waits, and whether this declaration
starts now): "Yes to both. We still have another phase of gen 2 left
even after we figure out the needs estimator as well."

What the set is for, each in the words that put it on the record:

- Decision 3 (deviations entry 13, `gen2-deviations.md:792-801`): the
  Phase 2 operating point is P(grave) ≥ 0.10 with a 2-tick burn-in,
  "provisional, re-read on the needy set (spec 067) before any Phase 2
  declaration fixes it". Her words when she ruled it, 2026-10-26: "We'll
  start with your recommendation (10/2) , then after we get the
  mid-episode testing, we can reevaluate and dial in on the optimal
  level."
- F-069's open question: whether the head sees a friend's slow crossing
  into grave after a long clean history. No set on disk holds one (no
  grave onset after a slice's hundredth tick in any evaluation set, 1d
  RESULTS §Addendum 3).
- Spec 067 SC-004 (merged 90429f0c): the minimum episode count per
  stratum, the worlds that buy it, and separate first-episode and
  later-episode reads are the consumer's to declare.
- The observer-stream ruling, 2026-10-27 (timeline, "OBSERVER STREAMS
  RULED"), her words: "B with all three amendments. One minor tweak:
  “without dropping below 0.995 below world start” seems overly
  restrictive. If we end up at e. g. 0.98 at world start and 0.95 mid
  world, that would clearly be an improvement." Its follow-ups bind this
  declaration: threshold-tuning seeds split from confirming seeds, and
  any training set collected separately, after a head's declaration is
  ruled.

Inputs: spec 067 (`specs/067-needy-preset/spec.md`); the Professor's
note `~/ai/professor/notes/for-experiments-midworld-onset-instrument-2026-10-25.md`,
sha256 3a5e3cc6614074dd75da597e874c30d4a9e9e858c120571411e12a070e12afae,
611 lines as read 2026-10-28 (it has moved since the 202cac6c read that
§Addendum 5 recorded; the change is the appended "P9 scored" section);
F-068, F-069, F-070; two read-only inventories run for this draft (their
reports are this thread's evidence, not results; every fact below that
rests on them carries its file:line).

**Status: DRAFT. Nothing collects and nothing is read before she rules
(§12). No number from this set exists.**

Welfare-cost line. Covered minds: the four frozen rot2 networks seated
beside the scripted friend in each covered world, and no others. No
weight changes anywhere in this arc. Expected exposure at the drafted
design: about 6.8M covered cat-ticks (arm N about 5.5M, arm T 0.8M, the
covered scout's paired worlds about 0.5M, the binding check 10,000),
capped at 8.0M (§7). Expected distress for the covered seats is near the
lived worlds' own: L held no grave tick for any friend in 1.0M covered
cat-ticks with 0 aborts (Phase 1 RESULTS.md:35-39, DECLARATION.md:296-300),
and on P distress stayed with the grave kitty in all 100 worlds (1b
RESULTS.md:48-54). The covered scout measures it in this composition,
against paired controls, before the set runs. The scripted friend is
exempt (README §Design discipline: scripted brains); its distress is the
instrument, reported and never gated. What the exposure buys: the
operating point the Phase 2 declaration fixes, whether the frozen probe
sees grave arrive after a long clean history on rows nobody stitched,
and whether it reads the cat's behaviour or the need law's consequences
(the transfer question for covered friends).

## 1. What is being asked

1. **Tie-back.** Does the frozen probe see a scripted friend's start-up
   grave as it sees a covered friend's (P's 0.995 at 0.10)? Both states
   are young, so a gap here is the scripted signature itself.
2. **History.** When grave arrives on natural rows after H clean ticks,
   how much does the probe detect, per history stratum, beside the
   splice's curve (F-069, F-070)?
3. **Anticipation.** Between the mask opening and the grave crossing,
   does the alarm rise early (the probe reads the cat stop servicing) or
   only at the crossing (it reads the need law's consequences)?
4. **The operating point.** Priced on mid-world onsets, which threshold
   and burn-in does she pick for Phase 2, and what do they buy on seeds
   the pick never saw?
5. **Price** (descriptive). What does living beside a friend who refuses
   help cost the four covered observers?

Scope: an instrument for the frozen probe. Nothing trains on this set;
its seeds are test-only. A needy training set, if she wants one, is a
later declaration on fresh seeds after a head's declaration is ruled,
and that head declaration carries F-070's transfer check with the
junction control beside it (the ruling's amendment 2 and Product's
2026-10-28 note, adopted).

## 2. Facts the design rests on

**The probe in force** (Phase 2 decisions 1, 2 and 4, two-stage on the
frozen Phase 1b head, NF, per-need probabilities; decision 3 above):
NF-h24 (`minifriend-phase1b-2026-10-23/results-raw/heads/NF-h24-s{1,2,3}/head-best.pt`,
7,807 parameters) plus the 25-parameter logistic grave read
(`minifriend-phase1d-2026-10-24/results-raw/probe/NF-h24-s{1,2,3}+p/probe.pt`),
three seeds. One shared head runs on every ordered (observer, friend)
pair: the observer's 109-cell self block plus that friend's 58-cell row,
its state zero at a world's start (`phase1_data.py:72-86`,
`train_heads.py:54-63`). GRAVE is the friend's true state: any hidden
need (eat, drink, sleep, play, cuddle) at or over 90, or happiness under
45; bath never enters a bin (`minifriend-phase1-2026-10-22/strata.py:6-8, 24-27`).

**The figures this set reads beside** (NF-h24+p at 0.10, seed mean ±
SD over the three probe seeds):

| condition | detected | source |
|---|---|---|
| P, covered friend grave at reset (200 episodes, B = 0) | 0.995 ± 0.009 | F-069; 1d RESULTS.md:1164 |
| splice after H = 1 / 2 / 5 / 10 / 20 / 50 clean ticks | 0.978 / 0.970 / 0.852 / 0.658 / 0.537 / 0.362 | F-070; 1d RESULTS.md:1391-1406 |
| splice after H = 100 | 0.358 ± 0.175 | F-069; 1d RESULTS.md:1409 |
| splice after H = 500 / 2,000 | 0.287 ± 0.143 / 0.288 ± 0.132 | F-069; 1d RESULTS.md:1173-1176 |

The splice's donors are P's 200 covered reset-grave episodes, 5 / 40 /
238 ticks long (min / median / max), 14 of them in sight at onset; the
junction control never fires from H = 2 on (1d RESULTS.md:1010-1012,
1391-1409). Training worlds hold no grave after offset 322 (F-069).

**The preset as landed** (spec 067; `crates/` unchanged since
90429f0c; below, `core/` is `crates/cloudkitty-core/src/` and `rl/` is
`crates/cloudkitty-rl/src/`). Defaults (`core/config/needy.rs:71-91`): mix [0.5, 0.2, 0.15,
0.15, 0, 0] over m = 1…6; release_level 90; hold_ticks 1,500; gap
{300, 1,200}; onset_levels [0, 2, 10, 50, 200, 20,000]; onset_weights
0.2 each; onset_draw flat (or log_uniform, one setting for every
level). An episode opens at the first tick at or past its onset;
`needy` releases when every masked need reaches release_level (checked
first) and either preset releases at onset + hold_ticks; the next onset
is the release plus a gap drawn flat (`core/needy.rs:276-300`).

**What a reader can see.**
- Ground truth per tick: `ParallelEnv.needy()` returns (id, masked
  needs, ordinal, phase), the phase resting, held, released_level or
  released_limit, the released values on the release tick only
  (`crates/cloudkitty-py/src/lib.rs:520-543`).
- The state is blanked from every other kitty's view and read by no
  encoder (`core/world.rs:1884-1892`).
- A refusal carries the reason `needy_masked` in the engine's refusal
  log (`core/world.rs:461-470`). The binding exposes no reason: Python
  sees only `survived == False` on a policy seat's refused proposal
  (`rl/episode.rs:584-593`). bc-collect's `--trace` carries the reason
  and the full needy state for all-scripted worlds
  (`experiments/tools/bc-collect/src/main.rs:387-403`).
- The engine safeguard (75; eat and drink) spawns food or water but
  changes no need and cannot override the mask
  (`core/spawn.rs:173-192`). A masked need is bounded only by the clamp
  at 100 and the release rules.

**The world.** `gen2-comparator-legs-2026-10-14/g2leg-20.toml` (sha256
64d77c8a…): 20×20, vision radius 4, five kitties, every config seat
`teacher` (the seating makes a seat a policy). Effective rise rates per
tick, read from the config and its per-kitty override rule
(`core/config/mod.rs:1771-1780`):

| kitty | eat | drink | sleep | play | cuddle | bath |
|---|---|---|---|---|---|---|
| Miso | .3 | .4 | .6 | .3 | .4 | .2 |
| Biscuit | .3 | .3 | .3 | .8 | .4 | .2 |
| Pumpkin | .6 | .4 | .2 | .4 | .4 | .1 |
| Kittybear | .4 | .3 | .3 | .3 | .4 | .4 |
| Clementine | .4 | .4 | .3 | .3 | .7 | .1 |

A masked need at rate r climbs from n to 90 in (90 − n)/r ticks: 113
ticks at r = 0.8 from 0, 450 at r = 0.2. **So from a default start,
grave arrives on the friend's row 100 to 450 ticks after the mask
opens**, and a mask opening at tick 5 does not put grave in front of a
5-tick-old state. The set therefore carries two anchors (§4), and the
history strata that pair with the splice are set on the crossing. The
scripted scout measures the climbs; the table is the expectation.

**Tooling as it stands** (`seating-analysis-g2-2026-10-21/seating_collect_g2.py`):
no seating puts a scripted seat beside rot2 networks (`cert_harness_fog.py:99-137`);
the F-053 abort watches every seat (`seating_collect_g2.py:56-64, 145-168`),
so a scripted friend held grave would stop its own world; no needy state
is recorded; the head readers assert every seat recorded observations
(`phase1_data.py:66`, `count_strata.py:63`). Both installed lab bindings
predate specs 066 and 067 and refuse a needy config (deviations entry 14
records the arc binding refusing the `[welfare_hazard]` key): a fresh
binding from main is required. The 399-cell observation carries four friend
rows, so **the scripted friend displaces one rot2 network: no world in
this set is the certified five-network composition.**

**Seeds.** `experiments/SEED-BANDS.md` is the single registry; claims
in the 1095xxx series end at 1095650 and nothing in `experiments/`
mentions 1095651–1099999 (grep, 2026-10-28).

## 3. The set

Two arms, five blocks each. In block k, kitty k is the scripted friend
and the other four seats keep their rot2 networks (Miso s2, Biscuit s4,
Pumpkin s6, Kittybear s7, Clementine s1). Greedy masked argmax, the
served clock, every covered seat's observation saved.

**Arm T, the tie-back.** P's own configs
(`minifriend-phase1b-2026-10-23/g2leg-20-P<k>.toml`, retrofitted per
deviations entry 14: kitty k starts every need in {60, 95},
`acknowledged = ["initial_needs"]`), with seat k scripted on its config
behaviour (`teacher`) in place of its network. P's 50 evaluation seeds,
10 per block (1b `split.json`), 4,000 ticks as P. Each world is paired
by seed with P's covered-friend world: the same generated world and the
same grave start, a different mind in the grave seat. A needy seat
decides as the teacher until its first onset (FR-006), so this is also
the needy friend's earliest history stratum. The reuse of P's seeds is
by design (precedent: the cert battery and Phase 1 L reuse g2cmp).

**Arm N, natural mid-world crossings.** `g2leg-20-N<k>.toml` =
g2leg-20.toml with kitty k on `needy`, `acknowledged = ["needy"]`, the
default start (every need 0, happiness 100), 6,000 ticks, and:

```toml
[needy]
mix = [0.5, 0.2, 0.15, 0.15, 0.0, 0.0]     # spec default
release_level = 90.0                       # spec default
hold_ticks = 1500                          # spec default
gap = { min = 300, max = 1200 }            # spec default
onset_levels = [0, 2, 10, 50, 200, 20000]  # spec default edges
onset_weights = [0.1, 0.1, 0.1, 0.1, 0.6]  # weighted to the late level
onset_draw = "log_uniform"
```

Why `needy` at 90: the episode releases on the tick its masked needs
reach the distress line, and the cat then services them, so grave lasts
as long as relief takes. That is a crossing with natural relief, the
shape of P's donor episodes. `needy_hold` holds grave to the limit and
answers a different consumer question, the probe's hold; it is not in
this set (§12 call 1).

Why these onset weights: every first onset under 200 lands its crossing
at roughly 100 to 650 ticks, so the spec's equal weights would pile four
fifths of first crossings into one history stratum. Weight on the late
level, drawn log-uniform, spreads them across the three late strata
(§4). Expected per-world shares at these settings, from the rates above:
H2 about 0.24, H3 about 0.35, H4 about 0.22, no first crossing before
6,000 about 0.17. The scout measures them. The probe is frozen and
cannot learn a clock, so the clock-free schedule FR-004 builds for
training sets is not needed here; a training set keeps it.

**Seeds** (claimed in `SEED-BANDS.md` in the commit that first burns
one): 1095651–1096650 for this arc.
- Scripted scout 1095651–1095700, 10 per block in block order.
- Covered scout 1095701–1095710, 2 per block in block order; each seed
  runs twice (§7).
- Arm N 1095711–1096010, 60 per block in block order (N1 1095711–1095770
  … N5 1095951–1096010); each block uses its first w seeds, w from the
  sizing rule (§7).
- 1096011–1096650 held for this arc (an extension under the sizing rule
  or a declared re-run), never a training set.

**The split.** Within each block, seeds in ascending order alternate
tuning, confirming, tuning, …, in both arms. `split.json` is committed
before any covered world runs.

## 4. Episodes, anchors and strata

- **Observer slices.** Every ordered pair (observer, friend) whose
  observer is one of the four covered seats; a slice runs the whole
  world. The scripted seat records no observation and is never an
  observer. 16 pairs per world, 4 with the scripted friend.
- **Grave episode** (R4d's definition, 1d DECLARATION.md:274-293): a
  maximal run of GRAVE on the friend's truth stream aligned to the
  observation (obs[t] with needs[t − 1]), counted once per observer.
- **The crossing** is the episode's first tick. **History H** is the
  crossing's offset from the slice's first tick, the quantity the
  splice's H measures.
- **The mask anchor** (arm N): the tick `needy()` first reports episode
  j as held. A grave episode of the scripted friend whose crossing falls
  between mask onset j and the tick after release j is episode j's
  crossing; one outside every mask window is "unmasked" and reported
  apart.
- **Primary strata, on H:** H0 [0, 2) (arm T's reset episodes); H2
  [100, 300); H3 [300, 1,250); H4 [1,250, 6,000). H2–H4 pair with the
  splice at H = 100 / 500 / 2,000, the nearest by midpoint. H1 [2, 100)
  is printed when arm N reaches it and is not sized; F-070's knee stays
  a splice result (§8).
- **Covariates, never pooled across without the weights printed:**
  ordinal (the primary reads use first episodes only; later episodes are
  their own table, R7); m (1–4); which need, play its own cell; in sight
  or under fog at the crossing (the friend's row present in the
  observer's view); which edge crossed (a need at 90, or happiness under
  45); release by level or limit.
- **Detection** (R4d): the alarm, P(grave) at or over the threshold
  after the burn-in, reaches threshold at any tick of the episode.
  Latency is the detection tick minus the crossing.
- **Anticipation** (the Professor's §Q4 (iv)): an alarm run that starts
  inside [mask onset, crossing) of the friend's episode is anticipation,
  never a false alarm. Lead is the crossing minus the first alarm tick
  at or after mask onset, positive before the crossing.
- **False alarms** (R4d's runs that touch no grave tick, anticipation
  runs excluded), per 10,000 observer-ticks, in three classes: the
  scripted friend before its first mask, the scripted friend between
  episodes, and covered friends. Runs starting at a slice's first tick
  are printed apart, as R4d did.
- **Burn-in B:** the alarm forced off for a slice's first B ticks (R6d).
- Every number is a seed mean ± SD over the three probe seeds, with its
  episode count beside it.

## 5. Reads

Each read is one fence with `--out` and `--md`. Nothing on a confirming
seed is read before her pick (§11 step 6).

- **R1 tie-back** (arm T, all 50 worlds): reset detection at 0.10, B = 0
  and B = 2, per block and pooled, beside P's same-seed covered figure.
  Scores P7.
- **R2 history** (arm N first episodes, all seeds): detection and median
  latency per primary stratum at 0.10, B = 0 and B = 2, beside the
  splice; the episode-length distribution beside the donors' 5 / 40 /
  238; in sight and under fog apart. Scores P10 with R1.
- **R3 anticipation** (arm N first episodes): the probe's logit aligned
  to the crossing from mask onset; fraction anticipated; lead
  distribution; per stratum, per m, per need. Scores P6.
- **R4 the ladder** (tuning seeds only): thresholds {0.05, 0.10, 0.20,
  0.30, 0.50} × burn-ins {0, 2, 5, 10}; per cell, detection and latency
  per primary stratum (H0 from arm T, H2–H4 from arm N), anticipation,
  and false alarms per class. No rule. The pick is hers, with its price
  printed (her "dial in on the optimal level").
- **R5 confirm** (confirming seeds only, after her pick): the picked
  cell, the same columns. These are the numbers the Phase 2 declaration
  cites; the tuning numbers sit beside them and are never cited for the
  pick. A stratum whose confirming value falls outside its tuning value
  ± 2 world-bootstrap SE is flagged, not failed.
- **R6 which need** (descriptive): on the scripted friend's grave
  samples in sight, how often NF-h24's means name the masked need (R3d's
  read), per need. Input to decision 4's per-need output; no per-need
  probability exists yet to read.
- **R7 later episodes** (descriptive): ordinal 2 and up, by the gap
  since the last release, never pooled with first episodes.
- **R8 price** (descriptive): the covered seats' happiness, distress
  ticks and worst streak per seat, in the covered scout against the
  paired controls and across the set; refused proposals toward the
  scripted friend (`survived == False`, attributed to the mask by
  target and timing; the reason itself is not readable through the
  binding).

## 6. Registered predictions

The Professor's, verbatim from the note at the sha256 above (lines
319-324, 536-542), scored in RESULTS beside the originals. All three sit
at a registered operating point, so they are scored on all seeds, after
R5.

- **P6 (anticipation).** "In single-need episodes in sight, the probe
  logit at 0.10 crosses threshold before the grave crossing in a
  majority of episodes, with a median lead of at least 20 ticks."
  Operationalised: arm N first episodes with m = 1, the masked need a
  hidden need, the friend in the observer's sight at the crossing; an
  alarm at 0.10 (B = 0) starting inside [mask onset, crossing); a
  majority is over 0.5 of eligible episodes on the seed mean; the median
  lead is taken over all eligible episodes, one never alarmed in the
  window counting as the lowest value. Both clauses must hold. Beside
  it, per stratum: his expectation of 2026-10-26 (lines 510-512) is that
  P6 holds "in the early stratum and fail[s] in the late ones".
- **P7 (tie-back).** "The scripted friend's start-up grave detection
  within the first 100 ticks at 0.10 is within the seed SD of P's
  covered figure (0.995)." Operationalised: arm T's reset episodes
  (crossing at a slice's first tick), detected at 0.10, B = 0, at a tick
  inside both the episode and the first 100; seed mean within P's seed
  SD (0.009) of 0.995, that is at least 0.986. R4d's anywhere-in-episode
  figure is printed beside.
- **P10 (natural-rows replication).** "For the scripted needy friend at
  0.10 on the frozen NF-h24+p, detection in the earliest history stratum
  is within one seed SD of P's 0.995, and detection in every stratum
  with onset after tick 100 is within one seed SD of the splice's figure
  at the nearest H (0.358 at 100; 0.287 / 0.288 at 500 / 2,000). If P10
  holds, F-069 is a property of the head, not of the splice."
  Operationalised: the earliest stratum is H0, so clause 1 is P7's read
  with R4d's anywhere-in-episode detection; "onset" in clause 2 is the
  crossing, the anchor the splice's H measures; H2, H3 and H4 each sit
  within the comparator's seed SD (0.175, 0.143, 0.132) of 0.358, 0.287
  and 0.288, at 0.10 and B = 0. Both clauses must hold. The mask-anchored
  version is printed beside it.

His reading of P6 and P7 together (lines 326-329): "If P6 holds and P7
holds, the scripted set is a usable proxy for a covered friend's
crossing with the behaviour-vs-consequence question answered in the
direction that transfers. If P7 fails, the signature gap is real and the
set licenses only the physics-consequence half."

## 7. Welfare and stops

**Scouts first** (README §Design discipline, item 2: a scripted scout
leg on any config no covered mind has run, its number cited).

- **Scripted scout.** Arm N's configs through bc-collect `--trace`,
  every seat scripted (seat k on `needy`, the others `teacher`), 10
  worlds per block, 6,000 ticks, 0 covered cat-ticks. Read: climb ticks
  per need and seat; the crossing H distribution and per-world stratum
  shares; episodes per world; release by level or limit; the scripted
  friend's distress streaks (reported, never gated); refusals by reason.
  Committed with the sizing below before any covered world runs.
- **Sizing rule** (applied to the scout, mechanically). Arm N's w per
  block is the smallest even number with 5w × (the smallest scout share
  among H2, H3, H4) ≥ 50 first-episode friend-episodes, that is 200
  observer-episodes, the family's floor pooled over the halves. At the
  expected shares w is 46 (230 worlds).
- **Covered scout.** Arm T's first world per block (counted in the set
  if clean), and the two covered-scout seeds per block, each run twice:
  once with seat k on `needy`, once on `teacher`. SC-002 makes each pair
  the same world until the first onset. 6,000 ticks, the S1 stop armed.

**Stops**, declared before launch, asymmetric (README item 1: harm and
futility, never early success):

- **S1, harm, hard.** F-053's 1,000-tick single-need streak on any
  **covered** seat aborts that world, and any abort stops the set and
  goes to her with options. The scripted friend is exempt; its streaks
  are recorded and never a stop. A `needy` friend crosses 90 on its
  release tick by construction, and with m ≥ 2 its first masked need can
  sit at 90 while the slowest climbs, so a roster-wide line would stop
  the instrument for doing its job.
- **S2, harm, the covered scout.** The set does not launch if the
  covered seats' pooled mean happiness in the scout's `needy` worlds is
  more than 1.0 point under their paired `teacher` worlds (for scale,
  every one-seat swap of rot2 sat within 0.3, pooled −0.083 ± 0.138 per
  world; battery RESULTS §"Swaps digest"), or on any covered abort. A
  miss goes to her with the read.
- **S3, futility.** A primary stratum with a scout share of 0, or w over
  60 (a share under 1/6), or a total over 8.0M covered cat-ticks, goes
  back to her before any covered world beyond the scout.

## 8. Blind spots (declared)

1. A scripted friend, not a covered one. The tie-back measures the
   signature gap on young states only; on late states the set separates
   signature from history only through R3, so a result on arm N
   transfers to covered friends as far as P7 and R3 carry it.
2. Four networks, not five: each block drops one certified network, and
   F-043 says a roster's tails belong to the roster.
3. Episode lengths: a `needy` grave run lasts as long as relief takes;
   R2 prints its lengths beside the donors' and reads detection anywhere
   in the episode, as the splice did.
4. One size (20×20), the default start in arm N, so crossings at H 2–100
   are not built and F-070's knee is not replicated on natural rows.
5. Two grave edges: a multi-need mask can cross happiness 45 before any
   need reaches 90; R2 prints which edge crossed.
6. No refusal reason through the binding: a covered seat's refused
   proposal is attributed to the mask by target and timing (the scripted
   scout reads reasons directly).
7. `needy_hold` not run: sustained grave and the probe's hold are
   unmeasured.
8. A bath-only mask makes no grave crossing (bath never enters a
   stratum); those episodes count only toward false alarms.
9. Test-only seeds: nothing here says what a head trained on late grave
   would do.

## 9. Doctrine check (against `experiments/DESIGN-DOCTRINE.md`)

- **Rule 12** (relief always available) moved a choice: the mask governs
  a scripted seat's own servicing, and the world's supply, the
  safeguard and every covered seat's relief are untouched (FR-013).
- **Rule 5** (a teacher acts only on what the student can see),
  checked: no demonstration row from any seat of a needy world
  (bc-collect bdc0022b); RL learning steps refuse a needy world (§10
  n7); this set trains nothing.
- **Rule 6** (the free register is never scripted), checked, moved
  nothing: law-named words only (FR-007).
- **Rule 9** (frozen pins), checked: the fresh binding reproduces a
  certified L world before use (n3); arm T runs P's configs as
  committed.
- **Rule 10** (two-layer gates) moved a choice: the covered stops (S1,
  S2) are this set's hard layer; the instrument's reads carry no bars
  beyond the registered predictions and the confirm flag.
- **Rule 11** (invalidation clauses), checked: any FINDINGS entry from
  this set names its domain (the frozen NF-h24+p; 20×20; rot2 less one
  network plus a scripted friend; `needy` at 90).
- **Rule 8**, checked: a coverage design read per stratum (spec 067
  SC-004). **Rules 1–4 and 7**, checked, moved nothing: no reward, price,
  rider or behaviour built for the served world.

## 10. Instrument and guards (built after her ruling; each red before trust, `scripts/mutate.sh --expect`)

- **n1, covered-only abort.** A collector option watching the policy
  seats only (today's single-seat `abort_seat` generalised); without it,
  the roster-wide rule is unchanged. Red: with the option mutated to
  count every seat, a short `needy` fixture under a lowered line aborts
  and the test fails. Must pass: a covered seat at the line still
  aborts.
- **n2, needy state recorded.** Per tick the scripted friend's mask,
  ordinal and phase from `needy()`. Red: a one-tick shift breaks the
  property checks (masked needs never fall while held; every
  released_level tick has each masked need at 90 or over; every onset
  is the previous release plus a gap inside {300, 1,200}).
- **n3, the binding reproduces the certified engine.** The fresh
  binding runs rot2 on L seed 905001 for 2,000 ticks; every array
  equals the first 2,000 ticks of Phase 1's recorded stream. Red: the
  check pointed at another seed's stream.
- **n4, observers.** The reader pairs covered observers only. Red: the
  scripted seat admitted as an observer trips the recorded-observation
  assertion.
- **n5, anchors.** On the scripted scout's real payloads: every masked
  crossing lies inside its mask window and no anticipation run lies
  outside one. Red: the window shifted by one tick.
- **n6, the split.** R4 refuses a confirming seed and R5 a tuning seed,
  both from `split.json`. Red: one seed's half flipped.
- **n7, RL learning steps** (the observer-stream ruling's follow-up):
  `train_ppo_g2.py` refuses an update on a batch from a world with a
  needy seat; `train_clone_g2.py` and `train_critic_g2.py` refuse any
  bc-collect rollout whose `meta.json` names a seat in
  `teachers_refused`. Estimate-only heads (`train_heads.py`,
  `sd_head.py`, `grave_probe.py`) stay open under their own
  declarations, per the ruling. Reds: each check removed lets a
  needy-world fixture reach its optimizer step. Must pass: frozen
  rollouts beside a needy seat still run (n1's fixture).
- **n8, the probe reproduces.** In the fresh venv, P(grave) on group
  P's first evaluation world equals the committed file to 0.0 for every
  probe seed (the 1d re-run precedent). Red: the wrong probe seed's
  file.

## 11. Run order (each step its own commit before its data)

1. This declaration, ruled by her (edits on her word only; a ruled
   version replaces "DRAFT" in the title with "RULED <date>").
2. Prerequisites: the SEED-BANDS claim; arm N's configs and their make
   script; `split.json`; the fresh venv with `BINDING.md` and n3; n7;
   the collector options n1–n2; the reader with n4, n6 and n8. Reds on
   record.
3. Scripted scout, its read, n5's red on its payloads, the sizing rule
   applied, arm N's w and the welfare-cost line's numbers committed. S3
   checked.
4. Covered scout; S2 read; a miss goes to her.
5. The set: arm T and arm N, both halves, S1 armed throughout.
6. R4 on the tuning seeds, to her for the pick; her words recorded.
7. R5, R1–R3 with the three predictions, R6–R8. RESULTS gated (a fresh
   subagent per round) and stamped; a FINDINGS entry only on a result
   that stands on its own; scores to the Professor; the read to Product
   as information.

## 12. Owner calls (rule on these with the declaration)

1. **Arms and preset.** Arm T (the tie-back on P's seeds) and arm N
   (`needy` releasing at 90: crossings with natural relief), with
   `needy_hold` left out of this set. Recommendation: as drafted.
   **RULED 2026-10-28: "Call 1 as recommended"** (after the in-depth
   walkthrough: T pins the scripted signature at H0 and supplies S2's
   paired controls; `needy` at 90 keeps the episode shape of P's donors,
   on which the comparator figures were read; `needy_hold` answers the
   hold question, breaks the any-tick detection scale, and is the
   heavier welfare mode, so it is a later declaration of its own).
2. **The anchor.** History measured at the grave crossing (what the
   splice's H measures), the mask opening kept as the second anchor for
   anticipation, P10's "onset" read as the crossing, and arm N's onset
   weights moved to the late level so crossings fill the late strata.
   Recommendation: yes. **RULED 2026-10-28: "Call 2 as put + arm E"**
   (after the in-depth walkthrough: the crossing is what the splice's H
   measures, so the comparator pairs on it; the mask opening stays as
   the anticipation anchor; her "+ arm E" answered the question put with
   it, whether to draft an early-crossing arm built from an elevated
   start under `needy`, which call 7 below carries for its own ruling).
3. **Which seat.** The scripted friend rotates through all five seats
   (five blocks, P's precedent, each dropping that seat's network), or
   one fixed seat. Recommendation: rotate.
4. **Size and cost.** Arm N at 6,000 ticks with w from the scout's
   sizing rule (expected 230 worlds, about 5.5M covered cat-ticks), arm
   T 50 worlds (0.8M), the covered scout about 0.5M, the total capped
   at 8.0M. The cheaper alternative stops each arm N world 300 ticks
   after its first episode ends: about 2.1M for arm N instead of 5.5M,
   first episodes only, no re-entry read. Recommendation: full length.
5. **Stops.** S1 on the covered seats only (the scripted friend exempt,
   its distress reported), S2's 1.0-point harm line on the covered
   scout, S3's futility caps. Recommendation: yes.
6. **The split and the pick.** Tuning and confirming seeds alternate
   within each block; R4's grid reads tuning seeds only; she picks; R5
   on the confirming seeds supplies the numbers the Phase 2 declaration
   cites; the predictions wait until after the pick so the confirming
   seeds stay unread until then. Recommendation: yes.
