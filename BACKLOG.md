# CloudKitty Backlog

Prioritized future work. Everything here was deliberately kept out of the MVP
(see `specs/001-cloudkitty-mvp/spec.md`, "Out of Scope") or added since. Per the
constitution, none of it may violate Articles I–VI, and each feature goes through
the spec-first flow (`/speckit-specify` → plan → tasks) when it is picked up —
this file records priority and intent, not design.

Priorities: **P1** quick wins, next up · **P2** the bigger pieces, for a proper
sitting · **P3** simulation depth · **P4** world-scale ambitions.

## P1 — quick wins, next up

<!-- shipped P1 items are removed once merged; see git history -->

### Graphics v2 follow-on: face-group pitch (added 2026-07-29; Client thread)
The one v2 piece still unbuilt (vocabulary, motion wiring, and swim all
shipped — see git history / PR #92). Slide eyes+nose+mouth together
up/down the head to simulate head tilt (looking down to eat/drink, up
at a bug). Shape agreed: a per-pose scalar (e.g. `L.pitch`) blended
through `blendLayouts` (the motion wiring's `Presentation.tweenFor`
seam makes this free), consumed in `drawFace` as one shared y-offset on
eyes and nose (mouth anchors to the nose and follows). **Trap:** the
tuxedo/seal-point head masks are anchored to the `NOSE` tunables — they
are fur markings and must NOT move with pitch; pin them to the static
baked values. **Dead end, do not rebuild:** pupil-shift gaze was built
and reverted — max travel ~0.24px at world size, unreadable; pitch
replaces it. House method: judge in `gallery-v2.html` (dials +
readout), bake on the owner's paste.

### Water cues: occlude the cat's lower body — SHIPPED 2026-08-07 (PR #124)
Clipping the cat against the waterline, so a cat on a water tile is
visibly half-submerged whatever pose it is wearing. Solved the
water+action case in one stroke, as the entry predicted: a cat keeps its
*drinking* or *grooming* pose (which `poseFor` lets outrank the wade) and
still reads as standing in water — no second pose, no per-activity
special-casing.

Built exactly on the groundwork the entry named: it consumes
`Presentation.wetFor`, so the surface rises and falls with a shoreline
crossing (measured 0.88 → 0.72 and back, symmetric over `wetFadeMs`)
rather than popping, and the shadow, the ripple and the waterline can
never disagree.

**Waterline 0.72**, owner-picked from six depths rendered through the
shipping path at live tile size; it crosses the bottom of the body so the
cat is clearly *in* the pond, while the pose stays legible. 0.62 —
matching `SWIM`'s own surface, which would have given wading and swimming
cats one shared water level — was rejected because a standing cat then
looks like it is swimming. The swim pose opts out of clipping entirely:
it is already drawn sunk.

The deferral condition was met by v3 Phase 1's larger tile, as planned.

**The entry's second half is resolved too, and verified rather than
assumed.** It said a single water tile rendered as a rounded blue square,
because `shoreRounding` was a flat 0.45 tiles applied to a 1×1 blob. The
shoreline pipeline was rewritten in the 2026-08-07 meadow round — arcs
first (`sampleRoundedLoop`), wobble riding the finished curve, rounding
0.8 — and an isolated water tile now draws as a rounded organic blob.
Checked on interior 1×1 ponds in the preview world at high zoom, not
inferred from the dial change.

That leaves the river case, which is NOT covered: rounding is still a
flat constant rather than clamped by local channel width, so a 1-wide
channel would still bead into lozenges, and `groupWaterTiles` still
floods 4-adjacent only. Both are recorded in the v3 plan's Phase 5.

### Pond restyle — give the pond a bottom (added 2026-08-09; Client thread)
The design handoff's **spec 02**, plus the deltas we measured against it. The
bundle itself lives at `deletemewhendone/design_handoff_art_uplevel/` and is
gitignored and temporary — everything below is the part worth keeping.

**The proposal, in one line:** a blurred copy of the pond's own silhouette is a
distance-to-shore field, so one blur buys depth without a distance transform.
Composite a pale shore over a deep base inside the existing clip, add a damp
"lip" ring outside the water, replace the per-tile shimmer with a caustic net,
and swap the hardcoded 1.5px `pondRim` for a tile-proportional meniscus. It
leaves `buildPondPath`, `groupWaterTiles` and the shore dials alone, adds seven
tunables plus `pondDeep`/`pondLip` per theme, and bakes into the existing
`pondCache`. Its own house-rules section is accurate — dual-home rule, Article
V/VI, no assets, gallery-meadow as the lab.

**Three deltas we measured, which the spec could not have known:**

1. **The caustics cost claim is inverted for our world.** It argues "8 polylines
   per pond instead of 2 strokes per tile", justified with a fifteen-tile pond.
   We have **7 water tiles in 4 blobs — one 2x2 lake and three lone tiles**.
   Today that is 14 shimmer strokes total; the proposal is 32 polylines, ~416
   segments. A ~3x increase, not a saving. Cheap either way, but `causticLines`
   wants to scale with blob area rather than being a flat 8 per pond.
2. **Build the shared offscreens from the start.** The spec offers two canvases
   *per pond* and notes in its own risks that 3+ blobs should share one pair. We
   have 4. At WQHD that is ~19MB per offscreen: **~153MB per-pond against ~38MB
   shared**.
3. **Our world is dominated by the spec's own hardest case.** Its acceptance
   criterion 1 says a lone tile is harder, because at `pondDepthBlurTiles = 0.95`
   it is almost entirely "shore". **Three of our four ponds are lone tiles.** Judge
   those first, and expect the blur to want clamping by blob size.

4. **Caustic count comes from AREA; the spacing comes from HEIGHT — so a long
   thin pond is double-dense.** `lines` is
   `round(tileCount * causticLinesPerTile)`, capped, but the lines are seated at
   `(i + 0.5) / lines` across the *bounding-box height*. A 4-tile river and a
   4-tile lake therefore both ask for 6 lines, and the river has half the
   vertical room. Each line wanders `±1.9 * causticAmplitude` (0.9 drift + 1.0
   wave), so lines collide once `height / lines` closes on that. Minimum gap
   between adjacent lines, sampled over 40s at a 31px tile:

   | values | lone 1x1 | 2x2 lake | river 4x1 |
   |---|---|---|---|
   | spec (amp 0.08, cap 8) | 6.7px | 1.5px | **-3.7px, crossing** |
   | shipped (amp 0.025, cap 4) | 11.9px | 11.9px | 4.2px |
   | shipped amp, cap 6 | 11.9px | 6.7px | 1.6px |

   The owner found this by eye on exactly the two shapes it predicts, and fixed
   it by lowering the cap. So **`causticLinesMax` is currently standing in for a
   density rule**: 4 is chosen by the river, the shape with the least height per
   tile, and it is what holds the lake's count down too. If ponds ever get
   bigger or longer, scale the count by bounding-box height instead of tile
   count and let the cap go back to being a safety net.

**Owner decisions already taken, ahead of the work:**
- **The cat's wet ripple is already off** (`VIEW.ambient.wetRipple`, 2026-08-09).
  The spec proposes keeping and recolouring those rings; we overrode it — two sets
  of rings, the cat's and the water's, read as a mistake rather than as depth.
- **Zero the shore wobble as part of this**, not before it. `shoreWobble: 0` in
  BOTH homes (dual-home rule). Measured at our pond sizes the irregular edge is
  nearly invisible — a lone tile is identical with it on or off — so it costs
  almost nothing, and the new lip and meniscus take over the job of softening the
  edge. `wobbleAlong` short-circuits cleanly at 0. **Not independent of
  `shoreOverdraw`**: the wobble biases the outline inward by
  `0.25 * amp * (1 - bulgeEase)`, which at the shipped values is 0.005 tile off a
  0.1 tile spill, so zeroing it returns that and the pond grows by a hair.

**Also in the bundle:** spec 03 (meadow drifts — clustered cover instead of
independent per-tile rolls, and the `grassTones` lattice), and a parked spec 01
(cat lighting) the owner deferred. Recommended order 02 then 03; 03 is the one
that needs the lab's occlusion strip.

### Ambient whole-body float — CLOSED, not doing (2026-08-09; Client thread)
Graphics v3 Phase 4 listed a slow whole-body y-bob for every cat, borrowed
from kitten.me, on top of the breathing we already have. **Closed by the
owner** rather than deferred, and the reasoning generalises so it is worth
keeping: the walk's body bob was built, measured and reverted the same day
(branch history, `56b071c`) because at our tile size a few tenths of a pixel
of vertical motion on a rigid body reads as **edge shimmer, not life** — the
body travelled 0.56px peak-to-peak at a 56px tile against a foot's 9.52px
fore–aft.

The same arithmetic applies to an ambient float, and worse: an idle cat has no
lateral motion to hide behind. If it ever comes back it should come back as
the *whole-cat* mechanism from that revert (head, tail and limb pivots riding
the body, grounded feet held), not as a torso sliding against a welded head —
and only at an amplitude that clears a pixel.

### Whiskers — deferred to camera mode (2026-08-09; Client thread)
`cat-v2.js` says "No whiskers — ever" and that stands for now: three per side
at our cat size land near **0.8px strokes**, which is where the original
attempt died. The v3 plan's hope was that a bigger tile would fix it; Phase 1
raised the tile and it is still not enough.

**The re-examination trigger is camera mode**, not a date. A camera that zooms
in is the one change that would move whiskers out of sub-pixel territory, and
it is already deferred until after the art (see Deferred, below). Judge them
at the *camera's* cat size, not the gallery's, and treat "cut again" as an
acceptable outcome — that is what happened the first two times.

### The walk contradicts itself travelling north/south (added 2026-08-08; Client thread)
Our cat is a **side profile**, so it encodes a heading. The legs sweep
fore–aft — horizontally on screen — whatever way the cat is actually
going, and that sweep is the entire basis of the planted foot: a stance
paw drifts backward at exactly the rate the ground passes under it, so
it holds still against a mark.

Travelling east or west that cancels: 9.5px of paw sweep against 56px of
travel per tick, same axis. Travelling **north or south the axes are
perpendicular** — the paw still sweeps 9.5px sideways while the cat
carries it 56px vertically, so every foot, planted or not, slides across
the ground at full walking speed. Nothing cancels. `dx === 0` also keeps
the previous facing (`anim.js`), so the cat is a profile sliding sideways
up the screen.

**Measured, not guessed** (9-minute live census, `client-measurements/`):
717 east/west moves against 394 north/south, so **35.5%** of walking is in
the mode where the planting does nothing. Walking is ~28% of frames, so
this is about **10% of all frames** — which is the budget any fix has to
fit inside, and it rules out a new art vocabulary on its own.

This is a consequence of the gait work succeeding, not a regression: with
the old pegs the feet slid in every direction, so nothing was claimed and
nothing was contradicted. **Doing nothing is a legitimate answer** and is
what ships today (owner's call, 2026-08-08 — deferred in favour of higher
value work).

Options, costed, so this does not get re-derived:
- **Front/rear-facing vocabulary** — the only true fix, and out of all
  proportion: two more views of body, head, ears, face, tail, legs and
  every pattern mask, for every pose, plus something sane when a cat turns
  from east to north (a snap pops, a blend needs in-between views).
- **Rotate the profile toward travel** — cheap, but a rotated side view
  reads as a cat climbing a hill, not walking away.
- **Isometric projection**, so north has a horizontal component — that is
  the whole world (tiles, ponds, shadows, elements), and camera work is
  already deferred until after the art.
- **Damp the sweep by the horizontal share of travel**, `|dx|/(|dx|+|dy|)`
  — about five lines, the renderer already has the delta. Risk: still legs
  read as an escalator, and the factor pops at direction changes unless
  smoothed across a tick.
- **Swap the motion instead of killing it**: for vertical travel replace
  the fore–aft sweep with a small alternating *piston*, paws stepping
  under the body rather than past it — the old sprite-game convention for
  "walking toward/away from you". ~30 lines, entirely inside the walking
  case, no new vocabulary. **Best value of the list if this is picked up.**

Suggested shape if revisited: one dial, 0 = today's full sweep, 1 = full
piston, damping as the midpoint, judged in the lab on a card that walks a
cat north and south — with "do nothing" as a fourth thing in the
comparison, not as the absence of one.

## P2 — the bigger pieces, for a proper sitting

### Eval-suite v2: a stronger counterfactual baseline (added 2026-07-25)
Spec 017's guest-welfare differentials and per-kitty sign test measure
every scripted kitty against its own counterfactual self in the
**all-scripted baseline**, where candidate seats are rewritten to
`needs_driven` (research.md R4). That reference is deliberate for v1 —
`needs_driven` is the shipped default, and pairing against it makes
temperament cancel exactly — but it means a differential reads "worse
than needs_driven neighbors would have been," not harm in an absolute
sense, and a merely-mediocre candidate trips sign tests as general harm
(now annotated as such, distinct from masked exploitation). Once a
trained policy has cleared certification and earned trust, a future
suite version can raise the bar: bind the **baseline** seats to a
proven better-than-needs-based agent (a pinned, hash-referenced
`.ckpolicy` — frozen like everything else in the version), so
differentials measure candidates against the best-known cooperative
partner rather than the hand-written default. Design cares when picked
up: the baseline artifact becomes part of the suite version's frozen
identity (manifest-referenced by hash — the artifact-agnostic
`policy:candidate` convention stays for the *candidate* seats only);
determinism self-checks must cover policy-driven baselines (they are no
longer "scripted", so the exit-2 fallback accounting applies to
baseline runs too); and cross-version comparability breaks by design —
v1-vs-v2 scores are different questions, which the version stamp
already makes explicit. Sequencing: after the first certified policy
exists, alongside whatever else v2 wants (owner note, 2026-07-25) —
**that condition is now met** (s3/s6 certified clean 2026-07-30), but
the suite is in active exp-003 service; hold until that experiment
closes. Natural pairing: the small-world exams entry below (P2).
Additional v2 nicety (experiments session, 2026-07-27, low priority):
Mixed mode always seats the subject at roster index 0
(`harness.rs`, the `Mixed if index == 0` arm), so mixed certification
only ever tests the policy from one seat/start position. Fine for
paired comparisons (seat-symmetric by construction — exp-001 is
unaffected); a rotate-the-seat option is a v2 nicety, not a fix.

### Suite reporting/visualization tooling — standing constraint (added 2026-07-25)
No such tooling exists yet; this entry records a **binding design
constraint** for whenever it is built (dashboards, experiment trackers,
report renderers — anything that consumes `kitty-eval --suite` JSON).
The mixed-roster exam's per-kitty **sign test** (spec 017 FR-015,
research R12) defaults to *warn*: a triggered exploitation signature
exits 0 and lives only in the report and the JSON `sign_test` block.
That tier's entire value is visibility — a warn that can be missed is a
gate that silently stopped existing, and we have the scar to prove it
(the PettingZoo conformance step failed silently under
`continue-on-error` for months). Therefore: **any reporting or
visualization surface MUST display a triggered sign-test warning
prominently** — top-level, not buried in a table — alongside the
doctrine that a signature on a real candidate prompts a strict rerun
(`--enforce sign-test`) before the result is quoted. When the tooling
is specced, this constraint goes in its FRs on day one.

### Refactoring targets — from the 2026-07-26 survey (added 2026-07-26)
A three-way parallel survey (core engine / RL crate / client + py bindings)
ranked refactors by benefit-per-risk, evidence verified line-by-line. Not
features: each is behavior-preserving, and the verification bar when picked
up is bit-identical output (determinism suite + byte-diffed eval reruns),
which may stand in for the full spec-first flow at the owner's call.

**Top three: all SHIPPED** as specs 018/019/020 (2026-07-26, tagged
v2.4, PRs #56–#58) — kitty-eval/suite dedup via `cli_support`, the
compiler-enforced need→relief pairing in `behavior/relief.rs`, and the
`config/{mod,defaults,validate}.rs` split. Each verified bit/byte-
identical; the specs and git history hold the detail.

**Runners-up (fold in opportunistically, don't open a sitting for them):**

- `suite.rs` (1,101 production lines) splits cleanly along its four banner
  seams (manifest / report types / scoring+verdict / render) — but it's
  days old and stable; let it earn the churn. Item 1 overlaps it anyway.
- `world.rs` (2,260 lines, ~49% tests) splits into activity-lifecycle /
  pursuit / environment submodules — the test module already clusters by
  the same themes. Pure navigability. Small bonus: the verbatim
  `AbandonedChase` push duplicated in two `update_pursuit` arms.
- `harness.rs` RosterMode fold — already owner-agreed for "the next
  harness touch" (017 deferral): fold `subject` into `RosterMode` so
  `FromConfig + Some(subject)` is unrepresentable (today a release-silent
  `debug_assert`). Scope confirmed ~5 real edit sites across 3 files;
  one care: `RosterMode` serializes into run JSON, so the wire shape is
  the non-mechanical part. **Definition-of-done ask (experiments session,
  2026-07-27): a golden-file test on run JSON lands before the refactor
  starts — SATISFIED same day (PR #59,
  `crates/cloudkitty-rl/tests/run_json_golden.rs`): all three RosterMode
  wire tags + PairedDelta pinned against a committed golden, regeneration
  doctrine in the module docs. The fold is now free to ride the next
  harness touch with its wire-shape care mechanically checked.**
- `cloudkitty-py/src/lib.rs` — the agent-info schema is marshaled in two
  places that must stay identical (`info_to_py` and
  `VectorEnv::stack_infos`; the code comments warn about it). Single-source
  via a shared field-descriptor table when the Python surface is next
  touched. Smaller: `reshape+map_err` boilerplate ×3, gymnasium-or-dict
  fallback ×2.
- `action.rs` — `apply` is a ~153-line dispatcher with full arm bodies
  inline; the wire/parsing layer (own test module already) splits cleanly
  from apply/validate. The `Action`/`Activity` parallel-enum shotgun
  surgery (~10 edit sites per new activity) is real but fully
  compile-forced — navigability, not hazard.
- Client, for a polish sitting: `cat.js` coat-pattern logic scattered
  across five draw functions (new colorway = five edits → one descriptor
  table); `anim.js:pushState` is ~129 lines doing six jobs (beats,
  path-heat, element-diff all separable); `distressPatienceTicks` lives in
  two hand-synced copies (`app.js` + `anim.js` — silent-divergence trap,
  cheap fix); DPR-canvas setup duplicated across 5 sites.

### ~~Welfare pinned-streak Cuddle false-positive~~ RETIRED 2026-08-01 — premise falsified
Not a bug: busy adjacent neighbors ARE lawful cuddle relief, so the
metric is correct as written and narrowing it would be a tighten-only
regression. Authoritative rule table:
[docs/cuddle-relief-semantics.md](docs/cuddle-relief-semantics.md).
Tombstone kept because the stale premise recruited a reader once.

### Dynamic element populations (added 2026-07-20 — ideate with the owner first)
Environmental elements are effectively static: `ensure_minimums`
(`spawn.rs`) tops every type back to its configured min on the very next
environment phase, only Article I safeguard spawns ever exceed it, and
the configured max is nearly dead config — so worlds sit pinned at min
counts forever. **That was never the intended behavior.** Spec 027
(2026-08-05) took the first bites: the guaranteed 2×2 lake (water's
spatial character, maintained by the restock path), the interior spawn
preference, and `ttl_jitter`/`spread_candidates`/`edge_penalty` in
config. **Still open — the actual dynamics**: populations wandering
between min and max, expiry gaps that linger a little instead of
refilling the same tick, time-varying spawn pressure (bug flushes, chow
deliveries), water spawning adjacent to water beyond the lake. Hard
constraints unchanged: never frustrating for the kitties — the Article
I safeguard's instant relief spawn is untouchable, and min still means
min; fully deterministic through the seeded RNG; tunables named in
config (Article VI). **Design not settled — start with an ideation
conversation, as the 008 direction was.**

### Meadow finishing touches: grass detail + world edge (deferred from 008; Client thread)
The meadow itself shipped in 008 (PR #13: organic ground, ponds,
sunbeam glow, worn paths, grid demoted to `l` toggle). Three pieces
were built or attempted, judged, and scrapped for a proper art pass:

1. **Grass detail** — two attempts at scattered flora accents both read
   as sparse/odd noise. Next attempt should try denser micro-texture
   (blade clusters, mottling) rather than discrete per-tile accents,
   judged at multiple tile sizes (16×16 renders at 45px, 64×64 at 11px).
2. **A world edge** — the grass-fringe frame never landed. Consider a
   low hedge or picket frame in the cats' outline style instead.
3. **Grass sway** — removed 2026-07-22: fixed-pixel geometry read as
   stray diagonal lines at mobile tile sizes. Any return must be
   tile-proportional.

Scaffolding stands ready: `tileHash` in `client/meadow.js`
(deterministic per-tile scatter, no served data), tunables homes,
harness in `client/test-meadow.mjs`. All new grass work is judged under
all three palettes (day / golden hour / night) and at multiple tile
sizes; any new color belongs in every `MEADOW_*` set.

### HttpBehavior — the remote plugin transport
The second transport for external behavior plugins, deliberately deferred
from spec 016 (clarified 2026-07-23): build it once ScriptBehavior has
proven satisfying in practice. Everything hard already exists and was kept
transport-agnostic on purpose — the hardened proposal wire, the
`DecisionRequest`/reply-envelope JSON bodies, `try_decide`, the budget /
breaker / fallback stack. This is a thin second speaker of the same
contract: the same request and correlated envelope over HTTP POST to a
configured endpoint. Spec'd as User Story 3 / FR-007 in
`specs/016-behavior-plugins/` — start there, not from scratch.

### ScriptBehavior transport residuals (from spec 016 review, 2026-07-23)
Three bounded, low-severity residuals the deep review of PR #45 surfaced
and accepted as not-blocking. Fold these in when ScriptBehavior is next
opened (likely the HttpBehavior sitting, which shares the exchange
machinery):
1. **Grandchild pipe-inheritance thread leak.** The per-child I/O thread
   reads the plugin's stdout; killing the plugin on timeout does *not*
   close that pipe if a grandchild inherited fd 1 (a shell wrapper, a
   leftover subprocess), so `read_until` never returns and the detached
   thread lives until the grandchild exits — one stuck OS thread per
   killed process, unbounded across relaunch cycles. The common wedge
   (no grandchild) is already fixed. Deeper fix: spawn each plugin in its
   own process group (`process_group(0)` on unix) and kill the whole
   group, so grandchildren die and the pipe closes. Also correct the
   `PluginChild::drop` comment, which currently claims the thread is
   "gone the moment the stream closes" — true only absent a surviving
   grandchild. `crates/cloudkitty-core/src/behavior/script.rs`.
2. **Shared-plugin mutex burst.** The instance mutex is held across
   `recv_timeout`, so when a shared plugin wedges, every sibling kitty's
   `spawn_blocking` thread parks on `self.lock()` for up to
   `exchange_timeout_ms` (default 1000) during the one relaunch+timeout
   tick per cooldown window. Bounded and self-limiting (siblings
   fast-fall-back once the first kitty marks the process Dead), strictly
   better than the pre-fix infinite hang. Mitigation today is a lower
   `exchange_timeout_ms` when many kitties share a process — already noted
   in `docs/plugins.md`'s shared-plugin caveat. Only revisit if per-kitty
   processes or a shorter default prove wanted in practice.
3. **Exec-bit precision.** Startup validation checks `mode & 0o111`
   (executable by *anyone*), not executability by the server's effective
   user, so a script executable only by another owner/group passes
   startup then fails every spawn. The common case (forgot `chmod +x`
   entirely) is caught; closing the gap fully needs an effective-uid/gid
   check, likely more than it's worth. Minimum: a doc note that the check
   means "executable by someone", not "by us".
   `crates/cloudkitty-server/src/lib.rs`.

### Friendship / relationship tracking (+ friend-proximity preference)
The foundational social feature. Kitties develop preferences from shared
history (play, co-sleeping, grooming); "friend" stops meaning "any other kitty"
and starts meaning *that* kitty; proximity preference makes bonded pairs drift
together. Unlocks meaning for "Follow me!" and most future communications.
Design care: relationship state must serialize into snapshots and stay
deterministic.

### Age / fur / eye stats
Cosmetic identity: fur colors and patterns, eye color, age. The vector-cat
renderer (shipped in 005) already shows fur as parameters — `appearanceFor`
in `client/cat.js` is the single documented override point when served
appearance data arrives, so this item is engine modeling plus palette
wiring, not new art. Age
must never become a health mechanic (Article II: no decline, no death; cats
may age into *distinguished*, never into frail).

### Kitty "brain" indicator in the viewer (added 2026-08-01; Client thread — no server work needed)
Show which brain drives each kitty — scripted profile (`needs_driven`,
`playful`) vs. a seated policy (`policy:s6`) — as a client toggle, now
that the served world mixes them. Its 2026-08-01 blocker (the swim
animation) shipped in PR #92. **Corrected 2026-08-06: the "small server
API addition" this entry once called for already exists** — `GET
/config` serializes the whole `Config`, `kitties[].behavior` included
verbatim, and the client already fetches `/config` (app.js:573). So
this is pure client work: map kitty id → behavior string from the
response already in hand, draw a thin overlay. Follow the debug-toggle
conventions (`g`/`l`/`p` keys, keyboard-only by design, off by
default); display the config string verbatim so the label can never
drift from the seating truth.

### evals/v2 — small-world exams for the certification path (added 2026-08-06, from the consumed pre-exp-003 handoff)
Post-exp-003, Product-owned. The owner tests 20×20 and 22×22 geometry
after exp-003 and picks a new default then; every frozen `evals/v1`
exam is ≥28×28, so a small-world default would leave certification
blind exactly where the served world lives. Design question the sitting
must settle before any exam is written: `evals/v1` is frozen by sha
pins plus a CI guard, and the held-out doctrine (017 FR-007) voids
results if an exam appeared in training — so v2 needs its own
freeze-and-guard story and a clean answer to "what was this exam's
provenance" before the first candidate is scored against it. Context
that shaped this: F-014 (22×22 is sub-floor on welfare *signal*, not
just size) and the world-tuning screens (landed, re-runnable).

## P3 — simulation depth

### Kitties learn each other's traits — anticipatory cooperation (added 2026-07-21)
A 014 follow-on, deliberately out of scope until the trained meadow is
proven working well (owner decision, 2026-07-21; recorded in 014's "Not in
this feature"). Today a policy kitty's observation carries its *own* static
traits (per-need rise rates, 014 FR-005) but neighbors appear in the kitty
slots with only their live state. Adding neighbors' traits to the slots
would let a policy anticipate — "Biscuit's metabolism runs hot, leave them
the bowl" — before the need is even high, instead of reacting to the
slots' current needs (the live form of the same signal, and v1's answer).
When it comes: an observation-schema version bump per 014's extensibility
doctrine, slot width paid per kitty slot, and worth pairing with a
training-ablation check that the traits actually earn their vector space.

### ~~Chases route around friends~~ SHIPPED in spec 024 (2026-08-01)
Design detail and the axis-aligned-lane correction live in
`specs/024-wet-fur-batch/contracts/chase-sidestep.md`. Still live:
pre-024 chase-statistic baselines must be re-measured before comparing
across the break (Experiments' calibration probe is the natural place).

### Trait-scaled routing with the charge off (added 2026-08-01)
`selection::bath_ratio` scales the `water_step_cost` surcharge even when
`[water] bath_gain = 0` (identity for shipped rosters, every ratio 1.0;
documented at the definition). Two open ends, opportunistic only:
whether an ablation lever should restore flat pre-024 routing for
trait-override rosters too, and whether an extreme bath-rise override
deserves a clamp so route pricing cannot become effectively prohibitive
(the "preference, never prohibition" doctrine holds today only because
shipped ratios stay near 1).

### Cuddle puddles (added 2026-07-22)
More than two kitties cuddling or sleeping together in one pile. Low
priority, but touches real machinery when it comes: today's duets are
strictly pairwise (`Activity` carries one `duet_partner`, spec 006's
conscription and one-sided-end rules assume two), so puddles need a group
activity concept — join/leave semantics (a puddle of three survives one
kitty leaving; the last pair falls back to a duet), conscription that
doesn't let one kitty chain-conscript the meadow, and adjacency geometry
(tiles are exclusive, so a puddle is a connected blob of neighbors).
Naturally rewards warmth: cuddle relief might scale gently with puddle
size. Interplay to watch: 012's approach etiquette around a growing pile,
and 014's action menu — a join-puddle proposal is a codec version bump
under the extensibility doctrine. Viewer gets the fun part: a pile of
cats drawn as a pile.

### Food types and desirability (+ water-near-food rules)
Different chow kinds with desirability modifiers; cats prefer better food and
dislike water adjacent to their bowl. One food-system design covering both
spec items. The safeguard guarantee (Article I) must hold regardless of
desirability — a picky cat still gets fed.

### Ear / tail affect
Ears and tail express mood in the viewer (content, curious, grumpy). Pure
rendering on top of existing state; the 005 refresh shipped vector cats
partly for this — ears and tail are already animatable parameters
(`earsBack`, tail curves in `client/cat.js`), so this item shrinks to
mood-to-parameter mapping.
Deliberately kept out of the 005 refresh (2026-07-18): the bar here is
*true-to-life* — real feline ear/tail vocabulary (tail-up greeting, airplane
ears, slow flicks of irritation), worth its own unhurried design pass with
reference study, not a quick mapping bolted onto the refresh.

### ~~Rethink how water works for learned cats~~ SHIPPED as spec 024 wet fur (2026-08-01)
The charge law, the original 1.5/50 dial derivation, and the 3.5/60
re-decision (spec 026, 2026-08-05 — which supersedes the "final value
is a prereg'd exp-002 decision" note this entry used to carry) now
live in [docs/wet-fur-pricing.md](docs/wet-fur-pricing.md), alongside
the hard doctrine **water is a cost, never a wall** (owner, 2026-07-31;
pinned by spec 010's wade tests and Article I). The guaranteed-lake
companion shipped as spec 027; the organic water-adjacency variant
remains with *Dynamic element populations* (P2). Trait-scaled routing
residuals keep their own entry above.

### ~~Swim pose for wading kitties~~ SHIPPED (PR #92, merged 2026-08-04)
`poseFor` water arm + v2 `swim` layout (v1 keeps normal standing per
the owner's call); values live in `CatV2.SWIM` on main. Whether a final
owner value-judging pass in `gallery-v2.html` closes this fully is the
Client thread's call — otherwise done.

### Dynamic in-game speed changes
⚠️ Architectural string attached: the MVP API is read-only and the spec fixes
tick rate at startup. Live speed control needs a control surface (an operator
endpoint or console) and a spec amendment distinguishing *operator controls*
from *simulation mutation* — the viewer must remain unable to touch the world.
Determinism note: tick duration affects nothing in the simulation itself (only
the external-behavior wall-clock budget), so speed changes are replay-safe for
built-in behaviors.

### Additional communications
More meow vocabulary. Most valuable once relationships exist to talk about;
each new message needs a cooldown severity mapping like the existing six.

## P4 — world-scale ambitions

### Crepuscular rewards — time-of-day enters the engine (added 2026-07-22)
The engine half of the world's sky. The viewer's full day–night cycle
shipped cosmetic-only (PRs #37–#39, owner call 2026-07-22): the hour is
a pure client function of the served tick (`hourForTick`, app.js) and
the engine knows nothing. When the trained meadow wants more challenge,
promote the hour into the engine and vary RL rewards by it — kitties
are crepuscular, so dawn and dusk could pay a premium for activity
while deep night favors sleep, teaching policies a daily rhythm instead
of a flat routine. Design cares when picked up: the hour must derive
from tick arithmetic in the engine so rollouts stay deterministic and
bit-reproducible; adding it to observations is a schema version bump
under 014's extensibility doctrine; the long-run welfare bounds must
hold at every hour — variable rewards may never starve a need (Article
I outranks the reward function); and the client's `hourForTick` retires
in favor of a served hour, keeping viewer and engine on one clock.
Sequencing: the pyo3 advisory upgrade that once gated RL work shipped
2026-07-23 (spec 015) — nothing blocks this but priority. (Replaces
the old P2 "Day–night cycle and moonbeams" entry, whose viewer half
is fully shipped.)

### Kittens
⚠️ Constitution note: adding kitties is lawful — Article II forbids removal,
not arrival — but population then only ever grows. Needs a birth-rate design
with a population cap tied to world capacity, or sequencing with expanding
worlds. Kittens are small, quick, and never in danger (Article I applies from
the first tick).

### Expanding worlds
Worlds that grow at the edges as the population does. Big engine change
(spawn bounds, snapshot compatibility, viewer viewport); enables kittens
long-term.

### State sharing between worlds
Kitties visiting other worlds / servers. Largest and least-defined item;
cross-world determinism and snapshot identity are open design problems. Last
on purpose.
