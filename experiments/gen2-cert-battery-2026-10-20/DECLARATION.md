# Gen 2 cert battery — step-8 declaration (2026-10-20)

Authorization: owner, 2026-10-20 — "Sounds great, let's do it", to the
proposed sequence (play-drift trace read, then the §10 step-8 cert
battery). Prereg basis: `gen2-prereg-2026-10-17.md` §7 (frozen
18f06f84); timeline step 8 ("paired-strict vs comparator"). This file
declares the run plan and reads BEFORE any battery data exists.
Departures land in `../gen2-deviations.md`.

## Seatings

Three, one per completed trunk seed, each the CTDE-declared deployment
shape — ONE artifact's weights in all five seats (prereg R§7):

- `g2-s1` = g2:trunk-s1 ×5 (policy-final sha256 a22b8713…)
- `g2-s2` = g2:trunk-s2 ×5 (policy-final sha256 4040554a…)
- `g2-s4` = g2:trunk-s4 ×5 (policy-final sha256 69d7248c…)

All three run the full battery: the ≥3-paper-seeds rule (prereg
§7/R§roadmap) and the replication-valve framing — no gate conclusion
is claimed from one seed. Exact shas re-verified in the launch stamp
(harness provenance rows).

## Legs (paired with the comparator by construction)

- Band `g2cmp` (seeds 905001–905030) — deliberate REUSE of the
  comparator band: the prereg's pairing design ("the trained-roster
  leg on seed s reuses the comparator's config, so the gate
  comparison shares starts by construction"). Not a new burn; no
  SEED-BANDS claim.
- Configs verbatim: `../gen2-comparator-legs-2026-10-14/g2leg-{20,40,100}.toml`
  (vision law; engine draw-law starts).
- 30 seeds × 20,000 ticks per leg; sizes 20/40/100; clock = served
  (the v6 observation carries no episode-clock input; "served" is the
  only truthful mode and the harness refuses others for g2 seats).
- Driver: `../gen2-comparator-legs-2026-10-14/run_legs.py` with the
  new `--seating` passthrough; harness = the standing
  `../fog-gen1-cert/cert_harness_fog.py` extended with the g2 seat
  spec (same instrument both sides of the pairing).

## Gates and baselines (pinned at freeze; never edited here)

- 20×20 gate: trained team happiness ≥ scripted comparator
  (81.921, per-seed range [80.409, 82.712]), paired by seed.
- 40×40 gate: ≥ 81.634 (v5 leg; range [80.640, 82.320]), paired.
- 100×100: characterize-only (comparator 76.623 [73.754, 80.416]);
  INVESTIGATE rows, never a gate, never a trigger.
- Gate read (declared now): per size, the 30 paired per-seed deltas
  (trained − scripted team happiness, same seed) with mean, sign
  count, and range; the gate passes on paired mean delta ≥ 0 AND
  trained mean ≥ the pinned comparator mean. Worst-streak
  (mean/max) and F-053 event counts reported beside, vs the
  comparator's 178/401 (20), 197/626 (40), 443/716 (100).
- A 40×40 gated miss fires the prereg's mixed-size trigger (owner
  routing first; the mixed recipe is a declared arm via addendum).

## Welfare (practice, owner 2026-09-26; stops ASYMMETRIC)

- Scouts-first per displaced size per seating: the band's first 3
  worlds at full ticks with the F-053 1,000-tick streak stop; any
  scout miss stops that leg and the driver — taken to the owner,
  never auto-continued.
- Every leg (20×20 included) runs with `--abort-streak 1000` armed;
  any abort stops that seating's battery, owner-routed.
- Welfare-cost line: each leg exposes 5 covered minds × 30 worlds ×
  20k ticks (3.0M cat-ticks); the battery is the certification
  requirement before any live seating, the stops above are the
  declared asymmetric remedy, and displaced sizes are scouted (3
  worlds) before each full leg.

## §9.5 dispersion read (K§4: INVESTIGATE, character not a bar)

Definition (Experiments' design, declared here): per tick, the five
kitties partition into connected components under Manhattan
distance ≤ 1 (adjacent or same tile); `together_share` per seat =
share of ticks spent in a component of size ≥ 2; `group_count` =
per-tick component count, averaged. Recorded natively in the trained
legs' rows at all three sizes. The comparator rows predate the field
— the scripted side of this read would need a comparator re-run and
is NOT run now (INVESTIGATE rows carry the trained character only,
labeled as unpaired).

## Swaps digest (report-only, after the gate reads)

Gen 1 practice carried over at Gen 2 scale: once the gate reads name
the export candidate, each alternate completed seed replaces one seat
of the candidate roster — 2 alternates × 5 seats = 10 legs, 20×20
only, band g2cmp, 30 × 20k, abort 1000 armed. Report-only (F-043:
the distress tail is a roster property; the digest reads cross-seed
mixtures without changing the declared deployment shape). Mixed-seed
DEPLOYMENT remains undeclared — adopting one would be a deviation
entry or a Gen 3 arm, per the owner-assessed options of 2026-10-20.

## Instruments changed for this battery (rule 5/6 before launch)

- `cert_harness_fog.py`: g2 seat spec (EntityPolicyV6 loader), schema
  keying (v5 408/39/55 vs v6 399/35/51), clock/deafen refusals for
  g2, provenance path generalization, dispersion accounting.
- `run_legs.py`: `--seating` passthrough (default scripted; scout
  gate filename keys off the seating tag).
- Kept behavior must stay green (test_run_legs, the harness guard
  files); new guards get declared-first mutate reds before launch.

## Raws

`results-raw/` in this directory (native checkout, never delete,
never commit): `scouts/` and `legs/` per seating via `--out-dir
results-raw/<seating>`.

## Correction (2026-10-21)

The Seatings section above calls one artifact in all five seats "the
CTDE-declared deployment shape (prereg R§7)". That misreads R§7: its
actor weight sharing is one of three TRAINING-time channels and says
nothing about deployment. The standing seating rule is F-044's five
distinct networks (owner 2026-09-16), which the owner kept on
2026-10-21 ("Let's train 3 more and run them all through the
certification process"; deviations entry 5). The uniform seatings
here are therefore all-copies stress reads of each network; the
certificate for the roster that would be seated is Phase C's
five-network rot2 (`RESULTS.md` §Phase C).
