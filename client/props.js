/**
 * CloudKitty's props, drawn from parameters (spec 007).
 *
 * The world's furniture in the cats' own vocabulary (FR-001): the gallery
 * and the live renderer both call exactly these functions, so what gets
 * approved is what ships. Shares cat.js's conventions through plain script
 * scope -- unit-box geometry (0..1, y down) scaled by `size`, outline-first
 * (`OUTLINE_W`), `TAU`, and the `fine = size >= 44` detail threshold.
 *
 * Pure drawing: no DOM beyond the ctx argument, no fetches. Timing periods
 * live in anim.js's `VIEW.props`; the *drawing-side* numbers (amplitudes,
 * the panic multiplier applied to an already-supplied phase) live in the
 * named `PROP_DEFAULTS` block below and defer to `VIEW.props` when the
 * animation layer is loaded -- the gallery deliberately runs without it.
 */

/* eslint-disable no-unused-vars */

/** The curated prop palette (FR-012): world-adjacent hues, named once. */
const PROPS_DAY = Object.freeze({
  bowlClay: '#cf8a5e', // terracotta, kin to the old kibble-brown pips
  bowlRim: '#a96a42',
  bowlInside: '#8f5a38',
  kibble: '#8a5f3c',
  ink: '#6b5a4e', // the world's --ink
  blush: '#f2a0b1', // the heart
  blushDeep: '#d97f95',
  soap: '#bfe3f2', // water-kin blues for drop and bubbles
  soapRim: '#9ccfe6',
  wisp: '#eef0f6', // the greeble's not-quite-there pale
  wispShade: '#8d96ad', // dark enough to hold the outline against grass
  yarn: '#c98da4', // a dusty rose no other prop uses
  fishDecal: '#3385ff', // the bowl's fish, a proper glaze blue (owner's pick)
  shadow: 'rgba(120, 110, 95, 0.25)', // the butterfly's ground shadow
  // Firefly colors -- only drawn from dusk onward (drawButterfly's
  // firefly opt), but named here so every palette inherits them.
  fireflyCore: 'rgba(255, 236, 160, 0.9)',
  fireflyMid: 'rgba(255, 236, 160, 0.38)',
  fireflyFade: 'rgba(255, 236, 160, 0)',
  fireflyLamp: 'rgba(255, 242, 170, 0.95)', // the abdomen pinpoint itself
});

/**
 * The props after sundown. Only what must change changes: the drawn ink
 * (Zs, yarn wraps) flips pale so it holds against dark grass, and the
 * shadows go away entirely. The furniture keeps its daytime colors -- a
 * terracotta bowl at night is still a terracotta bowl.
 */
const PROPS_NIGHT = Object.freeze({
  ...PROPS_DAY,
  ink: '#e6dccb',
  // Transparent, matching the meadow: nothing casts after dark, and a
  // firefly least of all (2026-08-05).
  shadow: 'rgba(8, 10, 20, 0)',
});

/** Golden hour barely touches the props: the daytime ink still reads on
 * amber grass, and only the shadows warm and stretch a little. */
const PROPS_DUSK = Object.freeze({
  ...PROPS_DAY,
  shadow: 'rgba(110, 75, 85, 0.28)',
});

/** Dawn does to the props what dusk does, in the opposite temperature:
 * the daytime ink still reads on cool grass, and the shadows go long and
 * cold instead of long and warm. */
const PROPS_DAWN = Object.freeze({
  ...PROPS_DAY,
  shadow: 'rgba(55, 60, 66, 0.28)',
});

/** The active palette; the theme switch (app.js setTheme) swaps it. */
const PROPS_BY_THEME = Object.freeze({
  day: PROPS_DAY,
  dusk: PROPS_DUSK,
  night: PROPS_NIGHT,
  dawn: PROPS_DAWN,
});

let PROPS = PROPS_DAY;

/** As setMeadowPalette: a named palette, or a blend of two between
 *  phases. `mixPalettes` lives in meadow.js, which loads after this file
 *  but well before anything calls in here. */
function setPropPalette(theme, next, t = 0) {
  const from = PROPS_BY_THEME[theme] ?? PROPS_DAY;
  if (!next || t <= 0) {
    PROPS = from;
    return;
  }
  PROPS = mixPalettes(from, PROPS_BY_THEME[next] ?? from, t);
}

/**
 * Three butterfly colorways (R2, FR-005) -- hues the meadow doesn't use,
 * pairwise distinguishable at 22px. Identity comes from the served element
 * id, exactly as kitty ids drive cat appearance.
 */
const BUTTERFLY_COLORWAYS = [
  { name: 'lavender', wing: '#c3b1e1', wingShade: '#8f7bb8', body: '#5d5470' },
  { name: 'lemon', wing: '#f2e2a0', wingShade: '#c9b665', body: '#6e6440' },
  { name: 'peach', wing: '#f7d9c9', wingShade: '#d9a68c', body: '#7a5c4e' },
];

/** The stable per-butterfly appearance (FR-005): callers never index. */
function butterflyColorwayFor(elementId) {
  return BUTTERFLY_COLORWAYS[elementId % BUTTERFLY_COLORWAYS.length];
}

/**
 * Drawing-side tunables, named (Article VI). `VIEW.props` (the animation
 * layer's frozen home for prop timing) overrides these when present; the
 * gallery runs on the defaults alone, which is what makes it standalone.
 */
const PROP_DEFAULTS = Object.freeze({
  panicMultiplier: 2.2, // flap-rate multiplier while hunted
  hoverLift: 0.06, // how high a butterfly rides above its shadow
  bobAmplitude: 0.035, // and how far the hover breathes
  wispBobAmplitude: 0.02,
  zRise: 0.08, // how far a Z drifts before fading out
  heartPulseScale: 0.08,
});

function propTunables() {
  return (typeof VIEW !== 'undefined' && VIEW.props) || PROP_DEFAULTS;
}

/**
 * Where the sun is, for anything here that casts a shadow (v3). The
 * values live in the meadow palette because they describe the world's
 * light rather than any one prop -- but gallery.html loads this file
 * WITHOUT meadow.js, so the read is defensive and falls back to a sun
 * directly overhead. Same defer-if-present shape as propTunables above.
 */
function sunShadow() {
  const world = typeof MEADOW !== 'undefined' ? MEADOW : null;
  return {
    lean: typeof world?.shadowLean === 'number' ? world.shadowLean : 0,
    length: typeof world?.shadowLength === 'number' ? world.shadowLength : 1,
  };
}

/** The wisp's not-quite-there outline (R6): dashed, unlike everything else. */
const WISP_DASH = [0.05, 0.035];

/** Shared entry: translate/scale into the unit box, rounded strokes. */
function propBox(ctx, size, x, y, draw) {
  ctx.save();
  ctx.translate(x, y);
  ctx.scale(size, size);
  ctx.lineJoin = 'round';
  ctx.lineCap = 'round';
  draw();
  ctx.restore();
}

// ---------------------------------------------------------------------------
// The bowl (R4, FR-004): the kibble mound IS the servings display.
// ---------------------------------------------------------------------------

/** Dot layouts per visible serving count -- a mound that shrinks bite by
 * bite, readable at 22px. Positions are (dx, dy) from the bowl's center. */
const KIBBLE_MOUNDS = [
  [], // 0: an empty bowl is a bowl, not an absence
  [[0, -0.02]],
  [[-0.07, -0.02], [0.07, -0.02]],
  [[-0.09, -0.01], [0.09, -0.01], [0, -0.09]],
  [[-0.12, 0], [0, -0.01], [0.12, 0], [-0.05, -0.09]],
  [[-0.12, 0], [0, -0.01], [0.12, 0], [-0.06, -0.09], [0.06, -0.09]],
];

function drawBowl(ctx, opts) {
  const { servings, size, x = 0, y = 0 } = opts;
  const level = Math.max(0, Math.min(5, servings ?? 0));
  const fine = size >= 44;

  propBox(ctx, size, x, y, () => {
    const rimY = 0.58;

    // The belly, thrown a little wide the way a proper cat bowl is.
    ctx.beginPath();
    ctx.moveTo(0.17, rimY);
    ctx.quadraticCurveTo(0.20, 0.82, 0.34, 0.85);
    ctx.quadraticCurveTo(0.5, 0.88, 0.66, 0.85);
    ctx.quadraticCurveTo(0.80, 0.82, 0.83, rimY);
    ctx.closePath();
    ctx.fillStyle = PROPS.bowlClay;
    ctx.fill();
    ctx.strokeStyle = PROPS.bowlRim;
    ctx.lineWidth = OUTLINE_W;
    ctx.stroke();

    if (fine) {
      // The little fish decal every cat bowl is legally required to have --
      // filled glaze-blue and low on the belly, where it reads against the
      // clay (gallery revisions 1-2, 2026-07-20).
      ctx.save();
      ctx.globalAlpha = 0.8;
      ctx.fillStyle = PROPS.fishDecal;
      ctx.beginPath();
      ctx.ellipse(0.48, 0.765, 0.07, 0.035, 0, 0, TAU);
      ctx.moveTo(0.55, 0.765);
      ctx.lineTo(0.60, 0.735);
      ctx.lineTo(0.60, 0.795);
      ctx.closePath();
      ctx.fill();
      ctx.restore();
    }

    // The opening, seen a touch from above.
    ctx.beginPath();
    ctx.ellipse(0.5, rimY, 0.34, 0.10, 0, 0, TAU);
    ctx.fillStyle = PROPS.bowlInside;
    ctx.fill();
    ctx.strokeStyle = PROPS.bowlRim;
    ctx.lineWidth = OUTLINE_W;
    ctx.stroke();

    // The mound: one dot per serving, stacked like real kibble settles.
    ctx.fillStyle = PROPS.kibble;
    ctx.strokeStyle = PROPS.bowlRim;
    ctx.lineWidth = OUTLINE_W * 0.6;
    for (const [dx, dy] of KIBBLE_MOUNDS[level]) {
      ctx.beginPath();
      ctx.arc(0.5 + dx, rimY - 0.05 + dy, 0.062, 0, TAU);
      ctx.fill();
      ctx.stroke();
    }
  });
}

// ---------------------------------------------------------------------------
// The butterfly (R3, FR-005/006): airborne by hover-bob over a shadow that
// stays on the ground.
// ---------------------------------------------------------------------------

function drawButterfly(ctx, opts) {
  const {
    colorway,
    phase = 0,
    bobPhase = 0,
    agitated = false,
    firefly = false,
    size,
    x = 0,
    y = 0,
  } = opts;
  const t = propTunables();
  const fine = size >= 44;
  // A hunted butterfly beats its wings faster; the rate lives on the
  // already-supplied phase so timing stays the animation layer's business.
  const flapPhase = agitated ? (phase * t.panicMultiplier) % 1 : phase;
  const flap = Math.abs(Math.sin(flapPhase * TAU)); // 0 folded .. 1 spread
  const spread = 0.55 + 0.45 * flap;
  const hover = t.hoverLift + t.bobAmplitude * Math.sin(bobPhase * TAU);

  propBox(ctx, size, x, y, () => {
    // The shadow keeps to the ground -- the gap is what says "flying" --
    // and leans and stretches with the sun, like the cats' (v3). No alpha
    // falloff here, unlike the cat shadow: the caller owns globalAlpha
    // for the element fade, and reading it back is not safe against the
    // harness's mock ctx, which answers every property with a function.
    // Anchored the same way the cats' shadows are: the sun-side edge stays
    // put and only the far edge travels.
    const sun = sunShadow();
    const footprint = 0.13 + 0.03 * flap;
    const halfWidth = footprint * sun.length;
    ctx.beginPath();
    ctx.ellipse(
      0.5 + sun.lean * (halfWidth - footprint),
      0.80,
      halfWidth,
      0.042,
      0,
      0,
      TAU,
    );
    ctx.fillStyle = PROPS.shadow;
    ctx.fill();

    ctx.save();
    ctx.translate(0, -hover);

    if (firefly) {
      // The twilight signature: a soft firefly glow carried behind the
      // body, riding the same hover so it never detaches from the flier.
      // Fireflies come out at dusk and stay for the night.
      const glow = ctx.createRadialGradient(0.5, 0.53, 0.02, 0.5, 0.53, 0.52);
      glow.addColorStop(0, PROPS.fireflyCore);
      glow.addColorStop(0.45, PROPS.fireflyMid);
      glow.addColorStop(1, PROPS.fireflyFade);
      ctx.fillStyle = glow;
      ctx.beginPath();
      ctx.arc(0.5, 0.53, 0.52, 0, TAU);
      ctx.fill();
    }

    // Wings: two chubby uppers, two small lower lobes, squashing toward
    // the body as they beat.
    for (const side of [-1, 1]) {
      ctx.beginPath();
      ctx.ellipse(
        0.5 + side * 0.16 * spread, 0.47,
        0.155 * spread, 0.125, side * 0.45, 0, TAU,
      );
      ctx.fillStyle = colorway.wing;
      ctx.fill();
      ctx.strokeStyle = colorway.wingShade;
      ctx.lineWidth = OUTLINE_W;
      ctx.stroke();

      ctx.beginPath();
      ctx.ellipse(
        0.5 + side * 0.095 * spread, 0.625,
        0.085 * spread, 0.07, side * 0.25, 0, TAU,
      );
      ctx.fillStyle = colorway.wing;
      ctx.fill();
      ctx.stroke();
    }

    // The dash of a body.
    ctx.beginPath();
    ctx.moveTo(0.5, 0.40);
    ctx.lineTo(0.5, 0.66);
    ctx.strokeStyle = colorway.body;
    ctx.lineWidth = 0.055;
    ctx.stroke();

    if (firefly) {
      // The lamp itself: a bright pinpoint at the abdomen tip, drawn over
      // the body so the light reads even where the halo washes out
      // against lighter grass.
      ctx.fillStyle = PROPS.fireflyLamp;
      ctx.beginPath();
      ctx.arc(0.5, 0.665, 0.055, 0, TAU);
      ctx.fill();
    }

    if (fine) {
      // Thread antennae with ball tips.
      ctx.strokeStyle = colorway.body;
      ctx.lineWidth = OUTLINE_W * 0.5;
      ctx.fillStyle = colorway.body;
      for (const side of [-1, 1]) {
        ctx.beginPath();
        ctx.moveTo(0.5, 0.41);
        ctx.quadraticCurveTo(0.5 + side * 0.05, 0.33, 0.5 + side * 0.09, 0.30);
        ctx.stroke();
        ctx.beginPath();
        ctx.arc(0.5 + side * 0.09, 0.30, 0.016, 0, TAU);
        ctx.fill();
      }
    }
    ctx.restore();
  });
}

// ---------------------------------------------------------------------------
// The greeble wisp (R6, FR-007): the one thing drawn as not-quite-there.
// The caller keeps the toggle and the translucency -- looks changed,
// secrecy didn't.
// ---------------------------------------------------------------------------

function drawGreebleWisp(ctx, opts) {
  const { face = 'blank', phase = 0, size, x = 0, y = 0 } = opts;
  const t = propTunables();
  const bob = t.wispBobAmplitude * Math.sin(phase * TAU);

  propBox(ctx, size, x, y, () => {
    ctx.save();
    ctx.translate(0, bob);

    // Teardrop body into a wavy skirt.
    ctx.beginPath();
    ctx.moveTo(0.5, 0.20);
    ctx.bezierCurveTo(0.76, 0.24, 0.80, 0.46, 0.78, 0.70);
    ctx.quadraticCurveTo(0.71, 0.63, 0.64, 0.72);
    ctx.quadraticCurveTo(0.57, 0.63, 0.5, 0.72);
    ctx.quadraticCurveTo(0.43, 0.63, 0.36, 0.72);
    ctx.quadraticCurveTo(0.29, 0.63, 0.22, 0.70);
    ctx.bezierCurveTo(0.20, 0.46, 0.24, 0.24, 0.5, 0.20);
    ctx.closePath();
    ctx.fillStyle = PROPS.wisp;
    ctx.fill();
    ctx.strokeStyle = PROPS.wispShade;
    ctx.lineWidth = OUTLINE_W * 0.8;
    ctx.setLineDash(WISP_DASH);
    ctx.stroke();
    ctx.setLineDash([]);

    // Hollow eyes: present, but nobody home.
    ctx.strokeStyle = PROPS.wispShade;
    ctx.lineWidth = OUTLINE_W * 0.8;
    for (const ex of [0.42, 0.58]) {
      ctx.beginPath();
      ctx.arc(ex, 0.42, 0.038, 0, TAU);
      ctx.stroke();
    }

    if (face === 'grin') {
      // The tiny grin of a creature that knows exactly what it's doing.
      ctx.beginPath();
      ctx.arc(0.5, 0.49, 0.055, 0.15 * Math.PI, 0.85 * Math.PI);
      ctx.stroke();
    }
    ctx.restore();
  });
}

// ---------------------------------------------------------------------------
// Overlays: the Zs and the heart (FR-008).
// ---------------------------------------------------------------------------

function drawSleepZs(ctx, opts) {
  const { phase = 0, size, x = 0, y = 0 } = opts;
  const t = propTunables();
  // Three Zs on a ladder; each drifts up and fades on its own offset of
  // the shared cycle. Phase 0 is the static ladder (reduced motion).
  const rungs = [
    { cx: 0.32, cy: 0.74, s: 0.10 },
    { cx: 0.52, cy: 0.48, s: 0.13 },
    { cx: 0.72, cy: 0.22, s: 0.16 },
  ];

  propBox(ctx, size, x, y, () => {
    ctx.strokeStyle = PROPS.ink;
    rungs.forEach((rung, i) => {
      const cyc = (phase + i * 0.33) % 1;
      const dy = -t.zRise * (phase === 0 ? 0 : cyc);
      const alpha = phase === 0 ? 0.9 - i * 0.25 : 0.9 * (1 - cyc);
      const half = rung.s / 2;
      ctx.save();
      ctx.globalAlpha = alpha;
      ctx.lineWidth = OUTLINE_W * 0.9;
      ctx.beginPath();
      ctx.moveTo(rung.cx - half, rung.cy - half + dy);
      ctx.lineTo(rung.cx + half, rung.cy - half + dy);
      ctx.lineTo(rung.cx - half, rung.cy + half + dy);
      ctx.lineTo(rung.cx + half, rung.cy + half + dy);
      ctx.stroke();
      ctx.restore();
    });
  });
}

/**
 * The purr glyph (owner's bake, 2026-08-14).
 *
 * A purr is a MOOD, not a request, and it used to wear the same speech
 * bubble as "I want to eat!". Measured on the candidate roster (attn-a1,
 * 246 ticks) that was 98% of every meow, and a bubble on screen 50.2% of
 * ticks -- so almost every bubble carried nothing a viewer could act on,
 * which is what devalues the ones that do. With purr taken out, request
 * bubbles fall to 1.2% of ticks and a bubble means something again.
 *
 * Judged in the lab against a drawn heart (vibrating and pulsing) and
 * sound waves; the owner took the emoji. Two things it cannot do, chosen
 * with eyes open: it will not follow the day/night palette, and it renders
 * as whatever emoji font the viewer's OS ships.
 */
const PURR = {
  size: 0.27, // share of the tile
  rise: -0.04, // NEGATIVE: down onto the cat's body (owner, 2026-08-14)
  offsetX: 0,
  alpha: 0.5,
  // A share of the GLYPH, with a pixel floor -- the same shape as the
  // whisker stroke, and for the opposite reason to the one first written
  // here. A flat pixel travel was tried and the owner's read (2026-08-14)
  // was that it looked cute large and frantic small, which is right: the
  // eye judges the displacement RELATIVE to the thing moving, and 0.8px
  // against an 8.4px glyph is a 9.6% lurch where the same 0.8px against a
  // 25px glyph is a 3.2% tremble.
  //
  // Pure proportion cannot do it alone either: anchored on the large view,
  // the live tile lands at 0.53px peak to peak and disappears under the
  // grid. So the share sets the character and the floor keeps it visible
  // at the tile the world actually draws at.
  // How many served ticks the glyph lingers. Its own number rather than
  // the bubbles' BUBBLE_TICKS (3): that was chosen as reading time for a
  // sentence, and a glyph is noticed rather than read. At 800ms a tick,
  // 2 is 1.6s -- long enough to catch a buzzing heart, a third less time
  // on screen than a bubble, which matters when a roster purrs this much.
  ticks: 2,
  shakeOfGlyph: 0.032,
  shakeMinPx: 0.4,
  shakeHz: 20,
};

/** Half the travel, in real pixels, for a glyph this big. */
function purrShakeAmp(px) {
  return Math.max(PURR.shakeMinPx, PURR.shakeOfGlyph * px);
}

/**
 * `phase` is 0..1 through one shake, and comes from the caller so a still
 * frame can hand over 0 and get a glyph that holds -- reduced motion keeps
 * the purr, it just stops it buzzing.
 */
function drawPurrGlyph(ctx, cx, topY, tile, phase) {
  const px = PURR.size * tile;
  ctx.save();
  ctx.globalAlpha = PURR.alpha;
  ctx.font = `${px}px system-ui, "Apple Color Emoji", "Segoe UI Emoji", sans-serif`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'alphabetic';
  ctx.fillText(
    '\u{1F497}',
    cx + PURR.offsetX * tile + Math.sin(phase * TAU) * purrShakeAmp(px),
    topY - PURR.rise * tile,
  );
  ctx.restore();
}

function drawHeart(ctx, opts) {
  const { phase = 0, size, x = 0, y = 0 } = opts;
  const t = propTunables();
  const pulse = 1 + t.heartPulseScale * Math.sin(phase * TAU);

  propBox(ctx, size, x, y, () => {
    ctx.save();
    ctx.translate(0.5, 0.53);
    ctx.scale(pulse, pulse);
    ctx.translate(-0.5, -0.53);

    ctx.beginPath();
    ctx.moveTo(0.5, 0.74);
    ctx.bezierCurveTo(0.12, 0.46, 0.24, 0.16, 0.5, 0.36);
    ctx.bezierCurveTo(0.76, 0.16, 0.88, 0.46, 0.5, 0.74);
    ctx.closePath();
    ctx.fillStyle = PROPS.blush;
    ctx.fill();
    ctx.strokeStyle = PROPS.blushDeep;
    ctx.lineWidth = OUTLINE_W;
    ctx.stroke();

    // One soft highlight.
    ctx.fillStyle = 'rgba(255, 255, 255, 0.65)';
    ctx.beginPath();
    ctx.ellipse(0.38, 0.36, 0.05, 0.035, -0.5, 0, TAU);
    ctx.fill();
    ctx.restore();
  });
}

// ---------------------------------------------------------------------------
// Thought icons (R5, FR-009): mini-props in one ink weight. Eat and cuddle
// reuse the real props -- consistency for free.
// ---------------------------------------------------------------------------

function drawNeedIcon(ctx, opts) {
  const { need, size, x = 0, y = 0 } = opts;

  switch (need) {
    case 'eat':
      drawBowl(ctx, { servings: 3, size, x, y });
      return;
    case 'sleep':
      drawSleepZs(ctx, { phase: 0, size, x, y });
      return;
    case 'cuddle':
      drawHeart(ctx, { phase: 0, size, x, y });
      return;
    default:
      break;
  }

  propBox(ctx, size, x, y, () => {
    if (need === 'drink') {
      // One plump water drop: pointed at the top where it fell from, a
      // proper round bulb at the bottom (gallery revision 3, 2026-07-20).
      const bulbR = 0.2;
      const bulbY = 0.56;
      ctx.beginPath();
      ctx.moveTo(0.5, 0.16);
      ctx.quadraticCurveTo(0.5 + bulbR, 0.34, 0.5 + bulbR, bulbY);
      ctx.arc(0.5, bulbY, bulbR, 0, Math.PI);
      ctx.quadraticCurveTo(0.5 - bulbR, 0.34, 0.5, 0.16);
      ctx.closePath();
      ctx.fillStyle = PROPS.soap;
      ctx.fill();
      ctx.strokeStyle = PROPS.soapRim;
      ctx.lineWidth = OUTLINE_W;
      ctx.stroke();
      ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
      ctx.beginPath();
      ctx.ellipse(0.43, 0.52, 0.04, 0.06, 0.3, 0, TAU);
      ctx.fill();
    } else if (need === 'play') {
      // A yarn ball: crossing wraps so it reads as wound thread, and the
      // trailing strand cats live for -- now longer, with a curl at the
      // end (gallery revision 4, 2026-07-20).
      ctx.beginPath();
      ctx.arc(0.48, 0.52, 0.26, 0, TAU);
      ctx.fillStyle = PROPS.yarn;
      ctx.fill();
      ctx.strokeStyle = PROPS.ink;
      ctx.lineWidth = OUTLINE_W * 0.8;
      ctx.stroke();
      // Two sets of two parallel wraps, angled against each other -- wound
      // yarn, not basketball seams (gallery revision 5, 2026-07-20).
      for (const [x0, y0, cx, cy2, x1, y1] of [
        [0.26, 0.65, 0.36, 0.38, 0.61, 0.30], // pair 1: lower-left -> upper-right
        [0.35, 0.72, 0.46, 0.48, 0.70, 0.40],
        [0.30, 0.36, 0.52, 0.44, 0.66, 0.68], // pair 2: upper-left -> lower-right
        [0.26, 0.46, 0.47, 0.53, 0.58, 0.74],
      ]) {
        ctx.beginPath();
        ctx.moveTo(x0, y0);
        ctx.quadraticCurveTo(cx, cy2, x1, y1);
        ctx.stroke();
      }
      // The strand: a longer fall, hooking into a little curl.
      ctx.beginPath();
      ctx.moveTo(0.7, 0.62);
      ctx.quadraticCurveTo(0.88, 0.7, 0.86, 0.86);
      ctx.quadraticCurveTo(0.845, 0.945, 0.775, 0.925);
      ctx.quadraticCurveTo(0.73, 0.91, 0.755, 0.865);
      ctx.stroke();
    } else if (need === 'bath') {
      // Three soap bubbles, each with its glint.
      ctx.lineWidth = OUTLINE_W * 0.8;
      for (const [bx, by, br] of [
        [0.38, 0.60, 0.15],
        [0.63, 0.52, 0.19],
        [0.47, 0.32, 0.11],
      ]) {
        ctx.beginPath();
        ctx.arc(bx, by, br, 0, TAU);
        ctx.fillStyle = PROPS.soap;
        ctx.globalAlpha = 0.85;
        ctx.fill();
        ctx.globalAlpha = 1;
        ctx.strokeStyle = PROPS.soapRim;
        ctx.stroke();
        ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
        ctx.beginPath();
        ctx.arc(bx - br * 0.35, by - br * 0.35, br * 0.22, 0, TAU);
        ctx.fill();
      }
    }
  });
}
