# Binding rebuild under the pin — continuity verified (2026-08-23)

Product flagged a gap in this harness after landing the toolchain pin
(#305, main 9f40c47): `cert_harness6.provenance` stamps `rustc -V` from
the PATH compiler at run time, which is not necessarily the compiler that
built the extension it imports. A binding built before a toolchain roll
keeps running afterwards, and the stamp would name a compiler that never
touched it. Their recommendation was one `maturin develop --release` so
the two converge.

Doing it turned up something larger, and one correction to the framing.

## The stale binding could already refuse a valid config

The venv extension dated 2026-08-21 18:44 local. Engine source moved twice
after that (`1253f49`, `bdfc574`), and the whole of that drift is spec
040's `[watchdog]` ForeignTable acceptance in `config/mod.rs` —
`skip_serializing`, discarded on parse, no simulation code.

Parse-only is not the same as harmless. `deny_unknown_fields` means the
pre-040 binding **rejects any config carrying a `[watchdog]` table**, and
the repo's root `cloudkitty.toml` has carried one since 040 landed:

```
ValueError: rl config error: TOML parse error at line 449, column 2
  unknown field `watchdog`, expected one of `world`, `persistence`, ...
```

Nothing had failed yet only because every config under
`exp-006-character-gen/configs/` predates 040 and has no such table. The
first lab run pointed at the served config would have hit it.

## A rebuild is not compiler-only, so it was verified as a change

Product's framing — rebuild so the stamp and the artifact converge — is
right about the compiler and incomplete about everything else: a rebuild
also imports whatever engine source has moved since. Here that was
parse-acceptance, which the diff shows and which cannot touch dynamics;
but "cannot" is an argument, and the house standard for an instrument
changing under a campaign is the 018–020 bit-identical practice.

`binding_continuity.py` (new) hashes the full global-state trace of a
fixed seating on a fixed seed, so it is sensitive to any dynamics change
anywhere in the engine rather than to a summary that might absorb one.

```
.venv/bin/python binding_continuity.py --out before.json
(cd crates/cloudkitty-py && maturin develop --release)
.venv/bin/python binding_continuity.py --out after.json --compare before.json
```

`c006a-L04s3`, seed 870,001, 2,000 ticks:

| | value |
|---|---|
| trace sha256, before | `57f70612…d43214` |
| trace sha256, after | `57f70612…d43214` |
| binding bytes changed | yes |
| verdict | **CONTINUOUS — new binding, identical dynamics** |

The check refuses to pass vacuously: if the binding bytes had not changed
it exits 2 ("did maturin actually run?"), because a matching digest across
an unchanged artifact proves nothing. The rebuilt binding loads the root
config.

Banked numbers therefore carry across the rebuild — exp-006, exp-006a and
the seating battery all stand.

## Stamp additions

`census_provenance.stamp` now records `toolchain_pin` (the channel from
`rust-toolchain.toml`), and the lab provenance adds `binding_artifacts` —
sha256 and mtime of the compiled `.so`. Three facts that can be compared
where there was one that had to be trusted:

- what the repo **requires** (`toolchain_pin`: 1.97.1),
- what the run **had on PATH** (`rustc`: 1.97.1, hash 8bab26f4f),
- what actually **ran** (`binding_artifacts` sha256).

The first two agreeing is the pin working. The third is the only one that
cannot drift from the run, and it is what would have caught this staleness
at the time instead of two days later.

## Not done

exp-005 keeps its own venv, deliberately pinned pre-wall. It is untouched
and must stay that way — a rebuild there would cross a schema boundary,
not a config-parse one.
