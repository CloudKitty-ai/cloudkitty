# Purrsonality register

Measured behavioral traits of CloudKitty minds — the companion to
[README.md](README.md)'s certification records. That file says a
policy is *safe*; this one says who it *is*. Entries are
measurement-backed only (no vibes without a probe), cite their
evidence, and state the company they were measured in — personality
is audience-dependent (F-012), so a trait line without its context is
not a trait. New entries follow the template at the bottom; traits
graduate into ROADMAP fingerprint gates when a seat conversion needs
them frozen.

---

## e004-a1-s2 — "the founding purr culture" (DEPLOYED, all four seats)

Artifact: `e004-a1-s2.ckpolicy` (v2) · certified exp-004 §9 ·
live since 2026-08-09.

- **Voice**: purr-dominant (~168/1k on-policy), want-words atrophied.
  Invented the **contact call**: purrs at the far point of an
  excursion ("I'm fine out here"), answered society-wide within the
  window (74.5% vs 53.4% baseline), steers hearers *away*; and
  repurposed **FollowMe as an approach announcement** ("I'm coming,
  stay put" — the speaker does the following).
- **Sociality**: cosleep-heavy; rotating pairs, no exclusive duets.
- Evidence: `experiments/exp-004-meow-channel/results/`
  (purr-deliberateness, purr-semantics, followme-2026-08-11).

## attn-A1-s1 — "the cuddler" (candidate, uncertified)

Artifact: `experiments/attn-ppo-2026-08-13/artifacts/attn-A1-s1.ckpolicy`
(v3) · sha256 `d8e31021…` · attention generation, A1 recipe seed 1.

- **Voice**: quiet purr economy (192/1k), far-ping deixis — the
  deployed generation's dialect at the deployed volume.
- **Sociality**: tightest spacing (nearest 2.59), most contact
  (.475), deepest sleeper (22% of decisions), most cosleep (23%);
  **everyone's preferred pile partner** in mixed company — the
  roster's social hub.
- **Robustness**: composition-robust (happiness 95.07–95.15 in every
  measured company; best welfare of all eight A1 runs, both
  architectures).

## attn-A1-s2 — "the loner" (candidate, uncertified)

Artifact: `…/attn-A1-s2.ckpolicy` (v3) · sha256 `f1a198a0…` · seed 2.

- **Voice**: mid-chatty (306–358/1k), the only seed keeping
  want-words measurably alive (WantEat 0.58/1k, FollowMe 0.28/1k).
- **Sociality**: most alone-time (.35), widest spacing, least
  grouping; self-sufficient and content (95.0 everywhere); bonds
  most readily with s1 (the quiet pair).
- **Robustness**: composition-robust.

## attn-A1-s3 — "the doter" (candidate, uncertified)

*(Renamed from "the groomer" 2026-08-14, owner's call — the older word
carries baggage the cat doesn't deserve. Earlier results docs keep the
original term as immutable records.)*

Artifact: `…/attn-A1-s3.ckpolicy` (v3) · sha256 `dfef0ec2…` · seed 3.

- **Voice**: chatterbox (794–808/1k — five of six decisions carry a
  word), and **inverted purr deixis**: purrs when close (2.54 vs
  3.73 declined), a companionship hum, not a distance ping. Per-purr
  causal potency undiminished at 4× volume (no devaluation).
- **Sociality**: the most social cat measured (31% social decisions)
  — through **grooming, not sleep**: GroomKitty 12.0% of decisions
  (85× its siblings' rate; classes dead in every pre-v4 generation).
  Cosleep drops to 13.6%. Runs a **gift economy**: grooming services
  the groomee's Bath; gives ~half its care outward unreciprocated,
  keeps one mutual bond with kin (53% kin share when a sibling
  exists).
- **Robustness — the caveat**: welfare is dose-dependent in its own
  kind: 94.87 among kin → 94.51 with one sibling → **93.93 alone**
  among quieter cats (gives without receiving, WantBath asks
  quadruple unanswered, drifts peripheral). **Seat with kin or not
  at all.**

## Measured roster: [s1, s2, s3, s3] (owner candidate, 2026-08-14)

All seats ≥ 94.5; two natural friendships (kin doter pair 9.3k
ticks/dyad, quiet pair 8.5k) with strong cross-links; no isolate;
s1/s2 bank s3's grooming as reclaimed self-care (−25% groom-self).
Loudest measurable roster (~500 meows/1k world-wide, ~3× live).
Evidence: `experiments/attn-meow-econ-2026-08-14/` (results.md,
valence-results.md) + `experiments/attn-ppo-2026-08-13/results.md`.

## The deployed world — candidate B, first live census (2026-08-17)

Measured on the box, ticks 1,023,004–1,024,817 (25 polls x 60s,
2,508 unique activity events; instrument
`experiments/attn-cert-2026-08-14/live_census.py`, raw
`results-raw/live-census-1023004.json`), immediately after the G6
soak verdict. Seats: Miso=attn-a1-s1 (the cuddler) ·
Biscuit=e004-a1-s2 (the founding purr culture) · Pumpkin &
Kittybear=attn-a1-s3 (the doters, kin pair). Lab entries above are
the priors; this is the live truth.

- **The doter kin pair is real on the box.** Pumpkin<->Kittybear is
  the strongest and most reciprocal grooming edge (36 + 41 events) —
  the valence lab's 2.2x kin preference, confirmed in production.
- **The cuddler is groomed, and is the pile.** Miso gave 3 grooming
  events and received 73 — the one-way service edge the s1 culture
  predicted — and sits in 8 of the 10 cosleep pair-observations
  (Miso+Biscuit 4, Miso+Pumpkin 2, Miso+Kittybear 2): the sleepy
  cuddler is the pile's nucleus.
- **Everyone else grooms everyone.** Biscuit 83 given / Kittybear 94
  / Pumpkin 85 — the responder culture generalized across dialects;
  no isolated seat.
- **Proximity fabric**: Pumpkin lives closest to the others (mean
  nearest 2.08 tiles, 84% of polls within 2) — the eat-0.8 seat's
  bowl-anchored orbit; Kittybear reads most peripheral (3.24, 64%) —
  the lab's s3 peripheral drift expressed by ONE of the two doters,
  the one without the trait pressure. Same mind, different body,
  different orbit: the bodies layer visibly steering a shared
  culture.
- **Welfare, live vs certified priors** (eval-band means in parens):
  Miso 95.44 (95.49) · Biscuit 95.20 (94.98) · Pumpkin 94.32 (93.95)
  · Kittybear 95.35 (95.03) — every seat at or above its prior,
  ordering preserved, Pumpkin lowest as certified. Soak context: one
  in-band distress event in 216k+ ticks (the soak record's verdict).
- **Voice**: not in this census (the REST surface carries no meow
  stream). The meow-economy lab numbers stand as priors — a ws-tap
  census is the noted extension if the live voice question opens.
- Method note: activity budgets in the raw JSON are event COUNTS
  (short activities over-represented vs tick-shares); the graph and
  pile readings above are count-safe.

**Bug-play baseline (2026-08-18, owner ask — the Biscuit-2.0
"before" picture)**: census ticks 1,082,536–1,084,348, play targets
across all four seats: solo 473 · kitty 17 · **bug 0 · greeble 0**.
Zero critter play in the deployed world — F-019's erosion signature
live (these minds trained under the annealed-to-zero leash era). The
post-seating comparison point: the 0.04-dose lineage arms measure
bug_over_meal 0.25–0.30 and time-near-critters 0.35–0.39 in probe
composition. Raw: results-raw/live-census-1082536.json.

**Zero-play baseline RE-BANKED (2026-08-21, SC-005 — the phase-1
roster's "before bugs-2.0" picture)**: the world above is gone
(--fresh 2026-08-21); this is the new roster (Miso/attn-a1-s1,
Biscuit/e004-a1-s2, Pumpkin/attn-a1-s3, Kittybear/e006-E1-s1,
Clementine scripted) on the pre-039 engine, censused deliberately
before the bugs-2.0 deploy so the before/after brackets only the
mechanics change. Census ticks 20,676–21,301 (12 polls, 1,593
events), play targets across all five seats: solo 266 · kitty 44 ·
**bug 0 · greeble 0**. The erosion signature carries into the new
generation — every seated mind trained under pre-bugs-2.0 economics
(the skill moat: unskilled bug EV 7.9 < solo 10 on that world).
Shorter window than the 08-18 baseline (9 min vs 25; solo-play
volume scales accordingly); zero-vs-nonzero is the banked claim,
not the rates. Raw: results-raw/live-census-20676.json.

**Boundary correction (2026-08-22, Product's flag)**: the bugs-2.0
restart landed at tick 20,978 — INSIDE the window above. The clean
pre-039 sub-window is 20,676–20,978 (~303 ticks); ticks
20,979–21,301 ran on new mechanics. The zero-play claim survives
the cut a fortiori (zero over the whole window ⇒ zero over the
sub-window); the rates cannot be split (the run predates raw-event
retention, added to the instrument same day).

**First post-deploy read (2026-08-22, ticks 22,037–22,663 — new
mechanics, ~1,100–1,700 ticks after the boundary)**: play targets
still **bug 0 · greeble 0** on all five seats (solo 257 · kitty 64,
1,578 events). The scripted seat included: Clementine's play is
kitty-partnered 27/27 — with four cats in reach, need-scheduled
play resolves to the better-paying duet, exactly the designed
ordering (duet-each 20 both-payer > bug 28 single). The unskilled
bug gradient is a training-time claim about learners, and the live
zero for frozen policies is F-019 erosion as expected — this read
is the "actual play numbers" starting point, not a failure of the
mechanics. Happiness healthy at every seat (policy 94.1–95.3,
scripted 90.7 ≈ the anchor band). Raw:
results-raw/live-census-22037.json. Longer-window census owed
before the owner's reward-tuning freeze question is called.

---

**Template for new entries**: name + epithet + status (deployed /
candidate / retired); artifact path, version, sha; Voice (rates,
kinds, dialect semantics with the probe that measured them);
Sociality (spacing, activity budget, pairing); Robustness
(composition sensitivity — always state the company measured in).
Update on new measurement, supersede by strikethrough + note, never
silently rewrite a measured claim.

**⚠ CORRECTION 2026-08-23 (F-029) — the "bug 0 · greeble 0" lines
above are an instrument artifact, not a measurement.**
`live_census.py` classified play targets by the 001 http-api
contract's ACTION shape while `/events/activity` carries the nested
ACTIVITY shape, so every critter play landed in the `kitty` column
and the tool could not emit a bug count under any world state
(registered F-029; fixed + guarded at main e02cf93).

- **First post-deploy read (ticks 22,037–22,663)** re-cut from its
  own retained raw events: solo 257 · kitty **46** · element **18**
  (Clementine 18 kitty / 9 element; Pumpkin 13/6; Kittybear 7/1;
  Miso 7/0; Biscuit-e004 1/2). The published "kitty 64" equals
  46 + 18 exactly. So "kitty-partnered 27/27" for Clementine is
  really 18 kitty + 9 element, and the "designed ordering — duet
  outbids bug" conclusion drawn from it does not follow.
- **Zero-play baseline (ticks 20,676–21,301, and its 20,676–20,978
  sub-window)**: that run predates raw-event retention, so it
  CANNOT be re-cut. Its "bug 0 · greeble 0" is unverifiable rather
  than disproven — and since every re-cuttable census from this
  roster shows element play, treat it as presumed nonzero. The
  a-fortiori sub-window argument recorded above inherits the same
  defect: it preserved a number the instrument could not have
  produced otherwise.
- **What still holds**: the policy seats' near-absence of critter
  play relative to solo play (1–6 element vs 45–96 solo here) —
  the F-019 erosion reading is unchanged in direction.
- **The post-cutover picture is different in kind**: the first
  Biscuit 2.0 census (ticks 143,222–145,500, after the boundary at
  125,349) reads **element 448 vs kitty 177** at the Biscuit seat —
  roughly 197 element plays per 1k ticks against ~3 for the e004
  mind that held the seat. A properly-classified census on the new
  roster supersedes this section for live-play questions.
