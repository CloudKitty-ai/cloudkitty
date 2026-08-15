/**
 * CloudKitty's viewer.
 *
 * Fetch the world once for a first paint, then subscribe to `/ws` and redraw on
 * every tick the server pushes. If the connection drops, take a fresh snapshot and
 * subscribe again -- the simulation never notices either way.
 */

const canvas = document.getElementById('world');
const renderer = new WorldRenderer(canvas);

const statusEl = document.getElementById('status');
const tickEl = document.getElementById('tick');
const panelEl = document.getElementById('panel');
const debugNoteEl = document.getElementById('debug-note');
const gridNoteEl = document.getElementById('grid-note');
const pathsNoteEl = document.getElementById('paths-note');
const happyNoteEl = document.getElementById('happy-note');
const pacedNoteEl = document.getElementById('paced-note');
const purrNoteEl = document.getElementById('purr-note');
const traitsNoteEl = document.getElementById('traits-note');

const NEED_LABELS = {
  eat: 'eat',
  drink: 'drink',
  sleep: 'sleep',
  play: 'play',
  cuddle: 'cuddle',
  bath: 'bath',
};

const RECONNECT_DELAY_MS = 1000;

/**
 * How long a distress may go unresolved before a kitty's card shows its gentle
 * cue. The real value comes from the server's /config ([viewer]
 * distress_patience_ticks) so it is never hard-coded here; this stand-in only
 * covers the moments before that fetch lands (or a server too old to serve it).
 */
let distressPatienceTicks = 60;

let latestWorld = null;

// The animation layer owns every drawing decision from here on (spec 005
// US3): app.js feeds it served states and keeps running the panel.
anim.init(renderer);
// ...and the panel's portraits ride the same frames, so the cats on the
// cards blink on the world's clock rather than a clock of their own.
anim.onFrame = paintPortraits;
// Served states reach the panel when the animation layer PROMOTES them,
// not when they land: the delay line holds a state back by about a tick
// (see `Pacer` in anim.js), and cards that updated on arrival would run
// that far ahead of the meadow they describe.
anim.onPromote = present;

/**
 * The hour themes (design experiment rounds two and three, split four
 * ways in v3): day, sunset, night and dawn. One applier flips everything
 * that carries color: the CSS tokens (body.dusk / body.night /
 * body.dawn), the canvas palettes (meadow, props), the renderer's theme
 * (fireflies, twilight fur), and the baked ground cache. Between phases
 * the canvas palettes are a blend of two rather than one of the four.
 *
 * The default mode is "auto": the world has its own sky (cosmetic for
 * now -- owner call, 2026-07-22), an hour derived as a pure function of
 * the served tick, so every viewer sees the same sky, restarts resume
 * mid-day where the snapshot left off, and the engine knows nothing
 * about any of it (Article V). When time-of-day someday shapes behavior
 * (crepuscular rewards for RL kitties), the served state will carry the
 * hour and hourForTick retires. The footer toggle cycles auto -> day ->
 * golden hour -> night; only explicit choices persist, so "no stored
 * choice" means "follow the world", exactly as designed in round two.
 */
const THEME_KEY = 'cloudkitty-theme';
const THEMES = ['day', 'dusk', 'night', 'dawn'];
const THEME_ICONS = { day: '☀️', dusk: '🌇', night: '🌙', dawn: '🌅' };
const MODE_CYCLE = ['auto', 'day', 'dusk', 'night', 'dawn'];
const AUTO_ICON = '🌤️'; // the sky decides

/** The settings' plain names, shown beside the toggle (owner request,
 * 2026-07-22: the bare icon needed words). */
const MODE_NAMES = {
  auto: 'Day/Night Cycle',
  day: 'Always Day',
  // "Twilight" was unambiguous while one palette served both ends of the
  // day; now that dawn is its own phase it has to say which twilight.
  dusk: 'Always Sunset',
  night: 'Always Night',
  dawn: 'Always Dawn',
};

/**
 * One world day, in ticks (at the default 800ms tick, an 8-minute day).
 *
 * Dawn used to wear the golden-hour set on the reasoning that the light
 * is the same and only the direction differs. It is not the same: sunset
 * is the day's warmth draining out, dawn is cold air and a sky that
 * brightens before anything is lit. They are separate phases as of v3.
 *
 * Each row is [name, span, fadeOut]: how long the phase lasts, and how
 * many of its closing ticks are spent crossing into the next one. The
 * fade is per phase rather than one global constant (owner, 2026-08-05)
 * so "how long is this phase" and "how long does it take to leave" are
 * independent -- a single constant capped at half a span coupled them,
 * and left the two short twilights settled for only 25 ticks each.
 *
 * The fades are 24 and 16 because both divide 32 (BLEND_STEPS): the
 * quantiser then lands on evenly-spaced steps, where an awkward length
 * like 13 gives gaps of 2,3,2,3. The shape is deliberate -- twilight is
 * approached slowly and handed over briskly -- and the spans give the
 * two short phases 49 settled ticks each, up from 25 under the old
 * single-constant scheme, without shortening the day much. */
const WORLD_DAY_PHASES = Object.freeze([
  ['day', 280, 24],
  ['dusk', 65, 16], // sunset -> night: twilight hands over briskly
  ['night', 190, 24],
  ['dawn', 65, 16], // dawn -> day
]);
const WORLD_DAY_TICKS = WORLD_DAY_PHASES.reduce((sum, [, span]) => sum + span, 0);

function hourForTick(tick) {
  let t = (Math.max(0, tick | 0)) % WORLD_DAY_TICKS;
  for (const [theme, span] of WORLD_DAY_PHASES) {
    if (t < span) return theme;
    t -= span;
  }
  return 'day';
}

/** The night's position inside the cycle, derived from the phase table so
 * a retuned day stays consistent everywhere. */
const NIGHT_WINDOW = (() => {
  let at = 0;
  for (const [theme, span] of WORLD_DAY_PHASES) {
    if (theme === 'night') return { start: at, end: at + span };
    at += span;
  }
  return null; // a world with no night keeps the sun up forever
})();

/**
 * Where the sky's traveler sits: { body: 'sun' | 'moon', t: 0..1 } across
 * its horizon-to-horizon arc. The sun's arc spans dawn + day + sunset --
 * rising as dawn begins, peaking mid-day, gone when sunset ends -- and
 * the moon owns the night. Pure function of the served tick, like
 * hourForTick above; the sky dial (render.js) reads it per frame.
 */
function skyForTick(tick) {
  const t = (Math.max(0, tick | 0)) % WORLD_DAY_TICKS;
  if (!NIGHT_WINDOW) return { body: 'sun', t: t / WORLD_DAY_TICKS };
  const nightSpan = NIGHT_WINDOW.end - NIGHT_WINDOW.start;
  if (t >= NIGHT_WINDOW.start && t < NIGHT_WINDOW.end) {
    return { body: 'moon', t: (t - NIGHT_WINDOW.start) / nightSpan };
  }
  const sinceDawn = (t - NIGHT_WINDOW.end + WORLD_DAY_TICKS) % WORLD_DAY_TICKS;
  return { body: 'sun', t: sinceDawn / (WORLD_DAY_TICKS - nightSpan) };
}

/**
 * How many steps a crossing is quantised into (v3, 2026-08-05).
 *
 * The world used to jump between three frozen palettes. It now crosses
 * between them -- but the ground cache BAKES the palette, so a genuinely
 * continuous blend would rebake it every frame and turn a one-blit ground
 * into a full redraw. Quantising is what makes it affordable: a palette
 * only exists at 1/32 steps, so a crossing costs at most 32 rebakes and a
 * settled phase costs none at all. A fade shorter than 32 ticks simply
 * gets one step per tick, which is already finer than the eye.
 */
const BLEND_STEPS = 32;

/** Which phase the world is in, which it is heading for, and how far
 * across -- quantised, so the caller can cheaply skip identical work.
 * The fade is clamped to the span as a guard: a table row asking to fade
 * for longer than its phase lasts would otherwise never settle. */
function phaseBlendFor(tick) {
  let t = Math.max(0, tick | 0) % WORLD_DAY_TICKS;
  for (let i = 0; i < WORLD_DAY_PHASES.length; i += 1) {
    const [theme, span, fadeOut = 0] = WORLD_DAY_PHASES[i];
    if (t < span) {
      const fade = Math.min(fadeOut, span);
      const remaining = span - t;
      if (fade <= 0 || remaining > fade) return { theme, next: null, step: 0 };
      const next = WORLD_DAY_PHASES[(i + 1) % WORLD_DAY_PHASES.length][0];
      const k = 1 - remaining / fade;
      return { theme, next, step: Math.round(k * BLEND_STEPS) / BLEND_STEPS };
    }
    t -= span;
  }
  return { theme: 'day', next: null, step: 0 };
}

let themeMode = 'auto'; // 'auto' | 'day' | 'dusk' | 'night'
let currentTheme = null; // the visual theme actually applied
let currentBlend = null; // and the quantised blend key it was applied at

/** Applies the mode's theme (auto reads the world clock) and syncs the
 * toggle. Cheap when nothing changed, so present() may call it per tick. */
/**
 * Every theme's page tokens, read out of the stylesheet once.
 *
 * Read rather than restated: index.html authors `:root` and the `body.dusk`
 * / `.night` / `.dawn` blocks, and a second copy of those colours in JS
 * would drift the first time one is tweaked. Which tokens matter is read
 * from the same place too -- the `transition-property` list on `body` is
 * already the set that is meant to cross with the light.
 *
 * Reading means briefly wearing each theme. Transitions are pinned to zero
 * across the read so the computed value is the theme's own colour rather
 * than a frame of the animation into it, and nothing yields in between, so
 * the browser never paints an intermediate state.
 */
let themeTokens = null;
function readThemeTokens() {
  const body = document.body;
  const savedDuration = body.style.transitionDuration;
  body.style.transitionDuration = '0s';
  // Take `reduced-motion` off for the read. It sets `transition: none`
  // (index.html), which computes transition-property to `none` -- so the
  // list below came back empty and, because this result is memoised, a
  // viewer who prefers reduced motion lost the world-clock crossing for the
  // whole session, silently, and never got it back by changing the setting.
  // The list we want is the one the stylesheet authors, not the one motion
  // preference leaves behind. Durations are already pinned above and nothing
  // paints before it goes back on, so this cannot start an animation.
  const hadReduced = body.classList.contains('reduced-motion');
  if (hadReduced) body.classList.remove('reduced-motion');
  const names = getComputedStyle(body)
    .transitionProperty.split(',')
    .map((n) => n.trim())
    .filter((n) => n.startsWith('--'));
  const had = THEMES.filter((t) => body.classList.contains(t));
  // Clear anything `paintThemeTokens` has already written. Inline
  // properties beat the class rules, so reading with them in place returns
  // the current blend four times over instead of the four themes. Memoising
  // means production never reaches that, but a function that silently
  // returns nonsense on a second call is a trap for whoever calls it next.
  const savedInline = {};
  for (const name of names) {
    savedInline[name] = body.style.getPropertyValue(name);
    body.style.removeProperty(name);
  }
  const out = {};
  for (const theme of THEMES) {
    for (const t of THEMES) body.classList.toggle(t, t === theme);
    void body.offsetHeight; // flush the class change into computed style
    const style = getComputedStyle(body);
    out[theme] = {};
    for (const name of names) out[theme][name] = style.getPropertyValue(name).trim();
  }
  for (const t of THEMES) body.classList.toggle(t, had.includes(t));
  if (hadReduced) body.classList.add('reduced-motion');
  for (const name of names) {
    if (savedInline[name]) body.style.setProperty(name, savedInline[name]);
  }
  body.style.transitionDuration = savedDuration;
  return out;
}

/**
 * The page tokens that INVERT between phases, rather than shifting.
 *
 * Ink goes dark-on-light to light-on-dark at night, and the card goes with
 * it. Interpolated linearly, as everything else here is, the pair walks
 * toward each other and MEETS: measured across dusk->night, the card falls
 * to L* 61 while the ink climbs to L* 66, which is 1.17:1 -- the text is
 * invisible against its own card for roughly 60% of the crossfade (owner
 * spotted it live, 2026-08-11).
 *
 * A faster easing does not fix it. Any monotonic curve still puts both
 * tokens at their own midpoint at the same instant, so they still meet --
 * just more briefly. The fix is not to interpolate them at all: they SWAP
 * at the halfway mark and the CSS transition does the crossing, which is
 * short and already tuned. The v3 plan called for exactly this and only
 * ever got it on the canvas side: "a separate faster curve for the
 * inverting tokens, because paper/ink blended linearly pass through mud".
 */
const INVERTING_TOKENS = new Set(['--ink', '--ink-soft', '--patience-ink', '--card']);

/** Paint the page's tokens at the world's own blend position. */
function paintThemeTokens(blend) {
  if (!themeTokens) themeTokens = readThemeTokens();
  const from = themeTokens[blend.theme];
  const to = themeTokens[blend.next ?? blend.theme];
  if (!from || !to) return;
  for (const name of Object.keys(from)) {
    const value = !blend.next
      ? from[name]
      : INVERTING_TOKENS.has(name)
        // Swap, never blend -- see INVERTING_TOKENS.
        ? (blend.step < 0.5 ? from[name] : to[name])
        : mixPaletteColor(from[name], to[name], blend.step);
    document.body.style.setProperty(name, value);
  }
}

function applyTheme() {
  // A hand-picked theme is exactly itself; only the world clock blends.
  const blend =
    themeMode === 'auto'
      ? phaseBlendFor(latestWorld?.tick ?? 0)
      : { theme: themeMode, next: null, step: 0 };
  // Which phase the page WEARS: its classes, its cat shading, its name in
  // the footer. Mid-crossing that is whichever end is nearer, the same
  // rule the canvas palette uses for anything it cannot interpolate.
  const theme = blend.next && blend.step > 0.5 ? blend.next : blend.theme;

  const toggle = document.getElementById('theme-toggle');
  if (toggle) {
    // The button wears the mode: the current hour when chosen by hand,
    // the "sky decides" glyph on auto (the page itself shows the hour).
    // The name beside it says the setting in words; the aria-label says
    // where the next click goes.
    const icon = themeMode === 'auto' ? AUTO_ICON : THEME_ICONS[themeMode];
    if (toggle.textContent !== icon) toggle.textContent = icon;
    const next = MODE_CYCLE[(MODE_CYCLE.indexOf(themeMode) + 1) % MODE_CYCLE.length];
    toggle.setAttribute('aria-label', `switch to ${MODE_NAMES[next]}`);
    const nameEl = document.getElementById('theme-name');
    if (nameEl && nameEl.textContent !== MODE_NAMES[themeMode]) {
      nameEl.textContent = MODE_NAMES[themeMode];
    }
  }

  // Cheap when nothing moved: a settled phase produces the same key every
  // tick, so this returns before touching the cache.
  const key = `${blend.theme}>${blend.next ?? ''}@${blend.step}`;
  if (key === currentBlend) return;
  currentBlend = key;

  // The classes still flip at the crossing's midpoint: they carry the
  // things that cannot be interpolated -- which phase the cats are shaded
  // for, the footer's name for the hour. Re-toggling a class it already
  // has would restart its transition, so only on a real change.
  if (theme !== currentTheme) {
    currentTheme = theme;
    document.body.classList.toggle('dusk', theme === 'dusk');
    document.body.classList.toggle('night', theme === 'night');
    document.body.classList.toggle('dawn', theme === 'dawn');
    renderer.theme = theme;
  }

  // ...but the COLOURS cross on the world's clock, not the class's.
  // They used to ride the class flip and a 1.5s CSS transition, so the page
  // finished changing 19 seconds before the meadow did -- the sky was still
  // handing over while the paper had long since decided (owner, 2026-08-07).
  // Setting them inline at the blend's own step puts the two on one clock;
  // the CSS transition survives only to smooth between quantised steps.
  paintThemeTokens(blend);

  setMeadowPalette(blend.theme, blend.next, blend.step);
  setPropPalette(blend.theme, blend.next, blend.step);
  renderer.groundCache = null; // the cache bakes the palette; rebake
  anim.redraw(); // safe pre-world: redraw no-ops until a state exists
}

function setThemeMode(mode) {
  themeMode = MODE_CYCLE.includes(mode) ? mode : 'auto';
  try {
    // Only explicit choices persist; auto is the unstored default.
    if (themeMode === 'auto') localStorage.removeItem(THEME_KEY);
    else localStorage.setItem(THEME_KEY, themeMode);
  } catch {
    // Private browsing may refuse storage; the sky still changes.
  }
  applyTheme();
}

function initTheme() {
  let stored = null;
  try {
    stored = localStorage.getItem(THEME_KEY);
  } catch {
    // No storage, no memory -- every visit follows the world.
  }
  themeMode = THEMES.includes(stored) ? stored : 'auto';
  applyTheme();
  document.getElementById('theme-toggle')?.addEventListener('click', () => {
    setThemeMode(MODE_CYCLE[(MODE_CYCLE.indexOf(themeMode) + 1) % MODE_CYCLE.length]);
  });
}

/**
 * Collapsed cards: portrait, name, what the cat is doing, its mood in
 * words -- and the distress cue, which never hides. The bars are what go.
 *
 * ALL of them or none (owner, 2026-08-06): one toggle over the whole
 * panel, never per-card. Collapsed is the default, and it is what lets
 * four cards sit in one stack beside the map on displays where four
 * expanded ones have to split across both sides.
 *
 * The class goes on `body` rather than on each card so a roster change
 * cannot leave a freshly built card in the wrong state -- there is one
 * flag, and no per-card state to keep in step.
 */
const CARDS_KEY = 'cloudkitty-cards';
let cardsCollapsed = true;

function applyCardMode() {
  document.body.classList.toggle('cards-collapsed', cardsCollapsed);
  const toggle = document.getElementById('cards-toggle');
  if (toggle) {
    toggle.textContent = cardsCollapsed ? 'expand' : 'collapse';
    toggle.setAttribute('aria-expanded', String(!cardsCollapsed));
    toggle.setAttribute(
      'aria-label',
      cardsCollapsed ? 'expand every kitty card' : 'collapse every kitty card',
    );
  }
  schedulePlacement();
}

/**
 * Re-place the cards once they are the size they are BECOMING.
 *
 * Collapsing changes card heights, which changes whether they fit as one
 * stack -- and it does not resize the canvas, so the ResizeObserver that
 * normally re-places them never fires for this. But measuring straight
 * after the class flip reads the size the cards are leaving, because the
 * collapse is a transition: the first build of this placed every toggle
 * one state behind (four in a column while expanded, split while
 * collapsed -- exactly backwards).
 *
 * So wait for the transition. `transitionend` is the precise signal, but
 * it does not fire when there is no transition to run -- which is the
 * reduced-motion case, where the CSS zeroes the duration -- so the
 * duration is read first and a zero one places the cards immediately.
 * The timer is the backstop for anything else that could swallow the
 * event, and whichever arrives first wins.
 */
let placementTimer = 0;
function schedulePlacement() {
  const details = panelEl.querySelector('.kitty-card .details');
  const seconds = details ? parseFloat(getComputedStyle(details).transitionDuration) || 0 : 0;
  clearTimeout(placementTimer);
  if (seconds <= 0) {
    placeCards();
    return;
  }
  // The bars inside `.details` run their own width transitions and those
  // events bubble, so the listener has to say which property it is for.
  const done = (event) => {
    if (event.target !== details || event.propertyName !== 'grid-template-rows') return;
    details.removeEventListener('transitionend', done);
    clearTimeout(placementTimer);
    placeCards();
  };
  details.addEventListener('transitionend', done);
  placementTimer = setTimeout(() => {
    details.removeEventListener('transitionend', done);
    placeCards();
  }, seconds * 1000 + 80);
}

function toggleCards() {
  cardsCollapsed = !cardsCollapsed;
  try {
    localStorage.setItem(CARDS_KEY, cardsCollapsed ? 'collapsed' : 'expanded');
  } catch {
    // Private browsing may refuse storage; the toggle still works.
  }
  applyCardMode();
}

function initCards() {
  let stored = null;
  try {
    stored = localStorage.getItem(CARDS_KEY);
  } catch {
    // No storage, no memory -- every visit opens collapsed.
  }
  cardsCollapsed = stored !== 'expanded';
  applyCardMode();
  document.getElementById('cards-toggle')?.addEventListener('click', toggleCards);

  // Clicking a card does the same thing (owner, 2026-08-07). It toggles
  // ALL of them, not the one clicked -- the all-or-none rule is the
  // owner's, and a card that expanded alone would quietly break it.
  //
  // Delegated to the panel rather than bound per card, because cards are
  // rebuilt on a roster change and per-card listeners would have to be
  // rebound with them.
  //
  // Deliberately NOT given `tabindex`/`role="button"`: the footer control
  // is a real button with `aria-expanded`, and it already reaches
  // everything this does. Four extra tab stops that all fire the same
  // global toggle would be four ways to hear the same thing, which is
  // worse for a keyboard or screen-reader user than one clear control.
  // So this is a pointer convenience over an affordance that already
  // exists, and it adds no function that is only reachable by mouse.
  // Someone dragging across a card is selecting a cat's name to copy, not
  // asking the panel to move, so a drag is not a click.
  //
  // This has to be measured from the pointer, NOT from `getSelection()`:
  // pressing the mouse clears the selection before the click event fires,
  // so by the time a handler runs there is never a selection to find. That
  // check was written first, tested, and did nothing at all.
  const DRAG_SLOP_PX = 4; // a steady hand still moves a pixel or two
  let pressedAt = null;
  panelEl.addEventListener('mousedown', (event) => {
    pressedAt = { x: event.clientX, y: event.clientY };
  });
  panelEl.addEventListener('click', (event) => {
    const from = pressedAt;
    pressedAt = null;
    if (!event.target.closest('.kitty-card')) return;
    if (from && Math.hypot(event.clientX - from.x, event.clientY - from.y) > DRAG_SLOP_PX) return;
    toggleCards();
  });
}

/**
 * The header's loafing kitties: the one place the world's art steps outside
 * the canvas. Both wear Biscuit's colorway, picked by name so a palette
 * reshuffle can never silently change who greets you; each canvas says
 * which way it faces (data-facing), so the pair bookends the wordmark.
 */
function drawHeaderKitties() {
  const size = 32;
  const dpr = window.devicePixelRatio || 1;
  for (const el of document.querySelectorAll('.header-kitty')) {
    el.width = size * dpr;
    el.height = size * dpr;
    el.style.width = `${size}px`;
    el.style.height = `${size}px`;
    const ctx = el.getContext('2d');
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    drawCat(ctx, {
      pose: 'loaf',
      appearance: PALETTES.find((p) => p.name === 'biscuit tabby') ?? appearanceFor(0),
      facing: el.dataset.facing === 'left' ? 'left' : 'right',
      size,
      phase: 0,
    });
  }
}

/** The sky dial's colors, named (Article VI). The dome tint follows the
 * world's own hour, never the viewer's theme override -- the dial is a
 * fact about the world. Sun gold is kin to the sparkle stars. */
const SKY_DIAL = Object.freeze({
  // Dome transparency halved from the first cut (owner call, 2026-07-23:
  // the map's border read through it); the day dome then darkened a hair
  // more, since near-white on the near-white stage card got lost (same
  // day: night's clear differential is the model).
  domeDay: 'rgba(240, 228, 205, 0.45)',
  domeDusk: 'rgba(255, 196, 130, 0.5)',
  domeNight: 'rgba(43, 39, 51, 0.6)',
  // Dawn's dome, cool and dim where dusk's is amber. Without it the
  // dial painted full daylight through the whole dawn phase while the
  // page, the meadow and the fur were all in the dim set -- the one
  // thing that tells you what hour you are in, misreporting it.
  domeDawn: 'rgba(206, 208, 224, 0.5)',
  // A richer gold than the sparkle stars: on the tan dome the soft
  // #f4c95d read dim (owner call, 2026-07-23), so the disc deepens and
  // takes a crisp rim, outline-first like the cats.
  sun: '#f5d12e',
  //sunRim: '#e6d119', // a real step down from the disc: the rim is the pop
  sunRim: '#f5ca19', // a real step down from the disc: the rim is the pop
  sunRay: 'rgba(245, 173, 46, 0.9)',
  // The low sun burns red-orange (owner call, 2026-07-23: gold vanished
  // into the amber twilight dome).
  duskSun: '#e2603c',
  duskSunRim: '#b64526',
  duskSunRay: 'rgba(226, 96, 60, 0.85)',
  moon: '#eae6f2',
  moonCrater: '#c9c2d8',
});

/**
 * The sky dial: the world's clock made visible. A small dome perched on
 * the map's top edge (owner call, 2026-07-23: up out of the grass) -- the
 * dial canvas's bottom edge IS the horizon, so a rising sun climbs out of
 * the world and a setting one sinks behind it, clipped by the canvas
 * bounds for free. The sun crosses through dawn, day and sunset; the moon
 * owns the night (skyForTick). Always the world's own hour, never the
 * viewer's theme override -- under a forced theme, the dial is what tells
 * you what you're overriding. Page chrome like the header kitties, drawn
 * parametrically, redrawn once per served tick.
 */
function drawSkyDial(tick) {
  const el = document.getElementById('sky-dial');
  if (!el) return;
  // The bitmap is drawn at the full-size dimensions (owner-tuned 78x39,
  // ~3.5 tiles at the 720px map) and the browser scales it: CSS owns the
  // displayed size (a fraction of the stage, index.html), so the dial
  // shrinks with the map on mobile and under window resizing. No inline
  // style sizes here -- they would override that CSS.
  const W = 78;
  const H = 39;
  const r = 35;
  const dpr = window.devicePixelRatio || 1;
  if (el.width !== W * dpr) {
    el.width = W * dpr;
    el.height = H * dpr;
  }
  const ctx = el.getContext('2d');
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, W, H);

  const cx = W / 2;
  const cy = H; // the horizon IS the bitmap's bottom edge -- no margin
  // (the 1.5px allowance below it left a visible gap above the tiles
  // once the rim stroke retired; owner call, 2026-07-23)
  const sky = skyForTick(tick);
  // The dial crosses between phases on the same clock as the meadow. It
  // used to pick one of four domes by `hourForTick` and swap at the phase
  // boundary, so the sky under the sun changed in a single frame while the
  // world it reports was still 19 seconds into a crossfade (owner,
  // 2026-08-07). Always the world's own blend, never the manual override --
  // the dial is what tells you what you are overriding.
  const blend = phaseBlendFor(tick);
  const domeOf = (phase) =>
    phase === 'night' ? SKY_DIAL.domeNight
    : phase === 'dusk' ? SKY_DIAL.domeDusk
    : phase === 'dawn' ? SKY_DIAL.domeDawn
    : SKY_DIAL.domeDay;
  // How low the sun sits, 0..1 -- read off its own height on the arc, not
  // off the name of the phase.
  //
  // Keying it to the phase was wrong twice over. Once by omission: `dusk`
  // alone meant dawn's horizon sun drew in high-noon gold. Then by blending
  // it, because the PHASE hands over to night 16 ticks before the sun
  // actually sets, so the disc warmed back toward gold over its last ten
  // seconds of being up -- the reverse of the point. Holding it across that
  // one crossing patched the symptom while leaving the cause: a colour that
  // says "near the horizon" derived from something that is not the horizon.
  //
  // `sky.t` runs 0 at the rising horizon, 0.5 at the peak, 1 at the setting
  // one, so its sine IS the height. Now the sun cannot un-redden while it is
  // still up, whatever the phase table says, and the warm-up happens as it
  // descends rather than as the label changes.
  //
  // The band is how high still counts as low. At 0.5 the red fades out
  // around a sixth of the way up the arc, which lands within three ticks of
  // where dawn ends today -- the look this replaces, arrived at honestly.
  const HORIZON_BAND = 0.5;
  const height = Math.sin(Math.min(1, Math.max(0, sky.t)) * Math.PI);
  const low = Math.min(1, Math.max(0, 1 - height / HORIZON_BAND));

  // The dome: a translucent slice of the world's actual sky, unlined --
  // the soft fill edge is the transition (owner call, 2026-07-23).
  ctx.beginPath();
  ctx.moveTo(cx - r, cy);
  ctx.arc(cx, cy, r, Math.PI, TAU);
  ctx.closePath();
  ctx.fillStyle = blend.next
    ? mixPaletteColor(domeOf(blend.theme), domeOf(blend.next), blend.step)
    : domeOf(blend.theme);
  ctx.fill();

  // Left horizon -> zenith -> right horizon as t runs 0 -> 1.
  const angle = Math.PI + sky.t * Math.PI;
  const bx = cx + Math.cos(angle) * r * 0.72;
  const by = cy + Math.sin(angle) * r * 0.72;
  const br = Math.max(3.5, r * 0.16);

  if (sky.body === 'sun') {
    // Twilight wears the setting-sun red; the high sun stays gold. Both
    // twilights sit on a horizon, so both get the low-sun disc -- a rising
    // sun is as red as a setting one. `low` is a share rather than a flag
    // now, so the warm-up happens across the crossfade.
    const warm = (high, lowColour) => mixPaletteColor(high, lowColour, low);
    ctx.strokeStyle = warm(SKY_DIAL.sunRay, SKY_DIAL.duskSunRay);
    ctx.lineWidth = 1.2;
    ctx.lineCap = 'round';
    for (let i = 0; i < 8; i++) {
      const a = (i / 8) * TAU;
      ctx.beginPath();
      ctx.moveTo(bx + Math.cos(a) * br * 1.35, by + Math.sin(a) * br * 1.35);
      ctx.lineTo(bx + Math.cos(a) * br * 1.8, by + Math.sin(a) * br * 1.8);
      ctx.stroke();
    }
    ctx.fillStyle = warm(SKY_DIAL.sun, SKY_DIAL.duskSun);
    ctx.strokeStyle = warm(SKY_DIAL.sunRim, SKY_DIAL.duskSunRim);
    ctx.lineWidth = 1.4;
    ctx.beginPath();
    ctx.arc(bx, by, br, 0, TAU);
    ctx.fill();
    ctx.stroke();
  } else {
    ctx.fillStyle = SKY_DIAL.moon;
    ctx.beginPath();
    ctx.arc(bx, by, br, 0, TAU);
    ctx.fill();
    // Three craters make it a moon and not a pale sun.
    ctx.fillStyle = SKY_DIAL.moonCrater;
    for (const [dx, dy, cr] of [[-0.3, -0.15, 0.22], [0.25, 0.2, 0.16], [0.05, -0.4, 0.12]]) {
      ctx.beginPath();
      ctx.arc(bx + dx * br, by + dy * br, cr * br, 0, TAU);
      ctx.fill();
    }
  }
}

function setStatus(text, connected) {
  statusEl.textContent = text;
  statusEl.classList.toggle('disconnected', !connected);
}

/** Everything outside the canvas, for the world that just became current. */
function present(world) {
  latestWorld = world;
  // The world's sky: on auto, the hour follows the served tick. applyTheme
  // early-returns when the hour hasn't changed, so this is per-tick cheap.
  if (themeMode === 'auto') applyTheme();
  drawSkyDial(world.tick);
  tickEl.textContent = world.tick;
  renderPanel(world);
}

/** Kitty cards: name, mood, happiness, and how each need is doing. */
function renderPanel(world) {
  // Rebuild only when the roster changes; otherwise update in place so the CSS
  // transitions can do their thing.
  // Everything is built into the right-hand column, which is where the cards
  // prefer to live; `placeCards` at the end splits them back across both
  // sides if that stack won't fit. Cards are only ever appended in roster
  // order, and the left column comes first in the DOM, so document order
  // equals roster order under either placement -- which is what the
  // positional update below relies on.
  const columns = panelEl.querySelectorAll('.panel-col');
  const cards = () => panelEl.querySelectorAll('.kitty-card');
  const needsRebuild = cards().length !== world.kitties.length;
  if (needsRebuild) {
    // Remove the kitty cards, not everything: the About card lives at the
    // top of the second column and emptying it would take About with it on
    // every roster change.
    for (const column of columns) {
      for (const card of column.querySelectorAll('.kitty-card')) card.remove();
    }
    for (const kitty of world.kitties) {
      columns[columns.length - 1].appendChild(buildKittyCard(kitty));
    }
  }

  const built = cards();
  world.kitties.forEach((kitty, index) => {
    const card = built[index];
    if (!card) return;
    card.querySelector('.name > span').textContent = kitty.name;
    // The sustained purr (spec 011) is a contentment signal, so it rides the
    // mood line -- as a lamp pinned to the right rather than a suffix that
    // lengthens it. `purring_until` in the payload means rumbling now.
    card.querySelector('.mood > span').textContent = moodFor(kitty);
    const purring = kitty.purring_until != null;
    const purr = card.querySelector('.purr');
    purr.classList.toggle('is-on', purring);
    purr.setAttribute('aria-label', purring ? 'purring' : 'not purring');
    // 🤍 unlit, 💗 lit. The white heart is a filled glyph with its own colour
    // rather than one that inherits the text's, which is why it reads as a
    // lamp that is off rather than a label that is broken -- and also the
    // one thing that would have to change if the cards ever took the world's
    // palette: a white heart on a night-themed card would be wrong, and the
    // outline ♡ (which does inherit colour) is the fallback (owner,
    // 2026-08-06, accepting that for this pass).
    for (const h of purr.querySelectorAll('.h')) h.textContent = purring ? '💗' : '🤍';
    card.querySelector('.doing').textContent = doingFor(kitty, world);
    card.querySelector('.patience').textContent = patienceFor(kitty, world);

    const happinessBar = card.querySelector('.happiness > span');
    happinessBar.style.width = `${clampPercent(kitty.happiness)}%`;
    happinessBar.style.backgroundColor = happinessColor(kitty.happiness);

    for (const [need, value] of Object.entries(kitty.needs)) {
      const bar = card.querySelector(`[data-need="${need}"] > span`);
      if (!bar) continue;
      // The engine sends pressure -- how much the cat wants this. The card
      // shows the other side of it, how well the need is MET, so that every
      // bar on the card fills the same way. Two bars 8px apart reading in
      // opposite directions is a legibility bug, not a style: a delighted
      // cat used to be a full green happiness bar above six empty ones.
      const satisfaction = 100 - clampPercent(value);
      bar.style.width = `${satisfaction}%`;
      bar.style.backgroundColor = needColor(satisfaction);
    }
  });

  // After the text lands, not before: the fit test measures real cards, and
  // an un-filled card is the wrong height.
  placeCards();
}

/**
 * Which side of the meadow the cards sit on. One stack on the right is the
 * preference; if that stack is taller than the map, split it as evenly as
 * possible across both sides instead.
 *
 * The test compares against the map's current height, and cannot chase its
 * own decision: both sides reserve a card column whether or not they hold
 * cards (index.html), so the map's width budget is the same under either
 * placement and moving cards cannot resize the map at all. The reading is
 * therefore stable by construction rather than merely monotone -- which is
 * what the reserve bought beyond centring the map.
 */
function placeCards() {
  const columns = panelEl.querySelectorAll('.panel-col');
  const cards = [...panelEl.querySelectorAll('.kitty-card')];
  if (columns.length < 2 || !cards.length) return;
  // Below the breakpoint `.panel-col` dissolves to `display: contents` and
  // the cards are one wrapping row beneath the map -- there are no sides to
  // choose. Ask the computed style rather than restating the media query's
  // width here, so the breakpoint keeps living in exactly one place.
  if (getComputedStyle(columns[0]).display === 'contents') return;

  const gap = parseFloat(getComputedStyle(columns[0]).rowGap) || 0;
  const stack =
    cards.reduce((sum, card) => sum + card.getBoundingClientRect().height, 0) +
    gap * (cards.length - 1);
  // An odd roster splits with the spare card on the right, the side the
  // cards prefer anyway -- both halves are the same height either way, so
  // the tie goes to keeping the rule's story straight.
  const onLeft =
    stack <= canvas.getBoundingClientRect().height ? 0 : Math.floor(cards.length / 2);

  // Appending a card that is already in place would restart its transitions,
  // so only touch the DOM when the split actually changes. The count is
  // enough to tell: the order within a placement is always roster order.
  // Count the KITTY cards, not every child: the About card lives in a
  // column too, and counting it made this early-return lie about where the
  // split currently is.
  if (columns[0].querySelectorAll('.kitty-card').length === onLeft) return;
  cards.forEach((card, index) => columns[index < onLeft ? 0 : 1].appendChild(card));
}

// Sized for the GESTURE to read, not to match the meadow.
//
// It was 33px on the reasoning that a cat draws at one tile, so the
// portrait and the animal in the world would be the same picture. That
// only held on two of six displays measured -- the tile is height-bound,
// so it is 47px on a WQHD, 23px on a 1100px window and 15px on a phone,
// and 20x20 worlds will widen the gap again. The load-bearing property
// was never "matches the meadow"; it was "big enough to read".
//
// 47px is what the slow blink needs. Closing two small eyes moves very
// little ink: at 33px a full blink changed 26 pixels where an ear twitch
// changed 44, so the gentler of the two gestures was the harder to see.
// 47px doubles the blink's ink (9 -> 20) and is the first size where the
// shut eyes read as shut rather than as slightly smudged. Owner call,
// 2026-08-07, with the card portraits about to start animating -- which
// is what makes the blink worth seeing at all, since a cat out in the
// world is usually mid-action and idle motion is suppressed there.
const PORTRAIT_CAT = 47;
// The chip is bigger than the cat because the idle pose's ink runs past
// its own box -- the tail crosses the left edge -- so a chip the size of
// the cat cuts the tail off. Measured at the real size, never derived:
// stroke widths do not scale linearly, so the ink is 0.957 x 0.766 of the
// cat here against 1.015 x 0.818 at 33px, and geometry from one size lies
// about another -- nor does a probe drawn with a different appearance,
// which is how the first pass at this landed 3px out. Measured in situ on
// the card's own canvas, the ink is 48.00 x 38.33.
//
// Not square, and the padding is proportional to the one owner-picked at
// 33px (2.25 side / 3.5 vertical on a 33px cat, so ~3.2 / ~5.0 on a 47px
// one). Absolute padding would have kept the frame the same thickness
// while the cat grew 42%, which drifts it from "a frame the cat sits in"
// toward "a shape cut around it" -- the thing the tighter chips were
// rejected for.
// 54 -> 58 (2026-08-10), for the stretch. The chip was measured against the
// resting poses, and a stretching cat is the widest thing the vocabulary
// draws: at PORTRAIT_CAT it spans 54.0px, exactly the old chip, so it lost
// 2.2px of its front to the right edge. Widened rather than shrinking the
// cat, because the portrait is the one place the fine detail (the tabby
// stripes, the new eye colour and its limbal ring) has the pixels to read.
// Costs the name row 4px of its own width, which ellipsises rather than
// wraps -- checked against the longest name on the roster.
// 58 -> 61 when whiskers landed (2026-08-13): they reach past the head, so
// `stretch` -- the widest thing drawn anywhere -- ran 0.8px off the right
// edge of the chip. Widened rather than shortening the whiskers, since the
// portrait is where the cat is BIGGEST (47px against the map's 31) and so
// where the detail reads best. The chip check is what caught it.
const PORTRAIT_W = 61;
const PORTRAIT_H = 48;
// Not the chip's geometric centre. The ink is not centred in the cat's
// own box -- the tail reaches past the left edge while the right side
// stops short, and the whole silhouette sits low -- so drawing at
// (chip - cat) / 2 leaves the cat visibly shoved left (owner spotted it
// at the old size). These equalise the measured ink margins instead.
const PORTRAIT_X = 5.33;
const PORTRAIT_Y = 0.91;

/**
 * Paint one card portrait at a given moment of idle motion.
 *
 * One painter for both callers -- the first paint when a card is built and
 * every frame after -- because two of these would drift the day someone
 * tunes one of them.
 */
function paintPortrait(canvas, kittyId, idle) {
  const dpr = window.devicePixelRatio || 1;
  // Re-size the backing store when the display changes under us -- issue
  // #102's bug, in a second place. Dragging a window between a Retina and
  // a non-Retina screen changes dpr while the CSS size stays put, so a
  // store sized once at build time is then wrong, and the transform below
  // happily scales into it: measured 1.5x too large and clipped at both
  // edges. The world canvas has guarded this since #102; the portraits
  // are the same canvas problem and need the same guard.
  const wantWidth = Math.round(PORTRAIT_W * dpr);
  if (canvas.width !== wantWidth) {
    canvas.width = wantWidth;
    canvas.height = Math.round(PORTRAIT_H * dpr);
  }
  const ctx = canvas.getContext('2d');
  // After a resize the store is cleared and the transform reset, so this
  // has to come after the block above, not before it.
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, PORTRAIT_W, PORTRAIT_H);
  // The same lid/blink handoff the meadow makes (render.js): on the v2
  // path the eased lid REPLACES the snap-closed eyes, or a blinking cat
  // wears both and the ease never shows. v1 has no lid and keeps the
  // snap, so the toggle still A/Bs the portraits like everything else.
  // The eased lid, when the beat is a blink. v1 has no lid and keeps its
  // snap, so the footer toggle still A/Bs the portraits like everything
  // else -- but v1 never gets here, because the whole beat table is v2's.
  const lid = typeof drawCatTween === 'function' ? idle?.blinkLid : undefined;
  const eyes = lid === undefined && idle?.blinkLid !== undefined ? 'closed' : undefined;
  const pose = idle?.pose ?? 'idle';
  const phase = idle?.phase ?? 0;
  const opts = {
    appearance: appearanceFor(kittyId),
    facing: 'right', // toward its own name
    size: PORTRAIT_CAT,
    x: PORTRAIT_X,
    y: PORTRAIT_Y,
    eyesOverride: eyes,
    lid,
    // The ear twitch, the gaze and the jaw all ride the RIG -- they are not
    // layout fields. Before this the portrait passed none, so scan and yawn
    // were computed every frame and thrown away, and the ear twitch drew in
    // its pre-upgrade snap form.
    rig: idle?.rig,
    // The beat length, for the play-pounce. Off the served tick entirely --
    // which is the point: at 800ms the load is 192ms and the butt wiggle
    // quantises to a single rock, and here it has room to be a wiggle.
    layout: idle?.beatMs
      ? { beatMs: idle.beatMs, wiggleHz: idle.wiggleHz, sway: idle.sway }
      : undefined,
  };
  // `sit` arrives as a pose with no ramp of its own -- 27px of movement at
  // portrait size -- so without a blend it would pop in and out on the card.
  // (`stretch` needs none: it carries a phase and is authored to leave and
  // return to neutral, 0.4px off a resting cat at both ends.) The meadow's
  // own blend does the work; the KEY is 'card' + id, never the bare id,
  // because tweenFor is stateful and sharing a key with the meadow cat would
  // have each restart the other's blend -- the same trap rigFor documents.
  const tween = idle?.tween;
  if (tween?.blend && typeof drawCatTween === 'function') {
    drawCatTween(ctx, {
      ...opts,
      from: tween.blend.from,
      to: pose,
      // CLAMPED, unlike the meadow's. `easeBack` leans back before it goes
      // and drifts past before it settles, which is free on a canvas the
      // size of the world and is not free in a 58x48 chip: measured, the
      // overshoot on an idle->sit blend reaches 6.6px off the left edge and
      // 6.5px off the bottom. The chip cannot afford the anticipation, so
      // the portraits take the plain ease and the meadow keeps the lean.
      t: Math.min(1, Math.max(0, tween.blend.t)),
      phaseFrom: tween.blend.fromPhase,
      phaseTo: phase,
    });
  } else {
    drawCat(ctx, { ...opts, pose, phase });
  }
}

/**
 * Every portrait, on the frame's own clock. Wired to `anim.onFrame`.
 *
 * The pose is ALWAYS `idle`, never the cat's real one (owner, 2026-08-07).
 * That is the entire point: `motionFor` returns early for action poses, so
 * idle motion is suppressed exactly where a cat spends most of its time,
 * and a portrait that mirrored the world would suppress it too. The card is
 * a portrait -- the cat at rest -- which is the one place the blink and the
 * ear twitch reliably get to happen.
 *
 * `view.motionFor` rather than the presentation's, so a still frame hands
 * back phase 0 and the portraits hold their pose along with the meadow.
 */
function paintPortraits(world, view) {
  const canvases = panelEl.querySelectorAll('.name canvas');
  for (const canvas of canvases) {
    const id = Number(canvas.dataset.kitty);
    if (!Number.isFinite(id)) continue;
    paintPortrait(canvas, id, idlePortraitFor(view, id));
  }
}

/**
 * The portrait's own idle pose, and the blend into it.
 *
 * Everything here is keyed `'card' + id` rather than `id`. The presentation
 * layer's pose memory is per-key state, so a portrait sharing the meadow
 * cat's key would restart its blend every frame and vice versa -- the same
 * hazard `rigFor` documents, on a different map.
 *
 * A still frame answers null from both, so the portraits hold their pose
 * along with the meadow.
 */
function idlePortraitFor(view, id, now) {
  if (typeof view.idleCardBeatFor !== 'function') return null;
  // The portrait's own table decides, and it decides ONE thing -- a beat is
  // a pose or a blink or a yawn, never a pose AND a blink. Sequencing rather
  // than layering was the owner's call: two clocks produced sixteen pose x
  // motion pairs nobody chose, including a cat yawning mid-pounce.
  //
  // The WORLD's wake-stretch is deliberately NOT an input here, though
  // `idlePoseFor` would hand it over for the asking. It used to outrank the
  // table, on the reasoning that a pose tied to something the engine really
  // did earns the slot ahead of anything merely scheduled. Measured on the
  // live box (2026-08-10, 209 wakes), that reasoning did not survive:
  //
  //   - cats nap in 5-tick bouts and wake every ~21s, so the wake-stretch
  //     ALONE out-frequented the slow blink (~23s) and made stretching the
  //     card's loudest beat rather than its rarest;
  //   - and it never finished. 98% of cats leave idle on the very next tick,
  //     and the meadow -- which draws first (anim.js startLoop) -- hands
  //     idlePoseFor the SERVED pose, which deletes `wokeAt` mid-motion. The
  //     stretch died at phase 0.49, dead centre of its own hold, so every
  //     portrait stretch was a half one that snapped back through the blend
  //     instead of playing the authored release.
  //
  // The map cat still stretches when it wakes -- there the pose is answering
  // for a cat the viewer just watched get up. The card is a portrait, and
  // keeps its own clock. Its stretch now arrives only as the tail of the sit
  // chain, which is on that clock and therefore always completes.
  const beat = view.idleCardBeatFor(id, 'idle');
  const pose = beat?.pose ?? 'idle';
  const tween = view.tweenFor ? view.tweenFor(`card${id}`, pose, beat?.phase ?? 0) : null;
  // The rig, keyed in the portrait's OWN namespace. `rigFor` INTEGRATES, so
  // sharing the meadow cat's key would double-step every spring on both.
  // A portrait has no world velocity, so its rig only ever carries the face
  // and ear channels -- which is exactly what a portrait wants.
  const rig = view.rigFor
    ? view.rigFor(`card${id}`, {
      vx: 0,
      vy: 0,
      facing: 'right',
      gazeX: beat?.gaze ? beat.gaze.x : 0,
      gazeY: beat?.gaze ? beat.gaze.y : 0,
      earTwitch: beat?.earTwitch || 0,
      earTwitchSide: beat?.earTwitchSide || 1,
      earsBack: 0,
      yawn: beat?.yawn || 0,
      breath: 0,
    })
    : null;
  return {
    pose,
    phase: beat?.phase,
    beatMs: beat?.beatMs,
    wiggleHz: beat?.wiggleHz,
    sway: beat?.sway,
    blinkLid: beat?.blinkLid,
    rig,
    tween,
  };
}

function buildKittyCard(kitty) {
  const card = document.createElement('div');
  card.className = 'kitty-card';

  const name = document.createElement('div');
  name.className = 'name';
  // The card wears the kitty's own portrait (spec 005 polish): the same
  // drawCat the world uses, on the same frames -- see paintPortraits.
  const portrait = document.createElement('canvas');
  // Sizing is PORTRAIT_CAT's business (above); the floor it respects is
  // that below about 30px the ears, eyes and stripes stop separating and
  // the cat is a blob, which is where the 22px original died.
  const dpr = window.devicePixelRatio || 1;
  portrait.width = PORTRAIT_W * dpr;
  portrait.height = PORTRAIT_H * dpr;
  portrait.style.width = `${PORTRAIT_W}px`;
  portrait.style.height = `${PORTRAIT_H}px`;
  portrait.dataset.kitty = kitty.id;
  // A first pose so a freshly built card is never a blank chip; the frame
  // hook takes it from here.
  paintPortrait(portrait, kitty.id, { phase: 0 });
  name.appendChild(portrait);
  name.appendChild(document.createElement('span'));
  card.appendChild(name);

  // Opens this cat's about. Its own button rather than a click on the card,
  // which already means "collapse them all" -- the owner's all-or-none rule,
  // and a second meaning on the same target would break it. Hidden entirely
  // until TRAITS.on.
  const more = document.createElement('button');
  more.className = 'kitty-about';
  more.type = 'button';
  more.textContent = 'about';
  more.setAttribute('aria-label', `about ${kitty.name}`);
  more.addEventListener('click', (event) => {
    event.stopPropagation();
    const live = latestWorld?.kitties.find((k) => k.id === kitty.id) ?? kitty;
    openTraitsDialog(live);
  });
  name.appendChild(more);

  const doing = document.createElement('div');
  doing.className = 'doing';
  card.appendChild(doing);

  const mood = document.createElement('div');
  mood.className = 'mood';
  mood.appendChild(document.createElement('span')); // the mood words
  // The purr lamp, always present so it never moves the line. Hearts are
  // decoration; `aria-label` carries the state, because "purring" flanked by
  // dim hearts would otherwise read to a screen reader as a purring cat.
  //
  // `role="img"` is what makes that label land. ARIA prohibits naming a
  // generic element, so on a bare <span> both Chrome and Firefox drop the
  // aria-label and fall through to the subtree -- which always contains the
  // word "purring", so every cat on the page announced as purring whether it
  // was or not. A role that takes a name replaces the subtree with the
  // label, which is the whole point of writing one.
  const purr = document.createElement('span');
  purr.className = 'purr';
  purr.setAttribute('role', 'img');
  const word = document.createElement('span');
  word.textContent = 'purring';
  const heart = () => {
    const h = document.createElement('span');
    h.className = 'h';
    h.setAttribute('aria-hidden', 'true');
    return h;
  };
  purr.append(heart(), word, heart());
  mood.appendChild(purr);
  card.appendChild(mood);

  // Everything the collapsed card drops, in one box so the toggle has a
  // single thing to hide. What stays is the owner's list: portrait, name,
  // what the cat is doing, the mood in words -- and `.patience`, which is
  // outside this box on purpose (see below).
  const details = document.createElement('div');
  details.className = 'details';
  // The grid-rows collapse needs exactly one child to size (see the CSS);
  // this is that child, and it is what actually clips.
  const detailsInner = document.createElement('div');
  detailsInner.className = 'details-inner';
  details.appendChild(detailsInner);

  const happiness = document.createElement('div');
  happiness.className = 'bar happiness';
  happiness.appendChild(document.createElement('span'));
  detailsInner.appendChild(happiness);

  // No heading over the need bars. It cost 17px on every card to caption
  // six rows that already carry their own labels -- and once the bars fill
  // as the need is MET, a heading reading "needs" pointed the wrong way.
  const needs = document.createElement('div');
  needs.className = 'needs';
  for (const [need, label] of Object.entries(NEED_LABELS)) {
    const caption = document.createElement('span');
    caption.textContent = label;
    const bar = document.createElement('div');
    bar.className = 'bar';
    bar.dataset.need = need;
    bar.appendChild(document.createElement('span'));
    needs.appendChild(caption);
    needs.appendChild(bar);
  }
  detailsInner.appendChild(needs);
  card.appendChild(details);

  // Last, under the needs (owner, 2026-08-06). The cue reserves its line
  // whether or not it speaks, so the card never resizes when a cat becomes
  // distressed -- and at the foot of the card that reservation doubles as
  // the bottom padding rather than sitting as a gap in the middle. It also
  // reads better here: it is a note about the cat, not about the bar it
  // used to sit beneath.
  //
  // OUTSIDE `.details`, deliberately (owner, 2026-08-06): it is the only
  // line in the UI that says a cat needs help, and a collapsed default
  // that could suppress the alarm would be worse than no alarm. It costs
  // nothing to keep -- it is empty until a distress goes unanswered past
  // the threshold -- and its reserved line is the collapsed card's bottom
  // padding exactly as it is the expanded one's.
  const patience = document.createElement('div');
  patience.className = 'patience';
  card.appendChild(patience);

  return card;
}

/** Mood is happiness, and only happiness -- a napping cat can still be delighted. */
function moodFor(kitty) {
  if (kitty.happiness >= 80) return 'delighted';
  if (kitty.happiness >= 55) return 'content';
  if (kitty.happiness >= 30) return 'wants something';
  return 'needs a bit of help';
}

/**
 * What the cat is doing right now, from the engine's post-validation record --
 * this line never claims an action the engine refused. Pure formatting of
 * server state (Article V): names are looked up, nothing is simulated.
 */
function doingFor(kitty, world) {
  const action = kitty.last_action;
  if (!action) return 'settling in';

  const friendName = (id) =>
    world.kitties.find((k) => k.id === id)?.name ?? 'a friend';
  const partner = kitty.activity?.with_friend;

  switch (action.action) {
    case 'idle':
      // Idle continues whatever the cat was doing (multi-tick activities).
      return activityText(kitty, partner, friendName);
    case 'move':
      return `trotting ${action.direction}`;
    case 'rest':
      return action.with != null ? `cuddling with ${friendName(action.with)}` : 'settling down for a rest';
    case 'sleep':
      return activityText(kitty, action.with ?? partner, friendName) || 'falling asleep';
    case 'groom':
      return action.target != null ? `grooming ${friendName(action.target)}` : 'grooming';
    case 'eat':
      return 'eating 🍥';
    case 'drink':
      return 'drinking 💧';
    case 'chase':
      return `chasing ${targetText(action, world, friendName)}`;
    case 'play':
      // No target means solo play: a kitty entertaining itself.
      return action.target != null
        ? `playing with ${targetText(action, world, friendName)}`
        : 'pouncing at nothing 🎈';
    case 'purr':
      return 'purring 💕';
    case 'meow':
      return `meowing: “${MEOW_TEXT[action.message] ?? '…'}”`;
    default:
      return '…';
  }
}

function activityText(kitty, partner, friendName) {
  const state = kitty.activity?.state ?? 'idle';
  if (state === 'sleeping') {
    const where = kitty.activity?.in_sunbeam ? ' in a sunbeam' : '';
    return partner != null ? `napping${where} with ${friendName(partner)}` : `fast asleep${where}`;
  }
  if (state === 'resting') {
    return partner != null ? `cuddling with ${friendName(partner)}` : 'having a lie down';
  }
  return 'lounging about';
}

/**
 * Friendly words for a chase/play target. Greebles stay mysterious: the data
 * says what it is, but this viewer keeps the secret.
 */
function targetText(action, world, friendName) {
  if (action.target === 'kitty') return friendName(action.id);
  const element = world.elements.find((e) => e.id === action.id);
  if (!element) return 'something';
  if (element.kind === 'greeble') return '… nothing? 👻';
  if (element.kind === 'bug') return 'a bug 🐛';
  return `the ${element.kind}`;
}

/**
 * The gentle long-distress cue (US5). When any need has been in distress past
 * the configured patience, say so -- caring, not alarming, and only the
 * longest-running one, never a stack of alarms. Pure arithmetic on served
 * state: age = world.tick - distress_since[need].
 */
function patienceFor(kitty, world) {
  const since = kitty.distress_since;
  if (!since) return '';

  let oldest = null;
  for (const [need, startTick] of Object.entries(since)) {
    const age = world.tick - startTick;
    if (age >= distressPatienceTicks && (oldest === null || age > oldest.age)) {
      oldest = { need, age };
    }
  }
  if (!oldest) return '';
  const label = NEED_LABELS[oldest.need] ?? oldest.need;
  return `has been wanting ${label} for a while 💭`;
}

function clampPercent(value) {
  return Math.max(0, Math.min(100, value));
}

/**
 * The colour of a need bar, keyed on how SATISFIED the need is, so every
 * bar on the card fills the same way: more is better.
 *
 * The thresholds are the old pressure ones read from the other end (75 and
 * 45 of pressure are 25 and 55 of satisfaction), so nothing changes about
 * when a need starts looking worrying -- only which end of the bar says so.
 *
 * The satisfied green is deliberately paler than `happinessColor`'s. Six
 * full bars in the headline green would out-shout the happiness bar right
 * above them, and happiness is the summary the eye should land on first.
 */
function needColor(satisfaction) {
  if (satisfaction <= 25) return '#efa98b';
  if (satisfaction <= 55) return '#f3cf7a';
  return '#bcd9c0';
}

async function fetchSnapshot() {
  const response = await fetch('/world');
  if (!response.ok) throw new Error(`GET /world returned ${response.status}`);
  return response.json();
}

/**
 * Per-cat need rates, and how far each sits from the world's baseline.
 *
 * The engine calls this a trait in so many words -- `observe.rs` builds its
 * observation from `need_rate_for(id, kind) / reference_need_rate` -- so the
 * card is showing the same quantity the minds are trained against, not a
 * presentational invention.
 */
let traitConfig = null;

/**
 * OFF until the trait plumbing is in place (owner, 2026-08-15). `t` reveals
 * the per-card `about` link that opens the dialog; nothing else changes, so
 * a viewer who never presses it sees the site exactly as it ships.
 */
const TRAITS = { on: 0 };

/**
 * The owner's copy, verbatim. Ours to lay out, not to edit.
 *
 * Keyed by id AND name: a reseeded roster could hand id 3 to a different
 * cat, and attaching Pumpkin's life story to somebody else is a worse
 * failure than showing nothing. A mismatch shows nothing.
 *
 * **This copy has two halves with different lifetimes** (Experiments'
 * template, 2026-08-15), which matters because the workflow reruns at every
 * generation and roster change:
 *
 *   - the TITLE and the first sentence describe the BODY -- the trait -- and
 *     are durable. They survive a mind swap, and the trait titles are locked
 *     in the policy registry.
 *   - the rest is the MIND: observed narrative about the policy currently
 *     seated. It is rewritten at every seating, from the new generation's
 *     measurements.
 *   - an optional closer is a relationship hook ("Bonded with...").
 *
 * Kept as ONE string per cat rather than split into those halves on purpose.
 * The boundary is a judgement about someone else's prose -- Kittybear's first
 * sentence carries both halves at once -- and guessing it wrong would be a
 * silent edit. A seating refresh replaces the whole entry.
 *
 * "Tidy Kitty" is a deliberate display translation of the registry's
 * canonical FASTIDIOUS, owner-approved for visitors. Not a typo; do not
 * "correct" it back.
 */
const KITTY_BIOS = {
  1: {
    name: 'Miso',
    epithet: 'Sleepy Kitty',
    body: 'With Miso, nap time is all the time, and she\u2019s decided naps are '
      + 'best shared: she sleeps in a pile whenever she can, and everyone wants the '
      + 'spot beside her. When she wanders off alone, she sends a little purr across '
      + 'the meadow: I\'m fine, back soon.',
  },
  2: {
    name: 'Biscuit',
    epithet: 'Playful Kitty',
    body: 'Born to chase: Biscuit would rather chase a bug than eat dinner. She\'s '
      + 'also the meadow\'s elder, keeper of the old customs: a purr from far away '
      + 'means all is well, and when a friend mews for bath time, she\'s the one who '
      + 'pads over to help wash.',
  },
  3: {
    name: 'Pumpkin',
    epithet: 'Hungry Kitty',
    body: 'A snack is never far from her thoughts. In between visits to the food '
      + 'bowl, her heart is enormous: she spends her days cleaning her friends\' '
      + 'ears, purring all the while. Bonded with Kittybear.',
  },
  4: {
    name: 'Kittybear',
    epithet: 'Tidy Kitty',
    body: 'Setting the record for most baths and most purrs, Kittybear shares '
      + 'Pumpkin\'s warm idea of the world: caring for someone looks like washing '
      + 'them. The chattiest pair around, and the kindest. Bonded with Pumpkin.',
  },
  // Placeholder until she is seated and has grown into a mind of her own.
  // Sent by the owner directly, 2026-08-15. Experiments' relay believed this
  // one was still being held, so if a second version arrives, hers is the
  // one that was written later.
  5: {
    name: 'Clementine',
    epithet: 'Cuddly Kitty',
    body: 'Came into the world wanting to be near somebody. What she\'ll make of the '
      + 'meadow, nobody knows yet \u2014 she\'s new here.',
  },
};

/** The bio for a cat, or null when the roster does not match the copy. */
function bioFor(kitty) {
  const bio = KITTY_BIOS[kitty.id];
  return bio && bio.name === kitty.name ? bio : null;
}

const NEED_ORDER = ['eat', 'drink', 'sleep', 'play', 'cuddle', 'bath'];

/**
 * A colour per need. Each is the colour of the thing in the MEADOW that
 * answers it -- the bowl's clay, the pond, the bloom's gold, the lily pads,
 * the cuddle heart, and lavender for the soap.
 *
 * **Fixed values, deliberately, and this was tried the other way first.**
 * Reading them live from `PROPS`/`MEADOW` sounds obviously right -- the
 * dialog would wear the current hour like everything else -- and it fails,
 * because the meadow's palette is lit for the MEADOW's ground and these sit
 * on a CARD. At night `pondDeep` is #0b1216 against a #37313f card: nearly
 * black on dark, 16 points of lightness apart. `lilyPadRim` was worse, at
 * 12. And only half the palette moves at all, so three bars swung with the
 * hour while three sat still, which reads as breakage rather than as time
 * passing (owner spotted it on the night cards).
 *
 * So the identity is borrowed from the meadow once and then held. Every one
 * clears 25 points of L* against both the light card (L* 99) and the night
 * card (L* 21), and the six hues are at least 18 degrees apart -- both
 * asserted against the values themselves rather than against where they
 * came from.
 */
const NEED_COLOUR = {
  eat: '#cf8a5e', // the bowl's clay
  drink: '#8ab2c7', // the pond
  sleep: '#c6aa64', // the bloom's gold, shaded to read on a light card
  play: '#84b877', // a lily pad
  cuddle: '#d97f95', // the cuddle heart
  bath: '#8f7bb8', // lavender, for the soap
};

function traitsFor(kittyId) {
  if (!traitConfig) return [];
  const base = traitConfig.base;
  const served = traitConfig.kitty.find((k) => k.id === kittyId)?.needs ?? {};
  return NEED_ORDER.filter((need) => Number.isFinite(base[need])).map((need) => {
    // Served first, stub second, baseline last: a real trait always wins.
    const rate = Number.isFinite(served[need]) ? served[need] : base[need];
    return {
      need,
      rate,
      base: base[need],
      pct: Math.round(((rate - base[need]) / base[need]) * 100),
    };
  });
}

/**
 * Where a rate sits on its own bar, 0..1.
 *
 * Each need is scaled to ITS OWN baseline (owner, 2026-08-15): 0 at the
 * left, the baseline dead centre, twice the baseline at the right. Every
 * row's centre mark therefore lines up down the card, which is what makes a
 * deviation readable at a glance -- the thing a traits view is actually for.
 *
 * The cost, taken knowingly: bars no longer compare BETWEEN needs. A bath
 * rising at 0.20 and an appetite at 0.40 both sit at centre. The raw number
 * beside each bar carries that, and the shared-scale version buried the
 * deviation, which is the more important of the two readings here.
 */
function traitFill(t) {
  return Math.max(0, Math.min(1, t.rate / (t.base * 2)));
}

function openTraitsDialog(kitty) {
  const dialog = document.getElementById('traits');
  if (!dialog) return;
  const bio = bioFor(kitty);
  dialog.querySelector('.traits-name').textContent = kitty.name;
  const epithet = dialog.querySelector('.traits-epithet');
  epithet.textContent = bio ? bio.epithet : '';
  epithet.hidden = !bio;
  const prose = dialog.querySelector('.traits-prose');
  prose.textContent = bio ? bio.body : '';
  prose.hidden = !bio;
  const behavior = kitty.behavior ?? '';
  dialog.querySelector('.traits-mind').textContent = behavior.startsWith('policy:')
    ? behavior.slice('policy:'.length)
    : behavior || 'no policy seated';

  const portrait = dialog.querySelector('canvas');
  const dpr = window.devicePixelRatio || 1;
  portrait.width = PORTRAIT_W * dpr;
  portrait.height = PORTRAIT_H * dpr;
  portrait.style.width = `${PORTRAIT_W}px`;
  portrait.style.height = `${PORTRAIT_H}px`;
  paintPortrait(portrait, kitty.id, { phase: 0 });

  const list = dialog.querySelector('.traits-needs');
  list.innerHTML = '';
  for (const t of traitsFor(kitty.id)) {
    const row = document.createElement('div');
    row.className = 'trait';

    const label = document.createElement('span');
    label.className = 'trait-need';
    label.textContent = t.need;

    const track = document.createElement('span');
    track.className = 'trait-track';
    const fill = document.createElement('span');
    fill.className = 'trait-fill';
    fill.style.width = `${traitFill(t) * 100}%`;
    fill.style.background = NEED_COLOUR[t.need] ?? 'var(--ink-soft)';
    // Dead centre on every row, so the marks line up as one rule down the
    // card and a deviation is the only thing that breaks the line.
    const mark = document.createElement('span');
    mark.className = 'trait-base';
    track.append(fill, mark);

    const value = document.createElement('span');
    value.className = 'trait-value';
    value.textContent = t.rate.toFixed(2);

    // Nothing at all when a cat is ordinary for this need (owner,
    // 2026-08-15). The em dash was a value in a column of values, and six
    // rows of it said only that most cats are unremarkable, loudly. Silence
    // says the same thing and lets the exceptions carry the eye.
    const delta = document.createElement('span');
    delta.className = 'trait-delta';
    delta.textContent = t.pct === 0 ? '' : `(${t.pct > 0 ? '+' : ''}${t.pct}%)`;

    row.append(label, track, value, delta);
    list.appendChild(row);
  }
  dialog.showModal();
}

/**
 * A modal <dialog> does not close on a backdrop click by default, so this
 * adds it beside the × (owner, 2026-08-15).
 *
 * Tested against the dialog's own RECTANGLE rather than `event.target ===
 * dialog`, which is the usual shorthand: the target is also the dialog when
 * the click lands on its own padding, so the shorthand closes the card when
 * someone clicks the quiet strip just inside its edge. Both conditions
 * together mean only the backdrop closes it -- and requiring the target
 * keeps a keyboard-fired click, which reports (0, 0), from reading as a
 * click in the top-left corner of the screen.
 */
function initTraitsDialog() {
  const dialog = document.getElementById('traits');
  if (!dialog) return;
  dialog.addEventListener('click', (event) => {
    if (event.target !== dialog) return;
    const r = dialog.getBoundingClientRect();
    const outside = event.clientX < r.left || event.clientX > r.right
      || event.clientY < r.top || event.clientY > r.bottom;
    if (outside) dialog.close();
  });
}

/** Pick up viewer tunables from the server; keep the stand-ins if unavailable. */
async function fetchViewerConfig() {
  try {
    const response = await fetch('/config');
    if (!response.ok) return;
    const config = await response.json();
    const patience = config?.viewer?.distress_patience_ticks;
    if (Number.isFinite(patience) && patience >= 1) {
      distressPatienceTicks = patience;
      anim.setDistressPatience(patience);
    }
    // The easing duration is the served tick interval (FR-005) -- already
    // in /config as world.tick_ms, so no server change was ever needed.
    anim.setTickMs(config?.world?.tick_ms);
    // The trait source. `config.needs` is the baseline rise rate per need
    // and `config.kitty[].needs` overrides it for one cat -- which is
    // already how the engine reads it (`need_rate_for`), and already how
    // the RL side defines a trait: `rate / reference_need_rate`
    // (observe.rs). So this is the real number, not a stand-in.
    if (config?.needs) traitConfig = { base: config.needs, kitty: config.kitty ?? [] };
  } catch {
    // The stand-ins in VIEW carry an older or unreachable server (FR-018).
  }
}

function subscribe() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const socket = new WebSocket(`${protocol}//${window.location.host}/ws`);

  socket.addEventListener('open', () => {
    // Whatever arrives after a (re)connect is a fresh moment of the world:
    // snap to it, never ease across the gap (US3 edge case).
    anim.bumpGeneration();
    setStatus('watching live', true);
  });

  // ARRIVALS GO TO THE DELAY LINE, never straight to the screen.
  //
  // A backgrounded tab stops running frames but the socket keeps taking
  // messages, and a frozen one queues them at the OS. Come back after two
  // hours and ~9,000 world states arrive at once -- each one once running
  // a full render: a theme pass, the sky dial, and a complete rebuild of
  // the cards. That is the "it replays every tick very quickly" the owner
  // saw. The animation layer was never the problem; it already snaps on
  // return. The panel was, draining a backlog through the DOM.
  //
  // The queue, the pacing and the backlog collapse all live in `Pacer`
  // (anim.js), where they can be tested against an arrival series with no
  // socket and no frames. What is left here is the parsing.
  socket.addEventListener('message', (event) => {
    let world;
    try {
      world = JSON.parse(event.data);
    } catch (err) {
      console.error('could not read a world update', err);
      return;
    }
    anim.push(world);
  });

  socket.addEventListener('close', () => {
    setStatus('reconnecting…', false);
    setTimeout(start, RECONNECT_DELAY_MS);
  });

  socket.addEventListener('error', () => socket.close());
}

async function start() {
  try {
    setStatus('connecting…', false);
    fetchViewerConfig(); // fire-and-forget: the cue threshold tightens when it lands
    // The first state has no predecessor to ease from, so the pacer hands
    // it straight through and the panel is up before the socket opens.
    anim.push(await fetchSnapshot());
    subscribe();
  } catch (err) {
    console.error(err);
    setStatus('server unreachable — retrying…', false);
    setTimeout(start, RECONNECT_DELAY_MS);
  }
}

// Watch the map itself rather than the window. A `resize` listener fires
// while the canvas is still the size the PREVIOUS display gave it -- the
// renderer resizes it on its own frame -- so dragging the window between a
// large screen and a small one decided the split against the screen just
// left: cards overflowing the map on the smaller one, cards split on the
// larger one that had room for the stack. A live world hid it by
// re-measuring on the next tick; a frozen one has no next tick and the
// wrong answer simply stayed. Observing the canvas fires once it has
// actually changed size, which is the moment the fit test wants, and it
// covers everything that can move the map: viewport, world size, dpr.
// This settles rather than looping -- placing the cards can resize the map,
// but re-running the test on the new size returns the same answer and
// writes nothing (see `placeCards`).
/**
 * Bring the middle of the meadow into view on a short viewport.
 *
 * A phone held sideways fits the world to the WIDTH and lets it overflow
 * (render.js), so the top of the page is the top EDGE of the map -- often
 * an empty corner with no cat in it, which is a poor thing to open on.
 * This scrolls to the world's middle instead.
 *
 * The guard is "has the reader moved the page themselves", NOT "have we
 * done this already". Latching on the first observation looked equivalent
 * and was not: that observation can arrive while the canvas is still the
 * 720px default in the markup, and centring a 720px map leaves an 840px
 * one 60px out with no second chance. So instead we remember the position
 * we set, and keep correcting for as long as the page is still sitting
 * exactly where we put it. The moment it isn't, the reader has scrolled
 * and we never touch it again. Leaving the short layout re-arms the whole
 * thing, so a rotate back into landscape is a new context rather than a
 * scroll anyone chose.
 */
let wasShort = false;
let autoScrollY = null;
function centreMapWhenShort() {
  if (!matchMedia('(max-height: 500px)').matches) {
    wasShort = false;
    autoScrollY = null; // re-arm for the next rotation
    return;
  }
  const rect = canvas.getBoundingClientRect();
  // Nothing to centre until the map actually overflows. Deliberately
  // BEFORE the `entering` latch, so a fire this early still counts as the
  // first one and the real centring is not skipped.
  if (rect.height <= window.innerHeight) return;
  const entering = !wasShort;
  wasShort = true;
  const untouched =
    autoScrollY === null ? window.scrollY === 0 : Math.abs(window.scrollY - autoScrollY) <= 1;
  if (!entering && !untouched) return;
  const target = Math.max(0, window.scrollY + rect.top + rect.height / 2 - window.innerHeight / 2);
  if (Math.abs(target - window.scrollY) <= 1) return;
  // Instant, not smooth: a page that slides on arrival reads as a glitch.
  window.scrollTo({ top: target, behavior: 'auto' });
  autoScrollY = Math.round(window.scrollY); // read back: the browser may clamp
}

new ResizeObserver(() => {
  placeCards();
  centreMapWhenShort();
}).observe(canvas);

// The debug toggles, all in one mold (spec 008 FR-004/FR-009): `g` reveals
// greebles, `l` the demoted grid lines, `p` the session's worn paths, `h`
// happiness bars. Each flips a flag, syncs its footer note, and redraws --
// and every fresh load starts from the default.
//
// `b` is the odd one out and its note reads the other way round: the delay
// line is ON by default, so the note appears when it has been turned OFF.
// A visible note means "not what this normally does" either way.
window.addEventListener('keydown', (event) => {
  const key = event.key.toLowerCase();
  if (key === 'g') {
    renderer.showGreebles = !renderer.showGreebles;
    debugNoteEl.hidden = !renderer.showGreebles;
  } else if (key === 'l' && VIEW.meadow.gridOverlay) {
    renderer.showGrid = !renderer.showGrid;
    gridNoteEl.hidden = !renderer.showGrid;
  } else if (key === 'p' && VIEW.meadow.paths) {
    renderer.showPaths = !renderer.showPaths;
    pathsNoteEl.hidden = !renderer.showPaths;
  } else if (key === 'h') {
    renderer.showHappiness = !renderer.showHappiness;
    happyNoteEl.hidden = !renderer.showHappiness;
  } else if (key === 'b') {
    anim.setPaced(!anim.paced);
    pacedNoteEl.hidden = anim.paced;
  } else if (key === 't') {
    TRAITS.on = TRAITS.on ? 0 : 1;
    document.body.classList.toggle('show-traits', !!TRAITS.on);
    traitsNoteEl.hidden = !TRAITS.on;
  } else if (key === 'r') {
    // Off by default, so this note reads the ordinary way round: it
    // appears when the hearts are showing. The key itself is in the
    // legend beside the others, which is where it is discoverable.
    PURR.on = PURR.on ? 0 : 1;
    purrNoteEl.hidden = !PURR.on;
  } else {
    return;
  }
  anim.redraw();
});

initTheme();
initCards();
initTraitsDialog();
drawHeaderKitties();
start();
