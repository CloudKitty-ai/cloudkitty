# Quickstart: Validating the Say-Surface Finalization

Runnable checks that prove the wall's engine item end-to-end. Normative
numbers: [contracts/say-surface-v3.md](contracts/say-surface-v3.md).

## Prerequisites

- The 033 worktree, `cargo` on PATH.
- For step 4 only: the new oracle fixtures from Experiments (mid-arc
  handshake) already at `crates/cloudkitty-rl/tests/fixtures/`.

## 1. The whole suite (the wall must be green everywhere)

```sh
cargo test --workspace
```

Expected: all green, including the shipped-config gates (the shipped
`cloudkitty.toml` seats scripted behaviors during the wall window) and the
un-ignored parity gate.

## 2. The vocabulary and its law

```sh
cargo test -p cloudkitty-core meow
```

Expected: the tiered-legality tests pass — Here* legal exactly at their
referents (empty bowl ≠ food here; far critter ≠ critter here), free
register legal anywhere off cooldown, reserves never-legal under defaults,
Silent always legal, grounding property test clean over randomized worlds.

## 3. The derived numbers (the schema-4 pin)

```sh
cargo test -p cloudkitty-rl schema_four_pins
```

Expected: HEAD_KINDS 15 / head 16 / digest 60 / observation 225 / message
mask 16 / menu 34 / logits 50, asserted against the contract's literals;
mew at head 3 / digest column 2 with cooldown-only law (the rename pin);
encode/decode roundtrip unchanged over the 34 menu indices.

## 4. The generation gate and parity

```sh
cargo test -p cloudkitty-rl --test artifact_v3_parity
cargo test -p cloudkitty-rl --test artifact_v3_reject
```

Expected: the new oracle loads and passes at ≤ 1e-4 with exact argmax
(≥ 100 rows printed); every stale-pin rejection test names the pin and the
expected value.

## 5. Flags gate legality, never layout

```sh
cargo test -p cloudkitty-rl vocabulary_flags
```

Expected: two configs differing only in flags produce byte-identical
observation and mask shapes; the disabled kind never emits; a misspelled
`[meow.vocabulary]` key refuses boot naming the field.

## 6. Eyes-on (optional but satisfying)

```sh
cargo run -p cloudkitty-server -- -c cloudkitty.toml -s /tmp/wall-check.json
curl -s localhost:8090/config | python3 -c "import json,sys; print(json.load(sys.stdin)['meow']['vocabulary'])"
```

Expected: the server boots with scripted seats; the vocabulary table echoes
with trill/ekekek false. A scripted world will speak want-kinds and purrs as
before; Here*/chirp await minds that choose them (phase 1's job, not this
spec's).

## 7. The living documents

- `docs/encodings.md` exists; its schema-4 section matches step 3's numbers;
  its preamble states the FR-019 rule; spec 014's contract points here.
- `docs/meows.md` exists; sixteen entries (Silent + 15) plus the WaitForMe
  footnote; law cells match the contract; observed-meaning citations
  resolve; unwritten cells say "meaning awaits the cats."
