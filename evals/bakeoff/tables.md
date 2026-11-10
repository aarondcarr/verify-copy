
### Holdout (n=34: 16 slop, 18 clean incl. 8 over-correction traps)

| Model | System | Slop drafts rewritten | Clean drafts touched | Rewrite-decision P / R / F1 | Residual slop: v2 | Residual slop: Opus judge | Residual slop: Sonnet judge | Slop fixed AND meaning kept (both judges) | Clean drafts harmed (Opus / Sonnet judge) | Meaning kept on changed outputs (Opus / Sonnet judge) | Cost (USD) | Cost per 1k drafts (extrapolated) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Haiku 5.5 | 1 Model default | 11/16 | 5/18 | 0.69 / 0.69 / 0.69 | 13/16 | 14/16 | 15/16 | 1/16 | 2/18 / 3/18 | 10/16 / 9/16 | $0.0058 | $0.17 |
| Haiku 5.5 | 2 Style contract | 16/16 | 6/18 | 0.73 / 1.00 / 0.84 | 6/16 | 5/16 | 5/16 | 7/16 | 2/18 / 2/18 | 14/22 / 16/22 | $0.0069 | $0.20 |
| Haiku 5.5 | 3 Always-on skill | 15/16 | 0/18 | 1.00 / 0.94 / 0.97 | 5/16 | 4/16 | 8/16 | 7/16 | 0/18 / 0/18 | 14/15 / 12/15 | $0.0095 | $0.28 |
| Haiku 5.5 | 4 Gate (v2 regex) | 14/16 | 0/18 | 1.00 / 0.88 / 0.93 | 5/16 | 5/16 | 7/16 | 6/16 | 0/18 / 0/18 | 11/14 / 11/14 | $0.0049 | $0.14 |
| Haiku 5.5 | 4b Gate (v2 + Haiku) | 15/16 | 0/18 | 1.00 / 0.94 / 0.97 | 5/16 | 4/16 | 7/16 | 8/16 | 0/18 / 0/18 | 15/15 / 14/15 | $0.0067 | $0.20 |
| Sonnet 5.5 | 1 Model default | 8/16 | 1/18 | 0.89 / 0.50 / 0.64 | 13/16 | 14/16 | 15/16 | 1/16 | 1/18 / 0/18 | 9/9 / 8/9 | $0.0578 | $1.70 |
| Sonnet 5.5 | 2 Style contract | 16/16 | 1/18 | 0.94 / 1.00 / 0.97 | 6/16 | 5/16 | 5/16 | 8/16 | 0/18 / 0/18 | 14/17 / 15/17 | $0.0786 | $2.31 |
| Sonnet 5.5 | 3 Always-on skill | 16/16 | 1/18 | 0.94 / 1.00 / 0.97 | 3/16 | 4/16 | 5/16 | 10/16 | 0/18 / 1/18 | 17/17 / 16/17 | $0.1753 | $5.16 |
| Sonnet 5.5 | 4 Gate (v2 regex) | 15/16 | 0/18 | 1.00 / 0.94 / 0.97 | 2/16 | 4/16 | 5/16 | 10/16 | 0/18 / 0/18 | 15/15 / 13/15 | $0.0964 | $2.84 |
| Sonnet 5.5 | 4b Gate (v2 + Haiku) | 16/16 | 0/18 | 1.00 / 1.00 / 1.00 | 3/16 | 5/16 | 6/16 | 10/16 | 0/18 / 0/18 | 15/16 / 15/16 | $0.0975 | $2.87 |
| Opus 5.5 | 1 Model default | 14/16 | 2/18 | 0.88 / 0.88 / 0.88 | 8/16 | 9/16 | 10/16 | 5/16 | 0/18 / 0/18 | 14/16 / 16/16 | $0.1602 | $4.71 |
| Opus 5.5 | 2 Style contract | 16/16 | 3/18 | 0.84 / 1.00 / 0.91 | 2/16 | 3/16 | 5/16 | 9/16 | 0/18 / 2/18 | 19/19 / 16/19 | $0.1750 | $5.15 |
| Opus 5.5 | 3 Always-on skill | 16/16 | 1/18 | 0.94 / 1.00 / 0.97 | 2/16 | 1/16 | 4/16 | 12/16 | 0/18 / 1/18 | 17/17 / 15/17 | $0.3695 | $10.87 |
| Opus 5.5 | 4 Gate (v2 regex) | 15/16 | 0/18 | 1.00 / 0.94 / 0.97 | 3/16 | 4/16 | 6/16 | 9/16 | 0/18 / 0/18 | 15/15 / 14/15 | $0.1879 | $5.53 |
| Opus 5.5 | 4b Gate (v2 + Haiku) | 16/16 | 0/18 | 1.00 / 1.00 / 1.00 | 2/16 | 2/16 | 4/16 | 11/16 | 0/18 / 0/18 | 16/16 / 14/16 | $0.1910 | $5.62 |

### Hard cases (n=12: 8 unseen-vocabulary slop, 4 long clean)

| Model | System | Slop drafts rewritten | Clean drafts touched | Rewrite-decision P / R / F1 | Residual slop: v2 | Residual slop: Opus judge | Residual slop: Sonnet judge | Slop fixed AND meaning kept (both judges) | Clean drafts harmed (Opus / Sonnet judge) | Meaning kept on changed outputs (Opus / Sonnet judge) | Cost (USD) | Cost per 1k drafts (extrapolated) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Haiku 5.5 | 1 Model default | 6/8 | 2/4 | 0.75 / 0.75 / 0.75 | 0/8 | 6/8 | 7/8 | 0/8 | 2/4 / 2/4 | 4/8 / 5/8 | $0.0029 | $0.24 |
| Haiku 5.5 | 2 Style contract | 8/8 | 3/4 | 0.73 / 1.00 / 0.84 | 0/8 | 2/8 | 5/8 | 1/8 | 2/4 / 2/4 | 7/11 / 7/11 | $0.0030 | $0.25 |
| Haiku 5.5 | 3 Always-on skill | 8/8 | 0/4 | 1.00 / 1.00 / 1.00 | 0/8 | 1/8 | 4/8 | 2/8 | 0/4 / 0/4 | 6/8 / 6/8 | $0.0039 | $0.32 |
| Haiku 5.5 | 4 Gate (v2 regex) | 0/8 | 0/4 | n/a / 0.00 / n/a | 0/8 | 8/8 | 8/8 | 0/8 | 0/4 / 0/4 | n/a / n/a | $0.0000 | $0.00 |
| Haiku 5.5 | 4b Gate (v2 + Haiku) | 8/8 | 0/4 | 1.00 / 1.00 / 1.00 | 0/8 | 4/8 | 4/8 | 2/8 | 0/4 / 0/4 | 6/8 / 6/8 | $0.0032 | $0.26 |
| Sonnet 5.5 | 1 Model default | 7/8 | 0/4 | 1.00 / 0.88 / 0.93 | 0/8 | 6/8 | 6/8 | 1/8 | 0/4 / 0/4 | 6/7 / 6/7 | $0.0311 | $2.59 |
| Sonnet 5.5 | 2 Style contract | 8/8 | 0/4 | 1.00 / 1.00 / 1.00 | 0/8 | 0/8 | 4/8 | 3/8 | 0/4 / 0/4 | 7/8 / 8/8 | $0.0378 | $3.15 |
| Sonnet 5.5 | 3 Always-on skill | 8/8 | 0/4 | 1.00 / 1.00 / 1.00 | 0/8 | 4/8 | 5/8 | 2/8 | 0/4 / 0/4 | 8/8 / 7/8 | $0.0718 | $5.98 |
| Sonnet 5.5 | 4 Gate (v2 regex) | 0/8 | 0/4 | n/a / 0.00 / n/a | 0/8 | 8/8 | 8/8 | 0/8 | 0/4 / 0/4 | n/a / n/a | $0.0000 | $0.00 |
| Sonnet 5.5 | 4b Gate (v2 + Haiku) | 8/8 | 0/4 | 1.00 / 1.00 / 1.00 | 0/8 | 2/8 | 4/8 | 4/8 | 0/4 / 0/4 | 8/8 / 8/8 | $0.0490 | $4.08 |
| Opus 5.5 | 1 Model default | 8/8 | 0/4 | 1.00 / 1.00 / 1.00 | 0/8 | 5/8 | 5/8 | 1/8 | 0/4 / 0/4 | 6/8 / 7/8 | $0.0722 | $6.02 |
| Opus 5.5 | 2 Style contract | 8/8 | 0/4 | 1.00 / 1.00 / 1.00 | 0/8 | 1/8 | 5/8 | 3/8 | 0/4 / 0/4 | 8/8 / 8/8 | $0.0749 | $6.24 |
| Opus 5.5 | 3 Always-on skill | 8/8 | 0/4 | 1.00 / 1.00 / 1.00 | 0/8 | 3/8 | 5/8 | 3/8 | 0/4 / 0/4 | 8/8 / 7/8 | $0.1523 | $12.69 |
| Opus 5.5 | 4 Gate (v2 regex) | 0/8 | 0/4 | n/a / 0.00 / n/a | 0/8 | 8/8 | 8/8 | 0/8 | 0/4 / 0/4 | n/a / n/a | $0.0000 | $0.00 |
| Opus 5.5 | 4b Gate (v2 + Haiku) | 8/8 | 0/4 | 1.00 / 1.00 / 1.00 | 0/8 | 2/8 | 2/8 | 6/8 | 0/4 / 0/4 | 8/8 / 8/8 | $0.1004 | $8.36 |

### Gate classification (should this draft be rewritten?)

| Gate | Split | TP | FP | FN | TN | Precision | Recall | F1 |
|---|---|---|---|---|---|---|---|---|
| 4 Gate (v2 regex) (Haiku 5.5 run) | holdout | 15 | 0 | 1 | 18 | 1.00 | 0.94 | 0.97 |
| 4 Gate (v2 regex) (Haiku 5.5 run) | stress | 0 | 0 | 8 | 4 | n/a | 0.00 | n/a |
| 4 Gate (v2 regex) (Sonnet 5.5 run) | holdout | 15 | 0 | 1 | 18 | 1.00 | 0.94 | 0.97 |
| 4 Gate (v2 regex) (Sonnet 5.5 run) | stress | 0 | 0 | 8 | 4 | n/a | 0.00 | n/a |
| 4 Gate (v2 regex) (Opus 5.5 run) | holdout | 15 | 0 | 1 | 18 | 1.00 | 0.94 | 0.97 |
| 4 Gate (v2 regex) (Opus 5.5 run) | stress | 0 | 0 | 8 | 4 | n/a | 0.00 | n/a |
| 4b Gate (v2 + Haiku) (Haiku 5.5 run) | holdout | 16 | 0 | 0 | 18 | 1.00 | 1.00 | 1.00 |
| 4b Gate (v2 + Haiku) (Haiku 5.5 run) | stress | 8 | 0 | 0 | 4 | 1.00 | 1.00 | 1.00 |
| 4b Gate (v2 + Haiku) (Sonnet 5.5 run) | holdout | 16 | 0 | 0 | 18 | 1.00 | 1.00 | 1.00 |
| 4b Gate (v2 + Haiku) (Sonnet 5.5 run) | stress | 8 | 0 | 0 | 4 | 1.00 | 1.00 | 1.00 |
| 4b Gate (v2 + Haiku) (Opus 5.5 run) | holdout | 16 | 0 | 0 | 18 | 1.00 | 1.00 | 1.00 |
| 4b Gate (v2 + Haiku) (Opus 5.5 run) | stress | 8 | 0 | 0 | 4 | 1.00 | 1.00 | 1.00 |

### Tokens and per-call cost

| Model | System | Split | Model calls | Haiku gate calls | Input tokens | Output tokens | Mean cost per rewrite call | Mean latency per draft (s) |
|---|---|---|---|---|---|---|---|---|
| Haiku 5.5 | 1 Model default | holdout | 34 | 0 | 4,649 | 10,618 | $0.00017 | 1.8 |
| Haiku 5.5 | 1 Model default | stress | 12 | 0 | 2,029 | 5,404 | $0.00024 | 2.5 |
| Haiku 5.5 | 2 Style contract | holdout | 34 | 0 | 9,579 | 11,885 | $0.00020 | 2.1 |
| Haiku 5.5 | 2 Style contract | stress | 12 | 0 | 3,769 | 5,346 | $0.00025 | 2.6 |
| Haiku 5.5 | 3 Always-on skill | holdout | 34 | 0 | 46,401 | 9,666 | $0.00028 | 1.9 |
| Haiku 5.5 | 3 Always-on skill | stress | 12 | 0 | 16,765 | 4,387 | $0.00032 | 2.2 |
| Haiku 5.5 | 4 Gate (v2 regex) | holdout | 15 | 0 | 20,496 | 5,693 | $0.00033 | 1.1 |
| Haiku 5.5 | 4 Gate (v2 regex) | stress | 0 | 0 | 0 | 0 | $0.00000 | 0.0 |
| Haiku 5.5 | 4b Gate (v2 + Haiku) | holdout | 16 | 19 | 30,111 | 7,297 | $0.00036 | 1.3 |
| Haiku 5.5 | 4b Gate (v2 + Haiku) | stress | 8 | 12 | 16,532 | 3,030 | $0.00030 | 1.3 |
| Sonnet 5.5 | 1 Model default | holdout | 34 | 0 | 4,649 | 4,847 | $0.00170 | 1.7 |
| Sonnet 5.5 | 1 Model default | stress | 12 | 0 | 2,029 | 2,706 | $0.00259 | 2.3 |
| Sonnet 5.5 | 2 Style contract | holdout | 34 | 0 | 9,579 | 5,945 | $0.00231 | 1.9 |
| Sonnet 5.5 | 2 Style contract | stress | 12 | 0 | 3,769 | 3,026 | $0.00315 | 2.3 |
| Sonnet 5.5 | 3 Always-on skill | holdout | 34 | 0 | 46,401 | 8,249 | $0.00516 | 2.3 |
| Sonnet 5.5 | 3 Always-on skill | stress | 12 | 0 | 16,765 | 3,829 | $0.00598 | 2.8 |
| Sonnet 5.5 | 4 Gate (v2 regex) | holdout | 15 | 0 | 20,496 | 5,545 | $0.00643 | 1.4 |
| Sonnet 5.5 | 4 Gate (v2 regex) | stress | 0 | 0 | 0 | 0 | $0.00000 | 0.0 |
| Sonnet 5.5 | 4b Gate (v2 + Haiku) | holdout | 16 | 19 | 30,111 | 5,674 | $0.00603 | 1.4 |
| Sonnet 5.5 | 4b Gate (v2 + Haiku) | stress | 8 | 12 | 16,532 | 3,044 | $0.00602 | 2.1 |
| Opus 5.5 | 1 Model default | holdout | 34 | 0 | 4,649 | 7,082 | $0.00471 | 2.6 |
| Opus 5.5 | 1 Model default | stress | 12 | 0 | 2,029 | 3,204 | $0.00602 | 3.1 |
| Opus 5.5 | 2 Style contract | holdout | 34 | 0 | 9,579 | 6,832 | $0.00515 | 2.5 |
| Opus 5.5 | 2 Style contract | stress | 12 | 0 | 3,769 | 2,991 | $0.00624 | 2.9 |
| Opus 5.5 | 3 Always-on skill | holdout | 34 | 0 | 46,401 | 9,193 | $0.01087 | 3.3 |
| Opus 5.5 | 3 Always-on skill | stress | 12 | 0 | 16,765 | 4,261 | $0.01269 | 4.4 |
| Opus 5.5 | 4 Gate (v2 regex) | holdout | 15 | 0 | 20,496 | 5,296 | $0.01253 | 1.8 |
| Opus 5.5 | 4 Gate (v2 regex) | stress | 0 | 0 | 0 | 0 | $0.00000 | 0.0 |
| Opus 5.5 | 4b Gate (v2 + Haiku) | holdout | 16 | 19 | 30,111 | 5,508 | $0.01187 | 1.6 |
| Opus 5.5 | 4b Gate (v2 + Haiku) | stress | 8 | 12 | 16,532 | 3,228 | $0.01245 | 2.7 |

### Judge calibration on the original drafts (judge's slop verdict vs. the hand label)

| Judge | Split | TP | FP | FN | TN |
|---|---|---|---|---|---|
| Opus 5.5 | holdout | 15 | 0 | 1 | 18 |
| Opus 5.5 | stress | 8 | 0 | 0 | 4 |
| Sonnet 5.5 | holdout | 16 | 0 | 0 | 18 |
| Sonnet 5.5 | stress | 8 | 0 | 0 | 4 |

Judge agreement: slop verdict 635/690 outputs; meaning verdict 295/337 changed outputs.

### Actual spend (from API usage fields x list prices)

| Stage | API calls | Input tokens | Output tokens | Cost (USD) |
|---|---|---|---|---|
| Prompt sanity check on tune set (dev, 39 drafts; not reported) | 312 | 209,684 | 80,868 | $0.54 |
| Bakeoff generations, holdout + hard cases (final) | 624 | 450,993 | 153,786 | $2.23 |
| System 4b first run (discarded: gate max_tokens bug) | 158 | 130,424 | 25,189 | $0.43 |
| Opus 5.5 judge (incl. 95 truncated replies re-run) | 478 | 286,376 | 118,774 | $3.52 |
| Sonnet 5.5 judge | 383 | 225,927 | 31,768 | $0.77 |
| **Total** | **1,955** | **1,303,404** | **410,385** | **$7.49** |
