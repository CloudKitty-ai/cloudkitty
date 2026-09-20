# LLM lab seat: results

## First read of `env.decision_request` (spec 055), 2026-09-20

Surface merged at 7612297 (PR #400). Lab binding rebuilt from that
commit into the exp-006 venv. Instrument: `first_read.py`; raw:
`results-raw/first-read-7612297.{json,output}` (uncommitted, house
rule). World: tier 2's `package.toml`, all five seats scripted, seeds
1093001–1093005 (ledger row), 5,000 ticks each, every kitty rendered
three times per tick (int id, `"kitty_N"`, int id again) in one run and
never in a twin run.

Checks, all held on every one of the 25,000 windows:

- R1 the three renders in a window are byte-equal.
- R2 the line carries the wire's seven keys, `v` 3, `tick` and
  `kitty_id` matching the window, `me.id` the kitty.
- R3 the twin run without any call reaches the same state vector every
  tick (SHA over 5,000 states per seed).
- R4 a call before the first reset raises ValueError ("reset first");
  an unknown id raises ValueError naming it.

Three mutate.sh reds on the instrument at 1 × 200 (twin run on the
wrong seed → R3; the name form rendering a different kitty → R1;
window counted from 1 → R2).

Reads for the seat's design:

| quantity | value |
|---|---|
| render time | 10.1 µs per call (5 kitties × 3 calls per tick, free at any screen scale) |
| request line, bytes | min 4,224, mean 9,800–10,260 per kitty, max 14,608 |
| `seed` field | distinct across kitties at tick 0; changes every tick for every kitty (4,999 of 4,999) |

Where the bytes sit at tick 3,000 for kitty 1: `config` 3,426
(constant for the episode), `world.recent_meows` 3,200–5,300 (the
largest variable block), `world.kitties` 600–4,400 with the number of
kitties in view, `me` 600–1,050, `world.elements` 140–360.

What this means for the seat. The wire line is the ground truth the
lab renders, and it is about 10 KB of JSON per decision, most of it
constant config and the meow log. An LLM seat will not be fed the line
verbatim; the harness renders a compact prompt from the parsed
document (the brainstorm's prefix carries the world rules once, the
per-tick body carries me, the kitties and elements in view, and the
recent meows trimmed to the window that matters). The seed changes per
tick and per kitty, so it is the per-decision tie-break the served
advisor would see and nothing the prompt needs. Nothing further waits
on Product for the seat; the next step is the owner's #392 definition.
