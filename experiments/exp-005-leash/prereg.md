# exp-005: the leash dose-response (pre-registration)

**FROZEN at first collection run (2026-08-15; owner's "do it" on
ROADMAP v2 phase 0 track 3).** Deviations append-only, D-numbered.
Findings relied on: F-007 (BC init necessary), F-011 (no per-seat
reward terms — the leash is a constraint, never an objective),
F-012 (fingerprints measured in the demonstration composition).

## Question

Does clone-then-leash-finetune preserve a durable, VISIBLE
personality? Specifically: map fingerprint retention and welfare
recovery as a function of the FINAL KL-leash weight β∞ — the
never-annealed-to-zero region our recipes have never visited.

## Arms

The exp-004 A1 recipe verbatim (train_attn_ppo fork) with ONE
change: kl_beta anneals from β0=0.5 to **β∞** (not 0) over the
first 20%, then holds. β∞ ∈ {0 (control — the known regime),
0.05, 0.2}. Two RNG seeds per arm (the lottery is real). Policy =
EntityPolicy (attention, v3-servable); init = the playful clone
(below); anchor = the same clone, never updated.

## Demonstrations & clone (the anchor)

Scripted `playful` at Biscuit's seat among three `needs_driven`, on
the served world config (current traits — this anchor is
METHODOLOGICAL and disposable; production lineage anchors are
re-collected after the phase-1 trait rebalance, per the
anchors-follow-surfaces rule). bc-collect, 100 rollouts × 8,000
ticks, seed base 856001 (collection band). Clone = train_attn_clone
recipe on the playful seat's rows only (kitty id 2), val split by
rollout.

## Frozen fingerprint metrics (defined BEFORE training; measured on
greedy rollouts in the DEMONSTRATION composition — subject at
Biscuit's seat among three needs_driven — probe band 820001–010 ×
10,000 ticks, for: scripted playful, the clone, and every arm)

1. **play_share**: subject decisions in the play/chase menu group
   (indices 18–32) ÷ all subject decisions.
2. **bug_over_meal**: among subject decisions where Eat AND at least
   one critter action (ChaseCritter*/PlayCritter*) are both legal in
   the mask, the share choosing a critter action.
3. **duet_initiation**: subject PlayKitty* choices per 1k decisions.
4. **time_near_critters** (trajectory-level, aimed at the
   state-visitation failure mode): share of subject ticks with a
   critter within 2 tiles (privileged positions).
5. Welfare: subject + team mean happiness, same rollouts.

## Registered hypotheses

- H1: β∞=0 collapses the fingerprint (play_share falls >50%
  relative to the clone's — the sunbeam/want-word erosion pattern).
- H2: fingerprint drift decreases monotonically in β∞.
- H3: welfare recovery (vs the clone's level) decreases in β∞ — the
  trade is real and the curve locates its knee.
- H4 (the state-visitation risk, F-012-adjacent): if a β∞ preserves
  decision-level metrics (1–3) but time_near_critters still
  collapses, the leash binds decisions, not trajectories — a
  registered failure mode, not a surprise.

No seating gates — nothing seats from this experiment. Its output
is the dose-response curve and the leash doctrine for the phase-1
lineage generation.

## Bands & instruments

Collection 856001+; training episode seeds 1M+ (recipe standard);
fingerprint probes 820001–010. Instruments: bc-collect,
train_attn_clone, train_attn_ppo fork (β∞ patch), fingerprint probe
(this directory). Horizon/world/roster/company stated above (F-009).

## Deviations

(append-only after freeze)

**D-001 (2026-08-16, owner-directed extension).** Two additional
dose arms, β∞ ∈ {0.03, 0.04}: recipe, anchor, seeds {1, 2}, and
fingerprint probe identical to the frozen arms — only the held β∞
differs. Motivation, recorded before any extension arm runs: the
seed-1 curve showed a strongly favorable exchange from 0.2 down to
0.05 (+6.5 subject happiness for flat decision metrics), and the
owner directed sampling just below 0.05 to test whether the trend
continues ("B<0.05 may continue the trend of elevated welfare for
disproportionately low character trade off"). Scope guard: the
frozen arms, hypotheses, and metrics are untouched; H1–H4 verdicts
are computed on the original {0, 0.05, 0.2} × 2-seed design, and
the extension arms enter the dose-response curve descriptively.
Known limit, stated at registration: {0.03, 0.04} samples only the
top of the (0, 0.05) interval — if character holds there, the
collapse boundary remains unlocated (acceptable: the objective is
choosing an operating dose, not mapping the cliff). Queued behind
wave 2 on the same machine.

**D-002 (2026-08-16, instrument use outside the design + §9.6 trip).**
The exp-005 trainer gained a `--scratch` mode (random init, KL
identically 0, recipe otherwise held) and ran ONE seed as the F-007
re-verification control on the owner's word. NOT an exp-005 arm: no
exp-005 hypothesis reads it, and it enters no dose-response table.
Recorded here because the trainer is this experiment's registered
instrument and the run tripped the recipe's §9.6 stop rule, which
demands an entry: welfare < 0.5 on three consecutive probes at update
149/6510 (nash 0.70 at init → 0.36, entropy rising 1.69 → 1.90),
checkpointed and stopped. Disposition: the trip IS the result —
finding recorded under F-007 in FINDINGS.md; no rerun, no stop-rule
override, checkpoint retained at artifacts/scratch-A1-s1/ (local). No
fingerprint probe (there is no final artifact; the collapse is the
evidence).
