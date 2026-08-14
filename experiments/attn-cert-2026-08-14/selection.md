# Selection & certification protocol: the mixed attention roster

**Status: FROZEN 2026-08-14 (owner: "Approved").** Edits from here
land append-only in the Deviations appendix (D-numbered). Where this
doc and PIPELINE.md disagree, this doc wins for this certification.

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

**D-001 (2026-08-14, instrument).** kitty-eval cannot seat a mixed
multi-artifact roster (`--brain|--artifact` only), so G2/G3 run
through `cert_harness.py` — an env-chain harness (deviation-31 replay
precedent) with welfare.rs metric definitions transcribed (floor ≤
happiness.floor, low < 45.0, distress-age = per-(kitty,need) flag
streak) and team Nash read from the engine's own reward. Validation
cell (attn-A1-s1 ×4, seed 870001 × 20k) vs kitty-eval: structural
metrics agree (mda 0/0, floor 0/0, low 0/0); trajectories diverge
slightly via the recorded torch-vs-Rust forward gap (~1.8e-5 logits →
greedy near-tie flips): |Δnash| = 0.0012, |Δmean-happiness| ≤ 0.13.
Consequence and mitigation: G2c-budget and G2d are evaluated
paired SAME-instrument (candidate and incumbent both through the
harness — forward bias cancels); the scripted hard floor comes from
kitty-eval natively (fresh anchor: 0.9056 on seed 870001); no gate
compares across instruments. If any nonzero max_distress_age appears
in the battery, the streak convention gets cross-checked against a
kitty-eval homogeneous stress cell before verdicts are read.

**D-002 (2026-08-14, owner approved).** G2b's "max distress age == 0"
was anchored to a stale record: the incumbent's own certification
carried 46/0/405 across stress shapes, and its fresh paired runs here
measure 17 (eval) / 3 (stress). The streak convention was verified
against engine source (in_distress = at-or-above threshold;
distress_since age ≡ flag-streak length) before any verdict was read.
G2b re-anchors to the constitutional bound: **max distress age ≤ 150**
on every run. Candidate: worst 77 (eval) / 88 (stress) → PASS.

**D-003 (2026-08-14, owner approved).** G2d compared fixed seats to a
rotation-pooled screen prior — an accounting error exposed by the
battery and explained by the Pumpkin diagnosis (`pumpkin_diag.py` +
`pumpkin-diag.json`): the eat-0.8 trait taxes ANY occupant ~1 point
(scripted −0.95, incumbent −1.06, s3 −0.96 vs its own Kittybear
sibling), the groomer carries that seat cheapest of all three models
(s1 −1.1, s2 −1.25 with the diagnosis's only distress ticks), the
candidate seating maximizes roster welfare among the three seatings
probed, and prosociality survives the hard seat (groom 10.4% vs
12.2%). G2d re-anchors **seat-paired**: every seat ≥ the incumbent at
the SAME seat − 0.006. Measured: Miso +0.04, Biscuit +0.15, Pumpkin
−0.49, Kittybear −0.41 → PASS. Standing consequence (owner's word:
"let's examine it this way going forward"): seat-paired accounting is
the norm for trait-differentiated seats in future certifications.

## Verdict (2026-08-14): CERTIFIED

G1 ✓ · G2a ✓ · G2b ✓ (per D-002) · G2c floor ✓ (+0.042 over 0.9058)
· G2c budget ✓ (−0.0018 eval / −0.0023 stress vs declared 0.005;
eval reads as parity) · G2d ✓ (per D-003) · G3 ✓ (0 exceedances of
bar 225; low_share ≤ 0.34% vs 5%). G4/G5 report-only entries and the
telemetry battery accompany the seating record. **Seating awaits the
owner's direct word (§5); G6 soak gates the keep thereafter.**
