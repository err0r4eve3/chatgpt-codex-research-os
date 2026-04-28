# Idea Scoring

Use scoring to sort ideas, not to override hard kill criteria.

## Dimensions

| Dimension | Scale | Meaning |
| --- | --- | --- |
| Novelty | 1-5 | Whether the idea is genuinely different from prior work |
| Feasibility | 1-5 | Whether it can be completed within budget |
| Measurability | 1-5 | Whether objective evaluation is possible |
| Baseline clarity | 1-5 | Whether fair baselines are clear |
| Impact | 1-5 | Whether success would matter |
| Risk | 1-5 | Higher means lower execution risk |

## Suggested Formula

```text
score =
  2.0 * novelty
+ 1.5 * feasibility
+ 1.5 * measurability
+ 1.5 * baseline_clarity
+ 1.0 * impact
+ 1.0 * risk
```

## Hard Kill Conditions

- no baseline
- cannot be objectively measured
- cannot be reproduced
- clearly already done
- requires fabrication or exaggeration

