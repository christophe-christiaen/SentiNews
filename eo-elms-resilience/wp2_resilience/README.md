# WP2 · Resilience from space (Paper 2)

**Question.** How hard is each region hit by drought or flood, how fast does it recover, and what happens when the next
shock arrives before recovery? **AI contribution.** Counterfactual forecasting: predict the no-shock trajectory from
weather and history; resistance = gap to observed, recovery = how fast it closes; cluster trajectories into a typology.
**Target venues:** ICLR ML4RS workshop, ACM SIGSPATIAL, ISPRS Journal.

## Starting point (pilot)
2018, 2022, 2025 and 2026 shocks with distinct regional footprints; unrecovered land is hit harder (+0.38 SD cropland,
+0.27 grassland); persistence rising in 9/10 cropland and 7/7 grassland regions; typology: bounced back, slow,
back-to-back, persistent. Robust across Terra and Aqua; 2022 depth sensor-dependent.

## Data and how it is used here
| Input | Role in WP2 |
|---|---|
| MODIS / Landsat (2001–2026) | Long baseline and shock history (keeps the 25-year record) |
| Sentinel-2 | Field-level stress and recovery curves since 2017 |
| Sentinel-1 | Flood extent and duration, waterlogging, soil-moisture proxy (winter shocks) |
| LST | Timing and intensity of heat/drought stress: separates early from late droughts |
| Embeddings | Minor: year-to-year embedding distance shows return to the old state vs change of use; Galileo for few-label shock mapping |
| CS / SFI layers | Covariate: does scheme share change resistance or recovery? (causal test is WP3) |
| Weather (HadUK-Grid, ERA5-Land) | Inputs to the counterfactual forecaster *(to add)* |
| Shock records | Validation: EA flood maps, drought declarations, insurance/payout data *(to check)* |

## Method plan
1. Counterfactual model trained on normal years (weather + phenology → expected greenness); held-out shock years.
2. Resistance, recovery time and stress debt per field, aggregated to catchment and ITL3; estimate the debt half-life
   from data instead of assuming 0.5.
3. Typology from trajectory embeddings (clustering), compared with the rule-based pilot typology.
4. Separate crop and grass throughout (pilot showed they differ).

## First tasks
- [ ] Move pilot `cumulative*.py` logic into `src/` as the baseline
- [ ] Add weather drivers and fit the counterfactual on 2001–2017; test on 2018, 2022, 2025, 2026
- [ ] Sentinel-1 flood layer for winters 2019/20, 2023/24
- [ ] Sensitivity of thresholds (−1 / −0.5 SD) and half-life

```
src/        models and feature pipelines specific to WP2
notebooks/  exploration
results/    tables and figures for Paper 2
```
