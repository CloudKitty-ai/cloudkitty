# Expansion acceptance — spec 035 candidates (2026-08-17)

Experiments' acceptance of the three surface-expanded candidates
produced by `ckpolicy-expand` (spec 035, PR #240, main @ a8969dd),
per prereg §5 (behavioral half of the settled Q2 division) and D-001
(per-artifact residual). Instrument:
`expansion_acceptance.py`; raw numbers in
`results-raw/expansion-acceptance.json`.

Regeneration (deterministic, run locally):

    cargo run --release -p cloudkitty-rl --bin ckpolicy-expand -- \
        policies/<name>.ckpolicy <out>/<name>-o4.ckpolicy

## 1. Determinism: local shas vs pinned constants

All three locally regenerated outputs match the constants pinned in
`crates/cloudkitty-rl/tests/expansion.rs` (which CI re-derives from
the committed sources every run). Cross-machine determinism is
confirmed mechanically, not assumed.

| candidate | sha256 | match |
|---|---|---|
| attn-a1-s1-o4 | 61d6d7cc699f1de303b4fb661a77380bf56b5d69e76db3eac5bd316b38ed604a | yes |
| attn-a1-s3-o4 | d6f60818ad0516445367a3cdbca2a7df24a36886ed457e3ee1c8fe06004569ad | yes |
| e004-a1-s2-o4 | b6293849a63bd2f8b915080e74a20a5dd5f539eb48911bece3d4e23876588b09 | yes |

Tool-attested placement (Product's half, CI-proven per run): attn
family mapped 77083 / zeroed 448 / floored 903; e004 mapped 127531 /
zeroed 7168 (256 x 28 new input columns) / floored 1799. Verified
PASS on the local regeneration runs as well.

## 2. Behavioral parity on old dims (prereg §5 gate)

10,000 obs rows sampled from the archived pre-wall dataset
(exp-004 `raw/bc-v4`, first 8 rollout dirs x first 2000 rows, pick
seed 20260818), embedded into the 225 surface with new-kind dims
zero. Source forwarded through the certified schema-3 harness
(`numpy_forward_v3`), expanded through the schema-4 harness
(`numpy_forward_v4`); e004 through a float64 MLP forward on both
layouts. All forwards in float64 so the number measures weight
placement, not BLAS blocking.

| candidate | max abs dlogit (34 act + 9 legacy msg) | greedy agree | new msg heads |
|---|---|---|---|
| attn-a1-s1-o4 | 0.0 (bit-exact) | 100.0000% | exactly -1e4 |
| attn-a1-s3-o4 | 0.0 (bit-exact) | 100.0000% | exactly -1e4 |
| e004-a1-s2-o4 | 0.0 (bit-exact) | 100.0000% | exactly -1e4 |

Gate (<= ~1e-5) passed with zero margin consumed. This licenses
§7's identification of "expanded artifact" with "the source,
embedded in the new surface": pre-expansion selves never run in the
battery.

## 3. Per-artifact U1 residual (D-001)

D-001 method on the real artifact bytes: dataset-v5 spread rows
(collection in flight; first 8 readable config dirs, 10k rows, pick
seed 20260818, injection pool seed 1), realistic audible legacy
tuple injected into the first new-kind slot, versus the same tuple
in a silent legacy slot (the mind's natural response to a known
meow). Flip = greedy activity decision changes.

| candidate | new-kind act-flip | legacy-ref act-flip | ratio |
|---|---|---|---|
| attn-a1-s1-o4 | 19.38% | 14.55% | 1.33x |
| attn-a1-s3-o4 | 15.64% | 11.36% | 1.38x |
| e004-a1-s2-o4 | 0.00% | 15.36% | 0.00x |

Reading:

- **e004-a1-s2-o4 is structurally deaf** to new kinds (asserted,
  not just observed): an MLP has no shared digest embedding, and its
  28 new input columns are provably zero. U1's residual is an
  attention-family property only. The legacy-ref column shows it
  hears known meows normally.
- The attn candidates hear an anonymous new word as roughly "a
  meow": 1.33x / 1.38x their natural response to a known kind,
  the same story as D-001's banked measurement.
- These numbers differ from D-001's banked 13.1% / 11.2% (1.17x)
  for attn-A1-s1. Two known sources: that run measured the torch
  checkpoint rather than the artifact bytes, and its v5 rows came
  from the first collection, which was later deleted for the
  config-index overwrite defect (different world sample). The
  ratio, which is what the 5/1k trigger reasoning leaned on, is
  consistent. The residual leg re-runs on the complete spread cell
  at acceptance QA; those are the final acceptance-record numbers.

**Final numbers landed** (collection complete, 10k rows spanning
all 108 spread dirs — `--full-cell`, raw in
`results-raw/expansion-acceptance-full.json`): attn-a1-s1-o4
19.61% / 14.10% (1.39x); attn-a1-s3-o4 17.85% / 12.16% (1.47x);
e004-a1-s2-o4 0.00% / 19.12% (structural deafness confirmed on the
full sample). See `dataset-v5-qa-2026-08-17.md` for the QA record
these join.

## 4. Standing

Battery unblocked: the -o4 candidates are §5 candidates like any
other (new shas, full battery). Registry obligation at seating time
stands: three rows keyed on the new shas, same PR as the artifacts,
display per the architecture-alone ruling, recipe
"<recipe>, expanded from <source sha> by ckpolicy-expand v1".
Sources retire to policies/retired/ with rows kept.

Local candidate copies live in `expanded-candidates/` (gitignored:
byte-identical regeneration is one command).
