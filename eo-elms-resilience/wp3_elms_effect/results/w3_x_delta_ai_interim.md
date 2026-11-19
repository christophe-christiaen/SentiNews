# Addendum 5 · ΔAI: what AI embeddings add on top of the no-AI products (interim)

Run plan in the record of [w3_x_addendum5_products_protocol.md](w3_x_addendum5_products_protocol.md) (19 November 2026, fixed before any statistic). N = Sentinel-2 indices + Sentinel-1 (**interim: no NDTI**). ΔAI(E) = I*(N + E) − I*(N), comparison B (management-only scheme land). Paired bootstrap of parcels within held-out regions (registered), Holm over the three embeddings within each family; 10 km block intervals (#9) beside. E **adds to the indices** if the Holm-adjusted interval lies above zero, N + E passes calibration (both controls within ±0.02 against never-treated land) and invariance (|I*(A) − I*(B)| < 0.03).

**Interim.** NDTI is still being extracted. The registered reading is the run with NDTI; this one is labelled interim.

## Calibration (controls against never-treated land, I*)

| Product | Buffer strips | Management only | passes ±0.02 |
|---|---|---|---|
| N | +0.005 | +0.016 | yes |
| N + AlphaEarth | +0.018 | +0.022 | no |
| N + TESSERA | +0.025 | +0.035 | no |
| N + Presto | +0.008 | +0.017 | yes |

## ΔAI by option family (comparison B)

| Family | I*(N) | Embedding | ΔAI | Holm-adjusted interval (parcels) | p (Holm) | 10 km block interval | invariance | Reading |
|---|---|---|---|---|---|---|---|---|
| Herbal leys | +0.176 | AlphaEarth | +0.014 | +0.004 to +0.023 | 0.000 | +0.003 to +0.024 | 0.028 | interval above zero, but fails calibration |
| Herbal leys | +0.176 | TESSERA | +0.011 | +0.002 to +0.019 | 0.000 | +0.001 to +0.020 | 0.016 | interval above zero, but fails calibration |
| Herbal leys | +0.176 | Presto | -0.006 | -0.012 to +0.002 | 0.122 | -0.014 to +0.002 | 0.014 | adds nothing shown |
| Cover crops | +0.060 | AlphaEarth | +0.020 | +0.010 to +0.030 | 0.000 | +0.010 to +0.031 | 0.023 | interval above zero, but fails calibration |
| Cover crops | +0.060 | TESSERA | +0.029 | +0.020 to +0.039 | 0.000 | +0.019 to +0.040 | 0.016 | interval above zero, but fails calibration |
| Cover crops | +0.060 | Presto | +0.002 | -0.006 to +0.010 | 0.598 | -0.007 to +0.011 | 0.008 | adds nothing shown |
| No-till | +0.102 | AlphaEarth | +0.004 | -0.004 to +0.012 | 0.296 | -0.004 to +0.013 | 0.028 | adds nothing shown |
| No-till | +0.102 | TESSERA | +0.007 | -0.002 to +0.016 | 0.208 | -0.006 to +0.019 | 0.025 | adds nothing shown |
| No-till | +0.102 | Presto | +0.008 | -0.001 to +0.017 | 0.120 | -0.004 to +0.018 | 0.028 | adds nothing shown |
| In-field flower and bird-food plots | +0.082 | AlphaEarth | +0.008 | +0.000 to +0.016 | 0.052 | -0.001 to +0.018 | 0.007 | interval above zero, but fails calibration |
| In-field flower and bird-food plots | +0.082 | TESSERA | +0.019 | +0.010 to +0.028 | 0.000 | +0.009 to +0.030 | 0.013 | interval above zero, but fails calibration |
| In-field flower and bird-food plots | +0.082 | Presto | +0.001 | -0.006 to +0.008 | 0.754 | -0.007 to +0.009 | 0.014 | adds nothing shown |
| Margins and corners | +0.005 | AlphaEarth | +0.003 | -0.006 to +0.012 | 0.756 | -0.006 to +0.013 | 0.009 | adds nothing shown |
| Margins and corners | +0.005 | TESSERA | +0.002 | -0.005 to +0.010 | 0.756 | -0.006 to +0.010 | 0.023 | adds nothing shown |
| Margins and corners | +0.005 | Presto | +0.006 | -0.003 to +0.016 | 0.384 | -0.004 to +0.017 | 0.007 | adds nothing shown |
| Grassland options | +0.067 | AlphaEarth | +0.002 | -0.010 to +0.012 | 1.000 | -0.010 to +0.013 | 0.032 | adds nothing shown |
| Grassland options | +0.067 | TESSERA | +0.007 | -0.005 to +0.019 | 0.510 | -0.006 to +0.020 | 0.026 | adds nothing shown |
| Grassland options | +0.067 | Presto | -0.000 | -0.011 to +0.010 | 1.000 | -0.011 to +0.010 | 0.007 | adds nothing shown |

Invariance of N alone: Herbal leys 0.015; Cover crops 0.016; No-till 0.023; In-field flower and bird-food plots 0.015; Margins and corners 0.005; Grassland options 0.026.
