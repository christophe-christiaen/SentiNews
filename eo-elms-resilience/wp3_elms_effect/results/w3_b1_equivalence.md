# W3-B1 equivalence tests

Protocol: [w3_b1_equivalence_protocol.md](w3_b1_equivalence_protocol.md). Labels beside registered results; no registered reading changes. Exploratory. The limits were chosen after the estimates were public, anchored on numbers written earlier. Script reproduced the published estimates and permutation p values exactly.

90% intervals. A result is within the limit only if both parts pass. X is the smallest effect ruled out, the larger of the two parts.

| Result | Limit | Estimate | Cell errors | Shuffled-season spread | Reading | X | Placebo |
|---|---:|---:|---|---|---|---:|---|
| A: H1 July NDVI, frozen | 0.10 SD | +0.082 | (+0.054, +0.110) fail | (+0.005, +0.160) fail | can't rule out | 0.160 | +0.079 (+0.048, +0.110), fails |
| B: H1 July NDVI, E3 sample | 0.10 SD | +0.087 | (+0.056, +0.117) fail | (+0.005, +0.166) fail | can't rule out | 0.166 | +0.080 (+0.049, +0.111), fails |
| C: dry or heat harvest, All agreement land | 0.10 t/ha | +0.039 | (+0.018, +0.059) pass | (-0.015, +0.078) pass | within the limit | 0.078 | -0.081 (-0.162, +0.001), passes narrowly |
| C: dry or heat harvest, Management-only | 0.10 t/ha | +0.041 | (+0.017, +0.066) pass | (-0.015, +0.088) pass | within the limit | 0.088 | -0.095 (-0.191, +0.001), passes narrowly |
| D: wet-winter harvest, All agreement land | 0.10 t/ha | -0.040 | (-0.060, -0.020) pass | (-0.087, +0.023) pass | within the limit, in a design that failed its placebo | 0.087 | -0.128 (-0.194, -0.061), fails |
| D: wet-winter harvest, Management-only | 0.10 t/ha | -0.050 | (-0.075, -0.026) pass | (-0.110, +0.014) fail | can't rule out | 0.110 | -0.139 (-0.224, -0.054), fails |
| D: wet-winter harvest, Buffer strips | 0.10 t/ha | -0.068 | (-0.092, -0.043) pass | (-0.132, +0.001) fail | can't rule out | 0.132 | -0.162 (-0.246, -0.078), fails |
| E: wet-winter July NDVI, All agreement land | 0.10 SD | -0.014 | (-0.039, +0.011) pass | (-0.116, +0.081) fail | can't rule out | 0.116 | -0.038 (-0.076, +0.000), passes narrowly |
| E: wet-winter July NDVI, Buffer strips | 0.10 SD | -0.053 | (-0.083, -0.022) pass | (-0.154, +0.031) fail | can't rule out | 0.154 | -0.025 (-0.070, +0.020), passes |

## Readings of X, harvest

| Result | X, t/ha | £/ha in a shock season | Share of a bad season's loss (0.85 t/ha) | Share of the no-till payment, annualised |
|---|---:|---:|---:|---:|
| C: dry or heat harvest, All agreement land | 0.078 | £16 | 9% | 10% |
| C: dry or heat harvest, Management-only | 0.088 | £18 | 10% | 12% |
| D: wet-winter harvest, All agreement land | 0.087 | £18 | 10% | 7% |
| D: wet-winter harvest, Management-only | 0.110 | £22 | 13% | 9% |
| D: wet-winter harvest, Buffer strips | 0.132 | £27 | 16% | 11% |

## How to read this

- **Three harvest results pass, and they are the ones with the weakest claim to be clean.** Equivalence measures noise around the estimate, not bias.
- **Dry-or-heat placebos pass only narrowly and are themselves close to the limit** (-0.081 and -0.095 t/ha). Not a registered calculation: if a bias of that size carried into the contrast, the estimate would be about +0.12 to +0.14 t/ha, above the limit. So the pass is conditional on the placebo being noise.
- **Wet-winter, all land, passes in a design that failed its placebo** (-0.128).
- **HonestDiD isn't included:** at M̄ = 0.25 the 95% sets on the averages are (-0.032, +0.122) for dry or heat, all land, and (-0.101, +0.012) for wet, all land, both past the limit.
- **The index isn't measured yield.** It is fitted to regional yields and tested only at regional level, and predictions of this kind can understate real differences between fields; this wasn't measured. If so, a limit in index t/ha is less demanding than the same limit in real t/ha.
- **Centring:** using the raw draws instead of centred ones changes no pass or fail.
