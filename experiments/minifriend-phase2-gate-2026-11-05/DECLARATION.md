# Gen 2 Phase 2 entry gate — the owner's one-tick counterfactual screen, run by replay (declaration 2026-11-05; on her words "Agreed" and "Let's do it")

The frozen prereg (`gen2-prereg-2026-10-17.md` §8 item 4, "PHASE-2 ENTRY
GATE [A2′ item 2]") requires, before Phase 2 enters, the owner's own
instrument of 2026-10-10: "for each kitty: For each mini model: simulate
the action predicted by the model being taken by the actual cat, measure
needs/happiness scores 2) after each kitty takes its actual actions,
compare the mini model-predicted values to the actuals". Its four pins
are frozen (A2′, Professor): (a) per ostrich stratum with a DIFFERENTIAL
fail — welfare-priced divergence lift in grave bins over benign bins
beyond the declared margin, the family's 1.5×; (b) currency UNCLAMPED;
(c) min-n 200 per stratum, FAIL-CLOSED, remedy = probe-generated
distress-adjacent coverage, never a waived stratum; (d) step 2 folds into
the ostrich metric, one instrument. k = 1 pinned in text; the screen
trips no welfare marker (sitting item 5: the harness computes the branch,
the state belongs to a seated kitty, the mini carries no self-state).

Her words, 2026-11-05, in order. After the walkthrough of the gate: "With
A we can also derive the welfare performance of the mini models without
having to run them though, correct?" (answered: A prices the heads'
errors in welfare currency per stratum at zero exposure; it does not
measure a policy's welfare). "Based on that, what is your
recommendation?" → the five steps (re-step check; if yes A as declared on
both heads; if no a declared substitute; fail-closed either way; the
Phase 2 declaration after the gate read) → "Agreed". On the re-step
check's result ("one replay per branch point is a lot, do we want to just
have product build feature instead?") → gate by replay now, the branch
API to Product in parallel → "Let's do it". The Product relay is msg
9b1d6d03, not a kickoff. Phase 2's acting ruling is on record the same
day ("I approve the need and action predictor heads as inputs to the
decision making head"; timeline block PHASE 2 RULINGS 2026-11-05); this
gate precedes the Phase 2 declaration, which is drafted after the read.

**Status: DECLARED 2026-11-05 (ec67845a); guards g1–g7 RED CONFIRMED (§7,
this commit); the reads run on her word after she sees this draft. Nothing
collects; no acting weight moves; nothing acts. No number from this arc
exists at this write beyond a one-world code-path smoke in the session
scratchpad (24 points, never cited).**

Welfare-cost line. Covered minds: none exposed. Every read walks recorded
worlds (the needy set's tuning half); the act read REPLAYS them on the
pinned binding (engine 5928b7ca) from seed and recorded actions and
branches one tick, then discards the branch. No covered network decides a
live tick: the kitties take their recorded actions; the heads and the
friend's own policy run as readers on recorded rows; the substituted act
is the gate's. Covered cat-ticks 0. k = 1. What it buys: the welfare
price of each head's errors, by the friend's true state, before nine
covered PPO seeds train on those heads' outputs — and, read side by side,
the open-loop half of her B10-vs-B15 question.

## 1. What is being asked

Do the two heads Phase 2 will feed the policy — the needs head
NF1e-h24+p (F-072, F-073) and the act head B15 (her pick, ladder
DECLARATION §8) — carry the ostrich shape: predictions systematically
rosier than reality exactly when the friend is grave? The gate answers
PASS / FAIL / INSUFFICIENT per head, fail-closed, by the frozen pins; B10
is read beside B15 as the Phase 2 comparator; the frequency predictor F
is a reference, never gated.

## 2. Facts the design rests on (all on record)

- The ostrich signature fired on every needs head at every width in
  Phase 1b (R4b: NF-h24 mind-visible grave bias −10.10 need points,
  common within 0.5 of zero, four of five friends). NF1e was retrained
  with late graves (F-072) and has never had the ostrich metric read on
  it; the frozen prereg (S§3d) reads the metric "on BOTH estimates, per
  phase". The act head has only been read by regime (seen / heard /
  silent), never by the friend's welfare state.
- RE-STEP CHECK DONE 2026-11-05 (timeline): a recorded needy-set world
  replays exactly from (config, seed, recorded covered-seat `act` /
  `msg`) — three worlds, worst difference 0 on needs, happiness and the
  observation rows, about 20,000 ticks/s; a covered seat's act
  substitutes at any tick through `step`; the scripted seat cannot be
  substituted (engine-decided), which costs nothing here (every head
  read is on covered friends). The one-tick price is SPARSE: move → rest
  moved nothing in one tick; play → move moved the friend's need and
  happiness.
- The act head's target classes (F-074): the eleven applied kinds; the
  live classes are move, rest, sleep, groom, eat, drink, chase, play,
  idle — purr and meow have zero training frequency and are never
  predicted.
- Strata (Phase 1's `strata.py`, prereg S§3d riders): GRAVE = any hidden
  need ≥ 90 or happiness < 45; ADJACENT = not grave, happiness < 70;
  COMMON = the rest; on the friend's TRUE state entering the tick
  (needs[t − 1]); bath (need 5) never enters a bin.

## 3. Data

The needy set's TUNING half (`needy-set-2026-10-28/split.json`, the act
and ladder arcs' primary surface; `read_act.needy_worlds("tuning")`),
covered observers and covered friends only. The CONFIRMING half is not
touched (five touches on record; none here). Nothing new is collected.

## 4. The reads (`gate_screen.py`; every module imported, none copied)

- **R-0 `sample`** — branch points. Candidates = every (observer k,
  friend j, tick t ≥ 1) with k and j covered seats, j ≠ k, binned by j's
  stratum at t (the needy loader's codes) and by version: `visible` (k's
  row for j is present at t) and `all`. Per stratum × version, 300 points
  drawn without replacement with seed 20261105. Coverage per cell
  reported; a cell under 200 candidates is INSUFFICIENT (pin c).
- **R-1 `act`** — the act branches. For every sampled point and each
  predictor (B10-s1..3, B15-s1..3, F = the training mode): the head's y0
  argmax on observer k's own stream at t (the act arc's forward, state
  from the world's start). If the predicted class equals j's APPLIED
  class at t, the branch IS the record (divergence 0, no replay). Else
  the class maps to one legal menu action — the entry of that class j's
  own policy ranks highest on her recorded row at t (legal = the
  engine's mask at t from the replay); a class with no legal entry maps
  to idle (the engine's refusal outcome); idle illegal too → the record
  stands. The replay reaches t asserting equality with the record, j
  takes the mapped action (her recorded message kept, every other seat as
  recorded), one step, j's happiness and needs are read. Divergence =
  branch − record, SIGNED and UNCLAMPED (pin b): happiness points
  (primary; positive = the predicted world is rosier than the real one)
  and the mean over the five hidden needs in need points (reported;
  negative = rosier). Per version × stratum × predictor: n, mean signed
  Δhap and Δneed, mean |Δhap| (the price), the share of points that
  branched and the share whose happiness moved (the sparsity); per
  friend and pooled; seed mean per arm.
- **R-2 `needs`** — step 2, the ostrich metric on NF1e-h24+p (pin d),
  with the frozen NF-h24+p beside: bias = predicted hidden-need mean −
  true hidden needs (need points, mean of five) on every covered
  (k, j, t) of the tuning half, by j's stratum and by version; per
  friend and pooled; seed mean of the three heads' per-seed means.
- **R-3 `verdict`** — §5 applied to R-0..R-2.

## 5. The rule (frozen pins applied; nothing here is a selector)

- **Act head (B15; B10 beside).** Per version: lift = |mean Δhap GRAVE| /
  |mean Δhap COMMON| (seed mean per arm, pooled over friends).
  SIGNATURE = lift ≥ 1.5 AND the GRAVE mean POSITIVE (optimism: the
  predicted act leaves a grave friend better off than she really was).
  A pessimistic grave lift is not the ostrich and is reported, not
  failed. Verdict: INSUFFICIENT if any GRAVE or COMMON cell of either
  version is under 200 candidates; else FAIL if the signature holds in
  either version; else PASS.
- **Needs head (NF1e).** Per version, Phase 1's signature verbatim
  (`read_phase1.ostrich`, LIFT 1.5): |GRAVE bias| ≥ 1.5 × |COMMON bias|
  with the GRAVE bias NEGATIVE (read less needy than she is). Verdict as
  above on the pooled cells (min-n 200 per seed).
- **The gate** PASSES only if B15 and NF1e both PASS. INSUFFICIENT
  anywhere → the gate is INSUFFICIENT: the remedy is probe-generated
  distress-adjacent coverage (pin c), never a waived stratum, and that is
  a new declaration on her word. FAIL on NF1e → Phase 2 does not enter;
  the next step is a Phase 1f composition arm on the needs head (her
  word). FAIL on B15 → the act head does not enter as the Phase 2 input;
  what replaces it is hers. Per-friend signatures are reported as
  "investigate", never as the verdict (the frozen "per-friend before
  pooled" is a reporting order; the rule is pooled).
- **B10 vs B15, open-loop.** Reported, not ruled: the two arms' mean
  |Δhap| and signed Δhap per stratum side by side. If no stratum shows
  B15's price under B10's beyond the seed SD, the Phase 2 declaration
  records that the B10 comparator arm's expected result is a null; the
  arm count stays her call ("three arms" is the default).

## 6. Registered predictions (this thread's; declared before any number)

- **P34.** Neither B10 nor B15 shows the act signature, pooled, in either
  version. Grounds: the act head's errors are not welfare-directional
  (F-074's confusions sit among move / idle / rest and eat / chase); the
  training set carries covered graves (Phase 1e's set).
- **P35.** NF1e's pooled mind-visible GRAVE bias is smaller in magnitude
  than the frozen NF-h24+p's on the same worlds (retraining with late
  graves, F-072, moved exactly this). Whether it clears the signature is
  NOT predicted: Phase 1b's signature fired at every width on group P.
- **P36.** The one-tick price is sparse: under 0.30 of the branched
  act points move happiness at all, in every stratum (the re-step probe:
  move ↔ rest priced to zero).
- **P37.** Every predictor's mean |Δhap| is larger in GRAVE than in
  COMMON (a grave friend has more to lose from a misread tick), F
  included — which is why the rule is differential AND signed, not a
  price bar.

Unscored expectations, reported: B15's mean |Δhap| at or under B10's in
every cell; F's GRAVE mean Δhap negative (always predicting play when a
hungry friend eats is pessimistic); GRAVE/visible candidates between 200
and 2,000 per world-set (one N world held 353).

## 7. Guards (`test_gate.py`; each red via `scripts/mutate.sh --expect` on the committed files before any read)

- **g1** — branch points: strata from the FRIEND's true state at t,
  t ≥ 1, covered friends only, never the scripted seat, never k = j;
  visible = the observer sees her; per-cell sample without replacement,
  fixed seed, min-n fail-closed (synthetic world).
- **g2** — class → menu action: the legal entry the policy ranks
  highest; none legal → idle; idle illegal → None; purr / meow have no
  entry (synthetic menu).
- **g3** — the replay runner on a real tuning world (N1, t = 40): the
  runner's own replay-equals-record assertion; a branch on the recorded
  act returns the record (the divergence scale's zero); a branch on
  another legal act returns a state.
- **g4** — the currency: signed, unclamped, happiness points and the
  hidden-need mean (bath excluded).
- **g5** — the act signature and the verdict: lift ≥ 1.5 with a positive
  GRAVE mean; pessimism is no signature; 1.4 under, 1.5 on the bar;
  fail-closed on a thin GRAVE cell; the needs head's signature fails the
  gate.
- **g6** — step 2: bias = pred − true hidden needs per tick on the
  friend's stratum; visibility per observer; the signature with GRAVE
  negative; a grave friend read MORE needy is no signature; 199 samples
  in one seed is under the floor.
- **g7** — the heads: exactly B10-s1..3 and B15-s1..3 from the act arc's
  store, frozen, at 8,182 / 12,438 parameters (B15 registered through the
  ladder arc).

Predicted reds (the FIRST assertion each mutant reaches; plain-string
replacements):

| guard | mutation (`gate_screen.py`) | predicted first failure |
|---|---|---|
| g1 | `codes = w["codes"][1:, j]` → `codes = w["codes"][1:, k]` (the OBSERVER's state bins the point) | first predicted `grave_all.shape[0] == 3 * 3` fails: `(0, 3)` — WRONG: observer 2's grave ticks give 3 friends × 3 ticks = 9 rows, the shape passes; re-predicted: the friend-set assertion prints the rows, `[[ 2  1 10] …` |
| g2 | `return max(cands, key=lambda i: float(logits[i]))` → `return min(...)` | "the policy's preferred legal rest" |
| g3 | `hap = np.asarray([st[k * pk + H.HAP] * 100` → `st[k * pk + H.HAP + 1] * 100` (the wrong state cell read as happiness) | first predicted "a branch on the recorded act is the record" — WRONG: `_state` also feeds the runner's own fidelity check, which fires first; re-predicted: "replay of 1095711 diverged from the record before tick 40" |
| g4 | `np.asarray(branch_needs)[S.HIDDEN] - np.asarray(rec_needs)[S.HIDDEN]` → `[:6]` both sides (bath counted) | the first g4 assertion prints `d_need` −10.0 |
| g5 | `"signature": bool(lift_v >= lift and g > 0)}` → `and g != 0)}` | "pessimism is not the ostrich" |
| g6 | `"signature": bool(lift_v is not None and lift_v >= lift and g < 0),` → `and g != 0),` | "a grave friend read MORE needy than she is is not the ostrich" |
| g7 | the `LA.register()` call removed from `act_heads()` | `KeyError: 'B15'` through g7's load |

**Reds on record 2026-11-05** (`scripts/mutate.sh --expect`, sequential,
baseline == restored, 7 passed each): seven of seven RED CONFIRMED. g2,
g4, g5, g6, g7 at the predicted first assertion; g1 and g3 red at the
FIRST run but at a different assertion than predicted (the two cases
above), re-predicted in writing and re-run: red at the re-predicted
assertion. Log in the session scratchpad (`gate-reds.log`). Lesson for
the recipe: a state reader shared by the fidelity check and the branch
reddens at the check; a mutant whose count coincides with the right one
(3 × 3 either way) is caught by the identity assertion, so a guard
asserts the identities, not only the count.

## 8. Blind spots (declared)

1. One tick never prices visitation shift or compounding (A2′'s declared
   blind spot; carried by the pairing with Phase 2's consumer reads and
   the canalization watch).
2. The class → menu mapping is this thread's: within the predicted class
   the friend's own policy chooses. A different within-class choice
   (random legal; the recorded partner) would move the price where the
   class has several entries (rest / sleep / groom / play with a
   partner). Reported beside: the share of branched points whose class
   had more than one legal entry.
3. The price is read on the FRIEND whose act was mispredicted, as her
   instrument says; the observer's own welfare under a wrong belief is
   not in it.
4. The heads' states run from the world's start on recorded rows; the
   Phase 2 policy will see the same streams, so this is the deployed
   condition, not a lab one.
5. GRAVE on the tuning half is natural covered crossings only; its count
   is reported, and a thin cell fails closed rather than being filled
   from the confirming half.

## 9. Doctrine check (`experiments/DESIGN-DOCTRINE.md`)

The screen is the frozen gate itself; the rules that moved a choice:
fail-closed min-n (pin c) → the INSUFFICIENT verdict and the no-waiver
remedy; unclamped currency (pin b) → raw happiness points, not the reward
floor; differential + signed (pin a, "an absolute bar alone fails
everything early or nothing ever") → the lift with the optimism sign, P37
registered as the reason; k = 1 (sitting item 5) → one step, the branch
discarded, no env is kept past its read; "never a selector" (her standing
rule 2026-11-02) → B10 vs B15 reported, the arm count hers; the scouts-
first practice: nothing here seats or trains a covered mind.

## 10. Owner calls

- Her word to run (after this draft). Her word on each consequence of
  §5's verdicts (INSUFFICIENT remedy; a FAIL on either head). The B10
  comparator arm's fate after the open-loop read (default three arms).
- Nothing else here is hers to decide; the thread's choices (§8 item 2,
  the sample size 300, the primary currency = happiness) are reversible
  and stated.

## 11. Run order (each step its own commit before its data)

1. This declaration + instrument + guards green (this commit).
2. Guards red on record (next commit).
3. On her word: `run_gate.sh` — sample → act → needs → verdict; RESULTS
   gated (a fresh subagent, Read fence only); TRIALS entry; deviations
   entry 21 CLOSED; timeline.
4. Then the Gen 2 Phase 2 declaration (on her word), carrying the
   verdict and the open-loop B10-vs-B15 read.

## 12. Regeneration

```
### Read (the gate runs these; fresh outputs to its scratchpad, never over reads/)
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $C/gate_screen.py sample  --out <scratch>/sample.json  --md            # minutes; 180 worlds
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $C/gate_screen.py act     --out <scratch>/act.json     --md --quiet    # about 10 min; replays; reads $C/reads/sample.json
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $C/gate_screen.py needs   --out <scratch>/needs.json   --md --quiet    # minutes; six heads x 180 worlds
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $C/gate_screen.py verdict --out <scratch>/verdict.json --md            # seconds; reads $C/reads/{sample,act,needs}.json
```

`A` = `experiments/needy-set-2026-10-28`, `C` =
`experiments/minifriend-phase2-gate-2026-11-05`, absolute paths in use.
Heads: `minifriend-act-2026-11-03/results-raw/heads/{B10,B15}-s{1,2,3}/head-best.pt`
(sha256 in each `done.json`); NF1e-h24+p and NF-h24+p through the Phase
1e diagnostics' loaders. Worlds: the needy set's `results-raw/set/`
tuning seeds; configs resolve in the needy-set arc, then Phase 1b's.
