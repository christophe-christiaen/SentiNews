# X2-L: the drought test with a Landsat long baseline (exploratory)

Protocol: [wp3_x2l_landsat_protocol.md](wp3_x2l_landsat_protocol.md). Frozen-plan estimator, main dry-or-heat shock, seasons 2017–2025; only the outcome changes. Estimates in SD of each field's normal, (95% interval); SE clustered by ERA5 cell. Reported beside the frozen H1, never instead of it.

**Reproduction:** recomputed MODIS H1 +0.104 and placebo +0.061, against X2's +0.104 and +0.061; within 0.005: yes.

## X2's matched sample (decides)

| Version | H1 | Placebo | Placebo ÷ H1 | Effect, shock seasons | Effect, other seasons | Pre-trend p (effect) | Pre-trend p (contrast) | Parcel-seasons |
|---|---|---|---:|---:|---:|---:|---:|---:|
| V0 · Sentinel-2, normal 2017–2020 (frozen) | +0.082 (+0.049, +0.115) | +0.079 (+0.048, +0.110) | 96% | +0.071 | -0.011 | 1.32e-06 | 0.0492 | 331,037 |
| V2 · MODIS, normal 2001–2016 | +0.104 (+0.087, +0.121) | +0.061 (+0.044, +0.078) | 59% | +0.097 | -0.007 | 0.31 | 2.64e-12 | 364,311 |
| L1 · Landsat, normal 2017–2020 | +0.057 (+0.017, +0.096) | +0.093 (+0.053, +0.133) | 165% | +0.083 | +0.026 | 5.13e-05 | 0.005 | 353,625 |
| L2 · Landsat, normal 2001–2016 | +0.064 (+0.050, +0.079) | +0.077 (+0.062, +0.092) | 120% | +0.065 | +0.000 | 2.09e-09 | 1.66e-10 | 354,750 |

## E3 matched sample (reported)

| Version | H1 | Placebo | Placebo ÷ H1 | Effect, shock seasons | Effect, other seasons | Pre-trend p (effect) | Pre-trend p (contrast) | Parcel-seasons |
|---|---|---|---:|---:|---:|---:|---:|---:|
| V0 · Sentinel-2, normal 2017–2020 (frozen) | +0.087 (+0.050, +0.123) | +0.080 (+0.049, +0.111) | 92% | +0.090 | +0.004 | 0.0348 | 0.187 | 328,699 |
| V2 · MODIS, normal 2001–2016 | +0.100 (+0.083, +0.118) | +0.060 (+0.043, +0.077) | 60% | +0.095 | -0.005 | 0.305 | 5.9e-12 | 362,008 |
| L1 · Landsat, normal 2017–2020 | +0.051 (+0.010, +0.093) | +0.060 (+0.018, +0.101) | 116% | +0.083 | +0.031 | 0.0841 | 0.0463 | 351,226 |
| L2 · Landsat, normal 2001–2016 | +0.060 (+0.045, +0.074) | +0.062 (+0.047, +0.077) | 104% | +0.066 | +0.007 | 0.0224 | 2.02e-06 | 352,339 |

## Event study (effect by event time, before entry)

| Version | e = -4 | e = -3 | e = -2 | e = -1 |
|---|---|---|---|---|
| V0 · Sentinel-2, normal 2017–2020 (frozen) | +0.002 | -0.016 | -0.009 | -0.056 |
| V2 · MODIS, normal 2001–2016 | +0.006 | -0.004 | -0.009 | +0.002 |
| L1 · Landsat, normal 2017–2020 | -0.014 | +0.010 | -0.042 | -0.020 |
| L2 · Landsat, normal 2001–2016 | -0.002 | -0.001 | -0.019 | -0.018 |

## Reading (fixed in advance)

1. **Pixel size matters** (L2 and MODIS differ by more than 0.05 SD in H1 or placebo): no. H1 +0.064 against +0.104; placebo +0.077 against +0.061.
2. **Baseline mechanism supported:** no. Placebo from L1 to L2: +0.093 → +0.077; shrinks by half: no; L2 interval includes zero: no; pre-trend p 5.13e-05 → 2.09e-09, passes only in L2: no.
3. **Drought cushion holds at field scale:** no.

## Reported, does not decide

| Version | Before entry | After entry | Trend-adjusted | Within cohort | Within cohort, before entry | H1, wet seasons dropped | Its placebo |
|---|---|---|---|---|---|---|---|
| L2 | +0.024 (+0.012, +0.035) | +0.064 (+0.050, +0.079) | +0.041 (+0.021, +0.060) | -0.016 (-0.077, +0.044) | +0.016 (-0.008, +0.039) | +0.061 (+0.040, +0.081) | +0.081 (+0.062, +0.099) |
| V0 | +0.008 (-0.016, +0.032) | +0.082 (+0.049, +0.115) | +0.074 (+0.033, +0.116) | +0.062 (-0.022, +0.145) | +0.019 (-0.022, +0.061) | +0.079 (+0.032, +0.125) | +0.046 (+0.006, +0.087) |
| V2 | +0.051 (+0.038, +0.064) | +0.104 (+0.087, +0.121) | +0.053 (+0.032, +0.075) | +0.102 (+0.052, +0.153) | +0.048 (+0.021, +0.075) | +0.099 (+0.075, +0.123) | +0.075 (+0.052, +0.098) |

**Landsat 7 only,** normal 2001–2016, seasons 2017–2023: H1 +0.112 (+0.010, +0.215), placebo +0.024 (-0.078, +0.127), 1,963 parcel-seasons. Stops before most treated fields enter.

## Coverage: share of parcel-seasons with a value, 2017–2025

| Source | Group | Season | Parcel-seasons | With a value |
|---|---|---|---:|---:|
| L2 | treated | shock | 1,036,159 | 95.7% |
| L2 | treated | other | 1,189,730 | 89.1% |
| L2 | never treated | shock | 240,439 | 96.0% |
| L2 | never treated | other | 277,979 | 89.9% |
| V2 MODIS | treated | shock | 1,036,159 | 97.1% |
| V2 MODIS | treated | other | 1,189,730 | 93.3% |
| V2 MODIS | never treated | shock | 240,439 | 97.1% |
| V2 MODIS | never treated | other | 277,979 | 93.6% |
| V0 Sentinel-2 | treated | shock | 1,036,159 | 95.4% |
| V0 Sentinel-2 | treated | other | 1,189,730 | 81.3% |
| V0 Sentinel-2 | never treated | shock | 240,439 | 95.4% |
| V0 Sentinel-2 | never treated | other | 277,979 | 81.7% |

L2 share with a value by season: 2017: 81%, 2018: 97%, 2019: 92%, 2020: 92%, 2021: 88%, 2022: 98%, 2023: 93%, 2024: 93%, 2025: 96%, 2026: 98%.

Limits: the normal rests mostly on Landsat 5 and 7 and after-entry seasons on Landsat 8 and 9; the window runs to 15 August, wider than MODIS's July; a field-centre pixel can touch the edge of a small field; a 2001–2016 normal can drift. Greenness only.
