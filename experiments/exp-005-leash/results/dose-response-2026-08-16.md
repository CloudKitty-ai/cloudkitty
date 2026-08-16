# exp-005: the leash dose-response — frozen-design results (2026-08-16)

All six registered arms (β∞ ∈ {0, 0.05, 0.2} × seeds {1, 2}) trained
to completion (6,510 updates / ~20M ticks each) and fingerprinted
through the frozen probe. H1–H4 verdicts below are computed on this
design per the prereg; the D-001 extension arms (β∞ 0.03/0.04, owner-
directed) were running as this was written and enter the curve
descriptively in the extension section when they land.

Anchors (from results/clone-2026-08-15.md): scripted demonstrator and
the clone. The clone is every arm's init AND its KL anchor.

## The measured curve (mean ± sd over 10 probe seeds, per arm)

| metric | demonstrator | clone | β∞=0 s1 | β∞=0 s2 | β∞=.05 s1 | β∞=.05 s2 | β∞=.2 s1 | β∞=.2 s2 |
|---|---|---|---|---|---|---|---|---|
| play_share | .632 | .674 | .217 | .265 | .571 | .637 | .579 | .625 |
| bug_over_meal | .279 | .287 | .001 | .004 | .267 | .308 | .247 | .234 |
| duet_initiation /1k | 154 | 178 | 11.4 | 9.0 | 79.1 | 103.6 | 82.1 | 141.9 |
| time_near_critters | .449 | .456 | .115 | .129 | .391 | .462 | .449 | .433 |
| subject happiness | 79.1 | 78.9 | 93.7 | 92.9 | 85.6 | 83.8 | 79.1 | 78.7 |
| team happiness | 87.5 | 87.5 | 91.4 | 91.3 | 89.5 | 88.8 | 87.6 | 87.5 |
| final KL from anchor | — | 0 | 3.51 | 3.84 | 0.43 | 0.44 | 0.06 | 0.07 |

(per-probe-seed sds in `artifacts/fingerprints/leash-*.json`; probe
sds are small — .006–.015 on shares, 6–15 on duets — so the s1-vs-s2
spread within an arm is seed lottery, not probe noise)

## Verdicts on the registered hypotheses

**H1 — SUPPORTED.** The control collapses the fingerprint in both
seeds: play_share falls 68% (s1) and 61% (s2) relative to the clone,
past the registered 50% bar. The collapse is total across the metric
set — bug_over_meal goes to zero (the unleashed cat never picks a
critter over a meal), duets fall to ~5% of the anchor's, and the cat
stops visiting critters (time_near_critters .12 vs .456). This is
the sunbeam/want-word erosion pattern, reproduced under the modern
recipe and measured end to end.

**H2 — SUPPORTED, with saturation.** Fingerprint drift is monotone
in β∞ at the scale that matters: the control drifts an order of
magnitude farther than either leashed dose on every metric (KL
3.5–3.8 vs 0.43–0.44 vs 0.06–0.07 tracks it). Between 0.05 and 0.2
the decision metrics saturate — play_share and bug_over_meal
differences sit inside the seed lottery (bug_over_meal points weakly
the wrong way: .020 vs .046 mean drift), so strict monotonicity is
not resolvable there. The design registered monotone-decreasing and
the data deliver monotone-non-strict with a flat top.

**H3 — SUPPORTED; the knee is at-or-below 0.05.** Welfare recovery
vs the clone (78.94): +14.8/+13.9 unleashed, +6.7/+4.8 at 0.05,
+0.1/−0.3 at 0.2. Monotone decreasing in β∞ in both seeds. β∞=0.2
recovers nothing — at that dose the leash is expensive cloning. All
recoverable welfare in this design lives at doses ≤ 0.05, which is
what motivated the owner's D-001 extension below it.

**H4 — failure mode ABSENT.** The registered risk was decision
metrics surviving while time_near_critters collapses (leash binds
decisions, not trajectories). At both leashed doses the trajectory
metric is anchor-grade (.391–.462 vs anchor .456) while the control
collapses it — the KL leash constrained state visitation here, not
just per-state choices. The concern stays registered for the fog
era (different information geometry), but at this world and these
doses it did not materialize.

## The duet finding (the design fact that outlives the verdicts)

duet_initiation is the most eroded AND most seed-variable metric at
every nonzero dose: −56%/−42% at 0.05, −54%/−20% at 0.2 (vs the
clone). An earlier same-day read ("duets halve under any dose") was
seed-1-only and overclaimed — seed 2 at 0.2 kept 80% of the
anchor's duets. The stable statement: initiating play with another
kitty is the most welfare-expensive expression of playfulness, so
it is the first thing every dose sells, and how much survives is
partly lottery. Consequence for the lineage generation: if a
lineage's identity claim includes "starts games with friends," the
dose alone does not secure it — the fingerprint gate needs a duet
floor, and candidates will vary seed-to-seed against it.

Worth noting the other side: at 0.05/0.2, seed 2 produced arms whose
play_share (.637/.625) matches the DEMONSTRATOR (.632) — the lottery
also deals anchor-grade hands.

## Extension arms (D-001, descriptive)

β∞ ∈ {0.03, 0.04} × seeds {1, 2}, same recipe/anchor/probe,
registered before running (prereg D-001). Pending at time of
writing; this section is appended when their fingerprints land.

## Regeneration

    # per arm (btag ∈ {0p0, 0p05, 0p2}, seed ∈ {1, 2}):
    .venv/bin/python trainer/train_leash_ppo.py --arm A1 \
      --seed <seed> --kl-beta-final <beta>
    .venv/bin/python fingerprint_probe.py \
      --subject artifacts/leash-A1-b<btag>-s<seed>/policy-final.pt \
      --name leash-b<btag>-s<seed>
