# W3-B1 protocol: few shocks, trends, multiple tests and crop conditioning

**Status: registered 5 November 2026 by public commit, before any statistic below was computed. Exploratory checks on
registered results. They add labels beside those results and change none of their readings.** Prompted by an outside
review of the deck. Changes after registration go in the record at the end.

## Why
Standard errors so far cluster by ERA5 cell. A 50 km wild block bootstrap barely moved them, but that check is spatial. After
entry, the shocks are a handful of seasons (dry or hot mostly 2022 and 2025; wet mostly 2021 and 2024), so the effective
sample may be far smaller than the parcel count. Separately: the event study rises before entry; Holm covers only H1–H3;
and the frozen H1 conditions on the crop in the season, which agreements may themselves change.

## Estimator, stated
Callaway–Sant'Anna-type group-time comparisons, as frozen: for cohort g and season t, the change from a base season in treated
fields minus the mean change in never-treated and not-yet-treated fields in the same stratum. The estimand is a triple
difference: treated × after entry × hazard season.

## Results examined
All with their registered point estimates, samples and strata:
- **A:** H1, July NDVI, X2's matched sample, crop strata, 2017–2025 (frozen).
- **B:** the same on the E3 matched sample.
- **C:** W3-H Step 3, harvest index: all agreement land, management-only.
- **D:** wet-winter harvest index: all agreement land, management-only, buffer strips.
- **E:** wet-winter July NDVI: all agreement land, buffer strips.

## 1. Inference when shocks are few
Same estimates; only the uncertainty changes.
1. ERA5 cell (the baseline).
2. **Cells merged by agreement:** any two cells sharing a CS contract (`CONTRACT_ID`) or an SFI application (`app_id`, its action points
   snapped to the nearest parcel as in `build_parcel_schemes.py`) form one cluster. Holding IDs exist for only 11% of treated
   fields and no never-treated field, so true farm clustering isn't possible. Farms mostly sit inside a 9 km cell, so cell clustering
   already nests most of a farm's fields; this catches the rest. Never-treated fields carry no ID.
3. 50 km blocks.
4. Defra region (8 clusters), reported with a t(7) critical value.
5. Two-way, cell and season: V(cell) + V(season) − V(cell × season).
6. **Season:** clusters are the after-entry seasons contributing to the contrast, with a t(G − 1) critical value.
7. **Permutation of shock seasons:** the map of shocked cells for season y is reassigned to season π(y), with π a random permutation of
   2017–2025, 1,999 draws, fixed seed; effects are held fixed. Two-sided p is the share of draws with |estimate| at least as large as the
   real one. Draws leaving either side empty are dropped and counted.
8. **Leave one season out:** the contrast dropping each after-entry season in turn.

**Label, fixed in advance:** a contrast is **robust to few shocks** only if its season-clustered 95% interval (6) excludes zero and its
permutation p (7) is below 0.05. Otherwise **not robust to few shocks**. Season clustering with about five clusters is imprecise, which
is why it isn't used alone. Effects that grow with time since entry are confounded with later seasons in this design; (8) shows this.

## 2. How large a trend violation overturns the result
Rambachan and Roth (2023, *Review of Economic Studies* 90(5), 2555–2591), R package HonestDiD from CRAN, on the event study of the
hazard contrast, one base season (g − 1), pre-periods −4 to −2, post-periods 0 to 3.
- **Restriction:** relative magnitudes (post-entry violations at most M̄ times the largest pre-entry one), M̄ from 0 to 2 in steps of 0.25,
  the package's default method. Targets: the average of post-periods 0–3, and post-period 0.
- **Reported:** the breakdown M̄, the smallest value at which the 95% set includes zero. Applied to A, B, C (all land) and D (all land).
- **Limit:** uses the cell-clustered covariance, so it doesn't include the few-shocks uncertainty in section 1.

## 3. Multiple testing
Romano and Wolf (2005, *JASA* 100, 94–108), stepdown on studentized statistics, with a multiplier bootstrap (Rademacher weights by ERA5
cell, 9,999 draws, fixed seed) using the estimator's influence functions.
- **Rows:** Part F's 20 July NDVI and recovery contrasts, 25 establishment, 15 harvest, and W3-H Step 3's 4 families: 64 in all.
- **Reported:** adjusted p over all 64, and within each outcome. A row **survives** if its adjusted p is below 0.05. Two-sided, so this covers
  cushions and costs alike. Placebos aren't part of the family and their failures stand.

## 4. Crop conditioning
- **H1 without crop strata:** result A and B, strata ERA5 cell × season. **Crop conditioning matters** if H1 moves by more than 0.05 SD.
- **Does entry change rotations?** Outcome: 1 if CROME shows cereals in the season, frozen estimator without crop strata, after-entry effect, 2017–2025,
  placebo with entry two seasons early. Families: all agreement land, management-only, cover crops, no-till, herbal leys, grassland options, buffer strips.
  **Entry shifts rotations** if the interval excludes zero, the effect is at least 2 percentage points and the placebo interval includes zero.

## Known before this registration
All registered results and their placebos, the Landsat rerun, the 50 km bootstrap, and: "2026 version" of the frozen test (cell × season strata, no crop,
with 2026) gave +0.115 before trend adjustment; 73% of herbal-ley fields and 70% of grassland-option fields have a non-cereal season after entry, against 52% and 59% never
treated. So sections 1 and 4 aren't blind to which seasons dominate.

## Output
`wp3_elms_effect/src/w3_b1_inference.py`, `w3_b1_honest.R`, `w3_b1_multiple.py`; `wp3_elms_effect/results/w3_b1_inference.md`, `.json` (aggregates only).

## Record
| Date | Change | Reason |
|---|---|---|
| 2026-11-05 | Registered by public commit before any statistic was computed | Project lead: start Block 1 of the review plan |
