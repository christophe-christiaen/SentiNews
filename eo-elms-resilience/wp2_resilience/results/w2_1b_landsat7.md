# W2-1b: why the Landsat 7-only version disagrees

Protocol: [w2_1b_landsat7_protocol.md](w2_1b_landsat7_protocol.md), written before any diagnostic was run. Reference Anderson–Hsiao T1: all-sensor -0.020 (2002–2026), Landsat 7 only -0.083 (2002–2023).

| Version | test | estimator | coefficient | SE | p | n |
|---|---|---|---|---|---|---|
| D1 · all-sensor on L7 field-seasons | T1 | pooled | +0.047 | 0.002 | 0 | 4,340,599 |
| D1 · all-sensor on L7 field-seasons | T2 | pooled | +0.070 | 0.002 | 0 | 1,534,951 |
| D1 · all-sensor on L7 field-seasons | T1 | field fixed effects | -0.036 | 0.002 | 0 | 4,340,599 |
| D1 · all-sensor on L7 field-seasons | T2 | field fixed effects | -0.018 | 0.002 | 4.88e-14 | 1,534,951 |
| D1 · all-sensor on L7 field-seasons | T1 | Anderson-Hsiao | -0.032 | 0.002 | 0 | 3,237,822 |
| D1 · all-sensor on L7 field-seasons | T2 | Anderson-Hsiao | -0.033 | 0.002 | 0 | 1,275,897 |
| D1 · all-sensor on L7 field-seasons | T3 | pooled | +0.132 | 0.003 | 0 | 1,014,181 |
| D1 · all-sensor on L7 field-seasons | T1 | shuffled seasons (placebo) | -0.002 | 0.001 | 0.00228 | 3,948,380 |
| D2 · all-sensor plus L7 excess noise | T1 | pooled | +0.025 | 0.001 | 0 | 4,340,599 |
| D2 · all-sensor plus L7 excess noise | T2 | pooled | +0.038 | 0.001 | 0 | 1,534,951 |
| D2 · all-sensor plus L7 excess noise | T1 | field fixed effects | -0.049 | 0.001 | 0 | 4,340,599 |
| D2 · all-sensor plus L7 excess noise | T2 | field fixed effects | -0.030 | 0.002 | 0 | 1,534,951 |
| D2 · all-sensor plus L7 excess noise | T1 | Anderson-Hsiao | -0.017 | 0.001 | 0 | 3,237,822 |
| D2 · all-sensor plus L7 excess noise | T2 | Anderson-Hsiao | -0.016 | 0.002 | 0 | 1,275,897 |
| D2 · all-sensor plus L7 excess noise | T3 | pooled | +0.099 | 0.003 | 0 | 1,014,181 |
| D2 · all-sensor plus L7 excess noise | T1 | shuffled seasons (placebo) | -0.002 | 0.001 | 0.00455 | 3,948,107 |
| D3a · L7, both windows | T1 | pooled | +0.107 | 0.007 | 0 | 117,788 |
| D3a · L7, both windows | T2 | pooled | +0.146 | 0.008 | 0 | 39,570 |
| D3a · L7, both windows | T1 | field fixed effects | -0.053 | 0.005 | 0 | 117,788 |
| D3a · L7, both windows | T2 | field fixed effects | -0.012 | 0.009 | 0.214 | 39,570 |
| D3a · L7, both windows | T1 | Anderson-Hsiao | -0.026 | 0.008 | 0.00135 | 64,102 |
| D3a · L7, both windows | T2 | Anderson-Hsiao | -0.022 | 0.015 | 0.136 | 25,579 |
| D3a · L7, both windows | T3 | pooled | +0.156 | 0.011 | 0 | 34,545 |
| D3a · L7, both windows | T1 | shuffled seasons (placebo) | +0.014 | 0.005 | 0.00253 | 93,899 |
| D3b · L7, >= 12 baseline seasons | T1 | pooled | -0.038 | 0.003 | 0 | 1,185,414 |
| D3b · L7, >= 12 baseline seasons | T2 | pooled | -0.009 | 0.003 | 0.00728 | 422,883 |
| D3b · L7, >= 12 baseline seasons | T1 | field fixed effects | -0.092 | 0.002 | 0 | 1,185,414 |
| D3b · L7, >= 12 baseline seasons | T2 | field fixed effects | -0.070 | 0.003 | 0 | 422,883 |
| D3b · L7, >= 12 baseline seasons | T1 | Anderson-Hsiao | -0.093 | 0.003 | 0 | 916,735 |
| D3b · L7, >= 12 baseline seasons | T2 | Anderson-Hsiao | -0.107 | 0.004 | 0 | 360,086 |
| D3b · L7, >= 12 baseline seasons | T3 | pooled | +0.072 | 0.004 | 0 | 253,352 |
| D3b · L7, >= 12 baseline seasons | T1 | shuffled seasons (placebo) | -0.019 | 0.001 | 0 | 1,126,441 |
| D4 · L7, tests 2017-2023 | T1 | pooled | +0.059 | 0.002 | 0 | 2,175,867 |
| D4 · L7, tests 2017-2023 | T2 | pooled | +0.050 | 0.002 | 0 | 999,945 |
| D4 · L7, tests 2017-2023 | T1 | field fixed effects | -0.216 | 0.001 | 0 | 2,175,867 |
| D4 · L7, tests 2017-2023 | T2 | field fixed effects | -0.135 | 0.004 | 0 | 999,945 |
| D4 · L7, tests 2017-2023 | T1 | Anderson-Hsiao | -0.096 | 0.002 | 0 | 2,052,332 |
| D4 · L7, tests 2017-2023 | T2 | Anderson-Hsiao | -0.113 | 0.003 | 0 | 954,657 |
| D4 · L7, tests 2017-2023 | T3 | pooled | +0.116 | 0.003 | 0 | 742,267 |
| D4 · L7, tests 2017-2023 | T1 | shuffled seasons (placebo) | +0.086 | 0.002 | 0 | 1,881,483 |

## Descriptive

- baseline seasons, median (all-sensor, L7): [12.0, 5.0]
- L7 field-seasons 2002-2023 with both windows (share): 0.37097344710873814
- all-sensor field-seasons 2002-2023 with both windows (share): 0.7514691090241693
- D2 excess variance of L7 (within field): 0.44689356336331987
- D3b fields with >= 12 L7 baseline seasons: 80143

## Reading (rules fixed in advance; Anderson–Hsiao T1)

- **R1 · sample and period not the cause** (D1 within ±0.05 of -0.020): D1 -0.032 → **yes**.
- **R2 · L7-sized noise reproduces the gap** (D2 within ±0.03 of -0.083): D2 -0.017 → **no**.
- **R3 · L7, both windows removes the gap** (within ±0.05 of -0.020): -0.026 → **yes**.
- **R3 · L7, >= 12 baseline seasons removes the gap** (within ±0.05 of -0.020): -0.093 → **no**.
- **R3 · L7, tests 2017-2023 removes the gap** (within ±0.05 of -0.020): -0.096 → **no**.

**Conclusion:** the flag is attributed to Landsat 7's data, not to the sensor or to carry-over.
