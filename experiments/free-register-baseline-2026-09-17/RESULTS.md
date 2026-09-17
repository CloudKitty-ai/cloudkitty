# Free-register baseline (mew, chirp, purr) on the Gen 1 roster — results, 2026-09-17

Declared in `PREREG.md` @ 251c67f; amendments @ 28e2bce, declared
before the rerun. Data: the gen1-A lab trace (five served artifacts on
`anchor-b3.toml`, trained clock, greedy, seeds 870001–870005 × 5,000
ticks, 125,000 decision rows) with the message head recomputed by
`add_msg.py` (the activity head reproduced the trace's actions on every
row; 37,391 non-silent rows, 299 per 1k). Raws, uncommitted:
`results-raw/gen1A-trace-msg.npz`, `results-raw/free-register-read.json`
(declared read), `results-raw/free-register-read-amended.json`
(amended read). Instrument guards: three `mutate.sh` reds (window
boundary, control aftermath, speaker-vs-listener silence).

## Emission (per 1k decisions; seats Miso, Biscuit, Pumpkin, Kittybear, Clementine)

| word | roster | by seat | spoken from rest or sleep | speaker's top need (all rows 0.162) |
|---|---|---|---|---|
| purr | 72.8 | 110, 117, 86, 29, 22 | 86% | 0.153 |
| mew | 36.8 | 43, 56, 32, 36, 16 | 62% | 0.147 |
| chirp | 31.7 | 13, 30, 41, 47, 28 | 66% | 0.144 |
| want_cuddle | 4.7 | 2.5, 7.1, 3.6, 2.4, 7.8 | 22% | 0.238 |
| want_play | 0.5 | 0.4–0.6 | 33% | 0.230 |

The free register is a settled-state register: all three words are
spoken mostly from rest or sleep, by a cat whose top need sits under
the all-rows mean, where the want-words come from idle cats under
pressure. Purr is the loudest and most seat-skewed (Miso and Biscuit
110–117, Kittybear and Clementine 22–29). Mew keeps a 17% play share
and chirp 18%, the one non-settled context either word has. Live
(Client's 0.3.0 census, 9,375 cat-ticks): mew 37, chirp 34, purr 24
per 1k cat-ticks; mew and chirp match the lab, purr runs at a third of
it on the served world (the lab counts a purr decision every tick of a
settled scene, the client counts unique meows off the ring, so the
purr line is not like-for-like).

## Uptake: does hearing one change what a listener does

Ratio = observed / expected over matched controls, window 10 ticks
after the word, per PREREG. Two reads.

**Declared read** (`--control any`): the control pool needs no other
cat saying the word in a 40-tick span, which barely exists at 30–70
per 1k; 26–97% of free-register events had no matched row. Recorded in
the raw, not read. Its positive control held (want_cuddle visible
proposal 1.34, dropped 0).

**Amended read** (`--control speaker --match-speaker`, the reading
band applies). Positive control holds: want_cuddle from a visible
caller, proposal-to-speaker 1.37 (per seed 1.26–1.53); from an unseen
caller, approach 1.51 (1.48–1.59) and proposal 2.50 (2.13–2.93), the
shakeout's result reproduced on the served composition.

| word | class | approach | proposal to speaker | echo | any speech | events (dropped) |
|---|---|---|---|---|---|---|
| mew | visible | 0.90 (0.48–1.36) | 0.97 (0.83–1.08) | 1.13 | 1.00 | 4,412 (2,299) |
| mew | unseen | 0.80 (0.66–0.91) | 0.63 (0.54–0.95) | 0.92 | 1.00 | 10,432 (1,205) |
| chirp | visible | 1.07 (0.78–1.34) | 1.02 (0.94–1.21) | 1.12 | 0.99 | 3,502 (2,269) |
| chirp | unseen | 0.85 (0.80–0.89) | 0.73 (0.52–0.85) | 1.00 | 1.00 | 8,344 (1,685) |
| purr | visible | 0.88 (0.57–1.48) | 0.94 (0.86–1.05) | 1.12 | 0.99 | 8,862 (5,794) |
| purr | unseen | 0.78 (0.65–1.00) | 0.53 (0.25–0.96) | 0.95 | 1.00 | 18,297 (3,363) |

Parentheses: the five per-seed ratios' range. Approach events are the
subset with the speaker at distance ≥ 2. Dropped = events whose key
(listener, speaker, sees, both activity classes) had no control row;
the visible class loses a third to two fifths of its events to the
finer key.

Reading per the band:

- **Visible caller: INERT on all three words.** Approach 0.88–1.07 and
  proposal 0.94–1.02, every per-seed range straddling 1.0. A listener
  who can see the speaker does nothing different after a mew, a chirp
  or a purr. Any-speech is 1.00 everywhere: no word makes anyone
  talk more.
- **Unseen caller: below the band on all three, ACTIVE by the sign
  test, in the direction of doing LESS.** Approach 0.78–0.85 and
  proposal 0.53–0.73, with 29 of the 30 per-seed ratios under 1.0 and
  the other exactly 1.0 (purr approach, seed 870001).
  Hearing a settled word from a friend out of view makes the listener
  less likely to walk towards it or to propose to it.
- **Echo: no contagion.** 0.92–1.13, per-seed ranges through 1.0.

The unseen effect is most likely the heard row, not the word. A word
from an unseen friend is stamped with the speaker's position and lands
on the listener's heard row with fresh dx, dy and the speaker's message
cells; in the control the speaker has been silent for 30 ticks or more
and its row is stale or empty. A proposal to an unseen friend is a
`partner_absent` refusal by design (the 286-per-hour stream in the
refusal window), so a listener whose row now says "far away, asleep"
proposing less is the mind reading the row, and the want-words do the
opposite with the same row because they carry an ask. This read cannot
separate "the word" from "a fresh row"; the control that would is a
speaker who said some OTHER word in the window (fresh row, different
word), the next refinement of this instrument. Until then the honest
Gen 2 baseline is: the free register carries no cue a visible listener
acts on, and from the fog it acts as a position report.

## Carry forward

- Gen 2 comparison numbers: emission per 1k (purr 72.8, mew 36.8,
  chirp 31.7, roster) and the settled-state shares; visible-class
  ratios at 1.0; unseen-class approach 0.78–0.85 and proposal
  0.53–0.73 under this control. A Gen 2 mind that hears meaning shows
  a visible-class ratio leaving the band or an unseen ratio above 1.0
  on a settled word.
- Instrument refinement before the Gen 2 read: the fresh-row control
  (speaker said another word), and distance in the unseen key.
- The Gen 2 shelf (`fog-gen1-shakeout/GEN2-INPUTS.md` §"The free
  register") is unchanged: three options, option 3 ruled for Gen 1.
