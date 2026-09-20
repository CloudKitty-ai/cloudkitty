"""Guards for tier6_read.py: the count-6 cell reads tier 5's RECORDED battery (shallow-15 + sg15 arms,
when present on disk) through the same pooling tier5_read used, and the prediction checks on staged
aggregates. Run from the repo root: experiments/exp-006-character-gen/.venv/bin/python -B experiments/beam-world-screen-2026-09-19/test_tier6_read.py"""
from pathlib import Path
import screen_read as S, tier2_read as T, tier6_read as R

HERE = Path(__file__).resolve().parent
T5 = HERE / "results-raw" / "tier5" / "battery"
# a leg the driver is still writing (header + fewer than 30 rows, or empty) is skipped, not read
assert not R.complete(HERE / "fixtures" / "gen1-A-c0-eval-2x400.jsonl") and not R.complete(HERE / "nope.jsonl")
if (T5 / "shallow-15" / S.FILES["gen1-A"]).exists():
    assert R.complete(T5 / "shallow-15" / S.FILES["gen1-A"])
    out = R.read(HERE / "results-raw" / "tier6" / "battery", T5)
    c6 = out["counts"][6]
    _h, rows = S.load_rows(T5 / "shallow-15" / S.FILES["gen1-A"]); a = S.aggregate(rows)["pooled"]
    assert c6["reference"]["gen1-A"]["happiness"] == a["happiness"] and c6["reference"]["gen1-A"]["placement"] == a["start_dist"][0]
    swaps = sorted((T5 / "sg15-s1").glob("gen1-A_s?-sg15-s1-c0-eval-*.jsonl"))
    assert c6["arms"]["s1"]["swap_legs"] == 5 and c6["arms"]["s1"]["own_seat"] == T.arm_in_seat(swaps, "sg15-s1")
    assert c6["transfer"] == {}, "count 6 has no transfer read (the arms were trained there)"
    assert R.slot(6, 2) == "sg15-s2" and R.slot(7, 1) == "cnt7-s1"

# staged checks: welfare orders and the gain shrinks; frozen flat; placement kept; transfer holds except one cell
def cell(hap, nash, pl, cd, need=0.03, over=()):
    return {"happiness": hap, "nash_state": nash, "placement": pl, "conducted": cd, "need_lt5": need, "seeds_over_line": list(over)}
staged = {"counts": {}}
hap = {5: (90.2, 90.4), 6: (90.9, 91.1), 7: (91.3, 91.4), 8: (91.35, 91.45)}   # spreads 0.2 / 0.2 / 0.1 / 0.1; gains 0.7 / 0.35 / 0.05
for n in R.COUNTS:
    staged["counts"][n] = {"reference": {"gen1-A": {"happiness": 89.8 + 0.05 * n, "placement": 0.05, "nash_state": 0.9, "seeds_over_line": []},
                                         "scripted": {"happiness": 93.0, "placement": 0.30 + 0.02 * n}},
                           "arms": {f"s{s}": {"own_seat": {"placement": 0.3 + 0.05 * n}, "all_arm": cell(hap[n][s - 1], 0.90 + 0.002 * n + 0.001 * s, 0.3 + 0.05 * n, 0.30 - 0.02 * n)} for s in (1, 2)},
                           "transfer": {}}
for n in (5, 7, 8):
    for s in (1, 2):
        staged["counts"][n]["transfer"][f"s{s}"] = cell(hap[n][s - 1] + (0.3 if (n, s) != (8, 2) else 0.7), 0.9, 0.3 + 0.05 * n + 0.05, 0.2)
c = R.checks(staged)
p1 = c["P1_welfare_with_count"]
assert p1["orders_both_seeds"] and p1["nash_orders_both_seeds"] and p1["gain_shrinks"]
assert abs(p1["gain_5_6"] - 0.7) < 1e-9 and abs(p1["gain_7_8"] - 0.05) < 1e-9
assert p1["count8_within_1_of_floor0"] and p1["count5_over_1p5_under_floor0"]
assert p1["line"] == 7, p1   # 7->8 gain 0.05 sits inside count 7's spread 0.1; 6->7 (0.35) does not sit inside 0.2
# every gain past the spread -> the largest count, with the note
big = {n: (hap[n][0], hap[n][1] + 0.0) for n in R.COUNTS}; big[8] = (91.8, 91.9)
for n in R.COUNTS:
    for s in (1, 2):
        staged["counts"][n]["arms"][f"s{s}"]["all_arm"]["happiness"] = big[n][s - 1]
assert R.checks(staged)["P1_welfare_with_count"]["line"] == 8 and "largest" in R.checks(staged)["P1_welfare_with_count"]["line_note"]
for n in R.COUNTS:
    for s in (1, 2):
        staged["counts"][n]["arms"][f"s{s}"]["all_arm"]["happiness"] = hap[n][s - 1]
# one seed out of order breaks the ordering, not the line
staged["counts"][7]["arms"]["s2"]["all_arm"]["happiness"] = 91.0
c2 = R.checks(staged); assert not c2["P1_welfare_with_count"]["orders_both_seeds"]
staged["counts"][7]["arms"]["s2"]["all_arm"]["happiness"] = 91.4
p2 = c["P2_frozen_flat"]; assert abs(p2["gen1A_span"] - 0.15) < 1e-9 and p2["frozen_flat"] and p2["teacher_placement_rises"]
p3 = c["P3_placement"]; assert p3["all_kept"] and p3["placement_orders"] and p3["conducted_falls"]
p4 = c["P4_transfer"]; assert p4["7-s1"]["holds"] and not p4["8-s2"]["holds"] and p4["holds_everywhere"] is False   # 0.7 > 0.5 on hap
assert abs(p4["8-s2"]["hap_transfer_minus_retrained"] - 0.7) < 1e-9
# placement past the line fails a cell on its own
staged["counts"][5]["transfer"]["s1"]["placement"] = 0.3 + 0.25 + 0.11
assert not R.checks(staged)["P4_transfer"]["5-s1"]["holds"]
# a missing cell yields None, not a verdict
del staged["counts"][8]["arms"]["s2"]["all_arm"]
c3 = R.checks(staged); assert "orders_both_seeds" not in c3["P1_welfare_with_count"] and c3["P4_transfer"]["holds_everywhere"] is None
print("test_tier6_read ok")
