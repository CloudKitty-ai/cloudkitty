# policies/ — deployed policy artifacts

The durable home for every `.ckpolicy` the served world references
(owner decision, 2026-07-31): committed so a fresh clone serves the
roster as-is, named here so certification stays auditable. The name
matches the `policies/` examples in `docs/rl-training.md`; the root
`artifacts/` name was rejected because it collides with the gitignored
`experiments/**/artifacts/` vocabulary.

## Rules

- **Byte-identical, never re-exported.** A file lands here as an exact
  copy of the bytes that passed certification; the sha256 below must
  match the certification record and what the server logs at startup
  (spec 014 FR-016: artifacts are schema-validated and content-hashed,
  never served on `GET /config`).
- Every file gets a row here: filename → sha256 → provenance →
  certification record. A file without a row (or a row whose hash no
  longer matches) is a deployment error.
- Retired artifacts are deleted, not overwritten — history keeps the
  bytes; this directory holds only what the served config may name.

## Artifacts

| File | sha256 | Provenance | Certification |
|------|--------|------------|---------------|
| `s6.ckpolicy` | `8030b94d8cbf670a46435b38a817035e864d4923203ffa71e52e761099eeeb5f` | exp-001 arm2, γ = 0.998, seed 6 (BC → MAPPO); drives Miso (`policy:s6`), greedy selection | `experiments/exp-001-bc-mappo/results/recert-2026-07-31.md` (certify clean, new engine + 24×24, +0.0448 AllSubject); lineage: `served-world-remeasure-2026-07-30.md`, `s6-promotion-2026-07-30.md`, `soak-record-2026-07-31.md` (§9.1 PASS) |
| `s3.ckpolicy` | `bbaf5f8bbfc312447046aae326eaff23cee9454a6d143cb472adbade9187aad2` | exp-001 arm2, γ = 0.998, seed 3 (BC → MAPPO); drives Kittybear (`policy:s3`), greedy selection | `experiments/exp-001-bc-mappo/results/recert-2026-07-31.md` (certify clean, new engine + 24×24, +0.0427 AllSubject); `pair-screen-2026-07-31.md` (seating screen, Seating B per the pre-registered rule) |
