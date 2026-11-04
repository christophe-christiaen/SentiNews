# W3-H results: field harvest index and its gate against Defra

Run of [w3_h_harvest_protocol.md](w3_h_harvest_protocol.md), Steps 1 and 2. Leave-one-year-out, 2017–2025, 8 English Defra regions. A crop passes if R² is at least 0.4 and dry-spring error is no more than 1.5 times that of other seasons. Aggregates only.

## Gate

| Crop | Field-seasons | R² | r | MAE dry (t/ha) | MAE other (t/ha) | Ratio | Gate |
|---|---:|---:|---:|---:|---:|---:|---|
| wheat | 1,318,003 | +0.55 | +0.75 | 0.48 | 0.40 | 1.19 | pass |
| winter barley | 355,489 | +0.57 | +0.78 | 0.36 | 0.37 | 0.95 | pass |
| spring barley | 460,710 | +0.43 | +0.68 | 0.37 | 0.37 | 0.98 | pass |

## Context, not part of the gate

| Crop | R², WP1 region-median prediction | R², England mean | Bias dry (t/ha) | Bias other (t/ha) | Half-months missing per field | Field SD within region-season (t/ha) |
|---|---:|---:|---:|---:|---:|---:|
| wheat | +0.60 | +0.75 | -0.10 | -0.13 | 28% | 0.88 |
| winter barley | +0.61 | +0.77 | +0.05 | -0.17 | 27% | 0.95 |
| spring barley | +0.49 | +0.59 | +0.01 | -0.11 | 27% | 0.89 |

## England mean by season (t/ha)

| Season | wheat: Defra, index | winter barley: Defra, index | spring barley: Defra, index |
|---|---:|---:|---:|
| 2017 | +0.40, +0.11 | +0.16, +0.14 | +0.01, +0.08 |
| 2018 (dry) | -0.12, -0.14 | -0.03, +0.15 | -0.58, -0.28 |
| 2019 | +1.16, +1.01 | +1.14, +0.45 | +1.13, +0.51 |
| 2020 (dry) | -1.08, -1.38 | -1.07, -0.69 | -0.03, +0.04 |
| 2021 | +0.07, -0.14 | -0.03, -0.13 | +0.20, +0.17 |
| 2022 (dry) | +0.82, +0.21 | +0.67, +0.51 | +0.59, -0.09 |
| 2023 | +0.24, -0.12 | +0.24, -0.04 | -0.65, -0.45 |
| 2024 | -0.77, -0.39 | -0.80, -0.56 | -0.22, -0.36 |
| 2025 (dry) | -0.71, -0.18 | -0.29, -0.50 | -0.44, -0.13 |

**Stated limit:** Defra's regional figures cannot show whether the index ranks fields correctly within a region.

## Step 3: agreement fields against matched fields

Harvest index anomaly in shock seasons minus other seasons, t/ha. Estimate (95% interval); SE clustered by ERA5 cell; strata ERA5 cell × season; seasons 2017–2025; E3 matched sample; frozen-plan estimator; placebo on 2017–2020. Rule fixed in advance. No multiple-testing correction. This is an index built from Sentinel-2 and weather, not measured yield.

### Decides

| Family | Parcel-seasons | In shock seasons | In other seasons | Contrast | Placebo | Reading |
|---|---:|---:|---:|---|---|---|
| All agreement land | 147,916 | +0.031 | -0.008 | +0.039 (+0.014, +0.063) | -0.081 (-0.162, +0.001) | holds better |
| Management-only | 102,626 | +0.030 | -0.011 | +0.041 (+0.012, +0.071) | -0.095 (-0.191, +0.001) | holds better |
| Cover crops | 11,795 | +0.033 | -0.023 | +0.056 (-0.012, +0.125) | -0.054 (-0.283, +0.174) | not shown |
| No-till | 2,249 | -0.035 | +0.004 | -0.039 (-0.194, +0.116) | +0.072 (-0.359, +0.503) | not shown |

### Reported only

| Family | Within cohort | Within cohort, before entry | Never-treated controls only | Strata with CROME crop | July NDVI, same rows (SD) |
|---|---|---|---|---|---|
| All agreement land | +0.049 (-0.001, +0.099) | -0.023 (-0.063, +0.016) | +0.013 (-0.018, +0.044) | +0.032 (+0.007, +0.057) | +0.041 (-0.011, +0.092) |
| Management-only | +0.041 (-0.027, +0.109) | -0.032 (-0.081, +0.017) | +0.021 (-0.016, +0.057) | +0.034 (+0.004, +0.064) | +0.046 (-0.017, +0.109) |
| Cover crops | +0.066 (-0.095, +0.227) | -0.112 (-0.235, +0.011) | +0.084 (+0.005, +0.163) | +0.039 (-0.032, +0.110) | +0.008 (-0.145, +0.162) |
| No-till | +0.002 (-0.152, +0.156) | -0.110 (-0.324, +0.104) | -0.095 (-0.261, +0.070) | -0.085 (-0.250, +0.079) | -0.071 (-0.357, +0.214) |
| Management-only, no other option | +0.050 (-0.158, +0.258) | -0.064 (-0.239, +0.112) | +0.114 (+0.047, +0.182) | +0.076 (+0.015, +0.138) | +0.026 (-0.137, +0.188) |

Management-only, no other option: contrast +0.075 (+0.014, +0.136), placebo not possible (no field in a cohort early enough); the rule cannot be applied.

### By crop: field in the same crop in both seasons compared

| Family | wheat: contrast; placebo | winter barley: contrast; placebo | spring barley: contrast; placebo |
|---|---|---|---|
| All agreement land | +0.012 (-0.021, +0.046); -0.005 (-0.134, +0.123) | +0.015 (-0.117, +0.146); +0.047 (-0.496, +0.591) | -0.008 (-0.083, +0.066); -0.031 (-0.177, +0.115) |
| Management-only | +0.018 (-0.023, +0.059); -0.056 (-0.219, +0.107) | +0.001 (-0.155, +0.157); +0.418 (-0.238, +1.074) | -0.010 (-0.101, +0.082); +0.024 (-0.187, +0.235) |
| Cover crops | +0.030 (-0.081, +0.141); +0.167 (-0.251, +0.586) | +0.326 (+0.015, +0.637); +2.076 (+1.350, +2.801) | -0.149 (-0.335, +0.038); -0.242 (-0.592, +0.108) |
| No-till | +0.049 (-0.192, +0.290); +0.080 (-0.503, +0.663) | +0.660 (-0.063, +1.384); -0.897 (-1.786, -0.009) | -0.170 (-0.532, +0.192); -0.437 (-0.750, -0.123) |
| Management-only, no other option | -0.008 (-0.098, +0.083);  | +0.244 (-0.112, +0.601);  | -0.116 (-0.327, +0.095);  |

### Options that take land out of cereals

Fields in cereals the season before entry, E3 matched sample: share with a non-cereal CROME season from entry to 2025. Never-treated fields cover the same seasons, weighted to the family's cohorts.

| Family | Fields | Family | Never treated |
|---|---:|---:|---:|
| Herbal leys | 4,181 | 73% | 52% |
| Grassland options | 2,103 | 70% | 59% |

### Regional context, no causal reading

Spearman correlation across region-seasons, 2021–2025, between Defra's yield anomaly and the region's share of the cereal frame in agreements. A region-season counts as shock if at least half its fields are in shock cells.

| Crop | Shock: n, correlation | Other: n, correlation |
|---|---|---|
| wheat | 16, -0.74 | 24, -0.55 |
| winter barley | 16, -0.63 | 24, -0.41 |
| spring barley | 16, -0.89 | 24, -0.20 |

### Not run or not stated

- **Farm-level reading: not run.** The farm grouping links agreements to companies by nearest location, covers only fields under an option, and holds no fields for non-agreement farms, so it cannot group fields into holdings.
- **£/ha: not stated yet.** Defra's farm-gate price series is not held locally.
- **2026:** added after Defra's final figures on 10 December 2026.
