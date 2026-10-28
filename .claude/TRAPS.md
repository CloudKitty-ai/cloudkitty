# Harness traps and lessons

What Harness's code (`.claude/` hooks and skills, `scripts/`, Harness's
workflow files) does that bites, and the method changes it taught (THREADS.md
§6). Entry: date, the trap in a sentence, where it bites, the evidence, the
guard if any. A trap a guard now catches is deleted; the guard is its home.

## Traps

- **2026-09-22** — checkout-guard reads a Bash command's text, not its effect:
  a checkout it would refuse trips it even inside quotes, a heredoc or a
  python replacement string (re-checked 2026-10-28: an `echo` that only quoted
  one was refused in the native checkout). *Bites:* writing or editing a file
  whose content names such a command. *Guard:* none; use the Edit or Write
  tool, or build the literal by concatenation.
- **2026-10-16** — mutating `scripts/mutate.sh` while it runs is undefined:
  bash reads a script as it executes. *Bites:* any rule-5 red on mutate.sh.
  *Evidence:* #453. *Guard:* none; run the cycle from a scratch copy of the
  runner.
- **2026-10-16** — `git check-ignore` matches a directory-only pattern
  (`dir/`) only once the directory exists, and exits 1 before that. *Bites:*
  a rule-5 red on a `.gitignore` line. *Evidence:* #457. *Guard:* none; create
  the directory before the cycle.
- **2026-10-16** — a `## Frozen` line in `.claude/CONDENSE-LOG.md` needs the
  freezing commit's SHA as it exists on main, and a squash merge replaces the
  branch's SHAs. *Bites:* freezing a tracker. *Evidence:* #454/#455. *Guard:*
  the frozen check refuses such a SHA, but its message ("frozen file … changed
  since <sha>") blames the file, not the missing SHA, so the entry stays. Land
  the freeze as two PRs: the content, then the log line naming the squash SHA.
- **2026-10-27** — `scripts/mutate.sh` prints only the first 12 lines of the
  mutated run that match its failure patterns. *Bites:* any prediction that
  spans several cases. *Evidence:* the #474 and #475 ledgers. *Guard:* none;
  re-run the mutated suite from a scratch copy of the scripts and read every
  FAIL line.
- **2026-10-27** — `scripts/tag-check.sh` exits 0 on a REPORT; 3 is only a
  check function's internal return. *Bites:* `--expect` predictions on
  test-tag-check's exit lines. *Evidence:* #475, M16 came back rc 7.
  *Guard:* none; predict the script's exit code.

## Lessons

- **2026-10-27** — CI-only behaviour (continue-on-error, annotations, step
  timeouts) gets its rule-5 red on a throwaway probe PR, closed unmerged:
  mutate.sh cannot exercise the runner. *Evidence:* #472/#473, #476/#477.
- **2026-10-28** — anchor an output guard to something only the target line
  carries, never a bare phrase: `hasnt "read ci.yml run"` also matched "could
  not read ci.yml run N". *Evidence:* #475, M18.
- **2026-10-28** — a stub must emulate every flag that changes the result
  (`--json` fields, `--limit`, `--paginate`); a flag it ignores lets that
  flag's mutants survive. *Evidence:* #475, review round 1.
- **2026-10-28** — before predicting a mutant's failure count, re-read every
  assertion on the mutated property, header lines and ids that pin a selected
  item included. *Evidence:* #475, four under-counts across three rounds.
- **2026-10-28** — a fixture is a recorded real payload; when this repo has
  none of the kind, record one from a public repo and name it (a cli/cli
  startup failure, an actions/checkout clean run). *Evidence:* #475.
