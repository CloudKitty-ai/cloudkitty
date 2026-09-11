# Fog Gen 1 step-5 shakeout — results (pass of 2026-09-10)

Nine arms, run indices 12–20, launched 2026-09-10 after the PREREG
declaration (86bf830) and finished the same day: every arm ended by the
Part C plateau rule (three flat 1M-tick bins), leash and nofog at 8.0M
ticks, the other seven at 9.0M. No welfare stop fired. The pre-declared
prior held pass-wide: episode returns settled at 0.88–0.92 with
KL-to-anchor 0.41–0.58, the leash holding at both β doses.

Part A: probe-1 read on all nine arms against matched-config anchor
traces; all stop rows green. The radius-1 A17 red was ruled a sampling
artifact on #367 (pooled read + off-pin declaration coverage landed at
f56b48c); nofog's A1 carries the documented known red (34 rare-overdue
columns whose radius-4 rates the whole-world config blocks by law).

Mid-pass events, all recovered with no data loss beyond one update per
arm: the plateau bookkeeping crash (np.bool_ vs json, fixed 945933a)
and the box's dark-wake thermal emergency loop (a wedged power state,
cleared by cold boot; `sleep 0` + High Power Mode on AC are now the
box's standing config, and passes run `nice -n 19` under `caffeinate`).

## Instruments

Anchor baselines: bc-collect `--trace` on each arm's derived config,
probe seeds 40001–3, 2,000 ticks × 3 rollouts
(`results-raw/pass-probe-anchor/{r3,r4,r5,r27}`). Policy readings: the
final probe npz of each arm through `partb_read.py`, whose obs-to-
snapshot adapter feeds `radius_screen.screen` verbatim and is validated
by equivalence against the recorded true snapshots on all four anchor
configs (`test_partb_read.py`; three mutate reds). Raw JSON:
`results-raw/partb/partb-raw.json`.

One reading caveat applies throughout: probes are greedy (argmax), so a
zero in the menu census means "never the argmax", not "zero probability
under sampling".

## Headline numbers (3 probe seeds pooled; anchors 3 rollouts)

| arm | wd | distress/1k | max age | sg-eat/1k | blind-hungry/1k | nn-euc med | friend-in-view | dom max |
|---|---|---|---|---|---|---|---|---|
| ref-s1 | 0 | 0.00 | 0 | 0.00 | 358 | 1.41 | .822 | .67 |
| ref-s2 | 0 | 0.00 | 0 | 0.00 | 342 | 1.41 | .802 | .64 |
| ref-s3 | 0 | 0.00 | 0 | 0.00 | 218 | 1.41 | .801 | .66 |
| leash | 0 | 0.00 | 0 | 0.00 | 328 | 1.41 | .818 | .67 |
| vocab | 0 | 0.17 | 12 | 0.17 | 362 | 1.41 | .803 | .64 |
| mixed | 0 | 0.33 | 65 | 0.50 | 404 | 1.41 | .746 | .67 |
| radius-1 | 0 | 0.00 | 0 | 0.00 | 377 | 1.41 | .672 | .68 |
| radius+1 | 0 | 0.00 | 0 | 0.17 | 155 | 1.41 | .872 | .64 |
| nofog | 0 | 0.00 | 0 | 0.00 | 0 | 1.00 | 1.000 | .59 |
| anchor r4 | 0 | 0.17 | 31 | 0.17 | 560 | 1.41 | .820 | .68 |
| anchor r3 | 0 | 1.17 | 105 | 0.50 | 805 | 1.41 | .811 | .69 |
| anchor r5 | 0 | 0.17 | 19 | 0.33 | 366 | 1.41 | .919 | .66 |
| anchor r27 | 0 | 0.50 | 61 | 0.00 | 0 | 1.41 | 1.000 | .66 |

Class shares (engine one-hot: idle, resting, sleeping, eating,
drinking, playing, grooming): every policy arm trades resting down
(0.56–0.80× its anchor) for sleeping (1.5–1.8×), eating (1.5–1.8×) and
drinking (1.5–2.3×), with idle flat at ~0.59–0.60 both sides. The
welfare table above is the consequence: the learners service needs
more than the teacher does and beat it on every distress measure at
every radius.

Message census (per 1k decisions, pooled): the taught vocabulary
survives 8–9M ticks of PPO in every fog arm — here_water 46–50,
here_food 39–46, here_critter 21–26, here_sunbeam 14–23, want words at
material rates. nofog speaks half the here-words (here_food 21), as a
world with nothing unseen should. The vocab-lesson arm alone speaks
the free register: chirp 20.4/1k and purr 17.3/1k, words no scripted
cat ever says (the a17-exempt group); the plain-clone arms sit at 0–2.

## Part B table — outcomes

| row | outcome | consequence |
|---|---|---|
| H1 watchdog, fog arms | **CLEAR**: 0 entries in every arm and every anchor | none |
| H1 in the no-fog control | CLEAR (0) | none |
| H2 worst seat below anchor | **CLEAR, inverted**: every arm at or above its matched anchor on distress, blind-hungry and safeguard; the anchors are the weaker rosters at every radius | none; per-seat split is a phase-2 read, pooled margin is wide |
| H3 hard-zero intended activity | **No activity class is dead.** GroomKitty is chosen in every arm (28–251 of 30k decisions: ref-s1 28, ref-s3 61, nofog 63, radius+1 112, ref-s2 116, vocab 136, radius-1 172, leash 197, mixed 251) but concentrates on kitty rows 0–1; rows 2–3 are the census's argmax-zeros in most arms — a per-TARGET slot bias, not a closed action. On the same legal rows the final ref-s1 policy argmax-picks GroomKitty on more rows than the clone (53 vs 41 of 6,563), but the realized RATE decays through training (phase-2 curve below: ~13/1k at u49 to 0.9/1k at plateau on ref-s1) — the per-row comparison hides a distribution shift. ChaseCritter/PlayCritter slot zeros are 1–10 legal rows (noise). A14 green: no legality path closed | logged, no break. The slot bias reads as corpus density (grooming examples concentrate in specific observer-to-row cells of the asymmetric roster) — a step-7 corpus/roster question, not a schema one |
| H4 domination > 0.55 | max per-seat class share .59–.68, all idle, all at or below the anchors' own .66–.69; no non-idle attractor, and the F-027 dyadic groom form is absent (GroomKitty near-zero) | none |
| H5 frozen cluster | absent: dispersion and contact match the anchor exactly (nn-euc median 1.41 everywhere), scene turnover normal | none |
| H6 hyper-dispersion | CLEAR: median 1.41 vs HALT bar 6; friend-in-view at anchor level except radius-1 (.672 vs .811) and mixed (.746 vs .820), both with welfare at or above anchor → strategy finding per the ruled joint read | logged |
| blind-hungry span | arms BELOW their anchors everywhere (ref class 218–362 vs 560/1k at r4; radius-1 377 vs 805 at r3) | none; supports the pin |
| radius bracket (slot 4) | radius+1 ≈ ref on all welfare gates (blind-hungry lower, as geometry predicts); fog barely separates 3/4/5 on welfare for LEARNERS | Gen 1 ships at pin 4; world-size × radius screen stays Gen 2 |
| slot 9 radius-1 vs anchor at pin−1 | the ruled tolerance row realized: policy holds welfare (0 distress) where the anchor degrades (1.17/1k, max age 105, blind-hungry 805) | Gen 1 ships at the pin; tolerance logged as the Gen 2 screen's first point |
| leash dose (slot 5) | no collapse: β 0.05 ≈ β 0.04 on every read (KL 0.41 vs 0.49–0.55, welfare identical) | β curve stands; no re-derivation owed |
| vocab arm vs plain clone | vocabulary lesson arm keeps the here-words AND opens the free register (chirp/purr ~38/1k combined vs ~0–2 in every other arm); entropy stayed ~1.15 to plateau vs ~0.8 elsewhere | registered result; sets the step-7 corpus-delivery default toward the lesson |
| slot 8 mixed | the one arm with any distress signal (0.33/1k, max age 65, sg-eat 0.50 vs anchor 0.17/31/0.17) — 2 episodes vs 1 in a 6k-cat-tick window, Poisson-level; also lowest friend-in-view and highest blind-hungry of the r4 arms, and the only arm that grooms specific friends | registered result for step 7's seating question, both directions of it |
| slot 7 ref-s3 spread | inside the s1/s2 spread on every gate (blind-hungry 218 vs 342/358 is the widest gap, same sign as seed noise) | three-seed spread stands for the bands |
| activity-mix band | only idle qualifies (≥500 anchor scenes): ratios 0.88–0.99, in band. Sleeping/eating/drinking sit at 1.5–2.3× on cat-tick shares but their anchor scene counts are far below 500 in a 2k window | logged; eval-census confirmation pending (phase 2) |
| groom pile-on / relief farm | groom-other runs at 0.9–8.4 per 1k decisions across arms — far too thin to farm, and grooming class share 1.1–1.5× anchor is dominantly GroomSelf. Sustainability is the live question, not farming: the behavior is held near clone level by the leash and corpus prior (the tightest-leash arm has the most groom-other of the all-policy arms) while its reward value at `groom_cuddle_relief` 0.5 is marginal — a longer or looser step-7 run is where it would decay | phase-2 read (groom-of-clean-friend on mixed); the sustain-vs-price question goes to step-6/7 pricing beside the relief-farm rule |

## Phase-2 reads (run 2026-09-11; instruments `phase2_read.py` +
## curve/attribution drivers, raw in `results-raw/partb/`)

**Groom-other over training (the sustainability curve)**: the rate
DECAYS through the run in every arm — from ~10–16/1k decisions at u49
(the clone's smeared level) to 0.9–8.4/1k at plateau; ref-s1 fell 14×.
Retention orders by leash and roster: leash 6.6, mixed 8.4, plain refs
0.9–3.9. The plateau rule stopped the arms before the decay finished,
not because it had.

**CORRECTED 2026-09-11 (gate-screen follow-up): the teacher grooms
plentifully and honestly.** The earlier "0 groom-other in 400k
cat-ticks" was an instrument artifact of the F-029 class:
`last_action.with` never carries groom targets — the target lives in
`activity.target`. Re-measured on the correct field: the corpus
teacher grooms others at 12.7/1k cat-ticks (4.9/1k scene starts), and
100% of scene starts follow a fresh want_bath with PRE-tick target
bath >= 20 (snapshots are post-apply; the first groom tick's ~20
relief made targets read clean). `groom_response` is the sole
initiator and works as designed. Consequences of the correction: the
clone's u49 groom rate (~13/1k) IS imitation of the corpus (~12.7/1k),
not emergence; the "farm germinating at 0.5" read was the same
post-apply/scene-tail artifact (teacher tick-level clean-share is 94%
by the same illusion) — no farm evidence anywhere. What SURVIVES the
correction, unchanged: PPO decays groom-other from the imitated ~13/1k
to 0.9-8.4/1k at plateau under the flat 0.5 price, which remains the
reprice's motivation. Gate screen (cuddle_real_threshold 5/8/10/15,
3x20k each, seeds 870001-3, results-raw/gate-screen/): initiations
6.33 / 5.55 / 4.99 / 4.47 per 1k cat-ticks — a smooth +42% from 15
down to 5, honest at every setting — with the shared gate's coupled
side-effect on the sleep economy (nap-adjacent share of sleeping
0.69 / 0.63 / 0.59 / 0.53). Recommendation recorded: keep 15.

**Responder-approach (pre-declared trigger FIRES)**: reference arms'
approach share to unseen speakers is at or below the anchor's chance
rate on BOTH words (want_cuddle .42–.47 vs anchor .56; want_play
.24–.57 vs .64). Per the ruled reading, the words are inert as cues:
this is the trigger for the banked scripted cue-answer rungs
(`cuddle_response` / `play_response` in needs_driven) and the FR-036
cuddle-clause revisit, in the same sitting. Step-7 input, no halt.
nofog reads 0/0 events (no unseen speakers at whole-world vision), the
instrument's built-in consistency check.

**Cosleep-on-beam (strategy finding, logged per the ruled branch)**:
arms present almost no settled-friend-on-beam opportunities (0–16
ticks vs anchors' 211–955) and close ~none; they sleep MORE than the
anchor with welfare intact, but only 5–10% of sleeping ticks are in a
sunbeam vs the anchor's 29% — the learners traded beam-seeking for
sleep-anywhere-beside-friends (SleepWith 66–115/1k and rising through
training as RestWith falls; partnered total holds ~230/1k). The T092
demonstration did not transfer; sleep welfare did not need it.

**Per-seat H2 attribution**: the pass's three distress episodes are
vocab seed-40003 kitty 2 (eat, 12 ticks) and mixed kitty 3 (eat, 11
and 65 ticks on seeds 40002/3). Nothing approaches the 150-tick
watchdog line; mixed kitty 3 is the seat to watch in step-7's mixed
question.

**Still open**: uptake halves of the approach and cosleep reads (need
scene spans), the eval-census half of the band read, and the
critic-compression rewatch (#365 nuance) — all step-6-sitting
material.

## Step-6 input, in one paragraph

No break rows fired; no knob re-pins are owed. The recipe held at both
β doses, welfare beat the scripted teacher at every radius including
pin−1, the taught vocabulary survived PPO everywhere, and the only
degrees of freedom the pass surfaced are choices, not defects: the
mixed-seating question (slot 8's noisier welfare against the richest
partnered-groom behavior of the nine), the corpus-delivery question
(the vocabulary lesson's free-register opening), and the groom-other
sustainability question (alive at clone level in every arm, but held
there by the leash and corpus prior rather than by the reward at the
0.5 relief price, and biased toward specific packmates by corpus
density). All were pre-declared as step-7 inputs or fall under the
pricing row.
