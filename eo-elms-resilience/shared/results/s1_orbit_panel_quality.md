# Sentinel-1 per-orbit panel: data quality (no scheme-group comparisons)

- Square-season files: 790 (of 790); parcel-seasons: 3,814,000; parcels: 381,400
- Gamma0 (angle-normalised), anomalies within parcel × orbit direction × month; winter = December–February.
- Season 2026 from Sentinel-1A passes only (Sentinel-1A only); 1C passes read darker than 1A.

## Does radar winter brightness follow the weather? (within each ERA5 cell, across seasons)

| Radar measure | weather measure | correlation | cell-seasons |
|---|---|---|---|
| winter_vv_anom | Oct–Mar rainfall anomaly | +0.16 | 16,550 |
| winter_vv_anom | Dec–Feb topsoil moisture (ERA5-Land) | +0.30 | 16,550 |
| winter_vv_anom_1A | Oct–Mar rainfall anomaly | -0.09 | 8,538 |
| winter_vv_anom_1A | Dec–Feb topsoil moisture (ERA5-Land) | +0.40 | 8,538 |
| winter_vh_anom | Oct–Mar rainfall anomaly | +0.17 | 16,550 |
| winter_vh_anom | Dec–Feb topsoil moisture (ERA5-Land) | +0.48 | 16,550 |

First run (all passes blended, no angle or orbit handling): r = +0.10 with October–March rainfall.

## By season

| Season | parcels | median winter passes | share of passes from 1A | median VV anomaly (dB) | same, 1A-only months | median rain vs normal (%) | median topsoil moisture z | % parcels in wet shock |
|---|---|---|---|---|---|---|---|---|
| 2017 | 381,400 | 59 | 50% | +0.02 | +nan | -16 | -0.50 | 0 |
| 2018 | 381,400 | 60 | 50% | +0.17 | +nan | +8 | +0.59 | 0 |
| 2019 | 381,400 | 70 | 58% | -0.35 | +0.06 | -12 | -0.87 | 0 |
| 2020 | 381,400 | 60 | 49% | +0.88 | +nan | +40 | +1.01 | 89 |
| 2021 | 381,400 | 54 | 49% | +0.48 | +nan | +35 | +1.48 | 73 |
| 2022 | 381,400 | 37 | 86% | -0.10 | -0.09 | -1 | +0.16 | 0 |
| 2023 | 381,400 | 29 | 100% | -0.97 | -0.77 | +21 | -1.45 | 8 |
| 2024 | 381,400 | 30 | 100% | +0.08 | +0.26 | +58 | +0.79 | 99 |
| 2025 | 381,400 | 29 | 100% | +0.43 | +0.58 | -5 | +0.36 | 0 |
| 2026 | 381,400 | 29 | 100% | -0.35 | -0.16 | +40 | +1.54 | 70 |

## Reading (12 October 2026)

- **The per-orbit, angle-normalised panel tracks winter soil wetness:** within each weather cell, winter VH follows
  ERA5-Land December–February topsoil moisture at r = +0.48 and VV at +0.30 (first, blended run: +0.10, and against
  rainfall). October–March rainfall is a weaker yardstick than soil moisture (e.g. 2023: wet October–March overall,
  but a dry February and dry soil, which the radar shows).
- **2026 is unexplained and should not be used yet.** The wettest winter of the record (topsoil moisture z +1.54) reads
  darker than normal (−0.35 dB). It is not Sentinel-1C: re-extracting 2026 with Sentinel-1A passes only leaves it dark
  (−0.16 dB in 1A-only months). It is not frost: December–February 2026 was mild (4.2–6.8 °C monthly means). The most
  likely cause is standing water or saturated, ponded fields, which reflect radar away and look dark; a different
  winter crop mix after the 2025 drought may add to it. Until checked against flood records, use 2017–2025 only.
- Seasons 2017–2025 are usable: dry winters (2017, 2019, 2023) read dark, wet ones (2020, 2021, 2024) bright.
