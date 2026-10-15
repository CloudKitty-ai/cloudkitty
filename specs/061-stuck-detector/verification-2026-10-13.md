# Clarify-gate verification: option B false-positive read (2026-10-13)

The owner accepted confinement (option B: the cat never leaves
Manhattan radius 1 of the window-anchor tile) conditionally: "B, first
verify if there would have been any false positives under this rule."
This record is that verification. Instrument: `stuck_rule_replay.py`
beside this file (run from the repo root; stdlib + numpy only; reads
recorded raws, writes nothing but a fire dump to its own directory).

## Data

Two arms of recorded healthy behavior, both read as-is from the
native checkout's raws:

- **A (scripted)**: `experiments/fog-gen1-shakeout/results-raw/
  anchor-resmoke-050-20k/config-00-rollout-{00,01,02}/trace.jsonl` —
  3 × 20,000 ticks × 5 cats = 300,000 cat-ticks of the scripted
  teacher roster, full per-tick snapshots (exact positions, needs,
  activity state).
- **B (policy)**: `experiments/fog-gen1-cert/results-raw/live/
  lab-dispersion-gen1A-trace.npz` — the certified gen1-A roster
  (the five live `.ckpolicy` files) replayed in the lab under the
  trained clock on anchor-b3: 5 seeds × 5,000 ticks × 5 seats =
  125,000 cat-ticks. Positions/needs/activity decoded from the v5
  self block (pos at cols 7–8 × 20, needs at 0–5 × 100, activity
  one-hot at 9–15 with slot 0 = Idle per `observe.rs push_activity`;
  block row-sum verified 1.0 and the idle share, 0.57, matches the
  live served poll's 0.57).

The rig was proven able to fire before any zero was trusted: a
synthetic F-044 two-tile pacer (alternating adjacent tiles, eat 95,
idle) fires at every swept setting (`--selftest` runs always).

## Rule as replayed (the spec's FR-001/FR-002 form)

Fire when, per seat: confined to Manhattan radius 1 of the anchor for
N consecutive ticks (leaving resets the anchor), AND some one need
has accumulated N armed scene-free ticks (need ≥ armed line, no
activity scene). Scene ticks PAUSE a need's streak; a scene tick on
which that need's value fell (the scene is relieving it) CLEARS the
streak. Full reset after a fire. Sweep: N ∈ {20, 30, 50}, armed line
∈ {75, 90}.

## Result: no false positives

| Setting | A scripted (300k ct) | B policy (125k ct) |
|---|---|---|
| N=20, armed≥75 | 2 fires | 4 fires |
| N=20, armed≥90 | 0 | 2 |
| N=30, armed≥75 | 0 | 3 |
| N=30, armed≥90 | 0 | 2 |
| N=50, armed≥75 | 0 | 1 |
| N=50, armed≥90 | 0 | 0 |

- **Every policy-arm fire is one true positive**: a single real
  episode — Biscuit, seed 870005, ~135 consecutive ticks pinned to
  the (18–19, 0) map corner, dithering MoveE/MoveW with eat climbing
  69 → 100, exactly the GEN2-INPUTS "corner signature" this detector
  was ruled to catch. The multiple fires are the stand-down rule
  re-firing while the episode persisted. Zero false positives on the
  deployment-relevant arm at every setting.
- **The two scripted-arm fires** (loosest setting only) are the same
  cat and shape twice: Clementine pacing in place with cuddle ~90–96
  waiting on a partner, who arrived within ~4 ticks of the would-be
  fire. Borderline rather than false — the need was armed, confined,
  unrelieved for 40+ ticks — and scripted seats are exempt from the
  detector regardless (FR-003). On a mind in that shape the option-B
  substitute (one scripted tick) is what a waiting teacher would do
  anyway.

## The refinement the replay forced

First pass used the drafted strict gate (no activity scene at ANY
tick of the window, any scene resets). Under it the real Biscuit
episode produced fires at N=20 only and **vanished at N ≥ 30**: the
loop carries one-to-two-tick play/sleep flickers that reset the
window each time. The pause-don't-reset gate above (clear only on a
scene relieving the tracked need) was re-swept: the real episode then
fires at every N (4/3/1 fires at N = 20/30/50, armed 75) and the
healthy arms are unchanged (no new fires anywhere). FR-002 pins the
pause form and names the strict form wrong by measurement.

## Caveats

- Arm B is five seeds × 5k ticks of one roster on one config; the
  SC-002 paired soak at implementation time is the declared read,
  this is the clarify-gate screen.
- Scene relief in arm B is inferred from the need falling during a
  scene tick (the obs carries no scene-target field); the engine
  implementation reads the scene directly and needs no inference.
  (Superseded for the shipped rule — see the 2026-10-15 re-run below.)
- The live served poll (`poll-20260916T200220.jsonl`) polls every
  ~25 ticks and cannot support a per-tick window read; it was used
  only to anchor the idle-share sanity check.

## Re-run 2026-10-15: the implementation relief rule (analysis F7)

The clarify-gate run cleared a streak when the need's VALUE FELL
in-scene. The implementation reads the engine's own mapping instead:
a streak clears only when the seat's own scene governs that need
(`Activity::governing_need`), restricted to the seat's own relief —
grooming WITH a target relieves the friend's bath, not the groomer's,
and solo rest governs nothing. The two rules diverge in principle
(co-sleep relieves cuddle by value but governs sleep; groom-other
lowers nobody's own bath; friendless rest governs nothing), so the
zero-false-positive result was re-verified rather than assumed to
carry over.

Re-run with `--relief governing` (now the default; `--relief
value-fell` preserves the original rule and still reproduces the
table above exactly): arm A maps the trace's serialized activity
(state + optional target/with_friend); arm B's one-hot carries no
target or partner, so resting and grooming there are read
PESSIMISTICALLY as clearing nothing — streaks survive longer, so a
zero under this reading is a zero under every reading.

**Result: the table is IDENTICAL to the clarify-gate table** — same
fire counts, same seats, at every one of the six swept settings, on
both arms (425k cat-ticks). The divergent cases exist in the
recordings but never change a fire. The committed
`stuck-rule-fires.json` (14 rows) is regenerated under the governing
rule and matches the implementation gate.

One residual the recordings cannot exercise: a cat being groomed BY
another is itself scene-free while its bath falls; its streak clears
only on the below-line crossing. A fire during slow externally-given
relief is theoretically possible and harmless (one scripted tick),
and no such shape appears in either arm.
