# Contract: Cue-Answer Rungs (FR-010, FR-011, FR-012, FR-016)

## Keying

`cuddle_response` keys `MessageKind::WantCuddle` → partnered rest;
`play_response` keys `WantPlay` → friend play. Want kinds ONLY — the
free register (Mew, Chirp, Trill, Ekekek) is never emitted by nor keyed
to the scripted teacher (FR-012; today's `announce`,
behavior/mod.rs:504-537, already emits want/here words only — a guard
pins it stays so).

Calls are read via `meow::freshest_audible` per kind on the
`FogView` digest; a call is audible from the tick AFTER emission and
for `digest_window_ticks` (world.rs:1754-1757; served 30).

## Fire condition (deterministic — clarify Q3)

A call applies its valuation term iff it survives the feasibility
filter AND

```
intensity ≥ max(reply_intensity_floor, top_pressure(me) / 100)
```

— the call must outrank the hearer's own loudest need; the existing
`[behavior] reply_intensity_floor` (served 0.20) is the floor. No RNG.
Graded response is across states: a louder call clears in strictly
more hearer states.

## Contention (FR-016; owner-confirmed Professor recommendation)

Per kind, per decide, over all audible callers:

```
window_remaining = digest_window_ticks − (now − call.tick)
feasible(i)      ⇔ d_i ≤ window_remaining_i − HANDSHAKE_TICKS      // hard filter
score_i          = intensity_i − k · d_i                            // d Manhattan
winner           = argmax score, ties: intensity → nearer → lower id
```

The winner alone sets the term and names the answered partner — calls
never stack. With an incumbent (the hearer is already pursuing an
answer, derivable from its pursuit target), a challenger displaces it
only if `score_challenger > score_incumbent + h`.

## Derived constants (single home: `behavior/teacher.rs`, documented)

| constant | derivation | served value |
|---|---|---|
| `I_min` | `announce_threshold / 100` (armed-emission floor — a quieter want-call cannot exist, meow.rs:279-298) | 0.20 |
| `I_max` | intensity clamp at emission (action.rs:963-966) | 1.0 |
| `HANDSHAKE_TICKS` | 1-tick hearing lag + 1 propose tick | 2 |
| `D_w` | `digest_window_ticks − HANDSHAKE_TICKS` tiles (walk speed is implicitly 1 tile/tick — one `pos.step` per Move) | 28 |
| `k` | `(I_max − I_min) / D_w` | ≈ 0.0286 |
| `h` | `k × response_commitment_ticks` (`[behavior]` key, default 3.0) | ≈ 0.0857 |

The flip signature (prereg-able): the answered choice flips from
louder to nearer across `intensity_diff = k · distance_diff`.

## Placement (valuation-only — FR-010)

The term raises the matching activity's value in the teacher's pursuit
comparison. It is NOT: a consent override (the engine gate runs
unchanged after — contracts/consent-gate.md), an adjacency bypass
(FR-009), a world price (doctrine rule 2), or an engine rule. It
expires with digest visibility; FR-036's cuddle-clause semantics are
inherited by construction.

## Guards owed (rule 5, each via mutate.sh --expect)

Term present within the window / absent one tick past it; the
threshold comparison (hearer's top pressure vs intensity) in both
directions; feasibility drops a louder-but-unreachable caller; the
iso-line flip (scenario 5); the commitment margin holds an incumbent
against an in-margin challenger; no free-register keying (armed
trill/ekekek in the digest moves nothing); consent + adjacency still
block an answered proposal (FR-010 scenario 1-2).

## Staging note (research R13)

`want_cuddle`/`want_play` are illegal while an idle friend is in view,
so scenarios stage emission while the hearer is busy (or out of view),
then exercise the hearer inside the window.
