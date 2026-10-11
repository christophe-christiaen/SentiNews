# WP3 results: do agreements buffer cereal land against weather shocks?

Run of the frozen pre-registration ([preregistration.md](preregistration.md), commit `b0f232b`). Outcomes are Sentinel-2 anomalies in standard deviations of the parcel's own 2017–2020 seasons; positive = agreement land did better. Standard errors clustered by ERA5 cell. All numbers are aggregates; no parcel is identified.

## Sample

- Agreement parcels (entering 2021–2026): 247,441; matched: 247,321
- Never-treated parcels: 89,690; used as matches: 57,602
- Balance (standardised mean difference): largest 0.87 before matching, 0.06 after; covariates above 0.1 after matching: 0

## Confirmatory tests (Holm-adjusted over three)

| Test | estimate | SE | 95% CI | p | p (Holm) | parcel-seasons |
|---|---|---|---|---|---|---|
| H1 July NDVI: shock minus non-shock effect | +0.082 | 0.017 | [+0.049, +0.115] | 0.000 | 0.000 | 331,037 |
| H2 peak NDVI: calm-after-shock minus calm-after-calm effect | +0.035 | 0.024 | [-0.012, +0.081] | 0.141 | 0.141 | 164,698 |
| H3 H1 contrast, family B minus family A | +0.065 | 0.034 | [-0.003, +0.132] | 0.060 | 0.119 | 327,710 |

Components:

| | estimate | SE | 95% CI | p |
|---|---|---|---|---|
|   effect in shock seasons | +0.071 | 0.014 | [+0.044, +0.098] | 0.000 |
|   effect in non-shock seasons | -0.011 | 0.014 | [-0.039, +0.017] | 0.433 |
|   effect, all post-entry seasons | +0.040 | 0.011 | [+0.018, +0.062] | 0.000 |
|   H2 effect after a shock | +0.027 | 0.018 | [-0.008, +0.063] | 0.129 |
|   H2 effect after a calm season | -0.008 | 0.019 | [-0.045, +0.030] | 0.695 |

H1 contrast by option family:

| | estimate | SE | 95% CI | p |
|---|---|---|---|---|
| H1 contrast, family A | +0.038 | 0.035 | [-0.031, +0.106] | 0.280 |
| H1 contrast, family B | +0.102 | 0.016 | [+0.071, +0.134] | 0.000 |
| H1 contrast, family C (not tested) | -0.120 | 0.074 | [-0.264, +0.025] | 0.104 |

50 km wild block bootstrap (75 blocks): SE H1 0.016 (cell-clustered 0.017), H2 0.024 (0.024), H3 0.032 (0.034).

## Check 1: event study and pre-trends (July NDVI)

| event time | effect | SE | shock minus non-shock | SE | parcel-seasons |
|---|---|---|---|---|---|
| -4 | +0.002 | 0.009 | +0.016 | 0.015 | 159,332 |
| -3 | -0.016 | 0.010 | -0.001 | 0.018 | 189,329 |
| -2 | -0.009 | 0.011 | +0.030 | 0.020 | 166,712 |
| -1 | -0.056 | 0.015 | +0.048 | 0.027 | 145,652 |
| +0 | +0.053 | 0.013 | +0.072 | 0.025 | 173,061 |
| +1 | +0.021 | 0.016 | +0.105 | 0.033 | 76,027 |
| +2 | -0.007 | 0.019 | +0.052 | 0.039 | 43,609 |
| +3 | +0.073 | 0.027 | +0.053 | 0.050 | 29,934 |

Joint test of event times −4 to −1: effect χ²(4) = 32.8, p = 0.000; shock contrast χ²(4) = 9.5, p = 0.049.

## Checks decided in advance (H1 contrast; H2 and H3 alongside)

| Check | H1 | SE | p | H2 | SE | H3 | SE |
|---|---|---|---|---|---|---|---|
| Placebo: entry two seasons earlier | +0.079 | 0.016 | 0.000 | +0.057 | 0.024 | -0.079 | 0.026 |
| Synthetic: injected +0.20 in shock seasons (should recover 0.20) | +0.251 | 0.036 | 0.000 | – | – | – | – |
| Excluding 2017 | +0.082 | 0.017 | 0.000 | +0.035 | 0.024 | +0.065 | 0.034 |
| Cereal land defined without CROME 2020 | +0.081 | 0.018 | 0.000 | +0.041 | 0.024 | +0.060 | 0.037 |
| Shock threshold: rain -15% | +0.086 | 0.017 | 0.000 | +0.039 | 0.024 | +0.076 | 0.035 |
| Shock threshold: rain -25% | +0.078 | 0.017 | 0.000 | +0.022 | 0.024 | +0.063 | 0.034 |
| Shock threshold: rain -30% | +0.078 | 0.017 | 0.000 | +0.010 | 0.024 | +0.056 | 0.034 |
| Shock threshold: soil -0.75 SD | +0.080 | 0.017 | 0.000 | +0.043 | 0.026 | +0.066 | 0.034 |
| Shock threshold: soil -1.25 SD | +0.081 | 0.017 | 0.000 | +0.040 | 0.023 | +0.064 | 0.035 |
| Shock threshold: rain only | +0.080 | 0.017 | 0.000 | +0.047 | 0.022 | +0.065 | 0.035 |
| Shock threshold: soil moisture only | +0.074 | 0.017 | 0.000 | +0.010 | 0.024 | +0.068 | 0.035 |
| Shock threshold: heat 3 days | +0.084 | 0.017 | 0.000 | +0.034 | 0.024 | +0.067 | 0.034 |
| Shock threshold: heat 8 days | +0.082 | 0.017 | 0.000 | +0.038 | 0.024 | +0.066 | 0.034 |
| 5 km hexagon averages (cell x season strata) | +0.059 | 0.024 | 0.014 | -0.016 | 0.044 | +0.016 | 0.042 |
| Excluding Flood Zone 3 and deep peat | +0.080 | 0.018 | 0.000 | +0.038 | 0.025 | +0.055 | 0.035 |
| 2026 version: seasons 2017-2026, cell x season strata (no crop) | +0.132 | 0.017 | 0.000 | -0.022 | 0.027 | +0.043 | 0.033 |
| Unmatched full sample | +0.111 | 0.016 | 0.000 | +0.048 | 0.023 | +0.044 | 0.033 |

## Exploratory (not confirmatory; no multiple-testing correction)

| Analysis | estimate | SE | 95% CI | p |
|---|---|---|---|---|
| Cohort first season 2021 | +0.042 | 0.028 | [-0.013, +0.097] | 0.137 |
| Cohort first season 2022 | +0.077 | 0.023 | [+0.032, +0.123] | 0.001 |
| Cohort first season 2023 | +0.119 | 0.032 | [+0.056, +0.182] | 0.000 |
| Cohort first season 2024 | +0.044 | 0.029 | [-0.013, +0.102] | 0.132 |
| Cohort first season 2025 | +0.043 | 0.144 | [-0.239, +0.325] | 0.766 |
| Region: East Midlands | +0.082 | 0.050 | [-0.016, +0.181] | 0.102 |
| Region: East of England | +0.070 | 0.026 | [+0.019, +0.120] | 0.007 |
| Region: London | -0.127 | 0.645 | [-1.391, +1.138] | 0.845 |
| Region: North East | +0.130 | 0.073 | [-0.013, +0.273] | 0.075 |
| Region: North West | -0.323 | 0.152 | [-0.621, -0.025] | 0.034 |
| Region: South East | +0.102 | 0.043 | [+0.017, +0.186] | 0.018 |
| Region: South West | +0.131 | 0.043 | [+0.047, +0.216] | 0.002 |
| Region: West Midlands | +0.072 | 0.057 | [-0.039, +0.184] | 0.202 |
| Region: Yorkshire and the Humber | +0.050 | 0.057 | [-0.062, +0.162] | 0.379 |
| Flood Zone 3 or deep peat | +0.049 | 0.054 | [-0.056, +0.154] | 0.361 |
| Not Flood Zone 3 or deep peat | +0.080 | 0.018 | [+0.045, +0.115] | 0.000 |
| H3 with SOH actions counted as A | +0.065 | 0.034 | [-0.002, +0.133] | 0.058 |
| Secondary outcome: July NDMI (canopy water) | +0.105 | 0.017 | [+0.072, +0.139] | 0.000 |
| Secondary outcome: July NDRE (chlorophyll) | +0.100 | 0.016 | [+0.069, +0.130] | 0.000 |
| Secondary outcome: Seasonal NDVI integral | +0.120 | 0.036 | [+0.049, +0.191] | 0.001 |
| Secondary outcome: Senescence timing (half-months) | -0.172 | 0.033 | [-0.237, -0.108] | 0.000 |
| Compound shock (shock after shock), peak NDVI vs calm-after-calm | +0.050 | 0.064 | [-0.076, +0.176] | 0.440 |
| Wet winter (waterlogging) vs not, July NDVI (Sentinel-2 only) | -0.069 | 0.017 | [-0.103, -0.036] | 0.000 |

Not yet run: the embedding (AlphaEarth) version of the matching, waiting for the national extraction; the Sentinel-1 waterlogging analysis, waiting for the national Sentinel-1 panel; the crop-controlled 2026 season, waiting for CROME 2026.
