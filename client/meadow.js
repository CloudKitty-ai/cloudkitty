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
  // The demoted debug lattice (formerly baked into the ground cache).
  gridLine: 'rgba(140, 170, 130, 0.16)',
  // Dust motes circling in the sunbeams (render.js reads this).
  moteColor: 'rgba(255, 236, 170, 0.75)',
  // The soft ground shadow that seats a cat on the grass (render.js), and
  // where the sun is putting it (v3): `shadowLean` slides it sideways in
  // half-tile units, `shadowLength` stretches it away from the caster.
  // Noon is nearly overhead, so the shadow is short and barely leans.
  groundShadow: 'rgba(140, 120, 100, 0.15)',
  shadowLean: 0.06,
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
  gridLine: 'rgba(190, 210, 190, 0.14)',
  moteColor: 'rgba(215, 228, 255, 0.8)',
  groundShadow: 'rgba(12, 10, 22, 0.35)',
  // The moon reads as a lamp overhead rather than a low light, so night
  // has no lean at all -- and that is the point: it is the still hour
  // between the two horizons the sun uses.
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
  gridLine: 'rgba(150, 150, 110, 0.18)',
  moteColor: 'rgba(255, 210, 140, 0.8)',
  groundShadow: 'rgba(120, 80, 90, 0.2)', // long violet-warm evening shadows
  // The sun is low on one horizon; shadows run long, away from it.
  shadowLean: 0.85,
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
  gridLine: 'rgba(140, 148, 140, 0.16)',
  moteColor: 'rgba(228, 226, 218, 0.75)',
  groundShadow: 'rgba(60, 66, 72, 0.24)', // long, cool, but not blue
  // The same low sun as sunset, on the opposite horizon -- so the lean
  // is the opposite sign. This is the one place dawn and sunset differ
  // in geometry rather than only in colour, and it is what stops the two
  // twilights reading as the same hour played twice.
  shadowLean: -0.8,
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
  toneCount: 4, // how many close grass tones the meadow mixes
  jitterAlpha: 0.05, // peak alpha of the per-tile brightness jitter
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
function drawMeadowGround(ctx, { width, height, tile }) {
  const t = meadowTunables();
  const tones = MEADOW.grassTones;
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const tone =
        Math.floor(tileHash(x, y, MEADOW_SALTS.tone) * t.toneCount) %
        tones.length;
      ctx.fillStyle = tones[tone];
      ctx.fillRect(x * tile, y * tile, tile, tile);
      const j = tileHash(x, y, MEADOW_SALTS.jitter);
      ctx.globalAlpha = t.jitterAlpha * Math.abs(j * 2 - 1);
      ctx.fillStyle = j < 0.5 ? MEADOW.jitterShade : MEADOW.jitterTint;
      ctx.fillRect(x * tile, y * tile, tile, tile);
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
