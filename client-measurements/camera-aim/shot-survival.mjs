/**
 * What would the SETTLED camera grammar do to this sample?
 *
 *   node client-measurements/camera-aim/shot-survival.mjs sample.jsonl
 *
 * Follow-up to camera-analyze.mjs, after the 2026-08-20 design session
 * settled the shot-picker grammar:
 *
 *   - the shot is the maximal-count set of groups that fits the width bounds
 *   - a NEAR rival (union fits at ceiling) is ADMITTED by widening, never
 *     switched to -- the owner's convergence/cross-pollination call
 *   - a FAR rival must be STRICTLY bigger than the whole frame, sustained
 *     ("numbers will always win out in interest over 15+ ticks"), and forces
 *     the only true transition: a fast pan
 *   - ties keep the incumbent; activity never enters
 *
 * Two passes:
 *   1. descriptive -- how long does the biggest group keep its identity?
 *   2. policy simulation -- widen / pan / break rates under the grammar,
 *      plus the far-superiority run lengths that tell us (a) whether the
 *      15-tick bar filters noise and (b) what a spec-032 lookahead buffer
 *      would buy (each pan fires DWELL_FAR ticks late without it).
 *
 * Dials here are stated assumptions, not shipped values. The dwell counters
 * are keyed on exact member sets, so membership churn resets them -- a
 * conservative model that undercounts transitions if groups churn members
 * while staying put.
 */
import { readFileSync } from 'node:fs';

const MARGIN = 2.6;    // VIEW.camera.fitMarginTiles, per side
const FLOOR = 7;       // minTiles
const TICK_MS = 800;
const DWELL_NEAR = 5;  // ticks a near group must persist before the widen
const DWELL_FAR = 15;  // the owner's number, 2026-08-20
const CEILINGS = { desktop: 13.33, phone: 7.6 };

const ticks = readFileSync(process.argv[2] || 'sample.jsonl', 'utf8')
  .trim().split('\n').map((l) => JSON.parse(l));
const mins = (ticks.length * TICK_MS) / 60000;

const dist = (a, b) => Math.hypot(a.x - b.x, a.y - b.y);
const centroid = (p) => ({ x: p.reduce((s, q) => s + q.x, 0) / p.length, y: p.reduce((s, q) => s + q.y, 0) / p.length });
const span = (p) => {
  const xs = p.map((q) => q.x); const ys = p.map((q) => q.y);
  return Math.max(Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys));
};
const fitW = (p) => span(p) + 2 * MARGIN;
const stats = (d) => {
  if (!d.length) return { median: 0, p90: 0, mean: 0 };
  const s = [...d].sort((a, b) => a - b);
  return { median: s[Math.floor(s.length / 2)], p90: s[Math.floor(s.length * 0.9)], mean: d.reduce((a, b) => a + b, 0) / d.length };
};

/** Connected components under link distance L. */
function components(ks, L) {
  const comps = []; const seen = new Set();
  for (const k of ks) {
    if (seen.has(k.id)) continue;
    const comp = [k]; seen.add(k.id);
    for (let i = 0; i < comp.length; i += 1) {
      for (const o of ks) {
        if (!seen.has(o.id) && dist(comp[i], o) <= L) { seen.add(o.id); comp.push(o); }
      }
    }
    comps.push(comp);
  }
  return comps;
}

/** Greedy maximal-count union of components that fits the ceiling. The seed
 *  component is always admitted whole even when it alone overflows (the
 *  camera clamps and frames it partially -- reality, not an error). Ties on
 *  count go to overlap with `pref` (incumbency), then first seed. */
function bestUnion(comps, ceiling, pref = new Set()) {
  let best = null;
  for (let i = 0; i < comps.length; i += 1) {
    const cats = [...comps[i]];
    const rest = comps.filter((_, j) => j !== i);
    let grew = true;
    while (grew) {
      grew = false;
      let pick = -1; let ps = null;
      for (let j = 0; j < rest.length; j += 1) {
        if (fitW([...cats, ...rest[j]]) <= ceiling) {
          const s = [rest[j].length, -dist(centroid(cats), centroid(rest[j]))];
          if (pick < 0 || s[0] > ps[0] || (s[0] === ps[0] && s[1] > ps[1])) { pick = j; ps = s; }
        }
      }
      if (pick >= 0) { cats.push(...rest[pick]); rest.splice(pick, 1); grew = true; }
    }
    const ov = cats.filter((k) => pref.has(k.id)).length;
    if (!best || cats.length > best.cats.length || (cats.length === best.cats.length && ov > best.ov)) best = { cats, ov };
  }
  return best ? best.cats : [];
}

/** Pass 1: identity survival of the biggest group (majority member overlap
 *  chains it across ticks; ties on size prefer the incumbent chain). */
function survival(L) {
  const runs = []; let prev = null; let run = 0; let sizeSum = 0;
  for (const t of ticks) {
    const comps = components(t.kitties, L);
    let top = null;
    for (const c of comps) {
      const ov = prev ? c.filter((k) => prev.has(k.id)).length : 0;
      if (!top || c.length > top.c.length || (c.length === top.c.length && ov > top.ov)) top = { c, ov };
    }
    const set = new Set(top.c.map((k) => k.id));
    if (prev && top.ov * 2 >= Math.max(set.size, prev.size)) run += 1;
    else { if (run) runs.push(run); run = 1; }
    prev = set; sizeSum += set.size;
  }
  runs.push(run);
  return { runs, meanSize: sizeSum / ticks.length };
}

/** Pass 2: run the grammar. */
function simulate(L, ceiling) {
  let S = null;                      // ids in the current shot
  let counters = new Map();          // 'n:'|'f:' + member-set signature -> ticks seen
  let pans = 0; let widens = 0; let breaks = 0; let jumpBreaks = 0;
  let framedSum = 0; let twoPlus = 0; let atCeil = 0; let overflow = 0;
  const widths = []; const segLens = []; let seg = 0;
  const superRuns = [];              // far-superiority episode lengths (15 = censored: pan fired)

  for (const t of ticks) {
    const ks = t.kitties;
    const byId = new Map(ks.map((k) => [k.id, k]));
    const catsOf = (set) => [...set].map((id) => byId.get(id));
    const comps = components(ks, L);

    if (!S) {
      S = new Set(bestUnion(comps, ceiling).map((k) => k.id));
    } else {
      // membership: follow every component that still holds a shot member;
      // shed (count-first, incumbency tiebreak) when the union no longer fits
      const touching = comps.filter((c) => c.some((k) => S.has(k.id)));
      const all = touching.flat();
      S = new Set((fitW(all) <= ceiling ? all : bestUnion(touching, ceiling, S)).map((k) => k.id));
    }

    if (S.size < 2) {               // the shot broke: re-pick the best window
      breaks += 1;
      const from = centroid(catsOf(S));
      let next = bestUnion(comps, ceiling);
      if (next.length < 2) {        // no pair anywhere within L: closest pair, framed partially
        let pair = null;
        for (const a of ks) for (const b of ks) {
          if (a.id < b.id && (!pair || dist(a, b) < dist(pair[0], pair[1]))) pair = [a, b];
        }
        next = pair;
      }
      if (dist(from, centroid(next)) > ceiling / 2) { jumpBreaks += 1; segLens.push(seg); seg = 0; }
      S = new Set(next.map((k) => k.id));
      counters.clear();
    }

    // admission (near) and rivals (far)
    const seen = new Set();
    for (const c of comps) {
      if (c.some((k) => S.has(k.id))) continue;
      const sig = c.map((k) => k.id).sort((a, b) => a - b).join(',');
      if (fitW([...c, ...catsOf(S)]) <= ceiling) {
        const key = 'n:' + sig; seen.add(key);
        const n = (counters.get(key) || 0) + 1;
        if (n >= DWELL_NEAR) { for (const k of c) S.add(k.id); widens += 1; counters.delete(key); }
        else counters.set(key, n);
      } else if (c.length > S.size) {
        const key = 'f:' + sig; seen.add(key);
        const n = (counters.get(key) || 0) + 1;
        counters.set(key, n);
        if (n >= DWELL_FAR) {
          superRuns.push(n);
          S = new Set(c.map((k) => k.id)); pans += 1; segLens.push(seg); seg = 0;
          counters.clear();
          break;
        }
      }
    }
    for (const key of [...counters.keys()]) {
      if (!seen.has(key)) {
        if (key.startsWith('f:')) superRuns.push(counters.get(key));
        counters.delete(key);
      }
    }

    const cats = catsOf(S);
    const w = Math.min(Math.max(fitW(cats), FLOOR), ceiling);
    widths.push(w);
    if (w >= ceiling - 1e-9) atCeil += 1;
    if (fitW(cats) > ceiling + 1e-9) overflow += 1;
    framedSum += S.size; if (S.size >= 2) twoPlus += 1;
    seg += 1;
  }
  segLens.push(seg);

  const ws = stats(widths); const sl = stats(segLens.map((s) => (s * TICK_MS) / 1000));
  return {
    line: `pan ${(pans / mins).toFixed(2)}/min  widen ${(widens / mins).toFixed(2)}/min`
      + `  break ${(breaks / mins).toFixed(2)}/min (${jumpBreaks} jumps)`
      + `  shot median ${sl.median.toFixed(0)}s`
      + `  framed ${(framedSum / ticks.length).toFixed(2)} cats  >=2 ${(100 * twoPlus / ticks.length).toFixed(0)}%`
      + `  width med ${ws.median.toFixed(1)}t  ceil ${(100 * atCeil / ticks.length).toFixed(0)}%  overflow ${(100 * overflow / ticks.length).toFixed(0)}%`,
    superRuns,
  };
}

console.log(`${ticks.length} ticks (${mins.toFixed(1)} min), ${ticks[0].kitties.length} kitties\n`);
console.log('SURVIVAL of the biggest group\'s identity (majority-overlap chains)');
for (const L of [4, 5, 6]) {
  const { runs, meanSize } = survival(L);
  const s = stats(runs.map((r) => (r * TICK_MS) / 1000));
  console.log(`L=${L}  median ${s.median.toFixed(0)}s  p90 ${s.p90.toFixed(0)}s  mean ${s.mean.toFixed(0)}s`
    + `  (${runs.length} chains, mean top-group ${meanSize.toFixed(2)} cats)`);
}

for (const [name, ceiling] of Object.entries(CEILINGS)) {
  console.log(`\nPOLICY at the ${name} ceiling (${ceiling} tiles)`);
  for (const L of [4, 5, 6]) {
    const { line, superRuns } = simulate(L, ceiling);
    const reached = superRuns.filter((r) => r >= DWELL_FAR).length;
    console.log(`L=${L}  ${line}`);
    if (superRuns.length) {
      const fizzles = superRuns.filter((r) => r < DWELL_FAR);
      console.log(`      far-superiority episodes ${superRuns.length}: ${reached} reached ${DWELL_FAR} ticks (panned),`
        + ` fizzles ${fizzles.length ? `median ${stats(fizzles).median} ticks` : 'none'}`);
    }
  }
}
