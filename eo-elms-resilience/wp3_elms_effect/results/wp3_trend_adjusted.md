# WP3 trend-adjusted results

Fallback named in the pre-registration (section 8, check 1) after the pre-trend test and placebo failed; method fixed in the decisions record **after the first results were seen**. Read alongside [wp3_results.md](wp3_results.md), not instead of it.

Each contrast uses one base season (the season before entry) and is computed before entry (seasons 2–4 before) and after entry. Adjusted = after minus before: the change in how agreement land responds to shocks, net of any difference that was already there. Matched sample, cell × season × crop strata, SE clustered by ERA5 cell.

## Confirmatory tests, trend-adjusted (Holm over three)

| Test | before entry | after entry | **adjusted** | SE | 95% CI | p | p (Holm) |
|---|---|---|---|---|---|---|---|
| H1 July NDVI, shock minus non-shock | +0.008 (0.012) | +0.082 (0.017) | **+0.074** | 0.021 | [+0.033, +0.116] | 0.000 | 0.001 |
| H2 peak NDVI, calm-after-shock minus calm-after-calm | +0.059 (0.030) | +0.035 (0.024) | **-0.024** | 0.039 | [-0.101, +0.053] | 0.537 | 0.537 |
| H3 H1 contrast, family B minus family A | -0.009 (0.020) | +0.065 (0.034) | **+0.074** | 0.040 | [-0.005, +0.153] | 0.067 | 0.133 |

50 km wild block bootstrap SE of the adjusted estimates: H1 0.020, H2 0.040, H3 0.036.

## Checks (adjusted estimate, SE in brackets)

| Check | H1 | H2 | H3 |
|---|---|---|---|
| Excluding 2017 | +0.075 (0.021) | -0.021 (0.043) | +0.076 (0.040) |
| Excluding Flood Zone 3 and deep peat | +0.074 (0.022) | -0.019 (0.041) | +0.067 (0.042) |
| 2026 version (cell x season strata, no crop) | +0.115 (0.021) | -0.086 (0.039) | +0.079 (0.038) |
| Unmatched full sample | +0.112 (0.020) | -0.025 (0.039) | +0.056 (0.039) |
| Shock: rain only | +0.065 (0.020) | -0.024 (0.034) | +0.088 (0.041) |
| Shock: soil moisture only | +0.066 (0.021) | -0.026 (0.035) | +0.079 (0.040) |

## Diagnostic: why does the placebo fail when the adjusted test passes? (post hoc, not confirmatory)

| Version | H1 contrast | SE |
|---|---|---|
| Placebo (entry two seasons early), as pre-registered | +0.079 | 0.016 |
| Placebo, leaving out the season just before entry | +0.058 | 0.021 |
| Placebo, contracts starting on or before 1 March only | +0.053 | 0.018 |
| Placebo, contracts starting after 1 March only | +0.111 | 0.028 |
| Trend-adjusted "before entry" contrast (base = season before entry) | +0.008 | 0.012 |

Contracts starting after 1 March (126,532 parcels) were under agreement for part of the season counted as "before
entry". That does not explain the failed placebo: parcels starting before 1 March fail it too. The two pre-entry
estimates differ mainly in the base season. Each cohort's estimates are shifted by its own base-season gap, and
shock and non-shock seasons come from different mixes of cohorts. So the size of the H1 contrast depends on which
season is the reference. Treat H1 as **consistent with buffering, but not yet robust**.
