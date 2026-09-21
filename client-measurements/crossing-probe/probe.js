// Crossing probe. Stubs the socket so the world clock is ours, then walks a
// real crossing four times over: as shipped, with the CSS token transitions
// off, with the canvas rebakes frozen, and with neither. Whichever condition
// the dropped frames follow is the cause.
//
// `renderer` is a top-level const in a classic script, so it is a global
// LEXICAL binding and not a property of window. Reach it bare.
(() => {
  const M = (window.__probe = { rows: [], done: false });
  const wrapped = { ground: { n: 0, ms: 0 }, pond: { n: 0, ms: 0 }, tokens: { n: 0, ms: 0 } };

  // --- canvas pool -------------------------------------------------------
  // Only the DISPOSABLE canvases: the blur scratch inside blurredLayer and
  // the four inside buildPondLayers. The ground cache itself has to persist,
  // so it is left alone. Setting .width reallocates the backing store, which
  // is the cost under test, so an unchanged size clears instead.
  let pooling = false;
  const pool = new Map();          // "WxH" -> canvas[]
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
    // Size is not known yet, so key on call order within this bake. Every
    // bake asks in the same order, so slot N is always the same buffer.
    const n = (counters.get('c') || 0); counters.set('c', n + 1);
    let list = pool.get('c'); if (!list) { list = []; pool.set('c', list); }
    if (!list[n]) list[n] = poolCanvas();
    return list[n];
  };

  let reuseCanvases = false;
  // A FLAT bake: same canvas, same size, rebuilt every step, but the content
  // is one fillRect instead of ~1200 fills plus the scatter and the blur.
  // If the jank survives this, the cost is producing and uploading a new
  // full-size image, and no amount of drawing faster will touch it.
  let flatBake = false;
  // The cross-fade's per-frame cost is 4 drawImages plus this wash. Zeroing
  // the wash alone says which of the two the residual is.
  let liveWash = true;
  // ---- the two-layer cross-fade, as a drop-in for drawMeadowGround --------
  // Each theme is baked ONCE into two static layers, split at the sun wash:
  //   under = tone + jitter + blur      (everything below the wash)
  //   over  = ground detail + cover     (everything above it)
  // A step then composites under_A/under_B, draws the wash at the LIVE lean,
  // and composites over_A/over_B. 184 bakes per crossing become 2, the sweep
  // stops being quantised, and nothing is drawn at reduced resolution.
  let crossfade = false;
  const layerCache = new Map();          // "theme|tile|dpr" -> {under, over}

  function makeLayer(o, paint) {
    const dpr = renderer.dpr || window.devicePixelRatio || 1;
    const c = document.createElement('canvas');
    c.width = Math.round(o.width * o.tile * dpr);
    c.height = Math.round(o.height * o.tile * dpr);
    const g = c.getContext('2d');
    g.setTransform(dpr, 0, 0, dpr, 0, 0);
    paint(g);
    return c;
  }

  function layersFor(theme, o) {
    const dpr = renderer.dpr || window.devicePixelRatio || 1;
    const key = `${theme}|${o.tile}|${dpr}`;
    let hit = layerCache.get(key);
    if (hit) return hit;
    const saved = MEADOW;
    const savedDials = VIEW.meadow;
    setMeadowPalette(theme, null, 0);          // the PURE theme, never a mix
    const t = meadowTunables();
    // under: the wash is dialled out, the detail is stubbed away
    VIEW.meadow = { ...savedDials, groundWashSun: 0, groundWashShade: 0 };
    const stubD = window.drawGroundDetail, stubC = window.drawGroundCover;
    window.drawGroundDetail = () => {};
    window.drawGroundCover = () => {};
    const under = makeLayer(o, (g) => realGround(g, { ...o, cover: false }));
    window.drawGroundDetail = stubD;
    window.drawGroundCover = stubC;
    VIEW.meadow = savedDials;
    // over: only what sits above the wash, on transparent glass
    const over = makeLayer(o, (g) => {
      stubD(g, { width: o.width, height: o.height, tile: o.tile, t });
      if (o.cover) stubC(g, { width: o.width, height: o.height, tile: o.tile, t });
    });
    MEADOW = saved;
    hit = { under, over };
    layerCache.set(key, hit);
    return hit;
  }

  // `applyTheme` writes the blend into paletteKey as "theme>next@step", which
  // is the only place the renderer can read it back from.
  function blendNow() {
    const m = /^([a-z]+)>([a-z]*)@([\d.]+)$/.exec(renderer.paletteKey || '');
    if (!m) return null;
    return { theme: m[1], next: m[2] || null, step: parseFloat(m[3]) };
  }

  function drawSunWash(ctx, w, h) {
    if (!liveWash) return;
    const t = meadowTunables();
    if (!(t.groundWashSun || t.groundWashShade)) return;
    const lean = MEADOW.shadowLean || 0;
    const sun = withAlpha(MEADOW.sunTint || MEADOW.glowCore, t.groundWashSun);
    const shade = withAlpha(MEADOW.jitterShade, t.groundWashShade);
    const dx = -Math.max(-1, Math.min(1, lean));
    const wash = ctx.createLinearGradient(w * (0.5 - dx * 0.5), 0, w * (0.5 + dx * 0.5), h);
    wash.addColorStop(0, sun);
    wash.addColorStop(0.55, withAlpha(MEADOW.sunTint || MEADOW.glowCore, 0));
    wash.addColorStop(1, shade);
    ctx.fillStyle = wash;
    ctx.fillRect(0, 0, w, h);
  }

  function crossfadeGround(g, o) {
    const b = blendNow();
    if (!b) return realGround(g, o);
    const A = layersFor(b.theme, o);
    const B = b.next ? layersFor(b.next, o) : null;
    const w = o.width * o.tile, h = o.height * o.tile;
    const pair = (pick) => {
      g.drawImage(pick(A), 0, 0, w, h);
      if (B && b.step > 0) { g.globalAlpha = b.step; g.drawImage(pick(B), 0, 0, w, h); g.globalAlpha = 1; }
    };
    pair((l) => l.under);
    drawSunWash(g, w, h);      // live, unquantised lean -- a continuous sweep
    pair((l) => l.over);
  }

  let lastGroundOpts = null, lastPondArgs = null;
  const realGround = window.drawMeadowGround;
  // ---- the same cross-fade, for the pond layers --------------------------
  // buildPondLayers returns {shore, lip, dpr}, both canvases baked from
  // MEADOW.pondShore / MEADOW.pondLip. The geometry -- pond paths, blur
  // sigma from the tunables -- owes nothing to the palette, so the pair
  // cross-fades exactly the way the ground does. Two composites per step
  // instead of four canvas allocations and eight filter:blur passes.

  // ---- can the bake be spread over frames? -------------------------------
  // The six layers (2 themes x {under, over, pond pair}) land in ONE frame if
  // they are built on demand. Spreading them one per frame only helps if
  // Safari actually rasterizes per frame rather than batching the lot on the
  // GPU thread -- which is exactly what this measures.
  const nextFrame = () => new Promise((r) => requestAnimationFrame(() => r()));

  async function prewarm(mode, themes = ['day', 'dusk'], reset = true) {
    if (reset) { layerCache.clear(); pondCacheByTheme.clear(); pondOut = null; }
    if (mode === 'none' || !lastGroundOpts || !lastPondArgs) return;
    const o = lastGroundOpts;
    const [ponds, po] = lastPondArgs;
    const water = ponds.map((q) => q.tiles.map((t) => `${t.x},${t.y}`).join(';')).join('|');
    // One unit of work per entry; 'spread' yields a frame between each.
    const units = [];
    for (const theme of themes) {
      units.push(() => layersFor(theme, o));
      units.push(() => pondLayersFor(theme, ponds, po, water));
    }
    for (const unit of units) {
      unit();
      if (mode === 'spread') { await nextFrame(); await nextFrame(); }
    }
    const firstLayer = layerCache.values().next().value;
    if (firstLayer) warmSide = firstLayer.under.width;
  }
  const pondCacheByTheme = new Map();
  let pondOut = null;

  function pondLayersFor(theme, ponds, o, water) {
    const key = `${theme}|${o.tile}|${o.widthPx}x${o.heightPx}|${water}`;
    let hit = pondCacheByTheme.get(key);
    if (hit) return hit;
    const saved = MEADOW;
    setMeadowPalette(theme, null, 0);
    hit = realPond(ponds, o);
    MEADOW = saved;
    pondCacheByTheme.set(key, hit);
    return hit;
  }

  function crossfadePond(ponds, o) {
    const b = blendNow();
    const water = ponds.map((p) => p.tiles.map((t) => `${t.x},${t.y}`).join(';')).join('|');
    if (!b) return realPond(ponds, o);
    const A = pondLayersFor(b.theme, ponds, o, water);
    const B = b.next ? pondLayersFor(b.next, ponds, o, water) : null;
    if (!pondOut || pondOut.shore.width !== o.widthPx || pondOut.shore.height !== o.heightPx) {
      const mk = () => { const c = document.createElement('canvas'); c.width = o.widthPx; c.height = o.heightPx; return c; };
      pondOut = { shore: mk(), lip: mk(), dpr: o.dpr };
    }
    for (const which of ['shore', 'lip']) {
      const g = pondOut[which].getContext('2d');
      g.setTransform(1, 0, 0, 1, 0, 0);
      g.clearRect(0, 0, o.widthPx, o.heightPx);
      g.globalAlpha = 1;
      g.drawImage(A[which], 0, 0);
      if (B && b.step > 0) { g.globalAlpha = b.step; g.drawImage(B[which], 0, 0); g.globalAlpha = 1; }
    }
    return pondOut;
  }

  const realPond = window.buildPondLayers;


  for (const [name, slot] of [['drawMeadowGround', 'ground'], ['buildPondLayers', 'pond']]) {
    const real = window[name];
    if (typeof real === 'function') {
      window[name] = function (...a) {
        const t0 = performance.now();
        if (reuseCanvases) beginPooling();
        try {
          if (slot === 'ground') lastGroundOpts = a[1];
          if (slot === 'pond') lastPondArgs = a;
          if (crossfade && slot === 'ground') { crossfadeGround(a[0], a[1]); return undefined; }
          if (crossfade && slot === 'pond') return crossfadePond(a[0], a[1]);
          if (flatBake) {
            if (slot === 'ground') {
              const [ctx, o] = a;
              ctx.fillStyle = MEADOW.grassTones ? MEADOW.grassTones[0] : '#e9f3e1';
              ctx.fillRect(0, 0, o.width * o.tile, o.height * o.tile);
              return undefined;
            }
            return { shore: null, lip: null };   // pond layers: draw nothing
          }
          return real.apply(this, a);
        }
        finally {
          endPooling();
          if (!firstSide && slot === 'ground' && a[1]) firstSide = Math.round(a[1].width * a[1].tile * (renderer.dpr || devicePixelRatio || 1));
          wrapped[slot].ms += performance.now() - t0; wrapped[slot].n++;
        }
      };
    }
  }

  const sockets = [];
  window.WebSocket = class {
    constructor() { this.readyState = 1; this.l = {}; sockets.push(this); setTimeout(() => this.fire('open', {}), 0); }
    addEventListener(t, fn) { (this.l[t] ||= []).push(fn); }
    fire(t, e) { for (const fn of this.l[t] || []) fn(e); }
    send() {} close() {}
  };

  // --- the two things a condition can switch off ---------------------------
  let freezeBakes = false;
  let freezePond = false;
  function installFreeze() {
    // The pond cache is not nulled -- it carries `paletteKey` in its own
    // signature and rebuilds when that moves -- so freezing the caches means
    // freezing the key too, or condition 3 silently keeps rebuilding ponds.
    let heldKey = renderer.paletteKey;
    Object.defineProperty(renderer, 'paletteKey', {
      configurable: true,
      get: () => heldKey,
      set: (v) => { if (!(freezeBakes || freezePond)) heldKey = v; },
    });
    for (const key of ['groundCache', 'pondCache']) {
      let held = renderer[key];
      Object.defineProperty(renderer, key, {
        configurable: true,
        get: () => held,
        // A frozen condition refuses the null that forces a rebake; it still
        // accepts a real cache, so the first bake of the run lands normally.
        set: (v) => { if (!(freezeBakes && v === null)) held = v; },
      });
    }
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
  // texture upload scale with pixels; the command list does not. So if the
  // jank tracks this dial, the cost is pixels; if it does not, the cost is
  // the ~1200 draw calls.
  let bakeScale = 1;
  let firstSide = 0;
  let targetDevice = 0;   // device px per side; 0 = leave the shipped clamp alone
  // The size the PREWARM actually baked at. If it disagrees with the size the
  // crossing then draws at, every prewarmed layer was a cache miss and the
  // burst happened again inside the run -- so the rig says so instead of
  // quietly reporting someone else's number.
  let warmSide = 0;
  function installBakeScale() {
    for (const m of ['bakeTileFor', 'pondBakeTileFor']) {
      const real = renderer[m] ? renderer[m].bind(renderer) : Object.getPrototypeOf(renderer)[m].bind(renderer);
      renderer[m] = (...a) => {
        const t = real(...a);
        if (!targetDevice) return t * bakeScale;
        const world = a[0];
        const dpr = renderer.dpr || window.devicePixelRatio || 1;
        const widest = Math.max(world.width, world.height);
        // The tile that puts the WIDEST side of the world at exactly the
        // target device size, never above what the renderer already chose.
        return Math.min(t, targetDevice / dpr / widest);
      };
    }
  }

  const TICK_MS = 800;
  const FROM = 256, TO = 269;   // 13 ticks of the day -> dusk fade, ~130 blend steps

  async function condition(world, label, { transitions = true, bakes = true, blur = true, reuse = false, scale = 1, device = 0, flat = false, xfade = false, pond = true, warm = 'none', wash = true, preheat = null }) {
    setTransitions(transitions);
    setBlur(blur);
    reuseCanvases = reuse;
    freezeBakes = !bakes;
    bakeScale = scale;
    flatBake = flat;
    crossfade = xfade;
    liveWash = wash;
    freezePond = !pond;
    if (!xfade) layerCache.clear();
    targetDevice = device;
    firstSide = 0;
    warmSide = 0;
    renderer.groundCache = null; renderer.pondCache = null;

    // Settle the bake size BEFORE anything is prewarmed or counted. The layer
    // key carries `o.tile`, and `device`/`scale` change it -- but `prewarm`
    // reads `lastGroundOpts`, which is whatever the PREVIOUS condition drew.
    // Prewarming against a stale tile keys every layer at the wrong size, so
    // the burst we believe we measured is thrown away and happens again,
    // lazily, inside the crossing.
    //
    // Wait for the DRAW, never for a duration. A fixed delay is a guess about
    // frame time, and the frame time here is the thing under measurement: 32ms
    // spanned a frame in Chrome and did not on the phone, where a baseline
    // frame runs 20-170ms. Nulling the opts first means a settle that never
    // lands leaves `prewarm` with nothing, which its own guard reports as
    // warm 0 -- a loud failure instead of a quiet wrong number.
    const wasCrossfade = crossfade;
    crossfade = false;
    lastGroundOpts = null; lastPondArgs = null;
    for (const s of sockets) s.fire('message', { data: JSON.stringify({ ...world, tick: FROM }) });
    const deadline = performance.now() + 4000;
    while (!(lastGroundOpts && lastPondArgs) && performance.now() < deadline) await nextFrame();
    crossfade = wasCrossfade;
    renderer.groundCache = null; renderer.pondCache = null;

    // A lull bake builds the NEXT theme against a cache that already holds the
    // current one. Preheating here -- before the counter -- makes the measured
    // burst a single theme, which is what section 6.3 actually ships; the
    // two-theme burst only ever happens once, on load.
    if (preheat) await prewarm('burst', [preheat], true);

    const g0 = { ...wrapped.ground }, p0 = { ...wrapped.pond };
    const frames = [];
    let last = performance.now(), stop = false;
    const tick = () => { const n = performance.now(); frames.push(n - last); last = n; if (!stop) requestAnimationFrame(tick); };
    requestAnimationFrame(tick);
    await prewarm(warm, ['day', 'dusk'], !preheat);
    for (let t = FROM; t <= TO; t++) {
      for (const s of sockets) s.fire('message', { data: JSON.stringify({ ...world, tick: t }) });
      await new Promise(r => setTimeout(r, TICK_MS));
    }
    stop = true;
    const over = (ms) => frames.filter(f => f > ms).length;
    const row = {
      label,
      frames: frames.length,
      janky: over(20), bad: over(33), worst: Math.round(Math.max(0, ...frames)),
      bakes: wrapped.ground.n - g0.n,
      side: firstSide || (renderer.groundCache ? renderer.groundCache.width : 0),
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
    el.innerHTML = '<b>crossing probe — day → dusk, 24 ticks each</b><br>'
      + `<span style="color:#9c8a7c">${navigator.userAgent.includes('Chrome') ? 'Chrome' : navigator.userAgent.includes('Safari') ? 'Safari' : '?'}`
      + ` · dpr ${devicePixelRatio} · bake ${renderer.groundCache ? renderer.groundCache.width + 'px' : '—'}</span>`
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
        + `${r.warmSide && r.warmSide !== r.side ? `<span style="color:#b4462f"> \u26a0warm ${r.warmSide}</span>` : ''}</td>`
        + `<td style="padding-left:14px;text-align:right">${r.bakeMs + r.pondMs}ms</td></tr>`).join('')
      + '</table>'
      + (M.done ? '<div style="margin-top:8px;color:#3f7a45">done — if the five baselines agree, the treatments are comparable; if they climb, the run drifted</div>'
                : '<div style="margin-top:8px;color:#9c8a7c">running… ~11s per row, nine rows (~1.7 min). WORST is the column that matters here. KEEP THE SCREEN AWAKE. Treatments are indented; compare each to the baselines either side.</div>');
  }

  window.__runProbe = async (world) => {
    installFreeze();
    installBakeScale();
    render();
    // Every treatment is bracketed by a baseline. If the baselines hold
    // steady the treatments are comparable; if they drift, the drift is
    // visible instead of being silently attributed to the treatment.
    await condition(world, 'baseline 1', {});
    await condition(world, '  x-fade, bake in ONE burst', { xfade: true, warm: 'burst' });
    await condition(world, 'baseline 2', {});
    // The ruled design of CROSSING-BAKES.md section 6: cross-fade AND the
    // 2048 cap together. Measured, not extrapolated from the full-res stall.
    await condition(world, '  x-fade + 2048 cap (THE RULED DESIGN)', { xfade: true, warm: 'burst', device: 2048 });
    await condition(world, 'baseline 3', {});
    // The recurring cost as shipped: one theme baked against a warm cache.
    await condition(world, '  x-fade + cap, ONE theme (THE LULL BAKE)', { xfade: true, warm: 'burst', device: 2048, preheat: 'day' });
    await condition(world, 'baseline 4', {});
    await condition(world, '  FROZEN (the ceiling)', { bakes: false });
    await condition(world, 'baseline 5', {});
    setTransitions(true); setBlur(true); reuseCanvases = false; freezeBakes = false; liveWash = true;
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
