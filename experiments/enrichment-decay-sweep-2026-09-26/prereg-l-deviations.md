# PREREG-L deviations

1. (2026-10-04, erratum — noted, never edited into the frozen
   prereg) PREREG-L §Step 1 describes the replay verification as
   "verified tick-exact against its recorded battery row". The
   instrument's actual check (`tending_bands_replay.py` /
   `e_edges_replay.py` assert) compares the leg's five per-seat
   mean-happiness values at the recorded 4-decimal precision — a
   whole-trajectory checksum proxy, not a per-tick comparison. A
   diverging trajectory would almost surely move those means, but
   "tick-exact" overstates what is checked. RESULTS-L states the
   check as it is; caught by the accuracy gate's round-1 report.
