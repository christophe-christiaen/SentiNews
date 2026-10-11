# WP3 within-cohort comparison

Specified in the decisions record **after the first results were seen, before this was run**; the last estimator version for this Sentinel-2 round. Read with [wp3_results.md](wp3_results.md) and [wp3_trend_adjusted.md](wp3_trend_adjusted.md).

Each contrast is formed inside each entry cohort, so the cohort's base-season gap cancels, then cohorts are combined by their parcel-seasons. "Before entry" (2–4 seasons before) works as a placebo and should be near zero. Matched sample, cell × season × crop strata, SE clustered by ERA5 cell; estimate (SE).

| Test | before entry | **after entry** | p (Holm) | after minus before | p (Holm) | cohorts (before / after) |
|---|---|---|---|---|---|---|
| H1 July NDVI, shock minus non-shock | +0.010 (0.012) | **+0.062 (0.042)** | 0.440 | +0.051 (0.044) | 0.731 | 5 / 5 |
| H2 peak NDVI, calm-after-shock minus calm-after-calm | +0.046 (0.038) | **+0.017 (0.031)** | 1.000 | -0.030 (0.050) | 1.000 | 5 / 4 |
| H3 H1 contrast, family B minus family A | -0.006 (0.020) | **-0.045 (0.084)** | 1.000 | -0.040 (0.086) | 1.000 | 5 / 5 |

## Checks: after entry; before entry in brackets

| Check | H1 | H2 | H3 |
|---|---|---|---|
| Within cohort x season | -0.010 ± 0.137 [+0.023] | -0.014 ± 0.087 [+0.023] | -0.203 ± 0.246 [+0.024] |
| Excluding 2017 | +0.062 ± 0.083 [+0.011] | +0.017 ± 0.060 [+0.046] | -0.045 ± 0.164 [-0.005] |
| Excluding Flood Zone 3 and deep peat | +0.068 ± 0.081 [+0.009] | +0.028 ± 0.062 [+0.050] | -0.053 ± 0.160 [-0.013] |
| 2026 version (cell x season strata, no crop) | +0.050 ± 0.108 [+0.023] | -0.015 ± 0.066 [+0.063] | -0.061 ± 0.167 [-0.035] |
| Unmatched full sample | +0.087 ± 0.077 [+0.007] | +0.027 ± 0.062 [+0.052] | -0.066 ± 0.165 [-0.009] |

## Reading

- **H1:** the within-cohort estimate (+0.062) is close to the earlier designs (+0.074 to +0.082), and the before-entry
  placebo is now near zero (+0.010). The standard error is 2.5 times larger (0.042), so the result is not significant.
  Most cohorts have only one to three seasons after entry, so within a cohort, shock and non-shock seasons are mostly
  different years, and different years are also different stages of the agreement. Within cohort × season, which
  compares only cells in the same year, has too little variation to say anything (±0.14).
- **H2:** null in every design.
- **H3:** the sign changes between designs (+0.065 pooled, −0.045 within cohort), with wide intervals: no evidence
  either way.
- **Overall:** across designs, agreement land drops about 0.06–0.08 SD less in shock seasons, on July NDVI. That is
  significant only when cohorts are pooled, which is the comparison the placebo questions. The Sentinel-2 seasons to
  date cannot separate it from chance once that is accounted for. Each added season (2027 onwards), and Sentinel-1
  for cloudy periods, adds within-cohort variation.
