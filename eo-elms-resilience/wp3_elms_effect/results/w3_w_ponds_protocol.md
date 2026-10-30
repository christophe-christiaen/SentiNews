# W3-W protocol: ponds and small water features, detection by EO product and drought resilience

**Status: registered 30 October 2026 by public commit, before any
water feature for these parcels is extracted. Exploratory.** Builds on [w3_4_metric_protocol.md](w3_4_metric_protocol.md) (I*,
checks, reading rules), [w3_4_model_comparison_protocol.md](w3_4_model_comparison_protocol.md) and the WP3 decisions
record ([preregistration.md](preregistration.md)). One of three drafts on the option groups not yet covered (with
[w3_4_wet_grassland_protocol.md](w3_4_wet_grassland_protocol.md) and
[w3_1_linear_features_protocol.md](w3_1_linear_features_protocol.md)). Changes after registration go in the record at the end.

## Why
Ponds are paid per item or per small area and are excluded from every WP3 analysis so far. They are the hardest group
for open satellite data. Created ponds start at 100 m², about one Sentinel-2 pixel, and the median WN6A pond is
0.05 ha, about five pixels. The pond's position within the field is not known: the option layer gives one point per
option, and whether it marks the pond or only the parcel has not been checked (Open decision 1). The questions:
1. Which EO products, with or without AI, can see a new or restored pond somewhere in the field, beyond selection?
2. Do ponds hold water through drought seasons, and do fields with new ponds hold up better?

## Families (Countryside Stewardship, entry 2021–2024; counts checked 30 October 2026)
- **Pond creation (primary, expected visible if ≥ 0.05 ha):** WN5A (first 100 m²), WN6A (areas over 100 m²);
  1,203 parcels.
- **Pond restoration and management (secondary, expected weak):** WN5B, WN6B, WT4, WT5; together with creation,
  3,011 parcels.
- **SFI pond and ditch actions (descriptive):** WBD1 and WBD2. Their names and units are confirmed against the SFI
  actions list before use; if they are not pond and ditch actions, they are dropped and the record says so. They are snapped to the nearest parcel point, as in the decisions record.
- **Negative control:** management-only parcels against never-treated.

All positives are used (no cap); comparisons A and B as in W3-4, drawn from the same ITL1 region, three per positive.
The frame is all land (cereal and grassland), because ponds are placed on both.

## Water features (whole field)
Computed within the UKFields polygon matched to the parcel; parcels without a polygon are excluded and counted:
- **Open-water pixels (no AI):** per season, the number of Sentinel-2 10 m pixels with NDWI (B3, B8) > 0 on at least
  25% of clear dates; the same with MNDWI (B3, B11, 20 m); and the largest connected cluster of such pixels.
- **Radar (no AI):** per season, the number of Sentinel-1 pixels with VV below −15 dB (open water is dark) on at least
  25% of dates. The threshold is reported with a sensitivity check at −13 and −17 dB.
- **AI, pixel-based:** AlphaEarth and TESSERA per-pixel embeddings within the polygon, pooled two ways: the mean, and
  the per-dimension 95th percentile (a small feature is lost in a mean).
- **AI, image-based (secondary):** OlmoEarth (addendum 3 settings), tokens covering the polygon, same two poolings.

## Part A: detection (I* as in W3-4)
- Pre-entry = 2017–2019, I₀ = 2020, post = 2025. Model, leave-one-region-out, bootstrap, calibration, invariance and
  detection rules as in W3-4. Paired bootstrap with Holm over valid products.
- **Key test:** pond creation, best AI product against the best no-AI water count.
- **Size split (descriptive):** WN6A ponds ≥ 0.05 ha against smaller ones, from OPTION_QUANTITY.
- **Visual check (descriptive):** 200 positive and 200 comparison fields, drawn at random. Each is shown to a coder who
  does not see the label, as a 2025 Sentinel-2 true-colour chip, and marked "new water visible / not". This gives an
  upper bound on what 10 m imagery can show.

## Part B: water persistence and drought resilience (exploratory)
- **Does the pond hold water in drought?** For pond-creation fields with new open water by 2025, the share of seasons
  2022–2026 whose July still shows the water pixels. Dry-shock seasons are compared with others (shock as in WP3), and
  the result is set against natural ponds in comparison fields that had open water before 2020.
- **Do fields with new ponds hold up better?** WP3's H1 contrast (shock minus non-shock) on the July NDVI z-score of the
  field interior (Sentinel-2, 2017–2020 normal, WP2 caveat), against matched never-treated fields, with the
  before-entry placebo. The expected effect is small and the sample is about 1,200 fields, so the minimum detectable
  effect is reported before the estimate.

## Part C: harvest (economic resilience, descriptive)
W3-H Step 3 ([w3_h_harvest_protocol.md](w3_h_harvest_protocol.md)) for pond-creation fields in cereals, using the
field-interior harvest index. Only crops that pass W3-H's Defra gate are included. The minimum detectable effect is
reported first; with about 1,200 fields, only the estimate and its interval are reported, with no reading.

## Expectations stated now, not used in the rules
- Pond creation is detected weakly by the open-water counts, and only for ponds of at least 0.05 ha.
- Mean-pooled embeddings miss it; 95th-percentile pooling does better.
- Restoration is not detected.
- The H1 contrast is not distinguishable from zero.

## Compute and data
- About 3,000 positives, 9,000 comparisons, and all pixels in their polygons.
- Sentinel-1 and Sentinel-2 from the shared tiles of addendum 3; no Earth Engine.
- AlphaEarth and TESSERA per pixel from their public sources.

Per-parcel data stay out of the public repository.

## Output
`wp3_elms_effect/results/w3_w_ponds.md`, `.json` (aggregates only).

## Decisions before registration (settled 30 October 2026: defaults adopted)
1. **Option coordinates:** check on 50 pond options, against the Sentinel-2 chip, whether XCOORD/YCOORD fall on the
   pond. If they do, a 64 × 64 window centred on them replaces the whole-field search. **Decided:** The whole-field search is kept; the 50-option coordinate check is reported descriptively and does not change the design.
2. **Visual check:** whether the project lead or a second person codes it (a second coder allows agreement to be
   reported). **Decided:** Coded by the project lead alone (no agreement statistic).
3. **Open products:** whether the Copernicus Land Monitoring Service water and wetness layer is added as a no-AI
   product. Its resolution, years and licence must be verified before inclusion. **Decided:** The Copernicus layer is not added.

## Record
| Date | Change | Reason |
|---|---|---|
| 2026-10-30 | Draft written, before any water feature for these parcels was extracted | Project lead's request to cover water and linear options |
| 2026-10-30 | Open decisions settled with the defaults (above); protocol registered by public commit | Project lead's decision |
