# WP1 addendum A: grain-fill features

Protocol addendum A ([protocol.md](protocol.md)), written before the features were computed. Same leave-one-year-out scoring as [wp1_results.md](wp1_results.md). Error = predicted minus Defra, England mean of the regional anomalies (t/ha); positive = over-predicted.

Dry-spring years (at least half of the wheat region-years in a dry shock): 2018, 2020, 2022, 2025.

## Wheat

| Model | cutoff | R² | England R² | mean error, dry years | mean abs. error, dry years | mean abs. error, other years |
|---|---|---|---|---|---|---|
| s2+weather | mid-July | +0.64 | +0.78 | -0.15 | 0.36 | 0.30 |
| s2+weather+gf | mid-July | +0.56 | +0.68 | -0.08 | 0.30 | 0.36 |
| s2+weather | end of August | +0.60 | +0.80 | -0.11 | 0.31 | 0.26 |
| s2+weather+gf | end of August | +0.53 | +0.69 | -0.08 | 0.32 | 0.36 |

## Winter barley

| Model | cutoff | R² | England R² | mean error, dry years | mean abs. error, dry years | mean abs. error, other years |
|---|---|---|---|---|---|---|
| s2+weather | mid-July | +0.52 | +0.81 | +0.03 | 0.16 | 0.24 |
| s2+weather+gf | mid-July | +0.44 | +0.62 | +0.03 | 0.18 | 0.41 |
| s2+weather | end of August | +0.61 | +0.86 | +0.11 | 0.20 | 0.21 |
| s2+weather+gf | end of August | +0.57 | +0.78 | +0.15 | 0.25 | 0.26 |

## Spring barley

| Model | cutoff | R² | England R² | mean error, dry years | mean abs. error, dry years | mean abs. error, other years |
|---|---|---|---|---|---|---|
| s2+weather | mid-July | +0.51 | +0.74 | +0.12 | 0.30 | 0.24 |
| s2+weather+gf | mid-July | +0.57 | +0.79 | +0.09 | 0.22 | 0.24 |
| s2+weather | end of August | +0.49 | +0.74 | +0.12 | 0.32 | 0.21 |
| s2+weather+gf | end of August | +0.54 | +0.78 | +0.16 | 0.30 | 0.14 |

## England error by year, wheat (predicted minus Defra, t/ha)

| Year | first run, mid-July | grain fill, mid-July | first run, end of August | grain fill, end of August |
|---|---|---|---|---|
| 2017 | +0.37 | +0.14 | +0.11 | +0.19 |
| 2018 | -0.25 | -0.01 | +0.02 | +0.15 |
| 2019 | +0.28 | -0.18 | +0.31 | -0.09 |
| 2020 | -0.34 | -0.28 | -0.33 | -0.27 |
| 2021 | -0.15 | -0.17 | -0.13 | -0.23 |
| 2022 | -0.44 | -0.48 | -0.51 | -0.52 |
| 2023 | -0.33 | -0.49 | -0.36 | -0.71 |
| 2024 | +0.35 | +0.80 | +0.40 | +0.57 |
| 2025 | +0.41 | +0.44 | +0.37 | +0.33 |

## 2026 nowcast re-issued where R² improved (written 2026-10-12 09:04)

| Crop | cutoff | region | nowcast (t/ha) | 80% interval | 2017–2025 mean |
|---|---|---|---|---|---|
| spring barley | mid-July | East Midlands | 5.56 | 4.83–6.24 | 5.59 |
| spring barley | mid-July | Eastern | 4.93 | 4.25–5.68 | 5.64 |
| spring barley | mid-July | North East | 6.37 | 5.66–7.02 | 5.73 |
| spring barley | mid-July | North West and Merseyside | 4.21 | 3.56–4.91 | 4.19 |
| spring barley | mid-July | South East and London | 5.16 | 4.47–5.93 | 5.68 |
| spring barley | mid-July | South West | 5.24 | 4.54–5.99 | 5.36 |
| spring barley | mid-July | West Midlands | 4.86 | 4.16–5.53 | 4.94 |
| spring barley | mid-July | Yorkshire & The Humber | 6.23 | 5.47–6.89 | 5.68 |
| spring barley | end of August | East Midlands | 5.36 | 4.57–6.02 | 5.59 |
| spring barley | end of August | Eastern | 4.90 | 4.18–5.62 | 5.64 |
| spring barley | end of August | North East | 6.11 | 5.28–6.75 | 5.73 |
| spring barley | end of August | North West and Merseyside | 4.17 | 3.44–4.80 | 4.19 |
| spring barley | end of August | South East and London | 5.01 | 4.28–5.72 | 5.68 |
| spring barley | end of August | South West | 5.11 | 4.38–5.86 | 5.36 |
| spring barley | end of August | West Midlands | 4.56 | 3.77–5.22 | 4.94 |
| spring barley | end of August | Yorkshire & The Humber | 6.09 | 5.24–6.83 | 5.68 |

Means over regions: spring barley end of August: 5.16 (mean 5.35); spring barley mid-July: 5.32 (mean 5.35)
