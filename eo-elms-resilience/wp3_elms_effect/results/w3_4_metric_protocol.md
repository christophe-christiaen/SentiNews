# W3-4 protocol: a placebo-adjusted detection metric

**Written 18 October 2026, before any model below was fitted.** Builds on [detection_protocol.md](detection_protocol.md)
(families, comparisons, sample, model and leave-one-region-out evaluation unchanged). Changes after this date go in the
record at the end.

## Question
Paper 3 measured detection as the AUC with the 2025 record minus the AUC with the 2017–2019 record (the "gain").
Can this be made a defined metric, with stated assumptions, uncertainty and a built-in check that it gives no
detection where none is possible, and does it give the same answer whichever comparison group is used?

## Definitions (per option family, comparison and feature family)
- **AUC_pre:** the model on the pre-entry record (2017–2019 mean). Measures selection: which land joins.
- **AUC_post:** the model on the 2025 record.
- **G (gain, as in Paper 3) = AUC_post − AUC_pre.**
- **I (incremental detection, primary) = AUC_pre+post − AUC_pre:** what the 2025 record adds to a model that already
  knows the pre-entry record.
- **I₀ (placebo increment) = AUC_pre+2020 − AUC_pre:** the same with the 2020 record, which is also before every entry
  (entry years 2021–2024). It measures what any extra year adds when no option is present: extra features, and drift
  in the joining land's traits.
- **I* (selection-corrected detection) = I − I₀.**
- Secondary: the AUC of a model on the change (2025 minus pre-entry mean).

**Feature families:** (1) AlphaEarth annual embeddings (64 dimensions); (2) Sentinel-2 half-monthly NDVI, NDRE and NDMI
medians, March–August (36 values; pre-entry = mean of 2017–2019, 2020 and 2025 as single years). TESSERA is not
included: it is not yet extracted for the national parcels (task W3-T).

## Assumptions under which I* measures detectability
(A1) No anticipation: the 2017–2020 records are unaffected by options entered from 2021. (A2) Any change in the
joining land's traits between 2020 and 2025 that is unrelated to the option is no larger than between 2017–2019 and
2020 (I₀ captures drift and the cost of extra features over one interval). (A3) Same model class and feature
dimension in the two increments. (A2) is the strong one; the negative controls test it.

## Uncertainty
95% intervals by bootstrap of parcels within held-out regions (500 resamples of the pooled held-out predictions),
for each AUC and each difference; plus the range across held-out regions.

## Reading, fixed in advance
- **Calibration:** the metric is valid for a feature family if I* is within ±0.02 of zero for both negative controls
  (buffer strips; management-only) against never-treated land. If not, the metric is reported as failing calibration
  for that feature family.
- **Detectable beyond selection:** a family whose I* has a 95% interval entirely above 0.02 against comparison B
  (management-only scheme land).
- **Selection-invariance:** for each family, |I*(A) − I*(B)| (never-treated vs management-only comparison) is compared
  with |AUC_post(A) − AUC_post(B)|; the metric is called selection-invariant if the first is below 0.03 for every
  non-control family while the second is not.
- Verdicts are set beside Paper 3's rule (AUC_post ≥ 0.70 and G ≥ 0.10 against comparison B).

## Output
`wp3_elms_effect/results/w3_4_metric.md`, `.json`.

## Record
| Date | Change | Reason |
|---|---|---|
| 2026-10-18 | Protocol written | Before any model |
| 2026-10-18 | Run ([w3_4_metric.md](w3_4_metric.md)): calibration valid for both feature families; five families detectable beyond selection (herbal leys, cover crops, no-till, in-field plots, grassland options), margins and corners not; selection-invariant for Sentinel-2, not for AlphaEarth (herbal leys 0.031 against the 0.03 limit) | Result |
| 2026-10-18 | **Addendum, before any TESSERA or Presto value for the national parcels was extracted:** the same metric, families, comparisons, sample, model, rules and bootstrap, rerun with two further feature families. **TESSERA v1.1** (128-d annual; 2017 is missing in the store, so pre = mean of 2018–2019; I₀ year 2020; post 2025). **Presto** (pretrained, MIT; 128-d encoder output from 12 monthly steps of Sentinel-1, Sentinel-2, ERA5-Land and SRTM; farm seasons October–September so winter cover is inside one season; pre = mean of seasons 2018–2019; I₀ season 2020 (October 2019–September 2020, before every entry); post season 2025). The AlphaEarth and Sentinel-2 results stay as reported; the new families are reported beside them, with the different pre-entry years stated | National runs approved |
| 2026-10-29 | Second addendum, [w3_4_model_comparison_protocol.md](w3_4_model_comparison_protocol.md), written during the TESSERA/Presto rerun before any of its results were read: which model detects which option best (paired bootstrap of I* differences on common 2018–2019 pre-entry years, Holm over 36 tests) | The W3-4 rules compare behaviour across models, not which model suits which option |
| 2026-10-29 | Presentation only: the Sentinel-2 indices are labelled as the no-AI baseline, separate from the AI embeddings, in all reports, papers and decks; results unchanged | Clarity (project lead) |
