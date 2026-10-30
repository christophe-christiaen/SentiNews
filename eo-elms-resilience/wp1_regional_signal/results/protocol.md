# WP1 evaluation protocol: Sentinel-2 regional yield nowcast

**Written on 11 October 2026, before any Sentinel-2 feature was compared with a yield.** Changes after this date go in
the record at the end, with date and reason.

## Target
Defra regional yields (t/ha) from *Cereal and oilseed production in the UK* (`data/raw/cops.ods`), for the 8 English
Defra regions: North East, North West and Merseyside, Yorkshire & The Humber, East Midlands, West Midlands, Eastern,
South East and London, South West. Crops: **wheat (primary**, for comparison with the pilot), winter barley, spring
barley. Harvest years 2017–2025 (72 region-years per crop). The target is the yield anomaly: the region's yield
minus its mean over the training years of each fold.

## Fields
Sentinel-2 parcel panel (381,400 cereal-land parcels; half-monthly NDVI, NDRE, NDMI medians, March–August). A parcel
counts for a crop in a season if CROME gives that crop: wheat = AC66 + AC32, winter barley = AC63, spring barley = AC01.
Regions from ITL1 (London is joined to the South East, as in Defra).

## Features (per region × season × crop)
- **EO:** the median over the crop's parcels of each index in each half-month up to the cutoff (3 indices × k
  half-months), as anomalies from the region's training-year mean; a missing half-month is set to the training mean.
- **Weather:** region means over the same parcels of the ERA5-Land spring rainfall anomaly, June–July soil moisture z,
  hot days ≥ 28 °C and winter rainfall anomaly (whole season, so this baseline gets more information than EO at early
  cutoffs).
- **Cutoffs:** mid-May (k ≤ 5), mid-June (k ≤ 7), **mid-July (k ≤ 9, primary)**, end of August (k ≤ 12).

## Models (all scored by leave-one-year-out; never random splits)
1. **Pilot-style:** pooled slope of yield anomaly on peak NDVI anomaly (max of half-months 4–9).
2. **MODIS pilot, same years:** the same with the pilot's MODIS peak NDVI, 2017–2025 (fair comparison).
3. **Weather only:** ridge regression on the four weather features.
4. **Sentinel-2:** ridge regression on all EO features to the cutoff.
5. **Sentinel-2 + weather:** ridge regression on both.
Ridge penalty chosen by an inner leave-one-year-out loop on the training years only. Features standardised within
each fold.

## Scores
Out-of-sample R² of the yield anomaly (primary), RMSE (t/ha) and correlation, pooled over all held-out region-years;
the same for the England mean. **Success:** model 4 or 5 at mid-July beats both the pilot-style Sentinel-2 slope and
the MODIS pilot on the same years.

## Uncertainty and the 2026 nowcast
Intervals from leave-one-year-out residuals (jackknife+): 80% and 90%, with their coverage reported. For 2026 (no
CROME yet), crop masks come from a classifier trained on the 2017–2024 Sentinel-2 profiles with CROME labels, checked
on 2025. The 2026 wheat nowcast (mid-July and end of August cutoffs) is written down and committed before any official
2026 regional figure is looked at.

## Addendum A: grain-fill features (written 12 October 2026, before they were computed)

The first run over-predicted dry-spring years (2025 by 0.4 t/ha; the pilot missed 2022 the same way): canopies stay
green into July while grain fill is cut short. This addendum adds features for the grain-fill period, scored by the
same leave-one-year-out rules.

- **Weather, mid-July cutoff (June only, as monthly ERA5-Land is complete for June by mid-July):** June mean
  temperature anomaly; June water balance anomaly (rain minus potential evaporation); June root-zone soil moisture z
  (7–28 cm); April–June water balance anomaly (the depth of the spring drought). Anomalies against each cell's
  1991–2020 June (or April–June) normal, averaged over the crop's parcels in the region.
- **Weather, end-of-August cutoff:** the above plus the same three for July, and days ≥ 28 °C and ≥ 30 °C (June–August).
- **Sentinel-2 grain-fill features:** NDVI and NDMI fall from the season peak (half-months 4–9) to the last
  half-month before the cutoff (k = 9 at mid-July; mean of k = 10–11 at end of August); median senescence half-month
  (end of August only).
- **Models:** "Sentinel-2 + weather + grain fill" (ridge, all features) at both cutoffs, against the first-run
  models.
- **Scores:** out-of-sample R² as before (primary), and the mean error in dry-spring years: seasons in which at least
  half of the wheat region-years are in a dry shock (section 5 of the WP3 pre-registration), listed in the results.
- **Rule for the 2026 nowcast:** the 2026 figures are re-issued with the new model only where it improves the
  leave-one-year-out R² at that cutoff; the first nowcast (commit 8427362) stays on record either way.

## Addendum B: no extrapolation, damage-only weather, compound drought (written 14 October 2026, before running)

Prompted by the post hoc diagnosis of the 2026 miss (wp1_diagnose_2026.md): a positive weight on hot days, learned in
2017–2025, was extrapolated to an unprecedented 2026 heatwave. **Defra's 2026 figures are known, so 2026 cannot test
this addendum**; it is judged on leave-one-year-out 2017–2025 only, and any 2026 figure it gives is an illustration.

- **Features:** Sentinel-2 indices averaged to months instead of half-months (March to the cutoff; 3 indices × 5 months
  at mid-July, × 6 at end of August), plus the four weather features of the first run.
- **No extrapolation:** each weather feature is clipped to the range seen in the training years of the fold.
- **Damage-only weather:** standardised coefficients constrained in sign: hot days ≤ 0; spring rainfall anomaly ≥ 0;
  June–July soil moisture ≥ 0; winter rainfall anomaly ≤ 0 (wet winters can only hurt). Sentinel-2 terms unconstrained.
- **Compound drought:** one added term, max(0, −spring rainfall anomaly / 20) × max(0, −soil moisture z), clipped like the
  others, coefficient ≤ 0.
- **Estimation:** bounded least squares with a ridge penalty (penalty from 1 to 1,000, chosen by inner
  leave-one-year-out), features standardised within each fold.
- **Scores:** as before (out-of-sample R², England R²), plus mean error and mean absolute error in the dry-spring years
  2018, 2020, 2022 and 2025, and the 2025 error on its own.
- **Adoption rule (for future nowcasts, from 2027):** addendum B replaces the first-run model for a crop and cutoff if
  its leave-one-year-out R² is no more than 0.02 below the first run **and** its mean absolute error in the dry-spring
  years is lower. Otherwise the first-run model stays.

## Addendum C: supporting datasets (written 17 October 2026, before running)

Uses the datasets the WP1 plan lists as supporting. Same targets, regions and leave-one-year-out scoring.

- **C1, MODIS long record:** region medians of MODIS July and peak NDVI (250 m, at cereal-land parcel points, since
  CROME starts in 2016), as anomalies, plus the four weather features; trained and scored by leave-one-year-out over
  2001–2025 (up to 25 seasons instead of 9). Scored on all years and on 2017–2025 alone, for comparison with Sentinel-2.
- **C2, Sentinel-1 in spring:** the first-run Sentinel-2 + weather model plus monthly Sentinel-1 cross-ratio (VH − VV,
  dB, mean of both orbit directions) medians over the crop's fields, March to the cutoff, as anomalies (2017–2025).
- **C3, schemes, flood and peat:** the first-run model plus the share of the crop's fields under an agreement that
  season, and the share in Flood Zone 3 or on deep peat multiplied by the wet-winter indicator (a static share alone
  is absorbed by each region's mean).
- **Rule:** an addition is adopted for a crop and cutoff if its leave-one-year-out R² on 2017–2025 is at least 0.02
  above the first run and its dry-spring-year mean absolute error is not higher. C1 is reported as a separate model.
  2026 is not used as a test (Defra's figures are known).

## Addendum D: AlphaEarth embeddings (written 17 October 2026, before running)

Each annual AlphaEarth embedding summarises the whole calendar year, including the months after harvest, so the
embedding of the season being forecast **cannot be used in a mid-July nowcast** (it would see the future).

- **D1, nowcast-valid:** the previous year's embedding (known by January), as farming-system context: for each
  region, season and crop, the median over that season's crop fields of their previous-year embedding (64 bands),
  reduced to 5 principal components fitted on the training years of each fold, added to the first-run Sentinel-2 +
  weather model. Seasons 2018–2025 (2017 has no previous-year embedding); the first run is re-scored on the same
  seasons for a like-for-like comparison.
- **D2, after-season, not a nowcast:** the same with the season's own embedding, alone and added to Sentinel-2 +
  weather, to show how much yield information the embeddings carry at best. Never used for a forecast.
- **Rule:** D1 is adopted for a crop and cutoff if its leave-one-year-out R² (2018–2025) is at least 0.02 above the
  first run on the same seasons and its dry-spring-year mean absolute error is not higher. 2026 is not used.

## Addendum E: heat as degree-days, sign-constrained weather, an out-of-range flag and shift-aware intervals (written 29 October 2026, before any new feature was computed)

Prompted by the 2026 miss (heat 4–5 SD beyond the training seasons, met by a positive hot-day weight) and planned as
tasks W1-2 and W1-4 of the publication plan. **Defra's provisional 2026 figures are known**, so 2026 cannot test the
skill of this addendum; it is judged on 2017–2025, and the 2027 harvest is its confirmatory test. One part can be
tested on 2026 fairly: the out-of-range flag uses only inputs known at the nowcast date, never yields.

- **E1, heat as degree-days.** Replace the count of days ≥ 28 °C with degree-days above 30 °C: the sum over days of
  max(0, daily maximum 2 m temperature − 30 °C) from ERA5-Land daily data, 1 June to the cutoff (15 July at mid-July;
  31 August at end of August), averaged over the crop's parcels in the region (the threshold follows the US evidence that
  damage rises steeply above about 29–30 °C; not tuned on our data). New data: ERA5-Land DAILY_AGGR maximum temperature
  for the cereal weather cells, 2017–2026; nothing else changes.
- **E2, sign-constrained weather inside the fit.** As addendum B (monthly Sentinel-2 indices; bounded least squares with a
  ridge penalty chosen by inner leave-one-year-out; features standardised within each fold; weather clipped to the
  training range), with the degree-day term in place of hot days and constrained ≤ 0, spring rainfall anomaly ≥ 0,
  June–July soil moisture ≥ 0, winter rainfall anomaly ≤ 0 and the compound drought term ≤ 0. Sentinel-2 terms
  unconstrained.
- **E3, out-of-range flag (area of applicability).** For each region-season, a dissimilarity index DI = distance to the
  nearest training region-season in the standardised feature space, each feature weighted by the absolute value of its
  fitted coefficient, divided by the mean distance between training region-seasons. The threshold is the upper
  whisker (Q3 + 1.5 × IQR) of the DIs that the training region-seasons get under leave-one-year-out. A nowcast above the
  threshold is flagged "outside the range of the training seasons".
- **E4, shift-aware intervals.** 80% intervals by weighted conformal prediction: leave-one-year-out residuals weighted by
  exp(−d²/2h²), with d the weighted distance between the new region-season and each calibration region-season and h the
  median of those distances in training; the interval is the weighted 80% quantile of absolute residuals around the
  point nowcast.

**Scores.** Leave-one-year-out 2017–2025: R², England R², mean absolute error in the dry-spring years (2018, 2020,
2022, 2025), and interval coverage for unweighted and weighted intervals. **Leave-one-extreme-season-out:** 2018, 2022
and 2025 each held out with all other seasons as training, reporting the error and whether E3 flags the held-out
season. **2026 (fair for E3 only):** the share of regions whose 2026 inputs the flag marks as out of range, computed from
inputs alone; and, as an illustration only, the E2/E4 nowcast against Defra's provisional and final (10 December 2026)
figures.

**Adoption rules, fixed now.**
- E1 + E2 replace the current model for a crop and cutoff (from 2027) if leave-one-year-out R² is no more than 0.02
  below the current one **and** mean absolute error over the held-out extreme seasons is lower.
- E3 is adopted if, under leave-one-extreme-season-out, it flags at least two of the three extreme seasons and at most
  one in ten of the other held-out region-seasons. Its 2026 result is reported whatever it is: the protocol counts the
  flag as having worked for 2026 if it marks at least half of the regions.
- E4 is adopted if its leave-one-year-out coverage of 80% intervals is between 75% and 90% and its coverage in the
  held-out extreme seasons is higher than the unweighted intervals'.
- Everything adopted is frozen, with code and date, before the 2027 season's first image (1 March 2027) is used.

## Record

| Date | Change | Reason |
|---|---|---|
| 2026-10-11 | Protocol written | Before any yield comparison |
| 2026-10-11 | Diagnostic after the nowcast was written: classifier vs CROME mask in 2025, and the 2025 held-out error (results, last section). Nowcast left unchanged | The 2026 nowcast is above average in a record-dry spring; checked whether the mask or the model drives it |
| 2026-10-12 | Addendum A: grain-fill features | Dry-spring years over-predicted in the first run; written before the new features were computed |
| 2026-10-12 | Addendum A run: no gain for wheat or winter barley, spring barley improved and re-issued for 2026 under the rule; the earlier "dry springs over-predicted" reading corrected in wp1_results.md (only 2025 was; 2018, 2020, 2022 were under-predicted) | Results of addendum A |
| 2026-10-12 | 2026 nowcast scored against Defra's provisional figures (wp1_score_2026.md). Defra had published them on 8 October 2026, before the nowcast was written on 11 October; they were not looked at, so the nowcast is blind, but the protocol's wording "before any official 2026 regional figure is looked at" holds only in that sense | Discovered when checking for the release |
| 2026-10-12 | Post hoc diagnosis of the 2026 miss (wp1_diagnose_2026.md): main cause extrapolation of a positive hot-day weight far beyond the 2017–2025 range; fix proposed, not yet run | Understanding the miss before any change |
| 2026-10-14 | Addendum B written (no extrapolation, damage-only weather, compound drought); 2026 excluded as a test because Defra's figures are known | Response to the diagnosed 2026 miss |
| 2026-10-14 | Addendum B run: adopted for spring barley (both cutoffs) under the rule; not for wheat or winter barley. 2026 shown as an illustration only | Results of addendum B |
| 2026-10-17 | Addendum C written: MODIS long record, Sentinel-1 spring cross-ratio, scheme share and flood/peat × wet winter | Using the supporting datasets listed for WP1 |
| 2026-10-17 | Addendum C run: C2 (Sentinel-1) adopted for winter barley at mid-July; C1 reported separately (weaker than Sentinel-2). **Deviation from the rule:** C3 met the adoption rule for wheat but is not adopted, because a post hoc check showed its gain comes from the agreement share acting as an indicator of the two poor 2024–2025 seasons (see wp1_addendum_c.md) | Avoid building a timing coincidence into future forecasts |
| 2026-10-17 | Addendum D written: embeddings, previous-year only for the nowcast (the season's own embedding sees after the harvest) | Using the embeddings in WP1 |
| 2026-10-17 | Addendum D run: embeddings not adopted for any crop; even the after-season own-year embedding carries little regional yield information | Results of addendum D |
| 2026-10-29 | Addendum E written: degree-days above 30 °C, sign-constrained weather, area-of-applicability flag, weighted conformal intervals; adoption rules fixed; 2027 is the confirmatory test, 2026 fair only for the flag | Registered before Defra's final 2026 figures (10 December 2026) |
| 2026-10-30 | **Addendum E clarifications, before any degree-day value was fetched or any E model fitted.** (1) *Current model* per crop and cutoff = the model in use: wheat, first run (both cutoffs); winter barley, first run + Sentinel-1 (addendum C2) at mid-July and first run at end of August; spring barley, addendum B (both cutoffs). (2) *Error in the held-out extreme seasons* = mean absolute England-level error (mean over regions of predicted minus Defra anomaly, t/ha, as in addendum B) in 2018, 2022 and 2025, each held out with all other seasons as training (leave-one-extreme-season-out coincides with leave-one-year-out for those seasons). (3) E3: a season counts as flagged if at least half its regions are flagged; *other held-out region-seasons* = the region-seasons of 2017, 2019, 2020, 2021, 2023 and 2024 under leave-one-year-out; features and weights are those of the E2 model fitted on the fold's training years, and the threshold comes from the training region-seasons' own inner leave-one-year-out DIs. (4) E4: calibration residuals come from inner leave-one-year-out within the training years (no held-out year is used); the unweighted comparison uses the same residuals with equal weights. (5) Degree-days: ERA5-Land DAILY_AGGR temperature_2m_max sampled at each weather cell centre as for the existing weather, summed over 1 June–15 July (mid-July) and 1 June–31 August (end of August), averaged over the crop's parcels in the region like the other weather terms. (6) 2026 (flag only, plus the illustration): the E2 model trained on 2017–2025, 2026 inputs with the predicted crop masks used for the 2026 nowcast. | Make the registered rules computable without choices after results |
