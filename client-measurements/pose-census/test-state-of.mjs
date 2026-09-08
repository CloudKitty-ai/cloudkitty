/**
 * Headless checks for `stateOf` -- run with
 * `node client-measurements/pose-census/test-state-of.mjs`.
 *
 * Owner call #357, ruled option B on 2026-09-08: "#357: ruled B".
 *
 * The harness pattern of client/test-motion.mjs: no toolchain, drive the
 * function directly, count and exit non-zero on any failure.
 *
 * Both fixtures are RECORDED, not composed. Neither raw is committed -- the
 * served world is live and this directory's jsonl is a local artifact -- so
 * they are pasted here verbatim with their provenance rather than read from
 * a file that is not in the tree.
 *
 * The last two checks are the ones that make the four call-site swaps
 * behaviour-preserving rather than merely plausible: each site gained a
 * fallback branch it did not have, and these say those branches are dead on
 * the shapes the site actually sees.
 */
import { stateOf } from './state-of.mjs';

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

// GET https://kitties.ai/world, tick 1946744, kitty 1. A tagged variant that
// carries its own fields, so the state is a key of `activity` and not the
// whole of it.
const SERVED_WITH_FIELDS = {
  id: 1,
  name: 'Miso',
  activity: { state: 'sleeping', in_sunbeam: false, with_friend: 2 },
};

// GET https://kitties.ai/world, tick 1946735, kitty 1. `Activity::Idle` is a
// unit variant, so `activity` is the tag alone.
const SERVED_UNIT = {
  id: 1,
  name: 'Miso',
  pos: { x: 19, y: 4 },
  activity: { state: 'idle' },
  last_action: { action: 'eat' },
};

// pose-census.mjs output, census-2026-08-23.jsonl line 1, tick 226217,
// kitty 1. What this directory writes, and what pose-analyze.mjs and
// scene-vs-action.mjs read back.
const JSONL_ROW = {
  id: 1,
  name: 'Miso',
  pos: { x: 13, y: 3 },
  state: 'sleeping',
  last_action: { action: 'sleep' },
};

check('nested: reads the tag out of a variant carrying its own fields', () => {
  assert(stateOf(SERVED_WITH_FIELDS) === 'sleeping',
    `got ${JSON.stringify(stateOf(SERVED_WITH_FIELDS))}, want 'sleeping'`);
});

check('nested: reads a unit variant', () => {
  assert(stateOf(SERVED_UNIT) === 'idle', `got ${JSON.stringify(stateOf(SERVED_UNIT))}, want 'idle'`);
});

check('flat: reads the top-level state this directory writes', () => {
  assert(stateOf(JSONL_ROW) === 'sleeping',
    `got ${JSON.stringify(stateOf(JSONL_ROW))}, want 'sleeping'`);
});

check('neither shape present is null, the value the capture tools already wrote', () => {
  assert(stateOf({ id: 1, name: 'Miso' }) === null,
    `got ${JSON.stringify(stateOf({ id: 1, name: 'Miso' }))}, want null`);
});

// pose-census.mjs:29 and meow-census.mjs:43 poll /world and used to write
// `k.activity?.state ?? null`. stateOf adds a `?? k.state` branch between
// those two. It can only change what they write if a served kitty ever
// carries a top-level `state` -- and the engine's Kitty struct has no such
// field, only `activity: Activity`.
check('the served shape has no top-level state, so the capture tools cannot change what they write', () => {
  for (const k of [SERVED_WITH_FIELDS, SERVED_UNIT]) {
    assert(!('state' in k), `a served kitty carries a top-level state: ${JSON.stringify(k)}`);
  }
});

// scene-vs-action.mjs:26 reads the jsonl and used to write `k.state ?? null`.
// stateOf puts `k.activity?.state` AHEAD of that, so it can only change what
// that tool counts if a jsonl row ever carries `activity`. pose-census.mjs
// writes five keys and `activity` is not one of them.
check('the jsonl shape has no activity, so the flat reader cannot change what it counts', () => {
  assert(!('activity' in JSONL_ROW), `a jsonl row carries activity: ${JSON.stringify(JSONL_ROW)}`);
});

console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
