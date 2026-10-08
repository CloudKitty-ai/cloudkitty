# partner_absent split — declaration (2026-10-07)

Characterization read feeding the #389 agenda's absent-partner-calls
ruling (the owner asked 2026-10-07 for a data-driven decision). No
decision rule here: the output is the three-bucket proportion, and the
ruling stays the owner's. Declared before collection.

**Question.** Of the served roster's `partner_absent` refusals, what
share was, at decision time: a proposal at an adjacent partner who
moved before the caller's turn (**race**), a proposal at a visible but
never-adjacent partner (**seen**), or a proposal at a partner outside
the caller's vision disc (**fog**)?

**Welfare cost: none.** Read-only HTTP GETs against the served box; no
world, config, or roster change.

## Join rule (derived from the engine, pinned here)

- A refusal event stamps the tick it was heard, **before** the tick
  increment (`crates/cloudkitty-core/src/world.rs:372`, phase 2).
- `self.tick += 1` runs at the end of phase 4 (`world.rs:434`), and
  phase 5 publishes `snapshot()` carrying the incremented tick. So the
  published snapshot labeled T holds the post-apply positions of tick
  T−1 = the start-of-tick positions every kitty decided against at
  tick T.
- Therefore: refusal at tick N joins the captured `/world` snapshot
  whose `tick == N`. Equal-tick join, no offset.

## Buckets (precedence order; geometry from the engine)

1. **race** — target at Manhattan distance ≤ 1 from the caller at tick
   start (`grid.rs:42` `is_adjacent`). The proposal was legal against
   the snapshot the mind decided on; the refusal means the partner
   moved earlier in the same tick's turn order. Includes distance 0.
2. **seen** — not adjacent, but inside the vision disc:
   dx² + dy² ≤ r² (`grid.rs:80` `visible_from`), r = the served
   `/config` `vision.radius` (4 at declaration time, re-read from the
   collection's stored config). The diagonal neighbour (1,1) lands
   here, not in race: Manhattan 2, d² = 2.
3. **fog** — outside the disc: the proposal was at a remembered or
   heard position.

Target id extraction, from real payloads (refusal-baseline raws):
`{"action":"sleep"|"rest","with":N}` → N;
`{"action":"groom","target":N}` → N;
`{"action":"play","target":"kitty","id":N}` → N.

## Window and drop rules

- Window: 7,500 served ticks (~100 min at 800 ms/tick), wall cap
  150 min. Expected ~480 `partner_absent` rows at the baseline's
  286/h.
- Positions: `/world` polled ~0.55 s; a tick's positions recorded the
  first time that tick is seen. Coverage = captured ticks / window
  ticks, reported.
- Drop rule: a `partner_absent` row whose tick has no captured
  snapshot is dropped and counted (never guessed from neighbouring
  ticks). Refusal-ring rollover gaps between polls are flagged as in
  the baseline collector.
- Dedupe on (kitty_id, tick, proposed-json), the baseline's row key.

## Output

Per bucket: count, share of joined `partner_absent` rows, absorbed
share, by proposal label; per seat and roster-wide. Plus: joined vs
dropped counts, tick coverage, window bounds, provenance (instrument
stamp + served halves), the stored `/config`.

## Regeneration

### Collect

```
cd /Users/elizabethkelly/ai/cloudkitty/experiments/partner-absent-split-2026-10-07
python3 collect_split.py 7500
```

(~100 min live; writes `results-raw/partner-absent-split-<start_tick>.json`)

### Read

```
cd /Users/elizabethkelly/ai/cloudkitty/experiments/partner-absent-split-2026-10-07
python3 split_read.py results-raw/partner-absent-split-<start_tick>.json --out /tmp/split-read.json
```

(runtime: seconds; prints the per-bucket table and every derived
column; `--out` writes the JSON the table is rendered from)
