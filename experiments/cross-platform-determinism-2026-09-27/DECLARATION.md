# Cross-platform determinism check — declaration

Declared and run 2026-09-27 on the owner's word ("running there
should be non-disruptive"; the server tested to ~10k req/s with
headroom). Measurement read, no gates: it converts the archive
ruling's two-tier reproducibility label (platform addendum, ruled
"Yes" 2026-09-27) from reasoning into measurement, per the standing
weigh-it-don't-reason-about-it rule.

## Question

Across the lab Mac (arm64, Accelerate) and the serving box (x86_64,
2 cores): (1) is the Rust engine's trajectory bitwise portable, (2)
how far do policy logits drift and how often does an argmax flip,
(3) where do greedy trajectories first fork and do 5-seed aggregate
means stay within the seed band. Layers isolate engine, torch/BLAS,
and end-to-end.

## Method

`determinism_check.py run` on each machine (same repo commit; the
engine crates are code-identical between the local binding's
befe5f0 and HEAD — only license metadata moved); checkpoint = the
gen1-A Miso mind (cand-s2) piloting all seats; fixture = 1,000
recorded observation rows (shipped, sha-checked before comparison);
torch single-threaded on both. Server side runs in a throwaway
clone under /root/detcheck with its own venv (torch 2.13.0 / numpy
2.5.2 pinned to the lab's), never touching the deploy checkout or
the running service; everything niced. Expectations (reasoning, to
be replaced by the measurement): layer 1 bitwise-equal trajectory
with any drift confined to libm-backed values; layer 2 ulp-scale
logit drift with high but imperfect argmax agreement; layer 3
trajectories fork at the first flip while 5-seed means stay in
band. Python differs (3.14 lab / 3.12 server) — the comparison is
tuple-vs-tuple, exactly what the two-tier label claims about.

## Welfare practice

Eval-only, greedy, package world, baseline-scale exposure (5 × 5k
ticks per machine, the calibration probe's footprint); no covered
mind trains; fences untouched. Seeds 900401–900405 (this band is
claimed by the enrichment screens' guard probes; reused here as a
read-only eval band, disjoint from anything trained).
