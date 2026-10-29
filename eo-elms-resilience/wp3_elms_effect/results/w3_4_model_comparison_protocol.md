# W3-4 model comparison: which embedding sees which option best

**Written 29 October 2026 at 15:37, while the TESSERA and Presto rerun of W3-4 was in progress.** At that time no
results file of the rerun existed; its progress log held 6 of 30 printed rows, which had not been opened. Changes after
this date go in the record at the end.

## Question
The W3-4 rules test whether the selection trap and the negative controls behave the same across models. They do not
say which model detects which option best. This addendum fixes how that comparison is made, before it is seen.

## Design
- **Models:** AlphaEarth (64-d annual), Sentinel-2 indices (36 half-monthly values, March–August), TESSERA (128-d
  annual), Presto (128-d, farm season October–September).
- **Common years for all four,** so the comparison is like for like: pre-entry record = mean of 2018–2019 (TESSERA has
  no 2017); I₀ from 2020 (Presto: season October 2019–September 2020); post = 2025 (Presto: season October 2024–
  September 2025). The AlphaEarth and Sentinel-2 figures here therefore differ slightly from the W3-4 report, which used
  2017–2019; that report stands as published.
- **Metric:** selection-corrected detection I* = [AUC(pre + post) − AUC(pre)] − [AUC(pre + 2020) − AUC(pre)], as in W3-4.
- **Comparison group:** B, management-only scheme land (primary). Six option families: herbal leys, cover crops,
  no-till, in-field flower and bird-food plots, margins and corners, grassland options.
- **Same parcels for every model:** the W3-4 sample (fixed seeds), leave-one-region-out models as in W3-4.
- **Test:** for each family and each of the 6 model pairs (36 tests), the difference in I* with a paired bootstrap
  (1,000 resamples of parcels within held-out regions, the same resample for all models); two-sided bootstrap p =
  2 × the smaller tail share at zero; Holm correction over the 36 tests.

## Reading, fixed in advance
- **Model X is better than model Y for an option** if X's I* exceeds Y's with Holm-adjusted p < 0.05.
- **Best suited:** a model better than each of the other three for that option. Otherwise "no single best", reported
  with the leading group (the top model and any model not significantly below it).
- An option on which no model passes the W3-4 detection rule (I* 95% interval above 0.02) is reported as "not
  detectable by any model"; its model differences are not interpreted.
- **Checks reported, not tested:** the same pairwise differences for the two negative controls against never-treated
  land (expected near zero for every pair); and the AUC with the 2025 record per model and option (how well a single
  field can be classified), descriptively.
- Expectations stated before the result, not used in the rule: Presto may do best on cover crops (winter months);
  TESSERA may do well on no-till (radar sees surface roughness); herbal leys may be seen equally by all.

## Output
`wp3_elms_effect/results/w3_4_model_comparison.md`, `.json`.

## Record
| Date | Change | Reason |
|---|---|---|
| 2026-10-29 | Protocol written (15:37), during the rerun, before any result was read | Question from the project lead: which model suits which option |
