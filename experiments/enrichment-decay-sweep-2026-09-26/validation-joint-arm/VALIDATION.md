# Joint-arm instrument validation (pre-PREREG-D shakeout)

Run 2026-10-03 on the owner's word ("Yes please" to checks 1–2; the
replay check from the Professor's critique under the same
commission). Everything here regenerates deterministically from the
scripts beside this file; run outputs lived in the session
scratchpad and are reproducible, not archived. Shakeout only — no
row here is a finding.

## Check 1 — anchor equivalence (`check1_pad_equiv.py`)

1,000 real schema-5 obs (gen1-A cert config, random masked actions,
seed 777 — outside every claimed band), clone-fog anchor.

- Zero-weight padded column, self token 85→86: NOT bit-exact, max
  logit |diff| 1.359e-05, constant across E ∈ {junk, 0, 1}.
- Padded clock token 1→2: NOT bit-exact, 1.621e-05.
- Transcription control (forward copy, no pad): bit-identical —
  the drift is the width change, not the copy.
- ADDITIVE form (`+ e_col·E`, e_col zero-init): bit-identical to
  stock for E ∈ {junk, 0, 1}; E-invariant bitwise.
- Reds (predicted first): nonzero pad column 3.442e-03; nonzero
  e_col 3.443e-03. Both broke equality as predicted.

## Check 2 — training inertness (`check2_driver.py` + compare)

Paired 20-update runs of the l14-s1 configuration, threads 1,
out-dirs and the enrich2b trace redirected to scratch.

- stock vs stock re-run: bit-identical (policy 49 keys, critic 37,
  opt state, both RNG states, all 20 metrics rows).
- fork (E held 0), joint clipping: DIVERGED at row 0 on exactly
  {kl_anchor, clip_frac, grad_norm, policy_loss}; collection stats
  bitwise equal — isolated to the extra zero-grad param's 0.0 in
  the clip_grad_norm_ stack. e_col ended exactly 0.
- fork with SPLIT clipping (e_col in its own group, same max-norm):
  bit-identical to stock on policy, critic, both RNG states, all 20
  rows; e_col exactly 0. Predicted before the run.
- Red (e_col 1e-3, E=1.0, channel live): diverged from row 0 on
  collection stats too, as predicted.

## Replay check — recorded runs reproducible (Professor's
induction-hole check; `replay_driver.py` logic now carried by the
battery-side `e_edges_replay.py` verification)

First 20 updates of BOTH recorded l14 seeds re-run with the recorded
invocation (threads 2, total-ticks 20M schedules) — every metrics
row equal to the recorded rows at full JSON float precision, both
seeds. First attempt of the eval-side replay drifted on the clock
(the `-c0` legs pin obs col 407 to 0); fixed, and the per-leg
assert in `e_edges_replay.py` now verifies every eval replay
tick-exact against its recorded battery row.

## What PREREG-D takes from this

Additive e_col (never a padded column); split-clip declared with
the null/positive asymmetry; `--threads 2` pinned; recorded l14 =
the control (no trained control arm; the four-run case returns only
on a positive, as the joint-clip replication rider); the `-0.0`
footnote in limits.
