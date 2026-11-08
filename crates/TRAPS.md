# Product traps and lessons

What Product's code (`crates/`, `evals/`, `specs/`, the root manifests
and configs) does that bites, and the method changes it taught
(THREADS.md §6; owner ruled 2026-09-22: one file per thread, co-located).
Entry: date, the trap in a sentence, where it bites, the evidence, the
guard if any. A trap a guard now catches is deleted; the guard is its
home. Harness's tooling traps (`scripts/mutate.sh`, the hooks, GitHub's
refusals) live in `.claude/TRAPS.md`, not here.

## Traps

- **2026-09-14** — `tracing` caches a callsite's interest process-wide from
  the thread that first hits it, so under parallel tests a scoped
  subscriber can miss the line it asserts on (the cache was filled by
  another test's dispatcher, or by none). *Bites:* any test asserting a
  log line through `tracing`. *Evidence:* spec 053 review (08249303),
  `cloudkitty-server/tests/seat_class_log.rs` runs as its own binary for
  this reason. *Guard:* none mechanical; use `test_log::capture` in the
  server crate and give a log-asserting test its own binary.
- **2026-10-20** — `ubuntu-latest` is 26.04 and its coreutils are uutils:
  `cat` and `/usr/bin/printf` exit 0 writing to a closed stdout (GNU exits
  1; `/dev/full` still fails). *Bites:* a shell guard on write-failure
  status. *Evidence:* #466 (ff2ece00). *Guard:* that guard uses bash's
  `printf` builtin; the entry stays because the next one will reach for
  `cat`.
- **2026-10-27** — the needy preset (spec 067) is sized by the need count:
  a seventh `NeedKind` extends it by a default weight and a floor entry
  and nothing else (FR-016). *Bites:* adding a need. *Evidence:* #471.
  *Guard:* none; re-run FR-016's grep (`\b6\b` in `needy.rs`) at the
  change.
- **2026-11-06** — `Activity::is_continued_by` treats Idle as continuing
  every scene, so a duration-enforcement guard staged as "propose Idle
  inside a minimum" is vacuous (exit 6). *Bites:* any guard on
  `enforcement_verdict`. *Evidence:* #491, G11's first cut. *Guard:* none;
  stage a solo Sleeping/Resting inside its minimum and propose a
  validation-legal Move onto a free tile.
- **2026-11-06** — the legal mask already replays duration enforcement, so
  inside a minimum every mask-legal act is a continuation: a guard cannot
  pick its interrupting act from the mask, and an override that names a
  mask-illegal act is ruled on by the engine, not refused. *Bites:*
  guards and readers that treat "mask-legal" as "will apply". *Evidence:*
  #491 (G11's second cut; the parity note in
  `specs/068-world-branch/contracts/python-api.md`). *Guard:* none.
- **2026-11-06** — `collect_step` builds per-agent infos for EXTERNAL seats
  only; a scripted seat's proposal, provenance and seed are reached
  through `Episode::tick_records()` (Python `tick_records()`), never
  through `infos`. *Bites:* a test or reader expecting a built-in seat in
  `infos`. *Evidence:* #491. *Guard:* none.
- **2026-11-06** — `Config::fingerprint()` is `w{}h{}s{}k{}`: weak, and it
  includes the seed, so it cannot identify a configuration across seeds.
  *Bites:* any identity check built on it. *Evidence:* #491 (spec 068
  derives `config_digest` as a sha256 of the serialized config with the
  seed zeroed and uses the fingerprint only as a tamper check on a parsed
  world). *Guard:* G20 pins the digest's seed-independence.
- **2026-11-06** — `Episode::new` auto-seats a needy config seat and treats
  an unnamed roster seat as External, so two control maps that differ only
  in what they leave unsaid describe one environment. *Bites:* comparing
  control maps. *Evidence:* #491 review (G16's normalization case).
  *Guard:* `Episode::control()` normalizes over the roster; compare that,
  never the constructor's map.

## Lessons

- **2026-10-26** — a new validator whose error reuses an OLD error's field
  text can make the old guard vacuous (065's bounds test asserted only the
  field name, which 066's missing-acknowledgement error also carried).
  Mutate the OLD validators after adding one. *Evidence:* #469 (3ba039c4).
- **2026-11-06** — an "untouched" assertion compares the whole state to its
  pre-call serialization, never one field: a restore that rewrote the
  world but kept the clock passed G16's first cut. *Evidence:* #491 review.
