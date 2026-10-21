# Play decomposition, Gen 2 — declaration (2026-10-21)

Authorization: owner, 2026-10-21. Her list, verbatim: "Analyze: where
play increase comes from"; her word on Experiments' proposal (the play
decomposition first, reads of existing raws plus scripted runs):
"Recommendation accepted". Recorded in
`../fog-gen2-timeline-2026-10-17.md` §Outstanding owner items. Committed
before any cell data. An instrument smoke of 5 ticks per cell ran before
this commit (each cell loads and steps through the collector); nothing
from it is kept.

## Question

The certified Gen 2 roster plays 0.319–0.413 of cat-ticks (exact;
`../seating-analysis-g2-2026-10-21/RESULTS.md` §Correction). The Gen 1
roster played 0.033–0.080, Biscuit 0.227–0.450 (flag-only ranges;
`../seating-analysis-2026-09-28/RESULTS.md` §Correction). Four things
changed together between those two readings:

1. The world: `fog-gen1-cert/anchor-b3.toml` (the Gen 1 seating and cert
   world) → `gen2-comparator-legs-2026-10-14/g2leg-20.toml` (the prereg's
   diff at freeze, `../gen2-prereg-2026-10-17.md` §"diff").
2. The scripted behaviors: Gen 1 seats ran `needs_driven` ×4 and Biscuit
   `playful`; Gen 2 seats all run `teacher` (`Teacher::GEN2`, every rung
   on). The presets differ in exactly two rungs that touch play: the
   luxury rung (play when `weighted_pressure < playful_comfort`), which
   `needs_driven` lacks, and partner responses, which neither Gen 1 preset
   has (`crates/cloudkitty-core/src/behavior/teacher.rs`).
3. Two dials: `playful_comfort` 55 → 30 and `consent_line` off → 30.
   Gen 1's TRAINING world (`fog-gen1-shakeout/anchor.toml`) ran 55/off;
   its seating world `anchor-b3.toml` already ran 30/30. So the Gen 1
   reading is a roster trained under 55/off and read under 30/30.
4. The training: Gen 2's trunk PPO on the Gen 2 corpus. The Gen 2 teacher
   itself plays 0.142–0.233 on the certified roster's own worlds, so the
   networks play about twice their teacher.

This arc attributes the rise across those factors and characterizes the
networks' extra play. Descriptive under doctrine rule 10: nothing here is
a bar, and nothing here decides a dial.

## Cells (all scripted; no covered minds)

Collector `../seating-analysis-g2-2026-10-21/seating_collect_g2.py` with
its new `--config`; seeds 905001–905005; 20,000 ticks; `--abort-streak
1000`. W2 = the Gen 2 world, W1 = the Gen 1 seating world; d2 = the Gen 2
dials (30/30), d1 = the Gen 1 training dials (55, consent 0); teacher =
`Teacher::GEN2` on every seat, gen1b = `needs_driven` ×4 + Biscuit
`playful`.

| cell | world | behaviors | dials | config | status |
|---|---|---|---|---|---|
| C1 | W2 | teacher | d2 | `g2leg-20.toml` as served | EXISTS: `../seating-analysis-g2-2026-10-21/results-raw/applied/scripted/`, not re-run |
| C2 | W2 | teacher | d1 | `w2-teacher-d1.toml` | runs |
| C3 | W2 | gen1b | d2 | `w2-gen1b-d2.toml` | runs |
| C4 | W2 | gen1b | d1 | `w2-gen1b-d1.toml` | runs |
| C5 | W1 | gen1b | d2 | `../fog-gen1-cert/anchor-b3.toml` as is | runs |
| C6 | W1 | gen1b | d1 | `w1-gen1b-d1.toml` | runs |

Each cell toml is its source with only the named lines changed (the
header of each says so; `diff` against the source shows 6, 12, 16 and 6
changed lines for C2, C3, C4, C6). The W2 cells share seeds with C1 and
the trained roster, so W2 differences are paired by world. W1 cells use
the same seed numbers on a different world: W1-vs-W2 differences are
unpaired.

Trained references, already recorded, not re-run:

- N2: the certified roster rot2, exact streams,
  `../seating-analysis-g2-2026-10-21/results-raw/applied/g2-rot2/`.
- N1: the Gen 1 roster on anchor-b3,
  `../seating-analysis-2026-09-28/results-raw/streams-90050[1-5].npz`,
  flag-only; play reads as a floor..ceiling range (`flag_estimate`).

## Definitions

- Play share: ticks whose activity is play over all ticks, per cat, on
  the corrected streams (`seating_read.corrected_streams`: the flag where
  it shows a scene, the applied action where it shows Idle). On N1's
  flag-only streams, the `flag_estimate` range.
- Kitty play: play ticks with a partner (the flag's partner, else
  `applied_with` ≥ 0). Element/solo play: the rest.
- Scene start: the first tick of a play run. Needs at a start are read
  one tick earlier (snapshots are post-apply).
- Worst other need: the largest of eat, drink, sleep, cuddle, bath.
- Pooled: cat-ticks pooled over the five cats of a world.

## Reads, declared now

R1. **The ladder.** Play share per cat and pooled, per cell and for N2,
mean over the five worlds with the between-world SD; N1 as a range. The
factor differences, each with its paired per-world SD where paired:
dials on the Gen 2 teacher, C2 − C1; dials on the Gen 1 behaviors, C4 −
C3; behaviors at Gen 2 dials, C3 − C1; behaviors at Gen 1 dials, C4 −
C2; world under the Gen 1 behaviors, C5 − C3 and C6 − C4 (unpaired);
training, Gen 2: N2 − C1 (paired); training, Gen 1: N1 − C5 (a range
against a mean). A difference inside its SD is reported as inside noise
and establishes nothing (rule 10). Five worlds per cell, stated with
every number.

R2. **Composition of the networks' extra play**, N2 against C1, per cat,
paired by world: kitty play vs element/solo play shares; scene counts
and mean scene length (inclusive); and, networks only, the share of
kitty-play starts on which both parties chose a PlayKitty action that
tick. The engine's proposer and acceptor roles are not in the streams
(the applied stream records partner play on both cats: 14,184 of 14,422
partner-play ticks in rot2 905001 show each playing with the other, and
scripted seats have no chosen-action stream), so no proposer/acceptor
split is read.

R3. **Displacement**: per-activity share differences N2 − C1 per cat,
paired: idle, rest, sleep, eat, drink, groom, play; and inside idle,
move, chase, purr, meow from the applied stream. Names which activities
the extra play ticks came out of.

R4. **Pressure at onset.** At each play scene start, the play need and
the worst other need, one tick earlier. Per cat for N2 and C1 (and C3,
the Gen 1 behaviors on the same worlds): the median play need at onset;
the share of starts with the worst other need above 30 (the served
consent line and `playful_comfort`: play begun while another need sits
past the teacher's own luxury gate) and above 50. This is the reward-side
signature named in `../gen2-deviations.md` entry 3 (play is the one need
whose distress carries no value penalty): if the networks start play
under more other-need pressure than their teacher, that hypothesis gains
a measured footing; if not, it loses one. A reading either way, never a
ruling.

R5. **Where the happiness gain sits.** Per cat, mean need by kind, N2 −
C1 paired, each weighted by the served happiness weight
(`g2leg-20.toml` `[happiness]`: eat .20, drink .20, sleep .15, play .15,
cuddle .15, bath .15), so the +5.566 team gain the certificate measured
at 20×20 (`../gen2-cert-battery-2026-10-20/RESULTS.md` §Phase C) is
shown need by need. Unclamped per-need arithmetic on the recorded
streams; the certificate's own number is not recomputed here.

Not read: speech (rule 6; scripted seats record none); refusals
(deferred, as in v1 and v2); any Gen 2 network under altered dials (a
frozen roster shifts, never answers, rule 9, and it would seat covered
minds).

## Doctrine check (CLAUDE.md rule 8)

- Rule 9 moved a choice: the dial cells run scripted behaviors only, and
  no network runs under 55/off. The read says nothing about redeploying
  either dial; a dial change is a Gen 3 boundary decision.
- Rule 10 moved the reporting: descriptive throughout, paired per-world
  SD, inside-noise differences establish nothing, n = 5 worlds stated.
- Rule 6 moved R2's scope: no speech from scripted cells, no claim about
  the free register.
- Rule 7: the read feeds the play-economy question banked for Gen 3
  (deviations entry 3); it proposes no world change.
- Rules 1–5, 8, 11, 12: checked, moved nothing (no reward, price, teacher
  or world change ships from here; no invalidation clause; relief
  untouched).
- FINDINGS read (CLAUDE.md rule 7): F-038 (the comfort dial buys food
  promptness and pays in element play, never duets), F-057, F-058 and
  F-059 (Gen 1's enrichment arc never cleared the 0.10 play bar while
  trained; above-bar capacity existed behind E-conditioned suppression).
  Gen 2's 0.32–0.41 sits far past that bar on a different world, teacher
  and reward; this arc does not read against the bar.

## Stops and welfare

- No covered minds in any new cell. Welfare-cost line: 0 covered
  cat-ticks; the trained references are streams already recorded (their
  cost lines are in their own declarations). No scouts: nothing covered,
  served size.
- `--abort-streak 1000` armed on every cell (the collector's default). An
  abort in a scripted cell is reported; the cell is read to the abort
  and flagged in every table it enters.
- C1 and N2 passed the same-world check at Amendment 1 (`same_world.py`);
  the new cells are different worlds by construction, so no identity
  check applies to them.

## Instrument

- Collector: `seating_collect_g2.py` gains `--config` (default unchanged,
  `g2leg-20.toml`). Guard, in `test_seating_g2.py`: a CLI run with a cell
  config records that config's name and sha256 in meta and provenance.
  Red via `scripts/mutate.sh`: drop the pass-through in `main()`, and the
  guard must fail naming `g2leg-20.toml`.
- Reader: `decomp_read.py` here, on `seating_read.corrected_streams` and
  `flag_estimate`; `--out decomp-read.json --md`. Guards, each with a
  predicted red before it runs: (g1) a play share on a recorded stream
  equals an independent count; (g2) the onset needs are read one tick
  earlier (shifting the fixture by one tick changes the answer); (g3)
  R5's weights and need order match the engine: the needs-derived
  happiness equals the recorded `hap` stream on rot2 905001 (no clamp
  binds there) within 0.05 per cat.
- Both scripts run from the lab venv
  (`../exp-006-character-gen/.venv`, `python3 -B`).

## Run

```
cd experiments/play-decomposition-g2-2026-10-21 && bash run_cells.sh
```

Five seeds in parallel per cell, cells in sequence (C2, C3, C4, C5, C6),
streams into `results-raw/<cell>/streams-<seed>.npz`, log
`results-raw/run.log`. Scripted cells took about 8 s for five worlds at
Amendment 1.

## Read

```
cd experiments/play-decomposition-g2-2026-10-21 && VIRTUAL_ENV=/Users/elizabethkelly/ai/cloudkitty/experiments/exp-006-character-gen/.venv /Users/elizabethkelly/ai/cloudkitty/experiments/exp-006-character-gen/.venv/bin/python3 -B decomp_read.py --out decomp-read.json --md
```

RESULTS.md follows, gated by `/accuracy-gate` before commit.
