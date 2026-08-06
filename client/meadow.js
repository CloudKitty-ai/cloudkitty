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
  bush: '#8ab377',
  bushHi: '#a6c78f',
  // The demoted debug lattice (formerly baked into the ground cache).
  gridLine: 'rgba(140, 170, 130, 0.16)',
  // Dust motes circling in the sunbeams (render.js reads this).
  moteColor: 'rgba(255, 236, 170, 0.75)',
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
  bush: '#33422f',
  bushHi: '#41533b',
  gridLine: 'rgba(190, 210, 190, 0.14)',
  moteColor: 'rgba(215, 228, 255, 0.8)',
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
  bush: '#8f9a5f',
  bushHi: '#a9b378',
  gridLine: 'rgba(150, 150, 110, 0.18)',
  moteColor: 'rgba(255, 210, 140, 0.8)',
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
  bush: '#7e8c79',
  bushHi: '#95a18e',
  gridLine: 'rgba(140, 148, 140, 0.16)',
  moteColor: 'rgba(228, 226, 218, 0.75)',
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
  bush: 19,
  bushShape: 20,
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
  toneSteps: 18, // steps in the ramp blended through the grass tones
  toneCells: 3, // tiles per noise cell: how broad a grass blotch is
  jitterCells: 1.7, // and the finer lattice the brightness grain rides
  jitterAlpha: 0.05, // peak alpha of the per-tile brightness jitter
  patchChance: 0.118, // share of tiles carrying a worn-earth or moss patch
  patchEarthAlpha: 0.03,
  patchMossAlpha: 0.05,
  bladeChance: 0.55, // tiles with a tuft of grass
  bladeAlpha: 0.38,
  bloomChance: 0.05, // tiles with a flower
  bushChance: 0.025, // tiles with a clump of tufted ground cover
  bushAlpha: 0.4, // and how strongly it reads against the grass
  bushStyle: 'shrub', // 'cover' | 'tuft' | 'bramble' | 'shrub' (gallery-meadow.html)
  // The shrub's shadow, damped against the cats': a squat canopy sits
  // close to the ground, so it stretches far less and needs no alpha
  // falloff. Only the LENGTH is damped -- the lean also anchors the
  // sun-side edge to the caster, and damping that recentres it.
  bushShadowLean: 1, // gain on the anchor: 1 keeps the sun-side edge on the shrub
  bushShadowLength: 0.3, // and of its stretch past the caster
  bushShadowAlpha: 1, // no thinning: contact, not a smear
  bushLift: 0.9, // how far a shrub's canopy stands above its base, in radii
  bushBase: 0.72, // where it meets the ground, in tiles from the tile's top
  // How far the canopy's height pushes its shadow along the lean. Kept
  // small: a rooted thing's shadow leaves its base, and pushing it far
  // is precisely what makes a bush look airborne.
  bushShadowThrow: 0.25,
  shoreRounding: 0.45, // pond corner rounding, in tiles
  shoreWobble: 0.07, // organic shoreline waviness, in tiles
  lilyPadMinTiles: 4, // ponds at least this big carry a lily pad
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
 * `toneSteps` mixes rather than one per tile -- 24 instead of 576 on the
 * demo world.
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

function drawMeadowGround(ctx, { width, height, tile, cover = true }) {
  const t = meadowTunables();
  const ramp = grassRamp(MEADOW.grassTones, t.toneSteps);
  const span = tile + TILE_BLEED * 2;
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const n = smoothNoise(x, y, MEADOW_SALTS.tone, t.toneCells);
      ctx.fillStyle = ramp[Math.min(ramp.length - 1, Math.floor(n * ramp.length))];
      ctx.fillRect(x * tile - TILE_BLEED, y * tile - TILE_BLEED, span, span);
      // The jitter stays finer-grained than the tone -- it is the grass's
      // own texture rather than the ground's shape -- but smoothed too,
      // on a tighter lattice, so it grains the meadow instead of tiling it.
      const j = smoothNoise(x, y, MEADOW_SALTS.jitter, t.jitterCells);
      ctx.globalAlpha = t.jitterAlpha * Math.abs(j * 2 - 1);
      ctx.fillStyle = j < 0.5 ? MEADOW.jitterShade : MEADOW.jitterTint;
      ctx.fillRect(x * tile - TILE_BLEED, y * tile - TILE_BLEED, span, span);
      ctx.globalAlpha = 1;
    }
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

  // --- grass tufts: one path for the lot, so it is a single stroke ---
  ctx.lineWidth = Math.max(1, tile * 0.035);
  ctx.lineCap = 'round';
  ctx.strokeStyle = MEADOW.moss;
  ctx.globalAlpha = t.bladeAlpha;
  ctx.beginPath();
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const n = tileHash(x, y, MEADOW_SALTS.blade);
      if (n < 1 - t.bladeChance) continue;
      const bx = (x + tileHash(x, y, MEADOW_SALTS.bladeX)) * tile;
      const by = (y + tileHash(x, y, MEADOW_SALTS.bladeY)) * tile;
      ctx.moveTo(bx, by);
      ctx.quadraticCurveTo(
        bx + tile * 0.06,
        by - tile * 0.17,
        bx + (n - 0.5) * tile * 0.34,
        by - tile * 0.32,
      );
    }
  }
  ctx.stroke();
  ctx.globalAlpha = 1;

  // --- flowers: five petals and a heart when the tile can carry them,
  //     a single dot when it cannot. The same `fine` threshold the cats
  //     and the bowl's decal use, so detail arrives everywhere at once. ---
  const fine = tile >= 44;
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      if (tileHash(x, y, MEADOW_SALTS.bloom) < 1 - t.bloomChance) continue;
      const k = tileHash(x, y, MEADOW_SALTS.bloomX);
      const bx = (x + 0.25 + k * 0.5) * tile;
      const by = (y + 0.25 + tileHash(x, y, MEADOW_SALTS.blade) * 0.5) * tile;
      const r = tile * 0.055;
      ctx.fillStyle = MEADOW.bloom;
      if (fine) {
        for (let i = 0; i < 5; i++) {
          const a = (i / 5) * TAU + k * 3;
          ctx.beginPath();
          ctx.arc(bx + Math.cos(a) * r, by + Math.sin(a) * r, r * 0.85, 0, TAU);
          ctx.fill();
        }
        ctx.fillStyle = MEADOW.bloomHeart;
        ctx.beginPath();
        ctx.arc(bx, by, r * 0.7, 0, TAU);
        ctx.fill();
      } else {
        ctx.beginPath();
        ctx.arc(bx, by, r * 1.15, 0, TAU);
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
function bushesFor(width, height, t, occupied) {
  const out = [];
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      if (tileHash(x, y, MEADOW_SALTS.bush) < 1 - t.bushChance) continue;
      if (occupied && occupied.has(`${x},${y}`)) continue;
      out.push({ x, y, seed: tileHash(x, y, MEADOW_SALTS.bushShape) });
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

/** One clump, at tile coordinates. Split out of the scatter so the
 *  renderer can interleave these with the cats by depth. */
function drawBushAt(ctx, { x, y, seed, tile, t }) {
  const style = t.bushStyle || 'cover';
  {
    {
      const s = seed;
      const bx = (x + 0.5) * tile;
      const by = (y + 0.5) * tile;
      const r = (0.26 + s * 0.18) * tile;

      if (style === 'shrub') {
        // Standing growth, with the leaning shadow that says so.
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
        ctx.ellipse(bx + offset, by + r * 0.52, r * length, r * 0.3, 0, 0, TAU);
        ctx.fill();
        // The canopy stands ABOVE the base rather than sitting on it, so
        // the shrub occupies the tile above its own -- which is the only
        // way a cat can be behind one. Its shadow stays at the base: that
        // is where it meets the ground, and where the depth sort keys it.
        const lift = canopyLift;
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
    roundedLoop(path, wobbleLoop(loop, t.shoreWobble), t.shoreRounding, tile);
  }
  return path;
}

/**
 * Organic shorelines: subdivide each straight run and push the new points
 * a hash-chosen whisker sideways (revision 1 -- straight-sided ponds read
 * exactly like the old squares, especially the common single-tile pool).
 * The wobble is small enough that tile membership stays unambiguous, and
 * hashing the quantized point keeps it deterministic (FR-002).
 */
function wobbleLoop(points, wobble) {
  const out = [];
  const n = points.length;
  for (let i = 0; i < n; i++) {
    const [ax, ay] = points[i];
    const [bx, by] = points[(i + 1) % n];
    out.push([ax, ay]);
    const len = Math.hypot(bx - ax, by - ay);
    const ux = (bx - ax) / len;
    const uy = (by - ay) / len;
    const segments = Math.max(2, Math.round(len * 2));
    for (let j = 1; j < segments; j++) {
      const px = ax + (bx - ax) * (j / segments);
      const py = ay + (by - ay) * (j / segments);
      const h = tileHash(Math.round(px * 4), Math.round(py * 4), MEADOW_SALTS.shore);
      const off = (h - 0.5) * 2 * wobble;
      // Perpendicular to the direction of travel.
      out.push([px - uy * off, py + ux * off]);
    }
  }
  return out;
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

/** Append one corner-rounded closed loop (tile units -> pixels) to path. */
function roundedLoop(path, points, rounding, tile) {
  const n = points.length;
  if (n < 3) return;
  const px = (p) => p[0] * tile;
  const py = (p) => p[1] * tile;
  const seg = (a, b) => {
    const dx = px(b) - px(a);
    const dy = py(b) - py(a);
    const len = Math.hypot(dx, dy);
    return { ux: dx / len, uy: dy / len, len };
  };
  for (let i = 0; i <= n; i++) {
    const prev = points[(i - 1 + n) % n];
    const v = points[i % n];
    const next = points[(i + 1) % n];
    const inc = seg(prev, v);
    const out = seg(v, next);
    const r = Math.min(rounding * tile, inc.len / 2, out.len / 2);
    const ax = px(v) - inc.ux * r;
    const ay = py(v) - inc.uy * r;
    if (i === 0) path.moveTo(ax, ay);
    else path.lineTo(ax, ay);
    if (i < n) path.quadraticCurveTo(px(v), py(v), px(v) + out.ux * r, py(v) + out.uy * r);
  }
  path.closePath();
}

/**
 * Ponds, step three (US2): fill + rim the cached shoreline paths; larger
 * ponds carry one hash-placed lily pad (FR-005).
 */
function drawPonds(ctx, { ponds, tile }) {
  const t = meadowTunables();
  ctx.save();
  for (const pond of ponds) {
    ctx.fillStyle = MEADOW.pondWater;
    ctx.fill(pond.path);
    // Shallows: a pale band hugging the inside of the shore (a wide
    // stroke clipped to the pond, so only its inner half shows).
    ctx.save();
    ctx.clip(pond.path);
    ctx.strokeStyle = MEADOW.pondShallow;
    ctx.lineWidth = tile * 0.24;
    ctx.stroke(pond.path);
    ctx.restore();
    ctx.strokeStyle = MEADOW.pondRim;
    ctx.lineWidth = 1.5;
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
  ctx.fillStyle = MEADOW.lilyPad;
  ctx.strokeStyle = MEADOW.lilyPadRim;
  ctx.lineWidth = Math.max(0.8, tile * 0.04);
  ctx.beginPath();
  ctx.ellipse(cx, cy, rx, ry, 0, 0, TAU);
  ctx.fill();
  ctx.stroke();
  // The notch: a wedge of water reclaiming the pad.
  ctx.fillStyle = MEADOW.pondWater;
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
