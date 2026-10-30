# WP3 E3b: does the agreement-land drought cushion survive matching on OlmoEarth embeddings?

**Status: registered 30 October 2026 by public commit, before any OlmoEarth
embedding of a pre-entry season is computed.** Builds on the WP3 decisions record ([preregistration.md](preregistration.md),
E3 rows of 17 October 2026) and [wp3_e3_embeddings.md](wp3_e3_embeddings.md). Exploratory, no multiple-testing
correction. Changes after registration go in the record at the end.

## Question
E3 matched agreement fields to never-treated fields on the first 10 principal components of their 2017–2020 AlphaEarth
embedding. Balance improved (largest embedding difference 0.33 → 0.05) and H1 barely moved (+0.082 → +0.087). Is that
stability a property of the land or of AlphaEarth? E3b repeats the matching with a second, independently trained
embedding, OlmoEarth-v1-Base, specified as in W3-4 addendum 3 ([w3_4_esa_models_protocol.md](w3_4_esa_models_protocol.md)).
It is not a new test of the ELMs effect; H1–H3 and their estimators are unchanged.

## Sample
OlmoEarth cannot be run on the full E3 sample within the project's compute (300,366 fields × 3 seasons at about 2.2 s
per 64 × 64 window on a T4 is roughly 550 GPU hours). E3b therefore uses a random subsample, drawn once (seed 30) before
any embedding is computed:
- 20,000 agreement fields from the E3 matched sample, stratified by ITL1 region and cohort in proportion to their size;
- all never-treated fields in the same ERA5 cells as those agreement fields, capped at 40,000 (random within cell if more).

Both matchings below are run on this same subsample, so the comparison is like for like and does not depend on the
subsample being representative.

## Embedding
- **OlmoEarth-v1-Base**, exactly as OE in addendum 3: monthly Sentinel-1, Sentinel-2 and Landsat mosaics over the farm
  season (October–September) from the shared tiles, 64 × 64 pixel window centred on the RPA parcel point, patch size 8,
  field embedding = mean of the 2 × 2 centre patch tokens (160 m).
- **Pre-entry embedding** = mean over farm seasons 2017/18, 2018/19 and 2019/20, before every cohort's first full season.
  (AlphaEarth's E3 window was the four calendar years 2017–2020; OlmoEarth works by farm season, and 2016/17 is left out
  because Sentinel-2B only began imaging in mid-2017, so earlier monthly mosaics are much sparser. Planetary Computer
  L2A availability for 2017/18 is to be checked before registration: Open decision 3.) Fields without any pre-entry embedding are
  reported and dropped, not filled.
- First 10 principal components, fitted on all subsample fields.

## Matching and estimates
Three matched samples on the subsample, each with the section 7 propensity covariates and otherwise unchanged
(logistic per ITL1 region, nearest neighbour on the logit, caliper 0.2 SD, with replacement):
- **M0** original covariates only;
- **MA** + 10 AlphaEarth components (as E3);
- **MO** + 10 OlmoEarth components.

Balance reported for all covariates and for both sets of components in all three samples (cross-balance: AlphaEarth
components in MO, OlmoEarth components in MA). H1, H2, H3 re-estimated on each with the frozen-plan estimator and the
within-cohort design (with its before-entry placebo); SE clustered by ERA5 cell.

## Reading, fixed in advance (frozen-plan H1)
- **R1 · balance:** MO reaches a largest standardised difference ≤ 0.1 on all covariates and OlmoEarth components;
  otherwise E3b is reported as inconclusive and R2–R3 are not read.
- **R2 · the cushion does not depend on the embedding:** H1 in MO lies within ±0.03 of H1 in MA and has the same sign.
- **R3 · each embedding catches what the other misses:** reported, not tested: the largest cross-balance difference in
  MA and in MO, against 0.1.
- **Subsample check:** if H1 in MA differs from the full-sample E3 value (+0.087) by more than 0.03, this is stated with
  the result.
- **Expectation stated now, not used in the rules:** R2 holds.

## Compute and data
Imagery from the shared tiles of addendum 3 (no Earth Engine). About 60,000 fields × 3 seasons = 180,000 windows;
embedding about 110 T4 GPU hours at the pilot's speed, plus imagery. Only embeddings are kept on the project machine;
per-field data stay out of the public repository.

## Output
`wp3_elms_effect/results/wp3_e3b_olmoearth_matching.md`, `.json` (aggregates only).

## Decisions before registration (settled 30 October 2026: defaults adopted)
1. **Compute:** 110 GPU hours exceeds free Colab. Options: Colab Pro or a cloud GPU (paid), a smaller subsample
   (10,000 agreement fields; wider intervals), or 16 × 16 windows with patch 4 (about 7 times cheaper, but no longer the
   addendum-3 OE specification). **Decided:** Specification unchanged (64 × 64 windows, 20,000 agreement fields); the compute source (paid GPU) is arranged before extraction and does not change the design. **Changed (30 October 2026, before any extraction):** 16 × 16 windows with patch size 4; field embedding = mean of all 16 patch tokens (the same 160 m square); the 640 m surroundings are no longer seen. Accepted subject to the bridge check in the record.
2. **Further embeddings:** whether TerraMind or Galileo are added as further matched samples (MT, MG) once their
   addendum-3 extraction exists, at no extra imagery cost. **Decided:** No further matched samples; TerraMind or Galileo would need a record entry before any use.
3. **Pre-entry imagery:** confirm that Planetary Computer's Sentinel-2 L2A and Sentinel-1 cover England for 2017/18
   (one tile, metadata only) before the window is fixed; if not, the pre-entry window becomes 2018/19–2019/20. **Decided:** The rule above applies as written: the window is 2017/18–2019/20 if the metadata check finds coverage, otherwise 2018/19–2019/20; the check reads metadata only.

## Record
| Date | Change | Reason |
|---|---|---|
| 2026-10-30 | Draft written, before any pre-entry OlmoEarth embedding | Project lead's request |
| 2026-10-30 | Open decisions settled with the defaults (above); protocol registered by public commit | Project lead's decision |
| 2026-10-30 | Batch-size timing on Colab (T4; 40 pilot parcels, season 2025, 64 × 64 windows, patch 8; no labels read; `olmoearth_batch_timing.json` in the project Drive): batch 1 127 s, batch 4 143 s, batch 8 151 s, batch 16 out of GPU memory. Larger batches do not speed up embedding, so the 64 × 64 run stays at about 2–3 s per window (roughly 110–160 T4 hours for E3b) | Compute check before extraction |
| 2026-10-30 | **Switch to 16 × 16 windows, patch 4, field embedding = mean of all 16 tokens (160 m), before any E3b extraction.** Bridge check fixed now, before it is run: (a) sample: the 200 pilot parcels (`docs/colab/olmoearth_pilot_parcels.csv`), farm seasons 2017/18 and 2024/25, no labels or scheme status read; (b) version A = the registered specification (64 × 64, patch 8, mean of the 2 × 2 centre tokens), version B = the new one, from the same imagery; (c) 10 principal components fitted separately for each version on all parcel-seasons pooled; (d) canonical correlations between the two 10-component sets, 2-fold cross-fitted by parcel (seed 30; fitted on one half, evaluated on the other, both directions averaged); (e) **rule: 16 × 16 is accepted as equivalent if the median of the 10 cross-fitted canonical correlations is ≥ 0.80.** The in-sample median, the first canonical correlation and per-season values are reported, not used. If the rule fails, E3b still runs on 16 × 16 and is reported as a weaker check on the AlphaEarth matching, not as a replication of addendum 3's OE. The existing pilot files (`olmoearth_w64_*`, `olmoearth_w16_*`) use patch 4 and the 2 × 2 centre tokens (80 m) in both window sizes, so they are not versions A and B; the same statistic on them is reported as descriptive context only (does the wider window change an 80 m embedding?) | Project lead's decision: 64 × 64 needs 110–160 T4 hours; 16 × 16 needs about 16 |
