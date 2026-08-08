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
    ' idlePickFor, idleOffsetFor, anim })',
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
// render.js reads `VIEW` as a global (the browser loads anim.js alongside
// it); each eval here gets its own scope, so hand it one. Direct eval runs
// in this scope, so the binding is visible to the code below -- and it is
// the SAME object anim.js built, so a re-dialled tunable cannot diverge
// between what the harness tests and what the page draws.
const VIEW = api.VIEW;
const { poseFor, WorldRenderer, waterlineFor } = eval(
  renderSrc + ';({ poseFor, WorldRenderer, waterlineFor })',
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

check('the swim pose opts out however wet it is', () => {
  // It is already drawn sunk (cat-v2's SWIM); clipping would submerge it
  // a second time.
  for (const wet of [0.01, 0.3, 0.7, 1]) {
    assert(waterlineFor('swim', wet) === null, `swim at wet ${wet}`);
  }
});

check('a land pose in water is clipped, and the pose does not change where', () => {
  // The whole point: poseFor lets these outrank the wade, so they must
  // all meet the same surface.
  const poses = ['grooming', 'drinking', 'eating', 'loaf', 'sleep-curl', 'idle', 'pouncing'];
  const at = poses.map((p) => waterlineFor(p, 1));
  for (let i = 0; i < poses.length; i += 1) {
    close(at[i], api.VIEW.waterline, `${poses[i]} fully wet`);
  }
});

check('the surface rises from the ground line, monotonically', () => {
  // Derived from VIEW, never a copy of it -- a re-dialled waterline must
  // not need this test edited.
  // Integer steps, and an epsilon on the endpoint: 0.88 - 1 * (0.88 - 0.72)
  // is 0.7199999999999999 in binary floating point, so an exact bound here
  // would fail on arithmetic rather than on behaviour.
  const EPS = 1e-9;
  let previous = GROUND + 1;
  for (let i = 1; i <= 50; i += 1) {
    const wet = i / 50;
    const cut = waterlineFor('grooming', wet);
    assert(cut < previous, `not monotonic at wet ${wet.toFixed(2)}`);
    assert(cut <= GROUND + EPS, `above the ground line at ${wet.toFixed(2)}: ${cut}`);
    assert(cut >= api.VIEW.waterline - EPS, `past the waterline at ${wet.toFixed(2)}: ${cut}`);
    previous = cut;
  }
  close(waterlineFor('grooming', 1), api.VIEW.waterline, 'fully wet sits exactly on the dial');
  // Half wet is half way, so the ease in `wetFor` is the only shaping.
  close(
    waterlineFor('grooming', 0.5),
    GROUND - 0.5 * (GROUND - api.VIEW.waterline),
    'halfway is halfway',
  );
});

check('the dial is honoured, not hardcoded', () => {
  const shallow = { waterline: 0.8 };
  const deep = { waterline: 0.6 };
  close(waterlineFor('grooming', 1, shallow), 0.8, 'shallow dial');
  close(waterlineFor('grooming', 1, deep), 0.6, 'deep dial');
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

  const leap = CatV2.catLayout('pouncing', 0.8); // phase >= 0.45 is the airborne half
  const leapShaped = reshaped({ bodyH: 1.2 }, () => CatV2.catLayout('pouncing', 0.8));
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

check('the pounce reaches both of its old positions exactly', () => {
  // The crouch and the leap are the drawings that shipped; only the frames
  // between them are new. Pinned as literals so an "improvement" to the
  // launch cannot quietly redraw either end.
  // Measured on the v1 body: these pin the POSE, not whatever the shape
  // dials are set to this week.
  const loaded = reshaped(IDENT, () => CatV2.catLayout('pouncing', 0));
  close(loaded.body.cy, 0.68, 'crouch body cy');
  close(loaded.body.ry, 0.17, 'crouch body ry');
  close(loaded.head.cy, 0.5, 'crouch head cy');
  assert(
    loaded.legs.every((l) => Math.abs(l.bottom - 0.88) < 1e-12),
    'the loaded cat has every foot on the ground',
  );

  const out = reshaped(IDENT, () => CatV2.catLayout('pouncing', 0.95));
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

check('the launch only ever extends, and holds at both ends', () => {
  const at = (p) => CatV2.catLayout('pouncing', p).body.cy;
  const P = CatV2.POUNCE;
  close(at(0), at(P.hold), 'the cat must stay loaded until the launch starts');
  close(at(Math.min(1, P.hold + P.launch)), at(1), 'and hold its reach afterwards');
  let prev = Infinity;
  for (let i = 0; i <= 200; i++) {
    const cy = at(i / 200);
    assert(cy <= prev + 1e-12, `the body dropped back mid-launch at phase ${i / 200}`);
    prev = cy;
  }
  assert(at(1) < at(0) - 0.05, 'the leap must actually rise off the crouch');
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

console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
