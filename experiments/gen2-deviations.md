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
