/**
 * Headless checks for the meadow (spec 008) -- run with `node client/test-meadow.mjs`.
 *
 * The 005/007 harness pattern: eval the plain scripts in one shared scope
 * (cat.js for TAU, meadow.js, anim.js for VIEW/Presentation), drive the
 * draw functions through a guarding mock ctx that throws on any non-finite
 * numeric argument, and test the derivation logic (hash, pond geometry,
 * worn-path memory) directly. No toolchain, no DOM.
 */
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const src =
  readFileSync(join(here, 'cat.js'), 'utf8') +
  ';' +
  // cat-v2.js is an IIFE that registers globalThis.CatV2 and declares
  // nothing else, so it is inert here -- but it has to be present or the
  // renderer's whole v2 branch is dead code in this harness, and the water
  // path lives inside it (`v2Motion ? submersionFor(...) : 0`). Without it
  // a full-frame check would draw a v1 cat and prove nothing about water.
  readFileSync(join(here, 'cat-v2.js'), 'utf8') +
  ';' +
  readFileSync(join(here, 'meadow.js'), 'utf8') +
  ';' +
  // props.js: the butterfly and the bowl. Needed since critters joined the
  // depth sort -- a full frame now DRAWS them, and without this the whole
  // element pass is a ReferenceError waiting to happen in any composed check.
  readFileSync(join(here, 'props.js'), 'utf8') +
  ';' +
  readFileSync(join(here, 'anim.js'), 'utf8') +
  ';' +
  // render.js for WorldRenderer.occupiedTiles: it is the other half of the
  // ground-cover contract bushesFor implements, and the two agree over a key
  // format that only a composed check can see. Safe to share the scope --
  // render.js declares no name the other three do, and runs nothing at the
  // top level.
  readFileSync(join(here, 'render.js'), 'utf8');

/** Path2D stand-in: records commands, throws on non-finite coordinates. */
class MockPath2D {
  constructor() {
    this.cmds = [];
  }
  record(name, args) {
    for (const a of args) {
      if (!Number.isFinite(a)) {
        throw new Error(`Path2D.${name} got non-finite args: ${args}`);
      }
    }
    this.cmds.push([name, ...args]);
  }
  moveTo(...a) {
    this.record('moveTo', a);
  }
  lineTo(...a) {
    this.record('lineTo', a);
  }
  quadraticCurveTo(...a) {
    this.record('quadraticCurveTo', a);
  }
  closePath() {
    this.cmds.push(['closePath']);
  }
}
globalThis.Path2D = MockPath2D;

/** Canvas ctx stand-in: every method logs and guards non-finite numbers. */
function guardCtx(log = []) {
  const guard = (name, args) => {
    for (const a of args) {
      if (typeof a === 'number' && !Number.isFinite(a)) {
        throw new Error(`ctx.${name} got non-finite args: ${args}`);
      }
    }
  };
  const serialize = (a) =>
    a instanceof MockPath2D ? `<path:${a.cmds.length}>` : typeof a === 'object' ? '<obj>' : a;
  return new Proxy(
    {},
    {
      get(target, prop) {
        if (prop === 'createRadialGradient' || prop === 'createLinearGradient') {
          return (...args) => {
            guard(prop, args);
            log.push([prop, ...args]);
            return {
              addColorStop: (offset, color) => {
                guard('addColorStop', [offset]);
                log.push(['addColorStop', offset, color]);
              },
            };
          };
        }
        if (prop === 'measureText') {
          // A real canvas answers with TextMetrics. Nothing here judges
          // type layout, so a plausible finite width is enough -- but it
          // has to be an OBJECT, or `drawBubble` throws on `.width` and
          // takes the whole frame with it. No check drew a speech bubble
          // until the purr split, which is why this was never needed.
          return (text) => {
            log.push(['measureText', text]);
            return { width: String(text).length * 6 };
          };
        }
        return (...args) => {
          guard(prop, args);
          log.push([prop, ...args.map(serialize)]);
        };
      },
      set(target, prop, value) {
        if (typeof value === 'number' && !Number.isFinite(value)) {
          throw new Error(`ctx.${prop} set to non-finite ${value}`);
        }
        log.push(['set', prop, typeof value === 'object' ? '<obj>' : value]);
        return true;
      },
    },
  );
}

/** A canvas stand-in, so code that builds offscreens can run headlessly.
 *  `buildPondLayers` makes four of them, which is exactly why the renderer
 *  path below was never reachable before. */
function mockCanvas(width = 640, height = 640, log = []) {
  // `clientWidth`/`clientHeight` are what a real canvas reports for its CSS
  // box, and `drawBubble` clamps against them to keep a bubble on screen --
  // undefined there is a NaN into moveTo, which the guard catches but only
  // once something actually draws a bubble. Nothing did until the purr
  // split. `log` is optional so a check can read back what was drawn.
  const canvas = { width, height, clientWidth: width, clientHeight: height, dataset: {}, style: {} };
  const ctx = guardCtx(log);
  ctx.canvas = canvas;
  canvas.getContext = () => ctx;
  return canvas;
}
globalThis.document = {
  createElement: (tag) => (tag === 'canvas' ? mockCanvas() : { style: {} }),
  // `draw` begins with `resizeFor`, which measures the page chrome around
  // the map. Answering "nothing is there" is the honest headless reading --
  // no header, no footer, no cards beside it -- so the map gets the whole
  // budget and the tile comes out at the cap. That the sizing pass runs at
  // all is worth having: it is on the path to every frame.
  querySelector: () => null,
  body: { style: {} },
  documentElement: { clientWidth: 1280, clientHeight: 900 },
};
globalThis.getComputedStyle = () => ({});
globalThis.window = { devicePixelRatio: 1 };

// MEADOW is a getter, not a value: setMeadowPalette rebinds it, and a
// snapshot taken at eval time could never see that.
const EXPORTS =
  ';({ get MEADOW() { return MEADOW; }, MEADOW_DAY, MEADOW_DUSK, MEADOW_NIGHT, setMeadowPalette,' +
  ' mixPaletteColor, mixPalettes, parsePaletteColor,' +
  ' MEADOW_DAWN, bushesFor, drawBushAt, drawGroundCover, MEADOW_SALTS, MEADOW_DEFAULTS, tileHash, drawMeadowGround, drawGridOverlay, groupWaterTiles,' +
  ' buildPondPath, drawPonds, pondInradius, drawSunbeamGlow, drawWornPaths, VIEW, Presentation,' +
  ' driftField, spriteOrder, SPRITE_RANK, coverSortKey, catSortKey, coverStands,' +
  ' WorldRenderer, PURR, drawPurrGlyph, Camera })';
const api = eval(src + EXPORTS);

let passed = 0;
let failed = 0;
function check(name, fn) {
  try {
    fn();
    passed += 1;
    console.log(`  ok   ${name}`);
  } catch (err) {
    if (process.env.SHOWSTACK) console.error(err.stack);
    failed += 1;
    console.error(`  FAIL ${name}: ${err.message}`);
  }
}
function assert(cond, msg) {
  if (!cond) throw new Error(msg);
}
function close(a, b, msg) {
  assert(Math.abs(a - b) < 1e-12, `${msg}: ${a} != ${b}`);
}

// ---- tunables home ----

check('VIEW.meadow is a superset of MEADOW_DEFAULTS with equal values', () => {
  for (const [key, value] of Object.entries(api.MEADOW_DEFAULTS)) {
    assert(key in api.VIEW.meadow, `VIEW.meadow missing ${key}`);
    assert(
      api.VIEW.meadow[key] === value,
      `VIEW.meadow.${key} = ${api.VIEW.meadow[key]} != default ${value}`,
    );
  }
});

// ---- tileHash (T004): determinism, range, distribution ----

check('tileHash is deterministic across independent evals', () => {
  const api2 = eval(src + EXPORTS);
  for (let x = -3; x < 20; x++) {
    for (let y = -3; y < 20; y++) {
      for (const salt of Object.values(api.MEADOW_SALTS)) {
        assert(
          api.tileHash(x, y, salt) === api2.tileHash(x, y, salt),
          `mismatch at (${x},${y},${salt})`,
        );
      }
    }
  }
});

check('tileHash stays in [0, 1)', () => {
  for (let i = 0; i < 10000; i++) {
    const h = api.tileHash(i % 173, (i * 7) % 211, i % 9);
    assert(h >= 0 && h < 1, `out of range: ${h}`);
  }
});

check('tone distribution is balanced with no long runs (SC-002)', () => {
  const tone = (x, y) =>
    Math.floor(api.tileHash(x, y, api.MEADOW_SALTS.tone) * 4) % 4;
  const counts = [0, 0, 0, 0];
  let maxRun = 0;
  for (let y = 0; y < 64; y++) {
    let run = 0;
    let last = -1;
    for (let x = 0; x < 64; x++) {
      const t = tone(x, y);
      counts[t] += 1;
      run = t === last ? run + 1 : 1;
      last = t;
      maxRun = Math.max(maxRun, run);
    }
  }
  let diagRun = 0;
  let diagMax = 0;
  let diagLast = -1;
  for (let i = 0; i < 64; i++) {
    const t = tone(i, i);
    diagRun = t === diagLast ? diagRun + 1 : 1;
    diagLast = t;
    diagMax = Math.max(diagMax, diagRun);
  }
  const total = 64 * 64;
  for (const c of counts) {
    const share = c / total;
    assert(share > 0.15 && share < 0.35, `tone share ${share} off-balance`);
  }
  assert(maxRun <= 10, `horizontal tone run of ${maxRun}`);
  assert(diagMax <= 10, `diagonal tone run of ${diagMax}`);
});

check('salt channels are decorrelated', () => {
  let agree = 0;
  const n = 2500;
  for (let i = 0; i < n; i++) {
    const x = i % 50;
    const y = Math.floor(i / 50);
    const a = api.tileHash(x, y, api.MEADOW_SALTS.tone) < 0.5;
    const b = api.tileHash(x, y, api.MEADOW_SALTS.jitter) < 0.5;
    if (a === b) agree += 1;
  }
  const share = agree / n;
  assert(share > 0.4 && share < 0.6, `salt agreement ${share}`);
});

// ---- draw sweeps (T009/T018/T021): every function, every size, guarded ----

const DIMS = [
  [2, 2],
  [32, 32],
  [64, 64],
  [1, 8],
];
const TILES = [8, 22];

check('drawMeadowGround / drawGridOverlay sweep clean', () => {
  for (const [width, height] of DIMS) {
    for (const tile of TILES) {
      const ctx = guardCtx();
      api.drawMeadowGround(ctx, { width, height, tile });
      api.drawGridOverlay(ctx, { width, height, tile });
    }
  }
});

check('ground drawing is deterministic (identical command streams)', () => {
  const api2 = eval(src + EXPORTS);
  const logA = [];
  const logB = [];
  api.drawMeadowGround(guardCtx(logA), { width: 32, height: 32, tile: 22 });
  api2.drawMeadowGround(guardCtx(logB), { width: 32, height: 32, tile: 22 });
  assert(JSON.stringify(logA) === JSON.stringify(logB), 'streams differ');
});

// (The world-edge margin test left with drawWorldEdge -- the edge frame
// was scrapped at the gate, 2026-07-20 round 2, and returned to the
// backlog.)

// ---- pond geometry (T014) ----

const P = (x, y) => ({ x, y });

check('grouping: single, 2x2, L, U, ring, diagonal', () => {
  assert(api.groupWaterTiles([P(3, 3)]).length === 1, 'single');
  assert(api.groupWaterTiles([P(0, 0), P(1, 0), P(0, 1), P(1, 1)]).length === 1, '2x2');
  assert(api.groupWaterTiles([P(0, 0), P(0, 1), P(1, 1)]).length === 1, 'L');
  const u = [P(0, 0), P(0, 1), P(0, 2), P(1, 2), P(2, 2), P(2, 1), P(2, 0)];
  assert(api.groupWaterTiles(u).length === 1, 'U');
  const ring = [P(0, 0), P(1, 0), P(2, 0), P(0, 1), P(2, 1), P(0, 2), P(1, 2), P(2, 2)];
  assert(api.groupWaterTiles(ring).length === 1, 'ring');
  assert(api.groupWaterTiles([P(0, 0), P(1, 1)]).length === 2, 'diagonal splits');
});

check('grouping is order-independent (signature stability)', () => {
  const tiles = [P(0, 0), P(0, 1), P(1, 1), P(5, 5), P(5, 6)];
  const sig = (groups) =>
    groups
      .map((g) => g.map((p) => `${p.x},${p.y}`).sort().join(' '))
      .sort()
      .join(' | ');
  const a = sig(api.groupWaterTiles(tiles));
  const b = sig(api.groupWaterTiles([...tiles].reverse()));
  assert(a === b, `signatures differ: ${a} vs ${b}`);
});

check('buildPondPath: closed rounded loops, finite everywhere', () => {
  const cases = [
    [P(0, 0)],
    [P(0, 0), P(1, 0), P(0, 1), P(1, 1)],
    [P(0, 0), P(0, 1), P(1, 1)],
    [P(0, 0), P(0, 1), P(0, 2), P(1, 2), P(2, 2), P(2, 1), P(2, 0)],
  ];
  for (const tiles of cases) {
    const path = api.buildPondPath(tiles, 22);
    const moves = path.cmds.filter(([c]) => c === 'moveTo').length;
    const closes = path.cmds.filter(([c]) => c === 'closePath').length;
    const quads = path.cmds.filter(([c]) => c === 'quadraticCurveTo').length;
    assert(moves === 1, `${tiles.length} tiles: ${moves} loops, expected 1`);
    assert(closes === moves, 'every loop closes');
    assert(quads > 0, 'corners are rounded');
  }
});

check('buildPondPath: a ring pond has an outer loop and a hole loop', () => {
  const ring = [P(0, 0), P(1, 0), P(2, 0), P(0, 1), P(2, 1), P(0, 2), P(1, 2), P(2, 2)];
  const path = api.buildPondPath(ring, 22);
  const moves = path.cmds.filter(([c]) => c === 'moveTo').length;
  const closes = path.cmds.filter(([c]) => c === 'closePath').length;
  assert(moves === 2, `ring produced ${moves} loops, expected 2`);
  assert(closes === 2, 'both loops close');
});

check('drawPonds: lily pad at threshold, none below it', () => {
  const big = api.groupWaterTiles([P(0, 0), P(1, 0), P(0, 1), P(1, 1)]).map(
    (tiles) => ({ tiles, path: api.buildPondPath(tiles, 22) }),
  );
  const bigLog = [];
  api.drawPonds(guardCtx(bigLog), { ponds: big, tile: 22 });
  assert(bigLog.some(([c]) => c === 'ellipse'), '4-tile pond carries a pad');

  const small = api.groupWaterTiles([P(0, 0)]).map((tiles) => ({
    tiles,
    path: api.buildPondPath(tiles, 22),
  }));
  const smallLog = [];
  api.drawPonds(guardCtx(smallLog), { ponds: small, tile: 22 });
  assert(!smallLog.some(([c]) => c === 'ellipse'), '1-tile pool stays bare');
});

// ---- glow and paths drawing (T021/T023) ----

check('drawSunbeamGlow builds a finite radial gradient', () => {
  for (const tile of TILES) {
    const log = [];
    api.drawSunbeamGlow(guardCtx(log), { cx: 5 * tile, cy: 3 * tile, tile, alpha: 0.7 });
    assert(log.some(([c]) => c === 'createRadialGradient'), 'gradient created');
    assert(log.filter(([c]) => c === 'addColorStop').length === 3, 'three stops');
  }
});

check('drawWornPaths scales opacity by heat', () => {
  const log = [];
  api.drawWornPaths(guardCtx(log), {
    entries: [
      { x: 1, y: 1, heat01: 1 },
      { x: 2, y: 1, heat01: 0.5 },
    ],
    tile: 22,
  });
  const alphas = log.filter(([c, p]) => c === 'set' && p === 'globalAlpha').map(([, , v]) => v);
  assert(alphas.length >= 2, 'per-entry alpha set');
  assert(alphas[0] > alphas[1], 'hotter tile draws stronger');
});

// ---- Presentation worn-path memory (T026) ----

const kitty = (id, x, y) => ({ id, pos: { x, y }, needs: {}, happiness: 50 });
const world = (tick, kitties) => ({
  tick,
  width: 8,
  height: 8,
  kitties,
  elements: [],
  recent_meows: [],
});

check('paths accumulate on continuous ticks only', () => {
  const p = new api.Presentation();
  p.pushState(world(10, [kitty(1, 2, 2)]), 1000); // first paint: discontinuous
  assert(p.wornPaths(1000).length === 0, 'first paint leaves clean grass');
  p.pushState(world(11, [kitty(1, 2, 3)]), 1800);
  const trails = p.wornPaths(1800);
  assert(trails.length === 1, 'one warmed tile');
  assert(trails[0].x === 2 && trails[0].y === 3, 'at the kitty tile');
});

check('heat clamps at the cap', () => {
  const p = new api.Presentation();
  let now = 1000;
  p.pushState(world(1, [kitty(1, 4, 4)]), now);
  for (let tick = 2; tick <= 30; tick++) {
    now += 800;
    p.pushState(world(tick, [kitty(1, 4, 4)]), now);
  }
  const [trail] = p.wornPaths(now);
  assert(trail.heat01 === 1, `heat01 ${trail.heat01} should cap at 1`);
});

check('trails decay by half-life and vanish below the floor', () => {
  const p = new api.Presentation();
  p.pushState(world(1, [kitty(1, 3, 3)]), 1000);
  p.pushState(world(2, [kitty(1, 3, 3)]), 1800);
  p.pushState(world(3, [kitty(1, 3, 3)]), 2600); // heat ~2 (decay tiny)
  const half = api.VIEW.meadow.pathHalfLifeMs;
  const fresh = p.wornPaths(2600)[0].heat01;
  const later = p.wornPaths(2600 + half)[0].heat01;
  assert(Math.abs(later - fresh / 2) < 0.01, `half-life decay (${fresh} -> ${later})`);
  assert(p.wornPaths(2600 + half * 3).length === 0, 'faded below the floor');
});

check('every discontinuity flavor clears the trails', () => {
  const flavors = [
    ['tick gap', (p) => p.pushState(world(9, [kitty(1, 1, 1)]), 5000)],
    ['roster change', (p) => p.pushState(world(3, [kitty(1, 1, 1), kitty(2, 5, 5)]), 5000)],
    ['teleport', (p) => p.pushState(world(3, [kitty(1, 6, 6)]), 5000)],
    [
      'generation bump',
      (p) => {
        p.bumpGeneration();
        p.pushState(world(3, [kitty(1, 1, 1)]), 5000);
      },
    ],
  ];
  for (const [name, disrupt] of flavors) {
    const p = new api.Presentation();
    p.pushState(world(1, [kitty(1, 1, 1)]), 1000);
    p.pushState(world(2, [kitty(1, 1, 1)]), 1800);
    assert(p.wornPaths(1800).length === 1, `${name}: warmed before`);
    disrupt(p);
    assert(p.wornPaths(5000).length === 0, `${name}: cleared after`);
  }
});

check('viewAt exposes wornPaths in moving and still frames alike', () => {
  const p = new api.Presentation();
  p.pushState(world(1, [kitty(1, 2, 2)]), 1000);
  p.pushState(world(2, [kitty(1, 2, 2)]), 1800);
  assert(p.viewAt(1900, false).wornPaths().length === 1, 'moving frame');
  assert(p.viewAt(1900, true).wornPaths().length === 1, 'still frame (state, not motion)');
});

// ---- palette blending (v3): the light crosses, it does not switch ----

check('colours parse from every form the palettes actually use', () => {
  // #rrggbb, rgba(), and the short hex form, since a future palette may.
  assert(api.mixPaletteColor('#000000', '#ffffff', 0.5) === 'rgb(128, 128, 128)', 'six-digit hex');
  assert(api.mixPaletteColor('#000', '#fff', 0) === '#000', 'identity returns the original string');
  const half = api.mixPaletteColor('rgba(0, 0, 0, 0)', 'rgba(100, 200, 40, 1)', 0.5);
  assert(half === 'rgba(50, 100, 20, 0.5)', `alpha mixes too, got ${half}`);
});

check('an unparseable colour snaps rather than throwing', () => {
  // A palette must never be able to crash a frame.
  assert(api.mixPaletteColor('not-a-colour', '#ffffff', 0.2) === 'not-a-colour', 'near end wins');
  assert(api.mixPaletteColor('not-a-colour', '#ffffff', 0.8) === '#ffffff', 'far end wins past halfway');
});

check('palettes blend entry by entry, arrays included', () => {
  const mid = api.mixPalettes(api.MEADOW_DAY, api.MEADOW_NIGHT, 0.5);
  assert(Array.isArray(mid.grassTones), 'grassTones stays an array');
  assert(mid.grassTones.length === api.MEADOW_DAY.grassTones.length, 'and the same length');
  for (const tone of mid.grassTones) {
    assert(/^rgba?\(/.test(tone), `each tone is a real colour, got ${tone}`);
  }
  // Midway grass must sit between day and night, not equal either.
  assert(mid.grassTones[0] !== api.MEADOW_DAY.grassTones[0], 'moved off day');
  assert(mid.grassTones[0] !== api.MEADOW_NIGHT.grassTones[0], 'and is not night yet');
  assert(Object.isFrozen(mid), 'blended palettes are frozen like the named ones');
});

/** Perceived lightness (CIE L*). The pond's depth ramp is tuned on this and
 *  not on WCAG contrast ratio: that measure exists for text legibility, and
 *  its +0.05 flare term swamps the comparison at night's luminances -- it
 *  called night's ramp healthy while it was half again too strong. */
function lstar(color) {
  const parsed = api.parsePaletteColor(color);
  assert(parsed, `parseable colour, got ${color}`);
  const lin = (c) => {
    const u = c / 255;
    return u <= 0.03928 ? u / 12.92 : ((u + 0.055) / 1.055) ** 2.4;
  };
  const y = 0.2126 * lin(parsed[0]) + 0.7152 * lin(parsed[1]) + 0.0722 * lin(parsed[2]);
  return y > 0.008856 ? 116 * Math.cbrt(y) - 16 : 903.3 * y;
}

check('every phase names its own shore and meniscus', () => {
  // These were derived at draw time as a fixed push toward white, which is a
  // daylight assumption: on the night palette it put the shore band 43 L*
  // over the deep water and the meniscus 49 L* over the ground.
  for (const [name, p] of Object.entries({
    day: api.MEADOW_DAY,
    dusk: api.MEADOW_DUSK,
    night: api.MEADOW_NIGHT,
    dawn: api.MEADOW_DAWN,
  })) {
    assert(typeof p.pondShore === 'string', `${name} names pondShore`);
    assert(typeof p.pondMeniscus === 'string', `${name} names pondMeniscus`);
  }
});

/* The pond's shape in lightness, in the two phases the owner signed off on
 * (day and dusk) -- everything below is measured against them.
 *
 * An earlier version of this check asserted a constant shore-to-deep ramp of
 * 24-31 L*, fitted across day, dusk AND dawn. That was wrong twice over: the
 * band was fitted to include dawn, which the owner then called too bright, and
 * the ramp is an OUTPUT, not an invariant -- it is whatever pondDeep leaves
 * under a shore that matches the grass, and it legitimately differs per phase.
 * What day and dusk actually share is the two relationships below. Replaced
 * rather than widened: a band stretched to admit night's 7 would have asserted
 * nothing at all. */
const PHASES = () => ({
  day: api.MEADOW_DAY,
  dusk: api.MEADOW_DUSK,
  night: api.MEADOW_NIGHT,
  dawn: api.MEADOW_DAWN,
});

check('the shore band sits at the grass, in every phase', () => {
  // Day +1.8, dusk -1.8. This is what stops a pond reading as a lit pool
  // dropped onto the meadow; night was +19 and dawn +12 before they were
  // named, and both looked exactly as bright as that sounds.
  for (const [name, p] of Object.entries(PHASES())) {
    const d = lstar(p.pondShore) - lstar(p.grassTones[0]);
    assert(Math.abs(d) < 4, `${name}: shore sits ${d.toFixed(1)} L* off the grass, want within 4`);
    // The meniscus is a small step above the shore band -- never below it,
    // and never a second ramp. Shipped: 1.3 / 4.0 / 3.3 / 3.3.
    const step = lstar(p.pondMeniscus) - lstar(p.pondShore);
    assert(step > 0 && step < 6, `${name}: meniscus is ${step.toFixed(1)} L* over the shore band`);
  }
});

check('every phase gives the pond a bottom', () => {
  // With the shore pinned to the grass, the depth ramp is entirely pondDeep's
  // doing, so THAT is what has to be checked. Night shipped at 7 L* under the
  // grass -- no bottom to fade to, which is why its shore had to shout.
  // Shipped: -24.2 / -28.7 / -25.0 / -16.7.
  for (const [name, p] of Object.entries(PHASES())) {
    const below = lstar(p.grassTones[0]) - lstar(p.pondDeep);
    assert(below > 12, `${name}: deep water is only ${below.toFixed(1)} L* under the grass`);
    assert(lstar(p.pondShore) > lstar(p.pondDeep), `${name}: the shore band is lighter than the deep`);
  }
});

check('a crossfade holds both relationships all the way across', () => {
  // Interpolated palettes are the ones nobody ever looks at.
  for (const [from, to, label] of [
    [api.MEADOW_DUSK, api.MEADOW_NIGHT, 'dusk->night'],
    [api.MEADOW_NIGHT, api.MEADOW_DAWN, 'night->dawn'],
  ]) {
    for (const t of [0.25, 0.5, 0.75]) {
      const mid = api.mixPalettes(from, to, t);
      const d = lstar(mid.pondShore) - lstar(mid.grassTones[0]);
      assert(Math.abs(d) < 4, `${label} at ${t}: shore ${d.toFixed(1)} L* off the grass`);
      const below = lstar(mid.grassTones[0]) - lstar(mid.pondDeep);
      assert(below > 12, `${label} at ${t}: deep only ${below.toFixed(1)} L* under the grass`);
    }
  }
});

check('the ends of a blend are exactly the named palettes', () => {
  assert(api.mixPalettes(api.MEADOW_DAY, api.MEADOW_NIGHT, 0) === api.MEADOW_DAY, 't=0 IS day');
  assert(api.mixPalettes(api.MEADOW_DAY, api.MEADOW_NIGHT, 1) === api.MEADOW_NIGHT, 't=1 IS night');
});

check('api.setMeadowPalette names one palette or a blend of two', () => {
  api.setMeadowPalette('day');
  assert(api.MEADOW === api.MEADOW_DAY, 'a named phase is the frozen set itself');
  api.setMeadowPalette('day', 'night', 0);
  assert(api.MEADOW === api.MEADOW_DAY, 'zero blend is still the set itself');
  api.setMeadowPalette('day', 'night', 0.5);
  assert(api.MEADOW !== api.MEADOW_DAY && api.MEADOW !== api.MEADOW_NIGHT, 'mid-crossing is neither');
  assert(typeof api.MEADOW.pondWater === 'string', 'and still reads as colour strings');
  api.setMeadowPalette('day'); // leave the module as we found it
});

// ---- the sun's position (v3): shadows lean and stretch with the hour ----

check('every phase says where its sun is', () => {
  for (const [name, pal] of [
    ['day', api.MEADOW_DAY],
    ['dusk', api.MEADOW_DUSK],
    ['night', api.MEADOW_NIGHT],
    ['dawn', api.MEADOW_DAWN],
  ]) {
    assert(typeof pal.shadowLean === 'number', `${name} has a lean`);
    assert(typeof pal.shadowLength === 'number', `${name} has a length`);
    assert(pal.shadowLength >= 1, `${name}: a shadow never shrinks below the caster`);
  }
});

check('shadows fall away from the sun the sky dial draws', () => {
  // skyForTick hands the dial t=0 (LEFT horizon) exactly as dawn begins
  // and t~1 (RIGHT) as sunset ends, and the dial runs left -> zenith ->
  // right. So the shadows must be thrown right at dawn and left at
  // sunset -- opposite signs, and each opposite to its own sun.
  assert(api.MEADOW_DAWN.shadowLean > 0.5, 'dawn: sun left, shadow right');
  assert(api.MEADOW_DUSK.shadowLean < -0.5, 'sunset: sun right, shadow left');
  assert(
    Math.sign(api.MEADOW_DAWN.shadowLean) !== Math.sign(api.MEADOW_DUSK.shadowLean),
    'and the two twilights are genuinely opposite',
  );
});

check('the shadow grows away from the light, not both ways', () => {
  // The geometry render.js and props.js both use: the sun-side edge stays
  // on the caster's own footprint and only the far edge travels.
  // The anchor is exact only at |lean| = 1; below that the sun-side edge
  // creeps out a little, which is the price of multiplying by `lean`
  // rather than its sign so nothing jumps as the lean crosses zero.
  const NEARLY = 0.2;
  const edges = (lean, length, footprint = 1) => {
    const halfWidth = footprint * length;
    const centre = lean * (halfWidth - footprint);
    return [centre - halfWidth, centre + halfWidth];
  };
  // Sunset: sun on the right, so the RIGHT edge should barely move while
  // the left one runs out.
  const [dl, dr] = edges(api.MEADOW_DUSK.shadowLean, api.MEADOW_DUSK.shadowLength);
  assert(Math.abs(dr - 1) < NEARLY, `sunset: sun-side edge stays put, got ${dr.toFixed(2)}`);
  assert(dl < -1.4, `sunset: the far edge runs out, got ${dl.toFixed(2)}`);
  // Dawn mirrors it.
  const [wl, wr] = edges(api.MEADOW_DAWN.shadowLean, api.MEADOW_DAWN.shadowLength);
  assert(Math.abs(wl + 1) < NEARLY, `dawn: sun-side edge stays put, got ${wl.toFixed(2)}`);
  assert(wr > 1.4, `dawn: the far edge runs out, got ${wr.toFixed(2)}`);
  // A light straight overhead has no side to run from, so it stays even.
  const [nl, nr] = edges(api.MEADOW_NIGHT.shadowLean, api.MEADOW_NIGHT.shadowLength);
  close(nl, -nr, 'overhead light stretches symmetrically');
});

check('noon is overhead and the moon has no direction', () => {
  assert(Math.abs(api.MEADOW_DAY.shadowLean) < 0.2, 'noon barely leans');
  close(api.MEADOW_DAY.shadowLength, 1, 'and casts the shortest shadow');
  close(api.MEADOW_NIGHT.shadowLean, 0, 'the moon reads as a lamp, not a low sun');
  assert(api.MEADOW_NIGHT.shadowLength > 1, 'but still stretches a little');
});

check('the sun swings round across a crossing rather than jumping', () => {
  // Numbers lerp in mixPalettes, so this comes for free -- which is the
  // reason the lean was made a number rather than a named direction.
  const mid = api.mixPalettes(api.MEADOW_DAY, api.MEADOW_DUSK, 0.5);
  const a = api.MEADOW_DAY.shadowLean;
  const b = api.MEADOW_DUSK.shadowLean;
  close(mid.shadowLean, (a + b) / 2, 'lean is halfway');
  close(
    mid.shadowLength,
    (api.MEADOW_DAY.shadowLength + api.MEADOW_DUSK.shadowLength) / 2,
    'length is halfway',
  );
  // And the long way round: night -> dawn passes through zero, so the
  // shadow shortens toward straight-down before swinging out the far side.
  const swing = api.mixPalettes(api.MEADOW_NIGHT, api.MEADOW_DAWN, 0.5);
  assert(
    swing.shadowLean > api.MEADOW_NIGHT.shadowLean &&
      swing.shadowLean < api.MEADOW_DAWN.shadowLean,
    'part way over',
  );
});

// ---- ground cover: a scatter the renderer can sort by depth ----

check('bushesFor is deterministic across independent evals', () => {
  const api2 = eval(src + EXPORTS);
  const a = api.bushesFor(40, 40, api.VIEW.meadow);
  const b = api2.bushesFor(40, 40, api.VIEW.meadow);
  assert(a.length > 0, 'some cover grows at all');
  assert(JSON.stringify(a) === JSON.stringify(b), 'same world, same shrubs');
});

check('cover density tracks bushChance', () => {
  const tiles = 60 * 60;
  const sparse = api.bushesFor(60, 60, { ...api.VIEW.meadow, bushChance: 0.02 }).length;
  const dense = api.bushesFor(60, 60, { ...api.VIEW.meadow, bushChance: 0.2 }).length;
  assert(dense > sparse * 4, `0.2 should far outgrow 0.02, got ${dense} vs ${sparse}`);
  assert(Math.abs(sparse / tiles - 0.02) < 0.01, `sparse share ${(sparse / tiles).toFixed(3)}`);
  assert(Math.abs(dense / tiles - 0.2) < 0.03, `dense share ${(dense / tiles).toFixed(3)}`);
});

check('cover keeps off tiles the server has put something on', () => {
  const all = api.bushesFor(40, 40, api.VIEW.meadow);
  assert(all.length > 3, 'enough cover to test with');
  // Occupy the first few and they must vanish, the rest untouched.
  const taken = new Set(all.slice(0, 3).map((b) => `${b.x},${b.y}`));
  const left = api.bushesFor(40, 40, api.VIEW.meadow, taken);
  assert(left.length === all.length - 3, `expected ${all.length - 3}, got ${left.length}`);
  for (const b of left) assert(!taken.has(`${b.x},${b.y}`), 'none on an occupied tile');
});

// ---- occupiedTiles x bushesFor: the two halves, composed ----

/**
 * WHICH elements the cover avoids is pinned next door, in test-motion.mjs
 * ("occupiedTiles keeps cover off water, and off nothing else"). This is the
 * other question, and the one neither side can answer alone: the two
 * functions meet over a `"x,y"` string and nothing else, so if `bushesFor`'s
 * lookup and `occupiedTiles`' key ever drift apart, cover silently stops
 * being excluded at all.
 *
 * Both unit tests stay green through exactly that: test-motion.mjs asserts
 * `has('3,4')` without ever calling `bushesFor`, and the hand-built set in
 * "cover keeps off tiles the server has put something on" never asks what
 * builds it. Verified 2026-08-07 by pointing `bushesFor` at `x:y` -- the
 * motion suite passed 33/33 and this check is what failed.
 */
check('the cover the renderer computes is the cover bushesFor honours', () => {
  // `occupiedTiles` never touches `this`, but going through a real instance
  // keeps this a test of the renderer's method rather than of a copy of it.
  const renderer = new api.WorldRenderer({ getContext: () => guardCtx() });
  const all = api.bushesFor(40, 40, api.VIEW.meadow);
  assert(all.length > 0, 'enough cover to test with');
  const spot = all[0]; // a tile the meadow does cover, so removing it shows

  const taken = renderer.occupiedTiles({
    elements: [
      { kind: 'water', id: 1, pos: { x: spot.x, y: spot.y } },
      { kind: 'bug', id: 2, pos: { x: spot.x, y: spot.y } }, // rides along, changes nothing
    ],
  });
  const left = api.bushesFor(40, 40, api.VIEW.meadow, taken);
  assert(left.length === all.length - 1, `expected ${all.length - 1}, got ${left.length}`);
  assert(!left.some((b) => b.x === spot.x && b.y === spot.y), 'and it is the water tile that went');
});

check('the lobed shrub\'s leaf ticks swing with the sun, and only as far as the dial', () => {
  // The owner saw these "off centre left" at dawn and "off centre right" at
  // dusk and reported them as two separate oddities. They are one term:
  // the four ticks are evenly spaced, so their cos offsets cancel exactly
  // and the motif's CENTRE is purely -shadowLean * r * bushLeafSwing. The
  // lobes and trunk do not move with it, which is why a large swing reads
  // as a part coming loose rather than as light.
  const centreOf = (swing, theme) => {
    api.setMeadowPalette(theme);
    const xs = [];
    const tile = 40;
    let r = 0;
    const ctx = new Proxy({}, {
      get: (_t, k) => {
        if (k === 'createLinearGradient') return () => ({ addColorStop() {} });
        // The ticks are the only ellipses drawn at this radius pair.
        if (k === 'ellipse') {
          return (x, _y, rx, ry) => { if (rx > 0 && Math.abs(ry / rx - 0.075 / 0.13) < 1e-6) { xs.push(x); r = rx / 0.13; } };
        }
        return () => {};
      },
      set: () => true,
    });
    const t = { ...api.VIEW.meadow, bushStyle: 'lobed', bushStyleAltShare: 0, bushLeafSwing: swing };
    api.drawBushAt(ctx, { x: 3, y: 4, seed: 0.42, tile, t });
    assert(xs.length === 4, `expected 4 leaf ticks, captured ${xs.length}`);
    return { centre: xs.reduce((s, v) => s + v, 0) / 4, r };
  };

  // At zero the motif is pinned to the crown in EVERY phase -- that is the
  // whole point of the dial, so it is the property worth guarding.
  const pinned = ['day', 'dusk', 'night', 'dawn'].map((ph) => centreOf(0, ph).centre);
  for (const c of pinned) {
    assert(Math.abs(c - pinned[0]) < 1e-9, 'swing 0 still moves the ticks between phases');
  }
  // And the swing is signed and proportional: dawn leans one way, dusk the
  // other. If these ever share a sign the cue has stopped tracking the sun.
  const r = centreOf(0.36, 'day').r;
  const dawn = centreOf(0.36, 'dawn').centre - pinned[0];
  const dusk = centreOf(0.36, 'dusk').centre - pinned[0];
  assert(dawn < 0 && dusk > 0, `dawn ${dawn.toFixed(2)} and dusk ${dusk.toFixed(2)} do not straddle`);
  // Magnitude follows the dial linearly, so halving it halves the travel.
  const half = centreOf(0.18, 'dawn').centre - pinned[0];
  assert(Math.abs(half - dawn / 2) < 1e-9, 'the swing is no longer linear in the dial');
  // Scale check in the units the owner sees: 0.29 canopy radii at dawn.
  assert(Math.abs(Math.abs(dawn) / r - 0.288) < 0.01,
    `dawn travel is ${(Math.abs(dawn) / r).toFixed(3)} radii, not the 0.288 measured`);
});

check('drawBushAt sweeps clean in every style, at every size', () => {
  for (const bushStyle of ['cover', 'tuft', 'bramble', 'shrub']) {
    for (const tile of [8, 22, 54]) {
      const t = { ...api.VIEW.meadow, bushStyle };
      // A guarding ctx throws on any non-finite argument.
      api.drawBushAt(guardCtx(), { x: 3, y: 4, seed: 0.42, tile, t });
      api.drawBushAt(guardCtx(), { x: 0, y: 0, seed: 0, tile, t });
      api.drawBushAt(guardCtx(), { x: 9, y: 9, seed: 0.999, tile, t });
    }
  }
});

check('standing styles cast a shadow, flat ones do not', () => {
  const shadowsIn = (bushStyle) => {
    const log = [];
    api.drawBushAt(guardCtx(log), {
      // `bushStyleAltShare` pinned to 0, or this tile may hash into the
      // ALT species and the check silently tests a style it did not name.
      // It shipped at 0 when this was written; the owner's mix (0.7) is
      // what exposed it.
      x: 2, y: 2, seed: 0.5, tile: 40,
      t: { ...api.VIEW.meadow, bushStyle, bushStyleAltShare: 0 },
    });
    return log.filter(([c, p, v]) => c === 'set' && p === 'fillStyle'
      && String(v) === String(api.MEADOW.groundShadow)).length;
  };
  for (const standing of ['shrub', 'grown', 'trunk', 'tall']) {
    assert(shadowsIn(standing) === 1, `${standing} stands up, so it casts`);
  }
  for (const flat of ['cover', 'tuft', 'bramble']) {
    assert(shadowsIn(flat) === 0, `${flat} lies on the ground and casts nothing`);
  }
});

check('pondInradius measures the circle that fits, not the tile count', () => {
  const P2 = (x, y) => ({ x, y });
  const r = (tiles) => api.pondInradius(tiles);
  const lone = r([P2(0, 0)]);
  const lake = r([P2(0, 0), P2(1, 0), P2(0, 1), P2(1, 1)]);
  const river = r([P2(0, 0), P2(1, 0), P2(2, 0), P2(3, 0)]);
  // Each within a lattice step of the true 0.5 / 1.0 / 0.5.
  assert(Math.abs(lone - 0.5) < 0.1, `lone tile ${lone}`);
  assert(Math.abs(lake - 1.0) < 0.1, `2x2 lake ${lake}`);
  assert(Math.abs(river - 0.5) < 0.1, `river ${river}`);
  // The one that matters, and the one an area-based estimate gets exactly
  // backwards: a four-tile river is as tight as a lone tile, not as roomy
  // as a four-tile lake. Rivers are a sketched future shape.
  assert(river < lake * 0.7, `a 1-wide river (${river}) must read tighter than a lake (${lake})`);
  assert(Math.abs(river - lone) < 0.1, 'and about as tight as a lone tile');
  // A reentrant corner has to count: axis rays alone read an L as 0.88.
  const ell = r([P2(0, 0), P2(1, 0), P2(1, 1)]);
  assert(ell < 0.7, `an L is 1-wide everywhere, got ${ell}`);
});

check('the depth blur is clamped so every pond has a middle', () => {
  const d = api.MEADOW_DEFAULTS;
  const depthAt = (tiles) => {
    const rad = api.pondInradius(tiles);
    const sigma = Math.min(d.pondDepthBlurTiles, rad / d.pondDepthBlurClamp);
    return 1 - Math.exp(-(rad * rad) / (2 * sigma * sigma));
  };
  const P2 = (x, y) => ({ x, y });
  const shapes = {
    'lone tile': [P2(0, 0)],
    '2x2 lake': [P2(0, 0), P2(1, 0), P2(0, 1), P2(1, 1)],
    river: [P2(0, 0), P2(1, 0), P2(2, 0), P2(3, 0)],
  };
  for (const [name, tiles] of Object.entries(shapes)) {
    // Unclamped, the spec's 0.95 leaves a lone tile at 18% and even our
    // 2x2 lake at 49% -- every pond in this world running pale.
    const bare = 1 - Math.exp(-(api.pondInradius(tiles) ** 2) / (2 * d.pondDepthBlurTiles ** 2));
    assert(bare < 0.55, `${name} would not need the clamp (${bare})`);
    assert(depthAt(tiles) > 0.75, `${name} still has no middle (${depthAt(tiles)})`);
  }
});

/* ---- the renderer's own pond path ----
 *
 * Everything above tests the meadow's functions directly. `drawPondLayer` is
 * the only place they are wired TOGETHER, and nothing executed it: the lab
 * calls groupWaterTiles / buildPondLayers / drawPonds itself, and no check
 * had ever constructed a WorldRenderer. A missing `groupWaterTiles` call
 * shipped through that gap and took the live world down to bare ground and
 * sunbeams -- every entity draws AFTER the ponds, so one throw there removes
 * all of them. These checks exist so that cannot happen twice. */

/** The live world's water: one 2x2 lake and three lone tiles (kitties.ai,
 *  2026-08-09). Grouping is the whole point -- 7 tiles must become 4 ponds. */
const LIVE_WATER = [
  { x: 10, y: 2 }, { x: 11, y: 2 }, { x: 10, y: 3 }, { x: 11, y: 3 },
  { x: 3, y: 18 }, { x: 12, y: 13 }, { x: 19, y: 1 },
];

function rendererFor(water) {
  const renderer = new api.WorldRenderer(mockCanvas(640, 640));
  renderer.tile = 32;
  renderer.dpr = 1;
  renderer.cssWidth = 640;
  renderer.cssHeight = 640;
  const world = {
    width: 20,
    height: 20,
    kitties: [],
    elements: water.map((pos, i) => ({ id: i + 1, kind: 'water', pos })),
  };
  const view = { elementAlphaFor: () => 1, expiredAlpha: 0, ambient: { now: 0 } };
  return { renderer, world, view };
}

check('the renderer draws the live world\'s ponds without throwing', () => {
  const { renderer, world, view } = rendererFor(LIVE_WATER);
  renderer.drawPondLayer(world, view); // threw ReferenceError before the fix
  assert(renderer.pondCache, 'a cache was built');
  assert(
    renderer.pondCache.ponds.length === 4,
    `7 water tiles group into 4 ponds, got ${renderer.pondCache.ponds.length}`,
  );
  const sizes = renderer.pondCache.ponds.map((p) => p.tiles.length).sort();
  assert(String(sizes) === '1,1,1,4', `one lake and three lone tiles, got ${sizes}`);
  assert(renderer.pondCache.layers, 'and the depth layers baked');
});

/* ---- a cat IN the water, drawn as a whole frame ----
 *
 * The pond checks above draw the water. Nothing drew a CAT in it, and the
 * new water model (2026-08-10) lives entirely in the kitty path: the
 * submersion sample, the waterline clip, and `drawWaterline`, which reaches
 * outside render.js for `MEADOW.pondMeniscus` and `lightenHex`. A missing
 * palette key or an undefined helper there is a throw in the middle of the
 * kitty loop -- and every cat after it would vanish, which is the same
 * shape of failure the pond regression had.
 *
 * So this drives the REAL renderer over the REAL Presentation's view, in
 * every theme, with a cat at a series of positions from the pond's middle
 * out onto dry grass. */
check("the hunter's gate is WIRED: the renderer measures the quarry", () => {
  // The gate lives in anim.js; the distance that feeds it is measured in
  // render.js. Either half is right on its own while the pair does nothing,
  // and every unit check stays green -- so this asks what the RENDERER
  // hands over, from a real world, for a real pursuit.
  //
  // Asserted at the seam rather than in the pixels: cat-v2 is inert in this
  // harness (it registers CatV2 and declares nothing else), so a frame here
  // draws a V1 cat, which has no focused eyes to compare. That is a real
  // limit of this harness, not of the feature.
  const seen = [];
  const p = new api.Presentation();
  const realExpression = p.expressionFor.bind(p);
  p.expressionFor = (kitty, quarryDist) => {
    seen.push(quarryDist);
    return realExpression(kitty, quarryDist);
  };
  const renderer = new api.WorldRenderer(mockCanvas(640, 640, []));
  renderer.tile = 32; renderer.dpr = 1; renderer.cssWidth = 640; renderer.cssHeight = 640;
  const at = (bugX) => ({
    tick: 10, width: 20, height: 20,
    elements: [{ id: 9, kind: 'bug', pos: { x: bugX, y: 2 } }],
    kitties: [{
      id: 1, name: 'Miso', pos: { x: 2, y: 2 }, needs: {}, happiness: 90,
      pursuit: { target: { target: 'element', id: 9 }, started: 1, closest: 3, improved_at: 1 },
      last_action: { action: 'chase', target: 'element', id: 9 },
    }],
  });
  p.pushState(at(9), 1000);
  p.pushState(at(9), 1800);
  renderer.draw(p.curr, p.viewAt(2200, false));
  assert(seen.length === 1, `expressionFor was called ${seen.length} times, want 1`);
  assert(seen[0] === 7, `the renderer measured ${seen[0]} tiles to a bug 7 away`);

  // The pursuit and the applied action name DIFFERENT things all the time
  // -- this shape is verbatim from the candidate world, a cat that stopped
  // for a drink without giving up on its bug. Measuring `last_action` here
  // would read null and hand the face back at any distance.
  const seen2 = [];
  p.expressionFor = (kitty, quarryDist) => {
    seen2.push(quarryDist);
    return realExpression(kitty, quarryDist);
  };
  const distracted = {
    tick: 11, width: 20, height: 20,
    elements: [{ id: 9, kind: 'bug', pos: { x: 9, y: 2 } }],
    kitties: [{
      id: 1, name: 'Miso', pos: { x: 2, y: 2 }, needs: {}, happiness: 90,
      pursuit: { target: { target: 'element', id: 9 }, started: 1, closest: 3, improved_at: 1 },
      last_action: { action: 'drink' },
    }],
  };
  p.pushState(distracted, 2600);
  renderer.draw(p.curr, p.viewAt(3000, false));
  assert(seen2[0] === 7,
    `a cat drinking mid-pursuit measured ${seen2[0]} -- the distance is coming off last_action, not the pursuit`);

  // ...and the value it hands over is the one the gate then acts on.
  const gate = api.VIEW.hunterGateTiles;
  const hunting = at(9).kitties[0];
  assert(realExpression(hunting, gate) === 'focused', 'at the gate the face is on');
  assert(realExpression(hunting, gate + 1) === undefined, 'past the gate the face is off');
});

check('a purr draws its glyph; a request still draws its bubble', () => {
  const wasOn = api.PURR.on;
  api.PURR.on = 1;
  // The split, checked through a whole frame rather than by calling
  // drawBubbles directly -- the glyph reaches for `drawPurrGlyph` and
  // `PURR` across a file boundary, and props.js is exactly the kind of
  // dependency that is present in a harness and missing in the browser.
  const frame = (meows, purringUntil = undefined) => {
    const log = [];
    const renderer = new api.WorldRenderer(mockCanvas(640, 640, log));
    renderer.tile = 32;
    renderer.dpr = 1;
    renderer.cssWidth = 640;
    renderer.cssHeight = 640;
    const kitties = [{
      id: 1, name: 'Miso', pos: { x: 5, y: 5 }, needs: {}, happiness: 90,
      purring_until: purringUntil,
    }];
    const at = (tick) => ({
      tick, width: 20, height: 20, elements: [], kitties, recent_meows: meows,
    });
    const p = new api.Presentation();
    p.pushState(at(9), 1000);
    p.pushState(at(10), 1800);
    renderer.draw(p.curr, p.viewAt(2200, false));
    return log.filter((e) => e[0] === 'fillText').map((e) => String(e[1]));
  };

  // The heart is state-driven: `purring_until` is what says a cat is
  // rumbling. Its meow is only the announcement, and carries no duration.
  const purr = frame([{ kitty_id: 1, kind: 'purr', tick: 9 }], 14);
  assert(purr.some((t) => t.includes('\u{1F497}')), 'a purring cat should draw the glyph');
  assert(!purr.some((t) => t.includes('purrrr')),
    'a purr still drew its speech bubble -- the whole point was to take it out');

  const asks = frame([{ kitty_id: 1, kind: 'want_eat', tick: 9 }]);
  assert(asks.some((t) => t.includes('I want to eat')), 'a request must keep its bubble');
  assert(!asks.some((t) => t.includes('\u{1F497}')), 'a request should not summon the purr glyph');

  // Both live at once: they want the same space above the cat, and the
  // thing a viewer can act on wins.
  const both = frame([{ kitty_id: 1, kind: 'want_eat', tick: 9 }], 14);
  assert(both.some((t) => t.includes('I want to eat')), 'the request must survive a purr');
  assert(!both.some((t) => t.includes('\u{1F497}')), 'the mood must give way to the request');

  // And nothing at all when the cat has said nothing.
  assert(!frame([]).some((t) => t.includes('\u{1F497}')), 'a silent cat should draw no glyph');
  // A cat whose purr has ENDED is silent, even though its meow is still in
  // the recent window -- which is the whole point of reading the state.
  assert(!frame([{ kitty_id: 1, kind: 'purr', tick: 9 }], 9).some((t) => t.includes('\u{1F497}')),
    'a finished purr still drew a heart');

  // The switch itself: off is off, and it is what SHIPS.
  api.PURR.on = 0;
  assert(!frame([], 14).some((t) => t.includes('\u{1F497}')),
    'the purr glyph drew with the switch off');
  assert(frame([{ kitty_id: 1, kind: 'want_eat', tick: 9 }]).some((t) => t.includes('I want to eat')),
    'turning purrs off must not touch request bubbles');
  api.PURR.on = wasOn;
  assert(api.PURR.on === 0,
    'the purr glyph ships OFF -- a heart popped in every 3s on the candidate roster, 20 a minute');
});

check('the heart is up for the whole purr, because it reads the purr', () => {
  // Two wrong answers preceded this one, both from keying the heart to the
  // MEOW. A purr is background state that runs 9-13 ticks; its meow is a
  // one-tick announcement -- so the heart flashed where a cat was rumbling
  // for the better part of ten seconds. And a meow is never served on the
  // tick it happened, so a dwell counted off its age was off by one too.
  //
  // `purring_until` is the engine's own answer, documented as the viewer's
  // "rumbling now" signal. Reading it retires the dwell constant and every
  // off-by-one that came with it.
  const wasOn = api.PURR.on;
  api.PURR.on = 1;
  const drawnAt = (tick, until) => {
    const log = [];
    const renderer = new api.WorldRenderer(mockCanvas(640, 640, log));
    renderer.tile = 32; renderer.dpr = 1; renderer.cssWidth = 640; renderer.cssHeight = 640;
    const kitties = [{
      id: 1, name: 'Miso', pos: { x: 5, y: 5 }, needs: {}, happiness: 90,
      purring_until: until,
    }];
    const at = (t) => ({ tick: t, width: 20, height: 20, elements: [], kitties, recent_meows: [] });
    const p = new api.Presentation();
    p.pushState(at(tick - 1), 1000);
    p.pushState(at(tick), 1800);
    renderer.draw(p.curr, p.viewAt(2200, false));
    return log.some((e) => e[0] === 'fillText' && String(e[1]).includes('\u{1F497}'));
  };
  // A ten-tick purr, from its first tick to its last and one past.
  const on = [];
  for (let t = 10; t <= 21; t += 1) if (drawnAt(t, 20)) on.push(t);
  api.PURR.on = wasOn;
  assert(on.length === 11, `a purr ending at 20 showed on ${on.length} ticks, want 11`);
  assert(on[0] === 10 && on[on.length - 1] === 20,
    `showed ${on[0]}..${on[on.length - 1]} -- the purr ends AT purring_until, inclusive`);
  assert(!drawnAt(21, 20), 'the heart outlived the purr');
  assert(api.PURR.ticks === undefined,
    'a dwell constant is back -- the served state is the duration, there is nothing to dial');
});
check('the purr glyph is actually buzzing in a live frame', () => {
  const wasOn = api.PURR.on;
  api.PURR.on = 1;
  // The glyph is only as alive as the phase the RENDERER hands it, and the
  // two halves are in different files: props.js knows how to shake, and
  // render.js decides what to shake by. Handing over a constant leaves a
  // perfectly correct glyph nailed to the spot, and every check that talks
  // to `drawPurrGlyph` directly still passes. So this asks the frame.
  const xAt = (nowMs) => {
    const log = [];
    const renderer = new api.WorldRenderer(mockCanvas(640, 640, log));
    renderer.tile = 32;
    renderer.dpr = 1;
    renderer.cssWidth = 640;
    renderer.cssHeight = 640;
    const kitties = [{
      id: 1, name: 'Miso', pos: { x: 5, y: 5 }, needs: {}, happiness: 90,
      purring_until: 20,
    }];
    const at = (tick) => ({
      tick, width: 20, height: 20, elements: [], kitties,
      recent_meows: [],
    });
    const p = new api.Presentation();
    p.pushState(at(9), 1000);
    p.pushState(at(10), 1800);
    renderer.draw(p.curr, p.viewAt(nowMs, false));
    return log.filter((e) => e[0] === 'fillText' && String(e[1]).includes('\u{1F497}'))[0][2];
  };
  // Half a shake apart at the shipped rate, which is the widest the glyph
  // ever travels.
  const half = 500 / api.PURR.shakeHz;
  const spread = Math.abs(xAt(2000) - xAt(2000 + half));
  api.PURR.on = wasOn;
  assert(spread > api.PURR.shakeMinPx,
    `the glyph moved ${spread.toFixed(2)}px across half a shake -- the renderer is feeding it a constant`);
});

check('the purr buzz scales with the glyph, with a floor so it survives the tile', () => {
  // This check asserted the OPPOSITE an hour ago -- a flat pixel travel, on
  // the argument that a vibration is judged by how far it moves on screen.
  // The owner watched it and that is wrong: the eye judges displacement
  // relative to the thing moving, so a flat 0.8px was a 9.6% lurch on the
  // live glyph against a 3.2% tremble on the big one. Cute large, frantic
  // small.
  //
  // Proportion alone cannot do it either, which is why there are two dials:
  // anchored on the large view, the live tile lands under a pixel and
  // disappears. The share sets the character; the floor keeps it visible at
  // the tile the world actually draws at.
  const amp = (tile) => {
    const at = (phase) => {
      const log = [];
      api.drawPurrGlyph(guardCtx(log), 100, 50, tile, phase);
      return log.filter((e) => e[0] === 'fillText')[0][2];
    };
    return (at(0.25) - at(0.75)) / 2;
  };
  const glyph = (tile) => api.PURR.size * tile;
  const shareAt = (tile) => amp(tile) / glyph(tile);

  // Above the floor it is pure proportion: double the glyph, double the
  // travel, and its share of the glyph does not move.
  assert(Math.abs(shareAt(120) - shareAt(240)) < 1e-9,
    `not proportional up there: ${(shareAt(120) * 100).toFixed(2)}% against ${(shareAt(240) * 100).toFixed(2)}%`);
  assert(Math.abs(amp(240) - amp(120) * 2) < 1e-9, 'doubling the glyph should double the travel');

  // At the tile the world draws at, the floor is what holds it up -- and it
  // still has to be worth drawing.
  // Compared with a tolerance: the amplitude is read back out of two
  // absolute x positions, so 100.4 minus 99.6 does not land on 0.4.
  assert(Math.abs(amp(31) - api.PURR.shakeMinPx) < 1e-9,
    `the floor should be binding at the live tile, got ${amp(31).toFixed(4)}`);
  assert(amp(31) * 2 >= 0.75, `only ${(amp(31) * 2).toFixed(2)}px peak to peak at 31px -- invisible`);
  // ...and calmer than the flat-pixel version the owner rejected, which put
  // 0.8px of amplitude on an 8.4px glyph.
  assert(shareAt(31) < 0.08,
    `the live glyph still lurches ${(shareAt(31) * 100).toFixed(1)}% of its own width`);

  // Phase 0 is what a still frame hands over (`propPhaseFor` returns 0
  // there), and it must still DRAW -- reduced motion keeps the purr, it
  // just stops it buzzing.
  const still = [];
  api.drawPurrGlyph(guardCtx(still), 100, 50, 31, 0);
  const drawn = still.filter((e) => e[0] === 'fillText');
  assert(drawn.length === 1, 'a still frame should still draw the glyph');
  assert(drawn[0][2] === 100 + api.PURR.offsetX * 31, 'at phase 0 the glyph sits at rest');
});
check('the renderer draws a cat in the water, in every theme, without throwing', () => {
  const themes = ['day', 'dusk', 'night', 'dawn'];
  for (const theme of themes) {
    api.setMeadowPalette(theme, null, 0);
    for (const x of [10, 10.5, 11, 11.5, 12, 13]) {
      const renderer = new api.WorldRenderer(mockCanvas(640, 640));
      renderer.tile = 32;
      renderer.dpr = 1;
      renderer.cssWidth = 640;
      renderer.cssHeight = 640;
      renderer.theme = theme;
      const elements = LIVE_WATER.map((pos, i) => ({ id: i + 1, kind: 'water', pos }));
      const kitties = [{ id: 1, name: 'Miso', pos: { x: 10, y: 2 }, needs: {}, happiness: 90 }];
      const p = new api.Presentation();
      const at = (tick, pos) => ({ tick, width: 20, height: 20, elements, kitties: [{ ...kitties[0], pos }] });
      p.pushState(at(1, { x: 10, y: 2 }), 1000);
      p.pushState(at(2, { x: Math.round(x), y: 2 }), 1800);
      const view = p.viewAt(2200, false);
      // The whole frame, not a hand-picked layer: the point is the wiring.
      renderer.draw(p.curr, view);
    }
  }
  api.setMeadowPalette('day', null, 0);
});

check('the renderer draws a cat walking north and south, in a whole frame', () => {
  // Covers the served-step half of the chain -- dy -> facingFor -> a whole
  // frame that does not throw -- and walks the cat through the pond at
  // (10,2)-(11,3) on the way, so a vertical walk and the waterline clip
  // land on the same frame.
  //
  // It does NOT reach `applyAxial`, and cannot: this harness evals every
  // file into one scope, where render.js's bare `drawCat` binds to cat.js's
  // v1 function rather than v2's (cat.js is eval'd first and its function
  // declaration is in scope). Verified by mutation -- throwing inside
  // applyAxial does not fail this check. The axial DRAWING is covered by
  // unit checks in test-motion instead, and the reason it is hard to reach
  // here is the same globals trap that had the feature shipping inert:
  // see 'every cat-v2 symbol the page reads bare is actually installed'.
  const renderer = new api.WorldRenderer(mockCanvas(640, 640));
  renderer.tile = 32;
  renderer.dpr = 1;
  renderer.cssWidth = 640;
  renderer.cssHeight = 640;
  const elements = LIVE_WATER.map((pos, i) => ({ id: i + 1, kind: 'water', pos }));
  const p = new api.Presentation();
  const at = (tick, x, y) => ({
    tick,
    width: 20,
    height: 20,
    elements,
    kitties: [{ id: 1, name: 'Miso', pos: { x, y }, needs: {}, happiness: 90 }],
  });
  // North up the pond column, then back south through it.
  const walk = [[10, 6], [10, 5], [10, 4], [10, 3], [10, 2], [10, 1], [10, 2], [10, 3], [10, 4]];
  let tick = 1;
  let now = 1000;
  p.pushState(at(tick++, 10, 7), now);
  const seen = new Set();
  for (const [x, y] of walk) {
    now += 800;
    p.pushState(at(tick++, x, y), now);
    seen.add(p.facingFor(1));
    renderer.draw(p.curr, p.viewAt(now + 400, false));
  }
  assert(seen.has('north'), `never faced north, saw ${[...seen]}`);
  assert(seen.has('south'), `never faced south, saw ${[...seen]}`);
});

check('the meniscus colour is a theme’s answer, not a constant', () => {
  // That every phase NAMES a pondMeniscus is checked above. What matters
  // for the surface the cat meets is that the values actually differ: the
  // handoff drew this by lightening pondWater 50% toward white, which is a
  // constant wearing a palette's clothes and lands 33.5 L* too bright at
  // night. A palette whose entries had collapsed to one value would pass
  // the naming check and reintroduce exactly that.
  const l = (name) => {
    api.setMeadowPalette(name, null, 0);
    return lstar(api.MEADOW.pondMeniscus);
  };
  const byDay = l('day');
  const byNight = l('night');
  assert(
    byDay - byNight > 40,
    `night's surface must be far darker than day's: ${byDay.toFixed(1)} vs ${byNight.toFixed(1)}`,
  );
  api.setMeadowPalette('day', null, 0);
});

check('the pond cache rebuilds only when the water moves', () => {
  const { renderer, world, view } = rendererFor(LIVE_WATER);
  renderer.drawPondLayer(world, view);
  const first = renderer.pondCache;
  renderer.drawPondLayer(world, view);
  assert(renderer.pondCache === first, 'same water, same cache -- no re-blur per frame');
  world.elements.push({ id: 99, kind: 'water', pos: { x: 5, y: 5 } });
  renderer.drawPondLayer(world, view);
  assert(renderer.pondCache !== first, 'new water rebuilds it');
  assert(renderer.pondCache.ponds.length === 5, 'and the new tile is its own pond');
});

check('a world with no water clears the cache instead of baking one', () => {
  const { renderer, world, view } = rendererFor(LIVE_WATER);
  renderer.drawPondLayer(world, view);
  assert(renderer.pondCache, 'cached with water');
  world.elements = [];
  renderer.drawPondLayer(world, view);
  assert(renderer.pondCache === null, 'and cleared without it');
});


/* ---- spec 03: cover grows in drifts ----
 *
 * The acceptance criterion that keeps this honest is the first one: the
 * drift field REDISTRIBUTES cover, it does not add any. Without it, "the
 * meadow looks lusher" is indistinguishable from "we quietly grew more
 * grass", and the whole change becomes unfalsifiable.
 */
check('cover clusters WITHOUT changing how much of it there is', () => {
  const t = api.MEADOW_DEFAULTS;
  const KINDS = [
    ['blade', api.MEADOW_SALTS.blade, t.bladeChance, 'blade'],
    ['bloom', api.MEADOW_SALTS.bloom, t.bloomChance, 'bloom'],
    ['shrub', api.MEADOW_SALTS.bush, t.bushChance, 'bush'],
  ];
  // Several sizes, because the first cut of this normalised to the NOMINAL
  // rate and looked fine at one size while cutting shrubs by 38% at
  // another: a few hundred tiles is far too small a sample for the hash to
  // look uniform at a 1.5% threshold, so the flat scatter's realised count
  // is not its nominal one. 20x20 is the live world.
  for (const [w, h] of [[20, 20], [24, 24], [40, 40]]) {
    const drift = api.driftField(w, h, t);
    for (const [name, salt, base, key] of KINDS) {
      let flat = 0;
      let clustered = 0;
      let fertHit = 0;
      let fertAll = 0;
      for (let y = 0; y < h; y++) {
        for (let x = 0; x < w; x++) {
          const i = y * w + x;
          const hash = api.tileHash(x, y, salt);
          fertAll += drift.fertility[i];
          if (hash >= 1 - base) flat++;
          if (hash >= 1 - drift[key][i]) { clustered++; fertHit += drift.fertility[i]; }
        }
      }
      assert(flat > 0, `${w}x${h} ${name}: nothing to compare against`);
      const drift10 = Math.max(1, Math.round(flat * 0.1));
      assert(
        Math.abs(clustered - flat) <= drift10,
        `${w}x${h} ${name}: ${flat} -> ${clustered}, outside the +/-10% the spec allows`,
      );
      // ...and it must actually CLUSTER. Conserving the count is trivially
      // satisfied by changing nothing at all, so the pair of assertions is
      // the check: cover must land on better-than-average ground.
      const meanAll = fertAll / (w * h);
      const meanHit = fertHit / clustered;
      assert(
        meanHit > meanAll * 1.15,
        `${w}x${h} ${name}: lands on ground of fertility ${meanHit.toFixed(3)} against a field mean of ${meanAll.toFixed(3)} -- not clustered`,
      );
    }
  }
});

check('the drift field is a pure function of the world and its dials', () => {
  const t = api.MEADOW_DEFAULTS;
  // Cover must be stable across a session -- the whole reason occupiedTiles
  // was narrowed to water only was to stop scenery flickering.
  const a = api.driftField(20, 20, t);
  const b = api.driftField(20, 20, t);
  assert(a === b, 'the same world should hand back the memoised field');
  const fresh = api.driftField(20, 20, { ...t });
  for (let i = 0; i < 400; i++) {
    assert(fresh.blade[i] === a.blade[i], `blade chance moved at tile ${i}`);
    assert(fresh.bush[i] === a.bush[i], `bush chance moved at tile ${i}`);
  }
  // A re-dial must actually re-solve rather than serve the old field.
  const broader = api.driftField(20, 20, { ...t, fertilityCells: 11 });
  let same = 0;
  for (let i = 0; i < 400; i++) if (broader.blade[i] === a.blade[i]) same++;
  assert(same < 400, 'a re-dialled fertilityCells returned the cached field');
});

/* ---- spec 03 part 2: the ground ---- */

/** A ctx that records what it was asked to draw, and hands out a DISTINCT
 *  recorder for any offscreen made while it is active. */
function recordingWorld() {
  const outer = [];
  const scratches = [];
  const make = (log) => new Proxy({ filter: 'none' }, {
    get: (t, k) => {
      if (k === 'createLinearGradient' || k === 'createRadialGradient') {
        return (...a) => { log.push([String(k), ...a]); return { addColorStop: (o, c) => log.push(['stop', o, c]) }; };
      }
      if (k === 'getTransform') return () => ({ a: 1, d: 1 });
      if (k === 'canvas') return { width: 1, height: 1 };
      if (k in t) return t[k];
      return (...a) => {
        for (const v of a) {
          if (typeof v === 'number' && !Number.isFinite(v)) throw new Error(`${String(k)} non-finite: ${a}`);
        }
        log.push([String(k), ...a]);
      };
    },
    set: (t, k, v) => { t[k] = v; log.push(['set', String(k), v]); return true; },
    has: (t, k) => k in t,
  });
  const realCreate = globalThis.document.createElement;
  globalThis.document.createElement = (tag) => {
    if (tag !== 'canvas') return realCreate(tag);
    const log = [];
    scratches.push(log);
    return { width: 0, height: 0, style: {}, dataset: {}, getContext: () => make(log) };
  };
  return { ctx: make(outer), outer, scratches, done: () => { globalThis.document.createElement = realCreate; } };
}

check('the blur softens the ground and spares what grows on it', () => {
  const w = recordingWorld();
  try {
    api.setMeadowPalette('day', null, 0);
    api.drawMeadowGround(w.ctx, { width: 12, height: 12, tile: 26, cover: false });
  } finally {
    w.done();
  }
  const blur = w.outer.find((o) => o[0] === 'set' && o[1] === 'filter' && String(o[2]).startsWith('blur('));
  assert(blur, 'the tone layer was never blurred');
  assert(w.outer.some((o) => o[0] === 'drawImage'), 'the blurred layer was never composited back');
  assert(w.scratches.length > 0, 'no offscreen was made, so nothing was blurred in isolation');
  // The point of doing it this way: tufts are drawn AFTER the blur, on the
  // outer ctx. Fold them into the blurred layer and 0.32 tiles does not
  // soften a blade of grass, it erases it.
  const tufts = (log) => log.filter((o) => o[0] === 'quadraticCurveTo').length;
  assert(tufts(w.outer) > 0, 'the grass tufts were not drawn on the un-blurred ctx');
  for (const scratch of w.scratches) {
    assert(tufts(scratch) === 0, 'grass was drawn INSIDE the blurred layer and will be erased by it');
  }
});

check('the light wash follows shadowLean, so the world agrees where the sun is', () => {
  const seen = {};
  for (const theme of ['day', 'dusk', 'night', 'dawn']) {
    const w = recordingWorld();
    try {
      api.setMeadowPalette(theme, null, 0);
      api.drawMeadowGround(w.ctx, { width: 12, height: 12, tile: 26, cover: false });
    } finally {
      w.done();
    }
    const grad = w.outer.find((o) => o[0] === 'createLinearGradient');
    assert(grad, `${theme}: no light wash`);
    seen[theme] = { x0: grad[1], x1: grad[3], lean: api.MEADOW.shadowLean };
    assert(typeof api.MEADOW.sunTint === 'string', `${theme} names no sunTint`);
  }
  // Dusk and dawn lean hard the opposite way from each other (-0.85 vs
  // +0.8), so the wash must run across the field in opposite directions.
  // Asserted as a RELATION, not against a coordinate, so re-dialling the
  // lean does not need this edited.
  const duskDir = Math.sign(seen.dusk.x1 - seen.dusk.x0);
  const dawnDir = Math.sign(seen.dawn.x1 - seen.dawn.x0);
  assert(duskDir !== 0, 'dusk washes straight down the field despite a hard lean');
  assert(
    duskDir === -dawnDir,
    `dusk (lean ${seen.dusk.lean}) and dawn (lean ${seen.dawn.lean}) must wash from opposite sides`,
  );
});

check('a meadow can grow two kinds of shrub, in any mix', () => {
  const t = api.MEADOW_DEFAULTS;
  const kindOf = (b, share) =>
    share > 0 && api.tileHash(b.x, b.y, api.MEADOW_SALTS.bushKind) < share ? 'alt' : 'primary';
  const shrubs = api.bushesFor(20, 20, t, null);
  assert(shrubs.length > 4, 'not enough shrubs to say anything about a mix');

  // Pinned to the owner's bake (2026-08-12: 0.3, so about three clumps in
  // ten are the small trees and the rest is flat cover). Pinned
  // rather than freed, per this file's convention for judged art: an
  // accidental edit is caught, and a deliberate one moves this line. The
  // assertion below it does not depend on the shipped value.
  assert(t.bushStyleAltShare === 0.3, `the alt share moved: ${t.bushStyleAltShare}`);
  assert(shrubs.every((b) => kindOf(b, 0) === 'primary'), 'share 0 grew an alt');
  assert(shrubs.every((b) => kindOf(b, 1) === 'alt'), 'share 1 grew a primary');

  // ...and in between, both. Asserted as "some of each" rather than an
  // exact split: 13 shrubs cannot land on a ratio, and pinning one would
  // fail the day the world changes size.
  const half = shrubs.map((b) => kindOf(b, 0.5));
  assert(half.includes('alt') && half.includes('primary'), 'a 50% mix grew only one kind');

  // A shrub must not change species between frames -- scenery that
  // flickers is the exact thing occupiedTiles was narrowed to prevent.
  const again = api.bushesFor(20, 20, t, null).map((b) => kindOf(b, 0.5));
  assert(String(half) === String(again), 'a shrub changed species between calls');

  // Both silhouettes have to actually draw, in every phase. The guard ctx
  // throws on non-finite geometry, which is what a mis-scaled lobe or an
  // undefined palette entry produces.
  for (const phase of ['day', 'dusk', 'night', 'dawn']) {
    api.setMeadowPalette(phase, null, 0);
    for (const style of [t.bushStyle, t.bushStyleAlt]) {
      for (const b of shrubs) {
        api.drawBushAt(guardCtx(), { ...b, tile: 48, t: { ...t, bushStyle: style, bushStyleAltShare: 0 } });
      }
    }
  }
  api.setMeadowPalette('day', null, 0);
});

check('the meadow lab dials every tunable the meadow ships', () => {
  // Spec 03 added eight tunables and no way to judge any of them: the lab
  // says so at runtime in its own banner, but only if someone opens it.
  // This is that banner, in CI.
  //
  // A dial that exists with no surface to judge it is how art values get
  // baked from a spec's suggestion rather than from the owner's eye, which
  // is the one thing the house method exists to prevent.
  const lab = readFileSync(join(here, 'gallery-meadow.html'), 'utf8');
  const ranges = lab.match(/const RANGES = \{[\s\S]*?\n {2}\};/);
  const elsewhere = lab.match(/const ELSEWHERE = new Set\(\[[\s\S]*?\]\);/);
  assert(ranges && elsewhere, 'could not find the lab\'s dial tables -- has it been restructured?');
  const dialled = [...ranges[0].matchAll(/^ {4}([A-Za-z_][\w]*):/gm)].map((m) => m[1]);
  const parked = [...elsewhere[0].matchAll(/'([^']+)'/g)].map((m) => m[1]);
  assert(dialled.length > 20, `only parsed ${dialled.length} dials -- the parse broke`);

  const keys = Object.keys(api.MEADOW_DEFAULTS);
  const undialled = keys.filter((k) => !dialled.includes(k) && !parked.includes(k));
  assert(
    undialled.length === 0,
    `shipped with no way to judge them: ${undialled.join(', ')} -- add to RANGES, or to ELSEWHERE if another lab owns them`,
  );
  // ...and the reverse, which is how a lab rots: dials for tunables that
  // no longer exist look fine and silently do nothing.
  const stale = dialled.filter((k) => !keys.includes(k));
  assert(stale.length === 0, `the lab dials tunables that no longer exist: ${stale.join(', ')}`);

  // Every shrub silhouette the drawing knows must have a button, or it
  // cannot be chosen -- including whichever one bushStyleAlt names.
  const styles = [...(lab.match(/const STYLES = \[[^\]]*\]/) || [''])[0].matchAll(/'([^']+)'/g)]
    .map((m) => m[1]);
  for (const named of [api.MEADOW_DEFAULTS.bushStyle, api.MEADOW_DEFAULTS.bushStyleAlt]) {
    assert(styles.includes(named), `the lab has no button for the shipped style '${named}'`);
  }
});

check('the stem is a dial, not a decision baked into the drawing', () => {
  const t = api.MEADOW_DEFAULTS;
  // Owner-baked off the lab, re-baked 2026-08-12. The LOBED species is now
  // the small tree -- lifted, stemmed and thick-trunked -- and the flat
  // cover is the alt, which takes the larger share. Pinned rather than
  // left free, so an accidental edit is still caught; this line has moved
  // twice now, both times because the owner pasted a readout. Anyone
  // re-dialling should paste the lab's readout, not edit here.
  assert(t.bushStyle === 'lobed', `the shipped shrub moved: ${t.bushStyle}`);
  assert(t.bushStyleAlt === 'trunk', `the shipped tree moved: ${t.bushStyleAlt}`);
  // The INTENT first, so a re-dial that swaps which species is the tree
  // leaves this sentence true and only moves the numbers below it:
  // exactly one of the two stands up, and it is the minority.
  const stands = (lift, trunk) => lift > 0 || trunk > 0;
  const primaryStands = stands(t.bushLift, t.bushTrunk);
  const altStands = stands(t.bushLiftAlt, t.bushTrunkAlt);
  assert(
    primaryStands !== altStands,
    'both species stand, or neither does -- the meadow is one kind of cover drawn twice',
  );
  const treeShare = altStands ? t.bushStyleAltShare : 1 - t.bushStyleAltShare;
  assert(treeShare < 0.5, `the standing species is ${(treeShare * 100).toFixed(0)}% of cover -- that is a wood, not trees in a meadow`);

  // ...then the numbers, pinned per this file's convention for judged art.
  // Owner-baked off the lab, 2026-08-12: the TRUNK species is the small
  // tree, the lobed one lies flat, and the trees are 30% of cover.
  assert(t.bushLift === 0, `bushLift moved off the owner's 0: ${t.bushLift}`);
  assert(t.bushTrunk === 0, `bushTrunk moved off the owner's 0: ${t.bushTrunk}`);
  assert(t.bushLiftAlt === 1.55, `bushLiftAlt moved: ${t.bushLiftAlt}`);
  assert(t.bushTrunkAlt === 1, `bushTrunkAlt moved: ${t.bushTrunkAlt}`);
  assert(t.bushTrunkWidthAlt === 1.4, `bushTrunkWidthAlt moved: ${t.bushTrunkWidthAlt}`);
  // The alt must be a DIFFERENT silhouette, or bushStyleAltShare has
  // nothing to mix and the dial is quietly inert.
  assert(
    t.bushStyleAlt && t.bushStyleAlt !== t.bushStyle,
    'bushStyleAlt names the same style as bushStyle -- the mix dial does nothing',
  );
  // Both stemmed styles honour it, and both reach zero. The lobed shrub
  // arrived from the spec with a trunk written into it and no way to turn
  // it off, which is the same fault as a baked art constant: an owner
  // cannot judge what they cannot move.
  for (const style of ['trunk', 'lobed']) {
    const stems = (bushTrunk) => {
      const log = [];
      api.drawBushAt(guardCtx(log), {
        x: 3, y: 3, seed: 0.55, tile: 48,
        t: { ...t, bushStyle: style, bushStyleAltShare: 0, bushTrunk },
      });
      // lobed strokes its stem, trunk fills one; either way it is the only
      // lineTo/rect the style draws.
      return log.filter((o) => o[0] === 'lineTo' || o[0] === 'rect').length;
    };
    assert(stems(1) > 0, `${style} draws no stem at all`);
    assert(stems(0) === 0, `${style} still draws a stem at bushTrunk 0`);
  }
});

check('nothing turns black mid-crossfade', () => {
  // The bug this pins (owner, 2026-08-11): shrubs and flowers went BLACK
  // during a phase transition and healed themselves once the phase
  // settled. cat.js's shadeHex does `parseInt(hex.slice(1), 16)`, and
  // between any two phases the palette mixer emits `rgb(...)`, not hex --
  // so it parsed garbage and every channel came out 0.
  //
  // Settled phases were fine, which is why every check here missed it:
  // they all drew at blend 0. This one drives the crossfades.
  //
  // Black is never an authored meadow colour, so "did anything paint pure
  // black" is a sound proxy for "did a colour helper fail to parse".
  const BLACK = /^(#000000|#000|rgba?\(\s*0\s*,\s*0\s*,\s*0\b)/i;
  const t = api.MEADOW_DEFAULTS;
  // Tile 48, so the FINE detail runs: below 44 the flowers take the
  // single-dot path and their shaded petals never draw. And BOTH shrub
  // styles through drawGroundCover, which takes its tunables explicitly --
  // only the shipped style draws at the shipped dials, and a stem only
  // draws when bushTrunk is up.
  const passes = [
    ['ground + flowers', (g) => api.drawMeadowGround(g, { width: 14, height: 14, tile: 48, cover: false })],
    ...['lobed', 'trunk'].map((style) => [`shrub:${style}`, (g) =>
      api.drawGroundCover(g, {
        width: 14, height: 14, tile: 48,
        t: { ...t, bushStyle: style, bushStyleAltShare: 0, bushTrunk: 1, bushLift: 1 },
      })]),
  ];
  const phases = ['day', 'dusk', 'night', 'dawn'];
  for (let i = 0; i < phases.length; i++) {
    const from = phases[i];
    const to = phases[(i + 1) % phases.length];
    for (const blend of [0, 0.15, 0.4, 0.6, 0.85, 1]) {
      api.setMeadowPalette(from, blend > 0 ? to : null, blend);
      for (const [what, paint] of passes) {
        const log = [];
        paint(guardCtx(log));
        const where = `${from}->${to} @${blend} ${what}`;
        const black = log.filter(
          (o) => o[0] === 'set' && (o[1] === 'fillStyle' || o[1] === 'strokeStyle')
            && BLACK.test(String(o[2])),
        );
        assert(black.length === 0, `${where}: ${black.length} draw(s) went black (${black[0] && black[0][2]})`);
        // Gradient stops go through the same helpers and never touch fillStyle.
        const stops = log.filter((o) => o[0] === 'addColorStop' && BLACK.test(String(o[2])));
        assert(stops.length === 0, `${where}: a gradient stop went black (${stops[0] && stops[0][2]})`);
      }
    }
  }
  api.setMeadowPalette('day', null, 0);
});

check('meadow.js never assumes a palette entry is hex', () => {
  // The rule the bug broke, stated where it can be enforced. Between any
  // two phases every palette entry is an `rgb(...)` string, so a helper
  // that slices a '#' off the front is guaranteed to be wrong there -- and
  // wrong SILENTLY, since it hands back a perfectly valid colour.
  const src = readFileSync(join(here, 'meadow.js'), 'utf8')
    .replace(/\/\*[\s\S]*?\*\//g, ' ')
    .replace(/^\s*\/\/.*$/gm, ' ');
  assert(!/\bshadeHex\s*\(/.test(src), 'meadow.js calls shadeHex, which only parses hex -- use shadePalette');
  assert(!/\blightenHex\s*\(/.test(src), 'meadow.js calls lightenHex, which only parses hex -- mix through mixPaletteColor');
});

// The summary stays LAST. It sat mid-file once and every check appended
// after it ran past `process.exit` and was silently never counted -- the
// suite reported green on tests that had not run. (Cost the motion suite
// a round of this too.)
// ---- critters join the depth sort (2026-08-11) ----
//
// Owner: bugs were drawn behind bushes, and should pass in front of one
// the way a kitty does -- dropping behind it again when they move north.
// In one square the order is kitty > bug > bush.

/** The layer as render.js builds it, ordered. */
const ordered = (items) => api.spriteOrder(items).map((i) => i.kind);
const coverAt = (y) => ({ kind: 'cover', y: api.coverSortKey({ y }, api.MEADOW_DEFAULTS) });
const critterAt = (y) => ({ kind: 'critter', y: api.catSortKey({ x: 0, y }) });
const kittyAt = (y) => ({ kind: 'kitty', y: api.catSortKey({ x: 0, y }) });

check('a bug passes in front of a bush, and behind it once it moves north', () => {
  const bush = coverAt(5);
  // Same square: the bug is in front. A butterfly hovering over the same
  // patch of earth a shrub is rooted in is nearer the viewer, because the
  // shrub's contact point is higher up the tile than the cat ground line.
  assert(
    String(ordered([critterAt(5), bush])) === 'cover,critter',
    `same tile: got ${ordered([critterAt(5), bush])}`,
  );
  // One square north (smaller y): behind it, exactly as a kitty would be.
  assert(
    String(ordered([critterAt(4), bush])) === 'critter,cover',
    `a tile north: got ${ordered([critterAt(4), bush])}`,
  );
  // One square south: still in front.
  assert(
    String(ordered([critterAt(6), bush])) === 'cover,critter',
    `a tile south: got ${ordered([critterAt(6), bush])}`,
  );
  // And the ordering is the same one a KITTY gets, which is the whole ask
  // -- a bug should not need its own depth rules.
  for (const y of [4, 5, 6]) {
    assert(
      String(ordered([critterAt(y), bush])) === String(ordered([kittyAt(y), bush]).map((k) => (k === 'kitty' ? 'critter' : k))),
      `a bug at y=${y} sorts differently from a kitty there`,
    );
  }
});

check('all three in one square go kitty, bug, bush -- front to back', () => {
  // Drawn back to front, so the array reads cover, critter, kitty.
  const got = ordered([kittyAt(5), critterAt(5), coverAt(5)]);
  assert(String(got) === 'cover,critter,kitty', `got ${got}`);
  // ...whatever order they were pushed in. Before this the tie fell to
  // insertion order, which is an ordering decided by accident.
  const shuffled = ordered([coverAt(5), kittyAt(5), critterAt(5)]);
  assert(String(shuffled) === 'cover,critter,kitty', `push order changed the result: ${shuffled}`);
  assert(
    api.SPRITE_RANK.cover < api.SPRITE_RANK.critter && api.SPRITE_RANK.critter < api.SPRITE_RANK.kitty,
    'the rank table itself must read cover < critter < kitty',
  );
});

check('a bowl is in front of the cover it shares a tile with', () => {
  // Owner, 2026-08-12. Cover stopped being kept off served elements when
  // `occupiedTiles` narrowed to water, so a shrub rooted in a bowl's tile
  // was painting straight over it.
  const propAt = (y) => ({ kind: 'prop', y: api.catSortKey({ x: 0, y }) });
  assert(
    String(ordered([propAt(5), coverAt(5)])) === 'cover,prop',
    `same tile: got ${ordered([propAt(5), coverAt(5)])}`,
  );
  // ...and it still sorts by the ground everywhere else: cover a tile
  // south of a bowl is nearer the viewer and stays in front of it.
  assert(
    String(ordered([propAt(5), coverAt(6)])) === 'prop,cover',
    'cover a tile south of a bowl must be drawn in front of it',
  );
  // The owner's ordering, front to back: cat > butterfly > bowl > shrub
  // (2026-08-12). A cat walks up to a bowl so it is in front of it, and a
  // butterfly is in the air over both. Drawn back to front, so the array
  // reads in reverse.
  const all = ordered([kittyAt(5), critterAt(5), propAt(5), coverAt(5)]);
  const frontToBack = [...all].reverse().join(' > ');
  assert(
    frontToBack === 'kitty > critter > prop > cover',
    `front to back is "${frontToBack}", want "kitty > critter > prop > cover" ` +
      '(cat > butterfly > bowl > shrub)',
  );
  assert(
    api.SPRITE_RANK.cover < api.SPRITE_RANK.prop && api.SPRITE_RANK.prop < api.SPRITE_RANK.kitty,
    'the rank table must read cover < prop < kitty',
  );
});

check('a bug a whole tile away still sorts by the ground, not by rank', () => {
  // Rank is only ever a TIE-break. A kitty one tile north of a bug must
  // still be behind it, or the rank has started deciding depth.
  assert(
    String(ordered([kittyAt(4), critterAt(5)])) === 'kitty,critter',
    'a kitty a tile north of a bug must be drawn behind it',
  );
  assert(
    String(ordered([coverAt(6), kittyAt(5)])) === 'kitty,cover',
    'cover a tile south of a kitty must be drawn in front of it',
  );
});

check('the renderer sorts critters instead of stamping them down', () => {
  // The pure ordering above is worth nothing if render.js still paints
  // butterflies in the flat element pass, where every shrub covers them.
  const src = readFileSync(join(here, 'render.js'), 'utf8');
  assert(/const CRITTER_KINDS = new Set\(\['bug', 'greeble'\]\)/.test(src), 'CRITTER_KINDS is gone or renamed');
  const pass = src.slice(src.indexOf("for (const el of world.elements) {\n      if (el.kind === 'sunbeam') continue;"));
  const flat = pass.slice(0, pass.indexOf('// Cats and ground cover'));
  assert(
    /CRITTER_KINDS\.has\(el\.kind\)[^\n]*continue;/.test(flat),
    'the flat element pass still draws critters -- they would sit behind every shrub',
  );
  assert(
    /PROP_KINDS\.has\(el\.kind\)[^\n]*continue;/.test(flat),
    'the flat element pass still draws bowls -- a shrub sharing the tile paints over them',
  );
  // Sorted on the DRAWN position: a gliding critter that sorted by its
  // served tile would change depth a tick off from when it visibly crosses.
  assert(
    /y: catSortKey\(view\.elementPosFor\(el\)\)/.test(src),
    'critters must sort on their drawn position, not their served tile',
  );
  // A bowl stands where a cat stands, so it takes the cat's ground line.
  // Keying it to the cover's would move every bowl-vs-cat crossover by
  // 0.16 of a tile, which no integer-tile check can see.
  const propPush = src.slice(src.indexOf("kind: 'prop',"));
  assert(
    /^\s*kind: 'prop',\s*\n\s*y: catSortKey\(el\.pos\),/.test(propPush),
    'a bowl must sort on the cat ground line and its served tile',
  );
  assert(/for \(const item of spriteOrder\(layer\)\) item\.draw\(\)/.test(src), 'the layer is not going through spriteOrder');

  // An expiring critter is still a critter: left in the fade pass it would
  // pop behind the shrub it was in front of a moment ago. Asserted on the
  // STRUCTURE of the two regions, not on a comment -- a comment travels
  // with a bad edit and proves nothing about what runs.
  const layerStart = src.indexOf('// Cats and ground cover');
  const fade = src.slice(0, layerStart);
  const layerRegion = src.slice(layerStart, src.indexOf('for (const item of spriteOrder(layer))'));
  const expiredFade = fade.slice(fade.indexOf('view.expired.length'));
  assert(
    /!CRITTER_KINDS\.has\(el\.kind\)/.test(expiredFade),
    'the expiry fade pass still draws critters -- they would pop behind cover while fading',
  );
  assert(
    /view\.expired/.test(layerRegion) && /kind: 'critter'/.test(layerRegion),
    'expired critters never reach the depth layer, so nothing draws them at all',
  );
});

check('a whole frame really draws its critters, live and expiring', () => {
  // The source checks above see that the code is THERE. They cannot see
  // whether it runs: an unreachable push reads exactly like a live one.
  // So this draws real frames and counts. No kitties in the world, which
  // keeps the cat vocabulary out of it -- the question is only whether a
  // butterfly reaches the canvas.
  const frame = ({ live = [], expired = [] }) => {
    const canvas = mockCanvas(640, 640);
    const log = [];
    const ctx = guardCtx(log);
    ctx.canvas = canvas;
    canvas.getContext = () => ctx;
    const renderer = new api.WorldRenderer(canvas);
    renderer.tile = 32;
    renderer.dpr = 1;
    renderer.cssWidth = 640;
    renderer.cssHeight = 640;
    renderer.theme = 'day';
    const world = { tick: 5, width: 20, height: 20, kitties: [], elements: live };
    const view = {
      now: 0,
      still: false,
      progress: 0.5,
      expired,
      expiredAlpha: expired.length ? 0.7 : 0,
      elementAlphaFor: () => 1,
      elementPosFor: (el) => el.pos,
      propPhaseFor: () => 0.25,
      ambient: { now: 0 },
    };
    renderer.draw(world, view);
    return log.length;
  };

  const bug = { id: 7, kind: 'bug', pos: { x: 6, y: 6 } };
  const bare = frame({});
  const withBug = frame({ live: [bug] });
  assert(withBug > bare, `a live bug drew nothing: ${bare} ops bare, ${withBug} with it`);

  const bowl = { id: 9, kind: 'chow', pos: { x: 9, y: 9 }, servings: 2 };
  const withBowl = frame({ live: [bowl] });
  assert(withBowl > bare, `a live bowl drew nothing: ${bare} vs ${withBowl}`);
  const bowlGoing = frame({ expired: [bowl] });
  assert(
    bowlGoing > bare,
    `an EXPIRING bowl drew nothing (${bare} vs ${bowlGoing}) -- it vanishes instead of fading`,
  );

  const withExpiring = frame({ expired: [bug] });
  assert(
    withExpiring > bare,
    `an EXPIRING bug drew nothing (${bare} vs ${withExpiring}) -- it vanishes instead of fading, ` +
      'which is what happens when its push into the depth layer is unreachable',
  );
});

// ---- two species, two stances (2026-08-11) ----
//
// Owner wants small trees among flat cover: one ground cover with lift and
// a trunk, one without. Style already differed per species; how far it
// STOOD UP did not, so both were flat or both were lifted.

/** Every op drawing one clump, at a tile the alt species owns. */
function clumpOps(t, { x, y }) {
  const log = [];
  api.drawBushAt(guardCtx(log), { x, y, seed: 0.55, tile: 32, t });
  return log;
}
/** A tile the species pick lands on, so the overlay is actually exercised. */
function tileOfSpecies(t, wantAlt) {
  for (let y = 0; y < 40; y += 1) {
    for (let x = 0; x < 40; x += 1) {
      const isAlt = api.tileHash(x, y, api.MEADOW_SALTS.bushKind) < t.bushStyleAltShare;
      if (isAlt === wantAlt) return { x, y };
    }
  }
  throw new Error(`no tile found for ${wantAlt ? 'alt' : 'primary'}`);
}

check('the second species carries its own lift and trunk', () => {
  // A mixed meadow, both species present.
  const base = { ...api.MEADOW_DEFAULTS, bushStyleAltShare: 0.5, bushStyle: 'lobed', bushStyleAlt: 'trunk' };
  const altTile = tileOfSpecies(base, true);
  const ownTile = tileOfSpecies(base, false);

  // Standing the ALT species up must change the alt tile's drawing...
  const tree = { ...base, bushLiftAlt: 1.2, bushTrunkAlt: 0.8 };
  assert(
    String(clumpOps(base, altTile)) !== String(clumpOps(tree, altTile)),
    'raising bushLiftAlt/bushTrunkAlt changed nothing on a tile the alt species owns',
  );
  // ...and must leave the primary species exactly where it was. This is
  // the whole point: one stands, the other lies on the ground.
  assert(
    String(clumpOps(base, ownTile)) === String(clumpOps(tree, ownTile)),
    'the alt stance leaked onto the primary species -- both would stand or both would lie',
  );
  // And the reverse, so neither dial is quietly driving both.
  const shrub = { ...base, bushLift: 1.2, bushTrunk: 0.8 };
  assert(
    String(clumpOps(base, ownTile)) !== String(clumpOps(shrub, ownTile)),
    'guard: bushLift should still move the primary species',
  );
  assert(
    String(clumpOps(base, altTile)) === String(clumpOps(shrub, altTile)),
    'the primary stance leaked onto the alt species',
  );
});

check('trunk width scales the width each style was authored with', () => {
  // Both styles draw a stem at different authored widths (the trunk style
  // at 0.2 canopy radii, the lobed one at 0.13). One absolute dial would
  // have had to pick a winner and restyle the other, so this one is a
  // MULTIPLIER on each.
  //
  // Asserted against the authored constant rather than against whatever
  // ships. The first version compared a width of 1 to the shipped default,
  // which held only while that default WAS 1 -- the owner baked 2.55 on
  // 2026-08-12 and it failed for a reason unrelated to the mechanism.
  for (const style of ['trunk', 'lobed']) {
    const base = { ...api.MEADOW_DEFAULTS, bushStyle: style, bushStyleAltShare: 0, bushTrunk: 0.8 };
    const at = { x: 3, y: 4 };
    assert(
      String(clumpOps({ ...base, bushTrunkWidth: 3 }, at)) !== String(clumpOps(base, at)),
      `${style}: the width dial does nothing -- this style's stem ignores it`,
    );
  }
  // The trunk style fills a rect, so its width is readable directly.
  const widthAt = (w) => {
    const t = { ...api.MEADOW_DEFAULTS, bushStyle: 'trunk', bushStyleAltShare: 0,
      bushTrunk: 0.8, bushTrunkWidth: w };
    const rects = clumpOps(t, { x: 3, y: 4 }).filter((o) => o[0] === 'rect');
    assert(rects.length, 'the trunk style drew no rect at all');
    return rects[0][3];
  };
  // Derived from the DIALS, not from a copy of the formula: this line
  // restated 0.26 + s*0.18 and broke the moment those became
  // bushSizeMin/bushSizeSpread, on a change that had nothing to do with
  // trunks.
  const d = api.MEADOW_DEFAULTS;
  const r = (d.bushSizeMin + 0.55 * d.bushSizeSpread) * 32; // clumpOps' seed and tile
  assert(
    Math.abs(widthAt(1) - r * 0.2) < 1e-9,
    `at 1 the trunk should be its authored 0.2 radii (${(r * 0.2).toFixed(3)}), got ${widthAt(1).toFixed(3)}`,
  );
  assert(
    Math.abs(widthAt(2) - 2 * widthAt(1)) < 1e-9,
    'the multiplier must be linear, or it is not a multiplier',
  );

  // ...and it thickens about its own CENTRE. Growing to one side only is
  // invisible at width 1, where the two forms compute the same number, and
  // reads as a trunk sliding out from under its canopy once dialled up.
  const trunkRect = (width) => {
    const t = { ...api.MEADOW_DEFAULTS, bushStyle: 'trunk', bushStyleAltShare: 0,
      bushTrunk: 0.8, bushTrunkWidth: width };
    const rects = clumpOps(t, { x: 3, y: 4 }).filter((o) => o[0] === 'rect');
    assert(rects.length, 'the trunk style drew no rect at all');
    const [, x, , w] = rects[0];
    return { centre: x + w / 2, w };
  };
  const thin = trunkRect(1);
  const fat = trunkRect(3);
  assert(fat.w > thin.w * 2.5, `the trunk barely thickened: ${thin.w} -> ${fat.w}`);
  assert(
    Math.abs(fat.centre - thin.centre) < 1e-9,
    `the trunk's centre moved as it thickened (${thin.centre} -> ${fat.centre}) -- ` +
      'it is growing to one side, out from under its own canopy',
  );
});

check('the two species carry their own trunk width too', () => {
  const base = { ...api.MEADOW_DEFAULTS, bushStyleAltShare: 0.5, bushStyle: 'lobed', bushStyleAlt: 'trunk', bushTrunk: 0.8, bushTrunkAlt: 0.8 };
  const altTile = tileOfSpecies(base, true);
  const ownTile = tileOfSpecies(base, false);
  const thick = { ...base, bushTrunkWidthAlt: 3 };
  assert(
    String(clumpOps(base, altTile)) !== String(clumpOps(thick, altTile)),
    'bushTrunkWidthAlt does not reach the alt species',
  );
  assert(
    String(clumpOps(base, ownTile)) === String(clumpOps(thick, ownTile)),
    'the alt trunk width leaked onto the primary species -- both trunks would thicken together',
  );
});

check('the two species ship with different stances, or the mix is pointless', () => {
  // This used to assert the Alt dials arrived EQUAL to the primary's,
  // proving that adding them left the meadow untouched. That guard is
  // spent: the owner dialled them on 2026-08-12, making the primary a
  // small tree and leaving the alt flat.
  //
  // What replaces it is the property the mix exists for. Two species that
  // stand the same way are one species drawn twice, and every dial that
  // separates them is then dead weight nobody would notice.
  const d = api.MEADOW_DEFAULTS;
  const differs =
    d.bushLiftAlt !== d.bushLift ||
    d.bushTrunkAlt !== d.bushTrunk ||
    d.bushTrunkWidthAlt !== d.bushTrunkWidth;
  assert(differs, 'both species now stand identically -- the per-species stance is inert');
  assert(
    d.bushStyleAltShare > 0 && d.bushStyleAltShare < 1,
    `a share of ${d.bushStyleAltShare} grows only one species, so the stance dials cannot show`,
  );
});

check('a standing species does not move where it meets the ground', () => {
  // `coverSortKey` is what interleaves cover with the cats, and it is keyed
  // to the BASE. A tree that sorted by its canopy would slide in front of
  // cats it is standing behind, which is the bug the sort exists to fix.
  const flat = { ...api.MEADOW_DEFAULTS, bushLiftAlt: 0, bushTrunkAlt: 0 };
  const tall = { ...api.MEADOW_DEFAULTS, bushLiftAlt: 1.6, bushTrunkAlt: 1 };
  assert(
    api.coverSortKey({ x: 4, y: 9 }, flat) === api.coverSortKey({ x: 4, y: 9 }, tall),
    'lifting a species changed its ground contact -- it would sort against cats by its canopy',
  );
});

check('the occlusion strip draws each species in its own stance', () => {
  // The strip forces one style at a time as the PRIMARY, so it has to
  // bring the alt stance with it or it shows a tree lying flat -- and the
  // strip is the only surface for judging whether a lifted canopy reads at
  // the live tile.
  const lab = readFileSync(join(here, 'gallery-meadow.html'), 'utf8');
  const strip = lab.slice(lab.indexOf('BOTH species, a row each'), lab.indexOf('OCC_OFFSETS.forEach'));
  for (const dial of ['bushLiftAlt', 'bushTrunkAlt', 'bushTrunkWidthAlt']) {
    assert(strip.includes(dial), `the occlusion strip draws both rows without ${dial}`);
  }
});

// ---- where cover stands (2026-08-13) ----

check('the top row grows the species that lies down', () => {
  // Owner: a tree hung off the top of the map. A standing canopy reaches
  // about 0.38 tiles above its own tile, and row 0 has no headroom, so the
  // edge of the world cut it off.
  const t = api.MEADOW_DEFAULTS;
  // Named args, not a default parameter: `some`/`every` pass (item, index,
  // array), so a default second argument silently receives the INDEX.
  const stands = (b, tt) => api.coverStands(tt || t, b.alt);
  const all = api.bushesFor(20, 20, t, null);
  assert(all.some((b) => stands(b)), 'guard: no standing cover at all, so this proves nothing');
  const row0 = all.filter((b) => b.y === 0);
  assert(row0.length > 0, 'guard: nothing grew in row 0, so the rule is untested');
  assert(row0.every((b) => !stands(b)), 'a standing clump is still growing in the top row');
  // Cover still GROWS there -- the fix is a different species, not a bald
  // stripe along the top.
  assert(row0.length === api.bushesFor(20, 20, { ...t, bushStyleAltShare: 0 }, null)
    .filter((b) => b.y === 0).length, 'the top row lost clumps instead of swapping species');

  // Keyed on which species STANDS, not on "the alt" -- which of the two is
  // the tree has already flipped once, and would take this rule with it.
  const flipped = { ...t, bushLift: t.bushLiftAlt, bushTrunk: t.bushTrunkAlt,
    bushLiftAlt: t.bushLift, bushTrunkAlt: t.bushTrunk };
  const flippedRow0 = api.bushesFor(20, 20, flipped, null).filter((b) => b.y === 0);
  assert(
    flippedRow0.every((b) => !stands(b, flipped)),
    'with the stances swapped the top row grows a tree again -- the rule is keyed on the wrong thing',
  );

  // Both standing leaves nothing better to offer, so the roll stands
  // rather than the world losing its top row of cover.
  const bothStand = { ...t, bushLift: 1, bushTrunk: 1, bushLiftAlt: 1, bushTrunkAlt: 1 };
  assert(
    api.bushesFor(20, 20, bothStand, null).filter((b) => b.y === 0).length === row0.length,
    'when both species stand the top row should keep its cover, not drop it',
  );
});

check('a clump stands slightly off the grid, and never off the map', () => {
  const t = api.MEADOW_DEFAULTS;
  const all = api.bushesFor(20, 20, t, null);
  assert(all.length > 8, 'guard: too few clumps to say anything');

  // It actually moves them, and within the dial.
  assert(all.every((b) => Math.abs(b.ox) <= t.bushJitterX + 1e-9),
    `a clump wandered past the dial (${t.bushJitterX})`);
  assert(all.some((b) => Math.abs(b.ox) > t.bushJitterX * 0.4),
    'every clump landed near the middle of its tile -- the nudge is not doing anything');
  assert(all.every((b) => b.ox !== 0), 'a clump is still dead on the grid');

  // Stable for the life of the world: scenery that moves between frames is
  // the flicker `occupiedTiles` was narrowed to prevent.
  assert(
    JSON.stringify(api.bushesFor(20, 20, t, null)) === JSON.stringify(all),
    'a clump moved between calls',
  );

  // Clamped at the side edges, or a sideways nudge just reintroduces the
  // owner's complaint one border over. Asserted on the CANOPY, not on the
  // centre: a clump is wider than its tile (the lobes reach ~1.14 radii,
  // and the widest is 0.57 tiles against a half-tile of 0.5), so holding
  // the centre inside the outermost tile centres still let the biggest
  // ones hang off the edge.
  const WIDE_JITTER = 0.4; // named, so the assertions below cannot read the
  // SHIPPED jitter while measuring a world built with a different one.
  const wide = api.bushesFor(20, 20, { ...t, bushChance: 0.9, bushJitterX: WIDE_JITTER }, null);
  const reach = (b) => 1.14 * (t.bushSizeMin + b.seed * t.bushSizeSpread);
  assert(wide.some((b) => b.x === 0) && wide.some((b) => b.x === 19), 'guard: no edge clumps to check');
  const off = wide.filter(
    (b) => (b.x + 0.5 + b.ox) - reach(b) < -1e-9 || (b.x + 0.5 + b.ox) + reach(b) > 20 + 1e-9,
  );
  assert(off.length === 0, `${off.length} clumps have a canopy hanging off the map`);
  // ...and the clamp only ever pushes INWARD, never past the far side.
  assert(wide.every((b) => Math.abs(b.ox) <= Math.max(WIDE_JITTER, reach(b)) + 1e-9),
    'the clamp shoved a clump further than it could possibly need');

  // And 0 is exactly the grid that shipped before this existed.
  assert(
    api.bushesFor(20, 20, { ...t, bushJitterX: 0 }, null).every((b) => b.ox === 0),
    'the dial does not switch off',
  );

  // Its OWN hash channel. Sharing `bushShape` would tie where a clump
  // stands to how it is shaped, so every clump of a given shape would sit
  // at the same offset -- a correlation nobody asked for and which the
  // bounds and determinism checks above cannot see.
  // Asserted on the OUTPUT, not by comparing the two salt constants: the
  // salts differing proves nothing about which one `bushesFor` reached
  // for. If it drew the offset from the shape channel, `ox` would be a
  // plain function of `seed` for every clump.
  const fromShape = all.filter(
    (b) => Math.abs(b.ox - (b.seed - 0.5) * 2 * t.bushJitterX) < 1e-9,
  ).length;
  assert(
    fromShape < all.length / 2,
    `${fromShape} of ${all.length} clumps have an offset derived from their SHAPE seed -- ` +
      'place and shape are sharing a hash channel',
  );

  // ...and the drawing actually MOVES. bushesFor deciding an offset that
  // drawBushAt then ignores would pass every check above it.
  const opsAt = (ox) => {
    const log = [];
    api.drawBushAt(guardCtx(log), { x: 3, y: 4, ox, alt: false, seed: 0.55, tile: 32, t });
    return log;
  };
  const home = opsAt(0);
  const moved = opsAt(0.25);
  assert(String(home) !== String(moved), 'drawBushAt ignores the offset it is handed');
  // Moved by exactly the offset, in x only: every x coordinate shifts by
  // 0.25 tiles and nothing vertical changes.
  const xs = (log) => log.filter((o) => o[0] === 'ellipse' || o[0] === 'arc').map((o) => o[1]);
  const ys = (log) => log.filter((o) => o[0] === 'ellipse' || o[0] === 'arc').map((o) => o[2]);
  assert(xs(home).length, 'guard: the clump drew no arcs to measure');
  assert(
    xs(home).every((v, i) => Math.abs(xs(moved)[i] - v - 0.25 * 32) < 1e-6),
    'the offset moved the drawing by something other than itself',
  );
  assert(String(ys(home)) === String(ys(moved)), 'a HORIZONTAL nudge moved the clump vertically');
});

check('two of a kind in one row never read as the same clump twice', () => {
  // Owner, 2026-08-13. Measured before the fix: two bushes in row 3 whose
  // radii differed by 0.2px, and widening the size range did not help --
  // two tiles that hash to nearly the same seed stay nearly the same at
  // any spread. So the second one's seed takes a half turn.
  const t = api.MEADOW_DEFAULTS;
  const radius = (b) => t.bushSizeMin + b.seed * t.bushSizeSpread;
  const rows = (tt) => {
    const byRow = {};
    for (const b of api.bushesFor(20, 20, tt, null)) (byRow[b.y] ||= []).push(b);
    return Object.values(byRow).map((r) => r.sort((a, c) => a.x - c.x));
  };

  // The invariant, over a crowded world so there is plenty to check.
  const crowded = { ...t, bushChance: 0.5 };
  let pairs = 0;
  for (const row of rows(crowded)) {
    for (let i = 1; i < row.length; i++) {
      if (row[i].alt !== row[i - 1].alt) continue;
      pairs++;
      const apart = Math.abs(radius(row[i]) - radius(row[i - 1]));
      assert(
        apart >= t.bushSizeMinDiff - 1e-9,
        `two ${row[i].alt ? 'trees' : 'bushes'} in row ${row[i].y} differ by ${apart.toFixed(4)} ` +
          `tiles, under the ${t.bushSizeMinDiff} they must clear`,
      );
    }
  }
  assert(pairs > 12, `only ${pairs} same-kind neighbours to check -- the world is too sparse`);

  // A tree beside a bush of its own size reads fine, and the owner said
  // so, so the rule must not fire across kinds. Checked by finding a mixed
  // pair that is closer than the threshold and confirming it was left be.
  const mixed = rows(crowded).flatMap((row) =>
    row.slice(1).map((b, i) => [row[i], b]).filter(([a, c]) => a.alt !== c.alt),
  );
  assert(mixed.length, 'guard: no mixed neighbours in this world');
  assert(
    mixed.some(([a, c]) => Math.abs(radius(a) - radius(c)) < t.bushSizeMinDiff),
    'no mixed pair is close in size, so nothing here proves the rule spares them',
  );

  // Off is exactly the placement that existed before the repel.
  const off = api.bushesFor(20, 20, { ...t, bushSizeMinDiff: 0 }, null);
  assert(off.some((b, i) => b.seed !== api.bushesFor(20, 20, t, null)[i].seed),
    'the repel changes nothing at all -- it is not running');
  // ...and it is stable, like everything else the scenery decides.
  assert(
    JSON.stringify(api.bushesFor(20, 20, t, null)) === JSON.stringify(api.bushesFor(20, 20, t, null)),
    'a clump changed size between calls',
  );
});

check('the sideways nudge cannot disagree with the depth sort', () => {
  // The reason this is horizontal ONLY (owner's call, 2026-08-13):
  // `coverSortKey` is keyed to y, so sliding a clump sideways cannot move
  // its ground contact. A vertical nudge would have to move the sort key
  // in the same edit, and getting that wrong puts a cat in front of a
  // shrub it is standing behind.
  const t = api.MEADOW_DEFAULTS;
  const at = { x: 5, y: 7 };
  const keys = [-0.4, -0.15, 0, 0.15, 0.4].map((ox) => api.coverSortKey({ ...at, ox }, t));
  assert(new Set(keys).size === 1, `the nudge moved the sort key: ${keys.join(', ')}`);
  // ...and a clump one tile south still sorts in front, whatever the nudge.
  assert(
    api.coverSortKey({ x: 5, y: 8, ox: -0.4 }, t) > api.coverSortKey({ x: 5, y: 7, ox: 0.4 }, t),
    'depth stopped following the row',
  );
});

check('the pond layers rebuild when the palette steps, not only when the water moves', () => {
  // `buildPondLayers` bakes MEADOW.pondShore and MEADOW.pondLip INTO the
  // shore and lip canvases, but the cache used to key on the water tiles
  // alone -- and `applyTheme` nulls only the ground cache. So a world
  // running from day into night kept its shore band and damp lip in
  // daylight paint while the grass, the pond body and the meniscus all
  // crossed. Reported by review, 2026-08-17; shipped that way since the
  // layers were introduced.
  const renderer = new api.WorldRenderer(mockCanvas(640, 640));
  renderer.tile = 32;
  renderer.cssWidth = 640;
  renderer.cssHeight = 640;
  renderer.dpr = 1;
  const world = {
    width: 20,
    height: 20,
    elements: [
      { kind: 'water', id: 1, pos: { x: 5, y: 5 } },
      { kind: 'water', id: 2, pos: { x: 6, y: 5 } },
    ],
  };
  const view = { elementAlphaFor: () => 1, ambient: { now: 0 } };

  renderer.paletteKey = 'day>dusk@0';
  renderer.drawPondLayer(world, view);
  const first = renderer.pondCache;
  assert(first, 'no pond cache was built at all');

  // Nothing moved: the cache is the whole point, so it must survive.
  renderer.drawPondLayer(world, view);
  assert(renderer.pondCache === first, 'the cache rebuilt with nothing changed');

  // The palette steps. `applyTheme` publishes the key it already computes
  // for its own early-return, and the layers key on it.
  renderer.paletteKey = 'day>dusk@0.5';
  renderer.drawPondLayer(world, view);
  assert(renderer.pondCache !== first, 'the pond layers survived a palette step');
});

check('applyTheme publishes the palette key the pond layers key on', () => {
  // Two halves in two files, and the failure mode if they drift is silent
  // -- the layers simply never rebuild. Worth pinning the join.
  const app = readFileSync(join(here, 'app.js'), 'utf8');
  assert(/renderer\.paletteKey = key;/.test(app), 'applyTheme no longer publishes the palette key');
  const render = readFileSync(join(here, 'render.js'), 'utf8');
  assert(
    /const signature = `\$\{this\.paletteKey\}\|/.test(render),
    'the pond signature no longer carries the palette key',
  );
});

/* ---- spec 036: what camera movement must NOT cost (SC-003, SC-012) ---- */

const camRenderer = () => {
  const r = new api.WorldRenderer(mockCanvas(620, 620));
  r.cssWidth = 620;
  r.cssHeight = 620;
  r.dpr = 1;
  r.camera = new api.Camera();
  return r;
};
const camWorldFor = (kitties = 5) => ({
  width: 20,
  height: 20,
  tick: 0,
  kitties: Array.from({ length: kitties }, (_, i) => ({ id: i + 1, pos: { x: 4 + i * 3, y: 10 } })),
  elements: [
    { kind: 'water', id: 90, pos: { x: 6, y: 6 } },
    { kind: 'water', id: 91, pos: { x: 7, y: 6 } },
    { kind: 'water', id: 92, pos: { x: 6, y: 7 } },
  ],
});
/** Sweep the camera across its whole band and back, panning as it goes. */
const sweep = (r, world, each) => {
  const D = api.VIEW.camera;
  for (let i = 0; i <= 120; i += 1) {
    const t = i / 120;
    r.camera.across = D.nominalAcross + (D.nominalAcross * D.ceilingFactor - D.nominalAcross) * Math.sin(t * Math.PI);
    r.camera.left = (20 - r.camera.across) * t;
    r.camera.top = (20 - r.camera.across) * (1 - t);
    r.tile = r.cssWidth / r.camera.across;
    each();
  }
};

check('camera movement never rebakes the ground', () => {
  // The quickstart says to instrument this BEFORE trusting a frame-rate
  // reading, because a bake count is diagnostic where fps is only a
  // symptom -- and render.js has already shipped a guard that mismatched
  // every frame and rebaked the whole ground at 60fps.
  const r = camRenderer();
  r.camera.on = true;
  const world = camWorldFor();
  let bakes = 0;
  let last = null;
  sweep(r, world, () => {
    r.blitGround(world);
    if (r.groundCache !== last) {
      bakes += 1;
      last = r.groundCache;
    }
  });
  assert(bakes === 1, `the ground rebaked ${bakes} times across a zoom sweep`);
});

check('camera movement never rebuilds the pond layers', () => {
  // Same claim for the water, which costs more: buildPondLayers blurs
  // four canvases where the ground bakes one.
  const r = camRenderer();
  r.camera.on = true;
  const world = camWorldFor();
  const view = { elementAlphaFor: () => 1, ambient: { now: 0 } };
  let builds = 0;
  let last = null;
  sweep(r, world, () => {
    r.drawPondLayer(world, view);
    if (r.pondCache !== last) {
      builds += 1;
      last = r.pondCache;
    }
  });
  assert(builds === 1, `the pond layers rebuilt ${builds} times across a zoom sweep`);
});

check('the ground the camera bakes is the WORLD, at every zoom', () => {
  // FR-024 / SC-012: decoration density is a property of the world, so
  // drawMeadowGround must keep receiving world dimensions no matter how
  // little of the world is on screen. Handing it the visible window
  // instead would thin the flowers out as the camera closed in.
  const seen = [];
  const realCreate = globalThis.document.createElement;
  globalThis.document.createElement = (tag) => {
    const el = realCreate(tag);
    if (tag === 'canvas') el.getContext = () => new Proxy({}, {
      get: (_t, k) => (k === 'createLinearGradient'
        ? () => ({ addColorStop() {} })
        : () => {}),
      set: () => true,
    });
    return el;
  };
  try {
    const r = camRenderer();
    r.camera.on = true;
    const world = camWorldFor();
    const realGround = globalThis.drawMeadowGround;
    void realGround;
    sweep(r, world, () => {
      r.groundCache = null; // force the bake so its arguments can be read
      r.blitGround(world);
      seen.push({ w: r.groundCache.width, h: r.groundCache.height, tile: Number(r.groundCache.dataset.bakeTile) });
    });
  } finally {
    globalThis.document.createElement = realCreate;
  }
  // Every bake covers the whole world: width = world.width * bakeTile.
  for (const s of seen) {
    assert(Math.abs(s.w - 20 * s.tile) < 1, `a bake covered ${s.w / s.tile} tiles, not 20`);
    assert(Math.abs(s.h - 20 * s.tile) < 1, `a bake covered ${s.h / s.tile} tiles vertically`);
  }
  // And the bake tile itself never moved, which is why nothing rebaked.
  const tiles = new Set(seen.map((s) => s.tile));
  assert(tiles.size === 1, `the bake tile took ${tiles.size} values across a zoom sweep`);
});

check('a thought bubble stays with its kitty when the camera has panned', () => {
  // Reported by the owner as "detached want bubbles appearing over empty
  // squares". The bubble clamped itself inside `canvas.clientWidth` --
  // the canvas BOX, in untranslated coordinates -- while its x came from
  // tileOrigin, which is world space that the camera now pans. Before a
  // camera existed the two were the same number, so the clamp read as
  // correct for years.
  const arcs = [];
  const ctx = new Proxy({}, {
    get: (_t, k) => {
      if (k === 'canvas') return { clientWidth: 620, clientHeight: 620 };
      if (k === 'measureText') return () => ({ width: 20 });
      if (k === 'arc') return (x, y) => { arcs.push({ x, y }); };
      if (k === 'createLinearGradient' || k === 'createRadialGradient')
        return () => ({ addColorStop() {} });
      return () => {};
    },
    set: () => true,
  });
  const r = new api.WorldRenderer({ getContext: () => ctx, clientWidth: 620, clientHeight: 620 });
  r.cssWidth = 620;
  r.cssHeight = 620;
  r.dpr = 1;
  r.camera = new api.Camera();
  r.camera.on = true;
  r.camera.across = 10;
  r.camera.left = 10; // panned to the world's right half
  r.camera.top = 0;
  r.tile = 62; // 620 / 10 across

  // A kitty at world x=15: comfortably inside the frame [10, 20).
  const kitty = { id: 1, pos: { x: 15, y: 4 }, needs: {} };
  const view = { posFor: (k) => k.pos };
  r.drawThought(kitty, 'eat', view);

  assert(arcs.length > 0, 'the bubble drew nothing');
  const bubble = arcs[0];
  const her = 15 * 62;
  // Inside the visible frame, in world pixels...
  assert(bubble.x >= 10 * 62 && bubble.x <= 20 * 62,
    `the bubble landed at ${bubble.x}, outside the visible frame ${10 * 62}..${20 * 62}`);
  // ...and beside HER, not dragged to the canvas box's edge at 620.
  assert(Math.abs(bubble.x - her) < 2 * 62,
    `the bubble sat ${Math.abs(bubble.x - her).toFixed(0)}px from its kitty at ${her}`);
});

check("the meadow lab's VIEW stand-in matches the VIEW that ships", () => {
  // gallery-meadow.html cannot load anim.js -- anim.js declares `const
  // VIEW` and the lab needs a MUTABLE one for its dials -- so it
  // hand-writes a stand-in. A hand-written fixture drifts, and this one
  // drifts SILENTLY: a missing field makes `surfaceForPose` return
  // undefined, `waterlineFor` return NaN, and the clip swallow the whole
  // cat. That reads as broken art, not as a broken lab.
  const lab = readFileSync(join(here, 'gallery-meadow.html'), 'utf8');
  const render = readFileSync(join(here, 'render.js'), 'utf8');
  const animSrc = readFileSync(join(here, 'anim.js'), 'utf8');

  // Every VIEW field render.js reads, except `meadow` (the lab owns that
  // one deliberately) and `props` (props.js keeps its own palette).
  const read = new Set(
    [...render.matchAll(/VIEW\.([a-zA-Z]+)/g)].map((m) => m[1]),
  );
  read.delete('meadow');
  read.delete('props');
  assert(read.size > 0, 'found no VIEW reads in render.js -- the scan broke');

  const block = lab.slice(lab.indexOf('var VIEW = {'), lab.indexOf('</script>', lab.indexOf('var VIEW = {')));
  for (const field of read) {
    assert(new RegExp(`\\b${field}\\s*:`).test(block),
      `the lab's VIEW stand-in is missing \`${field}\`, which render.js reads`);
  }

  // And the values have to agree, not merely exist.
  for (const [field, re] of [['waterline', /^  waterline: ([\d.]+),/m], ['cloudPeriodMs', /^  cloudPeriodMs: (\d+),/m]]) {
    const shipped = animSrc.match(re);
    assert(shipped, `could not read VIEW.${field} out of anim.js`);
    const labValue = block.match(new RegExp(`${field}:\\s*([\\d.]+)`));
    assert(labValue, `the lab does not set ${field}`);
    assert(labValue[1] === shipped[1],
      `the lab has ${field} ${labValue[1]}, anim.js ships ${shipped[1]}`);
  }
});

console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
