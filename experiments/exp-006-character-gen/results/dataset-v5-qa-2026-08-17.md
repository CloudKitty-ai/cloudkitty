# Dataset v5 acceptance QA (2026-08-17)

Both cells PASS. Instrument: `dataset_qa.py` (raw per-config tables
in `results-raw/dataset-v5-qa.json`). Collections ran via
`bc-collect --family-dir` after the config-index overwrite defect
forced a full re-collection; everything below is measured on the
re-collected data.

## Integrity

Per cell: 108 rollout dirs, all 18 configs x 6 rollouts present and
correctly indexed. World seeds match the registered formula
(base + ci x 1000 + r; spread band 910001-927006, pinned band
940001-957006). Every rollout's `config_sha256` matches the sha of
its family file on disk. Schema uniform across all 216 dirs: obs 4
(width 225), action 3 (mask 34), msg mask 16. Every config carries
a playful seat (F-022 guarantee, verified per dir).

## Aggregate QA

| cell | decisions | dropped | mask-mismatch | msg-mask-mismatch | msg-inexpressible |
|---|---|---|---|---|---|
| A pinned | 3,447,547 | 0.038% | 0.207% | 0 | 0.695% |
| B spread | 3,447,175 | 0.050% | 0.206% | 0 | 0.668% |

Mask-mismatch sits at the exp-005 probe-band level (0.207%,
cooldown-timing, known cause). msg-inexpressible is entirely the
engine-reserved WaitForMe labeling as Silent, the documented
mapping. Per-cell rows land at ~3.45M, under the prereg's ~4.3M
estimate: that estimate assumed 5 deciders/tick, but the roster
strata average 4 (see below). The registered budget itself
(6 x 8k ticks per variant per cell) was delivered exactly; only the
deciders-per-tick arithmetic in the estimate was off. 3.45M/cell is
~1.8x the v4 row count, against the ~2.2x the 3a raise aimed for.

## Roster strata and the trio welfare audit (record-never-exclude)

Each cell runs 6 trios, 6 quads, 6 quints (the family-gen roster
stratum), so `state.npy` width varies per world: 133/165/197 =
(roster x 32) + 37. Downstream consumers (critic, fingerprint probe)
must read the width from the header, not assume 197.

Welfare across the 36 worlds: mean happiness 82.5-88.3, team reward
0.823-0.882/tick. Both cells rank the same way: quints highest,
trios lowest (fewer duet partners — F-020's social pricing, visible
in scripted company). The spread cell's floor is lower than the
pinned cell's (82.5 vs 85.9) — extreme trait draws are doing what
the owner asked of them: producing stress-point worlds. Distress is
near-absent everywhere: worst world 0.01% of rows with any flag set
(spread cfg 03: 10 eat + 7 bath distress rows of 143k). Nothing
approaches an exclusion question; all 36 worlds stay in.

Stress exemplar for the record: spread cfg 15 (trio, happiness
82.5, reward floor 0.60). Happiest: pinned cfg 08 / spread cfg 02
(quints, 88.3 / 88.0).

## New-kind channel facts

- **Zero new-kind emissions anywhere**: every `label_msg` value in
  all 216 dirs is <= 8 (asserted). Confirmed at the source: no
  scripted behavior contains a Here*/Chirp proposal site. The BC
  stage therefore cannot teach a new word (the bootstrap doctrine's
  premise, now measured); any new-kind speech in candidates is PPO
  exploration, which is what the G5 census + 5/1k trigger watch.
- **Here* mask-legal exposure** (share of decision rows where the
  mask offers the word): here_food ~9.8%, here_water ~17-18%,
  here_critter ~10%, here_sunbeam ~13%, varying by world
  (min 6%, max 27%). Chirp is legal on 100% of rows (cooldown-only
  law, never spent by scripted). Trill/Ekekek are 0 everywhere —
  the reserve flag is confirmed off in the collection config.

## §4b Here*-void rate: finding and an open fork

The registered rider ("mask-legal-but-voided Here* rate, decisions
vs emissions on replay") is **structurally vacuous on this data**:
scripted experts never propose Here*, so there are zero Here*
decisions to compare against emissions. The rate is 0/0, not a
small number.

What CAN be reported from banked data is the mask-side exposure
above. The mechanism §4b worries about (mask legal on the pre-tick
snapshot, voided by mid-tick element state) remains real and
unmeasured — measuring it requires a shadow-replay tool that forces
Here* proposals through cloned tick states, which no current
instrument does. Options, for the owner's call:

1. Accept the documented asymmetry (the 033 spec's position) and
   revisit only if PPO candidates actually speak Here* (the G5
   census will show it).
2. Build the shadow-replay census before PPO, so the void-given-
   legal rate is known before any candidate explores the word.

Nothing in the frozen prereg blocks training on this: the rider
promised a measurement with the acceptance record, and this section
is that report.

**Owner ruling (2026-08-17): option 1.** The asymmetry stays a
documented property (it rots in the safe direction by design); the
shadow-replay census is built only if a candidate's G5 census shows
real Here* speech. The 5/1k new-kind trigger already watches that
behavior.

## Final expansion-residual numbers

The D-001 per-artifact residual re-ran on the complete spread cell
(10k rows spanning all 108 dirs; `expansion_acceptance.py
--full-cell`, raw in `results-raw/expansion-acceptance-full.json`):

| candidate | new-kind act-flip | legacy-ref | ratio |
|---|---|---|---|
| attn-a1-s1-o4 | 19.61% | 14.10% | 1.39x |
| attn-a1-s3-o4 | 17.85% | 12.16% | 1.47x |
| e004-a1-s2-o4 | 0.00% (structurally deaf) | 19.12% | 0.00x |

These supersede the provisional numbers in
`expansion-acceptance-2026-08-17.md` §3 as the acceptance-record
values. The reading stands: an anonymous new word lands as roughly
"a meow," modestly stronger than a known kind.
