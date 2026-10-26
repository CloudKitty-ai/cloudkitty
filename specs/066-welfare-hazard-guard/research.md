# Research: Welfare-Hazard Acknowledgement Guard

No NEEDS CLARIFICATION markers remain (four owner rulings in spec.md
§Clarifications). The decisions below resolve the plan-level unknowns
the spec left open, each measured against the tree at 60f9dc78.

## D1. Config shape: `[welfare_hazard] acknowledged = [...]`

- **Decision**: `Config.welfare_hazard: Option<WelfareHazardConfig>`
  with `#[serde(default, skip_serializing_if = "Option::is_none")]`;
  `WelfareHazardConfig { acknowledged: Vec<String> }`,
  `deny_unknown_fields`. Present (even with an empty list) it
  serializes; absent it does not.
- **Rationale**: the exact attribute pair `starts` and `initial_needs`
  use (config/mod.rs:101, :110) — proven to keep `engine_defaults_sha256`
  and `GET /config` unmoved when absent. Serializing when present is
  what makes the acknowledgement visible on `GET /config` (FR-007).
- **Alternatives**: a boolean `unsafe = true` — rejected by the spec
  (a new mode would ride under an old flag); a per-mode table
  `[welfare_hazard.initial_needs]` — rejected: the list form is the
  spec's and the error's "line to add" is one line.

## D2. Registry: a closed enum in `config/welfare_hazard.rs`

- **Decision**: `pub enum HazardMode { InitialNeeds }` with
  `HazardMode::ALL`, `name() -> &'static str` (`"initial_needs"`), and
  `activation(&self, &Config) -> Option<String>` returning the FIRST
  activating site as text (`[initial_needs].cuddle = 92` or
  `[[kitty]] 'Mochi' (id 3) initial_needs.eat = min = 0, max = 90` — the
  setting rendered exactly as `validate_initial_needs` renders its
  error value, guard-law §2) or `None` when inactive. `Config::active_hazards()` maps `ALL`
  through it. No teacher-eligibility field (owner, clarify Q4).
- **Rationale**: a closed enum IS a closed registry; a new mode cannot
  be guarded without a match arm, and `ALL` makes the sweep and the
  validator iterate the same list. The site text reuses the home
  strings `validate_initial_needs` already builds (validate.rs:1151 for
  the roster table, :1156 for a kitty override).
- **Alternatives**: a `&'static [HazardEntry]` of name + fn pointer —
  rejected: an enum gets exhaustiveness checks for free.

## D3. Predicate for `initial_needs` (owner, clarify Q2: widest)

- **Decision**: active iff ANY governing setting — the roster-wide
  table or any per-kitty override, any of the six needs — is
  `NeedInit::Value(v)` with `v > 0.0` or `NeedInit::Range(r)` with
  `r.max > 0.0`. Resolution precedence is irrelevant: a per-kitty
  override at 0 over a roster table at 90 still has the table present
  with a raised value, and the spec counts the written setting, not
  the resolved one. The predicate runs after `validate_initial_needs`,
  so every number it reads is finite and in bounds.
- **Rationale**: the widest reading; "present but every need at zero"
  is inert (spec Edge Cases), and zero is the pre-065 spawn value.

## D4. Exactness as a pure function

- **Decision**: `pub(super) fn check_acknowledgement(acknowledged:
  Option<&[String]>, active: &[(&str, String)], known: &[&str]) ->
  Result<(), ConfigError>` in validate.rs (`None` = section absent, so
  the error's value can say `absent`), checked in this order: unknown name → duplicate →
  missing (lists EVERY missing mode with its site and the exact line
  to add) → stale (lists every stale name). `validate_welfare_hazard`
  feeds it the registry's output and is called from
  `Config::validate` directly after `validate_initial_needs()`
  (config/mod.rs:1725).
- **Rationale**: with one registered mode the "partial" shape (some
  acknowledged, some missing) is unreachable through a real config;
  the pure function is unit-tested with a synthetic two-mode active
  set so all five shapes of SC-002 are red/green today, and the
  registry-driven wrapper is tested with the real mode. The
  `[welfare_hazard]` section absent and nothing active returns Ok
  before any allocation — the inert path does no work.
- **Error shape**: `ConfigError::invalid(field, value, expected)` with
  field `[welfare_hazard] acknowledged`, value the list as written (or
  `absent`), expected the sentence per contracts/guard-law.md §4. One
  `Display` string; the "line to add" appears verbatim inside it.

## D5. Sweep rule: outside `experiments/`, no active mode

- **Decision**: both sweeps gain `fn hazard_outside_experiments(root,
  file, &Config) -> Option<String>` returning the failing message
  (file + mode names) when the file is not under `<root>/experiments/`
  and `active_hazards()` is non-empty; the loop panics on `Some`. Each
  sweep file gets an in-file self-test on a scratch tree (one
  hazardous toml under `scratch/experiments/x/`, one under
  `scratch/specs/x/`) in the shape of `collect_never_follows_a_symlink`.
- **Rationale**: the rule must hold in BOTH sweeps (the RL one is the
  only one that loads `evals/v3` through `load_configs_from_str`, and
  the two collectors are maintained as mirrors since #468). Files under
  `experiments/` reach FR-004 through the existing `validate()` call,
  so no extra rule is needed there. A self-test on a scratch tree gives
  rule 5 a red without staging a file in the real tree.

## D6. Server switch: `--allow-welfare-hazard`, bare

- **Decision**: one flag in the hand-parsed `Args` (main.rs:16) with a
  HELP line; `Args.allow_welfare_hazard: bool`. The gate
  `welfare_hazard::gate(&config, allowed) -> anyhow::Result<()>` runs
  immediately after `config.validate()?` in `run()` (main.rs:236) —
  before the registry is built, before `load_or_generate_world`. It
  errs when `config.welfare_hazard` names one or more modes and the
  switch is absent; the message names the modes and the switch. With
  the switch, or with no acknowledged mode, it returns Ok.
- **Rationale**: owner, clarify Q3 (bare). Reading the acknowledged
  list rather than re-running the predicate is safe because
  validation has just proven the two sets equal; the gate stays a
  three-line function with no second copy of the predicate.
- **Alternatives**: an environment variable — rejected: the server's
  only env input is the log filter (settings.rs:36) and the house
  records dials from the command line and the file.

## D7. Visibility surfaces

- **Boot line**: `welfare_hazard::log_boot(&config)` emits one `info`
  line only when the list is non-empty, beside the other world-law
  lines (after `stuck::log_boot`, before `settings.announce()`):
  `welfare-hazardous world served on purpose (--allow-welfare-hazard):
  acknowledged modes initial_needs`. Silent otherwise — the served
  boot log stays byte-identical (the spec 045 silence rule).
- **`GET /config`**: automatic — `get_config` serializes the `Config`
  (api.rs:144) and D1 serializes the section when present.
- **Key-settings row**: `settings::build` pushes
  `welfare_hazard.acknowledged = ["initial_needs"] [toml]` (no default
  column) as the LAST entry, only when the list is non-empty. The
  pinned-names golden (`the_key_names_are_pinned`, minimal config)
  is unchanged; a new test pins the row's presence, position and
  rendering on an acknowledged config and its absence on an empty
  list.
- **Rationale**: FR-007 wants "no row, no line" without an
  acknowledged mode (the section itself follows D1: absent stays
  absent, a written empty list serializes); a conditional row is new to
  the block, so it gets
  its own pin rather than widening the minimal golden.

## D8. Fingerprint

- **Decision**: `Config::fingerprint()` (config/mod.rs:1810) is not
  edited; a test pins that two configs differing only in the section
  fingerprint equal (red by mutating the format string to include it).

## D9. Migration of the seven files

- **Decision**: append exactly
  `\n[welfare_hazard]\nacknowledged = ["initial_needs"]\n` to each
  (all seven end in a single `\n` on main, verified 2026-10-26), with
  `printf` in a loop; no other byte moves. Verification: strip the
  trailing table and sha256 the remainder, compare to the pre-retrofit
  hashes in `experiments/gen2-deviations.md` entry 14 — a read-only
  check of Experiments' contract, run here; their own `check_set` /
  `check_P` / `test_phase1b` runs on the landed tree are theirs.
- **Rationale**: owner to Experiments, "Option 1 for the retrofit";
  main 304221b1 strips exactly this shape.

## D10. Paths that validate without the server

All of these reach the guard through `Config::validate` with no edit:
`load_configs_from_str` (cloudkitty-rl/src/config.rs:395 — the Python
environment, `kitty-eval`, the suite loader, the needs/distress census
tools), and the tools that call `toml::from_str` + `.validate()`
directly (bc-collect, contact-census, twin-probe, family-gen — all in
Experiments' lane, listed here so their owners know the refusal reaches
them; nothing to change on this side).

## D11. Spec 065's FR-009 prose

Left untouched: 065 is a landed record; FR-005 here supersedes its
prose with a check, and `specs/INDEX.md` carries this spec's row.

## D12. Documentation

CHANGELOG `## Unreleased` gets one public-voice entry (no
compatibility marker: stamp, obs-schema, fingerprint and draw order all
unmoved). `docs/deploy/` is not changed; whether the live box ever
passes the switch is a deploy ruling. The `experiments/README.md`
pointer stays a proposal to the owner (spec Assumptions).
