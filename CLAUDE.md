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
