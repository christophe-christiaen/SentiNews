# WP3 E3b: matching on OlmoEarth pre-entry embeddings (exploratory)

Protocol: [wp3_e3b_olmoearth_matching_protocol.md](wp3_e3b_olmoearth_matching_protocol.md). OlmoEarth-v1-Base, 16 × 16 windows, patch 4 (the weaker check set by the bridge result), pre-entry = mean of farm seasons 2017/18–2019/20; 10 components each of OlmoEarth and AlphaEarth, fitted on the subsample.

Subsample fields in the panel 60,000; with a pre-entry OlmoEarth embedding 60,000; dropped 0 (0 agreement, 0 never-treated). Variance in 10 components: OlmoEarth 0.57, AlphaEarth 0.81.

## Balance (largest standardised difference after matching)

| Sample | agreement / never-treated fields | covariates | AlphaEarth comps | OlmoEarth comps | above 0.1 |
|---|---|---|---|---|---|
| M0 | 19,937 / 11,287 | 0.054 | 0.251 | 0.330 | 12 |
| MA | 19,934 / 10,538 | 0.025 | 0.020 | 0.157 | 1 |
| MO | 19,938 / 10,773 | 0.053 | 0.124 | 0.032 | 2 |

## Estimates (SE clustered by ERA5 cell)

| Estimate | M0 | MA | MO |
|---|---|---|---|
| H1 | +0.162 (0.053) | +0.152 (0.055) | +0.149 (0.053) |
| H2 | +0.023 (0.071) | +0.034 (0.073) | +0.042 (0.073) |
| H3 | +0.090 (0.115) | +0.141 (0.117) | +0.123 (0.117) |
| H1 within cohort | +0.128 (0.135) | +0.072 (0.131) | +0.040 (0.173) |
| H1 within cohort, before entry | +0.054 (0.037) | +0.050 (0.039) | +0.070 (0.037) |
| H2 within cohort | +0.012 (0.104) | -0.022 (0.106) | +0.021 (0.107) |
| H2 within cohort, before entry | -0.055 (0.110) | +0.003 (0.104) | +0.033 (0.116) |
| H3 within cohort | -0.018 (0.220) | -0.255 (0.343) | +0.256 (0.390) |
| H3 within cohort, before entry | -0.032 (0.068) | -0.016 (0.071) | -0.063 (0.068) |

## Harvest contrasts (t/ha, W3-H index)

| Contrast | M0 | MA | MO |
|---|---|---|---|
| Dry or heat, all land | -0.007 (0.031) | +0.014 (0.032) | -0.004 (0.031) |
| Wet winter, all land | +0.019 (0.031) | +0.005 (0.032) | +0.024 (0.031) |
| Dry or heat, management-only | +0.004 (0.036) | +0.022 (0.038) | +0.004 (0.037) |

## Readings fixed in advance

- **R1 · balance:** largest difference in MO 0.053 → passes.
- **R2 · cushion vs embedding:** H1 MO +0.149 vs MA +0.152 (difference -0.003) → passes.
- **R3 · cross-balance (reported):** OlmoEarth components in MA 0.157; AlphaEarth components in MO 0.124 (against 0.1).
- **R4 · Dry or heat, all land:** MO -0.004 vs MA +0.014 (difference -0.018) → fails (sign only; both within ±0.03 of zero).
- **R4 · Wet winter, all land:** MO +0.024 vs MA +0.005 (difference +0.019) → passes.
- **R4 · Dry or heat, management-only (reported, does not decide):** MO +0.004 vs MA +0.022 (difference -0.018) → passes.
- **R4 overall:** both deciding contrasts pass: no.
- **Subsample check:** H1 in MA +0.152 vs full-sample E3 +0.087: differs by more than 0.03: yes.

H1 = shock minus non-shock effect on July NDVI; H2 = recovery; H3 = land-use change minus management options. Limits as in the protocol: a pass is not evidence of a gain; the subsample is noisy; 16 × 16 is the weaker check.
