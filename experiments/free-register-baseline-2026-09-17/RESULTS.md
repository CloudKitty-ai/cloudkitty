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
| mew | 36.8 | 43, 56, 32, 36, 16 | 63% | 0.147 |
| chirp | 31.7 | 13, 30, 41, 47, 28 | 65% | 0.144 |
| want_cuddle | 4.7 | 2.5, 7.1, 3.6, 2.4, 7.8 | 23% | 0.238 |
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
| purr | visible | 0.88 (0.57–1.48) | 0.94 (0.86–1.05) | 1.11 | 0.99 | 8,862 (5,794) |
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

## Question 2: are mews and chirps clustered? (owner, 2026-09-17)

`cluster_read.py`, declared in PREREG §Question 2 @ c96ce9b; guards:
two `mutate.sh` reds (self pairs counted, null B ignoring the class).
Coincidences = cross-cat pairs of the word within lag ≤ k ticks;
ratio = observed / null mean over 200 draws; pct = share of null draws
at or above the observed count. Null A breaks cross-cat timing (each
cat's series circularly shifted); null B keeps shared state (each cat's
emissions re-drawn among its own ticks of the same activity class).

Lab (gen1-A trace, 25,000 ticks):

| set | k | observed | vs independent timing (null A) | vs shared state (null B) | pair distance (obs / null) |
|---|---|---|---|---|---|
| mew | 1 | 746 | 1.14 (pct 0.000) | 1.05 (0.11) | |
| mew | 3 | 2,139 | 1.09 (0.000) | 1.03 (0.08) | |
| mew | 10 | 6,564 | 1.01 (0.23) | 1.00 (0.65) | 9.8 / 11.1 |
| chirp | 1 | 578 | 1.19 (0.000) | 1.08 (0.035) | |
| chirp | 3 | 1,589 | 1.09 (0.000) | 1.02 (0.23) | |
| chirp | 10 | 4,830 | 1.00 (0.55) | 0.99 (0.79) | 10.4 / 11.0 |
| mew+chirp | 1 | 2,683 | 1.16 (0.000) | 1.06 (0.000) | |
| mew+chirp | 3 | 7,516 | 1.08 (0.000) | 1.02 (0.055) | |
| mew+chirp | 10 | 23,140 | 1.00 (0.36) | 0.99 (0.82) | 10.1 / 11.2 |
| purr | 1 | 3,842 | 1.57 (0.000) | 1.30 (0.000) | |
| purr | 3 | 10,324 | 1.41 (0.000) | 1.23 (0.000) | |
| purr | 10 | 27,924 | 1.14 (0.000) | 1.11 (0.000) | 8.4 / 11.0 |

Reading, lab:

- **Mew and chirp cluster a little, in the next tick or three, and
  not beyond.** After a mew, another cat mews in the very next tick
  16% of the time against 14% under independent timing (1.14×);
  chirp 1.19×; within three ticks 1.09×; within ten ticks nothing
  (1.00–1.01). The excess is statistically real (no null draw reached
  the observed count at k = 1 or 3) and small.
- **Most of it is cats being settled together.** Under null B the
  lag-1 excess falls to 1.05 (mew, pct 0.11) and 1.08 (chirp, pct
  0.035); on the pooled set 1.06 at pct 0.000, so a 5–8% residual in
  the next tick survives shared state. That residual is under the
  1.25 line the prereg set for "the echo the owner sees" and agrees
  with the uptake read's echo ratios (0.92–1.13). Coincident mew and
  chirp pairs are only slightly closer than chance (9.8–10.4 tiles
  against 11.0–11.2).
- **Purr is the clustered word.** 1.57× at lag 1, 1.30× after shared
  state, pairs at 8.4 tiles against 11.0: cats that purr together are
  the settled pairs and piles, and their purring stays clustered
  after matching on rest or sleep because the purr is earned by
  happiness (`purr_earned`) and a cosleep pile is happy together.
  Companionship, not echo.

### Client's read of what a viewer sees (relayed 2026-09-17; raw `results-raw/client-drawn-clustering-2026-09-17.json`)

Owner's follow-up: "have Client investigate what's visible." Client's
instrument, settled window ticks 3973–5879, same coincidence measure
against a circular-shift null (300 reps), engine ring against drawn
bubbles (what survives `VIEW.meowPoses`):

| word | stage | events | gate pass | next tick | within 3 | within 10 |
|---|---|---|---|---|---|---|
| mew | engine | 360 | | 1.09× | 1.05× | 1.01× |
| mew | drawn | 129 | 36% | 0.65× | 0.91× | 1.06× |
| chirp | engine | 322 | | 1.06× | 0.98× | 1.02× |
| chirp | drawn | 151 | 47% | 0.57× | 0.75× | 1.03× |
| purr | engine | 226 | | 0.99× | 1.14× | 0.99× |
| here_sunbeam | engine | 172 | | 1.72× | 1.39× | 1.41× |
| here_sunbeam | drawn | 137 | 80% | 1.86× | 1.39× | 1.56× |
| here_food | engine | 403 | | 1.03× | 1.00× | 0.98× |
| here_water | engine | 427 | | 1.08× | 0.96× | 0.99× |

The engine numbers for mew and chirp reproduce on the served world
(1.06–1.09× at one tick). Drawing takes them below chance (the pose
gate passes sounds at 36–47% and its cross-cat co-occurrence is
independent: 3.30 of 5 cats in a passing pose per tick, variance 1.12
against 1.12 for independent draws), so no client stage manufactures
sound bursts. What the viewer watches is here-words, which pass the
gate at 69–80%, and here_sunbeam is clustered in the engine itself.
Separately, 54% of answered asks put two or more reply bubbles on
screen at once, up to four: one cat asks, several answer within a tick
or two. That is the echo the owner describes, and it is the world,
not the drawing. (Client state: `meowCooldownMs` is 8,000 since
d717d49; it gates the gape only, and `drawBubbles` reads the ring with
no cooldown or queue. A client change to one reply per ask is on a
branch the owner is watching; not banked here.)

### Addenda: the here-words through both nulls (lab)

Declared in PREREG §Addendum and §Addendum 2 before each run. Null A
as above; null B keyed on activity × own in-sunbeam bit
(`cluster-lab-here-sunbeamkey.json`), then × "another cat said the
paired want in the 30 audible ticks before t" (`cluster-lab-here-askkey.json`).

| word | k | observed | null A | null B: own state | null B: own state × ask | pair distance obs / null |
|---|---|---|---|---|---|---|
| here_sunbeam | 1 | 442 | 1.89× | 1.86× | 1.31× | |
| here_sunbeam | 3 | 1,209 | 1.72× | 1.71× | 1.21× | |
| here_sunbeam | 10 | 3,975 | 1.69× | 1.69× | 1.24× | 10.1 / 11.3 |
| here_food | 1 | 1,372 | 1.20× | 1.19× | 1.11× | |
| here_food | 10 | 12,809 | 1.12× | 1.12× | 1.06× | 10.6 / 11.0 |
| here_water | 1 | 1,266 | 1.15× | 1.14× | 1.04× | |
| here_water | 10 | 12,403 | 1.12× | 1.12× | 1.04× | 9.6 / 11.0 |
| here_critter | 1 | 298 | 1.58× | 1.58× | 1.46× | |
| here_critter | 10 | 2,496 | 1.33× | 1.33× | 1.24× | 8.6 / 11.1 |

Every pct is 0.000 except here_water under the ask key (0.075–0.185,
at chance). Reading:

- **Client's here_sunbeam finding reproduces in the lab**, stronger
  (1.89× at one tick, and it does not decay by ten ticks).
- **Own state explains nothing.** Keying null B on whether the
  speaker is itself in a sunbeam leaves every ratio where it was. The
  addendum's prediction (the purr shape, cats sharing a beam) is
  refuted.
- **The shared ask explains here_water, most of here_food, and about
  two thirds of here_sunbeam's excess** (1.89 → 1.31 at one tick).
  Several cats hear the same want and answer it, and the ask repeats
  on its cooldown while the want lasts, which is why the clustering
  holds to ten ticks. This is Client's reply flurry measured from the
  engine side.
- **A residual stays on here_sunbeam (1.31×) and here_critter
  (1.46×)**, both above the 1.25 line the addendum set, so the ask is
  not the whole trigger. The remaining candidate is the shared
  referent: a here-word is legal beside its referent, beams and
  critters are few, and two cats beside the same beam or the same bug
  both announce it. The own-state key carried "on a beam", not
  "beside one", and nothing for critters. Per the declaration the read
  stops here for the owner's sitting; the referent-adjacency key is
  the next null if she wants the residual named.

### Live (served world)

`results-raw/live-meows-20260917T153356.jsonl`: the ring polled every
8 s for 45 min, ticks 88,095–91,495 (3,401 ticks, 332 polls, 3,798
meow rows); state and position from the nearest poll, so null B is
weak here and null A is the read (`cluster-live-free.json`,
`cluster-live-here.json`).

| word | n | next tick | within 3 | within 10 | pair distance obs / null |
|---|---|---|---|---|---|
| mew | 615 | 0.99× (pct 0.55) | 1.07× (0.09) | 1.03× (0.08) | 8.1 / 9.6 |
| chirp | 567 | 1.20× (0.035) | 1.00× (0.52) | 0.97× (0.92) | 7.8 / 9.4 |
| mew+chirp | 1,182 | 1.11× (0.015) | 1.05× (0.035) | 1.00× (0.37) | 8.1 / 9.4 |
| purr | 387 | 1.61× (0.000) | 1.18× (0.03) | 1.03× (0.19) | 7.1 / 9.7 |
| here_sunbeam | 230 | 1.17× (0.33) | 1.30× (0.06) | 1.91× (0.000) | 7.4 / 9.6 |
| here_food | 650 | 1.19× (0.065) | 1.14× (0.000) | 1.19× (0.000) | 9.2 / 9.2 |
| here_water | 740 | 1.17× (0.08) | 1.17× (0.000) | 1.12× (0.000) | 8.0 / 9.5 |
| here_critter | 308 | 1.37× (0.055) | 1.42× (0.000) | 1.36× (0.000) | 7.5 / 9.2 |

The served world agrees with the lab and with Client's window. Mew and
chirp sit at chance beyond the next tick (the pooled next-tick excess
is 1.11×, thin: 358 pairs); purr clusters in the next tick (1.61×) and
is gone by ten; here_sunbeam and here_critter are the clustered words
(1.9× and 1.4× within ten ticks), here_food and here_water mildly so
(1.1–1.2×). Verdict on the owner's question: mews and chirps are not
echoed. What she sees echoing is here-words answering the same ask
(and beams and critters being announced by everyone beside them), and
purring piles.

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

## Regeneration

(Added 2026-09-27 under the owner-approved five-file package: this
file predates the accuracy-gate skill; the block below was written
retroactively and verified to reproduce the recorded reads before
the gate ran.)

### Collect

The lab trace: five served gen1-A artifacts on `anchor-b3.toml`,
trained clock, greedy, seeds 870001–870005 × 5,000 ticks, message
head recomputed by `add_msg.py` onto
`results-raw/gen1A-trace-msg.npz`. The live poll:
`results-raw/live_meows_poll.py` against the served box, recorded to
`results-raw/live-meows-20260917T153356.jsonl` (unreproducible
source; the recorded file is the input of record). Never run by the
gate.

### Read

Runtime: each line under 3 minutes. No environment variables
required. The --out paths below point at the recorded raws;
regeneration is byte-exact for five of the seven, while the
declared read and cluster-lab.json regenerate with the added
fields listed below — so running verbatim rewrites those two raws
with slightly different bytes. A verifier redirects --out to a
scratch directory and compares. Known benign differences on regeneration: the DECLARED
read's `params` block gains two fields (`control`, `match_speaker`)
added to the reader by the amendment — every data key reproduces
exactly; `cluster-lab.json` regenerates equal on every key except
two fields added to `_meta` (`sets`, `state`).

```
cd /Users/elizabethkelly/ai/cloudkitty
experiments/exp-006-character-gen/.venv/bin/python experiments/free-register-baseline-2026-09-17/free_register_read.py \
  experiments/free-register-baseline-2026-09-17/results-raw/gen1A-trace-msg.npz \
  --out experiments/free-register-baseline-2026-09-17/results-raw/free-register-read.json
experiments/exp-006-character-gen/.venv/bin/python experiments/free-register-baseline-2026-09-17/free_register_read.py \
  experiments/free-register-baseline-2026-09-17/results-raw/gen1A-trace-msg.npz \
  --control speaker --match-speaker \
  --out experiments/free-register-baseline-2026-09-17/results-raw/free-register-read-amended.json
experiments/exp-006-character-gen/.venv/bin/python experiments/free-register-baseline-2026-09-17/cluster_read.py \
  lab experiments/free-register-baseline-2026-09-17/results-raw/gen1A-trace-msg.npz \
  --out experiments/free-register-baseline-2026-09-17/results-raw/cluster-lab.json
experiments/exp-006-character-gen/.venv/bin/python experiments/free-register-baseline-2026-09-17/cluster_read.py \
  live experiments/free-register-baseline-2026-09-17/results-raw/live-meows-20260917T153356.jsonl \
  --out experiments/free-register-baseline-2026-09-17/results-raw/cluster-live-free.json
experiments/exp-006-character-gen/.venv/bin/python experiments/free-register-baseline-2026-09-17/cluster_read.py \
  lab experiments/free-register-baseline-2026-09-17/results-raw/gen1A-trace-msg.npz \
  --sets here --state activity+sunbeam \
  --out experiments/free-register-baseline-2026-09-17/results-raw/cluster-lab-here-sunbeamkey.json
experiments/exp-006-character-gen/.venv/bin/python experiments/free-register-baseline-2026-09-17/cluster_read.py \
  lab experiments/free-register-baseline-2026-09-17/results-raw/gen1A-trace-msg.npz \
  --sets here --state activity+sunbeam+ask \
  --out experiments/free-register-baseline-2026-09-17/results-raw/cluster-lab-here-askkey.json
experiments/exp-006-character-gen/.venv/bin/python experiments/free-register-baseline-2026-09-17/cluster_read.py \
  live experiments/free-register-baseline-2026-09-17/results-raw/live-meows-20260917T153356.jsonl \
  --sets here \
  --out experiments/free-register-baseline-2026-09-17/results-raw/cluster-live-here.json
```

## Correction (2026-09-27, found by the retroactive accuracy gate)

The emission table's "spoken from rest or sleep" column originally
read 86 / 62 / 66 / 22 / 33; the gate's recompute from the trace
(the reader's own per_tick, activity at the emission tick, pooled
weighted by emission count) gives 86.37 / 62.80 / 65.34 / 22.60 /
32.79, so under the document's own round-to-nearest convention the
column is 86 / 63 / 65 / 23 / 33 — corrected above. No qualitative
reading changes. Four of the five original figures also appear in
PREREG.md amendment 2 (28e2bce; want_play's 33 is not there), which
is frozen and stays as written; this
note is its correction of record, and the carried-forward Gen 2
comparison numbers are the corrected ones.

## Corrections and re-readings (2026-09-27, retroactive gate round 2)

Each entry quotes the original sentence verbatim and states the
corrected reading; the quoted sentences are retired from the gate by
this addendum. Beyond the emission column (the Correction section)
and one double-rounded uptake cell (purr visible echo, originally
1.12, exact 1.1145 → 1.11, corrected in the table), the table
numbers reproduce; the rest are prose corrections.

1. Quoted: "Mew keeps a 17% play share and chirp 18%, the one
   non-settled context either word has." The shares are right (16.5%
   and 17.5%), the exclusivity is wrong: eat (11.2% mew / 9.1%
   chirp), drink, groom and idle are also non-settled contexts;
   non-settled totals are 37% (mew) and 35% (chirp), of which play
   is 44% (mew) and 51% (chirp).
2. Quoted: "from an unseen caller, approach 1.51 (1.48–1.59) and
   proposal 2.50 (2.13–2.93), the shakeout's result reproduced on
   the served composition." The shakeout found unseen-caller
   approach INERT (at or below chance); this read's 1.51 on a
   different instrument (within-policy matched control vs the
   shakeout's between-arm share) is the opposite reading, so
   "reproduced" is unsupported in either direction. The declared
   positive-control criterion itself passes (visible proposal
   1.37 > 1.25), which is all the decision used.
3. Quoted: "Any-speech is 1.00 everywhere: no word makes anyone
   talk more." The recorded values run
   0.988–1.003; the conclusion (no word makes anyone talk more)
   stands, the stated precision does not.
4. Quoted: "(and beams and critters being announced by everyone
   beside them)". Untested: the referent-adjacency null was never
   run, as this document says elsewhere; the residual is unnamed.
5. Quoted: "The served world agrees with the lab and with Client's
   window." Five cells disagree:
   purr at k=10 (lab 1.14 pct 0.000, live 1.03 pct 0.185),
   here_sunbeam's shape (lab decays 1.89→1.69, live grows
   1.17→1.91), purr at k=1 (Client engine 0.99, live 1.61), mew at
   k=1 (lab 1.14 pct 0.000, live 0.99 pct 0.55), chirp at k=3 (lab
   1.09 pct 0.000, live 1.00 pct 0.52). "Agrees" overstated a mixed
   picture.
6. Quoted (Carry forward): "visible-class ratios at 1.0". The Gen 2
   comparison values to carry are the recorded bands, not 1.0:
   approach 0.88–1.07, proposal 0.94–1.02, visible echo 1.11–1.13,
   per-seed ranges straddling 1.0.
7. Quoted: "(1.89× at one tick, and it does not decay by ten
   ticks)". The lab series goes 1.89 → 1.72 → 1.69: it stays high
   but does decay.
8. Quoted: "explains here_water, most of here_food". The ask key
   removes 42–55% of here_food's excess across lags against the ask
   file's own null A (40–54% against the own-state null B; k1
   1.20 → 1.11) — about half on every baseline, not most. The here_water clause stands (a
   1.04 residual at k=10, pct 0.000).
9. Quoted: "the other exactly 1.0 (purr approach, seed 870001)."
   The exact value is 1.00025 — a hair above 1.0, not exactly 1.0;
   "29 of 30 under 1.0" stands, and purr's ACTIVE reading rides its
   proposal ratios (all five seeds below 1) either way.
10. Quoted: "in the control the speaker has been silent for 30 ticks
   or more and its row is stale or empty." Measured on the trace,
   this is not how the amended control was built: it excludes only
   speakers of the SAME word, and in 99.5–99.6% of unseen-class
   control rows the speaker said some other word within the prior
   30 ticks (median 2 ticks since its last word; 21–27% spoke at
   the control tick itself). The listener's row for that speaker is
   populated in 99.19–99.34% of unseen-class control rows against
   99.9–100% of event rows. The fresh-row-vs-stale-row mechanism does not follow
   from the control's construction.
11. Quoted: "Until then the honest Gen 2 baseline is: the free
   register carries no cue a visible listener acts on, and from the
   fog it acts as a position report." The measured ratios stand
   (visible in-band, unseen below 1); the "position report"
   mechanism rests on the stale-row story corrected in entry 10 and
   is a hypothesis, not a measured reading.
12. Quoted: "Instrument refinement before the Gen 2 read: the
   fresh-row control (speaker said another word), and distance in
   the unseen key." The first half is largely vacuous as stated —
   the current control pool already consists overwhelmingly
   (99.5%+) of speakers who said another word in the window; a
   refinement that separates row freshness would have to key on
   the ROW's own staleness, not the speaker's other-word speech.
   The distance-key half stands.
13. Quoted: "Every pct is 0.000 except here_water under the ask key
   (0.075–0.185, at chance)." The 0.075–0.185 range covers k=1 and
   k=3; the table's k=10 ask-key cell for here_water is 1.04 with
   pct 0.000 — not at chance — as entry 8 records.
14. Quoted: "This read cannot separate "the word" from "a fresh
   row"; the control that would is a speaker who said some OTHER
   word in the window (fresh row, different word), the next
   refinement of this instrument." Entry 10's measurement shows the
   current control already IS that pool (99.49–99.61% of control
   unseen-class rows have the speaker saying another word in the
   window), so the
   read does largely separate the word from a fresh row, and the
   named refinement is the instrument as it stands.
15. Quoted: "The unseen effect is most likely the heard row, not
   the word." Its stated support was the stale-control-row story
   corrected in entry 10. With the control pool measured (other-word
   rows, populated 99.19–99.34%), the event/control contrast is
   mostly "row carrying w" vs "row carrying another word" — which
   points toward the word, not the row. The attribution is OPEN;
   F-048's title inherits this and carries a review caveat dated
   2026-09-27.
16. Quoted: "proposing less is the mind reading the row, and the
   want-words do the opposite with the same row because they carry
   an ask." The want-word numbers stand (1.51 / 2.50); the
   row-reading mechanism is a hypothesis resting on the corrected
   entry-10 story, not a measured reading.


Gate: **PASS** 2026-09-27 (retroactive, ten rounds; the owner-approved
five-file package). What the rounds corrected: three emission
percentages wrong for nine days and mirrored in the frozen PREREG
(the carried-forward Gen 2 numbers), one double-rounded uptake cell,
a refuted control-mechanism story (the row-vs-word attribution is
now OPEN, F-048 retitled), a near-vacuous proposed instrument
refinement, and the correction addendum's own errors three times
over. All seven Read lines regenerate as declared; 16 retired
quotes; ~330 arithmetic values verified round 10 with 3 non-failing
WEAK · raws f263fbddab39.
