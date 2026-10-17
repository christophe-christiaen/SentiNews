# WP3 E3: matching with AlphaEarth pre-entry embeddings (exploratory)

Specified in the decisions record before any embedding was used. Pre-entry embedding = mean 2017–2020; first 10 principal components added to the matching covariates.

- Matched: 247,236 agreement fields, 53,130 never-treated fields; largest standardised difference after matching 0.05 (0 covariates above 0.1).
- Embedding components: largest difference 0.44 before matching; 0.33 in the original matched sample; 0.05 with embedding matching.
- Fields without any 2017–2020 embedding (given the mean): 0.

| Estimate | original matching | matching + embeddings |
|---|---|---|
| H1 | +0.082 (0.017) | +0.087 (0.019) |
| H2 | +0.035 (0.024) | +0.024 (0.024) |
| H3 | +0.065 (0.034) | +0.072 (0.036) |
| H1 within cohort | +0.062 (0.042) | +0.081 (0.051) |
| H1 within cohort, before entry | +0.010 (0.012) | +0.024 (0.012) |
| H2 within cohort | +0.017 (0.031) | +0.006 (0.031) |
| H2 within cohort, before entry | +0.046 (0.038) | +0.058 (0.041) |
| H3 within cohort | -0.045 (0.084) | -0.027 (0.089) |
| H3 within cohort, before entry | -0.006 (0.020) | -0.023 (0.020) |

H1 = shock minus non-shock effect on July NDVI; H2 = recovery; H3 = land-use change minus management options. Frozen-plan estimator unless marked "within cohort". Estimate (SE), SE clustered by ERA5 cell.

## Reading (17 October 2026)

- **The embeddings found an imbalance the original matching missed.** In the original matched sample, agreement land
  still differed from comparison land on its 2017–2020 embedding (largest difference 0.33, against the 0.1 target);
  matching on the embedding components brings it to 0.05.
- **The results barely move.** H1 is +0.087 (was +0.082) under the frozen-plan estimator and +0.081 within cohort
  (was +0.062, SE 0.051, still not significant). H2 and H3 stay null. The before-entry placebo within cohort is
  +0.024 (SE 0.012), borderline, in line with the small pre-existing difference MODIS showed (E1, +0.016).
- **So WP3's reading stands:** agreement land drops about 0.08 SD less in drought seasons, consistently across
  matching choices, but it is not established once cohorts are compared within themselves, and part of it may be
  which land joined. Embeddings tighten the comparison; they do not settle the question.
