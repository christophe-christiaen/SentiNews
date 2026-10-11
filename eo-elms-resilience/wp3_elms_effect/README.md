# WP3 · Do ELMs buffer farms against shocks? (Paper 3)

**Question.** Does land in SFI and Countryside Stewardship respond differently to shocks than comparable land outside?
**AI contribution.** (1) Label-efficient detection of ELM actions on fields from geospatial embeddings, using the open
scheme layers as (noisy) labels; (2) embedding-based causal inference: look-alike controls, double ML / causal forests.
**Target venues:** ICML (application-driven), CVPR EarthVision (detection part), AAAI AI for Social Impact; stretch:
Nature Machine Intelligence.

## Starting point (pilot)
Site-level CS share shows no link to drought response, in cropland (37 sites) or grassland (20), for 2022, 2025, 2026
or the 2023 rebound (all p > 0.2). Reasons: small n, snapshot data (mostly 2022+), share measured per 6 × 6 km window
rather than per field. WP3 fixes all three.

## Data and how it is used here
| Input | Role in WP3 |
|---|---|
| CS options + agreements (GIS) | **Treatment**: option code × field × start/end date |
| SFI actions + agreement areas (GIS) | **Treatment** for the largest ELM scheme |
| Environmental Stewardship (legacy) | Pre-2016 history; earlier cohorts for event studies |
| Agreement history | Start dates for ended agreements (**gap**: RPA request or archived snapshots) |
| Embeddings (AlphaEarth, TESSERA, Clay/LGND) | **Central**: action detection; pre-treatment field similarity for matching |
| Sentinel-2 | Per-field response around agreement start; interpretable check on embeddings |
| Sentinel-1 | Management signals: mowing, grazing, tillage, cover crops |
| LST (Landsat ST, 30 m) | Do scheme fields run cooler / recover faster under heat? |
| Field parcels, CROME | Unit of analysis; match on crop, size, soil |

## Method plan
1. **Detection.** Linear probes and small heads on frozen embeddings vs fine-tuned models; label noise handled
   explicitly (declared ≠ implemented). Report per option type (cover crop, herbal ley, buffer strip, low-input grassland).
2. **Matching.** For each treated field, controls with near-identical *pre-agreement* embeddings, crop and region.
3. **Effects.** Event study around agreement start; double ML / causal forests for heterogeneity by option and region.
4. **Checks.** Injected synthetic effects, placebo start dates, spatially held-out evaluation.
5. Pre-register outcomes, shock years and matching rules before looking at treated outcomes.

## First tasks
- [x] Ingest CS options, CS management areas, ES options/agreements, SFI actions and SFI agreement areas for the pilot windows (`shared/src/fetch_schemes.py`)
- [x] Check which layers carry start dates (all do; live snapshots only) → `results/scheme_inventory_pilot.md`
- [x] SFI / CS action-code lookup (`shared/config/action_codes.csv`, 100% of pilot SFI records)
- [x] AlphaEarth demo: 6 sites × 2019/2025 at 20 m, ~11,000 scheme points + ~3,000 controls per year (`shared/data/embeddings/alphaearth_ov1/`); full run via Earth Engine
- [x] TESSERA demo: same 6 sites × 2019/2025 at 10 m via the v1.1 Zarr store (`shared/data/embeddings/tessera/`)
- [x] First embedding probes (`src/embedding_probe.py` → `results/embedding_probe/`): grassland vs arable SFI land AUC 0.92–0.97
  on held-out sites; herbal leys vs other grassland only 0.57–0.62; 2019→2025 change dominated by crop rotation
- [ ] Detection probe per CS option type, with a Sentinel-2 index baseline
- [x] Pre-registration frozen 11 Oct 2026 (`results/preregistration.md`, commit b0f232b; later choices in its decisions record)
- [x] First run on Sentinel-2, 2017–2026 (below)

## First results (Sentinel-2, October 2026)
337,131 cereal parcels (247,441 entering an agreement in 2021–2026, 89,690 never in a scheme), matched within region.
- **H1, smaller July drop in shock seasons:** +0.06 to +0.08 SD in all three designs. Significant in the frozen plan
  (+0.082) and trend-adjusted (+0.074), but the frozen-plan placebo fails (+0.079), and the within-cohort design, which
  passes its placebo, is not significant (+0.062, p = 0.44). **Consistent with buffering, not established.**
- **H2, better recovery:** null in every design. **H3, land-use change vs management options:** sign changes, no evidence.
- Files: `results/wp3_results.md` (frozen plan and all pre-agreed checks), `results/wp3_trend_adjusted.md`,
  `results/wp3_within_cohort.md`, `results/treatment_summary.md`; figure `../results/maps/wp3_effects.png`.
- Run: `src/build_treatment.py` → `src/wp3_did.py` → `src/wp3_trend_adjusted.py` → `src/wp3_within_cohort.py` → `src/wp3_figure.py`.

```
src/        models and feature pipelines specific to WP3
notebooks/  exploration
results/    tables and figures for Paper 3
```
