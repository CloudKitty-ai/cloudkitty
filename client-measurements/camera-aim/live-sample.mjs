/**
 * Sample kitty positions from the SERVED world, one line per tick.
 * Same shape as client-measurements/camera-aim/camera-sample.mjs, but
 * pointed at the running deployment rather than a local --fresh world:
 * the question is what the camera does on the generation the owner is
 * actually watching, with Biscuit 2.0 seated.
 */
import { appendFileSync, writeFileSync } from 'node:fs';
const WANT = Number(process.argv[2] || 350);
const OUT = process.argv[3];
const URL = process.argv[4] || 'wss://kitties.ai/ws';
writeFileSync(OUT, '');
let n = 0;
let lastTick = -1;
const t0 = Date.now();
const ws = new WebSocket(URL);
ws.onopen = () => process.stderr.write(`connected ${URL}\n`);
ws.onmessage = (ev) => {
  let w;
  try { w = JSON.parse(ev.data); } catch { return; }
  if (!w || !Array.isArray(w.kitties) || w.tick === lastTick) return;
  lastTick = w.tick;
  appendFileSync(OUT, `${JSON.stringify({
    tick: w.tick,
    width: w.width, height: w.height,
    kitties: w.kitties.map((k) => ({
      id: k.id, x: k.pos.x, y: k.pos.y,
      action: k.last_action?.action ?? null,
    })),
  })}\n`);
  n += 1;
  if (n % 50 === 0) process.stderr.write(`  ${n}/${WANT}  (${((Date.now()-t0)/1000).toFixed(0)}s)\n`);
  if (n >= WANT) { console.log(`captured ${n} ticks from ${URL}`); ws.close(); process.exit(0); }
};
ws.onerror = (e) => { console.error('capture failed:', e.message || e); process.exit(1); };
