# exp-006: the character generation (pre-registration)

**Status: DRAFT for owner review — freezes when phase-1 training
collection starts** (smoke runs on subset data exempt, exp-004
precedent). Deviations append-only, D-numbered, after freeze.
`[AT FREEZE]` marks values pinned when their measurements exist.

Findings relied on: F-007 (BC init necessary — re-established on this
class 2026-08-16), F-009 (instrument bounds), F-012 (measure in the
deployment composition, promoted), F-014/F-015 (re-baseline
obligations), F-018 (two-layer channel law), F-019 (leash
dose-response: the 0.04 knee, the venue shift, per-expression gate
floors), F-020 (trait prices are social prices; stage-3 mortality),
F-022 (demonstrations seed the channel), F-023 (dials are
listener-population properties), F-024 (entity attention carries),
F-025 (seating is culture-pairing), F-026 (the pre-fog channel null).

## 1. Question

Does the character generation — trait-spread-trained,
estimator-equipped, lineage-seeded — deliver a certifiable roster-5
world of five visible characters, with the first production lineage
preserving a personality on purpose?

## 2. Substrate (pinned)

Phase-1 world: the five locked trait sheets, sunbeam 7, 20×20,
roster 5, `kitty_slots` 3 (someone always unslotted — the estimator's
signal). Post-wall surface: obs 225 / menu 34 / head 16 / digest 15;
engine stamp `5d293c67…` (re-pin at freeze if main moves). Instrument
venv: `exp-006-character-gen/.venv`, binding built at the pinned
stamp, engine commit printed in every run manifest (the exp-005
lesson).

## 3. Family & dataset v5

family-gen v6 per the owner-decided spread design
(phase1-design-inputs.md §3, verdicts 2026-08-16): full-envelope
triangular-at-the-sheet sampling, off-rail, canonical share 1-in-3,
independent per-seat draws + corner stratum, random trios with
record-never-exclude QA (stress cells are data). Collection base =
served config + the three locked sheets (Miso/Biscuit/Kittybear) +
demonstrator seat(s); committed as `collect-config.toml` `[AT
FREEZE]`. Family size N ≡ 0 mod 18 (exact plan shares); N `[AT
FREEZE]`. Announce threshold T15 at collection (F-023: serving stays
T30). Collection budget: `[AT FREEZE]` — raised vs v4 per the 3a
verdict, multiplier proposed with measured collection costs.

**Price probe (3e)**: cell A pinned (`--traits pinned`), cell B the
spread design, matched budget; v4-battery clone recipe on each;
per-class fidelity, play/chase the canary (F-015 conditioning).
Decision rule `[AT FREEZE]`, proposal: spread may cost ≤ 2pp overall
masked act@1 and ≤ 4pp on play/chase vs cell A, else canonical share
rises (first fallback) or the box narrows (second).

QA riders: Here* mask-legal-but-voided rate measured during
collection (design-inputs §4b), reported with the acceptance record;
per-world welfare/distress stats recorded for the trio audit.

## 4. Arms

All arms: EntityPolicy (d64/4h/2L — F-024), A1 recipe, γ 0.998, 20M
ticks/run, BC init (F-007), team reward only (F-018 layer 2 guard),
maximum concurrency on the training box. Training seeds 1M+ band.

- **E1 — estimator ON** (2 seeds): aux head predicts every cat's
  need vector (CTDE supervision); per-pair calibration error logged
  and BANKED (the care-coupling program's pre-fog baseline,
  design-inputs §4c); aux weights retained in checkpoints (belief
  interventions run on checkpoints, never artifacts).
- **E0 — estimator OFF** (2 seeds): the control; identical
  otherwise. Registered comparison: welfare, channel metrics, and
  robustness across E1/E0 — "does predicting minds pay before fog."
- **L-04 — Biscuit 2.0 at β∞ = 0.04** (2 seeds): the measured knee
  (F-019). Anchor = playful scripted demonstrations collected
  POST-REBALANCE on the phase-1 config in healthy composition
  (anchors-follow-surfaces), production clone trained fresh; leash
  β0 = 0.5 annealed over 20% to the held β∞ (exp-005 recipe).
- **L-05 — Biscuit 2.0 at β∞ = 0.05** (2 seeds): the
  trajectory-safe dose; with L-04 gives the owner's requested
  observational set (four certified candidates, serial seating
  cheap post-cert).

No doter-2.0 arm: the doter minds carry by expansion (§5). No
per-kitty reward terms anywhere (F-011 archived clause via F-018).

## 5. Expansion candidates (derived, not trained)

Product's surface-expansion export (spec requested 2026-08-17) takes
attn-a1-s1, attn-a1-s3, and e004-a1-s2 onto the 225 surface. The
behavioral invariant is registered here as a gate input, in two
halves with two instruments (settled with Product 2026-08-17):

- **Structural, in the tool**: bijective weight placement (every
  source float provably at its mapped position), new head columns
  at-or-below the negative floor (never spuriously selected — mask
  legality cannot be the silencer, chirp and Here* are legal
  post-cutover), and ALL new input-side parameters exactly ZERO
  (type embeddings, digest-slot embeddings — deafness as a provable
  invariant, not an accident of seed; a future finetune that wants
  otherwise re-inits explicitly as a registered act).
- **Behavioral, in the battery**: forward parity on old dims ≤
  ~1e-5 logits vs the source, run in Experiments' numpy harness
  (independent reimplementation of both layouts — catches a wrong
  token map that a bijection check would bless), obs rows sampled
  from the archived pre-wall datasets. This parity leg is what
  licenses §7's identification of "expanded artifact" with "the
  source, embedded in the new surface."

Expanded artifacts are candidates like any other: new shas,
`-o4`-suffixed names, registry rows same-PR (provenance in the
recipe field; display unchanged), full battery. At cutover, sources
retire to policies/retired/ with rows kept, Superseded-by pointing
source → expanded successor (artifact lineage, not seat
inheritance — e004-a1-s2's successor seats at Clementine).

## 6. Seating plan (registered intent — seating itself awaits the
owner's direct word, as always)

Miso = expanded attn-a1-s1 · Pumpkin = expanded attn-a1-s3 ·
Kittybear = expanded attn-a1-s3 · **Clementine = expanded
e004-a1-s2** (the purr culture seated in the body that demands it) ·
**Biscuit = one certified lineage candidate**, the rest certified
alternates for serial observation (each swap = config change + G6
soak, no retraining). Cutover is `--fresh` (the wall's accepted
consequence; the current world ends at seating).

## 7. Gates (frozen before any candidate exists)

- **G1** zero fallbacks (in-process artifacts).
- **G2a** stress battery: bar 225, max(1, floor(0.05n)) exceedances,
  shapes iii/r3/r5 ON THE ACTUAL COMPOSITIONS (F-009/F-025);
  constitutional throughout: max_distress_age ≤ 150, floor_touches
  0.
- **G2b** hard floor: team welfare ≥ the fresh scripted anchor,
  re-derived against the actual cutover config at battery time
  (planning floor 0.9076, trait-screen corrected anchor).
- **G2c** team budget: candidate roster team ≥ reference composition
  − **0.005** (owner-declared 2026-08-17). Reference composition =
  the four expanded incumbents at their §6 seats + scripted
  needs_driven at Clementine's, same instrument, paired seeds.
- **G2d** seat-paired (D-003 norm), per-seat asymmetric
  (owner-declared). The pre-expansion selves never run in the
  battery: by §5's parity invariant the expanded artifacts ARE
  their sources on this surface, so every leg runs expanded
  artifacts natively, same-instrument, and "vs self" is realized
  as the G2c REFERENCE COMPOSITION — what the gate measures per
  seat is the company change, which is what actually varies:
  - carried seats (Miso/Pumpkin/Kittybear): welfare in the
    candidate roster ≥ same mind, same seat, in the reference
    composition − 0.006;
  - Clementine: ≥ scripted needs_driven at her seat − 0.006 (no
    incumbent — scripted-anchored by owner ruling);
  - **Biscuit: ≥ expanded e004-a1-s2 at Biscuit's seat (its
    reference-composition reading) − 0.030**
    (the owner's character budget: "we are EXPLICITLY trading
    welfare-optimal behavior for Biscuit behavior") — VALID ONLY
    WITH A G3 FINGERPRINT PASS. Budget without character is
    failure.
- **G3** lineage fingerprint gate (Biscuit candidates only),
  measured by the exp-005 probe ported to this surface, in the
  demonstration composition, ratios to the production anchor
  `[AT FREEZE]`, proposals from the measured 0.04 band:
  play_share ≥ 0.80×, time_near_critters ≥ 0.70×, bug_over_meal ≥
  0.70×, duet_initiation ≥ 0.50× (the lottery metric — gate
  per-candidate, F-019). The near-critters and bug floors exist
  because 0.03's two seeds demonstrated the venue shift they catch.
- **G4** registry rows (spec 034) in the same PR as every artifact.
- **G5** report-only: channel telemetry, estimator calibration
  curves, meow economies of the new generation (F-025 re-probe —
  meanings are per-generation).
- **G6** post-seating soak ≥ 48h, distribution-calibrated watch
  (v4 pattern), stateful distress tripwires; gates the keep.

## 8. Bands & instruments

Collection band `[AT FREEZE]` (fresh, above all prior bands);
fingerprint probe band `[AT FREEZE]` (fresh — 820k belongs to
exp-005's world); eval/stress bands per battery convention, declared
in the battery doc before verdicts. Instruments: family-gen v6,
bc-collect (post-wall build), the exp-006 venv binding, kitty-eval,
cert harness (post-wall port), fingerprint probe (post-wall port).
Every instrument prints its engine commit.

## 9. Riders

- Class-credit re-baseline + F-004 world-count bar re-derivation on
  the post-wall stamp BEFORE training-design finalization
  (F-013/F-014/F-015 fired triggers).
- Threshold dose-response re-measure at T {15, 20, 25, 30} with the
  trained generation (F-023's registered prediction: v5-trained
  listeners flatten the mixed/policy curves toward scripted).
- HereFood probe cell: enabled in one probe configuration, expected
  inert under global vision (F-026's prediction, pre-registered
  before fog overturns it).
- F-016 stays open-not-served (dials unchanged; noted per the
  register review).

## 10. Stop rules & discipline

Per-run §9.6-style welfare stop (welfare < 0.5 on 3 consecutive
probes → checkpoint, halt, deviation entry). No criterion weakens
after freeze; outcomes and deviations append-only. Selection rules
pin before per-candidate §7 numbers are read. Nothing seats without
the owner's direct word in the acting session.

## Deviations

(append-only after freeze)
