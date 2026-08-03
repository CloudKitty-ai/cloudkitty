# Class-conditioned credit on the exp-002 family base (post-024)

**Date**: 2026-08-02 · **Engine**: main @ `6d955ab` · **World**: the
frozen family base (`family/base.toml` — served shape + Clementine,
policy seats neutralized) · **Recipe**: 1,000 samples per class, 150
worlds (seeds 11001–11150), 1,200-tick traces, probe-seed 42,
cluster-robust per F-004 (+150-world addendum). Refreshes the dead
pre-024 prior (addendum §1: play/chase 3.6×) as prereg §6 requires.

| Substituted class | dr sig ticks (fp≈60) | S(.998) | vs all | mass ≤400 | peak |
|---|---|---|---|---|---|
| all actions | 83 | 0.0387 | 1× | 0.09 | 0.0029 @ k=948 |
| groom/sleep/rest | 35 | 0.0334 | 0.9× | 0.87 | @ k=0 (early) |
| eat/drink | 52 | 0.0333 | 0.9× | 0.37 | 0.009 @ k=0 |
| play/chase | **8** | **0.0039** | **0.1×** | 0.18 | — (sub-floor) |

## Findings

1. **The play/chase prior inverted.** Pre-024 it was the strongest
   cooperative lever (3.6×); on the post-024 family base it is the
   weakest (0.1×, deep sub-floor). Mechanism consistent with the 024
   batch: the chase sidestep removed chase-stall contention, and the
   roomy served-shape elements make play largely consequence-free.
   §10.1's diagnostics should watch **eat/drink and groom/sleep/rest
   contention**, not play/chase journeys, for first signs of learned
   cooperation.
2. **The 5-kitty base carries its credit late**: all-action bands at
   452–591, 646–653, 933–965 — only 9% of significant mass ≤ k=400,
   peak k=948. This matches F-014's roster-5 result (adding a cat
   spreads consequences later) and contrasts with the roster-4 served
   world's k≈230–330 band (three 150-world replications).
3. **Consequence — the prereg §3 dormant-γ trigger FIRES**: the
   registered rule ("0.9985 enters if the frozen family's measured dr
   band peak lands past k ≈ 500") is met on the base. Per the
   clause's own semantics this activates a **follow-up cell** (γ =
   0.9985 at the 33% mix, 3 seeds, after the main grid) — not a
   change to the 18-run grid, whose γ pair keeps its registered
   anchors. The roster-4 members of the family still put their band
   inside 0.998's horizon; the follow-up cell tests whether the
   5-kitty tail is worth reaching.

## Reproduce

```
./experiments/tools/twin-probe/target/release/twin-probe \
  --config experiments/exp-002-mixed-population/family/base.toml \
  --samples 1000 --trace-len 1200 --seeds 11001..11150 \
  --probe-seed 42 --quiet [--only-action groom,sleep,rest | eat,drink | play,chase] \
  --out experiments/exp-001-bc-mappo/raw/twin-probe-fambase-<class>-w11001.jsonl
# analysis: search.py channel_metrics, GAMMAS (0.995, 0.998, 0.9985, 1.0)
```
