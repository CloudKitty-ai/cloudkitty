// `last_action` and `activity.state` do NOT measure the same thing, and the
// ratio between them is not evidence of over-drawing.
//
// For play, eat and drink the state is a ONE-TICK resolution flag while the
// action spans the whole multi-tick engagement, so action/state lands near
// the action's run length (~2x) for all three. Only groom and sleep have
// genuine multi-tick states. Read this before calling any "the drawn pose
// runs Nx the budget" number an amplification.
//
// Usage: node scene-vs-action.mjs census.jsonl
import { readFileSync } from 'node:fs';
const rows = readFileSync(process.argv[2], 'utf8').trim().split('\n').map(JSON.parse);
const PAIRS = [['play', 'playing'], ['eat', 'eating'], ['drink', 'drinking'], ['groom', 'grooming'], ['sleep', 'sleeping']];

const runsOf = (pick) => {
  const out = {}; const last = new Map();
  for (const r of rows) for (const k of r.kitties) {
    const v = pick(k); const L = last.get(k.id);
    if (L && L.v === v) L.n++;
    else { if (L) (out[L.v] ||= []).push(L.n); last.set(k.id, { v, n: 1 }); }
  }
  for (const [, L] of last) (out[L.v] ||= []).push(L.n);
  return out;
};
const A = runsOf((k) => k.last_action?.action ?? null);
const S = runsOf((k) => k.state ?? null);
const sum = (a) => (a || []).reduce((x, y) => x + y, 0);

console.log('action        action-ticks  state-ticks   ratio   state-runs  ticks/state-run');
for (const [a, s] of PAIRS) {
  const at = sum(A[a]), st = sum(S[s]), sr = (S[s] || []).length;
  console.log(`  ${a.padEnd(12)} ${String(at).padStart(6)}       ${String(st).padStart(6)}     ${(at / st).toFixed(2)}x     ${String(sr).padStart(6)}       ${(st / sr).toFixed(2)}`);
}
