# Findings register

Distilled, generalizable research conclusions — the claims that outlive any
one experiment. Evidence lives in each arc's directory: `RESULTS.md`
(arcs since 2026-08-06) or a `results/` directory of dated reads
(exp-001 to exp-006). Both are append-only once cited: corrections are
addenda, never edits. Raws sit in uncommitted `results-raw/`; a claim
here cites a committed file. This register is the evolving knowledge
layer on top of that evidence (owner ruled A, 2026-09-25).

**Rules:**

- Entries are edited **by supersession, never in place**: a finding that is
  narrowed, overturned, or replaced gets its status changed and a new entry
  — so any past experiment's design can be read against what was believed
  at the time.
- Statuses: `active`, `superseded by F-NNN`, `refuted`.
- Every entry states its **scope of validity** (the conditions it was
  measured under) and **what would invalidate it** — findings stay
  falsifiable, matching the pre-registration culture.
- **An entry is the claim, not the read** (THREADS.md §6; owner ruled
  2026-10-28, "Sold on 1 and 3"): the heading is one sentence, the
  index row one line. The body carries the claim's own numbers (the
  headline figures a reader needs to use it), the scope, **Invalidated
  by**, **Re-verify when**, provenance (dates, SHAs, the deviations
  entry), and the pointer to the arc's `RESULTS.md` section. Every
  other number, table and method paragraph lives in RESULTS; restated
  here it is a condense cut. Her words appear verbatim where they are
  a ruling — a choice among options, or an override of a declared rule
  — because a ruling changes what the claim means; a kickoff or an
  approval changes nothing here and stays in the arc's RESULTS or
  DECLARATION (owner 2026-10-28: elide "where it doesn't add anything
  meaningful"). Entries minted before this rule are brought to it by
  condense passes, never by editing a claim.
- **Cold entries** (owner ruled 2026-10-28, "let's proceed with 1,3,
  and your recommended approach to 2"): at a generation's close, an
  `active` entry cited by no file of that generation moves verbatim to
  [FINDINGS-COLD.md](FINDINGS-COLD.md). The heading stays here as a stub
  pointing there, the index row keeps the claim behind a `(cold: scope)`
  tag, and the status does not change. A declaration that cites a cold
  entry moves it back in the citing commit. The cold file is tier 2 of
  the growth budget, so a move is budget-neutral. Every release PR
  reads both files' **Invalidated by** and **Re-verify when** lines
  against CHANGELOG `## Unreleased`, one disposition per entry touched
  (release template, Experiments rows).
- **Re-verify when** carries the standing trigger for re-testing a finding
  whose scope is expected to shift. This register — not BACKLOG.md — is
  where research re-checks live; the backlog is the product's register.
- New pre-registrations MUST cite the F-ids they rely on, and state
  `cold index scanned: none apply` or name the cold entries they opened.
- Findings that survive across contexts get **promoted**: the claim
  graduates into operating defaults (docs/rl-training.md, reference
  configs, the prereg conventions) with its F-id cited as provenance.
  Promotion is the point; a register that only accumulates is a graveyard.
- Superseded and refuted entries keep only a **stub** here (id · status ·
  claim · why it fell); their full text moves verbatim to
  [FINDINGS-ARCHIVE.md](FINDINGS-ARCHIVE.md) under the same `## F-NNN`
  header, so citations keep resolving. Do the move as part of the
  superseding edit. Promoted findings keep status `active` plus a
  promotion note naming where the operating default now lives.

---

## Index

| id | status | claim |
|---|---|---|
| F-001 | superseded → F-003 | Two-channel credit: fast self, slow teammate (pre-retune quantities) |
| F-002 | refuted | Non-binding cuddle routes carry no material headroom |
| F-003 | superseded → F-013 | The retune tripled the credit horizon; channels unchanged |
| F-004 | active · **promoted** | *(cold: promoted; twin-probe statistics)* Cluster probe statistics by world; replicate on disjoint worlds |
| F-005 | superseded → F-013 | Scarcity×tempo was the one replicated training-world improver |
| F-006 | superseded → F-013 | Pre-024 default world carried no detectable cooperative credit |
| F-007 | active | *(cold: exp-001 MLP, 20M ticks)* BC initialization is necessary for MAPPO to beat the baseline at exp-001's budget |
| F-008 | superseded → F-010 | All-policy collapse read as long-horizon coordination instability |
| F-009 | active · **promoted** | *(cold: promoted; instrument house rule)* Every dimension an instrument holds fixed bounds the failures it can detect |
| F-010 | active | *(cold: exp-001 policy class)* Roster-OOD fragility: an empty kitty slot can collapse an exp-001 policy |
| F-011 | superseded → F-018 | Meow restraint is a reward-structure equilibrium, not an engine guarantee |
| F-012 | active · **promoted** | *(cold: promoted; exp-001 policies)* Channel use is context-dependent; measure in policy company, not solo |
| F-013 | active | *(cold: post-024 scripted dynamics)* The 024 batch rewired the credit landscape; the served world gained a cooperative band |
| F-014 | active | *(cold: post-024 scripted world search)* Post-024 world search: the served world wins as it stands; knob landscape flat |
| F-015 | active | *(cold: twin-probe instrument)* Pooled probes dilute under heterogeneous class amplitudes; condition by class |
| F-016 | active | *(cold: scripted dials, 24×24 lake world)* Raising bath_gain increases scripted on-water time via the grooming channel |
| F-017 | active | *(cold: exp-003 schema-2 MLPs)* The multi-copy collapse is largely a symmetry artifact; sampling dissolves it |
| F-018 | active | *(cold: post-028 two-head surface)* The channel is two-layer: legality is engine law, meaning is reward economics |
| F-019 | active | *(cold: pre-wall 197 surface, global vision)* Clone-then-leash preserves visible personality; unleashed welfare-RL erases it |
| F-020 | active | *(cold: pre-fog carrier-seat rates)* Trait prices are social prices: the cost order inverts between scripted and policy company |
| F-021 | active | Seeing beats pricing: one observation bit bought the water behavior no reward dial could |
| F-022 | active | *(cold: exp-004 MLPs, 028 surface)* The channel comes alive through demonstration, then the policies author its meanings |
| F-023 | active | *(cold: exp-004 policies, generation-mortal numbers)* Channel dials are listener-population properties; no composition-free optimum exists |
| F-024 | active | *(cold: schema 3 / 197 surface)* Entity attention: welfare parity, 40% fewer params, structural robustness, wider expression space |
| F-025 | active | Same recipe, different seed: dialects and cultures, mutually intelligible, welfare-coupled |
| F-026 | active | Under global vision the channel is welfare-redundant — the measured baseline fog must overturn |
| F-027 | active | Twin-seating one artifact creates dyadic self-interaction attractors |
| F-028 | active | *(cold: census instrument provenance)* Census raws are attributable only if the instrument records its own provenance |
| F-029 | active | *(cold: reader contract shape)* A reader rule copied from the wrong contract shape reports a category that cannot exist |
| F-030 | active | *(cold: one seed, one λ, bugs-2.0 world)* Per-event shaping of a social behavior buys initiation churn; the KL leash does not prevent it |
| F-031 | active | A partnered scene runs its minimum only if the counterpart is pinned; grooming is the exception |
| F-032 | superseded → F-033 | Biscuit's idle read as the legality funnel refusing a partnered ask (inference; narrowed to 45% of idle) |
| F-033 | active | Every seat pays a partnered-action refusal tax in its own currency; for Biscuit under half her idle, the rest chosen (pre-048 numbers retired by F-039) |
| F-034 | active | Here* vocabulary cloning is a cliff between 5.6% and 8.2% corpus share, not near 1% |
| F-035 | active | The waterline charge is a magnet before it is a fence: charge-blind arms drift toward the edge |
| F-036 | active | The needflow model is not a proxy for the scripted teacher; three engine gates invert the sleep niche |
| F-037 | active | The collapse detector names a lock but trails the watchdog by 48–147 ticks; healthy margin 0.07 |
| F-038 | active | Comfort buys food promptness linearly and pays in element play, never duets; t_partner 5 halves roster duets |
| F-039 | active | Live refusal tax is Biscuit's alone and it is partner play (5.13%); other seats under 2.3% in groom and move |
| F-040 | active | Under the fog want law `want_drink` is structurally silent: water is permanent and memory never expires, so drink relief is always known; a memory reach of `radius + 0` revives it at ~12 calls/1000 ticks and adds ~12 eat calls (re-verified 2026-09-05 with spec 050 landed: 6–15 drink, +9 to +11 eat; the ~1.2 read was an all-scripted roster, Biscuit's playful seat carries 60–70% of the calls, #349) |
| F-041 | active | The answers-me bit is strict (`their_here > my_want`), so a want re-called on the reply's own tick hides the reply; equal cooldowns lock the pair into that phase (3 of 169 replies invisible in the anchor smoke) |
| F-042 | active | The cert battery on the served composition under the trained clock is the live prior: every Fog Gen 1 seat's 48 h live mean within 0.25 of its battery mean (roster 92.40 vs 92.47) |
| F-043 | active | The distress tail of a policy roster is a roster property: 30 of 55 swap-leg crossings land in an unchanged seat; live, six brief eat-led episodes in 216k ticks at the pacing-search seat |
| F-044 | active | Single-network probes overstate the catastrophe tail: nine crossings in 618 world-probes with one mind in every seat, none in 1.2 M ticks of the five-network composition (F-027 under fog) |
| F-045 | active | Distinct minds disperse: two or three small groups far apart (pairwise 11 vs scripted 6), nearest neighbour unchanged, lab shape reproduced live to the second decimal |
| F-046 | active | A priced target feature the corpus never conditioned on stays unused: under the 054 ramp the minds groom clean friends (74 of 76 live grooms on bath < 10); the scripted groom refusal tax left with the scripted seats |
| F-047 | active | A one-tick relief differential does not move sleep placement: on-beam 2.8× the all-rows rate, the adjacent ring at chance (0.93×), price 7/10/15 inside the seed spread, only the leash held the beam share; 25% of adjacent sleep starts face an occupied beam |
| F-048 | active | The free register (mew, chirp, purr) is inert for a visible listener (0.88–1.07) and an unseen listener does less (row-vs-word attribution OPEN, 2026-09-27 caveat); want_cuddle moves listeners 1.37× / 2.50× on the same instrument |
| F-049 | active | Mews and chirps are not echoed (1.0–1.2× chance, lag 1 only); purr piles are cosleep; the visible echo is several cats answering one ask with here-words (1.9× at lag 1, two thirds keyed on the ask) |
| F-050 | active | Beam seeking survives β 0.04 PPO once the tile changes a nap's outcome: under shallow ground (spec 056 floor 10–25) the package clone keeps 0.46–0.81 of naps on beams through the fine-tune, against 0.04–0.07 at floor 0; a learning mind pays a flat ~1.5 happiness, a frozen mind 1.4–5.2 |
| F-051 | active | Under a sleep floor, beam count is a step at six for a learned mind and flat past it: five beams cost ~0.6 happiness, six to eight are one level inside the seed spread; a mind trained at six seated on five, seven or eight is never worse than one retrained there |
| F-052 | active | Under fog the meow channel is load-bearing: hearer-side deafening of every kind costs the served roster 6.716 team happiness on 30 of 30 worlds; here-words alone cost 0.455; want-words are welfare-null |
| F-053 | active | Under fog, frozen Gen 1 minds do not survive world-size displacement: intact happiness falls 92.471 → 77.935 → 52.813 at 40×40 and 100×100 (teacher 86.343 / 82.898 on the same worlds); exact range on meows stays near-worthless at every size |
| F-054 | active | Objective-side pressure substitutes for the world floor: all three reward shapes restore beam placement on floor 0 (0.516–0.937 against a 0.033–0.062 null), every shaped arm pays 0.75–1.98 happiness against unshaped gen1-A, and the learned price settles interior at λ ≈ 0.12 |
| F-055 | active | An impact-only gate failed with a persistent bonus stock: the glow saturated into a level shift, play starts shifted into the closed-gate region (consistent with banking), and the pressure cost 0.729–0.839 happiness (30/30) without buying the behavior |
| F-056 | active | β is not the enrichment channel's binding lever: 4.7× the bonus moved pooled greedy play 0.0773 → 0.0885 (monotone, all under the 0.10 bar, glow off the cap), and closed-gate starts exceeded the stage-A band on every arm INCLUDING the accrual-gated arms whose closed-gate play pays nothing — the failure indicts the channel, not the gate mechanism |
| F-057 | active | The imitation leash sets the COMPOSITION of play, not its level: dropping it 0.04 → 0.01 released the four corpus-non-players (ex-Biscuit lift +0.0479/+0.0893, the arc's first non-Biscuit movement) while Biscuit gave play back and closed-gate starts fell to a third-to-half of baseline — with the total still under the 0.10 bar; making the stock visible moved nothing, so F-056's channel-dead verdict survives both releases at the total level (the nearest-branch reading: the declared "flat" condition missed downward on two arms) |
| F-058 | active | The aggregate-reward route is closed in its STRONG form: with the leash released to 0.01 AND the stock in the observation together, play's level still does not move (0.0744/0.0800 vs the 0.10 bar) and the policy learns no E-conditioned play beyond the confound floor (excess banded contrast −0.0126..+0.0020 vs the +0.02804 margin, 0 of 8 cells) — while posting the arc's largest positive paired welfare deltas (+0.714/+0.809) with a COLLAPSED tail (559 and 9 dist ticks vs l14's 3,262/1,238); SCOPED 2026-10-04 (owner ruling, no invalidation): holds for the trained channel AS EXPRESSED — see F-059 for the in-weights capacity |
| F-059 | active | Training on the E-channel taught E-conditioned SUPPRESSION, not inability: above-bar play capacity (0.1273/0.1270 blinded, vs 0.0955 arc trained max) sits in the j14 weights behind satiation conditioning — the policy holds the stock high (no overlap on eval E mean/p25 vs the blind twin at matched play) and holds play DOWN, relative to the blind twin, while E is high |
| F-060 | active | Gen 2's hidden-needs trunk transfers across size where frozen Gen 1 minds collapsed: a five-network roster of β 0.04 PPO seeds trained on the served 20×20 beats its scripted teacher in 30 of 30 worlds at 20, 40 and 100 (+5.566 / +4.594 / +7.187, worst streak 267 / 128 / 859, no F-053 stop); five copies of one network (s2) locked roster-wide once at 20×20 and five copies of another (s4) aborted 11 of 30 worlds at 100×100 |
| F-061 | active | The Gen 1 → Gen 2 play rise (0.074..0.147 → 0.363) is teacher and training, not world: the world moves it −0.004, one teacher on every seat +0.091 ± 0.007, training +0.166 ± 0.011; the networks play within 0.012 of the teacher with its comfort rule loosened and consent off, in slack time (less onset pressure than the teacher), out of idle moving and rest |
| F-062 | active | The vision law's wider radius buys the scripted teacher, not the trained roster: at 40×40 one radius step (5 → 4) costs the teacher 1.294 ± 0.958 happiness and the frozen roster 0.088 ± 0.122, so the trained-vs-scripted gap's fall between the cert legs (+5.566 → +4.594) travelled with the radius on the teacher's side (gap at 40×40, radius 4: +5.800 ± 0.860) |
| F-063 | active | A learned distress habit is a per-network trait: trunk-s7 parks at water and keeps choosing Drink while sated on 73% of its distress ticks (234 of 322 across the rotation's streams; the two other networks with distress there, s1 and s2, on none; the teacher 8 of 3,917), every one of the six s7 runs read is that shape (one under a window caveat), and company shortens it (worst 128 in mixed company at 40×40 vs 641 among copies there); the other network's long tails are a hold, pacing and a parked mix, relief beyond sight or adjacency |
| F-064 | active | A capped belief head reading only what a Gen 2 cat sees estimates a friend's hidden needs (7,807 parameters, 9.2% of the trunk): RMS error about 5.3 need points in sight in common states and about 25 in grave states, where the trivial baselines read about 53; trained at natural frequency it carries the ostrich signature on three of four covered friends (pooled grave-state bias −3.8 points against a common-state bias within 0.9 of zero), distress reweighting removes the pooled optimism (+1.7) for 7.5 points² of common-state error and is pooled worse on grave loss (NF/DR 0.944), and the declared dissolution test fails on one friend (NF's grave loss on Miso exceeds 1.10 × DR's by more than the between-seed SD; Biscuit's is 35% lower under NF), so the NF/DR tension is friend-specific and narrow, and no single head is free |
| F-065 | active | With one friend grave at reset and her observers never grave, the belief head's grave estimate is about half again as hard in squared error as Phase 1's all-grave worlds showed (NF in sight: G over P 0.651 ± 0.033 at width 24; RMS 30.1 against 24.3 need points for the same heads) and the ostrich signature is broader and deeper (NF pooled grave bias −10.10 in sight at width 24, signature on four of five friends at widths 24 and 48, distress reweighting no longer removing it at −7.57); head width moves every loss cell monotonically, beyond seed noise on every NF cell and on DR's at 48 over 24, in grave and common states alike (in sight: NF 0.870 and 0.884 at 48/24, 1.210 and 1.199 at 12/24; DR 0.827 and 0.767 at 48/24), so capacity above the 8,445 cap buys 13–17% of grave loss at this geometry and, in proportion, not grave-specifically; the dissolution procedure fails at every width with the reweighted head pooled better on grave (NF/DR 1.097–1.188), the reverse of Phase 1's read on its own evaluation worlds (its grave samples mostly from the all-grave set G, about a tenth from W) |
| F-066 | active | A structured discrete belief head (per-need 20-bin histogram with learned drift and relief, cross-entropy on two-hot targets) does not beat the natural-frequency head NF on the declared grave cells at equal capacity: at width 16 (6,679 params) its pooled mind-visible grave MSE on the per-cat worlds is 1119.69 against NF-h24's 908.10 (1.233 ± 0.091, READ) and its pooled grave bias in sight is −15.01 against NF's −10.10 (signature on all five friends), while in sight it is better than NF in common states by about a fifth (19.96 against 25.34, 0.787 READ); width moves every pooled SD loss cell in one direction (in sight on P: grave 1.414 at 8/16, 0.819 at 32/16, both READ; common 1.237 / 0.848), in proportion not grave-specific, and the 1.9×-cap probe (15,783 params) ties NF-h24 on grave in sight (917.44; 1.010 ± 0.083, not READ) at 2.0× NF-h24's parameters and is better by a third in common states (16.92; 0.668 READ); the grave probability the head emits is near the diagonal above p = 0.7 at width 16 in sight (realised 0.795 / 0.851 / 0.936 in the top three bins) with mean P(grave) 0.474 on grave samples, a belief whose histogram mean sits below the truth, which is the −15.01 the bias column reports and which the ostrich metric as declared does not separate from optimism; p_rel discriminates relief at AUROC 0.979 in sight and 0.797 under fog at width 16; six of nine runs hit the 200-epoch cap before plateauing and each run cost 10–14 hours against minutes for the comparators |
| F-067 | active | A 25-parameter logistic read of "the true stratum is GRAVE" on the FROZEN NF-h24 GRU states reads grave within the seed spread of the structured discrete belief head SD at width 16 (F-066) and ahead of it on the grave mean and Brier in sight and under fog, with its mean on common samples as low: in sight on the per-cat worlds its mean P(grave) on grave samples is 0.583 ± 0.015 against SD's 0.474 ± 0.115 (Δ −0.109, combined seed spread 0.116 → outcome A of the declared rule, "the histogram bought nothing the consumer needs"), its Brier 0.00054 against 0.00064, its mean on common samples 0.0003 against 0.0005; under fog 0.720 ± 0.010 against 0.500 ± 0.046 (Brier 0.00119 against 0.00185); in sight SD keeps its reliability above p = 0.7 (above-0.7 gap 0.019 against 0.057; NF-h24+p's top bins realise 0.760 and 0.882 where they say 0.854 and 0.959) and a lower mean on adjacent samples (0.183 against 0.265); on the DR-h24 states the same probe reads 0.577 ± 0.037 in sight; all three rank grave against non-grave at AUROC 0.998–0.999 in every version, so the heads differ in confidence, not discrimination; every MSE and bias cell of F-064 / F-065 / F-066 is unchanged by construction (the frozen heads' own output reproduces 1b's predictions to 3.9 / 4.5 / 3.7 / 3.0 / 2.4 / 3.6 × 10⁻⁷); the hybrid (a Phase 1 head plus one sigmoid) is 7,832 parameters, under the cap; the Professor's registered prediction P2 (≥ 0.40 on grave, ≤ 0.002 on common, in sight) is met. Beside it, the SD filter's drift operator smears a sharp belief exactly as the arithmetic says — sd √(n f (1 − f)) bins, matched to 2.3 × 10⁻⁸ bins over 79 unclamped rows; 2.708 bins (13.5 need points) after 100 ticks at every run's initial rate, 1.56–1.87 bins after 100 ticks at the learned width-16 median rates — while the engine's need rises with no uncertainty; the mechanism the Professor named for F-066's residual share stands as arithmetic, its causal share unmeasured |
| F-068 | active | The base head's five means name the grave need, the frozen-state grave probability is over 0.2 before a mid-world grave episode begins in most cases, and a consumer reading the means against 90 misses half or more of them: on the per-cat worlds NF-h24's means name a grave need on 0.871 ± 0.031 of the need-grave samples in sight (top-2 0.969; the always-name-drink baseline 0.353; DR-h24 0.872 ± 0.010; SD-w16's grave mass 0.739 ± 0.043, its mean 0.687 ± 0.031) and 0.867 under fog, play the weakest need (0.783); of 288 grave episodes over observer slices (72 friend-episodes × 4 observers) 200 are RESET episodes (grave at the world's first tick, group P's per-cat grave-start design; a crossing there is the prior, not a detection), 20 begin mid-world in the observer's sight and 68 mid-world under fog; on the mid-world fog-onset episodes NF-h24+p at P(grave) ≥ 0.2 detects 0.946 ± 0.042 at a median latency of 0 ticks and is over the threshold at the tick before onset as well in 0.931 of them, on the mid-world in-sight episodes 0.850 ± 0.087 (anticipated in 0.833), over all onsets 0.912 ± 0.051 of the 34 in-sight-onset and 0.966 ± 0.016 of the 254 fog-onset episodes; its false-alarm runs are 0.90 ± 0.30 per 10,000 observer-ticks in all and 0.07 ± 0.02 excluding runs that start at the world's first tick; the max-of-means ≥ 90 rule on the same head detects 0.367 ± 0.058 of the mid-world in-sight and 0.490 ± 0.090 of the mid-world fog episodes (0.490 ± 0.045 and 0.686 ± 0.065 over all onsets, 3 ticks late at the median), on SD-w16's means 0.294 and 0.177 over all onsets at a median of 11.3 and 34.0 ticks; both declared reading rules hold as declared ((i) NF-h24 mean which-need in sight, pooled, ≥ 0.80 with every per-need cell of n ≥ 200 above 0.60; (ii) NF-h24+p at P(grave) ≥ 0.2 detecting ≥ 0.90 of the episodes with onset in sight at median latency ≤ 10 ticks — 0.912, by less than one of its 34 episodes, 0.850 on the 20 mid-world in-sight episodes alone, disclosed) and the registered prediction that the mean rule detects under half of the in-sight-onset episodes holds on the seed mean (0.490; per seed 0.500 / 0.441 / 0.529, one seed exactly at half and one over), so the verdict as declared is "enough for detection and naming, on this evidence" |
| F-069 | active | The frozen NF-h24 head's grave probability is a property of the young state (at P(grave) ≥ 0.10 on the per-cat worlds unless stated): the same covered grave rows that it detects in 0.995 ± 0.009 of 200 reset episodes at a median latency of 0.3 ticks when they arrive at a world's start are detected in 0.358 ± 0.175 (0.540 / 0.345 / 0.190 per seed) at a median latency of 26.5 ± 12.4 ticks when spliced after 100 clean ticks of a lived world's history, 0.287 ± 0.143 and 0.288 ± 0.132 after 500 and 2,000, with a junction control of default-start rows never firing (0.000 at H = 100 / 500 / 2,000 at every threshold) and SD width 16 collapsing alike (1.000 → 0.275 → 0.282 → 0.287); the self block is not in it (H = 0 with the recipient's self block 0.995 / 0.972 / 0.968 at 0.10 / 0.30 / 0.50 against 0.995 / 0.970 / 0.965); the same head warm-started at the mean state over ticks 1,000 … 19,999 of L's clean slices detects the real reset episodes at 0.592 ± 0.066 (0.650 / 0.520 / 0.605 per seed) against 0.995 while every first-tick false-alarm run disappears (614.0 ± 322.2 → 0.0) and the clean slices' start-up firing goes 0.767 ± 0.403 → 0.000 ± 0.000; on L's clean slices the state's step does not shrink (median 0.0480 ± 0.0009 in ticks [1, 100), 0.0571 ± 0.0024 from tick 1,000 on) and the logit has no trend (0.0001 ± 0.0021 per 1,000 ticks against a within-slice SD of 0.9387 ± 0.0775), while the mean logit is −1.829 ± 0.598 at tick 0 (P(grave) 0.178 / 0.075 / 0.192 per seed), −4.059 at tick 1 and −9.371 at tick 10; the training worlds (every set) hold no grave after offset 322 (182 onsets, the latest at 171, 1 after tick 100; the validation worlds to 601, the evaluation worlds to 779); a burn-in of 2 ticks at 0.10 on the per-cat worlds takes all-runs false alarms 1.607 ± 0.805 → 0.136 ± 0.063 per 10,000 observer-ticks at reset detection 0.980 (5 ticks: 0.073 ± 0.001 at 0.960; 10: 0.072 ± 0.004 at 0.798) while on L / W / G the same burn-ins leave 0.538 → 0.521 → 0.577 per 10,000; swapping the observer's self block on the 200 grave-start slices moves reset detection 0.995 → 0.992 and the re-entries 0.900 → 0.883 in sight; the Professor's P4 and P8 are met, P3 and P5 not met as operationalised, and the condition named for reopening SD is not met |
| F-070 | active | The frozen NF-h24 head's grave detection falls gradually with the length of the clean history before the grave rows, most of the fall over by 20 ticks (at P(grave) ≥ 0.10 on the §Addendum 4 splice, group P's 200 covered reset-grave donors onto L's 60 clean recipients, seeds 1–3, unless stated): the same covered grave rows detected in 0.995 ± 0.009 of episodes at a world's start are detected in 0.978 ± 0.003 / 0.970 ± 0.009 / 0.852 ± 0.038 / 0.658 ± 0.096 / 0.537 ± 0.063 / 0.362 ± 0.070 after 1 / 2 / 5 / 10 / 20 / 50 clean ticks and 0.358 ± 0.175 after 100, at median latencies from the junction of 1.0 / 1.3 / 3.7 / 11.3 / 16.3 / 24.7 ticks against 26.5 at 100, with the junction control of default-start rows firing in 0.010 ± 0.017 of junctions at H = 1 and 0.000 from H = 2 on; the knee by the declared midpoint (0.641 between the start's 0.995 and the 500 / 2,000 plateau's 0.287) is at H = 20, with H = 10 just above it; at 0.30 and 0.50 the curve sits lower at every H (H = 10: 0.482 / 0.378); SD width 16 at 0.10 sits lower on the seed means at every H ≥ 5 (0.762 ± 0.185 / 0.487 ± 0.332 / 0.403 ± 0.306 / 0.297 ± 0.165 at 5 / 10 / 20 / 50; knee at 10), with one of its three seeds (seed 3, whose control still fires 0.140 / 0.130 there) above every NF seed at H = 10 and 20, while its rows at H = 1 and 2 are its own start-up transient (control 1.000 / 0.985) and its seed-mean control is under 0.05 only from H = 10; the Professor's P9 is not met as operationalised (0.658 at H = 10 is under 0.70; 0.537 at H = 20 is 0.178 from the committed 0.358 at H = 100, over its seed SD of 0.175 by 0.003); the provisional 2-tick burn-in of decision 3 sits inside the window in which the head sees a covered grave (0.970 at H = 2, 0.852 at 5) |

---

## F-001 · superseded by F-003 · Credit in CloudKitty is two-channel: fast self, slow teammate

Claimed the two-channel credit structure (fast self, ~60% of mass within
18 ticks; slow teammate, 50–200 ticks peaking k≈106) on the pre-retune
engine. The structure survived every engine since; these quantities died
with the companionship retune (PR #60). Chain: F-001 → F-003 → F-013.
Full text: [FINDINGS-ARCHIVE.md](FINDINGS-ARCHIVE.md).

---

## F-002 · refuted · Non-binding cuddle-route under-use is real but carries no material headroom

The mechanical under-use was confirmed, but the headroom hypothesis was
refuted post-retune: high-need opportunities beside friends occur ~1–2
per 100k ticks (the heavier cuddle weight services the need early), so
the route cannot beat `needs_driven`. The prereg's interpretation rule —
trained-policy Cuddle pinned streaks beside busy friends = real skill
gap — stands. Full text: [FINDINGS-ARCHIVE.md](FINDINGS-ARCHIVE.md).

---

## F-003 · superseded by F-013 · The companionship retune tripled the credit horizon; channels unchanged

Re-measured F-001 on the retuned engine: two-channel structure held,
every band moved out 2–4× (spillover ~230–430, team peak k≈230, live
tail past k=1,000). Killed by its own registered trigger when the 024
wet-fur batch moved the quantities again — the same death as F-001.
See F-013. Full text: [FINDINGS-ARCHIVE.md](FINDINGS-ARCHIVE.md).

---

## F-004 · active · Probe statistics must cluster by world; few-world batches produce phantoms

Cold since the Gen 1 close (2026-10-28): full text, scope, invalidator and
re-verify trigger in [FINDINGS-COLD.md](FINDINGS-COLD.md#f-004).

## F-005 · superseded by F-013 · Training-world knobs move detectable cooperative signal weakly; scarcity×tempo is the one replicated improver

Across 10 candidate worlds most knobs did nothing or hurt; scarcity +
tempo ×1.5 was the one replicated improver and became the frozen
training world. On the post-024 engine its gain fell below the
false-positive floor (the chase sidestep dissolved the queueing
consequences it fed on). The search was honest for an engine that is
gone. See F-013. Full text: [FINDINGS-ARCHIVE.md](FINDINGS-ARCHIVE.md).

---

## F-006 · superseded by F-013 · The default world carries no detectable cooperative credit

On the pre-024 32×32 default world, team/spillover significance sat
below the false-positive floor — the training-world selection was
load-bearing. Both of its re-verify conditions arrived at once (024 +
the 24×24 cutover) and the claim inverted: the served world now carries
a replicated cooperative band at k≈230–330. The 32×32 measurement
remains correct for the world it measured. See F-013.
Full text: [FINDINGS-ARCHIVE.md](FINDINGS-ARCHIVE.md).

---

## F-007 · active · BC initialization is necessary for MAPPO to beat the baseline at exp-001's budget

Cold since the Gen 1 close (2026-10-28): full text, scope, invalidator and
re-verify trigger in [FINDINGS-COLD.md](FINDINGS-COLD.md#f-007).

## F-008 · superseded by F-010 (2026-07-30) · A long-horizon all-policy instability mode exists that short probes cannot detect; scripted teammates arrest it

Read a 20k-tick all-policy collapse (invisible to 2k probes) as a
long-horizon coordination instability that scripted teammates arrest.
Forensics found both halves wrong: the mode is **roster-OOD input
fragility** — visible within 2k ticks on the world that triggers it,
collapsing a single policy alone; the framing was an artifact of
certification accidentally running a different world than the probes
(deviation 31). See F-010.
Full text: [FINDINGS-ARCHIVE.md](FINDINGS-ARCHIVE.md).

---

## F-009 · active · House rule: a measurement's horizon bounds the failures it can detect

Cold since the Gen 1 close (2026-10-28): full text, scope, invalidator and
re-verify trigger in [FINDINGS-COLD.md](FINDINGS-COLD.md#f-009).

## F-010 · active · Roster-OOD fragility: an empty kitty slot can collapse an exp-001 policy into idle catatonia (supersedes F-008)

Cold since the Gen 1 close (2026-10-28): full text, scope, invalidator and
re-verify trigger in [FINDINGS-COLD.md](FINDINGS-COLD.md#f-010).

## F-011 · superseded by F-018 · Meow restraint is a reward-structure equilibrium, not an engine guarantee

Held from spec 023 (no engine rate limit; restraint priced by the
turn cost and team reward) until spec 028 removed the turn cost
(ride-along head) and returned the cooldown as mask legality — law,
not manners. The reward-structure half survives in F-018. Full text:
[FINDINGS-ARCHIVE.md](FINDINGS-ARCHIVE.md).

## F-012 · active · Channel use is context-dependent: solo probes underestimate a policy's meow behavior

Cold since the Gen 1 close (2026-10-28): full text, scope, invalidator and
re-verify trigger in [FINDINGS-COLD.md](FINDINGS-COLD.md#f-012).

## F-013 · active · The 024 batch rewired the credit landscape: the served world gained a cooperative band, the frozen gym lost its edge (supersedes F-003/F-005/F-006 quantities)

Cold since the Gen 1 close (2026-10-28): full text, scope, invalidator and
re-verify trigger in [FINDINGS-COLD.md](FINDINGS-COLD.md#f-013).

## F-014 · active · Post-024 world search: the served world wins as it stands; the knob landscape is flat at 100-world power

Cold since the Gen 1 close (2026-10-28): full text, scope, invalidator and
re-verify trigger in [FINDINGS-COLD.md](FINDINGS-COLD.md#f-014).

## F-015 · active · Pooled all-action probes dilute under heterogeneous class amplitudes; class-conditioned batches carry the credit signal

Cold since the Gen 1 close (2026-10-28): full text, scope, invalidator and
re-verify trigger in [FINDINGS-COLD.md](FINDINGS-COLD.md#f-015).

## F-016 · active · The wet-fur dial subsidises the behaviour it prices: raising bath_gain increases scripted on-water time through the grooming channel

Cold since the Gen 1 close (2026-10-28): full text, scope, invalidator and
re-verify trigger in [FINDINGS-COLD.md](FINDINGS-COLD.md#f-016).

## F-017 · active · The multi-copy collapse is largely a symmetry artifact: identical greedy policies deadlock over contested resources, and sampled selection dissolves it

Cold since the Gen 1 close (2026-10-28): full text, scope, invalidator and
re-verify trigger in [FINDINGS-COLD.md](FINDINGS-COLD.md#f-017).

## F-018 · active · The channel is two-layer by design: legality is engine law, meaning is reward economics (supersedes F-011)

Cold since the Gen 1 close (2026-10-28): full text, scope, invalidator and
re-verify trigger in [FINDINGS-COLD.md](FINDINGS-COLD.md#f-018).

## F-019 · active · Clone-then-leash preserves visible personality; unleashed welfare-RL erases it (exp-005, the dose-response)

Cold since the Gen 1 close (2026-10-28): full text, scope, invalidator and
re-verify trigger in [FINDINGS-COLD.md](FINDINGS-COLD.md#f-019).

## F-020 · active · Trait prices are social prices: the cost order inverts between scripted and policy company (the exchange table)

Cold since the Gen 1 close (2026-10-28): full text, scope, invalidator and
re-verify trigger in [FINDINGS-COLD.md](FINDINGS-COLD.md#f-020).

## F-021 · active · Seeing beats pricing: a single self-observation bit bought the water behavior no reward dial could (exp-003)

Measured 2026-08-07 on the post-026/027 engine (stamp `cba976da…`).
exp-002 falsified the pricing route: no wet-fur dial setting bought
deployed water avoidance at welfare-neutral cost (its gates
extrapolated to dial 4.8–5.6, 3–4× shipped). exp-003 fixed the dial
at 3.5/60, added ONE bit — the in-water self-observation flag (obs
182→183, schema 1→2) — and registered no dial arm and no escalation
clause.

1. **The bit worked where the dial could not**: 7/9 candidates
   inside the registered water band, 9/9 under the in-water ceiling
   (1.5×B = 5.15%), 9/9 above the drink floor; both misses were
   lounging only. The selected candidate is *drier than scripted* —
   in-water 2.79% vs B 3.44%, lounging 0.62% vs 1.50% — at +0.042
   welfare over needs_driven.
2. **The F-016 loop dissolves under observability**: scripted cats
   groom *more* on water as the dial rises (wetness raises Bath, a
   needs_driven cat bathes where it stands); policy candidates
   groom-on-water at 0.12–0.75% — a policy that can see it is wet
   does not do that. F-016 point 3's prediction (scripted and
   learned move oppositely on this channel), confirmed.
3. **Routing, not luck**: the lake-retrofit accident enlarged served
   water 8→11 tiles; scripted B *rose* 3.44→3.66% while the policy
   *fell* 2.91→2.83% — policy water use is insensitive to water
   availability.
4. Methodology that carried: band bounds registered as MULTIPLES of
   the same-engine scripted baseline B, never absolutes — B is
   re-measured whenever the stamp moves, so thresholds keep their
   meaning across engines.

**Scope**: MLP policy class on obs schema 2, served world, dials
fixed at 3.5/60; 10 seeds × 20k (band), 30 × 20k (welfare). The
principle — make the cost observable rather than raising it — is
the generalizable claim; the shares are engine-mortal.

**Evidence**:
[grid-2026-08-07.md](exp-003-water-schema/results/grid-2026-08-07.md)
(§9.1, the standout, the lake section);
[water-band summary](exp-003-water-schema/results/water-band-2026-08-07/) (recorded (local): untracked, evidence-archive ruling 2026-09-27);
exp-003 prereg §1–§3 (the registered refusal to escalate the dial).

**Implications**: when a behavior needs steering, reach for
observability before reward surgery — the bit is schema-versioned,
priced once, and F-011-safe, where a dial fights adaptation forever.
(exp-003's other headline — H5's 0/9 zero gate — is not a finding
about these policies: F-017 showed the gate conflated coordination
with competence, and its respec became the bar-225 battery.)

**Would invalidate**: a dial setting matching the bit's water profile
at welfare-neutral cost; a schema bit failing to move a behavior the
policy demonstrably attends to.

**Re-verify when**: B re-measures on any stamp move (standing, by
construction); fog-era vision changes what "observable" means.

## F-022 · active · The channel comes alive through demonstration, then the policies author its meanings (exp-004)

Cold since the Gen 1 close (2026-10-28): full text, scope, invalidator and
re-verify trigger in [FINDINGS-COLD.md](FINDINGS-COLD.md#f-022).

## F-023 · active · Channel dials are listener-population properties; no composition-free optimum exists (the threshold curve)

Cold since the Gen 1 close (2026-10-28): full text, scope, invalidator and
re-verify trigger in [FINDINGS-COLD.md](FINDINGS-COLD.md#f-023).

## F-024 · active · Entity attention: welfare parity, 40% fewer parameters, structural robustness, and a wider expression space (the architecture arc)

Cold since the Gen 1 close (2026-10-28): full text, scope, invalidator and
re-verify trigger in [FINDINGS-COLD.md](FINDINGS-COLD.md#f-024).

## F-025 · active · Same recipe, different seed: dialects and cultures — mutually intelligible, kin-biased, welfare-coupled (the meow economies)

Measured 2026-08-14 across homogeneous and mixed rosters of the
three attention seeds (probe band, seat-rotation so traits never
confound model identity).

1. **Dialects**: s1 purrs at above-baseline separation (2.87 emit
   vs 2.53 declined — a contact call at excursion apogee, the
   deployed generation's dialect); s3 at below-baseline (2.54 vs
   3.73 — a proximity hum). Same word, opposite spatial deixis,
   both stable equilibria differing only in RNG seed.
2. **No devaluation at volume**: s3 purrs 4× as often as s1 (794 vs
   192/1k) with undiminished per-purr causal potency (7.6% vs 6.5%
   act-flip) — the channel does not saturate at measured volumes
   (79% duty cycle).
3. **Mutual intelligibility with kin bias**: cross-model act-flip
   7.3–7.4% vs same-model 7.8–8.9% (action semantics transfer);
   answering is kin-biased (same-model echo 20–26% vs cross 16–18%);
   voices stable in mixed company.
4. **Culture, welfare-coupled**: s3 is a groomer culture (GroomKitty
   12.0% of decisions vs 0.14/0.45% siblings — an 85× spread on
   classes dead in every pre-v4 generation). In mixed company it
   keeps giving unreciprocated, asks quadruple, drifts peripheral —
   and its welfare tracks its audience: 94.87 among kin → 93.93
   alone (−0.94), with kin recovering ~60% of the deficit. F-012's
   audience-dependence, surfacing at the welfare level for the
   first time.

**Scope**: three seeds of one recipe on one surface; screen-grade
(pooled probe seeds, no per-world clustering; the dose-response is
stated because it is consistent across all three mixed compositions
and both instruments). Certification of a heterogeneous roster must
run the battery on THAT composition — the homogeneous numbers do
not transfer (F-009).

**Evidence**:
[meow economies](attn-meow-econ-2026-08-14/results.md);
[valence results](attn-meow-econ-2026-08-14/valence-results.md).

**Implications**: seating is culture-pairing, not just
skill-selection — roster composition is a welfare variable for
cultured policies (the cross-gen roster's seat-paired accounting
absorbs this; the doter kin pair exists because of it). The
purrsonality register documents dialects per generation; lineage
work (F-019) is how a chosen culture survives one.

**Would invalidate**: dialects failing to replicate within their
own generation's re-probe; per-purr potency collapsing at higher
duty cycles.

**Re-verify when**: each generation (dialects are seed-born — new
seeds, new dialects); any roster/seating change involving a
culture-carrying policy.

## F-026 · active · Under global vision the channel is welfare-redundant — the measured baseline the fog generation must overturn

Measured 2026-08-15 (digest ablation, deployed roster B, hearer-side
per-kind digest zeroing, 4 arms × 10 seeds × 10k).

1. **Deafening moves nothing**: team happiness intact 94.887,
   purr-deaf 94.876, followme-deaf 94.873, both-deaf 94.900 — flat
   within ±0.015, an order of magnitude inside the parity band.
   Contact, cosleep, and grooming rates unmoved. The channel has
   measured *function* (deafening removes the answer-driven ~15% of
   purr volume — the chorus dies) without measurable *fitness*.
2. The mechanism was already visible in the want-words: WantEat is
   honest but inert (emitted 5.5–7.5 tiles from everyone —
   under global vision it tells hearers nothing their eyes don't).
   Everything a purr tells a hearer, the hearer already sees.
3. **The registered whisper, not a claim**: distress ticks double
   purr-deaf (37 → 78, 0.02% absolute). If fog-era ablations
   reproduce it at scale, the purr's value was tail-risk insurance,
   not mean welfare — the thing to look for first.

**Scope**: frozen minds (a generation *trained* deaf could differ —
the ablation removes input, not the training pressure);
screen-grade, 10 seeds, global vision, 0.95-welfare abundance.
This finding is deliberately a BASELINE: ROADMAP phase 2's
registered comparison (does grounded reference beat
FollowMe-overloading when fog creates an information gradient)
is powered by having this null on record first.

**Evidence**:
[digest-ablation results](digest-ablation-2026-08-15/results.md);
[meow economies addendum](attn-meow-econ-2026-08-14/results.md)
(want-word pragmatics).

**Implications**: no channel-value claims for the current
generation beyond culture and welfare-neutrality (client-facing
copy included); the Here* family's expected pre-fog inertness
(phase-1 rider) is this finding's prediction, not a surprise;
fog-era experiments inherit a clean before/after design.

**Would invalidate**: a same-generation composition where deafening
moves welfare outside the parity band (would mean the ablation
missed a load-bearing path).

**Re-verify when**: the fog generation (the entire point) -- RUN, 2026-09-24: F-052, the channel pays under fog (all-deaf -6.716 team happiness, 30 of 30 worlds); this entry keeps its own scope (global vision, the pre-039 world -- see the confound note below). Any
same-generation ablation at scale that can power the
distress-doubling whisper.

**Confound note (2026-08-21, SC-005)**: the bugs-2.0 world change
(spec 039: roam tether, critter ttl 600, pounce, greeble dart,
play_relief_bug 28) landed between this baseline and any fog-era
re-measurement. The redundancy reading above is a property of the
pre-039 world; fog-generation comparisons against it span TWO
changes (economy + vision), so a fog-era channel-fitness delta must
be decomposed before attribution — re-run the deafening ablation on
the post-039/pre-fog world first, and treat THAT as the fog
generation's baseline. Play-relevant calls are the likely coupling
(hunt/duet coordination now pays differently); the F-025 dialect
comparisons are within-generation and unaffected.

---

## F-027 · active · Twin-seating one artifact creates dyadic self-interaction attractors

Found 2026-08-20 by trace forensics on the exp-006 phase-1 battery's
G2a/r5 failure (family-11, five seats, stress band).

1. **The mechanism is a mutual loop, not scarcity**: the attn-a1-s3
   pair (same artifact at Pumpkin and Kittybear) settled on adjacent
   tiles and each chose SleepWithKitty at the other for 2151/2200 and
   2084/2200 decisions while eat and drink saturated at 100 —
   a 2331-tick distress streak with water standing 37 tiles away and
   chow abundant throughout. Co-sleep services sleep and cuddle, so
   the two needs the loop feeds stay low while every other need
   starves. Each wake tick, the policy observes an adjacent sleeping
   twin and re-chooses co-sleep: the same mind holds both seats, so
   both make the same wrong choice and each renews the other's
   context.
2. **It follows the pair, not the composition**: the reference
   composition (no new-generation mind) failed the same world through
   the same loop with the same twins (worst 465). Solo-seating s3
   removed the failure class entirely: 0 bar exceedances, worst
   streak 159, and that 159 is directed travel on the 26-tile map.
3. **The world modulates persistence, not existence**: 2.4M
   cutover-config ticks (20×20, water 7–9, stimulus-dense) never
   showed the loop; family-11's quiet far corner and single pond gave
   it room. Hence the recruited tail benchmark
   (`tail-benchmarks/family-11-r5`).
4. **The tail is the price of a paid-for benefit**: two s3 seats were
   a deliberate welfare choice (the 08-14 kin dose-response, 94.87
   kin / 93.93 alone). Solo with cuddle-forward company recovers
   about half the kin gap (−0.50 vs −0.94, cross-surface). Kin is not
   clone: the culture-pairing benefit (F-025) and the symmetric-lock
   tail arrive in the same seating decision.

5. **Same-day refinement (E-arm fill cell)**: the attractor family is
   not twin-exclusive. With s3 seated once and ppo-E0-s1 replacing
   the scripted fill, a heterogeneous pile formed (solo s3 choosing
   SleepWithKitty 382/435 while ppo-L-04-s1 groomed the sleeper
   366/435, the E arm half-adhered) and held 435 ticks — over the
   225 bar, self-breaking where the twin lock was self-renewing
   (2331). The same seed under scripted fill read mda 0. Twins make
   the lock symmetric and stable; policy company makes piles
   available; scripted seats act as perturbation sources that break
   them. Each scripted seat replaced by a policy mind removes a
   stabilizer.

**Scope**: greedy serving/eval mode — deterministic symmetric argmax
sustains the lock; sampled action selection is untested. Observed
with one artifact pair (attn-a1-s3); the e004-a1-s2 pacing seen in
the same runs is a separate solo pathology, not dyadic. Engine note:
the Article I safeguard is supply-side only (guarantees relief
exists, not that it is taken), so nothing in the engine interrupts
the loop.

**Evidence**:
[r5 forensics](exp-006-character-gen/results/r5-forensics-2026-08-20.md)
(mechanism, choice histograms, partner fields, follow-up cells);
[battery record](exp-006-character-gen/results/battery-2026-08-20.md);
[tail benchmark](tail-benchmarks/README.md).

**Implications**: seating multiples of one artifact requires
tail-benchmark coverage for the dyadic class; the serving-side
max_distress_age watchdog and the backlogged distress-gated
intervention (disabled in testing, enabled on the server — owner,
2026-08-20) are the operational complements; welfare readings of a
twin-seated roster carry a tail its means don't show (F-009's point,
in the seating dimension).

**Would invalidate**: a twin-seated composition surviving extended
family-11-class exposure with no lock (would localize the attractor
to s3's groomer culture rather than twin-seating as such); a
cross-mind pile matching the twin lock's self-renewing duration
(point 5's piles broke an order of magnitude earlier — parity would
collapse the twin/heterogeneous distinction the entry rests on).

**Re-verify when**: any new artifact is seated in multiple; any move
off greedy serving; the distress-gated intervention lands (it
truncates the observable, so streak-based detection must move
upstream of the override).

## F-028 · active · Census raws are attributable only if the instrument records its own provenance

Cold since the Gen 1 close (2026-10-28): full text, scope, invalidator and
re-verify trigger in [FINDINGS-COLD.md](FINDINGS-COLD.md#f-028).

## F-029 · active · A reader rule copied from the wrong contract shape reports a category that cannot exist

Cold since the Gen 1 close (2026-10-28): full text, scope, invalidator and
re-verify trigger in [FINDINGS-COLD.md](FINDINGS-COLD.md#f-029).

## F-030 · active · Per-event shaping of a social behavior buys initiation churn, and the KL leash does not prevent it

Cold since the Gen 1 close (2026-10-28): full text, scope, invalidator and
re-verify trigger in [FINDINGS-COLD.md](FINDINGS-COLD.md#f-030).

## F-031 · active · A partnered scene runs its minimum only if the counterpart is pinned; grooming is the exception

Found 2026-08-24 by Product while checking the waterline proposal's
priors, corroborated independently here. Registered on the owner's word
the same day.

**The instrument matters as much as the number.** Polled snapshots
cannot measure scene length — the final tick of a scene clears the clock
it stamped (`api.rs:95-97`) — and `activity.state` is a one-tick
resolution flag for play, eat and drink besides. `GET /events/activity`
records the true span, **inclusive: `ended - started + 1`**
(`events.rs:30-42`). Both threads dropped the `+1` on first reading and
saw every activity quit a tick early; the arithmetic now lives in
`live_census.py` beside its citation.

1. **Measured spans, 1000 scenes, live world**, against the config
   windows they were drawn from:

   | scene | n | mean span | config |
   |---|---|---|---|
   | cosleep | 79 | 6.00 | sleep 6-12 |
   | sleep-solo | 80 | 6.01 | sleep 6-12 |
   | groom-solo | 39 | **4.00** | bath 4-8 |
   | groom-other | 113 | **3.37** | bath 4-8 |
   | duet | 99 | 2.00 | play 2-5 |
   | play-solo | 103 | 2.00 | play 2-5 |
   | play-element | 136 | 1.74 | play 2-5 |

2. **The controlled comparison is groom-solo against groom-other**:
   one activity, one config window, differing only in whether a
   counterpart exists who can leave. Solo lands exactly on its minimum;
   partnered runs 0.63 ticks short. Everything else lands exactly on
   its minimum.
3. **The mechanism is which activities pin their partner.**
   `prune_dead_activity` (`world.rs:476`) ends a partnered groom through
   `is_available_friend`, and the groomed cat is never in an activity —
   it stays free to walk away mid-scene. Duets and cuddles lock both
   parties via `reciprocal_duet`; sleepers do not move. Grooming is the
   only partnered activity whose counterpart is unpinned, and it is the
   only one that dies early.
4. **play-element's 1.74 reproduces the banked bug `mlen` of 1.8**
   through a different endpoint than the Rust chase census that produced
   it — an independent check on the critter-play EV work, which the
   `bugs2-grid-analyze.ev()` docstring already warns must use measured
   rather than nominal lengths. Same lesson, second instrument.

**Why it is worth a number**: every EV that prices a partnered scene
multiplies by its length, and nominal config bounds overstate grooming
by 15%. It also predicts where a rule that reshapes pairing could show
up as a *duration* effect rather than a count effect — grooming is the
only partnered activity with slack.

**Scope**: served world, current roster, one 1000-scene window per
thread. Says nothing about scripted-only compositions, and the gap size
is a function of how mobile the groomed cat is, so a calmer roster
should show a smaller one.

**What would invalidate it**: a groom-other mean at or above 4.00 on any
roster (would mean the counterpart-gone rule is not what shortens it);
or a duet mean below 2.00 (would mean `reciprocal_duet` does not pin
what it appears to pin).

**Re-verify when**: any change to the friend helpers, `prune_dead_activity`,
or the duration config; and before pricing any partnered scene in an EV.

## F-032 · superseded by F-033 · The most social policy pays a turn tax: `Idle` in `last_action` is the legality funnel refusing an ask

Claimed from served-world evidence that Biscuit's `idle` ticks were
`action::validate` refusing a partnered-play proposal rather than the
policy choosing to idle — flagged at registration as an inference,
because proposals are not observable from outside the engine. The
settling experiment it specified was run the next day and **narrowed
it: the refusal is real, large and uniquely Biscuit's, but it is 45% of
the seat's idle, not all of it.** The majority is a genuine idle
proposal. Full text in [FINDINGS-ARCHIVE.md](FINDINGS-ARCHIVE.md);
the measured split, and the part that survives, are F-033.

## F-033 · active · Every seat pays a partnered-action refusal tax, in its own currency — but for Biscuit that is under half its idle; the rest it chooses

*Numbers retired 2026-09-02 by F-039 (live stamp read, post-048): the 4.7% figure below is seam-probe history; the mechanism stands, and so does the owner's 3.5% INVESTIGATE line.*

Settles the inference [F-032](FINDINGS-ARCHIVE.md) registered and could
not test. Run 2026-08-25 on the owner's word — the experiment F-032
itself specified. Cites [F-031](#f-031--active--a-partnered-scene-runs-its-minimum-only-if-the-counterpart-is-pinned-grooming-is-the-exception)
for the unpinned-counterpart mechanics it lands on.

**Why the served world could not answer it.** `last_action` carries the
ENFORCED action (`world.rs:338`), so a chosen idle and a refused ask are
spelled identically. Three actions exist per tick — `proposed`,
`validated`, `applied` (`seam.rs:212`) — and the served surface shows
only the last.

**Method**: all five served artifacts seated as external agents on the
certification config (`phase1-cutover-bugs2.toml`), greedy argmax under
the engine's own mask — the served decision rule (`behavior.rs:14`,
"argmax over masked logits, ties to the lowest index"; no served seat
enables sampling). Eval band 870001–870010, 10 seeds × 20,000 ticks =
200,000 ticks per seat. Instrument
`exp-006a-biscuit-corner/idle_rewrite_probe.py`.

1. **Of the ticks whose applied action is idle:**

   | seat | applied idle | CHOSE idle | was REFUSED into it | idle rate |
   |---|---|---|---|---|
   | **Biscuit** (e006a-L-04-s3) | **21,047** | **11,668 (55%)** | **9,379 (45%)** | **10.5%** |
   | Clementine | 4,196 | 12 | 4,184 | 2.1% |
   | Kittybear | 3,490 | 0 | 3,490 | 1.7% |
   | Pumpkin | 3,040 | 0 | 3,040 | 1.5% |
   | Miso | 1,873 | 6 | 1,867 | 0.9% |

   Counted two independent ways — from `survived` (`validated ==
   proposed`) and from decoding the proposal against the fixed menu —
   which agree to the unit on every seat.

2. **F-032 was 45% right, which means it was wrong as stated.** "Biscuit
   isn't idling, it's being refused" does not survive: the majority of
   its idle is a genuine idle proposal that passed validation. The
   register's own caveat — that a chosen idle fits the same served data —
   was the live possibility, and it was the larger half.

3. **The refusal is real, and it is partnered play specifically.** Of
   Biscuit's 9,379 refusals into idle, **9,187 (98%) were `play_kitty`** —
   a duet proposal naming a partner slot. Not solo play, not critter
   play. Duet legality is `is_conscriptable_friend`: the partner must be
   free.

4. **The tax is not Biscuit's alone — it is the general shape, and each
   seat pays it in its own currency.** Every seat's refusals are
   dominated by partnered actions whose counterpart can leave:

   | seat | top refused proposals (into idle) |
   |---|---|
   | Biscuit | `play_kitty` 9,187 · move 113 |
   | Clementine | `groom_kitty` 2,402 · move 1,277 · `sleep_kitty` 418 |
   | Kittybear | `groom_kitty` 1,958 · move 1,122 · `sleep_kitty` 286 |
   | Pumpkin | move 1,367 · `groom_kitty` 1,246 · `sleep_kitty` 201 |
   | Miso | move 1,091 · `sleep_kitty` 619 · eat 96 |

   The groomers are refused on grooming exactly as F-031 predicts —
   grooming is the partnered activity whose counterpart is never pinned.
   Biscuit is refused on duets because it is the only seat that proposes
   them at volume. (`move` refusals are a different rule: walking into
   an occupied tile.)

5. **Biscuit is the only seat that ever chooses idle** — 11,668 against
   0–12 for every other seat. The character-trained policy learned to
   propose a do-nothing turn; the four older policies essentially never
   do. That is a fact about the training, not the enforcement, and
   F-032 missed it entirely.

6. **The mechanism is structural, not a policy flaw.** The mask probes
   the FROZEN start-of-tick snapshot while enforcement runs in the
   kitty's apply slot, after earlier kitties' turns have applied —
   `meow.rs:167`, "probing shares the RULE, not the MOMENT", which states
   the activity mask probes `validate` the same way. A partner
   conscriptable at start-of-tick can be gone by the apply slot. No
   policy could avoid this by choosing better.

**Instrument warnings, each of which cost a wrong answer first:**

- **`survived == 0` is not a synonym for "refused"**, and reading it as
  one overstates by ~2×. It is `validated != proposed` and reflects
  `validate` ONLY; `enforce_durations` runs afterwards and normalizes a
  continuing proposal to the continuation action (`world.rs:487`).
  Biscuit's 21,121 rewrites split 9,379 into idle and 9,756 into `play`,
  the latter being scenes already running.
- **`survived == 1` does not mean applied == proposed**, for the same
  reason. An earlier version of this probe learned the menu from those
  ticks and had index 25 report as both `play` and `groom`.
- **The activity menu is a fixed 34-entry table** (codec v2, spec 028);
  schema 3 widened only the message head (`codec.rs:54`, "the 34-entry
  activity menu did NOT move"). The probe pins
  `ACTION_SCHEMA_VERSION == 3` and asserts alignment the engine
  guarantees: `validate` has `Action::Idle => true`, so a proposed idle
  can never be rewritten, and a misaligned table would show one.

**Scope**: certification config, greedy, the five served artifacts, one
eval band. The served world is a different config and this was not
re-derived there; the lab's 10.5% applied-idle rate against the served
15% is supporting, not proof. F-032's served-side
77%-of-scene-endings statistic was NOT re-measured here.

**What would invalidate it**: a seat proposing partnered actions at
volume with few partnered refusals (would break the concentration);
Biscuit's choice/refusal split moving materially on the served config or
another band; or a served-side replay showing the in-engine behavior
does not use the greedy masked argmax this assumed.

**Re-verify when**: any change to `is_conscriptable_friend`, the
`validate` legality arms, the mask's probe moment, or duet duration
config — and before pricing any partnered action in an EV, where the
refusal rate is a real cost that current EVs omit for grooming as well
as for play.

**What it opens**: the Biscuit 3.0 question is two questions, not one.
The refusal half (4.6% of ticks) is addressable — `Play { target: None }`
is always legal, so a solo-pounce fallback keeps the ask and drops the
tax, and the same argument extends to the groomers' `groom_kitty`
refusals via `Groom { target: None }`. The chosen half (5.8% of ticks)
is not a bug but a trained behaviour to understand, and it is the
larger one. Whether either moves a seat's happiness is still
unmeasured: that needs a needs-servicing count per turn, not this probe.

## F-034 · active · Here* vocabulary cloning is a cliff, and the cliff sits between 5.6% and 8.2% corpus share — not near 1%

The here-word density screen's Half A
(`here-word-screen/RESULTS.md`, run 2026-08-31 on the owner's
2026-08-30 word; plan pre-registered @ 8c50fda with the spec-043
FR-006 amendment). Extends [F-022] from two far-apart anchor points
(0.2% → mute; purr-rich ≈10% → fluent) to a bracket on the boundary
itself. Method: four paired-seed corpora on the anchor composition at
`announce_here` off/1/4/16 (realized here-share 0 / 8.18 / 5.56 /
2.36% of decisions), one V4 clone each under the verbatim
`train_clone6.py` recipe, readouts conditioned on the here-kinds per
[F-015].

1. **The cliff.** Opportunity-use (kind legal, no want spoken): A1 =
   .58–.80 by kind, msg@1 on here-rows .8748, predicted emission
   84.5/1k tracking its source's 82.4/1k per kind. A2 and A3: ≤ .0033
   use, ~0.3/1k — functionally mute at 5.6% and 2.4% corpus share.
   Nothing in between: the middle of the dial belongs to the mute
   side.

2. **The vocabulary is free where it works.** act@1 .7986–.8037
   across all four arms (no action-learning cost at any density), and
   reward streams byte-identical across arms at all 25 paired seeds —
   the welfare charge is exactly zero by gate-zero construction
   ([F-026]'s report-only expectation, satisfied at equality).

3. **Qualifier that keeps this honest**: "mute at 5.6%" is a claim
   about the registered recipe's budget (20 epochs, patience 3); A2's
   val loss was still falling at the cap. Epoch-extension on A2 is
   the registered follow-up before treating the cliff's location as
   an asymptote. Emission is offline masked-argmax on held-out
   states; live-rollout confirmation wants the lab binding gate.

**What it changes**: fog corpus seeding uses `announce_here = 1` as a
collection parameter, not a swept dial (per-kind cooldowns cap the
ceiling near 8%, so period 1 is the only workable setting); the
parked Here*-teacher likely collapses into "the scripted behaviors
with the knob armed" (plan §8, owner's read pending); and exp-003's
0.2% channel sat 40× under the cliff, not 5× — its failure was never
a near-miss.

**A1b addendum (2026-08-31, owner-routed, declared before
collection)**: a fifth arm at period 2 (realized share 7.61% — the
cooldown compression again) lands mid-transition: emission RATE
fluent (73.6/1k vs source 76.9) but placement half-right
(opportunity-use .35–.56, msg@1 on here-rows .691). So the shape is a
steep transition, not a pure step: mute ≤ 5.6%, half-fluent at 7.6%,
fluent at 8.2% — the whole rise inside ~2.6 points of corpus share.
A 0.57-point share difference (A1b→A1) buying +.14–.24 of use hints
raw share may not be the only driver (period 1 is also the most
regular context); one clone per arm, so the shape is the claim, not
the decimals. Decision unchanged: period 1 dominates — period 2's
corpus is barely smaller and strictly worse placed. act@1 .8009
(flat), rewards byte-identical (gate zero holds for the fifth arm at
all 25 paired seeds).

**Extension addendum (2026-08-31, owner-routed, decision rule
pre-declared)**: fresh 60-epoch/patience-10 runs on A1/A1b/A2 (the
qualifier in point 3, discharged). Verdict: **the cliff is
density-shaped, not budget-shaped** — 3× budget moved opportunity-use
by noise (A1 .60–.81, A1b .39–.54, A2 still mute at ≤ .027 with
here_critter exactly 0; no plateau-then-jump anywhere in the
histories). The 20-epoch recipe stands for vocabulary seeding.
Separate fact the probe surfaced: the budget DOES buy action
fidelity — act@1 +1.6–2.0 points on every arm (.80 → .82) at 3×
cost; whether that trade is taken for Fog Gen 1's BC stage is an
owner call at the fog prereg.

## F-035 · active · The waterline charge is a magnet before it is a fence: charge-blind arms drift TOWARD the water's edge, and only a charge-aware chooser turns the price into avoidance

The water's-edge avoidance smoke
(`edge-avoidance-smoke-2026-09-01/RESULTS.md`; prereg @ 978b436,
addendum @ 0049a70, both before collection; engine main @ dfa4b6b —
044 charge + both 045 dials). Six arms × three paired seeds, scripted
needs-driven lab worlds at the canonical economy.

1. **The magnet.** Cross-waterline adjacency (share of adjacent
   pair-ticks) rises with a blind charge: no-charge 6.61% → blind
   factor 1.0 = 11.84% → blind factor 10 = 13.70%. Mechanism: the
   charge raises bath need, and bath-relief seeking sends cats to the
   water. A welfare price whose payers cannot see it CONCENTRATES the
   population at the priced boundary.

2. **The fence needs eyes.** The charge-aware ladder reverses the
   drift: aware factor 1.0 lands at 7.66% (option_a) / 8.07%
   (bidirectional) — ~4 pp below blind at the same factor — and the
   10× positive control drops to 4.84%, ≤ half its drift-matched
   blind twin in pooled share and below it in every seed pair.

3. **Membership does not matter to behavior at factor 1.0**:
   |option_a − bidirectional| = 0.41 pp under the aware ladder, no
   consistent per-seed ordering, and the play channel obeyed the
   reciprocity prediction (C ≈ D, the pricing-bug canary stayed
   quiet). The step-4 bidirectional call gets clean data: no
   meaningful edge-avoidance difference between the rules.

**Ruling on this data (owner, 2026-09-01)**: no contagion for Gen 1
(`contagion-shelved-2026-09-01.md`). Point 1 is the argument: a Gen 1
learner cannot see a wet neighbour, so an armed charge trains arm B's
world. The wet-side vector (wet cats keeping away from dry friends) is
unpriced under BOTH membership rules — the wet member never pays
contagion — so it is not learnable in this economy at all. F-035 is
Gen 2 pricing input; reopen triggers are in the ruling doc.

**Scope**: scripted choosers only (BC clones imitate the teacher —
this is exactly the corpus-side question); canonical
`groom_cuddle_relief` 0.5; the 10× arms run a disclosed nonstandard
budget (ceiling 25 / safeguard 98 / distress 99), directional only.
**Invalidated by**: changes to the charge formula, the ladder value
shape, or E_ticks bounds; fog changing what a cat can see near water
(step-5 shakeout re-checks). **Re-verify when**: any proposal to arm
`contagion_aware_ladder` on a SERVED world — the groom collapse down
the aware arms (pair-ticks 1,893 blind → 527 aware-bidirectional) and
the two low Clementine happiness samples say the decline seam
redistributes relief in exactly the population 041 burned.

## F-036 · active · The needflow model is not a proxy for the scripted teacher: three engine gates it lacks invert the sleep niche and make relief dials invisible to `needs_driven` decisions

Needflow lab validation (`needflow-lab-validation-2026-09-01/RESULTS.md`;
prereg @ af4c5ea, scorer @ 261bbb7, both before collection; engine
main @ 055dc5b). Six 20k-tick `needs_driven` runs, three paired seeds
at `groom_cuddle_relief` 0.5 (canonical) and 2.0 (served bump).

1. **The 041 rest niche is wide open under scripted seats.** Rest is
   the largest scene class at 29.7/1k cat-ticks (model 12.8), 707–772
   scenes per 5,000-tick sub-window in every seed, both tiers emitting
   (mutual ≥1,392, drip ≥2,270 scenes per run). The emit gates the
   timeline asked for pass with room.

2. **Cosleep : solo sleep is 0.32 : 1, not the model's 5.6 : 1.**
   Engine cosleep routing (`needs_driven.rs:193`, spec 028 FR-020)
   opens only at cuddle ≥ `cuddle_real_threshold` (15.0); the 041 rest
   economy holds standing cuddle at ~14.2, so 1,153 of 1,513 naps in
   one run went solo. needflow offers cosleep to any adjacent pair
   ungated, and cosleep strictly dominates solo sleep there. Rest is
   eating cosleep's demand; whether that is the intended sleep niche
   is an owner design question.

3. **Relief dials are invisible to scripted decisions.** The bump moved
   groom-other −11%, groom-self +4%, rest −1%, bath −1% (model +76 /
   −62 / −55 / −34%). `groom_cuddle_relief` enters the engine only as
   payout and in the inert 045 exposure seam; kitty-grooms are
   initiated solely by `groom_response` to an audible bath meow (lab
   groom-other 2.4/1k vs model 15.8). A relief-pricing proxy predicts
   swings that neither scripted seats nor the frozen roster can
   produce; only a learner trained under the dial can answer a
   reprice.

**Scope**: scripted `needs_driven` seats on the served 20×20 world,
no fog, contagion shelved. needflow's calibration subject was the
POLICY roster; this is the first measurement of the scripted chooser
against it, and the bands it produced are the Gen 1 BC teacher's own
mix, which is why they (not the model's) are step 5's reference.
**Invalidated by**: changes to `cuddle_real_threshold`, the
`groom_response` seam, the 041 relief dials, or fog changing what a
sleepy cat sees within `sunbeam_reach` (step 6 re-derives the bands).
**Re-verify when**: needflow is next used to predict a scripted or
BC-clone mix — add the gates first, or don't use it for that.

## F-037 · active · The action-shape collapse detector names a lock but does not lead the watchdog: on every recorded starving lock it fires 48–147 ticks after the distress alarm would, and its healthy margin is 0.07

Collapse detector v0 (`collapse-detector-v0/RESULTS.md`; prereg,
detector and guard @ 72ca108 before any trace was read). Trailing
W = 200 share of one partnered activity (resting/sleeping/grooming
with partner flag) > 0.50 sustained D = 200, per seat; mutual-pair
share the same, per pair; need spread report-only. Run on all 19
exp-006 forensics traces.

1. **Validated as pinned.** 3/3 MUST-FIRE locks fire (880030 twins,
   880008 twins, 880015 triadic), the SHOULD-FIRE pile fires, 11/11
   MUST-SILENT traces stay silent. The discriminating negative holds:
   solo-s3-880013's watchdog equivalent fires at tick 6,585 on directed
   travel while the detector sits at 0.32. That is the one case the
   welfare instrument cannot separate and this one can.

2. **Not an early warning.** Detector first fire vs watchdog equivalent:
   4619/4566, 1368/1221, 3717/3669, 591/514. A ~300-tick lock is needed
   to cross-and-sustain, and every recorded lock had a need in distress
   within ~120 ticks of onset. The ROADMAP's "fires earlier because
   needs must starve first" premise is wrong for these locks. What
   survives is the naming (seat, family, pair) and the untested claim
   about welfare-quiet locks — no such lock exists in the trace set.

3. **The bar is on a knife edge on the healthy side.** Realized lock
   share is 0.82–0.83 (F-027's 98% was the action HEAD's share; the
   re-entry idle tick between naps takes ~17%), healthy peak 0.43 (a
   51-tick partnered sleep run at tick ~11.5k in solo-s3-e1s1-870003).
   Mutual-pair share confirms twins (0.58–0.67) but misses the triadic
   pile (0.38). Need spread reaches 93/82/73 on silent traces and stays
   report-only.

**Scope**: sleeping-with-partner locks only (every positive is one);
exp-006 trace format; 200k healthy ticks, not the ROADMAP's untraced
2.4M. **Invalidated by**: W/D/bar changes (v0.1 with its own prereg
line); a lock class outside the three partnered families.
**Re-verify when**: H4 is pinned at step-5 kickoff — the owner picks
the bar with the 0.43/0.82 numbers in hand, and a live v1 re-runs this
set before it watches a seating.

## F-038 · active · Scripted Biscuit's comfort dial buys food promptness linearly and pays in element play, never duets; a food-only weight band keeps play by leaving cuddle (her highest need) unserved; the spec-042 score at t_partner 5 refuses nearly every friend and halves the roster's duets

Biscuit 3.0 comfort sweep (`biscuit3-comfort-sweep-2026-09-01/RESULTS.md`;
prereg + tooling @ 893cd48 before collection). Scripted `playful`
Biscuit with four `needs_driven` seats, canonical 041 economy
(`groom_cuddle_relief` 0.5), 20k measured ticks × 2 seeds per arm,
20/20 runs valid, watchdog quiet throughout.

1. **The comfort curve is smooth, no free lunch.** Eat time-above-30
   0.455 / 0.362 / 0.236 / 0.132 at comfort 55 / 45 / 35 / 30 (in-run
   scripted floor 0.100); eat p50 88 / 56.5 / 26.5 / 10.5 ticks;
   hungry-play share 0.65 → 0.15. Total play 1.00 / 0.93 / 0.76 / 0.70x.
   Every play point lost is element play (162 → 96/1k); duets hold at
   67–79/1k in all arms. Seeds agree to two digits. Biscuit happiness
   77 → 85, demand price 22.7 → 15.2.

2. **The weights arm passed P3 by leaving cuddle unserved (corrected
   2026-09-01).** w35 (eat/drink/sleep at 35, bath/cuddle at 55) closes
   0.51 of the eat time>30 gap vs flat c35's 0.62 and keeps 209 vs 179
   play/1k, so P3 passes as pinned. But cuddle is Biscuit's highest
   elevated need at c55 (mean 30.8, 50% of polls ≥30; roster 16.5/13%),
   above eat (28.3/45%). w35 leaves it at 27.0/42% while c35 takes it to
   20.7/26%. The play w35 "saved" is play she did while wanting a
   cuddle. Bath is the one need genuinely fine at 55 (15.6, 7% ≥30; 1%
   at c30), so a weight band covering everything but bath is within
   noise of flat comfort. Welfare has to be read on all five needs;
   P3 as pinned read only eat. Weights are not recommended.

3. **The spec-042 candidate dials are not shippable.** With `t_partner
   5.0` against a realized mean partner play need of 4.3 at duet
   start, Biscuit's duets fall 72.6 → 8.9/1k at every comfort; she
   substitutes elements (total play flat, +4–9%) and the four other
   seats lose 51–57% of their duets. Partner need at duet start rises
   4.3 → 10–12 as designed. Food unmoved. The next campaign sweeps
   `t_partner` and `w_serious` with this as baseline.

4. **Two prereg measures failed as bars.** Armed excursions per 1k
   RISES as comfort drops (6.3 → 8.2): a meal resets eat to ~0
   (35/tick × ~2 ticks), so meals per 1k ∝ 1 ÷ eating level (6.6 at
   mean 48.5, 9.5 at 30.3), and an excursion is a meal that started
   above 30. The floor seats' 4–5/1k comes from eating at 21–27, below
   the line 70–85% of the time. The count measures how often a cat
   gets hungry enough to cross 30, not how late she is. "Low-need play" (scenes
   starting with food needs < 30) rises 1.6–2.9x for the same reason a
   fed cat lives below 30. Neither can serve as a bar again.

5. **Addendum 1 (c25 / c20, 2026-09-01): parity reached, play halves,
   meows vanish.** Both arms reach roster-parity welfare on all five
   needs (Biscuit's share ≥30 within 0 of the roster at c25, below it
   at c20); total play 0.58x / 0.45x of c55 (predicted 0.55–0.65 /
   0.40–0.55); duets begin to fall below 30 (67 → 56 → 54/1k) after
   holding 67–79 from 55 to 30; roster duets slide to 0.88x / 0.85x
   (bar 0.85x). Excursions per 1k turned over as point 4 predicted
   (8.2 → 3.15 → 2.02, under the floor). Her announce share fell to the
   roster's at c25 (0.39 → 0.19): below the announce threshold she
   leaves play before arming, so the hungry-Biscuit meow disappears
   from the client. c30 already met parity within +0.04 on the main
   raws.

6. **Addendum 1b (c32 / c28, 2026-09-01): the bracket fails on opposite
   sides.** c32 misses parity on eat, sleep and cuddle (+0.07–0.09,
   both seeds) at 0.76x play; c28 passes (+0.02–0.03) at 0.65x. Welfare
   and play are monotone over 35/32/30/28/25 (eat ≥30 0.23 → 0.18 →
   0.13 → 0.10 → 0.06; play 0.76 → 0.76 → 0.70 → 0.65 → 0.58) with one
   flat step: c32 keeps c35's play at a third less time hungry. Between
   32 and 28 each 2 points of comfort cost ~0.05x of c55 play and buy
   ~0.025 of every gap; duets hold 63–67/1k down to 28. Report-only:
   one c28 seed carried a 250-tick one-sided cosleep (Biscuit `resting
   with_friend` Miso while Miso idle, cuddle 82 → 100, happiness 25.4,
   watchdog quiet, self-resolved), the same shape as the served soak's
   Miso event; a roster mechanic a seed exposed, not a comfort effect.

7. **Addendum 2 (the spec-047 consent gate at c30, 2026-09-01): the
   gate works and costs a quarter of her duets plus parity.** On the
   f45a880 binary, `consent_line` absent reproduces the old c30 run
   tick for tick (15,355 / 15,144 events, all shared: C1 at the event
   level). At `consent_line = 30`, the share of her duets that
   conscript a friend with a non-play need over 30 falls 0.21 → 0.01
   (C2), but duets fall 67.3 → 49.0/1k (0.73x, bar 0.90x, predicted
   60–64) and the lost duets go to elements (95.7 → 117.3/1k, total
   play 1.02x), not to the idle eligible friend the offline pricing
   put within 2 tiles in 84% of blocked starts. Roster duets 0.83x is
   entirely her lost duets counted on their side (roster-roster starts
   34.8 → 35.7/1k, flat). Her E1 gaps widen +0.006–0.028 (cuddle most,
   both seeds) and E1 flips to MISS at c30 (+0.05–0.06 vs 0.05); the
   roster's shares improve 0.006–0.014. Partnered refusal tax 4.9% →
   3.4% of her ticks (scripted; the 4.9% matches F-033's policy 4.7%).
8. **Addendum 3 Half A (2026-09-02): a `w_value` re-admission dial
   cannot buy the duets back.** At `w_value` 0.25 / 0.5 (`w_busy` =
   1/`w_value`) under the gate, duets move 49.0 → 53.6 / 51.2 per 1k
   while element play falls 117.3 → 49.5 / 31.4 and SOLO play appears
   from zero (54.8 / 67.3 per 1k); loiter share (idle beside a busy
   friend) rises 0.137 → 0.18 / 0.20. Any `w_value` > 0 also switches
   on mid-scene friend admission (`selection.rs:499`), and
   `expected_wait` prices a resting or past-minimum friend at zero, so
   a settled rester out-scores every critter; Biscuit walks over,
   cannot conscript, and the solo backstop fires beside it. R7 / R8
   unmoved.

**Decision (prereg rule)**: middle case, owner's call on the curve. If
Biscuit is to be fed, use flat comfort; the food-only weight band is
withdrawn (point 2). Owner's lean 2026-09-01: c30 viable ("0.7x play
with solid element play is still very Biscuit"). Addendum 1's rule
(highest comfort passing parity with play ≥ the owner's 0.70x) lands
on **c30**, and the 32/28 bracket confirms it (c32 fails parity, c28
fails the play line); c25 is the next point on the curve (parity exact,
0.58x, half the meows), not a candidate under that line. **Addendum 2
(prereg rule)**: C2 passes, C3 / C4 / C5 miss → report the price, owner
call: ship c30 + consent with E1 at +0.05–0.06, or re-pin comfort with
the gate on (c28 / c26 + consent bracket; c28 passed E1 at +0.02–0.03
without it). **OWNER RULED 2026-09-02: the anchor is c30 +
`consent_line 30`, no re-admission mechanic** (C3 / C4 / C5 / E1
overridden on the record, RESULTS §Owner ruling). The gate binds the
scripted selector only; the RL menu picks partners directly and the
reward does not price consent, so the trained kitty inherits consent as
a teacher habit. Step 7 trains Biscuit 3.0 with `consent_line` 30 and 0
to read the transfer (RULED 2026-09-02 after Half B; `w_value`
re-admission SHELVED indefinitely, solo play is not a targeted
behaviour). **Scope**: scripted anchor only; a clone's
transfer is the training's to show. **Invalidated by**: an economy
change to `eat_relief` or the 041 rest dials; a `t_partner` re-sweep.
**Re-verify when**: the owner pins a comfort value (re-run that arm
against the then-served economy before the lineage retrain).

## F-039 · active · On the served world the refusal tax is Biscuit's alone and it is partner play: 5.13% of her ticks, 94% `play:kitty`; every other seat pays under 2.3% in grooming and movement

Live refusal baseline (`refusal-baseline-2026-09-02/RESULTS.md`; prereg
+ instrument @ 5831cde before collection). First read off the 046
stamp (`/events/refusal`) on the 2026-09-02 deploy (046 + 047 inert +
048; contagion disabled): 15,134 ticks, 95 polls, zero ring gaps,
served config `275a3d7b…bbed0`.

1. **Taxed share per seat** (refused, turn resolved to Idle): Miso
   0.70%, Biscuit 5.13%, Pumpkin 1.86%, Kittybear 1.91%, Clementine
   2.30%. Biscuit is above the step-5 INVESTIGATE line (3.5%, owner
   ruled 2026-09-01); the same ruling says Biscuit 2.0 at parity
   welfare paying this is not actionable and the reading that counts
   is Biscuit 3.0's. The other four are under the line.
2. **Biscuit's currency is partner play**: 734 of 777 taxed rows. The
   other seats' taxed play rows are 3–23 across the window; they pay in
   `groom:kitty` (150–252) and `move` (64–89).
3. **Absorbed refusals** (heard mid-scene, tick serviced) outnumber
   taxed 3,258 to 1,801. Miso absorbs the most (5.20%, 448 `sleep:with`
   from inside a sleep); Biscuit absorbs 785 play asks on top of the
   734 taxed, so about half her asks land while she is in a scene.
4. **Retention**: combined density 0.334/tick, 1.45× the taxed-only
   figure the 6,000 default was sized on; 15k-tick floor 5,014, the
   default stands.

Retires [F-033](#f-033--active--every-seat-pays-a-partnered-action-refusal-tax-in-its-own-currency--but-for-biscuit-that-is-under-half-its-idle-the-rest-it-chooses)'s
4.7% and the 4.6% seam figure as reference numbers (the 3.5%
INVESTIGATE line is the owner's and stands): those were seam-probe reads
on a pre-048 engine that counted dead-scene rows b9f9c00 removed. That
the stamp reads 5.13% after 048 took rows away says the seam probe
undercounted, not that 048 did nothing. F-033's mechanism claim (the
tax is partnered, per-seat currency) holds unchanged. **Scope**: the
2026-09-02 deploy's roster and economy. **Invalidated by**: any deploy
touching the selector, the play economy, or the roster. **Re-verify
when**: the Biscuit 3.0 cutover lands (step 7); one window, same
instrument.

## F-040 · active · Under the fog want law `want_drink` is structurally silent: water is permanent and memory never expires, so drink relief is always known; a memory reach of `radius + 0` revives it at ~12 calls per 1000 ticks and adds ~12 eat calls

Read off the fog-gen1-shakeout anchor smoke (`anchor.toml` = served
config + `groom_cuddle_relief 0.5`, `announce_here 1`,
`reply_intensity_floor 0.30`; bc-collect `--trace`, 1000 ticks, three
seeds at r=5 and three at r=4; instruments `schema_check.py` A1 and
`relief_radius_sweep.py`, both in `experiments/fog-gen1-shakeout/`).

1. **The mechanism.** `known_relief(drink)` (meow.rs) is "water visible
   or water remembered". Water pools never move or despawn and
   `memory_timeout_ticks = 0` never forgets, so the first sight of any
   pool silences `want_drink` for the rest of the run. Chow escapes the
   same fate only because an emptied bowl despawns, which refutes the
   memory (42 chow refutations in 1000 ticks; water 0). In 3000 ticks at
   r=5 no cat said `want_drink`; at r=4 one to three calls per 1000, all
   from cats thirsty before their first sight of water. Consequence for
   the corpus: no drink want and no `here_water` reply, 19 observation
   columns constant (schema_check A1).
2. **How often thirst is out of sight.** At r=5: 565 cat-ticks per 1000
   with drink ≥ 30; water in view for 438 of them (7 pools, disc ~81
   tiles); the remembered pool sat 6–8 Manhattan away in the other 127,
   never farther. So a distance gate on remembered relief has two
   regimes on a 20×20 with 7 pools: D > r stays silent, D ≤ r equals
   "visible relief only" (Manhattan ≤ r implies inside the disc).
3. **Counterfactual verbosity** (first order: recorded trajectory,
   simulated calls at cooldown 10; the D=0 column reproduces the actual
   trace within 3%). Per 1000 ticks, five cats, D = r versus today:
   drink 13/11/24 (r=5) and 5/6/26 (r=4); eat +15/0/+16 and
   +14/+11/+13; all wants +28/+12/+40 on 114/78/82 and +20/+17/+37 on
   110/120/104. Radius does not separate at this sample; seed does. Only
   eat, drink and play carry a memory clause, and play is already
   silenced by sight almost always (0–1 calls at every D).
4. **The law change asked of Product** (owner ruled 2026-09-04, spec to
   follow): `[meow] relief_memory_margin`, a remembered element counts
   as known relief only within `radius + margin` Manhattan tiles; key
   absent = today's unbounded rule; served and anchor set 0. At margin 0
   memory never silences a want (the visible clause already covers the
   disc), which is the radius-invariant reading; margin 1 trims drink
   and eat 10–20% (the D=6 column at r=5). Legality only, layout
   unchanged, A14 still recomputable from the self memory dx/dy.
   Navigation is untouched: `priced_nearest_element` reads memory
   independently of the want law, and the scripted asker does not act on
   element here-words.

**Re-verified 2026-09-05, spec 050 merged (PR #345, main 01c499e).**
Row 3 was a first-order counterfactual; these are recorded runs, anchor
config, 3 × 20,000 ticks, seeds 870001–3, five cats, calls per 1000
ticks. Key absent (the old rule): drink 0 / 0 / 0, eat 13.3 / 12.2 /
15.6, all wants 99.6 / 93.5 / 106.4. Margin 0: drink 6.3 / 5.9 / 15.2,
eat 22.2 / 23.2 / 24.2, all wants 116.6 / 116.1 / 121.4. Margin 1: drink
3.9 / 7.6 / 14.9, eat 21.1 / 22.2 / 19.8, all wants 110.5 / 110.8 /
113.3. So the headline's ~12 drink calls is 6–15 measured (mean 9), the
eat gain is +9 to +11 rather than the forecast's 0 to +16, and margin 1
trims eat by about 8% while drink does not separate from margin 0 at
three seeds (seed 870003 runs at 15 under both). Two corrections to the
instrument behind row 3: `relief_radius_sweep.py` counted every need
tied for the maximum as the top need (`v < top`), where
`needs.rs::highest_pressure` breaks ties by `NeedKind::ALL` order, and
eat = drink = sleep ties are common early in a run; with the engine's
tie-break the seed-870001 forecast at D = r falls from 13 to 9 drink
calls (eat unchanged at 39). `schema_check.py` A9 had the same tie read
(3 false violations on the margin-0 re-smoke) and A9/A14 now read the
margin. The served config's rate is lower (Product, 20k, floor unset,
`announce_here` 0, `groom_cuddle_relief` 2.0: 23 drink calls, ~1.2 per
1000), so the rate is config-shaped; which of the three anchor keys
carries the difference is not identified.

**Ablation 2026-09-08 (owner: "#349 ablation now").** The gap is the
roster, not a key. Four arms, 3 × 20k, seeds 870001–3, bc-collect on
anchor.toml with one key at the served value each and a fourth with all
three at served values; drink calls per 1000: groom 2.0 → 6.5 / 5.1 /
11.8, `announce_here` 0 → 6.0 / 7.4 / 13.2, floor unset → 4.9 / 7.8 /
13.8, all three served → 4.6 / 11.5 / 13.7 (anchor 6.3 / 5.9 / 15.2).
No key moves it. Product's 23 per 20k came from
`tests/relief_memory_margin.rs`, whose `served_all_scripted()` sets
every seat to `needs_driven`; the served roster seats Biscuit (kitty
2) on `playful`. Reproduced: all-scripted config at the served seed
20260718 reads 23 (Product's number), at 870001–2 reads 17 / 26; the
same config with Biscuit `playful` at 20260718 reads 278 (13.9 per
1000). Per kitty on the anchor, Biscuit says 60–70% of the drink calls
(88 of 126 at 870001, 176 of 304 at 870003) and about half the eat
calls: the playful seat spends its ticks on critters away from bowls
and pools, and under margin 0 it must see water to know relief. So
the served world hears drink at the anchor rate, the declared
`expected_per_1000` for want_drink is roster-shaped (drop Biscuit's
seat and it falls 8×), and drink is not a thin kind at corpus scale
(~7,000 rows over 800k ticks). Side read: `announce_here` 0 cuts
`here_water` from ~160 to ~54 per 1000 and floor unset cuts it to 0;
neither touches the want rate.

**Scope**: fog-era want law on the served 20×20 (7 pools, 6 bowls),
radius 4–5, scripted seats. **Invalidated by**: a water element that
despawns or moves, a non-zero `memory_timeout_ticks`. **Re-verify
when**: the step-5 radius screen (the rates above are r = 5 only).

## F-041 · active · The answers-me bit is strict (`their_here > my_want`), so a want re-called on the reply's own tick hides the reply; equal cooldowns lock the pair into that phase

Anchor smoke as F-040, schema_check A16. `push_answers_me`
(observe.rs:619) lights the bit when the friend's freshest audible
here-word is strictly newer than the observer's freshest paired want.
The scripted wanter re-calls every `recent_window_ticks` (10) and the
scripted responder replies every 10 as well, so once a reply lands on a
re-call tick the two stay in phase: kitty 2 `want_sleep` at 456/466/
476/486, kitty 4 `here_sunbeam` replies at 466/476/486, bit never 1 for
kitty 2. 3 of 169 replies in 1000 ticks were invisible this way; 0
bits were lit without a reply behind them.

The reading is engine semantics, not a wiring fault: the same-tick want
is a new, unanswered want. The cost is to learners: the tie-breaker the
reply bit exists to expose (the answered cat should stop asking and
walk) is absent for exactly the cats asking at the cooldown cadence.
Two ways out if it matters at step 5: compare `>=` when the here is a
`reply`, or read the bit on the want's tick as well. **Scope**: served
cooldown 10 for both wants and replies. **Invalidated by**: a reply
cadence that differs from the want cadence. **Re-verify when**: the
step-5 reply-here bar is read (a miss with A7/A8 green points here
first).


## F-042 · active · The cert battery run on the served composition under the trained clock is the live prior: every Fog Gen 1 seat's 48 h live mean sits within 0.25 of its battery mean

Fog Gen 1 soak, `fog-gen1-cert/soak-2026-09-18.md` (48 h, 216,000 ticks
on a fresh 0.3.0 world, 8,507 polls). The cert battery
(`fog-gen1-cert/RESULTS.md` §"Welfare gates", eval band, 30 × 20k, the
five served artifacts under the trained clock on the served config)
gave per-seat means Miso 92.94, Biscuit 91.06, Pumpkin 93.06, Kittybear
92.96, Clementine 92.33. Live over the whole window: 92.93, 91.02,
92.84, 92.81, 92.38 (roster 92.40 against 92.47); open-to-close moves
under 0.35 at every seat. The scripted priors in the same seats are
85.2–88.6, so the transfer is not a coincidence of a flat landscape.

The Biscuit 2.0 soak (`exp-006a-biscuit-corner/soak-2026-08-25.md`) had
to read its roster against a probe band from a different four-seat
roster and sat 0.7 under it; the gap was the comparator, not the world.
**Promotion**: the soak prior for a deployed roster is the battery on
that composition, run with the seam check green (positions and actions
matching the box for a pinned seed), and nothing else. **Scope**: five
distinct networks, 20×20, vision radius 4, tick 800 ms, the battery
under the trained clock. **Invalidated by**: a live seat mean more than
1.0 from its battery mean over a 48 h window with an unchanged config.
**Re-verify when**: every deploy soak, and whenever the clock or config
between battery and box differs (the seam check is the first suspect).

## F-043 · active · The distress tail of a policy roster is a roster property, not a seat's: in the swap legs 30 of 55 crossings land in a seat whose mind did not change, and live it shows as brief eat episodes at the pacing-search seat

Report-only swaps in `fog-gen1-cert/RESULTS.md` (every arm into every
seat of gen1-A, eval band, 100 legs × 30 runs): 55 of 3,000 seat-runs
reached distress age ≥ 150, 25 in the swapped seat and 30 in an
unchanged one; by seat Pumpkin 21, Biscuit 18, Kittybear 13, Miso 3,
Clementine 0. The served composition crossed 0 times in 1.2 M lab ticks
(worst age 112) and 0 in the two replication bands (14, 82). Live, 48 h
on the box: six episodes in 216,000 ticks (0.028 per 1k), five `eat` and
one `cuddle`, Pumpkin 3 / Biscuit 2 / Kittybear 1, longest sampled age
76; Pumpkin's is the pacing-search shape the probe series named (eat
and drink at 100, a two-step dither with chow in view). The Biscuit 2.0
roster's soak produced one episode in 229,510 ticks.

The reading: the tail is set by who the neighbours are, because the
starving cat's relief runs through partners and shared food pressure,
so a seat's clean 30 runs certify the seat only in that roster.
**Scope**: five-network rosters on the 20×20 fog config; distress age
≥ 150 as the crossing. **Invalidated by**: a swap battery where over
80% of crossings sit in the swapped seat. **Re-verify when**: each Gen 2
battery (the stuck detector, #389, is the intended fix for the pacing
shape), and any live rate over 0.1 per 1k ticks.

**Gen 2 read (2026-10-22)**: the re-verify fired (a Gen 2 battery: the swaps digest, `gen2-cert-battery-2026-10-20/RESULTS.md` §"Swaps digest"). Ten one-seat swaps of the certified roster rot2 at 20×20 (alternates trunk-s9 and trunk-s10, each in each seat, 30 worlds per leg): 6 cat-worlds crossed 150 ticks of distress and 0 of them sat in the swapped seat; four of the six were one world (905029), where the certified roster itself has no streak over 150. The roster-property reading holds for the Gen 2 lineage; the happiness change sits in the swapped seat (that seat moves most in eight of ten legs, −1.139 to +0.409; never over 0.14 at any other seat) and the tail does not.

## F-044 · active · Single-network probes overstate the catastrophe tail: nine crossings in 618 world-probes with one mind in every seat, none in 1.2 M ticks of the five-network composition

`fog-gen1-cert/RESULTS.md` §"Welfare and the stop rows" and §"Welfare
gates": the probe series (206 reads, 618 world-probes of 2,000 ticks,
one candidate network seated five times) produced nine watchdog
entries, two long (ages 1,162 and 525), three of them the pacing-search
shape and one a social lock-in (Miso and Biscuit in a mutual
RestWith/SleepWith/PlayKitty loop with eat 0.96). The five distinct
networks in their own seats produced no age over 112 in 30 × 20k on two
bands. The probe tail is F-027's twin artefact under fog: a mind
partnered with copies of itself locks in a way it does not with other
minds.

**Promotion**: five distinct networks is the seating rule (owner
2026-09-16), and a probe's welfare stop rows are read as a training
tripwire, not a live prediction; Gen 2 adds the identity input so a
twin knows it is one. **Scope**: fog Gen 1 lineage, single-network
probes vs a five-network eval. **Invalidated by**: a five-network
composition crossing at the probe rate (about 1.5 per 100 world-probes
of 2,000 ticks). **Re-verify when**: the seating rule is relaxed (Gen 2
identity input), or a probe series is used to gate a deploy.

**Gen 2 read (2026-10-22)**: the re-verify fired (the seating rule was tested at Gen 2 with the identity input). Five copies of trunk-s2 locked roster-wide at 20×20 in 1 of 30 worlds (seed 905008, every seat's distress onset within 60 ticks, a five-cat co-sleep pile; `gen2-cert-battery-2026-10-20/RESULTS.md` §"s2 stop investigation"), and five copies of trunk-s4 aborted 11 of 30 worlds at 100×100, while the five-network roster rot2 had no stop at any size (§Phase C). The owner kept the rule the same day (deviations entry 4's correction paragraph; battery DECLARATION §Correction): the single-network seatings are all-copies stress reads. F-060 carries the Gen 2 numbers.

## F-045 · active · Distinct minds disperse: the policy roster lives as two or three small groups far apart (pairwise 11 against the scripted roster's 6) with nearest-neighbour distance unchanged, and the lab shape reproduces live to the second decimal

`fog-gen1-cert/RESULTS.md` §"Dispersion" and the soak record. Groups
linked at Chebyshev ≤ 2. Scripted roster (lab, 25k ticks): all five
together 28% of ticks, modal shapes 5 / 4+1 / 3+1+1, mean pairwise
Manhattan 6.1, farthest pair 11.3. gen1-A (lab): all five together 3%,
two or more groups of ≥ 2 on 54% of ticks, modal 3+2 / 2+2+1 / 2+1+1+1,
pairwise 11.0, farthest 19.1, nearest neighbour 2.6–3.4 (scripted
2.4–2.8). Live, 48 h and 8,507 polls: 0.04 / 0.32 / 0.42 / 0.19 / 0.03
by group count, split 0.50, pairwise 10.9, farthest 19.1, nearest
3.2–3.7. Corner and edge occupancy near uniform (corner-within-3 share
0.13–0.19 against 0.16), so it is pairs and triads spreading, not
camping. Cosleep persists inside the groups (a friend on 57–93% of
sleeping polls, partners rotating).

The scripted pile is the needs-driven brain's shared errands (the same
chow, the same beam at the same time); distinct minds do not share them.
A character read, not a gate. **Scope**: five policy seats, 20×20,
radius 4, the served element density. **Invalidated by**: pairwise
distance within 1.0 of the scripted 6.1, or a single pile over 15% of
ticks, on the same map. **Re-verify when**: Gen 2 seating, and any
change that anchors piles (the beam package #390, a cuddle drip).

**Gen 2 read (2026-10-22)**: the re-verify fired (Gen 2 seating). A different instrument (prereg §9.5 as declared in the battery DECLARATION §9.5: together-share per seat under walk adjacency, Manhattan ≤ 1, and mean group count), so no pairwise number; the certified roster rot2 sits within 0.0141 of its own networks' uniform seatings at 20×20 and 40×40, and at 100×100 is together less than the scripted teacher on every seat (−0.045 to −0.087) with +0.37 more groups per tick (`gen2-cert-battery-2026-10-20/RESULTS.md` §"§9.5, the dispersion read at all three sizes"). The dispersing character holds for the Gen 2 lineage on the big map; this entry's pairwise bar is unread.

## F-046 · active · A priced target feature the corpus never conditioned on stays unused: under the spec 054 ramp the minds groom clean friends (74 of 76 live grooms on bath < 10, none in the paid bin), and the scripted groom refusal tax leaves with the scripted seats

FR-014 (spec 054) read in `fog-gen1-cert/RESULTS.md` and confirmed in
the soak record. Lab (gen1-A trace, 125k decisions): grooms of a friend
by the target's bath, per 1k visible friend-rows, 2.24 at bath < 10,
0.64 at 10–20, 1.48 at 20–35 (n = 3), none above; 280 of 304 grooms on
friends under 10. Live (48 h poll, disc-rule visibility): 74 / 2 / 0 /
0 / 0 grooms across 46,179 / 8,730 / 970 / 42 / 13 visible friend-rows,
1.6 / 0.23 / 0 / 0 / 0 per 1k. The dirtiest cat (Biscuit, mean bath
9.5) is the most groomed (49 of 76) and never grooms, which is her
character, not the ramp. Groomed share of dirty-visible spells 0.027–
0.052 on the candidates against the scripted anchor's 0.226; the
scripted seats' refusal tax in grooming (F-039) is 0–8 rows a seat
after the reseat.

The clones learned grooming as affinity (who is beside me and settled),
because that is what the pre-054 corpus contained; the ramp reprices a
feature no policy ever read, and doctrine rule 9 says a frozen model
cannot answer it. **Scope**: Gen 1 clones trained before spec 054 on
the c30 corpus; the ramp min(2.0, 0.25 + 3.5x). **Invalidated by**: a
Gen 2 clone trained on a 054-priced corpus whose grooms concentrate in
the ≥ 20 bins at or above the scripted rate. **Re-verify when**: the
Gen 2 teacher is re-recorded under 054 (rule 9), and at the next groom
reprice.

## F-047 · active · A relief differential worth one tick per nap does not move sleep placement: sleeping cats lie on a beam 2.8× as often as cats in general but the adjacent ring is at chance (0.93×), price 7 / 10 / 15 never left the seed spread, and only the leash held the beam share

`fog-gen1-cert/RESULTS.md` §"3. Beam naps" and
`results-raw/live/beam_adjacency.py` (recorded (local): untracked, evidence-archive ruling 2026-09-27) on the gen1-A trace
(`beam-adjacency-gen1A.json`, uncommitted): 16,299 sleeping cat-ticks, a
beam visible in 41% of them. Chebyshev distance to the nearest visible
beam, 0 / 1 / 2 / 3 / 4 tiles: 12.7 / 19.2 / 28.4 / 32.9 / 6.8% of
sleeping rows, against 4.6 / 20.7 / 31.6 / 35.9 / 7.2% over every row
with a beam visible (ratio 2.76 / 0.93 / 0.90 / 0.92 / 0.94; against
the geometric disc prior, 6.4 / 1.18 / 0.87 / 0.81 / 0.83). Of 3,255
sleep starts, 259 begin one tile from a visible beam and the beam is
occupied for 64 of them (25%): one tile, one cat, so the friend on the
beam makes the cosleeper's adjacent tile structural. In-beam share of
sleeping ticks: candidate pool 0.014–0.052 across seven seeds, beam
price 10 → 0.068 / 0.033, price 15 → 0.031, the tight leash (dose-hi)
0.21, the scripted teacher 0.26–0.29; live pooled 0.041.

The arithmetic: a need-40 nap is 8 ticks in the open and 6 on the beam
at relief 5 / 7, the step costs one, so stepping in nets one tick, and
the gradient does not find one tick. The cats on beams are the ones who
lay down there. **Scope**: sleep relief 5.0 off-beam, beam 7 / 10 / 15,
beam ttl 300, radius 4, Gen 1 lineage. **Invalidated by**: the in-beam
share clearing 0.10 without a leash at a price ≤ 15, or the adjacent
ring above 1.25× its prior. **Re-verify when**: the beam package (#390:
off-beam relief to 3, long-lived beams) is adopted; predicted in-beam
share then rises toward the scripted 0.26–0.29 at leash ≤ 0.04.
Note (2026-09-18): warmth conducts (spec 031, `action.rs` sleep rate),
so a mutual cosleeper beside a partner on the beam is paid the beam rate
already; of the 25% occupied-adjacent starts, only the non-mutual ones
lose the differential. Owner ruled (a) and (b) of #390 the same day.

## F-048 · active · The free register (mew, chirp, purr) is inert for a visible listener and an unseen listener does less after it (row-vs-word attribution OPEN — 2026-09-27 review caveat below; retitled from "which is the heard row, not the word"); the want words move listeners on the same instrument

`free-register-baseline-2026-09-17/RESULTS.md` (PREREG 251c67f, amended
28e2bce; gen1-A trace, 125k decisions, message head recomputed by
`add_msg.py`; read `free_register_read.py --control speaker
--match-speaker`, window 10). Emission per 1k decisions: purr 72.8, mew
36.8, chirp 31.7 (want_cuddle 4.7), spoken from rest or sleep 86 / 63 /
65% (corrected 2026-09-27 with the baseline doc). Uptake, ratio to a
matched control (the speaker's same-word speech excluded, keyed on both
cats' activity class): visible listener, approach 0.88–1.07, proposal
to the speaker 0.94–1.02, echo 1.11–1.13, any speech 0.99–1.00, INERT on all
three words. Unseen listener: approach 0.78–0.85, proposal 0.53–0.73,
29 of 30 per-seed ratios under 1.0. Positive control on the same
instrument: want_cuddle from a visible caller 1.37× the proposals, from
the fog approach 1.51× and proposal 2.50×.

The unseen-listener drop's attribution is OPEN (see the review
caveat below, which retires this paragraph's original claims —
quoted: "The unseen-listener drop reads as the heard row itself (a
fresh position for an unseen cat, whose state is "asleep or
resting" for these words) rather than the word, since the control
cannot yet separate the two; the next control is a speaker who said
some other word." — the measured control pool already consists of
other-word speakers, 99.49–99.61% of unseen-class rows, so the read
largely separates word from row and the contrast points toward the
word if anywhere). The register carries no fact under visible needs (F-026); Gen 2
hides needs, which is the first condition under which it could. **Scope**:
Gen 1 clones with needs visible, cooldown-only legality, intensity 0.
**Invalidated by**: a visible-class ratio outside [0.8, 1.25] or an
unseen ratio above 1.0 on a settled word. **Re-verify when**: the Gen 2
collection (hidden needs), and if option 1 or 2 of #391 is adopted.
Trap on record: the declared `--control any` pool starves (26–97% of
events dropped) and is never read.

**Review caveat (2026-09-27, the retroactive gate on the baseline
doc, its addendum entries 10/14/15):** the "heard row, not the
word" attribution's stated support — a control whose speaker had
been silent 30+ ticks with a stale or empty row — was refuted by
measurement: the amended control excludes same-word speech only,
and 99.49–99.61% of unseen-class control rows carry a speaker who
said another word within the window (rows populated 99.19–99.34%). The measured
ratios stand (visible in-band, unseen below 1, want_cuddle
active);
the row-vs-word attribution is OPEN, and the contrast as built
points toward the word if anywhere. Gen 2's free-register read
should treat the mechanism as undetermined.

## F-049 · active · Mews and chirps are not echoed: cross-cat coincidence is 1.0–1.2× chance and only at lag 1, purr piles are cosleep, and the echo the owner sees is several cats answering one ask with here-words (1.9× at lag 1, two thirds of it explained by keying on the ask)

`free-register-baseline-2026-09-17/RESULTS.md` §Question 2 and
§Addenda (`cluster_read.py`; null A = circular shift per cat, null B =
redraw within the cat's state class; lab trace + a 45-minute live poll
of `recent_meows`, ticks 88,095–91,495, 3,798 rows). Lab, lag 1 / 3 /
10 against null A: mew 1.14 / 1.09 / 1.01, chirp 1.19 / 1.09 / 1.00,
purr 1.57 / 1.41 / 1.14; against null B (same state) mew 1.05, chirp
1.08, purr 1.30. Live: mew 0.99 / 1.07 / 1.03, chirp 1.20 / 1.00 /
0.97, purr 1.61 / 1.18 / 1.03. Here-words: here_sunbeam 1.89 at lag 1
in the lab (1.86 keyed on being in a beam, 1.31 keyed on the ask, the
declared stop point), 1.91 live within 10; here_critter 1.4–1.6×. On
the client side (Client, 2026-09-17) drawing disperses the sounds (mew
0.65×, chirp 0.57× of the served coincidence) while here-words pass the
pose gate 69–80% against 36–47% for sounds, and 54% of answered asks
draw two or more reply bubbles.

Purr's 1.3–1.6 is cats purring in the same pile at the same time; the
free words cluster only as far as shared state explains. The visible
flurry is the reply law: every cat that hears a want and sees its
referent answers on the next tick. **Scope**: Gen 1 roster, cooldown 10,
digest 30, the served reply law (answers stamped on the next tick).
**Invalidated by**: mew or chirp over 1.25× at lag 1 under null B.
**Re-verify when**: F-048's register comes alive under Gen 2, or the
engine's reply law changes (one reply per ask is a client change, #395,
and does not touch this).

## F-050 · active · Beam seeking survives β 0.04 PPO once the tile changes a nap's outcome: under shallow ground (off-beam sleep relieves only to a floor, spec 056) the package clone keeps 0.46–0.81 of its naps on beams through the fine-tune at every floor from 10 to 25, where the same clone on the same world without a floor kept 0.04–0.07

`beam-world-screen-2026-09-19/RESULTS.md` §Tier 5 (prereg
`PREREG-tier5.md`). Eight arms from tier 2's package clone (placement
0.511 before PPO), the package world plus `sleep_floor_off_beam` at 10 /
15 / 20 / 25, two seeds each, run to the plateau rule (9–11 M ticks),
read by the swap legs (the arm in its own gen1-A seat, 30 × 20k, served
clock): 0.51 / 0.46, 0.44 / 0.72, 0.69 / 0.50, 0.81 / 0.65. Tier 2's
identically trained arms on the same world at floor 0: 0.070 / 0.037.
The arms also learned cosleep beside beam sleepers (conducted share
0.11–0.26 in all-arm rosters against 0.016 at floor 0). Their probe
series held through the 2.5–4.6 M-tick stretch where tier 2's fell.

Why: a nap is a six-tick minimum that ends once the need clears, and
these minds begin naps at need 7–9, so on flat ground a beam's higher
rate has nothing to relieve and the walk to it is worth zero ticks,
which PPO correctly unlearns (F-047, tier 2). Under a floor a ground nap
leaves the need at the floor and only a beam clears it, so the tile
changes every nap's outcome and the gradient keeps the walk. The price
to a learning mind is flat across floors, about 1.5 happiness against
floor 0 (all-arm rosters 90.5–91.1 vs 92.3), while a frozen mind pays
1.4–5.2 and spends up to 40% of its ticks in naps that relieve nothing,
armed for `want_sleep` most of the time from floor 15 up. **Scope**:
the package world (six beams, lifetime 3,000, off-beam rate 3), the Gen
1 lineage clone, β 0.04, floors 10–25; nap durations 6–12 with spec
056's early end at the reachable floor. One beam density only (the count axis was read next, F-051): under a
floor, welfare depends on beam access, so the welfare numbers here do
not transfer across beam count, lifetime, reach or roster size (owner's
caveat, 2026-09-20), and floor-0 welfare priors are not comparators for
a floored world. **Invalidated by**: an arm under
a floor ≥ 10 ending under 0.15 placement in its seat, or the floor's
cost to a learning mind exceeding 3 happiness. **Re-verify when**: the
Gen 2 teacher is re-recorded under the floor (the scripted sleep rule
does not read the floor today and naps on the spot into nothing:
placement 0.46 → 0.25 from floor 0 to 25), and at any change of the nap
duration law or the announce threshold. **Revisit at the Gen 2 read**
(owner, 2026-09-20): update this entry with the Gen 2 roster's placement
and welfare under floor 15 and the beam-density read, and update the
worked example under doctrine rule 7 with it. **Promotion**: a floor is the
Gen 2 world's beam law; the owner ruled 15 on 2026-09-20 (#390: keeps
the floor clear of the announce line at 20, so a naive mind's want
channel cycles rather than saturates); the served Gen 1 world stays at
floor 0 (the frozen column).

**Dated note, 2026-10-21 (the Gen 2 read, per the 2026-09-20 revisit;
no status change):** the certified Gen 2 roster rot2 (five distinct
networks, `gen2-cert-battery-2026-10-20/RESULTS.md` §Owed reads) on the
Gen 2 world (floor 15, one beam density) keeps 0.416 / 0.533 / 0.613 of its
sleep ticks on beams at 20×20 / 40×40 / 100×100 against its scripted
teacher's 0.387 / 0.472 / 0.538 on the same worlds, and conducts
(cosleep beside a beam sleeper) 0.138 / 0.109 / 0.084 against 0.055 /
0.054 / 0.049; team happiness 87.49 / 86.23 / 83.81 against 81.92 /
81.63 / 76.62. Placement rises with world size for both rosters;
Pumpkin (0.383 / 0.484 / 0.589 vs 0.486 / 0.548 / 0.668) and Clementine
(0.404 / 0.496 / 0.513 vs 0.417 / 0.513 / 0.581) sit below their teacher
at every size. One half of the revisit stays open: Gen 2 ran one beam
density (the sunbeam count scales with area, 6–7 / 24–28 / 150–175 at
20 / 40 / 100), so the density half is unmeasured. The re-verify
condition above (the teacher re-recorded under the floor) is met by
construction: spec 057 merged 2026-09-22, before the Gen 2 comparators
were recorded, so the scripted side here is the floor-reading teacher.

## F-051 · active · Under a sleep floor, beam count is a step at six for a learned mind and flat past it: five beams cost about 0.6 happiness, six to eight are one level inside the seed spread, frozen minds span 0.14 across the four counts, and a mind trained at six beams seated on five, seven or eight is never worse than one retrained there

`beam-world-screen-2026-09-19/RESULTS.md` §Tier 6 (prereg
`PREREG-tier6.md`). The floor-15 package world at count 5 / 6 / 7 / 8,
two PPO arms per count from the package clone (count 6 = F-050's
sg15 arms), 30 × 20k on the served clock. All-arm happiness by seed:
89.78 / 90.92, 90.86 / 91.13, 90.58 / 90.66, 90.81 / 91.30; own-seat
placement 0.44–0.72 at every count; the frozen gen1-A roster 89.77 →
89.90. The count-6 arms on the 5 / 7 / 8 worlds without retraining:
+0.78 / +0.13, +0.36 / +0.57, +0.21 / −0.01 happiness against the
retrained arms, placement carried with the arm (0.28–0.43 and
0.54–0.63 on every world). The teacher's placement rises with count
(0.29 → 0.44) at flat happiness; `here_sunbeam` rises with count for
everyone; the learned rosters' `want_sleep` is 8–11 per 1k from six
beams up and 15–17 at five.

Why: full sleep relief under the floor needs beam access (F-050), so
a count under what the roster can share costs the minds naps that
clear, and above it the sixth beam and up are slack; a frozen mind
naps into the floor on any tile and never reads the count. Count
changes what the policy observes (two nearest-beam slots), not what
any action is worth, so doctrine rule 9's mechanism (a reprice a
frozen model cannot answer) is absent on this knob; the prereg's
mechanical trigger (a gap past both lines) fired once at count 7, in
the transfer's favour (RESULTS §Tier 6, addendum 2026-09-23).
**Scope**: floor 15, beam lifetime 3,000, reach 8, the five-cat
gen1-A roster, the Gen 1 lineage clone, β 0.04, two seeds per count;
the ordering 6 < 7 < 8 was not found (7 under 6 on both seeds, 8 over
7 on both, all inside 0.75). Also on record: learned rosters under the
floor start 0.16–0.33 of naps with sleep need under 5, three fifths on
a beam and two fifths as ground cosleep joins, solo on the ground 0–1
times in ~2,700 starts per slot; tier 5's 0.02–0.05 was the same
measure pooled over frozen seats. One arm (cnt7-s1) under-serves drink at Biscuit's seat (a
3,015-tick streak, 9 of 30 seeds in its swap leg), a mind property
carried into the count-7 all-arm numbers. **Invalidated by**: a count
in 6–8 leaving the seed spread on both seeds, or a transferred arm
landing more than 0.5 happiness under a retrained one on any count.
**Re-verify when**: the floor, lifetime, reach or roster size changes
(the owner's density caveat, F-050), and at the Gen 2 read on the
re-recorded teacher. Owner's triggers from the spec 057 merge
(2026-09-22, PR #409, "B on both"): any floor change re-reads distress
on the scripted comparator leg, and a floor past `safeguard −
announce_threshold` needs the validator bound before it runs (the
off-beam urgency knee sits at safeguard + floor; at floor 15 that is
the distress line, measured clean). **Promotion**: the owner ruled count 6 on #390 (c)
(2026-09-21, "6 beams"): the Gen 2 world is the package world as it
stands (floor 15, lifetime 3,000, six beams); a later move to 7 or 8
needs no new screen.

## F-052 · active · Under fog the meow channel is load-bearing: hearer-side deafening of every kind costs the served roster 6.716 team happiness on 30 of 30 worlds and multiplies distress ticks 3,762×; here-words alone cost 0.455 (30 of 30), want-words are welfare-null, and F-026's global-vision redundancy does not carry into the fog generation

`fog-deafening-2026-09-23/RESULTS.md` (declaration `prereg.md`,
committed before collection at d5c6c74; the
`fog-gen1-cert/cert_harness_fog.py --deaf` mask landed at 207f8c9
with three mutate reds, and afc43ae's copy collected — its only
change the `deaf` band entry). The served gen1-A roster on `anchor-b3.toml`, served clock, 4
arms × the same 30 seeds (900101–900130) × 20,000 ticks, hearer-side
only, emission legal. Paired mean team-happiness deltas vs intact:
want-deaf −0.020 (15 of 30 worse — a null), here-deaf −0.455 (30 of
30), all-deaf −6.716 (30 of 30, range −4.948 to −11.935). Distress
ticks 125 → 299 / 3,891 / 470,286; the longest all-deaf streak runs
6,150 ticks. The all-deaf cost is unevenly carried: Clementine's seat
loses 15.1 happiness, Miso's 7.3, the other three 3.1–4.2.

Why (the fog-thesis reading; the worlds also differ, so this is
mechanism, not attribution — see the scope line): under fog a cat
outside the vision disc is knowable only by sound — heard rows carry
the caller's position, here-words carry what it found — where under
global vision no F-026 arm moved team happiness more than 0.015 (no
arm there silenced everything; both-deaf measured +0.013). Here-deaf moves the tail far more than
the mean, a 31× distress rise beside the 0.455 cost — the direction
of F-026's registered whisper, though that whisper was purr-deafening
at flat welfare and here-deaf's mean cost is real. Want-words remain
function without fitness (they move listeners, F-048, and buy no
happiness) even under fog. **Attribution (second collection, `prereg-2.md`,
2026-09-24; replaces the bound quoted in RESULTS §Addendum
2026-09-24)**: the heard-rows-only arm ran — erasing every heard row
alone costs 6.371 (30 of 30), 0.95 of the all-deaf 6.716, so what a
cat hears about unseen cats (their position and their in-fog words
together; the arm does not separate them) carries the load; free-deaf
costs 0.237 (28 of 30), an upper bound on free-word meaning (free
calls also create rows). Single-family costs (want −0.020, here
−0.455, free −0.237) sum to 0.712 against all-deaf's 6.716: strongly
non-additive. Third collection (`prereg-3.md`, the direction sweep):
the row without its exact range — bearing plus the in-fog words,
both kept by the dir arms, shares unmeasured — recovers 0.97 of the
rows-deaf loss (dir16 −0.203 against rows −6.371); exact range is
worth at most 0.203 (the clean intact-vs-dir16 contrast); the cost
is V-shaped in the fake range with its minimum at the true median
(R = 16); the bias asymmetry is in the distress tail (dir5 99 ticks
against dir28's 1,725 and dir37's 8,685, longest streak 612) while
matched-offset welfare is level (dir28 − dir5 = −0.037). **Scope**: frozen minds (hearing's value to cats that grew up
hearing), the served composition and world, one band; nothing here
attributes the change to fog alone vs the bugs-2.0 economy (F-026
SC-005). **Invalidated by**: a replication band where all-deaf lands
inside ±0.15, or a here-deaf sign flip. **Re-verify when**: any
roster or world reseating; Gen 2 (hidden needs raise the channel's
load by design — re-run before the Gen 2 cert so the gate has its
prior).

## F-053 · active · Under fog, frozen Gen 1 minds do not survive world-size displacement: intact happiness falls 92.471 → 77.935 → 52.813 at 40×40 and 100×100 (the scripted teacher reads 86.343 / 82.898 on the same worlds), distress streaks reach 15,927 ticks, and exact range on meows stays near-worthless at every size (dir gaps 0.203–0.715)

`world-size-screen-2026-09-24/RESULTS.md` (PREREG frozen 2026-09-24,
configs and per-size R in its freeze-time section; band 900201–900230,
20 legs × 30 × 20k, served clock; size20 cells from the fog-deafening
screen). Sizes 20/28/40/100 at served per-tile density plus ½× and ¼×
density at 40 and 100, elements scaled with area, radius pinned 4,
five-cat gen1-A roster displaced unretrained.

Why (the declared displacement reading): observations normalise
positions by world dimensions, so a familiar float means 2× the tiles
at 40×40 and 5× at 100×100 — the frozen minds mis-read every distance
while the sight-and-memory-gated teacher keeps working; the worlds are
livable, the displacement is what fails. The channel's absolute load
peaks at 40×40 (intact-vs-rows 37.025) and compresses at 100×100
(21.205) because the intact baseline itself collapses; density cuts
hurt both rosters monotonically, the teacher more than size hurts it
(74.508 at 40×40 ¼-density) and the roster less than size hurts it.
**Scope**: frozen minds displaced at read time (doctrine rule 9: a
generation trained at size is the unanswered branch), r = 4, five
cats, one band per cell, element density scaled with area.
**Invalidated by**: a replication band where size40 intact lands
within 2 happiness of size28 intact. **Re-verify when**: the radius
pin, roster size or element scaling rule changes; any generation
trained at a larger size (the rule-9 answer supersedes this entry's
displacement half). **Harm rule** (PREREG, fired; the named
set is every cell whose longest distress streak exceeds 1,000 ticks):
no further legs on size28, size40 at any density, size100 at any
density, or the rows arm on the served world, before the owner's
word — the full cell list with streaks is RESULTS §"The harm rule,
fired" (the longest streaks: size40/rows 19,872; size100/rows and
size100-d4 intact 19,776 each). **Promotion**: feeds the Gen 2 sitting
(#389) as the shelf's world-size input; no number here picks a world.

**Gen 2 read (2026-10-22)**: this entry's re-verify fired (the radius pin moved under the vision law); the same displacement branch, on a new lineage. The Gen 2 trunk, trained at the served 20×20 only and frozen at read time, beats its scripted teacher at 40×40 and 100×100 under the vision law (F-060), and the radius cell (F-062) shows the law's wider radius moving the scripted teacher, not the frozen roster. The trained-at-size branch this entry names as unanswered stays unanswered; and the two records are not the same cell (this entry at radius 4, the Gen 2 legs at 5 and 6).

## F-054 · active · Objective-side pressure substitutes for the world floor: on floor 0 all three counterfactual-floor reward shapes restore beam placement (hard 0.920/0.937, convex 0.768/0.767, priced 0.516/0.496 against the 0.033–0.062 null), the shapes trade placement for welfare along an ordered frontier (happiness orders the reverse), every shaped arm pays 0.75–1.98 happiness against unshaped gen1-A, and the learned price settles interior at λ ≈ 0.12

`reward-shape-screen-2026-09-24/RESULTS.md` (PREREG frozen 2026-09-24
+ deviations; owner: "Freezes approved"). Six PPO arms from the
package clone on `package.toml` (floor 0), β 0.04, plateau stops at
8–9M ticks; per arm the five swap legs + all-arm, 30 × 20k, eval
band, against the recorded gen1-A and pkg-arm comparators on the same
world and seeds. The shapes read the counterfactual state (asleep,
off-beam, sleep need < 15) from each cat's own observation at
magnitude-matched coefficients (c1 0.6, c2 1.0, d 0.06; probe-based
pins).

Why: the world floor worked by making the tile change a nap's outcome
(F-050); these shapes make the objective price the state the floor
world forbids, and the gradient finds beams either way. The frontier
ordering (hard > convex > priced on placement, reversed on happiness)
is a property of form for the magnitude-matched pair — hard and
convex shared expected magnitude at baseline, and the realized
per-tick terms order the other way — while the priced arm's lower
placement rides a genuinely lower marginal price (λ ≈ 0.12 against
c1 = 0.6). The discontinuity is not required to clear the bar
(convex reaches 0.77), though reproducing the fine's full placement
did need the fine (P2's failed clause). The arms buy placement
partly by sleeping less (sleep share 0.086–0.114 against gen1-A's
0.135, least suppressed under the price). The priced arm hit the
declared occupancy target (final-update 0.054–0.057, last-quarter
mean 0.060, against d = 0.06, from the 0.126 baseline) at the least
cost with a stable interior λ (0.117–0.119, stability 8–10% against
the 20% line): a readable exchange rate: a tick with the whole
roster in the counterfactual state costs about 0.12 team reward
(about 0.024 per cat-tick). **Scope**: lab
training variants only — rules 1 and 2 stand for shipped policy;
one world, one init, two seeds per shape; the shaped arms' happiness
deficit is against a baseline optimizing pure welfare on an easy
world. **Invalidated by**: a replication seed pair where any shape's
placement lands under 0.15, or a priced arm whose λ diverges or
pins the clamp. **Re-verify when**: any shape is considered for the
Gen 3 free-time objective (the amendment path, the owner's ruling);
the Gen 2 encoding change lands (retrain, new schema). **Promotion**:
feeds the Gen 3 free-time design as its reward machinery candidate
(the shelf's two-channel entry); the rule-1 structural question is
the owner's fork, RESULTS §Decision rules.

**Review caveat (2026-09-26, Professor memo
`2026-09-26-free-time-arc.md`, adopted by the owner):** the priced
arm ran at λ ≈ 0.12 against the hard fine's 0.6 — one fifth the
pressure — so the cost-channel-cheapest recommendation is
confounded with dose until an equal-pressure arm runs; the
hard-vs-convex form claim (the pressure-matched pair) stands. The
0.75–1.98 cost was measured on floor 0, where beam-seeking has no
welfare function; the cross-world reads
(`cross-world-cost-reads-2026-09-26/`) put it on one footing with
the world-side cost.

## F-055 · active · An impact-only gate failed with a persistent bonus stock: the enrichment glow saturated into a level shift (play share 0.0775/0.0885 vs 0.0749 baseline against a 0.10 bar), play starts shifted into the closed-gate region (0.1172–0.1801 vs 0.0843, consistent with banking glow through the need gate), and the residual pressure cost 0.729–0.839 happiness (30/30) without buying the behavior

`enrichment-bonus-screen-2026-09-26/RESULTS.md` (PREREG frozen
2026-09-26 on the owner's overnight word). Four PPO arms from the
package clone on `package.toml`, the Gen 3 free-time prototype: a
positive-only bonus b = β·E·g entering each cat's happiness before
the Nash mean (exact recomposition; the gap, the ramp 15→25 from the
gen1-A p50/~p90, the glow gain 0.25 and half-life ~139 ticks, and
β 0.03/0.015 × two seeds are the PREREG pins, frozen 61d7fc8);
plateau stops; all-arm batteries 30 × 20k under
`--abort-streak 1000` against the recorded gen1-A cell (happiness)
and a fresh gen1-A leg (play baselines, which reproduced the
recorded cell's shared fields exactly).

The plausible mechanics of the P1 miss (diagnosis, not proof — no
non-saturating control ran, and bonus-s2 still lifted play 18%):
baseline-rate play alone pins the glow near its cap (last-quarter
trace E 0.917–0.921 with the gate partly open, g 0.637–0.646, the
term a roughly steady ~58% of β per tick), so marginal play buys
almost nothing — a level shift teaches little. The stock's persistence leaves the gate pricing only the
payout, never the act — a cat that plays while needy still holds the
glow when the gate reopens — and the closed-gate start shift is
consistent with exactly that banking (not proven: the data cannot
separate it from needs generally running closer to the edge). Both dose arms sit inside
the full arms' play range (0.0833/0.0858 vs 0.0775–0.0885), so β
did not bind within the tested 0.015–0.03 (two seeds per β; larger
β untested); the welfare cost tracked β (full −0.729/−0.839,
dose −0.251/−0.381) while behavior did not. The F-054 sleep dodge
splits by training seed (bonus-s2 inside the ±0.015 sleep band,
0.1282 vs 0.1354; bonus-s1 breaks it, 0.1174); low-need nap starts
fell (0.132–0.273 vs 0.284), which does not discriminate from
F-054; part of bonus-s1's cost plausibly rides the old dodge, and
the split of the remainder is unmeasured — what was measured:
distress ticks 1,124/2,286 vs
360, teammate-distressed play-start share up to 0.0021 vs 0.0003,
all screen-scale, max streak 492, zero aborts. **Scope**: lab
trainer prototype only, one world, one init, two seeds per β; the
gate form tested is impact-only with these stock dynamics — the
finding is about that combination, not about bonus channels as a
class. **Invalidated by**: an accrual-gated or non-saturating
variant failing the same way (which would indict the channel, not
the gate), or a replication where these pins do lift play past the
bar. **Re-verify when**: the Gen 3 free-time design fixes its
mechanism. **Promotion**: redesign direction into the Gen 3 inputs
(`gen3-free-time-inputs-2026-09-26.md`), as the session's
RECOMMENDATION at the owner's fork, not a declared branch: gate the
ACCRUAL (the owner's original mechanism; per cat is this session's
recommendation) and de-saturate the stock so marginal play carries
marginal value — both preceding any engine work if she takes the
branch at all; RESULTS §Decision rules.

**2026-09-29 note (F-056)**: the Invalidated-by's first arm ran —
stage B's accrual-gated and non-saturating variants also missed
the traction bar, with glow OFF the cap (a different signature
than the saturation measured here). Per that clause the
indictment moves to the channel; the measured failures above
stand unchanged.

## F-056 · active · β is not the enrichment channel's binding lever: 4.7× the bonus moved pooled greedy play 0.0773 → 0.0885 (monotone, all under the 0.10 bar, glow off the cap), and closed-gate starts exceeded the stage-A band on every arm INCLUDING the accrual-gated arms whose closed-gate play pays nothing — the failure indicts the channel, not the gate mechanism

Stage B of the enrichment-decay sweep
(`enrichment-decay-sweep-2026-09-26/RESULTS-B.md`, PREREG-B frozen
ddd2301): eleven arms on the d100-1000 corner — β {0.06, 0.10,
0.14} × 3 seeds under the decay throttle, plus the accrual gate at
β 0.10 × 2 seeds — read on the stage-A instrument (11 all-arm legs
× 30 × 20,000, zero aborts on 330 rows). With stage A's β 0.03 as
the fourth point, family-mean pooled greedy play is monotone and
saturating in β, all under the 0.10 bar, against a 0.0749 baseline.
Cheap to summarize along the curve: β up 4.7×, play up 14% (the per-β
points and the step gains: RESULTS-B §"Predictions, scored" P1). Glow was off the cap on every
arm (P1), so the saturating curve is not saturation of the stock —
the prereg's ruled branch fired: "the channel is dead as designed
('channel dead' branch of the ruled adjudication); report; the fork
is the owner's". Trace banking
stayed dead (P2), but the closed-gate START share exceeded the 0.1043
stage-A band on every arm (0.1087–0.2540 vs comparator 0.0843) —
including both accrual-gated arms, where a closed-gate start earns
structurally nothing, so per PREREG-B's adjudicator the CORNER,
not the mechanism, is at fault for P2. Stage B ran both variants
F-055's Invalidated-by clause names, and both missed the traction
bar, though not with F-055's signature (its glow was saturated;
stage B's is off the cap): the clause's channel-indicting arm fires,
F-055's measured facts stand, and F-055 carries a dated note rather
than a status change (RESULTS-B §Decision rules). Welfare priced the
curve non-monotonically — family paired deltas b06 −0.806 (breaching
its −0.50 bar), b10 −0.464, b14 −0.605 — with the under-tending sign
everywhere (every arm's eat+drink below the comparator's 0.0499) and
the teammate-distressed watch line (0.001) exceeded on four arms
(§"The read", P3, P4).
**Scope**: lab trainer only, one world, the
d100-1000 corner with 15→25 brackets fixed (the stage-C bracket
sweep is unrun — its premise needed a β winner and there is none),
one init family, 2–3 seeds per family. **Invalidated by**: a
bracket/gain configuration, or a world change, at which this
β range clears the 0.10 bar. **Re-verify when**: the Gen 3
free-time design's leading refinement lands — dedicated recreation
actions (frolic/snuggle), recorded in the inputs doc as "leading
direction pending her confirmation" (what she HAS ruled there:
play and cuddle as free-time activities with the door open to
more, and scripted demonstration of the new actions).
**Promotion**: closes the β lever in the Gen 3
free-time inputs (`gen3-free-time-inputs-2026-09-26.md`); the fork
past channel-dead is the owner's (RESULTS-B §Decision rules).
## F-057 · active · The imitation leash sets the COMPOSITION of play, not its level: dropping it 0.04 → 0.01 released the four corpus-non-players (ex-Biscuit lift +0.0479/+0.0893, the arc's first non-Biscuit movement) while Biscuit gave play back and closed-gate starts fell to a third-to-half of baseline — with the total still under the 0.10 bar; making the stock visible moved nothing, so F-056's channel-dead verdict survives both releases at the total level (the nearest-branch reading: the declared "flat" condition missed downward on two arms)

The dead-or-held probe
(`enrichment-decay-sweep-2026-09-26/RESULTS-C.md`, PREREG-C frozen
d5bf7fca; the Professor review's recommended test): two arms at β
0.14 with the KL leash dropped 0.04 → 0.01 (l14 × 2 seeds), two
with the enrichment stock written into the obs clock slot at leash
0.04 (o14 × 2), read on the stage-B instrument (l14) and the
declared E-fed runner (o14). Totals stayed under the 0.10 bar on
every arm (greedy 0.0722–0.0915) and under b14's 0.0885 mean on 3
of 4 — so the channel cannot raise play even with its suspected
jailers removed one at a time, and F-056 stands at the total
level (the nearest-branch reading — the declared "flat" condition
missed downward on two arms). What the leash
release DID do: the four seats whose corpus is nearly play-free
moved for the first time anywhere in the arc (ex-Biscuit summed
lift +0.0479 and +0.0893 vs stage B's per-seed extremes −0.0315 to
+0.0160) while Biscuit's own lift went negative (−0.0612, −0.0300),
and the closed-gate start share fell to 0.0305–0.0424 — a third to
a half of the 0.0843 baseline, a fifth of b14's family mean — with
96–97% of play starts below worst-need 25: the policy, unleashed,
starts play almost exclusively with the gate open. Welfare split:
the l14 arms posted the enrichment arc's first positive paired
happiness deltas (+0.224, +0.441 — F-019's buy-the-mean direction,
Biscuit's play fingerprint eroding as F-019's trade predicts) with
a widened distress tail (3,262 dist ticks, a 952-tick streak,
tm-dist 0.0039 — the probe's worst arm; F-019 measured no tails);
the o14 arms moved the other way on the mean (−0.248, −0.887) and
carried the probe's one ABORT (seed 870011, episode cut at tick
1,224 — the welfare mechanism's second firing in anger).
**Scope**: lab trainer, one world, the d100-1000 corner, β 0.14,
one leash value below standard, 2 seeds per arm; the E-visibility
arm carries a declared confound (E rode the clock slot, so the
cycling clock vanished in the same move — moot for its null under
the attribution rule, though an E-helps / clock-removal-hurts
cancellation cannot be excluded from a null, and a clock-zero
control is owed before any future positive o14-style result is
attributed). **Invalidated by**: a leash schedule or
value at which the total clears 0.10 (that would make the leash
the level constraint after all), or a seat-level release that
fails to reproduce at other seeds/corners. **Re-verify when**: Gen
3 sets its leash dose — the composition effect and the tail cost
are both direct inputs to that choice, with the abort line as the
declared police. **Promotion**: Gen 3 inputs — the free-time SHAPE
(open-gate play, all seats) is purchasable by leash dose; the
free-time LEVEL is not purchasable by this channel at any tested
β or leash, and not by visibility as tested (a confounded null;
the clock-zero control is the owed discriminator) (RESULTS-C
§Decision rules; the fork is the owner's).

## F-058 · active · The aggregate-reward route is closed in its STRONG form: with the leash released to 0.01 AND the stock in the observation together, play's level still does not move (0.0744/0.0800 vs the 0.10 bar) and the policy learns no E-conditioned play beyond the confound floor (excess banded contrast −0.0126..+0.0020 vs the +0.02804 margin, 0 of 8 cells) — while posting the arc's largest positive paired welfare deltas (+0.714/+0.809) with a COLLAPSED tail (559 and 9 dist ticks vs l14's 3,262/1,238)

The joint release arm
(`enrichment-decay-sweep-2026-09-26/RESULTS-D.md`, PREREG-D frozen
3d274e70; the Professor's joint-arm spec as upgraded by their
validation critique): j14 × 2 seeds at β 0.14, leash 0.01, E
appended as obs column 408 (additive e_col policy — bit-identical
to stock at zero, validated pre-freeze; the clock kept, so the o14
confound does not arise), split clip declared, the recorded l14
runs serving as the bitwise-validated control. Primary was the
banded test the critique demanded: live high-E-minus-low-E play
contrast per seat MINUS the control's same contrast (the confound
floor — E tracks recent play at 0.085–0.094 per non-Biscuit seat
even when the policy cannot see it), against a margin frozen from
the control's between-seed spread. Result: the live contrasts sit
AT the floor (seven of eight non-Biscuit cells negative), e_col
trained to 0.09 with the main clip firing 100% of steps (full-rate
E gradient all run — the generous-to-discovery semantics), and the
totals stayed under the 0.10 bar and b14's 0.0885 mean, within
l14's 0.0722–0.0867 range. l14's composition shift
reproduced under E-visibility (ex-Biscuit +0.0727/+0.0765, Biscuit
−0.0751/−0.0508, closed-gate 0.0230–0.0379): the leash, not
observability, sets who plays. Welfare: largest positive paired
deltas of the arc's battery reads (+0.714/+0.809; both seeds
improve all 30 pairs) with the tail COLLAPSED rather than widened
(l14's buy-the-mean-pay-in-tail trade did not recur: max streak
162 vs 952, tm-dist inside the watch both arms, no abort). Two
tending watches crossed in the MORE-tending direction (s1
eat+drink 0.07004 vs ≤0.0699; s2 bin0 0.224 vs ≤0.211) — stage B's
under-tending dodge inverted. **Scope**: lab trainer, one world,
the d100-1000 corner, β 0.14, leash 0.01, 2 seeds; the null stands
on the recorded-l14 control per the declared asymmetry (the
joint-clip replication rider is owed only on a positive and is not
owed). **Invalidated by**: any setting of this channel at which
the banded excess clears its control-derived margin, or the total
clears 0.10. **Re-verify when**: Gen 3 designs its enrichment
need — whether E-VISIBILITY is what tamed the tail (two seeds, no
E-blind twin at these exact settings beyond l14) is the open
welfare question this arm raises and cannot answer. **Promotion**:
paper 1's negative-control paragraph (the route tested with both
constraints lifted at once); Gen 3 proceeds on recreation-actions
exactly as PREREG-C's consequence set, with the tail-collapse
observation flagged as the open welfare question for that design
(RESULTS-D §The negative control, closed; PREREG-D §Decision
rules; the fork is the owner's).

**Dated note, 2026-10-04 (RESULTS-L, gated PASS r2 — facts stand,
no status change made):** the PREREG-L lesion probe evaluated the
trained j14 policies with e_col zeroed (the E-invisible form of
the same weights). Blinded, pooled greedy play rose to
0.1273/0.1270 — past the 0.10 bar no trained arm reached (arc
maximum 0.0955, b14-s2) — while the tail STAYED at the collapsed
scale (282/92 dist ticks, zero aborts) and the paired mean gave
back most of its gain (−0.830/−0.727 on lesion; s1 to −0.116, s2
to +0.082). With F-058's own banded excess small-negative on 7 of
8 cells, the coherent reading is E-conditioned SUPPRESSION: the
policy learned satiation (hold play down when E is high; eval E
median 0.685/0.735), expressed as a level effect under the F-058
margin. F-058's claims about the TRAINED condition are untouched.
RULED by the owner 2026-10-04 ("A) confirmed", on the Professor's
concurring second opinion): DOES NOT INVALIDATE — the clause's
triggers quantify over trained arms at declared settings; an
off-training-condition ablation is a probe of the weights, not a
setting of the channel. Conditions executed with the ruling: the
scope line below; F-059 minted (the suppression/capacity finding,
three evidence legs); the paper-1 wording rule (the negative
control is against ELEVATED play under the aggregate route — "the
channel had no behavioral effect" is false and must not be
implied; the suppression result is the companion sentence);
doctrine line added (invalidation clauses state their
quantification domain — experiments/DESIGN-DOCTRINE.md).
**SCOPE LINE (mandatory, per the ruling):** F-058's "level not
purchasable" holds for the trained channel AS EXPRESSED — the
lesion probe (RESULTS-L) shows above-bar play capacity
(0.1273/0.1270) exists in the trained weights behind E-conditioned
suppression; see F-059.

## F-059 · active · Training on the E-channel taught E-conditioned SUPPRESSION, not inability: above-bar play capacity (0.1273/0.1270 blinded, vs 0.0955 arc trained max) sits in the j14 weights behind satiation conditioning — the policy holds the stock high (no overlap on eval E mean/p25 vs the blind twin at matched play) and holds play DOWN, relative to the blind twin, while E is high

Minted on the owner's ruling (2026-10-04, with the F-058
no-invalidation call; the Professor's second opinion specified the
three-leg evidence form). The claim stands on three independent
legs, each gated:
1. **The banded signature** (RESULTS-D): j14's excess banded play
   contrast ran small-NEGATIVE on 7 of 8 non-Biscuit seat-cells
   (−0.0126..+0.0020 vs the +0.02804 margin) — under the declared
   one-sided margin, which had no suppression branch; the
   maintenance signature sat in the TESTED cells, in the direction
   (sign) the one-sided reward-chasing test was not aimed at.
2. **The lesion capacity reveal** (RESULTS-L): e_col zeroed on the
   same weights, pooled greedy play rose to 0.1273/0.1270 — past
   the 0.10 bar no trained arm of the arc reached (max 0.0955,
   b14-s2) — while the tail stayed at the collapsed scale (282/92
   dist ticks, zero aborts) and the paired mean gave back most of
   its gain (−0.830/−0.727).
3. **The occupancy hold** (RESULTS-L addendum, the owner's read):
   at matched play totals (sighted 0.0744/0.0800 inside blind's
   0.0722–0.0867), sighted training holds the stock higher with NO
   overlap on eval E mean/p25 across conditions (worst sighted
   0.631/0.413 vs best blind 0.616/0.368), drains below the low
   edge less often (22–27% vs 31–36%), and does not peg the cap
   (at-cap 0.129–0.167 both conditions) — holding the stock
   higher rather than playing more.
Welfare reading attached to the mechanism: live E is load-bearing
for the MEAN (deltas fell −0.830/−0.727 when blinded) while tail
protection is in-weights — a sighted-trained policy is never
deployed blind; the lesion is a probe, not a configuration.
**Scope**: the j14 arms only (β 0.14, leash 0.01, d100-1000,
2 seeds per condition — below the ≥3-seed bar the owner confirmed
for paper-cited cells, 2026-10-04 Gen 3 input set; Gen 3's twin
legs are the confirmation sample). **Invalidated by** (domain:
trained arms at declared settings, INCLUDING eval-time ablations
of their weights — the wider form doctrine rule 11 names): a
sighted-trained arm whose lesioned eval
does NOT exceed its intact play, or a blind-trained arm matching
the sighted condition's E-occupancy profile at matched play.
**Re-verify when**: Gen 3's twin legs run (eval lesions declared
on both legs). **Promotion**: Gen 3 design inputs — two-sided
banded margins with a declared suppression branch; E-occupancy
(mean, p25, floor-drain share) as a declared secondary; the
paper-1 companion sentence to the F-058 negative control.

## F-060 · active · Gen 2's hidden-needs trunk transfers across size where frozen Gen 1 minds collapsed: a five-network roster of β 0.04 PPO seeds trained on the served 20×20 beats its scripted teacher in 30 of 30 worlds at 20, 40 and 100 (+5.566 / +4.594 / +7.187, worst streak 267 / 128 / 859, no F-053 stop); five copies of one network (s2) locked roster-wide once at 20×20 and five copies of another (s4) aborted 11 of 30 worlds at 100×100

Minted at the Gen 2 step-8 close (owner 2026-10-21 "Recommendation
accepted", the post-cert plan's FINDINGS item). Evidence:
`gen2-cert-battery-2026-10-20/RESULTS.md` §Phase C (the certificate),
§Gate read (the uniform seatings), §"s2 stop investigation";
`gen2-prereg-2026-10-17.md` §7 (gates pinned at the freeze, 18f06f84).
The roster rot2 (Miso s2, Biscuit s4, Pumpkin s6, Kittybear s7,
Clementine s1): team happiness 87.487 / 86.229 / 83.810 at 20 / 40 /
100 against the scripted teacher's 81.921 / 81.634 / 76.623 on the
same 30 worlds per size (band g2cmp, paired by seed), every world
positive, no abort, worst distress streak 267 / 128 / 859 against
the teacher's 401 / 626 / 716. Where frozen Gen 1 minds read 77.935
and 52.813 at 40×40 and 100×100 (F-053, radius 4), the Gen 2 trunk
under the vision law (radius 5 and 6 there) gains over the teacher
MORE at 100×100 than at the gated sizes. Composition matters: the
company effect against each network's own uniform seating is +0.067
at 20×20 and +0.025 at 40×40, and the uniform seatings carry the
tail — five copies of trunk-s2 locked roster-wide once at 20×20
(seed 905008: a five-cat co-sleep pile, every seat's distress onset
within 60 ticks, F-027's twin lock at roster scale) and five copies
of trunk-s4 aborted 11 of 30 worlds at 100×100 (8 of the 11 single-seat;
§"100×100 stops, row-level read"), while rot2 had no stop anywhere. **Scope**: the Gen 2 lineage (β 0.04 PPO from the
trunk clone on the g2leg-20 world, schema 6 observations with the
identity input), frozen at read time and displaced to 40×40 and
100×100 under the vision law with element density scaled by area;
100×100 is characterise-only by the prereg; greedy masked argmax
(sampled selection untested, as in F-027). **Invalidated by**: a
replication band of the same roster failing the paired gate at
either gated size, or an F-053 abort of the five-network roster at a
gated size. **Re-verify when**: the roster, binding or vision law
changes; the rot2 export goes live (the live prior per F-042); any
Gen 3 trunk. **Promotion**: the Gen 2 certificate; the five-distinct-
networks rule (F-044) kept as the deployment shape.

## F-061 · active · The Gen 1 → Gen 2 play rise (0.074..0.147 → 0.363) is teacher and training, not world: the world moves it −0.004, one teacher on every seat +0.091 ± 0.007, training +0.166 ± 0.011; the networks play within 0.012 of the teacher with its comfort rule loosened and consent off, in slack time (less onset pressure than the teacher), out of idle moving and rest

Minted at the step-8 close (owner's own list, "where play increase
comes from"). Evidence: `play-decomposition-g2-2026-10-21/RESULTS.md`
(gate PASS; five scripted cells, five worlds each, paired by world
where the world is shared). The ladder, pooled over five cats:
Gen 1 behaviors on the Gen 2 world 0.106 (the world −0.004 from
0.109, unpaired); the Gen 2 teacher on every seat 0.196 (+0.091 ±
0.007: the luxury rung and partner responses reach the four
`needs_driven` seats, +0.10–0.17 each, and Biscuit loses 0.10); the
certified roster 0.363 (+0.166 ± 0.011 over its own teacher). The
roster lands 0.012 ± 0.004 short of the same teacher at
`playful_comfort` 55 with consent off (0.375 ± 0.007); the teacher is
held by its own comfort rule plus the engine's consent line, the
networks by the consent line alone. About 0.7 of the extra play is
element and solo play and 0.3 kitty play; it came out of idle moving
(−0.10 to −0.12) and rest (−0.04 to −0.07), not out of eating, drinking
or sleeping (groom moved both ways). The
networks start play under LESS other-need pressure than the teacher
(another need past 30 on 1.5–5.3% of starts against 2.9–14%), so
deviations entry 3's reward-side hypothesis gains no footing at the
served size. Play's own need carries 14–22% of the roster's +5.1 to
+5.8 happiness over the teacher. **Scope**: the served 20×20 world,
Gen 2 dials (comfort 30, consent 30), the certified roster and the
`Teacher::GEN2` presets; n = 5 worlds per cell; the Gen 1 reference
is a flag-only range. **Invalidated by**: a same-design decomposition
on a replication band where the world step exceeds its paired SD or
the training step falls inside it. **Re-verify when**: either play
dial moves (a Gen 3 boundary decision, doctrine rule 9), the teacher
presets change, or a mini-friend roster is read. **Promotion**: the Gen 3
play-economy design input (deviations entry 3's banked question:
play is the one need whose distress carries no value penalty; the
networks' extra play is slack-time play under the present reward).

## F-062 · active · The vision law's wider radius buys the scripted teacher, not the trained roster: at 40×40 one radius step (5 → 4) costs the teacher 1.294 ± 0.958 happiness and the frozen roster 0.088 ± 0.122, so the trained-vs-scripted gap's fall between the cert legs (+5.566 → +4.594) travelled with the radius on the teacher's side (gap at 40×40, radius 4: +5.800 ± 0.860)

Minted from the prereg's declared future read (§8 item 5, "if the
trained-vs-scripted gap moves with size across cert legs, one
displaced-size radius cell runs"; owner 2026-10-21 "Call 1: run
it"). Evidence: `radius-cell-g2-2026-10-21/RESULTS.md` (gate PASS):
a 2 × 2 at 40×40 on the same 30 worlds, {scripted, rot2} × {radius 5,
radius 4}, the radius-5 cells the recorded law rows. Team happiness
81.634 / 86.229 at radius 5 and 80.341 / 86.140 at radius 4 (scripted
/ rot2); the gap difference +1.206 ± 0.941 (SE 0.172, 28 of 30 worlds
positive); every seat's gap widens (+0.850 to +1.396); the roster's
between-world SD is 5–10× smaller than the teacher's in both cells.
The scripted radius effect is the comparator arc's law-vs-v4 +1.294
with the sign turned, reproduced on the vocabulary-armed config
(byte-equal rows). **Scope**: one radius step at one displaced size,
the frozen certified roster (doctrine rule 9: what a roster trained
at radius 4 would do is the S§6 arm's question, declared at the
served 20×20); welfare clean in every cell. **Invalidated by**: a
replication of the cell where the rot2 radius effect exceeds the
scripted one, or a gap at radius 4 inside the law gap's paired SD.
**Re-verify when**: the vision law or the scripted vision rule
changes; any roster trained at a non-served radius or size; the
100×100 radius step if it is ever run. **Promotion**: a Gen 3 design
input — cross-size comparisons under the law carry a teacher-side
radius term, so a size effect on the gap must be read against a
radius-held cell before it is called a size effect.

## F-063 · active · A learned distress habit is a per-network trait: trunk-s7 parks at water and keeps choosing Drink while sated on 73% of its distress ticks (234 of 322 across the rotation's streams; the two other networks with distress there, s1 and s2, on none; the teacher 8 of 3,917), every one of the six s7 runs read is that shape (one under a window caveat), and company shortens it (worst 128 in mixed company at 40×40 vs 641 among copies there); the other network's long tails are a hold, pacing and a parked mix, relief beyond sight or adjacency

Minted at the step-8 close from two investigations the owner asked
for ("Can you investigate the S7 streak cause?", 2026-10-21; "Run
the tail reads", 2026-10-22). Evidence:
`gen2-cert-battery-2026-10-20/RESULTS.md` §"s7 streak investigation"
and §"s4/s7 tail reads" (the tail reads gated; the investigation
fence-checked at its commit). The shape: a cat effectively
alone sits at water and keeps choosing Drink while not thirsty while
its distressed need (cuddle or eat) goes untended; in the two eat
cases read in detail, chow was a median 8 and 7 tiles away, in sight
on 4% and 0% of the window. Across the rotation's recorded streams (full 20,000-tick rollouts,
mixed company), drinking while sated (thirst under 10) during
distress filled 234 of s7's 322 distress ticks and no tick for s1 or
s2 (55 and 40 distress ticks there; s4 and s6 had no distress tick
in those streams, so they carry no evidence either way); the
scripted teacher did it on 8 of 3,917 (a
comparison added after the first four cases were read). Six of six
s7 runs read (three rotation runs of 84–121 ticks, the 622, 641 and
323 among copies at 40×40) are this shape, both sizes, eat and cuddle;
the 641's window is a run of 100 or more of that cat in that world,
not necessarily the 641 itself (the tail reads' caveat). In the
early-stopped tail windows s4 seats also drank sated on 47 and 22 of
100 ticks, inside cuddle runs that were otherwise pacing or mixed. It concentrates on
the fast-need seats without being confined to them (of s7's 33 Phase
B streaks of 100 or more, 15 at Pumpkin and 9 at Clementine). Company
shortens it: s7's worst run in mixed company is 128 at 40×40 (the
certified roster's Kittybear seat) and 121 at 20×20, against 641 and
226 among copies at the same sizes.
The other network's long tails (trunk-s4, four worlds) are not that
habit: a group HOLD at 20×20 (two cats held inside a group of three
or more) with water out of sight, two
cuddle tails pacing alone at 40×40, one parked mix. **Scope**: the
Gen 2 lineage's six trained networks, greedy masked argmax, the
served and 40×40 worlds; "distress" is the engine flag (need past
90); the tail reads are 100-tick windows under a per-seat early stop.
**Invalidated by** (domain: full-rollout recorded streams of the
seating analysis, mixed company at the served size, never
early-stopped windows, pooled over the rotation's 25 cat-worlds with at
least 200 distress ticks for the network in question): s7's
sated-drinking share of its distress ticks falling under 25%, or
another network of the lineage showing the habit on more than 10% of
its distress ticks.
**Re-verify when**: rot2 goes live (the Kittybear seat holds s7; the
100×100 characterize leg's 15 parked runs were all that seat's); any
retrain of s7; the served stuck detector (spec 061) is extended to a
parked shape. **Promotion**: a Gen 3 design input — the holding
account cannot see a lone parked cat, so a tail read needs a parked
(still, sated-tending) shape beside the hold; and F-043's roster-
property reading gains a mechanism: the tail travels with the seat
that holds s7.

---

## F-064 · active · A capped belief head reading only what a Gen 2 cat sees estimates a friend's hidden needs (7,807 parameters, 9.2% of the trunk): RMS error about 5.3 need points in sight in common states and about 25 in grave states, where the trivial baselines read about 53; trained at natural frequency it carries the ostrich signature on three of four covered friends (pooled grave-state bias −3.8 points against a common-state bias within 0.9 of zero), distress reweighting removes the pooled optimism (+1.7) for 7.5 points² of common-state error and is pooled worse on grave loss (NF/DR 0.944), and the declared dissolution test fails on one friend (NF's grave loss on Miso exceeds 1.10 × DR's by more than the between-seed SD; Biscuit's is 35% lower under NF), so the NF/DR tension is friend-specific and narrow, and no single head is free

Minted from mini-friend Phase 1 (`minifriend-phase1-2026-10-22/RESULTS.md`,
the re-read of 2026-10-23, gated; declaration ruled as declared, owner
2026-10-22 "Fix the stale draft and go as declared"; prereg §8 item 3,
RULED S§3a; deviations entry 10 records the retrain with bath
downweighted). The head: Linear(167 → 24) + ReLU, GRU(24), Linear(24 →
7), reading the observer's self block and the friend's permanent row
from the observer's own frozen start-of-tick observation, nothing from
the global state; targets the friend's five hidden needs (with
happiness and, downweighted, bath as reported outputs) at the tick
the view was built from. Data: the certified roster rot2, 10 lived
worlds plus 25 wide-start and 25 grave-start worlds (spec 065
`[initial_needs]`, run on an arc binding that reproduces the certified
engine on the served config); 2,800,000 evaluation samples on 19
worlds split by world. Pooled mind-visible MSE on the five hidden
needs: COMMON 28.25 ± 0.93 (NF) / 35.78 ± 2.21 (DR); GRAVE 644.04 ±
30.61 / 682.11 ± 19.77; the marginal and persistence-proxy baselines
2,814.09 / 2,809.14 on GRAVE, and the proxy barely beats the marginal
(the friend's visible activity says almost nothing about how high her
hidden needs are). Ostrich read (prereg §9 item 2, S§3d; the 1.5×
margin shared with §8 item 4; both heads): NF grave bias −3.80 in
sight / −0.80 all states, signature on Miso, Kittybear and Clementine
in sight and pooled, not on Biscuit (+0.59); DR +1.71 / +5.64 pooled,
a small signature on Miso and Kittybear in sight (−3.21, −2.01) and
on Pumpkin all-states (−5.72), Biscuit overshooting to +10.16 / +12.55.
Dissolution (procedure frozen in the declaration): floor 682.11, NF
644.04, ratio 0.944 ≤ 1.10 pooled; per friend Miso +96.76 over 1.10 ×
DR against an NF SD of 79.56 (exceeds), Biscuit −401.27, Kittybear
−6.36, Clementine −48.67 (within): NOT dissolved; this licenses head
choice for Phase 2 only, never welfare adequacy. **Caveats the section
carries**: Pumpkin's mind-visible GRAVE stratum is 170 < 200 after
every declared set and is INSUFFICIENT COVERAGE (no number read;
pooled mind-visible GRAVE pools the other four); the grave stratum
comes from grave STARTS rather than from friends sliding into
distress (the sliding cases in the data are W's late entries and G's
re-entries after early relief, none lived), and in the
grave-start worlds every cat starts in GRAVE together, so the
observer's own needs are a cue at the start that they would not be in
lived distress (the grave numbers are best read as an upper bound on
inference skill); the 1.5× lift is met trivially wherever the
common-state bias is near zero, so the gap in points, not the
signature flag, is the informative column; bath, the one visible
need, is fitted at weight 0.1 and reads 3.99 points² in sight in
common states for NF (the pipeline floor under a downweighted output;
DR 28.15) and 138.56 in grave states (DR 335.09). **Scope**: the
certified Gen 2 roster at the served 20×20, greedy masked argmax,
schema 6 observations; offline heads, no consumer, no feedback into
any policy; three seeds per head, the NF/DR pair sharing each seed.
**Invalidated by** (domain: this declaration's reads re-run on a Gen 2
roster with at least three seeds per head and the same strata and
min-n): the NF pooled mind-visible GRAVE bias at or above −1.5 points,
or either head's pooled mind-visible GRAVE MSE within 1.5× of the
marginal baseline's on the same cells (checked on this entry's own
evidence: −3.80, and 4.4× / 4.1×; neither fires). **Re-verify when**:
Phase 2's live head is read (prereg §9 item 2 reads the ostrich metric
on both estimates, the Phase 1 offline heads and the Phase 2 live
head); any change of roster or schema. **Promotion**: the Phase 2 head
choice is the owner's call with this read in hand; the per-friend
failure says a single head is not free, and any mixed or
re-capacitated head is a Phase 2 declaration, not this entry's claim.

---

## F-065 · active · With one friend grave at reset and her observers never grave, the belief head's grave estimate is about half again as hard in squared error as Phase 1's all-grave worlds showed (NF in sight: G over P 0.651 ± 0.033 at width 24; RMS 30.1 against 24.3 need points for the same heads) and the ostrich signature is broader and deeper (NF pooled grave bias −10.10 in sight at width 24, signature on four of five friends at widths 24 and 48, distress reweighting no longer removing it at −7.57); head width moves every loss cell monotonically, beyond seed noise on every NF cell and on DR's at 48 over 24, in grave and common states alike (in sight: NF 0.870 and 0.884 at 48/24, 1.210 and 1.199 at 12/24; DR 0.827 and 0.767 at 48/24), so capacity above the 8,445 cap buys 13–17% of grave loss at this geometry and, in proportion, not grave-specifically; the dissolution procedure fails at every width with the reweighted head pooled better on grave (NF/DR 1.097–1.188), the reverse of Phase 1's read on its own evaluation worlds (its grave samples mostly from the all-grave set G, about a tenth from W)

Minted from mini-friend Phase 1b (`minifriend-phase1b-2026-10-23/RESULTS.md`,
gated; declaration ruled as declared, owner 2026-10-23 "No need to
change the declaration. Let's run this as proposed"; her ask quoted in
the declaration; deviations entry 11). Data: five per-cat grave sets,
one friend per block starting grave at reset by spec 065's per-kitty
`initial_needs` ({60, 95}) with the other four at the served default,
20 worlds per friend at 4,000 ticks (seeds 1095451–1095550), the
certified roster rot2 on the served 20×20; 0 aborts, distress confined
to the grave kitty in all 100 worlds; 4,000,000 evaluation samples on
50 worlds split by world; every friend over min-n on mind-visible
GRAVE (per friend: RESULTS §"Samples and coverage"), Pumpkin covered
for the first time. Heads: Phase 1's architecture at widths 12
/ 24 / 48 (3,043 / 7,807 / 22,519 parameters; 48 an over-cap probe,
never a Phase 2 candidate), NF and DR, three seeds each, trained on
34 of Phase 1's 41 non-evaluation L/W/G worlds plus 40 P training
worlds, validation re-carved under this arc's split seed
(not Phase 1's seven). Pooled mind-visible
MSE on the five hidden needs at width 24: COMMON 25.34 ± 0.52 (NF) /
40.15 ± 6.85 (DR), GRAVE 908.10 ± 33.43 / 827.69 ± 117.06; baselines
3,264.16 (marginal) / 3,261.15 (proxy) on GRAVE. **The all-grave
confound** (R5b, every cell there): the same heads' GRAVE loss on
Phase 1's all-grave evaluation worlds over their loss on the per-cat
worlds is READ under 1 at every width and both weightings: the
all-grave worlds, where an observer's own needs predicted her
friend's at the start, were 21–39% easier in squared error for the
same heads (23–35% in sight). The ratio bounds the
difference between the registers and does not isolate the cue's
share (different evaluation worlds and, in sight, different friend
pools); it is the number behind F-064's "upper bound" caveat.
**The size effect** (R2b, in sight; the GRAVE and COMMON ratios are
the headline's, the DA ratios beside them in R2b): every NF ratio to
width 24 READ, DR's at 48 READ; the DR 12/24 ratios not READ (DR's
between-seed spread, propagated into the ratio, exceeds the width
difference). For NF, halving the width costs about 20% in sight
and doubling it past the cap buys about 12–13% in sight (9–11%
all-states), in every stratum; for DR the 48/24 step buys 17–23% in
sight (13–21% all-states); in points the grave stratum gains most
because it is the largest cell (NF grave RMS 30.1 → 28.1, common 5.0
→ 4.7). **Ostrich** (R4b; signature rule prereg §8 item 4; per-friend
biases in R4b): NF pooled grave bias in sight −13.58 / −10.10 / −9.68
at 12 / 24 / 48 against a pooled common-state bias within 0.5 of zero;
signature on Miso, Biscuit, Pumpkin and Kittybear at 24 and 48 (at 24
Kittybear deepest; Biscuit read without it in Phase 1), not on
Clementine; DR pooled −7.38 / −7.57 / −6.06 with the signature on the
same four. **Dissolution** (R3b, Phase 1's procedure as information;
DR's floors, NF's excess over them and the friends exceeding at each
width in R3b): the pooled clause holds only at width 24 and only just
(1.097 against 1.10); the per-friend clause fails at every width;
Clementine's grave loss is lower under NF at every width and she is
the one friend DR hurts (by width: R1b (d)). The width did not change the
verdict; what differs from Phase 1 is the register together with the
retrained heads, their training set and validation carve, and on the
all-grave G worlds these same heads read NF/DR grave 1.227 / 1.018 /
0.997 at 12 / 24 / 48, so Phase 1's pooled NF advantage is absent for
these heads there too at 12 and 24. **Caveats the section carries**:
the grave stratum is a grave START relieved by the roster (about 61
grave ticks per observer-episode for Miso, 2,440 all-states GRAVE
samples over 40; a count, not a timing), seen by an observer for 13–29% of its ticks (a friend's
GRAVE spell is the start of her episode); in sight the G side of
R5b pools four friends (Pumpkin under min-n on G alone) and the P side
five, all-states both sides five; the
DR heads stop earlier than NF's and disagree between seeds (best
epochs 21–53;
between-seed SD up to 139.56 on a pooled grave cell), so a
friend's DR grave mean moves by 56–213 points² between neighbouring
widths with between-seed SDs of the same order (up to 226.98); the G-side losses are not Phase 1's
cells (new training set, G-only evaluation worlds) and are never
compared to them; the 1.5× lift is met trivially wherever the common
bias is near zero, so the gap in points, not the flag, is the
informative column. **Scope**: the certified Gen 2 roster at the
served 20×20, greedy masked argmax, schema 6 observations (as Phase
1); offline heads, no consumer read (RESULTS "Not read"); three seeds per head,
the NF/DR pair sharing each seed; one grave friend per world. **Does
not move**: F-064 (its worlds, floor and verdict stand); the §8 item 4
cap (a wider Phase 2 head is a deviations entry on the owner's word
with R2b as its evidence). **Invalidated by** (domain: this
declaration's reads re-run on a Gen 2 roster with at least three seeds
per head, the same strata and min-n, one friend grave per world; all
three bars on the pooled mind-visible cells): the G-over-P grave
ratio at width 24 at or above 1 − SD for NF (checked on this entry's
evidence: 0.651 ± 0.033, fires at 0.967); the 48/24 NF grave ratio at
or above 1 − SD (0.870 ± 0.053, fires at 0.947); the NF pooled
mind-visible grave bias at width 24 at or above −1.5 points (F-064's
bar; −10.10). **Re-verify
when**: a register exists in which a friend enters GRAVE during the
episode rather than at reset; Phase 2's live head is read
(§9 item 2); any change of roster or schema. **Promotion**: an input
to the Phase 2 head choice (hers) beside F-064: at Phase 1's width,
in this register, the reweighted head is the better grave estimator
pooled and the natural-frequency head under-reads a grave friend in
sight by ten points; neither is free (DR costs 14.81 points² of
pooled mind-visible common-state error and hurts Clementine).

## F-066 · active · A structured discrete belief head (per-need 20-bin histogram with learned drift and relief, cross-entropy on two-hot targets) does not beat the natural-frequency head NF on the declared grave cells at equal capacity: at width 16 (6,679 params) its pooled mind-visible grave MSE on the per-cat worlds is 1119.69 against NF-h24's 908.10 (1.233 ± 0.091, READ) and its pooled grave bias in sight is −15.01 against NF's −10.10 (signature on all five friends), while in sight it is better than NF in common states by about a fifth (19.96 against 25.34, 0.787 READ); width moves every pooled SD loss cell in one direction (in sight on P: grave 1.414 at 8/16, 0.819 at 32/16, both READ; common 1.237 / 0.848), in proportion not grave-specific, and the 1.9×-cap probe (15,783 params) ties NF-h24 on grave in sight (917.44; 1.010 ± 0.083, not READ) at 2.0× NF-h24's parameters and is better by a third in common states (16.92; 0.668 READ); the grave probability the head emits is near the diagonal above p = 0.7 at width 16 in sight (realised 0.795 / 0.851 / 0.936 in the top three bins) with mean P(grave) 0.474 on grave samples, a belief whose histogram mean sits below the truth, which is the −15.01 the bias column reports and which the ostrich metric as declared does not separate from optimism; p_rel discriminates relief at AUROC 0.979 in sight and 0.797 under fog at width 16; six of nine runs hit the 200-epoch cap before plateauing and each run cost 10–14 hours against minutes for the comparators

Minted from mini-friend Phase 1c (`minifriend-phase1c-2026-10-23/RESULTS.md`,
gated; owner 2026-10-23 "Let's try it. Currently our accuracy is low
enough that we can reevaluate model size limit if needed. Let's test
this approach first though" and, the same day, "Let's try 3 model
sizes this time as well so we can get an idea of what more/less
parameters buy"; deviations entry 12). Data: none new (0 covered
cat-ticks); Phase 1b's split byte for byte (74 training, 17
validation, 69 evaluation worlds); group P = the P1..P5 evaluation
worlds (4,000,000 samples; per-friend coverage in RESULTS §Data), the
comparators 1b's width-24 NF and DR runs re-read through this arc's
reader and pinned to 1b's gated cells. Head (§"Heads (R8c)"):
`sd_head.py`, the headline's per-need histogram (20 bins of 5 points;
learned drift rates and relief sizes, the relief probability p_rel
from a width-r GRU over the 167 input cells, a logit residual, learned
priors), trained by cross-entropy on two-hot targets plus a
relief-indicator BCE and Phase 1's happiness and bath terms; natural
frequency; point estimate the histogram mean; widths 8
/ 16 / 32 = 3,279 / 6,679 / 15,783 params (32 an over-cap probe, cap
8,445 not moved); seeds 1, 2, 3. **Decision rules, applied**
(the declaration's two criteria for what would count as the approach
helping; width 16, group P, in sight): (i) grave SD / NF-h24 READ under
1 — read 1.233 ± 0.091, READ, over 1, not met; (ii) pooled grave bias
within ±5.0 with no pooled signature — read −15.01 ± 1.74, signature,
not met; by the declared text the approach does not help at this
capacity. Below, every read but the rates is in sight on group P, and
every per-width cell is in RESULTS §R1c–§R9c. **Accuracy** (R1c,
R2c): SD's grave loss
is above NF's on every friend at width 16 and below both comparators
in common states on every friend. **Ostrich** (R3c): the signature
fires on all five friends at every width, Clementine (positive for NF
and DR) included. **Calibration** (R4c, P(grave by need) = 1 − ∏(1 −
grave mass_i)): at width 16 under-confident below p = 0.7 and on the
diagonal above it; happiness-only grave samples (168 of 2,527 in
sight) cannot be carried by need histograms. **Rates** (R5c, width
16): the filter need not be physical and is not; the per-friend
emphases are recovered, many ordinary cells sit well under the
empirical step, and the play rate collapses for four friends.
**Residual share** (R6c): no-residual over full grave loss meets the
structure-carries rule of 2.0× at 8 and misses it by 0.013 at 16; the
filter alone is worse than the marginal mean in common states at every
width (p_rel's AUROC by width: R6c(b)). **Floors** (R7c, information):
width 16 clears neither DR-h24 nor NF-h24; width 32 clears NF-h24
(every friend inside) and misses DR-h24 by 0.008 pooled. **Size**
(R9c): the cap binds for this head as it did for NF in 1b, on the
means at a rate like NF's or steeper (about 18% against 13% for the
doubling past the cap, spreads overlapping, the parameter steps
unequal, ×2.4 against ×2.9); at about equal parameters SD is behind NF
at every rung (3.3k: 1582.84 against NF-h12's 1098.53; 6.7k against
7.8k: 1119.69 against 908.10), and SD-h32 at 15.8k reaches NF-h24's
cell, not NF-h48's (790.22 at 22,519 params).
**Caveats the section carries**: six of
nine runs reached the 200-epoch cap with the validation loss still
improving by more than the plateau margin (best epochs 193–200; every
1b run plateaued by 82), which biases the comparison against SD by an
unmeasured amount and was reported, not re-run; every MSE and bias
cell reads the histogram mean, and the calibration read shows the
belief behind it on grave samples; SD saw an auxiliary target (the
relief indicator) the comparators did not, declared as the approach;
10–14 hours per run against 1b's 12–17 minutes for six, the
sequential per-tick filter loop being the cost; "ties NF-h24" at
width 32 is a tie at 2.0× NF-h24's parameters; offline, no consumer, no
welfare claim. What it hands to the Phase 2 head choice (hers) beside
F-064 and F-065: under the standing cap, and with the under-training
caveat above, SD at width 16 is behind NF on a grave friend in sight
(1.233 READ) and ahead of NF in common states (0.787 in sight, 0.902
all states, READ); the
structured head's grave probability and relief read are quantities
this arc reads for SD only, and whether a Phase 2 consumer should read
a probability rather than a mean is a design question this arc did
not answer; the cap question is hers with that read in hand.

## F-067 · active · A 25-parameter logistic read of "the true stratum is GRAVE" on the FROZEN NF-h24 GRU states reads grave within the seed spread of the structured discrete belief head SD at width 16 (F-066) and ahead of it on the grave mean and Brier in sight and under fog, with its mean on common samples as low: in sight on the per-cat worlds its mean P(grave) on grave samples is 0.583 ± 0.015 against SD's 0.474 ± 0.115 (Δ −0.109, combined seed spread 0.116 → outcome A of the declared rule, "the histogram bought nothing the consumer needs"), its Brier 0.00054 against 0.00064, its mean on common samples 0.0003 against 0.0005; under fog 0.720 ± 0.010 against 0.500 ± 0.046 (Brier 0.00119 against 0.00185); in sight SD keeps its reliability above p = 0.7 (above-0.7 gap 0.019 against 0.057; NF-h24+p's top bins realise 0.760 and 0.882 where they say 0.854 and 0.959) and a lower mean on adjacent samples (0.183 against 0.265); on the DR-h24 states the same probe reads 0.577 ± 0.037 in sight; all three rank grave against non-grave at AUROC 0.998–0.999 in every version, so the heads differ in confidence, not discrimination; every MSE and bias cell of F-064 / F-065 / F-066 is unchanged by construction (the frozen heads' own output reproduces 1b's predictions to 3.9 / 4.5 / 3.7 / 3.0 / 2.4 / 3.6 × 10⁻⁷); the hybrid (a Phase 1 head plus one sigmoid) is 7,832 parameters, under the cap; the Professor's registered prediction P2 (≥ 0.40 on grave, ≤ 0.002 on common, in sight) is met. Beside it, the SD filter's drift operator smears a sharp belief exactly as the arithmetic says — sd √(n f (1 − f)) bins, matched to 2.3 × 10⁻⁸ bins over 79 unclamped rows; 2.708 bins (13.5 need points) after 100 ticks at every run's initial rate, 1.56–1.87 bins after 100 ticks at the learned width-16 median rates — while the engine's need rises with no uncertainty; the mechanism the Professor named for F-066's residual share stands as arithmetic, its causal share unmeasured

Minted from mini-friend Phase 1d (`minifriend-phase1d-2026-10-24/RESULTS.md`,
gated; owner 2026-10-24 "Let's run those in three in the order you
listed", after the Professor's review of Phase 1c; deviations entry
13). Data: none new (0 covered cat-ticks); Phase 1b's split byte for
byte; the probe trains on every (world, observer, friend, tick) of the
74 training worlds; reads on group P (P1..P5, 4,000,000 samples; the
sample and grave counts per version in RESULTS §Data). **Read 2, the
probe** (`grave_probe.py`; fit recipe in DECLARATION §"Read 2", runs
in RESULTS §"R2d(b) — runs"): 1b's NF-h24-s{1,2,3} and
DR-h24-s{1,2,3} loaded, frozen, walked as `predict_world` walks them;
`Linear(24 → 1)` + sigmoid by natural-frequency BCE on the stratum
label, early stop on the validation BCE with a RELATIVE margin; every
fit stopped on the plateau rule, none at the 200-epoch cap; read
through 1c's R4c instrument (`calibration_p`) beside SD width 16's
committed cells. **Decision rule, applied** (declared before any fit;
group P, in sight, every covered sample pooled, mean of seeds 1–3;
comparator SD width 16 from 1c's committed read, base head NF-h24;
m = mean P(grave) on GRAVE, Δ = m_SD − m_NF, s = √(s_SD² + s_NF²) over
the seed SDs, g the above-0.7 gap): A if |Δ| ≤ s; B if Δ > s and
g_SD < g_NF; C otherwise — read Δ = 0.474 − 0.583 = −0.109, s = 0.116,
**A**, applied as declared; the stronger reading (the probe above SD on
the grave mean in every version and lower on Brier) is reported, not
ruled on (s is almost entirely SD's seed spread, 0.115 against the
probe's 0.015; one SD seed, 0.601, sits above the probe's mean of
0.583). **Read 1, the spread** (`filter_spread.py`, read-only on 1c's
nine `head-best.pt`; RESULTS §R1d): a delta at bin 2 pushed n ticks
through 1c's `shift_matrix` at the initial rate and at each run's median,
largest and smallest learned cell, no relief, no residual; sd equals
√(n f (1 − f)) at the printed precision on every unclamped row; the
largest learned cells overrun, piling the belief into the top bin (sd
0.000 by 500 ticks); one relief step adds at most 0.5 bins of sd.
**Caveats the section carries**: the
probe is calibrated on the training distribution and read on the
evaluation worlds (under-confident below p = 0.5, over-confident in its
top two bins in sight); nothing was tuned and the states were trained
for a squared-error mean; SD's P(grave) is derived from five need
histograms under an independence assumption and cannot carry the
happiness-only grave edge (168 of 2,527 in sight) that the probe reads
at 0.676 (NF) and 0.783 (DR) in sight; discrimination saturates (AUROC
above 0.998 for every head), so the read separates how much
probability each head commits, which a consumer reading the number
sees and one ranking by it would not; R1d is arithmetic on the operator, not an ablation of the
training; group P, offline, no consumer, no welfare claim. What it
hands to the Phase 2 head choice (hers) beside F-064, F-065 and F-066:
if the Phase 2 consumer reads a probability, a Phase 1 head with one
sigmoid on its state is the candidate shape and the SD line closes
under its own declared rule; DR-h24+p reads 0.577 ± 0.037 in sight and
0.685 ± 0.042 under fog beside NF-h24+p's 0.583 ± 0.015 and 0.720 ±
0.010, with the smaller above-0.7 gap in sight (0.022) and 0.783 on
the happiness-only grave samples in sight, and the Phase 2 head choice
stays hers; the hybrid is under the cap (7,832 ≤
8,445). Professor's P1 (a longer-cap SD re-run stays READ over 1
with the signature on ≥ 4 friends) is carried forward unscored.

## F-068 · active · The base head's five means name the grave need, the frozen-state grave probability is over 0.2 before a mid-world grave episode begins in most cases, and a consumer reading the means against 90 misses half or more of them: on the per-cat worlds NF-h24's means name a grave need on 0.871 ± 0.031 of the need-grave samples in sight (top-2 0.969; the always-name-drink baseline 0.353; DR-h24 0.872 ± 0.010; SD-w16's grave mass 0.739 ± 0.043, its mean 0.687 ± 0.031) and 0.867 under fog, play the weakest need (0.783); of 288 grave episodes over observer slices (72 friend-episodes × 4 observers) 200 are RESET episodes (grave at the world's first tick, group P's per-cat grave-start design; a crossing there is the prior, not a detection), 20 begin mid-world in the observer's sight and 68 mid-world under fog; on the mid-world fog-onset episodes NF-h24+p at P(grave) ≥ 0.2 detects 0.946 ± 0.042 at a median latency of 0 ticks and is over the threshold at the tick before onset as well in 0.931 of them, on the mid-world in-sight episodes 0.850 ± 0.087 (anticipated in 0.833), over all onsets 0.912 ± 0.051 of the 34 in-sight-onset and 0.966 ± 0.016 of the 254 fog-onset episodes; its false-alarm runs are 0.90 ± 0.30 per 10,000 observer-ticks in all and 0.07 ± 0.02 excluding runs that start at the world's first tick; the max-of-means ≥ 90 rule on the same head detects 0.367 ± 0.058 of the mid-world in-sight and 0.490 ± 0.090 of the mid-world fog episodes (0.490 ± 0.045 and 0.686 ± 0.065 over all onsets, 3 ticks late at the median), on SD-w16's means 0.294 and 0.177 over all onsets at a median of 11.3 and 34.0 ticks; both declared reading rules hold as declared ((i) NF-h24 mean which-need in sight, pooled, ≥ 0.80 with every per-need cell of n ≥ 200 above 0.60; (ii) NF-h24+p at P(grave) ≥ 0.2 detecting ≥ 0.90 of the episodes with onset in sight at median latency ≤ 10 ticks — 0.912, by less than one of its 34 episodes, 0.850 on the 20 mid-world in-sight episodes alone, disclosed) and the registered prediction that the mean rule detects under half of the in-sight-onset episodes holds on the seed mean (0.490; per seed 0.500 / 0.441 / 0.529, one seed exactly at half and one over), so the verdict as declared is "enough for detection and naming, on this evidence"

Minted from mini-friend Phase 1d §Addendum (`minifriend-phase1d-2026-10-24/RESULTS.md`
§Addendum, gated; owner 2026-10-24 "Agreed, let's proceed. First the
breakdown by need and latency read", after a sanity-check exchange on
whether the minis give the main models what they need; deviations
entry 13). Data: none new (0 covered cat-ticks); the outputs of Phase
1b's NF-h24 / DR-h24 runs, 1c's SD-w16 runs and 1d's probes, read on
group P (P1..P5, 4,000,000 samples). **R3d which need** (domain sizes
and the confusion counts in RESULTS §"R3d — which need"): domain the
grave samples with some hidden need ≥ 90; named need = argmax of the
head's five per-need scores, correct when it is one of the sample's
grave needs; per-need cells all n ≥ 500 per seed; NF-h24's means in
sight name a grave play need mostly as another need, eat the strongest
need in sight (0.986). **R4d latency** (definitions in §"R4d —
latency"): episodes = maximal runs of stratum GRAVE on the truth
stream per (world, friend), one per observer, classed by onset (RESET
at the world's first tick; mid-world in sight; mid-world under fog —
the split added after gate round 1, the declared rules scored as
declared and the mid-world numbers disclosed beside them). On the 68
mid-world fog-onset episodes every probability head at 0.2 detects
over nine in ten at a median latency of 0; on the 200 reset episodes
SD-w16's P(grave) is over 0.2 at the first tick for every friend,
grave or not (its prior) while NF-h24+p and DR-h24+p cross at a
median of 1 and 0 ticks, and the world-start transient holds almost
all of the probes' false-alarm runs; raising the threshold to 0.5
costs NF-h24+p and SD-w16 mid-world detection and slows SD's reset
detection (SD-w16's median reset latency at 0.5 is 11 ticks against
NF-h24+p's 1; the per-head numbers in §"R4d — latency"). **Caveats
the section carries**: reset episodes are over two thirds of the sample
and the declared splits count a head's prior as a detection there;
the mid-world in-sight split rests on 20 observer-episodes (one is
0.05 of the detected fraction) and the mid-world fog split on 68;
rule (ii) as declared clears its bar by less than one of its 34
episodes; the which-need read
is the base head's means, not the probe's (the probe emits one
number; a per-need probability is a Phase 2 design choice); 43% of
the in-sight need-grave samples have two or more grave needs and
naming any one counts; fog-onset detection says the belief knows,
not that the cat can reach; the false-alarm rate counts runs per
tick, at the 0.2 rows most one to three ticks long, and what a run
costs depends on the consumer; one group, offline, three seeds. What it hands to the
Phase 2 declaration (hers) beside F-067: a probability-reading
consumer at 0.2 sees a mid-world grave episode as it begins in most
cases (median latency 0), the base
head's means are where the need's name is, and the mean-against-90 reading is the
ostrich as a missed-detection rate; a per-need probability output is
a design choice for the Phase 2 declaration, not read here, and both
thresholds are printed so no single operating point is privileged.
Note 2026-10-24 (RESULTS §Addendum 2, gated): an operating-point
sweep over 0.05–0.50 found that nearly every false-alarm run this
entry calls "mid-world" starts within a slice's first hundred ticks,
so the start-up transient is about a hundred ticks long rather than
the one tick set aside here; the detection numbers above are
unaffected, and the false-alarm rate reads as mostly start-up.
Note 2026-10-25 (RESULTS §Addendum 3, gated): a burn-in read found
that every grave episode this entry calls "mid-world" begins inside a
slice's first hundred ticks — on the per-cat worlds each is the friend
that was grave at the world's first tick crossing back into grave
during the start-up — and that no grave onset in either evaluation
set comes later; the detection numbers above stand as printed, but
they are start-up detections, and neither set holds a mid-world grave
onset in the sense this entry's wording suggests (the lived worlds
hold none at all, which is evidence of rarity, not absence). Inside
the start-up window a higher threshold separates the grave-start
slices from the rest better than a lower one. What Phase 2 reads, and
on which set, is the owner's.
Note 2026-10-26 (RESULTS §Addendum 4, gated): the detection numbers
above are detections by a young state (every onset in the evaluation worlds at or before offset 90, the reset episodes at most 238 ticks long); at
P(grave) ≥ 0.10 the same covered grave rows spliced after 100 clean
ticks of lived history are detected in about a third of episodes, and
a warm-started state detects the real reset episodes on the per-cat
worlds in about six in ten (F-069). The
numbers stand as printed for the start-up domain they were read on.

## F-069 · active · The frozen NF-h24 head's grave probability is a property of the young state (at P(grave) ≥ 0.10 on the per-cat worlds unless stated): the same covered grave rows that it detects in 0.995 ± 0.009 of 200 reset episodes at a median latency of 0.3 ticks when they arrive at a world's start are detected in 0.358 ± 0.175 (0.540 / 0.345 / 0.190 per seed) at a median latency of 26.5 ± 12.4 ticks when spliced after 100 clean ticks of a lived world's history, 0.287 ± 0.143 and 0.288 ± 0.132 after 500 and 2,000, with a junction control of default-start rows never firing (0.000 at H = 100 / 500 / 2,000 at every threshold) and SD width 16 collapsing alike (1.000 → 0.275 → 0.282 → 0.287); the self block is not in it (H = 0 with the recipient's self block 0.995 / 0.972 / 0.968 at 0.10 / 0.30 / 0.50 against 0.995 / 0.970 / 0.965); the same head warm-started at the mean state over ticks 1,000 … 19,999 of L's clean slices detects the real reset episodes at 0.592 ± 0.066 (0.650 / 0.520 / 0.605 per seed) against 0.995 while every first-tick false-alarm run disappears (614.0 ± 322.2 → 0.0) and the clean slices' start-up firing goes 0.767 ± 0.403 → 0.000 ± 0.000; on L's clean slices the state's step does not shrink (median 0.0480 ± 0.0009 in ticks [1, 100), 0.0571 ± 0.0024 from tick 1,000 on) and the logit has no trend (0.0001 ± 0.0021 per 1,000 ticks against a within-slice SD of 0.9387 ± 0.0775), while the mean logit is −1.829 ± 0.598 at tick 0 (P(grave) 0.178 / 0.075 / 0.192 per seed), −4.059 at tick 1 and −9.371 at tick 10; the training worlds (every set) hold no grave after offset 322 (182 onsets, the latest at 171, 1 after tick 100; the validation worlds to 601, the evaluation worlds to 779); a burn-in of 2 ticks at 0.10 on the per-cat worlds takes all-runs false alarms 1.607 ± 0.805 → 0.136 ± 0.063 per 10,000 observer-ticks at reset detection 0.980 (5 ticks: 0.073 ± 0.001 at 0.960; 10: 0.072 ± 0.004 at 0.798) while on L / W / G the same burn-ins leave 0.538 → 0.521 → 0.577 per 10,000; swapping the observer's self block on the 200 grave-start slices moves reset detection 0.995 → 0.992 and the re-entries 0.900 → 0.883 in sight; the Professor's P4 and P8 are met, P3 and P5 not met as operationalised, and the condition named for reopening SD is not met

Minted from mini-friend Phase 1d §Addendum 4
(`minifriend-phase1d-2026-10-24/RESULTS.md` §Addendum 4, gated round 2;
owner 2026-10-25 "Let's do another threshold sweep rather than choosing
an arbitrary value. Maybe 0.1,0.3.,0.5 to start so we can get a feel
for the trade-off. Zero-collection reads first. …" and "Yes on splice
test. Yes on relay to product. Confirm 3", after the burn-in report and
the Professor's note of the same day; deviations entry 13). Data: none
new (0 covered cat-ticks; no weight touched) — the saved observation
streams of the evaluation worlds, Phase 1b's frozen NF-h24 heads, 1d's
three probes and 1c's SD width 16 heads, re-run by the reader exactly
as the probe fit walked them (the re-run P(grave) equals the committed
file on the first group-P evaluation world to 0.0e+00 on every seed).
Method in RESULTS §Addendum 4's opening paragraph and R7d (a)
convergence, (b) the splice, (c) burn-ins and the warm start, (d) the
self-block swap, (f) the fitted worlds. **The splice** places group
P's 200 reset-grave episodes over observer slices (the friend's
58-cell row over the episode, 14 in sight at onset) after H clean
ticks of one of L's 60 evaluation slices, with the recipient
observer's own self block continuing and a junction control of a
default-start friend's rows over the same ticks; H = 0 is the donor
episode in its own slice on the committed signal. Every table at 0.10
/ 0.30 / 0.50; after a clean history 0.10 detects the most (H = 100:
0.358 / 0.228 / 0.162) with the control at 0.000 at all three.
**Caveats the section carries**: the splice
junction is a jump into a covered friend's grave, not a crossing (the
donor's rows are the first ticks of its own world beside a self block
from another), so the read licenses the dependence of the response on
the state's history for a covered grave signature as recorded and
says nothing about a slow crossing from below, which no set on disk
contains; 14 of 200 donors in sight at onset; one warm start, not a
search; the fitted-worlds table is a fact about the data, and the
reads do not measure whether the collapse is learned from it; the
self block is separated from the state only at the zero state and at
H = 0. What it hands to the Phase 2 declaration (hers): the detection
numbers of F-068 are start-up detections by a young state; whether
the head sees a covered friend's slow crossing into grave after a long
clean history is unanswered by any set on disk, which holds none; the
threshold and the burn-in are hers on the three-point ladder, where a
2–5-tick burn-in removes the first-tick transient on the per-cat
worlds at little cost to reset detection and does not on L / W / G,
and the warm start removes it at a large cost.

## F-070 · active · The frozen NF-h24 head's grave detection falls gradually with the length of the clean history before the grave rows, most of the fall over by 20 ticks (at P(grave) ≥ 0.10 on the §Addendum 4 splice, group P's 200 covered reset-grave donors onto L's 60 clean recipients, seeds 1–3, unless stated): the same covered grave rows detected in 0.995 ± 0.009 of episodes at a world's start are detected in 0.978 ± 0.003 / 0.970 ± 0.009 / 0.852 ± 0.038 / 0.658 ± 0.096 / 0.537 ± 0.063 / 0.362 ± 0.070 after 1 / 2 / 5 / 10 / 20 / 50 clean ticks and 0.358 ± 0.175 after 100, at median latencies from the junction of 1.0 / 1.3 / 3.7 / 11.3 / 16.3 / 24.7 ticks against 26.5 at 100, with the junction control of default-start rows firing in 0.010 ± 0.017 of junctions at H = 1 and 0.000 from H = 2 on; the knee by the declared midpoint (0.641 between the start's 0.995 and the 500 / 2,000 plateau's 0.287) is at H = 20, with H = 10 just above it; at 0.30 and 0.50 the curve sits lower at every H (H = 10: 0.482 / 0.378); SD width 16 at 0.10 sits lower on the seed means at every H ≥ 5 (0.762 ± 0.185 / 0.487 ± 0.332 / 0.403 ± 0.306 / 0.297 ± 0.165 at 5 / 10 / 20 / 50; knee at 10), with one of its three seeds (seed 3, whose control still fires 0.140 / 0.130 there) above every NF seed at H = 10 and 20, while its rows at H = 1 and 2 are its own start-up transient (control 1.000 / 0.985) and its seed-mean control is under 0.05 only from H = 10; the Professor's P9 is not met as operationalised (0.658 at H = 10 is under 0.70; 0.537 at H = 20 is 0.178 from the committed 0.358 at H = 100, over its seed SD of 0.175 by 0.003); the provisional 2-tick burn-in of decision 3 sits inside the window in which the head sees a covered grave (0.970 at H = 2, 0.852 at 5)

Minted from mini-friend Phase 1d §Addendum 5
(`minifriend-phase1d-2026-10-24/RESULTS.md` §Addendum 5, gated round 3;
owner 2026-10-26 "Run the knee read now", on the walkthrough after
§Addendum 4's report, decision 3 ruled provisionally the same day at
0.10 with a 2-tick burn-in; deviations entry 13). Data: none new (0
new cat-ticks; no weight touched) — `history_read`'s splice
unchanged at six new history lengths, the same donors and recipients
as F-069, the recipient's self block continuing from the junction, the
head from the zero state; H = 100 re-run and equal to the committed
§Addendum 4 rows in every leaf; reader `knee_read.py`, 8 s. **Caveats
the section carries**: the junction is a jump into a covered friend's
grave, not a crossing (F-069's limitation); 14 of 200 donors in sight at
onset; one ladder of six H values, three seeds per head, NF's seed SD
at H = 10 (0.096) a third of its fall between 5 and 20; SD's rows at
H = 1 and 2 are its own transient (control 1.000 / 0.985) and at H = 5
one seed's is (control 0.365 on seed 3, 0.000 on the others), so SD's
curve is read from H = 10, where its seed-mean control is under 0.05,
with seed 3's control still firing 0.140 / 0.130 at H = 10 / 20 and
that seed clean only from H = 50; the false-alarm column of the tables
is, for NF, a count of recipient start-up runs over the whole spliced
index, not a rate comparable across addenda, and for SD seed 3 holds a
few runs that are not start-up runs (3 of 184 at H = 20 and 6 of 206
at 50 and 100, at 0.10); the knee's midpoint is one declared
convention and the curve is the result. What it hands on: the needy
set's onset strata are set from this number (DECLARATION §Addendum 5),
and the curve the declaration will read has 0.978 at H = 1 and 0.658 at
H = 10; the question F-069 left open, whether a slow crossing into grave
after a long clean history is seen, is still open (F-069).
