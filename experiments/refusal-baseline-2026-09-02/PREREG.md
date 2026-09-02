# Live refusal baseline (spec 046) — prereg, 2026-09-02

Declared before collection. The served world is the 2026-09-02 deploy:
046 refusal stamp (`/events/refusal`, capacity 6,000), 047
`consent_line` inert at 0, 048 no-stale-reproposal, 044/045 inert with
the boot line "waterline contagion disabled". Roster: Miso (1),
Biscuit (2), Pumpkin (3), Kittybear (4), Clementine (5); first ring row
at tick 1,295,021 (the boot).

## Purpose

Two numbers the timeline is waiting on before the v2.10 tag:

1. The per-seat taxed refusal share on the served world, in the step-5
   pin's currency (INVESTIGATE at >10% of a seat's ticks). This is the
   first read off the stamp itself; the seam-probe numbers (F-033
   Biscuit 4.7%, the 3.5% INVESTIGATE line) are pre-048 and are history,
   because b9f9c00 removed the dead-scene refusal rows. This read is the
   new reference, not a pass/fail against the old one.
2. The combined (taxed + absorbed) refusal density, which re-derives the
   ring retention: FR-004 wants at least 15,000 ticks held; 6,000 was
   sized on taxed density alone (0.23/tick) plus headroom.

## Measure

- Window: 15,000 ticks from the first poll (FR-004's window; about 3.3 h
  at the measured 1.27 ticks/s). Poll `/events/refusal` + `/world` every
  120 s; rows deduped on (kitty_id, tick, proposed); a poll whose
  oldest row is newer than the previous newest is a rollover gap and
  invalidates the window.
- Per seat: `taxed_share` = rows with `absorbed == false` / window ticks;
  `absorbed_share` likewise; taxed rows by proposed action and target
  kind. Roster: combined density per tick; `retention_floor_15k` =
  density × 15,000 rounded.
- Instrument: `refusal_baseline.py` (collector, stamps
  `census_provenance.stamp` + `served`), `score_refusal.py` (scorer,
  guarded by `test_score_refusal.py` on a recorded ring payload,
  9 pins, four mutants red).

## Decision rules

- Any seat's taxed share >10% → INVESTIGATE per the step-5 pin; the
  baseline is still valid, the pin fires early.
- `retention_floor_15k` > 6,000 → Product re-derives the knob by config
  (spec 046 caveat); ≤ 6,000 → the default stands.
- Zero gaps required; a gap means the window is re-run at a shorter
  interval.
- Neither number blocks the tag unless the pin fires.

## Reporting

RESULTS.md: the score table, gaps, provenance (served config hash +
instrument head), and the retention verdict. Raw stays in results-raw,
uncommitted.
