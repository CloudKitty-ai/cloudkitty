// The client's own pose rule, loaded from the shipped source.
//
// Owner call #362, ruled option B on 2026-09-08: "Ruled: B".
//
// This directory's convention is that a tool modelling a change to shipped
// code replays the shipped function verbatim beside the modelled variant. For
// six weeks pose-analyze.mjs did that with a hand-copy, and the copy drifted:
// `ACTION_POSE` entered render.js on 2026-08-13 and `grooming-other` on
// 2026-08-22, and by 2026-09-08 the column the tool labelled SHIPPED
// disagreed with the client on 23.1% of the kitty-ticks in
// census-2026-08-23.jsonl and 20.9% in meow2.jsonl.
//
// A convention telling you to keep a copy in step is not a guard. So there is
// no copy: `meow-analyze.mjs` already evals the shipped scripts and calls the
// real `poseFor`, and this is that approach lifted out so pose-analyze can
// use it too.
//
// The gate sweep survives without a second implementation. `poseFor` takes
// its dials as an argument, so a candidate gate is `dialsWithGate(n)` rather
// than a reimplementation of the rule with `n` substituted into it.
import { readFileSync } from 'node:fs';

const D = new URL('../../client/', import.meta.url).pathname;
const read = (f) => readFileSync(D + f, 'utf8');

// render.js's pose logic reaches into constants declared by the other three,
// so all four are evaluated into one scope, exactly as meow-analyze.mjs does.
const api = eval(read('anim.js') + ';({ VIEW })');
const shipped = eval(
  [read('cat.js'), read('props.js'), read('meadow.js'), read('render.js')].join('\n')
  + ';({ poseFor, chaseDistanceFor })',
);

export const VIEW = api.VIEW;
export const poseFor = shipped.poseFor;
export const chaseDistanceFor = shipped.chaseDistanceFor;

/** The shipped dials with the chase gate moved, for the counterfactual columns. */
export const dialsWithGate = (pounceGateTiles) => ({ ...VIEW, pounceGateTiles });

/**
 * The two-tile step spec 039 serves as the final pounce, derived the way the
 * client derives it (`Presentation.leapFor`, anim.js:1741): a chase whose
 * served position moved exactly two tiles since the previous tick. It
 * outranks the distance gate, so a replay that cannot see it under-counts
 * pouncing.
 */
export const lungedBetween = (was, is) =>
  is.last_action?.action === 'chase' &&
  Math.abs(is.pos.x - was.x) + Math.abs(is.pos.y - was.y) === 2;
