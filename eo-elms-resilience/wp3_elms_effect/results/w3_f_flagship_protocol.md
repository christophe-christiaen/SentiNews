# W3-F protocol: the whole programme. Failure taxonomy and requirements ladders

**Status: registered 1 November 2026 by public commit, before any requirements experiment was run and before any
failure cause was assigned.** Builds on every WP3 detection protocol:
- W3-4 and its addenda 3, 4 and 5 ([w3_4_metric_protocol.md](w3_4_metric_protocol.md),
  [w3_4_esa_models_protocol.md](w3_4_esa_models_protocol.md), [w3_4_wet_grassland_protocol.md](w3_4_wet_grassland_protocol.md),
  [w3_x_addendum5_products_protocol.md](w3_x_addendum5_products_protocol.md));
- W3-1 ([w3_1_linear_features_protocol.md](w3_1_linear_features_protocol.md));
- W3-W ([w3_w_ponds_protocol.md](w3_w_ponds_protocol.md));
- W3-S ([w3_s_option_stacks_protocol.md](w3_s_option_stacks_protocol.md)).

It changes none of their rules. It adds a fixed way to explain each failure, and experiments that translate failures
into product requirements. Exploratory. Changes after registration go in the record at the end.

## Questions
1. **Coverage:** share of programme hectares and payments whose options are detected beyond selection by at least one
   open product, by group and by product class.
2. **Failure cause:** for each family not detected, why.
3. **Requirements:** the coarsest resolution, longest revisit, bands, structure measure and label count at which each
   family would pass.

## Coverage
- **Unit:** option families from the W3-S crosswalk (every CS, SFI and live ES code entering 2021–2024).
- **Detected:** the family passes the I* rule of its own protocol (95% interval above 0.02 against comparison B,
  calibration and invariance passed) for at least one product.
- **Weights:**
  - hectares from the option layers;
  - payments as hectares, metres or items × the published payment rate for each code, where Defra tables are
    available. Codes without a rate are reported unweighted and counted.
- **Classes:** "detected", "not detected", "not testable" (crosswalk).

## Failure taxonomy (applied to every family not detected)
Each undetected family gets one primary cause, the first in this order whose test is met. Secondary causes are listed.

| Order | Cause | Test (fixed now) |
|---|---|---|
| 1 | **Selection** | Its I* fails calibration or invariance for every product (a signal exists before entry) |
| 2 | **Not physical** | The crosswalk marks it "not visible" (management, timing or record-keeping) |
| 3 | **Spatial** | It passes at a finer step of the resolution ladder |
| 4 | **Temporal** | It passes in a seasonal window, or at denser revisit, but not in the annual or standard setting |
| 5 | **Structural** | It passes only with LiDAR height |
| 6 | **Label** | I* on the verified subset (if any) exceeds the declared-label I* by more than its 95% interval |
| 7 | **Undetermined** | None of the above |

## Requirements ladders (same samples, folds and I* rules as each family's protocol)
1. **Resolution:**
   - Rungs: 1, 3, 5, 10, 20, 30 m, built by block-averaging from the finest source available for the family (1 m LiDAR
     vegetation height for linear features; 10 m Sentinel-2 and its coarsenings for all).
   - Requirement: the coarsest rung that passes.
2. **Revisit:**
   - Sentinel-1 and Sentinel-2 series thinned to one image per 5, 10, 20, 30 and 60 days (seed 30 for which dates are
     kept); separately, single-season windows (October–February, March–May, June–August).
   - Requirement: the longest revisit that passes, and the season.
3. **Bands:**
   - The best no-AI feature set with, in turn, red-edge, shortwave infrared or radar removed.
   - A band group is required if removing it makes the family fail.
4. **Model class:**
   - Indices → pixel time-series models → image models → precomputed planetary embeddings.
   - ΔAI (addendum 5) at each step tells whether a new sensor or only a new model is needed.
5. **Labels:**
   - If a verified subset exists, I* with 100, 300 and all verified parcels (random subsets, seed 30).
   - Gives the field verification a product would need.

**Output:** a requirements table with one row per family: minimum resolution, revisit and season, required bands or
structure, labels needed, and missions that would meet it. Missions are named only after their specifications are
verified from the agency's own documents.

## Reading
- The requirements are descriptive bounds, not causal claims.
- A rung "passes" by the same rule as detection.
- Ladders are run only for families that fail at the standard setting, plus herbal leys as a positive reference.

## Expectations stated now, not used in the rules
- New hedges are spatial and structural (pass only at ≤ 3 m with height).
- Cover crops are temporal (winter window).
- Hedge management is not physical.
- Margins are spatial (edge band).
- Ponds are spatial (≤ 5 m).
- AI helps only at the model-class step for cover crops.

## Output
`wp3_elms_effect/results/w3_f_flagship.md`, `.json` (aggregates only).

## Record
| Date | Change | Reason |
|---|---|---|
| 2026-11-01 | Written and registered by public commit, before any ladder was run or any cause assigned | Project lead: one flagship paper on the whole programme, its potential and shortcomings, and the products still needed |
| 2026-11-01 | **Labels: declared options tied to field outlines and farms, before any ladder was run.** (1) For each UKFields-matched field, declared coverage = declared option area (CS OPTION_QUANTITY in hectares, or SFI action area) over the outline area. The label ladder gains three tiers: whole-field (≥ 0.8), part-field (0.5–0.8), small (< 0.5); I* is reported by tier, and the failure cause "label" is also met if I* in the whole-field tier exceeds the pooled I* by more than its 95% interval. (2) Farm reference: agreement ID (CS CONTRACTID, SFI app_id) links fields to holdings. It is used for the within-farm design (W3-S design 3) and the farm-level harvest reading (W3-H), and for bootstrap clustering by holding wherever folds do not already separate farms. (3) Independent audit, small: RPA crop-map ground observation points (land cover and events, by parcel reference) and Environment Agency vertical aerial photography (ponds, hedges), used only to check declared labels on the parcels they happen to cover | Project lead: options mapped to fields and farms are the label set; outside sources only audit them |
