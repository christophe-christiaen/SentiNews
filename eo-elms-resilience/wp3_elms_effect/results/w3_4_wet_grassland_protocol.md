# W3-4 addendum 4: wet grassland and fen, detection by EO product and drought resilience

**Status: registered 30 October 2026 by public commit, before any feature for the
parcels below is extracted.** Builds on [w3_4_metric_protocol.md](w3_4_metric_protocol.md) (I*, checks, reading rules),
[w3_4_model_comparison_protocol.md](w3_4_model_comparison_protocol.md) (paired bootstrap, Holm) and the WP3 decisions
record ([preregistration.md](preregistration.md): H1 contrast, matching, frozen-plan estimator). One of three drafts on
the option groups not yet covered (with [w3_1_linear_features_protocol.md](w3_1_linear_features_protocol.md) and
[w3_w_ponds_protocol.md](w3_w_ponds_protocol.md)). Changes after registration go in the record at the end.

## Why
W3-4 covers in-field land management on cereal land. Water options are absent. Wet grassland and fen are the water
options that are paid by area, so the existing design applies once the frame is moved to grassland. The questions are
(1) which EO products, with or without AI, can see these options beyond selection, and (2) whether the land under them
holds up better in drought, which is what the options are meant to do (water kept on the land).

## Options (Countryside Stewardship, national option layer, entry 2021–2024; counts checked 30 October 2026)
- **Wet grassland (primary family):** GS9 management of wet grassland for breeding waders; GS10 for wintering waders
  and wildfowl; GS11 creation of wet grassland for breeding waders.
- **Fen and reedbed (secondary family, descriptive):** WT6 management of reedbed; WT8 management of fen; WT9 creation
  of fen.
- 7,534 parcels enter 2021–2024 with any of these six codes. The split between the families is reported before any
  feature is extracted. SFI has no matching action in the snapshot used; a later SFI wet-grassland action is not added
  without a record entry.

## Sample
- **Frame:** grassland as in U1 (CROME PG01 in ≥ 80% of observed years, ≥ 8 of 10 CROME years 2016–2025 observed,
  never cereals), all of England, not the 100,000-parcel U1 sample.
- **Positives:** frame parcels entering 2021–2024 with an option of the family. All are used if there are fewer than 3,000;
  otherwise 3,000, stratified by ITL1 region (seed 30).
- **Comparison A:** never-treated frame parcels. **Comparison B:** frame parcels entering 2021–2024 whose only options are
  management-only (W3-4 control codes). Each is a random draw of the same size from the same ITL1 region.
- **Negative controls on grassland:** management-only against never-treated, and SW2 (4–6 m buffer strip on intensive
  grassland; at the edge, so not visible at the parcel point) against never-treated.

## Part A: which EO products detect them (I* as in W3-4, parcel point)
Products, each a feature family, with pre-entry = mean 2017–2019, I₀ = 2020, post = 2025:
- **No AI:**
  - S2: Sentinel-2 half-monthly NDVI, NDRE and NDMI, March–August, as W3-4.
  - S2W: S2 plus NDWI, and the share of clear winter dates (October–March) with NDWI > 0.
  - S1: Sentinel-1 VV, VH and VH − VV, monthly October–September.
- **AI, pixel-based:** AlphaEarth (64-d annual), TESSERA (128-d annual), Presto (128-d, full season), Galileo
  (addendum 3 settings).
- **AI, image-based (secondary, if addendum 3's extraction has been run):** OlmoEarth and TerraMind with addendum 3
  settings.

Model, leave-one-region-out evaluation, bootstrap, calibration (controls within ±0.02), selection invariance
(|I*(A) − I*(B)| < 0.03) and detection (95% interval above 0.02) as in W3-4. The product comparison uses the paired
bootstrap with Holm correction over the products that pass validity. **Key test: does any AI product beat the best
no-AI product (S2W or S1)?**

## Part B: drought resilience (H1 contrast, exploratory)
- **Design:** WP3's H1 contrast, comparing shock with non-shock seasons. Effect of the family against matched
  never-treated frame parcels (section 7 matching, AlphaEarth pre-entry components as in E3). Strata are ERA5
  cell × season; SE clustered by ERA5 cell; seasons 2017–2026; frozen-plan estimator.
- **Outcomes, one per product:**
  - July NDVI z-score against the 2001–2016 Landsat normal (primary; avoids the short-normal artefact of WP2).
  - July NDVI z-score against the Sentinel-2 2017–2020 normal (secondary, with the WP2 caveat).
  - Summer NDMI z-score (Sentinel-2; moisture rather than greenness).
  - Embedding distance from the field's pre-entry AlphaEarth embedding (descriptive only).
- **Before-entry placebo:** the same contrast in 2017–2020, before entry.
- **Reading:** reported with intervals. A cushion is "indicated" for an outcome if the contrast is positive with a 95%
  interval above zero and the before-entry placebo's interval includes zero. Otherwise it is "not shown".

## Harvest (economic resilience)
Not run: wet grassland has no cereal harvest, and Defra's regional yields cover cereals and oilseeds only. Grass
production has no open yield record against which an EO index could be checked, so economic resilience on grassland is
stated as a gap, not inferred from greenness. The W3-H harvest test covers the cereal-land options
([w3_h_harvest_protocol.md](w3_h_harvest_protocol.md)).

## Expectations stated now, not used in the rules
Winter wetness (S1, S2W) detects wet grassland better than summer greenness. AI adds little beyond S1. The cushion
shows in NDMI more than in NDVI.

## Compute and data
New extraction for about 7,500 positives and up to 3 × as many comparison parcels:
- Sentinel-1, Sentinel-2 and Landsat from public archives via the shared tiles of addendum 3; no Earth Engine.
- AlphaEarth and TESSERA from the same sources as W3-4.
- Presto and Galileo run on the project machine.

Per-parcel data stay out of the public repository.

## Output
`wp3_elms_effect/results/w3_4_wet_grassland.md`, `.json` (aggregates only).

## Decisions before registration (settled 30 October 2026: defaults adopted)
1. Whether fen and reedbed are pooled with wet grassland (larger sample, mixed signal) or kept descriptive (as drafted). **Decided:** Fen and reedbed kept descriptive, not pooled.
2. Whether Part B also runs on cereal-land water options that are paid by area (WT2, buffering in-field ponds and
   ditches on arable land; SW4 watercourse buffers), which sit in W3-4's buffer-strip family. **Decided:** Part B is not run on WT2 or SW4.

## Record
| Date | Change | Reason |
|---|---|---|
| 2026-10-30 | Draft written, before any feature for these parcels was extracted | Project lead's request to cover water and linear options |
| 2026-10-30 | Open decisions settled with the defaults (above); protocol registered by public commit | Project lead's decision |
