# X2-L protocol: the drought test with a Landsat long baseline

**Status: registered 5 November 2026 by public commit, before any Landsat value was used in an agreement comparison.
Exploratory; reported beside the frozen H1, never instead of it.** Builds on X2 (decisions record, 18 October 2026;
[wp3_x2_long_baseline.md](wp3_x2_long_baseline.md)) and W2-1 ([w2_1_landsat_protocol.md](../../wp2_resilience/results/w2_1_landsat_protocol.md)).
Changes after registration go in the record at the end.

## Why
X2 reran H1 against a 2001–2016 MODIS normal: +0.104 (SE 0.009), with a placebo of +0.061 (SE 0.009). So about three
fifths of the effect is already there before entry, and X2's reading was "selection, not the short normal". But MODIS
pixels (250 m, about 6 ha) mix neighbouring fields, and X2 named that as a limit. Agreement and non-agreement fields
that sit side by side share pixels, which could blur the gap between them or hide part of it. A 30 m pixel at the field
centre sees one field. The publication plan listed this rerun for after W2-1, which is finished.

## Data
Existing per-parcel values from W2-1 (`shared/data/landsat_parcels/`, not published); no new download. Landsat 5, 7, 8
and 9, Collection 2 Level-2, the 30 m pixel containing the parcel point, no cross-sensor coefficients. **July** is the
median of clear NDVI from 1 July to 15 August. The window is wider than MODIS's July because Landsat revisits every 8–16
days, so this is not a like-for-like change of pixel alone.

## Versions
Frozen-plan estimator, main dry-or-heat shock, H1, placebo with entry two seasons early, pre-trend Wald tests on event
times −4 to −1, SE clustered by ERA5 cell, strata and seasons as in X2. Only the outcome changes.
- **L1:** Landsat July NDVI z against each field's 2017–2020 seasons, at least 3 clear seasons (W2-1's short rule).
- **L2:** Landsat July NDVI z against each field's 2001–2016 seasons, at least 8 clear seasons (W2-1's long rule).
- **References, recomputed in the same run:** V0 Sentinel-2 and V2 MODIS 2001–2016.

**Sample:** X2's matched sample decides, so that sensor and pixel are all that change. The E3 matched sample is reported
beside it, because later WP3 results use it. **Reproduction first:** the recomputed V2 must come within 0.005 of X2's
H1 (+0.104) and placebo (+0.061). If it doesn't, for example because of the D1 or D2 data corrections, the gap is reported
and L1 and L2 are compared with the recomputed values, not X2's.

## Reading, fixed in advance
1. **Does pixel size matter?** Yes if L2's H1 or placebo differs from recomputed MODIS V2's by more than 0.05 SD, the same
   margin W2-1 used.
2. **Baseline mechanism, X2's rule:** supported if, from L1 to L2, the placebo shrinks by at least half and its 95% interval
   includes zero, or the pre-trend Wald test on the effect moves from p < 0.05 to p ≥ 0.05. Otherwise the placebo is read
   as selection.
3. **Does the drought cushion hold at field scale?** Supported only if L2's H1 interval is above zero and its placebo
   interval includes zero. Otherwise it stays "not established". This cannot change the frozen H1 reading.

## Reported, does not decide
- L2's share of H1 in the placebo, placebo ÷ H1, beside MODIS's.
- H1 minus the same contrast before entry (trend-adjusted), and within cohort with its before-entry version, for L2.
- **L2 with wet-shock cell-seasons dropped from both sides,** and the same for V0. Added because the wet-winter harvest
  contrast showed that "other seasons" can carry a hazard of their own.
- **Landsat 7 only,** normal 2001–2016, seasons to 2023, as a sensor check. Results then stop before most treated fields enter, and this is stated.
- **Coverage:** share of parcel-seasons with a value, by sensor era (to 2012, 2013 on), treated and never treated, shock and other.

## Stated limits
- **Sensor change:** the normal rests mostly on Landsat 5 and 7, while after-entry seasons rest on Landsat 8 and 9. Cell ×
  season strata absorb a shift common to a cell and season. A shift that scales with a field's greenness would not be absorbed.
- **Drift:** a 2001–2016 normal can drift by 2017–2026, as X2 noted.
- **Field centre:** one pixel can touch the field edge in small fields, and it is not a field mean.
- **Cloud:** few clear overpasses in western summers. Coverage may depend on the shock itself, since dry summers are clearer.
- **July only:** as X2, this reruns greenness; it says nothing about harvest.

## Known before this registration
X2's results; the W2-1 carry-over results on these same Landsat values, including the Landsat 7 finding; the frozen H1
and its placebos. No WP3 script has read these values, and no agreement comparison has been made with them.

## Output
`wp3_elms_effect/src/wp3_x2l_landsat.py`; `wp3_elms_effect/results/wp3_x2l_landsat.md`, `.json` (aggregates only).

## Record
| Date | Change | Reason |
|---|---|---|
| 2026-11-05 | Registered by public commit before any Landsat value was used in an agreement comparison. Not run | Project lead: register the Landsat rerun |
