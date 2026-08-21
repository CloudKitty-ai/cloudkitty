/**
 * Headless checks for the v2 live-motion wiring -- run with
 * `node client/test-motion.mjs`.
 *
 * The 005/007/008 harness pattern: eval the plain scripts in one shared
 * scope, drive the logic directly, assert exact values. Presentation's
 * tween/blink decisions are tested as pure functions of draw calls; the
 * drawCatTween endpoints are checked structurally (a finished blend must
 * be command-for-command the held pose) through a guarding mock ctx that
 * throws on any non-finite numeric argument.
 */
import { existsSync, readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const animSrc = readFileSync(join(here, 'anim.js'), 'utf8');
const catV2Src = readFileSync(join(here, 'cat-v2.js'), 'utf8');
const renderSrc = readFileSync(join(here, 'render.js'), 'utf8');
const appSrc = readFileSync(join(here, 'app.js'), 'utf8');

/**
 * A `const NAME = <number>;` declared in app.js, read from the SHIPPED
 * source rather than copied. Two checks want the portrait dials now -- the
 * card geometry, and the camera's own size floor -- and a copy in either
 * would drift silently the moment the owner re-dials the cards.
 */
const appNum = (name) => {
  const m = appSrc.match(new RegExp(`const ${name} = ([\\d.]+);`));
  assert(m, `app.js still declares ${name}`);
  return Number(m[1]);
};

const api = eval(
  animSrc +
    ';({ VIEW, Presentation, Pacer, easeSmooth, slowBlinkLid, idleHash, idlePeriodFor,' +
    ' idlePickFor, idleOffsetFor, IDLE_SALTS, anim, nearestAdjacentOf, Camera, clampFrame })',
);

/**
 * A slot that actually draws `want`, and the clock reading that puts a cat
 * `x` ms into that motion. Which slot gets which motion is hashed now, so a
 * test cannot assume slot 0 is a blink starting on the beat -- it has to go
 * and find one. Slots start at 5 so `now` stays positive.
 */
function slotOf(api, id, want, dials = api.VIEW) {
  const period = api.idlePeriodFor(id, dials);
  const span =
    want === 'blink'
      ? dials.slowBlinkDownMs + dials.slowBlinkHoldMs + dials.slowBlinkUpMs
      : dials.idleMotionWindowMs;
  for (let slot = 5; slot < 400; slot++) {
    if (api.idlePickFor(id, slot, dials) !== want) continue;
    const off = api.idleOffsetFor(id, slot, period, span, dials);
    return { slot, period, off, span, at: (x) => slot * period + off + x - id * 1337 };
  }
  return null;
}
eval(catV2Src); // IIFE: registers globalThis.CatV2
const CatV2 = globalThis.CatV2;

/**
 * What the art blocks hold as SHIPPED, before any check has run.
 *
 * Half the checks here dial a value, draw, and put it back. A check that
 * forgets -- or that restores to a hardcoded literal after the owner has
 * re-baked the real one -- leaves every later check drawing a different
 * cat, silently and in a way no single assertion can see. The last check
 * in the file compares against this.
 */
const SHIPPED_BLOCKS = Object.fromEntries(
  Object.entries(CatV2)
    .filter(([, v]) => v && typeof v === 'object' && !Array.isArray(v) && !(v instanceof Set) && !(v instanceof Map))
    .map(([k, v]) => [k, JSON.stringify(v)]),
);
// render.js reads `VIEW` as a global (the browser loads anim.js alongside
// it); each eval here gets its own scope, so hand it one. Direct eval runs
// in this scope, so the binding is visible to the code below -- and it is
// the SAME object anim.js built, so a re-dialled tunable cannot diverge
// between what the harness tests and what the page draws.
const VIEW = api.VIEW;
const {
  poseFor, ACTION_POSE, WorldRenderer, waterlineFor, chaseDistanceFor, submersionFor, surfaceForPose,
  swimAxialAllows, gazeTargetFor, MEOW_TEXT, SOUND_WORDS, pursuitDistanceFor,
} = eval(
  renderSrc +
    ';({ poseFor, ACTION_POSE, WorldRenderer, waterlineFor, chaseDistanceFor, submersionFor, surfaceForPose,' +
    ' swimAxialAllows, gazeTargetFor, MEOW_TEXT, SOUND_WORDS, pursuitDistanceFor })',
);

/** Canvas ctx stand-in: logs every command, throws on non-finite numbers. */
function guardCtx(log = []) {
  return new Proxy(
    {},
    {
      get(target, prop) {
        return (...args) => {
          for (const a of args) {
            if (typeof a === 'number' && !Number.isFinite(a)) {
              throw new Error(`ctx.${prop} got non-finite args: ${args}`);
            }
          }
          log.push([prop, ...args.map((a) => (typeof a === 'object' ? '<obj>' : a))]);
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

const kitty = (id, x, y) => ({ id, pos: { x, y }, needs: {} });
const world = (tick, kitties) => ({ tick, kitties, elements: [] });

// ---- tweenFor: the pose blend ----

check('first sight records and never blends', () => {
  const p = new api.Presentation();
  assert(p.tweenFor(1, 'idle', 0.2, 1000) === null, 'no blend from nothing');
  assert(p.poseTween.size === 0, 'no tween record');
});

check('a held pose stays a held pose', () => {
  const p = new api.Presentation();
  p.tweenFor(1, 'idle', 0.1, 1000);
  assert(p.tweenFor(1, 'idle', 0.3, 1200) === null, 'same pose, no blend');
});

check('a pose change blends: smoothstep t, frozen from-phase', () => {
  const p = new api.Presentation();
  p.tweenFor(1, 'idle', 0.25, 1000);
  const start = p.tweenFor(1, 'eating', 0.5, 1100);
  assert(start.blend, 'blend opens on the change');
  assert(start.blend.from === 'idle', `from ${start.blend.from}`);
  close(start.blend.fromPhase, 0.25, 'from-phase frozen at last draw');
  close(start.blend.t, 0, 't starts at 0');
  const mid = p.tweenFor(1, 'eating', 0.6, 1230); // 130/260 = the exact midpoint
  close(mid.blend.t, 0.5, 'smoothstep midpoint is exactly 1/2');
  close(mid.blend.fromPhase, 0.25, 'from-phase still frozen');
});

check('the blend ends on time and is forgotten', () => {
  const p = new api.Presentation();
  p.tweenFor(1, 'idle', 0, 1000);
  p.tweenFor(1, 'eating', 0, 1100);
  assert(p.tweenFor(1, 'eating', 0, 1100 + api.VIEW.poseBlendMs - 1)?.blend, 'still blending at the edge');
  assert(p.tweenFor(1, 'eating', 0, 1100 + api.VIEW.poseBlendMs) === null, 'done exactly at poseBlendMs');
  assert(p.poseTween.size === 0, 'record cleaned up');
});

check('arriving (walking -> stand) settles, concurrent with its blend', () => {
  for (const stand of ['idle', 'loaf']) {
    const p = new api.Presentation();
    p.tweenFor(1, 'walking', 0.9, 1000);
    const t0 = p.tweenFor(1, stand, 0.1, 1080);
    assert(t0.blend && t0.sy !== undefined, `${stand}: blend and settle together`);
    close(t0.sy, 1, `${stand}: settle starts flat`);
    const t200 = p.tweenFor(1, stand, 0.1, 1280); // 200/400: sin(pi * smoothstep(1/2)) = 1
    close(t200.sy, 1 - api.VIEW.settleDip, `${stand}: peak squash is exactly the dip`);
    const tail = p.tweenFor(1, stand, 0.1, 1080 + api.VIEW.arriveBlendMs + 10);
    assert(!tail.blend && tail.sy !== undefined, `${stand}: settle outlives the blend`);
    assert(p.tweenFor(1, stand, 0.1, 1080 + api.VIEW.settleMs) === null, `${stand}: settle ends on time`);
    assert(p.poseTween.size === 0, `${stand}: record cleaned up`);
  }
});

check('only walking -> stand settles', () => {
  const pairs = [
    ['walking', 'eating'],
    ['walking', 'swim'],
    ['idle', 'loaf'],
    ['loaf', 'sleep-curl'],
    ['pouncing', 'idle'],
    ['swim', 'idle'],
  ];
  for (const [from, to] of pairs) {
    const p = new api.Presentation();
    p.tweenFor(1, from, 0, 1000);
    for (let ms = 0; ms < api.VIEW.settleMs; ms += 40) {
      const r = p.tweenFor(1, to, 0, 1100 + ms);
      assert(!r || r.sy === undefined, `${from}->${to} must not settle (at +${ms})`);
    }
  }
});

check('newest wins: a change mid-blend restarts from the old target', () => {
  const p = new api.Presentation();
  p.tweenFor(1, 'idle', 0.2, 1000);
  p.tweenFor(1, 'walking', 0.4, 1100); // idle -> walking opens
  const r = p.tweenFor(1, 'pouncing', 0.6, 1200); // preempted mid-blend
  assert(r.blend.from === 'walking', `restarts from walking, got ${r.blend.from}`);
  close(r.blend.fromPhase, 0.4, 'from-phase is walking as last drawn');
  close(r.blend.t, 0, 'restart begins at 0');
});

check('a draw gap past a tick snaps instead of blending', () => {
  const p = new api.Presentation();
  p.tweenFor(1, 'idle', 0, 1000);
  assert(p.tweenFor(1, 'eating', 0, 1000 + p.tickMs + 1) === null, 'stale change snaps');
  assert(p.poseTween.size === 0, 'and leaves no record');
});

check('fast ticks cap the blend at the tick-share', () => {
  const p = new api.Presentation();
  p.tickMs = 400; // capped blend = 0.45 * 400 = 180 < 260
  p.tweenFor(1, 'idle', 0, 1000);
  p.tweenFor(1, 'eating', 0, 1100);
  const mid = p.tweenFor(1, 'eating', 0, 1190); // 90/180
  close(mid.blend.t, 0.5, 'midpoint lands at half the capped window');
  assert(p.tweenFor(1, 'eating', 0, 1280) === null, 'done at the capped window');
});

check('a discontinuity clears all blend memory', () => {
  const p = new api.Presentation();
  p.pushState(world(1, [kitty(1, 2, 2)]), 1000);
  p.pushState(world(2, [kitty(1, 2, 2)]), 1800);
  p.tweenFor(1, 'idle', 0, 1900);
  p.tweenFor(1, 'eating', 0, 1950); // blend in flight
  p.pushState(world(9, [kitty(1, 2, 2)]), 2600); // tick jump: a different moment
  assert(p.lastPose.size === 0 && p.poseTween.size === 0, 'memory cleared');
  assert(p.tweenFor(1, 'idle', 0, 2700) === null, 'first sight again');
});

check('still frames neither blend nor record', () => {
  const p = new api.Presentation();
  p.pushState(world(1, [kitty(1, 2, 2)]), 1000);
  const still = p.viewAt(1100, true);
  assert(still.tweenFor(1, 'idle', 0) === null, 'still frame: null');
  assert(p.lastPose.size === 0, 'still frame: nothing recorded');
  const moving = p.viewAt(1200, false);
  assert(moving.tweenFor(1, 'idle', 0.5) === null, 'first motion frame: first sight');
  assert(p.lastPose.size === 1, 'motion frame: recorded');
});

// ---- motionFor: the slow-blink lid ----

check('the slow-blink lid walks the lab envelope exactly', () => {
  const p = new api.Presentation();
  const blink = slotOf(api, 1, 'blink');
  assert(blink, 'found a slot that draws a blink');
  const lidAt = (x) => p.motionFor(1, 'idle', blink.at(x)).blinkLid;
  // Derived from the dials, not restated: these spans are meant to be
  // re-judged in the lab, and a midpoint written out as a number turns
  // every re-dial into a test failure that says nothing about the shape.
  const { slowBlinkDownMs: down, slowBlinkHoldMs: hold, slowBlinkUpMs: up } = api.VIEW;
  close(lidAt(0), 0, 'starts open');
  close(lidAt(down / 2), 0.5, 'half-down at the down midpoint');
  close(lidAt(down), 1, 'fully down');
  close(lidAt(down + hold), 1, 'held');
  close(lidAt(down + hold + up / 2), 0.5, 'half-up at the up midpoint');
  const total = down + hold + up;
  assert(lidAt(total) === undefined, 'over after the envelope');
  // Not an art constraint, so unlike the spans themselves this is pinned:
  // `at` arrives modulo the idle slot, so a blink that outlasts its own
  // slot is always in progress and the eyes never settle open again.
  assert(
    total < api.VIEW.idleMotionPeriodMs,
    `a ${total}ms blink must fit the ${api.VIEW.idleMotionPeriodMs}ms idle slot`,
  );
});

// The v2 lab drives its Slow blink card through this same function with a
// bag of slider values, because VIEW is frozen. If the override stopped
// working the lab would silently judge the shipped numbers instead of the
// dialled ones -- and bake whatever it was shown.
check('slowBlinkLid takes its values from the bag it is given', () => {
  const p = new api.Presentation();
  const { slowBlinkDownMs: down, slowBlinkHoldMs: hold, slowBlinkUpMs: up } = api.VIEW;
  // Twice the shipped envelope, derived rather than written out, so a
  // re-dial cannot leave this test asserting against yesterday's numbers.
  const dials = {
    slowBlinkDownMs: down * 2,
    slowBlinkHoldMs: hold * 2,
    slowBlinkUpMs: up * 2,
  };
  close(api.slowBlinkLid(down, dials), 0.5, 'half-down at the dialled midpoint');
  close(api.slowBlinkLid(down * 2, dials), 1, 'shut when the dialled down ends');
  close(api.slowBlinkLid(down * 2 + hold, dials), 1, 'still shut through the dialled hold');
  close(api.slowBlinkLid((down + hold) * 2 + up, dials), 0.5, 'half-up at the dialled midpoint');
  assert(api.slowBlinkLid((down + hold + up) * 2, dials) === undefined, 'over after it');
  // The instant the shipped blink ends is the cleanest place to see which
  // envelope is in charge: one is finished, the other still has half to run.
  // Asked of the envelope directly, not through `motionFor` -- which slot
  // is blinking is the schedule's business, and has nothing to say here.
  const shipped = down + hold + up;
  assert(api.slowBlinkLid(shipped) === undefined, 'the shipped envelope is over');
  assert(api.slowBlinkLid(shipped, dials) !== undefined, 'the dialled one is still going');
  // Defaulting is what `motionFor` relies on.
  close(api.slowBlinkLid(down), 1, 'no bag: falls back to VIEW');
});

check('the v1 snap blink is untouched beside the lid', () => {
  const p = new api.Presentation();
  const blink = slotOf(api, 1, 'blink');
  const w = api.VIEW.idleMotionWindowMs;
  const inside = p.motionFor(1, 'idle', blink.at(w / 2));
  assert(inside.eyesOverride === 'closed', 'v1 window: snapped closed');
  assert(inside.blinkLid !== undefined, 'v2 lid runs alongside');
  const after = p.motionFor(1, 'idle', blink.at(w + 10));
  assert(after.eyesOverride === undefined, 'v1 window over: eyes open');
  assert(after.blinkLid !== undefined, 'the eased lid is still easing');
});

check('only a blink slot wears a lid', () => {
  const p = new api.Presentation();
  for (const want of ['ears', 'rest']) {
    const s = slotOf(api, 1, want);
    assert(s, `found a slot that draws ${want}`);
    // Sweep the whole slot: no part of it may carry a lid.
    for (let x = 0; x < s.period; x += 25) {
      const m = p.motionFor(1, 'idle', s.slot * s.period + x - 1337);
      assert(m.blinkLid === undefined, `${want} slot has no lid at +${x}ms`);
    }
  }
});

// ---- the idle schedule: hashed, bounded, and weighted ----

check('a rest slot is a real nothing, not a fast breath', () => {
  const p = new api.Presentation();
  const rest = slotOf(api, 1, 'rest');
  for (let x = 0; x < rest.period; x += 25) {
    const now = rest.slot * rest.period + x - 1337;
    const m = p.motionFor(1, 'idle', now);
    assert(m.eyesOverride === undefined, `no snap blink at +${x}ms`);
    assert(m.earsBack === undefined, `no ear twitch at +${x}ms`);
    assert(m.blinkLid === undefined, `no lid at +${x}ms`);
    // The old tail-flick branch overrode the breathing phase; a rest slot
    // must leave the ambient breath exactly as it found it.
    const ambient = ((now + 997) % api.VIEW.breathePeriodMs) / api.VIEW.breathePeriodMs;
    close(m.phase, ambient, `breathing undisturbed at +${x}ms`);
  }
});

check('no motion ever overruns its slot', () => {
  const p = new api.Presentation();
  for (const id of [1, 2, 3, 4]) {
    const period = api.idlePeriodFor(id);
    for (let slot = 5; slot < 60; slot++) {
      const pick = api.idlePickFor(id, slot);
      if (pick === 'rest') continue;
      const span =
        pick === 'blink'
          ? api.VIEW.slowBlinkDownMs + api.VIEW.slowBlinkHoldMs + api.VIEW.slowBlinkUpMs
          : api.VIEW.idleMotionWindowMs;
      const off = api.idleOffsetFor(id, slot, period, span);
      assert(off >= 0, `id ${id} slot ${slot}: offset is not negative`);
      assert(
        off + span <= period + 1e-6,
        `id ${id} slot ${slot}: ${pick} ends inside its own slot`,
      );
    }
  }
});

check('the weights are what decides how often each motion lands', () => {
  // The table is five-way since 2026-08-10 (scan and yawn joined). Every
  // weight is set explicitly: spreading VIEW and overriding three of them
  // left scan and yawn at their shipped values, silently diluting the shares
  // this asserts -- blink came out at 0.599 against an expected 0.70, which
  // reads as a broken hash rather than an incomplete fixture.
  const dials = {
    idleBlinkWeight: 70, idleEarsWeight: 20, idleScanWeight: 0,
    idleYawnWeight: 0, idleRestWeight: 10,
  };
  const seen = { blink: 0, ears: 0, scan: 0, yawn: 0, rest: 0 };
  const N = 4000;
  for (let slot = 0; slot < N; slot++) seen[api.idlePickFor(1, slot, dials)]++;
  // Loose bounds: this is asserting the draw is weighted, not that the
  // hash is a perfect uniform generator.
  assert(Math.abs(seen.blink / N - 0.7) < 0.03, `blink share ${(seen.blink / N).toFixed(3)} ~ 0.70`);
  assert(Math.abs(seen.ears / N - 0.2) < 0.03, `ears share ${(seen.ears / N).toFixed(3)} ~ 0.20`);
  assert(Math.abs(seen.rest / N - 0.1) < 0.03, `rest share ${(seen.rest / N).toFixed(3)} ~ 0.10`);
  assert(seen.scan === 0 && seen.yawn === 0, 'a zero weight must never be drawn');
  // And the shipped table still spends its whole budget somewhere.
  const shipped = ['idleBlinkWeight', 'idleEarsWeight', 'idleScanWeight', 'idleYawnWeight', 'idleRestWeight']
    .reduce((sum, k) => sum + api.VIEW[k], 0);
  assert(shipped === 100, `the shipped idle weights should total 100, got ${shipped}`);
  // All the weight on one motion means every slot draws it.
  const only = {
    idleBlinkWeight: 0, idleEarsWeight: 1, idleScanWeight: 0,
    idleYawnWeight: 0, idleRestWeight: 0,
  };
  for (let slot = 0; slot < 50; slot++) {
    assert(api.idlePickFor(1, slot, only) === 'ears', `slot ${slot}: only ears can be drawn`);
  }
});

check('jitter moves a motion inside its slot, and zero jitter is on the beat', () => {
  const still = { ...api.VIEW, idleJitter: 0 };
  const loose = { ...api.VIEW, idleJitter: 1 };
  const period = api.idlePeriodFor(1, still);
  const span = api.VIEW.idleMotionWindowMs;
  const offsets = new Set();
  for (let slot = 5; slot < 40; slot++) {
    close(api.idleOffsetFor(1, slot, period, span, still), 0, `slot ${slot}: no jitter, on the beat`);
    offsets.add(Math.round(api.idleOffsetFor(1, slot, period, span, loose)));
  }
  assert(offsets.size > 25, `jitter spreads the starts (${offsets.size} distinct of 35)`);
});

check('cats run their own tempos, and the schedule is deterministic', () => {
  const p = new api.Presentation();
  const periods = [1, 2, 3, 4].map((id) => api.idlePeriodFor(id));
  assert(new Set(periods.map(Math.round)).size === 4, `four cats, four tempos: ${periods.map(Math.round)}`);
  for (const period of periods) {
    const drift = Math.abs(period / api.VIEW.idleMotionPeriodMs - 1);
    assert(drift <= api.VIEW.idleTempoSpread + 1e-9, `tempo stays inside the spread (${drift.toFixed(3)})`);
  }
  // Purity is what still frames, reduced motion and this harness all rely
  // on: the same cat at the same instant is always doing the same thing.
  for (const now of [1234, 20000, 987654]) {
    const a = JSON.stringify(p.motionFor(3, 'idle', now));
    const b = JSON.stringify(new api.Presentation().motionFor(3, 'idle', now));
    assert(a === b, `id 3 at ${now}ms is the same on a fresh Presentation`);
  }
});

// ---- drawCatTween: structural endpoint identity ----

check('a finished blend is command-for-command the held pose', () => {
  const appearance = CatV2.appearanceFor(3);
  const pairs = [
    ['idle', 'walking'],
    ['walking', 'loaf'],
    ['loaf', 'sleep-curl'],
    ['eating', 'idle'],
    ['walking', 'swim'],
    ['swim', 'idle'],
  ];
  for (const [from, to] of pairs) {
    const base = { appearance, facing: 'right', size: 22, x: 3, y: 4 };
    const logTween0 = [];
    CatV2.drawCatTween(guardCtx(logTween0), { ...base, from, to, t: 0, phaseFrom: 0.3, phaseTo: 0.7 });
    const logFrom = [];
    CatV2.drawCat(guardCtx(logFrom), { ...base, pose: from, phase: 0.3 });
    assert(JSON.stringify(logTween0) === JSON.stringify(logFrom), `${from}->${to}: t=0 is exactly ${from}`);
    const logTween1 = [];
    CatV2.drawCatTween(guardCtx(logTween1), { ...base, from, to, t: 1, phaseFrom: 0.3, phaseTo: 0.7 });
    const logTo = [];
    CatV2.drawCat(guardCtx(logTo), { ...base, pose: to, phase: 0.7 });
    assert(JSON.stringify(logTween1) === JSON.stringify(logTo), `${from}->${to}: t=1 is exactly ${to}`);
  }
});

check('every blend frame sweeps clean at every lid depth', () => {
  const appearance = CatV2.appearanceFor(1);
  for (const from of CatV2.POSES) {
    for (const to of CatV2.POSES) {
      if (from === to) continue;
      for (let t = 0; t <= 1; t += 0.25) {
        for (const lid of [0, 0.37, 1]) {
          CatV2.drawCatTween(guardCtx(), {
            from, to, t, lid, appearance, facing: 'left', size: 22, x: 0, y: 0,
            phaseFrom: 0.9, phaseTo: 0.1,
          });
        }
      }
    }
  }
});

// ---- the swim pose (spec 010's parked wading pose) ----

check('swim is in the v2 vocabulary with the wading silhouette', () => {
  assert(CatV2.POSES.includes('swim'), 'POSES lists swim');
  const L = CatV2.catLayout('swim', 0.25);
  assert(L.legs.length === 0, 'legs paddle out of sight');
  // The splash droplet was cut 2026-08-04 -- see the dedicated check below.
  close(L.head.r, 0.226, 'the locked head radius is untouched');
  assert(L.body.ry < 0.21, 'body floats flatter than standing');
  assert(L.eyes === 'open', 'eyes open above water');
  assert(L.earsUpright === true, 'ears dry and up');
});

check('a nap still ends in a stretch, through the REAL two-layer pipeline', () => {
  // This is the check that was missing. When `poseFor` started reading the
  // applied action, the tick a nap ends began arriving at `idlePoseFor` as
  // `sleep-curl` instead of `idle` -- and its guard deleted the wake on the
  // very tick it was recorded, which removed EVERY stretch in the world.
  // 147 assertions passed while that happened, because each layer was only
  // ever checked on its own. So this one composes them.
  const rows = JSON.parse(readFileSync(join(here, 'fixtures/scene-ends.json'), 'utf8'));
  const asleep = rows.find((r) => r.case === 'mid:sleep').kitty;
  const waking = rows.find((r) => r.case === 'end:sleep').kitty;
  assert(asleep.activity.state === 'sleeping' && waking.activity.state !== 'sleeping',
    'the fixture no longer holds a sleep and the tick it ends on');

  const p = new api.Presentation();
  const drawn = (kit, now) => {
    // Exactly what render.js does: the served pose, then the cat's own
    // idle initiative on top of it.
    const served = poseFor(kit, false, false, null);
    const own = p.idlePoseFor(kit.id, served, now);
    return own ? own.pose : served;
  };
  // Ingest through pushState so the wake is recorded the way it is live,
  // rather than by reaching into `wokeAt` and asserting our own bookkeeping.
  const at = (tick, kit) => ({ tick, width: 20, height: 20, kitties: [kit], elements: [] });
  p.pushState(at(1, asleep), 0, p.tickMs);
  p.pushState(at(2, asleep), p.tickMs, p.tickMs);
  assert(drawn(asleep, p.tickMs) === 'sleep-curl', 'a cat mid-nap should be curled up');

  p.pushState(at(3, waking), p.tickMs * 2, p.tickMs);
  assert(drawn(waking, p.tickMs * 2) === 'stretch',
    `a waking cat drew ${drawn(waking, p.tickMs * 2)} -- a nap ends in a stretch`);

  // ...and the served pose underneath it is the honest one, so the stretch
  // is an idle overlay rather than a second opinion about what happened.
  assert(poseFor(waking, false, false, null) === 'sleep-curl',
    'the wake tick applied sleep, so that is what the served pose must say');

  // The stretch is abandoned, not banked, once the engine asks for something.
  const busy = { ...waking, last_action: { action: 'eat' } };
  assert(drawn(busy, p.tickMs * 2.5) === 'eating', 'an interrupted stretch must give way');
  assert(drawn(waking, p.tickMs * 3) === 'sleep-curl',
    'an abandoned stretch must not resume halfway through');
});

// A world just big enough to look around in: a cat at 5,5 with a friend, a
// bowl and a puddle around it.
const gazeWorld = () => ({
  tick: 1,
  width: 20,
  height: 20,
  kitties: [
    { id: 1, name: 'A', pos: { x: 5, y: 5 }, activity: { state: 'idle' } },
    { id: 2, name: 'B', pos: { x: 6, y: 5 }, activity: { state: 'idle' } },
    { id: 3, name: 'C', pos: { x: 5, y: 9 }, activity: { state: 'idle' } },
  ],
  elements: [
    { id: 40, kind: 'chow', pos: { x: 4, y: 5 } },
    { id: 41, kind: 'water', pos: { x: 5, y: 6 } },
    { id: 42, kind: 'chow', pos: { x: 12, y: 12 } },
  ],
});
const looker = (w) => w.kitties[0];

check('the gaze reads the kind-and-id shape, and reads it the right way round', () => {
  const w = gazeWorld();
  const me = looker(w);
  const at = (action) => {
    me.last_action = action;
    return gazeTargetFor(me, w, me.pos, null);
  };
  const chased = at({ action: 'chase', target: 'kitty', id: 3 });
  assert(chased && chased.y > 0.5, `chasing the cat to the south looked ${JSON.stringify(chased)}`);
  const bug = at({ action: 'chase', target: 'element', id: 42 });
  assert(bug && bug.x > 0.5, 'chasing an element to the east should look east');
  assert(at({ action: 'chase', target: 'kitty', id: 99 }) === null, 'a quarry that is not served');

  // `target` is the KIND here, never the id. Element ids and kitty ids
  // overlap -- elements ran 1-233 against kitties 1-4 in the live world --
  // so reading the wrong one aims at a different object rather than failing.
  w.elements.push({ id: 2, kind: 'chow', pos: { x: 5, y: 1 } });
  assert(at({ action: 'chase', target: 'kitty', id: 2 }).x > 0.9, 'id 2 as a KITTY is the cat to the east');
  assert(at({ action: 'chase', target: 'element', id: 2 }).y < -0.5, 'the same id as an ELEMENT is the bowl north');
});

check('the other target shapes are PARKED, and that is a decision', () => {
  // Built, measured and taken back out (owner, 2026-08-14). Reading groom's
  // bare kitty id and resolving eat/drink from the map took the gaze from
  // 5.2% of cat-ticks to 36.5% -- and it did not read. The only gaze channel
  // above the pixel floor at this tile is the ear lean, which responds to the
  // HORIZONTAL component alone, and 54% of the targets those sources add sit
  // directly north or south of the cat, where `gaze.x` is 0 and the ears do
  // not move at all. Grooming was worst: cats groom side by side, so 59% of
  // its ticks moved nothing and 26% leaned the ears the wrong way. Chase and
  // play, which stay, read at 43%.
  //
  // What is missing is a channel for `gaze.y`, not more sources, and it wants
  // judging at camera zoom where the pupil (0.48px here) and the head follow
  // (0.35px) are legible. Flipping this check is how they come back.
  const w = gazeWorld();
  const me = looker(w);
  const at = (action) => {
    me.last_action = action;
    return gazeTargetFor(me, w, me.pos, null);
  };
  assert(at({ action: 'groom', target: 2 }) === null,
    'grooming a friend is parked -- see the gaze entry in BACKLOG.md');
  assert(at({ action: 'eat' }) === null, 'eating is parked');
  assert(at({ action: 'drink' }) === null, 'drinking is parked');
  // The pose already names the activity in all three, which is the part that
  // reads. What the gaze would have added is WHICH thing, and at this tile
  // it cannot say it.
  assert(poseFor({ ...me, last_action: { action: 'groom', target: 2 } }, false) === 'grooming',
    'the pose still names the activity, which is the part that reads');
});

check('the gaze aims where the target is DRAWN, not where it is served', () => {
  // The same mistake as the pose bug, one function over: the looking cat's
  // position was already the drawn one and the target's was served, so a cat
  // looked at where its quarry WILL be -- grass. Half of all gaze-firing
  // ticks had a moving target, off by a median 8.1 degrees and up to 26.6.
  //
  // Three precedents in render.js say drawn: the wade pose keys on "the tile
  // under the DRAWN cat, not the served destination", submersionFor samples
  // where the cat visibly is, and the depth layer sorts by elementPosFor.
  const w = gazeWorld();
  const me = looker(w);
  me.last_action = { action: 'chase', target: 'kitty', id: 3 };
  // The quarry is served to the south but is DRAWN to the east, halfway
  // through its step. A view that lies this hard is the only way to tell
  // which end the function read.
  const view = {
    posFor: (k) => (k.id === 3 ? { x: 9, y: 5 } : k.pos),
    elementPosFor: (el) => (el.id === 42 ? { x: 5, y: 1 } : el.pos),
  };
  const served = gazeTargetFor(me, w, me.pos, null);
  const drawn = gazeTargetFor(me, w, me.pos, view);
  assert(served.y > 0.5, 'sanity: served has the quarry to the south');
  assert(drawn.x > 0.9 && Math.abs(drawn.y) < 0.2,
    `the gaze followed the served position, not the drawn one: ${JSON.stringify(drawn)}`);

  // Elements too -- critters glide, and a butterfly is the thing most worth
  // watching move.
  me.last_action = { action: 'chase', target: 'element', id: 42 };
  const el = gazeTargetFor(me, w, me.pos, view);
  assert(el.y < -0.5, `an element gaze ignored elementPosFor: ${JSON.stringify(el)}`);

  // And with no view at all -- v1 callers, still frames -- it falls back to
  // the served position rather than throwing.
  me.last_action = { action: 'chase', target: 'kitty', id: 2 };
  assert(gazeTargetFor(me, w, me.pos, null).x > 0.9, 'a missing view must not break the gaze');
  assert(gazeTargetFor(me, w, me.pos, {}).x > 0.9, 'a view without posFor must not break the gaze');
});

check('the gaze has NO MEMORY: an action naming nothing looks at nothing', () => {
  // Owner's decision, 2026-08-13, and it rules an approach OUT. Holding the
  // last target is the obvious way to raise the fire rate, and it is not
  // what we want: a cat that has stopped should not still be staring.
  const w = gazeWorld();
  const me = looker(w);
  for (const action of [
    { action: 'move', direction: 'east' },
    { action: 'idle' },
    { action: 'purr' },
    { action: 'meow', message: 'hello' },
    { action: 'play' },
    { action: 'sleep', with: 2 },
    // These two DO name something resolvable; not looking at them is the
    // parked decision above, not an absence of data.
    { action: 'groom', target: 2 },
    { action: 'eat' },
  ]) {
    me.last_action = action;
    assert(gazeTargetFor(me, w, me.pos, null) === null,
      `${action.action} names nothing to look at, so the gaze must be null`);
  }
  assert(gazeTargetFor({ ...me, last_action: undefined }, w, me.pos, null) === null,
    'a cat with no last_action at all looks at nothing');
});

check('poseFor: the LAST tick of a scene draws what the cat did, not idle', () => {
  // The bug, stated against real wire. `activity` is the scene in progress as
  // of END of tick; `last_action` is what the engine applied DURING it. The
  // engine acts, then clears scenes that ended, then publishes -- so a
  // scene's final tick truthfully reports both `last_action: eat` and
  // `state: idle`, and reading the state drew a cat standing about on 17.4%
  // of every cat-tick: half of every meal and drink, and a sleeper sitting
  // bolt upright for the last 600ms of every nap.
  //
  // The fixture is eight real cat-ticks lifted from a live capture rather
  // than hand-built objects, because the thing that was wrong was a belief
  // about the WIRE, and a hand-built object would just restate the belief.
  const rows = JSON.parse(readFileSync(join(here, 'fixtures/scene-ends.json'), 'utf8'));
  const want = {
    eat: 'eating', drink: 'drinking', groom: 'grooming', sleep: 'sleep-curl',
  };
  const seen = new Set();
  for (const row of rows) {
    const [when, action] = row.case.split(':');
    seen.add(row.case);
    // Not moving and not on water, so nothing below the scene can answer:
    // whatever comes back came from the action or the scene.
    const got = poseFor(row.kitty, false, false, null);
    assert(got === want[action],
      `${row.case}: served ${JSON.stringify(row.kitty.last_action)} with ` +
      `${JSON.stringify(row.kitty.activity)} and drew ${got}, wanted ${want[action]}`);
    if (when === 'end') {
      assert(row.kitty.activity.state === 'idle',
        `${row.case} is not a scene END -- the fixture no longer covers the bug`);
    }
  }
  for (const a of Object.keys(want)) {
    assert(seen.has(`end:${a}`) && seen.has(`mid:${a}`),
      `the fixture lost its ${a} pair -- both the last tick and a mid-scene one are needed`);
  }
});

check('poseFor: the scene still answers for actions that name no pose', () => {
  // This is what keeps the change additive rather than a rewrite. `Idle`,
  // `Purr` and `Meow` are real variants of the engine's Action enum and none
  // of them names a pose, so for those the scene decides exactly as it always
  // did. Drop the fallback and a purring cat stands up out of its nap.
  for (const action of ['idle', 'purr', 'meow']) {
    for (const [state, pose] of [['sleeping', 'sleep-curl'], ['resting', 'loaf'],
      ['eating', 'eating'], ['drinking', 'drinking'], ['grooming', 'grooming']]) {
      const k = { id: 1, pos: { x: 1, y: 1 }, last_action: { action }, activity: { state } };
      assert(poseFor(k, false) === pose,
        `${action} during a ${state} scene drew ${poseFor(k, false)}, wanted ${pose}`);
      // ...and it must not be beaten by movement or water either, which is
      // the precedence the old ordering was really protecting.
      assert(poseFor(k, true, true) === pose, `${action}/${state} lost to water or walking`);
    }
  }
  // A cat doing nothing in no scene is still just a cat.
  const bare = { id: 1, pos: { x: 1, y: 1 }, last_action: { action: 'idle' }, activity: { state: 'idle' } };
  assert(poseFor(bare, false) === 'idle', 'an idle cat in no scene should be idle');
  assert(poseFor(bare, true) === 'walking', 'an idle action that moved is walking');
});

check('poseFor: every pose-naming action in the engine enum is mapped', () => {
  // Read off `crates/cloudkitty-core/src/action.rs` rather than a list kept
  // here: a variant added there with no mapping falls through to idle, which
  // is exactly the failure this whole check exists to stop, and it would ship
  // silently. Only the pose-naming ones are required -- Move, Purr, Meow and
  // Idle deliberately name none.
  const src = readFileSync(join(here, '../crates/cloudkitty-core/src/action.rs'), 'utf8');
  const body = src.slice(src.indexOf('pub enum Action {'));
  const variants = [...body.slice(0, body.indexOf('\n}')).matchAll(/^ {4}(\w+)/gm)]
    .map((m) => m[1].replace(/([a-z])([A-Z])/g, '$1_$2').toLowerCase());
  assert(variants.length > 6, `only parsed ${variants.length} Action variants -- the enum moved`);
  const namesNoPose = new Set(['move', 'purr', 'meow', 'idle']);
  const handled = new Set([...Object.keys(ACTION_POSE), 'play', 'chase']);
  for (const v of variants) {
    if (namesNoPose.has(v)) {
      assert(!handled.has(v), `${v} is meant to name no pose but poseFor maps it`);
    } else {
      assert(handled.has(v), `the engine can serve ${v} and poseFor has no pose for it`);
    }
  }
  // And nothing mapped that the engine cannot send.
  for (const k of Object.keys(ACTION_POSE)) {
    assert(variants.includes(k), `poseFor maps ${k}, which is not an Action variant`);
  }
});

check('poseFor: water under movement and idling, never over the rest', () => {
  const k = (extra) => ({ id: 1, pos: { x: 2, y: 2 }, ...extra });
  assert(poseFor(k({}), true, true) === 'swim', 'moving on water swims');
  assert(poseFor(k({}), false, true) === 'swim', 'floating in place swims');
  assert(poseFor(k({}), true, false) === 'walking', 'dry movement walks');
  assert(poseFor(k({}), true) === 'walking', 'v1 callers (no flag) are untouched');
  assert(poseFor(k({ activity: { state: 'sleeping' } }), false, true) === 'sleep-curl', 'activity outranks water');
  assert(poseFor(k({ activity: { state: 'drinking' } }), false, true) === 'drinking', 'activity outranks water');
  assert(poseFor(k({ last_action: { action: 'chase' } }), true, true) === 'pouncing', 'the pounce outranks water');
});

check('the wading cat’s ripple ships off, beside its sibling water effect', () => {
  // Turned off 2026-08-09: the pond restyle gives the water its own surface
  // motion, and two sets of rings read as a mistake rather than as depth.
  assert(VIEW.ambient.wetRipple === false, 'the ripple must ship off');
  // In `ambient` on purpose -- that block is documented as "each effect
  // individually disableable", and this was the one water cue missing from
  // it. Being there is what makes it a dial rather than a deletion.
  for (const sibling of ['waterShimmer', 'sunbeamPulse', 'dustMotes', 'cloudShadows']) {
    assert(sibling in VIEW.ambient, `ambient lost ${sibling}`);
  }
  // The cue it replaced is not lost: submersion still fades the ground
  // shadow and the clip still cuts the cat. Both are checked elsewhere.
  assert(
    waterlineFor(1, surfaceForPose('idle')) !== null,
    'a submerged cat is still clipped at the waterline',
  );
});

// ---- the belly: a pale underside on every soft cat ----

check('the shipped belly is the one the owner dialled', () => {
  const B = CatV2.BELLY;
  close(B.x, 0.13, 'x drifted');
  close(B.y, 0.55, 'y drifted');
  close(B.rx, 0.62, 'rx drifted');
  close(B.ry, 0.42, 'ry drifted');
  close(B.lighten, 0.35, 'lighten drifted');
  close(B.alpha, 0.85, 'alpha drifted');
  // Low and wide: it should hug the underside, not float in the middle.
  assert(B.y > B.ry, 'the belly must sit below the body centre');
  assert(B.rx > B.ry, 'and read as an underside, not a blob');
});

check('lightenHex mixes toward white without wrapping the byte', () => {
  assert(CatV2.lightenHex('#808080', 0) === '#808080', 't=0 is the colour itself');
  assert(CatV2.lightenHex('#808080', 1) === '#ffffff', 't=1 is white');
  // The exact trap this helper exists for: shadeHex multiplies, so a
  // factor above 1 runs past 255 and wraps a pale cat to something lurid.
  const pale = CatV2.lightenHex('#f3e4c8', 0.9);
  assert(/^#[0-9a-f]{6}$/.test(pale), `still a hex: ${pale}`);
  for (let i = 1; i < 7; i += 2) {
    const c = parseInt(pale.slice(i, i + 2), 16);
    assert(c >= 0xc8 && c <= 255, `channel ${c} left the range`);
  }
});

/** Every fillStyle a cat's paint sets, in order. */
function fillStyles(palette) {
  const log = [];
  CatV2.drawCat(guardCtx(log), {
    pose: 'idle',
    appearance: CatV2.appearanceFor(palette),
    facing: 'right',
    size: 120,
    phase: 0.3,
  });
  return log.filter((e) => e[0] === 'set' && e[1] === 'fillStyle').map((e) => e[2]);
}

check('every soft cat gets a belly; the tuxedo keeps its bib instead', () => {
  // Palette 0 is the tuxedo, whose white bib already is an underside.
  // Through bellyInkOf, not lightenHex: the derivation has two directions
  // now, and restating one of them here would only pin half the cats.
  for (const pal of [1, 2, 3, 4, 5]) {
    const want = CatV2.bellyInkOf(CatV2.appearanceFor(pal));
    assert(fillStyles(pal).includes(want), `palette ${pal} has no belly (${want})`);
  }
  const tuxedo = CatV2.appearanceFor(0);
  assert(!fillStyles(0).includes(CatV2.bellyInkOf(tuxedo)), 'the tuxedo drew a belly behind its bib');
  assert(fillStyles(0).includes(tuxedo.pattern.color), 'the tuxedo still draws its bib');
});

check('a belly is visible on every coat, including the white one', () => {
  // The bug this replaces was silent because the belly was still PAINTED --
  // it just matched the fur. So the property is separation, not presence.
  for (const pal of [1, 2, 3, 4, 5]) {
    const a = CatV2.appearanceFor(pal);
    const sep = Math.abs(CatV2.lstar(CatV2.bellyInkOf(a)) - CatV2.lstar(a.furBase));
    assert(sep >= CatV2.BELLY.minSeparation,
      `${a.name}'s belly is ${sep.toFixed(1)} L* from its coat, under the ${CatV2.BELLY.minSeparation} floor`);
  }
  // The white cat is the one that cannot be lightened, so she must be the
  // one going the other way. If she ever comes out paler than her coat, the
  // headroom test has stopped biting and she is flat again.
  const her = CatV2.appearanceFor(5);
  assert(CatV2.lstar(CatV2.bellyInkOf(her)) < CatV2.lstar(her.furBase),
    'the white cat is still being lightened, which is what made her flat');
  // And the four that shipped before her must be untouched: their approved
  // ink is a lighten, and this dial was added on the promise it is a no-op
  // for them. MISO is the canary, at 3.0 L* -- not storm at 9.9, which is
  // what a regex that skipped the commented palettes first suggested. The
  // usable window for minSeparation is only (1.4, 3.0].
  for (const pal of [1, 2, 3, 4]) {
    const a = CatV2.appearanceFor(pal);
    assert(CatV2.bellyInkOf(a) === CatV2.lightenHex(a.furBase, CatV2.BELLY.lighten),
      `${a.name} changed ink, and it shipped with the owner's approval`);
  }
});

check('the body outline is struck on the BODY, and lands on top of the belly', () => {
  // Two faults in one check, because they are one seam. The belly has to
  // be painted before the outline -- a stroke straddles its path, so half
  // the outline is inside the clip and a belly drawn after washes it out.
  // And moving it earlier is only safe if the body path is re-laid: save/
  // restore puts back the clip and the alpha but NOT the current path, so
  // the outline otherwise strikes the belly ellipse and looks deliberate.
  const log = [];
  const L = CatV2.catLayout('idle', 0.3);
  const a = CatV2.appearanceFor(2);
  CatV2.drawCat(guardCtx(log), {
    pose: 'idle', appearance: a, facing: 'right', size: 1, phase: 0.3,
  });
  let pen = null;
  let width = null;
  let lastEllipseRx = null;
  let outlineRx = null;
  let bellyAt = -1;
  let outlineAt = -1;
  for (let i = 0; i < log.length; i++) {
    const e = log[i];
    if (e[0] === 'set' && e[1] === 'strokeStyle') pen = e[2];
    if (e[0] === 'set' && e[1] === 'lineWidth') width = e[2];
    if (e[0] === 'set' && e[1] === 'fillStyle'
        && e[2] === CatV2.lightenHex(a.furBase, CatV2.BELLY.lighten)) bellyAt = i;
    if (e[0] === 'ellipse') lastEllipseRx = e[3];
    if (e[0] === 'stroke' && pen === a.furShade
        && Math.abs(width - CatV2.OUTLINE_W) < 1e-12 && outlineRx === null) {
      outlineRx = lastEllipseRx;
      outlineAt = i;
    }
  }
  assert(bellyAt >= 0, 'no belly was drawn at all');
  assert(outlineRx !== null, 'the body outline was never struck');
  assert(
    bellyAt < outlineAt,
    'the belly was painted after the outline, so it washes out the line it crosses',
  );
  close(outlineRx, L.body.rx, 'the outline was struck on something other than the body');
  assert(
    Math.abs(outlineRx - L.body.rx * CatV2.BELLY.rx) > 1e-9,
    'the outline was struck on the belly ellipse',
  );
});

check('the belly is derived from the body, so it follows every pose', () => {
  // No layout field, no blendLayouts entry, nothing to pop on a pose
  // change: if it were per-pose it would have to be interpolated.
  for (const pose of CatV2.POSES) {
    const L = CatV2.catLayout(pose, 0.3);
    assert(L.belly === undefined, `${pose} put a belly in the layout`);
  }
  const A = CatV2.catLayout('idle', 0);
  const B = CatV2.catLayout('pouncing', 0.9);
  assert(CatV2.blendLayouts(A, B, 0.5).belly === undefined, 'blendLayouts invented one');
});

check('the pounce is gated on how far the quarry is', () => {
  const gate = VIEW.pounceGateTiles;
  const chasing = { id: 1, pos: { x: 2, y: 2 }, last_action: { action: 'chase', target: 'element', id: 9 } };
  assert(poseFor(chasing, true, false, 0) === 'pouncing', 'on top of the quarry');
  assert(poseFor(chasing, true, false, gate) === 'pouncing', 'exactly at the gate still pounces');
  assert(poseFor(chasing, true, false, gate + 1) === 'walking', 'one tile past it walks');
  assert(poseFor(chasing, true, false, 20) === 'walking', 'and a cross-map trek walks');
  // Unknown is not the same as far: a quarry caught or expired this tick
  // keeps the pounce, which is also why v1 callers are untouched.
  assert(poseFor(chasing, true, false, null) === 'pouncing', 'an unresolved quarry keeps the pounce');
  assert(poseFor(chasing, true, false) === 'pouncing', 'v1 callers pass no distance and are untouched');
  // Order below the gate is unchanged: water still outranks walking.
  assert(poseFor(chasing, true, true, 20) === 'swim', 'a far chase on water wades');
  assert(poseFor(chasing, false, false, 20) === 'idle', 'a far chase that did not move stands');
  // The APPLIED ACTION outranks the scene now (2026-08-13), which reverses
  // what this line used to assert. Two things make that safe to reverse
  // rather than a claim being weakened to pass:
  //
  //   - the combination cannot occur. A chase ends any scene on the tick it
  //     is applied, and the engine clears ended scenes before publishing, so
  //     `chase` was served with `state: idle` on all 130 of its cat-ticks in
  //     the live capture and never once alongside a scene;
  //   - and if it somehow did, the action is what the cat DID this tick,
  //     which is the whole reason the order changed.
  //
  // What the old line was really protecting -- that a busy cat is not
  // redrawn as walking or wading -- is unaffected, and is asserted directly
  // in the water check above (`activity outranks water`).
  const busy = { ...chasing, activity: { state: 'grooming' } };
  assert(poseFor(busy, true, false, 0) === 'pouncing',
    'the applied action outranks a scene it cannot actually coexist with');
});

check('play is never gated -- it is adjacent by lawfulness', () => {
  const solo = { id: 1, pos: { x: 2, y: 2 }, last_action: { action: 'play' } };
  const withBug = { ...solo, last_action: { action: 'play', target: 'element', id: 9 } };
  for (const d of [null, 0, 1, 99]) {
    assert(poseFor(solo, true, false, d) === 'pouncing', `solo play pounces at distance ${d}`);
    assert(poseFor(withBug, true, false, d) === 'pouncing', `targeted play pounces at distance ${d}`);
  }
});

check('chaseDistanceFor reads the served state, and admits when it cannot', () => {
  const world = {
    kitties: [
      { id: 1, pos: { x: 2, y: 2 }, last_action: { action: 'chase', target: 'element', id: 9 } },
      { id: 2, pos: { x: 6, y: 5 } },
    ],
    elements: [{ id: 9, kind: 'bug', pos: { x: 5, y: 4 } }],
  };
  close(chaseDistanceFor(world.kitties[0], world), 5, 'manhattan to the bug');
  const atKitty = { ...world.kitties[0], last_action: { action: 'chase', target: 'kitty', id: 2 } };
  close(chaseDistanceFor(atKitty, world), 7, 'manhattan to the friend');
  const gone = { ...world.kitties[0], last_action: { action: 'chase', target: 'element', id: 404 } };
  assert(chaseDistanceFor(gone, world) === null, 'a vanished quarry is null, not a distance');
  assert(chaseDistanceFor(world.kitties[1], world) === null, 'a cat that is not chasing is null');
  assert(
    chaseDistanceFor({ ...world.kitties[0], last_action: { action: 'play' } }, world) === null,
    'play is not a chase',
  );
});

check('swim paddles on the tick clock moving, bobs on the breathe cycle afloat', () => {
  const p = new api.Presentation();
  p.pushState(world(1, [kitty(1, 2, 2)]), 1000);
  p.pushState(world(2, [kitty(1, 3, 2)]), 1800); // moved: paddling
  close(p.motionFor(1, 'swim', 2200).phase, 0.5, 'mid-tick paddle is mid-phase');
  const q = new api.Presentation();
  q.pushState(world(1, [kitty(1, 2, 2)]), 1000);
  q.pushState(world(2, [kitty(1, 2, 2)]), 1800); // still: floating
  const m = q.motionFor(1, 'swim', 2200);
  close(m.phase, ((2200 + 997) % api.VIEW.breathePeriodMs) / api.VIEW.breathePeriodMs, 'ambient bob');
  assert(m.eyesOverride === undefined && m.blinkLid === undefined, 'no idle twitches afloat');
});

// ---- leaving the water (owner, 2026-08-04: "coming out of the water in
// the grass") ----

check('the wading kitty carries no splash droplet', () => {
  // A ~2px smudge at every size this world draws at, so it read as
  // clutter (owner, 2026-08-04). Being in water is the renderer's to
  // say -- the ripple and the lost shadow -- and that scales with tile.
  assert(CatV2.catLayout('swim', 0.25).droplet === false, 'swim: no droplet');
  assert(CatV2.catLayout('walking', 0.25).droplet === false, 'walking: none either');
  // Drinking keeps its own lap of water; that one is not about wading.
  assert(CatV2.catLayout('drinking', 0.25).droplet === true, 'drinking keeps its lap');
});

// ---- wetness: a fact about the tile, not the pose ----

check('wetness is independent of the pose the cat happens to be in', () => {
  const p = new api.Presentation();
  const drinkingInAPond = { id: 1, pos: { x: 2, y: 2 }, activity: { state: 'drinking' } };
  // poseFor keeps the activity -- that is its documented rule, unchanged.
  assert(poseFor(drinkingInAPond, false, true) === 'drinking', 'the activity still wins the pose');
  // ...and the cat is nonetheless soaking wet, which is the whole point.
  close(p.wetFor(1, true, 1000), 1, 'a drinking cat on water still reads as wet');
});

check('first sight settles rather than fading in', () => {
  const p = new api.Presentation();
  close(p.wetFor(1, true, 1000), 1, 'seen already in the water: fully wet at once');
  const q = new api.Presentation();
  close(q.wetFor(2, false, 1000), 0, 'seen on land: fully dry at once');
});

check('a coat wets fast and dries slow -- the two clocks differ on purpose', () => {
  // Asymmetric since 2026-08-10. A cat is wet the INSTANT it is in water
  // and dries over furDryMs, which is ~11x longer. Before, one clock ran
  // both ways, and it had to be short because the geometry rode it too --
  // now that geometry is spatial, drying is free to take as long as it
  // really does.
  const wetMs = api.VIEW.wetFadeMs;
  const dryMs = api.VIEW.furDryMs;
  assert(dryMs > wetMs * 4, `drying (${dryMs}ms) must be much slower than wetting (${wetMs}ms)`);

  const p = new api.Presentation();
  p.wetFor(1, true, 1000); // settled, in the water
  close(p.wetFor(1, false, 1000), 1, 'still wet at the moment it steps out');
  close(p.wetFor(1, false, 1000 + dryMs / 2), 0.5, 'half dry a half-DRY later');
  close(p.wetFor(1, false, 1000 + dryMs), 0, 'dry when the dry ends');
  close(p.wetFor(1, false, 1000 + dryMs * 3), 0, 'and stays dry');

  // The other direction still runs on the fast clock. Asserted as a pair
  // with the above, because a single clock would satisfy either one alone.
  const q = new api.Presentation();
  q.wetFor(2, false, 1000); // settled, on land
  q.wetFor(2, true, 1000); // steps in: the wetting starts here
  close(q.wetFor(2, true, 1000 + wetMs / 2), 0.5, 'half wet a half-WET later');
  close(q.wetFor(2, true, 1000 + wetMs), 1, 'soaked when the fade ends');
  // ...and at the drying clock's half-point it is long since soaked, which
  // is what proves wetting did not quietly inherit furDryMs.
  const r = new api.Presentation();
  r.wetFor(3, false, 1000);
  r.wetFor(3, true, 1000);
  close(r.wetFor(3, true, 1000 + dryMs / 2), 1, 'wetting must not run on the drying clock');
});

check('darting in and out resumes from the part-fade, never snapping', () => {
  const p = new api.Presentation();
  const dryMs = api.VIEW.furDryMs;
  const wetMs = api.VIEW.wetFadeMs;
  p.wetFor(1, true, 1000); // settled, in the water
  p.wetFor(1, false, 1000); // steps out: the dry starts here
  close(p.wetFor(1, false, 1000 + dryMs / 2), 0.5, 'half dry on the way out');
  close(p.wetFor(1, true, 1000 + dryMs / 2), 0.5, 'turning back does not snap to wet');
  // Re-wetting from 0.5 covers the remaining half on the FAST clock.
  close(p.wetFor(1, true, 1000 + dryMs / 2 + wetMs / 2), 0.75, 'it re-wets from where it had got to');
});

check('still frames carry wetness at full strength', () => {
  const p = new api.Presentation();
  p.pushState(world(1, [kitty(1, 2, 2)]), 1000);
  const still = p.viewAt(1100, true);
  close(still.wetFor(1, true), 1, 'state, not motion: a still frame shows it');
  close(still.wetFor(1, false), 0, 'and shows dry as dry');
});

check('a discontinuity clears wetness with the rest of the memory', () => {
  const p = new api.Presentation();
  p.pushState(world(1, [kitty(1, 2, 2)]), 1000);
  p.pushState(world(2, [kitty(1, 2, 2)]), 1800);
  p.wetFor(1, true, 1900);
  assert(p.wetness.size === 1, 'wetness recorded');
  p.pushState(world(9, [kitty(1, 2, 2)]), 2600); // tick jump: a different moment
  assert(p.wetness.size === 0, 'wetness cleared');
});

// ---- occupiedTiles: what the ground cover must keep off ----

// The rule this pins is a contract, not a preference: cover is scenery, so
// it may only avoid things that will still be there next tick. It used to
// avoid every served element, and bugs, greebles, chow and sunbeams all move
// or expire -- so a critter walking onto a tree's tile deleted the tree and
// walking off grew it back. Nothing caught that, because the cover test
// exercises `bushesFor` with a hand-built set and never asked what builds it.
check('occupiedTiles keeps cover off water, and off nothing else', () => {
  // `this` is unused, so the method can be exercised without a canvas.
  const occupied = (elements) =>
    WorldRenderer.prototype.occupiedTiles.call(null, { elements });
  const at = (kind, x, y) => ({ kind, pos: { x, y } });

  const water = occupied([at('water', 3, 4)]);
  assert(water.has('3,4'), 'water is avoided');

  for (const kind of ['bug', 'greeble', 'chow', 'sunbeam']) {
    const set = occupied([at(kind, 7, 8)]);
    assert(
      !set.has('7,8'),
      `${kind} does not suppress cover -- it moves or expires, and cover that ` +
        'follows it blinks',
    );
  }

  // The mixed case is the real world: a pond keeps its tile, the critter
  // wandering past it does not take one with it.
  const mixed = occupied([at('water', 1, 1), at('bug', 2, 2), at('chow', 3, 3)]);
  assert(mixed.size === 1 && mixed.has('1,1'), `only water: got ${[...mixed].join(' ')}`);
});

// ---- the card portraits: onFrame, and the always-idle rule ----

// A stand-in for the pair anim.redraw needs: something to draw with, and a
// world to draw. The portraits ride the same call, so this is all it takes.
function riggedAnim() {
  const a = Object.create(api.anim);
  a.presentation = new api.Presentation();
  a.presentation.curr = world(1, [kitty(1, 2, 2)]);
  a.renderer = { draw() {} };
  a.rafId = 0;
  return a;
}

check('a still frame hands the portraits a still view', () => {
  const a = riggedAnim();
  const seen = [];
  a.onFrame = (w, view) => seen.push({ w, view });
  a.redraw();
  assert(seen.length === 1, `onFrame ran ${seen.length} times, want 1`);
  assert(seen[0].w === a.presentation.curr, 'onFrame gets the drawn world');
  assert(seen[0].view.still === true, 'a still frame must say so');
  // This is what keeps reduced motion working without app.js knowing the
  // rule: phase 0 and nothing else, so a portrait holds its pose.
  const m = seen[0].view.motionFor(1, 'idle');
  assert(m.phase === 0, `still motion phase ${m.phase}, want 0`);
  assert(m.blinkLid === undefined, 'a still frame must not blink');
  assert(m.earsBack === undefined, 'a still frame must not twitch');
});

check('no onFrame hook is not an error', () => {
  const a = riggedAnim();
  a.onFrame = null;
  a.redraw(); // must not throw
});

check('the portrait pose is idle because an action pose has no idle motion', () => {
  // The card asks for 'idle' whatever the cat is really doing (owner,
  // 2026-08-07). This is the reason: motionFor returns early for action
  // poses, so a portrait that mirrored the world would go still exactly
  // when the cat is busy -- which is most of the time.
  const p = new api.Presentation();
  const slot = slotOf(api, 1, 'blink');
  assert(slot, 'no blink slot found for kitty 1');
  const mid = slot.at(api.VIEW.slowBlinkDownMs + api.VIEW.slowBlinkHoldMs / 2);

  const asIdle = p.motionFor(1, 'idle', mid);
  assert(asIdle.blinkLid > 0.9, `idle mid-blink lid ${asIdle.blinkLid}, want ~1`);

  for (const pose of ['pouncing', 'eating', 'drinking', 'grooming', 'walking']) {
    const acting = p.motionFor(1, pose, mid);
    assert(
      acting.blinkLid === undefined,
      `${pose} would have suppressed the portrait's blink`,
    );
  }
});

// ---- water occlusion: where the surface cuts the cat ----

const GROUND = 0.88;

check('a dry cat is never clipped, in any pose', () => {
  for (const pose of ['idle', 'walking', 'grooming', 'drinking', 'loaf', 'sleep-curl']) {
    assert(waterlineFor(pose, 0) === null, `${pose} dry`);
    assert(waterlineFor(pose, 0.005) === null, `${pose} barely damp`);
  }
});

check('the world owns the water level: EVERY pose meets one surface', () => {
  // The reverse of what this file asserted until 2026-08-10, and the
  // reversal is the point (handoff invariant 5). `swim` used to be exempt
  // from the clip because it drew itself sunk -- so the same pond read as
  // two depths, and a cat crossing into deep water changed level in one
  // step on the frame the pose flipped. SWIM was raised to sit at the land
  // poses' height and the CLIP now does the submerging.
  //
  // Note the old check passed for a reason that had nothing to do with
  // swimming: it called waterlineFor('swim', wet), and under the new
  // signature the string lands in `submersion`, where !('swim' > 0.01) is
  // true and the answer is null for every pose spelled any way at all.
  const poses = ['swim', 'grooming', 'drinking', 'eating', 'loaf', 'sleep-curl', 'idle', 'pouncing'];
  for (const pose of poses) {
    close(surfaceForPose(pose), api.VIEW.waterline, `${pose} disagrees about the surface`);
    close(waterlineFor(1, surfaceForPose(pose)), api.VIEW.waterline, `${pose} fully submerged`);
  }
  // ...and no pose may smuggle a level in through a dials object either.
  const shallow = { waterline: 0.8 };
  for (const pose of poses) {
    close(surfaceForPose(pose, shallow), 0.8, `${pose} ignored a re-dialled surface`);
  }
});

check('the surface rises from the ground line, monotonically', () => {
  // Derived from VIEW, never a copy of it -- a re-dialled waterline must
  // not need this test edited.
  // Integer steps, and an epsilon on the endpoint: 0.88 - 1 * (0.88 - 0.72)
  // is 0.7199999999999999 in binary floating point, so an exact bound here
  // would fail on arithmetic rather than on behaviour.
  const EPS = 1e-9;
  const surface = surfaceForPose('grooming');
  let previous = GROUND + 1;
  for (let i = 1; i <= 50; i += 1) {
    const submersion = i / 50;
    const cut = waterlineFor(submersion, surface);
    assert(cut < previous, `not monotonic at submersion ${submersion.toFixed(2)}`);
    assert(cut <= GROUND + EPS, `above the ground line at ${submersion.toFixed(2)}: ${cut}`);
    assert(cut >= api.VIEW.waterline - EPS, `past the waterline at ${submersion.toFixed(2)}: ${cut}`);
    previous = cut;
  }
  close(waterlineFor(1, surface), api.VIEW.waterline, 'fully submerged sits exactly on the dial');
  // Half submerged is half way: the geometry does no shaping of its own,
  // because the shoreline's smoothness now comes from POSITION.
  close(waterlineFor(0.5, surface), GROUND - 0.5 * (GROUND - surface), 'halfway is halfway');
});

check('the dial is honoured, not hardcoded', () => {
  close(waterlineFor(1, surfaceForPose('grooming', { waterline: 0.8 })), 0.8, 'shallow dial');
  close(waterlineFor(1, surfaceForPose('grooming', { waterline: 0.6 })), 0.6, 'deep dial');
});

// ---- submersion is a PLACE (2026-08-10) ----
//
// The bug this replaced: every water cue rode a 260ms ease toward "is the
// nearest tile water". A timer cannot know where the shoreline is, so how
// far past the shore a cat carried its water depended on how FAST it was
// going -- measured by the handoff at x~9.78 at one tile per tick and
// x~10.08 at two, over ground with no water under it.

/** A two-tile pond at (5,5)-(6,5), everything else dry. */
const pondWorld = () => ({
  tick: 1,
  kitties: [],
  elements: [
    { id: 1, kind: 'water', pos: { x: 5, y: 5 } },
    { id: 2, kind: 'water', pos: { x: 6, y: 5 } },
    { id: 3, kind: 'chow', pos: { x: 9, y: 9 } },
  ],
});

check('submersion is EXACTLY zero on dry ground, at any speed', () => {
  const w = pondWorld();
  // Sampled at frame resolution, not per tile. Per-tile sampling is
  // precisely what hid the old bug: it only ever asked at integers, where
  // even the timer happened to be right.
  for (let x = 7; x <= 12; x += 0.01) {
    const s = submersionFor({ x, y: 5 }, w, null);
    assert(s === 0, `wet on dry ground at x=${x.toFixed(2)}: ${s}`);
  }
  // ...and off the pond's axis too, including the diagonal neighbours the
  // bilinear sample reaches that a nearest-tile reading never did.
  for (let y = 7; y <= 9; y += 0.25) {
    assert(submersionFor({ x: 5, y }, w, null) === 0, `wet at y=${y}`);
  }
  // Speed cannot enter into it: this is a pure function of position, so
  // the same place answers the same number however the cat got there.
  assert(
    submersionFor({ x: 8, y: 5 }, w, null) === submersionFor({ x: 8, y: 5 }, w, null),
    'not a pure function of position',
  );
});

check('submersion is exactly 1 in the pond, and rises smoothly across the shore', () => {
  const w = pondWorld();
  close(submersionFor({ x: 5, y: 5 }, w, null), 1, 'the pond interior');
  close(submersionFor({ x: 6, y: 5 }, w, null), 1, 'the other water tile');
  close(submersionFor({ x: 6.5, y: 5 }, w, null), 0.5, 'halfway to the shore');
  // Monotonic on the way out, with no step: the smoothness comes from
  // MOVING, which is why no fade is needed to avoid a pop.
  let previous = Infinity;
  for (let x = 6; x <= 7; x += 0.02) {
    const s = submersionFor({ x, y: 5 }, w, null);
    assert(s <= previous + 1e-12, `not monotonic leaving the pond at x=${x.toFixed(2)}`);
    assert(Math.abs(s - previous) < 0.05 || previous === Infinity, `a step at x=${x.toFixed(2)}`);
    previous = s;
  }
  close(previous, 0, 'clear of the water by the next tile');
  // A world with no water at all short-circuits rather than sampling.
  assert(submersionFor({ x: 5, y: 5 }, { elements: [] }, null) === 0, 'dry world');
});

check('a pond fading in raises the water at its own alpha', () => {
  const w = pondWorld();
  const half = { elementAlphaFor: (el) => (el.kind === 'water' ? 0.5 : 1) };
  close(submersionFor({ x: 5, y: 5 }, w, half), 0.5, 'a half-arrived pond is half deep');
  const gone = { elementAlphaFor: () => 0 };
  assert(submersionFor({ x: 5, y: 5 }, w, gone) === 0, 'a fully faded pond is not water');
});

check('geometry reads the PLACE, colour reads the MEMORY -- never the reverse', () => {
  // The invariant the whole split exists for. A cat that has just left the
  // pond is still visibly damp AND completely clear of water geometry;
  // under the old single signal those were the same number, which is how
  // water came to be drawn on grass.
  const w = pondWorld();
  const p = new api.Presentation();
  p.wetFor(1, true, 1000); // soaked, standing in it
  const stillDamp = p.wetFor(1, false, 1000 + api.VIEW.furDryMs / 4);
  assert(stillDamp > 0.5, `a cat should still be damp a moment after leaving: ${stillDamp}`);
  assert(submersionFor({ x: 8, y: 5 }, w, null) === 0, 'but it is not in any water');
  assert(waterlineFor(0, surfaceForPose('idle')) === null, 'so nothing may clip it');

  // And the wiring: the draw path must not hand `wetFor`'s answer to any
  // geometry. Checked in the source because the failure is a substitution
  // that every geometry test would still pass -- the shapes stay valid,
  // they just outlive the pond.
  const geometry = [
    ['shadowAlpha', /const shadowAlpha = 1 - submersion;/],
    ['the waterline clip', /waterlineFor\(submersion, surfaceForPose\(pose\)\)/],
    ['the meniscus', /drawWaterline\(cx, y, cut, submersion, view\)/],
  ];
  for (const [what, pattern] of geometry) {
    assert(pattern.test(renderSrc), `${what} no longer reads submersion`);
  }
  assert(
    /const furWet = /.test(renderSrc) && !/const wet = v2Motion/.test(renderSrc),
    'the coat signal must be named furWet, so a stray `wet` cannot be geometry by accident',
  );
});

check('the meniscus takes its colour from the theme, not from a mix toward white', () => {
  // The handoff drew it as lightenHex(pondWater, 0.5). That is the daylight
  // assumption the pond restyle (#177) exists to retire: a constant mix
  // toward white is a statement about how much sun there is.
  //
  // Measured in CIE L*, the two agree where it does not matter and part
  // where it does -- day 94.1 vs 97.8, dusk 87.5 vs 93.2, dawn 83.3 vs
  // 76.6, and NIGHT 66.7 vs 33.2. That last one is a near-daylight line
  // drawn across a cat standing in a pond painted at L* 33.
  //
  // Guarded here rather than in test-meadow because the palette is not
  // what would regress: the per-theme entries are checked there and would
  // stay perfectly correct while render.js quietly stopped asking for them.
  assert(
    /ctx\.strokeStyle = MEADOW\.pondMeniscus/.test(renderSrc),
    'the meniscus no longer takes the per-theme surface colour',
  );
  assert(
    !/lightenHex\(MEADOW\.pondWater/.test(renderSrc),
    'the meniscus is back on a fixed mix toward white -- night will read as daylight',
  );
});

check('the far pair shows on the two poses that need it, and nowhere else', () => {
  const FAR = CatV2.FAR_LEGS;
  assert(FAR && typeof FAR.pounce === 'number', 'FAR_LEGS.pounce missing');
  assert(FAR.pounce < 0 && FAR.stretch < 0, 'the far pair trails the near one, so both are negative');
  // Every other pose leaves the far pair flush at GAIT.spread, where it
  // hides exactly behind the near one. Measured off the drawn legs rather
  // than the dial: `far` legs are drawn first, so a pose that separates
  // them puts a shaded leg at a different x from every near leg.
  const spread = CatV2.GAIT.spread;
  close(spread, 0, 'GAIT.spread is what keeps the far pair hidden for everything else');
  // The stretch scales its offset by its own push, so it is flush at both
  // ends of the pose and widest in the middle -- the depth cue arrives
  // with the reach.
  const legsAt = (pose, phase) => CatV2.catLayout(pose, phase, {}).legs.filter((l) => l.far);
  const atRest = legsAt('stretch', 0);
  const atFull = legsAt('stretch', 0.5);
  assert(atRest.length === atFull.length && atRest.length > 0, 'the stretch lost its far pair');
  const spreadAt = (legs, ref) => Math.abs(legs[0].x - ref[0].x);
  const near = (pose, phase) => CatV2.catLayout(pose, phase, {}).legs.filter((l) => !l.far);
  assert(
    spreadAt(atRest, near('stretch', 0)) < 1e-9,
    'the stretch shows its far pair before it has begun to reach',
  );
  assert(
    spreadAt(atFull, near('stretch', 0.5)) > 0.01,
    'the stretch never separates its far pair at full extension',
  );
});

// --------------------------------------------------------------- the walk
//
// The walk this replaced ran both feet along one shared sine at a fixed y,
// which gave it no stance at all: for half of every step a planted foot
// travelled FORWARD while the cat was already moving forward. Feet
// outrunning the cat is what reads as skating. These checks pin the
// properties that fix is made of, so a re-dial in the lab cannot quietly
// undo it.

const { catLayout, GAIT, MAX_LIFT, gaitStep, plantedReach } = CatV2;
const GROUND_Y = 0.88;
/** `phase` is progress across one TILE; the gait runs GAIT.cycles steps
 * inside it, so a cycle-space position converts back like this. */
const atCycle = (u) => catLayout('walking', u / GAIT.cycles);

/** `close` is 1e-12; wrap comparisons ride a finite phase step. */
function nearly(a, b, tol, msg) {
  assert(Math.abs(a - b) <= tol, `${msg}: ${a} != ${b}`);
}

check('a planted foot only ever travels backward', () => {
  const N = 720;
  let previous = null;
  let samples = 0;
  for (let i = 0; i <= N; i += 1) {
    const u = i / N;
    if (u >= GAIT.duty) break;
    const g = gaitStep(u, GAIT.duty);
    assert(g.lift === 0, `a planted foot is off the ground at u ${u.toFixed(3)}`);
    if (previous !== null) {
      assert(g.x < previous, `stance foot moved forward at u ${u.toFixed(3)}`);
      samples += 1;
    }
    previous = g.x;
  }
  assert(samples > 100, `only ${samples} stance samples -- is duty sane?`);
});

check('a planted foot drifts smoothly, never scrubs', () => {
  // REPLACES an equality check on 2*reach == duty/cycles. That equality is
  // correct physics -- it is the reach at which a foot holds still against
  // the ground, and it does not depend on leg count, since each planted
  // foot must match ground speed on its own. But it was the wrong pass/fail:
  // it conflated "planted" with "does not skate", and those are different
  // questions.
  //
  // What read as skating in the walk this replaced was DIRECTION REVERSAL
  // and speed mismatch -- feet moving forward through half of every stance
  // against a body already moving forward, compounded by posFor's easing
  // swinging body speed from 0 to 3x inside one tile. A foot that drifts
  // steadily, always the same way, at a fraction of the body's pace is a
  // far gentler artifact.
  //
  // Owner call (2026-08-08) at reach 0.085: "both look pretty natural,
  // 0.085 makes the cat look more leisurely and keeps the legs from
  // protruding too much." So a short stride is a deliberate choice, and
  // these are the properties it still has to have.
  const FLOOR = 0.4; // the foot must do at least this share of the ground's work
  const N = 400;
  const S = 1 / GAIT.cycles;
  // Driven through catLayout, NOT through a copy of its arithmetic. The
  // first version of this check recomputed the stance formula inline, so
  // it passed no matter what gaitStep did -- a mutation to a cosine stance
  // left it green. A test that cannot fail is not a test.
  //
  // `phase` is tiles covered, so the body's world position IS the phase,
  // and leg 2 (the near hind) rides the cycle directly: its stance runs
  // u in [0, duty), i.e. phase in [0, duty/cycles).
  const at = (i) => {
    const u = (GAIT.duty * i) / N;
    const phase = u / GAIT.cycles;
    const leg = catLayout('walking', phase).legs[2];
    assert(leg.bottom >= GROUND_Y - 1e-9, `leg 2 is not planted at u ${u.toFixed(3)}`);
    return phase + leg.x; // world-space foot position, in tiles
  };
  let first = null;
  for (let i = 1; i <= N; i += 1) {
    const v = (at(i) - at(i - 1)) / S;
    assert(v >= 0, `the foot reversed mid-stance at ${i}/${N}`);
    if (first === null) first = v;
    // Constant rate: a foot that speeds up and slows down inside its own
    // stance is the scrub, whatever its average comes to.
    nearly(v, first, 1e-6, `the drift rate changed at ${i}/${N}`);
  }
  const share = (2 * GAIT.reach) / (GAIT.duty * S);
  assert(
    share >= FLOOR,
    `the foot does only ${(100 * share).toFixed(0)}% of the ground's work ` +
      `(floor ${100 * FLOOR}%); planted would be reach ${plantedReach().toFixed(3)}`,
  );
});

check('the step count may be fractional', () => {
  // RETIRED and replaced. The old rule was that cycles had to be a whole
  // number, because `phase` was tick progress and returned to 0 every
  // tile, so a part-finished stride tore at the boundary. `phase` is now
  // tiles covered (Presentation.strideFor), which is continuous, and
  // fractional cadence is the point -- 1 step per tile reads too slow and
  // 2 too fast. What is still required is that it be a real rate.
  assert(GAIT.cycles > 0, `GAIT.cycles ${GAIT.cycles} is not a rate`);
  assert(Number.isFinite(GAIT.cycles), 'GAIT.cycles is not finite');
});

check('every foot clears the ground at mid-swing', () => {
  const mid = GAIT.duty + (1 - GAIT.duty) / 2;
  close(gaitStep(mid, GAIT.duty).lift, 1, 'peak lift is a full unit at mid-swing');
  // Legs are [right hind, right fore, left hind, left fore]; the near fore
  // is the one that rides `cycle - 0.25`, so mid-swing is measured there.
  const front = atCycle(mid + 0.25).legs[3];
  assert(front.bottom < GROUND_Y, 'the front foot never leaves the ground');
  close(GROUND_Y - front.bottom, GAIT.lift, 'and it clears by exactly the dial');
});

check('the paw arc can never invert', () => {
  // drawLegs strikes the paw as a half-disc of radius w/2 at `bottom`, so
  // a lift past (height - w/2) puts the arc above the leg's own top and
  // the path turns inside out. The mock ctx cannot catch it -- an
  // inverted path is made of perfectly finite numbers.
  assert(GAIT.lift <= MAX_LIFT, `baked lift ${GAIT.lift} exceeds the ${MAX_LIFT} ceiling`);
  for (let i = 0; i < 360; i += 1) {
    const phase = i / 360;
    for (const leg of catLayout('walking', phase).legs) {
      assert(
        leg.bottom - leg.w / 2 > leg.top,
        `leg inverted at phase ${phase.toFixed(3)}: bottom ${leg.bottom}, top ${leg.top}`,
      );
    }
  }
});

check('a walk always has a foot down', () => {
  // The boundary is 0.5, not above it. Two legs half a cycle apart means
  // that at duty 0.5 exactly one foot is down at all times -- no double
  // support, but no flight phase either. This first read `> 0.5`, which
  // is the quadruple-support convention for a four-legged walk and the
  // wrong rule for two drawn legs; verified against the per-phase count
  // below, which is the real check.
  assert(GAIT.duty >= 0.5, `duty ${GAIT.duty} leaves a flight phase`);
  for (let i = 0; i < 360; i += 1) {
    const phase = i / 360;
    const down = catLayout('walking', phase).legs.filter(
      (leg) => leg.bottom >= GROUND_Y - 1e-9,
    ).length;
    assert(down >= 1, `both feet airborne at phase ${phase.toFixed(3)}`);
  }
});

check('every limb hangs from under the cat', () => {
  // RETIRED and replaced, not loosened. The old rule was that a FOOT could
  // not pass the body's silhouette -- true only while a leg was a free
  // peg with nothing drawn between its top and the body. Legs now pivot
  // from inside the body, so a forepaw reaching out under the chin is
  // correct anatomy (the owner's brief calls for exactly that) and the
  // limb is visibly attached. What still has to hold is that the PIVOT
  // stays under the cat: a limb hanging off open air is the real defect.
  for (let i = 0; i < 360; i += 1) {
    const phase = i / 360;
    const { body, legs } = catLayout('walking', phase);
    for (const leg of legs) {
      const hx = leg.hx ?? leg.x;
      assert(
        hx >= body.cx - body.rx && hx <= body.cx + body.rx,
        `pivot at ${hx.toFixed(3)} is outside the body ` +
          `(${(body.cx - body.rx).toFixed(2)}..${(body.cx + body.rx).toFixed(2)}) ` +
          `at phase ${phase.toFixed(3)}`,
      );
    }
  }
});

check('the rear leg stays behind the front one', () => {
  // blendLayouts pairs legs BY INDEX, so a reach big enough to cross them
  // would cross a cat's legs on every blend out of the walk.
  for (let i = 0; i < 360; i += 1) {
    const phase = i / 360;
    const { legs } = catLayout('walking', phase);
    assert(legs[0].x < legs[1].x, `legs crossed at phase ${phase.toFixed(3)}`);
  }
});

check('the whole cycle draws, and blends out of it at every phase', () => {
  // The guarding ctx rejects any non-finite draw argument, so this sweeps
  // the new stance/swing maths for a phase that produces one -- and does
  // the same through blendLayouts, which now carries a moving `bottom`
  // where the old walk had a constant.
  const appearance = CatV2.appearanceFor(3);
  const base = { appearance, facing: 'right', size: 60, x: 0, y: 0 };
  for (let i = 0; i <= 120; i += 1) {
    const phase = i / 120;
    CatV2.drawCat(guardCtx(), { ...base, pose: 'walking', phase });
    for (const to of ['idle', 'loaf', 'grooming', 'swim']) {
      for (const t of [0.25, 0.5, 0.75]) {
        CatV2.drawCatTween(guardCtx(), {
          ...base, from: 'walking', to, t, phaseFrom: phase, phaseTo: 0.4,
        });
      }
    }
  }
});

check('the walk is continuous everywhere, at any cadence', () => {
  // Replaces the old tick-boundary wrap check, which asserted that phase 1
  // matched phase 0. That was the right property while phase meant
  // "progress across one tile"; it is meaningless now that phase is
  // distance and cycles may be fractional. The stronger property, and the
  // one that actually matters, is that NO phase is a seam -- swept here
  // across three cadences including a fractional one.
  const was = GAIT.cycles;
  try {
    for (const cadence of [1, 1.5, 2]) {
      GAIT.cycles = cadence;
      const N = 4000;
      let last = catLayout('walking', 0);
      for (let i = 1; i <= N; i += 1) {
        const now = catLayout('walking', (3 * i) / N); // three tiles of walking
        for (let j = 0; j < now.legs.length; j += 1) {
          nearly(now.legs[j].x, last.legs[j].x, 0.01, `cadence ${cadence}: leg ${j} x jumped`);
          nearly(now.legs[j].bottom, last.legs[j].bottom, 0.01, `cadence ${cadence}: leg ${j} foot jumped`);
        }
        nearly(now.body.cy, last.body.cy, 0.01, `cadence ${cadence}: the body jumped`);
        last = now;
      }
    }
  } finally {
    GAIT.cycles = was;
  }
});

check('the body dips once per beat, lowest where bobPhase says', () => {
  // GAIT.beats dips per cycle. At 4 that is one per footfall, which is the
  // only setting where bobPhase has a landmark to line up against.
  const cyAt = (u) => atCycle(u).body.cy;
  let lowest = -Infinity;
  let at = 0;
  for (let i = 0; i < 2000; i += 1) {
    const u = i / (2000 * GAIT.beats) + GAIT.bobPhase - 0.5 / GAIT.beats; // one beat
    if (cyAt(u) > lowest) {
      lowest = cyAt(u);
      at = u;
    }
  }
  nearly(at, GAIT.bobPhase, 1e-3, 'the dip does not sit where bobPhase says');
  close(GAIT.beats, Math.round(GAIT.beats), 'beats must be whole or dips drift off the feet');
  nearly(cyAt(GAIT.bobPhase), cyAt(GAIT.bobPhase + 1 / GAIT.beats), 1e-9, 'consecutive dips differ');
  close(lowest - catLayout('idle', 0).body.cy, GAIT.bob, 'dip depth is the dial');
});

// ---- strideFor: the gait's distance clock ----

check('the stride clock measures ground, not time', () => {
  const p = new api.Presentation();
  p.tickMs = 800;
  // Three ticks of walking east, then one standing still.
  const at = (t, x) => world(t, [kitty(1, x, 5)]);
  p.pushState(at(1, 0), 0);
  p.pushState(at(2, 1), 800);
  close(p.strideFor(1, 800), 0, 'a fresh pair starts the tick at zero distance');
  // Mid-tick the cat is eased, so the stride must be eased with it.
  const mid = p.strideFor(1, 1200);
  assert(mid > 0 && mid < 1, `mid-tick stride ${mid} is inside the tile`);
  // This first step is taken from rest, so it rides startEase, not linear.
  close(mid, 0.5 * 0.5 * (2 - 0.5), 'a step from rest eases in');
  close(p.strideFor(1, 1600), 1, 'a finished tick is exactly one tile');
  p.pushState(at(3, 2), 1600);
  // Second step in a row: the cat is already walking, so it runs linear
  // and does not brake into the tile boundary and start again.
  close(p.strideFor(1, 1600 + 400), 1.5, 'a continuing step is linear');
  close(p.strideFor(1, 2400), 2, 'two tiles after two moves');
  // Standing still must not advance the gait, however long it stands.
  p.pushState(at(4, 2), 2400);
  close(p.strideFor(1, 3200), 2, 'a stationary cat does not step');
  p.pushState(at(5, 2), 3200);
  close(p.strideFor(1, 4000), 2, 'still does not step');
});

check('the stride clock never runs backward', () => {
  const p = new api.Presentation();
  p.tickMs = 800;
  let last = -1;
  for (let t = 1; t <= 12; t += 1) {
    p.pushState(world(t, [kitty(1, t - 1, 5)]), (t - 1) * 800);
    for (let ms = 0; ms <= 800; ms += 50) {
      const d = p.strideFor(1, (t - 1) * 800 + ms);
      assert(d >= last - 1e-12, `stride went backward at tick ${t}+${ms}ms: ${d} < ${last}`);
      last = d;
    }
  }
});

check('a discontinuity resets the odometer with the rest of the memory', () => {
  const p = new api.Presentation();
  p.tickMs = 800;
  p.pushState(world(1, [kitty(1, 0, 5)]), 0);
  p.pushState(world(2, [kitty(1, 1, 5)]), 800);
  p.pushState(world(3, [kitty(1, 2, 5)]), 1600);
  assert(p.strideFor(1, 2400) > 1, 'distance accumulated');
  p.pushState(world(40, [kitty(1, 9, 9)]), 2400); // a different moment entirely
  assert(p.discontinuous, 'that is a discontinuity');
  close(p.strideFor(1, 2400), 0, 'the odometer starts clean, like facings and worn paths');
});

// ---- PROPORTION: the shape dials (the body:head work) ----

const PROP_SHIPPED = { ...CatV2.PROPORTION };
/** Run `fn` with the shape dials moved, and always put them back. */
function reshaped(over, fn) {
  Object.assign(CatV2.PROPORTION, over);
  try {
    return fn();
  } finally {
    Object.assign(CatV2.PROPORTION, PROP_SHIPPED);
  }
}
/** The body ellipse's lower edge directly above `x` -- the belly a leg hangs below. */
const bellyAt = (x, b) => {
  const t = (x - b.cx) / b.rx;
  return Math.abs(t) >= 1 ? b.cy - b.ry : b.cy + b.ry * Math.sqrt(1 - t * t);
};
const legAt = (over, x = CatV2.GAIT.hip) =>
  0.88 - bellyAt(x, reshaped(over, () => CatV2.catLayout('walking', 0)).body);

/** The v1 body every multiplier is measured against. */
const IDENT = { bodyW: 1, bodyH: 1, headR: 1, headY: 0, headX: 0 };

check('the shipped shape is the one the owner dialled', () => {
  const p = CatV2.PROPORTION;
  // Pinned, not asserted-as-identity: these were chosen in the lab on
  // 2026-08-08. The check exists so the next edit has to be deliberate too.
  close(p.bodyW, 1.1, 'bodyW drifted');
  close(p.bodyH, 1.05, 'bodyH drifted');
  close(p.headR, 1, 'headR drifted');
  close(p.headY, 0.01, 'headY drifted');
  close(p.headX, 0.02, 'headX drifted');
  // Aspect moves only by the RATIO of the two scales -- dialling both by
  // the same factor is a bigger body, not a rounder one. Worth asserting
  // because it is the thing an eye cannot check: 1.1/1.088 looks like two
  // different numbers and is very nearly none.
  const shipped = CatV2.catLayout('walking', 0);
  const v1 = reshaped(IDENT, () => CatV2.catLayout('walking', 0));
  close(
    shipped.body.rx / shipped.body.ry,
    (v1.body.rx / v1.body.ry) * (p.bodyW / p.bodyH),
    'the aspect moved by something other than bodyW/bodyH',
  );
});

check('the head slides along the body without reshaping it', () => {
  // Both ends measured from the v1 body: a check that reads the shipped
  // dials as its own baseline stops testing the mechanism the moment
  // someone pastes a new value into them.
  const base = reshaped(IDENT, () => CatV2.catLayout('walking', 0));
  const fwd = reshaped({ ...IDENT, headX: 0.05 }, () => CatV2.catLayout('walking', 0));
  close(fwd.head.cx - base.head.cx, 0.05, 'the head did not move forward');
  close(fwd.head.cy, base.head.cy, 'moving the head forward moved it vertically');
  close(fwd.body.cx, base.body.cx, 'the body followed the head');
  close(fwd.head.r, base.head.r, 'the head resized while sliding');
});

check('reshaping holds the belly floor in every pose', () => {
  for (const pose of CatV2.POSES) {
    const base = CatV2.catLayout(pose, 0.4);
    const shaped = reshaped({ bodyH: 1.2, bodyW: 1.1 }, () => CatV2.catLayout(pose, 0.4));
    close(
      shaped.body.cy + shaped.body.ry,
      base.body.cy + base.body.ry,
      `${pose}: the underside moved, which is a stand-height change wearing a proportion costume`,
    );
  }
});

check('a grounded foot stays on the ground; the leap’s feet ride the body', () => {
  const walk = CatV2.catLayout('walking', 0.4);
  const walkShaped = reshaped({ bodyH: 1.2 }, () => CatV2.catLayout('walking', 0.4));
  walk.legs.forEach((leg, i) =>
    close(walkShaped.legs[i].bottom, leg.bottom, `walking foot ${i} left the ground`),
  );
  assert(walkShaped.legs[0].top < walk.legs[0].top, 'the pivot must ride the body up with it');

  // Derived from the dials rather than hardcoded: 0.8 used to be airborne and
  // is now mid-RECOVERY, feet back on the ground, so a re-dial must not be
  // able to silently point this at the wrong phase again.
  const P = CatV2.POUNCE;
  const air = P.hold + P.launch * 0.9;
  const leap = CatV2.catLayout('pouncing', air);
  const leapShaped = reshaped({ bodyH: 1.2 }, () => CatV2.catLayout('pouncing', air));
  assert(
    leap.legs.every((leg, i) => leapShaped.legs[i].bottom < leg.bottom - 1e-9),
    'the leap has no ground under it -- holding those feet would detach the limbs mid-air',
  );
});

check('the head and tail ride the body they are attached to', () => {
  const base = CatV2.catLayout('walking', 0);
  const shaped = reshaped({ bodyH: 1.2 }, () => CatV2.catLayout('walking', 0));
  const dy = shaped.body.cy - base.body.cy;
  assert(dy < -1e-9, 'a taller body against a held floor must raise the centre');
  close(shaped.head.cy - base.head.cy, dy, 'the head came off the body');
  close(shaped.tail.y0 - base.tail.y0, dy, 'the tail stayed behind at the old rump');
});

check('rounding the body out is what buys visible leg', () => {
  // Measured against the v1 body, not the shipped one, so the claim stays
  // about the mechanism rather than about wherever the dials happen to sit.
  // kitten.me's 1.33 aspect, reached by height alone: ry 0.210 -> 0.241.
  const v1 = legAt(IDENT);
  const rounder = legAt({ ...IDENT, bodyH: 1.146 });
  assert(
    rounder > v1 + 0.008,
    `a rounder body must show MORE leg, not less: ${v1.toFixed(4)} -> ${rounder.toFixed(4)}`,
  );
});

check('the head ratio buys headroom, never leg', () => {
  close(legAt({ headR: 0.864 }), legAt({}), 'shrinking the head changed the leg daylight');
  const base = CatV2.catLayout('walking', 0);
  const small = reshaped({ headR: 0.864 }, () => CatV2.catLayout('walking', 0));
  assert(small.head.r < base.head.r, 'the head did not shrink');
  close(small.head.cy, base.head.cy, 'the head centre moved when only its radius was dialled');
});

// ---- POUNCE: the launch that replaced a two-position switch ----

check('the shipped pounce timing is the one the owner dialled', () => {
  // Re-pinned 2026-08-10 for the four-phase beat. The owner's 0.2 / 0.4 were
  // dialled against a TWO-phase pounce that ended airborne and held there;
  // the beat now returns to the crouch, so `launch` no longer means "and the
  // rest is held at full reach" -- the remainder is land + recover.
  const P = CatV2.POUNCE;
  close(P.hold, 0.3, 'hold drifted');
  close(P.launch, 0.42, 'launch drifted');
  close(P.land, 0.18, 'land drifted');
  close(P.snap, 4, 'snap drifted');
  close(P.twitch, 0, 'twitch drifted');
  assert(P.hold + P.launch + P.land <= 1, 'the beat must finish inside the tick');
  // The wiggle is a real frequency now. Above ~6Hz it reads as a vibration
  // rather than a cat gathering itself -- which is the bug this replaced,
  // where "2.5 rocks per load" became 14Hz once the load was 176ms.
  assert(P.wiggleHz > 0 && P.wiggleHz < 6, `wiggleHz ${P.wiggleHz} is outside the readable range`);
  close(P.wiggleHz, 1, 'wiggleHz drifted');
  close(P.wiggleAmp, 0.002, 'wiggleAmp drifted');
});

check('the pounce still reaches its crouch and its leap', () => {
  // The crouch and the leap are the drawings that shipped; pinned as literals
  // so an "improvement" to the timeline cannot quietly redraw either end.
  //
  // Rewritten 2026-08-10: the leap is no longer where the beat ENDS. Under
  // the four-phase timeline it is where the LAUNCH ends, and phase 1 is back
  // at the crouch. Sampling 0.95 now catches a cat mid-recovery.
  const P = CatV2.POUNCE;
  const loaded = reshaped(IDENT, () => CatV2.catLayout('pouncing', 0));
  close(loaded.body.cy, 0.68, 'crouch body cy');
  close(loaded.body.ry, 0.17, 'crouch body ry');
  close(loaded.head.cy, 0.5, 'crouch head cy');
  assert(
    loaded.legs.every((l) => Math.abs(l.bottom - 0.88) < 1e-12),
    'the loaded cat has every foot on the ground',
  );

  const out = reshaped(IDENT, () => CatV2.catLayout('pouncing', P.hold + P.launch));
  // Still exactly the old literals: the four-phase timeline changed WHEN the
  // leap happens, not what it looks like. Only the sample point moved.
  close(out.body.cy, 0.56, 'leap body cy');
  close(out.body.rot, -0.18, 'leap body rot');
  close(out.head.cx, 0.78, 'leap head cx');
  assert(
    out.legs.every((l) => l.bottom < 0.88 - 1e-9),
    'the leap has no foot on the ground',
  );
});

check('the launch is continuous -- no frame jumps', () => {
  // The bug this pose had: one 0.12-unit step at phase 0.45. Sampled at
  // 1/400 of a beat, no adjacent pair may move the body more than a
  // fraction of that, whatever the dials say.
  let worst = 0;
  let prev = CatV2.catLayout('pouncing', 0);
  for (let i = 1; i <= 400; i++) {
    const now = CatV2.catLayout('pouncing', i / 400);
    worst = Math.max(worst, Math.abs(now.body.cy - prev.body.cy));
    prev = now;
  }
  assert(worst < 0.01, `the pounce still jumps: biggest single-frame body move ${worst.toFixed(4)}`);
});

check('the pounce is a full beat: load, launch, land, recover', () => {
  // Replaces "the launch only ever extends, and holds at both ends".
  // That contract described a TWO-phase pounce which ended airborne and
  // stayed there, so the body only ever rose. The beat now comes back down,
  // and monotonicity is the wrong shape to assert -- the interesting
  // property is that each phase does its own job and the loop closes.
  const at = (p) => CatV2.catLayout('pouncing', p).body.cy; // smaller cy = higher
  const P = CatV2.POUNCE;
  const launchEnd = P.hold + P.launch;
  const landEnd = launchEnd + P.land;

  // The load holds still. The wiggle is a rock, not a rise, so the body may
  // move within the load -- but it must not have started climbing.
  assert(at(P.hold) >= at(0) - 0.02, 'the cat started launching before the load finished');
  // The launch rises, and rises the whole way.
  let prev = at(P.hold);
  for (let i = 1; i <= 60; i++) {
    const cy = at(P.hold + (P.launch * i) / 60);
    assert(cy <= prev + 1e-12, 'the body dropped back mid-launch');
    prev = cy;
  }
  assert(at(launchEnd) < at(0) - 0.05, 'the leap must actually rise off the crouch');
  // The landing comes back down and squashes THROUGH the crouch -- absorbing
  // is the point, so overshooting below the resting height is correct.
  assert(at(landEnd) > at(0), 'the landing must squash past the resting height');
  // And the recovery closes the loop. Phase 1 must equal phase 0 exactly or a
  // cat pouncing twice in a row jumps between beats.
  close(at(1), at(0), 'the beat does not close: phase 1 != phase 0');
});

check('pounceLaunch is exact at its ends for any dials', () => {
  for (const snap of [1, 2.4, 5]) {
    for (const hold of [0, 0.34, 0.7]) {
      const d = { hold, launch: 0.22, snap, twitch: 0 };
      close(CatV2.pounceLaunch(hold, d), 0, `snap ${snap} hold ${hold}: starts at 0`);
      close(CatV2.pounceLaunch(hold + 0.22, d), 1, `snap ${snap} hold ${hold}: ends at 1`);
      assert(CatV2.pounceLaunch(hold - 0.01, d) === 0, 'nothing happens before the hold');
      assert(CatV2.pounceLaunch(hold + 0.3, d) === 1, 'and nothing after the launch');
    }
  }
});

check('the far pair stays behind the body through the whole pounce', () => {
  for (let i = 0; i <= 20; i++) {
    const L = CatV2.catLayout('pouncing', i / 20);
    for (const leg of L.legs) {
      assert(!(leg.far && leg.front), `a shaded far leg drew in front at phase ${i / 20}`);
    }
  }
});

// ---- the sleeping head (2026-08-09) ----

check('the sleep-curl head comes from SLEEP, not a literal', () => {
  const before = CatV2.SLEEP.headR;
  try {
    close(CatV2.catLayout('sleep-curl', 0.3).head.r, before, 'the dial IS the radius');
    CatV2.SLEEP.headR = 0.21;
    close(CatV2.catLayout('sleep-curl', 0.3).head.r, 0.21, 'and moving it moves the pose');
  } finally {
    CatV2.SLEEP.headR = before; // a mutable tunable must not leak between checks
  }
});

check('the sleeping head blends rather than pops', () => {
  // head.r is interpolated by blendLayouts, so waking up is a ramp. This is
  // the trap that bit the droplet: a per-pose value that is NOT threaded
  // through blendLayouts switches at the midpoint instead.
  const sleep = CatV2.catLayout('sleep-curl', 0);
  const idle = CatV2.catLayout('idle', 0);
  assert(sleep.head.r !== idle.head.r, 'the two poses genuinely differ');
  const mid = CatV2.blendLayouts(sleep, idle, 0.5);
  const expected = (sleep.head.r + idle.head.r) / 2;
  close(mid.head.r, expected, 'halfway is halfway, not either end');
  close(CatV2.blendLayouts(sleep, idle, 0).head.r, sleep.head.r, 't=0 is exactly sleep');
  close(CatV2.blendLayouts(sleep, idle, 1).head.r, idle.head.r, 't=1 is exactly idle');
});

check('every pose draws a head, and sleep is the only one off the band', () => {
  // The band is what makes the cats read as one animal. If a future pose
  // lands outside it, that is a decision worth making on purpose.
  for (const pose of CatV2.POSES) {
    const r = CatV2.catLayout(pose, 0.3).head.r;
    assert(r > 0.1 && r < 0.3, `${pose}: head radius ${r} is off any plausible scale`);
    if (pose !== 'sleep-curl') {
      assert(r >= 0.21 && r <= 0.23, `${pose}: head ${r} left the 0.215-0.226 band`);
    }
  }
  // Sleep is allowed to sit under the band -- a curl foreshortens -- but not
  // by so much that it reads as a different, smaller animal. It shipped at
  // 0.173 (77% of the base) and that was the complaint; it is 0.211 now.
  const sleep = CatV2.catLayout('sleep-curl', 0.3).head.r;
  assert(sleep / 0.226 > 0.85, `sleep head is ${(sleep / 0.226 * 100).toFixed(0)}% of the base`);
});

check('the sleeping head sits ON the curled body, not beside it', () => {
  // A head whose centre leaves the body ellipse reads as detached, which is
  // the failure mode of moving it up and forward to make room for a bigger
  // one. Checked as the ellipse test rather than by eye.
  const L = CatV2.catLayout('sleep-curl', 0.3);
  const dx = (L.head.cx - L.body.cx) / L.body.rx;
  const dy = (L.head.cy - L.body.cy) / L.body.ry;
  const inside = dx * dx + dy * dy;
  assert(inside < 1, `head centre is outside the body ellipse (${inside.toFixed(2)})`);
  // And it must not sink through the ground line the pose is drawn on.
  assert(L.head.cy + L.head.r <= 0.88, 'the head clears the ground line');
});


// ---- the rig (animation upgrade, 2026-08-10) ----
//
// The two checks the handoff asks for by name, guarding the invariant the
// whole layer rests on: the rig is an OFFSET, so with nothing driving it the
// cat must draw exactly as it did before the rig existed. Still frames and
// reduced motion depend on this without knowing the rig is there -- they
// simply pass no rig at all.

/** The input shape render.js builds, with every channel at rest. */
const RIG_REST = {
  vx: 0, vy: 0, facing: 'left', gazeX: 0, gazeY: 0,
  earTwitch: 0, earTwitchSide: 1, earsBack: 0, yawn: 0, breath: 0,
};

check('a rig at rest draws the un-rigged cat', () => {
  // applyRig adds four channels that the un-rigged layout has no opinion
  // about; those are compared against their neutral values, and everything
  // else must be identical geometry.
  const ADDED = ['earNear', 'earFar', 'gaze', 'yawn'];
  for (const pose of CatV2.POSES) {
    for (const phase of [0, 0.25, 0.5, 0.75]) {
      const plain = CatV2.catLayout(pose, phase);
      const nulled = CatV2.applyRig(CatV2.catLayout(pose, phase), null);
      assert(
        JSON.stringify(plain) === JSON.stringify(nulled),
        `${pose}@${phase}: applyRig(L, null) is not the identity`,
      );
      const rested = CatV2.applyRig(
        CatV2.catLayout(pose, phase),
        CatV2.stepRig(CatV2.createRigState(), RIG_REST, 16),
      );
      for (const k of ADDED) delete rested[k];
      assert(
        JSON.stringify(plain) === JSON.stringify(rested),
        `${pose}@${phase}: a rig at rest moved the geometry`,
      );
    }
  }
  // And the neutral values really are neutral.
  const rest = CatV2.applyRig(CatV2.catLayout('idle', 0.25),
    CatV2.stepRig(CatV2.createRigState(), RIG_REST, 16));
  close(rest.earNear, 0, 'near ear at rest');
  close(rest.earFar, 0, 'far ear at rest');
  close(rest.yawn, 0, 'jaw at rest');
  close(rest.gaze.x, 0, 'gaze x at rest');
  close(rest.gaze.y, 0, 'gaze y at rest');
});

check('the springs return to rest after being driven', () => {
  // Underdamped on purpose, so "it settles" is a real claim and not a
  // restatement of the dials. A shove, then six seconds of nothing.
  const state = CatV2.createRigState();
  CatV2.stepRig(state, { ...RIG_REST, vx: 4 }, 16);
  let out;
  for (let i = 0; i < 400; i++) out = CatV2.stepRig(state, RIG_REST, 16);
  const plain = CatV2.catLayout('idle', 0.25);
  const settled = CatV2.applyRig(CatV2.catLayout('idle', 0.25), out);
  const drift = Math.abs(settled.tail.x1 - plain.tail.x1)
    + Math.abs(settled.head.cx - plain.head.cx);
  assert(drift < 1e-6, `the rig kept ${drift} of offset after settling`);
});

check('a still frame places the gaze without springing anything', () => {
  // stillRig is what a paused or reduced-motion frame gets. Looking at
  // something is STATE, not motion -- the same rule the wet fur and the worn
  // paths follow -- so the gaze survives a still frame, and the head and ears
  // lean with it because that is one cue and splitting it would make the
  // still frame disagree with the moving one. What must NOT survive is the
  // spring: no drag, no overshoot, nothing carried from a previous moment.
  const plain = CatV2.catLayout('idle', 0.25);
  const framed = CatV2.applyRig(
    CatV2.catLayout('idle', 0.25),
    CatV2.stillRig({ ...RIG_REST, gazeX: 0.7, gazeY: -0.4 }),
  );
  assert(framed.gaze.x !== 0 || framed.gaze.y !== 0, 'the gaze did not reach the pupils');
  assert(framed.earNear !== 0, 'the ears should turn with the look');
  // The tail is pure spring, so it is the channel that proves no momentum
  // leaked in: it must sit exactly where the pose put it.
  close(framed.tail.x1, plain.tail.x1, 'a still frame swung the tail');
  close(framed.tail.y1, plain.tail.y1, 'a still frame swung the tail');
  close(framed.tail.c2x, plain.tail.c2x, 'a still frame swung the tail');
  // And a cat with nothing to look at is the un-rigged drawing exactly.
  assert(CatV2.stillRig({ ...RIG_REST }) === null, 'no gaze should mean no rig at all');
});

check('rigFor rebuilds rather than springing out of a stale moment', () => {
  // A viewer joining mid-flight, a hidden tab, a spell of reduced motion:
  // whatever momentum the state held describes a moment this viewer never
  // saw. Starting at rest is the documented behaviour and the reconnect
  // safety the whole design is built around.
  const p = new api.Presentation();
  const driven = { ...RIG_REST, vx: 4 };
  p.rigFor('k', driven, 1000);
  for (let t = 1016; t < 1200; t += 16) p.rigFor('k', driven, t);
  const moving = p.rigFor('k', driven, 1216);
  assert(Math.abs(moving.tailTip.x) > 1e-6, 'a driven rig should have carried an offset');
  // Now leave a gap longer than a tick and come back.
  const afterGap = p.rigFor('k', RIG_REST, 1216 + 5000);
  const fresh = CatV2.stepRig(CatV2.createRigState(), RIG_REST, 16);
  assert(
    Math.abs(afterGap.tailTip.x - fresh.tailTip.x) < 1e-9,
    'a rig resumed from a stale moment instead of rebuilding at rest',
  );
});


check('every block the lab dials is actually writable', () => {
  // FOCUS_VARIANTS shipped frozen, so every slider on the hunting face was a
  // silent no-op -- and a dial that has stopped responding is indistinguishable
  // from a dial that needs turning further, which is the exact trap the
  // vocabulary's own notes warn about for the lid clamp. The house method is
  // dial-in-the-lab-then-bake, so a frozen dial block is a broken lab.
  for (const name of ['SWIM', 'POUNCE', 'GAIT', 'EYE', 'RIG', 'SLEEP', 'BELLY', 'PROPORTION', 'FOCUS_VARIANTS']) {
    const block = CatV2[name];
    assert(block, `${name} is exported`);
    assert(!Object.isFrozen(block), `${name} is frozen -- the lab cannot dial it`);
  }
  // And the write has to reach the drawing, not just the export: the module
  // reads these by reference, so the exported object must BE the live one.
  const before = CatV2.POUNCE.wiggleHz;
  try {
    CatV2.POUNCE.wiggleHz = before + 1;
    assert(CatV2.POUNCE.wiggleHz === before + 1, 'a write to POUNCE did not stick');
  } finally {
    CatV2.POUNCE.wiggleHz = before;
  }
  const variant = CatV2.EYE.focusVariant;
  const tilt = CatV2.FOCUS_VARIANTS[variant].focusLidTilt;
  try {
    CatV2.FOCUS_VARIANTS[variant] = { ...CatV2.FOCUS_VARIANTS[variant], focusLidTilt: tilt + 0.1 };
    assert(
      Math.abs(CatV2.FOCUS_VARIANTS[variant].focusLidTilt - (tilt + 0.1)) < 1e-9,
      'a write to the live focus variant did not stick',
    );
  } finally {
    CatV2.FOCUS_VARIANTS[variant] = { ...CatV2.FOCUS_VARIANTS[variant], focusLidTilt: tilt };
  }
});


check('every lab card names, in its readout, every dial it offers', () => {
  // A readout that does not name a field is quietly proposing to delete it:
  // the owner pastes back what the card printed, and the missing key reverts
  // on the next bake. That happened twice -- `land` off the Pounce card and
  // `wiggleSway` off the Portrait pounce card -- so this checks EVERY card
  // rather than the two that have already been caught.
  const html = readFileSync(join(here, 'gallery-v2.html'), 'utf8');
  const cards = html.split(/\n      title: '/).slice(1);
  let checked = 0;
  for (const card of cards) {
    const title = card.slice(0, card.indexOf("'"));
    // A dial whose label says "lab only" is a preview control -- how often
    // the lab replays a beat, say -- not a value that ever gets pasted back.
    // The convention already existed in the file; this just honours it.
    const dials = [...card.matchAll(/\{ key: '(\w+)'[^}]*\}/g)]
      .filter((m) => !/lab only/i.test(m[0]))
      .map((m) => [m[1], m[0]]);
    if (!dials.length) continue;
    // Matched on the VALUE reference (`${SOMETHING.key}`) rather than the
    // label, because a card may legitimately print a dial under another
    // name -- `VIEW.playBeatMs = ${PLAY.beatMs}`.
    for (const [key, decl] of dials) {
      // A dial may be an ALIAS -- `stand` writes PROPORTION.lift, because
      // the bag already has a `lift` from GAIT -- in which case the readout
      // names the field it writes, not the dial. Declared in the label so
      // the file says which, rather than this guessing.
      const alias = /writes \w+\.(\w+)/.exec(decl);
      const wants = alias ? alias[1] : key;
      assert(
        card.includes(`.${wants}}`),
        `the '${title}' card dials ${key} but never emits ${wants} in its readout`,
      );
    }
    checked++;
  }
  assert(checked >= 6, `only ${checked} dialled cards found -- the parser is probably broken`);
});
check('neither focused lid may eat the pupil (invariant 3)', () => {
  // The handoff's third invariant, and the one whose failure is invisible
  // from the dials: a brow deep enough to read as concentration crops the
  // pupil, and the geometry reports it GROWING while the drawing shrinks.
  // Both shipped lids ask for more than the clamp allows, so this is not a
  // hypothetical -- it is load-bearing on every frame of every hunt.
  for (const name of Object.keys(CatV2.FOCUS_VARIANTS)) {
    const F = { ...CatV2.EYE, ...CatV2.FOCUS_VARIANTS[name] };
    const er = 0.226 * CatV2.EYE.scale;
    const grow = 1 + (F.focusGrow || 0);
    const rh = er * F.apertureH * (1 - F.focusSquash) * grow;
    const focusDil = F.focusDilate ? Math.max(0.95, F.focusDilate) : null;
    const share = focusDil ? (F.focusPupilBase || F.pupil) * focusDil : F.focusPupilH;
    const ph = Math.min(rh * share, rh * F.pupilMax);
    const graze = ph * (1 - F.focusBrowGraze);
    const room = (curve, dir) => (rh + dir * (er * 0.06 + er * curve) - graze) / (2 * rh);
    // The clamp must leave the lid somewhere to sit: a NEGATIVE room means
    // even a closed-to-zero lid would cross the pupil, which is unrecoverable.
    assert(room(-F.focusLidCurve, 1) > 0, `${name}: the brow has no room at all`);
    assert(room(-F.focusLowerCurve, -1) > 0, `${name}: the cheek has no room at all`);
    // The pupil has to survive at the size it actually ships at -- but only
    // the SHIPPING take has to clear that bar. The alternatives exist to be
    // compared in the lab, and `cheek` is deliberately the gentlest: no
    // dilation at all, which leaves it a 1.35px pupil at a 31px tile. Worth
    // knowing before anyone switches to it, not worth failing over.
    if (name === CatV2.EYE.focusVariant) {
      assert(
        2 * ph * 31 > 2,
        `the shipping take '${name}' has a ${(2 * ph * 31).toFixed(2)}px pupil at a 31px tile`,
      );
    }
  }
});

check('the lid clamp actually bites — a deeper brow changes nothing', () => {
  // The check above only proves the clamp has room to work in. THIS proves it
  // is applied: both shipped lids already ask for more than they can have, so
  // asking for far more must draw the identical frame. If the clamp were
  // removed or mis-signed, the extra depth would reach the drawing and the
  // command streams would diverge.
  const name = CatV2.EYE.focusVariant;
  const original = CatV2.FOCUS_VARIANTS[name];
  const draw = () => {
    const log = [];
    CatV2.drawCat(guardCtx(log), {
      pose: 'pouncing', phase: 0.1, appearance: CatV2.appearanceFor(4),
      facing: 'right', size: 200, x: 0, y: 0, eyesOverride: 'focused',
    });
    return JSON.stringify(log);
  };
  try {
    const asShipped = draw();
    CatV2.FOCUS_VARIANTS[name] = { ...original, focusLid: original.focusLid * 4 };
    assert(draw() === asShipped, 'a 4x deeper brow reached the drawing -- the clamp is not biting');
    CatV2.FOCUS_VARIANTS[name] = { ...original, focusLowerLid: original.focusLowerLid * 4 };
    assert(draw() === asShipped, 'a 4x deeper cheek reached the drawing -- the clamp is not biting');
    // And the clamp must not be clamping EVERYTHING: a lid asking for less
    // than its room has to still move, or the dial is dead in both directions.
    CatV2.FOCUS_VARIANTS[name] = { ...original, focusLid: 0.02 };
    assert(draw() !== asShipped, 'a shallow brow changed nothing -- the dial is dead');
  } finally {
    CatV2.FOCUS_VARIANTS[name] = original;
  }
});


check('a resting pose closes its eyes rather than holding a half-lid', () => {
  // Owner, 2026-08-20: the half-lid "reads fine during transitions -- slow
  // blink, falling asleep -- but doesn't look great as a resting pose at our
  // new higher resolution". The lid POSITION was never wrong; its persistence
  // was. Passed through in 200ms it is a blink; held in front of you at
  // 57-103px it is a sleepy or unwell cat.
  //
  // Not a new convention: eating, grooming and sleep-curl already closed.
  // Drinking and loaf were the two that missed it, from when a cat drew at
  // ~31px and a lid and an arc were the same two pixels.
  //
  // Asserted WITHOUT knowing how an eye is drawn: draw the pose as shipped,
  // draw it again forced to 'closed', and require the two to be identical.
  // If the pose already closes, the override changes nothing.
  const drawn = (pose, override) => {
    const log = [];
    CatV2.drawCat(guardCtx(log), {
      pose,
      appearance: CatV2.appearanceFor(2),
      facing: 'right',
      size: 120,
      x: 0,
      y: 0,
      phase: 0.3,
      ...(override ? { eyesOverride: override } : {}),
    });
    return JSON.stringify(log);
  };

  for (const pose of ['drinking', 'loaf', 'eating', 'grooming', 'sleep-curl']) {
    assert(drawn(pose) === drawn(pose, 'closed'),
      `${pose} does not already draw closed eyes -- forcing 'closed' changed the drawing`);
  }

  // The control, and it is the whole reason the loop above means anything: a
  // pose that does NOT close must be changed by the same override. Without
  // this the check would pass if `eyesOverride` had quietly stopped working.
  for (const pose of ['idle', 'walking']) {
    assert(drawn(pose) !== drawn(pose, 'closed'),
      `${pose} draws the same with and without a forced 'closed', so eyesOverride is inert `
      + 'and the assertions above prove nothing');
  }

  // `stretch` keeps its half-lid deliberately: it is a TRANSITION, already
  // resolving to closed at the top of the push, and the owner's note exempts
  // transitions. Pinned so the exemption is a decision rather than an
  // oversight -- if it ever closes throughout, that was someone's choice.
  // Swept, because the stretch closes at the TOP of its push and only wears
  // the half-lid at the ends -- a single phase can land in either half, and
  // the first version of this check picked one that was already closed.
  const phases = Array.from({ length: 40 }, (_, i) => i / 40);
  const lidded = phases.filter((ph) => {
    const log = [];
    const logClosed = [];
    for (const [l, ov] of [[log, null], [logClosed, 'closed']]) {
      CatV2.drawCat(guardCtx(l), {
        pose: 'stretch',
        appearance: CatV2.appearanceFor(2),
        facing: 'right',
        size: 120,
        x: 0,
        y: 0,
        phase: ph,
        ...(ov ? { eyesOverride: ov } : {}),
      });
    }
    return JSON.stringify(log) !== JSON.stringify(logClosed);
  });
  assert(lidded.length > 0,
    'stretch closes throughout its cycle now; it is a transition and was left half-lidded '
    + 'on purpose, so this is either a decision nobody recorded or an accident');
  assert(lidded.length < phases.length,
    'stretch never reaches closed eyes at the top of its push, which it did before');
});

check('a belly never changes direction with the hour or the weather', () => {
  // Found 2026-08-20 by the owner asking to see the new belly value AT NIGHT.
  // `bellyInkOf` decided lighten-vs-shade from the DRAWN appearance, and
  // darkening a coat hands the lighten its headroom back -- so Clementine was
  // a shadow by day and a pale patch at dusk, night and dawn:
  //
  //   before: day D 6.9 | dusk l 2.7 | night l 4.8 | dawn l 3.2
  //
  // Not merely inconsistent: themes CROSSFADE, so the belly swung through the
  // coat colour and out the other side at every phase boundary, on the most
  // visible part of a white cat at 103px.
  //
  // Only the two near-white coats can reach the branch, which is exactly why
  // a sweep of all eight is the check -- the other six are the control, and
  // they prove the fix did not simply pin everything to one direction.
  const themes = ['day', 'dusk', 'night', 'dawn'];
  const lstar = (hex) => {
    const n = parseInt(hex.slice(1), 16);
    const lin = (v) => { const c = v / 255; return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4; };
    const y = 0.2126 * lin((n >> 16) & 255) + 0.7152 * lin((n >> 8) & 255) + 0.0722 * lin(n & 255);
    return y > 0.008856 ? 116 * y ** (1 / 3) - 16 : 903.3 * y;
  };
  // Darker-than-coat is the flipped branch. Read off the drawing, not off the
  // dial, so this still describes the cat if the derivation is rewritten.
  const darkens = (a) => lstar(a.furBase) - lstar(CatV2.bellyInkOf(a)) > 0;

  let flipped = 0;
  for (let id = 0; id < 8; id += 1) {
    const root = CatV2.appearanceFor(id);
    const want = darkens(root);
    if (want) flipped += 1;
    for (const theme of themes) {
      const shaded = CatV2.shadedAppearanceOf(root, theme);
      assert(darkens(shaded) === want,
        `${root.name} flips direction at ${theme}: the coat is ${want ? 'shaded' : 'lightened'} `
        + 'in daylight and the other way here');
      // Wet darkens by up to 0.22 on its own, so it is the second axis that
      // could reach the branch -- and it stacks on top of the theme.
      for (const wet of [0.5, 1]) {
        assert(darkens(CatV2.wetAppearanceOf(shaded, wet)) === want,
          `${root.name} flips direction when wet ${wet} at ${theme}`);
      }
    }
  }
  // The control: if nothing flips, the sweep proves only that one branch is
  // reachable. Both near-white coats must still be on the shaded branch.
  assert(flipped === 2,
    `${flipped} coats take the shaded branch, not the 2 near-white ones -- either the `
    + 'palettes changed or minSeparation no longer separates them');
});

check('every portrait pose fits inside the card chip', () => {
  // The chip was measured against the resting poses, and the idle vocabulary
  // has since grown two that are bigger than any of them: `stretch` is the
  // widest thing drawn anywhere and overran the old 54px chip by 2.2px, and
  // an idle->sit blend at full overshoot reached 6.6px off the left edge.
  // Nothing catches a portrait clipping except looking at it, so:
  const W = appNum('PORTRAIT_W');
  const H = appNum('PORTRAIT_H');
  const SIZE = appNum('PORTRAIT_CAT');
  const X = appNum('PORTRAIT_X');
  const Y = appNum('PORTRAIT_Y');

  const extentOf = (draw) => {
    const pts = [];
    let lw = 0;
    const ctx = new Proxy({}, {
      get: (t, prop) => {
        if (prop === 'canvas') return { width: W, height: H };
        return (...a) => {
          if (prop === 'ellipse') pts.push([a[0] - a[2], a[1] - a[3]], [a[0] + a[2], a[1] + a[3]]);
          else if (prop === 'arc') pts.push([a[0] - a[2], a[1] - a[2]], [a[0] + a[2], a[1] + a[2]]);
          else if (prop === 'moveTo' || prop === 'lineTo') pts.push([a[0], a[1]]);
          else if (prop === 'quadraticCurveTo') pts.push([a[0], a[1]], [a[2], a[3]]);
          else if (prop === 'bezierCurveTo') pts.push([a[0], a[1]], [a[2], a[3]], [a[4], a[5]]);
        };
      },
      set: (t, prop, v) => {
        if (prop === 'lineWidth' && typeof v === 'number') lw = Math.max(lw, v);
        return true;
      },
    });
    draw(ctx);
    const xs = pts.filter((q) => Number.isFinite(q[0])).map((q) => q[0]);
    const ys = pts.filter((q) => Number.isFinite(q[1])).map((q) => q[1]);
    const pad = lw / 2;
    return [
      X + (Math.min(...xs) - pad) * SIZE, X + (Math.max(...xs) + pad) * SIZE,
      Y + (Math.min(...ys) - pad) * SIZE, Y + (Math.max(...ys) + pad) * SIZE,
    ];
  };
  const base = { appearance: CatV2.appearanceFor(2), facing: 'right', size: SIZE, x: X, y: Y };
  const fits = (label, [x0, x1, y0, y1]) => {
    assert(x0 >= 0, `${label}: ${(-x0).toFixed(1)}px off the LEFT of the chip`);
    assert(x1 <= W, `${label}: ${(x1 - W).toFixed(1)}px off the RIGHT of the chip`);
    assert(y0 >= 0, `${label}: ${(-y0).toFixed(1)}px off the TOP of the chip`);
    assert(y1 <= H, `${label}: ${(y1 - H).toFixed(1)}px off the BOTTOM of the chip`);
  };
  // The poses a portrait can hold. `idlePoseFor` only ever answers sit or
  // stretch, and the resting pose is always idle.
  for (const pose of ['idle', 'sit', 'stretch', 'pouncing']) {
    for (let i = 0; i <= 8; i++) {
      fits(pose, extentOf((ctx) => CatV2.drawCat(ctx, { ...base, pose, phase: i / 8 })));
    }
  }
  // And the blends into them. The portrait clamps t to [0,1] where the meadow
  // lets `easeBack` lean past both ends -- so the clamp has to be asserted
  // DIRECTLY. Sampling [0,1] here cannot detect its removal, because the
  // range is this test's own choice, not the code's: measured, an unclamped
  // idle->sit overshoot reaches 6.6px off the left of the chip and 6.5px off
  // the bottom.
  assert(
    /t: Math\.min\(1, Math\.max\(0, tween\.blend\.t\)\)/.test(appSrc),
    'the portrait blend is no longer clamped -- the overshoot will leave the chip',
  );
  // The wiring itself. Geometry checks pass perfectly well on a portrait that
  // has quietly gone back to a hardcoded 'idle', so the feature needs saying
  // out loud.
  assert(
    /view\.idleCardBeatFor\(id, 'idle'\)/.test(appSrc),
    'the portrait no longer asks its own beat table for a pose',
  );
  assert(/idle\?\.pose \?\? 'idle'/.test(appSrc), 'the portrait no longer USES the idle pose it asked for');
  // ...and the WORLD's wake-stretch stays out of it (2026-08-10). The card
  // took it until measurement showed cats wake every ~21s, which made the
  // stretch beat the blink -- and that the meadow, drawing first, deleted
  // `wokeAt` a tick later, so the portrait only ever got half a stretch.
  // Asserted as absence because there is no value to compare: re-adding the
  // call is the regression, and it would look perfectly reasonable in review.
  // Matched on the CALL, not the name -- the reasoning above has to be free
  // to talk about `idlePoseFor` without failing the check that enforces it.
  assert(
    !/view\.idlePoseFor\s*\(/.test(appSrc),
    'the portrait is consulting idlePoseFor again -- the world wake-stretch will preempt the card table',
  );
  // And the key namespace, which is the part that breaks something else when
  // it goes: the presentation layer's pose memory is per-key, so a portrait
  // sharing the meadow cat's key restarts its blend every frame. Same hazard
  // rigFor documents, on a different map.
  assert(
    /tweenFor\(`card\$\{id\}`/.test(appSrc),
    "the portrait tween must be keyed 'card' + id, never the bare id",
  );
  for (const to of ['sit', 'stretch', 'pouncing']) {
    for (let i = 0; i <= 16; i++) {
      const t = i / 16;
      fits(`idle->${to} @t=${t.toFixed(2)}`, extentOf((ctx) =>
        CatV2.drawCatTween(ctx, { ...base, from: 'idle', to, t, phaseFrom: 0.3, phaseTo: 0.3 })));
    }
  }
});


check('the portrait pose beats are portrait-only and pure', () => {
  const p = new api.Presentation();
  // The meadow must never get one: a pounce on the map is a served fact,
  // and inventing one would be the client asserting something the world did
  // not say. The guard is that it only ever answers for 'idle'.
  //
  // Tested at a moment the beat is actually LIVE. Asserting null at an
  // arbitrary time proves nothing: most times answer null for every pose
  // because the beat is not running, so the guard can be deleted and the
  // check still passes. (It did.)
  let live = null;
  for (let t = 0; t < 200000 && live === null; t += 100) {
    if (p.idleCardBeatFor(1, 'idle', t)) live = t;
  }
  assert(live !== null, 'never found a moment the play-pounce was running');
  for (const pose of ['walking', 'pouncing', 'eating', 'loaf', 'sleep-curl', 'swim']) {
    assert(p.idleCardBeatFor(1, pose, live) === null, `it answered for ${pose} at a live moment`);
  }
  // Pure in (id, now), like every other idle decision -- a still frame and a
  // test both have to be able to ask what a cat is doing at time T.
  for (const t of [0, 1234, 55555, 999999]) {
    assert(
      JSON.stringify(p.idleCardBeatFor(2, 'idle', t)) === JSON.stringify(p.idleCardBeatFor(2, 'idle', t)),
      `not pure at ${t}`,
    );
  }
  // A cat waking must not reach the card table (2026-08-10). app.js dropping
  // its idlePoseFor call is only half the guard -- this is the other half, so
  // the world cannot get back in by wiring `wokeAt` into the beat itself.
  //
  // Driven through a REAL wake rather than by poking the map: pushState is
  // what sets wokeAt, and a test that set the field by hand would keep
  // passing if the trigger moved.
  const woken = new api.Presentation();
  const before = [];
  for (let t = 0; t < 40000; t += 250) before.push(JSON.stringify(woken.idleCardBeatFor(1, 'idle', t)));
  woken.pushState({ tick: 1, elements: [], kitties: [{ ...kitty(1, 2, 2), activity: { state: 'sleeping' } }] }, 1000);
  woken.pushState({ tick: 2, elements: [], kitties: [{ ...kitty(1, 2, 2), activity: { state: 'idle' } }] }, 1800);
  assert(woken.wokeAt.has(1), 'the wake was never recorded -- this check is testing nothing');
  assert(
    woken.idlePoseFor(1, 'idle', 1800)?.pose === 'stretch',
    'idlePoseFor no longer offers the wake-stretch, so the card cannot be shown to refuse it',
  );
  const after = [];
  for (let t = 0; t < 40000; t += 250) after.push(JSON.stringify(woken.idleCardBeatFor(1, 'idle', t)));
  assert(
    before.join('|') === after.join('|'),
    'a world wake changed the card beat table -- the portrait is back on the world clock',
  );
  // Four portraits must not move in UNISON. Not "never at the same time":
  // each cat is busy ~12% of the time now that the sit chain is 5.8s, so
  // independent draws coincide ~8% of the time by arithmetic, and asserting
  // zero would just be asserting the beats are rare. What must hold is that
  // the cats are not on the same clock -- so it is the phase offsets that
  // get checked.
  const period = api.VIEW.cardBeatPeriodMs;
  const offsets = [1, 2, 3, 4].map((id) => api.idleHash(id, 0, api.IDLE_SALTS.offset) * period);
  let closest = Infinity;
  for (let i = 0; i < offsets.length; i++) {
    for (let j = i + 1; j < offsets.length; j++) {
      const d = Math.abs(offsets[i] - offsets[j]);
      closest = Math.min(closest, Math.min(d, period - d));
    }
  }
  assert(
    closest > period * 0.04,
    `two portraits sit only ${(closest / 1000).toFixed(2)}s apart -- they will read as one clock`,
  );
});

check('the portrait beat is long enough for the wiggle to be a wiggle', () => {
  // The whole reason this beat is off the served tick. `pounceWiggle`
  // quantises to half-cycles so its sine lands on zero at the launch, and
  // half a cycle is ONE rock -- a lean, not a wiggle. The step is sharp: at
  // the shipped wiggleHz a 3000ms beat gives one rock and 3200 gives two, so
  // a re-dial can cross it without looking obviously different in a still.
  const P = CatV2.POUNCE;
  const holdSec = (P.hold * api.VIEW.playBeatMs) / 1000;
  // VIEW.playWiggleHz, NOT POUNCE.wiggleHz: the portrait picks its own rate,
  // because the map's is tuned against a 192ms load and the same value in a
  // 768ms load is a wallow. Computing this from the map's rate would pass
  // while testing a number the portrait never uses.
  const cycles = Math.max(0.5, Math.round(api.VIEW.playWiggleHz * holdSec * 2) / 2);
  assert(cycles >= 1, `the portrait load holds ${cycles} cycles -- one rock, not a wiggle`);
  // And the rock has to clear the size things read at here: the whiskers
  // died at ~0.8px and the body bob was reverted at 0.56px.
  const beat = {
    beatMs: api.VIEW.playBeatMs,
    wiggleHz: api.VIEW.playWiggleHz,
    sway: api.VIEW.playSway,
  };
  const rest = CatV2.catLayout('pouncing', 0, beat).body.cy;
  let swing = 0;
  for (let i = 0; i <= 100; i++) {
    const L = CatV2.catLayout('pouncing', (P.hold * i) / 100, beat);
    swing = Math.max(swing, Math.abs(L.body.cy - rest));
  }
  // Total travel of the hindquarters, since which axis carries the tread is
  // a dial -- see 'the tread moves the BUTT'.
  const rearOf = (L) => [
    L.body.cx - Math.cos(L.body.rot) * L.body.rx,
    L.body.cy - Math.sin(L.body.rot) * L.body.rx,
  ];
  const [rx0, ry0] = rearOf(CatV2.catLayout('pouncing', 0, beat));
  let travel = 0;
  for (let i = 0; i <= 100; i++) {
    const [rx, ry] = rearOf(CatV2.catLayout('pouncing', (P.hold * i) / 100, beat));
    travel = Math.max(travel, Math.hypot(rx - rx0, ry - ry0));
  }
  const px = travel * 47; // PORTRAIT_CAT
  assert(px > 0.8, `the tread travels ${px.toFixed(2)}px at portrait size -- under the floor`);
});


check('a caller may pick its own wiggle rate without moving the map\'s', () => {
  // The portrait needs a faster rock than the map, and must not get it by
  // reaching into POUNCE -- that would change the world's pounce as a side
  // effect of a card dial.
  const beat = 3200;
  // Swept, and over the whole body -- not one field at one phase. Two rates
  // cross at particular moments (1Hz and 3.4Hz give an identical `cy` at
  // phase 0.1 while `cx` differs by 0.03), so a single sample can report the
  // override as dead when it is working perfectly.
  const differs = (a, b) => a.body.cx !== b.body.cx || a.body.cy !== b.body.cy
    || a.body.rx !== b.body.rx || a.body.rot !== b.body.rot;
  let moved = 0;
  for (let i = 0; i <= 40; i++) {
    const ph = (CatV2.POUNCE.hold * i) / 40;
    if (differs(
      CatV2.catLayout('pouncing', ph, { beatMs: beat, wiggleHz: 1 }),
      CatV2.catLayout('pouncing', ph, { beatMs: beat, wiggleHz: 3.4 }),
    )) moved++;
  }
  assert(moved > 20, `the wiggleHz override reached the drawing at only ${moved}/41 phases`);
  // Absent, the map's own dial is what applies -- unchanged either way.
  const before = CatV2.POUNCE.wiggleHz;
  CatV2.catLayout('pouncing', 0.1, { beatMs: beat, wiggleHz: 7 });
  assert(CatV2.POUNCE.wiggleHz === before, 'an override mutated the shared dial');
  const plain = CatV2.catLayout('pouncing', 0.1, { beatMs: beat });
  const asMap = CatV2.catLayout('pouncing', 0.1, { beatMs: beat, wiggleHz: before });
  close(plain.body.cy, asMap.body.cy, 'no override should mean the map\'s rate');
});


check('the tread moves the BUTT, and only the butt', () => {
  // It shipped moving the chest instead, 27:1 the wrong way, on a pose whose
  // own comment says it "treads its hind feet and rocks its hindquarters".
  // The rock is a cy shift PLUS a rotation about the body's centre, so the
  // two add at one end of the ellipse and cancel at the other -- and with
  // the signs agreeing they added at the front.
  //
  // Measured as TOTAL travel, not per axis. WHICH axis carries the tread is
  // a dial: the owner moved it from a vertical bob to a lateral rock
  // (wiggleAmp 0.022 -> 0.002, the sway doing the work instead), and a
  // per-axis assertion only encodes whichever choice was current when it was
  // written. What has to hold either way is that the REAR moves, visibly,
  // and the chest does not.
  const P = CatV2.POUNCE;
  // The base cat faces right, so the hindquarters sit at cx - rx.
  const ends = (L) => ({
    rearX: L.body.cx - Math.cos(L.body.rot) * L.body.rx,
    rearY: L.body.cy - Math.sin(L.body.rot) * L.body.rx,
    frontX: L.body.cx + Math.cos(L.body.rot) * L.body.rx,
    frontY: L.body.cy + Math.sin(L.body.rot) * L.body.rx,
  });
  for (const [beat, px] of [
    [{ beatMs: 800 }, 31],
    [{ beatMs: api.VIEW.playBeatMs, wiggleHz: api.VIEW.playWiggleHz, sway: api.VIEW.playSway }, 47],
  ]) {
    const rest = ends(CatV2.catLayout('pouncing', 0, beat));
    let rear = 0;
    let front = 0;
    for (let i = 0; i <= 300; i++) {
      const e = ends(CatV2.catLayout('pouncing', (P.hold * i) / 300, beat));
      rear = Math.max(rear, Math.hypot(e.rearX - rest.rearX, e.rearY - rest.rearY));
      front = Math.max(front, Math.hypot(e.frontX - rest.frontX, e.frontY - rest.frontY));
    }
    // Visible at the size it is drawn at: the whiskers died at ~0.8px and the
    // body bob was reverted at 0.56px peak-to-peak.
    assert(rear * px > 0.8, `beat ${beat.beatMs}: the tread is ${(rear * px).toFixed(2)}px at ${px}px`);
    // The planted front is the other half of the read.
    assert(rear > front * 4, `beat ${beat.beatMs}: the chest moved ${(front / rear).toFixed(2)}x the butt`);
    assert(front * px < 0.4, `beat ${beat.beatMs}: the chest travels ${(front * px).toFixed(2)}px`);
  }

  // And the tread has to be back at rest when the cat leaves the ground --
  // the same reason the rock quantises to half-cycles. A body still swung at
  // the launch takes the swing into the air with it. A PIXEL claim, not an
  // equality: sampling either side of the boundary always differs a little,
  // and "invisible" is measured in pixels.
  for (const beat of [
    { beatMs: 800 },
    { beatMs: api.VIEW.playBeatMs, wiggleHz: api.VIEW.playWiggleHz, sway: api.VIEW.playSway },
  ]) {
    const at = (ph) => CatV2.catLayout('pouncing', ph, beat);
    const before = at(P.hold - 1e-4);
    const after2 = at(P.hold + 1e-4);
    const jump = Math.max(
      Math.abs(before.body.cx - after2.body.cx),
      Math.abs(before.body.rx - after2.body.rx),
      Math.abs(before.body.cy - after2.body.cy),
    ) * 47;
    assert(jump < 0.02, `beat ${beat.beatMs}: the tread pops ${jump.toFixed(3)}px at the launch`);
  }
});

check("the hunter's face is gated on how far the quarry is", () => {
  // Measured on the candidate roster, 4,604 cat-ticks: the median quarry
  // was 10 tiles away and the commonest 12, so an ungated face put a
  // hunting expression on a cat walking normally after a bug across the
  // meadow -- 85.6% of hunter faces were outside the 4-tile gate the POSE
  // uses, meaning the pose and the expression disagreed about whether a
  // hunt was on. Owner gated it at 8 (2026-08-14): wider than the pounce,
  // because eyes may lead a pounce, but not across the whole map.
  const p = new api.Presentation();
  const hunting = { pursuit: { target: { target: 'element', id: 9 } },
    last_action: { action: 'chase', target: 'element', id: 9 } };
  const gate = VIEW.hunterGateTiles;
  assert(p.expressionFor(hunting, gate) === 'focused', `at ${gate} tiles the face should still be on`);
  assert(p.expressionFor(hunting, gate - 1) === 'focused', 'inside the gate the face should be on');
  assert(p.expressionFor(hunting, gate + 1) === undefined, `at ${gate + 1} tiles the face should be gone`);
  assert(p.expressionFor(hunting, 20) === undefined, 'across the map it should be gone');
  assert(p.expressionFor(hunting, 0) === 'focused', 'on top of the quarry it should be on');

  // `null` is not "far". An unresolvable quarry -- caught or expired this
  // very tick -- keeps the face, which is the rule the pounce gate follows
  // too: take it away only on positive evidence.
  assert(p.expressionFor(hunting, null) === 'focused', 'an unresolved quarry lost its face to the gate');
  assert(p.expressionFor(hunting) === 'focused', 'a caller passing no distance must be unaffected');

  // The gate cannot GRANT a face: a kitty quarry has none at any distance.
  const social = { pursuit: { target: { target: 'kitty', id: 2 } },
    last_action: { action: 'chase', target: 'kitty', id: 2 } };
  for (const d of [0, gate, gate + 5, null]) {
    assert(p.expressionFor(social, d) === undefined, `chasing a kitty at ${d} wore the hunting face`);
  }
  assert(gate > VIEW.pounceGateTiles, 'the eyes are meant to reach further than the pounce');
});

check("the hunter's face reaches the cats that hunt", () => {
  // It shipped UNREACHABLE. `pursuit.target` is a TargetRef object
  // ({target: 'kitty', id: 2}) and `last_action.target` is a plain string
  // ('kitty') -- two shapes, one comparison against 'element' -- so every
  // pursuing cat fell through and 'focused' was never returned at all. The
  // gallery could not catch it: its card forces the expression with
  // `eyesOverride` instead of going through here.
  //
  // Shapes below are verbatim from the live server.
  const p = new api.Presentation();
  const pursuing = (kind, id) => ({
    pursuit: { target: { target: kind, id }, started: 1, closest: 6, improved_at: 1 },
    last_action: { action: 'chase', target: kind, id },
  });
  assert(p.expressionFor(pursuing('element', 9)) === 'focused', 'a cat hunting a bug should wear the hunting face');
  assert(p.expressionFor(pursuing('kitty', 2)) === undefined, 'a cat chasing a kitty should NOT wear it');
  // Play is a playmate too, whatever the action says.
  assert(
    p.expressionFor({ pursuit: { target: { target: 'kitty', id: 3 } }, last_action: { action: 'play', target: 'kitty', id: 3 } }) === undefined,
    'play on a kitty wore the hunting face',
  );
  // Withheld only on POSITIVE evidence, so an unresolvable quarry keeps it.
  assert(
    p.expressionFor({ pursuit: { target: null }, last_action: { action: 'chase', target: null } }) === 'focused',
    'a quarry caught this tick lost the face to a missing field',
  );
  // And a cat that is not pursuing at all keeps its ordinary eyes.
  assert(p.expressionFor({ last_action: { action: 'groom', target: null } }) === undefined, 'an idle cat wore the hunting face');
  // The string form on its own has to work too -- it is the fallback path.
  assert(
    p.expressionFor({ pursuit: { target: undefined }, last_action: { action: 'chase', target: 'element', id: 4 } }) === 'focused',
    'the last_action string fallback does not resolve',
  );
});


check('the hunter is hunting, not merely holding a grudge', () => {
  // Owner, 2026-08-16: hunter eyes on a cat RESTING beside another cat, and
  // again while GROOMING with a bug nearby. Both are the same fault, and it
  // is not the distance gate that let them through -- the bug really was
  // close. `pursuit` is an intention that outlives the acts serving it (its
  // own doc: it "survives a cat stopping for a drink"), so asking only
  // whether one exists asks what the cat WANTS, never what she is doing.
  //
  // Live sample, 945 kitty-ticks: of the ticks drawing the face, 27 were
  // `chase`, 19 `move` -- and 6 were `idle`, a cat standing perfectly still
  // in a hunter's face. The owner's groom and rest are the same absence.
  //
  // The fix shipped in #237 with only a fixture repair beside it; this is
  // its coverage, split out at the owner's request.
  const p = new api.Presentation();
  const hunting = (action) => ({
    pos: { x: 5, y: 5 },
    pursuit: { target: { target: 'element', id: 9 }, started: 1, closest: 3, improved_at: 2 },
    last_action: { action, target: 'element', id: 9 },
  });

  // Going after it -- both shapes seen live, plus the pounce that ends a
  // hunt. Losing the face at the pounce would take it away at the one
  // moment the hunt is most plainly a hunt.
  for (const action of ['chase', 'move', 'play']) {
    assert(p.expressionFor(hunting(action), 2) === 'focused',
      `a cat mid-hunt applying '${action}' lost the hunting face`);
  }

  // Sitting still with it on file. Every one of these is a cat the viewer
  // sees doing something else entirely.
  for (const action of ['groom', 'rest', 'sleep', 'eat', 'drink', 'purr', 'meow', 'idle']) {
    assert(p.expressionFor(hunting(action), 2) === undefined,
      `THE BUG: a cat applying '${action}' wore the hunting face`);
  }

  // The owner's two reports, built as served: the quarry is genuinely near,
  // so nothing else in the chain can be what withholds the face.
  const resting = hunting('rest');
  resting.activity = { state: 'resting' };
  assert(p.expressionFor(resting, 1) === undefined,
    'a cat resting next to a friend, bug one tile away, still hunted');
  const grooming = hunting('groom');
  grooming.activity = { state: 'grooming' };
  assert(p.expressionFor(grooming, 0) === undefined,
    'a cat grooming on top of a bug still hunted');

  // An action nobody has thought of yet reads as not-hunting: the owner
  // asked for the face "only when in active pursuit", so the list is an
  // allow-list and a new stationary action cannot inherit the face.
  assert(p.expressionFor(hunting('sunbathe'), 2) === undefined,
    'an unknown action inherited the hunting face');
  assert(p.expressionFor({ pursuit: { target: { target: 'element', id: 9 } } }, 2) === undefined,
    'a kitty with no applied action at all wore the hunting face');

  // And this must not have eaten the OTHER benefit of the doubt, which is
  // about a different field: an unresolvable QUARRY still keeps the face,
  // so long as the cat is actually pursuing.
  assert(p.expressionFor({ ...hunting('chase'), pursuit: { target: null } }, null) === 'focused',
    'a quarry caught this very tick lost the face while the cat was still chasing');
});

check('the portrait sit gets up through a stretch', () => {
  // The chain, and the reason sit can be scheduled at all: sit-then-stretch
  // is a BOUNDED BEAT, where the map's sit is a posture that runs 26-130s
  // and has to coexist with blinks. It is also what a cat actually does
  // standing up.
  //
  // Walked as a continuous timeline rather than per slot: the per-cat phase
  // offset means slot boundaries do not line up with `slot * period`, and
  // assuming they did made this read the chain as running off the end.
  const p = new api.Presentation();
  p.tickMs = 800;
  const stretchMs = api.VIEW.stretchTicks * 800;
  const STEP = 50;
  const seq = [];
  for (let t = 0; t < 900000; t += STEP) {
    const r = p.idleCardBeatFor(1, 'idle', t);
    seq.push(r ? r.pose : null);
  }
  // Every run of 'sit' must be followed immediately by a run of 'stretch'.
  let chains = 0;
  for (let i = 1; i < seq.length; i++) {
    if (seq[i - 1] === 'sit' && seq[i] !== 'sit') {
      assert(seq[i] === 'stretch', `a sit was followed by ${seq[i]}, not a stretch`);
      chains++;
      // ...and the stretch by nothing, never straight back to a sit.
      let j = i;
      while (seq[j] === 'stretch') j++;
      assert(seq[j] === null, `the stretch was followed by ${seq[j]}`);
    }
  }
  assert(chains > 5, `only ${chains} sit chains in 900s -- too few to trust`);

  // Durations are the dials, within one sample.
  const runLen = (want) => {
    let best = 0;
    let run = 0;
    for (const v of seq) {
      if (v === want) run++;
      else { best = Math.max(best, run); run = 0; }
    }
    return Math.max(best, run) * STEP;
  };
  const sitRun = runLen('sit');
  const stretchRun = runLen('stretch');
  assert(Math.abs(sitRun - api.VIEW.sitHoldMs) <= STEP, `the sit held ${sitRun}ms, want ${api.VIEW.sitHoldMs}`);
  assert(Math.abs(stretchRun - stretchMs) <= STEP, `the stretch ran ${stretchRun}ms, want ${stretchMs}`);

  // The stretch carries a phase that sweeps, so it eases rather than holding.
  const phases = [];
  for (let t = 0; t < 900000 && phases.length < 400; t += STEP) {
    const r = p.idleCardBeatFor(1, 'idle', t);
    if (r?.pose === 'stretch') phases.push(r.phase);
  }
  assert(Math.min(...phases) < 0.2 && Math.max(...phases) > 0.8, 'the stretch phase does not sweep');
});

check('the card beat weights are a share of 100, like the motion table', () => {
  // The handoff added scan and yawn ON TOP of the rarity budget by
  // declaring a weight twice; the budget only means something if it sums.
  const w = ['cardBlinkWeight', 'cardEarsWeight', 'cardScanWeight', 'cardYawnWeight',
    'cardSitWeight', 'cardPounceWeight', 'cardRestWeight'].map((k) => api.VIEW[k]);
  const total = w.reduce((a, b) => a + b, 0);
  assert(total === 100, `the card beat weights total ${total}, not 100`);
});


check('a portrait does exactly one thing at a time', () => {
  // The point of the whole rework. Two clocks -- motion slots plus a pose
  // clock -- put sixteen pose x motion pairs on screen that nobody chose,
  // including a cat yawning mid-pounce and blinking while gathering itself
  // to leap. One table, one beat, and the next beat AFTER it.
  const p = new api.Presentation();
  p.tickMs = 800;
  const channels = ['blinkLid', 'earTwitch', 'gaze', 'yawn'];
  let beats = 0;
  for (let t = 0; t < 900000; t += 50) {
    const r = p.idleCardBeatFor(1, 'idle', t);
    if (!r) continue;
    beats++;
    const live = channels.filter((c) => r[c] !== undefined && r[c] !== 0);
    const posed = r.pose !== 'idle';
    assert(live.length <= 1, `${live.join(' + ')} played together`);
    assert(
      !(posed && live.length),
      `a ${r.pose} played with a ${live[0]} -- poses and motions must sequence, not layer`,
    );
  }
  assert(beats > 1000, 'not enough beats sampled to trust this');
});

check('every portrait beat fits inside its slot', () => {
  // One-at-a-time only holds if a beat cannot run past its slot into the
  // next one. The sit chain is the long pole at 5.8s.
  const V = api.VIEW;
  const lengths = {
    blink: V.slowBlinkDownMs + V.slowBlinkHoldMs + V.slowBlinkUpMs,
    ears: V.idleMotionWindowMs,
    scan: V.scanMs,
    yawn: V.yawnOpenMs + V.yawnHoldMs + V.yawnCloseMs,
    sit: V.sitHoldMs + V.stretchTicks * 800,
    pounce: V.playBeatMs,
  };
  for (const [kind, ms] of Object.entries(lengths)) {
    assert(ms <= V.cardBeatPeriodMs, `the ${kind} beat is ${ms}ms in a ${V.cardBeatPeriodMs}ms slot`);
  }
  // And observed: no two consecutive beats ever touch without a gap.
  const p = new api.Presentation();
  p.tickMs = 800;
  let prev = null;
  let runs = 0;
  for (let t = 0; t < 600000; t += 50) {
    const r = p.idleCardBeatFor(1, 'idle', t);
    const kind = r ? (r.pose !== 'idle' ? r.pose : 'motion') : null;
    if (kind && prev && kind !== prev && !(prev === 'sit' && kind === 'stretch')) {
      assert(false, `a ${prev} ran straight into a ${kind} with no gap`);
    }
    if (kind !== prev) runs++;
    prev = kind;
  }
  assert(runs > 20, 'not enough transitions sampled');
});

// ---- the axial views: north and south are real drawings (2026-08-10) ----

/** Every op a cat draws, so order and colour are both inspectable. */
function drawLog(id, view, facing, pose = 'walking') {
  const out = [];
  const ctx = new Proxy(
    {},
    {
      get: (_t, p) => (...a) => {
        for (const v of a) {
          if (typeof v === 'number' && !Number.isFinite(v)) {
            throw new Error(`ctx.${String(p)} got non-finite args: ${a}`);
          }
        }
        out.push([String(p), ...a]);
      },
      set: (_t, p, v) => {
        out.push(['set', String(p), v]);
        return true;
      },
    },
  );
  CatV2.drawCat(ctx, {
    appearance: CatV2.appearanceFor(id),
    facing,
    size: 120,
    x: 0,
    y: 0,
    pose,
    phase: 0.3,
    layout: { view },
  });
  return out;
}
const marks = (log, color) =>
  log.filter((o) => o[0] === 'set' && o[1] === 'fillStyle' && String(o[2]).toLowerCase() === color)
    .length;

check('a muzzle is on the face, so a cat walking away has none', () => {
  // The bug this pins: paintCat deliberately skips drawFace and the inner
  // ears for the back view -- but the muzzle masks are painted by drawHead,
  // which ran regardless. The face vanished and a dark oval stayed behind
  // on the back of the skull. Only the tabby's forehead stripes consulted
  // `view` before this.
  //
  // Asserted as a DIFFERENCE rather than an absolute count: the point
  // colour also paints ears, paws and tail, and those are all still in view
  // from behind. Exactly one marking must disappear, and it is the muzzle.
  for (const [id, label, color] of [
    [1, 'Miso, seal point (LIVE)', '#986f4e'],
    [0, 'tuxedo (gallery only)', '#fbf7f0'],
  ]) {
    const side = marks(drawLog(id, 'side', 'right'), color);
    const front = marks(drawLog(id, 'front', 'south'), color);
    const back = marks(drawLog(id, 'back', 'north'), color);
    assert(side === front, `${label}: the muzzle must survive the FRONT view (${side} vs ${front})`);
    assert(back === front - 1, `${label}: expected exactly the muzzle to go, got ${front} -> ${back}`);
  }
});

check('the muzzle mask sits on the nose, in every view', () => {
  // Owner spotted this on the front view (2026-08-10): the nose moves to
  // the centreline head-on, and the muzzle MASK did not follow, so a
  // front-on seal point wore her dark muzzle beside her own nose.
  //
  // Both now go through `muzzleX`, so the check is that they COINCIDE
  // rather than that either is at a particular place -- a re-dialled NOSE.x
  // must not need this edited, and the side view (where they always did
  // agree) has to keep agreeing.
  //
  // The two are picked out by SIZE, not by colour: the point colour also
  // paints ears, paws and tail, and noseColor also paints the inner ears,
  // so a colour match alone measures the wrong shapes. (It did, first try.)
  const centres = (view, facing) => {
    const L = CatV2.catLayout('idle', 0.2, { view });
    const r = L.head.r;
    const ns = r * CatV2.NOSE.size;
    let fill = null; const stack = []; let pend = null; let tri = [];
    let mask = null; let nose = null;
    const ctx = new Proxy({}, {
      get: (_t, k) => {
        if (k === 'save') return () => stack.push(fill);
        if (k === 'restore') return () => { fill = stack.pop() ?? fill; };
        if (k === 'ellipse') return (cx, _cy, rx) => { pend = { cx, rx }; };
        if (k === 'beginPath') return () => { pend = null; tri = []; };
        if (k === 'moveTo') return (x) => { tri = [x]; };
        if (k === 'lineTo') return (x) => { tri.push(x); };
        if (k === 'fill') return () => {
          if (pend && Math.abs(pend.rx - r * 0.46) < r * 0.02) mask = pend.cx;
          if (tri.length >= 3 && Math.abs(Math.abs(tri[1] - tri[0]) - 2 * ns) < r * 0.02) {
            nose = (tri[0] + tri[1]) / 2;
          }
        };
        if (k === 'canvas') return { width: 200, height: 200 };
        return () => {};
      },
      set: (_t, k, v) => { if (k === 'fillStyle') fill = v; return true; },
    });
    CatV2.drawCat(ctx, {
      appearance: CatV2.appearanceFor(1), // Miso, the roster's one seal point
      facing, size: 1, x: 0, y: 0, pose: 'idle', phase: 0.2, layout: { view },
    });
    return { mask, nose };
  };
  // Where each view must put it. "Mask equals nose" alone is NOT enough:
  // both now call muzzleX, so they agree by construction and would go on
  // agreeing while both drifted. (Checked -- reverting muzzleX to the side
  // offset left an equality-only version of this passing.) The binding
  // assertion is the absolute one: front-on it is the centreline.
  for (const [view, facing] of [['front', 'south'], ['side', 'right']]) {
    const L = CatV2.catLayout('idle', 0.2, { view });
    const want = L.head.cx + L.head.r * (view === 'front' ? 0 : CatV2.NOSE.x);
    const { mask, nose } = centres(view, facing);
    assert(mask !== null, `${view}: never found the muzzle mask`);
    assert(nose !== null, `${view}: never found the nose`);
    close(mask, want, `${view}: the muzzle mask is not where this view puts a muzzle`);
    close(mask, nose, `${view}: the muzzle mask is off the nose`);
  }
});

check('paint order IS depth order: walking away inverts head and tail', () => {
  // Handoff invariant 6. For a cat walking away the head is the furthest
  // part of it and the tail the nearest, so the head draws BEHIND the body
  // and the tail in FRONT. Those two are the only depth cues the back view
  // has, and drawing them in the side view's order reads as a cat facing
  // you with its face rubbed out.
  //
  // Read off the ORDER of the two path builders rather than any coordinate,
  // because that is the whole claim -- a correct back view drawn in the
  // wrong order would pass every geometric check there is.
  // `headPath` is an arc of exactly head.r; the tail is the only bezier.
  // Both are read from the log rather than from coordinates, because the
  // claim is about ORDER -- a correct back view drawn in the wrong order
  // would pass every geometric check there is.
  for (const [view, facing, headBeforeTail] of [
    ['side', 'right', false],
    ['back', 'north', true],
  ]) {
    const log = drawLog(1, view, facing);
    const r = CatV2.catLayout('walking', 0.3, { view }).head.r;
    const headAt = log.findIndex((o) => o[0] === 'arc' && Math.abs(o[3] - r) < 1e-9);
    const tailAt = log.findIndex((o) => o[0] === 'bezierCurveTo');
    assert(headAt >= 0, `${view}: never found the head`);
    assert(tailAt >= 0, `${view}: never found the tail`);
    assert(
      headBeforeTail ? headAt < tailAt : headAt > tailAt,
      `${view}: head at ${headAt}, tail at ${tailAt} -- depth order is wrong`,
    );
  }
});

check('a pose with no axial authoring keeps its side drawing', () => {
  // The fallback is "draw the cat we have", never "draw nothing". Only
  // walking and idle are authored; everything else must be untouched by
  // the view, byte for byte.
  for (const pose of ['grooming', 'sleep-curl', 'pouncing', 'sit', 'stretch']) {
    assert(!CatV2.AXIAL_POSES.has(pose), `${pose} gained axial authoring -- update this check`);
    const side = JSON.stringify(CatV2.catLayout(pose, 0.3, { view: 'side' }));
    const back = JSON.stringify(CatV2.catLayout(pose, 0.3, { view: 'back' }));
    assert(side === back, `${pose} changed with the view but has no axial drawing`);
  }
  // ...and the ones that ARE authored must actually differ, or the whole
  // feature is a no-op that every other check here would still pass.
  for (const pose of ['walking', 'idle', 'swim']) {
    const side = CatV2.catLayout(pose, 0.3, { view: 'side' });
    const back = CatV2.catLayout(pose, 0.3, { view: 'back' });
    assert(back.body.rx < side.body.rx, `${pose}: a cat seen end-on must be narrower`);
    assert(back.view === 'back' && side.view === 'side', `${pose}: the view is not recorded`);
  }
});

/** Every op one cat draws, through whichever entry point is handed in. */
function opsOf(draw) {
  const out = [];
  const ctx = new Proxy({}, {
    get: (_t, p) => (...a) => out.push([String(p), ...a.map((v) => (typeof v === 'number' ? v.toFixed(6) : String(v)))]),
    set: (_t, p, v) => { out.push(['set', String(p), String(v)]); return true; },
  });
  draw(ctx);
  return JSON.stringify(out);
}

check('a blend from a pose to ITSELF draws exactly that pose', () => {
  // The general form of a bug that hid for a year. `blendLayouts` builds a
  // fresh layout field by field, so anything it forgets to copy is gone --
  // and a missing field is not neutral. `view` was the one that bit: a
  // layout with no view is not "no view" to the painter, it is NOT BACK,
  // so every pose blend on a north-facing cat painted a full face onto the
  // back of its skull for 260ms (owner, 2026-08-13: "cat facing north,
  // with face drawn on back of head").
  //
  // Rather than list the fields, this asserts the property: a blend that
  // goes nowhere must draw what it started as. Any future field dropped
  // from the blend fails here, whatever it is.
  for (const view of ['side', 'front', 'back']) {
    // `drinking` carries the droplet and `grooming` the raised paw. Without
    // them the property held vacuously for those two fields: nothing in
    // the list set them, so dropping them from the blend changed nothing.
    for (const pose of ['walking', 'idle', 'swim', 'loaf', 'sleep-curl', 'drinking', 'grooming']) {
      const base = {
        appearance: CatV2.appearanceFor(3),
        facing: view === 'side' ? 'right' : view === 'back' ? 'north' : 'south',
        size: 120, x: 0, y: 0, layout: { view },
      };
      const plain = opsOf((ctx) => CatV2.drawCat(ctx, { ...base, pose, phase: 0.3 }));
      for (const t of [0, 0.3, 0.5, 0.7, 1]) {
        const blended = opsOf((ctx) => CatV2.drawCatTween(ctx, {
          ...base, from: pose, to: pose, t, phaseFrom: 0.3, phaseTo: 0.3, layoutFrom: base.layout,
        }));
        assert(
          plain === blended,
          `${pose}/${view} at t=${t}: a blend to the same pose changed the drawing -- ` +
            'a field the painter reads did not survive blendLayouts',
        );
      }
    }
  }
});

check('every cat draw leaves the canvas state exactly as it found it', () => {
  // This suite had 140 checks green while the body and head were INVISIBLE
  // (2026-08-13). A stray `ctx.restore()` in drawLegs popped the transform
  // paintBox had pushed, so everything drawn after the legs landed in unit
  // space at the canvas origin -- a sub-pixel speck. The legs and tail
  // survived because they draw first.
  //
  // Nothing here could see it: every check reads WHICH ops were issued,
  // and the op list was unchanged. The damage was to the ctx STATE STACK,
  // which is invisible to a mock that only logs. So this one counts.
  const depths = (draw) => {
    let depth = 0;
    let lowest = 0;
    const ctx = new Proxy({}, {
      get: (_t, p) => (...a) => {
        const op = String(p);
        if (op === 'save') depth += 1;
        if (op === 'restore') { depth -= 1; lowest = Math.min(lowest, depth); }
        if (op === 'measureText') return { width: 10 };
        return undefined;
      },
      set: () => true,
    });
    draw(ctx);
    return { depth, lowest };
  };

  const POSES = ['idle', 'walking', 'swim', 'loaf', 'sleep-curl', 'drinking',
    'eating', 'grooming', 'pouncing', 'sit', 'stretch'];
  const wasOn = CatV2.WHISKER.on;
  for (const on of [0, 1]) {
    CatV2.WHISKER.on = on;
    for (const [view, facing] of [['side', 'right'], ['side', 'left'], ['front', 'south'], ['back', 'north']]) {
      for (const pose of POSES) {
        const r = depths((ctx) => CatV2.drawCat(ctx, {
          appearance: CatV2.appearanceFor(3), facing, size: 31, x: 0, y: 0,
          pose, phase: 0.4, layout: { view },
        }));
        assert(r.depth === 0,
          `${pose}/${view}${on ? ' (whiskers on)' : ''} left the ctx stack at ${r.depth}, not 0`);
        assert(r.lowest >= 0,
          `${pose}/${view}${on ? ' (whiskers on)' : ''} restored past its own saves -- ` +
            'it is popping state the CALLER pushed, and everything after it draws in the wrong space');
      }
    }
  }
  // The blend path too: it wraps the draw in its own save for the settle.
  const t = depths((ctx) => CatV2.drawCatTween(ctx, {
    appearance: CatV2.appearanceFor(3), facing: 'right', size: 31, x: 0, y: 0,
    from: 'walking', to: 'idle', t: 0.5, phaseFrom: 0.3, phaseTo: 0.3,
  }));
  CatV2.WHISKER.on = wasOn;
  assert(t.depth === 0 && t.lowest >= 0, `a blended draw left the ctx stack at ${t.depth}`);
});

check('whiskers ship OFF, and a cat walking away never grows any', () => {
  // Attempt three (2026-08-13), ported from kitten.me. Off until judged --
  // the first two were built and cut, and BACKLOG records that cutting
  // again is an acceptable outcome.
  // This asserted whiskers shipped OFF, which was the point while they were
  // unjudged. The owner turned them on (2026-08-13) after two previous
  // attempts were cut, so the guard is retired and what replaces it pins
  // the DECISION rather than the number: they ship, and going back to no
  // whiskers is a third cut, not a tweak.
  assert(CatV2.WHISKER.on > 0, 'whiskers ship on; turning them off is a decision, not a tweak');
  assert(CatV2.WHISKER.alpha < 1,
    'the whole technique is a hairline at reduced opacity -- at full alpha it is the aliased line that was cut twice');

  const strokes = (on, size, view, facing) => {
    const was = CatV2.WHISKER.on;
    CatV2.WHISKER.on = on;
    const out = [];
    const ctx = new Proxy({}, {
      get: (_t, p) => (...a) => out.push(String(p)),
      set: () => true,
    });
    CatV2.drawCat(ctx, {
      appearance: CatV2.appearanceFor(3), facing, size, x: 0, y: 0,
      pose: 'idle', phase: 0.3, layout: { view },
    });
    CatV2.WHISKER.on = was;
    return out.filter((c) => c === 'stroke').length;
  };

  // Head-on, both fans draw. Side-on the rearward one is buried in the
  // skull by our muzzle offset, so `back` ships at 0 and that fan is
  // skipped rather than drawn at zero length.
  const per = CatV2.WHISKER.count;
  const want = { side: CatV2.WHISKER.back > 0 ? per * 2 : per, front: per * 2 };
  for (const [view, facing] of [['side', 'right'], ['front', 'south']]) {
    const got = strokes(1, 31, view, facing) - strokes(0, 31, view, facing);
    assert(got === want[view], `${view}: expected ${want[view]} whisker strokes, got ${got}`);
  }
  // The rule that costs nothing because of WHERE they are drawn: a cat
  // walking away has no face, so it has no whiskers, and drawWhiskers
  // never has to know that rule exists.
  assert(
    strokes(1, 31, 'back', 'north') === strokes(0, 31, 'back', 'north'),
    'a cat walking away grew whiskers on the back of its head',
  );
});

check('darkening the nose takes the whole muzzle with it', () => {
  // Owner's ask, 2026-08-13: three hairlines either side of the muzzle
  // pull the eye off a pale pink nose, so the nose wants its own darkness
  // dial to hold the middle of the face.
  //
  // The trap is that the nose is not one colour. The yawn's jaw is
  // `shadeHex(nose, 0.5)` and the tongue is `lightenHex(nose, 0.22)`, both
  // mixed from the same source -- so darkening only the triangle would put
  // a pale mouth inside a dark muzzle the moment a cat yawns.
  const yawning = { ...CatV2.stillRig({ facing: 'right', gazeX: 0.1 }), yawn: 1 };
  const inks = (darken) => {
    const was = CatV2.NOSE.darken;
    CatV2.NOSE.darken = darken;
    const out = [];
    // Recorded at each `fill()`, not at each `fillStyle =`: the two inner
    // ears are painted from a SINGLE assignment, so counting assignments
    // counts one ear and cannot tell a pair from a single.
    let ink = null;
    const ctx = new Proxy({}, {
      get: (_t, p) => () => { if (String(p) === 'fill') out.push(ink); },
      set: (_t, p, v) => { if (String(p) === 'fillStyle') ink = v; return true; },
    });
    CatV2.drawCat(ctx, {
      pose: 'resting', appearance: CatV2.appearanceFor(3),
      facing: 'right', size: 31, rig: yawning,
    });
    CatV2.NOSE.darken = was;
    return out;
  };

  // 0 is neutral, whatever the shipped value happens to be: the dial has
  // to be able to mean "leave the colorway alone" exactly, or a colorway
  // can never be seen as it was authored.
  assert(CatV2.noseInkOf({ noseColor: '#abcdef' }) !== '#abcdef' || CatV2.NOSE.darken === 0,
    'sanity: noseInkOf disagrees with NOSE.darken');
  // Owner's call, 2026-08-13: a touch off the authored pink, because the
  // whiskers widened and took the eye with them. The VALUE is hers to
  // re-bake; what is pinned is that a call was made, so a revert to
  // neutral is loud rather than silent.
  assert(CatV2.NOSE.darken > 0, 'the nose is back to the raw authored pink -- an owner bake was reverted');
  const wasDark = CatV2.NOSE.darken;
  CatV2.NOSE.darken = 0;
  assert(CatV2.noseInkOf({ noseColor: '#abcdef' }) === '#abcdef',
    'at darken 0 the ink is not the authored colour');
  CatV2.NOSE.darken = wasDark;
  const authored = CatV2.appearanceFor(3).noseColor;
  const plain = inks(0);
  assert(plain.includes(authored), 'the yawning cat did not paint its authored nose colour at all');

  const dark = inks(0.6);
  assert(dark.length === plain.length, 'darkening the nose changed how many shapes the cat paints');
  const lum = (hex) => {
    const n = parseInt(hex.slice(1), 16);
    return (n >> 16) + ((n >> 8) & 255) + (n & 255);
  };
  // Compared SLOT BY SLOT against the same drawing undarkened, so this
  // reads off the paint rather than restating the mix -- the whisker width
  // check first passed while the code multiplied instead of dividing,
  // because it asserted its own arithmetic.
  const moved = plain.map((c, i) => [c, dark[i]]).filter(([a, b]) => a !== b);
  assert(moved.length === 5,
    'expected the nose, the yawn\'s jaw, the tongue and BOTH inner ears to move, ' +
    `${moved.length} fills did`);
  for (const [was, now] of moved) {
    assert(lum(now) < lum(was), `${was} -> ${now} is not darker`);
  }
  // Nothing anywhere is still wearing the authored pink, which is the
  // whole claim: the nose and the ears share one colour, so a site that
  // quietly ignored the dial would leave that colour on the canvas while
  // every other site moved.
  assert(!dark.includes(authored),
    `${authored} is still on the canvas at darken 0.6 -- some site is not going through noseInkOf`);

  // The inner ears were left out on the first cut and the owner's read was
  // that the face then disagreed with itself. They paint from `noseColor`,
  // so they are the same pink and they follow.
  const ears = inks(1).filter((c) => c === '#000000').length;
  assert(ears >= 3, 'at full darkness the nose, the ears and the mouth should all be black');
});

check('the whisker stroke is a PIXEL floor, not a unit one', () => {
  // The trap this file already recorded once: the drawing runs in unit
  // space, where a lineWidth of 0.8 is most of a cat. The floor is only
  // meaningful in real pixels, which is why `size` is threaded down to the
  // face at all.
  //
  // Read off the DRAWING, not recomputed here. The first version of this
  // check restated `max(widthPx/size, widthOfCat)` and then asserted its
  // own arithmetic, so it passed happily while the code multiplied instead
  // of dividing -- which is a whisker 25 times too thick.
  const W = CatV2.WHISKER;
  const drawnPx = (size, count = W.count) => {
    const was = { on: W.on, count: W.count };
    W.on = 1; W.count = count;
    let width = null;
    let strokes = 0;
    const ctx = new Proxy({}, {
      get: (_t, p) => (...a) => { if (String(p) === 'stroke') strokes++; return undefined; },
      set: (_t, p, v) => { if (String(p) === 'lineWidth') width = v; return true; },
    });
    // Head-on, where BOTH fans draw whatever `back` is set to.
    CatV2.drawWhiskers(ctx, { cx: 0.5, cy: 0.4, r: 0.226 }, CatV2.appearanceFor(3), 'front', size);
    W.on = was.on; W.count = was.count;
    return { px: width * size, strokes };
  };

  assert(Math.abs(drawnPx(31).px - W.widthPx) < 1e-9,
    `at 31px the stroke draws at ${drawnPx(31).px.toFixed(3)}px, want the ${W.widthPx}px floor`);
  assert(Math.abs(drawnPx(44).px - W.widthPx) < 1e-9, 'at 44px it should still be on the floor -- kitten.me is too');
  assert(drawnPx(60).px > W.widthPx, 'at a 60px tile it must finally clear the floor, or camera mode buys nothing');
  // The floor really is in pixels: a smaller cat must not get a thinner one.
  assert(Math.abs(drawnPx(22).px - drawnPx(31).px) < 1e-9,
    'the stroke scales with the cat while clamped, so it is not a floor');
  // ...and above the floor it does scale, or `widthOfCat` is decoration.
  assert(drawnPx(120).px > drawnPx(60).px, 'past the floor the stroke stops growing with the cat');

  // The count is a dial, not a number written twice.
  assert(drawnPx(31, 2).strokes === 4, `count 2 drew ${drawnPx(31, 2).strokes} strokes, want 4`);
  assert(drawnPx(31, 5).strokes === 10, `count 5 drew ${drawnPx(31, 5).strokes} strokes, want 10`);

  // Side-on, the fan sweeping BACK along the cheek is shorter than the one
  // sweeping forward off the muzzle -- it is pointing away from the camera.
  // The same argument the swim tail's foreshortening allowance is built on.
  // Read off the drawn segments, not off `W.back`.
  const spans = (view, back = W.back) => {
    const was = { on: W.on, back: W.back };
    W.on = 1; W.back = back;
    const segs = []; let from = null;
    const ctx = new Proxy({}, {
      get: (_t, p) => (...a) => {
        if (String(p) === 'moveTo') from = a;
        if (String(p) === 'lineTo' && from) segs.push(a[0] - from[0]);
        return undefined;
      },
      set: () => true,
    });
    CatV2.drawWhiskers(ctx, { cx: 0.5, cy: 0.4, r: 0.226 }, CatV2.appearanceFor(3), view, 31);
    W.on = was.on; W.back = was.back;
    return {
      forward: Math.max(...segs.filter((d) => d > 0)),
      back: Math.abs(Math.min(...segs.filter((d) => d < 0))),
    };
  };
  // `back` shipped at 0 while our muzzle offset buried the rearward fan.
  // The owner's longer `tipX` reaches past the skull, so it is dialled up
  // now -- that guard is retired rather than held. What survives is the
  // mechanism: when `back` is under 1 the rearward fan is SHORTER, because
  // it points away from the camera. Dialled here rather than read off the
  // shipped value, so a re-dial cannot make this vacuous.
  const sideOn = spans('side', 0.5);
  assert(
    sideOn.back < sideOn.forward - 1e-9,
    `dialled to 0.5, the rearward fan spans ${sideOn.back.toFixed(4)} against the forward ` +
      `${sideOn.forward.toFixed(4)} -- it cannot be as long`,
  );
  // The FORWARD fan has to clear the head: it is the one that changes the
  // cat's silhouette, and it must hold at any dial. Note what this does
  // NOT claim -- the rearward fan lies almost entirely against fur and the
  // owner's read is that it carries there, so clearance is a property of
  // the forward fan alone and not a visibility test for whiskers.
  const head = { cx: 0.72, cy: 0.399, r: 0.226 };
  const tips = [];
  const probe = new Proxy({}, {
    get: (_t, p) => (...a) => { if (String(p) === 'lineTo') tips.push(a[0]); },
    set: () => true,
  });
  const wasOn = W.on; W.on = 1;
  CatV2.drawWhiskers(probe, head, CatV2.appearanceFor(3), 'side', 31);
  W.on = wasOn;
  const past = (Math.max(...tips) - (head.cx + head.r)) * 31;
  assert(past > 2, `the forward fan clears the head by ${past.toFixed(2)}px -- it needs to read against grass, not fur`);
  // Head-on there is no near and no far, so both fans match.
  const front = spans('front');
  assert(
    Math.abs(front.back - front.forward) < 1e-9,
    'head-on the two fans must match -- neither side is further away',
  );
});

check('a turn only flips a facing that has something to flip through', () => {
  // `turnFacing` draws the PRE-turn facing for the first half of a turn,
  // which is what makes the flip land on the squash. It does that with a
  // left/right ternary, and it has been taking four values since the axial
  // facings landed: 'north' is not 'left', so it came back as 'left' and
  // an axial cat was drawn side-on for 100ms and then snapped.
  //
  // Unreachable today -- a turn is only stamped on a horizontal step, so
  // the facing is horizontal for the 200ms it lasts -- so this pins the
  // behaviour before something makes it reachable, rather than after.
  for (const facing of ['north', 'south']) {
    for (const t of [0, 0.1, 0.49, 0.5, 0.9, 1]) {
      assert(
        CatV2.turnFacing(facing, t) === facing,
        `a ${facing}-facing cat was drawn as '${CatV2.turnFacing(facing, t)}' at turn ${t}`,
      );
    }
  }
  // ...while the horizontal case still does the thing it exists for: the
  // old facing until the flip point, the new one after.
  assert(CatV2.turnFacing('right', 0.1) === 'left', 'a turn must show the pre-turn facing first');
  assert(CatV2.turnFacing('right', 0.9) === 'right', 'and the served one after the flip');
  assert(CatV2.turnFacing('left', 0.1) === 'right', 'both ways');
  assert(CatV2.turnFacing('left', null) === 'left', 'no turn, no change');
});

check('four facings come off the served step, and east/west is remembered', () => {
  const p = new api.Presentation();
  const step = (from, to) => {
    const q = new api.Presentation();
    q.pushState(world(1, [kitty(1, from.x, from.y)]), 1000);
    q.pushState(world(2, [kitty(1, to.x, to.y)]), 1800);
    return q;
  };
  assert(step({ x: 5, y: 5 }, { x: 6, y: 5 }).facingFor(1) === 'right', 'east');
  assert(step({ x: 5, y: 5 }, { x: 4, y: 5 }).facingFor(1) === 'left', 'west');
  assert(step({ x: 5, y: 5 }, { x: 5, y: 6 }).facingFor(1) === 'south', 'south');
  assert(step({ x: 5, y: 5 }, { x: 5, y: 4 }).facingFor(1) === 'north', 'north');
  // The engine moves cats on four axes only, so a diagonal is a guard
  // rather than a rule -- but the guard must still answer something drawable.
  const diag = step({ x: 5, y: 5 }, { x: 6, y: 6 });
  assert(
    ['right', 'left', 'north', 'south'].includes(diag.facingFor(1)),
    'a diagonal must still resolve to a drawable facing',
  );
  // A cat that walks north and then grooms is drawn side-on, and should
  // face the way it last plausibly did rather than snapping to a default.
  p.pushState(world(1, [kitty(1, 5, 5)]), 1000);
  p.pushState(world(2, [kitty(1, 4, 5)]), 1800); // west
  assert(p.sideFacingFor(1) === 'left', 'the side facing is the last east/west step');
  p.pushState(world(3, [kitty(1, 4, 4)]), 2600); // then north
  assert(p.facingFor(1) === 'north', 'now facing north');
  assert(p.sideFacingFor(1) === 'left', 'but the remembered side facing is unchanged');
});

check('every cat-v2 symbol the page reads bare is actually installed', () => {
  // The trap that swallowed two features before anyone noticed.
  //
  // cat-v2.js leaks its api onto globalThis only in DROP-IN mode
  // (`if (typeof globalThis.drawCat === 'undefined')`). Every lab loads
  // cat-v2 WITHOUT cat.js, so drop-in runs and every symbol is global
  // there. index.html loads cat.js FIRST, so it never runs, and each
  // symbol has to be installed by hand.
  //
  // render.js reads several of them bare and DEFENSIVELY -- `typeof
  // AXIAL_POSES !== 'undefined'`, `typeof turnFacing === 'function'` -- so
  // a missing one throws nothing. It just silently does nothing, in the
  // browser only. `turnFacing` had been missing since the turn shipped;
  // `AXIAL_POSES` would have shipped the entire north/south feature inert.
  //
  // This harness cannot catch it by running the code, because it evals
  // every file into ONE scope where the names are simply in scope. So the
  // check is on the SOURCES: what does the page install, and what do the
  // page's other scripts ask for?
  const html = readFileSync(join(here, 'index.html'), 'utf8');
  const v1 = readFileSync(join(here, 'cat.js'), 'utf8');
  const exportBlock = catV2Src.match(/const api = \{([\s\S]*?)\n\};/);
  assert(exportBlock, "could not find cat-v2's api export block");
  const exported = [...exportBlock[1].matchAll(/^\s{2}([A-Za-z_$][\w$]*)[,:]/gm)].map((m) => m[1]);
  assert(exported.length > 20, `only found ${exported.length} exports -- the parse broke`);

  // Whole-namespace install counts for everything; otherwise look for the
  // symbol being assigned by name.
  const blanket = /Object\.assign\(window, CatV2\)/.test(html);
  // Comments stripped first: this file talks about its own dials by name
  // ("mutable for a lab like SWIM/GAIT/EYE"), and matching prose would
  // report a symbol as missing that nothing actually reads.
  const code = (src) => src.replace(/\/\*[\s\S]*?\*\//g, ' ').replace(/^\s*\/\/.*$/gm, ' ');
  const consumers = {
    'render.js': code(renderSrc),
    'app.js': code(readFileSync(join(here, 'app.js'), 'utf8')),
  };
  const missing = [];
  for (const name of exported) {
    // Only care about symbols the page's own scripts actually reference
    // bare -- `CatV2.foo` is always fine, and so is anything cat.js
    // already defines at top level.
    const bare = new RegExp(`(^|[^.\\w])${name}\\s*[({.\\[]`);
    const used = Object.entries(consumers).filter(([, src]) => bare.test(src)).map(([f]) => f);
    if (!used.length) continue;
    if (new RegExp(`(function|const|let|var)\\s+${name}\\b`).test(v1)) continue; // cat.js provides it
    const named = new RegExp(`window\\.${name}\\s*=`).test(html);
    if (!blanket && !named) missing.push(`${name} (read by ${used.join(', ')})`);
  }
  assert(
    missing.length === 0,
    `index.html never installs: ${missing.join('; ')} -- these are undefined in the BROWSER only`,
  );
  // And the overdraw wrappers must be re-applied AFTER any blanket assign,
  // or the plain versions win and every cat loses its 5% overdraw.
  if (blanket) {
    const assignAt = html.indexOf('Object.assign(window, CatV2)');
    for (const wrapped of ['drawCat', 'drawCatTween']) {
      const at = html.indexOf(`window.${wrapped} = (ctx, opts) =>`);
      assert(at > assignAt, `window.${wrapped} is assigned BEFORE the namespace and gets clobbered`);
    }
  }
});

check('card text keeps its contrast THROUGH a phase change, not just at the ends', () => {
  // Owner, live: the card text became hard to read during transitions.
  // Ink and card both INVERT into night, and both were interpolated
  // linearly, so they walked toward each other and met -- 1.17:1 at the
  // midpoint, invisible, for most of the crossfade. Every existing check
  // looked at settled phases, where it reads perfectly.
  const themes = {
    dusk: { ink: '#6b5a4e', soft: '#9c8a7c', card: '#fdf3e6' },
    night: { ink: '#ece3d4', soft: '#b3a798', card: '#37313f' },
    dawn: { ink: '#6b5a4e', soft: '#9c8a7c', card: '#f2f1ec' },
  };
  const hex = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
  const lin = (c) => (c / 255 <= 0.04045 ? c / 255 / 12.92 : ((c / 255 + 0.055) / 1.055) ** 2.4);
  const lum = (c) => 0.2126 * lin(c[0]) + 0.7152 * lin(c[1]) + 0.0722 * lin(c[2]);
  const ratio = (a, b) => {
    const [x, y] = [lum(a) + 0.05, lum(b) + 0.05];
    return x > y ? x / y : y / x;
  };
  // The shipped rule: these tokens SWAP at the halfway mark rather than
  // blending, so at any blend position the pair is one theme's or the
  // other's -- never a mix of both.
  const swap = (a, b, t) => (t < 0.5 ? a : b);
  assert(/INVERTING_TOKENS/.test(appSrc), 'app.js no longer names the inverting tokens');
  assert(
    /blend\.step < 0\.5 \? from\[name\] : to\[name\]/.test(appSrc),
    'the inverting tokens are being blended again -- ink and card will meet in the middle',
  );
  for (const [from, to] of [['dusk', 'night'], ['night', 'dawn']]) {
    for (const t of [0, 0.2, 0.35, 0.49, 0.51, 0.65, 0.8, 1]) {
      const ink = hex(swap(themes[from].ink, themes[to].ink, t));
      const soft = hex(swap(themes[from].soft, themes[to].soft, t));
      const card = hex(swap(themes[from].card, themes[to].card, t));
      const r = ratio(card, ink);
      assert(r >= 4.5, `${from}->${to} @${t}: card text at ${r.toFixed(2)}:1, under the 4.5:1 floor`);
      // The muted line is smaller and greyer; hold it to the large-text bar.
      const rs = ratio(card, soft);
      assert(rs >= 2.9, `${from}->${to} @${t}: muted text at ${rs.toFixed(2)}:1`);
    }
  }
});

// ---- the delay line (2026-08-11) ----
//
// Owner: "a tiny hiccup at the end/beginning of motion between squares",
// worst north/south, not consistent. Mechanism: a pair used to play over
// the SERVED tick from the moment it landed, so any arrival that ran late
// left the cat parked on its tile until the next one came. The pacer holds
// a buffer and pays states out on its own clock instead.
//
// Everything below drives the real classes with an arrival series -- no
// socket, no frames -- because the whole bug lives in the gap between when
// states arrive and when they are drawn.

/** A cat walking due east, one tile per tick. Never wraps, so never teleports. */
const feedWorld = (tick) => ({
  tick,
  width: 64,
  height: 64,
  elements: [],
  kitties: [{ id: 1, name: 'K', pos: { x: tick, y: 5 }, needs: {}, happiness: 90 }],
});

/** Deterministic jitter -- a seeded LCG, so a failure is reproducible. */
function jitter(seed) {
  let s = seed;
  return (spread) => {
    s = (s * 1103515245 + 12345) & 0x7fffffff;
    return (s / 0x7fffffff - 0.5) * 2 * spread;
  };
}

/**
 * Drive the pacer and the store the way the browser does: arrivals on one
 * clock, frames on another. `paced: false` is the OLD path -- push on
 * arrival, play over the served tick -- kept as the control, because every
 * claim below is only worth making if the previous code fails it.
 */
function runFeed({ arrivals, frameMs = 16, untilMs, dials = api.VIEW, paced = true, tickMs }) {
  const pacer = new api.Pacer(dials);
  const store = new api.Presentation();
  if (tickMs) { pacer.setTickMs(tickMs); store.tickMs = tickMs; }
  const samples = [];
  const promoted = [];
  let next = 0;
  // The real wiring, on the harness's clock: `pump` is what the rAF
  // callback calls, so the promotion order is the page's own and not a
  // second copy of it living in this file.
  const wiring = Object.create(api.anim);
  wiring.presentation = store;
  wiring.pacer = pacer;
  wiring.onPromote = (world) => promoted.push({ tick: world.tick, at: wiring.at });
  let snaps = 0;
  const countSnaps = () => { snaps += 1; };
  for (let now = 0; now <= untilMs; now += frameMs) {
    while (next < arrivals.length && arrivals[next].at <= now) {
      const { world } = arrivals[next];
      if (paced) pacer.enqueue(world);
      else {
        store.pushState(world, now, store.tickMs);
        promoted.push({ tick: world.tick, at: now });
      }
      next += 1;
    }
    if (paced) {
      wiring.at = now;
      const before = store.generation;
      wiring.pump(now);
      if (store.generation !== before) countSnaps();
    }
    if (!store.curr) continue;
    samples.push({
      now,
      tick: store.curr.tick,
      progress: store.progress(now),
      stalled: !store.discontinuous && store.progress(now) >= 1,
      playMs: store.currPlayMs,
    });
  }
  return { samples, promoted, snaps, pacer, store };
}

/** Regular arrivals, plus whatever jitter the caller wants on top. */
function series(count, periodMs, spreadMs = 0, seed = 7) {
  const noise = jitter(seed);
  const out = [];
  for (let i = 1; i <= count; i += 1) {
    out.push({ at: Math.max(0, i * periodMs + (spreadMs ? noise(spreadMs) : 0)), world: feedWorld(i) });
  }
  return out.sort((a, b) => a.at - b.at);
}

/** Frames spent parked on a tile with nowhere to go, after the pace settles. */
const stallFrames = (samples, fromMs) =>
  samples.filter((s) => s.now >= fromMs && s.stalled).length;

check('the delay line absorbs the jitter that used to park cats on a tile', () => {
  // The headline. Arrivals wander +/-60ms around an 800ms tick, which is
  // an ordinary link, not a bad one.
  const arrivals = series(40, 800, 60);
  const settled = 8000; // give the pace a few states to find the rate

  const control = runFeed({ arrivals, untilMs: 33000, paced: false });
  const parked = stallFrames(control.samples, settled);
  assert(parked > 0, 'the control must reproduce the bug, or this test proves nothing');

  const paced = runFeed({ arrivals, untilMs: 33000 });
  assert(
    stallFrames(paced.samples, settled) === 0,
    `paced feed still parked cats for ${stallFrames(paced.samples, settled)} frames ` +
      `(control ${parked})`,
  );
});

check('two states landing together are paid out, not shown for no time at all', () => {
  // The other half of the same bug, and the bigger one on screen: a
  // stuttered frame lands two messages at once, the first is superseded
  // before it is ever drawn, and a cat crosses a whole tile instantly.
  const arrivals = series(12, 800);
  // Tick 6 arrives with tick 5 rather than 800ms later.
  arrivals[5].at = arrivals[4].at;

  const control = runFeed({ arrivals, untilMs: 12000, paced: false });
  const c5 = control.promoted.find((p) => p.tick === 5);
  const c6 = control.promoted.find((p) => p.tick === 6);
  assert(c6.at - c5.at === 0, 'the control must show the doubled arrival, or this proves nothing');

  const paced = runFeed({ arrivals, untilMs: 12000 });
  const p5 = paced.promoted.find((p) => p.tick === 5);
  const p6 = paced.promoted.find((p) => p.tick === 6);
  assert(p5 && p6, 'a doubled arrival must not drop either state');
  assert(
    p6.at - p5.at >= api.VIEW.tickMsFallback * api.VIEW.paceRateMin,
    `a doubled arrival crossed a tile in ${p6.at - p5.at}ms`,
  );
  assert(paced.snaps === 0, 'two states at once is a stutter, not a backlog');
});

check('the pace follows the server that is actually ticking, not its config', () => {
  // The pacer measures its own promotion interval, and in the long run
  // that cannot be anything but the rate states are produced at. So a box
  // whose real tick differs from the tick_ms it serves is absorbed rather
  // than stalled against -- which the old fixed clock could not do at all.
  for (const realPeriod of [1000, 650]) {
    const arrivals = series(60, realPeriod, 25);
    const untilMs = realPeriod * 62;
    const paced = runFeed({ arrivals, untilMs });
    const settled = realPeriod * 20;

    const drift = Math.abs(paced.pacer.playMs - realPeriod) / realPeriod;
    assert(drift < 0.08, `at a real ${realPeriod}ms tick the pace settled at ${paced.pacer.playMs.toFixed(0)}ms`);
    assert(
      stallFrames(paced.samples, settled) === 0,
      `a ${realPeriod}ms server still parked cats ${stallFrames(paced.samples, settled)} frames`,
    );
    assert(paced.snaps === 0, `a steady ${realPeriod}ms server must never look like a backlog`);
    // And nothing may be lost on the way there.
    assert(
      paced.promoted.length >= 55,
      `only ${paced.promoted.length} of 60 states were ever shown at ${realPeriod}ms`,
    );
  }
});

check('the play clock is frozen for its segment, so no cat steps backwards', () => {
  // progress divides by this every frame. A denominator that moved under a
  // running tick would run progress BACKWARDS, so the pace a pair plays at
  // is stamped when it lands and never read live.
  const store = new api.Presentation();
  store.tickMs = 800;
  store.pushState(feedWorld(1), 0, 1000);
  store.pushState(feedWorld(2), 1000, 1000);
  assert(
    Math.abs(store.progress(1500) - 0.5) < 1e-9,
    `a pair handed a 1000ms pace read ${store.progress(1500)} at its halfway point ` +
      '(0.625 means progress is still dividing by the served tick)',
  );

  // And on a live jittery feed, where the pacer really is moving its clock
  // about: progress may never fall while the pair on screen is unchanged.
  const paced = runFeed({ arrivals: series(40, 800, 90), untilMs: 33000 });
  for (let i = 1; i < paced.samples.length; i += 1) {
    const a = paced.samples[i - 1];
    const b = paced.samples[i];
    if (a.tick !== b.tick) continue;
    assert(b.progress >= a.progress, `progress fell from ${a.progress} to ${b.progress} within tick ${b.tick}`);
  }
});

check('velocity is the derivative of the drawn motion, at whatever pace it plays', () => {
  // The rig lags the body, so the speed it lags must be the speed the cat
  // is actually travelling -- the paced one, not the served tick.
  const store = new api.Presentation();
  store.tickMs = 800;
  for (let t = 1; t <= 3; t += 1) store.pushState(feedWorld(t), (t - 1) * 1000, 1000);
  const at = 1400;
  const step = 1;
  const drawn = (now) => store.posFor(store.curr.kitties[0], now);
  const numeric = ((drawn(at + step).x - drawn(at - step).x) / (2 * step)) * 1000;
  const analytic = store.velocityFor(1, at).x;
  assert(
    Math.abs(numeric - analytic) < 1e-6,
    `velocity says ${analytic.toFixed(4)} tiles/s, the drawing moves at ${numeric.toFixed(4)} ` +
      '(1.25x out means it is still dividing by the served tick)',
  );
});

check('a backlog collapses to one state, and a stutter never does', () => {
  // Coming back to a tab left for hours: ~9,000 states arrive at once.
  // Easing across two hours is a lie at any pace, so this one snaps.
  const pacer = new api.Pacer();
  const store = new api.Presentation();
  for (let t = 1; t <= 9000; t += 1) pacer.enqueue(feedWorld(t));
  const { worlds, snap } = pacer.due(0);
  assert(worlds.length === 1, `9000 queued states became ${worlds.length} promotions, want 1`);
  assert(worlds[0].tick === 9000, `caught up to tick ${worlds[0].tick}, want the newest`);
  assert(snap, 'a collapsed backlog must break continuity so the world SNAPS across the gap');

  // The snap has to reach the store BEFORE the state does -- `pushState`
  // decides continuity as it lands -- so this drives the real `pump`
  // rather than restating its order here.
  const wiring = Object.create(api.anim);
  wiring.presentation = store;
  wiring.pacer = new api.Pacer();
  store.pushState(feedWorld(1), 0);
  for (let t = 2; t <= 9000; t += 1) wiring.pacer.enqueue(feedWorld(t));
  wiring.pump(0);
  assert(store.curr.tick === 9000, `pump promoted tick ${store.curr.tick}, want the newest`);
  assert(store.discontinuous, 'the collapsed state must land as a new moment, not an 8999-tile step');

  // ...and the state AFTER it must land normally. This is what pins the
  // ORDER rather than the fact of the bump: a generation raised after the
  // promotion instead of before is invisible here (the tick jump alone
  // already breaks continuity) and then snaps the next, innocent pair.
  wiring.pacer.enqueue(feedWorld(9001));
  wiring.pump(5000);
  assert(store.curr.tick === 9001, `the state after a collapse never landed (got ${store.curr.tick})`);
  assert(
    !store.discontinuous,
    'the pair after a collapsed backlog snapped -- the generation was raised after the promotion, not before',
  );

  // Exactly the ceiling is a buffer, not a backlog: nothing is dropped and
  // nothing snaps.
  const easy = new api.Pacer();
  for (let t = 1; t <= api.VIEW.paceMaxBacklog; t += 1) easy.enqueue(feedWorld(t));
  const out = [];
  for (let now = 0; now <= 20000; now += 16) {
    const due = easy.due(now);
    assert(!due.snap, `${api.VIEW.paceMaxBacklog} pending states is a buffer, not a backlog`);
    out.push(...due.worlds.map((w) => w.tick));
  }
  assert(
    String(out) === String(Array.from({ length: api.VIEW.paceMaxBacklog }, (_, i) => i + 1)),
    `a full buffer replayed as ${out}`,
  );
});

check('ordinary running shows every state, in order, exactly once', () => {
  const paced = runFeed({ arrivals: series(30, 800, 40), untilMs: 30000 });
  const ticks = paced.promoted.map((p) => p.tick);
  assert(paced.snaps === 0, 'an ordinary feed must never snap');
  assert(
    String(ticks) === String(Array.from({ length: ticks.length }, (_, i) => i + 1)),
    `states were dropped or reordered: ${ticks}`,
  );
  assert(ticks.length >= 26, `only ${ticks.length} of 30 states were shown in 30s`);
});

check('a differently-paced box is reseeded, not walked to', () => {
  // /config lands within the first second and may say 80ms (the fast
  // server used to judge the time-of-day changes). The pace is clamped to
  // a band around the SERVED tick, so a pacer left seeded at 800 cannot
  // play an 80ms feed at all: it drips one state per 400ms, the rest pile
  // up, and the world snaps through a backlog collapse over and over.
  const arrivals = series(120, 80, 6);
  const stale = runFeed({ arrivals, frameMs: 8, untilMs: 11000 });
  assert(stale.snaps > 0, 'a stale seed must actually break, or reseeding proves nothing');

  const reseeded = runFeed({ arrivals, frameMs: 8, untilMs: 11000, tickMs: 80 });
  assert(reseeded.snaps === 0, `a reseeded pacer still snapped ${reseeded.snaps} times on an 80ms feed`);
  assert(
    reseeded.promoted.length >= 110,
    `only ${reseeded.promoted.length} of 120 states were shown on an 80ms feed`,
  );

  // And the wiring actually calls it: `anim.setTickMs` owns both clocks.
  const wiring = Object.create(api.anim);
  wiring.presentation = new api.Presentation();
  wiring.pacer = new api.Pacer();
  wiring.setTickMs(80);
  assert(wiring.presentation.tickMs === 80, 'setTickMs did not reach the store');
  assert(wiring.pacer.tickMs === 80 && wiring.pacer.playMs === 80, 'setTickMs did not reach the pacer');
});

/**
 * `anim.push` and `anim.setPaced` are the parts of the delay line that read
 * the DOM, and exactly where a silent failure would live: get the branching
 * wrong and the page shows NOTHING with every other check still green. So
 * they get just enough of a document to run against.
 */
function withDom(fn) {
  const env = { hidden: false, clock: 0 };
  const saved = {
    document: globalThis.document,
    performance: globalThis.performance,
    requestAnimationFrame: globalThis.requestAnimationFrame,
  };
  globalThis.document = { get hidden() { return env.hidden; } };
  globalThis.performance = { now: () => env.clock };
  globalThis.requestAnimationFrame = () => 1;
  env.fresh = () => {
    const a = Object.create(api.anim);
    a.presentation = new api.Presentation();
    a.pacer = new api.Pacer();
    a.seen = [];
    a.onPromote = (w) => a.seen.push(w.tick);
    a.renderer = { draw() {} };
    return a;
  };
  try {
    return fn(env);
  } finally {
    for (const [k, v] of Object.entries(saved)) {
      if (v === undefined) delete globalThis[k];
      else globalThis[k] = v;
    }
  }
}

check('every way a state reaches the screen still reaches it', () => {
  withDom((env) => {
    const at = (ms) => { env.clock = ms; };

    // The first state has no predecessor to ease from, so it must not sit
    // in the buffer -- the panel would be empty until the second tick.
    let a = env.fresh();
    at(0); a.push(feedWorld(1));
    assert(a.seen.join() === '1', `the first state did not reach the screen (saw ${a.seen})`);
    at(100); a.push(feedWorld(2));
    assert(a.seen.join() === '1', 'the second state jumped the queue instead of waiting for its beat');
    at(900); a.pump(900);
    assert(a.seen.join() === '1,2', `the second state never landed (saw ${a.seen})`);

    // Reduced motion runs no frame loop, so nothing would ever pump the
    // buffer: these have to go straight through or the world freezes.
    a = env.fresh();
    a.reduced = true;
    for (const t of [1, 2, 3]) { at(t * 50); a.push(feedWorld(t)); }
    assert(a.seen.join() === '1,2,3', `reduced motion stopped showing states (saw ${a.seen})`);

    // A hidden tab banks arrivals and does no DOM work at all -- that was
    // the "it replays every tick very quickly" fix, and it still holds.
    a = env.fresh();
    at(0); a.push(feedWorld(1));
    env.hidden = true;
    for (let t = 2; t <= 9000; t += 1) { at(t); a.push(feedWorld(t)); }
    assert(a.seen.join() === '1', `a hidden tab rendered ${a.seen.length} states`);
    env.hidden = false;
    at(20000); a.pump(20000);
    assert(a.seen.join() === '1,9000', `the return did not collapse to the newest (saw ${a.seen})`);
    assert(a.presentation.discontinuous, 'the return must snap, not ease across the gap');
  });
});

check('the delay line can be switched off, and is on until it is', () => {
  // For driving a world far faster than production -- flicking through a
  // day to judge the crossfades. At a tick shorter than a frame no pace
  // helps (two states cannot both be drawn in one frame), so the buffer
  // would be latency and nothing else.
  withDom((env) => {
    const at = (ms) => { env.clock = ms; };
    assert(api.anim.paced === true, 'the delay line must be ON by default');

    const a = env.fresh();
    at(0); a.push(feedWorld(1)); // the first state is unpaced either way
    at(100); a.push(feedWorld(2));
    assert(a.seen.join() === '1', 'guard: the second state should be buffered while paced');

    // Switching off must not strand what is already buffered.
    a.setPaced(false);
    assert(a.seen.join() === '1,2', `switching off lost a buffered state (saw ${a.seen})`);
    assert(!a.paced, 'setPaced(false) did not take');

    // ...and from then on every state draws as it lands, over the SERVED
    // tick -- exactly the behaviour that shipped before the pacer.
    for (const t of [3, 4, 5]) { at(100 + t); a.push(feedWorld(t)); }
    assert(a.seen.join() === '1,2,3,4,5', `unpaced states did not draw as they landed (saw ${a.seen})`);

    // ...over the SERVED tick, which needs a pacer whose clock has
    // actually drifted off it to mean anything. A pacer fresh out of the
    // constructor is already sitting at the served tick, so asserting it
    // there proves nothing -- this one has been run against a 1000ms
    // server until its pace followed.
    const drifted = runFeed({ arrivals: series(40, 1000, 20), untilMs: 42000 });
    assert(
      Math.abs(drifted.pacer.playMs - drifted.store.tickMs) > 100,
      'guard: the pace should have followed the 1000ms server away from the served 800ms',
    );
    const b = env.fresh();
    b.pacer = drifted.pacer;
    b.presentation = drifted.store;
    at(50000); b.setPaced(false);
    at(50100); b.push(feedWorld(41));
    assert(
      b.presentation.currPlayMs === b.presentation.tickMs,
      `an unpaced pair plays over ${b.presentation.currPlayMs}ms, want the served ${b.presentation.tickMs}ms`,
    );

    // And back on: the buffer fills again rather than staying bypassed.
    a.setPaced(true);
    at(200); a.push(feedWorld(6));
    assert(a.seen.join() === '1,2,3,4,5', `switching back on did not resume buffering (saw ${a.seen})`);
    at(1400); a.pump(1400);
    assert(a.seen.join() === '1,2,3,4,5,6', `the buffer never paid out again (saw ${a.seen})`);
  });

  // The key and its note, in the same mold as the other four -- except the
  // note reads the other way round, because this one is on by default.
  const src = readFileSync(join(here, 'app.js'), 'utf8');
  assert(/key === 'b'/.test(src), "no 'b' key toggles the delay line");
  assert(
    /pacedNoteEl\.hidden = anim\.paced/.test(src),
    'the note must show when the delay line is OFF, which is the non-default state',
  );
  const markup = readFileSync(join(here, 'index.html'), 'utf8');
  assert(markup.includes('id="paced-note"'), 'the footer has no note for the delay line');
  assert(/<kbd>b<\/kbd>/.test(markup), 'the footer never tells anyone the key exists');
});

// ---- the axial whip (2026-08-11) ----
//
// Owner: "occasional fast motions by a cat in place... might be associated
// with north/south movement". Measured on a live feed: 60% of all view
// changes happened with the served facing UNCHANGED, and 295 of those
// reversed inside one tick. `AXIAL_POSES` is only {walking, idle}, so a
// cat facing north at the water alternating `drinking` and `idle` spun
// ninety degrees and back every tick while standing perfectly still.

/** A cat that stays exactly where it is, tick after tick. */
function stillWorld(tick, pos = { x: 5, y: 5 }) {
  return {
    tick,
    width: 64,
    height: 64,
    elements: [],
    kitties: [{ id: 1, name: 'K', pos: { ...pos }, needs: {}, happiness: 90 }],
  };
}

check('a cat that has not moved keeps its drawing, whatever it is doing', () => {
  const store = new api.Presentation();
  // Walk it north first, so it is genuinely facing north and axial.
  store.pushState(stillWorld(1, { x: 5, y: 7 }), 0);
  store.pushState(stillWorld(2, { x: 5, y: 6 }), 800);
  assert(store.facingFor(1) === 'north', `expected a north-facing cat, got ${store.facingFor(1)}`);
  assert(store.axialFor(1, true), 'a cat that just stepped north must be drawable axially');

  // Now it stands at the water and alternates drinking / idle, ticking all
  // the while but never moving. The pose alternates; the DRAWING must not.
  const poses = ['drinking', 'idle', 'drinking', 'idle', 'drinking', 'idle'];
  const axialPose = (p) => p === 'walking' || p === 'idle';
  const seen = [];
  const control = [];
  for (let i = 0; i < poses.length; i += 1) {
    store.pushState(stillWorld(3 + i, { x: 5, y: 6 }), 1600 + i * 800);
    seen.push(store.axialFor(1, axialPose(poses[i])));
    control.push(axialPose(poses[i])); // what shipped before: the pose alone
  }
  const changes = (xs) => xs.filter((v, i) => i && v !== xs[i - 1]).length;
  assert(
    changes(control) === 5,
    `control: the pose alone should whip the drawing 5 times, got ${changes(control)}`,
  );
  assert(
    changes(seen) === 0,
    `a stationary cat's drawing changed ${changes(seen)} times: ${seen.join(',')}`,
  );
  assert(seen.every((v) => v === false), 'it should have settled side-on, where a drinking cat can be drawn');
});

check('a step re-earns the axial drawing, and only a step does', () => {
  const store = new api.Presentation();
  store.pushState(stillWorld(1, { x: 5, y: 7 }), 0);
  store.pushState(stillWorld(2, { x: 5, y: 6 }), 800);
  store.axialFor(1, false); // groomed once: side-on from here
  store.pushState(stillWorld(3, { x: 5, y: 6 }), 1600);
  assert(!store.axialFor(1, true), 'standing still must not re-earn the axial drawing');

  store.pushState(stillWorld(4, { x: 5, y: 5 }), 2400); // steps north again
  assert(
    store.axialFor(1, true),
    'a served step is the evidence that re-earns it -- the cat really is facing that way',
  );

  // And a cat that keeps walking is never held side-on: being locked is
  // for cats that stopped, not cats that are travelling.
  for (let t = 5; t < 12; t += 1) {
    store.pushState(stillWorld(t, { x: 5, y: 10 - t }), t * 800);
    assert(store.axialFor(1, true), `a walking cat was held side-on at tick ${t}`);
  }
});

check('a discontinuity forgets the lock, like every other memory', () => {
  const store = new api.Presentation();
  store.pushState(stillWorld(1, { x: 5, y: 7 }), 0);
  store.pushState(stillWorld(2, { x: 5, y: 6 }), 800);
  store.axialFor(1, false);
  assert(!store.axialFor(1, true), 'guard: the cat should be locked side-on');
  store.bumpGeneration();
  store.pushState(stillWorld(9, { x: 5, y: 6 }), 1600);
  assert(store.discontinuous, 'guard: that push should have broken continuity');
  assert(
    store.axialFor(1, true),
    'a new moment of the world starts fresh -- a lock is presentational memory like the rest',
  );
});

check('the renderer asks before it draws a cat axially', () => {
  // The rule is worthless if the draw path still decides on the pose alone.
  const src = readFileSync(join(here, 'render.js'), 'utf8');
  const decision = src.slice(src.indexOf('const axialPose ='), src.indexOf('const catView ='));
  assert(/view\.axialFor/.test(decision), 'render.js decides the axial view without consulting axialFor');
  assert(
    /const axial = axialOk &&/.test(decision),
    'the axial view must be gated by axialFor, not merely informed by it',
  );
  // ...and the swim views stay gated separately even now that they ship.
  // cat-v2 can DRAW them; VIEW.swimAxial decides which directions the
  // meadow asks for, and dropping the gate would take that choice away.
  assert(
    /swimAxialAllows\(/.test(decision),
    'render.js must gate the axial swim on VIEW.swimAxial, whatever it is currently set to',
  );
});

check('every view method the renderer guards for is actually served', () => {
  // render.js reads most of the view DEFENSIVELY -- `view.axialFor ? ... :
  // fallback` -- so that a v1 caller or the labs can hand it a smaller
  // object. The cost is that a method dropped from `viewAt` does not
  // throw: it silently takes the fallback, which is the OLD behaviour,
  // and the feature ships inert with every test green. That is exactly
  // how #182 shipped and how #187 nearly did.
  //
  // So the guard is the check: anything render.js is willing to fall back
  // from must still be there to fall back FROM.
  const src = readFileSync(join(here, 'render.js'), 'utf8');
  const guarded = new Set(
    [...src.matchAll(/view\.(\w+)\s*\?/g)].map((m) => m[1]),
  );
  assert(guarded.size >= 5, `only found ${guarded.size} guarded view methods -- the scan is not finding them`);

  const store = new api.Presentation();
  store.pushState(feedWorld(1), 0);
  store.pushState(feedWorld(2), 800);
  for (const still of [false, true]) {
    const v = store.viewAt(1200, still);
    const missing = [...guarded].filter((name) => typeof v[name] !== 'function');
    assert(
      missing.length === 0,
      `viewAt(${still ? 'still' : 'moving'}) is missing ${missing.join(', ')} -- ` +
        'render.js guards for those, so they would silently take the fallback',
    );
  }
});

// ---- swimming end-on (2026-08-11), built but NOT shipped ----

check('a swimming cat drawn end-on keeps its head out of the water', () => {
  // The whole judging problem in one assertion. At the live waterline only
  // a few pixels of body clear the surface, so nearly everything that says
  // "cat" is the head -- and a head that dips below the clip leaves a
  // swimming cat as a sliver of back and nothing else.
  const surface = VIEW.waterline;
  for (const view of ['front', 'back']) {
    const L = CatV2.catLayout('swim', 0.25, { view });
    const headTop = L.head.cy - L.head.r;
    const headBottom = L.head.cy + L.head.r;
    assert(headBottom < surface, `${view}: the head dips under the waterline (${headBottom} vs ${surface})`);
    assert(headTop > 0, `${view}: the head has left the top of the box`);

    // Some back, but not the whole body: a cat sitting entirely above the
    // surface is a cat standing ON water, which is the bug SWIM's own
    // comment records being fixed once already.
    const bodyTop = L.body.cy - L.body.ry;
    const bodyBottom = L.body.cy + L.body.ry;
    assert(bodyTop < surface, `${view}: no body clears the surface at all`);
    assert(bodyBottom > surface, `${view}: the whole body floats above the water`);

    // No legs, like the side pose -- they are under water, and the clip
    // would take them anyway.
    assert(L.legs.length === 0, `${view}: a swimming cat is drawing ${L.legs.length} legs`);

    // The tail is HELD UP (owner, 2026-08-11): it leaves a submerged rump
    // and rides clear of the surface, which is the posture the shallow
    // water we built calls for -- and in the away view it is the only
    // piece of silhouette above water that is not a circle or an ear.
    assert(L.tail && Number.isFinite(L.tail.y0), `${view}: the swim tail is not a drawable tail`);
    assert(L.tail.y0 > surface, `${view}: the tail's base should leave a submerged rump`);
    assert(L.tail.y1 < surface, `${view}: the tail tip is under the water, where nobody can see it`);
    assert(
      surface - L.tail.y1 > 0.15,
      `${view}: only ${((surface - L.tail.y1) * 31).toFixed(1)}px of tail clears the water -- ` +
        'that is not a raised tail, it is a nub',
    );
    // ...and it must clear the BODY by enough to SEE, or the raised length
    // is lost against the very silhouette it is meant to break up.
    // Clearing by a hair is the same as not clearing: at a 31px tile a
    // third of a pixel of tail above the back is nothing at all.
    const overBody = (L.body.cy - L.body.ry - L.tail.y1) * 31;
    assert(
      overBody > 2,
      `${view}: only ${overBody.toFixed(1)}px of tail rises above the body's own top edge`,
    );
  }
});

check('an end-on swimmer is narrower than a side-on one, and not by nothing', () => {
  const side = CatV2.catLayout('swim', 0.25, { view: 'side' });
  const front = CatV2.catLayout('swim', 0.25, { view: 'front' });
  assert(front.body.rx < side.body.rx, 'a cat seen end-on must be narrower than one seen side-on');
  assert(
    side.body.rx - front.body.rx > 0.05,
    `only ${(side.body.rx - front.body.rx).toFixed(3)} narrower -- that is not a different view`,
  );
  // The two directions differ from each other too, or there was no point
  // drawing both: the far head is smaller, which is the depth cue.
  const back = CatV2.catLayout('swim', 0.25, { view: 'back' });
  assert(back.head.r < front.head.r, 'the head going away must read as farther than the one coming toward');
  // What the two views owe the tail is NOT the same thing, and the
  // difference is paint order, not taste.
  //
  // (This replaces an assertion that the away view must show MORE tail
  // than the toward view. That was a hypothesis of mine, not an invariant,
  // and the owner's dialling falsified it: away reads best with the tail
  // near vertical out of the centre of the back, toward with it pushed
  // wide. Only the mechanical constraint below survives.)
  //
  // Walking away, the tail paints IN FRONT of the body, so it may rise
  // from anywhere -- the centre included -- and still be seen. Coming
  // toward you it paints BEHIND, so anything inside the body's own edge is
  // hidden by it, and a tail nobody can see is not a tail.
  const flank = 0.5 + front.body.rx;
  assert(
    Math.abs(front.tail.x1 - 0.5) > front.body.rx,
    `the toward view's tail tip sits at ${front.tail.x1} and the flank is at ${flank} -- ` +
      'it paints behind the body, so it would be invisible',
  );
});

check('the side swim tail can be pulled upright without re-authoring it', () => {
  // Owner, 2026-08-11: an upright tail is the posture shallow water calls
  // for. The dial ships at 0, which must be the shape that shipped -- the
  // live meadow does not change until it is judged in the lab.
  // This used to assert the dial SHIPPED at 0, to guarantee the live
  // meadow could not change before the lab had spoken. It has now spoken
  // (owner, 2026-08-11: tailUpright 1), so that guard has done its job and
  // is retired rather than quietly deleted. What survives is the property
  // that actually keeps the dial honest: its zero end must still reproduce
  // the trailing tail v2.7 shipped, exactly, so the change is a CHOICE and
  // not a one-way door.
  const wasUp = CatV2.SWIM.tailUpright;
  CatV2.SWIM.tailUpright = 0;
  const shipped = CatV2.catLayout('swim', 0.25, { view: 'side' });
  CatV2.SWIM.tailUpright = wasUp;
  assert(
    Math.abs(shipped.tail.x1 - 0.05) < 1e-9 && Math.abs(shipped.tail.c2x - 0) < 1e-9,
    'at tailUpright 0 the tail must be exactly the trailing shape that shipped',
  );

  assert(
    Math.abs(shipped.tail.x1 - shipped.tail.x0) > 0.1,
    'guard: at 0 the tail should still be trailing, or this dial does nothing',
  );

  // At 1 it must MATCH the end-on views, which is the whole ask: a cat
  // wading north, east and south is one animal. The first cut only
  // straightened the trail and left the tip at `tailLift`, which is 0.08
  // above the body -- a stub, because a trailing tail gets its length from
  // the horizontal run. Height is the thing to assert, not straightness.
  CatV2.SWIM.tailUpright = 1;
  const upright = CatV2.catLayout('swim', 0.25, { view: 'side' });
  CatV2.SWIM.tailUpright = wasUp; // restore what SHIPS, not a hardcoded 0
  const away = CatV2.catLayout('swim', 0.25, { view: 'back' });
  assert(Math.abs(upright.tail.x0 - shipped.tail.x0) < 1e-9, 'the base moved');
  // The two are tied together by ONE anchor plus ONE declared difference,
  // never two free numbers: the side tail rides at the shared height
  // raised by `tailUprightRise`, the foreshortening allowance (a tail seen
  // broadside shows its whole length; seen end-on it draws short). Set
  // that to 0 and the three views match exactly.
  //
  // Asserted in PIXELS with the slack accounted for rather than guessed:
  // `proportionLayout` shifts a layout by ry x (1 - bodyH) to keep feet on
  // the floor, and the two swim poses carry different body depths (0.155
  // side, 0.15 end-on -- a flank is not a chest), which leaves ~0.008px on
  // the table.
  const expected = away.tail.y1 - CatV2.SWIM.tailUprightRise;
  const apart = Math.abs(upright.tail.y1 - expected) * 31;
  assert(
    apart < 0.5,
    `the side tail rides ${apart.toFixed(2)}px off the shared height plus its allowance -- ` +
      'one anchor and one declared difference, or they drift apart on the next re-dial',
  );
  // The allowance's SIGN is an invariant; its size is the owner's. A tail
  // seen broadside cannot draw shorter than the same tail seen end-on --
  // that is foreshortening running backwards -- but 0 is a legitimate
  // choice (it makes the three views identical, which is where this
  // started), so the magnitude is deliberately not pinned.
  assert(
    CatV2.SWIM.tailUprightRise >= 0,
    `tailUprightRise is ${CatV2.SWIM.tailUprightRise}: a broadside tail cannot be SHORTER than an end-on one`,
  );

  // The swimming tail SHIPS held up (owner, 2026-08-11) -- that is a
  // visible change to the live meadow, not a lab-only value, so a silent
  // revert to the trailing tail should not pass unremarked. How far up is
  // still hers: this pins the decision, not the number.
  assert(
    CatV2.SWIM.tailUpright > 0,
    'the swimming tail ships held up; going back to the trailing one is a decision, not a tweak',
  );
  const rise = (L) => (L.body.cy - L.tail.y1) * 31;
  assert(
    rise(upright) > rise(shipped) + 4,
    `upright rises ${rise(upright).toFixed(1)}px against the trail's ${rise(shipped).toFixed(1)}px ` +
      '-- that is a straightened stub, not a raised tail',
  );
  assert(
    upright.tail.y1 < VIEW.waterline - 0.15,
    'the upright side tail must clear the water by as much as the end-on ones do',
  );
});

check('two dials own the side tail height, and the lab says which is live', () => {
  // `tailLift` sets the TRAILING tip and `AXIAL_SWIM.tailTopY` the raised
  // one, so whichever is not in charge looks broken when you drag it --
  // the same "nothing happens" the owner reported for a different reason.
  // Measured, not assumed: at upright 1 the height is entirely the shared
  // one, which is what makes the three views agree.
  // Restore to what SHIPS rather than to a literal: the shipped value is
  // the owner's and moves, and a test that hardcodes it silently re-dials
  // the cat for every check that runs after it.
  const shippedUp = CatV2.SWIM.tailUpright;
  const shippedLift = CatV2.SWIM.tailLift;
  const tipAt = (up, lift) => {
    CatV2.SWIM.tailUpright = up;
    CatV2.SWIM.tailLift = lift;
    const y = CatV2.catLayout('swim', 0, { view: 'side' }).tail.y1;
    CatV2.SWIM.tailUpright = shippedUp;
    CatV2.SWIM.tailLift = shippedLift;
    return y;
  };
  assert(tipAt(0, 0.45) !== tipAt(0, 0.7), 'tailLift must move the trailing tip');
  assert(
    tipAt(1, 0.45) === tipAt(1, 0.7),
    'at upright 1 the tip must come from the SHARED height, or the three views drift apart',
  );
  assert(tipAt(0.5, 0.45) !== tipAt(0.5, 0.7), 'part-way, tailLift should still have a say');

  // Since one of them is always inert, the lab has to name the live one
  // and the label has to warn -- otherwise the next dialling session
  // rediscovers this the slow way.
  const html = readFileSync(join(here, 'gallery-v2.html'), 'utf8');
  const card = html.slice(html.indexOf("title: 'Swimming end-on"));
  const body = card.slice(0, card.indexOf('\n    },'));
  assert(/inert at upright 1/.test(body), 'the tail-tip dial must say when it does nothing');
  assert(/governed by \$\{owner\}/.test(body), 'the readout must name which dial owns the tip height');
  // ...and warn when the tail is dialled under the water, where the clip
  // eats it: the top of the range (0.75) is past the waterline (0.72).
  assert(/BELOW the waterline/.test(body), 'the readout must flag a tail dialled under the surface');
});

check('a raised tail is drawn where it can be SEEN, in every view', () => {
  // The bug this pins, twice over. A tail that paints behind the body and
  // rises INSIDE the body's own silhouette is not a tail, it is a hidden
  // line -- all that shows is whatever pokes above the back. The first cut
  // of the upright side tail stood it over the rump at x 0.12 against a
  // body edge at x 0.11, and the owner's report was simply that the dial
  // did nothing.
  //
  // Only the away view is exempt, and for a mechanical reason: it paints
  // the tail IN FRONT of the body (see the paint-order check), so it may
  // rise from anywhere, the centre included.
  const ships = CatV2.SWIM.tailUpright;
  const cases = [
    ['side, tail up', () => { CatV2.SWIM.tailUpright = 1; }, { view: 'side' }],
    ['side, trailing', () => { CatV2.SWIM.tailUpright = 0; }, { view: 'side' }],
    ['side, as shipped', () => {}, { view: 'side' }],
    ['toward you', () => {}, { view: 'front' }],
  ];
  for (const [name, setup, opts] of cases) {
    setup();
    const L = CatV2.catLayout('swim', 0, opts);
    CatV2.SWIM.tailUpright = ships;
    const clear = Math.abs(L.tail.x1 - L.body.cx) - L.body.rx;
    assert(
      clear > 0.01,
      `${name}: the tail tip is ${(-clear * 31).toFixed(1)}px INSIDE the body's edge, ` +
        'so it paints behind the body and cannot be seen',
    );
  }
});

check('the swim-view setting is one the code actually recognises', () => {
  // This check used to assert `swimAxial` shipped as 'none', to prove the
  // meadow could not change before the lab had spoken. It has spoken
  // (owner, 2026-08-11: both), so that guard is retired rather than
  // quietly deleted.
  //
  // What replaces it guards the way this particular switch FAILS. It is a
  // string compared against literals, and anything unrecognised -- 'Both',
  // a stray space, a rename on one side only -- silently means 'none':
  // the feature ships inert, the meadow looks exactly as it did, and every
  // check here still passes. That is the same shape as #182 shipping inert
  // and #187 nearly doing so, so the shipped value has to be a value the
  // code can actually act on.
  const known = ['none', 'toward', 'both'];
  assert(
    known.includes(VIEW.swimAxial),
    `VIEW.swimAxial is '${VIEW.swimAxial}', which no branch matches -- it would silently mean 'none'`,
  );
  // The end-on swim SHIPS (owner, 2026-08-11: both). Which directions is
  // still hers -- 'toward' is a legitimate answer -- but turning it off
  // altogether removes a drawing from the live meadow, and that is a
  // decision someone should have to write down, not a value that can
  // drift back with every test still green.
  assert(
    VIEW.swimAxial !== 'none',
    'the end-on swim ships; switching it off is a decision, not a tweak',
  );
  assert(
    ['north', 'south'].some((f) => swimAxialAllows(f)),
    `VIEW.swimAxial is '${VIEW.swimAxial}' but no facing is allowed -- the feature is inert`,
  );
  // ...and each setting means what it says.
  assert(swimAxialAllows('south', { swimAxial: 'toward' }), "'toward' must allow a cat swimming at you");
  assert(!swimAxialAllows('north', { swimAxial: 'toward' }), "'toward' must NOT allow one swimming away");
  assert(swimAxialAllows('north', { swimAxial: 'both' }), "'both' must allow either");
  assert(swimAxialAllows('south', { swimAxial: 'both' }), "'both' must allow either");
  // An unknown value is not a licence to draw something nobody picked.
  assert(!swimAxialAllows('south', { swimAxial: 'yes please' }), 'an unrecognised setting must draw side-on');
  assert(!swimAxialAllows('south', {}), 'a missing setting must draw side-on');
});

check('a dial that names its own block actually writes that block', () => {
  // The swim card judges the axial views and the SIDE pose's tail
  // together, and those live in different bags. If the builder ignored
  // `d.bag`, the SIDE sliders would quietly write a `tailUpright` onto
  // AXIAL_SWIM instead: the slider moves, the readout prints, the drawing
  // never changes, and a whole dialling session is wasted. That has
  // happened before with pasted values, so it gets a guard.
  const html = readFileSync(join(here, 'gallery-v2.html'), 'utf8');
  const declared = [...html.matchAll(/bag: CatV2\.(\w+)/g)].map((m) => m[1]);
  if (!declared.length) return; // no card needs a second block right now
  const builder = html.slice(html.indexOf('function buildDemoDials'));
  const body = builder.slice(0, builder.indexOf('\n  }\n'));
  assert(
    /const bag = d\.bag \?\? demo\.bag/.test(body),
    'a dial declares its own bag but buildDemoDials still writes demo.bag',
  );
  assert(
    !/\bdemo\.bag\[d\.key\]/.test(body),
    'buildDemoDials still reaches demo.bag[d.key] directly somewhere -- a per-dial bag would be ignored there',
  );
  for (const name of new Set(declared)) {
    assert(CatV2[name], `a dial names CatV2.${name}, which the vocabulary does not export`);
  }
});

check('the inner ear is a shape, not a sub-pixel needle', () => {
  // Owner, 2026-08-13: "I only see a tiny sliver of pink there anyway."
  // Measured, she was describing the geometry exactly. The first tick ran
  // 35%..100% along the ear's spine with a 0.12 nudge sideways at ONE of
  // its three points, so it was a one-sided needle: 0.71px2 of paint at a
  // 31px cat, never more than 0.64px across -- under the 0.8px floor that
  // killed whiskers twice.
  //
  // What is measured here is the pink she can SEE: inside its quad, inside
  // the ear, and outside the head that paints over its base. Measuring the
  // drawn shape instead would count paint hidden under the skull, which is
  // most of it and none of the point.
  const a = CatV2.appearanceFor(3);
  const shapes = (pose, view, facing) => {
    const out = [];
    let cur = null; let ink = null; let clip = null; const stack = [];
    const ctx = new Proxy({}, {
      get: (_t, p) => (...g) => {
        const n = String(p);
        if (n === 'beginPath') cur = [];
        else if ((n === 'moveTo' || n === 'lineTo') && cur) cur.push([g[0], g[1]]);
        else if (n === 'arc' && cur) cur.arc = { cx: g[0], cy: g[1], r: g[2] };
        else if (n === 'save') stack.push(clip);
        else if (n === 'restore') clip = stack.pop() ?? null;
        else if (n === 'clip') clip = cur ? cur.slice() : [];
        else if (n === 'fill' && cur) out.push({ pts: cur.slice(), arc: cur.arc, ink, clip });
      },
      set: (_t, p, v) => { if (String(p) === 'fillStyle') ink = v; return true; },
    });
    CatV2.drawCat(ctx, { pose, appearance: a, facing, size: 31, layout: { view } });
    // The NOSE is a pink shape too, so colour alone picks up three and
    // measures the wrong one. (It did, first try -- the same mistake the
    // muzzle check upstream records having made.) The inner ears are the
    // pink drawn under a three-point clip, which is what they are.
    return {
      all: out,
      pink: out.filter((r) => r.clip && r.clip.length === 3 && r.pts.length >= 3
        && r.ink === CatV2.noseInkOf(a)),
      ears: out.filter((r) => r.ink === a.furBase && r.pts.length === 3),
    };
  };
  const inPoly = (pt, poly) => {
    let inside = false;
    for (let i = 0, j = poly.length - 1; i < poly.length; j = i, i += 1) {
      const [xi, yi] = poly[i]; const [xj, yj] = poly[j];
      if ((yi > pt[1]) !== (yj > pt[1])
        && pt[0] < ((xj - xi) * (pt[1] - yi)) / (yj - yi) + xi) inside = !inside;
    }
    return inside;
  };
  // Sampled rather than solved: the visible region is a polygon minus a
  // disc, and the number wanted is "does this survive the pixel grid", not
  // an exact area. The EAR's visible area comes back too, because the pink
  // has to be judged against the ear it is in -- see the floor below.
  const seenPx = (r, head) => {
    const xs = r.clip.map((q) => q[0]); const ys = r.clip.map((q) => q[1]);
    const x0 = Math.min(...xs); const x1 = Math.max(...xs);
    const y0 = Math.min(...ys); const y1 = Math.max(...ys);
    const N = 160; let pink = 0; let ear = 0;
    for (let i = 0; i < N; i += 1) {
      for (let j = 0; j < N; j += 1) {
        const pt = [x0 + ((x1 - x0) * (i + 0.5)) / N, y0 + ((y1 - y0) * (j + 0.5)) / N];
        if (Math.hypot(pt[0] - head.cx, pt[1] - head.cy) <= head.r) continue;
        if (!inPoly(pt, r.clip)) continue;
        ear += 1;
        if (inPoly(pt, r.pts)) pink += 1;
      }
    }
    const cell = (((x1 - x0) * (y1 - y0)) / (N * N)) * 31 * 31;
    return { pink: pink * cell, ear: ear * cell };
  };

  const up = shapes('idle', 'side', 'right');
  assert(up.pink.length === 2, `expected two inner ears, drew ${up.pink.length}`);
  const head = CatV2.catLayout('idle', 0, { view: 'side' }).head;
  const seen = seenPx(up.pink[0], head).pink;
  assert(seen > 2, `an inner ear shows ${seen.toFixed(2)}px2 at a 31px cat -- the old needle showed 0.71`);

  // Painted WITH the ear, under the head. That is what lets it run the
  // ear's full height with no rule of its own about where the skull
  // begins, and solving for that line instead got the centre right and
  // still put both base corners inside the head, because the skull is
  // round. Order is the mechanism, so order is what is asserted.
  const headFill = up.all.findIndex((r) => r.arc && Math.abs(r.arc.r - head.r) < 1e-9);
  const pinkFill = up.all.indexOf(up.pink[0]);
  assert(headFill > 0, 'could not find the head in the paint order');
  assert(pinkFill < headFill,
    'the inner ear is painted after the head -- its base will show on the skull');

  // The claim the re-cut was FOR: fur shows down both sides, at every
  // height, and the gap does not close toward the tip. Three mutations
  // walked straight through the checks above -- no side margin at all, a
  // margin dialled outward past the ear, and a tip that ignores the side
  // margin so the sides converge and the fur runs out at the top. Every
  // one of them still drew a big enough pink inside a clip.
  const ear0 = up.ears[0];
  const base = [(ear0.pts[0][0] + ear0.pts[2][0]) / 2, (ear0.pts[0][1] + ear0.pts[2][1]) / 2];
  const tip = ear0.pts[1]; // b1, point, b2
  const hx = (ear0.pts[0][0] - ear0.pts[2][0]) / 2;
  const hy = (ear0.pts[0][1] - ear0.pts[2][1]) / 2;
  const spinePx = Math.hypot(tip[0] - base[0], tip[1] - base[1]) * 31;
  const halfPx = Math.hypot(hx, hy) * 31;
  const at = (u, w) => [base[0] + (tip[0] - base[0]) * u + hx * w,
    base[1] + (tip[1] - base[1]) * u + hy * w];

  // EVEN down both sides, which is the fix this shape went through a
  // second cut for. An ear leans -- `earPoints` swings the tip outward --
  // so its two slanted edges make different angles with its base, and
  // insetting by a fixed step ALONG the base gave one edge more fur than
  // the other: 0.46px against 0.64px, which the owner could see at a 31px
  // cat. Perpendicular distance is the thing being judged, so it is the
  // thing measured.
  const perp = (pt, p, q) => Math.abs((q[0] - p[0]) * (p[1] - pt[1]) - (p[0] - pt[0]) * (q[1] - p[1]))
    / Math.hypot(q[0] - p[0], q[1] - p[1]);
  for (const pink of up.pink) {
    const ear = pink.clip; // [b1, point, b2]
    const left = Math.min(...pink.pts.map((pt) => perp(pt, ear[0], ear[1]))) * 31;
    const right = Math.min(...pink.pts.map((pt) => perp(pt, ear[2], ear[1]))) * 31;
    assert(Math.abs(left - right) < 0.02,
      `fur is ${left.toFixed(2)}px down one side and ${right.toFixed(2)}px down the other`);
    assert(left > 0.4, `only ${left.toFixed(2)}px of fur shows beside the pink`);
  }

  // The blunt tip, which the owner's bake (tipFur 0, 2026-08-13) does not
  // take: at 0 the inset sides meet on their own and the pink comes to a
  // point, so the cut branch stops running and would rot unseen. Dialled
  // up here to hold it to its claim -- a flat top, and the SIDES
  // unmoved, which is the whole reason the cut is parallel to the base.
  const wasTip = CatV2.INNER_EAR.tipFur;
  CatV2.INNER_EAR.tipFur = 0.2;
  const blunt = shapes('idle', 'side', 'right');
  CatV2.INNER_EAR.tipFur = wasTip;
  assert(blunt.pink.length === 2, 'dialling the tip lost the inner ears');
  assert(blunt.pink[0].pts.length === 4,
    `a blunt tip should add a top edge, drew ${blunt.pink[0].pts.length} corners`);
  const gapOf = (r) => Math.min(...r.pts.map((pt) => perp(pt, r.clip[0], r.clip[1]))) * 31;
  assert(Math.abs(gapOf(blunt.pink[0]) - gapOf(up.pink[0])) < 0.02,
    `cutting the tip moved the side gap from ${gapOf(up.pink[0]).toFixed(2)}px ` +
    `to ${gapOf(blunt.pink[0]).toFixed(2)}px -- the two dials are meant to be independent`);
  let bluntTop = 0;
  for (let u = 0; u <= 1; u += 0.002) if (inPoly(at(u, 0), blunt.pink[0].pts)) bluntTop = u;

  // How high the pink actually reaches, read off the shape rather than
  // recomputed from the dials -- restating `1 - sideFur - tipFur` here
  // would assert this test's own arithmetic.
  let pinkTop = 0;
  for (let u = 0; u <= 1; u += 0.002) if (inPoly(at(u, 0), up.pink[0].pts)) pinkTop = u;
  assert(pinkTop > 0, 'no pink anywhere along the ear');
  assert((1 - pinkTop) * spinePx > 0.4,
    `fur at the tip is ${((1 - pinkTop) * spinePx).toFixed(2)}px -- the pink runs into the point`);
  assert(bluntTop < pinkTop,
    'dialling tipFur up did not shorten the pink -- the cut is doing nothing');

  // ...and fur down both sides, at every height the pink reaches. The gap
  // must not close toward the tip either: three mutations walked straight
  // through the checks above -- no side margin at all, a margin dialled
  // OUTWARD past the ear, and a tip that ignores the side margin so the
  // sides converge and the fur runs out at the top. All three still drew a
  // big enough pink inside a clip.
  for (const frac of [0.2, 0.5, 0.85]) {
    const u = pinkTop * frac;
    for (const dir of [-1, 1]) {
      let lastPink = 0; let lastEar = 0;
      for (let w = 0; w <= 1.4; w += 0.002) {
        if (inPoly(at(u, w * dir), up.pink[0].pts)) lastPink = w;
        if (inPoly(at(u, w * dir), ear0.pts)) lastEar = w;
      }
      const side = dir < 0 ? 'left' : 'right';
      assert(lastPink > 0, `${(frac * 100).toFixed(0)}% up the pink there is none on the ${side}`);
      assert((lastEar - lastPink) * halfPx > 0.4,
        `${(frac * 100).toFixed(0)}% up the pink, the fur on the ${side} is ` +
        `${((lastEar - lastPink) * halfPx).toFixed(2)}px -- it should sit inside, evenly, all the way up`);
    }
  }

  let smallest = Infinity;
  let where = '';
  for (const [pose, view, facing] of [
    ['idle', 'side', 'right'], ['walking', 'side', 'right'],
    ['idle', 'front', 'south'], ['eating', 'side', 'right'],
    ['sleeping', 'side', 'right'], ['pouncing', 'side', 'right'],
  ]) {
    const got = shapes(pose, view, facing);
    if (!got.pink.length) continue;
    const h = CatV2.catLayout(pose, 0, { view }).head;
    for (let i = 0; i < got.pink.length; i += 1) {
      const ear = got.ears[i];
      assert(ear, `${pose}/${view}: an inner ear without an ear to sit in`);
      // The clip is what turns an over-dialled margin into a filled ear
      // rather than pink smeared across the skull. At the SHIPPED values
      // the pink is inside its ear anyway, so no pixel would notice the
      // clip going missing -- hence the mechanism, not its effect.
      assert(
        JSON.stringify(got.pink[i].clip) === JSON.stringify(ear.pts),
        `${pose}/${view} ear ${i}: the pink is not clipped to the ear it sits in`,
      );
      const m = seenPx(got.pink[i], h);
      const share = m.pink / m.ear;
      if (share < smallest) {
        smallest = share;
        where = `${pose}/${view} ear ${i}`;
      }
    }
  }
  // A SHARE, not an area, and the reason is worth keeping. The first
  // version of this floor was absolute, and the perpendicular inset above
  // tripped it: with the ears laid flat the whole visible EAR is 1.65px2,
  // so a fixed pink area there is really a demand that the pink take up
  // more of a smaller ear. A cat flattening its ears and hiding the pink
  // is the drawing being right. What must hold in every pose is that the
  // pink is a real feature of whatever ear is showing -- which the old
  // floor never checked, since a pink that shrank while its ear did not
  // would have passed it.
  assert(smallest > 0.15,
    `the pink is only ${(smallest * 100).toFixed(0)}% of the visible ear at ${where}`);
});

check('every face dial is PRINTED, or a dialling session cannot be baked', () => {
  // The lab's whole contract: the owner moves sliders, reads the block,
  // and pastes it back as source. A dial the readout does not print is a
  // slider whose value is lost the moment the page reloads -- which is
  // worse than no dial, because the session that spent an hour on it only
  // finds out at the paste. Whiskers and nose darkness joined the face
  // card on 2026-08-13 and this is what stops the next pair being added
  // to the array and forgotten in the readout.
  const html = readFileSync(join(here, 'gallery-v2.html'), 'utf8');
  const dials = html.slice(html.indexOf('  const DIALS = ['));
  const body = dials.slice(0, dials.indexOf('\n  ];'));
  assert(body.includes("obj: 'EYE'"), 'could not slice the face dials out of the lab');

  const readout = html.slice(html.indexOf('function updateReadout()'));
  const printed = readout.slice(0, readout.indexOf('\n  }'));
  // The readout aliases each block (`const n = CatV2.NOSE`), so resolve the
  // alias rather than guessing at it -- otherwise this passes on any file
  // that merely happens to contain the key somewhere.
  const alias = {};
  for (const m of printed.matchAll(/const (\w+) = CatV2\.(\w+);/g)) alias[m[2]] = m[1];

  const seen = new Set();
  for (const m of body.matchAll(/obj: '(\w+)', key: '(\w+)'/g)) {
    const [, obj, key] = m;
    seen.add(`${obj}.${key}`);
    assert(CatV2[obj], `a face dial names CatV2.${obj}, which the vocabulary does not export`);
    assert(CatV2[obj][key] !== undefined, `a face dial names ${obj}.${key}, which does not exist`);
    assert(alias[obj], `${obj} has dials but the readout never reads CatV2.${obj}`);
    assert(printed.includes(`\${${alias[obj]}.${key}}`),
      `${obj}.${key} has a slider but the readout never prints it -- the value cannot be baked`);
  }
  assert(seen.has('WHISKER.alpha') && seen.has('NOSE.darken'),
    'the two dials this check was written for are gone from the face card');
});

check('the socket hands arrivals to the delay line and nothing else', () => {
  // The queue, the pacing and the backlog collapse all moved into `Pacer`,
  // where the checks above can reach them. What is left in app.js is
  // parsing -- and if a future edit puts a second queue back beside it,
  // there would be two clocks again, which is the whole bug.
  const src = readFileSync(join(here, 'app.js'), 'utf8');
  const body = src.slice(
    src.indexOf('  // ARRIVALS GO TO THE DELAY LINE'),
    src.indexOf("  socket.addEventListener('close'"),
  );
  assert(body.includes('anim.push'), 'could not slice the socket handler out of app.js');
  assert(
    !/requestAnimationFrame|setTimeout|pending/.test(body),
    'the socket handler is queueing or scheduling again -- that belongs to the pacer',
  );
  // The panel rides promotion, not arrival, or the cards lead the meadow.
  assert(
    /anim\.onPromote\s*=\s*present/.test(src),
    'the panel must be driven by anim.onPromote, not by the socket',
  );
});

check("the owner's kitty copy is present, verbatim", () => {
  // ITS OWN CHECK, deliberately. This lived inside the traits check twice and
  // was deleted twice by slices aimed at something else in that block -- and
  // the second time the copy itself went three commits later with nothing
  // left to catch it. A guard nested inside a region under active edit is a
  // guard with a short life.
  const app = readFileSync(join(here, 'app.js'), 'utf8');
  const at = app.indexOf('const KITTY_BIOS');
  assert(at > 0, 'the kitty bios are gone from app.js');
  const bios = app.slice(at, app.indexOf('/** The bio for a cat', at));
  assert(bios.length > 500, 'the bio table is empty or the slice is wrong');

  for (const [name, epithet] of [
    ['Miso', 'Sleepy Kitty'], ['Biscuit', 'Playful Kitty'], ['Pumpkin', 'Hungry Kitty'],
    ['Kittybear', 'Tidy Kitty'], ['Clementine', 'Cuddly Kitty'],
  ]) {
    assert(bios.includes(`name: '${name}'`), `${name} has lost her bio`);
    assert(bios.includes(`epithet: '${epithet}'`), `${name}'s epithet has drifted`);
  }
  // The owner's own correction, which has been lost with the table before.
  assert(/enormous: she/.test(bios), "Pumpkin's colon fix has been lost");

  // Keyed by id AND name, so a reseeded roster shows nothing rather than
  // attaching one cat's life story to another.
  const fnAt = app.indexOf('function bioFor');
  assert(fnAt > 0, 'bioFor is gone, so nothing resolves a cat to her copy');
  assert(/bio\.name === kitty\.name/.test(app.slice(fnAt, fnAt + 400)),
    'the bio is looked up by id alone, so a reseeded roster would mis-attach it');
  assert(/bioFor\(kitty\)/.test(app), 'nothing calls bioFor, so no cat has a bio on screen');
});

check('the per-kitty about ships, and its numbers are the served ones', () => {
  // Shipped visible (owner, 2026-08-15). It was gated behind `t` while the
  // rates were part placeholder; they are the served ones now -- exactly
  // what the config says, baseline included -- so both the stub table and
  // the gate are gone.
  const app = readFileSync(join(here, 'app.js'), 'utf8');
  const markup = readFileSync(join(here, 'index.html'), 'utf8');

  assert(!/STUB_TRAITS/.test(app), 'the placeholder rate table is back');
  assert(!/show-traits|traits-note|const TRAITS/.test(app + markup),
    'the gate is back, so the about link is hidden again');
  const link = markup.slice(markup.indexOf('  .kitty-about {'), markup.indexOf('}', markup.indexOf('  .kitty-about {')));
  assert(!/display: none/.test(link), 'the about link is hidden');
  // It has to be built, and it has to open the dialog.
  assert(/className = 'kitty-about'/.test(app), 'no about link is built on the cards');
  assert(/openTraitsDialog\(live\)/.test(app), 'the about link does not open the dialog');

  // Its visible label is a single `?` now, so the ACCESSIBLE name carries the
  // whole meaning -- without it a screen reader hears "?" and nothing else.
  const build = app.slice(app.indexOf("more.className = 'kitty-about'"));
  const built = build.slice(0, build.indexOf('name.appendChild(more)'));
  assert(/textContent = '\?'/.test(built), 'the about control is no longer the question mark');
  assert(/aria-label', `about \$\{kitty\.name\}`/.test(built),
    'the about control has no accessible name, so it announces as "?"');

  // Drawn as a circle rather than set as a glyph: Unicode's circled question
  // mark is poorly covered and would box on some machines.
  const ring = markup.slice(markup.indexOf('  .kitty-about {'), markup.indexOf('}', markup.indexOf('  .kitty-about {')));
  assert(/border-radius: 50%/.test(ring), 'the about control is no longer a circle');
  assert(/border: 1px solid currentColor/.test(ring),
    'the ring is not drawn in the text colour, so it will not follow a phase change');
  // THE DRAWN RING IS THE BORDER BOX. `border-radius: 50%` resolves against
  // it, so `width` is only the ring's diameter when the box sizes that way
  // and carries no padding. The rule this replaces used content-box padding
  // to grow what it called the touch target, and drew a 23px circle around
  // an 11px box -- three rounds of "shrinking" that changed nothing on
  // screen, because each one was cancelled by the padding added to hold the
  // total. Both halves of that mistake are guarded here.
  const box = ring.match(/width: ([\d.]+)px/);
  assert(box, 'the about control no longer states a width');
  assert(/box-sizing: border-box/.test(ring),
    'the ring is not sized by its border box, so `width` is not its diameter');
  // border-box is what makes the padding below safe, and it is the whole
  // guard against the original bug: under content-box that padding would go
  // straight back into the circle's diameter.
  //
  // The padding is optical centring. Flex centres the LINE box and a `?` is
  // nearly all above its baseline, so the ink centre sits 0.29px above the
  // box centre -- 0.58 device px at 2x, which rounds away on a card at one y
  // offset and up to a full pixel on a card at another. Twice the bias, as
  // padding-top, cancels it. Only the top may carry any.
  const padTop = ring.match(/padding: ([\d.]+)px 0 0/);
  assert(padTop, 'the ring no longer states a top-only padding, so the glyph is off centre');
  assert(Math.abs(Number(padTop[1]) - 0.58) < 0.02,
    `padding-top ${padTop[1]}px does not cancel the 0.29px the glyph rides high`);
  // The ring has a measured floor, not a taste one. Nunito's own `?` outline
  // at weight 700 and 0.69rem was flattened to points and tested against the
  // inscribed circle: the ink clears it by 0.74px at a 12px ring and by
  // 0.02px at 10px, where the glyph touches the circle it sits in.
  assert(Number(box[1]) >= 12,
    `a ${box[1]}px ring puts the question mark against the circle`);
  // And the glyph has to be the thing that reads, so it may neither shrink
  // nor lighten back under the ring it sits in. Both are dialled values.
  const glyph = ring.match(/font-size: ([\d.]+)rem/);
  assert(glyph && Number(glyph[1]) >= 0.69,
    'the question mark is smaller than the size it was dialled to');
  const wght = ring.match(/font-weight: (\d+)/);
  assert(wght && Number(wght[1]) >= 900,
    'the question mark is lighter than the weight it was dialled to');

  // The ring is small; the hit area must not be. It comes from a pseudo
  // element that draws nothing, because the ring cannot supply it.
  const after = markup.slice(markup.indexOf('  .kitty-about::after {'),
    markup.indexOf('}', markup.indexOf('  .kitty-about::after {')));
  assert(after.length, 'the about control has no ::after, so it has no touch target');
  assert(/position: absolute/.test(after),
    'the touch target is in flow, so it moves the name row');
  const inset = after.match(/inset: (-?[\d.]+)px/);
  assert(inset, 'the touch target states no inset');
  const target = Number(box[1]) - 2 * Number(inset[1]);
  assert(target >= 23, `the about control's touch target is only ${target}px`);

  // The bar colours are checked as COLOURS, not by where they came from.
  // The first version read them live from the meadow's palette and asserted
  // that fact -- which passed while `pondDeep` went to #0b1216 on a #37313f
  // night card, 16 points of lightness apart and invisible. The palette is
  // lit for the meadow's ground; these sit on a card. So the property that
  // matters is contrast against both cards, and that is what is measured.
  // Sliced FORWARD from the table, not to the next symbol that happens to
  // be named: `const TRAITS` sits ABOVE this one, so seeking to it produced
  // a backwards slice and an empty string -- which finds no colours and
  // reports every need missing. Third time today; the endpoints get checked
  // now rather than assumed.
  const colourAt = app.indexOf('const NEED_COLOUR');
  const colours = app.slice(colourAt, app.indexOf('};', colourAt));
  assert(colourAt > 0 && colours.length > 40, 'could not slice the colour table out of app.js');
  const hexes = {};
  for (const m of colours.matchAll(/(\w+): '(#[0-9a-f]{6})'/gi)) hexes[m[1]] = m[2];
  const needs = ['eat', 'drink', 'sleep', 'play', 'cuddle', 'bath'];
  for (const n of needs) assert(hexes[n], `${n} has no colour`);

  const rgb = (v) => [1, 3, 5].map((i) => parseInt(v.slice(i, i + 2), 16));
  const lum = (v) => {
    const [r, g, b] = rgb(v).map((c) => {
      const x = c / 255;
      return x <= 0.04045 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4;
    });
    const y = 0.2126 * r + 0.7152 * g + 0.0722 * b;
    return y <= 0.008856 ? 903.3 * y : 116 * y ** (1 / 3) - 16;
  };
  const hue = (v) => {
    const [r, g, b] = rgb(v).map((c) => c / 255);
    const mx = Math.max(r, g, b); const mn = Math.min(r, g, b); const d = mx - mn;
    if (!d) return 0;
    const x = mx === r ? ((g - b) / d) % 6 : mx === g ? (b - r) / d + 2 : (r - g) / d + 4;
    return (Math.round(x * 60) + 360) % 360;
  };
  // The two card colours the bars ever sit on, read out of the stylesheet
  // rather than restated here.
  const cardOf = (block) => markup.slice(markup.indexOf(block)).match(/--card: (#[0-9a-f]{6})/i)[1];
  for (const card of [cardOf('  :root {'), cardOf('  body.night {')]) {
    for (const n of needs) {
      const gap = Math.abs(lum(hexes[n]) - lum(card));
      assert(gap >= 25, `${n} (${hexes[n]}) is ${gap.toFixed(0)} from the ${card} card -- invisible on it`);
    }
  }
  // ...and distinguishable from each other, which is the whole point.
  for (let i = 0; i < needs.length; i += 1) {
    for (let j = i + 1; j < needs.length; j += 1) {
      const d = Math.abs(hue(hexes[needs[i]]) - hue(hexes[needs[j]]));
      assert(Math.min(d, 360 - d) >= 18,
        `${needs[i]} and ${needs[j]} are ${Math.min(d, 360 - d)} degrees apart and will read as one colour`);
    }
  }

  // The backdrop closes it, beside the ×. Asserted as the RECT test rather
  // than the `target === dialog` shorthand: the target is also the dialog
  // when the click lands on its own padding, so the shorthand shuts the card
  // on a click just inside its own edge.
  const init = app.slice(app.indexOf('function initTraitsDialog'), app.indexOf('function ', app.indexOf('function initTraitsDialog') + 10));
  assert(/getBoundingClientRect/.test(init), 'the backdrop click closes on target alone, so the padding closes it too');
  assert(/event\.target !== dialog/.test(init), 'a keyboard-fired click at (0, 0) will read as a backdrop click');
  assert(/dialog\.close\(\)/.test(init), 'nothing closes the dialog on a backdrop click');
  assert(/initTraitsDialog\(\);/.test(app.slice(app.lastIndexOf('initCards();'))),
    'initTraitsDialog is never called, so the backdrop does nothing');

  // Every bar starts at the same x. `.trait` is one grid PER ROW, so an
  // `auto` label column sizes to that row's own word and the bars come out
  // ragged -- the labels are right-aligned in a fixed column instead.
  const row = markup.slice(markup.indexOf('  .trait {'), markup.indexOf('}', markup.indexOf('  .trait {')));
  assert(/grid-template-columns: [\d.]+rem/.test(row),
    'the label column is content-sized again, so the bars will not line up');
  const need = markup.slice(markup.indexOf('  .trait-need {'), markup.indexOf('}', markup.indexOf('  .trait-need {')));
  assert(/text-align: right/.test(need), 'the labels no longer sit against their bars');

  // The number columns hold their widest reading without wrapping. Checked
  // as arithmetic rather than by eye: tabular figures at the row's own size,
  // against "0.80" and "+100%".
  const rowSize = parseFloat(row.match(/font-size: ([\d.]+)rem/)[1]) * 16;
  const digit = rowSize * 0.6;
  const cols = row.match(/grid-template-columns: [\d.]+rem 1fr ([\d.]+)rem ([\d.]+)rem/);
  assert(cols, 'could not read the trait row columns');
  for (const [i, sample] of [[1, '0.80'], [2, '(+100%)']]) {
    const have = parseFloat(cols[i]) * 16;
    assert(have >= sample.length * digit,
      `the ${i === 1 ? 'value' : 'delta'} column is ${have.toFixed(0)}px and "${sample}" needs ${(sample.length * digit).toFixed(0)}px`);
  }
  assert(/white-space: nowrap/.test(markup.slice(markup.indexOf('  .trait-value,'), markup.indexOf('}', markup.indexOf('  .trait-value,')))),
    'a tight number column can wrap, which pushes the row height instead of looking cramped');

  // An ordinary cat shows nothing rather than an em dash, and a deviation
  // reads as part of its own number: "0.50 (+25%)".
  const dialogFn = app.slice(app.indexOf('function openTraitsDialog'), app.indexOf('function initTraitsDialog'));
  assert(/pct === 0 \? ''/.test(dialogFn), 'a cat with no deviation still prints a placeholder');
  assert(/\(\$\{t\.pct > 0 \? '\+' : ''\}\$\{t\.pct\}%\)/.test(dialogFn),
    'the deviation is not parenthesised beside its number');
  assert(/\.trait-delta \{ text-align: left/.test(markup),
    'the deviation is right-aligned, so it floats away from the number it belongs to');

  // Each need is scaled to its own baseline, so every centre mark lines up.
  assert(/t\.base \* 2/.test(app), 'the bar is no longer scaled to twice the need\'s own baseline');
  const mark = markup.slice(markup.indexOf('  .trait-base {'), markup.indexOf('}', markup.indexOf('  .trait-base {')));
  assert(/left: 50%/.test(mark), 'the baseline mark is not at the centre of the track');

  // The footnote has to fit its line: the dialog is 360px with 20px padding
  // either side, and at 0.68rem that is about 60 characters.
  const foot = markup.slice(markup.indexOf('<p class="traits-foot">') + 23);
  const text = foot.slice(0, foot.indexOf('</p>')).split(/\s+/).join(' ').trim();
  assert(text.length <= 58, `the traits footnote is ${text.length} characters and will wrap`);
});
check('the camera control seats beside the dial and scales with it', () => {
  const markup = readFileSync(join(here, 'index.html'), 'utf8');
  const app = readFileSync(join(here, 'app.js'), 'utf8');

  // Comments are stripped before anything is matched. These rules DOCUMENT
  // the values they must not have -- the vanished-control comment quotes
  // `padding: 8%` verbatim -- and a text check that reads its own prose
  // reports the bug it was written to catch, on a file that does not have
  // it. Every slice below is comment-free.
  const strip = (css) => css.replace(/\/\*[\s\S]*?\*\//g, '');
  const ruleFor = (sel) => strip(markup.slice(markup.indexOf(sel), markup.indexOf('}', markup.indexOf(sel))));
  const dial = ruleFor('  #sky-dial {');
  const cam = ruleFor('  #camera-toggle {');
  assert(cam.length, 'the camera control has no rule');

  // THE PIN IS THE POINT, and the two now pin one pixel apart on purpose
  // (owner, 2026-08-20). `bottom: 100%` lands on the PADDING box's top edge
  // and the hairline is drawn outside that box, so an unlifted control shares
  // its last row with the line: the dial reads low there and is lifted by the
  // border width, the camera control reads right and was left alone.
  //
  // What both must keep is the rule that made the pin work at all: every term
  // is a VARIABLE. A repeated number leaves one of them floating the moment a
  // breakpoint changes the mat or the line's weight -- and there are three
  // breakpoints now.
  assert(/bottom: calc\(100% - var\(--stage-pad\) \+ var\(--stage-line\)\)/.test(dial),
    'the dial no longer sits on the line: it must clear the padding box by the border width');
  assert(/bottom: calc\(100% - var\(--stage-pad\)\)/.test(cam),
    'the camera control no longer pins to the stage padding, so it has left the horizon');
  for (const [name, rule] of [['dial', dial], ['camera control', cam]]) {
    assert(!/bottom:[^;]*\d+px/.test(rule),
      `the ${name} pins with a literal pixel value; both terms must stay variables`);
  }
  // And the line the dial is lifted by must be the one the stage actually
  // draws, or the dial clears a border that is not there.
  const stageRule = ruleFor('  .stage {');
  assert(/border: var\(--stage-line\) solid/.test(stageRule),
    'the stage border no longer reads --stage-line, so the dial is clearing a guess');

  // One layout for phone and desktop was the owner's whole reason for this
  // seat, and it only holds while BOTH are fractions of the stage. A pixel
  // width on either one makes the pair drift apart as the map resizes --
  // exactly the bug the dial's own width was changed to fix in 2026-07.
  const dialW = dial.match(/width: ([\d.]+)%/);
  const camW = cam.match(/width: ([\d.]+)%/);
  assert(dialW && camW, 'the dial and the camera control are no longer both sized in %');
  // The square stands as tall as the dome: the dial canvas is 2:1, so its
  // height is half its width, and that is what the control matches.
  assert(Math.abs(Number(camW[1]) - Number(dialW[1]) / 2) < 0.01,
    `the camera control is ${camW[1]}% against a dial ${Number(dialW[1]) / 2}% tall -- they no longer stand level`);
  assert(/aspect-ratio: 1/.test(cam), 'the camera control is no longer square');

  // THE DRAWN CHIP IS NOT THE BOX. The box's bottom edge IS the map's top
  // edge, so a chip drawn at the full width of it is tangent to the border
  // and reads as biting into it. The padding is the clearance, and it only
  // works while the pressed background is clipped to the CONTENT box --
  // the `background` shorthand resets that to border-box, which would put
  // the circle straight back on the border with nothing else changing.
  const chip = ruleFor('  .camera-chip {');
  assert(chip.length, 'the camera control has no chip, so its circle sits on the map border');
  const chipW = chip.match(/width: ([\d.]+)%/);
  assert(chipW, 'the chip no longer states a width');

  // A PERCENTAGE PADDING ON THE CONTROL IS THE BUG THAT ATE IT. Percentage
  // padding resolves against the CONTAINING BLOCK's width -- the stage --
  // and never the element's own. `padding: 8%` was written meaning "8% of
  // this 38px control" and got 8% of a 732px stage: 58px a side, inside a
  // 38px border box. Under border-box the content collapsed to zero and
  // the control vanished on reload (owner, 2026-08-16).
  //
  // Asserted by MODELLING the rule rather than banning the property, so a
  // padding that genuinely fits still passes -- and so this check fails for
  // the reason the bug actually had.
  const padPct = cam.match(/padding: ([\d.]+)%/);
  if (padPct) {
    const stageW = 732; // desktop stage, where the ratio is worst
    const eaten = 2 * stageW * (Number(padPct[1]) / 100);
    const boxW = stageW * (Number(camW[1]) / 100);
    assert(eaten < boxW,
      `padding: ${padPct[1]}% is ${eaten.toFixed(0)}px against a ${boxW.toFixed(0)}px control -- it resolves against the STAGE, and the control collapses`);
  }
  // The chip is a CHILD for exactly that reason: as a flex item its width
  // resolves against the control's own content box.
  assert(/flex: none/.test(chip), 'the chip can shrink, so its size is no longer the one stated');

  // Clearance is measured at the small end, where a fraction is worth least.
  const clear = 310 * (Number(camW[1]) / 100) * ((100 - Number(chipW[1])) / 200);
  assert(clear >= 1, `the chip clears the map border by ${clear.toFixed(2)}px on a 320px phone`);

  // And the shrink was the CIRCLE's, not the camera's: the svg is a
  // fraction of the CHIP, so a smaller chip takes the icon with it unless
  // the percentage compensates.
  const svg = markup.match(/#camera-toggle svg \{ width: ([\d.]+)%/);
  assert(svg, 'the camera icon no longer states a width');
  const ofBox = (Number(svg[1]) / 100) * (Number(chipW[1]) / 100);
  assert(Math.abs(ofBox - 0.76) < 0.01,
    `the icon is ${(ofBox * 100).toFixed(1)}% of the control, not the 76% it was dialled to`);

  // The lit state has to reach the chip, which is where the circle is now.
  assert(/#camera-toggle\[aria-pressed='true'\] \.camera-chip \{ background/.test(markup),
    'the pressed state no longer paints the chip, so the toggle has no visible state');

  // The dial has to have actually MOVED, and by the full width of what now
  // sits beside it. Their margins are the same 5%, so the dial's offset is
  // that margin plus the control plus the gap; if the dial were left where
  // it was, the two would overlap and the icon would sit on the dome.
  const dialR = Number(dial.match(/right: ([\d.]+)%/)[1]);
  const camR = Number(cam.match(/right: ([\d.]+)%/)[1]);
  assert(dialR >= camR + Number(camW[1]),
    `the dial at right ${dialR}% overlaps a control spanning ${camR}-${camR + Number(camW[1])}%`);

  // The dial is `pointer-events: none` and must stay so; a control that
  // cannot be clicked is not a control.
  assert(/pointer-events: none/.test(dial), 'the dial has become clickable');
  assert(!/pointer-events: none/.test(cam), 'the camera control cannot be clicked');

  // Small drawing, large hit area -- the about ring's lesson. Asymmetric on
  // purpose: upward is empty page, downward is the meadow, so the bottom
  // inset is the one that must stay shallow.
  const after = ruleFor('  #camera-toggle::after {');
  assert(/position: absolute/.test(after), 'the camera target is in flow and will move the map');
  const inset = after.match(/inset: (-?[\d.]+)px (-?[\d.]+)px (-?[\d.]+)px (-?[\d.]+)px/);
  assert(inset, 'the camera control states no four-sided inset');
  // Every side is read separately because every side is bounded by a
  // DIFFERENT thing, and three of the four bounds are real bugs.
  const grow = inset.slice(1, 5).map((n) => -Number(n)); // top, right, bottom, left
  const [up, out, down, back] = grow;
  // The narrowest stage the phone rule has to hold at: a 320px viewport.
  // Sizing off the desktop's 38px square is how a target that reads fine
  // on a laptop ships 25px on a phone.
  const stage = 310;
  const square = stage * (Number(camW[1]) / 100);
  assert(square + up + down >= 44,
    `the camera target is ${(square + up + down).toFixed(1)}px tall on a 320px phone`);
  // Height comes from ABOVE, which is empty page. The about ring's 23px is
  // the house floor for a width, and the sides here cannot reach 44 without
  // breaking one of the two rules below.
  assert(square + out + back >= 23,
    `the camera target is ${(square + out + back).toFixed(1)}px wide on a 320px phone`);
  assert(down <= 8, `the target reaches ${down}px into the meadow and steals the corner tile`);
  // THE TWO BOUNDS THE SLIDE-RIGHT CREATED. Neither shows up on a laptop.
  //
  // Rightward: the control now sits 1.5% off the stage edge, so a target
  // wider than that margin hangs off the page and a phone gets a sideways
  // scroll -- from an element that draws nothing.
  assert(out <= stage * (camR / 100),
    `the target hangs ${(out - stage * (camR / 100)).toFixed(1)}px past the stage and will scroll a phone`);
  // Leftward: the dial is pointer-events: none, so it cannot refuse a tap
  // the camera's target has already claimed. Cross the gap and tapping the
  // sun silently toggles the camera.
  const gap = stage * ((dialR - camR - Number(camW[1])) / 100);
  assert(back <= gap,
    `the target crosses the ${gap.toFixed(1)}px gap and turns taps on the dial into taps on the camera`);

  // It is a button, it says what it is, and it carries its state where a
  // screen reader can read it -- the icon alone announces as nothing.
  const tag = markup.slice(markup.indexOf('<button id="camera-toggle"'), markup.indexOf('</button>', markup.indexOf('<button id="camera-toggle"')));
  assert(/aria-pressed="false"/.test(tag), 'the camera control ships without a pressed state');
  assert(/aria-label="[^"]+"/.test(tag), 'the camera control has no accessible name');
  assert(/aria-hidden="true"/.test(tag), 'the icon is not hidden from the reader, so it doubles the label');
  assert(/\[aria-pressed='true'\]/.test(markup), 'the pressed state has no look, so the toggle is invisible');

  // This check has now been wrong twice in one day, both times by pinning
  // WHERE the behaviour lived rather than WHAT it does. It read
  // "placement only" after the behaviour landed, then read
  // `initCameraControl`'s body after the behaviour moved into
  // `setCameraMode`. Pin the contract, and slice the function that owns
  // each half of it.
  const fn = (name) => {
    const from = app.indexOf(`function ${name}(`);
    assert(from >= 0, `${name} no longer exists`);
    return app.slice(from, app.indexOf('\n}\n', from));
  };
  const mode = fn('setCameraMode');
  assert(/anim\.camera\.on = on/.test(mode), 'the toggle no longer drives the camera');
  assert(/setAttribute\(\s*'aria-pressed'/.test(mode), 'the pressed state is no longer kept in step');
  // Reduced motion never runs the rAF loop, so without an explicit redraw
  // the button is dead to the viewers likeliest to notice.
  assert(/anim\.redraw\(\)/.test(mode), 'the toggle waits for a frame that may never come');
  assert(/storeCamera\(\)/.test(mode), 'camera mode is not persisted (FR-018)');
  assert(/storeCamera\(\)/.test(fn('setFollow')), 'the followed kitty is not persisted (FR-019)');
  assert(/setCameraMode\(/.test(fn('initCameraControl')), 'the control is not wired to the toggle');
  // FR-027 at the level where it would actually be broken. The Camera
  // class is checked separately, but the toggle lives HERE, and a mutation
  // clearing the follow inside setCameraMode passed the whole suite until
  // this line existed.
  assert(!/followId/.test(mode),
    'setCameraMode touches the follow -- the toggle governs scale alone (FR-027)');
  assert(/initCameraControl\(\);/.test(app), 'the camera control is never wired up');
});
check("the about survives a phase change, and the owner's words survive us", () => {
  const markup = readFileSync(join(here, 'index.html'), 'utf8');

  // A card in the panel with its own type (owner, 2026-08-14/15), not a
  // <details> in the header and not a kitty card. Two properties carried
  // over from the header version, and both are the reason it is static
  // markup rather than a built card:
  //   - it works with NO SCRIPT. A dead socket, reduced motion, before
  //     app.js runs or after it throws. "What is this place" should be the
  //     last thing on the page to break, not the first.
  //   - it collapses on its own, independently of the kitty cards, which a
  //     <details> gives for free with no state to remember.
  assert(!/<details class="about"/.test(markup), 'the about went back into the header');
  assert(!/buildAboutCard/.test(readFileSync(join(here, 'app.js'), 'utf8')),
    'the about card is built in JS, so it vanishes whenever app.js does');
  const at = markup.indexOf('<aside class="about-card">');
  assert(at > 0, 'the about card is gone');
  const card = markup.slice(at, markup.indexOf('</aside>', at));
  assert(/<details>/.test(card) && /<summary>/.test(card),
    'the about no longer collapses without script');
  assert(!/cards-collapsed/.test(card), 'the about was tied to the kitty cards\' collapse');

  // The h2 is for the page OUTLINE -- CloudKitty is the h1 and this is a
  // real section, unlike a kitty card's `.name`, which is a data chip. Its
  // size is a separate question and lives in CSS.
  assert(/<h2>/.test(card), 'the about card has no heading, so the page has no outline for it');

  // It must cost the map NOTHING, and the header lost its second line
  // entirely: `resizeFor` subtracts `boxOf('header')` from the map's height
  // budget, and at a 20-row world ~20px of header is a whole pixel off the
  // tile -- which is 20px off each edge of the map.
  const header = markup.slice(markup.indexOf('<header'), markup.indexOf('</header>'));
  assert(!/about/i.test(header), 'the about is back in the header, where it costs the map a row');
  assert(!/class="subtitle"|class="tagline"/.test(markup),
    'the tagline is still in the header, so the header still has a second line');

  // At the TOP of the stack the cards are appended to (owner, 2026-08-15).
  // The previous version of this asserted the opposite -- that About sat
  // outside the columns -- by checking it came after the last column's
  // opening tag. That is also true when it is INSIDE that column, so the
  // check went on passing through the move without noticing. Position is
  // asserted against the column's closing tag now, which cannot be read
  // both ways.
  const panel = markup.slice(markup.indexOf('<section class="panel"'), markup.indexOf('</section>'));
  const lastCol = panel.lastIndexOf('<div class="panel-col">');
  const aboutAt = panel.indexOf('about-card');
  assert(aboutAt > lastCol && aboutAt < panel.indexOf('</div>', lastCol),
    'the about card is no longer inside the last panel column');

  // Which puts it in the way of two things that manage that column, and
  // both have to spare it. A roster change must not empty the column out
  // from under it, and the side-to-side carry must move only cats.
  const app = readFileSync(join(here, 'app.js'), 'utf8');
  const rebuild = app.slice(app.indexOf('if (needsRebuild) {'), app.indexOf('const built = cards();'));
  assert(!/innerHTML = ''/.test(rebuild),
    'the roster rebuild empties the column, which deletes the about card with it');
  assert(/querySelectorAll\('\.kitty-card'\)/.test(rebuild),
    'the roster rebuild no longer removes the kitty cards specifically');
  const place = app.slice(app.indexOf('function placeCards'), app.indexOf('// Sized for the GESTURE'));
  assert(!/children\.length/.test(place),
    'placeCards counts every child again, so the about card corrupts its split');

  // The owner's copy, verbatim. Ours to lay out, not to edit -- both the
  // line that shows closed and the paragraph behind it.
  const lede = 'a small, safe world where kitties frolic and play';
  // The heading now rides inside the summary so `more…` can share its line,
  // so the lede is the summary's text rather than its whole content.
  const summary = card.slice(card.indexOf('<summary>'), card.indexOf('</summary>'));
  assert(summary.includes(lede), 'the closed line has drifted from the owner\'s');
  assert(summary.includes('<h2>'), 'the heading left the summary, so `more…` has no line to share');
  const wanted =
    'CloudKitty is a peaceful meadow where kitties wander, eat, drink, nap in ' +
    'sunbeams, groom each other, chase bugs, and meow about it. The kitties are ' +
    'a team. Each kitty is driven by a neural network trained for one objective: ' +
    'the happiness of all the kitties in the meadow. The kitties look out for ' +
    'each other, communicate with purrs and meows, and keep each other company ' +
    'as they frolic and play.';
  const got = card.slice(card.indexOf('<p>') + 3, card.indexOf('</p>')).split(/\s+/).join(' ').trim();
  assert(got === wanted, `the about text has drifted from what the owner wrote:\n  ${got}`);

  // And the trap this page has already fallen into once (#193): the four
  // inverting tokens SWAP across a phase, so any colour written as a
  // literal here sits at the wrong end of the palette for half the day.
  for (const selector of ['.about-card', '.about-card h2', '.about-card summary', '.about-card p']) {
    const start = markup.indexOf(`  ${selector} {`);
    assert(start > 0, `no CSS rule for ${selector}`);
    const rule = markup.slice(start, markup.indexOf('}', start) + 1);
    const colours = rule.match(/(?:^|[^-])(?:color|background)\s*:\s*([^;]+);/g) || [];
    for (const c of colours) {
      assert(/var\(--/.test(c), `${selector} names a colour literal (${c.trim()}), wrong for half the day`);
    }
  }
});
check('the about names the kind of mind, and which one', () => {
  // Evaluated, not regexed. This function's whole job is to pick between
  // four outcomes, and a source match cannot tell which one it picks -- the
  // same mistake that let a glossed `mew` through the first meow check.
  // It closes over nothing but its own arguments, so it lifts out cleanly.
  const app = readFileSync(join(here, 'app.js'), 'utf8');
  const start = app.indexOf('function mindTextFor(');
  assert(start > 0, 'mindTextFor is gone');
  const end = app.indexOf('\n}', start);
  assert(end > start, 'could not find the end of mindTextFor');
  const src = app.slice(start, end + 2);
  assert(/behavior_description/.test(src), 'the extracted source is not the right function');
  const mindTextFor = eval(`(${src})`);

  const seat = (behavior, behavior_description) => ({ behavior, behavior_description });
  const world = (...ks) => ({ kitties: ks });

  // A policy seat post-034: the registry says WHAT, the config says WHICH.
  const miso = seat('policy:attn-a1-s1', 'Transformer');
  assert(mindTextFor(miso, world(miso)) === 'Transformer (attn-a1-s1)',
    `policy seat reads "${mindTextFor(miso, world(miso))}"`);
  // A scripted seat takes no parenthetical -- there is no artifact to name.
  const clem = seat('needs_driven', 'Scripted');
  assert(mindTextFor(clem, world(clem)) === 'Scripted',
    `scripted seat reads "${mindTextFor(clem, world(clem))}"`);
  // A plugin, told apart from an old engine by its NEIGHBOURS carrying
  // descriptions. This is the assertion that stops "Plugin" from being
  // printed over every cat on a pre-034 world.
  const plug = seat('my_plugin', undefined);
  assert(mindTextFor(plug, world(miso, plug)) === 'Plugin',
    `plugin reads "${mindTextFor(plug, world(miso, plug))}"`);
  // ...and the same kitty shape on a pre-034 world is NOT a plugin.
  assert(mindTextFor(plug, world(plug, seat('needs_driven', undefined))) === 'my_plugin',
    'a pre-034 world was read as plugins');
  // The live box today: policy seats, no descriptions anywhere. Must still
  // render the id exactly as it does before this change ships.
  const pre = seat('policy:attn-a1-s1', undefined);
  assert(mindTextFor(pre, world(pre, seat('policy:attn-a1-s3', undefined))) === 'attn-a1-s1',
    `a pre-034 policy seat reads "${mindTextFor(pre, world(pre))}"`);
  // A described policy seat NEVER falls to "Plugin", even sitting in a world
  // that describes others. A 034 engine refuses to start an undescribed
  // policy (the artifact has to be recertified first), so this state can
  // only be an old engine -- and calling it a plugin would be the one thing
  // it definitely is not.
  assert(mindTextFor(pre, world(miso, pre)) === 'attn-a1-s1',
    `an undescribed policy seat reads "${mindTextFor(pre, world(miso, pre))}"`);
  assert(mindTextFor({}, world()) === 'no policy seated', 'an unseated cat says nothing sensible');
});
check('every cat on the roster wears her own coat', () => {
  // The index IS the kitty id, so re-ordering PALETTES re-coats a cat and
  // nothing else complains. That is how Clementine came to be dark: she was
  // added to the config as id 5 and the array's index 5 held 'midnight',
  // while the white 'cloud' written for her sat unused at 6.
  //
  // Pinned by NAME, per id, because the failure mode is positional. An
  // assertion written as PALETTES[5] would move along with the bug.
  for (const [id, coat] of [[1, 'seal point'], [2, 'biscuit tabby'],
    [3, 'pumpkin tabby'], [4, 'storm'], [5, 'cloud']]) {
    assert(CatV2.appearanceFor(id).name === coat,
      `kitty ${id} wears "${CatV2.appearanceFor(id).name}", not "${coat}"`);
  }
  // And the one that would have caught it without knowing the coat's name:
  // she is the white cat, so hers must be the lightest coat on the roster.
  const lum = (hex) => {
    const n = parseInt(hex.slice(1), 16);
    return 0.2126 * ((n >> 16) & 255) + 0.7152 * ((n >> 8) & 255) + 0.0722 * (n & 255);
  };
  const clementine = lum(CatV2.appearanceFor(5).furBase);
  for (const id of [1, 2, 3, 4]) {
    assert(clementine > lum(CatV2.appearanceFor(id).furBase),
      `kitty ${id} has a lighter coat than the white cat`);
  }
});
check('every word the engine can say has a bubble', () => {
  // Read the vocabulary from the ENGINE, not from a list restated here. The
  // spec-033 gap this guards was exactly a restatement going stale: the
  // client's map still said `follow_me` months after the engine renamed it
  // to `mew`, and all four Here words plus chirp fell through to the '…'
  // fallback -- graceful, silent, and wrong in every bubble.
  //
  // Coupling to a Rust path is deliberate. It is the only thing that would
  // have caught this, and if the file moves, this failing is the correct
  // outcome: the vocabulary's home changed and the client's copy needs a
  // human look. A skip here would pass while saying nothing.
  const meowRs = join(here, '..', 'crates', 'cloudkitty-core', 'src', 'meow.rs');
  assert(existsSync(meowRs), `the engine vocabulary moved from ${meowRs}`);
  const rust = readFileSync(meowRs, 'utf8');
  const body = rust.slice(rust.indexOf('pub fn wire_name'));
  const kinds = [...body.slice(0, body.indexOf('\n    }')).matchAll(/=>\s*"([a-z_]+)"/g)]
    .map((m) => m[1]);
  assert(kinds.length >= 15, `only parsed ${kinds.length} kinds out of meow.rs`);

  // Read the EVALUATED table, not the source text. The first cut of this
  // check sliced the object literal, and a mutation that glossed `mew` on
  // the line after it sailed straight through -- the table is built in two
  // steps and only the finished value is what a bubble reads.
  for (const kind of kinds) {
    assert(typeof MEOW_TEXT[kind] === 'string' && MEOW_TEXT[kind],
      `the engine can say "${kind}" and the client draws '…' for it`);
  }
  // The free register is shown as the sound itself. Glossing one would put a
  // meaning on a word whose predicate does not carry it (FR-002b), so the
  // rule is asserted rather than the presence of an entry.
  assert(SOUND_WORDS.length === 4, `expected 4 sound-words, found ${SOUND_WORDS.length}`);
  for (const word of SOUND_WORDS) {
    assert(MEOW_TEXT[word] === word,
      `${word} is a sound-word but renders as "${MEOW_TEXT[word]}"`);
  }
  // The owner's copy ships verbatim, and each Here word must land on the
  // kind whose law it describes -- warm is the sunbeam, bug is the critter.
  // Mapping these by the order she wrote them would have crossed both.
  for (const [kind, copy] of [['here_food', 'Here food!'], ['here_water', 'Here drink!'],
    ['here_critter', 'Here bug!'], ['here_sunbeam', 'Here warm!']]) {
    assert(MEOW_TEXT[kind] === copy,
      `${kind} reads "${MEOW_TEXT[kind]}", not "${copy}"`);
  }
  // Pre-wall the served box still emits follow_me; dropping it before the
  // cutover deletes the only bubble that word draws today.
  assert(MEOW_TEXT.follow_me, 'follow_me is gone, and the pre-wall box still emits it');
});
check('a cat turns to the bowl it is drinking from, and then stays put', () => {
  // Owner, 2026-08-16: a cat drank from a pond on its left while facing
  // right. Two halves to the fix and the second is the one with teeth --
  // turning must not buy more flipping.
  const P = api.Presentation;
  const pres = new P();
  const el = (id, kind, x, y, extra = {}) => ({ id, kind, pos: { x, y }, ...extra });
  const elements = [el(1, 'water', 4, 5), el(2, 'chow', 9, 9, { servings: 3 })];
  const at = (x, y, action) => ({
    tick: 1, width: 20, height: 20, elements,
    kitties: [{ id: 1, pos: { x, y }, needs: {}, last_action: { action } }],
  });
  const feed = (w, t) => { w.tick = t; pres.pushState(w, t * 1000); };

  // Walk east so the cat is genuinely facing away, then drink from a pond
  // one tile to its WEST.
  feed(at(4, 5, 'move'), 1);
  feed(at(5, 5, 'move'), 2);
  assert(pres.facingFor(1) === 'right', `walked east but faces ${pres.facingFor(1)}`);
  feed(at(5, 5, 'drink'), 3);
  assert(pres.facingFor(1) === 'left', `did not turn to the pond: ${pres.facingFor(1)}`);

  // ...and it STAYS. Nine more ticks of the same meal must not flip it,
  // and must not restamp a turn -- a re-turn every tick is exactly the
  // flipping the owner asked us not to add.
  const turnAt = pres.turns.get(1);
  for (let t = 4; t < 13; t++) {
    feed(at(5, 5, 'drink'), t);
    assert(pres.facingFor(1) === 'left', `flipped mid-meal at tick ${t}`);
  }
  assert(pres.turns.get(1) === turnAt, 'the meal restamped the turn, so the cat re-pivots every tick');
  // Idling afterward keeps it too: only a move may re-face a cat.
  feed(at(5, 5, 'idle'), 13);
  assert(pres.facingFor(1) === 'left', 'the facing did not survive the end of the meal');

  // A served STEP outranks the meal. The engine applies one action a tick,
  // so a cat cannot really move and drink at once -- but the precedence is
  // stated in code and is worth stating here too, because the day it stops
  // holding, a walking cat starts being aimed at furniture it passed.
  // The step has to land the cat STILL BESIDE the pond, or both branches
  // agree by default and the case proves nothing -- the first version
  // walked out of range and passed whatever the code did.
  const pres3 = new P();
  const step = (x, action, t) => pres3.pushState({
    tick: t, width: 20, height: 20, elements,
    kitties: [{ id: 1, pos: { x, y: 5 }, needs: {}, last_action: { action } }],
  }, t * 1000);
  step(4, 'move', 1); // stood in the pond at (4,5)
  step(5, 'drink', 2); // stepped EAST out of it, pond now one tile west
  assert(pres3.facingFor(1) === 'right', `a served step lost to the bowl: ${pres3.facingFor(1)}`);

  // A bowl straight above carries no left-right information, so the cat is
  // left exactly as it was rather than being turned to an invented side.
  const pres2 = new P();
  const above = [el(3, 'chow', 5, 4, { servings: 1 })];
  const w = (action) => ({
    tick: 1, width: 20, height: 20, elements: above,
    kitties: [{ id: 1, pos: { x: 5, y: 5 }, needs: {}, last_action: { action } }],
  });
  pres2.pushState({ ...w('move'), kitties: [{ id: 1, pos: { x: 4, y: 5 }, needs: {}, last_action: { action: 'move' } }] }, 1000);
  pres2.pushState({ ...w('move'), tick: 2 }, 2000);
  const before = pres2.facingFor(1);
  pres2.pushState({ ...w('eat'), tick: 3 }, 3000);
  assert(pres2.facingFor(1) === before, `a bowl due north turned the cat ${pres2.facingFor(1)}`);
});

check('which bowl a cat turns to is the engine\'s choice, not the array\'s order', () => {
  // The engine picks the NEAREST adjacent element of the kind, ties broken
  // by lowest id, and for chow only bowls that still hold a serving. This
  // is a port of that predicate, so it is pinned against the rule rather
  // than against one happy case -- a disagreement here aims a cat at a
  // bowl it is not eating from.
  const pick = api.nearestAdjacentOf;
  const at = (id, kind, x, y, extra = {}) => ({ id, kind, pos: { x, y }, ...extra });
  const me = { x: 5, y: 5 };

  // Out of range: manhattan 2 is not adjacent, even diagonally.
  assert(!pick([at(1, 'water', 7, 5)], me, 'water'), 'reached a tile two away');
  assert(!pick([at(1, 'water', 6, 6)], me, 'water'), 'reached diagonally');
  // The cat's own tile counts -- that is a cat drinking while stood in it.
  assert(pick([at(1, 'water', 5, 5)], me, 'water')?.id === 1, 'its own tile did not count');
  // Nearest wins, and the ids are deliberately set AGAINST it: the nearer
  // tile carries the higher id, so a sort key that forgot distance would
  // pick the other one. Written the obvious way round first, it passed
  // that mutation by coincidence.
  const far = at(2, 'water', 4, 5); // distance 1
  const near = at(9, 'water', 5, 5); // distance 0, higher id
  assert(pick([far, near], me, 'water').id === 9, 'distance 0 lost to distance 1');
  assert(pick([near, far], me, 'water').id === 9, 'and it depends on array order');
  // Ties break by LOWEST id, whichever way the array is written.
  const l = at(9, 'water', 4, 5);
  const r = at(3, 'water', 6, 5);
  assert(pick([l, r], me, 'water').id === 3, 'tie did not break to the lowest id');
  assert(pick([r, l], me, 'water').id === 3, 'the tie-break depends on array order');
  // An empty bowl is not a meal, so it is not the thing to face.
  assert(!pick([at(1, 'chow', 4, 5, { servings: 0 })], me, 'chow'), 'faced an empty bowl');
  assert(pick([at(1, 'chow', 4, 5, { servings: 0 }), at(2, 'chow', 6, 5, { servings: 2 })], me, 'chow').id === 2,
    'the empty bowl beat the stocked one');
  // Water has no servings field at all; requiring one would break drinking.
  assert(pick([at(1, 'water', 4, 5)], me, 'water')?.id === 1, 'water needed a servings field');
});

check('a hunt whose quarry is gone is over, but a missing field is not', () => {
  // Owner, 2026-08-16: hunter eyes with no bug anywhere near. The gate reads
  // `dist !== null && dist > gate`, so null never gates -- and BOTH "I do
  // not understand this target" and "that bug no longer exists" used to
  // return null. Only the first deserves the benefit of the doubt.
  const bug = { id: 7, kind: 'bug', pos: { x: 5, y: 5 } };
  const world = (els) => ({ tick: 1, width: 20, height: 20, elements: els, kitties: [] });
  const cat = (target) => ({ id: 1, pos: { x: 5, y: 5 }, pursuit: target ? { target } : undefined });

  const measured = pursuitDistanceFor(cat({ target: 'element', id: 7 }), world([bug]));
  assert(measured === 0, `a served quarry measured ${measured}`);
  // The one that matters: well-formed, and names something the world does
  // not have. The payload IS the whole world, so this is evidence.
  const gone = pursuitDistanceFor(cat({ target: 'element', id: 7 }), world([]));
  assert(gone === Infinity, `a vanished quarry gave ${gone}, so the gate cannot fire`);
  // Shapes this does not understand keep their benefit of the doubt.
  assert(pursuitDistanceFor(cat(null), world([bug])) === null, 'no pursuit is not null');
  assert(pursuitDistanceFor(cat({ target: 'element' }), world([])) === null,
    'a target with no id was treated as a vanished quarry');
  assert(pursuitDistanceFor(cat({ target: 'wat', id: 7 }), world([])) === null,
    'an unrecognised target kind was treated as a vanished quarry');

  // Composed through the face, which is what the viewer sees.
  const P = api.Presentation;
  const pres = new P();
  // The applied action is part of the shape now (a pursuit on file is not a
  // pursuit in progress), and every served kitty carries one -- so a fixture
  // without it tests a cat the server cannot produce. This check is about
  // the DISTANCE gate, so the action is held at a hunting one throughout.
  const chasing = { action: 'chase', target: 'element', id: 7 };
  const faceFor = (els, at) => {
    const k = { id: 1, pos: { x: 5, y: 5 }, pursuit: { target: { target: 'element', id: 7 } }, last_action: chasing };
    const w = world(els);
    return pres.expressionFor(k, pursuitDistanceFor(k, w));
  };
  assert(faceFor([bug]) === 'focused', 'a real hunt lost its face');
  assert(faceFor([]) === undefined, 'THE BUG: the face survives its quarry vanishing');
  // And the gate itself, at the owner's 6.
  assert(api.VIEW.hunterGateTiles === 6, `the gate is ${api.VIEW.hunterGateTiles}, not 6`);
  assert(faceFor([{ ...bug, pos: { x: 11, y: 5 } }]) === 'focused', 'a quarry exactly 6 tiles off lost the face');
  assert(faceFor([{ ...bug, pos: { x: 12, y: 5 } }]) === undefined, 'a quarry 7 tiles off kept the face');
  // A malformed target still keeps it -- the defensive half is intact.
  const odd = { id: 1, pos: { x: 5, y: 5 }, pursuit: { target: { target: 'element' } }, last_action: chasing };
  assert(pres.expressionFor(odd, pursuitDistanceFor(odd, world([]))) === 'focused',
    'a missing field now costs a hunting cat its face');
});

check('no check left a dial moved behind it', () => {
  // Must be LAST. Half the file dials a value, draws, and puts it back;
  // one that forgets leaves every later check drawing a different cat,
  // and nothing else here can see it. It has already nearly happened
  // twice: a restore written as a literal 0 kept working right up until
  // the owner baked 1, at which point it would have quietly re-dialled
  // the swimming tail for the rest of the run.
  const moved = [];
  for (const [name, before] of Object.entries(SHIPPED_BLOCKS)) {
    const now = JSON.stringify(CatV2[name]);
    if (now !== before) moved.push(`${name}\n     shipped ${before}\n     left as ${now}`);
  }
  assert(
    moved.length === 0,
    `a check restored something to the wrong value:\n  ${moved.join('\n  ')}`,
  );
});

/* ---------------------------------------------------------------------
 * Camera mode (spec 036), Foundational phase.
 *
 * The claim this phase has to earn is that NOTHING MOVED: the whole
 * mechanism is in, and with the camera off the client draws exactly what
 * it drew before. Pixel-for-pixel proof needs a browser we do not have
 * here, so what these checks pin is the layer above it -- the numbers that
 * decide the pixels. If `across` is the world, `left`/`top` are zero, the
 * derived tile equals the tile `resizeFor` computes, and the ground bakes
 * at that same tile, then the drawing cannot differ.
 * ------------------------------------------------------------------- */

const camWorld = (width = 20, height = 20) => ({
  width,
  height,
  tick: 0,
  kitties: [
    { id: 1, pos: { x: 3, y: 4 } },
    { id: 2, pos: { x: 15, y: 12 } },
  ],
  elements: [],
});

/**
 * A view like the one anim hands the renderer, without standing one up.
 *
 * `ambient` is null on still frames because `viewAt` makes it null there
 * (anim.js, `ambient: still ? null : { now }`). The first cut of this
 * helper always supplied it, which is a shape the client cannot produce --
 * and that single divergence is what let the camera's clock bug pass a
 * green suite. A fixture that is easier than production tests nothing at
 * the seam.
 */
const camView = (still = false, now = 1000) => ({ still, ambient: still ? null : { now } });

check('the camera off frames the whole world and nothing else', () => {
  const world = camWorld();
  const cam = new api.Camera();
  cam.update(world, camView(), { aspect: 1, cssWidth: 1000 });
  assert(cam.across === world.width, `across is ${cam.across}, not the world's ${world.width}`);
  assert(cam.left === 0 && cam.top === 0, `origin moved to ${cam.left},${cam.top}`);
  assert(cam.anchorId === null, 'the off camera picked an anchor it has no use for');

  // The identity claim, in the one number that decides it. `resizeFor`
  // computes tile = floor(budget / world.width) and cssWidth = tile *
  // world.width, so cssWidth / across must give that tile back exactly.
  const tile = 31;
  const cssWidth = tile * world.width;
  assert(cssWidth / cam.across === tile, `the off camera would draw at ${cssWidth / cam.across}px, not ${tile}px`);
});

check('a non-square world keeps its shape through the camera', () => {
  const world = camWorld(24, 16);
  const cam = new api.Camera();
  // The canvas is world-aspect, so the vertical span follows from it.
  cam.update(world, camView(), { aspect: 16 / 24, cssWidth: 1000 });
  assert(cam.across === 24, `across is ${cam.across}`);
  assert(cam.left === 0 && cam.top === 0, `origin moved to ${cam.left},${cam.top} on a wide world`);
});

check('a frame wider than its world centres, and one inside it is held', () => {
  // Wider than the world: clamping to a range whose min exceeds its max
  // would pin the frame to an edge and put void on the other side. This
  // is every frame the camera draws while it is off, so it is not a
  // corner case.
  assert(api.clampFrame(-5, 20, 20) === 0, 'a frame exactly its world did not sit at the origin');
  assert(api.clampFrame(3, 20, 30) === -5, 'a frame wider than its world did not centre');
  // Inside the world: held, so a kitty in the corner never shows void.
  assert(api.clampFrame(-4, 20, 10) === 0, 'the frame escaped past the left edge');
  assert(api.clampFrame(18, 20, 10) === 10, 'the frame escaped past the right edge');
  assert(api.clampFrame(4, 20, 10) === 4, 'a frame already inside the world was moved');
});

check('the ground bakes at the whole-world tile while the camera is off', () => {
  const world = camWorld();
  const tile = 31;
  // Called on a stand-in rather than a real renderer: the method reads
  // four fields and the harness has no DOM to build the rest.
  const off = { cssWidth: tile * world.width, dpr: 2, camera: { on: false } };
  const baked = WorldRenderer.prototype.bakeTileFor.call(off, world);
  assert(baked === tile, `the off camera bakes at ${baked}px, not the ${tile}px it draws at`);
});

check('the ground bake is bounded, because an over-budget canvas comes back blank', () => {
  const world = camWorld();
  // A real Camera, not a stand-in with an `on` flag: `bakeTileFor` reads
  // the camera's OWN dials, and a stub without them is a world where the
  // two can disagree without anything noticing.
  const cam = new api.Camera();
  cam.on = true;
  const on = { cssWidth: 1200, dpr: 2, camera: cam };
  const baked = WorldRenderer.prototype.bakeTileFor.call(on, world);
  const side = baked * Math.max(world.width, world.height) * on.dpr;
  assert(side <= 4096, `the bake would be ${Math.round(side)} device px a side`);
  assert(baked > 0, 'the clamp collapsed the bake');
  // And it follows the camera's dials rather than the module's. Under 037
  // a "tighter" camera is one with a BIGGER pixel floor -- it zooms in
  // further, so it frames fewer tiles and bakes a larger tile.
  const tight = new api.Camera({ ...api.VIEW.camera, floorPx: 80, minTiles: 4 });
  tight.on = true;
  const tighter = WorldRenderer.prototype.bakeTileFor.call(
    { cssWidth: 400, dpr: 1, camera: tight },
    world,
  );
  // 400 / 80 = 5 tiles, which clears its own minTiles of 4, so the floor is
  // 5 tiles and the bake tile is 80px -- the pixel target exactly, which is
  // the property that makes the bake stop scaling with the display.
  assert(tighter === 80, `a tighter camera baked at ${tighter}, not its own 80px floor`);
});

check('the camera-off bake is what shipped, at every dpr', () => {
  // The budget clamp used to apply to the off path too. On a dpr-4
  // display that magnified the ground AND made `this.tile / bakeTile`
  // differ from 1, which pushes the off-state pond path through the
  // ctx.scale branch its own comment promises it never takes. "Nothing
  // moved" has to hold at every dpr, not the ones I thought of.
  const world = camWorld();
  const tile = 60;
  for (const dpr of [1, 2, 3, 4, 5]) {
    const off = { cssWidth: tile * world.width, dpr, camera: new api.Camera() };
    const baked = WorldRenderer.prototype.bakeTileFor.call(off, world);
    assert(baked === tile, `at dpr ${dpr} the off camera bakes at ${baked}, not ${tile}`);
  }
});

check('screen to world inverts the frame the camera laid down', () => {
  const world = camWorld();
  const tile = 62; // camera scale, 10 across on a 620px map
  const cam = new api.Camera();
  cam.on = true;
  cam.update(world, camView(), { aspect: 1, cssWidth: 1000 });
  // The display scale is the trap here: the canvas's measured size is not
  // its drawing size, so a conversion through cssWidth rather than the
  // measured rect lands on the wrong kitty at some viewports.
  const stub = {
    cssWidth: 620,
    cssHeight: 620,
    tile,
    camera: cam,
    canvas: { getBoundingClientRect: () => ({ left: 10, top: 20, width: 310, height: 310 }) },
  };
  const hit = WorldRenderer.prototype.toWorld.call(stub, 10 + 155, 20 + 155);
  // Halfway across a half-scale canvas is halfway across the frame.
  const wantX = cam.left + 620 / 2 / tile;
  assert(Math.abs(hit.x - wantX) < 1e-9, `x came back ${hit.x}, wanted ${wantX}`);
  assert(Math.abs(hit.y - (cam.top + 620 / 2 / tile)) < 1e-9, `y came back ${hit.y}`);
});

check('the camera reads the world and never writes to it', () => {
  // Article V is the constitution's one article this feature engages, and
  // it is cheaper to assert than to remember.
  const world = camWorld();
  const before = JSON.stringify(world);
  const cam = new api.Camera();
  cam.on = true;
  for (let i = 0; i < 5; i += 1) cam.update(world, camView(false, 1000 + i * 16), { aspect: 1, cssWidth: 1000 });
  assert(JSON.stringify(world) === before, 'the camera mutated the world it was handed');
});

check('a still view arrives, and leaves the clock where it found it', () => {
  const world = camWorld();
  const cam = new api.Camera();
  cam.on = true;

  cam.update(world, camView(false, 5000), { aspect: 1, cssWidth: 1000 });
  assert(cam.lastAt === 5000, 'an animated frame did not set the clock');

  // A still frame carries no clock. It must arrive at its target AND
  // leave `lastAt` alone -- storing 0 here is storing the sentinel that
  // means "never ran", so the next animated frame loses its dt.
  cam.update(world, camView(true), { aspect: 1, cssWidth: 1000 });
  assert(cam.lastAt === 5000, `a still frame moved the clock to ${cam.lastAt}`);
});

check('the camera reaches the renderer by the tile, never by a context scale', () => {
  const body = renderSrc.slice(renderSrc.indexOf('applyCamera(world, view, dpr)'));
  const fn = body.slice(0, body.indexOf('\n  }'));
  assert(/this\.tile = this\.cssWidth \/ cam\.across/.test(fn), 'applyCamera no longer sets the tile');
  assert(/setTransform\(/.test(fn), 'applyCamera no longer lays down the pan');
  // `this.tile` is what every art dial is a fraction of -- it was also what
  // the 44px `fine` gate read, until that was deleted. Scaling the context
  // would magnify the small-size drawing and leave `fine` reading the old
  // number: bigger cats still wearing their 31px detail.
  assert(!/ctx\.scale\(/.test(fn), 'applyCamera scales the context, which leaves `fine` blind to the zoom');
});

check('the wiring that would ship inert is asserted, not assumed', () => {
  // A renderer with no camera falls back to the whole-world view, which
  // is indistinguishable from a correct off state -- so a dropped
  // assignment in anim.init would ship silently. render.js has done this
  // before (the axial whip shipped inert for exactly this reason).
  const init = animSrc.slice(animSrc.indexOf('init(renderer) {'));
  assert(
    /renderer\.camera = this\.camera/.test(init.slice(0, init.indexOf('\n  },'))),
    'anim.init no longer hands the renderer its camera',
  );
  // And the camera must be advanced from draw, not from the rAF loop:
  // startLoop is skipped entirely under reduced motion, so a camera
  // driven from there is frozen for those viewers while testing fine.
  const drawBody = renderSrc.slice(renderSrc.indexOf('  draw(world, view) {'));
  assert(
    /this\.applyCamera\(world, view, dpr\)/.test(drawBody.slice(0, drawBody.indexOf('\n    this.blitGround'))),
    'draw no longer advances the camera, so reduced motion would freeze it',
  );
  assert(
    !/camera\.update\(/.test(animSrc.slice(animSrc.indexOf('startLoop() {'), animSrc.indexOf('stopLoop() {'))),
    'the camera is advanced from the rAF loop, which reduced motion never runs',
  );
});

check('the pond cache keys on everything it bakes', () => {
  // Two independent staleness bugs, found a day apart. The PALETTE is
  // baked into the shore and lip layers (fixed on main); the TILE is what
  // the paths are built at (the camera's doing). Either one missing from
  // the key is a silent wrong-looking pond, so both are pinned here --
  // and a merge that keeps one side of this line is exactly how one of
  // them would get dropped.
  const body = renderSrc.slice(renderSrc.indexOf('drawPondLayer(world, view) {'));
  const fn = body.slice(0, body.indexOf('\n  }'));
  const sig = fn.match(/const signature = `([^`]*)`/);
  assert(sig, 'the pond signature is no longer a template literal');
  assert(/\$\{this\.paletteKey\}/.test(sig[1]), 'the pond signature dropped the palette');
  assert(/\$\{bakeTile\}/.test(sig[1]), 'the pond signature dropped the tile');
  assert(/buildPondPath\(tiles, bakeTile\)/.test(fn), 'pond paths are not built at the bake tile');
});

/* ---- US1: the camera holds the group (spec 036 FR-003..FR-010, FR-029) ---- */

/** A world with the kitties placed exactly where a case needs them. */
const camAt = (...spots) => ({
  width: 20,
  height: 20,
  kitties: spots.map(([x, y], i) => ({ id: i + 1, pos: { x, y } })),
  elements: [],
});
const onCam = (world, view = camView()) => {
  const cam = new api.Camera();
  cam.on = true;
  cam.update(world, view, { aspect: 1, cssWidth: 1000 });
  return cam;
};

check('nominal is a floor a huddled group cannot push through', () => {
  // Everyone on one tile: the fit collapses and nominal has to hold, or a
  // gathered clowder zooms until the meadow is two cats and a bowl.
  const cam = onCam(camAt([10, 10], [10, 10], [10, 10]));
  // A huddled group sits ON the floor, and the floor IS the pixel target --
  // asserted as the TILE rather than the tile count, because the tile is the
  // thing the dial names and the count is just 1000/113.
  assert(Math.abs(1000 / cam.across - api.VIEW.camera.floorPx) < 1e-9,
    `huddled group sat at a ${(1000 / cam.across).toFixed(1)}px tile, not the ${api.VIEW.camera.floorPx}px floor`);
});

check('the ceiling binds, and the wanderer is let go', () => {
  // Opposite corners of a 20-tile world: fitting both needs ~25 tiles.
  const cam = onCam(camAt([0, 0], [19, 19]));
  // 1000/50 asks for 20 tiles of a 20-tile world, so the MIN-ZOOM CAP is what
  // stops it: 20/1.5 = 13.33 tiles. The old `world - 1` backstop allowed 19,
  // which is one tile of crop and indistinguishable from camera-off -- the
  // fault reported from WQHD on 2026-08-19.
  const cap = 20 / api.VIEW.camera.minZoomVsBase;
  assert(Math.abs(cam.across - cap) < 1e-9,
    `scattered group sat at ${cam.across.toFixed(2)}, not the ${cap.toFixed(2)}-tile min-zoom cap`);
  // And the frame really is smaller than the world, which is what "let
  // her leave" means -- the roster accounts for whoever is off-screen.
  assert(cam.across < 20, 'the ceiling did not actually crop the world');
});

// The supported viewport range, swept the way FR-010 requires: 20px steps
// from the smallest phone map to the 1200px cap, plus the widths the spec's
// own Overview table names. One sweep, shared by every criterion below, so
// they cannot silently disagree about what "supported" means.
const ZOOM_SWEEP = (() => {
  const widths = [];
  for (let w = 340; w <= 1200; w += 20) widths.push(w);
  for (const named of [460, 640, 1000]) if (!widths.includes(named)) widths.push(named);
  return widths.sort((a, b) => a - b);
})();
const zoomWorld = { width: 20, height: 20, elements: [], kitties: [] };
const zoomLimits = (w) => new api.Camera().limitsFor(zoomWorld, w);

check('no viewport draws a kitty smaller than the portrait cards', () => {
  // This replaces SC-001's factor-of-2 size band, WITHDRAWN by the owner on
  // 2026-08-19. The band capped the largest floor tile over the smallest
  // ACROSS ALL VIEWPORTS, and the reason it went is that no user ever
  // experiences that ratio -- everyone has one device and sees one size.
  //
  // Its last act was to forbid `minTiles: 7`, which its own margin note had
  // predicted in as many words: "raising it further means lowering minTiles
  // and paying for it in phone framing". At 7 the band measures 2.33x. So
  // the criterion did not fail here, it fired -- and it was already retired.
  //
  // What survives is the per-device bar the ratio was standing in for.
  // PORTRAIT_CAT is the size the cat art is actually dialled against, and it
  // is where `ceilingPx: 50` came from in the first place, so the honest
  // invariant is that nothing in the meadow is drawn smaller than the cards.
  //
  // Reported as NUMBERS, as SC-001 was, so a regression reads as a figure
  // rather than a boolean.
  const bar = appNum('PORTRAIT_CAT');
  const tiles = ZOOM_SWEEP.map((w) => w / zoomLimits(w).floorTiles);
  assert(tiles.length >= 40, `the sweep only sampled ${tiles.length} widths`);
  const smallest = Math.min(...tiles);
  assert(smallest >= bar,
    `the smallest floor tile is ${smallest.toFixed(1)}px, under the ${bar}px portrait cards `
    + `-- the range runs to ${Math.max(...tiles).toFixed(1)}px`);
});

check('the ceiling still crops on a world smaller than today\'s', () => {
  // Every other sweep here varies cssWidth against a fixed 20-tile world, so
  // nothing exercised the OTHER clamp. Found in review of PR #246: the floor
  // was capped at world.width while the ceiling was capped one tile below,
  // and the ceiling is then raised back to meet the floor -- so on a small
  // enough world the floor saturates at the world's own width and drags the
  // ceiling up with it. The camera then frames the whole world at every
  // zoom, camera-on becomes pixel-identical to camera-off, and 036 FR-005
  // and 037 FR-007 are both silently retired.
  //
  // Not reachable on today's 20x20 map -- MAP_MAX_PX caps cssWidth at 1200,
  // so the floor tops out at 12 tiles -- which is exactly why no existing
  // check saw it. Fog is expected to make the world BIGGER, but a spec that
  // says "a world that is not 20 tiles" in its edge cases should hold in
  // both directions.
  const cam = new api.Camera();
  for (const size of [6, 8, 10, 12, 14, 20, 40]) {
    const small = { width: size, height: size };
    for (const w of [340, 640, 1000, 1200]) {
      const { floorTiles, ceilingTiles } = cam.limitsFor(small, w);
      assert(ceilingTiles < size,
        `a ${size}-tile world at ${w}px frames ${ceilingTiles} of ${size} -- the camera stopped cropping`);
      assert(floorTiles <= ceilingTiles + 1e-9,
        `a ${size}-tile world at ${w}px inverted: floor ${floorTiles}, ceiling ${ceilingTiles}`);
      assert(floorTiles > 0 && Number.isFinite(floorTiles),
        `a ${size}-tile world at ${w}px gave a floor of ${floorTiles}`);
    }
  }
});

check('the ceiling always crops, on every supported viewport', () => {
  // SC-006. Expected to BIND at the large end on today's 20-tile world --
  // that is the Fog dependency -- so this asserts the clamp holds, not that
  // it never fires.
  let clamped = 0;
  for (const w of ZOOM_SWEEP) {
    const { ceilingTiles } = zoomLimits(w);
    assert(ceilingTiles < zoomWorld.width,
      `at ${w}px the ceiling frames ${ceilingTiles} of a ${zoomWorld.width}-tile world`);
    if (w / api.VIEW.camera.ceilingPx > ceilingTiles + 1e-9) clamped += 1;
  }
  // The clamp firing is expected; it firing NOWHERE would mean the world
  // stopped being the binding constraint and this check went vacuous.
  assert(clamped > 0, 'the world clamp never fired anywhere in the sweep');
});

check('the floor never frames fewer tiles than the minimum', () => {
  // FR-005/FR-006/SC-005. Where the minimum binds, the kitties must be drawn
  // SMALLER than the pixel target rather than the world being cropped
  // further -- so the tile is under floorPx exactly where the clamp is on.
  let bound = 0;
  for (const w of ZOOM_SWEEP) {
    const { floorTiles } = zoomLimits(w);
    assert(floorTiles >= api.VIEW.camera.minTiles - 1e-9,
      `at ${w}px the floor frames ${floorTiles}, under the ${api.VIEW.camera.minTiles}-tile minimum`);
    if (floorTiles > w / api.VIEW.camera.floorPx + 1e-9) {
      bound += 1;
      assert(w / floorTiles < api.VIEW.camera.floorPx,
        `at ${w}px the minimum binds but the tile is ${(w / floorTiles).toFixed(1)}px, `
        + `not under the ${api.VIEW.camera.floorPx}px target`);
    }
  }
  assert(bound > 0, 'the minimum never bound anywhere in the sweep');
});

check('a letterboxed canvas is capped in ROWS, and a square one is not', () => {
  // The landscape-only zoom limit (owner, 2026-08-20). `rows = across *
  // aspect`, so the cap in across is `ceilingRows / aspect`.
  //
  // Parametric on the aspect rather than pinned to a device: the large
  // viewport of a 16 Pro sideways still has not been measured, and the point
  // of stating the limit in ROWS is that the answer stops depending on it.
  const d = api.VIEW.camera;
  const cam = new api.Camera();

  // It is a MAXIMUM, not a target, and it is the WEAKEST of the limits rather
  // than an override. Two ways it legitimately does not hold:
  //
  //   below aspect 0.45, `minZoomVsBase` is tighter and the frame comes in
  //     UNDER the cap of its own accord;
  //   above aspect 6/7, `minTiles` demands more tiles across than 6 rows
  //     allows, and the FLOOR wins -- ceiling raised to meet it (FR-013),
  //     because "never frame fewer than 7 tiles" outranks "never more than 6
  //     rows". A nearly-square short window is the only place that happens.
  for (const aspect of [0.30, 0.40, 0.50, 0.545, 0.75, 0.95]) {
    const { floorTiles, ceilingTiles } = cam.limitsFor(zoomWorld, 720, aspect);
    assert(ceilingTiles * aspect <= d.ceilingRows + 1e-9
      || Math.abs(ceilingTiles - floorTiles) < 1e-9,
      `at aspect ${aspect} the ceiling frames ${(ceilingTiles * aspect).toFixed(2)} rows, `
      + `over the ${d.ceilingRows} allowed, and the floor (${floorTiles}) is not what is `
      + 'holding it there');
  }

  // ...and where the cap is genuinely the tightest of the three, it is the one
  // deciding the width. WHICH aspects those are is derived from the dial, not
  // listed: the crossover is `ceilingRows / wide`, so a hardcoded list silently
  // stops testing the cap the moment the dial moves. Found by mutation --
  // `ceilingRows: 7` failed this check for bookkeeping rather than for a
  // defect, which is the shape of a test that will be edited to pass one day.
  const wide = cam.limitsFor(zoomWorld, 720).ceilingTiles;
  const crossover = d.ceilingRows / wide;
  const binding = [0.30, 0.40, 0.50, 0.545, 0.75].filter((a) => a > crossover);
  assert(binding.length >= 2,
    `only ${binding.length} sampled aspects put the row cap in charge (crossover `
    + `${crossover.toFixed(2)}), so this witnesses almost nothing`);
  for (const aspect of binding) {
    const { ceilingTiles } = cam.limitsFor(zoomWorld, 720, aspect);
    assert(Math.abs(ceilingTiles - d.ceilingRows / aspect) < 1e-9,
      `at aspect ${aspect} the ceiling is ${ceilingTiles.toFixed(2)} tiles, not the `
      + `${(d.ceilingRows / aspect).toFixed(2)} the row cap allows`);
    assert(ceilingTiles < wide,
      `the cap did not tighten anything at aspect ${aspect}, so this proves nothing`);
  }
  // Below the crossover the min-zoom cap is tighter and this dial does nothing,
  // which is correct and worth pinning so the two cannot quietly swap.
  const below = crossover / 2;
  assert(Math.abs(cam.limitsFor(zoomWorld, 720, below).ceilingTiles - wide) < 1e-9,
    `at aspect ${below.toFixed(2)} the row cap bound before the min-zoom cap did`);

  // A SQUARE canvas is every viewport but a letterboxed one, and there rows
  // and across are the same number -- so an uncapped row limit would quietly
  // become an across limit and zoom in everywhere. Portrait is the case that
  // matters: it must be untouched.
  for (const aspect of [1, 1.2, null, undefined, NaN]) {
    for (const w of [380, 720, 1200]) {
      assert(cam.limitsFor(zoomWorld, w, aspect).ceilingTiles
        === cam.limitsFor(zoomWorld, w).ceilingTiles,
        `aspect ${aspect} moved the ceiling at ${w}px -- the row cap escaped the letterbox`);
    }
  }
});

check('the row cap reaches the camera, not just the derivation', () => {
  // The dial is computed in `limitsFor` and only bites if `update` hands it
  // the aspect. That argument is the whole feature and nothing else would
  // notice it going missing: `bakeTileFor` asks for the FLOOR and passes no
  // aspect at all, quite correctly, so a call site that forgot would look
  // exactly like a call site that should not pass it.
  const aspect = 0.545;
  const cam = new api.Camera();
  cam.on = true;
  // Spread far enough that the FIT wants more than the ceiling, so the camera
  // is pinned at its widest and the cap is what decides the width.
  const world = camAt([2, 2], [18, 18], [10, 3]);
  for (let i = 0; i < 400; i += 1) {
    cam.update(world, camView(false, i * 16.67), { aspect, cssWidth: 720 });
  }
  const rows = cam.across * aspect;
  assert(rows <= api.VIEW.camera.ceilingRows + 1e-6,
    `the camera settled at ${cam.across.toFixed(2)} tiles across = ${rows.toFixed(2)} rows, `
    + `over the ${api.VIEW.camera.ceilingRows} allowed -- update is not passing the aspect`);
  // And it is genuinely the cap doing it, not the fit happening to be small.
  const uncapped = new api.Camera({ ...api.VIEW.camera, ceilingRows: 0 });
  uncapped.on = true;
  for (let i = 0; i < 400; i += 1) {
    uncapped.update(world, camView(false, i * 16.67), { aspect, cssWidth: 720 });
  }
  assert(uncapped.across > cam.across + 0.01,
    `without the cap the camera settled at the same ${uncapped.across.toFixed(2)} tiles, `
    + 'so the fixture never reached the ceiling and this witnesses nothing');
});

check('the floor never crosses the ceiling', () => {
  // FR-013 and contract invariant 5. They may MEET -- that viewport simply
  // has no zoom range -- but an inversion would ask the camera to widen past
  // its own floor.
  //
  // Swept with the SHIPPED dials this cannot fail: 100/50/6 keeps the two
  // far apart everywhere in the supported range, so a check that only swept
  // them would be green for a reason unrelated to the guard. Caught by
  // mutation -- swapping the two pixel targets left this check silent while
  // seven others fired. So it is asserted where the clamp is actually
  // load-bearing: a minimum that reaches past the ceiling's own target.
  for (const w of ZOOM_SWEEP) {
    const { floorTiles, ceilingTiles } = zoomLimits(w);
    assert(floorTiles <= ceilingTiles + 1e-9,
      `at ${w}px the floor (${floorTiles}) is wider than the ceiling (${ceilingTiles})`);
  }
  // minTiles 12 with a 100px ceiling target: the floor is held at 12 tiles
  // while the ceiling target asks for 4. Without the clamp the ceiling would
  // come back NARROWER than the floor.
  const squeezed = new api.Camera({ ...api.VIEW.camera, floorPx: 100, ceilingPx: 100, minTiles: 12 });
  let met = 0;
  for (const w of ZOOM_SWEEP) {
    const { floorTiles, ceilingTiles } = squeezed.limitsFor(zoomWorld, w);
    assert(floorTiles <= ceilingTiles + 1e-9,
      `squeezed at ${w}px: floor ${floorTiles} is wider than ceiling ${ceilingTiles}`);
    if (Math.abs(floorTiles - ceilingTiles) < 1e-9) met += 1;
  }
  assert(met > 0, 'the squeezed case never made the two meet, so the clamp was never exercised');
});

check('a resize produces continuous limits, with no jump at either boundary', () => {
  // SC-009, swept in 1px steps across BOTH boundaries -- where minTiles
  // starts binding and where the world clamp does. A jump here is a visible
  // cut on a window drag, which 036 FR-008 forbids outright.
  let prev = null;
  let steps = 0;
  for (let w = 300; w <= 1250; w += 1) {
    const { floorTiles, ceilingTiles } = zoomLimits(w);
    if (prev) {
      // 1px of viewport can never move a limit by more than a small
      // fraction of a tile; anything larger is a discontinuity.
      assert(Math.abs(floorTiles - prev.floorTiles) < 0.05,
        `the floor jumped ${Math.abs(floorTiles - prev.floorTiles).toFixed(3)} tiles at ${w}px`);
      assert(Math.abs(ceilingTiles - prev.ceilingTiles) < 0.05,
        `the ceiling jumped ${Math.abs(ceilingTiles - prev.ceilingTiles).toFixed(3)} tiles at ${w}px`);
    }
    prev = { floorTiles, ceilingTiles };
    steps += 1;
  }
  assert(steps > 900, `the resize sweep only took ${steps} steps`);
});

check('applyCamera actually hands the camera its pixels', () => {
  // The feature's ONE structural change is that render.js passes cssWidth
  // into cam.update. Deleting that line is SILENT: `limitsFor` reads the
  // missing value as "not laid out yet", returns the whole world, and the
  // camera renders camera-off while claiming to be on. Verified by
  // mutation, 2026-08-18 -- with the line removed, all 300 checks passed.
  //
  // This client has shipped inert wiring before (see the note in
  // `applyCamera` about the tile assignment, and 036's axial-whip fix), so
  // the guard is behavioural rather than a source-text match: a regex would
  // pass on a line that computed the wrong number.
  const cam = new api.Camera();
  cam.on = true;
  const world = camAt([9, 10], [10, 10], [11, 10]); // huddled: the fit sits ON the floor
  const stub = {
    camera: cam,
    cssWidth: 1000,
    cssHeight: 1000,
    ctx: { setTransform() {} },
  };
  WorldRenderer.prototype.applyCamera.call(stub, world, camView(false, 1000), 1);
  assert(Math.abs(cam.across - 1000 / api.VIEW.camera.floorPx) < 1e-9,
    `applyCamera left the camera at ${cam.across.toFixed(2)} tiles, not the `
    + `${(1000 / api.VIEW.camera.floorPx).toFixed(2)} a 1000px map derives -- `
    + `${cam.across === world.width ? 'it framed the WHOLE WORLD, which is what a '
      + 'dropped cssWidth looks like' : 'the derivation is wrong'}`);
  // And the tile it hands the renderer really is the pixel target.
  assert(Math.abs(stub.tile - api.VIEW.camera.floorPx) < 1e-9,
    `the renderer got a ${stub.tile}px tile, not the ${api.VIEW.camera.floorPx}px target`);
});

check('a resize mid-ease moves the target without cutting the movement', () => {
  // SC-010. The easing itself is 036's and unchanged -- but 037 is what makes
  // the TARGET depend on cssWidth, so this case only became reachable with
  // this feature and had never been exercised (found by /speckit-converge).
  //
  // The failure it guards is a CUT: 036 FR-008 forbids the camera jumping,
  // and a resize is the one event that can move the width target by several
  // tiles at once.
  const cam = new api.Camera();
  cam.on = true;
  // THE FIXTURE IS THE HARD PART OF THIS CHECK, and it has caught me twice.
  // The camera sits at max(fit, floor), so unless the FIT is under the floor
  // at BOTH widths the test measures the fit and not the resize.
  //
  //   three kitties spread 2 tiles -> fit 7.2, governs at 640px (floor 6)
  //   two kitties one tile apart   -> fit 6.2, STILL governs at 640px
  //   two kitties on one tile      -> fit 5.2, under the floor at both  <-
  //
  // So they share a tile. Artificial, and deliberately so: the subject here
  // is the width target moving under an easing, and anything the fit touches
  // is noise in that measurement.
  const world = camAt([10, 10], [10, 10]);
  cam.update(world, camView(false, 0), { aspect: 1, cssWidth: 1000 });
  const settled = cam.across;
  const start = 1000 / api.VIEW.camera.floorPx;
  assert(Math.abs(settled - start) < 1e-9,
    `setup: expected the 1000px floor of ${start.toFixed(2)}, got ${settled.toFixed(2)}`);

  // The window narrows to 640. The target is read from the derivation rather
  // than written as a literal: this check's subject is the EASING -- that the
  // camera moves, does not cut, and converges -- and hard-coding the width
  // couples it to floorPx. It was `minTiles` until a mutation lowering floorPx
  // to 100 broke it for a reason having nothing to do with easing.
  //
  // Not circular: the fixture puts the fit below the floor at both widths, so
  // the floor IS the target, and every assertion below is about how the camera
  // travels to it rather than what it is.
  const wanted = cam.limitsFor(world, 640).floorTiles;
  cam.update(world, camView(false, 16.67), { aspect: 1, cssWidth: 640 });
  assert(cam.across < settled,
    `the camera ignored the resize and stayed at ${cam.across}`);
  assert(cam.across > wanted,
    `the camera CUT to ${cam.across} instead of easing toward ${wanted}`);

  // And it does arrive, rather than easing toward it forever.
  for (let i = 2; i < 400; i += 1) {
    cam.update(world, camView(false, i * 16.67), { aspect: 1, cssWidth: 640 });
  }
  assert(Math.abs(cam.across - wanted) < 0.01,
    `after 400 frames the camera sat at ${cam.across}, not the new ${wanted} floor`);
});

check('the limits follow the viewport on the SAME camera, not just a fresh one', () => {
  // FR-015: derived from the viewport as it is when the camera decides a
  // frame, never from a measurement taken earlier. `limitsFor`'s own comment
  // warns against caching the pair on the instance -- and every other check
  // here builds a FRESH Camera per width, so a per-instance cache would
  // satisfy all of them (found by /speckit-converge).
  const cam = new api.Camera();
  const world = { width: 20, height: 20 };
  const wide = cam.limitsFor(world, 1000);
  const narrow = cam.limitsFor(world, 640);
  assert(wide.floorTiles !== narrow.floorTiles,
    `the same camera reported floor ${wide.floorTiles} at both 1000px and 640px -- the pair is cached`);
  assert(wide.ceilingTiles !== narrow.ceilingTiles,
    `the same camera reported ceiling ${wide.ceilingTiles} at both widths -- the pair is cached`);
  // Back again, so a cache that merely lags by one call is caught too.
  const again = cam.limitsFor(world, 1000);
  assert(again.floorTiles === wide.floorTiles && again.ceilingTiles === wide.ceilingTiles,
    'the same viewport gave different limits on a second ask');
});

check('a cat is the same cat at every size', () => {
  // SC-003: fine detail cannot change state at any size, because the 44px
  // gate was deleted. Three files carried that gate -- cat-v2.js, props.js,
  // meadow.js -- and only the flowers were guarded (test-meadow). This is the
  // cats' half; the props' half is in test-meadow beside the flowers'.
  //
  // Asserted on the SHAPE of the command stream: same sequence of operations
  // at any size, only the coordinates differing. A returning gate changes the
  // shape and fires here instead of shipping quietly.
  const shapeAt = (size) => {
    const log = [];
    CatV2.drawCat(guardCtx(log), {
      pose: 'idle',
      appearance: CatV2.appearanceFor(3),
      facing: 'right',
      size,
      phase: 0.3,
    });
    return log.map((e) => (e[0] === 'set' ? `set:${e[1]}` : e[0])).join(',');
  };
  const small = shapeAt(20);
  assert(small.length > 0, 'nothing was drawn at all');
  for (const size of [21, 43, 44, 100]) {
    assert(shapeAt(size) === small,
      `a cat draws a different SHAPE at ${size}px than at 20px -- a size gate is back`);
  }
});

check('the floor is the pixel target and the ceiling is the min-zoom cap', () => {
  // This used to assert "1000 / 100 = 10 tiles, the nominalAcross that
  // shipped". That identity was a Foundational-phase crutch and it is gone by
  // design: floorPx is 113 now, so the width where the floor frames exactly
  // 10 tiles is 1130, not 1000. What matters was never the tile count -- it
  // is that the floor IS the pixel target and the ceiling IS the world cap.
  const D = api.VIEW.camera;
  const world = { width: 20, height: 20 };
  const cam = new api.Camera();
  const { floorTiles, ceilingTiles } = cam.limitsFor(world, 1000);
  assert(Math.abs(1000 / floorTiles - D.floorPx) < 1e-9,
    `the floor tile is ${(1000 / floorTiles).toFixed(1)}px, not the ${D.floorPx}px target`);
  // The ceiling is world/minZoomVsBase -- 13.33 tiles -- NOT the 50px target,
  // which would ask for 20 on this map. The cap is what governs at the large
  // end and the pixel target at the small.
  assert(Math.abs(ceilingTiles - world.width / D.minZoomVsBase) < 1e-9,
    `ceiling is ${ceilingTiles.toFixed(2)} tiles, not the ${(world.width / D.minZoomVsBase).toFixed(2)} the min-zoom cap allows`);
  // Which is the whole point of the cap, stated the way the owner asked for
  // it: a kitty at the camera's widest is at least minZoomVsBase times the
  // size the whole-world view would draw her.
  const base = 1000 / world.width;
  assert((1000 / ceilingTiles) / base >= D.minZoomVsBase - 1e-9,
    `at its widest a kitty is ${((1000 / ceilingTiles) / base).toFixed(2)}x base, under the ${D.minZoomVsBase}x floor`);
  // And on a phone the cap does NOT bind -- something else gets there first,
  // which is what keeps small screens untouched by THIS rule. WHICH
  // something else depends on the width, and `minTiles: 7` moved that
  // boundary, so both sides of it are pinned here.
  //
  // At a 380px map -- the owner's handset after the portrait-gap work -- the
  // ceiling is still the 50px pixel target.
  const phone = cam.limitsFor(world, 380);
  assert(phone.ceilingTiles < world.width / D.minZoomVsBase - 1e-9,
    `on a 380px map the min-zoom cap bound at ${phone.ceilingTiles.toFixed(2)} tiles`);
  assert(Math.abs(380 / phone.ceilingTiles - D.ceilingPx) < 1e-9,
    `on a 380px map the ceiling tile is ${(380 / phone.ceilingTiles).toFixed(1)}px, not the ${D.ceilingPx}px target`);

  // At 340px -- the smallest map the feature is verified across -- the floor
  // now asks for more tiles than the ceiling's own target does, so the
  // ceiling is raised to MEET the floor (FR-013) and that map has no zoom
  // range at all. contracts/zoom.md invariant 3 names this case: both limits
  // together, the tile under `ceilingPx`, FR-006 working rather than a
  // violation. It moved from "below about 300px" to 350px with minTiles 7.
  const smallest = cam.limitsFor(world, 340);
  assert(Math.abs(smallest.floorTiles - smallest.ceilingTiles) < 1e-9,
    `at 340px the floor (${smallest.floorTiles}) and ceiling (${smallest.ceilingTiles}) no longer meet`);
  assert(340 / smallest.ceilingTiles < D.ceilingPx,
    `at 340px the tile is ${(340 / smallest.ceilingTiles).toFixed(1)}px, not under the ${D.ceilingPx}px target`);
});

check('a viewport of zero still produces a usable frame', () => {
  // FR-014, and not hypothetical: the map has no width until the page has
  // laid out, so the FIRST FRAME of every session arrives here. Every limit
  // divides by or multiplies against cssWidth, so an unguarded zero makes
  // the whole frame non-finite and the canvas transform throws.
  const cam = new api.Camera();
  cam.on = true;
  const world = camAt([9, 9], [11, 11]);
  for (const bad of [0, -1, NaN, Infinity, undefined, null]) {
    const { floorTiles, ceilingTiles } = cam.limitsFor(world, bad);
    assert(Number.isFinite(floorTiles) && floorTiles > 0,
      `cssWidth ${bad} gave a floor of ${floorTiles}`);
    assert(Number.isFinite(ceilingTiles) && ceilingTiles > 0,
      `cssWidth ${bad} gave a ceiling of ${ceilingTiles}`);
    const fresh = new api.Camera();
    fresh.on = true;
    fresh.update(world, camView(false, 1000), { aspect: 1, cssWidth: bad });
    assert(Number.isFinite(fresh.across) && fresh.across > 0,
      `cssWidth ${bad} gave across ${fresh.across}`);
    assert(Number.isFinite(fresh.left) && Number.isFinite(fresh.top),
      `cssWidth ${bad} put the frame at ${fresh.left},${fresh.top}`);
  }
});

check('the fit, the anchor and the bake read ONE derivation', () => {
  // contracts/zoom.md invariant 2. If `bound` compared against a different
  // ceiling than the fit clamps to, the anchor would take over at a width
  // the camera never reaches: invisible to the eye, and the aim would jump
  // to one kitty while the frame was still sized to hold everybody.
  //
  // Asserted as an IMPLICATION rather than by recomputing the span here --
  // duplicating the span maths would just agree with a broken copy of it.
  const cam = new api.Camera();
  cam.on = true;
  const world = { width: 20, height: 20, elements: [], kitties: [] };
  const { floorTiles, ceilingTiles } = cam.limitsFor(world, 1000);
  let sawBound = 0;
  let sawFree = 0;
  for (let gap = 0; gap <= 19; gap += 1) {
    const w = camAt([Math.max(0, 10 - Math.floor(gap / 2)), 10],
                    [Math.min(19, 10 + Math.ceil(gap / 2)), 10]);
    const want = cam.targetFor(w, null, 1, 1000);
    if (want.bound) {
      sawBound += 1;
      assert(Math.abs(want.across - ceilingTiles) < 1e-9,
        `bound at gap ${gap} but the fit sat at ${want.across}, not the ${ceilingTiles} ceiling`);
    } else {
      sawFree += 1;
      assert(want.across <= ceilingTiles + 1e-9 && want.across >= floorTiles - 1e-9,
        `unbound at gap ${gap} with across ${want.across} outside [${floorTiles}, ${ceilingTiles}]`);
    }
  }
  // A sweep that never reached either state would pass while proving
  // nothing, which is the vacuous green rule 6 names.
  assert(sawBound > 0 && sawFree > 0,
    `the sweep only ever saw one state: ${sawFree} free, ${sawBound} bound`);

  // And the ground bake keys on that same floor, so it can never be keyed
  // to a tile the camera never draws.
  const baked = WorldRenderer.prototype.bakeTileFor.call(
    { cssWidth: 1000, dpr: 1, camera: cam }, world,
  );
  assert(baked === 1000 / floorTiles,
    `the bake used ${baked}px, not the floor's ${1000 / floorTiles}px`);
});

check('a fit that binds keeps every kitty clear of the frame edge', () => {
  // Between the floor and the ceiling the fit governs, and FR-004 says
  // nobody is drawn flush against the edge.
  const world = camAt([7, 9], [13, 11]);
  const cam = onCam(world);
  // Floor 8.85 (1000/113), ceiling 13.33 (the min-zoom cap). NOTE: the old
  // literals here were 10 and 19, and 11.2 sits inside BOTH bands -- so this
  // check would have stayed green while measuring the wrong thing. Fixed
  // deliberately rather than left to pass.
  const lo = 1000 / api.VIEW.camera.floorPx;
  const hi = 20 / api.VIEW.camera.minZoomVsBase;
  assert(cam.across > lo && cam.across < hi,
    `wanted the fit to govern between ${lo.toFixed(2)} and ${hi.toFixed(2)}, got ${cam.across.toFixed(2)}`);
  for (const k of world.kitties) {
    const x = k.pos.x + 0.5;
    const y = k.pos.y + 0.5;
    assert(x > cam.left && x < cam.left + cam.across, `${k.id} is outside the frame in x`);
    assert(y > cam.top && y < cam.top + cam.across, `${k.id} is outside the frame in y`);
  }
});

check('the frame always holds somebody, even at the world\'s corner', () => {
  // SC-005, as reworded 2026-08-18. When the ceiling binds the camera
  // aims at the anchor, and the clamp can only push the frame until it
  // meets the world's edge -- the anchor is a kitty AT a real tile, so
  // she cannot be clamped out of shot. Worth asserting rather than
  // reasoning about, since the clamp and the aim are computed apart.
  for (const spot of [[0, 0], [19, 0], [0, 19], [19, 19]]) {
    const world = camAt(spot, [10, 10], [11, 10], [12, 10], [13, 10]);
    const cam = new api.Camera();
    cam.on = true;
    cam.followId = 1; // force the corner kitty to be the aim
    cam.update(world, camView(), { aspect: 1, cssWidth: 1000 });
    const held = world.kitties.filter((k) => {
      const x = k.pos.x + 0.5;
      const y = k.pos.y + 0.5;
      return x >= cam.left && x <= cam.left + cam.across
        && y >= cam.top && y <= cam.top + cam.across;
    });
    assert(held.length > 0, `following a kitty at ${spot} left an empty frame`);
    assert(held.some((k) => k.id === 1), `the followed kitty at ${spot} is not in her own frame`);
  }
});

check('the frame never shows ground the world does not have', () => {
  // FR-029. A kitty in the corner is the case: aiming at her would put
  // several tiles of void on screen, which reads as a rendering fault.
  for (const spot of [[0, 0], [19, 0], [0, 19], [19, 19], [10, 10]]) {
    const cam = onCam(camAt(spot, spot));
    assert(cam.left >= 0, `left ${cam.left} at ${spot}`);
    assert(cam.top >= 0, `top ${cam.top} at ${spot}`);
    assert(cam.left + cam.across <= 20 + 1e-9, `right edge ${cam.left + cam.across} at ${spot}`);
    assert(cam.top + cam.across <= 20 + 1e-9, `bottom edge ${cam.top + cam.across} at ${spot}`);
  }
});

check('the camera aims at a kitty, never at the grass between them', () => {
  // Two kitties far apart: the midpoint and the centre of mass are the
  // same empty tile, and aiming there is the thing FR-006 forbids.
  const world = camAt([2, 10], [18, 10]);
  const cam = onCam(world);
  assert(cam.anchorId !== null, 'no anchor was chosen');
  const anchor = world.kitties.find((k) => k.id === cam.anchorId);
  assert(anchor, `anchor ${cam.anchorId} is not a kitty in the roster`);
  assert(
    cam.aimX === anchor.pos.x + 0.5 && cam.aimY === anchor.pos.y + 0.5,
    'the aim is not on the anchor',
  );
  assert(cam.aimX !== 10.5, 'the camera aimed at the empty midpoint');
});

check('the anchor is the kitty inside the cluster, not the outlier', () => {
  // Three together, one away. The centre of mass is pulled toward the
  // cluster, so the nearest kitty to it is one of the three.
  const world = camAt([9, 10], [10, 10], [11, 10], [19, 10]);
  const cam = onCam(world);
  assert(cam.anchorId !== 4, 'the camera anchored on the outlier');
});

check('ties break on id, so a reordered roster cannot change the pick', () => {
  // The SAME kitties -- same ids, same tiles -- handed over in opposite
  // array order. Their distances to the centre of mass are identical, so
  // without a rule the winner is whichever the loop met first, and the
  // camera would pick differently depending on serialisation order.
  const kitties = [
    { id: 1, pos: { x: 9, y: 10 } },
    { id: 2, pos: { x: 11, y: 10 } },
  ];
  const forward = { width: 20, height: 20, elements: [], kitties };
  const reversed = { width: 20, height: 20, elements: [], kitties: [...kitties].reverse() };
  const a = onCam(forward);
  const b = onCam(reversed);
  assert(a.anchorId === b.anchorId, `same world, different order: ${a.anchorId} vs ${b.anchorId}`);
  assert(a.anchorId === 1, `expected the lower id to win the tie, got ${a.anchorId}`);
  assert(a.aimX === b.aimX && a.aimY === b.aimY, 'the aim moved with the array order');
});

check('the anchor holds until another kitty is clearly more central', () => {
  // Without hysteresis this walk flips the anchor every frame it crosses
  // the midpoint, which is the flicker kitten.me deleted a snap rule over.
  const cam = new api.Camera();
  cam.on = true;
  let flips = 0;
  let last = null;
  for (let step = 0; step <= 20; step += 1) {
    // Two kitties drifting past each other through the centre of mass.
    const world = camAt([10 - step * 0.0, 10], [10, 10]);
    world.kitties[0].pos = { x: 9 + step * 0.1, y: 10 };
    cam.update(world, camView(false, 1000 + step * 16), { aspect: 1, cssWidth: 1000 });
    if (last !== null && cam.anchorId !== last) flips += 1;
    last = cam.anchorId;
  }
  assert(flips <= 1, `the anchor changed ${flips} times crossing one midpoint`);
});

check('the anchor survives a challenger twice as central', () => {
  // `flips <= 1` above holds at ANY hysteresis, so until this check nothing
  // in the suite went red when the dial moved. This one pins it: the rule is
  // `d2(held) < bestD * h**2`, squared on both sides, so the dial is a ratio
  // of REAL distances from the centre of mass and the anchor survives a
  // challenger up to `h` times more central.
  //
  //   frame 1   A x=10  B x=7  C x=13   com x=10   A is 0 away -> A anchors
  //   frame 2   A x=12  B x=9  C x=9    com x=10   A is 2 away, B and C are 1
  //
  // Built at a ratio of exactly 2.0, which sits between the 1.5 this suite
  // shipped with and the 2.5 measured for SC-006 on 2026-08-18. It goes red
  // for any dial at or below 2.0 -- including the 2.0 that was decided and
  // never landed.
  const world = (ax, bx, cx) => ({
    width: 20,
    height: 20,
    elements: [],
    kitties: [
      { id: 1, pos: { x: ax, y: 10 } },
      { id: 2, pos: { x: bx, y: 10 } },
      { id: 3, pos: { x: cx, y: 10 } },
    ],
  });
  const cam = new api.Camera();
  cam.on = true;
  cam.update(world(10, 7, 13), camView(false, 1000), { aspect: 1, cssWidth: 1000 });
  assert(cam.anchorId === 1, `setup: expected kitty 1 to anchor, got ${cam.anchorId}`);
  cam.update(world(12, 9, 9), camView(false, 1016), { aspect: 1, cssWidth: 1000 });
  assert(
    cam.anchorId === 1,
    `the anchor jumped to ${cam.anchorId} against a challenger only 2x more central`,
  );
});

check('easing settles at the same real speed on 60Hz and 120Hz', () => {
  // A rate written per-frame eases twice as fast at 120Hz uncorrected,
  // which is the bug kitten.me's own comment calls out.
  const world = camAt([3, 3], [4, 4]);
  const run = (frameMs) => {
    const cam = new api.Camera();
    cam.on = true;
    cam.update(world, camView(false, 0), { aspect: 1, cssWidth: 1000 }); // first frame arrives
    cam.aimX = 15; // shove it away, then let it come back
    let t = 0;
    for (let i = 0; i < Math.round(500 / frameMs); i += 1) {
      t += frameMs;
      cam.update(world, camView(false, t), { aspect: 1, cssWidth: 1000 });
    }
    return cam.aimX;
  };
  const at60 = run(16.67);
  const at120 = run(8.33);
  assert(Math.abs(at60 - at120) < 0.05, `after 500ms: 60Hz ${at60}, 120Hz ${at120}`);
});

check('the camera never cuts, however far the target jumps', () => {
  // FR-008. A kitty teleporting across the meadow (a reseed, a snap)
  // must not drag the camera with her in one frame.
  const cam = new api.Camera();
  cam.on = true;
  cam.update(camAt([2, 2], [3, 3]), camView(false, 0), { aspect: 1, cssWidth: 1000 });
  const before = cam.aimX;
  cam.update(camAt([18, 18], [17, 17]), camView(false, 16.67), { aspect: 1, cssWidth: 1000 });
  const moved = Math.abs(cam.aimX - before);
  assert(moved > 0, 'the camera did not follow at all');
  assert(moved < 3, `the camera jumped ${moved.toFixed(1)} tiles in one frame`);
});

check('the camera holds still while the group only fidgets', () => {
  // The complaint this answers, verbatim: "repeatedly panning in a
  // direction and snapping back". The aim tracked a statistic that moves
  // every tick, so the camera never once came to rest.
  const cam = new api.Camera();
  cam.on = true;
  cam.update(camAt([9, 10], [11, 10], [10, 11]), camView(false, 0), { aspect: 1, cssWidth: 1000 });
  const settled = { x: cam.aimX, y: cam.aimY };
  // A kitty shuffles a tile and back, twice. Inside the deadzone this is
  // beneath the camera's notice.
  let t = 0;
  for (const spots of [[[9, 10], [11, 10], [10, 12]], [[9, 10], [11, 10], [10, 11]],
                       [[9, 11], [11, 10], [10, 11]], [[9, 10], [11, 10], [10, 11]]]) {
    t += 16.67;
    cam.update(camAt(...spots), camView(false, t), { aspect: 1, cssWidth: 1000 });
  }
  assert(cam.aimX === settled.x && cam.aimY === settled.y,
    `the camera chased a fidget from ${settled.x},${settled.y} to ${cam.aimX},${cam.aimY}`);
});

check('but it follows the group when the group actually goes somewhere', () => {
  // The deadzone must not become a cage: a real move has to move the camera.
  const cam = new api.Camera();
  cam.on = true;
  cam.update(camAt([3, 3], [4, 4], [3, 4]), camView(false, 0), { aspect: 1, cssWidth: 1000 });
  const from = cam.aimX;
  let t = 0;
  for (let i = 0; i < 200; i += 1) {
    t += 16.67;
    cam.update(camAt([15, 15], [16, 16], [15, 16]), camView(false, t), { aspect: 1, cssWidth: 1000 });
  }
  assert(cam.aimX > from + 8, `the camera only reached ${cam.aimX.toFixed(1)} from ${from.toFixed(1)}`);
});

check('the aim is the centre of mass, not the box the extremes describe', () => {
  // Four kitties together and one far off: the box midpoint sits in the
  // grass between them, the centre of mass sits with the four.
  const world = camAt([9, 10], [10, 10], [11, 10], [10, 11], [19, 10]);
  const cam = onCam(world);
  const boxMid = (9.5 + 19.5) / 2;
  assert(Math.abs(cam.aimX - boxMid) > 1.5,
    `the aim sat at ${cam.aimX}, which is the box midpoint ${boxMid}`);
  assert(cam.aimX < 13, `the aim did not stay with the cluster: ${cam.aimX}`);
});

check('a followed kitty is the anchor, whatever the group is doing', () => {
  // FR-015: unconditional. No hysteresis, no centrality, no ceiling test.
  const world = camAt([2, 2], [10, 10], [11, 10], [12, 10]);
  const cam = new api.Camera();
  cam.on = true;
  cam.followId = 1; // the outlier, the anchor rule would never pick her
  cam.update(world, camView(), { aspect: 1, cssWidth: 1000 });
  assert(cam.anchorId === 1, `anchor is ${cam.anchorId}, not the followed kitty`);
  assert(cam.aimX === 2.5 && cam.aimY === 2.5, `aim sat at ${cam.aimX},${cam.aimY}`);
});

check('following moves the aim and nothing else', () => {
  // FR-014. The frame must not tighten around her, or the neighbours she
  // is sitting with get cropped away to centre her.
  const world = camAt([9, 10], [10, 10], [11, 10]);
  const loose = onCam(world);
  const cam = new api.Camera();
  cam.on = true;
  cam.followId = 1;
  cam.update(world, camView(), { aspect: 1, cssWidth: 1000 });
  assert(cam.across === loose.across, `following changed the width ${loose.across} -> ${cam.across}`);
});

check('a followed kitty who leaves the roster is let go, camera untouched', () => {
  // FR-020. The same path serves a restored id that names nobody and a
  // kitty who leaves while the page is open -- which is why it lives in
  // the camera and not in the startup restore.
  const cam = new api.Camera();
  cam.on = true;
  cam.followId = 99;
  cam.update(camAt([10, 10], [11, 11]), camView(), { aspect: 1, cssWidth: 1000 });
  assert(cam.followId === null, 'a follow on a kitty who is not here survived');
  assert(cam.on === true, 'dropping the follow turned the camera off');
  assert(cam.anchorId !== null, 'the camera failed to fall back to the group');
});

check('the toggle never releases a follow', () => {
  // FR-027, and the one rule clarify had to settle. Off and on again
  // returns to the same cat rather than to the group.
  const world = camAt([3, 3], [10, 10], [11, 10]);
  const cam = new api.Camera();
  cam.on = true;
  cam.followId = 1;
  cam.update(world, camView(false, 0), { aspect: 1, cssWidth: 1000 });
  cam.on = false;
  cam.update(world, camView(false, 16), { aspect: 1, cssWidth: 1000 });
  assert(cam.followId === 1, 'turning the camera off released the follow');
  cam.on = true;
  cam.update(world, camView(false, 32), { aspect: 1, cssWidth: 1000 });
  assert(cam.anchorId === 1, 'turning the camera back on lost the followed kitty');
});

check('the click lifecycle is one table, and every row is here', () => {
  // Spread across handlers this grows a hole; the hole clarify found was
  // the toggle's effect on a live follow.
  const app = readFileSync(join(here, 'app.js'), 'utf8');
  const from = app.indexOf('function initCameraClicks(');
  const body = app.slice(from, app.indexOf('\n}\n', from));
  assert(/setFollow\(null\)/.test(body), 'nothing releases a follow');
  assert(/anim\.camera\.followId === hit/.test(body), 'clicking the followed kitty does not release her');
  assert(/if \(!anim\.camera\.on\) setCameraMode\(true\)/.test(body),
    'clicking a kitty while the camera is off no longer turns it on (FR-012)');
  // FR-026: anything that is not a kitty releases, and it is NOT gated on
  // camera mode -- releasing is releasing.
  assert(/hit === null/.test(body), 'clicking away from the kitties does nothing');

  const hitFn = app.slice(app.indexOf('function kittyAtPoint('));
  const hit = hitFn.slice(0, hitFn.indexOf('\n}\n'));
  assert(/hitRadiusFloorPx/.test(hit), 'the hit radius has no floor, so a phone at the ceiling cannot catch a kitty');
  assert(/view\.posFor/.test(hit), 'the hit test reads served positions, not drawn ones');
  assert(/pos\.y > best\.y/.test(hit), 'overlapping kitties do not resolve to the one on top');
});

check('the hit test reads the frame that was drawn, not the one arriving', () => {
  // `viewAt(now, still)` sets `progress: still ? 1 : progress(now)`. A
  // still view therefore reports a walking kitty at her DESTINATION,
  // which mid-tick is up to a whole tile from where she is drawn. First
  // shown by the owner as "issues clicking on moving cats".
  const p = new api.Presentation();
  // Consecutive ticks and a single tile: anything else is a
  // discontinuity, which `pushState` correctly snaps rather than glides,
  // and there would be nothing to measure.
  const state = (tick, x) => ({ width: 20, height: 20, tick, kitties: [{ id: 1, pos: { x, y: 5 } }], elements: [] });
  p.pushState(state(0, 5), 0, 800);
  p.pushState(state(1, 6), 0, 800);
  const kitty = { id: 1, pos: { x: 6, y: 5 } };
  const mid = p.viewAt(400, false).posFor(kitty);
  const arrived = p.viewAt(400, true).posFor(kitty);
  assert(arrived.x === 6, `a still view should report the destination, got ${arrived.x}`);
  assert(mid.x < arrived.x - 0.3,
    `mid-glide should trail the destination: ${mid.x} vs ${arrived.x}`);

  const app = readFileSync(join(here, 'app.js'), 'utf8');
  const from = app.indexOf('function initCameraClicks(');
  const body = app.slice(from, app.indexOf('\n}\n', from));
  assert(/viewAt\(performance\.now\(\), anim\.reduced\)/.test(body),
    'the hit test does not use the same stillness the renderer drew with');
  assert(!/viewAt\([^)]*,\s*true\)/.test(body),
    'the hit test pins still to true, so it tests where a kitty is going');
});

check('the followed card is marked, and only hers', () => {
  const app = readFileSync(join(here, 'app.js'), 'utf8');
  const markup = readFileSync(join(here, 'index.html'), 'utf8');
  const mark = app.slice(app.indexOf('function markFollowedCard('));
  const body = mark.slice(0, mark.indexOf('\n}\n'));
  assert(/classList\.toggle\('followed'/.test(body), 'no card mark');
  assert(/=== id/.test(body), 'the mark is not restricted to the followed kitty');
  assert(/\.kitty-card\.followed/.test(markup), 'the followed card has no style');

  // The mark has to SURVIVE, which is where it actually broke: nothing
  // owns a card at the moment the follow is restored (initCameraState
  // runs before the first world arrives), and renderPanel throws every
  // card away when the roster size changes. Both were invisible to the
  // assertions above, which only ask whether the marking code exists.
  //
  // These are still source-shape checks -- app.js has no DOM in this
  // harness, so a real one would mean standing up a document here. That
  // is worth doing when app.js next needs behavioural coverage; it is not
  // worth pretending these are equivalent.
  // Scoped to the rebuild block: a bare /markedFollow = null/ also
  // matches the declaration, so removing the reset left the check green.
  const panel = app.slice(app.indexOf('function renderPanel('));
  const rebuild = panel.slice(panel.indexOf('if (needsRebuild)'), panel.indexOf('buildKittyCard(kitty)'));
  assert(/markedFollow = null;/.test(rebuild), 'a card rebuild no longer invalidates the mark');
  assert(/syncFollowMark\(\);/.test(app), 'nothing reconciles a follow the camera ended');
  const sync = app.slice(app.indexOf('function syncFollowMark('));
  const syncBody = sync.slice(0, sync.indexOf('\n}\n'));
  assert(/storeCamera\(\)/.test(syncBody), 'a dropped follow never reaches storage (FR-020)');
  assert(/markFollowedCard\(/.test(syncBody), 'a dropped follow never clears its card');
  // An outline cannot reflow the column; a border would nudge every card
  // below it the moment a follow started.
  assert(!/\.kitty-card\.followed\s*\{[^}]*border:/.test(markup),
    'the follow mark uses border, which reflows the card');
});

check('the pond layers are bounded tighter than the ground, being four of them', () => {
  // buildPondLayers allocates four canvases where the ground allocates
  // one. Bounding each canvas's side while the count quadrupled guards
  // the wrong quantity, and mobile Safari caps TOTAL canvas memory and
  // returns a blank canvas rather than failing.
  const world = camWorld();
  const cam = new api.Camera();
  cam.on = true;
  // Backed by the real prototype: pondBakeTileFor calls its sibling, and
  // a bare object stub cannot reach it.
  const r = Object.assign(Object.create(WorldRenderer.prototype), {
    cssWidth: 1200, dpr: 2, camera: cam,
  });
  const ground = r.bakeTileFor(world);
  const pond = r.pondBakeTileFor(world);
  assert(pond <= ground, `pond bakes larger than the ground: ${pond} > ${ground}`);
  const side = pond * Math.max(world.width, world.height) * r.dpr;
  assert(side <= 2048, `each pond layer would be ${Math.round(side)} device px a side`);
  // Four of them must not cost more than one ground bake.
  const groundSide = ground * Math.max(world.width, world.height) * r.dpr;
  assert(4 * side * side <= 4 * groundSide * groundSide,
    'four pond layers outweigh the ground bake they were bounded against');
});

check('the pond bake leaves the camera-off state alone, at every dpr', () => {
  // The ground bake skips its clamp when the camera is off so the off
  // state is byte-for-byte what shipped. The pond bound then undid that
  // for the water: on a 5K display the tile reaches ~59 and the bound
  // dropped the bake to 51.2, softening shore, lip, meniscus and pads --
  // and making `this.tile / bakeTile` differ from 1, which pushes the
  // off-state pond path through a ctx.scale it is documented never to
  // take. An identity claim has to hold for every layer.
  const world = camWorld();
  for (const [tile, dpr] of [[31, 1], [48, 2], [59, 2], [60, 3], [60, 4]]) {
    const r = Object.assign(Object.create(WorldRenderer.prototype), {
      cssWidth: tile * world.width, dpr, camera: new api.Camera(),
    });
    const pond = r.pondBakeTileFor(world);
    assert(pond === tile, `off at tile ${tile} dpr ${dpr}: pond bakes at ${pond}`);
    assert(pond === r.bakeTileFor(world), 'the pond and ground bakes disagree while off');
  }
  // With the camera ON the bound applies, which is the whole point of it.
  const cam = new api.Camera();
  cam.on = true;
  const on = Object.assign(Object.create(WorldRenderer.prototype), {
    cssWidth: 1200, dpr: 2, camera: cam,
  });
  assert(on.pondBakeTileFor(world) < on.bakeTileFor(world),
    'the pond bound does nothing when the camera is on');
});

check('the pond layers blit only what is on screen', () => {
  // They are baked at WORLD size, which under a camera is several times
  // the canvas. blitGround was given a source rect for this; these were
  // left without one.
  const meadowSrc = readFileSync(join(here, 'meadow.js'), 'utf8');
  const from = meadowSrc.indexOf('function drawPonds(');
  const fn = meadowSrc.slice(from, meadowSrc.indexOf('\n}\n', from));
  assert(/clip = null/.test(fn), 'drawPonds takes no visible clip rect');
  // Not `window`: a parameter of that name shadows the global for the
  // whole function body, so a later `window.devicePixelRatio` in here
  // would silently read a rectangle.
  assert(!/\bwindow = null/.test(fn), 'the clip parameter shadows the global `window`');
  assert(/drawImage\(layer, sx \* layers\.dpr/.test(fn), 'the layer blit has no source rect');
  assert(!/drawImage\(layers\.(lip|shore), 0, 0,/.test(fn), 'a layer still blits the whole world');
});

check('a still frame is the same moment again, not a jump forward', () => {
  // Every palette step, follow, unfollow, toggle and tab-return draws a
  // still frame. Treating those as "arrive" teleported the camera several
  // times a minute and eased the rest of the time -- reported as
  // intermittent jerking. A crossfade alone fires up to BLEND_STEPS.
  const near = camAt([9, 10], [11, 10]);
  const far = camAt([2, 2], [3, 3]);
  const cam = new api.Camera();
  cam.on = true;
  cam.update(near, camView(false, 0), { aspect: 1, cssWidth: 1000 });
  cam.update(far, camView(false, 16.67), { aspect: 1, cssWidth: 1000 }); // one eased step toward far
  const mid = { x: cam.aimX, y: cam.aimY, across: cam.across };

  cam.update(far, camView(true), { aspect: 1, cssWidth: 1000 });
  assert(cam.aimX === mid.x && cam.aimY === mid.y,
    `a still frame moved the aim from ${mid.x},${mid.y} to ${cam.aimX},${cam.aimY}`);
  assert(cam.across === mid.across, `a still frame moved the width to ${cam.across}`);

  // And it must still be mid-journey, or the assertion above is vacuous.
  // cssWidth MUST match what drove the camera: without it `limitsFor` reads
  // the missing value as "not laid out yet" and `want` comes back derived
  // from the WHOLE-WORLD limits (20 tiles) instead of 10/19. Harmless today
  // -- both worlds are compact enough that `bound` is false either way, so
  // the aim is the centre of mass regardless -- but the aim switches to the
  // anchor once `bound` flips, and a looser world would make this compare
  // against the wrong target in silence.
  const want = cam.targetFor(far, null, 1, 1000);
  assert(Math.abs(cam.aimX - want.aimX) > 0.5, 'the camera had already arrived, so nothing was proved');
});

check('reduced motion arrives instead, because it gets no other frames', () => {
  // FR-010, SC-009. The same `still` flag means the opposite thing here,
  // which is exactly why the camera cannot read it from the view alone.
  const world = camAt([2, 2], [3, 3]);
  const cam = new api.Camera();
  cam.on = true;
  cam.reduced = true;
  cam.update(camAt([15, 15], [16, 16]), camView(true), { aspect: 1, cssWidth: 1000 });
  cam.update(world, camView(true), { aspect: 1, cssWidth: 1000 });
  const want = cam.targetFor(world, null, 1, 1000);
  // Through the deadzone -- declining to chase a fidget is not motion.
  assert(Math.hypot(cam.aimX - want.aimX, cam.aimY - want.aimY) <= api.VIEW.camera.aimDeadzoneTiles + 1e-9,
    `reduced motion did not arrive: ${cam.aimX},${cam.aimY} vs ${want.aimX},${want.aimY}`);
});

check('a tab returning after a minute cannot cut', () => {
  // The path is: hidden tab banks arrivals -> visibilitychange calls
  // redraw() (STILL, no clock) -> startLoop() draws animated. So the vast
  // gap reaches the animated frame, and only the clamp stands between it
  // and an easing factor of 1, which is the cut FR-008 forbids.
  const world = camWorld();
  const cam = new api.Camera();
  cam.on = true;
  cam.update(world, camView(false, 1000), { aspect: 1, cssWidth: 1000 });
  cam.update(world, camView(true), { aspect: 1, cssWidth: 1000 }); // the redraw on return
  assert(cam.lastAt === 1000, 'the still redraw swallowed the gap');

  const dt = cam.dtFor(camView(false, 61_000));
  assert(dt === api.VIEW.camera.maxFrameMs, `dt came back ${dt}, not the clamp`);
  assert(dt < 61_000 - 1000, 'a minute-long gap reached the easing uncorrected');
});

check('every camera requirement holds at 3, 4 and 5 kitties', () => {
  // FR-022. The aesthetic half (SC-010) needs the owner's eye; the
  // REQUIREMENTS are arithmetic and can be swept here. A 3-kitty roster
  // sits at the zoom floor most of the time and a 5-kitty one is what
  // exercises the ceiling, so a bug that only shows at one size is
  // exactly what this is for.
  // Derived from cssWidth 1000 on a 20-tile world: floor 1000/113 = 8.85,
  // ceiling 20/1.5 = 13.33 (the min-zoom cap, which beats the 50px target's
  // 20 tiles). Written out rather than read back from limitsFor, so the sweep
  // cannot agree with a broken derivation.
  const FLOOR = 1000 / 113;
  const CEIL = 20 / 1.5;
  // 036 SC-005 -- never a frame with no kitty -- is WAIVED here, deliberately
  // and by the owner (2026-08-19), pending the camera-logic pass. Counted
  // rather than asserted away, so it stays visible and cannot get worse
  // unnoticed:
  //
  //   real world, 1500 recorded ticks, 5 kitties: ZERO empty frames at 640,
  //   1000 and 1200; three at 340, which is the case originally waived.
  //   this synthetic walk: ONE frame in 300, at 4 kitties, at 1000px.
  //
  // The gap is the fixture, not the camera. This walk moves every kitty one
  // tile per FRAME while the engine moves them one tile per TICK -- 48x
  // faster -- so its clowder scatters faster than any camera could track. The
  // comment below still says "one tile a tick"; the clock says otherwise.
  //
  // Cause is known and unchanged: the TARGET frame always holds the anchor,
  // the EASED frame can miss her mid-flight. Measured at the failing frame,
  // the anchor sat 0.13 tiles outside the left edge. The remedy is behaviour
  // -- track the largest group, cut rather than pan between groups, close in
  // when nobody is on the periphery -- and is parked in BACKLOG.md. If empty
  // frames survive THAT work, they stop being acceptable.
  let emptyFrames = 0;
  let checked = 0;
  for (const count of [3, 4, 5]) {
    // Deterministic pseudo-random walks: same worlds every run, so a
    // failure is reproducible rather than a story about last Tuesday.
    let seed = 1234 + count;
    const rnd = () => ((seed = (seed * 1103515245 + 12345) & 0x7fffffff) / 0x7fffffff);
    const cam = new api.Camera();
    cam.on = true;
    const kitties = Array.from({ length: count }, (_, i) => ({
      id: i + 1, pos: { x: Math.floor(rnd() * 20), y: Math.floor(rnd() * 20) },
    }));
    for (let step = 0; step < 300; step += 1) {
      for (const k of kitties) {
        // One tile a tick, which is what the engine allows.
        k.pos.x = Math.max(0, Math.min(19, k.pos.x + Math.round(rnd() * 2 - 1)));
        k.pos.y = Math.max(0, Math.min(19, k.pos.y + Math.round(rnd() * 2 - 1)));
      }
      const world = { width: 20, height: 20, elements: [], kitties };
      cam.update(world, camView(false, step * 16.67), { aspect: 1, cssWidth: 1000 });
      checked += 1;

      assert(cam.across >= FLOOR - 1e-9, `${count} kitties: across ${cam.across} below the floor`);
      assert(cam.across <= CEIL + 1e-9, `${count} kitties: across ${cam.across} above the ceiling`);
      assert(Number.isFinite(cam.aimX) && Number.isFinite(cam.aimY), `${count} kitties: aim went non-finite`);
      // FR-029: never a pixel of ground the world does not have.
      assert(cam.left >= -1e-9 && cam.top >= -1e-9, `${count} kitties: frame at ${cam.left},${cam.top}`);
      assert(cam.left + cam.across <= 20 + 1e-9, `${count} kitties: frame right edge ${cam.left + cam.across}`);
      assert(cam.top + cam.across <= 20 + 1e-9, `${count} kitties: frame bottom edge ${cam.top + cam.across}`);
      assert(kitties.some((k) => k.id === cam.anchorId), `${count} kitties: anchor ${cam.anchorId} is nobody`);
      // SC-005 as the owner reworded it (2026-08-18): not every kitty --
      // the ceiling deliberately lets a wanderer go (FR-005) -- but NEVER
      // a frame with nobody in it. An empty meadow reads as broken, and
      // it is the failure the original "the aim always rests on a kitty"
      // was reaching for without saying so.
      const inFrame = kitties.filter((k) => {
        const x = k.pos.x + 0.5;
        const y = k.pos.y + 0.5;
        return x >= cam.left && x <= cam.left + cam.across
          && y >= cam.top && y <= cam.top + cam.across;
      });
      // WAIVED, not asserted -- see the note at the top of this check. A
      // ratchet, so the known case cannot quietly become a common one.
      if (inFrame.length === 0) emptyFrames += 1;
    }
  }
  assert(checked === 900, `swept ${checked} states, expected 900`);
  assert(emptyFrames <= 1,
    `${emptyFrames} empty frames across the sweep, against the 1 measured when 036 SC-005 `
    + `was waived on 2026-08-19. The waiver covers a rare mid-ease miss, not a common one -- `
    + `if this grew, the camera-logic work stopped being optional`);
});

check('aim settles faster than width, so the zoom lags the pan', () => {
  assert(api.VIEW.camera.panRate > api.VIEW.camera.zoomRate,
    'the zoom is not slower than the pan');
});

check('the waterline is centred on the cat\'s body, not on her box', () => {
  // Owner, 2026-08-18: "a few pixels too far to the right on the
  // right-facing cat". She is not symmetric about her own box -- the body
  // sits behind the head -- so a box-centred meniscus is offset toward the
  // head by however far BODY_CX is from 0.5.
  //
  // This measures where cat-v2 ACTUALLY puts the body and checks
  // render.js's assumption against it, so it fails if either side moves.
  const T = 100;
  const bodyCentre = (facing) => {
    let m = [1, 0, 0, 1, 0, 0];
    const stack = [];
    const marks = [];
    const mul = (a, b) => [
      a[0] * b[0] + a[2] * b[1], a[1] * b[0] + a[3] * b[1],
      a[0] * b[2] + a[2] * b[3], a[1] * b[2] + a[3] * b[3],
      a[0] * b[4] + a[2] * b[5] + a[4], a[1] * b[4] + a[3] * b[5] + a[5],
    ];
    const ctx = new Proxy({}, {
      get: (_t, k) => {
        if (k === 'createLinearGradient' || k === 'createRadialGradient') return () => ({ addColorStop() {} });
        if (k === 'measureText') return () => ({ width: 10 });
        if (k === 'save') return () => stack.push([...m]);
        if (k === 'restore') return () => { m = stack.pop() || [1, 0, 0, 1, 0, 0]; };
        if (k === 'translate') return (x, y) => { m = mul(m, [1, 0, 0, 1, x, y]); };
        if (k === 'scale') return (x, y) => { m = mul(m, [x, 0, 0, y, 0, 0]); };
        if (k === 'rotate') return (a) => { m = mul(m, [Math.cos(a), Math.sin(a), -Math.sin(a), Math.cos(a), 0, 0]); };
        if (k === 'ellipse') return (x, y, rx) => marks.push({ x: m[0] * x + m[2] * y + m[4], rx: Math.abs(rx * m[0]) });
        return () => {};
      },
      set: () => true,
    });
    CatV2.drawCat(ctx, { pose: 'idle', appearance: CatV2.appearanceFor(2), facing, size: T, x: 0, y: 0, phase: 0.3 });
    // The body is the widest ellipse she draws.
    return marks.sort((a, b) => b.rx - a.rx)[0].x;
  };

  const expected = (facing) => T * (facing === 'left' ? 1 - CatV2.BODY_CX : CatV2.BODY_CX);
  for (const facing of ['right', 'left', 'north', 'south']) {
    const drawn = bodyCentre(facing);
    assert(Math.abs(drawn - expected(facing)) < 0.5,
      `${facing}: body drawn at ${drawn.toFixed(1)}, BODY_CX says ${expected(facing).toFixed(1)}`);
  }
  // And she really is off-centre, or the whole check is vacuous.
  assert(Math.abs(bodyCentre('right') - T / 2) > 3,
    'the body sits on the box centre, so this check proves nothing');

  // render.js must USE that, not the box centre.
  // NB there are two `if (submerged)` blocks -- the clip is the other one.
  assert(/const bodyCx = drawnFacing === 'left' \? 1 - BODY_CX : BODY_CX;/.test(renderSrc),
    'the waterline no longer centres on the body');
  assert(/drawWaterline\(x \+ this\.tile \* bodyCx,/.test(renderSrc),
    'the waterline is not drawn at the body centre');
  assert(!/this\.drawWaterline\(cx,/.test(renderSrc), 'the waterline is back on the box centre');
});

/* ── resizeFor, against four RECORDED layouts ───────────────────────────
 *
 * The one function in the client with no coverage, and six layout changes
 * have now shipped through it (#248, #250, #251, #252, the card gap, the
 * hairline). Nothing could drive it: it reads documentElement,
 * getComputedStyle, getBoundingClientRect and matchMedia, while every other
 * check here sets `cssWidth` on a stub.
 *
 * The obvious fix is an invented DOM, which is the hand-written-fixture lie.
 * These four cases are RECORDED off the owner's real devices with
 * record-layout.js (2026-08-19) and pasted in verbatim -- and crucially each
 * one carries `canvasCssWidth`, what the BROWSER actually laid out. So the
 * assertion compares resizeFor against Safari, not against my arithmetic.
 * A harness that replayed these inputs and checked them against a number
 * resizeFor produced would agree with itself and prove nothing.
 *
 * What the four are for, because none of them is decoration:
 *   1728x919@2  desktop, cards BESIDE the map -- the only case exercising
 *               besideWidth and columnGap. Height-bound.
 *   752x919@2   mid-range, cards below. Width-bound AND sitting 2px past a
 *               tile boundary, which is the ONLY case where the 1px stage
 *               border is worth a whole tile. Without it nothing guards the
 *               border term at all -- the other three floor to the same tile
 *               with or without it. Its footer WRAPS to 54px, which no
 *               invented fixture would have thought to do.
 *   402x654@3   the phone. dpr 3, width-bound, `.panel-col` collapsed to
 *               zero width so besideWidth is 0 -- the branch the desktop
 *               case cannot reach. Note 654, not the nominal 874: Safari's
 *               chrome is real and a guessed viewport would have missed it.
 * ── */
const RECORDED_LAYOUTS = [
  { name: '1728x919 @2 — desktop, cards beside the map',
    docClientWidth: 1728, docClientHeight: 919, headerHeight: 51, footerHeight: 20,
    bodyPadY: 48, stageFrameX: 2, stageFrameY: 2, layoutClientWidth: 1696,
    besideWidth: 452, columnGap: 16, panelColCount: 2, shortBranch: false,
    dpr: 2, canvasCssWidth: 760, canvasBackingWidth: 1520 },
  { name: '752x919 @2 — mid-range, and the only border witness',
    docClientWidth: 752, docClientHeight: 919, headerHeight: 51, footerHeight: 54,
    bodyPadY: 48, stageFrameX: 2, stageFrameY: 2, layoutClientWidth: 720,
    besideWidth: 0, columnGap: 0, panelColCount: 2, shortBranch: false,
    dpr: 2, canvasCssWidth: 700, canvasBackingWidth: 1400 },
  { name: '761x919 @2 — mid-range, one tile up',
    docClientWidth: 761, docClientHeight: 919, headerHeight: 51, footerHeight: 54,
    bodyPadY: 48, stageFrameX: 2, stageFrameY: 2, layoutClientWidth: 729,
    besideWidth: 0, columnGap: 0, panelColCount: 2, shortBranch: false,
    dpr: 2, canvasCssWidth: 720, canvasBackingWidth: 1440 },
  { name: '402x654 @3 — the phone',
    docClientWidth: 402, docClientHeight: 654, headerHeight: 52, footerHeight: 40,
    bodyPadY: 44, stageFrameX: 2, stageFrameY: 2, layoutClientWidth: 398,
    besideWidth: 0, columnGap: 0, panelColCount: 2, shortBranch: false,
    // `probeLvh` is 100px over clientHeight even upright -- and `innerHeight`
    // and `visualViewport.height` BOTH agree with clientHeight at 654, so
    // `lvh` is the only one of the four that can see the retractable bar.
    // Inert here: portrait is not short, so the letterbox never asks.
    probeLvh: 754, dpr: 3, canvasCssWidth: 380, canvasBackingWidth: 1140 },
  // The only recording that takes the SHORT branch, so it is the only one
  // where `matchMedia` is load-bearing: replayed as not-short its width
  // collapses from 720 to 140, because the height would bind instead.
  { name: '750x285 @3 — the phone held sideways',
    docClientWidth: 750, docClientHeight: 285, headerHeight: 33, footerHeight: 52,
    bodyPadY: 14, stageFrameX: 2, stageFrameY: 2, layoutClientWidth: 730,
    besideWidth: 0, columnGap: 0, panelColCount: 2, shortBranch: true,
    // THE FOUR VIEWPORT HEIGHTS, and they disagree by 126px. The layout
    // viewport is 285 and holds still by design; `innerHeight` and
    // `visualViewport.height` were 276 with the bar shown; `lvh` is 402 --
    // the whole screen, because in landscape the bar retracts completely.
    // Sizing to anything but `lvh` leaves a third of the screen showing card.
    probeLvh: 402,
    dpr: 3, canvasCssWidth: 720, canvasCssHeight: 400, canvasBackingWidth: 2160 },
];

/**
 * Replays one recording through the REAL resizeFor and returns what it sized
 * the canvas to. The stubs answer only what resizeFor asks for; anything it
 * grew a dependency on would throw here rather than silently read undefined.
 */
function replayLayout(rec, world = { width: 20, height: 20 }, camera = null, reuse = null) {
  const saved = {
    document: globalThis.document, window: globalThis.window,
    getComputedStyle: globalThis.getComputedStyle, matchMedia: globalThis.matchMedia,
  };
  const half = (n) => `${n / 2}px`;
  const box = (h) => ({ getBoundingClientRect: () => ({ height: h, width: 0 }) });
  const cols = Array.from({ length: rec.panelColCount }, () => ({
    getBoundingClientRect: () => ({ width: rec.besideWidth / rec.panelColCount, height: 0 }),
  }));
  const layout = {
    clientWidth: rec.layoutClientWidth,
    querySelectorAll: () => (rec.besideWidth > 0 ? cols : cols.map(() => ({
      getBoundingClientRect: () => ({ width: 0, height: 0 }),
    }))),
  };
  const cell = { parentElement: layout };
  const stage = { parentElement: cell, __stage: true };
  const body = { __body: true };
  const canvas = { parentElement: stage, style: {}, width: 0, height: 0 };
  const ctx = { setTransform() {} };

  globalThis.document = {
    documentElement: { clientWidth: rec.docClientWidth, clientHeight: rec.docClientHeight },
    body,
    // `probeLvh` absent means the recording predates the probe, and 0 is the
    // honest answer for that: render.js reads it as "no answer" and falls back
    // to clientHeight, which is exactly what those four layouts were recorded
    // under. It is NOT a stand-in for a large viewport nobody measured.
    querySelector: (sel) => (sel === 'header' ? box(rec.headerHeight)
      : sel === 'footer' ? box(rec.footerHeight)
      : sel === '#vh-probe' ? box(rec.probeLvh || 0) : null),
    createElement: () => ({ getContext: () => null, dataset: {}, style: {} }),
  };
  globalThis.window = { devicePixelRatio: rec.dpr };
  // The frame goes in the BORDER, not the padding, because that is where the
  // shipped CSS puts it: `--stage-pad: 0px` and a 1px --grass-line hairline.
  // The recording reports the two summed and cannot tell them apart, so this
  // is the one place the fixture has to know something the recording does not
  // -- and it matters. Putting the frame in padding here would leave the
  // border term unread by resizeFor and unguarded by this test, which is the
  // exact hole the 752 case was recorded to close.
  globalThis.getComputedStyle = (el) => (el === stage ? {
    paddingLeft: '0px', paddingRight: '0px', paddingTop: '0px', paddingBottom: '0px',
    borderLeftWidth: half(rec.stageFrameX), borderRightWidth: half(rec.stageFrameX),
    borderTopWidth: half(rec.stageFrameY), borderBottomWidth: half(rec.stageFrameY),
  } : el === body ? {
    paddingTop: half(rec.bodyPadY), paddingBottom: half(rec.bodyPadY),
    paddingLeft: '0px', paddingRight: '0px',
  } : { columnGap: `${rec.columnGap}px` });
  globalThis.matchMedia = () => ({ matches: rec.shortBranch });

  try {
    const r = reuse || Object.create(WorldRenderer.prototype);
    if (!reuse) { r.canvas = canvas; r.ctx = ctx; r.dpr = null; }
    // A reused renderer keeps its canvas -- as the real one does across a
    // resize -- but its ANCESTORS must be the freshly measured stubs, because
    // `resizeFor` reaches the layout through `canvas.parentElement`. Without
    // this, a reuse could only ever vary what comes off the globals
    // (clientHeight, dpr) and silently ignored a new layoutClientWidth: a
    // width-change test would pass while measuring no width change at all.
    else r.canvas.parentElement = stage;
    r.camera = camera;
    r.resizeFor(world);
    return {
      cssWidth: r.cssWidth, cssHeight: r.cssHeight, tile: r.tile,
      backing: r.canvas.width, backingH: r.canvas.height,
      styleW: r.canvas.style.width, styleH: r.canvas.style.height,
      renderer: r,
    };
  } finally {
    Object.assign(globalThis, saved);
  }
}

for (const rec of RECORDED_LAYOUTS) {
  check(`resizeFor reproduces the browser: ${rec.name}`, () => {
    const got = replayLayout(rec);
    assert(got.cssWidth === rec.canvasCssWidth,
      `sized the map to ${got.cssWidth}px; Safari laid out ${rec.canvasCssWidth}px`);
    assert(got.backing === rec.canvasBackingWidth,
      `backing store ${got.backing}; the browser made ${rec.canvasBackingWidth}`);
  });
}

check('the stage FRAME is measured, not just its padding', () => {
  // The witness case, and the reason it was recorded at 752 and not a round
  // number: its width budget lands 2px past a tile boundary, so the 1px
  // hairline each side is worth a whole tile. On every other recording the
  // budget floors to the same tile with the border or without it, which is
  // exactly how this term could have gone unguarded while looking covered.
  const witness = RECORDED_LAYOUTS.find((r) => r.docClientWidth === 752);
  assert(replayLayout(witness).cssWidth === 700, 'the witness no longer reproduces');
  const borderless = { ...witness, stageFrameX: 0, stageFrameY: 0 };
  assert(replayLayout(borderless).cssWidth === 720,
    'dropping the stage frame changed nothing here, so this case no longer '
    + 'witnesses the border and the term is unguarded');
});

/* ── The letterbox: a short window gets a canvas shaped like the WINDOW ──
 *
 * RECORDED, as of 2026-08-20. It was CONSTRUCTED, on the argument that these
 * checks pin a RELATIONSHIP -- a wide short window makes a wide short canvas
 * -- and a relationship does not need a device to be true. The relationship
 * held. The numbers did not, and they were the ones being reasoned FROM:
 *
 *   guessed 874x402, footer 28   ->   real 750x285, footer 52
 *
 * A 41% over-estimate of the height a landscape phone actually has, and a
 * footer nearly double. Predictions made against it were wrong by about 2x
 * (13x5 tiles predicted, 13x2.85 delivered), and the footer waste this file
 * now guards was invisible while the fixture said the footer was 28px of a
 * roomy 402. A fixture that is "at least plausible" is a fixture that agrees
 * with whatever you already believed.
 * ── */
const LANDSCAPE = RECORDED_LAYOUTS.find((r) => r.shortBranch);
const cameraOn = (on) => ({ on });

check('a short window with the camera ON gets a canvas shaped like the window', () => {
  const got = replayLayout(LANDSCAPE, { width: 20, height: 20 }, cameraOn(true));
  assert(got.cssHeight < got.cssWidth,
    `letterboxed canvas is ${got.cssWidth}x${got.cssHeight} -- still not wider than tall`);
  // It FILLS the screen (owner, 2026-08-20), which is a different target from
  // the one this check used to hold. It asked that the map fit the fold
  // alongside the header; the map now takes the whole viewport and the header
  // is meant to be scrolled AWAY. So the assertion is the screen, not the
  // budget -- and deliberately not a rebuild of resizeFor's own arithmetic,
  // which is how the previous version of this line went wrong.
  assert(got.cssHeight === LANDSCAPE.canvasCssHeight,
    `the canvas is ${got.cssHeight} tall; Safari laid out ${LANDSCAPE.canvasCssHeight} `
    + `from a ${LANDSCAPE.probeLvh}px large viewport`);
  assert(got.cssHeight === LANDSCAPE.probeLvh - LANDSCAPE.stageFrameY,
    'the recorded height is no longer the large viewport less the hairline, so one of '
    + 'the two stopped being what this thinks it is');
  // 126px of it -- a third of the screen -- is invisible to every other
  // measurement the page can take: `clientHeight` says 285, `innerHeight` and
  // `visualViewport.height` both said 276 with the bar showing.
  assert(got.cssHeight > LANDSCAPE.docClientHeight,
    `the canvas (${got.cssHeight}) did not exceed the layout viewport `
    + `(${LANDSCAPE.docClientHeight}), so it is still sized to the wrong one`);
  // And it therefore OVERFLOWS the fold on purpose: that overflow is the
  // feature, not a defect. Scroll once and the header, sky dial and camera
  // control are gone and the screen is meadow.
  const aboveTheMap = LANDSCAPE.headerHeight + LANDSCAPE.bodyPadY + LANDSCAPE.stageFrameY;
  assert(aboveTheMap + got.cssHeight > LANDSCAPE.docClientHeight,
    'the map no longer overflows the fold, so there is nothing to scroll the header away with');
  // And the camera must be TOLD, which is the only reason any of this works.
  // It reads aspect as cssHeight/cssWidth; at 1.0 it frames a square.
  assert(got.cssHeight / got.cssWidth < 0.6,
    `aspect ${(got.cssHeight / got.cssWidth).toFixed(2)} still reads as roughly square`);
});

check('the footer is charged to the map only when it is the next thing under it', () => {
  // The letterbox shipped 2.85 world-rows tall on the owner's handset where
  // the same window affords 3.81, and the missing 52px was a footer that is
  // nowhere near the map. Below the 1100px breakpoint the card columns
  // dissolve and the cards stack BETWEEN the map and the footer, so the page
  // already scrolls to reach either -- charging the map for the footer buys
  // nothing and costs a real tile. 52px of a 285px viewport is 18% of the
  // whole screen.
  //
  // Invisible everywhere else, which is why it survived: every other recorded
  // layout is bound by WIDTH, so its height budget has slack to waste. Only a
  // short window is height-bound with the cards stacked.
  const world = { width: 20, height: 20 };

  // THE LETTERBOX NO LONGER READS THE HEIGHT BUDGET -- it fills the screen
  // (2026-08-20) -- so the landscape case can no longer witness this, and no
  // recorded layout can: all five are bound by WIDTH or take the letterbox
  // path. The branch is still live for any window under 1100px whose HEIGHT
  // binds with the cards stacked, e.g. a 900x600 browser window.
  //
  // So it is exercised here by replaying the real landscape measurements with
  // the media query answered the other way. That is a BRANCH PROBE, not a
  // device: no 750x285 viewport is "not short". Every number in it is still
  // measured -- only the one input `replayLayout` exists to parameterise is
  // varied. Owed a real recording of a short-and-wide desktop window, which
  // would retire this.
  const asTall = replayLayout({ ...LANDSCAPE, shortBranch: false }, world);
  assert(asTall.cssWidth === 200,
    `the height-bound stacked case sized to ${asTall.cssWidth}px, not 200 -- with the `
    + `footer charged it is 160, so this no longer witnesses the footer at all`);

  // The other branch, and it is load-bearing rather than hypothetical: the
  // 1728 desktop recording IS height-bound, and there the cards sit beside the
  // map so the footer really is the next thing under it. Dropping the footer
  // unconditionally would take that map from 760px to 780px.
  const beside = RECORDED_LAYOUTS.find((r) => r.besideWidth > 0);
  assert(beside.docClientHeight - (beside.headerHeight + beside.footerHeight
    + beside.bodyPadY + beside.stageFrameY + 30) < beside.layoutClientWidth - beside.besideWidth,
    'the flanking recording stopped being height-bound, so it no longer guards the footer');
  assert(replayLayout(beside, world).cssWidth === beside.canvasCssWidth,
    `the flanking layout sized to ${replayLayout(beside, world).cssWidth}px, not its recorded `
    + `${beside.canvasCssWidth}px -- the footer stopped being charged where it should be`);
});

check('a height-only resize keeps the baked ground; a width change still drops it', () => {
  // iOS collapses its toolbar AS YOU SCROLL, and `resizeFor` runs every frame,
  // so a screen-filling map means a stream of frames each reporting a
  // different clientHeight. Nulling the caches on any of them would re-bake
  // the whole ground and every shoreline mid-scroll, on the one device that
  // can least afford it.
  //
  // Safe to skip because neither cache is keyed on the canvas: the ground
  // checks `dpr|bakeTile|width` against its own dataset, the ponds sign
  // `paletteKey|bakeTile|water`. This asserts the SKIP, which is the half a
  // mutation can reach -- their own signatures already have their own checks.
  const world = { width: 20, height: 20 };
  const first = replayLayout(LANDSCAPE, world, cameraOn(true));
  const r = first.renderer;
  const baked = { ground: 'ground-bake', pond: 'pond-bake' };
  r.groundCache = baked.ground;
  r.pondCache = baked.pond;

  // A taller large viewport at the same width -- a short desktop window
  // dragged down, or a device with less browser chrome. NOT the toolbar
  // sliding away, which is what this used to model: `lvh` is measured with
  // the retractable UI already gone, so it does not move during a scroll and
  // the canvas no longer resizes mid-gesture at all. The skip below still
  // matters for every other height change.
  const taller = replayLayout({ ...LANDSCAPE, probeLvh: LANDSCAPE.probeLvh + 40 },
    world, cameraOn(true), r);
  assert(taller.cssHeight !== first.cssHeight,
    `the height did not move (${taller.cssHeight}), so this proves nothing`);
  assert(taller.cssWidth === first.cssWidth, 'the width moved too -- not a height-only resize');
  assert(r.groundCache === baked.ground,
    'a height-only resize threw the baked ground away -- that is a full re-bake per scroll frame');
  assert(r.pondCache === baked.pond, 'a height-only resize threw the shorelines away');
  assert(r.canvas.height === Math.floor(taller.cssHeight * LANDSCAPE.dpr),
    `the backing store stayed at ${r.canvas.height} while the canvas grew -- issue #102 again`);

  // But a WIDTH change must still drop them: the tile moves, and everything
  // both caches bake is keyed to the tile.
  const narrower = replayLayout(
    { ...LANDSCAPE, docClientWidth: 600, layoutClientWidth: 580 }, world, cameraOn(true), r);
  assert(narrower.cssWidth !== first.cssWidth, 'the width did not move, so this proves nothing');
  assert(r.groundCache === null && r.pondCache === null,
    'a width change kept the caches, so the ground is baked at the previous tile');
});

check('the letterbox fills the LARGE viewport, not the layout one', () => {
  // A phone browser retracts its toolbar as you scroll and `clientHeight` does
  // not follow -- it is the LAYOUT viewport and holds still by design. Sized
  // to it, the map stops short of the screen you can actually see once the bar
  // is gone, which is what the owner reported: a band of card under the map.
  //
  // PARAMETRIC ON PURPOSE. The real `lvh` of a 16 Pro sideways has not been
  // measured yet -- the recorder only started reporting it in this change --
  // so this asserts that the canvas TRACKS the probe rather than asserting any
  // particular device's number. Inventing that number is exactly how the
  // constructed landscape fixture went wrong, and this is the same axis.
  const world = { width: 20, height: 20 };
  const frame = LANDSCAPE.stageFrameY;
  for (const lvh of [LANDSCAPE.docClientHeight + 60, LANDSCAPE.docClientHeight + 106]) {
    const got = replayLayout({ ...LANDSCAPE, probeLvh: lvh }, world, cameraOn(true));
    assert(got.cssHeight === lvh - frame,
      `a ${lvh}px large viewport gave a ${got.cssHeight}px canvas, not ${lvh - frame}`);
  }

  // A probe that reports SMALLER than the layout viewport is not an answer --
  // a browser that does not understand `lvh` drops the declaration and the
  // empty div measures 0. That must not shrink the map to nothing.
  for (const lvh of [0, 40]) {
    const got = replayLayout({ ...LANDSCAPE, probeLvh: lvh }, world, cameraOn(true));
    assert(got.cssHeight === LANDSCAPE.docClientHeight - frame,
      `a ${lvh}px probe gave a ${got.cssHeight}px canvas instead of falling back to `
      + `${LANDSCAPE.docClientHeight - frame}`);
  }
});

check('the recorded landscape phone frames seven rows at a 57px tile', () => {
  // The whole landscape arc of 2026-08-20, end to end, against one recorded
  // device rather than the four different estimates it took to get here. Every
  // input is measured: 750x285 layout viewport, 402 large viewport, 33px
  // header, a footer that wraps to 52.
  //
  // Worth stating as the OUTCOME and not the arithmetic, because each of the
  // four changes moved a different term and only the product is visible: the
  // footer stopped being charged, the map went from the fold to the screen,
  // the screen became the large viewport, and the row cap decided how much
  // world goes in it.
  const world = { width: 20, height: 20 };
  const got = replayLayout(LANDSCAPE, world, cameraOn(true));
  const { ceilingTiles: across, floorTiles } =
    new api.Camera().limitsFor(world, got.cssWidth, got.cssHeight / got.cssWidth);
  const tile = got.cssWidth / across;
  const rows = across * (got.cssHeight / got.cssWidth);

  assert(Math.abs(rows - api.VIEW.camera.ceilingRows) < 1e-9,
    `the widest frame is ${rows.toFixed(2)} rows, not the ${api.VIEW.camera.ceilingRows} the cap allows`);
  assert(Math.abs(tile - 57.1) < 0.1,
    `a kitty draws at ${tile.toFixed(1)}px; the measured device gives 57.1`);
  assert(tile > api.VIEW.camera.ceilingPx,
    `${tile.toFixed(1)}px is under the ${api.VIEW.camera.ceilingPx}px target, so landscape `
    + 'is now the smallest cat anywhere rather than the biggest');
  // And it has a zoom range again. It had NONE this morning on the smallest
  // map -- floor and ceiling met -- which was the accepted cost of minTiles 7.
  assert(across > floorTiles + 1e-9,
    `landscape floor ${floorTiles} and ceiling ${across.toFixed(2)} have met, so the camera `
    + 'pans without ever zooming');
});

check('camera OFF keeps the square-and-scroll, untouched (036 SC-007)', () => {
  const off = replayLayout(LANDSCAPE, { width: 20, height: 20 }, cameraOn(false));
  const none = replayLayout(LANDSCAPE, { width: 20, height: 20 }, null);
  assert(off.cssHeight === off.cssWidth,
    `camera-off canvas is ${off.cssWidth}x${off.cssHeight}; the off state must stay square`);
  assert(none.cssHeight === none.cssWidth, 'no camera at all must behave as camera-off');
  assert(off.cssWidth === none.cssWidth, 'an off camera changed the width');
});

check('a tall window is unaffected -- and the `short` guard is belt-and-braces', () => {
  // This check was written expecting to guard the `short &&` half of the
  // condition. It CANNOT, and finding that out is more useful than the check
  // was: when the viewport is not short, `tile` is already
  // min(width/20, height/20), so `tile * world.height` never exceeds the
  // height budget and `Math.min(heightBudget, tile * height)` is a no-op by
  // construction. Removing `short &&` changes no output anywhere.
  //
  // So the guard is DEFENSIVE, not load-bearing, and it is kept for intent
  // and against the tile arithmetic changing under it -- not because a test
  // holds it in place. Saying so here beats a green check that implies
  // otherwise.
  const rec = RECORDED_LAYOUTS.find((r) => r.docClientWidth === 1728);
  const on = replayLayout(rec, { width: 20, height: 20 }, cameraOn(true));
  assert(on.cssHeight === on.cssWidth && on.cssWidth === rec.canvasCssWidth,
    `a tall window got a ${on.cssWidth}x${on.cssHeight} canvas with the camera on`);
});

check('the resize guard watches HEIGHT, not only width', () => {
  // Two resizes on ONE renderer, which is the only way a guard can be seen at
  // all: a fresh canvas has no previous size, so its style is undefined and
  // the guard fires no matter what it watches. The first version of this
  // check replayed twice from scratch and stayed green with the height
  // condition deleted -- it was witnessing nothing.
  //
  // The scenario is real: a phone sideways with the browser bar sliding into
  // view keeps its width and loses height. Before the letterbox, height was a
  // pure function of width and a width that had not moved proved a height
  // that had not moved. That implication is now false.
  const world = { width: 20, height: 20 };
  const first = replayLayout(LANDSCAPE, world, cameraOn(true));
  const second = replayLayout(
    { ...LANDSCAPE, probeLvh: LANDSCAPE.probeLvh - 60 },
    world, cameraOn(true), first.renderer,
  );
  assert(first.cssWidth === second.cssWidth,
    'the fixture no longer holds width constant, so it cannot witness this');
  assert(first.cssHeight !== second.cssHeight, 'the height budget never reached the canvas');
  assert(second.styleH === `${second.cssHeight}px`,
    `CSS height stuck at ${second.styleH} for a ${second.cssHeight}px canvas -- guard never fired`);
  assert(second.backingH === Math.floor(second.cssHeight * LANDSCAPE.dpr),
    `backing store is ${second.backingH}, not ${Math.floor(second.cssHeight * LANDSCAPE.dpr)}`);
});

console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
