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

**SUPERSEDED same day — see the post-review re-measurement below: the
miss was not structural after all.** The sheds pushing the phone over the
bar were zero-dwell flap sheds let through by the overflow counter bug
(review finding 2); with overflow ticks banking no dwell, the phone
passes with margin and no ruling is needed.

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

## Post-review re-measurement — 2026-08-21, commit 8cffb3f

The medium code review confirmed 8 findings (+3 below its cap); all were
remediated with red-first guards (harness 260 → 268). Same capture, same
replay, through the fixed camera:

| | Desktop (1000px) | Phone (380px) |
|---|---|---|
| SC-001 rest | **86%** (unchanged) | **90%** (was 87) |
| SC-002 ≥2 framed / zero-kitty | **100% / 0** | **100% / 0** |
| SC-003 re-framing | **3.00/min** (widen 0.86, shed 2.14) — still at the line | **2.36/min** (shed 1.93, break 0.43) — **PASS, was 3.43 MISS** |
| SC-004 zoom | at-ceiling **3%**, size **1.36×** | at-ceiling 51%, size 1.75× (overflow regime, as modelled) |
| SC-005 interest | **90% / 3.29** — still at the line | **100% / 3.05** |
| SC-010 breaks | 0 | **0.43/min** |

**The phone SC-003 story resolved itself**: the over-bar sheds were the
overflow-counter bug's zero-dwell flaps (finding 2), not the phone's
structure. With the dwell honest, the phone passes with 0.64/min of
margin — the ruling request in the section above is withdrawn. At-ceiling
rose 44 → 51% because the dwell now (correctly) holds overflow shots
whole through boundary flaps; SC-004's at-ceiling bar is desktop-scoped
and unaffected. Desktop moved on no bar.

Behavioural fixes folded into these numbers: re-aim-in-flight (a fence
walker is now kept in frame), empty-roster ease-home, still-frame hold
guard, follow-companion dwell, follow-tap-overrides-pan (owner ruling),
one-heir evidence chains. Full list: commit 8cffb3f and the amended
contract.

## Second re-measurement — 2026-08-21, commit a7c0dcc (high review)

A high-effort review of the remediated branch confirmed 10 further
findings (edge-transition and guard-strength class); all fixed red-first
(harness 268 → 276). Same capture, same replay:

- **Desktop: bit-identical on every number** — rest 86%, re-framing
  3.00/min, at-ceiling 3%, size 1.36×, maximal-or-tied 90% / 3.29.
- **Phone: every bar still passes**, slightly better where it moved —
  re-framing 2.36/min unchanged, rest 90% unchanged, median width
  7.80 → 7.00 (the floor; the shed licence and re-latch hysteresis stop
  frames idling wide), size 1.75× → 1.9×, at-ceiling 51 → 48%.

Behavioural deltas folded in: re-latch hysteresis (`relatchTiles` 0.5 —
no single-frame cut on membership absorptions or generation snaps),
decisions gated off still frames (taps/toggles read the drawn world),
reduced-motion mid-episode arrival, the shed licence (a shed that cannot
restore fit never fires), one shed clock for both modes, order-proof
window ties, strict-majority chains, and a second recorded harness
window (ticks 164–238) chosen because the dwell demonstrably has teeth
there — the first SC-003 guard that can fail on real data in CI.

## T026 dial pass, first live session — 2026-08-21

The owner judged the live world: framing "much better", but chained
corrections read as "fits and starts" and both speeds too fast. Her
rulings, all implemented: **moveMs 2000 / panMs 3000** (judged live
through 700 → 1000 → 2000), and the **velocity-carry amendment** (FR-007
dated note): re-latches inherit momentum on a Hermite, so a tracked
walker never passes through a stop; `relatchTiles` retired same-day.

Full-capture replay at her dials: **desktop rest 66%, re-framing
2.79/min (OFF the line at last), corrections 5.14/min (was 9.0) —
chained pursuits now count once; at-ceiling 1%, size 1.36×, maximal 90%
/ 3.29. Phone rest 71%, re-framing 2.36/min, size 1.85×.** Every SC
passes both viewports; SC-001 dropped 86→66 desktop (the price of 2s
moves, well above the 60% bar). The flap-window harness check re-pinned
at its measured 53% rest (motion-heavy by construction; the full capture
owns SC-001).

## Open for T026 (owner's live gate)

- Judge the feel at 3/4/5 kitties and on the handset (SC-010).
- The two at-the-line DESKTOP bars (SC-003 3.00, SC-005 90%) have zero
  margin — dial moves will swing them either way. The phone now has
  margin everywhere.
- Dial pass per house method; consider a seed change for an independent
  generation.
