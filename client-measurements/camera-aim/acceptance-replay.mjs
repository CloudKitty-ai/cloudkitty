// Drive the REAL Camera over a recorded capture; report against the 038 SCs.
// Extends scratchpad/acceptance-replay.mjs (T025/T026) with the two calm
// stats the dial pass reported -- fully-still ticks and calm-spell length --
// so a re-run is comparable line for line. Every pre-existing formula is
// carried over UNCHANGED, including sizeVsPinned's (20/1.5) numerator.
import { readFileSync } from 'node:fs';
const src = ['cat.js','cat-v2.js','props.js','meadow.js','render.js','anim.js']
  .map((f) => readFileSync(`client/${f}`, 'utf8')).join('\n');
const { Camera } = new Function(`${src}\n; return { Camera };`)();
const rows = readFileSync(process.argv[2], 'utf8').trim().split('\n').map(JSON.parse);
const cssWidth = Number(process.argv[3] || 1000);

const cam = new Camera();
cam.on = true;
const mins = (rows.length * 0.8) / 60;
let clock = 0; let still = 0; let frames = 0; let prev = null; let lastKind = null;
const events = { correction: 0, widen: 0, shed: 0, break: 0, pan: 0 };
let twoPlus = 0; let zero = 0; let zeroDuringPan = 0; let atCeil = 0; let maximal = 0;
let framedSum = 0; const widths = [];
let tickStill = 0; const spells = []; let spell = 0;
const probe = new Camera(); probe.on = true;
const W = rows[0].width || 20; const H = rows[0].height || 20;

for (const r of rows) {
  const world = { width: W, height: H, tick: r.tick, elements: [],
    kitties: r.kitties.map((k) => ({ id: k.id, pos: { x: k.x, y: k.y } })) };
  let movedThisTick = false;
  for (let f = 0; f < 8; f += 1) {
    clock += 100;
    cam.update(world, { still: false, ambient: { now: clock } }, { aspect: 1, cssWidth });
    const kind = cam.episode ? cam.episode.kind : null;
    if (kind !== lastKind && kind !== null) events[kind] += 1;
    const inPan = kind === 'pan';
    lastKind = kind;
    const pose = `${cam.left},${cam.top},${cam.across},${cam.aimX},${cam.aimY}`;
    if (prev !== null) {
      frames += 1;
      // A "still" frame is one where nothing about the frame moved; a calm
      // SPELL is a run of them, measured in the 100ms the frame occupies.
      if (pose === prev) { still += 1; spell += 1; }
      else { movedThisTick = true; if (spell) spells.push(spell); spell = 0; }
    }
    prev = pose;
    const inFrame = world.kitties.filter((k) => {
      const x = k.pos.x + 0.5; const y = k.pos.y + 0.5;
      return x >= cam.left && x <= cam.left + cam.across
        && y >= cam.top && y <= cam.top + cam.across;
    }).length;
    if (inFrame === 0) { zero += 1; if (inPan) zeroDuringPan += 1; }
  }
  if (!movedThisTick) tickStill += 1;
  const { ceilingTiles } = cam.limitsFor(world, cssWidth, 1);
  widths.push(cam.across);
  if (cam.across >= ceilingTiles - 1e-6) atCeil += 1;
  framedSum += cam.shotIds.size;
  if (cam.shotIds.size >= 2) twoPlus += 1;
  const at = (k) => ({ x: k.pos.x + 0.5, y: k.pos.y + 0.5 });
  const best = probe.bestWindowFor(probe.groupsFor(world.kitties, at), at, 1, ceilingTiles);
  if (cam.shotIds.size >= best.length) maximal += 1;
}
if (spell) spells.push(spell);
const med = (a) => { const s = [...a].sort((x, y) => x - y); return s.length ? s[Math.floor(s.length / 2)] : 0; };
const sorted = [...widths].sort((a, b) => a - b);
const median = sorted[Math.floor(sorted.length / 2)];
const perMin = (n) => Number((n / mins).toFixed(2));
console.log(JSON.stringify({
  cssWidth, ticks: rows.length, mins: Number(mins.toFixed(1)),
  restPct: Math.round((100 * still) / frames),
  ticksFullyStillPct: Math.round((100 * tickStill) / rows.length),
  calmSpellMedianS: Number((med(spells) * 0.1).toFixed(1)),
  calmSpellLongestS: Number((Math.max(0, ...spells) * 0.1).toFixed(1)),
  eventsPerMin: {
    corrections: perMin(events.correction), widens: perMin(events.widen),
    sheds: perMin(events.shed), breaks: perMin(events.break), pans: perMin(events.pan),
    reframingTotal: perMin(events.widen + events.shed + events.break + events.pan),
  },
  twoPlusPct: Math.round((100 * twoPlus) / rows.length),
  zeroKittyFrames: zero, zeroDuringPan,
  atCeilPct: Math.round((100 * atCeil) / rows.length),
  medianWidth: Number(median.toFixed(2)),
  sizeVsPinned: Number(((20 / 1.5) / median).toFixed(2)),
  meanFramed: Number((framedSum / rows.length).toFixed(2)),
  maximalOrTiedPct: Math.round((100 * maximal) / rows.length),
}, null, 1));
