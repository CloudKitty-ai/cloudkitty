/**
 * CloudKitty's cats, v2 vocabulary -- PROTOTYPE, not yet the shipped look.
 *
 * A fork of cat.js (which remains the live vocabulary) for the 2026-07
 * graphics investigation. Same art style, same palettes, same poses; what
 * changes is the face and the proportions:
 *
 *  - Kawaii proportions: every pose's head is ~1.05x its v1 radius. The
 *    body, patterns, tail and palette are untouched, so the cats stay
 *    recognizably themselves.
 *  - Cuter eyes: larger, repositionable (CatV2.EYE dials), and always
 *    fully drawn -- iris color, dark pupil -- at every size. v1 gated eye
 *    detail behind `fine` (>= 44px), which no live-world cat ever
 *    reached. The white glint was tried and cut (owner, 2026-07-29). The
 *    narrowed 'focused' hunting eyes are kept exactly as v1 drew them.
 *  - Face under live revision (owner, 2026-07-29): symmetric front-on
 *    nose near the eye midline; mouth is an upside-down V under the nose
 *    (the profile ω was tried and cut). No whiskers -- tried and cut.
 *
 * Everything lives in an IIFE so this file can share a page with cat.js:
 * the comparison gallery and index.html's v1/v2 toggle both load the two
 * side by side. When loaded WITHOUT cat.js, it claims the same global
 * names and works as a drop-in replacement.
 *
 * Pure drawing, as v1: no DOM beyond ctx, no fetches. Unit box 0..1,
 * y down; the base cat faces right and mirrors for left.
 */

(() => {

/**
 * Curated colorways (research R2): appearance is PALETTES[id % length], so a
 * kitty's look is stable across frames, sessions and restarts. Indices 1-3
 * are the shipped defaults -- Miso the seal-point, Biscuit the warm solid,
 * Pumpkin the orange tabby -- tuned to be told apart at 22px.
 */
const PALETTES = [
  {
    name: 'tuxedo',
    furBase: '#4a4550',
    furShade: '#2f2b36',
    pattern: { kind: 'tuxedo-mask', color: '#fbf7f0' },
    eyeColor: '#8fce8f',
    noseColor: '#e8a1a1',
  },
  {
    name: 'seal point', // Miso
    furBase: '#f3e4c8',
    furShade: '#c2a37d',
    // v2 (owner, 2026-07-29): point lightened ~10% from v1's #8a6547 and
    // nose darkened ~25% overall from v1's #b98a76 -- the pale nose
    // floated silly against the dark mask; now the contrast runs the
    // right way (nose darker than mask, mouth darker still).
    pattern: { kind: 'point-mask', color: '#986f4e' },
    eyeColor: '#7ab8d9',
    noseColor: '#866455',
  },
  {
    name: 'biscuit tabby', // Biscuit
    furBase: '#e3bd8b',
    furShade: '#b9905f',
    pattern: { kind: 'tabby-stripes', color: '#c89a63' },
    eyeColor: '#8a5f2b',
    noseColor: '#c98d7b',
  },
  {
    name: 'pumpkin tabby', // Pumpkin
    furBase: '#f09d52',
    furShade: '#c0722f',
    pattern: { kind: 'tabby-stripes', color: '#cd7430' },
    eyeColor: '#6fae5c',
    noseColor: '#d98a77',
  },
  {
    name: 'storm',
    furBase: '#a9b2bf',
    furShade: '#7d8795',
    pattern: { kind: 'solid' },
    eyeColor: '#c9a227',
    noseColor: '#b58a94',
  },
  {
    name: 'midnight',
    furBase: '#4d4752',
    furShade: '#332e3b',
    pattern: { kind: 'solid' },
    eyeColor: '#e3b341',
    noseColor: '#8f7482',
  },
  {
    name: 'cloud',
    furBase: '#f7f3ec',
    furShade: '#c6b9a6',
    pattern: { kind: 'solid' },
    eyeColor: '#84b6d8',
    noseColor: '#e8a1a1',
  },
  {
    name: 'calico',
    furBase: '#faf4ea',
    furShade: '#c9baa4',
    pattern: { kind: 'patches', color: '#e2924e', color2: '#9b93a6' },
    eyeColor: '#b0793a',
    noseColor: '#e0958a',
  },
];

/**
 * The pose vocabulary -- the spec's clarified eight (idle is a standing
 * cat; sitting is deliberately skipped for now), plus v2's swim (the
 * parked 010 wading pose, built 2026-08-02; v1 never wears it).
 */
const POSES = [
  'idle',
  'walking',
  'pouncing',
  'eating',
  'drinking',
  'grooming',
  'loaf',
  'sleep-curl',
  'swim',
];

/**
 * Swim-pose tunables, mutable for the gallery lab's dials exactly like
 * EYE/NOSE/MOUTH: the owner dials, the paste gets baked here. Unit space
 * (0..1 box, ground near y 0.88); the pond draws underneath the cat, so
 * "underwater" is a reading the low flat silhouette earns, not clipping.
 */
const SWIM = {
  bodyY: 0.78, // body center: low, most of the cat under the waterline
  bodyRy: 0.14, // flattened floating body
  headY: 0.56, // head held clear of the water
  bob: 0.012, // vertical bob amplitude (paddle rhythm)
  rock: 0.045, // paddling body rock, radians
  tailLift: 0.6, // where the tail tip rides above the surface
};

/** The stable per-kitty appearance (FR-003). The one override point when
 * served appearance data exists someday: callers never index PALETTES. */
function appearanceFor(kittyId) {
  return PALETTES[kittyId % PALETTES.length];
}

/**
 * Twilight fur (dusk/night themes): the same appearance, every fur color
 * dimmed by the theme's named factor -- which also cures the "white
 * outline" a pale colorway like the seal point grows against dark grass,
 * since that ring is simply near-white furBase at full daylight
 * brightness. Eyes are the deliberate exception at every hour: dusk and
 * night are when a cat's eyes shine. The night factor was tuned live
 * (2026-07-22); dusk barely dims -- golden hour flatters the fur.
 */
const FUR_SHADE_BY_THEME = Object.freeze({ day: 1, dusk: 0.96, night: 0.89 });

function shadeHex(hex, factor) {
  const n = parseInt(hex.slice(1), 16);
  const r = Math.round(((n >> 16) & 255) * factor);
  const g = Math.round(((n >> 8) & 255) * factor);
  const b = Math.round((n & 255) * factor);
  return `#${((r << 16) | (g << 8) | b).toString(16).padStart(6, '0')}`;
}

/** Memoized per palette entry and factor -- appearances are stable
 * frozen objects, so identity is a sound cache key. */
const SHADED_APPEARANCES = new Map();

function shadedAppearanceOf(appearance, theme) {
  const factor = FUR_SHADE_BY_THEME[theme] ?? 1;
  if (factor === 1) return appearance;
  let byFactor = SHADED_APPEARANCES.get(appearance);
  if (!byFactor) {
    byFactor = new Map();
    SHADED_APPEARANCES.set(appearance, byFactor);
  }
  let shaded = byFactor.get(factor);
  if (!shaded) {
    const p = appearance.pattern;
    shaded = {
      ...appearance,
      furBase: shadeHex(appearance.furBase, factor),
      furShade: shadeHex(appearance.furShade, factor),
      noseColor: shadeHex(appearance.noseColor, factor),
      pattern: p && {
        ...p,
        ...(p.color ? { color: shadeHex(p.color, factor) } : {}),
        ...(p.color2 ? { color2: shadeHex(p.color2, factor) } : {}),
      },
    };
    byFactor.set(factor, shaded);
  }
  return shaded;
}

/**
 * Draws one cat.
 *
 * opts: {
 *   pose:       one of POSES                     (default 'idle')
 *   appearance: a PALETTES-shaped object         (required)
 *   facing:     'left' | 'right'                 (default 'left')
 *   size:       box edge in px                   (required)
 *   phase:      0..1 local animation phase       (default 0; poses may ignore)
 *   x, y:       top-left of the box in ctx space (default 0, 0)
 *   eyesOverride: force an eye state ('open'|'closed'|'half'|'focused') --
 *                 blinks (US4) and expressions (US5) land through here
 *   earsBack:   force the ears back briefly (ear twitch, sad beat)
 *   lid:        0..1 partial-blink lid over open eyes (v2) -- 1 lands on
 *               the same happy arcs as 'closed', so eased blinks work
 * }
 */
function drawCat(ctx, opts) {
  const {
    pose = 'idle',
    appearance,
    facing = 'left',
    size,
    phase = 0,
    x = 0,
    y = 0,
    eyesOverride,
    earsBack,
  } = opts;

  const L = catLayout(pose, phase);
  if (eyesOverride) L.eyes = eyesOverride;
  if (earsBack) L.earsUpright = false;
  paintBox(ctx, L, appearance, { facing, size, x, y, lid: opts.lid });
}

/** The shared box pipeline: mirror, scale, paint. drawCat and
 * drawCatTween meet here so a blended frame is drawn by exactly the
 * machinery a held pose uses. */
function paintBox(ctx, L, appearance, { facing, size, x, y, lid = 0 }) {
  // v2: `fine` gates only the tabby forehead stripes (sub-pixel noise when
  // small). Eyes, mouth and inner ears draw at every size -- v1's 44px
  // cliff meant no live-world cat ever wore its own face.
  const fine = size >= 44;

  ctx.save();
  ctx.translate(x, y);
  if (facing === 'left') {
    // The base cat faces right; a left-facing cat is its mirror.
    ctx.translate(size, 0);
    ctx.scale(-1, 1);
  }
  ctx.scale(size, size);
  ctx.lineJoin = 'round';
  ctx.lineCap = 'round';

  paintCat(ctx, L, appearance, fine, lid);
  ctx.restore();
}

/**
 * Pose-space blending: because every pose is a parameter set over the
 * same reference cat, a transition between poses is a lerp between their
 * layouts -- no frames, no assets. Discrete facts (eye state, ear set,
 * droplet, raised paw) switch at the midpoint; a leg with no counterpart
 * in the other pose shrinks away on its own half of the blend.
 */
function blendLayouts(A, B, t) {
  // Exact at both endpoints (float lerp lands t=1 a few ulps off B):
  // t=0 IS pose A and t=1 IS pose B, bit for bit.
  const n = t === 1 ? (a, b) => b : (a, b) => a + (b - a) * t;
  const legs = [];
  for (let i = 0; i < Math.max(A.legs.length, B.legs.length); i++) {
    const a = A.legs[i];
    const b = B.legs[i];
    if (a && b) {
      legs.push({ x: n(a.x, b.x), top: n(a.top, b.top), bottom: n(a.bottom, b.bottom), w: n(a.w, b.w) });
    } else if (a) {
      const w = a.w * Math.max(0, 1 - 2 * t);
      if (w > 0.015) legs.push({ ...a, w });
    } else if (b) {
      const w = b.w * Math.max(0, 2 * t - 1);
      if (w > 0.015) legs.push({ ...b, w });
    }
  }
  const late = t >= 0.5 ? B : A;
  return {
    body: {
      cx: n(A.body.cx, B.body.cx), cy: n(A.body.cy, B.body.cy),
      rx: n(A.body.rx, B.body.rx), ry: n(A.body.ry, B.body.ry),
      rot: n(A.body.rot || 0, B.body.rot || 0),
    },
    head: { cx: n(A.head.cx, B.head.cx), cy: n(A.head.cy, B.head.cy), r: n(A.head.r, B.head.r) },
    tail: {
      x0: n(A.tail.x0, B.tail.x0), y0: n(A.tail.y0, B.tail.y0),
      c1x: n(A.tail.c1x, B.tail.c1x), c1y: n(A.tail.c1y, B.tail.c1y),
      c2x: n(A.tail.c2x, B.tail.c2x), c2y: n(A.tail.c2y, B.tail.c2y),
      x1: n(A.tail.x1, B.tail.x1), y1: n(A.tail.y1, B.tail.y1),
    },
    legs,
    earsUpright: late.earsUpright,
    eyes: late.eyes,
    droplet: late.droplet,
    pawUp: late.pawUp,
  };
}

/**
 * Draws one cat mid-transition. Same opts as drawCat, except `pose` is
 * replaced by { from, to, t } (plus per-pose phases). t=0 is exactly
 * drawCat(from), t=1 exactly drawCat(to).
 */
function drawCatTween(ctx, opts) {
  const {
    from, to, t,
    appearance, facing = 'left', size,
    phaseFrom = 0, phaseTo = 0,
    x = 0, y = 0, eyesOverride, earsBack, lid,
  } = opts;
  const L = blendLayouts(catLayout(from, phaseFrom), catLayout(to, phaseTo), Math.min(1, Math.max(0, t)));
  if (eyesOverride) L.eyes = eyesOverride;
  if (earsBack) L.earsUpright = false;
  paintBox(ctx, L, appearance, { facing, size, x, y, lid });
}

// ---------------------------------------------------------------------------
// Layouts: each pose is a parameter set, never a separate drawing routine.
// Unit space: x 0..1 rightward, y 0..1 downward; the ground sits near y 0.88.
// ---------------------------------------------------------------------------

const TAU = Math.PI * 2;

function catLayout(pose, phase) {
  const breathe = Math.sin(phase * TAU);

  // The idle standing cat is the reference; poses adjust it. v2: the head
  // grows ~1.05x for kawaii proportion, at v1's exact position -- only the
  // radius changes (owner-tuned: 1.2x -> 1.1x -> 1.05x, pull-ins zeroed, 2026-07-29),
  // so any silhouette difference is size alone. The body is deliberately
  // v1's: "rounder cat", never "different cat".
  const L = {
    body: { cx: 0.44, cy: 0.64, rx: 0.3, ry: 0.21, rot: 0 },
    head: { cx: 0.7, cy: 0.4, r: 0.226 },
    earsUpright: true, // false = flattened back a touch (naps, meals)
    // Tail as a cubic bezier from rump to tip, drawn as an outlined stroke.
    tail: { x0: 0.16, y0: 0.62, c1x: 0.02, c1y: 0.62, c2x: 0.0, c2y: 0.42, x1: 0.05, y1: 0.3 },
    legs: [
      { x: 0.3, top: 0.74, bottom: 0.88, w: 0.1 },
      { x: 0.6, top: 0.74, bottom: 0.88, w: 0.1 },
    ],
    eyes: 'open', // 'open' | 'closed' | 'half' | 'focused'
    droplet: false,
    pawUp: false,
  };

  switch (pose) {
    case 'idle':
      L.body.ry += 0.008 * breathe; // soft breathing
      L.tail.x1 += 0.012 * breathe; // and an idly swaying tail tip
      break;

    case 'walking': {
      const stride = Math.sin(phase * TAU);
      L.body.rx = 0.32;
      L.body.cy += 0.008 * Math.sin(phase * 2 * TAU); // gait bob
      L.head.cx = 0.72;
      L.legs = [
        { x: 0.28 - 0.05 * stride, top: 0.74, bottom: 0.88, w: 0.095 },
        { x: 0.62 + 0.05 * stride, top: 0.74, bottom: 0.88, w: 0.095 },
      ];
      // Tail streams behind, gently lifted.
      L.tail = { x0: 0.14, y0: 0.58, c1x: 0.04, c1y: 0.56, c2x: 0.0, c2y: 0.5, x1: 0.03, y1: 0.42 };
      break;
    }

    case 'pouncing': {
      // Anticipation crouch, then the leap: squash before stretch. The
      // static pose (phase 0, reduced motion) is the loaded crouch.
      const leap = phase >= 0.45;
      if (!leap) {
        L.body = { cx: 0.42, cy: 0.68, rx: 0.31, ry: 0.17, rot: -0.1 };
        L.head = { cx: 0.68, cy: 0.5, r: 0.221 };
        L.legs = [
          { x: 0.28, top: 0.78, bottom: 0.88, w: 0.1 },
          { x: 0.58, top: 0.78, bottom: 0.88, w: 0.1 },
        ];
        // Tail high and twitching with intent.
        L.tail = {
          x0: 0.14, y0: 0.6, c1x: 0.03, c1y: 0.5, c2x: 0.0, c2y: 0.32,
          x1: 0.06 + 0.02 * Math.sin(phase * 2 * TAU), y1: 0.24,
        };
      } else {
        L.body = { cx: 0.46, cy: 0.56, rx: 0.34, ry: 0.165, rot: -0.18 };
        L.head = { cx: 0.78, cy: 0.34, r: 0.215 };
        L.legs = [
          { x: 0.22, top: 0.66, bottom: 0.84, w: 0.09 },
          { x: 0.74, top: 0.5, bottom: 0.68, w: 0.09 }, // forepaw reaching
        ];
        L.tail = { x0: 0.14, y0: 0.6, c1x: 0.02, c1y: 0.6, c2x: 0.0, c2y: 0.46, x1: 0.04, y1: 0.38 };
      }
      break;
    }

    case 'eating': {
      L.body.rot = 0.07; // leaning into the bowl
      L.head = { cx: 0.71, cy: 0.6 + 0.012 * Math.sin(phase * 2 * TAU), r: 0.21 };
      L.earsUpright = false;
      L.eyes = 'closed'; // happy chomping
      L.tail = { x0: 0.15, y0: 0.66, c1x: 0.05, c1y: 0.68, c2x: 0.02, c2y: 0.6, x1: 0.03, y1: 0.55 };
      L.legs = [
        { x: 0.28, top: 0.76, bottom: 0.88, w: 0.1 },
        { x: 0.56, top: 0.76, bottom: 0.88, w: 0.1 },
      ];
      break;
    }

    case 'drinking': {
      L.body.rot = 0.05;
      L.head = { cx: 0.72, cy: 0.57 + 0.008 * Math.sin(phase * 3 * TAU), r: 0.21 };
      L.earsUpright = false;
      L.eyes = 'half';
      L.droplet = true; // the little lap of water that says "drinking"
      L.tail = { x0: 0.15, y0: 0.66, c1x: 0.05, c1y: 0.68, c2x: 0.02, c2y: 0.6, x1: 0.03, y1: 0.55 };
      L.legs = [
        { x: 0.28, top: 0.76, bottom: 0.88, w: 0.1 },
        { x: 0.56, top: 0.76, bottom: 0.88, w: 0.1 },
      ];
      break;
    }

    case 'grooming': {
      // Head swung back toward the flank, one paw raised mid-lick; the
      // head nods with each lick.
      L.body = { cx: 0.48, cy: 0.64, rx: 0.3, ry: 0.21, rot: 0 };
      L.head = { cx: 0.54, cy: 0.42 + 0.012 * Math.sin(phase * 3 * TAU), r: 0.215 };
      L.eyes = 'closed';
      L.pawUp = true;
      L.legs = [{ x: 0.32, top: 0.76, bottom: 0.88, w: 0.1 }];
      L.tail = { x0: 0.16, y0: 0.62, c1x: 0.03, c1y: 0.6, c2x: 0.01, c2y: 0.44, x1: 0.06, y1: 0.34 };
      break;
    }

    case 'loaf': {
      L.body = { cx: 0.46, cy: 0.68, rx: 0.34, ry: 0.185 + 0.006 * breathe, rot: 0 };
      L.head = { cx: 0.68, cy: 0.48, r: 0.21 };
      L.eyes = 'half'; // contentedly elsewhere
      L.legs = []; // all paws folded away: the defining loaf fact
      // Tail wrapped along the front of the loaf.
      L.tail = { x0: 0.16, y0: 0.76, c1x: 0.3, c1y: 0.9, c2x: 0.56, c2y: 0.9, x1: 0.68, y1: 0.82 };
      break;
    }

    case 'sleep-curl': {
      const slow = Math.sin(phase * TAU * 0.5); // slower breath in sleep
      L.body = { cx: 0.5, cy: 0.64, rx: 0.3, ry: 0.25 + 0.008 * slow, rot: 0 };
      L.head = { cx: 0.62, cy: 0.68, r: 0.173 };
      L.earsUpright = false;
      L.eyes = 'closed';
      L.legs = [];
      // Tail curled right around to the nose.
      L.tail = { x0: 0.24, y0: 0.82, c1x: 0.4, c1y: 0.94, c2x: 0.66, c2y: 0.92, x1: 0.78, y1: 0.76 };
      break;
    }

    case 'swim': {
      // The wading kitty (spec 010's parked pose): a low flat float, head
      // and ears dry, legs paddling out of sight below the surface (none
      // drawn -- blends shrink them away on the way in). Paddling reads
      // as a gentle bob plus a slow body rock. Every number lives in SWIM
      // for the lab.
      //
      // No splash droplet (owner, 2026-08-04): at 0.028 x 0.04 of a tile
      // it is a ~2px smudge at any size this world draws at, so it read
      // as clutter rather than water. Being in water is said by the
      // ripple and the lost shadow, which are the renderer's job and
      // scale with the tile.
      const bob = SWIM.bob * Math.sin(phase * TAU);
      const rock = SWIM.rock * Math.sin(phase * TAU * 2);
      L.body = { cx: 0.44, cy: SWIM.bodyY + bob, rx: 0.3, ry: SWIM.bodyRy, rot: rock };
      L.head = { cx: 0.7, cy: SWIM.headY + bob, r: 0.226 };
      L.legs = [];
      // Tail trailing behind, tip riding above the surface.
      L.tail = {
        x0: 0.16, y0: SWIM.bodyY + bob,
        c1x: 0.04, c1y: SWIM.bodyY - 0.05,
        c2x: 0.0, c2y: SWIM.tailLift + 0.08,
        x1: 0.05, y1: SWIM.tailLift,
      };
      break;
    }

    default:
      break;
  }

  return L;
}

// ---------------------------------------------------------------------------
// Painting. Order matters: tail, body (+body pattern), legs, ears, head
// (+head pattern), face, extras -- so overlaps read like a cat.
// ---------------------------------------------------------------------------

const OUTLINE_W = 0.035;
const WATER_DROPLET = '#9ccfe6'; // matches the world's water rim

function paintCat(ctx, L, a, fine, lid = 0) {
  const p = a.pattern || { kind: 'solid' };

  drawTail(ctx, L.tail, a, p);
  drawBody(ctx, L.body, a, p);
  drawLegs(ctx, L.legs, a, p);
  drawEars(ctx, L.head, a, p, L.earsUpright);
  drawHead(ctx, L.head, a, p, fine);
  drawInnerEars(ctx, L.head, a, L.earsUpright);
  drawFace(ctx, L.head, L.eyes, a, lid);
  if (L.pawUp) drawRaisedPaw(ctx, L.head, a);
  if (L.droplet) drawDroplet(ctx, L.head);
}

function drawTail(ctx, t, a, p) {
  const color = p.kind === 'point-mask' ? p.color : a.furBase;
  const path = () => {
    ctx.beginPath();
    ctx.moveTo(t.x0, t.y0);
    ctx.bezierCurveTo(t.c1x, t.c1y, t.c2x, t.c2y, t.x1, t.y1);
  };
  path();
  ctx.strokeStyle = a.furShade;
  ctx.lineWidth = 0.085;
  ctx.stroke();
  path();
  ctx.strokeStyle = color;
  ctx.lineWidth = 0.085 - OUTLINE_W * 1.6;
  ctx.stroke();
}

function bodyPath(ctx, b) {
  ctx.beginPath();
  ctx.ellipse(b.cx, b.cy, b.rx, b.ry, b.rot || 0, 0, TAU);
}

function drawBody(ctx, b, a, p) {
  bodyPath(ctx, b);
  ctx.fillStyle = a.furBase;
  ctx.fill();
  ctx.strokeStyle = a.furShade;
  ctx.lineWidth = OUTLINE_W;
  ctx.stroke();

  // Body-side pattern work, clipped so it can never spill off the fur.
  ctx.save();
  bodyPath(ctx, b);
  ctx.clip();
  if (p.kind === 'tabby-stripes') {
    ctx.fillStyle = p.color;
    for (const s of [-0.45, 0, 0.45]) {
      ctx.beginPath();
      ctx.ellipse(
        b.cx + s * b.rx, b.cy - b.ry * 0.55,
        b.rx * 0.075, b.ry * 0.62, s * 0.25, 0, TAU,
      );
      ctx.fill();
    }
  } else if (p.kind === 'patches') {
    ctx.fillStyle = p.color;
    ctx.beginPath();
    ctx.ellipse(b.cx - b.rx * 0.4, b.cy - b.ry * 0.35, b.rx * 0.42, b.ry * 0.55, -0.3, 0, TAU);
    ctx.fill();
    ctx.fillStyle = p.color2 || p.color;
    ctx.beginPath();
    ctx.ellipse(b.cx + b.rx * 0.45, b.cy + b.ry * 0.3, b.rx * 0.34, b.ry * 0.5, 0.4, 0, TAU);
    ctx.fill();
  } else if (p.kind === 'tuxedo-mask') {
    // The white bib down the chest and belly.
    ctx.fillStyle = p.color;
    ctx.beginPath();
    ctx.ellipse(b.cx + b.rx * 0.5, b.cy + b.ry * 0.42, b.rx * 0.52, b.ry * 0.75, 0.15, 0, TAU);
    ctx.fill();
  }
  ctx.restore();
}

function drawLegs(ctx, legs, a, p) {
  for (const leg of legs) {
    const half = leg.w / 2;
    ctx.beginPath();
    ctx.moveTo(leg.x - half, leg.top);
    ctx.lineTo(leg.x - half, leg.bottom - half);
    ctx.arc(leg.x, leg.bottom - half, half, Math.PI, 0, true);
    ctx.lineTo(leg.x + half, leg.top);
    ctx.closePath();
    ctx.fillStyle = a.furBase;
    ctx.fill();
    ctx.strokeStyle = a.furShade;
    ctx.lineWidth = OUTLINE_W;
    ctx.stroke();

    // Socked paws for the masked colorways.
    if (p.kind === 'tuxedo-mask' || p.kind === 'point-mask') {
      ctx.save();
      ctx.clip(); // the leg path built above
      ctx.fillStyle = p.color;
      ctx.fillRect(leg.x - half, leg.bottom - leg.w * 0.9, leg.w, leg.w);
      ctx.restore();
    }
  }
}

function earPoints(head, side, back) {
  // side: +1 toward the facing direction, -1 behind. Upright ears sit high;
  // "back" ears (eating, sleeping) flatten outward a touch.
  const tiltOut = back ? 0.22 : 0.38;
  const spread = back ? 0.62 : 0.5;
  const baseAngle = -Math.PI / 2 + side * spread;
  const bx = head.cx + Math.cos(baseAngle) * head.r * 0.92;
  const by = head.cy + Math.sin(baseAngle) * head.r * 0.92;
  const apexAngle = baseAngle + side * (back ? 0.3 : 0.12);
  const ax = head.cx + Math.cos(apexAngle) * head.r * (back ? 1.28 : 1.42);
  const ay = head.cy + Math.sin(apexAngle) * head.r * (back ? 1.28 : 1.42);
  const halfBase = head.r * tiltOut;
  const perp = baseAngle + Math.PI / 2;
  return {
    b1x: bx + Math.cos(perp) * halfBase,
    b1y: by + Math.sin(perp) * halfBase,
    b2x: bx - Math.cos(perp) * halfBase,
    b2y: by - Math.sin(perp) * halfBase,
    ax,
    ay,
  };
}

function drawEars(ctx, head, a, p, upright) {
  const pointMask = p.kind === 'point-mask';
  for (const side of [-1, 1]) {
    const e = earPoints(head, side, !upright);
    ctx.beginPath();
    ctx.moveTo(e.b1x, e.b1y);
    ctx.lineTo(e.ax, e.ay);
    ctx.lineTo(e.b2x, e.b2y);
    ctx.closePath();
    // Calico wears one tinted ear; points wear both dark.
    let fill = a.furBase;
    if (pointMask) fill = p.color;
    else if (p.kind === 'patches' && side === 1) fill = p.color;
    ctx.fillStyle = fill;
    ctx.fill();
    ctx.strokeStyle = a.furShade;
    ctx.lineWidth = OUTLINE_W;
    ctx.stroke();
  }
}

function drawInnerEars(ctx, head, a, upright) {
  // Little pink inner-ear ticks, sized to stay inside the visible ear tips.
  ctx.fillStyle = a.noseColor;
  for (const side of [-1, 1]) {
    const e = earPoints(head, side, !upright);
    const mx = (e.b1x + e.b2x) / 2;
    const my = (e.b1y + e.b2y) / 2;
    ctx.beginPath();
    ctx.moveTo(mx + (e.ax - mx) * 0.35, my + (e.ay - my) * 0.35);
    ctx.lineTo(e.ax, e.ay);
    ctx.lineTo(mx + (e.ax - mx) * 0.75 + (e.b1x - e.b2x) * 0.12,
      my + (e.ay - my) * 0.75 + (e.b1y - e.b2y) * 0.12);
    ctx.closePath();
    ctx.fill();
  }
}

function headPath(ctx, head) {
  ctx.beginPath();
  ctx.arc(head.cx, head.cy, head.r, 0, TAU);
}

function drawHead(ctx, head, a, p, fine) {
  headPath(ctx, head);
  ctx.fillStyle = a.furBase;
  ctx.fill();
  ctx.strokeStyle = a.furShade;
  ctx.lineWidth = OUTLINE_W;
  ctx.stroke();

  ctx.save();
  headPath(ctx, head);
  ctx.clip();
  if (p.kind === 'point-mask') {
    // The seal-point face: a soft dark oval over the muzzle -- anchored
    // to NOSE.x (v2, owner 2026-07-29) so the mask follows the front-on
    // face instead of v1's profile muzzle at the head's edge. Upright
    // (no rotation): the old 0.1 rad lean was a profile artifact.
    ctx.fillStyle = p.color;
    ctx.globalAlpha = 0.85;
    ctx.beginPath();
    ctx.ellipse(head.cx + head.r * NOSE.x, head.cy + head.r * (NOSE.y + 0.08), head.r * 0.46, head.r * 0.32, 0, 0, TAU);
    ctx.fill();
    ctx.globalAlpha = 1;
  } else if (p.kind === 'tuxedo-mask') {
    // The white muzzle that makes the tuxedo, centered under the nose
    // like the point mask (v2).
    ctx.fillStyle = p.color;
    ctx.beginPath();
    ctx.ellipse(head.cx + head.r * NOSE.x, head.cy + head.r * (NOSE.y + 0.14), head.r * 0.5, head.r * 0.4, 0, 0, TAU);
    ctx.fill();
  } else if (p.kind === 'patches') {
    ctx.fillStyle = p.color2 || p.color;
    ctx.beginPath();
    // v2 (owner, 2026-07-29): the calico's grey patch, shrunk and slid up
    // toward the ear -- at v1's placement the relocated rear eye cut it
    // into a half-hidden sliver. Now it clears the eye and reads whole.
    ctx.ellipse(head.cx - head.r * 0.62, head.cy - head.r * 0.58, head.r * 0.36, head.r * 0.3, -0.35, 0, TAU);
    ctx.fill();
  } else if (p.kind === 'tabby-stripes' && fine) {
    // Three tiny forehead stripes, only when they can actually read.
    ctx.strokeStyle = p.color;
    ctx.lineWidth = OUTLINE_W * 0.8;
    for (const s of [-0.28, 0, 0.28]) {
      ctx.beginPath();
      ctx.moveTo(head.cx + head.r * (s + 0.02), head.cy - head.r * 0.92);
      ctx.lineTo(head.cx + head.r * s, head.cy - head.r * 0.45);
      ctx.stroke();
    }
  }
  ctx.restore();
}

/** Perceived-luminance check so eyes stay visible on every coat. */
function isDarkColor(hex) {
  const n = parseInt(hex.slice(1), 16);
  const r = (n >> 16) & 255;
  const g = (n >> 8) & 255;
  const b = n & 255;
  return 0.299 * r + 0.587 * g + 0.114 * b < 120;
}

/** The pupil's ink -- one warm near-black on every coat; the iris color
 * behind it carries the per-cat identity and the dark-fur contrast. */
const PUPIL_INK = '#2f2a26';

/**
 * Eye tunables (v2), BAKED from the lab dials (owner, 2026-07-29): bigger
 * than v1 (scale 0.19 vs 0.14), raised a touch above head center (height
 * -0.075 vs v1's +0.02), and shifted well back toward the middle of the
 * face (shift -0.15) -- a significant move off v1's nose-hugging
 * placement, dialed live and judged really cute. pupil is a ratio of the
 * iris radius. Still mutable: the lab's dials write here live.
 */
const EYE = {
  scale: 0.19, // iris radius / head.r
  height: -0.075, // eye center vs head center / head.r (+down, -up)
  shift: -0.15, // both eyes together / head.r (+toward nose, -toward back)
  spreadNear: 0.12, // rear eye offset / head.r
  spreadFar: 0.62, // front eye offset / head.r
  pupil: 0.7, // pupil radius / iris radius
  // The hunter's eyes keep v1's smaller radius AND v1's lower vertical
  // position (owner, 2026-07-29: the narrowed look reads worse blown up
  // or raised). Horizontal placement stays v2's shifted-back spread.
  focusedScale: 0.14,
  focusedHeight: 0.02, // v1's ey offset / head.r (+down, -up)
  // 'half' is a lidded open eye, not v1's flat dash: the same partial
  // lid the slow blink passes through, parked at this coverage. All
  // three lid values BAKED from the lab dials (owner, 2026-07-29).
  halfLid: 0.54,
  // Lid edge slope, in iris radii of drop per radius of run. Dialed
  // slightly NEGATIVE: the outer corners droop away from the nose --
  // the strong toward-the-middle slant read angry, the soft outward
  // droop reads sleepy. Applies to every lid; blinks sweep the same way.
  lidTilt: -0.08,
  // Lid edge curvature, in iris radii of center sag: + bows the edge
  // DOWN (convex -- rounder, sleepier), - scoops it UP (concave), 0 is
  // the straight edge (which read angry on its own, owner 2026-07-29).
  lidCurve: 0.14,
};

/** Nose tunables (v2), dialed in the lab like EYE. Working values
 * (owner, 2026-07-29, NOT final): pulled from v1's muzzle tip (0.86,
 * 0.26) back to the eye midline for the front-on face. */
const NOSE = {
  x: 0.22, // nose center from head center / head.r (toward the muzzle)
  y: 0.29, // below head center / head.r
  size: 0.17, // half-width / head.r
};

/** Mouth tunables (v2): an upside-down V hanging under the nose apex,
 * centered on NOSE.x. Under review (owner, 2026-07-29) -- the earlier
 * side-profile ω was tried and cut, but the front-on face reopened the
 * question. All ratios of head.r. */
const MOUTH = {
  style: 'w', // 'v' = upside-down V | 'w' = rounded ω (two half-ellipses)
  gap: 0, // space between nose apex and the mouth's center point
  width: 0.24, // half-span
  depth: 0.08, // vertical reach: leg drop ('v') or arc bulge ('w')
};

function drawFace(ctx, head, eyes, a, lid = 0) {
  const darkFur = isDarkColor(a.furBase);
  const eyeInk = darkFur ? a.eyeColor : '#453c36';
  const ex1 = head.cx + head.r * (EYE.spreadNear + EYE.shift);
  const ex2 = head.cx + head.r * (EYE.spreadFar + EYE.shift);
  const ey = head.cy + head.r * EYE.height;
  const er = head.r * EYE.scale;
  // 'half' rides the open-eye path under a standing lid (v2): the drowsy
  // face is the slow blink's midpoint, held. A deeper transient lid (a
  // blink mid-drink) still wins via max().
  if (eyes === 'half') {
    eyes = 'open';
    lid = Math.max(lid, EYE.halfLid);
  }
  // A fully-lowered lid IS the closed eye: blinks that ease the lid down
  // land on the same happy arcs a served 'closed' state draws.
  if (lid >= 0.97 && eyes !== 'focused') eyes = 'closed';

  if (eyes === 'closed') {
    // Happy little down-curved arcs.
    ctx.strokeStyle = eyeInk;
    ctx.lineWidth = OUTLINE_W * 0.9;
    for (const ex of [ex1, ex2]) {
      ctx.beginPath();
      ctx.arc(ex, ey - er * 0.4, er, 0.25 * Math.PI, 0.75 * Math.PI);
      ctx.stroke();
    }
  } else if (eyes === 'focused') {
    // The hunter's face (spec 005 US5): v1's shape at v1's size and v1's
    // lower height (focusedScale/focusedHeight) -- only the horizontal
    // spread follows the v2 face.
    const fer = head.r * EYE.focusedScale;
    const fey = head.cy + head.r * EYE.focusedHeight;
    for (const ex of [ex1, ex2]) {
      ctx.fillStyle = eyeInk;
      ctx.beginPath();
      ctx.ellipse(ex, fey + fer * 0.15, fer, fer * 0.55, 0, 0, TAU);
      ctx.fill();
      ctx.strokeStyle = eyeInk;
      ctx.lineWidth = OUTLINE_W * 0.9;
      ctx.beginPath();
      ctx.moveTo(ex - fer, fey - fer * 0.75);
      ctx.lineTo(ex + fer, fey - fer * 0.45);
      ctx.stroke();
    }
  } else {
    // Open eyes, fully dressed at every size: iris color, big pupil, one
    // bright glint. Canvas antialiasing shoulders the tiny sizes -- a
    // 22px cat keeps a readable spark where v1 drew two flat dots.
    for (const ex of [ex1, ex2]) {
      ctx.fillStyle = a.eyeColor;
      ctx.beginPath();
      ctx.arc(ex, ey, er, 0, TAU);
      ctx.fill();
      // A hairline liner so pale irises hold their shape on pale fur.
      ctx.strokeStyle = a.furShade;
      ctx.lineWidth = OUTLINE_W * 0.45;
      ctx.stroke();
      ctx.fillStyle = PUPIL_INK;
      ctx.beginPath();
      ctx.arc(ex, ey + er * 0.06, er * EYE.pupil, 0, TAU);
      ctx.fill();
      // (White glint tried and cut, owner 2026-07-29.)
      if (lid > 0.02) {
        // A partial lid: fur slides down over the eye, its edge sloping
        // toward the face's middle (lidTilt), with a soft lash line.
        // Clipped to the iris so it can never smear.
        ctx.save();
        ctx.beginPath();
        ctx.arc(ex, ey, er + OUTLINE_W * 0.3, 0, TAU);
        ctx.clip();
        const edge = ey - er + 2 * er * lid;
        const d = ex < (ex1 + ex2) / 2 ? 1 : -1; // downhill toward middle
        const run = er * 1.4;
        const drop = er * EYE.lidTilt;
        const top = ey - er * 1.4;
        const y0 = edge - d * drop;
        const y1 = edge + d * drop;
        // Quadratic control point: offset 2x sinks the curve's midpoint
        // by exactly er * lidCurve below the straight chord.
        const ctrlY = (y0 + y1) / 2 + 2 * er * EYE.lidCurve;
        ctx.fillStyle = a.furBase;
        ctx.beginPath();
        ctx.moveTo(ex - run, top);
        ctx.lineTo(ex + run, top);
        ctx.lineTo(ex + run, y1);
        ctx.quadraticCurveTo(ex, ctrlY, ex - run, y0);
        ctx.closePath();
        ctx.fill();
        ctx.strokeStyle = a.furShade;
        ctx.lineWidth = OUTLINE_W * 0.5;
        ctx.beginPath();
        ctx.moveTo(ex - run, y0);
        ctx.quadraticCurveTo(ex, ctrlY, ex + run, y1);
        ctx.stroke();
        ctx.restore();
      }
    }
  }

  // Nose: the tiny triangle that makes it a cat. Placed by NOSE dials.
  // v2: a symmetric upside-down triangle, upright with respect to the
  // eyes (owner call, 2026-07-29) -- v1's skewed profile-leaning triangle
  // read wrong once the face went front-on.
  const nx = head.cx + head.r * NOSE.x;
  const ny = head.cy + head.r * NOSE.y;
  const ns = head.r * NOSE.size;
  ctx.fillStyle = a.noseColor;
  ctx.beginPath();
  ctx.moveTo(nx - ns, ny - ns * 0.6);
  ctx.lineTo(nx + ns, ny - ns * 0.6);
  ctx.lineTo(nx, ny + ns * 0.7);
  ctx.closePath();
  ctx.fill();

  // Mouth under the nose, tracking NOSE.x; two styles under review
  // (owner, 2026-07-29). 'v': the upside-down V. 'w': the rounded front-on
  // ω -- two half-ellipses meeting beneath the nose apex, bulge set by
  // depth. (The old profile ω was cut with the profile face; this is its
  // front-on cousin.) No whiskers -- ever.
  // Ink: furShade normally, but on a point mask the mouth sits ON the
  // dark mask, so it inks slightly darker than the point color itself
  // (owner, 2026-07-29: furShade read pale-on-dark, silly).
  const my = ny + ns * 0.7 + head.r * MOUTH.gap;
  ctx.strokeStyle = a.pattern?.kind === 'point-mask'
    ? shadeHex(a.pattern.color, 0.82)
    : a.furShade;
  ctx.lineWidth = OUTLINE_W * 0.55;
  ctx.beginPath();
  if (MOUTH.style === 'w') {
    // Each half-ellipse needs its own moveTo: without it, canvas draws a
    // connecting chord between the arcs that closes them into solid-
    // looking capsules.
    const half = head.r * MOUTH.width * 0.5;
    for (const side of [-1, 1]) {
      const cx = nx + side * half;
      ctx.moveTo(cx + half, my);
      ctx.ellipse(cx, my, half, head.r * MOUTH.depth, 0, 0, Math.PI);
    }
  } else {
    ctx.moveTo(nx - head.r * MOUTH.width, my + head.r * MOUTH.depth);
    ctx.lineTo(nx, my);
    ctx.lineTo(nx + head.r * MOUTH.width, my + head.r * MOUTH.depth);
  }
  ctx.stroke();
}

function drawRaisedPaw(ctx, head, a) {
  // The grooming paw, lifted toward the swung-back head.
  ctx.beginPath();
  ctx.ellipse(head.cx + head.r * 1.05, head.cy + head.r * 1.15, 0.055, 0.09, -0.5, 0, TAU);
  ctx.fillStyle = a.furBase;
  ctx.fill();
  ctx.strokeStyle = a.furShade;
  ctx.lineWidth = OUTLINE_W;
  ctx.stroke();
}

function drawDroplet(ctx, head) {
  ctx.fillStyle = WATER_DROPLET;
  ctx.beginPath();
  ctx.ellipse(head.cx + head.r * 1.15, head.cy + head.r * 0.75, 0.028, 0.04, 0.3, 0, TAU);
  ctx.fill();
}

// ---------------------------------------------------------------------------
// Exports. Namespaced always (the comparison gallery and index.html's
// v1/v2 toggle draw both vocabularies from one page); global drop-in only
// when cat.js is absent, so a page can swap vocabularies by swapping one
// script tag.
// ---------------------------------------------------------------------------

const api = {
  drawCat,
  drawCatTween,
  blendLayouts,
  appearanceFor,
  shadedAppearanceOf,
  catLayout,
  EYE,
  NOSE,
  MOUTH,
  SWIM,
  PALETTES,
  POSES,
  // Not cat API, but props.js, meadow.js and app.js quietly depend on
  // these leaking from cat.js's top level (they define no fallbacks of
  // their own). Drop-in mode must leak them too or the first frame dies
  // with "TAU is not defined" and the page white-screens.
  TAU,
  OUTLINE_W,
};
globalThis.CatV2 = api;
if (typeof globalThis.drawCat === 'undefined') {
  Object.assign(globalThis, api);
}
})();
