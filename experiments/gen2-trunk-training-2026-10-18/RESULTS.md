# Gen 2 trunk training — results

Arc home for the frozen prereg's §5 trunk recipe
(`gen2-prereg-2026-10-17.md`): BC clone, critic, then PPO at three
seeds. Trainer package in `trainer/` (committed 29e430fa, c9c2c2fe,
bdca5d82); artifacts land in `artifacts/` (gitignored — never delete).
Corpus = `../gen2-collection-driver-2026-10-14/results-raw/full-100/`
(100 rollouts, 9,960,292 decisions, collection gates in that arc's
RESULTS.md).

## BC clone (trunk-clone) — readout 2026-10-18

train_clone_g2.py on the full corpus: EntityPolicyV6 (obs 399 →
35 activities + 16 messages, 84,450 params), two-head masked CE
(eps 0.05 over the legal set), Adam 3e-4, batch 4096, plateau
patience 10 on summed val loss, epoch cap 200, seed 20261018.
Split: 90 train / 10 val rollouts (every rNN ending in 3), i.e.
8,964,180 train / 996,112 val rows. Consent swap per frozen §4:
136,699 refusal rows took the proposed label; 389 kept applied
(off-menu residual, `gen2-deviations.md` entry 1, RULED).

Stopped by plateau at epoch 112. Best epoch 102:

| metric | value |
|---|---|
| val loss (summed) | 0.8330 |
| val act loss / msg loss | 0.5198 / 0.3132 |
| act@1 | 0.8608 |
| msg@1 | 0.9763 |
| H(act) / H(msg) | 0.5233 / 0.3121 |

Per-group val accuracy (val counts in parentheses; groups per
data_g2.ACTION_GROUPS):

| group | acc | n |
|---|---|---|
| move | 0.8748 | 325,411 |
| rest/sleep | 0.9652 | 238,775 |
| groom-self | 0.9415 | 15,174 |
| groom-kitty | 0.9842 | 31,497 |
| eat/drink | 0.9833 | 38,890 |
| play/chase | 0.8402 | 293,604 |
| idle | 0.2300 | 52,761 |

Notes, measured not interpreted:

- Idle is the one group far below the rest (0.2300 on 52,761 val
  rows); the smallest activity class is ChaseCritter1 (n=101,
  acc 0.1980). No frozen bar names a clone top-1; this readout is
  the record and the pin's basis, and PPO reshapes the policy from
  here.
- The free registers never appear as val labels — Mew, Purr, Chirp,
  Trill, Ekekek all n=0 — consistent with the §8.1 chatter floor
  (0 free-register emissions in all 9,960,292 corpus decisions;
  `../gen2-comparator-legs-2026-10-14/RESULTS.md` §Chatter floor).
  Silent is 746,121 of 996,112 val labels (74.9%).

PIN: `train_ppo_g2.PINS["init_clone"]` =
`artifacts/trunk-clone/trunk-clone.pt` (sha256
dbe912eb4e9ec3028fe5b02ca8de5da454fb9d00ac6470ff60b6fce464c5d430);
the launcher re-hashes it at launch. Critic and PPO launch stay
behind their own gates: probe-then-accept for the critic and the
PPO launch card, both on the owner's word.

### Regeneration

#### Collect (~6.2 h: 112 epochs × ~190 s; writes artifacts/trunk-clone/)

```
cd experiments/gen2-trunk-training-2026-10-18/trainer
caffeinate -s ../../exp-006-character-gen/.venv/bin/python -B train_clone_g2.py \
  --name trunk-clone \
  --data-root ../../gen2-collection-driver-2026-10-14/results-raw/full-100 \
  --consent-rows ../../gen2-collection-driver-2026-10-14/results-raw/consent-rows-full-100.json \
  > ../artifacts/trunk-clone-train.log 2>&1
```

#### Read (seconds; stdlib python3 only)

```
python3 - <<'EOF'
import json
m = json.load(open("experiments/gen2-trunk-training-2026-10-18/artifacts/trunk-clone/trunk-clone-metrics.json"))
assert m["params"] == 84450 and m["best_epoch"] == 102 and m["stopped_by"] == "plateau"
assert m["consent_swap_rows"] == 136699 and m["consent_unswappable_rows"] == 389
assert sorted(m["val_rollouts"]) == [f"r{i}3" for i in range(10)]
v = m["val"]
print({k: round(x, 4) for k, x in v.items()})
groups = {g: (round(d["accuracy"], 4), d["count"]) for g, d in m["activity_groups"].items()}
assert sum(c for _, c in groups.values()) == 996112
print(groups)
cc1 = next(c for c in m["activity_classes"] if c["name"] == "ChaseCritter1")
print("ChaseCritter1", cc1["count"], round(cc1["accuracy"], 4))
free = {c["name"]: c["count"] for c in m["message_classes"]
        if c["name"] in ("Mew", "Purr", "Chirp", "Trill", "Ekekek")}
assert set(free.values()) == {0}, free
sil = next(c for c in m["message_classes"] if c["name"] == "Silent")
print("Silent", sil["count"], round(sil["count"] / 996112, 3))
EOF
```
