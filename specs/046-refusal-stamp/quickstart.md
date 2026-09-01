# Quickstart: validating the refusal stamp (spec 046)

Prerequisites: the 046 branch built (`cargo build --workspace`), tests
green (`cargo test --workspace`), clippy via CI's exact invocation
(`cargo clippy --workspace --all-targets -- -D warnings`).

## 1. Unit/integration proof (the suite)

```sh
cargo test --workspace
```

Covers: emit-proof at ring + serialized layers (FR-008), the
non-refusal carve-outs (chosen Idle, legal-proposal duration override),
turn-order within a tick, driver parity (behavior loop vs seam),
capacity trim + retention-0 rejection, pre-046 save resume with
capacity re-stamp, stamp guard (`refusal_retention` absent from default
serialization), evolution golden untouched.

## 2. Live emit-proof (bounded boot; macOS has no `timeout`)

```sh
perl -e 'alarm 12; exec @ARGV' target/debug/cloudkitty-server --config <lab-config> &
sleep 6
curl -s localhost:PORT/events/refusal | python3 -m json.tool | head
```

Expected: a JSON array; on any config with co-located kitties it
populates within a few hundred ticks (mask-vs-moved-world refusals are
routine). Each entry shows `kitty_id`, the verbatim `proposed` action
(target included when named), `tick`; ticks non-decreasing.

## 3. Byte-identical dynamics check (SC-003)

Seeded twin runs, pre-branch build vs 046 build, same config + seed:
diff the kitty traces (needs/positions/actions/messages). Expected:
identical. The evolution golden test is the in-suite version of this —
it must pass **unregenerated**.

## 4. Additivity checks (SC-004 / FR-006)

- Parse the deployed serving config with the 046 binary: loads
  unchanged; `engine_defaults_sha256` equals the pre-046 stamp.
- Load a pre-046 world save (no `refusal_log` key): resumes; first
  `/events/refusal` read returns `[]`; after refusals accrue past 1,
  the ring holds more than one event (proves the capacity re-stamp —
  without it the ring would be stuck at one).

## 5. Sizing spot-check (SC-005)

On a lab run at roster density, confirm ring length grows toward and
caps at 4,000, and that two polls 10,000 ticks apart overlap (no
rollover gap) at ~0.23 refusals/tick.
