# Spec 047: Partner Consent Line for Playful Targeting

One new `[behavior]` dial, `consent_line` (default 0.0 = OFF, byte
identity). The owner's rule, verbatim from the Biscuit 3.0 prereg
(Addendum 2): play can always be proposed if the friend's top need is
play; it cannot be proposed if a non-play need is the friend's top need
and that need is over the line. Strict `>` on both comparisons — ties
stay eligible.

## Scope (Clarifications 2026-09-01, Experiments-confirmed)

The gate covers **all three** playful friend-play start paths — the
brief's original single site would have made acceptance bar C2 a test of
the leak, not the rule:

1. **Partner ranking** (`scored_playmate`): blocked friend never becomes
   a candidate.
2. **Get-serious relief** (`choose_consenting` → the parameterized scan):
   the blocked friend is excluded from the scan itself, so score and walk
   agree (the 004 rule).
3. **Adjacent opportunism** (`take_what_is_here_consenting`): adjacency
   is not a bypass.

Playful-scoped by construction: needs_driven's entry points are untouched
code paths, pinned by doctrine guards on both the opportunism and
`choose()` halves. Critters, elements, solo play never gated (Article
III: a fully-blocked neighborhood degrades to friends-absent behavior,
asserted positively). Rejection stays engine law (Article IV — the gate
moves what the playful advisor proposes, never what is legal).

## Identity

No world-state change: **evolution golden pin and defaults stamp both
UNMOVED** (unlike 046 — nothing to regen). `skip_serializing_if` at 0.0
(039-D5 discipline); the short-circuit returns before reading a single
need. Proven movable: temporarily defaulting the dial to 30.0 reds the
stamp, the golden, and the 046 strip witness (redden cycle 7).

## Verification

13 red-first cycles in `specs/047-consent-line/redden-list.md`; suite
793 → 809/0; fmt + CI-exact clippy clean. Each gated site's guard was
written before its site was wired (the pre-implementation red IS the
site-removal proof Experiments asked for), and a removal audit re-reds
each site individually. One honestly-recorded prediction miss (cycle 6a:
site-1 removal also reds the end-to-end opportunism guard — depth, not
vacuity).

**New standard adopted** (medium review): mutation cycles run
`cargo test --workspace --no-fail-fast` — per-target fail-fast hid two
lib reds in cycle 7's original record (re-verified: all other cycles'
records were complete).

## Review (medium, 8 findings — all resolved)

- **#1 (accepted by the owner)**: blocking the only playmate re-prices
  play as solo (distance 0, the pre-existing absent-friend rule), which
  near the play/eat crossover can buy solo play a tick over a moderately
  higher need. Accepted 2026-09-01: the scripted cat is a training
  teacher; marginal detours wash out — the point is that consideration
  of other cats' needs is modeled so it is learnable. Pinned as intended
  (`blocking_the_only_playmate_may_buy_solo_play_a_tick_over_eating`);
  Experiments' R2 (hungry-play share, both arms) watches the aggregate.
- **#2 (fixed)**: the classic scan's consent flag was unguarded —
  `the_classic_scan_ignores_the_consent_line` now reds on exactly that
  mutation, workspace-wide.
- **#3 (fixed)**: cycle-7 record amended (5 reds, not 3); the 042/047
  boundary now has an explicit pin — at a live line the hard drop
  supersedes 042's penalize-not-drop on the no-veto pin's own staging.
- **#4 (fixed)**: `consent_line > 100` refused at load (needs cap at
  100; 100 itself legal but blocks nothing) — relevant to sweep arms.
- **#5 (cleared by Experiments)**: R7 reads census, not the refusal
  ring; R8 filters `absorbed == false`, excluding scene-continuation
  refusals by construction; chase-exclusion tails recorded as
  unattributed in C3/C4.
- **#6 (fixed)**: quickstart runs the FR-003 guard by name; live-smoke
  section rewritten (KittyConfig exposes rates, not starting levels).
- Low-review asymmetry note (accepted): site 1 gates unconditionally
  inside `scored_playmate` (playful-only by its contract) while sites
  2/3 plumb a flag; a future needs_driven caller of `scored_playmate`
  would gate silently.

## Downstream

Experiments rebuilds and runs the pinned four-run acceptance batch
(c30-off ×2, c30-consent30 ×2; bars C1–C5, readouts incl. R2/R7/R8) once
this is on main. Banked follow-up (note-only): extending consent to
needs_driven — two call-site flips on the existing variants, but a
doctrine inversion needing its own spec, sequenced after the acceptance
run.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_017Wov2on3vAYMEAYCCTWb9y
