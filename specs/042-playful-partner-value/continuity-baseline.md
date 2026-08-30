# Continuity baselines (T002) — BOTH must be unchanged at feature end

Recorded 2026-08-29 at branch base (main b48c264 lineage), pre-042 code.

- `engine_defaults_sha256`:
  `6c73f89443671d5acc06a1e029c28c94856e3404396c231ee559026c98f07687`
  (contract §2: skip-at-identity serialization must keep this IDENTICAL —
  a moved stamp means a missing skip guard, HALT and fix.)
- `golden_evolution_flag_absent_10k_ticks`: GREEN against pin
  `7b361b2a5582d33efd96d8d64ef5be73d890c76e9d9751e57453e37f44ec17ad`
  (must-GREEN through the whole feature — byte-identical launch; a red
  golden is a HALT, never a regenerate.)
