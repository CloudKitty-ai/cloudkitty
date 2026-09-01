// Re-cut a meow-census jsonl: how often does a served meow land on a pose the
// meow ANIMATION can actually be seen on?
//
// Replays the census through the REAL Presentation and the REAL poseFor, so
// facing, movement and the axial lock are the client's own answers rather
// than a second implementation of them. Usage: node meow-analyze.mjs <file>
import { readFileSync } from 'node:fs';

const D = new URL('../../client/', import.meta.url).pathname;
const api = eval(readFileSync(D + 'anim.js', 'utf8') + ';({VIEW, Presentation})');
const VIEW = api.VIEW;
const R = eval(
  readFileSync(D + 'cat.js', 'utf8') + '\n' + readFileSync(D + 'props.js', 'utf8') + '\n'
  + readFileSync(D + 'meadow.js', 'utf8') + '\n' + readFileSync(D + 'render.js', 'utf8')
  + ';({poseFor, chaseDistanceFor, AXIAL_POSES: (typeof AXIAL_POSES !== "undefined" ? AXIAL_POSES : null)})',
);
const AX = globalThis.CatV2?.AXIAL_POSES
  ?? new Set(['walking', 'idle', 'swim', 'grooming-other']);

// The poses the call is GATED on, read from the shipped `VIEW` rather than
// restated. This was a literal `['walking', 'idle']` and the gate has since
// grown `pouncing` (2026-08-25) and `loaf` (2026-08-27) -- so the analyzer
// scored every meow on those two as a miss, which for `loaf` is precisely the
// question the 041 re-census exists to answer.
const GOOD_POSES = new Set(VIEW.meowPoses);

const lines = readFileSync(process.argv[2] || 'meow-census.jsonl', 'utf8')
  .trim().split('\n').map((l) => JSON.parse(l));

const p = new api.Presentation();
// Pass 1: the drawn state of every cat on every tick, keyed by tick.
// A meow is attributed to the tick it was SPOKEN, which is not the tick it is
// seen on: `recent_meows` is a rolling window and an entry first appears one
// tick after its own and lingers about ten. Filtering on `m.tick === w.tick`
// therefore matched nothing at all -- 169 real events read as zero, which is
// exactly F-029's trap (an absent category is not evidence of absence until
// the instrument is shown able to emit one). It was shown: the raw carries
// purr / want_eat / want_bath / here_water / mew / want_drink.
const drawn = new Map();
let catTicks = 0;
for (const w of lines) {
  const world = {
    ...w,
    kitties: w.kitties.map((k) => ({ ...k, activity: k.state ? { state: k.state } : undefined })),
  };
  p.pushState(world, w.tick * 800);
  for (const k of world.kitties) {
    catTicks += 1;
    const moved = p.movedFor(k.id);
    const onWater = w.elements.some((e) => e.kind === 'water' && e.pos.x === k.pos.x && e.pos.y === k.pos.y);
    const pose = R.poseFor(k, moved, onWater, R.chaseDistanceFor(k, world), false, VIEW);
    const facing = p.facingFor(k.id);
    const axial = p.axialFor(k.id, AX.has(pose)) && (facing === 'north' || facing === 'south');
    drawn.set(`${k.id}:${w.tick}`, {
      name: k.name, pose, facing,
      view: axial ? (facing === 'north' ? 'back' : 'front') : 'side',
    });
  }
}

// Pass 2: every unique meow, looked up at the tick it was spoken.
const seenMeow = new Set();
const rows = [];
let unresolved = 0;
for (const w of lines) {
  for (const m of (w.recent_meows || [])) {
    const key = `${m.kitty_id}:${m.tick}:${m.kind}`;
    if (seenMeow.has(key)) continue;
    seenMeow.add(key);
    const at = drawn.get(`${m.kitty_id}:${m.tick}`);
    if (!at) { unresolved += 1; continue; } // spoken before the window opened
    rows.push({ id: m.kitty_id, name: at.name, kind: m.kind, tick: m.tick, ...at });
  }
}

const NAMES = {};
for (const r of rows) NAMES[r.id] = r.name;
const speech = rows.filter((r) => r.kind !== 'purr');
const shows = (r) => GOOD_POSES.has(r.pose) && r.view !== 'back';
const minutes = (lines.length * 800) / 60000;

console.log(`${lines.length} ticks (${minutes.toFixed(1)} min of world), ${catTicks} cat-ticks`);
if (unresolved) console.log(`(${unresolved} meows spoken before the window opened, dropped)`);
console.log(`meow events: ${rows.length} total, ${rows.length - speech.length} purrs, ${speech.length} speech\n`);

const byKind = {};
for (const r of speech) byKind[r.kind] = (byKind[r.kind] || 0) + 1;
console.log('speech by kind:', JSON.stringify(byKind));

const byPose = {};
for (const r of speech) byPose[r.pose] = (byPose[r.pose] || 0) + 1;
console.log('speech by POSE :', JSON.stringify(byPose));
const byView = {};
for (const r of speech) byView[r.view] = (byView[r.view] || 0) + 1;
console.log('speech by VIEW :', JSON.stringify(byView));

console.log('\ncat           speech   would ANIMATE   per hour animated');
const ids = [...new Set(speech.map((r) => r.id))].sort();
let ok = 0;
for (const id of ids) {
  const mine = speech.filter((r) => r.id === id);
  const good = mine.filter(shows).length;
  ok += good;
  console.log(
    (NAMES[id] || id).padEnd(13) + String(mine.length).padStart(5)
    + String(good).padStart(14) + `   ${(good / (minutes / 60)).toFixed(1)}`.padStart(14),
  );
}
console.log(`\n${ok} of ${speech.length} speech events land on ${[...GOOD_POSES].join('/')} with a face `
  + `= ${(ok / Math.max(1, speech.length) * 100).toFixed(0)}%`);
console.log(`roster rate: ${(ok / (minutes / 60)).toFixed(1)} animated meows per hour, `
  + `one every ${(60 / Math.max(0.01, ok / (minutes / 60))).toFixed(1)} minutes`);

// ...but the cat only OPENS ITS MOUTH for some of those. `meowFor` holds a
// per-cat cooldown, so a burst of eligible calls draws once and the rest are
// dropped on the floor -- not queued. Everything above is the ceiling; this is
// what a viewer sees, and the two diverge exactly when the world gets chatty.
const coolTicks = VIEW.meowCooldownMs / 800;
let drawnCount = 0;
const perCat = {};
for (const id of ids) {
  const mine = speech.filter((r) => r.id === id && shows(r)).sort((a, b) => a.tick - b.tick);
  let last = -Infinity;
  let n = 0;
  for (const r of mine) {
    if (r.tick - last < coolTicks) continue;
    last = r.tick;
    n += 1;
  }
  perCat[NAMES[id] || id] = n;
  drawnCount += n;
}
console.log(`\nafter the ${VIEW.meowCooldownMs / 1000}s per-cat cooldown: ${drawnCount} actually drawn `
  + `= ${(drawnCount / (minutes / 60)).toFixed(1)} per hour, one every `
  + `${(60 / Math.max(0.01, drawnCount / (minutes / 60))).toFixed(1)} minutes`);
console.log('  per cat:', JSON.stringify(perCat));
if (ok > 0) {
  console.log(`  the cooldown drops ${ok - drawnCount} of ${ok} eligible calls `
    + `(${((1 - drawnCount / ok) * 100).toFixed(0)}%)`);
}
