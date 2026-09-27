# Evidence archive — the ruling (Experiments' side of the record)

Owner ruled 2026-09-27 in the Experiments session ("Agreed on all 4,
relay to harness"), on the four dimensions Harness relayed from the
public-release survey (Professor, Tier 1 finding 1). Harness owns the
tag-time checklist integration; this file records what binds the
raws and manifests, which are this thread's.

1. **Venue**: Zenodo is the archive of record (immutable, DOI-keyed,
   50 GB/record). Hugging Face at most a later mirror; no S3.
2. **Keying**: bundles keyed by the run-manifests' existing git_head
   + SHA-256s. A bundle is the CLOSURE OF THE ARC'S RESULTS
   REGENERATION READ FENCE — raws, checkpoints, configs, manifest —
   so "reproducible" means the accuracy gate passes against the
   archived bundle. The gate stamp's raw-dir hash is the bundle
   integrity check.
3. **Split**: per-finding minimal sets derived mechanically by
   tracing reader path constants; the register labels findings
   "reproducible (DOI)" or "recorded (local)". POISONED DIRS ARE
   NEVER ARCHIVED (currently the tier-5 stale pair,
   `beam-world-screen-2026-09-19/results-raw/tier5-stale-c6b8481/`
   and `…/artifacts/stale-c6b8481/`).
4. **Scope**: forward-only from the next tag; retroactive at
   citation (the F-050/F-054/F-055 lineage expected first). Every
   upload is publishing: it happens on the owner's word, batched
   for one approval at tag time.

**Platform addendum — RULED (owner, 2026-09-27: "Yes")**: a platform tuple in every run-manifest
(CPU arch, OS, python/torch/numpy/BLAS versions, thread count,
beside the existing rustc/binding identity), and a two-tier
reproducibility label per bundle — bitwise on the recorded tuple;
statistical elsewhere (printed-precision tables, 30-seed aggregates
in band), because floating-point reduction order across
architectures, BLAS implementations, and thread counts can flip a
greedy argmax and fork a trajectory while leaving every conclusion
intact. Old arcs get the tuple stamped at bundling time (one
machine throughout).
