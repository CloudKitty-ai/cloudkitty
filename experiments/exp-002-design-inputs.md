# exp-002 design inputs — carry-forward register

Standing inputs for the next training generation, collected before its
prereg exists. When exp-002's `prereg.md` is written, each item here is
either adopted (and cited), consciously rejected, or deferred — nothing
silently dropped. Companion to `FINDINGS.md` (read that first; F-ids
cited here are load-bearing).

## 1. Preserve the meow behavior (owner priority, 2026-07-31)

s6's use of the meow channel is a valued feature of the deployed model
("I really like that feature") and must survive retraining. The facts:

- **Base rate is 1/9**: across nine Arm 2 seeds trained identically, s6
  is the only meower. Scratch retraining with few seeds is a bad bet.
- **Nobody scripted listens** (verified 2026-07-31: nothing under
  `crates/cloudkitty-core/src/behavior/` reads `recent_meows`; scripted
  cats emit but never hear). The only ears in the world are policy
  digests. Meowing therefore pays only in worlds with ≥2 policy kitties
  (or in self-play training, where all siblings hear) — in today's
  1-policy soak it is pure ornament.
- **The water lesson cuts both ways** (see BACKLOG "Rethink how water
  works"): imitation copies style, RL keeps what pays. A behavior with
  no reward backing survives only as cheap drift; s6 meows at 0.1% of
  turns, cheap enough to drift. Whether it is instead *functional*
  (copy-to-copy communication learned in self-play) is unresolved.

**Gate before exp-002 design: run the digest-zeroing test** (replay s6
with meow-digest features zeroed vs as-lived, diff the actions).
Communication vs ornament decides which preservation lever matters:
functional meowing is an attractor that re-emerges under self-play;
ornamental meowing must be carried deliberately.

> **GATE RESOLVED 2026-07-31 — s6 LISTENS**
> ([results/meow-listening-2026-07-31.md](exp-001-bc-mappo/results/meow-listening-2026-07-31.md)):
> silencing the digest changes **8.18%** of digest-active decisions
> (10,213/124,838; 7.7–8.6% across all 10 seeds). Flips are coherent:
> hearing pulls s6 toward play/chase (39.9% vs 15.2% silenced) and
> attending-idle (20.2% vs 0.2%); silenced it would sleep/groom. The
> gloss: Biscuit meows WantPlay, Miso answers. **Speak and listen are
> both demonstrated — the channel is functional communication**, so
> preservation upgrades from "carry a lucky quirk" to "keep a working
> behavior with reward backing." Levers below stand; selection is now
> the backstop, not the main hope. Caveat: 8.18% is marginal decision
> change in the scripted served world (mostly one playful emitter);
> welfare value of listening and responses to the other four kinds
> remain unmeasured.

> **SECOND SPEAKER FOUND 2026-07-31 (F-012, pair-screen)**: s3 —
> silent in every solo measurement — emits FollowMe beside s6.
> Channel use is context-dependent; the 1/9 "meower base rate" is a
> solo-context floor. Consequences for the levers: channel-use
> selection (lever 5) must screen candidates *in policy company*;
> the two-policy served world (lever 3) already carries two-way
> traffic (s6: Purr/WantDrink; s3: FollowMe) before exp-002 begins.

Preservation levers, strongest first:
1. **Warm-start from s6, not scratch.** Issue #79's shape A (menu row
   38 keeps its slot, no codec bump) was chosen to keep s6's artifact
   loadable precisely so exp-002 can fine-tune. Existing behaviors are
   sticky under PPO unless the new engine actively charges for them.
2. **#79 raises the channel's value**: deliberate purrs go from
   two-thirds-swallowed (34.3% audible, self-collision with the
   spontaneous motor) to a working action. More function = more reward
   backing = self-sustaining behavior.
3. **Second policy seat** (already roadmapped): gives meows a real
   listener in the served world for the first time.
4. **Seed the imitation prior**: include s6 rollouts in exp-002's BC
   data. bc-v1 contained essentially no meow labels (clone meow
   accuracy 0.000) — meowing had to emerge from nothing; next time it
   shouldn't have to.
5. **Select for it, officially**: prereg channel-use as an explicit
   secondary selection criterion. Picking s6 "because I like the meows"
   was already selection; write it down. At the raw 1/9 rate, 12
   scratch seeds give ~76% odds of ≥1 meower; warm-started seeds start
   from a meowing parent.

## 2. Purr engine parameters open for rethink (owner, 2026-07-31)

Alongside #79's deliberate-purr reinstatement, the spontaneous purr's
tuning is on the table: motor `cooldown_ticks` (30), duration draw
(`min_ticks`/`max_ticks` = 6–15), and the earned rule itself
(`happiness > thresholds.purr || rose`, `world.rs` purr_phase — note
the `rose` clause dominates in a healthy world, so threshold changes
alone do ~nothing; analysis 2026-07-31). Interplay to respect: the
spontaneous motor's cadence is what swallows deliberate purrs, so
quieting it unmasks the learned channel — but purr frequency is also
demo charm, so there is a floor on how quiet the meadow should get.
Fold into the #79 spec conversation: "what should each purr system
mean once both exist?" One engine batch, one recertification.

> **RESOLVED in spec 022 (Product, 2026-07-31; final numbers from the
> batch handoff).** Duration 8–13; flat `cooldown_ticks` retired for a
> **per-end uniform factor draw 1.75–2.75** (each rest = factor × the
> finished purr, ceiling-rounded) → ambient duty ≈ 1/(1+2.25) ≈
> **30.8%**. This supersedes the in-chat flat 2.5×/28.6% — midpoint
> 2.25 purrs slightly more; inside the owner's stated ≤1/3 envelope,
> and the draw gives the meadow an organic rhythm instead of a
> metronome. The **earned rule stays verbatim**, now one definition
> for both origins (`Kitty::purr_earned`) — deliberately scoped OUT
> of 022, because the tuning depends on it: the constant duty cycle
> holds only because `rose` re-earns instantly at rest expiry, and
> the deliberate purr's mask gate keys on the same rule. Any future
> earned-rule change must re-derive both the ambient duty cycle and
> the row-38 gate — treat the rule as pinned by 022's Assumptions,
> not still open. (The inert Purr message-cooldown stamp is DELETED
> by the batch — spec 023 removed its last reader.)

## 2a. Meow cooldown retired at engine level (owner decision, issue #84)

Owner-approved 2026-07-31: the engine stops enforcing meow cooldowns on
agent meows (the silent swallow was illegible and wasted turns; cooldown
15 > window 10 forced dead air). Scripted behaviors keep a voluntary
courtesy cooldown at 10 via their existing `can_meow()` checks (both
needs_driven and playful). Constant deliberate purring is endorsed
(turn cost + earned gate + one announcement per phase are the brakes).
Full design and pins in issue #84. **Timing RESOLVED: #84 became spec
023 and rides the 022 batch** (branch `022-deliberate-purr`): engine
never blocks a meow ("manners, not law"), served `courtesy_ticks = 10`
(= digest window), `urgent_courtesy_ticks = 5`, both behavior-consulted
only. Standing obligation: the spam backstop for learned agents becomes
*economics under cooperative team reward* — any per-kitty or
competitive reward design must revisit before training.

Experiments carries from the batch handoff (2026-07-31):
- **Forensics contract changed**: pyo3 `recent_meows()` now streams
  every emitted meow (per-tick repeats legal, bounded only by the
  window), and a Purr entry no longer implies a motor start (motor
  silent at `announce_probability = 0`; Purr entries ≈ deliberate).
  Pre-022 stream-derived baselines are dead for cross-engine
  comparison: the 36:1 reflex:deliberate ratio, 34.3% audibility, and
  the 0.101% meow rate are old-engine numbers. `forensics_replay.py`'s
  set-dedup logic survives as-is; its meow-collection comment and any
  rate interpretation get swept at recert setup.
- **`configs/cloudkitty-24x24-screen.toml` migrated values-preserved**
  on the batch branch (courtesy 15/5 kept from the capture; pinned
  `cooldown_factor 2.857143` = 30/mean(6..15), preserving the captured
  ~25.9% duty in expectation; rest *shape* now proportional, which no
  migration can undo). Kept as the historical capture — its purpose
  completes when `cloudkitty.toml` goes 24×24 in the same batch; the
  recert measures the served config, not this file.
- `cloudkitty16.toml`/`cloudkitty48.toml` removed by the batch (copies
  in `worlds.backup/`); verified nothing under `experiments/` or
  `evals/` references them.

## 2b. Wet-fur engine change rides exp-002's generation (owner-picked design)

Full design in BACKLOG "Rethink how water works for learned cats" —
that entry is the source of truth; this section records only what
binds exp-002's design (ported 2026-08-01 per the register rule):

- **Engine batch fixed by owner 2026-08-01**: `elements()` pyo3
  accessor + the wet-fur bath cost (`water_bath_gain = 1.5` starting
  dial, bath<50 safety clamp) + the **chase sidestep** (BACKLOG
  "Chases route around friends", approved into this batch 2026-08-01;
  `chase_patience_ticks` re-baseline rides along). **No schema changes
  this generation** (protects the warm-start-from-s6 lever; the policy
  already observes water slots, own bath need, and own traits — the
  cost is learnable from the existing 182-dim vector). Client
  (parallel, non-blocking): swim animation; the per-kitty
  brain-indicator toggle is owner-deferred to BACKLOG. The Cuddle
  pinned-streak "fix" is RETIRED (premise falsified — spec 021,
  docs/cuddle-relief-semantics.md); what rides the batch instead is
  that doc's **welfare ↔ action::validate equivalence guardrail test**
  (owner call, 2026-08-01).
- **Family must vary bath rise rates** across kitties, or the policy
  memorizes a constant instead of learning trait→cost.
  **TOOL READY 2026-08-02** (family-gen v3, `experiments/tools/family-gen`):
  roster stratified 3/4/5 per variant (exact ⅓ coverage — roster-3 is
  the only empty-slot shape, F-010), every kitty gets an explicit bath
  override spanning ratio 0.5–2.0×, `[water]` pinned into variants
  (`--water-gain` = the prereg's dial, default 1.5). Base
  `training.toml` untouched (exp-001's registered artifact). The
  *frozen* family (N, seed, dial) is generated at prereg time.
  Consequence for the trainer: **global-state dim varies with roster**
  (32/kitty; 133 floats at roster 3 vs 197 at roster 5) — the exp-002
  critic must pad or bucket. Obs stays 182 on every roster (verified
  in ParallelEnv; dropped ids simply vanish from the agent list).
- **Final gain value is a prereg'd exp-002 tuning decision**,
  calibrated by seating the water-indifferent s6 on a wet-fur build
  and measuring welfare delta per crossing (needs `elements()`).
  **CALIBRATED 2026-08-02**
  ([results/water-calibration-2026-08-02.md](exp-001-bc-mappo/results/water-calibration-2026-08-02.md)):
  at the shipped 1.5 dial the frozen policies show **no avoidance —
  a groom-loop equilibrium** (occupancy up to 9.3–9.5%,
  grooming-on-water doubled; the success signature is a training
  outcome). Welfare price: paired ΔNash **−0.0014** (t ≈ −4.2,
  9/10 seeds), ≈ −0.06 reward-units per crossing. Clamp healthy
  (max bath 57.1 vs safeguard 75); Article I drinking unharmed.
  The prereg picks the dial with this as its measurement.
- **Pre-change baseline is a now-or-never measurement**: quantify s6's
  current water behavior (wading/lounging occupancy) before the engine
  changes — post-022 stream-baseline lesson applied prospectively.
  **RECORDED 2026-08-01**
  ([results/water-baseline-2026-08-01.md](exp-001-bc-mappo/results/water-baseline-2026-08-01.md)):
  agents occupy water 8.28%/7.87% of ticks vs scripted 1.40–1.74%,
  incl. sleeping+grooming in the pond; ~21–24% of agent drinking is
  on-tile (Article I exposure, judged benign under the clamp). The
  batch is UNBLOCKED on Experiments' side.
- **Distress hygiene**: the clamp guarantees no voluntary swim can
  cross safeguard/distress lines — certification hygiene by
  construction; spec should carry an executable guard.

## 2c. Mixed-population training (owner-directed, 2026-08-01)

Test the impact of **training with scripted teammates vs. pure
self-play** as explicit compared conditions — not a single chosen
recipe. Prior arms trained pure self-play and deployed into scripted
company; that transfer gap is implicated in both F-010 (roster-OOD
catatonia) and F-012 (latent channel use). Evaluation for every
candidate covers **three deployment shapes**: 1 (new) agent among
scripted kitties, partial-agent worlds (mixed policy + scripted, incl.
seats beside s6), and full-agent worlds. Interplay with §1: channel
use must be screened in policy company (F-012), so the eval matrix
above doubles as the channel-use screen.

## 3. Standing carries (recorded elsewhere; do not re-derive)

- **Roster 3–5 coverage in the training family** or absent-slot
  masking — F-010 is the bill for family-v1's deferral (collection
  decision 14). Primary robustness target.
- **Screen candidates on every roster the deploy surface can present**
  (3/4/5 kitties), certify-length, per F-010.
- **One-engine rule**: exp-002 trains *and* evaluates on the post-#79
  engine — never split across engine versions.
- **World geometry**: served world moves to 24×24 before the recert
  (owner intent restored; family-v1 already spans 22–26, so the family
  centers on the served size for free).
- **Heterogeneous policy pairs are unmeasured**: extend
  `forensics_replay.py` to per-seat policies; screen pairwise + the
  exact demo roster before any mixed-model world.
- **Meow listening is unverified** — the §1 digest-zeroing test doubles
  as this check.
- **Latency residual dissolved** on the served world (deviation 31
  re-measure) — do not carry it as a target; roster-OOD fragility is
  the target.
- **FINDINGS re-verify triggers fired by the 024 batch — RUN
  2026-08-02, landscape inverted (F-013)**: the served 24×24 world
  now carries a replicated cooperative band (k ≈ 230–330, S(.998) ≈
  0.09–0.11) while the frozen gym's paired-seed signal fell sub-floor
  (sidestep dissolved its stall-queueing advantage). F-003/F-005/
  F-006 superseded by F-013
  ([results/twin-probe-2026-08-02-post024.md](exp-001-bc-mappo/results/twin-probe-2026-08-02-post024.md)).
  Prereg consequences: **training-world choice reopened** (served-
  centered family is the evidence-backed default; slimmed post-024
  world search recommended before freezing); γ sweep {0.995, 0.998}
  stands with 0.9985 as a conditional arm only if the chosen world's
  band peak lands past k ≈ 500; class-conditioned priors (play/chase
  3.6×) must be re-measured on the chosen world; certification on the
  served world is no longer credit-blind.
  **SEARCH RUN 2026-08-02 (F-014)**: the served world wins as it
  stands — no searched knob beats it at 150-world power (3rd
  independent replication S(.998) ≈ 0.09; gym 3rd sub-floor batch;
  scarcity/tempo now hurt). Family base = served shape, family-gen v3
  jitter as the envelope; the 5-kitty base variant for roster
  stratification halves S (0.090 → 0.041) — a quantified
  signal-for-robustness trade the prereg owns explicitly. Probe
  claims on this engine need 150+ worlds (F-004 addendum).
