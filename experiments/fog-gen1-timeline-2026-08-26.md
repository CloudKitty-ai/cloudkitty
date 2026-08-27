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
  window so far) before the step-6 design call.

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
- **Here-word density screen** (plan @ 8c50fda) — the fog-vocabulary
  de-risker runs HERE, on the current gen, before fog forecloses it.
- **Biscuit 3.0 comfort sweep** (`biscuit3-design-note-2026-08-26.md`)
  — scripted `playful_comfort` dose-response, owner-gated to run once
  ALL pre-fog engine changes are in (step 1 + any step-2½ economy
  members), so it prices the dial against the economy Biscuit 3.0
  trains under.

The validated step-2 mix bands become step 4's reference.

## Step 2½ — the pre-fog schema-break bundle (owner decisions)

A short doc listing in/out. Known members: the TABLED waterline
pairing rule (owner 2026-08-24: "revisit when finalizing the pre-fog
schema-break bundle" — this is that moment; `here_water` confound with
fog vocabulary arms noted there), the KITTY_SLOT gap ("wants the
wall"), anything else wanting a schema break. Nothing enters step 3's
spec without appearing here first.

## Step 3 — implement Fog Gen 1

Spec-first (speckit). Scope per ROADMAP; free register never scripted;
here_* words are about the WORLD, want_* about speaker state.

## Step 4 — shakeout training round

Deliberately small: fewer seeds, shorter horizon. Purpose = discover
remaining schema/engine changes, not certify. Criteria PRE-DECLARED
below; anything not on the HALT list is step-5 data, not a stop.

### HALT (egregious — stop, fix, possibly break schema)

| # | trigger | threshold | baseline / instrument |
|---|---|---|---|
| H1 | watchdog alarm | any | spec-040 box log (absolute, fog-independent) |
| H2 | worst-seat welfare below the scripted anchor on the SAME fog config, sustained | anchor re-derived on fog config | scripted anchors = house cert practice; per-seat because Nash p=0 punishes one sacrificed cat |
| H3 | hard-zero intended activity | 0 over an emit-proven window | F-029 rule; census + F-031 spans |
| H4 | single-activity domination | one partnered activity >50% of a seat's decisions, sustained | F-027 ran ~98%; detector v0 validated on family-11-r5 |
| H5 | frozen cluster | same-pair contact share near-total, sustained | F-027's spatial signature; `nn_distance.py` + pair census |
| H6 | hyper-dispersion | NN cheb MEDIAN ≥ 5, sustained | baseline median 1.0 — 5× current; loose deliberately (fog legitimately disperses) |

### INVESTIGATE (log, continue; input to step 5)

- activity mix outside step-2 bands by modest factors
- needs-servicing latency percentile creep (the "world harder" vs
  "mind broken" separator)
- refusal-tax share >10% of any seat's ticks (F-033 seam instrument;
  Biscuit 2.0 pays 4.6% today)
- dispersion drift (NN median ≥3 but <5)
- vocabulary oddities (remember: aggregate msg@1 useless, 95% Silent)

Owner pins the exact H4/H6/refusal numbers at step-4 kickoff now that
baselines exist.

## Step 5 — remediate + LOCK

Apply step-4 remediations. "Locked" means all three at once: schema
version final; `binding_continuity.py` green (deny_unknown_fields —
the 040 lesson); both config sweeps green. Cert anchors re-derived on
the locked fog config (second and final re-baseline; the first was
step 1's — two total, accepted knowingly).

## Step 6 — certification round

5 new certifiable seats incl. Biscuit 3.0. Biscuit 3.0's design gated
on the step-0 needs-servicing latency finding before committing to the
solo-pounce fallback. Two-layer welfare gates, G5 census, G6 soak,
owner's word for seating/deploy — the standing machinery, unchanged.
