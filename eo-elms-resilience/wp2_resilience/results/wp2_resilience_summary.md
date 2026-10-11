# WP2 · Parcel-level resilience of England's cereal land, 2017–2026 (no scheme-group comparisons)

- Parcels: 381,400; parcel-seasons: 3,814,000. Stress index S = mean of July and peak NDVI z-scores vs each parcel's 2017–2020 seasons.
- Shock seasons from ERA5-Land (dry or heat shock for the parcel's cell, pre-registration definitions).

## Tests (cell × season effects absorbed; errors clustered by ERA5 cell)

- **T1 legacy** (S_t on S_t−1): +0.199 (SE 0.002, p <0.001; n 3,429,308, cells 1,655)
- **T2 unrecovered land is hit harder** (shock seasons): +0.210 (SE 0.002, p <0.001; n 1,965,095, cells 1,655)
- **T3 stress debt slows rebound** (carry-over 0.5): +0.176 (SE 0.004, p <0.001; n 931,183, cells 1,655)
- T3 with carry-over 0.3: +0.173 (SE 0.004, p <0.001; n 931,183, cells 1,655); 0.7: +0.174 (SE 0.004, p <0.001; n 931,183, cells 1,655)

Pilot comparison (50 MODIS sites): T1 +0.12, T2 +0.35, T3 0.31 (suggestive, threshold-dependent).

## Resilience types, 2018–2026 (share of cereal parcels)

|                   |   share |
|:------------------|--------:|
| Bounced back      |   0.291 |
| Little affected   |   0.249 |
| Persistent stress |   0.227 |
| Back-to-back hits |   0.123 |
| Slow recovery     |   0.11  |

- **Repeated stress** (persistent or back-to-back): 35.0% of cereal parcels

## By region

| region                   |   parcels |   repeated |   resistance |   recovery |   debt_2026 |
|:-------------------------|----------:|-----------:|-------------:|-----------:|------------:|
| East Midlands            |     70170 |      0.389 |       -0.326 |      0.268 |      -1.414 |
| East of England          |     90492 |      0.338 |       -0.337 |      0.313 |      -1.325 |
| London                   |       357 |      0.412 |       -0.302 |      0.187 |      -1.285 |
| South East               |     44680 |      0.34  |       -0.316 |      0.187 |      -1.256 |
| North East               |     18425 |      0.371 |       -0.341 |      0.212 |      -1.162 |
| Yorkshire and the Humber |     54175 |      0.358 |       -0.341 |      0.147 |      -1.134 |
| West Midlands            |     41184 |      0.323 |       -0.29  |      0.224 |      -1.08  |
| South West               |     48860 |      0.325 |       -0.306 |      0.07  |      -1.046 |
| North West               |     12898 |      0.36  |       -0.176 |     -0.051 |      -0.901 |

## National medians by season

|   year |      S |   shock |      D |
|-------:|-------:|--------:|-------:|
|   2017 |  0.151 |   0     |  0     |
|   2018 | -0.15  |   0.962 | -0.352 |
|   2019 |  0.371 |   0.314 | -0.281 |
|   2020 | -0.222 |   0.82  | -0.436 |
|   2021 |  0.416 |   0.026 | -0.355 |
|   2022 | -0.123 |   0.939 | -0.453 |
|   2023 |  0.038 |   0.127 | -0.529 |
|   2024 | -0.139 |   0     | -0.701 |
|   2025 | -0.611 |   0.988 | -1.158 |
|   2026 | -0.502 |   0.983 | -1.218 |

Map: results/maps/wp2_resilience_types_debt.png. Caveats: the 2017–2020 baseline contains the 2018 and 2020 droughts, so z-scores are relative to a recent, not a drought-free, normal; 2017 has thin coverage; parcel points sample the field centre (15 m).

## Robustness to crop rotation

Cereal in both seasons (CROME), effects absorbed within cell × season × crop; 2026 excluded (no CROME).

| test                  |   coef |    se | p      |       n |
|:----------------------|-------:|------:|:-------|--------:|
| T1 legacy             |  0.22  | 0.003 | <0.001 | 1233652 |
| T2 hit harder         |  0.197 | 0.004 | <0.001 |  633316 |
| T3 debt slows rebound |  0.112 | 0.005 | <0.001 |  385110 |
