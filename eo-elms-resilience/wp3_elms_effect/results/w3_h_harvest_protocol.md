# W3-H protocol: economic resilience. Do ELMs fields hold their harvest better in bad seasons?

**Status: registered 30 October 2026 by public commit, before any field-level
harvest index is computed.** Builds on the WP3 decisions record ([preregistration.md](preregistration.md): H1 contrast,
section 7 matching, frozen-plan estimator, shocks), the W3-4 detection results ([w3_4_metric.md](w3_4_metric.md)) and
the WP1 nowcast ([protocol.md](../../wp1_regional_signal/results/protocol.md), model "Sentinel-2 + weather", Defra
regional yields). Changes after registration go in the record at the end.

## Why
The programme asks whether Earth observation can help policy on the **physical** and **economic** resilience of UK
agriculture. WP3's H1 measures physical resilience: does agreement land's July greenness drop less in drought? The
economic counterpart is the harvest: **do ELMs fields hold their yield better in bad seasons than comparable non-ELMs
fields?** No open field-level yields exist in England. This protocol builds a field-level harvest index from EO and
weather, checks it against Defra's regional harvest before use, and only then compares ELMs and non-ELMs fields.

## Data
- **Harvest (ruler):** Defra *Cereal and oilseed production in the UK* (`data/raw/cops.ods`), regional yields (t/ha)
  for the 8 English Defra regions. Wheat, winter barley and spring barley; harvest years 2017–2025, plus 2026 once the
  final figures are published (10 December 2026).
- **Fields:** the Sentinel-2 cereal-land panel (381,400 parcels; half-monthly NDVI, NDRE, NDMI, March–August). Crop per
  field and season from CROME. ERA5-Land weather of the parcel's cell, as in WP1.
- **Scheme status and families:** as in W3-4 (agreement snapshot, entry 2021–2024, never-treated comparison).

## Step 1: the field harvest index (crop by crop)
- The WP1 model in use (ridge, "Sentinel-2 + weather", end-of-August cutoff) is fitted on region × season medians, as
  in WP1. It is then **applied to each field's own indices and its cell's weather**, giving a predicted yield anomaly
  (t/ha) per field and season. Fields are used only in seasons when CROME shows the crop in question.
- Leave-one-year-out: a field's index for season t comes from the model fitted without season t.

## Step 2: validation against Defra, fixed in advance (gate)
- **Aggregation:** for each region and season, the median of the field index over the crop's fields, compared with
  Defra's regional yield anomaly (leave-one-year-out, 2017–2025).
- **Gate:** the index is used for a crop only if the aggregated index reaches R² ≥ 0.40 against Defra's anomalies, and
  its mean absolute error in dry-spring seasons (2018, 2020, 2022, 2025) is no worse than 1.5 times that in other seasons.
  A crop that fails is reported, and Step 3 is not run for it.
- **Stated limit:** Defra's regional figures cannot show whether the index ranks fields correctly within a region. The
  field-level reading assumes it does. Farm or field yields (Farm Business Survey; partners' yield-monitor data) would
  test this and are noted as future validation.

## Step 3: ELMs against non-ELMs harvest (economic H1)
- **Contrast:** WP3's H1 design with the harvest index as the outcome. The effect of agreement land on the harvest
  anomaly in shock seasons minus non-shock seasons, against matched never-treated fields (section 7 matching with the
  E3 AlphaEarth components). Strata are ERA5 cell × season; SE clustered by ERA5 cell; seasons 2017–2025 (2026 added
  after 10 December); frozen-plan estimator; before-entry placebo 2017–2020.
- **Families:** the land-management families detected in W3-4 that leave the field in a cereal crop:
  - cover crops, which precede a spring crop;
  - no-till.

  Plus management-only agreement land. Herbal leys and grassland options take the field out of cereals by design and
  are reported only as the share of their fields leaving cereals.
- **Farm-level reading (secondary):** for agreement holders whose fields can be grouped into a holding (as in the
  existing farm grouping, `shared/data/farms`), the area-weighted harvest index of the holding's cereal fields. This
  is so that options taking land out of crops are not counted as harvest losses on the farm.
- **Regional context (descriptive, no causal reading):** Defra's regional yield anomaly in shock seasons against the
  region's share of cereal land in agreements (8 regions × 9 seasons).

## Reading, fixed in advance
- A family **holds its harvest better** if the shock-minus-non-shock contrast is positive with a 95% interval above
  zero, and the before-entry placebo's interval includes zero.
- It **holds worse** if the interval lies below zero. Otherwise "not shown".
- Results in t/ha are also stated in £/ha at Defra's average farm-gate price for the season, for the policy reading.
- **Expectation stated now, not used in the rules:** the physical cushion (H1 +0.08 SD of July NDVI) translates into a
  small, borderline harvest difference, about 0.1 t/ha for wheat in drought seasons.

## Links to the option-group drafts
The same Step 3 is run, as a "harvest part", in the drafts for linear features
([w3_1_linear_features_protocol.md](w3_1_linear_features_protocol.md); field interior) and ponds
([w3_w_ponds_protocol.md](w3_w_ponds_protocol.md); descriptive). It is not run for wet grassland, which has no cereal
harvest; see [w3_4_wet_grassland_protocol.md](w3_4_wet_grassland_protocol.md).

## Output
`wp3_elms_effect/results/w3_h_harvest.md`, `.json` (aggregates only).

## Decisions before registration (settled 30 October 2026: defaults adopted)
1. **Gate threshold:** R² ≥ 0.40, as drafted. WP1's region-level model reached 0.60 for wheat at end of August. **Decided:** R² ≥ 0.40.
2. **Farm-level reading:** whether the existing farm grouping is usable for this (to be checked), or whether this part
   waits for the Farm Business Survey. **Decided:** The farm grouping is checked before Step 3; if it cannot group fields into holdings, the farm-level reading is reported as not run.
3. **Farm Business Survey:** whether to apply for secure access through the UK Data Service. This is for the project
   lead to submit. **Decided:** No application for now; the field-level design stands without it.

## Record
| Date | Change | Reason |
|---|---|---|
| 2026-10-30 | Draft written, before any field harvest index was computed | Project lead's definition of economic resilience (the harvest) |
| 2026-10-30 | Open decisions settled with the defaults (above); protocol registered by public commit | Project lead's decision |
