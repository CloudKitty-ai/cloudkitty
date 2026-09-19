# Beam-world screen, tier 2: does a clone learn to seek beams under the package? — prereg, 2026-09-19

Declared before collection. Owner's word 2026-09-19 ("Start tier 2"),
after tier 1 (`RESULTS.md`) showed the teacher's beam placement is set
by count and lifetime and that the relief numbers move nothing the
teacher does. Tier 2 runs the Gen 1 recipe end to end on the package
world, once with the floor change and once without, and reads whether
the resulting minds keep the teacher's beam placement through PPO. On
Gen 1 the BC clone kept 87% of the teacher's beam share (anchor r4
0.257 against the corpus 0.294, `fog-gen1-cert/RESULTS.md` §"3. Beam
naps") and PPO at β 0.04 then lost most of it (candidate pool
0.014–0.052); the price arms, which shared the candidates' corpus and
changed only the PPO world, did not recover it. Findings this rests on:
F-042, F-043, F-044, F-046, F-047.

## Worlds

- **package** (`package.toml`, sha256
  `7c33560a900e2a73a31252e7df901d0fc10d4987bd825bec6fb4446abfef41b5`):
  `anchor-b3.toml` with off-beam `sleep_relief` 5 → 3, `sleep_relief_sunbeam`
  7 (unchanged), sunbeam `ttl` 300 → 3000, sunbeam `min` 4 → 6 and
  `max` 5 → 7. The #390 (a) and (b) rulings at count 6 (the count is
  still the owner's; six is tier 1's package corner).
- **floor5** (`floor5.toml`, sha256
  `4f7cb1420379305593ba4e20ac096dcc2e8ef7e22c782a4600129208d21e4196`):
  the same with `sleep_relief` left at 5. The one-key contrast that
  isolates (a).

Both are tier 1's derivation (`derive_configs.derive`), byte-identical
to the tier-1 variants `s3-b7-t3000-n6` and `s5-b7-t3000-n6`, and
committed here so the arms cite a file.

## Corpus (one, the package world)

`bc-collect` (rebuilt today against main at f81b7f6; the lockfile gains
the core crate's `libc` dependency, nothing else) on `package.toml`,
the Gen 1 shape: 40 rollouts × 20,000 ticks, held-out = index ending in
3 (03/13/23/33) with `--trace`, nine seed blocks in parallel (`stage1.sh`).
Seeds **1,092,001–1,092,040** (new band, ledger row added). The flat
view `results-raw/tier2/bc-corpus-pkg/flat/config-00-rollout-NN` is what
the loaders read. Both arms clone from this corpus; the floor5 arms
train on a floor-3 corpus in a floor-5 world by design, so their
contrast with the package arms is the PPO world alone (the beam-price
screen's design). Raws uncommitted (about 8.5 GB).

## Clone, bars, critic

Lesson clone, the served recipe (`train_vocab_fog.py --stage strip`,
then `--stage teach`, d_model 64 / ffn 128), `pkg-vocab`. It seeds an
arm only if it clears the cert's BC bars on the held-out four
(`readout_fog.py --want-source proposed`: reply-here mass ≥ 0.50 per
kind, msg@1 ≥ 0.80 on here rows, wants within ±15% for kinds with ≥ 100
rows); the applied-source read is reported beside it. A miss is the
owner's call, as it was on 2026-09-13. Part A (`schema_check.py` with
the cert's `declared_constant.json`) runs on the four held-out traces;
a column that now varies because the world changed (the beam slots'
ttl fraction under a 3,000-tick lifetime is the candidate) is reported,
not a stop. **Critic**: the B3 critic is reused, the assumption the
consent-off twin declared (the world change moves returns' scale a
little through longer naps, not their ranking); its #365 probe bars
are not re-run.

## PPO (four runs, `trainer/train_ppo_beam.py`)

| slot | world | init | β | seed | run index |
|---|---|---|---|---|---|
| pkg-s1 | package | pkg-vocab | 0.04 | 1 | 41 |
| pkg-s2 | package | pkg-vocab | 0.04 | 2 | 42 |
| floor5-s1 | floor5 | pkg-vocab | 0.04 | 1 | 43 |
| floor5-s2 | floor5 | pkg-vocab | 0.04 | 2 | 44 |

Everything else is the shakeout trainer verbatim through the cert
wrapper's pattern: all-policy (MIX empty), 12 worlds, the Part C
plateau rule and the §10 welfare stop, probes every 50 updates on
40,001–3 for 2,000 ticks on the arm's own world, the 20M cap. Episode
seed bands = run index × 20M + 100M: **920,000,000–999,999,999**
(ledger row added). Four runs at 4 threads each under `nice -n 19` and
`caffeinate -s`, logs in `results-raw/tier2/pass-logs/`, artifacts in
`artifacts/ppo-fog-<slot>/` (gitignored). Part A at probe 1 on every
arm (`schema_check.py <held-out trace> --policy-trace
artifacts/ppo-fog-<slot>/probe-u49.npz`) before the pass is left to run.

## Reads (after the pass; `cert_harness_fog.py` with the beam block, 30 × 20k on the shared eval band, served clock)

Per arm, on its own world:

1. **arm into each gen1-A seat** (five report-only swap legs, the
   battery's own design): the arm's placement and tick share pooled
   over the five seatings, the matched read of "this mind in a served
   roster".
2. **all-arm roster** (the same network in five seats), with F-044's
   caveat on its welfare tail.

References already on disk from tier 1 on the same worlds and seeds:
the scripted teacher (placement 0.458 / 0.453, tick share 0.365 /
0.438 on package / floor5) and gen1-A (0.068 / 0.067 placement).
Matched reads across arms are taken at the same probe index (the
earlier plateau) off the probe series, and at each arm's final probe
beside it, as the cert did.

## Predictions

1. **Corpus.** The teacher's placement on the 40 package rollouts is
   0.42–0.50 and its tick share 0.33–0.40 (tier 1's 0.458 / 0.365 on
   other seeds).
2. **Clone.** `pkg-vocab` clears the bars, and its own placement on the
   package world (a quick 5-seed read of the clone at all five seats,
   greedy, before PPO) is at least 0.7 of the teacher's, i.e. ≥ 0.30.
   The Gen 1 clone kept 0.87.
3. **The pass, the question.** Package arms keep at least half of the
   clone's placement through PPO: pooled swap-leg placement ≥ 0.15 on
   both seeds. Floor5 arms lose it the way Gen 1 did: under 0.10 on
   both seeds. Read as a pair: (a) both under 0.10 means the corpus
   alone does not hold beam seeking against β 0.04 and the floor change
   does not either, so the remaining lever is the leash (F-047 stands
   in full); (b) package ≥ 0.15 and floor5 < 0.10 means the floor change
   is what holds it (F-047's re-verify passes as predicted there); (c)
   both ≥ 0.15 means the corpus (count 6, long beams) carries it and
   the floor change buys nothing the mind needs. Any other pattern is
   reported as it falls.
4. **Welfare.** Package arms' team Nash on their own world is at or
   above the scripted roster's (tier 1: 0.868) on every seed; no
   welfare stop fires; distress ages over 150 are reported by name.

## Decision rules

- Prediction 3's letter is the finding; it goes to #390 and to the Gen 2
  prereg as the F-047 re-verify. Nothing here changes the served
  world or the Gen 2 rulings on its own.
- A clone that misses a bar, an arm that hits the welfare stop, or a
  Part A red is reported to the owner before the next stage runs.
- No arm is dropped; every arm runs to its stop rule or the cap.

## Doctrine check (DESIGN-DOCTRINE.md)

- Rule 2 (prices are physics): the floor change is the world-state
  lever; the screen asks whether a mind answers it.
- Rule 7 (build a behavior when the world that values it exists): this
  is that test, run before the Gen 2 world is fixed so the world can
  still move.
- Rule 9 (frozen models cannot answer a reprice): the teacher is
  re-recorded and the minds retrained; no frozen artifact is read for
  the answer.
- Rule 10 (two-layer gates, noise is never a bar): the 0.15 / 0.10
  lines are placement bars on 30 × 20k, pooled over five seatings, not
  welfare readings; the Nash bar is the scripted roster's own number.
- Rules 1, 3, 4, 5, 6, 8: checked, moved nothing (the rule 4 farming
  read from tier 1 is repeated on the arms, report-only).

## Budget

One corpus (about 1.5 h), two clone stages (hours), four PPO runs
(7–17 h each at the box's hot pace, in parallel), the battery (about 1
h). About a day and a half end to end.
