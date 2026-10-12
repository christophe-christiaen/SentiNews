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

## Record

| Date | Change | Reason |
|---|---|---|
| 2026-10-11 | Protocol written | Before any yield comparison |
| 2026-10-11 | Diagnostic after the nowcast was written: classifier vs CROME mask in 2025, and the 2025 held-out error (results, last section). Nowcast left unchanged | The 2026 nowcast is above average in a record-dry spring; checked whether the mask or the model drives it |
