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

- Spec 066 retrofit of the seven committed initial_needs configs (W, G,
  P1–P5): RULED 2026-10-26 ("Option 1 for the retrofit"); the scout
  checks read provenance on the recorded bytes since 304221b1; the
  files moved in Product's PR #469 (merge 3ba039c4); landed sha256s
  recorded in `gen2-deviations.md` entry 14, the three checks green and
  byte-identical on the landed tree, make_configs.py taught the table
  (b92b41af). CLOSED 2026-10-26. Standing trap: the arc binding
  (a2e8d044) refuses the retrofitted files (unknown key); collection is
  closed, no run owed.
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
  OWNER 2026-10-21, the three calls, verbatim: "Call 1: run it / Call
  2: can we train 3 extra seeds while we run the vision radius work? /
  Call 3: I was planning on waiting on seating on prod until we have
  the mini models working. So wait". Call 1 DONE 2026-10-22
  (`radius-cell-g2-2026-10-21/`, declaration cd846eac before data;
  RESULTS gated): at 40×40 with the radius one step below the law the
  paired gap is +5.800 ± 0.860 against the law's +4.594 ± 0.451 (gap
  difference +1.206 ± 0.941, 28/30 worlds); the scripted teacher gains
  1.294 from the wider radius, the frozen roster 0.088 — the fall
  between the cert legs travelled with the radius, on the teacher's
  side; descriptive, the certificate stands; all scouts and legs clean.
  Call 2 is a question, answered 2026-10-22 (yes, cheap: ~3.3 h per
  seed, three in parallel as s5–s7 ran); then RULED 2026-10-22,
  verbatim: "Train the additional seeds so we can run the swaps
  digest" → deviations entry 7 (04f0bce5): trunk-s8/s9/s10, run
  indices 103–105, stripes claimed, pinned recipe and binding,
  ALTERNATES for the digest only; launched 2026-10-22T05:40Z, three in
  parallel. s8 HALTED ~06:04Z by the frozen §6 probe-distress stop
  (streak 392 on world 40002 at u299; deviations entry 8, closed by
  entry 7's terms: no legs, no automatic replacement); REPLACED by
  s11 on her word ("Replace s8 just in case.", entry 8 ruling,
  launched 06:28Z); s11 HALTED ~06:35Z at u99 on probe world 40003
  (streak 371; entry 9, closed by entry 7's terms; a further
  replacement is her call). Four of eleven same-recipe seeds have
  tripped the §6 stop, all inside 1M ticks. s9 and s10 PLATEAU-COMPLETE
  ~09:20Z (finals 6feaa9d5 / ab194dd5). SWAPS DIGEST DONE 2026-10-22
  (battery RESULTS §"Swaps digest", gated; SWAPS-DECLARATION.md): ten
  legs, all clean; every one-seat swap within 0.3 of rot2 (pooled
  −0.083 ± 0.138 per world); the change sits in the swapped seat
  (Pumpkin's the one seat both alternates improve, Kittybear's where
  both lose most); 6 crossings ≥ 150, 0 in the swapped seat, four of
  them world 905029 — F-043 holds for Gen 2 (dated addendum). The
  step-8 declaration's last open item is closed; mixed-seed
  deployment stays undeclared. The digest runs 20×20 with every completion as an
  alternate once they end. Call 3: §9.4 partner_absent WAITS behind
  the mini models and the prod seating, her ruling.
  TAIL READS: owner 2026-10-22 "Run the tail reads" → battery RESULTS
  §"s4/s7 tail reads" (reader cedcd37b declared before replay): six
  worlds replayed with a per-seat stop at 100 ticks; s7's two unread
  tails are water parking, pure (six of six s7 tails now); s4's four
  are not that habit: a group HOLD at 20×20 (Miso and Biscuit, water
  out of sight), two cuddle tails pacing alone at 40×40, one parked
  mix. The first replay pass was lost to a serialisation error after
  running, so the replays ran twice (disclosed in the section).
  MINI-FRIEND PHASE 1 (§8.3) STARTED 2026-10-22: owner "Fix the stale
  draft and go as declared" to `minifriend-phase1-2026-10-22/
  DECLARATION.md` (its three open choices stand: one belief-state
  architecture; grave-start set G as the conditional fail-closed
  coverage remedy; a separate arc binding). The early §6 stops (4 of
  11 seeds) are SKIPPED on her word the same day ("Skip it"): the
  halting probes are already on disk, the shape would be a barely
  trained policy's, and no current decision turns on it. Step 1 DONE:
  arc venv + binding from main a2e8d044 (`BINDING.md`: engine delta =
  spec 065 only, gated on the section being present), the collector's
  `--save-obs` + `needs0/hap0` with the start-of-tick guard, the
  strata module with its edge guard; W/G seed sub-band 1095401–1095450
  claimed (the critic's IN rows are held by kept raws). PHASE 1 DONE
  2026-10-23 (`minifriend-phase1-2026-10-22/RESULTS.md`, gate PASS
  round 2): L 10 worlds all EQUAL to the certified battery (the arc
  binding reproduces the certified engine), W 25 and G 25 clean (0
  aborts, worst streak 756); GRAVE mind-visible after G 664 / 746 /
  170 / 671 / 316, Pumpkin's INSUFFICIENT COVERAGE by the fail-closed
  rule; heads 7,807 params. RE-READ 2026-10-23 after a retrain with
  bath downweighted (the first pass fitted bath at weight 1 against
  the prereg's "excluded/downweighted"; caught by the F-064 copy
  check; deviations entry 10; first read superseded at d0de3213): RMS
  5.3 need points in sight in common states, 25 in grave states
  (baselines 53); NF carries the ostrich signature on three of four
  covered friends (pooled grave bias −3.8, common ≈ 0), DR removes the
  pooled optimism (+1.7) for 7.5 points² of common error and is pooled
  worse on grave loss (NF/DR 0.944); dissolution test NOT passed on
  one friend (Miso's NF grave loss exceeds 1.10 × DR by 96.76 against
  an SD of 79.56; Biscuit 35% better under NF): the NF/DR tension is
  friend-specific and narrow. Phase 2 head choice is HER CALL with
  this read in hand (the declaration licenses head choice only).
  FINDINGS F-064 minted from the re-read (copy-check gated).
  PHASE 1b DECLARED 2026-10-23 (owner the same day: per-cat grave
  states + three head sizes; `minifriend-phase1b-2026-10-23/
  DECLARATION.md`, deviations entry 11): sets P1..P5 (one friend grave
  at reset per world via spec 065 per-kitty initial needs, 20 worlds
  per friend, seeds 1095451–1095550, extension blocks reserved) and
  widths 12 / 24 / 48 (the 48 an over-cap probe) × NF / DR × 3 seeds;
  reads R1b–R6b (per-cat grave accuracy, size ratios with a READ rule,
  the all-grave confound G/P). Her go 2026-10-23 ("No need to change
  the declaration. Let's run this as proposed"); 100 P worlds, 0
  aborts, every friend over min-n (extension not fired); 18 heads;
  RESULTS gated (round 5 PASS) → F-065: per-cat grave about half
  again as hard as the all-grave worlds (G/P 0.651 at width 24),
  width monotone on every cell and not grave-specific (cap binds:
  48/24 NF 0.870), ostrich broader and deeper (−10.10, four of five
  friends, DR −7.57), dissolution fails at every width with DR pooled
  better. STATUS: DONE 2026-10-23; Phase 2 head choice HERS with
  F-064 + F-065 in hand; a wider head = deviations entry on her word.
  PHASE 1c DECLARED 2026-10-23 (owner the same day, after the F-065
  report: "Let's try it. Currently our accuracy is low enough that we
  can reevaluate model size limit if needed. Let's test this approach
  first though"; `minifriend-phase1c-2026-10-23/DECLARATION.md`,
  deviations entry 12): a third offline candidate, the structured
  discrete belief head SD (per-need 20-bin histogram, learned
  per-friend drift up and relief down, width-16 recurrent residual,
  cross-entropy on two-hot targets, natural frequency; 6,679 params,
  under the cap) × 3 seeds on the Phase 1 + 1b raws (0 new cat-ticks)
  against 1b's width-24 NF and DR; reads R1c–R8c (contrast with the
  READ rule, ostrich, grave-probability calibration, rate recovery,
  residual share, the floors). Amended the same day on her word
  ("Let's try 3 model sizes this time as well so we can get an idea
  of what more/less parameters buy"): widths 8 / 16 / 32 (3,279 /
  6,679 / 15,783 params; 32 an over-cap probe as 1b's 48, cap not
  moved); R9c size effect. Nine heads done 2026-10-24 (six at the
  200-epoch cap, 10–14 h each); RESULTS gated (round 3 PASS) → F-066:
  the approach does not help on the declared criteria at width 16
  (grave 1.233 × NF-h24 READ, bias −15.01 with the signature on all
  five friends; common states better by a fifth); width moves every
  pooled loss cell (0.819 at 32/16, 1.414 at 8/16); the over-cap
  probe ties NF-h24 on grave at 2.0× NF-h24's parameters; the grave
  probability it emits is near the diagonal above p = 0.7 (mean
  P(grave) 0.474 on grave samples); p_rel AUROC 0.979 in sight / 0.797
  under fog. STATUS: DONE 2026-10-24; Phase 2 head choice HERS with
  F-064 + F-065 + F-066; the cap question hers.
  PHASE 1d DECLARED 2026-10-24 (owner the same day, after the
  Professor's 1c review was carried to her: "Let's run those in three
  in the order you listed"; `minifriend-phase1d-2026-10-24/
  DECLARATION.md`, deviations entry 13): two reads on committed heads,
  0 new cat-ticks — R1d the SD filter's spread under pure drift
  (read-only on 1c's `head-best.pt`; the √(n f (1 − f)) mechanism) and
  R2d a 25-param logistic grave probability on the FROZEN NF-h24 /
  DR-h24 states (three seeds each) read with 1c's R4c instrument
  against SD-w16; decision rule A / B / C declared first; Professor's
  prediction P2 scored beside it. Six probes fitted 2026-10-24 (60–79 s
  each); RESULTS gated (round 4 PASS) → F-067: outcome A — the
  frozen-state logistic read on NF-h24 reaches mean P(grave) on grave
  0.583 ± 0.015 in sight against SD-w16's 0.474 ± 0.115 (|Δ| ≤ s),
  Brier 0.00054 against 0.00064, 0.720 against 0.500 under fog; SD
  keeps the above-0.7 reliability (gap 0.019 against 0.057); the SD
  drift operator smears a sharp belief as √(n f (1 − f)) (2.708 bins
  after 100 ticks at the initial rate); P2 MET; the hybrid (a Phase 1
  head plus one sigmoid, 7,832 params) is the candidate shape for a
  probability-reading consumer and the SD line closes under its own
  rule. STATUS: DONE 2026-10-24; Phase 2 head choice HERS with F-064 +
  F-065 + F-066 + F-067; the cap question hers (unmoved by this read).
  ADDENDUM 2026-10-24 on her word ("Agreed, let's proceed. First the
  breakdown by need and latency read"): R3d which-need accuracy and
  R4d episode-detection latency on the same outputs (0 cat-ticks);
  reading rules declared (≥ 0.80 which-need in sight; ≥ 0.90 of
  in-sight-onset episodes detected at P ≥ 0.2 with median latency ≤ 10
  ticks). Read and gated the same day (round 2 PASS) → F-068: which-need
  0.871 in sight for NF-h24's means (baseline 0.353); 200 of 288
  episodes are reset episodes, disclosed; mid-world fog-onset detection
  0.946 at median latency 0 for NF-h24+p ≥ 0.2, mid-world in-sight
  0.850 (20 episodes); the mean ≥ 90 rule 0.367 / 0.490; false alarms
  0.07 per 10,000 ticks outside the world-start transient; verdict as
  declared "enough for detection and naming, on this evidence".
  STATUS: DONE 2026-10-24; Phase 2 declaration (hybrid shape, NF vs DR,
  probability consumer, threshold, per-need probability, calibration
  step) HERS with F-064..F-068.
  ADDENDUM 2 2026-10-24 on her word ("Let's run the read and see what
  we find", after decisions 1, 2 and 4 of the Phase 2 talk-through were
  ruled as recommended: two-stage on the frozen 1b head, NF, per-need
  probabilities): R5d operating-point sweep, P(grave) ≥ 0.05 … 0.50,
  NF-h24+p and DR-h24+p, group P and the held-out L / W / G evaluation
  worlds; descriptive, no rule, the threshold pick hers with a stated
  price; 0 cat-ticks. Read and gated the same day (round 3 PASS):
  detections fall all the way up the ladder (P mid-world in sight
  0.950 → 0.850 → 0.650 at 0.05 / 0.20 / 0.50), nearly every
  "mid-world" false-alarm run starts within a slice's first 100 ticks
  (the start-up transient is ~100 ticks, not 1), runs after tick 100
  0.027 / 0.003 / 0.000 per 10k on P; L / W / G carries 296 episodes (G
  is a grave-start group). STATUS: DONE 2026-10-24; the threshold pick
  HERS (Phase 2 declaration).
  THRESHOLD RULED 2026-10-25 (owner, on the sweep report: "Agreed,
  let's start with 0.10. Run the burn in"): P(grave) ≥ 0.10 for the
  evaluation's reading rule; "start with" verbatim, hers to move.
  ADDENDUM 3 2026-10-25 on the same words: R6d the burn-in as an
  instrument — the alarm forced off for the first B ticks of every
  observer slice (0 … 300) under R4d's latency read, NF-h24+p, group P
  and L / W / G; the full grid read, two cross-sections printed (burn-in
  ladder at 0.10; threshold ladder at 100); blind ticks and delayed
  episodes priced against false alarms removed; descriptive, no rule,
  the burn-in length hers; 0 cat-ticks. Read and gated the same day
  (round 3 PASS): NO GRAVE ONSET AFTER A SLICE'S HUNDREDTH TICK in
  either set (P 8–72, all re-entries of the grave-start friend; L / W / G
  3–90; L none) — the burn-in removes nearly all false alarms and every
  onset; inside the start-up window a higher threshold discriminates
  better (P clean slices 0.767 → 0.067 from 0.10 to 0.50, grave slices
  0.995 → 0.978); the sweep's "pick low" reading was this thread's
  error. STATUS: DONE 2026-10-25; threshold, burn-in and whether a set
  with known mid-world onsets must be built: HERS.
  DECISION 3 REOPENED 2026-10-25 (owner, after the burn-in report and
  the Professor's note: "Let's do another threshold sweep rather than
  choosing an arbitrary value. Maybe 0.1,0.3.,0.5 to start so we can
  get a feel for the trade-off. Zero-collection reads first."): the
  0.10 "start with" withdrawn; the ladder 0.10 / 0.30 / 0.50 on every
  table; no burn-in ruled. ADDENDUM 4 the same day ("Yes on splice
  test. Yes on relay to product. Confirm 3"): R7d, five zero-collection
  reads (state convergence on L; the splice of covered reset-grave rows
  onto 100 / 500 / 2,000 clean ticks with a junction control, NF+p and
  SD; burn-ins 2 / 5 / 10 and a warm-started state; the self-block
  swap; the three-point ladder throughout); the Professor's P3 / P4 /
  P5 / P8 scored; 0 cat-ticks. The scripted "needy" friend RELAYED to
  Product on her word (msg fe6e7d7c), not a kickoff; its set waits for
  these reads. STATUS: DONE 2026-10-26 (gated round 2 PASS): THE
  PROBE'S GRAVE DETECTION IS A YOUNG-STATE PROPERTY — the same covered
  grave rows 0.995 at a world's start → 0.358 after 100 clean ticks,
  flat to 2,000, SD alike; control never fires; self block not in it;
  warm start cuts reset detection 0.995 → 0.592 and removes every
  first-tick false alarm; training worlds hold no grave after offset
  322 (validation 601, evaluation 779); P4 / P8 met, P3 / P5 not met
  as operationalised; SD reopen condition not met; F-069. DECISION 3
  RULED 2026-10-26 on the ladder walkthrough ("We'll start with your
  recommendation (10/2) , then after we get the mid-episode testing,
  we can reevaluate and dial in on the optimal level."): P(grave) ≥
  0.10 with a 2-tick burn-in, PROVISIONAL, re-read on the needy set
  (Product's spec 067, kicked off in their session 2026-10-26) before
  any Phase 2 declaration fixes it; deviations entry 13. ADDENDUM 5
  the same day ("Run the knee read now"): R8d, the splice at H ∈ {1, 2,
  5, 10, 20, 50}; 0 cat-ticks. STATUS: DONE 2026-10-26 (gated round 3
  PASS): THE FALL IS GRADUAL, MOST OF IT OVER BY 20 TICKS — detection
  0.978 / 0.970 / 0.852 / 0.658 / 0.537 / 0.362 at H = 1 / 2 / 5 / 10 /
  20 / 50 against 0.995 at the start and 0.358 at 100; control never
  fires from H = 2; knee at 20 by the declared midpoint; P9 not met as
  operationalised (clause ii by 0.003); the ruled 2-tick burn-in sits
  inside the window; F-070. The number → Product (067 strata) and the
  Professor (P9).

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
