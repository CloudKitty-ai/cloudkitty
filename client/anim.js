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

/** The element each feeding action consumes, and so the thing to face. */
const FEEDING_KIND = Object.freeze({ eat: 'chow', drink: 'water' });

/**
 * The applied actions that ARE a pursuit happening right now, as against
 * a pursuit merely being on file.
 *
 * `pursuit` is an intention and outlives the acts that serve it -- its own
 * documentation says it "survives a cat stopping for a drink on the way".
 * So it answers "what is this cat after", never "is she after it this
 * tick", and the hunter's face was reading it as if it answered both.
 *
 * Measured on the live world, 945 kitty-ticks (2026-08-16): of the ticks
 * that drew the hunting face, 27 were `chase` and 19 `move` -- the cat
 * going after something -- and 6 were `idle`, a cat standing still wearing
 * a hunter's eyes. Owner saw the same thing while resting and while
 * grooming; those are rarer than the sample was long, but they are this
 * list's absence, not a separate fault.
 *
 * `play` is here because it is how a hunt ENDS: a cat that reaches its bug
 * pounces with Play, and leaving it out would take the face away at the
 * one moment the hunt is most obviously a hunt.
 *
 * An allow-list, not a deny-list of the sitting-still actions, because the
 * owner's ask was that the face trigger "only when in active pursuit" -- so
 * an action nobody has thought about yet should read as not-hunting. Note
 * this does NOT touch the rule that an unresolvable QUARRY keeps the face:
 * different field, different question, still benefit of the doubt.
 */

/**
 * The element the engine would have picked for a feeding action at `pos`.
 *
 * A port of `adjacent_element_in`, plus the serving filter that
 * `adjacent_stocked_chow_in` puts on top of it: adjacency is manhattan
 * distance <= 1 (the cat's OWN tile included), and among the candidates the
 * nearest wins with ties broken by lowest id. Both halves matter -- a cat
 * between two ponds faces the one the engine chose, not whichever the
 * elements array happened to list first.
 *
 * Deliberately mirrors the engine rather than approximating it. If the
 * predicate there ever changes, this silently disagrees, which is why a
 * test pins the tie-break rather than only the happy path.
 */
function nearestAdjacentOf(elements, pos, kind) {
  let best = null;
  let bestKey = null;
  for (const el of elements ?? []) {
    if (el.kind !== kind || !el.pos) continue;
    if (kind === 'chow' && !(el.servings > 0)) continue;
    const d = Math.abs(el.pos.x - pos.x) + Math.abs(el.pos.y - pos.y);
    if (d > 1) continue;
    const key = d * 1e9 + el.id;
    if (bestKey === null || key < bestKey) {
      best = el;
      bestKey = key;
    }
  }
  return best;
}

/**
 * Every new visual tunable, named in one place (FR-017, Article VI). The
 * two `*Fallback` values are stand-ins for served configuration and are
 * replaced by /config when it lands.
 */
const VIEW = Object.freeze({
  // Server-owned values (with their named stand-ins).
  tickMsFallback: 800, // easing duration <- config.world.tick_ms
  distressPatienceFallback: 60, // thought bubble <- config.viewer.distress_patience_ticks

  // Pacing (2026-08-11). How deep the delay line runs and how hard it
  // trims itself -- see `Pacer`. The depth is in whole states, so a target
  // of 1 means one spare arrival in hand at all times, which is a whole
  // tick of jitter absorbed with nothing visible.
  //
  // DEEPENING THIS IS FREE TODAY, AND WHY IT IS FREE IS THE PART TO KEEP.
  // Every pixel the viewer sees is derived from the frame being rendered --
  // the meows, the need bars, the tick readout, and the sky dial, which takes
  // `world.tick` and not a wall clock. So a deeper line moves ALL of it
  // together and there is no reference left to notice the delay against. At
  // depth 10 the meadow runs 8s behind live and nobody can tell, because
  // nothing on screen disagrees with anything else on screen.
  //
  // That holds only while the viewer is a WINDOW. The moment anything reaches
  // the simulation -- a "pet the cat" control, any round trip -- the delay
  // stops being invisible and becomes the whole feel of it: you would act on a
  // frame N ticks old and wait N more to see it land, at 800ms a tick. The
  // owner does not anticipate that (2026-08-20: this is a front end for an AI
  // experimentation engine, not a game), so this is a constraint on a future
  // feature rather than a caveat on this dial -- but it is the kind that gets
  // discovered as "why does the button feel broken" months later, by someone
  // who has no reason to suspect a buffer.
  //
  // The real cost of depth is the FILL, not the latency: a deep line fills by
  // running slow, measured at ~14.6s of visible slow motion at depth 5, on
  // every page load and every reconnect. Spec 032 is what removes that, which
  // is why a lookahead camera needs 032 to ship rather than merely to be
  // judged (BACKLOG, camera-logic entry).
  paceTargetDepth: 1,
  paceTrimMs: 60, // how far off the measured interval a full state of depth pulls
  paceDepthSmoothing: 0.34, // ~3 promotions
  paceIntervalSmoothing: 0.1, // ~10 promotions: the production rate, not its jitter
  paceRateMin: 0.5, // the pace may never leave this band around the served tick
  paceRateMax: 2,
  paceMaxBacklog: 8, // beyond this it is not a stutter, it is a backlog

  // Camera mode (spec 036). The camera holds the group at a legible scale
  // and following a kitty changes only where it AIMS, never how wide it
  // sits -- so hold-the-group and follow-one are one path differing by a
  // single value, the anchor.
  //
  // Every number here is a starting point to be judged in motion at the
  // live size, not a result. The rates are kitten.me's.
  camera: Object.freeze({
    // The zoom band, in PIXELS (spec 037). These two are a RATIO, not two
    // independent numbers: the zoom range is floorPx / ceilingPx, so moving
    // either one moves it and they are dialled as a pair. Judged in the
    // gallery-v2.html band card and pasted by the owner 2026-08-18.
    //
    // They SHOULD be independent, and are not yet -- per-platform deviation
    // is already visible at the small end and a client-controlled zoom would
    // need them to move separately (037 FR-003). Anything that later
    // decouples them is an improvement, not a regression.
    floorPx: 113, // zoom IN until a tile is about this big
    ceilingPx: 50, // widen until a tile would fall below this
    // ...and never widen so far that camera mode stops being worth having.
    // The camera must always draw a kitty at least this many times the size
    // the WHOLE-WORLD view would draw her at (owner, 2026-08-19).
    //
    // This is the job 036 did for free and 037 dropped: `nominalAcross: 10`
    // on a 20-tile world is exactly half of it, so 036's floor was 2.00x the
    // whole-world tile on EVERY display. Replacing it with a pixel target
    // made apparent size consistent and quietly made the zoom BENEFIT vary --
    // 3.33x on a phone against 1.05x on WQHD, where the camera at its widest
    // was 5% bigger than no camera at all.
    //
    // `cssWidth` cancels out of `cssWidth/ceilTiles >= k * cssWidth/world`,
    // so this is a pure tile cap of `world / k` -- 13.3 tiles on a 20-tile
    // world. It therefore binds only where the pixel ceiling would have
    // overshot, which is the large maps, and leaves small ones alone. It also
    // RETIRES ITSELF as the world grows: at 40x40 it allows 26.7 tiles and
    // the 50px target only asks for 24.
    minZoomVsBase: 1.5,
    // The most world-ROWS the camera may show, and the only limit here stated
    // on the vertical. It binds ONLY on a letterboxed canvas (aspect < 1),
    // which is a phone held sideways and nothing else -- everywhere else the
    // canvas is square, height is not the scarce axis, and `ceilingPx` already
    // governs.
    //
    // Landscape needed its own limit because the others cannot express one.
    // `ceilingPx` and `minZoomVsBase` are both stated ACROSS, so tightening
    // either to zoom a sideways phone in also zooms in every viewport where it
    // binds: `ceilingPx` 66 would re-close the PORTRAIT phone's zoom range to
    // nothing (7.60 tiles to 7.00, the defect spotted on the 340px map), and
    // `minZoomVsBase` 1.82 would take a 1200px desktop from 13.3 tiles to
    // 11.0. Measured 2026-08-20, both.
    //
    // SETTLED AT 7 (owner, 2026-08-20), and the reasoning is the useful part.
    // 6 was judged live first and looked good -- but the ceiling is the WIDEST
    // the camera goes, not a midpoint, so capping at 6 makes 66.7px the
    // SMALLEST a kitty is ever drawn in landscape and leaves the meadow no
    // room. The camera also sits at its ceiling most of the time today, which
    // makes the widest end the one you actually see. So: keep the wide end
    // wide, and earn the zoom-in with better camera logic rather than forcing
    // it with a dial. That is the queued camera-logic work, which sizes to the
    // chosen group once the fit can no longer hold everyone -- it moves the
    // camera INSIDE this range.
    //
    // At 7 the cap barely touches this handset: 7.41 rows uncapped to 7.00,
    // a 5.5% narrowing, 54.0px to 57.1px. **It is a bound, not a zoom
    // decision**, and it earns its place across devices rather than on this
    // one -- a taller landscape screen drifts past 8 rows uncapped, and this
    // holds every landscape screen at 7.
    //
    // Costed at the time, for whoever moves it: 6 = 66.7px at 10.8 across,
    // 5 = 80px at 9.0 across. Both make the widest view NARROWER, which is
    // the opposite of what landscape wanted.
    //
    // What it fixes is not the tile, which still scales with the canvas
    // (`tile = cssHeight / ceilingRows`), but the FRAMING: how much world is
    // in shot vertically is now a decision instead of a remainder. It used to
    // fall out of the large-viewport height, which is the one number in this
    // arc that has been guessed twice and measured never.
    ceilingRows: 7,
    minTiles: 7, // ...but never frame fewer tiles than this, so a small
    // viewport shows a scene rather than a keyhole. Where it binds the
    // kitties are drawn SMALLER than floorPx rather than the world being
    // cropped further (037 FR-006).
    //
    // 6 until 2026-08-19. The phone is the primary consumption path and
    // ~3 kitties in frame is the target, so the phone buys meadow here and
    // pays for it in apparent size: on a 380px map the floor tile goes
    // 63.3px -> 54.3px, still clear of the 50px `ceilingPx` bar.
    //
    // It is NOT a phone-only dial, which is the part that misleads. The
    // break-even is `minTiles * floorPx` = 791px, so every map below that
    // loses size at full zoom -- a 640px map goes 106.7px -> 91.4px. Maps
    // at or above 791px do not move at all.
    //
    // And on the smallest supported map it takes the zoom range to
    // NOTHING: at 340px the floor asks for 7 tiles and the ceiling's own
    // target asks for 6.8, so the ceiling is raised to meet the floor
    // (FR-013) and the camera pans without ever zooming. Zoom range first
    // appears at a 351px map, against 301px before. Accepted: the owner's
    // ruling of 2026-08-19 is that zoom range is instrumental, not a goal.
    // fitMarginTiles, panRate, zoomRate and hysteresis died with the
    // aim-chase model (spec 038): the margin is fitMarginFrac below, the
    // rates became episode durations, and incumbency replaced hysteresis.
    // The shot grammar (spec 038). Groups are connected components at this
    // link radius; measured (client-measurements/camera-aim): identity
    // survives a median 88s at 5, the phone re-frames least, 4 is twitchy
    // and 6 merges nearly the whole roster.
    linkTiles: 5,
    // Persistence, in TICKS, before the camera acts on a disjoint group:
    // a nearby group is ADMITTED by widening after nearDwellTicks; a far,
    // STRICTLY bigger one takes the shot with the one true pan after
    // farDwellTicks -- the owner's number ("numbers will always win out in
    // interest over 15+ ticks", 2026-08-20). Thresholds are compared at
    // exactly two sites in decide(), which is the spec-032 seam: a
    // lookahead buffer replaces the window's source, not the grammar.
    nearDwellTicks: 10, // owner-judged at the calm pass (2026-08-21; was 5 — stop re-opening negotiations with a 4th/5th group every few seconds)
    farDwellTicks: 15,
    // ...and a shed waits too (un-fit must persist this many consecutive
    // ticks). Added at acceptance measurement, 2026-08-21: the reference
    // sim never counted sheds, and the live grammar without this flapped
    // at the link boundary -- join free, shed instantly, rejoin -- at
    // 3/min on desktop and 8/min on the phone, blowing SC-003. Persistence
    // before action is the grammar's whole idea; FR-010 had simply missed
    // its dose.
    shedDwellTicks: 3,
    // A shot may keep a frame this much wider than it needs before the
    // hold eases it tighter (the 'breathe in', US3 scenario 2). Without
    // it the width only ever changed at membership events, ran stale-wide
    // (median 11.5 tiles against the fit's 9.2), and SC-004's size bar
    // failed at 1.16x. 1.3 first: the measured median oversize is 1.25,
    // so a 1.3 threshold never fired at the median and the width never
    // moved -- the dial must sit BELOW the drift it is meant to catch.
    tightenFrac: 1.2, // owner-judged at the calm pass (2026-08-21; was 1.15 — 1.3 doubled the calm but broke SC-004's size floor)
    // The inner region of the frame the shot may wander inside without the
    // camera moving AT ALL. A member pressing past it earns one eased
    // correction, then stillness again (038 FR-006/FR-007).
    // Owner-judged 2026-08-22 on the live world after the Biscuit 2.0
    // cutover: 0.88 held rest at 54%% against SC-001's 60%% floor, because a
    // tighter clowder puts nearly all five cats in one frame and the safe
    // zone is then under near-continuous pressure. A wider deadzone
    // answers a PERSISTENT press; more dwell does not (pressDwellTicks 8
    // bought 5 points, this buys 27). Restores rest 81%%, median calm
    // spell 4.4s, size unchanged at 1.51x, zero empty frames.
    safeZoneFrac: 0.92, // owner-judged (2026-08-22; was 0.88, was 0.80)
    // Persistence before action, applied to the HOLD (owner, 2026-08-21
    // calm pass): a press (or standing slack) must survive this many
    // consecutive ticks before a correction latches from rest. A cat
    // leaning out and back costs nothing; a real walk still gets tracked
    // ~2.4s in. Exempt: mid-episode re-aims (motion underway stays
    // continuous), a member leaving the FRAME, and an EMPTY frame --
    // SC-002 outranks calm.
    pressDwellTicks: 3,
    // Episode durations. Every camera-mode move latches a goal, eases over
    // one of these, snaps EXACTLY on arrival and returns to rest -- there
    // is no per-frame pursuit left to trail off (038 FR-006, research D7).
    moveMs: 2000, // corrections, widens, sheds, break re-frames (owner-judged live, 2026-08-21; was 700)
    panMs: 3000, // the one committed fast move, 038 FR-013 (owner-judged live, 2026-08-21; was 1100)
    // Breathing room around the shot, per side, as a FRACTION of the frame
    // -- 0.195 is today's 2.6 tiles over the 13.33-tile desktop ceiling,
    // so desktop framing is unchanged while the phone margin finally
    // scales down (2.6 absolute tiles was 68% of its 7.6-tile frame).
    fitMarginFrac: 0.195,
    // How far an OVERFLOW shot's box centre may drift before the camera
    // moves at all (038 FR-007a). Its old job -- damping the aim-chase --
    // died with the chase; what survives is the judged distance at which
    // "the subject wandered" starts to be true. Measured against the live
    // world, 2026-08-17: at 0 the camera holds for 19% of ticks, at 1.5
    // for 78%.
    aimDeadzoneTiles: 1.5,
    hitRadiusFloorPx: 22, // a kitty stays tappable at ~23px on a phone at the ceiling
    // A backgrounded tab returns with a vast dt. Uncorrected that eases to
    // 1, which is the cut FR-008 forbids -- so the correction is clamped
    // rather than the easing being special-cased on return.
    maxFrameMs: 100,
  }),

  // Which directions a swimming cat may be drawn end-on (2026-08-11).
  // 'none' | 'toward' | 'both'. Both directions were drawn, dialled and
  // judged side by side in the lab at the live tile; owner took both
  // (2026-08-11). The away view earns its place on the raised tail, which
  // is the only silhouette it has -- it has no face by design.
  swimAxial: 'both',

  // Interpolation & element comings-and-goings (US3).
  elementFadeShare: 0.4, // share of a tick over which spawns/expiries fade
  // Critters (bug/greeble) glide between served states like kitties do
  // (007 refinement, 2026-07-20 -- the hover-bob alone left the hops
  // jerky). Anything farther than a skitter is a different moment: snap.
  critterGlideMaxTiles: 2,
  // Greebles alone go farther since spec 039's dart schedule: 1-3 tiles
  // along one heading on a moving tick, so THEIR skitter boundary is 3.
  // Bugs keep 2 -- a bug never legally moves three, so a wider bound
  // would turn bug respawns into visible scoots (2026-08-21; the owner
  // caught the 3-tile dart snapping).
  greebleGlideMaxTiles: 3,

  // Idle life (US4).
  idleMotionPeriodMs: 5200, // one idle slot about this long
  idleMotionWindowMs: 420, // an ear twitch (and v1's snap blink) lasts this
  breathePeriodMs: 3400, // the slow ambient cycle for resting poses
  // The grooming sine's full cycle -- three nods. On the tick beat (800ms)
  // the lick read dog-like; judged at half rate (owner, 2026-08-22).
  groomCycleMs: 1600,
  // Per-kitty drawn size, owner-curated (2026-08-22): Biscuit is a playful
  // KITTEN now, Pumpkin is snacky. Presentation only -- the logical
  // footprint stays one tile, the feet stay on the ground line
  // (render.js kittyBoxFor), and an id outside the map draws at 1.
  // Owner-pasted from the clowder card, 2026-08-22.
  kittySize: Object.freeze({
    1: 0.99, // Miso
    2: 0.92, // Biscuit
    3: 1.06, // Pumpkin
    4: 0.98, // Kittybear
    5: 1.01, // Clementine
  }),

  // What breaks up the rhythm (2026-08-06). The slots used to run a strict
  // blink -> flick -> twitch rotation, every cat on the same clock and
  // every motion starting exactly on the beat, which measured as a literal
  // metronome: all four cats blinking at 13800ms intervals, zero spread.
  // Each slot now draws a motion from these weights and starts it somewhere
  // inside the slot. All of it is hashed from (id, slot), never random, so
  // `motionFor` stays a pure function of (id, pose, now) -- still frames,
  // reduced motion and the harness all depend on that.
  // Owner-dialled 2026-08-06, and the intent matters more than the
  // numbers: a new viewer should think "did that cat just slow blink?",
  // watch for a while, and find the occasional blink or ear twitch --
  // common enough to be really there, rare enough to stay a treat. So the
  // long quiet stretches are the point, not a shortfall. Measured over 30
  // minutes, the gaps where all four cats are still run 1.79s +/- 1.47s
  // (median 1.54s, p99 6.3s); before any of this it was a flat 0.9s.
  // Anything that makes the meadow busier is trading that feeling away.
  idleBlinkWeight: 30,
  idleEarsWeight: 26,
  // Added 2026-08-10, on the owner's call that the measured rarity above
  // was about BEATS -- discrete things that punctuate -- and that
  // continuous motion is exempt and wanted. These two are still beats, so
  // they are priced as beats: together they take 20 of the 100 weight,
  // which lengthens the all-four-cats-still gaps by roughly a fifth
  // rather than filling them in. The continuous work (tail, head, gaze,
  // ears) is not scheduled here at all -- it never stops, and it never
  // punctuates, so it cannot spend this budget.
  idleScanWeight: 14, // a slow look at something, or nothing
  idleYawnWeight: 6, // rarest on purpose: a yawn you see often is a tic
  // A slot where nothing happens. It is what makes the others feel
  // unscheduled -- and it is a real nothing, not the vestigial tail flick
  // it replaces, which quietly restarted the breathing cycle at 8x speed
  // for a tail-tip sway of 0.4px at a live 33px cat.
  //
  // 35 -> 24 (2026-08-10): the key was declared TWICE when scan and yawn
  // landed, 24 above and the old 35 here, and the last one wins. The budget
  // came to 111, so scan and yawn were added ON TOP of the rarity budget
  // instead of priced into it -- the one thing the handoff said it had not
  // done. A test now asserts the five weights total 100.
  idleRestWeight: 24,
  // 0 = every motion on the beat (the old behaviour), 1 = anywhere in the
  // slot it still fits. The motion can never overrun its slot either way.
  // Half, owner-dialled: enough to break the metronome without letting a
  // motion drift so far into its slot that two land back to back.
  idleJitter: 0.5,
  // Per-cat tempo, +/- this share. Four cats on one clock read as one
  // animal drawn four times; a little spread reads as four animals.
  idleTempoSpread: 0.15,

  // v2 live motion -- every value owner-judged in the gallery-v2 motion
  // lab (2026-07-29; the settle was slowed 180→400ms on owner feedback).
  // Consumed only when the vocabulary dispatcher installs drawCatTween
  // (the v2 kitties); v1 keeps its pose snap and its snap blink.
  poseBlendMs: 260, // generic pose-space blend on any pose change
  // Wetness is a fact about the tile, not the pose (owner, 2026-08-04):
  // a cat drinking in a pond is still standing in water. It fades on the
  // same clock as a pose blend so a shoreline crossing does not pop.
  wetFadeMs: 260,
  /**
   * How long a coat stays visibly damp after leaving the water.
   *
   * Asymmetric with `wetFadeMs` on purpose: a cat is wet the instant it
   * is in water, and dries slowly. This is the ONLY water cue that
   * outlives the pond -- see `wetFor`, and the invariant recorded there.
   */
  furDryMs: 2800,
  /*
   * ONE water level, for every pose (owner, 2026-08-10).
   *
   * A per-pose surface was tried first -- 0.72 wading, 0.82 floating, on
   * the reasoning that a cat standing in shallow water and one floating in
   * deep water do not sit at the same height. That is true of real ponds
   * and wrong for this one: the meadow's water is one depth everywhere, so
   * two levels made the same pond look like two, and the level changed
   * under a cat that had only changed what it was DOING.
   *
   * So `waterline` above is now the whole story, and the poses may not
   * encode depth of their own -- see cat-v2's SWIM, which had to be raised
   * to sit at the same height as the land poses once it started being
   * clipped like them. The rule: the WORLD owns the water level, the POSE
   * owns what the cat is doing at it.
   */
  /**
   * Where the pond surface cuts a cat standing in it, in the cat's own
   * unit space (0 top, ground at 0.88) -- BACKLOG P1, the owner's idea.
   *
   * The cat is clipped below this line, so a cat on a water tile reads as
   * half-submerged whatever pose it is in. That is the point: `poseFor`
   * deliberately lets drinking and grooming outrank the wade, so those
   * cats keep a land pose while standing in a pond, and occlusion is what
   * makes them look like it -- one clip instead of a water variant of
   * every activity.
   *
   * Rides `wetFor`, the same eased 0..1 the shadow and ripple already
   * use, so the surface rises and falls with the shoreline crossing
   * rather than popping, and the three cues can never disagree.
   *
   * NOT applied to the swim pose: that one earns "underwater" from its
   * own low flat silhouette (see cat-v2's SWIM), and clipping it too
   * would submerge a cat that is already drawn sunk.
   *
   * 0.72 owner-picked 2026-08-07 from a sheet of six depths rendered
   * through this exact path. It cuts across the bottom of the body
   * rather than sitting under it, so the cat is clearly IN the pond
   * instead of on it, while the grooming or drinking pose stays legible.
   * The two depths either side were both rejected for real reasons:
   * 0.76 only hides the legs and is easy to miss, and 0.62 -- which
   * would have matched SWIM's own surface, so wading and swimming cats
   * shared one water level -- makes a standing cat look like it is
   * swimming. One water level lost to pose legibility, deliberately.
   */
  waterline: 0.72,
  /**
   * How close a chase's quarry has to be before the cat is drawn
   * mid-pounce, in tiles (Manhattan, like every decision distance).
   *
   * `Action::Chase` is lawful at any distance -- the engine's selection
   * scans the whole world -- so a cat crossing the map after a bug used
   * to be drawn mid-pounce the entire way, hiding the walk. Measured on
   * 2700 live kitty-ticks: gating at 4 moves pouncing 27.9% -> 25.3% and
   * walking 28.1% -> 30.5%, which is smaller than it sounds because half
   * of pouncing is PLAY (adjacent by lawfulness, so never gated) and the
   * median chase is only 2 tiles. 19% of chase runs reach past 4, about
   * one every 12 seconds somewhere on the map.
   *
   * A chase whose target cannot be resolved -- caught or expired this
   * tick -- keeps the pounce. The gate only ever takes it away when the
   * quarry is positively known to be far, which is also what keeps v1
   * callers, who pass no distance at all, drawing exactly as before.
   *
   * 4 -> 3 (owner, 2026-08-23), after the Biscuit 2.0 cutover made the
   * world read pounce-heavy. Re-measured on 350 live ticks off the served
   * world (1,745 cat-ticks): 3 moves drawn pouncing 24.0% -> 23.2% and
   * walking 22.4% -> 23.2%, demoting 13 chase ticks, every one of them to
   * walking. Deliberately NOT 2, though 2 is the bigger cut (21.8%): the
   * chase-distance histogram peaks at 1-2 tiles, so a gate sitting ON the
   * mode doubles mid-chase pose flips (0.33 -> 0.70 per scene) and leaves
   * roughly one lunge in six flying spec 039's arc while drawn in a
   * walking pose -- `leapFor` keys on the served two-tile step and never
   * consults this dial, so the gate can only ever disagree with a leap,
   * never suppress one. 3 buys most of the trim and neither cost.
   */
  pounceGateTiles: 3,
  /* The final pounce (spec 039): the served world may move a chasing cat
   * TWO tiles in one tick -- the lunge, the only two-tile step the world
   * ever serves. The map presents that served fact as its one leap: the
   * body lifts on `leapArc` while the ground shadow stays on the travel
   * line, and the landing hands to the settle. */
  pounceLeap: {
    // Peak lift as a fraction of a tile. Owner's paste from the
    // gallery-v2 leap card, 2026-08-21 ("looks surprisingly good"):
    // a quarter tile -- the arc reads at both the phone's ~50px and the
    // desktop's ~110px without turning the lunge into a bounce.
    liftFrac: 0.25,
  },
  /* The groomer's sub-tile lean toward the friend she is washing (spec
   * GROOM-OTHER-EDITS): the read is the nose crossing the friend's outline,
   * and position is the one cue that survives every zoom. Presentation
   * only -- logical position never moves, so camera, grouping and draw
   * order keep keying off real tiles. First-cut values, judged in the
   * gallery's groom-other card. */
  groomLean: {
    tiles: 0.22, // how far the sprite slides toward the friend, in tiles
    easeMs: 450, // the slide in -- and OUT: endings are abrupt (the friend
    // binds to nothing and may walk off any tick), and the eased return
    // IS the "sitting back up" read.
  },
  // ...and how far the hunter's FACE carries. Measured on the candidate
  // roster over 4,604 cat-ticks: the median quarry was 10 tiles off and the
  // most common 12, so an ungated face meant a cat wearing a hunting
  // expression for a bug across the meadow while drawing an ordinary walk
  // -- the pose and the expression disagreeing about whether a hunt was
  // happening, on 85.6% of the ticks the face was on. Wider than the pounce
  // on purpose (owner, 2026-08-14): the eyes may lead the pounce, they just
  // may not lead it across the whole map.
  //
  // 8 -> 6 (owner, 2026-08-16), after "hunter eyes with no bug in
  // proximity". 8 is manhattan, and on a 20x20 world that is most of the
  // way across it -- the quarry was on screen but nowhere the eye would
  // call near. 6 is still wider than the pounce gate (4, then 3 from
  // 2026-08-23), so the eyes keep the lead they were given.
  arriveBlendMs: 340, // the walking -> standing blend, paired with the settle
  // The landing settle. `settleMs` is the whole span; the SHAPE and the
  // amplitudes live in cat-v2's SETTLE, because since 2026-08-19 the settle
  // is a deformation of the CAT rather than a scale of the canvas -- see the
  // note there. Lengthened 400 -> 460 with the rebound: the recovery is now
  // most of the span and needs the room.
  settleMs: 460,
  // Peak squash for the V1 FALLBACK ONLY. v1's cat file has no `applySettle`,
  // so on that path the renderer still runs the old whole-canvas scale, which
  // is the right cheat at v1's tile sizes and the wrong one at camera sizes.
  settleDip: 0.05,
  blendTickShareCap: 0.45, // a blend never outlasts this share of a tick
  // The cat "I love you", re-dialled in the v2 lab (owner, 2026-08-06):
  // the lid eases down, holds, and releases. The hold carries the gesture
  // and was the value that moved -- 150ms was long enough to see but not
  // to mean anything, and at 550 the closed eye is held rather than
  // passed through. 1550ms total, well inside the 4600ms idle slot.
  slowBlinkDownMs: 550, // the lid eases down ...
  slowBlinkHoldMs: 550, // ... holds ...
  slowBlinkUpMs: 450, // ... and releases

  // Idle motion durations (2026-08-10). Both comfortably inside the
  // 4600ms slot, for the same reason the slow blink has to be: `at`
  // arrives modulo the period, so a motion longer than its own slot
  // would always be in progress.
  scanMs: 1500,
  // The yawn, as three spans rather than one duration (2026-08-10). Same
  // shape as the slow blink, and for exactly the same reason: the weight
  // of the gesture is in the HOLD. The first cut had none -- it opened
  // over 400ms straight into a 600ms close -- and a gape with no pause at
  // full stretch is a mouth opening and shutting, which reads as eating
  // rather than yawning (owner, 2026-08-10). 1420ms total, comfortably
  // inside even the fastest cat's 4420ms slot.
  yawnOpenMs: 340, // the jaw drops ...
  yawnHoldMs: 620, // ... and stays down, which is the yawn ...
  yawnCloseMs: 460, // ... then eases shut

  /* The meow (2026-08-25), extracted from an accident.
   *
   * A yawn cut short by a pose change reads as a vocalisation, and the owner
   * named it before it was measured: "it reads very meow". Measured, that is
   * what was on screen -- of the yawns Biscuit started, only 3.6% ever
   * reached their close phase and the median drew 485ms of 1420ms.
   *
   * DIALLED IN THE LAB AND BAKED 2026-08-25, on the owner's word. The
   * accident was the baseline it was tuned OFF -- deliberately, because an
   * earlier cut of this block shipped a tidier call (smaller jaw, open eyes,
   * no tongue) and moved three things away from the thing being liked before
   * any of them had been judged.
   *
   * What she kept: the whole FACE. `RIG.meowMouth`, `meowHeadTilt`,
   * `meowSquint` and `meowTongue` are all still the yawn's own values, so a
   * call and a yawn draw the same face and differ only in timing. Her read:
   * "even the full yawn comes off as more 'relaxed meow'".
   *
   * What she changed: the timing, to a budget she chose -- "the best looking
   * animation I could fit into 800ms". The hold nearly doubles the accident's
   * and the close is real where the accident had none, which is 800ms against
   * the accident's 485 and the yawn's 1420.
   *
   * `meowGape` still treats a ZERO close as a snap rather than dividing by
   * it. Nothing ships with one now, but the lab card's reference cat replays
   * the accident with exactly that, and a test keeps it honest.
   */
  meowOpenMs: 340, // the yawn's own opening, which she kept ...
  meowHoldMs: 260, // ... a longer dwell than the accident's 145 ...
  meowCloseMs: 200, // ... and a real close, where the accident had none

  /* How much of the yawn's eye-squeeze a call borrows, BY POSE.
   *
   * Sparse, like FAR_LEGS: a pose named here overrides `RIG.meowSquint`, and
   * everything unnamed takes the dial. Same reason that map is sparse -- most
   * of the vocabulary wants the default and saying so five times invites the
   * five to drift apart.
   *
   * `pouncing: 0` is the owner's call, 2026-08-25: "it works on pounce with
   * meowsquint=0". The pose does not distinguish itself -- `pouncing` sets
   * eyes 'open' exactly as `walking` and `idle` do -- so this is a judgement
   * about the MOMENT rather than something derivable from the drawing. A cat
   * mid-lunge is watching its target; shutting its eyes to call reads wrong
   * in a way the same squeeze on a stroll does not.
   *
   * Which is why this is a map and not a second global: the call's character
   * follows what the cat is doing, and the thing that fires it knows that.
   */
  meowSquintByPose: { pouncing: 0 },

  /* Which poses a served meow is DRAWN on, and how often at most.
   *
   * The animation is tied to the engine's own meow channel -- it never
   * invents one -- but the RATE is ours, and it has to be, because policy
   * verbosity is not something the client controls. The Fog generation is
   * expected to be markedly chattier than today's roster (owner, 2026-08-25),
   * and without a ceiling the same wiring that reads as charm now would read
   * as a tic then. Same reasoning that demoted the purr to a glyph: "a bubble
   * for both meant 98% of bubbles said nothing".
   *
   * The poses are the owner's, judged in the lab: the call reads on a walk,
   * on idle, on a pounce (the last only with its eyes open, which is what
   * `meowSquintByPose` is for), and on a loaf. Everything else is skipped
   * rather than queued -- a meow drawn late is a cat mouthing at nothing.
   *
   * `loaf` is the odd one and was added 2026-08-26 ahead of its own need. It
   * is the only gated pose whose eyes are ALREADY closed, so `meowSquint` is
   * inert there -- the lid only ever goes further shut -- and the owner
   * judged it that way and ruled "keep eyes closed". So a loafing cat mumbles
   * with its eyes shut, deliberately, and a squint that could OPEN an eye
   * would be a different animal from the one she approved.
   *
   * It also drew ZERO speech in the 2026-08-25 census, and that is a true
   * zero rather than a thin sample: `rest` is not currently chosen by any
   * seat. The owner is repricing the cuddle economy, which will change that,
   * so this is in the gate BEFORE the behaviour that needs it. Re-census
   * after that lands -- the cooldown caps the ceiling, but the floor moves
   * with whatever the policies choose.
   *
   * Measured on the live world 2026-08-25: 30 speech events in 9 minutes, of
   * which 17 land on these three poses -- about 110 an hour across five cats
   * before the cooldown binds. A chattier generation raises the numerator and
   * `meowCooldownMs` holds the ceiling.
   */
  meowPoses: ['walking', 'idle', 'pouncing', 'loaf'],
  meowCooldownMs: 20000, // at most one drawn call per cat per this

  // The on-the-spot turn (2026-08-10). Short: this is a cat pivoting on
  // its front feet, not a considered about-face, and anything longer
  // reads as the cat sliding through a wall.
  turnMs: 200,

  // Anticipation and overshoot on pose blends (2026-08-10). Dialled well
  // down from the usual 1.70158 -- see easeBack.
  blendBack: 0.5,

  // The waking stretch, in TICKS rather than milliseconds (2026-08-10).
  // tick_ms is served, and a stretch pinned to the wall clock would span
  // a different number of served DECISIONS on a faster or slower world --
  // so the one thing that must not drift, how many instructions can land
  // while the cat is mid-stretch, would be exactly the thing that did.
  // Two ticks is long enough to read as luxurious and short enough that
  // the engine's next instruction lands after it, not through it.
  stretchTicks: 2,

  // How often an idle cat sits down instead of standing. `sitChance` is
  // drawn once per `sitPeriodMs`, so a cat that stays put long enough
  // will sit, get up, and sit again -- all of it hashed from (id, slot),
  // so it stays a pure function of time and the pose blend gives the
  // sitting-down and standing-up for free.
  //
  // `sitAfterTicks` is what makes it look considered. The hash decides
  // WHETHER a stretch of time is a sitting one; this decides whether the
  // cat has been still long enough to mean it. Without it, a one-tick
  // pause mid-walk lands a whole sit-down and stand-up inside 800ms,
  // which reads as a stumble rather than as a decision.
  sitPeriodMs: 26000,
  sitChance: 0.38,
  sitAfterTicks: 3,

  /* The card portrait's POSE BEATS (2026-08-10). PORTRAITS ONLY -- the
   * meadow must never draw these.
   *
   * A pounce in the world is a served fact: the engine says a cat is
   * chasing and the renderer draws it. Inventing one on the map would be
   * the client asserting something the world did not say, which Article V
   * forbids. The portrait is different, and already documented as
   * different: it is deliberately NOT the cat's real pose (owner,
   * 2026-08-07) but the cat AT REST, which is what lets it carry idle
   * motion at all. A cat play-pouncing or sitting down at rest claims
   * nothing about the world.
   *
   * Why they live off the served tick: on the map a pounce has one 800ms
   * tick to happen in, which is why its load is 240ms and the wiggle
   * quantises to a single rock. A portrait runs on the frame clock, so the
   * whole beat is legible here and nowhere else.
   *
   * Why they are NOT gated on stillness the way the map's `sit` is:
   * measured on the live world, a cat never has nothing to do for more
   * than 2 consecutive ticks (107 runs of one, 3 of two, none of three) --
   * so `sitAfterTicks: 3` is unsatisfiable and the map's sit can never
   * fire. That gate is right for the map, where a busy cat should not sit
   * down. It is wrong for a portrait, which is at rest BY DEFINITION.
   *
   * One weighted draw per period, so a sit and a pounce can never collide,
   * and the weights are a share of 100 the way the motion table's are. */
  cardBeatPeriodMs: 7000,
  /* ONE table, one beat at a time (2026-08-10, owner's call). The portrait
   * used to run two schedulers side by side -- the motion slots and a pose
   * clock -- which meant a cat could yawn mid-pounce, and 16 different
   * pose x motion pairs existed that nobody had chosen. Sequencing them
   * instead is the same move the sit chain made: one thing at a time, and
   * the next thing after it.
   *
   * The slot has to fit the LONGEST beat, which is the 5.8s sit chain; at
   * 7000ms everything else has slack. Weights are a share of 100, like the
   * map's motion table -- new beats are priced IN, never added on top,
   * which is the mistake the handoff made with scan and yawn.
   *
   * These are the PORTRAIT's. The map keeps `motionFor` and its own slots:
   * a map cat is idle only 24% of the time and in isolated single ticks, so
   * it needs short beats that fit in a tick, not a 5.8s chain. */
  cardBlinkWeight: 30,
  cardEarsWeight: 14,
  // 0 (2026-08-10): the gaze is TABLED for a longer session, so the card
  // does not scan for now. Kept as a weight rather than deleted -- turning
  // it back on is one number, and the branch stays exercised. See BACKLOG:
  // the look is one coupled gesture (gaze drives pupils, head and ears) but
  // only the ears clear the visibility floor at portrait size, so it wants
  // dialling as a whole rather than switching on as-is.
  cardScanWeight: 0,
  cardYawnWeight: 5,
  cardSitWeight: 12,
  cardPounceWeight: 7,
  cardRestWeight: 32, // 20 + the scan's 12, so no other beat's rate moved
  // The sit holds, then the cat gets up THROUGH a stretch -- which is what
  // a cat actually does standing up, and the reason `stretch` is authored
  // to leave and return to neutral (it is 0px off a resting cat at both
  // ends). The chain is sitHoldMs + one stretch.
  sitHoldMs: 4200,
  // The pounce beat, and the two dials it needs that the map's cannot
  // share: at 2x the map's beat the same rock rate is a wallow, and the
  // same tread depth that reads at 47px is 0.62px at 31.
  playBeatMs: 1600,
  playWiggleHz: 3.9,
  playSway: 0.06,

  // Beats (US5).
  // The observed drop is relief minus that tick's need rise, so the
  // threshold must sit below the smallest sparkle-worthy relief: cuddle at
  // 15/tick lands as ~14.6. Kept above solo play (~9.6) and sleep (~7.7),
  // which stay sparkle-free.
  reliefSparkleDrop: 12, // need-points a drop must exceed to sparkle
  sadBeatMs: 1600,
  sparkleMs: 1000,

  // Ambient life & juice (US6) -- each effect individually disableable.
  ambient: Object.freeze({
    waterShimmer: true,
    // The rings a wading cat pushes out. OFF since 2026-08-09: the pond
    // restyle gives the water its own surface motion, and two ring sets --
    // the cat's and the water's -- read as a mistake rather than as depth.
    // The cue it replaced is not lost: `wet` also fades the ground shadow,
    // and the waterline clip already reads as submersion. Its own comment
    // always called it a first pass pending exactly this work.
    wetRipple: false,
    // The damp coat: darker, flatter fur that outlives the pond. Tried
    // 2026-08-10 and OFF by the owner's call the same day -- the
    // coloration was not wanted. Kept behind the flag rather than deleted,
    // beside its sibling water effect, so the lab can put it back.
    //
    // Nothing about the water FIX depends on this. Submersion is spatial
    // and drives every piece of geometry; this was only ever the optional
    // colour half, and with it off leaving the water simply has no
    // lingering cue -- which is what shipped before.
    wetCoat: false,
    sunbeamPulse: true,
    dustMotes: true,
    cloudShadows: true,
  }),
  ambientPeriodMs: 5200,
  cloudPeriodMs: 60000,
  bubblePopShare: 0.35, // share of a tick a speech bubble spends popping in

  // Props (spec 007, FR-012): timing periods plus the drawing-side values
  // props.js's PROP_DEFAULTS carries when this layer is absent (the
  // standalone gallery). This is the full set propTunables() serves, so it
  // must stay a superset of PROP_DEFAULTS.
  props: Object.freeze({
    flapPeriodMs: 900, // one leisurely wingbeat cycle
    panicMultiplier: 2.2, // flap-rate multiplier while hunted
    bobPeriodMs: 2600, // the hover's slow breathe
    bobAmplitude: 0.035,
    hoverLift: 0.06,
    wispBobMs: 3800, // the greeble wisp drifts slowest of all
    wispBobAmplitude: 0.02,
    heartPulseMs: 1400,
    heartPulseScale: 0.08,
    zDriftMs: 2800,
    zRise: 0.08,
  }),

  // The meadow (spec 008, FR-010): per-layer availability flags plus every
  // ground number, named. meadow.js's MEADOW_DEFAULTS carries the
  // drawing-side values when this layer is absent (the headless harness);
  // this is the authoritative set, so it must stay a superset of
  // MEADOW_DEFAULTS.
  meadow: Object.freeze({
    ponds: true, // merged smooth-shored water (off: per-tile pools)
    glow: true, // sunbeams as radial light (off: plain warm tile)
    // Worn paths are UNAVAILABLE for now (owner, 2026-08-21): visitors
    // never saw them (showPaths defaults false, 008 FR-009) and the p-key
    // debug overlay goes inert with this. The BACKLOG carries the
    // successor: real heatmaps, low priority. One boolean turns the 008
    // machinery back on.
    paths: false,
    gridOverlay: true, // whether the grid debug overlay is available at all
    toneSteps: 32, // steps in the ramp blended through the grass tones
    toneCells: 3, // tiles per noise cell: how broad a grass blotch is
    jitterCells: 1.7, // and the finer lattice the brightness grain rides
    toneCells2: 7.5, // a second, broader tone field over the first
    groundBlurTiles: 0.32, // softens the tone mosaic; detail draws on top
    groundWashSun: 0.3, // the field-wide light wash, keyed to shadowLean
    groundWashShade: 0.16,
    jitterAlpha: 0.05, // peak alpha of the per-tile brightness jitter
    patchChance: 0.118, // share of tiles carrying a worn-earth or moss patch
    patchEarthAlpha: 0.03,
    patchMossAlpha: 0.05,
    // Cover grows in DRIFTS (spec 03). Mirrors MEADOW_DEFAULTS -- the
    // superset assertion in test-meadow.mjs fails on drift.
    fertilityCells: 4.5, // tiles per fertility blotch; larger = broader passages
    bladeFertPower: 2,
    bloomFertPower: 3,
    bushFertPower: 4,
    bladeChance: 0.55, // tiles with a tuft of grass
    bladeAlpha: 0.38,
    bloomChance: 0.05, // tiles with a flower
    bloomShade: 0.28, // how far the lower petals lean toward the heart
    bushChance: 0.0175, // tiles with a clump of tufted ground cover
    bushJitterX: 0.15, // how far off the grid a clump may stand, sideways, in tiles
    bushSizeMin: 0.2, // the smallest a clump may be, in tiles
    bushSizeSpread: 0.3, // ...and how much the shape seed adds on top
    bushSizeMinDiff: 0.07, // two of a kind in one row must differ by this much
    bushAlpha: 0.9, // and how strongly it reads against the grass
    // 'cover' | 'tuft' | 'bramble' (flat) | 'shrub' | 'grown' | 'trunk' |
    // 'tall' (standing). Judged in gallery-meadow.html.
    bushStyle: 'lobed',
    bushStyleAlt: 'trunk', // the second species, when a meadow grows two
    bushStyleAltShare: 0.3, // 0 = primary only, 1 = alt only, between = a mix
    bushTrunk: 0, // how much stem the stemmed styles draw; 0 is none
    bushTrunkAlt: 1, // the same, for the bushStyleAlt species
    bushTrunkWidth: 2.55, // stem thickness, as a multiple of each style's own
    bushTrunkWidthAlt: 1.4, // the same, for the bushStyleAlt species
    // How far the lobed shrub's four leaf ticks slide toward the sun, in
    // canopy radii per unit of shadowLean. 0 pins them to the crown and
    // lets the gradient carry the light on its own.
    bushLeafSwing: 0.1,
    // The shrub's shadow, damped against the cats': a squat canopy sits
    // close to the ground, so it stretches far less and needs no alpha
    // falloff. Only the LENGTH is damped -- the lean also anchors the
    // sun-side edge to the caster, and damping that recentres it.
    bushShadowLean: 1, // gain on the anchor: 1 keeps the sun-side edge on the shrub
    bushShadowLength: 0.3, // and of its stretch past the caster
    bushShadowAlpha: 1, // no thinning: contact, not a smear
    bushLift: 0, // how far a shrub's canopy stands above its base, in radii
    bushLiftAlt: 1.55, // the same, for the bushStyleAlt species
    bushBase: 0.72, // where it meets the ground, in tiles from the tile's top
    // How far the canopy's height pushes its shadow along the lean. Kept
    // small: a rooted thing's shadow leaves its base, and pushing it far
    // is precisely what makes a bush look airborne.
    bushShadowThrow: 0.25,
    // The shoreline. Corners are rounded into arcs first and the wobble
    // rides on the finished curve (meadow.js buildPondPath); before, the
    // wobble subdivided the edges and capped the radius at 0.25 tile
    // whatever this said.
    shoreRounding: 0.35, // pond corner rounding, in tiles
    // 0 since the pond restyle -- see MEADOW_DEFAULTS for why.
    shoreWobble: 0,
    shoreWobblePeriod: 0.35, // and its wavelength around the perimeter, in tiles
    // Scales the OUTWARD bulges only: bays cut the full `shoreWobble`,
    // headlands reach this share of it. See meadow.js `wobbleAlong`.
    shoreBulgeEase: 0.75,
    shoreOverdraw: 0.1, // push the whole outline out this far, in tiles
    lilyPadMinTiles: 4, // ponds at least this big carry a lily pad
    // Pond depth (design handoff spec 02). Reasoning lives beside the
    // originals in meadow.js's MEADOW_DEFAULTS; these must match it.
    pondDepthBlurTiles: 0.95,
    pondDepthBlurClamp: 1.8,
    pondLipBlurTiles: 0.42,
    pondLipAlpha: 0.8,
    meniscusWidthTiles: 0.058,
    causticLinesPerTile: 1.6,
    causticLinesMax: 4,
    causticAlpha: 0.055,
    causticAmplitude: 0.025,
    glowRadiusTiles: 1.4, // sunbeam glow radius, in tiles
    glowAlpha: 0.6, // overall glow strength
    pathHeatCap: 12, // worn-path heat ceiling per tile (memory, not display)
    pathFullHeat: 3, // passes at which a trail draws at full tint
    pathHalfLifeMs: 60000, // trail fading half-life
    pathVisibilityFloor: 0.4, // decayed heat below this draws nothing
    pathTintAlpha: 0.5, // trail opacity at full heat
  }),
});

/** Worn-path heat after read-time decay (spec 008 research R6): a pure
 * half-life curve, so fading needs no timers and no per-frame writes. */
function decayedPathHeat(entry, now) {
  return (
    entry.heat * 0.5 ** ((now - entry.stampedAt) / VIEW.meadow.pathHalfLifeMs)
  );
}

function easeInOutCubic(t) {
  return t < 0.5 ? 4 * t * t * t : 1 - (-2 * t + 2) ** 3 / 2;
}

/** The motion lab's smoothstep: gentle at both ends. Pose blends, the
 * slow-blink lid, and the landing settle all ease through this. */
function easeSmooth(t) {
  return t * t * (3 - 2 * t);
}

/**
 * Named channels for the idle hash. Same discipline as the meadow's
 * MEADOW_SALTS: each scatter gets its own channel, because two draws off
 * one channel correlate and the correlation is what reads as a pattern.
 */
const IDLE_SALTS = Object.freeze({
  tempo: 1, // each cat's own clock speed
  pick: 2, // which motion a slot gets
  offset: 3, // where in the slot it starts
  side: 4, // and which ear a twitch belongs to
  look: 5, // where a scan looks
  sit: 6, // whether an idle cat is sitting this stretch of time
  play: 7, // and whether a card portrait play-pounces in one
});

/**
 * Deterministic 0..1 from two small integers and a salt. Hashed rather than
 * random so `motionFor` stays pure: a still frame, a reduced-motion frame
 * and a test all have to be able to ask what a cat is doing at time T and
 * get the same answer, and an RNG would buy the same look and cost that.
 *
 * meadow.js has `tileHash` doing the same job for ground scatter, and one
 * hash would be better than two -- but anim.js currently depends on
 * nothing, the motion harness evals it on its own, and motion reaching into
 * ground art for a hash is the wrong direction for that dependency to run.
 * Four lines is the cheaper price. If a third caller turns up, lift both
 * into one file rather than adding a third.
 */
function idleHash(a, b, salt = 0) {
  let h = (a | 0) * 374761393 + (b | 0) * 668265263 + (salt | 0) * 2246822519;
  h = (h ^ (h >>> 13)) * 1274126177;
  return ((h ^ (h >>> 16)) >>> 0) / 4294967296;
}

/** This cat's own idle tempo. Constant per cat, so the slot maths stays
 * modular arithmetic on a fixed period rather than accumulated time. */
function idlePeriodFor(id, dials = VIEW) {
  const spread = (idleHash(id, 0, IDLE_SALTS.tempo) * 2 - 1) * dials.idleTempoSpread;
  return dials.idleMotionPeriodMs * (1 + spread);
}

/** Which motion this slot gets, drawn from the weights. A table rather
 * than a chain of ifs since 2026-08-10: adding a fourth motion to the
 * chain meant restating the running total in three places, which is the
 * shape of bug that silently reweights everything downstream of it. */
function idlePickFor(id, slot, dials = VIEW) {
  const table = [
    ['blink', dials.idleBlinkWeight],
    ['ears', dials.idleEarsWeight],
    ['scan', dials.idleScanWeight],
    ['yawn', dials.idleYawnWeight],
    ['rest', dials.idleRestWeight],
  ].map(([kind, w]) => [kind, Math.max(0, w || 0)]);
  const total = table.reduce((sum, [, w]) => sum + w, 0);
  if (total <= 0) return 'rest';
  let draw = idleHash(id, slot, IDLE_SALTS.pick) * total;
  for (const [kind, w] of table) {
    if (draw < w) return kind;
    draw -= w;
  }
  return 'rest';
}

/**
 * How far into the slot the motion starts. Bounded by the slack the slot
 * has left after the motion's own length, so jitter can move a motion
 * around inside its slot but can never let one overrun into the next.
 */
function idleOffsetFor(id, slot, period, durationMs, dials = VIEW) {
  const slack = Math.max(0, period - durationMs);
  return idleHash(id, slot, IDLE_SALTS.offset) * slack * dials.idleJitter;
}

/**
 * The slow-blink lid at `at` ms into a blink, or undefined once the blink
 * is over. Down, hold, release -- the "I love you" envelope. The three
 * spans are dialled independently and the weight sits in the hold: the
 * gesture is the held closed eye, not the travel to it.
 *
 * Pulled out of `motionFor` so the v2 lab can drive its Slow blink card
 * through the shipping envelope instead of restating the shape and the
 * numbers, which it used to do -- a second home for values that are meant
 * to be judged in the lab and pasted back is the one place drift is
 * guaranteed to start. `dials` exists for that lab: VIEW is frozen, so the
 * sliders need a bag of their own to write to, and passing it here keeps
 * the shape shared even while the values differ.
 *
 * The three spans must stay comfortably under `idleMotionPeriodMs`: `at`
 * arrives modulo that period, so a blink longer than its own slot would
 * always be in progress and the eyes would never settle open.
 */
function slowBlinkLid(at, dials = VIEW) {
  const down = dials.slowBlinkDownMs;
  const hold = dials.slowBlinkHoldMs;
  const up = dials.slowBlinkUpMs;
  if (at < 0 || at >= down + hold + up) return undefined;
  if (at < down) return easeSmooth(at / down);
  if (at < down + hold) return 1;
  return 1 - easeSmooth((at - down - hold) / up);
}

/**
 * A blend that leans back before it goes and drifts past before it
 * settles: the standard in-out "back" ease, with its constant dialled a
 * long way down from the usual 1.70158.
 *
 * This is only legal because pose space is LINEAR. A t of -0.03 is a real
 * pose three percent beyond the one the cat is leaving, and 1.04 is three
 * percent past the one it is arriving at -- so anticipation and overshoot
 * cost no new poses and no new geometry, only a different curve through
 * the blend that already existed. The vocabulary's poses are already
 * extremes, which is exactly why the constant has to be small: at
 * 1.70158 a pounce crouch overshoots into a cat folded in half.
 */
function easeBack(t, s = VIEW.blendBack) {
  const c = s * 1.525;
  return t < 0.5
    ? ((2 * t) ** 2 * ((c + 1) * 2 * t - c)) / 2
    : ((2 * t - 2) ** 2 * ((c + 1) * (2 * t - 2) + c) + 2) / 2;
}

/**
 * The yawn gape at `at` ms into a yawn, or undefined once it is over.
 *
 * Open, hold, close -- factored out beside `slowBlinkLid` because it is
 * the same envelope doing the same job, and because a second home for
 * values meant to be judged in the lab and pasted back is the one place
 * drift is guaranteed to start.
 *
 * As with the blink, the three spans must stay comfortably under
 * `idleMotionPeriodMs`: `at` arrives modulo the period, so a yawn longer
 * than its own slot would always be in progress.
 */
function yawnGape(at, dials = VIEW) {
  const open = dials.yawnOpenMs;
  const hold = dials.yawnHoldMs;
  const close = dials.yawnCloseMs;
  if (at < 0 || at >= open + hold + close) return undefined;
  if (at < open) return easeSmooth(at / open);
  if (at < open + hold) return 1;
  return 1 - easeSmooth((at - open - hold) / close);
}

/** The meow gape at `at` ms into a call, or undefined once it is over.
 *
 * Same three-span shape as `yawnGape` and deliberately so: they share the jaw
 * in `drawFace`, and giving them different curve families would make the two
 * hard to compare in the lab, which is where the difference is being judged.
 * What differs is the timing and, in the drawing, the amplitude, the eyes and
 * the tongue. */
function meowGape(at, dials = VIEW) {
  const open = dials.meowOpenMs;
  const hold = dials.meowHoldMs;
  const close = dials.meowCloseMs;
  if (at < 0 || at >= open + hold + close) return undefined;
  if (at < open) return easeSmooth(at / open);
  // A zero close is the accident's snap, not a division. The gape simply
  // ends: `at` has already passed the total above, so falling through here
  // with close 0 would divide by it.
  if (at < open + hold) return 1;
  if (close <= 0) return undefined;
  return 1 - easeSmooth((at - open - hold) / close);
}

/** Where a wetness fade has got to. Resumed from `from` rather than from
 * the far end, so a cat darting in and out of the shallows never snaps. */
function wetValue(w, now) {
  const target = w.on ? 1 : 0;
  // Wet fast, dry slow.
  const ms = w.on ? VIEW.wetFadeMs : VIEW.furDryMs;
  return w.from + (target - w.from) * easeSmooth(Math.min(1, (now - w.at) / ms));
}

/** A little overshoot-and-settle, for things that pop in (US6 juice). */
function easeOutBack(t) {
  const c1 = 1.70158;
  const c3 = c1 + 1;
  return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2;
}

/**
 * A step taken from a standstill: starts at rest and arrives at full
 * walking speed, so it hands over to a linear stride with no velocity
 * jump. f(0)=0, f(1)=1, f'(0)=0, f'(1)=1 -- the unique cubic that does
 * both, which is what makes the join invisible.
 */
function startEase(t) {
  return t * t * (2 - t);
}

/**
 * The final pounce's flight path (spec 039): a ballistic parabola over
 * the tick -- zero at both feet, peak 1 at mid-flight. The map's one
 * piece of vertical language, shared verbatim with gallery-v2's leap
 * card so the arc the owner judges IS the arc that ships.
 */
function leapArc(p) {
  return 4 * p * (1 - p);
}

/**
 * The delay line: served states in, paced states out.
 *
 * States arrive on a socket; frames draw at 60Hz. The renderer eases a cat
 * from its previous served position to its current one and has to decide
 * how long that takes. Playing it over the served `tick_ms` assumes the
 * next state lands exactly one tick later, and it never quite does --
 * network, GC and a stuttered frame each move an arrival by tens of ms.
 * Land late and the cat reaches the tile and SITS THERE until the next
 * state comes: the boundary hiccup the owner reported (2026-08-11). Land
 * early -- two states drained in one frame -- and the first is superseded
 * before it is ever drawn, so a cat crosses a whole tile in no time at all.
 *
 * So states are not played as they arrive. A small buffer is held and
 * played out at a paced rate. The buffer IS the jitter budget: one spare
 * state in hand means an arrival may be a whole tick late with nothing
 * visible on screen. The pace is then trimmed to keep that budget from
 * draining away or growing without bound, out of two measurements:
 *
 *   - the smoothed interval between PROMOTIONS, which in the long run
 *     cannot be anything but the rate states are actually produced at
 *     (you cannot play more states than you receive) -- so this tracks a
 *     server whose real tick differs from its configured one, and it is
 *     trustworthy in a way that measuring arrivals is not, because
 *     promotions are paced and arrivals are bursty;
 *   - the buffer depth, as a small additive trim: run a touch slow while
 *     the buffer is shallow, a touch fast while it is deep.
 *
 * The cost is latency -- the meadow runs about `paceTargetDepth` ticks
 * behind live. At an 800ms tick nobody can see it, and it is the whole
 * reason the hiccup goes away.
 *
 * Pure and clock-injected: `due` is handed the frame's `now`, so the
 * harness drives it with an arrival series and no rAF at all.
 */
class Pacer {
  constructor(dials = VIEW) {
    this.dials = dials;
    this.queue = []; // arrivals not yet promoted, oldest first
    this.tickMs = dials.tickMsFallback;
    this.intervalMs = this.tickMs; // measured production rate
    this.playMs = this.tickMs; // what the CURRENT segment plays over
    this.depth = dials.paceTargetDepth;
    this.lastPromoteAt = null;
  }

  enqueue(world) {
    this.queue.push(world);
  }

  /** The served tick changed (config landed, or a differently-paced box). */
  setTickMs(ms) {
    this.tickMs = ms;
    this.intervalMs = ms;
    this.playMs = ms;
  }

  /**
   * Everything queued, at once, for the paths that do no interpolation
   * (reduced motion) or have nothing to interpolate from (the first state).
   */
  drain() {
    const out = this.queue;
    this.queue = [];
    this.lastPromoteAt = null; // an unpaced promotion teaches the clock nothing
    this.playMs = this.tickMs; // ...and has no pace of its own to play at
    return out;
  }

  /**
   * What to promote on this frame: `{ worlds, snap }`, normally zero or
   * one world. `snap` means the caller must break continuity BEFORE
   * promoting -- a collapsed backlog is a different moment of the world,
   * not a long step.
   */
  due(now) {
    if (!this.queue.length) return { worlds: [], snap: false };
    // A tab left for hours is not a stutter. Collapse to the newest state
    // and show it at once; easing across two hours would be a lie whatever
    // pace it ran at.
    if (this.queue.length > this.dials.paceMaxBacklog) {
      const newest = this.queue[this.queue.length - 1];
      this.queue = [];
      this.lastPromoteAt = now;
      this.depth = this.dials.paceTargetDepth;
      this.intervalMs = this.tickMs;
      this.playMs = this.tickMs;
      return { worlds: [newest], snap: true };
    }
    if (this.lastPromoteAt !== null && now - this.lastPromoteAt < this.playMs) {
      return { worlds: [], snap: false };
    }
    const world = this.queue.shift();
    if (this.lastPromoteAt !== null) {
      // Clamped BEFORE it is smoothed: a resumed tab or a paused server
      // must not teach the clock a rate the world never ran at.
      const gap = clampRate(now - this.lastPromoteAt, this.tickMs, this.dials);
      this.intervalMs += (gap - this.intervalMs) * this.dials.paceIntervalSmoothing;
    }
    this.lastPromoteAt = now;
    // Depth is read AFTER the promotion -- what is still in hand, which is
    // what the next segment actually has to spend.
    this.depth += (this.queue.length - this.depth) * this.dials.paceDepthSmoothing;
    const trim = this.dials.paceTrimMs * (this.depth - this.dials.paceTargetDepth);
    this.playMs = clampRate(this.intervalMs - trim, this.tickMs, this.dials);
    return { worlds: [world], snap: false };
  }
}

/** Keep a duration inside the sane band around the served tick. */
function clampRate(ms, tickMs, dials = VIEW) {
  return Math.max(tickMs * dials.paceRateMin, Math.min(tickMs * dials.paceRateMax, ms));
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
    // What the CURRENT pair plays over, which is the pacer's business and
    // not the served tick's -- see `Pacer`. Frozen for the whole segment
    // on purpose: `progress` divides by it every frame, so a denominator
    // that moved under a running tick would make a cat step BACKWARDS.
    this.currPlayMs = VIEW.tickMsFallback;
    this.distressPatienceTicks = VIEW.distressPatienceFallback;
    this.facings = new Map(); // id -> 'left' | 'right'
    this.movedNow = new Map(); // id -> bool, for this pair
    // Tiles of ground each kitty has covered, completed ticks only. The
    // walk rides this instead of the clock -- see strideFor.
    this.odometer = new Map(); // id -> tiles
    this.movedBefore = new Map(); // id -> bool, for the PREVIOUS pair
    this.sleepingSince = new Map(); // id -> tick its current sleep began
    this.oneShots = new Map(); // id -> { kind, t0, duration }, one slot each
    this.newElementIds = new Set();
    this.expiredElements = [];
    this.pathHeat = new Map(); // "x,y" -> { heat, stampedAt } (spec 008 US5)
    // v2 pose-blend memory (motion wiring): what each kitty last wore on
    // screen, and its in-flight blend if a change just happened.
    this.lastPose = new Map(); // id -> { pose, phase, at } as last drawn
    this.poseTween = new Map(); // id -> { from, fromPhase, at }
    // Wetness, kept apart from the pose on purpose: the drawn tile says
    // whether a cat is in water, whatever it happens to be doing there.
    this.wetness = new Map(); // id -> { on, at, from }
    // The rig (2026-08-10): per-cat spring state for the tail, head, gaze
    // and ears, plus the clock each was last advanced on.
    //
    // This is the one genuinely stateful thing in the layer, and it is
    // safe for the same reason the pose blend is: it is dropped on every
    // discontinuity, and `rigFor` also rebuilds any state it has not
    // touched for a tick. So a viewer joining the feed mid-flight starts
    // every cat's rig AT REST rather than inheriting momentum from a
    // moment it never saw -- and a cat drawn out of a hidden tab does the
    // same, rather than springing violently to catch up.
    this.rigStates = new Map(); // id -> createRigState()
    this.rigAt = new Map(); // id -> the now it was last stepped at
    this.turns = new Map(); // id -> when this cat began turning around
    // Cats being drawn side-on until they next take a step. Only two poses
    // have an axial drawing, so wearing any other one turns a north/south
    // cat side-on -- and going back would whip it 90 degrees for a reason
    // the served world never gave. See `axialFor`.
    this.axialLocks = new Set(); // ids
    this.wokeAt = new Map(); // id -> when it last stopped sleeping
    this.stillSince = new Map(); // id -> tick it last had nothing to do
  }

  /** Reconnects and hidden-tab returns break continuity by definition. */
  bumpGeneration() {
    this.generation += 1;
  }

  pushState(world, now, playMs) {
    const prev = this.curr;
    // Bank the distance the OUTGOING pair covered, so the odometer holds
    // whole ticks and strideFor adds the eased part of the current one.
    if (prev && this.prev) {
      for (const k of prev.kitties) {
        const was = this.prev.kitties.find((p) => p.id === k.id);
        if (!was) continue;
        this.odometer.set(
          k.id,
          (this.odometer.get(k.id) ?? 0) + Math.hypot(k.pos.x - was.pos.x, k.pos.y - was.pos.y),
        );
      }
    }
    this.movedBefore = new Map(this.movedNow);
    this.prev = prev;
    this.curr = world;
    this.currArrivedAt = now;
    this.currPlayMs = Number.isFinite(playMs) && playMs >= 1 ? playMs : this.tickMs;

    const rosterChanged =
      prev &&
      prev.kitties.map((k) => k.id).join(',') !==
        world.kitties.map((k) => k.id).join(',');
    // Kitties step at most one tile per tick -- with ONE exception since
    // spec 039: a chasing kitty's final pounce lunges a second step in
    // the same tick, so a chase delta of Manhattan two is MOTION (the
    // leap). Anything larger, or two tiles outside a chase, is still not
    // motion -- it is a different moment of the world. Without this
    // carve-out the lunge tripped the teleport guard and the pounce
    // SNAPPED instead of leaping (found by the leap's own unit fixture).
    const teleported =
      prev &&
      !rosterChanged &&
      world.kitties.some((k) => {
        const was = prev.kitties.find((p) => p.id === k.id);
        const dx = Math.abs(k.pos.x - was.pos.x);
        const dy = Math.abs(k.pos.y - was.pos.y);
        if (k.last_action?.action === 'chase' && dx + dy === 2) return false;
        return dx > 1 || dy > 1;
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
      this.movedBefore.clear();
      this.odometer.clear();
      this.sleepingSince.clear();
      this.oneShots.clear();
      this.newElementIds = new Set();
      this.expiredElements = [];
      // Worn paths are the session's own memory (spec 008 FR-009): a
      // different moment of the world starts with clean grass.
      this.pathHeat.clear();
      this.lastPose.clear();
      this.poseTween.clear();
      this.wetness.clear();
      // Momentum belongs to a moment; a different moment starts still.
      this.rigStates.clear();
      this.rigAt.clear();
      this.turns.clear();
      this.axialLocks.clear();
      this.wokeAt.clear();
      this.stillSince.clear();
      return;
    }

    // Facing memory (FR-004): the horizontal component of the last move,
    // kept while standing still, derived only from served positions. The
    // same pass notes falling-asleep edges, so the curl transition plays
    // once and only once (US4 acceptance 3).
    this.movedNow.clear();
    // Served meows, stamped with the clock they ARRIVED on.
    //
    // `recent_meows` is a rolling window: an entry first appears the tick
    // AFTER it was spoken and lingers about ten, so the tick it carries is
    // never this one and it will be seen again on the next nine polls. Keyed
    // by (kitty, tick, kind) so a meow is stamped ONCE, on the frame it first
    // became visible -- which is the honest moment to start drawing it, and
    // the same trap that made a census of these read zero.
    //
    // Purrs are excluded here rather than at the draw: a purr is engine-owned
    // background state drawn as a glyph, never speech, and it outnumbers
    // speech four to one.
    if (!this.meowSeen) this.meowSeen = new Set();
    if (!this.meowAt) this.meowAt = new Map();
    for (const m of world.recent_meows || []) {
      if (m.kind === 'purr') continue;
      const key = `${m.kitty_id}:${m.tick}:${m.kind}`;
      if (this.meowSeen.has(key)) continue;
      this.meowSeen.add(key);
      this.meowAt.set(m.kitty_id, { at: now, kind: m.kind, drawn: false });
    }
    // The set would otherwise grow for the life of the page; the window is
    // ten ticks, so anything this old can never come back.
    if (this.meowSeen.size > 4000) this.meowSeen.clear();

    for (const kitty of world.kitties) {
      const was = prev.kitties.find((p) => p.id === kitty.id);
      const dx = kitty.pos.x - was.pos.x;
      // A reversal is a served fact about the pair, so the turn is
      // stamped here rather than sniffed at draw time -- which also means
      // a fresh connection has no turns pending and simply faces the way
      // it was served, exactly as before.
      const facing = this.facings.get(kitty.id);
      if ((dx > 0 && facing === 'left') || (dx < 0 && facing === 'right')) {
        this.turns.set(kitty.id, now);
      }
      // Four facings (2026-08-10). The engine moves cats on four axes only,
      // so exactly one of dx/dy is ever non-zero and there is no diagonal
      // to resolve -- the dominant-axis test below is a guard, not a rule.
      const dy = kitty.pos.y - was.pos.y;
      if (dx || dy) {
        const horizontal = Math.abs(dx) >= Math.abs(dy);
        const next = horizontal ? (dx > 0 ? 'right' : 'left') : dy > 0 ? 'south' : 'north';
        this.facings.set(kitty.id, next);
        // The last EAST/WEST facing, remembered separately. Only some poses
        // have an axial drawing, so a cat that walks north and then starts
        // grooming has to be drawn side-on -- and it should face the way it
        // last plausibly did, not a direction picked at random.
        if (!this.sideFacings) this.sideFacings = new Map();
        if (horizontal) this.sideFacings.set(kitty.id, next);
      }
      // A groomer faces the friend she is washing. The engine guarantees
      // the pair adjacent on a cardinal, so the direction is one of four
      // and needs no memory -- the target rides last_action on every tick
      // of the scene. Overrides walk history while the scene runs; what it
      // leaves behind afterwards ("sat back up facing the friend") is a
      // plausible history, so sideFacings is written through too.
      const gRef = kitty.last_action;
      if (gRef?.action === 'groom' && gRef.target != null) {
        const friend = world.kitties.find((k) => k.id === gRef.target);
        if (friend) {
          const fdx = friend.pos.x - kitty.pos.x;
          const fdy = friend.pos.y - kitty.pos.y;
          const fHoriz = Math.abs(fdx) >= Math.abs(fdy);
          const face = fHoriz ? (fdx > 0 ? 'right' : 'left') : fdy > 0 ? 'south' : 'north';
          this.facings.set(kitty.id, face);
          if (!this.sideFacings) this.sideFacings = new Map();
          if (fHoriz) this.sideFacings.set(kitty.id, face);
          // ...and this re-earns the axial drawing, exactly as a step does.
          //
          // `axialFor` locks a cat side-on the moment it wears a pose with no
          // axial drawing, and until 2026-08-24 only a STEP cleared it. Social
          // grooming happens standing still, so a cat that had just been
          // sitting, eating, drinking or washing itself carried that lock into
          // the scene and never shed it: the facing above turned it north, the
          // lock kept the drawing side-on, and `grooming-other` -- which HAS an
          // axial drawing, and whose axial case is the majority one at 54% of
          // targets -- was painted east-west at a friend due north.
          //
          // The lock's own rule is "served evidence that this cat is oriented
          // the way the view claims". A groom target is that, and more of it
          // than a step: the engine names the partner and guarantees the pair
          // adjacent on a cardinal, so the direction is known rather than
          // inferred from a delta. The anti-whip invariant is untouched -- this
          // fires only while `last_action` names a partner, which is the same
          // thing that put the cat in the pose.
          this.axialLocks.delete(kitty.id);
        }
      }
      // A cat eats and drinks from a tile BESIDE it, so it can be served
      // mid-meal facing away from the bowl -- owner, 2026-08-16: "pond is
      // to the left, cat is drinking facing right".
      //
      // `last_action` names no element for eat or drink (verified on the
      // live feed: the payload is a bare `{"action":"eat"}`), so which one
      // it is has to be worked out here. That is not a guess: the engine
      // picks by a predicate this can reproduce exactly -- the nearest
      // adjacent element of the kind, ties broken by lowest id, and for
      // chow only bowls that still hold a serving. Every field it needs is
      // served. See `adjacent_element_in` / `adjacent_stocked_chow_in`.
      //
      // Adjacency there is manhattan <= 1, which INCLUDES the cat's own
      // tile, so a cat drinking while standing in the pond resolves to
      // distance 0 and gets left alone -- as does a bowl directly north or
      // south. Neither carries any left-right information to face.
      // The INCOMING state's action: `last_action` is what happened during
      // the tick being ingested, so the meal is on `kitty`, not on `was`.
      const feeding = FEEDING_KIND[kitty.last_action?.action];
      if (feeding && !dx && !dy) {
        const at = nearestAdjacentOf(world.elements, kitty.pos, feeding);
        const towards = at && at.pos.x > kitty.pos.x ? 'right' : at && at.pos.x < kitty.pos.x ? 'left' : null;
        // Only ever writes when the facing is WRONG, so a meal that is
        // already facing its bowl stamps no turn and the cat does not
        // twitch once per tick of it. The write goes through the same
        // facings map as a step, so it then persists exactly as a step's
        // would -- until the next move re-faces it.
        if (towards && this.facings.get(kitty.id) !== towards) {
          this.turns.set(kitty.id, now);
          this.facings.set(kitty.id, towards);
          if (!this.sideFacings) this.sideFacings = new Map();
          this.sideFacings.set(kitty.id, towards);
        }
      }
      this.movedNow.set(kitty.id, dx !== 0 || kitty.pos.y !== was.pos.y);
      // A step is the one thing that re-earns an axial drawing: it is the
      // served evidence that this cat is oriented the way the view claims.
      if (dx || dy) this.axialLocks.delete(kitty.id);

      const sleepingNow = kitty.activity?.state === 'sleeping';
      if (sleepingNow && was.activity?.state !== 'sleeping') {
        this.sleepingSince.set(kitty.id, world.tick);
      } else if (!sleepingNow) {
        if (was.activity?.state === 'sleeping') this.wokeAt.set(kitty.id, now);
        this.sleepingSince.delete(kitty.id);
      }

      // How long this kitty has had nothing asked of it, in served ticks:
      // the gate on sitting down. Movement and any named activity both
      // count as something to do. A chase or a play needs no entry here,
      // because those wear their own pose and never reach the idle
      // vocabulary at all.
      const activity = kitty.activity?.state;
      if (this.movedNow.get(kitty.id) || (activity && activity !== 'idle')) {
        this.stillSince.delete(kitty.id);
      } else if (!this.stillSince.has(kitty.id)) {
        this.stillSince.set(kitty.id, world.tick);
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
          // The pounce it accompanies rides `progress`, so the plaything
          // has to be on the pace this pair plays at, not the served tick.
          duration: this.currPlayMs,
        });
      }
    }

    // Worn paths (spec 008 US5): every kitty's served tile warms its heat
    // entry on each *continuous* tick -- accumulation is independent of any
    // toggle (visibility is not memory). Cold entries are pruned here so a
    // long session never grows past the tiles actually walked.
    for (const kitty of world.kitties) {
      const key = `${kitty.pos.x},${kitty.pos.y}`;
      const entry = this.pathHeat.get(key);
      const carried = entry ? decayedPathHeat(entry, now) : 0;
      this.pathHeat.set(key, {
        heat: Math.min(VIEW.meadow.pathHeatCap, carried + 1),
        stampedAt: now,
      });
    }
    for (const [key, entry] of this.pathHeat) {
      if (decayedPathHeat(entry, now) < VIEW.meadow.pathVisibilityFloor) {
        this.pathHeat.delete(key);
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
    return Math.min(1, (now - this.currArrivedAt) / this.currPlayMs);
  }

  facingFor(id) {
    return this.facings.get(id) ?? 'left';
  }

  /** The cat's last east/west facing, for poses with no axial drawing. */
  sideFacingFor(id) {
    return this.sideFacings?.get(id) ?? 'left';
  }

  /**
   * May this cat be drawn in an axial view right now?
   *
   * Only `walking` and `idle` have an axial drawing, so every other pose
   * turns a north/south cat side-on. Going straight back the moment the
   * pose changes again is what produced the owner's report (2026-08-11):
   * a cat facing north at the water, alternating `drinking` and `idle`,
   * spun ninety degrees and back every tick while standing perfectly
   * still. Measured on a live feed, 60% of all view changes happened with
   * the served facing UNCHANGED, and 295 of those reversed inside one
   * tick.
   *
   * So the view is not free to change on a pose alone. Once a cat has
   * been drawn side-on for want of an axial drawing it stays side-on
   * until it takes a STEP -- the one piece of served evidence that it is
   * really oriented the way an axial view would claim. The invariant is
   * "the drawing turns when the cat turns", and a change of expression is
   * not a turn.
   *
   * Harmless while a cat faces east or west: there is no axial view to
   * lose, and the only way to start facing north or south is to move,
   * which lifts the lock in the same breath.
   */
  axialFor(id, poseHasAxial) {
    if (!poseHasAxial) {
      this.axialLocks.add(id);
      return false;
    }
    return !this.axialLocks.has(id);
  }

  movedFor(id) {
    return this.movedNow.get(id) ?? false;
  }

  /**
   * How far a kitty has walked, in tiles -- the clock the gait runs on.
   *
   * The walk used to ride `progress`, which is LINEAR, while `posFor`
   * eases the cat across every tile with easeInOutCubic. The cat's speed
   * therefore swings from a dead stop to three times its own average
   * inside one tile while the feet swept at a constant rate, so a planted
   * foot slid backward at the tile edges and forward through the middle,
   * reversing twice per tile. No choice of stride length could fix that,
   * because no instant is the average.
   *
   * Keying the gait to distance makes the easing cancel exactly: the foot
   * and the ground are now measured in the same units. A cat easing to a
   * stop slows its steps, which is what a cat does. And because distance
   * is continuous, the steps-per-tile dial is free to be fractional --
   * there is no longer a tick boundary for a part-finished stride to tear
   * against.
   */
  strideFor(id, now) {
    const done = this.odometer.get(id) ?? 0;
    const was = this.prev?.kitties.find((p) => p.id === id);
    const is = this.curr?.kitties.find((p) => p.id === id);
    if (!was || !is) return done;
    const step = Math.hypot(is.pos.x - was.pos.x, is.pos.y - was.pos.y);
    const p = this.progress(now);
    // The same curve posFor uses, or the feet would come off the ground.
    return done + step * (this.movedBefore.get(id) ? p : startEase(p));
  }

  /**
   * Float tile position: the blend of the two newest served states.
   *
   * This used to run easeInOutCubic on EVERY tile, which meant a cat
   * crossing eight tiles accelerated from a standstill and braked to a
   * dead stop eight times -- a stutter, not a walk (owner, 2026-08-08:
   * "stopping/starting every step"). A cat already walking now carries
   * its speed straight through the tile boundary; only a step taken from
   * rest eases in, and it arrives at exactly walking speed so the join
   * cannot be seen.
   *
   * There is deliberately no ease-OUT: the newest served state is the one
   * being walked into, so whether the cat stops after it is not knowable
   * yet, and a one-tick display lag to find out would cost more than it
   * buys. The stop is absorbed by the landing settle instead, which is
   * what that squash was always for.
   *
   * Safe because the gait rides distance (strideFor), not time: the feet
   * stay planted under any speed profile this picks.
   */
  posFor(kitty, now) {
    const was = this.prev?.kitties.find((p) => p.id === kitty.id);
    if (!was) return { x: kitty.pos.x, y: kitty.pos.y };
    const p = this.progress(now);
    const t = this.movedBefore.get(kitty.id) ? p : startEase(p);
    return {
      x: was.pos.x + (kitty.pos.x - was.pos.x) * t,
      y: was.pos.y + (kitty.pos.y - was.pos.y) * t,
    };
  }

  /**
   * The final pounce in flight, or null. Spec 039's lunge is the ONLY
   * two-tile step the world ever serves (ordinary locomotion is one tile
   * per tick), so the signature is exact -- a chasing kitty whose newest
   * pair covers Manhattan distance two -- and drawing it as a leap
   * asserts nothing the world did not say (Article V). Rides the same
   * progress the position blend rides, so the flight lands exactly when
   * the slide does. Null across a discontinuity: a generation snap is a
   * teleport, not a jump.
   */
  leapFor(id, now) {
    if (!this.curr || this.discontinuous) return null;
    const is = this.curr.kitties.find((k) => k.id === id);
    const was = this.prev?.kitties.find((p) => p.id === id);
    if (!is || !was) return null;
    if (is.last_action?.action !== 'chase') return null;
    const dist = Math.abs(is.pos.x - was.pos.x) + Math.abs(is.pos.y - was.pos.y);
    if (dist !== 2) return null;
    return { lift01: leapArc(this.progress(now)) };
  }

  /**
   * The gape of a served meow in flight, or null.
   *
   * Tied to the engine's own message channel and NOTHING ELSE: the client
   * never invents a call. Spec 028 took the meow off the activity menu, so a
   * meow rides alongside whatever the cat is doing rather than being its
   * action -- which is why this can play over a walk or a pounce without
   * contradicting the pose.
   *
   * Three gates, in the order they can disqualify:
   *
   *   1. POSE. The call is only drawn where the owner judged it reads --
   *      `VIEW.meowPoses`. A meow spoken mid-groom is skipped, not queued: a
   *      call drawn late is a cat mouthing at nothing.
   *   2. AGE. It plays once, from the frame it arrived. Past the envelope it
   *      is over; there is no catching up.
   *   3. COOLDOWN. At most one drawn call per cat per `meowCooldownMs`,
   *      whatever the engine's rate. The animation follows the world; the
   *      RHYTHM is ours, and has to be -- the Fog generation is expected to
   *      be much chattier and the same wiring would read as a tic.
   *
   * Returns the gape AND the kind, so a caller can tell what was said; only
   * the gape drives the drawing today.
   */
  meowFor(id, now, pose) {
    if (!this.curr || this.discontinuous) return null;
    if (!this.meowAt) return null;
    const m = this.meowAt.get(id);
    if (!m) return null;
    if (!VIEW.meowPoses.includes(pose)) return null;
    const gape = meowGape(now - m.at, VIEW);
    if (gape === undefined) return null;
    // The cooldown is spent when a call is first DRAWN, not when it is heard:
    // a meow skipped for its pose has cost nothing and the next one is free.
    if (!m.drawn) {
      const last = this.meowDrawnAt?.get(id);
      if (last !== undefined && now - last < VIEW.meowCooldownMs) return null;
      m.drawn = true;
      if (!this.meowDrawnAt) this.meowDrawnAt = new Map();
      this.meowDrawnAt.set(id, m.at);
    }
    return { gape, kind: m.kind };
  }

  /**
   * The groomer's eased sub-tile lean toward the friend she is washing, in
   * TILES (screen axes), or null when there is nothing to lean at.
   *
   * The state is a per-id envelope, advanced by the caller's clock: the
   * amount eases toward 1 while the groom-with-target scene runs and back
   * toward 0 the moment it ends. The direction is captured while the scene
   * is live and KEPT through the ease-out -- the friend who ended the scene
   * by walking away is not there to aim at any more, and re-aiming the
   * return trip would swing the sprite through an arc.
   *
   * Adjacency is trusted at up to 2 manhattan: the served step that ends
   * the scene can show the friend one tile into her walk before the engine
   * clears the activity, and snapping the lean off for that single frame
   * read as a flinch.
   */
  leanFor(id, now) {
    if (!this.curr || this.discontinuous) return null;
    if (!this.leans) this.leans = new Map();
    const is = this.curr.kitties.find((k) => k.id === id);
    const ref = is?.last_action;
    let aim = null;
    if (is && ref?.action === 'groom' && ref.target != null) {
      const friend = this.curr.kitties.find((k) => k.id === ref.target);
      if (friend) {
        const fdx = friend.pos.x - is.pos.x;
        const fdy = friend.pos.y - is.pos.y;
        const m = Math.abs(fdx) + Math.abs(fdy);
        if (m > 0 && m <= 2) aim = { dx: fdx / m, dy: fdy / m };
      }
    }
    let st = this.leans.get(id);
    if (!st) {
      if (!aim) return null;
      st = { amt: 0, dx: 0, dy: 0, at: now };
      this.leans.set(id, st);
    }
    const dt = Math.min(250, Math.max(0, now - st.at));
    st.at = now;
    const step = dt / Math.max(1, VIEW.groomLean.easeMs);
    if (aim) {
      st.dx = aim.dx;
      st.dy = aim.dy;
      st.amt = Math.min(1, st.amt + step);
    } else {
      st.amt = Math.max(0, st.amt - step);
      if (st.amt === 0) {
        this.leans.delete(id);
        return null;
      }
    }
    const t = smooth01(st.amt);
    return { dx: st.dx * t * VIEW.groomLean.tiles, dy: st.dy * t * VIEW.groomLean.tiles };
  }

  /**
   * Body velocity in tiles per second, screen axes (y down).
   *
   * Analytic rather than differenced. `posFor` is a known function of
   * progress, so its derivative is known too -- reading it costs nothing
   * and cannot jitter the way a frame-to-frame difference does on an
   * uneven rAF. It is also correct on the FIRST frame after a state
   * arrives, which a difference is not, and the first frame is exactly
   * when a tail ought to start moving.
   */
  velocityFor(id, now) {
    if (!this.curr || this.discontinuous) return { x: 0, y: 0 };
    const is = this.curr.kitties.find((k) => k.id === id);
    const was = this.prev?.kitties.find((p) => p.id === id);
    if (!is || !was) return { x: 0, y: 0 };
    const p = this.progress(now);
    // d/dp of the blend posFor uses. A cat already walking crosses the
    // tile linearly (slope 1); one stepping off from rest rides startEase,
    // whose slope is 4p - 3p^2 -- and which lands at exactly 1, which is
    // what makes the join between the two invisible.
    const slope = this.movedBefore.get(id) ? 1 : 4 * p - 3 * p * p;
    // The pace this pair is actually PLAYING at, not the served tick: this
    // is the derivative of a position that rides `progress`, so it has to
    // divide by the same clock progress does or the rig lags a speed the
    // cat is not travelling at.
    const perSec = 1000 / this.currPlayMs;
    return {
      x: (is.pos.x - was.pos.x) * slope * perSec,
      y: (is.pos.y - was.pos.y) * slope * perSec,
    };
  }

  /**
   * How much of this cat's travel is ACROSS the screen rather than into
   * it: 1 for a pure east/west step, 0 for due north or south. Feeds the
   * walk's foreshortening -- see cat-v2's walking case for why a vertical
   * walk drawn with a horizontal stride is 100% skate by construction.
   */
  travelHFor(id) {
    const is = this.curr?.kitties.find((k) => k.id === id);
    const was = this.prev?.kitties.find((p) => p.id === id);
    if (!is || !was) return 1;
    const dx = Math.abs(is.pos.x - was.pos.x);
    const dy = Math.abs(is.pos.y - was.pos.y);
    if (dx + dy === 0) return 1;
    return dx / (dx + dy);
  }

  /** 0..1 through an on-the-spot turn, or null when this cat is not
   * turning. Stamped from served facing changes in pushState. */
  turnFor(id, now) {
    const t0 = this.turns.get(id);
    if (t0 === undefined) return null;
    const t = (now - t0) / VIEW.turnMs;
    if (t >= 1) {
      this.turns.delete(id);
      return null;
    }
    return t;
  }

  /**
   * Advances one cat's rig and hands back the bag cat-v2's `applyRig`
   * consumes. Must be called at most once per cat per frame: it
   * integrates, so a second call in the same frame double-steps it.
   *
   * The motion maths lives in cat-v2 and the STATE lives here, which is
   * the split that lets the motion lab drive rigs with no animation layer
   * at all -- and lets the headless harness run with no cat vocabulary
   * loaded, since a missing `stepRig` simply means no rig.
   */
  rigFor(key, input, now) {
    if (typeof stepRig !== 'function') return null;
    const last = this.rigAt.get(key);
    let state = this.rigStates.get(key);
    if (!state || last === undefined || now - last > this.tickMs) {
      // No state, or a gap long enough that whatever we had describes a
      // different moment -- a hidden tab, a spell of reduced motion, a
      // fresh connection. Start at rest rather than springing out of
      // stale momentum. Same rule the pose blend uses, same reason.
      state = createRigState();
      this.rigStates.set(key, state);
    }
    this.rigAt.set(key, now);
    return stepRig(state, input, last === undefined ? 16 : Math.min(250, now - last));
  }

  /**
   * The pose an idle cat takes on its own initiative, or null to leave
   * the served pose alone (FR-008: idle motion can never imply an
   * action, so both of these are things a cat does while doing nothing).
   *
   * Returns { pose, phase } so the caller can hand the stretch its own
   * clock. Everything the pose tween needs comes free: sitting down,
   * standing up, and the stretch's entry and exit are all just pose
   * changes, and the blend was already there.
   */
  idlePoseFor(id, pose, now) {
    if (!this.curr) return null;
    // `sleep-curl` has to reach the wake below (2026-08-13). The tick a nap
    // ends is the tick the engine last APPLIED sleep, so since poseFor
    // started reading the applied action that tick arrives here as
    // `sleep-curl` rather than `idle` -- and this guard deleted the wake on
    // the very tick it was recorded, which silently removed every stretch in
    // the world. It cannot wait for the next tick either: measured over a
    // live capture, the tick after a wake is a bare idle stand 3% of the
    // time, so a deferred stretch is a stretch that never happens.
    if (pose !== 'idle' && pose !== 'loaf' && pose !== 'sleep-curl') {
      // The engine has given this cat something to do. An interrupted
      // stretch is ABANDONED rather than banked: resuming one later would
      // start it halfway through, which looks worse than never having
      // started it at all.
      this.wokeAt.delete(id);
      return null;
    }
    // A cat that just woke stretches. This is the one place the rarity
    // budget is not consulted, because it is not scheduled: it happens
    // exactly as often as cats wake up, which the engine decides.
    //
    // It fires on the OBSERVED wake, and cannot be moved to the last tick
    // of sleep however much better that would look: a tick is not known
    // to be the last one until the next state arrives, so anticipating it
    // would mean predicting the world, which this layer never does.
    const woke = this.wokeAt.get(id);
    if (woke !== undefined) {
      const t = (now - woke) / (VIEW.stretchTicks * this.tickMs);
      if (t < 1) return { pose: 'stretch', phase: t };
      this.wokeAt.delete(id);
    }
    if (pose !== 'idle') return null;
    const still = this.stillSince.get(id);
    if (still === undefined || this.curr.tick - still < VIEW.sitAfterTicks) return null;
    const slot = Math.floor((now + id * 7919) / VIEW.sitPeriodMs);
    if (idleHash(id, slot, IDLE_SALTS.sit) < VIEW.sitChance) return { pose: 'sit' };
    return null;
  }

  /**
   * The card portrait's play-pounce, or null. **Portraits only** -- see
   * VIEW.cardBeatPeriodMs for why the meadow must never call this.
   *
   * Pure in (id, now) like every other idle decision, so a still frame and
   * a test can both ask what a cat is doing at time T. Returns the beat
   * length with the phase, because the pounce's wiggle is authored as a
   * real frequency and needs to know how long the beat is -- the whole
   * point of doing this off the served tick.
   */
  /**
   * The card portrait's pose beat, or null. **Portraits only** -- see
   * VIEW.cardBeatPeriodMs for why the meadow must never call this.
   *
   * One weighted draw per period picks a sit-chain, a play-pounce, or
   * nothing. Pure in (id, now) like every other idle decision, so a still
   * frame and a test can both ask what a cat is doing at time T.
   *
   * The sit chain is sit -> stretch -> gone: the cat sits, holds, then gets
   * up through a stretch. `stretch` carries its own phase and returns to
   * neutral at the end, so the tail needs no blend out.
   */
  idleCardBeatFor(id, pose, now) {
    if (pose !== 'idle') return null;
    // Offset per cat, HASHED rather than a fixed multiple of the id: fixed
    // offsets land mod the period, and cats 1 and 4 once came out 453ms
    // apart, close enough to read as one clock.
    const period = VIEW.cardBeatPeriodMs;
    const clock = now + idleHash(id, 0, IDLE_SALTS.offset) * period;
    const slot = Math.floor(clock / period);
    const into = clock - slot * period;
    const table = [
      ['blink', VIEW.cardBlinkWeight],
      ['ears', VIEW.cardEarsWeight],
      ['scan', VIEW.cardScanWeight],
      ['yawn', VIEW.cardYawnWeight],
      ['sit', VIEW.cardSitWeight],
      ['pounce', VIEW.cardPounceWeight],
      ['rest', VIEW.cardRestWeight],
    ].map(([kind, w]) => [kind, Math.max(0, w || 0)]);
    const total = table.reduce((sum, [, w]) => sum + w, 0);
    if (total <= 0) return null;
    let draw = idleHash(id, slot, IDLE_SALTS.pick) * total;
    let pick = 'rest';
    for (const [kind, w] of table) {
      if (draw < w) { pick = kind; break; }
      draw -= w;
    }
    if (pick === 'rest') return null;

    const blinkMs = VIEW.slowBlinkDownMs + VIEW.slowBlinkHoldMs + VIEW.slowBlinkUpMs;
    const yawnMs = VIEW.yawnOpenMs + VIEW.yawnHoldMs + VIEW.yawnCloseMs;
    const stretchMs = VIEW.stretchTicks * this.tickMs;
    const lengths = {
      blink: blinkMs,
      ears: VIEW.idleMotionWindowMs,
      scan: VIEW.scanMs,
      yawn: yawnMs,
      sit: VIEW.sitHoldMs + stretchMs,
      pounce: VIEW.playBeatMs,
    };
    // Placed somewhere inside the slot, bounded by its OWN length, so a
    // long beat cannot start so late that it runs into the next slot --
    // the whole point of one-at-a-time.
    const start = idleOffsetFor(id, slot, period, lengths[pick], VIEW);
    const t = into - start;
    if (t < 0 || t >= lengths[pick]) return null;

    if (pick === 'sit') {
      if (t < VIEW.sitHoldMs) return { pose: 'sit' };
      return { pose: 'stretch', phase: (t - VIEW.sitHoldMs) / stretchMs };
    }
    if (pick === 'pounce') {
      return {
        pose: 'pouncing',
        phase: t / VIEW.playBeatMs,
        beatMs: VIEW.playBeatMs,
        wiggleHz: VIEW.playWiggleHz,
        sway: VIEW.playSway,
      };
    }
    // The face and ear beats. They ride the rig, so this only says what and
    // how far -- the springs are the portrait's own (`'card' + id`).
    if (pick === 'blink') return { pose: 'idle', blinkLid: slowBlinkLid(t, VIEW) };
    if (pick === 'ears') {
      const u = t / VIEW.idleMotionWindowMs;
      return {
        pose: 'idle',
        earTwitch: Math.sin(u * Math.PI),
        earTwitchSide: idleHash(id, slot, IDLE_SALTS.side) < 0.5 ? -1 : 1,
      };
    }
    if (pick === 'scan') {
      const u = t / VIEW.scanMs;
      const env = easeSmooth(Math.min(1, u * 3)) * (1 - easeSmooth(Math.max(0, (u - 0.6) / 0.4)));
      const dir = idleHash(id, slot, IDLE_SALTS.look);
      return {
        pose: 'idle',
        gaze: { x: (dir * 2 - 1) * env, y: (idleHash(id, slot, IDLE_SALTS.side) - 0.5) * env },
      };
    }
    if (pick === 'yawn') return { pose: 'idle', yawn: yawnGape(t, VIEW) };
    return null;
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
   * The v2 pose blend (motion wiring): a pose change opens a short
   * pose-space blend for drawCatTween, and arriving -- walking to a
   * stand -- lands with the lab's slow settle squash, concurrent with its
   * blend (the lab's own timeline). Detection is draw-time, so mid-tick
   * changes (the fall-asleep loaf -> sleep-curl swap) blend too. The
   * from-phase freezes at the change: the old pose leaves exactly as last
   * seen. Only the v2 renderer path consumes this; the recording is
   * harmless when nothing reads it.
   */
  tweenFor(id, pose, phase, now) {
    const last = this.lastPose.get(id);
    this.lastPose.set(id, { pose, phase, at: now });
    if (last && last.pose !== pose) {
      if (now - last.at <= this.tickMs) {
        // Newest wins: a change mid-blend restarts from the old target.
        this.poseTween.set(id, { from: last.pose, fromPhase: last.phase, at: now });
      } else {
        // A draw gap past a tick is a different moment (hidden tab, a
        // reduced-motion spell): snap, never a catch-up blend.
        this.poseTween.delete(id);
      }
    }
    const tw = this.poseTween.get(id);
    if (!tw) return null;
    const arrive = tw.from === 'walking' && (pose === 'idle' || pose === 'loaf');
    const blendMs = Math.min(
      arrive ? VIEW.arriveBlendMs : VIEW.poseBlendMs,
      VIEW.blendTickShareCap * this.tickMs,
    );
    const elapsed = now - tw.at;
    const out = {};
    if (elapsed < blendMs) {
      out.blend = {
        from: tw.from,
        fromPhase: tw.fromPhase,
        // easeBack, not easeSmooth: the blend now leans back before it
        // goes and drifts a little past before it settles. Costs nothing
        // -- pose space is linear, so the over- and under-shoot are real
        // poses either side of the two ends.
        t: easeBack(elapsed / blendMs),
      };
    }
    if (arrive && elapsed < VIEW.settleMs) {
      const u = elapsed / VIEW.settleMs;
      // The shape belongs to the vocabulary that draws it. v2 deforms the cat
      // -- head keeps its skull, legs take the compression, tail whips -- and
      // v1 has no such function, so it keeps the whole-canvas squash. Both
      // values are emitted and each path reads its own.
      const curve = globalThis.CatV2 && globalThis.CatV2.settleCurve;
      const k = curve ? curve(u) : Math.sin(Math.PI * easeSmooth(u));
      out.settle = k;
      out.sy = 1 - VIEW.settleDip * Math.max(0, k);
    }
    if (!out.blend && out.sy === undefined) {
      this.poseTween.delete(id);
      return null;
    }
    return out;
  }

  /**
   * How wet a cat's COAT is, 0..1 -- a fact about the cat, not the place.
   *
   * Still independent of the pose (owner call, 2026-08-04): a cat
   * drinking in a pond keeps its drinking pose and must still look wet.
   * What changed on 2026-08-10 is what this drives.
   *
   * **The invariant: this may only ever change COLOUR.** Every piece of
   * water GEOMETRY -- the waterline clip, the meniscus, the lost ground
   * shadow, the displacement rings -- is driven by `submersionFor`, which
   * is spatial and is exactly zero the moment the cat is clear of the
   * water. This signal outlives the pond by design (`furDryMs`), so
   * anything positional hung off it draws water on grass. That was the
   * bug; keeping the two apart is the fix.
   */
  wetFor(id, onWater, now) {
    const prev = this.wetness.get(id);
    if (!prev) {
      // First sight settles rather than fading in, as pose memory does.
      this.wetness.set(id, { on: onWater, at: now, from: onWater ? 1 : 0 });
      return onWater ? 1 : 0;
    }
    if (prev.on !== onWater) {
      this.wetness.set(id, { on: onWater, at: now, from: wetValue(prev, now) });
    }
    return wetValue(this.wetness.get(id), now);
  }

  /**
   * Phase and micro-motion for one kitty (US4). Action poses run on the
   * tick clock (their whole animation fits the tick that served them);
   * resting poses breathe on a slow local cycle; idle cats get their
   * scheduled blink, tail flick, or ear twitch -- gentle, occasional, and
   * never during an action, so idle motion can never imply one (FR-008).
   */
  motionFor(id, pose, now, dials = VIEW) {
    // The walk is measured in ground covered, not in time (strideFor);
    // eating, drinking and the pounce ride the tick clock; the lick rides
    // its own (below).
    if (pose === 'walking') return { phase: this.strideFor(id, now) };
    const isAction =
      pose === 'pouncing' ||
      pose === 'eating' ||
      pose === 'drinking';
    if (isAction) return { phase: this.progress(now) };

    const seed = id * 997;
    if (pose === 'grooming' || pose === 'grooming-other') {
      // The lick rides its OWN clock. On the tick beat it nodded three
      // times per 800ms and read dog-like (owner, 2026-08-22); a cat is
      // slower, and a lick has no reason to sync to world ticks. Rolls on
      // an ambient modulo like the breath -- seeded so a clowder does not
      // lick in unison -- and wraps seamlessly, since the pose's three
      // nods end where they begin.
      return { phase: ((now + seed) % dials.groomCycleMs) / dials.groomCycleMs };
    }
    const motion = {
      phase: ((now + seed) % dials.breathePeriodMs) / dials.breathePeriodMs,
    };
    if (pose === 'sleep-curl') return motion; // sleepers just breathe
    if (pose === 'swim') {
      // Paddling rides the tick clock on the move, like the walk it
      // replaces; a floating cat bobs on the ambient cycle and, like a
      // sleeper, skips the idle twitches (its tail is underwater).
      if (this.movedFor(id)) return { phase: this.progress(now) };
      return motion;
    }

    // Idle and loafing cats are never statues: each slot draws a motion and
    // starts it somewhere inside the slot. A slot may equally draw nothing,
    // which is what stops the ones that do land from reading as scheduled.
    const period = idlePeriodFor(id, dials);
    const wobble = now + id * 1337;
    const slot = Math.floor(wobble / period);
    const at = wobble % period;
    const pick = idlePickFor(id, slot, dials);
    if (pick === 'rest') return motion; // a slot off, breathing as usual

    const blinkMs =
      dials.slowBlinkDownMs + dials.slowBlinkHoldMs + dials.slowBlinkUpMs;
    const yawnMs = dials.yawnOpenMs + dials.yawnHoldMs + dials.yawnCloseMs;
    // Each motion's jitter must be bounded by its OWN length. Sharing the
    // 420ms window let the two long motions start as late as a short one
    // may and then run past the end of their slot -- into the next slot,
    // where the next motion is already playing. Overlapping idle motions
    // are precisely what the slot machinery exists to prevent.
    const durationMs =
      pick === 'blink' ? blinkMs
        : pick === 'yawn' ? yawnMs
          : pick === 'scan' ? dials.scanMs
            : dials.idleMotionWindowMs;
    // Time into the motion itself, which is what every envelope below is
    // measured from -- negative before it starts, past `durationMs` after.
    const t = at - idleOffsetFor(id, slot, period, durationMs, dials);

    if (pick === 'ears') {
      if (t >= 0 && t < dials.idleMotionWindowMs) {
        const u = t / dials.idleMotionWindowMs;
        // A continuous envelope on ONE ear, replacing a boolean that
        // flipped BOTH for the whole window. A cat twitches one ear; two
        // ears going back together is a mood, not a twitch, and the
        // instant on/off was a switch rather than a motion either way.
        // `earsBack` is kept for the v1 path, which has no rig to ease.
        motion.earTwitch = Math.sin(u * Math.PI);
        motion.earTwitchSide = idleHash(id, slot, IDLE_SALTS.side) < 0.5 ? -1 : 1;
        motion.earsBack = u < 0.5;
      }
      return motion;
    }

    if (pick === 'scan') {
      // A slow look somewhere and back. The gaze channel is sprung in the
      // rig, so this only has to say where and for how long.
      if (t >= 0 && t < dials.scanMs) {
        const u = t / dials.scanMs;
        const env = easeSmooth(Math.min(1, u * 3)) * (1 - easeSmooth(Math.max(0, (u - 0.6) / 0.4)));
        const dir = idleHash(id, slot, IDLE_SALTS.look);
        motion.gaze = {
          x: (dir * 2 - 1) * env,
          y: (idleHash(id, slot + 7, IDLE_SALTS.look) * 1.2 - 0.7) * env,
        };
      }
      return motion;
    }

    if (pick === 'yawn') {
      // Opens quicker than it closes: the other way round reads as a
      // hiss, which is the last thing this world wants.
      const gape = yawnGape(t, dials);
      if (gape !== undefined) motion.yawn = gape;
      return motion;
    }

    // v1 keeps its snap blink over its own short window; the v2 renderer
    // prefers the eased lid and drops the snap, so v1 stays bit-identical.
    if (t >= 0 && t < dials.idleMotionWindowMs) motion.eyesOverride = 'closed';
    const lid = slowBlinkLid(t, dials);
    if (lid !== undefined) motion.blinkLid = lid;
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

  /* THE HUNTER'S FACE IS RETIRED (owner, 2026-08-20), and with it
   * `expressionFor`, `PURSUING_ACTIONS` and `hunterGateTiles`, which existed
   * for nothing else. A cat chasing prey now looks exactly like a cat chasing
   * a kitty, which is what the presentation already did for roughhousing.
   *
   * The reason is worth keeping, because it is not "the drawing was wrong":
   * the fierce face was cute at a 31px thumbnail and reads as fierce at
   * 57-103px, and fierce is not the vibe. Retiring it also drops "hunting
   * kitties do not blink" (owner, 2026-08-02), deliberately -- the whole
   * point is that a hunt is drawn the way play already is, and players blink.
   *
   * The DRAWING survives: `eyesOverride: 'focused'` and `FOCUS_VARIANTS` are
   * still there, still dialled, still exercised by the gallery card and by
   * cat.js's v1 path. Nothing in the world reaches them any more. If those
   * dials are ever to go too, that is a separate deletion and the owner's
   * call -- 79 lines of values she judged.
   */

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

  /**
   * Float tile position for a moving element (007 refinement, 2026-07-20):
   * critters glide on the same eased clock as kitties. Spawns and
   * anything farther than `critterGlideMaxTiles` snap -- that is not
   * motion, it is a different moment of the world.
   */
  elementPosFor(el, now) {
    const was = this.prev?.elements.find((p) => p.id === el.id);
    // The glide bound is per KIND: a greeble's dart legally covers three
    // tiles (spec 039), a bug's skitter never passes two -- and each
    // kind's bound is also its teleport boundary, so a respawn beyond it
    // still snaps.
    const max = el.kind === 'greeble'
      ? VIEW.greebleGlideMaxTiles
      : VIEW.critterGlideMaxTiles;
    if (
      !was ||
      Math.abs(el.pos.x - was.pos.x) > max ||
      Math.abs(el.pos.y - was.pos.y) > max
    ) {
      return { x: el.pos.x, y: el.pos.y };
    }
    const t = easeInOutCubic(this.progress(now));
    return {
      x: was.pos.x + (el.pos.x - was.pos.x) * t,
      y: was.pos.y + (el.pos.y - was.pos.y) * t,
    };
  }

  /**
   * The worn-path snapshot (spec 008 US5): decayed heat per walked tile,
   * filtered to what is visible, normalized to 0..1. Available in still
   * frames too -- revealed trails are state, not motion (FR-012).
   */
  wornPaths(now) {
    const entries = [];
    for (const [key, entry] of this.pathHeat) {
      const heat = decayedPathHeat(entry, now);
      if (heat < VIEW.meadow.pathVisibilityFloor) continue;
      const [x, y] = key.split(',').map(Number);
      // Display saturates at pathFullHeat, not the memory cap (revision 1:
      // normalizing by the cap left a once-walked tile at 3% alpha --
      // arithmetically invisible). A few passes now read plainly.
      entries.push({ x, y, heat01: Math.min(1, heat / VIEW.meadow.pathFullHeat) });
    }
    return entries;
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
      strideFor: (id) => this.strideFor(id, now),
      adjustPose: (id, pose) => (still ? pose : this.adjustPose(id, pose, now)),
      // Still frames get the static pose for the state, nothing more
      // (FR-015): phase 0, no blinks, no flicks.
      motionFor: (id, pose) => (still ? { phase: 0 } : this.motionFor(id, pose, now)),
      // The v2 pose blend + landing settle. Null in still frames -- a
      // still frame is the pose, held -- and recording skips with it, so
      // a spell of stillness can never seed a stale blend.
      tweenFor: (id, pose, phase) => (still ? null : this.tweenFor(id, pose, phase, now)),
      // The rig (2026-08-10). Null in a still frame, which is what makes
      // reduced motion and the snap after a discontinuity draw the
      // un-rigged vocabulary exactly as they always did: applyRig(L, null)
      // is the same drawing as no rig at all.
      // A still frame gets gaze and nothing else: where a cat is looking is
      // served state, not motion, so it survives reduced motion for the
      // same reason the focused eyes and the worn paths do (R6, FR-012).
      // The idle scan is not included and cannot be -- `motionFor` returns
      // bare phase 0 in a still frame -- so only a real served target ever
      // moves a still cat's eyes.
      rigFor: (key, input) =>
        still
          ? (typeof stillRig === 'function' ? stillRig(input) : null)
          : this.rigFor(key, input, now),
      velocityFor: (id) => (still ? { x: 0, y: 0 } : this.velocityFor(id, now)),
      // The final pounce's flight (spec 039). Motion, not state: a still
      // frame holds the pose ON the ground, like every other motion class.
      leapFor: (id) => (still ? null : this.leapFor(id, now)),
      // Stilled with everything else: a paused frame holds the call it was
      // on rather than replaying it.
      meowFor: (id, pose) => (still ? null : this.meowFor(id, now, pose)),
      leanFor: (id) => (still ? null : this.leanFor(id, now)),
      travelHFor: (id) => this.travelHFor(id),
      sideFacingFor: (id) => this.sideFacingFor(id),
      // Whether an axial drawing is allowed right now. Applies in still
      // frames too: reduced motion still receives a state per tick, so
      // the whip this prevents would be just as visible there -- more so,
      // with no motion to distract from it.
      axialFor: (id, poseHasAxial) => this.axialFor(id, poseHasAxial),
      // The served beat length, so presentation code whose timing is a
      // real-world frequency (the pounce wiggle) can derive its rate from
      // the tick rather than assuming 800ms.
      tickMs: this.tickMs,
      turnFor: (id) => (still ? null : this.turnFor(id, now)),
      // A still frame is the served pose, held -- a cat is not caught
      // mid-stretch in a frame that is meant to have no motion in it.
      idlePoseFor: (id, pose) => (still ? null : this.idlePoseFor(id, pose, now)),
      idleCardBeatFor: (id, pose) => (still ? null : this.idleCardBeatFor(id, pose, now)),
      // Wetness carries state (this cat is in water), not motion, so a
      // still frame gets it at full strength rather than not at all --
      // the worn-paths and focused-eyes rule (FR-012, R6).
      wetFor: (id, onWater) =>
        still ? (onWater ? 1 : 0) : this.wetFor(id, onWater, now),
      // One-shot particles rest under reduced motion; the sustained
      // *informational* cues (focused eyes, the thought bubble) do not --
      // they carry state, not motion (R6).
      oneShotFor: (id) => (still ? null : this.oneShotFor(id, now)),
      // Prop motion (spec 007): one wall-clock phase source over a named
      // period, seeded by an element *or* kitty id -- 0 when still, so
      // reduced motion gets static props with full state (FR-013).
      propPhaseFor: (id, periodMs) =>
        still ? 0 : ((now + id * 4241) % periodMs) / periodMs,
      thoughtFor: (kitty) => this.thoughtFor(kitty),
      elementAlphaFor: (el) => (still ? 1 : this.elementAlphaFor(el, now)),
      elementPosFor: (el) =>
        still ? { x: el.pos.x, y: el.pos.y } : this.elementPosFor(el, now),
      expired: still ? [] : this.expiredElements,
      expiredAlpha: still ? 0 : this.expiredAlpha(now),
      // Worn paths draw in still frames too: the overlay carries state
      // (where cats have walked), not motion (spec 008 FR-012).
      wornPaths: () => this.wornPaths(now),
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
 * Where a frame of the given span sits, in world tiles, once it is held
 * inside the world.
 *
 * A frame WIDER than the world centres it instead of clamping, because
 * clamping to a range whose minimum exceeds its maximum is how you get a
 * frame pinned to one edge with void on the other. That case is not
 * hypothetical: it is every frame the camera draws while it is off, where
 * the frame is exactly the world.
 */
function clampFrame(edge, worldSpan, frameSpan) {
  if (frameSpan >= worldSpan) return (worldSpan - frameSpan) / 2;
  return Math.min(Math.max(edge, 0), worldSpan - frameSpan);
}

/**
 * The camera (spec 036): a window over the world rather than a map of it.
 *
 * It reports where to look in WORLD TILES and how many of them fit across.
 * The renderer turns that into a tile size and a pan -- see `draw`. Scale
 * arrives by moving `renderer.tile`, never by scaling the context, because
 * `tile` is the size every art value is a fraction of (it was also what the
 * 44px `fine` gate read, until that gate was deleted 2026-08-18 -- the
 * invariant outlived its most-cited example and still holds, above
 * all) and camera mode exists to cross exactly that threshold.
 *
 * `update` is called from inside `renderer.draw`, which is what makes the
 * reduced-motion path safe: `startLoop` is skipped entirely when reduced
 * motion is set, so a camera advanced from the rAF callback would be
 * frozen for those viewers while testing perfectly. Both the loop and the
 * served-tick `redraw` go through `draw`, so there is one call site and it
 * cannot be half-wired.
 *
 * While `on` is false this is an identity: the frame is the whole world,
 * `left`/`top` are 0, and `cssWidth / across` is the tile `resizeFor`
 * already computed. That is the off state FR-002 requires, and it is the
 * same code path rather than a bypass around it.
 */
class Camera {
  constructor(dials = VIEW.camera) {
    this.dials = dials;
    /** Camera mode. app.js owns the flag; everything here just reads it. */
    this.on = false;
    /**
     * Whether the viewer asked for reduced motion. Kept in step by
     * `anim.init`, because the camera cannot tell from a view alone: a
     * still frame means "arrive" for a reduced-motion viewer and "this is
     * the same moment again" for everyone else, and those are opposites.
     */
    this.reduced = false;
    /** The kitty the viewer chose, or null. Survives `on` going false. */
    this.followId = null;
    /** Frame width in world tiles. */
    this.across = 0;
    /** Aim point in world tiles. */
    this.aimX = 0;
    this.aimY = 0;
    /** Frame origin in world tiles, held inside the world. */
    this.left = 0;
    this.top = 0;
    /**
     * Previous frame's clock reading. NULL, not 0, because 0 is a
     * legitimate reading -- `performance.now()` is near zero at page load,
     * and a 0 sentinel silently drops the first frames of easing.
     */
    this.lastAt = null;

    /* -- The shot picker (spec 038) ----------------------------------- */
    /** The incumbent shot: a Set of kitty ids, or null before the first
     *  decision. Membership drifts kitty by kitty; identity is what ties
     *  and rivals are judged against. */
    this.shotIds = null;
    /** Whether decide() has ever run -- world.tick may legitimately be
     *  undefined in a fixture, so "never decided" needs its own flag. */
    this.hasDecided = false;
    this.lastTick = undefined;
    /** The followId the last decision was made under, so a click
     *  re-decides on the very next frame rather than the next tick. */
    this.decidedFollowId = null;
    /** {cssWidth, aspect} the last decision consumed -- a resize is a
     *  discrete retarget (one episode), never a per-frame pursuit. */
    this.lastBounds = null;
    /** Disjoint-group evidence chains: [{ids:Set, members, nearTicks,
     *  farTicks}]. See evidenceFor -- the spec-032 seam. */
    this.chains = [];
    /** Consecutive ticks the shot's groups have failed to share a frame;
     *  a shed fires only at shedDwellTicks (the flap damper). */
    this.unfitTicks = 0;
    /** Consecutive ticks the hold has been pressed; a correction latches
     *  from rest only at pressDwellTicks (FR-007 as amended 2026-08-21). */
    this.pressTicks = 0;
    /**
     * The one mover of the camera. null means REST, and REST means the
     * frame is BIT-STILL -- nothing eases, nothing drifts (038 FR-006).
     * {kind, from, goal, elapsed, duration, committed}.
     */
    this.episode = null;
  }

  /**
   * The two limits, in TILES, derived from the viewport (spec 037).
   *
   * ONE derivation, deliberately: the fit clamps to this pair, the
   * overflow predicate compares against this ceiling, and the ground bake
   * keys on this floor. If they read different ceilings, the overflow
   * centre-hold would engage at a width the camera never reaches --
   * invisible to the eye (contracts/zoom.md invariant 2).
   *
   * One FUNCTION, not one call: the frame's fit and `bakeTileFor` each
   * ask, so this runs twice a frame. That is deliberate and safe: it is pure
   * in (world.width, cssWidth, dials) -- two callers cannot disagree. Do not
   * "optimise" it into cached state on the instance: a cache would have to
   * be invalidated on resize, and a stale one reintroduces exactly the
   * disagreement the single derivation exists to prevent.
   *
   * The floor is the tile size the camera zooms IN to; the ceiling is the
   * smallest tile it will widen to. Expressed in pixels, the zoom range
   * becomes their ratio and stops varying with the window.
   */
  limitsFor(world, cssWidth, aspect = null) {
    const d = this.dials;
    // A viewport of zero or NaN must still produce a usable frame (FR-014).
    // This is not hypothetical: the map has no width until the page has laid
    // out, so the FIRST FRAME of every session arrives here, and every limit
    // below divides by or multiplies against it. The whole world is the
    // honest answer -- it is what the camera shows while it is off.
    if (!Number.isFinite(cssWidth) || cssWidth <= 0) {
      return { floorTiles: world.width, ceilingTiles: world.width };
    }
    // The minimum raises the floor; the world caps it. Both clamps are
    // continuous in cssWidth, which is what makes a resize across either
    // boundary produce no jump (FR-017, SC-009).
    //
    // The floor is capped one tile below the world for the SAME reason the
    // ceiling is, and it has to be: the ceiling is raised back to meet the
    // floor (FR-013), so a floor allowed to reach the world's width drags
    // the ceiling with it and the camera stops cropping at every zoom.
    // Capping only the ceiling looked sufficient and was not -- on a
    // 10-tile world both limits came back at 10. Found in review of PR
    // #246; unreachable on today's 20x20 map, which is why no sweep saw it.
    const edge = Math.max(
      Math.min(world.width - 1, world.width / d.minZoomVsBase),
      1,
    );
    const floorTiles = Math.min(Math.max(cssWidth / d.floorPx, d.minTiles), edge);
    // How wide the camera may ever go, in tiles. TWO bounds, and the tighter
    // wins:
    //
    //   world/minZoomVsBase -- the camera must stay at least that many times
    //     zoomed in versus the whole-world view, or it is not a camera. This
    //     is what governs on a 20-tile world.
    //   world - 1 -- a backstop so the frame always crops at all, which is
    //     what keeps 036's FR-005 (let a wanderer leave rather than shrink
    //     everyone) alive on worlds too small for the first bound to bite.
    //
    // `world - 1` used to be the ONLY bound, and it was not an answer: at a
    // 1200px map the pixel ceiling asks for 24 tiles of a 20-tile world, so
    // the clamp decided everything at the large end and one tile of crop is
    // indistinguishable from camera-off. Reported from WQHD, 2026-08-19.
    // THE THIRD BOUND, and the only one stated on the vertical: at most
    // `ceilingRows` rows of world. `rows = across * aspect`, so the cap in
    // across is `ceilingRows / aspect`.
    //
    // Gated on `aspect < 1` because that is what "the height is the scarce
    // axis" means. On a square canvas -- every viewport but a letterboxed one
    // -- rows and across are the same number, so a row cap would silently
    // become an across cap and zoom in everywhere. That is not a defensive
    // guard; it is the whole scope of the dial.
    //
    // Ceiling-only by construction, which is what keeps `bakeTileFor` honest:
    // it asks for the FLOOR and passes no aspect, so it cannot disagree with
    // the fit about anything it reads (contracts/zoom.md invariant 2).
    const rowCap =
      Number.isFinite(aspect) && aspect > 0 && aspect < 1 && d.ceilingRows > 0
        ? d.ceilingRows / aspect
        : Infinity;
    const ceilingTiles = Math.max(
      Math.min(cssWidth / d.ceilingPx, edge, rowCap),
      floorTiles, // may MEET the floor on a tiny viewport, never cross it (FR-013)
    );
    return { floorTiles, ceilingTiles };
  }

  /**
   * Drawn positions, never served ones. The pacer eases between states, so
   * a camera reading served positions jumps a tick ahead and eases back
   * once per tick -- the camera leading the cats it is following. A tile
   * coordinate addresses the tile's ORIGIN; a cat is drawn at its centre.
   */
  atOf(view) {
    return (k) => {
      const p = view && view.posFor ? view.posFor(k) : k.pos;
      return { x: p.x + 0.5, y: p.y + 0.5 };
    };
  }

  /**
   * Connected components at the link radius (038 FR-002): kitties within
   * `linkTiles` of one another belong to one group, transitively.
   */
  groupsFor(kitties, at) {
    const link = this.dials.linkTiles;
    const groups = [];
    const seen = new Set();
    for (const k of kitties) {
      if (seen.has(k.id)) continue;
      const members = [k];
      seen.add(k.id);
      for (let i = 0; i < members.length; i += 1) {
        const a = at(members[i]);
        for (const o of kitties) {
          if (seen.has(o.id)) continue;
          const b = at(o);
          if (Math.hypot(a.x - b.x, a.y - b.y) <= link) {
            seen.add(o.id);
            members.push(o);
          }
        }
      }
      groups.push(members);
    }
    return groups;
  }

  /** Bounding box of drawn positions, plus its centre -- the aim of every
   *  shot, and the whole of the overflow hold (FR-007a). */
  bboxOf(cats, at) {
    let minX = Infinity;
    let maxX = -Infinity;
    let minY = Infinity;
    let maxY = -Infinity;
    for (const k of cats) {
      const p = at(k);
      if (p.x < minX) minX = p.x;
      if (p.x > maxX) maxX = p.x;
      if (p.y < minY) minY = p.y;
      if (p.y > maxY) maxY = p.y;
    }
    return {
      minX, maxX, minY, maxY,
      cx: (minX + maxX) / 2,
      cy: (minY + maxY) / 2,
    };
  }

  /**
   * The frame width, in tiles, that holds these kitties with breathing
   * room (038 FR-005). The margin is a FRACTION of the frame per side --
   * span = across * (1 - 2f) -- so it scales down to the phone instead of
   * eating 68% of its frame, and the vertical costs width through the
   * canvas aspect exactly as the old fit priced it.
   */
  fitWidthFor(cats, at, aspect) {
    return this.fitWidthOf(this.bboxOf(cats, at), aspect);
  }

  /** The same fit, from a bbox the caller already swept -- goalFrameFor
   *  and holdViolated each need the box AND the fit, and sweeping the
   *  positions twice per caller doubled the hold's frame cost (high
   *  review 2026-08-21, below-cap). */
  fitWidthOf(b, aspect) {
    const denom = Math.max(1e-6, 1 - 2 * this.dials.fitMarginFrac);
    return Math.max(b.maxX - b.minX, (b.maxY - b.minY) / (aspect || 1)) / denom;
  }

  /** Where a shot of these kitties wants the frame: centred on their box,
   *  sized to their fit, clamped to the 037 band. `overflow` is the fit
   *  asking more than the ceiling -- a first-class state on the phone. */
  goalFrameFor(cats, at, aspect, floorTiles, ceilingTiles) {
    const b = this.bboxOf(cats, at);
    const need = this.fitWidthOf(b, aspect);
    return {
      aimX: b.cx,
      aimY: b.cy,
      across: Math.min(Math.max(need, floorTiles), ceilingTiles),
      overflow: need > ceilingTiles + 1e-9,
    };
  }

  /**
   * The maximal-count union of groups that fits the ceiling (038 FR-003).
   * Greedy from every seed; a seed group is admitted WHOLE even when it
   * alone overflows (the camera clamps and frames it partially -- reality,
   * not an error). Ties prefer overlap with `pref` (incumbency), then the
   * lexicographically-lowest sorted id set, so a cold start is
   * deterministic under roster reorder (research D6) -- all the way down:
   * the greedy expansion carries its own lowest-id key too.
   */
  bestWindowFor(groups, at, aspect, ceilingTiles, pref = null) {
    let best = null;
    for (let i = 0; i < groups.length; i += 1) {
      const cats = [...groups[i]];
      const rest = groups.filter((_, j) => j !== i);
      let grew = true;
      while (grew) {
        grew = false;
        let pick = -1;
        let ps = null;
        for (let j = 0; j < rest.length; j += 1) {
          if (this.fitWidthFor([...cats, ...rest[j]], at, aspect) <= ceilingTiles + 1e-9) {
            const here = this.bboxOf(cats, at);
            const there = this.bboxOf(rest[j], at);
            // THREE keys, the last one order-proof (review 2026-08-21,
            // finding 5): an exact [count, distance] tie -- realistic on
            // integer tile layouts -- otherwise fell to array order, and a
            // server reordering its roster flipped the framed wing on
            // every cold start (research D6's determinism, restated).
            const score = [
              rest[j].length,
              -Math.hypot(there.cx - here.cx, there.cy - here.cy),
              -Math.min(...rest[j].map((k) => k.id)),
            ];
            if (pick < 0 || score[0] > ps[0]
              || (score[0] === ps[0] && score[1] > ps[1])
              || (score[0] === ps[0] && score[1] === ps[1] && score[2] > ps[2])) {
              pick = j;
              ps = score;
            }
          }
        }
        if (pick >= 0) {
          cats.push(...rest[pick]);
          rest.splice(pick, 1);
          grew = true;
        }
      }
      const ov = pref ? cats.filter((k) => pref.has(k.id)).length : 0;
      // The outer tie key is the whole SORTED id set, compared
      // lexicographically -- not just the lowest member (review
      // 2026-08-21, finding 5): two grown windows can share their lowest
      // kitty ({1,2}+either wing), and a min-id key ties exactly where
      // the seed ORDER -- the roster order -- would decide the shot.
      const ids = cats.map((k) => k.id).sort((a, b) => a - b);
      const lex = (a, b) => {
        for (let i = 0; i < Math.min(a.length, b.length); i += 1) {
          if (a[i] !== b[i]) return a[i] - b[i];
        }
        return a.length - b.length;
      };
      if (!best || cats.length > best.n
        || (cats.length === best.n && ov > best.ov)
        || (cats.length === best.n && ov === best.ov && lex(ids, best.ids) < 0)) {
        best = { cats, n: cats.length, ov, ids };
      }
    }
    return best ? best.cats : [];
  }

  /**
   * ONE tick of persistence evidence -- research D5/D10, and the spec-032
   * seam: this consumes the current tick's disjoint groups and yields
   * consecutive-tick counters per chain. The thresholds live OUTSIDE, at
   * decide()'s two comparison sites, so a lookahead buffer can replace
   * the window's source without touching the grammar.
   *
   * Chains carry identity by STRICT-majority member overlap (> half the
   * larger), so a rival that churns one member mid-dwell keeps its clock
   * -- keying on exact member sets would reset a counter every join/leave
   * and a churning rival could never reach 15.
   *
   * ONE HEIR PER CHAIN, and an exact half is NOT an heir (review
   * 2026-08-21, both passes). Plain majority admitted exact halves, so an
   * even split first handed its whole clock to BOTH halves (double
   * inheritance), then -- once chains were consumed on match -- to
   * whichever half groupsFor emitted first (iteration-order arbitrary).
   * Strict majority removes the boundary case at the root: neither half
   * of an even split is the chain's continuation, so both clocks restart.
   */
  evidenceFor(disjoint, shotSize, admissible) {
    const next = [];
    const pool = [...this.chains];
    for (const g of disjoint) {
      const ids = new Set(g.map((k) => k.id));
      let match = null;
      let mi = -1;
      for (let i = 0; i < pool.length; i += 1) {
        const c = pool[i];
        let shared = 0;
        for (const id of ids) if (c.ids.has(id)) shared += 1;
        if (shared * 2 > Math.max(ids.size, c.ids.size)
          && (!match || shared > match.shared)) { match = { c, shared }; mi = i; }
      }
      if (mi >= 0) pool.splice(mi, 1);
      const near = admissible(g);
      const rival = !near && g.length > shotSize;
      next.push({
        ids,
        members: g,
        nearTicks: near ? (match ? match.c.nearTicks : 0) + 1 : 0,
        farTicks: rival ? (match ? match.c.farTicks : 0) + 1 : 0,
      });
    }
    this.chains = next;
    return next;
  }

  /**
   * THE shed clock -- every judgement of a standing shot's un-fitness
   * goes through here (review 2026-08-21: the counter had grown scattered
   * write sites, and two zero-dwell bugs grew in the gaps between them).
   * `whole` is the membership-followed shot; `kept` is what a shed would
   * keep. The dwell banks ONLY when a shed would both CHANGE the shot and
   * RESTORE fit -- FR-010's licence to shed is restoring fit, so
   * whole-shot overflow (kept == whole) and a kept set that still
   * overflows (keptFits false) are overflow conditions for the
   * centre-hold (FR-007a), never shed evidence. Wholesale identity
   * resets (cold start, pan, follow change, empty roster, camera off)
   * stay at their own sites -- they replace the shot outright.
   */
  shedGate(whole, kept, keptFits, advanceEvidence) {
    if (setsEqual(kept, whole) || !keptFits) {
      if (advanceEvidence) this.unfitTicks = 0;
      return { ids: whole, shed: false };
    }
    if (advanceEvidence) this.unfitTicks += 1;
    if (this.unfitTicks >= this.dials.shedDwellTicks) {
      this.unfitTicks = 0;
      return { ids: kept, shed: true };
    }
    return { ids: whole, shed: false };
  }

  /**
   * The decision layer, in the contract's order (shot-grammar.md section 2):
   * follow pin -> membership follow -> shed -> break -> admission -> pan.
   * Runs once per world TICK (dwell is a tick count by definition), plus
   * on a follow change or a bounds change -- both discrete, neither a
   * pursuit. Evidence advances only on true tick edges.
   *
   * Membership changes here latch at most ONE episode; a joiner walking
   * into a shot group changes only the member set (FR-008) and the hold
   * picks the wider frame up when someone presses the edge.
   */
  decide(world, view, aspect, cssWidth, advanceEvidence, followChanged = false) {
    const d = this.dials;
    const kitties = world.kitties || [];
    const at = this.atOf(view);
    const { floorTiles, ceilingTiles } = this.limitsFor(world, cssWidth, aspect);

    // A follow on a kitty who is not here is dropped rather than
    // remembered -- one path serves a kitty leaving mid-session and a
    // restored id that names nobody (036 FR-020).
    let followed = null;
    if (this.followId !== null) {
      followed = kitties.find((k) => k.id === this.followId) || null;
      if (!followed) this.followId = null;
    }
    // `followChanged` arrives from update() -- the edge has ONE owner
    // (review 2026-08-21, finding 7): deriving it again here, after the
    // FR-020 ghost-drop above has mutated followId, read a tap on a
    // departed kitty as "no change" and skipped the bookkeeping a follow
    // change carries. The change resets the shed clock: whatever was
    // flapping under the old subject is not evidence against the new one.
    if (followChanged) this.unfitTicks = 0;
    this.decidedFollowId = this.followId;

    if (!kitties.length) {
      this.shotIds = null;
      this.chains = [];
      this.unfitTicks = 0;
      return;
    }

    const groups = this.groupsFor(kitties, at);
    const catsOf = (ids) => kitties.filter((k) => ids.has(k.id));
    const idsOf = (cats) => new Set(cats.map((k) => k.id));
    const fits = (cats) => this.fitWidthFor(cats, at, aspect) <= ceilingTiles + 1e-9;

    // Kitties can leave the roster; a shot never holds ghosts.
    let shot = this.shotIds
      ? new Set([...this.shotIds].filter((id) => kitties.some((k) => k.id === id)))
      : null;
    let kind = null; // the strongest episode this decision earns

    if (followed) {
      // 1. Follow pin (038 FR-014): her group is the subject,
      // unconditionally, even alone (min-two is a group-mode rule --
      // owner, 2026-08-21). Prior admitted company is kept while it still
      // fits alongside her group; far rivals are never evaluated.
      const hers = groups.find((g) => g.some((k) => k.id === followed.id));
      let cats = [...hers];
      if (shot) {
        const others = groups.filter((g) => g !== hers && g.some((k) => shot.has(k.id)));
        if (followChanged) {
          // A FRESH pin frames her NOW (owner ruling 2026-08-21): company
          // that no longer fits is dropped with the tap, never dwelled out.
          for (const g of others) {
            if (fits([...cats, ...g])) cats.push(...g);
          }
        } else {
          // An ONGOING follow sheds companions through the SAME gate as
          // group mode -- contract section 2: a follow skips step 6 ONLY.
          // One path whether companions exist, fit, or neither: with no
          // companions kept == whole trivially and the gate resets the
          // clock (finding 4 -- a frozen count from DEPARTED companions
          // armed a zero-dwell shed for the next arrivals), and a kept
          // set that cannot fit -- her own group past the ceiling --
          // licences nothing (finding 6).
          const union = [...cats, ...others.flat()];
          const kept = [...cats];
          for (const g of others) {
            if (fits([...kept, ...g])) kept.push(...g);
          }
          const verdict = this.shedGate(idsOf(union), idsOf(kept), fits(kept), advanceEvidence);
          if (verdict.shed) kind = 'shed';
          cats = catsOf(verdict.ids);
        }
      }
      const next = idsOf(cats);
      if (kind === 'shed' && setsEqual(next, shot)) kind = null;
      shot = next;
      if (followChanged) {
        // The pin itself latches ONE correction, replacing even a
        // committed pan -- the redirect the owner chose over the deferral
        // (ruling 2026-08-21; FR-013 protects against grammar dithering,
        // not against the person holding the phone).
        kind = 'correction';
      }
    } else {
      if (!shot || !shot.size) {
        // Cold start / re-engage: the best window, deterministically. With
        // a live frame already on screen (toggling ON mid-session) the
        // narrowing is one eased episode; with none (first paint) the
        // arrival block below places it before anything is drawn (SC-009).
        shot = idsOf(this.bestWindowFor(groups, at, aspect, ceilingTiles));
        kind = this.across ? 'break' : null;
        this.unfitTicks = 0;
      } else {
        // 2. Membership follow (FR-008): the shot is every group that still
        // holds a member. 3. Shed (FR-010) when they no longer fit together.
        const touching = groups.filter((g) => g.some((k) => shot.has(k.id)));
        const all = touching.flat();
        if (fits(all)) {
          shot = idsOf(all);
          if (advanceEvidence) this.unfitTicks = 0;
        } else {
          // The shed gate asks whether a shed would CHANGE anything and
          // RESTORE fit. A single group wider than the frame is an
          // OVERFLOW shot, not a shed -- bestWindowFor admits its seed
          // whole, so `kept` only differs when a whole group could
          // actually be dropped -- and overflow ticks bank NO dwell
          // (review 2026-08-21, finding 2): the old counter saturated
          // through an overflow spell, and a later one-tick un-link shed
          // with zero dwell -- the exact flap shedDwellTicks exists to
          // kill. Most boundary flaps re-fit within a tick or two and no
          // one ever moves.
          const kept = idsOf(this.bestWindowFor(touching, at, aspect, ceilingTiles, shot));
          const verdict = this.shedGate(idsOf(all), kept, fits(catsOf(kept)), advanceEvidence);
          if (verdict.shed) kind = 'shed';
          shot = verdict.ids;
        }
        if (shot.size < 2) kind = 'break';
      }
      // 4. Break / minimum-two (FR-004/FR-011), on EVERY group-mode path --
      // cold start included, which is where the first cut of this missed
      // it (caught by 'the ceiling binds, and the wanderer is let go'):
      // below two, re-pick outright; when even the best window is a
      // singleton, the closest PAIR at the widest -- partial visibility
      // beats a portrait.
      if (shot.size < 2) {
        let next = idsOf(this.bestWindowFor(groups, at, aspect, ceilingTiles, shot));
        if (next.size < 2 && kitties.length >= 2) {
          let pair = null;
          let bestD = Infinity;
          for (const a of kitties) {
            for (const b of kitties) {
              if (a.id < b.id) {
                const pa = at(a);
                const pb = at(b);
                const dd = Math.hypot(pa.x - pb.x, pa.y - pb.y);
                if (dd < bestD) { bestD = dd; pair = [a, b]; }
              }
            }
          }
          next = idsOf(pair);
        }
        shot = next;
      }
    }

    // 5. Admission and 6. pan, on tick edges only -- dwell is a count of
    // TICKS, and these are the grammar's only two threshold reads (the
    // spec-032 seam; research D10).
    if (advanceEvidence) {
      const disjoint = groups.filter((g) => !g.some((k) => shot.has(k.id)));
      const admissible = (g) => fits([...g, ...catsOf(shot)]);
      const chains = this.evidenceFor(disjoint, shot.size, admissible);
      for (const c of chains) {
        if (c.nearTicks >= d.nearDwellTicks && admissible(c.members)) {
          // Widen to admit -- never switch to -- a group that can share
          // the frame (FR-009). The owner's convergence call, made
          // geometry.
          for (const id of c.ids) shot.add(id);
          this.chains = this.chains.filter((o) => o !== c);
          if (!kind) kind = 'widen';
        } else if (!followed && c.farTicks >= d.farDwellTicks && c.members.length > shot.size) {
          // The only true transition (FR-012/FR-013): strictly bigger,
          // unreachable by widening, sustained. Equal never dethrones.
          shot = new Set(c.ids);
          kind = 'pan';
          this.chains = [];
          this.unfitTicks = 0;
          break;
        }
      }
    }

    this.shotIds = shot;
    if (!shot.size) return;

    const goal = this.goalFrameFor(catsOf(shot), at, aspect, floorTiles, ceilingTiles);
    // A shed or break re-centres at HELD width; the standing breathe-in
    // owns the zoom, later and slowly (owner, 2026-08-21 live judging:
    // membership re-frames were the "substantial moves" -- median 4.8
    // tiles of travel WITH 3.3 tiles of zoom in one motion. Decomposed,
    // the same event is a modest pan, a beat of rest, then a calm
    // tighten). Widens keep their width change -- admitting IS widening
    // -- and so does a re-frame whose CURRENT width sits outside the 037
    // band: toggling the camera on from the whole-world view has no
    // established framing to preserve, and holds its one-ease narrowing
    // (036 continuity, 'toggling ON narrows in one eased episode').
    if ((kind === 'shed' || kind === 'break')
      && this.across && this.across <= ceilingTiles + 1e-9) {
      goal.across = Math.max(goal.across, Math.min(this.across, ceilingTiles));
    }
    if (kind === 'pan') {
      this.startEpisode('pan', goal);
    } else if (kind) {
      this.startEpisode(kind, goal);
    } else if (this.lastBounds && (this.lastBounds.cssWidth !== cssWidth
      || this.lastBounds.aspect !== aspect)
      && Math.abs(goal.across - this.across) > 1e-6) {
      // A resize is a discrete retarget: one eased episode to the new
      // band, never a cut (036 FR-008) and never a pursuit. Tick edges
      // leave the width to the hold, or the frame would breathe with the
      // group's span every tick.
      this.startEpisode('correction', goal);
    }
  }

  /**
   * Has the shot pressed out of the frame's comfort? Two regimes:
   *
   *   fitting shot -- any member outside the inner safe-zone rect
   *     (038 FR-006/FR-007);
   *   OVERFLOW shot (fit > ceiling, common on the phone) -- the box
   *     CENTRE drifting past the deadzone. Members half-out of frame
   *     trigger NOTHING: the camera never chases edge kitties
   *     (038 FR-007a, owner 2026-08-21).
   */
  holdViolated(frame, cats, at, aspect, world, ceilingTiles) {
    const b = this.bboxOf(cats, at);
    if (this.fitWidthOf(b, aspect) > ceilingTiles + 1e-9) {
      return Math.hypot(b.cx - frame.aimX, b.cy - frame.aimY)
        > this.dials.aimDeadzoneTiles;
    }
    const down = frame.across * (aspect || 1);
    const left = clampFrame(frame.aimX - frame.across / 2, world.width, frame.across);
    const top = clampFrame(frame.aimY - down / 2, world.height, down);
    const mx = (frame.across * (1 - this.dials.safeZoneFrac)) / 2;
    const my = (down * (1 - this.dials.safeZoneFrac)) / 2;
    return cats.some((k) => {
      const p = at(k);
      return p.x < left + mx || p.x > left + frame.across - mx
        || p.y < top + my || p.y > top + down - my;
    });
  }

  /**
   * Latch a goal and ease to it. The episode is the ONLY thing that moves
   * the camera: it eases over a fixed duration, snaps EXACTLY on arrival,
   * and rests. Reduced motion arrives now instead (FR-016).
   */
  startEpisode(kind, goal) {
    if (this.reduced || !this.across) {
      this.across = goal.across;
      this.aimX = goal.aimX;
      this.aimY = goal.aimY;
      this.episode = null;
      return;
    }
    this.episode = {
      kind,
      from: { aimX: this.aimX, aimY: this.aimY, across: this.across },
      goal,
      // The velocity this move INHERITS (per-ms, zeros from rest). A
      // re-latch mid-flight hands its momentum to the next curve, so
      // motion between two rest states never passes through a stop while
      // its cause persists -- the owner's "fits and starts", resolved
      // structurally (2026-08-21).
      v0: this.episodeVelocity(),
      elapsed: 0,
      duration: kind === 'pan' ? this.dials.panMs : this.dials.moveMs,
      committed: kind === 'pan',
    };
  }

  /** The running episode's current per-ms velocity, or zeros at rest. */
  episodeVelocity() {
    const ep = this.episode;
    if (!ep) return { ax: 0, ay: 0, ac: 0 };
    const lead = ep.duration * Camera.AIM_LEAD;
    const tA = Math.min(1, ep.elapsed / lead);
    const tW = Math.min(1, ep.elapsed / ep.duration);
    return {
      ax: hermiteVel(ep.from.aimX, ep.goal.aimX, ep.v0.ax * lead, tA) / lead,
      ay: hermiteVel(ep.from.aimY, ep.goal.aimY, ep.v0.ay * lead, tA) / lead,
      ac: hermiteVel(ep.from.across, ep.goal.across, ep.v0.ac * ep.duration, tW) / ep.duration,
    };
  }

  /**
   * The gap since the last timed frame, clamped -- pure, so the clamp can
   * be tested without driving a whole frame.
   *
   * `viewAt` publishes `ambient: still ? null : { now }`, so a STILL frame
   * carries no clock at all. Reading that as 0 and storing it wiped
   * `lastAt` with the very value that means "never ran", and every palette
   * step, tab return and reduced-motion frame is a still frame. It also
   * put the `maxFrameMs` clamp out of reach of the case it exists for: a
   * returning tab calls `redraw()` (still) before `startLoop()`, so the
   * vast gap was swallowed by a clockless frame before any easing saw it.
   */
  dtFor(view) {
    const now = view?.ambient?.now;
    if (typeof now !== 'number' || this.lastAt === null) return 0;
    return Math.min(now - this.lastAt, this.dials.maxFrameMs);
  }

  /**
   * Advance one frame. Decisions run on discrete edges (a new tick, a
   * follow change, a resize, or never-yet-decided); motion is the current
   * episode easing toward its latched goal; REST is bit-stillness.
   */
  update(world, view, opts = {}) {
    const aspect = opts.aspect || 1; // cssHeight / cssWidth
    const cssWidth = opts.cssWidth;
    const now = view?.ambient?.now;
    const dt = this.dtFor(view);
    // A frame with no clock leaves the clock alone. See `dtFor`.
    if (typeof now === 'number') this.lastAt = now;

    if (!this.on) {
      // Off IS the whole-world view, not an approach to it -- a deliberate
      // cut, and the only one: the ground bakes at the whole-world tile,
      // so a frame mid-zoom would magnify it. The shot does not survive
      // the toggle (a fresh ON re-picks); the follow does (036 FR-027).
      this.across = world.width;
      this.aimX = world.width / 2;
      this.aimY = world.height / 2;
      this.shotIds = null;
      this.hasDecided = false;
      this.chains = [];
      this.unfitTicks = 0;
      // Pre-satisfied, not zeroed: the press dwell debounces the GRAMMAR's
      // transient presses, and the first press after an off->on toggle is
      // the VIEWER's own doing -- the re-pick's tighten should start easing
      // on the first frame, not wait out a patience meant for noise (owner,
      // 2026-08-22: "a couple second delay before the camera zooms back
      // in"; same principle as the follow-tap redirect ruling).
      this.pressTicks = this.dials.pressDwellTicks || 0;
      this.episode = null;
      const downOff = this.across * aspect;
      this.left = clampFrame(this.aimX - this.across / 2, world.width, this.across);
      this.top = clampFrame(this.aimY - downOff / 2, world.height, downOff);
      return;
    }

    // -- Decide, on edges only ------------------------------------------
    const tickEdge = !this.hasDecided
      || (world && world.tick !== undefined && world.tick !== this.lastTick);
    const followEdge = this.followId !== this.decidedFollowId;
    const boundsEdge = this.lastBounds !== null
      && (this.lastBounds.cssWidth !== cssWidth || this.lastBounds.aspect !== aspect);
    const mustDecide = tickEdge || followEdge || boundsEdge || !this.shotIds;
    // A committed pan finishes before the grammar looks again (FR-013) --
    // unless the VIEWER intervened: a follow change redirects immediately
    // (owner ruling 2026-08-21; commitment protects against grammar
    // dithering, not against the person holding the phone).
    //
    // And NEVER from a still frame (review 2026-08-21, finding 2): taps
    // and toggles arrive via redraw(), whose view carries SERVED
    // positions, so a decision there latches a shot and goal the drawn
    // cats have not reached -- the hold's guard, applied to the decision
    // layer it was protecting. Deferring one frame hands the decision to
    // the rAF loop and the drawn world. Two exemptions, both places where
    // served IS what the frame draws: reduced motion (still frames are
    // its only frames) and the never-decided first paint (SC-009 -- the
    // restored view must be in place before anything is drawn).
    const liveDecision = !(view && view.still) || this.reduced || !this.hasDecided;
    if (mustDecide && liveDecision
      && (followEdge || !(this.episode && this.episode.committed))) {
      this.decide(world, view, aspect, cssWidth, tickEdge, followEdge);
      this.hasDecided = true;
      this.lastTick = world ? world.tick : undefined;
      this.lastBounds = { cssWidth, aspect };
    }

    const at = this.atOf(view);
    const { floorTiles, ceilingTiles } = this.limitsFor(world, cssWidth, aspect);
    const shotCats = this.shotIds && this.shotIds.size
      ? (world.kitties || []).filter((k) => this.shotIds.has(k.id))
      : [];

    if (!this.across && shotCats.length) {
      // First frame: the restored view is in place before the first paint
      // (SC-009) -- arrive, never travel from a default.
      const goal = this.goalFrameFor(shotCats, at, aspect, floorTiles, ceilingTiles);
      this.across = goal.across;
      this.aimX = goal.aimX;
      this.aimY = goal.aimY;
      this.episode = null;
    } else if (!shotCats.length && !this.across) {
      this.across = world.width;
      this.aimX = world.width / 2;
      this.aimY = world.height / 2;
    } else if (!shotCats.length) {
      // The roster emptied under an established frame (a reseed between
      // generations). The old model's fit answered "the whole world" and
      // the frame eased out; the shot picker has no shot to frame, so it
      // must say so itself or the viewer stares at a frozen close-up of
      // empty grass. One episode, guarded against re-latching -- and it
      // outranks even a committed pan, whose destination no longer exists.
      const whole = { aimX: world.width / 2, aimY: world.height / 2, across: world.width };
      const there = Math.abs(this.across - whole.across) < 1e-6
        && Math.abs(this.aimX - whole.aimX) < 1e-6
        && Math.abs(this.aimY - whole.aimY) < 1e-6;
      const heading = this.episode
        && this.episode.goal.across === whole.across
        && this.episode.goal.aimX === whole.aimX
        && this.episode.goal.aimY === whole.aimY;
      if (!there && !heading) this.startEpisode('correction', whole);
    }

    // Reduced motion flipped MID-EPISODE arrives now (review 2026-08-21,
    // finding 3): every reduced frame is still (dt 0), so an in-flight
    // episode would otherwise never advance again -- the camera frozen
    // mid-ease while the cats walk out of frame. Same rule startEpisode
    // applies at latch time, applied to the episode the flip caught.
    if (this.reduced && this.episode) {
      this.across = this.episode.goal.across;
      this.aimX = this.episode.goal.aimX;
      this.aimY = this.episode.goal.aimY;
      this.episode = null;
    }

    // -- The hold -------------------------------------------------------
    // At REST, a violation of the CURRENT frame starts one correction; mid
    // NON-PAN episode, a violation of the LATCHED GOAL re-latches a
    // velocity-carrying episode from the current state whenever the goal
    // has actually moved (research D9, re-amended 2026-08-21 twice) --
    // evaluated against the goal, not the moving frame. A pan is
    // committed and looks at nothing.
    //
    // NEVER on a still frame: `viewAt(now, true)` publishes SERVED
    // positions (posFor is `kitty.pos`), up to a tile ahead of the drawn
    // cats, so a palette blend or tab-return redraw would latch a goal the
    // viewer's cats have not reached -- camera motion off a non-motion
    // event. Reduced motion is exempt on the same reasoning inverted: its
    // still frames are its ONLY frames, and for it drawn IS served.
    if (shotCats.length && (!(view && view.still) || this.reduced)) {
      const probe = this.episode && !this.episode.committed
        ? this.episode.goal
        : !this.episode
          ? { aimX: this.aimX, aimY: this.aimY, across: this.across }
          : null;
      if (probe) {
        // One position sweep each for the goal and the violation -- and
        // each of those now sweeps ONCE internally (fitWidthOf reuses the
        // caller's bbox), so a rest frame costs two sweeps total. The
        // first cut ran ~6 (high review 2026-08-21, below-cap).
        const goal = this.goalFrameFor(shotCats, at, aspect, floorTiles, ceilingTiles);
        const violated = this.holdViolated(probe, shotCats, at, aspect, world, ceilingTiles);
        // The breathe-in fires from REST only: mid-episode, slack alone
        // never re-latches. Without this gate the held-width shed above
        // collapses back into pan+zoom-together ONE FRAME after it
        // latches -- the hold would immediately re-latch the tight goal
        // (found by measurement: the first cut of the decomposition
        // changed nothing at all).
        const slack = violated || this.episode ? 0 : probe.across / Math.max(1e-6, goal.across);
        const pressed = violated || slack > this.dials.tightenFrac;
        // The press dwell: count persistence on tick edges; from REST the
        // trigger waits it out, mid-episode it does not.
        // The FRAME EDGE bypasses patience: the safe zone is a polite
        // buffer, but a member actually leaving the frame is SC-002's
        // contract -- measured: without the bypass, a 3-tick dwell let a
        // walking group exit entirely for 9 frames.
        if (tickEdge) this.pressTicks = pressed ? this.pressTicks + 1 : 0;
        const down = probe.across * (aspect || 1);
        const pLeft = clampFrame(probe.aimX - probe.across / 2, world.width, probe.across);
        const pTop = clampFrame(probe.aimY - down / 2, world.height, down);
        const outOf = (k) => {
          const pt = at(k);
          return pt.x < pLeft || pt.x > pLeft + probe.across
            || pt.y < pTop || pt.y > pTop + down;
        };
        const escaping = (violated && shotCats.some(outOf))
          // An EMPTY frame waives all patience regardless of the trigger:
          // SC-002 outranks calm, and an overflow pair drifting centred
          // can carry both members out before the deadzone trips.
          || shotCats.every(outOf);
        const patient = escaping || this.episode !== null
          || this.pressTicks >= (this.dials.pressDwellTicks || 0);
        if (pressed && patient) {
          // Move only when moving HELPS. Near the world's edge the clamp
          // can leave a member outside ANY legal frame's safe zone -- a
          // kitty sleeping against the fence -- and for her the fresh
          // goal is IDENTICAL, so it must trigger nothing or the hold
          // restarts the same episode forever. When the goal HAS moved, a
          // re-latch is free at any cadence: the new episode inherits the
          // old one's position AND velocity (Hermite), so a walker is one
          // continuous tracked move -- no zero-slope crawl (the restart
          // bug), no single-frame warp (the goal-mutation bug), and no
          // surge-stop rhythm at episode seams (the owner's ruling,
          // 2026-08-21) -- and a fidgeting shot still ARRIVES, because an
          // un-violated goal never re-latches and the last episode runs
          // out its clock and snaps.
          const same = Math.abs(goal.aimX - probe.aimX) < 1e-6
            && Math.abs(goal.aimY - probe.aimY) < 1e-6
            && Math.abs(goal.across - probe.across) < 1e-6;
          if (!same) {
            this.startEpisode(this.episode ? this.episode.kind : 'correction', goal);
          }
        }
      }
    }

    // -- The motion -----------------------------------------------------
    if (this.episode && dt > 0) {
      const ep = this.episode;
      ep.elapsed += dt;
      const t = Math.min(1, ep.elapsed / ep.duration);
      if (t >= 1) {
        // EXACT arrival, then rest. No easing residue, no epsilon drift --
        // the measured cause of "too active" was pursuit that never
        // arrives, and this is its structural remover (038 FR-006).
        this.across = ep.goal.across;
        this.aimX = ep.goal.aimX;
        this.aimY = ep.goal.aimY;
        this.episode = null;
      } else {
        // The aim settles slightly faster than the width (036 FR-009,
        // kept through the episode model): it finishes its travel at
        // AIM_LEAD of the duration. Each channel rides a Hermite that
        // starts at the INHERITED velocity and lands at rest.
        const lead = ep.duration * Camera.AIM_LEAD;
        const tA = Math.min(1, ep.elapsed / lead);
        this.aimX = hermite(ep.from.aimX, ep.goal.aimX, ep.v0.ax * lead, tA);
        this.aimY = hermite(ep.from.aimY, ep.goal.aimY, ep.v0.ay * lead, tA);
        // Carried momentum can OVERSHOOT the width a hair past the 037
        // band, and the band is a hard invariant -- but a transit that
        // legitimately STARTS outside it (toggling on from the
        // whole-world 20 tiles) must pass through smoothly, so the clip
        // widens to admit the start point. Aim overshoot stays unclipped:
        // a slight swing-through reads as momentum, and clampFrame keeps
        // the frame inside the world regardless.
        this.across = Math.min(
          Math.max(hermite(ep.from.across, ep.goal.across, ep.v0.ac * ep.duration, t),
            Math.min(floorTiles, ep.from.across)),
          Math.max(ceilingTiles, ep.from.across),
        );
      }
    }
    // A still frame (dt 0) is the same moment drawn again: the episode
    // neither advances nor snaps, and REST frames touch nothing at all --
    // `left`/`top` below recompute to identical values from identical
    // inputs, which is what bit-stillness means.

    const down = this.across * aspect;
    this.left = clampFrame(this.aimX - this.across / 2, world.width, this.across);
    this.top = clampFrame(this.aimY - down / 2, world.height, down);
  }
}

/** The aim's head start inside an episode: it finishes at this fraction of
 *  the duration, so the zoom lags the pan slightly (036 FR-009). */
Camera.AIM_LEAD = 0.85;

/**
 * Cubic Hermite on [0,1] with an INITIAL tangent and a rest landing --
 * the curve that lets an episode inherit the previous episode's momentum
 * (owner, 2026-08-21: chained rest-to-rest S-curves read as fits and
 * starts on a walker). m0 is the start tangent in unit time (per-ms
 * velocity x the channel's own duration); the end tangent is always 0,
 * so every episode still lands at rest and snaps exactly. With m0 = 0
 * this is a plain smoothstep -- a fresh move from rest is unchanged in
 * character.
 */
const hermite = (p0, p1, m0, t) => p0 * (2 * t ** 3 - 3 * t * t + 1)
  + m0 * (t ** 3 - 2 * t * t + t) + p1 * (-2 * t ** 3 + 3 * t * t);

/** Its velocity, in the same unit time (divide by the duration for per-ms). */
const hermiteVel = (p0, p1, m0, t) => p0 * (6 * t * t - 6 * t)
  + m0 * (3 * t * t - 4 * t + 1) + p1 * (6 * t - 6 * t * t);

/** Two id-sets with the same members. */
const setsEqual = (a, b) => a.size === b.size && [...a].every((id) => b.has(id));

/**
 * The browser side: one rAF loop, stopped whenever it has no business
 * running (hidden page, reduced motion). Everything here is wiring; the
 * decisions above stay pure.
 */
const anim = {
  presentation: new Presentation(),
  pacer: new Pacer(),
  camera: new Camera(),
  renderer: null,
  rafId: 0,
  reduced: false,
  // The delay line, on by default. Off means states draw as they land, at
  // the served tick -- which is what a world running far faster than it
  // will in production wants: at a tick shorter than a frame there is no
  // pace that helps, since two states cannot both be drawn in one frame,
  // and the buffer's tick of latency is pure lag on top. See `setPaced`.
  paced: true,

  init(renderer) {
    this.renderer = renderer;
    // Handed over rather than reached for: the renderer drives the camera
    // from inside `draw`, so both the rAF loop and the still redraw
    // advance it without either knowing the other exists.
    renderer.camera = this.camera;

    const media = window.matchMedia('(prefers-reduced-motion: reduce)');
    const applyMotionPreference = () => {
      this.reduced = media.matches;
      // The camera needs this in its own right: a still frame means
      // "arrive" to a reduced-motion viewer and "the same moment again"
      // to everyone else, and it cannot tell them apart from the view.
      this.camera.reduced = this.reduced;
      // The panel's CSS transitions go still with the canvas (FR-015).
      document.body.classList.toggle('reduced-motion', this.reduced);
      if (this.reduced) this.stopLoop();
      this.redraw();
      if (!this.reduced) this.startLoop();
    };
    media.addEventListener('change', applyMotionPreference);
    this.reduced = media.matches;
    this.camera.reduced = this.reduced;
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

  /**
   * A served world arrived (first snapshot or WS frame). It goes into the
   * delay line rather than straight to the store -- see `Pacer`.
   *
   * Two paths skip the pacing, for the same reason: there is no
   * interpolation to protect. Reduced motion draws each state held and
   * still, and the very first state has no predecessor to ease from. A
   * hidden tab does neither: it just banks arrivals, and the backlog
   * collapses on the first frame after the tab is looked at again.
   */
  push(world) {
    this.pacer.enqueue(world);
    if (!this.paced || this.reduced || !this.presentation.curr) {
      const now = performance.now();
      for (const queued of this.pacer.drain()) this.promote(queued, now);
      if (this.reduced) this.redraw();
      else if (!document.hidden) this.startLoop();
      return;
    }
    if (document.hidden) return;
    this.startLoop();
  },

  /**
   * The delay line pays out, once per frame: a state becomes current at a
   * paced moment rather than the moment it landed. Kept off the rAF
   * callback so the harness can drive it on its own clock.
   */
  pump(now) {
    const { worlds, snap } = this.pacer.due(now);
    // Before the promotion, not after: `pushState` decides continuity as
    // it lands, so a collapsed backlog has to already be a new moment.
    if (snap) this.presentation.bumpGeneration();
    for (const world of worlds) this.promote(world, now);
  },

  /** A state stops waiting and becomes the world on screen. */
  promote(world, now) {
    this.presentation.pushState(world, now, this.pacer.playMs);
    // Everything outside the canvas that reads the world -- the cards, the
    // sky dial, the tick counter -- moves on THIS beat rather than on
    // arrival, so the panel can never lead the meadow by the delay line.
    if (this.onPromote) this.onPromote(world);
  },

  /** One static draw of the newest state (reduced motion, snaps, toggles). */
  redraw() {
    if (!this.presentation.curr || !this.renderer) return;
    const view = this.presentation.viewAt(performance.now(), true);
    this.renderer.draw(this.presentation.curr, view);
    // The still view is what makes this safe to share: `motionFor` returns
    // phase 0 and nothing else, so whatever paints here holds its pose.
    if (this.onFrame) this.onFrame(this.presentation.curr, view);
  },

  /**
   * Anything outside the canvas that has to move on the world's clock.
   *
   * The card portraits are the first: they are cats, so they blink and
   * twitch off the same `motionFor` the meadow uses. Handing them the
   * frame's own view rather than letting them run a second rAF loop is
   * what keeps the two honest -- one clock, and every rule the canvas
   * already obeys comes with it. A still frame passes a still view, so
   * reduced motion stops the portraits without app.js knowing the rule
   * exists (FR-015); a hidden tab stops the loop, so they stop too
   * (FR-016); and the pair can never drift, because there is no second
   * timer to drift from.
   */
  onFrame: null,

  /** A world became current. Set by app.js; see `promote`. */
  onPromote: null,

  startLoop() {
    if (this.rafId || this.reduced) return;
    const step = () => {
      this.rafId = 0;
      if (document.hidden || this.reduced) return;
      const p = this.presentation;
      this.pump(performance.now());
      if (p.curr) {
        const view = p.viewAt(performance.now(), false);
        this.renderer.draw(p.curr, view);
        if (this.onFrame) this.onFrame(p.curr, view);
      }
      this.rafId = requestAnimationFrame(step);
    };
    this.rafId = requestAnimationFrame(step);
  },

  stopLoop() {
    if (this.rafId) cancelAnimationFrame(this.rafId);
    this.rafId = 0;
  },

  /**
   * Turn the delay line off (or back on). A debug switch for driving a
   * world far faster than it will ever run in production -- flicking
   * through a day to judge the phase crossfades, say. Unpaced is exactly
   * the behaviour that shipped before the pacer: each state draws as it
   * lands, over the served tick.
   *
   * Whatever is already buffered goes out at once rather than being
   * stranded, so turning it off never loses a state.
   */
  setPaced(on) {
    this.paced = Boolean(on);
    if (this.paced) return;
    const now = performance.now();
    for (const world of this.pacer.drain()) this.promote(world, now);
  },

  setTickMs(ms) {
    if (Number.isFinite(ms) && ms >= 1) {
      this.presentation.tickMs = ms;
      // Reseed rather than let the pacer walk there: /config lands within
      // the first second, and a box on an 80ms tick would otherwise spend
      // its first dozen states collapsing a backlog it never really had.
      this.pacer.setTickMs(ms);
    }
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
