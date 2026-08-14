# Selection & certification protocol: the mixed attention roster

**Status: DRAFT for owner review — freezes when the first
certification instrument runs.** After freeze, edits land append-only
in the Deviations appendix (D-numbered). Where this doc and PIPELINE.md
disagree, this doc wins for this certification once frozen.

## 1. The candidate (pinned)

One candidate, chosen by the owner (2026-08-14) on screen-grade
evidence — a **seating map**, not a policy:

| seat | kitty | model | artifact (v3) | sha256 |
|---|---|---|---|---|
| 1 | Miso | attn-A1-s1 "the cuddler" | `attn-A1-s1.ckpolicy` | `d8e310215d7d…` |
| 2 | Biscuit | attn-A1-s2 "the loner" | `attn-A1-s2.ckpolicy` | `f1a198a03b99…` |
| 3 | Pumpkin | attn-A1-s3 "the groomer" | `attn-A1-s3.ckpolicy` | `dfef0ec29161…` |
| 4 | Kittybear | attn-A1-s3 "the groomer" | `attn-A1-s3.ckpolicy` | `dfef0ec29161…` |

Artifacts are the three attention-PPO finals (A1 recipe, 20M ticks,
seeds 1–3; `experiments/attn-ppo-2026-08-13/`), exported via the
spec-030 certified path. Byte-identity by sha; never re-exported.
Greedy selection (the deployed mode). The certified object is THIS
map — model×trait interactions make any other assignment a different
candidate (F-009: roster and seating are held-fixed dimensions).

**Selection rationale (recorded, not re-litigated):** the owner chose
composition over single-model uniformity for personality texture. The
screen-grade priors (all in `experiments/attn-meow-econ-2026-08-14/`
and `attn-ppo-2026-08-13/results.md`): welfare parity with the
incumbent at the ~0.95 ceiling; s3's kin dose-response (94.87 kin /
94.51 one sibling / 93.93 alone) — hence exactly two s3 seats; no
isolate in the pair census; the grooming gift economy with one
reciprocal kin bond. The known accepted cost: s3 seats run ~0.4 below
their all-kin ceiling; channel volume ~3× the incumbent world
(owner-accepted; presentation handled client-side).

## 2. Held fixed for the whole battery

- Engine: defaults stamp `412d00e2a92e…` (unchanged since the
  incumbent's certification — spec 031 changed rule semantics, not
  defaults), code at the commit this doc freezes at. Served config
  `cloudkitty.toml` as-is, **`sleep_relief_sunbeam` = 8.0**: the
  screened 7-re-pin is DEFERRED to the next generation's re-baseline
  and must not land mid-certification (a config change voids this
  battery — F-013 mortality).
- Baseline runs are **paired on identical seeds** with the incumbent
  seating (e004-a1-s2 ×4) on the same binary, same bands, same
  instrument — freshly run, never quoted from prior records.
- Bands per the §6-lineage ledger: eval 870001–870030, stress
  880001–880030, both 20,000 ticks. Every claim inherits (horizon,
  world = served, roster = this seating, band, greedy) — F-009.

## 3. Gates (pass/fail pinned before any instrument runs)

- **G1 — load & serve smoke.** Each artifact loads under the current
  binary; `kitty-eval --artifact` runs exit 0 with **zero fallbacks**
  (exit 2 fails the gate). The CI parity gate already pins forward
  semantics; no re-derivation here.
- **G2 — welfare certification** (eval band, 30 seeds × 20k, this
  seating vs incumbent paired):
  - G2a: every constitutional welfare bound holds on every run (the
    §9.3-lineage battery as the harness encodes it).
  - G2b: **max unresolved distress age == 0 on all 30 runs** (the
    incumbent's record on this band; band-property caveat noted).
  - G2c — two layers (the structure, not the numbers, is the
    standing precedent; owner decision 2026-08-14 with the LLM-seat
    future explicitly in mind):
    - **Hard floor (never moves across seatings)**: paired team Nash
      ≥ the same-battery scripted-baseline anchor (needs_driven at
      every seat, paired seeds; historical anchor ≈ 0.9069). The
      durable invariant every future seating — including an eventual
      LLM cat — must clear: no seating makes the world worse than
      the sanctuary's scripted guarantee.
    - **Declared budget (per-seating)**: paired team Nash ≥ incumbent
      − **0.005** — the price the owner accepts for personality
      texture, declared before the bill (screens predict ≈ 0.003).
      Re-declared per seating in its own selection doc; never
      inherited. Differences within **0.002** read as parity (the
      derived noise floor) in all reporting.
  - G2d: worst-seat gate — min per-kitty welfare component ≥ the
    screen prior for that seat's model (s3 seats: 0.9451) − 0.002
    noise, AND above the scripted-baseline floor. "The s3 seats must
    not do worse than the cost the owner accepted," not "must match
    a cuddler."
- **G3 — stress** (stress band, 30 seeds × 20k, this seating): the
  settled §9.2 machinery — bar = distress line ÷ fastest rise
  (**225** at 90/0.4); exceedances ≤ max(1, floor(0.05·n)) = 1 of
  30; low-welfare share ≤ 5%.
- **G4 — roster-OOD secondary screen** (deviation-31 pattern,
  report-only, named): compiled 3-kitty world seated [s1, s2, s3].
  Not a gate — F-010 context for the record. (Note: 3 kitty slots
  always full at roster 4; the attention encoding additionally
  handles vacancy by mask — reported, not gated.)
- **G5 — kitty-eval smoke** (demoted instrument, report-only):
  `--roster both` per artifact; numbers recorded as archaeology
  alongside, never as a bar.
- **G6 — soak** (post-seating, gates the *keep*, not the seat): ≥48h
  supervised on the box, stage-1 protocol (happiness band vs the
  probe prior ~94.5–95.2, distress events ≈ 0, no degenerate
  pairing), plus channel and personality telemetry vs the lab priors.
  Rollback = the incumbent config stays registered untouched; any
  soak failure reverts on the owner's word.

**Decision rule:** all of G1–G3 pass → seating proceeds (mechanics
§5). Any failure → stop, no gate-shopping; findings written up, the
candidate returns to the bench, deviations appendix records why.

## 4. Report-only telemetry (no gates, feeds the record)

Meow/1k by kind by seat; the directed grooming graph; pile census;
water occupancy by activity (exp-003 continuity — measured on THIS
roster, solo numbers do not transfer); cosleep-on-beam / conduction
shares (spec-031 census). These become the priors for the
**deployed-world purrsonality entry** (the register's reserved
section) after G6.

## 5. Seating mechanics

**Single cutover, not staged.** The staged-restart principle was
written for converting one seat among scripted incumbents; here every
intermediate composition (attention seeds mixed with MLP incumbents)
is an uncertified composition never probed — staging through them
certifies nothing and risks exactly the cross-culture effects this
battery cannot see. One restart to the full certified seating,
incumbent config registered for instant rollback. **Production
seating happens only on the owner's direct word in the acting
session** (standing rule; this document is not that word).

On seating: policies/README.md gains the certification record
(hashes, gates, numbers); purrsonality.md gains the deployed-world
entry after soak; CHANGELOG gets its line.

## 6. Post-certification obligations

The F-015/F-013 standing triggers (class-credit re-measure on any
engine change) are untouched by this seating. The sunbeam 7-re-pin,
dataset-v5, threshold re-measure, and estimator-generation work all
queue behind it exactly as recorded in the roadmap docs.

**Forward note for the LLM-seat era (owner direction, 2026-08-14):**
G1's zero-fallback rule is correct for in-process artifacts and WRONG
for a future plugin/LLM seat, where Article IV fallback is an expected
operating mode, not brokenness. That seating's protocol will replace
zero-fallbacks with a registered fallback-rate band plus a
fallback-behavior welfare check — designed then, flagged now so the
change is anticipated rather than improvised. The G2c two-layer
structure (scripted-baseline hard floor + per-seating declared
budget) is what makes such a seat certifiable at all.

## Deviations

(append-only after freeze)
