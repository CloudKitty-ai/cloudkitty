// Does the pounce gate disagree with spec 039's lunge?
//
// `leapFor` (client/anim.js) keys on the SERVED two-tile step of a chasing
// kitty and never consults `pounceGateTiles`, so the gate can never suppress
// a leap -- only leave one flying its arc while the cat is drawn walking.
// This asks, for a candidate gate, how often that happens.
//
// Usage: node leap-strand.mjs census.jsonl [gate ...]
import { readFileSync } from 'node:fs';
const rows = readFileSync(process.argv[2], 'utf8').trim().split('\n').map(JSON.parse);
const gates = process.argv.slice(3).map(Number);
const GATES = gates.length ? gates : [2, 3, 4];
const man = (a, b) => Math.abs(a.x - b.x) + Math.abs(a.y - b.y);

const prev = new Map();
const lunges = [];
for (const r of rows) {
  const el = new Map(r.elements.map((e) => [e.id, e.pos]));
  const ki = new Map(r.kitties.map((k) => [k.id, k.pos]));
  for (const k of r.kitties) {
    const p = prev.get(k.id);
    prev.set(k.id, k.pos);
    if (!p || k.last_action?.action !== 'chase') continue;
    if (man(p, k.pos) !== 2) continue; // the lunge signature, and only it
    const q = k.last_action.target === 'element' ? el.get(k.last_action.id) : ki.get(k.last_action.id);
    lunges.push({ id: k.id, name: k.name, tick: r.tick, d: q ? man(k.pos, q) : null });
  }
}
const h = {};
for (const l of lunges) h[l.d] = (h[l.d] || 0) + 1;
console.log(`ticks ${rows.length}; lunges (chase + two-tile step) ${lunges.length}`);
console.log(`quarry distance ON the lunge tick: ${Object.entries(h).sort((a, b) => a[0] - b[0]).map(([d, n]) => `${d}:${n}`).join(' ')}`);
for (const g of GATES) {
  // null keeps the pounce, so only a RESOLVED far quarry can strand a leap.
  const stranded = lunges.filter((l) => l.d !== null && l.d > g).length;
  console.log(`  gate ${g}: ${lunges.length - stranded}/${lunges.length} lunges drawn as pouncing; ${stranded} stranded (leaping while drawn walking)`);
}
const by = {};
for (const l of lunges) by[l.name ?? l.id] = (by[l.name ?? l.id] || 0) + 1;
console.log(`  by cat: ${Object.entries(by).sort((a, b) => b[1] - a[1]).map(([n, c]) => `${n} ${c}`).join(', ') || '(none)'}`);
