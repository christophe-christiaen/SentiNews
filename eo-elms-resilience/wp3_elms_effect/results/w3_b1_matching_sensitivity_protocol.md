# W3-B1 matching sensitivity protocol: how strong would an unobserved factor have to be?

**Status: registered 5 November 2026 by public commit, before any statistic below was computed. Exploratory checks on registered results. They add labels
beside those results and change none of their readings.** Item 7 of the outside review's Block 1. Changes after registration go in the record at the end.

## Why, and why not the standard tool
The review suggested Cinelli and Hazlett (2020, *JRSS B* 82(1), 39–67). Its robustness value is derived for a linear regression with one treatment coefficient, and its benchmarks use
partial R² from that regression. This estimator is a weighted triple difference of group-time means with cell-clustered errors, so the formula doesn't carry over: any robustness value here would
rest on an assumed degrees of freedom and have no benchmarks. **So it isn't used.** The two checks below keep its logic: size the confounder needed, then compare it with the observed ones.

## What a confounder has to do here
Because the estimate is a contrast of shock and other seasons, a fixed difference between fields cancels. A confounder U must be **imbalanced** between agreement and comparison fields, and must
change **how fields respond to the shock**. Bias ≈ δ × γ, with δ the difference in U in SD units and γ the difference in U's slope on the outcome between shock and other seasons. The formula assumes a linear slope, and one U.

## Results examined
With their registered point estimates, strata and hazard definitions, as W3-B1 section 1:
- **A:** H1 July NDVI, frozen sample, frozen matching covariates. Crop strata.
- **B:** H1 July NDVI, E3 sample. Crop strata.
- **C:** dry or heat harvest: all agreement land, management-only. E3 sample.
- **D:** wet-winter harvest: all agreement land, management-only, buffer strips. E3 sample.

E (wet-winter July NDVI) isn't examined: its estimates aren't distinguished from zero, so there's nothing to overturn.

## Check 1: leave one covariate group out (uses the real estimator)
Repeat the frozen matching (`wp3_did.match`) with one group removed, then the estimate above on that sample. The groups:
1. pre-entry NDVI trajectory, including missingness flags;
2. crop history: cereal and crop sequence 2016–2020;
3. flood zone;
4. peat class;
5. scheme intensity within 1 km;
6. embedding components (E3 sample only, so B, C and D).

Also **no matching at all**, for scale; it isn't a group and doesn't enter the ratio. **First, the baseline matching must reproduce the saved samples exactly, or the run stops and goes in the record.**

**Reported:** the shift for each group. S is the largest absolute shift. **k1 = |estimate| ÷ S:** how many times more influential than the most influential observed group an unobserved factor must be to take the estimate to zero.
Re-matching also changes which fields are in the sample, so each shift includes some noise, which makes k1 lean low.

## Check 2: the δ × γ bound
For every matching covariate, standardised by its SD in the sample:
- **δ:** the agreement-minus-comparison standardised difference before matching, using all parcels, for the result's family. This is the imbalance a factor like this has when nothing has been matched on.
- **γ:** in never-treated fields of the matched sample, seasons 2021–2025, the same outcome and hazard map: demean outcome and covariate within the result's strata, take the slope in shock seasons minus the slope in other seasons. Never-treated only, so agreements can't affect it.
- **b = |δ × γ|** for each covariate. **k2 = |estimate| ÷ max b.**

**Reported:** the covariates with the largest δ, |γ| and b; k2; γ needed to reach zero at the largest δ; δ needed at the largest |γ|. Results that use the 0.10 t/ha or 0.10 SD limit also report the bias needed to push the estimate past it, limit − |estimate|, against both S and max b.

**Marginal slopes.** Covariates are correlated, so these aren't separate effects and shouldn't be added.

## Labels, fixed in advance
With k = the smaller of k1 and k2:
- **k below 1, fragile:** a factor no stronger than one already observed could remove the result.
- **k from 1 to 3, moderate.**
- **k of 3 or more, strong:** it would take a factor at least three times the strongest observed.

**A label is about strength against one unobserved factor, nothing more. "Strong" can't clear a failed placebo:** a failed placebo already shows differences of about the needed size between these fields. The placebo is shown beside each label and the reading goes with the placebo. The few-shocks spread and HonestDiD are separate and aren't included.

## Check on the method
**The embeddings as a test case.** They were unobserved in the frozen match: A's sample has imbalance on them, and adding them gave B. Using A's sample: predicted shift = sum over the 10 components of δ (after matching, in A's sample) × γ, against the realised change from A to B. Reported only; it has one data point and no pass mark.

## Known before this registration
All estimates and placebos in W3-B1; the frozen match's balance; embedding imbalance (0.33 in A's sample, 0.05 after); H1 moved +0.082 to +0.087 with embeddings; and the wet-winter harvest moved from −0.062 on all observable parcels to −0.040 on the E3 sample, −0.093 to −0.068 for buffer strips. So the effect of matching on some of these rows is already known. No covariate-level slope or group-removal result has been computed.

## Output
`wp3_elms_effect/src/w3_b1_matching_sensitivity.py`; `wp3_elms_effect/results/w3_b1_matching_sensitivity.md`, `.json` (aggregates only).

## Record
| Date | Change | Reason |
|---|---|---|
| 2026-11-05 | Registered by public commit before any statistic was computed | Project lead: start the matching sensitivity |
| 2026-11-05 | **Statement corrected after the run; no analysis change.** "Known" above says wet-winter harvest moved from −0.062 on all observable parcels to −0.040 on the E3 sample, and implies this was the effect of matching. −0.062 and −0.093 are on the GFM-observable subset, a different frame, so they say nothing about matching. Report writer added to the script after the run; numbers unchanged | Error in the protocol's wording |
| 2026-11-05 | **Run** ([w3_b1_matching_sensitivity.md](w3_b1_matching_sensitivity.md)). Both saved samples and all estimates reproduced. **Harvest depends on the embeddings:** without them dry-or-heat harvest goes +0.039 to −0.001 (all land), +0.041 to 0.000 (management-only); wet −0.040 to −0.013. **Labels:** dry-or-heat harvest fragile, k 0.97 and 0.998; wet all land and management-only moderate, 1.47 and 1.65; wet buffer strips strong, 3.60; H1 strong, 4.72 and 3.17. Strong can't clear the failed placebos on H1 and wet buffer strips. Embedding test: predicted −0.001, realised +0.004. Registered readings unchanged | Registered checks |
