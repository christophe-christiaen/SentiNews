# Diagnosing the 2026 nowcast miss (post hoc; the nowcast is unchanged)

## 1. Data quality

Median clear Sentinel-2 observations per field, March–August: 2017: 6, 2018: 22, 2019: 18, 2020: 27, 2021: 19, 2022: 21, 2023: 16, 2024: 15, 2025: 33, 2026: 42.

## 2. Crop mask (wheat fields in the panel)

| region                    |   CROME wheat fields 2025 |   classifier wheat fields 2026 |   change |
|:--------------------------|--------------------------:|-------------------------------:|---------:|
| East Midlands             |                     29285 |                          24901 |   -0.15  |
| Eastern                   |                     39383 |                          28907 |   -0.266 |
| North East                |                      6680 |                           5678 |   -0.15  |
| North West and Merseyside |                      2506 |                           1858 |   -0.259 |
| South East and London     |                     16160 |                          14669 |   -0.092 |
| South West                |                     13413 |                          10410 |   -0.224 |
| West Midlands             |                     15402 |                          11780 |   -0.235 |
| Yorkshire & The Humber    |                     22366 |                          17868 |   -0.201 |

Defra (June survey): wheat area in England −1.8% in 2026. Classifier check on 2025: wheat precision 0.94, recall 0.86.

## 3. Was 2026 outside the training range? (wheat, anomalies vs 2017–2025)

| region                    |   features beyond ±2 SD of 2017–2025 |   largest |z| | feature     |
|:--------------------------|-------------------------------------:|--------------:|:------------|
| East Midlands             |                                    5 |           4.2 | hot_days_28 |
| Eastern                   |                                    7 |           4.3 | hot_days_28 |
| North East                |                                    0 |           1.8 | ndre_p04    |
| North West and Merseyside |                                    1 |           2   | ndmi_p09    |
| South East and London     |                                    7 |           5.2 | hot_days_28 |
| South West                |                                    4 |           5.1 | hot_days_28 |
| West Midlands             |                                    4 |           4.9 | hot_days_28 |
| Yorkshire & The Humber    |                                    2 |           2.4 | hot_days_28 |

## 4. What pushed the 2026 wheat prediction (ridge contributions, t/ha, mean over regions)

Ridge penalty 0.3. Positive = pushed the prediction above the region's 2017–2025 mean.

| Feature group | contribution |
|---|---|
| NDMI early Jul (k9) | -0.80 |
| NDVI Mar–Apr (k1–4) | -0.80 |
| NDMI Mar–Apr (k1–4) | +0.78 |
| weather: hot_days_28 | +0.69 |
| NDRE Mar–Apr (k1–4) | +0.63 |
| NDVI May–Jun (k5–8) | +0.39 |
| NDRE May–Jun (k5–8) | -0.32 |
| NDVI early Jul (k9) | -0.29 |
| weather: soil_moist_z | +0.22 |
| NDMI May–Jun (k5–8) | -0.15 |

Sum of contributions (predicted anomaly), mean over regions: +0.47 t/ha; actual anomaly: -0.41 t/ha.

Same, 2025 (model trained without 2025) next to 2026:

|                      |   2025 (held out) |   2026 |
|:---------------------|------------------:|-------:|
| NDRE early Jul (k9)  |             -0.87 |   0.04 |
| NDMI early Jul (k9)  |             -0.69 |  -0.8  |
| NDVI Mar–Apr (k1–4)  |              0.26 |  -0.8  |
| NDMI Mar–Apr (k1–4)  |              0.02 |   0.78 |
| weather: hot_days_28 |              0.15 |   0.69 |
| NDRE Mar–Apr (k1–4)  |             -0.22 |   0.63 |
| NDVI early Jul (k9)  |              0.6  |  -0.29 |
| NDVI May–Jun (k5–8)  |              0.46 |   0.39 |

## 5. Dry years compared (wheat areas; error = predicted minus Defra; 2017–2025 held out, 2026 the nowcast)

|      |   Mar–May water balance vs normal (mm) |   Jun–Jul water balance vs normal (mm) |   Jun–Jul temperature vs normal (°C) |   days ≥ 28 °C (Jun–Aug) |   England error, wheat (t/ha) |
|-----:|---------------------------------------:|---------------------------------------:|-------------------------------------:|-------------------------:|------------------------------:|
| 2017 |                                 -21.9  |                                  27.85 |                                 0.81 |                     0.66 |                          0.37 |
| 2018 |                                  94.23 |                                -150.37 |                                 2.05 |                     2.05 |                         -0.25 |
| 2019 |                                 -12.36 |                                  70.84 |                                 0.51 |                     2.36 |                          0.28 |
| 2020 |                                -191.6  |                                  15.6  |                                -0.09 |                     3.54 |                         -0.34 |
| 2021 |                                   7.02 |                                  44.07 |                                 0.96 |                     0.06 |                         -0.15 |
| 2022 |                                 -41.26 |                                 -97.51 |                                 1.15 |                     5.75 |                         -0.44 |
| 2023 |                                  77.65 |                                 -20.15 |                                 0.94 |                     0.19 |                         -0.33 |
| 2024 |                                 107.3  |                                 -11.92 |                                -0.26 |                     0.42 |                          0.35 |
| 2025 |                                -160.88 |                                 -86.69 |                                 2.09 |                     3.22 |                          0.41 |
| 2026 |                                -139.03 |                                -172.94 |                                 2.86 |                     9.63 |                          0.89 |


## What this says (12 October 2026)

- **Not a data-quality problem.** 2026 had the most clear Sentinel-2 views of any season (median 42 per field).
- **The main cause is extrapolation on heat, with the wrong sign.** Summer 2026 had 9.6 days ≥ 28 °C over wheat
  areas, far beyond anything in 2017–2025 (maximum 5.75 in 2022); in the south and west it sat 4–5 SD outside the
  training range. In 2017–2025 hotter summers happened to come with average-or-better yields (2018 and 2022 were
  under-predicted), so the model learned a *positive* weight on hot days, and extrapolated it: hot days alone pushed
  the 2026 prediction up by about +0.7 t/ha, roughly the size of the miss (+0.47 predicted vs −0.41 actual anomaly).
  The regions with the most extreme heat (South East z 5.2, South West 5.1, West Midlands 4.9) are the ones missed
  by 1.5–1.8 t/ha; the North East, inside the range, was right.
- **2026 was a compound drought.** It had the driest early summer (−173 mm water balance in June–July), the hottest
  (+2.9 °C) and a dry spring (−139 mm). 2025, the other over-predicted year, was dry in both spring and early summer
  too. 2018, 2020 and 2022, all under-predicted, were dry in only one of the two. With two cases this is a pattern
  to test, not a finding.
- **The crop mask may add a little.** The classifier found 9–27% fewer wheat fields than CROME had in 2025, while
  Defra reports wheat area down only 1.8%; if the missed fields are the most stressed (least wheat-like), that biases
  the forecast up. In 2025 the effect was small (+0.03 t/ha), and the regional pattern here is mixed.
- **The model is also unstable.** With 39 features and 64 training region-years, the ridge penalty chosen was low
  (0.3), and early-season contributions are large and cancel each other (NDVI March–April −0.80, NDMI +0.78).

## Proposed fix (to be written as protocol addendum B before testing)

1. Do not let weather features extrapolate: clip each to its training range, and constrain heat and water deficit to
   act only in the damaging direction (heat can lower, never raise, the prediction).
2. Add a compound term (dry spring and dry or hot early summer together).
3. Stronger regularisation or fewer features (e.g. one value per index per month).
4. Score by leave-one-year-out as before, with 2025 as the key held-out year; 2026 can only be used as a test once,
   and only after the rules are fixed (Defra's final figures arrive on 10 December).
