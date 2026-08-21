/**
 * What would the camera do, given where the kitties actually are?
 *
 *   node client-measurements/camera-aim/camera-analyze.mjs sample.jsonl
 *
 * Three questions, and the third was the one worth asking:
 *
 *   1. How far does the AIM move per tick, and how often does it break the
 *      deadzone? (Centre of mass, against the densest-neighbourhood centroid
 *      the owner proposed on 2026-08-20.)
 *   2. How often would the SUBJECT change under a density rule?
 *   3. How far does the WIDTH target move -- and is the fit governing at all?
 *
 * The dials are read as literals here rather than imported: this is a model
 * of the camera, not the camera, and pretending otherwise by importing
 * anim.js would make it look authoritative about behaviour it does not run.
 */
import { readFileSync } from 'node:fs';

const DEADZONE = 1.5;   // VIEW.camera.aimDeadzoneTiles
const MARGIN = 2.6;     // VIEW.camera.fitMarginTiles
const FLOOR = 7;        // minTiles, which binds on every map under 791px
const CEILING = 13.33;  // world / minZoomVsBase on a 20-tile world
const TICK_MS = 800;

const ticks = readFileSync(process.argv[2] || 'sample.jsonl', 'utf8')
  .trim().split('\n').map((l) => JSON.parse(l));
const mins = (ticks.length * TICK_MS) / 60000;

const dist = (a, b) => Math.hypot(a.x - b.x, a.y - b.y);
const mean = (p) => ({ x: p.reduce((s, q) => s + q.x, 0) / p.length, y: p.reduce((s, q) => s + q.y, 0) / p.length });
const span = (p) => {
  const xs = p.map((q) => q.x); const ys = p.map((q) => q.y);
  return Math.max(Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys));
};

/** The kitty with the most others within R, and that neighbourhood. Ties keep
 *  the previous subject, which is the cheapest possible hysteresis -- and the
 *  result is still worse than the centre of mass, see the README. */
function densest(ks, R, prevId) {
  let best = null;
  for (const k of ks) {
    const near = ks.filter((o) => dist(k, o) <= R);
    if (!best || near.length > best.near.length
      || (near.length === best.near.length && k.id === prevId)) best = { k, near };
  }
  return best;
}

/** A held target that only moves when its goal drifts past the deadzone --
 *  which is what the camera actually does, and NOT the same as the per-tick
 *  delta. Measuring the delta alone understates a slow, steady drift. */
const releases = (goals) => {
  let held = goals[0]; let n = 0;
  for (const g of goals) if (dist(held, g) > DEADZONE) { held = g; n += 1; }
  return n;
};

const stats = (d) => {
  const s = [...d].sort((a, b) => a - b);
  return {
    median: s[Math.floor(s.length / 2)],
    p90: s[Math.floor(s.length * 0.9)],
    mean: d.reduce((a, b) => a + b, 0) / d.length,
  };
};
const deltas = (pts) => pts.slice(1).map((p, i) => dist(pts[i], p));
const row = (label, pts, extra = '') => {
  const s = stats(deltas(pts));
  console.log(`${label.padEnd(28)} median ${s.median.toFixed(2).padStart(5)}  p90 ${s.p90.toFixed(2).padStart(5)}`
    + `  mean ${s.mean.toFixed(2).padStart(5)}  releases ${(releases(pts) / mins).toFixed(1).padStart(5)}/min${extra}`);
};

console.log(`${ticks.length} ticks (${mins.toFixed(1)} min), ${ticks[0].kitties.length} kitties\n`);
console.log('THE AIM, in tiles per tick — lower is a calmer camera');
row('centre of mass (ships)', ticks.map((t) => mean(t.kitties)));
for (const R of [4, 5, 6]) {
  let prev = null; let switches = 0; let groupSum = 0; let spanSum = 0;
  const pts = ticks.map((t) => {
    const b = densest(t.kitties, R, prev);
    if (prev !== null && b.k.id !== prev) switches += 1;
    prev = b.k.id; groupSum += b.near.length; spanSum += span(b.near);
    return mean(b.near);
  });
  row(`densest neighbourhood R=${R}`, pts,
    `  subject ${(switches / mins).toFixed(1)}/min  group ${(groupSum / ticks.length).toFixed(2)} cats`
    + `  span ${(spanSum / ticks.length).toFixed(1)}t`);
}

console.log('\nTHE WIDTH, in tiles per tick');
const raw = ticks.map((t) => span(t.kitties) + 2 * MARGIN);
const clamped = raw.map((v) => Math.min(Math.max(v, FLOOR), CEILING));
for (const [label, arr] of [['raw fit (span + margin)', raw], ['after the clamp', clamped]]) {
  const s = stats(arr.slice(1).map((v, i) => Math.abs(v - arr[i])));
  console.log(`${label.padEnd(28)} median ${s.median.toFixed(2).padStart(5)}  p90 ${s.p90.toFixed(2).padStart(5)}  mean ${s.mean.toFixed(2).padStart(5)}`);
}
const bound = clamped.filter((v) => v >= CEILING - 1e-9).length;
console.log(`\nbound at the ceiling ${(100 * bound / clamped.length).toFixed(0)}% of ticks`);
console.log(`the fit asks for a median ${stats(raw).median.toFixed(1)} tiles against a ${CEILING} ceiling`);
