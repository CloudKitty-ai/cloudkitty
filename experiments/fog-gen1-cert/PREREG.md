# Fog Gen 1 step 7 (certification round) — pre-registration

**DRAFT.** §Corpus and §Capacity check are declared (committed
2026-09-13 before their runs, per house rule). Everything else below
is the draft of the rest, written 2026-09-13 from the step-6 sitting's
rulings (`experiments/fog-gen1-timeline-2026-08-26.md` §"Step-6
sitting rulings"); it becomes the declaration when the pins fill, the
owner has read it, and this header is removed. Instruments and the
trainer are the shakeout's (`experiments/fog-gen1-shakeout/`), reused
unchanged unless a section here says otherwise. Doctrine check (CLAUDE.md
rule 8) recorded in §Doctrine.

## Purpose

Train and certify the Gen 1 roster: five distinct networks for five
seats (owner, 2026-09-13; re-confirmed for the twin risk), each a
roster-wide mind cloned from the B3 corpus and trained under the
leash at the pinned knobs, then read on the served composition. The
pass also carries the contrasts the doctrine owes this generation
(spec 054's reprice, the leash dose, the beam price), the
consent-transfer pair, and a candidate pool wide enough for the charm
ruling to refuse. Everything the step-5 shakeout screened stays
pinned: radius 4, speaker floor 20, listener 0.20, β 0.04 low end,
schema 5 width 408, the reward of spec 014 verbatim.

## The run table (20 of the owner's 27; ruled 2026-09-13)

All arms all-policy (MIX 0.0, no exception), radius 4, one network
per run. Every arm outside the twin is also a seat candidate if it
passes the floor. Inits are this directory's clones (§Pins).

| runs | slot family | init | dials | β | seed | reads |
|---|---|---|---|---|---|---|
| 5 | `cand-s1..s5` | B3 lesson | ramp, beam 7 | 0.04 | 1–5 | the pool; ramp side of the flat contrast; β 0.04 point of the dose sweep; `cand-s1` = consent-on side of the pair |
| 2 | `cand-s6, s7` | B3 lesson | ramp, beam 7 | 0.04 | 6–7 | pool to seven |
| 1 | `twin-off` | B3-off lesson | ramp, beam 7 | 0.04 | 1 | consent-transfer pair vs `cand-s1` |
| 2 | `plain-s1, s2` | B3 plain | ramp, beam 7 | 0.04 | 1–2 | charm contrast (free register); seatable insurance |
| 3 | `flat-s1..s3` | B3 lesson | `groom_cuddle_floor` 0.5, `slope` 0, `ceiling` 0.5; beam 7 | 0.04 | 1–3 | 054 re-verify, paired with `cand-s1..s3` |
| 2 | `dose-lo-s1, s2` | B3 lesson | ramp, beam 7 | 0.02 | 1–2 | rule 7 dose diagnostic, low |
| 2 | `dose-hi-s1, s2` | B3 lesson | ramp, beam 7 | 0.10 | 1–2 | rule 7 dose diagnostic, high |
| 2 | `beam10-s1, s2` | B3 lesson | ramp, `sleep_relief_sunbeam` 10 | 0.04 | 1–2 | beam screen |
| 1 | `beam15-s1` | B3 lesson | ramp, `sleep_relief_sunbeam` 15 | 0.04 | 1 | beam screen, upper point |

Seven of the 27 unspent; first use of the headroom, if the owner
takes it, is a third seed at each leash dose (two runs). Not spent:
no-seeding control (deferred to Gen 2), mixed seating (ruled
all-policy), a longer horizon (Gen 2 recipe data), a balanced corpus
(finding 6 corrected: the cause was dirt, not the corpus).

**Trainer**: `trainer/train_ppo_cert.py` (landed 2026-09-13 @
c699512, guard + three mutate reds), a wrapper that points the
shakeout trainer at `anchor-b3.toml`, the SLOTS table above with run
indices 21–40 (bands [520M, 920M), disjoint from every band in use),
pins `beta_lo` 0.02 / `beta_hi` 0.10 / `init_lesson` / `init_plain`
/ `init_lesson_off` / `critic`, an empty MIX, and per-slot dial
overrides applied beside the radius line (an existing key is
rewritten, an absent one inserted under its section; the result is
re-read and checked equal to the anchor with exactly the radius and
those keys moved, the shakeout's own check extended; the overrides
are written to `cert-overrides.json` beside the manifest). Smoked on
`beam15-s1` with the shakeout clone and critic as stand-ins (39
updates, 20k ticks): derived config carries `sleep_relief_sunbeam =
15.0` and `radius = 4`, manifest run index 40, seed base 900M,
anchor sha `782f96…`. The plateau and welfare stop rules,
the probe cadence (every 50 updates, 2k ticks, PROBE_SEEDS 40,001–3)
and the Part A read at probe 1 (`schema_check.py --policy-trace`
against a B3 anchor trace at r4, collected fresh) are the shakeout's
verbatim. The 20M cap stands; no arm is expected to reach it.

**Matched reads for the pair and the contrasts.** Arms stop at their
own plateaus, so paired reads (consent pair; `flat` vs `cand`; the
dose points against the β 0.04 pool; beam arms against the pool) are
taken at the same probe index, the earlier of the two plateaus, off
the probe series; a read at each arm's own final probe is reported
beside it, never in its place.

## Doctrine (CLAUDE.md rule 8: checked against `DESIGN-DOCTRINE.md` before the plan)

Rules that changed a choice, or confirmed one already on the table:

- Rule 9 (deploy test) **changed** the corpus plan: a teacher change
  orphans the corpus, so the Biscuit 3.0 anchor forced a fresh
  collection (§Corpus); a reprice orphans nothing scripted, so the
  beam and flat arms need no corpus of their own.
- Rule 7 (build when the world values it) **changed** two choices: the
  cue-answer rungs wait for Gen 2 (finding 4) and the mixed arm's
  groom retention was not a reason to seat mixed (finding 5); it also
  names the dose sweep as the diagnostic this pass runs.
- Rule 10 **changed** the battery's shape (§Battery): a floor against
  the scripted baseline of the same battery plus a per-seating trade,
  where the timeline's step 7 still said "two-layer welfare gates" in
  the incumbent-relative form. ROADMAP guard 1 still carries the old
  wording; owner's word owed.
- Rule 4 item 3 and rule 10 **confirmed** the free register, Biscuit's
  non-grooming and the beam screen as charm, declared here, ruled
  after.
- Rule 6 **confirmed** nothing in this pass filters a free word; the
  lesson clone strips scripted here-words only.
- Rule 2 **confirmed** the beam price as a state of the world.

## Rule 10 declaration (the trade, before instruments run)

**What this seating is for**: the first policy roster under fog with
the taught vocabulary, the spec 054 price, and the Biscuit 3.0
anchor; welfare at or above the scripted roster on the served world
(the floor); and, as charm, three things the pass cannot score:

1. **The free register** (chirp, purr; finding 8). Purpose: an honest
   state signal on the served roster. Benefit instrument:
   `phase2_read.py` free-word rate and activity split on the final
   probes, against the `plain` arms (the contrast). Declared cost:
   chatter (meow/1k against the plain arms, the shakeout read
   350–415 vs 185–240), reply-mass bars below the plain clone's (both
   above 0.50), message-head entropy that does not cool, and rule 7's
   expected drift-down in longer runs.
2. **Biscuit's non-grooming** (finding 6). Purpose: a character, play
   given where the others give bath. Instrument: `groom_cells.py` on
   the final probes (Biscuit's giver row stays 0; every dirty, visible,
   legal friend elsewhere is groomed). Declared cost: none at Gen 1
   (nobody dirty for Biscuit to groom); re-open at Gen 2 with dirt
   supply.
3. **Beam naps** (finding 7). Purpose: sunbeam naps back on the served
   roster. Instrument: in-beam share of sleeping ticks and
   settled-friend-on-beam opportunities (`phase2_read.py`'s cosleep
   read) on the beam arms against the pool. Declared cost: whatever
   welfare the picked price gives up inside the floor; the pick is
   the owner's, pencilled as the smaller price whose in-beam share
   clears the pool's beyond seed spread; a dominant preference is not
   required.

The charm ruling comes after the instruments: which candidates, and
which roster, have it; it may refuse all, which leaves a seat
scripted. Precedence, never a bar.

**Re-verifies this pass owes**: spec 054 (rule 7 contrast, `flat` vs
`cand`: groom-other at plateau, groom latency vs bath, three seeds a
side; a difference inside the seed spread establishes nothing); the
leash dose (rule 7 diagnostic: groom-other and free-word rates ordered
by β across 0.02 / 0.04 / 0.10, world-anchored if flat across dose,
leash-held if ordered); rules 3 and 4 at the beam pick (the beam is a
sleep-specialist form, not a rider; conduction pays the co-sleeper's
own specialist).

**Consent-transfer prediction (owner asked, 2026-09-13)**: consent
transfers. Conscripting a friend in need lowers that friend's welfare
and the team reward counts it, so unlike groom-other the world values
the gate. Read: consent share of duets (share conscripting a friend
with a non-play need over 30), duets/1k, element play, E1, `cand-s1`
vs `twin-off` at the matched probe index. Twins that match = a finding
against the prediction and the reopen trigger for a friend
re-admission mechanic (comfort-sweep Addendum 3 stays declined until
then).

**INVESTIGATE rows (log, never stop)**: the critic-compression
rewatch (owner approved 2026-09-13): explained variance and the value
range off each arm's `metrics.jsonl` through the pass, against #365's
compression nuance (ranks, does not extrapolate down); the shakeout's
Part B INVESTIGATE list (activity-mix band, latency creep, refusal
share above 3.5% by `reason`, dispersion drift, vocabulary oddities)
carried verbatim; the F-037 collapse detector v0.2 as a namer.

**Stop rows**: the shakeout's HALT list H1–H6 with its pinned numbers,
and Part A's stop-the-pass set at probe 1, unchanged.

## Battery (the floor, rule 10; runs after the pass, before seating)

Harness: `kitty-eval` on exported artifacts (the 006a path: torch
actor → export → seat), certification world = `anchor-b3.toml` with
the beam pick applied (the config the reseat serves), eval band
870,001–030, stress band 880,001–030, 30 × 20k, greedy; the scripted
baseline re-derived on the same config at battery time and its sha
checked against the intended world (D-003).

- **Floor, team**: rule 1's Nash (p = 0) of the candidate composition ≥
  the all-scripted roster on the same config, paired by seed.
- **Floor, per seat**: each seat's happiness ≥ the scripted cat in that
  seat of the same battery (needs_driven at four seats, playful c30 +
  consent at Biscuit's), paired; no noise allowance; a miss inside
  noise is replicated on a disjoint band and counts only if it
  survives.
- **Catastrophe gates**: distress age (constitutional 150; watchdog
  0), the stress streak bar as a multiple of the re-measured baseline
  (F-021; the 006a arithmetic 225 / max(1, floor(0.05 n)) stands
  until the baseline is re-measured here), fallback bound zero (no
  fallback path exists; the distress-gated intervention was deferred
  past the reseat on 2026-09-13 and bundles with the LLM-seat fallback
  chain, whose declared band will replace zero then).
- **Compositions read**: the candidate five-network roster (the one
  seated), and, report-only, each candidate in every seat against the
  pool (the per-seat pick's evidence).
- **Failure**: the gate stops, reports, and waits for the owner.

The incumbent delta at each seat (guard 2) is a reading that charges
the declared cost, cross-generation by nature: the 2.x roster cannot
run on the 3.0 world, so the delta is read off the last 2.x soak and
G5 census on record, stated as such.

## Part A on the B3 corpus (2026-09-14)

`schema_check.py` on the four B3 held-out traces with the shakeout's
declarations: A1 unproven with 0 undeclared and 0 overdue (the
shakeout's accepted state; 8 reasons read stale because their columns
moved on B3, the good outcome), A10 / A13 / A18 ok on all four, and
**one A14 row on rollout-03**: Biscuit at tick 1755 with sleep and
cuddle both at 27.899977 in the observation and want_cuddle legal.
Cause: an exact f32 tie in the encoded needs where the engine's
unrounded values order the two by less than the observation's
resolution, so the mask carries a fact the observation cannot. One
row in 400,000. **Part A amendment RULED (owner 2026-09-14, "A14
option 1 for now"):** A14's top-need clause exempts rows where the
want's need ties the observation's top need exactly; the count is
reported on every read (`<want>_top_need_tie_exempt` in the detail,
"N top-need ties exempt" in the summary) and stays on the record.
Landed in `schema_check.py` with a guard case (the tick-1755 pair
exempt, one float step under it red) and a mutate red. Rollout-03
re-reads A14 ok, 1 tie exempt. The engine-side fix (the want law
comparing needs in the observation's encoded space, so mask and
observation agree bit for bit) is BACKLOG, Product's lane, a teacher
change under rule 9 for the next corpus.

`declared_constant.json` in this directory is the cert copy: the
shakeout's groups and reasons verbatim, `expected_per_1000` refilled
on the B3 held-out traces by the 2026-09-08 method (events per 1000
world ticks over 80k): want_drink 39.663 → 32.938, want_play 6.463 →
8.2, second-sunbeam occupied 2.325 → 0.938, distress 0.088 → null
(zero crossings of the 90 line in 80k ticks: the c30 Biscuit keeps
its needs under it; A17 still exempts the group). The pass's Part A
read at probe 1 uses this file.

## BC bars (the shakeout's, unchanged)

Every clone that seeds an arm clears, on the held-out four: reply-here
mass ≥ 0.50 per kind; msg@1 ≥ 0.80 on rows where the source said a
here-word; want emission per kind within ±15% of the source for kinds
with ≥ 100 source rows. `expected_per_1000` refilled from the B3
held-out traces; `schema_check.py` green on them.

## Pins (filled as each artifact clears)

**Want bar on the proposed layer (2026-09-14, after the re-collection;
`bars-proposed.json` beside each clone).** The mechanism is confirmed
end to end: on the B3 held-out four the teacher proposed want_cuddle
5,888 times and the tick applied 4,904 (984 downgrades, 17% of
proposals; want_bath, the armed-only kind with no top-need or social
clause, has zero). Read against proposals every clone passes, and the
lesson clones slightly UNDER-emit:

| clone | want_cuddle proposed / applied | worst want ratio | bars |
|---|---|---|---|
| `b3-vocab-s2` (init_lesson) | 0.962 / 1.155 | want_drink 0.902 | PASS |
| `b3-clone` (init_plain) | 0.920 / 1.104 | want_play 0.892 | PASS |
| `b3off-vocab-s2` (init_lesson_off) | 0.972 / 1.170 | want_drink 0.904 | PASS |

- `init_lesson` — B3 lesson clone `results-raw/clones/b3-vocab-s2/b3-vocab-s2.pt`
  (strip best epoch 115, val 0.8323, act@1 0.8278; teach best epoch
  103, msg@1|here 0.953); reply mass .790 / .796 / .701 / .762, msg@1
  .953, wants 0.90–1.00 on proposals. FILLED.
- `init_plain` — B3 plain clone `b3-clone/b3-clone.pt` (best epoch
  111, val 0.8845, act@1 0.8251); reply mass .829 / .849 / .763 / .786,
  msg@1 .942, wants 0.89–1.04. FILLED.
- `init_lesson_off` — B3-off lesson clone `b3off-vocab-s2/b3off-vocab-s2.pt`;
  reply mass .794 / .789 / .684 / .775, msg@1 .953, wants 0.90–1.00.
  FILLED.
- `critic` — B3 critic (`b3-critic/`); the twin reuses it (declared).
  Trained 2026-09-13: best epoch 2, held-out EV 0.065 on targets of
  std 4.09 around 434 — the shakeout's flat-anchor-returns shape
  (#365, EV −0.046), not a defect. Acceptance = the #365 probe bars,
  declared here before the probe runs: on a random-legal policy (3
  worlds, 4k ticks, seed base 870,004, the B3 config) every prediction
  finite and inside [0, 2 × target mean], Spearman ≥ 0.3 against
  realized returns. Pass = accept as the distribution-recalibrated
  init ("Probe then accept", owner 2026-09-10); miss = owner call.
  **Probe PASS 2026-09-13** (`b3-critic/probe.json`): finite, in band
  (predictions 427–437 against realized 224–310, the same compression
  as #365: ranks, does not extrapolate down), Spearman 0.493 ≥ 0.3.
  `critic` = `results-raw/clones/b3-critic/critic6-0p998.pt`, FILLED.
- `init_lesson_off` bars (2026-09-13, `b3off-vocab-s2/bars.json`;
  strip best epoch 75, teach best epoch 114): reply-here mass
  .794 / .789 / .684 / .775 (bar .50) PASS; msg@1 on here rows .953
  (bar .80) PASS; wants 0.98–1.12 PASS except **want_cuddle 1.170,
  MISS** on the ±15% bar. Split by seat: every seat over-emits
  (Miso 1.15, Biscuit 1.17, Pumpkin 1.16, Kittybear 1.13, Clem 1.21),
  partnered rows 1.29 vs unpartnered 1.13, so it is systematic, not a
  seat; the shakeout's lesson clone had the same shape five points
  lower (1.06–1.16 by seat, 1.127 overall, a pass). Disposition
  waits on the B3 lesson clone's own bars (the seat init); the twin
  is the control arm. The bar is declared and changes only on the
  owner's word.
  **Root cause (2026-09-13, read on rollout-03's trace):** not the
  clone and not the cooldown. On the 1,094 false-positive rows the
  teacher was armed for cuddle, cuddle was its top need, no idle
  friend was in view, the cooldown was clear, and the mask said the
  word was legal, so the law says speak, and the teacher's proposal
  was want_cuddle. The corpus labels the APPLIED message
  (bc-collect's applied-not-proposed doctrine), and `world.rs`
  re-validates every message at apply time on the live mid-tick view
  after the activity and the earlier cats' turns have landed,
  downgrading an illegal one to Silent (the social clause and the
  top-need clause move mid-tick; reviewed 2026-09-04, 049 finding 3).
  On the post-apply snapshot 23% of the false-positive rows have a
  top need other than cuddle (true positives 1%), 70% an idle friend
  in view (58%), 83% one or the other (58%); ticks since the last own
  call and WaitForMe and action refusals were ruled out. So the
  clone reproduces the teacher's proposals, and the want bar, which
  compares argmax proposals with applied labels, carries the tick's
  downgrade rate as a built-in bias: +12.7% at c55 (a pass) and +17%
  at c30, where cuddle scenes start more often (partnered rows
  +29%). In the served world a policy's proposal meets the same
  downgrade, so this is not over-emission there either.
  **Disposition = owner's call.** The instrument reads the wrong
  layer for wants (proposal against applied). The fix is to record
  the proposed message beside the applied one in bc-collect
  (`label_msg_proposed.npy`) and read the want bar proposal against
  proposal; that is a tool change plus a re-collection, banked for
  the next corpus. For this pass the honest options are to accept
  the raw ratio with this mechanism on the record, or to re-collect
  now (about 1.6 h for both corpora, the clones unaffected since the
  applied labels are unchanged).
  **OWNER RULED option 2 (2026-09-13, "2"). Declared before the
  re-collection:** bc-collect gains `label_msg_proposed.npy` (the
  proposed message under the same codec, WaitForMe → Silent as
  before) and `msg_downgraded` in meta.json; nothing else it writes
  changes. Both corpora are re-collected with the new tool at the
  declared seeds and configs into fresh directories; guard
  `test_proposed_labels.py` proves, per held-out rollout, that every
  pre-existing file is byte-identical to the first collection (so the
  running clones and the critic stand) and that the proposed file
  obeys its invariants (a downgrade only goes to Silent, every
  proposed label mask-legal, at least one downgrade). The want bar
  (readout_fog `--want-source proposed`) then reads the clone's
  argmax proposals against the teacher's PROPOSED emissions, the
  layer the clone imitates; the applied ratio is reported beside it.
  The ±15% tolerance and the ≥ 100-row floor are unchanged. Training
  labels stay applied.
- `radius` 4, `floor` 20 / 0.20, `beta_low` 0.04 (shakeout pins, carried);
  `beta_lo` 0.02, `beta_hi` 0.10 (ruled 2026-09-13)
- `beam` 7 served; screen 10 / 15
- `flat` = floor 0.5, slope 0, ceiling 0.5 (spec 054 dials)

## Launch (owner's word)

Twenty runs at one thread each fill the box in one wave (or two waves
of ten at two threads); `nice -n 19` under `caffeinate -s`; logs in
`results-raw/pass-logs/`, artifacts in `artifacts/ppo-fog-<slot>/`.
Part A read at probe 1 on every arm before the pass is left to run.

## Corpus (declared 2026-09-13, before collection)

Two corpora, one teacher change apart. Both derive from the served
`cloudkitty.toml` under the shakeout's config rule (served file plus
declared keys), verified by flattened-TOML diff at generation: the
five shakeout keys (`announce_threshold` 30 → 20, `announce_here`
unset → 1, `reply_intensity_floor` unset → 0.20, `[vision] radius`
5 → 4; the retired flat `groom_cuddle_relief` is dropped, the spec
054 ramp defaults apply as served) plus the Biscuit 3.0 anchor ruled
2026-09-02 (F-038, `biscuit3-comfort-sweep-2026-09-01/`):
`playful_comfort` 55 → 30 and the spec 047 consent gate.

- `anchor-b3.toml` — `consent_line = 30.0`; sha256
  `782f969065541b3083923c1fac526f9574b592e34846246ac95a928db599c8ff`.
  The Gen 1 corpus: every certification candidate clones from it.
- `anchor-b3-off.toml` — `consent_line = 0.0` (gate off, byte-identical
  selector to pre-047); sha256
  `58864233e8bc9116508c8d607d1fcaac23716868413041847832066db20181f8`.
  The consent-transfer twin's corpus (timeline step 7: Biscuit 3.0
  trained twice, c30 with the gate at 30 and at 0, same seed and
  budget). The gate lives only in the scripted selector, so the two
  corpora differ in teacher rows, not in any price or view.

Why a fresh corpus at all: the shakeout corpus (seeds 1080001–40,
`anchor.toml`) was collected with Biscuit's teacher at comfort 55 and
the gate off; the ruled anchor never entered a config, so no step-5
clone is a Biscuit 3.0 clone (found 2026-09-13).

Shape, as the shakeout's (owner-ruled 40 × 20k, #350): 40 rollouts ×
20,000 ticks per corpus; held-out = index ending in 3 (03/13/23/33),
`--trace` on those four only; collected in nine seed blocks so the
trace flag applies per block; a flat symlink view with global rollout
numbering (`results-raw/<corpus>/flat/config-00-rollout-NN`) is what
the loader reads (`data6._is_val` keys on the name). Seeds: B3
1,090,001–1,090,040; B3-off 1,091,001–1,091,040. Both bands are new
and disjoint from every band in use (probe trio 40,001–3, shared eval
870,001–030, shakeout corpus 1,080,001–040, all PPO bands ≥ 100M).
Binary: `experiments/tools/bc-collect` rebuilt 2026-09-13 against
main at spec 054 (core rlib of the same build). Raws under
`experiments/fog-gen1-cert/results-raw/` stay uncommitted.

Collection, per block (`B` = b3 or b3-off, `S` = band base + offset):

    nice -n 19 experiments/tools/bc-collect/target/release/bc-collect \
      --config experiments/fog-gen1-cert/anchor-B.toml --rollouts N \
      --ticks 20000 --seed-base S [--trace] \
      --out-dir experiments/fog-gen1-cert/results-raw/bc-corpus-B/idxAA-BB

Blocks: idx00-02 (3), idx03 (1, trace), idx04-12 (9), idx13 (1,
trace), idx14-22 (9), idx23 (1, trace), idx24-32 (9), idx33 (1,
trace), idx34-39 (6). Eighteen processes, nine per corpus, launched
together under `caffeinate -s`.

## Capacity check (declared 2026-09-13, before training; owner: "Let's run the test")

Question (owner's): would a mind specialised to one seat free capacity
that the roster-wide mind spends learning to drive every seat? Read
as: is the clone capacity-bound at the served width? Two plain clones
on the B3 corpus, the registered recipe, same seed and data: the
served shape (`d_model` 64, `ffn` 128; 83,170 parameters) and a wide
shape (`d_model` 128, `ffn` 256; > 3× the parameters), via
`train_clone_fog.py --d-model 128 --ffn 256`. Reads on the held-out
four: val loss, act@1, msg@1 and the three BC bars (`readout_fog.py`).
**Prediction: not capacity-bound.** The wide clone lands within the
shakeout's seed noise on act@1 (the clone-fog run's 0.8369 stands as
the scale; a gain under 0.01 is noise, over 0.02 is a finding) and
moves no bar's pass/fail. If the wide clone clears 0.02 on act@1 or
flips a bar, capacity binds and a wider mind is a Gen 2 recipe input;
nothing about step 7 changes either way (the pass runs the served
shape). No PPO run is spent.

**Collected 2026-09-13 16:33–18:12 MDT.** Both corpora: 40 rollouts,
seeds exactly the declared bands (40 unique each), every meta.json
carrying the declared config sha, traces on 03/13/23/33 only, zero
dropped rows; B3 3,973,189 decisions, B3-off 3,973,440; 8.5 GB each.
The teacher change took (rollout-03, Biscuit's seat, against the
shakeout corpus): eat-over-30 share 0.472 → 0.124 (B3) / 0.150
(B3-off), the comfort sweep's c30 point (0.132); play chosen while
another need is armed and on top 0.56 → 0.04 in both; PlayKitty
per 1k 139 (shakeout) → 153 (gate off) → 97 (gate 30), the gate's
cut at 0.64× against the sweep's 0.73× on duets; Biscuit grooms
nobody in all three.

After collection, per corpus, the shakeout chain unchanged: lesson
clone (`train_vocab_fog.py --stage strip`, then `--stage teach`), the
plain clone for B3 only (`train_clone_fog.py`, the plain-clone
candidates), BC bars on the held-out four (`readout_fog.py`, the
shakeout's bar numbers stand until this file says otherwise),
`expected_per_1000` refill and `schema_check.py` on the held-out
traces, critic on B3 (`train_critic_fog.py`; the twin reuses it, a
declared assumption: the gate changes teacher rows, not returns'
scale). Pins are filled here when each artifact clears its bar.
