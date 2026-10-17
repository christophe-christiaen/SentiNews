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
