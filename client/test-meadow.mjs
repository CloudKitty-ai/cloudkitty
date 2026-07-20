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
  readFileSync(join(here, 'meadow.js'), 'utf8') +
  ';' +
  readFileSync(join(here, 'anim.js'), 'utf8');

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

const EXPORTS =
  ';({ MEADOW, MEADOW_SALTS, MEADOW_DEFAULTS, tileHash, drawMeadowGround, drawGridOverlay, groupWaterTiles, buildPondPath, drawPonds, drawWorldEdge, drawSunbeamGlow, drawWornPaths, VIEW, Presentation })';
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

check('drawMeadowGround / drawGridOverlay / drawWorldEdge sweep clean', () => {
  for (const [width, height] of DIMS) {
    for (const tile of TILES) {
      const ctx = guardCtx();
      api.drawMeadowGround(ctx, { width, height, tile });
      api.drawGridOverlay(ctx, { width, height, tile });
      api.drawWorldEdge(ctx, { width, height, tile });
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

check('world edge stays within the boundary-tile margin (FR-007)', () => {
  for (const [width, height] of DIMS) {
    const tile = 22;
    const log = [];
    api.drawWorldEdge(guardCtx(log), { width, height, tile });
    const depth = api.MEADOW_DEFAULTS.edgeDepth * tile;
    const w = width * tile;
    const h = height * tile;
    // Every drawn coordinate must hug a border to within the fringe reach
    // (plus the small lean allowance).
    const slack = depth + tile * 0.3;
    for (const [name, ...args] of log) {
      if (name !== 'moveTo' && name !== 'quadraticCurveTo' && name !== 'fillRect') continue;
      const points =
        name === 'fillRect'
          ? [[args[0], args[1]], [args[0] + args[2], args[1] + args[3]]]
          : [[args[args.length - 2], args[args.length - 1]]];
      for (const [x, y] of points) {
        const nearBorder =
          x <= slack || y <= slack || x >= w - slack || y >= h - slack;
        assert(nearBorder, `${name} at (${x},${y}) strays from the border`);
      }
    }
  }
});

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

console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
