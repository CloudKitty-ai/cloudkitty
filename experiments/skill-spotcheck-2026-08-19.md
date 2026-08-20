# Skill spot-check: experiment-design (2026-08-19)

Two-round blind A/B test of the `.claude/skills/experiment-design`
skill, run while exp-006 wave 1 trained. Outcome: the skill was retired
at `fc9c73c` and the rules that measurably helped moved to
[README.md](README.md) (Design discipline, Ownership). This page keeps
the method and the numbers for the next time a skill has to prove it
earns its maintenance.

## Question

Does the skill produce better experiment designs from a fresh session
than baseline context alone (CLAUDE.md, FINDINGS.md, full read-only
repo access)? Bar: any measurable value, not optimality.

## Method (the reusable part)

1. **Freeze the rubric before any generation.** 14 items plus 2 gap
   detectors, each anchored to an incident this project actually paid
   for. Never derive the rubric from the skill's own checklist; that
   is circular and the skill wins by construction. Scoring 0/0.5/1
   per item, with an evidence quote required for any nonzero score.
2. **Two briefs at different formality**: a formal in-domain design
   ask with no existing prereg to copy from, and an informal
   owner-style ask ("can we just bump groom_relief..."), because a
   skill claims to catch informal experiment work too.
3. **Generators are fresh subagents** with no session memory,
   identical prompts and repo access; the skill arm gets the skill
   text inline. Both arms are barred from reading `.claude/`. Round
   1's controls found and read the skill unprompted, which voided
   them and forced a re-run; budget for that deviation up front.
4. **Every design ends with a self-reported "Sources consulted"
   list.** That audit trail carried the entire mechanism finding.
5. **Contamination check, then blind judging.** Grep controls for
   skill-distinctive phrasing, strip the audit sections, anonymize to
   X/Y with labels balanced and flipped between rounds. Two judges
   per brief, reading order swapped, item scores plus a forced
   choice. Judges get read-only repo access to verify factual claims,
   minus `.claude/`.
6. **Round 2 after edits regenerates BOTH arms.** Same-brief control
   totals across rounds calibrate generation noise (about ±1 rubric
   point here); an improvement that matters must clear that band and
   map onto specific edits.

## Results

Round 1, skill v1 (totals out of 14, judge 1 / judge 2):

| brief | control | skill | forced choices |
|---|---|---|---|
| formal | 14.0 / 14.0 | 11.0 / 11.0 | 2–0 control |
| informal | 11.0 / 10.5 | 10.5 / 11.5 | 2–0 control |

Mechanism, read off the sources lists: the skill arm never read the
object of its load-bearing claims. On the formal brief it made a false
claim about the trainer's entropy anneal without opening the trainer;
on the informal brief it read checked-in config as the live deploy
state and never opened the census register. It also named process
instead of instantiating it ("QA per house practice" against the
control's counted rider). Meanwhile the controls reproduced the whole
house process grammar (D-numbered deviations, owner forks, seed-band
claims) from the repo's artifacts alone, so the restated process in
the skill was pure redundancy.

Rewrite (v2, `e3dd534`): added Ground truth, Named-steps-are-not-plans,
and a reading-priority rule; cut restated lifecycle, statistics, and
register hygiene to pointers.

Round 2, skill v2:

| brief | control | skill v2 | forced choices |
|---|---|---|---|
| formal | 13.0 / 12.5 | 13.5 / 13.5 | 1–1 |
| informal | 12.0 / 11.0 | 10.5 / 8.5 | 2–0 control |

The formal failures inverted into strengths that map line-for-line to
the v2 additions (trainer and runner read and verified, smoke seen red
on a mis-phased log, counted exposure audit). The informal failure
recurred in softened form: the arm declared its box state "a
hypothesis read off the register and the config history, not off the
box" but still never opened `policies/purrsonality.md`. The rule had
named a concept ("the purrsonality register") instead of a file.

## Resolution and lessons

Owner's ruling: relocate and delete. The kernel lives in
[README.md](README.md); the skill file is deleted at `fc9c73c`, with
v1 and v2 reachable in history at `e3dd534` and its parent.

1. Restating process the artifacts already demonstrate is dead
   weight, and under a bounded reading budget it crowds out the
   object-level verification that decides design quality.
2. Rules must name artifacts, not concepts: `policies/purrsonality.md`,
   never "the register." A named source is not a plan any more than a
   named step is.
3. Judges err too. One flagged a true claim (an "810-run history") as
   embellishment; the repo said otherwise. Check disputed claims
   yourself before adopting a judge's word.
4. On both rounds of the formal brief, each arm held a piece the
   other needed. For design work, two generations plus a merge beat
   either arm alone.

Caveats: one generation per cell per round, so the totals alone prove
little; the actionable part was the mechanism mapping between edits
and item-level changes. The test measures the fresh-session floor
only. Full protocol, all ten designs, and eight judge reports lived in
session scratchpad and are summarized here; this page is the durable
record.
