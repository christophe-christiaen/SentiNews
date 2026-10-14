# WP1 addendum B: no extrapolation, damage-only weather, compound drought

Protocol addendum B ([protocol.md](protocol.md)), written 14 October 2026 before this ran. Leave-one-year-out over 2017–2025, same scoring as the first run. Dry-spring years: 2018, 2020, 2022, 2025. Error = predicted minus Defra (England mean of regional anomalies, t/ha).

| Crop | cutoff | R² first run | R² addendum B | dry-year mean error (first → B) | dry-year mean abs. error (first → B) | 2025 error (first → B) | adopt for 2027 |
|---|---|---|---|---|---|---|---|
| wheat | mid-July | +0.64 | +0.55 | -0.15 → +0.00 | 0.36 → 0.40 | +0.41 → +0.80 | no |
| wheat | end of August | +0.60 | +0.64 | -0.11 → -0.08 | 0.31 → 0.32 | +0.37 → +0.47 | no |
| winter barley | mid-July | +0.52 | +0.54 | +0.03 → -0.03 | 0.16 → 0.19 | -0.15 → -0.09 | no |
| winter barley | end of August | +0.61 | +0.57 | +0.11 → -0.02 | 0.20 → 0.18 | -0.19 → -0.12 | no |
| spring barley | mid-July | +0.51 | +0.58 | +0.12 → -0.01 | 0.30 → 0.15 | +0.30 → +0.11 | yes |
| spring barley | end of August | +0.49 | +0.60 | +0.12 → +0.01 | 0.32 → 0.11 | +0.26 → +0.09 | yes |

## Wheat, England error by year (mid-July)

| Year | first run | addendum B |
|---|---|---|
| 2017 | +0.37 | +0.29 |
| 2018 | -0.25 | -0.04 |
| 2019 | +0.28 | -0.29 |
| 2020 | -0.34 | -0.10 |
| 2021 | -0.15 | -0.13 |
| 2022 | -0.44 | -0.65 |
| 2023 | -0.33 | +0.16 |
| 2024 | +0.35 | +0.56 |
| 2025 | +0.41 | +0.80 |

## Weather coefficients in the full fit (standardised, sign-constrained)

| Crop, cutoff | penalty | spring_anom_pct | soil_moist_z | hot_days_28 | winter_anom_pct | compound |
|---|---|---|---|---|---|---|
| wheat | mid-July | 100 | +0.000 | +0.000 | -0.000 | -0.074 | -0.007 |
| wheat | end of August | 100 | +0.000 | +0.000 | -0.000 | -0.064 | -0.019 |
| winter barley | mid-July | 1 | +0.000 | +0.000 | -0.000 | -0.180 | -0.000 |
| winter barley | end of August | 10 | +0.000 | +0.000 | -0.000 | -0.138 | -0.000 |
| spring barley | mid-July | 30 | +0.000 | +0.007 | -0.000 | -0.000 | -0.004 |
| spring barley | end of August | 10 | +0.000 | +0.000 | -0.000 | -0.000 | -0.003 |

## 2026, illustration only (Defra known when the addendum was written; not a test)

| Crop, cutoff | addendum B, mean of regions | Defra, mean of regions | error | first nowcast error |
|---|---|---|---|---|
| wheat | mid-July | 7.56 | 7.18 | +0.37 | +0.89 |
| wheat | end of August | 7.56 | 7.18 | +0.38 | +0.80 |
| winter barley | mid-July | 6.39 | 6.52 | -0.13 | +0.79 |
| winter barley | end of August | 6.62 | 6.52 | +0.10 | +0.79 |
| spring barley | mid-July | 5.26 | 4.54 | +0.72 | +0.76 |
| spring barley | end of August | 5.17 | 4.54 | +0.63 | +0.67 |

## Reading (14 October 2026)

- **Adopted for spring barley only**, under the rule set in advance: R² 0.51 → 0.58 (mid-July) and 0.49 → 0.60 (end of
  August), with dry-year errors cut from about 0.3 to 0.1–0.15 t/ha.
- **Not adopted for wheat or winter barley.** Wheat at mid-July loses skill (R² 0.64 → 0.55) and its 2025 error grows
  (+0.41 → +0.80); at end of August R² rises (0.60 → 0.64) but the dry-year error does not fall (0.31 → 0.32), so the
  rule keeps the first-run model. Winter barley changes little either way.
- **With the sign constraints, the weather terms mostly drop to zero.** Heat can no longer push a forecast up, and
  there is not enough evidence in 2017–2025 for it to push one down; only winter rainfall keeps a (negative) weight.
  The 2025 over-prediction comes from the Sentinel-2 features themselves, not from the weather.
- **2026, illustration only:** addendum B would have put wheat at 7.56 t/ha (Defra 7.18; first nowcast 8.07) and
  winter barley within 0.1–0.13 of Defra (first nowcast +0.79). That looks much better, but it was designed after
  Defra's figures were known, so it is not evidence. The real test of the wheat question is the 2027 harvest.
