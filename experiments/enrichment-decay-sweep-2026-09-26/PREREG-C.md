# Enrichment channel — dead-or-held probe, preregistration (stage C′)

Drafted and FROZEN 2026-09-30 on the owner's word ("run the probe"),
from the Professor's stage-B review (memo
`~/ai/professor/reviews/2026-09-29-stage-b-review.md`, relayed
2026-09-30 at her word). NOT the bracket sweep PREREG-B called
stage C — that premise (brackets on a β winner) died with F-056;
this probe adjudicates the review's narrower reading first.
Deviations go in `prereg-c-deviations.md`.

## Question

F-056 closed the β lever: the prize barely moves play. The
Professor's review says stage B never separated "channel dead" from
"channel held": (a) the agent cannot SEE the stock it is paid for
(E never enters the observation), and (b) the KL leash to the BC
anchor (0.04) penalizes play directly, with the per-seat lift read
showing the whole stage-B rise was Biscuit — the one seat whose
corpus plays. Dead or held?

## Arms (both at β 0.14, throttle, d100-1000 corner, run recipe
otherwise stage B's: clone init, package.toml, 20M cap, plateau
stop, futility 0.80 × 5)

| arm | what changes | seeds | run indices |
|---|---|---|---|
| l14 | leash 0.01 (pin `beta_probe`; stage B ran 0.04) | 2 | 90–91 |
| o14 | E visible: the stock written into the obs CLOCK slot (col 407) at every rollout tick and stored in the buffer; leash 0.04 | 2 | 92–93 |

Episode band 1,900,000,000–1,979,999,999 (the run-index formula).
Trainer `trainer/train_ppo_enrich2c.py`; the o14 rollout stock uses
enrich2b_terms' recurrence exactly (guard-proven equivalent); the
reward term is stage B's enrich2b_terms at β 0.14.

DECLARED DEVIATION from the review's "E appended to obs": schema 5
has no spare float and a 409th column breaks the tokenizer, so E
rides the clock slot — in range (0–1, like the cycling clock the
embedding was trained on), and the clock input is already ruled for
removal at Gen 2. DECLARED CONFOUND: o14 removes the cycling clock
and adds E in one move; if o14 moves play, a clock-zero control is
owed before attributing the move to E alone.

## Instrument and reads

Trace play per arm (training-side, the enrich2b trace). Greedy
battery: l14 on the stage-B instrument unchanged (cert harness,
30 × 20,000, eval band 870001, `--clock train`, all-arm
composition, `--abort-streak 1000`); o14 needs E fed at eval, so
its leg runs on a declared custom runner (`probe_eval_o14.py`,
written before its leg is read): the cert-harness loop with the
same online-E recurrence writing col 407, greedy both heads, same
seeds/ticks/abort line. Reader `enrich2c_read.py` (before the
battery is read): per arm greedy + trace play, per-seat play lift
over the stage-B fresh gen1-A baseline, closed-gate share, at-cap
share, E p50, paired happiness vs recorded gen1-A, sleep, bin0,
eat+drink, teammate-distressed share, dist ticks, max streak —
stage-B columns, same definitions.

## Predictions (a probe: directional, readings not bars; the one
fixed reference is the standing 0.10 play bar)

1. **If the leash binds**: l14 pooled greedy play > the b14 family
   mean 0.0885, with the per-seat lift no longer Biscuit-only
   (ex-Biscuit summed lift > 0 on both seeds).
2. **If observability binds**: o14 > b14 on trace play (> 0.0938)
   and greedy play, same per-seat test.
3. **Both flat** (within the b14 family's per-seed range): the
   channel-dead verdict survives the review's narrower test.
4. Watched (stage-B lines): closed-gate share, bin0 ≤ 0.211,
   eat+drink ≤ 0.0699, sleep band, tm-dist 0.001, no aborts,
   streaks < 1,000, at-cap reported before conclusions. l14 is the
   welfare watch of the probe: a loosened leash frees MORE than
   play, and the F-019 finding (the leash carries personality and
   its removal costs welfare) predicts a happiness price — the
   paired delta is a primary read, not a footnote.

## Decision rules

- Any arm clearing 0.10 pooled greedy play: the channel is HELD,
  not dead — F-056 gains a dated scope note naming what released
  it; the Gen 3 fork input changes accordingly. Her fork either
  way; nothing deploys; rule 1 unamended.
- l14 moves but o14 does not (or vice versa): the binding
  constraint is named (leash vs observability); report; her fork.
- Both flat: F-056 stands on the narrower test; the Gen 3
  free-time design proceeds on the recreation-actions direction
  with the reward-channel branch closed twice.
- o14 movement is NOT attributed to E alone without the clock-zero
  control (the declared confound).

## Welfare practice

1. **Stops**: plateau, 20M cap, §10, futility 0.80 × 5; asymmetric;
   no early-success stop. The 1,000-tick abort line on every eval
   leg.
2. **Scout**: not a new world config (package.toml, standing
   numbers).
3. **Welfare cost**: expected exposure at stage-B levels (worst leg
   1,563 distress ticks); declared expectation ≤ 2× stage-B's worst
   leg (≤ ~3,200 per 30-seed leg), except l14, where the loosened
   leash is uncharted — l14 carries the stage-A line instead
   (≤ ~8,200) and the abort line is the hard stop. What the run
   buys: the dead-vs-held adjudication the Gen 3 fork needs, per
   the Professor review.
4. **Measurement aborts**: `--abort-streak 1000` every leg; trainer
   futility armed.
5. **Fences**: untouched.

## Guard (rule 5)

`test_enrich2c.py`, three mutate reds predicted before running:
(a) decay dropped from `roll_E_step` → `test_recurrence_equivalence`;
(b) `E_COL` 407 → 406 → `test_collect_writes_E`;
(c) l14's pin flipped to the 0.04 leash → `test_leash_pins`.
The stub-runner justification is in the test's docstring (the
property is pure wiring; no recorded payload carries the E column).
