# W2-1: the carry-over tests with a Landsat 30 m long baseline

Protocol: [w2_1_landsat_protocol.md](w2_1_landsat_protocol.md), written before any Landsat value was extracted. Field-centre 30 m pixel; Landsat 5, 7, 8, 9 (no cross-sensor coefficients; cell × season effects); errors clustered by ERA5 cell. Parcels with a usable normal: long 381,400, short 381,399, Landsat 7 only 353,008.

| Version | test | estimator | coefficient | SE | p | n |
|---|---|---|---|---|---|---|
| L-long · 2002-2026 | T1 | pooled | +0.046 | 0.002 | 0 | 8,839,315 |
| L-long · 2002-2026 | T2 | pooled | +0.090 | 0.002 | 0 | 3,154,857 |
| L-long · 2002-2026 | T1 | field fixed effects | -0.001 | 0.001 | 0.469 | 8,839,315 |
| L-long · 2002-2026 | T2 | field fixed effects | +0.006 | 0.001 | 3.86e-05 | 3,154,857 |
| L-long · 2002-2026 | T1 | Anderson-Hsiao | -0.020 | 0.001 | 0 | 8,174,354 |
| L-long · 2002-2026 | T2 | Anderson-Hsiao | -0.021 | 0.002 | 0 | 3,114,447 |
| L-long · 2002-2026 | T3 | pooled | +0.088 | 0.003 | 0 | 1,639,255 |
| L-long · 2002-2026 | T1 | shuffled seasons (placebo) | +0.001 | 0.001 | 0.0278 | 8,488,018 |
| L-long · 2017-2026 | T1 | pooled | +0.161 | 0.002 | 0 | 3,810,557 |
| L-long · 2017-2026 | T2 | pooled | +0.157 | 0.002 | 0 | 1,966,029 |
| L-long · 2017-2026 | T1 | field fixed effects | -0.074 | 0.001 | 0 | 3,810,557 |
| L-long · 2017-2026 | T2 | field fixed effects | -0.036 | 0.002 | 0 | 1,966,029 |
| L-long · 2017-2026 | T1 | Anderson-Hsiao | -0.011 | 0.002 | 1.58e-10 | 3,808,690 |
| L-long · 2017-2026 | T2 | Anderson-Hsiao | +0.004 | 0.002 | 0.0839 | 1,965,505 |
| L-long · 2017-2026 | T3 | pooled | +0.159 | 0.003 | 0 | 931,118 |
| L-long · 2017-2026 | T1 | shuffled seasons (placebo) | +0.127 | 0.002 | 0 | 3,429,558 |
| L-short · 2017-2026 | T1 | pooled | +0.138 | 0.002 | 0 | 3,810,881 |
| L-short · 2017-2026 | T2 | pooled | +0.158 | 0.002 | 0 | 1,966,442 |
| L-short · 2017-2026 | T1 | field fixed effects | -0.031 | 0.001 | 0 | 3,810,881 |
| L-short · 2017-2026 | T2 | field fixed effects | +0.036 | 0.002 | 0 | 1,966,442 |
| L-short · 2017-2026 | T1 | Anderson-Hsiao | +0.010 | 0.002 | 1.6e-09 | 3,808,736 |
| L-short · 2017-2026 | T2 | Anderson-Hsiao | +0.017 | 0.002 | 0 | 1,965,898 |
| L-short · 2017-2026 | T3 | pooled | +0.115 | 0.003 | 0 | 931,052 |
| L-short · 2017-2026 | T1 | shuffled seasons (placebo) | +0.076 | 0.001 | 0 | 3,429,856 |
| L7 only · 2002-2023 | T1 | pooled | -0.010 | 0.002 | 3.83e-08 | 4,340,599 |
| L7 only · 2002-2023 | T2 | pooled | +0.018 | 0.002 | 0 | 1,534,951 |
| L7 only · 2002-2023 | T1 | field fixed effects | -0.096 | 0.002 | 0 | 4,340,599 |
| L7 only · 2002-2023 | T2 | field fixed effects | -0.073 | 0.002 | 0 | 1,534,951 |
| L7 only · 2002-2023 | T1 | Anderson-Hsiao | -0.083 | 0.002 | 0 | 3,237,822 |
| L7 only · 2002-2023 | T2 | Anderson-Hsiao | -0.101 | 0.003 | 0 | 1,275,897 |
| L7 only · 2002-2023 | T3 | pooled | +0.096 | 0.002 | 0 | 1,014,181 |
| L7 only · 2002-2023 | T1 | shuffled seasons (placebo) | -0.011 | 0.001 | 0 | 3,947,682 |

## Reading (rules fixed in advance)

- **Confirms MODIS** (Anderson–Hsiao T1 and T2 within ±0.05, long normal): T1 -0.020, T2 -0.021 → **yes**.
- **Artefact on Landsat** (short normal): pooled − Anderson–Hsiao = +0.128; placebo +0.076 (p = 0) → **replicates**.
- **Pixel mixing**: Landsat Anderson–Hsiao T1 -0.020 vs MODIS -0.019 → did not matter (within 0.05).
- **Sensor mix (sensitivity)**: Landsat 7 only T1 -0.083 → **flagged** as a limit.

Limits: Landsat 7 alone is patchy in cloudy western summers (2–3 overpasses in the window); 30 m field-centre pixels can still touch field edges in small fields.
