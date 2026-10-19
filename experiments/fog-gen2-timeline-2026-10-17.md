# Fog Gen 2: sequencing timeline
## (Opened 2026-10-17 at the freeze sitting, per the generation
## practice — owner 2026-09-22; the tracker, not the design record.)

Design lives in the prereg (`gen2-prereg-skeleton-2026-10-09.md`,
superseded by the frozen PREREG at freeze), standing texts in
`WELFARE-STANDING.md`, claims in `FINDINGS.md`, evidence in the
experiment RESULTS files; this file points at them. Freezes in one
commit at the generation's close.

Goal: train the first hidden-needs generation (schema v6, fog +
hidden needs, one parameterized teacher, consent engine-validated
target-side) and certify it paired-strict against the realized
scripted comparator; the mini-friend arm phases and the three-leg
consent BC comparison ride the trunk.

## Rulings record

- Kickoff + scope: `gen2-kickoff-rulings-2026-10-07.md` (#389),
  `gen2-sitting-rulings-2026-10-08.md` (S§), #390 package world.
- Freeze sitting 2026-10-17 (agenda `gen2-freeze-agenda-2026-10-13.md`):
  A/B via pre-freeze work; C bites 1–3 (36bd53e3, 45e506f3, 64d71389);
  D bites 1–2 (ed7d7400, 43f50e2f); E all five blocks + seven
  Professor pins (c36ed5b9 — text (b) flow trigger landed in
  WELFARE-STANDING.md); trigger-bin restate + semantic anchor
  (anchor read 0fd90eba, restate pin in §9.2 rider (a)).
- Consent arc: `gen2-consent-design-2026-10-17.md` (three-leg
  design + decision grid); dial rulings in §4 of the skeleton.

## Steps, gates, status

1. **Product specs land** — DONE. 058 schema v6; teacher rework +
   consent re-key; 061 stuck detector (dark); 062 engine-drawn
   starts; #459 label_proposed; 063 friend-ward drift (flag off,
   screened null under the law, v4 tail rescue on record); 064
   waypoint start (flag off, screened null, owner "Agreed, default
   off"). Dispersion C2 SHELVED on her word.
2. **Readers on schema v6** — DONE (bc-collect ported, schema_check
   tranches, corpus readers, dial-draw extension d2f71897).
3. **Scripted comparator legs** — DONE, realized numbers pinned in
   §7 (`gen2-comparator-legs-2026-10-14/RESULTS.md`): law table
   20/40/100 under the vision law, zero F-053; v4 record kept.
4. **Prereg FREEZE** — DONE 2026-10-17 (owner "Do it"):
   `gen2-prereg-2026-10-17.md` is THE prereg; collection cites it.
   Copy-check gate: round 1 FAIL (vocabulary arming missing from
   the world toml vs S§7 — fixed, battery re-run byte-identical,
   90/90 rows; probe-envelope numbers uncommitted — section added)
   → round 2 PASS, fresh subagent each. Deviations ledger open:
   `gen2-deviations.md`.
5. **Pilot collection** (30 rollouts) — DONE 2026-10-17 (owner
   "Start the pilot"): placement 0.4254 PASS, here-word density
   17.10% PASS, mask-mismatch 0.406% composition measured
   (`gen2-collection-driver-2026-10-14/RESULTS.md`). Starts check
   DONE 2026-10-18 (owner "Starts check first"): golden byte-exact
   + engine echo + driver replay 30/30.
6. **Full collection** (100 rollouts; mix 0.6 served / 0.12
   enrichment / 0.28 traits; dial draws per §4) — DONE 2026-10-18:
   placement 0.4341 PASS, density 17.23% PASS, mask-mismatch
   per-class uniformity PASS, starts check 100/100, classes
   60/12/28 exact (`results-raw/full-100/`). §8.1 chatter-floor
   re-measure DONE 2026-10-18 (owner "Proceed"): the no-seeding
   floor is 0 free-register emissions per 1k on all three comparator
   legs (0 of ~2.99M rows each) and 0 in the full corpus
   (0/9,960,292); here-word channel alive in the same histograms
   (`gen2-comparator-legs-2026-10-14/RESULTS.md` §Chatter floor).
7. **Trunk training** (BC+PPO, 3 seeds; §5 recipe carried; stops:
   probe 300, F-053 1,000, 20M cap) — IN FLIGHT. BC clone DONE
   2026-10-18 (plateau at epoch 112, best 102: val 0.8330, act@1
   0.8608, msg@1 0.9763; consent swap 136,699 + 389 kept-applied
   per deviations entry 1; `gen2-trunk-training-2026-10-18/
   RESULTS.md`), init_clone PINNED. Critic trained same day (val EV
   0.8351, best epoch 3) but the #365 acceptance probe FAILED its
   Spearman bar (pooled rho −0.026 vs ≥ 0.3; finite + in-band PASS;
   rank-blind on far-off-distribution states while strong
   on-distribution). Professor second opinion relayed (her word);
   investigation reads run on her word 2026-10-18: welfare features
   UNBOUND (needs inert, distress flags wrong-sign +17.5) and the
   eps-on-clone re-probes miss the declared per-world benign line
   (best world rho 0.284) — RULED 2026-10-18 (owner "Agreed,
   mitigate under this design"): MITIGATE per the Professor
   corpus-extension design, deviations entry 2 (coverage in outcome
   currency, cheapest-welfare-cost-first rungs, contrast pairing,
   binding-not-volume acceptance). Mitigation EXECUTED 2026-10-18
   (declaration MITIGATION.md + results in the arc RESULTS.md): all
   coverage targets met (below-45 2.647%, 45–70 6.835%, span 156,
   pairs every kind), retrain EV 0.8249 no-regression PASS,
   mechanism test PASS (distress sign repaired +17.54 → −1.65),
   ε-0.1 leg PASS; random leg misses the per-world bar (one world
   0.061; pooled 0.418 clears the ORIGINAL #365 bar) and ε-0.3
   fails its null — acceptance not met as declared;
   ACCEPT / ITERATE rung (iv) / HOLD owner-routed, pending her
   word; then the PPO launch card (her word) before any seed
   burns.
8. **Cert battery** — paired-strict vs comparator, replication
   valve (§6) — PENDING.
9. **Three-leg consent BC comparison** (9 trainings; decision grid
   in `gen2-consent-design-2026-10-17.md` appendix; deployed-episode
   consent line DEFERRED to this readout) — PENDING.
10. **Arms per §8 order + declared reads §9** — PENDING (mini-friend
    phases, §8.4 closure, §8.5 radii, ostrich/approach/outcome
    instruments).
11. **Close** — timeline freezes; Gen 3 handoff items below.

## Outstanding owner items

- The freeze word on the assembled skeleton (step 4).
- Deployed/PPO-episode consent line — at the three-leg readout.
- 057-triggered Gen 2 re-record — waits on her word
  (`fog-gen1-timeline` note).
- #392 deferred behind Gen 2+3.

## Banked for Gen 3 (pointers)

Critic-corpus prevention trio (deviations entry 2, 2026-10-18;
prereg-amendment candidates at the Gen 3 freeze): corpus-adequacy
gate before training; inherited constants re-derived at freeze; the
collection-declaration question "what will this critic be asked to
evaluate that this collection policy never produces?".

`gen3-roadmap-inputs-2026-10-04.md` addenda: favourites re-screen on
the stratified stack; bin-edge re-anchor + bridge (addendum 3);
play-demonstration refresher; vision-law measurements; 064 flag-on
default candidate; 063 drift as robustness-knob candidate; C2 reopen
carries the comparator re-run sequencing note. Teacher polish (owner
2026-10-18 "Keep default, add teacher polish note to gen3", on
deviations entry 1): the scripted teacher's ladder skips
partner-targeted proposals while inside its own activity minimum —
389/137,088 Gen 2 refusal rows were doubly-blocked mid-rest play
proposals (mask collapsed to RestSolo); harmless here (zero
action-head gradient, measured), but a Gen 3 teacher change lands
before its collection, Product's lane on her kickoff.

## Standing welfare machinery

Scouts-first on displaced sizes (never a veto); F-053 1,000-tick
line armed everywhere; asymmetric stops; paired-strict cert gate;
WELFARE-STANDING texts (a)–(c) incl. the 2026-10-17 flow trigger;
margin family 1.5× / min-n 200 across the §8/§9 instruments.
