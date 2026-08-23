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
5. A green check proves nothing until you've seen it red. For any
   assertion you add, modify, or cite as evidence: introduce the exact
   bug it should catch, at the cheapest layer that exercises it. Predict
   the failure first — green, wrong assertion, or wrong reason means
   unverified. Undo; confirm green. Undo means revert, commit first, or ensure there’s a copy to restore from.  Three lies survive this: string
   matches (assert on state, not wording — unless the wording is the
   contract), hand-written fixtures (record real payloads), wrong layer
   (put the check where the bug occurs).
6. Changed behavior: sort its checks before running. Guards of the
   change must go red; kept behavior must stay green. A must-fail that
   stays green is vacuous — fix it if you made it so, report it (rule 3)
   if it already was. Re-read the must-pass pile; running is not
   reading. Point the failed guards at the new behavior — that's rule
   5's red, for free.
7. Before designing experiments or training runs, read
   experiments/FINDINGS.md.
