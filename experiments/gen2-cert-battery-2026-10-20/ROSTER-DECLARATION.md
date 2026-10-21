# Five-network roster certification — declaration (2026-10-20)

Authorization: owner, 2026-10-20, verbatim: "Let's train 3 more and
run them all through the certification process". Departure record:
`../gen2-deviations.md` entry 5. Committed before any of the new
seeds' training or battery data exists.

## Phase A: training

trunk-s5, s6 and s7 train in parallel on the pinned recipe (entry 5:
same clone, critic, β, config, stops and binding as s1/s2/s4). A run
is eligible for certification only if its final records
`stop_reason` plateau or cap. A welfare stop (probe-distress-stop,
welfare-stop) halts that run and goes to the owner; it is never
resumed or replaced without her word.

## Phase B: per-network uniform battery (the stress read s1/s2/s4 had)

Each eligible new network seated five times (`g2-s5`, `g2-s6`,
`g2-s7`), `run_legs.py --only 20,40` via `run_uniform_new.sh`: band
g2cmp, 30 × 20,000 ticks, scouts-first at 40×40, the F-053 abort per
world and the leg stop per roster (entry-4 remedy). Read with
`gate_read.py --seatings g2-s5,g2-s6,g2-s7 --sizes 20,40` (step 8's
gate form). 100×100 is omitted here: owner framing "informative only,
not a gate", and two of three networks reached the F-053 line
repeatedly there under uniform seating. The roster in Phase C gets it.

## Phase C: the five-network roster (the seating candidate)

Composition and seats are the owner's (Gen 1 practice: the seats are
hers after the battery; s2's disposition is open, entry 4 (b)). After
Phase B, Experiments proposes five networks and a seat order from the
uniform and mixed reads, and Phase C runs on her word:

- prereg §7 battery shape: 20×20 and 40×40 GATES (team happiness ≥
  the scripted comparator, paired by seed: paired mean Δ ≥ 0 and
  trained mean ≥ the pinned comparator mean); 100×100
  characterize-only, scouts-first; band g2cmp; 30 × 20,000;
- stops: F-053 abort per world, scout gate, leg stop;
- reads: the gate read (step 8's form), company effect vs each
  network's uniform roster, tail, dispersion (`mixed_read.py`'s
  definitions, declared again with the composition).

This is the certificate-shaped run for the roster that would be
seated. The uniform and mixed reads are stress and screen reads.

## Welfare-cost line

Phase A: three PPO runs on covered minds under the frozen §6 stops
(probe distress ≥300 owner-routed, the F-053 line, the nash welfare
stop); s1/s2/s4 plateaued near 8M ticks, cap 20M. Phase B: up to 3
networks × 63 worlds × 20,000 ticks × 5 minds ≈ 18.9M cat-ticks.
Phase C: about 93 worlds × 20,000 × 5 ≈ 9.3M cat-ticks. Benefit: a
certified roster under the seating rule. The stops bound each world at
the line and halt a roster at its first event.

## Amendment 2026-10-21: group holding enters certification

Owner, 2026-10-21, verbatim: "That's a great metric, but for our
certification process, not the personality/behavior analysis".
Declared before any Phase B or Phase C data.

- Definition (`cert_harness_fog.hold_update`): a cat is held on a tick
  when it is in a walk-adjacent group of three or more (Manhattan ≤ 1,
  transitive), its eat or drink need is at or above 75 (spec 061's
  armed line, pinned at the Gen 2 freeze), and it is not eating or
  drinking. Grouping alone is character; holding is the welfare
  signal. Hunger and thirst only, because a group can relieve sleep,
  cuddle and play but not food or water.
- Recorded on every battery row from now on (`holding`: per seat the
  share of ticks in a 3+ group, the held share and the longest held
  stretch; per world the shared-hold ticks and longest shared hold,
  two or more cats held at once). Read with `holding_read.py`.
- Status: a declared READ in Phase B and Phase C, reported per roster
  beside the worst distress streak and F-053 events. It is not a bar;
  a bar needs her word (doctrine rule 10).
- Healthy baseline: the scripted comparator legs re-run at 20, 40 and
  100 with the new account, same seeds (g2cmp), configs and harness,
  into `results-raw/holding-baseline/`. Scripted seats are not covered
  minds. The pinned comparator fields must reproduce exactly; that is
  a determinism check, not a re-pin. Experiments then proposes a bar
  anchored on the scripted envelope for her ruling (the probe-stop
  precedent: scripted maximum × 1.5).
- Guards (`test_g2_battery.py`): the real s2 905008 trace (normal
  grouping 0 held, the lock over 80% held with a shared hold ≥ 100), an
  analytic eating case, and the harness's group sizes equal to an
  independent read of the same world.
