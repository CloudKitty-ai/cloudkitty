/**
 * Headless checks for `shipped-pose.mjs` -- run with
 * `node client-measurements/pose-census/test-shipped-pose.mjs`.
 *
 * Owner call #362, ruled option B on 2026-09-08: "Ruled: B".
 *
 * These are characterization checks on the CLIENT's own `poseFor`, reached
 * through the loader. They are not here to pin the client's behaviour -- the
 * client is free to change and these follow it. They are here so that
 * replacing the loader with a hand-copy goes red, which is the failure this
 * ruling exists to prevent: the previous copy drifted for six weeks and
 * disagreed with the client on 21-23% of kitty-ticks.
 *
 * Each check names the drift it would have caught.
 */
import { poseFor, chaseDistanceFor, dialsWithGate, lungedBetween, VIEW } from './shipped-pose.mjs';

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

const kitty = (activity, last_action, pos = { x: 0, y: 0 }) => ({ id: 1, pos, activity, last_action });
const SHIPPED = dialsWithGate(VIEW.pounceGateTiles);

check('the applied action outranks the running scene (drift 2026-08-13, ACTION_POSE)', () => {
  // 134 ticks in meow2.jsonl looked like this and the old copy called them idle.
  const k = kitty({ state: 'idle' }, { action: 'drink' });
  assert(poseFor(k, false, false, null, false, SHIPPED) === 'drinking',
    `got ${poseFor(k, false, false, null, false, SHIPPED)}, want drinking`);
});

check('grooming names its pose by target (drift 2026-08-22, grooming-other)', () => {
  const withTarget = kitty({ state: 'grooming' }, { action: 'groom', target: 5 });
  const alone = kitty({ state: 'grooming' }, { action: 'groom' });
  assert(poseFor(withTarget, false, false, null, false, SHIPPED) === 'grooming-other',
    `targeted groom came out ${poseFor(withTarget, false, false, null, false, SHIPPED)}`);
  assert(poseFor(alone, false, false, null, false, SHIPPED) === 'grooming',
    `solo groom came out ${poseFor(alone, false, false, null, false, SHIPPED)}`);
});

check('the action outranks water too', () => {
  // The old copy checked onWater before the action, so these read as swim.
  const k = kitty({ state: 'idle' }, { action: 'eat' });
  assert(poseFor(k, true, true, null, false, SHIPPED) === 'eating',
    `got ${poseFor(k, true, true, null, false, SHIPPED)}, want eating`);
});

check('the chase gate is the shipped dial, and it bites', () => {
  const k = kitty({ state: 'idle' }, { action: 'chase', target: 'kitty', id: 2 });
  const g = VIEW.pounceGateTiles;
  assert(poseFor(k, true, false, g, false, SHIPPED) === 'pouncing', `at the gate (${g}) it should pounce`);
  assert(poseFor(k, true, false, g + 1, false, SHIPPED) === 'walking',
    `one tile beyond the gate it should walk, got ${poseFor(k, true, false, g + 1, false, SHIPPED)}`);
});

check('an unresolvable quarry KEEPS the pounce (the old copy dropped it)', () => {
  const k = kitty({ state: 'idle' }, { action: 'chase', target: 'kitty', id: 99 });
  assert(poseFor(k, true, false, null, false, SHIPPED) === 'pouncing',
    'a null distance must not take the pounce away -- the gate only acts on positive evidence');
});

check('a lunge outranks the gate (the old copy had no lunged argument)', () => {
  const k = kitty({ state: 'idle' }, { action: 'chase', target: 'kitty', id: 2 });
  const far = VIEW.pounceGateTiles + 3;
  assert(poseFor(k, true, false, far, true, SHIPPED) === 'pouncing', 'a lunge should pounce at any distance');
  assert(poseFor(k, true, false, far, false, SHIPPED) === 'walking', 'without the lunge it should walk');
});

check('dialsWithGate(Infinity) is the no-gate column, without a second rule', () => {
  const k = kitty({ state: 'idle' }, { action: 'chase', target: 'kitty', id: 2 });
  assert(poseFor(k, true, false, 999, false, dialsWithGate(Infinity)) === 'pouncing',
    'opening the gate must make every chase pounce');
});

check('lungedBetween matches the client rule: a chase that stepped exactly two tiles', () => {
  const chase = { action: 'chase', target: 'kitty', id: 2 };
  assert(lungedBetween({ x: 0, y: 0 }, kitty({ state: 'idle' }, chase, { x: 2, y: 0 })), 'two tiles is a lunge');
  assert(!lungedBetween({ x: 0, y: 0 }, kitty({ state: 'idle' }, chase, { x: 1, y: 0 })), 'one tile is not');
  assert(!lungedBetween({ x: 0, y: 0 }, kitty({ state: 'idle' }, { action: 'move' }, { x: 2, y: 0 })),
    'only a chase lunges -- leapFor returns null for any other action');
});

check('chaseDistanceFor resolves out of the world, and null when it cannot', () => {
  const k = kitty({ state: 'idle' }, { action: 'chase', target: 'kitty', id: 2 }, { x: 1, y: 1 });
  const world = { kitties: [k, { id: 2, pos: { x: 4, y: 1 } }], elements: [] };
  assert(chaseDistanceFor(k, world) === 3, `got ${chaseDistanceFor(k, world)}, want 3`);
  assert(chaseDistanceFor(k, { kitties: [k], elements: [] }) === null, 'a missing quarry is null, not a distance');
});

console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
