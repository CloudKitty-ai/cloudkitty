# Handover: starting the CloudKitty Harness thread

Written by Experiments 2026-09-22 on the owner's ask. Harness is the
fifth thread; its charter is THREADS.md §1 (ruled 2026-09-22). This
file is the kickoff reading: what the thread owns, what it inherits
from the four others, what it does first, and the facts nobody wrote
down anywhere it would look. Harness owns this file from its first
session and may delete it once the items below have homes.

## Charter, in one paragraph

Harness owns the Claude Code tooling and reports on everything else.
Tooling: `.claude/` (skills, hooks, agents, settings), `scripts/mutate.sh`,
the memory directory's hygiene, the meta checks in CI in a workflow file
of its own, and drafts of `THREADS.md` and `CLAUDE.md` for the owner's
ruling. Content: code, specs, experiments, docs, client. On content it
produces reports (an accuracy verdict, a cut list) and the owning thread
applies them. It works in a worktree and lands by PR. It never launches
a spec or a pass on a peer's relay; the owner's word in the Harness
session starts each.

## What it inherits

- **The prepare-for-compact skill** (`.claude/skills/prepare-for-compact/`,
  merged #402–#407, last 6e12ec6). Three trials in `TRIALS.md` beside it,
  the shape every future trial record follows: what dropped, what patched
  it, and clean runs count. Still untested there: a live training-shaped
  job card and a step-5 late arrival.
- **The public-voice skill** (user-level, `~/.claude/skills/public-voice/`):
  the sentence-level brevity pass. It stays where it is; Harness edits
  it on the owner's word.
- **Two hooks** in `.claude/hooks/`: `checkout-guard.py` (#356) and
  `revert-guard.py` (#353). The files and the rules they enforce are
  both Harness's (owner ruled 2026-09-26, superseding this handover's
  split); a change to either is a Harness PR with a second-thread
  review, Product by default.
- **`scripts/mutate.sh`**, the rule-5 cycle. Its lessons live in the
  memory file `mutate-cycle-lessons`.
- **The memory directory** (`~/.claude/projects/-Users-elizabethkelly-ai-cloudkitty/memory/`):
  `MEMORY.md` is the index every session loads; four threads edit it per
  line, never whole-file. One trim on record (2026-09-20). No budget, no
  staleness rule, no owner until now.
- **The design conversation** this thread came out of, 2026-09-21/22 in
  the Experiments session. The decisions are below; the reasoning is in
  that transcript and should not need re-litigating.

## Decisions already made (owner, 2026-09-22)

1. **Accuracy gate**: a skill that spawns a fresh-context subagent to
   re-derive an artifact's claims from the recorded raws and the command
   that produced them. Runs last, before the owning thread commits.
   Provenance is mostly mechanical: the tier readers emit JSON, so the
   subagent re-runs the named reader over the named raws and diffs the
   numbers against the doc's tables; a doc without a regeneration
   section fails by construction. The subagent runs in the native
   checkout, because raws are uncommitted and live only there.
2. **Condense pass**: a cut list (delete, move, replace with a pointer;
   never restate a number), prioritised by where a file is read, not how
   long it is. Always-loaded files first (CLAUDE.md, THREADS.md, the
   skills, MEMORY.md); evidence files last or never. The value test for
   a paragraph: which decision breaks if it goes, and which future reader
   would re-derive it.
3. **Enforcement is a budget, not a stamp.** "ARC CLOSED" in an index
   line is a convention and stays one. The guarantee is accumulation
   since the last pass: a condense log with the origin/main SHA of each
   pass, and CI diffing from that SHA on the loaded files, blocking past
   a line budget on the always-loaded files and advisory on FINDINGS,
   RESULTS and the shelf. Event hooks (owner-call issue closed, spec PR
   merged) comment "condense owed" as a supplement.
4. **One home per fact, pointers elsewhere.** The map is the first
   deliverable (below).
5. **Codebase repetition**: jscpd, run once as a survey, then a CI
   ratchet set at the measured value. Test modules thresholded
   separately or excluded. The CI step is Product's to accept; Harness
   proposes it with the survey attached.
6. **Delegation by task shape** is CLAUDE.md rule 9 (landed with this
   handover). The subagent default is `CLAUDE_CODE_SUBAGENT_MODEL: opus`
   in the `env` block of `~/.claude/settings.json`, live and verified
   from a running Fable session on 2026-09-22. The `fork` type ignores
   it; typed agents with a `model:` line in their definition override
   it.
7. **Model**: the Harness session runs on Fable; its passes spawn on the
   default (Opus). The trial record says whether Opus misses things.

## First deliverables, in order

1. **The "what lives where" table** for THREADS.md: claims in
   `experiments/FINDINGS.md`, evidence in the per-arc `RESULTS.md`,
   decision inputs on the Gen 2 shelf (`experiments/fog-gen1-shakeout/GEN2-INPUTS.md`),
   rules in `experiments/DESIGN-DOCTRINE.md`, the product register in
   `BACKLOG.md`, open decisions in the `owner-call` issues, session state
   in the memory directory, thread rules in `THREADS.md`, work rules in
   `CLAUDE.md`. Ten lines; a draft for the owner's ruling.
2. **The condense log and the CI budget**: `CONDENSE-LOG.md` (location
   Harness's call), one line per pass with the origin/main SHA; a
   workflow job that diffs from that SHA and applies the two-tier
   budget. The first log line is the SHA at which the budgets were set.
3. **The accuracy-gate skill**, with its trial record started on its
   first real use. First real use: the next Experiments write-up.
4. **The condense skill**, first run on the always-loaded files. The
   owner has said the passes are useful only if they beat the current
   habit of open-ended "please persist"; the record decides.
5. **The jscpd survey** on `crates/`, `client/`, `experiments/` (read
   only, report to Product with a proposed threshold per language and
   the test-module handling).
6. **Take over the prepare-for-compact skill**: add the "Delegated this
   arc" line rule 9 promises to the anchor's sections, and a MEMORY.md
   byte budget to hard check 8.
7. **A mechanical guard for the Chebyshev trap**: lab code that computes
   `max(abs(` on tile coordinates fails a grep check unless the file
   carries the tier-1 declaration label. Background in the memory file
   `movement-is-manhattan` (2026-09-22).

## Facts that were only in conversation

- The settings file's `env` block reached a running session's tool
  shell without a restart, and a plain general-purpose subagent spawned
  from Fable reported `claude-opus-5`. A shell-function variable set at
  launch did not appear to work for the owner; the four older sessions
  predate the function and have been resumed since, which is the likely
  reason. Keep the settings block as the one source.
- All four peer sessions were started around 2026-09-12 and are resumed
  with `claude --model claude-fable-5 --resume <name>`; Client ran trial
  2 on Opus.
- Experiments appends to `TRIALS.md` on main directly; Product and
  Client via PR. Harness, as owner, edits it via PR like any of its
  files, and the append-shared rule for trialling threads stands.
- The shipped-config sweep loads every toml under `experiments/`; a CI
  budget job must not touch tomls. Local sweep red on record: the
  untracked `experiments/trait-screen-2026-08-15/configs/trait-bath-0.5.toml`.
- Rule 5 applies to skills and hooks as much as to code: a hook change
  gets a red (a command it must refuse, refused; one it must allow,
  allowed) before it merges. `mutate.sh` refuses an untracked file, so
  commit first, then red.

## Kickoff prompt (for the owner to paste)

> You are CloudKitty Harness, the fifth thread. Read THREADS.md, then
> `.claude/HANDOVER-harness-2026-09-22.md`, then MEMORY.md. Work in a
> worktree from the first command. Your first deliverable is the
> "what lives where" table as a draft for my ruling; nothing else
> starts until I say go on it.
