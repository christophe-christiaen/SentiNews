# W2-4 protocol: a closed form for the short-baseline artefact

**Written 18 October 2026, before the Monte Carlo check below was run.** Changes after this date go in the record.

## Claim
Fields with no season-to-season carry-over, y_it = a_i + c_cell,t + e_it with e iid normal, are scored as
z_it = (y_it − mean of the first n seasons) / (their SD, ddof = 1), over T seasons, and the legacy test regresses
z_t on z_t−1 pooled over fields within cell × season. Ignoring the interaction between cell shocks and each field's
scale, the expected pooled coefficient is

β(n, T) = [ (T − n − 1)·K_n − (n − 1) ] / [ n(n − 1) + (T − n − 1)(n + 1)·K_n ],   K_n = E[1/s²] = (n − 1)/(n − 3)

from three kinds of pair: (i) both seasons in the baseline (n − 1 pairs): the deviations sum to zero, so
E[z_j z_k] = −1/n and E[z_j²] = (n − 1)/n exactly, whatever the scale; (ii) the pair across the baseline edge: zero
covariance; (iii) both seasons after the baseline (T − n − 1 pairs): they share the error of the baseline mean,
covariance K/n and variance K(n + 1)/n, the sample mean being independent of the sample SD for normal errors.
Special cases: with the scale known or not estimated, K = 1 and β = (T − 2n)/[n(n − 1) + (T − n − 1)(n + 1)];
with only post-baseline pairs, β = 1/(n + 1) (the earlier approximation). β = 0 when T = 2n − 2. For n ≤ 3, K is
infinite: the pooled estimate is dominated by the fields with the smallest baseline SD and has no stable value
(it tends to 1/(n + 1) only as a ratio of expectations); for n = 4, 5 its variance is infinite (E[1/s⁴] diverges), so
single runs are noisy and medians are the fair comparison.

## Check, fixed in advance
Monte Carlo of the WP2 design (40,000 fields, 400 cells, cell shocks SD 0.8, field effects SD 1), 200 replications
per setting, for n = 2, 3, 4, 5, 6, 8, 10, 15 and T = 10 (the Sentinel-2 panel) and T = max(10, n + 6) (the earlier
simulation); plus versions with no cell shocks, with the true SD instead of the estimated one, and with the mean
removed but no scaling.
- **Accepted** for n ≥ 6 if the formula lies within 2 Monte Carlo standard errors of the mean of the replications in
  every setting without cell shocks, and within 0.02 of it with cell shocks (the neglected interaction).
- For n = 4, 5 the comparison is with the median and reported, not used for acceptance (infinite variance).
- For n ≤ 3 the spread across replications is reported, to show the estimate has no stable value.
- The known-SD and mean-only versions must match K = 1 within 2 Monte Carlo standard errors for every n ≥ 2.

## Output
`wp2_resilience/results/w2_4_closed_form.md`, `.json`; figure `results/maps/wp2_closed_form.png`.

## Record
| Date | Change | Reason |
|---|---|---|
| 2026-10-18 | Protocol written | Before the Monte Carlo |
| 2026-10-18 | Run ([w2_4_closed_form.md](w2_4_closed_form.md)): 24 of 26 checks passed. The two failures are n = 8 without cell shocks (formula −0.082 vs Monte Carlo −0.081; 0.000 vs −0.0003): gaps of about 0.001, beyond 2 Monte Carlo SE (≈ 0.0002) because the formula is a ratio of expectations and the estimator a ratio of sums with heavy-tailed weights. Reported as failures; the rule is not changed. The unscaled version matches K = 1 in every case; n = 4 and 5 (medians) are within 0.004 | Result |
