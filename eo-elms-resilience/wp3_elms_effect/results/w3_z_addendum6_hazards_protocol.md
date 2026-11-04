# Addendum 6 (draft): flooding and crop disease as hazards, beside drought

**Status: registered 1 November 2026 by public commit, before any outcome was read for the wet-season or disease
contrasts below.** Builds on the WP3 decisions record ([preregistration.md](preregistration.md): section 5 shocks, H1 contrast,
section 7 matching, frozen-plan estimator), W3-H ([w3_h_harvest_protocol.md](w3_h_harvest_protocol.md)) and addendum 5
([w3_x_addendum5_products_protocol.md](w3_x_addendum5_products_protocol.md)). Exploratory; it does not change H1–H3.
Changes after registration go in the record at the end.

## Why
Physical resilience has so far meant drought: does greenness hold in dry summers? English farming loses as much to
wet winters. The 2019/20 and 2023/24 winters left fields unsown or waterlogged, and both were followed by poor
harvests. Several options are meant to help in exactly this case: cover crops and no-till (soil structure,
infiltration), buffer strips, wet grassland and arable reversion (water storage). The decisions record already defines a
wet shock (section 5: October–March rainfall at least 30% above normal) but uses it only as a secondary split. Crop
disease is the third hazard named by the project lead; it is the hardest to observe from space, so it gets a gate.

## Part F · flooding and waterlogging
**Hazard, three layers (from weather and water only, never from the crop):**
1. **Wet shock (primary, already defined):** section 5's October–March rainfall at least 30% above the 1991–2020 normal,
   per ERA5-Land cell and season.
2. **Observed inundation (secondary):** Copernicus Emergency Management Service Global Flood Monitoring (GFM), observed
   flood extent from Sentinel-1 at 20 m, 2015 onwards. A parcel is flooded in a season if any GFM observation flags its
   point (or, for UKFields-matched parcels, at least 10% of its outline) between October and March. Its licence, access
   and the archive's England coverage are verified before use; if any fails, this layer is dropped and the record says so.
3. **Validation of layer 2:** the Environment Agency's Recorded Flood Outlines (Open Government Licence; the licence
   field is checked before use). The share of GFM-flooded parcels inside a recorded outline of the same event is reported.

**Exposure, as a stratifier and in matching (already in section 7):** Flood Zone 3 and deep peat.

**Outcomes:**
- **Establishment:** share of clear February–March Sentinel-2 dates with NDVI above 0.3 (green cover after the wet
  winter).
- **Summer:** July NDVI z-score (as H1).
- **Recovery:** after an inundated season, the first half-month from March with NDVI back within 1 SD of the field's
  own pre-entry normal for that half-month.
- **Economic:** W3-H's harvest index, for crops that pass its Defra gate.

**Contrast:** WP3's H1 design with the wet shock in place of the dry shock. The effect of agreement land in wet-shock
seasons minus other seasons, against matched never-treated fields (section 7 matching with E3 AlphaEarth components).
Strata are ERA5 cell × season; SE clustered by ERA5 cell; seasons 2017–2026; before-entry placebo 2017–2020; also
within cohort. The 2023/24 winter falls after entry for the 2021–2023 cohorts, which is the strongest test available.

**Families:** management-only land; cover crops; no-till; buffer strips (SW1, SW3, SW4, WT2); wet grassland (on the
grassland frame, addendum 4). Option combinations through W3-S Part C, with the wet shock as the hazard.

**Reading, fixed in advance:** as H1. A cushion is "indicated" if the contrast is positive with a 95% interval above
zero and the placebo interval includes zero. Selection is a known risk: options for water are placed where land is wet.
So the Flood Zone 3 and peat stratification is reported for every result.

## Part D · crop disease (gated, most exploratory)
No validated disease-specific index exists for 10 m satellite data under UK conditions. A red-edge yellow-rust index
for Sentinel-2 has been published (Zheng et al., 2018, *Sensors*; about 84% accuracy in Chinese wheat). Disease symptoms
are confounded with nitrogen shortage, drought and early senescence. Hence a gate, as for the harvest index.

- **Hazard (weather, not EO):** disease-favourable seasons per ERA5 cell, defined before any disease data are read:
  - septoria: April–June days with at least 1 mm rain and mean temperature above 10 °C, top tercile of 1991–2020;
  - yellow rust: a mild winter (December–February mean above the 1991–2020 upper tercile) followed by a cool, humid
    spring.
- **EO signal:** May–June anomalies of red-edge indices (NDRE, red-edge chlorophyll index CIre, and the yellow-rust index
  REDSI), against each field's pre-entry normal, on wheat fields (CROME).
- **Survey data (downloaded 1 November 2026, free public files only):** Defra/ADAS winter-wheat pest and disease survey,
  regional mean time series (October 2025 release). Mean severity (% leaf area affected) on the flag leaf, leaf 2 and
  leaf 3 at about GS73, plus plant and crop incidence, by disease (including *Zymoseptoria tritici*, yellow rust, brown
  rust, powdery mildew) and region. The eight English regions are listed for 2017–2025 except **2020 (no survey)**.
  Terms: free to access; extracts for personal use; files not modified or redistributed; no commercial use without a
  licence; ADAS acknowledged. Results derived from it are cleared with ADAS (pestanddiseasesurvey@adas.co.uk) before
  publication; only aggregates are reported.
- **Gate (fixed in advance):** the disease part runs only if, at region × year level (8 English regions × 8 seasons,
  2017–2025 without 2020), the EO signal's anomaly correlates with the survey's flag-leaf plus leaf-2 mean severity of
  the same disease, with r ≥ 0.4. The weather hazard must also predict that severity, r ≥ 0.3. Septoria
  (*Z. tritici*) and yellow rust are gated separately. If the gate fails, the disease part is reported as
  "not measurable with open satellite data" (itself a result for policy) and not run further.
- **If the gate passes:** the H1 contrast with the disease-favourable season as the hazard and the red-edge anomaly as
  the outcome. Families: diverse rotations and herbal leys (break crops), cover crops, management-only.

## Expectations stated now, not used in the rules
- Wet shocks show a larger and clearer scheme effect than drought for cover crops and no-till.
- GFM flags few arable parcels outside Flood Zone 3.
- The disease gate fails for septoria and possibly passes for yellow rust in the 2023–2024 rust-heavy seasons.

## Compute and data
- ERA5-Land, already extracted.
- GFM flood extents for England 2015–2026 (size and access to be checked).
- EA Recorded Flood Outlines (vector, small).
- Sentinel-2 red-edge bands from the existing extraction.
- The pest and disease survey at region × year level.

Per-parcel data stay out of the public repository.

## Decisions before registration (settled 1 November 2026)
1. **Part F (flooding):** exploratory, as drafted; not co-primary with H1.
2. **Part D (disease):** included, behind the gate.
3. **Survey data:** only the free public files are used (they give region-level severity); no request to ADAS.

## Record
| Date | Change | Reason |
|---|---|---|
| 2026-11-01 | Draft written, before any wet-season or disease contrast was estimated | Project lead: add flooding and crop disease as hazards beside drought |
| 2026-11-01 | Decisions settled (above); free survey files downloaded and described (structure only; no association with any EO signal or weather hazard computed); registered by public commit | Project lead's decisions |
| 2026-11-03 | **Part F layer 2 (GFM) checks before use, all passed.** Licence: CEMS terms, free, full and open use including modification; outputs carry "Contains modified Copernicus Emergency Management Service information [year]". Access: EODC STAC collection `GFM` (2015 onwards), unauthenticated cloud-optimized GeoTIFFs (Equi7 EU020M, T3 tiles, 20 m). England coverage: all 12 tiles covering England have items in every October–March winter 2015/16–2025/26, but revisit is uneven (median items per tile: 247 in 2015/16; 547–661 in 2016/17–2020/21; 460 in 2021/22; 269–333 in 2022/23–2024/25 after the Sentinel-1B loss, including the 2023/24 winter; 614 in 2025/26). **Consequences, fixed now:** the flooded share is not compared across years; contrasts stay within ERA5 cell × season; the number of observed days per parcel-season is reported with every layer-2 result. **Extraction rules, fixed before any pixel is read at a parcel:** (1) winters October–March, labelled by the March year (2016–2026); (2) one observation per parcel per UTC acquisition day: the day's frames are merged per pixel (observed if any frame observes it; flooded if any frame flags it); (3) a pixel is observed if `ensemble_flood_extent` is not 255 and either `exclusion_mask` is 0 or the pixel is flooded (the manual keeps flooded pixels unmasked); any non-zero `exclusion_mask` value counts as excluded (the manual describes a binary mask; archive files hold values 0–20, almost all 1); flooded means `ensemble_flood_extent` = 1 (already 0 on reference water); (4) point version: the pixel containing the parcel point; (5) outline version (UKFields-matched parcels): the outline is observed on a day if at least half of its pixels are observed, and flooded if flooded pixels are at least 10% of its pixels; each outline is read in the tile holding its parcel point; (6) per parcel-season kept: observed days, flooded days, and the flood dates; advisory flags and likelihood layers are not used. Images are streamed and discarded; only the per-parcel results are kept (private). **Layer 3:** EA Recorded Flood Outlines licence verified as Open Government Licence from the official harvest metadata (the catalogue page's "no licence provided" is the portal's display); downloaded (GeoPackage, 31,744 outlines, 3,759 starting on or after 1 October 2015). "Same event" for validation: an outline whose start date falls in the same October–March winter; stricter version: a GFM flood day between the outline's start date and 7 days after its end date | Project lead approved the downloads, the GFM streaming and this row |
| 2026-11-03 | **Layer 3 validation, written before any GFM result was compared with an EA outline** ([`src/w3_z_gfm_validate.py`](../src/w3_z_gfm_validate.py)). As registered: the share of GFM-flooded parcel-seasons (point and outline versions) whose parcel point lies inside an EA outline starting in the same October–March winter, and the stricter version (a GFM flood day from the outline's start to 7 days after its end; missing end dates take the start date). Added as context, labelled so and not read as validation on their own: the same share among observed, never-flooded parcel-seasons (the base rate), and, among parcel-seasons inside a same-winter EA outline, GFM's observed share and its flooded share of those observed. Also reported per winter: observed share and median observed days (the observability found in the first tile: about a third of parcel points observed in a winter, the rest under GFM's static exclusion mask) | Project lead: run the EA validation when GFM finishes |
| 2026-11-04 | **Layers 2 and 3 run** ([w3_z_gfm_validation.md](w3_z_gfm_validation.md)). Extraction complete: 132 tile-winters, 2,686,103 parcels in each of 11 winters, no read retries. Point version, all winters: 35.7% of parcels observed (outline version 51.3%); 162,078 flooded parcel-seasons, of which 2.8% lie inside a same-winter EA outline (2.5% stricter), against 0.05% of observed, never-flooded parcel-seasons; of observed parcel-seasons inside an EA outline, 47.5% are flooded. **Deviation, logged after the fact:** descriptive checks not in the registered plan were run before this row was written (no outcome and no contrast involved; script not kept in the repository): 64.2% of parcels are observed in no winter and 35.7% in all 11; the observed share is 79.5% in Flood Zone 3, 73.9% in Flood Zone 2 and 30.4% outside them; 42.1% on agreement land and 31.4% on land with no agreement; 49.7% of flooded parcel-seasons come from parcels flagged in 5 or more winters, and 48.3% of flooded parcel-seasons have a single flood day. Winter labels in the output were also corrected (2016.0 to 2016); the numbers are unchanged | Project lead: run the EA validation; checks on observability and repeated flags |
| 2026-11-04 | **Registered before the checks below were run. (A) Observable land for the layer 2 contrast:** GFM cannot see most parcels, and the parcels it sees are not random, so any contrast using layer 2 uses observable parcels only, on both the agreement and the comparison side. A parcel is observable, by version, if it has at least one observed day in every winter 2016–2020. This fixes the set before any 2021–2024 entry and does not condition on later flooding (a flooded pixel counts as observed). Matching is redone within observable parcels. Results apply to observable land only and are reported beside a comparison of observable and all parcels by agreement status, Flood Zone and peat. The wet shock (layer 1) keeps all parcels and stays primary. **(B) Two further validation checks** ([`src/w3_z_gfm_validate_strata.py`](../src/w3_z_gfm_validate_strata.py)): the validation table repeated (1) within Flood Zone 3 only, and (2) without repeat-flag parcels, meaning parcels flagged in 5 or more of the 11 winters, by version. This threshold follows the descriptive check of 4 November, so it was chosen after seeing that distribution. Each reports, all winters and for the three winters with the most parcels in outlines (2016, 2020, 2024): flagged inside a same-winter outline, the stricter version, the base rate (observed, never flagged, inside an outline), their ratio with a 95% interval (bootstrap over 10 km British National Grid squares, 2,000 draws), and GFM's flagged share of observed parcels inside an outline. **Reading, fixed now:** geography does not explain the agreement if the ratio's interval lies above 1 in the Flood Zone 3 table, all winters. Check (2) removes flagged parcels, so its flagged share falls mechanically and is compared only through the ratio. Neither check measures GFM's false-alarm rate | Project lead's approval of the restriction and the checks |
| 2026-11-04 | **Part B checks run** ([w3_z_gfm_validation_strata.md](w3_z_gfm_validation_strata.md)). Reading as fixed: the ratio's interval lies above 1 within Flood Zone 3, all winters (point 17.2, 95% interval 13.3–21.8; outline 34.5, 26.0–44.8), so geography does not explain the agreement. It does explain part of it: the unrestricted point ratio is about 58. Without repeat-flag parcels the point ratio is 61.3 (48.9–74.7) and the outline ratio 72.7 (56.3–90.5), so those parcels do not drive the agreement. Neither check measures GFM's false-alarm rate; whether repeat flags are persistently wet land or radar artefacts stays open | Registered checks completed |
