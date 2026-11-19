# W3-B1 #9: Paper B intervals with clustered resampling

Run of [w3_b1_block_bootstrap_protocol.md](w3_b1_block_bootstrap_protocol.md) (registered before any statistic). Point estimates reproduce [w3_4_model_comparison.md](w3_4_model_comparison.md) exactly (largest gap 0e+00). Intervals: 1,000 resamples of 10 km British National Grid blocks within held-out regions (5 and 20 km as sensitivity), against the published resampling of single parcels. Detectable beyond selection: interval lower end above 0.02.

## Labels (10 km blocks, primary)

| Family | Models detecting (parcels → 10 km) | Verdict, parcels | Verdict, 10 km | Label |
|---|---|---|---|---|
| Herbal leys | AlphaEarth, Sentinel-2, TESSERA, Presto → AlphaEarth, Sentinel-2, TESSERA, Presto | no single best; leading group: AlphaEarth, TESSERA | no single best; leading group: AlphaEarth, TESSERA | **holds under clustering** |
| Cover crops | AlphaEarth, Sentinel-2, TESSERA, Presto → AlphaEarth, Sentinel-2, TESSERA, Presto | best suited: TESSERA | no single best; leading group: AlphaEarth, TESSERA | **detection holds, ranking changes** |
| No-till | AlphaEarth, Sentinel-2, TESSERA, Presto → AlphaEarth, Sentinel-2, TESSERA, Presto | no single best; leading group: AlphaEarth, Sentinel-2, TESSERA, Presto | no single best; leading group: AlphaEarth, Sentinel-2, TESSERA, Presto | **holds under clustering** |
| In-field flower and bird-food plots | AlphaEarth, Sentinel-2, TESSERA, Presto → AlphaEarth, Sentinel-2, TESSERA, Presto | best suited: TESSERA | best suited: TESSERA | **holds under clustering** |
| Margins and corners | none → none | not detectable by any model | not detectable by any model | **holds under clustering** |
| Grassland options | AlphaEarth, Sentinel-2, TESSERA, Presto → AlphaEarth, Sentinel-2, TESSERA, Presto | no single best; leading group: AlphaEarth, Sentinel-2, TESSERA, Presto | no single best; leading group: AlphaEarth, Sentinel-2, TESSERA, Presto | **holds under clustering** |

## Sensitivity: verdicts by block size

| Family | 5 km | 10 km | 20 km |
|---|---|---|---|
| Herbal leys | AlphaEarth, Sentinel-2, TESSERA, Presto; no single best; leading group: AlphaEarth, TESSERA | AlphaEarth, Sentinel-2, TESSERA, Presto; no single best; leading group: AlphaEarth, TESSERA | AlphaEarth, Sentinel-2, TESSERA, Presto; no single best; leading group: AlphaEarth, Sentinel-2, TESSERA |
| Cover crops | AlphaEarth, Sentinel-2, TESSERA, Presto; best suited: TESSERA | AlphaEarth, Sentinel-2, TESSERA, Presto; no single best; leading group: AlphaEarth, TESSERA | AlphaEarth, Sentinel-2, TESSERA, Presto; best suited: TESSERA |
| No-till | AlphaEarth, Sentinel-2, TESSERA, Presto; no single best; leading group: AlphaEarth, Sentinel-2, TESSERA, Presto | AlphaEarth, Sentinel-2, TESSERA, Presto; no single best; leading group: AlphaEarth, Sentinel-2, TESSERA, Presto | AlphaEarth, Sentinel-2, TESSERA, Presto; no single best; leading group: AlphaEarth, Sentinel-2, TESSERA, Presto |
| In-field flower and bird-food plots | AlphaEarth, Sentinel-2, TESSERA, Presto; best suited: TESSERA | AlphaEarth, Sentinel-2, TESSERA, Presto; best suited: TESSERA | AlphaEarth, Sentinel-2, TESSERA, Presto; best suited: TESSERA |
| Margins and corners | none; not detectable by any model | none; not detectable by any model | none; not detectable by any model |
| Grassland options | AlphaEarth, Sentinel-2, TESSERA, Presto; no single best; leading group: AlphaEarth, Sentinel-2, TESSERA, Presto | AlphaEarth, Sentinel-2, TESSERA, Presto; no single best; leading group: AlphaEarth, Sentinel-2, TESSERA, Presto | AlphaEarth, Sentinel-2, TESSERA, Presto; no single best; leading group: AlphaEarth, Sentinel-2, TESSERA, Presto |

## I* and 95% intervals

| Family | comp. | Model | I* | parcels | 5 km | 10 km | 20 km | width ratio 10 km / parcels |
|---|---|---|---|---|---|---|---|---|
| Herbal leys | B | AlphaEarth | +0.186 | +0.177 to +0.194 | +0.173 to +0.197 | +0.173 to +0.198 | +0.173 to +0.199 | 1.43 |
| Herbal leys | B | Sentinel-2 | +0.171 | +0.162 to +0.181 | +0.158 to +0.183 | +0.158 to +0.184 | +0.158 to +0.184 | 1.36 |
| Herbal leys | B | TESSERA | +0.190 | +0.181 to +0.199 | +0.177 to +0.202 | +0.178 to +0.201 | +0.178 to +0.203 | 1.31 |
| Herbal leys | B | Presto | +0.171 | +0.163 to +0.180 | +0.158 to +0.183 | +0.158 to +0.185 | +0.158 to +0.185 | 1.51 |
| Cover crops | B | AlphaEarth | +0.072 | +0.066 to +0.079 | +0.064 to +0.081 | +0.064 to +0.081 | +0.063 to +0.081 | 1.29 |
| Cover crops | B | Sentinel-2 | +0.054 | +0.046 to +0.061 | +0.044 to +0.063 | +0.043 to +0.064 | +0.043 to +0.064 | 1.29 |
| Cover crops | B | TESSERA | +0.087 | +0.080 to +0.094 | +0.078 to +0.096 | +0.078 to +0.097 | +0.078 to +0.097 | 1.29 |
| Cover crops | B | Presto | +0.057 | +0.050 to +0.064 | +0.048 to +0.066 | +0.047 to +0.065 | +0.047 to +0.065 | 1.33 |
| No-till | B | AlphaEarth | +0.098 | +0.090 to +0.107 | +0.087 to +0.111 | +0.085 to +0.112 | +0.083 to +0.113 | 1.57 |
| No-till | B | Sentinel-2 | +0.091 | +0.082 to +0.100 | +0.077 to +0.104 | +0.076 to +0.108 | +0.074 to +0.107 | 1.70 |
| No-till | B | TESSERA | +0.100 | +0.092 to +0.107 | +0.088 to +0.112 | +0.086 to +0.114 | +0.085 to +0.115 | 1.90 |
| No-till | B | Presto | +0.091 | +0.083 to +0.099 | +0.079 to +0.103 | +0.079 to +0.104 | +0.077 to +0.104 | 1.52 |
| In-field flower and bird-food plots | B | AlphaEarth | +0.085 | +0.079 to +0.093 | +0.076 to +0.095 | +0.076 to +0.095 | +0.075 to +0.096 | 1.39 |
| In-field flower and bird-food plots | B | Sentinel-2 | +0.076 | +0.068 to +0.083 | +0.066 to +0.085 | +0.066 to +0.085 | +0.066 to +0.086 | 1.28 |
| In-field flower and bird-food plots | B | TESSERA | +0.104 | +0.096 to +0.111 | +0.095 to +0.112 | +0.095 to +0.113 | +0.095 to +0.113 | 1.27 |
| In-field flower and bird-food plots | B | Presto | +0.072 | +0.065 to +0.079 | +0.062 to +0.080 | +0.062 to +0.080 | +0.063 to +0.080 | 1.33 |
| Margins and corners | B | AlphaEarth | +0.005 | -0.001 to +0.011 | -0.002 to +0.012 | -0.002 to +0.013 | -0.002 to +0.013 | 1.16 |
| Margins and corners | B | Sentinel-2 | +0.012 | +0.004 to +0.019 | +0.003 to +0.020 | +0.003 to +0.020 | +0.003 to +0.019 | 1.14 |
| Margins and corners | B | TESSERA | +0.005 | -0.002 to +0.011 | -0.002 to +0.011 | -0.002 to +0.012 | -0.003 to +0.012 | 1.13 |
| Margins and corners | B | Presto | +0.009 | +0.002 to +0.015 | +0.001 to +0.016 | +0.001 to +0.016 | +0.001 to +0.016 | 1.15 |
| Grassland options | B | AlphaEarth | +0.077 | +0.067 to +0.087 | +0.064 to +0.090 | +0.064 to +0.090 | +0.063 to +0.093 | 1.23 |
| Grassland options | B | Sentinel-2 | +0.069 | +0.057 to +0.081 | +0.056 to +0.083 | +0.055 to +0.083 | +0.055 to +0.084 | 1.14 |
| Grassland options | B | TESSERA | +0.082 | +0.072 to +0.093 | +0.070 to +0.095 | +0.069 to +0.095 | +0.069 to +0.097 | 1.23 |
| Grassland options | B | Presto | +0.068 | +0.057 to +0.079 | +0.055 to +0.081 | +0.054 to +0.082 | +0.054 to +0.083 | 1.35 |
| Buffer strips (control) | A | AlphaEarth | +0.019 | +0.015 to +0.023 | +0.014 to +0.023 | +0.014 to +0.023 | +0.015 to +0.024 | 1.15 |
| Buffer strips (control) | A | Sentinel-2 | -0.001 | -0.007 to +0.004 | -0.008 to +0.005 | -0.008 to +0.005 | -0.008 to +0.005 | 1.18 |
| Buffer strips (control) | A | TESSERA | +0.020 | +0.015 to +0.024 | +0.014 to +0.025 | +0.014 to +0.025 | +0.015 to +0.025 | 1.18 |
| Buffer strips (control) | A | Presto | +0.010 | +0.005 to +0.015 | +0.004 to +0.016 | +0.004 to +0.016 | +0.003 to +0.017 | 1.12 |
| Management only (control) | A | AlphaEarth | +0.015 | +0.011 to +0.019 | +0.010 to +0.020 | +0.010 to +0.020 | +0.010 to +0.021 | 1.10 |
| Management only (control) | A | Sentinel-2 | +0.005 | -0.001 to +0.011 | -0.001 to +0.011 | -0.001 to +0.012 | -0.002 to +0.011 | 1.08 |
| Management only (control) | A | TESSERA | +0.034 | +0.029 to +0.040 | +0.028 to +0.041 | +0.029 to +0.040 | +0.029 to +0.040 | 1.07 |
| Management only (control) | A | Presto | +0.017 | +0.011 to +0.022 | +0.011 to +0.023 | +0.010 to +0.023 | +0.010 to +0.023 | 1.16 |

## Blocks

| Family | n parcels | blocks 5 / 10 / 20 km | median parcels per 10 km block | resamples skipped |
|---|---|---|---|---|
| Herbal leys | 15,870 | 3,414 / 1,273 / 427 | 9 | 0 |
| Cover crops | 30,000 | 3,933 / 1,316 / 433 | 18 | 0 |
| No-till | 15,540 | 3,165 / 1,194 / 400 | 9 | 0 |
| In-field flower and bird-food plots | 30,000 | 3,896 / 1,301 / 424 | 17 | 0 |
| Margins and corners | 30,000 | 3,936 / 1,284 / 419 | 19 | 0 |
| Grassland options | 6,662 | 2,752 / 1,174 / 408 | 4 | 0 |
| Buffer strips (control) | 30,000 | 4,053 / 1,323 / 431 | 18 | 0 |
| Management only (control) | 30,000 | 4,294 / 1,368 / 444 | 19 | 0 |

Calibration (controls within ±0.02) is a point-estimate rule and is unchanged by this check.
