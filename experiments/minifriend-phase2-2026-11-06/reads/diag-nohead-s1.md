# Entry 25 — the p2-nohead-s1 streak, read off the halted run's own probe dump (probe-u399)

World 40001, kitty_3 (Pumpkin), ticks 873–1235 = 363 ticks (recorded per world [363, 0, 0]; nash at the stop 0.8923). Flag ticks by need in the window: eat 363, drink 48. Happiness min 48.6.

| stretch | ticks | eat legal ticks | mean legal acts | eat proposed (when legal) | moves proposed | chow in memory | chow in sight | partnered | top proposals |
|---|---|---|---|---|---|---|---|---|---|
| before | 173 | 1 | 8.05 | 1 (1) | 46 | 0.133 | 0.133 | 0.22 | play_solo 28, play_critter_0 25, rest_with_kitty_2 18, move_north 14 |
| window | 363 | 1 | 4.79 | 1 (1) | 21 | 0.011 | 0.011 | 0.088 | play_solo 252, sleep_with_kitty_3 40, play_critter_0 40, move_north 6 |
| after | 165 | 12 | 8.19 | 7 (7) | 26 | 0.648 | 0.473 | 0.17 | play_critter_0 20, chase_critter_0 18, move_south 13, sleep_solo 13 |

Window needs mean: eat 99.8, drink 52.8, sleep 22.1, play 0.8, cuddle 14.6, bath 14.2; messages: silent 316, want_eat 32, want_bath 10, here_sunbeam 2, here_food 1, here_water 1, here_critter 1; activity: idle 180, playing 146, sleeping 35, drinking 2; here_food heard (share of ticks, per row) [0.24, 0.325, 0.488, 0.496]; rows present [0.0, 0.0, 0.094, 0.38].

Others on the world in the window: Miso: ate 12 ticks, eat need 13.1, hap min 83.8; Biscuit: ate 15 ticks, eat need 9.0, hap min 85.2; Kittybear: ate 17 ticks, eat need 15.5, hap min 78.3; Clementine: ate 12 ticks, eat need 16.3, hap min 81.5

| contrast (same kitty / world / window) | flagged ticks (world) | longest run | eat legal ticks | mean legal | chow memory | partnered | top proposals |
|---|---|---|---|---|---|---|---|
| probe-u349 | 0 | 0 | 34 | 9.0 | 0.609 | 0.273 | play_critter_0 44, play_kitty_2 31, rest_with_kitty_2 24, play_kitty_1 22 |
| probe-u299 | 0 | 0 | 33 | 8.66 | 0.862 | 0.187 | play_critter_0 73, play_kitty_0 26, move_east 25, chase_critter_0 24 |
| probe-u199 | 0 | 0 | 31 | 8.36 | 0.647 | 0.262 | rest_with_kitty_3 56, play_solo 40, play_kitty_3 38, play_critter_0 37 |
| trunk-s1 probe-u2599 | 0 | 0 | 28 | 9.45 | 0.689 | 0.218 | play_solo 49, move_west 32, rest_with_kitty_3 31, move_east 29 |

| whole probe (3 worlds × 2,000 × 5) | play_solo | solo | partner | eat | eat when legal | eat legal | moves | mean legal |
|---|---|---|---|---|---|---|---|---|
| trunk-s1 probe-u2599 | 0.09 | 0.292 | 0.416 | 0.021 | 0.299 | 0.072 | 0.175 | 8.7 |
| p2-nohead-s1 probe-u349 | 0.087 | 0.357 | 0.331 | 0.026 | 0.341 | 0.076 | 0.165 | 8.07 |
| p2-nohead-s1 probe-u399 | 0.122 | 0.398 | 0.289 | 0.027 | 0.378 | 0.073 | 0.161 | 7.47 |
| p2-act15-s1 probe-u399 | 0.086 | 0.308 | 0.402 | 0.026 | 0.362 | 0.073 | 0.157 | 8.0 |
| p2-act15-s1 probe-u599 | 0.09 | 0.37 | 0.345 | 0.028 | 0.364 | 0.078 | 0.149 | 7.78 |
| p2-act10-s1 probe-u399 | 0.153 | 0.392 | 0.32 | 0.027 | 0.363 | 0.075 | 0.159 | 7.56 |
| p2-act10-s1 probe-u599 | 0.064 | 0.356 | 0.352 | 0.026 | 0.379 | 0.068 | 0.151 | 7.84 |
