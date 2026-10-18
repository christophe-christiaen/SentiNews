# U1: short-baseline tests and the field score on England's grassland

Protocol: [u1_grassland_protocol.md](u1_grassland_protocol.md), written before extraction. Random sample of 100,000 permanent-grassland parcels (CROME PG01 in ≥ 80% of years, never cereal). Cell × season effects; errors clustered by ERA5 cell. Parcels with Sentinel-2 values: 100,000; with MODIS: 100,000.

## WP2 tests

| Data | test | version | coefficient | SE | p | n |
|---|---|---|---|---|---|---|
| Sentinel-2 · short normal · 2017-2026 | T1 | pooled | +0.262 | 0.003 | 0 | 899,162 |
| Sentinel-2 · short normal · 2017-2026 | T2 | pooled | +0.286 | 0.004 | 0 | 466,204 |
| Sentinel-2 · short normal · 2017-2026 | T1 | field fixed effects | +0.041 | 0.002 | 0 | 899,162 |
| Sentinel-2 · short normal · 2017-2026 | T2 | field fixed effects | +0.104 | 0.004 | 0 | 466,204 |
| Sentinel-2 · short normal · 2017-2026 | T1 | Anderson-Hsiao | +0.020 | 0.003 | 1.29e-11 | 798,944 |
| Sentinel-2 · short normal · 2017-2026 | T2 | Anderson-Hsiao | +0.059 | 0.004 | 0 | 370,853 |
| Sentinel-2 · short normal · 2017-2026 | T3 | pooled | +0.180 | 0.007 | 0 | 243,988 |
| Sentinel-2 · short normal · 2017-2026 | T1 | shuffled seasons (placebo) | +0.073 | 0.002 | 0 | 898,888 |
| Sentinel-2 · short normal · season mean (secondary) | T1 | pooled | +0.311 | 0.004 | 0 | 560,858 |
| Sentinel-2 · short normal · season mean (secondary) | T2 | pooled | +0.347 | 0.005 | 0 | 292,338 |
| Sentinel-2 · short normal · season mean (secondary) | T1 | field fixed effects | +0.028 | 0.003 | 0 | 560,858 |
| Sentinel-2 · short normal · season mean (secondary) | T2 | field fixed effects | +0.044 | 0.005 | 0 | 292,338 |
| Sentinel-2 · short normal · season mean (secondary) | T1 | Anderson-Hsiao | -0.056 | 0.004 | 0 | 423,467 |
| Sentinel-2 · short normal · season mean (secondary) | T2 | Anderson-Hsiao | +0.031 | 0.006 | 1.41e-06 | 228,371 |
| Sentinel-2 · short normal · season mean (secondary) | T3 | pooled | +0.277 | 0.011 | 0 | 159,204 |
| Sentinel-2 · short normal · season mean (secondary) | T1 | shuffled seasons (placebo) | +0.061 | 0.003 | 0 | 516,275 |
| MODIS · long normal · 2002-2026 | T1 | pooled | +0.113 | 0.002 | 0 | 2,497,988 |
| MODIS · long normal · 2002-2026 | T2 | pooled | +0.191 | 0.002 | 0 | 782,732 |
| MODIS · long normal · 2002-2026 | T1 | field fixed effects | +0.063 | 0.001 | 0 | 2,497,988 |
| MODIS · long normal · 2002-2026 | T2 | field fixed effects | +0.079 | 0.002 | 0 | 782,732 |
| MODIS · long normal · 2002-2026 | T1 | Anderson-Hsiao | +0.021 | 0.001 | 0 | 2,397,650 |
| MODIS · long normal · 2002-2026 | T2 | Anderson-Hsiao | +0.023 | 0.002 | 0 | 782,239 |
| MODIS · long normal · 2002-2026 | T3 | pooled | +0.107 | 0.003 | 0 | 489,709 |
| MODIS · long normal · 2002-2026 | T1 | shuffled seasons (placebo) | -0.002 | 0.001 | 0.0454 | 2,398,056 |
| MODIS · long normal · 2017-2026 | T1 | pooled | +0.235 | 0.003 | 0 | 899,307 |
| MODIS · long normal · 2017-2026 | T2 | pooled | +0.278 | 0.003 | 0 | 466,479 |
| MODIS · long normal · 2017-2026 | T1 | field fixed effects | -0.060 | 0.002 | 0 | 899,307 |
| MODIS · long normal · 2017-2026 | T2 | field fixed effects | +0.002 | 0.003 | 0.54 | 466,479 |
| MODIS · long normal · 2017-2026 | T1 | Anderson-Hsiao | +0.027 | 0.002 | 0 | 799,248 |
| MODIS · long normal · 2017-2026 | T2 | Anderson-Hsiao | +0.022 | 0.004 | 2.72e-10 | 370,891 |
| MODIS · long normal · 2017-2026 | T3 | pooled | +0.200 | 0.005 | 0 | 243,854 |
| MODIS · long normal · 2017-2026 | T1 | shuffled seasons (placebo) | +0.065 | 0.002 | 0 | 899,290 |

## Field score (X1 design)

| Version | model | AUC, hit hard next season | lift (top 20%) | base rate |
|---|---|---|---|---|
| V0 · Sentinel-2, normal 2017–2020 | Current stress only (pilot rule) | 0.617 | 1.61 | 20.2% |
| V0 · Sentinel-2, normal 2017–2020 | Fitted score (logistic) | 0.566 | 1.44 | 20.2% |
| V0 · Sentinel-2, normal 2017–2020 | Region only (baseline) | 0.490 | 1.07 | 20.2% |
| V0 · Sentinel-2, normal 2017–2020 | Transparent score (no fitting) | 0.630 | 1.63 | 20.2% |
| V1 · MODIS, normal 2017–2020 | Current stress only (pilot rule) | 0.588 | 1.53 | 20.6% |
| V1 · MODIS, normal 2017–2020 | Fitted score (logistic) | 0.564 | 1.40 | 20.6% |
| V1 · MODIS, normal 2017–2020 | Region only (baseline) | 0.499 | 1.00 | 20.6% |
| V1 · MODIS, normal 2017–2020 | Transparent score (no fitting) | 0.617 | 1.59 | 20.6% |
| V2 · MODIS, normal 2001–2016 | Current stress only (pilot rule) | 0.618 | 1.49 | 28.1% |
| V2 · MODIS, normal 2001–2016 | Fitted score (logistic) | 0.619 | 1.50 | 28.1% |
| V2 · MODIS, normal 2001–2016 | Region only (baseline) | 0.561 | 1.20 | 28.1% |
| V2 · MODIS, normal 2001–2016 | Transparent score (no fitting) | 0.684 | 1.71 | 28.1% |

| Season | V0 · Sentinel-2, normal 2017–2020 | V1 · MODIS, normal 2017–2020 | V2 · MODIS, normal 2001–2016 |
|---|---|---|---|
| 2020 | 0.505 | 0.477 | 0.645 |
| 2021 | 0.577 | 0.561 | 0.678 |
| 2022 | 0.607 | 0.612 | 0.629 |
| 2023 | 0.684 | 0.697 | 0.666 |
| 2024 | 0.640 | 0.632 | 0.693 |
| 2025 | 0.767 | 0.720 | 0.792 |

## Reading (rules fixed in advance)

- **R1, artefact on grass:** pooled − Anderson–Hsiao (T1, Sentinel-2) = +0.242; shuffled placebo +0.073 (p = 0). **Replicates.**
- **R2, carry-over on grass:** Anderson–Hsiao Sentinel-2 · short normal · 2017-2026 T1 +0.020; Sentinel-2 · short normal · 2017-2026 T2 +0.059; MODIS · long normal · 2002-2026 T1 +0.021; MODIS · long normal · 2002-2026 T2 +0.023; MODIS · long normal · 2017-2026 T1 +0.027; MODIS · long normal · 2017-2026 T2 +0.022. **Not all within ±0.05**: reported as evidence of carry-over, with its sign.
- **R3, field score on grass:** transparent-score AUC with the long normal 0.684 (usable, ≥ 0.60); V1 − V2 = -0.067 (robust).

Limits: cutting and grazing move grass NDVI independently of weather (the season-mean outcome is the check); MODIS pixels mix neighbouring fields; a sample, not all grassland.
