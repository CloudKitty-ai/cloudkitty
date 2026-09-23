---
name: "accuracy-gate"
description: "Hard gate on a results write-up before it commits: a fresh-context subagent re-runs the doc's Read block in the native checkout and three-way compares doc, fresh JSON, and recorded JSON; FAIL blocks the commit until the doc or the reader is fixed."
compatibility: "CloudKitty threads (THREADS.md); assumes raws in the native checkout and a Regeneration block with a Read fence"
metadata:
  author: "cloudkitty"
user-invocable: true
disable-model-invocation: false
---

# Accuracy gate

`/accuracy-gate <RESULTS.md> <section>` — run by the OWNING thread,
last, before committing a write-up. The gate is HARD: FAIL means no
commit until the doc or the reader is fixed (owner ruled 2026-09-22).
A write-up is the one artifact a session cannot proofread itself —
the session that wrote it also chose the numbers it remembers.

Ownership (THREADS.md §1): this file is Harness's — edits route
there. `TRIALS.md` beside it is append-shared: the owning thread
appends a section every run, pass or fail.

## What one run gates

One RESULTS.md section, plus the FINDINGS.md entry and the
GEN2-INPUTS.md line that land in the same commit (tier 6's 8dc0f10
carried all three). The F-entry and the shelf line get a COPY check
only: every number and quote in them must appear in the cited section
at the same printed precision. Product spec read addenda join later.

## The subagent

One subagent, fresh context, run in the NATIVE checkout — the raws
live there, never in a worktree (worktree-remove eats them). Default
model: the settings file sets it. Never show it
`fixture/expected-findings.md` or any other answer key. It:

1. Runs ONLY the `### Read` fence of the section's Regeneration
   block, writing fresh JSON to the scratchpad. It never edits a
   file and never runs a `### Collect` fence.
2. Asserts the fresh seed counts equal the recorded JSON's before
   comparing anything — a partial battery silently drops counts and
   every downstream mean shifts while every row still looks sane.
3. Makes three compares: doc vs fresh JSON; fresh vs recorded JSON;
   prose vs numbers it re-derives itself from either.

The subagent's report is evidence the owning thread reads (CLAUDE.md
rule 9), never a verdict to paste. The owning thread writes the stamp
and the TRIALS entry.

## The regeneration contract — forward-only

Confirmed forward-only (owner, 2026-09-22): docs written before this
skill are not rewritten to satisfy it; they gate as far as their
paths resolve (the tier 1–6 docs carry seven `...` elisions). From
now on a section's Regeneration block carries:

- `### Collect` and `### Read` as separate fences; the gate never
  runs Collect.
- Full paths, no `...` elisions.
- Env inline per read line (the venv interpreter, `CERT_ARTS`).
- Declared runtime per read line (`distress_inspect` replays
  minutes; a gate that discovers that mid-run guesses wrong about
  hangs).
- Every read names `--out`; new readers ship `--md` and print every
  derived column the doc uses.

No usable Read block = **UNGATEABLE**: stamped as such, and the
owning thread takes the section to the owner — the gate cannot pass
what it cannot re-run, and it does not pretend to.

## Claim kinds and verdicts

Every claim in the section is one of five kinds.

1. **Arithmetic** — recomputed from fresh JSON or from printed
   cells. CONTRADICTED fails.
2. **Threshold** — each claim naming a bar states its SOURCE: a
   prereg line, a reader constant, or unsourced (reported). A
   prediction claim reports two things separately: the arithmetic
   against the declared range, and the characterisation of it.
3. **Characterisation** — SUPPORTED / WEAK / CONTRADICTED, one
   sentence of grounds each. CONTRADICTED fails anywhere. WEAK fails
   in "Decision rules, applied" and on any line naming an F-number
   or an owner ruling; elsewhere it is reported.
4. **UNDECIDABLE** — no regeneration path (a replay not run, a raw
   not present). Counted, never fails alone.
5. **Provenance** — issue quotes verbatim against the issue, SHAs,
   seed counts × ticks, borrowed comparator rows against their
   source doc. Mechanical; a miss fails. An addendum that QUOTES the
   sentence it corrects retires that sentence from the gate; a
   paraphrase does not.

## Tolerance

- A reader-backed cell matches if the fresh value rounds to it at
  the printed precision. Integers exact. A printed range: fresh
  value inside it.
- A derived cell (a doc-written gain or difference) may match from
  raw values OR from printed-cell arithmetic — the doc may have
  subtracted before or after rounding. Exactly one unit off in the
  last printed digit = ROUNDING, reported, never a fail; larger
  fails.

## Output and stamp

The subagent's report: counts per claim kind; every non-SUPPORTED
claim quoted with its numbers and grounds; verdict **PASS / FAIL /
UNGATEABLE**. The owning thread then writes one stamp line at the end
of the section's Regeneration block — verdict, date, claim counts,
raw-dir hash — and appends the run to `TRIALS.md` beside this file.

## The fixture (rule 5)

`fixture/RESULTS-tier6-planted.md` is the tier 6 read with four
plants; `fixture/expected-findings.md` names them and stays out of
the subagent's context. Running the gate on the fixture must FAIL
listing exactly those four — predict that in writing before the run.
Re-run the fixture on every edit to this skill that changes what
fails. When a real run misses an error the report should have
caught, the miss becomes a new plant: the fixture grows from real
failures, not from what plausibly could fail.
