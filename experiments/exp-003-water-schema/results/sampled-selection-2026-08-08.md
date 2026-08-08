# Sampled selection on the served world — measured, and it loses

**2026-08-08.** The exp-004 design inputs (§2) parked sampled selection
with a proposed test: §9.1 water band + deployed-composition distress
probe under sampling, against the committed greedy records, same world,
same seeds. Run today; instrument
`trainer/sampled_probe.py`, raw in `sampled-selection-2026-08-08/`.
Candidate `A2-m0-g998-s3` (the deployed artifact), served 20x20 world,
deployed composition (policy at Miso + Kittybear, scripted Biscuit /
Pumpkin), sampling as the engine does it (temperature-1 softmax over
masked finite logits; torch's draw stream, seeded per run — a
statistical twin of `DecisionRng`, not a replay).

| measurement | greedy (committed record) | sampled (this run) |
|---|---|---|
| deployed-composition crossings, 30 seeds | **0/30**, worst streak 0 | **1/30**, worst streak **127** |
| §9.1 in-water (10 paired seeds) | 3.30% = **79% of B** | 3.76% = **90% of B** |
| §9.1 lounging | 0.73% | 0.80% |
| band verdict (B = optE-B policy seats, 4.18% / 1.83%) | PASS | PASS |

Greedy anchors: `screens/geometry-20x20-optE-2026-08-07/water-band/
wb-opte-20x20/A2-m0-g998-s3.json` (seeds 800001–800010) and
`screens/geometry-20x20-optE-2026-08-07/seeds/deployed-composition.json`
optE rows (seeds 800001–800030). Mean water tiles 7.0 — same world.

The crossing seed is 800020: 311 hot ticks across eat 95 / drink 101 /
sleep 38 / cuddle 77, one 127-tick streak — a real incident, not a
threshold graze.

## Verdict: the parked position is now a measured one

Sampling at the deployed composition **costs** distress-cleanliness the
world currently has for free (0/30 → 1/30 with a 127-tick streak) and
**gives back** a chunk of the water advantage that is exp-003's
headline (79% → 90% of the scripted baseline — still inside the band,
but the "drier than scripted" margin narrows by half). And it fixes
nothing: greedy is already 0/30 here. The selection-symmetry record's
case for sampling lives at the all-policy roster (4 copies), where
self-interaction collapses under greedy — a *gate* composition, not the
served one. Adopt-side conclusion unchanged and now evidenced:
**greedy stays; sampling is a measurement tool for symmetric-roster
evaluation, not a deployment setting.** (Adoption would anyway be a
registered condition and a re-certification, issue #70.)

Caveat: one sampled run per seed; a different draw stream could land
the incident on a different seed or none. The direction of both deltas
(toward B, toward incident) is the expected effect of softening a sharp
policy's action distribution, and both agree with the
selection-symmetry record's "near-greedy but not greedy" analysis —
this is a confirmation at deployment composition, not a surprise.
