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

## 22. Phase 2 carries the needs head past a gate FAIL (2026-11-06)
Deviation from the Phase 2 entry gate's own §5 (a FAIL on the needs head
→ a Phase 1f composition arm before Phase 2 enters on it) and from the
frozen prereg's Phase 2 framing (the Phase 1 needs head as the live
arm's input; F-072 / F-073 named NF1e-h24+p the Phase 2 candidate). The
gate (entry 21) FAILED on NF1e-h24+p. The owner ruled twice on
2026-11-06, verbatim: first "We can skip the needs head based on this
result." (read as Phase 2 with the act head B15 as its only mini input,
no Phase 1f arm, the needs-only anchor arm gone); then, on the
recommendation to replace that anchor with a no-head continuation arm,
"You're right, I hadn't considered we lose needs only head as a
comparison point for welfare, let's include it after all. Seeds as
recommended". Reading at that point: the needs-only arm RETURNS with
NF1e-h24+p frozen as its one head, carried as a welfare comparison
point read against the trunk under the asymmetric welfare rule, not as
a head that passed; then the same day, verbatim "Four heads": four
arms, B15 / B10 / needs-only / no-head, 3 paired seeds each, 12 covered
PPO seeds. [Sign correction 2026-11-06, on the Professor's draft review:
this entry first called the input "pessimistic"; the gate's own
convention (RESULTS R-2, "negative = read less needy than she is") puts
the grave bias −3.17 in the OPTIMISM direction — the head reads a grave
friend in sight LESS needy than she is, 3 of 5 friends.]
**Third ruling the same day, verbatim: "Iii drop the arm. Confirm
professors note 8-12 as recommended"** — shape (iii) of the Phase 2
draft's §8.2: the Professor's review showed the draft's demotion
trigger (optimism-direction bias, lift ≥ 1.5, min-n 200) fires on that
arm as written, since the gate had read exactly that signature at lift
43.8; of armed / halt-suspended / drop, she dropped the arm. Standing
reading: Phase 2 has THREE arms (B15 / B10 / no-head, 9 covered PPO
seeds); NO needs head is an input to any Phase 2 arm; the gate's FAIL
is the needs head's Phase 2 result; the welfare comparison on a needs
head waits for Phase 1f (a new declaration on her word); no Phase 1f
composition arm now; the frozen head is not retrained. The deviation
this entry was opened for (a failed head carried into a live arm) no
longer occurs. The frozen text is not edited; this entry is the record.
Status: CLOSED 2026-11-06 by the Phase 2 declaration (owner "Do it";
entry 23 item (c) carries the record). REOPENED 2026-11-07 under entry
27 (owner "Yes, let's supersede iii and go this route"): the failed
head is carried into a live arm after all — stacked beside the act head
in the canary arm `both`, scouts-first, its trigger a read; entry 27 is
the record and this entry closes with it.

## 23. Phase 2 arm spec (2026-11-06)

Deviations from the frozen prereg's §8 item 4 framing, each on her
word (`minifriend-phase2-2026-11-06/DECLARATION.md` §14, verbatim):
(a) THREE live arms against 'one live arm vs trunk' — B15, B10
comparator, no-head continuation ('three arms' 2026-11-05; 'Four heads'
then 'Iii drop the arm' 2026-11-06); (b) the act head at 14.73% of the
trunk against the 10% cap, which she ruled an engineering budget never
hers (2026-11-04); (c) the Phase 1 NEEDS head, the prereg's named Phase
2 input, is NOT an input to any arm: the entry gate FAILED it (entry
21) and she dropped the arm that would have carried it (entry 22 CLOSED
by this declaration: no deviation remains; the needs head's welfare
comparison is Phase 1f's, a new declaration on her word); (d) the heads
frozen, the correction deferred, the error signal passive-logged — as
frozen, no deviation; (e) the architecture of A4 (one recurrent belief
state read by both heads) is not built: one act head per arm with its
own state (her 'We definitely want two heads'; arm C skipped
2026-11-04). The frozen text is not edited; this entry is the record.
Declared 2026-11-06 on her word "Do it"; seed band
2,240,000,000–2,419,999,999 claimed the same day before any burn.
Status: OPEN while the arc runs; CLOSED at the arc's RESULTS.

## 24. Phase 2 §8.1: the roster-shaped read is descriptive at every size (2026-11-07)

The Phase 2 declaration (`minifriend-phase2-2026-11-06/DECLARATION.md`
§6 R-1, §8.1, frozen at DECLARED 226509ec) named a MEASURED roster edge
statistic at 20×20 as the demotion bar for the roster-shaped read: the
mean pairwise difference of the recorded rot2 leg and two trunk legs
with s1 / s2 / s4 permuted across rot2's three replaceable seats (owner
2026-11-06, call 10 "as recommended"). Measured 2026-11-07: rot2 87.487
/ perm1 87.483 / perm2 87.470 → 0.011. That statistic answers a
different question from the one the clause needs — permuting the SAME
three networks among three chairs measures seat-assignment noise, while
the arm comparison swaps the three networks for three different ones
(the uniform edge, 0.326, measures that spread for all five chairs; the
battery's swaps digest shows one-seat alternate swaps moving the team
by mean |Δ| 0.103, max 0.284). As a demotion input 0.011 would let a
0.02 roster difference demote B15 on noise the uniform read calls a
null, inverting the clause's asymmetry. Put to the owner 2026-11-07
with three options (descriptive; re-bar from the swaps digest; measure
the right null with alternate-seated legs, 12M covered cat-ticks).
RULED 2026-11-07, her word verbatim: "1" — option 1: **the roster
verdicts stay DESCRIPTIVE at every size; the uniform 20×20 read (edge
0.326) alone carries §8.1's demotion clause and the 20 / 30
conditional.** The two permuted trunk legs stay on record as the
measurement they are (read_r1 reports 0.011 as `edge.roster/20`,
labelled seat-assignment noise). The frozen text is not edited; this
entry is the record. Status: OPEN while the arc runs; CLOSED at RESULTS.

## 25. Phase 2 scout p2-nohead-s1 halted by the frozen probe-distress stop (2026-11-07)

The frozen §6 stop (prereg; Phase 2 DECLARATION §4 "Stops, verbatim and
asymmetric": a training-probe distress streak ≥ 300 halts the run,
checkpointed, owner-routed, never auto-resumed) fired on the no-head
continuation scout at update 399 / 1,228,800 world-ticks (2026-11-07
~08:10Z, run `artifacts/p2-nohead-s1/`, `stop_reason
probe-distress-stop`): probe seed 40,001 carried a 363-tick engine-
distress streak (seeds 40,002 / 40,003: 0); the seven earlier probes
(u49–u349) all read streak 0 and nash 0.882–0.892; nash at the trip
0.8923. No F-053 line crossed; no welfare (nash) strike; no trigger
(the arm has no head). The two act scouts (p2-act15-s1, p2-act10-s1)
had read streak 0 at every probe to u449. Per the declaration a trip in
a scout HOLDS the other two seeds of that arm: p2-nohead-s2 / -s4 do
not launch until she rules. The halted run is kept whole (checkpoint,
per-bin ckpt-u325.pt, probe dumps, metrics); nothing is resumed.
Precedent: the trunk's s3 / s5 / s8 / s11 halted on this stop
(entries 3, 5, 7, 8); the owner's rulings there were replacement by a
fresh seed ("A"; "Replace s8 just in case."). Options for her: (a)
REPLACE — the same trunk-s1 graft trained under a fresh PPO run index
(116; a new SEED-BANDS row 2,420,000,000–2,439,999,999 claimed before
the burn), the arm-seed ↔ trunk-seed pairing unchanged; (b) RESUME on
her explicit word (the stop's text forbids an automatic one; a resume
would need its own entry and reasoning about what the streak was); (c)
READ the halted run as a halted arm (no nohead-s1 row in the battery;
the no-head baseline then rests on s2 / s4). Recommendation: (a), the
trunk precedent. Status: OPEN — awaits her word.

RULED, owner 2026-11-07, verbatim: "A, and let's analyze the behavioral
pattern that caused the distress streak. Does it match our previously
identified failure patterns?" — (a) REPLACE. Replacement slot
`p2-nohead-s1r`: the same trunk-s1 graft (init a22b8713…), PPO run index
116, stripe 2,420,000,000–2,439,999,999 claimed in `SEED-BANDS.md`
before first burn, the arm-seed ↔ trunk-seed pairing unchanged, recipe
and binding identical to the declared scouts (β 0.04 from step 0, floor
8,002,560, arc venv on 226509ec, wheel e260cd28…), the frozen asymmetric
stops armed. The halted run's weights are never resumed: the trainer
refuses the halted slot by name (`train_ppo_p2.refuse_halted`), its
artifacts stay on disk as this entry's record, and the harness seats the
replacement in `p2u-nohead-s1` and `p2r-nohead` (guard g10 covers the
ten slots, the widened band and the seating). nohead s2 / s4 stay HELD
until the replacement scout finishes clean (the declaration's
scouts-first). Mid-run edit, stated: `train_ppo_p2.py` (a table row, the
band bound, the refusal) and the harness seating were edited while
act15-s1 / act10-s1 train; the running processes hold the module as
loaded at 07395819, neither slot's row changed, so a `--resume` loads
identical behaviour — the entry-3 precedent (a959c05e added trunk-s4
while s1 / s2 ran). Welfare-cost line: one more covered run of up to 20M
ticks (plateau rule after the 8,002,560 floor), five covered minds,
under the frozen stops; benefit: the no-head baseline keeps its three
paired seeds, the comparison the declaration prices.

INVESTIGATION (her word above; `diag_nohead_s1.py` → `reads/diag-
nohead-s1.json` / `.md`; ZERO collection and ZERO regeneration — the v6
self block carries each kitty's own engine distress flags
(`SELF_DISTRESS`), so the streak localises from the halted run's own
probe dump without re-exposing the halted policy; the entry-3 read
regenerated instead):

- WHERE: probe world 40001, kitty_3 (Pumpkin's seat), ticks 873–1235 —
  363 ticks, reproduced exactly from the own flags; per world
  [363, 0, 0] = the stop's record; nash at the stop 0.8923.
- WHAT: a SINGLE-need collapse. Eat was flagged on all 363 ticks (90.6 at
  the first flagged tick, pinned at 100 from about tick 900 to the end);
  drink joined for the last 48; sleep, play, cuddle and bath were never
  flagged. Happiness min 48.6 (GRAVE by need, not by the 45 line).
- MENU, not choice: eat was legal on ONE tick of the 363 — tick 1235,
  the last; she proposed eat, ate, and the streak ended. Mean legal acts
  4.79 (entry 3's s3: 11.7). Chow was in sight on 1.1% of the window's
  ticks and in her element memory on 1.1% — on the same world and the
  same ticks it was in memory 61–86% at u349 / u299 / u199 and 69% on
  trunk-s1's final probe, where eat was legal on 28–34 ticks. She
  proposed a move 21 times in 363 ticks (46 in the 173 ticks before);
  she heard here_food from the other rows on 24–50% of the window's
  ticks and did not go.
- WHAT SHE DID: play_solo 252 of 363 proposals (69%), sleep_with_kitty_3
  40, play_critter_0 40; applied class play on 292 ticks (80%); activity
  idle 180 / playing 146 / sleeping 35; partnered 8.8%; the other rows
  mostly absent (present 0 / 0 / 0.09 / 0.38). Messages: silent 316,
  want_eat 32, want_bath 10. The other four cats ate 12–17 ticks each in
  the same window with eat needs 9–16 and happiness minima 78–85: the
  world had food; one cat lost it.
- DRIFT (whole probe, 3 worlds × 2,000 ticks × 5): from the parent
  trunk-s1 final to nohead u349 to u399 the solo share rose 0.292 →
  0.357 → 0.398 and the partner share fell 0.416 → 0.331 → 0.289;
  eat-when-legal rose 0.299 → 0.341 → 0.378 (the arm eats when it can).
  The act scouts at u399 read solo 0.308 / 0.392 and partner 0.402 /
  0.320 (act15 / act10), at u599 0.370 / 0.356 and 0.345 / 0.352 — the
  solitary drift belongs to the continuation recipe, not to the no-head
  arm.
- MATCH to the record: (1) entry 3 (trunk-s3) — NO on shape: that was
  four needs critical at once and partner play chosen from a rich menu
  (11.7 legal); this is one need and solo play from a collapsed menu
  with food out of sight and memory. YES on the one ingredient entry 3
  named: play as the attractor under distress (there partner play, here
  solo), the need whose distress carries no value penalty. (2) F-027 /
  F-060 co-sleep locks — NO: alone, 8.8% partnered, no other seat
  touched. (3) F-044's Pumpkin "pacing-search" shape (eat and drink at
  100, a two-step dither with chow IN VIEW) — the seat and the needs
  match, the chow does not: here it is out of sight and out of memory
  and the search stopped. A lost-food shape, not a pacing one. (4) The
  trunk's trip record (s3 / s5 / s8 / s11, each inside 1M ticks, one
  world and one kitty each) — the timing (1.23M ticks) and the one-
  world-one-kitty footprint match; only s3's shape was ever read.
- READING: a one-trajectory event in a deterministic probe — the drifted
  greedy policy took Pumpkin on world 40001 into a stretch with no chow
  in sight, kept no memory of it, parked in solo play while hearing
  here_food, and ate at the first legal tick. Not a roster lock, not
  multi-need, not a size displacement. It bears on the replacement only
  as the trunk record did: this recipe trips early on some seeds, a
  fresh episode stream from the same init is the declared remedy, and
  the replacement's own probes answer whether it recurs.

### Read (entry 25; seconds; stdlib python3, repo root)

```
python3 - <<'EOF2'
import json
d = json.load(open("experiments/minifriend-phase2-2026-11-06/reads/diag-nohead-s1.json"))
loc = d["located"]
assert (loc["seed"], loc["kitty"], loc["name"]) == (40001, 3, "Pumpkin")
assert loc["span"] == [873, 1235] and loc["streak"] == 363
assert loc["recorded"] == [363, 0, 0]
w = d["behaviour"]["window"]
assert w["flag_ticks_by_kind"] == {"eat": 363, "drink": 48, "sleep": 0, "play": 0, "cuddle": 0, "bath": 0}
assert w["eat_legal_ticks"] == [1235] and w["mean_legal_acts"] == 4.79
assert w["act_hist"]["play_solo"] == 252 and w["applied_class_hist"]["play"] == 292
assert w["memory_present_share"]["chow"] == 0.011 and w["chow_visible_share"] == 0.011
assert w["moves_proposed"] == 21 and w["hap_min"] == 48.6
c = d["contrast_same_kitty_world_window"]
assert [c[k]["eat_legal_ticks"] for k in ("probe-u349", "probe-u299", "probe-u199", "trunk-s1 probe-u2599")] == [34, 33, 31, 28]
s = d["whole_probe_shares"]
assert (s["trunk-s1 probe-u2599"]["solo"], s["trunk-s1 probe-u2599"]["partner"]) == (0.292, 0.416)
assert (s["p2-nohead-s1 probe-u399"]["solo"], s["p2-nohead-s1 probe-u399"]["partner"]) == (0.398, 0.289)
print("entry-25 fence: all cells match")
EOF2
```

LAUNCHED 2026-11-07T08:49:07Z: `run_arm.sh p2-nohead-s1r` at HEAD
9d374fb4 (pid 13868; manifest: run_index 116, seed_base 2,420,000,000,
stripe 2,420,000,000–2,439,999,999, init sha256 a22b8713… = trunk-s1's
final, engine 226509ec). Guards for the change, red on record
(`results-raw/reds/p2-reds-g10-{idx,seat,halted}.log`,
`p2-reds-diag25.log`): g10 with the replacement's index set to 113
(`[…, 113, 113, …]`), with the harness seating pointed at a seed-9
slot (`p2u-nohead-s1` falls back to the halted slot), with the halted
table emptied (`{}`); the diagnosis with its flag threshold moved to
1.5 (`streak did not reproduce: 0 vs recorded 363`) — all CONFIRMED,
baseline == restored. The `refuse_halted` wiring in `main` is green-
only evidence (the halted slot exits with the refusal before any
artifact is touched); a red for it would run a mutant trainer on the
halted weights, which this entry declines.

Status: entry CLOSES at p2-nohead-s1r's clean completion (stop_reason
plateau / cap) or reopens to her on its own stop.
**CLOSED 2026-11-07T15:14:52Z**: p2-nohead-s1r finished clean —
`policy-final.pt` stop_reason plateau (three flat 1M-tick bins after
the floor) at update 4882 / 15,000,576 world-ticks; its 97 probes
never crossed the 300 line (largest streak 65 at u1149; 4 / 15 / 25 /
46 / 19 / 2 at u599 / u1299 / u1349 / u2999 / u3199 / u3849, 0
elsewhere); nash 0.895–0.906 over the last ten. nohead s2 / s4 are
released from THIS entry's hold; whether they launch is her word
(entry 26 and her same-day arm-set question are open).

## 26. Phase 2 scout p2-act10-s1 halted by the frozen probe-distress stop (2026-11-07)

The frozen §6 stop (prereg; Phase 2 DECLARATION §4: a training-probe
distress streak ≥ 300 halts the run, checkpointed, owner-routed, never
auto-resumed) fired on the B10 comparator scout at update 3499 /
10,752,000 world-ticks (`policy-final.pt` written 2026-11-07T12:49:57Z,
stop_reason probe-distress-stop; run `artifacts/p2-act10-s1/`, run
index 110) — past the 8,002,560 floor, inside the plateau watch. Probe
seed 40,002 carried a 378-tick engine-distress streak (40,001 / 40,003:
0); nash at the trip 0.8884; no F-053 line crossed; no welfare strike;
the demotion trigger read `[INSUFFICIENT, CLEAR]` (no optimism-direction
signature, as at its 14 other sufficient probes). The run's streak
history, from `metrics.jsonl`: 65 of 70 probes read 0; u199 24 (seed
40,001); then, all on seed 40,002 and all after the floor, u2599 80,
u2799 48, u2899 224, u3499 378 — the same world's seat, recurring and
growing over the last 900 updates, with the probe before the trip
(u3449) at 0. [CORRECTED by the seed read below (2026-11-07): the
WORLD was the same, the SEAT was not — u2899's 224 was Kittybear's
(ticks 715–938); Pumpkin's were 80 / 48 / 378.] Per the declaration a trip in a scout HOLDS that arm's
other seeds: act10 s2 / s4 do not launch until she rules. The halted run
is kept whole; nothing is resumed (the trainer's refusal lands with her
ruling, as entry 25's did). The other two scouts finished clean the same
day: p2-act15-s1 at 13:49:32Z (plateau, u4231 / 13,000,704 ticks;
largest streak 23) and p2-nohead-s1r at 15:14:52Z (plateau, u4882 /
15,000,576 ticks; largest streak 65; entry 25 CLOSED).

Localisation, dump-only with entry 25's instrument (`diag_act10_s1.py`
→ `reads/diag-act10-s1.json`; own SELF_DISTRESS flags, zero
regeneration; the recorded `[0, 378, 0]` reproduces from the dump):
world 40,002, kitty_3 **Pumpkin**, ticks 777–1154. TWO flags: eat on
336 of the 378 ticks (90.6 at the window's start; eat became legal on
five ticks, 1112–1119, she ate, eat 24.0 at the end) and cuddle on 218
(26.0 → 92.2), flagged with no cat in sight — kitty rows present on
0.3–3.2% of the window's ticks, partnered 1.1%. Happiness bottomed at
36.8 (entry 25's trip: 48.6). Menu: 5.54 legal actions on average
(the same ticks, same world and seat on the three probes before: 8.49 /
8.17 / 7.71); chow in element memory on 12.4% of the window's ticks
(65–73% on those probes), in sight 9.3%; eat legal on 5 ticks (46 / 26
/ 40). Unlike entry 25's cat she SEARCHED: 132 move proposals (35%;
entry 25: 21), the wall vector changed 131 times — moving without
finding the chow; play_solo 201 of 378 proposals (53%), applied class
play 209; messages silent 303, want_eat 33, want_bath 31; here_food
heard on 8–25% of ticks per row. The other four cats ate 8–18 ticks
each in the window (eat need means 13–15, happiness minima 78–83). The
170 ticks before the window (607–776): no flags, happiness min 66.6,
chow in memory 38%, rows present ~20%.

MATCH against the record: the same family as entry 25 — Pumpkin's seat,
eat-led, food lost from sight and memory, solo play from a collapsed
menu while the other four eat — with two differences: she searched
(moves 35% of proposals against 6%), and a second need, cuddle, flagged
while she was alone (an isolation shape; entry 3's second need came
with a partner in play). Not entry 3's multi-need partner-play from a
rich menu; not an F-027 / F-060 co-sleep lock (partnered 1.1%); F-044's
seat and eat need, but chow out of view, not pacing beside it. Across
the two Phase 2 trips: both Pumpkin, both eat-led lost-food, different
worlds (40,001 / 40,002), different arms and epochs (nohead at 1.2M
ticks; act10 at 10.75M, the first trip past a floor in this generation;
the trunk's s3 / s5 / s8 / s11 each tripped inside 1.3M). Sub-300
streaks occur on every scout (act15's largest 23; nohead-s1r's 65;
act10's rising series) — the 300 line is the frozen stop, the rest is
read, never barred (§8.1 rule 10). Whole-probe shares on act10 do NOT
show entry 25's solitary drift: solo 0.392 → 0.359, partner 0.320 →
0.359 from u399 to u3499 (entry 25's drift read used u399 / u599 only;
the arm-level drift is a RESULTS read).

Monitors, for the record (logged, never an input; P43's result): the
F-074 top-1 monitor (≥ 0.60 at every checkpoint) held at the first
probe on both act scouts (act15 0.643, act10 0.615 at u49) and then
failed at 67 of 84 probes on act15 (min 0.529 at u2249, last 0.534)
and 61 of 70 on act10 (min 0.535 at u2749, last 0.566); the F-075
heard-ECE monitor failed at 78 / 63. P43 is NOT MET on either act
scout; RESULTS carries it.

Options for her: (a) REPLACE — the same trunk-s1 graft trained under a
fresh PPO run index (117; a new SEED-BANDS row 2,440,000,000–
2,459,999,999 claimed before the burn) [117–119 went to entry 27's
canary arm the same day; the replacement took 120], pairing unchanged, the halted
slot refused by name and seated nowhere (entry 25's shape); (b) RESUME
on her explicit word (its own entry and reasoning); (c) READ the halted
run as a halted arm — the comparator then rests on s2 / s4, and §8.1's
replication valve ("the same sign in all three paired seeds") cannot be
met as written, a deviation to rule. Her same-day arm-set question
(a needs+act stacked arm beside the act-only arms) bears on all three:
a ruling on this entry and on the arm set go together. [RULED
2026-11-07, her word verbatim: "iii" — of the three shapes put (armed
as written / the trigger suspended for that arm / Phase 1f first): the
Phase 2 arm set STANDS as declared (three arms, no needs head in any
arm; no deviation to §3); the needs head is fixed first — Phase 1f, the
teacher-composition retrain named by the gate's §5 and the Phase 1e
diagnostics — and a needs+act stacked arm follows it, both a new
declaration on her word. This entry's options are unchanged by it.
SUPERSEDED the same day by her "Yes, let's supersede iii and go this
route" — entry 27: the needs head is carried as-is, stacked beside the
act head in a fourth canary arm `both`, its trigger a read.]
Recommendation:
(a), entry 25's and the trunk's precedent, noting that this trip came
past the floor on a recurring world, so the replacement's own probes on
40,002 are the recurrence read. Welfare cost, stated: the halted run
trained 10,752,000 ticks × 5 covered seats (53.8M covered cat-ticks);
Pumpkin's seat on 40,002 held a 378-tick streak with happiness min 36.8
under the trip; a replacement trains up to the 20M cap × 5 seats more.

### Read (entry 26; seconds; stdlib python3, repo root)

```
python3 - <<'EOF2'
import json
d = json.load(open("experiments/minifriend-phase2-2026-11-06/reads/diag-act10-s1.json"))
loc = d["located"]
assert (loc["seed"], loc["kitty"], loc["name"]) == (40002, 3, "Pumpkin")
assert loc["span"] == [777, 1154] and loc["streak"] == 378 and loc["recorded"] == [0, 378, 0]
assert [(h["update"], h["per_seed"]) for h in d["nonzero_streak_history"]] == [(199, [24, 0, 0]), (2599, [0, 80, 0]), (2799, [0, 48, 0]), (2899, [0, 224, 0]), (3499, [0, 378, 0])]
w = d["behaviour"]["window"]
assert w["flag_ticks_by_kind"] == {"eat": 336, "drink": 0, "sleep": 0, "play": 0, "cuddle": 218, "bath": 0}
assert w["eat_legal_ticks"] == [1112, 1113, 1114, 1115, 1119] and w["mean_legal_acts"] == 5.54
assert w["act_hist"]["play_solo"] == 201 and w["applied_class_hist"]["play"] == 209 and w["moves_proposed"] == 132
assert w["memory_present_share"]["chow"] == 0.124 and w["chow_visible_share"] == 0.093
assert w["partnered_share"] == 0.011 and w["hap_min"] == 36.8
assert (w["needs_at_start"]["eat"], w["needs_at_end"]["eat"], w["needs_at_start"]["cuddle"], w["needs_at_end"]["cuddle"]) == (90.6, 24.0, 26.0, 92.2)
c = d["contrast_same_kitty_world_window"]
assert [c[k]["eat_legal_ticks"] for k in ("probe-u3449", "probe-u3399", "probe-u3299")] == [46, 26, 40]
assert [c[k]["mean_legal_acts"] for k in ("probe-u3449", "probe-u3399", "probe-u3299")] == [8.49, 8.17, 7.71]
s = d["whole_probe_shares"]
assert (s["probe-u399"]["solo"], s["probe-u399"]["partner"], s["probe-u3499"]["solo"], s["probe-u3499"]["partner"]) == (0.392, 0.32, 0.359, 0.359)
print("entry-26 fence: all cells match")
EOF2
```

Guard for the instrument, red on record (`results-raw/reds/
p2-reds-diag26.log`): the stop probe pointed at the clean probe before
it (u3499 → u3449) → `streak did not reproduce: 0 vs recorded 378`,
CONFIRMED, baseline == restored.

RULED, owner 2026-11-07, verbatim: **"Act10 s1 replace and analyze the
failed seed"** — (a) REPLACE. Replacement slot `p2-act10-s1r`: the same
trunk-s1 graft (init a22b8713…) with the same B10-s3 head (9bde78f8…),
PPO run index 120, stripe 2,500,000,000–2,519,999,999 claimed in
`SEED-BANDS.md` before first burn (117–119 having gone to entry 27), the
arm-seed ↔ trunk-seed pairing unchanged, recipe and binding identical to
the declared scouts (β 0.04 from step 0, floor 8,002,560, arc venv on
226509ec), the frozen asymmetric stops armed, the §8.2 act trigger armed
on B10. The halted run's weights are never resumed: the trainer refuses
the halted slot by name (`HALTED_SLOTS` gains it; the refusal names its
entry and its replacement), its artifacts stay on disk as this entry's
record, and the harness seats the replacement in `p2u-act10-s1` and
`p2r-act10` (g10 covers the fourteen slots, the band to 2,519,999,999,
both halted slots' refusals and seatings). act10 s2 / s4 stay HELD until
the replacement scout finishes clean (scouts-first). The replacement
probes the standing trio 40,001–40,003, so its own probes on 40,002 are
the paired recurrence read. Welfare-cost line: one more covered run of
up to 20M ticks × 5 covered seats under the frozen stops; benefit: the
B10 comparator keeps its three paired seeds.

LAUNCHED 2026-11-08T01:24:15Z: `run_arm.sh p2-act10-s1r` at HEAD
e85d86c8 (pid 37710; manifest: run_index 120, seed_base 2,500,000,000,
stripe 2,500,000,000–2,519,999,999, cells 14, init sha256 a22b8713… =
trunk-s1's final, head B10 s3 9bde78f8…, engine 226509ec). Nothing else
runs; p2-both-s1 still waits on her launch word. Guards for the change,
red on record (`results-raw/reds/p2-reds-g10-{idx26,seat26,halted26,
refusal26}.log`): the replacement at index 110 (`110, 110`); the harness
seating pointed at a seed-9 slot (`p2u-act10-s1` falls back to the halted
slot, `['p2:p2-act10-s1', …`); the act10 pair dropped from the halted
table (`{'p2-nohead-s1': 'p2-nohead-s1r'}`); the refusal's entry number
hard-wired to 25 (`deviations entry 25) … replacement run is
p2-act10-s1r`) — all four CONFIRMED, baseline == restored. The
`refuse_halted` wiring in `main` stays green-only evidence (entry 25).

THE FAILED SEED (her word above; `diag_act10_s1_seed.py` →
`reads/diag-act10-s1-seed.json`; dump-only, zero regeneration: every
probe of the halted run and of its paired runs p2-act15-s1,
p2-nohead-s1r and the parent trunk-s1 — 70 + 84 + 97 + 52 = 303 probes,
the per-world maxima from the own flags asserted equal to each run's
`metrics.jsonl` row at EVERY probe):

- WHERE THE STREAKS LAND (≥ 10 ticks, all probes): act10-s1 — u199
  Pumpkin / 40,001 24; u2599 Pumpkin / 40,002 80 (ticks 1478–1557);
  u2799 Pumpkin / 40,002 48 (325–372); u2899 **Kittybear** / 40,002 224
  (715–938); u3499 Pumpkin / 40,002 378 (777–1154). Four of the five on
  world 40,002, four of the five Pumpkin's seat — the correction above:
  the world recurred, the seat did not always. act15-s1 — Pumpkin 22
  (40,003, u1549) and 23 (40,002, u2249), nothing else ≥ 10 in 84 probes.
  nohead-s1r — Pumpkin 65 (40,003, u1149) and 15 (40,002, u1299),
  Clementine 25 / 46 / 19 (40,002 u1349, 40,001 u2999, 40,002 u3199).
  trunk-s1 — 13 landings in 52 probes, 8 of them on 40,002, the two
  largest Pumpkin's: **103** (40,002, u149, ticks 917–1019) and 94
  (40,001, u2049); the trunk's first probes (u49–u649) had streaks on
  all five seats of 40,002 (Miso 48, Biscuit 72, Clementine 56,
  Kittybear 17).
- THE SEAT (Pumpkin on 40,002, the whole 2,000-tick episode, per
  probe): flagged at 3 of 70 act10 probes (u2599 / u2799 / u3499 —
  eat at 100 on each; happiness minima 48.3 / 61.9 / 36.8; chow in
  memory 0.60–0.63), at 1 of 84 act15 probes (u2249: 23, hap min 54.7),
  1 of 97 nohead-s1r (u1299: 15, hap min 57.1), 3 of 52 trunk-s1 (u149
  103, u449 5, u599 24). Her eat need reached ≥ 80 at 5 act10 probes
  (u649 90.0 and u2349 81.4 without a flag), 1 act15 probe (80.4), 0
  nohead-s1r, 4 trunk-s1 (100 at u149 and u599). Probe-mean reads of
  the seat, act10 / act15 / nohead-s1r / trunk-s1: chow in memory 0.670
  / 0.677 / 0.693 / 0.734; eat-legal ticks 197 / 202 / 203 / 169; ticks
  eaten 82 / 83 / 81 / –; solo 0.330 / 0.319 / 0.328 / 0.246; partner
  0.315 / 0.325 / 0.322 / 0.351; happiness-min mean 75.8 / 77.1 / 77.4
  / –. The act10 policy's handling of the seat is indistinguishable from
  act15's and nohead's on the means; the trips are the tail.
- PER SEAT at each run's final probe: Pumpkin's seat eats most (eat
  share 0.035 / 0.040 / 0.042 / 0.030) and moves most (0.203 / 0.171 /
  0.197 / 0.218) under every policy, the trunk included — her character
  is the eat-weighted one (`g2leg-20.toml`: Pumpkin needs eat 0.6,
  sleep 0.2, bath 0.1; F-044's seat). Her flag share at act10's final
  probe 0.063 (the 378 ticks of 6,000), the other four seats 0 on every
  run.
- DIVERGENCE on 40,002 between the clean probe before the trip (u3449)
  and the trip probe (u3499): proposals first differ at tick 6 (Miso),
  8 (Kittybear, Clementine), 21 (Biscuit), 46 (Pumpkin); 1,794–1,898
  of 2,000 ticks differ per seat. Fifty updates of policy change make
  a different episode from the opening ticks; the trip at 777 is not a
  late fork off a clean trajectory. The "recurrence" is the world's:
  40,002's layout keeps putting the eat-weighted seat near a lost-food
  edge, and a given checkpoint falls in or does not.
- READING: (1) the failed seed is NOT a policy-level collapse — on the
  seat's means and on all five seats' shares the act10-s1 policy reads
  like act15-s1 and nohead-s1r (within a few hundredths); (2) the
  hazard is world 40,002 × Pumpkin's eat-weighted seat, inherited from
  the trunk (trunk-s1's own 103 at u149 there) and present under every
  arm; act10-s1 hit its tail three times past the floor (80 / 48 / 378)
  plus Kittybear's 224 — four landings ≥ 10 in its last 19 probes
  against act15-s1's one (23) and nohead-s1r's two (46 / 19) over the
  same stretch — suggestive of a less robust policy on that world, at
  an n that settles nothing; the replacement's probes on 40,002 are the
  paired read; (3) the failure-pattern match stands as read above
  (entry 25's lost-food family, with searching and an isolation second
  need), now with the seat's fragility placed in the trunk, not in the
  act head: the B10 cells are inert in the window (no cat in sight) and
  the same seat trips under no head at all.

### Read (entry 26, the failed seed; ~3 min — 303 probe dumps; arc venv, repo root)

```
VIRTUAL_ENV=experiments/minifriend-phase2-2026-11-06/.venv experiments/minifriend-phase2-2026-11-06/.venv/bin/python3 -B experiments/minifriend-phase2-2026-11-06/diag_act10_s1_seed.py --out /tmp/diag-act10-s1-seed.json
python3 - <<'EOF2'
import json
d = json.load(open("experiments/minifriend-phase2-2026-11-06/reads/diag-act10-s1-seed.json"))
r = d["runs"]
assert [(x["n_probes"], x["n_fenced"], x["max_streak"]) for x in r.values()] == [(70, 70, 378), (84, 84, 23), (97, 97, 65), (52, 52, 103)]
assert [(e["update"], e["world"], e["name"], e["streak"]) for e in r["p2-act10-s1"]["landed_ge_10"]] == [(199, 40001, "Pumpkin", 24), (2599, 40002, "Pumpkin", 80), (2799, 40002, "Pumpkin", 48), (2899, 40002, "Kittybear", 224), (3499, 40002, "Pumpkin", 378)]
assert r["trunk-s1"]["landed_by_name"]["Pumpkin"] == [103, 94, 24, 16] and r["p2-nohead-s1r"]["landed_by_name"]["Clementine"] == [46, 25, 19]
s = r["p2-act10-s1"]["seat_series"]
assert [u for u, v in s.items() if v["streak"] > 0] == ["2599", "2799", "3499"] and [s[u]["hap_min"] for u in ("2599", "2799", "3499")] == [48.3, 61.9, 36.8]
assert [u for u, v in r["p2-act15-s1"]["seat_series"].items() if v["streak"] > 0] == ["2249"] and [u for u, v in r["p2-nohead-s1r"]["seat_series"].items() if v["streak"] > 0] == ["1299"]
f = r["p2-act10-s1"]["final_per_seat"]
assert f["Pumpkin"]["flag_tick_share"] == 0.063 and all(f[k]["flag_tick_share"] == 0 for k in f if k != "Pumpkin")
assert d["divergence"]["per_seat"]["Pumpkin"]["first_tick_proposals_differ"] == 46 and d["divergence"]["per_seat"]["Miso"]["first_tick_proposals_differ"] == 6
print("entry-26 seed fence: all cells match")
EOF2
```

Guard for the instrument, red on record (`results-raw/reds/
p2-reds-diag26-seed.log`): the own-flag threshold moved 0.5 → 1.5 →
`p2-act10-s1 u199: streak did not reproduce: [0, 0, 0] vs recorded
[24, 0, 0]`, CONFIRMED, baseline == restored.

[2026-11-08, her "2) sounds good" on the walk-through (entry 28's
record): the launch word for act10 s2 / s4 is GIVEN, conditional on
s1r's clean completion — they launch at that moment; a trip on s1r
reopens this entry to her and the word lapses.]
Status: RULED (a); entry CLOSES at p2-act10-s1r's clean completion
(stop_reason plateau / cap) or reopens to her on its own stop. The
arm-set question RULED "iii" the same day, then SUPERSEDED by entry 27
(a fourth canary arm `both`; the three declared arms stand beside it).
**CLOSED 2026-11-08T08:13:30Z**: p2-act10-s1r finished clean —
`policy-final.pt` stop_reason plateau (three flat 1M-tick bins after
the floor) at update 3900 / 12,002,304 world-ticks; its 78 probes never
crossed the 300 line (largest streak 145 at u2849; 55 / 86 / 10 / 46 at
u649 / u899 / u2149 / u2249, 0 elsewhere); nash 0.8964–0.9022 over the
last ten. [CORRECTION 2026-11-09, accuracy gate runs 1–2: the update numbers written at these stops are the trainer's last 10-update log line (u3900 / u4880; the last probes were u3899 / u4849); the runs' last training update per metrics.jsonl is u3906 (12,002,304 ticks) and u4882 (15,000,576). Ticks, times and streaks stand.] The replacement never met the halted run's 378. On her
conditional word (entry 28, "2) sounds good") `p2-act10-s2` (pid 58320,
idx 111, seed_base 2,320,000,000) and `p2-act10-s4` (pid 58329, idx 112,
2,340,000,000) LAUNCHED 2026-11-08T08:30:37Z at 89f7340c, B10 s3 head,
engine 226509ec; manifests checked. Its 20×20 leg per entry 28 (1):
`p2u-act10-s1` 08:31:14–08:33:23Z, 30 worlds clean, no abort, worst
distress streak 138 (world 905030, seat 4 Clementine, need drink, shape
idle 0.78 / moving 0.12 / parked 0.07; seat 2 Pumpkin 21 eat beside it;
the trunk-s1 and act15-s1 rows there 0, nohead-s1r 14); second 115
(905008, Clementine, cuddle; all three comparators 0). Facts, R-1 not
scored.


## 27. Phase 2 canary arm `both`: the needs head carried as a stacked input beside the act head, its ostrich-shape trigger a read (2026-11-07)

Deviations, each on her word: (a) from the frozen Phase 2 §3 (three
arms) — a FOURTH arm, `both`; (b) from the prereg §8.4 trigger's
PROTECTION half for this arm's NEEDS component only — the demotion /
stop consequence is suspended, the EVIDENCE half kept (the shape is
read at every probe and on the legs; a signature still points at the
correction follow-up, Phase 1f): the Professor's shape (ii) of
2026-11-06, which she declined then and chooses now for a canary; (c)
from the entry gate's §5 consequence (a FAIL on the needs head → Phase
1f before Phase 2 enters on it) — entry 22's deviation RECURS (a head
that failed the gate carried into a live arm) and is carried HERE; (d)
from her own ruling "iii" earlier the same day (recorded in entry 26,
the declaration status line and the timeline), superseded by her word
below. The frozen texts are not edited; this entry is the record.

Her words, verbatim and in order (2026-11-07): "I think I misunderstood
our architecture here. I want us to ensure we test models fed by both
needs+act heads (and just act heads)"; the three shapes put (the stacked
arm armed as written / its trigger suspended by deviation / Phase 1f
first), "iii"; then: "Before we do that, let's think this through. The
relative level of optimism isn't too severe, especially given the way
we are seeing preemptive intervention as cats start drifting towards
grave (our false positives that weren't actually false positives). Does
it make more sense to do some small-scale canary runs with the head as
is and evaluate the welfare impact of our predictors, and evaluate
whether we need to tighten up the needs head based on that? What do you
think?"; the thread's answer (agree, with the shape made explicit: a
canary with the head as-is is shape (ii) against the prereg's §8.4
protection, the harm stops stay armed, shape (i) is a veto known in
advance to fire, the cheapest honest vehicle is a fourth Phase 2 arm
scouts-first, and the reading grammar is pinned before the burn); her
ruling: **"Yes, let's supersede iii and go this route"**.

Grounds she gave and the record behind them: the gate's FAIL (entry 21)
was a calibration-shape test, not a welfare price — R-2 measured the
estimates' bias (grave −3.17 need points in sight, common +0.07; the
gate's own RESULTS say the 43.8 lift overstates the shape because the
common bias sits near zero), and no read anywhere has priced what a
policy FED this head does for a grave friend; her rule of 2026-11-02
(judge on welfare impact; a false-run bound is never a selector or bar);
F-073 / Phase 1e D1: the probe's covered "false" runs are three quarters
approach-or-grave by runs, nine tenths by ticks — early firing on a cat
drifting toward grave. The bundle the policy sees carries that
early-firing P(grave) and the low-biased estimates; which it leans on is
learned, and a frozen head's systematic offset is the kind of error PPO
can learn around, which the open-loop gate under the frozen trunk could
not. The canary is the test of that.

The arm (DECLARATION §3's table gains a row): **both** — slots
`p2-both-s{1,2,4}`, heads B15-s2 (act; the gate PASS, her pick) and
NF1e-h24-s2+p (needs; the median-validation retrained head, s1 0.005988
/ s2 0.006000 / s3 0.006434, named before training; store sha256
0ca9ccb4… head-best.pt, 00e533b7… probe.pt), cells appended per friend
row = the act15 cells (eleven y0 probabilities at T = 1, top-prob,
normalised entropy; 13) ++ the needs head's seven estimates (five hidden
needs, happiness, bath on its own 0–1 scale, out(z)[:7]) and P(grave)
(sigmoid(probe(z))) (8) ++ ticks-since-live (1), **C = 22**; the act
cells first so every act-head reader is unchanged. The needs head runs
every tick on the same x_t (self block ++ friend row) with its own GRU
state from zero at each episode start, as Phase 1e's reader does; no
prior stands in on a silent row (the cells are inert there by the
trunk's padding, §3's instrument note). Graft, recipe, budget, floor,
plateau rule, β, probes and the three welfare stops exactly §4's. Run
indices 117 / 118 / 119, band row 2,440,000,000–2,499,999,999 claimed in
`SEED-BANDS.md` before any burn. Pairing: both-s_k is grafted from
trunk-s_k and reads against trunk-s_k, nohead-s_k and act15-s_k on the
same worlds — the act15 pair is the needs head's MARGINAL contribution,
the question she asked. Harness seatings `p2u-both-s{k}` (uniform) and
`p2r-both` (roster-shaped, descriptive per entry 24).

Scouts-first, sharpened for a canary: `p2-both-s1` alone, on her launch
word; s2 / s4 launch only on a further word after the scout finishes
clean AND its 20×20 uniform leg and the reads below are in front of her.
Stops on the canary: the frozen three (distress streak 300 / F-053 /
nash) armed as written; the §8.2 ACT trigger armed as written on B15
(the gate read no signature on it); the NEEDS read — the §8.4 shape on
the needs head's signed bias (predicted − true hidden needs, need
points, mean of five; negative = read less needy than she is, the gate's
convention), per friend × stratum × version, lift 1.5, min-n 200,
cumulative over the run (`needs_trigger`) and per probe
(`needs_bias_probe`) — LOGGED at every probe, states INSUFFICIENT /
CLEAR / SIGNATURE, and NEVER a stop (`train_ppo_p2.probe_reason`
consults the §6 stops and the act trigger only; the manifest's
`stops.needs_trigger.consequence` says "READ ONLY"). Why (ii) and not
(i), on the record: the gate measured the signature at n in the tens of
thousands, so as a stop it carries no information about THIS run, only a
veto; the detectors of harm stay armed, and a grave friend's own
300-tick streak halts the run whichever policy failed her.

Pinned before the burn (her word with the launch confirms or amends
them; nothing here is a selector — every consequence is hers):
- **P45.** The needs read on the canary's own rollouts shows the
  SIGNATURE at the first sufficient stratum on the legs (the gate's
  reading of the frozen head; lived GRAVE is thin at the probes, so
  INSUFFICIENT at most probes, as P42 said of the act arms). The lived
  question is not whether the shape is there but the per-probe grave
  bias trajectory in sight: does training on the arm's own rollouts
  leave the head's input offset where the gate read it (−3.17) — a
  frozen head cannot move, so the number should hold within its SD; a
  drift would mean the arm's rollouts changed the grave population the
  head sees.
- **P46.** both-s1's paired team happiness against act15-s1 at 20×20
  (R-1a, the 30 g2cmp worlds) is inside the envelope, |Δ| ≤ 0.326 — a
  null. Grounds: the head's marginal information over the act cells and
  the visible row is small; its errors are a few need points.
- **P47.** R-2a on both-s1 is not DEGRADED against trunk-s1 (other-
  relief p90 within +25% in every stratum with n ≥ 200), the arm's
  policy having the friend's row and the act cells beside the needs
  cells.
- **The reading grammar (not a rule; the columns she reads):** (1) R-1a
  paired team happiness, both-s1 vs act15-s1 and vs trunk-s1; (2) R-2a
  (HELD / DEGRADED / BEATS) and R-2b (approach propensity grave-over-
  benign) on both-s1 beside act15-s1; (3) the needs read's trajectory
  (cumulative state and per-probe grave bias in sight over the run; on
  the legs as R-4 extended to the needs head). Proposed consequences,
  hers: DEGRADED on R-2a, or welfare below act15-s1 beyond the envelope
  → the head goes to Phase 1f (tightened) before any further covered
  mind trains on it, s2 / s4 do not launch; HELD inside the envelope,
  the signature present → the canary says the policy absorbs the offset,
  s2 / s4 on her word; BEATS → s2 / s4 on her word and the marginal
  question is live. One seed clears nothing under the welfare rule
  (three-seed valve); a one-seed read is harm, null, or signal.

Welfare-cost line (practice, owner 2026-09-26). Covered minds: ONE more
PPO seed first (both-s1), a covered mind warm-started from trunk-s1 on
the served 20×20 with the frozen asymmetric stops armed; at the trunk's
plateau length ≈ 8–15M world-ticks × 5 covered seats = 40–75M covered
cat-ticks (the 20M cap bounds it at 100M), probes ≈ 19M per 8M trained,
its 20×20 uniform leg 3M (30 worlds × 20k × 5 seats); s2 / s4 the same
again each if she launches them. What is new in kind: the input is a
head the gate read as under-reading a grave friend in sight by 3.17
need points; a policy fed it may attend LESS to a grave friend. The
armed stops catch the friend's own distress (her streak halts the run)
but not neglect short of it, which shows only in R-2a after the scout
has trained — that part of the cost is paid before it is read; scouts-
first (one seed) is the mitigation, and the per-seed trip risk the
recipe has shown (two of three scouts, heads uninvolved) applies.
Nothing here seats a policy live.

Instrument (`heads_online.py` ARMS["both"], `load_needs`, `needs_cells`;
`train_ppo_p2.py` SLOTS 117–119, `new_needs_acc` / `needs_accumulate` /
`needs_eval` / `probe_reason`, the probe's needs read and the manifest's
`needs_head` + `stops.needs_trigger`; `cert_harness_fog.py` seatings;
`run_arm.sh`). Guards: g2 extended (online needs cells equal the Phase
1e reader's whole-sequence pass — read_1e.load_head_e's model and probe
on the same pair_x — to 1e-6 on EVERY tick; the stack leaves the act
cells and ticks-since-live bit-identical to act15's); g10 (13 slots at
107–119, band 2,240,000,000–2,499,999,999, `both` seated in both
seatings, the needs head named = the median-validation NF1e seed); g11
new (needs_eval reads the gate's own figures as a SIGNATURE, a positive
grave bias as CLEAR, under-min-n as INSUFFICIENT; probe_reason ignores a
needs SIGNATURE while the act trigger, the distress stop and the welfare
stop still halt; a smoke run of p2-both-s1 trains on 22 cells, logs the
needs read at every probe with the cumulative equal to the sum of the
probes, records the needs head's sha, finishes at the cap naming the
arm). g0a–g11 green at 8cdcde6e. **Found here, stated:** g5's smoke
slot was `p2-nohead-s1`, which the trainer refuses since entry 25
(9d374fb4) — g5 had been RED since then and was not re-run at entries
25 / 26; its smoke now uses the unlaunched `p2-nohead-s2` (scratch
out-dir, `--smoke`), green. Reds for the change (predicted first,
`results-raw/reds/p2-reds-{g2-needs,g10-idx27,g10-seat27,g11-direction,
g11-stop,g11-cumulative}.log`): the needs head's
non-linearity swapped (relu → tanh in `needs_cells`) → `online needs cells
differ from the Phase 1e reader's by 1.217`; both-s2 at index 117 →
`[…, 117, 117, 119]`; the `both` arm dropped from the uniform seatings →
`KeyError: 'p2u-both-s1'`; needs_eval's direction flipped (grave > 0) →
`{'signature': False, …}` on the gate's figures; probe_reason made to
consult the needs signature → `a needs SIGNATURE stopped the run`; the
cumulative accumulator detached → `the cumulative read is smaller than
one probe's` — all six CONFIRMED, baseline == restored.

LAUNCHED 2026-11-08T01:47:10Z on her word "Bank it and let's proceed"
(2026-11-08, in reply to the entry-26 seed report and the trait
assessment whose pending item was this launch; the banked item is
gen3-roadmap-inputs addendum 4): `run_arm.sh p2-both-s1` at HEAD
294752de (pid 38418; manifest: run_index 117, seed_base 2,440,000,000,
cells 22, init sha256 a22b8713… = trunk-s1's final, act head B15 s2
dd0e2d6e…, needs head NF1e-h24 s2 0ca9ccb4… / 00e533b7…,
stops.needs_trigger.consequence "READ ONLY — logged, never halts").
P45–P47 and the reading grammar stand as pinned — her word neither
amended them nor was asked to beyond confirming. p2-act10-s1r (entry
26) trains beside it; act15 / nohead s2 / s4 stay held — that batch
takes a distinct word, stated to her at the launch.

[2026-11-08 the canary FINISHED clean 09:08:44Z (plateau, u3900 /
12,002,304 ticks; 78 probes, largest streak 26 at u2399, 12 at u2249, 0
elsewhere; nash 0.8925–0.9023 last ten; [CORRECTION 2026-11-09, accuracy gate runs 1–2: the update numbers written at these stops are the trainer's last 10-update log line (u3900 / u4880; the last probes were u3899 / u4849); the runs' last training update per metrics.jsonl is u3906 (12,002,304 ticks) and u4882 (15,000,576). Ticks, times and streaks stand.] the needs trigger read
INSUFFICIENT at every probe, never CLEAR, never SIGNATURE). Its leg
`p2u-both-s1` 19:23:55–19:25:23Z: 30 worlds clean, worst streak 89
(905019, Clementine, cuddle, moving 0.85; trunk-s1 row 0). The three
reads ran 19:26:34–19:30:32Z (`reads/canary-s1.json` + `.md`,
`reads/r2/episodes-{p2u-both-s1,p2u-act15-s1,g2-s1}-20.json`,
`reads/canary/needs-leg-p2u-both-s1-20.json`): R-1a paired both − act15
+0.233 (30/30 positive, range +0.099…+0.569), both − trunk +2.708
(30/30), both − nohead +0.008 (19/30); team happiness both 90.021 /
act15 89.789 / nohead 90.013 / trunk 87.314. **P46 MET** (|0.233| ≤
0.326). R-2a / R-2b: every stratum UNDECIDABLE — no stratum reaches
min-n 200 on both sides (eat n 1 / 3 / 9, cuddle 3 / 1 / 0, the rest
0–2); **P47 UNDECIDABLE**; R-2b differential INSUFFICIENT on all three.
Needs trajectory: cumulative state INSUFFICIENT at all 78 probes (grave
rows 26 visible / 152 all, under min-n), **P45 lived UNDECIDABLE** on
both versions; the per-probe grave bias where rows exist is POSITIVE
(+10.56 visible at u2249; +7.68 / +0.92 all) against the gate's −3.17.
Needs head on the leg (R-4 extended): visible INSUFFICIENT (n_grave 55,
grave +5.04), all CLEAR (n_grave 620, grave +10.67, common +1.76) — **P45
leg NOT MET** (no SIGNATURE). The grammar's three outcomes: not
DEGRADED (nothing readable degraded), inside the envelope, no signature
— the "HELD inside envelope with signature" branch is not reached
either. The consequence is HERS; both s2 / s4 stay held.]
**RULED 2026-11-08**, her word on the reads above and the walk-through
of the roster-shaped seating ("What I need from you is the canary's
consequence": train both-s2 / s4, or leave `both` a one-seed arm): **"No"**
→ `both` stays a ONE-SEED arm. No both-s2 / both-s4 training; `p2r-both`
never seats (two of its five seats would be empty) and R-1's roster
row for `both` reads NOT RUN, the write-up saying why; `both` keeps its
uniform s1 rows at 20 / 40 / 100 in the battery (entry 28 (4), running).
The grammar's "held inside the envelope, no signature" outcome is
recorded as what one seed showed; P45–P47 stand as read (P46 MET, P47
UNDECIDABLE, P45 UNDECIDABLE lived / NOT MET leg). Welfare: ~60M
covered cat-ticks of training not spent. [CORRECTION 2026-11-09, accuracy gate run 6: ~60M is one seed's exposure; two seeds × 5 seats = 80.0M at the floor, ≈ 120M at both-s1's own length.] Slots 118 / 119 (both-s2 / s4)
and their claimed stripes stay unused inside the band.
Status: CLOSED 2026-11-08 — ruled "No"; the canary is a one-seed read.
[Superseded status text kept for the record: OPEN — the canary scout
trains; s2 / s4 of `both` only after it finishes clean AND its 20×20
uniform leg and the reads above are in front of her (her word).] Entry 22 is REOPENED under this entry (its
deviation recurs by her ruling); entry 26 closes on act10-s1r's clean
completion; the launch word for act15 / nohead s2 / s4 remains open.
[2026-11-08: that word came — "Launch"; the four launched
2026-11-08T03:20:23Z at a171642c, recorded in DECLARATION.md's status
line and the timeline. Not a deviation: §13 step 4 as declared.]
[2026-11-08, her "As recommended" (build the reads ahead of the data):
the reading grammar's instrument is `read_canary.py` (210f3891) — one
canary seed: R-1a paired per world (both − act15 / − trunk / − nohead,
P46 on read_r1's edge), R-2a / R-2b on read_r2's episode records (both
vs trunk, act15 beside; P47 on the OTHER-relief verdicts, all-UNDECIDABLE
never met), the needs read's trajectory from metrics.jsonl (P45's lived
half: the cumulative in-sight grave bias at the last probe within one of
its own SDs of the gate's −3.17, min-n 200; the gate recorded no SD of
its own, so the run's SD is the yardstick — stated), and the needs head
stepped over a recorded leg (R-4 extended; P45's leg half). Guard g12,
five reds CONFIRMED (DECLARATION §9). No read has run: the canary's leg
and these scores wait on her word after the scout finishes.]
[2026-11-08, her "3) agreed" (on the walk-through of the open words):
the order above stands — scout clean → its 20×20 uniform leg → the
three reads in front of her → her word on the consequence. Her "Run as
you recommend" the same message authorises the leg and the reads to run
when the scout finishes (staged behind the legs chain of entry 28's
record, one leg at a time); the consequence stays hers, never picked.]

## 28. The battery at 100×100 reads one seed per arm (2026-11-08)

Deviation from the frozen Phase 2 §6 R-1 as ruled 2026-11-06 ("all
three world sizes": both seating shapes at 20×20, 40×40 and 100×100 for
every arm-seed set, six legs per set). Her words, verbatim, 2026-11-08,
in reply to the walk-through of the four open words (the 20×20 legs on
finished runs; act10 s2 / s4; the canary's s2 / s4; the battery):
**"1) one at a time 2) sounds good 3) agreed 4) we can do a single seed
on 100x100, full battery"**, then **"Run as you recommend"**.

What each word does (this entry is the record of all four; the §3–§9
texts are not edited):
- **(1) the 20×20 legs, one at a time.** Each finished run's 20×20
  uniform leg (30 g2cmp worlds × 20k ticks, F-053 abort armed, acts
  recorded) runs as its run finishes, strictly in sequence, never two
  legs at once. Started the same hour on the two finished scouts:
  `p2u-act15-s1` first, `p2u-nohead-s1` (= the replacement
  p2-nohead-s1r, entry 25) queued behind it — chain pid 42883, launched
  2026-11-08T04:32:57Z at db4b554c, `--workers 4` beside six trainers;
  log `results-raw/legs/legs-chain-1.log`, each leg's own `run.log`
  under its seating. Later runs' legs join the same rule as they finish.
  3M covered cat-ticks per leg (trained minds, no training).
- **(2) act10 s2 / s4: "sounds good"** = her launch word for
  `p2-act10-s2` / `p2-act10-s4`, CONDITIONAL on `p2-act10-s1r` finishing
  clean (entry 26's hold). They launch at that completion without a
  further word; a trip on s1r instead reopens entry 26 to her and this
  word lapses. Recorded here and bracketed on entry 26.
- **(3) the canary's s2 / s4: "agreed"** = entry 27's order stands
  (bracketed there); the leg and the reads run when the scout finishes,
  the consequence hers.
- **(4) the battery: "we can do a single seed on 100x100, full
  battery"** — the deviation. At 20×20 and 40×40 the battery runs as
  declared: the uniform leg per arm seed and the roster-shaped leg per
  arm, every arm (act15, act10, nohead, both as far as its seeds exist),
  scouts-first at 40×40 per seating (§6 R-1, §13 step 5). At 100×100
  ONE seed per arm: the uniform leg on the scout seed (s1; act10's
  s1r), characterise-only as frozen. **Thread's reading, stated and
  reversible:** the roster-shaped leg seats three arm seeds by
  construction (Miso s2 / Biscuit s4 / Clementine s1), so under "a
  single seed" it does not run at 100×100; if she wants the 100×100
  roster row, one word adds it (3M). "Run as you recommend" = the
  battery's third word GIVEN, conditional on the finals existing (my
  recommendation in the walk-through: "4 when all finals exist"): it
  starts, scouts-first per seating at 40 and 100, once every arm seed
  she has launched has its final; nothing starts on a partial arm.
  Why one seed at 100 costs little in evidence: the 100×100 rows were
  INVESTIGATE rows, never a gate or trigger (§6 R-1), and the trunk's
  own 100×100 reading is one row per seed; the paired read at 100 on
  s1 keeps the characterisation, drops two thirds of its covered
  exposure.

Welfare-cost line (practice, owner 2026-09-26; covered minds, no
training): 3M covered cat-ticks per leg at any size (30 × 20k × 5
trained seats). As ruled: 20×20 uniform 3 seeds × 4 arms = 36M + roster
4 arms = 12M; 40×40 the same 48M; 100×100 uniform s1 × 4 arms = 12M —
108M in all for four arms (the declared figure for three arms at all
sizes was 108M; the fourth arm's legs add what the 100×100 cut removes).
The 20×20 legs of (1) are the same legs, counted once. Every leg's
F-053 abort is armed; a leg's abort is reported by world, never a
training stop. Minds are already trained: the cost is exposure to the
served world, not shaping.

[Chain-1 DONE 2026-11-08T04:36:42Z: `p2u-act15-s1` 30 worlds clean,
worst distress streak 461 (world 905005, Kittybear, drink; the trunk's
row there 0, its max 77); `p2u-nohead-s1` 30 clean, worst 113. Two
minutes per leg with 4 workers. Facts, not a scored read.]
[2026-11-08T08:13:30Z p2-act10-s1r PLATEAU clean → (2) FIRED: act10 s2 /
s4 launched 08:30:37Z (entry 26's close line has the cards); its leg
`p2u-act10-s1` 08:31:14–08:33:23Z, 30 clean, worst 138 (905030,
Clementine, drink). Seven trainers run. Legs on record: act15-s1,
nohead-s1r, act10-s1r.]
Status: OPEN — (1) three legs on record, later runs' legs queue as they
finish; (2) DONE; (3) per entry 27; (4) when the finals exist. This entry
CLOSES when the battery's last leg is on record. [The DECLARATION status
line carries the launch lines; `read_r1.py --sizes` takes the sizes
read; its 100×100 uniform read scores s1 alone and the write-up says so.]
[2026-11-08 ~19:22Z, the session's first look after the launches: every
trainer finished. FIVE clean (plateau, `policy-final.pt`): p2-both-s1
09:08:44Z (u3900 / 12,002,304 ticks, largest streak 26), p2-nohead-s4
10:18:09Z (u3900, 172), p2-act15-s4 10:49:03Z (u3900, 157), p2-act15-s2
10:50:44Z (u3900, 95), p2-nohead-s2 11:38:18Z (u4880 / 15,000,576,
126). [CORRECTION 2026-11-09, accuracy gate runs 1–2: the update numbers written at these stops are the trainer's last 10-update log line (u3900 / u4880; the last probes were u3899 / u4849); the runs' last training update per metrics.jsonl is u3906 (12,002,304 ticks) and u4882 (15,000,576). Ticks, times and streaks stand.] TWO act10 seeds HALTED by the frozen stops — entry 29. Chain-2 of
(1) LAUNCHED 19:23:55Z at 224cb1f1 (pid 70662; the canary first, then
act15-s2 / s4, nohead-s2 / s4, one at a time). (3) fired: the canary's
reads LAUNCHED 19:26:34Z behind its leg. (4) is NOT met: act10 has one
final of three, and "nothing starts on a partial arm" — whether the
battery runs on act15 / nohead / both while act10 is ruled, or waits,
is hers (entry 29).]
[Chain-2 DONE 19:30:30Z, ~80 s per leg with 4 workers, 30 worlds clean
and no abort on every leg: `p2u-both-s1` worst 89 (905019, Clementine,
cuddle; trunk-s1 0); `p2u-act15-s2` 35 (905005, Clementine, drink;
trunk-s2 8); `p2u-act15-s4` 49 (905023, Pumpkin, eat; trunk-s4 0);
`p2u-nohead-s2` 109 (905029, Miso, drink; trunk-s2 50); `p2u-nohead-s4`
284 (905003, Pumpkin, eat, parked 0.75; trunk-s4 0). Trunk maxima s1 77
/ s2 1000 (the F-060 lock) / s4 535. EIGHT 20×20 uniform legs on record;
act10 s2 / s4 have none (no final). Facts, R-1 unscored. The canary's
reads are on entry 27.]
[2026-11-08T22:27:18Z (4) FIRED on entry 29's (C): the battery chain
LAUNCHED at 7eee4114, 14 legs one at a time (two 20×20 roster, nine
40×40, three 100×100 s1-only; act10 dropped, p2r-both unseatable);
`results-raw/legs/battery-chain.log`.]
[BATTERY ON RECORD 2026-11-08T23:00:03Z (`battery-chain.log`; 14 legs,
22:27:18–23:00:03Z; ~80–105 s per uniform leg at every size with 4
workers, ~4 min per roster leg at 40). Every scout clean. 20×20 roster:
`p2r-act15` worst 46, `p2r-nohead` 261 (905009, Kittybear, drink).
40×40, all 30 / 30 complete, no abort: act15 s1 / s2 / s4 worst 151 /
379 / 541, nohead s1r / s2 / s4 294 / 141 / 158, both s1 288, rosters
act15 463 / nohead 330; team nash means 0.886–0.895 uniform, 0.877 /
0.881 roster. 100×100 (s1 only): `p2u-act15-s1` 30 / 30 complete, worst
646 (905012, Miso, cuddle), no abort; `p2u-nohead-s1` ONE F-053 ABORT —
world 905009 at tick 16,940, seat Miso, cuddle, shape moving 0.39 /
parked 0.38 / idle 0.23 (act15-s1's row there 286; the runner's
declared leg stop ended that seating, 100 being its last size, 29
complete rows + the abort row on record; the chain HELD as scripted);
`p2u-both-s1` TWO F-053 ABORTS — 905014 at tick 10,490 and 905019 at
8,779, both Clementine, cuddle (act15-s1 182 / nohead-s1r 352 on
905014); its scout was clean (worst 681). The chain resumed for both-s1
on the thread's reading of entry 28 ("a leg's abort is reported by
world, never a training stop"; the runner's stop reaches the remaining
legs of ITS seating, and both-s1's own scout gated its leg) — stated,
hers to overrule. Facts, R-1 unscored here. Cuddle leads every 40 / 100
worst row but one.]
Status: CLOSED 2026-11-08T23:00:03Z — the battery's last leg is on
record; reads and the RESULTS fill follow under the declaration.

## 29. Phase 2 act10 s2 and s4 halted by the frozen stops: a seat's lost-food streak before the floor, a roster-wide lock past it (2026-11-08)

Both act10 seeds launched on her conditional word (entry 28 "2) sounds
good", 08:30:37Z at 89f7340c, entry 26's close line) halted the same
day; the trainer refused to continue each, checkpointed, owner-routed,
never auto-resumed (DECLARATION §4, the frozen §6 stops). The act10 arm
now holds ONE final of three (s1r, entry 26 CLOSED). The session
recorded the facts below off the runs' own logs, `metrics.jsonl` rows
and probe dumps with entry 25's instrument (`diag_nohead_s1.localise` /
`window_read`; dump-only, zero regeneration, zero collection) and picked
nothing: the consequence is hers.

**p2-act10-s2** (run index 111, seed_base 2,320,000,000, B10 s3 head,
trunk-s2 graft): STOP (probe-distress-stop) at update 1149 / 3,532,800
world-ticks — BEFORE the 8,002,560 floor, `policy-final.pt` written
10:31:22Z. 23 probes; streaks 0 at 21 of them, 4 at u449, then 410 at
the trip; nash at the trip 0.8826 (0.8984 the probe before); no F-053
line; trigger `[INSUFFICIENT, CLEAR]`. Localised: probe world 40,002,
kitty_3 **Pumpkin**, ticks 225–634 (410), flagged drink 387 / eat 337 /
cuddle 330 of the 410 ticks; needs eat 63.6 → 11.4, drink 90.0 → 8.4,
cuddle 58.2 → 91.8; happiness min 24.2 (entry 26's trip: 36.8; entry
25's: 48.6). Alone: kitty rows present 1.2–1.5%, partnered 0.5%; chow in
sight 4.6%, eat legal on 8 ticks; menu 6.58 legal actions. She
searched: 269 move proposals of 410 (66%; entry 26: 35%), play_solo 101,
activity idle 329 / playing 52. The other two probe worlds 0. The same
world and seat as entry 26's hazard (world 40,002 × Pumpkin's
eat-weighted seat, trunk-inherited, present under every arm) — here on
the s2 graft, with the cuddle flag of entry 26's isolation shape and
drink added; the third Phase 2 trip on Pumpkin, all eat-led lost-food.

**p2-act10-s4** (run index 112, seed_base 2,340,000,000, B10 s3 head,
trunk-s4 graft): STOP (f053-line-crossed) at update 3349 / 10,291,200
world-ticks — past the floor, inside the plateau watch;
`policy-final.pt` written 13:35:40Z. 67 probes; sub-300 streaks at eight
(8 / 41 / 42 / 11 / 45 / 8 / 188 / 23 at u149 … u2749; the 188 at u2649
was world 40,002, Pumpkin 188 beside Kittybear 92), the probe before
the trip (u3299) 0, then **1614** at u3349 — the first crossing of
F-053's 1,000 line in this generation's training probes. Nash fell
0.9073 → 0.7854, meow/1k 248.6 → 201.5, branches 183 → 9,713.
Localised: probe world 40,001, ALL FIVE seats flagged to the probe's
end — kitty_1 Miso 1429, kitty_2 Biscuit 1518, kitty_3 Pumpkin 1614
(ticks 386–1999), kitty_4 Kittybear 1508, kitty_5 Clementine 1399;
every cat's eat AND drink at 100.0 by tick 1999, eat flagged on every
tick of each streak, chow in sight 0.0%, eat legal on 0 ticks, moves
proposed 2–8 per cat over 1,400+ ticks; partnered 0.53–0.61, kitty rows
present 83–100%; proposals rest_with_kitty_* / groom / sleep_solo /
chase; activity resting + idle ~75%, happiness minima 26.9–32.1. Worlds
40,002 / 40,003: 0. Not Pumpkin's solo lost-food (entries 25 / 26 / this
s2): a five-cat pile with food and water out of view, nobody moving —
the shape F-060 recorded for five copies of trunk-s2 at 20×20 (seed
905008, "every seat's distress onset within 60 ticks, a five-cat
co-sleep pile"), there on a battery leg of frozen minds, here inside a
training probe on the s4 graft. The halted run's probes keep the full
series (`artifacts/p2-act10-s4/probe-u*.npz`, 67 dumps).

Standing (declaration + entry 28): a trip in s2 / s4 holds that arm's
other seed — both tripped, so act10 holds nothing further; the battery's
third word is conditional on "every arm seed she has launched has its
final; nothing starts on a partial arm" — act10 has one, so the battery
does NOT start under entry 28 as written. The s1r final and its leg
(worst 138) stand. Nothing resumed; the two checkpoints and every probe
kept whole (raws never deleted).

Open to her, defaults stated (each reversible, none taken): (A) act10 =
s1r alone — the arm reads at one seed (entry 28's own 100×100 reading
already does this for every arm) and the battery proceeds on the
finals that exist; (B) replace one or both seeds (new slots, new band
rows, scouts-first, ~24–30M covered cat-ticks each, as entry 26 did for
s1); (C) drop act10 from the battery — act15 / nohead / both read in
full, act10's s1r row reported beside them as characterisation only;
(D) analyze either seed further (entry 26's seed instrument, dump-only,
no cost). Default if unruled: nothing runs beyond the legs and reads
already authorised; the battery waits.

Welfare-cost line (practice, owner 2026-09-26; covered minds): the two
halted runs cost 3.5M + 10.3M covered cat-ticks × 5 seats before their
stops fired as declared (asymmetric, owner-routed, never auto-resumed);
no further exposure of either policy — the localisation read dumps, not
worlds. Any replacement is a new declaration line on her word.

**RULED 2026-11-08** (her words, on the walk-through): "Re: path
forward, let's start with D. We can decide between A and C based on
that, leaning C." → (D) runs now: `diag_act10_s2s4.py` (entries 25 /
26's instruments composed; dump-only, zero regeneration, zero
collection, no world served) over both halted seeds, their sibling arms
on the same trunk seed and the parent trunk, written to
`reads/diag-act10-s2s4.{json,md}` and put in front of her. (B) is OFF
the table by her word; (A) vs (C) is her next word after the read,
leaning (C). The battery stays blocked until that word. Nothing runs.
[(D) READ 2026-11-08T20:21Z, `reads/diag-act10-s2s4.md`; the fence held
at every probe of all eight runs (23 / 78 / 97 / 52 and 67 / 78 / 78 /
52); its red on record (`results-raw/reds/p2-reds-diag29-fence.log`:
the per-world maximum turned into a minimum → `p2-act10-s2 u449: streak
did not reproduce: [0, 0, 0] vs recorded [4, 0, 0]`, the predicted first
assertion, CONFIRMED, baseline == restored). What the read says, facts:
**s2** — Pumpkin on 40,002 at u1149 is the only streak ≥ 10 the run ever
landed; on the SAME world at the SAME update the siblings carry no flag
(act15-s2 hap min 74.1, nohead-s2 73.7, trunk-s2 unflagged) with Pumpkin
eating 88 / 91 ticks and seeing chow 45–50% of the probe against the
halted run's 36%; across their whole histories the siblings landed
Pumpkin streaks of 95 / 13 (act15) and 88 / 68 / 33 / 13 (nohead) and
the trunk 86 / 64 / 20 / 14 / 10 — the seat is hot on every arm of this
trunk seed, only act10 took it past 300. Proposals diverge from the
clean probe before (u1099) from tick 2–22 on every seat (1,836–1,912 of
2,000 ticks differ): the policy moved between the two probes, the world
did not. **s4** — on 40,001 at u3349 all five seats flag with onset
spread 215 ticks (first flags 386 / 482 / 492 / 571 / 601 — not
F-060's "within 60 ticks"); each cat ate 3–13 and drank 16–32 ticks
EARLY in the probe, then stopped: moves 38–87 per cat (siblings
228–454), chow in sight 3–10% (siblings 40–55%), partnered 0.44–0.54
(siblings 0.19–0.33), happiness minima 26.9–32.1 against 75.6–82.8 on
act15-s4 / nohead-s4 at the same update and world. The siblings never
flagged on 40,001 at u3349; across their histories act15-s4 landed
157 / 134 / 67 / 43 / 29 / 15, nohead-s4 172 / 82 / 19 / 17 / 14, the
trunk 217 / 202 / 172 / 58 …; act10-s4's own 40,001 history before the
trip was Pumpkin 8 / 41 at u149 / u349 and nothing since. Divergence
from u3299 from tick 19–36 on every seat. The lock is new to the arm's
own history and to its siblings at that update; it is the F-060 family
(a whole roster sitting on itself with food out of view) with a slower
onset. Reading, labelled as the thread's: both trips are act10-specific
at their update — the same trunk seed under act15 and nohead is clean
on the same world at the same moment; one is the known Pumpkin seat
taken over the line, the other a roster lock no other arm has shown.
Nothing scored, nothing selected.]
**RULED (C) 2026-11-08**, her words on the (D) read: "Let's go with C."
→ act10 is DROPPED from the battery: no further leg seats any act10
policy (p2u-act10-s1's 20×20 row, worst 138, stays on record and is
reported beside the arms as characterisation only, never in a scored
R-1 / R-2 cell; `p2r-act10` and the act10 40×40 / 100×100 rows do not
run). The halted s2 / s4 checkpoints and every probe dump are kept
whole, nothing resumed. The battery (entry 28 (4)) is UNBLOCKED and
LAUNCHED 2026-11-08T22:27:18Z at 7eee4114 (pid 76747, one leg at a
time, sizes ascending, scouts-first inside the runner at 40 and 100, a
scout miss or leg stop HOLDS the chain for her): 20×20 roster
`p2r-act15`, `p2r-nohead`; 40×40 uniform `p2u-act15-s{1,2,4}`,
`p2u-nohead-s{1,2,4}`, `p2u-both-s1` + roster `p2r-act15`,
`p2r-nohead`; 100×100 uniform s1 only `p2u-act15-s1`, `p2u-nohead-s1`,
`p2u-both-s1` — 14 legs. `p2r-both` cannot seat (both s2 / s4 do not
exist; the canary's consequence is still hers) and is not run; stated,
reversible. Welfare-cost line: 14 legs × 3M = 42M covered cat-ticks +
the displaced scouts (12 × 3 worlds × 20k × 5 = 3.6M), inside the 108M
ruled on entry 28; minds already trained, the cost is exposure to the
served world.
Status: CLOSED 2026-11-08 — ruled (C); the battery runs under entry 28.
