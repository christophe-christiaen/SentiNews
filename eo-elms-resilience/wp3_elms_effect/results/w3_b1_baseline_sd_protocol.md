# W3-B1 protocol: is H1's z-score result a scaling artefact of baseline variability?

**Status: registered 9 November 2026 by public commit, before any statistic below was computed. Exploratory. Adds a label beside H1 and changes none of its registered reading.** Follows [w3_b1_h1h2_checks.md](w3_b1_h1h2_checks.md), which found H1 positive only on the field z-score. Changes after registration go in the record at the end.

## The mechanism being tested
H1's outcome is (July NDVI − field's 2017–2020 mean) ÷ field's 2017–2020 SD, the SD floored at 0.02.
- **The idea:** if July NDVI falls in shock seasons, then a field with a larger baseline SD shows a smaller fall in z-score for the same fall in NDVI.
- **What would follow:** if agreement fields have larger baseline SDs than the fields they're compared with, H1 on z-scores would read as a cushion even with no difference in NDVI.
- **Matching doesn't prevent it:** matching uses each field's 2017–2020 mean half-month NDVI, crop history, flood zone, peat and nearby scheme intensity, but not its variability.

## Three parts
Frozen H1 sample (X2 matched sample), crop strata, 2017–2025; E3 sample reported beside.
1. **Do the groups differ in baseline variability?** Outcome log(field SD of July NDVI, 2017–2020, at least 2 seasons, unfloored, SD of 0 dropped and counted). Difference, agreement minus comparison fields, within ERA5 cell, averaged over cells weighted by agreement fields. Comparison fields: never treated and those entering after 2025. 95% interval clustered by cell. Also the share of each group at the 0.02 floor.
2. **Does NDVI fall in shock seasons?** Among comparison fields only: mean change in raw July NDVI from the base season, shock seasons minus other seasons after 2020, using the estimator's control means. The mechanism needs this to be negative.
3. **Does H1 survive holding baseline variability fixed?** Frozen z-score H1 with strata ERA5 cell × season × crop × tercile of baseline SD. Terciles are cut over all fields in the panel, regardless of treatment; fields with no SD form their own group.

## Label, fixed in advance
- **Scaling artefact supported:** part 1's interval lies above zero, part 2 is negative, and in part 3 H1's interval includes zero or its estimate falls to half or less of +0.082.
- **Not supported:** part 1's interval includes zero or lies below it. Then the z-score result needs another explanation, and none is offered here.
- **Partly supported:** anything else. The parts that hold are stated.

## Limits
- Tercile strata are coarse, so part 3 can only weaken the result, not remove all of the mechanism.
- If the label is "supported", it says why the z-score and other scalings differ. It doesn't say agreements have no effect. The raw and ratio results already speak to that.

## Known before this registration
- **H1 and its scaling check:** H1 +0.082 (+0.049, +0.115), and all results in [w3_b1_h1h2_checks.md](w3_b1_h1h2_checks.md).
- **Floor share, pooled:** 1.4% of all fields' July NDVI SDs are at the 0.02 floor.
- **Not computed:** no split of baseline SD by agreement status.

## Output
`wp3_elms_effect/src/w3_b1_baseline_sd.py`; `wp3_elms_effect/results/w3_b1_baseline_sd.md`, `.json` (aggregates only).

## Record
| Date | Change | Reason |
|---|---|---|
| 2026-11-09 | Registered by public commit before any statistic above was computed | Project lead: register the baseline-variability check |
| 2026-11-09 | **Run** ([w3_b1_baseline_sd.md](w3_b1_baseline_sd.md)). **Scaling artefact supported** on both samples: agreement fields' baseline SD higher by 11% (frozen; log difference +0.105, +0.099 to +0.111) and 6% (E3); comparison fields' July NDVI falls 0.167 in shock seasons; H1 with SD-tercile strata −0.010 (−0.042, +0.021) and +0.021 (−0.012, +0.055). Registered reading unchanged | Registered check |
