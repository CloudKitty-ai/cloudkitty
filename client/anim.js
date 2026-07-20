/**
 * CloudKitty's animation layer (spec 005).
 *
 * Everything Article V scrutiny cares about lives in this file: what may
 * move, when, and why. The rules, from contracts/viewer-contract.md:
 *
 *  - Render only what was served. The screen shows a blend of the two
 *    newest served states at a progress given by the local clock and the
 *    served tick interval -- plus beats derived from differences between
 *    those states. Nothing else.
 *  - Never extrapolate: progress clamps at the newest state. A late tick
 *    means the world holds still, never a predicted step.
 *  - Newest wins: a fresh state preempts any in-flight animation.
 *  - Snap across discontinuities: first paint, reconnect, hidden-tab
 *    return, non-consecutive ticks, roster changes, teleport-sized jumps.
 *
 * The pure logic (`Presentation`) is DOM-free and testable; the `anim`
 * object at the bottom wires the browser (rAF loop, reduced-motion media
 * query, page visibility).
 */

/**
 * Every new visual tunable, named in one place (FR-017, Article VI). The
 * two `*Fallback` values are stand-ins for served configuration and are
 * replaced by /config when it lands.
 */
const VIEW = Object.freeze({
  // Server-owned values (with their named stand-ins).
  tickMsFallback: 800, // easing duration <- config.world.tick_ms
  distressPatienceFallback: 60, // thought bubble <- config.viewer.distress_patience_ticks

  // Interpolation & element comings-and-goings (US3).
  elementFadeShare: 0.4, // share of a tick over which spawns/expiries fade

  // Idle life (US4).
  idleMotionPeriodMs: 4600, // one flick/blink about this often
  idleMotionWindowMs: 420, // and lasting about this long
  breathePeriodMs: 3400, // the slow ambient cycle for resting poses

  // Beats (US5).
  reliefSparkleDrop: 15, // need-points a drop must exceed to sparkle
  sadBeatMs: 1600,
  sparkleMs: 1000,

  // Ambient life & juice (US6) -- each effect individually disableable.
  ambient: Object.freeze({
    waterShimmer: true,
    sunbeamPulse: true,
    dustMotes: true,
    grassSway: true,
    cloudShadows: true,
  }),
  ambientPeriodMs: 5200,
  cloudPeriodMs: 60000,
  bubblePopShare: 0.35, // share of a tick a speech bubble spends popping in
});

function easeInOutCubic(t) {
  return t < 0.5 ? 4 * t * t * t : 1 - (-2 * t + 2) ** 3 / 2;
}

/** A little overshoot-and-settle, for things that pop in (US6 juice). */
function easeOutBack(t) {
  const c1 = 1.70158;
  const c3 = c1 + 1;
  return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2;
}

/**
 * The state-pair store plus per-kitty presentational memory. Consumes
 * served worlds; produces the view the renderer draws. No DOM, no fetches.
 */
class Presentation {
  constructor() {
    this.prev = null;
    this.curr = null;
    this.currArrivedAt = 0;
    this.generation = 0;
    this.lastPushGeneration = -1;
    this.discontinuous = true;
    this.tickMs = VIEW.tickMsFallback;
    this.distressPatienceTicks = VIEW.distressPatienceFallback;
    this.facings = new Map(); // id -> 'left' | 'right'
    this.movedNow = new Map(); // id -> bool, for this pair
    this.sleepingSince = new Map(); // id -> tick its current sleep began
    this.oneShots = new Map(); // id -> { kind, t0, duration }, one slot each
    this.newElementIds = new Set();
    this.expiredElements = [];
  }

  /** Reconnects and hidden-tab returns break continuity by definition. */
  bumpGeneration() {
    this.generation += 1;
  }

  pushState(world, now) {
    const prev = this.curr;
    this.prev = prev;
    this.curr = world;
    this.currArrivedAt = now;

    const rosterChanged =
      prev &&
      prev.kitties.map((k) => k.id).join(',') !==
        world.kitties.map((k) => k.id).join(',');
    // Kitties step at most one tile per tick, so anything larger is not
    // motion -- it is a different moment of the world.
    const teleported =
      prev &&
      !rosterChanged &&
      world.kitties.some((k) => {
        const was = prev.kitties.find((p) => p.id === k.id);
        return (
          Math.abs(k.pos.x - was.pos.x) > 1 || Math.abs(k.pos.y - was.pos.y) > 1
        );
      });
    this.discontinuous =
      !prev ||
      this.generation !== this.lastPushGeneration ||
      world.tick !== prev.tick + 1 ||
      Boolean(rosterChanged) ||
      Boolean(teleported);
    this.lastPushGeneration = this.generation;

    if (this.discontinuous) {
      // An unrelated pair must never blend: snap, and start memory afresh.
      // (A mid-sleep snapshot shows the held curl, not a replayed settle.)
      this.prev = null;
      this.facings.clear();
      this.movedNow.clear();
      this.sleepingSince.clear();
      this.oneShots.clear();
      this.newElementIds = new Set();
      this.expiredElements = [];
      return;
    }

    // Facing memory (FR-004): the horizontal component of the last move,
    // kept while standing still, derived only from served positions. The
    // same pass notes falling-asleep edges, so the curl transition plays
    // once and only once (US4 acceptance 3).
    this.movedNow.clear();
    for (const kitty of world.kitties) {
      const was = prev.kitties.find((p) => p.id === kitty.id);
      const dx = kitty.pos.x - was.pos.x;
      if (dx > 0) this.facings.set(kitty.id, 'right');
      else if (dx < 0) this.facings.set(kitty.id, 'left');
      this.movedNow.set(kitty.id, dx !== 0 || kitty.pos.y !== was.pos.y);

      const sleepingNow = kitty.activity?.state === 'sleeping';
      if (sleepingNow && was.activity?.state !== 'sleeping') {
        this.sleepingSince.set(kitty.id, world.tick);
      } else if (!sleepingNow) {
        this.sleepingSince.delete(kitty.id);
      }

      // Beats (US5, research R5): derived here, once per served pair, from
      // served fields and their differences -- never invented, never
      // re-derived per frame. One slot per kitty; the newest wins.
      // (Speech-bubble pop-in is deliberately not a beat -- analyze I2.)
      const relieved = Object.entries(kitty.needs ?? {}).some(
        ([need, value]) =>
          (was.needs?.[need] ?? 0) - value >= VIEW.reliefSparkleDrop,
      );
      if (relieved) {
        this.oneShots.set(kitty.id, {
          kind: 'sparkle',
          t0: now,
          duration: VIEW.sparkleMs,
        });
      }
      const chaseKey = (a) => `${JSON.stringify(a.target)}@${a.until}`;
      const knownChases = new Set((was.abandoned_chases ?? []).map(chaseKey));
      const gaveUp = (kitty.abandoned_chases ?? []).some(
        (a) => !knownChases.has(chaseKey(a)),
      );
      if (gaveUp) {
        this.oneShots.set(kitty.id, {
          kind: 'sad',
          t0: now,
          duration: VIEW.sadBeatMs,
        });
      }
      const action = kitty.last_action;
      if (action?.action === 'play' && action.target == null) {
        // Solo play: the imaginary plaything appears for exactly the tick
        // the pounce animation plays (FR-009).
        this.oneShots.set(kitty.id, {
          kind: 'plaything',
          t0: now,
          duration: this.tickMs,
        });
      }
    }

    // Elements fade in and out; they never glide from nowhere.
    const prevIds = new Set(prev.elements.map((e) => e.id));
    const currIds = new Set(world.elements.map((e) => e.id));
    this.newElementIds = new Set(
      world.elements.filter((e) => !prevIds.has(e.id)).map((e) => e.id),
    );
    this.expiredElements = prev.elements.filter((e) => !currIds.has(e.id));
  }

  /** 0..1 through the current tick. Clamped: never past the newest state. */
  progress(now) {
    if (!this.curr || this.discontinuous) return 1;
    return Math.min(1, (now - this.currArrivedAt) / this.tickMs);
  }

  facingFor(id) {
    return this.facings.get(id) ?? 'left';
  }

  movedFor(id) {
    return this.movedNow.get(id) ?? false;
  }

  /** Float tile position: the eased blend of the two newest served states. */
  posFor(kitty, now) {
    const was = this.prev?.kitties.find((p) => p.id === kitty.id);
    if (!was) return { x: kitty.pos.x, y: kitty.pos.y };
    const t = easeInOutCubic(this.progress(now));
    return {
      x: was.pos.x + (kitty.pos.x - was.pos.x) * t,
      y: was.pos.y + (kitty.pos.y - was.pos.y) * t,
    };
  }

  /**
   * The fall-asleep settle (US4): on the very tick sleep begins, the first
   * half of the tick still shows the loaf, so the curl reads as a
   * transition -- and later sleeping ticks hold the curl without replaying.
   */
  adjustPose(id, pose, now) {
    if (
      pose === 'sleep-curl' &&
      this.sleepingSince.get(id) === this.curr?.tick &&
      this.progress(now) < 0.5
    ) {
      return 'loaf';
    }
    return pose;
  }

  /**
   * Phase and micro-motion for one kitty (US4). Action poses run on the
   * tick clock (their whole animation fits the tick that served them);
   * resting poses breathe on a slow local cycle; idle cats get their
   * scheduled blink, tail flick, or ear twitch -- gentle, occasional, and
   * never during an action, so idle motion can never imply one (FR-008).
   */
  motionFor(id, pose, now) {
    const isAction =
      pose === 'pouncing' ||
      pose === 'eating' ||
      pose === 'drinking' ||
      pose === 'grooming' ||
      pose === 'walking';
    if (isAction) return { phase: this.progress(now) };

    const seed = id * 997;
    const motion = {
      phase: ((now + seed) % VIEW.breathePeriodMs) / VIEW.breathePeriodMs,
    };
    if (pose === 'sleep-curl') return motion; // sleepers just breathe

    // Idle and loafing cats are never statues: one small motion per period,
    // cycling blink -> tail flick -> ear twitch, offset per kitty.
    const wobble = now + id * 1337;
    const at = wobble % VIEW.idleMotionPeriodMs;
    if (at < VIEW.idleMotionWindowMs) {
      const kind = Math.floor(wobble / VIEW.idleMotionPeriodMs) % 3;
      const w = at / VIEW.idleMotionWindowMs;
      if (kind === 0) motion.eyesOverride = 'closed'; // a blink
      else if (kind === 1) motion.phase = w; // one quick tail flick
      else motion.earsBack = w < 0.5; // an ear twitch
    }
    return motion;
  }

  /** The active one-shot beat for a kitty, with its own 0..1 progress. */
  oneShotFor(id, now) {
    const beat = this.oneShots.get(id);
    if (!beat) return null;
    const t = (now - beat.t0) / beat.duration;
    if (t >= 1) {
      this.oneShots.delete(id);
      return null;
    }
    return { kind: beat.kind, t };
  }

  /** Sustained expression, a pure function of the newest state (FR-010):
   * a cat mid-pursuit wears determined eyes for as long as it hunts. */
  expressionFor(kitty) {
    return kitty.pursuit ? 'focused' : undefined;
  }

  /**
   * The long-wanted need, if any (FR-012): the longest-running served
   * distress at or past the served patience threshold -- the panel cue's
   * exact comparison (>=, analyze A1) and the same threshold value. At
   * most one; null when nothing has waited that long.
   */
  thoughtFor(kitty) {
    const since = kitty.distress_since;
    if (!since || !this.curr) return null;
    let oldest = null;
    for (const [need, startTick] of Object.entries(since)) {
      const age = this.curr.tick - startTick;
      if (age >= this.distressPatienceTicks && (!oldest || age > oldest.age)) {
        oldest = { need, age };
      }
    }
    return oldest?.need ?? null;
  }

  elementAlphaFor(el, now) {
    if (!this.newElementIds.has(el.id)) return 1;
    return Math.min(1, this.progress(now) / VIEW.elementFadeShare);
  }

  expiredAlpha(now) {
    return Math.max(0, 1 - this.progress(now) / VIEW.elementFadeShare) * 0.7;
  }

  /**
   * The frame the renderer draws. `still` (reduced motion, or a snap after
   * a discontinuity) is simply progress = 1 with no fades -- one draw path
   * for both modes, so they cannot drift apart.
   */
  viewAt(now, still) {
    return {
      now,
      still,
      progress: still ? 1 : this.progress(now),
      posFor: (kitty) =>
        still ? { x: kitty.pos.x, y: kitty.pos.y } : this.posFor(kitty, now),
      facingFor: (id) => this.facingFor(id),
      movedFor: (id) => this.movedFor(id),
      adjustPose: (id, pose) => (still ? pose : this.adjustPose(id, pose, now)),
      // Still frames get the static pose for the state, nothing more
      // (FR-015): phase 0, no blinks, no flicks.
      motionFor: (id, pose) => (still ? { phase: 0 } : this.motionFor(id, pose, now)),
      // One-shot particles rest under reduced motion; the sustained
      // *informational* cues (focused eyes, the thought bubble) do not --
      // they carry state, not motion (R6).
      oneShotFor: (id) => (still ? null : this.oneShotFor(id, now)),
      expressionFor: (kitty) => this.expressionFor(kitty),
      thoughtFor: (kitty) => this.thoughtFor(kitty),
      elementAlphaFor: (el) => (still ? 1 : this.elementAlphaFor(el, now)),
      expired: still ? [] : this.expiredElements,
      expiredAlpha: still ? 0 : this.expiredAlpha(now),
      // Ambient life (US6): absent entirely under reduced motion (FR-013).
      ambient: still ? null : { now },
      // Juice (US6): a fresh meow pops in with a small settle; the over-cat
      // happiness bar eases between the two served values on the same
      // progress clock as everything else (FR-014, FR-019). The engine
      // stamps a meow during the apply phase and advances the tick counter
      // before publishing, so the freshest served meow always reads
      // curr.tick - 1 -- a meow from the tick that just closed is the new
      // one (review fix: comparing against curr.tick matched nothing, and
      // the pop-in never played).
      bubbleScaleFor: (meow) => {
        if (still || !this.curr || meow.tick !== this.curr.tick - 1) return 1;
        return easeOutBack(Math.min(1, this.progress(now) / VIEW.bubblePopShare));
      },
      barValueFor: (kitty) => {
        if (still) return kitty.happiness;
        const was = this.prev?.kitties.find((p) => p.id === kitty.id);
        if (!was) return kitty.happiness;
        return (
          was.happiness +
          (kitty.happiness - was.happiness) * easeInOutCubic(this.progress(now))
        );
      },
    };
  }
}

/**
 * The browser side: one rAF loop, stopped whenever it has no business
 * running (hidden page, reduced motion). Everything here is wiring; the
 * decisions above stay pure.
 */
const anim = {
  presentation: new Presentation(),
  renderer: null,
  rafId: 0,
  reduced: false,

  init(renderer) {
    this.renderer = renderer;

    const media = window.matchMedia('(prefers-reduced-motion: reduce)');
    const applyMotionPreference = () => {
      this.reduced = media.matches;
      // The panel's CSS transitions go still with the canvas (FR-015).
      document.body.classList.toggle('reduced-motion', this.reduced);
      if (this.reduced) this.stopLoop();
      this.redraw();
      if (!this.reduced) this.startLoop();
    };
    media.addEventListener('change', applyMotionPreference);
    this.reduced = media.matches;
    document.body.classList.toggle('reduced-motion', this.reduced);

    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        // Zero animation work while hidden (FR-016). Frames still arrive
        // and update the store cheaply, so the return is instant.
        this.stopLoop();
      } else {
        // The return snaps to the newest state; no catch-up replay.
        this.presentation.bumpGeneration();
        this.redraw();
        this.startLoop();
      }
    });
  },

  /** A served world arrived (first snapshot or WS frame). */
  push(world) {
    this.presentation.pushState(world, performance.now());
    if (document.hidden) return;
    if (this.reduced) this.redraw();
    else this.startLoop();
  },

  /** One static draw of the newest state (reduced motion, snaps, toggles). */
  redraw() {
    if (!this.presentation.curr || !this.renderer) return;
    this.renderer.draw(
      this.presentation.curr,
      this.presentation.viewAt(performance.now(), true),
    );
  },

  startLoop() {
    if (this.rafId || this.reduced) return;
    const step = () => {
      this.rafId = 0;
      if (document.hidden || this.reduced) return;
      const p = this.presentation;
      if (p.curr) this.renderer.draw(p.curr, p.viewAt(performance.now(), false));
      this.rafId = requestAnimationFrame(step);
    };
    this.rafId = requestAnimationFrame(step);
  },

  stopLoop() {
    if (this.rafId) cancelAnimationFrame(this.rafId);
    this.rafId = 0;
  },

  setTickMs(ms) {
    if (Number.isFinite(ms) && ms >= 1) this.presentation.tickMs = ms;
  },

  setDistressPatience(ticks) {
    if (Number.isFinite(ticks) && ticks >= 1) {
      this.presentation.distressPatienceTicks = ticks;
    }
  },

  bumpGeneration() {
    this.presentation.bumpGeneration();
  },
};
