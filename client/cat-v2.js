/**
 * CloudKitty's cats, v2 vocabulary -- PROTOTYPE, not yet the shipped look.
 *
 * A fork of cat.js (which remains the live vocabulary) for the 2026-07
 * graphics investigation. Same art style, same palettes, same poses; what
 * changes is the face and the proportions:
 *
 *  - Kawaii proportions: every pose's head is ~1.05x its v1 radius. The
 *    body, patterns, tail and palette are untouched, so the cats stay
 *    recognizably themselves.
 *  - Cuter eyes: larger, repositionable (CatV2.EYE dials), and always
 *    fully drawn -- iris color, dark pupil -- at every size. v1 gated eye
 *    detail behind `fine` (>= 44px), which no live-world cat ever
 *    reached. The white glint was tried and cut (owner, 2026-07-29). The
 *    narrowed 'focused' hunting eyes are kept exactly as v1 drew them.
 *  - Face under live revision (owner, 2026-07-29): symmetric front-on
 *    nose near the eye midline; mouth is an upside-down V under the nose
 *    (the profile ω was tried and cut). No whiskers -- tried and cut.
 *
 * Everything lives in an IIFE so this file can share a page with cat.js:
 * the comparison gallery and index.html's v1/v2 toggle both load the two
 * side by side. When loaded WITHOUT cat.js, it claims the same global
 * names and works as a drop-in replacement.
 *
 * Pure drawing, as v1: no DOM beyond ctx, no fetches. Unit box 0..1,
 * y down; the base cat faces right and mirrors for left.
 */

(() => {

/**
 * Curated colorways (research R2): appearance is PALETTES[id % length], so a
 * kitty's look is stable across frames, sessions and restarts. Indices 1-3
 * are the shipped defaults -- Miso the seal-point, Biscuit the warm solid,
 * Pumpkin the orange tabby -- tuned to be told apart at 22px.
 *
 * THE ORDER IS THE ROSTER. Because the index is the kitty id, moving an entry
 * re-coats a cat, and 'cloud' and 'midnight' were swapped for exactly that
 * reason (spec 033): the fifth cat is id 5, and she is the white one. Nothing
 * indexes this array by hand -- appearanceFor is the one door, and app.js
 * looks its portrait palette up by name -- so the swap was the whole change.
 * A test pins every roster id to the colorway it is meant to wear.
 */
const PALETTES = [
  {
    name: 'tuxedo',
    furBase: '#4a4550',
    furShade: '#2f2b36',
    pattern: { kind: 'tuxedo-mask', color: '#fbf7f0' },
    eyeColor: '#8fce8f',
    noseColor: '#e8a1a1',
  },
  {
    name: 'seal point', // Miso
    furBase: '#f3e4c8',
    furShade: '#c2a37d',
    // v2 (owner, 2026-07-29): point lightened ~10% from v1's #8a6547 and
    // nose darkened ~25% overall from v1's #b98a76 -- the pale nose
    // floated silly against the dark mask; now the contrast runs the
    // right way (nose darker than mask, mouth darker still).
    pattern: { kind: 'point-mask', color: '#986f4e' },
    eyeColor: '#7ab8d9',
    noseColor: '#866455',
  },
  {
    name: 'biscuit tabby', // Biscuit
    furBase: '#e3bd8b',
    furShade: '#b9905f',
    pattern: { kind: 'tabby-stripes', color: '#c89a63' },
    // Green, owner's call 2026-08-10 (was amber #8a5f2b). Gooseberry rather
    // than the roster's other two greens: 33 degrees of hue off pumpkin's
    // leaf and 47 off the tuxedo's mint, so three green-eyed cats still
    // read as three cats. Warm enough to sit with the biscuit fur.
    eyeColor: '#a8c24e',
    noseColor: '#c98d7b',
  },
  {
    name: 'pumpkin tabby', // Pumpkin
    furBase: '#f09d52',
    furShade: '#c0722f',
    pattern: { kind: 'tabby-stripes', color: '#cd7430' },
    eyeColor: '#6fae5c',
    noseColor: '#d98a77',
  },
  {
    name: 'storm',
    furBase: '#a9b2bf',
    furShade: '#7d8795',
    pattern: { kind: 'solid' },
    eyeColor: '#c9a227',
    noseColor: '#b58a94',
  },
  {
    name: 'cloud', // Clementine
    furBase: '#f7f3ec',
    furShade: '#c6b9a6',
    pattern: { kind: 'solid' },
    eyeColor: '#84b6d8',
    noseColor: '#e8a1a1',
  },
  {
    name: 'midnight',
    furBase: '#4d4752',
    furShade: '#332e3b',
    pattern: { kind: 'solid' },
    eyeColor: '#e3b341',
    noseColor: '#8f7482',
  },
  {
    name: 'calico',
    furBase: '#faf4ea',
    furShade: '#c9baa4',
    pattern: { kind: 'patches', color: '#e2924e', color2: '#9b93a6' },
    eyeColor: '#b0793a',
    noseColor: '#e0958a',
  },
];

/**
 * The pose vocabulary -- the spec's clarified eight (idle is a standing
 * cat; sitting is deliberately skipped for now), plus v2's swim (the
 * parked 010 wading pose, built 2026-08-02; v1 never wears it).
 */
const POSES = [
  'idle',
  'walking',
  'pouncing',
  'eating',
  'drinking',
  'grooming',
  'loaf',
  'sleep-curl',
  'swim',
  // Added 2026-08-10. `sit` is the pose the vocabulary was missing: it is
  // what a cat does when it has decided to STAY somewhere, and without it
  // an untasked cat only ever had "standing" to say that with. `stretch`
  // is the waking one. Both are reachable from state the engine already
  // serves -- see anim.js's idlePoseFor and wokeAt.
  'sit',
  'stretch',
];

/**
 * Swim-pose tunables, mutable for the gallery lab's dials exactly like
 * EYE/NOSE/MOUTH: the owner dials, the paste gets baked here. Unit space
 * (0..1 box, ground near y 0.88); the pond draws underneath the cat, so
 * "underwater" is a reading the low flat silhouette earns, not clipping.
 */
/**
 * The axial views -- a cat seen head-on or from behind (2026-08-10).
 *
 * The vocabulary has been one drawing since it began: a side view, mirrored
 * for left. That is why a cat walking north had to be faked with
 * foreshortening, and why the turn-around was cut twice -- a flat side view
 * has no depth to rotate into, so squashing it reads as a card turning
 * edge-on rather than an animal turning away.
 *
 * These are real drawings instead, and they need no new machinery: the
 * layout schema (body ellipse, head circle, legs, tail bezier) already
 * describes a front-on cat perfectly well. What changes is only WHERE the
 * parts sit, so blends, the rig, the water clip and the pose tween all
 * keep working untouched.
 *
 * The engine moves cats in four directions only (owner, 2026-08-10), so
 * there are exactly four facings and never a diagonal to resolve.
 *
 * Unit space, ground at 0.88, box centred on 0.5 -- unlike the side view,
 * which is built around a nose at high x.
 */
const AXIAL = {
  bodyY: 0.7, // body centre
  bodyRx: 0.205, // narrower than the side view's 0.3: this is the chest, not the flank
  bodyRy: 0.185,
  // The head is at the FAR end of a cat walking away and the NEAR end of
  // one walking toward you, so it cannot be one size. Drawing it the same
  // either way is what made the back view read as a cat facing you with
  // its face rubbed out -- the depth cue was missing, so the only thing
  // left to go on was the tail, and the tail then looked like it grew from
  // the head end.
  // Which treatment is live. `elevation` owner-picked 2026-08-10 from the
  // three rendered side by side, at 120px and at the live tile.
  //
  // The argument that won: the axial views have to match the SIDE view's
  // camera, not the ground's. A cat turning from east to north must look
  // like the same animal one tick later, and the side view -- the one seen
  // most -- cannot tilt with them, so any tilt makes every turn a camera
  // move as well as a rotation. The ground being drawn in plan while the
  // cats are drawn in elevation is the convention every top-down game
  // uses, and nobody reads it as a mistake.
  //
  // `tilt` and `topdown` stay on the shelf: one line switches, and the
  // Camera Lab compares all three.
  camera: 'elevation',
  headYFront: 0.4,
  headRFront: 0.232, // nearest the camera: a touch larger than the side view
  // Lowered 0.355 -> 0.425 (owner: "sits too high up the body"). Measured,
  // the body was hiding only 13% of the back-view head against 28% of the
  // front-view one -- so the head furthest from the camera was the one
  // floating clear of the shoulders, which is backwards. A cat's head sits
  // INTO its shoulders, and more so as it turns away from you; a head
  // clear of the body reads as a balloon on a string.
  headYBack: 0.425,
  headRBack: 0.196, // further away, and the body takes its chin
  // Legs. The near pair is the one you see: forelegs from the front, hind
  // legs from behind. The far pair sits wider and draws behind the body.
  legNear: 0.098, // offset from centre
  legFar: 0.152,
  legTop: 0.7,
  legW: 0.095,
  // The walk, which in this view is almost all vertical: a cat coming at
  // you covers no sideways ground, so the stride is invisible and what is
  // left is the lift, the bob and the sway. (The side view's `depth*`
  // dials were the fake of exactly this; they stay for graceful
  // degradation but the live path no longer needs them.)
  // Dialled right down 2026-08-10: the first cut read as "a horse at a
  // canter" (owner), and both causes were mine. The legs were on a
  // DIAGONAL sequence -- the footfall pattern of a trot -- and the body
  // rocked hard enough to bound. A walking cat is famously level: it
  // places one foot at a time in a lateral sequence and its shoulders
  // barely move. So the rock is now a fifth of what it was and the
  // sequence is the right one; see the leg phases below.
  lift: 0.042, // how far a foot picks up
  bob: 0.007, // body rise and fall
  sway: 0.006, // and its side-to-side shift
  roll: 0.018, // body lean, radians
  headFollow: 0.25, // share of the bob the head takes -- a cat holds it level
  headSway: 0.55, // and of the sway
  // The tail. From behind it stops being a side detail and becomes most of
  // the silhouette, which is why it goes straight up (owner's call): at
  // 31px it is the one part of a walking-away cat that reads.
  // The raised tail rises BESIDE the cat, not over it.
  //
  // Two wrong answers first, both instructive. Drawn behind and vertical
  // out of the rump, it was hidden completely -- the body and head between
  // them cover the whole centre of this view. Drawn in front to fix that,
  // it became a thick diagonal bar laid across the body, which reads as a
  // stick rather than a tail.
  //
  // The answer is neither: put it out past the silhouette's edge (the body
  // is 0.205 wide, the head 0.222) and it needs no compositing trick at
  // all. It stays behind the cat like every other tail, its base is hidden
  // by the rump exactly as it should be, and the raised length is in clear
  // air. Which is also how the sprite reads in every game that has ever
  // drawn a cat walking away.
  tailTopY: 0.33,
  tailBaseY: 0.8,
  tailBaseX: 0.55, // at the rump, still inside the body silhouette
  tailOutX: 0.79, // ...and out past its edge, where the raised length shows
  tailSway: 0.025, // tip drift across the walk
  tailCurve: 0.06, // how far it bows on the way out and up
  // From the front the tail is behind the cat, so only a hint of it clears
  // the body's edge.
  tailPeekX: 0.26, // just past the body's 0.205 edge -- a hint, not a shape
  tailPeekY: 0.66,
};

/**
 * Three camera treatments for the axial views (2026-08-10).
 *
 * The axial views are the first drawings in this world where the camera
 * ANGLE is visible. A side view never shows the depth axis, so any camera
 * height projects to the same silhouette; head-on and from behind, the
 * depth axis points into the screen and how much of the cat's LENGTH you
 * see IS the angle.
 *
 * Only the body and head change: the further above the horizon the camera
 * sits, the more spine you see running away up-screen, the smaller the far
 * end of the cat gets, and the more of the legs the body hides. Nothing
 * here is new machinery -- it is the same layout with different numbers.
 */
const AXIAL_CAMERAS = {
  // A cat seen from its own eye level. Matches the SIDE view's camera,
  // which is the argument for it: a cat turning from east to north has to
  // look like the same animal, and the side view is the one seen most.
  elevation: {
    bodyY: 0.7, bodyRx: 0.205, bodyRy: 0.185,
    headYFront: 0.4, headRFront: 0.232,
    headYBack: 0.425, headRBack: 0.196,
  },
  // Looking down a little -- roughly what the elliptical ground shadows
  // already imply. Some spine, a slightly smaller far end.
  tilt: {
    bodyY: 0.685, bodyRx: 0.195, bodyRy: 0.205,
    headYFront: 0.375, headRFront: 0.222,
    headYBack: 0.44, headRBack: 0.176,
  },
  // Clearly above: the cat reads as a length running away from you, and
  // the legs mostly disappear under the body, which is what foreshortening
  // does to them.
  topdown: {
    bodyY: 0.66, bodyRx: 0.185, bodyRy: 0.225,
    headYFront: 0.335, headRFront: 0.208,
    headYBack: 0.46, headRBack: 0.152,
  },
};

const AXIAL_POSES = new Set(['walking', 'idle', 'swim']);

/**
 * A swimming cat seen end-on (2026-08-11).
 *
 * The world moves cats through water on every axis equally -- measured at
 * 20 north/south wet steps against 21 east/west -- but `swim` had no axial
 * drawing, so one was always drawn side-on however it was actually going.
 *
 * What makes this pose different from the other two axial ones is that the
 * waterline does most of the drawing. At full submersion the clip sits at
 * 0.72, so only about 6px of a 31px cat's body clears the surface and the
 * rest of what reads as "cat" is the head. That is the whole design
 * problem: it is a portrait, not a body.
 *
 * Which is why the two directions are not equally worth having, and the
 * lab draws them side by side rather than this file deciding. Coming
 * TOWARD you the head is the largest in the vocabulary (`headRFront`
 * 0.232, deliberately, as a depth cue) and carries a full face right at
 * the waterline. Going AWAY, `paintCat` draws no face at all by design,
 * so it is a featureless circle and two ears. `VIEW.swimAxial` picks which
 * of them ships; nothing here assumes the answer.
 */
const AXIAL_SWIM = {
  bodyDrop: 0.012, // below the axial body, the way SWIM sits below idle
  bodyRy: 0.15, // flattened: a floating back, not a standing barrel
  bodyRx: 0.2, // a shade narrower than standing -- the flanks are under
  headDrop: 0.055, // chin toward the surface, the swimming read
  bob: 0.012, // matches the side pose's paddle bob
  rock: 0.03, // less than the side view's: an end-on roll shows more
  // The tail, held UP out of the water (owner, 2026-08-11).
  //
  // This is the posture the water we actually built calls for. The
  // waterline cuts a cat at 0.72 of its box -- its flank, not its neck --
  // so these are cats wading and paddling in the shallows, and a wading
  // cat carries its tail clear of the surface. It also happens to be the
  // one thing that can rescue the away view: everything else above water
  // there is a circle and two ears, and a raised tail is the only piece of
  // silhouette left that says CAT rather than otter.
  tailBaseDrop: 0.06, // where it leaves the body, under the surface
  tailTopY: 0.42, // ...and where the tip rides, well clear of it
  tailOutX: 0.52, // owner 2026-08-11: near vertical -- see the note below
  tailPeekX: 0.8, // owner: pushed wide, so the tail is beside the cat, not behind it
  tailCurve: 0.05, // how far it bows on the way out and up
};

const SWIM = {
  // Raised 2026-08-10, when the swim pose started being CLIPPED at the
  // waterline like every other pose.
  //
  // These used to encode depth themselves: the pose sat low in its box and
  // earned "underwater" from its own silhouette, because it was exempt
  // from the clip. Once the world owns one water level, a pose that also
  // sinks itself is submerged twice -- and a swimming cat sat visibly
  // deeper than a wading one in the same pond.
  //
  // So the body now sits at very nearly the land poses' height (idle is
  // 0.64) and the CLIP does the submerging. What still distinguishes a
  // swimming cat from a standing one is posture, which is where the
  // difference belonged all along: a flatter body, a lower chin, no legs.
  bodyY: 0.68, // body center: just under a standing cat's, not far under
  bodyRy: 0.155, // flattened floating body (idle is 0.21)
  headY: 0.47, // chin near the surface -- the swimming read, without sinking
  bob: 0.012, // vertical bob amplitude (paddle rhythm)
  rock: 0.045, // paddling body rock, radians
  tailLift: 0.6, // where the tail tip rides above the surface
  tailUpright: 1, // owner 2026-08-11: HELD UP. 0 is the trailing tail v2.7 shipped.
  // How much TALLER the raised side tail stands than the end-on ones.
  //
  // Not a fudge: it is foreshortening. A tail held up and pointing partly
  // toward or away from the camera is seen at an angle and draws short;
  // the same tail seen broadside shows its whole length. Drawing all three
  // at the identical height therefore makes the side view -- the one with
  // nothing to hide behind -- look stubby, which is what the owner saw.
  //
  // So the shared height (AXIAL_SWIM.tailTopY) stays the anchor for all
  // three, and this is the one declared, dialable difference on top of it.
  // At 0 the three match exactly again.
  tailUprightRise: 0.05, // owner: even across all three, allowing for perspective
};

/**
 * Sleep-curl tunables, mutable for the lab like SWIM.
 *
 * Factored out 2026-08-09 because the head was the one measured outlier in
 * the whole vocabulary: every other pose sits in a tight 0.215-0.226 band
 * (idle and swim 0.226, loaf 0.221, pounce 0.215) and sleep alone was
 * 0.173 -- 23% under the base. A cat's skull does not shrink when it curls
 * up, so the sleeping cat read as a different, smaller animal.
 *
 * `headR` is interpolated by blendLayouts like every other head radius, so
 * moving it blends rather than pops on the way in and out of sleep.
 * Position comes with it: a bigger head in a curl sits differently against
 * the body, so growing it alone is not the whole change.
 */
const SLEEP = {
  // Owner-dialled 2026-08-09 against the awake cat drawn beside it, which is
  // the only way to judge it: 0.173 -> 0.211 is 93% of the base head where it
  // was 77%, so the sleeper is the same cat now, just a touch foreshortened
  // by the curl. The head rose 0.1 and came forward 0.075 to sit on the ball
  // rather than inside it.
  headR: 0.211, // base head is 0.226; the rest of the vocabulary is 0.215-0.226
  headX: 0.695, // where the head sits along the curled body
  headY: 0.58, // and how far down it tucks
};

/**
 * The breath, mutable for the lab like SWIM and GAIT.
 *
 * A sine is symmetric and a chest is not. The top of an inhale is the
 * moment a body is most resisted; the bottom of an exhale is the moment
 * it is least, and a real ribcage sinks a little further than it swells.
 *
 * `skew` buys exactly that trade and nothing else: subtracting k*b^2 from
 * the wave flattens the inhale peak by k and deepens the exhale by the
 * same k, so the TOTAL travel is untouched -- 0.92 to -1.08 is still a
 * span of 2. The roundness at the top is spent on squash at the bottom
 * rather than given up, which is what was asked for (owner, 2026-08-10:
 * slightly too round at peak, same amount of motion). It is a polynomial,
 * so there is no kink at the zero crossings the way a two-sided gain has.
 *
 * The small side effect is deliberate: the mean of b^2 over a cycle is
 * one half, so the cat also sits a hair slimmer on average. That is the
 * same note being answered.
 */
const BREATH = { skew: 0.08 };

/** The shaped breath. Feeds every resting pose, so idle, loaf, sit and
 * the sleeper all breathe with one character rather than three. */
function breathCurve(b, k = BREATH.skew) {
  return b - k * b * b;
}

/**
 * Walk-cycle tunables, mutable for the lab like SWIM.
 *
 * The walk this replaces slid both feet along a shared sine at a fixed
 * y. That has no stance: for half of every step each planted foot moved
 * FORWARD while the cat was already moving forward, so the feet outran
 * the cat and the whole thing read as skating. Invisible at a 30px tile;
 * at 60 it is the first thing you see.
 *
 * A foot on the ground has exactly one honest job -- to hold still
 * against the world, which in body space means travelling backward at
 * the speed the ground passes under it. So the cycle is split: `duty` of
 * it planted and drifting back, the rest lifted and swinging forward.
 * The lift is what buys the illusion, because a foot in the air is
 * ALLOWED to move.
 */
const GAIT = {
  // Steps per tile. MUST be a whole number: `phase` is tick progress and
  // returns to 0 every tile, so a fractional count tears the cycle once
  // per tile crossed. It is also the setting that makes planting possible
  // at all -- see PLANTED below.
  cycles: 2,
  duty: 0.62, // share of the cycle a foot is planted (>0.5 = a walk, not a run)
  reach: 0.085, // stride half-width, in tiles either side of the leg's base
  lift: 0.04, // ground clearance at mid-swing
  bob: 0.005, // body rise and fall -- the old 0.008 was 0.48px at tile 60
  // Body dips per gait cycle.
  //
  // Dropped 2 -> 1 (owner, 2026-08-10: too jiggly, and "part of it is the
  // pace"). The read is right and the arithmetic says why. For a travel
  // of A at rate w, peak velocity goes as A*w but peak ACCELERATION goes
  // as A*w^2 -- and jiggle is an acceleration percept. So halving the
  // rate takes three quarters of the bounce out while leaving the travel
  // untouched, which is the part that reads as life. Cutting the
  // amplitude instead would have traded the two off one for one.
  //
  // At `cycles` 2 the old setting put four body dips in every tile, which
  // at a live walk is about 5Hz -- a shiver, not a gait. One dip per gait
  // cycle is a cat's weight moving rather than a cat vibrating.
  beats: 1,
  bobPhase: 0.5, // where in the cycle the body sits lowest (0 = at footfall)
  pivot: 0.62, // where the limb hangs from, inside the body and out of sight
  hip: 0.2, // hind limb's pivot x
  shoulder: 0.66, // fore limb's pivot x
  spread: 0, // how far the far-side pair sits off the near one (depth, not stance)
  // --- Carriage. One ellipse cannot show a shoulder rising, but it can
  // LEAN, and the lean says most of what the shoulder was going to.
  roll: 0.05, // body lean per gait cycle, radians
  surge: 0.006, // and the small fore/aft shift of weight over the feet
  // ...at this many per gait cycle. Also halved: a cat shifts its weight
  // forward and back ONCE per stride. Twice was the "back and forth"
  // motion that read as fidgeting.
  surgeBeats: 1,
  // A walking cat holds its head remarkably level -- one of the strongest
  // quadruped signatures there is. The cat had this by accident (the walk
  // set head.cx and left head.cy alone, so the head did not bob AT ALL);
  // it is now deliberate and partial, because a little float reads alive
  // where none reads like the head is bolted to a passing rail.
  //
  // The rate is the thing, and getting it wrong is unmistakable. Two
  // mistakes made the cat walk like a bird (owner, 2026-08-10): a fore/aft
  // nod at the stride rate -- which is exactly the head-thrust a pigeon
  // walks with, and cats have no equivalent of it at all -- and a vertical
  // follow keyed to the BODY's bob, which runs at the footfall rate and so
  // dipped the head twice per stride. Thrust at 1x against dip at 2x
  // traces a figure-eight, and a figure-eight is a bird.
  //
  // A cat's head floats: ONE slow rise and fall per stride, slightly
  // behind the body, and no fore/aft travel whatsoever.
  // Kept deliberately UNDER the body's own bob: stabilization means the
  // head moves less than the shoulders it sits on, and at 0.007 it was
  // travelling 1.7px against the body's 1.2px at a 120px cat -- floating
  // more than the thing carrying it, which is a bird again by another
  // route. Roughly 60% of the body's travel, at half its rate.
  headLift: 0.003, // one rise and fall per stride, in units
  headLag: 0.12, // how far behind the body's own cycle it runs
  // --- Foreshortening, for the walk that runs toward or away from the
  // camera rather than across it. See the walking case for why these
  // exist at all; in short, a cat walking north covers no horizontal
  // ground, so a horizontal stride is 100% skate by construction.
  // Legs draw UNDER the body, so the body is the only thing hiding how
  // long they are. Everything here has to respect that: a foot pushed
  // clear of the silhouette stops being a glimpse of paw and becomes a
  // whole exposed stick (owner, 2026-08-10).
  depthNarrow: 0.06, // how much the body narrows head-on -- small, it is cover
  depthBob: 1.5, // extra bob, as a multiple of the base
  // With no stride left to spend, the step has to happen VERTICALLY: a
  // cat walking at you picks its feet up, because up is the only
  // direction still pointed at the camera.
  depthLift: 1.8, // extra foot clearance
  depthGround: 0.028, // how far the pairs part along the GROUND plane
  depthSwing: 0.018, // and the small sideways pass that goes with it
  depthTaper: 0.12, // the far pair thins with distance
};

/**
 * How far the cat stands off the ground, in tiles. Mutable for the lab.
 *
 * Today's cat is a body resting on 1.9px of paw: the body's underside sits
 * at 0.85 and the feet at 0.88, so there is almost no daylight beneath it.
 * That silhouette -- low mass, negligible legs, sliding horizontally -- is
 * what reads as an insect rather than a cat, and no amount of gait work
 * reaches it, because there is nowhere for the motion to happen.
 *
 * The lift raises the body, head and tail while leaving the FEET where
 * they are, which is what turns it into leg length. Because the ground
 * line never moves, render.js's CAT_GROUND_Y, the pond clip and the
 * landing settle all keep working untouched.
 *
 * A real cat's belly clearance is ~40% of its standing height. We are not
 * going there -- kitten.me has no legs at all and reads beautifully. This
 * only has to buy somewhere for an articulation to live.
 */
const PROPORTION = {
  lift: 0, // 0 is exactly today's cat
  // Shape, as multiples of the v1 cat -- 1 is the body this vocabulary
  // shipped with. Held as multipliers rather than radii because every pose
  // sets its own body (walking widens rx, the pounce crouch squashes ry,
  // sleep-curl is a ball); an absolute would overwrite all of that, a
  // scale respects it.
  //
  // Owner-dialled 2026-08-08. Note bodyW and bodyH move together here, so
  // the ASPECT is untouched at 1.52 -- this is a 10% bigger body, not a
  // rounder one. What it buys is head:body 0.71 -> 0.64, most of the way to
  // kitten.me's 0.61, by growing the body rather than shrinking the head.
  bodyW: 1.1,
  bodyH: 1.05,
  headR: 1,
  headY: 0.01, // head nudge after the ride-along, + is down
  headX: 0.02, // and along the body, + is forward (the base cat faces right)
};

/**
 * The rig: everything that moves and is NOT a pose.
 *
 * The vocabulary's great strength is that a pose is a parameter set, so a
 * transition is a lerp. That same design is also why the cats read as
 * drawings being swapped rather than as animals: a pose is a POSITION,
 * and an animal is mostly the LAG between positions -- the tail that has
 * not caught up, the head that led the turn, the ears that arrived late.
 * None of that can live in a pose, because none of it is a function of
 * the pose. It is a function of what the cat was doing a moment ago.
 *
 * So the rig sits AFTER the pose, and after any blend between poses, and
 * offsets it. Nothing here changes WHICH pose a cat is in; it only
 * changes how the cat got there. That ordering is the whole trick: it
 * applies to a blended layout as happily as to a held one, needs no new
 * entries in blendLayouts, and has nothing that can pop on a pose change.
 *
 * Two properties are load-bearing and easy to lose:
 *
 *  - The rest state is EXACTLY today's cat. Every channel springs toward
 *    zero, so a cat standing still with no input draws bit-identically to
 *    the un-rigged vocabulary. Still frames and reduced motion pass no
 *    rig at all, which is the same drawing by a shorter route.
 *  - The state is per-cat and disposable. `createRigState` is cheap and
 *    `stepRig` is pure in (state, input, dt), so a viewer joining the
 *    feed mid-flight builds fresh states AT REST rather than inheriting
 *    momentum that belongs to a moment it never saw. anim.js drops every
 *    rig on the same discontinuity path that already drops pose memory.
 */
const RIG = {
  // --- The tail. A cat's tail is a counterweight on a slow spring; ours
  // was a fixed curve per pose, which is why the only tail motion anyone
  // could find was 0.4px of idle sway and why the tail flick had to be
  // deleted rather than fixed. Two segments, follow-the-leader: the mid
  // drags against body motion and the tip inherits the mid's swing and
  // overshoots it. No flicks -- a flick is a discrete beat and reads as
  // aggression (owner, 2026-08-09). This is continuous, so it never
  // punctuates and can never be mistaken for a signal.
  tailOmega: 8.5, // spring rate, rad/s -- lower is heavier and lazier
  tailZeta: 0.55, // <1 is underdamped: the settle after a stop IS the point
  tailDrag: 0.030, // units of trail per tile/s of body speed
  tailWhip: 1.75, // how much further the tip travels than the mid
  tailLead: 0.34, // and how much of the mid's swing the first handle takes
  tailSwayAmp: 0.011, // ambient breath-driven sway at the tip
  tailMax: 0.11, // hard clamp: a sprinting cat never flings its tail off-box

  // --- The head. Underdamped on purpose: it leads into a move and
  // overshoots on the stop, which is most of what makes a cat look like
  // it DECIDED to walk rather than having been translated.
  headOmega: 13, // faster than the tail: less mass, shorter lever
  headZeta: 0.52,
  headDrag: 0.024, // + is forward, in units per tile/s
  headMax: 0.045,

  // --- Gaze. A cat that never looks at anything is furniture. One unit
  // vector in the cat's own facing space, sprung so a look travels
  // instead of snapping, and spent three ways.
  gazeOmega: 9,
  gazeZeta: 0.85,
  gazePupil: 0.36, // pupil travel inside the iris, in iris radii
  gazeHead: 0.05, // the head follows the eyes, in head radii
  gazeEar: 0.2, // and the ears turn with it, in radians

  // --- Ears. Light, fast, independent. A real twitch is ONE ear; the
  // boolean this replaces flipped both for 420ms, which is a switch and
  // not a motion.
  earOmega: 24,
  earZeta: 0.45,
  earTwitch: 0.42, // radians at full twitch
  earBackOmega: 12, // how fast ears ease back for a nap or a meal
  earBackZeta: 1,

  // --- The turn. Facing flips by mirroring, which on its own is a
  // 180-degree snap on the spot, every time a cat reverses.
  //
  // Tried and cut (owner, 2026-08-10): scaling the cat horizontally
  // through the turn, cos being the honest projection of a flat cat
  // rotating about its vertical axis. It is arithmetically right and
  // visually wrong, and no dial reaches it -- the narrowing IS the
  // reveal. A three-quarter drawing is what a squeeze needs to squeeze
  // TOWARD, and we do not have one, so the cat can only narrow toward
  // being a card and duly reads as one. That is a job for 3D cats, not
  // for a tuning pass.
  //
  // What is left carries the turn on WEIGHT instead of width, which is
  // how sprite animation has always done it: the cat drops onto its
  // front feet, the facing swaps at the bottom of the dip -- where the
  // silhouette says least and the eye is least able to catch the swap --
  // and it rebounds. No horizontal scale at any frame. The mirror is
  // still instant; it is simply no longer the thing you are looking at.
  //
  // Set VIEW.turnMs to 0 in anim.js to go back to the bare instant flip:
  // turnFor then never returns a turn and none of this runs.
  turnSquash: 0.09, // how far the cat drops through the pivot
  turnFlipAt: 0.5, // where in the dip the mirror happens
  turnWiden: 0.7, // and how much of the lost height goes to width

  // --- The yawn: an idle OVERLAY rather than a pose, so it can happen on
  // top of whatever the cat is already doing and needs no engine state.
  yawnMouth: 0.36, // how far the mouth opens, in head radii
  yawnHeadTilt: -0.03, // and the chin lifts (units; - is up)
};

const rclamp = (v, lo, hi) => (v < lo ? lo : v > hi ? hi : v);
const smooth01 = (t) => {
  const u = rclamp(t, 0, 1);
  return u * u * (3 - 2 * u);
};

/**
 * One 2-D channel of a damped spring, integrated semi-implicitly.
 * `omega` is rad/s; `zeta` is the damping ratio -- 1 is critical (no
 * overshoot at all), and below 1 it rings, which is where the life is.
 */
function springStep(s, tx, ty, omega, zeta, dt) {
  const k = omega * omega;
  const c = 2 * zeta * omega;
  s.vx += (-k * (s.x - tx) - c * s.vx) * dt;
  s.vy += (-k * (s.y - ty) - c * s.vy) * dt;
  s.x += s.vx * dt;
  s.y += s.vy * dt;
}

/** A fresh rig, at rest. Every channel zero, so an un-stepped rig draws
 * the vocabulary exactly as it was -- which is what a new connection, a
 * still frame and a reduced-motion frame all get, by construction. */
function createRigState() {
  const ch = () => ({ x: 0, y: 0, vx: 0, vy: 0 });
  return { tailMid: ch(), tailTip: ch(), head: ch(), gaze: ch(), ears: ch() };
}

/**
 * Advances one cat's rig and returns the bag `applyRig` consumes.
 *
 * `input` is what the world knows about this cat right now:
 *   vx, vy         body velocity in TILES PER SECOND, screen axes (y down)
 *   facing         'left' | 'right' -- rig space is the cat's own, so this
 *                  is what turns screen velocity into forward and back
 *   gazeX, gazeY   unit-ish vector toward whatever it is attending to, in
 *                  screen axes, or 0 for "nothing in particular"
 *   earTwitch      0..1 envelope, with earTwitchSide picking which ear
 *   earsBack       0..1 target (naps, meals, the sad beat)
 *   yawn           0..1
 *   breath         0..1 phase for the ambient sway
 *
 * dt is clamped and substepped: a spring integrated across a 300ms
 * hidden-tab hitch does not ring, it detonates.
 */
function stepRig(state, input, dtMs) {
  // Four facings since 2026-08-10. What matters here is not the direction
  // but the MIRROR: a side view is drawn mirrored for left, so its forward
  // is always +x in drawn space and the sign lives in `vf`. An axial view
  // is not mirrored at all, so its forward really is up or down the screen
  // and that sign has to survive into the target.
  const axial = input.facing === 'north' || input.facing === 'south';
  const dir = input.facing === 'left' || input.facing === 'north' ? -1 : 1;
  // The rig lives in the cat's OWN space, so the instant a cat mirrors,
  // every x offset it is carrying means the opposite thing in the world:
  // a tail trailing west becomes a tail trailing east, in one frame. That
  // is a pop on every single reversal, and it is there whether the turn
  // is animated or instant. Negating x and its velocity preserves the
  // world-space motion across the mirror, so the tail simply keeps
  // swinging the way it was already going and swings round after.
  if (state.facing !== undefined && state.facing !== input.facing) {
    for (const ch of [state.tailMid, state.tailTip, state.head, state.gaze]) {
      ch.x = -ch.x;
      ch.vx = -ch.vx;
    }
  }
  state.facing = input.facing;
  // Speed along the nose, positive when the cat is going where it faces...
  const vf = axial ? (input.vy || 0) * dir : (input.vx || 0) * dir;
  // ...and across it. Cats move on four axes only, so an axial cat has no
  // sideways travel to speak of.
  const vd = axial ? 0 : input.vy || 0;
  // Gaze arrives in screen axes; head-on there is no mirror to undo.
  const gx = axial ? input.gazeX || 0 : (input.gazeX || 0) * dir;
  const gy = input.gazeY || 0;
  const twitch = input.earTwitch || 0;

  let left = rclamp(dtMs, 0, 250) / 1000;
  while (left > 0) {
    const dt = Math.min(1 / 120, left);
    left -= dt;
    // The tail trails: its target is the negation of where the body is
    // going, so it is always behind -- and it keeps travelling after the
    // body stops, because the spring still has velocity when the cat
    // does not. That settle is the single most alive thing here.
    // The drag is along the nose either way, but an axial cat's nose points
    // up or down the screen rather than along +x, so the whole trail moves
    // onto the y channel.
    const trail = rclamp(-RIG.tailDrag * vf, -RIG.tailMax, RIG.tailMax);
    springStep(
      state.tailMid,
      axial ? 0 : trail,
      axial ? trail * dir : rclamp(-RIG.tailDrag * vd * 0.6, -RIG.tailMax, RIG.tailMax),
      RIG.tailOmega, RIG.tailZeta, dt,
    );
    // Follow-the-leader, so the curve BENDS instead of the whole tail
    // sliding as one rigid stick.
    springStep(
      state.tailTip,
      state.tailMid.x * RIG.tailWhip,
      state.tailMid.y * RIG.tailWhip,
      RIG.tailOmega * 0.8, RIG.tailZeta * 0.85, dt,
    );
    const lead = rclamp(RIG.headDrag * vf, -RIG.headMax, RIG.headMax);
    springStep(
      state.head,
      axial ? 0 : lead,
      axial ? lead * dir : rclamp(-RIG.headDrag * vd * 0.5, -RIG.headMax, RIG.headMax),
      RIG.headOmega, RIG.headZeta, dt,
    );
    springStep(state.gaze, gx, gy, RIG.gazeOmega, RIG.gazeZeta, dt);
    springStep(
      state.ears,
      twitch * RIG.earTwitch * (input.earTwitchSide || 1),
      input.earsBack || 0,
      twitch ? RIG.earOmega : RIG.earBackOmega,
      twitch ? RIG.earZeta : RIG.earBackZeta,
      dt,
    );
  }

  const sway = RIG.tailSwayAmp * Math.sin((input.breath || 0) * TAU);
  return {
    tailMid: { x: state.tailMid.x, y: state.tailMid.y },
    tailTip: { x: state.tailTip.x, y: state.tailTip.y + sway },
    head: { x: state.head.x, y: state.head.y },
    gaze: { x: state.gaze.x, y: state.gaze.y },
    // The near ear takes the twitch and the far one answers, smaller and
    // opposite -- which is what stops a twitch reading as a head shake.
    earNear: state.ears.x + state.gaze.x * RIG.gazeEar,
    earFar: state.ears.x * -0.35 + state.gaze.x * RIG.gazeEar,
    earsBack: rclamp(state.ears.y, 0, 1),
    yawn: input.yawn || 0,
  };
}

/**
 * Lays a rig over a finished (possibly blended) layout.
 *
 * Offsets only. Every channel is zero at rest, so `applyRig(L, null)` and
 * a rig that has never been stepped are the same drawing as no rig at
 * all -- the property that keeps still frames, reduced motion and a
 * fresh connection honest without any of them knowing the rig exists.
 */
function applyRig(L, rig) {
  if (!rig) return L;
  const t = L.tail;
  // The base stays welded to the rump and the curve bends along its
  // length, most at the tip. A tail translated bodily reads as a prop
  // someone is holding next to the cat.
  t.c1x += rig.tailMid.x * RIG.tailLead;
  t.c1y += rig.tailMid.y * RIG.tailLead;
  t.c2x += rig.tailMid.x;
  t.c2y += rig.tailMid.y;
  t.x1 += rig.tailTip.x;
  t.y1 += rig.tailTip.y;

  L.head.cx += rig.head.x + rig.gaze.x * L.head.r * RIG.gazeHead;
  L.head.cy +=
    rig.head.y + rig.gaze.y * L.head.r * RIG.gazeHead + rig.yawn * RIG.yawnHeadTilt;

  if (rig.earsBack) L.earsBackAmt = Math.max(L.earsBackAmt || 0, rig.earsBack);
  L.earNear = rig.earNear;
  L.earFar = rig.earFar;
  L.gaze = rig.gaze;
  L.yawn = rig.yawn;
  return L;
}

/**
 * The rig a STILL frame gets: every spring at rest, and the gaze placed
 * directly at its target with no travel.
 *
 * Gaze is the one channel here that carries INFORMATION rather than
 * motion. Where a cat is looking is a fact about the served world -- the
 * same kind of fact as the focused hunting eyes, or a worn path, and both
 * of those draw in still frames. `wetFor` sets the precedent exactly: a
 * still frame takes wetness at full strength rather than not at all,
 * because the fade is the motion and the wetness is the state. Here the
 * travel is the motion and the direction is the state.
 *
 * Without this, a hunting cat under reduced motion kept its focused eyes
 * but lost the fact that it was looking AT something -- the two halves of
 * one cue disagreeing.
 *
 * Nothing else is populated, so a reduced-motion cat still holds its
 * pose, its tail, its ears and its breath exactly as it always did; and
 * because this touches no spring state, a still frame can neither seed
 * nor disturb a live rig. Pure, like everything else a still frame reads.
 */
function stillRig(input) {
  if (!input) return null;
  const axial = input.facing === 'north' || input.facing === 'south';
  const dir = input.facing === 'left' ? -1 : 1;
  const gx = axial ? input.gazeX || 0 : (input.gazeX || 0) * dir;
  const gy = input.gazeY || 0;
  // Nothing has this cat's attention: the un-rigged drawing, as before.
  if (!gx && !gy) return null;
  const zero = { x: 0, y: 0 };
  return {
    tailMid: zero,
    tailTip: zero,
    head: zero,
    gaze: { x: gx, y: gy },
    // The ears turn with the look, as they do live -- it is one cue, and
    // splitting it would make the still frame disagree with the moving one.
    earNear: gx * RIG.gazeEar,
    earFar: gx * RIG.gazeEar,
    earsBack: 0,
    yawn: 0,
  };
}

/**
 * The on-the-spot turn, as a canvas transform.
 *
 * `t` runs 0..1 and the FACING flips at the midpoint, so both ends are
 * exactly the mirrored drawings the vocabulary already produced: the
 * turn only fills in the middle, where there used to be nothing at all.
 * cos is the honest projection of a flat cat rotating about its own
 * vertical axis; the floor stops it vanishing at small sizes, and the
 * lift and stretch are the cat pushing off its front feet.
 */
/**
 * Which way the cat is DRAWN at a point in a turn: still the facing it
 * had BEFORE the turn until the mirror lands, the served one after.
 *
 * Exported because two places need it and they must agree exactly --
 * paintBox, to draw it, and the rig, which has to flip its world-space
 * momentum on the same frame the drawing does. Computing it separately
 * in each is two places to get the polarity wrong, which is precisely
 * what happened: drawing the served facing immediately and then swapping
 * at the midpoint gives a flip, a flip back, and a third flip when the
 * turn ends -- one turn read as two.
 */
function turnFacing(facing, turn) {
  if (turn == null) return facing;
  // A turn is a horizontal flip, so only a horizontal facing has anything
  // to turn THROUGH. Without this guard the ternary below reads 'north' as
  // "not left" and hands back 'left' -- an axial cat drawn side-on for the
  // first half of a turn, then snapping back. It cannot fire today (a turn
  // is only stamped on a horizontal step, so the facing is horizontal for
  // the 200ms it lasts), but this is a two-value function that has been
  // taking four values since the axial facings landed in #187, and the
  // gap closes the moment turnMs outgrows a tick or a vertical reversal
  // starts stamping turns too.
  if (facing !== 'left' && facing !== 'right') return facing;
  if (turnTransform(turn).flipped) return facing;
  return facing === 'left' ? 'right' : 'left';
}

function turnTransform(t) {
  const u = rclamp(t, 0, 1);
  const dip = Math.sin(Math.PI * u);
  const sy = 1 - RIG.turnSquash * dip;
  return {
    // Widening is safe where narrowing was not: a compressing cat is
    // expected to spread, and spreading says nothing about whether it
    // has a third dimension.
    sx: 1 + (1 - sy) * RIG.turnWiden,
    sy,
    lift: 0,
    flipped: u >= RIG.turnFlipAt,
  };
}

/**
 * Overwrites a finished side-view layout with its axial equivalent.
 *
 * Runs AFTER the pose switch rather than inside it, so a pose with no
 * axial authoring simply keeps the side drawing it already had -- the
 * fallback is "draw the cat we have", never "draw nothing".
 *
 * `back` is the walking-away view (moving north, up-screen) and `front`
 * is the walking-toward one (south). The difference between them is small
 * in the layout and large in the paint: the back view has no face, and its
 * tail is the whole silhouette.
 */
function applyAxial(L, pose, phase, view, opts) {
  const back = view === 'back';
  const swimming = pose === 'swim';
  const walking = pose === 'walking';
  // Distance-keyed like the side walk, so feet still plant against ground
  // covered rather than against time.
  const cycle = walking ? phase * GAIT.cycles : 0;
  const breathe = walking ? 0 : Math.sin(phase * TAU);

  const bob = walking ? AXIAL.bob * Math.cos((cycle - GAIT.bobPhase) * GAIT.beats * TAU) : 0;
  const sway = walking ? AXIAL.sway * Math.sin(cycle * TAU) : 0;
  const roll = walking ? AXIAL.roll * Math.sin(cycle * TAU) : 0;

  // The camera treatment moves the body and the head and nothing else --
  // the gait, the tail and the paint order are the same drawing at any
  // angle.
  const C = AXIAL_CAMERAS[(opts && opts.camera) || AXIAL.camera] || AXIAL_CAMERAS.elevation;

  // Swimming end-on: the same camera, but afloat. A slow bob and roll
  // instead of a gait, a flattened back, the chin down toward the surface
  // -- and no legs at all, which is the side pose's rule for the same
  // reason (they are under the water, and the clip would eat them anyway).
  if (swimming) {
    const swimBob = AXIAL_SWIM.bob * Math.sin(phase * TAU);
    const swimRock = AXIAL_SWIM.rock * Math.sin(phase * TAU * 0.5);
    L.body = {
      cx: 0.5,
      cy: C.bodyY + AXIAL_SWIM.bodyDrop + swimBob,
      rx: AXIAL_SWIM.bodyRx,
      ry: AXIAL_SWIM.bodyRy,
      rot: swimRock,
    };
    L.head = {
      cx: 0.5,
      cy: (back ? C.headYBack : C.headYFront) + AXIAL_SWIM.headDrop + swimBob,
      r: back ? C.headRBack : C.headRFront,
    };
    // Legs are already empty: the side swim pose drew none, and this
    // branch has no reason to put any back -- they are under water, and
    // the clip would take them anyway. (Asserted rather than re-assigned,
    // so if the side pose ever grows legs this is a test failure and not a
    // silent difference between the two views.)
    //
    // Out of the water, not under it. The base stays below the surface --
    // it leaves a submerged rump -- and everything above the clip is the
    // raised length, which is the whole point of drawing it.
    const stern = C.bodyY + AXIAL_SWIM.bodyDrop + AXIAL_SWIM.tailBaseDrop + swimBob;
    const top = AXIAL_SWIM.tailTopY + swimBob;
    if (back) {
      // Swimming away: the tail is the near end, so its whole raised
      // length is in view. Out from behind the rump, then up.
      const tip = AXIAL_SWIM.tailOutX;
      L.tail = {
        x0: 0.5, y0: stern,
        c1x: tip - AXIAL_SWIM.tailCurve, c1y: stern - 0.02,
        c2x: tip + AXIAL_SWIM.tailCurve, c2y: top + 0.16,
        x1: tip, y1: top,
      };
    } else {
      // Swimming toward you: the tail is the far end and paints behind the
      // body, so only what clears the flank is seen -- a raised tip over
      // the shoulder rather than a whole tail.
      const tip = AXIAL_SWIM.tailPeekX;
      L.tail = {
        x0: 0.5, y0: stern,
        c1x: 0.5 + (tip - 0.5) * 0.5, c1y: stern - 0.02,
        c2x: tip + AXIAL_SWIM.tailCurve, c2y: top + 0.14,
        x1: tip, y1: top,
      };
    }
    L.view = view;
    return L;
  }

  L.body = {
    cx: 0.5 + sway,
    cy: C.bodyY + bob,
    rx: C.bodyRx,
    ry: C.bodyRy + (walking ? 0 : 0.006 * breathe),
    rot: roll,
  };
  L.head = {
    cx: 0.5 + sway * AXIAL.headSway,
    cy: (back ? C.headYBack : C.headYFront) + bob * AXIAL.headFollow,
    r: back ? C.headRBack : C.headRFront,
  };

  // Four legs, on the same diagonal sequence the side walk uses. In this
  // view a step is a LIFT, because the swing is pointed at the camera.
  // Walking away, the HIND legs are the near pair; walking toward, the
  // forelegs are. `far` decides which side of the body a leg is drawn on.
  const leg = (dx, u, far) => {
    const g = walking ? gaitStep(((u % 1) + 1) % 1, GAIT.duty) : { x: 0, lift: 0 };
    const x = 0.5 + dx + sway * 0.4;
    return {
      x,
      hx: 0.5 + dx * 0.6,
      top: AXIAL.legTop,
      bottom: CAT_GROUND - AXIAL.lift * g.lift,
      w: AXIAL.legW,
      far,
    };
  };
  // The lateral sequence -- hind, then the fore on the SAME side, then
  // across: left hind, left fore, right hind, right fore, evenly spaced.
  // The first cut ran left-fore, right-hind, left-hind, right-fore, which
  // is a diagonal pattern, and a diagonal pattern is a trot. That is most
  // of what read as a canter.
  const hind = back ? -AXIAL.legNear : -AXIAL.legFar;
  const fore = back ? -AXIAL.legFar : -AXIAL.legNear;
  L.legs = [
    leg(hind, cycle, !back),
    leg(fore, cycle - 0.25, back),
    leg(-hind, cycle - 0.5, !back),
    leg(-fore, cycle - 0.75, back),
  ];

  if (back) {
    // Out from behind the rump, then up: an S that leaves the base hidden
    // by the body and puts the whole raised length clear of the silhouette.
    const tip = AXIAL.tailOutX + AXIAL.tailSway * Math.sin(cycle * TAU) + sway;
    L.tail = {
      x0: AXIAL.tailBaseX + sway * 0.5, y0: AXIAL.tailBaseY,
      c1x: AXIAL.tailOutX + AXIAL.tailCurve, c1y: AXIAL.tailBaseY - 0.02,
      c2x: tip + AXIAL.tailCurve, c2y: AXIAL.tailTopY + 0.16,
      x1: tip, y1: AXIAL.tailTopY,
    };
  } else {
    // Behind the cat, so only what clears the body's edge is seen.
    L.tail = {
      x0: 0.5, y0: AXIAL.tailBaseY,
      c1x: 0.5 + AXIAL.tailPeekX * 0.5, c1y: AXIAL.tailBaseY + 0.02,
      c2x: 0.5 + AXIAL.tailPeekX, c2y: AXIAL.tailPeekY + 0.06,
      x1: 0.5 + AXIAL.tailPeekX * 0.85, y1: AXIAL.tailPeekY,
    };
  }
  L.view = view;
  return L;
}

/**
 * Applies PROPORTION.lift to a finished layout.
 *
 * `airborne` is the whole point of the signature. A foot on the ground is
 * positioned against the GROUND, so it must not move -- that is what
 * lengthens the leg. But the pounce's leap has both feet already clear of
 * the ground, where they are positioned against the BODY, and lifting the
 * body out from under them would detach the limbs mid-leap. So grounded
 * poses lift everything except `bottom`, and airborne ones lift the foot
 * too, keeping the limb rigid.
 *
 * Runs inside catLayout, so nothing downstream ever sees an unlifted cat
 * and blendLayouts needs no new field.
 */
function liftLayout(L, airborne) {
  const d = PROPORTION.lift;
  if (!d) return L;
  const up = (y) => y - d;
  L.body.cy = up(L.body.cy);
  L.head.cy = up(L.head.cy);
  const t = L.tail;
  t.y0 = up(t.y0); t.c1y = up(t.c1y); t.c2y = up(t.c2y); t.y1 = up(t.y1);
  L.legs = L.legs.map((leg) => ({
    ...leg,
    top: up(leg.top),
    bottom: airborne ? up(leg.bottom) : leg.bottom,
  }));
  return L;
}

/**
 * Pounce timing, mutable for the lab like GAIT and SWIM.
 *
 * `phase` is tick progress, so the whole beat is one served tick (800ms
 * live). The old pose was a two-position switch at 0.45 -- loaded, then
 * suddenly extended -- which is why it popped. These three numbers say
 * how long the cat stays loaded, how fast it extends, and how sharply.
 */
const POUNCE = {
  hold: 0.3, // share of the beat spent loaded and wiggling
  launch: 0.42, // share spent extending
  land: 0.18, // and absorbing the landing; the rest is the recovery
  snap: 4, // >1 front-loads the extension. A cat launches, it does not glide.
  // The wiggle. A cat about to pounce treads its hind feet and rocks its
  // hindquarters, and that anticipation is what makes the launch read as
  // a decision rather than a teleport. From the side it projects as a
  // small vertical rock plus a lean -- exactly what one ellipse can say.
  // (Deliberately not a tail flick: flicks read as aggression.)
  // The wiggle's rate is a real-world FREQUENCY, not a count of rocks
  // (2026-08-10). It was authored as "2.5 rocks per load", which is a
  // share of a beat rather than a speed -- so when the pounce was
  // compressed to one 800ms tick the load became 176ms and those 2.5
  // rocks became 14Hz. A cat's hindquarters rock at about 3Hz; 14Hz is a
  // vibration, and it read as one.
  //
  // Expressed in Hz it is immune to that: the beat can be any length and
  // the wiggle still looks like a cat gathering itself. Same class of bug
  // as the body bob running at twice the gait cycle, and the same lesson --
  // what reads as "shaking" is almost always rate, not amplitude, because
  // acceleration goes as the SQUARE of the rate.
  // NOTE the quantiser below floors this at half a cycle, so at the shipped
  // 192ms load anything under ~3.9 lands on the same 2.60Hz rock. Owner set
  // 1 (2026-08-10) knowing that: it is the amplitude that moved. To get a
  // rock genuinely SLOWER than 2.6Hz, lengthen `hold` -- a half cycle over
  // the load is the floor by construction.
  wiggleHz: 1, // rocks per second
  // 0.012 was tried and reverted: the rock came to 0.29px on a 31px tile
  // and 0.50px at 54, under both floors this project has measured (the
  // whiskers died at ~0.8px, the body bob was reverted at 0.56px). At 0.022
  // it is 0.52px / 0.91px -- marginal in the demo world, clear on a large
  // display. NOTE the dial is not the travel: the rock rides an envelope
  // whose peak is ~0.77 of this, so quoting wiggleAmp overstates it.
  wiggleAmp: 0.002, // vertical, in units
  wiggleRot: 0.01, // and the lean that comes with it, in radians
  // The side-to-side half of the tread (2026-08-10, owner's ask). A cat
  // gathering itself shifts its weight between its hind paws, which is a
  // LATERAL motion -- and a side-profile cat has no lateral axis on screen.
  // So it is drawn the way the walk already draws a cat coming toward the
  // camera: as depth, by narrowing the body (GAIT.depthNarrow, same idea).
  //
  // Anchored at the CHEST, not the centre. Narrowing about the middle would
  // slide the front, and a planted front is most of why the pose reads as
  // aiming -- the same thing the rot sign cost us. Holding `cx + rx` fixed
  // instead means the width comes off the BACK: the hindquarters swing
  // toward and away while the shoulders stay exactly where they are.
  //
  // A quarter-cycle behind the vertical rock, so the rear traces an ellipse
  // -- up-and-back, down-and-forward -- which is what a weight shift does,
  // rather than pulsing in and out on the same beat.
  wiggleSway: 0.085, // share of body length the rear swings, in depth
  twitch: 0, // tail-tip twitch while loading -- kept, and kept at 0
};

/**
 * The butt wiggle, 0 outside the load. Grows as the cat commits and
 * lands on exactly zero at the launch: anticipation that faded out
 * would read as the cat changing its mind.
 *
 * `beatMs` is how long the whole pounce beat lasts -- one served tick, so
 * 800ms by default. The rock count is derived from it and `wiggleHz`,
 * which is what keeps the wiggle's SPEED constant across tick lengths.
 *
 * Quantised to half a cycle, and never less than half: a half-integer
 * count is what lands the sine on exactly zero at the launch, and the
 * floor guarantees at least one visible rock however short the beat gets.
 * At 800ms this comes out at one rock, around 2.8Hz -- and one deliberate
 * rock reads far more like a cat gathering itself than two and a half
 * blurred ones did.
 */
/**
 * The lateral half of the tread: the same rock, a quarter-cycle behind, so
 * the hindquarters trace an ellipse instead of pumping along one axis.
 *
 * Shares `pounceWiggle`'s envelope and its half-cycle quantisation, so it
 * grows with the load and lands on zero at the launch exactly as the
 * vertical rock does -- if it did not, the body would still be swung
 * sideways at the moment the cat leaves the ground.
 */
function pounceWiggleSway(phase, dials = POUNCE, beatMs = 800) {
  if (phase >= dials.hold) return 0;
  const holdSec = (dials.hold * beatMs) / 1000;
  const cycles = Math.max(0.5, Math.round(dials.wiggleHz * holdSec * 2) / 2);
  const u = phase / Math.max(1e-6, dials.hold);
  // `sin(u*PI)` and not the vertical rock's `sin(u*PI/2)` envelope: this one
  // has to vanish at BOTH ends. A quarter-cycle shift of the rock does not --
  // sin(u*TAU*c - PI/2) is 1 when u is 1, so the body would still be swung
  // sideways at the instant the cat leaves the ground, and the launch popped
  // by 0.5px. Same failure the half-cycle quantisation exists to prevent,
  // one axis over.
  //
  // What it draws, at half a cycle: the rear swings one way, then the other,
  // while the vertical rock does a single rise and fall. One weight shift.
  return Math.sin(u * Math.PI) * -Math.cos(u * TAU * cycles);
}

function pounceWiggle(phase, dials = POUNCE, beatMs = 800) {
  if (phase >= dials.hold) return 0;
  const holdSec = (dials.hold * beatMs) / 1000;
  const cycles = Math.max(0.5, Math.round(dials.wiggleHz * holdSec * 2) / 2);
  const u = phase / Math.max(1e-6, dials.hold);
  return Math.sin(u * Math.PI * 0.5) * Math.sin(u * TAU * cycles);
}

/**
 * How far through the launch `phase` is: 0 while loaded, 1 once extended.
 *
 * `snap` shapes it as 1-(1-u)^snap -- most of the travel in the first
 * part of the window, decelerating into the reach. Exactly 0 and exactly
 * 1 at the ends, which is what lets the crouch and the leap stay the
 * drawings they already were.
 */
function pounceLaunch(phase, dials = POUNCE) {
  const u = (phase - dials.hold) / Math.max(1e-6, dials.launch);
  if (u <= 0) return 0;
  if (u >= 1) return 1;
  return 1 - (1 - u) ** dials.snap;
}

/**
 * Applies PROPORTION's shape multipliers to a finished layout.
 *
 * The belly floor -- the body ellipse's lowest point -- is the invariant.
 * Scaling `ry` about the centre would push the underside through the
 * ground (or lift it off), which is a stand-height change wearing a
 * proportion costume; `lift` is the dial for that, and confusing the two
 * makes neither judgeable. So the floor stays and the centre moves.
 *
 * Everything that rides the body rides that move: head, tail, and each
 * limb's pivot. Feet do not -- they are positioned against the GROUND, so
 * holding them is exactly what turns a rounder body into more visible leg.
 * Airborne poses are the documented exception, same rule as liftLayout.
 *
 * Measured consequence, for whoever tunes this: at a leg's x the ellipse
 * edge sits above the floor by ry*(1 - sqrt(1 - t^2)) less than at the
 * centre, so raising ry and the centre together RAISES the belly over the
 * legs. Rounding the body out is what buys daylight; the head ratio buys
 * none of it, only headroom.
 */
function proportionLayout(L, airborne) {
  const { bodyW, bodyH, headR, headY, headX } = PROPORTION;
  if (bodyW === 1 && bodyH === 1 && headR === 1 && !headY && !headX) return L;

  const floor = L.body.cy + L.body.ry;
  L.body.rx *= bodyW;
  L.body.ry *= bodyH;
  const dy = floor - L.body.ry - L.body.cy; // how far the centre had to move
  L.body.cy += dy;

  L.head.r *= headR;
  L.head.cy += dy + headY;
  L.head.cx += headX;

  const t = L.tail;
  t.y0 += dy; t.c1y += dy; t.c2y += dy; t.y1 += dy;

  L.legs = L.legs.map((leg) => ({
    ...leg,
    top: leg.top + dy,
    bottom: airborne ? leg.bottom + dy : leg.bottom,
  }));
  return L;
}

/**
 * The reach that actually plants a foot, for a given duty and step count.
 *
 * Moving backward is not enough: a foot that drifts back too SLOWLY still
 * skates, just less. To hold still against the world it has to sweep back
 * through exactly the ground the cat covers while it is down -- the cat
 * travels 1/cycles of a tile per step and is planted for `duty` of that,
 * so 2 * reach must equal duty / cycles.
 *
 * This is why the step count matters, and it is the whole reason `cycles`
 * exists. Reach has a hard ceiling of 0.14: a leg here is a free peg, not
 * a limb on a hip, so a foot that reaches past the body's own edge
 * (the walking body spans x 0.12..0.76) leaves a stick hanging in the air
 * with no cat above it. Planting therefore needs
 * duty / (2 * cycles) <= 0.14 -- at least THREE steps per tile at a 0.62
 * duty. One step per tile wants a reach of 0.31 and cannot be planted at
 * all, only made less bad, which is where this started.
 */
function plantedReach(dials = GAIT) {
  return dials.duty / (2 * dials.cycles);
}

/**
 * The paw is a half-disc of radius w/2 struck at `bottom`, so a foot
 * lifted past (height - w/2) puts the arc above the leg's own top and
 * the path turns inside out. Nothing downstream notices -- the harness's
 * mock ctx only rejects non-finite numbers, and an inverted path is
 * perfectly finite -- so the ceiling is asserted in test-motion.mjs
 * instead. 0.14 tall, 0.095 wide => 0.0925 of headroom.
 */
const MAX_LIFT = 0.0925;

/**
 * The far-side pair: the same legs a little further off, drawn FIRST and
 * in shade so they sit behind.
 *
 * Two legs read as a biped the moment they stop being pegs and start
 * being limbs -- a horizontal body with a tail on two articulated legs is
 * a theropod, which is exactly what the first cut looked like. The second
 * pair is the whole difference between a cat and a dinosaur.
 *
 * Narrow tracking (a cat sets its paws almost on one line) means the
 * offset is small: this is depth, not a stance.
 */
function withFarPair(legs, dx = GAIT.spread) {
  const far = legs.map((l) => ({ ...l, x: l.x + dx, hx: (l.hx ?? l.x) + dx, far: true }));
  return [...far, ...legs];
}

/**
 * How far the far-side pair sits off the near one, for the two poses that
 * want it -- mutable for the lab like GAIT/SWIM/EYE.
 *
 * Every pose already asked for a far pair; `withFarPair` defaulted its
 * offset to `GAIT.spread`, which is 0, so the far legs drew EXACTLY behind
 * the near ones and were invisible. That is right for most of the
 * vocabulary -- a cat standing square shows two legs from the side -- but
 * wrong for these two, where the body is twisted or extended and the
 * far-side legs would genuinely come into view.
 *
 * Negative, i.e. offset toward the tail: at these attitudes the far side
 * is the one rotated away from the camera, so its legs trail the near
 * pair rather than leading it. Small on purpose -- about 3% of a tile, so
 * it reads as depth at 120px and quietly vanishes at 31px, where a
 * one-pixel outline would only muddy the silhouette.
 */
const FAR_LEGS = {
  pounce: -0.03,
  stretch: -0.035,
};

/**
 * One leg's offset at its own phase `u` in [0,1). Returns a stride
 * position in -1..1 (+1 forward) and a lift in 0..1, both unitless --
 * GAIT scales them. Continuous at u=0/1 and across the stance/swing
 * seam, so the cycle wraps without a snap at the tick boundary.
 */
function gaitStep(u, duty) {
  if (u < duty) {
    // Planted: a straight backward drift. Linear on purpose -- the
    // ground moves at a constant rate, and easing this is what made the
    // old sine read wrong.
    return { x: 1 - 2 * (u / duty), lift: 0 };
  }
  // Airborne: forward again, eased at both ends so the foot settles into
  // its next stance rather than snapping into it, and arcing over.
  const v = (u - duty) / (1 - duty);
  return { x: -Math.cos(v * Math.PI), lift: Math.sin(v * Math.PI) };
}

/** The stable per-kitty appearance (FR-003). The one override point when
 * served appearance data exists someday: callers never index PALETTES. */
function appearanceFor(kittyId) {
  return PALETTES[kittyId % PALETTES.length];
}

/**
 * Twilight fur (dusk/night themes): the same appearance, every fur color
 * dimmed by the theme's named factor -- which also cures the "white
 * outline" a pale colorway like the seal point grows against dark grass,
 * since that ring is simply near-white furBase at full daylight
 * brightness. Eyes are the deliberate exception at every hour: dusk and
 * night are when a cat's eyes shine. The night factor was tuned live
 * (2026-07-22); dusk barely dims -- golden hour flatters the fur.
 */
const FUR_SHADE_BY_THEME = Object.freeze({ day: 1, dusk: 0.96, night: 0.89, dawn: 0.94 });

function shadeHex(hex, factor) {
  const n = parseInt(hex.slice(1), 16);
  const r = Math.round(((n >> 16) & 255) * factor);
  const g = Math.round(((n >> 8) & 255) * factor);
  const b = Math.round((n & 255) * factor);
  return `#${((r << 16) | (g << 8) | b).toString(16).padStart(6, '0')}`;
}

/**
 * Mix a hex toward white. `shadeHex` cannot do this: it multiplies each
 * channel, so a factor above 1 runs past 255 and wraps the byte, turning a
 * pale cat lurid. Clamped, and separate rather than a fix to shadeHex,
 * which every caller uses to DARKEN and none to lighten.
 */
function lightenHex(hex, t) {
  const n = parseInt(hex.slice(1), 16);
  const up = (c) => Math.min(255, Math.round(c + (255 - c) * t));
  const r = up((n >> 16) & 255);
  const g = up((n >> 8) & 255);
  const b = up(n & 255);
  return `#${((r << 16) | (g << 8) | b).toString(16).padStart(6, '0')}`;
}

/**
 * How far a cat's pupils are open, by hour (2026-08-10).
 *
 * Real pupils open in the dark, and this world already knows what time it
 * is -- so the cue arrives on the same clock as the fur shading and the
 * shadow lean, and costs one number. A night cat's wide round pupil is
 * also, conveniently, the cuter one; a midday cat's narrower one is the
 * more catlike. The hour gets to choose rather than us.
 */
// Re-dialled 2026-08-10 alongside the larger resting pupil: these are set
// so that every hour lands just UNDER the aperture clamp rather than
// against it. A clamped value is a dial that silently stops responding,
// which is the worst thing to hand someone who is tuning.
const PUPIL_DILATE_BY_THEME = Object.freeze({ day: 1, dusk: 1.11, night: 1.22, dawn: 1.13 });

/**
 * Takes on the hunter's face, 2026-08-10.
 *
 * The brief that finally pinned this down: "an adorable little kitten
 * pouncing on a toy -- me so fierce!". That reconciles ferocious with
 * not-cartoony, which sound opposed and are not. The ferocity belongs to
 * the KITTEN'S EFFORT rather than to any real threat: the eye mechanics
 * should be a genuine predator's, and the animal wearing them should be
 * far too small for it. Cartoony is what you get when the mechanics are
 * fake; evil is what you get when the animal is convincing.
 *
 * Each take locates the ferocity somewhere different, which is the only
 * honest way to offer three of anything:
 *
 *   intense  SHIPPED. The first take, revived. Ferocity from a lowered
 *            brow, which dilation made safe to use again: a big round
 *            pupil under that brow reads as a kitten concentrating, where
 *            the slit pupil it originally carried read as a predator. The
 *            brow keeps its full DEPTH and its angle is eased to 0.20 --
 *            depth is the effort, angle is the threat.
 *   wide   pupils DILATE. Owner's correction, 2026-08-10, and it is a
 *          fact about cats: a hunting pupil opens, it does not narrow --
 *          narrowing is a bright-light squint. This take is therefore
 *          1c's aperture and increased tilt (the tilt is what gave the
 *          original focused face its charm) with a blown round pupil
 *          instead of a slit. Two things fall out of it for free: a
 *          dilated pupil is ROUND, so the reptilian look that dogged the
 *          slit is gone by construction; and it is the largest, darkest
 *          mark the eye can make, which is exactly what survives at
 *          31px. Cute and lethal turn out to be the same drawing.
 *   cheek    the mischief take. Ferocity from the lower lid, eye
 *            near-round. Kept as the gentlest option on the shelf.
 *   intense  the first take, revisited: ferocity from a lowered brow
 *            angled toward the nose, which dilation makes readable as
 *            concentration rather than as threat.
 *
 * Every take keeps the iris, the eye colour and the round-pupil resting
 * face intact, and none of them adds a drawing -- they are all the
 * ordinary eye with different dials, which is what makes them swappable
 * in one line and comparable in one lab.
 */
/* Mutable, like SWIM / POUNCE / EYE / RIG, and for the same reason: the
 * gallery dials these in place and the module reads them at call time. Frozen
 * (as this shipped) every slider on the hunting face is a silent no-op --
 * which is the exact failure the notes above warn about for the lid clamp,
 * where a dial that has stopped responding looks like a dial that needs more
 * turning. The inner takes stay frozen; only the table is writable. */
const FOCUS_VARIANTS = ({
  wide: Object.freeze({
    focusSquash: 0, // no narrowing whatsoever: this is not a squint
    focusWiden: 0,
    focusGrow: 0.24, // the eye itself opens, which is where the room comes from
    focusSpread: 0.1, // ...and the pair moves apart, so the two do not collide
    focusTilt: 0.24, // strong positive canthal tilt -- the original's charm
    focusLid: 0.05, // barely a brow
    focusLidTilt: -0.03, // tilted AWAY from the menace direction
    focusLidCurve: 0.06,
    focusLowerLid: 0.1, // a little cheek, to keep the intensity
    focusLowerTilt: -0.05,
    focusLowerCurve: -0.16,
    focusAsym: 0.28,
    focusPupilW: 1, // ROUND. A dilated pupil has no reason to be a slit.
    // A LOWER base than the resting eye's 0.78, which is what leaves the
    // dilation somewhere to go. The resting pupil is already at 0.78 of
    // its aperture and night takes it to 0.95, a hair under the ceiling --
    // so a hunting pupil built on that base clamps in three themes out of
    // four and the hour stops meaning anything. On 0.63, every hour lands
    // clear of the ceiling and night is visibly wider than day. Paired
    // with focusGrow's bigger aperture, the absolute pupil still comes out
    // larger than a resting night pupil, which is the ask.
    focusPupilBase: 0.63,
    // Dilation, composed with the hour rather than replacing it -- see the
    // pupil sizing below for how the two combine.
    focusDilate: 1.12,
    limbal: 0.7,
  }),

  // The very first take, revisited 2026-08-10 at the owner's suggestion.
  //
  // Its character was the lowered brow angled toward the nose -- the real
  // threat signal -- and it was rejected as too evil. The reptilian half
  // of that verdict belonged to the slit pupil, and dilation has since
  // solved it: a big round pupil under a lowered brow is a kitten
  // CONCENTRATING, where a slit under the same brow was a predator. So
  // the brow comes back at nearly full strength and the pupil carries the
  // cuteness. Squash is well down from the original 0.3, because a
  // narrowed eye and a blown pupil cannot both fit in one aperture.
  intense: Object.freeze({
    // Squash nearly off and the aperture grown hard (2026-08-10): both
    // buy the pupil ABSOLUTE size without raising its share of the eye,
    // which is the only way to get a bigger pupil that does not also
    // eat the iris. The share stays clear of the ceiling, so the hour
    // still moves it.
    focusSquash: 0.06,
    focusWiden: 0.02,
    // Grown a little harder than 2a, and on a higher base, so that this
    // take's pupil comes out the same ABSOLUTE size as 2a's -- otherwise
    // the two are not a fair comparison and 2b loses on a detail nobody
    // chose. The brow covers the top of the eye, so the room has to come
    // from the aperture rather than from the share.
    focusGrow: 0.34,
    focusSpread: 0.14,
    focusTilt: 0.2,
    focusLid: 0.3, // a real brow, unlike 2a's hint of one -- clamped off the pupil
    // 0.20, owner-picked 2026-08-10 from a side-by-side against 0.24.
    // Down from the 0.34 of the original take, which read as evil: the
    // angle is the menace and the DEPTH is the concentration, so easing
    // the angle while keeping the depth is what makes this a kitten
    // frowning in effort rather than a cat about to do harm.
    focusLidTilt: 0.18, // owner-dialled 2026-08-10, from 0.2
    focusLidCurve: 0.04,
    focusLowerLid: 0.1,
    focusLowerTilt: -0.05,
    focusLowerCurve: -0.14,
    focusAsym: 0.26,
    focusPupilW: 1,
    focusPupilBase: 0.64,
    focusDilate: 1.12,
    limbal: 0.72,
  }),

  // The shipped take: whatever EYE already says.
  cheek: Object.freeze({}),



});

/** Mix two hexes, `t` of the way from a to b. `shadeHex` multiplies and
 * `lightenHex` mixes toward white; neither can walk one colour toward
 * another, which is what a limbal ring is. */
function mixHex(a, b, t) {
  const na = parseInt(a.slice(1), 16);
  const nb = parseInt(b.slice(1), 16);
  const ch = (sh) => {
    const x = (na >> sh) & 255;
    const y = (nb >> sh) & 255;
    return Math.round(x + (y - x) * t);
  };
  return `#${((ch(16) << 16) | (ch(8) << 8) | ch(0)).toString(16).padStart(6, '0')}`;
}

/** CIE L*, 0..100. The house unit for "can the eye tell these apart", set
 * during the pond restyle: sRGB channel values are gamma-encoded, so their
 * arithmetic difference is not a perceived one, and a fixed mix ratio buys
 * far less separation at the light end than at the dark. */
function lstar(hex) {
  const n = parseInt(hex.slice(1), 16);
  const lin = (v) => {
    const c = v / 255;
    return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
  };
  const y =
    0.2126 * lin((n >> 16) & 255) + 0.7152 * lin((n >> 8) & 255) + 0.0722 * lin(n & 255);
  return y > 0.008856 ? 116 * y ** (1 / 3) - 16 : 903.3 * y;
}

/**
 * The one ink for a belly, the way `noseInkOf` is the one ink for a nose.
 *
 * A belly is PALER than the back on most cats, which is why this was a
 * lighten -- but a lighten is a claim about headroom, and a near-white coat
 * has none. Measured on the shipped palettes: 26.2 L* of separation on the
 * tuxedo, 9.9 on storm, and 1.4 on 'cloud', which is Clementine. At 1.4 the
 * belly is not faint, it is absent.
 *
 * So the rule is stated as the thing being judged -- how far the belly must
 * sit from the coat -- and the DIRECTION follows the room available. Where
 * lightening reaches `minSeparation` nothing changes, which is every cat
 * that shipped before this. Where it cannot, the belly goes the other way,
 * toward the coat's own shade: a white cat's underside reads as shadow
 * rather than as a paler patch, which is what it is on a real one.
 */
function bellyInkOf(appearance) {
  const lit = lightenHex(appearance.furBase, BELLY.lighten);
  if (lstar(lit) - lstar(appearance.furBase) >= BELLY.minSeparation) return lit;
  return mixHex(appearance.furBase, appearance.furShade, BELLY.darken);
}

/** Memoized per palette entry and theme. Keyed on the THEME rather than
 * on the shade factor since 2026-08-10: two themes with equal factors
 * would have shared an entry and therefore a pupil, which is a bug that
 * would only appear the day someone re-tuned a factor. */
const SHADED_APPEARANCES = new Map();

/**
 * A damp coat (2026-08-10).
 *
 * Wet fur is darker, a little less saturated, and its shading collapses
 * toward the base as the hairs clump -- which is why a wet cat reads as
 * flatter as well as darker. `wet` is 0..1.
 *
 * This exists so that leaving the water has a cue that is a fact about
 * the CAT rather than about the place. The bug it answers: every water
 * cue used to ride one 260ms fade keyed on the tile, so for a quarter
 * second after the shoreline a cat on grass was still being clipped at a
 * waterline and still missing its ground shadow -- water geometry, drawn
 * on land. Submersion is a PLACE and wetness is a MEMORY; they need
 * opposite timing, so they cannot be the same signal. Geometry now comes
 * from position and only the COLOUR lingers.
 *
 * Not cached: it is three colour ops on a continuous input, so a cache
 * keyed on `wet` would grow without ever hitting.
 */
function wetAppearanceOf(appearance, wet) {
  if (!(wet > 0.01)) return appearance;
  const w = wet > 1 ? 1 : wet;
  const damp = shadeHex(appearance.furBase, 1 - 0.22 * w);
  return {
    ...appearance,
    furBase: damp,
    // The shade walks toward the (already darkened) base rather than
    // darkening on its own: clumped fur loses its soft gradient, and
    // shading them independently would keep a dry cat's contrast.
    furShade: mixHex(shadeHex(appearance.furShade, 1 - 0.12 * w), damp, 0.35 * w),
  };
}

function shadedAppearanceOf(appearance, theme) {
  const factor = FUR_SHADE_BY_THEME[theme] ?? 1;
  const dilate = PUPIL_DILATE_BY_THEME[theme] ?? 1;
  if (factor === 1 && dilate === 1) return appearance;
  let byTheme = SHADED_APPEARANCES.get(appearance);
  if (!byTheme) {
    byTheme = new Map();
    SHADED_APPEARANCES.set(appearance, byTheme);
  }
  let shaded = byTheme.get(theme);
  if (!shaded) {
    const p = appearance.pattern;
    shaded = {
      ...appearance,
      furBase: shadeHex(appearance.furBase, factor),
      furShade: shadeHex(appearance.furShade, factor),
      noseColor: shadeHex(appearance.noseColor, factor),
      pupilDilate: dilate,
      pattern: p && {
        ...p,
        ...(p.color ? { color: shadeHex(p.color, factor) } : {}),
        ...(p.color2 ? { color2: shadeHex(p.color2, factor) } : {}),
      },
    };
    byTheme.set(theme, shaded);
  }
  return shaded;
}

/**
 * Draws one cat.
 *
 * opts: {
 *   pose:       one of POSES                     (default 'idle')
 *   appearance: a PALETTES-shaped object         (required)
 *   facing:     'left' | 'right'                 (default 'left')
 *   size:       box edge in px                   (required)
 *   phase:      0..1 local animation phase       (default 0; poses may ignore)
 *   x, y:       top-left of the box in ctx space (default 0, 0)
 *   eyesOverride: force an eye state ('open'|'closed'|'half'|'focused') --
 *                 blinks (US4) and expressions (US5) land through here
 *   earsBack:   force the ears back briefly (ear twitch, sad beat)
 *   lid:        0..1 partial-blink lid over open eyes (v2) -- 1 lands on
 *               the same happy arcs as 'closed', so eased blinks work
 * }
 */
function drawCat(ctx, opts) {
  const {
    pose = 'idle',
    appearance,
    facing = 'left',
    size,
    phase = 0,
    x = 0,
    y = 0,
    eyesOverride,
    earsBack,
  } = opts;

  const L = applyRig(catLayout(pose, phase, opts.layout), opts.rig);
  if (eyesOverride) {
    L.eyes = eyesOverride;
  }
  if (earsBack) {
    L.earsUpright = false;
    L.earsBackAmt = 1;
  }
  paintBox(ctx, L, appearance, { facing, size, x, y, lid: opts.lid, turn: opts.turn });
}

/** The shared box pipeline: mirror, scale, paint. drawCat and
 * drawCatTween meet here so a blended frame is drawn by exactly the
 * machinery a held pose uses. */
function paintBox(ctx, L, appearance, { facing, size, x, y, lid = 0, turn = null }) {
  // v2: `fine` gates only the tabby forehead stripes (sub-pixel noise when
  // small). Eyes, mouth and inner ears draw at every size -- v1's 44px
  // cliff meant no live-world cat ever wore its own face.
  const fine = size >= 44;
  // The served facing does not take effect until the mirror lands at the
  // bottom of the dip; before that the cat is still drawn the way it was
  // going. Both ends of the turn are therefore exactly the held drawings.
  const tr = turn == null ? null : turnTransform(turn);
  const dir = turnFacing(facing, turn);

  ctx.save();
  ctx.translate(x, y);
  if (dir === 'left') {
    // The base cat faces right; a left-facing cat is its mirror.
    ctx.translate(size, 0);
    ctx.scale(-1, 1);
  }
  ctx.scale(size, size);
  if (tr) {
    // A cat turns about its own footprint: the paws stay put and the
    // body swings round them. Anchoring anywhere else slides the cat
    // sideways through the turn, which reads as a stumble.
    ctx.translate(0.5, CAT_GROUND - tr.lift);
    ctx.scale(tr.sx, tr.sy);
    ctx.translate(-0.5, -CAT_GROUND);
  }
  ctx.lineJoin = 'round';
  ctx.lineCap = 'round';

  paintCat(ctx, L, appearance, fine, lid, size);
  ctx.restore();
}

/**
 * Pose-space blending: because every pose is a parameter set over the
 * same reference cat, a transition between poses is a lerp between their
 * layouts -- no frames, no assets. Discrete facts (eye state, ear set,
 * droplet, raised paw) switch at the midpoint; a leg with no counterpart
 * in the other pose shrinks away on its own half of the blend.
 */
function blendLayouts(A, B, t) {
  // Exact at both endpoints (float lerp lands t=1 a few ulps off B):
  // t=0 IS pose A and t=1 IS pose B, bit for bit.
  const n = t === 1 ? (a, b) => b : (a, b) => a + (b - a) * t;
  const legs = [];
  for (let i = 0; i < Math.max(A.legs.length, B.legs.length); i++) {
    const a = A.legs[i];
    const b = B.legs[i];
    if (a && b) {
      legs.push({
        x: n(a.x, b.x), top: n(a.top, b.top), bottom: n(a.bottom, b.bottom), w: n(a.w, b.w),
        hx: n(a.hx ?? a.x, b.hx ?? b.x),
        front: t >= 0.5 ? b.front : a.front,
        far: t >= 0.5 ? b.far : a.far,
      });
    } else if (a) {
      // Clamped both ways: an anticipating or overshooting blend hands us
      // a t a little outside [0,1], and an unclamped share would grow a
      // vanishing leg back instead of shrinking it.
      const w = a.w * rclamp(1 - 2 * t, 0, 1);
      if (w > 0.015) legs.push({ ...a, w });
    } else if (b) {
      const w = b.w * rclamp(2 * t - 1, 0, 1);
      if (w > 0.015) legs.push({ ...b, w });
    }
  }
  const late = t >= 0.5 ? B : A;
  return {
    body: {
      cx: n(A.body.cx, B.body.cx), cy: n(A.body.cy, B.body.cy),
      rx: n(A.body.rx, B.body.rx), ry: n(A.body.ry, B.body.ry),
      rot: n(A.body.rot || 0, B.body.rot || 0),
    },
    head: { cx: n(A.head.cx, B.head.cx), cy: n(A.head.cy, B.head.cy), r: n(A.head.r, B.head.r) },
    tail: {
      x0: n(A.tail.x0, B.tail.x0), y0: n(A.tail.y0, B.tail.y0),
      c1x: n(A.tail.c1x, B.tail.c1x), c1y: n(A.tail.c1y, B.tail.c1y),
      c2x: n(A.tail.c2x, B.tail.c2x), c2y: n(A.tail.c2y, B.tail.c2y),
      x1: n(A.tail.x1, B.tail.x1), y1: n(A.tail.y1, B.tail.y1),
    },
    legs,
    // Carried for completeness only: by the time a layout reaches here
    // `catLayout` has already derived `earsBackAmt` from it, and the
    // painter reads the boolean only as a fallback for when that is
    // missing -- which a blended layout never is. Dropping it changes no
    // drawing, which is why the check below it cannot see it.
    earsUpright: late.earsUpright,
    // Continuous, unlike `earsUpright`. Ears easing back through a pose
    // change is a MOTION; a boolean switching at the midpoint is not, and
    // the switch is what made every nap and every meal start with a
    // one-frame ear snap.
    earsBackAmt: n(
      A.earsBackAmt === undefined ? (A.earsUpright ? 0 : 1) : A.earsBackAmt,
      B.earsBackAmt === undefined ? (B.earsUpright ? 0 : 1) : B.earsBackAmt,
    ),
    eyes: late.eyes,
    droplet: late.droplet,
    pawUp: late.pawUp,
    // WHICH DRAWING this is. Switched at the midpoint like the other
    // un-blendable fields, though in practice both sides carry the same
    // one: render.js hands `layoutFrom` the very object it hands `layout`.
    //
    // Dropping it was invisible for a year and then unmistakable. A layout
    // with no `view` is not "no view" to paintCat, it is NOT BACK -- so
    // every pose blend on a north-facing cat drew a full face onto the
    // back of its skull for the length of the blend. Two things hid it:
    // the blend is 260ms, and until swim became axial (#199) a cat
    // entering water left the back view anyway, so the commonest blend of
    // all could not show it.
    view: late.view,
  };
}

/**
 * Draws one cat mid-transition. Same opts as drawCat, except `pose` is
 * replaced by { from, to, t } (plus per-pose phases). t=0 is exactly
 * drawCat(from), t=1 exactly drawCat(to).
 */
function drawCatTween(ctx, opts) {
  const {
    from, to, t,
    appearance, facing = 'left', size,
    phaseFrom = 0, phaseTo = 0,
    x = 0, y = 0, eyesOverride, earsBack, lid,
  } = opts;
  // Deliberately NOT clamped to [0,1]. Pose space is linear, so a t a
  // little outside it is a legal pose slightly beyond each end -- which
  // is precisely what anticipation and overshoot ARE. Bounded so that a
  // wild t can never turn a cat inside out.
  const L = applyRig(
    blendLayouts(
      catLayout(from, phaseFrom, opts.layoutFrom),
      catLayout(to, phaseTo, opts.layout),
      rclamp(t, -0.3, 1.3),
    ),
    opts.rig,
  );
  if (eyesOverride) {
    L.eyes = eyesOverride;
  }
  if (earsBack) {
    L.earsUpright = false;
    L.earsBackAmt = 1;
  }
  paintBox(ctx, L, appearance, { facing, size, x, y, lid, turn: opts.turn });
}

// ---------------------------------------------------------------------------
// Layouts: each pose is a parameter set, never a separate drawing routine.
// Unit space: x 0..1 rightward, y 0..1 downward; the ground sits near y 0.88.
// ---------------------------------------------------------------------------

const TAU = Math.PI * 2;

/** The cat's own ground line, in its unit box. render.js knows the same
 * number as CAT_GROUND_Y; the turn transform needs it here too. */
const CAT_GROUND = 0.88;

function catLayout(pose, phase, opts = {}) {
  const breathe = breathCurve(Math.sin(phase * TAU));

  // The idle standing cat is the reference; poses adjust it. v2: the head
  // grows ~1.05x for kawaii proportion, at v1's exact position -- only the
  // radius changes (owner-tuned: 1.2x -> 1.1x -> 1.05x, pull-ins zeroed, 2026-07-29),
  // so any silhouette difference is size alone. The body is deliberately
  // v1's: "rounder cat", never "different cat".
  const L = {
    body: { cx: 0.44, cy: 0.64, rx: 0.3, ry: 0.21, rot: 0 },
    head: { cx: 0.7, cy: 0.4, r: 0.226 },
    earsUpright: true, // false = flattened back a touch (naps, meals)
    earsBackAmt: 0, // ...and the same fact as a 0..1 the rig can ease
    // Tail as a cubic bezier from rump to tip, drawn as an outlined stroke.
    tail: { x0: 0.16, y0: 0.62, c1x: 0.02, c1y: 0.62, c2x: 0.0, c2y: 0.42, x1: 0.05, y1: 0.3 },
    legs: withFarPair([
      { x: 0.2, top: 0.74, bottom: 0.88, w: 0.1 },
      { x: 0.7, top: 0.74, bottom: 0.88, w: 0.1 },
    ]),
    eyes: 'open', // 'open' | 'closed' | 'half' | 'focused'
    droplet: false,
    pawUp: false,
  };
  // Set by any pose whose feet are clear of the ground; see liftLayout.
  let airborne = false;

  switch (pose) {
    case 'idle':
      L.body.ry += 0.008 * breathe; // soft breathing
      L.tail.x1 += 0.012 * breathe; // and an idly swaying tail tip
      break;

    case 'walking': {
      // `phase` is TILES COVERED, not time (see Presentation.strideFor),
      // so `cycles` is steps per tile of ground and may be fractional --
      // there is no tick boundary left for a part-stride to tear against.
      const cycle = phase * GAIT.cycles;

      // How much of this cat's travel is ACROSS the screen: 1 is a pure
      // east/west walk (the one that always looked cute), 0 is due north
      // or south.
      //
      // This is the fix for "walking north/south looks unnatural" (owner,
      // 2026-08-09), and the cause turns out to be arithmetic rather than
      // taste. `plantedReach` earns its planted foot by sweeping the paw
      // backward through exactly the ground the cat covers -- but that
      // sweep is always HORIZONTAL, and a cat walking north covers no
      // horizontal ground at all. Every foot was therefore skating at
      // 100% of stride, in every vertical step ever drawn, and no amount
      // of gait tuning could reach it: the walk was correct only for the
      // one axis it was derived on.
      //
      // The honest answer is foreshortening. As the walk turns toward the
      // camera the stride collapses, because there is no sideways ground
      // left to push against -- and what carries the walk instead is
      // DEPTH: the near and far pairs swing past each other, the body
      // rocks and narrows, and the whole cat rises and falls more. A cat
      // walking at you is mostly bob and shoulder; a cat walking across
      // you is mostly stride. It is now drawn that way, and the two blend
      // continuously, so a diagonal is a real mixture rather than a
      // choice between them.
      const travelH = opts.travelH === undefined ? 1 : rclamp(opts.travelH, 0, 1);
      const depth = 1 - travelH;

      L.body.rx = 0.32 * (1 - GAIT.depthNarrow * depth);
      const bob = GAIT.bob * (1 + GAIT.depthBob * depth);
      const bobOff = bob * Math.cos((cycle - GAIT.bobPhase) * GAIT.beats * TAU);
      L.body.cy += bobOff;
      // Weight rolls from one diagonal pair to the other. Stronger
      // head-on, where the roll is doing the work the lost stride used to.
      L.body.rot = GAIT.roll * (0.35 + 0.65 * depth) * Math.sin(cycle * TAU);
      L.body.cx += GAIT.surge * Math.sin(cycle * TAU * GAIT.surgeBeats);
      L.head.cx = 0.72;
      L.head.cy += GAIT.headLift * Math.sin((cycle - GAIT.headLag) * TAU);
      // Index 0 is the rear leg and index 1 the front, in every pose that
      // has them -- blendLayouts pairs legs BY INDEX, so swapping them
      // here would cross a cat's legs on the way to any other pose.
      // Half a cycle apart: one foot is planted while the other swings.
      // The pivot sits high INSIDE the body and never moves; only the foot
      // swings, so the limb angles like a leg instead of sliding like a peg.
      // Everything above the belly is hidden, so the limb getting longer at
      // the stride extremes costs nothing -- which is what lets the stance
      // foot stay honestly planted at y 0.88 while the swing foot arcs.
      const { hip: HIP, shoulder: SHOULDER } = GAIT;
      // The stride is the part that foreshortens away; the lift is the
      // part that grows to replace it. A cat coming at you picks its feet
      // UP, because that is the only component of the step still pointed
      // at the camera.
      const reach = GAIT.reach * travelH;
      const lift = GAIT.lift * (1 + GAIT.depthLift * depth);
      // Depth is said with the GROUND, not with sideways travel. The
      // first cut moved the two pairs apart horizontally, which pushed
      // feet clear of the body -- and a leg that clears the body shows
      // its entire length. A foot that is further away belongs HIGHER on
      // the ground plane instead, and a little thinner: that is where
      // depth actually lives, and neither ever leaves the body's cover.
      const groundSwing = GAIT.depthGround * depth * Math.sin(cycle * TAU);
      const swing = GAIT.depthSwing * depth * Math.sin(cycle * TAU);
      const leg = (base, u, far) => {
        const g = gaitStep(((u % 1) + 1) % 1, GAIT.duty);
        const side = far ? -1 : 1;
        return {
          hx: base,
          x: base + reach * g.x + side * swing,
          top: GAIT.pivot,
          bottom: CAT_GROUND - lift * g.lift + side * groundSwing,
          w: 0.095 * (far ? 1 - GAIT.depthTaper * depth : 1),
        };
      };
      // The four-beat lateral walk off the owner's footfall chart: left
      // hind, left fore, right hind, right fore, each a quarter cycle
      // apart. Far pair first so it draws behind. Index order is fixed --
      // blendLayouts pairs legs BY INDEX.
      //
      // All of it costs exactly nothing at travelH 1 -- every depth term
      // is multiplied by `depth` -- so the east/west walk the owner
      // already likes is untouched, byte for byte.
      L.legs = [
        { ...leg(HIP, cycle - 0.5, true), far: true },       // right hind
        { ...leg(SHOULDER, cycle - 0.75, true), far: true }, // right fore
        leg(HIP, cycle, false),                              // left hind
        leg(SHOULDER, cycle - 0.25, false),                  // left fore
      ].map((l, i) =>
        i < 2 ? { ...l, x: l.x + GAIT.spread, hx: l.hx + GAIT.spread } : l,
      );
      // Tail streams behind, gently lifted. The rig's drag does the rest,
      // which is why this no longer needs a sway of its own.
      L.tail = { x0: 0.14, y0: 0.58, c1x: 0.04, c1y: 0.56, c2x: 0.0, c2y: 0.5, x1: 0.03, y1: 0.42 };
      break;
    }

    case 'pouncing': {
      // Anticipation crouch, then the leap: squash before stretch. The
      // static pose (phase 0, reduced motion) is the loaded crouch.
      //
      // The two positions are unchanged -- what used to be a switch at
      // phase 0.45 is now a launch BETWEEN them. Held loaded for
      // POUNCE.hold, extended over POUNCE.launch, then held out. Both
      // ends are reached exactly, so the crouch and the leap are the same
      // drawings they have always been; only the frames between them are
      // new, and there used to be none.
      const t = pounceLaunch(phase);
      // opts.beatMs is the served tick length, so the wiggle keeps its
      // real-world speed whatever config.world.tick_ms says.
      // `opts.wiggleHz` lets a caller off the served tick pick its own rock
      // rate without moving the world's. The card portrait needs it: its
      // beat is 4x longer, so the SAME Hz that reads as one deliberate rock
      // in 192ms becomes a slow wallow in 768ms.
      const wig = pounceWiggle(
        phase,
        opts.wiggleHz ? { ...POUNCE, wiggleHz: opts.wiggleHz } : POUNCE,
        opts.beatMs,
      );
      // The lateral tread, a quarter-cycle behind the vertical rock. `wig`
      // is the rock; `sway` is where that rock is in its own cycle a beat
      // earlier, which is what puts the two 90 degrees apart.
      const sway = pounceWiggleSway(phase, opts.wiggleHz
        ? { ...POUNCE, wiggleHz: opts.wiggleHz } : POUNCE, opts.beatMs);
      // Keep the chest (cx + rx) fixed and take the width off the back.
      // `opts.sway` is the same escape hatch as `opts.wiggleHz`: the depth
      // of the tread that reads at a 47px portrait is a whisper at a 31px
      // map cat, so the two pick their own rather than sharing one.
      const swayK = (opts.sway ?? POUNCE.wiggleSway) * sway;
      const crouch = {
        ...L,
        body: {
          cx: 0.42 + 0.31 * swayK,
          cy: 0.68 + POUNCE.wiggleAmp * wig,
          rx: 0.31 * (1 - swayK),
          ry: 0.17,
          // MINUS, not plus (2026-08-10). The rock is a `cy` shift plus a
          // rotation about the body's centre, so the two ADD at one end of
          // the ellipse and CANCEL at the other -- and with the signs
          // agreeing they added at the CHEST. Measured, the front travelled
          // 1.97px against the hindquarters' 0.07px: a 27:1 ratio, on a pose
          // whose own comment says it "treads its hind feet and rocks its
          // hindquarters". Opposed, the cancellation lands on the chest
          // instead, which is what plants the front while the butt wiggles --
          // and a planted front is most of why the pose reads as aiming.
          rot: -0.1 - POUNCE.wiggleRot * wig,
        },
        head: { cx: 0.68, cy: 0.5, r: 0.221 },
        legs: withFarPair([
          { x: 0.2, top: 0.78, bottom: 0.88, w: 0.1 },
          { x: 0.64, top: 0.78, bottom: 0.88, w: 0.1 },
        ], FAR_LEGS.pounce),
        // Tail high and twitching with intent.
        tail: {
          x0: 0.14, y0: 0.6, c1x: 0.03, c1y: 0.5, c2x: 0.0, c2y: 0.32,
          x1: 0.06 + POUNCE.twitch * Math.sin(phase * 2 * TAU), y1: 0.24,
        },
      };
      const leapLegs = withFarPair([
        { x: 0.22, top: 0.66, bottom: 0.84, w: 0.09 },
        // Drawn in FRONT of the body. Legs otherwise go behind it now,
        // and the leap's body covers y 0.47..0.65 at this x -- which
        // would bury all but 1.6px of the reach, gutting the one frame
        // the owner singled out as worth protecting. Grooming's raised
        // paw has always been a front element for the same reason.
        { x: 0.74, top: 0.5, bottom: 0.68, w: 0.09, front: true }, // forepaw reaching
      ], FAR_LEGS.pounce);
      // The far pair belongs behind the body whatever the near one does:
      // a shaded copy drawn in front would read as a second cat's paw.
      leapLegs.forEach((leg, i) => {
        if (i < 2) leg.front = false;
      });
      const leap = {
        ...L,
        body: { cx: 0.46, cy: 0.56, rx: 0.34, ry: 0.165, rot: -0.18 },
        head: { cx: 0.78, cy: 0.34, r: 0.215 },
        legs: leapLegs,
        tail: { x0: 0.14, y0: 0.6, c1x: 0.02, c1y: 0.6, c2x: 0.0, c2y: 0.46, x1: 0.04, y1: 0.38 },
      };
      // Touchdown: the forelegs take the weight, the body compresses over
      // them, the rump is still coming down. This is the frame the old
      // pounce had nowhere to put -- it extended and then HELD full reach
      // until the tick ended, so every pounce finished frozen at the top
      // of the leap and the next pose had to blend out of a cat in mid-air.
      const land = {
        ...L,
        body: { cx: 0.47, cy: 0.715, rx: 0.335, ry: 0.15, rot: 0.07 },
        head: { cx: 0.76, cy: 0.575, r: 0.219 },
        legs: withFarPair([
          { x: 0.26, hx: 0.24, top: 0.72, bottom: CAT_GROUND, w: 0.1 },
          { x: 0.72, hx: 0.68, top: 0.7, bottom: CAT_GROUND, w: 0.095 },
        ], FAR_LEGS.pounce),
        tail: { x0: 0.16, y0: 0.64, c1x: 0.04, c1y: 0.68, c2x: 0.0, c2y: 0.54, x1: 0.04, y1: 0.44 },
      };

      const launchEnd = POUNCE.hold + POUNCE.launch;
      const landEnd = launchEnd + POUNCE.land;
      let blended;
      if (phase < launchEnd) {
        blended = blendLayouts(crouch, leap, t);
        // Feet leave the ground the moment the launch starts: past t=0
        // they are positioned against the BODY, not the ground, so they
        // have to travel with it. Only the loaded crouch is planted.
        airborne = t > 0;
      } else if (phase < landEnd) {
        blended = blendLayouts(leap, land, smooth01((phase - launchEnd) / POUNCE.land));
        airborne = false;
      } else {
        // ...and back up to a ready crouch. The recovery is the slowest
        // part of the beat on purpose: a cat that snaps upright the
        // instant it lands has no weight in it.
        blended = blendLayouts(
          land,
          crouch,
          smooth01((phase - landEnd) / Math.max(1e-6, 1 - landEnd)),
        );
        airborne = false;
      }
      L.body = blended.body;
      L.head = blended.head;
      L.tail = blended.tail;
      L.legs = blended.legs;
      break;
    }

    case 'eating': {
      L.body.rot = 0.07; // leaning into the bowl
      L.head = { cx: 0.71, cy: 0.6 + 0.012 * Math.sin(phase * 2 * TAU), r: 0.21 };
      L.earsUpright = false;
      L.eyes = 'closed'; // happy chomping
      L.tail = { x0: 0.15, y0: 0.66, c1x: 0.05, c1y: 0.68, c2x: 0.02, c2y: 0.6, x1: 0.03, y1: 0.55 };
      L.legs = withFarPair([
        { x: 0.2, top: 0.76, bottom: 0.88, w: 0.1 },
        { x: 0.66, top: 0.76, bottom: 0.88, w: 0.1 },
      ]);
      break;
    }

    case 'drinking': {
      L.body.rot = 0.05;
      L.head = { cx: 0.72, cy: 0.57 + 0.008 * Math.sin(phase * 3 * TAU), r: 0.21 };
      L.earsUpright = false;
      L.eyes = 'half';
      L.droplet = true; // the little lap of water that says "drinking"
      L.tail = { x0: 0.15, y0: 0.66, c1x: 0.05, c1y: 0.68, c2x: 0.02, c2y: 0.6, x1: 0.03, y1: 0.55 };
      L.legs = withFarPair([
        { x: 0.2, top: 0.76, bottom: 0.88, w: 0.1 },
        { x: 0.66, top: 0.76, bottom: 0.88, w: 0.1 },
      ]);
      break;
    }

    case 'grooming': {
      // Head swung back toward the flank, one paw raised mid-lick; the
      // head nods with each lick.
      L.body = { cx: 0.48, cy: 0.64, rx: 0.3, ry: 0.21, rot: 0 };
      L.head = { cx: 0.54, cy: 0.42 + 0.012 * Math.sin(phase * 3 * TAU), r: 0.215 };
      L.eyes = 'closed';
      L.pawUp = true;
      L.legs = withFarPair([{ x: 0.26, top: 0.76, bottom: 0.88, w: 0.1 }]);
      L.tail = { x0: 0.16, y0: 0.62, c1x: 0.03, c1y: 0.6, c2x: 0.01, c2y: 0.44, x1: 0.06, y1: 0.34 };
      break;
    }

    case 'loaf': {
      L.body = { cx: 0.46, cy: 0.68, rx: 0.34, ry: 0.185 + 0.006 * breathe, rot: 0 };
      L.head = { cx: 0.68, cy: 0.48, r: 0.21 };
      L.eyes = 'half'; // contentedly elsewhere
      L.legs = []; // all paws folded away: the defining loaf fact
      // Tail wrapped along the front of the loaf.
      L.tail = { x0: 0.16, y0: 0.76, c1x: 0.3, c1y: 0.9, c2x: 0.56, c2y: 0.9, x1: 0.68, y1: 0.82 };
      break;
    }

    case 'sleep-curl': {
      const slow = breathCurve(Math.sin(phase * TAU * 0.5)); // slower breath in sleep
      L.body = { cx: 0.5, cy: 0.64, rx: 0.3, ry: 0.25 + 0.008 * slow, rot: 0 };
      L.head = { cx: SLEEP.headX, cy: SLEEP.headY, r: SLEEP.headR };
      L.earsUpright = false;
      L.eyes = 'closed';
      L.legs = [];
      // Tail curled right around to the nose.
      L.tail = { x0: 0.24, y0: 0.82, c1x: 0.4, c1y: 0.94, c2x: 0.66, c2y: 0.92, x1: 0.78, y1: 0.76 };
      break;
    }

    case 'swim': {
      // The wading kitty (spec 010's parked pose): a low flat float, head
      // and ears dry, legs paddling out of sight below the surface (none
      // drawn -- blends shrink them away on the way in). Paddling reads
      // as a gentle bob plus a slow body rock. Every number lives in SWIM
      // for the lab.
      //
      // No splash droplet (owner, 2026-08-04): at 0.028 x 0.04 of a tile
      // it is a ~2px smudge at any size this world draws at, so it read
      // as clutter rather than water. Being in water is said by the
      // ripple and the lost shadow, which are the renderer's job and
      // scale with the tile.
      const bob = SWIM.bob * Math.sin(phase * TAU);
      const rock = SWIM.rock * Math.sin(phase * TAU * 2);
      L.body = { cx: 0.44, cy: SWIM.bodyY + bob, rx: 0.3, ry: SWIM.bodyRy, rot: rock };
      L.head = { cx: 0.7, cy: SWIM.headY + bob, r: 0.226 };
      L.legs = [];
      // The tail, trailing at `tailUpright` 0 and HELD UP at 1.
      //
      // The first cut of this only straightened the trail -- it pulled the
      // x extent toward the base and left the tip at `tailLift`. That
      // makes a stub, not an upright tail, because a trailing tail gets
      // nearly all its LENGTH from the horizontal run: tailLift 0.6 is a
      // bare 0.08 above the body. Straightening it threw the length away.
      //
      // So the upright end is authored as its own curve, and it rises to
      // AXIAL_SWIM.tailTopY -- the SAME height the end-on views use, on
      // purpose. A cat wading north, east and south is one animal, and
      // three tail heights that have to be kept in agreement by eye will
      // drift apart the first time one of them is re-dialled. One value,
      // three views. (Same argument as the world's single water level.)
      // The raised end keeps the trailing tail's HORIZONTAL place and
      // changes only its height. Standing it up over the rump instead put
      // the tip at x 0.12 against a body edge at x 0.11 -- inside the
      // silhouette, painted behind the body, so all that showed was a 3px
      // nub above the back. ("The side tail upright doesn't seem to work",
      // owner, and it did not.) It is the same rule the toward-facing
      // axial view already carries: a tail inside the body's own edge is
      // not a tail, it is a hidden line. A real cat's tail leaves the rump,
      // sweeps ASTERN, and then rises -- which is both correct and visible.
      const up = SWIM.tailUpright;
      const baseY = SWIM.bodyY + bob;
      // The shared height, plus the side view's declared foreshortening
      // allowance -- see SWIM.tailUprightRise.
      const top = AXIAL_SWIM.tailTopY - SWIM.tailUprightRise + bob;
      const mix = (trail, upright) => trail + (upright - trail) * up;
      L.tail = {
        x0: 0.16, y0: baseY,
        // Out and back along the water, or back and then up.
        c1x: mix(0.04, 0.10), c1y: mix(SWIM.bodyY - 0.05, baseY - 0.04),
        c2x: mix(0.0, 0.03), c2y: mix(SWIM.tailLift + 0.08, top + 0.13),
        x1: 0.05, y1: mix(SWIM.tailLift, top),
      };
      break;
    }

    case 'sit': {
      // Sitting is what a cat does when it has decided to STAY somewhere.
      // Rump down and back, chest up and forward, forelegs straight, tail
      // curled round the front paws. It reads at 31px because the
      // silhouette is unlike anything else in the vocabulary: tall and
      // narrow where idle is long and low.
      L.body = { cx: 0.42, cy: 0.665, rx: 0.275, ry: 0.215 + 0.007 * breathe, rot: -0.4 };
      L.head = { cx: 0.685, cy: 0.325, r: 0.226 };
      L.legs = withFarPair([
        { x: 0.27, hx: 0.31, top: 0.74, bottom: CAT_GROUND, w: 0.1 },
        { x: 0.66, hx: 0.63, top: 0.58, bottom: CAT_GROUND, w: 0.095 },
      ]);
      L.tail = { x0: 0.17, y0: 0.79, c1x: 0.34, c1y: 0.93, c2x: 0.62, c2y: 0.93, x1: 0.76, y1: 0.85 };
      break;
    }

    case 'stretch': {
      // The waking stretch. `phase` is the stretch's OWN 0..1: it reaches,
      // holds, and eases off, so the pose has a shape of its own rather
      // than being a position the blend happens to arrive at. The pose
      // tween still handles the edges, so this only has to be the middle.
      const push = smooth01(phase / 0.3) * (1 - smooth01((phase - 0.72) / 0.28));
      const k = (rest, full) => rest + (full - rest) * push;
      L.body = {
        cx: k(0.44, 0.47),
        cy: k(0.64, 0.625),
        rx: k(0.3, 0.345),
        ry: k(0.21, 0.155),
        rot: k(0, 0.3),
      };
      L.head = { cx: k(0.7, 0.775), cy: k(0.4, 0.655), r: 0.219 };
      L.eyes = push > 0.4 ? 'closed' : 'half';
      L.earsBackAmt = push * 0.55;
      // The far pair comes into view as the cat extends: at rest it hides
      // behind the near one exactly as it does in every other pose, and it
      // slides out only as the stretch pushes. So the depth cue arrives
      // with the reach rather than sitting there through the whole pose.
      L.legs = withFarPair([
        { x: k(0.2, 0.215), hx: k(0.2, 0.245), top: k(0.74, 0.6), bottom: CAT_GROUND, w: 0.1 },
        { x: k(0.7, 0.9), hx: k(0.7, 0.715), top: k(0.74, 0.7), bottom: k(CAT_GROUND, 0.86), w: 0.095 },
      ], FAR_LEGS.stretch * push);
      L.tail = {
        x0: k(0.16, 0.14), y0: k(0.62, 0.6),
        c1x: k(0.02, 0.0), c1y: k(0.62, 0.44),
        c2x: k(0.0, 0.05), c2y: k(0.42, 0.22),
        x1: k(0.05, 0.17), y1: k(0.3, 0.15),
      };
      break;
    }

    default:
      break;
  }

  // Shape first, then stand height: proportion holds the belly floor and
  // lift moves it, so running them the other way round would have lift's
  // rise silently undone by proportion's floor-restoring step.
  // The axial views overwrite the finished layout rather than branching
  // inside the switch, so a pose with no axial authoring keeps its side
  // drawing instead of vanishing.
  const view = opts.view || 'side';
  L.view = 'side';
  if (view !== 'side' && AXIAL_POSES.has(pose)) applyAxial(L, pose, phase, view, opts);

  // Poses still speak in the boolean; the continuous value is derived so
  // no pose had to be rewritten to gain an eased ear.
  if (!L.earsUpright) L.earsBackAmt = 1;
  return liftLayout(proportionLayout(L, airborne), airborne);
}

// ---------------------------------------------------------------------------
// Painting. Order matters: tail, body (+body pattern), legs, ears, head
// (+head pattern), face, extras -- so overlaps read like a cat.
// ---------------------------------------------------------------------------

const OUTLINE_W = 0.035;
const WATER_DROPLET = '#9ccfe6'; // matches the world's water rim

function paintCat(ctx, L, a, fine, lid = 0, size = 31) {
  const p = a.pattern || { kind: 'solid' };

  // Paint order IS the depth order, and for a cat walking away it inverts:
  // the head is the furthest part of it and the tail the nearest. Drawing
  // them in the side view's order put the head on top of the body and the
  // tail underneath it -- which reads as a cat facing you with its face
  // missing, because those two are the only depth cues the view has.
  const rear = L.view === 'back';
  const earsBack = L.earsBackAmt === undefined ? (L.earsUpright ? 0 : 1) : L.earsBackAmt;
  const paintHead = () => {
    drawEars(ctx, L.head, a, p, earsBack, L.earNear || 0, L.earFar || 0);
    // The pink is part of the EAR, so it is painted with the ear and the
    // head then covers its base -- which is why it needs no rule of its
    // own about where the skull begins.
    if (!rear) drawInnerEars(ctx, L.head, a, earsBack, L.earNear || 0, L.earFar || 0);
    drawHead(ctx, L.head, a, p, fine, L.view);
    // A cat walking away has the BACKS of its ears toward you and no face
    // at all. Skipping both is the rest of the back view's difference, and
    // it is what makes the view read instantly: a faceless head is
    // unmistakable even at 31px.
    if (!rear) {
      drawFace(ctx, L.head, L.eyes, a, lid, L.gaze, L.yawn || 0, L.view, size);
    }
  };

  // Furthest first.
  if (rear) paintHead();
  else drawTail(ctx, L.tail, a, p);
  // Legs go UNDER the body (owner's idea, 2026-08-08): a limb pivots from
  // high inside the body and only the part below the silhouette is seen,
  // so the visible paw is small while its MOTION is a long lever's. The
  // body doing the hiding means no clip and no new geometry -- just this
  // order. It also hides changes in limb LENGTH, which is what lets a
  // stance foot stay planted on the ground while a swinging one arcs.
  drawLegs(ctx, L.legs.filter((l) => !l.front), a, p);
  drawBody(ctx, L.body, a, p, L.view);
  drawLegs(ctx, L.legs.filter((l) => l.front), a, p);
  // ...and nearest last.
  if (rear) drawTail(ctx, L.tail, a, p);
  else paintHead();
  if (L.pawUp) drawRaisedPaw(ctx, L.head, a);
  if (L.droplet) drawDroplet(ctx, L.head);
}

function drawTail(ctx, t, a, p) {
  const color = p.kind === 'point-mask' ? p.color : a.furBase;
  const path = () => {
    ctx.beginPath();
    ctx.moveTo(t.x0, t.y0);
    ctx.bezierCurveTo(t.c1x, t.c1y, t.c2x, t.c2y, t.x1, t.y1);
  };
  path();
  ctx.strokeStyle = a.furShade;
  ctx.lineWidth = 0.085;
  ctx.stroke();
  path();
  ctx.strokeStyle = color;
  ctx.lineWidth = 0.085 - OUTLINE_W * 1.6;
  ctx.stroke();
}

function bodyPath(ctx, b) {
  ctx.beginPath();
  ctx.ellipse(b.cx, b.cy, b.rx, b.ry, b.rot || 0, 0, TAU);
}

function drawBody(ctx, b, a, p, view = 'side') {
  // Everything below reads `view`; `rear` is the one that suppresses
  // markings that only exist on a cat's front.
  const rear = view === 'back';
  bodyPath(ctx, b);
  ctx.fillStyle = a.furBase;
  ctx.fill();

  // The belly is painted BEFORE the outline, in a clip of its own. A stroke
  // straddles its path, so half the body's outline lies INSIDE the clip --
  // drawn after, the belly paints over that inner half and the body's own
  // line goes thin and pale exactly where the belly meets it. Skipped for
  // the tuxedo, whose bib IS its belly and sits lower and paler; drawing
  // both leaves the belly poking out behind the bib.
  if (p.kind !== 'tuxedo-mask') {
    const rot = b.rot || 0;
    const cos = Math.cos(rot);
    const sin = Math.sin(rot);
    // The offset is expressed along the body's own axes, so it has to turn
    // with the body -- otherwise the belly slides out of the crouch.
    // A cat walking away shows its BACK, and a back has no pale belly. The
    // patch is a chest marking seen from the front and a nonsense from
    // behind -- it was the last thing making the rear view read as a
    // frontal cat with its face missing.
    const ox = view === 'side' ? BELLY.x * b.rx : 0;
    const oy = BELLY.y * b.ry * (view === 'front' ? 0.72 : 1);
    ctx.save();
    bodyPath(ctx, b);
    ctx.clip();
    ctx.globalAlpha = rear ? 0 : BELLY.alpha;
    ctx.fillStyle = bellyInkOf(a);
    ctx.beginPath();
    ctx.ellipse(
      b.cx + ox * cos - oy * sin,
      b.cy + ox * sin + oy * cos,
      b.rx * BELLY.rx,
      b.ry * BELLY.ry,
      rot,
      0,
      TAU,
    );
    ctx.fill();
    ctx.restore();
  }

  // Re-lay the body path before stroking it. `restore()` puts back the
  // clip and the alpha but NOT the current path, so without this the
  // outline is struck on whatever the belly last drew -- which is the
  // belly ellipse, and it looks convincingly deliberate.
  bodyPath(ctx, b);
  ctx.strokeStyle = a.furShade;
  ctx.lineWidth = OUTLINE_W;
  ctx.stroke();

  // Body-side pattern work, clipped so it can never spill off the fur.
  ctx.save();
  bodyPath(ctx, b);
  ctx.clip();
  if (p.kind === 'tabby-stripes') {
    ctx.fillStyle = p.color;
    // No body stripes head-on or from behind (owner, 2026-08-10).
    //
    // A tabby's bands run AROUND the barrel, so seen end-on they project
    // to rings hugging the body outline -- not to anything a viewer reads
    // as fur. Two tries confirmed it: the side bars became neck
    // striations, and the honest quarter-turn became horizontal bands
    // across the chest. There is no third orientation to try, because the
    // problem is not the angle: a band around a cylinder seen down its own
    // axis has no legible projection at 31px.
    //
    // Which turns out to match the animal. A tabby seen head-on wears its
    // markings on the FACE and the legs, not the chest -- and the forehead
    // stripes are still drawn (see drawHead), so the front view keeps the
    // most recognisable tabby marking there is.
    if (view === 'side') {
      for (const s of [-0.45, 0, 0.45]) {
        ctx.beginPath();
        ctx.ellipse(
          b.cx + s * b.rx, b.cy - b.ry * 0.55,
          b.rx * 0.075, b.ry * 0.62, s * 0.25, 0, TAU,
        );
        ctx.fill();
      }
    }
  } else if (p.kind === 'patches') {
    ctx.fillStyle = p.color;
    ctx.beginPath();
    ctx.ellipse(b.cx - b.rx * 0.4, b.cy - b.ry * 0.35, b.rx * 0.42, b.ry * 0.55, -0.3, 0, TAU);
    ctx.fill();
    ctx.fillStyle = p.color2 || p.color;
    ctx.beginPath();
    ctx.ellipse(b.cx + b.rx * 0.45, b.cy + b.ry * 0.3, b.rx * 0.34, b.ry * 0.5, 0.4, 0, TAU);
    ctx.fill();
  } else if (p.kind === 'tuxedo-mask') {
    // The white bib down the chest and belly.
    ctx.fillStyle = p.color;
    ctx.beginPath();
    ctx.ellipse(b.cx + b.rx * 0.5, b.cy + b.ry * 0.42, b.rx * 0.52, b.ry * 0.75, 0.15, 0, TAU);
    ctx.fill();
  }
  ctx.restore();
}

function drawLegs(ctx, legs, a, p) {
  // A stroked segment from the pivot (hx, top) to the foot (x, bottom):
  // outline underneath, fur over it, round caps so the far end IS the paw.
  // `hx` defaults to x, which is the old vertical peg exactly.
  for (const leg of legs) {
    const hx = leg.hx ?? leg.x;
    const limb = () => {
      ctx.beginPath();
      ctx.moveTo(hx, leg.top);
      ctx.lineTo(leg.x, leg.bottom);
      ctx.stroke();
    };
    ctx.lineCap = 'round';
    ctx.strokeStyle = leg.far ? shadeHex(a.furShade, 0.85) : a.furShade;
    ctx.lineWidth = leg.w + OUTLINE_W;
    limb();
    ctx.strokeStyle = leg.far ? a.furShade : a.furBase;
    ctx.lineWidth = leg.w;
    limb();
    // Socked paws for the masked colorways: the last stretch before the toe.
    if (p.kind === 'tuxedo-mask' || p.kind === 'point-mask') {
      const at = 0.68;
      ctx.strokeStyle = p.color;
      ctx.lineWidth = leg.w;
      ctx.beginPath();
      ctx.moveTo(hx + (leg.x - hx) * at, leg.top + (leg.bottom - leg.top) * at);
      ctx.lineTo(leg.x, leg.bottom);
      ctx.stroke();
    }
  }
}

function earPoints(head, side, back, turn = 0) {
  // side: +1 toward the facing direction, -1 behind. Upright ears sit high;
  // "back" ears (eating, sleeping) flatten outward a touch.
  //
  // `back` is a 0..1 amount, not a flag. Ears easing back is a motion and
  // the boolean it replaces was a switch -- which is why every nap and
  // every meal used to open with a one-frame ear snap. `turn` swivels the
  // ear on its base: both ears the same way for a look, one alone for a
  // twitch. The base is fixed and only the apex travels, which is what an
  // ear actually does.
  const b = rclamp(back, 0, 1);
  const lerp = (lo, hi) => lo + (hi - lo) * b;
  const tiltOut = lerp(0.38, 0.22);
  const spread = lerp(0.5, 0.62);
  const reach = lerp(1.42, 1.28);
  const baseAngle = -Math.PI / 2 + side * spread;
  const bx = head.cx + Math.cos(baseAngle) * head.r * 0.92;
  const by = head.cy + Math.sin(baseAngle) * head.r * 0.92;
  const apexAngle = baseAngle + side * lerp(0.12, 0.3) + turn;
  const ax = head.cx + Math.cos(apexAngle) * head.r * reach;
  const ay = head.cy + Math.sin(apexAngle) * head.r * reach;
  const halfBase = head.r * tiltOut;
  const perp = baseAngle + Math.PI / 2;
  return {
    b1x: bx + Math.cos(perp) * halfBase,
    b1y: by + Math.sin(perp) * halfBase,
    b2x: bx - Math.cos(perp) * halfBase,
    b2y: by - Math.sin(perp) * halfBase,
    ax,
    ay,
  };
}

function drawEars(ctx, head, a, p, back, turnNear = 0, turnFar = 0) {
  const pointMask = p.kind === 'point-mask';
  for (const side of [-1, 1]) {
    const e = earPoints(head, side, back, side === 1 ? turnNear : turnFar);
    ctx.beginPath();
    ctx.moveTo(e.b1x, e.b1y);
    ctx.lineTo(e.ax, e.ay);
    ctx.lineTo(e.b2x, e.b2y);
    ctx.closePath();
    // Calico wears one tinted ear; points wear both dark.
    let fill = a.furBase;
    if (pointMask) fill = p.color;
    else if (p.kind === 'patches' && side === 1) fill = p.color;
    ctx.fillStyle = fill;
    ctx.fill();
    ctx.strokeStyle = a.furShade;
    ctx.lineWidth = OUTLINE_W;
    ctx.stroke();
  }
}

/**
 * One pink for the whole face. A colorway's `noseColor` paints the nose
 * triangle, the yawn's jaw and tongue mixed from it, and the inner ears --
 * so `NOSE.darken` has to reach all four or the face disagrees with
 * itself. Resolved here rather than at each site for that reason.
 */
function noseInkOf(a) {
  return NOSE.darken > 0 ? shadeHex(a.noseColor, 1 - NOSE.darken) : a.noseColor;
}

const INNER_EAR = {
  // Dialled as FUR SHOWING, because that is what the owner is judging
  // (2026-08-13). The first cut used positions in the ear's own frame --
  // base, point, width -- and every one of them moved two things at once:
  // the ear tapers, so widening the pink also closed the gap at the tip.
  //
  // Both are shares of the ear's own size rather than absolute distances,
  // so a laid-back ear (shorter and narrower) keeps its proportions
  // instead of being eaten by a fixed margin.
  sideFur: 0.28, // fur left along each slanted side
  tipFur: 0, // fur left between the pink's end and the ear's point
};

/** Where two lines, each given as a point and a direction, meet. */
function lineMeet(l1, l2) {
  const den = l1.dx * l2.dy - l1.dy * l2.dx;
  if (Math.abs(den) < 1e-12) return null;
  const t = ((l2.x - l1.x) * l2.dy - (l2.y - l1.y) * l2.dx) / den;
  return [l1.x + l1.dx * t, l1.y + l1.dy * t];
}

/** The line through p and q, moved `d` toward `inner`. */
function insetEdge(p, q, inner, d) {
  let nx = -(q[1] - p[1]);
  let ny = q[0] - p[0];
  const len = Math.hypot(nx, ny) || 1;
  nx /= len;
  ny /= len;
  if ((inner[0] - p[0]) * nx + (inner[1] - p[1]) * ny < 0) {
    nx = -nx;
    ny = -ny;
  }
  return { x: p[0] + nx * d, y: p[1] + ny * d, dx: q[0] - p[0], dy: q[1] - p[1] };
}

function drawInnerEars(ctx, head, a, back, turnNear = 0, turnFar = 0) {
  const E = INNER_EAR;
  ctx.fillStyle = noseInkOf(a);
  for (const side of [-1, 1]) {
    const e = earPoints(head, side, back, side === 1 ? turnNear : turnFar);
    const b1 = [e.b1x, e.b1y];
    const b2 = [e.b2x, e.b2y];
    const apex = [e.ax, e.ay];
    const mx = (e.b1x + e.b2x) / 2;
    const my = (e.b1y + e.b2y) / 2;

    // An ear LEANS: `earPoints` swings the tip outward, so the apex does
    // not sit over the middle of its base and the two slanted edges make
    // different angles with it. Inset by a fixed step along the base --
    // which is what "share of the ear's width" first meant -- and the two
    // edges get different amounts of fur: measured 0.46px against 0.64px,
    // and the owner could see it (2026-08-13). So each edge is moved
    // PERPENDICULAR to itself, which is the distance being judged.
    const dSide = E.sideFur * Math.hypot(e.b1x - e.b2x, e.b1y - e.b2y) * 0.5;
    const l1 = insetEdge(b1, apex, b2, dSide);
    const l2 = insetEdge(b2, apex, b1, dSide);
    // The base needs no inset: the head is painted over it.
    const base = { x: e.b1x, y: e.b1y, dx: e.b2x - e.b1x, dy: e.b2y - e.b1y };
    const foot1 = lineMeet(l1, base);
    const foot2 = lineMeet(l2, base);
    const point = lineMeet(l1, l2);
    if (!foot1 || !foot2 || !point) continue;

    // How far up the ear the inset sides meet, and where the tip is cut.
    const sx = e.ax - mx;
    const sy = e.ay - my;
    const spine = sx * sx + sy * sy;
    const uPoint = ((point[0] - mx) * sx + (point[1] - my) * sy) / spine;
    // Measured DOWN FROM where the inset sides meet, not down from the
    // ear's own point. A side margin already pulls the pink's point well
    // clear of the tip -- at the shipped 0.28 the sides meet at 0.651 up
    // the ear -- so a tip margin measured from the ear's point does
    // nothing at all until it passes that, and the threshold moves every
    // time the side dial does. From here, 0 is the natural point and
    // every value above it blunts.
    const uCut = uPoint - E.tipFur;
    if (uCut <= 0) continue; // dialled shut

    ctx.save();
    ctx.beginPath();
    ctx.moveTo(e.b1x, e.b1y);
    ctx.lineTo(e.ax, e.ay);
    ctx.lineTo(e.b2x, e.b2y);
    ctx.closePath();
    // Clipped to the ear it sits in. Belt and braces beside the maths
    // above, and it is what turns an over-dialled margin into a filled ear
    // rather than pink smeared across the skull.
    ctx.clip();
    ctx.beginPath();
    ctx.moveTo(foot1[0], foot1[1]);
    if (E.tipFur <= 0) {
      // Nothing asked for: the inset sides meet and it comes to a point.
      ctx.lineTo(point[0], point[1]);
    } else {
      // A blunt end, cut parallel to the base, so the fur at the tip is
      // dialled without the side gap changing anywhere.
      const cut = { x: mx + sx * uCut, y: my + sy * uCut, dx: e.b2x - e.b1x, dy: e.b2y - e.b1y };
      const top1 = lineMeet(l1, cut);
      const top2 = lineMeet(l2, cut);
      ctx.lineTo(top1[0], top1[1]);
      ctx.lineTo(top2[0], top2[1]);
    }
    ctx.lineTo(foot2[0], foot2[1]);
    ctx.closePath();
    ctx.fill();
    ctx.restore();
  }
}

function headPath(ctx, head) {
  ctx.beginPath();
  ctx.arc(head.cx, head.cy, head.r, 0, TAU);
}

function drawHead(ctx, head, a, p, fine, view = 'side') {
  headPath(ctx, head);
  ctx.fillStyle = a.furBase;
  ctx.fill();
  ctx.strokeStyle = a.furShade;
  ctx.lineWidth = OUTLINE_W;
  ctx.stroke();

  ctx.save();
  headPath(ctx, head);
  ctx.clip();
  // A MUZZLE is on the face, so a cat walking away does not have one in
  // view (2026-08-10). `paintCat` already skips drawFace and the inner ears
  // for exactly this reason -- "a faceless head is unmistakable even at
  // 31px" -- but the muzzle masks are painted by drawHead, which ran
  // regardless, so the two disagreed: the face vanished and a dark oval
  // stayed behind on the back of the skull.
  //
  // Only the tabby's forehead stripes checked `view` before this, and they
  // are the one head marking a cat really does wear where it can still be
  // seen from behind -- which is why they check for 'back' and keep drawing
  // head-on. The handoff's own gap list names calico and tuxedo; it does
  // not name point-mask, and point-mask is the one on the live roster
  // (Miso). Measured at a 31px tile the stray oval is 3.1 x 2.2px at 85%
  // alpha against her cream fur -- four times the sub-pixel floor that
  // killed whiskers, so it reads as a smudge rather than as a marking.
  const rear = view === 'back';
  if (p.kind === 'point-mask' && !rear) {
    // The seal-point face: a soft dark oval over the muzzle -- anchored
    // to NOSE.x (v2, owner 2026-07-29) so the mask follows the front-on
    // face instead of v1's profile muzzle at the head's edge. Upright
    // (no rotation): the old 0.1 rad lean was a profile artifact.
    ctx.fillStyle = p.color;
    ctx.globalAlpha = 0.85;
    ctx.beginPath();
    ctx.ellipse(muzzleX(head, view), head.cy + head.r * (NOSE.y + 0.08), head.r * 0.46, head.r * 0.32, 0, 0, TAU);
    ctx.fill();
    ctx.globalAlpha = 1;
  } else if (p.kind === 'tuxedo-mask' && !rear) {
    // The white muzzle that makes the tuxedo, centered under the nose
    // like the point mask (v2). Same rule, same reason -- though no cat on
    // the roster wears it, so this one only shows in the gallery today.
    ctx.fillStyle = p.color;
    ctx.beginPath();
    ctx.ellipse(muzzleX(head, view), head.cy + head.r * (NOSE.y + 0.14), head.r * 0.5, head.r * 0.4, 0, 0, TAU);
    ctx.fill();
  } else if (p.kind === 'patches') {
    ctx.fillStyle = p.color2 || p.color;
    ctx.beginPath();
    // v2 (owner, 2026-07-29): the calico's grey patch, shrunk and slid up
    // toward the ear -- at v1's placement the relocated rear eye cut it
    // into a half-hidden sliver. Now it clears the eye and reads whole.
    ctx.ellipse(head.cx - head.r * 0.62, head.cy - head.r * 0.58, head.r * 0.36, head.r * 0.3, -0.35, 0, TAU);
    ctx.fill();
  } else if (p.kind === 'tabby-stripes' && fine && view !== 'back') {
    // Three tiny forehead stripes, only when they can actually read.
    ctx.strokeStyle = p.color;
    ctx.lineWidth = OUTLINE_W * 0.8;
    for (const s of [-0.28, 0, 0.28]) {
      ctx.beginPath();
      ctx.moveTo(head.cx + head.r * (s + 0.02), head.cy - head.r * 0.92);
      ctx.lineTo(head.cx + head.r * s, head.cy - head.r * 0.45);
      ctx.stroke();
    }
  }
  ctx.restore();
}

/** Perceived-luminance check so eyes stay visible on every coat. */
function isDarkColor(hex) {
  const n = parseInt(hex.slice(1), 16);
  const r = (n >> 16) & 255;
  const g = (n >> 8) & 255;
  const b = n & 255;
  return 0.299 * r + 0.587 * g + 0.114 * b < 120;
}

/** The pupil's ink -- one warm near-black on every coat; the iris color
 * behind it carries the per-cat identity and the dark-fur contrast. */
const PUPIL_INK = '#2f2a26';

/**
 * Eye tunables (v2), BAKED from the lab dials (owner, 2026-07-29): bigger
 * than v1 (scale 0.19 vs 0.14), raised a touch above head center (height
 * -0.075 vs v1's +0.02), and shifted well back toward the middle of the
 * face (shift -0.15) -- a significant move off v1's nose-hugging
 * placement, dialed live and judged really cute. pupil is a ratio of the
 * iris radius. Still mutable: the lab's dials write here live.
 */
const EYE = {
  scale: 0.19, // iris radius / head.r
  height: -0.075, // eye center vs head center / head.r (+down, -up)
  shift: -0.15, // both eyes together / head.r (+toward nose, -toward back)
  // Head-on, both eyes sit this far either side of centre. Wider than half
  // the side view's spread (0.25 vs 0.35) on purpose: a front-on face reads
  // cuter with the eyes set a little apart, and it keeps them clear of the
  // muzzle beneath.
  frontSpread: 0.25,
  spreadNear: 0.12, // rear eye offset / head.r
  spreadFar: 0.62, // front eye offset / head.r
  // Pupil size as a share of the APERTURE's half-height, not of `er`
  // (2026-08-10). Measured against er, the aperture dials silently ate
  // the iris: at apertureH 0.92 the visible coloured ring fell to 1.1px
  // at a 120px cat by day and 0.28px at night, and that ring is the
  // per-cat identity signal -- eye colour is how a viewer tells Miso from
  // Pumpkin. Sized against the aperture, the ring is a fixed share of the
  // eye whatever shape the eye is, and dilation has honest room to move
  // instead of hitting the clamp.
  // 0.78 owner-dialled 2026-08-10: bigger reads cuter, and this is a
  // little larger than the pupil the vocabulary shipped with (which was
  // 0.7 of `er`, and worked out at 0.607 once the aperture arrived --
  // a 13% shrink nobody asked for).
  //
  // Note the trade this sets up, because it is physical rather than a
  // tuning accident: the bigger the resting pupil, the less room is left
  // above it to dilate into. A large day pupil and a dramatic night one
  // cannot both be had out of one aperture.
  pupil: 0.78, // pupil half-height / aperture half-height
  // The hunter's eyes keep v1's smaller radius AND v1's lower vertical
  // position (owner, 2026-07-29: the narrowed look reads worse blown up
  // or raised). Horizontal placement stays v2's shifted-back spread.
  // Unused since the hunter's eyes were rebuilt out of the ordinary eye
  // (2026-08-10). Kept only because gallery-v2's dial table names them.
  focusedScale: 0.14,
  focusedHeight: 0.02,
  // --- The hunter's eyes.
  //
  // Built FROM the ordinary eye rather than beside it, so a hunting cat
  // keeps its iris, its colour and its identity. What they replace was a
  // flat dark ellipse with a straight line struck above it -- readable at
  // 22px, where the whole eye is three pixels and a dark mark is all
  // anyone can see, and shapeless the moment there is room for detail.
  //
  // Intensity is a lowered lid angled the OTHER way: a sleepy lid droops
  // at the outer corner, an intense one drops at the inner one. Same lid
  // drawing, opposite sign.
  // Re-dialled 2026-08-10: the first cut was intense and also EVIL, and
  // the fix is structural rather than a matter of degree.
  //
  // Anger narrows an eye from ABOVE -- a brow lowered toward the nose is
  // the threat signal, in cats and in everything else with a face.
  // Mirth narrows it from BELOW: a raised lower lid is what a hard grin
  // does to an eye. The two look equally narrowed and mean opposite
  // things, so the squint can move from the top of the eye to the bottom
  // and keep every bit of its intensity while losing the menace.
  //
  // So the brow is now barely there, the work is done by the lower lid,
  // and two supporting cues follow: a pupil that stays engaged rather
  // than reptilian, and a little asymmetry -- a symmetrical stare reads
  // as threat, a lopsided one as scheming.
  // Second pass: the first attempt at the cheek squint closed the eye so
  // far that the pupil filled what was left, which is the flat dark slot
  // the whole rebuild was meant to escape -- and a slot reads grumpy, not
  // mischievous. Total closure is now well down and the WORK is done by
  // the shape of the lower lid's edge rather than by its height.
  //
  // `focusLowerCurve` is the expression. Scooping the edge up in the
  // middle makes the eye's visible underside an arc, which is the same
  // happy curve the closed eyes are drawn with -- a smile, in the eye.
  // Both dialled well down on the third pass. Widening the aperture while
  // narrowing it put the eye at half again as wide as it was tall BEFORE
  // the lids landed, so whatever they left over came out as a letterbox
  // slot -- and a slot reads grumpy however it is shaped. A mischievous
  // squint is not a wide eye, it is a nearly round one with the bottom
  // pushed up. Keep these small; the lower lid is what should be doing
  // the work.
  focusSquash: 0.05, // how far the aperture narrows
  focusWiden: 0.03, // and widens as it narrows
  focusTilt: 0.05, // extra tilt on the aperture itself
  focusLid: 0.05, // the brow: a hint of one, no more
  focusLidTilt: 0.1, // + drops the inner corner. Was 0.34, which was the menace
  focusLidCurve: 0.1, // and a soft bow, as the resting lid has
  // The cheek. This is the expression.
  focusLowerLid: 0.24, // how far the lower lid rides up
  focusLowerTilt: -0.05, // a slight outer lift, the way a grin pushes
  focusLowerCurve: -0.3, // scooped UP in the middle: the smile, in the eye
  focusAsym: 0.3, // how much less the rear eye squints -- scheming, not menacing
  focusPupilW: 0.78, // narrower than resting, well short of a reptile's slit
  // The focused eye needs its own pupil HEIGHT, not just its own width.
  // At the resting 0.78 of the aperture the pupil filled everything the
  // lids left over, so a narrowed eye came out dark-green-dark -- a slot
  // with a bar through it, which is the flat blob the rebuild set out to
  // escape. Smaller here leaves iris visible above the pupil, which is
  // what makes a narrowed eye still read as an eye.
  focusPupilH: 0.58, // pupil half-height / aperture, when focused
  // Which take of the hunter's face is live. See FOCUS_VARIANTS.
  // 'intense' shipped 2026-08-10 (owner). The remaining tuning knob, if
  // anyone wants one, is FOCUS_VARIANTS.intense.focusLidTilt -- the brow's
  // inward angle, and the whole menace axis: 0.20 ships, 0.34 read as
  // evil, 0 reads as pure concentration. Nothing else in the take needs
  // touching to move it along that spectrum.
  focusVariant: 'intense',
  // How much the aperture GROWS when focused. The hunting pupil dilates
  // (see FOCUS_VARIANTS.wide), and it needs somewhere to go.
  //
  // Growing the aperture alone does NOT buy the pupil room, which is the
  // trap the first attempt fell into: the pupil is a fraction OF the
  // aperture, so scaling the aperture scales the pupil in lockstep and
  // the relative headroom -- the visible iris -- is unchanged. Room comes
  // from pairing this with `focusPupilBase`, a lower base share that the
  // grown aperture then makes absolutely large. The eye gets bigger, the
  // pupil gets bigger, and the iris survives; all three at once.
  focusGrow: 0,
  // How far the two eyes move APART when focused, in head radii, split
  // evenly either side of the face's midline.
  //
  // Needed because `focusGrow` grows each eye about its own centre while
  // the centres stay put: at 24% growth the two apertures overlapped by
  // 0.8px on a 120px cat, which is why the hunting face read as one wide
  // dark band rather than as two eyes. Spreading rather than shrinking,
  // because the whole point of the dilated take is a big pupil.
  focusSpread: 0,
  // How far either lid may crop the pupil, as a share of the pupil's own
  // height. Both lids lower until they just kiss the pupil and stop --
  // see the clamps at the lid calls.
  focusBrowGraze: 0.03,
  // 'half' is a lidded open eye, not v1's flat dash: the same partial
  // lid the slow blink passes through, parked at this coverage. All
  // three lid values BAKED from the lab dials (owner, 2026-07-29).
  // --- The aperture (2026-08-10). Two concentric circles read as dots.
  // A cat's eye opening is a rounded almond, a little wider than it is
  // tall, with the outer corner carried lower than the inner one -- and
  // because those are whole-eye SHAPE changes they survive the live tile,
  // where the iris is 1.3px of radius and nothing smaller than itself can
  // read at all.
  apertureW: 1.12, // iris half-width / er
  apertureH: 0.92, // and half-height
  tilt: 0.15, // outer corner drop, radians; mirrored about the face
  // --- The pupil.
  //
  // ROUND is the shipped starting point (owner, 2026-08-10), and the dial
  // stays because the argument for narrowing it is real but was not
  // taken: a vertical pupil is the most catlike mark available, yet this
  // vocabulary already owns the predatory look in `focused`, so narrowing
  // the RESTING pupil spends a contrast that is already doing a job. A
  // world of cats with slit pupils has nothing left to say "hunting".
  //
  // What carries the cat reading instead is dilation, below: the pupil
  // stays round and changes SIZE with the hour, which is what a real
  // pupil mostly does and what a viewer actually notices.
  pupilW: 1, // pupil width as a share of its height; below ~0.6 reads as hunting
  // --- The rim. What this replaces was a hairline in FUR colour, there
  // so a pale iris held its shape against pale fur. A darkened iris
  // reads as the limbal ring a real eye has AND does that job better.
  pupilMax: 0.96, // hard ceiling as a share of the aperture; a guard, not a look
  limbal: 0.55, // how far the rim walks toward the pupil ink
  limbalW: 0.17, // and its width, in iris radii
  irisDepth: 0.2, // a soft darker cap at the top, for roundness
  halfLid: 0.54,
  // Lid edge slope, in iris radii of drop per radius of run. Dialed
  // slightly NEGATIVE: the outer corners droop away from the nose --
  // the strong toward-the-middle slant read angry, the soft outward
  // droop reads sleepy. Applies to every lid; blinks sweep the same way.
  lidTilt: -0.08,
  // Lid edge curvature, in iris radii of center sag: + bows the edge
  // DOWN (convex -- rounder, sleepier), - scoops it UP (concave), 0 is
  // the straight edge (which read angry on its own, owner 2026-07-29).
  lidCurve: 0.14,
};

/** Nose tunables (v2), dialed in the lab like EYE. Working values
 * (owner, 2026-07-29, NOT final): pulled from v1's muzzle tip (0.86,
 * 0.26) back to the eye midline for the front-on face. */
/**
 * The pale underside, mutable for the lab like NOSE and MOUTH.
 *
 * Every soft cat gets one; ours had none. The only underside in the whole
 * vocabulary was the tuxedo's white bib, which is a PATTERN on one palette
 * — so Miso, Biscuit, Pumpkin and Kittybear, the four cats actually on the
 * world, were flat ellipses of a single fur colour.
 *
 * Offsets are in the body's OWN radii and its own rotated frame, so this
 * follows every pose for free: the loaf, the curl, the crouch and the
 * float all get a belly in the right place without a per-pose value, and
 * without an entry in `blendLayouts` that could pop on a pose change.
 *
 * Ratios are kitten.me's, converted out of their tile units: their belly
 * sits at (0.06s, 0.12s) with a body of (0.44s, 0.33s) and radii of half
 * the body — which is 0.14 rx across, 0.36 ry down, at 0.5 x 0.45.
 */
const BELLY = {
  x: 0.13, // centre, in body rx from the body centre (+ is forward)
  y: 0.55, // and in body ry downward
  rx: 0.62, // half-width, in body rx
  ry: 0.42, // half-height, in body ry
  lighten: 0.35, // how far the fur base is mixed toward white
  // The least a belly may differ from its coat, in CIE L*. Below this the
  // lighten has run out of headroom and `bellyInkOf` shades instead.
  //
  // The window is narrow and worth knowing before touching this: Clementine
  // separates by 1.4 and MUST flip; Miso, the seal point, separates by only
  // 3.0 and must NOT, because her belly shipped with the owner's approval.
  // Everyone else is 7.4 or better. 2.2 sits between the two, so this is a
  // strict no-op for every coat that shipped before the fifth cat.
  //
  // That Miso is at 3.0 is a finding, not a comfort -- her belly is nearly
  // as faint as the one being fixed here. Raising this dial past 3.0 brings
  // her in too, which is a live option and the owner's call, not a bug.
  minSeparation: 2.2,
  darken: 0.3, // ...and how far toward furShade it goes when it does
  alpha: 0.85,
};

/**
 * Whiskers, attempt three (2026-08-13). Off by default -- the first two
 * were built and cut, and BACKLOG says cut again is an acceptable outcome.
 *
 * Ported from kitten.me, which draws them without ever using the word, and
 * whose trick is not resolution but ALPHA. Its stroke is
 * `max(0.8, cat * 0.018)`, so below a 44px cat it sits pinned at the 0.8px
 * floor -- kitten.me does not escape the sub-pixel problem, it lives with
 * it at 0.4 opacity, where a hairline reads as a soft hint instead of an
 * aliased dotted line. Our two attempts died at "0.8px strokes", which is
 * the same number drawn at full strength.
 *
 * The other half is placement: theirs run from 0.30 to 1.05 head radii, so
 * they leave the muzzle and finish PAST the head silhouette, and most of
 * their visible length is against the background rather than against fur.
 *
 * `widthPx` is in PIXELS and everything else is in head radii, because a
 * pixel floor is the whole point. paintCat is handed `size` for it -- the
 * drawing is otherwise in unit space, where a 0.8 lineWidth would be most
 * of a cat.
 */
const WHISKER = {
  on: 1, // owner-baked 2026-08-13, off the lab. 0..1, a fade not a switch.
  count: 3, // per side
  alpha: 0.25, // kitten.me's, and the reason theirs work at all
  widthPx: 0.8, // the floor, in real pixels
  widthOfCat: 0.016, // ...and the share of the cat it grows past that
  rootX: 0.34, // from the muzzle, in head radii
  tipX: 1.25, // ...to past the head's own edge
  rootY: 0.28, // where the middle one leaves the muzzle
  tipY: 0.17, // and where it ends up
  // The whole set, up or down together, in head radii. Separate from
  // rootY/tipY on purpose: those two set the DROOP, and nudging the pair
  // of them in step to move the set is how a droop gets lost by accident.
  offsetY: 0,
  rootSpread: 0.1, // fan at the root
  tipSpread: 0.24, // ...and at the tip, so they splay
  // How much of the forward length the REARWARD fan gets, side-on. 0 by
  // default, and that is geometry rather than taste: our muzzle sits 0.22
  // head radii forward of the head centre (kitten.me's face is centred),
  // so a rear fan starts deep inside the skull and would have to be 1.2x
  // the FORWARD one just to reach the back of the head. Every stroke of it
  // is buried in fur. Head-on there is no near side, so both fans draw.
  back: 1,
};

const NOSE = {
  x: 0.22, // nose center from head center / head.r (toward the muzzle)
  y: 0.29, // below head center / head.r
  size: 0.17, // half-width / head.r
  // 0 leaves each colorway's authored nose alone; 1 takes it to black.
  // Added when whiskers landed (2026-08-13): three hairlines either side
  // of the muzzle pull the eye there, and a pale pink nose that read fine
  // on its own stops holding the middle of the face against them.
  darken: 0.02,
};

/**
 * Where the muzzle sits ACROSS the face, in head radii.
 *
 * From the side it leads toward the nose; seen front-on there is no
 * "toward", so it sits on the centreline. One function because three
 * things have to agree about it -- the nose, the mouth that tracks the
 * nose, and the muzzle MASK the point and tuxedo colourways paint under
 * both. They did not: the mask kept the side view's offset while the nose
 * moved to centre, so a front-on seal point wore her dark muzzle 0.22
 * head-radii to one side of her own nose (owner spotted it, 2026-08-10).
 * Measured, the two centres sat 2.40px apart at the 47px card portrait and
 * 1.58px at a 31px tile. The SIDE view was never wrong -- mask and nose
 * both read NOSE.x there -- which is why this survived: it is visible only
 * head-on, the one view that did not exist until this round.
 */
function muzzleX(head, view) {
  return head.cx + head.r * (view === 'front' ? 0 : NOSE.x);
}
// A kitten.me-style heart was tried and cut (owner, 2026-08-09): a shallow
// V over-stroked with round caps and joins, so the caps make the lobes and
// the join the point. It is a good heart in isolation -- but at our head
// radius it reads worse than the triangle it replaced, softer and less
// legible where the triangle is a clean mark. Their heart works on a head
// nearly 1.6x ours (0.27s against our 0.226 of a smaller box).

/** Mouth tunables (v2): an upside-down V hanging under the nose apex,
 * centered on NOSE.x. Under review (owner, 2026-07-29) -- the earlier
 * side-profile ω was tried and cut, but the front-on face reopened the
 * question. All ratios of head.r. */
const MOUTH = {
  style: 'w', // 'v' = upside-down V | 'w' = rounded ω (two half-ellipses)
  gap: 0, // space between nose apex and the mouth's center point
  width: 0.24, // half-span
  depth: 0.08, // vertical reach: leg drop ('v') or arc bulge ('w')
};

function drawFace(ctx, head, eyes, a, lid = 0, gaze = null, yawn = 0, view = 'side', size = 31) {
  // A yawn squeezes the eyes shut on its way open -- it is the eyes, not
  // the mouth, that make a yawn read as one at 31px.
  if (yawn > 0.02) lid = Math.max(lid, smooth01(yawn * 1.1));
  const darkFur = isDarkColor(a.furBase);
  const eyeInk = darkFur ? a.eyeColor : '#453c36';
  const focus = eyes === 'focused' ? 1 : 0;
  // The focused eye reads its dials through the live variant; the resting
  // eye reads EYE itself, unspread and unchanged, so nothing about the
  // ordinary face can depend on which take of the hunter is selected.
  const F = focus ? { ...EYE, ...(FOCUS_VARIANTS[EYE.focusVariant] || null) } : EYE;
  // Half the spread each way, so widening the pair cannot shift the face.
  const half = (focus * (F.focusSpread || 0)) / 2;
  // The side view's eyes are deliberately asymmetric about the head -- one
  // near, one far, shifted toward the muzzle -- which is what gives that
  // drawing its three-quarter read. Head-on there is no near and no far,
  // so they sit symmetric about the centre; keeping the side spread here
  // would slide the whole face off the middle of a front-on skull.
  const frontOn = view === 'front';
  const ex1 = frontOn
    ? head.cx - head.r * (EYE.frontSpread + half)
    : head.cx + head.r * (EYE.spreadNear + EYE.shift - half);
  const ex2 = frontOn
    ? head.cx + head.r * (EYE.frontSpread + half)
    : head.cx + head.r * (EYE.spreadFar + EYE.shift + half);
  const ey = head.cy + head.r * EYE.height;
  const er = head.r * EYE.scale;
  // 'half' rides the open-eye path under a standing lid (v2): the drowsy
  // face is the slow blink's midpoint, held. A deeper transient lid (a
  // blink mid-drink) still wins via max().
  if (eyes === 'half') {
    eyes = 'open';
    lid = Math.max(lid, EYE.halfLid);
  }
  // The hunter's eyes are the SAME eyes, narrowed -- not a second
  // drawing. See EYE.focus* for why that matters.
  if (focus) {
    eyes = 'open';
    // Locked: hunting kitties do not blink (owner, 2026-08-02). The lid
    // they wear is a brow at a fixed depth, not a blink in progress, so
    // it is assigned rather than max()'d over whatever was passed in.
    lid = F.focusLid;
  }
  // A fully-lowered lid IS the closed eye: blinks that ease the lid down
  // land on the same happy arcs a served 'closed' state draws.
  if (lid >= 0.97 && !focus) eyes = 'closed';

  if (eyes === 'closed') {
    // Happy little down-curved arcs.
    ctx.strokeStyle = eyeInk;
    ctx.lineWidth = OUTLINE_W * 0.9;
    for (const ex of [ex1, ex2]) {
      ctx.beginPath();
      ctx.arc(ex, ey - er * 0.4, er, 0.25 * Math.PI, 0.75 * Math.PI);
      ctx.stroke();
    }
  } else {
    // Open eyes, fully dressed at every size. Canvas antialiasing
    // shoulders the tiny sizes -- a 22px cat keeps a readable eye where
    // v1 drew two flat dots.
    //
    // The three changes over the two concentric circles this replaces are
    // all whole-eye shape, which is the only kind that survives the live
    // tile: an almond aperture carried at a tilt, a vertical pupil, and a
    // rim that darkens instead of matching the fur.
    const mid = (ex1 + ex2) / 2;
    for (const ex of [ex1, ex2]) {
      // Mirrored about the face's own midline, so the pair reads as a face
      // rather than as two identical marks. The rotation lifts each eye's
      // OUTER corner -- positive canthal tilt, the thing that reads as
      // alert rather than sad. (An earlier comment here claimed the
      // corners dropped; they do not, and the sign is load-bearing.)
      const side = ex < mid ? 1 : -1;
      const rot = side * (F.tilt + focus * F.focusTilt);
      // Narrower AND a touch wider: a hunting cat's eye is a stare, and a
      // stare is not a squint. Narrowing alone reads as a cat in bright
      // sun rather than one that has seen something.
      const grow = 1 + focus * (F.focusGrow || 0);
      const rw = er * F.apertureW * (1 + focus * F.focusWiden) * grow;
      const rh = er * F.apertureH * (1 - focus * F.focusSquash) * grow;
      const aperture = () => {
        ctx.beginPath();
        ctx.ellipse(ex, ey, rw, rh, rot, 0, TAU);
      };
      aperture();
      ctx.fillStyle = a.eyeColor;
      ctx.fill();
      // A soft darker cap at the top: light comes from above, so the
      // underside of an iris is the bright part. Clipped, so it can only
      // ever shade the eye it belongs to.
      if (EYE.irisDepth > 0) {
        ctx.save();
        aperture();
        ctx.clip();
        ctx.globalAlpha = EYE.irisDepth;
        ctx.fillStyle = PUPIL_INK;
        ctx.beginPath();
        ctx.ellipse(ex, ey - rh * 0.98, rw * 1.2, rh * 0.85, rot, 0, TAU);
        ctx.fill();
        ctx.restore();
      }
      // The pupil travels inside the iris toward whatever the cat is
      // attending to. This is the cheapest aliveness in the entire rig --
      // a pupil that never moves is a printed dot, and moving it costs
      // one clip and two additions. Clipped to the aperture so a hard
      // look can never push the pupil out onto the fur.
      //
      // `pupilDilate` arrives on the appearance, set by the hour.
      //
      // The clamp is a guard rather than part of the look: no theme should
      // reach it, because a pupil filling the whole aperture takes the
      // eye COLOUR with it, and eye colour is how a viewer tells one cat
      // from another. Every hour keeps a visible ring of iris.
      const dil = a.pupilDilate || 1;
      // A hunting pupil DILATES (owner, 2026-08-10). The two dilations
      // compose rather than one replacing the other: a hunting cat's
      // pupil is at least as open as a night pupil whatever the hour, and
      // at night it opens further still, as far as the aperture allows.
      // Taking the max rather than just multiplying is what guarantees
      // the floor -- a midday hunt must not come out narrower than an
      // idle midnight.
      //
      // Takes that predate the correction still say focusPupilH and are
      // drawn as they were reviewed; only a take naming focusDilate goes
      // through the dilation path.
      const focusDil = focus && F.focusDilate
        ? Math.max(PUPIL_DILATE_BY_THEME.night, dil * F.focusDilate)
        : null;
      const share = focusDil
        ? (F.focusPupilBase || F.pupil) * focusDil
        : focus ? F.focusPupilH : F.pupil * dil;
      const ph = Math.min(rh * share, rh * F.pupilMax);
      // The vertical pupil, saved for exactly this moment. It was kept
      // deliberately out of the resting eye so that narrowing it HERE
      // would still mean something: a world of slit-pupilled cats has
      // nothing left to say "hunting" with.
      const wRatio = focus ? F.focusPupilW : Math.min(1, F.pupilW * dil);
      const pw = Math.min(ph * wRatio, rw * 0.94);
      ctx.save();
      aperture();
      ctx.clip();
      ctx.fillStyle = PUPIL_INK;
      ctx.beginPath();
      ctx.ellipse(
        ex + (gaze ? gaze.x * er * RIG.gazePupil : 0),
        ey + er * 0.06 + (gaze ? gaze.y * er * RIG.gazePupil : 0),
        pw,
        ph,
        rot,
        0,
        TAU,
      );
      ctx.fill();
      ctx.restore();
      // The limbal ring, struck last so it sits over both iris and pupil
      // and closes the eye's edge cleanly. Walks the iris colour toward
      // the pupil ink rather than toward the fur, which is what makes it
      // read as an eye rather than as an outline round one.
      if (F.limbalW > 0) {
        aperture();
        ctx.strokeStyle = mixHex(a.eyeColor, PUPIL_INK, F.limbal);
        ctx.lineWidth = er * F.limbalW;
        ctx.stroke();
      }
      // (White glint tried and cut, owner 2026-07-29.)
      // One lid, drawable from either side of the eye. `dir` is -1 for
      // the upper lid coming down and +1 for the lower coming up; every
      // other difference between the two is a dial, which is what lets
      // the hunting face move its squint from the top of the eye to the
      // bottom without a second drawing.
      //
      // All of it is measured against the APERTURE rather than against
      // `er`: with a narrowed hunting eye the two differ, and a lid sized
      // to the wrong one covers the wrong share of it. Clipped to the
      // aperture so it can never smear onto the fur.
      const drawLid = (cover, tiltAmt, curveAmt, dir) => {
        if (!(cover > 0.02)) return;
        ctx.save();
        ctx.beginPath();
        ctx.ellipse(ex, ey, rw + OUTLINE_W * 0.3, rh + OUTLINE_W * 0.3, rot, 0, TAU);
        ctx.clip();
        const edge = ey + dir * (rh - 2 * rh * cover);
        const run = rw * 1.3;
        const drop = er * tiltAmt;
        const far = ey + dir * rh * 1.7; // past the eye, on the lid's own side
        const y0 = edge - side * drop;
        const y1 = edge + side * drop;
        // Offsetting the control point by 2x sinks the curve's midpoint
        // by exactly er * curve off the straight chord.
        const ctrlY = (y0 + y1) / 2 + 2 * er * curveAmt;
        ctx.fillStyle = a.furBase;
        ctx.beginPath();
        ctx.moveTo(ex - run, far);
        ctx.lineTo(ex + run, far);
        ctx.lineTo(ex + run, y1);
        ctx.quadraticCurveTo(ex, ctrlY, ex - run, y0);
        ctx.closePath();
        ctx.fill();
        ctx.strokeStyle = a.furShade;
        ctx.lineWidth = OUTLINE_W * 0.5;
        ctx.beginPath();
        ctx.moveTo(ex - run, y0);
        ctx.quadraticCurveTo(ex, ctrlY, ex + run, y1);
        ctx.stroke();
        ctx.restore();
      };

      // Neither lid may eat the pupil.
      //
      // A brow deep enough to look like concentration was cropping 41% of
      // the pupil's height, which cost the take the very thing it was
      // revived for: `focusPupilW: 1` makes a ROUND pupil, and a round
      // pupil clipped flat across the top is a letterbox. Worse, the
      // damage was invisible in the dials -- the geometry said the pupil
      // had grown while the drawing showed it shrinking, so tuning
      // `focusPupilBase` could never have fixed it.
      //
      // So it is an invariant rather than a number: whatever a lid is set
      // to, it lowers until it just kisses the pupil and stops. It applies
      // to the cheek as much as to the brow -- the first version of this
      // clamp only guarded the top, and the lower lid went on quietly
      // taking a slice off the bottom, which is why the pupil was still
      // 10% short of its neighbour's. Any variant can now ask for as much
      // of either lid as it likes and the round pupil survives, which is
      // the property that makes the takes comparable at all.
      // The lids are CURVED, and the bow at mid-span reaches deeper into
      // the eye than the lid's edge height does -- by exactly er * curve,
      // since a quadratic with its control point offset 2k sits k off the
      // chord at the midpoint. The first two attempts at this clamp
      // measured only the edge, so a lid whose cover was legitimately
      // clear of the pupil still bowed across it, and the numbers refused
      // to move. The pupil sits at the eye's mid-span, which is precisely
      // where the bow is deepest, so the curve term is the whole story.
      const graze = ph * (1 - F.focusBrowGraze);
      const pupilCy = er * 0.06;
      const lidRoom = (curveAmt, dir) =>
        (rh + dir * (pupilCy + er * curveAmt) - graze) / (2 * rh);
      let effLid = lid;
      if (focus) effLid = Math.min(lid, lidRoom(-F.focusLidCurve, 1));
      drawLid(
        effLid,
        focus ? F.focusLidTilt : F.lidTilt,
        focus ? F.focusLidCurve : F.lidCurve,
        -1,
      );
      if (focus) {
        // The cheek pushing up under the eye. The rear eye squints less,
        // because a face doing the same thing on both sides reads as a
        // threat and a face doing it lopsidedly reads as up to something.
        drawLid(
          Math.min(
            F.focusLowerLid * (side === 1 ? 1 - F.focusAsym : 1),
            // Negated because `dir` already flips the curve term: passing
            // the raw value flipped it twice and left the cheek MORE room
            // than it should have had, not less.
            lidRoom(-F.focusLowerCurve, -1),
          ),
          F.focusLowerTilt,
          F.focusLowerCurve,
          1,
        );
      }
    }
  }

  // Nose: the tiny triangle that makes it a cat. Placed by NOSE dials.
  // v2: a symmetric upside-down triangle, upright with respect to the
  // eyes (owner call, 2026-07-29) -- v1's skewed profile-leaning triangle
  // read wrong once the face went front-on.
  // ...and the muzzle sits on the centreline for the same reason.
  const nx = muzzleX(head, view);
  const ny = head.cy + head.r * NOSE.y;
  const ns = head.r * NOSE.size;
  const noseInk = noseInkOf(a);
  ctx.fillStyle = noseInk;
  ctx.beginPath();
  ctx.moveTo(nx - ns, ny - ns * 0.6);
  ctx.lineTo(nx + ns, ny - ns * 0.6);
  ctx.lineTo(nx, ny + ns * 0.7);
  ctx.closePath();
  ctx.fill();

  // Mouth under the nose, tracking NOSE.x; two styles under review
  // (owner, 2026-07-29). 'v': the upside-down V. 'w': the rounded front-on
  // ω -- two half-ellipses meeting beneath the nose apex, bulge set by
  // depth. (The old profile ω was cut with the profile face; this is its
  // front-on cousin.) No whiskers -- ever.
  // Ink: furShade normally, but on a point mask the mouth sits ON the
  // dark mask, so it inks slightly darker than the point color itself
  // (owner, 2026-07-29: furShade read pale-on-dark, silly).
  const my = ny + ns * 0.7 + head.r * MOUTH.gap;
  ctx.strokeStyle = a.pattern?.kind === 'point-mask'
    ? shadeHex(a.pattern.color, 0.82)
    : a.furShade;
  ctx.lineWidth = OUTLINE_W * 0.55;
  if (yawn > 0.02) {
    // The jaw drops UNDER the muzzle mark; the mark itself stays exactly
    // where it is (owner, 2026-08-10).
    //
    // The first cut replaced the omega with the opening, which is what a
    // human mouth does -- lips part and the line becomes the shape. A
    // cat's does not: the :3 is not a pair of lips, it is where the
    // muzzle meets the upper lip, and it stays put while the jaw swings
    // down beneath it. Deleting it deleted the only mark on the face
    // saying "cat", which is why the gape read human however the outline
    // was shaped.
    //
    // So this draws the opening first and lets the omega stroke over its
    // top edge: the mark becomes the upper lip of the open mouth for
    // free, and the closed and open faces share it rather than
    // interpolating between two different drawings.
    const o = smooth01(yawn);
    const gw = head.r * MOUTH.width * (0.6 + 0.3 * o);
    const top = my + head.r * MOUTH.depth * 0.5; // just under the omega's bulges
    const d = head.r * RIG.yawnMouth * o;
    // The jaw alone, with no top edge -- the omega is the top edge.
    const jaw = () => {
      ctx.moveTo(nx - gw, top);
      ctx.bezierCurveTo(nx - gw * 0.98, top + d * 0.66, nx - gw * 0.52, top + d, nx, top + d);
      ctx.bezierCurveTo(nx + gw * 0.52, top + d, nx + gw * 0.98, top + d * 0.66, nx + gw, top);
    };
    ctx.fillStyle = shadeHex(noseInk, 0.5);
    ctx.beginPath();
    jaw();
    ctx.closePath(); // the chord back along `top`, hidden under the omega
    ctx.fill();
    if (o > 0.45) {
      // The tongue. Small, but it is what keeps a gape reading as a yawn
      // rather than as a hiss -- which is the last thing this world wants.
      ctx.fillStyle = lightenHex(noseInk, 0.22);
      ctx.beginPath();
      ctx.ellipse(nx, top + d * 0.72, gw * 0.46, d * 0.2, 0, 0, TAU);
      ctx.fill();
    }
    ctx.beginPath();
    jaw(); // stroked open, so no line is struck where the omega will go
    ctx.stroke();
  }
  ctx.beginPath();
  if (MOUTH.style === 'w') {
    // Each half-ellipse needs its own moveTo: without it, canvas draws a
    // connecting chord between the arcs that closes them into solid-
    // looking capsules.
    const half = head.r * MOUTH.width * 0.5;
    for (const side of [-1, 1]) {
      const cx = nx + side * half;
      ctx.moveTo(cx + half, my);
      ctx.ellipse(cx, my, half, head.r * MOUTH.depth, 0, 0, Math.PI);
    }
  } else {
    ctx.moveTo(nx - head.r * MOUTH.width, my + head.r * MOUTH.depth);
    ctx.lineTo(nx, my);
    ctx.lineTo(nx + head.r * MOUTH.width, my + head.r * MOUTH.depth);
  }
  ctx.stroke();

  drawWhiskers(ctx, head, a, view, size);
}

/**
 * Three a side, leaving the muzzle and finishing past the head's own edge.
 *
 * Inside `drawFace` on purpose: that is only ever called for a face we can
 * see, so a cat walking away has no whiskers without this knowing the rule
 * exists. The same placement is why the muzzle masks moved there in #187.
 */
function drawWhiskers(ctx, head, a, view, size) {
  const W = WHISKER;
  if (!(W.on > 0)) return;
  // In PIXELS, then converted: the drawing runs in unit space, where a
  // lineWidth of 0.8 would be most of a cat. This is the floor kitten.me
  // pins to below a 44px cat, and the reason its hairlines survive.
  ctx.save();
  ctx.lineWidth = Math.max(W.widthPx / size, W.widthOfCat);
  // Alpha through the context, not baked into a colour string: cat-v2 has
  // no `withAlpha`, and a whisker has to work over fur AND over grass, so
  // compositing beats picking one blend.
  ctx.globalAlpha = W.alpha * W.on;
  // A pale cat needs a dark hair and a dark cat a pale one, or the whisker
  // is the one part of the face that vanishes on half the roster.
  ctx.strokeStyle = isDarkColor(a.furBase) ? '#efe7dd' : '#453c36';
  ctx.lineCap = 'round';
  const r = head.r;
  const cx = muzzleX(head, view);
  const cy = head.cy + r * NOSE.y;
  // Front-on there is no near side and no far side, so both fans are the
  // same length. In the side view the far fan is foreshortened -- the same
  // argument the axial swim tail is built on.
  const sides = view === 'front' ? [1, -1] : [1, -1];
  const mid = (W.count - 1) / 2;
  for (const dir of sides) {
    const reach = view === 'front' || dir > 0 ? 1 : W.back;
    if (reach <= 0) continue; // a zero-length fan is six strokes of nothing
    for (let i = 0; i < W.count; i++) {
      const k = i - mid;
      ctx.beginPath();
      const dy = r * W.offsetY;
      ctx.moveTo(
        cx + dir * r * W.rootX,
        cy + dy + r * (W.rootY - 0.26) + k * r * W.rootSpread,
      );
      ctx.lineTo(
        cx + dir * r * (W.rootX + (W.tipX - W.rootX) * reach),
        cy + dy + r * (W.tipY - 0.26) + k * r * W.tipSpread,
      );
      ctx.stroke();
    }
  }
  ctx.restore();
}

function drawRaisedPaw(ctx, head, a) {
  // The grooming paw, lifted toward the swung-back head.
  ctx.beginPath();
  ctx.ellipse(head.cx + head.r * 1.05, head.cy + head.r * 1.15, 0.055, 0.09, -0.5, 0, TAU);
  ctx.fillStyle = a.furBase;
  ctx.fill();
  ctx.strokeStyle = a.furShade;
  ctx.lineWidth = OUTLINE_W;
  ctx.stroke();
}

function drawDroplet(ctx, head) {
  ctx.fillStyle = WATER_DROPLET;
  ctx.beginPath();
  ctx.ellipse(head.cx + head.r * 1.15, head.cy + head.r * 0.75, 0.028, 0.04, 0.3, 0, TAU);
  ctx.fill();
}

// ---------------------------------------------------------------------------
// Exports. Namespaced always (the comparison gallery and index.html's
// v1/v2 toggle draw both vocabularies from one page); global drop-in only
// when cat.js is absent, so a page can swap vocabularies by swapping one
// script tag.
// ---------------------------------------------------------------------------

const api = {
  drawCat,
  drawCatTween,
  blendLayouts,
  appearanceFor,
  shadedAppearanceOf,
  catLayout,
  EYE,
  BELLY,
  NOSE,
  MOUTH,
  SWIM,
  SLEEP,
  GAIT,
  POUNCE,
  PROPORTION,
  MAX_LIFT,
  gaitStep,
  pounceWiggle,
  FAR_LEGS,
  AXIAL,
  AXIAL_CAMERAS,
  AXIAL_POSES,
  AXIAL_SWIM,
  WHISKER,
  drawWhiskers,
  INNER_EAR,
  noseInkOf,
  applyAxial,
  FOCUS_VARIANTS,
  BREATH,
  breathCurve,
  // The rig (2026-08-10). Exported so the motion lab can build and drive
  // its own states without anim.js, and so anim.js can hold per-cat state
  // without owning any of the motion maths.
  RIG,
  createRigState,
  stepRig,
  stillRig,
  applyRig,
  turnTransform,
  turnFacing,
  springStep,
  smooth01,
  CAT_GROUND,
  lightenHex,
  mixHex,
  lstar,
  bellyInkOf,
  wetAppearanceOf,
  PUPIL_DILATE_BY_THEME,
  plantedReach,
  proportionLayout,
  pounceLaunch,
  PALETTES,
  POSES,
  // Not cat API, but props.js, meadow.js and app.js quietly depend on
  // these leaking from cat.js's top level (they define no fallbacks of
  // their own). Drop-in mode must leak them too or the first frame dies
  // with "TAU is not defined" and the page white-screens.
  TAU,
  OUTLINE_W,
};
globalThis.CatV2 = api;
if (typeof globalThis.drawCat === 'undefined') {
  Object.assign(globalThis, api);
}
})();
