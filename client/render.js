/**
 * CloudKitty's renderer.
 *
 * A pure view: it draws whatever world the server sent and computes nothing about
 * the simulation itself (Article V). The one piece of judgement it makes is a
 * presentational one -- greebles are not drawn, which is why kitties appear to
 * chase nothing at all. Press `g` to see what they can see.
 */

// (TILE_COLORS is gone -- spec 008: every ground hue now lives in the named
// MEADOW palette in meadow.js, beside the drawings that use it.)

/** A ceiling on the map's longest side, in CSS pixels, so a very large
 * display does not blow the meadow up past the art's comfortable range.
 * On any normal screen the viewport height binds long before this does. */
const MAP_MAX_PX = 1200;

/** Slack for the margins between header, map and footer, which are not
 * worth measuring individually. Too small and the page gains a scrollbar;
 * too large and the map is needlessly shy of the space it has. Tightened
 * 40 -> 30 (owner, 2026-08-05) now that the rest of the fit is measured
 * rather than guessed. 16 was tried and is too tight: it left an 8-12px
 * scrollbar on the larger displays, which is exactly the inter-section
 * margin this constant stands in for. Verified scrollbar-free across the
 * display matrix at both 20x20 and 24x24 -- if that ever regresses, this
 * is the first number to suspect.
 *
 * The invariant is narrower than it reads: it holds where the cards sit
 * BESIDE the map (>= 1100px). Below that breakpoint they stack under it
 * and their height is real vertical chrome this sum does not include, so
 * a narrow window scrolls to reach them -- accepted (owner, 2026-08-05:
 * phones may scroll for the cards). */
const VERTICAL_SLACK = 30;

const MEOW_TEXT = {
  want_eat: 'I want to eat!',
  want_drink: 'I want to drink!',
  follow_me: 'Follow me!',
  want_play: 'I want to play!',
  want_cuddle: 'I want to cuddle!',
  purr: 'purrrr',
  wait_for_me: 'Wait for me!',
};

/** The greeble wisp's face -- decided at the 007 gallery gate (2026-07-20):
 * the tiny grin of a creature that knows exactly what it's doing. */
const GREEBLE_FACE = 'grin';

// (The sky dial moved to app.js, 2026-07-23: it perches on the map's top
// edge as its own overlay canvas -- page chrome, not world drawing.)

/** How many ticks a speech bubble lingers on screen. */
const BUBBLE_TICKS = 3;

/**
 * Which pose a served kitty is in (spec 005, data-model table): the activity
 * state speaks first, then the applied action, then movement, then idle --
 * with water under the last two (a wading kitty paddles instead of walking
 * or standing; activities and the pounce keep their poses, spec 010's
 * skirt-the-puddle rule makes all of these rare). Pure function of served
 * data -- nothing here predicts (Article V). `onWater` arrives pre-gated:
 * only the v2 vocabulary owns a swim pose, so v1 callers pass false.
 */
function poseFor(kitty, moved, onWater = false) {
  const state = kitty.activity?.state;
  if (state === 'sleeping') return 'sleep-curl';
  if (state === 'resting') return 'loaf';
  if (state === 'eating') return 'eating';
  if (state === 'drinking') return 'drinking';
  if (state === 'grooming') return 'grooming';
  const action = kitty.last_action?.action;
  if (action === 'play' || action === 'chase') return 'pouncing';
  if (onWater) return 'swim';
  if (moved) return 'walking';
  return 'idle';
}

/** The cat's own ground line, in its 0..1 unit space (see cat-v2). */
const CAT_GROUND_Y = 0.88;

/**
 * Where the pond surface cuts a cat, in the cat's unit space -- or null
 * when nothing should be clipped (BACKLOG P1, the owner's idea).
 *
 * Pure, and derived from `wet` rather than from the pose, because the
 * pose is exactly what must NOT decide this: `poseFor` lets drinking and
 * grooming outrank the wade, so those cats keep a land pose while
 * standing in a pond and still have to look wet. The one pose exempted
 * is `swim`, which is already drawn sunk and would be submerged twice.
 *
 * The surface travels from the ground line up to the waterline as `wet`
 * eases 0 -> 1, so a shoreline crossing raises the water instead of
 * popping it.
 */
function waterlineFor(pose, wet, dials = VIEW) {
  if (pose === 'swim' || !(wet > 0.01)) return null;
  return CAT_GROUND_Y - wet * (CAT_GROUND_Y - dials.waterline);
}

class WorldRenderer {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.showGreebles = false;
    this.showGrid = false; // spec 008 FR-004: the demoted debug lattice
    this.showPaths = false; // spec 008 FR-009: worn trails, off by default
    // Happiness bars, off by default (owner, 2026-08-05): the cards carry
    // the same number in words, and a well-trained roster pins happiness
    // near its ceiling anyway -- so four near-full bars said little while
    // sitting exactly where the ground shadows fall. `h` brings them back.
    this.showHappiness = false;
    this.theme = 'day'; // 'day' | 'dusk' | 'night' -- set by setTheme
    // (app.js), which also swaps the MEADOW/PROPS palettes and clears
    // the ground cache
    this.tile = 22;
    this.cssWidth = 0;
    this.cssHeight = 0;
    this.groundCache = null;
    this.pondCache = null; // { signature, ponds } -- rebuilt on water change
    // The devicePixelRatio the backing store was actually sized with, not
    // whatever the display reports right now (issue #102). Null until the
    // first fit.
    this.dpr = null;
  }

  /**
   * Fits the canvas to the world and the screen, accounting for retina
   * displays. Runs every frame, so the fit is a pure function of the
   * world's dimensions and the viewport: a rotated phone -- or a world
   * that someday grows mid-session -- re-fits on the next frame, no
   * resize listener required.
   */
  resizeFor(world) {
    // v3 (2026-08-04): fitted to the room the map actually has, in BOTH
    // axes. This used to be a flat 720px cap on width alone, so a square
    // world simply overflowed the viewport vertically and the page
    // scrolled -- and for a square world HEIGHT is the binding axis,
    // because screens are wide and not tall. Measured rather than
    // hardcoded, so reclaiming a header or moving the cards beside the
    // map (see index.html) feeds straight back into tile size.
    //
    // A cat draws at exactly one tile, so the tile IS the cat, and this
    // is the one dial that sets how big cats are.
    const doc = document.documentElement;
    const stage = this.canvas.parentElement;
    const cell = stage ? stage.parentElement : null;
    const px = (el, ...sides) => {
      if (!el) return 0;
      const cs = getComputedStyle(el);
      return sides.reduce((sum, side) => sum + (parseFloat(cs[side]) || 0), 0);
    };
    const boxOf = (sel) => {
      const el = document.querySelector(sel);
      return el ? el.getBoundingClientRect().height : 0;
    };

    const stagePadX = px(stage, 'paddingLeft', 'paddingRight');
    const stagePadY = px(stage, 'paddingTop', 'paddingBottom');
    // Everything the map is not: header, footer, the body's own padding,
    // the stage's padding, and a little slack for the margins between.
    const chromeY =
      boxOf('header') + boxOf('footer') +
      px(document.body, 'paddingTop', 'paddingBottom') +
      stagePadY + VERTICAL_SLACK;

    // Width the map may have: the layout's full width less whatever the
    // card columns take beside it. Measured from `.layout` rather than
    // from the map's own cell, because a content-sized cell is exactly as
    // wide as the canvas already in it -- ask that and the map can never
    // grow. When the cards are stacked below, the columns are
    // `display: contents` and measure zero, which is the right answer.
    const layout = cell ? cell.parentElement : null;
    const columns = layout ? layout.querySelectorAll('.panel-col') : [];
    let besideWidth = 0;
    for (const column of columns) besideWidth += column.getBoundingClientRect().width;
    const gap = layout ? parseFloat(getComputedStyle(layout).columnGap) || 0 : 0;
    const widthBudget =
      (layout ? layout.clientWidth : doc.clientWidth) -
      besideWidth -
      (besideWidth > 0 ? gap * columns.length : 0) -
      stagePadX;
    // Floored, and not only for tidiness: chromeY can exceed the viewport
    // on a very short window, and a negative budget used to reach `scale`
    // below and produce a negative CSS width. The CSSOM rejects that, so
    // `canvas.style.width` keeps its old value while the guard keeps
    // comparing it against a string that can never be assigned -- which
    // mismatches on EVERY frame and rebakes the whole ground cache at
    // 60fps. The tile had a floor already; the budget did not.
    const heightBudget = Math.max(120, (doc.clientHeight || 800) - chromeY);
    // A phone held sideways is the one viewport where fitting the height
    // is the wrong answer: a square world in a 280px-tall window is a
    // 12px tile whatever we reclaim, and there is half a screen of unused
    // WIDTH beside it. So on a short viewport the map fits the width and
    // overflows into a scroll instead -- owner call, 2026-08-07: "if they
    // want to scroll they can pinch zoom". Keyed to the same query the
    // landscape CSS uses, so "this screen is short" has one definition.
    const short =
      typeof matchMedia === 'function' && matchMedia('(max-height: 500px)').matches;
    this.tile = Math.max(
      8,
      Math.floor(
        Math.min(
          widthBudget / world.width,
          short ? Infinity : heightBudget / world.height,
          MAP_MAX_PX / Math.max(world.width, world.height),
        ),
      ),
    );
    const cssWidth = this.tile * world.width;
    const cssHeight = this.tile * world.height;
    // Integer tiles keep the art crisp, but the 8px floor means a wide
    // enough world (45+ tiles) is irreducibly wider than a phone. The
    // display scale absorbs the difference: the canvas still renders at
    // the floor and the browser shrinks the result to fit.
    const scale = Math.max(
      0.05,
      Math.min(1, widthBudget / cssWidth, short ? Infinity : heightBudget / cssHeight),
    );
    const displayWidth = `${cssWidth * scale}px`;
    const dpr = window.devicePixelRatio || 1;

    // The guard watches dpr as well as CSS width (issue #102). Dragging a
    // window between a Retina and a non-Retina display changes dpr while
    // the CSS width stays put, so a width-only guard left the backing
    // store at its old pixel size and old transform -- invisible on its
    // own, because everything drawn live is then stale *consistently*.
    // The damage surfaced minutes later, when the day->dusk->night change
    // nulled the ground cache and it rebaked at the old size with a fresh
    // dpr, putting the meadow in the upper-left quarter of the map.
    if (this.canvas.style.width !== displayWidth || this.dpr !== dpr) {
      this.canvas.style.width = displayWidth;
      this.canvas.style.height = `${cssHeight * scale}px`;
      this.canvas.width = Math.floor(cssWidth * dpr);
      this.canvas.height = Math.floor(cssHeight * dpr);
      this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      this.dpr = dpr;
      this.groundCache = null; // new size, new ground
      this.pondCache = null; // and shorelines rebuilt at the new tile size
    }
    this.cssWidth = cssWidth;
    this.cssHeight = cssHeight;
  }

  /**
   * Draws one frame: `world` is the newest served state, `view` the
   * presentational lens from anim.js (eased positions, fades, phases).
   * The same path serves animated and still frames -- a still frame is
   * simply progress 1 with fades off.
   */
  draw(world, view) {
    this.resizeFor(world);
    const ctx = this.ctx;
    ctx.clearRect(0, 0, this.cssWidth, this.cssHeight);

    // Which elements are being hunted right now (spec 007 FR-006): a pure
    // per-frame read of served pursuits, consumed by the butterfly's
    // panic flap. No store, no memory -- newest state wins.
    this.agitatedIds = new Set();
    for (const kitty of world.kitties) {
      const target = kitty.pursuit?.target;
      if (target && target.target === 'element') this.agitatedIds.add(target.id);
    }

    this.blitGround(world);
    // Worn paths sit directly on the grass, under everything that lives
    // (spec 008 US5); the grid overlay is debug chrome above them.
    if (this.showPaths && VIEW.meadow.paths) {
      drawWornPaths(ctx, { entries: view.wornPaths(), tile: this.tile });
    }
    if (this.showGrid && VIEW.meadow.gridOverlay) {
      drawGridOverlay(ctx, { width: world.width, height: world.height, tile: this.tile });
    }
    this.drawGroundAmbient(world, view);
    // Sunbeams are warmth on the ground, so they go under everything else.
    for (const el of world.elements) {
      if (el.kind === 'sunbeam') this.drawSunbeam(el, view.elementAlphaFor(el), view);
    }
    // Ponds: the merged, smooth-shored redrawing of exactly the served
    // water tiles (spec 008 US2). Mid-fade tiles stay individual pools.
    if (VIEW.meadow.ponds) this.drawPondLayer(world, view);
    // Expired elements take a brief bow instead of vanishing mid-glance.
    if (view.expired.length && view.expiredAlpha > 0) {
      for (const el of view.expired) {
        if (el.kind === 'sunbeam') this.drawSunbeam(el, view.expiredAlpha, view);
        else this.drawElement(el, view.expiredAlpha, view);
      }
    }
    for (const el of world.elements) {
      if (el.kind === 'sunbeam') continue;
      if (el.kind === 'water' && VIEW.meadow.ponds && view.elementAlphaFor(el) >= 1) {
        // Drawn by the pond body already; only its shimmer remains here.
        this.drawWaterShimmer(el, view);
        continue;
      }
      this.drawElement(el, view.elementAlphaFor(el), view);
    }
    // Cats and ground cover, interleaved by depth (v3, 2026-08-05).
    //
    // Ground cover used to bake into the ground cache, which sits under
    // everything -- so a cat crossing a shrub walked over the top of it.
    // Sorting the two together by their drawn y is what lets a cat pass
    // BEHIND one. Only these two participate: bubbles and thought
    // bubbles already run as their own passes below, so they stay clear
    // of cover for free, and served elements stay out of the ordering
    // rather than being sorted -- which avoids dragging bowls and
    // butterflies into it.
    //
    // That used to be free, because cover was kept off every served
    // element's tile. `occupiedTiles` now yields water only (see there for
    // why), so it is no longer free: the element pass above draws first,
    // so a shrub or tree sharing a tile with a bowl or a toy is painted
    // OVER it. Owner accepted that trade against the alternative -- trees
    // blinking out wherever a bug walked -- but it is a real edge, not the
    // guarantee this comment used to claim.
    const cover = typeof bushesFor === 'function'
      ? bushesFor(world.width, world.height, VIEW.meadow, this.occupiedTiles(world))
      : [];
    const layer = [];
    for (const bush of cover) {
      // Sorted by GROUND CONTACT, not by tile position: what decides
      // which of two things is in front is where each one meets the
      // earth. A cat's ground line is 88% down its box (the same 0.88 the
      // landing settle and the header wordmark use); a shrub's is its
      // base, below the canopy that stands up off it. Keying either by
      // its tile instead put a shrub on top of a cat sharing its tile --
      // the exact bug the sort exists to fix.
      layer.push({
        y: coverSortKey(bush, VIEW.meadow),
        draw: () => drawBushAt(this.ctx, { ...bush, tile: this.tile, t: VIEW.meadow }),
      });
    }
    for (const kitty of world.kitties) {
      layer.push({
        y: catSortKey(view.posFor(kitty)),
        draw: () => this.drawKitty(kitty, world, view),
      });
    }
    layer.sort((a, b) => a.y - b.y);
    for (const item of layer) item.draw();

    this.drawBubbles(world, view);
    // Thought bubbles sit above speech in the stack (the documented
    // two-beats rule): at most one per kitty, only while the wait is long.
    for (const kitty of world.kitties) {
      const need = view.thoughtFor(kitty);
      if (need) this.drawThought(kitty, need, view);
    }
  }

  /**
   * The meadow never changes between resizes, so it is rendered once to
   * an offscreen layer and blitted per frame (005 research R7) -- the
   * difference between thousands of fills and one drawImage each frame.
   * The grid lines that used to live here are now the debug-only overlay
   * behind `l` (spec 008 FR-004).
   */
  /**
   * Tiles the ground cover must keep off, and ONLY the ones that will still
   * be there next tick.
   *
   * This used to take every served element, which made trees blink: a bug or
   * a greeble skittering across the meadow occupied a tile for a moment, the
   * tree standing there vanished, and it came back when the critter moved on
   * (owner-reported 2026-08-07; measured at one flickering tile in 41 samples
   * of a fast world, the culprit a greeble). Chow and sunbeams do the same
   * more slowly, by spawning and expiring.
   *
   * Water is the only element that is a fact about the world rather than an
   * event in it -- placed at worldgen and fixed for the world's life -- so
   * keying on it alone makes the cover a pure function of the map, stable for
   * the session, which is what scenery has to be. A bowl can now spawn on a
   * tree's tile; at a 1.5% cover chance that is about one tile in eight
   * worlds, and a bowl briefly under a canopy is a far smaller wrong than
   * trees popping in and out everywhere a bug walks.
   */
  occupiedTiles(world) {
    const taken = new Set();
    for (const el of world.elements) {
      if (el.kind !== 'water') continue;
      taken.add(`${el.pos.x},${el.pos.y}`);
    }
    return taken;
  }

  blitGround(world) {
    // The cache's transform must be the ratio the canvas was SIZED with,
    // never a freshly-read devicePixelRatio (issue #102): the offscreen is
    // sized from `this.canvas.width`, so reading the display's current dpr
    // here straddles the two and paints the meadow into a corner of its
    // own cache. Belt and braces on top of the resize guard -- the stamp
    // catches any future path that clears the cache without a resize.
    const dpr = this.dpr || window.devicePixelRatio || 1;
    const stale =
      !this.groundCache ||
      this.groundCache.dataset.dpr !== String(dpr) ||
      this.groundCache.width !== this.canvas.width;
    if (stale) {
      const off = document.createElement('canvas');
      off.width = this.canvas.width;
      off.height = this.canvas.height;
      const g = off.getContext('2d');
      g.setTransform(dpr, 0, 0, dpr, 0, 0);
      // `cover: false` -- ground cover is drawn per frame instead, sorted
      // against the cats so they can pass behind it (see draw()).
      drawMeadowGround(g, { width: world.width, height: world.height, tile: this.tile, cover: false });
      off.dataset.dpr = String(dpr);
      this.groundCache = off;
    }
    this.ctx.drawImage(this.groundCache, 0, 0, this.cssWidth, this.cssHeight);
  }

  /**
   * The pond layer (spec 008 US2): group the fully-present served water
   * tiles, cache their smooth shorelines under the position signature,
   * and redraw the cached paths -- rebuild only when water actually
   * spawns or expires. Mid-fade tiles are excluded here and drawn as
   * their own small pools by drawElement, at the element alpha.
   */
  drawPondLayer(world, view) {
    const stable = [];
    for (const el of world.elements) {
      if (el.kind === 'water' && view.elementAlphaFor(el) >= 1) stable.push(el.pos);
    }
    if (!stable.length) {
      this.pondCache = null;
      return;
    }
    const signature = stable.map((p) => `${p.x},${p.y}`).sort().join(';');
    if (!this.pondCache || this.pondCache.signature !== signature) {
      const groups = groupWaterTiles(stable);
      this.pondCache = {
        signature,
        ponds: groups.map((tiles) => ({ tiles, path: buildPondPath(tiles, this.tile) })),
      };
    }
    drawPonds(this.ctx, { ponds: this.pondCache.ponds, tile: this.tile });
  }

  /** The shimmer sliding across a water surface (005 US6), shared by the
   * pond body and the standalone pools. */
  drawWaterShimmer(el, view) {
    const t = view?.ambient?.now;
    if (t === undefined || !VIEW.ambient.waterShimmer) return;
    const ctx = this.ctx;
    const { x, y } = this.tileOrigin(el.pos);
    const cx = x + this.tile / 2;
    const cy = y + this.tile / 2;
    ctx.save();
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.55)';
    ctx.lineWidth = 1.2;
    ctx.lineCap = 'round';
    const drift = Math.sin(t / 1600 + el.id) * this.tile * 0.14;
    for (const [dx, dy, len] of [[-0.18, -0.12, 0.24], [0.06, 0.14, 0.18]]) {
      ctx.beginPath();
      ctx.moveTo(cx + dx * this.tile + drift, cy + dy * this.tile);
      ctx.lineTo(cx + (dx + len) * this.tile + drift, cy + dy * this.tile);
      ctx.stroke();
    }
    ctx.restore();
  }

  /**
   * Ambient life on the ground layer (US6, FR-013): each effect sits behind
   * its own named VIEW flag, stays subtle, and is absent entirely when the
   * view carries no ambient clock (reduced motion).
   */
  drawGroundAmbient(world, view) {
    if (!view.ambient) return;
    const ctx = this.ctx;
    const t = view.ambient.now;

    // Cloud shadows are sunlight's doing, so the night sky has none
    // (owner call, 2026-07-23) -- and their greenish daytime tint read
    // wrong on moonlit grass anyway.
    if (VIEW.ambient.cloudShadows && this.theme !== 'night') {
      // Two soft shadows drifting slowly across the meadow.
      ctx.save();
      ctx.fillStyle = 'rgba(120, 140, 110, 0.05)';
      for (const [speed, cy, ry] of [[1, 0.28, 3.2], [1.35, 0.72, 2.4]]) {
        const span = this.cssWidth + this.tile * 12;
        const cx = ((t * speed) / VIEW.cloudPeriodMs) * span % span - this.tile * 6;
        ctx.beginPath();
        ctx.ellipse(cx, cy * this.cssHeight, this.tile * 5, this.tile * ry, 0.3, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.restore();
    }

    // (Grass sway retired 2026-07-22: its fixed-pixel blades read as stray
    // diagonal lines at small tile sizes. A tile-proportional return is
    // queued with the meadow finishing touches in BACKLOG.md.)
  }

  drawSunbeam(el, alpha = 1, view) {
    const ctx = this.ctx;
    const { x, y } = this.tileOrigin(el.pos);
    const t = view?.ambient?.now;
    // The warm pulse: a slow breathing of the beam's glow (US6).
    const pulse =
      t !== undefined && VIEW.ambient.sunbeamPulse
        ? 0.92 + 0.08 * Math.sin(t / 1900 + el.id)
        : 1;
    ctx.save();
    if (VIEW.meadow.glow) {
      // Light, not a tile (spec 008 US4): the warm radial pool bleeding
      // softly past the tile bounds, breathing on the same pulse.
      drawSunbeamGlow(ctx, {
        cx: x + this.tile / 2,
        cy: y + this.tile / 2,
        tile: this.tile,
        alpha: alpha * pulse,
      });
    } else {
      // The glow layer disabled: a plain warm tile keeps the beam readable.
      ctx.globalAlpha = alpha * pulse;
      ctx.fillStyle = MEADOW.glowMid;
      this.roundRect(x + 1, y + 1, this.tile - 2, this.tile - 2, 6);
      ctx.fill();
      ctx.globalAlpha = 1;
    }

    if (t !== undefined && VIEW.ambient.dustMotes) {
      // Two lazy dust motes circling in the warmth.
      ctx.fillStyle = MEADOW.moteColor;
      for (const i of [0, 1]) {
        const angle = t / (2600 + i * 700) + el.id * 2.1 + i * Math.PI;
        const mx = x + this.tile / 2 + Math.cos(angle) * this.tile * 0.28;
        const my = y + this.tile / 2 + Math.sin(angle * 1.3) * this.tile * 0.24;
        ctx.globalAlpha = alpha * (0.4 + 0.3 * Math.sin(angle * 2));
        ctx.beginPath();
        ctx.arc(mx, my, 1.1, 0, Math.PI * 2);
        ctx.fill();
      }
    }
    ctx.restore();
  }

  drawElement(el, alpha = 1, view) {
    // The greeble rule: present in the data, absent from the picture.
    if (el.kind === 'greeble' && !this.showGreebles) return;

    const ctx = this.ctx;
    ctx.save();
    ctx.globalAlpha = alpha;
    // Critters glide between served states (007 refinement); furniture
    // stands still, as furniture does.
    const isCritter = el.kind === 'bug' || el.kind === 'greeble';
    const pos = isCritter && view ? view.elementPosFor(el) : el.pos;
    const { x, y } = this.tileOrigin(pos);

    switch (el.kind) {
      case 'water': {
        // The standalone pool: mid-fade (spawning/expiring) water, and
        // every water tile when the pond layer is disabled (spec 008
        // US2). Fully-present water otherwise draws as the merged pond
        // body in drawPondLayer.
        ctx.fillStyle = MEADOW.pondWater;
        this.roundRect(x + 2, y + 2, this.tile - 4, this.tile - 4, 8);
        ctx.fill();
        ctx.strokeStyle = MEADOW.pondRim;
        ctx.lineWidth = 1.5;
        ctx.stroke();
        this.drawWaterShimmer(el, view);
        break;
      }
      case 'chow': {
        // The terracotta bowl whose kibble mound IS the servings display
        // (spec 007 FR-004) -- the old meter bar is gone with the emoji.
        drawBowl(ctx, { servings: el.servings ?? 0, size: this.tile, x, y });
        break;
      }
      case 'bug':
        // Drawn as a butterfly (spec 007): its own stable colorway, wings
        // on the flap clock, hover above a grounded shadow, and a panicked
        // beat while any kitty's served pursuit names it (FR-005/006).
        drawButterfly(ctx, {
          colorway: butterflyColorwayFor(el.id),
          phase: view.propPhaseFor(el.id, VIEW.props.flapPeriodMs),
          bobPhase: view.propPhaseFor(el.id, VIEW.props.bobPeriodMs),
          agitated: this.agitatedIds?.has(el.id) ?? false,
          firefly: this.theme !== 'day', // fireflies from dusk onward
          size: this.tile,
          x,
          y,
        });
        break;
      case 'greeble':
        // Only ever reached with the debug toggle on: the wisp, wearing
        // the gate-chosen grin. Still translucent -- it is a ghost -- but
        // legible: at the original 0.55 the pale body vanished into the
        // grass and the toggle looked broken (owner call, 2026-07-22).
        ctx.globalAlpha = 0.8 * alpha;
        drawGreebleWisp(ctx, {
          face: GREEBLE_FACE,
          phase: view.propPhaseFor(el.id, VIEW.props.wispBobMs),
          size: this.tile,
          x,
          y,
        });
        break;
      default:
        break;
    }
    ctx.restore();
  }

  drawKitty(kitty, world, view) {
    const ctx = this.ctx;
    const pos = view.posFor(kitty);
    const { x, y } = this.tileOrigin(pos);
    const cx = x + this.tile / 2;
    const cy = y + this.tile / 2;
    const state = kitty.activity?.state ?? 'idle';

    // Live motion and the swim pose are v2-vocabulary affairs: the
    // dispatcher installs drawCatTween exactly when v2 kitties are
    // active, so v1 keeps its pose snap, its snap blink, and its
    // walk-through-water by construction.
    const v2Motion = typeof drawCatTween === 'function';
    // A kitty over a water tile is wading (spec 010's parked swim pose).
    // Keyed on the tile under the DRAWN cat -- the eased interpolation,
    // not the served destination -- so the pose flips as the cat visibly
    // crosses the shore (mid-tick; the tween machinery blends it there),
    // never a full glide early. The served elements are the truth about
    // where water is, mid-fade or not.
    const onWater =
      v2Motion &&
      world.elements.some(
        (el) =>
          el.kind === 'water' &&
          el.pos.x === Math.round(pos.x) &&
          el.pos.y === Math.round(pos.y),
      );

    // The approved vector cat (spec 005 US2/US4/US5): identity from the
    // kitty's id, pose from served state (with the fall-asleep settle),
    // facing from its last horizontal movement, motion from the animation
    // layer -- and the drama layered by the documented rule: pose, then
    // action animation, then expression, then the single one-shot beat.
    const pose = view.adjustPose(kitty.id, poseFor(kitty, view.movedFor(kitty.id), onWater));

    const motion = view.motionFor(kitty.id, pose);
    const beat = view.oneShotFor(kitty.id);
    let eyes = motion.eyesOverride;
    let ears = motion.earsBack;
    let lid;
    if (v2Motion && motion.blinkLid !== undefined) {
      lid = motion.blinkLid;
      if (eyes === 'closed') eyes = undefined; // the eased lid replaces the snap blink
    }
    const expression = view.expressionFor(kitty);
    // On the v2 path a pursuit's focused eyes hold through the blink slot
    // -- drawFace exempts 'focused' from the lid, so hunters keep their
    // unbroken stare (v1 still snap-blinks over focused, as it always
    // has). Locked (owner, 2026-08-02): hunting kitties do not blink.
    if (expression && !eyes) eyes = expression;
    if (beat?.kind === 'sad') {
      // The give-up droop wears on the cat itself: ears back, eyes low --
      // and it outranks a blink in progress, exactly as it did pre-lid
      // (a full lid would promote the droop to the happy closed arcs).
      ears = true;
      eyes = 'half';
      lid = undefined;
    }
    const tween = v2Motion && view.tweenFor ? view.tweenFor(kitty.id, pose, motion.phase) : null;

    // Wetness is a fact about the tile, not the pose (owner call,
    // 2026-08-04). `poseFor` lets an activity outrank the wade, so a cat
    // drinking in a pond keeps its drinking pose -- but it is still
    // standing in water and should look it. One eased signal now drives
    // both cues, the shadow it loses and the ripple it gains, so the two
    // can never disagree the way the old pose-derived reading could: that
    // read `pose === 'swim'`, and therefore dried a grooming cat off
    // while it stood in the pond.
    const wet = v2Motion && view.wetFor ? view.wetFor(kitty.id, onWater) : 0;

    // A soft shadow so cats sit on the grass rather than float above it --
    // and, since v3, one that knows where the sun is. It leans and
    // stretches with the phase (MEADOW.shadowLean / shadowLength), which
    // is the cue that most says "the hour is moving": short and almost
    // straight down at noon, long and thrown to one side at sunset, long
    // to the OTHER side at dawn, and directionless under the moon.
    // Because both are plain numbers, they interpolate across a phase
    // crossing for free -- the shadow swings round as the light does.
    const shadowAlpha = 1 - wet;
    if (shadowAlpha > 0) {
      const lean = MEADOW.shadowLean ?? 0;
      const length = MEADOW.shadowLength ?? 1;
      // A shadow starts at the thing casting it and runs away from the
      // light -- it does not spread out both ways. So the extra length is
      // thrown entirely to one side: the sun-side edge stays where the
      // caster's own footprint is, and only the far edge travels.
      //
      // Multiplying the throw by `lean` rather than by its sign keeps this
      // smooth: at lean 0 (noon, and the moon) the stretch stays
      // symmetrical, which is right for a light directly overhead, and
      // nothing jumps as the lean crosses zero between phases.
      const footprint = this.tile * 0.3;
      const halfWidth = footprint * length;
      const offset = lean * (halfWidth - footprint);
      ctx.save();
      // Alpha falls as the shadow stretches: the same darkness spread
      // over more ground would read as a stain rather than a shadow.
      ctx.globalAlpha = shadowAlpha / Math.max(1, length * 0.8);
      ctx.fillStyle = MEADOW.groundShadow;
      ctx.beginPath();
      ctx.ellipse(
        cx + offset,
        cy + this.tile * 0.32,
        halfWidth,
        this.tile * 0.12,
        0,
        0,
        Math.PI * 2,
      );
      ctx.fill();
      ctx.restore();
    }
    if (wet > 0.01) {
      // ...and the water it displaces instead. A first pass: the finished
      // waterline is the pond restyle's business, judged in the lab.
      ctx.save();
      ctx.globalAlpha = wet * 0.55;
      ctx.strokeStyle = MEADOW.pondRim;
      ctx.lineWidth = Math.max(1, this.tile * 0.045);
      for (const [rx, ry, dy] of [[0.34, 0.13, 0.3], [0.22, 0.085, 0.36]]) {
        ctx.beginPath();
        ctx.ellipse(cx, cy + this.tile * dy, this.tile * rx, this.tile * ry, 0, 0, Math.PI * 2);
        ctx.stroke();
      }
      ctx.restore();
    }
    // Water occlusion (BACKLOG P1, the owner's idea): clip the cat against
    // the waterline so a cat standing in a pond is visibly in it, whatever
    // pose it is wearing. This is what makes the water+activity case work
    // without a second pose per activity -- a cat drinking at the edge of a
    // pond keeps its drinking pose and still reads as standing in water.
    const cut = waterlineFor(pose, wet);
    const submerged = cut !== null;
    if (submerged) {
      ctx.save();
      ctx.beginPath();
      // Generous horizontally and upward: the tail and the dispatcher's
      // 1.05x overdraw both put ink outside the nominal box, and clipping
      // is only ever meant to cut the BOTTOM off.
      ctx.rect(x - this.tile, y - this.tile * 2, this.tile * 3, this.tile * (2 + cut));
      ctx.clip();
    }
    if (tween?.sy !== undefined) {
      // The landing settle: a soft squash about the ground line, so the
      // feet stay planted (the dispatcher's overdraw anchors feet too).
      const groundY = y + 0.88 * this.tile;
      ctx.save();
      ctx.translate(0, groundY);
      ctx.scale(1, tween.sy);
      ctx.translate(0, -groundY);
    }
    const catOpts = {
      appearance: shadedAppearanceOf(appearanceFor(kitty.id), this.theme),
      facing: view.facingFor(kitty.id),
      size: this.tile,
      eyesOverride: eyes,
      earsBack: ears,
      lid,
      x,
      y,
    };
    if (tween?.blend) {
      drawCatTween(ctx, {
        ...catOpts,
        from: tween.blend.from,
        to: pose,
        t: tween.blend.t,
        phaseFrom: tween.blend.fromPhase,
        phaseTo: motion.phase,
      });
    } else {
      drawCat(ctx, { ...catOpts, pose, phase: motion.phase });
    }
    if (tween?.sy !== undefined) ctx.restore();
    if (submerged) ctx.restore();
    // The beat, the Zs and the cuddle heart all live ABOVE the water and
    // are drawn after the clip is released -- a thought bubble does not
    // get cut off because the cat it belongs to is standing in a pond.
    if (beat) this.drawBeat(beat, cx, cy, view.facingFor(kitty.id));

    if (state === 'sleeping') {
      // Drawn Zs drift up from the sleeper (spec 007 FR-008), replacing
      // the emoji wisp at the same corner.
      ctx.save();
      ctx.globalAlpha = 0.75;
      drawSleepZs(ctx, {
        phase: view.propPhaseFor(kitty.id, VIEW.props.zDriftMs),
        size: this.tile * 0.8,
        x: x + this.tile * 0.35,
        y: y - this.tile * 0.5,
      });
      ctx.restore();
    }

    // Cuddling cats get a little heart between them -- at their eased
    // positions, so it floats where the cats visibly are; it beats on the
    // drawn kitty's own clock (spec 007 FR-008).
    const partner = kitty.activity?.with_friend;
    if (partner !== undefined && partner !== null) {
      const friend = world.kitties.find((k) => k.id === partner);
      if (friend) {
        const fpos = view.posFor(friend);
        const fx = (fpos.x + 0.5) * this.tile;
        const fy = (fpos.y + 0.5) * this.tile;
        const heartSize = this.tile * 0.5;
        drawHeart(ctx, {
          phase: view.propPhaseFor(kitty.id, VIEW.props.heartPulseMs),
          size: heartSize,
          x: (cx + fx) / 2 - heartSize / 2,
          y: (cy + fy) / 2 - this.tile * 0.15 - heartSize / 2,
        });
      }
    }

    if (this.showHappiness) this.drawHappinessBar(kitty, x, y, view);
  }

  /**
   * One-shot beats (US5): short presentational sequences beside the cat.
   * The plaything is deliberately unlike every real element (FR-009) --
   * a twinkling star, where the world's things are emoji and tiles.
   */
  drawBeat(beat, cx, cy, facing) {
    const ctx = this.ctx;
    const dir = facing === 'right' ? 1 : -1;
    if (beat.kind === 'sparkle') {
      // Relief: little golden twinkles rising beside the kitty (FR-011).
      ctx.save();
      ctx.globalAlpha = 1 - beat.t;
      const rise = beat.t * this.tile * 0.5;
      this.star(cx + dir * this.tile * 0.35, cy - this.tile * 0.35 - rise, this.tile * 0.1, '#f4c95d');
      this.star(cx - dir * this.tile * 0.18, cy - this.tile * 0.55 - rise * 0.7, this.tile * 0.065, '#f8dc9a');
      ctx.restore();
    } else if (beat.kind === 'plaything') {
      // Solo play: the imaginary quarry hops with the pounce and twinkles
      // out of existence when the game ends.
      ctx.save();
      const hop = Math.sin(beat.t * Math.PI) * this.tile * 0.35;
      const px = cx + dir * this.tile * 0.55;
      const py = cy - this.tile * 0.08 - hop;
      ctx.globalAlpha = 0.9;
      const twinkle = 0.8 + 0.2 * Math.sin(beat.t * 6 * Math.PI);
      this.star(px, py, this.tile * 0.13 * twinkle, '#ffd97a');
      ctx.globalAlpha = 0.5;
      this.star(px + dir * this.tile * 0.14, py + this.tile * 0.12, this.tile * 0.06, '#ffe9b5');
      ctx.restore();
    }
    // 'sad' draws nothing extra: the droop is worn on the cat itself.
  }

  /** A little four-point star -- the beat vocabulary's one glyph. */
  star(cx, cy, r, color) {
    const ctx = this.ctx;
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.moveTo(cx, cy - r);
    ctx.quadraticCurveTo(cx, cy, cx + r, cy);
    ctx.quadraticCurveTo(cx, cy, cx, cy + r);
    ctx.quadraticCurveTo(cx, cy, cx - r, cy);
    ctx.quadraticCurveTo(cx, cy, cx, cy - r);
    ctx.closePath();
    ctx.fill();
  }

  /**
   * The in-world twin of the panel's gentle cue (US5, FR-012): one soft
   * thought bubble with the long-wanted need's icon, above the kitty and
   * clear of its speech bubble.
   */
  drawThought(kitty, need, view) {
    const ctx = this.ctx;
    const { x, y } = this.tileOrigin(view.posFor(kitty));
    const r = this.tile * 0.34;
    let bx = x + this.tile * 1.05;
    bx = Math.min(bx, this.canvas.clientWidth - r - 2);
    const by = Math.max(r + 2, y - this.tile * 0.55);

    ctx.save();
    ctx.fillStyle = 'rgba(255, 253, 250, 0.92)';
    ctx.strokeStyle = 'rgba(150, 125, 105, 0.28)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.arc(bx, by, r, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
    // The trail of little thought-dots down toward the kitty's head.
    const headX = x + this.tile * 0.6;
    const headY = y + this.tile * 0.2;
    for (const [k, dr] of [[0.55, 0.12], [0.8, 0.07]]) {
      ctx.beginPath();
      ctx.arc(bx + (headX - bx) * k, by + (headY - by) * k, this.tile * dr, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
    }
    // The wanted need as its drawn mini-prop (spec 007 FR-009) -- the same
    // vocabulary the world uses, at bubble scale.
    const iconSize = r * 1.5;
    drawNeedIcon(ctx, { need, size: iconSize, x: bx - iconSize / 2, y: by - iconSize / 2 });
    ctx.restore();
  }

  drawHappinessBar(kitty, x, y, view) {
    const ctx = this.ctx;
    const width = this.tile - 6;
    const height = 3;
    const bx = x + 3;
    const by = y + this.tile - 3.5;
    // Eased toward the served value on the shared progress clock (US6) --
    // the color reads the true value, never the blend.
    const value = view.barValueFor(kitty);

    ctx.fillStyle = 'rgba(255, 255, 255, 0.75)';
    ctx.fillRect(bx, by, width, height);
    ctx.fillStyle = happinessColor(kitty.happiness);
    ctx.fillRect(bx, by, width * clamp01(value / 100), height);
  }

  drawBubbles(world, view) {
    const recent = (world.recent_meows || []).filter(
      (m) => m.tick > world.tick - BUBBLE_TICKS,
    );
    // One bubble per cat: the newest thing they said.
    const newest = new Map();
    for (const meow of recent) newest.set(meow.kitty_id, meow);

    for (const meow of newest.values()) {
      const kitty = world.kitties.find((k) => k.id === meow.kitty_id);
      if (!kitty) continue;
      this.drawBubble(kitty, MEOW_TEXT[meow.kind] || '…', view, meow);
    }
  }

  drawBubble(kitty, text, view, meow) {
    const ctx = this.ctx;
    const { x, y } = this.tileOrigin(view.posFor(kitty));
    ctx.font = '600 11px ui-rounded, system-ui, sans-serif';
    const padding = 6;
    const width = ctx.measureText(text).width + padding * 2;
    const height = 18;

    // Keep the bubble on screen even for cats hugging the edges.
    let bx = x + this.tile / 2 - width / 2;
    bx = Math.max(2, Math.min(bx, this.canvas.clientWidth - width - 2));
    const by = Math.max(2, y - height - 4);

    // A fresh meow pops in with a small settle (US6); older bubbles and
    // reduced motion render at full size instantly.
    const scale = view.bubbleScaleFor(meow);
    ctx.save();
    if (scale !== 1) {
      const ax = x + this.tile / 2;
      const ay = by + height;
      ctx.translate(ax, ay);
      ctx.scale(scale, scale);
      ctx.translate(-ax, -ay);
    }

    ctx.fillStyle = 'rgba(255, 253, 250, 0.96)';
    ctx.strokeStyle = 'rgba(150, 125, 105, 0.28)';
    ctx.lineWidth = 1;
    this.roundRect(bx, by, width, height, 9);
    ctx.fill();
    ctx.stroke();

    // Tail.
    ctx.beginPath();
    ctx.moveTo(x + this.tile / 2 - 3, by + height - 1);
    ctx.lineTo(x + this.tile / 2, by + height + 4);
    ctx.lineTo(x + this.tile / 2 + 3, by + height - 1);
    ctx.closePath();
    ctx.fillStyle = 'rgba(255, 253, 250, 0.96)';
    ctx.fill();

    ctx.fillStyle = '#6b5a4e';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, bx + padding, by + height / 2);
    ctx.restore();
  }

  // ---- small helpers ----

  tileOrigin(pos) {
    return { x: pos.x * this.tile, y: pos.y * this.tile };
  }

  // (The emoji() helper is gone -- spec 007 FR-010: with every world glyph
  // drawn parametrically, deleting it makes "zero emoji on the canvas"
  // structural rather than aspirational.)

  roundRect(x, y, w, h, r) {
    const ctx = this.ctx;
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
  }
}

function happinessColor(happiness) {
  if (happiness >= 70) return '#8fce8f';
  if (happiness >= 40) return '#f3cf7a';
  return '#efa98b';
}

function clamp01(value) {
  return Math.max(0, Math.min(1, value));
}
