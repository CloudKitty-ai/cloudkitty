# Contract: the consent gate (spec 047)

The externally observable contract for `[behavior] consent_line`. Consumers:
Experiments' acceptance run (prereg
`experiments/biscuit3-comfort-sweep-2026-09-01/prereg.md` §Addendum 2, bars
C1–C5 and readout R7), future character configs.

## The dial

```toml
[behavior]
# Spec 047: a friend whose top non-play need is over this line (and over
# its own play need) is never proposed to for play by a playful cat.
# 0.0 (the default) = off, byte-identical to pre-047.
consent_line = 30.0
```

- Default 0.0 = OFF. At the default the engine is byte-identical to a
  pre-047 build: evolution golden pin and defaults stamp both unmoved.
- Validation: must be finite, ≥ 0 and ≤ 100 (needs cap at 100, so a higher
  line could never block — it is refused rather than loaded inert; 100
  itself is legal but blocks nothing); violations fail config load with an
  error naming `[behavior] consent_line`.

## The rule (owner's, pinned in the prereg)

With `consent_line` L > 0, a candidate FRIEND k is **blocked** iff

```text
top_non_play(k) > L  AND  top_non_play(k) > play(k)
```

where `top_non_play(k)` = max of k's eat/drink/sleep/cuddle/bath needs at
decision time. Both comparisons STRICT: a friend exactly at the line, or
whose play need ties its top non-play need, stays eligible. Play on top =
always proposable.

## Where it binds (all three playful friend-play paths)

| Site | Path | Effect when blocked |
|---|---|---|
| Partner ranking | playful below comfort → scored selection | friend never becomes a candidate: score, approach, wait, and solo-suppression all behave as if the friend were absent |
| Get-serious relief | playful at/above comfort → shared need scoring picks play | friend excluded from the playmate scan itself; the play score prices the next candidate or none |
| Adjacent opportunism | playful's take-what-is-here, Playmate rung | blocked friend not batted into a game; a critter in reach is still taken; nothing in reach → the rung yields nothing |

Invariants across sites:

- One predicate, one snapshot: all sites evaluate the same rule against the
  same decision-time world needs (R7's single definition).
- Friends only: critters, element play, and the solo backstop are NEVER
  gated, on any path.
- Playful only: needs_driven (and every other behavior) is untouched even
  with the dial set.
- Hard drop, not a cost: the gate never shifts a score; it removes the
  candidate. Independent of `w_value`/score on-off and every other dial.
- Article IV: the gate moves what the playful advisor proposes, never what
  is legal — engine validation is unchanged.

## Non-changes

No endpoint, no event, no snapshot field, no persistence change. R7 is
computed by Experiments from existing census polls; the engine emits nothing
new.
