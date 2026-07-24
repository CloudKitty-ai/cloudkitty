# Quickstart: Validating 016 — Boundary Hardening & Behavior Plugins

**Feature**: 016-behavior-plugins | **Date**: 2026-07-23

The end-to-end validation runbook. Each step maps to success criteria; run
from the repository root. **Never run the real served world in place** — every
step here uses isolated test worlds or a scratch directory.

## Prerequisites

- Rust toolchain (workspace MSRV 1.83+), `cargo`
- Python 3 (or any scripting language) for the fixture plugin
- No new crates: `cargo tree` gains no external dependencies from this feature

## 1. The full regression gate (SC-001, SC-006)

```bash
cargo fmt --all --check
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace
```

Expected: everything green, including the untouched welfare property suite,
determinism suite, and fairness tests. SC-006 (plugin-free byte-identity) is
guarded by the existing determinism suite passing **unmodified**.

## 2. The wire: round-trip + rejection matrix (SC-002)

```bash
cargo test -p cloudkitty-core proposal
```

Expected: for all 11 action shapes — round-trip identity tests pass, and
every malformed-variant class (unknown kind, missing field, wrong type,
unrecognized value, incomplete target, extra field) fails to parse. The
[wire contract](contracts/wire-protocol.md) examples appear verbatim among
the cases.

## 3. Hostile plugin endurance (SC-003)

```bash
cargo test -p cloudkitty-core --test plugin_e2e hostile
```

Expected: a garbage-emitting fixture plugin advises a kitty for 1,000+ ticks;
every tick completes, constitution invariants hold throughout, every affected
decision is a fallback, rejection log events carry the parse errors.

## 4. Well-behaved plugin drives a kitty (SC-004)

```bash
cargo test -p cloudkitty-core --test plugin_e2e well_behaved
```

Expected: a fixture plugin proposing sensible actions drives its kitty for a
full in-world day (600 ticks); its proposals are applied and attributed to
the advisor, not the fallback.

## 5. Kill it mid-run (SC-005)

```bash
cargo test -p cloudkitty-core --test plugin_e2e killed_mid_run
```

Expected: the fixture process is killed partway; zero missed ticks, fallback
takes over from the first affected decision within budget, relaunch happens
after `relaunch_cooldown_ticks`, recovery is automatic.

## 6. Docs examples are live (SC-007)

```bash
cargo test -p cloudkitty-core docs_examples
```

Expected: every `json accepted` / `json rejected` fenced block in
`docs/plugins.md` parses / fails exactly as labeled.

## 7. Manual smoke: a real kitty, a real script (isolated)

In a scratch directory (never the live serving directory):

```bash
cp cloudkitty.toml /tmp/016-smoke/cloudkitty.toml
# In the copy: add the [plugins.demo] block pointing at the shipped example
# script (see docs/plugins.md), set one kitty's behavior = "demo",
# and point [persistence] at a scratch snapshot path.
cargo run --release -p cloudkitty-server -- --config /tmp/016-smoke/cloudkitty.toml --fresh
```

Expected: startup log registers the plugin; the demo kitty visibly follows
the script's proposals in the viewer; `Ctrl-C` shuts down cleanly. Then:
break the script's output on purpose (make it print garbage) and watch the
kitty fall back — with `proposal rejected` warnings naming the parse error —
while the world sails on.

## 8. Startup validation (FR-011)

```bash
# Point [plugins.broken] at a nonexistent command in a scratch config:
cargo run -p cloudkitty-server -- --config /tmp/016-smoke/broken.toml
```

Expected: startup fails with a clear error naming the missing command; no
world is created, no tick runs.

## Constitution amendment check (FR-017)

`.specify/memory/constitution.md` shows Article IV at v1.2.0 with the
two-outcomes wording (research.md R10), and this spec + the rejection suite
land in the same change. `git log` for the change shows all three together.
