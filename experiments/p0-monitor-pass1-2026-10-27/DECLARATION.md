# P0 behavioural-degeneracy monitor — pass 1, archive only (declaration 2026-10-27; DRAFT for the owner's ruling)

Owner's words. The Professor's preregistration framing
(`~/ai/professor/notes/for-experiments-behavioral-monitor-prereg-framing-2026-10-23.md`,
sha256 7c7e888e105e3b0e0fb9764925ed0c56b911b7942b55ac7de97fa857663ae466,
178 lines, 9,055 bytes as received 2026-10-26; held by her since
2026-10-25 "until we figure out the mini-models", released on her word in
the Professor session, "Relay the P0 entity rate monitor info to
Experiments") was put to her in this session with two calls — kick off
the pass-1 declaration, and run it in the gap while Product builds the
needy set (spec 067), before the mini-friend Phase 2 declaration. Her
words, 2026-10-27: "Yes to both". This document is the declaration she
rules on; the Professor's note is its input, not its text. The 1.0
positioning ruled the same day ("Correct, positioned around the
instrument stack.") makes this read the headline the release waits for.

Her addition before ruling, 2026-10-27, verbatim: "Before the four calls,
there’s one other potential source (the pre-“wait for me” teacher config
regularly ended up in lockstep on approach)". Folded in below: §2's July
pair, §3's movement alphabet (the source showed that the first draft's
action alphabet erased move direction, and re-deriving the estimator
orders for the new alphabet corrected the first draft's), §12 call 5.

**Status: DRAFT; all five calls RULED 2026-10-27 (§12). Open with her
the same day, verbatim: "Do we need to run P0 pass 1 now? I was thinking
we wait until we get gen 2 figured out. Pros and cons of waiting?" Nothing below runs until she rules. No number from this
arc exists.**

Publication track P0 (her word 2026-10-23: "Let's try to make this our
first paper"): every headline number is a candidate paper number, so
three or more seeds wherever one is cited. Here "seeds" are of two kinds
and both are stated per number: the world seeds behind an episode set,
and three declared random splits of the healthy worlds into calibration
and test (the band's seeds).

Welfare-cost line: 0 new covered cat-ticks. Pass 1 reads arrays already
on disk; no weight is changed (call 3's replay only reads committed
weights over recorded observations; no world runs), no covered mind
experiences anything. One
scripted-only regeneration is proposed (§2's July pair, §12 call 5):
scripted kitties of the July engine, exempt under the welfare practice,
their distress reported, not gated. Pass 2 (fresh labeled episodes or a
transfer environment) is a separate declaration on her word.

## 1. What is being asked

A monitor on realized action streams, gated by the welfare register:
does a kitty's recent behaviour carry the signature of degeneracy — a
loop or stuck state (low entropy rate, needs-blind), dithering (high
entropy rate, needs-blind), or lockstep (one kitty's actions determined
by another's with neither's needs improving) — before the needs trigger
fires, and does a monitor calibrated on healthy behaviour plus two of
those patterns catch the third unseen? The monitor is not a reward term,
not a training change, never a stop on its own (§6).

Four questions, answered in this order:
1. **Bands.** What do the monitored quantities look like on competent
   teacher behaviour with good welfare, per window, and how wide are the
   bands?
2. **Recall and latency.** On the labeled unhealthy episodes the archive
   holds, does the monitor flag them, and how many ticks before the
   needs trigger?
3. **False positives.** How often does the monitor flag held-out healthy
   teacher worlds, and healthy certified policy worlds, against a budget
   declared below?
4. **Leave-one-pattern-out** (the headline). Calibrated on healthy plus
   two patterns, does it catch the third?

## 2. The archive (inventory 2026-10-27, read-only; the facts a design claim rests on)

Five stream formats hold per-tick behaviour; only three carry what the
monitor needs (an action per kitty per tick, the needs vector, and
positions):

- **Collector rollouts** (`experiments/tools/bc-collect`): `label.npy` is
  the APPLIED action as a codec index (`main.rs:4-8`); `state.npy` is the
  pre-tick global state with per-kitty needs (6), happiness, position,
  the 7-way activity, partner and distress flags (`global_state.rs:10-19`;
  v2 is 40 floats per kitty). Alphabet 35 on Gen 2 (codec v2 at kitty
  slots 4, critter slots 2; `codec.rs:305-308`), 39 on Gen 1 fog, 34 on
  codec v1.
- **Seating streams** (`streams-<seed>.npz`): `needs (T,R,6)`, `pos`,
  `activity` (7-way, end-of-tick, each scene's last tick dropped —
  `seating-analysis-g2-2026-10-21/RESULTS.md:292-305`), `act (T,R)` the
  35-way PROPOSED menu action (−1 on scripted seats), and in the
  `applied/` directories and later arcs an exact 11-way APPLIED action
  (move, rest, sleep, groom, eat, drink, chase, play, purr, meow, idle;
  no move direction).
- **PPO probes** (`artifacts/*/probe-u<N>.npz`, gitignored): `act` the
  PROPOSED greedy action, `obs` with the deciding cat's OWN needs only,
  no positions, no global state (`observe.rs:12-17`). Single-kitty
  quantities only.
- **Cert-harness evaluation rows**: one aggregate row per world, no
  per-tick arrays. Not usable here; their `aborted_streak` records name
  worlds whose streams mostly do not exist.
- **Live polls**: subsampled; not usable.

Sources, by label (paths under `experiments/`; counts are worlds × ticks
× kitties unless stated):

| label | source | alphabet | needs | positions | size |
|---|---|---|---|---|---|
| HEALTHY teacher | `gen2-collection-driver-2026-10-14/results-raw/full-100` (five teacher seats; applied + proposed) | 35 applied | yes | yes | 100 × 20,000 × 5 |
| HEALTHY teacher, exact applied | `seating-analysis-g2-2026-10-21/results-raw/applied/scripted`; `play-decomposition-g2-2026-10-21/results-raw/C2` | 11 applied | yes | yes | 5 × 20,000 × 5 each |
| HEALTHY certified policy | `seating-analysis-g2-2026-10-21/results-raw/g2-rot1..5`; `minifriend-phase1-2026-10-22/results-raw/L` (rot2) | 35 proposed (+ 11 applied in `applied/g2-rot2` and L) | yes | yes | 25 × 20,000 × 5; 10 × 20,000 × 5 |
| LOCKSTEP / pile | `exp-006-character-gen/traces/` (19 traces; hand labels fixed in `collapse-detector-v0/prereg.md:50-70`: must-fire 880030, 880008, 880015; should-fire 880017; must-silent ×14; report 880013); `gen2-cert-battery-2026-10-20/diag-s2-905008.npz` (five-cat co-sleep pile, ticks 16,000–18,300, `RESULTS.md:46-73`) | v1 codec on policy seats (`chosen`), scripted seats without actions; 35 proposed | yes | yes | 19 traces; 1 replay |
| WRONG-NEED fixation ("water parking") | `seating-analysis-g2-2026-10-21/results-raw/g2-rot1/streams-905002` (Clementine, 13,987–14,107), `g2-rot1/streams-905005` (Clementine, 1,503–1,586), `g2-rot3/streams-905002` (Pumpkin, 13,448–13,541); `diag-s7-part1.json`, `RESULTS.md:450-498` | 35 proposed | yes | yes | 3 spans |
| LOOP / catatonia | `exp-001-bc-mappo/artifacts/arm2-g0p998-s2/forensics-seed8*.npz` (idle catatonia from t ≈ 1,541, `collapse-forensics-2026-07-30.md:43-57`; seed 4 and s6 seed 8 the healthy controls) | v1 applied | **no** (one any-distress bit) | yes | 1 episode + 2 controls |
| TRAINING COLLAPSE halted by the probe-distress stop | `gen2-trunk-training-2026-10-18/artifacts/ppo-g2-trunk-s{3,5,8,11}/probe-u*.npz` (s3 localized: world 40002, kitty 1, ticks 820–1,136, `artifacts/diag-s3.json`; s8 streak 392 on 40002 at u299; s11 streak 371 on 40003 at u99; s5 at u199) | 35 proposed | own needs only | **no** | 4 runs × 3 probe worlds × 2,000 × 5 per checkpoint; earlier checkpoints on disk (s8: u49 … u299) |
| LOCKSTEP on approach, scripted (not in the archive; regenerable, §12 call 5) | the July pair below: edc7d332 vs d91b7c86, paired world seeds | July `Action` → A9; M5 from positions | yes | yes | 30 × 5,000 × 4 per commit |

Not used, and why: `heads-pass1/` (never read); a message-channel
lockstep in the Gen 1 shakeout smoke (`fog-gen1-shakeout/PREREG.md:156-161`,
kitty 2 / kitty 4, ticks 456–486; both alphabets below exclude the
message head); the 4k rungs marked
POISONED FOR TRAINING (their value targets, not their behaviour streams,
are the poison — `gen2-trunk-training-2026-10-18/MITIGATION.md:362-372`;
left out anyway, no label needs them, and not healthy material: the ε
rungs saved state and reward only, no actions, under the BC clone with
ε-random actions, and the initial-needs rungs start from drawn wide or
grave need levels; call 4 RULED no); battery post-stop rows (citation
open, deviations entry 4(a)); `beam-world-screen` tier5-stale; eps01 /
eps03 (no action labels). What does not exist: machine-readable hand
labels (every label above is prose in a RESULTS, prereg or diag file,
transcribed into this arc's `labels.json` before any read, with the
file:line it came from); streams for 15 of the 17 battery aborts; any
LLM-seated episode; policy logits for the PPO probes (so the policy-
entropy baseline is not reproducible in pass 1).

**Lockstep on approach, scripted — her addition; not in the archive,
regenerable.** Spec 012 ("Wait for me!", d91b7c86, 2026-07-20 21:13
−0600) fixed a period-2 corner orbit between mutually approaching
kitties: each stepped toward where the other had just been, at Manhattan
distance 2, for as long as the urgent-meow lottery stayed quiet (145
ticks in the verified silenced reproduction,
`specs/012-approach-etiquette/research.md:5`). The same commit
de-synchronised a lockstep convoy sidestep (FR-008), and a head-on
corridor mirror had been fixed by spec 010 (d614a22d) an hour earlier
(`crates/cloudkitty-core/src/behavior/mod.rs:20-31`). No archived stream
shows it: the RL encodings arrived the next day (spec 014, 90cf2ae3,
2026-07-21), the collector on 2026-07-27 (9aee1e28), and every stream on
disk was recorded with the yield. The only pre-fix data on disk are six
world snapshots in the untracked `worlds.backup/` (2026-07-18 … 20; state
plus a ring of the last 1,000 activity spans, no movement history),
which are not streams. The pattern is cleanly regenerable as a natural
experiment: the fix commit's diff is the yield, FR-008's sidestep
de-synchronisation and the new word (`needs_driven.rs`, `selection.rs`,
`meow.rs`, a test), so the same worlds run on edc7d332 (the commit
before it) and on d91b7c86 differ by those alone. Proposed (§12 call 5;
pass 1 stays archive-only without her word on it): that commit's
default world (32 × 32; Miso, Pumpkin and Kittybear needs_driven,
Biscuit playful; the same six needs as today), world seeds 1 … 30,
5,000 ticks each, both commits, paired by seed; a per-tick dump of
positions, needs, the applied `Action` and the activity by a harness
under this arc's directory, built against each commit's core crate by
path (`World::generate` and `World::tick` exist at both), no engine
file edited; scripted brains only. The post-fix runs are this source's
own healthy band (§4: bands are per era). Label rule, declared now and
mechanical: an APPROACH ORBIT is a pair at Manhattan distance exactly 2
on ≥ 10 consecutive ticks, both kitties' applied action a `Move` on
every one of them and each kitty's position at t equal to its position
at t − 2. On the post-fix runs the rule is expected to find none (spec
012's SC-001: the reproduction world resolves within 6 ticks in 100% of
runs, `specs/012-approach-etiquette/spec.md:161-162`); any it finds are
reported, labeled like the pre-fix ones, and their windows kept out of
the band. Convoys (the same `Move` direction on ≥ 10 consecutive ticks
at Manhattan distance ≤ 1) are counted on both commits, report-only and
unlabeled. This would be the archive's only SCRIPTED unhealthy source,
which is the point: it tests whether the pairwise quantity reads the
pattern rather than the seat type.

Two facts that shape the design: the healthy episodes are overwhelmingly
scripted-teacher and the unhealthy ones overwhelmingly policy, so a
separator could be learning "policy vs teacher" instead of degeneracy —
hence the healthy certified-policy false-positive read (§5, question 3)
as a required column, not an option; and the alphabets differ by source,
so every band is per alphabet and per engine era (§4), and no number
is compared across alphabets or eras.

## 3. Quantities (per kitty, sliding windows; the Professor's §1–§2 as operationalised here)

Alphabets, declared once:
- **A9**, what the kitty does: move, rest, sleep, groom, eat, drink,
  chase, play, idle. From a codec index (34, 35 or 39 entries) by that
  era's codec entry table, built by the instrument from the code and
  asserted to cover every entry; from the 11-way applied action by name
  (purr and meow → idle); from the July engine's `Action` by variant
  (`Purr` and `Meow` → idle: a turn that neither moves nor starts an
  activity). Where a stream holds both, the APPLIED action is the
  monitored one and the proposed a reported second column.
- **M5**, how it moves: north, east, south, west, or not moving — the
  realised step, from consecutive positions (de-normalised and rounded
  where the state stores fractions; no change is "not moving", a blocked
  move included; a change of more than one tile is refused except at a
  declared episode reset, and no window spans a reset). Every source
  with positions has it, the 11-way streams and the scripted seats of
  the exp-006 traces included. The PPO probes have no positions; there
  M5 is the proposed `Move` entry's direction, stated as proposed.
- **N7**, the needs symbol: the identity of the highest need if it is
  at or above 45 (the rider (b) lower edge), else "none" — six needs
  plus none, the same six in every era.

Why M5 (her addition, §2): every movement loop — the July corner orbit,
a corridor mirror, the exp-006 "pacing near resources without consuming"
(`exp-006-character-gen/results/r5-forensics-2026-08-20.md:14`) — is a
pattern in move direction, and A9 writes every step as the same symbol.

Resolvability, the framing's "many times" made a number: a plug-in table
of C cells is read only at windows W ≥ 10 × C, C counted on the declared
alphabet sizes (never on the symbols a window happens to use, so no
order is chosen from the data). Windows W ∈ {100, 300, 1000} ticks,
stride 100.

| quantity | cells | W = 100 | W = 300 | W = 1000 |
|---|---|---|---|---|
| H(A9), marginal entropy | 9 | read | read | read |
| H(M5), marginal entropy | 5 | read | read | read |
| h1(M5) = H(M_t \| M_t−1), entropy rate | 25 | — | read | read |
| h1(A9), entropy rate | 81 | — | — | read |
| c_LZ, LZ76 complexity of the 12-symbol string (M5's four directions, A9's eight non-move kinds), normalised by n / log₁₂ n | — | — | — | read (longest window only, the framing's rule) |
| I(A9 ; N7), needs-informativeness | 63 | — | — | read |
| I(A9 ; ΔN3), wrong-need auxiliary (the top need's next-tick change: falling, flat, rising) | 27 | — | read | read |
| pairwise I(M5_A ; M5_B) and H(M5_A \| M5_B) | 25 | — | read | read |
| pairwise I and H on A9 | 81 | — | — | read |

Not read at any declared window: second-order rates (125 cells on M5,
729 on A9) and the framing's history-conditioned informativeness
I(A_t ; N_t | A_t−1) (567 cells). Correction to this draft's first
version (ca9cd1e6), made before her ruling: it paired a first-order rate
with W = 100 and 300 on A9 (1.2 and 3.7 samples per bigram cell), a
second-order rate with W = 1000, and conditioned the informativeness on
history at every window — all of which the framing's own rule calls
reading noise.

Pairs: two kitties are a pair for a window when their Manhattan distance
is at most 2 on at least half its ticks.

Every quantity is reported as **excess over its own shuffled null**: 200
block permutations within the window (blocks of 10 ticks; for the
informativeness and the pairwise quantities one string is permuted
against the other), the null's mean subtracted and its SD kept as the
per-window scale. The policy's per-state entropy H(π(·|s)) is a
different object (a baseline in §5, reproducible only where logits
exist) and is never called the entropy rate.

The drop, not the level: beside every level, the windowed quantity minus
the median of the kitty's previous ten windows, in units of the null SD.
Cells and flags (§4) are assigned on the levels against the band.

## 4. The 2 × 2 and the health band

Band: per quantity, per window, per alphabet and per ENGINE ERA — the
distribution of the excess over null on the era's healthy calibration
worlds; a reading is out of band outside the central 1 − α ("low"
below the α/2 quantile, "high" above 1 − α/2), α set per false-alarm
setting on the calibration worlds (§5, call 1 RULED). An episode is read only
against its own era's band. Eras and their healthy sources:
- **Gen 2**: the 100 full-100 teacher worlds, split 60 calibration / 40
  test by world seed, three declared splits (seeds 1, 2, 3 of a declared
  RNG over the world-seed list), every band number mean ± SD over the
  three; the 11-way streams' band from the ten `applied/scripted` and C2
  worlds, split 6 / 4 the same way, with its small-n caveat.
- **Gen 1**: the era-matched scripted collector corpora —
  `exp-006-character-gen/raw` for the exp-006 traces,
  `exp-001-bc-mappo/raw/bc-v1` for the catatonia episode — split by the
  same rule over their world lists.
- **July** (if she rules call 5 yes): the post-fix runs, split by the
  same rule.

The 2 × 2 is assignable at W = 1000 only, the one window where the
informativeness is read: rate low (h1(A9) below band) × needs-blind
(I(A9 ; N7) below band) = STUCK or LOOP; rate high × needs-blind =
DITHERING; rate low × informative = routine; rate high × informative =
responsive. c_LZ is the rate's cross-check, reported beside with the
agreement rate, never a second chance to flag. At W = 300 the rate is
read without its classifier: an out-of-band h1(M5) is a LOW-RATE or
HIGH-RATE flag, unclassified; I(A9 ; ΔN3) below band is a WRONG-NEED
flag. LOCKSTEP at either window: H(M5_A | M5_B) (or, at W = 1000, H on
A9) below band with neither kitty's top need falling over the window.

Flag and episode. A kitty-window is FLAGGED when it carries a degenerate
cell or lockstep at W = 1000, or a low-rate, high-rate, wrong-need or
lockstep flag at W = 300. An EPISODE is three or more consecutive
flagged W = 300 windows at stride 100 on the same kitty (or pair), or
one flagged W = 1000 window; onset = the first tick of the first flagged
window, and every recall and latency row names the window class that
flagged it. W = 100 carries marginal entropies only, kept as the
multiscale profile and never flagged.

## 5. Validation reads (question 2–4) and the bars declared before any read

Needs trigger, for latency: the tick at which the kitty's sustained
distress on any need reaches 150 ticks (the served watchdog line,
`[watchdog] threshold = 150`), or would have on a stream that ended
earlier; where an episode never reaches it, latency is right-censored at
the stream's end and reported as such. The watchdog line is the
HEADLINE for every run (call 2, RULED 2026-10-27). As context only,
each latency is also reported against the hard stop actually armed on
that run, recorded per stream in `streams.json` with its source: 300
ticks for Gen 2 training runs (the frozen §6 probe-distress stop,
`gen2-deviations.md:227-229`), 1,000 ticks for certification-battery
runs (`--abort-streak 1000`, `gen2-deviations.md:339-340`), and no
context row where no stop was armed. The F-053 line is never a uniform
comparator.

- **Recall and latency** (question 2): per labeled unhealthy episode and
  window, flagged yes/no, onset tick, and (onset − needs-trigger tick);
  distributions per pattern. The exp-001 catatonia episode and the
  training-collapse probes contribute to the entropy-rate columns only
  where their needs are missing or partial (stated per row). Lockstep
  recall is reported by seat type, policy (the exp-006 traces, the
  905008 pile) and scripted (the July orbits), so the seat-type confound
  is measured on that pattern. The four training-collapse halts carry no
  pattern label (s3's localization reads a policy drifting toward
  play-seeking under multi-need pressure, `gen2-deviations.md:266-284`):
  they enter recall, latency and the across-training series, never a
  leave-one-out fold.
- **False positives** (question 3): on the 40 held-out healthy teacher
  worlds per split, flagged windows per 10,000 kitty-windows and flagged
  episodes per 100,000 kitty-ticks, per window and quantity; the same
  on the healthy certified-policy worlds (g2-rot1..5, L), which is the
  rate a runtime monitor on a policy would see. **False-alarm ladder
  (call 1, RULED 2026-10-27; replaces the single FP budget):** three
  settings, one flagged episode per 10,000, per 100,000 and per
  1,000,000 kitty-ticks (about ten, one and one-tenth per healthy
  five-kitty, 20,000-tick world). Per setting and split, α is the
  largest on the grid {0.10, 0.05, 0.02, 0.01, 0.005, 0.002, 0.001,
  0.0005, 0.0002, 0.0001} (the most sensitive band) whose flagged-episode
  rate on the CALIBRATION healthy worlds is at or under the setting; an
  α with fewer than 10 calibration windows beyond a tail quantile is
  unavailable, and a setting no available α meets is reported as not
  met. Held-out worlds and labeled episodes never move α. Recall,
  latency, the leave-one-pattern-out folds, the baselines and the
  ablation are read at every setting. The HEADLINE is the middle
  setting, one per 100,000, declared now; the other two are reported
  beside it and carry no headline claim. The held-out healthy teacher
  worlds' rate at each setting is the measurement, reported against its
  target; flagged windows are reported, not budgeted. The strictest
  setting expects about four flagged episodes in a split's 40 held-out
  worlds (4,000,000 kitty-ticks), so its held-out rate is reported with
  its count and claims no more than met or not met. On healthy
  certified-policy worlds the rate is reported at each setting, and the
  gap between the two healthy classes is the seat-type confound's size.
  The cost trade (how many false alarms one earlier catch is worth,
  perhaps different for a served world and a training run) is pass 2's,
  made with this curve and the measured incidence in hand.
- **Leave-one-pattern-out** (question 4, the headline): calibrate the
  band on healthy worlds plus two patterns' episodes (their flagged
  windows define nothing — the band is the healthy quantiles; the two
  patterns set the cell thresholds' side), test on the third pattern:
  caught = flagged episode with onset before the needs trigger (or
  before the stream's end where no trigger fires). Three folds. A fold
  with fewer than three held-out episodes is reported with its count and
  carries no claim.
- **Baselines**: repeated-action counters (longest run of one action in
  the window), episode-length statistics, needs thresholds alone (the
  watchdog line), and the policy entropy from replayed logits (call 3,
  RULED 2026-10-27): each halted run's halting probe recording through
  that run's `policy-final.pt` (the weights that ran it; earlier
  probes' weights were not kept, so they get no logits), and the healthy
  side, the certified roster's L streams (observations saved at half
  precision) through rot2's own weights, split by world like every band.
  The detector: mean policy entropy over a W = 1000 window, two-sided
  band at central 1 − α, α set on the healthy L calibration worlds to
  each ladder setting's rate. Fidelity first (m13): the probes acted
  greedily, so the replay's masked argmax reproduces every recorded
  action and message exactly on the probe recordings; on L a mismatch is
  allowed only at a near-tie (top-two logit gap under 0.01), every one
  reported with its count; any other mismatch and nothing is scored.
- **Ablation**: entropy rate alone / informativeness alone / both, on
  recall at matched FP.
- **Across training** (her addition, §7b of the framing): on trunk s8
  (u49 … u299) and every trunk seed with ≥ 3 checkpoints on disk, a
  detector FROZEN at the teacher band: per checkpoint, incidence of
  flagged episodes, duration to recovery (onset → first in-band window),
  severity (depth of the informativeness drop); durations right-censored
  by the stream's end or the hard stop, reported as Kaplan–Meier curves
  with 95% bands, never as raw means. MONITOR ONLY; nothing selects on
  it.

## 6. Trips (dashboard → guard; declared, not armed in pass 1)

- **Behavioural trip, SOFT**: a flagged episode flags the episode,
  snapshots the state at onset, and starts the welfare clock. What it
  fires on that is NOT the target: competent routine (a kitty executing
  a known relief sequence is low-entropy-rate and healthy), which is why
  classification waits on the needs-informativeness column.
- **Pairwise trip, SOFT**: lockstep as defined. Not the target:
  deliberate coordination (cuddling, shared feeding), which is why the
  call requires neither kitty's needs improving.
- **The distress-duration stop stays the HARD trip.** Never stop on the
  behavioural trip alone. A false positive costs attention, never
  training.
- Quantification domain (doctrine rule 11): every trip and bar above
  quantifies over ARCHIVED streams read offline in pass 1; nothing here
  arms on a running world or a training run until a pass-2 declaration
  says so.

## 7. Registered predictions (the Professor's, verbatim from the framing's §7 and §7b; scored in RESULTS, beside the originals)

§7:
1. "Monitor detection precedes the needs trigger by ≥ 5× in median
   latency on loop and wrong-need episodes."
2. "Lockstep is caught by the pairwise quantity and NOT by any
   single-kitty quantity in ≥ half of lockstep episodes."
3. "Leave-one-out catches loops and wrong-need fixation when held out;
   lockstep held-out is the likeliest miss."
4. "Policy entropy alone separates fewer than half the labeled unhealthy
   episodes from healthy at matched FP."
"Falsification of 3 means the generalization claim is dropped from the
paper, not softened."

§7b: "median time-to-recovery falls monotonically across the first half
of training in ≥ 2 of 3 seeds; its early-checkpoint value predicts final
welfare rank across seeds (validation of the leading-indicator claim —
if not, the claim is dropped)."

Operationalised: (1) median (needs-trigger tick − onset), the watchdog
line per call 2, over loop and wrong-need episodes ≥ 5 × the median latency of the needs trigger
itself from the episode's labeled start, on the episodes where both
exist; (2) over lockstep episodes, the fraction flagged by a pairwise
quantity and by no single-kitty quantity at the same window ≥ 0.5;
(3) scored per fold as "caught" in ≥ half of the held-out episodes;
(4) at each ladder setting, the fraction of the labeled episodes
that have logits (the halting probes') which the policy-entropy
detector flags; the prediction holds if under 0.5 at the headline
setting, scored with its count (four runs); (§7b) scored on the trunk seeds with ≥ 3
checkpoints, the "first half" being the checkpoints at or under half
the run's final update.

This thread's expectations, not predictions: the healthy certified-policy
false-positive rate exceeds the teacher's (the seat-type confound is
real and measurable); the wrong-need spans (84–121 ticks) sit at the
edge of what the W = 300 wrong-need flag can see and below what the
W = 1000 informativeness can, so recall on them is expected to be low —
the resolvability rule's price, stated before the read (the first draft
expected them flagged at W = 100 by a quantity that window cannot
resolve); on the July orbits, if run, the single-kitty h1(M5) at W = 300
flags as often as the pairwise quantity, an orbit being a 2-cycle for
each kitty on its own, so the Professor's prediction 2 is expected to
fail on that source and to hold, if anywhere, on the piles.

## 8. Blind spots (declared)

Needs-informative degeneracy (competent servicing by welfare-costly
means) is invisible to this monitor; the welfare register is the
backstop. Improvement looks like novelty: the band is per checkpoint for
runtime use, frozen for the across-training series. Base rates under
many-kitty monitoring: the false-alarm ladder above, its headline
setting declared; the cost trade is pass 2's.
Label scarcity: three wrong-need spans, one catatonia episode, a handful
of lockstep traces, four training-collapse runs and, if regenerated, the
July orbits (the one mechanical label) — pass 1 is a
known-failure read at that n and will say so in every sentence that
cites a recall.

## 9. Doctrine check (CLAUDE.md rule 8, against `experiments/DESIGN-DOCTRINE.md`)

- Rule 10 (two-layer gates; a noise reading is never a pass bar) moved
  three choices: the false-alarm ladder, its headline setting and the
  rule that sets each setting's band are declared (§4, §5) before any
  read; a leave-one-out fold under three held-out
  episodes carries no claim; the band's seeds are three declared splits
  so no single split's quantile is a bar.
- Rule 11 (quantification domain) moved §6: every trip quantifies over
  archived streams in pass 1.
- Rule 1 (reward is welfare only; nothing is a reward term) is why the
  monitor is a monitor: nothing here enters a reward or a selection
  (§5 across-training, MONITOR ONLY).
- Rules 5 and 6 moved nothing: no teacher and no register text changes.
- Rule 12 moved nothing; the hard stop is unchanged.

## 10. Instrument and guards (built after her ruling; each with a predicted red before trust)

Reader `monitor_read.py` in this directory (arc venv:
`experiments/minifriend-phase1-2026-10-22/.venv`), `labels.json`
(the transcribed labels with file:line provenance), `--out` JSON and
`--md`; plain-assert `test_monitor.py`:
- m1: the A9 map covers every codec entry at kitty slots 4 / critter
  slots 2 (35), at Gen 1's 39 and codec v1's 34, every 11-way applied
  name and every July `Action` variant; predicted red: one entry
  dropped → "A9 map: every menu entry has a kind".
- m2: h_k on a hand string — a pure 2-cycle has h_1 = 0 and H(A) = 1
  bit; an i.i.d. uniform string over 4 symbols has h_1 ≈ 2 bits within
  the null SD; predicted red: the n-gram subtraction order swapped → the
  2-cycle's h_1 ≠ 0.
- m3: I(A9 ; N7) on a hand pair where the action is a function of the
  needs symbol (I = H(N)) and where it is independent (I ≈ 0 after the
  null); predicted red: the needs symbol shifted by one tick → the
  functional case loses its information.
- m4: the lockstep quantity on two identical strings (H(A | B) = 0)
  and two independent ones; predicted red: the co-location test inverted
  → the pair excluded.
- m5: the episode rule on a hand flag series (two consecutive flags are
  not an episode; three are; W = 1000 alone is); predicted red: `>= 3` →
  `>= 2`.
- m6: the split is deterministic per seed and disjoint; the band's
  quantiles at a given α on a hand distribution; predicted red: the
  1 − α/2 quantile read at 1 − α.
- m7: the labels file round-trips and every span lies inside its
  stream's length; predicted red: one span's end past the stream.
- m8: M5 from positions on a hand track — a step north reads north in
  the engine's `Direction` convention, a blocked move reads not moving,
  a two-tile jump off a reset tick is refused; predicted red: the y-axis
  sign flipped → "M5: a step north is north".
- m9: the July label rule on hand pairs — a period-2 orbit at Manhattan
  2 for 9 ticks is not an episode and for 10 is; a pair that closes to
  adjacency never is; predicted red: the period test made t − 1 →
  "orbit: period-2 at Manhattan 2 for 10 ticks is an episode".
- m10: the resolvability table — every (quantity, window) pair the
  reader computes satisfies W ≥ 10 × cells and no other pair is
  computed; predicted red: h1(A9) admitted at W = 300 →
  "resolvability: h1(A9) needs W ≥ 810".
- m11: the ladder's band rule on a hand calibration set with known
  flagged-episode counts per α — each setting takes the largest α on the
  grid whose calibration rate is at or under it, an α with fewer than 10
  calibration windows beyond a tail quantile is unavailable, and adding
  a held-out world or a labeled episode to the inputs leaves every chosen
  α unchanged; predicted red: the comparison flipped to take the
  smallest α → "ladder: the most sensitive band at or under the
  setting".
- m12: every stream in `streams.json` carries an armed stop of 300,
  1,000 or none, each non-none with a source line, and each context
  latency is computed against its own stream's stop; predicted red: the
  context computed against a constant 1,000 → "context: each run
  against its own armed stop".
- m13: the replay's masked argmax reproduces the recorded action and
  message on every row of a halting probe recording; predicted red: the
  legality mask dropped from the argmax → "replay: masked greedy
  reproduces every recorded action".

Every guard's red goes through `scripts/mutate.sh --expect` and is
recorded in this file before the read runs.

## 11. Run order (each step its own commit before its data)

1. This declaration, ruled by her (edits on her word only; a ruled
   version replaces "DRAFT" in the title line with "RULED <date>").
2. `labels.json` transcribed from the prose sources with file:line, and
   the stream inventory `streams.json` (path, alphabet, kitties, ticks,
   needs present, positions present) — committed, zero numbers of the
   monitor computed.
2b. Only on her word (§12 call 5): the July harness committed; both
   commits built in detached worktrees, nothing edited in them; the
   label rule's post-fix count read and committed before any monitor
   quantity is computed; streams under `results-raw/july/` (untracked,
   never deleted).
3. `monitor_read.py` + `test_monitor.py`, reds on record.
3b. The replay (call 3): logits for the halting probe recordings and
   the healthy L streams, m13 passing first; committed before any read
   uses them.
4. The band read (question 1) on the calibration worlds only; committed.
5. Recall / latency, false positives, leave-one-out, baselines,
   ablation, across-training (questions 2–4); one fence, `--out
   p0-pass1.json --md`.
6. RESULTS.md, gated (fresh subagent per round), stamped; predictions
   scored verbatim beside the originals; a FINDINGS entry only on a
   result that stands on its own.
7. To the Professor (scores) and Product (nothing to build; information
   only), on her standing word for this arc; pass 2, if any, is hers.

## 12. Open with the owner (rule on these with the declaration)

1. The FP budget number (§5): one flagged episode per 100,000
   kitty-ticks at W = 1000 is this thread's proposal; the Professor left
   it to the declaration.
   RULED 2026-10-27 on this thread's walkthrough. Her words, verbatim:
   "Let’s think this through. I’m assuming there will be a trade-off in
   the shape of fewer false positives = more false negatives. We should
   evaluate the relative cost of false positives vs false negatives, and
   use that to inform our target"; then, on the proposal put to her (a
   three-setting ladder, the middle setting the headline declared now,
   the cost decision in pass 2, where the trade curve and the incidence
   it needs exist): "Yes". §4, §5 and m11 carry it.
2. The needs-trigger definition (§5): the watchdog's 150-tick sustained
   distress. The alternative is the F-053 1,000-tick abort line, which
   would make every latency look better by about 850 ticks.
   RULED 2026-10-27 on this thread's walkthrough. Put to her: the
   watchdog as the headline line, the 1,000-tick line as context. Her
   question, verbatim: "Do we need the 1000 tick line reported on
   non-training runs? We should hopefully never see it on trained
   models"; answered from the record (the 1,000-tick line is the
   battery's armed abort, training runs stop at 300, and the step-8
   battery aborted 17 worlds on two trained seatings, one at 20×20 —
   g2-s2, world 905008, tick 18,949, a pass-1 lockstep source); revised
   proposal: the watchdog the headline for every run, context against
   the stop actually armed on each run. Her words: "Thanks for the
   correction. Yes, that works". §5 and m12 carry it.
3. Whether the PPO probes' policies may be replayed to recover logits
   for prediction 4 (a read of committed weights, no training; a few
   minutes per checkpoint) or prediction 4 waits for pass 2.
   RULED 2026-10-27 on this thread's walkthrough. Put to her: replay
   the recorded observations through each halted run's saved final
   weights (0 cat-ticks, no world runs, no training), with the greedy
   probes' recorded actions as an exact fidelity check, the halting
   probes the unhealthy side, the certified roster's lived worlds the
   healthy side, scored with its count. Her words: "Yes". §5, §7 (4),
   m13 and run-order step 3b carry it.
4. Whether the 4k rungs' behaviour streams (poisoned for training, not
   for reading) may be used as additional healthy-teacher material if
   the A9 band needs more worlds; the default here is no.
   RULED 2026-10-27 on this thread's walkthrough: no, and closed. Put
   to her with the finding above (the call's "healthy-teacher
   material" framing was this thread's error: `results-raw-extension-iter/
   eps01`, `eps03` hold meta.json, reward.npy and state.npy only;
   `IN-wide`, `IN-grave` are scripted seats from drawn need levels).
   Her words: "5) no and close it".
5. The July pair (§2): regenerate the pre-“wait for me” approach orbits
   inside pass 1 (scripted only, 0 covered cat-ticks, 30 worlds × 5,000
   ticks × 4 kitties per commit, minutes of compute), or leave them for
   pass 2. Without them the lockstep fold rests on a handful of policy
   traces and one pile, and the seat-type confound is untested on
   lockstep.
   RULED 2026-10-27 on this thread's walkthrough: regenerate inside
   pass 1 (run-order step 2b). Her words: "Yes, regenerate."
