# Fog Gen 1 step-5 shakeout — prereg DRAFT (2026-09-03, not declared)

Status: draft, being hashed out with the owner. Knob and field names
marked `<049:…>` were spec 049's to pin; all filled 2026-09-04 from the
merged tree (PR #344, main 75e97d1, served `cloudkitty.toml`). Still
open before declaration: the `reply_intensity_floor` pin on
`anchor.toml` (rule ruled 2026-09-05, number follows the speaker-floor
screen), the `expected_per_1000` rates in `declared_constant.json`
(filled from the BC corpus trace at declaration, rule ruled 2026-09-05),
and the anchor re-smoke at margin 0 once spec 050 `relief_memory_margin`
is on main (merging 2026-09-05; the declaration waits for it, owner
ruled). The BC bar numbers were ruled 2026-09-05 (Part C, BC bullet).
`schema_check.py` and its guard landed 2026-09-04 (e4f0642);
the A1 reasons were ratified the same day (5a16b43). The trainer
(`trainer/train_ppo_fog.py`) landed 2026-09-05 with its own pin list
(`PINS`: β 0.04 / 0.05 provisional; radius, the two schema-5 clones and
the fog critic None until the screens and the BC pass fill them).
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
instrument is `schema_check.py` (landed 2026-09-04; guard
`test_schema_check.py` = plain-python asserts on a recorded bc-collect
`--trace` directory, each row driven red by the exact defect it names,
rule 5). Width and offsets come from spec 049's FR-026 layout
(pinned 408 after the owner's 2026-09-04 ruling adding the kitty-row
"neighbour on a sunbeam" bit: self 85 | 4 × 63 | elements 70 | clock 1;
was 404 with rows of 62; schema number stays 5, no artifact predates
the change). Landed on `049-fog-gen1` @ 51b2baa. Kitty-row offsets
after the landing: water bit 20, on-sunbeam 21, scene age 22, message
block 23–52 (23+2k recency, 24+2k rate), want intensities 53–58,
answers-me 59–62. Element blocks: chow 2 × 5, water 2 × 4, sunbeam
2 × 6, critter 4 × 10. Numpy layout for `schema_check.py`:
`experiments/attn-oracle-2026-08-15/obs_layout_v5.py`.

| # | block | check | healthy reading | degenerate signature → suspect |
|---|---|---|---|---|
| A1 | every column | variance over the probe window | > 0 for every column that can vary on this config | a constant column that should move → wiring; a constant column that cannot move on this config is listed as such at declaration, never discovered |
| A2 | self: element-memory token (20) | per kind: memory set only after a sighting; cleared on a refuted arrival; never set for a kind not yet seen | set-events == first-sight events; refutations > 0 in the fog arms, == 0 in the no-fog control | memory set without sight → leak; never cleared → refutation path dead; token identical across kinds → slot indexing |
| A3 | kitty rows: fog mask | row fields masked exactly when Euclidean distance > `[vision] radius` (served 5, `dx² + dy² ≤ r²` edge included; the knob the radius screen re-pins) | mask flips agree with the geometry on every sampled tick; no-fog control never masks | mask disagrees with geometry → visibility predicate; mask never flips at the pinned radius → radius not applied |
| A4 | kitty rows: heard-unseen position | a masked row whose speaker meowed inside the window carries `pos` from that meow, static until the next audible meow | position changes only on meow ticks; equals the speaker's true position at that tick | position tracks the live cat → Q1 re-rule not implemented (leak); position never set → `pos` plumbing dead |
| A5 | kitty rows: digest (30) | recency + rate per (speaker × kind) populated for masked AND visible speakers | heard-unseen rows have non-zero recency; rates within the scripted emission rates measured in the floor screen | zero digest on masked rows → audibility gated on visibility (wrong); rates > emission → double counting |
| A6 | kitty rows: want intensity (6) | equals the caller's stamped `need/100` at its last want of that kind | matches the trace stamp on every want tick; 0 for kinds never called | constant 0 → not observed; drifts between wants → live need leaking |
| A7 | kitty rows: answers-me (4) | 1 only when the observer emitted the matching want inside the window before the here | count == engine-stamped `reply` events addressed to the observer, per F-029 emit-proof | never 1 in any arm → derivation dead; 1 without a prior own want → window logic |
| A8 | `reply` stamp (engine) | `reply = 1` iff a matching want is audible AND the referent is visible from the speaker | rule holds on every here in the trace; reply count > 0 in fog arms with the scripted reply path on | replies on ticks with no audible want → stamp rule; zero replies with wants and visible referents present → stamp dead |
| A9 | want law | a want is emitted only when armed, top need, and nothing visible or remembered for it | zero violations on the scripted anchor trace (the law is engine-side: policies cannot violate it either) | any violation → `message_legal` under fog |
| A10 | FR-023 explore (lattice serpentine tour, owner ruled 2026-09-03, T088; landed as `crate::explore::Lattice`, field `explore_waypoint`) | a scripted cat with nothing visible or remembered walks toward its current lattice waypoint (inset ⌊r/√2⌋, spacing ≤ ⌊r√2⌋, boustrophedon and back, cycle 2N−2) and `explore_waypoint` advances only on reach or when another cat holds the waypoint; coverage is complete: over one blind tour every tile of the world lies inside some disc, at EVERY screened radius (20×20 lattices: r=5 {3,10,16}, r=4 {2,7,12,17}, r=3 {2,6,10,13,17}, r=2 ten points per axis; the r=2 screen is the hardest case and the one checked) | union of discs along the anchor's blind path == the whole grid within one tour; `explore_waypoint` advances by one per reach, never resets across errands; first-sight latency from blind ≤ one tour + approach (SC-012 bound 144 at r=5; Product measured worst 108, median 28, mean 35 over 399 trials) | a tile never inside any disc → lattice inset or spacing wrong for this (r, W, H) (the old heading rule's pockets: 100/36/4/0 uncovered core tiles at r = 2/3/4/5 on 20×20 plus corners); index resets after an errand → state not persisted; index skips → advance rule |
| A11 | scene age + water bit | scene age climbs 1/tick inside a scene and resets on exit; water bit == on-water tile | exact agreement with the trace | either drifts → snapshot bump |
| A12 | elements block (70) | only visible elements populated; remembered elements appear in the memory token, not here | element rows zero when no element is inside the radius | remembered bowl appears in the element block → memory leaking into sight |
| A13 | emit-proof (F-029) | every category the instruments read has been EMITTED at least once in the window before "zero" is reported; the list includes the kitty-row on-sunbeam bit (kitty-row offset 21, ruled and landed 2026-09-04) at 1 on a Seen row and the water bit at 1, each in the anchor trace | a table of first-emission ticks per category | any category never emitted is "unproven", never "zero" |
| A14 | legality mask (activity + message) | no legality bit depends on a masked fact: the mask is recomputable from the observer's visible rows + own memory alone (adjacency incl. diagonal, distance 1.41, sits inside every radius ≥ 2, so the current law passes; the ruled want / reply law reads only the speaker's knowledge) | recomputing the mask from the observation reproduces the engine mask on every sampled tick | a bit that differs → a 049 rule reads true state through fog |
| A15 | kitty rows: by-id permanent rows (`kitty_slots` = roster−1 = 4) | row identity fixed per observer across ticks; a masked row still exists with masked FIELDS, never dropped or shifted | the (observer, row) → kitty-id map is constant over the probe | rows re-order or compact when a cat leaves view → every downstream column mislabelled |
| A16 | kitty rows: `reply` bit (observed) | the observing cat's row carries the engine `reply` stamp on the same here, per speaker | observed reply column == A8's stamp on every here in the trace | engine stamps, observation stays zero → the ladder tie-breaker is invisible to learners |
| A17 | anchor / policy observation parity | the scripted anchor and the PPO arms observe the identical vector on the identical config (same fog, radius, memory) | per-block variance (A1) and mask flip rate agree between the anchor trace and a policy trace at matched ticks | disagreement → the arms train on a world the anchor did not see (the exam-vs-gym skew class) |
| A18 | probe determinism | same snapshot + same radius → byte-identical observation (house bit-identical methodology) | two encodes of every probe snapshot agree byte for byte | any difference → nothing in A1–A17 is interpretable across probes |

Rows A14–A18 added on the (3) walk (owner ruled all five 2026-09-03).
Not added: contagion (shelved for Gen 1), scene-age float (A11), the
width itself (a schema-header pin, `attn.rs:322`, not a probe read).

Reading rule: any red on A2–A9, A12, A14, A15, or A16 at probe 1 is a
**stop the pass** event (it is the defect the pass exists to find and
every later probe is contaminated); A1, A11, A13, A17, A18 are
logged and read with Part B, except that an outright A17 or A18 failure
also stops the pass because nothing else is then interpretable. A10's
coverage half is read once, on the scripted r=2 radius screen BEFORE
the pass (it is an anchor property, not a training one); a red there
stops the screen, since an uncovered core would make the radius pin
measure the sweep rule instead of vision (why T088 was re-ruled). Its
index-persistence half is read at probe 1 with the rest.

Instrument status, 2026-09-04 (anchor smoke: `anchor.toml`, 1000 ticks,
seed 870001, bc-collect `--trace`; 4981 decisions, 5000 observations):
17 rows green; A17 lit 2026-09-05 from the fog trainer's smoke probe
(random init, 3 × 100 ticks): red as expected for a random policy, and
the disagreement split by direction taught the exemption rule below.
What the smoke taught, carried into the rows' reading:

- A5's healthy reading "heard rows have non-zero recency" is false for a
  row heard only through `wait_for_me`, which is outside the 15 digest
  kinds (110 of 10553 heard rows). The checker counts those apart; they
  are not a defect.
- A6: a want stamp is taken after the caller's own action and before the
  phase-4 rise, so it can sit below both snapshot readings by one tick's
  rise. On water the bath rise is `bath_gain × bath_ratio` (kitty 4:
  0.4 + 3.5 × 2 = 7.4 per tick, world.rs:1097).
- A8 and A9 are read exactly only where both snapshot ends agree; the
  rest (a bowl emptied earlier in the apply order, a want armed at one
  end only) is reported as "soft", never as green. Smoke: 0 hard
  violations, 5 soft.
- A16: the answers-me compare is strict (`their_here > my_want`,
  observe.rs:619), so a wanter who re-calls on the reply's own tick
  never sees the bit. With equal cooldowns the pair falls into lockstep
  (kitty 2 / kitty 4, ticks 456–486); 3 of 169 replies in the smoke were
  invisible this way. Engine semantics, not a wiring fault; logged as a
  Part B observation on the reply channel.
- A1 on this config: 102 constant columns, six reasons
  (`declared_constant.json`), all ratified by the owner 2026-09-04.
  Constancy is a property of the sample; inertness is a property of the
  generator, so a reason is one of two kinds. STRUCTURAL: a proof from
  law, config or roster that the setting event is unreachable, good for
  any corpus length. Three of these: trill/ekekek off in the vocabulary;
  mew/chirp/purr never scripted; **want_drink is silent for the whole
  run** because `known_relief(drink)` holds once water is seen or
  remembered, water never moves and memory never expires (F-040). Spec
  050 `relief_memory_margin` = 0 revives the want, but at ~1.2 calls per
  1000 ticks on the served seed (Product's 20k read, 2026-09-05: 1,021
  drink-top-and-armed cat-ticks, 25 legal; the law is armed AND top need
  AND no known relief, `meow.rs:262`), not the ~12 that F-040 row 3
  simulated. So when 050 lands this group is not dropped; it converts to
  RARE with the re-smoke's measured rate (owner ruled 2026-09-05).
  RARE: the wiring is shown alive by a sibling column on the same
  encoder loop (or a forced emission) and only incidence is unknown.
  Three of these: distress flags for five needs (the cuddle flag on the
  same loop moved; the others peaked 35–64 against a line at 90),
  want_play on kitty rows 0 and 3 plus the here_critter bit (rows 1–2
  moved; play is rare by law with five cats), critter slots 3–4 (slots
  1–2 fill; four critters on the map, three in one disc never seen in
  5000 cat-ticks). The checker reads a rare constant as **unproven**,
  and red once the corpus is 5× the expected wait (`expected_per_1000`,
  filled at declaration from the BC corpus trace at the pinned knobs,
  the same config and roster the clone learns from, so the rate and the
  clone share one world; null until then; the factor 5.0 stands. Owner
  ruled 2026-09-05). A rare group whose columns moved reads stale, the good
  outcome. A17 exempts rare-declared columns from the can-vary
  comparison (early PPO crosses distress; the anchor never does). A
  structural reason has two proofs, and only one binds a policy: LAW
  (trill/ekekek refused by the engine) holds for every mind, ROSTER
  (mew/chirp/purr never scripted; water remembered before the first
  drink) holds for the scripted anchor alone, and the smoke policy
  moved all 31 of those columns. Roster-proof groups carry
  `a17_exempt: true` and A17 reports them apart; a law-proof column
  that moves stays red.
- Scripted mask-mismatch: 19 of 4981 decisions (0.38%) had the behavior
  propose an action the mask forbids (bc-collect drops none; it records
  the mask). Read with Part B; not a schema row.

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
| blind-hungry span long (floor screen + arms) | radius too small for six bowls; or explore not sweeping (A10) | radius re-pin; FR-023 if A10 red | knob / **break** (A10 red means `crate::explore::Lattice` semantics or the `explore_waypoint` snapshot field) |
| reply-here bar missed by the clone | corpus density (F-034 cliff) or a dead `reply`/answers-me column (A7/A8) | density first (period), then the column | knob / **break** (column) |
| want bar missed | want density on the scripted seats too low at the pinned floor | floor re-pin | knob |
| ambient-here bar missed | F-034 continuity broken by the new digest matrix | corpus / recipe | knob, unless the self digest is shown degenerate (A1) → **break** |
| digest rows never fire for heard-unseen cats | `pos` / audibility plumbing | FR-014 | **break** |
| refusal tax > 3.5% on a seat | drop-on-arrival runs THROUGH the stamp: `Chase(Kitty)` is legal whenever the friend exists (`action.rs:403`), `Play{Kitty}` needs conscriptable (`action.rs:414`), so a partnered proposal at a stale stamp is a refusal; the 3.5% line is the OWNER'S HEURISTIC from previous-generation Biscuit (wasted turns proposing to a partner who cannot or is unlikely to say yes), not a hard rule | **instrument first, landing BEFORE the pass**: a `reason` on `RefusalEvent` (`events.rs:72`; at least `partner_absent` / `partner_busy` / `other`, read off the same validate call; the log is not snapshot state, so this is an event + `/events/refusal` change only). Then: fog-shaped share above the line → knob (audible window / radius); F-033-shaped share above the line → the Biscuit 3.0 design question, outside this pass | instrument (pre-pass); owner ruled 2026-09-03; lands as 049 convergence task T093 (owner confirmed in the Product session 2026-09-03). **Shape (Product, 2026-09-04, implementation follows T092)**: `GET /events/refusal` → `{capacity: 6000, events: [{kitty_id, proposed, tick, absorbed, reason}]}`, oldest first; `reason` ∈ `partner_absent` (kitty target exists, not adjacent) / `partner_busy` (adjacent, failed conscription: only `Play{Kitty}`) / `other` (everything else, incl. nonexistent target); derived at the stamp site from the one `validate` judgement; runtime ring only, no schema consequence. **Read**: tax = TAXED share per seat per tick (refused and the turn resolved to Idle; F-039's convention, the one the 3.5% line was drawn on), split by `reason`; the fog-shaped share is `partner_absent` on `Rest/Sleep/Groom{f}` (stale heard position) plus `partner_busy` on `Play{Kitty}`. **The scripted anchor's own partner rate is NOT zero (Product measured 2026-09-04, served roster all scripted, 20k)**: r = 5 partner_absent 3,293 (Rest 2,596, Play 366, Sleep 323, Groom 8; 1,096 taxed / 2,197 absorbed), partner_busy 1,979 (all Play; 294 / 1,685), other 2,975 (Move 2,437, Eat 538); r = 40 absent 3,352 / busy 2,210 / other 3,074, radius-flat. Mechanism: a scripted cat proposes at a friend adjacent in the start-of-tick snapshot, the friend (earlier in the fair turn order) moved first, the proposal is refused at apply: the same-tick ordering tax, ~1.4% taxed partner share per cat-tick at global vision, so fog adds nothing to it at these radii. The earlier expectation of zero was wrong. So the anchor at the same radius is the calibration baseline and the fog-specific drop-on-arrival signal is the policy seat's taxed partner share MINUS the anchor's; the 3.5% line applies to the seat's absolute taxed share as in F-039. `other` is split by the verbatim `proposed` variant in the instrument (Eat/Drink with nothing adjacent = the stale-memory arrival class, Move = collisions, Play/Chase{Critter} = the intended play-ends-short artifact), so no fourth `reason` value is needed. Reading test in the 049 branch: `cargo test -p cloudkitty-core --test refusal_reasons -- --ignored --nocapture` |
| vocabulary lesson arm (slot 6) differs from mixed corpus (slot 1) on the bars | delivery matters under the new digest (same schema, same columns in both arms, so it cannot name a column) | registered result, feeds step 7's three-arm design | none for the LOCK; sets the step-7 corpus default |
| radius bracket (slot 4) indistinguishable from the pin on welfare | fog barely binds at 20×20 (ROADMAP's standing concern) | Gen 1 ships at the pin; the world-size × radius screen moves to Gen 2 | knob |
| leash dose (slot 5) collapses where slot 1 holds | F-019's fog invalidation condition met | β curve re-derived under fog before step 7 | knob (recipe) |
| groom pile-on: responders per audible `want_bath` > 1 sustained (anchor at r=40 vs the fog radii) | the 049 groom response hears for the 30-tick digest window while 2.x listened within the 10-tick cooldown, so stale asks attract two responders to a caller a third cat is already grooming (Product measured 2026-09-03: divergence at tick 559 at r=40); under fog a responder cannot see the caller is busy until it arrives | rung freshness rule (act only on asks aged ≤ the announce cooldown, inclusive; audibility itself unchanged) plus an on-sight drop when the visible caller's bath is below the announce threshold; **owner ruled 2026-09-03** (049 T087 rulings 3 and 4), lands with 049, so this read is a check that the rung holds, not a proposal | knob-class law change; **break** only if the second arrival exposes a double-groom scene defect (Groom validation checks adjacency only, action.rs:385) |
| groom relief farm: groom-of-clean-friend rate (target bath below the announce threshold at scene start) in a policy arm above the anchor's | `Grooming { target: Some }` pays the groomer `groom_cuddle_relief` unconditionally (action.rs:747-760) and `Groom { target }` is legal on any adjacent friend (action.rs:385), so cuddle relief can be farmed on a clean neighbour with no ask; 2.x pricing, first looked for here; degenerate form = the F-027 dyadic attractor. Product's probe 2026-09-03 saw the scripted form (k1 + k5 grooming k4 at bath 1.6 on a 25-tick-old ask); rung fixes bind anchors only | pricing (groomer relief scaled by the target's bath need, or zero below threshold), never a reward term (F-018 layer 2: the farm is an equilibrium under the price; scripted seats are IN the team reward, so an honest groom of a dirty anchor already pays more than a clean-target groom at 0.5); post-LOCK is fine | **law** (pricing), no schema; read TOGETHER with H4 |
| pace at 3 threads runs the stop rule past the planned wall clock | box | **no arm is dropped (owner 2026-09-03)**: all six run to the stop rule or the 20M cap and the pass takes the extra hours | none |

## Part C — the rest of the prereg (owner walk-through 2026-09-03)

- **Radius screen (ruled)**: scripted, radii {2, 3, 4, 5, 6} plus the
  whole-world control; the pin is drawn from {3, 4, 5}, 2 and 6 are
  context (where the anchor breaks, where fog stops binding). Euclidean
  disc coverage of 20×20: r=2 3.2%, 3 7.2%, 4 12.2%, 5 20.2%, 6 28.2%
  (open field; edge-clipped averages 3.0 / 6.4 / 10.3 / 16.1 / 21.5%).
  Per radius: anchor welfare curve (watchdog entries, eat/drink max,
  safeguard entries, blind-hungry span), `nn_distance.py` dispersion,
  friend-in-view share. The blind-hungry span and safeguard entries
  test the ratified blind price (T090, owner 2026-09-04: an unseen,
  unremembered kind is priced `radius + 1`, the Manhattan lower bound;
  `None` at a covering radius): with the tour coverage-complete, a
  small-radius anchor grooming or playing through hunger points at
  `tile_cost × (r + 1)` first (6 at r = 5, 3 at r = 2), and a long span
  on a cat holding a stale memory points at the memory-beats-bound
  rule, not at the price. **Pin rule PENCILLED, set after the curve is
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
  the timeline step 4. **Listener floor rule (owner 2026-09-05)**: no
  arm of its own; `reply_intensity_floor` = picked speaker floor / 100,
  so every audible want is answerable and a 0.30 listener over a 15
  speaker (the step-4 caveat) cannot occur. If the pick is 20 or 30, a
  two-arm scripted contrast at that speaker floor, listener
  {picked / 100, 0.30}, reads reply rate and informativeness before
  the pin. Neither floor varies in the PPO pass.
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
  ticks with ≥ 1 friend inside `[vision] radius`, always against
  the anchor at the same radius) and cluster shape, to tell loose
  clusters with excursions from five solo cats.
- **Responder-approach read (companion, added 2026-09-03 after the
  FR-036 bath re-ruling)**: `want_cuddle` and `want_play` have no
  scripted listener (the groom response answers `want_bath` only), so
  under the ruled want law these two words are pure social cues and
  whether anyone acts on them is the learners' to show. Measure, per
  learner seat and per word: of the audible `want_cuddle` /
  `want_play` entries in `recent_meows` whose speaker was NOT in the
  listener's view at the tick of the meow, the share where the
  listener's Euclidean distance to the speaker falls by ≥ 2 within the
  next `[meow] recent_window_ticks` (served 10) ticks (approach), and the share where
  a partnered cuddle or play scene with that speaker starts within the
  same window (uptake). The in-view exclusion keeps the read on the
  word: a speaker already visible triggers the want-gate path, not the
  cue. Always against the anchor at the same radius, whose approach
  share is the chance rate (scripted seats never route on these
  words). Reading: learners above the anchor on approach = the cue
  carries and no rung is owed; at or below the anchor on BOTH words
  across the reference arms = the words are inert, which is the
  trigger for the banked scripted cue-answer rungs (a
  `cuddle_response` / `play_response` in `needs_driven`, mirror of the
  groom response: hear, approach, offer; law-class, no schema, fine
  post-LOCK) and for revisiting the cuddle clause of FR-036 in the
  same sitting (owner 2026-09-03: "see how those shake out, add a
  scripted cue answer if needed"). No HALT and no step-6 gate hangs on
  this read; it is a step-7 input only. Instrument: probe-side, from
  the probe's own snapshots (`recent_meows`, positions, scene starts
  from `/events/activity` spans); written with `schema_check.py`.
- **Config rule (owner ruled 2026-09-03)**: every screen, corpus, and
  arm here, and the step-7 certification training, derive from the
  served `cloudkitty.toml` with the #332 bump reverted
  (`groom_cuddle_relief = 0.5`); any deliberate training/serving
  divergence is declared in this file by key. Root `training.toml`
  (the exp-001 scarcity world: 1.5× need rates, pre-041 relief prices,
  `groom_cuddle_relief` 15.0) is NOT a source for Gen 1 configs;
  exp-006's `collect-config.toml` trained at 8.0 against a served 0.5,
  which is the Clementine futile loop and the #332 bump in one line.
- **Reward (declared)**: spec 014 team welfare, unchanged: Nash power
  mean (`p = 0`, `epsilon = 0.01`, `mode = level`) of unclamped
  happiness over the FULL roster, scripted seats included; happiness
  weights 0.2 / 0.2 / 0.15 × 4 (identical in every config checked);
  no per-seat or personality term (ROADMAP guard 3, F-018 layer 2);
  shaping off unless an arm declares a team-level potential here. The
  leash β is a constraint, never an objective. No arm in the pass
  touches `[rl.reward]`, so no F-018 layer-2 exception is claimed.
  The stop rule reads `ep_return_mean`, the env's unshaped team return.
- Corpus: `announce_here = 1` scripted seats, served period, pinned
  radius + floor; size sized to clear the F-034 cliff with margin.
  Config = `anchor.toml` (this directory): the served `cloudkitty.toml`
  with three keys changed, each declared here: `groom_cuddle_relief`
  2.0 → 0.5 (the config rule), `announce_here` unset → 1 (this line),
  `reply_intensity_floor` unset → 0.30 (the served comment assigns the
  floor to this config; 0.30 is the provisional value, owner pins at
  declaration). Unset, the served config emits no here-word and no
  reply at all (anchor smoke: 0 of each in 1000 ticks), so A7/A8/A16
  cannot be read on it. Anchor roster: 1 needs_driven, 2 playful, 3–5
  needs_driven.
- BC: train to plateau, patience 10, no epoch floor. The 60-epoch
  extension (F-034 addendum 2: act@1 .80 → .82 at 3× cost) is NOT taken;
  the clone is PPO's init and PPO moves the action head, while the
  message head's fluency is density-shaped. Reopen only on a bar miss.
  **Bars (owner ruled 2026-09-05), all on the held-out set**:
  reply-here and ambient-here opportunity-use ≥ 0.50 per kind (under
  F-034's fluent band .58–.80, above the half-fluent .35–.56); msg@1 on
  here-rows ≥ 0.80 (A1 read .8748); want emission per kind within ±15%
  of the source rate (relative, so it survives the speaker-floor pick),
  applied only to kinds with ≥ 100 source rows; a thinner kind (drink
  at ~1.2/1000 is one) reports its count and is excluded from the gate.
- Critic: retrain at width 408, γ 0.998, censored MC targets (the
  exp-006 recipe). The trainer pins width through its tokenizer module
  (`obs_tokens_v4.OBS_DIM`, asserted against the runner's dims at
  start); Gen 1 has `obs_tokens_v5` (cbf76eb, pads only all-zero rows
  so a Heard row stays attended), so no schema-4 artifact is touched.
  Trainer cutover landed 2026-09-05: `model_v5.py` (torch forward
  parity-guarded against the certified oracle) and
  `trainer/train_ppo_fog.py` (the exp-006 recipe at 408/55, six slots
  keyed to the step-5 table, owner pins in `PINS` with the launcher
  refusing an unpinned slot outside `--smoke`, per-arm config =
  `anchor.toml` with only `[vision] radius` rewritten, the Part C
  plateau stop beside the §10 welfare stop, `probe-u*.npz` dumps for
  A17). Two rulings (owner 2026-09-05): the training roster is the
  served composition with every seat a policy (the exp-006 mix 0.0, no
  spread family), and the critic keeps its 197-wide global-state view
  (schema 1 did not move; the "width 408" above is the policy's, the
  critic retrain is for the value distribution under fog, not a new
  width).
- **Cosleep-on-beam read (companion, owner ruled 2026-09-04 with the
  on-sunbeam bit)**: T092 made the scripted sleep arm cosleep beside a
  settled friend on a sunbeam (conduction pays sunbeam-grade relief),
  and the final 049 review had scripted cats walk to a settled friend's
  beam in reach. The observation now carries the trigger as a primitive
  (row on-sunbeam bit × the row's resting/sleeping one-hot). Measure per
  learner seat: of its cosleep scenes, the share started beside a friend
  whose tile is a sunbeam; and of the ticks a settled friend on a beam
  was Seen and the seat's own sleep need was armed, the share where the
  seat closed distance to that friend within `[meow] recent_window_ticks`
  (served 10) ticks. Both against the anchor at the same radius. Learners at or
  above the anchor = the demonstration transferred; well below with
  sleep welfare intact = the learner found other sleep (a strategy
  finding, logged); well below with sleep welfare below the anchor =
  INVESTIGATE, first suspect the bit's plumbing (A13 must show it at 1
  before this read is trusted). No gate hangs on it.
- Pass: six slots per the timeline table; horizon `<owner>` ticks;
  probe every 50 updates, 2,000 probe ticks; Part A at probe 1.
- Kickoff pins owed by the owner: INVESTIGATE band factor, horizon. (H6
  median and the three bar numbers are ruled, above.)
- Results: `RESULTS.md` ends in the Part B table with each row's
  outcome filled, which IS the step-6 input.
