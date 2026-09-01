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

## Step 2 — pre-fog validation (lab, fast)

- **Primary: scripted needs-driven lab worlds** vs the needflow model's
  predicted bands (`cuddle-economy-model/RESULTS.md`) — rest nonzero
  and sustained, cosleep ~6:1 over solo sleep, play within ~2/1k,
  groom mix retained, both rest tiers shown able to emit.
- Secondary: MLP fast-training smoke. Weak negatives (learners barely
  discovered hunting under a correct economy) — confirmatory only.
- `tail-benchmarks/family-11-r5` against the collapse-detector v0
  (ROADMAP parking lot item; the known-positive it must catch).
- **Here-word density screen** — **Half A DONE 2026-08-31 (F-034,
  `here-word-screen/RESULTS.md`)**: vocabulary cliff between 5.6% and
  8.2% corpus share; `announce_here = 1` is the fog collection
  parameter; act@1 and welfare untouched. Collection complete, so the
  contagion flip is unblocked from the screen side.
- **Biscuit 3.0 comfort sweep** (`biscuit3-design-note-2026-08-26.md`)
  — scripted `playful_comfort` dose-response, owner-gated to run once
  ALL pre-fog engine changes are in (step 1 + any step-3 economy
  members), so it prices the dial against the economy Biscuit 3.0
  trains under.

The validated step-2 mix bands become step 5's reference.

## Step 3 — the pre-fog schema-break bundle (owner decisions)

A short doc listing in/out. Known members: the waterline (**ruled
2026-08-30: contagion IN for Gen 1 at factor 1.0** — the mechanism
ships pre-wall inert and flips after the 041 soak, handoff at
`waterline-contagion-handoff-2026-08-30.md`; only the
neighbour-in-water float waits for the wall, ruled jointly with the
scene-age float), the KITTY_SLOT gap ("wants the wall"), anything else
wanting a schema break. Nothing enters step 4's spec without appearing
here first.

## Step 3.5 — tag v2.10 (owner-ruled 2026-08-30)

The last stable 2.x, capping the pre-wall deploy train: 041 deploy +
soak → refusal-stamp fast-follow → `announce_here` knob → contagion
flip deploy + soak → **tag**. Prereq per house practice: expand
`## Unreleased` first — joint pass at tag time (owner + Experiments),
completeness-checked against `git log v2.9..` (toolchain pin #305,
Biscuit 2.0 cutover, the client run #300+, 041, 042, plus whatever the
train adds). Fog work on the far side is 3.0-numbered.

## Step 4 — implement Fog Gen 1

Spec-first (speckit). Scope per ROADMAP; free register never scripted;
here_* words are about the WORLD, want_* about speaker state.

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
| H4 | single-activity domination | one partnered activity >50% of a seat's decisions, sustained | F-027 ran ~98%; detector v0 validated on family-11-r5 |
| H5 | frozen cluster | same-pair contact share near-total, sustained | F-027's spatial signature; `nn_distance.py` + pair census |
| H6 | hyper-dispersion | NN cheb MEDIAN ≥ 5, sustained | baseline median 1.0 — 5× current; loose deliberately (fog legitimately disperses) |

### INVESTIGATE (log, continue; input to step 6)

- activity mix outside step-2 bands by modest factors
- needs-servicing latency percentile creep (the "world harder" vs
  "mind broken" separator)
- refusal-tax share >10% of any seat's ticks (F-033 seam instrument;
  Biscuit 2.0 pays 4.6% today)
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
