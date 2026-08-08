// Sample the live served world and append one JSON line per distinct tick.
// Read-only: GET /world only. Usage: node pose-census.mjs <seconds> <outfile>
import { appendFileSync } from 'node:fs';

const seconds = Number(process.argv[2] ?? 480);
const out = process.argv[3] ?? 'census.jsonl';
const URL = 'https://kitties.ai/world';

const seen = new Set();
const until = Date.now() + seconds * 1000;
let polls = 0;
let fails = 0;

while (Date.now() < until) {
  try {
    const r = await fetch(URL, { signal: AbortSignal.timeout(5000) });
    const w = await r.json();
    polls++;
    if (!seen.has(w.tick)) {
      seen.add(w.tick);
      appendFileSync(
        out,
        JSON.stringify({
          tick: w.tick,
          kitties: w.kitties.map((k) => ({
            id: k.id,
            name: k.name,
            pos: k.pos,
            state: k.activity?.state ?? null,
            last_action: k.last_action ?? null,
          })),
          elements: w.elements.map((e) => ({ id: e.id, kind: e.kind, pos: e.pos })),
        }) + '\n',
      );
    }
  } catch {
    fails++;
  }
  await new Promise((r) => setTimeout(r, 380));
}

console.log(`ticks=${seen.size} polls=${polls} fails=${fails}`);
