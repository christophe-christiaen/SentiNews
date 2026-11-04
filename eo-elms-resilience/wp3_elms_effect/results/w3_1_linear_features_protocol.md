# W3-1 protocol: linear features (hedges, edge strips), detection by EO product and drought resilience

**Status: registered 30 October 2026 by public commit, before any edge-band
feature is extracted.** Builds on [w3_4_metric_protocol.md](w3_4_metric_protocol.md) (I*, checks, reading rules),
[w3_4_model_comparison_protocol.md](w3_4_model_comparison_protocol.md) (paired bootstrap, Holm) and the WP3 decisions
record ([preregistration.md](preregistration.md)). One of three drafts on the option groups not yet covered (with
[w3_4_wet_grassland_protocol.md](w3_4_wet_grassland_protocol.md) and [w3_w_ponds_protocol.md](w3_w_ponds_protocol.md)).
Changes after registration go in the record at the end.

## Why
The WP3 analyses so far sample each field at its parcel point, at the field centre, and exclude options paid per metre
or per item (decisions record, section 3). Hedges, walls and edge strips are therefore not covered, although hedgerow
actions are among the most common in SFI (about 860,000 records for HRW1–3 and CHRW1–3 in the snapshot). This protocol
samples the field edge from field polygons and asks:
1. Which EO products, with or without AI, detect linear options beyond selection?
2. Do fields with new hedges or edge strips hold up better in drought, in the edge band or in the field interior
   (shelter)?

## Geometry
- **Field polygons:** UKFields, matched to RPA parcels (the existing match, `shared/data/parcels/ukfields_sample.parquet`).
  Parcels whose polygon overlaps the RPA parcel by less than the match threshold already used there are excluded.
- **Edge band:** pixels whose centre is within 20 m inside the polygon boundary. **Interior:** pixels more than 30 m
  inside. Fields with fewer than 10 interior pixels are excluded.
- **Edge-band summary:** each product is averaged over the edge-band pixels. For image-based models, the patch tokens
  that overlap the band are averaged.

## Families (entry 2021–2024; counts checked 30 October 2026)
- **New and restored hedges (primary, expected visible slowly):** BN11 planting new hedges, BN7 hedgerow gapping;
  33,592 parcels.
- **Area strips at the edge (primary, expected visible):** buffer strips SW1, SW3, AHW6–AHW11, and margins and
  corners AHL3, AHL4, CAHL3, CAHL4, AB8. These are W3-4's buffer-strip control and its weak margins family, now sampled
  where they are.
- **Hedge management (expected not visible at 10 m; a test of the method):** BE3 management of hedgerows, BN5 laying,
  BN6 coppicing (145,774 parcels), and the SFI hedgerow actions HRW1–3 and CHRW1–3 (snapped to the nearest parcel
  point, as in the decisions record).
- **Negative control:** management-only parcels against never-treated, in the edge band.

Positives: 3,000 per family, stratified by ITL1 region (seed 30), on the W3-4 cereal-land frame. Comparisons A and B as
in W3-4.

## Part A: which EO products detect them (I* as in W3-4)
Products, each in three versions (edge band, interior, and edge minus interior):
- **No AI:** S2 (half-monthly NDVI, NDRE, NDMI, March–August); S1 (monthly VV, VH, VH − VV); S2 texture (standard
  deviation of NDVI across the edge-band pixels).
- **AI, pixel-based:** AlphaEarth, TESSERA (10 m per-pixel embeddings, averaged over the band).
- **AI, image-based:** Clay v1.5 patch embeddings over the polygon (as planned for W3-1); OlmoEarth and TerraMind
  (addendum 3 settings, tokens overlapping the band), if addendum 3's tiles exist.

Pre-entry = mean 2017–2019, I₀ = 2020, post = 2025. Calibration, invariance and detection rules as in W3-4. The product
comparison uses the paired bootstrap with Holm correction over valid products.

**Key tests:**
1. Edge band against parcel point for the area strips: does sampling the edge turn W3-4's invisible control into a
   detected family?
2. The best AI product against the best no-AI product, edge-minus-interior version.

## Part B: drought resilience (H1 contrast, exploratory)
- **Design:** WP3's H1 contrast (shock minus non-shock seasons) for new hedges and for area strips, against matched
  never-treated fields (section 7 matching with AlphaEarth pre-entry components). Strata are ERA5 cell × season; SE
  clustered by ERA5 cell; seasons 2017–2026; before-entry placebo 2017–2020.
- **Outcomes:**
  - July NDVI z-score (Sentinel-2, 2017–2020 normal, with the WP2 caveat), in the edge band and in the interior.
  - **Interior minus edge.** If hedges shelter the crop, the interior should drop less in drought relative to the
    edge band.
  - Landsat (30 m) is not used here: its pixels are wider than the band.
- **Reading:** as in the wet-grassland addendum. A cushion is "indicated" if the interval lies above zero and the
  placebo interval includes zero.

## Part C: harvest (economic resilience)
W3-H Step 3 ([w3_h_harvest_protocol.md](w3_h_harvest_protocol.md)) for new hedges and area strips. The outcome is the
field harvest index computed from **interior** pixels only, so that the strip itself, out of crop, is not counted as a
loss. It runs only for crops that pass W3-H's Defra gate. Reading as in W3-H. This is the policy question for hedges:
does shelter show up in the harvest in drought seasons?

## Expectations stated now, not used in the rules
- Area strips are detected in the edge band.
- New hedges are not detected by 2025, because whips planted in 2021–2024 are below 10 m resolution.
- Hedge management is not detected.
- AI products beat no-AI products only through the image models' context.

## Compute and data
- Edge-band and interior pixels for about 15,000 positives and their comparisons.
- Sentinel-1 and Sentinel-2 from the shared tiles of addendum 3; no Earth Engine.
- AlphaEarth and TESSERA per pixel from their public sources.
- Clay and the addendum-3 models on Colab.

Per-parcel data stay out of the public repository.

## Output
`wp3_elms_effect/results/w3_1_linear_features.md`, `.json` (aggregates only).

## Decisions before registration (settled 30 October 2026: defaults adopted)
1. **Band widths:** 20 m edge and 30 m interior, as drafted. A 10 m edge band is closer to a hedge but leaves very few
   pixels. **Decided:** 20 m edge band, 30 m interior.
2. **Hedges on boundaries:** a hedge lies on the boundary between two fields. Whether to also sample a band outside
   the polygon, which brings in the neighbouring field and is drafted without it. **Decided:** No band outside the polygon.
3. **Stone walls and earth banks** (BN12, BN4): add as a further "not visible" family, or leave out. **Decided:** Stone walls and earth banks left out. **Changed (30 October 2026, before any extraction):** added as a family expected not to be visible at 10 m, sampled in the edge band: stone walls (BN12, BN13, BN14), earth and stone-faced banks (BN1, BN2, BN3, BN4).

## Record
| Date | Change | Reason |
|---|---|---|
| 2026-10-30 | Draft written, before any edge-band feature was extracted | Project lead's request to cover water and linear options |
| 2026-10-30 | Open decisions settled with the defaults (above); protocol registered by public commit | Project lead's decision |
| 2026-10-30 | Changed before any extraction: options dropped by the defaults are kept (see Decisions) | Project lead: keep every option as far as possible |
| 2026-10-30 | **Correction and change before any extraction.** (1) Field polygons: the file named under Geometry (`ukfields_sample.parquet`) holds only Scotland and Northern Ireland points from U3, so no English polygon match exists. England's polygons come instead from the full UKFields release (Bancroft and Wilkins 2024, Zenodo 10.5281/zenodo.11110206, CC BY 4.0, Sentinel-2 2021 boundaries within 2021 cropland). A parcel is matched to the UKFields polygon containing its RPA parcel point if that polygon contains no other RPA parcel point and the point lies more than 20 m from its boundary; otherwise the parcel is excluded, and the exclusions are counted by family. (2) **Existing woody edge from LiDAR, as a covariate:** from the Environment Agency National LIDAR Programme (1 m, Open Government Licence), the share of the 20 m edge band whose first-return surface minus terrain height exceeds 1 m, and the band's mean height. Each field uses the latest survey flown before 1 January 2021 (before any entry in the frame); fields surveyed only later use that survey and are flagged, with a sensitivity check excluding them. Uses: added to the section 7 matching covariates for Parts B and C (balance reported); effects reported by tercile of existing woody edge (descriptive); and a check on the measure: hedge-management fields should have more existing woody edge than never-treated fields. Not used as an outcome. Tiles are downloaded to the project Google Drive only for sampled fields | Project lead's decision (addendum 5, section 5): LiDAR cannot show new hedges, but shows the hedges already there |
| 2026-10-30 | UKFields matching run ([`src/match_ukfields_england.py`](../src/match_ukfields_england.py); aggregates in [ukfields_england_match.json](ukfields_england_match.json)): cereal frame 244,436 of 381,400 parcels matched (64%); by family, new hedges 6,492 of 8,913 (73%), area strips 64,560 (75%), hedge management 82,685 (71%), walls and banks 571 (52%); never-treated cereal parcels only 44,203 of 90,447 (49%), mostly because one UKFields polygon holds several RPA points. Walls and banks fall below 3,000, so all 571 are used. **Because agreement and never-treated fields match at different rates, matched and excluded fields are compared on pre-entry July NDVI (2017–2020), parcel area and ITL1 region within each group, and reported before any outcome is read.** No outcome or EO feature was read | Geometry step before sampling |
| 2026-10-30 | **Matched against excluded fields, and samples drawn** ([`src/w3_1_sample.py`](../src/w3_1_sample.py); [w3_1_sample.json](w3_1_sample.json)), before any outcome was read. Pre-entry July NDVI, matched against excluded: within each family, standardised differences −0.05 to −0.10; management-only −0.08; **never-treated −0.40** (0.521 against 0.575): UKFields leaves out more of the greener never-treated parcels, probably grass margins inside a single outline. Matched pools are close to each other (families 0.50–0.51, management-only 0.519, never-treated 0.521). Matched fields are smaller (median 4–7 ha against 8–10 ha), because large outlines holding several parcels are excluded. Region shares differ by at most 0.08. Samples (seed 30, matched fields only): 3,000 positives each for new hedges, area strips, hedge management and the management-only control; all 368 walls-and-banks fields; comparisons A and B the same size by region, no shortfall; 30,242 parcels. Because comparison A is a selected subset of never-treated land, the imbalance is reported with every result (superseded the same day: see the next rows) | Geometry and sampling step |
| 2026-10-30 | **LiDAR product and storage, before any LiDAR value was read.** The Environment Agency publishes, for each National LIDAR Programme tile, a vegetation object model (VOM: height of vegetation above ground at 1 m). The woody-edge measure uses it instead of first-return surface minus terrain, because it already excludes buildings; the 1 m threshold and the band are unchanged, and the product's definition is confirmed from its documentation and from values on one tile before use. 4,125 tiles cover the sampled fields (840 surveyed only after 2020, flagged). Tiles (about 22 MB each, about 90 GB in all) are streamed on Colab and discarded; only each sampled field's VOM window (field outline plus 25 m) and its edge-band statistics are kept on the project Google Drive (expected well under the 10 GB approved) | Storage within the approved volume |
| 2026-10-30 | **Matching kept as registered.** Pre-entry July NDVI is not added to the section 7 matching covariates (matching on the outcome's own pre-entry level risks regression-to-the-mean artefacts in a before-and-after contrast). The matched-against-excluded imbalance above, and the balance of pre-entry July NDVI in each matched sample, are reported with every Part B and Part C result | Project lead's decision |
| 2026-11-01 | **LiDAR extraction done; the registered measure fails its own check.** VOM windows and statistics for 29,945 of 30,242 sampled fields (99%; 0.42 GB on Drive); 39 tiles failed after one retry (unreadable downloads, mostly SO20–SO45 on the Welsh border, listed in `w3_1_lidar_failed.txt` on Drive); 14.8% of fields use a post-2020 survey (flagged). Edge-band woody share (> 1 m) is near zero everywhere (mean 0.2–0.4% by group, median 0). **Registered check fails:** hedge-management fields 0.31% against never-treated (comparison A) 0.41% and management-only (B) 0.29%. Diagnostic (15 random tiles, all fields in them, no labels): share above 1 m is 0.6% 0–10 m inside the UKFields outline, 2.1% 0–5 m outside, 3.4% 0–10 m outside and 11.8% 10–25 m outside. UKFields outlines (Sentinel-2 2021 cropland) stop at the crop, so the hedge lies outside the polygon and the inside band does not measure it. **Not used as a covariate as registered.** A replacement (an outside band, which reverses decision 2) needs the project lead's decision and a record row before any value is computed; this row is written after the check result was seen | Registered validity check |
| 2026-11-01 | **Change: woody edge measured outside the field outline (reverses decision 2), fixed before any value of it is computed.** Written after the inside-band check failed (previous row), so it is a deviation, reported as such. **Outside band:** the 0–25 m ring outside the UKFields outline, minus any other UKFields polygon (the full release), so that it covers the uncropped strip around the field (hedge, verge, ditch, adjacent woodland) and not the neighbouring crop. Computed from the VOM windows already on Drive (outline + 25 m; no new download). Per field: **outside woody share** = share of ring pixels above 1 m; **outside mean height** (heights below 0 set to 0); ring pixel count. Fields whose ring has fewer than 200 valid pixels are reported and left out. **Check (fixed now):** hedge-management fields have a higher mean outside woody share than never-treated fields (comparison A): difference with a 95% bootstrap interval (2,000 resamples of fields, seed 30) above 0; also reported against management-only (B) and for each family; repeated without fields using a post-2020 survey. If the check fails, LiDAR is not used as a covariate. Uses unchanged if it passes (section 7 covariate for Parts B and C with balance reported; terciles descriptive; not an outcome). The inside-band values are reported beside it | Project lead's decision (1 November 2026) |
| 2026-11-01 | **Outside-band result: the check fails; LiDAR is not used as a covariate** ([`src/w3_1_outside_band.py`](../src/w3_1_outside_band.py); [w3_1_outside_band.md](w3_1_outside_band.md)). 33,761 sample rows with a usable ring. The outside band does see woody vegetation (mean share 0.065–0.086 by group against 0.002–0.004 inside), but hedge-management fields do not have more than never-treated fields: difference −0.0002 (95% interval −0.0038 to +0.0034); pre-2021 surveys only +0.0008 (−0.0032 to +0.0047). Against management-only land +0.0072 (+0.0035 to +0.0110). Reported, not used: new-hedge fields have less existing woody edge than their never-treated comparison (−0.015, −0.019 to −0.011), and walls-and-banks fields less still (−0.019), consistent with new hedges being planted where there were none. As fixed in advance, W3-1 runs without the LiDAR covariate and without the tercile split; the measure and these values are reported | Registered check |
| 2026-11-04 | Method suggestions from the project lead recorded and checked against their sources: [w3_detection_method_suggestions.md](w3_detection_method_suggestions.md). Not adopted; no rule here changes | Keep them with this protocol for when it resumes; resilience work comes first |
