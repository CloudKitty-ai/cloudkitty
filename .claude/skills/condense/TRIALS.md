# Trial record

Every run of /condense lands a section here: fixture reds and real
passes, clean or not. Edits to SKILL.md check themselves against
this file — the skill is shaped by what actually failed, not what
plausibly could.

This file is append-shared (THREADS.md §1): the thread that runs a
pass appends its own section and never touches another thread's.
Product and Client append through a worktree and a PR; Experiments
appends on main directly; Harness through a worktree and a PR.

Lifetime: shakeout evidence, then frozen (owner ruled 2026-09-25;
the close-out procedure is in SKILL.md §TRIALS lifetime beside this
file). Shakeout closes on the owner's word, backstop 2026-10-15.

## Fixture red — Harness thread, Fable, 2026-09-24

The rule-5 red for the skill's first commit. mutate.sh does not fit
(the assertion under test is a subagent procedure; the mutation is
the fixture's three plants) — hand-rolled with the prediction
written in the session before the run.

**Predicted**: exactly three losses — the owner's density caveat of
2026-09-20 (category 1); the dropped mechanism reasoning (six-tick
minimum, need 7–9, zero-tick walk, F-047; category 2); the
frozen-mind cost range 1.4–5.2 silently printed as 1.4–4.2
(category 4). Nothing else flagged.

**Got**: 3 LOSSES, exactly the three plants, each with the old
sentence quoted verbatim and the category named. No false positive:
the merged comparator sentence, the tightened conducted prose, and
the scope relocation were all correctly cleared as rewording.
Two catches worth keeping: the checker flagged the changed number as
WRONG, not merely missing (it looked the real 5.2 up in RESULTS.md
§Tier 5), and it checked recoverability by actually following the
new text's pointers — it found the nap mechanism DOES exist in
RESULTS.md's 2026-09-20 addendum but ruled it unrecoverable because
the condensed text's pointers do not lead there. That is the
recoverability standard exactly as SKILL.md states it.

**Verdict**: red confirmed; no checker bug. First real pass is
whichever file next owes one under the gate.

## Fixture red, round 2 — Harness thread, Fable, 2026-09-24

Re-run owed by the skill's own rule after the review round changed
the checker handoff (document bodies with headers stripped, native
checkout named). Predicted the same three losses, nothing else; got
exactly the three, and the round-2 checker additionally traced that
F-051's re-verify clause points BACK to F-050 as the caveat's home —
the §6 home logic applied unprompted. The review round's other
outcomes: two blockers fixed in SKILL.md (merge-commit-only landing;
the global base documented with the pre-pass `--report` guard),
her ruling-2 sentence now quoted verbatim, T2 advisory self-serve
confirmed by her word, THREADS.md §1 refreshed in the same PR.
