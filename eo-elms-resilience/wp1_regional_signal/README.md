# WP1 · Seeing the harvest early (Paper 1)

**Question.** Can Earth observation nowcast regional crop output months before official statistics?
**AI contribution.** Weakly supervised nowcasting: learn field-level signals from *regional* yield labels
(learning from aggregates), with calibrated uncertainty by date. **Target venues:** KDD Applied Data Science, ACM ICAIF.

## Starting point (pilot)
Cropland MODIS NDVI vs Defra wheat yield: r = 0.57, out-of-sample R² = 0.27; by mid-July 0.58 / 0.26. The signal comes
from cropland (grassland adds nothing once cropland is in). Misses: 2012 (disease), 2022 (late drought).

## Data and how it is used here
| Input | Role in WP1 |
|---|---|
| Sentinel-2 L2A | Core features: NDVI, red-edge (NDRE), SWIR moisture per field, to the mid-July cutoff |
| Sentinel-1 | Fills cloud gaps; crop-structure signal in wet springs |
| LST (MODIS / Sentinel-3 daily) | Heat stress around flowering and grain fill (fixes 2022-type misses) |
| Embeddings | Supporting: AlphaEarth / TESSERA of the *previous* year as farming-system context; Presto for in-season pixel series |
| CROME / crop masks | Wheat, barley, oilseed fields per region |
| CS / SFI layers | Mask or covariate (fields under arable options behave differently) |
| Defra yields, regional accounts | Targets (region-year) |

## Method plan
1. Field features → region aggregation by learned attention (multiple-instance learning) vs simple area-weighted mean.
2. Time-to-decision curve: skill vs cutoff date (May → August).
3. Uncertainty: conformal prediction intervals per region-year.
4. Validation: leave-one-year-out and leave-region-out; never random splits.
5. Baselines: pilot regression (floor), gradient boosting on indices, embeddings-only, fine-tuned Presto.

## First tasks
- [ ] Pull Sentinel-2 field statistics for the 50 pilot windows, 2017–2026 (`shared/src`)
- [ ] Rebuild the pilot yield test with Sentinel-2 vs MODIS on the same windows
- [ ] Add LST heat-stress features; re-test 2018/2022/2025
- [ ] Scale to all ITL3 regions with CROME crop masks

```
src/        models and feature pipelines specific to WP1
notebooks/  exploration
results/    tables and figures for Paper 1
```
