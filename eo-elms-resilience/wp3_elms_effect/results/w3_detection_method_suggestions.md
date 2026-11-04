# Method suggestions for linear and water options (not adopted)

**Status: suggestions received from the project lead on 4 November 2026, checked against their sources. Nothing here changes a
registered rule.** They apply when [W3-1](w3_1_linear_features_protocol.md) and [W3-W](w3_w_ponds_protocol.md) resume;
resilience work comes first. Adopting any of them needs a record row before any value is computed.

## The suggestion
Treat detection as fusion, not a choice of one source:
- **LiDAR (terrain and surface models):** fixed structure, such as ponds, hedges and ditches.
- **Sub-metre aerial imagery:** buffer strips, using repeat years to date features roughly, embedded with DINOv3-SAT, Clay v1.5
  or AnySat.
- **Sentinel-2 or TESSERA time series:** when a change happened.
- **AnySat:** a single model for the mix, with LiDAR as its elevation channel.
- **Google's Farmscapes map:** existing linear-feature masks, instead of building our own.

LiDAR is expected to fail for grass strips, which differ in vegetation type more than height. It also cannot date a feature against
agreement start, so it is at best a static covariate or an existence check.

## What the sources support

| Claim | Checked | Consequence here |
|---|---|---|
| UKCEH's England hedgerow map came from LiDAR, with 96% accuracy | Yes, from a trade article. 96% compares **total hedge length** across surveyed 1 km squares, so errors can cancel. It is not a per-hedge rate | Good for regional length; does not show field-level detection |
| LiDAR flights ran 2016–2021, each area once | Partly. Programme metadata gives 11 November 2016 to 5 April 2021, but the 2022 composite uses surveys to 5 May 2022 and also older time-stamped archive. Flown over winters | One survey date per tile is close enough to treat as one snapshot. Winter flights make the "tall standing crop beside a mown margin" route unlikely |
| Environment Agency 1 m terrain data is public | Yes: about 99% of England, ±15 cm RMSE vertically, free with attribution | Usable |
| Farmscapes covers most of England at 25 cm, hedgerow F1 72% | Yes. Precision 73, recall 70; stone walls F1 60; woodland 96 | Usable as a mask with stated error |
| Farmscapes masks can replace our own | Only for hedges, walls and woodland. These are the only layers in the first public release; strips, margins and ponds are not. The imagery is proprietary, 2018–2022, a static snapshot, and the paper says change monitoring is not yet possible | Spans agreement entry, so not a clean pre-entry covariate, and cannot date anything |
| AnySat takes aerial RGB+NIR+elevation at 0.2 m with Sentinel-1/2 time series | Partly. Those modalities exist in its training sets, but no one set has all of them: FLAIR has elevation with Sentinel-2 only; TreeSatAI-TS has Sentinel-1 and 2 without elevation. Code and models are released | Needs a test. Its training data, as far as checked, are not British; 1 m LiDAR and 25 cm aerial would have to be resampled to fit |
| APGB 25 cm has repeat years, so features can be dated | Partly. No single repeat cycle found (two and three years in different sources); the public feed serves the most recent imagery; the licence seen is for public-sector members | **Likely blocker: access for this project is unconfirmed** |
| DINOv3-SAT | Yes: satellite weights trained on 0.6 m Maxar RGB imagery. Download is gated, under a custom licence | Terms need the project lead's approval; sharper imagery than training data is untested |
| Ponds appear as terrain depressions and point-cloud voids, even under trees | **No source checked** | Treat as a hypothesis to test |

## What this project has already found
The W3-1 record (1 November 2026) tried a LiDAR vegetation height model for woody field edges. It sees woody vegetation outside
the field outline, but hedge-management fields do not have more than never-treated fields (−0.0002, 95% interval −0.0038 to
+0.0034), so it failed its registered check as a covariate. LiDAR can show that a hedge exists; that has not shown it can
identify which hedges are in a scheme. Most option effects are also management of an existing feature, not a new structure.

## Non-EO sources, candidates only

| Source | Best use | Limits |
|---|---|---|
| **Terrain from a DEM** (slope, low-lying position, wetness index, depressions) | Resilience: a fixed field characteristic for matching or for splitting drought and wet-winter results. No timing problem, because terrain does not change with the scheme | Terrain is not an outcome; a split is exploratory unless registered |
| **Ground-level photos** (Mapillary, Geograph) | Spot-checking a sample of detection results, with dates where the photo has them | Roadside views, patchy rural coverage (no British measure found), unsystematic. Geograph has only 195 photos under one hedgerow-field tag. Licences not verified. Faces and number plates need care. A 2023 study reached AUC 0.87 for wheat and 0.85 for maize from street-level images, but not in Britain and not for scheme options |
| **Mapped landscape classes** (National Character Areas, soils, flood zones) | Stratifying results | Fixed context, not evidence of an option. Flood zone, peat and the `nca` field are already held |

## Sources
- Conserva et al., *Mapping Farmed Landscapes from Remote Sensing*, [arXiv 2506.13993](https://arxiv.org/abs/2506.13993)
- Astruc et al., *AnySat: One Earth Observation Model for Many Resolutions, Scales, and Modalities*, [arXiv 2412.14123](https://arxiv.org/abs/2412.14123)
- [UKCEH hedgerow map, GeoConnexion, 2 February 2024](https://www.geoconnexion.com/in-depth/high-tech-aerial-mapping-reveals-englands-hedgerow-landscape) (trade article; the underlying UKCEH validation not read)
- [England 1 m Composite DTM/DSM, Earth Engine catalogue](https://developers.google.com/earth-engine/datasets/catalog/UK_EA_ENGLAND_1M_TERRAIN_2022)
- [APGB WMS feed](https://apgbgm.freshdesk.com/support/solutions/articles/201000067046-what-data-is-available-through-the-wms-feed-) and [APGB licence note](https://marine.gov.scot/taxonomy/term/2073)
- [DINOv3 SAT-493M model card](https://huggingface.co/facebook/dinov3-vitl16-pretrain-sat493m)
- [Crowdsourced street-level imagery for crop monitoring, *Land* 2018](https://doi.org/10.3390/land7040127); [*Geographies*, August 2023](https://doaj.org/article/7155e01a18e64c0d87e573ab5e43c917); [Geograph tag](https://www.geograph.org.uk/tagged/hedgerow+dividing+fields)
