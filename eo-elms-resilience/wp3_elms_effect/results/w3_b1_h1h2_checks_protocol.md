# W3-B1 protocol: does H2 lean on wet seasons, and does H1 depend on its z-score scaling?

**Status: registered 9 November 2026 by public commit, before any statistic below was computed. Exploratory checks on the frozen confirmatory tests. They add labels beside H1 and H2 and change none of their registered readings.** Both checks were raised by the resilience indices of 6 November ([w3_b1_resilience_indices.md](w3_b1_resilience_indices.md)). Changes after registration go in the record at the end.

## Check 1: what H2's comparison seasons are
**Why:** in the resilience indices, the calm-after-calm side of the recovery contrast was 91% season 2024 on management-only land, and 92% of that side lay in wet-shock cells. Agreement land does worse in wet seasons, so that side would sit low for reasons unrelated to recovery. Frozen H2 uses the same contrast (calm after a dry or heat shock minus calm after calm), on peak NDVI z-score, X2's matched sample, crop strata, 2017–2025.

**Run on frozen H2 exactly as registered,** reproducing +0.035 first:
- Season weights on both sides; share of each side in wet-shock cells; each season's mean effect.
- Leave one season out.
- Wet-shock cells removed from both sides.
- The same on the E3 matched sample, reported beside.

**Labels, fixed in advance:**
- **Comparison side dominated by wet seasons** if at least 50% of the calm-after-calm weight lies in wet-shock cells.
- **H2 depends on wet seasons** if removing wet-shock cells from both sides moves the estimate by more than its cell-clustered SE (0.024), or changes whether its 95% interval includes zero.
- H2 already isn't significant; these labels say whether its null result compares like with like. The registered reading stands either way.

## Check 2: H1 under other scalings
**Why:** H1's outcome is a field z-score, (value − field's 2017–2020 mean) / field's 2017–2020 SD, the SD floored at 0.02. The SD comes from 2–4 seasons, so fields that happened to be steady get large z values. The resilience-index ratio of the seasonal integral was +0.18% of normal (−0.14, +0.51) on X2's sample, while its z-score was +0.120 SD (+0.049, +0.191). So the scaling may matter.

**Run on frozen H1 exactly as registered** (July NDVI, X2 sample, crop strata, 2017–2025), reproducing +0.082 first, then with the outcome replaced by:
1. **Raw July NDVI** (units of NDVI). The difference-in-differences removes the field's level.
2. **Ratio** to the field's 2017–2020 mean, ×100.
3. **Pooled-SD z-score:** field's own mean, but the SD is the median of the 2017–2020 field SDs among all fields in the same ERA5 cell, so one field's steadiness doesn't set its scale.
4. **Frozen z-score, values beyond ±5 set to ±5.**

The same four, plus the frozen z-score, on the seasonal integral (the registered `integral`), reported beside, to reconcile the 6 November discrepancy. Result B (E3 sample) reported beside under the same four.

**Diagnostics, pooled over all fields and not split by agreement:** share of field SDs at the floor; share of July z-scores beyond ±5 by season.

**Labels, fixed in advance:**
- **H1 depends on scaling** if under any of 1–4 the 95% interval includes zero or the sign changes.
- Otherwise **H1 holds across scalings.**
- Sizes on different scales aren't compared directly. Each is also given as estimate ÷ SE.

## Limits
- Both checks reuse the frozen estimator and samples, so the problems already known stay: failed placebos for H1, the few-shocks result, trends and matching sensitivity.
- Check 1 can't fix H2's design; at most it says what H2 compared.

## Known before this registration
- **H1 and H2:** H1 +0.082 (+0.049, +0.115) and H2 +0.035 (−0.012, +0.081), with their components; all W3-B1 results.
- **Resilience indices and post-hoc:** that post-hoc check was on the E3 sample, 2017–2026, without crop strata, on the integral ratio.
- **Not yet seen:** no season weights for frozen H2, and no rescaled H1, have been computed.

## Output
`wp3_elms_effect/src/w3_b1_h1h2_checks.py`; `wp3_elms_effect/results/w3_b1_h1h2_checks.md`, `.json` (aggregates only).

## Record
| Date | Change | Reason |
|---|---|---|
| 2026-11-09 | Registered by public commit before any statistic above was computed | Project lead: register the two H1/H2 checks |
| 2026-11-09 | **Run** ([w3_b1_h1h2_checks.md](w3_b1_h1h2_checks.md)). Reproduced H1 +0.082 and H2 +0.035. **H2:** comparison side 93% season 2024, 94% in wet-shock cells; without wet cells −0.028 (−0.164, +0.109): dominated by wet seasons, depends on wet seasons. **H1 depends on scaling:** frozen sample raw −0.0014 (−0.0044, +0.0016), ratio −0.68% (−1.34, −0.03), pooled-SD z −0.011 (−0.029, +0.006); capped z +0.074 (+0.050, +0.099). E3 sample alike. Registered readings unchanged | Registered checks |
