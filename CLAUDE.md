Five sessions share this repo. Who you are and what you own:
THREADS.md — read it at kickoff, before anything below.

1. Surface assumptions, confusion, and tradeoffs. State reversible
   assumptions and proceed; ask before irreversible decisions
   (migrations, deletions, public interfaces).
2. Simplest correct solution, smallest footprint. Before writing new code,
   reach in order for: an existing helper in this codebase → the standard
   library → an already-installed dependency → only then new code. Nothing
   speculative — tests for your own changes aren't speculative.
3. Touch only what you must; clean up your own mess. Report other
   problems; don't fix them.
4. Fix success criteria before coding, then loop until verified. Never
   weaken tests or criteria to pass. If stuck after ~3 real attempts,
   stop and say exactly where.
5. Green proves nothing until you have seen it red. Every assertion
   you add, change, or cite as evidence: introduce the exact bug it
   should catch, at the cheapest layer that exercises it, predicting
   the failure first. Green, the wrong assertion, or the wrong reason
   means unverified. The cycle is `scripts/mutate.sh --expect
   <prediction>`; hand-rolling it needs a stated reason. Three lies
   survive it: asserting on wording (assert on state, unless the
   wording is the contract), hand-written fixtures (record real
   payloads), the wrong layer (check where the bug occurs).
6. Changed behaviour: sort its checks before running. Guards of the
   change must go red; kept behaviour must stay green. A must-fail
   that stays green is vacuous: fix it if you made it so, report it
   (rule 3) if not. Read the must-pass pile, don't only run it. The
   failed guards, pointed at the new behaviour, are rule 5's red.
7. Before designing experiments or training runs, read
   experiments/FINDINGS.md.
8. A spec that prices, observes, or scripts behavior is checked against
   experiments/DESIGN-DOCTRINE.md before /speckit-plan. The spec names
   each rule that moved a choice and the choice it moved; a check that
   moved nothing says so.
9. Delegate by task shape. A subagent takes work whose output must be
   independent of your context or would flood it: verifying an
   artifact's claims, sweeping files or raws, applying a written rule
   set mechanically. The session keeps what decides or applies:
   rulings and their records, write-ups, guard design, the rule-5
   prediction. A subagent's report is evidence you read, never a
   result you paste. The resume anchor lists what was delegated.
