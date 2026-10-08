# partner_absent split — results

Collected 2026-10-07 under the declaration committed pre-collection
(`PREREG.md`, 84228007): one live window off kitties.ai, served fog
Gen 1 policy roster, ticks 2275950..2283450 (7,501 ticks, ~100 min at
the served clock), positions polled ~0.55 s. Tick coverage 0.997,
0 refusal-ring gaps, vision radius 4 from the stored `/config`. Raw
in `results-raw/partner-absent-split-2275950.json` (uncommitted, by
design); scored JSON `results-raw/split-read.json`; rendered table
`read.md`.

## The table (read.md, from `results-raw/split-read.json`)

539 `partner_absent` rows in-window, all 539 joined (0 dropped for a
missing snapshot, 0 unparsed):

| bucket | rows | share | absorbed share | top proposals |
|---|---|---|---|---|
| race | 350 | 0.649 | 0.574 | sleep:with 174, rest:with 97, play:kitty 76 |
| seen | 189 | 0.351 | 1.000 | rest:with 101, sleep:with 88 |
| fog | 0 | 0.000 | -- | -- |

seen manhattan-distance histogram: {'2': 185, '3': 4}
seen same-pair run lengths (gap <= 2 ticks): {'1': 189}

| seat | race | seen | fog | rows |
|---|---|---|---|---|
| Miso | 69 | 46 | 0 | 115 |
| Biscuit | 79 | 25 | 0 | 104 |
| Pumpkin | 47 | 25 | 0 | 72 |
| Kittybear | 71 | 42 | 0 | 113 |
| Clementine | 84 | 51 | 0 | 135 |

Rate: 539 rows over 7,501 ticks is about 323/h at 4,500 ticks/h, the
same order as the baseline window's 286/h
(`refusal-baseline-2026-09-02/RESULTS.md`, second window).

## The headline: zero calls from the fog

No `partner_absent` proposal in this window targeted a partner
outside the caller's vision disc. The standing story — the baseline
RESULTS section titled "Unanswered from-the-fog calls (reason
`partner_absent`)" — does not describe the served volume: it is not
calls at remembered or heard positions. It is two mundane shapes:

- **64.9% races**: the target was adjacent (Manhattan <= 1) in the
  start-of-tick snapshot the mind decided against, and moved earlier
  in the same tick's turn order. The mind's decision was correct
  against what it saw, so no mask can touch these, and the per-tick
  fresh turn-order draw means no seat systematically eats them.
  57.4% were absorbed; the taxed remainder is ~90 turns/h
  roster-wide, about 0.4% of a seat's ticks.
- **35.1% near-misses at a visible friend**: 185 of 189 at Manhattan
  distance exactly 2 and 4 at distance 3 — one to two tiles short of
  adjacency — every one a one-off (no same-pair run longer than 1;
  the run gap of <= 2 ticks is a reader constant, not prereg'd), and
  every one absorbed (the caller was mid-scene, so no turn was
  lost).

A correction addendum pointing here was added to the baseline
RESULTS section 2026-10-08, alongside this read; its definition
sentence (a stale heard position is a refusal by design) stays true
as spec text — what the split corrects is the assumption that the
volume was that case.

## Decision feed

This read fed the Gen 2 sitting's absent-partner-calls item; the
standing outcome (record:
`experiments/gen2-kickoff-rulings-2026-10-07.md` §3, which carries
the owner's words and their exact scope): the by-design refusal
stays, no engine change — she accepted the engine-alternative close
in-session 2026-10-08 — with a declared post-Gen 2 re-read.
The fog bucket's zero is the clean Gen 1 baseline for that re-read:
under hidden needs, a nonzero fog bucket would be the first
appearance of calls into the fog, which is an emergence read, not a
defect.

## Regeneration

### Collect

```
cd /Users/elizabethkelly/ai/cloudkitty/experiments/partner-absent-split-2026-10-07
python3 collect_split.py 7500
```

(live window off kitties.ai, ~100 min wall; writes
`results-raw/partner-absent-split-<start_tick>.json`; a fresh collect
is a NEW window — the gate never runs this)

### Read

```
cd /Users/elizabethkelly/ai/cloudkitty/experiments/partner-absent-split-2026-10-07
python3 -B split_read.py results-raw/partner-absent-split-2275950.json --out /tmp/split-read-fresh.json --md /tmp/split-read-fresh.md
```

(stdlib python3, no venv; runtime seconds; prints the full table and
every derived column above, including the seen histogram and run
lengths)

Gate: **PASS** r2, 2026-10-08 — arithmetic 22, threshold 4 (3
sourced, 1 disclosed reader constant), characterisation 10,
provenance 9, undecidable 2; r1 FAIL on two wording items (owner-
ruling overreach in the decision feed; "one tile short" vs the
4-at-distance-3 histogram rows in the companion record), both fixed
and re-verified. Raw-dir hash v1:710a6dda6cdc4a9e
(`scripts/rawdir-hash.sh` recipe v1).
