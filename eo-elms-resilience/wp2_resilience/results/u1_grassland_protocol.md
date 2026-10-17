# U1 protocol: the short-baseline tests and the field score on England's grassland

**Written 18 October 2026, before any grassland satellite value was extracted.** Changes after this date go in the
record at the end.

## Question
Do the cereal findings hold on grassland? (1) Does a four-season per-field normal manufacture persistence on grass as
it does on cereals (WP2)? (2) Is there real season-to-season carry-over on grass? (3) Does the field resilience score
(lender score) have skill on grass, and is that skill robust to a long baseline (as X1 found for cereals)?

## Sample
- **Grassland land:** RPA parcels with CROME permanent grassland (PG01) in at least 80% of observed years, at least 8
  of the 10 CROME years (2016–2025) observed, and never in cereals. 
- **Sample:** 100,000 parcels drawn at random from that set (seed 20261018), so the extraction stays within the
  Earth Engine budget of the cereal run. Counts by region reported.

## Data (same pipelines as cereals)
- Sentinel-2, 2017–2026: `gee_s2_interactive.py --set grass` (Cloud Score+ and SCL mask, half-monthly medians of NDVI,
  NDRE, NDMI, 15 m buffer).
- MODIS MOD13Q1, 2001–2026: `gee_modis_parcels.py --set grass` (July mean and 15 April–15 July maximum NDVI at the
  parcel point's 250 m pixel).
- Weather shocks: the parcel's ERA5-Land cell, unchanged definitions.

## Outcomes
- **Primary:** stress index S = mean of the July and peak NDVI z-scores (as for cereals), clipped to ±6.
  Short normal: each field's 2017–2020 Sentinel-2 seasons; long normal: its 2001–2016 MODIS seasons.
- **Secondary (grass-specific):** z-score of the March–August mean of the half-monthly NDVI medians (needs at least 8
  of 12 half-months), less sensitive to the timing of cutting and grazing. Sentinel-2 only.

## Tests
- **WP2 T1–T3** as in `modis_long_baseline_check.py`: pooled, field fixed effects, Anderson–Hsiao, season-shuffling
  placebo, with cell × season effects and errors clustered by ERA5 cell. Run on (a) Sentinel-2 with the short normal,
  2017–2026; (b) MODIS with the long normal, 2002–2026 and 2017–2026.
- **Field score:** the X1 back-test (V0 Sentinel-2 short normal, V1 MODIS short normal, V2 MODIS long normal),
  scoring seasons 2020–2025, same features and targets as the cereal score.

## Reading, fixed in advance
- **R1, artefact replicates on grass** if, on Sentinel-2 with the short normal, pooled T1 minus Anderson–Hsiao T1 is at
  least 0.05 **and** the shuffled-season placebo is positive with p < 0.01.
- **R2, no material carry-over on grass** if the Anderson–Hsiao T1 and T2 estimates lie within ±0.05 on both sensors;
  otherwise the estimates are reported as evidence of carry-over, with their sign.
- **R3, score usable on grass** if the transparent score's AUC (hit hard next season) with the long normal (V2) is at
  least 0.60; **robust** if V1 − V2 < 0.03 (as for cereals).

## Limits stated in advance
Cutting and grazing change NDVI within a season independently of weather; the secondary outcome is there for that.
MODIS pixels (250 m) mix neighbouring fields. CROME grass classes include some temporary leys mislabelled as permanent.
A sample, not all grassland: national shares are not estimated.

## Output
`wp2_resilience/results/u1_grassland.md`, `.json` (aggregates only).

## Record
| Date | Change | Reason |
|---|---|---|
| 2026-10-18 | Protocol written | Before extraction |
