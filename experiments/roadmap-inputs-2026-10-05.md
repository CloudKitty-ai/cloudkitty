# Roadmap input set — owner confirmations, 2026-10-05

Addendum to `gen3-roadmap-inputs-2026-10-04.md`. Two forward
placements ruled in the Professor session 2026-10-05, relayed to
Experiments on her word, and confirmed by the owner IN THE
EXPERIMENTS SESSION 2026-10-05 ("Confirmed"). Both are placements
only: nothing in the 2026-10-04 ruled order moves, and nothing
starts now. Full design records live in the Professor lane
(`~/ai/professor/notes/rlhf-ideation-2026-10-05.md`,
`~/ai/professor/notes/self-other-weight-2026-10-05.md`).

## Her words

- In-session (Experiments, 2026-10-05): "Confirmed" — on both
  items as summarized below.
- Relayed via Professor (her words as relayed, on the RLHF slot):
  "I was thinking it's 1.2 after we have LLMs and the lab world
  (since activating food/water dispensers for others is an easy
  display of altruism)."

## 1) RLHF slotted at 1.2

After seated LLM (1.1) and the lab world — the slot is hers; the
reasoning below is the Professor's (read, concurred): the version
ladder becomes a progression of the LLM's role, 1.0 plumbing → 1.1
LLM as kitty → 1.2 LLM/human as judge, and the pump solves RLHF's
legibility prerequisite — a press is discrete, attributable,
costly in ticks, and recipient-identified: the right unit for
pairwise clip judgment (base-world kindness is too diffuse to rate
from short clips).

Design watch item, banked for when 1.2 firms: legible displays are
counterfeitable (performative pressing — trough full, recipient
not thirsty — because the rater sees the press, not the need). The
ground-truth leg (judged kindness vs delivered welfare per
recipient, scored on the welfare register) must be co-designed
with the preference arm from run one. Judge-tier ideas in the Professor
note: her solo labels / LLM judge against the written constitution
(RLAIF; 1.1 plumbing reused) / oracle-as-judge calibration from
the register (cheapest; the control arm).

## 2) Self-vs-other reward weighting — pilot in the followups window

Added to the Gen 3 followups window (slot 3 of the ruled order),
pilot only, own timebox. Her framing as relayed: team Nash is
essentially perfect selflessness; test whether some
self-prioritization yields broader group welfare.

Headline design pieces (full version in the Professor note):

- `R_i = w*h_i + (1-w)*G` swept over w.
- Two sharpenings: current kitties are impartial, not selfless (no
  indexical self-term); and Nash already floor-guards the
  worst-off via `dG/dh_i = G/(n*h_i)` — the question is what a
  self-term adds beyond that.
- Three separable mechanisms for why w>0 might help: credit
  assignment; own-state observability under hidden needs;
  equilibrium robustness.
- Discriminator arms: difference reward
  `D_i = G(all) - G(minus i's contribution)` to separate
  training-aid from better-objective; a w-taper arm (scaffold, per
  her leash-not-a-crutch stance).
- One trap: raw w is misleading because the Nash gradient carries
  1/n (at n=4 equal welfare, w=0.2 already weights self ~2x a
  friend) — pick the grid in effective-gradient-ratio space and
  report that ratio.
- All arms scored on the canonical register regardless of training
  objective; realized-distress stop rules apply.

The full version (heterogeneous-w populations × lab-world altruism
displays) stays in the lab-world slot; the pilot's dose-response
decides how much of that crossing is warranted.
