// Crossing probe. Stubs the socket so the world clock is ours, then walks a
// real day->dusk crossing under each condition while counting dropped frames.
//
// WHAT THIS MEASURES NOW. The cross-fade has landed, so the no-flag baseline
// IS the shipped renderer: two bakes per crossing, composited per frame. The
// sustained jank this rig was built to find is gone (32-47% of frames over
// 20ms -> 0.5-0.8%, against a frozen ceiling of 0.3-0.8%).
//
// What is left is ONE stall, ~400ms, when a theme is baked. Section 6.3 puts
// that bake in the lull before a crossing rather than inside it, which moves
// the stall somewhere harmless but does not remove it -- and nothing shrinks
// it. The 2048 cap bought 13%, baking one theme instead of two bought 5%,
// spreading it over frames bought nothing, and only 8-17ms of the frame is
// inside the draw calls at all. A cost indifferent to area, to volume and to
// JS timers is not a cost in JavaScript.
//
// THE HYPOTHESIS UNDER TEST (section 7): Safari defers an offscreen canvas's
// rasterization until something draws FROM it. If that is right, the bake in
// the lull is cheap and the stall is really the FIRST BLIT, landing wherever
// the crossing first composites -- and the fix is to blit each layer once, in
// the lull, on purpose. `lull: 'blit'` does exactly that and nothing else.
//
// `renderer` is a top-level const in a classic script, so it is a global
// LEXICAL binding and not a property of window. Reach it bare.
(() => {
  const M = (window.__probe = { rows: [], done: false });
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
  let blitAfterBake = false;
  let warmSide = 0;
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
      const before = renderer.groundLayers.size;
      const built = real(...a);
      // Only a MISS did any baking. A hit must not be charged for a blit it
      // would never have done -- and, more importantly, a lull row that HITS
      // measured nothing at all and has to say so.
      if (renderer.groundLayers.size !== before) {
        warmSide = built.under ? built.under.width : 0;
        if (blitAfterBake) forceRaster(built);
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
    scale = 1, device = 0, flat = false, freeze = false, lull = null }) {
    setTransitions(transitions);
    setBlur(blur);
    reuseCanvases = reuse;
    bakeScale = scale;
    flatBake = flat;
    targetDevice = device;
    frozen = false;
    blitAfterBake = false;
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

    // The settle leaves the quiet hour baked -- and `app.js` prewarms the NEXT
    // phase during a lull, so dusk is warm too. Drop dusk on purpose: the
    // measurement is the bake of ONE theme against a cache that already holds
    // the current one, which is what section 6.3 ships, and it has to land
    // inside the counter rather than before it.
    if (lull) {
      for (const k of [...renderer.groundLayers.keys()]) {
        if (k.startsWith('dusk|')) renderer.groundLayers.delete(k);
      }
    }
    frozen = freeze;

    const g0 = { ...wrapped.ground }, p0 = { ...wrapped.pond };
    const frames = [];
    let last = performance.now(), stop = false;
    const tick = () => { const n = performance.now(); frames.push(n - last); last = n; if (!stop) requestAnimationFrame(tick); };
    requestAnimationFrame(tick);

    // The lull bake, inside the counter and before the crossing: exactly what
    // `app.js` does when it sees a quiet tick and warms the next phase.
    if (lull) {
      blitAfterBake = lull === 'blit';
      renderer.warmGroundLayers(world, 'dusk');
      blitAfterBake = false;
      await nextFrame();
    }

    for (let t = FROM; t <= TO; t++) {
      for (const s of sockets) s.fire('message', { data: JSON.stringify({ ...world, tick: t }) });
      await new Promise(r => setTimeout(r, TICK_MS));
    }
    stop = true;
    if (lull && !warmSide) {
      throw new Error(`${label}: the lull bake was a cache HIT -- nothing was baked inside the counter, `
        + 'so this row measures nothing. The settle tick or the dusk eviction is wrong.');
    }
    const over = (ms) => frames.filter(f => f > ms).length;
    const row = {
      label,
      frames: frames.length,
      janky: over(20), bad: over(33), worst: Math.round(Math.max(0, ...frames)),
      side: firstSide,
      warmSide,
      bakeMs: +(wrapped.ground.ms - g0.ms).toFixed(0),
      pondMs: +(wrapped.pond.ms - p0.ms).toFixed(0),
    };
    M.rows.push(row);
    render();
    await new Promise(r => setTimeout(r, 1200));
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
      + '<td style="padding-left:14px">device px</td><td style="padding-left:14px">in canvas</td></tr>'
      + M.rows.map(r => `<tr><td>${r.label}</td>`
        + `<td style="padding-left:14px;text-align:right">${r.frames}</td>`
        + `<td style="padding-left:14px;text-align:right">${r.janky} (${pct(r)}%)</td>`
        + `<td style="padding-left:14px;text-align:right">${r.bad}</td>`
        + `<td style="padding-left:14px;text-align:right">${r.worst}ms</td>`
        + `<td style="padding-left:14px;text-align:right">${r.side}`
        + `${r.warmSide && r.warmSide !== r.side ? `<span style="color:#b4462f"> ⚠warm ${r.warmSide}</span>` : ''}</td>`
        + `<td style="padding-left:14px;text-align:right">${r.bakeMs + r.pondMs}ms</td></tr>`).join('')
      + '</table>'
      + (M.done ? '<div style="margin-top:8px;color:#3f7a45">done — read WORST on the two lull rows against each other, then both against the baselines either side</div>'
                : '<div style="margin-top:8px;color:#9c8a7c">running… ~12s per row, seven rows (~1.5 min). WORST is the column that matters here. KEEP THE SCREEN AWAKE.</div>');
  }

  window.__runProbe = async (world) => {
    installFreeze();
    installLullInstrument();
    installBakeScale();
    render();
    // Every treatment is bracketed by a baseline. If the baselines hold
    // steady the treatments are comparable; if they drift, the drift is
    // visible instead of being silently attributed to the treatment.
    await condition(world, 'baseline 1', {});
    await condition(world, '  LULL BAKE (as shipped)', { lull: 'plain' });
    await condition(world, 'baseline 2', {});
    await condition(world, '  LULL BAKE + blit each layer once', { lull: 'blit' });
    await condition(world, 'baseline 3', {});
    await condition(world, '  FROZEN (the ceiling)', { freeze: true });
    await condition(world, 'baseline 4', {});
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
