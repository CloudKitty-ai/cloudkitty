# Pre-sitting confirms for agenda section B (2026-10-15)

Two of the freeze agenda's section-B items are confirmable against
landed text today; this note is the citation the sitting can lift.
Nothing here pins a blank — the sitting's word does.

## B: §4 cue-answer response shape — both named halves pinned at
## spec on Experiments' reading (recommend: confirm-and-cite)

The skeleton blank (L161-162): "[BLANK] response shape (drift rule,
answer threshold) at spec." Spec 059 landed at #447 with
`specs/059-teacher-rework/contracts/cue-answer.md`, which pins both —
on Experiments' reading of the blank's two names, since the contract
uses neither: "answer threshold" maps directly to the contract's
"Fire condition" (its guards call it "the threshold comparison");
"drift rule" Experiments reads as the contention/margin/expiry law:

- **Answer threshold** — the fire condition, deterministic: a call
  applies its valuation term iff it survives the feasibility filter
  and "intensity ≥ max(reply_intensity_floor, top_pressure(me) /
  100)" — the call must outrank the hearer's own loudest need; the
  existing `[behavior] reply_intensity_floor` (served 0.20) is the
  floor. No RNG.
- **Drift rule** — how an in-flight answer moves between callers and
  dies: the per-kind contention law (feasibility
  `d_i ≤ window_remaining_i − HANDSHAKE_TICKS`, score
  `intensity_i − k · d_i`, winner by score then intensity then
  nearer then lower id; calls never stack); a play answer's
  incumbent is displaced only past the commitment margin
  `h = k × response_commitment_ticks` (served ≈ 0.0857), a cuddle
  answer switches cleanly per fresh net-surplus winner with NO
  margin (the principled asymmetry, owner ruled B 2026-10-10); and
  the term "expires with digest visibility".

The contract's derived-constants table carries every number
(`I_min` 0.20, `HANDSHAKE_TICKS` 2, `D_w` 28, `k` ≈ 0.0286,
`h` ≈ 0.0857). Experiments' reading: nothing inside the blank's two
named items is left open; the sitting can confirm-and-cite the
contract. (The FR-036 cuddle-clause revisit riding with the rungs is
a separate clause of the same skeleton bullet, not part of this
blank.)

## B: §4 empty-bowl early end — LANDED BEFORE COLLECTION
## (recommend: strike)

The blank's second half (skeleton L212-215): "the empty-bowl early
end's spec-006 amendment (own spec, every cat — ruled IN S§6)
landing BEFORE collection." Confirmed: spec 060 ("060 empty-bowl",
`specs/060-empty-bowl/spec.md`) is its own spec, classed there as "a
spec-006 amendment, an engine scene rule" "affecting EVERY cat,
policy seats included" (its FR-001: "binds every seat identically"),
merged at #448 (048a83cb, 2026-10-12).
Gen 2 collection has not run (it waits on 061), so the
before-collection condition holds. The sitting can strike this half;
the first half of the same bullet (teacher dial ranges) stays an
open blank.
