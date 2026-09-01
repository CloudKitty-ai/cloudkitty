# Step-2 addition: the water's-edge avoidance smoke (design)
## (2026-08-31, Experiments + owner; arms declared here, bars pinned at prereg)

Owner's framing, on the record: we are changing a lot this generation,
and the more we can understand the individual changes, the better
chance we have of a successful fog experiment. This smoke isolates ONE
change — the contagion charge's behavioral pull on position choice —
from fog, the digest, and the schema break, and it produces the data
for the owner's bidirectional-membership call BEFORE Gen 1's corpus is
collected (fog timeline step 4 decision point).

## Why this design (and not the live check)

Two facts pin the shape:

1. The frozen roster cannot learn avoidance (chooser charge-blind,
   charge unobserved, no incumbent trained under it), so the post-flip
   live check is a sanity pass, not evidence.
2. Gen 1 is BC from scripted anchors: clones imitate the TEACHER. If
   the scripted ladder never weighs the charge, no clone learns
   avoidance under either membership rule — the question "does the
   charge produce edge avoidance?" is a question about a CHARGE-AWARE
   chooser. This smoke rules the ladder charge-aware for the lab arms
   only; nothing here commits the served anchors (that stays the
   banked anchor-probe question, owner's call separately).

## Arms (scripted needs-driven lab worlds, paired seeds across arms)

| arm | ladder | factor | membership | role |
|---|---|---|---|---|
| A | charge-blind | 0.0 | — | baseline |
| B | charge-blind | 1.0 | option_a | negative control: isolates need-level drift with NO avoidance possible |
| C | charge-aware | 1.0 | option_a | the shipped rule, felt |
| D | charge-aware | 1.0 | bidirectional | the candidate rule, felt |
| E | charge-aware | cranked (≥10x, above the ceiling's bite) | bidirectional | positive control: avoidance MUST appear here, or the instrument cannot emit the signal and arms C/D are void (F-029's rule) |

## Readouts

Water's-edge behavior: water-adjacent share of cat-ticks, on-water
share, cross-waterline adjacency share of adjacent pair-ticks —
`attn-cert-2026-08-14/waterline_exposure.py`'s measures, pointed at a
headless lab server (tick_ms 1, the 041-investigation repro pattern;
the instrument needs a --base flag, a small Experiments tweak).
Context readouts: scene mix vs the step-2 bands (groom modes
especially), happiness/bath levels vs the needflow predictions
(coin-flip table superseded; Option A + bidirectional tables in
`cuddle-economy-model/RESULTS.md`).

## Decision rule (bars pinned at prereg, shape declared now)

- E must show the avoidance signature (water-adjacent share and/or
  cross-waterline adjacency down, clearly and directionally). If E is
  flat, the smoke is VOID — no conclusion about C/D, and the
  bidirectional call falls back to design preference with that
  disclosed.
- Given E fires: if D ≈ C ≈ B on the edge metrics (bar pinned at
  prereg; paired seeds make a tight bar honest), bidirectional is
  behaviorally safe at factor 1.0 and the owner may flip membership
  pre-fog so Gen 1's corpus is collected under the final rule.
- If D separates from C, the owner rules with the size and shape of
  the separation visible — that is the smoke doing its job, not a
  failure.

## Dependencies (block collection, not this design)

1. **044 merged** (inert; arms set the dial in lab configs only).
2. **A `contagion_membership` config dial** (option_a | bidirectional,
   default option_a) — engine charge-filter branch, lab-use;
   Product's lane, small. NOT YET REQUESTED — handoff awaits the
   owner's word.
3. **A charge-aware ladder option** for the scripted chooser (weigh
   expected contagion exposure in scene value), config-gated,
   default off — Product's lane; the larger of the two. NOT YET
   REQUESTED — same word. Its design should reuse the needflow value
   shape (charge x expected scene-ticks against the payer's bath).
4. Instrument --base flag (Experiments, trivial).

## Sequencing

After 044 merges and the two dials exist; before the step-4 fog spec
window closes, so the membership ruling lands before step-5
collection. Fog-side re-check stays as declared in the timeline: the
step-5 shakeout watches edge behavior under fog regardless of which
rule ships (fog changes what a cat can see near water; the pre/post
schema-break comparison is itself informative — the owner's point).

## Live reference (banked 2026-08-31)

Fresh pre-flip exposure baseline on the served 041+bump world
(`waterline_exposure.py`, ticks 1,110,103–1,110,851): on-water share
3.02% of cat-ticks; cross-waterline adjacency 6.20% of adjacent
pair-ticks (87/1403); per-kind scene shares groom 4.5% / cosleep
9.3% / duet 3.4% — between the two 08-24 windows (low groom 9.0%,
high 25.0% predate the 041 mix shift; carry all three rather than
averaging). Raw: `attn-cert-2026-08-14/results-raw/`
`waterline-exposure-1110103.json` (uncommitted). This is the live
"before" for the post-flip sanity check AND the exposure input the
lab arms should roughly reproduce before their contrasts mean much.
