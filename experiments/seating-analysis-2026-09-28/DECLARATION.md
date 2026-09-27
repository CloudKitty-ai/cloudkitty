# Seating analysis v1 — instrument declaration

Declared before collection (owner kickoff 2026-09-28: "Can we run the
seating analysis on the current seating?"). Design record:
`experiments/seating-analysis-inputs-2026-09-28.md` (metric set
approved "I like all of these, and they're cheap to collect"). This
is a DESCRIPTIVE instrument: every output is a reading under
doctrine rule 10, never a bar; nothing here gates anything.

## The seating under analysis (verified off the running server)

gen1-A as served: the five `/root/cloudkitty/policies/fog-gen1-*.ckpolicy`
files hash byte-identical to the handoff table
(`fog-gen1-cert/seating-handoff-2026-09-16.md`), and the served
`cloudkitty.toml` differs from `fog-gen1-cert/anchor-b3.toml` only in
seat wiring (15 diffs, all `behavior`/`[rl.policy.*]` keys; zero
world-law keys). Lab replication: `cert_harness_fog.SEATINGS["gen1-A"]`
(the battery-measured torch actors; ≡ the served exports by the
handoff parity record, max logit delta 2.4e-05, exact argmax) on
`anchor-b3.toml`, clock in `train` mode — the served seam
(tick mod 2000)/2000 per the 2026-09-15 ruling, the certified
condition. Greedy on both heads under the engine mask.

## Collection

`seating_collect.py`: the cert-harness run_one loop (imported
read-only — stage B trains; no file on the do-not-edit list is
edited) recording per-tick streams instead of aggregate accounts:
positions, engine activity, chosen message head, needs (×6),
happiness, partner (present, index), distress flags, team nash
(state), and the element table (type-coded, for water tiles and
play/sleep element partners). One npz per seed under `results-raw/`.

- Seeds **900501–900505** × 20,000 ticks (5 legs), plus **900506**
  × 300 ticks as the guard fixture (tracked). Band claimed in
  `SEED-BANDS.md`.
- `--abort-streak 1000` semantics on every leg (the F-053 line): the
  leg stops the tick any distress streak reaches 1,000; an aborted
  or short leg is reported as such, never silently pooled.
- Runs nice'd, torch single-threaded, beside the stage-B driver.

## Metrics (fixed here; the reader implements exactly these)

Per cat and roster unless said otherwise. Welfare/needs metrics are
computed FULL-RUN (comparable to the battery convention); spatial
metrics are full-run with the windowed convergence curve alongside.

1. **Actions & partners**: activity share per engine activity;
   social-scene share per cat pair (undirected pair-tick counts and
   scene counts; a scene = a maximal run of partnered ticks for a
   pair). Element partners: playing within Manhattan 1 of a
   bug/greeble = element play; sleeping on a beam tile = beam sleep.
   Initiation/receipt attribution is OUT of v1 (needs the live event
   stream); recorded as deferred.
2. **Needs**: per-need median and p95; worst-gate-need
   (GATE_NEED_IDX × 100) median/p95; streak distribution of worst
   need ≥ 25 (count, median, max); tending cadence = inter-start
   intervals of Eat and of Drink (median, p95).
3. **Speech**: message-head distribution per cat (Silent + 15
   kinds); rate by own worst-need bin (<15, 15–25, ≥25).
   DESCRIPTIVE co-occurrence only — F-048 row-vs-word attribution
   is OPEN; no control claims.
4. **Grouped vs. solo & distances**: three declared levels —
   contact (nearest cat at Manhattan ≤ 1), company (nearest cat at
   Manhattan ≤ 4, the served vision radius), engine-partnered.
   Distances Manhattan (`walk_distance`): nearest-cat and per-pair
   median/p95, full histogram attached when p95 − median > 4 tiles
   (her "if large variance then more").
5. **Social structure**: pair-tick matrix, partner concentration
   (share of each cat's social ticks with its top partner),
   reciprocity = min/max of the pair's two directed shares of each
   member's social time.
6. **Distress response**: for each distress onset (any flag 0→1),
   latency to first CONTACT (another cat at Manhattan ≤ 1) and
   which cat arrived; censored at flag clear or run end.
7. **Behavioral entropy**: Shannon entropy of the activity
   distribution, and first-order transition entropy of the activity
   stream (bits).
8. **Routine**: autocorrelation of the sleep indicator at lags
   1–4,000; dominant lag = argmax beyond lag 50, reported with its
   correlation.
9. **Territory**: per-cat tile-occupancy heatmap; pairwise
   Jensen–Shannon divergence between normalized per-cat heatmaps;
   home range = fewest tiles holding 90% of occupancy.
10. **Path efficiency**: per-tick displacement distribution; water
    directness = mean per-tick change in Manhattan distance to the
    nearest water element over ticks where drink need ≥ 25 and the
    cat is not Drinking (negative = approaching).
11. **Welfare shape**: per-cat happiness mean, p5; per-tick
    worst-cat gap (max − min happiness) mean/p95; team nash (state)
    mean.

**Heatmap artifact**: per-cat + all-cat counts as JSON
(`heatmap-gen1-A.json`, tracked) for Client. **Steady-state read**
(her item 2): 2,000-tick windowed all-cat heatmaps, JS divergence
between successive windows per seed — the convergence curve locates
the mixing time and sets the pre-generation horizon.

## Comparability rules (from the inputs doc, binding on the write-up)

Same seed/world = same initial conditions, not tick-pairable
trajectories; same-world comparators only across seatings; any
"matches the server" claim carries the determinism result's scope
(measured at its seeds, an inference elsewhere). Water positions are
per-seed (water is a spawned element, min 7 max 9, no ttl — static
within a world instance, not across seeds).

## Welfare practice (five parts)

1. **Stops**: fixed 20,000-tick legs; the 1,000-tick streak abort on
   every leg. Asymmetric: aborts cut suffering short, nothing stops
   early on success.
2. **Scout**: not a new world config — the served config itself,
   under the roster certified on it; standing battery numbers are
   the scout.
3. **Welfare cost**: expected exposure at the certified level (the
   battery ran this composition 120 runs × 4 bands at 0 catastrophe
   gates; soak confirmed on the served world). What the run buys:
   the standing per-seating behavioral baseline the owner asked for,
   the Client heatmap artifact, and the mixing-time read.
4. **Measurement aborts**: the streak abort above.
5. **Fences**: untouched (served config only; HARM-RULE FENCE not in
   play — no legs on size28/40/100).
