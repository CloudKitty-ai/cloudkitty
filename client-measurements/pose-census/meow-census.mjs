// Sample the live served world for MEOWS beside poses, one JSON line per
// distinct tick. Read-only: GET /world only.
// Usage: node meow-census.mjs <seconds> <outfile>
//
// A sibling of pose-census.mjs rather than a field added to it, because it
// needs `recent_meows` and that tool's records are already banked without it.
//
// WHY recent_meows AND NOT `last_action.action === 'meow'`: the meow left the
// activity menu in spec 028. `action::validate` now rejects a Meow proposal
// outright -- "the message channel (`Decision.message`) is the only way to
// speak" -- and a stray one resolves to Idle. So a meow is NOT a tick's
// action; it rides ALONGSIDE whatever the cat did, and a cat can act and
// speak in the same tick. Counting the action would have measured a legacy
// path that can never fire.
//
// `purr` is carried but flagged: the client draws a purr as a glyph, never a
// bubble, so it is not speech for our purposes.
import { appendFileSync } from 'node:fs';

const seconds = Number(process.argv[2] || 300);
const out = process.argv[3] || 'meow-census.jsonl';
const HOST = process.env.CK_HOST || 'https://kitties.ai';

const seen = new Set();
let polls = 0;
let fails = 0;
const until = Date.now() + seconds * 1000;

while (Date.now() < until) {
  try {
    const w = await (await fetch(`${HOST}/world`)).json();
    polls += 1;
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
          // The whole window as served; dedupe by (kitty_id, tick, kind) at
          // analysis time, since a meow stays in the window for several polls.
          recent_meows: w.recent_meows ?? [],
        }) + '\n',
      );
    }
  } catch {
    fails += 1;
  }
  await new Promise((r) => setTimeout(r, 380));
}
console.log(`ticks=${seen.size} polls=${polls} fails=${fails}`);
