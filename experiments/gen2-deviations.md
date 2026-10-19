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
