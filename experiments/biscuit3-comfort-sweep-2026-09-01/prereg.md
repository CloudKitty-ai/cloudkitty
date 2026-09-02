# Biscuit 3.0 comfort × score × weights sweep — preregistration
## (2026-09-01, Experiments; `biscuit3-design-note-2026-08-26.md` §The comfort sweep; owner-gated on the 041+bump soak, called 2026-09-01; bars pinned HERE before collection)

Engine: main @ 0df1e7f (crate tree unchanged since 41c6025: 041
economy, spec-042 dials in and inert at defaults, 044/045 inert,
contagion shelved). Debug build, headless local servers, tick_ms 40,
five in parallel on distinct ports.

## Question

Lever 1 of the design note: how much of scripted Biscuit's food gap
does a lower `playful_comfort` buy, and what does it cost in play?
Riders: do per-need comfort weights (spec 042 FR-005) buy the same food
gain for less play, and what does the partner-value score (FR-001–004)
do to whom Biscuit bothers? All scripted, no training: the subject is
the ANCHOR Biscuit 3.0 would be cloned from, so what moves here is what
the clone will be taught.

## Arms and configs

`gen_configs.py` rewrites the served `cloudkitty.toml` textually
(needflow-lab pattern): Biscuit's seat `playful`, the other four
`needs_driven`, tick_ms 40, `groom_cuddle_relief` 0.5 (the canonical
economy Biscuit 3.0 trains under; the served 2.0 is a temporary bump,
and F-036 says scripted decisions never read it), per-run seed / port /
snapshot, no `[water]` block.

| arm | playful_comfort | comfort_weight | note |
|---|---|---|---|
| c55 | 55 | identity | today's anchor (the baseline arm) |
| c45 | 45 | identity | |
| c35 | 35 | identity | |
| c30 | 30 | identity | the announce threshold: serious the tick a need arms |
| w35 | 55 | eat/drink/sleep 1.571429, others 1.0 | food band trips at 35.00, bath/cuddle keep 55 |

Each × score {off, on}. Score-on = the spec-042 candidate dials,
chosen before any data and disclosed as a first pass, not a tuned set:
`w_value 0.5, w_busy 1.0, w_serious 0.5, t_self 5.0, t_partner 5.0,
critter_appeal 0.0`. Reading: a friend's play need is worth half a tile
per point; a friend mid-scene pays one play-point per tick still owed
on its minimum; a friend's top non-play need costs half a play-point
per point; Biscuit bothers nobody under her own play need of 5, and
nobody whose value is under 5. Critter appeal 0 keeps the
critter-first tie.

10 arms × 2 seeds (20260911, 20260912) = 20 runs.

## Protocol (per run)

Fresh world (`--fresh --no-backup`); discard ticks < 1,500; measure
**20,000 ticks** (100k cat-ticks). Two pollers at 0.5 s (~12 ticks):
`needflow-lab-validation-2026-09-01/scene_census.py` for the scene mix
(F-031 rules, its own guard) and this directory's `run_sweep.py`
polling `/world` in the `need_latency.py` shape (needs, `last_relief`,
happiness, activity per seat). Archive final `/world` + `/welfare` and
the boot log. Raws → `results-raw/` (uncommitted).

Validity per run: `polls_in_window` ≥ 1,000 on the census poller and
≥ 1,000 world polls; watchdog read from the final `/welfare` (an alarm
is reported with the arm, not a re-run trigger).

## Readouts (Biscuit unless stated; pooled over both seeds, each seed shown)

- **R1 food latency** (`need_latency.analyze`, spec-028 band arm 30 /
  disarm 25): eat and drink armed excursions per 1k ticks, latency
  p50, time-above-30 share. In-run control: the four `needs_driven`
  seats' same numbers (the scripted floor, F-033 baseline 1–4 ticks).
- **R2 hungry-play share**: Biscuit play relief stamps (`last_relief.play`
  advancing between polls) taken while her eat or drink is ≥ 30 at
  that poll, over all her play relief stamps. Same definition as the
  2026-08-26 live baseline (15/86 ≈ 17% for policy Biscuit). Poll-level
  approximation, stated.
- **R3 play, and low-need play**: Biscuit's play scenes per 1k ticks by
  class (duet / element / solo, F-031 spans), and the LOW-NEED subset:
  scenes whose start tick has eat, drink and sleep all < 30
  (interpolated linearly between the bracketing world polls). Comfort
  cannot reach these by construction; second-order loss (time spent
  eating) can.
- **R4 roster play access**: play-duet scenes per 1k ticks for the four
  `needs_driven` seats, pooled and per seat. Biscuit is the roster's
  play supply.
- **R5 welfare**: happiness mean per seat; Biscuit's standing-demand
  price (happiness points); watchdog.
- **R6 score arm only**: mean partner play need at the start of
  Biscuit's duets (interpolated), duet share of her play, and R4.

## Pinned bars

Baseline arm is c55-off. "Gap" = c55-off Biscuit minus the pooled
`needs_driven` seats, on eat time-above-30 AND eat excursions per 1k.

- **P1 (character bound)**: an arm KEEPS the character if its low-need
  play rate (R3) is within −15% of c55-off, pooled, and its total play
  is within −25%.
- **P2 (gap closure)**: an arm CLOSES the gap if it removes ≥ 2/3 of
  both gap measures, pooled and in both seeds.
- **Decision (design note's rule)**: if some comfort arm passes P1 and
  P2, vector 2 is config + one lineage retrain at the highest comfort
  that does (report the whole curve; the value itself is the owner's).
  If no arm passing P1 removes even 1/3 of the gap, the gap is
  geometry/travel, not choice: redirect before training. In between:
  owner call on the curve.
- **P3 (weights)**: w35-off closes at least as much of the gap as
  c35-off does (within 0.25× of c35's closure on each measure) AND
  keeps more play (total Biscuit play ≥ c35-off's). Both must hold for
  "weights preserve more character" to stand.
- **P4 (roster supply)**: for every arm passing P1, the four-seat
  pooled duet rate (R4) is within −15% of c55-off. A miss names the
  arm as fixing one seat's demand by taxing four seats' supply.
- **P5 (score, comfort-matched pairs, both seeds)**: score-on raises
  the mean partner play need at Biscuit's duet starts (R6) vs
  score-off; Biscuit's total play stays within ±10%; R4 does not fall
  by more than 15%. Any miss is reported per dial family; refusal
  exposure is NOT measurable here (FR-004 makes it zero by
  construction; the refusal stamp is Product's fast-follow).

Report-only: happiness per seat, spans, duet share, excursion maxima.

## Guard

`test_score.py` on a RECORDED payload: two real polls from a lab world
plus real activity events, pins for (a) the interpolated need at a
scene start, (b) a play relief stamp counted hungry only when eat or
drink ≥ 30 at that poll, (c) the low-need filter dropping a scene whose
interpolated sleep crosses 30. Each shown red in-run (fixture edit
that should flip the pin) before commit.

## What this is not

Not a Biscuit 3.0 certification, not a claim about policy Biscuit (a
clone imitates with the leash's fidelity, but the transfer is the
training's to show), not a pricing of the score's refusal effect. The
score-on dials are one candidate point, not a sweep of the score; if
P5 misses, the next campaign sweeps those dials with this as its
baseline.

## Addendum 1: comfort 25 / 20 extension (declared 2026-09-01 before collection)

Owner's ask after F-038: extend the comfort curve to 25 and 20, and read
Biscuit's welfare on every need, not on eat alone. The eat-only reading
let w35 pass P3 while leaving cuddle, her highest elevated need at c55
(mean 30.8, 50% of polls ≥30), at 0.42; c35 took it to 0.26. Weight
bands are withdrawn; bath is the only need fine at 55 (7% ≥30), so a
band covering everything but bath is within noise of flat comfort. The
extension is flat comfort only, score off only (the score dials get an
offline pricing pass from this sweep's raws before any run).

**Arms**: c25-off, c20-off × seeds 20260911 / 20260912 = 4 runs, one
batch. Everything else as §Arms and configs (`gen_configs.py --ext`,
ports 8320–8323). Baseline stays c55-off from the main sweep; the c30
and floor figures it is read against are the main sweep's too.

**Why these two**: 30 is the announce threshold. At c30 Biscuit leaves
play the tick a need arms and meows about it; below 30 she leaves
before arming, so her food and cuddle meows should mostly vanish (R5).
The `needs_driven` seats eat at mean 21–27, so c20 should land on the
roster's food line (R1) and the reading of interest becomes how much of
her play survives (R3), which is the identity cost of feeding her.

**Readouts** (Biscuit unless stated; pooled, each seed shown):

- R1 **all-needs welfare** (primary): per need in eat/drink/sleep/
  cuddle/bath, mean level and share of polls ≥30, Biscuit and the
  pooled roster, from the /world polls. Plus happiness mean, worst
  poll, share of polls under 60.
- R2 lateness: eat/drink time>30 and latency p50 (F-038's surviving
  measures). Armed excursions per 1k is REPORT-ONLY with a prediction:
  it turns over below 30 (F-038 point 4 says it can only fall once she
  eats below the line most of the time; c25 < c30's 8.2, c20 within
  +1 of the floor's 4.4–5.0). A failure of that prediction reopens the
  mechanism, not the bar.
- R3 character: total play per 1k vs c55-off, split duet / element /
  solo; duet share.
- R4 roster supply: the four seats' pooled duet rate.
- R5 announce share: share of (poll, kitty) rows with a non-empty
  `announce_armed`, any need and per need, Biscuit and roster.

**Bars**:

- **E1 (roster-parity welfare)**: an arm reaches parity if, for each of
  eat, drink, sleep and cuddle, Biscuit's share of polls ≥30 is within
  +0.05 of the pooled roster's, pooled and in both seeds. (Bath is
  already within 0.06 at c55 and 0.00 at c30; reported, not barred.)
  Prediction: c20 passes; c25 passes on eat/drink/sleep and is the
  arm to watch on cuddle.
- **E2 (character)**: reported as the ratio to c55-off. The bound is
  the owner's: c30's 0.70x was accepted on 2026-09-01 ("0.7x play with
  solid element play is still very Biscuit"), which supersedes P1's
  −25% for this decision. Prediction: c25 0.55–0.65x, c20 0.40–0.55x,
  with element play taking the loss first and duets starting to fall
  below 30 (a serious cat does not start scenes).
- **E3 (roster supply)**: P4 as pinned, others' duets within −15% of
  c55-off.
- **E4 (troughs)**: share of Biscuit polls under 60 happiness no worse
  than c30's (0.0% both seeds); worst poll reported.
- **Recommendation rule**: recommend the highest comfort that passes E1
  and E3 if its E2 ratio is at or above the owner's accepted 0.70x;
  otherwise present c30 (accepted, E1 status as measured) against the
  E1-passing arm as the owner's trade. The pin is the owner's either
  way.

**Known before collection**: running the E-bars over the main sweep's
raws (`score.py`, same commit as this addendum) shows c30-off already
passes E1: gaps +0.04 / +0.04 / +0.04 / +0.03 pooled, seed 1 all ≤
0.037, seed 2 all ≤ 0.045; E3 PASS, E4 PASS. So by the rule above c30
is already the recommendation, and the extension cannot move it
upward. What c25/c20 can show is (i) whether Biscuit's residual +0.04
above the roster closes to zero or reverses (a `playful` cat that eats
before the roster does), (ii) the shape of the play cliff below 30
(E2), and (iii) the announce consequence (R5). The owner asked for the
curve; this is its exploratory tail, declared as such. If c25 passes
E1 with a residual under +0.02 AND keeps E2 ≥ 0.70x, that is reported
as a second candidate beside c30, not as a replacement.

**Guard**: `test_score.py` grows three pins on the same recorded slice
for the new primitives (per-need share and mean, announce share,
happiness trough), each shown red in-run before commit.

**Not here**: the score dial re-sweep (offline pricing first), any
policy Biscuit, any economy change. Re-verify trigger unchanged: the
pinned arm is re-run against the then-served economy before the lineage
retrain.

## Addendum 1b: comfort 32 / 28 (declared 2026-09-01 before collection)

Owner's ask after Addendum 1: bracket the accepted point. c32-off and
c28-off × the two seeds, 4 runs, one batch (`gen_configs.py --ext2`,
ports 8324–8327). Same binary, protocol, baseline and bars as Addendum
1 (E1–E4, recommendation rule unchanged). w arms dropped by the owner.

What the bracket can show: the two announce-threshold effects (meow
share, excursion turnover) should sit on opposite sides of 30, so c32
should look like c30 with a little more play and c28 like c25 with a
little more. Predictions, from the curve's slope between 35 and 25:
c32 play 0.72–0.78x, c28 0.62–0.68x; c32 fails E1 narrowly (gaps
+0.05–0.09), c28 passes; excursions c32 ≈ 8, c28 ≈ 4–6; announce c32
≈ 0.45, c28 ≈ 0.25. A monotone read between neighbours is the test; a
non-monotone reading (c32 below c30 on play, c28 above c30 on welfare
gaps) would say two seeds are not enough at this spacing and the pin
should not lean on a 2–3 point difference. No new instrument, no new
guard.

## Addendum 2: the consent gate at c30 (declared 2026-09-01 before the binary exists)

Replaces the HELD dial sweep. Owner's rule (2026-09-01): play can
always be proposed if the friend's top need is play; it cannot be
proposed if a non-play need is the friend's top need and that need is
over 30. Product implements it as the spec-042 dial `consent_line`
(0.0 = off, byte identity; brief sent 2026-09-01). Rejection is not the
target (RESULTS §Play rejection pricing); consent is.

**Arms**: c30-off (the existing raws, re-run on the new binary as the
identity check: the two must agree within seed noise) and
c30-consent30 (`consent_line = 30.0`, every other dial identity) ×
seeds 20260911 / 20260912. Four runs. Everything else as §Arms and
configs.

**Readouts**: R3 play split, R4 roster duets, Addendum 1 R1 (all-needs
welfare, Biscuit and roster), and a new **R7 consent share**: of
Biscuit's duet starts (census events, partner needs interpolated at the
start tick as `partner_need` already is), the share whose partner's top
non-play need is > 30 and above its play need. Report-only: blocked
partner's top need distribution; who she plays with instead (duet
partner mix); element share.

**R8 refusal tax (added 2026-09-01, owner's ceiling, before collection)**:
Biscuit's share of ticks spent refused into idle (a partnered proposal
bounced, `absorbed == false` on the spec-046 `/events/refusal` stamp,
which the rebuilt binary carries; exact field names pinned from a real
payload when the server is up, and `len(events) < capacity` checked or
the endpoint polled so the 6,000-event ring never drops a run's tail).
Read on both arms. Owner's rule (clarified 2026-09-01): **3.5% is the
line above which investigation is warranted**, not a retrain gate;
c30 + consent is itself the current response to the tax, and the
reading that decides is Biscuit 3.0's after training. R8 here is the
scripted early look, reported next to the E1 welfare gap (Biscuit vs
roster, all five needs), which is the quantity the whole arc exists to
close. Caveat carried:
the 4.6–4.7% figures on record are a POLICY seat's (Biscuit 2.0,
F-033, `idle_rewrite_probe.py` on seam traces); these arms are
scripted, so this is the first scripted-Biscuit reading with the
served instrument, not a before/after on the same seat.

**Review caveats folded in (Product's 047 review, 2026-09-01, before
collection)**: (1) R2 hungry-play share joins the readouts for both
arms, split duet / element / solo: when the gate drops a friend on the
get-serious path, play is priced as SOLO (as if the friend were absent,
the spec's declared degradation), so any welfare cost of the gate would
show up as solo play started while a need is ≥ 30, not in R7. Owner
walked it through and ACCEPTED the re-pricing as-is (2026-09-01):
training runs against this scripted cat, so marginal scoring detours
wash out; what matters is that consideration of other cats' needs is
MODELED so its learnability can be tested. Pinned INTENDED in-tree by
Product. R2 stays the report-only aggregate watch. (2) R7 is
read from census duet starts, never from the refusal ring, so
`finish_what_you_started` continuation refusals cannot make the gate
look leaky; R8 filters on `absorbed == false`, which excludes them by
construction (a mid-scene continuation is enforced, hence absorbed);
verified on a real payload before R8 is read. (3) C3/C4 compare levels
at one dial value against off; the duet delta includes chase-exclusion
tails paid when a mid-chase target is blocked, and the bars do not
separate that from the gate itself. Reported as one price, not
attributed. (4) `consent_line` is refused above 100 at load; this
addendum's arm is 30.0.

**Offline pricing that these predictions rest on** (c30 raws,
`consent_price.py`): 565 of 2,693 duets (21%) would be blocked; in 84%
of those an eligible idle friend stood within a median 2 tiles.

**Bars**:
- **C1 identity**: c30-off on the new binary reproduces the old c30-off
  within seed noise on total play (±5%) and eat ≥30 (±0.02), pooled.
- **C2 consent**: R7 falls from 0.19–0.21 to under 0.05 in both seeds.
- **C3 play kept**: Biscuit duets 60–64/1k (prediction; bar ≥ 0.90x
  c30-off's 67.3), total play ≥ 0.96x c30-off.
- **C4 roster supply**: roster duets ≥ 0.95x c30-off.
- **C5 welfare**: Biscuit's E1 gaps do not widen by more than +0.02 on
  any need; roster all-needs shares unchanged within ±0.02.

**Scope (clarified 2026-09-01 with Product, before collection)**: the
rule is unconditional, so the gate sits on every playful friend-play
start, not only the spec-042 ranking. Three sites on main 1f60b8d:
the ranking (`selection.rs:484`), get-serious via `choose()` →
`nearest_viable_playmate` (`selection.rs:46`, :384), and opportunism
via `take_what_is_here` → `adjacent_playmate` (`needs_driven.rs:159`,
`selection.rs:702`). Playful-scoped; needs_driven kitties never read
the dial; 0.0 short-circuits at each site. Sizing from the c30 raws:
Biscuit's own max need ≥ 30 at duet start (the get-serious path) in
167 of 2,693 duets, 22 of the 565 blocked; partner adjacent at the
poll before start in 64% of duets, 68% of blocked ones. A one-site
gate would leave C2 measuring the opportunism leak. Product owes one
redden-first guard per site.

**Recommendation rule**: C1–C5 all pass → the gate ships in the
Biscuit 3.0 anchor config at c30 (owner pins). C2 passes and C3 or C4
misses → report the price; owner call. C2 misses → the gate is not
doing its job (check the snapshot the gate reads against the census's
interpolation before anything else, then check all three sites fire).

**Guard**: `test_score.py` gains a pin for R7 on the recorded payload
(one duet whose partner is blocked, one whose partner has play on top,
one whose partner is under the line), shown red in-run before commit.

## Addendum 3: friend re-admission under the gate, and the re-proposal fix (declared 2026-09-02 before collection)

Owner ruled (a) on Addendum 2's price (2026-09-02): keep c30 + consent,
re-admit friends by dial only, "we still want element play so we don't
want to discourage that too much", and bake in the "don't re-propose an
ended play scene" fix. Owner then asked for the two effects separately
and combined. Two halves, one prereg.

**Correction on the record first.** Product's mechanism read for the
Addendum 2 price (the spec-042 eligibility bar dropping second-choice
friends) described the withdrawn c30-on arm, not the measured one:
c30-consent30 carried the score dials at identity (`gen_configs.py`
forces score off under `--consent`). At identity `scored_playmate` is
the classic pick (`selection.rs:429`): everyone scores −distance, ties go
critter-first, and opportunism is critter-first by structure
(`selection.rs:770`). So there was no `w_serious` or `t_partner` to
lower. The dial that re-admits friends without an element penalty is
`w_value`: a friend scores `w_value·(play − w_busy·wait) − dist`
against a critter's `0 − dist`. With `w_busy = 1/w_value` a tick of
wait costs one tile, the unit distance is already in.

Second correction: my Addendum 2 walk-through called about half the
partnered refusal rows a post-scene artifact. Product's replay probe
(2026-09-02, branch 275896e, never merges) found dead-at-snapshot duets
= 0 in all four arms: those rows are same-tick races (the partner
interrupted in an earlier apply slot), invisible to any snapshot-side
fix. R8 stands as declared. The artifact is real only for element rows
(critter moved off; dead at snapshot, 100% refused, 0 rescued:
554–788 per run) and a few groom rows.

**Offline sizing of the dial** (c30-consent30 polls, at each of
Biscuit's 2,376 / 2,318 element-play starts, nearest idle
gate-eligible friend at the bracketing poll): friend play need
quartiles 3.6 / 8.8 / 13.8 (seed 2: 4.2 / 8.8 / 15.0), distance
quartiles 2 / 4–5 / 9 tiles, 27–29% within 2 tiles, no eligible idle
friend in 6–8% of starts. At the median friend, `w_value` 0.25 buys 2.2
tiles of margin, 0.5 buys 4.4; 0.1 would buy under one tile. Bracket
= 0.25 / 0.5. Caveats: these are positions at the start tick, not the
decision tick, and the roster's play needs are low (mean 9–10), so the
margin is friend-need-limited, not dial-limited.

**Arms.** Half A, same binary as Addendum 2 (main f8a3bc0, built
2026-09-01): `c30-wv25` (consent 30, `w_value 0.25`, `w_busy 4.0`) and
`c30-wv50` (`w_value 0.5`, `w_busy 2.0`); everything else identical to
c30-consent30 (diffed). Half B, on the re-proposal-fix binary (Product
spec, lands on main first; commit recorded in RESULTS): `c30-fix-off`
(= c30-off2's config), `c30-fix-consent30`, `c30-fix-wv25`,
`c30-fix-wv50`. Seeds 20260911 / 20260912. Twelve runs; the Addendum 2
raws are the unfixed baselines. Ports 8332–8343 (`gen_configs.py
--add3 A|B`).

**Readouts** (all of Addendum 2's, plus): element refused-idle share
(R8's `by_action` split, the fix's target); roster-wide race rate
(partnered refused rows per tick, report-only); loiter share = polls
where Biscuit is idle with a busy friend on an adjacent tile (the
poll-resolution face of anticipatory approach, which any `w_value > 0`
switches on at `selection.rs:499`). Baselines already read: loiter
0.14 / 0.14 (off2 / consent30) with seed spread ~0.012; race 0.064 →
0.050 per tick; element refused 2.4% → 3.1% of Biscuit's ticks.

**Bars, Half A** (each `wv` arm; D1/D3/D4/D5 against c30-off2, D2 on its
own, D6 against c30-consent30):
- **D1 duets**: Biscuit duets ≥ 0.90x c30-off2 (≥ 60.6/1k; consent30
  sits at 49.0).
- **D2 consent kept**: R7 < 0.05 both seeds (the dial must not leak
  the gate).
- **D3 element floor**: element play ≥ 0.95x c30-off2 (≥ 90.9/1k). The
  gate's substitution (95.7 → 117.3) may be handed back; the dial may
  not take element play below where it stood without the gate.
- **D4 roster supply**: roster duets ≥ 0.95x c30-off2.
- **D5 welfare**: E1 gaps widen ≤ +0.02 on every need vs c30-off2;
  roster shares within ±0.02.
- **D6 loiter watch**: report-only; FLAG if loiter share exceeds
  c30-consent30's by more than 0.03 (2.5x the seed spread).

**Bars, Half B**, twin against twin (fix-off vs off2, fix-consent30 vs
consent30, fix-wv25 vs wv25, fix-wv50 vs wv50):
- **F1 element rows gone**: element refused-idle share ≤ 0.10x the twin's.
- **F2 partnered unmoved**: R8 partnered share within ±0.005 of the
  twin's (Product's prediction: races persist).
- **F3 within noise**: total play ±5%, duets ±5%, E1 gaps ±0.02 vs the
  twin. The fix recovers idle ticks; it is not expected to move the
  economy.
The fixed `wv` arms also get D1–D6 against `c30-fix-off` /
`c30-fix-consent30`, and the interaction is reported as the dial's duet
gain on the fixed binary minus its gain on the unfixed one.

**Predictions.** wv25: duets 49 → 54–58, element 117 → 106–112, D1
MISS, D3/D4/D5 pass, loiter quiet. wv50: duets 60–66, element 95–104,
D1 borderline, D3 borderline, D5 pass, loiter up but under the flag.
Prior from Product: the dial reopens site 1 only; sites 2 and 3 stay
critter-first, and the partner was adjacent in 68% of blocked duets, so
the recovery may undershoot the tile arithmetic. Fix: F1/F2 pass on all
four twins, F3 passes, element play +2–4/1k (the freed tick often
re-chases), everything else inside seed noise. Interaction ≈ 0.

**Recommendation rule.** A `wv` arm with D1–D5 all PASS and no D6 flag
→ recommend it as the Biscuit 3.0 anchor dial next to the gate (owner
pins; the anchor is c30 + consent30 + that `w_value`, re-run against
the served economy before the retrain). D1 MISS but D3–D5 PASS at both
values → the dial is safe but weak; report the curve, and Product's
option (b) (blocked-conditional friend-first, which can reach site 3)
becomes the next candidate, owner call. D3 or D5 MISS → the dial buys
duets with element play or welfare; do not raise `w_value` further.
F1 MISS → the fix did not land where the probe said; check the binary
before anything else.

**Guard.** `test_score.py` pins (j) element share and roster race rate
on the recorded ring payload (11 element rows; 17 partnered rows
roster-wide), (k) loiter share on three unedited c30-consent30 polls
(1/3), each shown red by mutating `score.py` before commit.
