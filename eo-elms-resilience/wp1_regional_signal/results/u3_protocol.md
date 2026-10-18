# U3 protocol: the WP1 nowcast in Scotland and Northern Ireland

**Written 18 October 2026, before any Sentinel-2 value for Scottish or Northern Irish fields was extracted.** Changes
after this date go in the record at the end.

## Question
Does the WP1 regional yield nowcast generalise beyond England, to Scotland and Northern Ireland, where spring barley
dominates and the season is later? Does adding their region-years help?

## Yields (targets)
From `shared/data/yields/uk_nation_yields.csv` (Scottish Government regional estimates; Defra dataset for NI):
- **Scotland, regional:** ITL2 2021 regions North Eastern Scotland, Highlands and Islands, Eastern Scotland, Southern
  Scotland, 2018–2024; the 2025 regions (adding East Central Scotland) for 2025. West Central Scotland excluded.
  2017 is not used (different regional geography). 2020 and 2022 use a different yield method (publisher's note);
  results are also reported without those two years.
- **Northern Ireland:** national, 2017–2025.
- Crops: wheat, winter barley, spring barley.

## Fields
UKFields (Bancroft and Wilkins 2024, CC BY 4.0; Sentinel-2 2021 boundaries within Dynamic World 2021 cropland):
random samples of **120,000 fields in Scotland and 60,000 in Northern Ireland** (Earth Engine `random` property,
fixed threshold), as centroid points with polygon area. Regions by point-in-polygon with ONS ITL2 boundaries (2021
and 2025 versions).

## Crop labels
No open field crop labels exist in either nation. A gradient-boosted classifier (as `classify_2026` in WP1) is trained
on England: the 381,400 cereal-land parcels with CROME labels 2017–2025 (wheat = AC66 + AC32, winter barley = AC63,
spring barley = AC01, other) plus the U1 permanent-grassland sample as **grass**, so that grass fields in the north are
not forced into a crop. Features: half-monthly NDVI, NDRE, NDMI. History years use the full-season classifier (k ≤ 12),
as CROME labels are also end-of-season; the 2026 nowcast uses the classifier for its cutoff (k ≤ 9 or 12).

**Validation gate, fixed in advance.** Classified area of each crop (field area × inverse sampling fraction) is compared
with the official area: Scotland by region-year (2018–2024) and nationally (2018–2025); NI nationally (2017–2025).
A crop passes in a nation if the classified national area is within a factor of 1.5 of the official area (0.67–1.5)
in at least 6 of its years, and, for Scotland, the Spearman correlation of regional shares (mean over 2018–2024) is at
least 0.6. A crop that fails is not used in that nation; the failure is reported.

## Features and models
As the WP1 protocol (first run, without addenda): EO half-monthly medians to the cutoff, as anomalies from the
region's mean over training years; four ERA5-Land weather features; pilot-style peak slope; weather only; Sentinel-2
ridge; Sentinel-2 + weather ridge. Region-crop-years with fewer than 100 classified fields in the sample are dropped.

## Designs
- **D1 transfer:** models trained on England's 72 region-years per crop (2017–2025) and applied to Scotland and NI
  anomalies (each region's mean from its other years).
- **D2 local:** leave-one-year-out over Scotland and NI region-years only.
- **D3 pooled UK:** leave-one-year-out over England, Scotland and NI together; scored on Scotland and NI.
Scores: out-of-sample R² of the yield anomaly, RMSE, correlation, pooled over held-out region-years; jackknife+ 80%
interval coverage.

## Reading, fixed in advance
- **Primary:** D1 R² for wheat and spring barley at mid-July. The nowcast **generalises** to a crop if R² ≥ 0.30.
- **Local data help** if D3 R² exceeds D1 by at least 0.10.
- Spring barley is read against England's result (no skill before June there).

## 2026 nowcast (blind)
For each crop and region, mid-July and end-of-August nowcasts with 80% intervals, from the best-scoring design, are
committed publicly before any official 2026 Scottish or Northern Irish yield is looked at. The Scottish Government
usually publishes a first 2026 estimate in October; **it has not been and will not be consulted until the nowcast is
committed**: this blindness is declared, not verifiable. Targets: Scottish final estimates (expected December 2026)
and the Defra/DAERA 2026 figures.

## Output
`wp1_regional_signal/results/u3_scotland_ni.md`, `.json`, `u3_nowcast_2026.csv` (aggregates only).

## Record
| Date | Change | Reason |
|---|---|---|
| 2026-10-18 | Protocol written | Before extraction |
| 2026-10-18 | Before extraction: fields under 0.5 ha excluded (about 5% of UKFields fields, under 5% of their area; the 15 m sampling buffer would reach past them). Sampling by each nation's bounding box, then point-in-polygon with ITL1; field area computed from the geometry | The first sampler, filtering by the nation outline, timed out |
| 2026-10-18 | Clarifications before any Scottish or NI value was extracted or analysed: (1) the reading rule applies to the Sentinel-2 + weather ridge (WP1 model 5); Sentinel-2 alone is reported beside it. (2) D1 also leaves the scored year out of England's training data (England's same-season yield is not known at mid-July either). (3) East Central Scotland exists only in 2025, so it has no other years for its anomaly and is dropped; the four same-named regions are treated as continuous across the 2025 boundary change, with a sensitivity check without 2025. (4) 80% intervals for every design: the 80% quantile of that design's absolute leave-one-year-out residuals | Writing the analysis code |
