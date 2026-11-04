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
