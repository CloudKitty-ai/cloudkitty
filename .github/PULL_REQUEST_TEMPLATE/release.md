<!-- Release PR template (checklist item 12; owner's word 2026-09-27).
     Open the release PR with ?template=release.md. The tag waits for
     four ticks — one per thread — and a green dispatch of tag-rigor.yml
     on this branch. Mechanical rows live in scripts/tag-check.sh; only
     the human-judgment rows are listed here. -->

# Release X.Y.Z — <tagline>

## Mechanical gate

- [ ] `tag-rigor` workflow dispatched on this branch and **green**
      (full `scripts/tag-check.sh` + quickstart smoke). Paste the run link:
- [ ] `scripts/tag-check.sh --tag X.Y.Z` run locally: version/CHANGELOG/tag
      agree, `## Unreleased` is expanded.
- [ ] The staleness REPORT reviewed — every flagged §6 home is either
      updated or its subject truly did not change this release (say which,
      below the sign-offs).

## Human rows — Product

- [ ] README claims of state ("all five kitties…", generation, "next:" list)
      match `policies/README.md`.
- [ ] `docs/deployment.md` + `docs/deploy/*.sh` hosts and service names current.
- [ ] `evals/` suite version notes current.
- [ ] CHANGELOG compatibility markers on every entry that needs one.

## Human rows — Experiments

- [ ] `PIPELINE.md`, `ROADMAP.md` describe the current pipeline/plan
      ("current as of" stamps updated).
- [ ] `experiments/README.md` "owed" list reconciled against code.
- [ ] `DESIGN-DOCTRINE.md` rulings carry their issue numbers.
- [ ] `GEN2-INPUTS.md` closed inputs pruned.
- [ ] Evidence bundles for this release's findings uploaded on the owner's
      word (one batched approval; ruling 2026-09-27).

## Human rows — Client

- [ ] `client-measurements/README.md` tool list current.
- [ ] `scripts/tag-check.d/client-ship.txt` / `client-noship.txt` reviewed:
      classification still right, deploy exclude wired to it.

## Human rows — Harness

- [ ] `THREADS.md` / `CLAUDE.md` dated rulings: none superseded unmarked.
- [ ] `BACKLOG.md` spot-check: shipped entries removed at their merge.
- [ ] GLOSSARY report reviewed; new in-house terms this release have entries.

## Sign-off (the tag waits for all four)

- [ ] Product
- [ ] Experiments
- [ ] Client
- [ ] Harness

## Staleness dispositions

<!-- one line per flagged home: updated | unchanged-subject (why) -->
