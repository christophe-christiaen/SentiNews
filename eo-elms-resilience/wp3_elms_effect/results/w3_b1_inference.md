# W3-B1: few shocks, trends, multiple tests and crop conditioning

Protocol: [w3_b1_inference_protocol.md](w3_b1_inference_protocol.md). Labels beside registered results; no registered reading changes. Exploratory.

## 1. Inference when shocks are few

SE (95% interval). Season and two-way use scores from each row's deviation from its side's mean, because the estimator's influence functions sum to about zero within a season (see the protocol record). **Season clustering understates uncertainty when one season dominates, as it does here, so the permutation test carries more weight.**

| Result | Estimate | Cell | 50 km | Region (no conditioning) | Season | Permutation p | Label | Share of hazard side by season |
|---|---:|---|---:|---|---|---:|---|---|
| A: H1 July NDVI, frozen | +0.082 | 0.017 (+0.049, +0.115) | 0.017 | 0.010 (+0.058, +0.106) | 0.007 (+0.062, +0.102), G = 5 | 0.059 | not robust | 2021: 0%, 2022: 15%, 2023: 2%, 2025: 83% |
| B: H1 July NDVI, E3 sample | +0.087 | 0.019 (+0.050, +0.123) | 0.019 | 0.017 (+0.047, +0.126) | 0.008 (+0.065, +0.108), G = 5 | 0.048 | robust to few shocks | 2021: 0%, 2022: 15%, 2023: 2%, 2025: 83% |
| C: dry or heat harvest, All agreement land | +0.039 | 0.013 (+0.014, +0.063) | 0.014 | 0.017 (-0.001, +0.078) | 0.013 (+0.002, +0.075), G = 5 | 0.322 | not robust | 2021: 0%, 2022: 14%, 2023: 3%, 2025: 84% |
| C: dry or heat harvest, Management-only | +0.041 | 0.015 (+0.012, +0.071) | 0.015 | 0.015 (+0.007, +0.076) | 0.017 (-0.006, +0.088), G = 5 | 0.297 | not robust | 2021: 0%, 2022: 11%, 2023: 2%, 2025: 87% |
| D: wet-winter harvest, All agreement land | -0.040 | 0.012 (-0.064, -0.016) | 0.013 | 0.017 (-0.081, +0.001) | 0.012 (-0.073, -0.007), G = 5 | 0.279 | not robust | 2021: 6%, 2023: 4%, 2024: 90% |
| D: wet-winter harvest, Management-only | -0.050 | 0.015 (-0.079, -0.022) | 0.014 | 0.016 (-0.088, -0.013) | 0.006 (-0.067, -0.034), G = 5 | 0.235 | not robust | 2021: 5%, 2023: 3%, 2024: 92% |
| D: wet-winter harvest, Buffer strips | -0.068 | 0.015 (-0.097, -0.038) | 0.016 | 0.017 (-0.109, -0.027) | 0.016 (-0.113, -0.023), G = 5 | 0.104 | not robust | 2021: 9%, 2023: 5%, 2024: 85% |
| E: wet-winter July NDVI, All agreement land | -0.014 | 0.015 (-0.044, +0.016) | 0.013 | 0.019 (-0.060, +0.032) | 0.047 (-0.134, +0.106), G = 6 | 0.840 | not robust | 2021: 3%, 2023: 2%, 2024: 36%, 2026: 59% |
| E: wet-winter July NDVI, Buffer strips | -0.053 | 0.019 (-0.089, -0.016) | 0.018 | 0.011 (-0.078, -0.027) | 0.046 (-0.170, +0.065), G = 6 | 0.433 | not robust | 2021: 7%, 2023: 4%, 2024: 55%, 2026: 35% |

### Leave one season out

| Result | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---:|---:|---:|---:|---:|---:|
| A: H1 July NDVI, frozen | +0.085 | +0.086 | +0.081 | +0.071 | +0.062 |  |
| B: H1 July NDVI, E3 sample | +0.088 | +0.092 | +0.086 | +0.082 | +0.059 |  |
| C: dry or heat harvest, All agreement land | +0.038 | +0.044 | +0.048 | +0.021 | +0.010 |  |
| C: dry or heat harvest, Management-only | +0.039 | +0.044 | +0.056 | +0.011 | +0.026 |  |
| D: wet-winter harvest, All agreement land | -0.042 | -0.045 | -0.047 | +0.002 | -0.018 |  |
| D: wet-winter harvest, Management-only | -0.050 | -0.053 | -0.054 | -0.017 | -0.040 |  |
| D: wet-winter harvest, Buffer strips | -0.072 | -0.075 | -0.075 | -0.031 | -0.050 |  |
| E: wet-winter July NDVI, All agreement land | -0.013 | -0.019 | -0.025 | +0.038 | -0.002 | -0.086 |
| E: wet-winter July NDVI, Buffer strips | -0.058 | -0.050 | -0.075 | +0.014 | -0.036 | -0.085 |

**Cells merged by agreement: not informative.** 38,172 agreements, 12,808 in more than one cell, so 89% of cells fall into one cluster, and with so few effective clusters the SE collapses. Farm-level clustering remains unaddressed, apart from 50 km blocks, which are coarser than most farms.

## 2. How large a trend violation overturns the result

Rambachan and Roth (2023), relative magnitudes, cell-clustered covariance. Breakdown M̄ is the smallest grid value (step 0.25) whose 95% set includes zero. The package warned in 36 of its fits that a set is open at an endpoint, so set lengths may not be exact.

| Result | Parameter | Estimate | M̄ = 0 | M̄ = 0.25 | M̄ = 0.5 | Breakdown M̄ |
|---|---|---:|---|---|---|---:|
| A: H1 July NDVI, frozen | average of 0–3 | +0.070 | (+0.035, +0.106) | (-0.010, +0.153) | (-0.078, +0.222) | 0.25 |
| A: H1 July NDVI, frozen | first season | +0.072 | (+0.023, +0.121) | (+0.009, +0.140) | (-0.008, +0.161) | 0.5 |
| B: H1 July NDVI, E3 sample | average of 0–3 | +0.075 | (+0.035, +0.114) | (-0.008, +0.157) | (-0.073, +0.217) | 0.25 |
| B: H1 July NDVI, E3 sample | first season | +0.067 | (+0.015, +0.120) | (-0.003, +0.136) | (-0.022, +0.153) | 0.25 |
| C: dry or heat harvest, All agreement land | average of 0–3 | +0.045 | (+0.014, +0.077) | (-0.032, +0.122) | (-0.092, +0.182) | 0.25 |
| C: dry or heat harvest, All agreement land | first season | +0.033 | (-0.002, +0.068) | (-0.015, +0.085) | (-0.033, +0.105) | 0 |
| D: wet-winter harvest, All agreement land | average of 0–3 | -0.045 | (-0.073, -0.017) | (-0.101, +0.012) | (-0.142, +0.053) | 0.25 |
| D: wet-winter harvest, All agreement land | first season | -0.035 | (-0.070, +0.000) | (-0.080, +0.011) | (-0.091, +0.022) | 0 |

## 3. Multiple testing

Romano–Wolf over 64 contrasts, cell-level uncertainty. 12 have raw p below 0.05; **6 survive.** Cushions and costs both count. Placebo failures stand.

| Outcome | Contrast | Family | Estimate (95% interval) | Raw p | Adjusted, all 64 | Adjusted, within outcome |
|---|---|---|---|---:|---:|---:|
| Harvest, wet | Wet shock: harvest index, observable parcels | Buffer strips | -0.093 (-0.132, -0.054) | 0.0000 | 0.0005 | 0.0002 |
| Harvest, wet | Wet shock: harvest index, E3 matched sample (decides) | Buffer strips | -0.068 (-0.097, -0.038) | 0.0000 | 0.0006 | 0.0002 |
| Harvest, wet | Wet shock: harvest index, observable parcels | All agreement land | -0.062 (-0.094, -0.030) | 0.0001 | 0.0055 | 0.0011 |
| Harvest, wet | Wet shock: harvest index, E3 matched sample (decides) | Management-only | -0.050 (-0.079, -0.022) | 0.0006 | 0.0206 | 0.0034 |
| Harvest, wet | Wet shock: harvest index, observable parcels | Management-only | -0.063 (-0.100, -0.027) | 0.0007 | 0.0237 | 0.0034 |
| Harvest, wet | Wet shock: harvest index, E3 matched sample (decides) | All agreement land | -0.040 (-0.064, -0.016) | 0.0011 | 0.0355 | 0.0050 |
| Harvest, dry or heat | Dry or heat: harvest index, E3 matched sample (decides) | All agreement land | +0.039 (+0.014, +0.063) | 0.0022 | 0.0640 | 0.0063 |
| July NDVI | Wet shock: July NDVI, E3 matched sample | Buffer strips | -0.053 (-0.089, -0.016) | 0.0048 | 0.1467 | 0.0515 |
| Harvest, dry or heat | Dry or heat: harvest index, E3 matched sample (decides) | Management-only | +0.041 (+0.012, +0.071) | 0.0059 | 0.1773 | 0.0167 |
| July NDVI | Wet shock: July NDVI, observable parcels | Buffer strips | -0.062 (-0.107, -0.016) | 0.0080 | 0.2246 | 0.0769 |
| Establishment | Wet shock: observable parcels | Management-only | -0.010 (-0.017, -0.002) | 0.0138 | 0.3550 | 0.1573 |
| Establishment | Wet shock: observable parcels | All agreement land | -0.008 (-0.015, -0.001) | 0.0193 | 0.4631 | 0.2118 |

## 4. Crop conditioning

| Version | H1 | Placebo |
|---|---|---|
| A: frozen sample, crop strata yes | +0.082 (+0.049, +0.115) | +0.079 (+0.048, +0.110) |
| A: frozen sample, crop strata no | +0.096 (+0.063, +0.130) | +0.088 (+0.056, +0.119) |
| B: E3 sample, crop strata yes | +0.087 (+0.050, +0.123) | +0.080 (+0.049, +0.111) |
| B: E3 sample, crop strata no | +0.098 (+0.062, +0.133) | +0.087 (+0.055, +0.120) |

Crop conditioning matters (H1 moves by more than 0.05 SD): no.

### Does entry change rotations?

Share of seasons in cereals, after entry, E3 matched sample, in share units.

| Family | Effect | Placebo | Entry shifts rotations |
|---|---|---|---|
| All agreement land | -0.017 (-0.022, -0.012) | -0.001 (-0.012, +0.009) | no |
| Management-only | -0.015 (-0.021, -0.009) | -0.000 (-0.014, +0.013) | no |
| Cover crops | +0.027 (+0.012, +0.042) | -0.009 (-0.052, +0.034) | yes |
| No-till | +0.033 (+0.001, +0.065) | -0.002 (-0.068, +0.065) | yes |
| Herbal leys | -0.184 (-0.206, -0.161) | +0.033 (-0.034, +0.100) | yes |
| Grassland options | -0.063 (-0.088, -0.039) | +0.016 (-0.045, +0.076) | yes |
| Buffer strips | -0.006 (-0.014, +0.002) | -0.011 (-0.023, +0.002) | no |
