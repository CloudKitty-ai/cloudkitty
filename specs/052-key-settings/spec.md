# Feature Specification: Key Settings (the effective-values block)

**Feature Branch**: `052-key-settings`

**Created**: 2026-09-08

**Status**: Draft

**Input**: Owner question (2026-09-08, Product thread): "Should we update the upgrade script so that it ends with outputting a 'key settings' section so that we can verify what's enabled?" Answer relayed and accepted: yes, with the truth in the server, not the script. The invocation of `/speckit-specify` here is the go.

## Problem

Every dial that mattered this month needed a "was it actually on?" answer after a deploy — the groom bump and its owed revert, `announce_here`, the waterline contagion flip, the vision radius, `[meow] relief_memory_margin` — and each answer was read a different way: a hand-written boot line, a grep of the journal, a curl of `/config`, or memory of what the toml said. Those readings are not equivalent, and one of them is structurally unable to answer:

- `GET /config` serialises the validated config with every engine-defaulted field **skipped** (spec 039 pins its key set and the `engine_defaults_sha256` stamp on it). On the box today its output carries no `vision`, no `meow.relief_memory_margin`, no `water.contagion_*`; "not set" and "at the default" are indistinguishable from outside. It cannot grow keys, so it cannot become this feature.
- The boot log names three dials because three specs each added a line by hand (wet fur and contagion, spec 044/045; the vision radius, spec 049). Anything not so blessed is silent, and a pipeline that drops fields must read the rule off a sentence.
- The deploy script ends with `deployed <rev> — serving at …` and a five-line unit status. Verifying a dial means opening the journal afterwards, by eye.

The fix is one list, owned by the server: the **key settings**, every entry an *effective* value (after defaults and validation), said once at boot, served read-only at `GET /settings`, and printed by `docs/deploy/update.sh` as its closing section so a deploy's own output answers the question. One source, three readers, nothing to drift.

## Clarifications

### Session 2026-09-08

- Q: Should each key setting carry only its effective value, or also its default and where the value came from? → A: All three: `value (default: <engine default>) [source]`, where source is `toml` (the key is written in the served config) or `default` (it is not). A third source does not exist today — the server's command line takes only paths and `--fresh`, and the only environment variable it reads is the log filter — so the source tag is a two-value set, defined so a future override layer adds a value rather than a rewrite. Keys with no meaningful engine default (world size and seed, the seats) carry no default.
- Q: When the deploy succeeds but the key settings section cannot be produced, exit non-zero or warn and exit zero? → A: Exit non-zero, message naming the cause, no rollback; the `deployed` line and the backup prune still run first. Owner asked whether the script could hit the endpoint too soon after start: verified in the source that the server loads the config, builds its state, registers every route, and only then binds the listener; the health check needs `/world` to answer twice, three seconds apart, before the section runs. So the endpoint is answerable whenever the health check passes — provided the block is built at boot, not on first request (now FR-006a).
- Q: Should a test also pin the served toml's full block (values, defaults, sources), so a later served-dial change is a golden diff? → A: No. Pin key names only (FR-011). The toml diff and the existing config sweeps already show a value change; a key silently dropped from the served toml shows up as `[default]` in the deploy tail, which is where anyone would look.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A deploy ends by stating what is on (Priority: P1)

The operator runs the update script; after the world is confirmed serving, the last thing on the terminal is a `key settings` section listing every key setting and its effective value, read from the running server — not from the toml that was copied, not from the script's idea of the defaults.

**Why this priority**: this is the owner's question verbatim. The deploy is the moment the answer is needed and the terminal is where the operator already is.

**Independent Test**: run the deploy path against a server that serves `/settings`; the output ends with the section and every key in the list appears with a value. Run it against a server that does not (an older binary): the script says so by name and exits non-zero, without rolling back a world that is serving.

**Acceptance Scenarios**:

1. **Given** a successful deploy (the server answers the health check), **When** the script finishes, **Then** its final section is titled `key settings`, one setting per line in the form `key = value (default: d) [source]`, and contains every key in the list below.
2. **Given** the served toml leaves an optional key absent, **When** the section prints, **Then** that key still appears, showing the engine default (or the rule that "absent" selects) tagged `[default]`, never blank and never missing.
3. **Given** the served toml writes a key at exactly its engine default, **When** the section prints, **Then** the line reads `value (default: value) [toml]` — the tag says the edit landed; the parenthesis says it changed nothing.
4. **Given** a deployed binary that predates this feature (no `/settings`), **When** the script reaches the section, **Then** it prints a message naming the cause ("this binary does not serve /settings") and exits non-zero; the world stays up and nothing is rolled back.
5. **Given** the server is serving but `/settings` returns an empty or unreadable body, **When** the script reaches the section, **Then** it exits non-zero with a message distinct from scenario 4.
6. **Given** the health check passed but the server stops answering before the section runs, **When** the fetch fails to connect, **Then** the script exits non-zero with a third message ("the server stopped answering after the health check"), distinct from 4 and 5, and still does not roll back — the operator reads the unit status the script already printed.
7. **Given** the client-only deploy path (no server restart), **When** the script finishes, **Then** its output is unchanged — the server's settings did not move, so nothing is re-stated.

---

### User Story 2 - Anyone can ask the running server (Priority: P2)

A person (or a census script, or a peer thread reading deploy state off the running system instead of off conversation memory) fetches `GET /settings` from the served world and gets the same list: every key, every effective value, in a machine-readable shape, regardless of which keys the config set.

**Why this priority**: the deploy tail is one reader; the standing rule is "read deploy state off the RUNNING SYSTEM". The endpoint is that rule made cheap, and it is what the script itself reads.

**Independent Test**: start a server on a minimal config (every optional key absent) and on the served toml; fetch `/settings` from each; both return the identical key set, and the values differ only where the configs differ.

**Acceptance Scenarios**:

1. **Given** a running server on any valid config, **When** `/settings` is fetched, **Then** the response carries every key in the list below, each with its effective value, its engine default (where one exists), and its source (`toml` or `default`); no key is skipped for being at its default.
2. **Given** an optional key whose absence selects a rule (`[meow] relief_memory_margin` absent = unbounded memory reach; `[behavior] reply_intensity_floor` absent = no floor), **When** `/settings` is fetched, **Then** the entry states the effective rule in words or as an explicit sentinel — never `null`, never omitted — and its source reads `default`.
3. **Given** a minimal valid config — every section present (under the 3.0 rule every section is required; only inert launch dials have per-key defaults) with every optional listed key absent, plus exactly one optional listed key written — **When** `/settings` is fetched, **Then** that key and the required keys (`world.*`, the seats, `vision.*`) read `toml` and every other optional listed key reads `default` (the per-key guard that the source check reads the right path).
4. **Given** a boot with no config file at all (the server's built-in-defaults path), **When** `/settings` is fetched, **Then** every key's source is `default`.
5. **Given** the served toml, **When** `/config` is fetched before and after this feature, **Then** its output is byte-identical and `engine_defaults_sha256` is unmoved (spec 039's contract; this feature adds a route, it touches nothing `/config` serializes).
6. **Given** the endpoint, **When** it is called with any method other than GET, or with a body, **Then** it behaves like every other read-only endpoint here (the viewer is a window, not a control surface).

---

### User Story 3 - The journal says the same thing (Priority: P3)

At boot, after the config is validated and before the first tick, the server logs the key settings as one block — the same keys and values the endpoint serves — so a journal excerpt is evidence on its own, and the three hand-written per-spec lines stop being the only place a dial is spoken.

**Why this priority**: the journal is what survives a restart and what gets pasted into a ruling. It should not disagree with the endpoint, and it should not depend on which spec remembered to add a line.

**Independent Test**: boot a server under a captured log; the logged block and the `/settings` response name the same keys with the same values (a test compares them key by key).

**Acceptance Scenarios**:

1. **Given** a server booting on any valid config, **When** the log is read, **Then** one `key settings` block appears at info level, once, before the first tick, listing every key in the list with its effective value, default and source.
2. **Given** the boot block and a `/settings` fetch from the same process, **When** they are compared key by key, **Then** they agree on every value, default and source.
3. **Given** the existing per-spec boot lines (wet fur, contagion armed/disabled, vision radius, the ladder gate), **When** this feature lands, **Then** those lines are unchanged — they are cited by their specs' redden lists and stay as they are; the block is added beside them, not in place of them.

---

### Edge Cases

- **A key list that drifts.** The list is the contract. A test pins the set of key **names** (a golden), so adding or dropping a key is a visible diff in that golden, never a silent change to what the deploy tail shows. Values are not pinned (they are the config's business).
- **Foreign tables.** `[watchdog]` is parsed by the server, not the engine, and never serializes into `/config`. Its threshold is a key setting all the same; the block is assembled where the server sees both the engine config and its own.
- **Absent optional keys.** Covered by US2 scenario 2: the entry renders the rule, not `null`, and its source is `default`.
- **A key written at its default.** `5 (default: 5) [toml]`: the source says the edit landed, the parenthesis says it changed nothing. Neither column alone answers both questions, which is why both are there.
- **No config file.** The server boots on built-in defaults; every source is `default`, and the block still prints in full.
- **Seats and world shape.** A valid config always has a world and at least two seats (Article III), so their source is `toml` whenever a file was loaded; they carry no default column.
- **Inert dials.** `[water] contagion_factor = 0` still lists `contagion_membership`; a dial is listed because it is a key, not because it is currently doing something. The reader decides what "off" means.
- **A resumed world.** Settings come from the loaded config, not the snapshot; the snapshot fingerprint check (spec 039) already refuses a config that disagrees with the saved world's shape. The block states the config the process is running.
- **No hot reload.** The block is fixed at boot; the endpoint serves the same values for the life of the process. (There is no reload path in this server; none is added.)
- **Too soon after start?** Not possible by construction: the server registers every route and builds the block before it binds, and the script's health check needs two answers from `/world` three seconds apart before the section runs. FR-006a keeps it that way.
- **A server that is up but the section fails.** The deploy has succeeded (the world serves); the verification has not. The script exits non-zero **after** its `deployed` line and the backup prune, so a stale generation is not kept by accident and the exit code still says "look at this".

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The server MUST hold **one** definition of the key settings list, from which both the boot block and the `/settings` response are produced. There is no second list to fall out of step.
- **FR-002**: Every entry MUST carry three things: the **effective** value (what the running engine uses after defaults and validation, not the raw toml text and not "unset"); the **engine default** for that key, where one exists; and the **source**, `toml` when the key is written in the loaded config file and `default` when it is not.
- **FR-003**: An optional key whose absence selects a rule MUST render that rule explicitly (a word or sentinel the reader can act on), never `null`, never omitted; its default column shows the same rule.
- **FR-003a**: The source MUST be decided by the key's presence in the loaded config text, not by comparing the value to the default; a key written at its default reads `[toml]`. With no config file loaded, every source is `default`. The source set is `{toml, default}`; no other origin exists in this server today, and adding one later is adding a value to the set.
- **FR-004**: `GET /settings` MUST return every key in the list on every valid config; no key is skipped because it sits at its default.
- **FR-005**: `GET /settings` MUST be read-only and MUST NOT change the behavior, output, key set, or `engine_defaults_sha256` stamp of `GET /config`.
- **FR-006**: At boot, after validation and before the first tick, the server MUST log the key settings once as one block, at info level, with the same keys and values the endpoint serves.
- **FR-006a**: The block MUST be computed once at boot, before the listener binds, and held for the life of the process; the endpoint serves the held block. This is what makes "the health check passed" imply "the section can be produced": there is no first-request work to race against.
- **FR-007**: The existing per-spec boot lines (wet fur / contagion, vision radius, ladder gate) MUST be left unchanged.
- **FR-008**: `docs/deploy/update.sh` MUST, on the server-restart path after the health check passes, fetch `/settings` from the running server and print it as its **last** section, titled `key settings`, one setting per line.
- **FR-009**: If `/settings` is not served by this binary, or returns an empty or unreadable body, or the server no longer answers at all, the script MUST print a message that names which of the three it was and MUST exit non-zero, without rolling back and without skipping the `deployed` line or the backup prune.
- **FR-010**: The client-only deploy path MUST be unchanged.
- **FR-011**: A test MUST pin the set of key names (a golden), so a change to the list is a deliberate, visible diff.
- **FR-011a**: A test MUST show, for a minimal valid config (every section present, every optional listed key absent) plus exactly one optional listed key, that that key and the required keys read `toml` and every other optional listed key reads `default` (US2 scenario 3), and that a no-config boot tags every key `default` (US2 scenario 4).
- **FR-012**: The boot log MUST be emitted by the same renderer the endpoint serves as text, and a test MUST capture the emitted log event and show its message equals that renderer's output; a second test MUST show the endpoint's text and JSON carry the built value unchanged.
- **FR-015**: Every guard this spec adds MUST run in CI, including the deploy-script test; the repository's existing by-hand shell tests (the two hook self-tests and the mutation-runner test) join the same CI step, so "run in CI" (Article VI) holds for every guard in the tree, not only the Rust ones.
- **FR-013**: The README endpoint table and `docs/deployment.md` MUST list `GET /settings` and say what it is for, in the register those documents already use.
- **FR-014**: `CHANGELOG.md` `## Unreleased` MUST carry a one-line entry.

### Key Entities *(include if feature involves data)*

- **Key setting**: a named dial with its effective value, its engine default (where one exists), its source (`toml` / `default`), and the config path it lives in — the path is what the source check reads. The list, as of this spec (the golden of FR-011 is this list):

  | Group | Key | Config path | Default column | Absent means |
  |---|---|---|---|---|
  | (header) | `engine_defaults_sha256` | computed stamp (spec 039); rendered as the block's first line, not an entry, so it carries no source | none | — |
  | world | `width`, `height`, `seed` | `[world]` | none | — |
  | seats | per kitty: `id`, `name`, `behavior` | `[[kitty]]` | none | — |
  | vision | `radius`, `memory_timeout_ticks` | `[vision]` | engine default | engine default |
  | meow | `relief_memory_margin` | `[meow]` | `unbounded` | `unbounded` (today's rule) |
  | actions | `groom_cuddle_relief` | `[actions]` | engine default | engine default |
  | behavior | `announce_here`, `contagion_aware_ladder`, `reply_intensity_floor` | `[behavior]` | engine default; floor `none` | engine default; floor absent = `none` |
  | water | `bath_gain`, `bath_gain_ceiling`, `contagion_factor`, `contagion_membership` | `[water]` | engine default | engine default |
  | watchdog | `threshold`, `remind_every` | `[watchdog]` (server-owned) | server default | server default |

  Growing the list is a one-line change in the one definition plus the golden; the bar for adding a key is "someone needed to verify it after a deploy".

- **Key settings block**: the list rendered once. Two renderings, same content: a structured response at `/settings` and a log block at boot.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: After a deploy, the operator can read every key setting's effective value from the deploy's own terminal output, with zero further commands (no journal, no curl by hand).
- **SC-002**: `/settings` returns the same key set on a minimal config (every optional key absent) and on the served toml — zero keys missing in either, every optional-key entry is a value or a named rule, never `null`, and every entry carries a source; on the served toml today, 100% of listed keys read `toml`.
- **SC-003**: `/config`'s output on the served toml is byte-identical before and after this feature, and `engine_defaults_sha256` is unchanged.
- **SC-004**: For one running process, the boot block and the endpoint agree on 100% of keys, values, defaults and sources, and a test goes red if the boot log stops emitting the renderer's output.
- **SC-007**: The CI run on the feature branch executes the deploy-script test and the three existing shell tests, and a deliberate break in any one of them fails the run.
- **SC-005**: Deploying a binary without `/settings` produces a non-zero exit and a message naming that cause, within the script's existing health-wait budget (no hang, no rollback).
- **SC-006**: The next dial anyone needs to verify after a deploy is added by editing one definition and one golden, in a diff a reviewer can read in under a minute.

## Assumptions

- **The deployed revision is the script's business, not the server's.** The binary embeds no source revision today and the script already logs `deployed <rev>`; adding build-time stamping is out of scope. The block's identity key is `engine_defaults_sha256`, which the engine already computes.
- **No authentication.** Every endpoint here is public and read-only (the viewer is a window); `/settings` inherits that posture. Nothing in the list is a secret (bind addresses and paths are not key settings and are not listed).
- **Rendering.** The endpoint returns a structured document; the script prints one setting per line as `key = value (default: d) [source]`, the parenthesis omitted where the key has no default. How the script turns one into the other (a plain-text rendering the server offers, or a tool on the box) is a plan decision, bounded by what the box has installed.
- **The list is the one above.** It is the union of the dials that needed a "was it on?" answer between 2026-08-14 and today. Anything else waits for a real need; `BACKLOG.md` takes the request as a one-liner.
- **No simulation change.** This feature reads config and serves it; it touches no tick, no observation, no reward, no legality. The stamp, the goldens, and the streams are expected unmoved, and SC-003 checks the one artifact that could move.
- **Owner-authored text** in the README, `docs/deployment.md`, and the served toml ships verbatim; this spec adds beside it and edits none of it.
