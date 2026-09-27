# Seating analysis + heatmaps — design inputs (2026-09-28)

Owner-driven design record, same shape as
`gen3-free-time-inputs-2026-09-26.md`: her words verbatim, the
converged design, and what stays open. The instrument builds after
the stage-B readout; nothing here is a prereg or a bar.

## Her words (2026-09-28)

Origin: "I'm building a heatmap feature for Client, and rather than
try to calculate it dynamically, we should be able to pre-generate
it (yay determinism)." Then:

1. "We should calculate a heatmap with per-cat and all-cat numbers
   for each seating. There could be useful information about
   behavior changes, and if we use the same seed/world config, we
   can compare across seatings/generations."
2. "We can evaluate if the heatmaps evolves over time, or settles
   into a steady state (I suspect the latter, probably mostly
   stable around our water positions, which are static)"
3. "Formalizing a seating analysis each time we seat would be good.
   We did this for a little bit (e.g. the work we did for
   purrsonality.md), but haven't been consistent."

Her metric list: "What do they do? Who do they do it with? (Include
elements for play/sleep) / Needs: median, p95 / What do they say? /
Time grouped vs. solo. Distance: from any cat + from EACH individual
cat (median, p95 — if large variance then more)."

Rulings on the follow-ups: dynamic heatmap "not something I want to
prioritize at the moment if we can get a statistically accurate
distribution through headless simulation" (pre-generation only);
steady-state evaluation "let's test that when we implement heat
maps"; the extended metric set (below) "I like all of these, and
they're cheap to collect."

## The instrument (converged shape)

One standing declared instrument — a metric spec plus one reader and
one report template, versioned, run identically at every seating,
write-up accuracy-gated. Not a fresh prereg per seating: the metrics
are fixed in advance, which buys the forking-paths protection for
what is descriptive work. One seating run produces both the analysis
report and the Client heatmap artifact.

### Heatmaps

Per-tile occupancy per cat per tick, headless replay, emitted as
JSON for Client to render (Client thread wires the feature; this
thread owns generation). Per-cat and all-cat layers.

Comparison caveats, recorded at design time:
- Same seed/world config gives identical initial conditions and
  world RNG, not identical trajectories — different minds act
  differently and the world evolves under those actions. The
  divergence IS the behavior difference, but it is whole-trajectory,
  not tick-pairable. Static anchors (water, the sleep floor) stay
  comparable; beam-chase regions vary with each seating's own draw.
- Cross-generation comparisons cross world configs (floor 0 → 15,
  beam count/ttl moved), and the standing caveat holds: same-world
  comparators only. The comparison grid is seatings × seeds WITHIN a
  world config; across generations, shapes compare qualitatively,
  never cells.
- Any "matches the server" claim inherits the determinism result's
  scope discipline (`cross-platform-determinism-2026-09-27/`):
  measured at these seeds, an inference elsewhere. For pre-generation
  this mostly does not bind — generate once, ship the artifact.

Steady-state test (rides the implementation, her word): windowed
heatmaps (~2,000-tick windows) with a distance between successive
windows (Jensen–Shannon or L1 on normalized occupancy). A converging
distance locates the mixing time — how long a heatmap must run
before it is representative — which then sets the pre-generation
horizon.

### Metrics (her four, then the extension set — all approved)

1. **Actions and partners**: what each cat does and with whom,
   partners including world elements for play/sleep (`activity.target`,
   never `last_action.with`; snapshots are post-apply, scene-start
   reads at t−1).
2. **Needs**: per-cat median and p95, plus (extension) streak
   distributions (max time below threshold), tending cadence
   (inter-eat/drink intervals), and margin kept (worst-need
   distribution).
3. **Speech**: per-cat emission distributions and echo structure
   from the free-register reads. Descriptive only: F-048's
   row-vs-word attribution is OPEN, so no causal claims about what a
   word controls.
4. **Grouped vs. solo, distances**: span instrument for grouped
   time; pairwise distances Manhattan (`walk_distance`), median/p95
   from any cat and per pair, with the full distribution attached
   when variance is large (her rule).
5. **Social structure**: interaction-graph reciprocity, partner
   concentration, per-pair initiation vs. receipt; refusal rates per
   pair from the refusal instrument.
6. **Distress response**: latency from a teammate crossing a need
   threshold to a helper's approach, and the responder matrix
   (extends the teammate-distressed start share).
7. **Behavioral entropy**: per-cat action-distribution entropy
   (specialist vs. generalist) and transition entropy
   (predictability).
8. **Routine**: autocorrelation of location and action streams —
   cycles, their period and phase per cat.
9. **Territory**: pairwise heatmap overlap (Jaccard or JS) and
   home-range size (area holding 90% of occupancy).
10. **Path efficiency**: Manhattan travel per tick; directness to
    water when the relevant need is high.
11. **Welfare shape**: per-cat happiness p5 and the worst-cat gap
    (max−min), beside the team mean — equity, not just level.

### Methodology

- **Multi-seed per seating** (~5 seeds), per-metric spread reported —
  separates a seating's character from the draw.
- **Fixed-scenario probes**: a small set of scripted openings (e.g.
  one cat distressed at t0) replayed identically at every seating.
  Standardized situations survive generation changes better than
  free-running stats; natural home for Gen 2's hidden-needs
  questions later. Probe scenarios get declared in the instrument
  spec before first use.

## Doctrine check (rule 8 of CLAUDE.md; DESIGN-DOCTRINE.md)

- **Rule 10 (bars vs readings)**: everything here is a READING. No
  metric becomes a bar by accumulation; a bar needs her declared
  word per seating. This moved the doc's framing: the template
  reports, it never gates.
- **Rule 9 (census rule)**: choice-share readings on a fresh seating
  carry re-verify triggers, never conclusions; the analysis runs
  post-transient (needs oscillating around a stable mean). This
  moved the run-window definition.
- **Rule 6**: speech metrics observe; no scripted decision or filter
  keys on a free word's kind. Checked; moved nothing (the instrument
  only reads).
- **Rules 1–5, 7**: checked; moved nothing — the instrument prices,
  scripts, and rewards nothing. The probe openings are lab scenarios
  (rule 6's lab-emitter carve-out shape: nothing learns from them).

## Open

- Build order: after the stage-B readout (RESULTS-B first).
- The §Design discipline rule line ("every seating gets the standing
  analysis") lands in `experiments/README.md` on her word once the
  template has run once.
- Probe scenario set: proposed with the instrument spec, declared
  before first use.
- Client-side rendering: Client thread's, relayed when the JSON
  artifact shape exists.
