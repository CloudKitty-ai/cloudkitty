#!/usr/bin/env node
/**
 * Photograph two builds of the client through one time-of-day crossing and
 * measure how far apart they are, pixel by pixel.
 *
 *     node client-measurements/crossing-shots/run.mjs <baseline-root> <change-root> [out-dir]
 *
 * Each root is a worktree root (the directory holding `client/`). Both are
 * served with NO probe injection -- the shipped page, the shipped renderer --
 * from `crossing-probe/world.json` + `config.json`, so the two sides see the
 * same world and the only difference is the code. Prints one row per tick:
 * mean channel delta, worst channel delta, and the share of pixels moving
 * more than 2/255.
 *
 * It exists because the cross-fade (CROSSING-BAKES.md section 6) replaces a
 * per-step rebake with two baked layers blended per frame, and the argument
 * that this is visually equivalent is arithmetic -- `bake(mix(A,B,t))` ==
 * `mix(bake(A),bake(B),t)` -- which is worth exactly nothing until something
 * photographs it. Section 9 carries what it measured.
 *
 * THE TRAP THIS RIG IS BUILT AROUND: the app drives its own clock. Setting
 * `latestWorld.tick` and waiting does not pin it -- the render loop
 * reschedules at the bottom of every frame and walks the tick back under
 * you. Cancelling the pending frame is not enough either. The scheduler
 * itself has to be stubbed FIRST, and only then is the tick ours. Two full
 * capture runs were invalid before that landed, and both looked plausible:
 * the shots came out, they just weren't of the ticks they were named after.
 * A delay is a guess about frame time, and here frame time IS the subject.
 *
 * So this rig never trusts a delay to establish app state. It asserts the
 * blend it asked for, and it refuses to report a side whose frames came back
 * identical to each other -- which is what a silently-unpinned clock looks
 * like from the outside. The residual settle below is for the compositor
 * presenting a frame, nothing more.
 */
import { spawn } from 'node:child_process';
import http from 'node:http';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { createHash } from 'node:crypto';

const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
// day -> dusk, sampled to the END of the fade. 256 is the fade's first tick
// (step 0, both builds drawing the same settled hour); 262/266/272 are
// 0.25/0.42/0.67; 279 is 0.958; 279.99 is step 1; 280 is settled dusk, the
// frame a step-1 frame snaps to. The day row quantises to 192 steps, so
// `Math.round(k * 192) / 192` reaches exactly 1 once `k >= 1 - 1/384` -- the
// last ~60ms of every crossing.
//
// Sampling to the end matters, but NOT because the divergence grows to step 1.
// Measured 2026-09-21 (mean channel delta / share of meadow pixels over
// 2/255): 0.25 -> 1.30/6.4%, 0.42 -> 1.19/5.4%, 0.67 -> 1.42/6.6%,
// 0.958 -> 1.46/10.8%, 1 -> 1.18/7.6%, against a 0.54-0.56/0.5% noise floor
// read off the two settled rows. It peaks just BEFORE step 1 and falls back.
//
// Two predictions died here and both are worth keeping. An earlier version of
// this file claimed mid-fade was "the only place a cross-fade can differ from
// a per-step rebake at all" and stopped at 0.67 -- which is why the first
// capture run reported the cross-fade exact while shipping a defect. Its
// replacement claimed the opposite, that divergence is monotone to step 1.
// Also wrong. The two hours' detail scatters are DETERMINISTIC and land on the
// same tiles, so the far hour's ink stacks on the near hour's rather than
// beside it; at alpha 1 it covers that ink most completely, and just under 1
// it covers it least. The extra ink is widest where the far layer is nearly,
// but not quite, opaque.
//
// So the mean is a poor instrument here and the share-over-JND is better --
// but the load-bearing read is BOUNDARY_PAIR below, which is exact.
//
// Fractional ticks are legal. applyTheme feeds `latestWorld.tick + subTick` to
// phaseBlendFor, so the clock the blend reads is continuous and 279.99 is a
// moment the running app passes through on every crossing.
const TICKS = [256, 262, 266, 272, 279, 279.99, 280];
// The last frame of a crossing and the first frame of the next hour are the
// SAME PICTURE when the blend is right: at step 1 the lerp is pure dusk, and
// the frame after the boundary is settled dusk. A build where those two
// differ POPS once per crossing. So this one pair is allowed to collide --
// whether it does is a RESULT this rig reports, not an error it raises.
// Every other pair colliding still means a page that stopped repainting, and
// a dead page collides at t262 long before it reaches here.
const BOUNDARY_PAIR = [279.99, 280];
// How far apart those two frames may be, as a share of the compared pixels
// moving more than the 2/255 this file already treats as the JND.
//
// NOT byte-identity, though the per-step-rebake baseline does achieve it.
// The baseline bakes one layer per step and never has to isolate anything;
// a cross-fade of TRANSPARENT layers has to composite the pair on its own
// surface first, and that intermediate is 8-bit premultiplied, so it costs
// about one LSB. Demanding bit-equality of the fixed renderer would only
// force an `if (step === 1) drawTheFarHour()` special case -- which would
// make this very check tautological.
//
// Measured on the day->dusk boundary, 1,642,230 pixels compared
// (2026-09-21): the two-blit source-over moved 96,180 of them past the JND,
// max 66. The isolated lerp moves 12, max 10, with 21,657 of its 21,676
// differing pixels off by exactly 1. The bar below sits ~8,000x from one and
// ~13x from the other, so it is nowhere near either edge.
const BOUNDARY_MAX_SHARE = 0.0001;
const PRESENT_MS = 400; // compositor only; see the docblock.
const HERE = path.dirname(new URL(import.meta.url).pathname);

const [, , baseRoot, changeRoot, outArg] = process.argv;
if (!baseRoot || !changeRoot) {
  console.error('usage: run.mjs <baseline-root> <change-root> [out-dir]');
  process.exit(1);
}
const OUT = outArg || fs.mkdtempSync(path.join(os.tmpdir(), 'crossing-shots-'));
fs.mkdirSync(OUT, { recursive: true });

const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png', '.woff2': 'font/woff2' };
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/** The shipped client, plus the captured world it would have fetched. */
function serveClient(root) {
  const client = path.join(root, 'client');
  const cap = path.join(root, 'client-measurements', 'crossing-probe');
  for (const f of ['world.json', 'config.json']) {
    if (!fs.existsSync(path.join(cap, f))) {
      throw new Error(`${root} has no crossing-probe/${f} -- is it a worktree root at or after the probe merge (9b06c4f)?`);
    }
  }
  return listen((req, res) => {
    const u = req.url.split('?')[0];
    if (u === '/world' || u === '/config') {
      res.writeHead(200, { 'content-type': 'application/json' });
      return res.end(fs.readFileSync(path.join(cap, `${u.slice(1)}.json`)));
    }
    const f = u === '/' ? '/index.html' : u;
    const full = path.join(client, f);
    if (!fs.existsSync(full)) { res.writeHead(404); return res.end('no'); }
    res.writeHead(200, { 'content-type': MIME[path.extname(f)] || 'application/octet-stream' });
    res.end(fs.readFileSync(full));
  });
}

/** The shots, and the page that subtracts them. */
function serveShots() {
  return listen((req, res) => {
    const u = req.url.split('?')[0];
    const full = u === '/compare.html' ? path.join(HERE, 'compare.html') : path.join(OUT, u);
    if (!fs.existsSync(full)) { res.writeHead(404); return res.end('no'); }
    res.writeHead(200, { 'content-type': MIME[path.extname(full)] || 'application/octet-stream' });
    res.end(fs.readFileSync(full));
  });
}

function listen(handler) {
  const s = http.createServer(handler);
  return new Promise((r) => s.listen(0, '127.0.0.1', () => r({ port: s.address().port, close: () => s.close() })));
}

/** Headless Chrome on a throwaway profile, letting Chrome pick its own port. */
async function chrome(extraArgs = []) {
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'crossing-shots-chrome-'));
  const proc = spawn(CHROME, ['--headless=new', '--remote-debugging-port=0', '--no-first-run',
    `--user-data-dir=${profile}`, ...extraArgs, 'about:blank'], { stdio: 'ignore' });
  const portFile = path.join(profile, 'DevToolsActivePort');
  let port = null;
  for (let i = 0; i < 40 && port === null; i++) {
    await sleep(250);
    try { port = Number(fs.readFileSync(portFile, 'utf8').split('\n')[0]); } catch {}
  }
  if (!port) { proc.kill(); throw new Error('Chrome never reported a debugging port'); }

  let ws = null;
  for (let i = 0; i < 40 && !ws; i++) {
    await sleep(250);
    try {
      const list = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
      const page = list.find((t) => t.type === 'page');
      if (!page) continue;
      const sock = new WebSocket(page.webSocketDebuggerUrl);
      await new Promise((res, rej) => { sock.onopen = res; sock.onerror = rej; });
      ws = sock;
    } catch {}
  }
  if (!ws) { proc.kill(); throw new Error('Chrome never opened a debuggable page'); }

  let id = 0;
  const pending = new Map();
  ws.onmessage = (e) => {
    const m = JSON.parse(e.data);
    const p = pending.get(m.id);
    if (p) { pending.delete(m.id); p(m); }
  };
  const send = (method, params) => new Promise((res) => {
    const n = ++id;
    pending.set(n, res);
    ws.send(JSON.stringify({ id: n, method, params }));
  });
  const ev = async (expression) =>
    (await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true })).result?.result?.value;
  await send('Page.enable');
  return { send, ev, close: () => { ws.close(); proc.kill(); } };
}

async function capture(root, tag) {
  const server = await serveClient(root);
  // dpr 2: the bake is capped in DEVICE pixels, so a dpr-1 shot would compare
  // a upscale path neither phone nor laptop actually walks.
  const cdp = await chrome(['--window-size=900,900', '--force-device-scale-factor=2']);
  try {
    await cdp.send('Page.navigate', { url: `http://127.0.0.1:${server.port}/` });
    let booted = false;
    for (let i = 0; i < 60 && !booted; i++) {
      await sleep(250);
      booted = await cdp.ev('typeof renderer !== "undefined" && !!latestWorld');
    }
    if (!booted) throw new Error(`${tag}: client never booted`);

    // Stub the scheduler BEFORE touching the tick. See the docblock.
    await cdp.ev('(() => { window.requestAnimationFrame = () => 0; if (typeof anim !== "undefined" && anim && anim.rafId) { cancelAnimationFrame(anim.rafId); anim.rafId = 0; } return true; })()');
    await sleep(PRESENT_MS);

    const digests = new Map();
    const byTick = new Map();
    for (const tick of TICKS) {
      const blend = await cdp.ev(`(() => { latestWorld.tick = ${tick}; applyTheme(0, true); return JSON.stringify(currentBlend); })()`);
      if (!blend) throw new Error(`${tag} t${tick}: applyTheme returned no blend -- the clock stub or the world shape moved`);
      await sleep(PRESENT_MS);
      // THE guard. If the scheduler stub did not take, the app's own clock
      // walks the tick back during the settle and the shot is of some other
      // moment entirely -- which is exactly how two earlier capture runs
      // produced plausible, wrong images. Re-read rather than trust.
      const held = await cdp.ev(`latestWorld.tick + '|' + JSON.stringify(currentBlend)`);
      if (held !== `${tick}|${blend}`) {
        throw new Error(`${tag} t${tick}: the clock moved during the settle (${held} != ${tick}|${blend}). The app is still driving itself; these shots are not of the ticks they are named after.`);
      }
      const shot = await cdp.send('Page.captureScreenshot', { format: 'png' });
      const data = shot.result?.result?.data ?? shot.result?.data;
      if (!data) throw new Error(`${tag} t${tick}: no screenshot came back`);
      const png = Buffer.from(data, 'base64');
      fs.writeFileSync(path.join(OUT, `${tag}-t${tick}.png`), png);
      const digest = createHash('sha256').update(png).digest('hex');
      byTick.set(tick, digest);
      const twin = digests.get(digest);
      if (twin !== undefined && !(BOUNDARY_PAIR.includes(tick) && BOUNDARY_PAIR.includes(twin))) {
        // Not the clock -- the guard above owns that. This is the page not
        // repainting between ticks at all.
        throw new Error(`${tag}: t${tick} is byte-identical to t${twin}. The page is not repainting. Do NOT read these numbers.`);
      }
      digests.set(digest, tick);
      console.log(`  ${tag} t${tick}  blend ${blend}`);
    }
    const [a, b] = BOUNDARY_PAIR;
    return byTick.get(a) === byTick.get(b);
    // (byte-identity, reported alongside the pixel read -- see the verdict)
  } finally {
    cdp.close();
    server.close();
  }
}

async function compare() {
  const server = await serveShots();
  const cdp = await chrome();
  try {
    await cdp.send('Page.navigate', { url: `http://127.0.0.1:${server.port}/compare.html` });
    for (let i = 0; i < 40; i++) {
      await sleep(250);
      if (await cdp.ev('typeof run === "function"')) break;
    }
    const rows = [];
    for (const tick of TICKS) {
      const raw = await cdp.ev(`run('/base-t${tick}.png','/change-t${tick}.png')`);
      if (!raw) throw new Error(`t${tick}: the diff page returned nothing`);
      rows.push({ tick, ...JSON.parse(raw) });
    }
    // The boundary pair, WITHIN each build: does its last crossing frame
    // match the settled hour it is about to become?
    const [a, b] = BOUNDARY_PAIR;
    const boundary = {};
    for (const tag of ['base', 'change']) {
      const raw = await cdp.ev(`run('/${tag}-t${a}.png','/${tag}-t${b}.png')`);
      if (!raw) throw new Error(`${tag} boundary: the diff page returned nothing`);
      boundary[tag] = JSON.parse(raw);
    }
    return { rows, boundary };
  } finally {
    cdp.close();
    server.close();
  }
}

console.log(`shots -> ${OUT}`);
const baseHeld = await capture(baseRoot, 'base');
const changeHeld = await capture(changeRoot, 'change');
const { rows, boundary } = await compare();
console.log('\n tick | mean d | max d | % over 2/255');
console.log('------+--------+-------+-------------');
for (const r of rows) {
  console.log(` ${String(r.tick).padStart(4)} | ${String(r.mean).padStart(6)} | ${String(r.max).padStart(5)} | ${String(r.pctOver2).padStart(11)}`);
}
console.log('\nRows 256 and 280 are settled hours -- the two builds drawing the same');
console.log('thing -- so both should sit near zero. The rest are inside the fade. A mean');
console.log('under ~2/255 is below a just-noticeable difference even though isolated');
console.log('pixels at detail edges move much further, and the two settled rows are');
console.log('this rig\'s own noise floor -- read every fade row against those, not zero.');
console.log('The fade rows peak just BEFORE step 1, not at it (see the TICKS note), so');
console.log('no single row bounds the others. The boundary verdict below is the exact');
console.log('read and the one to trust.');
console.log(`\nPhase boundary -- t${BOUNDARY_PAIR[0]} (step 1) against t${BOUNDARY_PAIR[1]} (settled),`);
console.log('WITHIN each build. This is the exact read and the one to trust: a build');
console.log('whose last crossing frame is not the hour it becomes POPS, once a crossing.');
const say = (tag, r, byteSame) => {
  const share = r.overJND / r.n;
  const held = share <= BOUNDARY_MAX_SHARE;
  console.log(`  ${tag.padEnd(9)} ${held ? 'HOLDS' : 'POPS '}  ${r.overJND} of ${r.n} px over the JND` +
    ` (${(100 * share).toFixed(4)}%, bar ${(100 * BOUNDARY_MAX_SHARE).toFixed(2)}%), max ${r.max}` +
    `${byteSame ? ', byte-identical' : ''}`);
  return held;
};
say('baseline', boundary.base, baseHeld);
const ok = say('change', boundary.change, changeHeld);
if (!ok) process.exitCode = 1;
