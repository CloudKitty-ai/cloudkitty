# The waterline pairing rule — tabled, with its groundwork banked

**STATUS: TABLED by the owner 2026-08-24.** Nothing built, nothing
specced, no ruling on scope. Revisit **before finalizing what rolls in
ahead of the fog schema break** — that is the decision point this
document exists to serve, because half the cost of the rule depends on
whether it rides that wall or ships alone.

## The proposal, in the owner's framing

A **partnered-activity** rule, not a grooming or sleeping rule:

- two adjacent cats both on land — any paired activity may be legal
- two adjacent cats both on water — same
- one on land, one on water — **cannot pair**

Paired means the action names another kitty: duet, co-sleep, cuddle,
groom-a-friend. Element play and solo play are not pairings. Chase and
meow name no activity and are untouched (hearing stays global, which is
the same line fog keeps).

It surfaced from a client animation bug in grooming, and the owner's
position is that it stands on physical grounds independently. Product's
guard rail, which Experiments endorses: **do not change world physics to
fix a drawing.** The animation fix is separable and Client's either way.

## Engine cost: small (Product's assessment, 2026-08-24)

One legality funnel. `action::validate` (`action.rs:341`) routes every
partner activity through two three-line helpers —
`is_conscriptable_friend` (`world.rs:1168`) for cuddle and social play,
`is_available_friend` (`world.rs:1157`) for co-sleep and groom. A
waterline clause in those two covers all four activities.

Everything downstream inherits it: `legal_action_mask` does not
reimplement legality, it calls `action::validate` on a probe world
(`rl/src/mask.rs:61`), so mask, plugin wire and server follow from one
edit, and `mask_oracle.rs` asserts mask-equals-engine with no carve-outs.

Mid-activity separation is already handled: grooming's end rule
(`world.rs:476`) routes through `is_available_friend`, so a groom in
progress ends when the pair is split. It cannot arise for the others —
duets and cuddles lock both parties via `reciprocal_duet`, sleepers do
not move, water elements are permanent.

**The cost is Experiments', not Product's**: anchors re-derive (scripted
0.9077, parity 90.71, playful 79.31, character price 11.40) and the
battery re-runs on five seats.

## The observation gap, and why it argues for the fog wall

A cat sees whether **it** is in water (self-block flag, tile-derived,
schema 2) but not whether its neighbour is: `KITTY_SLOT`
(`observe.rs:86`) has no water bit. The rule is therefore enforceable
today but only marginally learnable — a policy would have to infer "the
cat I want to groom is standing on water" by cross-referencing the
partner slot's relative position against the water slots'. Representable;
a spatial coincidence across two slot groups is the kind of thing a small
net learns badly.

Fixing it is one float in `KITTY_SLOT`, which costs an observation-schema
bump: artifacts refuse, everything retrains. **Free if it rides the fog
wall** (ROADMAP: "Only the observation schema moves at the fog wall").
Expensive as a standalone — a full five-seat retrain to buy one feature.

Second coupling in the same direction: the rule's **severity** is a
function of dials the fog prereg already screens. 7-9 water elements on
20×20 is a small bite; Phase 2 contemplates decluttering toward sparsity
and a world-size × vision-radius screen. Pinning the rule's behaviour
before that screen picks a world means pinning it against a world that
will not exist.

## How often it would bind (measured, and read the corrections first)

Instrument: `attn-cert-2026-08-14/waterline_exposure.py`, raws under
`results-raw/waterline-exposure-*.json` with F-028 headers. Two windows
on the corrected reader, 364-376 ticks each:

| paired activity | pair-ticks | cross-waterline | scenes | cross |
|---|---|---|---|---|
| groom-other | 168 / 111 | 25.0% / 9.0% | 48 / 33 | 20.8% / 9.1% |
| co-sleep | 256 / 265 | 8.6% / 6.4% | 48 / 47 | 8.3% / 6.4% |
| duet | 58 / 38 | 6.9% / 0% | 18 / 15 | 11.1% / 0% |
| cuddle | 0 / 0 | — | 0 / 0 | — |

On-water share of cat-ticks 2.0% / 9.3%; cross-waterline adjacency 5.3%
/ 15.1% of adjacent pair-ticks.

**What holds**: grooming is the most exposed partnered activity in both
windows. Cuddle cannot bind at all — `Resting` never runs on this roster,
because the cuddle need is fully served by groom-other's `cuddle_relief`
8.0 and co-sleep's mutual 8.0 / drip 3.0 (Product's structural reason,
better than the "extinct on this roster" framing it replaced). Duets are
common but rarely cross the waterline: 4 cross pair-ticks in 96.

**What does not hold, and cost two retractions**: magnitude swings 3×
window to window, and *which cat pays* is not a property of a seat —
Clementine, then Pumpkin, then Miso and Biscuit across consecutive
windows. It is whoever is loitering near water. **No live window prices
this rule.** Only seeds × 20k will.

### Two reader bugs, recorded so the revisit does not repeat them

1. **Bucketing per-cat activity state while adjacent** drops duets
   entirely if the reader enumerates only the activities the proposal
   happens to name.
2. **Counting pair-ticks off `activity.state`** under-weights duets ~3×
   and grooming ~1.3× against co-sleep, because the state is a one-tick
   resolution flag for play (measured mean run 1.00 over 82 runs) while
   it persists for sleep (5.03) and groom (2.62). Read `last_action`,
   which spans the engagement and is also the semantically correct unit:
   the rule lives in helpers that `validate` consults per proposed
   action, so one action-tick is one unit of relief denied.

Both produced confident wrong statements before they were caught. See
also F-031 for the span-measurement rule.

## F-016: the rule does not oppose the loop, it feeds it

Product's initial argument was that the rule pushes against F-016 by
removing the in-place social escape. **That is backwards.** F-016's loop
is solo: wet fur raises Bath, and a `needs_driven` cat grooms itself
where it stands, which keeps it standing in the charge. `Groom{None}` is
untouched by a pairing rule.

And the direction is worse than neutral. `Groom{Some(friend)}`
(`action.rs:754-763`) lowers **the friend's** Bath and pays the groomer
in Cuddle — so the only non-solo route to a wet cat's Bath relief is a
dry friend grooming it, which the rule blocks. Remove it and the wet cat
falls back on the location-indifferent relief that keeps it in the water.

**Pre-registered prediction, before any probe runs: scripted
grooming-on-water share rises under the rule.** F-016's own scope line
generalises it — "expect it wherever a cost raises a need whose relief
activity is location-indifferent."

Note also where the cost actually lands, which is not where the proposal
aims it: the wet cat never controlled being groomed, since the groomer
initiates for its own Cuddle. What the rule removes is the **dry cat's
cuddle relief** — spec 021's withdrawn premise (busy neighbours *are*
lawful cuddle relief) pointed at directly.

## The probe, if she rules

Product's design, which Experiments endorses with additions: **re-derive
the scripted anchors under the rule.** `needs_driven` cats are not
learned, so this measures the rule's effect on the world with no training
run, and the anchors must be re-derived anyway if the rule ships.

Cuts to report:

- **per-need**, not aggregate happiness — the relief is two-sided and
  asymmetric (groomer paid in Cuddle, recipient in Bath)
- **per-seat** — exposure concentrates, and on a different seat each time
- **tick and scene both** — ticks are relief-time denied, scenes are
  pairings dissolved; they agree on rate and disagree on volume
- **on-water time split by activity**, never pooled — F-016's own
  registered implication ("it pools a channel the dial suppresses with
  one it amplifies")
- **`max_distress_age` and its tail**, not means — the failure this rule
  can create is a tail event (a cat in the lake with every friend on the
  bank) against a constitutional bound of 150

**Interpretation limit, load-bearing**: F-016 §3 found a scripted floor
and a learned policy moving *oppositely* on the grooming-on-water
channel. The probe answers what the rule costs the anchor. It does not
bound learners on the one channel this rule runs through.

## The confound to protect if it co-sequences with fog

`here_water` is one of the four grounded here-words, Kittybear speaks it
at 8.8% of its messages, and fog's registered comparison is whether
grounded reference beats FollowMe-overloading. The rule changes what that
word *means* socially — an invitation to a place becomes notice that
whoever goes there is unreachable. Land both in one generation and that
arm is uninterpretable.

Two cheap fixes, either works: separate them by a generation, or exclude
`here_water` from the fog vocabulary arms and register why.

Smaller, same family: the here-word density screen's gate zero asserts a
byte-identical action stream and its arms collect against the scripted
anchor, so the screen wants to run wholly before or wholly after the
rule, never across it.

## Open, none ruled

- **Scope of the contact line.** Settled as "all paired activities" in
  the owner's framing above; what remains is whether social play is worth
  including given that including it re-derives the character price
  (11.40) while measured duet exposure is 4 cross pair-ticks in 96. The
  most expensive arm to certify may be the one that changes least.
- **Is "in water" standing on a water tile?** Cheapest reading. Spec
  010's skirt-the-puddle rule already holds occupancy near 2-9%, so the
  crossing-a-puddle case is rarer than the standing-in-it case.
- **Does the partner in-water bit ride the fog wall, or does the rule
  ship without it?**
- **Ordering** — probe before or after the fog prereg design pass.
- **Sequencing against the distress-gated intervention** (BACKLOG P2).
  The rule creates a third category beside deadlock and untaken relief:
  relief that is lawful and exists but is unreachable from where the cat
  stands. Experiments' position is that the rule should not serve before
  that item is settled, and the probe's distress tail is what says
  whether the concern is real or theoretical.
