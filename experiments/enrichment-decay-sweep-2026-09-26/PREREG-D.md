# Enrichment channel — joint release arm, preregistration (stage D)

Drafted and FROZEN 2026-10-03 on the owner's word ("Go"), the
E-band edges filled from `results-raw/e-edges/summary.json` before
this freeze. From the Professor's joint-arm critique (memo
`~/ai/professor/reviews/2026-09-29-stage-b-review.md`, §"What the
joint arm needs" + §"Joint-arm validation critique", both relayed on
her word). Deviations go in `prereg-d-deviations.md`.

## Question

F-057 lifted each suspected constraint alone: the leash release
(l14) moved play's composition but not its level; E-visibility (o14)
moved nothing, confounded by clock removal. The strong form of the
held hypothesis says both must lift TOGETHER — the policy must see E
and be free to act on it. With Gen 3 already proceeding on the
recreation-actions direction (PREREG-C consequence), this arm's
value is paper 1's negative control for the aggregate-reward route:
the route tested with both constraints lifted at once.

## Arm (β 0.14, throttle, d100-1000 corner, run recipe otherwise
stage B's: clone init, package.toml, 20M cap, plateau stop,
futility 0.80 × 5)

| arm | what changes | seeds | run indices |
|---|---|---|---|
| j14 | leash 0.01 (pin `beta_probe`) AND E visible, appended as obs column 408 | 2 | 94–95 |

Episode band 1,980,000,000–2,019,999,999 (the run-index formula;
SEED-BANDS.md row added at this commit). Trainer
`trainer/train_ppo_enrich2d.py`. `--threads 2` PINNED (the recorded
control ran 2; bit-replay verified at 2 — see Control).

## Design (validated before this freeze; evidence in
`validation-joint-arm/`)

- **E rides python-side only**: `roll_E_step` (guard-proven ≡
  `enrich2b_terms`) computed in collection, appended as a 409th
  column in the lab buffers and at eval. Schema 5, the binding, and
  `docs/encodings.md` untouched. The clock stays in col 407 — the
  o14 slot-sharing confound does not arise.
- **Additive form, not a padded column**: the policy is
  `EntityPolicyV5` + `e_col` (zero-init d_model vector); the self
  token embed becomes `Linear85(x) + e_col·E`. A padded 86-wide
  column is NOT bit-exact (kernel/summation order; measured
  1.36e-05 logit drift); the additive form is bit-identical to the
  stock function at `e_col = 0` for every E value (measured, 1,000
  real obs, red confirmed). The anchor is therefore the STOCK
  anchor, loaded as-is; `e_col` exists only in the live policy.
- **Split clipping, declared**: `e_col`'s gradient is clipped in its
  own group at the same max-norm, not jointly — the price of a
  bit-exact control (joint clipping shifts the norm stack by a last
  bit; measured, isolated, fixed). Professor's asymmetry rider
  applies (Decision rules).
- **Token placement**: self token (Professor: E is a need-like
  internal stock; read where the policy reads its own needs; o14's
  clock-slot placement was schema fullness, not design).

## Control — the recorded l14 runs ARE the control

No new control arm trains. Validated chain: (1) fork with E held 0
is bitwise the stock trainer over 20 paired updates (policy, critic,
RNG, all metrics rows; `e_col` exactly 0); (2) full checkpoint state
equality extends the identity by induction to any length; (3) the
CURRENT code reproduces the RECORDED l14 runs — both seeds' first 20
metrics rows replay bitwise at the recorded `--threads 2`
(Professor's induction-hole check, closed 2026-10-03). A POSITIVE
result owes the joint-clip replication rider before any claim
(Decision rules); a null stands on this control as is.

Residual, footnote-level: the additive identity leans on `x + 0.0`
being bitwise identity, which flips `-0.0` inputs to `+0.0`;
empirically clean over every validation run, vanishingly unlikely,
noted here as the declared limit.

## Instrument and reads

Training trace per arm: stage-B trace columns plus the clip
diagnostic — fraction of minibatch steps where the main clip fires
(`grad_norm > 0.5`), and `e_col`'s own grad-norm ratio to the main
group (Professor: bounds the split-vs-joint semantic gap; if the
main clip rarely fires, the semantics coincide).

Greedy battery: declared custom runner `probe_eval_j14.py` (written
before its legs are read): the cert-harness loop, clock pinned 0 at
col 407 (`-c0`, as the control legs), E appended at col 408 via the
same online recurrence, greedy both heads, 30 × 20,000, eval band
870001, `--abort-streak 1000`, all-seat composition. Per-tick
(seed, tick, seat) E and playing flags recorded (the control's
equivalents already recorded in `results-raw/e-edges/*.npz`).

Reader `enrich2d_read.py` (written before the battery is read):
stage-B columns (enrich2c definitions) PLUS the banded contrast
below.

## E-band edges — FROZEN FROM THE RECORDED CONTROL

Pooled per-tick E over both recorded l14 seeds (2 × 30 × 20,000 × 5
= 6,000,000 samples; `e_edges_replay.py`, each leg verified
tick-exact against its recorded battery row before use):

- low band:  E ≤ 0.43660981456438697
- high band: E ≥ 0.8065612316131592
- middle tercile excluded.
- Control per-seat contrasts (high-minus-low play share, pooled
  edges) and between-seed spreads (|s1−s2|):

| seat | contrast | spread |
|---|---|---|
| Miso (0) | 0.08509 | 0.01343 |
| Biscuit (1) | 0.22609 | 0.03098 |
| Pumpkin (2) | 0.09090 | 0.01219 |
| Kittybear (3) | 0.08604 | 0.00772 |
| Clementine (4) | 0.09404 | 0.01402 |

  The non-Biscuit control contrasts of 0.085–0.094 are the confound
  floor made concrete: E tracks recent play mechanically even when
  the policy cannot see it.
- Minimum per-band per-seat occupancy for a seat's contrast to be
  read: 10,000 tick-samples per band per seat per arm-seed (the
  control runs 199,531–716,732); below that the seat is reported
  UNREAD, never imputed.

## Predictions

1. **Primary (the strong held-form test)**: per-seat excess
   contrast = live j14 (play share in high band − low band, frozen
   edges) MINUS the control's same-seat contrast. The channel is
   ALIVE in the strong form if excess contrast > 0.02804 (=
   max(0.02, 2 × the largest NON-BISCUIT control between-seed
   spread, Clementine's 0.01402; Biscuit's spread is excluded as
   Biscuit is excluded from the condition) on at least 3 of the 4
   non-Biscuit seats, on BOTH live seeds. The
   control contrast is the confound floor (E correlates with recent
   play even unseen); the raw live contrast is never the test.
   Biscuit's excess contrast is reported separately (anchor-dominant
   seat), never part of the condition.
2. **Secondary**: pooled greedy play vs the 0.10 bar; vs b14 mean
   0.0885 and l14 (0.0722/0.0867); ex-Biscuit lift vs l14's
   (+0.0479/+0.0893). Directional readings, not bars.
3. **Watched** (stage-B lines): closed-gate share, bin0 ≤ 0.211,
   eat+drink ≤ 0.0699, sleep band, tm-dist 0.001, aborts/streaks,
   at-cap reported before conclusions; paired happiness vs recorded
   gen1-A a primary welfare read (l14 precedent: positive mean,
   widened tail).

## Decision rules

- **Primary met on both seeds**: the channel is HELD in the strong
  form — but NO claim lands until the joint-clip replication rider
  runs (same arm, joint clipping, 2 seeds — the four-run case
  returns only here) and reproduces the direction. F-056/F-057 then
  gain dated scope notes; her fork on everything downstream.
- **Primary not met**: the negative control stands — the
  aggregate-reward route is closed with both constraints lifted
  together; paper 1 gets its paragraph; F-056 and F-057 stand
  unchanged; Gen 3 proceeds exactly as PREREG-C's consequence
  already set (this arm changes nothing on a null — declared now).
- Totals clearing 0.10 without the primary: reported as a
  composition-free rise; the primary still decides the strong form.
- Nothing deploys; rule 1 unamended.

## Welfare practice

1. **Stops**: plateau, 20M cap, §10, futility 0.80 × 5; asymmetric;
   no early-success stop. 1,000-tick abort line every eval leg.
2. **Scout**: not a new world config (package.toml, standing
   numbers).
3. **Welfare cost**: the joint release is uncharted but l14-shaped;
   declared expectation ≤ the stage-A line l14 carried (≤ ~8,200
   dist ticks per 30-seed leg), abort line the hard stop. Both
   prior releases ran toward the abort line (l14-s1 streak 952;
   o14-s2 aborted) — named here as a condition of running, per the
   critique. What the run buys: paper 1's negative control for the
   aggregate-reward route, or the strong-form held verdict.
4. **Measurement aborts**: `--abort-streak 1000` every leg; trainer
   futility armed.
5. **Fences**: untouched.

## Guard (rule 5)

`test_enrich2d.py`, mutate reds predicted before running:
(a) `e_col` init nonzero (1e-3) → the anchor-equivalence test
(additive forward at e_col=0 must equal stock forward on real obs)
goes red; (b) E appended at the wrong column (407 for 408) → the
append-position test goes red; (c) the split-clip filter's marker
dropped → the main-clip-param-list test (must exclude `e_col`) goes
red; (d) l14 leash pin regression → `test_leash_pins` (inherited
check, 0.01 on j14). Recurrence equivalence already guarded in
`test_enrich2c.py` and reused unchanged.
