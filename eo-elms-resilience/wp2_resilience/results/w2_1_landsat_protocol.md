# W2-1 protocol: a Landsat 30 m long baseline for every cereal field

**Written 29 October 2026, before any Landsat value was extracted.** Changes after this date go in the record at the end.

## Question
The MODIS long-baseline test (16-season normal, 2001–2016) found carry-over of about zero within fields, but MODIS
pixels (250 m, about 6 ha) mix neighbouring fields. Does the same hold at 30 m, where a field-centre pixel sees one
field? And does the short-baseline artefact appear on Landsat when its normal is cut to four seasons?

## Data
- **Sensors:** Landsat 5 TM, 7 ETM+, 8 OLI and 9 OLI-2, Collection 2 Level-2 surface reflectance (Google Earth Engine:
  LANDSAT/LT05, LE07, LC08, LC09 /C02/T1_L2), seasons 2001–2026.
- **Masking:** QA_PIXEL fill, dilated cloud, cloud, cloud shadow and snow removed; scale factor 0.0000275, offset −0.2.
  Landsat 7 scan-line gaps after May 2003 are simply missing values.
- **Indices per field-centre pixel (30 m, the pixel containing the RPA parcel point), per season**, in the same windows
  as the MODIS test: **July** = median of clear NDVI observations 1 July–15 August (widened from July alone because
  Landsat observes every 8–16 days); **peak** = maximum of clear NDVI 15 April–15 July.
- **No cross-sensor coefficients.** Sensor changes act on all fields of a season alike; the tests' cell × season effects
  absorb that. Sensitivity: Landsat 7 only, which spans 2001–2023 with one sensor.
- **Parcels:** the 381,400 cereal-land parcels of WP2.

## Outcomes and tests (as the MODIS long-baseline test, `modis_long_baseline_check.py`)
Stress S = mean of the July and peak NDVI z-scores against each field's own normal, clipped to ±6; a field needs at
least 8 clear baseline seasons for the long normal and 3 for the short one. Shocks: the field's ERA5-Land cell
(unchanged). T1 S_t on S_t−1; T2 the same in shock seasons; T3 rebound on stress debt. Versions: pooled with cell ×
season effects; field fixed effects; Anderson–Hsiao; season-shuffling placebo; T2 leaving out one shock season at a
time; errors clustered by ERA5 cell.
- **L-long:** normal 2001–2016, tests on 2002–2026 and on 2017–2026.
- **L-short:** normal 2017–2020 (as Sentinel-2), tests on 2017–2026: the artefact on the same sensor.
- **L7 only:** L-long restricted to Landsat 7 observations, 2002–2023.
- Calibration: the existing simulation of this design (16-season normal over 26 seasons).

## Reading, fixed in advance
- **Confirms the MODIS result** if, with the long normal (2002–2026), the Anderson–Hsiao estimates of T1 and T2 lie
  within ±0.05 of zero. Otherwise they are reported as carry-over, with sign.
- **Artefact replicates on Landsat** if, with the short normal, pooled T1 minus Anderson–Hsiao T1 is at least 0.05 and
  the shuffled placebo is positive with p < 0.01.
- **Pixel mixing mattered** if Landsat and MODIS long-normal Anderson–Hsiao T1 differ by more than 0.05.
- The Landsat 7–only version is reported as a sensitivity check; if it differs from the all-sensor version by more
  than 0.05 in Anderson–Hsiao T1, the sensor mix is flagged as a limit.

## Output
`wp2_resilience/results/w2_1_landsat.md`, `.json` (aggregates only); per-parcel values in `shared/data/landsat_parcels/`
(not published).

## Record
| Date | Change | Reason |
|---|---|---|
| 2026-10-29 | Protocol written | Before any Landsat value |
| 2026-10-29 | Run ([w2_1_landsat.md](w2_1_landsat.md)); all 381,400 parcels have a usable long normal. R1 confirms MODIS (Anderson–Hsiao T1 −0.020, T2 −0.021). R2 artefact replicates on Landsat (short normal: pooled − Anderson–Hsiao +0.128; placebo +0.076, p < 0.001). R3 pixel mixing did not matter (Landsat −0.020 vs MODIS −0.019). R4 sensor mix flagged: Landsat 7 only gives Anderson–Hsiao T1 −0.083 (353,008 parcels, 2002–2023); every version is at or below zero, none shows positive carry-over | Result |
