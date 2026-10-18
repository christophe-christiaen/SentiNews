# WP3 X2: the frozen-plan test with long-baseline normals (exploratory)

Specified in the decisions record before running. Frozen-plan estimator, matched sample, main shock definition; only the outcome changes. Estimates in SD of each field's normal; SE clustered by ERA5 cell.

| Version | H1 (shock − non-shock) | effect, shock seasons | effect, other seasons | placebo H1 (entry 2 seasons early) | pre-trend p (effect) | pre-trend p (contrast) |
|---|---|---|---|---|---|---|
| V0 · Sentinel-2, normal 2017–2020 (frozen) | +0.082 (0.017) | +0.071 (0.014) | -0.011 (0.014) | +0.079 (0.016) | 1.32e-06 | 0.0492 |
| V1 · MODIS, normal 2017–2020 | +0.075 (0.030) | +0.068 (0.021) | -0.006 (0.025) | +0.049 (0.040) | 0.748 | 0.194 |
| V2 · MODIS, normal 2001–2016 | +0.104 (0.009) | +0.097 (0.008) | -0.007 (0.007) | +0.061 (0.009) | 0.31 | 2.64e-12 |

## Event study (effect by event time, before entry)

| Version | e = -4 | e = -3 | e = -2 | e = -1 |
|---|---|---|---|---|
| V0 · Sentinel-2, normal 2017–2020 (frozen) | +0.002 | -0.016 | -0.009 | -0.056 |
| V1 · MODIS, normal 2017–2020 | -0.012 | +0.028 | -0.028 | -0.002 |
| V2 · MODIS, normal 2001–2016 | +0.006 | -0.004 | -0.009 | +0.002 |

## Reading (fixed in advance)

- Placebo from V1 to V2: +0.049 → +0.061; shrinks by half: no; V2 interval includes zero: no.
- Pre-trend test on the effect: V1 p = 0.748, V2 p = 0.31; passes only in V2: no.
- **The baseline mechanism is not supported:** the failed placebo is read as selection, not the short normal.

Long-baseline H1 (V2, exploratory, beside the frozen estimate): +0.104 (0.009).

Limits: MODIS pixels (250 m) mix neighbouring fields; a 2001–2016 normal can drift by 2017–2026.
