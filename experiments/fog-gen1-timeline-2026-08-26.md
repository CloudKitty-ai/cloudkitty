# Fog Gen 1: sequencing timeline + shakeout criteria
## (2026-08-26, Experiments + owner, hashed out live. Owner-ruled sequence.)

Goal: land every compatibility-breaking change before the schema locks,
then train the next certifiable generation (5 seats incl. Biscuit 3.0)
against a stable target. Fog Gen 1 scope is ROADMAP @ a6eb3c8: radius
vision only, needs stay visible, 20×20, registers grounded reference
only.

## Step 0 — now, in parallel (no gates)

- **Cuddle sibling spec** — Product, in flight (handoff =
  `cuddle-economy-handoff-2026-08-26.md` @ f4b3708 + three spec notes:
  share the mutual predicate à la `action.rs:829-834`; state whether the
  legality mask feeds observations; one legality funnel with the tabled
  waterline rule).
- **Clustering baseline — DONE.** `attn-cert-2026-08-14/nn_distance.py`
  (+ guard): NN Chebyshev median 1.0 / mean ~1.9 / p90 4–5 / contact
  share 0.66–0.67. Banked (ticks 145,857–148,134) and live (547,416–
  547,657) agree.
- **Needs-servicing latency instrument — DONE.**
  `attn-cert-2026-08-14/need_latency.py` (+ guard); baseline banked at
  `need-latency-baseline-2026-08-26.md` (ticks 552,654–553,376). The
  pre-declared Biscuit 3.0 question is ANSWERED on this window: the
  welfare gap is eat/drink/sleep standing demand (+4.2 of the +4.8 pts
  vs Miso; eat armed-latency p50 31 ticks), and play-while-hungry is
  caught in the relief stamps — consistent with F-033's spare-cycles
  theory (owner's framing). Design levers with headroom: acceptance
  prediction + food-over-play prioritization; solo-pounce redirects
  reclaimed turns into more play, no payoff shown. Re-run (one 12-min
  window so far) before the step-7 design call.

## Step 1 — roll out non-fog changes

Cuddle sibling package, in PR-sized steps: dial split at 8.0/8.0
(byte-identical, spec-028 pattern) → reprice → engine sibling
(legality + tiers). Re-baseline BEFORE deploy (house rule; bugs-2.0
precedent). Owner's word to deploy; G6-style soak after.

**Pre-declared**: zero live rest scenes is EXPECTED — the served roster
is all-policy and every incumbent trained under saturated riders. Do
not read that zero as failure (F-029's lesson). Product verified
(2026-08-26): the legality mask does NOT feed observations — obs
distributions are unchanged for incumbents. The residual soak risk is
narrower: a newly-legal `rest_kitty` entry at select time exposes
logits the incumbents never trained under a live mask bit, so a frozen
policy could occasionally select rest on untrained weight. Watch
welfare + watchdog, not rest counts; a few odd incumbent rest scenes
are the expected signature of this mechanism, not a defect.

**SOAK CALLED 2026-09-01 (owner, early — "in the interest of moving
along to models more robust in the updated world").** Span: bump
deploy (PR #332) to the closing spot check at tick 1,193,578
(`attn-cert-2026-08-14/results-raw/soak-spot-1193578.json`): alarm
never live, `/welfare` entries empty at close, five seats happiness
89.3–94.8, worst need Kittybear bath 25.8. One blemish on the record:
the Miso one-sided-cosleep stall (~ticks 1,153,885–1,154,404, cuddle
100, distress age peaked 131 of 150, self-resolved, no alarm; raw
`miso-stall-1788266378.jsonl`) — the only watchdog entries of the
soak. Step 1 closes; the refusal-stamp fast-follow and the Biscuit
3.0 comfort sweep are unblocked.

## Step 2 — pre-fog validation (lab, fast)

- **Primary: scripted needs-driven lab worlds** vs the needflow model's
  predicted bands (`cuddle-economy-model/RESULTS.md`) — **DONE
  2026-09-01 (`needflow-lab-validation-2026-09-01/RESULTS.md`, F-036)**.
  Emit gates pass with room: rest 29.7/1k, the largest scene class,
  both tiers emitting in every seed and sub-window; play corridor flat
  under the bump (Δ 0.2/1k); groom mix retained. The "cosleep ~6:1"
  expectation was the model's number and does not hold: measured
  0.32:1, because engine cosleep routing is gated on
  `cuddle_real_threshold` 15 and the 041 rest economy holds cuddle
  near 14 (owner design question, not blocking). needflow is NOT a
  proxy for the scripted chooser (three engine gates it lacks); step
  5's bands are the MEASURED canon table, not the model's.
- Secondary: MLP fast-training smoke. Weak negatives (learners barely
  discovered hunting under a correct economy) — confirmatory only.
  **SKIPPED for this round (owner ruled 2026-09-01)**; step 2's
  remaining measurement is the Addendum 2 consent gate run.
- `tail-benchmarks/family-11-r5` against the collapse-detector v0 —
  **DONE 2026-09-01 (`collapse-detector-v0/RESULTS.md`, F-037)**:
  VALIDATED on the pinned labels (3/3 MUST-FIRE, 11/11 MUST-SILENT,
  the directed-travel negative held where the watchdog fires). Two
  corrections to the ROADMAP design: it fires 48–147 ticks AFTER the
  watchdog on every recorded lock (a namer, not an early warning), and
  the healthy margin on signal (a) is 0.07 (peak 0.43 vs bar 0.50), so
  H4's pin does not inherit ">50%" unexamined.
- **Here-word density screen** — **Half A DONE 2026-08-31 (F-034,
  `here-word-screen/RESULTS.md`)**: vocabulary cliff between 5.6% and
  8.2% corpus share; `announce_here = 1` is the fog collection
  parameter; act@1 and welfare untouched. Collection complete, so the
  contagion flip is unblocked from the screen side.
- **Water's-edge avoidance smoke** — **RUN + COMPLETE 2026-09-01
  (F-035, `edge-avoidance-smoke-2026-09-01/RESULTS.md`)**: positive
  control fires (vs the addendum's drift-matched blind arm — the
  charge is a MAGNET when unseen, blind arms drift toward the edge);
  option_a vs bidirectional = 0.41 pp under the aware ladder, play
  reciprocity prediction held. **Owner ruled on this data 2026-09-01:
  no contagion for Gen 1** (`contagion-shelved-2026-09-01.md`) — the
  magnet finding is the argument: Gen 1 cannot see a wet neighbour, so
  an armed charge trains arm B's world. F-035 is Gen 2 pricing input.
- **Biscuit 3.0 comfort sweep** (`biscuit3-design-note-2026-08-26.md`)
  — **DONE 2026-09-01 (F-038,
  `biscuit3-comfort-sweep-2026-09-01/RESULTS.md`)**: 20/20 runs valid.
  Comfort buys food linearly (eat time>30 0.455 → 0.132 at 55 → 30) and
  pays in element play only (duets hold 55–30). Weights arm WITHDRAWN
  on the owner's all-needs question: w35 passed P3 by leaving cuddle,
  her highest need, at 0.42 ≥30 (c35: 0.26). Spec-042 candidate dials
  NOT shippable (`t_partner 5.0` cuts Biscuit's duets 72.6 → 8.9/1k,
  roster duets −51–57%); offline pricing shows `t_self 5.0` is the
  larger cut (her own play need clears it in 46% of free moments).
  Decision rule: middle case, **owner call on the curve**; owner leans
  c30 (0.70x play accepted). **Addendum 1 (c25/c20) DONE 2026-09-01**:
  both reach roster-parity welfare on all five needs, play 0.58x /
  0.45x, duets start falling below 30, roster duets 0.88x / 0.85x,
  hungry meows fall to the roster's rate at c25; by the addendum's rule
  **c30 stands**, c25 is the next point on the curve. **Addendum 1b
  (c32/c28) DONE 2026-09-01**: the bracket fails on opposite sides (c32
  misses parity +0.07–0.09 at 0.76x; c28 passes +0.02–0.03 at 0.65x),
  curve monotone, duets hold 63–67/1k to 28; c30 confirmed under the
  rule. Two prereg measures failed as bars (excursions/1k counts meals
  that started above 30 and RISES as the eating level falls toward 30,
  turning over only below it: 8.2 → 3.15 → 2.02; low-need play is
  compositional). Score: play REJECTION is not a target (refusal reads
  only the partner's activity clock, `world.rs:1256`; the friend's need
  state moves availability by ~8 pp across its whole range against a
  37% base hazard per 12 ticks; the tax is Biscuit's alone, 4.7% of her
  ticks). The score's job is reframed as CONSENT (share of duets that
  conscript a friend with a need ≥30: 0.29 at c55, 0.19 at c30, 0.16 at
  c25), with roster duet supply and all-five-needs parity as bars; the
  owner's delta form is the right shape with slack; multiplicative
  delay HELD (it is a rejection lever). Addendum 2 = small consent-dial
  sweep, pending owner.

The validated step-2 mix bands become step 5's reference.

## Step 3 — the pre-fog schema-break bundle (owner decisions)

A short doc listing in/out. Known members: the waterline (**ruled
2026-09-01: contagion OUT for Gen 1**, superseding the 2026-08-30 IN
ruling — 044/045 stay in tree inert, no flip deploy; reasons and
reopen triggers in `contagion-shelved-2026-09-01.md`. The
neighbour-in-water float still waits for the wall, ruled jointly with
the scene-age float, and is reopen trigger 1), the KITTY_SLOT gap
("wants the wall"), anything else wanting a schema break. Nothing
enters step 4's spec without appearing here first.

## Step 3.5 — tag v2.10 (owner-ruled 2026-08-30)

The last stable 2.x, capping the pre-wall deploy train: 041 deploy +
soak → refusal-stamp fast-follow → `announce_here` knob → **tag**
(contagion flip deploy + soak removed from the train by the 2026-09-01
shelving; `announce_here` merged 2026-08-31). Prereq per house practice: expand
`## Unreleased` first — joint pass at tag time (owner + Experiments),
completeness-checked against `git log v2.9..` (toolchain pin #305,
Biscuit 2.0 cutover, the client run #300+, 041, 042, plus whatever the
train adds). Fog work on the far side is 3.0-numbered.

## Step 4 — implement Fog Gen 1

Spec-first (speckit). Scope per ROADMAP; free register never scripted;
here_* words are about the WORLD, want_* about speaker state.

**Bidirectional-contagion decision point — CLOSED 2026-09-01.** The
data came in (F-035: positive control fired, |option_a −
bidirectional| = 0.41 pp at factor 1.0 under the charge-aware ladder)
and the owner ruled contagion OUT for Gen 1 on it
(`contagion-shelved-2026-09-01.md`), so no membership call is needed.
The post-flip `waterline_exposure.py` sanity pass is dropped; the
pre-flip baseline (2026-08-31: on-water 3.02%, cross-adjacency 6.20%)
stays banked as a reference. The step-5 edge-behavior watch item is
dropped with it. Both rules remain pre-priced welfare-benign at both
economies for Gen 2.

Also specced in this window: the **Here*-teacher** scripted behavior
(Product; parked since 2026-08-17, doctrine in the comms brainstorm
addendum + ROADMAP bootstrap paragraph) — law-named words only,
grounded-predicate emission, courtesy dials per F-023. A
demonstration-corpus contributor (teacher seat in collection
compositions), never servable on the box; no schema break, so it
enters here, not step 3. **F-034 (2026-08-31) supports collapsing
this item**: the scripted behaviors with `announce_here = 1` produce
a corpus a V4 clone learns the register from — scoping it away is
the owner's call at this window.

## Step 5 — shakeout training round

Deliberately small: fewer seeds, shorter horizon. Purpose = discover
remaining schema/engine changes, not certify. Criteria PRE-DECLARED
below; anything not on the HALT list is step-6 data, not a stop.

Teacher rows enter the corpora here and in step 7; delivery is the
ROADMAP's registered three-arm comparison — mixed-corpus vs vocabulary
lesson (head-selective message-head finetune) vs no-seeding control.

**BC recipe (owner-ruled 2026-08-31, from F-034's extension)**: stop
rule = train-to-plateau on val loss with patience ~10 (patience 3
provably censors; the 20-epoch cap left ~+2 act@1 on the table), NO
epoch floor for the vocabulary — the message head converges by ~epoch
10 at period-1 density and no budget rescues wrong density. The
vocabulary is gated by MEASUREMENT instead: every clone must clear a
here-conditioned acceptance bar (opportunity-use + msg@1 on
here-rows, held-out set; `here-word-screen/readout_screen.py` is the
instrument) before advancing. A miss points at density or schema,
never epochs. Exact bar numbers pinned at the prereg alongside the
schema-4→fog caveat: message-head convergence speed under the new
digest matrix + self-row is extrapolated, not yet measured.

### HALT (egregious — stop, fix, possibly break schema)

| # | trigger | threshold | baseline / instrument |
|---|---|---|---|
| H1 | watchdog alarm | any | spec-040 box log (absolute, fog-independent) |
| H2 | worst-seat welfare below the scripted anchor on the SAME fog config, sustained | anchor re-derived on fog config | scripted anchors = house cert practice; per-seat because Nash p=0 punishes one sacrificed cat |
| H3 | hard-zero intended activity | 0 over an emit-proven window | F-029 rule; census + F-031 spans |
| H4 | single-activity domination | one partnered activity **>55%** (owner pinned 2026-09-01, v0.2) of a seat's REALIZED ticks over a trailing 200, sustained 200 | detector v0.2 VALIDATED on family-11-r5 (`collapse-detector-v0/RESULTS.md` §v0.2): 4/4 locks fire (0.82–0.83), 11/11 healthy silent (peak 0.43), margin 0.12; 0.65 was tried first and dropped the ramping ~500-tick twins lock (silent at any bar ≥0.60), so revisit only on a new collapse class; fires 66–122 ticks after H1 on a starving lock, so it names the cause rather than leading the alarm |
| H5 | frozen cluster | same-pair contact share near-total, sustained | F-027's spatial signature; `nn_distance.py` + pair census |
| H6 | hyper-dispersion | NN cheb MEDIAN ≥ 5, sustained | baseline median 1.0 — 5× current; loose deliberately (fog legitimately disperses) |

### INVESTIGATE (log, continue; input to step 6)

- activity mix outside step-2 bands by modest factors (bands =
  `needflow-lab-validation-2026-09-01/RESULTS.md` Deliverable 1;
  seed spread <4%, so pin the factor at prereg; rest-solo and
  play-solo are exact zeros for the teacher)
- needs-servicing latency percentile creep (the "world harder" vs
  "mind broken" separator)
- refusal-tax share above **3.5%** of any seat's ticks (owner ruled
  2026-09-01: 3.5% is where INVESTIGATION is warranted, not a retrain
  gate; was >10%). F-033 seam instrument / spec-046 stamp; Biscuit 2.0
  pays 4.6% today. c30 + consent IS the current response to the tax;
  the reading that counts is Biscuit 3.0's (policy seat, after
  training), with comfort-sweep Addendum 2 R8 as the scripted early
  look. Read it TOGETHER with the Biscuit-vs-roster welfare gap (E1
  all-needs parity): closing that gap is the point, the tax is one of
  its mechanisms.
- dispersion drift (NN median ≥3 but <5)
- vocabulary oddities (remember: aggregate msg@1 useless, 95% Silent)

Owner pins the exact H4/H6/refusal numbers at step-5 kickoff now that
baselines exist.

## Step 6 — remediate + LOCK

Apply step-5 remediations. "Locked" means all three at once: schema
version final; `binding_continuity.py` green (deny_unknown_fields —
the 040 lesson); both config sweeps green. Cert anchors re-derived on
the locked fog config (second and final re-baseline; the first was
step 1's — two total, accepted knowingly).

## Step 7 — certification round

5 new certifiable seats incl. Biscuit 3.0. Biscuit 3.0's design per
`biscuit3-design-note-2026-08-26.md` (anchor-side comfort fix +
proposal filter; the step-2 comfort sweep is its pricing input).
Two-layer welfare gates, G5 census, G6 soak,
owner's word for seating/deploy — the standing machinery, unchanged.
