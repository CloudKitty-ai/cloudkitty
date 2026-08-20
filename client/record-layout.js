/**
 * Records what `resizeFor` actually saw, off the page it is running in.
 *
 * Loaded only when the URL carries `#record` (see index.html), so it costs a
 * normal visitor one hash comparison and no bytes.
 *
 * WHY NOT AN IFRAME. The first version framed index.html and swept five
 * viewports by resizing the frame. That cannot work on the deployed site and
 * never could: Caddy sends `x-frame-options: DENY`, so the frame is refused,
 * `contentDocument` stays null, and every case fails. The header is right --
 * it is clickjacking protection, and a lab page is a terrible reason to
 * weaken it -- so the recorder moved into the page instead of trying to look
 * at it from outside.
 *
 * Measuring in-page is better anyway, and not only as a workaround: the
 * numbers that cannot be derived from the CSS are the RENDERED header and
 * footer heights, which depend on font metrics. A framed page at a forced
 * width is not guaranteed to lay those out the way the real device does, and
 * on iOS it would have been a fiction -- Safari there ignores frame sizing
 * the way it ignores window.resizeTo.
 *
 * The trade is that one visit records one viewport. That is the honest unit:
 * resize the window, press the button again, and each entry is a real
 * measurement of a real layout rather than five interpolations of one.
 */
(() => {
  const px = (cs, ...sides) => sides.reduce((s, k) => s + (parseFloat(cs[k]) || 0), 0);

  function sample() {
    const q = (s) => document.querySelector(s);
    const stage = q('.stage');
    const cell = stage && stage.parentElement;
    const layout = cell && cell.parentElement;
    const cols = layout ? layout.querySelectorAll('.panel-col') : [];
    const boxH = (s) => (q(s) ? q(s).getBoundingClientRect().height : 0);
    let beside = 0;
    for (const c of cols) beside += c.getBoundingClientRect().width;
    const world = q('#world');
    return {
      docClientWidth: document.documentElement.clientWidth,
      docClientHeight: document.documentElement.clientHeight,
      // The three viewport heights, because on a phone they disagree and the
      // disagreement is the whole problem: clientHeight stays at the SMALL
      // one while the visible screen grows to the LARGE one as the toolbar
      // retracts. `lvh` is what a landscape map should fill.
      probeLvh: +boxH('#vh-probe').toFixed(2),
      visualViewportHeight: window.visualViewport
        ? +window.visualViewport.height.toFixed(2) : null,
      innerHeight: window.innerHeight,
      headerHeight: +boxH('header').toFixed(2),
      footerHeight: +boxH('footer').toFixed(2),
      bodyPadY: px(getComputedStyle(document.body), 'paddingTop', 'paddingBottom'),
      bodyPadX: px(getComputedStyle(document.body), 'paddingLeft', 'paddingRight'),
      stageFrameX: stage ? px(getComputedStyle(stage), 'paddingLeft', 'paddingRight',
        'borderLeftWidth', 'borderRightWidth') : null,
      stageFrameY: stage ? px(getComputedStyle(stage), 'paddingTop', 'paddingBottom',
        'borderTopWidth', 'borderBottomWidth') : null,
      layoutClientWidth: layout ? layout.clientWidth : null,
      besideWidth: +beside.toFixed(2),
      columnGap: layout ? (parseFloat(getComputedStyle(layout).columnGap) || 0) : 0,
      panelColCount: cols.length,
      shortBranch: matchMedia('(max-height: 500px)').matches,
      // The ANSWER, not just the inputs. A harness that replays these through
      // resizeFor and compares against a number resizeFor produced would agree
      // with itself; comparing against what the browser actually laid out is
      // the only part of this that can fail.
      canvasCssWidth: world ? world.style.width : null,
      canvasCssHeight: world ? world.style.height : null,
      canvasBackingWidth: world ? world.width : null,
      dpr: window.devicePixelRatio || 1,
    };
  }

  const KEY = 'cloudkitty-layout-recording';
  const load = () => {
    try { return JSON.parse(sessionStorage.getItem(KEY)) || {}; } catch { return {}; }
  };

  const ui = document.createElement('div');
  ui.style.cssText = 'position:fixed;inset:auto 8px 8px 8px;z-index:9999;background:#fffdfa;'
    + 'border:1px solid #c3b3a3;border-radius:10px;padding:10px 12px;font:13px/1.5 system-ui,sans-serif;'
    + 'color:#6b5a4e;box-shadow:0 8px 24px rgba(150,125,105,.3);max-height:60vh;overflow:auto';
  ui.innerHTML = '<div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">'
    + '<strong style="font-size:13px">layout recorder</strong>'
    + '<button id="rec-add" style="font:inherit;padding:4px 10px;border-radius:6px;'
    + 'border:1px solid #c3b3a3;background:#fdf6ec;cursor:pointer">Record this size</button>'
    + '<button id="rec-clear" style="font:inherit;padding:4px 10px;border-radius:6px;'
    + 'border:1px solid #c3b3a3;background:none;cursor:pointer">Clear</button>'
    + '<span id="rec-count" style="font-size:12px;opacity:.7"></span></div>'
    + '<p style="margin:6px 0 0;font-size:12px;opacity:.8">Resize the window and press Record again '
    + 'for each size worth capturing. On a phone one size is all there is, which is the point.</p>'
    + '<textarea id="rec-out" readonly style="width:100%;min-height:9rem;margin-top:8px;'
    + 'font-family:ui-monospace,monospace;font-size:11px;border:1px solid #c3b3a3;'
    + 'border-radius:6px;padding:8px"></textarea>';
  document.body.appendChild(ui);

  const out = ui.querySelector('#rec-out');
  const count = ui.querySelector('#rec-count');

  function render() {
    const store = load();
    const n = Object.keys(store).length;
    count.textContent = n ? `${n} size${n === 1 ? '' : 's'} recorded` : 'nothing recorded yet';
    out.value = JSON.stringify({
      recordedOn: navigator.userAgent,
      dpr: window.devicePixelRatio || 1,
      cases: store,
    }, null, 2);
  }

  ui.querySelector('#rec-add').addEventListener('click', () => {
    const s = sample();
    const store = load();
    // Keyed by the viewport AND the dpr: the same CSS size on a retina and a
    // non-retina display is two different recordings, and overwriting one with
    // the other is exactly how a fixture ends up guarding the wrong device.
    store[`${s.docClientWidth}x${s.docClientHeight}@${s.dpr}`] = s;
    sessionStorage.setItem(KEY, JSON.stringify(store));
    render();
    out.select();
  });
  ui.querySelector('#rec-clear').addEventListener('click', () => {
    sessionStorage.removeItem(KEY);
    render();
  });
  render();
})();
