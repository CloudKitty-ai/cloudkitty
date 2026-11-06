# Gen 2 deviations ledger

Opened at the prereg freeze (2026-10-17, owner "Do it";
`gen2-prereg-2026-10-17.md` §11). Every departure from the frozen
prereg lands here with its date, what moved, why, and her word where
one was given. Discrepancies resolve toward the ruling records.

## 1. Consent swap: 389 refusal rows keep the applied label (2026-10-18)

Frozen §4 pins the trunk trainer to consume PROPOSED-where-
consent-refused, applied everywhere else. In the full-100 corpus,
389 of 137,088 refusal rows (0.284%; consent_rows.py extraction,
`gen2-collection-driver-2026-10-14/results-raw/consent-rows-full-100.json`)
carry a proposed label the recorded decision mask forbids — every
one a PlayKittyN proposal absorbed to RestSolo, at rows where no
play action is on the student's menu. Masked cross-entropy cannot
train on an off-menu target, so the loader (`data_g2.load_rollout`)
swaps the 136,699 mask-legal rows and keeps the applied label at the
389-row residual, counting both (`swapped` / `unswappable`, surfaced
in the clone's metrics JSON). Chosen as the nearest-to-text fallback
(the pin's own "applied everywhere else"); dropping the rows from
the loss is the alternative, and the choice is reversible without
recollection — both label columns are in the corpus by the pin's
design.

Cause (traced 2026-10-18, owner's question): the proposer is
mid-rest INSIDE its activity minimum — the mask is an outcome claim
and duration enforcement collapses it to the continuation's entry
(mask.rs doc; all 389 rows have mask = [RestSolo] only). The
scripted teacher's ladder runs every tick regardless of its ongoing
activity and proposes play on need pressure (adjacency-legal per
the K§3 rider); the partner's consent gate declines it first
(action.rs refusal_reason, spec 059 order), and apply absorbs the
resolved Idle into the rest continuation (is_continued_by →
continue_current_activity), which is why the residual is 100%
RestSolo. The rows are doubly blocked — the teacher's play could
not have been applied even with consent — so the applied RestSolo
label is the engine's continuation law, not an artifact: the
fallback is the correct demonstration for a mask-constrained
student.

Loss-level fact (measured 2026-10-18 on row 2656 of r02, the
owner's drop-from-loss question): the §5 masked cross-entropy
(bc_loss2 → exp-001 bc_loss) pushes illegal logits to −inf, so on
a one-legal-action row the action-head loss and gradient are
exactly 0 whatever the label — keep-applied, swap, and drop are
gradient-identical on the action head, while the row's message
label (never refused) still trains the message head. Dropping the
389 rows would therefore change nothing the clone learns and would
discard 389 valid message-head demonstrations; the default stands
on that measurement.

RULED (owner, 2026-10-18): "Keep default, add teacher polish note
to gen3" — the keep-applied default stands for Gen 2; the teacher
polish (ladder skips partner proposals inside its own activity
minimum) is banked in `fog-gen2-timeline-2026-10-17.md` §Banked for
Gen 3.

## 2. Critic pretraining corpus extended for the mitigation (2026-10-18)

Frozen §5 carries the critic recipe on the trunk corpus (exp-002
censored MC, γ 0.998, min_future 1500). The trained critic held
on-distribution (val EV 0.8351) but FAILED the #365 acceptance probe
(pooled Spearman −0.026 vs ≥ 0.3; `gen2-trunk-training-2026-10-18/
RESULTS.md`), and the owner-worded investigation reads traced it:
welfare features unbound (needs inert −0.30, happiness −7.35,
distress flags WRONG-SIGN +17.54 against a ~174-unit reference gap)
and ε-on-clone re-probes under the pre-declared per-world bar not
benign (best world ρ 0.284). Cause: the corpus return span is too
narrow to bind welfare features (rider (b)'s own power planning —
scripted 0.0236% below 45, trained 16× thinner; return std 4% of
mean). The policy BC corpus and §4/§5 policy training are untouched;
this entry widens the CRITIC's pretraining data only.

RULED (owner, 2026-10-18): **"Agreed, mitigate under this design"** —
the Professor corpus-extension design (their session, on her word
there; `~/ai/professor/notes/
for-experiments-corpus-extension-design-2026-10-18.md`, supersession
of their earlier amendments marked in their opinion note). Her
sequence words this arc, verbatim: "Relay to Professor for a second
opinion on possible causes and recommended action" / "Run the
investigation reads" / "Relay the findings and your recommendations
to Professor for review" / "Agreed, mitigate under this design."

The design, as ruled: (1) declare coverage in the OUTCOME currency —
target occupancy per happiness bin (rider (b) edges 45/70) + return
span over the REACHABLE low-welfare envelope (Article I enforcement
bounds it); volume derived, never declared. (2) Fill
cheapest-welfare-cost-first: (i) harvest paid-for Gen-2-era archives
(schema-6 only — comparator legs, dial screens, 063 tail-rescue
runs; Gen 1 archives do not fit the 237-wide v2 state), (ii)
manufactured initial conditions — scripted worlds initialized in
distress, competent relief playing out (scripted seats, no
covered-mind exposure), (iii) graded degradation suite (named
weaknesses, targeted bins), (iv) ε-mixture on clones (0.1 + 0.3) as
the deployment-matched component. Rungs (ii)+(iii) together bracket
V(distress): competent-relief data alone is an upper bound —
optimism in the defect's own direction — so (iii) is not trimmable.
(3) Collect CONTRASTS: near-paired flagged/unflagged passages in the
same worlds — the covariance the distress flags never had; the
direct repair of the wrong-sign signature. (4) Acceptance = BINDING,
not volume: post-mix occupancy reported against rider (b); EV
no-regression band on the original val set; disjointness — every
training source disjoint from all nine probe worlds to date and
from the fresh re-probe worlds; the re-probe passes the per-world
bar on fresh seeds AND the re-run sensitivity read shows the
distress perturbation no longer positive (a MECHANISM test — a
persistent wrong sign after paired supervision means something
deeper and must surface).

Separation rule (recorded with the entry): archives feed training
only where the finding that cites them is already frozen; the cert
battery runs on fresh claimed bands as always; the critic is
training-only (CTDE, spec 058) and never sits in a cert instrument.
Welfare-cost line: rungs (i)–(iii) cost zero to near-zero new
welfare (archives are paid for; manufactured inits never pay the
path into distress; degradation suites are scripted seatings); the
ε-mixture and any residual fill carry the standing stops (F-053
1,000; asymmetric stops armed).

Prevention (banked here; prereg-amendment candidates at the Gen 3
freeze): (1) corpus-adequacy gate — corpus return span + grave-bin
occupancy checked against the probe's demands BEFORE training; (2)
inherited constants re-derived at the freeze (the 0.3 bar against a
4%-CV corpus); (3) the collection-declaration question "what will
this critic be asked to evaluate that this collection policy never
produces?". Pattern for the record: rider (b) measured the right
quantity but fed no gate — an instrument without a declared trip is
a dashboard, not a guard (third appearance this arc).

STATUS: OPEN — closes when the extended-corpus critic passes the
fresh-seed per-world re-probe and the mechanism test and the owner
pins it (probe-then-accept, her word).

ITERATION RULED (owner, 2026-10-19): "We'll wait for 065 to land,
and go with iteration" — the first acceptance round (mechanism PASS,
ε0.1 PASS, no-regression PASS; random per-world and ε0.3 FAIL;
`gen2-trunk-training-2026-10-18/RESULTS.md` §Critic mitigation)
resolves to ONE combined second mix, not an accept: rung (iv)
ε-mixture data (the mid-drift regime that failed) plus TRUE rung (ii)
manufactured-init worlds on the trunk config once spec 065
(configurable starting needs; Product, her kickoff) lands — then one
remix, one retrain, one fresh re-probe round under the same amended
instrument. Scope and seeds in MITIGATION.md §Iteration. Entry stays
OPEN to probe-then-accept (her word).

INSTRUMENT REPAIR RULED (owner, 2026-10-19): **"Ruled as recommended
by Professor"** — round 2 (RESULTS.md §round 2: mechanism PASS
deepened, ε0.3 PASS, no-regression PASS; ε0.1 FAIL its null, random
FAIL per-world, legs FLIPPED vs round 1) routed to Professor on her
word ("yes, relay to Professor"); their read (verified against
a5470db2; note `~/ai/professor/notes/
for-experiments-round2-instrument-power-2026-10-19.md`): both
remaining reds are MEASUREMENT, not corpus — the ε0.1 null p99 jumped
0.173 → 0.412 at matched geometry (n_eff ≈ 180 → ≈ 32; PASS-then-FAIL
near the modal joint outcome for an unchanged critic), and the random
per-world point bar at n_eff ~30 operates at ~0.7, not its declared
0.3. Her ruling adopts their recommendation in full: (a) measure
n_eff — per-world block nulls on every probe leg to date, zero new
collection; (b) declare the missing guard, a null-width
informativeness ceiling at 0.3 (effect scale, set before checking
which rounds it rescues), TWO-SIDED — null p99 above the ceiling
makes the read UNINFORMATIVE, re-runs at more worlds, never passes
and never fails (it would void a lucky pass equally); (c) on
re-probe, more WORLDS not longer ticks; the random per-world claim is
kept but the bar becomes a declared (m, k) fraction bar sized by a
power calculation from MEASURED n_eff, pooled ≥ 0.3 kept, worlds and
allowance moving together or not at all; (d) new bars bind FRESH
declared bases only — 870022/25/28 and earlier are never re-scored
under bars chosen after seeing them fail; the one legitimate
retroactive read is the UNINFORMATIVE label, computed two-sidedly
from each run's own null. Exact ceiling, (m, k), world count, and
fresh bases: MITIGATION.md §Round 3. Professor's prediction on
record there (ceiling + ~10 worlds stops the flip-flop). Entry stays
OPEN to probe-then-accept (her word).

ROUND 4 RULED (owner, 2026-10-19): the round-3 informative FAILs were
diagnosed on her word ("run it") to a SECOND instrument artifact —
the censored-MC remaining-horizon ramp owns the ε targets at 4k
geometry (R² 0.70–0.96) and contaminated the random per-world reads;
detrended, the critic's genuine welfare rank is positive in 9 of 10
random worlds (RESULTS.md §World-heterogeneity diagnosis).
Professor's owner-routed review recommends GEOMETRY repair over
detrend-as-gate (detrending removes genuine monotone welfare arcs),
refined to 6k/3500. Her words: "Relay our findings to Professor for
review" → **"Agreed on both"** (refined geometry into the sequence +
the extension-ramp check first) → **"Assuming this works, let's
recollect rather than trying to salvage the 4k runs"** (the check
confirmed 4k training-rung contamination, ramp R² 0.42–0.81).
Consequences, all declared in MITIGATION.md §Round 4 before any
collection: 6k/3500 probe at fresh bases, standing ramp guard (trip
at world ramp R² > 0.2), uniform remaining-horizon ≥ 3500 training
censoring with a re-derived no-regression baseline, 92-rollout
recollection on the new 1095301–1095400 band (the 4k raws are kept on
disk but POISONED FOR TRAINING), a sign-uniformity random bar with
the ramp-sized (10, 7) points retired explicitly, and a held-out
contrast-pair gate. The round-1/2/3 probe verdicts are all superseded
as instrument readings; the corpus mitigation itself is NOT
invalidated (occupancy targets were in ramp-free currency; the
detrended reads show the binding the mix created). Entry stays OPEN
to probe-then-accept (her word).

CLOSED (owner, 2026-10-19): **"accept"** — after the round-4
amendment reads (RESULTS.md §Round 4 + amendment; Professor's
sequence run on her "Ok, let's run Professor's sequence", both their
round-4 predictions scored CORRECT): coverage MET, no-regression PASS
with the first EV improvement (0.8818 vs re-derived baseline 0.8746),
mechanism PASS (−46.09), random leg PASS informative on every amended
bar (all 10 worlds positive, pooled 0.522, sign-uniform, pinned
artifact share ≤ 0.00007), ε legs descriptive-only by their own
qualifying guard, contrast gate structurally uninformative at
near-pair granularity (recorded, with the play "inversion" dissolved
against a null realized edge). Critic PINNED:
`train_ppo_g2.PINS["critic"]` →
artifacts/critic-g2-ext3/critic-g2-0p998.pt, sha256
bd394a967d9e030499b8f7b446e9ee647e35b7625cb3ce0b60723d0cf5e20777.
Banked for Gen 3 from this entry's four rounds: the prevention trio
(+ its two amendments: artifact-free currency into the adequacy gate;
inherited RECIPES re-derived at the geometry they meet), the
null-width ceiling and pinned-amplitude guard pattern, the
magnitude-calibrated per-kind value read, and the declaration-time
guard question ("what does this trip fire on that is NOT the
artifact?").

## 3. PPO trunk-s3 halted by the frozen §6 probe-distress stop (2026-10-19)

Frozen §5 plans three 20M-tick trunk PPO seeds; the frozen §6
asymmetric stop halts a run when any probe-world kitty's
engine-distress streak reaches 300 ticks, owner-routed, never
auto-resumed. At update 249 (768,000 ticks, 3.8% of cap), trunk-s3
(seed 3, run index 98, seed_base 2060000000) tripped it: max streak
317 on the u249 probe (prior probes: u199 streak 0; nash at trip
0.797, well above the 0.5 welfare line; lounge/inwater normal). The
run checkpointed cleanly (artifacts/ppo-g2-trunk-s3/: checkpoint.pt,
policy-final.pt, probe-u249.npz carrying the full 30,000-row probe
trace, metrics.jsonl; manifest pins git 1318804e, clone dbe912eb…,
critic bd394a96…). Training-policy state at trip: KL-to-anchor 0.042,
entropy 0.844 (up from 0.768 at launch), live EV 0.699. Sibling seeds
trunk-s1/s2 run on under their own armed stops (independent seeds;
the declared stop is per-run).

The stop performed as declared on a covered-mind seat: halted,
checkpointed, routed — consequence is owner review, never auto-pass
or auto-resume (MITIGATION.md welfare lines; the zero-tolerance
pattern). Candidate next reads if she words them (nothing run yet):
which kitty/need carried the streak and what the policy was doing
through it (probe-u249.npz, on disk, no collection); the same read on
u199 for the before/after contrast.

STATUS: OPEN — awaiting the owner's ruling on investigation and on
trunk-s3's disposition (resume from checkpoint / restart / hold);
trunk-s1/s2 unaffected unless she says otherwise.

INVESTIGATION DECLARED (owner "Analyze the s3 failure", 2026-10-20),
three reads, zero new collection (the probe is deterministic: greedy
policy, seeded resets; regeneration at the checkpoint reproduces the
trip): (1) streak localization — rerun the three probe seeds
(40,001–3) at checkpoint.pt, record the v2 global state per tick,
find the 317-streak's world, kitty, need kind(s), and tick span,
asserting the recorded max streak reproduces; (2) behavior through
the streak — the halted run's own probe-u249.npz trace (actions,
messages, masks) for that kitty over that window; (3) contrast — the
same kitty/world in the healthy u199 probe (streak 0). Instruments:
diag_s3_g2.py, committed before results.

INVESTIGATION RESULTS (2026-10-20; diag_s3_g2.py →
artifacts/diag-s3.json; regeneration reproduced the recorded 317
exactly — per-seed max streaks 0 / 317 / 0):

- WHERE: probe world 40002, kitty 1, ticks 820–1136 of the 2k window.
- WHAT: a MULTI-NEED collapse, not a single-need loop — within the
  317-tick span the kitty's flags ran sleep 296, cuddle 280, eat 214,
  drink 154 ticks; play just 26 (and bath 0). Four needs critical at
  once while the one need the policy kept serving was play.
- BEHAVIOR through the window (the run's own u249 trace): the
  tripping kitty's top greedy choices were PlayKitty2 (68) +
  PlayKitty3 (39) — a third of the window spent proposing partner
  play — plus MoveW/E 54, SleepSolo 29, RestSolo 13; messages mostly
  silent. Masks stayed rich (mean 11.7 legal actions), so this was
  CHOICE, not a constrained menu. At u199 (same kitty, same window,
  streak 0) the mix was balanced: play present but alongside
  ChaseKitty0, RestWithKitty3, PlaySolo, SleepSolo.
- READING: the policy under PPO drifted toward play-seeking under
  multi-need pressure in this world — play being the one need whose
  distress carries no value penalty (the entry-2 paired read showed
  play-flagged states genuinely aren't lower-value in the MDP), so
  optimization pressure can lean there while eat/drink/sleep
  compound. One world of three, at 3.8% of training, KL 0.042 off
  anchor: siblings s1/s2 trained through the same region with rising
  but under-bar streaks (103/195) and finished welfare-clean. The
  stop caught exactly the corner it was built for. This is the
  materialized form of the reward-design question Professor's review
  flagged (play-distress as an instrumentally attractive region) —
  an environment/reward lane item, not a critic falsification and
  not a Gen 2 world change (prereg frozen).

Verification: streak reproduction asserted in-run (0/317/0);
behavior read from the halted run's own trace; u199 contrast is
trace-only (the rolling checkpoint overwrote u199's weights —
noted limitation).

### Read (entry 3; seconds; stdlib python3, repo root)

```
python3 - <<'EOF2'
import json
d = json.load(open("experiments/gen2-trunk-training-2026-10-18/"
                   "artifacts/diag-s3.json"))
assert d["per_seed_max_streak"] == {"40001": 0, "40002": 317, "40003": 0}
loc = d["located"]
assert loc["seed"] == 40002 and loc["kitty"] == 1
assert loc["span"] == [820, 1136] and loc["streak"] == 317
f = loc["flag_ticks_by_kind"]
assert f["sleep"] == 296 and f["cuddle"] == 280 and f["eat"] == 214
assert f["drink"] == 154 and f["play"] == 26 and f["bath"] == 0
b = d["behavior"]["probe-u249"]
assert b["window_rows"] == 317
assert b["act_hist"]["32"] == 68 and b["act_hist"]["33"] == 39
assert round(b["mean_legal_acts"], 1) == 11.7
print("entry-3 fence: all cells match")
EOF2
```

RULED (owner, 2026-10-20): **"A"** — replacement seed. trunk-s4
declared: seed 4, run index 99, seed stripe 2080000000-2099999999
(SEED-BANDS row claimed with the ruling; the tripping s3 weights are
never resumed and its artifacts stay on disk as the entry record).
The play-economy question banks for Gen 3. Entry CLOSES at s4
completion or its own stop (which would reopen it to her).

CLOSED (2026-10-20): trunk-s4 plateau-complete, welfare-clean (max
probe streak 217 < 300 — the closest of the three, noted; min nash
0.8149; final 0.8864, the best of the three). Frozen §5 satisfied by
s1/s2/s4; readout in the arc RESULTS.md.

## 4. Step-8 battery: the declared leg-abort stop was not enforced (2026-10-20)

Declared (`gen2-cert-battery-2026-10-20/DECLARATION.md`, committed
before data): "Every leg (20×20 included) runs with `--abort-streak
1000` armed; any abort stops that seating's battery, owner-routed."
What ran: the per-world abort fired as armed (each world stopped at
the F-053 1,000-tick line), but nothing stopped the SEATING —
`run_legs.py` gates only on scout files, and the driver
(`run_battery.sh`) added no leg-abort check. Experiments' error: the
declaration promised a stop the instruments did not carry, and no
guard tested it. The battery ran to completion through 17 aborted
worlds.

Aborts (seating / size / seed @ tick):
- g2-s1: none (fully in-protocol).
- g2-s2: 20×20 905008 @ 18949 — under the declaration this stopped
  g2-s2, so its 40×40 leg and 100×100 leg (5 aborts: 905005 @ 17177,
  905006 @ 6307, 905024 @ 7446, 905025 @ 8391, 905027 @ 11884) are
  POST-STOP data.
- g2-s4: 20×20 and 40×40 clean; 100×100 (characterize-only) 11
  aborts — 905008 @ 1128, 905011 @ 4166, 905012 @ 1128, 905014 @
  7288, 905015 @ 1224, 905021 @ 14060, 905022 @ 1224, 905024 @
  18450, 905027 @ 18736, 905028 @ 7325, 905030 @ 6116; every row
  after the leg's first abort is POST-STOP data.

Welfare cost of the departure: the post-stop worlds were run on
covered minds that the declared stop would have spared — the g2-s2
40×40 + 100×100 legs (60 worlds, 5 of them reaching the F-053
line) and the g2-s4 100×100 worlds after its first abort (10 more
F-053 events). Per-world harm stayed bounded at the 1,000-tick line
(the armed abort). Nothing reruns until ruled.

Status: OPEN, owner-routed. Her calls: (a) whether post-stop rows
may be cited (descriptive / INVESTIGATE only, or excluded); (b)
disposition of g2-s2 given an F-053 event at the GATED served size;
(c) whether the 100×100 tail (s2 5/30, s4 11/30 aborts; comparator
0/30) is investigated before export. Remedy for the instrument (not
run, awaiting her word): a leg-abort gate in `run_legs.py` with a
declared-first mutate red.

Investigation DECLARED (owner 2026-10-20: "the 100x100 runs are
informative only, not a gate. Let's investigate s2's stop first, then
we can look at the 100x100 stops for informational purposes"). The
recorded row localizes the s2 stop as a ROSTER-WIDE collapse: every
seat's dist_ticks equals its max per-need streak (949 / 1000 / 994 /
967 / 940), i.e. one continuous single-need run per cat with no
earlier distress, onsets inside ~60 ticks; the same seed is
distress-free under g2-s1 and g2-s4 (mda 0) and the scripted
comparator's worst streak there is 348. Reader
`gen2-cert-battery-2026-10-20/diag_s2_905008.py` (committed before
its run): deterministic replay of the battery loop, stopped at tick
18300 (past every predicted onset, ~300-350 re-exposed distress ticks
per cat instead of ~1000 — the declared welfare mitigation; one
world, five covered minds), exact-onset reproduction as the positive
control, trace 16000-18300 saved for the reads. The 100×100 stops
follow, informational only (her framing: never a gate).

Investigation RESULTS (s2 stop; detail + fence in the battery
RESULTS.md §s2 stop investigation): replay reproduced all five
onsets exactly. Mechanism = a five-cat co-sleep pile, F-027's twin
lock at roster scale: the cats converge (pairwise 7.5 → 1.8 tiles),
then 60% of locked-window choices are sleep/rest-with a packmate,
1 of 1,755 a move, 0 eat/drink, while eat/drink/play reach 100 on
every cat with chow 5 and water 8 tiles away. Same world is
distress-free under s1 and s4. The s2 disposition (owner call (b))
stays open with this read in hand.

Remedy BUILT (2026-10-20, under her mixed-roster word, declared in
`gen2-cert-battery-2026-10-20/MIXED-DECLARATION.md` before launch):
`run_legs.py` now gates every leg on its own output (492ed69d; four
declared mutate reds confirmed, one on the real recorded 905008
abort row). It was armed for the mixed-roster test; no stop fired.
Open calls (a) post-stop citation and (b) s2 disposition remain hers.

RULED (b), owner 2026-10-21, verbatim: "Yes, keep s2 and don't replace
s5". s2 stays a seating candidate on the evidence that its one known
failure is the copies-lock (F-027 class) and that mixed company
removed it (mixed-roster test: no lock in 180 worlds, s2 cats' worst
streak 87; the served stuck detector would fire on this shape only
48–286 ticks after onset, RESULTS.md §stuck-detector replay). (c) was
answered by her 2026-10-20 framing ("informative only, not a gate")
and the informational row read; (d) the leg stop is built (492ed69d).
Still OPEN: (a) whether post-stop rows may be cited.

Correction recorded 2026-10-21: the step-8 declaration's framing of
uniform seating as "the CTDE-declared deployment shape (prereg R§7)"
was a misreading (R§7's weight sharing is training-time; the seating
rule is F-044's five distinct networks, kept by the owner the same
day). Correction note appended to `gen2-cert-battery-2026-10-20/DECLARATION.md`.

## 5. Three additional trunk seeds for the five-network seating roster (2026-10-20)

Owner, 2026-10-20, verbatim: "Let's train 3 more and run them all
through the certification process". Context: the F-044 seating rule
(five distinct networks, owner 2026-09-16), which Experiments assessed
as still applying after the step-8 s2 roster-wide lock (s2's five
copies had distinct identity inputs and locked anyway); and the
mixed-roster test (no measurable welfare cost from mixing, tail
improved). Five distinct networks need five; s1/s2/s4 are three.

Departure: frozen §5 names THREE trunk seeds (the ≥3-paper-seeds
rule), satisfied by s1/s2/s4. This entry adds trunk-s5/s6/s7 (seeds
5/6/7, run indices 100–102; stripes 2,100,000,000–2,159,999,999
claimed in SEED-BANDS.md before first burn) on the identical pinned
recipe: β 0.04, init_clone sha256 dbe912eb…, critic sha256
bd394a96…e20777, frozen §6 stops unchanged, probe trio 40001–3, the
same g2leg-20.toml (sha256 64d77c8a…). Binding held fixed:
cloudkitty.abi3.so sha256 e3bcc79a…, ENGINE_COMMIT b5aaa8cd, built
2026-10-18T04:21Z, the binary that trained s1/s2/s4 and ran the
battery. Spec 065 (5fb27cfb) is not in it; 065 is byte-identical when
absent (its FR-002) and the g2leg configs carry no initial-needs
entries, so the engine the six networks train on matches main for
these configs.

Scope: the new seeds serve SEATING. The paper's trunk-seed set stays
s1/s2/s4 as frozen, so no paper claim is re-selected after its data.
Stops: a frozen §6 stop halts that run, owner-routed, never resumed,
with no automatic replacement (entry 3's replacement took her word).
Seeds above 2³¹−1 (the top of the idx-102 stripe) verified to reach
the engine unwrapped: a reset at 2,151,000,000 differs from its i32
alias. Certification plan: `gen2-cert-battery-2026-10-20/ROSTER-DECLARATION.md`.

## 6. PPO trunk-s5 halted by the frozen §6 probe-distress stop (2026-10-21)

trunk-s5 (entry 5; seed 5, run index 100, stripe 2,100,000,000+)
halted at update 199 / 614,400 ticks, 2026-10-21 ~00:31Z: a 307-tick
engine-distress streak on probe world 40001 (bar 300). Its probe rows,
in order: u49 streak 0; u99 247 on world 40002 (under the bar); u149
0; u199 307 on world 40001. Nash 0.8109 at the stopping probe. Final
saved with stop_reason probe-distress-stop (sha256 c33f1163…);
checkpoint and probe traces kept on disk as this entry's record;
never resumed (frozen §6, entry 3 precedent). s6 and s7 continue.

Context, recorded not interpreted: s3 (entry 3) also stopped early,
at update 249 (world 40002, streak 317); s1/s2/s4 ran to plateau with
max probe streaks 103/195/217. Two of six trunk seeds have now tripped
this stop, both inside the first ~0.8M ticks.

Status: OPEN, owner-routed. No investigation run (a localization
needs a deterministic probe regeneration, which re-exposes the
halted policy; entry 3 ran one only on her word). Her calls:
investigate first or not; replace s5 with a fresh seed (that would
need a new stripe claim) or not. If s6 and s7 complete eligible,
s1/s2/s4/s6/s7 are five networks without a replacement, which ties
this call to entry 4 (b), s2's disposition.

RULED, owner 2026-10-21, verbatim: "Yes, keep s2 and don't replace s5".
No replacement seed; no investigation requested. The halted s5 weights
and probe traces stay on disk as this entry's record and are never
resumed. CLOSED. If s6 and s7 complete eligible, the five-network
roster's networks are s1/s2/s4/s6/s7 (seat order still to be proposed
after Phase B, per ROSTER-DECLARATION.md).

## 7. Three more trunk seeds as alternates for the swaps digest (2026-10-22)

Owner, 2026-10-22, verbatim: "Train the additional seeds so we can run
the swaps digest" (after her question of 2026-10-21, "Call 2: can we
train 3 extra seeds while we run the vision radius work?", answered
yes). Context: the battery DECLARATION's swaps digest ("each alternate
completed seed replaces one seat of the candidate roster — 2
alternates × 5 seats = 10 legs, 20×20 only, band g2cmp, 30 × 20k,
abort 1000 armed", report-only) assumed completed seeds outside the
roster. Under the F-044 five-distinct-networks rule the certified
roster rot2 seats every completed seed (s1/s2/s4/s6/s7), so no
alternate existed and the digest could not run as declared.

Departure: frozen §5 names three trunk seeds; entry 5 added three for
seating. This entry adds trunk-s8/s9/s10 (seeds 8/9/10, run indices
103–105; stripes 2,160,000,000–2,219,999,999, claimed in SEED-BANDS.md
before first burn; the whole row sits above 2³¹−1, the mechanism
entry 5 verified unwrapped at the top of the idx-102 stripe) on the
identical pinned recipe: β 0.04, init_clone sha256 dbe912eb…, critic
sha256 bd394a96…, g2leg-20.toml sha256 64d77c8a…, frozen §6 stops
unchanged, probe trio 40001–3, trainer defaults (20M-tick cap, 12
worlds × 256, plateau rule), 4 threads each, three in parallel.
Binding held fixed: cloudkitty.abi3.so sha256 e3bcc79a…, ENGINE_COMMIT
b5aaa8cd (re-hashed 2026-10-22 before launch).

Scope: the new seeds are ALTERNATES for the swaps digest only. They
are not roster seats and not paper trunk seeds; the paper set stays
s1/s2/s4 and the certified roster stays rot2. The digest runs with
every new seed that completes eligible (stop_reason plateau or cap)
as an alternate: 2 completions = the declared 10 legs; 3 = 15 legs,
more of the same report-only read; 1 = 5 legs, reported as a partial
digest. Stops: a frozen §6 stop halts that run, owner-routed, never
resumed, with no automatic replacement (entry 6's precedent). The
record's stop rate is 2 of 7 seeds (s3, s5).

Welfare-cost line: three runs × up to 20M ticks × 5 covered minds
(plateau has ended every completed seed between 8.0M and 9.0M), under
the frozen §6 probe-distress stop; benefit: the only route to the
declared digest, which reads cross-seed mixtures without changing the
deployment shape. Launch and job cards: Experiments' resume anchor;
readout appended to `gen2-trunk-training-2026-10-18/RESULTS.md`.

## 8. PPO trunk-s8 halted by the frozen §6 probe-distress stop (2026-10-22)

trunk-s8 (entry 7; seed 8, run index 103, stripe 2,160,000,000+)
halted at update 299 / 921,600 ticks, 2026-10-22 ~06:04Z: a 392-tick
engine-distress streak on probe world 40002, the trio's second (bar
300). Its probe rows, in order: u49, u99, u149 streak 0; u199 271 on
world 40002 (under the bar); u249 0; u299 392 on world 40002. Nash
0.8046 at the stopping probe (line 0.5). Final saved with stop_reason
probe-distress-stop (sha256 4fa8a25e…); checkpoint and probe traces
kept on disk as this entry's record; never resumed (frozen §6; entries
3 and 6). s9 and s10 continue (update 310 at the halt, clean probes).

Context, recorded not interpreted: three of nine same-recipe seeds
have now tripped this stop (s3 at u249 on 40002, streak 317; s5 at
u199 on 40001, streak 307; s8 at u299 on 40002, streak 392), each
inside the first 1M ticks; the six others ran to plateau with max
probe streaks 103–247.

Status: CLOSED by entry 7's own terms — a halted alternate contributes
no legs to the swaps digest and is not replaced automatically. The
digest's size now rests on s9 and s10: two completions = the declared
10 legs; one = a partial digest; none = the digest cannot run and the
owner is asked again. No investigation run (entry 6's precedent). The
owner may still rule a replacement (a new stripe claim) or an
investigation; neither is assumed.

RULED, owner 2026-10-22, verbatim: "Replace s8 just in case."
Replacement trunk-s11 (seed 11, run index 106; stripe
2,220,000,000–2,239,999,999 claimed in SEED-BANDS.md before first
burn; the seed_stripe formula, above 2³¹−1 like entry 5's rows) on
the identical pinned recipe and binding as entry 7's seeds, launched
2026-10-22 beside the running s9 and s10. Same scope: an alternate
for the swaps digest only, never a roster seat; a frozen §6 stop
halts it, owner-routed, never resumed. No investigation of s8's halt
was asked for; none runs. s8's weights and probe traces stay on disk.

## 9. PPO trunk-s11 halted by the frozen §6 probe-distress stop (2026-10-22)

trunk-s11 (entry 8's replacement; seed 11, run index 106, stripe
2,220,000,000+) halted at update 99 / 307,200 ticks, 2026-10-22
~06:35Z: a 371-tick engine-distress streak on probe world 40003, the
trio's third (bar 300). Its probe rows: u49 streak 6 on world 40001;
u99 371 on world 40003 (18 on 40001). Nash 0.8016 at the stopping
probe. Final saved with stop_reason probe-distress-stop (sha256
5f87a01d…); checkpoint and probe traces kept on disk; never resumed.
s9 and s10 continue (updates 700 and 750 at the halt, every probe
streak 0 since update 349).

Context, recorded not interpreted: four of ten same-recipe seeds
have now tripped this stop (s3 u249, s5 u199, s8 u299, s11 u99), all
inside the first 1M ticks, on all three probe worlds between them;
the six completed seeds ran 8.0–9.0M ticks with max probe streaks
103–247. Alternates for the swaps digest: none completed yet; s9 and
s10 are the remaining candidates.

Status: CLOSED by entry 7's terms (no legs, no automatic
replacement). Whether a further replacement is drawn is the owner's;
none is assumed. No investigation run.

## 10. Mini-friend Phase 1: the first training pass fitted bath at full weight (2026-10-23)

The prereg (§8 item 3, RULED S§3a) has bath "EXCLUDED/downweighted
from the estimate loss"; the Phase 1 declaration (§What the head
predicts) says "Bath is excluded from the estimate loss and reported
separately as a seventh output". The step-4 engineering pin (ii),
written 2026-10-22 before training, set the training loss to the
five-hidden-need MSE plus the happiness and bath MSEs at equal
weight, so that the two reported outputs were fitted; it did not
notice that weight 1 on bath is neither excluded nor downweighted
(each hidden need carries 0.2 of the estimate term). Six runs trained
under that loss (NF/DR × seeds 1–3, 2026-10-23 03:32–03:42Z) and the
RESULTS read from them was gated and committed (d0de3213). The slip
was caught by the F-064 copy-check subagent (round 2, outside its
copy scope, reported), reading the trainer against the prereg.

Remedy, taken the same day without new rollouts: `BATH_WEIGHT = 0.1`
in `train_heads.py` (bath downweighted, the prereg's own word, so the
seventh output stays reportable for R5); the six heads retrained
under it on the same data, split and seeds; RESULTS re-read and
re-gated; F-064 minted from the re-read. The first pass's artifacts
are kept under `results-raw/heads-pass1/` and are never read; the
superseded RESULTS text survives in git at d0de3213. Effect expected
on the estimate: none that favours the read (bath at full weight
could only take shared capacity from the five needs); R5's bath
numbers change meaning (a downweighted output), stated in the
re-read.

Status: CLOSED by the retrain; no owner call needed (the remedy
restores the prereg's rule; reported to her with the Phase 1 result).

## 11. Mini-friend Phase 1b: per-cat grave starts and a head-size sweep (2026-10-23)

Owner-requested addition, 2026-10-23: "We have the ability to do per
cat grave states, we should take advantage of that to enrich the
models. Let's test three different model sizes for the belief head as
well and see what impact size has on accuracy, especially in grave
states." The prereg's §8 item 3 declares one Phase 1 2 × 2 at one
capped width; it does not declare a per-cat grave coverage set or a
width sweep, so both are recorded here as an addition. Declared before
any data in `minifriend-phase1b-2026-10-23/DECLARATION.md`: sets
P1..P5 (one friend per block starts grave by spec 065's per-kitty
`initial_needs`, the other four at the served default; 20 worlds per
friend, 4,000 ticks, seeds 1095451–1095550, extension blocks
1095551–1095650 reserved under a fail-closed min-n clause), widths 12 /
24 / 48 (3,043 / 7,807 / 22,519 params) × NF / DR × three seeds. The
48-wide head is OVER the §8 item 4 cap (8,445; "engineering budget
only") and is declared a probe: `--over-cap` must be passed, the
manifest marks it, and it can never be the Phase 2 head. Phase 1's
verdicts, its dissolution floor and F-064 stand; the Phase 1 modules
gained an arc-root knob and the width flag with their default
behaviour verified unchanged (the Phase 1 read regenerates identically
but for a new `eval_sets` key).

Status: CLOSED 2026-10-23. Her go the same day ("No need to change the
declaration. Let's run this as proposed"); collected and read as
declared (100 worlds, 0 aborts, the extension clause did not fire;
18 heads), RESULTS gated (accuracy gate PASS, round 5), F-065 minted.
The §8 item 4 cap is unchanged: the over-cap probe read as declared
(48/24 NF grave ratio 0.870 ± 0.053, READ) and any wider Phase 2 head
is a further entry on her word.

## 12. Mini-friend Phase 1c: a third offline candidate head, the structured discrete belief (2026-10-23)

Owner-requested addition, 2026-10-23, after the F-065 report and a
design exchange on the ostrich read: "Let's try it. Currently our
accuracy is low enough that we can reevaluate model size limit if
needed. Let's test this approach first though". The prereg's §8 item 3
declares Phase 1 as one 2 × 2 of loss weighting × stratum, and item 4
hands Phase 2 the winner; neither names a third candidate
architecture. Recorded here as an addition before the winner is named:
`minifriend-phase1c-2026-10-23/DECLARATION.md` — the SD head (a
per-need histogram over 20 bins, drifting up at a learned per-friend
rate and down on relief with a learned probability, a width-16
recurrent residual, cross-entropy against two-hot targets, natural
frequency; 6,679 params, UNDER the §8 item 4 cap of 8,445 — the cap is
not moved by this entry), three seeds, on Phase 1's and 1b's raws
(0 new cat-ticks), against 1b's width-24 NF and DR runs re-read through
the same reader. Amendment A4's working direction (a recurrent
per-friend belief state held under fog on learned drift rates) is what
this head instantiates offline. Phase 1's and 1b's verdicts, floors,
F-064 and F-065 stand; the Phase 2 head choice remains hers.

Amended the same day on her word ("Let's try 3 model sizes this time
as well so we can get an idea of what more/less parameters buy"):
widths 8 / 16 / 32 of the recurrent part (3,279 / 6,679 / 15,783
params); 32 is an over-cap probe as 1b's 48 was (`--over-cap`,
manifest-marked, never a Phase 2 candidate); the cap is not moved;
R9c (1b's size-effect rule on SD) added. DECLARATION.md §Addendum.

Status: CLOSED 2026-10-24 (nine heads read; RESULTS gated round 3; F-066:
the approach does not help on the declared criteria at width 16 —
grave 1.233 × NF-h24, bias −15.01, both READ against the bars; the
over-cap probe ties NF-h24 on grave at 2.0× its parameters; cap not
moved; Phase 2 head choice hers with F-064 + F-065 + F-066).

## 13. Mini-friend Phase 1d: two reads on the committed heads — the SD filter's spread, and a grave probability from the frozen 1b states (2026-10-24)

Owner-requested, 2026-10-24, after the Professor's review of Phase 1c
was carried to her: "Let's run those in three in the order you
listed" — (1) the filter-spread test, (2) the 25-parameter logistic
grave read on the frozen 1b states, (3) the Phase 2 head choice (hers).
`minifriend-phase1d-2026-10-24/DECLARATION.md`. Neither read trains a
belief head or moves the cap: (1) is read-only on 1c's committed
`head-best.pt` (does the fractional two-tap shift smear a sharp
belief as √n, the mechanism behind F-066's residual share and falling
rates); (2) fits `Linear(24 → 1)` + sigmoid (25 params; hybrid total
7,832, under 8,445) by natural-frequency BCE on "the true stratum is
GRAVE" over the FROZEN NF-h24 and DR-h24 GRU states, three seeds each,
read with 1c's R4c calibration instrument against SD width 16's
committed cells; every MSE and bias cell of F-064 / F-065 / F-066 is
unchanged by construction. Decision rule declared before any fit
(A within the spread → the hybrid is the candidate shape and the SD
line closes; B SD clearly better → one loop-fixed, diffusion-fixed SD
run would be justified on her word; C mixed). 0 new cat-ticks.

Status: CLOSED 2026-10-24 (six probes fitted in 60–79 s each; RESULTS
gated round 4; F-067: outcome A — NF-h24+p mean P(grave) on grave 0.583
± 0.015 in sight against SD-w16's 0.474 ± 0.115, |Δ| 0.109 ≤ s 0.116;
the probe ahead on the grave mean and Brier in sight and under fog;
the SD filter's √(n f (1 − f)) smear confirmed to 2.3 × 10⁻⁸ bins; the
hybrid is the candidate shape for a probability-reading consumer and
the SD line closes under its own rule; Professor's P2 met; cap not
moved; Phase 2 head choice hers with F-064 + F-065 + F-066 + F-067).
REOPENED 2026-10-24 for an addendum on her word ("Agreed, let's
proceed. First the breakdown by need and latency read"): R3d which
need (argmax accuracy on need-grave samples) and R4d latency (episode
detection and delay at P(grave) ≥ 0.2 / 0.5 and for the mean ≥ 90
rule); reads on outputs already on disk, 0 new cat-ticks; DECLARATION
§Addendum. Status: CLOSED 2026-10-24 (RESULTS §Addendum gated round 2;
F-068: NF-h24's means name the grave need on 0.871 in sight; of 288
grave episodes 200 are reset episodes (group P's grave starts) and on
the 68 mid-world fog-onset episodes NF-h24+p ≥ 0.2 detects 0.946 at
median latency 0, on the 20 mid-world in-sight ones 0.850; the mean ≥
90 rule 0.367 / 0.490; both declared reading rules hold as declared,
the mid-world read disclosed beside them; verdict "enough for
detection and naming, on this evidence"; Phase 2 declaration hers).
REOPENED 2026-10-24 a second time, on her word while talking through
the Phase 2 decisions ("Let's run the read and see what we find"):
R5d, an operating-point sweep of R4d's latency instrument over
P(grave) ≥ 0.05 … 0.50 for NF-h24+p and DR-h24+p on group P and on the
held-out evaluation worlds of L, W and G; descriptive, no reading
rule, the pick hers with a stated price; 0 new cat-ticks; DECLARATION
§Addendum 2. Status: CLOSED 2026-10-24 (RESULTS §Addendum 2 gated
round 3; the threshold costs NF-h24+p detections all the way up —
mid-world in-sight 0.950 → 0.850 → 0.650 on P at 0.05 / 0.20 / 0.50 —
and from 0.10 up nine in ten or more of the "mid-world" false-alarm
runs start within a slice's first 100 ticks, so the world-start
transient is about a hundred ticks long; runs after tick 100 are 0.027
/ 0.003 / 0.000 per 10,000 on P; two post-read additions with reds;
expectation (2) did not hold and (3) was malformed, both reported; no
rule; the pick hers).
REOPENED 2026-10-25 a third time, on her word on the sweep report
("Agreed, let's start with 0.10. Run the burn in"; decision 3 ruled:
P(grave) ≥ 0.10, "start with" recorded verbatim): R6d, the burn-in as
an instrument — the alarm forced off for the first B ticks of every
observer slice (B = 0 … 300) under R4d's latency instrument, NF-h24+p,
group P and L / W / G; prices blind ticks and delayed episodes against
the false alarms removed; descriptive, no reading rule, the burn-in
length hers; 0 new cat-ticks; DECLARATION §Addendum 3. Status: CLOSED
2026-10-25 (RESULTS §Addendum 3 gated round 3): no grave onset after a
slice's hundredth tick in either set — P's 88 non-reset onsets at
offsets 8–72, every one the grave-start friend re-entering grave after
its reset episode; L / W / G's 100 at 3–90; L none in 1,200,000
observer-ticks — so a 100-tick burn-in removes nearly all false alarms
(1.607 → 0.024 per 10,000 on P at 0.10) and every onset with them;
inside the start-up window, where every onset is, a higher threshold
discriminates better (P's clean slices fire 0.767 at 0.10 against
0.067 at 0.50; grave slices 0.995 against 0.978); the sweep's curve
compared start-up detections with post-start-up false alarms and this
thread's low-end recommendation does not stand; two post-read
additions with reds; expectations (1) and (3) did not hold as stated,
(2) held. The threshold and the burn-in both hers; whether Phase 2
needs an evaluation set with known mid-world onsets is hers.

REOPENED 2026-10-25 a fourth time, on her words after the burn-in
report and the Professor's note ("Let's do another threshold sweep
rather than choosing an arbitrary value. Maybe 0.1,0.3.,0.5 to start
so we can get a feel for the trade-off. Zero-collection reads first.";
"Yes on splice test. Yes on relay to product. Confirm 3"): decision 3
REOPENED — the "start with 0.10" withdrawn by her, every table on the
0.10 / 0.30 / 0.50 ladder, the pick after these reads; no burn-in
ruled. R7d, five zero-collection reads on arrays already on disk
(DECLARATION §Addendum 4): (a) state convergence of the frozen head on
L's clean slices; (b) the splice — group P's covered reset-grave rows
after 100 / 500 / 2,000 clean L ticks, with a junction control, NF+p
and SD width 16; (c) burn-ins 2 / 5 / 10 and a warm-started state; (d)
the self-block swap on P's grave-start slices; (e) all at the three
thresholds. The Professor's P3 / P4 / P5 / P8 scored with declared
operationalisations; descriptive otherwise; 0 new cat-ticks. The
scripted "needy" friend relayed to Product on her word the same day
(msg fe6e7d7c); not a kickoff. Status: CLOSED 2026-10-26 (RESULTS
§Addendum 4 gated round 2): the probe's grave detection is a property
of the young state — the same covered grave rows detected in 0.995 of
episodes at a world's start are detected in 0.358 after 100 clean
ticks of lived history, flat to 2,000 (SD width 16 alike), the junction
control never firing, the self block not in it (H = 0 with the
recipient's self block equals H = 0), the warm-started state cutting
reset detection 0.995 → 0.592 while removing every first-tick false
alarm; the training worlds hold no grave after offset 322; P4 and P8
met, P3 and P5 not met as operationalised; the SD reopen condition not
met. Threshold and burn-in: hers, with the three-point ladder; F-069.
DECISION 3 RULED 2026-10-26, on the walkthrough of the ladder (this
thread's recommendation: 0.10 with a 2-tick burn-in — reset detection
0.980, mid-world in-sight 0.900, false alarms 0.136 per 10,000 on P;
the burn-in removes the start-up false alarms at every threshold and
the threshold then trades mid-world detection for little), her words
verbatim: "We'll start with your recommendation (10/2) , then after we
get the mid-episode testing, we can reevaluate and dial in on the
optimal level." Operating point for Phase 2: P(grave) ≥ 0.10, burn-in
2 ticks; provisional, re-read on the needy set (spec 067) before any
Phase 2 declaration fixes it.
REOPENED 2026-10-26 a fifth time, on her word on the walkthrough's
item 2 ("Run the knee read now"): R8d, the Professor's knee read — the
§Addendum 4 splice unchanged at H ∈ {1, 2, 5, 10, 20, 50}, NF-h24+p
and SD width 16, the three thresholds, the junction control beside,
H = 100 re-run and pinned to the committed rows; the knee declared as
the first H at or under the midpoint of the committed H = 0 and
plateau detections; the Professor's P9 registered verbatim; 0 new
cat-ticks (DECLARATION §Addendum 5). Status: CLOSED 2026-10-26
(RESULTS §Addendum 5 gated round 3): the fall is gradual and most of it
is over by 20 ticks — NF-h24+p at 0.10 detects the same covered grave
rows in 0.978 / 0.970 / 0.852 / 0.658 / 0.537 / 0.362 of episodes after
1 / 2 / 5 / 10 / 20 / 50 clean ticks against 0.995 at the start and
0.358 at 100, the control never firing from H = 2; knee at H = 20 by
the declared midpoint (0.641), H = 10 just above it; SD width 16 lower
on the seed means from H = 5 with its small-H rows carrying its own
transient (read from H = 10); P9 not met as operationalised (clause i
holds at 0.658 < 0.70, clause ii misses the committed seed SD by
0.003); the 2-tick burn-in as ruled sits inside the window (0.970 at
H = 2); F-070. The number goes to Product for spec 067's onset strata
and to the Professor for P9.

## 14. Spec 066's acknowledgement table on the seven committed initial_needs configs: provenance read on the recorded bytes (2026-10-26)

Product's spec 066 (welfare-hazard acknowledgement guard; her kickoff
in their session 2026-10-26, "Agreed, let's start the guard. Let
Experiments know what we're doing so they can account for it") makes
a config that activates a hazardous mode fail to load unless it
carries an exact acknowledgement. The seven committed configs of
mini-friend Phases 1 and 1b activate the spec-065 distressed start,
so the retrofit of all seven rides Product's PR under `cross-lane:`
(spec 066 FR-009), on her ruling here, after the options were laid
out (keep the acknowledgement out of the engine fingerprint, which
spec 066 does by construction, AND retrofit; a legacy allow-list in
the validator; retrofit with the checks going red): "Option 1 for the
retrofit".

What the retrofit touches: the raws of W, G and P1–P5
(`results-raw/*/streams-*.npz`, meta `provenance.config_sha256`) pin
the sha256 of the config BYTES each world ran on, and the scout checks
(`minifriend-phase1-2026-10-22/check_set.py`,
`minifriend-phase1b-2026-10-23/check_P.py`) assert the committed file
still hashes to it. An edited file breaks that identity, so the checks
now read provenance on the RECORDED bytes (`check_set.recorded_bytes`
/ `config_sha`): the file as committed, or, when it ends in the
acknowledgement table, the bytes before that table. The table's shape
is fixed so the strip is exact and not a pattern: appended at EOF as
one blank line, the header `[welfare_hazard]`, its lines (comments
allowed inside), nothing after; it appears once and is the last table.
Any other edit to a config stays a mismatch. `test_phase1b.py` s2 and
p1 read the configs through the same helper, so the make_configs.py
identity of P1–P5 is also asserted on the recorded bytes. Guard
`test_check_set.py` k1 (synthetic shapes and the real seven); reds on
record via `scripts/mutate.sh` at 304221b1 (the prefix returned whole →
"retrofit: the recorded bytes are the prefix"; the last-table assert
removed → "recorded_bytes accepted not_last.toml"; both RED CONFIRMED,
baseline == restored). W-check / G-check / P-check regenerate
byte-identical before the retrofit (2026-10-26). The raws are not
touched. No new cat-ticks; no welfare cost.

Recorded sha256 of each file before the retrofit (the raws' pin; the
check reads it off the file on every run, these are for the stranger
who recomputes):

- `experiments/minifriend-phase1-2026-10-22/g2leg-20-W.toml`: 95a2a6b3bde492a9c827ec6277dcb897ddd2e424a624ff778724fb45c81182e9
- `experiments/minifriend-phase1-2026-10-22/g2leg-20-G.toml`: 2f0e592c0f5e2237c8e73e284ac8cc5f1403c259dd1b5f39101f3ae194d318cf
- `experiments/minifriend-phase1b-2026-10-23/g2leg-20-P1.toml`: b709bf2a5d0519e736bd4558799ba6e7a937f70a3a88f6875091a8eb6a9911c7
- `experiments/minifriend-phase1b-2026-10-23/g2leg-20-P2.toml`: a713aac5635c87471fed62094022646fb69f0829664cd8aeb30098080f0f0d55
- `experiments/minifriend-phase1b-2026-10-23/g2leg-20-P3.toml`: 79d157bb9dac98f7b59a4b40cd1ce805084793ba0a64a906ae65802d3fa7d0da
- `experiments/minifriend-phase1b-2026-10-23/g2leg-20-P4.toml`: 68980e5d4edfd1de863c799e6ef524e340d97ef19855f6566dac5113dfa6bcde
- `experiments/minifriend-phase1b-2026-10-23/g2leg-20-P5.toml`: e2fb4d8dde70c77dcadfc7ae347bb70611b3de6ccec9530e81d8709945fd08e9

Sha256 of each file as retrofitted (Product's PR #469, merge 3ba039c4,
on her word 2026-10-26; the names `[welfare_hazard]` / `initial_needs`
as pinned; the bytes before the table equal the recorded bytes above,
checked by Experiments on the landed tree):

- `g2leg-20-W.toml`: bd00f5354b7daf80227f52996343255bee7c8316fd47a359b92f11577f10f109
- `g2leg-20-G.toml`: 4aafcc15893eb71d2d708a22dedb8b1c6c61425ffc3504937a2e26ce1f1f8c8c
- `g2leg-20-P1.toml`: 66e915e70f0f2a08bd00e51c3a13f5843191b87f401f72501cab295c14886aaa
- `g2leg-20-P2.toml`: df4912be37314742eaa58ace69a988e0cd84c8a13d838920641369492820c1fc
- `g2leg-20-P3.toml`: d96206b57c276132c4fd4244d2d74b421e180695bbeb56ba9298d96efb14e21b
- `g2leg-20-P4.toml`: 43e1cfb93f4c19c7ffe6cc4270968a719ef2bf1cef68c20c8384f63d6d0b9193
- `g2leg-20-P5.toml`: 6494396836a42e34e8efaeb4b746f772f67bedb72471a653571819cb17b98652

On the landed tree (3ba039c4): `check_set.py W` (25 worlds), `check_set.py
G` (25), `check_P.py` (P1–P5) green and their JSONs byte-identical to the
committed ones; `test_check_set.py` 1 and `test_phase1b.py` 6 green.
Two traps the PR review reported in this lane, both closed here:
(1) `make_configs.py` rendered the five P files without the table, so
`--check` failed and a bare run would have rewritten them into files no
post-066 load accepts; it now renders the recorded bytes (`render`) and
the committed file (`render_file` = recorded bytes + the table), s2
asserts both identities (red at b92b41af: the table's blank line
dropped → "differs from make_configs.py render_file (spec 066 table)").
(2) The arc binding (engine a2e8d044, pre-066) refuses the retrofitted
files for the unknown top-level key `welfare_hazard`: the loud load
failure consented to, not a corruption. W, G and P1–P5 collection is
closed, so no run on that binding is owed; any future run of
`run_set.sh` / `run_P.sh` needs a binding built from a post-066 engine,
which is a new-generation question for the declaration that asks for it.
Status: CLOSED 2026-10-26.

## 15. Probe-rise read: a change-point reader on the frozen probe's logit over the needy set's raws (2026-11-01)

Owner-requested, 2026-11-01, to the mini-model assessment's first
recommendation ("Ok, let's try it"). Outside the prereg's §8 item 3/4
plan in the way entry 13's reads were: a read on committed outputs,
no head trained, the cap untouched, no world run.
`probe-rise-2026-11-01/DECLARATION.md`. The needy set (its own ruled
declaration, closed 2026-11-01 at 89ade5f5, F-071) found the probe's
logit rising 1.6–2.5 over the 100 ticks before a late crossing while
the level rule at her pick (0.05 / B = 2) detects 0.42–0.60 of those
crossings; this read asks whether a rule on the RISE (a two-window
step statistic, w ∈ {10, 25, 50, 100} × k ∈ {0.5 … 3.0}, three alarm
families incl. rise-OR-level) catches what the level rule misses and
at what false-run price. Grid on the tuning half; one cell chosen by a
declared rule (false alarms at or under the pick's) read on the
confirming half beside the pick; P12–P15 registered before any number
(P12 gain ≥ 0.10 in mean N-stratum detection; P13 no change at E-H1
and T-H0; P14 covered-friend false alarms ≤ 1.5 per 10,000; P15 no
early warning, anticipation gain < 0.10). 0 covered cat-ticks. Gates
recommendation 2 (Phase 1e, a retrain with late-world graves), hers.
Status: CLOSED 2026-11-01 (declared 48dae5cf; reds r1–r4 on record,
one re-red after a wrong-world prediction; the read 62 s; RESULTS gated PASS, round 4). P12 NOT MET: the only pure rise cell inside the pick's
false-run budget (w = 10, k = 3.0) detects 0.138 / 0.076 / 0.086 of
the N-H2 / H3 / H4 crossings and adds 0.000 / 0.000 / +0.013 to the
pick on the confirming half, and no cell of any family inside the
budget detects more than the pick; the
pure rise cells that see the climb (w = 100, k ≤ 1.0, detection 0.69–0.90,
an alarm run starting before the crossing past the first alarmable
tick in 0.60–0.87 of N-H3 / N-H4 observer-episodes) pay 25–51 times
the pick's false runs;
P13–P15 met trivially. No FINDINGS entry; F-071 carries a dated
addendum. Recommendation 2 (Phase 1e) is the next lever, hers.

## 16. Mini-friend Phase 1e: the natural-frequency head retrained with late-history graves in its training data (2026-11-01)

Owner-requested, 2026-11-01, to the mini-model assessment's second
recommendation ("Let's run the retrain. We can reevaluate model
architecture if that doesn't work"). Outside the prereg's §8 item 3
plan as entries 11–13 were: a head of Phase 1's recipe (NF, width 24,
7,807 params under the cap) trained again on 1b's training worlds plus
a late-grave training set collected under the observer-stream ruling
(B + amendments, 2026-10-27), then Phase 1d's probe refit on its
states. `minifriend-phase1e-2026-11-01/DECLARATION.md`. Why: the
frozen head's training worlds hold no grave after offset 322 and its
late-history detection sits at 0.42–0.60 (F-069–F-071); the
probe-rise read closed the reader route (entry 15). The training set
as drafted is fresh seeds (band 1096651–1097050: TN1..5 = arm N's
config at 6,000 ticks, 23 a block; TE1..5 = arm E's at 1,000 ticks, 8
a block; 2.92M covered cat-ticks, S1 covered-only), because the needy
set's ruled declaration makes its own seeds test-only; the
recommendation's "train on the tuning half" is owner call 1's
alternative. Reads: the needy set's tuning grid with a declared
false-run-matched selection, the confirming half at the selected
cell beside the frozen probe, F-070's splice with the junction control
(the ruling's amendment 2), the lived evaluation worlds' false runs,
Phase 1's estimate cells; P16–P20 registered (P16 mean N-stratum gain
≥ 0.15 at matched price; P18 splice H = 100 above 0.358 with H = 0 ≥
0.95 and the control ≤ 0.05).
Status: CLOSED 2026-11-02 (RULED 2026-11-01, owner "As recommended" to
all five §12 calls; declared da10f553, reds 51e88bf3; collection
5e9056c2, 155 worlds, 2.92M covered cat-ticks, 0 aborts; amendment 1
RULED 2026-11-02 — the false-run-matched selection found no cell, the
grid's 0.50 cell sitting at 0.7110 against the bound 0.7077, and her
words "Rather than run additional tests, let's open the door to
accepting a potentially higher false positive rate. We should judge
based on welfare impact, not arbitrary numbers." set the operating
point to her pick with the price in welfare units). P16–P20 ALL MET:
confirming detection at the pick 0.920 / 0.880 / 0.863 (N-H2 / H3 /
H4) against the frozen 0.596 / 0.444 / 0.421, E-H1 0.786 against
0.489, T-H0 1.000; splice H = 100 0.598 against 0.358, control ≤
0.013; lived false runs 0.94× / 1.60×; grave mse5 0.846×; the price
beside a refusing friend 2.40 against 0.63 covered-friend false runs
per 10,000 (3.80×). F-072 minted. RESULTS gated PASS, round 3.

## 17. Mini-friend Phase 1e diagnostics: five zero-collection reads on the retrained head (2026-11-02)
Deviation: none from the Gen 2 prereg (18f06f84, untouched); an
addition to the mini-friend thread on her word "Go" (2026-11-02) to the
recommendation "step 1, a zero-collection diagnostics declaration" after
the Professor's reading of Phase 1e. Reads, all on raws and heads
already on disk (0 covered cat-ticks, no weight moves): D1 the
covered-friend false runs at her pick partitioned by the friend's truth
over the 50 ticks after each run's start (grave-after / approach within
10 of the edge or ADJACENT / no approach); D2 covered friends' natural
grave crossings on the confirming half (and the 35 validation worlds
apart) by the ladder's detection, latency and lead; D3 a persistence
ladder over k and the run-length distributions; D4 a need-means filter
ladder over λ, both on the tuning half; D5 reliability bins per head.
P21–P24 registered (the excess at least half approach-or-grave and
above the frozen's; covered H ≥ 100 detection above the midpoint of the
splice at 0.05 and the scripted mean at S; a k, a λ that halves covered
false runs at under 0.05 detection cost). Her side note the same day
("document our working recipe") → `experiments/MINIFRIEND-RECIPE.md`.
`minifriend-phase1e-diag-2026-11-02/DECLARATION.md`.
Status: CLOSED 2026-11-02 (declared 048803a4, reds 036d24d7, reads the
same day, 0 covered cat-ticks). P22 MET: covered friends' natural
crossings on the confirming half (251, H ≥ 100) detected 0.971 at her
pick against the frozen 0.564, anticipated 0.923 with a 51.3-tick
median lead — the scripted friend is a fair, conservative proxy. P21
NOT MET on its relative clause: the retrained head's covered false
runs are 0.752 approach-or-grave by runs (approach alone 0.728 by runs
and 0.903 by ticks; a post-hoc null 0.028 approach) against the
frozen's 0.848; the excess is 0.718 approach by runs and 0.923 by
ticks under alarm, the no-approach quarter 0.6232 per 10,000.
P23 MET at k = 10 only (0.534 of covered false runs removed at −0.037
N detection, −12.4 ticks of lead, T-H0 1.000 → 0.720); P24 NOT MET
(λ = 70: 0.446 at −0.035). D5: a [0.05, 0.10) tick is grave now in
0.0329 on covered friends (frozen 0.3647). F-073 minted. RESULTS gated
PASS, round 4 (rounds 1–3 wording and precision).

## 18. Mini-friend act predictor, Phase 1: a friend's next act from the observer's belief — shared state against its own memory at three budgets (2026-11-03)
Deviation: none from the Gen 2 prereg (18f06f84, untouched); the arm
spec amendment A4 deferred ("estimate head and act predictor both read
[b_t] … Detail at the arm spec", bracket mine), on her words "We definitely want two
heads", "Re: budget, we need to determine it empirically. Let's start
with 10%,20%,30% and evaluate accuracy. We can increase if needed." and
"Go". Zero collection: four arms × three seeds trained on Phase 1e's
split verbatim with the friend's applied act as the target (y0 =
applied[t] aligned to obs[t] per the collector's doc, y10 = applied[t +
10]); arm A = NF1e-h24's frozen GRU state + the friend row → a two-layer
head (6,742 trained parameters); arms B10 / B20 / B30 = their own
GRU at widths 24 / 39 / 50 (8,182 / 16,792 / 24,822 = 9.7 / 19.9 /
29.4% of the trunk; the needs head's 10% cap "was intended for need
prediction", her words, and does not bind here). Baselines F
(frequency), V (the visible row's activity), R (repeat). Reads on the
lived evaluation worlds and the needy TUNING half's covered friends;
the confirming half once for the chosen arm. P25–P28 registered (B10
beats F by ≥ 0.05 under fog; A within her margin m of B's best on the
primary and fog cells; B30 − B10 < 0.02; every arm ≥ V in sight).
Owner call 1: the margin m (recommended 0.02).
`minifriend-act-2026-11-03/DECLARATION.md`.
Status: CLOSED 2026-11-03 (declared 45368022, reds e2987d73, margin
RULED "As recommended" 3565f9be after training and before any read;
twelve heads, 0 covered cat-ticks). P26 NOT MET: arm A on the needs
head's state reads 0.616 against B10's 0.634 and B30's 0.647 (A −
B_best = −0.0305) — the act predictor is B10, its own state of width
24, two states per friend; arm C (joint training) hers by the rule.
P27 MET: B30 − B10 = 0.0127 top-1, the budget closes at 10% (log-loss
1.090 → 1.042 reported). P25 NOT MET as declared: the silent cell is
0.34% of covered-friend samples and B10 is 0.022 over frequency there;
heard (47.4%) reads 0.522 against 0.329, reported, the "sight-only"
consequence hers. P28 MET. Confirming half 0.633. F-074 minted. RESULTS
gated PASS, round 2 (round 1 one sentence's wording).
Owner calls 2–4 RULED 2026-11-04 ("Sounds good, let's get started" to
the plan "1+2+3 (5 done)?"): P25's consequence AMENDED to live in sight
and heard, frequency prior when silent (P25 stays scored NOT MET; heard
is a reported cell until a new declaration registers it); arm C SKIPPED
for Gen 2; the Professor's review note (sha256 938134f9…) CONFIRMED,
its declaration items carried into the Phase 2 draft. DECLARATION §13.
Next on her word: the act-head reliability read (B10 and B30) before the
Phase 2 declaration.

## 19. Act-head calibration: a zero-collection reliability read on B10 and B30 before Phase 2 declares (2026-11-04)
Deviation: none from the Gen 2 prereg (18f06f84, untouched). On her
question "is there a measure of predictive certainty we can use when
feeding this information into the main cat model" and her word "Sounds
good, let's get started" to the order reliability read → Phase 2
declaration → recipe sharpenings, after the Professor's review (note
sha256 938134f9…, confirmed). Zero collection: the committed act heads
B10-s1..3 and B30-s1..3 read on the needy TUNING half's covered friends
(top-prob reliability and ECE by regime at three temperings; accuracy by
entropy and the AUROC of 1 − entropy and of top-prob for correctness,
within regime) and on Phase 1e's 52 VALIDATION worlds (one temperature
per head, horizon and regime, grid 0.50–3.00 step 0.01, frozen).
Registered cells B10 / B30 × y0 × seen / heard with a 10,000-sample
floor (a count); P29–P32 registered (confidence tracks regime by ≥ 0.10;
in-sight AUROC ≥ 0.70; B30 − B10 AUROC < 0.02 in sight and heard; seen
and heard temperatures differ by ≥ 0.10). Decision rules fix Phase 2's
tempering (per-regime if P32, else global, T = 1 where it worsens a
registered cell), whether B20 is registered as a Phase 2 prediction
(only if P31 fails), and whether entropy / top-prob may be called
certainty cells (P30). No head chosen or budget reopened here.
`minifriend-act-calib-2026-11-04/DECLARATION.md`.
Status: CLOSED 2026-11-04 (declared 2d111f51, reds 9d048366; the fit
and reliability reads on that commit, the score read re-run after gate
round 1 with the per-head tempering rule, committed with RESULTS; 0
covered cat-ticks). P29 MET (B10 mean top-prob 0.737 in
sight against 0.537 heard); P30 MET (in-sight AUROC of 1 − entropy for
correctness 0.860); P31 MET (B30 − B10 AUROC −0.0002 seen, 0.0079
heard, under the declared 0.02; B20 not registered in Phase 2 by the
rule as declared, though its stated rationale is contradicted — a
temperature recovers at most 0.0003 of B30's roughly 0.047 NLL
advantage — so the registration question is hers); P32 NOT MET (B10 seen / heard temperatures
differ by 0.010; every non-silent fit 0.97–1.03). ECE at T = 1: B10 seen 0.0057,
heard 0.0149. Rules: top-prob and entropy are the two certainty
scalars; tempering per head (this thread's reading of "a head", chosen
after the read; the per-arm reading differs only on B10-s2, 0.99; her
word confirms or overrides), B10 frozen at 1.01 / 1.00 / 1.02 (seed 2's
0.99 raised its own ECE), B30 at 1.00 / 1.00 / 1.00. F-075 minted. RESULTS gated PASS, round 7
(rounds 1–6 wording and provenance; every number equal throughout).
Owner RULED after the gate (calib DECLARATION §9, "T=1.00 seems
reasonable … overfitting trying to tune it by 1-2%"; "Do it"): T = 1 for
every act head, no frozen temperatures; reliability read = monitor with
a 0.05 ECE trigger; the B20 question overtaken by her parameter-count
ladder (entry 20).

## 20. Act-head parameter ladder: B5 and B15 beside B10 / B20 / B30 — the loss curve against parameter count (2026-11-04)
Deviation: none from the Gen 2 prereg (18f06f84, untouched); the act
head's 10% closure (entry 18, P27) was this thread's rule, never hers
("The 10% budget rule was arbitrary and never declared by me last I
checked"). Her design: "What about B5,10,15 to better calibrate the loss
curve against parameter count? I. E. where are we getting bang for our
buck. We can extend to 20,30 if we see real welfare benefit"; her word
"Do it". Zero collection: six heads (B5 = GRU width 14, 3,942 params,
4.67% of the trunk; B15 = width 32, 12,438, 14.73%) trained by
`train_act.py` verbatim on Phase 1e's split, seeds 1–3, into the act
arc's heads store; reads = the act arc's accuracy read and the
calibration arc's reliability read over the five B arms (tuning half,
lived worlds, validation fit reported only — T = 1 ruled), and a curve
read: log-loss and top-1 per 1,000 added parameters at each step. P33
registered (the log-loss gain per 1,000 params shrinks at every step).
Decision rule: none selects — the Phase 2 act head is HER pick after the
curve (§8), her conditional "extend to 20,30 if we see real welfare
benefit" travels into Phase 2. Confirming half untouched until her pick.
`minifriend-act-ladder-2026-11-04/DECLARATION.md`.
Status: DECLARED 2026-11-04; guards l1–l5 green, reds next commit;
training starts on the reds commit.
DONE 2026-11-05 (reds 2c26664d; six heads trained and the four reads run
on that commit; 0 covered cat-ticks): on the tuning half, covered
friends, y0, log-loss 1.149 / 1.090 / 1.066 / 1.055 / 1.042 across B5 /
B10 / B15 / B20 / B30, top-1 0.615 / 0.634 / 0.640 / 0.644 / 0.647; per
1,000 added parameters the log-loss gain is 0.0140, 0.0055, 0.0025,
0.0017 — P33 MET, concave at every step, no knee (successive gains
shrink by 1.5–2.6×); B10 holds 0.55 of the B5 → B30 log-loss gain, B15
0.77, B20 0.87. Every arm honest at T = 1
(largest registered-cell ECE 0.0149, B10 heard; none over the 0.05
trigger); in-sight entropy AUROC 0.856–0.860 across the ladder. No
F-entry (the declared test, a knee the record did not have, is not
met); the ladder is a Phase 2 input cited from
`minifriend-act-ladder-2026-11-04/RESULTS.md`. CLOSED; the Phase 2 act
head is her pick (DECLARATION §8, not yet asked at this write).

## 21. The Phase 2 entry gate run by replay: the one-tick counterfactual screen on NF1e-h24+p and the act head B15 (2026-11-05)
Deviation: none from the gate's frozen text (A2′ item 2 and its four
pins stand verbatim); what the frozen text left to the arm spec is fixed
here — the gate runs on the needy set's TUNING half by replay on the
pinned binding (the Python binding has no snapshot path; a recorded world
replays exactly from seed and recorded actions, RE-STEP CHECK 2026-11-05),
the branch's menu action is the predicted class's legal entry the
friend's own policy ranks highest, the currency is unclamped happiness
points (hidden-need points reported), the sample is 300 points per
stratum × version at min-n 200 fail-closed, and step 2 is Phase 1's
ostrich metric read on NF1e (never read on it before; the prereg reads
the metric "on BOTH estimates, per phase") with the frozen NF-h24+p
beside. B10 is read beside B15 as the Phase 2 comparator (open-loop
B10-vs-B15); F is a reference. Her words: "Agreed" (the five steps),
"Let's do it" (gate by replay now; the branch API to Product, msg
9b1d6d03, not a kickoff). Zero collection; 0 covered cat-ticks (recorded
actions replayed, the branch discarded, k = 1). P34–P37.
`minifriend-phase2-gate-2026-11-05/DECLARATION.md`. Status: CLOSED
2026-11-05 — read on her "Go": GATE FAIL on the needs head (B10 PASS,
B15 PASS; NF1e FAIL: in-sight grave bias −3.17 need points against
common +0.07, Phase 1's signature in both versions; the frozen NF-h24+p
−26.86 beside). P34 / P35 MET, P36 / P37 NOT MET. Two reporting fixes
after the first run (7b7459f2, e1ed7605), rows equal.
`minifriend-phase2-gate-2026-11-05/RESULTS.md`. The consequence (§5: a
Phase 1f composition arm on the needs head) is hers.

## 22. Phase 2 without a needs head (2026-11-06)
Deviation from the frozen prereg's Phase 2 framing (the Phase 1 needs
head as the live arm's input; F-072 / F-073 named NF1e-h24+p the Phase 2
candidate): the entry gate (entry 21) FAILED on NF1e-h24+p and the owner
ruled, 2026-11-06, verbatim: "We can skip the needs head based on this
result." Phase 2 proceeds with the act head B15 as its only mini input
(B10 the comparator), no Phase 1f composition arm, the needs head and
its grave probability out of the policy's inputs. Consequences carried
into the Phase 2 declaration: the "needs-only anchor" arm she named on
2026-11-05 ("three arms") no longer exists as described — its replacement
(a no-head continuation anchor, or two arms) is her call; the consumer
read "harm-prediction beats trunk" was aimed at the grave channel and is
re-aimed or dropped in the declaration; the ticks-since-seen cell and
the act head's eleven probabilities, top-prob and entropy at T = 1 stay.
The frozen text is not edited; this entry is the record. Status: OPEN
until the Phase 2 declaration carries it.
