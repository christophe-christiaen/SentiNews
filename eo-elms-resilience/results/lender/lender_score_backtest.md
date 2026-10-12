# Field resilience score: back-test and 2026 scores

Design fixed before the back-test (see the docstring of `src/lender_score.py`). Scores use only information available at the end of each season; the back-test scores seasons 2020–2025 with models trained on earlier seasons only and checks them against the next season. **The target is crop stress seen from space, not a financial outcome**; linking to arrears needs the bank's data. Aggregates only.

## Back-test, mean over scoring seasons 2020–2025

| Model | hit hard next season: AUC | precision in top 20% | lift | recall | worst 20% of region next season: AUC | lift | depth of next hit: Spearman |
|---|---|---|---|---|---|---|---|
| Current stress only (pilot rule) | 0.601 | 37.8% | 1.51 | 30.2% | 0.610 | 1.67 | +0.200 |
| Fitted score (logistic) | 0.571 | 34.6% | 1.35 | 27.0% | 0.582 | 1.50 | +0.105 |
| Region only (baseline) | 0.496 | 25.1% | 1.04 | 26.7% | 0.500 | 1.00 | -0.092 |
| Transparent score (no fitting) | 0.631 | 39.2% | 1.56 | 31.2% | 0.643 | 1.72 | +0.227 |

Base rate of a hard hit next season: 23.9% (varies with the weather of each season).

## By scoring season (AUC, hit hard next season)

|   year |   Current stress only (pilot rule) |   Fitted score (logistic) |   Region only (baseline) |   Transparent score (no fitting) |
|-------:|-----------------------------------:|--------------------------:|-------------------------:|---------------------------------:|
|   2020 |                              0.476 |                     0.514 |                    0.5   |                            0.497 |
|   2021 |                              0.585 |                     0.432 |                    0.476 |                            0.578 |
|   2022 |                              0.617 |                     0.519 |                    0.468 |                            0.636 |
|   2023 |                              0.593 |                     0.608 |                    0.561 |                            0.64  |
|   2024 |                              0.607 |                     0.635 |                    0.502 |                            0.681 |
|   2025 |                              0.726 |                     0.715 |                    0.468 |                            0.754 |

## Fitted score held out by region (AUC, trained on the other regions)

| Region | AUC |
|---|---|
| East Midlands | 0.645 |
| East of England | 0.663 |
| London | 0.709 |
| North East | 0.645 |
| North West | 0.646 |
| South East | 0.662 |
| South West | 0.647 |
| West Midlands | 0.634 |
| Yorkshire and the Humber | 0.650 |

**The 2026 scores use the transparent score**, which did better than the fitted one in the back-test (chosen after the back-test). Its weights are equal by design; the fitted coefficients below are for information.

## What drives the fitted score (standardised coefficients, 2026 model)

| Feature | coefficient |
|---|---|
| stress debt carried | -0.952 |
| stressed this season | +0.369 |
| unstable season to season | -0.149 |
| frequent weather shocks locally | +0.023 |
| often hit hard | +0.021 |
| Flood Zone 3 | +0.017 |
| held up poorly in past shocks | +0.012 |
| deep peat | -0.010 |
| slow to recover after past shocks | -0.009 |
| Flood Zone 2 | +0.009 |
| shallow peat | -0.004 |

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
| frequent weather shocks locally | 31,944 |
| held up poorly in past shocks | 18,463 |
| often hit hard | 13,053 |
| stress debt carried | 10,971 |
| slow to recover after past shocks | 8,149 |
| unstable season to season | 3,939 |
| stressed this season | 3,906 |
| Flood Zone 3 | 1,887 |
| Flood Zone 2 | 1,161 |
| deep peat | 911 |
| shallow peat | 776 |

Share of parcels high or very high, by region:

| Region | share |
|---|---|
| East Midlands | 30% |
| London | 28% |
| East of England | 26% |
| South East | 25% |
| Yorkshire and the Humber | 24% |
| South West | 23% |
| West Midlands | 21% |
| North East | 18% |
| North West | 16% |

**Stranding watch-list** (high or very high, and Flood Zone 3 or deep peat): 18,198 parcels.

| Region | parcels |
|---|---|
| East of England | 6,572 |
| East Midlands | 5,901 |
| Yorkshire and the Humber | 3,010 |
| South East | 1,098 |
| North West | 545 |
| West Midlands | 472 |
| South West | 423 |
| North East | 159 |
| London | 4 |
