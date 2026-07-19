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

const NEED_LABELS = {
  eat: 'eat',
  drink: 'drink',
  sleep: 'sleep',
  play: 'play',
  cuddle: 'cuddle',
  bath: 'bath',
};

const RECONNECT_DELAY_MS = 1000;

let latestWorld = null;

function setStatus(text, connected) {
  statusEl.textContent = text;
  statusEl.classList.toggle('disconnected', !connected);
}

function render(world) {
  latestWorld = world;
  renderer.draw(world);
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
    card.querySelector('.name').textContent = `${faceFor(kitty)} ${kitty.name}`;
    card.querySelector('.mood').textContent = moodFor(kitty);
    card.querySelector('.doing').textContent = doingFor(kitty, world);

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
  card.appendChild(name);

  const mood = document.createElement('div');
  mood.className = 'mood';
  card.appendChild(mood);

  const doing = document.createElement('div');
  doing.className = 'doing';
  card.appendChild(doing);

  const happiness = document.createElement('div');
  happiness.className = 'bar happiness';
  happiness.appendChild(document.createElement('span'));
  card.appendChild(happiness);

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

function faceFor(kitty) {
  const state = kitty.activity?.state;
  if (state === 'sleeping') return '😴';
  if (state === 'resting') return '😌';
  return '🐱';
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
      return `playing with ${targetText(action, world, friendName)}`;
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

function subscribe() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const socket = new WebSocket(`${protocol}//${window.location.host}/ws`);

  socket.addEventListener('open', () => setStatus('watching live', true));

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
    render(await fetchSnapshot());
    subscribe();
  } catch (err) {
    console.error(err);
    setStatus('server unreachable — retrying…', false);
    setTimeout(start, RECONNECT_DELAY_MS);
  }
}

// The debug toggle: greebles are always in the data, never on screen, until now.
window.addEventListener('keydown', (event) => {
  if (event.key !== 'g' && event.key !== 'G') return;
  renderer.showGreebles = !renderer.showGreebles;
  debugNoteEl.hidden = !renderer.showGreebles;
  if (latestWorld) renderer.draw(latestWorld);
});

start();
