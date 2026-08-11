/**
 * CloudKitty's animation layer (spec 005).
 *
 * Everything Article V scrutiny cares about lives in this file: what may
 * move, when, and why. The rules, from contracts/viewer-contract.md:
 *
 *  - Render only what was served. The screen shows a blend of the two
 *    newest served states at a progress given by the local clock and the
 *    served tick interval -- plus beats derived from differences between
 *    those states. Nothing else.
 *  - Never extrapolate: progress clamps at the newest state. A late tick
 *    means the world holds still, never a predicted step.
 *  - Newest wins: a fresh state preempts any in-flight animation.
 *  - Snap across discontinuities: first paint, reconnect, hidden-tab
 *    return, non-consecutive ticks, roster changes, teleport-sized jumps.
 *
 * The pure logic (`Presentation`) is DOM-free and testable; the `anim`
 * object at the bottom wires the browser (rAF loop, reduced-motion media
 * query, page visibility).
 */

/**
 * Every new visual tunable, named in one place (FR-017, Article VI). The
 * two `*Fallback` values are stand-ins for served configuration and are
 * replaced by /config when it lands.
 */
const VIEW = Object.freeze({
  // Server-owned values (with their named stand-ins).
  tickMsFallback: 800, // easing duration <- config.world.tick_ms
  distressPatienceFallback: 60, // thought bubble <- config.viewer.distress_patience_ticks

  // Interpolation & element comings-and-goings (US3).
  elementFadeShare: 0.4, // share of a tick over which spawns/expiries fade
  // Critters (bug/greeble) glide between served states like kitties do
  // (007 refinement, 2026-07-20 -- the hover-bob alone left the hops
  // jerky). Anything farther than a skitter is a different moment: snap.
  critterGlideMaxTiles: 2,

  // Idle life (US4).
  idleMotionPeriodMs: 5200, // one idle slot about this long
  idleMotionWindowMs: 420, // an ear twitch (and v1's snap blink) lasts this
  breathePeriodMs: 3400, // the slow ambient cycle for resting poses

  // What breaks up the rhythm (2026-08-06). The slots used to run a strict
  // blink -> flick -> twitch rotation, every cat on the same clock and
  // every motion starting exactly on the beat, which measured as a literal
  // metronome: all four cats blinking at 13800ms intervals, zero spread.
  // Each slot now draws a motion from these weights and starts it somewhere
  // inside the slot. All of it is hashed from (id, slot), never random, so
  // `motionFor` stays a pure function of (id, pose, now) -- still frames,
  // reduced motion and the harness all depend on that.
  // Owner-dialled 2026-08-06, and the intent matters more than the
  // numbers: a new viewer should think "did that cat just slow blink?",
  // watch for a while, and find the occasional blink or ear twitch --
  // common enough to be really there, rare enough to stay a treat. So the
  // long quiet stretches are the point, not a shortfall. Measured over 30
  // minutes, the gaps where all four cats are still run 1.79s +/- 1.47s
  // (median 1.54s, p99 6.3s); before any of this it was a flat 0.9s.
  // Anything that makes the meadow busier is trading that feeling away.
  idleBlinkWeight: 30,
  idleEarsWeight: 26,
  // Added 2026-08-10, on the owner's call that the measured rarity above
  // was about BEATS -- discrete things that punctuate -- and that
  // continuous motion is exempt and wanted. These two are still beats, so
  // they are priced as beats: together they take 20 of the 100 weight,
  // which lengthens the all-four-cats-still gaps by roughly a fifth
  // rather than filling them in. The continuous work (tail, head, gaze,
  // ears) is not scheduled here at all -- it never stops, and it never
  // punctuates, so it cannot spend this budget.
  idleScanWeight: 14, // a slow look at something, or nothing
  idleYawnWeight: 6, // rarest on purpose: a yawn you see often is a tic
  // A slot where nothing happens. It is what makes the others feel
  // unscheduled -- and it is a real nothing, not the vestigial tail flick
  // it replaces, which quietly restarted the breathing cycle at 8x speed
  // for a tail-tip sway of 0.4px at a live 33px cat.
  //
  // 35 -> 24 (2026-08-10): the key was declared TWICE when scan and yawn
  // landed, 24 above and the old 35 here, and the last one wins. The budget
  // came to 111, so scan and yawn were added ON TOP of the rarity budget
  // instead of priced into it -- the one thing the handoff said it had not
  // done. A test now asserts the five weights total 100.
  idleRestWeight: 24,
  // 0 = every motion on the beat (the old behaviour), 1 = anywhere in the
  // slot it still fits. The motion can never overrun its slot either way.
  // Half, owner-dialled: enough to break the metronome without letting a
  // motion drift so far into its slot that two land back to back.
  idleJitter: 0.5,
  // Per-cat tempo, +/- this share. Four cats on one clock read as one
  // animal drawn four times; a little spread reads as four animals.
  idleTempoSpread: 0.15,

  // v2 live motion -- every value owner-judged in the gallery-v2 motion
  // lab (2026-07-29; the settle was slowed 180→400ms on owner feedback).
  // Consumed only when the vocabulary dispatcher installs drawCatTween
  // (the v2 kitties); v1 keeps its pose snap and its snap blink.
  poseBlendMs: 260, // generic pose-space blend on any pose change
  // Wetness is a fact about the tile, not the pose (owner, 2026-08-04):
  // a cat drinking in a pond is still standing in water. It fades on the
  // same clock as a pose blend so a shoreline crossing does not pop.
  wetFadeMs: 260,
  /**
   * How long a coat stays visibly damp after leaving the water.
   *
   * Asymmetric with `wetFadeMs` on purpose: a cat is wet the instant it
   * is in water, and dries slowly. This is the ONLY water cue that
   * outlives the pond -- see `wetFor`, and the invariant recorded there.
   */
  furDryMs: 2800,
  /*
   * ONE water level, for every pose (owner, 2026-08-10).
   *
   * A per-pose surface was tried first -- 0.72 wading, 0.82 floating, on
   * the reasoning that a cat standing in shallow water and one floating in
   * deep water do not sit at the same height. That is true of real ponds
   * and wrong for this one: the meadow's water is one depth everywhere, so
   * two levels made the same pond look like two, and the level changed
   * under a cat that had only changed what it was DOING.
   *
   * So `waterline` above is now the whole story, and the poses may not
   * encode depth of their own -- see cat-v2's SWIM, which had to be raised
   * to sit at the same height as the land poses once it started being
   * clipped like them. The rule: the WORLD owns the water level, the POSE
   * owns what the cat is doing at it.
   */
  /**
   * Where the pond surface cuts a cat standing in it, in the cat's own
   * unit space (0 top, ground at 0.88) -- BACKLOG P1, the owner's idea.
   *
   * The cat is clipped below this line, so a cat on a water tile reads as
   * half-submerged whatever pose it is in. That is the point: `poseFor`
   * deliberately lets drinking and grooming outrank the wade, so those
   * cats keep a land pose while standing in a pond, and occlusion is what
   * makes them look like it -- one clip instead of a water variant of
   * every activity.
   *
   * Rides `wetFor`, the same eased 0..1 the shadow and ripple already
   * use, so the surface rises and falls with the shoreline crossing
   * rather than popping, and the three cues can never disagree.
   *
   * NOT applied to the swim pose: that one earns "underwater" from its
   * own low flat silhouette (see cat-v2's SWIM), and clipping it too
   * would submerge a cat that is already drawn sunk.
   *
   * 0.72 owner-picked 2026-08-07 from a sheet of six depths rendered
   * through this exact path. It cuts across the bottom of the body
   * rather than sitting under it, so the cat is clearly IN the pond
   * instead of on it, while the grooming or drinking pose stays legible.
   * The two depths either side were both rejected for real reasons:
   * 0.76 only hides the legs and is easy to miss, and 0.62 -- which
   * would have matched SWIM's own surface, so wading and swimming cats
   * shared one water level -- makes a standing cat look like it is
   * swimming. One water level lost to pose legibility, deliberately.
   */
  waterline: 0.72,
  /**
   * How close a chase's quarry has to be before the cat is drawn
   * mid-pounce, in tiles (Manhattan, like every decision distance).
   *
   * `Action::Chase` is lawful at any distance -- the engine's selection
   * scans the whole world -- so a cat crossing the map after a bug used
   * to be drawn mid-pounce the entire way, hiding the walk. Measured on
   * 2700 live kitty-ticks: gating at 4 moves pouncing 27.9% -> 25.3% and
   * walking 28.1% -> 30.5%, which is smaller than it sounds because half
   * of pouncing is PLAY (adjacent by lawfulness, so never gated) and the
   * median chase is only 2 tiles. 19% of chase runs reach past 4, about
   * one every 12 seconds somewhere on the map.
   *
   * A chase whose target cannot be resolved -- caught or expired this
   * tick -- keeps the pounce. The gate only ever takes it away when the
   * quarry is positively known to be far, which is also what keeps v1
   * callers, who pass no distance at all, drawing exactly as before.
   */
  pounceGateTiles: 4,
  arriveBlendMs: 340, // the walking -> standing blend, paired with the settle
  settleMs: 400, // landing squash, concurrent with the arrive blend
  settleDip: 0.05, // peak vertical squash of the settle
  blendTickShareCap: 0.45, // a blend never outlasts this share of a tick
  // The cat "I love you", re-dialled in the v2 lab (owner, 2026-08-06):
  // the lid eases down, holds, and releases. The hold carries the gesture
  // and was the value that moved -- 150ms was long enough to see but not
  // to mean anything, and at 550 the closed eye is held rather than
  // passed through. 1550ms total, well inside the 4600ms idle slot.
  slowBlinkDownMs: 550, // the lid eases down ...
  slowBlinkHoldMs: 550, // ... holds ...
  slowBlinkUpMs: 450, // ... and releases

  // Idle motion durations (2026-08-10). Both comfortably inside the
  // 4600ms slot, for the same reason the slow blink has to be: `at`
  // arrives modulo the period, so a motion longer than its own slot
  // would always be in progress.
  scanMs: 1500,
  // The yawn, as three spans rather than one duration (2026-08-10). Same
  // shape as the slow blink, and for exactly the same reason: the weight
  // of the gesture is in the HOLD. The first cut had none -- it opened
  // over 400ms straight into a 600ms close -- and a gape with no pause at
  // full stretch is a mouth opening and shutting, which reads as eating
  // rather than yawning (owner, 2026-08-10). 1420ms total, comfortably
  // inside even the fastest cat's 4420ms slot.
  yawnOpenMs: 340, // the jaw drops ...
  yawnHoldMs: 620, // ... and stays down, which is the yawn ...
  yawnCloseMs: 460, // ... then eases shut

  // The on-the-spot turn (2026-08-10). Short: this is a cat pivoting on
  // its front feet, not a considered about-face, and anything longer
  // reads as the cat sliding through a wall.
  turnMs: 200,

  // Anticipation and overshoot on pose blends (2026-08-10). Dialled well
  // down from the usual 1.70158 -- see easeBack.
  blendBack: 0.5,

  // The waking stretch, in TICKS rather than milliseconds (2026-08-10).
  // tick_ms is served, and a stretch pinned to the wall clock would span
  // a different number of served DECISIONS on a faster or slower world --
  // so the one thing that must not drift, how many instructions can land
  // while the cat is mid-stretch, would be exactly the thing that did.
  // Two ticks is long enough to read as luxurious and short enough that
  // the engine's next instruction lands after it, not through it.
  stretchTicks: 2,

  // How often an idle cat sits down instead of standing. `sitChance` is
  // drawn once per `sitPeriodMs`, so a cat that stays put long enough
  // will sit, get up, and sit again -- all of it hashed from (id, slot),
  // so it stays a pure function of time and the pose blend gives the
  // sitting-down and standing-up for free.
  //
  // `sitAfterTicks` is what makes it look considered. The hash decides
  // WHETHER a stretch of time is a sitting one; this decides whether the
  // cat has been still long enough to mean it. Without it, a one-tick
  // pause mid-walk lands a whole sit-down and stand-up inside 800ms,
  // which reads as a stumble rather than as a decision.
  sitPeriodMs: 26000,
  sitChance: 0.38,
  sitAfterTicks: 3,

  /* The card portrait's POSE BEATS (2026-08-10). PORTRAITS ONLY -- the
   * meadow must never draw these.
   *
   * A pounce in the world is a served fact: the engine says a cat is
   * chasing and the renderer draws it. Inventing one on the map would be
   * the client asserting something the world did not say, which Article V
   * forbids. The portrait is different, and already documented as
   * different: it is deliberately NOT the cat's real pose (owner,
   * 2026-08-07) but the cat AT REST, which is what lets it carry idle
   * motion at all. A cat play-pouncing or sitting down at rest claims
   * nothing about the world.
   *
   * Why they live off the served tick: on the map a pounce has one 800ms
   * tick to happen in, which is why its load is 240ms and the wiggle
   * quantises to a single rock. A portrait runs on the frame clock, so the
   * whole beat is legible here and nowhere else.
   *
   * Why they are NOT gated on stillness the way the map's `sit` is:
   * measured on the live world, a cat never has nothing to do for more
   * than 2 consecutive ticks (107 runs of one, 3 of two, none of three) --
   * so `sitAfterTicks: 3` is unsatisfiable and the map's sit can never
   * fire. That gate is right for the map, where a busy cat should not sit
   * down. It is wrong for a portrait, which is at rest BY DEFINITION.
   *
   * One weighted draw per period, so a sit and a pounce can never collide,
   * and the weights are a share of 100 the way the motion table's are. */
  cardBeatPeriodMs: 7000,
  /* ONE table, one beat at a time (2026-08-10, owner's call). The portrait
   * used to run two schedulers side by side -- the motion slots and a pose
   * clock -- which meant a cat could yawn mid-pounce, and 16 different
   * pose x motion pairs existed that nobody had chosen. Sequencing them
   * instead is the same move the sit chain made: one thing at a time, and
   * the next thing after it.
   *
   * The slot has to fit the LONGEST beat, which is the 5.8s sit chain; at
   * 7000ms everything else has slack. Weights are a share of 100, like the
   * map's motion table -- new beats are priced IN, never added on top,
   * which is the mistake the handoff made with scan and yawn.
   *
   * These are the PORTRAIT's. The map keeps `motionFor` and its own slots:
   * a map cat is idle only 24% of the time and in isolated single ticks, so
   * it needs short beats that fit in a tick, not a 5.8s chain. */
  cardBlinkWeight: 30,
  cardEarsWeight: 14,
  // 0 (2026-08-10): the gaze is TABLED for a longer session, so the card
  // does not scan for now. Kept as a weight rather than deleted -- turning
  // it back on is one number, and the branch stays exercised. See BACKLOG:
  // the look is one coupled gesture (gaze drives pupils, head and ears) but
  // only the ears clear the visibility floor at portrait size, so it wants
  // dialling as a whole rather than switching on as-is.
  cardScanWeight: 0,
  cardYawnWeight: 5,
  cardSitWeight: 12,
  cardPounceWeight: 7,
  cardRestWeight: 32, // 20 + the scan's 12, so no other beat's rate moved
  // The sit holds, then the cat gets up THROUGH a stretch -- which is what
  // a cat actually does standing up, and the reason `stretch` is authored
  // to leave and return to neutral (it is 0px off a resting cat at both
  // ends). The chain is sitHoldMs + one stretch.
  sitHoldMs: 4200,
  // The pounce beat, and the two dials it needs that the map's cannot
  // share: at 2x the map's beat the same rock rate is a wallow, and the
  // same tread depth that reads at 47px is 0.62px at 31.
  playBeatMs: 1600,
  playWiggleHz: 3.9,
  playSway: 0.06,

  // Beats (US5).
  // The observed drop is relief minus that tick's need rise, so the
  // threshold must sit below the smallest sparkle-worthy relief: cuddle at
  // 15/tick lands as ~14.6. Kept above solo play (~9.6) and sleep (~7.7),
  // which stay sparkle-free.
  reliefSparkleDrop: 12, // need-points a drop must exceed to sparkle
  sadBeatMs: 1600,
  sparkleMs: 1000,

  // Ambient life & juice (US6) -- each effect individually disableable.
  ambient: Object.freeze({
    waterShimmer: true,
    // The rings a wading cat pushes out. OFF since 2026-08-09: the pond
    // restyle gives the water its own surface motion, and two ring sets --
    // the cat's and the water's -- read as a mistake rather than as depth.
    // The cue it replaced is not lost: `wet` also fades the ground shadow,
    // and the waterline clip already reads as submersion. Its own comment
    // always called it a first pass pending exactly this work.
    wetRipple: false,
    // The damp coat: darker, flatter fur that outlives the pond. Tried
    // 2026-08-10 and OFF by the owner's call the same day -- the
    // coloration was not wanted. Kept behind the flag rather than deleted,
    // beside its sibling water effect, so the lab can put it back.
    //
    // Nothing about the water FIX depends on this. Submersion is spatial
    // and drives every piece of geometry; this was only ever the optional
    // colour half, and with it off leaving the water simply has no
    // lingering cue -- which is what shipped before.
    wetCoat: false,
    sunbeamPulse: true,
    dustMotes: true,
    cloudShadows: true,
  }),
  ambientPeriodMs: 5200,
  cloudPeriodMs: 60000,
  bubblePopShare: 0.35, // share of a tick a speech bubble spends popping in

  // Props (spec 007, FR-012): timing periods plus the drawing-side values
  // props.js's PROP_DEFAULTS carries when this layer is absent (the
  // standalone gallery). This is the full set propTunables() serves, so it
  // must stay a superset of PROP_DEFAULTS.
  props: Object.freeze({
    flapPeriodMs: 900, // one leisurely wingbeat cycle
    panicMultiplier: 2.2, // flap-rate multiplier while hunted
    bobPeriodMs: 2600, // the hover's slow breathe
    bobAmplitude: 0.035,
    hoverLift: 0.06,
    wispBobMs: 3800, // the greeble wisp drifts slowest of all
    wispBobAmplitude: 0.02,
    heartPulseMs: 1400,
    heartPulseScale: 0.08,
    zDriftMs: 2800,
    zRise: 0.08,
  }),

  // The meadow (spec 008, FR-010): per-layer availability flags plus every
  // ground number, named. meadow.js's MEADOW_DEFAULTS carries the
  // drawing-side values when this layer is absent (the headless harness);
  // this is the authoritative set, so it must stay a superset of
  // MEADOW_DEFAULTS.
  meadow: Object.freeze({
    ponds: true, // merged smooth-shored water (off: per-tile pools)
    glow: true, // sunbeams as radial light (off: plain warm tile)
    paths: true, // whether the worn-paths overlay is available at all
    gridOverlay: true, // whether the grid debug overlay is available at all
    toneSteps: 18, // steps in the ramp blended through the grass tones
    toneCells: 3, // tiles per noise cell: how broad a grass blotch is
    jitterCells: 1.7, // and the finer lattice the brightness grain rides
    toneCells2: 7.5, // a second, broader tone field over the first
    groundBlurTiles: 0.32, // softens the tone mosaic; detail draws on top
    groundWashSun: 0.3, // the field-wide light wash, keyed to shadowLean
    groundWashShade: 0.16,
    jitterAlpha: 0.05, // peak alpha of the per-tile brightness jitter
    patchChance: 0.118, // share of tiles carrying a worn-earth or moss patch
    patchEarthAlpha: 0.03,
    patchMossAlpha: 0.05,
    // Cover grows in DRIFTS (spec 03). Mirrors MEADOW_DEFAULTS -- the
    // superset assertion in test-meadow.mjs fails on drift.
    fertilityCells: 5.5, // tiles per fertility blotch; larger = broader passages
    bladeFertPower: 2,
    bloomFertPower: 3,
    bushFertPower: 4,
    bladeChance: 0.55, // tiles with a tuft of grass
    bladeAlpha: 0.38,
    bloomChance: 0.05, // tiles with a flower
    bushChance: 0.015, // tiles with a clump of tufted ground cover
    bushAlpha: 0.9, // and how strongly it reads against the grass
    // 'cover' | 'tuft' | 'bramble' (flat) | 'shrub' | 'grown' | 'trunk' |
    // 'tall' (standing). Judged in gallery-meadow.html.
    bushStyle: 'lobed',
    bushStyleAlt: 'trunk', // the second species, when a meadow grows two
    bushStyleAltShare: 0, // 0 = primary only, 1 = alt only, between = a mix
    bushTrunk: 0, // how much stem the stemmed styles draw; 0 is none
    // The shrub's shadow, damped against the cats': a squat canopy sits
    // close to the ground, so it stretches far less and needs no alpha
    // falloff. Only the LENGTH is damped -- the lean also anchors the
    // sun-side edge to the caster, and damping that recentres it.
    bushShadowLean: 1, // gain on the anchor: 1 keeps the sun-side edge on the shrub
    bushShadowLength: 0.3, // and of its stretch past the caster
    bushShadowAlpha: 1, // no thinning: contact, not a smear
    bushLift: 0, // how far a shrub's canopy stands above its base, in radii
    bushBase: 0.72, // where it meets the ground, in tiles from the tile's top
    // How far the canopy's height pushes its shadow along the lean. Kept
    // small: a rooted thing's shadow leaves its base, and pushing it far
    // is precisely what makes a bush look airborne.
    bushShadowThrow: 0.25,
    // The shoreline. Corners are rounded into arcs first and the wobble
    // rides on the finished curve (meadow.js buildPondPath); before, the
    // wobble subdivided the edges and capped the radius at 0.25 tile
    // whatever this said.
    shoreRounding: 0.35, // pond corner rounding, in tiles
    // 0 since the pond restyle -- see MEADOW_DEFAULTS for why.
    shoreWobble: 0,
    shoreWobblePeriod: 0.35, // and its wavelength around the perimeter, in tiles
    // Scales the OUTWARD bulges only: bays cut the full `shoreWobble`,
    // headlands reach this share of it. See meadow.js `wobbleAlong`.
    shoreBulgeEase: 0.75,
    shoreOverdraw: 0.1, // push the whole outline out this far, in tiles
    lilyPadMinTiles: 4, // ponds at least this big carry a lily pad
    // Pond depth (design handoff spec 02). Reasoning lives beside the
    // originals in meadow.js's MEADOW_DEFAULTS; these must match it.
    pondDepthBlurTiles: 0.95,
    pondDepthBlurClamp: 1.8,
    pondLipBlurTiles: 0.42,
    pondLipAlpha: 0.8,
    meniscusWidthTiles: 0.058,
    causticLinesPerTile: 1.6,
    causticLinesMax: 4,
    causticAlpha: 0.055,
    causticAmplitude: 0.025,
    glowRadiusTiles: 1.4, // sunbeam glow radius, in tiles
    glowAlpha: 0.6, // overall glow strength
    pathHeatCap: 12, // worn-path heat ceiling per tile (memory, not display)
    pathFullHeat: 3, // passes at which a trail draws at full tint
    pathHalfLifeMs: 60000, // trail fading half-life
    pathVisibilityFloor: 0.4, // decayed heat below this draws nothing
    pathTintAlpha: 0.5, // trail opacity at full heat
  }),
});

/** Worn-path heat after read-time decay (spec 008 research R6): a pure
 * half-life curve, so fading needs no timers and no per-frame writes. */
function decayedPathHeat(entry, now) {
  return (
    entry.heat * 0.5 ** ((now - entry.stampedAt) / VIEW.meadow.pathHalfLifeMs)
  );
}

function easeInOutCubic(t) {
  return t < 0.5 ? 4 * t * t * t : 1 - (-2 * t + 2) ** 3 / 2;
}

/** The motion lab's smoothstep: gentle at both ends. Pose blends, the
 * slow-blink lid, and the landing settle all ease through this. */
function easeSmooth(t) {
  return t * t * (3 - 2 * t);
}

/**
 * Named channels for the idle hash. Same discipline as the meadow's
 * MEADOW_SALTS: each scatter gets its own channel, because two draws off
 * one channel correlate and the correlation is what reads as a pattern.
 */
const IDLE_SALTS = Object.freeze({
  tempo: 1, // each cat's own clock speed
  pick: 2, // which motion a slot gets
  offset: 3, // where in the slot it starts
  side: 4, // and which ear a twitch belongs to
  look: 5, // where a scan looks
  sit: 6, // whether an idle cat is sitting this stretch of time
  play: 7, // and whether a card portrait play-pounces in one
});

/**
 * Deterministic 0..1 from two small integers and a salt. Hashed rather than
 * random so `motionFor` stays pure: a still frame, a reduced-motion frame
 * and a test all have to be able to ask what a cat is doing at time T and
 * get the same answer, and an RNG would buy the same look and cost that.
 *
 * meadow.js has `tileHash` doing the same job for ground scatter, and one
 * hash would be better than two -- but anim.js currently depends on
 * nothing, the motion harness evals it on its own, and motion reaching into
 * ground art for a hash is the wrong direction for that dependency to run.
 * Four lines is the cheaper price. If a third caller turns up, lift both
 * into one file rather than adding a third.
 */
function idleHash(a, b, salt = 0) {
  let h = (a | 0) * 374761393 + (b | 0) * 668265263 + (salt | 0) * 2246822519;
  h = (h ^ (h >>> 13)) * 1274126177;
  return ((h ^ (h >>> 16)) >>> 0) / 4294967296;
}

/** This cat's own idle tempo. Constant per cat, so the slot maths stays
 * modular arithmetic on a fixed period rather than accumulated time. */
function idlePeriodFor(id, dials = VIEW) {
  const spread = (idleHash(id, 0, IDLE_SALTS.tempo) * 2 - 1) * dials.idleTempoSpread;
  return dials.idleMotionPeriodMs * (1 + spread);
}

/** Which motion this slot gets, drawn from the weights. A table rather
 * than a chain of ifs since 2026-08-10: adding a fourth motion to the
 * chain meant restating the running total in three places, which is the
 * shape of bug that silently reweights everything downstream of it. */
function idlePickFor(id, slot, dials = VIEW) {
  const table = [
    ['blink', dials.idleBlinkWeight],
    ['ears', dials.idleEarsWeight],
    ['scan', dials.idleScanWeight],
    ['yawn', dials.idleYawnWeight],
    ['rest', dials.idleRestWeight],
  ].map(([kind, w]) => [kind, Math.max(0, w || 0)]);
  const total = table.reduce((sum, [, w]) => sum + w, 0);
  if (total <= 0) return 'rest';
  let draw = idleHash(id, slot, IDLE_SALTS.pick) * total;
  for (const [kind, w] of table) {
    if (draw < w) return kind;
    draw -= w;
  }
  return 'rest';
}

/**
 * How far into the slot the motion starts. Bounded by the slack the slot
 * has left after the motion's own length, so jitter can move a motion
 * around inside its slot but can never let one overrun into the next.
 */
function idleOffsetFor(id, slot, period, durationMs, dials = VIEW) {
  const slack = Math.max(0, period - durationMs);
  return idleHash(id, slot, IDLE_SALTS.offset) * slack * dials.idleJitter;
}

/**
 * The slow-blink lid at `at` ms into a blink, or undefined once the blink
 * is over. Down, hold, release -- the "I love you" envelope. The three
 * spans are dialled independently and the weight sits in the hold: the
 * gesture is the held closed eye, not the travel to it.
 *
 * Pulled out of `motionFor` so the v2 lab can drive its Slow blink card
 * through the shipping envelope instead of restating the shape and the
 * numbers, which it used to do -- a second home for values that are meant
 * to be judged in the lab and pasted back is the one place drift is
 * guaranteed to start. `dials` exists for that lab: VIEW is frozen, so the
 * sliders need a bag of their own to write to, and passing it here keeps
 * the shape shared even while the values differ.
 *
 * The three spans must stay comfortably under `idleMotionPeriodMs`: `at`
 * arrives modulo that period, so a blink longer than its own slot would
 * always be in progress and the eyes would never settle open.
 */
function slowBlinkLid(at, dials = VIEW) {
  const down = dials.slowBlinkDownMs;
  const hold = dials.slowBlinkHoldMs;
  const up = dials.slowBlinkUpMs;
  if (at < 0 || at >= down + hold + up) return undefined;
  if (at < down) return easeSmooth(at / down);
  if (at < down + hold) return 1;
  return 1 - easeSmooth((at - down - hold) / up);
}

/**
 * A blend that leans back before it goes and drifts past before it
 * settles: the standard in-out "back" ease, with its constant dialled a
 * long way down from the usual 1.70158.
 *
 * This is only legal because pose space is LINEAR. A t of -0.03 is a real
 * pose three percent beyond the one the cat is leaving, and 1.04 is three
 * percent past the one it is arriving at -- so anticipation and overshoot
 * cost no new poses and no new geometry, only a different curve through
 * the blend that already existed. The vocabulary's poses are already
 * extremes, which is exactly why the constant has to be small: at
 * 1.70158 a pounce crouch overshoots into a cat folded in half.
 */
function easeBack(t, s = VIEW.blendBack) {
  const c = s * 1.525;
  return t < 0.5
    ? ((2 * t) ** 2 * ((c + 1) * 2 * t - c)) / 2
    : ((2 * t - 2) ** 2 * ((c + 1) * (2 * t - 2) + c) + 2) / 2;
}

/**
 * The yawn gape at `at` ms into a yawn, or undefined once it is over.
 *
 * Open, hold, close -- factored out beside `slowBlinkLid` because it is
 * the same envelope doing the same job, and because a second home for
 * values meant to be judged in the lab and pasted back is the one place
 * drift is guaranteed to start.
 *
 * As with the blink, the three spans must stay comfortably under
 * `idleMotionPeriodMs`: `at` arrives modulo the period, so a yawn longer
 * than its own slot would always be in progress.
 */
function yawnGape(at, dials = VIEW) {
  const open = dials.yawnOpenMs;
  const hold = dials.yawnHoldMs;
  const close = dials.yawnCloseMs;
  if (at < 0 || at >= open + hold + close) return undefined;
  if (at < open) return easeSmooth(at / open);
  if (at < open + hold) return 1;
  return 1 - easeSmooth((at - open - hold) / close);
}

/** Where a wetness fade has got to. Resumed from `from` rather than from
 * the far end, so a cat darting in and out of the shallows never snaps. */
function wetValue(w, now) {
  const target = w.on ? 1 : 0;
  // Wet fast, dry slow.
  const ms = w.on ? VIEW.wetFadeMs : VIEW.furDryMs;
  return w.from + (target - w.from) * easeSmooth(Math.min(1, (now - w.at) / ms));
}

/** A little overshoot-and-settle, for things that pop in (US6 juice). */
function easeOutBack(t) {
  const c1 = 1.70158;
  const c3 = c1 + 1;
  return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2;
}

/**
 * A step taken from a standstill: starts at rest and arrives at full
 * walking speed, so it hands over to a linear stride with no velocity
 * jump. f(0)=0, f(1)=1, f'(0)=0, f'(1)=1 -- the unique cubic that does
 * both, which is what makes the join invisible.
 */
function startEase(t) {
  return t * t * (2 - t);
}

/**
 * The state-pair store plus per-kitty presentational memory. Consumes
 * served worlds; produces the view the renderer draws. No DOM, no fetches.
 */
class Presentation {
  constructor() {
    this.prev = null;
    this.curr = null;
    this.currArrivedAt = 0;
    this.generation = 0;
    this.lastPushGeneration = -1;
    this.discontinuous = true;
    this.tickMs = VIEW.tickMsFallback;
    this.distressPatienceTicks = VIEW.distressPatienceFallback;
    this.facings = new Map(); // id -> 'left' | 'right'
    this.movedNow = new Map(); // id -> bool, for this pair
    // Tiles of ground each kitty has covered, completed ticks only. The
    // walk rides this instead of the clock -- see strideFor.
    this.odometer = new Map(); // id -> tiles
    this.movedBefore = new Map(); // id -> bool, for the PREVIOUS pair
    this.sleepingSince = new Map(); // id -> tick its current sleep began
    this.oneShots = new Map(); // id -> { kind, t0, duration }, one slot each
    this.newElementIds = new Set();
    this.expiredElements = [];
    this.pathHeat = new Map(); // "x,y" -> { heat, stampedAt } (spec 008 US5)
    // v2 pose-blend memory (motion wiring): what each kitty last wore on
    // screen, and its in-flight blend if a change just happened.
    this.lastPose = new Map(); // id -> { pose, phase, at } as last drawn
    this.poseTween = new Map(); // id -> { from, fromPhase, at }
    // Wetness, kept apart from the pose on purpose: the drawn tile says
    // whether a cat is in water, whatever it happens to be doing there.
    this.wetness = new Map(); // id -> { on, at, from }
    // The rig (2026-08-10): per-cat spring state for the tail, head, gaze
    // and ears, plus the clock each was last advanced on.
    //
    // This is the one genuinely stateful thing in the layer, and it is
    // safe for the same reason the pose blend is: it is dropped on every
    // discontinuity, and `rigFor` also rebuilds any state it has not
    // touched for a tick. So a viewer joining the feed mid-flight starts
    // every cat's rig AT REST rather than inheriting momentum from a
    // moment it never saw -- and a cat drawn out of a hidden tab does the
    // same, rather than springing violently to catch up.
    this.rigStates = new Map(); // id -> createRigState()
    this.rigAt = new Map(); // id -> the now it was last stepped at
    this.turns = new Map(); // id -> when this cat began turning around
    this.wokeAt = new Map(); // id -> when it last stopped sleeping
    this.stillSince = new Map(); // id -> tick it last had nothing to do
  }

  /** Reconnects and hidden-tab returns break continuity by definition. */
  bumpGeneration() {
    this.generation += 1;
  }

  pushState(world, now) {
    const prev = this.curr;
    // Bank the distance the OUTGOING pair covered, so the odometer holds
    // whole ticks and strideFor adds the eased part of the current one.
    if (prev && this.prev) {
      for (const k of prev.kitties) {
        const was = this.prev.kitties.find((p) => p.id === k.id);
        if (!was) continue;
        this.odometer.set(
          k.id,
          (this.odometer.get(k.id) ?? 0) + Math.hypot(k.pos.x - was.pos.x, k.pos.y - was.pos.y),
        );
      }
    }
    this.movedBefore = new Map(this.movedNow);
    this.prev = prev;
    this.curr = world;
    this.currArrivedAt = now;

    const rosterChanged =
      prev &&
      prev.kitties.map((k) => k.id).join(',') !==
        world.kitties.map((k) => k.id).join(',');
    // Kitties step at most one tile per tick, so anything larger is not
    // motion -- it is a different moment of the world.
    const teleported =
      prev &&
      !rosterChanged &&
      world.kitties.some((k) => {
        const was = prev.kitties.find((p) => p.id === k.id);
        return (
          Math.abs(k.pos.x - was.pos.x) > 1 || Math.abs(k.pos.y - was.pos.y) > 1
        );
      });
    this.discontinuous =
      !prev ||
      this.generation !== this.lastPushGeneration ||
      world.tick !== prev.tick + 1 ||
      Boolean(rosterChanged) ||
      Boolean(teleported);
    this.lastPushGeneration = this.generation;

    if (this.discontinuous) {
      // An unrelated pair must never blend: snap, and start memory afresh.
      // (A mid-sleep snapshot shows the held curl, not a replayed settle.)
      this.prev = null;
      this.facings.clear();
      this.movedNow.clear();
      this.movedBefore.clear();
      this.odometer.clear();
      this.sleepingSince.clear();
      this.oneShots.clear();
      this.newElementIds = new Set();
      this.expiredElements = [];
      // Worn paths are the session's own memory (spec 008 FR-009): a
      // different moment of the world starts with clean grass.
      this.pathHeat.clear();
      this.lastPose.clear();
      this.poseTween.clear();
      this.wetness.clear();
      // Momentum belongs to a moment; a different moment starts still.
      this.rigStates.clear();
      this.rigAt.clear();
      this.turns.clear();
      this.wokeAt.clear();
      this.stillSince.clear();
      return;
    }

    // Facing memory (FR-004): the horizontal component of the last move,
    // kept while standing still, derived only from served positions. The
    // same pass notes falling-asleep edges, so the curl transition plays
    // once and only once (US4 acceptance 3).
    this.movedNow.clear();
    for (const kitty of world.kitties) {
      const was = prev.kitties.find((p) => p.id === kitty.id);
      const dx = kitty.pos.x - was.pos.x;
      // A reversal is a served fact about the pair, so the turn is
      // stamped here rather than sniffed at draw time -- which also means
      // a fresh connection has no turns pending and simply faces the way
      // it was served, exactly as before.
      const facing = this.facings.get(kitty.id);
      if ((dx > 0 && facing === 'left') || (dx < 0 && facing === 'right')) {
        this.turns.set(kitty.id, now);
      }
      // Four facings (2026-08-10). The engine moves cats on four axes only,
      // so exactly one of dx/dy is ever non-zero and there is no diagonal
      // to resolve -- the dominant-axis test below is a guard, not a rule.
      const dy = kitty.pos.y - was.pos.y;
      if (dx || dy) {
        const horizontal = Math.abs(dx) >= Math.abs(dy);
        const next = horizontal ? (dx > 0 ? 'right' : 'left') : dy > 0 ? 'south' : 'north';
        this.facings.set(kitty.id, next);
        // The last EAST/WEST facing, remembered separately. Only some poses
        // have an axial drawing, so a cat that walks north and then starts
        // grooming has to be drawn side-on -- and it should face the way it
        // last plausibly did, not a direction picked at random.
        if (!this.sideFacings) this.sideFacings = new Map();
        if (horizontal) this.sideFacings.set(kitty.id, next);
      }
      this.movedNow.set(kitty.id, dx !== 0 || kitty.pos.y !== was.pos.y);

      const sleepingNow = kitty.activity?.state === 'sleeping';
      if (sleepingNow && was.activity?.state !== 'sleeping') {
        this.sleepingSince.set(kitty.id, world.tick);
      } else if (!sleepingNow) {
        if (was.activity?.state === 'sleeping') this.wokeAt.set(kitty.id, now);
        this.sleepingSince.delete(kitty.id);
      }

      // How long this kitty has had nothing asked of it, in served ticks:
      // the gate on sitting down. Movement and any named activity both
      // count as something to do. A chase or a play needs no entry here,
      // because those wear their own pose and never reach the idle
      // vocabulary at all.
      const activity = kitty.activity?.state;
      if (this.movedNow.get(kitty.id) || (activity && activity !== 'idle')) {
        this.stillSince.delete(kitty.id);
      } else if (!this.stillSince.has(kitty.id)) {
        this.stillSince.set(kitty.id, world.tick);
      }

      // Beats (US5, research R5): derived here, once per served pair, from
      // served fields and their differences -- never invented, never
      // re-derived per frame. One slot per kitty; the newest wins.
      // (Speech-bubble pop-in is deliberately not a beat -- analyze I2.)
      const relieved = Object.entries(kitty.needs ?? {}).some(
        ([need, value]) =>
          (was.needs?.[need] ?? 0) - value >= VIEW.reliefSparkleDrop,
      );
      if (relieved) {
        this.oneShots.set(kitty.id, {
          kind: 'sparkle',
          t0: now,
          duration: VIEW.sparkleMs,
        });
      }
      const chaseKey = (a) => `${JSON.stringify(a.target)}@${a.until}`;
      const knownChases = new Set((was.abandoned_chases ?? []).map(chaseKey));
      const gaveUp = (kitty.abandoned_chases ?? []).some(
        (a) => !knownChases.has(chaseKey(a)),
      );
      if (gaveUp) {
        this.oneShots.set(kitty.id, {
          kind: 'sad',
          t0: now,
          duration: VIEW.sadBeatMs,
        });
      }
      const action = kitty.last_action;
      if (action?.action === 'play' && action.target == null) {
        // Solo play: the imaginary plaything appears for exactly the tick
        // the pounce animation plays (FR-009).
        this.oneShots.set(kitty.id, {
          kind: 'plaything',
          t0: now,
          duration: this.tickMs,
        });
      }
    }

    // Worn paths (spec 008 US5): every kitty's served tile warms its heat
    // entry on each *continuous* tick -- accumulation is independent of any
    // toggle (visibility is not memory). Cold entries are pruned here so a
    // long session never grows past the tiles actually walked.
    for (const kitty of world.kitties) {
      const key = `${kitty.pos.x},${kitty.pos.y}`;
      const entry = this.pathHeat.get(key);
      const carried = entry ? decayedPathHeat(entry, now) : 0;
      this.pathHeat.set(key, {
        heat: Math.min(VIEW.meadow.pathHeatCap, carried + 1),
        stampedAt: now,
      });
    }
    for (const [key, entry] of this.pathHeat) {
      if (decayedPathHeat(entry, now) < VIEW.meadow.pathVisibilityFloor) {
        this.pathHeat.delete(key);
      }
    }

    // Elements fade in and out; they never glide from nowhere.
    const prevIds = new Set(prev.elements.map((e) => e.id));
    const currIds = new Set(world.elements.map((e) => e.id));
    this.newElementIds = new Set(
      world.elements.filter((e) => !prevIds.has(e.id)).map((e) => e.id),
    );
    this.expiredElements = prev.elements.filter((e) => !currIds.has(e.id));
  }

  /** 0..1 through the current tick. Clamped: never past the newest state. */
  progress(now) {
    if (!this.curr || this.discontinuous) return 1;
    return Math.min(1, (now - this.currArrivedAt) / this.tickMs);
  }

  facingFor(id) {
    return this.facings.get(id) ?? 'left';
  }

  /** The cat's last east/west facing, for poses with no axial drawing. */
  sideFacingFor(id) {
    return this.sideFacings?.get(id) ?? 'left';
  }

  movedFor(id) {
    return this.movedNow.get(id) ?? false;
  }

  /**
   * How far a kitty has walked, in tiles -- the clock the gait runs on.
   *
   * The walk used to ride `progress`, which is LINEAR, while `posFor`
   * eases the cat across every tile with easeInOutCubic. The cat's speed
   * therefore swings from a dead stop to three times its own average
   * inside one tile while the feet swept at a constant rate, so a planted
   * foot slid backward at the tile edges and forward through the middle,
   * reversing twice per tile. No choice of stride length could fix that,
   * because no instant is the average.
   *
   * Keying the gait to distance makes the easing cancel exactly: the foot
   * and the ground are now measured in the same units. A cat easing to a
   * stop slows its steps, which is what a cat does. And because distance
   * is continuous, the steps-per-tile dial is free to be fractional --
   * there is no longer a tick boundary for a part-finished stride to tear
   * against.
   */
  strideFor(id, now) {
    const done = this.odometer.get(id) ?? 0;
    const was = this.prev?.kitties.find((p) => p.id === id);
    const is = this.curr?.kitties.find((p) => p.id === id);
    if (!was || !is) return done;
    const step = Math.hypot(is.pos.x - was.pos.x, is.pos.y - was.pos.y);
    const p = this.progress(now);
    // The same curve posFor uses, or the feet would come off the ground.
    return done + step * (this.movedBefore.get(id) ? p : startEase(p));
  }

  /**
   * Float tile position: the blend of the two newest served states.
   *
   * This used to run easeInOutCubic on EVERY tile, which meant a cat
   * crossing eight tiles accelerated from a standstill and braked to a
   * dead stop eight times -- a stutter, not a walk (owner, 2026-08-08:
   * "stopping/starting every step"). A cat already walking now carries
   * its speed straight through the tile boundary; only a step taken from
   * rest eases in, and it arrives at exactly walking speed so the join
   * cannot be seen.
   *
   * There is deliberately no ease-OUT: the newest served state is the one
   * being walked into, so whether the cat stops after it is not knowable
   * yet, and a one-tick display lag to find out would cost more than it
   * buys. The stop is absorbed by the landing settle instead, which is
   * what that squash was always for.
   *
   * Safe because the gait rides distance (strideFor), not time: the feet
   * stay planted under any speed profile this picks.
   */
  posFor(kitty, now) {
    const was = this.prev?.kitties.find((p) => p.id === kitty.id);
    if (!was) return { x: kitty.pos.x, y: kitty.pos.y };
    const p = this.progress(now);
    const t = this.movedBefore.get(kitty.id) ? p : startEase(p);
    return {
      x: was.pos.x + (kitty.pos.x - was.pos.x) * t,
      y: was.pos.y + (kitty.pos.y - was.pos.y) * t,
    };
  }

  /**
   * Body velocity in tiles per second, screen axes (y down).
   *
   * Analytic rather than differenced. `posFor` is a known function of
   * progress, so its derivative is known too -- reading it costs nothing
   * and cannot jitter the way a frame-to-frame difference does on an
   * uneven rAF. It is also correct on the FIRST frame after a state
   * arrives, which a difference is not, and the first frame is exactly
   * when a tail ought to start moving.
   */
  velocityFor(id, now) {
    if (!this.curr || this.discontinuous) return { x: 0, y: 0 };
    const is = this.curr.kitties.find((k) => k.id === id);
    const was = this.prev?.kitties.find((p) => p.id === id);
    if (!is || !was) return { x: 0, y: 0 };
    const p = this.progress(now);
    // d/dp of the blend posFor uses. A cat already walking crosses the
    // tile linearly (slope 1); one stepping off from rest rides startEase,
    // whose slope is 4p - 3p^2 -- and which lands at exactly 1, which is
    // what makes the join between the two invisible.
    const slope = this.movedBefore.get(id) ? 1 : 4 * p - 3 * p * p;
    const perSec = 1000 / this.tickMs;
    return {
      x: (is.pos.x - was.pos.x) * slope * perSec,
      y: (is.pos.y - was.pos.y) * slope * perSec,
    };
  }

  /**
   * How much of this cat's travel is ACROSS the screen rather than into
   * it: 1 for a pure east/west step, 0 for due north or south. Feeds the
   * walk's foreshortening -- see cat-v2's walking case for why a vertical
   * walk drawn with a horizontal stride is 100% skate by construction.
   */
  travelHFor(id) {
    const is = this.curr?.kitties.find((k) => k.id === id);
    const was = this.prev?.kitties.find((p) => p.id === id);
    if (!is || !was) return 1;
    const dx = Math.abs(is.pos.x - was.pos.x);
    const dy = Math.abs(is.pos.y - was.pos.y);
    if (dx + dy === 0) return 1;
    return dx / (dx + dy);
  }

  /** 0..1 through an on-the-spot turn, or null when this cat is not
   * turning. Stamped from served facing changes in pushState. */
  turnFor(id, now) {
    const t0 = this.turns.get(id);
    if (t0 === undefined) return null;
    const t = (now - t0) / VIEW.turnMs;
    if (t >= 1) {
      this.turns.delete(id);
      return null;
    }
    return t;
  }

  /**
   * Advances one cat's rig and hands back the bag cat-v2's `applyRig`
   * consumes. Must be called at most once per cat per frame: it
   * integrates, so a second call in the same frame double-steps it.
   *
   * The motion maths lives in cat-v2 and the STATE lives here, which is
   * the split that lets the motion lab drive rigs with no animation layer
   * at all -- and lets the headless harness run with no cat vocabulary
   * loaded, since a missing `stepRig` simply means no rig.
   */
  rigFor(key, input, now) {
    if (typeof stepRig !== 'function') return null;
    const last = this.rigAt.get(key);
    let state = this.rigStates.get(key);
    if (!state || last === undefined || now - last > this.tickMs) {
      // No state, or a gap long enough that whatever we had describes a
      // different moment -- a hidden tab, a spell of reduced motion, a
      // fresh connection. Start at rest rather than springing out of
      // stale momentum. Same rule the pose blend uses, same reason.
      state = createRigState();
      this.rigStates.set(key, state);
    }
    this.rigAt.set(key, now);
    return stepRig(state, input, last === undefined ? 16 : Math.min(250, now - last));
  }

  /**
   * The pose an idle cat takes on its own initiative, or null to leave
   * the served pose alone (FR-008: idle motion can never imply an
   * action, so both of these are things a cat does while doing nothing).
   *
   * Returns { pose, phase } so the caller can hand the stretch its own
   * clock. Everything the pose tween needs comes free: sitting down,
   * standing up, and the stretch's entry and exit are all just pose
   * changes, and the blend was already there.
   */
  idlePoseFor(id, pose, now) {
    if (!this.curr) return null;
    if (pose !== 'idle' && pose !== 'loaf') {
      // The engine has given this cat something to do. An interrupted
      // stretch is ABANDONED rather than banked: resuming one later would
      // start it halfway through, which looks worse than never having
      // started it at all.
      this.wokeAt.delete(id);
      return null;
    }
    // A cat that just woke stretches. This is the one place the rarity
    // budget is not consulted, because it is not scheduled: it happens
    // exactly as often as cats wake up, which the engine decides.
    //
    // It fires on the OBSERVED wake, and cannot be moved to the last tick
    // of sleep however much better that would look: a tick is not known
    // to be the last one until the next state arrives, so anticipating it
    // would mean predicting the world, which this layer never does.
    const woke = this.wokeAt.get(id);
    if (woke !== undefined) {
      const t = (now - woke) / (VIEW.stretchTicks * this.tickMs);
      if (t < 1) return { pose: 'stretch', phase: t };
      this.wokeAt.delete(id);
    }
    if (pose !== 'idle') return null;
    const still = this.stillSince.get(id);
    if (still === undefined || this.curr.tick - still < VIEW.sitAfterTicks) return null;
    const slot = Math.floor((now + id * 7919) / VIEW.sitPeriodMs);
    if (idleHash(id, slot, IDLE_SALTS.sit) < VIEW.sitChance) return { pose: 'sit' };
    return null;
  }

  /**
   * The card portrait's play-pounce, or null. **Portraits only** -- see
   * VIEW.cardBeatPeriodMs for why the meadow must never call this.
   *
   * Pure in (id, now) like every other idle decision, so a still frame and
   * a test can both ask what a cat is doing at time T. Returns the beat
   * length with the phase, because the pounce's wiggle is authored as a
   * real frequency and needs to know how long the beat is -- the whole
   * point of doing this off the served tick.
   */
  /**
   * The card portrait's pose beat, or null. **Portraits only** -- see
   * VIEW.cardBeatPeriodMs for why the meadow must never call this.
   *
   * One weighted draw per period picks a sit-chain, a play-pounce, or
   * nothing. Pure in (id, now) like every other idle decision, so a still
   * frame and a test can both ask what a cat is doing at time T.
   *
   * The sit chain is sit -> stretch -> gone: the cat sits, holds, then gets
   * up through a stretch. `stretch` carries its own phase and returns to
   * neutral at the end, so the tail needs no blend out.
   */
  idleCardBeatFor(id, pose, now) {
    if (pose !== 'idle') return null;
    // Offset per cat, HASHED rather than a fixed multiple of the id: fixed
    // offsets land mod the period, and cats 1 and 4 once came out 453ms
    // apart, close enough to read as one clock.
    const period = VIEW.cardBeatPeriodMs;
    const clock = now + idleHash(id, 0, IDLE_SALTS.offset) * period;
    const slot = Math.floor(clock / period);
    const into = clock - slot * period;
    const table = [
      ['blink', VIEW.cardBlinkWeight],
      ['ears', VIEW.cardEarsWeight],
      ['scan', VIEW.cardScanWeight],
      ['yawn', VIEW.cardYawnWeight],
      ['sit', VIEW.cardSitWeight],
      ['pounce', VIEW.cardPounceWeight],
      ['rest', VIEW.cardRestWeight],
    ].map(([kind, w]) => [kind, Math.max(0, w || 0)]);
    const total = table.reduce((sum, [, w]) => sum + w, 0);
    if (total <= 0) return null;
    let draw = idleHash(id, slot, IDLE_SALTS.pick) * total;
    let pick = 'rest';
    for (const [kind, w] of table) {
      if (draw < w) { pick = kind; break; }
      draw -= w;
    }
    if (pick === 'rest') return null;

    const blinkMs = VIEW.slowBlinkDownMs + VIEW.slowBlinkHoldMs + VIEW.slowBlinkUpMs;
    const yawnMs = VIEW.yawnOpenMs + VIEW.yawnHoldMs + VIEW.yawnCloseMs;
    const stretchMs = VIEW.stretchTicks * this.tickMs;
    const lengths = {
      blink: blinkMs,
      ears: VIEW.idleMotionWindowMs,
      scan: VIEW.scanMs,
      yawn: yawnMs,
      sit: VIEW.sitHoldMs + stretchMs,
      pounce: VIEW.playBeatMs,
    };
    // Placed somewhere inside the slot, bounded by its OWN length, so a
    // long beat cannot start so late that it runs into the next slot --
    // the whole point of one-at-a-time.
    const start = idleOffsetFor(id, slot, period, lengths[pick], VIEW);
    const t = into - start;
    if (t < 0 || t >= lengths[pick]) return null;

    if (pick === 'sit') {
      if (t < VIEW.sitHoldMs) return { pose: 'sit' };
      return { pose: 'stretch', phase: (t - VIEW.sitHoldMs) / stretchMs };
    }
    if (pick === 'pounce') {
      return {
        pose: 'pouncing',
        phase: t / VIEW.playBeatMs,
        beatMs: VIEW.playBeatMs,
        wiggleHz: VIEW.playWiggleHz,
        sway: VIEW.playSway,
      };
    }
    // The face and ear beats. They ride the rig, so this only says what and
    // how far -- the springs are the portrait's own (`'card' + id`).
    if (pick === 'blink') return { pose: 'idle', blinkLid: slowBlinkLid(t, VIEW) };
    if (pick === 'ears') {
      const u = t / VIEW.idleMotionWindowMs;
      return {
        pose: 'idle',
        earTwitch: Math.sin(u * Math.PI),
        earTwitchSide: idleHash(id, slot, IDLE_SALTS.side) < 0.5 ? -1 : 1,
      };
    }
    if (pick === 'scan') {
      const u = t / VIEW.scanMs;
      const env = easeSmooth(Math.min(1, u * 3)) * (1 - easeSmooth(Math.max(0, (u - 0.6) / 0.4)));
      const dir = idleHash(id, slot, IDLE_SALTS.look);
      return {
        pose: 'idle',
        gaze: { x: (dir * 2 - 1) * env, y: (idleHash(id, slot, IDLE_SALTS.side) - 0.5) * env },
      };
    }
    if (pick === 'yawn') return { pose: 'idle', yawn: yawnGape(t, VIEW) };
    return null;
  }

  /**
   * The fall-asleep settle (US4): on the very tick sleep begins, the first
   * half of the tick still shows the loaf, so the curl reads as a
   * transition -- and later sleeping ticks hold the curl without replaying.
   */
  adjustPose(id, pose, now) {
    if (
      pose === 'sleep-curl' &&
      this.sleepingSince.get(id) === this.curr?.tick &&
      this.progress(now) < 0.5
    ) {
      return 'loaf';
    }
    return pose;
  }

  /**
   * The v2 pose blend (motion wiring): a pose change opens a short
   * pose-space blend for drawCatTween, and arriving -- walking to a
   * stand -- lands with the lab's slow settle squash, concurrent with its
   * blend (the lab's own timeline). Detection is draw-time, so mid-tick
   * changes (the fall-asleep loaf -> sleep-curl swap) blend too. The
   * from-phase freezes at the change: the old pose leaves exactly as last
   * seen. Only the v2 renderer path consumes this; the recording is
   * harmless when nothing reads it.
   */
  tweenFor(id, pose, phase, now) {
    const last = this.lastPose.get(id);
    this.lastPose.set(id, { pose, phase, at: now });
    if (last && last.pose !== pose) {
      if (now - last.at <= this.tickMs) {
        // Newest wins: a change mid-blend restarts from the old target.
        this.poseTween.set(id, { from: last.pose, fromPhase: last.phase, at: now });
      } else {
        // A draw gap past a tick is a different moment (hidden tab, a
        // reduced-motion spell): snap, never a catch-up blend.
        this.poseTween.delete(id);
      }
    }
    const tw = this.poseTween.get(id);
    if (!tw) return null;
    const arrive = tw.from === 'walking' && (pose === 'idle' || pose === 'loaf');
    const blendMs = Math.min(
      arrive ? VIEW.arriveBlendMs : VIEW.poseBlendMs,
      VIEW.blendTickShareCap * this.tickMs,
    );
    const elapsed = now - tw.at;
    const out = {};
    if (elapsed < blendMs) {
      out.blend = {
        from: tw.from,
        fromPhase: tw.fromPhase,
        // easeBack, not easeSmooth: the blend now leans back before it
        // goes and drifts a little past before it settles. Costs nothing
        // -- pose space is linear, so the over- and under-shoot are real
        // poses either side of the two ends.
        t: easeBack(elapsed / blendMs),
      };
    }
    if (arrive && elapsed < VIEW.settleMs) {
      out.sy = 1 - VIEW.settleDip * Math.sin(Math.PI * easeSmooth(elapsed / VIEW.settleMs));
    }
    if (!out.blend && out.sy === undefined) {
      this.poseTween.delete(id);
      return null;
    }
    return out;
  }

  /**
   * How wet a cat's COAT is, 0..1 -- a fact about the cat, not the place.
   *
   * Still independent of the pose (owner call, 2026-08-04): a cat
   * drinking in a pond keeps its drinking pose and must still look wet.
   * What changed on 2026-08-10 is what this drives.
   *
   * **The invariant: this may only ever change COLOUR.** Every piece of
   * water GEOMETRY -- the waterline clip, the meniscus, the lost ground
   * shadow, the displacement rings -- is driven by `submersionFor`, which
   * is spatial and is exactly zero the moment the cat is clear of the
   * water. This signal outlives the pond by design (`furDryMs`), so
   * anything positional hung off it draws water on grass. That was the
   * bug; keeping the two apart is the fix.
   */
  wetFor(id, onWater, now) {
    const prev = this.wetness.get(id);
    if (!prev) {
      // First sight settles rather than fading in, as pose memory does.
      this.wetness.set(id, { on: onWater, at: now, from: onWater ? 1 : 0 });
      return onWater ? 1 : 0;
    }
    if (prev.on !== onWater) {
      this.wetness.set(id, { on: onWater, at: now, from: wetValue(prev, now) });
    }
    return wetValue(this.wetness.get(id), now);
  }

  /**
   * Phase and micro-motion for one kitty (US4). Action poses run on the
   * tick clock (their whole animation fits the tick that served them);
   * resting poses breathe on a slow local cycle; idle cats get their
   * scheduled blink, tail flick, or ear twitch -- gentle, occasional, and
   * never during an action, so idle motion can never imply one (FR-008).
   */
  motionFor(id, pose, now, dials = VIEW) {
    // The walk is measured in ground covered, not in time (strideFor);
    // every other action still rides the tick clock.
    if (pose === 'walking') return { phase: this.strideFor(id, now) };
    const isAction =
      pose === 'pouncing' ||
      pose === 'eating' ||
      pose === 'drinking' ||
      pose === 'grooming';
    if (isAction) return { phase: this.progress(now) };

    const seed = id * 997;
    const motion = {
      phase: ((now + seed) % dials.breathePeriodMs) / dials.breathePeriodMs,
    };
    if (pose === 'sleep-curl') return motion; // sleepers just breathe
    if (pose === 'swim') {
      // Paddling rides the tick clock on the move, like the walk it
      // replaces; a floating cat bobs on the ambient cycle and, like a
      // sleeper, skips the idle twitches (its tail is underwater).
      if (this.movedFor(id)) return { phase: this.progress(now) };
      return motion;
    }

    // Idle and loafing cats are never statues: each slot draws a motion and
    // starts it somewhere inside the slot. A slot may equally draw nothing,
    // which is what stops the ones that do land from reading as scheduled.
    const period = idlePeriodFor(id, dials);
    const wobble = now + id * 1337;
    const slot = Math.floor(wobble / period);
    const at = wobble % period;
    const pick = idlePickFor(id, slot, dials);
    if (pick === 'rest') return motion; // a slot off, breathing as usual

    const blinkMs =
      dials.slowBlinkDownMs + dials.slowBlinkHoldMs + dials.slowBlinkUpMs;
    const yawnMs = dials.yawnOpenMs + dials.yawnHoldMs + dials.yawnCloseMs;
    // Each motion's jitter must be bounded by its OWN length. Sharing the
    // 420ms window let the two long motions start as late as a short one
    // may and then run past the end of their slot -- into the next slot,
    // where the next motion is already playing. Overlapping idle motions
    // are precisely what the slot machinery exists to prevent.
    const durationMs =
      pick === 'blink' ? blinkMs
        : pick === 'yawn' ? yawnMs
          : pick === 'scan' ? dials.scanMs
            : dials.idleMotionWindowMs;
    // Time into the motion itself, which is what every envelope below is
    // measured from -- negative before it starts, past `durationMs` after.
    const t = at - idleOffsetFor(id, slot, period, durationMs, dials);

    if (pick === 'ears') {
      if (t >= 0 && t < dials.idleMotionWindowMs) {
        const u = t / dials.idleMotionWindowMs;
        // A continuous envelope on ONE ear, replacing a boolean that
        // flipped BOTH for the whole window. A cat twitches one ear; two
        // ears going back together is a mood, not a twitch, and the
        // instant on/off was a switch rather than a motion either way.
        // `earsBack` is kept for the v1 path, which has no rig to ease.
        motion.earTwitch = Math.sin(u * Math.PI);
        motion.earTwitchSide = idleHash(id, slot, IDLE_SALTS.side) < 0.5 ? -1 : 1;
        motion.earsBack = u < 0.5;
      }
      return motion;
    }

    if (pick === 'scan') {
      // A slow look somewhere and back. The gaze channel is sprung in the
      // rig, so this only has to say where and for how long.
      if (t >= 0 && t < dials.scanMs) {
        const u = t / dials.scanMs;
        const env = easeSmooth(Math.min(1, u * 3)) * (1 - easeSmooth(Math.max(0, (u - 0.6) / 0.4)));
        const dir = idleHash(id, slot, IDLE_SALTS.look);
        motion.gaze = {
          x: (dir * 2 - 1) * env,
          y: (idleHash(id, slot + 7, IDLE_SALTS.look) * 1.2 - 0.7) * env,
        };
      }
      return motion;
    }

    if (pick === 'yawn') {
      // Opens quicker than it closes: the other way round reads as a
      // hiss, which is the last thing this world wants.
      const gape = yawnGape(t, dials);
      if (gape !== undefined) motion.yawn = gape;
      return motion;
    }

    // v1 keeps its snap blink over its own short window; the v2 renderer
    // prefers the eased lid and drops the snap, so v1 stays bit-identical.
    if (t >= 0 && t < dials.idleMotionWindowMs) motion.eyesOverride = 'closed';
    const lid = slowBlinkLid(t, dials);
    if (lid !== undefined) motion.blinkLid = lid;
    return motion;
  }

  /** The active one-shot beat for a kitty, with its own 0..1 progress. */
  oneShotFor(id, now) {
    const beat = this.oneShots.get(id);
    if (!beat) return null;
    const t = (now - beat.t0) / beat.duration;
    if (t >= 1) {
      this.oneShots.delete(id);
      return null;
    }
    return { kind: beat.kind, t };
  }

  /**
   * Sustained expression, a pure function of the newest state (FR-010):
   * a cat mid-pursuit wears the hunter's eyes for as long as it hunts.
   *
   * Hunting, though -- not roughhousing (owner, 2026-08-10). A cat
   * stalking a bug is doing something predatory and should look it; a cat
   * pouncing on another cat is playing. The pounce is the SAME pose
   * either way, so the face is the only thing that can tell them apart --
   * and the answer is already in the served data: what the quarry is. An
   * element is prey; a kitty is a playmate.
   *
   * The expression is withheld only on positive evidence that the quarry
   * is a kitty -- the same rule the pounce gate follows, and for the same
   * reason. A quarry that cannot be resolved (caught or expired this very
   * tick) keeps the hunter's face rather than losing it to a missing
   * field, so this can never make a hunting cat look ordinary because
   * something failed to resolve.
   */
  expressionFor(kitty) {
    if (!kitty.pursuit) return undefined;
    // The served pursuit names its quarry when it can; otherwise the
    // applied action does.
    // The two sources name the quarry in DIFFERENT shapes, which is what
    // made this dead on arrival: `pursuit.target` is a TargetRef OBJECT
    // ({target: 'kitty', id: 2}) while `last_action.target` is a plain
    // string ('kitty'). Comparing the object against 'element' is never
    // equal, so every pursuing cat fell through to `undefined` and
    // 'focused' was unreachable -- the hunter's face never once appeared in
    // the live world. It looked fine in the gallery because the card forces
    // it with `eyesOverride: 'focused'` rather than going through here.
    const ref = (kitty.pursuit && kitty.pursuit.target) || kitty.last_action?.target;
    const kind = typeof ref === 'string' ? ref : ref?.target;
    // Withheld only on POSITIVE evidence the quarry is a kitty, the same
    // rule the pounce gate follows: a quarry that cannot be resolved --
    // caught or expired this tick -- keeps the face rather than losing it
    // to a missing field.
    if (kind && kind !== 'element') return undefined;
    return 'focused';
  }

  /**
   * The long-wanted need, if any (FR-012): the longest-running served
   * distress at or past the served patience threshold -- the panel cue's
   * exact comparison (>=, analyze A1) and the same threshold value. At
   * most one; null when nothing has waited that long.
   */
  thoughtFor(kitty) {
    const since = kitty.distress_since;
    if (!since || !this.curr) return null;
    let oldest = null;
    for (const [need, startTick] of Object.entries(since)) {
      const age = this.curr.tick - startTick;
      if (age >= this.distressPatienceTicks && (!oldest || age > oldest.age)) {
        oldest = { need, age };
      }
    }
    return oldest?.need ?? null;
  }

  /**
   * Float tile position for a moving element (007 refinement, 2026-07-20):
   * critters glide on the same eased clock as kitties. Spawns and
   * anything farther than `critterGlideMaxTiles` snap -- that is not
   * motion, it is a different moment of the world.
   */
  elementPosFor(el, now) {
    const was = this.prev?.elements.find((p) => p.id === el.id);
    if (
      !was ||
      Math.abs(el.pos.x - was.pos.x) > VIEW.critterGlideMaxTiles ||
      Math.abs(el.pos.y - was.pos.y) > VIEW.critterGlideMaxTiles
    ) {
      return { x: el.pos.x, y: el.pos.y };
    }
    const t = easeInOutCubic(this.progress(now));
    return {
      x: was.pos.x + (el.pos.x - was.pos.x) * t,
      y: was.pos.y + (el.pos.y - was.pos.y) * t,
    };
  }

  /**
   * The worn-path snapshot (spec 008 US5): decayed heat per walked tile,
   * filtered to what is visible, normalized to 0..1. Available in still
   * frames too -- revealed trails are state, not motion (FR-012).
   */
  wornPaths(now) {
    const entries = [];
    for (const [key, entry] of this.pathHeat) {
      const heat = decayedPathHeat(entry, now);
      if (heat < VIEW.meadow.pathVisibilityFloor) continue;
      const [x, y] = key.split(',').map(Number);
      // Display saturates at pathFullHeat, not the memory cap (revision 1:
      // normalizing by the cap left a once-walked tile at 3% alpha --
      // arithmetically invisible). A few passes now read plainly.
      entries.push({ x, y, heat01: Math.min(1, heat / VIEW.meadow.pathFullHeat) });
    }
    return entries;
  }

  elementAlphaFor(el, now) {
    if (!this.newElementIds.has(el.id)) return 1;
    return Math.min(1, this.progress(now) / VIEW.elementFadeShare);
  }

  expiredAlpha(now) {
    return Math.max(0, 1 - this.progress(now) / VIEW.elementFadeShare) * 0.7;
  }

  /**
   * The frame the renderer draws. `still` (reduced motion, or a snap after
   * a discontinuity) is simply progress = 1 with no fades -- one draw path
   * for both modes, so they cannot drift apart.
   */
  viewAt(now, still) {
    return {
      now,
      still,
      progress: still ? 1 : this.progress(now),
      posFor: (kitty) =>
        still ? { x: kitty.pos.x, y: kitty.pos.y } : this.posFor(kitty, now),
      facingFor: (id) => this.facingFor(id),
      movedFor: (id) => this.movedFor(id),
      strideFor: (id) => this.strideFor(id, now),
      adjustPose: (id, pose) => (still ? pose : this.adjustPose(id, pose, now)),
      // Still frames get the static pose for the state, nothing more
      // (FR-015): phase 0, no blinks, no flicks.
      motionFor: (id, pose) => (still ? { phase: 0 } : this.motionFor(id, pose, now)),
      // The v2 pose blend + landing settle. Null in still frames -- a
      // still frame is the pose, held -- and recording skips with it, so
      // a spell of stillness can never seed a stale blend.
      tweenFor: (id, pose, phase) => (still ? null : this.tweenFor(id, pose, phase, now)),
      // The rig (2026-08-10). Null in a still frame, which is what makes
      // reduced motion and the snap after a discontinuity draw the
      // un-rigged vocabulary exactly as they always did: applyRig(L, null)
      // is the same drawing as no rig at all.
      // A still frame gets gaze and nothing else: where a cat is looking is
      // served state, not motion, so it survives reduced motion for the
      // same reason the focused eyes and the worn paths do (R6, FR-012).
      // The idle scan is not included and cannot be -- `motionFor` returns
      // bare phase 0 in a still frame -- so only a real served target ever
      // moves a still cat's eyes.
      rigFor: (key, input) =>
        still
          ? (typeof stillRig === 'function' ? stillRig(input) : null)
          : this.rigFor(key, input, now),
      velocityFor: (id) => (still ? { x: 0, y: 0 } : this.velocityFor(id, now)),
      travelHFor: (id) => this.travelHFor(id),
      sideFacingFor: (id) => this.sideFacingFor(id),
      // The served beat length, so presentation code whose timing is a
      // real-world frequency (the pounce wiggle) can derive its rate from
      // the tick rather than assuming 800ms.
      tickMs: this.tickMs,
      turnFor: (id) => (still ? null : this.turnFor(id, now)),
      // A still frame is the served pose, held -- a cat is not caught
      // mid-stretch in a frame that is meant to have no motion in it.
      idlePoseFor: (id, pose) => (still ? null : this.idlePoseFor(id, pose, now)),
      idleCardBeatFor: (id, pose) => (still ? null : this.idleCardBeatFor(id, pose, now)),
      // Wetness carries state (this cat is in water), not motion, so a
      // still frame gets it at full strength rather than not at all --
      // the worn-paths and focused-eyes rule (FR-012, R6).
      wetFor: (id, onWater) =>
        still ? (onWater ? 1 : 0) : this.wetFor(id, onWater, now),
      // One-shot particles rest under reduced motion; the sustained
      // *informational* cues (focused eyes, the thought bubble) do not --
      // they carry state, not motion (R6).
      oneShotFor: (id) => (still ? null : this.oneShotFor(id, now)),
      // Prop motion (spec 007): one wall-clock phase source over a named
      // period, seeded by an element *or* kitty id -- 0 when still, so
      // reduced motion gets static props with full state (FR-013).
      propPhaseFor: (id, periodMs) =>
        still ? 0 : ((now + id * 4241) % periodMs) / periodMs,
      expressionFor: (kitty) => this.expressionFor(kitty),
      thoughtFor: (kitty) => this.thoughtFor(kitty),
      elementAlphaFor: (el) => (still ? 1 : this.elementAlphaFor(el, now)),
      elementPosFor: (el) =>
        still ? { x: el.pos.x, y: el.pos.y } : this.elementPosFor(el, now),
      expired: still ? [] : this.expiredElements,
      expiredAlpha: still ? 0 : this.expiredAlpha(now),
      // Worn paths draw in still frames too: the overlay carries state
      // (where cats have walked), not motion (spec 008 FR-012).
      wornPaths: () => this.wornPaths(now),
      // Ambient life (US6): absent entirely under reduced motion (FR-013).
      ambient: still ? null : { now },
      // Juice (US6): a fresh meow pops in with a small settle; the over-cat
      // happiness bar eases between the two served values on the same
      // progress clock as everything else (FR-014, FR-019). The engine
      // stamps a meow during the apply phase and advances the tick counter
      // before publishing, so the freshest served meow always reads
      // curr.tick - 1 -- a meow from the tick that just closed is the new
      // one (review fix: comparing against curr.tick matched nothing, and
      // the pop-in never played).
      bubbleScaleFor: (meow) => {
        if (still || !this.curr || meow.tick !== this.curr.tick - 1) return 1;
        return easeOutBack(Math.min(1, this.progress(now) / VIEW.bubblePopShare));
      },
      barValueFor: (kitty) => {
        if (still) return kitty.happiness;
        const was = this.prev?.kitties.find((p) => p.id === kitty.id);
        if (!was) return kitty.happiness;
        return (
          was.happiness +
          (kitty.happiness - was.happiness) * easeInOutCubic(this.progress(now))
        );
      },
    };
  }
}

/**
 * The browser side: one rAF loop, stopped whenever it has no business
 * running (hidden page, reduced motion). Everything here is wiring; the
 * decisions above stay pure.
 */
const anim = {
  presentation: new Presentation(),
  renderer: null,
  rafId: 0,
  reduced: false,

  init(renderer) {
    this.renderer = renderer;

    const media = window.matchMedia('(prefers-reduced-motion: reduce)');
    const applyMotionPreference = () => {
      this.reduced = media.matches;
      // The panel's CSS transitions go still with the canvas (FR-015).
      document.body.classList.toggle('reduced-motion', this.reduced);
      if (this.reduced) this.stopLoop();
      this.redraw();
      if (!this.reduced) this.startLoop();
    };
    media.addEventListener('change', applyMotionPreference);
    this.reduced = media.matches;
    document.body.classList.toggle('reduced-motion', this.reduced);

    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        // Zero animation work while hidden (FR-016). Frames still arrive
        // and update the store cheaply, so the return is instant.
        this.stopLoop();
      } else {
        // The return snaps to the newest state; no catch-up replay.
        this.presentation.bumpGeneration();
        this.redraw();
        this.startLoop();
      }
    });
  },

  /** A served world arrived (first snapshot or WS frame). */
  push(world) {
    this.presentation.pushState(world, performance.now());
    if (document.hidden) return;
    if (this.reduced) this.redraw();
    else this.startLoop();
  },

  /** One static draw of the newest state (reduced motion, snaps, toggles). */
  redraw() {
    if (!this.presentation.curr || !this.renderer) return;
    const view = this.presentation.viewAt(performance.now(), true);
    this.renderer.draw(this.presentation.curr, view);
    // The still view is what makes this safe to share: `motionFor` returns
    // phase 0 and nothing else, so whatever paints here holds its pose.
    if (this.onFrame) this.onFrame(this.presentation.curr, view);
  },

  /**
   * Anything outside the canvas that has to move on the world's clock.
   *
   * The card portraits are the first: they are cats, so they blink and
   * twitch off the same `motionFor` the meadow uses. Handing them the
   * frame's own view rather than letting them run a second rAF loop is
   * what keeps the two honest -- one clock, and every rule the canvas
   * already obeys comes with it. A still frame passes a still view, so
   * reduced motion stops the portraits without app.js knowing the rule
   * exists (FR-015); a hidden tab stops the loop, so they stop too
   * (FR-016); and the pair can never drift, because there is no second
   * timer to drift from.
   */
  onFrame: null,

  startLoop() {
    if (this.rafId || this.reduced) return;
    const step = () => {
      this.rafId = 0;
      if (document.hidden || this.reduced) return;
      const p = this.presentation;
      if (p.curr) {
        const view = p.viewAt(performance.now(), false);
        this.renderer.draw(p.curr, view);
        if (this.onFrame) this.onFrame(p.curr, view);
      }
      this.rafId = requestAnimationFrame(step);
    };
    this.rafId = requestAnimationFrame(step);
  },

  stopLoop() {
    if (this.rafId) cancelAnimationFrame(this.rafId);
    this.rafId = 0;
  },

  setTickMs(ms) {
    if (Number.isFinite(ms) && ms >= 1) this.presentation.tickMs = ms;
  },

  setDistressPatience(ticks) {
    if (Number.isFinite(ticks) && ticks >= 1) {
      this.presentation.distressPatienceTicks = ticks;
    }
  },

  bumpGeneration() {
    this.presentation.bumpGeneration();
  },
};
