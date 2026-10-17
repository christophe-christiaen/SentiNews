# Lender score under a long baseline (X1)

Protocol in [lender_baseline_protocol.md](lender_baseline_protocol.md), written before running. Same features, targets and rolling-origin back-test (scoring seasons 2020–2025) as the published score; only the stress index changes. 381,400 parcels with both Sentinel-2 and MODIS values; panel 2017–2026 in every version.

## Mean over scoring seasons 2020–2025

| Version | model | hit hard next season: AUC | lift (top 20%) | base rate | worst 20% of region: AUC |
|---|---|---|---|---|---|
| V0 · Sentinel-2, normal 2017–2020 | Region only (baseline) | 0.496 | 1.04 | 23.9% | 0.500 |
| V0 · Sentinel-2, normal 2017–2020 | Current stress only (pilot rule) | 0.601 | 1.51 | 23.9% | 0.610 |
| V0 · Sentinel-2, normal 2017–2020 | Transparent score (no fitting) | 0.632 | 1.57 | 23.9% | 0.645 |
| V0 · Sentinel-2, normal 2017–2020 | Fitted score (logistic) | 0.571 | 1.35 | 23.9% | 0.583 |
| V1 · MODIS, normal 2017–2020 | Region only (baseline) | 0.530 | 1.15 | 20.2% | 0.500 |
| V1 · MODIS, normal 2017–2020 | Current stress only (pilot rule) | 0.575 | 1.48 | 20.2% | 0.576 |
| V1 · MODIS, normal 2017–2020 | Transparent score (no fitting) | 0.612 | 1.53 | 20.2% | 0.616 |
| V1 · MODIS, normal 2017–2020 | Fitted score (logistic) | 0.568 | 1.37 | 20.2% | 0.565 |
| V2 · MODIS, normal 2001–2016 | Region only (baseline) | 0.526 | 1.22 | 24.7% | 0.500 |
| V2 · MODIS, normal 2001–2016 | Current stress only (pilot rule) | 0.605 | 1.49 | 24.7% | 0.602 |
| V2 · MODIS, normal 2001–2016 | Transparent score (no fitting) | 0.656 | 1.70 | 24.7% | 0.649 |
| V2 · MODIS, normal 2001–2016 | Fitted score (logistic) | 0.612 | 1.56 | 24.7% | 0.606 |

## Transparent score by scoring season (AUC, hit hard next season)

| Season | V0 · Sentinel-2, normal 2017–2020 | V1 · MODIS, normal 2017–2020 | V2 · MODIS, normal 2001–2016 |
|---|---|---|---|
| 2020 | 0.495 | 0.480 | 0.667 |
| 2021 | 0.579 | 0.565 | 0.631 |
| 2022 | 0.640 | 0.629 | 0.651 |
| 2023 | 0.636 | 0.655 | 0.633 |
| 2024 | 0.686 | 0.660 | 0.660 |
| 2025 | 0.754 | 0.684 | 0.691 |

**Reading (fixed in advance):** V1 − V2 = -0.043 AUC for the transparent score; below 0.03, so the short normal does not materially inflate the published back-test.

Limits: MODIS pixels are 250 m and mix neighbouring fields; a 2001–2016 normal can drift by 2017–2026, so V2 is free of the in-panel shared error, not of every baseline effect.
