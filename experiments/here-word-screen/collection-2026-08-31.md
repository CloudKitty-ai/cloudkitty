# Here-word density screen — collection declaration (before any rollout)

Owner's word 2026-08-30 ("Half A runs NOW"); knob merged as spec 043
(PR #328 → main `2f5fb6c`, 2026-08-31). Everything not stated here is
inherited verbatim from the pre-registered plan
(`experiments/here-word-density-screen.md`, incl. the 2026-08-30
FR-006 selection amendment) — arms, read-outs, predictions, F-015
conditioning, welfare report-only. Declared BEFORE any collection ran;
committed first.

## Verification already done on the merged tree (2026-08-31)

- Gate zero (in-tree, `announce_here_gate_zero`): 3/3 green —
  action digests equal knob off/on, Here\* present in the on-run,
  want/WaitForMe streams identical, armed-run determinism, density
  ladder descends with the period.
- `evolution_golden` green (pin unregenerated); stamp CI-guard
  (`roam_cell_stays_out_of_the_default_serialization`) + both
  `announce_here` config guards green.
- bc-collect rebuilt at main `2f5fb6c` (prints its engine commit per
  rollout meta).
- `HEAD_KINDS` confirmed to carry all four Here\* kinds (indices 8–11),
  so `label_msg`/`mask_msg` rows can express and a V4 clone can emit
  them — the F-029 emit-proof for this instrument.

## Design

**Composition**: `exp-006-character-gen/collect-config-bugs2.toml`
verbatim — the anchor-cell composition (5 seats: 1 playful + 4
needs_driven, 20×20, 041-migrated dials in-tree). One derived config
per arm, differing from the source by exactly one line:

| arm | config | `announce_here` |
|---|---|---|
| A0 | `arm-A0.toml` | absent (byte-identical copy of the source) |
| A1 | `arm-A1.toml` | 1 |
| A2 | `arm-A2.toml` | 4 |
| A3 | `arm-A3.toml` | 16 |

Each derived config verified by tomllib assert (the one key) plus
line-diff against the source (A0: empty diff; A1–A3: one insertion
only).

**Rollouts**: 25 per arm × 8,000 ticks (5 deciders/tick ≈ 1.0M
decisions per arm; the plan's "fraction of the 3.9M-row anchor").

**Seeds — PAIRED ACROSS ARMS BY DESIGN**: band **1,060,001–1,060,025**
(fresh, above the prior 6-digit high 1,057,006; claimed in
SEED-BANDS.md in this commit). All four arms run the SAME 25 seeds
(bc-collect formula base + r, single config so ci = 0). The pairing is
deliberate and is itself an instrument: knob-off and knob-on worlds at
the same seed must produce byte-identical action streams, so gate zero
gets re-verified at corpus scale on real payloads, and arm contrasts
are within-seed.

**Training** (after QA): `train_clone6.py` verbatim — defaults
(epochs 20, batch 4096, lr 3e-4, patience 3, trainer seed 20260818 —
the trainer's own seed, not a world seed), EntityPolicyV4, lab venv
`exp-006-character-gen/.venv`. One clone per arm, `--data-root` the
arm's rollout dir. Speed dials (`--limit-rollouts`, lower epochs) only
if an arm drags, recorded here if used.

## Acceptance (before any training touches the data)

1. Integrity, anchor-cell style: seed contiguity on the formula,
   config sha match per rollout meta, engine commit `2f5fb6c` in every
   meta, drop/mask-mismatch rates at v6 levels (≈0.06% / ≈0.22%),
   msg-mask-mm 0.
2. **Corpus-scale gate zero**: for every seed, `label`/`kitty`/`tick`
   arrays byte-identical A0 vs each armed arm; `label_msg` differs
   knob-on; want/WaitForMe label rows identical across arms.
3. **Realized here-share table** (report): per arm, here-word share of
   decisions and per-kind counts — prediction 2 (monotone in the
   period) is read here.

Welfare read-outs at training/readout time are REPORT-ONLY (F-026);
a null is the expected result. Acceptance record appended here with
raw pointers before training.

## Outputs

Raws to `experiments/here-word-screen/results-raw/arm-A{0..3}/`
(uncommitted, house practice); this doc carries the acceptance record
and the numbers that survive.
