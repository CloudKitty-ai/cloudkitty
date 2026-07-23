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

/**
 * The hour themes (design experiment rounds two and three): day, golden
 * hour, and night. One applier flips everything that carries color: the
 * CSS tokens (body.dusk / body.night), the canvas palettes (meadow,
 * props), the renderer's theme (fireflies, twilight fur), and the baked
 * ground cache.
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
const THEMES = ['day', 'dusk', 'night'];
const THEME_ICONS = { day: '☀️', dusk: '🌇', night: '🌙' };
const MODE_CYCLE = ['auto', 'day', 'dusk', 'night'];
const AUTO_ICON = '🌤️'; // the sky decides

/**
 * One world day, in ticks (at the default 1s tick: a 10-minute day).
 * Dawn and dusk both wear the golden-hour set -- the light is the same,
 * only the direction differs, and ticks have no compass.
 */
const WORLD_DAY_PHASES = Object.freeze([
  ['day', 240],
  ['dusk', 60], // sunset
  ['night', 240],
  ['dusk', 60], // dawn
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

let themeMode = 'auto'; // 'auto' | 'day' | 'dusk' | 'night'
let currentTheme = null; // the visual theme actually applied

/** Applies the mode's theme (auto reads the world clock) and syncs the
 * toggle. Cheap when nothing changed, so render() may call it per tick. */
function applyTheme() {
  const theme =
    themeMode === 'auto' ? hourForTick(latestWorld?.tick ?? 0) : themeMode;

  const toggle = document.getElementById('theme-toggle');
  if (toggle) {
    // The button wears the mode: the current hour when chosen by hand,
    // the "sky decides" glyph on auto (the page itself shows the hour).
    // The label says where the next click goes.
    const icon = themeMode === 'auto' ? AUTO_ICON : THEME_ICONS[themeMode];
    if (toggle.textContent !== icon) toggle.textContent = icon;
    const next = MODE_CYCLE[(MODE_CYCLE.indexOf(themeMode) + 1) % MODE_CYCLE.length];
    const names = { auto: "the world's sky", day: 'day', dusk: 'golden hour', night: 'night' };
    toggle.setAttribute('aria-label', `switch to ${names[next]}`);
  }

  if (theme === currentTheme) return;
  currentTheme = theme;
  document.body.classList.toggle('dusk', theme === 'dusk');
  document.body.classList.toggle('night', theme === 'night');
  setMeadowPalette(theme);
  setPropPalette(theme);
  renderer.theme = theme;
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

function setStatus(text, connected) {
  statusEl.textContent = text;
  statusEl.classList.toggle('disconnected', !connected);
}

function render(world) {
  latestWorld = world;
  // The world's sky: on auto, the hour follows the served tick. applyTheme
  // early-returns when the hour hasn't changed, so this is per-tick cheap.
  if (themeMode === 'auto') applyTheme();
  anim.push(world);
  tickEl.textContent = world.tick;
  renderPanel(world);
}

/** Kitty cards: name, mood, happiness, and how each need is doing. */
function renderPanel(world) {
  // Rebuild only when the roster changes; otherwise update in place so the CSS
  // transitions can do their thing.
  const needsRebuild = panelEl.childElementCount !== world.kitties.length;
  if (needsRebuild) {
    panelEl.innerHTML = '';
    for (const kitty of world.kitties) {
      panelEl.appendChild(buildKittyCard(kitty));
    }
  }

  world.kitties.forEach((kitty, index) => {
    const card = panelEl.children[index];
    if (!card) return;
    card.querySelector('.name > span').textContent = kitty.name;
    // The sustained purr (spec 011) is a contentment signal, so it rides the
    // mood line -- and the card is fixed-width (index.html), so no line ever
    // resizes the portrait. `purring_until` in the payload means rumbling now.
    const purring = kitty.purring_until != null ? ' · purring 💕' : '';
    card.querySelector('.mood').textContent = moodFor(kitty) + purring;
    card.querySelector('.doing').textContent = doingFor(kitty, world);
    card.querySelector('.patience').textContent = patienceFor(kitty, world);

    const happinessBar = card.querySelector('.happiness > span');
    happinessBar.style.width = `${clampPercent(kitty.happiness)}%`;
    happinessBar.style.backgroundColor = happinessColor(kitty.happiness);

    for (const [need, value] of Object.entries(kitty.needs)) {
      const bar = card.querySelector(`[data-need="${need}"] > span`);
      if (!bar) continue;
      bar.style.width = `${clampPercent(value)}%`;
      // Needs are pressure: a full bar is a cat that wants something.
      bar.style.backgroundColor = needColor(value);
    }
  });
}

function buildKittyCard(kitty) {
  const card = document.createElement('div');
  card.className = 'kitty-card';

  const name = document.createElement('div');
  name.className = 'name';
  // The card wears the kitty's own portrait (spec 005 polish): the same
  // drawCat the world uses, drawn once -- appearance never changes.
  const portrait = document.createElement('canvas');
  const portraitSize = 22;
  const dpr = window.devicePixelRatio || 1;
  portrait.width = portraitSize * dpr;
  portrait.height = portraitSize * dpr;
  portrait.style.width = `${portraitSize}px`;
  portrait.style.height = `${portraitSize}px`;
  const portraitCtx = portrait.getContext('2d');
  portraitCtx.setTransform(dpr, 0, 0, dpr, 0, 0);
  drawCat(portraitCtx, {
    pose: 'idle',
    appearance: appearanceFor(kitty.id),
    facing: 'right', // toward its own name
    size: portraitSize,
    phase: 0,
  });
  name.appendChild(portrait);
  name.appendChild(document.createElement('span'));
  card.appendChild(name);

  const doing = document.createElement('div');
  doing.className = 'doing';
  card.appendChild(doing);

  const mood = document.createElement('div');
  mood.className = 'mood';
  card.appendChild(mood);

  const happiness = document.createElement('div');
  happiness.className = 'bar happiness';
  happiness.appendChild(document.createElement('span'));
  card.appendChild(happiness);

  const patience = document.createElement('div');
  patience.className = 'patience';
  card.appendChild(patience);

  const needsLabel = document.createElement('div');
  needsLabel.className = 'section-label';
  needsLabel.textContent = 'needs';
  card.appendChild(needsLabel);

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
  card.appendChild(needs);

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

function needColor(value) {
  if (value >= 75) return '#efa98b';
  if (value >= 45) return '#f3cf7a';
  return '#bcd9c0';
}

async function fetchSnapshot() {
  const response = await fetch('/world');
  if (!response.ok) throw new Error(`GET /world returned ${response.status}`);
  return response.json();
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

  socket.addEventListener('message', (event) => {
    try {
      render(JSON.parse(event.data));
    } catch (err) {
      console.error('could not read a world update', err);
    }
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
    render(await fetchSnapshot());
    subscribe();
  } catch (err) {
    console.error(err);
    setStatus('server unreachable — retrying…', false);
    setTimeout(start, RECONNECT_DELAY_MS);
  }
}

// The debug toggles, all in one mold (spec 008 FR-004/FR-009): `g` reveals
// greebles, `l` the demoted grid lines, `p` the session's worn paths. Each
// flips a renderer flag, syncs its footer note, and redraws -- and every
// fresh load starts with all three off.
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
  } else {
    return;
  }
  anim.redraw();
});

initTheme();
drawHeaderKitties();
start();
