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
function mockCanvas(width = 640, height = 640) {
  const canvas = { width, height, dataset: {}, style: {} };
  const ctx = guardCtx([]);
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
  ' driftField,' +
  ' WorldRenderer })';
const api = eval(src + EXPORTS);

let passed = 0;
let failed = 0;
function check(name, fn) {
  try {
    fn();
    passed += 1;
    console.log(`  ok   ${name}`);
  } catch (err) {
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
      x: 2, y: 2, seed: 0.5, tile: 40, t: { ...api.VIEW.meadow, bushStyle },
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

  // 0 must be EXACTLY the behaviour that existed before the dial did, or
  // this is a silent restyle of the live world rather than a new option.
  assert(t.bushStyleAltShare === 0, 'the alt share must ship at 0');
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

// The summary stays LAST. It sat mid-file once and every check appended
// after it ran past `process.exit` and was silently never counted -- the
// suite reported green on tests that had not run. (Cost the motion suite
// a round of this too.)
console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
