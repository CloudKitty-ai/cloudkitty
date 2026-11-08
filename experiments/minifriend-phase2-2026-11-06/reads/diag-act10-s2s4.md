# Entry 29 (D): the two halted act10 seeds, dump-only

## s2: p2-act10-s2 tripped at u1149 on world 40002

| run | probes (fenced) | final u | max streak | streaks >= 10 by seat |
|---|---|---|---|---|
| p2-act10-s2 | 23 (23) | u1149 | 410 | {"Pumpkin": [410]} |
| p2-act15-s2 | 78 (78) | u3899 | 95 | {"Clementine": [58, 57], "Pumpkin": [95, 13], "Kittybear": [51]} |
| p2-nohead-s2 | 97 (97) | u4849 | 126 | {"Pumpkin": [88, 68, 33, 13], "Kittybear": [126]} |
| trunk-s2 | 52 (52) | u2599 | 195 | {"Clementine": [170, 125, 78, 43, 30, 28, 27, 26, 17], "Pumpkin": [86, 64, 20, 14, 10], "Miso": [195, 69, 19], "Kittybear": [45, 35]} |

Trip world 40002 at u1149 (trunk at u1149), per seat: first flag tick / flagged ticks / flags / hap min / applied eat / applied drink / moves / partnered / chow seen

| run | Pumpkin |
|---|---|
| p2-act10-s2 (n flagged 1, onset spread 0) | 225 / 410 / eat,drink,cuddle / 24.2 / 81 / 61 / 734 / 0.132 / 0.361 |
| p2-act15-s2 (n flagged 0, onset spread None) | None / 0 / - / 74.1 / 88 / 72 / 505 / 0.159 / 0.451 |
| p2-nohead-s2 (n flagged 0, onset spread None) | None / 0 / - / 73.7 / 91 / 96 / 412 / 0.188 / 0.504 |
| trunk-s2 (n flagged 0, onset spread None) | None / 0 / - / - / - / - / 645 / 0.162 / 0.454 |

Divergence (clean probe before vs trip probe, first tick proposals differ / ticks differ): {"Miso": [2, 1875], "Biscuit": [5, 1876], "Pumpkin": [22, 1836], "Kittybear": [16, 1868], "Clementine": [17, 1912]}

- p2-act10-s2 Pumpkin on 40002: probes with any own flag 1 of 23 (u:streak/hap min/chow mem/eat legal/eaten): u1149:410/24.2/0.451/189/81
- p2-act15-s2 Pumpkin on 40002: probes with any own flag 0 of 78 (u:streak/hap min/chow mem/eat legal/eaten): 
- p2-nohead-s2 Pumpkin on 40002: probes with any own flag 1 of 97 (u:streak/hap min/chow mem/eat legal/eaten): u899:68/45.9/0.627/188/72
- trunk-s2 Pumpkin on 40002: probes with any own flag 3 of 52 (u:streak/hap min/chow mem/eat legal/eaten): u99:10/-/0.796/132/- u249:86/-/0.721/112/- u699:5/-/0.774/161/-

## s4: p2-act10-s4 tripped at u3349 on world 40001

| run | probes (fenced) | final u | max streak | streaks >= 10 by seat |
|---|---|---|---|---|
| p2-act10-s4 | 67 (67) | u3349 | 1614 | {"Pumpkin": [1614, 188, 41, 11], "Clementine": [1399, 45, 42, 22], "Kittybear": [1508, 92], "Miso": [1429, 23], "Biscuit": [1518]} |
| p2-act15-s4 | 78 (78) | u3899 | 157 | {"Clementine": [157], "Pumpkin": [134, 67, 15], "Miso": [29], "Biscuit": [43]} |
| p2-nohead-s4 | 78 (78) | u3899 | 172 | {"Pumpkin": [82, 19, 17, 14], "Kittybear": [172]} |
| trunk-s4 | 52 (52) | u2599 | 217 | {"Clementine": [217, 41, 33, 29, 18, 18], "Miso": [172, 27], "Pumpkin": [202, 58, 29, 27, 14]} |

Trip world 40001 at u3349 (trunk at u2599), per seat: first flag tick / flagged ticks / flags / hap min / applied eat / applied drink / moves / partnered / chow seen

| run | Miso | Biscuit | Pumpkin | Kittybear | Clementine |
|---|---|---|---|---|---|
| p2-act10-s4 (n flagged 5, onset spread 215) | 571 / 1429 / eat,drink,sleep,play / 29.3 / 12 / 24 / 87 / 0.442 / 0.053 | 482 / 1518 / eat,drink,sleep,play / 26.9 / 3 / 16 / 78 / 0.506 / 0.034 | 386 / 1614 / eat,drink,play / 31.7 / 11 / 18 / 72 / 0.535 / 0.075 | 492 / 1508 / eat,drink / 32.1 / 6 / 31 / 38 / 0.536 / 0.037 | 601 / 1399 / eat,drink,sleep / 29.2 / 13 / 32 / 62 / 0.544 / 0.097 |
| p2-act15-s4 (n flagged 0, onset spread None) | None / 0 / - / 81.5 / 44 / 116 / 258 / 0.228 / 0.4 | None / 0 / - / 79.4 / 39 / 72 / 236 / 0.204 / 0.481 | None / 0 / - / 80.3 / 76 / 136 / 333 / 0.232 / 0.552 | None / 0 / - / 82.0 / 48 / 90 / 239 / 0.244 / 0.51 | None / 0 / - / 82.3 / 49 / 86 / 237 / 0.326 / 0.515 |
| p2-nohead-s4 (n flagged 0, onset spread None) | None / 0 / - / 78.5 / 56 / 100 / 305 / 0.259 / 0.435 | None / 0 / - / 82.8 / 68 / 88 / 247 / 0.22 / 0.479 | None / 0 / - / 75.6 / 85 / 94 / 394 / 0.234 / 0.508 | None / 0 / - / 80.8 / 67 / 78 / 267 / 0.222 / 0.555 | None / 0 / - / 78.7 / 51 / 96 / 228 / 0.317 / 0.472 |
| trunk-s4 (n flagged 0, onset spread None) | None / 0 / - / - / - / - / 400 / 0.201 / 0.407 | None / 0 / - / - / - / - / 291 / 0.226 / 0.446 | None / 0 / - / - / - / - / 454 / 0.189 / 0.484 | None / 0 / - / - / - / - / 305 / 0.198 / 0.467 | None / 0 / - / - / - / - / 427 / 0.231 / 0.512 |

Divergence (clean probe before vs trip probe, first tick proposals differ / ticks differ): {"Miso": [19, 1932], "Biscuit": [32, 1875], "Pumpkin": [36, 1854], "Kittybear": [29, 1924], "Clementine": [26, 1886]}

- p2-act10-s4 Miso on 40001: probes with any own flag 1 of 67 (u:streak/hap min/chow mem/eat legal/eaten): u3349:1429/29.3/0.082/23/12
- p2-act10-s4 Biscuit on 40001: probes with any own flag 1 of 67 (u:streak/hap min/chow mem/eat legal/eaten): u3349:1518/26.9/0.069/4/3
- p2-act10-s4 Pumpkin on 40001: probes with any own flag 3 of 67 (u:streak/hap min/chow mem/eat legal/eaten): u149:8/66.8/0.618/153/64 u349:41/56.3/0.635/226/77 u3349:1614/31.7/0.109/32/11
- p2-act10-s4 Kittybear on 40001: probes with any own flag 1 of 67 (u:streak/hap min/chow mem/eat legal/eaten): u3349:1508/32.1/0.054/31/6
- p2-act10-s4 Clementine on 40001: probes with any own flag 1 of 67 (u:streak/hap min/chow mem/eat legal/eaten): u3349:1399/29.2/0.117/22/13
- p2-act15-s4 Miso on 40001: probes with any own flag 0 of 78 (u:streak/hap min/chow mem/eat legal/eaten): 
- p2-act15-s4 Biscuit on 40001: probes with any own flag 0 of 78 (u:streak/hap min/chow mem/eat legal/eaten): 
- p2-act15-s4 Pumpkin on 40001: probes with any own flag 1 of 78 (u:streak/hap min/chow mem/eat legal/eaten): u1599:67/53.8/0.604/182/73
- p2-act15-s4 Kittybear on 40001: probes with any own flag 0 of 78 (u:streak/hap min/chow mem/eat legal/eaten): 
- p2-act15-s4 Clementine on 40001: probes with any own flag 0 of 78 (u:streak/hap min/chow mem/eat legal/eaten): 
- p2-nohead-s4 Miso on 40001: probes with any own flag 0 of 78 (u:streak/hap min/chow mem/eat legal/eaten): 
- p2-nohead-s4 Biscuit on 40001: probes with any own flag 0 of 78 (u:streak/hap min/chow mem/eat legal/eaten): 
- p2-nohead-s4 Pumpkin on 40001: probes with any own flag 1 of 78 (u:streak/hap min/chow mem/eat legal/eaten): u599:14/70.3/0.703/199/84
- p2-nohead-s4 Kittybear on 40001: probes with any own flag 1 of 78 (u:streak/hap min/chow mem/eat legal/eaten): u1949:172/47.4/0.531/116/52
- p2-nohead-s4 Clementine on 40001: probes with any own flag 0 of 78 (u:streak/hap min/chow mem/eat legal/eaten): 
- trunk-s4 Miso on 40001: probes with any own flag 0 of 52 (u:streak/hap min/chow mem/eat legal/eaten): 
- trunk-s4 Biscuit on 40001: probes with any own flag 0 of 52 (u:streak/hap min/chow mem/eat legal/eaten): 
- trunk-s4 Pumpkin on 40001: probes with any own flag 3 of 52 (u:streak/hap min/chow mem/eat legal/eaten): u99:3/-/0.762/111/- u1399:27/-/0.751/183/- u1699:58/-/0.688/163/-
- trunk-s4 Kittybear on 40001: probes with any own flag 0 of 52 (u:streak/hap min/chow mem/eat legal/eaten): 
- trunk-s4 Clementine on 40001: probes with any own flag 4 of 52 (u:streak/hap min/chow mem/eat legal/eaten): u49:3/-/0.769/132/- u99:18/-/0.729/75/- u199:33/-/0.684/82/- u349:7/-/0.687/86/-

Facts off the dumps; nothing scored, nothing selected (entry 29: the consequence is hers).
