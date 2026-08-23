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

## T026 calm pass — 2026-08-21, second live session

The owner, on the shipped-candidate feel: "calm static periods look
great; periods with a lot of movement look not as great," then "get the
median calm spell up." Measured anatomy: the busy periods were
MEMBERSHIP re-frames (sheds median 4.8t travel + 3.3t zoom in one move)
and instant corrections. Her judged remedies, all baked:

- **nearDwellTicks 5 → 10** (slower to court a 4th/5th group),
  **safeZoneFrac 0.80 → 0.88**, **tightenFrac 1.15 → 1.2** (1.3 doubled
  calm but broke SC-004's 1.2× size floor — rejected on measurement).
- **Shed/break decomposition**: an in-band re-frame lands at HELD width;
  the breathe-in owns the zoom from rest (FR-010 amendment).
- **pressDwellTicks 3** (FR-007 amendment): a press must persist ~2.4s
  before a correction; frame-edge and empty-frame escapes bypass it
  (without them, measurement showed 9 zero-kitty frames).
- **SC-005 amended 90 → 80%** (owner ruling: "~3 is the target" outranks
  strict numbers-win; measured 85%). **SC-002's transit exemption
  widened** to any eased re-frame's moving middle (one 100ms mid-break
  empty frame on the phone at 2s durations — the pan clause's own
  phenomenon at smaller scale).

Final numbers, full capture: **desktop rest 78%, 74% of ticks fully
still, median calm spell 4.8s (longest 30s), re-framing 1.93/min, size
1.51×, maximal 85%, zero empty frames. Phone rest 79%, re-framing
2.36/min, size 1.75×, one mid-break transit frame (exempted above).**
Harness 279 motion / 88 meadow, every new mechanism seen red first.

## Open for T026 (owner's live gate)

- Judge the feel at 3/4/5 kitties and on the handset (SC-010).
- The two at-the-line DESKTOP bars (SC-003 3.00, SC-005 90%) have zero
  margin — dial moves will swing them either way. The phone now has
  margin everywhere.
- Dial pass per house method; consider a seed change for an independent
  generation.

## Re-census on the LIVE world — 2026-08-22, after the Biscuit 2.0 cutover

The owner asked for the stats again now that Biscuit 2.0 is seated
("she wanders a lot more"). Two independent windows captured from the
**served** world (`wss://kitties.ai/ws`, ticks 143174+ and 143520+) —
350 ticks (4.7 min) and 900 ticks (12 min) — replayed through the
deployed `Camera` at 8 frames/tick. Tooling now committed beside the
older sampler: `client-measurements/camera-aim/live-sample.mjs` and
`acceptance-replay.mjs` (the T026 replay plus the two calm statistics
the dial pass reported; every pre-existing formula carried over
unchanged).

**Read the comparison with its confound in view.** The banked numbers
came from a LOCAL `--fresh` world on the *previous* roster; this is the
served generation on the *current* one. Roster and generation moved
together, so this is "what the camera does on the world she is watching",
not a clean A/B of Biscuit 2.0. The two windows agree with each other,
so the desktop result is not a sampling artefact.

| Desktop (1000px) | T026 banked | 350t | 900t |
|---|---|---|---|
| SC-001 rest | 78% | **54%** | **54%** — **MISS** (bar ≥ 60%) |
| ticks fully still | 74% | 47% | 48% |
| median calm spell | 4.8s | 1.5s | 2.3s (longest 30.8s) |
| SC-003 re-framing | 1.93/min | 1.50 | **1.17** — PASS, better |
| corrections | (~6.6 implied) | 7.93 | 6.33 |
| SC-004 size | 1.51× | 1.36× | **1.51×** — PASS |
| SC-005 maximal / mean | 85% / — | 99% / 4.69 | **96% / 4.57** — PASS |
| SC-002 ≥2 framed | 100% / 0 | 100% / 0 | 100% / 0 |

| Phone (380px) | T026 banked | 350t | 900t |
|---|---|---|---|
| SC-001 rest | 79% | 83% | **79%** — unchanged |
| median calm spell | — | 5.5s | 4.7s (longest 56.7s) |
| SC-003 re-framing | 2.36/min | 1.71 | **1.75** — PASS |
| SC-004 size | 1.75× | 1.75× | **1.75×** |
| SC-002 zero-kitty | 1 (exempted) | 0 | 3, **all inside one eased shed** (progress 0.05–0.15) — covered by the transit exemption |

**Mechanism, and it is not thrash.** Membership churn went DOWN (1.93 →
1.17/min); what rose is the gentle in-shot correction. The clowder is
now tight — mean bounding span 6.5 tiles, within 8 tiles on 69% of ticks
— so a single legal shot holds nearly everyone: mean framed 3.27 → 4.57,
maximal-or-tied 85% → 96%. Five cats milling inside one frame press the
safe zone almost continuously, and each press buys a 2s eased
correction; ~6.3/min of those is the whole calm budget. The camera is
not hunting between shots, it is drift-following a crowd it is
successfully holding.

**Per-cat, 12 min.** Biscuit is not the biggest mover by step count —
she steps on 36% of ticks against Pumpkin's 40% — but her *mix* is
distinct: chase 34% + play 29%, i.e. 63% of ticks in bursty pursuit,
roaming 14x8 tiles. Pumpkin roams widest (18x17). So the owner's read is
real, but the camera cost comes from group COHESION more than from any
one cat's mileage.

**Open for the owner** — the calm/interest trade is now live, and her own
SC-005 ruling ("~3 is the target") sits against a measured mean of 4.57:

1. `safeZoneFrac` 0.88 → ~0.92 — a wider deadzone before a press counts.
   Most directly aimed at the corrections that cost the calm.
2. `pressDwellTicks` 3 → 5 — more persistence before correcting; the
   lever she already used once at T026.
3. Structural: stop ADMITTING once the shot holds ~3 (a good-enough
   rule), trading maximal-or-tied% for calm. This is the one that matches
   her stated target and the one that needs a spec amendment.

No dial was moved on the strength of this measurement.

### Follow-up: what the structural option would actually take — 2026-08-22

Asked what the "stop admitting at ~3" option looks like. Measured on the
same 900-tick capture, and **the option as stated is inert on this
world**:

- **Groups are atomic to the shot.** `bestWindowFor` admits a seed group
  WHOLE (its own comment: "even when it alone overflows") and then grows
  by whole groups while the union still fits the ceiling. No stopping
  rule can shoot fewer cats than one group holds.
- **One group usually holds nearly everyone.** At the shipped
  `linkTiles: 5`, the clowder is a SINGLE group on 61% of ticks, and a
  group of ≥4 exists on 79%.
- Simulated both readings — splitting oversized groups, and stopping the
  greedy growth at `enough` while preferring the tightest window — and
  mean framed moved 4.57 → 4.53 → 4.51 (stop-at-2). Rest and calm moved
  by a point. It never binds.
- Lowering `linkTiles` does not rescue it: at L=3 a ≥4 group still exists
  on 64% of ticks, and the 2026-08-20 finding (identity survives minutes
  at L=5) says a smaller L trades this for flickering identity — i.e.
  more churn, which is what `shedDwellTicks` exists to suppress.

So the real structural change is **letting a shot be a SUBSET of a
group** — the grammar's unit stops being the group and becomes a cat
set. That needs a new selection objective (which three?), its own
membership hysteresis (today stability is free, inherited from group
identity; a subset has none, so the flap problem returns one level down),
a rule for the "why is she cut off?" case when an excluded cat stands
beside an included one, and amendments to FR-003, SC-005 and the grammar
contract.

**And it would not fix the thing being complained about.** The corrections
come from the HOLD, not from the shot's size: a three-cat shot still
chases its three cats. The dials say so directly — same capture, desktop,
shipped `Camera` with dials injected:

| config | rest | ticks still | median calm | corr/min | re-fr/min | size | member outside | zero-kitty |
|---|---|---|---|---|---|---|---|---|
| shipped (0.88 / 3) | 54% | 48% | 2.3s | 6.3 | 1.17 | 1.51× | 1% | 0 |
| **safeZoneFrac 0.92** | **81%** | **77%** | **4.4s** | 4.0 | 1.17 | 1.51× | 2% | 0 |
| safeZoneFrac 0.95 | 82% | 79% | 4.4s | 3.8 | 1.17 | 1.51× | 2% | 0 |
| pressDwellTicks 5 | 57% | 51% | 3.0s | 6.0 | 1.17 | 1.51× | 1% | 0 |
| pressDwellTicks 8 | 59% | 53% | 3.0s | 5.7 | 1.17 | 1.51× | 1% | 0 |
| 0.92 / 5 | 82% | 78% | 4.7s | 3.8 | 1.17 | 1.51× | 2% | 0 |
| 0.95 / 8 | 83% | 79% | 6.3s | 3.6 | 1.17 | **1.36×** | 2% | 0 |

`safeZoneFrac` 0.88 → 0.92 alone restores rest to 81% and the median calm
spell to 4.4s — past the T026 baseline (78%, 4.8s) on rest, level on calm
— with size unchanged at 1.51×, zero empty frames, and shot members
drawn outside the frame rising only 1% → 2% of frames. **More patience
barely helps** (pressDwell 8 buys 5 points) and that is the diagnosis:
with five cats inside one frame the safe zone is under near-continuous
pressure, so the press is persistent rather than transient. A wider
deadzone answers a persistent press; a longer dwell does not. 0.95/8
buys another 1.6s of calm but costs size (1.51× → 1.36×).

Replay numbers only — the feel is the owner's call live, per T026. No
dial moved.
