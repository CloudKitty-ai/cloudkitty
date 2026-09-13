# Fog Gen 1 step 7 (certification round) — pre-registration

**DRAFT.** Only §Corpus below is declared (committed 2026-09-13 before
collection, per house rule). The run table, the rule 10 declaration
(floor battery, charm trade, re-verify contrasts, INVESTIGATE rows),
the BC bars and the pins follow as the step-6 sitting closes; the
rulings so far live in `experiments/fog-gen1-timeline-2026-08-26.md`
§"Step-6 sitting rulings". Instruments and the trainer are the
shakeout's (`experiments/fog-gen1-shakeout/`), reused unchanged unless
a section here says otherwise.

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

After collection, per corpus, the shakeout chain unchanged: lesson
clone (`train_vocab_fog.py --stage strip`, then `--stage teach`), the
plain clone for B3 only (`train_clone_fog.py`, the plain-clone
candidates), BC bars on the held-out four (`readout_fog.py`, the
shakeout's bar numbers stand until this file says otherwise),
`expected_per_1000` refill and `schema_check.py` on the held-out
traces, critic on B3 (`train_critic_fog.py`; the twin reuses it, a
declared assumption: the gate changes teacher rows, not returns'
scale). Pins are filled here when each artifact clears its bar.
