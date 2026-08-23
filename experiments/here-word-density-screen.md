# Here-word density screen — the plan

**Authored 2026-08-23. NOT YET RUN. Sequencing undecided by the owner
(before or after the fog engine work) — §6 lays out the tradeoff
rather than settling it.**

The question: **how densely must scripted cats speak grounded Here\*
words for a cloned mind to pick the vocabulary up, and does speaking
them densely cost anything?**

## 1. Why this exists

Fog's registered comparison is whether grounded reference (`here_food`)
beats FollowMe-overloading once fog creates an information gradient.
That comparison presupposes a mind that *has* the vocabulary. F-022
says where vocabulary comes from, and it is not exploration:
demonstrations seed the channel. exp-003's near-empty channel (0.2% of
dataset decisions) never came alive — its clone predicted meows at
**0.0000** accuracy and 20M PPO ticks left it at 0.01–0.41 per 1k.
exp-004's purr-rich corpus cloned at 104.66/1k and certified near
170/1k. Same recipe family, same reward; the difference was what the
clone had seen.

So there is a density cliff, this project has fallen off it once, and
nobody has measured where it sits for the Here\* family. That is what
this screen buys — before the fog prereg commits to vocabulary arms it
cannot deliver.

**Rests on**: F-022 (demonstration seeds the channel — the primary
claim), F-026 (under global vision the channel is welfare-redundant —
why welfare here is report-only, §4), F-015 (pooled probes dilute under
heterogeneous class amplitudes — why every read-out is conditioned on
the here-kinds, §5), F-012 (channel use is context-dependent — measure
in company, never solo).

## 2. The mechanism under test

Scripted speech is a separate channel from scripted action. `NeedsDriven::decide`
and `Playful::decide` both call `decide_action()` for the activity and
the **shared** `announce()` for the word, which "rides along, never
displacing it" (spec 028). The action ladder reads exactly one message
kind — `WantBath`, for `groom_response` — so it is structurally blind
to Here\* words.

`announce()` today iterates only `MessageKind::for_need(need)`: the
want-family. Every other piece already exists — `message_legal`
implements the Here\* grounded predicates (spec 033: "the referent is
adjacent, or the word is not spoken"), each kind is config-gated, and
`emit_message` sets its cooldown arithmetically and **draws no RNG**.

**The change under test**: extend `announce()`'s candidate set to the
Here\* kinds, behind a new knob on the scripted behaviors (NOT
`meow.vocabulary.*`, which governs legality for policies too and is
already `true` for all four here-kinds on the served world — that is
how Kittybear speaks `here_water`).

**Selection among multiple legal here-words uses the stateless
derivation, never the master RNG**: `(tick + kitty_id) % n_legal`, the
same trick as `Element::critter_moves_this_tick`. A master-RNG draw
inside `announce` would shift the stream, change the next `wander`
`gen_bool(0.4)`, and diverge the action trajectory — destroying the
one property that makes this cheap. The same trick supplies the
density dial: speak when `(tick + kitty_id) % period == 0`.

Owner's rule for the precedence, settled 2026-08-23: **existing speech
wins**; a here-word is spoken only when no want-word is. That conflict
is rarer than it sounds — want-words arm at need ≥ 30 (hysteresis to
25) and live needs run 1–11, so the scripted corpus is ~95% `Silent`.

## 3. Gate zero: action-equivalence, before any arm runs

Run the all-scripted anchor with the knob off and on and assert the
**action stream is byte-identical** while the message stream differs.
House methodology (the 018–020 refactor arc's bit-identical practice).

This is a gate, not a prediction. If it fails, the screen stops: a
vocabulary change that moves actions re-bases the scripted anchor
(0.9077), thermostat parity (90.71), the character price, and spec
017's eval-suite baseline, and none of that is worth a screen.

## 4. What this screen can and cannot answer

**Can**: (a) learnability — does a clone take the words up, and at what
corpus share; (b) harm — does dense here-speech cost action fidelity,
welfare, or channel legibility.

**Cannot**: whether grounded reference is *worth* anything. F-026 says
the channel is welfare-redundant under global vision — "here food"
tells a cat nothing it can already see. **Welfare read-outs here are
REPORT-ONLY and a null is the expected result, not a failure.** Dialing
density against a welfare criterion pre-fog would tune toward zero for
the wrong reason.

## 5. Design

**Arms** — the density ladder, pre-registered:

| arm | `announce_here` period | intent |
|---|---|---|
| A0 | off | control; the current corpus |
| A1 | 1 (every legal tick) | aggressive ceiling |
| A2 | 4 | middle |
| A3 | 16 | sparse |

Realized here-word share of decisions is MEASURED per arm and reported
(the sticker sweep's practice — predict the dial, report the realised
value).

**Collection**: scripted compositions on the current certification
world, the anchor-playful pattern (both scripted behaviors share
`announce`, so one knob arms the whole corpus). Seeds from a fresh
SEED-BANDS row, claimed before collection.

**Training**: `train_clone6.py` verbatim — **EntityPolicyV4**, the
seated architecture (d_model 64, heads 4, layers 2, ffn 128; 78,434
params). No MLP port: V4 is already wired and validated, a pilot corpus
is a fraction of the 3.9M-row anchor (~200 s/epoch), and staying on V4
removes any does-this-transfer asterisk. `--limit-rollouts` and a lower
epoch cap are the speed dials if an arm drags.

**Read-outs**, all conditioned on the here-kinds per F-015:

1. **Opportunity-use** (the headline): of ticks where here-kind K was
   legal and no want-word was armed, the fraction where the clone
   emitted K. This is the learnability metric.
2. Clone emission rate per 1k vs its scripted source (the F-022
   comparison shape: 104.66/1k cloned from a rich corpus).
3. `act@1` and overall `msg@1`, plus `msg@1` restricted to here-kinds.
   **Aggregate `msg@1` is near-useless here** — the corpus is ~95%
   `Silent`, so a clone that never speaks scores 0.9995.
4. Welfare: team and per-seat, REPORT-ONLY (§4).

## 6. Sequencing — the open question (owner's call)

The screen splits into two halves with different dependencies:

- **Half A (learnability + harm)** needs no fog. Its result is an
  *input* to the fog prereg: if the vocabulary will not seed even from
  dense demonstrations, fog's registered comparison needs rethinking
  before the engine investment, not after.
- **Half B (does density change USE — whether the words earn their
  place)** needs fog by construction, per F-026.

**Running A first** de-risks the fog prereg's arms and is cheap. Its
cost: the corpus is collected on the pre-fog observation schema, so it
is re-collected after the schema-4 wall regardless — expected, and
small against the information.

**Running everything after** measures under the conditions that matter
and collects once, but serializes the whole vocabulary question behind
the engine work and forces the fog prereg to register arms without
knowing a workable density.

**Recommendation: A before, B after.** Not settled — owner's call.

**Hard dependency either way**: the screen cannot run until the
`announce_here` knob exists. That is a small spec-first engine change
(core-side, `announce()` plus a config field) and it is Product's lane.
Gate zero (§3) is its acceptance test.

## 7. Pre-registered predictions (committed before any arm runs)

1. Gate zero passes: actions byte-identical, messages differ.
2. Realized here-word share rises monotonically as the period falls.
3. Opportunity-use shows a **threshold**, not a gradient: near-zero
   learning below roughly 1% of decisions carrying here-words (F-022's
   cliff sat at 0.2%), rising steeply above it.
4. `act@1` is unchanged across arms within seed noise — the vocabulary
   does not cost action learning.
5. Welfare differences are null within the parity band (F-026).

Prediction 3 is the one worth being wrong about: a smooth gradient
would mean the exp-003 failure was about something other than density,
and that would change how fog seeds every word, not just these four.

## 8. What a result would change

A workable density becomes a **collection parameter** for the fog
corpus, and the parked Here\*-teacher item may collapse entirely — if
`needs_driven` can speak grounded words under a flag, the teacher might
just be the existing scripted behaviors with the knob armed, with no
new behavior, no new spec, and no servable-vs-contributor line to
police. Worth checking before fog scopes it as new work.
