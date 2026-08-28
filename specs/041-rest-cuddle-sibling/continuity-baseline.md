# SC-001 continuity baseline (T003)

**Instrument**: `crates/cloudkitty-core/tests/evolution_golden.rs` —
the in-tree golden evolution harness (default config, default seed,
scripted behaviors, 10,000 ticks, sha256 of the serialized world).

**Baseline runs (2026-08-28, branch @ 2555205 = main, pre-041 code)**:
`golden_evolution_flag_absent_10k_ticks` GREEN ×3 against the pinned
digest

```
GOLDEN_DIGEST_MAIN_87236C5 =
3f89642eb3594a8a0444fc16ff5b7110f05bb55b3c27e65dcfee944ecaa5910c
```

**How each commit uses it**:

- **Commit 1 (split)**: the same pinned digest must stay GREEN ×3 —
  new dials at classic values + inert key must not move world
  evolution by one byte. A mismatch is a HALT: the split is not the
  no-op it claims to be.
- **Commit 2 (engine sibling)**: the digest is EXPECTED to move —
  rest legality changes scripted choices, and tier counters ride the
  serialized world. Per the harness's own doctrine ("an intentional
  wire change regenerates the golden in the same PR with the
  justification alongside"), the pinned digest is regenerated in
  commit 2 with justification, and FR-010's claim for commits 2–3 is
  determinism (same seed → same state, ×3 agreement on the NEW
  digest), not byte-identity to pre-041.
- **Commit 3 (reprice)**: the commit does not touch engine defaults
  (`Config::default()`), so the commit-2 digest must stay GREEN ×3 —
  a second, free continuity check that the reprice is config-only.
