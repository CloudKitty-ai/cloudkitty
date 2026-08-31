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

## ACCEPTANCE RECORD (2026-08-31, collection complete — PASS)

All four arms collected same day on bc-collect rebuilt at merged main
`2f5fb6c`; adjudicated by `qa_screen.py` (this dir). Every assertion
in the QA script was shown red first by its exact predicted bug on
corrupted copies (real raws untouched): action-label corruption,
non-here message injection, here-overwrites-want, non-here mask_msg
column flip, off-formula seed — five mutations, five predicted reds,
all restored green.

**Integrity**: seeds 1,060,001–25 on formula in every arm, config shas
uniform per arm, schema 4/3/3, widths 225/34/16, msg-mask-mm 0
everywhere. Per arm: 996,714 decisions, dropped 1,378 (0.138%),
mask-mm 1,908 (0.191%) — identical across arms, as paired seeds
require. **Deviation from the declared drop bar**: 0.138% vs the v6
anchor's ≈0.06% (mask-mm 0.191% is at level). The drops are
chase-dominated (`dropped_by_action`: chase ≈ 39/40 in the spot-checked
rollout) — consistent with 042's partner-value pick moving playful
targets, an engine change the v6 bar predates. Recorded, not excluded;
same rate in all arms so no arm contrast is touched.

**Corpus-scale gate zero (prediction 1 CONFIRMED)**:
`label`/`kitty`/`tick` byte-identical to A0 at every one of the 25
paired seeds in all three armed arms; every message diff is
Silent→Here\*; non-here `mask_msg` columns byte-identical (per-kind
cooldowns don't bleed into want legality).

**Realized shares (prediction 2 CONFIRMED — monotone in the period)**:

| arm | period | here% of decisions | food | water | critter | sunbeam | want% | silent% |
|---|---|---|---|---|---|---|---|---|
| A0 | off | 0.000 | 0 | 0 | 0 | 0 | 6.557 | 93.443 |
| A1 | 1 | 8.176 | 15,967 | 24,263 | 22,364 | 18,896 | 6.557 | 85.267 |
| A2 | 4 | 5.561 | 10,519 | 16,882 | 13,720 | 14,306 | 6.557 | 87.882 |
| A3 | 16 | 2.363 | 3,744 | 7,277 | 5,405 | 7,130 | 6.557 | 91.080 |

want% identical to the third decimal across arms — the precedence rule
at corpus scale. **The ladder is compressed**: A1:A3 ≈ 3.5×, not 16× —
per-kind cooldowns self-limit emission at period 1, so the density
dial buys less than its nominal ratio at the aggressive end. All three
armed corpora sit ABOVE the hypothesized ~1% cliff (sparsest = 2.36%);
if all three clones learn, the screen brackets the cliff between 0%
and 2.36% rather than straddling it — a period-64-class arm would be
the follow-up if the cliff's location (not just existence) matters.

Dataset accepted for training. Training started same day
(`train_clone6.py` verbatim defaults, artifacts to
`artifacts/here-A{0..3}/`, uncommitted).

## ADDENDUM (2026-08-31, owner-routed, declared before collection):
## arm A1b, period 2

Owner's word after the Half-A result: probe INSIDE the 5.6–8.2%
bracket with a period-2 arm rather than an A2 epoch extension —
location under the fixed recipe is the decision-relevant number
(the same recipe fog will use), accepting that the 20-epoch budget
qualifier carries over. Design identical to the registered arms in
every respect: `arm-A1b.toml` = source + `announce_here = 2` (one
insertion, tomllib + line-diff verified), the SAME paired seeds
1,060,001–25 (no new band — the claimed row's pairing extends to
five arms), 25 × 8,000, bc-collect at `2f5fb6c`, same acceptance
bars, `qa_screen.py`/`readout_screen.py` extended with the arm
(assertion logic unchanged — the red-first evidence stands).

## ADDENDUM 2 (2026-08-31, owner-routed, declared before running):
## training-budget extension on A1 / A1b / A2

Owner's question: is the transition's location (mute ≤ 5.6%,
half-fluent 7.6%, fluent 8.2%) a fact about density or about the
recipe's 20-epoch budget — and should Fog Gen 1's BC stage train
longer? Probe: re-train the three transition arms FRESH on the same
corpora, same trainer seed 20260818, same everything except
**epochs 60 (3×) and patience 10** — patience deliberately loosened
because a `--resume` continuation restores a nearly-spent counter
and patience 3 would censor exactly the plateau-then-late-learning
dynamic under test. This is explicitly a RECIPE PROBE, not the
verbatim recipe; artifacts land as `here-A{1,1b,2}-x60/`
(originals untouched). A0/A3 not extended (both sides of the
transition are settled; A3's corpus is A2's shape at lower density).

**Decision rule, pre-declared**: if the extension moves A2 from mute
to competent, or A1b from half-fluent to fluent, the training budget
binds at moderate density → recommend a longer BC cycle for Fog
Gen 1's clones, priced from the measured epoch cost. If the final
here-conditioned readouts land within noise of the 20-epoch values,
the recipe stands and density remains the binding constraint.
Learning curves read from each run's per-epoch `history` (aggregate
msg@1 is a valid per-arm curve proxy at fixed here-share; the
here-conditioned readout runs on final models).
