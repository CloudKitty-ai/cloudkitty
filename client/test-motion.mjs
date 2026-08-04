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
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const animSrc = readFileSync(join(here, 'anim.js'), 'utf8');
const catV2Src = readFileSync(join(here, 'cat-v2.js'), 'utf8');
const renderSrc = readFileSync(join(here, 'render.js'), 'utf8');

const api = eval(animSrc + ';({ VIEW, Presentation, easeSmooth })');
eval(catV2Src); // IIFE: registers globalThis.CatV2
const CatV2 = globalThis.CatV2;
const { poseFor } = eval(renderSrc + ';({ poseFor })');

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

// id 0 puts the idle-motion wobble at `now` itself: kind 0 (a blink) for
// now in [0, idleMotionPeriodMs), offset `at` = now.
check('the slow-blink lid walks the lab envelope exactly', () => {
  const p = new api.Presentation();
  const lidAt = (now) => p.motionFor(0, 'idle', now).blinkLid;
  close(lidAt(0), 0, 'starts open');
  close(lidAt(175), 0.5, 'half-down at the down midpoint');
  close(lidAt(api.VIEW.slowBlinkDownMs), 1, 'fully down');
  close(lidAt(api.VIEW.slowBlinkDownMs + api.VIEW.slowBlinkHoldMs), 1, 'held');
  close(lidAt(725), 0.5, 'half-up at the up midpoint'); // 350+150+225, 225/450
  const total = api.VIEW.slowBlinkDownMs + api.VIEW.slowBlinkHoldMs + api.VIEW.slowBlinkUpMs;
  assert(lidAt(total) === undefined, 'over after the envelope');
});

check('the v1 snap blink is untouched beside the lid', () => {
  const p = new api.Presentation();
  const m100 = p.motionFor(0, 'idle', 100);
  assert(m100.eyesOverride === 'closed', 'v1 window: snapped closed');
  assert(m100.blinkLid !== undefined, 'v2 lid runs alongside');
  const m430 = p.motionFor(0, 'idle', 430); // past the 420ms v1 window
  assert(m430.eyesOverride === undefined, 'v1 window over: eyes open');
  assert(m430.blinkLid !== undefined, 'the eased lid is still easing');
});

check('only the blink slot wears a lid', () => {
  const p = new api.Presentation();
  // id 0, now in [4600, 9200): kind 1, the tail flick.
  const m = p.motionFor(0, 'idle', 4700);
  assert(m.blinkLid === undefined, 'tail-flick slot has no lid');
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
  assert(L.droplet === true, 'the splash droplet shows');
  close(L.head.r, 0.226, 'the locked head radius is untouched');
  assert(L.body.ry < 0.21, 'body floats flatter than standing');
  assert(L.eyes === 'open', 'eyes open above water');
  assert(L.earsUpright === true, 'ears dry and up');
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

console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
