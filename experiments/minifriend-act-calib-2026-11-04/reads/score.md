# Act-head calibration read: score

```
{
 "score": {
  "P29": {
   "gap": 0.20019999999999993,
   "bar": 0.1,
   "met": true
  },
  "P30": {
   "auroc": 0.8599,
   "bar": 0.7,
   "met": true
  },
  "P31": {
   "gaps": {
    "seen": -0.00019999999999997797,
    "heard": 0.007900000000000018
   },
   "bar": 0.02,
   "met": true
  },
  "P32": {
   "gap": 0.010000000000000009,
   "per_seed": [
    0.010000000000000009,
    0.0,
    0.020000000000000018
   ],
   "bar": 0.1,
   "met": false
  }
 },
 "met": {
  "P29": true,
  "P30": true,
  "P31": true,
  "P32": false
 },
 "undecidable_registered_cells": [],
 "tempering_rule": "global",
 "tempering": {
  "B10-s1": {
   "adopted": "global",
   "worsened_cells": [],
   "T_frozen": 1.01,
   "ece": {
    "seen": {
     "T1": 0.007892662551447072,
     "global": 0.006935282184312718,
     "regime": 0.006036856479284147
    },
    "heard": {
     "T1": 0.011770967588250091,
     "global": 0.00794857000438079,
     "regime": 0.00794857000438079
    }
   }
  },
  "B10-s2": {
   "adopted": "T1",
   "worsened_cells": [
    "seen",
    "heard"
   ],
   "T_frozen": 1.0,
   "ece": {
    "seen": {
     "T1": 0.0018793068790198947,
     "global": 0.0026241276526191314,
     "regime": 0.0026241276526191314
    },
    "heard": {
     "T1": 0.008982809784286557,
     "global": 0.012542666708064963,
     "regime": 0.012542666708064963
    }
   }
  },
  "B10-s3": {
   "adopted": "global",
   "worsened_cells": [],
   "T_frozen": 1.02,
   "ece": {
    "seen": {
     "T1": 0.007318794336225193,
     "global": 0.004750712988750083,
     "regime": 0.0060019631612679885
    },
    "heard": {
     "T1": 0.0238215367491752,
     "global": 0.016150069993907078,
     "regime": 0.012778227425234467
    }
   }
  },
  "B30-s1": {
   "adopted": "T1",
   "worsened_cells": [
    "heard"
   ],
   "T_frozen": 1.0,
   "ece": {
    "seen": {
     "T1": 0.004657179713637306,
     "global": 0.0024602725476975318,
     "regime": 0.003122655126996846
    },
    "heard": {
     "T1": 0.005742690287561799,
     "global": 0.013168480065568252,
     "regime": 0.013168480065568252
    }
   }
  },
  "B30-s2": {
   "adopted": "global",
   "worsened_cells": [],
   "T_frozen": 1.0,
   "ece": {
    "seen": {
     "T1": 0.004732045128538575,
     "global": 0.004732045128538575,
     "regime": 0.0034392186569925137
    },
    "heard": {
     "T1": 0.009194605003004539,
     "global": 0.009194605003004539,
     "regime": 0.005513003691696709
    }
   }
  },
  "B30-s3": {
   "adopted": "global",
   "worsened_cells": [],
   "T_frozen": 1.0,
   "ece": {
    "seen": {
     "T1": 0.006954447765145849,
     "global": 0.006954447765145849,
     "regime": 0.006954447765145849
    },
    "heard": {
     "T1": 0.0095264476333833,
     "global": 0.0095264476333833,
     "regime": 0.0095264476333833
    }
   }
  }
 },
 "arm_view": {
  "B10": {
   "adopted_if_read_per_arm": "global",
   "worsened_cells": [],
   "ece": {
    "seen": {
     "T1": 0.0057,
     "global": 0.0048,
     "regime": 0.0049
    },
    "heard": {
     "T1": 0.0149,
     "global": 0.0122,
     "regime": 0.0111
    }
   }
  },
  "B30": {
   "adopted_if_read_per_arm": "T1",
   "worsened_cells": [
    "heard"
   ],
   "ece": {
    "seen": {
     "T1": 0.0054,
     "global": 0.0047,
     "regime": 0.0045
    },
    "heard": {
     "T1": 0.0082,
     "global": 0.0106,
     "regime": 0.0094
    }
   }
  }
 },
 "b20": "not registered in Phase 2 (P31 met; the rule as declared \u2014 RESULTS reports on its rationale)",
 "registered": [
  [
   "B10",
   "y0",
   "seen"
  ],
  [
   "B10",
   "y0",
   "heard"
  ],
  [
   "B30",
   "y0",
   "seen"
  ],
  [
   "B30",
   "y0",
   "heard"
  ]
 ]
}
```

