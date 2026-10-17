# WP3 E4: drought-season effects of the options visible from space (exploratory)

Specified in the decisions record before running. Embedding-matched sample (E3). H1 contrast = effect on July NDVI in shock seasons minus other seasons, against never-treated fields; SD of each field's 2017–2020 normal; SE clustered by ERA5 cell.

Matched agreement fields: other options 150,211, management only 75,833, no-till 11,159, herbal leys 10,033.

## Frozen-plan estimator

| Group | estimate | SE | 95% CI | p |
|---|---|---|---|---|
| herbal leys | +0.126 | 0.080 | [-0.031, +0.283] | 0.116 |
| no-till | +0.124 | 0.070 | [-0.013, +0.261] | 0.076 |
| management only | +0.050 | 0.041 | [-0.030, +0.130] | 0.218 |
| other options | +0.084 | 0.018 | [+0.049, +0.119] | 0.000 |
| herbal leys minus management only | +0.076 | 0.087 | [-0.095, +0.246] | 0.383 |
| no-till minus management only | +0.074 | 0.078 | [-0.079, +0.226] | 0.343 |

## Within cohort, after entry

| Group | estimate | SE | 95% CI | p |
|---|---|---|---|---|
| herbal leys | +0.002 | 0.174 | [-0.338, +0.342] | 0.992 |
| no-till | -0.217 | 0.234 | [-0.677, +0.242] | 0.353 |
| management only | +0.113 | 0.099 | [-0.082, +0.307] | 0.256 |
| herbal leys minus management only | -0.111 | 0.150 | [-0.406, +0.184] | 0.460 |
| no-till minus management only | -0.330 | 0.237 | [-0.794, +0.133] | 0.163 |

## Within cohort, before entry (placebo)

| Group | estimate | SE | 95% CI | p |
|---|---|---|---|---|
| herbal leys | +0.031 | 0.050 | [-0.066, +0.129] | 0.528 |
| no-till | +0.008 | 0.048 | [-0.086, +0.101] | 0.873 |
| management only | +0.040 | 0.020 | [+0.002, +0.079] | 0.041 |
| herbal leys minus management only | -0.009 | 0.051 | [-0.109, +0.092] | 0.866 |
| no-till minus management only | -0.032 | 0.051 | [-0.132, +0.067] | 0.522 |

## Reading (17 October 2026)

- **Suggestive direction, no evidence.** With the frozen-plan estimator, fields with herbal leys (+0.126) and no-till
  (+0.124) drop less in drought seasons than management-only scheme fields (+0.050), about twice the cushion. But the
  key differences (+0.076 and +0.074) have standard errors near 0.08: far from significant.
- **Within cohort the estimates carry no information** (standard errors 0.17–0.23; signs change). About 10,000 fields
  per option, clustered in weather cells, are too few for this design with nine seasons.
- **The before-entry placebo is clean for both options** (+0.031, +0.008), so the comparison is fair; management-only
  land shows a small pre-existing edge (+0.040, p = 0.04).
- **Verdict:** verifying actions from space sharpens the question but not yet the answer. More seasons (2027 onwards)
  and field-polygon outcomes are what would make this test informative.
