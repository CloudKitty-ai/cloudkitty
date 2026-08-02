# Post-024 twin-probe re-verification: the credit landscape rewired

**Date**: 2026-08-02 · **Engine**: main @ `6d955ab` (the 024 wet-fur
batch — the fired F-003/F-005/F-006 "engine-defaults change" triggers)
· **Statistics**: cluster-robust per F-004 throughout
(`search.py channel_metrics`, GAMMAS widened; `analyze.py` not used)

Six probe runs, all 1,000 samples × 1,200-tick traces, probe-seed 42:

| Run | Config | Worlds | Purpose |
|---|---|---|---|
| A | `training.toml` | 101–120 (20) | F-003 exact recipe, comparability |
| B | `training.toml` | 5001–5150 (150) | F-004-clean, fresh batch |
| C | `training.toml` | 3001–3150 (150) | **paired** vs addendum §1 anchor |
| D | `cloudkitty.toml` (24×24 served) | 4001–4150 (150) | F-006 recipe on current config |
| E | served patched 32×32 | 4001–4150 (150) | geometry deconfound (F-009: two things changed since F-006) |
| F | `cloudkitty.toml` | 6001–6150 (150) | F-004 replication of D |

## 1. The frozen gym lost its signal (paired seeds, engine-only change)

Run C vs the addendum §1 all-action anchor (same seeds 3001–3150, same
recipe, same statistics — only the engine moved):

| | pre-024 | post-024 |
|---|---|---|
| dr significant ticks (fp ≈ 60) | 68 | **36 (sub-floor)** |
| S(.998) absolute | 0.026 | **0.011** |
| surviving dr bands | mid-horizon + queueing | k≈920–937 + scraps |

Run B (disjoint 150-world batch) agrees: 29 significant dr ticks,
band structure dissolved. **Mechanism consistent with the chase
sidestep**: F-005's replicated gain carried a queueing/turn-taking
signature (stall-fed, k≈730–940). Sidestep exists to dissolve stalls;
it appears to have dissolved the signal they carried. What survives on
the gym is a remnant of exactly that band (k≈930) — reachable only by
γ ≥ 0.9985 and small.

Run A (the 20-world F-003 recipe) shows *rich* mid bands (102–374,
peak k=343) that neither 150-world batch reproduces — the F-004
phantom pattern, textbook. Recipe-matched comparability with F-003 is
therefore limited to: the two-channel *structure* reproduces (early
self band 0–16 everywhere); the *quantities* do not survive clean
statistics on the new engine.

## 2. The served world now carries the strongest band we have measured

Run D — the current served `cloudkitty.toml` (24×24, 4 kitties, roomy
elements, 1× rates), where F-006 found statistical silence (13 dr
ticks) on the pre-024 32×32 shape:

| Channel | sig ticks (fp≈60) | main band | peak | S(.998) abs |
|---|---|---|---|---|
| team reward (dr) | **82** | **282–324 (43 contiguous)** | 0.0045 @ k=311 | **0.0885** |
| teammates (spillover) | 41 | 267–321 | 0.343 @ k=311 | 3.30 |

Run F replicates on fully disjoint worlds (**required by F-004 before
acting** — passed): 111 sig ticks, bands 229–260 + 265–279, peak
k=271, S(.998) = 0.109. Two disjoint 150-world batches, one coherent
story: **a cooperative band at k ≈ 230–330 now lives on the served
world**, with amplitude and discounted mass larger than the frozen
gym ever showed (3.4–4× the gym's pre-024 S(.998); ~8× its post-024).

## 3. Deconfound: geometry is the bigger lever, the engine contributes

F-006's measurement was 32×32; the served config went 24×24 in the #86
cutover — so D-vs-F-006 changed two things. Run E isolates them:

| World shape (post-024 engine) | dr sig | S(.998) | verdict |
|---|---|---|---|
| 32×32 (F-006's shape) | 57 | 0.036 | borderline, sub-floor |
| 24×24 (served today) | 82 / 111 | 0.089 / 0.109 | clear, replicated |

Pre-024 32×32 was silent (13); post-024 32×32 is borderline; post-024
24×24 sings. Both factors move the needle; **the 24×24 cutover is the
dominant one** — one more instance of the contention story that runs
through F-005/F-006 (smaller floor → more shared-resource collisions).
Plausible engine contribution: wet-fur turns water into a priced,
shared resource with scene-length consequences (the calibration probe's
groom-loop is exactly a new medium-horizon consequence chain).

## 4. Dense retention curves (the γ question this re-run was for)

S(γ)/S(1.0) over band ticks, cluster-robust:

| World | .99 | .9925 | .995 | .9965 | .998 | **.9985** | .999 |
|---|---|---|---|---|---|---|---|
| served 24×24 (run D) | 0.11 | 0.16 | 0.26 | 0.36 | 0.54 | 0.62 | 0.72 |
| frozen gym (run C) | — | — | 0.05 | 0.09 | 0.16 | **0.25** | 0.40 |

(Gym row ≈ from the k≈930 remnant; treated as descriptive.)

**Reading**: on the world that now carries the signal, the band
(k ≈ 230–330) sits comfortably inside γ=0.998's ~500-tick horizon —
0.9985 adds +0.08 retention, mostly from late scraps, and γ=0.995's
200-tick horizon ends *before the band begins* (0.26 retention, the
same mistake γ=0.99 was for the pre-024 gym). On the post-024 gym,
only γ ≥ 0.9985 reaches the surviving queueing remnant — but §1 says
the gym itself is the questionable choice now.

## 5. What this means for exp-002 (register inputs, owner decisions)

1. **The training-world question is reopened** — F-005's trigger
   ("re-run the search with fresh budget before choosing") has fired
   *and its answer inverted*: the scarcity×tempo gym lost its
   replicated advantage while the deployment-shaped served world
   became signal-bearing. Training on a family centered on the served
   world is now the evidence-backed default hypothesis; family-gen v3
   already centers 24×24 and spans 22–26. A slimmed post-024
   world-search (served-config-centered candidates) costs minutes on
   current hardware and would put the choice on measurement.
2. **γ sweep recommendation**: {0.995, 0.998} stands as the sweep;
   0.9985 is *not* needed for the served-world band (0.998 covers it)
   — carry 0.9985 only as a conditional arm if the chosen training
   world turns out to have late-band structure (decision rule: swap
   0.998 → 0.9985 iff the chosen world's dr band peak sits past
   k ≈ 500 under this instrument).
3. **Certification re-framing**: "certification is a welfare gate,
   not a cooperation instrument" (F-006 implication) no longer holds
   on the current served world — paired-Nash gains there can now
   partially reflect marginal cooperative credit. Eval design should
   note this, not lean on it.
4. Every pre-024 probe quantity is dead for design use (band edges,
   retentions, S values, class-conditioning ratios). The play/chase
   3.6× class prior (addendum §1) is unmeasured on the new engine —
   re-run `--only-action` on the chosen training world before citing.

## Reproduce

```
cargo build --release --manifest-path experiments/tools/twin-probe/Cargo.toml
# A: seeds 101-120; B: 5001-5150; C: 3001-3150 (config training.toml)
# D: 4001-4150; F: 6001-6150 (config cloudkitty.toml)
# E: family-gen --base cloudkitty.toml --set world.width=32 --set world.height=32
./experiments/tools/twin-probe/target/release/twin-probe \
  --config <cfg> --samples 1000 --trace-len 1200 \
  --seeds <batch> --probe-seed 42 --quiet --out <raw/....jsonl>
# analysis: search.py channel_metrics with GAMMAS widened
# (0.99, 0.9925, 0.995, 0.9965, 0.998, 0.9985, 0.999, 1.0)
```

Raw JSONL is gitignored (`raw/`); runs regenerate bit-identically on
main @ `6d955ab`. Wall-clock ≈ 40 s per 1,000-sample run (18-core).
