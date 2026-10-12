# EO signal for UK agri-environment schemes and regional resilience — pilot

**Question.** Is there a statistically detectable signal in Earth-observation (EO) spectral
indices that relates to (a) UK regional agricultural outcomes, (b) resilience to climate
shocks and (c) agri-environment scheme (AES / ELMs) coverage?

This repository holds a **pilot** built entirely from open data. It is a
feasibility check for a full study, not a finished result.

## Repository layout
```
src/, data/, results/, docs/   pilot (MODIS, 50 sites) — results shown in the deck
shared/                        one data layer for all work packages (catalogue, configs, fetchers)
wp1_regional_signal/           Paper 1 · Seeing the harvest early (weakly supervised nowcasting)
wp2_resilience/                Paper 2 · Resilience from space (counterfactual forecasting)
wp3_elms_effect/               Paper 3 · Do ELMs buffer farms? (embedding detection + causal ML)
```
Data use across work packages (details in `shared/README.md`):

| | WP1 harvest | WP2 resilience | WP3 ELMs |
|---|---|---|---|
| Sentinel-2 | Core in-season features | Field stress / recovery | Field response around agreement start |
| Sentinel-1 | Cloud gaps | Floods, soil moisture | Mowing, grazing, tillage |
| Land surface temperature | Heat-stress covariate | Early vs late drought | Cooler scheme fields? |
| Geospatial embeddings | Supporting context | Land-use change | **Central**: detection, matching |
| CS / SFI GIS (options, dates) | Mask / covariate | Covariate | **Treatment** |

## Data (all open)
| Source | What | Licence |
|---|---|---|
| NASA MODIS **MOD13Q1** v061 (Terra) via ORNL DAAC subset API | 250 m, 16-day NDVI, 2001–2026, Mar–Aug | NASA open data |
| NASA MODIS **MYD13Q1** v061 (Aqua) | Same, 2016–2026, cross-sensor check | NASA open data |
| NASA MODIS **MCD12Q1** (2019) | 500 m land cover (IGBP) → cropland / grassland masks | NASA open data |
| Defra *Cereal and oilseed rape production* (`data/raw/cops.ods`) | Regional wheat yields (t/ha), 8 English regions + Scotland + Wales | OGL v3 |
| Defra *Total income from farming for the regions of England* (`tiff_itl1*.ods`) | TIFF, crop output per ha, ITL1, 2010–2025 | OGL v3 |
| Natural England / RPA *Countryside Stewardship Management Areas* (ArcGIS FeatureServer) | Live CS agreement polygons, clipped to each site | OGL v3 |

## Design
* 50 sites (5 per region × 10 regions), each a 6 × 6 km window in agricultural land, chosen *a priori*
  (`src/sites.py`). Each 250 m pixel is masked to cropland (IGBP 12, 14) or grassland (10).
* NDVI metrics per site-year (`src/build_ndvi.py`): **peak** = mean of 3 highest composites,
  late Apr–mid Jul (primary, pre-specified); **early** = same, using data available by mid-July;
  **july** = max composite late Jun–late Jul (senescence / drought).
* Tests (`src/analysis.py`): H1 yield, H1b lead time, H1c cross-regional (year fixed effects),
  H2 income, H3 drought shock profiles, H4 CS coverage vs drought response.
  Anomalies are detrended per region; out-of-sample skill is leave-one-year-out.

## Headline pilot results (`results/pilot_results.json`)
| Test | Result |
|---|---|
| H1 region-year NDVI vs wheat-yield anomaly | r = 0.57, n = 250, leave-one-year-out R² = 0.27 |
| H1b data available by mid-July | r = 0.58, out-of-sample R² = 0.26 |
| H1c with year fixed effects (within-year, across regions) | +1.0 t/ha per +0.1 NDVI, p ≈ 0.001 |
| England, national series | r = 0.72 (n = 25 years) |
| H2 TIFF per ha (region + year FE) | +12 % per 0.1 NDVI, p ≈ 0.2 (not significant) |
| H2 crop output per ha | +4.8 % per 0.1 NDVI, p = 0.03 (region-clustered); fragile |
| H3 July NDVI in drought years | 2022 and 2025 ≈ −2 SD (crop and grass); 2018 grass −1.9 SD, crop −1.0 SD |
| H4 CS share vs drought response (40 English sites) | no detectable association (ρ = 0.19, p = 0.24 for 2022) |

**Known failures.** 2012 (wet year, disease; yields −1.2 t/ha, NDVI normal) and 2022 (drought after
grain fill; July NDVI −2 SD but yields above trend). Greenness is not yield.

**Caveats.** 5 sites per region is a sample, not a census; MODIS 250 m mixes field edges;
the land-cover mask is static (2019); regional yield statistics are themselves survey estimates;
CS polygons are the current live snapshot, so H4 is cross-sectional and confounded by land type.

## Maps (`results/maps/`)
* `map1_sites_cs_coverage.png` — 50 sites; English sites shaded by Countryside Stewardship share
* `map2_yield_signal_by_region.png` — NDVI–yield correlation by region
* `map3_drought_fingerprints.png` — July NDVI anomaly, 2018 / 2022 / 2025
* `map4_recovery.png` — the following season after 2018 and 2022


## Yield signal by land cover (`src/yield_by_cover.py`, results in `results/yield_by_cover/`)
| Test | Cropland | Grassland |
|---|---|---|
| NDVI vs wheat-yield anomaly, r (region-years) | 0.57 (n = 250, 10 regions) | 0.40 (n = 175, 7 regions) |
| Out-of-sample R² (leave-one-year-out) | 0.27 | 0.10 |
| Both in one model, year effects (7 regions with both) | +1.1 t/ha per 0.1 NDVI, p = 0.004 | +0.03, p = 0.95 |
| Early warning (data to mid-July): r / out-of-sample R² | 0.58 / 0.26 | 0.41 / 0.11 |
| Early warning, both in one model with year effects | +0.8 t/ha per 0.1 NDVI, p = 0.02 | +0.08, p = 0.85 |

The yield signal comes from cropland, not shared regional weather. Map: `results/maps/map2_yield_signal_by_cover.png`.

## Income by land cover (`src/income_by_cover.py`, results in `results/income_by_cover/`)
Same method as the pilot income test (log £/ha, region + year effects, ITL1 England 2010–2025).

| Outcome, % per +0.1 NDVI | Cropland (8 regions) | Grassland (5 regions) |
|---|---|---|
| Total Income from Farming | +12.6 (p = 0.24) | +8.5 (p = 0.69) |
| Crop output | +4.8 early-season (p = 0.03 region-clustered, 0.26 OLS) | −3.1 (p = 0.70) |
| Livestock output | −1.0 (p = 0.79) | −7.6 (p = 0.26; wrong sign, plausibly price effects) |

No reliable income signal from either land cover at regional scale.

## Cumulative and compound shocks (`src/cumulative.py`, results in `results/cumulative/`)

> **Correction, 12 October 2026.** The national field-level version of these tests (WP2, 381,400 parcels) does not
> survive a within-field check: once each field's own level is removed, legacy and hit-harder effects are small at most
> (`wp2_resilience/results/within_field_check.md`). The pilot results below were not tested that way; sites were
> compared against a 2001–2015 normal and later seasons share any offset from it, so "unrecovered land is hit harder"
> is **not confirmed** until the pilot is re-run with site effects.
Responds to the question of regions hit again before they could recover. Uses the 2026 MODIS season (complete to mid-August).

* **Stress index** per site-year: mean of peak-season and July NDVI anomalies (z vs the site's 2001–2015 normal), averaged over crop and grass masks.
* **Shock** ≤ −1 SD; **recovered** ≥ −0.5 SD; **compound hit** = shock in a year that started below −0.5 SD;
  **stress debt** D(t) = 0.5·D(t−1) + min(S(t), 0).
* **Typology 2016–2026:** persistent stress (3+ years below normal) > back-to-back hits > slow recovery > bounced back.

| Result | Value |
|---|---|
| Unrecovered sites hit harder in shock years (2018, 2022, 2025, 2026) | +0.35 SD per SD carried in, n = 200, p < 0.001 |
| Stress debt slows the next rebound | 0.31 SD per unit debt, n = 150, p = 0.04 |
| Deficits persist beyond common weather (all years) | +0.12, p = 0.002 |
| Lag-1 autocorrelation, 2002–13 → 2014–26 | rose in 10 of 10 regions (indicative; short windows) |
| Site types | 25 back-to-back, 16 persistent, 4 slow, 5 bounced back |

**Land-cover control (`src/cumulative_cover.py`).** Re-run at site × land-cover level (44 crop, 27 grass series) with
separate crop and grass year effects. Unrecovered land is hit harder in both (pooled +0.34, p < 0.001; crop +0.38; grass +0.27,
p = 0.03); legacy holds (+0.12, p = 0.003); no significant crop–grass difference. The debt-slows-rebound effect weakens to
0.23, p = 0.09 (suggestive). North West persistence comes from its grassland, North East persistence from its cropland.
Persistence (lag-1 autocorrelation, 2002–13 → 2014–26) rose in 9 of 10 cropland regions and 7 of 7 grassland regions.

**Stewardship coverage by land cover (`src/cs_by_cover.py`).** Site CS share vs the stress index in 2022 (agreements started by 2021),
2025 and 2026 (all live agreements) and the 2023 rebound, separately for cropland (37 English sites) and grassland (20): no
association in any test (all p > 0.2, Spearman and region fixed effects). CS share is for the whole site window, not split by land cover.

**Cross-sensor check (`src/fetch_aqua.py`, `src/crosscheck_aqua.py`).** Terra's orbit has drifted since ~2020; Aqua's the
opposite way. On Aqua (2016–2026, same sites and masks): r = 0.86 with Terra across region-years, no trend in the gap
(p = 0.38). The 2025–26 back-to-back drought and North East persistent stress hold on both; the depth of 2022 and the
slow 2023 recovery are milder on Aqua. By land cover (`results/cumulative/crosscheck_aqua_by_cover.json`): cropland r = 0.85, grassland r = 0.84, no drift
trend in either (p = 0.33, 0.54); the 2025–26 drought holds in both, and North East cropland (2023–26) and North West grassland
(2024–26) stay below normal on Aqua too.

Crop vs grass maps (`src/cover_maps.py`): `map3_drought_by_cover.png`, `map4_recovery_by_cover.png`, `map5_stress_debt_by_cover.png`,
`map6_resilience_types_by_cover.png`, `fig_timeline_heat_by_cover.png` (regions filled only where ≥ 2 sites have that land cover). These are the versions used in the deck.

Figures: `results/maps/fig_timeline_heat.png`, `map4_recovery.png` (2019 / 2023 / 2026), `map5_stress_debt.png`,
`map6_resilience_types.png`.

## Reproduce
```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
cd src
python fetch_modis.py     # ~15–60 min, depends on ORNL server load; writes data/raw/modis/
python fetch_aes.py       # Countryside Stewardship coverage per site
python build_ndvi.py
python analysis.py
python figures.py
python yield_by_cover.py
python income_by_cover.py
python fetch_aqua.py       # Aqua cross-check data
python cumulative.py
python cumulative_cover.py
python cs_by_cover.py
python cover_maps.py       # crop vs grass map versions (*_by_cover.png)
python crosscheck_aqua.py
python cumulative_maps.py
python maps.py            # results/maps/*.png (boundaries: ONS ITL1 2021, data/raw/boundaries/)
```
`data/raw/modis/` and `data/raw/modis_aqua/` are git-ignored; re-download with `fetch_modis.py`.
