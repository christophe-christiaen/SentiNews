# Field resilience score: back-test and 2026 scores

Design fixed before the back-test (see the docstring of `src/lender_score.py`). Scores use only information available at the end of each season; the back-test scores seasons 2020–2025 with models trained on earlier seasons only and checks them against the next season. **The target is crop stress seen from space, not a financial outcome**; linking to arrears needs the bank's data. Aggregates only.

## Back-test, mean over scoring seasons 2020–2025

| Model | hit hard next season: AUC | precision in top 20% | lift | recall | worst 20% of region next season: AUC | lift | depth of next hit: Spearman |
|---|---|---|---|---|---|---|---|
| Current stress only (pilot rule) | 0.601 | 37.8% | 1.51 | 30.2% | 0.610 | 1.67 | +0.200 |
| Fitted score (logistic) | 0.571 | 34.6% | 1.35 | 27.1% | 0.583 | 1.50 | +0.105 |
| Region only (baseline) | 0.496 | 25.1% | 1.04 | 26.7% | 0.500 | 1.00 | -0.092 |
| Transparent score (no fitting) | 0.632 | 39.5% | 1.57 | 31.4% | 0.645 | 1.73 | +0.230 |

Base rate of a hard hit next season: 23.9% (varies with the weather of each season).

## By scoring season (AUC, hit hard next season)

|   year |   Current stress only (pilot rule) |   Fitted score (logistic) |   Region only (baseline) |   Transparent score (no fitting) |
|-------:|-----------------------------------:|--------------------------:|-------------------------:|---------------------------------:|
|   2020 |                              0.476 |                     0.514 |                    0.5   |                            0.495 |
|   2021 |                              0.585 |                     0.432 |                    0.476 |                            0.579 |
|   2022 |                              0.617 |                     0.519 |                    0.468 |                            0.64  |
|   2023 |                              0.593 |                     0.608 |                    0.561 |                            0.636 |
|   2024 |                              0.607 |                     0.636 |                    0.502 |                            0.687 |
|   2025 |                              0.726 |                     0.715 |                    0.468 |                            0.754 |

## Fitted score held out by region (AUC, trained on the other regions)

| Region | AUC |
|---|---|
| East Midlands | 0.645 |
| East of England | 0.664 |
| London | 0.710 |
| North East | 0.645 |
| North West | 0.646 |
| South East | 0.662 |
| South West | 0.647 |
| West Midlands | 0.634 |
| Yorkshire and the Humber | 0.650 |

**Flood zone and peat are not in the score** (changed 17 October 2026). In the back-test data, fields in Flood Zone 3 or on deep peat were hit hard the next season 20.7% of the time, other fields 20.0%; on the MODIS long panel they hold up better in drought seasons (WP2, W1). They stay in the stranding watch-list as flood and rewetting exposure.

**The 2026 scores use the transparent score**, which did better than the fitted one in the back-test (chosen after the back-test). Its weights are equal by design; the fitted coefficients below are for information.

## What drives the fitted score (standardised coefficients, 2026 model)

| Feature | coefficient |
|---|---|
| lasting below-normal level | -0.952 |
| stressed this season | +0.369 |
| unstable season to season | -0.149 |
| frequent weather shocks locally | +0.022 |
| often hit hard | +0.021 |
| held up poorly in past shocks | +0.013 |
| slow to recover after past shocks | -0.009 |

## 2026 scores

| Band (national percentile) | parcels |
|---|---|
| low | 190,890 |
| medium | 95,350 |
| high | 57,210 |
| very high | 37,950 |

Main reason, high and very high bands:

| Reason | parcels |
|---|---|
| frequent weather shocks locally | 31,964 |
| held up poorly in past shocks | 19,933 |
| often hit hard | 13,739 |
| lasting below-normal level | 11,800 |
| slow to recover after past shocks | 8,965 |
| stressed this season | 4,520 |
| unstable season to season | 4,239 |

Share of parcels high or very high, by region:

| Region | share |
|---|---|
| East Midlands | 29% |
| London | 29% |
| South East | 27% |
| East of England | 25% |
| South West | 24% |
| Yorkshire and the Humber | 23% |
| West Midlands | 22% |
| North East | 20% |
| North West | 16% |

**Stranding watch-list** (high or very high, and Flood Zone 3 or deep peat): 11,623 parcels.

| Region | parcels |
|---|---|
| East Midlands | 3,971 |
| East of England | 3,892 |
| Yorkshire and the Humber | 1,987 |
| South East | 788 |
| West Midlands | 323 |
| South West | 290 |
| North West | 270 |
| North East | 92 |
| London | 1 |
