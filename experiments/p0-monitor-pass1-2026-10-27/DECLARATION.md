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

**Status: DRAFT. Nothing below runs until she rules. No number from this
arc exists.**

Publication track P0 (her word 2026-10-23: "Let's try to make this our
first paper"): every headline number is a candidate paper number, so
three or more seeds wherever one is cited. Here "seeds" are of two kinds
and both are stated per number: the world seeds behind an episode set,
and three declared random splits of the healthy worlds into calibration
and test (the band's seeds).

Welfare-cost line: 0 new cat-ticks. Pass 1 reads arrays already on disk;
nothing rolls out, no weight is touched, no covered mind experiences
anything. Pass 2 (fresh labeled episodes or a transfer environment) is a
separate declaration on her word.

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

Not used, and why: `heads-pass1/` (never read); the 4k rungs marked
POISONED FOR TRAINING (their value targets, not their behaviour streams,
are the poison — `gen2-trunk-training-2026-10-18/MITIGATION.md:362-372`;
left out anyway, no label needs them); battery post-stop rows (citation
open, deviations entry 4(a)); `beam-world-screen` tier5-stale; eps01 /
eps03 (no action labels). What does not exist: machine-readable hand
labels (every label above is prose in a RESULTS, prereg or diag file,
transcribed into this arc's `labels.json` before any read, with the
file:line it came from); streams for 15 of the 17 battery aborts; any
LLM-seated episode; policy logits for the PPO probes (so the policy-
entropy baseline is not reproducible in pass 1).

Two facts that shape the design: the healthy episodes are overwhelmingly
scripted-teacher and the unhealthy ones overwhelmingly policy, so a
separator could be learning "policy vs teacher" instead of degeneracy —
hence the healthy certified-policy false-positive read (§5, question 3)
as a required column, not an option; and the alphabets differ by source,
so every band is per alphabet and no number is compared across
alphabets.

## 3. Quantities (per kitty, sliding windows; the Professor's §1–§2 as operationalised here)

Alphabets. **A9**: the codec's nine menu kinds (move, rest, sleep,
groom, eat, drink, chase, play, idle), obtained from a 35-way (or 34- /
39-way) index by the codec's own entry table, built by the instrument
from `codec.rs` and asserted to cover every entry. **A11**: the exact
11-way applied action where a stream carries it. Each row names its
alphabet. Where both proposed and applied exist, the APPLIED action is
the monitored one and the proposed is a reported second column.

Needs symbol. N_t = (the need with the highest value, its band at the
rider (b) edges 45 / 70): six needs × two bands above 45, plus "none
above 45" — 13 symbols. Declared once, here.

Windows W ∈ {100, 300, 1000} ticks, stride 100. Estimator order tied to
the window by the Professor's rule (a table of order k + 1 over an
alphabet of size |A| needs a window many times |A|^(k+1)): on A9,
|A|² = 81, |A|³ = 729, so **k = 1 at W = 100 and 300, k = 2 at
W = 1000**, and the compressibility estimator (LZ76) at W = 1000 only.
On A11 the same orders. k = 4 is not resolvable at any window on these
alphabets and is not read.

Per kitty and window:
- `H(A)`: plug-in marginal entropy (bits).
- `h_k`: entropy rate by n-gram conditional entropy, H(k+1-grams) −
  H(k-grams); `c_LZ`: LZ76 complexity normalised by n / log₂ n at
  W = 1000.
- `I(A_t ; N_t | A_{t-k..t-1})`: needs-informativeness, the plug-in
  conditional mutual information at the window's k.
- Pairwise, for every pair co-located for ≥ half the window (Chebyshev
  distance ≤ 2, the engine's adjacency, read from `pos`): `I(A ; B)` and
  `H(A | B)`.
- Wrong-need auxiliary: `I(A_t ; Δneed_{t+1})` with Δneed the sign of
  the change of the top need.

Every quantity is reported as **excess over its own shuffled null**: 200
block permutations of the kitty's action string within the window
(block length 10 ticks, the family the probe work used), the null's mean
subtracted, and the null's SD kept as the per-window scale. The policy's
per-state entropy H(π(·|s)) is a different object (a baseline in §5,
reproducible only where logits exist) and is never called the entropy
rate.

The drop, not the level: a change-point statistic on the kitty's own
series — the windowed quantity minus the median of its previous ten
windows, in units of the null SD — is kept beside every level, and the
2 × 2 cell (§4) is assigned on the levels against the band.

## 4. The 2 × 2 and the health band

Cells: entropy rate low × needs-informative = routine; low × needs-blind
= STUCK or LOOP; high × informative = responsive; high × needs-blind =
DITHERING. Lockstep = `H(A | B)` below its band with neither kitty's top
need falling over the window.

Band: the per-quantity, per-window, per-alphabet distribution over the
HEALTHY teacher calibration worlds; a reading is out of band when it
falls outside the central 95% (the 2.5% and 97.5% quantiles). "Low" and
"high" are the band's two sides. Calibration / test split: the 100
full-100 worlds split by world seed, 60 calibration / 40 test, three
declared splits (seeds 1, 2, 3 of a declared RNG over the world-seed
list), every band number reported as mean ± SD over the three. The
A11 band comes from the ten `applied/scripted` + C2 worlds with a 6 / 4
split, three seeds, and is reported with its small-n caveat.

Flag and episode. A kitty-window is FLAGGED when it sits in a
degenerate cell (stuck/loop, dithering) or in lockstep. A flagged
EPISODE is three or more consecutive flagged windows at stride 100 on
the same kitty (so ≥ 300 ticks at W = 100; one window at W = 1000
counts on its own). Onset = the first tick of the first flagged window.

## 5. Validation reads (question 2–4) and the bars declared before any read

Needs trigger, for latency: the tick at which the kitty's sustained
distress on any need reaches 150 ticks (the served watchdog line,
`[watchdog] threshold = 150`), or would have on a stream that ended
earlier; where an episode never reaches it, latency is right-censored at
the stream's end and reported as such.

- **Recall and latency** (question 2): per labeled unhealthy episode and
  window, flagged yes/no, onset tick, and (onset − needs-trigger tick);
  distributions per pattern. The exp-001 catatonia episode and the
  training-collapse probes contribute to the entropy-rate columns only
  where their needs are missing or partial (stated per row).
- **False positives** (question 3): on the 40 held-out healthy teacher
  worlds per split, flagged windows per 10,000 kitty-windows and flagged
  episodes per 100,000 kitty-ticks, per window and quantity; the same
  on the healthy certified-policy worlds (g2-rot1..5, L), which is the
  rate a runtime monitor on a policy would see. **FP budget, declared
  now by this thread (not the Professor's number):** on held-out healthy
  teacher worlds, flagged episodes ≤ 1 per 100,000 kitty-ticks at
  W = 1000 (one per kitty per five worlds); flagged windows are expected
  near the band's nominal 5% and are reported, not budgeted. On healthy
  certified-policy worlds the rate is reported against the same number
  and the gap between the two healthy classes is the seat-type confound's
  size.
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
  watchdog line), and the policy entropy where logits exist (none in
  pass 1 unless a probe's policy is replayed; declared out of pass 1).
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

Operationalised: (1) median (needs-trigger tick − onset) over loop and
wrong-need episodes ≥ 5 × the median latency of the needs trigger
itself from the episode's labeled start, on the episodes where both
exist; (2) over lockstep episodes with both kitties' actions recorded,
the fraction flagged by `H(A | B)` and by no single-kitty quantity ≥ 0.5;
(3) scored per fold as "caught" in ≥ half of the held-out episodes;
(4) NOT SCOREABLE in pass 1 (no logits) unless a probe's policy is
replayed, and said so; (§7b) scored on the trunk seeds with ≥ 3
checkpoints, the "first half" being the checkpoints at or under half
the run's final update.

This thread's expectations, not predictions: the healthy certified-policy
false-positive rate exceeds the teacher's (the seat-type confound is
real and measurable); the wrong-need spans are flagged by the
informativeness column at W = 100 (they are 84–121 ticks long).

## 8. Blind spots (declared)

Needs-informative degeneracy (competent servicing by welfare-costly
means) is invisible to this monitor; the welfare register is the
backstop. Improvement looks like novelty: the band is per checkpoint for
runtime use, frozen for the across-training series. Base rates under
many-kitty monitoring: the FP budget is the declared number above.
Label scarcity: three wrong-need spans, one catatonia episode, a handful
of lockstep traces and four training-collapse runs — pass 1 is a
known-failure read at that n and will say so in every sentence that
cites a recall.

## 9. Doctrine check (CLAUDE.md rule 8, against `experiments/DESIGN-DOCTRINE.md`)

- Rule 10 (two-layer gates; a noise reading is never a pass bar) moved
  three choices: the FP budget and the band quantiles are declared bars
  (§4, §5) before any read; a leave-one-out fold under three held-out
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
  slots 2 (35) and at Gen 1's 39; predicted red: one entry dropped →
  "A9 map: every menu entry has a kind".
- m2: h_k on a hand string — a pure 2-cycle has h_1 = 0 and H(A) = 1
  bit; an i.i.d. uniform string over 4 symbols has h_1 ≈ 2 bits within
  the null SD; predicted red: the n-gram subtraction order swapped → the
  2-cycle's h_1 ≠ 0.
- m3: the conditional MI on a hand pair where the action is a function
  of the needs symbol (I = H(N)) and where it is independent (I ≈ 0
  after the null); predicted red: the needs symbol shifted by one tick →
  the functional case loses its information.
- m4: the lockstep quantity on two identical strings (H(A | B) = 0)
  and two independent ones; predicted red: the co-location test inverted
  → the pair excluded.
- m5: the episode rule on a hand flag series (two consecutive flags are
  not an episode; three are; W = 1000 alone is); predicted red: `>= 3` →
  `>= 2`.
- m6: the split is deterministic per seed and disjoint; the band's
  quantiles on a hand distribution; predicted red: the 97.5 → 95
  quantile.
- m7: the labels file round-trips and every span lies inside its
  stream's length; predicted red: one span's end past the stream.

Every guard's red goes through `scripts/mutate.sh --expect` and is
recorded in this file before the read runs.

## 11. Run order (each step its own commit before its data)

1. This declaration, ruled by her (edits on her word only; a ruled
   version replaces "DRAFT" in the title line with "RULED <date>").
2. `labels.json` transcribed from the prose sources with file:line, and
   the stream inventory `streams.json` (path, alphabet, kitties, ticks,
   needs present, positions present) — committed, zero numbers of the
   monitor computed.
3. `monitor_read.py` + `test_monitor.py`, reds on record.
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
2. The needs-trigger definition (§5): the watchdog's 150-tick sustained
   distress. The alternative is the F-053 1,000-tick abort line, which
   would make every latency look better by about 850 ticks.
3. Whether the PPO probes' policies may be replayed to recover logits
   for prediction 4 (a read of committed weights, no training; a few
   minutes per checkpoint) or prediction 4 waits for pass 2.
4. Whether the 4k rungs' behaviour streams (poisoned for training, not
   for reading) may be used as additional healthy-teacher material if
   the A9 band needs more worlds; the default here is no.
