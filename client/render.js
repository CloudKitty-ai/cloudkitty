/**
 * CloudKitty's renderer.
 *
 * A pure view: it draws whatever world the server sent and computes nothing about
 * the simulation itself (Article V). The one piece of judgement it makes is a
 * presentational one -- greebles are not drawn, which is why kitties appear to
 * chase nothing at all. Press `g` to see what they can see.
 */

const TILE_COLORS = {
  grass: '#e7f2df',
  grassAlt: '#e1eed8',
  gridLine: 'rgba(140, 170, 130, 0.16)',
  water: '#bfe3f2',
  waterRim: '#9ccfe6',
  sunbeam: 'rgba(255, 226, 138, 0.55)',
  sunbeamRim: 'rgba(255, 206, 92, 0.75)',
};

const MEOW_TEXT = {
  want_eat: 'I want to eat!',
  want_drink: 'I want to drink!',
  follow_me: 'Follow me!',
  want_play: 'I want to play!',
  want_cuddle: 'I want to cuddle!',
  purr: 'purrrr',
};

/** How many ticks a speech bubble lingers on screen. */
const BUBBLE_TICKS = 3;

/**
 * Which pose a served kitty is in (spec 005, data-model table): the activity
 * state speaks first, then the applied action, then movement, then idle.
 * Pure function of served data -- nothing here predicts (Article V).
 */
function poseFor(kitty, moved) {
  const state = kitty.activity?.state;
  if (state === 'sleeping') return 'sleep-curl';
  if (state === 'resting') return 'loaf';
  if (state === 'eating') return 'eating';
  if (state === 'drinking') return 'drinking';
  if (state === 'grooming') return 'grooming';
  const action = kitty.last_action?.action;
  if (action === 'play' || action === 'chase') return 'pouncing';
  if (moved) return 'walking';
  return 'idle';
}

class WorldRenderer {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.showGreebles = false;
    this.tile = 22;
  }

  /** Fits the canvas to the world, accounting for retina displays. */
  resizeFor(world) {
    const maxPixels = 720;
    this.tile = Math.max(8, Math.floor(maxPixels / Math.max(world.width, world.height)));
    const cssWidth = this.tile * world.width;
    const cssHeight = this.tile * world.height;
    const dpr = window.devicePixelRatio || 1;

    if (this.canvas.style.width !== `${cssWidth}px`) {
      this.canvas.style.width = `${cssWidth}px`;
      this.canvas.style.height = `${cssHeight}px`;
      this.canvas.width = Math.floor(cssWidth * dpr);
      this.canvas.height = Math.floor(cssHeight * dpr);
      this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
  }

  draw(world, presentation) {
    this.resizeFor(world);
    const ctx = this.ctx;
    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    this.drawGround(world);
    // Sunbeams are warmth on the ground, so they go under everything else.
    for (const el of world.elements) {
      if (el.kind === 'sunbeam') this.drawSunbeam(el);
    }
    for (const el of world.elements) {
      if (el.kind !== 'sunbeam') this.drawElement(el);
    }
    for (const kitty of world.kitties) {
      this.drawKitty(kitty, world, presentation);
    }
    this.drawBubbles(world);
  }

  drawGround(world) {
    const ctx = this.ctx;
    for (let y = 0; y < world.height; y++) {
      for (let x = 0; x < world.width; x++) {
        ctx.fillStyle = (x + y) % 2 === 0 ? TILE_COLORS.grass : TILE_COLORS.grassAlt;
        ctx.fillRect(x * this.tile, y * this.tile, this.tile, this.tile);
      }
    }
    ctx.strokeStyle = TILE_COLORS.gridLine;
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (let x = 0; x <= world.width; x++) {
      ctx.moveTo(x * this.tile + 0.5, 0);
      ctx.lineTo(x * this.tile + 0.5, world.height * this.tile);
    }
    for (let y = 0; y <= world.height; y++) {
      ctx.moveTo(0, y * this.tile + 0.5);
      ctx.lineTo(world.width * this.tile, y * this.tile + 0.5);
    }
    ctx.stroke();
  }

  drawSunbeam(el) {
    const ctx = this.ctx;
    const { x, y } = this.tileOrigin(el.pos);
    ctx.fillStyle = TILE_COLORS.sunbeam;
    this.roundRect(x + 1, y + 1, this.tile - 2, this.tile - 2, 6);
    ctx.fill();
    ctx.strokeStyle = TILE_COLORS.sunbeamRim;
    ctx.lineWidth = 1.5;
    ctx.stroke();
  }

  drawElement(el) {
    // The greeble rule: present in the data, absent from the picture.
    if (el.kind === 'greeble' && !this.showGreebles) return;

    const ctx = this.ctx;
    const { x, y } = this.tileOrigin(el.pos);
    const cx = x + this.tile / 2;
    const cy = y + this.tile / 2;

    switch (el.kind) {
      case 'water': {
        ctx.fillStyle = TILE_COLORS.water;
        this.roundRect(x + 2, y + 2, this.tile - 4, this.tile - 4, 8);
        ctx.fill();
        ctx.strokeStyle = TILE_COLORS.waterRim;
        ctx.lineWidth = 1.5;
        ctx.stroke();
        break;
      }
      case 'chow': {
        this.emoji('🍥', cx, cy);
        // A little pip per remaining serving, so you can watch a bowl run down.
        const servings = Math.min(el.servings ?? 0, 5);
        ctx.fillStyle = '#c98b6b';
        for (let i = 0; i < servings; i++) {
          ctx.beginPath();
          ctx.arc(x + 4 + i * 3.2, y + this.tile - 3, 1.2, 0, Math.PI * 2);
          ctx.fill();
        }
        break;
      }
      case 'bug':
        this.emoji('🐛', cx, cy);
        break;
      case 'greeble':
        // Only ever reached with the debug toggle on.
        ctx.globalAlpha = 0.55;
        this.emoji('👻', cx, cy);
        ctx.globalAlpha = 1;
        break;
      default:
        break;
    }
  }

  drawKitty(kitty, world, presentation) {
    const ctx = this.ctx;
    const { x, y } = this.tileOrigin(kitty.pos);
    const cx = x + this.tile / 2;
    const cy = y + this.tile / 2;
    const state = kitty.activity?.state ?? 'idle';

    // A soft shadow so cats sit on the grass rather than float above it.
    ctx.fillStyle = 'rgba(140, 120, 100, 0.15)';
    ctx.beginPath();
    ctx.ellipse(cx, cy + this.tile * 0.32, this.tile * 0.3, this.tile * 0.12, 0, 0, Math.PI * 2);
    ctx.fill();

    // The approved vector cat (spec 005 US2): identity from the kitty's id,
    // pose from served state, facing from its last horizontal movement.
    drawCat(ctx, {
      pose: poseFor(kitty, presentation?.movedFor(kitty.id) ?? false),
      appearance: appearanceFor(kitty.id),
      facing: presentation?.facingFor(kitty.id) ?? 'left',
      size: this.tile,
      phase: 0,
      x,
      y,
    });

    if (state === 'sleeping') {
      ctx.save();
      ctx.globalAlpha = 0.75;
      this.emoji('💤', cx + this.tile * 0.42, cy - this.tile * 0.42, 0.45);
      ctx.restore();
    }

    // Cuddling cats get a little heart between them.
    const partner = kitty.activity?.with_friend;
    if (partner !== undefined && partner !== null) {
      const friend = world.kitties.find((k) => k.id === partner);
      if (friend) {
        const fx = (friend.pos.x + 0.5) * this.tile;
        const fy = (friend.pos.y + 0.5) * this.tile;
        this.emoji('💗', (cx + fx) / 2, (cy + fy) / 2 - this.tile * 0.15, 0.42);
      }
    }

    this.drawHappinessBar(kitty, x, y);
  }

  drawHappinessBar(kitty, x, y) {
    const ctx = this.ctx;
    const width = this.tile - 6;
    const height = 3;
    const bx = x + 3;
    const by = y + this.tile - 3.5;

    ctx.fillStyle = 'rgba(255, 255, 255, 0.75)';
    ctx.fillRect(bx, by, width, height);
    ctx.fillStyle = happinessColor(kitty.happiness);
    ctx.fillRect(bx, by, (width * clamp01(kitty.happiness / 100)), height);
  }

  drawBubbles(world) {
    const recent = (world.recent_meows || []).filter(
      (m) => m.tick > world.tick - BUBBLE_TICKS,
    );
    // One bubble per cat: the newest thing they said.
    const newest = new Map();
    for (const meow of recent) newest.set(meow.kitty_id, meow);

    for (const meow of newest.values()) {
      const kitty = world.kitties.find((k) => k.id === meow.kitty_id);
      if (!kitty) continue;
      this.drawBubble(kitty, MEOW_TEXT[meow.kind] || '…');
    }
  }

  drawBubble(kitty, text) {
    const ctx = this.ctx;
    const { x, y } = this.tileOrigin(kitty.pos);
    ctx.font = '600 11px ui-rounded, system-ui, sans-serif';
    const padding = 6;
    const width = ctx.measureText(text).width + padding * 2;
    const height = 18;

    // Keep the bubble on screen even for cats hugging the edges.
    let bx = x + this.tile / 2 - width / 2;
    bx = Math.max(2, Math.min(bx, this.canvas.clientWidth - width - 2));
    const by = Math.max(2, y - height - 4);

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
  }

  // ---- small helpers ----

  tileOrigin(pos) {
    return { x: pos.x * this.tile, y: pos.y * this.tile };
  }

  emoji(glyph, cx, cy, scale = 0.72) {
    const ctx = this.ctx;
    ctx.font = `${Math.floor(this.tile * scale)}px "Apple Color Emoji", "Segoe UI Emoji", sans-serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(glyph, cx, cy);
  }

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
