// Replay a census and compare the shipped poseFor against a chase-distance gate.
// Usage: node pose-analyze.mjs census.jsonl [gate]
import { readFileSync } from 'node:fs';

const file = process.argv[2] ?? 'census.jsonl';
const GATE = Number(process.argv[3] ?? 4);

const rows = readFileSync(file, 'utf8')
  .split('\n')
  .filter(Boolean)
  .map((l) => JSON.parse(l));
const byTick = new Map(rows.map((r) => [r.tick, r]));
const ticks = [...byTick.keys()].sort((a, b) => a - b);

const manhattan = (a, b) => Math.abs(a.x - b.x) + Math.abs(a.y - b.y);

/**
 * The rule as it stood BEFORE the gate shipped -- the counterfactual now,
 * kept so the cost of the gate stays measurable after the fact.
 */
function poseUngated(state, action, moved, onWater) {
  if (state === 'sleeping') return 'sleep-curl';
  if (state === 'resting') return 'loaf';
  if (state === 'eating') return 'eating';
  if (state === 'drinking') return 'drinking';
  if (state === 'grooming') return 'grooming';
  if (action === 'play' || action === 'chase') return 'pouncing';
  if (onWater) return 'swim';
  if (moved) return 'walking';
  return 'idle';
}

/**
 * render.js:64 -- the shipped rule, verbatim, gate and all. Keep this in
 * step with render.js: it is a copy, and a copy that drifts reports on a
 * client nobody is running.
 */
function poseFor(state, action, moved, onWater, near) {
  if (state === 'sleeping') return 'sleep-curl';
  if (state === 'resting') return 'loaf';
  if (state === 'eating') return 'eating';
  if (state === 'drinking') return 'drinking';
  if (state === 'grooming') return 'grooming';
  if (action === 'play') return 'pouncing';
  if (action === 'chase' && near) return 'pouncing';
  if (onWater) return 'swim';
  if (moved) return 'walking';
  return 'idle';
}

const now = new Map();
const gated = new Map();
const dists = [];
const chaseKind = { element: 0, kitty: 0 };
const playKind = { solo: 0, element: 0, kitty: 0 };
let pairs = 0;
let gaps = 0;
let unresolved = 0;
let chaseNoMove = 0;
const movedWhenChasing = { moved: 0, still: 0 };
const seq = new Map(); // id -> [{tick, now, gate}] for churn analysis

const bump = (m, k) => m.set(k, (m.get(k) ?? 0) + 1);

for (let i = 1; i < ticks.length; i++) {
  const t0 = ticks[i - 1];
  const t1 = ticks[i];
  if (t1 !== t0 + 1) {
    gaps++;
    continue;
  }
  const prev = byTick.get(t0);
  const cur = byTick.get(t1);
  const wasAt = new Map(prev.kitties.map((k) => [k.id, k.pos]));
  const kittyPos = new Map(cur.kitties.map((k) => [k.id, k.pos]));
  const elPos = new Map(cur.elements.map((e) => [e.id, e.pos]));
  const water = new Set(
    cur.elements.filter((e) => e.kind === 'water').map((e) => `${e.pos.x},${e.pos.y}`),
  );

  for (const k of cur.kitties) {
    const was = wasAt.get(k.id);
    if (!was) continue;
    pairs++;
    const moved = was.x !== k.pos.x || was.y !== k.pos.y;
    const onWater = water.has(`${k.pos.x},${k.pos.y}`);
    const action = k.last_action?.action ?? null;

    let near = false;
    if (action === 'chase') {
      chaseKind[k.last_action.target] = (chaseKind[k.last_action.target] ?? 0) + 1;
      const tp =
        k.last_action.target === 'element'
          ? elPos.get(k.last_action.id)
          : kittyPos.get(k.last_action.id);
      if (tp) {
        const d = manhattan(k.pos, tp);
        dists.push(d);
        near = d <= GATE;
      } else {
        unresolved++; // target gone this tick: cannot verify proximity
      }
      if (moved) movedWhenChasing.moved++;
      else {
        movedWhenChasing.still++;
        chaseNoMove++;
      }
    }
    if (action === 'play') {
      const kind = k.last_action.target ?? 'solo';
      playKind[kind] = (playKind[kind] ?? 0) + 1;
    }

    const pNow = poseUngated(k.activity?.state ?? k.state, action, moved, onWater);
    const pGate = poseFor(k.activity?.state ?? k.state, action, moved, onWater, near);
    bump(now, pNow);
    bump(gated, pGate);
    seq.set(k.id, [...(seq.get(k.id) ?? []), { tick: t1, now: pNow, gate: pGate }]);
  }
}

// Pose churn: a distance gate can flicker when a target hovers at the boundary.
// Count switches between consecutive ticks, and how many reverse within 2 ticks.
function churn(pick) {
  let switches = 0;
  let flicker = 0;
  for (const runs of seq.values()) {
    for (let i = 1; i < runs.length; i++) {
      if (runs[i].tick !== runs[i - 1].tick + 1) continue;
      if (pick(runs[i]) === pick(runs[i - 1])) continue;
      switches++;
      for (let j = i + 1; j <= i + 2 && j < runs.length; j++) {
        if (runs[j].tick !== runs[j - 1].tick + 1) break;
        if (pick(runs[j]) === pick(runs[i - 1])) {
          flicker++;
          break;
        }
      }
    }
  }
  return { switches, flicker };
}

const pct = (n) => ((100 * n) / pairs).toFixed(2).padStart(6) + '%';
const keys = [...new Set([...now.keys(), ...gated.keys()])].sort();

console.log(`ticks sampled: ${ticks.length}  usable consecutive pairs: ${pairs} kitty-ticks  (gaps skipped: ${gaps})`);
console.log(`gate: chase pounces only within ${GATE} tiles (Manhattan)\n`);
console.log('pose          ungated     SHIPPED    delta');
for (const key of keys) {
  const a = now.get(key) ?? 0;
  const b = gated.get(key) ?? 0;
  const d = ((100 * (b - a)) / pairs).toFixed(2);
  console.log(
    `${key.padEnd(12)} ${pct(a)}  ${pct(b)}   ${(d > 0 ? '+' : '') + d}%   (${a} -> ${b})`,
  );
}

const cNow = churn((r) => r.now);
const cGate = churn((r) => r.gate);
console.log(
  `\npose switches between consecutive ticks: present ${cNow.switches} (${cNow.flicker} reverse within 2 ticks)` +
    `  ->  gated ${cGate.switches} (${cGate.flicker} reverse within 2 ticks)`,
);

dists.sort((a, b) => a - b);
const hist = new Map();
for (const d of dists) hist.set(d, (hist.get(d) ?? 0) + 1);
console.log(`\nchase kitty-ticks: ${dists.length + unresolved}  (target gone, unresolvable: ${unresolved})`);
console.log(`  by target: ${JSON.stringify(chaseKind)}   moved this tick: ${movedWhenChasing.moved}, stood still: ${movedWhenChasing.still}`);
console.log(`  play kitty-ticks by target: ${JSON.stringify(playKind)}`);
if (dists.length) {
  const q = (p) => dists[Math.min(dists.length - 1, Math.floor(p * dists.length))];
  console.log(`  distance: min ${dists[0]}  p25 ${q(0.25)}  median ${q(0.5)}  p75 ${q(0.75)}  p90 ${q(0.9)}  max ${dists.at(-1)}`);
  const within = dists.filter((d) => d <= GATE).length;
  console.log(`  within ${GATE}: ${within}/${dists.length} = ${((100 * within) / dists.length).toFixed(1)}%`);
  console.log('  histogram (distance: count):');
  for (const d of [...hist.keys()].sort((a, b) => a - b)) {
    console.log(`    ${String(d).padStart(2)}: ${'#'.repeat(Math.ceil(hist.get(d) / 2))} ${hist.get(d)}`);
  }
  console.log('\n  cumulative share of chase ticks kept as pounce, by gate:');
  for (const g of [1, 2, 3, 4, 5, 6, 8, 10]) {
    const n = dists.filter((d) => d <= g).length;
    console.log(`    <=${String(g).padStart(2)}: ${((100 * n) / dists.length).toFixed(1)}% of chases   (${((100 * n) / pairs).toFixed(2)}% of all kitty-ticks)`);
  }
}
