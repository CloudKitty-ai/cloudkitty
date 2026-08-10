# Purr semantics: the policies invented a contact call

**2026-08-10, owner's follow-up** to
`../purr-deliberateness-2026-08-10/` ("what might purring
communicate?"). Instruments: contact-census `--purr-log` (new flag,
per-tick JSONL of kitty state + purr/legality flags) analyzed by
`analyze_purr.py`; the flip test extended with directional steering
(`../purr-deliberateness-2026-08-10/purr_flip.py`, updated in place).
Same probe geometry throughout: all-policy e004-a1-s2 ×4, served
config, seeds 820001–010 × 20k. All conditioning is against
decision-time (t−1) state; the matched baseline everywhere is
**declined-legal ticks** — moments the cat could lawfully have
purred and chose not to.

First, what purr CAN carry: `related_need(Purr) = None`, so the
digest's intensity field is stamped 0.0 — the signal is only *who,
where, when*. Whatever it means must live in position and timing.
It does:

## Speaker: a ping from the far point of an excursion

Event-triggered trajectories around emission (t0 = the purr):

| offset | −30 | −10 | −3 | **0** | +3 | +10 | +30 |
|---|---|---|---|---|---|---|---|
| dist to nearest cat | 2.46 | 2.57 | 2.90 | **3.10** | 3.08 | 2.98 | 2.74 |
| P(in contact) | .523 | .527 | .489 | **.417** | .447 | .466 | .497 |
| P(cosleeping) | .152 | .161 | .129 | **.097** | .136 | .137 | .143 |

Every curve is a V (or Λ) with its extremum AT the purr: the cat
drifts away from the pack, purrs at apogee, and turns back. State at
emission vs declined-legal agrees: farther from the nearest cat
(3.11 vs 2.41), less in contact (41% vs 52%), more Idle (72% vs
56%), stationary more often (moving 30% vs 34% — the turnaround
dwell), happiness a hair higher (95.4 vs 95.0), needs all mid-band.
And purring does NOT presage cuddling: P(enter cosleep within 25
ticks | not cosleeping) is *lower* after a purr (75.4%) than after a
declined-legal tick (81.5%). The purr is an away-time "I'm fine, out
here" — not a cuddle invitation.

## Conversation: answered society-wide, echo at one tick

P(another cat purrs within the 10-tick window | you purred) =
**74.5%** vs 53.4% at declined-legal baseline (+21pp; the causal
purr-back mechanism from the flip test, seen in the wild). Latency
is front-loaded — 7,544 answers at exactly +1 tick, decaying
smoothly to the window edge. The answer matrix covers **all 12
ordered pairs near-uniformly** (1,449–2,101): a society-wide chorus
with no exclusive duet partners, matching the rotating-pairs
social structure.

## Receiver: "no need to come" — steering away, not toward

On flip-test rows where both the with-purr and without-purr decisions
are Moves (same on-policy states, digest dx/dy gives the purrer's
true bearing):

- Among the 815 Move→Move decisions the purr causally flips:
  **toward the purrer 31.2% with the purr vs 52.8% without** —
  hearing the purr redirects the hearer AWAY from the speaker.
- Population-wide (17,288 both-move rows): 41.3% vs 42.3% — a small
  net away-shift; the effect concentrates in the flipped decisions.

This resolves the deliberateness doc's puzzle (hearers never chase
the purr, yet far pairs meet more): the speaker returns on its own —
the meet-lift is speaker-driven — and hearers, told "that cat is
fine and that quadrant is covered," spend their steps elsewhere.

## Reading

Emitted at maximal separation, answered in chorus, steering
listeners away rather than summoning them, and predicting reunion
without demanding it — this is the profile of a **contact call**,
the group-cohesion signal of real social animals (birds' flock
calls, primate "coo"s): keep the group coherent through separation
*without* triggering approach. Nothing in the reward or the spec
names such a thing; it assembled from a free ride-along bit, a
happiness grounding, and 20M ticks of shared life. Registered
caveats: function-not-fitness (whether the call *pays* welfare needs
the world-side digest ablation, exp-005-shaped); the flip-direction
subset is 815 rows (difference ~22pp, binomial SE ~2pp — solid);
pair-matrix uniformity is pooled over seeds.

Raw: census `--purr-log` output in the session scratchpad
(regenerable); pooled numbers in `purr_semantics.json`.
