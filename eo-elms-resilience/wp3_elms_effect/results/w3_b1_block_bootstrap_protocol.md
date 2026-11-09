# W3-B1 protocol (#9): Paper B intervals with clustered resampling

**Status: registered 9 November 2026 by public commit, before any statistic below was computed. Exploratory check on inference only. Point estimates, models and reading rules of [w3_4_model_comparison.md](w3_4_model_comparison.md) are unchanged; only the intervals are redone.** Changes after registration go in the record at the end.

## The problem
Paper B's intervals on I\* (the selection-corrected detection metric) come from a bootstrap that resamples **single parcels** within each held-out region.
- Parcels in one holding or one agreement share a farmer, management, soils and weather.
- So they are not independent. Resampling them one at a time understates the uncertainty, and an interval that clears the 0.02 detection threshold may not clear it once clustering is allowed for.

## What is redone
The four-model comparison ([w3_4_model_comparison.py](../src/w3_4_model_comparison.py)): the same families, samples, comparisons (B for options, A for controls), features (AlphaEarth, Sentinel-2, TESSERA, Presto), leave-one-region-out predictions, I\* and the 0.02 rule.
1. **Reproduce first.** Predictions are refitted with the same seeds. Each I\* and AUC(post) must match the published JSON to within 1e-9 before any interval is drawn. If they don't, stop and log.
2. **Block bootstrap, primary.** Blocks are 10 km British National Grid squares (from each parcel's x, y). Each block is cut by region, so it never spans two held-out regions. Within each region, blocks are resampled with replacement, taking all their parcels. There are 1,000 resamples, shared across the four models (seed 29, as before), and resamples with a single class are skipped and counted.
3. **Sensitivity.** 5 km and 20 km blocks, with the same procedure.
4. **Pairwise model differences.** The same draws give the difference in I\* for each pair of models: a two-sided bootstrap p, Holm over the 36 tests as before, and the same verdict rule (best suited / leading group / not detectable).
5. **Design effect.** The ratio of the block interval's width to the parcel interval's width, for each family and model.

Why not cluster by agreement: the 2021–2024 entrants are mostly CS and SFI. SFI agreements have no polygons in the data we hold, and never-treated parcels have no agreement. So agreement clusters would cover only part of the sample. A 10 km block contains nearly all of a holding's parcels, so it nests both farm and agreement clustering, and it also absorbs local weather and soils.

## Reading, fixed in advance
For each option family:
- **Detectable beyond selection**, as before: the lower end of the 95% interval on I\* (comparison B) is above 0.02. Calibration on the two control families stays a point-estimate rule (within ±0.02) and is not changed by this check.
- **Label per family**, read on 10 km blocks:
  - **Holds under clustering:** the set of models detecting the family and the verdict (best suited / leading group / not detectable) are both unchanged.
  - **Detection holds, ranking changes:** the same models detect the family, but the verdict changes.
  - **Depends on clustering:** a model that detected the family no longer does, or the reverse.
- The 5 km and 20 km results are reported beside the primary. If they disagree with the 10 km result, that is stated, not resolved.

## Also for Paper B (text, not analysis)
- **State the split plainly:** training on all regions but one and testing on the held-out region. Parcels from one farm can't be on both sides of a region boundary unless the holding straddles it.
- **Frame I\* as difference-in-differences on classifier scores:** (pre + post vs pre) minus (pre + 2020 vs pre), with 2020 a pre-entry placebo year.

## Known before this registration
- **Published parcel-bootstrap results:** all of [w3_4_model_comparison.md](w3_4_model_comparison.md) (five families detectable beyond selection; margins and corners not detectable; TESSERA fails calibration).
- **Narrowest margins over 0.02:** the published interval lower ends closest to 0.02 are the cover crops for Sentinel-2 (+0.046) and Presto (+0.050). For margins and corners, every upper end is below 0.02.
- **Not computed:** no block counts, no block-level statistic and no clustered interval.

## Output
`wp3_elms_effect/src/w3_b1_block_bootstrap.py`; `wp3_elms_effect/results/w3_b1_block_bootstrap.md`, `.json` (aggregates only).

## Record
| Date | Change | Reason |
|---|---|---|
| 2026-11-09 | Registered by public commit before any statistic above was computed | Project lead: start #9 |
