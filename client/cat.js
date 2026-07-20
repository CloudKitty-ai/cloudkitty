/**
 * CloudKitty's cats, drawn from parameters.
 *
 * The one drawing vocabulary (spec 005, FR-001): the portrait gallery and the
 * live renderer both call exactly these functions, so what gets approved in
 * the gallery is what ships in the world. Everything is parametric -- a
 * palette is data, a pose is a parameter set, and revising the look means
 * editing this file and reloading.
 *
 * Pure drawing: no DOM access beyond the ctx argument, no fetches, no
 * globals written. Geometry lives in a unit box (0..1, y down), scaled to
 * `size` at draw time; the base cat faces right and mirrors for left.
 */

/* eslint-disable no-unused-vars */

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
    pattern: { kind: 'point-mask', color: '#8a6547' },
    eyeColor: '#7ab8d9',
    noseColor: '#b98a76',
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
 * The pose vocabulary -- eight names, matching the spec's clarified list
 * (idle is a standing cat; sitting is deliberately skipped for now).
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
];

/** The stable per-kitty appearance (FR-003). The one override point when
 * served appearance data exists someday: callers never index PALETTES. */
function appearanceFor(kittyId) {
  return PALETTES[kittyId % PALETTES.length];
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
  const fine = size >= 44; // whiskers, mouth, glints only when they can read

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

  paintCat(ctx, L, appearance, fine);
  ctx.restore();
}

// ---------------------------------------------------------------------------
// Layouts: each pose is a parameter set, never a separate drawing routine.
// Unit space: x 0..1 rightward, y 0..1 downward; the ground sits near y 0.88.
// ---------------------------------------------------------------------------

const TAU = Math.PI * 2;

function catLayout(pose, phase) {
  const breathe = Math.sin(phase * TAU);

  // The idle standing cat is the reference; poses adjust it.
  const L = {
    body: { cx: 0.44, cy: 0.64, rx: 0.3, ry: 0.21, rot: 0 },
    head: { cx: 0.7, cy: 0.4, r: 0.215 },
    earsUpright: true, // false = flattened back a touch (naps, meals)
    // Tail as a cubic bezier from rump to tip, drawn as an outlined stroke.
    tail: { x0: 0.16, y0: 0.62, c1x: 0.02, c1y: 0.62, c2x: 0.0, c2y: 0.42, x1: 0.05, y1: 0.3 },
    legs: [
      { x: 0.3, top: 0.74, bottom: 0.88, w: 0.1 },
      { x: 0.6, top: 0.74, bottom: 0.88, w: 0.1 },
    ],
    eyes: 'open', // 'open' | 'closed' | 'half'
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
        L.head = { cx: 0.68, cy: 0.5, r: 0.21 };
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
        L.head = { cx: 0.78, cy: 0.34, r: 0.205 };
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
      L.head = { cx: 0.71, cy: 0.6 + 0.012 * Math.sin(phase * 2 * TAU), r: 0.2 };
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
      L.head = { cx: 0.72, cy: 0.57 + 0.008 * Math.sin(phase * 3 * TAU), r: 0.2 };
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
      L.head = { cx: 0.54, cy: 0.42 + 0.012 * Math.sin(phase * 3 * TAU), r: 0.205 };
      L.eyes = 'closed';
      L.pawUp = true;
      L.legs = [{ x: 0.32, top: 0.76, bottom: 0.88, w: 0.1 }];
      L.tail = { x0: 0.16, y0: 0.62, c1x: 0.03, c1y: 0.6, c2x: 0.01, c2y: 0.44, x1: 0.06, y1: 0.34 };
      break;
    }

    case 'loaf': {
      L.body = { cx: 0.46, cy: 0.68, rx: 0.34, ry: 0.185 + 0.006 * breathe, rot: 0 };
      L.head = { cx: 0.68, cy: 0.48, r: 0.2 };
      L.eyes = 'half'; // contentedly elsewhere
      L.legs = []; // all paws folded away: the defining loaf fact
      // Tail wrapped along the front of the loaf.
      L.tail = { x0: 0.16, y0: 0.76, c1x: 0.3, c1y: 0.9, c2x: 0.56, c2y: 0.9, x1: 0.68, y1: 0.82 };
      break;
    }

    case 'sleep-curl': {
      const slow = Math.sin(phase * TAU * 0.5); // slower breath in sleep
      L.body = { cx: 0.5, cy: 0.64, rx: 0.3, ry: 0.25 + 0.008 * slow, rot: 0 };
      L.head = { cx: 0.62, cy: 0.68, r: 0.165 };
      L.earsUpright = false;
      L.eyes = 'closed';
      L.legs = [];
      // Tail curled right around to the nose.
      L.tail = { x0: 0.24, y0: 0.82, c1x: 0.4, c1y: 0.94, c2x: 0.66, c2y: 0.92, x1: 0.78, y1: 0.76 };
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

function paintCat(ctx, L, a, fine) {
  const p = a.pattern || { kind: 'solid' };

  drawTail(ctx, L.tail, a, p);
  drawBody(ctx, L.body, a, p);
  drawLegs(ctx, L.legs, a, p);
  drawEars(ctx, L.head, a, p, L.earsUpright);
  drawHead(ctx, L.head, a, p, fine);
  if (fine) drawInnerEars(ctx, L.head, a, L.earsUpright);
  drawFace(ctx, L.head, L.eyes, a, fine);
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
    // The seal-point face: a soft dark oval over the muzzle.
    ctx.fillStyle = p.color;
    ctx.globalAlpha = 0.85;
    ctx.beginPath();
    ctx.ellipse(head.cx + head.r * 0.62, head.cy + head.r * 0.28, head.r * 0.52, head.r * 0.4, 0.1, 0, TAU);
    ctx.fill();
    ctx.globalAlpha = 1;
  } else if (p.kind === 'tuxedo-mask') {
    // The white muzzle that makes the tuxedo.
    ctx.fillStyle = p.color;
    ctx.beginPath();
    ctx.ellipse(head.cx + head.r * 0.5, head.cy + head.r * 0.38, head.r * 0.55, head.r * 0.48, 0, 0, TAU);
    ctx.fill();
  } else if (p.kind === 'patches') {
    ctx.fillStyle = p.color2 || p.color;
    ctx.beginPath();
    ctx.ellipse(head.cx - head.r * 0.45, head.cy - head.r * 0.35, head.r * 0.5, head.r * 0.42, -0.4, 0, TAU);
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

function drawFace(ctx, head, eyes, a, fine) {
  const darkFur = isDarkColor(a.furBase);
  const eyeInk = darkFur ? a.eyeColor : '#453c36';
  const ex1 = head.cx + head.r * 0.14;
  const ex2 = head.cx + head.r * 0.62;
  const ey = head.cy + head.r * 0.02;
  const er = head.r * 0.14;

  if (eyes === 'closed') {
    // Happy little down-curved arcs.
    ctx.strokeStyle = eyeInk;
    ctx.lineWidth = OUTLINE_W * 0.9;
    for (const ex of [ex1, ex2]) {
      ctx.beginPath();
      ctx.arc(ex, ey - er * 0.4, er, 0.25 * Math.PI, 0.75 * Math.PI);
      ctx.stroke();
    }
  } else if (eyes === 'half') {
    ctx.strokeStyle = eyeInk;
    ctx.lineWidth = OUTLINE_W * 1.1;
    for (const ex of [ex1, ex2]) {
      ctx.beginPath();
      ctx.moveTo(ex - er * 0.8, ey);
      ctx.lineTo(ex + er * 0.8, ey);
      ctx.stroke();
    }
  } else {
    for (const ex of [ex1, ex2]) {
      if (fine && !darkFur) {
        // Iris ring behind the pupil, for the close-up portraits.
        ctx.fillStyle = a.eyeColor;
        ctx.beginPath();
        ctx.arc(ex, ey, er * 1.25, 0, TAU);
        ctx.fill();
      }
      ctx.fillStyle = eyeInk;
      ctx.beginPath();
      ctx.arc(ex, ey, er, 0, TAU);
      ctx.fill();
      if (fine) {
        ctx.fillStyle = 'rgba(255,255,255,0.85)';
        ctx.beginPath();
        ctx.arc(ex + er * 0.3, ey - er * 0.35, er * 0.32, 0, TAU);
        ctx.fill();
      }
    }
  }

  // Nose: the tiny triangle that makes it a cat.
  const nx = head.cx + head.r * 0.86;
  const ny = head.cy + head.r * 0.26;
  const ns = head.r * 0.14;
  ctx.fillStyle = a.noseColor;
  ctx.beginPath();
  ctx.moveTo(nx - ns, ny - ns * 0.6);
  ctx.lineTo(nx + ns * 0.7, ny - ns * 0.6);
  ctx.lineTo(nx - ns * 0.1, ny + ns * 0.7);
  ctx.closePath();
  ctx.fill();

  if (fine) {
    // The little ω mouth.
    ctx.strokeStyle = a.furShade;
    ctx.lineWidth = OUTLINE_W * 0.6;
    ctx.beginPath();
    ctx.arc(nx - ns * 1.1, ny + ns * 1.3, ns * 0.9, -0.25 * Math.PI, 0.6 * Math.PI);
    ctx.stroke();

    // Whiskers.
    ctx.strokeStyle = darkFur ? 'rgba(255,255,255,0.5)' : 'rgba(69,60,54,0.45)';
    ctx.lineWidth = OUTLINE_W * 0.45;
    for (const dy of [-0.06, 0.08]) {
      ctx.beginPath();
      ctx.moveTo(head.cx + head.r * 0.55, ny + head.r * dy);
      ctx.lineTo(head.cx - head.r * 0.15, ny + head.r * (dy - 0.09));
      ctx.stroke();
    }
  }
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
