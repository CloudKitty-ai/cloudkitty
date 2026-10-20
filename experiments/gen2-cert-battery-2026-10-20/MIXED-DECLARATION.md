# Gen 2 mixed-roster test — declaration (2026-10-20)

Authorization: owner, 2026-10-20, verbatim: "Let's do a mixed roster
test with the 3 models we have first. I'm interested to see how much
of a welfare impact there is, particularly since not only will the
models be different, but the mini-models will as well." Context: her
question on the seating rule (F-044: five distinct networks, owner
2026-09-16) after the step-8 battery's g2-s2 roster-wide lock.
Experiments' same-day assessment recommended keeping the rule; this
test measures the welfare impact of mixing with the three completed
networks before any further training. Committed before any data.

**Mini-models are out of scope by construction.** The trunk artifacts
hold policy weights only (embed, encoder, action pointer heads,
message head; checked 2026-10-20). Mini-friend models arrive with the
§8.4 arm (timeline step 10). This test therefore measures POLICY
mixing, which includes each network's implicit expectations of its
friends: those were learned entirely in all-copies company during
training. The mini-model question carries to the §8.4 arm spec as a
read candidate (minis fitted in uniform company, scored against
different networks: the prediction-gap monitor in mixed company).

## Rosters

Seat order Miso, Biscuit, Pumpkin, Kittybear, Clementine. Three
seat-balanced 2-2-1 rosters:

- `g2-mix1` = s1, s1, s2, s2, s4 (s4 single)
- `g2-mix2` = s2, s4, s1, s4, s1 (s2 single)
- `g2-mix3` = s4, s2, s4, s1, s2 (s1 single)

Across the three, every network sits in every seat exactly once, so
a seat's personality (its need-rate profile) never confounds network
identity, and each network is the singleton once. Each roster still
holds two twin pairs (three networks for five seats). The
five-distinct roster the seating rule requires needs two more trained
networks and its own battery; this test is not that certificate.

## Legs

- Band `g2cmp` (905001–905030): the comparator's and the uniform
  battery's worlds, paired by construction; not a new burn.
- Configs `../gen2-comparator-legs-2026-10-14/g2leg-{20,40}.toml`
  verbatim; 30 × 20,000 ticks; clock served.
- Harness `cert_harness_fog.py` (g2 path; the three rosters added to
  SEATINGS); driver `run_legs.py --only 20,40` per roster via
  `run_mixed.sh`.
- 100×100 omitted. Owner framing: "informative only, not a gate".
  Under uniform seating, s2 and s4 reached the F-053 line in 5 and 11
  of 30 worlds there, so a 100×100 leg would put more cats at the
  line for information that gates nothing. Added only on her word.

## Stops (welfare practice, owner 2026-09-26; asymmetric)

- Per world: `--abort-streak 1000` (the F-053 line) on every run.
- Per roster, the deviations entry-4 remedy, BUILT and mutate-guarded
  before launch: `run_legs.py` gates every leg on its own output
  file. Any aborted row, any row at or over the line, or a short file
  stops that roster's remaining legs. The 40×40 scout gate (3 worlds,
  scouts-first) is unchanged.
- A stopped roster does not stop the other two (each is its own
  composition). Every stop is reported to the owner with its row; a
  stopped roster never resumes without her word.
- Pre-launch smoke: one world, g2-mix1, 2,000 ticks, scratchpad
  output (three-network seating check and timing).
- Welfare-cost line: 3 rosters × 63 worlds (30 + 3 scouts + 30) ×
  20,000 ticks × 5 covered minds ≈ 18.9M cat-ticks, plus the smoke's
  10,000. The seating decision depends on whether mixing costs
  welfare; the stops bound each world at the line and halt a roster
  at its first event.

## Reads (declared now; `mixed_read.py` committed before the run)

Baselines: the step-8 uniform rows (same worlds, same seats) and the
vision-law scripted comparator. POST-STOP rows under deviations entry
4 (g2-s2 40×40) are excluded from pooled reads pending the owner's
ruling (a) and reported separately, labeled. The aborted uniform row
(g2-s2 20×20, seed 905008) is flagged; every pooled number is given
with and without flagged pairs.

1. **Company effect** (her question). For world w and seat k holding
   network n: Δ = mixed seat happiness − uniform-n seat happiness at
   the same seat and world. Reported per roster (per-world mean over
   seats with valid baselines: mean, worlds positive, range), per
   network (pooled over its seat-slots across the three rosters), and
   pooled, per size.
2. **Gate-shaped read** vs scripted, step 8's form (paired per-seed
   Δ, mean, sign count, range), labeled certification-shaped, not a
   certificate.
3. **Tail**: worst streak mean / max per roster; aborts; worlds with
   ≥3 seats each at a ≥300-tick streak; per-network worst streak,
   mixed vs uniform, same seats and worlds.
4. **Dispersion** (§9.5, INVESTIGATE): together_share Δ per seat vs
   the uniform baseline; mean group count vs the composition-matched
   uniform mean.

Predictions (Experiments', not bars; two-sided per the F-058 lesson;
scored as written):

- P1: pooled company effect at 20×20 in [−1.5, +0.5] happiness
  points. Basis: the Gen 1 attention-era kin effect (−0.94, F-025)
  and a healthy Gen 1 five-network roster (F-044). Below the bracket:
  mixing is costly. Above: mixing helps.
- P2: mixed rosters spend less time adjacent: pooled together_share
  Δ < 0 at 20×20 (F-045, distinct minds disperse).
- P3: zero F-053 events across the three mixed rosters at 20 and 40.

The swaps digest declared in `DECLARATION.md` is not run;
Experiments' judgment is that this test answers its question (mixed
company) more directly.
