/**
 * CloudKitty's meadow -- the ground vocabulary (spec 008).
 *
 * Everything here is decoration in the viewer's eye only (Article V): the
 * meadow is a pure function of tile coordinates, ponds redraw exactly the
 * served water tiles, the glow redraws served sunbeams, and worn paths
 * render session-local memory owned by the animation layer. Nothing is
 * predicted, stored, or sent back.
 *
 * Shared conventions with cat.js/props.js: plain script in the common
 * lexical scope, ctx-only drawing, VIEW read at call time so the standalone
 * test harness can run this file with its own tunables fallback.
 */

/* ── palette interpolation (v3, 2026-08-05) ──────────────────────────
   The world used to jump between three frozen palettes. It now crosses
   between them, so the meadow changes light the way a day does rather
   than switching sets. The palettes stay as named colour STRINGS -- every
   drawing call site reads them unchanged -- and the blend parses, mixes
   and re-serialises. That is more work per rebuild than kitten.me's
   [r,g,b] arrays, but it costs nothing per frame: the blend is quantised
   (see app.js) so a palette is rebuilt a few dozen times a transition,
   not sixty times a second.

   Lives here rather than props.js because the standalone meadow harness
   evals cat.js + meadow.js + anim.js only. props.js loads first in the
   browser but calls these later, by which point they are in scope. */

const HEX3 = /^#([0-9a-f])([0-9a-f])([0-9a-f])$/i;
const HEX6 = /^#([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$/i;
const RGB_FN = /^rgba?\(([^)]+)\)$/i;

/** '#abc' | '#aabbcc' | 'rgb(r,g,b)' | 'rgba(r,g,b,a)' -> [r, g, b, a]. */
function parsePaletteColor(value) {
  if (typeof value !== 'string') return null;
  const short = HEX3.exec(value);
  if (short) {
    return [
      parseInt(short[1] + short[1], 16),
      parseInt(short[2] + short[2], 16),
      parseInt(short[3] + short[3], 16),
      1,
    ];
  }
  const long = HEX6.exec(value);
  if (long) {
    return [parseInt(long[1], 16), parseInt(long[2], 16), parseInt(long[3], 16), 1];
  }
  const fn = RGB_FN.exec(value);
  if (fn) {
    const parts = fn[1].split(',').map((n) => parseFloat(n));
    if (parts.length < 3 || parts.some((n) => !Number.isFinite(n))) return null;
    return [parts[0], parts[1], parts[2], parts.length > 3 ? parts[3] : 1];
  }
  return null;
}

function formatPaletteColor([r, g, b, a]) {
  const c = (n) => Math.max(0, Math.min(255, Math.round(n)));
  return a >= 1
    ? `rgb(${c(r)}, ${c(g)}, ${c(b)})`
    : `rgba(${c(r)}, ${c(g)}, ${c(b)}, ${Math.round(a * 1000) / 1000})`;
}

/** Mixes two colour strings. Anything unparseable snaps at the midpoint
 *  rather than throwing -- a palette should never be able to crash a frame. */
function mixPaletteColor(from, to, t) {
  // Exact at both ends, the same guarantee blendLayouts makes for poses: a
  // settled phase is its authored colour string, not a re-serialised
  // approximation of it.
  if (from === to || t <= 0) return from;
  if (t >= 1) return to;
  const a = parsePaletteColor(from);
  const b = parsePaletteColor(to);
  if (!a || !b) return t < 0.5 ? from : to;
  return formatPaletteColor([
    a[0] + (b[0] - a[0]) * t,
    a[1] + (b[1] - a[1]) * t,
    a[2] + (b[2] - a[2]) * t,
    a[3] + (b[3] - a[3]) * t,
  ]);
}

/** Blends two palettes entry by entry: colour strings mix, arrays of them
 *  mix elementwise, numbers lerp (the sun's lean and shadow length), and
 *  anything else takes the nearer end. */
function mixPalettes(A, B, t) {
  if (t <= 0) return A;
  if (t >= 1) return B;
  const out = {};
  for (const key of Object.keys(A)) {
    const from = A[key];
    const to = Object.prototype.hasOwnProperty.call(B, key) ? B[key] : from;
    if (Array.isArray(from) && Array.isArray(to)) {
      out[key] = Object.freeze(from.map((c, i) => mixPaletteColor(c, to[i] ?? c, t)));
    } else if (typeof from === 'number' && typeof to === 'number') {
      out[key] = from + (to - from) * t;
    } else if (typeof from === 'string' && typeof to === 'string') {
      out[key] = mixPaletteColor(from, to, t);
    } else {
      out[key] = t < 0.5 ? from : to;
    }
  }
  return Object.freeze(out);
}

/** Every meadow color, named in one place (spec 008 FR-010, Article VI). */
const MEADOW_DAY = Object.freeze({
  // The ground: close greens, deliberately near the retired checkerboard
  // pair so the world keeps its palette while losing its grid.
  grassTones: Object.freeze(['#e9f3e1', '#e4efd9', '#dfecd4', '#e6f1dc']),
  jitterTint: '#ffffff', // the brighter half of the per-tile jitter
  jitterShade: '#7f9a72', // and the darker half
  // (Flora accents and the edge fringe were scrapped at the gate,
  // 2026-07-20 round 2 -- back on the backlog for a proper art pass.)
  // Water, matching the shipped pool hues so ponds read as the same water.
  pondWater: '#bfe3f2',
  pondShallow: '#daf1fb', // the pale band hugging the inside of the shore
  pondDeep: '#8ab2c7', // the middle, away from any shore
  // The shallow band the depth field fades into, and the surface line at the
  // water's edge. Named per theme rather than mixed toward white at draw
  // time: a fixed push toward white is a daylight assumption, and it made
  // both of these shout in the dim phases (see MEADOW_NIGHT).
  //
  // Day and dusk are the reference, and what they share is NOT a ramp: it is
  // that the shore band sits AT the grass (+1.8 here, -1.8 at dusk) with the
  // meniscus a few L* above it. The depth ramp is then whatever pondDeep
  // leaves underneath. Both carry exactly what the old mixes produced, so
  // they render unchanged; night and dawn were tuned to match them.
  pondShore: '#ebf7fd',
  pondMeniscus: '#f2fafe',
  pondLip: '#b9b288', // damp earth just outside the water
  pondRim: '#9ccfe6',
  lilyPad: '#9fcf8e',
  lilyPadRim: '#84b877',
  // Sunbeam glow stops (radial: core -> mid -> transparent).
  glowCore: 'rgba(255, 231, 150, 0.85)',
  glowMid: 'rgba(255, 226, 138, 0.4)',
  glowFade: 'rgba(255, 226, 138, 0)',
  // Worn paths: bare warm earth showing through the grass.
  pathTint: '#c8b28e',
  // Ground detail (v3): moss patches, the two flower colours, and the
  // shrubs. Worn earth reuses pathTint -- it is the same bare ground.
  moss: '#cfe0c0',
  bloom: '#fbf7ef',
  bloomHeart: '#f2cf7a',
  // The second flower colourway (spec 03 part 3), so a drift has
  // variation inside it rather than one flower repeated.
  bloomCool: '#e9f4f6',
  bloomCoolHeart: '#edb88e',
  bush: '#8ab377',
  bushHi: '#a6c78f',
  // The demoted debug lattice (formerly baked into the ground cache).
  gridLine: 'rgba(140, 170, 130, 0.16)',
  // Dust motes circling in the sunbeams (render.js reads this).
  moteColor: 'rgba(255, 236, 170, 0.75)',
  // The colour the ground takes on the sun's side (spec 03 part 2).
  sunTint: '#fff4d6',
  // The soft ground shadow that seats a cat on the grass (render.js), and
  // where the sun is putting it (v3): `shadowLean` slides it sideways in
  // half-tile units, `shadowLength` stretches it away from the caster.
  // Noon is nearly overhead, so the shadow is short and barely leans.
  groundShadow: 'rgba(140, 120, 100, 0.15)',
  shadowLean: -0.06,
  shadowLength: 1,
});

/**
 * The same meadow after sundown: every hue keeps its identity, just
 * moonlit. Not a dark mode -- greens stay green, water stays water, and
 * the sunbeam stops turn silvery because the light is now the moon's.
 */
const MEADOW_NIGHT = Object.freeze({
  grassTones: Object.freeze(['#3e4a3d', '#39453a', '#344136', '#404d3f']),
  jitterTint: '#9db3d0', // moonlight, where day jitter is white sunlight
  jitterShade: '#1f2922',
  pondWater: '#2f4a5c',
  pondShallow: '#3c5a6d',
  // Night's water was the palette's real outlier, and not in the way the
  // spec feared. Its deep sat 7 L* under the grass where day is 24 under and
  // dusk 29 -- so the pond had no bottom to speak of, and the shore band and
  // meniscus were made to carry the whole read by being far too pale. This
  // is 25 under the grass, day's own relationship.
  pondDeep: '#0b1216',
  // Night is why these are named. Derived, they were a fixed push toward
  // white -- a daylight assumption that put the shore band 19 L* over the
  // grass and the meniscus 21 over it, where day and dusk both sit their
  // shore AT the grass (+1.8 / -1.8) and step the meniscus a few L* above.
  // A pale ring round a dark middle is what "reads as a hole" looks like.
  pondShore: '#334958',
  pondMeniscus: '#3a515f',
  pondLip: '#444134',
  pondRim: '#52748a',
  lilyPad: '#4d6847',
  lilyPadRim: '#3c5439',
  // Moonbeams: the same radial pool, silver instead of gold.
  glowCore: 'rgba(205, 220, 255, 0.55)',
  glowMid: 'rgba(195, 212, 250, 0.28)',
  glowFade: 'rgba(195, 212, 250, 0)',
  pathTint: '#4a4136',
  moss: '#33402f',
  bloom: '#7f8ba0', // moonlit, not white: nothing is lit from above now
  bloomHeart: '#9aa6b8',
  // The second flower colourway (spec 03 part 3), so a drift has
  // variation inside it rather than one flower repeated.
  bloomCool: '#5a7084',
  bloomCoolHeart: '#c1a4ad',
  bush: '#33422f',
  bushHi: '#41533b',
  gridLine: 'rgba(190, 210, 190, 0.14)',
  moteColor: 'rgba(215, 228, 255, 0.8)',
  // The colour the ground takes on the sun's side (spec 03 part 2).
  sunTint: '#d7e4ff',
  // No shadows after dark (owner, 2026-08-05). Expressed as a zero ALPHA
  // rather than a theme special-case, so the shadows fade out as night
  // falls and return with the dawn -- the alpha interpolates along with
  // every other colour, and no drawing code needs to know about night.
  groundShadow: 'rgba(12, 10, 22, 0)',
  // Lean and length still carry values because a crossing interpolates
  // through them: shadows lengthen as they fade at dusk, and come back
  // out of dawn already pointing the right way.
  shadowLean: 0,
  shadowLength: 1.25,
});

/**
 * The meadow at golden hour. Sunset only as of v3 -- dawn was split off
 * into MEADOW_DAWN below, which runs cool and dim where this runs warm
 * and bright. Grass takes an amber wash, the water sits exactly midway between
 * its day and night blues (owner call, 2026-07-22: evening water, not
 * sunset-rose), and the sunbeam pools deepen from noon gold to low-sun
 * amber. Shadows warm and stretch.
 */
const MEADOW_DUSK = Object.freeze({
  grassTones: Object.freeze(['#e6e8c2', '#e0e2bb', '#dadcb3', '#e3e5be']),
  jitterTint: '#fff0d8', // golden light where day jitter is white
  jitterShade: '#8a8a60',
  pondWater: '#9bbdcd', // 75% of the way from night #2f4a5c to day #bfe3f2
  pondShallow: '#b3cbd8', // (owner-tuned, 2026-07-22: evening light lingers
  pondDeep: '#749cb2',
  pondShore: '#d5e2ea',
  pondMeniscus: '#e4edf1',
  pondLip: '#b69f70',
  pondRim: '#8ab8cf', // on the water)
  lilyPad: '#93b183',
  lilyPadRim: '#79996d',
  // Low-sun beams: the same radial pool, deeper amber.
  glowCore: 'rgba(255, 190, 110, 0.85)',
  glowMid: 'rgba(255, 175, 100, 0.4)',
  glowFade: 'rgba(255, 175, 100, 0)',
  pathTint: '#c3a075',
  moss: '#cdd0a0',
  bloom: '#fdf0d8',
  bloomHeart: '#e8b45e',
  // The second flower colourway (spec 03 part 3), so a drift has
  // variation inside it rather than one flower repeated.
  bloomCool: '#d4dcd8',
  bloomCoolHeart: '#e8ab80',
  bush: '#8f9a5f',
  bushHi: '#a9b378',
  gridLine: 'rgba(150, 150, 110, 0.18)',
  moteColor: 'rgba(255, 210, 140, 0.8)',
  // The colour the ground takes on the sun's side (spec 03 part 2).
  sunTint: '#ffce8c',
  groundShadow: 'rgba(120, 80, 90, 0.2)', // long violet-warm evening shadows
  // The sun sets on the RIGHT of the sky dial (skyForTick puts it at
  // t~1 as sunset ends), so shadows are thrown LEFT, away from it.
  shadowLean: -0.85,
  shadowLength: 1.85,
});

/**
 * First light, and the counterweight to golden hour (v3, 2026-08-05).
 * Dawn and dusk shared one palette until now, because ticks have no
 * compass and the light was called "the same, only the direction
 * differs". It is not the same: sunset is the day's warmth draining out
 * through amber, dawn is cold air and a sky that brightens before
 * anything is lit. So this set runs cool where MEADOW_DUSK runs warm --
 * lilac-grey rather than gold, the jitter picking out blue-white first
 * light rather than sunlight, and shadows a cold violet.
 *
 * FIRST CUT -- authored to be dialed, not to be right. Judge it on the
 * meadow at real scale (the theme toggle now stops on Dawn) and paste
 * back whatever it should be.
 */
const MEADOW_DAWN = Object.freeze({
  // Second pass (owner, 2026-08-05). The first cut sat at day's lightness
  // with the saturation pulled out, which read as a washed-out noon
  // rather than an early morning -- and it made the step out of night
  // enormous, the wrong shape for the phase that LEADS out of night. This
  // one drops the value so dawn lands between night and day, and takes
  // the blue back out: the cast was never really in the grass, it was in
  // the jitter, the glow, the motes and the shadow, all of which are now
  // neutral. The sky is lit; the ground is not lit yet.
  grassTones: Object.freeze(['#adb8ab', '#a7b2a5', '#a1ac9f', '#aab5a8']),
  jitterTint: '#f0e9de', // first light: pale, and a touch warm -- the sun
  //                          is coming, even if it has not arrived
  jitterShade: '#5f6a5c',
  pondWater: '#8fa3b0', // water still reads as water, just unlit
  pondShallow: '#a6b8c2',
  pondDeep: '#6d8da1',
  // Dawn ran bright the same way night did, just less far: shore 12 L* over
  // the grass rather than 19. Its deep water is left alone -- at 17 under
  // the grass it still has a bottom, where night's 7 did not.
  pondShore: '#a4b7c3',
  pondMeniscus: '#aec0c9',
  pondLip: '#8b887d',
  pondRim: '#7b8f9c',
  lilyPad: '#7d9184',
  lilyPadRim: '#66786c',
  // The sky brightening before the sun clears the horizon. A hint of
  // warmth rather than silver -- silver is the moon's, and this light is
  // the sun's, just not arrived.
  glowCore: 'rgba(226, 216, 204, 0.62)',
  glowMid: 'rgba(218, 208, 196, 0.3)',
  glowFade: 'rgba(218, 208, 196, 0)',
  pathTint: '#8f867e',
  moss: '#9aa697',
  bloom: '#e8e6df',
  bloomHeart: '#c9bda2',
  // The second flower colourway (spec 03 part 3), so a drift has
  // variation inside it rather than one flower repeated.
  bloomCool: '#c4cdcf',
  bloomCoolHeart: '#d9afa2',
  bush: '#7e8c79',
  bushHi: '#95a18e',
  gridLine: 'rgba(140, 148, 140, 0.16)',
  moteColor: 'rgba(228, 226, 218, 0.75)',
  // The colour the ground takes on the sun's side (spec 03 part 2).
  sunTint: '#eae7de',
  groundShadow: 'rgba(60, 66, 72, 0.24)', // long, cool, but not blue
  // The sun RISES on the left (skyForTick hands the dial t=0 exactly as
  // dawn begins), so shadows are thrown right -- the opposite sign to
  // sunset. This is the one place dawn and sunset differ in geometry
  // rather than only in colour, and it is what stops the two twilights
  // reading as the same hour played twice.
  shadowLean: 0.8,
  shadowLength: 1.8,
});

/**
 * The active palette. Drawing code reads MEADOW as ever; the theme switch
 * (app.js setTheme) swaps which frozen set it names, or blends two of
 * them. The renderer's ground cache is invalidated by the same switch --
 * the cache bakes these colors.
 */
const MEADOW_BY_THEME = Object.freeze({
  day: MEADOW_DAY,
  dusk: MEADOW_DUSK,
  night: MEADOW_NIGHT,
  dawn: MEADOW_DAWN,
});

let MEADOW = MEADOW_DAY;

/** Names the active palette, or a blend of two when the world is between
 *  phases. `t` is how far from `theme` toward `next`. */
function setMeadowPalette(theme, next, t = 0) {
  const from = MEADOW_BY_THEME[theme] ?? MEADOW_DAY;
  if (!next || t <= 0) {
    MEADOW = from;
    return;
  }
  MEADOW = mixPalettes(from, MEADOW_BY_THEME[next] ?? from, t);
}

/** Named salts for peeling independent values off tileHash (research R2). */
const MEADOW_SALTS = Object.freeze({
  tone: 1,
  jitter: 2,
  lily: 7,
  shore: 9,
  // Ground detail (v3). Each scatter needs its own channel, or the
  // patches, blades, blooms and shrubs would all land on the same tiles.
  patch: 11,
  patchKind: 12,
  blade: 13,
  bladeX: 14,
  bladeY: 15,
  bloom: 17,
  bloomX: 18,
  bloomY: 16,
  bush: 19,
  bushShape: 20,
  // Which SILHOUETTE a shrub takes, when two are mixed. Its own channel on
  // purpose: sharing `bushShape` would tie the choice to the lobe angles,
  // so every shrub of one kind would also wear the same shape.
  bushKind: 22,
  // Where in its tile a clump actually stands. Its own channel so nudging
  // one does not also reshape it or change its species.
  bushX: 23,
  // How good this patch of ground is (spec 03). Its own channel, sampled
  // SMOOTH rather than per-tile, and shared by all three scatters -- that
  // sharing is the point: grass, flowers and shrubs thicken in the same
  // places, which is what a drift is.
  fertility: 21,
});

/**
 * The drawing-side stand-ins for VIEW.meadow, used only when the animation
 * layer is absent (the headless harness). VIEW.meadow in anim.js is the
 * authoritative superset -- the harness asserts it stays one.
 */
const MEADOW_DEFAULTS = Object.freeze({
  ponds: true, // merged smooth-shored water (off: per-tile pools)
  glow: true, // sunbeams as radial light (off: plain warm tile)
  paths: true, // whether the worn-paths overlay is available at all
  gridOverlay: true, // whether the grid debug overlay is available at all
  toneSteps: 32, // steps in the ramp blended through the grass tones
  toneCells: 3, // tiles per noise cell: how broad a grass blotch is
  jitterCells: 1.7, // and the finer lattice the brightness grain rides
  toneCells2: 7.5, // a second, broader tone field over the first
  // The ground softens (spec 03 part 2). The tone mosaic is faint but
  // still RECTANGULAR at tile size, and it was the one thing left saying
  // "grid" in a world that otherwise hides its grid. Applied to the tone
  // layer only -- the tufts and flowers are drawn on top of the blur, or
  // 0.32 tiles would not soften a blade of grass, it would erase it.
  groundBlurTiles: 0.32,
  // ...and the ground learns where the sun is. One field-wide wash keyed
  // to `shadowLean`, the same number the cat and shrub shadows read, so
  // the light cannot disagree with itself across the world.
  groundWashSun: 0.3,
  groundWashShade: 0.16,
  jitterAlpha: 0.05, // peak alpha of the per-tile brightness jitter
  patchChance: 0.118, // share of tiles carrying a worn-earth or moss patch
  patchEarthAlpha: 0.03,
  patchMossAlpha: 0.05,
  // Cover grows in DRIFTS (spec 03). The three scatters below used to be
  // independent per-tile rolls, and independent Bernoulli rolls produce a
  // field whose density looks the same through any window you put over it:
  // the eye reads that as texture, never as landscape. There were no
  // PLACES in the meadow. One low-frequency fertility field now gates all
  // three, so thick passages and open ground appear at the same average
  // density -- a redistribution, not more cover.
  //
  // Rarer features take a higher power, so they concentrate harder. That
  // is what makes a thicket read as a thicket rather than as three shrubs
  // standing near each other.
  fertilityCells: 4.5, // tiles per fertility blotch; larger = broader passages
  bladeFertPower: 2,
  bloomFertPower: 3,
  bushFertPower: 4,
  bladeChance: 0.55, // tiles with a tuft of grass
  bladeAlpha: 0.38,
  bloomChance: 0.05, // tiles with a flower
  // How far the lower petals lean toward the flower's heart. Shading them
  // toward BLACK instead only greyed them: a near-white petal has no colour
  // to darken into. Judged in gallery-meadow.html.
  bloomShade: 0.28,
  bushChance: 0.0175, // tiles with a clump of tufted ground cover
  // How far a clump may stand from the middle of its tile, left or right,
  // in tiles. Cover drawn dead on the grid reads as planted rather than
  // grown (owner, 2026-08-13). HORIZONTAL ONLY, deliberately: `coverSortKey`
  // is keyed to y, so sliding a clump sideways cannot disagree with the
  // depth sort. A vertical nudge would have to move the sort key with it.
  bushJitterX: 0.15,
  // How big a clump is, in tiles: the smallest, and how much the shape
  // seed adds on top. The seed drives the lobe angles too, so a clump that
  // differs in size differs in silhouette with it.
  bushSizeMin: 0.2,
  bushSizeSpread: 0.3,
  // How far apart two clumps of the same kind must be in radius, in tiles,
  // before they stop reading as the same clump twice. 0 switches the
  // repel off. Measured on the world that prompted it: the pair that read
  // as a repeat differed by 0.01 tiles, the pair the owner was happy with
  // by 0.09.
  bushSizeMinDiff: 0.07,
  bushAlpha: 0.9, // and how strongly it reads against the grass
  // 'cover' | 'tuft' | 'bramble' (flat) | 'shrub' | 'grown' | 'trunk' |
  // 'tall' | 'lobed' (standing). Judged in gallery-meadow.html.
  bushStyle: 'lobed',
  // A meadow may grow TWO kinds of shrub. `bushStyleAlt` is the second and
  // `bushStyleAltShare` is how much of the population it takes: 0 is the
  // primary alone (and is exactly the behaviour before this existed), 1 is
  // the alt alone, anything between is a mix. Deterministic per tile, so a
  // shrub never changes species between frames.
  //
  // It exists because 'trunk' and the spec's own lobed shrub are both
  // defensible and the argument is not settleable on paper -- this lets a
  // lab session settle it by eye, including at a mix neither side proposed.
  bushStyleAlt: 'trunk',
  bushStyleAltShare: 0.3,
  // How much of the gap between the ground and the canopy the stem covers,
  // for the styles that draw one ('trunk', 'lobed'). 1 is a full stem, 0 is
  // none at all -- and at 0 the canopy is left hanging over its own shadow
  // unless `bushLift` comes down with it, which is the trade this dial
  // exists to let someone see rather than argue about.
  bushTrunk: 0,
  // ...and the SECOND species' own stance, so a meadow can grow small
  // trees among flat cover. Both start where the primary is, so adding
  // these changed nothing until they were dialled (owner, 2026-08-11).
  bushTrunkAlt: 1,
  // How THICK that stem is, as a multiple of the width each style was
  // drawn with -- the trunk style at 0.2 canopy radii, the lobed one
  // at 0.13. A multiplier rather than an absolute, so 1 is exactly the
  // shipped drawing and neither style loses the proportion it was
  // authored with. A small tree wants this well above 1.
  bushTrunkWidth: 2.55,
  bushTrunkWidthAlt: 1.4,
  // How far the lobed shrub's four leaf ticks slide toward the sun, in
  // canopy radii per unit of `shadowLean`. They mark the lit side, but the
  // lobes and the trunk do not move with them, so past a point the motif
  // stops reading as light and starts reading as a part that came loose:
  // at the shipped 0.36 it travelled 0.29 radii between dawn and noon, and
  // the owner caught it as "off centre left" at dawn and "off centre right"
  // at dusk without knowing the two were the same dial. The gradient follows
  // the sun regardless, so this can go to 0 and the shrub is still lit.
  // Judged in the lab's four-phase strip and pasted by the owner
  // (2026-08-16): 0.1, which is about a pixel either side of centre at the
  // live tile -- present as a cue, gone as a displacement.
  bushLeafSwing: 0.1,
  // The shrub's shadow, damped against the cats': a squat canopy sits
  // close to the ground, so it stretches far less and needs no alpha
  // falloff. Only the LENGTH is damped -- the lean also anchors the
  // sun-side edge to the caster, and damping that recentres it.
  bushShadowLean: 1, // gain on the anchor: 1 keeps the sun-side edge on the shrub
  bushShadowLength: 0.3, // and of its stretch past the caster
  bushShadowAlpha: 1, // no thinning: contact, not a smear
  bushLift: 0, // how far a shrub's canopy stands above its base, in radii
  bushLiftAlt: 1.55, // the same, for the bushStyleAlt species
  bushBase: 0.72, // where it meets the ground, in tiles from the tile's top
  // How far the canopy's height pushes its shadow along the lean. Kept
  // small: a rooted thing's shadow leaves its base, and pushing it far
  // is precisely what makes a bush look airborne.
  bushShadowThrow: 0.25,
  // The shoreline. Corners are rounded into arcs first and the wobble rides
  // on the finished curve (buildPondPath); before, the wobble subdivided the
  // edges and capped the radius at 0.25 tile whatever this said.
  // 0.8 rounded a lone tile into a plain circle: the radius clamps to half
  // the shortest edge, and a 1x1 pond's edges are one tile, so anything from
  // 0.5 up was the same circle. 0.35 is back inside the range where the dial
  // bites, and the shape reads as a pond rather than a coin.
  shoreRounding: 0.35, // pond corner rounding, in tiles
  // 0 since the pond restyle: the damp lip and the meniscus took over
  // softening the edge, and measured at our pond sizes the undulation was
  // nearly invisible anyway (a lone tile is identical with it on or off).
  // Not independent of shoreOverdraw -- see wobbleAlong.
  shoreWobble: 0,
  shoreWobblePeriod: 0.35, // and its wavelength around the perimeter, in tiles
  // Scales the OUTWARD bulges only: bays cut the full `shoreWobble`,
  // headlands reach this share of it. See `wobbleAlong`.
  shoreBulgeEase: 0.75,
  shoreOverdraw: 0.1, // push the whole outline out this far, in tiles
  lilyPadMinTiles: 4, // ponds at least this big carry a lily pad
  // --- pond depth (design handoff spec 02) ----------------------------
  // A blurred copy of the pond's own silhouette IS a distance-to-shore
  // field: near the edge the blur bleeds outward and coverage falls, deep
  // inside nothing bleeds in and it stays 1. One blur, no distance
  // transform, and it bakes when buildPondPath is already rebuilding.
  pondDepthBlurTiles: 0.95, // depth-field blur radius, in tiles (a CEILING)
  // ...but the blur must not outrun the pond. Depth at a blob's centre is
  // 1 - exp(-r^2 / 2*sigma^2), so at the shipped 0.95 a lone tile reaches
  // 18% and even our 2x2 lake only 49% -- every pond in this world would
  // run pale. Clamping sigma to inradius/1.8 puts all of them at 80%.
  // The spec was tuned for a fifteen-tile pond; ours are 1 and 4.
  pondDepthBlurClamp: 1.8, // sigma <= inradius / this
  pondLipBlurTiles: 0.42, // blur radius of the damp lip
  pondLipAlpha: 0.8, // how strongly the lip reads
  meniscusWidthTiles: 0.058, // surface line, replacing pondRim's hardcoded 1.5px
  // Ripple lines per pond, scaled by blob area rather than flat: the spec's
  // 8-per-pond costs MORE than the per-tile shimmer it replaces on a world
  // of small blobs (ours: 14 strokes today against 32 polylines).
  //
  // Dialed 2026-08-09: the ceiling now binds at 3 tiles and up, so on every
  // blob this world has except the lone tile and the pair, the CAP sets the
  // count and `causticLinesPerTile` is inert. Kept as the dial anyway --
  // it is what makes a bigger pond busier if the cap is ever raised.
  causticLinesPerTile: 1.6,
  causticLinesMax: 4,
  // Peak white, composited 'lighter'. Landed at well under half the spec's
  // 0.13 with a third of its wave depth: at a 31px tile a ribbon is only a
  // couple of pixels wide, so what reads as "a suggestion of moving water"
  // in a mockup reads as bold white rope in the world.
  causticAlpha: 0.055,
  causticAmplitude: 0.025, // wave depth, in tiles
  glowRadiusTiles: 1.4, // sunbeam glow radius, in tiles
  glowAlpha: 0.6, // overall glow strength
  pathHeatCap: 12, // worn-path heat ceiling per tile (memory, not display)
  pathFullHeat: 3, // passes at which a trail draws at full tint
  pathHalfLifeMs: 60000, // trail fading half-life
  pathVisibilityFloor: 0.4, // decayed heat below this draws nothing
  pathTintAlpha: 0.5, // trail opacity at full heat
});

/** VIEW.meadow when the animation layer is loaded; the stand-ins otherwise. */
function meadowTunables() {
  return (typeof VIEW !== 'undefined' && VIEW.meadow) || MEADOW_DEFAULTS;
}

/**
 * The one deterministic scatter source (research R2): a pure integer
 * bit-mixer over tile coordinates and a named salt, returning [0, 1).
 * Same inputs, same output -- on every reload, restart, and machine
 * (FR-002); no seed, no state, no Math.random anywhere in this file.
 */
function tileHash(x, y, salt = 0) {
  let h = Math.imul(x | 0, 0x9e3779b1) ^ Math.imul(y | 0, 0x85ebca77);
  h ^= Math.imul(salt | 0, 0xc2b2ae3d);
  h = Math.imul(h ^ (h >>> 15), 0x2c1b3c6d);
  h = Math.imul(h ^ (h >>> 12), 0x297a2d39);
  h ^= h >>> 15;
  return (h >>> 0) / 4294967296;
}

/**
 * The organic meadow (US1, FR-001): per-tile base tone and a barely-there
 * brightness jitter, both from tileHash. Drawn once into the ground
 * cache; the per-frame cost stays one blit. (Flora accents were scrapped
 * at the gate, 2026-07-20 round 2 -- deferred to the backlog.)
 */
/**
 * A finer ramp than the four authored tones (v3, 2026-08-05).
 *
 * The ground used to pick one of four discrete tones per tile, so
 * neighbouring tiles differed by a whole step and the meadow read as a
 * mosaic -- the grid spec 008 retired, drawn in colour instead of lines.
 * Blending through the same four tones in `toneSteps` gives tiles that
 * differ by a little rather than a lot, without changing the palette
 * anyone authored.
 *
 * Cached on the tones array's identity: a settled phase reuses one ramp
 * forever, and a blended palette (a fresh frozen array each rebake) pays
 * `toneSteps` mixes rather than one per tile -- 32 against a 20x20 world's
 * 400, so the ramp can be made finer without the rebake noticing. (The
 * figures here were 24 and 576 when the world was 24x24 and the ramp
 * coarser; they are the same argument at any size, since one is a dial and
 * the other is the tile count.)
 */
let GRASS_RAMP = { source: null, steps: 0, ramp: null };

function grassRamp(tones, steps) {
  if (GRASS_RAMP.source === tones && GRASS_RAMP.steps === steps) return GRASS_RAMP.ramp;
  const ramp = new Array(steps);
  for (let s = 0; s < steps; s += 1) {
    const at = (s / steps) * tones.length;
    const i = Math.floor(at) % tones.length;
    ramp[s] = mixPaletteColor(tones[i], tones[(i + 1) % tones.length], at - Math.floor(at));
  }
  GRASS_RAMP = { source: tones, steps, ramp };
  return ramp;
}

/** Half a pixel of overdraw on every side. At fractional tile sizes a
 *  rect edge lands mid-pixel and antialiasing leaves a paler hairline
 *  between neighbours -- which reads as exactly the lattice spec 008
 *  demoted to a debug toggle. Overlapping the neighbour hides it. */
const TILE_BLEED = 0.5;

/**
 * Smooth value noise over the tile grid (v3, 2026-08-05).
 *
 * A per-tile hash gives every tile a tone unrelated to its neighbours, so
 * however fine the ramp, the meadow reads as a mosaic -- shrinking each
 * step only shrinks the checks. What kills it is spatial correlation:
 * sample the hash on a COARSER lattice and interpolate between those
 * corners, and the ground gains soft blotches of lighter and darker
 * grass, the way a real meadow varies, while neighbouring tiles differ by
 * a fraction of a step.
 *
 * Still a pure function of tile coordinates and a salt, so the ground
 * stays identical across reloads, restarts and machines (FR-002) -- the
 * same contract the raw hash carries, just smoothed.
 */
function smoothNoise(x, y, salt, cells) {
  const fx = x / cells;
  const fy = y / cells;
  const x0 = Math.floor(fx);
  const y0 = Math.floor(fy);
  // Smoothstep the cell-local position so the seams between lattice cells
  // have no visible crease -- a plain lerp would leave a gradient kink.
  const sx = easeCell(fx - x0);
  const sy = easeCell(fy - y0);
  const h00 = tileHash(x0, y0, salt);
  const h10 = tileHash(x0 + 1, y0, salt);
  const h01 = tileHash(x0, y0 + 1, salt);
  const h11 = tileHash(x0 + 1, y0 + 1, salt);
  const top = h00 + (h10 - h00) * sx;
  const bottom = h01 + (h11 - h01) * sx;
  return top + (bottom - top) * sy;
}

function easeCell(t) {
  return t * t * (3 - 2 * t);
}

/**
 * A darker version of a palette colour, in ANY format the palette uses.
 *
 * Not cat.js's `shadeHex`, which is where this went wrong: it does
 * `parseInt(hex.slice(1), 16)`, so handed the `rgb(140, 169, 109)` that the
 * palette MIXER emits mid-crossfade it parses garbage, and every channel
 * comes out 0. The result is pure black -- on the shrubs and the flowers,
 * during a phase transition only, healing itself the moment the phase
 * settled back to a hex string (owner, 2026-08-11).
 *
 * Nothing in this file may assume a palette entry is a hex string. Between
 * any two phases it is not.
 */
function shadePalette(color, factor) {
  return mixPaletteColor(color, '#000000', 1 - factor);
}

/** A colour with a chosen alpha, so a palette entry can be washed at one
 *  strength in one place and another elsewhere without storing it twice. */
function withAlpha(color, alpha) {
  const c = parsePaletteColor(color);
  if (!c) return color;
  return formatPaletteColor([c[0], c[1], c[2], c[3] * alpha]);
}

/**
 * Lays the tone field into `paint`, blurs it, and returns it to `ctx`.
 *
 * The mosaic is the thing being dissolved: `grassTones` walked over a noise
 * cell is faint, but at tile size it is still visibly RECTANGULAR, and it
 * was the first thing in the world that said "grid" in a world that
 * otherwise hides its grid.
 *
 * Only the tone layer goes through this. The spec said to blur the whole
 * ground cache, but the cache also holds the tufts and flowers, and 0.32
 * tiles of blur does not soften a blade of grass -- it erases it. Blurring
 * the ground the detail then sits ON is what "the mosaic dissolves into
 * passages" actually asks for.
 *
 * Padded by the blur radius on every side, because a blur reads the
 * transparent space beyond a canvas as transparency and would draw a
 * vignette around the whole meadow.
 */
function blurredLayer(ctx, w, h, radius, paint) {
  const canMake = typeof document !== 'undefined' && typeof document.createElement === 'function';
  if (!(radius > 0.05) || !canMake) {
    paint(ctx, 0, 0);
    return;
  }
  const m = typeof ctx.getTransform === 'function' ? ctx.getTransform() : null;
  const sx = m && m.a ? m.a : 1;
  const sy = m && m.d ? m.d : 1;
  const pad = Math.ceil(radius) + 2;
  const scratch = document.createElement('canvas');
  scratch.width = Math.max(1, Math.ceil((w + pad * 2) * sx));
  scratch.height = Math.max(1, Math.ceil((h + pad * 2) * sy));
  const g = scratch.getContext('2d');
  if (!g) {
    paint(ctx, 0, 0);
    return;
  }
  g.setTransform(sx, 0, 0, sy, 0, 0);
  paint(g, pad, pad);
  ctx.save();
  // A ctx without filter support (or a harness stand-in) still gets the
  // ground, just unsoftened -- never a blank meadow.
  if ('filter' in ctx) ctx.filter = `blur(${radius}px)`;
  ctx.drawImage(scratch, -pad, -pad, w + pad * 2, h + pad * 2);
  ctx.restore();
}

function drawMeadowGround(ctx, { width, height, tile, cover = true }) {
  const t = meadowTunables();
  const ramp = grassRamp(MEADOW.grassTones, t.toneSteps);
  const span = tile + TILE_BLEED * 2;
  const w = width * tile;
  const h = height * tile;

  blurredLayer(ctx, w, h, (t.groundBlurTiles || 0) * tile, (g, ox, oy) => {
    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        const n = smoothNoise(x, y, MEADOW_SALTS.tone, t.toneCells);
        g.fillStyle = ramp[Math.min(ramp.length - 1, Math.floor(n * ramp.length))];
        g.fillRect(ox + x * tile - TILE_BLEED, oy + y * tile - TILE_BLEED, span, span);
        // A second, BROADER tone field over the first. One grain size blurs
        // into mush; two keeps the ground reading as painted rather than as
        // out of focus, which is the failure mode the blur invites.
        if (t.toneCells2) {
          const n2 = smoothNoise(x, y, MEADOW_SALTS.tone, t.toneCells2);
          g.globalAlpha = 0.5;
          g.fillStyle = ramp[Math.min(ramp.length - 1, Math.floor(n2 * ramp.length))];
          g.fillRect(ox + x * tile - TILE_BLEED, oy + y * tile - TILE_BLEED, span, span);
          g.globalAlpha = 1;
        }
        // The jitter stays finer-grained than the tone -- it is the grass's
        // own texture rather than the ground's shape -- but smoothed too,
        // on a tighter lattice, so it grains the meadow instead of tiling it.
        const j = smoothNoise(x, y, MEADOW_SALTS.jitter, t.jitterCells);
        g.globalAlpha = t.jitterAlpha * Math.abs(j * 2 - 1);
        g.fillStyle = j < 0.5 ? MEADOW.jitterShade : MEADOW.jitterTint;
        g.fillRect(ox + x * tile - TILE_BLEED, oy + y * tile - TILE_BLEED, span, span);
        g.globalAlpha = 1;
      }
    }
  });

  // One field-wide wash, so the whole meadow knows where the sun is. Keyed
  // to `shadowLean` -- the same number the cat and shrub shadows read -- so
  // the light can never disagree with itself across the world. At noon the
  // lean is near zero and this is a faint top-to-bottom gradient; at dusk
  // it rakes hard across the field.
  if (typeof ctx.createLinearGradient === 'function' && (t.groundWashSun || t.groundWashShade)) {
    const lean = MEADOW.shadowLean || 0;
    const sun = withAlpha(MEADOW.sunTint || MEADOW.glowCore, t.groundWashSun);
    const shade = withAlpha(MEADOW.jitterShade, t.groundWashShade);
    // The sun sits on the side the shadows point AWAY from.
    const dx = -Math.max(-1, Math.min(1, lean));
    const wash = ctx.createLinearGradient(
      w * (0.5 - dx * 0.5), 0,
      w * (0.5 + dx * 0.5), h,
    );
    wash.addColorStop(0, sun);
    wash.addColorStop(0.55, withAlpha(MEADOW.sunTint || MEADOW.glowCore, 0));
    wash.addColorStop(1, shade);
    ctx.fillStyle = wash;
    ctx.fillRect(0, 0, w, h);
  }

  drawGroundDetail(ctx, { width, height, tile, t });
  // Ground cover is drawn here only for callers that are not sorting
  // it themselves (the lab, the harness). render.js passes false and
  // draws it interleaved with the cats -- see bushesFor/drawBushAt.
  if (cover) drawGroundCover(ctx, { width, height, tile, t });
}

/**
 * What makes it a meadow rather than a green field (v3, 2026-08-05):
 * worn earth and moss, tufts of grass, the odd flower, and low shrubs.
 * This is the flora that was scrapped at the 2026-07-20 gate and sent to
 * the backlog -- back now that phase 1 gave the tiles the size to carry
 * it, and softened so it reads as ground rather than as sprites.
 *
 * Every layer is a sparse scatter over the tile grid from its own salt,
 * so it is deterministic and it never lands on the same tiles as another
 * layer. Patches and shrubs are drawn from the tile CENTRE and are wider
 * than a tile on purpose: crossing the boundaries is what stops them
 * re-drawing the grid the tone work just removed.
 *
 * All of it bakes into the ground cache, so it costs nothing per frame.
 */
function drawGroundDetail(ctx, { width, height, tile, t }) {
  // Cover grows in drifts (spec 03): the same fertility field gates the
  // tufts, the flowers and the shrubs, so they thicken together.
  const drift = driftField(width, height, t);
  // --- worn earth and moss: broad, soft, crossing tile lines ---
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      if (tileHash(x, y, MEADOW_SALTS.patch) < 1 - t.patchChance) continue;
      const k = tileHash(x, y, MEADOW_SALTS.patchKind);
      const earth = k > 0.62;
      const r = (0.9 + k * 1.7) * tile * 0.5;
      ctx.globalAlpha = earth ? t.patchEarthAlpha : t.patchMossAlpha;
      ctx.fillStyle = earth ? MEADOW.pathTint : MEADOW.moss;
      ctx.beginPath();
      ctx.ellipse((x + 0.5) * tile, (y + 0.5) * tile, r, r * 0.66, k * 3, 0, TAU);
      ctx.fill();
    }
  }
  ctx.globalAlpha = 1;

  // --- grass tufts: three blades each, leaning away from the sun ---
  //
  // Everything here is a fraction of a TILE. The old tuft was one stroke at
  // a fixed pixel length, which is the same fault that retired grass sway
  // in the first place: fixed-pixel blades read as stray diagonal lines the
  // moment the tile is small. Being tile-proportional is also the
  // precondition for bringing sway back -- the drawing that was wrong is
  // the drawing being replaced.
  //
  // Three passes rather than three strokes per tuft: each blade index gets
  // its own colour and width, so batching by INDEX keeps the whole meadow
  // to three stroked paths instead of three per tuft.
  const bladeLean = Math.max(-1, Math.min(1, MEADOW.shadowLean ?? 0));
  ctx.lineCap = 'round';
  for (let b = 0; b < 3; b++) {
    const step = b / 2; // 0 = the near blade, 1 = the far one
    // Stepping the colour across the three gives the tuft a near and a far
    // edge, which is what stops it reading as a flat scribble.
    ctx.strokeStyle = step < 0.5 ? MEADOW.bush : MEADOW.bushHi;
    ctx.lineWidth = Math.max(0.6, tile * 0.032 * (1 - step * 0.25));
    ctx.globalAlpha = t.bladeAlpha * (1 - step * 0.2);
    ctx.beginPath();
    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        const n = tileHash(x, y, MEADOW_SALTS.blade);
        if (n < 1 - drift.blade[y * width + x]) continue;
        const bx = (x + tileHash(x, y, MEADOW_SALTS.bladeX)) * tile;
        const by = (y + tileHash(x, y, MEADOW_SALTS.bladeY)) * tile;
        // Fanned around the root, so the three read as one plant.
        const fan = (b - 1) * 0.5 + (n - 0.5) * 0.4;
        const high = tile * (0.13 + n * 0.08) * (1 - step * 0.22);
        const tipX = bx + fan * tile * 0.12 + bladeLean * high * 0.5;
        ctx.moveTo(bx + fan * tile * 0.03, by);
        ctx.quadraticCurveTo(
          bx + fan * tile * 0.06 + bladeLean * high * 0.15,
          by - high * 0.6,
          tipX,
          by - high,
        );
      }
    }
    ctx.stroke();
  }
  ctx.globalAlpha = 1;

  // --- flowers: five petals and a heart, at every tile size.
  //
  //     The 44px gate is GONE, 2026-08-18, along with the one the cats and
  //     the bowl's decal carried. The owner judged fine detail legible at
  //     21px and chose to draw it at every size rather than keep a
  //     resolution threshold anyone has to reason about again. Raised in
  //     review of PR #246, where this was the last one standing: the cats
  //     had stopped gating, so with the camera off at a 32px tile they wore
  //     full face detail while every flower was a bare dot. ---
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      if (tileHash(x, y, MEADOW_SALTS.bloom) < 1 - drift.bloom[y * width + x]) continue;
      const k = tileHash(x, y, MEADOW_SALTS.bloomX);
      const bx = (x + 0.25 + k * 0.5) * tile;
      // Its own channel, not the tuft's: sharing `blade` tied a flower's
      // height in its tile to whether that tile also grew grass, so
      // every bloom in the upper part of the band sat on bare ground
      // and every one below it sat in a tuft.
      const by = (y + 0.25 + tileHash(x, y, MEADOW_SALTS.bloomY) * 0.5) * tile;
      const r = tile * (0.085 + k * 0.03);
      // Two colourways off the SAME seed, so a drift has variation inside
      // it rather than one flower repeated across the whole meadow. The
      // cool pair is a named palette entry per theme, not a draw-time mix:
      // mixing toward a fixed colour is the daylight assumption the pond
      // restyle retired, and it would be wrong at night in exactly the
      // same way.
      const cool = tileHash(x, y, MEADOW_SALTS.bloomY) > 0.62;
      const petal = cool ? MEADOW.bloomCool || MEADOW.bloom : MEADOW.bloom;
      const heart = cool ? MEADOW.bloomCoolHeart || MEADOW.bloomHeart : MEADOW.bloomHeart;
      {
        // A stem, so the flower grows out of the ground instead of lying
        // on it. Drawn first and leaning with the light, like the blades.
        ctx.strokeStyle = MEADOW.bush;
        ctx.globalAlpha = 0.75;
        ctx.lineWidth = Math.max(0.6, tile * 0.022);
        ctx.beginPath();
        ctx.moveTo(bx - (MEADOW.shadowLean ?? 0) * r * 0.4, by + r * 2.1);
        ctx.quadraticCurveTo(bx, by + r * 1.1, bx, by + r * 0.5);
        ctx.stroke();
        ctx.globalAlpha = 1;
        for (let i = 0; i < 5; i++) {
          const a = (i / 5) * TAU + k * 3;
          const dy = Math.sin(a);
          // The lower petals sit in the flower's own shade, which is what
          // gives it a top and a bottom rather than a flat rosette.
          // Shaded toward the flower's own HEART, not toward black.
          //
          // These petals are near-white -- the warm bloom is L* 97 -- and a
          // near-white has almost no colour to darken INTO, so mixing it
          // toward black can only produce grey. That read as a dirty lower
          // half rather than as a shaded one (owner, 2026-08-11). Same
          // shape as the seal point's belly: lightening an almost-white fur
          // toward white has very little to give.
          //
          // A real flower's lower petals catch bounce off the centre, so
          // the heart is both the physically right direction and the one
          // that keeps some chroma on the way down.
          // Toward a DARKENED heart, so the lower half loses lightness as
          // well as gaining colour. Toward the plain heart it only tinted:
          // the heart is barely darker than the petal, so the flower read
          // warmer at the bottom without reading shaded.
          ctx.fillStyle = dy > 0.2
            ? mixPaletteColor(petal, shadePalette(heart, 0.74), t.bloomShade)
            : petal;
          ctx.beginPath();
          ctx.arc(bx + Math.cos(a) * r * 0.78, by + dy * r * 0.78, r * 0.62, 0, TAU);
          ctx.fill();
        }
        ctx.fillStyle = heart;
        ctx.beginPath();
        ctx.arc(bx, by, r * 0.42, 0, TAU);
        ctx.fill();
      }
    }
  }

}

/**
 * The scrubby growth between the grass -- in one of four vocabularies,
 * named by `bushStyle` so the meadow lab dials exactly what ships
 * (gallery-meadow.html).
 *
 * The constraint that shapes all of them: this bakes into the ground
 * cache, which sits under EVERYTHING. Nothing in the renderer y-sorts --
 * elements draw before cats, always -- so a cat crossing one of these
 * draws on top of it. Anything that reads as standing UP off the ground
 * therefore reads wrong the moment a cat walks through it, which is why
 * the shipped default lies flat. `shrub` is kept anyway, because seeing
 * the failure is the fastest way to judge whether a sorted sprite layer
 * is worth building.
 */
function drawGroundCover(ctx, { width, height, tile, t, occupied }) {
  for (const bush of bushesFor(width, height, t, occupied)) {
    drawBushAt(ctx, { ...bush, tile, t });
  }
}

/**
 * Where the ground cover grows: a pure, deterministic scatter over the
 * tile grid, so the same world always grows the same shrubs (FR-002).
 *
 * `occupied` is the set of tiles the server has put something on --
 * bowls, water, critters. Cover skips them. That is only possible because
 * this is evaluated per frame against the served state rather than baked
 * into the ground cache, and it is what keeps a bowl from sprouting a
 * shrub through it without needing elements in the sort order too.
 */
/**
 * The drift field: per-tile odds for each scatter, clustered but conserving
 * the flat scatter's average density (spec 03).
 *
 * The spec proposed a closed-form normaliser -- `chance = base * (p+1) *
 * f^p`, from `E[f^p] = 1/(p+1)` for f uniform on 0..1 -- and warned that
 * value noise is not uniform so the constant would come out low. Measured,
 * it is worse than low: it is world-size DEPENDENT. A 20x20 world spans
 * only ~3.6 fertility cells, so the field's mean is whatever that handful
 * of lattice corners happens to be and never converges. The multiplier
 * that conserves density measured 29.1 at 20x20, 32.2 at 24x24 and 9.4 at
 * 64x64 -- so any baked constant is right for exactly one world.
 *
 * So it is SOLVED per field instead, by bisection on the one number that
 * matters: the multiplier k where mean(min(1, k*f^p)) equals the flat
 * chance it replaces. That makes acceptance criterion 1 -- density is
 * conserved, this is a redistribution and not a content change -- true by
 * construction at every world size, and it absorbs the clamp for free.
 * The clamp is intended: inside a drift every tile has a tuft.
 *
 * Memoised because `bushesFor` runs once per FRAME (render.js draws shrubs
 * in the sorted sprite layer so they y-sort against cats), while this is a
 * pure function of the world's size and these tunables.
 */
const DRIFT_CACHE = new Map();

function driftField(width, height, t) {
  const key = [
    width, height, t.fertilityCells,
    t.bladeChance, t.bladeFertPower,
    t.bloomChance, t.bloomFertPower,
    t.bushChance, t.bushFertPower,
  ].join(':');
  const hit = DRIFT_CACHE.get(key);
  if (hit) return hit;

  const n = width * height;
  const f = new Float64Array(n);
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      f[y * width + x] = smoothNoise(x, y, MEADOW_SALTS.fertility, t.fertilityCells);
    }
  }

  const chancesFor = (base, power, salt) => {
    const out = new Float64Array(n);
    if (!(base > 0)) return out;
    // Matched against the count the flat scatter ACTUALLY produced, not
    // against `base`. Those are not the same number and the gap is not
    // small: at 20x20 the shrub roll fires on 13 tiles where 0.015 x 400
    // predicts 6, because a few hundred tiles is far too small a sample
    // for the hash to look uniform out at a 1.5% threshold. Normalising to
    // the nominal rate therefore CUT shrubs by 38% while reporting itself
    // as conserved. Acceptance criterion 1 measures against the current
    // algorithm's counts, so that is what this solves for.
    const hash = new Float64Array(n);
    let target = 0;
    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        const i = y * width + x;
        hash[i] = tileHash(x, y, salt);
        if (hash[i] >= 1 - base) target++;
      }
    }
    if (!target) return out;
    const countAt = (k) => {
      let c = 0;
      for (let i = 0; i < n; i++) {
        const ch = k * Math.pow(f[i], power);
        if (hash[i] >= 1 - (ch > 1 ? 1 : ch)) c++;
      }
      return c;
    };
    // countAt rises monotonically with k and saturates at n, so bracket
    // then bisect for the smallest k that reaches the target. A degenerate
    // field (every tile zero) can never get there; fall back to the flat
    // chance rather than drawing nothing.
    let hi = 1;
    while (countAt(hi) < target && hi < 1e12) hi *= 4;
    if (countAt(hi) < target) {
      out.fill(base);
      return out;
    }
    let lo = 0;
    for (let i = 0; i < 60; i++) {
      const mid = (lo + hi) / 2;
      if (countAt(mid) < target) lo = mid;
      else hi = mid;
    }
    for (let i = 0; i < n; i++) {
      const c = hi * Math.pow(f[i], power);
      out[i] = c > 1 ? 1 : c;
    }
    return out;
  };

  const field = {
    width,
    fertility: f,
    blade: chancesFor(t.bladeChance, t.bladeFertPower, MEADOW_SALTS.blade),
    bloom: chancesFor(t.bloomChance, t.bloomFertPower, MEADOW_SALTS.bloom),
    bush: chancesFor(t.bushChance, t.bushFertPower, MEADOW_SALTS.bush),
  };
  // Bounded: one entry per world size and dial set, and the dials only move
  // in the lab. Cleared wholesale rather than aged -- there is never more
  // than a handful.
  if (DRIFT_CACHE.size > 24) DRIFT_CACHE.clear();
  DRIFT_CACHE.set(key, field);
  return field;
}

/** Does this species stand up off the ground, or lie on it? */
function coverStands(t, alt) {
  return (alt ? t.bushLiftAlt : t.bushLift) > 0 || (alt ? t.bushTrunkAlt : t.bushTrunk) > 0;
}

function bushesFor(width, height, t, occupied) {
  const out = [];
  const drift = driftField(width, height, t);
  const jitter = t.bushJitterX || 0;
  for (let y = 0; y < height; y++) {
    // The last clump placed in THIS row, for the size-repel below. Reset
    // per row, and x runs left to right, so "the previous one" is the
    // neighbour the eye pairs it with.
    let prev = null;
    for (let x = 0; x < width; x++) {
      if (tileHash(x, y, MEADOW_SALTS.bush) < 1 - drift.bush[y * width + x]) continue;
      if (occupied && occupied.has(`${x},${y}`)) continue;

      // Which species, decided HERE rather than at draw time, because only
      // this function knows where the map ends.
      let alt = (t.bushStyleAltShare || 0) > 0
        && tileHash(x, y, MEADOW_SALTS.bushKind) < t.bushStyleAltShare;
      // A standing one needs headroom, and the top row has none: its canopy
      // reaches about 0.38 tiles above its own tile and is cut off by the
      // edge of the world (owner, 2026-08-13). So the top row grows the
      // species that LIES DOWN. Keyed on which one stands rather than on
      // "the alt", because which of the two is the tree has already flipped
      // once. If both stand there is nothing better to offer, so the roll
      // stands.
      if (y === 0 && coverStands(t, alt) && !coverStands(t, !alt)) alt = !alt;

      // ...and a small sideways nudge off the grid, clamped so the clump's
      // own CANOPY stays on the map -- the same "keep it on the map" rule
      // as the row above, one axis over.
      //
      // Clamped on the canopy rather than the centre because a clump is
      // wider than its tile: the lobes reach about 1.14 radii, so at the
      // widest size that is 0.57 tiles against a half-tile of 0.5. Holding
      // only the centre inside the outermost tile centres let the biggest
      // clumps hang a couple of pixels off the left and right edges, which
      // is the top-row complaint again at a smaller scale.
      // Two clumps of the SAME kind, near enough in size, read as one
      // clump stamped twice -- the owner's report (2026-08-13), measured
      // at two bushes in a row whose radii differed by 0.2px. Widening the
      // size range does not fix it: two tiles that hash to nearly the same
      // seed stay nearly the same at any spread.
      //
      // So when the previous clump in this row is the same kind and within
      // `bushSizeMinDiff` of this one, the seed takes a half turn. That is
      // provably enough -- if |s - p| < T then |s' - p| >= 0.5 - T -- and
      // one shift always suffices, so there is no loop here. The seed
      // drives the lobe angles too, so the pair ends up differing in
      // silhouette as well as in size.
      //
      // Same kind only: a tree standing beside a bush of its own size
      // reads fine, and the owner said so.
      let seed = tileHash(x, y, MEADOW_SALTS.bushShape);
      const minDiff = t.bushSizeMinDiff || 0;
      if (prev && prev.alt === alt
        && Math.abs(seed - prev.seed) * t.bushSizeSpread < minDiff) {
        seed = (seed + 0.5) % 1;
      }
      prev = { alt, seed };

      const reach = 1.14 * (t.bushSizeMin + seed * t.bushSizeSpread);
      let ox = (tileHash(x, y, MEADOW_SALTS.bushX) - 0.5) * 2 * jitter;
      // No `min(0, ...)` on the low end: a clump wider than half a tile
      // hangs off the edge at its tile centre, so the clamp has to be able
      // to push it INWARD, not merely stop it drifting further out.
      const lo = reach - (x + 0.5);
      const hi = width - (x + 0.5) - reach;
      ox = Math.max(lo, Math.min(hi, ox));

      out.push({ x, y, ox, alt, seed });
    }
  }
  return out;
}

/**
 * Depth-sort keys, in tiles measured from a tile's top edge.
 *
 * Shared so the renderer and the meadow lab cannot disagree about what
 * "in front" means. Both are GROUND CONTACT points, because that is what
 * decides which of two things is nearer: a cat's ground line sits 88% down
 * its box (the same 0.88 the landing settle and the header wordmark use),
 * and a shrub's is its base, below the canopy standing up off it.
 */
const CAT_GROUND_LINE = 0.88;

function catSortKey(pos) {
  return pos.y + CAT_GROUND_LINE;
}

function coverSortKey(bush, t) {
  return bush.y + t.bushBase;
}

/**
 * Who wins when two things meet the ground on exactly the same line.
 *
 * Ground contact decides depth, but a cat and a butterfly sharing a tile
 * contact it at the same place, so the key alone leaves them tied and the
 * order falls to whichever loop happened to push first. That is a real
 * ordering, decided by accident. This is the same ordering, decided on
 * purpose. Cover is scenery and goes behind. A kitty is the subject and
 * comes to the front. Between them stand the props a cat walks up to (a
 * bowl), then the critters, which are in the air over both.
 */
const SPRITE_RANK = { cover: 0, prop: 1, critter: 2, kitty: 3 };

/**
 * The depth layer, ordered. Pure so the ordering can be tested without a
 * canvas: what goes wrong here is invisible in any single draw call and
 * only shows as one thing painted over another.
 */
function spriteOrder(items) {
  return [...items].sort(
    (a, b) => a.y - b.y || (SPRITE_RANK[a.kind] ?? 0) - (SPRITE_RANK[b.kind] ?? 0),
  );
}

/** One clump, at tile coordinates. Split out of the scatter so the
 *  renderer can interleave these with the cats by depth. */
/** Styles whose silhouette leaves the ground, and so cast a shadow. The
 *  flat ones lie on it and would only look like they stand. */
const STANDING_COVER = new Set(['shrub', 'grown', 'trunk', 'tall', 'lobed']);

function drawBushAt(ctx, { x, y, ox, alt, seed, tile: tileSize, t: tunables }) {
  // Which of the two this one is, and where in its tile it stands. Both are
  // decided by `bushesFor`, which knows the map's edges; the fallbacks are
  // for hand-made clumps (the lab draws one at a time, off any map).
  //
  // Drawn from their own channels so the choices are independent of the
  // shape seed, and from (x, y) so they are stable for the life of the
  // world -- scenery that changed species or place between frames is the
  // flicker `occupiedTiles` was narrowed to avoid.
  const share = tunables.bushStyleAltShare || 0;
  const isAlt = alt === undefined
    ? share > 0 && tileHash(x, y, MEADOW_SALTS.bushKind) < share
    : alt;
  const nudge = ox === undefined ? 0 : ox;
  const style = isAlt
    ? tunables.bushStyleAlt || tunables.bushStyle || 'cover'
    : tunables.bushStyle || 'cover';
  // The two species carry their OWN stance (owner, 2026-08-11): a meadow
  // may grow one cover that stands on a trunk and one that lies on the
  // ground. Style already differed per species; how far it stands up did
  // not, so both were flat or both were lifted and "trees among shrubs"
  // was unreachable.
  //
  // Applied as an overlay on the tunables rather than threaded through the
  // eight places the style switch reads `bushLift`/`bushTrunk` -- and the
  // shadow reads them too, so an overlay is the only way the shadow can
  // stay honest about the height it is cast by. Same shape the lab already
  // uses to draw one species at a time.
  const t = isAlt
    ? {
        ...tunables,
        bushLift: tunables.bushLiftAlt,
        bushTrunk: tunables.bushTrunkAlt,
        bushTrunkWidth: tunables.bushTrunkWidthAlt,
      }
    : tunables;
  const tile = tileSize;
  {
    {
      const s = seed;
      const bx = (x + 0.5 + nudge) * tile;
      const by = (y + 0.5) * tile;
      // Size, as a dial rather than two constants (owner, 2026-08-13:
      // "two places where similar sized bushes on the same row look a
      // little off"). The old 0.26 + s*0.18 gave 8.1 to 13.6px at a 31px
      // tile, and with a dozen-odd clumps drawn independently from a 5.5px
      // range, two landing within a pixel of each other is not bad luck --
      // it is the expected spacing. Widening does not change the collision
      // RATE, it changes how far apart two colliding clumps look.
      const r = (t.bushSizeMin + s * t.bushSizeSpread) * tile;
      // Where this thing meets the earth. The shadow is centred here, so
      // anything standing must be planted here too -- drawing from the
      // tile centre instead left the trunk stopping 0.4 radii short of
      // its own shadow, which reads as hovering (owner, 2026-08-05).
      const groundY = by + r * 0.52;

      // Anything that stands up off the ground casts; the flat styles
      // have nothing to cast onto and would only look like they stand.
      if (STANDING_COVER.has(style)) {
        // The leaning shadow that says a thing stands up.
        //
        // Damped against the cats' (owner, 2026-08-05: "too dramatic").
        // A shrub is squat and its canopy sits close to the ground, so it
        // throws a far shorter shadow than a standing cat does under the
        // same low sun -- and because it is no longer long, the alpha does
        // not have to be spread thin to stay believable.
        //
        // The damping applies to LENGTH only. `lean` does two jobs here:
        // it says which way the shadow goes, and it anchors the sun-side
        // edge to the caster (the same `lean * (halfWidth - footprint)`
        // the cats use). Damping it damped the anchor too, which recentred
        // the shadow under the shrub -- the bug this fixes.
        // `bushShadowLean` is therefore a gain on that anchor, not a
        // brake on the sun: 1 keeps the sun-side edge on the shrub.
        const lean = (MEADOW.shadowLean ?? 0) * t.bushShadowLean;
        const sunLength = MEADOW.shadowLength ?? 1;
        const length = 1 + (sunLength - 1) * t.bushShadowLength;
        // The alpha falloff keys on the SUN's lowness, not on how long we
        // chose to draw this shadow. The palettes' groundShadow alphas
        // climb into twilight (0.15 day, 0.20 sunset, 0.24 dawn) precisely
        // BECAUSE the cats divide them by their length -- authored to land
        // near 0.15 either way. Taking the raw value, as this did while
        // its own length was damped short, made a twilight shrub 33-60%
        // darker than a midday one and concentrated it besides (owner,
        // 2026-08-05: "too intense during dusk/dawn"). Spreading light
        // over more ground is a fact about the light; the drawn length is
        // an art choice, and must not be the thing that sets the alpha.
        ctx.globalAlpha = t.bushShadowAlpha / Math.max(1, sunLength * 0.8);
        ctx.fillStyle = MEADOW.groundShadow;
        // Two terms, and the second is what makes the shadow belong to a
        // canopy that stands UP rather than to a flat patch:
        //
        //   anchor  keeps the sun-side edge on the caster, as the cats' does
        //   throw   displaces it by the canopy's HEIGHT along the lean --
        //           a tall thing's shadow falls further from its base than
        //           a short one's under the same sun, which is the whole
        //           reason a lifted canopy needs its shadow moved at all
        const canopyLift = r * t.bushLift;
        const offset = lean * (r * length - r) + lean * canopyLift * t.bushShadowThrow;
        ctx.beginPath();
        ctx.ellipse(bx + offset, groundY, r * length, r * 0.3, 0, 0, TAU);
        ctx.fill();
      }

      if (style === 'shrub') {
        // The canopy stands ABOVE the base rather than sitting on it, so
        // the shrub occupies the tile above its own -- which is the only
        // way a cat can be behind one. Its shadow stays at the base: that
        // is where it meets the ground, and where the depth sort keys it.
        const lift = r * t.bushLift;
        ctx.globalAlpha = t.bushAlpha;
        ctx.fillStyle = MEADOW.bush;
        // A skirt at the base FIRST, so the silhouette is continuous from
        // the ground up. Without it a lifted canopy hangs over its own
        // shadow with clear air between, which reads as hovering -- the
        // butterfly's trick, and deliberate there, but wrong for
        // something rooted (owner, 2026-08-05).
        ctx.beginPath();
        ctx.ellipse(bx, by + r * 0.08, r * 0.58, r * 0.44, 0, 0, TAU);
        ctx.fill();
        for (let i = 0; i < 4; i++) {
          const a = (i / 4) * TAU + s * 5;
          ctx.beginPath();
          ctx.arc(bx + Math.cos(a) * r * 0.42, by - lift + Math.sin(a) * r * 0.34, r * 0.62, 0, TAU);
          ctx.fill();
        }
        ctx.globalAlpha = t.bushAlpha * 0.5;
        ctx.fillStyle = MEADOW.bushHi;
        ctx.beginPath();
        ctx.arc(bx - r * 0.22, by - lift - r * 0.3, r * 0.3, 0, TAU);
        ctx.fill();
      } else if (style === 'grown') {
        // PROPOSAL 1 -- grow, do not lift. Lobes are distributed from the
        // base upward over a height set by bushLift, tapering as they go,
        // so the silhouette fills its whole height by construction. No
        // gap is possible at any lift: the lowest lobe always sits on the
        // ground. `bushLift` stops meaning "how high off the ground" and
        // starts meaning "how tall".
        const height = r * (0.5 + t.bushLift);
        ctx.globalAlpha = t.bushAlpha;
        ctx.fillStyle = MEADOW.bush;
        const lobes = 5;
        for (let i = 0; i < lobes; i++) {
          const up = (i / (lobes - 1)) * height;
          const taper = 1 - 0.34 * (i / (lobes - 1));
          const sway = Math.cos(i * 2.3 + s * 7) * r * 0.3;
          ctx.beginPath();
          ctx.ellipse(bx + sway, groundY - r * 0.46 - up, r * 0.58 * taper, r * 0.46 * taper, 0, 0, TAU);
          ctx.fill();
        }
        ctx.globalAlpha = t.bushAlpha * 0.5;
        ctx.fillStyle = MEADOW.bushHi;
        ctx.beginPath();
        ctx.ellipse(bx - r * 0.18, groundY - r * 0.46 - height * 0.85, r * 0.24, r * 0.18, 0, 0, TAU);
        ctx.fill();
      } else if (style === 'trunk') {
        // PROPOSAL 2 -- own the gap. A stem connects the raised canopy to
        // the ground, so the height reads as structure rather than as
        // levitation. Reads as a standard or a young tree, not a bush.
        // Measured from groundY, so the stem ends in the middle of its
        // own shadow rather than in the air above it.
        const crown = groundY - r * t.bushLift - r * 0.3;
        ctx.globalAlpha = t.bushAlpha;
        ctx.fillStyle = MEADOW.bush;
        const stemShare = t.bushTrunk === undefined ? 1 : t.bushTrunk;
        if (stemShare > 0) {
          const top = groundY - (groundY - crown) * stemShare;
          ctx.beginPath();
          // Authored at 0.2 radii; the dial scales it rather than
          // replacing it, so the two styles keep the different trunks
          // they were drawn with and 1 is exactly today.
          const w = r * 0.2 * (t.bushTrunkWidth ?? 1);
          ctx.rect(bx - w / 2, top, w, groundY - top);
          ctx.fill();
        }
        // The canopy, then the LIGHT across it (spec 03 part 3). The lobes
        // and their offsets are unchanged: the spec's own constraint is
        // that the silhouette and its bounding shape stay put, so
        // `coverSortKey` keeps answering the same and the occlusion
        // behaviour dialled in the meadow lab is preserved exactly. Only
        // the shading is new.
        //
        // (The spec described today's shrub as one ellipse plus a
        // highlight and gave lobe geometry to match. That is the 'cover'
        // style; 'trunk' is what ships. Replacing this silhouette with
        // that one would have broken the very thing the spec asked to
        // preserve, so the lighting is applied to the shipped shape.)
        const lobes = [];
        for (let i = 0; i < 4; i++) {
          const a = (i / 4) * TAU + s * 5;
          const lx = bx + Math.cos(a) * r * 0.38;
          const ly = crown + Math.sin(a) * r * 0.3;
          lobes.push([lx, ly]);
          ctx.beginPath();
          ctx.arc(lx, ly, r * 0.55, 0, TAU);
          ctx.fill();
        }
        // Clipped to the canopy's own union, so the gradient cannot spill
        // past the silhouette and change its shape.
        const lean = Math.max(-1, Math.min(1, MEADOW.shadowLean ?? 0));
        const sunX = -lean; // the sun is the side the shadows point away from
        if (typeof ctx.createLinearGradient === 'function') {
          ctx.save();
          ctx.beginPath();
          for (const [lx, ly] of lobes) {
            ctx.moveTo(lx + r * 0.55, ly);
            ctx.arc(lx, ly, r * 0.55, 0, TAU);
          }
          ctx.clip();
          const g = ctx.createLinearGradient(
            bx + sunX * r, crown - r, bx - sunX * r, crown + r,
          );
          g.addColorStop(0, withAlpha(MEADOW.bushHi, 0.95));
          g.addColorStop(0.5, withAlpha(MEADOW.bushHi, 0.25));
          g.addColorStop(1, withAlpha(
            shadePalette(MEADOW.bush, 0.72), 0.55,
          ));
          ctx.globalAlpha = t.bushAlpha;
          ctx.fillStyle = g;
          ctx.fillRect(bx - r * 1.2, crown - r * 1.2, r * 2.4, r * 2.4);
          ctx.restore();
        }
        // A few leaf ticks, on the lit side only -- the cheapest thing
        // that says "leaves" rather than "a green blob with a gradient".
        ctx.globalAlpha = t.bushAlpha * 0.6;
        // meadow.js's OWN mixer, not cat-v2's mixHex. cat-v2 leaks nothing
        // unless it is in drop-in mode, so a bare mixHex here is undefined
        // in gallery-meadow.html -- guarded, therefore silent, therefore
        // exactly the trap that had the axial views shipping inert.
        ctx.fillStyle = mixPaletteColor(MEADOW.bushHi, '#ffffff', 0.35);
        for (let i = 0; i < 4; i++) {
          const a = (i / 4) * TAU + s * 9;
          const lx = bx + sunX * r * 0.3 + Math.cos(a) * r * 0.34;
          const ly = crown + Math.sin(a) * r * 0.3;
          ctx.beginPath();
          ctx.ellipse(lx, ly, r * 0.14, r * 0.08, a, 0, TAU);
          ctx.fill();
        }
      } else if (style === 'lobed') {
        // The spec's own shrub (03 part 3), built to its numbers: three
        // overlapping lobes at the offsets and scales it names, clipped to
        // their union and lit across from the sun's side, with leaf ticks
        // on the lit side and a short trunk leaning away from the light.
        //
        // Offered as a SECOND species rather than as a replacement. The
        // spec describes the shrub it is redrawing as "one ellipse plus a
        // highlight", which is the 'cover' style -- but 'trunk' is what
        // ships, and swapping the silhouette would have broken the one
        // thing the spec insisted on preserving. Both now exist and
        // `bushStyleAltShare` decides the mix (owner's call, 2026-08-10).
        const lift = r * t.bushLift;
        const crown = groundY - lift - r * 0.3;
        const lean = Math.max(-1, Math.min(1, MEADOW.shadowLean ?? 0));
        const sunX = -lean;
        // A short trunk first, leaning AWAY from the light, so the canopy
        // has something to stand on and reaches its own shadow.
        ctx.globalAlpha = t.bushAlpha;
        const stem = t.bushTrunk === undefined ? 1 : t.bushTrunk;
        if (stem > 0) {
          const top = groundY - (groundY - crown) * stem;
          ctx.strokeStyle = shadePalette(MEADOW.bush, 0.72);
          // Same multiplier, this style's own 0.13. The 1px floor is a
          // legibility clamp, so a thin dial stops biting below it.
          ctx.lineWidth = Math.max(1, r * 0.13 * (t.bushTrunkWidth ?? 1));
          ctx.lineCap = 'round';
          ctx.beginPath();
          ctx.moveTo(bx, groundY);
          ctx.lineTo(bx + lean * r * 0.14 * stem, top);
          ctx.stroke();
        }
        // The canopy: the spec's three lobes, in canopy radii.
        const LOBES = [[-0.42, 0.06, 0.62], [0.4, 0.1, 0.58], [-0.02, -0.34, 0.72]];
        ctx.fillStyle = shadePalette(MEADOW.bush, 0.94);
        for (const [ox, oy, scale] of LOBES) {
          ctx.beginPath();
          ctx.arc(bx + ox * r, crown + oy * r, r * scale, 0, TAU);
          ctx.fill();
        }
        if (typeof ctx.createLinearGradient === 'function') {
          ctx.save();
          ctx.beginPath();
          for (const [ox, oy, scale] of LOBES) {
            ctx.moveTo(bx + ox * r + r * scale, crown + oy * r);
            ctx.arc(bx + ox * r, crown + oy * r, r * scale, 0, TAU);
          }
          ctx.clip();
          const g = ctx.createLinearGradient(
            bx + sunX * r * 1.1, crown - r, bx - sunX * r * 1.1, crown + r,
          );
          g.addColorStop(0, withAlpha(MEADOW.bushHi, 0.95));
          g.addColorStop(0.5, withAlpha(MEADOW.bushHi, 0.25));
          g.addColorStop(1, withAlpha(shadePalette(MEADOW.bush, 0.72), 0.55));
          ctx.fillStyle = g;
          ctx.fillRect(bx - r * 1.6, crown - r * 1.6, r * 3.2, r * 3.2);
          ctx.restore();
        }
        ctx.globalAlpha = t.bushAlpha * 0.6;
        ctx.fillStyle = mixPaletteColor(MEADOW.bushHi, '#ffffff', 0.35);
        // Four ticks, evenly spaced, so their cos terms cancel exactly and
        // the motif's centre is purely the swing term -- which is why it
        // reads as a clean sideways displacement rather than a rotation.
        const swing = t.bushLeafSwing ?? 0.36;
        for (let i = 0; i < 4; i++) {
          const a = (i / 4) * TAU + s * 9;
          ctx.beginPath();
          ctx.ellipse(
            bx + sunX * r * swing + Math.cos(a) * r * 0.3,
            crown - r * 0.1 + Math.sin(a) * r * 0.26,
            r * 0.13, r * 0.075, a, 0, TAU,
          );
          ctx.fill();
        }
      } else if (style === 'tall') {
        // PROPOSAL 3 -- one silhouette, stretched. A single rounded body
        // rising from the ground with lobed bumps on its crown, rather
        // than a cluster of circles. Height is the shape's own
        // proportion, so it scales to any lift without ever separating.
        const height = r * (0.8 + t.bushLift * 1.1);
        ctx.globalAlpha = t.bushAlpha;
        ctx.fillStyle = MEADOW.bush;
        ctx.beginPath();
        ctx.ellipse(bx, groundY - height * 0.55, r * 0.6, height * 0.55, 0, 0, TAU);
        ctx.fill();
        for (let i = 0; i < 3; i++) {
          const off = (i - 1) * r * 0.36;
          ctx.beginPath();
          ctx.ellipse(bx + off, groundY - height * (0.85 + 0.1 * Math.cos(i + s * 5)),
            r * 0.3, r * 0.26, 0, 0, TAU);
          ctx.fill();
        }
        ctx.globalAlpha = t.bushAlpha * 0.5;
        ctx.fillStyle = MEADOW.bushHi;
        ctx.beginPath();
        ctx.ellipse(bx - r * 0.2, groundY - height * 0.82, r * 0.22, r * 0.3, 0.3, 0, TAU);
        ctx.fill();
      } else if (style === 'tuft') {
        // A fan of blades from one root: long grass rather than a bush.
        // Nothing to stand on, so a cat crossing it reads as wading.
        ctx.globalAlpha = t.bushAlpha;
        ctx.strokeStyle = MEADOW.bush;
        ctx.lineWidth = Math.max(1, tile * 0.045);
        ctx.lineCap = 'round';
        ctx.beginPath();
        for (let i = 0; i < 7; i++) {
          const spread = (i / 6 - 0.5) * 1.5;
          ctx.moveTo(bx + spread * r * 0.5, by + r * 0.3);
          ctx.quadraticCurveTo(
            bx + spread * r * 0.9,
            by - r * 0.2,
            bx + spread * r * 1.5 + (s - 0.5) * r * 0.6,
            by - r * (0.5 + s * 0.4),
          );
        }
        ctx.stroke();
      } else if (style === 'bramble') {
        // A scatter of small leaves: texture rather than a silhouette,
        // and the least bothered of the four by being walked over.
        ctx.globalAlpha = t.bushAlpha;
        ctx.fillStyle = MEADOW.bush;
        for (let i = 0; i < 9; i++) {
          const a = (i / 9) * TAU + s * 7;
          const d = 0.25 + ((i * 37) % 11) / 11 * 0.75;
          ctx.beginPath();
          ctx.ellipse(
            bx + Math.cos(a) * r * d,
            by + Math.sin(a) * r * d * 0.6,
            r * 0.24,
            r * 0.16,
            a,
            0,
            TAU,
          );
          ctx.fill();
        }
      } else {
        // 'cover' -- the shipped default: flattened overlapping lobes,
        // lying on the ground, casting nothing. A cat standing on it
        // reads as a cat on a denser patch of grass, which is true.
        ctx.globalAlpha = t.bushAlpha;
        ctx.fillStyle = MEADOW.bush;
        for (let i = 0; i < 4; i++) {
          const a = (i / 4) * TAU + s * 5;
          ctx.beginPath();
          ctx.ellipse(
            bx + Math.cos(a) * r * 0.42,
            by + Math.sin(a) * r * 0.26,
            r * 0.62,
            r * 0.42,
            0,
            0,
            TAU,
          );
          ctx.fill();
        }
        ctx.globalAlpha = t.bushAlpha * 0.5;
        ctx.fillStyle = MEADOW.bushHi;
        ctx.beginPath();
        ctx.ellipse(bx - r * 0.22, by - r * 0.22, r * 0.3, r * 0.2, 0, 0, TAU);
        ctx.fill();
      }
      ctx.globalAlpha = 1;
    }
  }
}

/**
 * The demoted lattice (US1, FR-004): the exact grid the old ground cache
 * baked in, now drawn per frame only while the debug toggle is on.
 */
function drawGridOverlay(ctx, { width, height, tile }) {
  ctx.save();
  ctx.strokeStyle = MEADOW.gridLine;
  ctx.lineWidth = 1;
  ctx.beginPath();
  for (let x = 0; x <= width; x++) {
    ctx.moveTo(x * tile + 0.5, 0);
    ctx.lineTo(x * tile + 0.5, height * tile);
  }
  for (let y = 0; y <= height; y++) {
    ctx.moveTo(0, y * tile + 0.5);
    ctx.lineTo(width * tile, y * tile + 0.5);
  }
  ctx.stroke();
  ctx.restore();
}

/**
 * The largest circle that fits inside a blob, in tiles.
 *
 * Needed because the depth field is a blurred silhouette, and a blur wider
 * than the pond has nothing to be deep in the middle of: depth at a blob's
 * centre is `1 - exp(-r^2 / 2*sigma^2)`, so at the spec's 0.95 a lone tile
 * reaches 18% and a 2x2 lake 49%. Sigma is clamped to this over
 * `pondDepthBlurClamp`, which puts every shape we have at ~80%.
 *
 * Sampled on a half-tile lattice rather than derived from tile COUNT: area
 * would call a 1-wide four-tile channel (a river, the shape we know is
 * coming) as roomy as a 2x2 lake, and it is the one blob that most needs a
 * tight blur. Blobs are a handful of tiles, and this runs once per cache
 * rebuild, so walking the lattice costs nothing.
 */
function pondInradius(tiles) {
  const inSet = new Set(tiles.map((p) => `${p.x},${p.y}`));
  const xs = tiles.map((p) => p.x);
  const ys = tiles.map((p) => p.y);
  // Every cell that is NOT water, out to a ring around the blob. The
  // nearest one bounds the circle -- measured as point-to-rectangle, so a
  // reentrant corner counts. An axis-ray version was tried and cut: it
  // read an L as 0.88 tiles when the true answer is 0.18, because the
  // nearest boundary is diagonal and no ray ever meets it.
  const out = [];
  for (let x = Math.min(...xs) - 2; x <= Math.max(...xs) + 2; x++) {
    for (let y = Math.min(...ys) - 2; y <= Math.max(...ys) + 2; y++) {
      if (!inSet.has(`${x},${y}`)) out.push([x, y]);
    }
  }
  const toCell = (px, py, cx, cy) => {
    const dx = Math.max(cx - px, 0, px - (cx + 1));
    const dy = Math.max(cy - py, 0, py - (cy + 1));
    return Math.hypot(dx, dy);
  };
  const STEP = 0.125;
  let best = 0;
  for (const { x, y } of tiles) {
    for (let sx = STEP / 2; sx < 1; sx += STEP) {
      for (let sy = STEP / 2; sy < 1; sy += STEP) {
        let d = Infinity;
        for (const [cx, cy] of out) {
          d = Math.min(d, toCell(x + sx, y + sy, cx, cy));
          if (d <= best) break; // cannot beat the incumbent
        }
        best = Math.max(best, d);
      }
    }
  }
  return best || 0.5;
}

/**
 * Ponds, step one (US2, research R4): group water tile positions into
 * 4-adjacent blobs. Pure data-in data-out; order-independent.
 */
function groupWaterTiles(positions) {
  const key = (x, y) => `${x},${y}`;
  const remaining = new Map();
  for (const p of positions) remaining.set(key(p.x, p.y), { x: p.x, y: p.y });
  const groups = [];
  for (const [seedKey] of remaining) {
    if (!remaining.has(seedKey)) continue;
    const seed = remaining.get(seedKey);
    remaining.delete(seedKey);
    const group = [seed];
    const queue = [seed];
    while (queue.length) {
      const { x, y } = queue.pop();
      for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
        const k = key(x + dx, y + dy);
        const next = remaining.get(k);
        if (!next) continue;
        remaining.delete(k);
        group.push(next);
        queue.push(next);
      }
    }
    groups.push(group);
  }
  return groups;
}

/**
 * Ponds, step two (US2, research R4): trace the blob's boundary (marching
 * squares over the tile set -- directed edges chained into loops, so a
 * ring pond gets an outer loop and an opposite-winding hole loop, which
 * nonzero fill renders correctly), then round every corner with quadratic
 * curves at the named shore radius. Returns a Path2D in pixels.
 */
function buildPondPath(tiles, tile) {
  const t = meadowTunables();
  const inSet = new Set(tiles.map((p) => `${p.x},${p.y}`));
  const has = (x, y) => inSet.has(`${x},${y}`);

  // Directed boundary edges between grid points (tile-unit coordinates),
  // oriented so the water stays on one consistent side.
  const edges = new Map(); // "sx,sy" -> array of [ex, ey]
  const addEdge = (sx, sy, ex, ey) => {
    const k = `${sx},${sy}`;
    if (!edges.has(k)) edges.set(k, []);
    edges.get(k).push([ex, ey]);
  };
  for (const { x, y } of tiles) {
    if (!has(x, y - 1)) addEdge(x, y, x + 1, y); // top, walking right
    if (!has(x + 1, y)) addEdge(x + 1, y, x + 1, y + 1); // right, down
    if (!has(x, y + 1)) addEdge(x + 1, y + 1, x, y + 1); // bottom, left
    if (!has(x - 1, y)) addEdge(x, y + 1, x, y); // left, up
  }

  // Chain edges into closed loops. At a pinch point (two loops sharing a
  // grid corner) prefer the sharpest right turn, which keeps each loop
  // hugging its own water.
  const loops = [];
  for (const [startKey, list] of edges) {
    while (list.length) {
      const [sx, sy] = startKey.split(',').map(Number);
      let [ex, ey] = list.pop();
      const loop = [[sx, sy]];
      let px = sx;
      let py = sy;
      while (ex !== sx || ey !== sy) {
        loop.push([ex, ey]);
        const outs = edges.get(`${ex},${ey}`) ?? [];
        if (!outs.length) break; // malformed input; bail on this loop
        let pick = 0;
        if (outs.length > 1) {
          const inx = ex - px;
          const iny = ey - py;
          let best = -Infinity;
          outs.forEach(([ox, oy], i) => {
            // cross > 0 is a right turn in screen coordinates (y down).
            const cross = inx * (oy - ey) - iny * (ox - ex);
            if (cross > best) {
              best = cross;
              pick = i;
            }
          });
        }
        const [nx, ny] = outs.splice(pick, 1)[0];
        px = ex;
        py = ey;
        ex = nx;
        ey = ny;
      }
      if (loop.length >= 4) loops.push(simplifyLoop(loop));
    }
  }

  const path = new Path2D();
  for (const loop of loops) {
    // Round the corners FIRST, into a dense polyline, then wobble that.
    // The old order did the reverse and the two fought: wobbling split every
    // edge into half-tile segments, and the corner radius clamps to half a
    // segment, so a 1x1 pond could never round further than 0.25 tile no
    // matter what `shoreRounding` said. It read as a rounded square and the
    // tunable did nothing above 0.5.
    let points = sampleRoundedLoop(loop, t.shoreRounding);
    points = wobbleAlong(points, t.shoreWobble, t.shoreWobblePeriod, t.shoreBulgeEase, loop[0]);
    points = growOutward(points, t.shoreOverdraw);
    smoothClosedPath(path, points, tile);
  }
  return path;
}

/**
 * Walk a corner loop and sample the arc-rounded outline into a dense
 * polyline, in tile units.
 *
 * True circular arcs, not the quadratic-with-the-corner-as-control-point
 * this replaces: at the same radius a quadratic bulges ~6% past the arc and
 * leaves flats either side of it, which is most of why ponds read square.
 * The radius still clamps to half of each adjoining edge, so a 1x1 pond
 * tops out at a circle and a 2x2 needs 1.0 to get there.
 */
function sampleRoundedLoop(corners, rounding, step = 0.22) {
  const n = corners.length;
  const raw = [];
  // Consecutive duplicates are not harmless here. Where the radius uses up a
  // whole edge -- a 1x1 pond at rounding >= 0.5, where the arcs meet exactly
  // at the edge midpoints -- one corner's end point IS the next one's start,
  // and a repeated point gives the wobble a zero-length tangent, hence a
  // garbage normal and a spike in the outline.
  const pts = {
    push(p) {
      const last = raw[raw.length - 1];
      if (last && Math.abs(last[0] - p[0]) < 1e-9 && Math.abs(last[1] - p[1]) < 1e-9) return;
      raw.push(p);
    },
  };
  if (n < 3) return corners.map((c) => c.slice());
  const unit = (a, b) => {
    const dx = b[0] - a[0];
    const dy = b[1] - a[1];
    const len = Math.hypot(dx, dy) || 1;
    return { ux: dx / len, uy: dy / len, len };
  };
  const geom = corners.map((v, i) => {
    const prev = corners[(i - 1 + n) % n];
    const next = corners[(i + 1) % n];
    const inc = unit(prev, v);
    const out = unit(v, next);
    const r = Math.min(rounding, inc.len / 2, out.len / 2);
    // Which side the turn goes decides where the arc's centre sits.
    const turn = Math.sign(inc.ux * out.uy - inc.uy * out.ux) || 1;
    const t1 = [v[0] - inc.ux * r, v[1] - inc.uy * r];
    const t2 = [v[0] + out.ux * r, v[1] + out.uy * r];
    const nx = -inc.uy * turn;
    const ny = inc.ux * turn;
    return { r, t1, t2, cx: t1[0] + nx * r, cy: t1[1] + ny * r };
  });
  for (let i = 0; i < n; i++) {
    const g = geom[i];
    if (g.r > 1e-6) {
      const a1 = Math.atan2(g.t1[1] - g.cy, g.t1[0] - g.cx);
      const a2 = Math.atan2(g.t2[1] - g.cy, g.t2[0] - g.cx);
      let sweep = a2 - a1;
      while (sweep > Math.PI) sweep -= Math.PI * 2;
      while (sweep < -Math.PI) sweep += Math.PI * 2;
      const steps = Math.max(2, Math.ceil((Math.abs(sweep) * g.r) / step));
      for (let k = 0; k <= steps; k++) {
        const a = a1 + sweep * (k / steps);
        pts.push([g.cx + Math.cos(a) * g.r, g.cy + Math.sin(a) * g.r]);
      }
    } else {
      pts.push(g.t1.slice());
    }
    const to = geom[(i + 1) % n].t1;
    const run = unit(g.t2, to);
    const steps = Math.max(1, Math.round(run.len / step));
    for (let k = 1; k < steps; k++) {
      pts.push([g.t2[0] + run.ux * run.len * (k / steps), g.t2[1] + run.uy * run.len * (k / steps)]);
    }
  }
  // The loop closes on itself, so the last point can duplicate the first.
  const first = raw[0];
  const last = raw[raw.length - 1];
  if (raw.length > 1 && Math.abs(first[0] - last[0]) < 1e-9 && Math.abs(first[1] - last[1]) < 1e-9) {
    raw.pop();
  }
  return raw;
}

/**
 * Displace a sampled outline along its own normals, with smooth 1-D noise
 * around the perimeter rather than a hash per point.
 *
 * Per-point hashing (what this replaces) gives neighbouring samples
 * independent values, so the edge chatters at the sampling frequency instead
 * of undulating. Here the noise is drawn at a coarse lattice around the loop
 * and smoothstepped between, so the whole shoreline moves together, and the
 * lattice wraps so the seam is invisible.
 *
 * `bulgeEase` scales the OUTWARD half -- the headlands that push away from
 * the water. Bays cut the full `amp`; headlands reach `bulgeEase * amp`. So
 * lower flattens the seaward bulges and leaves only bays, higher lets the
 * headlands out.
 *
 * Which half is which is not obvious from the arithmetic, so: with the
 * winding the tile walk produces, `(-ty, tx)` points INTO the water. A
 * positive noise value is therefore an inward bay, and it is the negative
 * half that `value *= bulgeEase` reaches. (This shipped for a while as
 * `shoreDipEase`, documented as easing the bays -- the opposite of what it
 * does. Renamed 2026-08-07; the numbers were always the ones the owner
 * dialled and are unchanged.)
 *
 * The same sign carries into the mean: the outline is biased INWARD by
 * `0.25 * amp * (1 - bulgeEase)` on average, so it eats into `shoreOverdraw`
 * rather than riding on top of it -- the two are not independent. At the
 * shipped 0.08 / 0.75 / 0.1 that is 0.005 tile off a 0.1 tile spill.
 */
function wobbleAlong(points, amp, period, bulgeEase, seed) {
  if (!amp) return points;
  const n = points.length;
  let perimeter = 0;
  for (let i = 0; i < n; i++) {
    const a = points[i];
    const b = points[(i + 1) % n];
    perimeter += Math.hypot(b[0] - a[0], b[1] - a[1]);
  }
  const cells = Math.max(4, Math.round(perimeter / Math.max(0.05, period)));
  const salt = MEADOW_SALTS.shore;
  const lattice = (i) => tileHash(((i % cells) + cells) % cells, seed[0] * 13 + seed[1] * 7, salt);
  const ease = (u) => u * u * (3 - 2 * u);
  const out = [];
  let walked = 0;
  for (let i = 0; i < n; i++) {
    const u = (walked / perimeter) * cells;
    const cell = Math.floor(u);
    const frac = u - cell;
    let value = (lattice(cell) + (lattice(cell + 1) - lattice(cell)) * ease(frac) - 0.5) * 2;
    if (value < 0) value *= bulgeEase;
    const prev = points[(i - 1 + n) % n];
    const next = points[(i + 1) % n];
    const tx = next[0] - prev[0];
    const ty = next[1] - prev[1];
    const len = Math.hypot(tx, ty) || 1;
    out.push([points[i][0] + (-ty / len) * value * amp, points[i][1] + (tx / len) * value * amp]);
    const b = points[(i + 1) % n];
    walked += Math.hypot(b[0] - points[i][0], b[1] - points[i][1]);
  }
  return out;
}

/**
 * Push the outline outward along its normals, so the water reaches past the
 * flat edges of its tiles instead of stopping short of them.
 *
 * Rounding costs a pond the corners of its own tiles -- unavoidable, since a
 * circle inscribed in a square leaves 0.207 tile at each corner -- and this
 * buys some of it back. It spills the same distance everywhere, so corner
 * grass and edge spill move together: it cannot fill one without the other.
 * Owner accepted the spill (2026-08-07); it also means more of a water tile
 * reads as water, which helps a wading cat look like it is in the pond.
 *
 * Which way is "out" depends on the loop's winding, and the loops here come
 * from an edge walk that does not guarantee one, so pick the direction that
 * grows the loop's SIGNED area.
 *
 * Signed, not absolute. A ring pond traces an outer loop and an
 * opposite-winding hole loop (see `buildPondPath`), and on |area| both of
 * them grow away from their own centre -- so the island swelled by
 * `shoreOverdraw` and ate 0.1 tile of water, instead of the hole tightening
 * and giving 0.1 tile back. Signed area gets both: it grows the outer loop
 * and shrinks the hole, which is "more water" in each case.
 */
function growOutward(points, amount) {
  if (!amount) return points;
  const n = points.length;
  const push = (sign) =>
    points.map((p, i) => {
      const prev = points[(i - 1 + n) % n];
      const next = points[(i + 1) % n];
      const tx = next[0] - prev[0];
      const ty = next[1] - prev[1];
      const len = Math.hypot(tx, ty) || 1;
      return [p[0] + (-ty / len) * amount * sign, p[1] + (tx / len) * amount * sign];
    });
  const area = (pts) => {
    let sum = 0;
    for (let i = 0; i < pts.length; i++) {
      const a = pts[i];
      const b = pts[(i + 1) % pts.length];
      sum += a[0] * b[1] - b[0] * a[1];
    }
    return sum / 2;
  };
  const outward = push(1);
  const inward = push(-1);
  return area(outward) > area(inward) ? outward : inward;
}

/** Draw a closed curve through the points: quadratics via segment midpoints,
 * which is continuous at every joint, so the wobble reads as undulation
 * rather than as a polygon with a lot of corners. */
function smoothClosedPath(path, points, tile) {
  const n = points.length;
  if (n < 3) return;
  const mid = (a, b) => [((a[0] + b[0]) / 2) * tile, ((a[1] + b[1]) / 2) * tile];
  const start = mid(points[n - 1], points[0]);
  path.moveTo(start[0], start[1]);
  for (let i = 0; i < n; i++) {
    const v = points[i];
    const to = mid(v, points[(i + 1) % n]);
    path.quadraticCurveTo(v[0] * tile, v[1] * tile, to[0], to[1]);
  }
  path.closePath();
}


/** Merge collinear runs so rounding only happens at true corners. */
function simplifyLoop(points) {
  const out = [];
  const n = points.length;
  for (let i = 0; i < n; i++) {
    const [ax, ay] = points[(i - 1 + n) % n];
    const [bx, by] = points[i];
    const [cx, cy] = points[(i + 1) % n];
    if ((bx - ax) * (cy - by) - (by - ay) * (cx - bx) !== 0) {
      out.push(points[i]);
    }
  }
  return out;
}


/**
 * Ponds, step three (US2): fill + rim the cached shoreline paths; larger
 * ponds carry one hash-placed lily pad (FR-005).
 */
/**
 * The pond's depth field, damp lip and surface, baked into two layers.
 *
 * A blurred copy of a pond's own silhouette IS a distance-to-shore field:
 * near the edge the blur bleeds outward and coverage falls toward a half,
 * deep inside nothing bleeds in and it stays 1. So one blur buys depth --
 * no distance transform, no per-pixel loop.
 *
 * **Two layers for the whole world, not two per pond.** The spec offered
 * a pair of offscreens per pond; at our backing-store size that is ~19MB
 * each, and this world has four blobs -- ~153MB against ~38MB. Each pond
 * is built in a scratch and composited in, so the buffers are shared while
 * the CONTENT stays per-pond, which matters because every pond gets its
 * own blur radius (see `pondInradius`).
 *
 * Built where `buildPondPath` is already rebuilding, so per-frame cost is
 * two `drawImage` calls.
 */
function buildPondLayers(ponds, { tile, widthPx, heightPx, dpr }) {
  const t = meadowTunables();
  const make = () => {
    const c = document.createElement('canvas');
    c.width = widthPx;
    c.height = heightPx;
    const g = c.getContext('2d');
    g.setTransform(dpr, 0, 0, dpr, 0, 0);
    return { c, g };
  };
  const shore = make();
  const lip = make();
  const scratch = make();
  const mask = make();
  const cssW = widthPx / dpr;
  const cssH = heightPx / dpr;
  const clear = (l) => l.g.clearRect(0, 0, cssW, cssH);

  for (const pond of ponds) {
    // Sigma is clamped by the pond's own inradius: a blur wider than the
    // pond has nothing to be deep in the middle of.
    const radius = pondInradius(pond.tiles);
    const sigma =
      Math.min(t.pondDepthBlurTiles, radius / t.pondDepthBlurClamp) * tile;

    clear(mask);
    mask.g.fillStyle = '#fff';
    mask.g.fill(pond.path);

    // Shore: pale everywhere the water is, then the blurred silhouette
    // punched out of it. What survives is strongest where it is shallow.
    clear(scratch);
    scratch.g.fillStyle = MEADOW.pondShore;
    scratch.g.fill(pond.path);
    scratch.g.save();
    scratch.g.globalCompositeOperation = 'destination-out';
    scratch.g.filter = `blur(${sigma}px)`;
    scratch.g.drawImage(mask.c, 0, 0, cssW, cssH);
    scratch.g.restore();
    shore.g.drawImage(scratch.c, 0, 0, cssW, cssH);

    // Lip: the blurred silhouette stamped in damp earth, with the sharp
    // path punched out -- a soft ring that exists only OUTSIDE the water.
    clear(scratch);
    scratch.g.save();
    scratch.g.filter = `blur(${t.pondLipBlurTiles * tile}px)`;
    scratch.g.drawImage(mask.c, 0, 0, cssW, cssH);
    scratch.g.restore();
    scratch.g.save();
    scratch.g.globalCompositeOperation = 'source-in';
    scratch.g.fillStyle = MEADOW.pondLip;
    scratch.g.fillRect(0, 0, cssW, cssH);
    scratch.g.globalCompositeOperation = 'destination-out';
    scratch.g.fill(pond.path);
    scratch.g.restore();
    lip.g.drawImage(scratch.c, 0, 0, cssW, cssH);
  }
  // The scratches are the peak, not the resting cost; drop them here.
  return { shore: shore.c, lip: lip.c, dpr };
}

/**
 * Ripple lines across a pond, replacing the per-tile shimmer.
 *
 * Count scales with the blob rather than being flat: the spec's 8-per-pond
 * was costed against a fifteen-tile pond, and on a world of small blobs it
 * comes to MORE work than the shimmer it replaces (ours: 14 strokes today
 * against 32 polylines). Scaled, a lone tile gets two.
 */
function drawCaustics(ctx, pond, tile, now) {
  const t = meadowTunables();
  const xs = pond.tiles.map((p) => p.x);
  const ys = pond.tiles.map((p) => p.y);
  const x0 = Math.min(...xs) * tile;
  const x1 = (Math.max(...xs) + 1) * tile;
  const y0 = Math.min(...ys) * tile;
  const y1 = (Math.max(...ys) + 1) * tile;
  const lines = Math.max(
    1,
    Math.min(t.causticLinesMax, Math.round(pond.tiles.length * t.causticLinesPerTile)),
  );
  const amp = t.causticAmplitude * tile;
  ctx.save();
  ctx.globalCompositeOperation = 'lighter';
  ctx.strokeStyle = `rgba(255, 255, 255, ${t.causticAlpha})`;
  ctx.lineCap = 'round';
  for (let i = 0; i < lines; i++) {
    const seat = (i + 0.5) / lines;
    const drift = Math.sin(now / 4200 + i * 1.7) * amp * 0.9;
    ctx.lineWidth = Math.max(0.6, tile * 0.03 * (1 + 0.35 * Math.sin(now / 2600 + i)));
    ctx.beginPath();
    for (let k = 0; k <= 12; k++) {
      const u = k / 12;
      const px = x0 + (x1 - x0) * u;
      const py = y0 + (y1 - y0) * seat + drift + Math.sin(now / 1500 + k * 0.9 + i * 2.1) * amp;
      k ? ctx.lineTo(px, py) : ctx.moveTo(px, py);
    }
    ctx.stroke();
  }
  ctx.restore();
}

function drawPonds(ctx, { ponds, tile, layers = null, now = 0, motion = true, clip = null }) {
  const t = meadowTunables();
  ctx.save();
  // `clip` is the visible rectangle in this layer's own pixel space --
  // NOT named `window`, which would shadow the global for the whole
  // function body and hand a silent rect to anyone later reaching for
  // `window.devicePixelRatio` in here.
  // or null for "all of it" (spec 036). The layers are baked at world
  // size, which under a camera is several times the canvas -- blitting
  // the whole thing every frame means scaling an image of which most
  // pixels fall outside the frame. `blitGround` was given a source rect
  // for exactly this reason; these had been left without one.
  const blit = (layer) => {
    const w = layer.width / layers.dpr;
    const h = layer.height / layers.dpr;
    if (!clip) {
      ctx.drawImage(layer, 0, 0, w, h);
      return;
    }
    const sx = Math.max(0, Math.min(clip.x, w));
    const sy = Math.max(0, Math.min(clip.y, h));
    const sw = Math.min(clip.w, w - sx);
    const sh = Math.min(clip.h, h - sy);
    if (sw <= 0 || sh <= 0) return;
    ctx.drawImage(layer, sx * layers.dpr, sy * layers.dpr, sw * layers.dpr, sh * layers.dpr, sx, sy, sw, sh);
  };
  // The damp ring first: it lives outside the water, on the grass.
  if (layers) {
    ctx.globalAlpha = t.pondLipAlpha;
    blit(layers.lip);
    ctx.globalAlpha = 1;
  }
  for (const pond of ponds) {
    // A deep middle to sit the shore band on. Without the layers (a caller
    // that has not baked them) this is the flat pond we always had.
    ctx.fillStyle = layers ? MEADOW.pondDeep : MEADOW.pondWater;
    ctx.fill(pond.path);
  }
  if (layers) {
    blit(layers.shore);
  } else {
    // Fallback: the one flat shallow band, as before.
    for (const pond of ponds) {
      ctx.save();
      ctx.clip(pond.path);
      ctx.strokeStyle = MEADOW.pondShallow;
      ctx.lineWidth = tile * 0.24;
      ctx.stroke(pond.path);
      ctx.restore();
    }
  }
  for (const pond of ponds) {
    if (motion) {
      ctx.save();
      ctx.clip(pond.path);
      drawCaustics(ctx, pond, tile, now);
      ctx.restore();
    }
    // The meniscus, replacing pondRim's hardcoded 1.5px -- the literal that
    // made the rim vanish at a 44px tile and shout at 14px.
    ctx.strokeStyle = MEADOW.pondMeniscus;
    ctx.lineWidth = Math.max(1, tile * t.meniscusWidthTiles);
    ctx.stroke(pond.path);
    if (pond.tiles.length >= t.lilyPadMinTiles) {
      // Anchor on the pond's lowest (x, y) tile so the pad never moves.
      let anchor = pond.tiles[0];
      for (const p of pond.tiles) {
        if (p.x < anchor.x || (p.x === anchor.x && p.y < anchor.y)) anchor = p;
      }
      const at =
        pond.tiles[
          Math.floor(
            tileHash(anchor.x, anchor.y, MEADOW_SALTS.lily) * pond.tiles.length,
          )
        ];
      drawLilyPad(ctx, (at.x + 0.5) * tile, (at.y + 0.55) * tile, tile);
    }
  }
  ctx.restore();
}

/** A lily pad: a soft ellipse with the classic notch. */
function drawLilyPad(ctx, cx, cy, tile) {
  const rx = tile * 0.26;
  const ry = tile * 0.18;
  ctx.save();
  // A contact shadow, so the pad sits ON the new deep water rather than
  // floating over it. Offset down and forward, like everything else here.
  ctx.fillStyle = 'rgba(20, 50, 70, 0.22)';
  ctx.beginPath();
  ctx.ellipse(cx + tile * 0.03, cy + tile * 0.05, rx, ry, 0, 0, TAU);
  ctx.fill();
  ctx.fillStyle = MEADOW.lilyPad;
  ctx.strokeStyle = MEADOW.lilyPadRim;
  ctx.lineWidth = Math.max(0.8, tile * 0.04);
  ctx.beginPath();
  ctx.ellipse(cx, cy, rx, ry, 0, 0, TAU);
  ctx.fill();
  ctx.stroke();
  // A lit edge on the upper shoulder.
  ctx.strokeStyle = mixPaletteColor(MEADOW.lilyPad, '#ffffff', 0.6);
  ctx.lineWidth = Math.max(0.6, tile * 0.028);
  ctx.beginPath();
  ctx.ellipse(cx, cy, rx * 0.92, ry * 0.92, 0, Math.PI * 1.15, Math.PI * 1.85);
  ctx.stroke();
  // The notch: a wedge of water reclaiming the pad. In pondDeep, not
  // pondWater -- against the new body the old pale would glow.
  ctx.fillStyle = MEADOW.pondDeep;
  ctx.beginPath();
  ctx.moveTo(cx, cy);
  ctx.lineTo(cx + rx * 1.1, cy - ry * 0.9);
  ctx.lineTo(cx + rx * 1.1, cy + ry * 0.1);
  ctx.closePath();
  ctx.fill();
  ctx.restore();
}

/**
 * Sunbeams as light (US4, FR-008): a radial warm gradient bleeding softly
 * past the tile bounds, replacing the hard-edged tinted square. Default
 * compositing at a low named alpha, so adjacent beams blend by natural
 * gradient accumulation without banding (research R5). The 005 pulse and
 * dust motes play over this unchanged, from the caller.
 */
function drawSunbeamGlow(ctx, { cx, cy, tile, alpha = 1 }) {
  const t = meadowTunables();
  const r = t.glowRadiusTiles * tile;
  const gradient = ctx.createRadialGradient(cx, cy, tile * 0.15, cx, cy, r);
  gradient.addColorStop(0, MEADOW.glowCore);
  gradient.addColorStop(0.55, MEADOW.glowMid);
  gradient.addColorStop(1, MEADOW.glowFade);
  ctx.save();
  ctx.globalAlpha = alpha * t.glowAlpha;
  ctx.fillStyle = gradient;
  ctx.beginPath();
  ctx.arc(cx, cy, r, 0, TAU);
  ctx.fill();
  ctx.restore();
}

/**
 * Worn paths (US5, FR-009): soft rounded tints of bare earth, opacity
 * scaled by the decayed heat the animation layer serves. The renderer
 * calls this only while the toggle is on; memory itself lives (and is
 * cleared) in Presentation, never here.
 */
function drawWornPaths(ctx, { entries, tile }) {
  const t = meadowTunables();
  ctx.save();
  ctx.fillStyle = MEADOW.pathTint;
  const inset = tile * 0.08;
  const r = tile * 0.34;
  for (const e of entries) {
    ctx.globalAlpha = t.pathTintAlpha * e.heat01;
    const x = e.x * tile + inset;
    const y = e.y * tile + inset;
    const s = tile - inset * 2;
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + s, y, x + s, y + s, r);
    ctx.arcTo(x + s, y + s, x, y + s, r);
    ctx.arcTo(x, y + s, x, y, r);
    ctx.arcTo(x, y, x + s, y, r);
    ctx.closePath();
    ctx.fill();
  }
  ctx.restore();
}
