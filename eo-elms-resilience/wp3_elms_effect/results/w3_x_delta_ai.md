# Addendum 5 · ΔAI: what AI embeddings add on top of the no-AI products

Run plan in the record of [w3_x_addendum5_products_protocol.md](w3_x_addendum5_products_protocol.md) (19 November 2026, fixed before any statistic). N = Sentinel-2 indices + NDTI + Sentinel-1. ΔAI(E) = I*(N + E) − I*(N), comparison B (management-only scheme land). Paired bootstrap of parcels within held-out regions (registered), Holm over the three embeddings within each family; 10 km block intervals (#9) beside. E **adds to the indices** if the Holm-adjusted interval lies above zero, N + E passes calibration (both controls within ±0.02 against never-treated land) and invariance (|I*(A) − I*(B)| < 0.03).

## Calibration (controls against never-treated land, I*)

| Product | Buffer strips | Management only | passes ±0.02 |
|---|---|---|---|
| N | +0.008 | +0.015 | yes |
| N + AlphaEarth | +0.017 | +0.023 | no |
| N + TESSERA | +0.024 | +0.035 | no |
| N + Presto | +0.011 | +0.020 | no |

## ΔAI by option family (comparison B)

| Family | I*(N) | Embedding | ΔAI | Holm-adjusted interval (parcels) | p (Holm) | 10 km block interval | invariance | Reading |
|---|---|---|---|---|---|---|---|---|
| Herbal leys | +0.170 | AlphaEarth | +0.018 | +0.009 to +0.027 | 0.000 | +0.007 to +0.029 | 0.027 | interval above zero, but fails calibration |
| Herbal leys | +0.170 | TESSERA | +0.016 | +0.008 to +0.024 | 0.000 | +0.007 to +0.025 | 0.017 | interval above zero, but fails calibration |
| Herbal leys | +0.170 | Presto | +0.004 | -0.002 to +0.011 | 0.194 | -0.003 to +0.012 | 0.022 | adds nothing shown |
| Cover crops | +0.056 | AlphaEarth | +0.023 | +0.013 to +0.032 | 0.000 | +0.012 to +0.033 | 0.020 | interval above zero, but fails calibration |
| Cover crops | +0.056 | TESSERA | +0.034 | +0.024 to +0.044 | 0.000 | +0.023 to +0.044 | 0.020 | interval above zero, but fails calibration |
| Cover crops | +0.056 | Presto | +0.006 | -0.002 to +0.012 | 0.148 | -0.003 to +0.014 | 0.004 | adds nothing shown |
| No-till | +0.094 | AlphaEarth | +0.006 | -0.001 to +0.013 | 0.116 | -0.003 to +0.014 | 0.026 | adds nothing shown |
| No-till | +0.094 | TESSERA | +0.013 | +0.005 to +0.023 | 0.000 | +0.002 to +0.025 | 0.027 | interval above zero, but fails calibration |
| No-till | +0.094 | Presto | +0.006 | -0.001 to +0.015 | 0.116 | -0.004 to +0.016 | 0.023 | adds nothing shown |
| In-field flower and bird-food plots | +0.078 | AlphaEarth | +0.012 | +0.004 to +0.020 | 0.000 | +0.002 to +0.021 | 0.005 | interval above zero, but fails calibration |
| In-field flower and bird-food plots | +0.078 | TESSERA | +0.019 | +0.011 to +0.027 | 0.000 | +0.011 to +0.029 | 0.017 | interval above zero, but fails calibration |
| In-field flower and bird-food plots | +0.078 | Presto | +0.005 | -0.002 to +0.012 | 0.142 | -0.003 to +0.013 | 0.009 | adds nothing shown |
| Margins and corners | +0.008 | AlphaEarth | -0.003 | -0.011 to +0.006 | 0.968 | -0.010 to +0.005 | 0.018 | adds nothing shown |
| Margins and corners | +0.008 | TESSERA | -0.002 | -0.010 to +0.005 | 0.968 | -0.011 to +0.006 | 0.025 | adds nothing shown |
| Margins and corners | +0.008 | Presto | +0.005 | -0.004 to +0.014 | 0.714 | -0.005 to +0.015 | 0.008 | adds nothing shown |
| Grassland options | +0.069 | AlphaEarth | +0.001 | -0.009 to +0.010 | 1.000 | -0.010 to +0.012 | 0.033 | adds nothing shown |
| Grassland options | +0.069 | TESSERA | +0.008 | -0.005 to +0.020 | 0.372 | -0.006 to +0.022 | 0.017 | adds nothing shown |
| Grassland options | +0.069 | Presto | -0.002 | -0.012 to +0.009 | 1.000 | -0.013 to +0.010 | 0.017 | adds nothing shown |

Invariance of N alone: Herbal leys 0.014; Cover crops 0.008; No-till 0.017; In-field flower and bird-food plots 0.015; Margins and corners 0.009; Grassland options 0.022.
