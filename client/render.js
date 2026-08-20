/**
 * CloudKitty's renderer.
 *
 * A pure view: it draws whatever world the server sent and computes nothing about
 * the simulation itself (Article V). The one piece of judgement it makes is a
 * presentational one -- greebles are not drawn, which is why kitties appear to
 * chase nothing at all. Press `g` to see what they can see.
 */

// (TILE_COLORS is gone -- spec 008: every ground hue now lives in the named
// MEADOW palette in meadow.js, beside the drawings that use it.)

/** A ceiling on the map's longest side, in CSS pixels, so a very large
 * display does not blow the meadow up past the art's comfortable range.
 * On any normal screen the viewport height binds long before this does. */
const MAP_MAX_PX = 1200;
// The ground bake's ceiling, in DEVICE pixels per side (spec 036). Mobile
// Safari caps total canvas area and hands back a BLANK canvas rather than
// a slow one, so this is a correctness bound and not a tuning knob. Past
// it the ground magnifies slightly, which is the graceful failure; an
// empty meadow is not.
const GROUND_BAKE_MAX_PX = 4096;
// The pond layers get a tighter bound than the ground, because
// `buildPondLayers` allocates FOUR canvases where the ground allocates
// one -- two that persist and two scratch. Bounding each canvas's side
// while the feature multiplied the canvas COUNT is guarding the wrong
// quantity, and mobile Safari caps total canvas memory and hands back a
// blank canvas rather than an error. Halving the side quarters the area,
// which is what brings four layers back to roughly one ground bake.
const POND_BAKE_MAX_PX = 2048;

/** Slack for the margins between header, map and footer, which are not
 * worth measuring individually. Too small and the page gains a scrollbar;
 * too large and the map is needlessly shy of the space it has. Tightened
 * 40 -> 30 (owner, 2026-08-05) now that the rest of the fit is measured
 * rather than guessed. 16 was tried and is too tight: it left an 8-12px
 * scrollbar on the larger displays, which is exactly the inter-section
 * margin this constant stands in for. Verified scrollbar-free across the
 * display matrix at both 20x20 and 24x24 -- if that ever regresses, this
 * is the first number to suspect.
 *
 * The invariant is narrower than it reads: it holds where the cards sit
 * BESIDE the map (>= 1100px). Below that breakpoint they stack under it
 * and their height is real vertical chrome this sum does not include, so
 * a narrow window scrolls to reach them -- accepted (owner, 2026-08-05:
 * phones may scroll for the cards). */
const VERTICAL_SLACK = 30;

/* The free register (spec 033). These are SOUND-named, not law-named: the
 * word denotes the noise and means nothing until the cats decide otherwise,
 * so the viewer is shown the sound itself. Glossing `mew` as "Follow me!"
 * would reassert exactly the meaning its rename stripped, and FR-002b makes
 * that a naming-law violation -- a bubble is a name the viewer reads.
 * Owner's ruling, 2026-08-15: the client renders sound-words AS-IS.
 *
 * `trill` and `ekekek` are config-off reserves. They are written here anyway
 * so that arming them for the post-fog language-capacity work stays a pure
 * config flip with no client change, which is the point of holding them. */
const SOUND_WORDS = ['mew', 'chirp', 'trill', 'ekekek'];

const MEOW_TEXT = {
  want_eat: 'I want to eat!',
  want_drink: 'I want to drink!',
  // Pre-wall only. The served box still runs its pre-wall binary and emits
  // this, so it is load-bearing until the phase-1 --fresh; the engine has no
  // FollowMe variant after that, so it simply stops arriving and this line
  // becomes housekeeping. Both keys carry the same copy across the cutover.
  follow_me: 'Follow me!',
  want_play: 'I want to play!',
  want_cuddle: 'I want to cuddle!',
  // Kept, but no longer reached: a purr draws a glyph rather than a bubble
  // (see drawBubbles). A test pins that, so this entry is provably unused
  // rather than merely believed to be.
  purr: 'purrrr',
  wait_for_me: 'Wait for me!',
  // Spec 028 gave the two silent needs their words. Appended in the engine's
  // own order -- a kind missing here renders as the '…' fallback, not a crash,
  // so the only symptom would have been a bubble with nothing to say.
  want_bath: 'Bath time!',
  want_sleep: 'I’m sleepy!',
  // The Here family (spec 033), owner's copy, verbatim. Law-named, and the
  // law is ADJACENCY: the cat is standing beside the thing it announces, so
  // these read as "right here" rather than as a report from across the
  // meadow. here_critter is play-predicate only.
  here_food: 'Here food!',
  here_water: 'Here drink!',
  here_critter: 'Here bug!',
  here_sunbeam: 'Here warm!',
};
for (const word of SOUND_WORDS) MEOW_TEXT[word] = word;

/** The greeble wisp's face -- decided at the 007 gallery gate (2026-07-20):
 * the tiny grin of a creature that knows exactly what it's doing. */
const GREEBLE_FACE = 'grin';

// (The sky dial moved to app.js, 2026-07-23: it perches on the map's top
// edge as its own overlay canvas -- page chrome, not world drawing.)

/** How many ticks a speech bubble lingers on screen. */
const BUBBLE_TICKS = 3;

/**
 * The pose a served action puts a kitty in. `Rest` is mapped though the live
 * world has not served one -- the variant is in the engine's `Action` enum
 * and the sunbeam work may start surfacing it.
 */
const ACTION_POSE = {
  sleep: 'sleep-curl',
  rest: 'loaf',
  groom: 'grooming',
  eat: 'eating',
  drink: 'drinking',
};

/** The same poses, named by a scene that is still running. */
const SCENE_POSE = {
  sleeping: 'sleep-curl',
  resting: 'loaf',
  grooming: 'grooming',
  eating: 'eating',
  drinking: 'drinking',
};

/**
 * Which pose a served kitty is in (spec 005, data-model table): the applied
 * ACTION speaks first, then the scene it is in, then movement, then idle --
 * with water under the last two (a wading kitty paddles instead of walking
 * or standing; activities and the pounce keep their poses, spec 010's
 * skirt-the-puddle rule makes all of these rare). Pure function of served
 * data -- nothing here predicts (Article V). `onWater` arrives pre-gated:
 * only the v2 vocabulary owns a swim pose, so v1 callers pass false.
 *
 * The action first, and the order is the whole point (2026-08-13).
 * `activity` is the scene IN PROGRESS as of END of tick, while `last_action`
 * is what the engine applied DURING it -- the engine acts, then clears scenes
 * that ended, then publishes. So a scene's final tick truthfully reports
 * `last_action: eat` AND `state: idle`, and reading the state drew a cat
 * standing about on 17.4% of all cat-ticks: half of every meal and drink,
 * and a sleeper sitting bolt upright for the last 600ms of every nap.
 * `doingFor` in app.js already follows `last_action` -- the documented
 * pattern, spec 006 -- so the card said "eating" over a cat doing nothing.
 *
 * The scene fallback is NOT vestigial: `Idle`, `Purr` and `Meow` name no pose
 * of their own, and for those the scene still decides exactly as it always
 * did. That is what makes this change additive rather than a rewrite -- the
 * only ticks that move are the ones where the action itself names a pose.
 */
function poseFor(kitty, moved, onWater = false, chaseDist = null, dials = VIEW) {
  const action = kitty.last_action?.action;
  const acted = ACTION_POSE[action];
  if (acted) return acted;
  // Play is never gated: every targeted Play is adjacent by lawfulness
  // (the engine requires it), and solo play has no target at all.
  if (action === 'play') return 'pouncing';
  // A chase pounces once its quarry is within reach. `null` means the
  // target could not be resolved -- caught or expired this very tick, or
  // a v1 caller passing no distance -- and an unknown quarry keeps the
  // pounce, so the gate only ever takes it away on positive evidence.
  if (action === 'chase' && (chaseDist === null || chaseDist <= dials.pounceGateTiles)) {
    return 'pouncing';
  }
  const scene = SCENE_POSE[kitty.activity?.state];
  if (scene) return scene;
  if (onWater) return 'swim';
  if (moved) return 'walking';
  return 'idle';
}

/**
 * Manhattan tiles from a kitty to whatever its applied chase named, or
 * null when it is not chasing or the quarry is no longer served.
 *
 * Measured against the same served state the frame draws, which is
 * exactly what the gate should see -- nothing here predicts (Article V).
 */
function chaseDistanceFor(kitty, world) {
  const ref = kitty.last_action;
  if (ref?.action !== 'chase') return null;
  const pos =
    ref.target === 'element'
      ? world.elements.find((el) => el.id === ref.id)?.pos
      : world.kitties.find((k) => k.id === ref.id)?.pos;
  if (!pos) return null;
  return Math.abs(kitty.pos.x - pos.x) + Math.abs(kitty.pos.y - pos.y);
}

/**
 * Manhattan tiles from a kitty to whatever its PURSUIT names.
 *
 * Deliberately not `chaseDistanceFor`: that one reads `last_action`, which
 * is this tick's applied action, while the hunter's face is driven by the
 * pursuit -- a longer-lived thing that survives a cat stopping for a drink
 * on the way. They can name different quarry on the same tick.
 *
 * THREE outcomes, and the difference between the last two is the whole
 * point (owner, 2026-08-16: "hunter eyes with no bug in proximity"):
 *
 *   - a number, when the quarry is served and can be measured;
 *   - `null` when there is nothing to measure -- no pursuit, or a target
 *     whose shape this does not recognise. The caller gives `null` the
 *     benefit of the doubt and keeps the hunter's face, so a field that
 *     goes missing can never make a hunting cat look ordinary;
 *   - `Infinity` when the target is WELL-FORMED and names something the
 *     world does not contain. That is not a failure to resolve, it is the
 *     quarry being gone -- caught or expired -- and the payload carries
 *     the whole world, so absence is evidence rather than ignorance.
 *
 * Both of the last two used to return `null`, which meant the tick where a
 * bug expired was served as pursuit-present-quarry-absent and drew the
 * hunter's face at nothing. Infinity gates on any finite threshold, so the
 * caller needs no special case.
 */
function pursuitDistanceFor(kitty, world) {
  const ref = kitty.pursuit?.target;
  if (!ref) return null;
  const named = ref.target === 'element' || ref.target === 'kitty';
  if (!named || typeof ref.id !== 'number') return null;
  const pos =
    ref.target === 'element'
      ? world.elements.find((el) => el.id === ref.id)?.pos
      : world.kitties.find((k) => k.id === ref.id)?.pos;
  if (!pos) return Infinity;
  return Math.abs(kitty.pos.x - pos.x) + Math.abs(kitty.pos.y - pos.y);
}

/**
 * Where a served thing is DRAWN, which is where a look should land.
 *
 * Everything else in this file already keys visual relationships to the
 * drawn position -- the wade pose to "the tile under the DRAWN cat, not the
 * served destination", `submersionFor` to where the cat visibly is, the
 * depth layer to `elementPosFor`. A gaze aimed at a SERVED position aims at
 * where a moving quarry will be at the end of the tick, which on screen is
 * grass: measured over a live capture, half of all gaze-firing ticks had a
 * moving target, off by a median 8.1 degrees and up to 26.6.
 */
function drawnPosOf(obj, view, isElement) {
  if (!obj) return null;
  if (isElement) return view?.elementPosFor ? view.elementPosFor(obj) : obj.pos;
  return view?.posFor ? view.posFor(obj) : obj.pos;
}

/**
 * Where a kitty is looking, as a unit-ish vector in screen axes -- or
 * null when nothing in the served world has its attention.
 *
 * Read off `last_action`, so this predicts nothing and invents nothing: if
 * the engine said this cat is chasing that bug, the cat looks at that bug.
 * When nothing can be resolved the answer is null and the idle scan has the
 * channel instead -- the gaze has NO MEMORY (owner, 2026-08-13), so a cat
 * whose current action names nothing looks at nothing rather than holding a
 * stare at whatever it was doing before.
 *
 * Only the CHASE and PLAY shape is read -- `{target: kind, id: N}`. The other
 * two shapes the engine serves (`groom`'s bare kitty id, and eat/drink, which
 * name nothing and would have to be resolved from the map) are PARKED, and
 * that is a decision rather than an omission.
 *
 * They were built, measured and taken back out (owner, 2026-08-14). Reading
 * them took the gaze from 5.2% of cat-ticks to 36.5%, and it did not read:
 * the only gaze channel above the pixel floor at this tile is the ear lean,
 * which responds to the HORIZONTAL component alone, and 54% of the targets
 * those sources add sit directly north or south, where `gaze.x` is 0 and the
 * ears do not move at all. Grooming was the worst of them -- cats groom side
 * by side, so 59% of its ticks moved nothing and 26% leaned the ears away
 * from the cat's facing. Chase and play, which stay, read at 43%.
 *
 * The fix is a vertical channel for `gaze.y`, not more sources, and it wants
 * judging at camera zoom where the pupil (0.48px here) and the head follow
 * (0.35px) become legible. See the gaze entry in BACKLOG.md; the reader for
 * the parked shapes is recoverable from PR #221.
 *
 * `sleep.with` names a real co-sleeper and was never read: the eyes are shut
 * and `sleep-curl` skips the idle beats anyway.
 *
 * Vertical travel is damped: eyes move much further side to side than up
 * and down, and a pupil driven hard vertically reads as alarm.
 */
function gazeTargetFor(kitty, world, pos, view = null) {
  const ref = kitty.last_action;
  if (!ref) return null;
  if (ref.id === undefined || ref.id === null) return null;
  const at = ref.target === 'element'
    ? drawnPosOf(world.elements.find((el) => el.id === ref.id), view, true)
    : drawnPosOf(world.kitties.find((k) => k.id === ref.id), view, false);
  if (!at) return null;
  const dx = at.x - pos.x;
  const dy = at.y - pos.y;
  const m = Math.hypot(dx, dy);
  // Standing on the thing: there is no direction to look, and a cat on its
  // own bowl would otherwise get a gaze made of rounding error.
  if (m < 0.05) return null;
  return { x: dx / m, y: (dy / m) * 0.6 };
}

/** The cat's own ground line, in its 0..1 unit space (see cat-v2). */
const CAT_GROUND_Y = 0.88;

/**
 * The things that move under their own steam and are sorted by depth with
 * the cats, rather than stamped down with the furniture. Named once: the
 * kind list decides three separate things (glide, depth sorting, and which
 * pass draws them) and they have to agree.
 */
const CRITTER_KINDS = new Set(['bug', 'greeble']);

/**
 * Furniture that stands ON the ground rather than under it: it sorts with
 * the cats and the cover, but it does not move, so it keeps its served
 * tile. Water and sunbeams are not here -- they ARE the ground, and are
 * drawn beneath everything by their own passes.
 */
const PROP_KINDS = new Set(['chow']);

/**
 * How much of the cat is in water, 0..1 -- sampled from WHERE IT IS.
 *
 * This replaces a 260ms timer keyed on the nearest tile, and the change
 * of kind is the whole fix. Depth is a fact about a place: the old signal
 * eased toward a boolean and therefore kept easing for a quarter second
 * after the cat had left, so a cat standing on grass was still clipped at
 * a waterline and still missing its ground shadow. No amount of
 * retuning the fade could fix that -- a timer cannot know where the
 * shoreline is.
 *
 * Bilinear over the served water tiles, at the DRAWN (interpolated)
 * position. That gives three properties for free:
 *   - exactly 0 once every neighbouring tile is dry, so water cues can
 *     never appear on grass;
 *   - exactly 1 in a pond's interior;
 *   - smooth across the shore, so no fade is needed to avoid a pop --
 *     the cat wades in and the water rises because it MOVED.
 * And being a pure function of served data plus the drawn position, it
 * needs no per-cat state, survives a reconnect by construction, and is
 * already correct in a still frame.
 *
 * Mid-fade water counts at its own alpha, so a pond spawning under a cat
 * raises the water at the same rate the pond itself arrives.
 */
function submersionFor(pos, world, view) {
  const depth = new Map();
  for (const el of world.elements) {
    if (el.kind !== 'water') continue;
    const a = view?.elementAlphaFor ? view.elementAlphaFor(el) : 1;
    if (a > 0) depth.set(`${el.pos.x},${el.pos.y}`, a);
  }
  if (!depth.size) return 0;
  const at = (tx, ty) => depth.get(`${tx},${ty}`) ?? 0;
  const x0 = Math.floor(pos.x);
  const y0 = Math.floor(pos.y);
  const fx = pos.x - x0;
  const fy = pos.y - y0;
  return (
    at(x0, y0) * (1 - fx) * (1 - fy) +
    at(x0 + 1, y0) * fx * (1 - fy) +
    at(x0, y0 + 1) * (1 - fx) * fy +
    at(x0 + 1, y0 + 1) * fx * fy
  );
}

/**
 * The surface height, in the cat's unit space.
 *
 * One level for every pose (owner, 2026-08-10): the meadow's water is one
 * depth everywhere, so every cat in it must meet the surface at the same
 * height whatever it is doing there. A per-pose level was tried and cut --
 * it made one pond look like two, and moved the water under a cat that had
 * only changed pose.
 *
 * Kept as a function rather than inlining `VIEW.waterline` so there is
 * exactly one place that answers "where is the surface", and so the poses
 * cannot start disagreeing about it again.
 */
/**
 * May a swimming cat be drawn end-on, going this way?
 *
 * The two directions are judged separately on purpose. Only about 6px of a
 * 31px cat's body clears the waterline, so a swimming cat is mostly head
 * -- and `paintCat` draws no face on the back view by design, which makes
 * a cat swimming AWAY a featureless circle and two ears, while one
 * swimming TOWARD you wears the largest head in the vocabulary and a whole
 * face at the surface. `VIEW.swimAxial` is the owner's answer to that, and
 * 'none' keeps the side drawing that shipped.
 */
function swimAxialAllows(facing, dials = VIEW) {
  const mode = dials.swimAxial ?? 'none';
  if (mode === 'both') return true;
  if (mode === 'toward') return facing === 'south';
  return false;
}

function surfaceForPose(pose, dials = VIEW) {
  return dials.waterline;
}

/**
 * Where the surface cuts the cat, in its unit space -- or null when
 * nothing should be clipped (BACKLOG P1, the owner's idea).
 *
 * The clip is what makes the water+activity case work without a water
 * variant of every pose: `poseFor` deliberately lets drinking and
 * grooming outrank the wade, and occlusion is what makes those cats look
 * like they are standing in a pond.
 *
 * The swim pose is no longer exempt. Exempting it was what made the depth
 * jump: the surface simply vanished on the frame the pose flipped, so a
 * cat crossing into deep water changed level in one step. `surface` is
 * now passed in already blended across the pose change, so the cat sinks
 * into its swim depth instead of arriving at it.
 */
function waterlineFor(submersion, surface) {
  if (!(submersion > 0.01)) return null;
  return CAT_GROUND_Y - submersion * (CAT_GROUND_Y - surface);
}

/**
 * The meniscus, mutable for a lab like SWIM/GAIT/EYE.
 *
 * Toned down and cut to a half-arc 2026-08-10 (owner). Two things were
 * wrong at camera-mode sizes: it was too bright, and it was a closed
 * ellipse. The surface is drawn AFTER the cat -- it has to be, or it would
 * be clipped away with the legs -- so the far half of a closed ring paints
 * straight over the body it is supposed to be behind, and the whole thing
 * reads as a plate the cat is standing in rather than as water.
 *
 * Only the near half is drawn now: the arc from 0 to PI, which in canvas
 * angles is the half nearest the viewer. The far half is exactly the part
 * a real cat's body would hide.
 */
const MENISCUS = {
  fill: 0.16, // displaced water under the line (was 0.3, closed)
  line: 0.42, // the bright surface itself (was 0.85, closed)
  ring: 0.2, // the ring spreading off it (was 0.22 closed, then 0.1)
  rx: 0.38, // radius as a share of the tile
  ry: 0.062,
  breathe: 0.015, // how much rx pulses
};

class WorldRenderer {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.showGreebles = false;
    this.showGrid = false; // spec 008 FR-004: the demoted debug lattice
    this.showPaths = false; // spec 008 FR-009: worn trails, off by default
    // Happiness bars, off by default (owner, 2026-08-05): the cards carry
    // the same number in words, and a well-trained roster pins happiness
    // near its ceiling anyway -- so four near-full bars said little while
    // sitting exactly where the ground shadows fall. `h` brings them back.
    this.showHappiness = false;
    this.theme = 'day'; // 'day' | 'dusk' | 'night' -- set by setTheme
    // (app.js), which also swaps the MEADOW/PROPS palettes and clears
    // the ground cache
    this.tile = 22;
    this.cssWidth = 0;
    this.cssHeight = 0;
    this.groundCache = null;
    this.pondCache = null; // { signature, ponds } -- rebuilt on water change
    // Handed over by anim.init (spec 036). Undefined for a renderer used
    // without anim -- the lab, the harness -- which draws the whole world,
    // the same frame the camera reports while it is off.
    this.camera = null;
    // Set by applyTheme. The pond layers bake palette colours, so the
    // palette belongs in their key rather than in a null someone has to
    // remember to write.
    this.paletteKey = '';
    // The devicePixelRatio the backing store was actually sized with, not
    // whatever the display reports right now (issue #102). Null until the
    // first fit.
    this.dpr = null;
  }

  /**
   * Fits the canvas to the world and the screen, accounting for retina
   * displays. Runs every frame, so the fit is a pure function of the
   * world's dimensions and the viewport: a rotated phone -- or a world
   * that someday grows mid-session -- re-fits on the next frame, no
   * resize listener required.
   */
  resizeFor(world) {
    // v3 (2026-08-04): fitted to the room the map actually has, in BOTH
    // axes. This used to be a flat 720px cap on width alone, so a square
    // world simply overflowed the viewport vertically and the page
    // scrolled -- and for a square world HEIGHT is the binding axis,
    // because screens are wide and not tall. Measured rather than
    // hardcoded, so reclaiming a header or moving the cards beside the
    // map (see index.html) feeds straight back into tile size.
    //
    // A cat draws at exactly one tile, so the tile IS the cat, and this
    // is the one dial that sets how big cats are.
    const doc = document.documentElement;
    const stage = this.canvas.parentElement;
    const cell = stage ? stage.parentElement : null;
    const px = (el, ...sides) => {
      if (!el) return 0;
      const cs = getComputedStyle(el);
      return sides.reduce((sum, side) => sum + (parseFloat(cs[side]) || 0), 0);
    };
    const boxOf = (sel) => {
      const el = document.querySelector(sel);
      return el ? el.getBoundingClientRect().height : 0;
    };

    // The stage's FRAME, not just its padding: everything of the stage's own
    // box that sits between the viewport edge and the canvas. The phone
    // breakpoint retired the mat for a 1px hairline border (2026-08-19), and
    // a border a padding-only measurement cannot see is 2px the budget thinks
    // it has and does not -- the stage comes out wider than the width it was
    // sized against and the document scrolls sideways by two pixels.
    //
    // Harmless on every handset we fit, where the integer-tile slack is 8px
    // or more, and exactly the kind of thing that surfaces on the one
    // viewport whose slack is zero. Same class as the bake clamp measured in
    // CSS px against a budget in device px: the arithmetic was right and the
    // units were not.
    //
    // An `outline` with a negative offset was the alternative -- it draws
    // inside the border box and costs no layout at all, so this measurement
    // could have stayed padding-only. Rejected because it makes the box model
    // lie in the other direction: the line would be real to the eye and
    // invisible to every measurement, and a later change that thickened it
    // would silently eat the meadow instead of resizing the map.
    const stageFrameX = px(stage, 'paddingLeft', 'paddingRight',
      'borderLeftWidth', 'borderRightWidth');
    const stageFrameY = px(stage, 'paddingTop', 'paddingBottom',
      'borderTopWidth', 'borderBottomWidth');
    // Width the map may have: the layout's full width less whatever the
    // card columns take beside it. Measured from `.layout` rather than
    // from the map's own cell, because a content-sized cell is exactly as
    // wide as the canvas already in it -- ask that and the map can never
    // grow. When the cards are stacked below, the columns are
    // `display: contents` and measure zero, which is the right answer.
    //
    // Measured BEFORE the vertical chrome because it decides part of it:
    // whether the footer is under the map or under the cards.
    const layout = cell ? cell.parentElement : null;
    const columns = layout ? layout.querySelectorAll('.panel-col') : [];
    let besideWidth = 0;
    for (const column of columns) besideWidth += column.getBoundingClientRect().width;
    const gap = layout ? parseFloat(getComputedStyle(layout).columnGap) || 0 : 0;

    // Everything the map is not: header, the body's own padding, the stage's
    // frame, a little slack for the margins between -- and the footer, but
    // ONLY where the footer is the next thing under the map.
    //
    // It is not, below the 1100px breakpoint. There the columns dissolve
    // (`display: contents`) and the cards stack between the map and the
    // footer, so the page already scrolls to reach either of them -- accepted
    // outright (owner, 2026-08-05: phones may scroll for the cards), and
    // VERTICAL_SLACK's own comment says the fit invariant is narrower than it
    // reads for exactly this reason. Charging the map for a footer that is
    // hundreds of pixels below the fold buys nothing and costs a real tile.
    //
    // Measured, and it is not a rounding error: on a 16 Pro held sideways the
    // footer WRAPS to 52px of a 285px viewport. That is 18% of the entire
    // screen reserved for something off it -- the letterbox came out 2.85
    // world-rows tall where the same window affords 3.81. The landscape frame
    // is the one place this could ever have been visible, because everywhere
    // else the map is bound by WIDTH and the height budget is slack anyway.
    //
    // Where the cards DO sit beside the map, the footer really is next and is
    // still charged; the 1728x919 recording in test-motion.mjs is height-bound
    // and guards that branch.
    const chromeY =
      boxOf('header') + (besideWidth > 0 ? boxOf('footer') : 0) +
      px(document.body, 'paddingTop', 'paddingBottom') +
      stageFrameY + VERTICAL_SLACK;
    const widthBudget =
      (layout ? layout.clientWidth : doc.clientWidth) -
      besideWidth -
      (besideWidth > 0 ? gap * columns.length : 0) -
      stageFrameX;
    // Floored, and not only for tidiness: chromeY can exceed the viewport
    // on a very short window, and a negative budget used to reach `scale`
    // below and produce a negative CSS width. The CSSOM rejects that, so
    // `canvas.style.width` keeps its old value while the guard keeps
    // comparing it against a string that can never be assigned -- which
    // mismatches on EVERY frame and rebakes the whole ground cache at
    // 60fps. The tile had a floor already; the budget did not.
    const heightBudget = Math.max(120, (doc.clientHeight || 800) - chromeY);
    // A phone held sideways is the one viewport where fitting the height
    // is the wrong answer: a square world in a 280px-tall window is a
    // 12px tile whatever we reclaim, and there is half a screen of unused
    // WIDTH beside it. So on a short viewport the map fits the width and
    // overflows into a scroll instead -- owner call, 2026-08-07: "if they
    // want to scroll they can pinch zoom". Keyed to the same query the
    // landscape CSS uses, so "this screen is short" has one definition.
    const short =
      typeof matchMedia === 'function' && matchMedia('(max-height: 500px)').matches;
    this.tile = Math.max(
      8,
      Math.floor(
        Math.min(
          widthBudget / world.width,
          short ? Infinity : heightBudget / world.height,
          MAP_MAX_PX / Math.max(world.width, world.height),
        ),
      ),
    );
    const cssWidth = this.tile * world.width;
    // LETTERBOX (2026-08-19). A short viewport with the camera ON gets a
    // canvas the shape of the WINDOW, not the shape of the world.
    //
    // The landscape complaint was never the tile count. `resizeFor` builds a
    // SQUARE canvas -- the world is 20x20 -- and the short branch above fits
    // it to WIDTH, so on a phone held sideways the map is as tall as it is
    // wide and the page scrolls past the bottom of it. The camera is then
    // handed `aspect = cssHeight / cssWidth` = 1.0 and dutifully frames a
    // square, in a window that is nothing like square.
    //
    // MEASURED 2026-08-20, and the tile size is NOT what this buys -- it is
    // 54px either way. On the owner's handset held sideways (750x285, a 720px
    // canvas) the camera frames 13.3 tiles across in both cases. Square, that
    // is 13.3 rows down a 720px-tall canvas of which the window shows 206px,
    // and the frame is CENTRED on the canvas -- so the kitties the camera is
    // aiming at sit ~360px down a 285px window, off screen, and the user
    // scrolls to find the thing that is already being followed. Letterboxed,
    // the same 13.3 across becomes 3.8 rows and the strip the camera aims IS
    // the strip you can see.
    //
    // So the win is aim, not size, and the row count is set by
    // `heightBudget / tilePx` -- canvas width cancels out of it entirely.
    // Which is why the footer that `chromeY` used to charge below the fold
    // was worth a third of the frame: 2.85 rows against 3.81.
    //
    // Camera OFF is untouched, and that is the whole reason for the
    // condition: 036 SC-007 says the off state is indistinguishable from the
    // build before camera mode existed, and the square-plus-scroll IS that
    // build. Owner's call, 2026-08-07: "if they want to scroll they can pinch
    // zoom." Letterboxing the off state would silently crop the world instead.
    const letterbox = short && !!(this.camera && this.camera.on);
    const cssHeight = letterbox
      ? Math.max(this.tile, Math.min(heightBudget, this.tile * world.height))
      : this.tile * world.height;
    // Integer tiles keep the art crisp, but the 8px floor means a wide
    // enough world (45+ tiles) is irreducibly wider than a phone. The
    // display scale absorbs the difference: the canvas still renders at
    // the floor and the browser shrinks the result to fit.
    const scale = Math.max(
      0.05,
      Math.min(1, widthBudget / cssWidth, short ? Infinity : heightBudget / cssHeight),
    );
    const displayWidth = `${cssWidth * scale}px`;
    const displayHeight = `${cssHeight * scale}px`;
    const dpr = window.devicePixelRatio || 1;

    // The guard watches dpr as well as CSS width (issue #102). Dragging a
    // window between a Retina and a non-Retina display changes dpr while
    // the CSS width stays put, so a width-only guard left the backing
    // store at its old pixel size and old transform -- invisible on its
    // own, because everything drawn live is then stale *consistently*.
    // The damage surfaced minutes later, when the day->dusk->night change
    // nulled the ground cache and it rebaked at the old size with a fresh
    // dpr, putting the meadow in the upper-left quarter of the map.
    // HEIGHT is in the guard now, and the letterbox is why. Before it, height
    // was a pure function of width -- one tile count set both -- so a width
    // that had not moved proved a height that had not moved. Under the
    // letterbox they are independent: rotating a phone, or the browser bar
    // sliding away, changes the height budget while the width holds, and a
    // width-only guard would leave the backing store and the transform at the
    // old shape. That is issue #102 again, arrived at from the other axis.
    if (this.canvas.style.width !== displayWidth
      || this.canvas.style.height !== displayHeight
      || this.dpr !== dpr) {
      this.canvas.style.width = displayWidth;
      this.canvas.style.height = displayHeight;
      this.canvas.width = Math.floor(cssWidth * dpr);
      this.canvas.height = Math.floor(cssHeight * dpr);
      this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      this.dpr = dpr;
      this.groundCache = null; // new size, new ground
      this.pondCache = null; // and shorelines rebuilt at the new tile size
    }
    this.cssWidth = cssWidth;
    this.cssHeight = cssHeight;
  }

  /**
   * The camera (spec 036) reaches the drawing code through exactly two
   * values: the tile, which is the scale, and a translate, which is the
   * pan. Everything downstream then draws at camera scale untouched --
   * the 80-odd `this.tile` reads in this file, the 150-odd in meadow.js,
   * `tileOrigin`, and the handful of places that multiply by the tile
   * inline without going through it.
   *
   * Deliberately NOT `ctx.scale`. `this.tile` is the number every art
   * decision keyed to apparent size reads -- `fine = size >= 44` was the
   * headline example until it was deleted 2026-08-18, and every remaining
   * art dial is still a fraction of it --
   * and camera mode exists to cross that threshold. Scaling the finished
   * picture would magnify the SMALL-size drawing instead: bigger cats
   * still wearing their 31px detail.
   *
   * No camera means the whole-world view with the tile `resizeFor`
   * computed, which is also exactly what the camera returns while it is
   * off. The two agree on purpose. `anim.init` does the wiring and a
   * check in test-motion.mjs holds it there, because a dropped assignment
   * here would ship inert rather than loudly.
   */
  applyCamera(world, view, dpr) {
    const cam = this.camera;
    if (!cam) return;
    cam.update(world, view, {
      aspect: this.cssHeight / this.cssWidth,
      // The camera's only new input (spec 037). It works in tiles and the
      // renderer turns those into a tile size; give it the pixels and it
      // can decide the tile count FROM the size instead. The line below is
      // unchanged, and evaluates to the pixel target exactly.
      cssWidth: this.cssWidth,
    });
    this.tile = this.cssWidth / cam.across;
    this.ctx.setTransform(
      dpr,
      0,
      0,
      dpr,
      -cam.left * this.tile * dpr,
      -cam.top * this.tile * dpr,
    );
  }

  /**
   * Screen to world, derived from the transform `applyCamera` just laid
   * down rather than written a second time. Two hand-written transforms
   * drift, and the only symptom is clicks landing on the wrong kitty at
   * some zooms and not others.
   *
   * `rect` is the canvas's MEASURED size, which is not `cssWidth`:
   * `resizeFor` applies a display scale, so the canvas's layout size and
   * its drawing size differ whenever the map is wider than its budget.
   */
  /**
   * The visible rectangle in WORLD pixels -- the space everything is
   * drawn in, offset by the camera's pan.
   *
   * Anything that keeps itself on screen has to clamp against THIS, not
   * against the canvas box. The canvas box is 620px while the world under
   * a camera is 1240px wide, and the two used to be the same number, so a
   * clamp written against `canvas.clientWidth` looked right for years and
   * became a bug the moment a pan existed (spec 036): a bubble belonging
   * to a kitty out at x=18 was yanked to a coordinate with no relation to
   * her, and drew over empty grass while she was off-frame.
   *
   * `cssWidth` rather than `clientWidth` on purpose. `resizeFor` applies a
   * display scale, so the canvas's CSS box is smaller than its drawing
   * space whenever the map outgrows its budget -- which means the old
   * clamp also fired early on a narrow viewport, before the camera
   * existed. Same fix covers both.
   */
  viewportRect() {
    const cam = this.camera;
    const left = cam ? cam.left * this.tile : 0;
    const top = cam ? cam.top * this.tile : 0;
    return { left, top, right: left + this.cssWidth, bottom: top + this.cssHeight };
  }

  toWorld(clientX, clientY) {
    const rect = this.canvas.getBoundingClientRect();
    if (!rect.width || !rect.height) return null;
    const cssX = (clientX - rect.left) * (this.cssWidth / rect.width);
    const cssY = (clientY - rect.top) * (this.cssHeight / rect.height);
    const left = this.camera ? this.camera.left : 0;
    const top = this.camera ? this.camera.top : 0;
    return { x: left + cssX / this.tile, y: top + cssY / this.tile };
  }

  /**
   * Draws one frame: `world` is the newest served state, `view` the
   * presentational lens from anim.js (eased positions, fades, phases).
   * The same path serves animated and still frames -- a still frame is
   * simply progress 1 with fades off.
   */
  draw(world, view) {
    this.resizeFor(world);
    const ctx = this.ctx;
    // The pan is an absolute transform, re-set every frame rather than
    // accumulated -- and reset BEFORE the clear, or a panned frame clears
    // the wrong rectangle and leaves the previous one smeared at the edge.
    const dpr = this.dpr || window.devicePixelRatio || 1;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, this.cssWidth, this.cssHeight);
    this.applyCamera(world, view, dpr);

    // Which elements are being hunted right now (spec 007 FR-006): a pure
    // per-frame read of served pursuits, consumed by the butterfly's
    // panic flap. No store, no memory -- newest state wins.
    this.agitatedIds = new Set();
    for (const kitty of world.kitties) {
      const target = kitty.pursuit?.target;
      if (target && target.target === 'element') this.agitatedIds.add(target.id);
    }

    this.blitGround(world);
    // Worn paths sit directly on the grass, under everything that lives
    // (spec 008 US5); the grid overlay is debug chrome above them.
    if (this.showPaths && VIEW.meadow.paths) {
      drawWornPaths(ctx, { entries: view.wornPaths(), tile: this.tile });
    }
    if (this.showGrid && VIEW.meadow.gridOverlay) {
      drawGridOverlay(ctx, { width: world.width, height: world.height, tile: this.tile });
    }
    this.drawGroundAmbient(world, view);
    // Sunbeams are warmth on the ground, so they go under everything else.
    for (const el of world.elements) {
      if (el.kind === 'sunbeam') this.drawSunbeam(el, view.elementAlphaFor(el), view);
    }
    // Ponds: the merged, smooth-shored redrawing of exactly the served
    // water tiles (spec 008 US2). Mid-fade tiles stay individual pools.
    if (VIEW.meadow.ponds) this.drawPondLayer(world, view);
    // Expired elements take a brief bow instead of vanishing mid-glance.
    if (view.expired.length && view.expiredAlpha > 0) {
      for (const el of view.expired) {
        if (el.kind === 'sunbeam') this.drawSunbeam(el, view.expiredAlpha, view);
        // A critter taking its bow is still a critter: it sorts with the
        // rest, or it would pop behind the shrub it was just in front of
        // for the length of its fade.
        else if (!CRITTER_KINDS.has(el.kind) && !PROP_KINDS.has(el.kind)) {
          this.drawElement(el, view.expiredAlpha, view);
        }
      }
    }
    for (const el of world.elements) {
      if (el.kind === 'sunbeam') continue;
      // Critters are sorted with the cats and the cover instead -- see the
      // depth layer below. Drawing them here would put every butterfly
      // behind every shrub, whatever the ground said.
      if (CRITTER_KINDS.has(el.kind) || PROP_KINDS.has(el.kind)) continue;
      if (el.kind === 'water' && VIEW.meadow.ponds && view.elementAlphaFor(el) >= 1) {
        // Drawn by the pond body already -- and since the pond restyle its
        // surface motion is the caustic net, one per POND, so a per-tile
        // shimmer on top would double it and re-tile a merged pond. The
        // standalone mid-fade pools below keep theirs.
        continue;
      }
      this.drawElement(el, view.elementAlphaFor(el), view);
    }
    // Cats and ground cover, interleaved by depth (v3, 2026-08-05).
    //
    // Ground cover used to bake into the ground cache, which sits under
    // everything -- so a cat crossing a shrub walked over the top of it.
    // Sorting the two together by their drawn y is what lets a cat pass
    // BEHIND one. Only these two participate: bubbles and thought
    // bubbles already run as their own passes below, so they stay clear
    // of cover for free, and served elements stay out of the ordering
    // rather than being sorted -- which avoids dragging bowls and
    // butterflies into it.
    //
    // That used to be free, because cover was kept off every served
    // element's tile. `occupiedTiles` now yields water only (see there for
    // why), so it is no longer free: the element pass above draws first,
    // so a shrub or tree sharing a tile with a bowl or a toy is painted
    // OVER it. Owner accepted that trade against the alternative -- trees
    // blinking out wherever a bug walked -- but it is a real edge, not the
    // guarantee this comment used to claim.
    const cover = typeof bushesFor === 'function'
      ? bushesFor(world.width, world.height, VIEW.meadow, this.occupiedTiles(world))
      : [];
    const layer = [];
    for (const bush of cover) {
      // Sorted by GROUND CONTACT, not by tile position: what decides
      // which of two things is in front is where each one meets the
      // earth. A cat's ground line is 88% down its box (the same 0.88 the
      // landing settle and the header wordmark use); a shrub's is its
      // base, below the canopy that stands up off it. Keying either by
      // its tile instead put a shrub on top of a cat sharing its tile --
      // the exact bug the sort exists to fix.
      layer.push({
        kind: 'cover',
        y: coverSortKey(bush, VIEW.meadow),
        draw: () => drawBushAt(this.ctx, { ...bush, tile: this.tile, t: VIEW.meadow }),
      });
    }
    // Critters join the sort (owner, 2026-08-11). A butterfly stands on
    // the ground the same way a cat does -- it just hovers a little above
    // where it stands -- so it takes the CAT's ground line, and the rank
    // decides the tie: kitty in front of bug in front of bush. Keyed to
    // the DRAWN position, not the served tile, or a gliding critter would
    // change depth a tick before or after it visibly crosses the shrub.
    for (const el of world.elements) {
      if (CRITTER_KINDS.has(el.kind)) {
        layer.push({
          kind: 'critter',
          y: catSortKey(view.elementPosFor(el)),
          draw: () => this.drawElement(el, view.elementAlphaFor(el), view),
        });
      } else if (PROP_KINDS.has(el.kind)) {
        // A bowl stands where a cat stands, so it takes the cat's ground
        // line: cover rooted in the same tile meets the earth higher up
        // and sorts behind it. Owner, 2026-08-12 -- a shrub was painting
        // over the bowl it shared a tile with, which is the trade
        // `occupiedTiles` took when it stopped keeping cover off served
        // elements. It does not glide, so its served tile is its place.
        layer.push({
          kind: 'prop',
          y: catSortKey(el.pos),
          draw: () => this.drawElement(el, view.elementAlphaFor(el), view),
        });
      }
    }
    if (view.expired.length && view.expiredAlpha > 0) {
      for (const el of view.expired) {
        if (!CRITTER_KINDS.has(el.kind) && !PROP_KINDS.has(el.kind)) continue;
        layer.push({
          kind: CRITTER_KINDS.has(el.kind) ? 'critter' : 'prop',
          y: catSortKey(el.pos),
          draw: () => this.drawElement(el, view.expiredAlpha, view),
        });
      }
    }
    for (const kitty of world.kitties) {
      layer.push({
        kind: 'kitty',
        y: catSortKey(view.posFor(kitty)),
        draw: () => this.drawKitty(kitty, world, view),
      });
    }
    for (const item of spriteOrder(layer)) item.draw();

    this.drawBubbles(world, view);
    // Thought bubbles sit above speech in the stack (the documented
    // two-beats rule): at most one per kitty, only while the wait is long.
    for (const kitty of world.kitties) {
      const need = view.thoughtFor(kitty);
      if (need) this.drawThought(kitty, need, view);
    }
  }

  /**
   * The meadow never changes between resizes, so it is rendered once to
   * an offscreen layer and blitted per frame (005 research R7) -- the
   * difference between thousands of fills and one drawImage each frame.
   * The grid lines that used to live here are now the debug-only overlay
   * behind `l` (spec 008 FR-004).
   */
  /**
   * Tiles the ground cover must keep off, and ONLY the ones that will still
   * be there next tick.
   *
   * This used to take every served element, which made trees blink: a bug or
   * a greeble skittering across the meadow occupied a tile for a moment, the
   * tree standing there vanished, and it came back when the critter moved on
   * (owner-reported 2026-08-07; measured at one flickering tile in 41 samples
   * of a fast world, the culprit a greeble). Chow and sunbeams do the same
   * more slowly, by spawning and expiring.
   *
   * Water is the only element that is a fact about the world rather than an
   * event in it -- placed at worldgen and fixed for the world's life -- so
   * keying on it alone makes the cover a pure function of the map, stable for
   * the session, which is what scenery has to be. A bowl can now spawn on a
   * tree's tile; at a 1.5% cover chance that is about one tile in eight
   * worlds, and a bowl briefly under a canopy is a far smaller wrong than
   * trees popping in and out everywhere a bug walks.
   */
  occupiedTiles(world) {
    const taken = new Set();
    for (const el of world.elements) {
      if (el.kind !== 'water') continue;
      taken.add(`${el.pos.x},${el.pos.y}`);
    }
    return taken;
  }

  /**
   * The pond layers' bake tile: the ground's, held under a tighter bound.
   * Past the bound the shorelines are drawn at a coarser tile and scaled
   * up, which a blurred band and a damp lip carry far better than the
   * ground's grass and flowers would.
   */
  pondBakeTileFor(world) {
    const bakeTile = this.bakeTileFor(world);
    // Camera off is camera off. `bakeTileFor` deliberately skips its own
    // clamp there so the ground is byte-for-byte what shipped, and a
    // clamp here would undo that for the ponds: on a 5K display the tile
    // reaches ~59 and the bound would drop the bake to 51.2, softening
    // the shore, lip, meniscus and lily pads AND pushing the off-state
    // pond path through the ctx.scale branch its comment promises it
    // never takes. The claim has to hold for every layer, not the one I
    // happened to be looking at.
    if (!this.camera || !this.camera.on) return bakeTile;
    const dpr = this.dpr || window.devicePixelRatio || 1;
    const widest = Math.max(world.width, world.height);
    const maxSide = POND_BAKE_MAX_PX / dpr;
    return Math.max(1, bakeTile * widest > maxSide ? maxSide / widest : bakeTile);
  }

  /**
   * The tile the ground bakes at: the one the camera produces at its
   * NARROWEST frame, which is the largest it can ever ask for.
   *
   * Baking there is what makes camera mode affordable. Every per-frame
   * blit is then a downscale, so the ground is never magnified into
   * softness under crisp vector cats, and -- the part that matters for
   * SC-003 -- zooming and panning change only the SOURCE RECTANGLE. The
   * rebake triggers stay exactly what they were before the camera: dpr,
   * canvas resize, palette step, world change.
   *
   * That is not a small distinction. render.js has already shipped a bug
   * where a guard mismatched every frame and rebaked the whole ground at
   * 60fps (see the note in resizeFor); a bake keyed to a per-frame tile
   * would reproduce it by design rather than by accident.
   *
   * With the camera off this returns the whole-world tile, so the bake is
   * pixel-for-pixel the one that shipped before this feature.
   */
  bakeTileFor(world) {
    // Camera off: the whole-world tile, unclamped, which is byte-for-byte
    // the bake that shipped before this feature -- an offscreen the size
    // of the canvas. Clamping here too would have magnified the ground on
    // a dpr-4 display and, worse, made `this.tile / bakeTile` differ from
    // 1, pushing the off-state pond path through a scale it is documented
    // never to take. The claim "nothing moved" has to survive every dpr,
    // not the ones I happened to think of.
    if (!this.camera || !this.camera.on) return this.cssWidth / world.width;

    // Camera on: the tile at the narrowest frame, from the camera's OWN
    // derivation. Reaching for the module global instead would let a Camera
    // built with different dials ask for a tile larger than the bake, and
    // every blit would silently become the upscale this exists to prevent.
    //
    // Under 037 this is the camera's FLOOR, which is the pixel target
    // wherever it is reachable -- so the bake stops scaling with the display
    // and gets SMALLER on a large one (research R3). Same pair the fit and
    // `bound` read, so the bake and the frame can never disagree about the
    // band.
    //
    // And it is a downscale only while GROUND_BAKE_MAX_PX does not bind. That
    // budget is in DEVICE px (4096 / dpr), so above dpr ~2.05 a 100px floor
    // tile on a 20-tile world wants a 2000 CSS px bake and is clamped to
    // 1365 -- a 1.46x UPSCALE at the zoom floor, in steady state. It predates
    // 037 (a 1200px map at dpr 2 was already 1.17x on the old fixed floor);
    // 037 improves the worst case and widens the band. Parked in BACKLOG.md,
    // because the fix couples the camera's floor to this budget.
    //
    // The downscale is also a STEADY-STATE claim in TIME. `cssWidth`
    // changes the instant a window is resized while `across` EASES toward
    // its new floor at zoomRate, so widening 700px -> 1200px with the group
    // huddled leaves `this.tile` above `bakeTile` for about a second and the
    // ground blit is briefly an upscale. Soft, not broken, and it ends when
    // the ease does. Worth knowing before anyone reads "always a downscale"
    // and trusts it mid-resize -- under the old fixed nominalAcross this
    // could not happen, because the floor did not move with the viewport.
    const narrowest = this.camera.limitsFor(world, this.cssWidth).floorTiles;
    const dpr = this.dpr || window.devicePixelRatio || 1;
    const widest = Math.max(world.width, world.height);
    const bakeTile = this.cssWidth / narrowest;
    const maxSide = GROUND_BAKE_MAX_PX / dpr;
    return Math.max(1, bakeTile * widest > maxSide ? maxSide / widest : bakeTile);
  }

  blitGround(world) {
    // The cache's transform must be the ratio the canvas was SIZED with,
    // never a freshly-read devicePixelRatio (issue #102): reading the
    // display's current dpr here straddles the two and paints the meadow
    // into a corner of its own cache. Belt and braces on top of the
    // resize guard -- the stamp catches any future path that clears the
    // cache without a resize.
    const dpr = this.dpr || window.devicePixelRatio || 1;
    const bakeTile = this.bakeTileFor(world);
    const bakeW = Math.round(world.width * bakeTile * dpr);
    const bakeH = Math.round(world.height * bakeTile * dpr);
    const stale =
      !this.groundCache ||
      this.groundCache.dataset.dpr !== String(dpr) ||
      this.groundCache.dataset.bakeTile !== String(bakeTile) ||
      this.groundCache.width !== bakeW;
    if (stale) {
      const off = document.createElement('canvas');
      off.width = bakeW;
      off.height = bakeH;
      const g = off.getContext('2d');
      g.setTransform(dpr, 0, 0, dpr, 0, 0);
      // `cover: false` -- ground cover is drawn per frame instead, sorted
      // against the cats so they can pass behind it (see draw()).
      drawMeadowGround(g, { width: world.width, height: world.height, tile: bakeTile, cover: false });
      off.dataset.dpr = String(dpr);
      off.dataset.bakeTile = String(bakeTile);
      this.groundCache = off;
    }
    // Source rect in bake pixels, destination in world pixels -- the
    // context is panned, so the destination is where the frame sits in
    // the world, not at the canvas origin. With the camera off this is
    // the whole cache onto the whole canvas, exactly as before.
    const cam = this.camera;
    const left = cam ? cam.left : 0;
    const top = cam ? cam.top : 0;
    const across = cam ? cam.across : world.width;
    const down = across * (this.cssHeight / this.cssWidth);
    // The source rect is clamped to the cache it reads from. The bake's
    // dimensions are rounded and this rect is not, so on a fractional dpr
    // the source could run a fraction of a pixel past the image -- and
    // drawImage clips source and destination TOGETHER, which paints the
    // ground a hair narrow and leaves an unpainted strip down the right
    // edge. The old 5-argument blit had no source rect and could not
    // disagree with itself this way.
    const sx = Math.min(left * bakeTile * dpr, bakeW);
    const sy = Math.min(top * bakeTile * dpr, bakeH);
    this.ctx.drawImage(
      this.groundCache,
      sx,
      sy,
      Math.min(across * bakeTile * dpr, bakeW - sx),
      Math.min(down * bakeTile * dpr, bakeH - sy),
      left * this.tile,
      top * this.tile,
      across * this.tile,
      down * this.tile,
    );
  }

  /**
   * The pond layer (spec 008 US2): group the fully-present served water
   * tiles, cache their smooth shorelines under the position signature,
   * and redraw the cached paths -- rebuild only when water actually
   * spawns or expires. Mid-fade tiles are excluded here and drawn as
   * their own small pools by drawElement, at the element alpha.
   */
  drawPondLayer(world, view) {
    const stable = [];
    for (const el of world.elements) {
      if (el.kind === 'water' && view.elementAlphaFor(el) >= 1) stable.push(el.pos);
    }
    if (!stable.length) {
      this.pondCache = null;
      return;
    }
    // This cache is built from three things and used to key on one.
    //
    // The PALETTE, because `buildPondLayers` bakes MEADOW.pondShore and
    // MEADOW.pondLip into the shore and lip canvases. Keyed on the water
    // tiles alone, the layers survived every palette step: the grass, the
    // pond body and the meniscus all crossed into night while the shore
    // band and the damp lip stayed in daylight paint, for the rest of the
    // session. Fixed on main, 2026-08-17.
    //
    // The TILE, because the paths and layers are built at one. That was
    // safe for a reason that is not the obvious one -- `resizeFor` nulls
    // this cache on canvas resize, and before the camera every way the
    // tile could change went through a resize. A camera changes the tile
    // with no resize at all, so nothing would fire, the signature would
    // match, and the ponds would draw at the previous zoom's geometry.
    //
    // Two independent staleness bugs in one cache, found a day apart, from
    // one cause: a cache keyed on a subset of what it bakes is only ever
    // safe because something else invalidates it.
    const dpr = this.dpr || window.devicePixelRatio || 1;
    const bakeTile = this.pondBakeTileFor(world);
    const water = stable.map((p) => `${p.x},${p.y}`).sort().join(';');
    const signature = `${this.paletteKey}|${bakeTile}|${water}`;
    if (!this.pondCache || this.pondCache.signature !== signature) {
      const groups = groupWaterTiles(stable);
      const ponds = groups.map((tiles) => ({ tiles, path: buildPondPath(tiles, bakeTile) }));
      this.pondCache = {
        signature,
        ponds,
        // Depth and lip bake here, where the paths are already being
        // rebuilt -- so the blur is paid once per water change, not once
        // per frame. Two layers for the whole world, not two per pond.
        // Built at the bake tile like the ground, so camera movement
        // never reaches this blur.
        layers: buildPondLayers(ponds, {
          tile: bakeTile,
          widthPx: Math.round(world.width * bakeTile * dpr),
          heightPx: Math.round(world.height * bakeTile * dpr),
          dpr,
        }),
      };
    }
    // Bake geometry drawn at camera scale. The factor is 1 whenever the
    // camera is off, and the guard keeps the no-op transform out of the
    // draw log so the off state stays command-for-command what it was.
    const scale = this.tile / bakeTile;
    const scaled = scale !== 1;
    if (scaled) {
      this.ctx.save();
      this.ctx.scale(scale, scale);
    }
    const cam = this.camera;
    drawPonds(this.ctx, {
      ponds: this.pondCache.ponds,
      tile: bakeTile,
      layers: this.pondCache.layers,
      // Only the visible slice of the world-sized layers. In bake-tile
      // pixels, because that is the space this call draws in.
      clip: cam
        ? {
            x: cam.left * bakeTile,
            y: cam.top * bakeTile,
            w: cam.across * bakeTile,
            h: cam.across * (this.cssHeight / this.cssWidth) * bakeTile,
          }
        : null,
      // Same clock and same flag the per-tile shimmer used, since the
      // caustics replace it: reduced motion still stills the water.
      now: view?.ambient?.now ?? 0,
      motion: view?.ambient?.now !== undefined && VIEW.ambient.waterShimmer,
    });
    if (scaled) this.ctx.restore();
  }

  /**
   * The surface where it meets a cat (2026-08-10).
   *
   * The clip alone says "the bottom of this cat is missing", which is not
   * the same statement as "this cat is in water" -- a hard edge across a
   * silhouette reads as a rendering fault before it reads as a pond. What
   * makes it water is the meniscus: a bright line riding the surface, and
   * the water darkening where the cat displaces it.
   *
   * This is also what makes the two depths legible. A wading cat and a
   * swimming cat sit at different levels, and until the surface was drawn
   * there was nothing to tell the viewer that the difference was depth
   * rather than the cat changing size.
   *
   * Gated on `submersion`, so it cannot appear on grass.
   */
  drawWaterline(cx, y, cut, submersion, view) {
    if (!(submersion > 0.01)) return;
    const ctx = this.ctx;
    const lineY = y + cut * this.tile;
    // A slow breath, so the surface is never a frozen decal. Same clock
    // and same flag as the caustics, so reduced motion stills it too.
    const now = view?.ambient?.now;
    const still = now === undefined || !VIEW.ambient.waterShimmer;
    const pulse = still ? 0 : Math.sin(now / 700 + cx * 0.05);
    const rx = this.tile * (MENISCUS.rx + MENISCUS.breathe * pulse) * (0.75 + 0.25 * submersion);
    const ry = Math.max(0.6, this.tile * MENISCUS.ry);
    // The near half only, 0 to PI: canvas angles run clockwise from +x
    // with +y downward, so this is the arc between the two ends of the
    // waterline passing in FRONT of the cat. The far half is the part its
    // body would hide, and drawing it here -- on top of the cat, since the
    // surface has to be painted after the clip is released -- is what made
    // this read as a plate.
    const nearArc = (radX, radY, dy) => {
      ctx.beginPath();
      ctx.ellipse(cx, lineY + dy, radX, radY, 0, 0, Math.PI);
    };

    ctx.save();
    // Displaced water: a little pool of shadow hugging the cat, which is
    // what gives the waterline something to sit ON. Closed along the
    // waterline itself, so its flat edge IS the surface.
    ctx.globalAlpha = MENISCUS.fill * submersion;
    ctx.fillStyle = MEADOW.pondRim;
    nearArc(rx * 1.12, ry * 1.5, ry * 0.35);
    ctx.closePath();
    ctx.fill();
    // The meniscus itself: brightest right at the cut.
    ctx.globalAlpha = MENISCUS.line * submersion;
    // The PER-THEME surface colour, not a fixed mix toward white.
    //
    // The handoff lightened `pondWater` 50% toward white, which is the
    // daylight assumption the pond restyle (#177) was built to retire: a
    // constant mix is a statement about how much sun there is. Measured in
    // CIE L*, that expression lands within a few points of this palette
    // entry by day (94.1 vs 97.8) and dusk (87.5 vs 93.2) -- and 33.5
    // points too bright at NIGHT (66.7 vs 33.2), where it would paint a
    // near-daylight line across a cat standing in a pond drawn at L* 33.
    // Same shape of bug the night shore band had, same fix: the palette
    // already answers this per theme, so ask it.
    ctx.strokeStyle = MEADOW.pondMeniscus ?? MEADOW.pondRim;
    ctx.lineWidth = Math.max(1, this.tile * 0.045);
    nearArc(rx, ry, 0);
    ctx.stroke();
    // ...and one ring spreading off it, faint enough not to fight the
    // pond's own caustics -- which is what retired the old wetRipple.
    ctx.globalAlpha = MENISCUS.ring * submersion;
    ctx.lineWidth = Math.max(1, this.tile * 0.03);
    nearArc(rx * (1.35 + 0.06 * pulse), ry * 1.7, ry * 0.5);
    ctx.stroke();
    ctx.restore();
  }

  /** The shimmer sliding across a water surface (005 US6), shared by the
   * pond body and the standalone pools. */
  drawWaterShimmer(el, view) {
    const t = view?.ambient?.now;
    if (t === undefined || !VIEW.ambient.waterShimmer) return;
    const ctx = this.ctx;
    const { x, y } = this.tileOrigin(el.pos);
    const cx = x + this.tile / 2;
    const cy = y + this.tile / 2;
    ctx.save();
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.55)';
    ctx.lineWidth = 1.2;
    ctx.lineCap = 'round';
    const drift = Math.sin(t / 1600 + el.id) * this.tile * 0.14;
    for (const [dx, dy, len] of [[-0.18, -0.12, 0.24], [0.06, 0.14, 0.18]]) {
      ctx.beginPath();
      ctx.moveTo(cx + dx * this.tile + drift, cy + dy * this.tile);
      ctx.lineTo(cx + (dx + len) * this.tile + drift, cy + dy * this.tile);
      ctx.stroke();
    }
    ctx.restore();
  }

  /**
   * Ambient life on the ground layer (US6, FR-013): each effect sits behind
   * its own named VIEW flag, stays subtle, and is absent entirely when the
   * view carries no ambient clock (reduced motion).
   */
  drawGroundAmbient(world, view) {
    if (!view.ambient) return;
    const ctx = this.ctx;
    const t = view.ambient.now;

    // Cloud shadows are sunlight's doing, so the night sky has none
    // (owner call, 2026-07-23) -- and their greenish daytime tint read
    // wrong on moonlit grass anyway.
    if (VIEW.ambient.cloudShadows && this.theme !== 'night') {
      // Two soft shadows drifting slowly across the meadow.
      ctx.save();
      ctx.fillStyle = 'rgba(120, 140, 110, 0.05)';
      // The world's drawn extent, NOT the canvas's. Before camera mode the
      // two were the same number and these read `cssWidth`/`cssHeight`;
      // under the camera the world spans `world.width * tile` while the
      // canvas stays put, so the old reads crowded both shadows into the
      // top third of the meadow and drifted them across the wrong width.
      // This is the one place the "everything downstream goes through
      // this.tile" audit was wrong.
      const worldW = world.width * this.tile;
      const worldH = world.height * this.tile;
      for (const [speed, cy, ry] of [[1, 0.28, 3.2], [1.35, 0.72, 2.4]]) {
        const span = worldW + this.tile * 12;
        const cx = ((t * speed) / VIEW.cloudPeriodMs) * span % span - this.tile * 6;
        ctx.beginPath();
        ctx.ellipse(cx, cy * worldH, this.tile * 5, this.tile * ry, 0.3, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.restore();
    }

    // (Grass sway retired 2026-07-22: its fixed-pixel blades read as stray
    // diagonal lines at small tile sizes. A tile-proportional return is
    // queued with the meadow finishing touches in BACKLOG.md.)
  }

  drawSunbeam(el, alpha = 1, view) {
    const ctx = this.ctx;
    const { x, y } = this.tileOrigin(el.pos);
    const t = view?.ambient?.now;
    // The warm pulse: a slow breathing of the beam's glow (US6).
    const pulse =
      t !== undefined && VIEW.ambient.sunbeamPulse
        ? 0.92 + 0.08 * Math.sin(t / 1900 + el.id)
        : 1;
    ctx.save();
    if (VIEW.meadow.glow) {
      // Light, not a tile (spec 008 US4): the warm radial pool bleeding
      // softly past the tile bounds, breathing on the same pulse.
      drawSunbeamGlow(ctx, {
        cx: x + this.tile / 2,
        cy: y + this.tile / 2,
        tile: this.tile,
        alpha: alpha * pulse,
      });
    } else {
      // The glow layer disabled: a plain warm tile keeps the beam readable.
      ctx.globalAlpha = alpha * pulse;
      ctx.fillStyle = MEADOW.glowMid;
      this.roundRect(x + 1, y + 1, this.tile - 2, this.tile - 2, 6);
      ctx.fill();
      ctx.globalAlpha = 1;
    }

    if (t !== undefined && VIEW.ambient.dustMotes) {
      // Two lazy dust motes circling in the warmth.
      ctx.fillStyle = MEADOW.moteColor;
      for (const i of [0, 1]) {
        const angle = t / (2600 + i * 700) + el.id * 2.1 + i * Math.PI;
        const mx = x + this.tile / 2 + Math.cos(angle) * this.tile * 0.28;
        const my = y + this.tile / 2 + Math.sin(angle * 1.3) * this.tile * 0.24;
        ctx.globalAlpha = alpha * (0.4 + 0.3 * Math.sin(angle * 2));
        ctx.beginPath();
        ctx.arc(mx, my, 1.1, 0, Math.PI * 2);
        ctx.fill();
      }
    }
    ctx.restore();
  }

  drawElement(el, alpha = 1, view) {
    // The greeble rule: present in the data, absent from the picture.
    if (el.kind === 'greeble' && !this.showGreebles) return;

    const ctx = this.ctx;
    ctx.save();
    ctx.globalAlpha = alpha;
    // Critters glide between served states (007 refinement); furniture
    // stands still, as furniture does.
    const isCritter = CRITTER_KINDS.has(el.kind);
    const pos = isCritter && view ? view.elementPosFor(el) : el.pos;
    const { x, y } = this.tileOrigin(pos);

    switch (el.kind) {
      case 'water': {
        // The standalone pool: mid-fade (spawning/expiring) water, and
        // every water tile when the pond layer is disabled (spec 008
        // US2). Fully-present water otherwise draws as the merged pond
        // body in drawPondLayer.
        ctx.fillStyle = MEADOW.pondWater;
        this.roundRect(x + 2, y + 2, this.tile - 4, this.tile - 4, 8);
        ctx.fill();
        ctx.strokeStyle = MEADOW.pondRim;
        ctx.lineWidth = 1.5;
        ctx.stroke();
        this.drawWaterShimmer(el, view);
        break;
      }
      case 'chow': {
        // The terracotta bowl whose kibble mound IS the servings display
        // (spec 007 FR-004) -- the old meter bar is gone with the emoji.
        drawBowl(ctx, { servings: el.servings ?? 0, size: this.tile, x, y });
        break;
      }
      case 'bug':
        // Drawn as a butterfly (spec 007): its own stable colorway, wings
        // on the flap clock, hover above a grounded shadow, and a panicked
        // beat while any kitty's served pursuit names it (FR-005/006).
        drawButterfly(ctx, {
          colorway: butterflyColorwayFor(el.id),
          phase: view.propPhaseFor(el.id, VIEW.props.flapPeriodMs),
          bobPhase: view.propPhaseFor(el.id, VIEW.props.bobPeriodMs),
          agitated: this.agitatedIds?.has(el.id) ?? false,
          firefly: this.theme !== 'day', // fireflies from dusk onward
          size: this.tile,
          x,
          y,
        });
        break;
      case 'greeble':
        // Only ever reached with the debug toggle on: the wisp, wearing
        // the gate-chosen grin. Still translucent -- it is a ghost -- but
        // legible: at the original 0.55 the pale body vanished into the
        // grass and the toggle looked broken (owner call, 2026-07-22).
        ctx.globalAlpha = 0.8 * alpha;
        drawGreebleWisp(ctx, {
          face: GREEBLE_FACE,
          phase: view.propPhaseFor(el.id, VIEW.props.wispBobMs),
          size: this.tile,
          x,
          y,
        });
        break;
      default:
        break;
    }
    ctx.restore();
  }

  drawKitty(kitty, world, view) {
    const ctx = this.ctx;
    const pos = view.posFor(kitty);
    const { x, y } = this.tileOrigin(pos);
    const cx = x + this.tile / 2;
    const cy = y + this.tile / 2;
    const state = kitty.activity?.state ?? 'idle';

    // Live motion and the swim pose are v2-vocabulary affairs: the
    // dispatcher installs drawCatTween exactly when v2 kitties are
    // active, so v1 keeps its pose snap, its snap blink, and its
    // walk-through-water by construction.
    const v2Motion = typeof drawCatTween === 'function';
    // A kitty over a water tile is wading (spec 010's parked swim pose).
    // Keyed on the tile under the DRAWN cat -- the eased interpolation,
    // not the served destination -- so the pose flips as the cat visibly
    // crosses the shore (mid-tick; the tween machinery blends it there),
    // never a full glide early. The served elements are the truth about
    // where water is, mid-fade or not.
    // How deep, sampled from the drawn position (see submersionFor). The
    // pose reads the same number so the wade pose and the water level can
    // never disagree about where the shoreline is -- they used to be two
    // separate readings of it.
    const submersion = v2Motion ? submersionFor(pos, world, view) : 0;
    const onWater = submersion >= 0.5;

    // The approved vector cat (spec 005 US2/US4/US5): identity from the
    // kitty's id, pose from served state (with the fall-asleep settle),
    // facing from its last horizontal movement, motion from the animation
    // layer -- and the drama layered by the documented rule: pose, then
    // action animation, then expression, then the single one-shot beat.
    const served = view.adjustPose(
      kitty.id,
      poseFor(kitty, view.movedFor(kitty.id), onWater, chaseDistanceFor(kitty, world)),
    );
    // A cat with nothing asked of it may sit, or stretch on waking. Both
    // are things a cat does while doing NOTHING, so neither can imply an
    // action (FR-008) -- and because both are ordinary poses, the pose
    // tween gives the sitting-down and the standing-up for free.
    const own = v2Motion && view.idlePoseFor ? view.idlePoseFor(kitty.id, served) : null;
    const pose = own ? own.pose : served;

    const motion = view.motionFor(kitty.id, pose);
    if (own && own.phase !== undefined) motion.phase = own.phase;
    const beat = view.oneShotFor(kitty.id);
    let eyes = motion.eyesOverride;
    let ears = motion.earsBack;
    // Ears held back as a MOOD, as opposed to the transient twitch. Only
    // the mood goes through the rig, where it eases; the twitch has its
    // own continuous channel, and letting both drive one input would make
    // every twitch look like a flinch.
    let earsHold = false;
    let lid;
    if (v2Motion && motion.blinkLid !== undefined) {
      lid = motion.blinkLid;
      if (eyes === 'closed') eyes = undefined; // the eased lid replaces the snap blink
    }
    const expression = view.expressionFor(kitty, pursuitDistanceFor(kitty, world));
    // On the v2 path a pursuit's focused eyes hold through the blink slot
    // -- drawFace exempts 'focused' from the lid, so hunters keep their
    // unbroken stare (v1 still snap-blinks over focused, as it always
    // has). Locked (owner, 2026-08-02): hunting kitties do not blink.
    if (expression && !eyes) eyes = expression;
    if (beat?.kind === 'sad') {
      // The give-up droop wears on the cat itself: ears back, eyes low --
      // and it outranks a blink in progress, exactly as it did pre-lid
      // (a full lid would promote the droop to the happy closed arcs).
      ears = true;
      earsHold = true;
      eyes = 'half';
      lid = undefined;
    }
    const tween = v2Motion && view.tweenFor ? view.tweenFor(kitty.id, pose, motion.phase) : null;

    // The rig (2026-08-10): the motion that is not a pose. Velocity comes
    // from the served pair analytically, gaze from the served action, and
    // the springs live in the animation layer -- so a still frame passes
    // no rig at all and draws exactly the vocabulary it always did.
    const turn = v2Motion && view.turnFor ? view.turnFor(kitty.id) : null;
    // The facing as DRAWN, which mid-turn is still the pre-turn one. The
    // rig has to see the same value the drawing does, or it flips its
    // world-space momentum half a turn early.
    const drawnFacing =
      typeof turnFacing === 'function'
        ? turnFacing(view.facingFor(kitty.id), turn)
        : view.facingFor(kitty.id);
    // Four facings (2026-08-10). North is walking away, south is walking
    // toward -- but only poses with an axial DRAWING can wear them, so
    // anything else falls back to the cat's last east/west facing rather
    // than to a view that does not exist. That fallback is the whole
    // reason `sideFacingFor` is remembered separately: a cat that walks
    // north and then grooms should face the way it last plausibly did.
    const axialPose =
      typeof AXIAL_POSES !== 'undefined' &&
      AXIAL_POSES.has(pose) &&
      (pose !== 'swim' || swimAxialAllows(drawnFacing));
    // ...and having an axial drawing is not enough on its own: a cat that
    // was just turned side-on for wearing a pose without one stays side-on
    // until it steps again, or it whips ninety degrees every time it
    // stops drinking. See `axialFor` in anim.js.
    const axialOk = view.axialFor ? view.axialFor(kitty.id, axialPose) : axialPose;
    const axial = axialOk && (drawnFacing === 'north' || drawnFacing === 'south');
    const catView = axial ? (drawnFacing === 'north' ? 'back' : 'front') : 'side';
    const paintFacing = axial
      ? drawnFacing
      : drawnFacing === 'north' || drawnFacing === 'south'
        ? view.sideFacingFor
          ? view.sideFacingFor(kitty.id)
          : 'right'
        : drawnFacing;
    const vel = v2Motion && view.velocityFor ? view.velocityFor(kitty.id) : { x: 0, y: 0 };
    const gaze = (v2Motion && gazeTargetFor(kitty, world, pos, view)) || motion.gaze || null;
    const rig =
      v2Motion && view.rigFor
        ? view.rigFor(kitty.id, {
            vx: vel.x,
            vy: vel.y,
            facing: drawnFacing,
            gazeX: gaze ? gaze.x : 0,
            gazeY: gaze ? gaze.y : 0,
            earTwitch: motion.earTwitch || 0,
            earTwitchSide: motion.earTwitchSide || 1,
            earsBack: earsHold ? 1 : 0,
            yawn: motion.yawn || 0,
            breath: motion.phase || 0,
          })
        : null;
    // Which way this cat is actually travelling, for the walk's
    // foreshortening. See cat-v2's walking case: a vertical walk drawn
    // with a horizontal stride is 100% skate, by construction.
    const layout = {
      travelH: view.travelHFor ? view.travelHFor(kitty.id) : 1,
      // How long one beat lasts, for motion authored as a real frequency.
      beatMs: view.tickMs,
      // Which drawing to use. Resolved above, from the pose AND the facing:
      // the facing is not settled until the turn has had its say, so this
      // cannot be computed where the other layout fields are chosen.
      view: catView,
    };

    // How damp the COAT is -- and nothing else. This is the one water cue
    // allowed to outlive the pond, so it may only ever change colour;
    // every piece of geometry below reads `submersion` instead. Hanging
    // anything positional off this is precisely how water ended up being
    // drawn on grass.
    const furWet = v2Motion && view.wetFor ? view.wetFor(kitty.id, onWater) : 0;

    // A soft shadow so cats sit on the grass rather than float above it --
    // and, since v3, one that knows where the sun is. It leans and
    // stretches with the phase (MEADOW.shadowLean / shadowLength), which
    // is the cue that most says "the hour is moving": short and almost
    // straight down at noon, long and thrown to one side at sunset, long
    // to the OTHER side at dawn, and directionless under the moon.
    // Because both are plain numbers, they interpolate across a phase
    // crossing for free -- the shadow swings round as the light does.
    const shadowAlpha = 1 - submersion;
    if (shadowAlpha > 0) {
      const lean = MEADOW.shadowLean ?? 0;
      const length = MEADOW.shadowLength ?? 1;
      // A shadow starts at the thing casting it and runs away from the
      // light -- it does not spread out both ways. So the extra length is
      // thrown entirely to one side: the sun-side edge stays where the
      // caster's own footprint is, and only the far edge travels.
      //
      // Multiplying the throw by `lean` rather than by its sign keeps this
      // smooth: at lean 0 (noon, and the moon) the stretch stays
      // symmetrical, which is right for a light directly overhead, and
      // nothing jumps as the lean crosses zero between phases.
      const footprint = this.tile * 0.3;
      const halfWidth = footprint * length;
      const offset = lean * (halfWidth - footprint);
      ctx.save();
      // Alpha falls as the shadow stretches: the same darkness spread
      // over more ground would read as a stain rather than a shadow.
      ctx.globalAlpha = shadowAlpha / Math.max(1, length * 0.8);
      ctx.fillStyle = MEADOW.groundShadow;
      ctx.beginPath();
      ctx.ellipse(
        cx + offset,
        cy + this.tile * 0.32,
        halfWidth,
        this.tile * 0.12,
        0,
        0,
        Math.PI * 2,
      );
      ctx.fill();
      ctx.restore();
    }
    if (submersion > 0.01 && VIEW.ambient.wetRipple) {
      // ...and the water it displaces instead. Ships OFF (VIEW.ambient):
      // the pond restyle owns the water's surface now, and the cat's rings
      // fought the water's own. Kept behind the flag beside its sibling
      // water effect rather than deleted, so the lab can put it back.
      ctx.save();
      ctx.globalAlpha = submersion * 0.55;
      ctx.strokeStyle = MEADOW.pondRim;
      ctx.lineWidth = Math.max(1, this.tile * 0.045);
      for (const [rx, ry, dy] of [[0.34, 0.13, 0.3], [0.22, 0.085, 0.36]]) {
        ctx.beginPath();
        ctx.ellipse(cx, cy + this.tile * dy, this.tile * rx, this.tile * ry, 0, 0, Math.PI * 2);
        ctx.stroke();
      }
      ctx.restore();
    }
    // Water occlusion (BACKLOG P1, the owner's idea): clip the cat against
    // the waterline so a cat standing in a pond is visibly in it, whatever
    // pose it is wearing. This is what makes the water+activity case work
    // without a second pose per activity -- a cat drinking at the edge of a
    // pond keeps its drinking pose and still reads as standing in water.
    // One level for every pose, so there is nothing to interpolate across
    // a pose change: a cat starting to paddle meets the water exactly
    // where it did while standing in it.
    const cut = waterlineFor(submersion, surfaceForPose(pose));
    const submerged = cut !== null;
    if (submerged) {
      ctx.save();
      ctx.beginPath();
      // Generous horizontally and upward: the tail and the dispatcher's
      // 1.05x overdraw both put ink outside the nominal box, and clipping
      // is only ever meant to cut the BOTTOM off.
      ctx.rect(x - this.tile, y - this.tile * 2, this.tile * 3, this.tile * (2 + cut));
      ctx.clip();
    }
    if (tween?.sy !== undefined) {
      // The landing settle: a soft squash about the ground line, so the
      // feet stay planted (the dispatcher's overdraw anchors feet too).
      // Volume-preserving since 2026-08-10: a squash that only loses
      // height reads as the cat shrinking rather than as weight arriving.
      // Compressed about the ground line so the paws stay planted, and
      // widened about the cat's own middle so the mass has somewhere to go.
      const groundY = y + 0.88 * this.tile;
      const midX = x + this.tile / 2;
      ctx.save();
      ctx.translate(midX, groundY);
      ctx.scale(1 + (1 - tween.sy) * 0.7, tween.sy);
      ctx.translate(-midX, -groundY);
    }
    const catOpts = {
      // The damp coat ships OFF (VIEW.ambient.wetCoat). Guarded on the
      // symbol as well as the flag: it is a v2 vocabulary feature and the
      // dispatcher can be running v1, whose cat file has no such function.
      appearance:
        VIEW.ambient.wetCoat && typeof wetAppearanceOf === 'function'
          ? wetAppearanceOf(shadedAppearanceOf(appearanceFor(kitty.id), this.theme), furWet)
          : shadedAppearanceOf(appearanceFor(kitty.id), this.theme),
      facing: paintFacing,
      size: this.tile,
      eyesOverride: eyes,
      // On the v2 path the rig owns the ears, so the hard boolean (which
      // sets them fully back in one frame) is left to v1.
      earsBack: v2Motion ? undefined : ears,
      lid,
      rig,
      turn,
      layout,
      x,
      y,
    };
    if (tween?.blend) {
      drawCatTween(ctx, {
        ...catOpts,
        from: tween.blend.from,
        to: pose,
        t: tween.blend.t,
        phaseFrom: tween.blend.fromPhase,
        phaseTo: motion.phase,
        // The outgoing pose was travelling the same way the incoming one
        // is: a walk blending out has to keep its foreshortening or the
        // stride pops back to full width on the way to standing.
        layoutFrom: layout,
      });
    } else {
      drawCat(ctx, { ...catOpts, pose, phase: motion.phase });
    }
    if (tween?.sy !== undefined) ctx.restore();
    if (submerged) ctx.restore();
    // Drawn after the clip is released, so the surface sits ON the cat
    // rather than being cut away with its legs.
    if (submerged) {
      // Centred on her BODY, not her box. She is not symmetric about her
      // own box -- the body sits behind the head at BODY_CX and mirrors
      // with the facing -- so a box-centred waterline lands about 6% of a
      // tile toward the head. At a camera tile that is 6px, which the
      // owner saw as "a few pixels too far to the right" on a
      // right-facing cat. `drawCat` mirrors on 'left' alone, and this
      // follows it rather than restating the rule.
      const bodyCx = drawnFacing === 'left' ? 1 - BODY_CX : BODY_CX;
      this.drawWaterline(x + this.tile * bodyCx, y, cut, submersion, view);
    }
    // The beat, the Zs and the cuddle heart all live ABOVE the water and
    // are drawn after the clip is released -- a thought bubble does not
    // get cut off because the cat it belongs to is standing in a pond.
    if (beat) this.drawBeat(beat, cx, cy, paintFacing);

    if (state === 'sleeping') {
      // Drawn Zs drift up from the sleeper (spec 007 FR-008), replacing
      // the emoji wisp at the same corner.
      ctx.save();
      ctx.globalAlpha = 0.75;
      drawSleepZs(ctx, {
        phase: view.propPhaseFor(kitty.id, VIEW.props.zDriftMs),
        size: this.tile * 0.8,
        x: x + this.tile * 0.35,
        y: y - this.tile * 0.5,
      });
      ctx.restore();
    }

    // Cuddling cats get a little heart between them -- at their eased
    // positions, so it floats where the cats visibly are; it beats on the
    // drawn kitty's own clock (spec 007 FR-008).
    const partner = kitty.activity?.with_friend;
    if (partner !== undefined && partner !== null) {
      const friend = world.kitties.find((k) => k.id === partner);
      if (friend) {
        const fpos = view.posFor(friend);
        const fx = (fpos.x + 0.5) * this.tile;
        const fy = (fpos.y + 0.5) * this.tile;
        const heartSize = this.tile * 0.5;
        drawHeart(ctx, {
          phase: view.propPhaseFor(kitty.id, VIEW.props.heartPulseMs),
          size: heartSize,
          x: (cx + fx) / 2 - heartSize / 2,
          y: (cy + fy) / 2 - this.tile * 0.15 - heartSize / 2,
        });
      }
    }

    if (this.showHappiness) this.drawHappinessBar(kitty, x, y, view);
  }

  /**
   * One-shot beats (US5): short presentational sequences beside the cat.
   * The plaything is deliberately unlike every real element (FR-009) --
   * a twinkling star, where the world's things are emoji and tiles.
   */
  drawBeat(beat, cx, cy, facing) {
    const ctx = this.ctx;
    const dir = facing === 'right' ? 1 : -1;
    if (beat.kind === 'sparkle') {
      // Relief: little golden twinkles rising beside the kitty (FR-011).
      ctx.save();
      ctx.globalAlpha = 1 - beat.t;
      const rise = beat.t * this.tile * 0.5;
      this.star(cx + dir * this.tile * 0.35, cy - this.tile * 0.35 - rise, this.tile * 0.1, '#f4c95d');
      this.star(cx - dir * this.tile * 0.18, cy - this.tile * 0.55 - rise * 0.7, this.tile * 0.065, '#f8dc9a');
      ctx.restore();
    } else if (beat.kind === 'plaything') {
      // Solo play: the imaginary quarry hops with the pounce and twinkles
      // out of existence when the game ends.
      ctx.save();
      const hop = Math.sin(beat.t * Math.PI) * this.tile * 0.35;
      const px = cx + dir * this.tile * 0.55;
      const py = cy - this.tile * 0.08 - hop;
      ctx.globalAlpha = 0.9;
      const twinkle = 0.8 + 0.2 * Math.sin(beat.t * 6 * Math.PI);
      this.star(px, py, this.tile * 0.13 * twinkle, '#ffd97a');
      ctx.globalAlpha = 0.5;
      this.star(px + dir * this.tile * 0.14, py + this.tile * 0.12, this.tile * 0.06, '#ffe9b5');
      ctx.restore();
    }
    // 'sad' draws nothing extra: the droop is worn on the cat itself.
  }

  /** A little four-point star -- the beat vocabulary's one glyph. */
  star(cx, cy, r, color) {
    const ctx = this.ctx;
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.moveTo(cx, cy - r);
    ctx.quadraticCurveTo(cx, cy, cx + r, cy);
    ctx.quadraticCurveTo(cx, cy, cx, cy + r);
    ctx.quadraticCurveTo(cx, cy, cx - r, cy);
    ctx.quadraticCurveTo(cx, cy, cx, cy - r);
    ctx.closePath();
    ctx.fill();
  }

  /**
   * The in-world twin of the panel's gentle cue (US5, FR-012): one soft
   * thought bubble with the long-wanted need's icon, above the kitty and
   * clear of its speech bubble.
   */
  drawThought(kitty, need, view) {
    const ctx = this.ctx;
    const { x, y } = this.tileOrigin(view.posFor(kitty));
    const r = this.tile * 0.34;
    const vp = this.viewportRect();
    let bx = x + this.tile * 1.05;
    bx = Math.min(bx, vp.right - r - 2);
    bx = Math.max(vp.left + r + 2, bx);
    const by = Math.max(vp.top + r + 2, y - this.tile * 0.55);

    ctx.save();
    ctx.fillStyle = 'rgba(255, 253, 250, 0.92)';
    ctx.strokeStyle = 'rgba(150, 125, 105, 0.28)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.arc(bx, by, r, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
    // The trail of little thought-dots down toward the kitty's head.
    const headX = x + this.tile * 0.6;
    const headY = y + this.tile * 0.2;
    for (const [k, dr] of [[0.55, 0.12], [0.8, 0.07]]) {
      ctx.beginPath();
      ctx.arc(bx + (headX - bx) * k, by + (headY - by) * k, this.tile * dr, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
    }
    // The wanted need as its drawn mini-prop (spec 007 FR-009) -- the same
    // vocabulary the world uses, at bubble scale.
    const iconSize = r * 1.5;
    drawNeedIcon(ctx, { need, size: iconSize, x: bx - iconSize / 2, y: by - iconSize / 2 });
    ctx.restore();
  }

  drawHappinessBar(kitty, x, y, view) {
    const ctx = this.ctx;
    const width = this.tile - 6;
    const height = 3;
    const bx = x + 3;
    const by = y + this.tile - 3.5;
    // Eased toward the served value on the shared progress clock (US6) --
    // the color reads the true value, never the blend.
    const value = view.barValueFor(kitty);

    ctx.fillStyle = 'rgba(255, 255, 255, 0.75)';
    ctx.fillRect(bx, by, width, height);
    ctx.fillStyle = happinessColor(kitty.happiness);
    ctx.fillRect(bx, by, width * clamp01(value / 100), height);
  }

  drawBubbles(world, view) {
    const recent = (world.recent_meows || []).filter(
      (m) => m.tick > world.tick - BUBBLE_TICKS,
    );
    // A purr never gets a speech bubble (2026-08-14). Nine of the ten meow
    // kinds are things a viewer can act on; a purr is a mood, and the same
    // bubble for both meant 98% of bubbles said nothing -- see PURR in
    // props.js. One bubble per cat, newest wins.
    const said = new Map();
    for (const meow of recent) {
      if (meow.kind === 'purr') continue;
      said.set(meow.kitty_id, meow);
    }
    for (const meow of said.values()) {
      const kitty = world.kitties.find((k) => k.id === meow.kitty_id);
      if (!kitty) continue;
      this.drawBubble(kitty, MEOW_TEXT[meow.kind] || '…', view, meow);
    }

    if (!PURR.on) return;
    // The mood is drawn from `purring_until`, NOT from the meow. A purr is
    // background state that runs 9-13 ticks; the meow is only its
    // announcement, one tick long, and keying the heart to that showed a
    // flash where a cat was rumbling for the better part of ten seconds.
    // The engine calls this field "the viewer's rumbling now signal" in so
    // many words. Reading it also retires a dwell constant and the
    // off-by-one that came with it -- there is no duration to get wrong.
    for (const kitty of world.kitties) {
      if (!(kitty.purring_until >= world.tick)) continue;
      // A request outranks the mood: they want the same space above the
      // cat, and the thing the viewer can act on is the one to keep.
      if (said.has(kitty.id)) continue;
      const { x, y } = this.tileOrigin(view.posFor(kitty));
      drawPurrGlyph(
        this.ctx,
        x + this.tile / 2,
        y,
        this.tile,
        view.propPhaseFor(kitty.id, 1000 / PURR.shakeHz),
      );
    }
  }

  drawBubble(kitty, text, view, meow) {
    const ctx = this.ctx;
    const { x, y } = this.tileOrigin(view.posFor(kitty));
    ctx.font = '600 11px ui-rounded, system-ui, sans-serif';
    const padding = 6;
    const width = ctx.measureText(text).width + padding * 2;
    const height = 18;

    // Keep the bubble on screen even for cats hugging the edges.
    let bx = x + this.tile / 2 - width / 2;
    const vp = this.viewportRect();
    bx = Math.max(vp.left + 2, Math.min(bx, vp.right - width - 2));
    const by = Math.max(2, y - height - 4);

    // A fresh meow pops in with a small settle (US6); older bubbles and
    // reduced motion render at full size instantly.
    const scale = view.bubbleScaleFor(meow);
    ctx.save();
    if (scale !== 1) {
      const ax = x + this.tile / 2;
      const ay = by + height;
      ctx.translate(ax, ay);
      ctx.scale(scale, scale);
      ctx.translate(-ax, -ay);
    }

    ctx.fillStyle = 'rgba(255, 253, 250, 0.96)';
    ctx.strokeStyle = 'rgba(150, 125, 105, 0.28)';
    ctx.lineWidth = 1;
    this.roundRect(bx, by, width, height, 9);
    ctx.fill();
    ctx.stroke();

    // Tail.
    ctx.beginPath();
    ctx.moveTo(x + this.tile / 2 - 3, by + height - 1);
    ctx.lineTo(x + this.tile / 2, by + height + 4);
    ctx.lineTo(x + this.tile / 2 + 3, by + height - 1);
    ctx.closePath();
    ctx.fillStyle = 'rgba(255, 253, 250, 0.96)';
    ctx.fill();

    ctx.fillStyle = '#6b5a4e';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, bx + padding, by + height / 2);
    ctx.restore();
  }

  // ---- small helpers ----

  tileOrigin(pos) {
    return { x: pos.x * this.tile, y: pos.y * this.tile };
  }

  // (The emoji() helper is gone -- spec 007 FR-010: with every world glyph
  // drawn parametrically, deleting it makes "zero emoji on the canvas"
  // structural rather than aspirational.)

  roundRect(x, y, w, h, r) {
    const ctx = this.ctx;
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
  }
}

function happinessColor(happiness) {
  if (happiness >= 70) return '#8fce8f';
  if (happiness >= 40) return '#f3cf7a';
  return '#efa98b';
}

function clamp01(value) {
  return Math.max(0, Math.min(1, value));
}
