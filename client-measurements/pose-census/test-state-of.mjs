/**
 * Headless checks for `stateOf` -- run with
 * `node client-measurements/pose-census/test-state-of.mjs`.
 *
 * Owner call #357, ruled option B on 2026-09-08: "#357: ruled B".
 *
 * The harness pattern of client/test-motion.mjs: no toolchain, drive the
 * function directly, count and exit non-zero on any failure.
 *
 * Every fixture is RECORDED, not composed: served kitties are pasted from a
 * `GET /world` response and the census rows from real tool output, each with
 * its tick. They are TRIMMED to the keys these functions touch -- a served
 * kitty also carries `needs`, `happiness`, `behavior` and more -- so they are
 * verbatim in their values, not complete as payloads. Nothing is read from a
 * file because neither raw is committed: the served world is live, and this
 * directory's jsonl is gitignored.
 *
 * Every check below calls a function under test. Two earlier ones did not --
 * they asserted properties of a hand-written literal, which cannot go red for
 * any change to state-of.mjs, and stayed green under every code mutation.
 * What they were documenting is recorded as comments where the assumptions
 * belong; the guarding is done by the censusKitty checks, against rows those
 * functions actually produce.
 */
import { stateOf, asServed, censusKitty } from './state-of.mjs';

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

// pose-census.mjs output BEFORE it captured `activity`:
// census-2026-08-23.jsonl line 1, tick 226217, kitty 1. Every banked raw
// looks like this and the readers must keep taking it.
const JSONL_OLD = {
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

// pose-census.mjs output AFTER it captured `activity`, tick 1946891, kitty 3.
// `target: 5` is the point of the widening: a sibling field the flat capture
// discarded, on a raw that cannot be re-collected once the world moves on.
const JSONL_BOTH = {
  id: 3,
  name: 'Pumpkin',
  pos: { x: 10, y: 1 },
  state: 'grooming',
  activity: { state: 'grooming', target: 5 },
  last_action: { action: 'groom', target: 5 },
};

check('flat: reads the top-level state a pre-widening raw carries', () => {
  assert(stateOf(JSONL_OLD) === 'sleeping',
    `got ${JSON.stringify(stateOf(JSONL_OLD))}, want 'sleeping'`);
});

check('neither shape present is null, the value the capture tools already wrote', () => {
  assert(stateOf({ id: 1, name: 'Miso' }) === null,
    `got ${JSON.stringify(stateOf({ id: 1, name: 'Miso' }))}, want null`);
});

// TWO ASSUMPTIONS THE SWAPS REST ON, neither of them testable from here.
// Recorded rather than asserted, because an assertion over a fixture typed in
// this file cannot notice either one becoming false.
//
// 1. A served kitty has no top-level `state`. pose-census.mjs and
//    meow-census.mjs poll /world and used to write `k.activity?.state ??
//    null`; stateOf adds a `?? k.state` branch between those two, which is
//    dead only while this holds. The evidence is the engine type, not
//    anything in JavaScript: `Kitty` in crates/cloudkitty-core/src/kitty.rs
//    has `activity: Activity` and no `state` field, and `Activity` is
//    serialized internally tagged on `state`. If that ever changes, this file
//    will not be what tells you.
// 2. Where a row carries both shapes, they agree. scene-vs-action.mjs reads
//    the jsonl and used to write `k.state ?? null`; stateOf puts
//    `k.activity?.state` AHEAD of that, so on a widened row precedence
//    decides. This one IS guarded, by `censusKitty: the two shapes it writes
//    agree` below -- against a row censusKitty produces, which is the only
//    place a widened row comes from.

// --- asServed: the flat -> served direction, for replay through the client ---

check('asServed: a pre-widening raw is reconstructed, and loses its flat state', () => {
  const k = asServed(JSONL_OLD);
  assert(k.activity?.state === 'sleeping', `activity came back ${JSON.stringify(k.activity)}`);
  assert(!('state' in k), `the result is a hybrid carrying both shapes: ${JSON.stringify(k)}`);
  assert(k.last_action?.action === 'sleep', 'the rest of the kitty did not survive');
});

check('asServed: a captured activity passes through with its sibling fields', () => {
  const k = asServed(JSONL_BOTH);
  assert(k.activity?.target === 5,
    `the sibling field was dropped, so the replay sees a poorer kitty than the client: ${JSON.stringify(k.activity)}`);
  assert(k.activity === JSONL_BOTH.activity, 'the captured activity was rebuilt rather than passed through');
  assert(!('state' in k), `the result is a hybrid carrying both shapes: ${JSON.stringify(k)}`);
});

check('asServed: a censusKitty row with no activity comes back clean, not half-shaped', () => {
  // The composition the pipeline actually performs: capture writes the row,
  // replay hands it to the client. censusKitty writes `activity: null` for a
  // kitty that has none, so asServed has to strip that key rather than pass
  // it through -- a kitty carrying `activity: null` is neither shape.
  const k = asServed(censusKitty({ id: 1, name: 'Miso', pos: { x: 0, y: 0 } }));
  assert(!('activity' in k),
    `a null activity survived into the replay: ${JSON.stringify(k)}`);
  assert(!('state' in k), `the result is a hybrid carrying both shapes: ${JSON.stringify(k)}`);
  assert(k.id === 1 && k.name === 'Miso', 'the rest of the kitty did not survive');
});

// --- censusKitty: what the two capture tools write ---

// GET https://kitties.ai/world, tick 1950821, kitty 3. A whole served kitty
// with a sibling field on its activity.
const SERVED_FULL = {
  id: 3,
  name: 'Pumpkin',
  pos: { x: 10, y: 3 },
  activity: { state: 'grooming', target: 2 },
  last_action: { action: 'groom', target: 2 },
};

check('censusKitty: keeps the flat tag every banked raw and analyzer relies on', () => {
  const row = censusKitty(SERVED_FULL);
  assert(row.state === 'grooming', `flat state came out ${JSON.stringify(row.state)}`);
  assert(stateOf(row) === 'grooming', 'the row does not read back through stateOf');
});

check('censusKitty: banks the whole activity, not just the tag', () => {
  const row = censusKitty(SERVED_FULL);
  assert(row.activity?.target === 2,
    'the sibling field was discarded at capture and cannot be recovered later '
    + '(the raw is collected against a world that then moves on). If you are '
    + 'narrowing capture back to the flat tag to satisfy owner call #357: the '
    + 'owner set that assumption aside on 2026-09-08 -- "the flat `state` tag '
    + 'is always written, and the full `activity` object may ride alongside '
    + 'it". See the second conventions bullet in client-measurements/README.md. '
    + `Got ${JSON.stringify(row.activity)}`);
});

check('censusKitty: the two shapes it writes agree, which is what makes precedence safe', () => {
  const row = censusKitty(SERVED_FULL);
  assert(row.activity.state === row.state,
    `nested ${JSON.stringify(row.activity.state)} != flat ${JSON.stringify(row.state)}`);
});

check('censusKitty: a kitty with no activity still yields a readable row', () => {
  const row = censusKitty({ id: 1, name: 'Miso', pos: { x: 0, y: 0 } });
  assert(row.state === null, `state came out ${JSON.stringify(row.state)}, want null`);
  assert(row.activity === null, `activity came out ${JSON.stringify(row.activity)}, want null`);
  assert(row.last_action === null, 'last_action should be null, as both tools already wrote');
});

console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
