# Mini-friend Phase 1b — per-cat grave starts × head size (declaration 2026-10-23; owner-requested)

Owner, 2026-10-23: "We have the ability to do per cat grave states, we
should take advantage of that to enrich the models. Let's test three
different model sizes for the belief head as well and see what impact
size has on accuracy, especially in grave states." This file declares
that work before any data; collection runs on her word to the design
below. It is an ADDITION to Phase 1 (`../minifriend-phase1-2026-10-22/
RESULTS.md`, gated c0360c1d; F-064), never a re-read of it: the Phase 1
verdicts, its floor and F-064 stand as written. Nothing here changes
the prereg (frozen 18f06f84); the addition is recorded as
`../gen2-deviations.md` entry 11.

Prereg basis: §8 item 3 (the Phase 1 2 × 2, its strata, min-n 200
fail-closed with "the remedy is probe coverage, never a waived
stratum", the dissolution procedure pin, the 10%-of-trunk capacity
cap "engineering budget only, ratio reported as descriptor"); §8 item
4's shared ostrich bins. Everything Phase 1 declared about the target,
the input, the belief state, the strata, the alignment of observation
and truth, the split rule and the reads carries over unchanged; this
file states only what is new.

## Question

Two things Phase 1 could not answer:

1. **Is the grave skill real when only the friend is in distress?**
   Phase 1's grave stratum came from set G, where every cat starts
   grave together, so the observer's own self block was a proxy for
   the friend's state (RESULTS §Limitations, the second, "an upper
   bound on inference skill"). Spec 065's per-kitty `initial_needs`
   lets ONE cat start grave among four at the served default. That is
   the register the Phase 2 head will meet: a friend in trouble while
   the observer is not.
2. **Does head size move grave accuracy, and does the cap bind?**
   Phase 1 trained one width (GRU 24, 7,807 params, 9.2% of the
   trunk). Three widths bracket it: one well under the cap, the Phase
   1 width, and one over the cap as a declared probe that can never
   be a Phase 2 candidate but tells whether the 8,445 budget is what
   limits grave accuracy.

## Data

Sets L, W, G are Phase 1's recorded worlds with Phase 1's split
VERBATIM (`split.json` copies those three sets from Phase 1's file;
guard s1). New:

| set | worlds | ticks | config | purpose |
|---|---|---|---|---|
| P1..P5 (per-cat grave starts) | 20 per friend = 100, seeds 1095451 + 20·(k−1) … +19 (P1 Miso 1095451–1095470, P2 Biscuit –1095490, P3 Pumpkin –1095510, P4 Kittybear –1095530, P5 Clementine –1095550; SEED-BANDS row claimed 2026-10-23 before first burn) | 4,000 | `g2leg-20-P<k>.toml` = the served `g2leg-20.toml` plus ONE line in kitty k's `[[kitty]]` block: `initial_needs = { eat = { min = 60, max = 95 }, … bath = … }` (set G's band, per need, per spec 065's kitty × need draws); the other four kitties carry no entry and start at the served default (every need 0, happiness 100; FR-003) | GRAVE coverage per friend with the observer NOT grave |
| X1..X5 (reserved extension) | 20 per friend, 1095551 + 20·(k−1) …; same configs | 4,000 | run for friend k ONLY if P leaves k's mind-visible GRAVE stratum on the P eval worlds under 200; promoted into P_k by `split.py --extend Pk` (its 10/10 split is already drawn); after it, fail-closed |

Reset-only probe before this declaration (world generation, no tick
stepped): on the first seed of each block the grave kitty's reset
needs lie in 61–95 with happiness 19–24 (GRAVE by the happiness edge
at tick 0) and the other four sit at 0 / 100. The per-world GRAVE
yield under a non-grave observer is unknown — in G, Pumpkin yielded
about 21 mind-visible grave samples per eval world, Biscuit about 92
— which is why P takes half its worlds for evaluation (grave
coverage is the scarce thing; COMMON training data is abundant from
L) and why the extension block exists per friend.

Split (`split.py` → `split.json`, SPLIT_SEED 20261023, declared now):
per P block the 20 seeds are permuted once and the first 10 evaluate;
validation for early stopping is carved from the train worlds by
Phase 1's rule (round(0.2·n)). Heads train on the TRAIN worlds of L,
W, G and P1..P5 together (34 + 50 worlds before validation carving);
the DR weights are recomputed on that training set (the stratum
frequencies shift with P in). Min-n 200 per friend × stratum ×
version, FAIL-CLOSED, as in Phase 1.

## Heads

Phase 1's architecture (Linear(167 → h) + ReLU, GRU(h), Linear(h →
7)), loss (w · (mse5 + mse_hap + 0.1 · mse_bath)), optimiser, early
stopping and seeds, at three widths:

| width h | params | vs cap 8,445 | vs trunk 84,450 | role |
|---|---|---|---|---|
| 12 | 3,043 | under | 3.6% | the small candidate |
| 24 | 7,807 | under | 9.2% | Phase 1's width (retrained with P in the training set) |
| 48 | 22,519 | OVER (2.7×) | 26.7% | probe only: `--over-cap` must be passed; the manifest marks it; never a Phase 2 candidate |

× NF / DR × seeds 1, 2, 3 = 18 runs (`run_heads.sh`; the pair shares
its seed; six at a time). Run names `<HEAD>-h<h>-s<seed>` under
`results-raw/heads/` here. Widths 12 / 24 / 48 were chosen before any
run as roughly geometric steps (×2.6, ×2.9 in params) that place one
head on each side of the cap.

## Reads, declared now (all descriptive; rule 10)

`read_phase1b.py` runs Phase 1's reader unchanged (every cell, the
baselines, the dissolution procedure, the ostrich metric) once per
width and per evaluation GROUP — **P** = the eval worlds of P1..P5
(the clean per-cat grave read) and **G** = Phase 1's G eval worlds —
then adds two contrasts. Pooled = sample-weighted over the covered
friends, mean of three seeds, SD between seeds.

- **R1b. Accuracy by width.** Per width × head × stratum class × version,
  per friend then pooled, on group P; the marginal and persistence
  baselines beside (recomputed on the new training set). The headline
  grave number of this arc is the group-P mind-visible GRAVE cell.
- **R2b. Size effect.** r(h) = pooled loss at width h over the loss at
  width 24, per head × class × version, SD by first-order propagation
  (r · √(cv_h² + cv_24²)). A size effect is READ when |r − 1| exceeds
  that SD; otherwise the widths tie at the seed noise. The cap-binds
  question is r(48) on GRAVE: a READ ratio under 1 says capacity above
  the budget buys grave accuracy; a tie says it does not.
- **R3b. The dissolution procedure at each width** (Phase 1's R2,
  verbatim, on group P): informational. Phase 1's floor and verdict
  were set at Phase 1's first read and stand; a different outcome at
  another width is an input to the Phase 2 head choice (hers), never
  a replacement of the Phase 1 read.
- **R4b. The ostrich gap and signature** at each width × head on group P.
- **R5b. The all-grave confound.** q = GRAVE loss on group G over GRAVE
  loss on group P, per width × head × version, same SD rule: q over
  1 + SD says the all-grave worlds were harder than the per-cat ones,
  under 1 − SD easier. This quantifies Phase 1's second limitation.
- **R6b. Curves and the cap:** params per width against 8,445; epochs to
  the plateau per run; the over-cap flag on the 48 runs.

Coverage is reported per friend on group P before anything else; a
friend under min-n mind-visible after P and its extension is
insufficient coverage, first-class, as Phase 1 reported Pumpkin.

Not read: anything Phase 1 did not read (consumers, clone_fraction,
welfare claims); the G group's non-grave cells beyond R5b; any
comparison that pools P with G.

## Doctrine check (CLAUDE.md rule 8)

Phase 1's check carries over. What this file moves:

- Rule 10 moved the contrasts: ratios with a propagated SD and a stated
  READ rule, per friend before pooled, descriptive; the over-cap head
  is labelled a probe in the manifest and every table.
- Rule 12 (relief always available) is why P can exist: one covered
  mind per world starts grave with relief on the map and four
  flourishing companions; the stops below are the asymmetric remedy.
- Rules 5, 8, 9, 11: unchanged from Phase 1 (same input, same
  question, frozen policies, the same three bins).
- Rules 1–4, 6, 7: checked, moved nothing.
- FINDINGS read (rule 7): F-064 (the Phase 1 result this extends: the
  tension is friend-specific, Miso alone fails the clause; the per-cat
  sets are per friend by construction so that stays visible), F-060,
  F-063 (s7's water parking at Kittybear's seat), F-053 (the 1,000 line).

## Welfare (practice, owner 2026-09-26; stops ASYMMETRIC)

- P seats the certified roster in 100 worlds of 4,000 ticks: 2.0M
  covered cat-ticks, of which 100 cat-episodes (0.4M cat-ticks) begin
  in grave need and 400 begin at the served default. Per world the
  exposure is one cat, not five: lighter per world than G, more worlds.
- Extension X: up to 100 more worlds under the clause above (2.0M
  cat-ticks, 0.4M from grave starts), never for a friend already
  covered.
- Scouts-first, stricter than the three-world practice: ONE world per
  friend (the first seed of each block) runs alone with the F-053
  1,000-tick stop armed; `check_P.py` must report no abort on all five
  before the rest launch. Every world runs with the stop armed; an
  abort stops the set and goes to the owner.
- The heads add no rollout. The over-cap probe adds no rollout.
- Engine: the Phase 1 arc binding and venv (`../minifriend-phase1-2026-
  10-22/BINDING.md`, engine a2e8d044, the one that reproduced the
  certified battery rows), untouched; the Gen 2 lab venv is not used.
- Welfare-cost line: at most 4.0M covered cat-ticks, 0.8M of them from
  grave starts, for two reads: whether the grave skill survives a
  non-grave observer, and whether the Phase 2 head's size is the thing
  that limits it.

## Instrument and guards (each with a predicted red before trust)

- Phase 1 modules unchanged in behaviour: with `MINIFRIEND_ARC` unset,
  Phase 1's reader regenerated `phase1-read.json` identical to the
  committed file except for the new `eval_sets` key (checked 2026-10-23
  before this declaration); Phase 1's 16 guards pass.
- `train_heads.py --hidden / --over-cap` (Phase 1's guard h6: the three
  widths count 3,043 / 7,807 / 22,519; `check_cap` refuses 22,519
  without the flag; red: the cap comparison loosened).
- `split.py` (guard s1: L/W/G verbatim from Phase 1, P blocks 20
  contiguous seeds with 10/10, X blocks reserved and disjoint; red: the
  eval share moved).
- `make_configs.py` → the five tomls (guard s2: each parses to the
  served config plus exactly one kitty's six {60, 95} ranges; red: the
  band moved in the generator while the committed tomls stand).
- `read_phase1.py --eval-sets` (guard b2: reading ["G"] alone returns
  the G eval worlds and the recorded G coverage; red: the filter
  ignored).
- `read_phase1b.py` (guards b1, b3: ratio arithmetic and the READ rule
  by hand; the group contrast equals the two reads divided by hand;
  reds: the ratio pinned to 1; the groups swapped).
- `check_P.py` (guard after the scouts, on a recorded P world: the
  grave kitty's band and the others' default; red: the band check
  flipped). Declared now, run when the first scout exists.
- RESULTS.md gated by `/accuracy-gate` before commit; Collect and Read
  fences separate, runtime declared.

## Run order (each step its own commit before its data)

1. This declaration, `split.json`, the five configs, the drivers, the
   reader and the guards with their reds; deviations entry 11; the
   SEED-BANDS row. Then the owner's word to collect.
2. P scouts: one world per friend. `check_P.py`; no abort → the other
   19 per friend. `check_P.py` on all 100; `count_strata.py` on the P
   eval worlds. Extension clause applied per friend, if it fires.
3. Heads: `run_heads.sh` (18 runs). Pins carried from Phase 1 step 4:
   chunk 500, hidden carried detached, Adam 1e-3, batch 128 sequences,
   patience 10 / margin 1e-4 / cap 200 epochs, BATH_WEIGHT 0.1, DR
   weights from the training set only, cap 50× COMMON.
4. `read_phase1b.py --md`; RESULTS.md; gate; F-entry if the read earns
   one (an addendum to F-064 is the default if the size effect is a
   tie and the per-cat grave numbers match Phase 1's).
