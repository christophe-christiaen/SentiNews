# Shared data layer

All three work packages read from one set of harmonised inputs. Each source is downloaded and
processed **once** here, then consumed by `wp1_regional_signal/`, `wp2_resilience/` and `wp3_elms_effect/`.

```
shared/
  config/data_sources.yaml   machine-readable catalogue (source, access, licence, years, resolution, status)
  config/study_area.yaml     common grid, years, CRS, regions
  src/fetch_schemes.py       CS / ES / SFI layers: --pilot (40 English windows) or --national <layer>
  src/summarise_schemes.py   inventory -> wp3_elms_effect/results/scheme_inventory_pilot.md
  src/fetch_embeddings.py    AlphaEarth (S3, no login) | TESSERA (geotessera) | Earth Engine (server-side)
  data/                      raw + harmonised data (git-ignored; large)
```

### Running the fetchers
```bash
cd shared/src
python fetch_schemes.py --pilot                       # ~10 min; six layers clipped to the pilot windows
python fetch_schemes.py --national sfi_actions        # whole-England attribute table (2.5M rows)
python summarise_schemes.py
python fetch_embeddings.py --sites top6 --years 2019,2025 --overview 1   # AlphaEarth, 20 m, local
python3.12 fetch_embeddings.py --backend tessera --sites top6 --years 2019,2025   # needs geotessera>=0.11 (Python 3.12)
python fetch_embeddings.py --backend earthengine --ee-project <your-project> --sites all --years 2017,2018,2019,2020,2021,2022,2023,2024,2025
```
**Bandwidth note.** AlphaEarth tiles are band-interleaved (64 bands x 1024-px blocks), so one 6 x 6 km window at 10 m
costs ~100 MB and ~5 min from this machine (~0.6 MB/s); 20 m (`--overview 1`) ~4x less. For all sites and years, or
national scale, use the Earth Engine backend (only sampled values are transferred) or run on a cloud machine.

**TESSERA** is read from its v1.1 Zarr store on Source Cooperative (`dclimate` variant, pinned: variants are not
comparable). `geotessera` 0.11+ needs Python 3.12 (`uv venv --python 3.12`; `uv pip install git+https://github.com/ucam-eo/geotessera`);
the PyPI 0.7.5 release still points at a retired Cambridge server. One 10 m window takes ~4 min here. Model weights
are on Hugging Face (`geotessera/TESSERA-V-1.0`, CC0) if we ever need to run inference ourselves.

**Action codes.** `src/fetch_sfi_codes.py` builds `config/action_codes.csv` (259 codes) from Defra's SFI uptake
statistics (SFI23/SFI24) and the GOV.UK funding finder (SFI26, CS); strip the `_26` suffix before lookup. Covers
100% of SFI action records in the pilot windows.

**Common frame.** British National Grid (EPSG:27700); 10 m analysis grid for Sentinel-derived layers, aggregated to
**field parcel** (unit for WP3), **site / catchment** and **ITL3 region** (unit for WP1–WP2). Growing seasons 2017–2026
for Sentinel and embeddings; 2001–2026 baseline from MODIS / Landsat (from the pilot).

## Sources and how each work package uses them

| Source | What it gives | WP1 · harvest | WP2 · resilience | WP3 · ELMs |
|---|---|---|---|---|
| **Sentinel-2 L2A** (10–20 m, ~5-day) | Red-edge (B5–B7), SWIR (B11–12), NDVI/NDRE/NDMI time series | Core: in-season crop features to mid-July | Core: field-level stress and recovery curves | Core: per-field response around agreement start |
| **Sentinel-1 GRD** (C-band SAR, 10 m, all-weather) | VV/VH backscatter, coherence | Fills cloud gaps in the nowcast | Floods, waterlogging, soil-moisture proxy | Detect mowing, grazing, tillage, cover crops |
| **Land surface temperature** | Heat stress, evaporative stress timing | Late-season heat as a yield covariate | Separates early vs late droughts (the 2022 miss) | Do scheme fields run cooler under drought? |
| **MODIS / Landsat** (pilot) | 2001–2026 NDVI baseline | Long-run normal for anomalies | 25-year shock history, typology | Pre-2017 field history |
| **Geospatial embeddings** | Pretrained per-pixel / per-chip vectors | Supporting: farming-system context | Minor: year-to-year shift = land-use change | **Central**: action detection, look-alike controls |
| **Countryside Stewardship** (agreements + options GIS) | Which option is on which field, start/end dates | Mask / covariate | Scheme share as a resilience covariate | **Treatment**: option × field × start date |
| **SFI** (actions + agreement areas GIS) | Which SFI action is on which land | Mask / covariate | Covariate | **Treatment** (largest ELM scheme) |
| **Field parcels / crop maps** | Unit of analysis; crop type per field | Crop masks per region | Crop vs grass per field | Matching by crop, parcel size |
| **Outcomes** (Defra yields, regional accounts, FBS) | Yields, income, output | Target variable | Shock impacts | Economic side of scheme effects |

### Land surface temperature options
| Product | Resolution | Revisit | Notes |
|---|---|---|---|
| Landsat 8/9 Collection 2 Level-2 Surface Temperature | 30 m (thermal 100 m) | 8 days combined | Field scale; cloud-limited in the UK |
| MODIS MOD11A1 / MYD11A1 (Terra / Aqua) | 1 km | Daily | Long record from 2000; same orbit-drift caveat as the pilot |
| Sentinel-3 SLSTR LST | 1 km | Daily | Copernicus; continuity after MODIS |
| ECOSTRESS (ISS) | ~70 m | Irregular | Diurnal coverage; patchy |

Plan: Sentinel-3 / MODIS LST for regional daily heat stress; Landsat ST for field-level contrasts (WP3).

### Geospatial embeddings (precomputed products and open models)
| Embedding | Form | Licence (checked Oct 2026) | Main use |
|---|---|---|---|
| AlphaEarth (Google DeepMind) | 64-d, 10 m, annual, 2017–2025 | CC BY 4.0 (model closed) | WP3 detection + matching; WP1 context |
| TESSERA (Cambridge) | 128-d, 10 m, annual, S1 + S2 | CC0 data/weights, MIT code | WP3; benchmark vs AlphaEarth |
| Clay v1.5 / LGND Sentinel-2 embeddings | Chip-level, monthly | Apache-2.0 model; CC BY 4.0 embeddings | WP3 within-year changes |
| Presto, Galileo (NASA Harvest) | Pixel time series; multimodal | MIT | WP1 in-season nowcast; WP2 with few labels |
| Prithvi-EO-2.0, TerraMind (IBM with NASA / ESA) | HLS 30 m; any-to-any multimodal | Permissive / Apache-2.0 | WP2 longer record; TerraMind for cloud gap-filling |
| Major TOM (ESA Φ-lab) | Global, several models | CC BY-SA 4.0 (share-alike) | Benchmark only (licence) |

Rule across WPs: **embeddings never replace interpretable indices** — every embedding result is reported next to an
NDVI/red-edge/SWIR baseline, and validated on held-out regions, not random fields.

### Scheme data (GIS + agreement records)
| Layer | Publisher | What is in it | Status |
|---|---|---|---|
| Countryside Stewardship Scheme Management Areas (England) | Natural England / RPA (ArcGIS FeatureServer) | Agreement polygons, CS type, start/end date, value | Used in pilot |
| Countryside Stewardship Scheme Options (England) | Natural England / RPA | Option codes per land parcel (e.g. cover crop, buffer strip, herbal ley) | To ingest |
| Countryside Stewardship Scheme Agreements (England) | Natural England / RPA | Agreement-level records | To ingest |
| SFI Scheme Actions (England) | RPA, Defra Data Services Platform | Which SFI action sits on which land; updated Sep 2026 | To ingest |
| SFI Scheme Agreement Areas (England) | RPA, Defra Data Services Platform | Land under live SFI agreements | To ingest |
| Environmental Stewardship (legacy) agreements and options | Natural England | Pre-2016 scheme history (ELS/HLS) | To ingest: gives pre-ELMs history |
| Agreement history (past snapshots) | RPA / archived open-data snapshots | Start dates for agreements no longer live | **Partly covered**: live CS options carry start dates 2017–2026 and live ES options 2009–2014; ended agreements still missing |

Open layers are live snapshots; the WP3 before/after design needs agreement history. Contract-level details beyond what
the GIS layers publish (payment rates, compliance outcomes) would need an RPA data request.

### Field parcels and crop maps
| Layer | Use | Status |
|---|---|---|
| Crop Map of England (CROME), RPA | Crop type per field polygon, annual | To check availability and years |
| RPA land parcels / field boundaries | Parcel unit for WP3 | To check open availability |
| UKCEH Land Cover Map | Crop vs grass masks (replaces MODIS 500 m mask) | To check licence |

Items marked "to check" are planned sources whose current availability and terms have not been verified yet.
