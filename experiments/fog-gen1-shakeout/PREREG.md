# Fog Gen 1 step-5 shakeout — prereg DRAFT (2026-09-03, not declared)

Status: draft, being hashed out with the owner. Knob and field names
marked `<049:…>` are spec 049's to pin; the width, the radius default,
and the acceptance-bar numbers are filled in when the 049 branch lands.
Declaration = a later commit that removes this header. Timeline
authority: `experiments/fog-gen1-timeline-2026-08-26.md` step 5 (HALT /
INVESTIGATE tables, BC recipe, the training-pass slate).

## Purpose

Owner, 2026-09-03: find anything that needs a further major change,
schema-breaking above all, before the step-6 LOCK. A welfare cap under
fog is a by-product, not the goal. Two consequences for the design:

- Defects are looked for at the **first probe**, not at the end of the
  pass. A dead observation column found in hour one saves the pass.
- Every pre-declared finding maps to a **named step-6 decision** with
  its schema consequence (break / knob / instrument) written down now,
  so the pass ends in a list of decisions rather than a list of
  surprises.

## Part A — schema-defect checklist (read at probe 1, then every probe; rows ruled 2026-09-03)

Runs against the first `--probe-every` checkpoint of every arm and the
scripted anchor on the same config. Every row is a test with a
predicted healthy reading and a named degenerate signature; the
instrument is `schema_check.py` (to write; guard = plain-python asserts
on recorded probe traces, each row driven red by the exact defect it
names, rule 5). Width and offsets come from spec 049's FR-026 layout
(pinned 404: self 85 | 4 × 62 | elements 70 | clock 1).

| # | block | check | healthy reading | degenerate signature → suspect |
|---|---|---|---|---|
| A1 | every column | variance over the probe window | > 0 for every column that can vary on this config | a constant column that should move → wiring; a constant column that cannot move on this config is listed as such at declaration, never discovered |
| A2 | self: element-memory token (20) | per kind: memory set only after a sighting; cleared on a refuted arrival; never set for a kind not yet seen | set-events == first-sight events; refutations > 0 in the fog arms, == 0 in the no-fog control | memory set without sight → leak; never cleared → refutation path dead; token identical across kinds → slot indexing |
| A3 | kitty rows: fog mask | row fields masked exactly when Euclidean distance > `<049:vision_radius>` | mask flips agree with the geometry on every sampled tick; no-fog control never masks | mask disagrees with geometry → visibility predicate; mask never flips at the pinned radius → radius not applied |
| A4 | kitty rows: heard-unseen position | a masked row whose speaker meowed inside the window carries `pos` from that meow, static until the next audible meow | position changes only on meow ticks; equals the speaker's true position at that tick | position tracks the live cat → Q1 re-rule not implemented (leak); position never set → `pos` plumbing dead |
| A5 | kitty rows: digest (30) | recency + rate per (speaker × kind) populated for masked AND visible speakers | heard-unseen rows have non-zero recency; rates within the scripted emission rates measured in the floor screen | zero digest on masked rows → audibility gated on visibility (wrong); rates > emission → double counting |
| A6 | kitty rows: want intensity (6) | equals the caller's stamped `need/100` at its last want of that kind | matches the trace stamp on every want tick; 0 for kinds never called | constant 0 → not observed; drifts between wants → live need leaking |
| A7 | kitty rows: answers-me (4) | 1 only when the observer emitted the matching want inside the window before the here | count == engine-stamped `reply` events addressed to the observer, per F-029 emit-proof | never 1 in any arm → derivation dead; 1 without a prior own want → window logic |
| A8 | `reply` stamp (engine) | `reply = 1` iff a matching want is audible AND the referent is visible from the speaker | rule holds on every here in the trace; reply count > 0 in fog arms with the scripted reply path on | replies on ticks with no audible want → stamp rule; zero replies with wants and visible referents present → stamp dead |
| A9 | want law | a want is emitted only when armed, top need, and nothing visible or remembered for it | zero violations on the scripted anchor trace (the law is engine-side: policies cannot violate it either) | any violation → `message_legal` under fog |
| A10 | FR-023 explore | a scripted cat with nothing visible or remembered walks a persistent heading; re-draws only with the wall inside the radius | heading changes / blind ticks small and concentrated near edges; first-sight latency from blind consistent with the r-sweep arithmetic | re-draw every tick → heading not persisted; cats pin to a corner → re-draw filter |
| A11 | scene age + water bit | scene age climbs 1/tick inside a scene and resets on exit; water bit == on-water tile | exact agreement with the trace | either drifts → snapshot bump |
| A12 | elements block (70) | only visible elements populated; remembered elements appear in the memory token, not here | element rows zero when no element is inside the radius | remembered bowl appears in the element block → memory leaking into sight |
| A13 | emit-proof (F-029) | every category the instruments read has been EMITTED at least once in the window before "zero" is reported | a table of first-emission ticks per category | any category never emitted is "unproven", never "zero" |
| A14 | legality mask (activity + message) | no legality bit depends on a masked fact: the mask is recomputable from the observer's visible rows + own memory alone (adjacency incl. diagonal, distance 1.41, sits inside every radius ≥ 2, so the current law passes; the ruled want / reply law reads only the speaker's knowledge) | recomputing the mask from the observation reproduces the engine mask on every sampled tick | a bit that differs → a 049 rule reads true state through fog |
| A15 | kitty rows: by-id permanent rows (`kitty_slots` = roster−1 = 4) | row identity fixed per observer across ticks; a masked row still exists with masked FIELDS, never dropped or shifted | the (observer, row) → kitty-id map is constant over the probe | rows re-order or compact when a cat leaves view → every downstream column mislabelled |
| A16 | kitty rows: `reply` bit (observed) | the observing cat's row carries the engine `reply` stamp on the same here, per speaker | observed reply column == A8's stamp on every here in the trace | engine stamps, observation stays zero → the ladder tie-breaker is invisible to learners |
| A17 | anchor / policy observation parity | the scripted anchor and the PPO arms observe the identical vector on the identical config (same fog, radius, memory) | per-block variance (A1) and mask flip rate agree between the anchor trace and a policy trace at matched ticks | disagreement → the arms train on a world the anchor did not see (the exam-vs-gym skew class) |
| A18 | probe determinism | same snapshot + same radius → byte-identical observation (house bit-identical methodology) | two encodes of every probe snapshot agree byte for byte | any difference → nothing in A1–A17 is interpretable across probes |

Rows A14–A18 added on the (3) walk (owner ruled all five 2026-09-03).
Not added: contagion (shelved for Gen 1), scene-age float (A11), the
width 404 itself (a schema-header pin, `attn.rs:322`, not a probe read).

Reading rule: any red on A2–A9, A12, A14, A15, or A16 at probe 1 is a
**stop the pass** event (it is the defect the pass exists to find and
every later probe is contaminated); A1, A10, A11, A13, A17, A18 are
logged and read with Part B, except that an outright A17 or A18 failure
also stops the pass because nothing else is then interpretable.

## Part B — finding → step-6 decision map

Each HALT / INVESTIGATE line from the timeline, plus the pass-specific
reads, gets its schema consequence now. "Break" = a change the step-6
LOCK must absorb (obs layout, snapshot, wire); "knob" = config or
prereg value, no break; "instrument" = measurement change only; "law" = engine-rule change,
no layout consequence.
Classification: every row RULED (owner 2026-09-03). Labels: "break" /
"knob" / "instrument" as above, plus "law" = an engine-rule change
with no layout consequence (the legality mask is an oracle over
`validate`, so it follows a law change without a schema bump).

| finding | most likely cause | step-6 decision | consequence |
|---|---|---|---|
| H1 watchdog alarm in a fog arm, silent in the no-fog control | policy never learned to search; or FR-023/memory defective on the scripted side too (check A2, A10) | if A-checks clean: radius / floor re-pin, or a training-budget finding | knob |
| H1 in the no-fog control too | 3.0 schema or digest defect, not fog | Part A localises; fix at the named block | **break** |
| H2 worst seat below the scripted anchor on the same fog config | information the anchor uses (memory, heading) is not reaching the policy in a learnable form | obs layout of the memory token or digest | **break** if a column is dead or degenerate (A2/A5); knob (radius) if columns are healthy |
| H3 hard-zero intended activity | a legality path closed under fog (e.g. the approach to a heard friend arrives at a stale stamp and the partnered proposal fails `is_conscriptable_friend`, `world.rs:1248`) | engine law, or the action surface | **break** iff the fix changes menu length, message-head count, or target-slot layout (`ACTION_SCHEMA` / `MASK_SCHEMA` bump); otherwise **law** (validation or chooser change; the mask is an oracle over `validate`, `mask.rs:56-65`, so it follows for free; re-verify run at the owner's discretion). A zero that Part A traces to a dead column or a masked-row leak is that row's break, not H3's. Owner ruled 2026-09-03 |
| H4 single-activity domination > 0.55 | the F-027 dyadic attractor returning under fog, or the leash too loose for the fog geometry (slot 5 separates these) | β re-pin, or roster arrangement | knob |
| H5 frozen cluster | same as H4, spatial signature | as H4 | knob |
| H6 hyper-dispersion (median ≥ owner's pin) | cats spread to keep everything in view; or the want gate never fires so nobody is called in | floor / listener floor re-pin if wants are under-fired; radius if over-dispersed with wants healthy | knob |
| blind-hungry span long (floor screen + arms) | radius too small for six bowls; or explore not sweeping (A10) | radius re-pin; FR-023 if A10 red | knob / **break** (A10 red means `explore_heading` semantics or the snapshot field) |
| reply-here bar missed by the clone | corpus density (F-034 cliff) or a dead `reply`/answers-me column (A7/A8) | density first (period), then the column | knob / **break** (column) |
| want bar missed | want density on the scripted seats too low at the pinned floor | floor re-pin | knob |
| ambient-here bar missed | F-034 continuity broken by the new digest matrix | corpus / recipe | knob, unless the self digest is shown degenerate (A1) → **break** |
| digest rows never fire for heard-unseen cats | `pos` / audibility plumbing | FR-014 | **break** |
| refusal tax > 3.5% on a seat | drop-on-arrival runs THROUGH the stamp: `Chase(Kitty)` is legal whenever the friend exists (`action.rs:403`), `Play{Kitty}` needs conscriptable (`action.rs:414`), so a partnered proposal at a stale stamp is a refusal; the 3.5% line is the OWNER'S HEURISTIC from previous-generation Biscuit (wasted turns proposing to a partner who cannot or is unlikely to say yes), not a hard rule | **instrument first, landing BEFORE the pass**: a `reason` on `RefusalEvent` (`events.rs:72`; at least `partner_absent` / `partner_busy` / `other`, read off the same validate call; the log is not snapshot state, so this is an event + `/events/refusal` change only). Then: fog-shaped share above the line → knob (audible window / radius); F-033-shaped share above the line → the Biscuit 3.0 design question, outside this pass | instrument (pre-pass); owner ruled 2026-09-03; lands as 049 convergence task T093 (owner confirmed in the Product session 2026-09-03), endpoint shape to follow |
| vocabulary lesson arm (slot 6) differs from mixed corpus (slot 1) on the bars | delivery matters under the new digest (same schema, same columns in both arms, so it cannot name a column) | registered result, feeds step 7's three-arm design | none for the LOCK; sets the step-7 corpus default |
| radius bracket (slot 4) indistinguishable from the pin on welfare | fog barely binds at 20×20 (ROADMAP's standing concern) | Gen 1 ships at the pin; the world-size × radius screen moves to Gen 2 | knob |
| leash dose (slot 5) collapses where slot 1 holds | F-019's fog invalidation condition met | β curve re-derived under fog before step 7 | knob (recipe) |
| pace at 3 threads runs the stop rule past the planned wall clock | box | **no arm is dropped (owner 2026-09-03)**: all six run to the stop rule or the 20M cap and the pass takes the extra hours | none |

## Part C — the rest of the prereg (owner walk-through 2026-09-03)

- **Radius screen (ruled)**: scripted, radii {2, 3, 4, 5, 6} plus the
  whole-world control; the pin is drawn from {3, 4, 5}, 2 and 6 are
  context (where the anchor breaks, where fog stops binding). Euclidean
  disc coverage of 20×20: r=2 3.2%, 3 7.2%, 4 12.2%, 5 20.2%, 6 28.2%
  (open field; edge-clipped averages 3.0 / 6.4 / 10.3 / 16.1 / 21.5%).
  Per radius: anchor welfare curve (watchdog entries, eat/drink max,
  safeguard entries, blind-hungry span), `nn_distance.py` dispersion,
  friend-in-view share. **Pin rule PENCILLED, set after the curve is
  seen and before corpus collection**: smallest radius in {3, 4, 5} at
  which the anchor holds welfare within the seed spread of the no-fog
  anchor was the first draft; the owner expects a substantial scripted
  welfare impact, so "zero adverse events" may be unrealistic and the
  sweep is descriptive first. If no radius clears whatever rule is set,
  that is the finding and the pass runs at 5 as a shakeout, not a pin.
- **Leash consequence (pencilled)**: a weak anchor under fog means the
  clone-and-leash recipe holds learners near a weak teacher; slot 5 (β
  up) is promoted to essential, H2 becomes a floor we expect to clear,
  and H1 (absolute) carries the welfare reading.
- Speaker floor {10, 15, 20, 30}; listener floor set in the same
  sitting (placeholder 0.30). Measures and decision rules as ruled in
  the timeline step 4.
- **PPO horizon (ruled)**: no fixed tick count. Stop an arm when three
  consecutive 1M-tick bins each improve the bin-mean shaped return by
  < 0.005 AND KL-to-anchor changes by < 10% or < 0.02 absolute per bin.
  Cap 20M (safety, never the target). Viability read at 6M: an arm at
  the clone's return with KL flat = leash holding, learner found
  nothing (slot 5's question); an arm below the clone's return = recipe
  not viable under fog, stop and read Part A. Replayed on the twelve
  exp-006 runs the rule stops 10 at 8–9M, E0-s2 at 12M, E0-s1 at 16M,
  never before the 3.5–4.5M transition, return at stop within 0.006 of
  the 20M final. Freed threads may take an extra run.
- **H6 (ruled)**: metric switches to Euclidean (the vision disc;
  instrument already emits `euc_median`; banked baseline is 1.0 in
  both metrics). HALT = NN Euclidean median ≥ 6 sustained 200 ticks,
  one number, no anchor term: five random cats on 20×20 give median
  5.4 (Chebyshev 4.8), so ≥ 6 is avoidance and welfare cannot excuse
  it. Dispersion below the bar is read JOINTLY with welfare: above the
  fog-anchor median with welfare at or above the anchor = strategy
  finding (logged, no investigation); above the anchor with welfare
  below it = INVESTIGATE. Contact share and H5 stay Chebyshev (engine
  adjacency). Companion reads: friend-in-view share (per cat, share of
  ticks with ≥ 1 friend inside `<049:vision_radius>`, always against
  the anchor at the same radius) and cluster shape, to tell loose
  clusters with excursions from five solo cats.
- Corpus: `announce_here = 1` scripted seats, served period, pinned
  radius + floor; size sized to clear the F-034 cliff with margin.
- BC: train to plateau, patience 10, no epoch floor; bars reply-here /
  ambient-here / want, numbers `<pin at declaration>`, held-out set.
- Critic: retrain at width 404, γ 0.998, censored MC targets (the
  exp-006 recipe).
- Pass: six slots per the timeline table; horizon `<owner>` ticks;
  probe every 50 updates, 2,000 probe ticks; Part A at probe 1.
- Kickoff pins owed by the owner: H6 median, the three bar numbers,
  INVESTIGATE band factor, horizon.
- Results: `RESULTS.md` ends in the Part B table with each row's
  outcome filled, which IS the step-6 input.
