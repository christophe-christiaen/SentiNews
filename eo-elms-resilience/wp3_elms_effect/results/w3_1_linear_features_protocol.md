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
3. **Stone walls and earth banks** (BN12, BN4): add as a further "not visible" family, or leave out. **Decided:** Stone walls and earth banks left out.

## Record
| Date | Change | Reason |
|---|---|---|
| 2026-10-30 | Draft written, before any edge-band feature was extracted | Project lead's request to cover water and linear options |
| 2026-10-30 | Open decisions settled with the defaults (above); protocol registered by public commit | Project lead's decision |
