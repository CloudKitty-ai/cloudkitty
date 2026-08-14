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

const api = eval(
  animSrc +
    ';({ VIEW, Presentation, Pacer, easeSmooth, slowBlinkLid, idleHash, idlePeriodFor,' +
    ' idlePickFor, idleOffsetFor, IDLE_SALTS, anim })',
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
  poseFor, WorldRenderer, waterlineFor, chaseDistanceFor, submersionFor, surfaceForPose,
  swimAxialAllows,
} = eval(
  renderSrc +
    ';({ poseFor, WorldRenderer, waterlineFor, chaseDistanceFor, submersionFor, surfaceForPose,' +
    ' swimAxialAllows })',
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
  for (const pal of [1, 2, 3, 4]) {
    const want = CatV2.lightenHex(CatV2.appearanceFor(pal).furBase, CatV2.BELLY.lighten);
    assert(fillStyles(pal).includes(want), `palette ${pal} has no belly (${want})`);
  }
  const tuxedo = CatV2.appearanceFor(0);
  const wouldBe = CatV2.lightenHex(tuxedo.furBase, CatV2.BELLY.lighten);
  assert(!fillStyles(0).includes(wouldBe), 'the tuxedo drew a belly behind its bib');
  assert(fillStyles(0).includes(tuxedo.pattern.color), 'the tuxedo still draws its bib');
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
  // Activities still outrank the whole branch, near or far.
  const busy = { ...chasing, activity: { state: 'grooming' } };
  assert(poseFor(busy, true, false, 0) === 'grooming', 'activity outranks a near chase');
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


check('every portrait pose fits inside the card chip', () => {
  // The chip was measured against the resting poses, and the idle vocabulary
  // has since grown two that are bigger than any of them: `stretch` is the
  // widest thing drawn anywhere and overran the old 54px chip by 2.2px, and
  // an idle->sit blend at full overshoot reached 6.6px off the left edge.
  // Nothing catches a portrait clipping except looking at it, so:
  const app = readFileSync(join(here, 'app.js'), 'utf8');
  const num = (name) => {
    const m = app.match(new RegExp(`const ${name} = ([\\d.]+);`));
    assert(m, `app.js still declares ${name}`);
    return Number(m[1]);
  };
  const W = num('PORTRAIT_W');
  const H = num('PORTRAIT_H');
  const SIZE = num('PORTRAIT_CAT');
  const X = num('PORTRAIT_X');
  const Y = num('PORTRAIT_Y');

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
    /t: Math\.min\(1, Math\.max\(0, tween\.blend\.t\)\)/.test(app),
    'the portrait blend is no longer clamped -- the overshoot will leave the chip',
  );
  // The wiring itself. Geometry checks pass perfectly well on a portrait that
  // has quietly gone back to a hardcoded 'idle', so the feature needs saying
  // out loud.
  assert(
    /view\.idleCardBeatFor\(id, 'idle'\)/.test(app),
    'the portrait no longer asks its own beat table for a pose',
  );
  assert(/idle\?\.pose \?\? 'idle'/.test(app), 'the portrait no longer USES the idle pose it asked for');
  // ...and the WORLD's wake-stretch stays out of it (2026-08-10). The card
  // took it until measurement showed cats wake every ~21s, which made the
  // stretch beat the blink -- and that the meadow, drawing first, deleted
  // `wokeAt` a tick later, so the portrait only ever got half a stretch.
  // Asserted as absence because there is no value to compare: re-adding the
  // call is the regression, and it would look perfectly reasonable in review.
  // Matched on the CALL, not the name -- the reasoning above has to be free
  // to talk about `idlePoseFor` without failing the check that enforces it.
  assert(
    !/view\.idlePoseFor\s*\(/.test(app),
    'the portrait is consulting idlePoseFor again -- the world wake-stretch will preempt the card table',
  );
  // And the key namespace, which is the part that breaks something else when
  // it goes: the presentation layer's pose memory is per-key, so a portrait
  // sharing the meadow cat's key restarts its blend every frame. Same hazard
  // rigFor documents, on a different map.
  assert(
    /tweenFor\(`card\$\{id\}`/.test(app),
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
  assert(p.expressionFor(pursuing('element', 9)) === 'focused', 'a cat hunting a bug has no hunting face');
  assert(p.expressionFor(pursuing('kitty', 2)) === undefined, 'a cat chasing a kitty wears the hunting face');
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
  const appSrc = readFileSync(join(here, 'app.js'), 'utf8');
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

check("the about survives a phase change, and the owner's words survive us", () => {
  const markup = readFileSync(join(here, 'index.html'), 'utf8');

  // A <details>, so it opens with no script at all: it still works with a
  // dead socket, under reduced motion, and before app.js has run. Wiring
  // it to a click handler would make "what is this place" the first thing
  // to break when anything else does.
  const about = markup.slice(markup.indexOf('<details class="about">'));
  assert(about.startsWith('<details'), 'the about is gone or is no longer a <details>');
  assert(/<summary>[^<]*about<\/summary>/.test(about), 'the about has no summary to click');

  // It must cost the map NOTHING. The map is height-bound and `resizeFor`
  // subtracts the header from its budget, so at a 20-row world every 20px
  // of header is a whole pixel off the tile -- and a pixel of tile is 20px
  // off each edge of the map. So the summary rides a line that already
  // exists, and the panel is taken out of flow rather than pushing the
  // layout down when it opens (owner, 2026-08-13).
  assert(
    /<span class="tagline">/.test(markup) && about.indexOf('</div>') > about.indexOf('</details>'),
    'the about is no longer inside the subtitle line, so it costs the map a row',
  );

  // The owner's copy, verbatim. Ours to lay out, not to edit.
  const wanted =
    'CloudKitty is a peaceful meadow where kitties wander, eat, drink, nap in ' +
    'sunbeams, groom each other, chase bugs, and meow about it. The kitties are ' +
    'a team. Each kitty is driven by a neural network trained for one objective: ' +
    'the happiness of all the kitties in the meadow. The kitties look out for ' +
    'each other, communicate with purrs and meows, and keep each other company ' +
    'as they frolic and play.';
  const got = about.slice(about.indexOf('<p>') + 3, about.indexOf('</p>'))
    .split(/\s+/).join(' ').trim();
  assert(got === wanted, `the about text has drifted from what the owner wrote:\n  ${got}`);

  // And the trap this page has already fallen into once (#193): the four
  // inverting tokens SWAP across a phase, so any colour written as a
  // literal here sits at the wrong end of the palette for half the day.
  // Each rule read on its own. A loose search across the whole block is
  // how the first version of this passed while the panel was back in the
  // layout: `display: inline` also matches the SUMMARY's rule, and
  // `position: absolute` was outside the slice entirely.
  const ruleFor = (selector) => {
    const at = markup.indexOf(`  ${selector} {`);
    assert(at > 0, `no CSS rule for ${selector}`);
    // To the closing brace, not to a newline-plus-brace: `.about` is a
    // ONE-LINER, so looking for `\n  }` ran straight past it and into the
    // summary's rule -- which also says `display: inline`, so the check
    // passed while the about had a row of its own again.
    return markup.slice(at, markup.indexOf('}', at) + 1);
  };
  const container = ruleFor('.about');
  const panel = ruleFor('.about > p');
  // The summary rides a line that already exists...
  assert(/display: inline;/.test(container), 'the about takes a row of its own again');
  // ...and the panel is out of flow, or opening it shrinks the meadow.
  assert(/position: absolute;/.test(panel), 'the about panel is back in the layout');
  assert(/var\(--card\)/.test(panel), 'the panel needs the card background to be readable over the map');

  const block = container + panel + ruleFor('.about > summary');
  const literals = block.match(/#[0-9a-fA-F]{3,8}|rgba?\(/g);
  assert(!literals, `the about hardcodes ${literals} instead of using a theme token`);
  assert(/var\(--ink-soft\)/.test(block), 'the about must take its colour from the palette');
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

console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
