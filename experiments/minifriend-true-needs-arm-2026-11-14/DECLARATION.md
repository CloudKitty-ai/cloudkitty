# Mini-friend Phase 2c: the true-needs arm (DECLARED 2026-11-14)

Status: **DECLARED 2026-11-14** on her word "Yes as drafted." (§0, §12).
§3–§9 are frozen as drafted from this commit; a change to them is a
`gen2-deviations.md` entry on her word. Run index 124 is claimed in
`SEED-BANDS.md`; the record is deviations entry 37. The arc is the needs-only arm (`minifriend-needs-arm-2026-11-12/
DECLARATION.md`, frozen 84b3a3ec) with one thing changed: what the nine
cells hold. Every text of Phase 2 and of that declaration it does not
restate stands as written.

## 0. Her words, verbatim and in order

- 2026-11-14, after the needs scout's read: "Long term, I would like to
  incorporate a world model and model of friends, in a way that is
  welfare positive. It seems to me that either the current world is too
  simple for the information the new heads provide to be useful, that
  the information the heads provide is inadequate to produce better
  decisions, or that the information from the heads is not being
  properly incorporated to the trained models (so the world is complex
  enough, the heads are informative enough, but the models aren't using
  that information well)".
- 2026-11-14, on the session's "One training run would separate your
  second hypothesis from the others: feed the true needs in place of
  the head's estimates": "I like that training run with the true needs
  fed in as well, let's test that".
- 2026-11-14, on the seven calls of §12 as put to her ("'Yes as
  drafted' declares calls 1–6 as recommended; say so if you also want
  call 7"): "Yes as drafted.", and in the same message: "While that
  runs, what options do we have to improve model utilization of the
  heads data, assuming for the moment that that's the issue?"

## 1. What is being asked

**If a cat is told its friends' true needs, does welfare rise?** The
needs-only arm fed the policy a head's estimates of each friend's
hidden needs and read level with the no-head arm at equal length. This
arm feeds the facts themselves through the same nine cells. It is the
ceiling of every needs head: if the truth buys nothing, no head of this
kind can.

Not asked: whether a head could reach the ceiling (the truth is given
for friends the cat cannot see or hear, which no head could know: §10);
anything about position or search (the lost-cat read, entry 36); seating
anything anywhere. **This arm's networks act on facts a cat under fog
does not have. They are a measurement and are never seated, served or
used as a teacher** (§11, rule 5).

## 2. Facts the design rests on (all on record)

- **The needs-only scout** (entry 36, seed 1, paired per world):
  against the no-head final −0.235 / −0.442 at 20×20 / 40×40 (0 of 30
  worlds each); against the no-head arm's own 12M checkpoint at 40×40
  +0.032 (21 of 30). It stopped at 12,002,304 ticks, the no-head final
  at 15,000,576. The dual-head seed, also 12.0M, sits +0.243 / +0.468
  above it. Edges 0.326 / 0.325.
- **Its cells are read.** Zeroing them changes 0.0287 / 0.0252 of acts,
  0.0966 / 0.0917 on rows the head flags.
- **The head's error** (F-064): RMS about 5.3 need points in common
  states, about 25 in grave ones.
- **Wants are already spoken.** Hearing is global and a want call
  carries the caller's need at the call (docs/encodings.md). Deafening
  every hearer to want-words costs the served roster nothing
  measurable (F-052).
- **The lost-cat read** (entry 36, `diag_lost.py`): the long streaks
  are one cat far from its friends; its friends hear it on 0.92–1.0 of
  their moves and close on it on 0.52–0.66 of them.
- **Findings relied on:** F-052, F-064–F-073, F-046 (a feature training
  never conditioned on stays unused), F-021 (one observation bit can
  buy a behaviour), F-053 / F-060 (size transfer; the 1,000-tick line),
  F-059 (eval-time ablation is a probe), F-063 (a distress habit is a
  per-network trait), F-017 / F-044 (uniform seatings are stress
  reads).

## 3. The arm

`truth`: slot `p2-truth-s1` (the scout), grafted from trunk seed 1 and
read against it, as Phase 2 §3–§4. Cells appended to each friend's row,
**C = 9, the needs arm's shape and order**:

| cell | needs arm | this arm |
|---|---|---|
| 0–4 | the head's estimate of eat, drink, sleep, play, cuddle | the friend's true need / 100 |
| 5 | estimated happiness | true happiness / 100 |
| 6 | estimated bath | true bath / 100 |
| 7 | P(grave) | 1 if the friend is grave by `strata.stratum`, else 0 |
| 8 | ticks-since-live | unchanged (from the cat's own rows) |

The truth is the engine's state at the start of the tick, for every
friend on every tick, in sight or not. A vacant row is zero. No head is
loaded. Run index: the next unclaimed at DECLARED (124 as the ledger
stands, stripe 2,580,000,000–2,599,999,999), claimed in `SEED-BANDS.md`
before first burn.

## 4. Training (Phase 2's recipe verbatim; deltas only)

- **Stop rule: Phase 2's, unchanged** (the 8,002,560-tick floor, the
  frozen plateau rule, the 20M cap).
- **Harm stops armed as written**: probe distress streak ≥ 300, F-053's
  1,000-tick line, nash < 0.5 on three probes. A trip halts the seed,
  owner-routed, never auto-resumed. There is no needs trigger: no head
  is read.
- **Scout seed only.** Seeds 2 and 4 are not part of this declaration.
- **Binding**: the Phase 2 arc venv (engine 226509ec).
- **Code this needs, none built**: `heads_online.ARMS["truth"]` (no
  head, 9 cells) and a truth-cell builder from the engine state;
  `OnlineHeads.step` takes the state for this arm only; the trainer's
  runner, its probe actor and the cert harness's `p2` seat pass the
  state; the slot and stripe bound in `train_ppo_p2.py`; a
  `p2u-truth-s1` seating; the readers' arm lists. Each change sorts
  Phase 2's and the needs arm's guards first (CLAUDE.md rule 6) and
  lands with its own red.

## 5. Welfare-cost line

Covered minds train on the served 20×20 under the frozen asymmetric
stops and are then read on battery legs.

| | expected (12.0–15.0M ticks) | most (the 20M cap) |
|---|---|---|
| training | 60–75M | 100.0M |
| probes | 2.3–2.9M | 3.9M |
| legs 20 / 40 at the 12M checkpoint, size scouts at 40 and 100 | 6.6M | 6.6M |
| legs 20 / 40 at the final, if it is not the 12M checkpoint | 0–6.0M | 6.0M |
| **total** | **about 69–91M** | **about 117M** |
| call 5, if ruled: the no-head 12M checkpoint's 20×20 leg | 3.0M | 3.0M |

(Covered cat-ticks; five seats.) Expected distress exposure: the needs
scout's worst training probe streak was 268 against the line of 300
and its legs' worst 201 / 908, with two of three 100×100 scout worlds
aborted at the 1,000-tick line; a halt here is a live possibility. The
decision bought: whether information about friends' needs can pay at
all in this world, which decides whether the needs-head line (Phase 1f,
the held dual-head seeds) is worth any further cost.

## 6. The reads

- **R-1 welfare, at equal length.** Uniform legs at 20×20 and 40×40,
  30 worlds × 20k ticks on g2cmp 905001–905030, F-053 abort armed, on
  the arm's checkpoint at update 3,906 (12,002,304 ticks), paired per
  world against: the needs scout's final (12.0M), the dual-head seed's
  final (12.0M), the no-head arm's 12M checkpoint (recorded at 40×40;
  at 20×20 only if call 5 is ruled), and trunk seed 1. If the run stops
  later than 12.0M its final is read too, against the no-head final,
  labelled as the unequal-length read.
- **The block read** (the needs arm's reader at C = 9): the share of
  acts the truth cells drive, on all rows and on rows where the friend
  is truly grave.
- **The tail read** (`diag_lost.py` on this arm's legs): streaks of
  300+, a lonely cat's closing by walk, and friends' closing on a lost
  cat.
- **Size scouts**: 3 worlds at 40×40 before its leg; 3 worlds at
  100×100 (905001–905003, the lost-cat read's worlds) read by the tail
  read only. A 100×100 leg is not part of this declaration.

## 7. Predictions (the session's; registered at DECLARED, before any number)

- **T1.** truth − needs at equal length is inside the edge at 20×20 and
  40×40 (|Δ| ≤ 0.326 / 0.325). Grounds: wants are already spoken and
  hearing them is welfare-null (F-052); the needs arm is level with
  no-head at equal length; a cat has few acts that serve a friend.
- **T2.** truth − no-head at equal length is inside the edge at 40×40.
- **T3.** The truth cells drive at least 0.025 of acts at both sizes,
  and more on rows where the friend is truly grave than on others.
- **T4.** Friends still do not come: on the 40×40 leg and the 100×100
  scout, unpartnered friends' moves close on a lost cat on under 0.70
  of them (scored only on 500+ such moves at a size). Grounds: the
  lost-cat read puts the limit at long walks, not at knowing.
- Unscored expectation: no change in the count of 300+ streaks against
  the needs scout on the same worlds.

## 8. Reading grammar (every consequence is hers)

On truth − needs at equal length, at 20×20 and 40×40 against the edges.
Every outcome is one of these five:

- **LEVEL** (inside the edge at both sizes): true needs buy nothing
  measurable as an input in this world at this budget. The limit is
  not the head's quality. Put to her: close the needs-head line for
  Gen 2's world (Phase 1f, the held dual-head seeds), spend on the
  tail.
- **ABOVE** (beyond the edge at both sizes): needs information can pay.
  Put to her: a second arm that gives the truth only for friends seen
  or heard, to split a better head from facts no head could know;
  Phase 1f back on the table.
- **BELOW** (beyond the edge at both sizes): even true information
  costs as an input. That is her third reading (the model does not
  incorporate it well) and a question about the graft, not the head.
- **ONE SIZE** (the same sign at both, beyond the edge at one): named
  as that; nothing is concluded until replicated.
- **UNDECIDABLE** (opposite signs, either beyond its edge).

One seed clears nothing; a result inside the edge establishes nothing
until replicated (doctrine rule 10). The edge is seed-to-seed spread: a
real effect smaller than about 0.33 is invisible here.

## 9. Guards (each red before the scout trains)

Phase 2's g0–g12 and the needs arm's g13 re-run on the edited files;
new, each through `scripts/mutate.sh --expect` with its prediction
written first:

| guard | asserts | mutant | predicted red |
|---|---|---|---|
| g14a | on a recorded world the truth arm's cells 0–7 equal the engine state's needs / 100, happiness / 100, bath / 100 and the `strata` grave flag of the ROW'S friend on every tick; cell 8 is ticks-since-live | the friend index off by one (each row reads the next friend) | `truth cells differ from the engine state's` |
| g14b | the cells are the start-of-tick state, the same tick as the observation | the state read after the step | `truth cells lead the observation by a tick` |
| g14c | a truth step loads no head and refuses to run without a state; every other arm's step is unchanged and takes none | the state defaulted to zeros when absent | `truth step ran without a state` |
| g14d | `p2u-truth-s1` seats `p2:p2-truth-s1` in all five seats; the harness's seat on a truth artifact equals the trainer's forward at every tick of a recorded 300-tick leg | the harness seat passes no state | `truth step ran without a state` |
| g14e | a smoke run of `p2-truth-s1`: 9 cells, the claimed run index and stripe, no head sha256 in the manifest, no needs read, no world fork, the final names the arm | the slot mapped to the needs arm | `the final names arm needs` |
| g10 | the slot table's run indices and stripes, the truth slot above every claimed stripe | the truth slot given run index 123 | the duplicated index named |

The readers' extensions (the equal-length paired read on a checkpoint,
the block read on true-grave rows, `diag_lost.py`'s arm list) are not
needed to train; each is built before its first read with its own red.

## 10. Blind spots (declared)

- One seed; one checkpoint an arm. The equal-length read removes the
  budget term from the contrast with the needs and dual-head seeds, and
  from the no-head contrast only where a 12M no-head leg exists.
- The truth is given for friends out of sight and hearing. ABOVE would
  not say a head can get there; LEVEL says no head can.
- Friends who act on true needs behave differently from the friends
  any head was trained beside.
- Battery worlds hold few grave events at 20×20 and 40×40: LEVEL there
  may mean little to act on. The 100×100 scout is three worlds and is
  read for the tail only.
- Uniform five-copy seatings are stress reads; the contrast holds, the
  level does not.
- Found at the build: the graft pads a friend's row when its 58
  observed cells are all zero (Phase 2's tokenizer rule, unchanged), so
  the truth cells of a friend neither seen nor heard in the digest
  window are computed and never reach the policy. Such rows are 0.4% of
  rows on the two leg worlds read (905001 at 20×20, 905012 at 40×40,
  6,000 ticks each). Every head's cells are inert on the same rows, so
  the arm is still the ceiling of a needs head under this graft.
- The grafted trunk never saw these cells (as in every Phase 2 arm);
  BELOW would not separate "cannot learn to use them" from "this graft
  at this budget does not".

## 11. Doctrine check (`experiments/DESIGN-DOCTRINE.md`; CLAUDE.md rule 8)

- Rule 5 (a teacher may only act on what the student can see): the arm
  acts on what no cat can see. It moved §1's fence: the networks are a
  measurement, never a teacher, never seated. Her call 2.
- Rule 8 (design scarcity of information): the arm removes the
  scarcity on purpose to price it; it moved the framing to a ceiling,
  not a proposal.
- Rule 1 (reward is team welfare only): reward unchanged; moved nothing.
- Rule 7 (build a behaviour when the world that values it exists):
  LEVEL would be read as this rule's case; moved §8's first bullet.
- Rule 9 (frozen models cannot answer a reprice): the contrasts are
  same-generation arms; moved nothing new.
- Rule 10 (a noise reading is never a bar): moved §8's last paragraph.
- Rule 11 (name the invalidation domain): eval-time ablation is a
  probe (§6 block read), outside the arm's configuration.
- Rule 12 (relief is always available): the harm stops armed; nothing
  in the world changes.
- Rules 2, 3, 4, 6: moved nothing.

## 12. Owner calls (recommendation first; her word rules)

**RULED 2026-11-14, "Yes as drafted.": calls 1–6 as recommended.**
Call 7: her message goes on "While that runs, …". The session reads
that as her word that the scout runs once §9's reds are on record (the
session's reading, labelled as such and told to her at the launch; the
run stops on her word at any time).

1. **Declare this** (after her edits). Recommended.
2. **A covered mind trained on facts it could not have under fog**, as
   a measurement only, never seated. Recommended; it is the only way to
   price the ceiling.
3. **The truth for every friend on every tick** (the full ceiling),
   not only friends seen or heard. Recommended: if the full ceiling is
   level, one run closes the question; the narrower arm is §8's ABOVE
   follow-up.
4. **The equal-length read at the 12M checkpoint** as the primary read.
   Recommended: the needs scout's result turned on training length.
5. **The no-head 12M checkpoint's 20×20 leg** (3.0M covered, an
   existing checkpoint) so T2 has both sizes. Recommended.
6. **A 100×100 size scout only** (0.3M), no 100×100 leg. Recommended:
   the needs scout aborted two of three worlds there.
7. **Launch on the guards**: the scout starts when §9's reds are on
   record, without a further word. Hers to give or withhold; without it
   the launch waits for her.

## 13. Run order (each step its own commit before its data)

1. DECLARED on her word; the seed-band row; a deviations entry.
2. Instruments and guards; every red on record.
3. On her word (or call 7): the scout trains.
4. The checkpoint legs (40×40 scout, then 20 and 40), the 100×100
   scout, call 5's leg if ruled; the final's legs if it ran past 12M.
5. The reads; the grammar put to her.
6. RESULTS gated.
