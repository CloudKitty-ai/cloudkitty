# Contract: Registry File & Served Behavior Description (spec 034)

Normative. A change to anything in this file is a spec amendment.

> **Amendment 2026-08-16 (owner, via Experiments):** the display line is
> the **architecture alone, general-audience wording** ("Transformer",
> "Multi-Layer Perceptron") — recipe stays provenance, never served.
> §2's table and the §1 example are the launch content, kept as the
> historical record; the row-immutability rule is precisely: sha key and
> architecture/recipe never change, and a display amendment on the
> owner's word is the one sanctioned row change. Everything else below
> stands.

## 1. Registry file

Location: `registry.toml` in the same directory as the artifacts it
describes — `policies/registry.toml` in this repository and on the box.

```toml
# policies/registry.toml — sha256-keyed model registry (spec 034).
# A row is born in the PR that lands its artifact and never changes:
# sha is identity, rows outlive renames and retirement.

[artifact."<64-hex sha256>"]
architecture = "<spelled out: Transformer, MLP, …>"
recipe = "<as certified: BC+PPO, …>"
display = "<served verbatim: Transformer · BC+PPO>"
```

- Strict parse: unknown fields refused; duplicate keys refused (TOML native);
  all three fields required and non-empty.
- The `display` value is authoritative as written — consumers never derive it
  from `architecture`/`recipe`.

## 2. Initial rows (ship content, shas per policies/README.md Active table)

| sha256 | architecture | recipe | display |
|--------|--------------|--------|---------|
| `21d197307a475b3ee8f71ffb98d5af275d8374283244314010a0741229b84277` | MLP | BC+PPO | MLP · BC+PPO |
| `d8e310215d7dd095e9d3f4a59d03d62e012bb677d4141cd2c45e3b5d86569c32` | Transformer | BC+PPO | Transformer · BC+PPO |
| `dfef0ec29161f93bded92c3a6e8b89cc1db92d9b3e478edd35a3d31e25941b46` | Transformer | BC+PPO | Transformer · BC+PPO |

## 3. Served field

`behavior_description` on every kitty object, on every surface that serves
kitty objects today (`GET /world`, `GET /kitties`, `GET /kitties/:id`, and
the WS world stream — identical payloads by existing doctrine):

| Seat | Wire value |
|------|-----------|
| `policy:<name>` | the registry row's `display`, verbatim |
| builtin (`needs_driven`, scripted builtins) | `"Scripted"` |
| plugin (`[plugins.*]`) | field absent |

- Additive only: no existing field changes name, type, value, or presence.
  `behavior` stays served verbatim (FR-009).
- Client contract: render `behavior_description` verbatim; when absent, fall
  back to the existing model-id rendering. (Client implementation is the
  Client thread's; this table is what they build against.)
- Not served on `GET /config` (the registry is not part of `Config`).

## 4. Startup refusal (FR-007)

Seating `policy:<name>` whose artifact resolves to a sha with no registry
row — or whose directory has no `registry.toml` — fails startup with an
error that names, at minimum: the config field (`[rl.policy.<name>]`), the
artifact path, and the sha256. No warn mode, no opt-out (owner ruling
2026-08-15).

## 5. Repo integrity gate (FR-008)

A repository test asserts, independent of any seating: `policies/registry.toml`
parses strictly; every `.ckpolicy` at `policies/` top level has a row keyed
by the file's actual sha256 (failure names file + sha). The row→file
direction is unchecked by design (rows are history).
