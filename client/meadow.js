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
  // The soft ground shadow that seats a cat on the grass (render.js).
  groundShadow: 'rgba(140, 120, 100, 0.15)',
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
});

/**
 * The active palette. Drawing code reads MEADOW as ever; the theme switch
 * (app.js setTheme) swaps which frozen set it names. The renderer's ground
 * cache is invalidated by the same switch -- the cache bakes these colors.
 */
let MEADOW = MEADOW_DAY;

function setMeadowPalette(night) {
  MEADOW = night ? MEADOW_NIGHT : MEADOW_DAY;
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
