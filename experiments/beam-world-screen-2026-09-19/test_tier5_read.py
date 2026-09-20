"""Guards for tier5_read.py: the reference reader on a RECORDED leg (fixtures/gen1-A-c0-eval-2x400.jsonl)
and the prediction checks on staged aggregates. Run: python -B test_tier5_read.py"""
from pathlib import Path
import screen_read as S, tier5_read as R

HERE = Path(__file__).resolve().parent
f = HERE / "fixtures" / "gen1-A-c0-eval-2x400.jsonl"
r = R.ref(f); _h, rows = S.load_rows(f); a = S.aggregate(rows)["pooled"]
assert r["placement"] == a["start_dist"][0] and r["happiness"] == a["happiness"] and r["nash_state"] == a["nash_state"] and r["need_lt5"] == a["start_need_bins"][0]

# staged checks: floor 0 gen1-A at 92.3; a floor where the frozen roster drops 3.8 and the arms recover it
out = {"floor0": {"gen1-A": {"happiness": 92.3}},
       "floors": {20: {"reference": {"gen1-A": {"happiness": 88.5, "nash_state": 0.885, "sleep_share": 0.35, "start_need_mean": 20.4, "seeds_over_line": []}},
                       "arms": {"sg20-s1": {"own_seat": {"placement": 0.52}, "roster_with_arm": {"happiness": 92.4, "nash_state": 0.92, "seeds_over_line": []}},
                                "sg20-s2": {"own_seat": {"placement": 0.16}, "roster_with_arm": {"happiness": 91.0, "nash_state": 0.91, "seeds_over_line": [(1, 0, 200)]}}}},
                  25: {"reference": {"gen1-A": {"happiness": 87.2, "nash_state": 0.871, "sleep_share": 0.40, "start_need_mean": 24.8, "seeds_over_line": []}},
                       "arms": {"sg25-s1": {"own_seat": {"placement": 0.09}, "roster_with_arm": {"happiness": 88.0, "nash_state": 0.88, "seeds_over_line": []}},
                                "sg25-s2": {"own_seat": {"placement": 0.60}, "roster_with_arm": {"happiness": 92.0, "nash_state": 0.92, "seeds_over_line": []}}}}}}
c = R.checks(out)
assert c["P1_floor_felt"][20]["felt_over_0.3"] and abs(c["P1_floor_felt"][20]["gen1A_hap_drop"] - 3.8) < 1e-9
assert c["P2_placement"][20]["both_ge_keep"] and not c["P2_placement"][20]["both_lt_lose"]
assert not c["P2_placement"][25]["both_ge_keep"], "one seed under the keep line fails the floor"   # 0.09 < 0.15
assert c["P2_holds_at_20_and_25"] is False
assert c["P3_arms_vs_frozen"][20]["s1"]["recovers_floor_cost"] and not c["P3_arms_vs_frozen"][20]["s2"]["recovers_floor_cost"]   # 2.5 < 3.8
assert c["P5_over_line"][20]["s2"] == [(1, 0, 200)] and c["P5_over_line"][25]["s1"] == []
# an unreadable floor yields None, not a verdict
assert R.checks({"floor0": {"gen1-A": {"happiness": 92.3}}, "floors": {10: {"reference": {}, "arms": {}}}})["P2_holds_at_20_and_25"] is None
print("test_tier5_read ok")
