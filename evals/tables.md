
**dev** (n=39)

| Gate | TP | FP | FN | TN | Precision | Recall | F1 | Flag rate |
|---|---|---|---|---|---|---|---|---|
| v1 (starter gate) | 11 | 1 | 8 | 19 | 0.917 | 0.579 | 0.71 | 0.308 |
| v2 (verify-copy, tuned on dev) | 18 | 0 | 1 | 20 | 1.0 | 0.947 | 0.973 | 0.462 |
| stop-slop presence ban-list | 10 | 13 | 9 | 7 | 0.435 | 0.526 | 0.476 | 0.59 |
| always rewrite (always-on skill as gate) | 19 | 20 | 0 | 0 | 0.487 | 1.0 | 0.655 | 1.0 |

**holdout** (n=34)

| Gate | TP | FP | FN | TN | Precision | Recall | F1 | Flag rate |
|---|---|---|---|---|---|---|---|---|
| v1 (starter gate) | 8 | 1 | 8 | 17 | 0.889 | 0.5 | 0.64 | 0.265 |
| v2 (verify-copy, tuned on dev) | 15 | 0 | 1 | 18 | 1.0 | 0.938 | 0.968 | 0.441 |
| stop-slop presence ban-list | 12 | 13 | 4 | 5 | 0.48 | 0.75 | 0.585 | 0.735 |
| always rewrite (always-on skill as gate) | 16 | 18 | 0 | 0 | 0.471 | 1.0 | 0.64 | 1.0 |

**stress** (n=12)

| Gate | TP | FP | FN | TN | Precision | Recall | F1 | Flag rate |
|---|---|---|---|---|---|---|---|---|
| v1 (starter gate) | 0 | 0 | 8 | 4 | 0.0 | 0.0 | 0.0 | 0.0 |
| v2 (verify-copy, tuned on dev) | 0 | 0 | 8 | 4 | 0.0 | 0.0 | 0.0 | 0.0 |
| stop-slop presence ban-list | 6 | 4 | 2 | 0 | 0.6 | 0.75 | 0.667 | 0.833 |
| always rewrite (always-on skill as gate) | 8 | 4 | 0 | 0 | 0.667 | 1.0 | 0.8 | 1.0 |

**all** (n=85)

| Gate | TP | FP | FN | TN | Precision | Recall | F1 | Flag rate |
|---|---|---|---|---|---|---|---|---|
| v1 (starter gate) | 19 | 2 | 24 | 40 | 0.905 | 0.442 | 0.594 | 0.247 |
| v2 (verify-copy, tuned on dev) | 33 | 0 | 10 | 42 | 1.0 | 0.767 | 0.868 | 0.388 |
| stop-slop presence ban-list | 28 | 30 | 15 | 12 | 0.483 | 0.651 | 0.554 | 0.682 |
| always rewrite (always-on skill as gate) | 43 | 42 | 0 | 0 | 0.506 | 1.0 | 0.672 | 1.0 |

**Per category, dev+holdout combined (correct / n)**

| Gate | classic | residual55 | structural | clean | overcorrection |
|---|---|---|---|---|---|
| v1 (starter gate) | 13/13 | 5/13 | 1/9 | 21/21 | 15/17 |
| v2 (verify-copy, tuned on dev) | 13/13 | 13/13 | 7/9 | 21/21 | 17/17 |
| stop-slop presence ban-list | 10/13 | 10/13 | 2/9 | 12/21 | 0/17 |
