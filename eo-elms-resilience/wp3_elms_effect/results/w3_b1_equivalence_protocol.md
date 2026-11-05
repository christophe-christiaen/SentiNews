# W3-B1 equivalence protocol: can we rule out an effect of a useful size?

**Status: registered 5 November 2026 by public commit, before the shuffled-season spread or any equivalence result below was computed.
Exploratory checks on registered results. They add labels beside those results and change none of their readings.** Item 4 of the outside
review's Block 1. Changes after registration go in the record at the end.

## Why
"Not shown" isn't "ruled out". Equivalence tests (two one-sided tests, TOST) ask whether an effect is demonstrably smaller than a chosen size.

## Limits, chosen by the project lead on 5 November 2026
- **Harvest index: 0.10 t/ha** (about £20/ha at £204/t feed wheat, revenue only). Anchor: the W3-H protocol's prior expectation of about 0.1 t/ha for wheat in droughts, written on 30 October before any harvest estimate; W3-T used the same limit.
- **July NDVI: 0.10 SD.** Anchor: W3-T's limit, written before W3-T's estimates. It is about the size of H1, so it isn't independent of that result.

**The choice was made after the estimates were public,** which is why anchors written earlier were preferred to any number fitted now.

## Results tested
The nine in W3-B1 section 1, with their registered point estimates, samples and strata: A and B (H1 July NDVI); C (dry or heat harvest: all agreement land, management-only);
D (wet-winter harvest: all agreement land, management-only, buffer strips); E (wet-winter July NDVI: all agreement land, buffer strips). Not tested: establishment, which has no limit
fixed independently of results, and recovery, whose intervals are too wide.

## The test: it must pass twice
With δ the limit and θ̂ the estimate, each part forms a 90% interval, the equivalent of two one-sided 5% tests.
1. **Cell errors:** θ̂ ± 1.645 × the cell-clustered SE (W3-B1 section 1, method 1).
2. **Shuffled-season spread:** the draws of W3-B1 section 1, method 7, reproduced exactly (same order of results, same seed 20261105, 1,999 draws) and saved this time. With D the draws minus their mean: θ̂ + q05(D) to θ̂ + q95(D). Empirical quantiles, numpy's default linear rule.

**Part passes** if its 90% interval lies strictly inside (−δ, +δ). **A result is "within the limit" only if both parts pass.** Otherwise: **"can't rule out an effect of this size".**

**Smallest effect ruled out:** for each part, the larger absolute endpoint of its interval. The headline X for a result is the larger of the two parts.

**Check before reading:** the script must reproduce the published estimate to 1e-9 and the published permutation p exactly; if not, the run stops and goes in the record.

## Readings beside X, harvest only
- **Share of a bad season's loss:** X ÷ 0.85 t/ha, the mean of Defra's England wheat shortfalls in 2025, 2024 and 2020 (−0.71, −0.77, −1.08).
- **Share of the no-till payment if annualised:** X × £204 × shock frequency ÷ £73/ha/year (SOH1, GOV.UK), frequencies dry or hot 47%, wet 30%. A reading only: only some of this land is no-till, and payments also fund environmental outcomes, so this is no verdict on value for money.

## Limits of the test, stated in advance
- **Equivalence doesn't remove bias.** The test measures noise around the estimate; it says nothing about the trends that fail placebos. Each result's placebo status from its registered run is shown beside it. A "within the limit" with a failed placebo reads "within the limit in a design that failed its placebo", not "no effect".
- **HonestDiD sensitivity (W3-B1 section 2) isn't included in either part,** and a post-entry violation a quarter of the largest pre-entry one already overturns the averages.
- **Few distinct shock patterns.** Part 2 reshuffles nine seasons (2017–2025; ten for E), and effects stay fixed, so seasons with unusual effects drive its spread. That is the point, but the quantiles are coarse.
- **No multiplicity adjustment** over the nine rows. Adjusting would widen intervals and make passing harder; none is applied because these are labels on exploratory checks, and the reader should bear that in mind for any single pass.

## Known before this registration
All estimates, cell SEs, permutation p values, season shares and leave-one-season-out results in [w3_b1_inference.md](w3_b1_inference.md). The smallest limits that part 1 could pass at for C and D (0.060, 0.066, 0.060, 0.074, 0.093 t/ha) were computed in drafting the options, so part 1 passes on those rows are expected. **The published p values also constrain the spread:** a p of 0.28–0.32 on an estimate of ±0.04 implies wide draws, so part 2 isn't blind, though its value at these quantiles hasn't been computed.

## Output
`wp3_elms_effect/src/w3_b1_equivalence.py`; `wp3_elms_effect/results/w3_b1_equivalence.md`, `.json`, `w3_b1_equivalence_draws.json` (aggregates only).

## Record
| Date | Change | Reason |
|---|---|---|
| 2026-11-05 | Registered by public commit before the shuffled-season spread or any equivalence result was computed. Limits and two-part rule chosen by the project lead from the drafted options (option A) | Project lead: option A with the two-part test |
