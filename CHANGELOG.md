# Changelog

CloudKitty is a living world first and a software project second, so this
changelog tracks something ordinary changelogs don't have to: the world
itself. Each release entry opens with what the release *means*, then walks
the arcs of work that made it up. Pull requests are cited as references —
the story should read without them.

Because changes here can invalidate things that outlive the code — saved
worlds, trained policy artifacts, measured baselines — entries carry
**compatibility markers** where they apply:

- **`[obs-schema]`** — the observation layout policies are trained against
  changed; existing `.ckpolicy` artifacts refuse to load on the new engine.
- **`[world-fresh]`** — the world fingerprint (size, seed, roster) changed;
  a saved world cannot resume and a redeploy needs `update.sh --fresh`.
- **`[rng-sequence]`** — the order of random draws changed; every seeded
  world regenerates differently even at the same seed.
- **`[stamp]`** — the engine-defaults hash (`engine_defaults_sha256`)
  moved; measurements pinned to the old stamp are history, and baselines
  re-derive on the new engine before anything is compared against them.

The absence of a marker is a claim too: several of the largest changes
below were engineered specifically to move *none* of these, and proving
that (byte-identical outputs, unchanged stamps) was most of the work.

What was *learned* in the experiments lives in
[`experiments/FINDINGS.md`](experiments/FINDINGS.md); this file records
what *shipped*. Findings are cited by number (F-###) where they drove a
change.

---

## Unreleased

- **A patch of the meadow has bugs now.** Bugs 2.0 (spec 039): each bug
  lives its whole life inside the 4×4 world-aligned cell it was born
  in, and both critter lifetimes double to 600 ticks. The point is the
  hunt's economics, repriced without touching a single reward value:
  a bug's location becomes a durable fact a mind can learn, and the
  cell walls end the endgame dance where the last two tiles used to
  leak the catch. The measured pair-payment ceiling means hunting
  lands opportunistic and cannot land dominant — a willing friend
  always pays more. Greebles stay free-range on purpose; the tether is
  a bug-only key the config validator refuses anywhere else, and a
  one-tile cell is refused outright rather than silently freezing the
  meadow. No compatibility markers, and each absence is a proof, not a
  hope: the world fingerprint never moves (old saves resume, their
  bugs adopting the tether mid-life from wherever they stand), the
  defaults stamp never moves (verified byte-identical against main),
  and with the key unconfigured a seeded world reproduces the pre-039
  engine's 10,000-tick evolution bit-for-bit under a pinned digest.
  Acceptance economics ran as a pre-registered census grid against
  this branch before merge — Experiments' record has the arms and the
  numbers (#pending).

- **The phase-1 generation takes the seats, and the wall comes down.**
  `[world-fresh]` Six days after the say-surface froze, the schema-4
  generation certified as a composition (deploy battery 2026-08-21, all
  gates) and the shipped config seats it: Miso and Pumpkin on the two
  expanded attention minds (`attn-a1-s1-o4`, `attn-a1-s3-o4` — seated
  once now; the twin pattern retired with F-027), Biscuit keeping its
  exp-004 mind in expanded form (`e004-a1-s2-o4`), and Kittybear on
  `e006-E1-s1`, the first natively schema-4 mind to serve — seated for
  its dialect, the here-words and a meaningful mew, on the owner's
  ruling that it was worth the recert. Clementine runs scripted this
  phase; her policy mind arrives with the bugs-2.0 sequence. The three
  sources retire to `policies/retired/` with their records, each
  superseded by its own re-placed self (artifact lineage: same run,
  same mind, new surface — the spec-035 attestation and the bit-exact
  parity leg jointly prove it). Every seated artifact carries its
  registry row in the same change, and the generation-gap test swaps
  for its stronger successor: the shipped config now proves every
  named artifact opens, rather than proving none does. The rollout
  serving this roster is the `--fresh` the wall rider promised when
  Clementine's id moved the fingerprint (#280).

- **The phone was framing a keyhole, and now frames a scene.** At its most
  zoomed-in the camera would hold as few as six tiles, which on a handset is
  about three paces of meadow with a cat filling it. It now holds seven. A cat
  on a modern phone draws a little smaller for it — around 54 pixels rather than
  63 — which is still comfortably above the size the character cards are drawn
  at, and buys back a meaningful amount of world. The trade is deliberate: three
  kitties in shot is the target, and five reads as busy.

  Two things this does that the description does not suggest. It is **not a
  phone-only change** — any map narrower than about 790 pixels now zooms in
  slightly less far, so a small desktop window is affected as well as a handset.
  And on the very smallest phones the camera's zoom range closes entirely: the
  minimum and the widest view arrive at the same seven tiles, so on those
  screens the camera pans without ever zooming. Both were measured rather than
  reasoned about, and both are accepted — the range was never the point.

  The success criterion that had capped this — "a kitty is never more than twice
  as big on one screen as another" — was **withdrawn** rather than loosened, for
  a reason worth recording: no one ever experiences that ratio. Everyone has one
  device and sees one size on it. What replaces it is the bar the ratio was
  standing in for — nothing in the meadow is drawn smaller than the character
  cards the art was dialled against.

- **A landscape phone was being shown a square, and then charged rent on a
  footer it could not see.** With the camera on, a short window built a square
  canvas and let the page scroll, and — more to the point — told the camera the
  shape it was filling was square, so the camera framed a square. The kitties it
  was busy following therefore sat in the middle of a canvas more than twice as
  tall as the window, which is to say off screen: you had to scroll to find the
  thing that was already being followed. Told the truth about the window, the
  strip the camera aims at is the strip you can actually see. Cats are exactly
  the same size either way — that was never what this was about.

  How tall that strip is turned out to be a second, separate problem. The map's
  share of the screen was calculated by subtracting the header, the footer and
  the page margins from the window — but on a phone the cards sit between the
  map and the footer, so the footer is hundreds of pixels below the fold and was
  never competing for that space. On a sideways handset it wraps to 52 pixels of
  a 285-pixel screen: eighteen percent of everything, held back for something
  nobody can see. Where the cards genuinely do sit beside the map — a wide
  desktop — the footer is the next thing underneath and is still counted.

  And then the strip stopped trying to share the screen at all. **A sideways
  phone now gets a mapful of screen rather than a map that fits above the
  fold**: the canvas is the full height of the window, so one scroll takes the
  header, the sundial and the camera button away and leaves nothing but meadow,
  and a second scroll reaches the cards. Five and a quarter rows of world where
  the first version of this managed under three.

  One consequence had to be handled for it to be usable at all: the map
  re-measures the window on every single frame, and a phone browser slides its
  own toolbar away *as you scroll* — which is precisely the gesture this
  invites. Every frame of that would have thrown away the baked ground and
  every shoreline and drawn them again. They are keyed to the tile, which a
  taller window does not change, so they now survive it.

  And filling "the window" turned out to need saying more precisely. When a
  phone browser retracts its toolbar, the height the page is *laid out* against
  deliberately does not move — so a map sized to it stops short of the screen
  you can now see, leaving a stripe of card below it. The page asks the browser
  for the height it will have once the bar is gone, rather than trying to model
  a toolbar it cannot see, and fills that instead.

  With the screen finally full, how much world to put in it became a choice
  rather than a leftover — so the camera gained its first limit expressed in
  **rows**. Every other limit it has is stated in tiles across, which is fine
  until you want a sideways phone to come in closer: tightening those would
  have zoomed in every other screen too, and one of them would have taken the
  upright phone's zoom range back to nothing. Stated on the vertical, the rule
  applies only where height is the scarce axis, which is a phone on its side
  and nowhere else.

  It is set to seven rows, which is a bound rather than a magnification: it
  barely moves the phone it was measured on, and exists so that a roomier
  landscape screen cannot quietly drift to showing eight or nine. How close the
  camera actually gets is a question about what it chooses to follow, and that
  is the next piece of work rather than a number to turn up here.

- **The frame around the meadow was answering four different questions with
  one number.** On a phone the map sat on a small white mat, which separated it
  from the page — but how much separation the meadow needs turns out to depend
  entirely on the hour. At dawn the grass is already far darker than the paper
  and the mat is nearly redundant; at golden hour the two are the same
  lightness to within a rounding error and the mat is the only thing making an
  edge exist at all. It is now a hairline in the same colour the meadow already
  uses for its own soft rules, which is themed by the hour like everything else
  — so the edge strengthens and softens with the light instead of holding
  steady against it. The cards below the map also gained a little air. The mat
  is gone at every size now, not only on phones, and on a desktop that quietly
  hands the meadow back the twelve pixels of height the frame was holding —
  which is often a whole extra tile of cat.

- **The meadow was giving away a strip of itself on every phone.** The page
  held the map off the screen edge, and then — because a tile has to be a
  whole number of pixels — threw away whatever was left over, which came back
  as a second margin outside the frame. Sixteen pixels a side on a recent
  iPhone, most of it not doing anything. The page now keeps the barest inset
  in portrait, and the map takes the rest: a phone that showed a 360-pixel
  meadow shows a 380-pixel one, and a kitty grows with it. How much any given
  handset gains is a step, not a slope — the map can only widen a whole tile
  at a time — so some phones gain a tile and some gain nothing but a tidier
  edge. The cards come to the edge with the map. Landscape is untouched; its
  problem is a different one.

- **The meadow can be a window now, not only a map.** Camera mode holds
  the clowder at roughly twice the old scale and follows them about;
  turning it off returns the whole world exactly as before. It aims at
  the group's centre of mass, or at the kitty nearest it once the frame
  stops being able to hold everyone, and it declines to move at all
  while they only fidget, so it comes to rest instead of drifting.
  Clicking a kitty follows her, clicking her again or clicking the grass
  lets her go, and her card says so. The camera and the chosen kitty both
  survive a reload. Nothing about the world changes: two viewers watching
  at different zooms see the same meadow at the same tick.

- **The camera's widest view was barely a camera.** Expressing both zoom
  limits in pixels made a kitty the same size everywhere, and quietly gave up
  something the old rule had held for free: how much the camera zooms *at all*.
  On a large monitor its widest view had drifted out to 95% of the meadow — a
  kitty five percent bigger than with no camera on. The camera now guarantees
  it always draws her at least half again the size the whole-world view would,
  which on today's meadow means it never shows more than about two-thirds of
  it, and it closes in a little further than before at its tightest. Small
  screens are untouched: the rule only bites where the view was drifting too
  wide, and it retires itself once the world grows.

- **A kitty was three and a half times bigger on one screen than another,
  at the same "zoom".** The camera framed a fixed count of tiles, so how big
  she actually came out depended entirely on how wide the map happened to
  be — 34 pixels on a phone, 120 on a large monitor. Every piece of art in
  the client is a fraction of a tile, so a whisker dialled until it read at
  120px was a third of that on a phone, and no single dialling pass could be
  right in both places. The camera now zooms until a kitty is about 100
  pixels and widens until she would drop below 50, whatever the window is
  doing. (The floor target settled at 113 rather than 100, and the size band
  that justified it has since been retired — see the minimum-tiles entry
  above.) Small
  screens keep a minimum amount of meadow in shot rather than becoming a
  keyhole, and pay for it in size — the one place the rule bends. Above a
  600-pixel map the ground is also cached at a size that no longer grows with
  the display; below it the minimum-tiles rule still moves it.

- **The camera was flicking between kitties more than it should.** Once
  the frame stops being able to hold everyone it aims at an anchor kitty,
  and that anchor changes only when another is clearly more central —
  where "clearly" meant 1.5× the distance. Measured against a live world
  at five kitties that gave 4.5 anchor changes a minute against a bar of
  3, so the camera read as restless rather than deliberate. It is 2.5×
  now, which measures 2.7. Almost all of those changes were invisible
  while the frame could still hold the group, which is why the fault was
  hard to see; they stop being invisible the moment the frame is smaller,
  so this is a debt settled before it came due.

- **The ponds were still wearing daylight at midnight.** A pond's
  shoreline band and its damp lip are blurred once and kept, because
  blurring them on every frame is not affordable. What was kept included
  their colour, and the cache holding them asked only whether the water
  had moved. So the grass, the pond body and the meniscus all crossed
  into night on the world clock while the shore stayed in the afternoon,
  and stayed there. The cache now knows which sky it was painted under.

- **The surface-expansion export** (spec 035): certified minds can now
  cross a generation wall. `ckpolicy-expand` carries a pre-wall artifact
  onto the current surface deterministically — every value moved, zeroed,
  or set to the constant floor, never computed — with a structural
  attestation (bijective placement, provably-zero new inputs,
  provably-floored new head outputs) re-derived from the raw bytes before
  anything touches disk. Expanded minds are mute in the new vocabulary by
  construction (the mask cannot silence mask-legal words; the −1e4 floor
  does) and deaf per family: the MLP fully, the entity-attention family
  to kind identity (it hears "a meow," never which new word — the
  measured 1.17× residual is registered in Experiments' acceptance QA,
  exp-006 D-001). The three phase-1 candidates are generated on demand
  and land in `policies/` only at the seating PR. No behavior, schema,
  config, or stamp movement.

- **And it needs the cat to be hunting.** The same face, a second fault,
  surfaced the moment the first was fixed. `pursuit` is an intention, and
  it outlives the acts that serve it; its own documentation says it
  survives a cat stopping for a drink on the way. Asking only whether one
  exists therefore asks what the cat wants and never what she is doing,
  which the owner saw twice in an evening: a hunter's eyes on a cat
  resting beside a friend, and again on a cat grooming with a bug nearby.
  Neither was the distance gate. Both quarry really were close. Sampled
  against the running world over 945 kitty-ticks, the ticks that drew the
  face were 27 `chase` and 19 `move`, and then 6 `idle` — a cat standing
  perfectly still wearing a hunting expression. The face now needs an
  applied action that is itself a pursuit: `chase`, `move` or `play`.
  `play` earns its place because it is how a hunt ends, a cat that reaches
  its bug pouncing with it, and omitting it would strip the face at the
  moment the hunt is most plainly a hunt. The list is an allow-list rather
  than a deny-list of the sitting-still actions, so an action nobody has
  thought of yet reads as not-hunting. What it does not touch is the rule
  that an unresolvable *quarry* keeps the face, that being a different
  field and a different question (#237, with its coverage in #238).

- **The hunter's face stops outliving its quarry.** Reported as "hunter
  eyes with no bug in proximity", and it was two things at once. The
  distance gate reads `dist !== null`, so a null never gates — and both
  "I do not recognise this target" and "that bug no longer exists"
  returned null, when only the first deserves the benefit of the doubt.
  The served payload carries the whole world, so an element missing from
  it is gone rather than unresolved; and because the engine clears a stale
  pursuit at the start of the cat's next update, the tick a bug expires on
  arrives as pursuit-present-quarry-absent and drew the face at nothing.
  Every chase ending in an expiry produced one. `pursuitDistanceFor` now
  answers `Infinity` for a well-formed target the world does not contain,
  which gates on any finite threshold, while a shape it cannot read still
  keeps the face. Separately the gate goes 8 tiles to 6: 8 is manhattan on
  a 20x20 world, most of the way across it, so the quarry was on screen
  but nowhere the eye would call near. Still wider than the 4-tile pounce
  gate, so the eyes keep the lead they were given (#236).

- **A cat faces what it is eating, and the shrubs stop drifting.** Two
  things the owner saw in the live meadow on the same evening. Eating and
  drinking both take from a tile *beside* the cat — the engine's predicate
  is manhattan distance ≤ 1 — so a cat could be served mid-meal facing
  away from the pond it was drinking out of. `last_action` names no
  element for either action (the payload is a bare `{"action":"eat"}`), so
  the client works out which one by porting the engine's own predicate
  rather than guessing: nearest adjacent element of the kind, ties broken
  by lowest id, empty bowls excluded. A cat between two ponds faces the
  one the engine chose. Turning must not buy more flipping, and it does
  not: the write happens only when the facing is wrong, and then persists
  through the same memory a step uses, so a meal already facing its bowl
  stamps nothing and a served step still outranks the meal. Drinking while
  stood *in* the pond has no left-right component and is left alone.
  Separately, the lobed shrub's four leaf ticks mark the lit side, and
  they were sliding 0.29 canopy radii between dawn and dusk while the
  lobes and trunk stayed put — reported as two different faults a day
  apart, "off centre left" one evening and "off centre right" the next,
  which is one dial seen from both ends. `bushLeafSwing` exposes it and
  the owner dialled it to 0.1: about a pixel either side of centre at the
  live tile, present as a cue and gone as a displacement. The gradient was
  always carrying the direction anyway. A lab card draws one shrub through
  all four phases and measures the travel off the actual paint, since the
  dial is dead at noon and there was nowhere to judge it (#235).

- **The viewer learns the new language, and meets the fifth cat.** The
  client half of specs 033 and 034, shipped ahead of the phase-1 seating
  so none of it has to land on the same day the world turns over. Every
  word of the finalized say-surface now draws a bubble: the owner's copy
  for the Here family ("Here food!", "Here drink!", "Here warm!",
  "Here bug!"), mapped by the law each word describes rather than the
  order it was written, and the sound-named free register rendered
  as-is — `mew` says *mew*, because glossing it would reassert the
  meaning its rename stripped (FR-002b holds for a bubble as much as for
  a wire name). The reserves are written in too, so arming `trill` and
  `ekekek` stays a pure config flip. Clementine gets her white coat: the
  index into the palette table is the kitty id, so the fifth cat had been
  rendering "midnight" while the "cloud" written for her sat unused one
  slot along, and swapping the two entries was the whole fix. Her belly
  needed more: it was derived by lightening the coat toward white, which
  is a claim about headroom a near-white cat has none of, and it
  separated by 1.4 L\* — absent rather than faint. A belly is now stated
  as a separation and the direction follows the room available, so she is
  shaded toward her own furShade at 6.9 L\* while the four coats that
  shipped before her keep the exact ink they were approved with. And the
  about names the mind: "Transformer (attn-a1-s1)", composed client-side
  from the registry's architecture and the config's id, since without the
  id both attention seats read identically. Nothing here is visible on
  the served world — the box runs its pre-wall binary, so the new words
  are unreachable, no cat has id 5, and the four seated cats paint
  byte-identically (28/28 across seven poses). It is in place for the
  cutover instead of racing it (#234).

- **033 review remediation** (owner-directed medium code review of the
  wall merges; engine-side findings 3–8): pre-wall saves carrying live
  `follow_me` state now *parse* — deserialize-only serde alias, Experiments
  blessed — so the fingerprint/schema gates refuse them with the guided
  `Incompatible` error instead of a corruption-flavored parse failure
  (amends the 033 recorded consequence, which said such saves "don't
  parse"). The plugin proposal wire keeps refusing `follow_me` — wire v2
  dropped it deliberately, and the docs-examples gate caught the alias
  leaking there — so the wire now parses its own `wire_name()` vocabulary,
  immune to any persistence alias, present or future.
  `message_legal` enumerates the Want tier so an untiered future
  kind is a compile error, never a silently-dead word; the "mask and
  enforcement agree by construction" comment corrected for the Here family
  (they share the rule, not the moment — the divergence is spec-deliberate
  and only ever silences; Experiments registered the QA measurement);
  vocabulary defaults collapse to one source (container-level serde
  default), pinned by an exhaustive one-source test; the grounding
  property tests adopt the crate's `SimRng`; seven stale schema-2/3 width
  comments corrected to the schema-4 numbers. No behavior, wire, schema,
  or stamp movement.

- **The model registry** (spec 034): kitty cards can finally say what
  drives the cat. A sha256-keyed `policies/registry.toml` maps each
  certified artifact to a spelled-out display line — the architecture
  alone, worded for a general audience ("Transformer",
  "Multi-Layer Perceptron"; the owner trimmed the launch
  "architecture · recipe" format the next day, recipe staying as
  unserved provenance) — served verbatim as a new
  `behavior_description` field beside
  `behavior` on every kitty payload — "Scripted" for builtin seats, absent
  for plugins, with the raw model id still served and merely demoted in
  presentation. The registry row lands in the same PR as its artifact and
  the process can't skip it: CI fails a rowless artifact and the server
  refuses to seat one. Deliberately moves no marker: no schema pin, no
  fingerprint, no stamp — the field is additive and the registry lives
  outside the config.

- **The wall's config rider** (spec 033 window) **[stamp]**: the roster
  gains its fifth cat — **Clementine** (`[[kitty]] id 5`), the comms
  generation's always-someone-unslotted thesis made flesh, scripted until
  the phase-1 generation seats her; her white coat arrives as a
  client-side palette override. Pumpkin's character becomes a proper
  3-dial vector (eat 0.6, sleep 0.2, bath 0.1 — verified −0.11 vs
  trait-flat under policy company, zero distress), and
  `sleep_relief_sunbeam` re-pins 8.0 → 7.0 (owner preference, screened
  welfare-indistinguishable). Trait rates are stage-3 mortal: re-derived
  under the phase-1 world, pins rather than forever numbers. The new
  kitty id moves the world fingerprint, so the rollout that first serves
  this roster is a `--fresh` — the fifth cat costs the old world, and the
  owner accepted that price knowingly. (The **[world-fresh]** consequence
  lands at that future rollout, not at this merge: the served box stays
  on its pre-wall binary and world throughout the window.)

- **The say-surface, finalized** (spec 033) **[obs-schema] [stamp]**: the
  meow channel closes its vocabulary as a two-tier language, and the codec
  makes its last move before the character-era freeze. Law-named words
  mean what their predicate enforces — the six wants, the purr, and the
  new **Here family** (`here_food`, `here_water`, `here_critter`,
  `here_sunbeam`), legal exactly when the referent stands adjacent to the
  speaker, so a cat can only announce what it could itself use. The free
  register is sound-named and means nothing until the cats decide
  otherwise: `follow_me` becomes **mew** (its designed meaning died on
  contact with the cats years ago in cat time; the name now denotes the
  sound, same head index, same law), **chirp** joins active, and **trill**
  and **ekekek** enter as flag-off reserves so the post-fog
  language-capacity experiments are config flips, never codec moves.
  Every speakable kind gains a `[meow.vocabulary]` flag — legality only,
  never layout. The digest widens to 15 kinds (observation 197 → 225,
  message head 9 → 16, menu untouched at 34), all three schema pins turn
  (observation 4, action 3, mask 3), and the plugin proposal wire moves
  to v2. The engine guarantees emission-time truth only: announcing food
  and then eating the last serving is lawful, and whether hosting beats
  abandoning is the cats' economy to settle. Two living documents are
  born at the freeze: `docs/encodings.md` (the field tables, now a
  required deliverable of every schema-moving spec) and `docs/meows.md`
  (the language reference — law, intent, and observed meaning per word,
  with the Here-family cells honestly awaiting their speakers). The
  generation wall reopens with this entry: every committed artifact pins
  the previous schemas, the repo seats run scripted, the served box holds
  its pre-wall binary and world, and only client-only deploys are safe
  until the phase-1 generation certifies. Parity gate re-anchored at the
  new layout (oracle expanded from the certified attention clone;
  3.3e-6 over 144 rows, exact argmax).

## v2.8 — 2026-08-17 — the attention era seats a cross-generation roster

`[stamp]` (spec 031) — deliberately **not** `[world-fresh]`: the cutover
continued the served world's history.

The generation-4 release. Its meaning in one line: **the minds became
entity-attention transformers — identity by content, never by slot —
and the world they joined kept three generations of memory, because the
new serving machinery can run old and new artifact formats side by
side.** Candidate B (the cross-generation roster below) was certified
under the two-layer gates, seated on the owner's word at tick 790,166,
and held its 48-hour G6 soak clean: one in-band distress event in
216,000+ ticks, zero alerts on the distribution-calibrated watch, the
verdict crossed at tick 1,006,166. The tail of this entry is the
client's own era: the animation rig, the depth layer, the meadow
drifts, and the long war with the sub-pixel.

- The cross-generation roster seated: three seats hand over to the
  attention generation — Miso to `attn-a1-s1` "the cuddler", Pumpkin and
  Kittybear to `attn-a1-s3` "the doter" — the first spec-030 v3
  (entity-attention) artifacts to reach the served world, running beside
  the v2 incumbent through the version dispatch built for exactly this.
  Biscuit keeps `e004-a1-s2`, and not as a courtesy: the previous
  generation grooms the new doters back (~8.7% of its decisions), the
  trained responder culture meeting cats that finally ask, and that is
  why the owner chose the mixed composition over the all-attention one.
  Certified as candidate B (all gates, no deviations; paired team Nash
  within the 0.002 parity band of the incumbent world) in
  `experiments/attn-cert-2026-08-14/selection-crossgen.md`; the world
  continues on its snapshot — new minds wake in old bodies.

- Shared sunbeam warmth (spec 031): warmth conducts through a sleeping
  pile. A sleeper whose direct cosleep partner is settled in the pile
  (sleeping or resting, the spec-028 mutual definition) on a sunbeam tile
  now sleeps at `sleep_relief_sunbeam` — so a pile touching a beam sleeps
  at sunbeam grade, and the beam becomes a placement target for the
  cosleep behavior the world already loves instead of a losing
  competitor (the live policies sleep 21.8% of ticks, 7:1 cosleep, yet
  deliberate sunbeam sleep was effectively zero). One hop only, never
  stacked, re-checked every serviced tick; only sleepers receive it —
  a beam-resting cat warms its friend but takes only its usual cuddle
  relief. No new dial, no schema or RNG change; the deployed frozen
  policies won't seek it, so the payoff waits for the next trained
  generation, and the re-baseline rides the pre-freeze schedule the
  pipeline already requires.
- Clowder, the viewer load benchmark (spec 029): a new `crates/clowder`
  tool that asks how many concurrent viewers a server sustains and how it
  fails past that. It drives real viewer traffic in five shapes (ramp,
  spike, slow-consumer, churn, soak) plus a read-only poller mix, and
  measures everything from outside — the tick number in every payload
  gives per-connection skips, lag, and the world's observed cadence, so
  the tool needs no server or engine change. Runs write one identity-
  stamped CSV (interval rows on a single schema, derived step and run
  summaries) and name the ceiling under a configurable health definition,
  classifying any degradation and blaming the generator when the
  bottleneck is its own. Local targets by default; the live world is
  never a permitted target.
- Policy artifact v3, the entity-attention format (spec 030): a policy
  can now be a transformer encoder over per-entity tokens with pointer
  action heads, not just the v2 MLP. The motivation is F-010 — slot-
  structured encodings extrapolate undefined on rosters they never
  trained against; content tokens with a padding mask make a vacant slot
  a masked-out token instead of a novel input region. The loader supports
  both versions in one binary: a v2 artifact loads and serves byte-for-
  byte as before, a v3 artifact runs the attention forward, and any other
  version is refused by version rather than by a downstream shape
  accident. The v3 header is strict and authoritative — it carries the
  four transformer hyperparameters and nothing derivable, so a re-tuned
  model is an artifact swap, not a rebuild. The forward is hand-rolled
  scalar `f32` with a fixed reduction order, matching v2's no-BLAS
  doctrine; it is reproducible on a given binary and certified against a
  numpy oracle at 1e-4, though `exp`/`sqrt` mean cross-platform bit-
  exactness is no longer promised. No engine, world, config, or behavior
  change rides along — the observation schema, codecs, masks, and
  behavior seam are untouched, so existing artifacts and worlds are
  unaffected.
- Spec 03: the meadow grows in drifts — one low-frequency fertility
  field gates all three ground scatters, so grass, flowers and shrubs
  thicken together and the meadow has *places*, not texture; the
  density normaliser is bisected per field against the realised count
  (world-size dependent — a baked constant is right for exactly one
  world, and normalising to the nominal rate had silently cut shrubs
  38%); a second shrub species with a mix dial, ground shading that
  knows where the sun is, and the spec-03 dials in the lab (#189).
- Crossfade fix: shrubs and flowers went black mid-phase — `shadeHex`
  parses only hex while the phase mixer emits `rgb()`; the five things
  spec 03 shades now go through `mixPaletteColor`, which parses both.
  Forty-odd meadow checks all drew at blend 0; the new one draws the
  crossfade (#191).
- Three hygiene fixes: card text keeps contrast through a phase change
  (`--card`/`--ink` both invert and met at 1.17:1 mid-crossfade; they
  now swap at the halfway mark on their own 0.18s transition — the v3
  plan's ask, finally landed on the DOM side); a backgrounded tab's
  socket is latest-wins, so a two-hour backlog can no longer replay
  ~9,000 renders through the DOM; flower lower petals shade toward the
  heart, not toward grey (#193).
- Catch-up keeps a buffer: strict latest-wins (from #193) dropped
  ordinary ticks whenever a frame outlasted the 800ms tick, lurching a
  cat two tiles in one tick's ease — up to 4 pending states now replay
  in order, and only a genuine backlog collapses, bumping the
  generation so the world snaps across the gap like the reconnect path
  already did (#194).
- Served states now reach the screen through a delay line: a pair used
  to play over the *served* tick from the moment it landed, so a late
  arrival parked the cat on its tile until the next one came, and two
  arrivals in a stuttered frame crossed a whole tile in no time at all
  — the clock states were *drawn* on was the clock they *arrived* on.
  A small buffer is held and paid out on its own pace, trimmed from the
  smoothed interval between promotions (which in the long run can only
  be the rate states are produced at, so a box whose real tick differs
  from its configured one is absorbed rather than stalled against). The
  socket's queue and the backlog collapse move there too, and the cards
  ride promotion rather than arrival so they cannot lead the meadow.
  Costs about one tick of latency, which at 800ms is invisible (#196).
  Pressing `b` turns the buffer off for worlds driven far faster than
  production: below about a frame per tick no pace can help, since two
  states cannot both be drawn in one frame (#197).
- The axial whip: a cat facing north at the water, alternating
  `drinking` and `idle`, spun ninety degrees and back every tick while
  standing perfectly still — `AXIAL_POSES` is only `{walking, idle}`, so
  every other pose drops a north/south cat to a side view and the next
  pose change snaps it straight back. Measured on a live feed, 60% of
  all view changes happened with the served facing *unchanged* and 295
  of those reversed inside one tick. The drawing now turns when the cat
  turns: once a pose without an axial drawing has turned it side-on it
  stays there until it takes a step, which is the served evidence that
  it really is oriented the way an axial view would claim. Flips that
  reverse within a tick fall 295 → 81, and genuine turns are untouched
  (#198).
- A swimming cat is drawn end-on now, in both directions — the world
  swims cats north/south as often as east/west (20 wet steps against
  21, measured) but `swim` had no axial drawing, so one was always
  drawn side-on however it was going. Both directions were drawn,
  dialled and judged side by side at the live tile before either
  shipped, because they are not equally served by the pose: a swimming
  cat is mostly head — only ~6px of a 31px cat's body clears the
  waterline — and coming toward you that is the largest head in the
  vocabulary plus a whole face, while going away `paintCat` draws no
  face at all by design. Measured on a live feed after: 1,304 of 3,102
  swim frames now draw end-on, so the feature reaches the screen rather
  than shipping inert the way #182 did.

  What carries the away view is the **tail**, now held up clear of the
  surface in every direction — the posture the shallow water we
  actually built calls for, since the waterline cuts a cat at its flank
  rather than its neck. It is the only silhouette a cat swimming away
  has when everything else above water is a circle and two ears. The
  side pose changes with it (`SWIM.tailUpright` 1) so the three views
  read as one animal: a single shared height with one declared
  difference on top — `tailUprightRise`, a foreshortening allowance,
  because a tail seen broadside shows its whole length while the same
  tail end-on draws short. `tailUpright` 0 still reproduces v2.7's
  trailing tail exactly, so this is a choice and not a one-way door.

  The lab draws all three views side by side under the world's own
  waterline and clip, prints how much cat clears the water each way,
  and names which of the two dials owns the tail height at the current
  blend — one of them is always inert, and saying so is cheaper than
  rediscovering it (#199).
- The ground's tone ramp goes from 18 steps to 32, so neighbouring
  tiles differ by less and the last of the mosaic reading goes. It costs
  nothing measurable: the ramp is cached on the tone array's identity,
  so a settled phase reuses one forever and a crossfade pays 32 colour
  mixes per rebake against a 20×20 world's 400 tiles — the dial was
  always free to be finer (#200).
- Butterflies join the depth sort. They were drawn in the flat element
  pass, which runs before the cover, so every bug sat behind every shrub
  no matter where it was. A critter now takes the *cat's* ground line and
  sorts with the cats and the cover, so it passes in front of a bush and
  drops behind it again on the way north — the same rule a kitty already
  followed. Sharing one square the order is kitty, bug, bush, front to
  back, and that comes from a named rank rather than from whichever loop
  happened to push first, which is an ordering decided by accident (#201).
  Food bowls joined them (#202): cover stopped being kept off served
  elements when `occupiedTiles` narrowed to water, so a shrub rooted in a
  bowl's tile had been painting over it. A bowl takes the cat's ground
  line, since that is where a cat stands to eat from it. Front to back the
  meadow now reads cat, butterfly, bowl, shrub.
- The meadow's two ground-cover species can now stand differently, so
  it can grow small trees among flat cover: `bushLiftAlt` and
  `bushTrunkAlt` give the second species its own lift and trunk. Style
  already differed per species; how far it stood *up* did not, so both
  were flat or both were lifted and "trees among shrubs" was
  unreachable. Both dials ship equal to the primary's, so nothing
  changes until they are dialled. A lifted species still meets the
  ground where it always did: `coverSortKey` is keyed to the base rather
  than the canopy, or a tree would slide in front of the cats it stands
  behind.

  `bushTrunkWidth` sets how thick that stem is, as a multiple of the
  width each style was drawn with. The trunk style carries 0.2 canopy
  radii and the lobed one 0.13, so an absolute dial would have had to
  pick a winner and restyle the other; at 1 the multiplier draws exactly
  what shipped. It has its own `Alt` for the second species, and the
  stem thickens about its centre rather than growing out from under its
  canopy. The lab's occlusion strip draws each species in its own
  stance (#202).
- An `about` on the page: what this place is, for anyone curious. A
  `<details>`, so it opens with no script at all and still works with a
  dead socket, under reduced motion, or before `app.js` has run. It keeps
  its colour from the palette rather than a literal, since `--ink-soft`
  is one of the four tokens that *invert* across a phase (#202). It costs
  the map nothing in either state: the summary rides the subtitle's line
  and the panel opens *over* the meadow rather than pushing it down.
  That is not cosmetic — the map is square and height-bound, and
  `resizeFor` subtracts the header from its budget, so at a 20-row world
  every 20px of header is a whole pixel off the tile, and a pixel of tile
  is 20px off each edge of the map (#213).
- The face on the back of the head: `blendLayouts` builds a fresh layout
  field by field and never copied `view`, so every pose blend produced a
  layout the painter read as *not back* — and drew a full face onto the
  skull of a cat walking away, for the 260ms the blend lasted. Latent
  since the axial views landed in #187 and hidden by two things: the
  blend is brief, and until swimming became axial in #199 a cat entering
  water left the back view anyway, so the commonest blend of all could
  not show it. The fix is one field. The check is the general property —
  a blend from a pose to *itself* must draw exactly that pose — so the
  next field dropped from the blend fails whatever it is (#203).
- Cover density eased back to `bushChance` 0.0175, between where it sat
  before the tree bake and the 0.02 that bake pushed it to. On the live
  20×20 world that is 19 clumps down to 16, or 4.8% of tiles down to
  4.0%, and it keeps all five of the small trees — the drop comes out of
  the flat cover (#211).
- Cover stops looking planted. Two changes to where it grows, both in
  `bushesFor`, which is the only thing that knows where the map ends.
  The top row now grows the species that lies down: a standing canopy
  reaches about 0.38 tiles above its own tile, so a tree in row 0 was cut
  off by the edge of the world. Cover density there is unchanged — it is
  a different species, not a bald stripe. And every clump stands a little
  off the grid, up to `bushJitterX` (0.15 tiles) to either side,
  deterministic per tile and clamped so it cannot be nudged past the
  outermost tile centres. Horizontal only, deliberately: `coverSortKey`
  is keyed to y, so a sideways nudge cannot disagree with the depth sort
  the way a vertical one would (#212).
- Cover size becomes a dial and widens: `bushSizeMin` 0.2 and
  `bushSizeSpread` 0.3, so a clump runs 6.2–15.5px at a 31px tile against
  the old 8.1–13.6. The seed drives the lobe angles too, so a clump that
  differs in size differs in silhouette with it. The side-edge clamp now
  holds the *canopy* on the map rather than the centre: lobes reach about
  1.14 radii, which at the new top size is 0.57 tiles against a half-tile
  of 0.5, so the biggest clumps had started hanging off the left and
  right borders — the top-row complaint again, at a smaller scale.

  Widening alone did not fix what prompted it: two tiles that hash to
  nearly the same seed stay nearly the same at any spread, and the pair
  that read as one clump twice went from 0.2px apart to 0.4px. So a
  clump whose radius is within `bushSizeMinDiff` (0.07 tiles) of the
  previous clump of the *same kind* in its row now takes a half turn in
  seed space — provably far enough that one shift always suffices, and
  since the seed drives the lobe angles too, the pair ends up differing
  in silhouette as well as size. A tree beside a bush of its own size is
  left alone, because that reads fine (#214).
- **The hunter's face is gated on how far the quarry is**, the way the
  pounce pose already was. Measured over 4,604 cat-ticks on the incoming
  candidate roster: the median hunted quarry was **10 tiles away** and the
  commonest 12 — so a cat wore a hunting expression for a bug across the
  meadow while drawing an ordinary walk, and on **85.6%** of the ticks the
  face was on, the pose and the expression disagreed about whether a hunt
  was happening. `VIEW.hunterGateTiles` is 8, deliberately wider than the
  pounce's 4: eyes may lead a pounce, they just may not lead it across the
  whole map. Owner's number. An unresolvable quarry still keeps the face,
  the same rule the pounce follows — the gate takes it away only on
  positive evidence (#223).
- **A purr is a mood, not a request, and it stops using a speech bubble.**
  Measured on the incoming candidate roster (attn-a1, 246 ticks live):
  **98% of every meow is a purr**, and a bubble sat on screen 50.2% of
  ticks against 15.1% for the seated policy. Nine of the ten meow kinds
  are things a viewer can act on — *I want to eat!*, *Follow me!* — so
  giving a mood the same bubble meant almost every bubble carried nothing,
  which is what devalues the ones that do. Purrs now draw a small
  vibrating glyph instead, and request bubbles are untouched: they fall to
  **1.2% of ticks**, which makes a bubble worth reading again. A request
  outranks the mood where both are live, since they want the same space
  above the cat. Judged in the lab against a vibrating heart, a pulsing
  heart and sound waves; the owner took the emoji knowing the two things
  it cannot do — follow the day/night palette, and look the same on two
  machines. The buzz is a **share of the glyph with a pixel floor** — the
  same shape as the whisker stroke. A flat pixel travel was tried first
  and read cute on a big cat and frantic on a small one, which is right:
  the eye judges displacement against the thing moving, so 0.8px on an
  8.4px glyph is a 9.6% lurch where the same 0.8px on a 25px glyph is a
  3.2% tremble. Pure proportion cannot do it alone either — anchored on
  the large view the live tile lands at 0.53px peak to peak and vanishes
  under the grid — so the share sets the character and the floor keeps it
  visible at the tile the world actually draws at. Reduced motion keeps
  the glyph and stops the buzz.

  **It ships off.** Watched on the candidate roster, the drawing reads
  well and the rate does not: a heart popped in somewhere in the meadow
  **every 3 seconds — 20 a minute** — and that is distracting whatever it
  looks like. `r` toggles it live. The heart is also up for exactly as
  long as the cat is purring rather than lingering: a fixed dwell read as
  *popping*, and 3 ticks read calmer than 2, which says the appearing and
  disappearing was the distraction rather than the presence. A purr is a
  one-tick action, so the glyph tracks served state and has one end
  instead of two.

  The heart reads **`purring_until`**, the served state, not the meow. A
  purr runs 9–13 ticks and its meow is a one-tick announcement, so keying
  the glyph to the announcement drew a flash where a cat was rumbling for
  the better part of ten seconds — and since a meow is never served on
  the tick it happened, a dwell counted off its age was off by one on top
  of that. The engine documents `purring_until` as the viewer's "rumbling
  now" signal; reading it retires the dwell constant and every off-by-one
  that came with it (#223).
- **A card per kitty, and an about for each of them.** The site's About
  moved out of the header into a card of its own: in the header it either
  cost the map a row or had to overlay it, and down here it costs nothing
  — the header lost its second line entirely, which is worth about a pixel
  of tile at a 20-row world. It is static markup and a `<details>`, so it
  still works with no script at all and collapses independently of the
  kitty cards.
- Each cat now has an **about** of her own: her portrait, her name and
  epithet, the policy driving her, the owner's copy, and a row per need
  showing the rate as a bar, the number, and how far it sits from the
  world's baseline. The rates are not a presentational invention — the
  engine reads `config.kitty[].needs` over `config.needs` through
  `need_rate_for`, and the training side defines a trait as exactly
  `rate / reference_need_rate`, so the card shows the quantity the minds
  are trained against. Each need is scaled to **its own** baseline, so
  every centre mark lines up down the card and a deviation is the only
  thing that breaks the line. Bars wear the colour of the thing in the
  meadow that answers them — the bowl's clay, the pond, the bloom's gold,
  a lily pad, the cuddle heart, lavender for the soap — held fixed rather
  than read live from the palette, because the meadow's night colours are
  lit for its own ground and went invisible on a card (#225).
- It opens from a `?` in a ring, drawn in CSS rather than set as a glyph:
  Unicode's circled question mark is poorly covered and would box on some
  machines, and a drawn ring follows the day's ink where an emoji could
  not. The ring is 14px and its touch target is 23px, which one box cannot
  hold at once, because `border-radius: 50%` resolves against the border
  box and padding there grows the circle rather than the target. The
  target is a transparent pseudo-element instead. The `?` is nudged down
  0.58px: flex centres the line box, a `?` is nearly all above its
  baseline, and the resulting 0.29px bias was a whole device pixel on some
  cards and none on others (#230).
- **The gaze aims at what it can express, and no more.** Reading the two
  target shapes the client had been ignoring — `groom`'s bare kitty id, and
  eat/drink resolved from the map — took the gaze from 5.2% of cat-ticks to
  36.5%, and it was built, measured against the live world and taken back
  out. The cue is the reason: the only gaze channel above the pixel floor
  at map size is the ear lean, and it responds to the *horizontal*
  component alone, while **54% of the targets those sources add sit
  directly north or south**, where the ears do not move at all. Grooming
  was worst — cats groom side by side, so 59% of its ticks moved nothing
  and 26% leaned the ears away from where the cat faced. Chase and play,
  which stay, read at 43%. What is missing is somewhere for `gaze.y` to go,
  not more things to look at, and that is art to judge at camera zoom where
  the pupil and the head follow stop being sub-pixel (#221, #222).
- **And it aims where the target is drawn, not where it is served.** The
  looking cat's position was already the interpolated one while the
  target's was the served destination, so a cat looked at where its
  quarry *will* be — on screen, grass. Half of all gaze-firing ticks had
  a moving target, off by a median 8.1° and up to 26.6°, worst up close.
  Three rules in the same file already said drawn: the wade pose keys on
  "the tile under the DRAWN cat, not the served destination",
  `submersionFor` samples where the cat visibly is, and the depth layer
  sorts by `elementPosFor`. It also sat directly under the comment
  invoking Article V — a moving cat's served position *is* its
  destination, so aiming at it was the prediction that rule forbids. This
  is the part that stays: it makes the chase gaze — the one that already
  read well — aim where the quarry is drawn (#221).
- **The cat now does what the panel says it is doing.** `activity.state` and
  `last_action` describe different moments of the same tick — the engine
  applies every action, then clears the scenes that ended, then publishes —
  so a scene's final tick truthfully reports `last_action: eat` *and*
  `state: idle`. Both fields are right; `poseFor` read the wrong one, and
  drew a cat standing about on **13.6% of every cat-tick**: half of every
  meal and drink, and 22% of grooming. `doingFor` already followed
  `last_action`, which is the documented pattern, so the card read
  *eating 🍥* over a cat doing nothing. The applied action speaks first now,
  with the scene kept as the fallback — `Idle`, `Purr` and `Meow` name no
  pose of their own, and for those the scene still decides exactly as
  before, which is what makes this additive rather than a rewrite (#219).
- **And a nap still ends in a stretch**, which the change above quietly
  broke and a replay of the drawn pose caught: **105 stretches in a
  2,672-tick capture became 0**. The tick a nap ends is the tick the engine
  last applied `sleep`, so it started arriving at `idlePoseFor` as
  `sleep-curl` rather than `idle` — and that method's opening guard, whose
  job is to abandon a stretch once the engine asks for something, deleted
  the wake on the very tick it was recorded. It cannot simply wait for the
  next tick either: measured, the tick after a wake is a bare idle stand 3%
  of the time, so a deferred stretch is a stretch that never happens. Two
  layers, each correct alone (#220).
- Whiskers, attempt three, and this one **ships on**. The first two were
  cut and the backlog recorded that cutting again was an acceptable
  answer; the owner's read at the live tile was that they carry even at
  low resolution. Ported from kitten.me, whose trick turns out not to be
  resolution: its stroke is `max(0.8, cat × 0.018)`, so below a 44px cat
  it sits pinned at the 0.8px floor exactly as ours would. What makes it
  read is **opacity**, where a hairline is a soft hint rather than an
  aliased dotted line, and a length that runs past the head so most of it
  falls against the background rather than against fur. Baked at 0.25
  alpha, three a side, 0.2 to 1.25 head radii. Drawn inside `drawFace`,
  so a cat walking away has none without the whiskers knowing that rule
  exists. The portrait chip grew 3px because the stretch pose put a tip
  over its edge (#215).
- Nose darkness (`NOSE.darken`, 0 = the colorway's own) — a consequence
  of the whiskers rather than a separate idea, since six hairlines either
  side of the muzzle pull the eye off a pale pink nose. It resolves one
  ink for the whole muzzle: the yawn's jaw and the tongue are both mixed
  from the nose, so darkening only the triangle would have left a pale
  mouth inside a dark face the moment a cat yawned. The inner ears paint
  from the same colour and follow it too. Both this and the whiskers are
  on the face card, where a check now proves every slider is printed in
  the readout — it found `SWIM.tailUpright` had been dialled for a whole
  session and typed back by hand (#215).
- The inner ear is a shape now. It was a one-sided needle running 35% to
  100% along the ear's spine with a single nudge sideways, which at a
  31px cat is **0.71px² of paint, never wider than 0.64px** — under the
  same floor that killed whiskers twice, and visible only as a sliver of
  pink. At the owner's bake it shows **2.18px²** at the same cat, a third
  of the visible ear rather than an eighth, and 8.17px² at the 60px tile
  camera mode will reach.
- It is dialled as *fur showing*, which took two goes. The first cut gave
  it the obvious knobs — where the pink's base sits, where its point
  stops, how wide it is — and the owner's read was that they were hard to
  aim: the ear tapers, so widening the pink also closed the gap at its
  tip, and every knob moved two things. What she was actually judging was
  the fur left around it, so that is what the two dials are now, one for
  the sides and one for the tip. Holding the side gap even the whole way
  up makes the pink a blunt-ended shape rather than a spike, which is
  also what an ear looks like. Even took a second pass to mean even: an
  ear *leans*, its tip swung outward, so its two slanted edges meet its
  base at different angles and a margin stepped along that base left
  0.46px of fur on one side against 0.64px on the other. Each edge moves
  perpendicular to itself now, and the two match to within a thousandth
  of a pixel. The tip dial is measured down from where those inset sides
  meet rather than down from the ear's own point: a side margin already
  pulls the pink clear of the tip, so measured the other way the dial did
  nothing for the first 0.349 of its travel — and that dead zone moved
  every time the side dial did. Baked at `sideFur` 0.28 and `tipFur` 0,
  where the sides meet on their own and it comes to a point. It is painted **with** the ear and under
  the head, so it needs no rule about where the skull starts — solving
  for that line got the centre right and still left both base corners
  inside a round skull (#215).
- Docs: rl-training + howto-rl caught up to spec 028 (two-head wire,
  20×20, certification assumptions rewritten — the channel is
  restrained by law, not economics), and kitty-eval is a pre-seating
  smoke, not the bar: certification is the §9-harness pipeline,
  written down in `experiments/PIPELINE.md`; every doc number re-run
  for real (#190).
- Spec 028 FR-021 amended — the acceptance check evaluates within
  behavior class where demonstrator composition differs (the v4
  composition artifact), echo sites tagged; py-binding width accessors
  became properties and two stale comments were corrected (#192).

---

## v2.7.1 — 2026-08-10 — the cat becomes an animal

No compatibility markers: everything here draws pixels or records
measurements. The engine, the world, and the stamp are exactly v2.7's.

A client-only patch release — the animation handover from Design, applied
in five rounds (#182–#187), plus the first experiment records taken from
the all-policy world v2.7 seated.

### The rig (#182)

The idea the whole arc hangs on: **a pose is a position; an animal is
mostly the lag between positions** — the tail that hasn't caught up, the
head that led the turn, the ears that arrived late. None of that can live
in a pose, so a new layer (the rig) sits after the pose and after any
blend, and offsets it, springing to zero so a cat at rest is exactly the
un-rigged cat. The handoff landed as a verbatim drop (`73bc715`) with
every change on top reviewable as one range. With it: a walk that works
on every axis — closing the north/south foot-slide finding by
foreshortening, not the piston that was costed — the full pounce beat,
the hunting face, and a dial pass that baked the owner's judged values
(pounce hold/launch/land, wiggle, tread depth per context, focusLidTilt).
Biscuit got green eyes. The tail tip renders at 2.55px on a 31px cat —
the first cat-art feature to clear the sub-pixel wall.

### Four rounds of making it true

- **The hunter's face was unreachable (#183).** Found by review after
  the merge: `expressionFor` compared a quarry that arrives as an object
  (`{target: 'kitty', id}`) against the string `'element'`, so the
  headline visual of #182 had never once appeared in the live world.
- **Card portraits got an idle life (#184).** One weighted beat table,
  one beat at a time, priced *in* like the map's motion table — a
  portrait now draws nothing 79.8% of the time, and a sit, stretch,
  pounce, yawn, or ear-flick the rest.
- **The world's wake-stretch left the portraits (#185).** Owner spotted
  it by eye against the census; the census was measuring only what the
  client *schedules*. Live cats nap in exactly-5-tick bouts and wake
  every ~21s, and every wake fired an unscheduled stretch that
  out-drew the entire beat table. Portraits now ignore it; the map
  keeps it.
- **Water became a place, not a timer (#186); north and south became
  real drawings (#187).** Submersion by location, one shared surface
  line with a guarded meniscus, far-side legs, axial facings with a
  muzzle on the face. Both rounds ported by three-way merge against the
  previous drop (zero conflicts), because the bundle's `client/` forked
  before #182 — a straight application would have reverted rounds 1–3
  and every pasted dial. #187 also caught that `cat-v2.js` installs its
  namespace by name on the real page and only four symbols were being
  installed — the whole feature would have shipped inert.

### Records, no code shipped

- First measurements off the all-policy world: **the policies invented a
  contact call**. A cat drifts away from the pack, purrs at the far
  point of the excursion, and turns back — an "I'm fine, out here,"
  not a cuddle invitation — and the purring is deliberate: selective
  (the head declines ~24 of every 25 legal chances), answered, and
  load-bearing (erasing the purr digest slot changes downstream
  decisions; zeroing a null slot doesn't). Records in
  `experiments/exp-004-meow-channel/results/` (purr-deliberateness +
  purr-semantics, 2026-08-10); the contact-census tool grew the
  instruments.
- Portrait gaze tabled for its own sitting; the ear twitch stays
  (BACKLOG).
- The exp-004 policy pipeline written down as standing doctrine
  (`experiments/PIPELINE.md`).

---

## v2.7 — 2026-08-09 — the meow channel, and the world goes all-policy

`[obs-schema 2→3]` `[rng-sequence]` `[stamp]` — deliberately **not**
`[world-fresh]`

The generation-3 release, and the shortest span between tags for the
largest change of state. Its meaning in one line: **every decision is now
a pair — an activity, and a message riding along for free — and for the
first time every seat in the served world runs a learned policy.** Rolled
out 2026-08-09 via a plain `update.sh`: no `--fresh`, because the schema
break is policy-side only — the live world *resumed*, history intact,
soak clock past 215,000 ticks, with cosleeping visible in the first
snapshot.

### The Meow Channel (spec 028)

One wall crossed on purpose. `Action::Meow` retired by the Purr precedent
(parses, validates to Idle); announcing stopped costing the turn. Menu
40 → 34; message head 9 (Silent + 8 want-kinds — WantBath and WantSleep
join); observation 183 → 197 (digest v3: one coherent freshest audible
emitter, with the engine-stamped intensity); mask wire 43 = 34 ∥ 9;
artifact v2 (one trunk, two heads, one split RNG draw when sampling).
New `engine_defaults_sha256`:
`412d00e2a92e4f5a3a4f4e72caa8f0266b18455e331ed41aef3044f05e749c87`
(recorded, not triaged — baselines re-derive on this engine). Pre-028
world snapshots load and run; the committed fixture is the proof (#163).

- Message legality is engine law: a want-kind needs its need armed
  (announce_threshold 30 / hysteresis 5, updated beside distress) and
  its per-kind cooldown clear (= recent_window_ticks); Silent is never
  masked, structurally. The `[meow]` courtesy trio retired loudly;
  the sweep gained the pinned-generation exclusion manifest
  (`config-sweep-exclusions.txt`, decided with Experiments).
- Scripted cats are demonstrators now: deterministic announce (the
  lotteries died), a groom-response rung keyed on the audible
  `WantBath` alone (imitability — GroomKitty went from 0-in-800k to
  occurring by construction), cosleep routed to a friend's side when
  cuddle is real (`cuddle_real_threshold` 15), and cosleep priced by
  presence (`cosleep_drip_relief`/`cosleep_mutual_relief`, 15/15
  behavior-preserving until the pilot re-prices them).
- The distress-tick census rides every welfare report (instrument
  convention verbatim; reported, never gated).
- The batch briefly re-parked the policy seats to scripted across the
  generation gap (e003 artifacts speak action schema 1) — a parking
  that lasted exactly as long as it took a generation-3 artifact to
  certify (below).

### The first certified seating — then all four seats

exp-004 ran its preregistered arc end to end: freeze (#170), dataset v4
(#171), behavior cloning (#172), the PPO grid (#173), and the verdict
(#174) — **e004-a1-s2**, the shaping arm's seed-2 winner: 15/15 on the
settled §9.2 gate, §9.3 welfare +0.0440 over the paired baseline, zero
fallbacks under stress. The artifact landed with its certification
record (#175).

It took Miso's and Kittybear's seats first (#176) — the first certified
generation-3 seating, retiring e003-m0-g998-s3 to `policies/retired/`;
the seats-a-policy release test returned for its second tour,
superseding the generation-gap test per its own instruction. The
remaining two seats followed the same day (#178), on the 4x deployment
screen: 30 fresh seeds at 0.9499 reserved-band welfare vs the live 2+2
composition's 0.8866 — the scripted seats were the live-welfare cap —
with §9.1 water bounds PASS at the all-policy composition. Biscuit's
playful era ends; Pumpkin keeps the snacky needs override (world-law,
not behavior).

### The client: phase-4 cats, deeper ponds, the new vocabulary

The cat learned to move like a body instead of a sprite: legs pivot
inside the silhouette and the gait rides distance, not the tick clock
(#137); the pounce launches instead of switching (#152), and a chase
only draws it once the quarry is within four tiles (#157); body:head
proportion became a judged dial (#148); every soft cat got a belly
(#158); the sleep-curl head joined the head-radius band every waking
pose already kept (#180). The pond gained depth — palette, dials, and
the blur ceiling (#177), plus the lost `groupWaterTiles` call restored
(#179) — and the wading cat stopped making its own ripples (#159). The
client also learned spec 028's language: `MEOW_TEXT` gained want_bath
and want_sleep (#162).

### Housekeeping

- The changelog itself (#135): the whole story, v1.0 to v2.6, told for
  a reader — with the compatibility-marker convention this entry uses.
- exp-004 design inputs committed (#134): working notes toward making
  the meow carry more signal — explicitly inputs, not yet a design.
- Findings register housekeeping: archived findings split out, F-017
  registered (the multi-copy training collapse is largely a symmetry
  artifact), and exp-003's record corrected from a verification sweep.
- Operational, post-v2.6: the 20×20 world went live 2026-08-08 via
  `update.sh --fresh` — the first world of the canonical generation,
  and the world this release *resumed* rather than replaced.
- Refactor, no markers: `[rl]` config defaults collapsed to
  container-level serde defaults and eleven dead accessors deleted
  across core and rl — behavior-identical, stamp verified unchanged;
  also corrects `policies/README.md`'s pre-#114 claim that unknown
  `[rl.policy.*]` keys are silently inert (they refuse to load) (#142).

---

## v2.6 — 2026-08-07 — exp-003 shipped, the world remade, client v3

`[obs-schema 1→2]` `[world-fresh]` `[rng-sequence]` `[stamp]`

The biggest span in the project's history (PRs #87–#131, three weeks of
work across four parallel threads). Its meaning in one line: **learned
policies now hold both policy seats in the served world, and the world was
rebuilt around what training taught us it needed.** Rolled out to the live
site 2026-08-08 via `update.sh --fresh` — the old world's history closed,
and the soak clock restarted on a canonically generated 20×20 world.

### The roster becomes two-policy

Kittybear took seat s3 (#87), joining Miso (s6, seated in v2.5) — two
learned policies alongside scripted Biscuit and Pumpkin. From here on,
"the deployed composition" means this mix, and evaluation had to learn to
construct it (neither `--roster` flag did).

### The wet-fur batch (specs 024, 025)

Water gained a cost: standing on a water tile now charges a wet-fur
mechanic that raises the Bath need (spec 024, #90), and play relief was
split so playing in water stopped double-paying (spec 025, #93). The
client learned to show it — a swim gait for kitties crossing water (#92).
One counterintuitive result came out of tuning this: raising the wet-fur
*gain* — the dial that prices water — actually **increases** scripted
kitties' time on water, because a wet cat wants a bath and grooms where it
stands (F-016). The ceiling, not the gain, is the lever.

### exp-002 → exp-003: the observation was the bottleneck, not the reward

exp-002 (mixed-population training) closed with its central negative
result intact: training a policy against copies of itself collapses, and
it collapses monotonically with the mix — a self-interaction failure, not
a data-volume one (later refined by F-017: largely a symmetry artifact).
Its successor asked a sharper question: is the policy's water problem a
*reward* problem or a *perception* problem?

exp-003 answered it. **One observation bit — "am I in water" (spec 026,
#106) — bought what no reward dial could**: the winning candidate,
`e003-m0-g998-s3`, ended up *drier than the scripted baseline*
(2.79% in-water vs 3.44%; 0.62% lounging vs 1.50%). The preregistration
was frozen before results (#115), with water bounds defined as multiples
of a same-engine scripted baseline rather than absolutes — a construction
that twice saved a better world from being blocked by an absolute
threshold. The winner was deployed to **both** policy seats (#118).

The schema bump is the release's sharpest edge: `[obs-schema 1→2]`
stranded every schema-1 policy artifact (they exit rather than
misbehave), which is why the deploy path grew `--client-only` (below) and
why the old anchors were retired rather than re-measured.

### The worldgen batch (spec 027) and the 20×20 world

Worldgen learned placement opinions (#107): a **conditional lake** —
worlds whose water minimum allows it get a guaranteed 2×2 water square,
and resumed worlds grow one at rollout — plus an edge-avoidance penalty
on element spawns, and the last spawn constants promoted from code to
config. `[rng-sequence]` `[stamp]`: every seeded world regenerates
differently, so the measurement baselines were re-derived on the new
engine *before* the exp-003 prereg froze (the ordering exists because
exp-002's registered water gate turned out to sit below the new scripted
baseline — freezing first would have demanded the policy out-avoid its
own baseline). One batch item — a minimum same-type element separation
(item 3b) — was **proposed and withdrawn the same day** by the owner;
spec 027 records it as deliberately unbuilt.

Then the world itself moved: **24×24 → 20×20 "optE"** (#127) — water 7,
chow 6, bug 3, sunbeam 4, greeble 1. Screened 6/6 against the world it
replaced and measurably better on the deployed composition (0/30 seeds
with a distress-threshold crossing vs 1/30; worst distress 107 → 6).
The screen also taught a lesson worth recording: element *density* is a
visual metric, not a welfare one — the 16%-"busier" world has measurably
better-off cats. `[world-fresh]`.

### The config loader stops being polite

`#[serde(deny_unknown_fields)]` landed on all 27 config structs (#114)
after a near-miss in the lab: a typo'd dial (`bath_gain_ceilling`) was
silently accepted and silently ignored, and the error was caught only
because bit-identical results looked too clean to be true. Unknown keys
and keys in the wrong table now refuse to load, by name. The wrinkle:
the same TOML file is parsed by three owners (core, RL, plugins), so the
core parser recognises the other two's tables as opaque foreign tables.
Engineered to be `[stamp]`-neutral and proven so — the deserialization-
only change left the defaults hash byte-identical, so the frozen eval
exams and the re-baseline stayed pinned.

### Client graphics v3 and the card-layout arc

The viewer got its biggest rework since v2.1: a generative meadow ground
(#111, phases 0–3 of the v3 plan), then a run of layout work — cards
that collapse, animated portraits, landscape fitting to width, water
occlusion so wading kitties read as *in* the water, and click-to-toggle
panels (#116–#129, #131). All deployed. Phase 4 (cat art) and phase 5
(props/ponds) are chartered but not started.

### The deploy estate grows up

Three gaps in `update.sh`, each found by a real rollout: `--client-only`
(#105) deploys viewer assets without touching a server that can't yet
boot the newer schema; the cargo-PATH fix (#119) after a non-interactive
SSH deploy died mid-script (harmlessly — before the backup window); and
`--fresh` (#130), which retires the saved world (backup first, rename
aside, rollback renames it straight back) so a fingerprint-changing
config can regenerate instead of failing the resume guard. `--fresh` was
exercised in anger for the 20×20 rollout the day after tagging.

### Also in this release

- **Apache 2.0 license** — the repo is now formally open source.
- A 22×22 geometry screen and a resource-declutter screen both *passed*
  on welfare and were **recommended against anyway** (#101 archives the
  data): 22×22 is sub-floor on observation signal (F-014), and declutter
  spent 76% of the welfare margin for a visual preference. Screens that
  pass are not mandates.
- Repo hygiene: stacked-PR CI gap fixed (#109), backlog groomed, the
  config file's placement dials moved under a real `[elements]` header
  they had only appeared to be under.

---

## v2.5 — 2026-07-31 — the first learned kitty, the purr batch, the deployment estate

`[world-fresh]` `[stamp]`

The release where a trained policy first went live. exp-001 ran
end-to-end — dataset, behavior cloning, PPO/MAPPO arms, certification,
forensics — and its surviving artifact, **s6, was seated as Miso in the
served world** (#78): the first kitty whose mind is a neural network
rather than a script.

### exp-001: behavior cloning wins, and the collapse gets a name

The experiment's one-line outcome: **the behavior-cloned policy certified
clean and took a seat; the from-scratch RL arms collapsed**, and the
forensics (#77, #80) traced the collapse to roster-out-of-distribution
catatonia — a policy that freezes when the world contains an empty kitty
slot it never saw in training (F-010, superseding the earlier F-008
account). En route the experiment built the lab's durable tooling: the
engine-defaults stamp that pins every measurement to the engine that made
it (#61), the world-family collector, the twin probe, and `kitty-eval
--sample` (#71). Winners s3/s4/s6 all certified clean on the restored
world.

### The purr batch (specs 022, 023)

Purring became deliberate (spec 022, #79/#82): a kitty *chooses* the
quiet motor rather than it being a side effect, with a third-emitter
yield rule so purr choruses stay polite. The meow cooldown was retired
(spec 023, #84) — analysis showed it was doing nothing the turn economy
didn't already do. Soak §9.1 passed on the new shape.

### Withdrawn, deliberately: spec 021

The "welfare Cuddle" spec was **withdrawn before implementation**
(2026-07-27, parked at tag `parked/021-withdrawn`) when review falsified
its premise: busy neighbors already *are* lawful cuddle relief —
`Sleep{with}` and `Groom{target}` need only adjacency, so the "bug" the
spec existed to fix was the engine working as designed. The rule is now
durable in `docs/cuddle-relief-semantics.md`. Cheapest bug fix of the
project: zero lines.

### Estate work

- `policies/` became the committed artifact home, with s6's bytes
  verified against the training run's hash (#86).
- `kitty-eval` learned world identity (#83): certification output names
  the world it certified against, closing an ambiguity found when two
  worlds shared a config name.
- The served world was restored to 24×24 (it had drifted to 32×32),
  which is why this release carries `[world-fresh]`.
- Client, quietly: the v2 kitty portraits became the default viewer
  (footer toggle keeps v1). One dead end recorded honestly: pupil-gaze
  tracking was built, measured at ~0.24px of visible effect, and
  reverted.

---

## v2.4 — 2026-07-26 — the refactor arc complete (specs 018–020)

The three survey-ranked refactors shipped one at a time, each spec-first
and behavior-proven — **zero unratified behavior change across the arc**,
which is the entire point of the entry:

- **018** (#56): the certification CLI's four duplicated concerns
  single-sourced into `cli_support`; byte-identical output in both modes.
- **019** (#57): the need→relief pairing centralized into one exhaustive
  mapping, with score/walk/grab agreement compiler-enforced;
  bit-identical decisions throughout.
- **020** (#58): the config module restructured into
  `config/{mod,defaults,validate}.rs`, the validation catch-all dissolved
  into six section validators on a documented ordering; a 46-rule
  enumerated sweep stayed byte-identical throughout.

The by-product that mattered most: the **bit/byte-identical refactor
methodology** proved out here and became house practice — later releases
(the v2.6 strictness change especially) lean on it. This arc also
surfaced the welfare-Cuddle false positive that became spec 021's
withdrawal in v2.5.

---

## v2.3 — 2026-07-26 — the lab notebook opens

Zero engine changes — the release is the **experiments/ scaffold** (#55):
a governance rule separating the lab from the product, a findings
register opening with F-001 (two-channel credit assignment: fast for
self, slow for teammates), exp-001's preregistration with its first
honest Deviations entry, the twin probe with a first committed result,
and non-blocking drift-annotation CI. The project's working rules picked
up two clauses the same week: reach for existing code before writing new
(rule 2), and read the findings register before designing experiments
(rule 5). Specs 018–020 were chartered from a refactoring survey, setting
up v2.4.

---

## v2.2 — 2026-07-25 — the held-out evaluation suite (spec 017)

Certification stopped meaning "passes on the default world."
`kitty-eval --suite` scores a policy across **committed, frozen exam
configs** — four exams in `eval-suite-v1`: scale (48×48, 8 kitties),
scarcity at the validation floor, heterogeneity with a 40× trait spread,
and mixed-roster composition cells (guest/half/host) probing ad-hoc
teamwork via the guest-welfare differential. The suite is frozen by a
sha256 manifest verified at startup and in CI; evolution means a new
version alongside, never an edit — a discipline that later saved the
frozen exams through two engine strictness changes.

Verdicts anchor to the suite's own all-scripted baseline, never the
default world's bounds, with a per-kitty paired sign test (warn by
default, tighten-only enforcement). Also landed: `training.toml`, the
reference training world — the gym, not the bar. (#54)

---

## v2.1 — 2026-07-24 — RL hardened for round one; the meadow gets a sky

Two stories share the span. The RL surface was hardened for the first
real training round (#51–#53): a release-safe reward guard, a bounded
power-mean, unified reset-panic behavior, batch-vs-solo equivalence
tested at the Python surface, and full **PettingZoo 1.26 conformance**
behind a pinned, non-optional CI gate (the conformance work found a real
space-identity bug). Alongside it, spec 015 upgraded the pyo3 bridge and
spec 016 introduced **behavior plugins** (#45) — external brains behind a
trait, which is also where the plugin config's strict unknown-key
precedent was set.

Meanwhile the viewer became a place: night and dusk themes, a sky with
crepuscular tuning dials, mobile rendering fixes, kitty favicons, card
layout polish, and a serialize-once WebSocket optimization. The
deployment doc was written (#30) — the first version of what became the
deploy estate.

---

## v2.0 — 2026-07-23 — the world becomes a training environment

One spec, one merge, a new identity: **multi-agent RL** (spec 014, #22).
The world gained a PettingZoo `ParallelEnv` face over a pyo3 bridge,
observation schema 1, a welfare-shaped reward, and — the part that makes
it CloudKitty rather than a gym wrapper — **policy seats**: a trained
policy can be exported as a `.ckpolicy` artifact and installed as a
kitty's mind in the served world, sitting beside scripted kitties in the
same turn order under the same rules. Everything after this tag is the
consequence of that decision.

---

## v1.0 — 2026-07-23 — the living world

The state of the world at first tag (specs 001–013): a meadow grid
served over WebSocket to a vanilla-JS viewer, inhabited by kitties with
**needs** (thirst, hunger, play, sleep, bath, cuddle) that decay and
demand relief, **scripted brains** (needs-driven and playful) choosing
activities with real durations, **meows** as the signal vector between
kitties, purring, approach etiquette, water-averse pathing (a kitty
wades only when water is the only way forward — an invariant every later
water feature had to preserve), a **fair turn order** so no kitty
systematically moves last, and **welfare instrumentation** — happiness
tracking with anti-lock-in dynamics (spec 004) and the distress
thresholds that every later certification gate builds on. The world
persists as a snapshot and resumes across restarts; elements (water,
chow, bugs, sunbeams) spawn to configured minimums with jittered TTLs.

The versions before 1.0 are the road to exactly this; the specs
(001–013) are the honest record of how it got here.
