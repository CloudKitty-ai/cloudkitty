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
   probe 300, F-053 1,000, 20M cap) — DONE 2026-10-21. BC clone DONE
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
   ACCEPT / ITERATE rung (iv) / HOLD owner-routed — RULED 2026-10-19
   ("We'll wait for 065 to land, and go with iteration"): one
   combined second mix, rung (iv) ε-mixture collected at once (40
   rollouts, seeds 1095201–1095240) + true rung (ii) on spec 065's
   landing (landed 5fb27cfb same day; IN-wide/IN-grave 50 rollouts,
   seeds 1095241–1095290, unaltered trunk config). ROUND 2 EXECUTED
   2026-10-19 (results in the arc RESULTS.md §round 2): coverage
   still met (2.464% / 6.670% / span 156), retrain EV 0.8286
   no-regression PASS, mechanism PASS and deepened (−1.65 → −29.87),
   ε-0.3 PASS its null (the regime the mix targeted); ε-0.1 now
   FAILS its null and the random leg still misses the per-world bar
   (−0.204 on one world; pooled 0.533, third straight pooled climb).
   Acceptance not met as declared (2 of 4 legs);
   ACCEPT / ITERATE / HOLD owner-routed — her word 2026-10-19 "yes,
   relay to Professor", then "Ruled as recommended by Professor":
   INSTRUMENT REPAIR (MITIGATION.md §Round 3 + addendum): n_eff
   measured on all six legs (per-world block nulls, seed-exact
   regeneration), null-width ceiling 0.3 declared two-sided —
   retroactive UNINFORMATIVE labels kill the ε flip-flop (every
   informative ε read through round 2 was a PASS); bars resized
   (m,k)=(10,7) from measured SE 0.166. ROUND-3 READS at 10 fresh
   worlds/leg (870031/34/37): random FAIL informative (4/10 at bar,
   pooled 0.202), ε0.1 FAIL informative (0.108 < p99 0.177), ε0.3
   UNINFORMATIVE (6/10 qualifying, re-run owed), mechanism PASS
   stands (−29.87). The defect moved back into the object: per-world
   ρ spans ~6 SE (+0.778 to −0.519 across legs) — real world-level
   heterogeneity of binding — DIAGNOSED on her word ("run it") to a
   SECOND instrument artifact: the censored-MC remaining-horizon ramp
   owns the ε targets at 4k (R² 0.70–0.96) and the "heterogeneity"
   was its share varying by world; detrended, genuine binding is
   positive 9/10. ROUND 4 (her "Agreed on both" + recollect-not-
   salvage + "Ok, let's run Professor's sequence"; Professor reviewed
   twice): honest geometry 6k/3500, 92-rollout recollection (band
   1095301–1095400; 4k rungs poisoned for training), uniform ≥3500
   censoring, re-derived baseline 0.8746. RESULTS (19a3c5da +
   82e85564): no-regression PASS with first EV IMPROVEMENT (0.8818),
   mechanism PASS −46.09, random leg PASS informative (all 10 worlds
   positive, pooled 0.522, sign-uniform; re-scored under the
   pinned-amplitude trip amendment 28f57999 — the declared free-R²
   trip was under-specified, voided legs for genuine welfare drift),
   ε legs descriptive-only EARNED (3/10 qualifying at honest
   geometry; ε0.1 descriptively positive), contrast gate
   STRUCTURALLY UNINFORMATIVE (paired play read fired the benign
   branch — critic right, 55.2% p 0.165; NO kind has a realized
   near-pair direction at these horizons; play "inversion"
   dissolved). Every informative read PASSES.
   PROBE-THEN-ACCEPT RULED: "accept" (owner 2026-10-19) — critic
   PINNED (critic-g2-ext3, sha bd394a96...e20777); deviations entry 2
   CLOSED. PPO launched on "Launch it" (2026-10-19, 1318804e):
   trunk-s1 and trunk-s2 plateau-complete 2026-10-20, welfare-clean;
   trunk-s3 HALTED at u249 by the frozen §6 probe-distress stop
   (deviations entry 3, RULED "A": replacement seed); trunk-s4
   plateau-complete 2026-10-20, entry 3 CLOSED. Frozen §5's three
   seeds are s1/s2/s4. Seating seeds (entry 5, owner "Let's train 3
   more and run them all through the certification process"):
   trunk-s5 HALTED at u199 by the same stop (entry 6, RULED "Yes,
   keep s2 and don't replace s5", CLOSED); s6 and s7 plateau-complete
   2026-10-21. Readouts in the arc RESULTS.md.
8. **Cert battery** — paired-strict vs comparator, replication
   valve (§6) — RAN 2026-10-20; DONE 2026-10-21, FIVE-NETWORK ROSTER rot2 CERTIFIED (Miso s2, Biscuit s4, Pumpkin s6, Kittybear s7, Clementine s1: 20×20 +5.566 and 40×40 +4.594 in 30/30 worlds, no stops; 100×100 characterize +7.187, no aborts, worst 859 = s7 water parking at Kittybear) (`gen2-cert-battery-2026-10-20/`): uniform rosters all PASS both happiness gates; s2 roster-wide lock at 20×20 (deviations entry 4: its declared stop was not enforced; (b) RULED 2026-10-21 "Yes, keep s2 and don't replace s5"; (a) post-stop citation still OPEN); the F-044 seating rule (five distinct networks) KEPT by the owner (entry 5), so the uniform seatings are all-copies stress reads (battery DECLARATION §Correction); mixed-roster test (3 seat-balanced rosters, 180 worlds) no measurable welfare cost, tail improved, no stops. Phase C composition RULED 2026-10-21: "Rot 2, run the analysis after we certify it" (0f1fadd4). Standing analysis of the certified roster DONE (34062ded, `seating-analysis-g2-2026-10-21/`); its activity and partner columns CORRECTED 2026-10-21 (owner: "Those eat and drink numbers look suspiciously low (e. g. 0.007 for biscuit)"; ruling "1 for gen 2"): the readers dropped every scene's last tick; rot2 re-collected exactly on byte-identical worlds (Amendment 1, 9920a6f3..b3978398), Gen 1 re-read as ranges (98732453); the certificate is unaffected (its gates read happiness and distress).
9. **Three-leg consent BC comparison** (9 trainings; decision grid
   in `gen2-consent-design-2026-10-17.md` appendix; deployed-episode
   consent line DEFERRED to this readout) — PENDING.
10. **Arms per §8 order + declared reads §9** — PENDING (mini-friend
    phases, §8.4 closure, §8.5 radii, ostrich/approach/outcome
    instruments).
11. **Close** — timeline freezes; Gen 3 handoff items below.

## Outstanding owner items

- Step 9, the three-leg consent BC comparison — waits on her word.
- Deviations entry 4 (a): may post-stop rows be cited.
- rot2 policy export for serving — waits on her word.
- The cert harness's own reads of the end-of-tick activity flag
  (eat/drink tick counts, sleep/play accounting, streak shape,
  holding): reported, not fixed; no gate reads them
  (`seating-analysis-g2-2026-10-21/RESULTS.md` §Correction).
- Deployed/PPO-episode consent line — at the three-leg readout.
- 057-triggered Gen 2 re-record — waits on her word
  (`fog-gen1-timeline` note).
- #392 deferred behind Gen 2+3.
- Post-cert analysis plan RULED 2026-10-21 ("Recommendation accepted",
  on the owner's own list "where play increase comes from" and
  "Accuracy of mini models"): (1) the play decomposition, reads of
  existing raws plus a scripted-teacher run on the rot2 worlds under
  the Gen 1 dials, own arc with a DECLARATION; (3) the owed cheap
  reads: §9.5 dispersion at 100×100, the battery DECLARATION's swaps
  digest (run or deviate), §8.5's "gap moves with size" trigger
  recorded, §9.4 partner_absent re-read on the trained roster, §9.8
  F-050 revisit, the unread s4/s7 tails, the Gen 2 FINDINGS entries,
  entry 4 (a); THEN mini-friend Phase 1 (§8.3, the "accuracy" read,
  stratified, never overall); THEN step 9 and the remaining §8 arms
  decided with those results in hand. Skipping any arm is a roadmap
  adjustment recorded in the deviations ledger.
  STATUS 2026-10-21: (1) play decomposition DONE
  (`play-decomposition-g2-2026-10-21/`, 2c1cae0f, gate PASS): the rise
  is teacher (+0.091) and training (+0.166), not world (−0.004); the
  roster plays 0.012 short of its teacher with the comfort rule
  loosened and consent off; extra play is slack-time play (less onset
  pressure than the teacher), out of idle moving and rest; play's own
  need carries 14–22% of the happiness gain. (3) DONE in
  `gen2-cert-battery-2026-10-20/RESULTS.md` §Owed reads (d541d55a, gate
  PASS): §9.5 dispersion at all sizes; §8.5 trigger recorded (gap
  +5.566 / +4.594 / +7.187, not flat, no margin declared: whether the
  displaced-size radius cell runs is HER CALL); §9.8 F-050 revisit
  (placement 0.416/0.533/0.613 vs 0.387/0.472/0.538; F-050, doctrine
  rule 7 and the GEN2-INPUTS shelf carry dated addenda; the density
  half stays unmeasured, one density in Gen 2). STILL OPEN from (3):
  the swaps digest (Experiments proposes a deviation entry: under the
  F-044 five-distinct-networks roster every completed seed is seated,
  so no alternate exists to swap in; her word); §9.4 partner_absent
  re-read (its instrument polls the live server, so it waits behind the
  rot2 export and deploy); the s4/s7 unread tails; the Gen 2 FINDINGS
  entries; entry 4 (a).

## Flagged follow-ups (owner's word to start)

- Relief just beyond vision (owner 2026-10-21: "Let's flag this for a
  deep follow up"; she suggests a round before Gen 3): the 905029
  search-latency failure and the scripted 20×20 holds share one
  structure that wider vision masks; she wants the cats to solve it
  organically. Her sequencing (same day): fix it in the teacher before
  any training-side attempt; a bug or minor fix becomes Gen 2a, a
  structural cause goes straight to Gen 3 (the tiered-needs teacher),
  iterated until the behavior is gone. Test sketch: lower vision on 100×100.
  Evidence and design questions:
  `vision-search-followup-inputs-2026-10-21.md`.

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
