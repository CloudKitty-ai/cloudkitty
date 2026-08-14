# Meow economics: three dialects of purr, and what happens when they meet

**2026-08-14, owner's ask** ("who's saying what in which circumstances,
what impact are those meows having, and what happens mixed together").
Instrument: `mix_meow_probe.py` — six compositions × probe seeds
820001–005 × 10,000 ticks (200k kitty-ticks each), served config,
greedy; seat→model assignment rotated per seed so traits never
confound model identity. Homogeneous worlds give each seed's native
economy; mixed worlds (s1+s2+s3 + rotating fourth) give
interoperation, with every causal flip attributed speaker-model →
hearer-model (freshest-other reconstruction, matching
`freshest_audible`). Analyzer: `meow_econ.py`; pooled numbers in
`econ-report.json`.

## The three native economies (homogeneous company)

| | s1 "the quiet one" | s2 | s3 "the chatterbox" |
|---|---|---|---|
| Purr /1k | 191.6 | 306.1 | **794.0** |
| other kinds /1k | WantBath 0.24 | WantEat .58 · FollowMe .28 · traces | ~0.6 total across six kinds |
| purr act-flip (hearer) | 6.5% | 7.9% | 7.6% |
| FollowMe act-flip | — | 12.3% | 16.8% |
| happiness | 95.07 | 94.99 | 94.87 |

All three are purr economies — the want-words survive only as traces
(the attention generation kept the exp-004 channel culture). Two
standout facts:

- **No devaluation.** s3 purrs 4× as often as s1, yet the per-purr
  causal potency on hearers is undiminished (7.6% vs 6.5% act-flip;
  every audible purr-tick still moves decisions). The channel does
  not saturate at these volumes — contrast the F-011 intuition that
  an always-on signal devalues its own contrast: at 79% duty cycle,
  not yet.
- **The dialects invert the word's spatial meaning.** s1 purrs at
  above-baseline separation (dist-to-nearest 2.87 at emission vs 2.53
  declined — the deployed generation's excursion-apogee contact
  call). s3 purrs at *below*-baseline separation (2.54 vs 3.73 — it
  goes quiet when far and hums when close: a proximity/companionship
  signal). Same word, opposite deixis, both stable equilibria of the
  same recipe differing only in RNG seed.

## Mixed company: universal comprehension, kin-biased answering

Mixing all three (three compositions, fourth seat rotating):

- **Dialects are mutually intelligible.** Cross-model purr act-flip
  7.3–7.4% vs same-model 7.8–8.9% — an s1 hearing an s3's purr is
  moved by it almost exactly as much as by its own kin's. The
  *action* semantics of the word transfer completely.
- **Answering is kin-biased.** The message-head flip (purring back
  because you heard it) runs same-model 20–26% vs cross-model 16–18%
  — cats echo their own dialect's purrs noticeably more, while the
  chorus itself spans every pair (reply matrix: s2↔s3 ~246k both
  directions, all six model-pairs heavily populated).
- **Voices are stable with mild accommodation.** In mixed company s1
  purrs ~13% more (192→217/1k), s2 ~11–17% more (306→339–358), s3
  slightly less (794→776–808). Nobody adopts anyone else's register;
  the quiet cats lean in a little.

## The welfare finding: the chatterbox needs its kin

| composition | s1 | s2 | s3 |
|---|---|---|---|
| homogeneous | 95.07 | 94.99 | 94.87 |
| mixed, two s3 copies | 95.15 | 95.17 | **94.51** |
| mixed, one s3 | 95.12–95.14 | 95.13–95.20 | **93.93** |

s1 and s2 are composition-robust (±0.15 everywhere, zero distress).
**s3's welfare is dose-dependent in its own kind**: 94.87 among kin →
94.51 with one sibling → 93.93 alone among quieter cats, a −0.94
swing. Its strategy is tuned to a purr-saturated soundscape and
mis-fires in quieter company — F-012's audience-dependence lesson
appearing at the *welfare* level for the first time. Meanwhile s1/s2
do marginally *better* with a chatterbox around than at home.

## Selection implications (when/if a candidate goes forward)

s1: best welfare of all eight A1 runs across both architectures,
composition-robust, and speaks the deployed generation's dialect at
the deployed generation's volume — the conservative candidate. s2:
robust, moderately chatty, the only seed keeping want-words
measurably alive. s3: the most interesting cat and the worst
candidate — composition-sensitive by nearly a full happiness point,
and its 800/1k voice is a product decision, not just a certification
one. Any formal selection pins its rule before per-seed §9 numbers
are examined (pipeline discipline).

Screen-grade throughout: pooled over probe seeds, no per-world
clustering (F-004/F-009 bounds apply); flip causality is exact
(greedy determinism) but composition welfare deltas ride 5-seed
pools — the s3 dose-response is consistent across all three mixed
compositions, which is why it is stated.

Raw per-composition JSONs regenerable via `mix_meow_probe.py` env
knobs (MEOW_COMPS/MEOW_TICKS/MEOW_SEEDS).
