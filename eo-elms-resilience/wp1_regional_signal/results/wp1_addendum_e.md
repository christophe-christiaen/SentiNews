# WP1 addendum E: degree-days, sign-constrained weather, an out-of-range flag and shift-aware intervals

Protocol addendum E ([protocol.md](protocol.md)), written 29 October 2026, with clarifications recorded 30 October 2026 before any degree-day value was fetched. Leave-one-year-out 2017–2025. Extreme seasons: 2018, 2022, 2025. Errors are England-level (mean over regions of predicted minus Defra anomaly, t/ha).

## E1 + E2 against the model in use

| Crop · cutoff | model in use | R² in use | R² E | England R² in use → E | extreme-season MAE in use → E | dry-spring MAE in use → E | adopt |
|---|---|---|---|---|---|---|---|
| wheat | mid-July | first run | +0.64 | +0.57 | +0.78 → +0.67 | 0.37 → 0.44 | 0.36 → 0.34 | no |
| wheat | end of August | first run | +0.60 | +0.64 | +0.80 → +0.78 | 0.30 → 0.36 | 0.31 → 0.32 | no |
| winter barley | mid-July | first run + Sentinel-1 (C2) | +0.56 | +0.38 | +0.81 → +0.66 | 0.08 → 0.37 | 0.14 → 0.32 | no |
| winter barley | end of August | first run | +0.61 | +0.57 | +0.86 → +0.85 | 0.15 → 0.14 | 0.20 → 0.18 | no |
| spring barley | mid-July | addendum B | +0.58 | +0.56 | +0.79 → +0.78 | 0.20 → 0.17 | 0.15 → 0.13 | no |
| spring barley | end of August | addendum B | +0.60 | +0.60 | +0.84 → +0.84 | 0.14 → 0.12 | 0.11 → 0.09 | **yes** |

Rule: adopted if R² is at most 0.02 below the model in use and the extreme-season error is lower.

## E3, out-of-range flag (leave-one-year-out)

| Crop · cutoff | share of regions flagged: 2018 / 2022 / 2025 | extreme seasons flagged (≥ half of regions) | other region-seasons flagged | adopt |
|---|---|---|---|---|
| wheat | mid-July | 0.00 / 0.00 / 0.00 | 0 of 3 | 8% | no |
| wheat | end of August | 0.00 / 0.00 / 0.00 | 0 of 3 | 8% | no |
| winter barley | mid-July | 0.00 / 0.00 / 0.62 | 1 of 3 | 4% | no |
| winter barley | end of August | 0.00 / 0.00 / 0.00 | 0 of 3 | 4% | no |
| spring barley | mid-July | 0.00 / 0.00 / 0.00 | 0 of 3 | 2% | no |
| spring barley | end of August | 0.00 / 0.00 / 0.00 | 0 of 3 | 0% | no |

Rule: adopted if at least two of the three extreme seasons and at most one in ten other region-seasons are flagged.

## E4, distance-weighted 80% intervals (leave-one-year-out, nested)

| Crop · cutoff | coverage weighted | coverage unweighted | extreme seasons: weighted vs unweighted | mean half-width weighted / unweighted (t/ha) | adopt |
|---|---|---|---|---|---|
| wheat | mid-July | 75% | 78% | 58% vs 67% | 0.81 / 0.75 | no |
| wheat | end of August | 83% | 83% | 67% vs 67% | 0.82 / 0.74 | no |
| winter barley | mid-July | 83% | 83% | 83% vs 83% | 0.85 / 0.86 | no |
| winter barley | end of August | 85% | 86% | 88% vs 88% | 0.73 / 0.73 | no |
| spring barley | mid-July | 85% | 83% | 96% vs 92% | 0.55 / 0.52 | **yes** |
| spring barley | end of August | 82% | 78% | 96% vs 96% | 0.52 / 0.50 | no |

Rule: adopted if weighted coverage is 75–90% and higher than the unweighted intervals in the extreme seasons.

## Weather coefficients in the full fit (standardised; signs constrained)

| Crop · cutoff | penalty | spring_anom_pct | soil_moist_z | dd30 | winter_anom_pct | compound |
|---|---|---|---|---|---|---|
| wheat | mid-July | 30 | +0.000 | +0.000 | -0.103 | -0.138 | -0.000 |
| wheat | end of August | 100 | +0.000 | +0.000 | -0.000 | -0.064 | -0.019 |
| winter barley | mid-July | 1 | +0.000 | +0.000 | -0.000 | -0.180 | -0.000 |
| winter barley | end of August | 10 | +0.000 | +0.000 | -0.000 | -0.138 | -0.000 |
| spring barley | mid-July | 30 | +0.000 | +0.008 | -0.016 | -0.000 | -0.000 |
| spring barley | end of August | 10 | +0.000 | +0.000 | -0.000 | -0.000 | -0.003 |

## 2026: the out-of-range flag (a fair test: inputs only)

| Crop · cutoff | regions flagged | flag worked (≥ half) |
|---|---|---|
| wheat | mid-July | 5 of 8 | **yes** |
| wheat | end of August | 0 of 8 | no |
| winter barley | mid-July | 0 of 8 | no |
| winter barley | end of August | 0 of 8 | no |
| spring barley | mid-July | 0 of 8 | no |
| spring barley | end of August | 0 of 8 | no |

## 2026 nowcast with E2 and E4 (illustration only: Defra’s provisional figures were known when E was written)

| Crop · cutoff | nowcast, mean of regions | Defra provisional | error | regions inside the 80% interval |
|---|---|---|---|---|
| wheat | mid-July | 7.06 | 7.18 | -0.13 | 7 of 8 |
| wheat | end of August | 7.56 | 7.18 | +0.38 | 6 of 8 |
| winter barley | mid-July | 6.39 | 6.52 | -0.13 | 7 of 8 |
| winter barley | end of August | 6.62 | 6.52 | +0.10 | 6 of 8 |
| spring barley | mid-July | 5.19 | 4.54 | +0.66 | 3 of 8 |
| spring barley | end of August | 5.17 | 4.54 | +0.63 | 3 of 8 |

Limits: eight regions and nine seasons per crop; degree-days at the weather-cell centre, averaged over the crop’s parcels; the confirmatory test is the 2027 harvest; Defra’s final 2026 figures (10 December 2026) will replace the provisional ones in the illustration.
