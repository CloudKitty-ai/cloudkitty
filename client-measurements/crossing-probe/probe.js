// Crossing probe. Stubs the socket so the world clock is ours, then walks a
// real day->dusk crossing under each condition while counting dropped frames.
//
// WHAT THIS MEASURES NOW. The cross-fade has landed, so the no-flag baseline
// IS the shipped renderer: two bakes per crossing, composited per frame. The
// sustained jank this rig was built to find is gone (32-47% of frames over
// 20ms -> 0.5-0.8%, against a frozen ceiling of 0.3-0.8%).
//
// ⚠ THE ~400ms STALL DOES NOT EXIST. This file used to open by asserting it
// did, and by naming a Safari-defers-rasterization hypothesis that was going
// to explain it. Both are withdrawn (CROSSING-BAKES section 7, 2026-09-21).
// Measured directly, 12 reps against a control, the frame that bakes a theme
// costs 18ms against a control's 17. The ~400ms was the `worst` column --
// ONE sample of ~660 -- reading this device's outlier tail, which the same
// runs put at 122-177ms with nothing baking. `stallRow` below is the
// instrument that settled it; read its control row first.
//
// THE OPEN QUESTION (2026-09-21): `drawGroundLean` draws the grass blades and
// the flower stems live, on EVERY frame, because they lean with the sun and a
// baked lean cross-dissolves into a ghost. Its JavaScript costs 37us/frame in
// headless Chrome -- but Safari records 2D canvas commands and rasterizes
// them elsewhere, so that number is command-building and not the cost. The
// lean sweep measures it the only way that works here: by frame time, in
// BLOCKS within one run, at 0, 1 and 8 draws per frame. 8 is for slope --
// if 1x cannot be resolved against 0x, 8x still bounds it.
//
// `renderer` is a top-level const in a classic script, so it is a global
// LEXICAL binding and not a property of window. Reach it bare.
(() => {
  const M = (window.__probe = { rows: [], stalls: [], done: false });
  const wrapped = { ground: { n: 0, ms: 0 }, pond: { n: 0, ms: 0 } };

  // --- canvas pool -------------------------------------------------------
  // Only the DISPOSABLE canvases: the blur scratch inside blurredLayer and
  // the four inside buildPondLayers. Setting .width reallocates the backing
  // store, which is the cost under test, so an unchanged size clears instead.
  let pooling = false;
  const pool = new Map();
  const counters = new Map();
  const realCreate = document.createElement.bind(document);
  const nativeDim = {
    width: Object.getOwnPropertyDescriptor(HTMLCanvasElement.prototype, 'width'),
    height: Object.getOwnPropertyDescriptor(HTMLCanvasElement.prototype, 'height'),
  };
  function poolCanvas() {
    const c = realCreate('canvas');
    for (const dim of ['width', 'height']) {
      const d = nativeDim[dim];
      Object.defineProperty(c, dim, {
        configurable: true,
        get() { return d.get.call(this); },
        set(v) { if (d.get.call(this) === v) { this.__dirty = true; return; } d.set.call(this, v); },
      });
    }
    const realGet = c.getContext.bind(c);
    c.getContext = (...a) => {
      const g = realGet(...a);
      if (c.__dirty && g) { g.setTransform(1, 0, 0, 1, 0, 0); g.clearRect(0, 0, c.width, c.height); c.__dirty = false; }
      return g;
    };
    return c;
  }
  function beginPooling() { pooling = true; counters.clear(); }
  function endPooling() { pooling = false; }
  document.createElement = function (tag, ...rest) {
    if (!pooling || String(tag).toLowerCase() !== 'canvas') return realCreate(tag, ...rest);
    const n = (counters.get('c') || 0); counters.set('c', n + 1);
    let list = pool.get('c'); if (!list) { list = []; pool.set('c', list); }
    if (!list[n]) list[n] = poolCanvas();
    return list[n];
  };

  let reuseCanvases = false;
  // A FLAT bake: same canvas, same size, but the content is one fillRect
  // instead of ~1200 fills plus the scatter and the blur. If the jank
  // survives this, the cost is producing and uploading the image, and no
  // amount of drawing faster will touch it.
  let flatBake = false;
  let lastGroundOpts = null;
  let lastPondArgs = null;
  let firstSide = 0;

  for (const [name, slot] of [['drawMeadowGround', 'ground'], ['buildPondLayers', 'pond']]) {
    const real = window[name];
    if (typeof real !== 'function') continue;
    window[name] = function (...a) {
      const t0 = performance.now();
      if (reuseCanvases) beginPooling();
      try {
        if (slot === 'ground') lastGroundOpts = a[1];
        if (slot === 'pond') lastPondArgs = a;
        if (flatBake) {
          if (slot === 'ground') {
            const [ctx, o] = a;
            ctx.fillStyle = MEADOW.grassTones ? MEADOW.grassTones[0] : '#e9f3e1';
            ctx.fillRect(0, 0, o.width * o.tile, o.height * o.tile);
            return undefined;
          }
          return { shore: null, lip: null };
        }
        return real.apply(this, a);
      } finally {
        endPooling();
        if (!firstSide && slot === 'ground' && a[1]) {
          firstSide = Math.round(a[1].width * a[1].tile * (renderer.dpr || devicePixelRatio || 1));
        }
        wrapped[slot].ms += performance.now() - t0;
        wrapped[slot].n++;
      }
    };
  }

  const sockets = [];
  window.WebSocket = class {
    constructor() { this.readyState = 1; this.l = {}; sockets.push(this); setTimeout(() => this.fire('open', {}), 0); }
    addEventListener(t, fn) { (this.l[t] ||= []).push(fn); }
    fire(t, e) { for (const fn of this.l[t] || []) fn(e); }
    send() {} close() {}
  };

  // --- the ceiling ---------------------------------------------------------
  // The pre-cross-fade rig froze `groundCache` and `paletteKey` separately, to
  // attribute cost between the ground and the pond. That question is answered
  // and closed -- both mattered, and the cross-fade removed both -- and those
  // two fields no longer exist. What is still worth having is the FLOOR: the
  // same crossing with nothing baking and nothing compositing, so a treatment
  // has something to be compared against that is not another treatment.
  //
  // Frozen pins `renderer.blend` at null, which is the state `blitGround` and
  // the pond path already fall back to before the page has a clock: one hour,
  // one blit, no pair. Both layer providers are then memoized so the first
  // bake of the run lands normally and no later one can.
  let frozen = false;
  function installFreeze() {
    let heldBlend = renderer.blend;
    Object.defineProperty(renderer, 'blend', {
      configurable: true,
      get: () => (frozen ? null : heldBlend),
      set: (v) => { heldBlend = v; },
    });
    const realGround = renderer.groundLayersFor.bind(renderer);
    let heldGround = null;
    renderer.groundLayersFor = (...a) => {
      if (frozen && heldGround) return heldGround;
      const built = realGround(...a);
      heldGround = built;
      return built;
    };
    const realPond = renderer.pondLayersFor.bind(renderer);
    let heldPond = null;
    renderer.pondLayersFor = (...a) => {
      if (frozen && heldPond) return heldPond;
      const built = realPond(...a);
      heldPond = built;
      return built;
    };
  }

  // --- the blit, which is the whole experiment -----------------------------
  // Draw the entire freshly-baked layer down into a 1x1 scratch. Nothing is
  // shown and the destination work is a single pixel, so anything this costs
  // is the SOURCE being made real. Scaling the whole canvas into that pixel
  // is deliberate: sampling one texel might let a tile-based rasterizer
  // realise one tile and defer the rest.
  let warmSide = 0;
  // Scoped to the lull call itself. A counter that any bake anywhere in the
  // counted window can satisfy proves nothing -- the crossing bakes too, so
  // the row passes while the lull did nothing. Measured: it does.
  let inLull = false;
  let lullBakes = 0;
  const scratch = document.createElement('canvas');
  scratch.width = 1; scratch.height = 1;
  const scratchCtx = scratch.getContext('2d');
  function forceRaster(layers) {
    if (!layers) return;
    for (const c of [layers.under, layers.over, layers.shore, layers.lip]) {
      if (c && c.width) scratchCtx.drawImage(c, 0, 0, c.width, c.height, 0, 0, 1, 1);
    }
  }
  function installLullInstrument() {
    const real = renderer.groundLayersFor.bind(renderer);
    renderer.groundLayersFor = (...a) => {
      const n0 = wrapped.ground.n;
      const built = real(...a);
      // A real bake calls drawMeadowGround twice, once per layer. Cache SIZE
      // cannot detect it: the provider evicts down to the cap before it
      // inserts, so a miss on a full cache leaves the size exactly where it
      // was. That read blind for every row after the cache filled.
      //
      // Only a bake may be charged for a blit it would otherwise not have
      // done -- and a lull row that HIT measured nothing and has to say so.
      if (wrapped.ground.n !== n0 && inLull) {
        lullBakes++;
        warmSide = built.under ? built.under.width : 0;
      }
      return built;
    };
  }

  const setTransitions = (on) => { document.body.style.transitionProperty = on ? '' : 'none'; };
  const BLUR_DIALS = { groundBlurTiles: 0.32, pondDepthBlurTiles: null, pondLipBlurTiles: null };
  const setBlur = (on) => {
    const base = VIEW.meadow || {};
    if (BLUR_DIALS.pondDepthBlurTiles === null) {
      BLUR_DIALS.groundBlurTiles = base.groundBlurTiles;
      BLUR_DIALS.pondDepthBlurTiles = base.pondDepthBlurTiles;
      BLUR_DIALS.pondLipBlurTiles = base.pondLipBlurTiles;
    }
    VIEW.meadow = { ...base,
      groundBlurTiles: on ? BLUR_DIALS.groundBlurTiles : 0,
      pondDepthBlurTiles: on ? BLUR_DIALS.pondDepthBlurTiles : 0,
      pondLipBlurTiles: on ? BLUR_DIALS.pondLipBlurTiles : 0 };
  };

  // Shrinking the bake keeps the COMMAND COUNT identical (still 400 tiles,
  // still the same scatter) while quartering the pixels. Rasterization and
  // upload scale with pixels; the command list does not.
  let bakeScale = 1;
  let targetDevice = 0;   // device px per side; 0 = leave the shipped clamp alone
  function installBakeScale() {
    for (const m of ['bakeTileFor', 'pondBakeTileFor']) {
      const real = renderer[m] ? renderer[m].bind(renderer) : Object.getPrototypeOf(renderer)[m].bind(renderer);
      renderer[m] = (...a) => {
        const t = real(...a);
        if (!targetDevice) return t * bakeScale;
        const world = a[0];
        const dpr = renderer.dpr || window.devicePixelRatio || 1;
        const widest = Math.max(world.width, world.height);
        return Math.min(t, targetDevice / dpr / widest);
      };
    }
  }

  // --- the lean sweep ----------------------------------------------------
  // `drawGroundLean` is a function DECLARATION in a classic script, so it is
  // a property of window and reassigning it changes what render.js's bare
  // call resolves to. Same trick as drawMeadowGround above.
  //
  // Blocks, not alternate frames. Safari hands the command list to another
  // process, so a frame's raster cost can land in the NEXT frame's rAF delta;
  // strict alternation would smear the treatment across both populations.
  // A block lets the pipeline reach steady state, and the first LEAN_SETTLE
  // frames after each switch are dropped for the same reason.
  const LEAN_LEVELS = [0, 1, 8];
  const LEAN_BLOCK = 12;
  const LEAN_SETTLE = 2;
  let leanRepeats = 1;
  // Counted, per level, because the whole failure mode of this row is that it
  // measures nothing and reports three identical medians as "below the noise
  // floor". If the wrapper never fires -- render.js stops calling it, the name
  // stops being global, the sweep never rotates -- the numbers still come out
  // and still look like an answer. The tally below turns that into a refusal.
  const leanCalls = new Map();
  function installLeanInstrument() {
    const real = window.drawGroundLean;
    if (typeof real !== 'function') {
      throw new Error('drawGroundLean is not on window -- the renderer moved it, and the lean sweep would silently measure nothing');
    }
    // Counted at the point of WORK, not the point of intent. Counting
    // `+= leanRepeats` up front looks equivalent and is not: it tallies what
    // the loop meant to do, so a loop that draws anyway at level 0 still
    // reports zero draws and the guard waves it through. That exact mutation
    // came back green once.
    const counted = function (...a) {
      leanCalls.set(leanRepeats, (leanCalls.get(leanRepeats) || 0) + 1);
      return real.apply(this, a);
    };
    window.drawGroundLean = function (...a) {
      for (let i = 0; i < leanRepeats; i++) counted.apply(this, a);
    };
  }

  const nextFrame = () => new Promise(r => requestAnimationFrame(r));
  const TICK_MS = 800;
  const FROM = 256, TO = 269;   // 13 ticks of the day -> dusk fade
  // A settled day hour, before the fade opens. Settling at FROM instead put
  // the settle INSIDE the crossing, where the renderer already holds both
  // themes -- so the lull bake was a cache hit and every row measured the
  // same nothing. The rig reported `warm 0` and `in canvas 0ms` and that is
  // how it was caught; the guard below now refuses the row outright.
  const QUIET = 248;

  async function condition(world, label, { transitions = true, blur = true, reuse = false,
    scale = 1, device = 0, flat = false, freeze = false, leanSweep = false }) {
    setTransitions(transitions);
    setBlur(blur);
    reuseCanvases = reuse;
    bakeScale = scale;
    flatBake = flat;
    targetDevice = device;
    frozen = false;
    firstSide = 0;
    warmSide = 0;
    renderer.groundLayers = new Map();
    renderer.pondCache = null;

    // Settle the bake size BEFORE anything is warmed or counted. The layer key
    // carries the bake tile, and `device`/`scale` move it, so warming against
    // a stale tile keys every layer at the wrong size -- the burst we believe
    // we measured is thrown away and happens again, lazily, inside the
    // crossing. That bug invalidated a whole run once.
    //
    // Wait for the DRAW, never for a duration. A fixed delay is a guess about
    // frame time, and frame time here is the thing under measurement: 32ms
    // spanned a frame in Chrome and did not on the phone, where a baseline
    // frame runs 20-170ms. Nulling the opts first means a settle that never
    // lands leaves the row reporting warm 0 -- loud, not quietly wrong.
    lastGroundOpts = null; lastPondArgs = null;
    for (const s of sockets) s.fire('message', { data: JSON.stringify({ ...world, tick: QUIET }) });
    const deadline = performance.now() + 4000;
    while (!(lastGroundOpts && lastPondArgs) && performance.now() < deadline) await nextFrame();

    frozen = freeze;

    const g0 = { ...wrapped.ground }, p0 = { ...wrapped.pond };
    // Frames are tagged with whether a bake happened inside them. That is the
    // within-row control this rig needed all along: `worst` compares a
    // treatment against a different run, where this device's outlier tail
    // swamps it, but a baked frame and a quiet frame from the SAME run are
    // paired by construction.
    const frames = [];
    const bakeFrames = [];
    const leanTags = [];
    let blockFrame = 0, levelIdx = 0;
    if (leanSweep) { levelIdx = 0; leanRepeats = LEAN_LEVELS[0]; leanCalls.clear(); }
    let last = performance.now(), stop = false, lastN = wrapped.ground.n;
    const tick = () => {
      const n = performance.now();
      const dur = n - last;
      frames.push(dur);
      // Tag with the level that was in force DURING this frame, before the
      // rotation below moves it on.
      if (leanSweep) leanTags.push({ level: leanRepeats, pos: blockFrame, dur });
      if (wrapped.ground.n !== lastN) { bakeFrames.push(Math.round(dur)); lastN = wrapped.ground.n; }
      last = n;
      if (leanSweep) {
        blockFrame += 1;
        if (blockFrame >= LEAN_BLOCK) {
          blockFrame = 0;
          levelIdx = (levelIdx + 1) % LEAN_LEVELS.length;
          leanRepeats = LEAN_LEVELS[levelIdx];
        }
      }
      if (!stop) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);

    for (let t = FROM; t <= TO; t++) {
      for (const s of sockets) s.fire('message', { data: JSON.stringify({ ...world, tick: t }) });
      await new Promise(r => setTimeout(r, TICK_MS));
    }
    stop = true;
    leanRepeats = 1;
    const pct50 = (xs) => { const s2 = [...xs].sort((a, b) => a - b); return s2.length ? +s2[Math.floor(s2.length * 0.5)].toFixed(2) : 0; };
    const pct90 = (xs) => { const s2 = [...xs].sort((a, b) => a - b); return s2.length ? +s2[Math.floor(s2.length * 0.9)].toFixed(2) : 0; };
    if (leanSweep) {
      const drew = (lvl) => leanCalls.get(lvl) || 0;
      if (drew(0) !== 0) {
        throw new Error(`${label}: level 0 drew the lean ${drew(0)} times -- the skip does not skip, so every level is the same condition`);
      }
      if (!drew(1) || !drew(8)) {
        throw new Error(`${label}: the lean wrapper did not fire (1x drew ${drew(1)}, 8x drew ${drew(8)}). `
          + 'render.js is not reaching window.drawGroundLean, and this row measures nothing.');
      }
      // Per FRAME the ratio is 8; per row it is 8x the frame ratio, and the
      // blocks are equal length, so the call ratio lands near 8 as well. Loose
      // bounds: this is catching "the sweep never rotated", not drift.
      const ratio = drew(8) / drew(1);
      if (ratio < 4 || ratio > 16) {
        throw new Error(`${label}: 8x drew ${ratio.toFixed(1)}x what 1x drew, not ~8 -- the block rotation is wrong`);
      }
    }
    const lean = leanSweep ? LEAN_LEVELS.map((level) => {
      // Steady-state frames only: the first LEAN_SETTLE of each block are the
      // pipeline catching up with the switch, not the treatment.
      const d = leanTags.filter(x => x.level === level && x.pos >= LEAN_SETTLE).map(x => x.dur);
      return { level, n: d.length, med: pct50(d), p90: pct90(d) };
    }) : null;
    const over = (ms) => frames.filter(f => f > ms).length;
    // p99 over the whole row: the shape of a typical bad frame, which `worst`
    // (the single maximum) cannot show. Bake frames are at most a handful of
    // 660 and do not move it.
    const sorted = [...frames].sort((a, b) => a - b);
    const row = {
      label,
      frames: frames.length,
      janky: over(20), bad: over(33), worst: Math.round(Math.max(0, ...frames)),
      bakeFrames,
      p99: Math.round(sorted[Math.floor(sorted.length * 0.99)] || 0),
      side: firstSide,
      warmSide,
      bakeMs: +(wrapped.ground.ms - g0.ms).toFixed(0),
      pondMs: +(wrapped.pond.ms - p0.ms).toFixed(0),
      lean,
    };
    M.rows.push(row);
    render();
    await new Promise(r => setTimeout(r, 1200));
    return row;
  }


  // --- the stall, measured directly ------------------------------------
  // The crossing rows cannot see this. A bake is ONE frame, `worst` is one
  // sample out of ~660, and the phone throws 350ms outliers unprompted --
  // measured: the FROZEN row, with nothing baking and nothing compositing,
  // came back at 351ms against baselines climbing 171 -> 353. Every number
  // that column has ever reported about the stall is one draw from that
  // distribution.
  //
  // So measure the bake frame itself, many times, against a control that
  // does the same nothing. Two intervals per repetition:
  //
  //   W -- the frame containing the bake
  //   D -- the next frame, containing the first DRAW from what was baked
  //
  // Section 7 predicts the cost sits in whichever of those two first touches
  // the pixels. If Safari defers rasterization until something draws from an
  // offscreen, then plain gives small W and large D, blitting at bake time
  // gives large W and small D, and W+D barely moves. If instead the bake is
  // simply expensive, W is large either way and D is small either way.
  const REPS = 12;
  function evictTheme(theme) {
    for (const k of [...renderer.groundLayers.keys()]) {
      if (k.startsWith(`${theme}|`)) renderer.groundLayers.delete(k);
    }
  }
  const median = (xs) => {
    const a = [...xs].sort((x, y) => x - y);
    return a.length ? +a[Math.floor(a.length / 2)].toFixed(0) : 0;
  };
  const top = (xs) => (xs.length ? +Math.max(...xs).toFixed(0) : 0);

  async function stallRow(world, label, { bake = true, blit = false }) {
    // The crossing rows leave their flags set, and the ceiling leaves `frozen`
    // true -- under which the layer provider is memoized and NOTHING can bake,
    // so every repetition is a cache hit. Caught by the guard below rather
    // than reported as a very fast bake.
    frozen = false;
    flatBake = false;
    reuseCanvases = false;
    targetDevice = 0;
    bakeScale = 1;
    const W = [], D = [];
    for (let i = 0; i < REPS; i++) {
      await nextFrame();
      // Start on a fresh frame so the interval is ours, not the tail of the
      // previous one.
      await nextFrame();
      let layers = null;
      const t0 = performance.now();
      if (bake) {
        // Evict INSIDE the measured window. Evicting before the two settling
        // frames does not work: the render loop composites the crossing from
        // this very cache, so it refills the entry within a frame and the
        // measured call is a hit. The delete itself is a Map operation and
        // costs nothing against a bake.
        evictTheme('dusk');
        inLull = true; lullBakes = 0;
        const draws0 = wrapped.ground.n;
        layers = renderer.groundLayersFor(world, 'dusk', renderer.bakeTileFor(world),
          renderer.dpr || devicePixelRatio || 1);
        inLull = false;
        if (!lullBakes) {
          throw new Error(`${label}: rep ${i} baked nothing -- ${wrapped.ground.n - draws0} draws, `
            + `keys [${[...renderer.groundLayers.keys()].join(', ')}], frozen=${frozen}`);
        }
        if (blit) forceRaster(layers);
      }
      await nextFrame();
      const t1 = performance.now();
      if (bake) forceRaster(layers);
      await nextFrame();
      const t2 = performance.now();
      W.push(t1 - t0);
      D.push(t2 - t1);
    }
    const row = { label, reps: REPS, wMed: median(W), wMax: top(W), dMed: median(D), dMax: top(D),
      sumMed: median(W.map((w, i) => w + D[i])) };
    M.stalls.push(row);
    render();
    return row;
  }

  function render() {
    let el = document.getElementById('probe-panel');
    if (!el) {
      el = document.createElement('div');
      el.id = 'probe-panel';
      const narrow = Math.min(window.innerWidth, window.innerHeight) < 500;
      el.style.cssText = 'position:fixed;left:6px;top:6px;right:6px;z-index:99999;background:#fffdfa;color:#3b3229;'
        + `font:${narrow ? 10 : 12}px ui-monospace,Menlo,monospace;padding:10px 12px;border:1px solid #d8c9b4;`
        + 'border-radius:10px;box-shadow:0 6px 24px rgba(120,100,80,.25);overflow-x:auto;'
        + '-webkit-overflow-scrolling:touch;max-height:70vh;overflow-y:auto';
      document.body.appendChild(el);
    }
    const pct = r => (100 * r.janky / r.frames).toFixed(1);
    el.innerHTML = '<b>crossing probe — day → dusk, the shipped cross-fade</b><br>'
      + `<span style="color:#9c8a7c">${navigator.userAgent.includes('Chrome') ? 'Chrome' : navigator.userAgent.includes('Safari') ? 'Safari' : '?'}`
      + ` · dpr ${devicePixelRatio}</span>`
      + '<table style="border-collapse:collapse;margin-top:8px">'
      + '<tr style="color:#9c8a7c"><td>condition</td><td style="padding-left:14px">frames</td><td style="padding-left:14px">frames&gt;20ms</td>'
      + '<td style="padding-left:14px">&gt;33ms</td><td style="padding-left:14px">worst</td>'
      + '<td style="padding-left:14px">p99</td><td style="padding-left:14px">frames that BAKED</td>'
      + '<td style="padding-left:14px">in canvas</td></tr>'
      + M.rows.map(r => `<tr><td>${r.label}</td>`
        + `<td style="padding-left:14px;text-align:right">${r.frames}</td>`
        + `<td style="padding-left:14px;text-align:right">${r.janky} (${pct(r)}%)</td>`
        + `<td style="padding-left:14px;text-align:right">${r.bad}</td>`
        + `<td style="padding-left:14px;text-align:right">${r.worst}ms</td>`
        + `<td style="padding-left:14px;text-align:right">${r.p99}ms</td>`
        + `<td style="padding-left:14px;text-align:right">${r.bakeFrames.length ? r.bakeFrames.join(', ') + 'ms' : '—'}</td>`
        + `<td style="padding-left:14px;text-align:right">${r.bakeMs + r.pondMs}ms</td></tr>`).join('')
      + '</table>'
      + (M.stalls.length ? '<div style="margin-top:10px"><b>the bake frame, measured directly</b>'
        + '<table style="border-collapse:collapse;margin-top:6px">'
        + '<tr style="color:#9c8a7c"><td>condition</td><td style="padding-left:14px">reps</td>'
        + '<td style="padding-left:14px">W median</td><td style="padding-left:14px">W max</td>'
        + '<td style="padding-left:14px">D median</td><td style="padding-left:14px">D max</td>'
        + '<td style="padding-left:14px">W+D median</td></tr>'
        + M.stalls.map(r => `<tr><td>${r.label}</td>`
          + `<td style="padding-left:14px;text-align:right">${r.reps}</td>`
          + `<td style="padding-left:14px;text-align:right">${r.wMed}ms</td>`
          + `<td style="padding-left:14px;text-align:right">${r.wMax}ms</td>`
          + `<td style="padding-left:14px;text-align:right">${r.dMed}ms</td>`
          + `<td style="padding-left:14px;text-align:right">${r.dMax}ms</td>`
          + `<td style="padding-left:14px;text-align:right">${r.sumMed}ms</td></tr>`).join('')
        + '</table><div style="margin-top:4px;color:#9c8a7c">W = the frame that bakes. '
        + 'D = the next frame, which first draws from it. Read the CONTROL first: it is '
        + 'what a frame costs when nothing happens.</div></div>' : '')
      + (() => {
        const r = M.rows.find(x => x.lean);
        if (!r) return '';
        const base = r.lean.find(l => l.level === 0);
        return '<div style="margin-top:10px"><b>drawGroundLean, by frame time</b>'
          + '<table style="border-collapse:collapse;margin-top:6px">'
          + '<tr style="color:#9c8a7c"><td>draws/frame</td><td style="padding-left:14px">frames</td>'
          + '<td style="padding-left:14px">median</td><td style="padding-left:14px">p90</td>'
          + '<td style="padding-left:14px">vs 0, per draw</td></tr>'
          + r.lean.map(l => `<tr><td>${l.level}${l.level === 1 ? ' (shipped)' : ''}</td>`
            + `<td style="padding-left:14px;text-align:right">${l.n}</td>`
            + `<td style="padding-left:14px;text-align:right">${l.med}ms</td>`
            + `<td style="padding-left:14px;text-align:right">${l.p90}ms</td>`
            + `<td style="padding-left:14px;text-align:right">${l.level && base ? ((l.med - base.med) / l.level).toFixed(3) + 'ms' : '—'}</td></tr>`).join('')
          + '</table><div style="margin-top:4px;color:#9c8a7c">Blocks of 12 frames inside ONE run, '
          + 'first 2 of each block dropped. Read the last column: 8 draws is there for slope, so if '
          + '1 cannot be resolved against 0, 8 still bounds what one costs.<br>'
          + '⚠ The lean sweep\'s row in the table above is NOT comparable to the baselines: a third '
          + 'of its frames draw the lean 8 times on purpose, so its jank columns are inflated by this '
          + 'instrument. Only this table is a read on that row.<br>'
          + 'This table is within-row and survives a drifting device; every OTHER comparison here is '
          + 'between rows. Check the two baselines against each other first -- if they disagree, the '
          + 'crossing rows and the stall table are not telling you about the treatment.</div></div>';
      })()
      + (M.done ? '<div style="margin-top:8px;color:#3f7a45">done — the lean table is the new read; the crossing rows are the standing regression check</div>'
                : '<div style="margin-top:8px;color:#9c8a7c">running… ~12s per row, seven rows (~1.5 min). KEEP THE SCREEN AWAKE.</div>');
  }

  window.__runProbe = async (world) => {
    installFreeze();
    installLullInstrument();
    installBakeScale();
    installLeanInstrument();
    render();
    // Every treatment is bracketed by a baseline. If the baselines hold
    // steady the treatments are comparable; if they drift, the drift is
    // visible instead of being silently attributed to the treatment.
    // Sustained jank, which is the thing that was actually fixed: one
    // baseline and the ceiling, enough to show it has not regressed. The
    // treatments that used to live here could not separate and are gone.
    // The shipped path bakes the incoming theme lazily, inside the fade, so
    // the baseline's own `frames that BAKED` column is the measurement: read
    // it against that same row's p99. The prewarm that used to move this bake
    // into the lull was removed once it measured below ordinary frame noise.
    await condition(world, 'baseline (as shipped)', {});
    await condition(world, '  FROZEN (the ceiling)', { freeze: true });
    await condition(world, 'baseline 2', {});
    // The stall, which needed a different instrument entirely.
    await stallRow(world, 'control (no bake)', { bake: false });
    await stallRow(world, 'bake, draw next frame', {});
    await stallRow(world, 'bake + blit, draw next frame', { blit: true });
    // The live lean pass, by frame time. Its JavaScript is 37us; what this
    // asks is what the RASTER costs, which no timer on this side can see.
    await condition(world, 'lean sweep ⚠ not comparable', { leanSweep: true });
    setTransitions(true); setBlur(true); reuseCanvases = false; frozen = false; flatBake = false;
    M.done = true;
    render();
    document.title = 'PROBE DONE';
  };

  // Self-start once the client has a world, so opening the URL is the whole
  // interaction -- no console, no clicking.
  const boot = setInterval(async () => {
    if (typeof renderer === 'undefined' || !renderer.groundLayers?.size) return;
    clearInterval(boot);
    const w = await (await fetch('/world')).json();
    window.__runProbe(w);
  }, 400);
})();
