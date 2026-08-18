# Contract: `ckpolicy-expand` (spec 035)

Normative. A change to anything here is a spec amendment.

## 1. Invocation

```sh
cargo run -p cloudkitty-rl --bin ckpolicy-expand -- <source.ckpolicy> <output.ckpolicy>
```

- `<source>`: a pre-wall artifact of either committed family (v2 MLP /
  v3 entity-attention). The tool reads it through a tooling-only entry;
  the serving loader's refusal of old generations is untouched.
- `<output>`: written only if every check passes; the conventional name is
  `<source-stem>-o4.ckpolicy`, and the tool warns (does not fail) on a
  nonconforming name.

## 2. Refusals (nonzero exit, message names path + reason)

- Source already at the current pins ("nothing to expand" — a no-op export
  would mint a second sha for the same mind).
- Unknown artifact version, or schema pins AHEAD of the compiled surface.
- Corrupted source (magic/header/size failures — loader doctrine).
- Any structural attestation failure (§4).

## 3. The two invariants (constants)

- `NEW_HEAD_FLOOR = -1.0e4_f32`: every new message-kind head output has
  weights 0.0 and bias −1.0e4 — the logit is constantly −1.0e4 (argmax
  never selects it; softmax probability underflows to exactly 0).
- New input-side parameters (new-kind type rows / digest columns per
  family): exactly 0.0.

## 4. Attestation (printed report; tests reach it as a struct)

source {path, sha256, family, pins} · target pins · output {path, sha256}
· tool version · counts {mapped, zeroed, floored} · verdict. The counts
partition the output parameter space exactly: mapped == total source
parameters (bijective), mapped + zeroed + floored == total output
parameters. Determinism contract: identical inputs + tool version →
identical output bytes (same sha), any machine.

## 5. Naming & provenance (lands with the seating PR, not this arc)

- Filename: `<source-name>-o4.ckpolicy` (o4 = observation-schema-4
  surface token); convention recorded in policies/README Naming.
- Registry row (spec 034 machinery, same-PR law): display unchanged per
  the owner's architecture-alone ruling; recipe =
  `"<source recipe>, expanded from <source sha256> by ckpolicy-expand v1"`.
- Retirement at cutover: sources → `policies/retired/` with rows kept;
  Superseded-by = artifact lineage (not seat inheritance).

## 6. The proof division (settled Q2 — binding)

The tool proves PLACEMENT (this contract, §4). Experiments' independent
harness proves SEMANTICS (behavioral parity on old dims — exp-006 prereg
§5). Neither side may assume the other's proof; in-repo, the SC-003
engine-level deaf/mute test is the behavioral net.
