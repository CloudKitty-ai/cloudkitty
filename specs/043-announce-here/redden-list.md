# Redden List: spec 043 `announce_here` (house rules 5/6)

Sorted before code (rule 6). Every must-RED is shown red for its
predicted reason before the guard counts as evidence; observations land
in the OBSERVED lines as the injections run. Every must-GREEN pile is
re-read (not just re-run) before the final pass.

## Must-RED (new guards, each shown red first)

| # | Guard | Injection | Predicted failure |
|---|---|---|---|
| R1 | stamp guard `roam_cell_stays_out_of_the_default_serialization` + `"announce_here"` key (T005) | temporarily drop the field's `skip_serializing_if` attribute | "announce_here leaked into the stamp" — key appears in default serialization |
| R2 | `HERE_KINDS` order pin (T007) | swap two entries in the const | pin names the swapped order vs `MessageKind::ALL` |
| R3 | precedence guard (T009) | none needed pre-impl | red before T014: here path absent → guard's armed-want case passes trivially? NO — guard asserts want-kind returned; red comes from the knob-on/silent case in the same test run (see R4–R7: all five US1 guards red together pre-T014 because the here path does not exist) |
| R4 | phase-gate guard (T010) | pre-impl red | expects `None` off-phase but ALSO expects here-speech on-phase in its fixture sanity arm → fails: no here path |
| R5 | selection-cycling guard (T011) | (a) pre-impl red; (b) T014 injection: the handoff's literal `(tick+id) % n_legal` | (a) no here path → no cycling; (b) index pinned to first legal kind — cycling assertion reds |
| R6 | legality guards (T012) | pre-impl red | non-adjacent case would pass trivially; the adjacent+cooldown-re-derive arm fails: no here path |
| R7 | vocabulary guard (T013) | pre-impl red | disabled-vocab case trivially `None`; the enabled sanity arm fails: no here path |
| R8 | gate-zero assertion 1 (T016/T017) | give world B a divergent `playful_comfort` | action-projection digest mismatch |
| R9 | gate-zero assertion 2 (T016/T017) | set world B's knob to 0 | non-vacuity red: zero Here\* emissions in B |
| R10 | gate-zero assertion 3 (T016/T017) | temporarily run the here path BEFORE the want loop | want+WaitForMe streams diverge between A and B |
| R11 | density ladder (T019) | temporarily ignore the period in the phase gate (any N ≥ 1 treated as 1) | all three arms emit the period-1 count → strict-decrease assertion reds |
| R12 | armed determinism (T020) | process-global `static AtomicU64` mixed into the selection index (announce has no RNG access; `gen_bool` won't compile) | second run's message stream diverges once the counter differs |

### OBSERVED (filled at implement time)

- R1: OBSERVED RED as predicted — dropped `skip_serializing_if`, guard
  panicked "announce_here leaked into the stamp: …\"announce_here\":0…";
  restored, green.
- R1b (T006 round-trip guard): OBSERVED RED — injected
  `skip_serializing` (unconditional), guard panicked at the
  `"announce_here":4` assertion; restored, green.
- R1c (T006 zero≡absent guard): first injection attempt (drop `default`)
  stayed GREEN for the wrong reason — the original `absent` arm omitted
  the whole `[behavior]` table, so the struct-level default masked the
  bug. Strengthened the test to a present-table/absent-key fixture (the
  shape every existing world config has); re-observed RED
  ("missing field `announce_here`"); restored `default`, green.
- R2: OBSERVED RED as predicted — swapped HereWater/HereFood in the
  const, pin panicked naming the swapped order (left
  `[HereWater, HereFood, …]` vs right `[HereFood, HereWater, …]`);
  restored, green. (First injection attempt was a no-op — a perl regex
  that matched nothing; caught because the "red" never appeared.)
- R3–R7: _pending_
- R8: _pending_
- R9: _pending_
- R10: _pending_
- R11: _pending_
- R12: _pending_

## Must-GREEN (kept pile — re-read, then run; zero modifications allowed)

| # | Witness | Why it must stay green |
|---|---|---|
| G1 | `roam_cell_stays_out_of_the_default_serialization` (with the new key) | stamp unmoved (SC-001) |
| G2 | `evolution_golden` — pin `7b361b2a…` unregenerated | 10k-tick default world byte-identical |
| G3 | `meow_courtesy` tests | courtesy interplay untouched (message channel law) |
| G4 | `say_surface_grounding` tests | grounded-legality law untouched |
| G5 | `behavior_variation` tests | scripted decision ladders untouched |
| G6 | needs_driven + playful decide tests | from_legacy junction byte-unchanged |
| G7 | full `cargo test --workspace` | zero modified existing tests |

### Re-read log (filled at T015/T025)

- _pending_
