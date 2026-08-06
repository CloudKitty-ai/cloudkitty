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
    ';({ VIEW, Presentation, easeSmooth, slowBlinkLid, idleHash, idlePeriodFor,' +
    ' idlePickFor, idleOffsetFor })',
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
  const dials = { ...api.VIEW, idleBlinkWeight: 70, idleEarsWeight: 20, idleRestWeight: 10 };
  const seen = { blink: 0, ears: 0, rest: 0 };
  const N = 4000;
  for (let slot = 0; slot < N; slot++) seen[api.idlePickFor(1, slot, dials)]++;
  // Loose bounds: this is asserting the draw is weighted, not that the
  // hash is a perfect uniform generator.
  assert(Math.abs(seen.blink / N - 0.7) < 0.03, `blink share ${(seen.blink / N).toFixed(3)} ~ 0.70`);
  assert(Math.abs(seen.ears / N - 0.2) < 0.03, `ears share ${(seen.ears / N).toFixed(3)} ~ 0.20`);
  assert(Math.abs(seen.rest / N - 0.1) < 0.03, `rest share ${(seen.rest / N).toFixed(3)} ~ 0.10`);
  // All the weight on one motion means every slot draws it.
  const only = { ...api.VIEW, idleBlinkWeight: 0, idleEarsWeight: 1, idleRestWeight: 0 };
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

check('a shoreline crossing fades over wetFadeMs, both ways', () => {
  const p = new api.Presentation();
  p.wetFor(1, true, 1000); // settled, in the water
  close(p.wetFor(1, false, 1000), 1, 'still wet at the moment it steps out');
  close(p.wetFor(1, false, 1130), 0.5, 'half dry a half-fade later');
  close(p.wetFor(1, false, 1260), 0, 'dry when the fade ends');
  close(p.wetFor(1, false, 5000), 0, 'and stays dry');
});

check('darting in and out resumes from the part-fade, never snapping', () => {
  const p = new api.Presentation();
  p.wetFor(1, true, 1000); // settled, in the water
  p.wetFor(1, false, 1000); // steps out: the fade starts here
  close(p.wetFor(1, false, 1130), 0.5, 'half dry on the way out');
  close(p.wetFor(1, true, 1130), 0.5, 'turning back does not snap to wet');
  close(p.wetFor(1, true, 1260), 0.75, 'it re-wets from where it had got to');
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

console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
