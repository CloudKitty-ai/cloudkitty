# Free-register baseline (mew, chirp, purr) on the Gen 1 roster — prereg, 2026-09-17

Declared before the reader runs. Owner's ask 2026-09-17: "Let's
measure mew/chirp/purr now so we have a baseline for Gen 2." The words
have no engine meaning (cooldown-only legality, intensity 0.0, no
referent, no reply stamp, no scripted rule reads them; `meow.rs:232`,
`behavior/mod.rs` has no listener) and the minds inherit them from
lineage rows (doctrine rule 6; F-022). This read records, for the Gen 1
roster as served, (1) how the words are emitted and (2) whether hearing
one changes what a listener does next. Report-only: no gate hangs on
it, and no line is proposed. The numbers are the reference Gen 2 is
measured against.

## Data

The gen1-A lab trace already on disk,
`fog-gen1-cert/results-raw/live/lab-dispersion-gen1A-trace.npz`
(the five served artifacts on `fog-gen1-cert/anchor-b3.toml`, trained
clock, greedy, seeds 870001–870005 × 5,000 ticks, 125,000 decision
rows; collected 2026-09-16 for the dispersion read). It carries obs,
mask, tick, kitty, act and seed but not the message head, so
`add_msg.py` recomputes the message choice per row by the same
masked-argmax forward the loop used (`numpy_forward_v5`, the served
bytes), writing `results-raw/gen1A-trace-msg.npz`. Rows already
collected, declaration before the read: stated plainly, and the
reader is not run on them until this file is committed. No new
rollouts, no seed claim. Live emission rates come from Client's
0.3.0 census (banked in `fog-gen1-cert/results-raw/live/
meow-recensus-client-2026-09-16.json`) and are quoted, not re-measured.

## Measure (`free_register_read.py`)

Words: mew, chirp, purr (the free register). Reference words on the
same instrument: want_cuddle and want_play, which the shakeout already
read (approach inert from unseen callers; visible callers get ~2× the
partnered scene starts). Silent is head index 0; kinds are
`obs_layout_v5.HEAD_KINDS` order.

Emission, per word and per seat, per 1k decisions: rate; the speaker's
activity mix at emission (self one-hot); the speaker's top need at
emission against the all-rows mean (the settled-state read of
`fog-gen1-cert/RESULTS.md` §"The free register").

Uptake. An event is (speaker S says word w at tick t, listener L ≠ S).
Events split by whether L sees S at t (L's kitty row for S, present
bit). Outcomes over the window t+1..t+10 (10 ticks, the shakeout's
window; audibility runs 30 ticks, the digest window, so every window
tick is inside it):

- approach: L's Euclidean distance to S falls by ≥ 2 from its value at
  t (the shakeout's definition), counted only where the distance at t
  is ≥ 2;
- proposal to the speaker: any L action in the window that targets S
  (RestWith, SleepWith, GroomKitty, ChaseKitty, PlayKitty on S's slot);
- echo: L says w in the window;
- any speech: L says any word in the window.

Control: rows (L, t′) where no cat other than L said w in the 30 ticks
up to and including t′ nor in the 10-tick window after it (so a
control window never overlaps a word's aftermath), keyed by (L, S, L
sees S at t′, L's activity class at t′). Each event is compared with the control rate of its own
key; the reported ratio is observed events with the outcome over the
sum of matched control rates (observed / expected). Pooled over the
five seeds and per seed.

## Expectation and reading

Expected (F-026: with needs visible the channel is welfare-redundant;
the shakeout's inert-cue result): every free-register ratio near 1.0
on every outcome and both visibility classes. Declared reading band:
a word is INERT if its pooled approach and proposal-to-speaker ratios
both lie in [0.8, 1.25] on both visibility classes; LEANING if a ratio
lies outside the band but the five per-seed ratios are not all on one
side of 1.0; ACTIVE if outside the band with all five seeds on one
side (sign test, p = 0.0625). Echo and any-speech are recorded without
a band: a contagion of chirps is charm, not function.

Positive control: want_cuddle from a visible caller must show the
shakeout's uptake (proposal-to-speaker ratio above 1.25). If it does
not, the instrument is suspect and no free-register reading is taken.

Report-only. Nothing here moves a config, a seating, or a Gen 2 design
choice by itself; the Gen 2 shelf (`fog-gen1-shakeout/GEN2-INPUTS.md`
§"The free register") keeps its three options and the owner's ruling
for Gen 1 (option 3, do nothing).

## Doctrine check

Rule 6 (the free register is never scripted): nothing here scripts a
word or a listener; the read is of policies only. Rule 7 (a behavior
when the world values it): sets the expectation, inert. Rule 9 (frozen
models cannot answer a reprice): this is a census of the served roster
and the Gen 2 baseline, never a conclusion about what a repriced world
would do. Rules 1–5, 8, 10 moved nothing.

## Amendments (2026-09-17, after the first run of the declared read)

The first run stands as declared and is reported in RESULTS.md. Two
things it showed about the instrument, not the words:

1. **The declared control pool is near-empty for frequent words.** Mew,
   chirp and purr run at 37, 32 and 73 per 1k decisions, so a 40-tick
   span with no other cat saying the word barely exists; 26–97% of
   free-register events, by cell, had no matched control row (dropped
   1,320–10,909 per cell; worst on the visible class, best on purr
   unseen), while the rare want-words matched fully (dropped 0) and
   passed the positive control. Amended control: rows (L, S, t′)
   where the SPEAKER S did not say w in the 30 ticks up to and
   including t′ nor in the 10-tick window after it. Other cats' words
   are background in both arms. Audibility is per speaker in the
   digest (each friend row carries its own recency and rate cells), so
   the speaker is the right unit of silence. Reader flag
   `--control speaker`; the declared pool stays as `--control any`.
2. **The speaker's state is a confound the declared key did not
   carry.** Purr is spoken 86% from rest or sleep, chirp 66%, mew 62%,
   against 22% for want_cuddle; a listener's approach or proposal
   towards a sleeping friend differs from one towards an idle friend
   whatever was said. Amended key: (L, S, L sees S, L's activity
   class, S's activity class). Reader flag `--match-speaker`.

The reading band applies to the amended read (`--control speaker
--match-speaker`); the declared read is kept beside it for the record.
The positive control (want_cuddle visible proposal ratio above 1.25)
must hold on the amended read too.

## Instrument guards

`test_free_register_read.py`: plain-python asserts on synthetic rows
in the probe format (state, not wording): counts of events, approaches
and proposals on a staged listener, the visibility split, the window
boundary, and the control exclusion. Reds via `scripts/mutate.sh`
before the reader touches the trace.
