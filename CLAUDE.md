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
5. Before designing experiments or training runs, read experiments/FINDINGS.md
6. Never trust a passing check — test, CI gate, or eval — until you've
   watched it fail. Introduce the exact bug the check should catch
   (revert the fix, flip the logic), predict which assertion fails and
   why, then run. Green, a different failure point, or a different
   reason all mean the check is unverified. Undo the break; confirm
   green. Three failure modes pass this procedure anyway: string
   assertions match wording, not behavior — assert on state and
   outcomes; hand-written fixtures can be wrong together with the code —
   build them from recorded real payloads; a test only catches bugs in
   the layer it exercises — put the check where the bug would occur
   (core unit tests can't catch server-contract bugs).
