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
- [x] Sentinel-2 field statistics for all 381,400 cereal parcels, 2017–2026 (`shared/src/gee_s2_interactive.py`)
- [x] Evaluation protocol fixed before any yield comparison (`results/protocol.md`)
- [x] Regional nowcast vs MODIS on the same years, 8 English regions, wheat and barley (`src/wp1_nowcast.py`)
- [x] 2026 nowcast written 11 Oct 2026, before the official 2026 figures (`results/wp1_nowcast_2026.csv`)
- [ ] **Grain-fill fix:** heat and moisture after mid-July (LST, ERA5 July–August); dry springs (2022, 2025) are
      over-predicted. New protocol entry before running
- [ ] Score the 2026 nowcast against Defra's provisional figures when published
- [ ] Learning from aggregates (field attention / multiple-instance learning) vs region medians; ITL3 targets

## First results (October 2026)
Leave-one-year-out over 2017–2025, 8 English Defra regions ([results](results/wp1_results.md)):
- **Wheat:** Sentinel-2 + weather by mid-July R² 0.64 (England 0.78), against 0.44 for the MODIS pilot on the same
  years and 0.45 for peak NDVI alone; already 0.55 by mid-May. Weather alone has no skill (−0.05).
- **Winter barley** 0.52, **spring barley** 0.52 by mid-July. 80% intervals cover 79–81% of held-out region-years.
- **2026:** wheat nowcast about 0.4–0.5 t/ha above the 2017–2025 mean, but the model over-predicted the dry 2025 by
  0.4 t/ha, so 2026 (drier still) is probably too high: see the last section of the results.

```
src/        models and feature pipelines specific to WP1
notebooks/  exploration
results/    tables and figures for Paper 1
```
