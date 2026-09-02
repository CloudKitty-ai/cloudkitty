# Behavioural-collapse detector v0 — preregistration
## (2026-09-01, Experiments; fog timeline step 2: "`tail-benchmarks/family-11-r5` against the collapse-detector v0"; ROADMAP parking-lot design; bars pinned HERE, before the detector ran on any trace)

## What it is

An offline detector over recorded per-tick world state that names a
dyadic lock (F-027's twin co-sleep deadlock) by its ACTION SHAPE, not
by distress. Detect-and-report only. v0 reads the exp-006 forensics
traces (`exp-006-character-gen/traces/*.npz`, `states` array =
`global_state.rs` layout, 32 floats per kitty); every signal is
derived from fields a served instrument could read off `/world` each
tick (activity, partner, needs), so a live v1 is a transport change,
not a redesign. The `chosen` action-head array is used only as a
cross-check for policy seats.

## Signals (pinned)

Window `W = 200` ticks, trailing. A signal FIRES when its condition
holds at every tick of a run of at least `D = 200` consecutive ticks.
A lock of length L puts the trailing share over 0.5 for L−1 ticks, so
the shortest lock that fires is 201 ticks and the fire lands ~300
ticks after onset — about when the spec-040 watchdog (150 ticks of
distress, which itself starts after the lock) would fire on a
starving lock, and well before it on a lock that services enough
needs to stay welfare-quiet. Both W and D were chosen from F-027's
numbers before any healthy margin was read: the deadlock ran 2,331
ticks; healthy partnered spans are 2–7 ticks (F-031, needflow lab),
so a 200-tick window at >50% one partnered family needs the same nap
re-entered ~17 times back to back.

- **(a) partnered-activity concentration**, per seat. Family = realized
  activity ∈ {resting, sleeping, grooming} with the partner-present
  flag set (state offsets 9–15 one-hot, 17 flag). Condition: the
  share of one family in the trailing window > 0.50.
- **(b) mutual-pair persistence**, per unordered pair. Mutual at tick
  t iff each names the other as partner (offset 18 × (roster−1),
  rounded). Condition: mutual share in the trailing window > 0.50.
  Duets are reciprocal by construction, so this is about duration.
- **(c) need spread**, per seat, REPORT ONLY in v0: trailing mean of
  (max need − min need) > 60 on the 0–100 scale. Catches the lock's
  starvation face and Mechanism 2's corner pacing (e004 MLP), but it
  is welfare-adjacent and could discriminate against character, so it
  is not a firing signal.

Verdict per trace: FIRE iff (a) or (b) fires on any seat/pair. Output:
first-fire tick, signal, seat/pair, episode length; plus the watchdog
equivalent (first distress streak reaching 150 ticks, from offsets
20–25) so "fires earlier" is a measured number.

## Trace labels (from `results/r5-forensics-2026-08-20.md`, fixed before running)

MUST FIRE (twin/triadic locks):
- candidate-r5 880030 (twins, 2,331 ticks, from ~4,300)
- reference-r5 880008 (twins, ~500 ticks)
- candidate-r5 880015 (triadic pile, ~475 ticks)

SHOULD FIRE (report; heterogeneous pile at the bar's edge):
- solo-s3-e0 880017 (435-tick pile, ticks 365–800)

MUST STAY SILENT:
- candidate-r5 880001 (mda 0, same twins, same world — the seed lottery)
- solo-s3 880013 (mda 159 = DIRECTED TRAVEL, not a lock — the
  discriminating negative)
- reference 870005 (mda 87), candidate-clone 870001, val-scripted
  870001, solo-s3-e1s1 ×3, solo-s3-e1s1-swap ×3, solo-s3-e1s2 ×3 (all
  mda 0)

REPORT ONLY: candidate 880013 (mda 137: brief twin events on 20×20,
interrupted early — either outcome is informative).

## Margin (report)

For each signal, the maximum trailing share seen on any MUST-SILENT
trace, and the minimum over the MUST-FIRE traces' lock windows. A
margin under 0.10 on either side says v0's threshold is on a knife
edge and H4's pin at step-5 kickoff should not inherit it unexamined.

## Guard

`test_collapse_detector.py`: synthetic state arrays (a 500-tick mutual
partnered sleep starting at tick 100 fires (a) and (b) at tick 399
with a 499-tick episode; 6-on/6-off naps sit exactly AT 0.5 and stay
silent under the strict bar; a 150-tick lock stays silent under D;
one-sided partnering fires (a) but not (b); the mutual pin uses pair
(1, 2) because index 0 encodes as 0.0 under any decode). Each pin shown red
in-run before commit (sustain requirement dropped; strict `>` relaxed
to `>=`; window off by one; partner index decode).

## Verdicts

- v0 VALIDATED iff all three MUST-FIRE fire, all eleven MUST-SILENT
  stay silent. Then H4's step-5 pin has a validated instrument and the
  parking-lot item closes.
- Any MUST-SILENT fire is a false-positive class named by seat/tick;
  any MUST-FIRE miss names the lock v0 cannot see. Either is reported,
  not tuned away post hoc — a threshold change is a v0.1 with its own
  prereg line.

## v0.1: H4 bar lifted to 0.65 (owner ruled 2026-09-01; declared before re-running)

Owner's reasoning: one recorded lock class is not enough data for a firm
bar, and a healthy Biscuit could plausibly hold one partnered activity
at half a 200-tick window. Signal (a)'s bar moves 0.50 → 0.65; signal
(b) (mutual pair) stays at 0.50 (margin 0.24 there, not ruled on); W, D
and (c) unchanged. Reevaluate if a later collapse class would be caught
by a lower bar.

Predictions on the same 19 traces: all three MUST-FIRE still fire on
(a) (their lock shares 0.82–0.83 clear 0.65), first fire later by
about 0.15·W = 30 ticks on a hard lock (the synthetic 500-tick lock
moves 399 → 429, episode 499 → 439) and by more where the lock ramps;
`first_fire_tick` stays (b)'s where (b) also fires; all eleven MUST-SILENT stay
silent (healthy peak 0.43); healthy-side margin becomes 0.22, lock-side
0.17. Guard: a one-sided 0.60-share partnering that fired under 0.50
stays silent under 0.65 (shown red by restoring 0.50 before commit);
the at-the-bar pin moves to exactly 0.65 one-sided.

## What this is not

Not a live instrument (transport is v1). Not silence "across the 2.4M
cutover-config ticks" the ROADMAP names — those runs were not traced;
the ten cutover-config traces here (200k ticks) stand in, and the gap
is recorded. Not a welfare gate: the spec-040 watchdog stays the
alarm; this names a cause.
