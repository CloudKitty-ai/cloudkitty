/**
 * Sample kitty positions from a LOCAL world, one line per tick.
 *
 *   target/debug/cloudkitty-server --config cloudkitty.toml \
 *     --client client --snapshot /tmp/w/snapshot.json --fresh
 *   node client-measurements/camera-aim/camera-sample.mjs 350 sample.jsonl
 *
 * A local world rather than the served one, deliberately: this question is
 * about the ROSTER SIZE the camera will face after the cutover, and
 * cloudkitty.toml already seats five. The served box is still on four.
 *
 * Positions only. Everything the camera decides is a pure function of where
 * the kitties are, so nothing else needs recording -- and a narrow sample is
 * one that stays readable when someone re-runs it in six weeks.
 */
import { appendFileSync, writeFileSync } from 'node:fs';
const WANT = Number(process.argv[2] || 350);
const OUT = process.argv[3];
if (!OUT) { console.error('usage: camera-sample.mjs <ticks> <out.jsonl>'); process.exit(1); }
writeFileSync(OUT, '');
let n = 0;
let lastTick = -1;
const ws = new WebSocket('ws://127.0.0.1:8090/ws');
ws.onmessage = (ev) => {
  let w;
  try { w = JSON.parse(ev.data); } catch { return; }
  if (!w || !Array.isArray(w.kitties) || w.tick === lastTick) return;
  lastTick = w.tick;
  appendFileSync(OUT, `${JSON.stringify({
    tick: w.tick,
    kitties: w.kitties.map((k) => ({ id: k.id, x: k.pos.x, y: k.pos.y })),
  })}\n`);
  n += 1;
  if (n % 50 === 0) process.stderr.write(`  ${n}/${WANT}\n`);
  if (n >= WANT) { console.log(`captured ${n} ticks`); ws.close(); process.exit(0); }
};
ws.onerror = () => { console.error('no world on 127.0.0.1:8090 -- start the server first'); process.exit(1); };
