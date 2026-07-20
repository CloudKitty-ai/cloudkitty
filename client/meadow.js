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
const MEADOW = Object.freeze({
  // The ground: close greens, deliberately near the retired checkerboard
  // pair so the world keeps its palette while losing its grid.
  grassTones: Object.freeze(['#e9f3e1', '#e4efd9', '#dfecd4', '#e6f1dc']),
  jitterTint: '#ffffff', // the brighter half of the per-tile jitter
  jitterShade: '#7f9a72', // and the darker half
  floraTuft: '#a9c99a',
  floraClover: '#8fbd85',
  floraPetal: '#f7eef5',
  floraCenter: '#f4c95d', // the same gold the beat stars wear
  // Water, matching the shipped pool hues so ponds read as the same water.
  pondWater: '#bfe3f2',
  pondRim: '#9ccfe6',
  lilyPad: '#9fcf8e',
  lilyPadRim: '#84b877',
  // The world edge fringe: a deeper grass than any ground tone.
  edgeFringe: '#b3cf9e',
  // Sunbeam glow stops (radial: core -> mid -> transparent).
  glowCore: 'rgba(255, 231, 150, 0.85)',
  glowMid: 'rgba(255, 226, 138, 0.4)',
  glowFade: 'rgba(255, 226, 138, 0)',
  // Worn paths: bare warm earth showing through the grass.
  pathTint: '#c8b28e',
  // The demoted debug lattice (formerly baked into the ground cache).
  gridLine: 'rgba(140, 170, 130, 0.16)',
});

/** Named salts for peeling independent values off tileHash (research R2). */
const MEADOW_SALTS = Object.freeze({
  tone: 1,
  jitter: 2,
  flora: 3,
  floraKind: 4,
  floraOffsetX: 5,
  floraOffsetY: 6,
  lily: 7,
  edge: 8,
});

/**
 * The drawing-side stand-ins for VIEW.meadow, used only when the animation
 * layer is absent (the headless harness). VIEW.meadow in anim.js is the
 * authoritative superset -- the harness asserts it stays one.
 */
const MEADOW_DEFAULTS = Object.freeze({
  scatter: true, // flora + brightness jitter (base tones always draw)
  ponds: true, // merged smooth-shored water (off: per-tile pools)
  edge: true, // the world fringe frame
  glow: true, // sunbeams as radial light (off: plain warm tile)
  paths: true, // whether the worn-paths overlay is available at all
  gridOverlay: true, // whether the grid debug overlay is available at all
  toneCount: 4, // how many close grass tones the meadow mixes
  jitterAlpha: 0.05, // peak alpha of the per-tile brightness jitter
  floraDensity: 0.06, // share of tiles carrying a tuft/clover/flower
  shoreRounding: 0.45, // pond corner rounding, in tiles
  lilyPadMinTiles: 4, // ponds at least this big carry a lily pad
  glowRadiusTiles: 1.4, // sunbeam glow radius, in tiles
  glowAlpha: 0.6, // overall glow strength
  edgeDepth: 0.3, // fringe depth, in tiles (stays inside boundary tiles)
  pathHeatCap: 12, // worn-path heat ceiling per tile
  pathHalfLifeMs: 45000, // trail fading half-life
  pathVisibilityFloor: 0.5, // decayed heat below this draws nothing
  pathTintAlpha: 0.35, // trail opacity at full heat
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
 * The organic meadow (US1, FR-001): per-tile base tone, a barely-there
 * brightness jitter, and sparse flora -- all from tileHash. Drawn once
 * into the ground cache; the per-frame cost stays one blit.
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
      if (!t.scatter) continue;
      const j = tileHash(x, y, MEADOW_SALTS.jitter);
      ctx.globalAlpha = t.jitterAlpha * Math.abs(j * 2 - 1);
      ctx.fillStyle = j < 0.5 ? MEADOW.jitterShade : MEADOW.jitterTint;
      ctx.fillRect(x * tile, y * tile, tile, tile);
      ctx.globalAlpha = 1;
    }
  }
  if (!t.scatter) return;
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      if (tileHash(x, y, MEADOW_SALTS.flora) >= t.floraDensity) continue;
      const kind = Math.floor(tileHash(x, y, MEADOW_SALTS.floraKind) * 3);
      const ox = 0.25 + tileHash(x, y, MEADOW_SALTS.floraOffsetX) * 0.5;
      const oy = 0.25 + tileHash(x, y, MEADOW_SALTS.floraOffsetY) * 0.5;
      drawFlora(ctx, kind, (x + ox) * tile, (y + oy) * tile, tile);
    }
  }
}

/** One flora accent: 0 a grass tuft, 1 a clover, 2 a tiny flower. */
function drawFlora(ctx, kind, cx, cy, tile) {
  ctx.save();
  if (kind === 0) {
    // A tuft: three short blades leaning apart.
    ctx.strokeStyle = MEADOW.floraTuft;
    ctx.lineWidth = Math.max(0.7, tile * 0.045);
    ctx.lineCap = 'round';
    for (const lean of [-0.14, 0, 0.16]) {
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.quadraticCurveTo(
        cx + lean * tile * 0.5,
        cy - tile * 0.12,
        cx + lean * tile,
        cy - tile * 0.22,
      );
      ctx.stroke();
    }
  } else if (kind === 1) {
    // A clover: three leaflets in a tight cluster.
    ctx.fillStyle = MEADOW.floraClover;
    const r = tile * 0.055;
    for (const [dx, dy] of [[0, -1.1], [-1, 0.7], [1, 0.7]]) {
      ctx.beginPath();
      ctx.arc(cx + dx * r, cy + dy * r, r, 0, TAU);
      ctx.fill();
    }
  } else {
    // A tiny flower: four petals around a gold center.
    const r = tile * 0.05;
    ctx.fillStyle = MEADOW.floraPetal;
    for (const [dx, dy] of [[0, -1.4], [0, 1.4], [-1.4, 0], [1.4, 0]]) {
      ctx.beginPath();
      ctx.arc(cx + dx * r, cy + dy * r, r, 0, TAU);
      ctx.fill();
    }
    ctx.fillStyle = MEADOW.floraCenter;
    ctx.beginPath();
    ctx.arc(cx, cy, r * 0.9, 0, TAU);
    ctx.fill();
  }
  ctx.restore();
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
    roundedLoop(path, loop, t.shoreRounding, tile);
  }
  return path;
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
 * The world edge (US3, FR-007): a taller-grass fringe hugging the outer
 * margin of the boundary tiles -- blades plus a soft baseline strip --
 * so any size world reads as a garden with an edge. Depth stays within
 * the boundary tiles, so the frame can never cover a resident.
 */
function drawWorldEdge(ctx, { width, height, tile }) {
  const t = meadowTunables();
  const depth = t.edgeDepth * tile;
  const w = width * tile;
  const h = height * tile;
  ctx.save();

  // The baseline: a whisper of deeper green along every border.
  ctx.globalAlpha = 0.22;
  ctx.fillStyle = MEADOW.edgeFringe;
  ctx.fillRect(0, 0, w, depth * 0.5);
  ctx.fillRect(0, h - depth * 0.5, w, depth * 0.5);
  ctx.fillRect(0, 0, depth * 0.5, h);
  ctx.fillRect(w - depth * 0.5, 0, depth * 0.5, h);
  ctx.globalAlpha = 1;

  // The blades: hash-varied spacing, height, and lean per side.
  ctx.strokeStyle = MEADOW.edgeFringe;
  ctx.lineWidth = Math.max(0.9, tile * 0.055);
  ctx.lineCap = 'round';
  const step = tile * 0.3;
  // side: 0 top, 1 bottom, 2 left, 3 right. Each blade roots on the
  // border and leans inward.
  const sides = [
    { len: w, root: (s) => [s, 0], dir: [0, 1] },
    { len: w, root: (s) => [s, h], dir: [0, -1] },
    { len: h, root: (s) => [0, s], dir: [1, 0] },
    { len: h, root: (s) => [w, s], dir: [-1, 0] },
  ];
  sides.forEach((side, si) => {
    const count = Math.max(2, Math.floor(side.len / step));
    for (let i = 0; i < count; i++) {
      const hJit = tileHash(i, si, MEADOW_SALTS.edge);
      const hLen = tileHash(i + 1000, si, MEADOW_SALTS.edge);
      const hLean = tileHash(i + 2000, si, MEADOW_SALTS.edge);
      const s = (i + 0.2 + hJit * 0.6) * step;
      if (s > side.len) continue;
      const [rx, ry] = side.root(s);
      const reach = depth * (0.55 + hLen * 0.45);
      const lean = (hLean - 0.5) * tile * 0.24;
      const tipX = rx + side.dir[0] * reach + (side.dir[0] === 0 ? lean : 0);
      const tipY = ry + side.dir[1] * reach + (side.dir[1] === 0 ? lean : 0);
      ctx.beginPath();
      ctx.moveTo(rx, ry);
      ctx.quadraticCurveTo(
        rx + side.dir[0] * reach * 0.5,
        ry + side.dir[1] * reach * 0.5,
        tipX,
        tipY,
      );
      ctx.stroke();
    }
  });
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
  const inset = tile * 0.12;
  const r = tile * 0.3;
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
