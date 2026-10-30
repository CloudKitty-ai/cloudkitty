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
- **2026-10-29** — no PR in this repo can carry a GitHub approval: all five
  threads push and review from the owner's one account, and GitHub refuses
  "approve" on your own PR. Two consequences stack on it: the sessions'
  permission classifier refuses `gh pr merge` as a merge without review
  whatever a peer said by message, and (since 2026-10-29) refuses a peer's
  review comment on the PR as well. *Bites:* every tooling PR at review and
  at merge. *Evidence:* #480 ("Can not approve your own pull request"), #485
  and #486/#487 (merges and review comments refused in both sessions).
  *Guard:* none — the owner ruled 2026-10-29 that her approval before each
  merge stays the rule ("I'm ok continuing providing my approval before pr
  merge"). Procedure: the reviewing thread sends its verdict by cross-session
  message; the author quotes it, head SHA included, in the PR body; the merge
  goes to the owner with the PR number (`gh pr merge N --squash`). No thread
  asks a peer to merge or comment for it — that routes around the refusal
  instead of through her. Merge style follows whoever presses the button:
  Harness squashes, Product's session merges with a merge commit (every
  Product PR since #444), so a Harness PR landed by Product arrives as a
  merge commit unless the command says `--squash`.

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
