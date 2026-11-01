## Step 7 reads (360 worlds; 0 covered cat-ticks; pick (0.05, 2); 59 s)

First-episode status: {"T": {"tuning": {"H0": 25}, "confirming": {"H0": 25}}, "E": {"tuning": {"H2": 13, "H1": 24, "unreleased": 3}, "confirming": {"H2": 11, "H1": 23, "released_no_crossing": 1, "unreleased": 5}}, "N": {"tuning": {"H3": 45, "H2": 35, "H4": 32, "released_no_crossing": 3}, "confirming": {"H3": 64, "H2": 26, "released_no_crossing": 5, "H4": 20}}}

### R5 — the picked cell t0.05-B2 on the confirming half, beside the tuning half (flag: outside tuning ± 2 world-bootstrap SE, 2000 draws)

| group | primary | episodes conf / tun | detected conf / tun | SE band (tun) | flag | median latency conf / tun | in sight conf / tun | fog conf / tun | anticipated not at B conf / tun | SE band | flag | median lead not at B conf / tun |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E-H1 | yes | 23 / 24 | 0.489 ± 0.022 / 0.528 ± 0.091 | [0.3532, 0.7024] | - | 36.7 ± 17.7 / 2.0 ± 3.5 | 0.400 ± 0.029 / 0.528 ± 0.048 | 0.544 ± 0.018 / 0.528 ± 0.142 | 0.254 ± 0.082 / 0.392 ± 0.110 | [0.2421, 0.5427] | - | 38.0 ± 7.9 / 36.8 ± 9.4 |
| E-H2 | no | 11 / 13 | 0.386 ± 0.186 / 0.301 ± 0.139 | [0.0671, 0.5355] | - | 32.2 ± 54.0 / 29.2 ± 33.7 | 0.321 ± 0.095 / 0.354 ± 0.126 | 0.500 ± 0.375 / 0.217 ± 0.161 | 0.545 ± 0.120 / 0.474 ± 0.078 | [0.2627, 0.6861] | - | 62.8 ± 14.2 / 77.8 ± 1.0 |
| N-H2 | yes | 26 / 35 | 0.596 ± 0.092 / 0.536 ± 0.077 | [0.3756, 0.6958] | - | 23.7 ± 12.1 / 43.3 ± 12.3 | 0.582 ± 0.096 / 0.558 ± 0.077 | 0.612 ± 0.089 / 0.503 ± 0.100 | 0.253 ± 0.059 / 0.150 ± 0.047 | [0.0494, 0.2506] | FLAG | 30.0 ± 21.9 / 20.8 ± 9.3 |
| N-H3 | yes | 64 / 45 | 0.444 ± 0.110 / 0.459 ± 0.111 | [0.3216, 0.597] | - | 35.0 ± 26.7 / 15.8 ± 14.1 | 0.501 ± 0.072 / 0.485 ± 0.086 | 0.359 ± 0.169 / 0.421 ± 0.158 | 0.211 ± 0.077 / 0.232 ± 0.125 | [0.1192, 0.3438] | - | 35.2 ± 18.9 / 40.3 ± 12.5 |
| N-H4 | yes | 20 / 32 | 0.421 ± 0.134 / 0.409 ± 0.144 | [0.2531, 0.5647] | - | 2.3 ± 3.2 / 3.8 ± 6.6 | 0.429 ± 0.149 / 0.439 ± 0.118 | 0.405 ± 0.144 / 0.355 ± 0.202 | 0.275 ± 0.108 / 0.307 ± 0.098 | [0.1627, 0.4519] | - | 23.8 ± 6.7 / 42.2 ± 11.9 |
| T-H0 | yes | 25 / 25 | 1.000 ± 0.000 / 1.000 ± 0.000 | [1.0, 1.0] | - | 2.0 ± 0.0 / 2.0 ± 0.0 | - / - | - / - | - / - | - | - | - / - |

| arm | class | confirming per 10k | tuning per 10k | tuning SE | flag |
|---|---|---|---|---|---|
| T | scripted_before_first_mask | - | - | None | - |
| T | scripted_from_first_mask | 0.51 ± 0.12 | 0.91 ± 0.28 | 0.2846 | - |
| T | covered_friends | 0.07 ± 0.09 | 0.05 ± 0.06 | 0.0239 | - |
| E | scripted_before_first_mask | - | - | None | - |
| E | scripted_from_first_mask | 1.95 ± 0.39 | 3.39 ± 0.70 | 1.1434 | - |
| E | covered_friends | 1.02 ± 0.45 | 1.04 ± 0.44 | 0.3628 | - |
| N | scripted_before_first_mask | 0.38 ± 0.42 | 0.29 ± 0.26 | 0.1002 | - |
| N | scripted_from_first_mask | 1.47 ± 0.65 | 1.50 ± 0.63 | 0.1954 | - |
| N | covered_friends | 0.63 ± 0.23 | 0.71 ± 0.22 | 0.0639 | - |

Flags: [{'group': 'N-H2', 'column': 'anticipated_run_not_at_offset_B', 'tuning': 0.15, 'confirming': 0.2532, 'se': 0.0503}]

### R1 — tie-back (arm T reset episodes; P's same-seed covered figure beside)

| cell | scope | friend episodes (T / P) | length median (T / P) | T anywhere | T within 100 | P anywhere | P within 100 |
|---|---|---|---|---|---|---|---|
| t0.10-B0 | pooled | 50 / 50 | 23.5 / 40.0 | 1.000 ± 0.000 | 1.000 ± 0.000 | 0.995 ± 0.009 | 0.995 ± 0.009 |
| t0.10-B0 | T1 | 10 / 10 | 27.0 / 57.5 | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 |
| t0.10-B0 | T2 | 10 / 10 | 27.0 / 27.0 | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 |
| t0.10-B0 | T3 | 10 / 10 | 18.5 / 37.0 | 1.000 ± 0.000 | 1.000 ± 0.000 | 0.975 ± 0.043 | 0.975 ± 0.043 |
| t0.10-B0 | T4 | 10 / 10 | 16.5 / 41.5 | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 |
| t0.10-B0 | T5 | 10 / 10 | 35.0 / 32.0 | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 |
| t0.10-B2 | pooled | 50 / 50 | 23.5 / 40.0 | 1.000 ± 0.000 | 1.000 ± 0.000 | 0.980 ± 0.005 | 0.980 ± 0.005 |
| t0.10-B2 | T1 | 10 / 10 | 27.0 / 57.5 | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 |
| t0.10-B2 | T2 | 10 / 10 | 27.0 / 27.0 | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 |
| t0.10-B2 | T3 | 10 / 10 | 18.5 / 37.0 | 1.000 ± 0.000 | 1.000 ± 0.000 | 0.917 ± 0.014 | 0.917 ± 0.014 |
| t0.10-B2 | T4 | 10 / 10 | 16.5 / 41.5 | 1.000 ± 0.000 | 1.000 ± 0.000 | 0.983 ± 0.029 | 0.983 ± 0.029 |
| t0.10-B2 | T5 | 10 / 10 | 35.0 / 32.0 | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 |

Arm T worlds not grave at tick 0: 0; P worlds without a reset episode: 0

### R2 — history (first episodes, all seeds; splice comparators from DECLARATION §2; donors 5 / 40 / 238)

| group | primary | episodes (tun + conf) | H min/median/max | length min/q1/median/q3/max | edge need/hap | m 1/2/3/4 | det 0.10 B0 | lat | in sight | fog | det 0.10 B2 | det need-edge / hap-edge (B0) | splice |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E-H1 | yes | 47 (24 + 23) | 11.0/75.0/75.0 | 1/5.0/12.0/134.5/546 | 39/8 | 23/10/10/4 | 0.431 ± 0.043 | 25.3 ± 16.8 | 0.418 ± 0.053 | 0.439 ± 0.075 | 0.431 ± 0.043 | 0.410 ± 0.068 / 0.531 ± 0.083 | {'H50': 0.362, 'H10': 0.658, 'H20': 0.537} |
| E-H2 | no | 24 (13 + 11) | 100.0/100.0/217.0 | 1/2.75/7.5/28.5/393 | 24/0 | 18/3/3/0 | 0.306 ± 0.126 | 29.8 ± 45.7 | 0.294 ± 0.063 | 0.324 ± 0.231 | 0.306 ± 0.126 | 0.306 ± 0.126 / - | - |
| N-H2 | yes | 61 (35 + 26) | 113.0/217.0/290.0 | 1/14.0/105.0/225.0/813 | 55/6 | 15/17/10/19 | 0.490 ± 0.084 | 46.0 ± 4.4 | 0.514 ± 0.110 | 0.459 ± 0.072 | 0.490 ± 0.084 | 0.480 ± 0.077 / 0.583 ± 0.232 | {'H100': 0.358} |
| N-H3 | yes | 109 (45 + 64) | 300.0/507.0/1236.0 | 1/5.0/43.0/173.0/632 | 106/3 | 49/25/20/15 | 0.398 ± 0.094 | 37.2 ± 22.7 | 0.432 ± 0.063 | 0.349 ± 0.159 | 0.398 ± 0.094 | 0.390 ± 0.097 / 0.694 ± 0.048 | {'H500': 0.287} |
| N-H4 | yes | 52 (32 + 20) | 1278.0/2434.5/4498.0 | 1/6.5/33.0/126.5/668 | 47/5 | 23/17/7/5 | 0.370 ± 0.108 | 6.2 ± 6.5 | 0.403 ± 0.082 | 0.311 ± 0.156 | 0.370 ± 0.108 | 0.323 ± 0.115 / 0.817 ± 0.126 | {'H2000': 0.288} |
| T-H0 | yes | 50 (25 + 25) | 0.0/0.0/0.0 | 6/11.25/23.5/51.25/118 | -/- | - | 1.000 ± 0.000 | 0.3 ± 0.6 | - | - | 1.000 ± 0.000 | - / - | - |

E-H1 by the splice's bins (0.10 / B = 0): [10,20): 3 episodes, 0.083 ± 0.144; [20,50): 9 episodes, 0.546 ± 0.016; [50,100): 35 episodes, 0.431 ± 0.066 — splice H10 0.658, H20 0.537, H50 0.362

Mask-anchored version (§6 P10: the stratum set by the mask onset's offset instead of the crossing's; first episodes, 0.10 / B = 0): E-H0: 71 episodes, onsets [0, 0.0, 0], detected 0.389 ± 0.064; N-H0: 31 episodes, onsets [0, 0.0, 1], detected 0.352 ± 0.061; N-H1: 50 episodes, onsets [2, 20.5, 88], detected 0.472 ± 0.077; N-H2: 28 episodes, onsets [116, 205.5, 288], detected 0.408 ± 0.192; N-H3: 65 episodes, onsets [301, 520.0, 1142], detected 0.444 ± 0.076; N-H4: 48 episodes, onsets [1253, 2313.0, 4287], detected 0.371 ± 0.100

### R3 — anticipation (first episodes; runs starting inside [mask onset, crossing); leads from the first such run)

| group | cell | anticipated (all) | median lead | anticipated (not at B) | median lead | q1–q3 lead | detected without anticipation | never alarmed | per m: anticipated | per single masked need: anticipated |
|---|---|---|---|---|---|---|---|---|---|---|
| E-H1 | t0.10-B0 | 0.777 ± 0.382 | 62.3 ± 21.9 | 0.325 ± 0.037 | 45.3 ± 13.3 | 27.7 ± 15.1–64.2 ± 13.5 | 0.241 ± 0.052 | 0.434 ± 0.027 | m1 0.754 ± 0.427 (n 92), m2 0.775 ± 0.368 (n 40), m3 0.792 ± 0.361 (n 40), m4 0.875 ± 0.216 (n 16) | eat 0.717 ± 0.491 (n 20), drink 0.792 ± 0.361 (n 8), sleep 0.917 ± 0.144 (n 8), play 0.750 ± 0.433 (n 28), cuddle 0.726 ± 0.474 (n 28) |
| E-H1 | t0.05-B2 | 0.589 ± 0.161 | 55.0 ± 20.3 | 0.325 ± 0.093 | 37.2 ± 8.0 | 21.3 ± 8.2–50.8 ± 7.3 | 0.285 ± 0.069 | 0.390 ± 0.040 | m1 0.591 ± 0.196 (n 92), m2 0.683 ± 0.128 (n 40), m3 0.483 ± 0.167 (n 40), m4 0.604 ± 0.253 (n 16) | eat 0.450 ± 0.229 (n 20), drink 0.750 ± 0.331 (n 8), sleep 1.000 ± 0.000 (n 8), play 0.488 ± 0.238 (n 28), cuddle 0.631 ± 0.161 (n 28) |
| E-H2 | t0.10-B0 | 0.847 ± 0.265 | 93.7 ± 11.0 | 0.531 ± 0.055 | 76.7 ± 5.1 | 39.5 ± 25.0–96.7 ± 2.3 | 0.101 ± 0.048 | 0.368 ± 0.043 | m1 0.829 ± 0.297 (n 72), m2 1.000 ± 0.000 (n 12), m3 0.806 ± 0.337 (n 12) | eat 0.774 ± 0.392 (n 28), drink 0.708 ± 0.505 (n 8), sleep 1.000 ± 0.000 (n 24), play 0.694 ± 0.529 (n 12) |
| E-H2 | t0.05-B2 | 0.701 ± 0.112 | 90.3 ± 13.3 | 0.507 ± 0.089 | 67.7 ± 9.1 | 43.0 ± 20.6–87.0 ± 6.6 | 0.101 ± 0.048 | 0.392 ± 0.042 | m1 0.699 ± 0.150 (n 72), m2 0.778 ± 0.193 (n 12), m3 0.639 ± 0.193 (n 12) | eat 0.762 ± 0.273 (n 28), drink 0.292 ± 0.260 (n 8), sleep 0.833 ± 0.144 (n 24), play 0.556 ± 0.411 (n 12) |
| N-H2 | t0.10-B0 | 0.329 ± 0.152 | 105.2 ± 79.4 | 0.130 ± 0.035 | 27.5 ± 18.0 | 10.2 ± 4.8–40.1 ± 23.1 | 0.387 ± 0.066 | 0.484 ± 0.090 | m1 0.267 ± 0.176 (n 60), m2 0.324 ± 0.096 (n 68), m3 0.450 ± 0.263 (n 40), m4 0.320 ± 0.158 (n 76) | eat 0.194 ± 0.173 (n 12), drink 0.133 ± 0.116 (n 20), play 0.333 ± 0.289 (n 8), cuddle 0.417 ± 0.318 (n 20) |
| N-H2 | t0.05-B2 | 0.197 ± 0.040 | 28.3 ± 10.8 | 0.194 ± 0.044 | 27.0 ± 10.1 | 10.3 ± 3.8–43.2 ± 23.1 | 0.385 ± 0.051 | 0.421 ± 0.094 | m1 0.078 ± 0.042 (n 60), m2 0.240 ± 0.084 (n 68), m3 0.258 ± 0.163 (n 40), m4 0.219 ± 0.141 (n 76) | eat 0.306 ± 0.268 (n 12), drink 0.017 ± 0.029 (n 20), play 0.000 ± 0.000 (n 8), cuddle 0.033 ± 0.029 (n 20) |
| N-H3 | t0.10-B0 | 0.188 ± 0.074 | 44.8 ± 23.4 | 0.164 ± 0.091 | 32.3 ± 16.6 | 15.4 ± 11.1–61.0 ± 24.6 | 0.262 ± 0.011 | 0.574 ± 0.101 | m1 0.133 ± 0.075 (n 196), m2 0.240 ± 0.125 (n 100), m3 0.221 ± 0.038 (n 80), m4 0.239 ± 0.107 (n 60) | eat 0.226 ± 0.074 (n 28), drink 0.103 ± 0.089 (n 52), sleep 0.300 ± 0.434 (n 40), play 0.000 ± 0.000 (n 40), cuddle 0.031 ± 0.054 (n 32), bath 0.333 ± 0.382 (n 4) |
| N-H3 | t0.05-B2 | 0.219 ± 0.096 | 36.5 ± 15.2 | 0.219 ± 0.096 | 36.5 ± 15.2 | 17.0 ± 3.5–71.5 ± 20.6 | 0.258 ± 0.015 | 0.522 ± 0.107 | m1 0.122 ± 0.125 (n 196), m2 0.307 ± 0.122 (n 100), m3 0.317 ± 0.089 (n 80), m4 0.261 ± 0.118 (n 60) | eat 0.214 ± 0.186 (n 28), drink 0.006 ± 0.011 (n 52), sleep 0.383 ± 0.513 (n 40), play 0.000 ± 0.000 (n 40), cuddle 0.031 ± 0.054 (n 32), bath 0.333 ± 0.382 (n 4) |
| N-H4 | t0.10-B0 | 0.210 ± 0.063 | 29.7 ± 4.5 | 0.210 ± 0.063 | 29.7 ± 4.5 | 18.5 ± 3.1–58.2 ± 26.7 | 0.191 ± 0.051 | 0.599 ± 0.113 | m1 0.112 ± 0.120 (n 92), m2 0.172 ± 0.086 (n 68), m3 0.524 ± 0.083 (n 28), m4 0.350 ± 0.132 (n 20) | eat 0.167 ± 0.144 (n 20), drink 0.042 ± 0.072 (n 8), sleep 0.250 ± 0.433 (n 24), play 0.042 ± 0.072 (n 16), cuddle 0.000 ± 0.000 (n 20), bath 0.000 ± 0.000 (n 4) |
| N-H4 | t0.05-B2 | 0.295 ± 0.099 | 37.8 ± 10.1 | 0.295 ± 0.099 | 37.8 ± 10.1 | 18.8 ± 2.1–64.7 ± 23.1 | 0.168 ± 0.058 | 0.537 ± 0.134 | m1 0.210 ± 0.130 (n 92), m2 0.245 ± 0.114 (n 68), m3 0.595 ± 0.149 (n 28), m4 0.433 ± 0.058 (n 20) | eat 0.400 ± 0.250 (n 20), drink 0.125 ± 0.216 (n 8), sleep 0.306 ± 0.529 (n 24), play 0.083 ± 0.096 (n 16), cuddle 0.050 ± 0.087 (n 20), bath 0.167 ± 0.289 (n 4) |

Mean probe logit aligned to the crossing (offset 0 = the crossing), from the mask onset, over observer-episodes (n at each offset in parentheses):

| group | -100 | -50 | -20 | -10 | -5 | -2 | -1 | 0 | 1 | 2 | 5 | 10 | 20 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E-H1 | nan (0) | -4.41 (35) | -4.91 (44) | -5.11 (47) | -5.16 (47) | -5.13 (47) | -5.12 (47) | -5.11 (47) | -5.08 (47) | -5.08 (47) | -5.08 (47) | -5.14 (47) | -5.45 (47) |
| E-H2 | -2.73 (24) | -4.67 (24) | -5.48 (24) | -5.61 (24) | -5.69 (24) | -5.65 (24) | -5.60 (24) | -5.59 (24) | -5.54 (24) | -5.54 (24) | -5.61 (24) | -5.81 (24) | -6.01 (24) |
| N-H2 | -8.43 (60) | -7.04 (61) | -6.36 (61) | -6.14 (61) | -6.04 (61) | -5.95 (61) | -5.93 (61) | -5.92 (61) | -5.89 (61) | -5.88 (61) | -5.78 (61) | -5.70 (61) | -5.54 (61) |
| N-H3 | -7.60 (94) | -7.04 (109) | -6.39 (109) | -6.18 (109) | -6.05 (109) | -5.98 (109) | -5.94 (109) | -5.96 (109) | -5.95 (109) | -5.95 (109) | -5.96 (109) | -6.01 (109) | -6.06 (109) |
| N-H4 | -7.69 (50) | -6.51 (52) | -5.87 (52) | -5.79 (52) | -5.67 (52) | -5.58 (52) | -5.52 (52) | -5.47 (52) | -5.45 (52) | -5.43 (52) | -5.39 (52) | -5.43 (52) | -5.44 (52) |

P6 read (arm N first episodes, m = 1, hidden need, in sight at the crossing; 0.10 / B = 0): single-need hidden-need first episodes 85, of them with at least one observer in sight at the crossing 74 (194 observer-episodes per seed); pooled majority 0.153 ± 0.012, padded median lead -1.0 ± 0.0; per stratum H2: majority 0.265 ± 0.179, padded median lead -1.0 ± 0.0 (n obs-episodes 34); H3: majority 0.131 ± 0.020, padded median lead -1.0 ± 0.0 (n obs-episodes 104); H4: majority 0.125 ± 0.095, padded median lead -1.0 ± 0.0 (n obs-episodes 56)

### R6 — which need (the scripted friend's grave samples in sight; argmax of the five predicted means)

| arm | samples (seed 1) | names a masked need | names a need at 90 | per single masked need (samples, accuracy) |
|---|---|---|---|---|
| T | 2240 | - | 0.803 ± 0.055 | - |
| E | 30648 | 0.780 ± 0.026 | 0.831 ± 0.026 | cuddle (2032, 0.633 ± 0.129), eat (521, 0.432 ± 0.068), play (20, -), sleep (319, 1.000 ± 0.000) |
| N | 396818 | 0.771 ± 0.018 | 0.805 ± 0.022 | play (3940, 0.498 ± 0.076), cuddle (16233, 0.629 ± 0.094), eat (7189, 0.872 ± 0.019), sleep (13595, 0.966 ± 0.007), drink (9729, 0.720 ± 0.128) |

### R7 — later episodes (ordinal 2 and up), by the gap since the last release; never pooled with first episodes

| arm | gap band | episodes | length median | H since onset median | in sight share | det 0.10 B0 | lat | det pick | lat |
|---|---|---|---|---|---|---|---|---|---|
| E | [300,600) | 9 | 10.0 | 118.0 | 0.92 | 0.176 ± 0.058 | 6.5 ± 3.1 | 0.204 ± 0.058 | 2.3 ± 3.2 |
| N | [300,600) | 323 | 42.0 | 176.0 | 0.61 | 0.420 ± 0.089 | 33.3 ± 21.5 | 0.473 ± 0.093 | 19.0 ± 18.0 |
| N | [600,900) | 337 | 37.0 | 182.0 | 0.59 | 0.426 ± 0.104 | 32.3 ± 23.2 | 0.470 ± 0.101 | 21.7 ± 20.6 |
| N | [900,1201) | 260 | 30.5 | 176.5 | 0.62 | 0.420 ± 0.108 | 38.7 ± 34.1 | 0.477 ± 0.103 | 23.7 ± 23.9 |

arm E: 31 later windows, 9 released with a crossing, 22 unreleased at the world's end
arm N: 1049 later windows, 920 released with a crossing, 74 unreleased at the world's end

### R8 — price (covered seats)

| arm | half | worlds | covered mean happiness (mean / SD / min) | distress ticks per 1,000 covered cat-ticks | grave ticks per 1,000 | worst covered streak median / max | worlds with covered grave | scripted grave ticks mean |
|---|---|---|---|---|---|---|---|---|
| T | tuning | 25 | 87.36 / 0.25 / 86.99 | 0.01 | 0.01 | 0.0 / 4 | 1 | 48.8 |
| T | confirming | 25 | 87.36 / 0.24 / 86.89 | 0.00 | 0.00 | 0.0 / 0 | 0 | 38.7 |
| T | pooled | 50 | 87.36 / 0.24 / 86.89 | 0.01 | 0.01 | 0.0 / 4 | 1 | 43.8 |
| E | tuning | 40 | 86.50 / 1.72 / 79.45 | 4.52 | 4.93 | 0.0 / 125 | 5 | 115.2 |
| E | confirming | 40 | 86.37 / 2.25 / 78.01 | 5.55 | 6.11 | 0.0 / 375 | 7 | 178.6 |
| E | pooled | 80 | 86.43 / 1.99 / 78.01 | 5.04 | 5.52 | 0.0 / 375 | 12 | 146.9 |
| N | tuning | 115 | 86.47 / 0.59 / 84.74 | 3.37 | 3.75 | 11.0 / 514 | 68 | 645.2 |
| N | confirming | 115 | 86.40 / 0.85 / 82.34 | 4.82 | 5.27 | 14.0 / 487 | 73 | 644.3 |
| N | pooled | 230 | 86.43 / 0.73 / 82.34 | 4.10 | 4.51 | 13.0 / 514 | 141 | 644.7 |

Refused proposals toward the scripted friend (a covered seat's chosen menu action naming the friend, not applied as proposed), per 1,000 covered cat-ticks:

| arm | half | asks toward friend | refused | by the mask | other | refused share of asks | refused by family | worlds with over 100 refusals |
|---|---|---|---|---|---|---|---|---|
| T | tuning | 102.44 | 24.027 | 0.0 | 24.027 | 0.235 | {'Chase': 5114, 'Groom': 340, 'Play': 3826, 'RestWith': 226, 'SleepWith': 105} | 25 |
| T | confirming | 101.568 | 23.228 | 0.0 | 23.228 | 0.229 | {'Chase': 4858, 'Groom': 339, 'Play': 3716, 'RestWith': 280, 'SleepWith': 98} | 25 |
| T | pooled | 102.004 | 23.627 | 0.0 | 23.627 | 0.232 | {'Chase': 9972, 'Groom': 679, 'Play': 7542, 'RestWith': 506, 'SleepWith': 203} | 50 |
| E | tuning | 137.469 | 68.25 | 47.188 | 21.062 | 0.496 | {'Chase': 1377, 'Groom': 4227, 'Play': 1858, 'RestWith': 981, 'SleepWith': 293} | 23 |
| E | confirming | 143.586 | 75.195 | 54.555 | 20.641 | 0.524 | {'Chase': 1360, 'Groom': 5074, 'Play': 2175, 'RestWith': 747, 'SleepWith': 269} | 28 |
| E | pooled | 140.527 | 71.723 | 50.871 | 20.852 | 0.51 | {'Chase': 2737, 'Groom': 9301, 'Play': 4033, 'RestWith': 1728, 'SleepWith': 562} | 51 |
| N | tuning | 130.451 | 59.437 | 36.591 | 22.846 | 0.456 | {'Chase': 31982, 'Groom': 74612, 'Play': 40175, 'RestWith': 12498, 'SleepWith': 4778} | 115 |
| N | confirming | 131.137 | 59.747 | 36.821 | 22.926 | 0.456 | {'Chase': 32665, 'Groom': 73472, 'Play': 41728, 'RestWith': 11772, 'SleepWith': 5265} | 115 |
| N | pooled | 130.794 | 59.592 | 36.706 | 22.886 | 0.456 | {'Chase': 64647, 'Groom': 148084, 'Play': 81903, 'RestWith': 24270, 'SleepWith': 10043} | 230 |

Covered scout pairs (needy minus teacher, covered seats): 
- arm N (10 pairs): mean happiness -0.876 ± 0.404 (min -1.495, max -0.313); distress ticks 122.1 per world; grave ticks 129.8; refused asks toward the friend, teacher vs needy worlds [5823, 13692], of the needy worlds' 8555 attributed to the mask
- arm E (10 pairs): mean happiness -0.222 ± 2.444 (min -3.109, max 6.061); distress ticks -40.1 per world; grave ticks -40.0; refused asks toward the friend, teacher vs needy worlds [707, 2321], of the needy worlds' 1672 attributed to the mask

### Predictions (§6), on all seeds

- P7: within-100 reset detection 1.000 against the bar 0.986 → MET (anywhere 1.000; P's same-seed covered within-100 0.995)
- P10: clause 1 anywhere 1.000 ≥ 0.986 → True; clause 2 H2 0.490 vs 0.358 ± 0.175 → True; H3 0.398 vs 0.287 ± 0.143 → True; H4 0.370 vs 0.288 ± 0.132 → True → MET
- P11: E-H1 0.431 in [0.292, 0.432] → MET; above the splice's H50 0.362: True; by bin {'[10,20)': 0.0833, '[20,50)': 0.5463, '[50,100)': 0.431}; by edge {'need': {'mean': 0.4103, 'sd': 0.0678, 'n_seeds': 3}, 'happiness': {'mean': 0.5312, 'sd': 0.0827, 'n_seeds': 3}}
- P6: eligible 85 friend episodes; majority 0.153 (> 0.5?), padded median lead -1.0 (≥ 20?) → NOT MET; per stratum {'H2': {'majority': 0.2647, 'median_lead_padded': -1.0, 'met': False}, 'H3': {'majority': 0.1314, 'median_lead_padded': -1.0, 'met': False}, 'H4': {'majority': 0.125, 'median_lead_padded': -1.0, 'met': False}}

