# Biscuit 3.0 design note (2026-08-26, Experiments + owner)

Owner's framing, banked here on her word. Fog is ignored for
simplicity throughout; everything below is expressible on the current
surface. Evidence chain: F-033 (the spare-cycles theory),
`need-latency-baseline-2026-08-26.md` (the gap is eat/drink/sleep;
play-while-hungry caught in the relief stamps), F-019 + D-001 (the
leash dose-response and its narrow band), F-030 (why not reward-side
shaping).

## The two vectors (owner's)

1. **More efficient play proposal** — stop burning turns on proposals
   that will be refused (the F-033 refusal half, 4.6% of ticks).
2. **Give up a small amount of play for more needs fulfillment while
   keeping the character** — Biscuit 2.0 plays a LOT; there is wiggle
   room before the personality is touched (the chosen half).

## Why the old narrow band should not transfer

The good-welfare + still-Biscuit band was narrow **along β** — a
global, state-blind dial that pays character everywhere to buy welfare
anywhere (D-001: erosion is indiscriminate, seed-varying, and can
relocate rather than fade). The proposed axis is different:
`[behavior] playful_comfort` (default 55, `playful.rs:64`) is
**already state-conditioned** — it removes play only in the high-need
band, and play at low needs (the bulk of the visible character) is
logically unreachable by the dial. β does not move: the leash stays at
the proven 0.04 knee, and the transmission fidelity that faithfully
taught play-while-hungry (eat excursions peak at 35–39, inside the
30–55 play-anyway band the anchor teaches) is what should faithfully
teach the fix.

## Levers, ranked

1. **Anchor-side comfort fix (vector 2, primary)**: lower
   `playful_comfort` in the demonstration config, regenerate
   demonstrations, clone + leash at β∞ 0.04 unchanged. Priced by the
   sweep below BEFORE any training compute. **Plus per-need comfort
   weights (owner 2026-08-29, rolled into the Playful 2.0 spec)**:
   the get-serious check weighs needs before comparing to comfort
   (default 1.0 each = today, inert). Rationale: Biscuit's gap is
   eat > drink > sleep (both banked windows), while every seat's
   bath routinely peaks 30–40 — a GLOBAL comfort of 30–35 buys
   food-attentiveness by also taxing play for slow low-stakes needs;
   weights target the food band and preserve more character.
2. **Anchor-side partner-value score — "Playful 2.0" (vector 1;
   SUPERSEDES the bare floor filter, owner 2026-08-28)**: both
   vectors ride the same fix-the-teacher mechanism. Design:
   - Per candidate friend:
     `value = play_need − w_busy·expected_wait − w_serious·partner_max_pressure`;
     `score = w_value·value − distance`. `expected_wait` ≈ scene
     min-duration − elapsed for a mid-scene partner (readable from
     `ActivityClock`), 0 if free. Critters enter the same ranking at
     a flat appeal constant (no needs), preserving the critter-first
     tie at defaults.
   - Gate: propose/chase the best friend only when own play need ≥
     `T_self` AND best value ≥ `T_partner`; otherwise critter/solo
     play, which stay UNCONDITIONAL — the thresholds gate who Biscuit
     bothers, never whether Biscuit plays (the character).
   - Why partner activity: the hard busy-filter already exists
     (spec 006, `selection.rs is_viable`); the score adds the two
     signals it throws away — soon-free partners (anticipatory
     approach; proposal still waits for free, no new refusal
     exposure) and about-to-get-serious partners. The residual
     refusal tax is the timing seam and stays (owner kept it).
   - Teachability: every input is observed by the clone — partner
     needs (`rl/src/observe.rs:299`), dx/dy/dist; scene age arrives
     with the step-3 bundle's float, and Biscuit 3.0 trains
     post-wall, so the term is learnable exactly when it matters.
   - All dials (`w_value`, `w_busy`, `w_serious`, `T_self`,
     `T_partner`, critter appeal) inert at 0.0 → byte-identical
     launch (house pattern). Engine work, spec-first; routed to
     Product 2026-08-28 as one spec with the comfort dial's sweep
     plumbing; rides OUTSIDE 041 and outside the wall (config-only).
   - Expect play to REDISTRIBUTE toward high-need partners at real
     weights: roster-wide play access should improve, per-pair
     contact shifts — the F-027 frozen-cluster check matters more,
     not less.
3. **State-conditioned leash β(s) (fallback)**: only if the anchor
   route under-delivers. Requires state-conditioned fingerprint gates
   (D-001's relocation lesson) before it can be certified honestly.
4. **NOT reward-side shaping**: a play-when-hungry penalty is
   per-event shaping of a social behavior — F-030's churn signature,
   which the leash demonstrably does not prevent.

## The comfort sweep (scripted, lab, no training)

**RUN 2026-09-01 — `biscuit3-comfort-sweep-2026-09-01/RESULTS.md`,
F-038.** Curve smooth, no free lunch; duets untouched, element play
pays; w35 (per-need weights) beats flat c35 on play kept for the same
food line; spec-042 candidate dials refuse nearly every friend (not
shippable, `t_partner` re-sweep owed). Decision rule → middle case,
owner's call on the curve. The "scripted floor 1–4" below was the live
800 ms server's; the lab floor is p50 7–25.


**⏳ SEQUENCING (owner, 2026-08-26): run the sweep once ALL pre-fog
engine changes are in** — after step 1 (cuddle sibling package) lands
and anything else in the step-3 bundle that touches the economy, so
the sweep prices the dial against the economy Biscuit 3.0 will
actually train under, not the one being retired.

- Arms: `playful_comfort` ∈ {55 (baseline), 45, 35, 30}, scripted
  Biscuit in the lab family, other seats per the then-current cert
  config. **Joint with Playful 2.0 (owner 2026-08-28): once the
  partner-value score lands (inert), the sweep also prices its dials
  — comfort × {score off, score at candidate weights} — so one lab
  campaign answers both levers.**
- Pre-declared readouts:
  - eat/drink/sleep armed-latency + time-above (need_latency.py; live
    baseline: eat p50 31 ticks, scripted floor 1–4);
  - hungry-play share (play services while a food need is armed —
    live baseline ~17%, 15/86, one window);
  - play mix + scene spans per F-031's span rules (comfort is a hard
    line mid-decision; span changes feed EV pricing elsewhere);
  - **roster-wide** play access and refusal rates — Biscuit is the
    roster's biggest play supply; do not fix one seat's demand by
    silently taxing four seats' supply;
  - welfare/happiness per seat.
- Decision rule: if the sweep closes most of the eat-latency gap at a
  comfort value whose low-need play share is unchanged, vector 2 is
  config + one lineage retrain; if the gain is a sliver, the gap is
  geometry/travel, not choice — redirect before spending training.

## Owner calls still open

- The comfort value itself (sweep informs, owner rules).
- The identity question: is playing-through-hunger part of
  Biscuit-ness? Lowering comfort redefines the certified character
  slightly; char price re-derives.
- Whether the proposal filter (lever 2) ships in the same generation
  or waits.
