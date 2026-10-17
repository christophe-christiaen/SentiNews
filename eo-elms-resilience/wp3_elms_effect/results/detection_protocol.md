# Paper 3 protocol: can satellites see agri-environment options on the field?

**Written 17 October 2026, before any detection model was fitted.** Changes after this date go in the record at the end.

## Question
For SFI and Countryside Stewardship options on England's cereal land, can a field's satellite record show whether
an option is present, beyond what simply tells apart the land that joins a scheme?

## Option families (from the scheme records, area-based options; "_26" suffixes merged)
| Family | Codes | Expected |
|---|---|---|
| Herbal leys | SAM3, CSAM3 | visible: whole field becomes a multi-species ley |
| Cover crops | SAM2, CSAM2, SOH2, SOH3 | visible in winter and spring |
| No-till | SOH1 | possibly visible (stubble, residue) |
| In-field flower and bird-food plots | AHL1, AHL2, CAHL1, CAHL2 | visible where the plot covers the field centre |
| Margins and corners | AHL3, AHL4, CAHL3, CAHL4, AB8 | weak: mostly at field edges |
| Grassland options | LIG1, CLIG3, IGL2, CIGL2, GS1, GS2 | visible: arable to grass |
| Buffer strips (negative control) | SW1, SW3, SW4, AHW6–AHW11 | not visible at a field-centre point |
| Management only (negative control) | SAM1, IPM2–4, CIPM2–4, NUM2–3, CNUM2–3, PRF1–4 | not visible: practices and plans |

## Sample
Cereal-land parcels. **Positives:** agreement parcels entering 2021–2024 (so the option is in place for the 2025
season) carrying at least one option of the family. **Comparison A:** never-treated parcels (no scheme record).
**Comparison B (within schemes):** agreement parcels entering 2021–2024 whose only options are management-only
(the negative-control family), so both groups chose to join. Each positive is compared with a random draw of the same
number of comparison parcels from the same ITL1 region (seed fixed). Positives capped at 15,000 per family.

## Features (three versions, same model)
1. **Embedding 2025:** AlphaEarth annual embedding of the 2025 season (64 values).
2. **Sentinel-2 2025:** half-monthly NDVI, NDRE and NDMI medians, March–August 2025 (36 values; the interpretable
   baseline).
3. **Both together.**
**Placebo (selection):** the mean AlphaEarth embedding of 2017–2019, before any of these parcels had an option. What
it achieves measures which land joins, not the option. **Detection gain = AUC with the 2025 embedding minus AUC with the
2017–2019 embedding.**

## Model and evaluation
Gradient-boosted trees (scikit-learn HistGradientBoostingClassifier, default settings, 200 iterations), one per
family, comparison and feature version. **Leave one region out** (8 regions; London merged with the South East):
trained on seven, tested on the eighth, never random splits. Scores: area under the ROC curve (AUC; 0.5 = chance)
pooled over the held-out regions, and its range across regions.

## Reading, fixed in advance
- A family counts as **detected** if the 2025 embedding reaches AUC ≥ 0.70 against comparison B **and** the
  detection gain over the placebo is at least 0.10.
- The negative controls should not be detected; if they are, the method is picking up something other than the option.
- Labels are declared options, not verified ones (an option on the record may not be implemented, or may cover only
  part of the field); results are read as detection of declared options.

## Record
| Date | Change | Reason |
|---|---|---|
| 2026-10-17 | Protocol written | Before any detection model |
