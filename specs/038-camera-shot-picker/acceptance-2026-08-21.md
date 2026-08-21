# Acceptance measurement — 2026-08-21 (T025)

**Provenance**: 350 ticks (4.7 min) captured from a local five-kitty world
(`cloudkitty.toml`, `--fresh`), replayed through the REAL `Camera` at 8
frames per tick. **The capture is the SAME generation as the committed
reference sample** — same seed + config ⇒ same world (Article V working as
designed) — so model-vs-camera comparisons here are same-data and clean,
but an *independent* generation needs a seed change (owner's call whether
to vary it at the dial pass). Replay tooling: scratchpad
`acceptance-replay.mjs` (drives `client/anim.js` verbatim).

## Desktop (1000px, ceiling 13.33t) — every bar met

| SC | Bar | Measured | |
|---|---|---|---|
| SC-001 rest | ≥ 60% of ticks | **86%** | PASS |
| SC-002 ≥2 framed | ≥ 99%; zero-kitty never outside a pan | **100%; 0 zero-kitty frames** | PASS |
| SC-003 re-framing | ≤ 3/min; pans ≤ 0.5/min | **3.00/min** (widen 0.86, shed 2.14, break 0, pan 0) | PASS — **at the line** |
| SC-004 zoom | at-ceiling ≤ 20%; size ≥ 1.2× | **3%; 1.36×** (median width 9.84t) | PASS |
| SC-005 interest | maximal-or-tied ≥ 90%; mean ≥ 3 | **90%; 3.27** | PASS — **at the line** |

Corrections (gentle in-shot moves, deliberately outside SC-003): 9.0/min —
the price of the tighten; rest stays 86%. The owner judges the *feel* live
(T026).

## Phone (380px, ceiling 7.6t)

| SC | Bar | Measured | |
|---|---|---|---|
| SC-001 rest | ≥ 60% | **87%** | PASS |
| SC-002 ≥2 framed | ≥ 99% | **100%; 0 zero-kitty** | PASS |
| SC-010 breaks | ≤ 1/min | **0.43/min** | PASS |
| SC-003 re-framing | ≤ 3/min | **3.43/min** (shed 3.00) | **MISS by 0.43** |
| — overflow | (expected 42–61%) | at-ceiling 44% | as modelled |

**The phone SC-003 miss is structural and surfaced, not smoothed over**: a
7.6-tile frame holds less, so groups exit fit more often, and sheds are
the grammar's honest response. SC-003 was written unscoped by viewport
while SC-010 already gives the phone its own bars — whether SC-003 should
be viewport-scoped (or the phone dwell dialled higher) is the owner's
call at the dial pass. Raising `shedDwellTicks` further trades real
dispersal responsiveness for the last 0.43/min.

## What the measurement changed (mechanism history)

First replay (before fixes): re-framing 4.29/min desktop / 8.57 phone,
size 1.16×, maximal-or-tied 86%. Two causes, two fixes:

1. **Shed flap.** Membership-join is free (FR-008) but sheds fired the
   first un-fit tick, so link-boundary churn produced join/shed cycles at
   3–8/min. The reference model never counted sheds at all — SC-003's bar
   was set blind to them. Fix: `shedDwellTicks` (3) — persistence before
   action, the grammar's own principle, applied to the one rule that
   lacked it. Spec FR-010 amended with a dated note.
2. **Stale-wide frames.** Width changed only at membership events; a
   gathered group kept its old wide frame (median 11.48t vs the fit's
   9.2t → kitties 1.16×). Fix: the hold eases tighter once the frame
   exceeds need by `tightenFrac` — set 1.3 first, which sat ABOVE the
   measured 1.25 median oversize and never fired; 1.15 works. The dial
   must sit below the drift it exists to catch.

Both mechanisms carry harness checks with verified mutations (shed-dwell
removed → red; tighten unreachable → red).

## Open for T026 (owner's live gate)

- Judge the feel at 3/4/5 kitties and on the handset (SC-010).
- The two at-the-line bars (SC-003 3.00, SC-005 90%) have zero margin —
  dial moves will swing them either way.
- The phone SC-003 ruling (scope it, or dial for it).
- Dial pass per house method; consider a seed change for an independent
  generation.
