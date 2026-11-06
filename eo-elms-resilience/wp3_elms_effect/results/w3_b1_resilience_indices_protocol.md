# W3-B1 protocol: Lloret-type resilience indices, season-integrated NDVI and a senescence date

**Status: registered 6 November 2026 by public commit, before any statistic below was computed. Exploratory. These add readings beside registered results and change none of them.** Item 8 of the outside review. Changes after registration go in the record at the end.

## Why
H1 and H2 use their own measures: July NDVI anomaly and peak NDVI anomaly. The review asked whether the standard resilience components say the same thing over the whole season, and whether canopy senescence shifts. No new data: half-monthly Sentinel-2 NDVI, March to August.

## Indices
X is season-integrated NDVI: half-months 3–10, linear interpolation across missing half-months, trapezoid sum. Half-month 1 is 1–15 March, so the window is 1 April to 15 August (half-months 3–10 as in the registered integral).
- **Usable X:** at least 5 of the 8 half-months, with one observed in half-months 3–5 and one in 8–10; no extrapolation beyond the first and last observed (held flat). X below 0.4 (mean NDVI under 0.05) is treated as missing. The rule was set from coverage counts alone, because the registered "6 of 8" keeps only 47% of 2023 and 53% of 2024; "6 of 8" is reported beside.
- **N:** the field's mean X over 2017–2020, at least 2 usable seasons. All of these seasons precede the first entry (2021).

Following Lloret, Keeling and Sala (2011, *Oikos* 120(12), 1909–1920), formulas checked in the R package pointRes (`res.comp`), for a season t:

| Index | Here | Lloret term | Contrast, after entry |
|---|---|---|---|
| **Resistance, Rt** | X(t) / N | Dr / PreDr | hazard seasons minus other seasons (as H1) |
| **Resilience, Rs** | X(t) / N | PostDr / PreDr | calm season after a hazard minus calm after calm (as H2) |
| **Recovery, Rc** | X(t) / X(t − 1) | PostDr / Dr | same as Rs |
| **Relative resilience, RRs** | (X(t) − X(t − 1)) / N | (PostDr − Dr) / PreDr | same as Rs |

**Departures from Lloret, stated:** the reference period is the fixed 2017–2020 normal rather than a moving window just before each event, because a moving window would reach into agreement years; "post" is one season, because shocks are too close together for more; the indices were built for tree rings on one species, and here they sit on rotating crops.

**Rc depends on Rt by construction:** a lower X(t − 1) raises X(t) / X(t − 1) with no change in X(t) (Schwarz et al. 2020, *Current Forestry Reports* 6, 185–200, critique these indices). So **a resistance gain can show up as a recovery loss. Rs is the index read for recovery; Rc is reported because it was asked for and is not interpreted alone.**

## Senescence date
- **Definition:** peak as registered (maximum over half-months 4–9). The date is where NDVI crosses 50% of the peak after it, by linear interpolation between the last observed half-month at or above 50% and the first observed below. Both must exist and lie at most 2 half-months apart; otherwise missing.
- **Outcome:** the date minus the field's 2017–2020 mean date (at least 2 usable seasons), in half-months; 1 half-month is about 15 days.
- **Direction:** later is shown as positive. A later date means canopy lasted longer, which isn't by itself more yield: it can also reflect variety, drilling date or disease.
- **Selection check:** whether a date exists at all (0 or 1) goes through the same estimator. Fields not reaching 50% by the end of August, or clouded, drop out. If this row's interval excludes zero and the effect is at least 2 percentage points, senescence rows for that family and hazard are labelled **selected**.

## Estimator and rows
Frozen estimator, E3 matched sample (`matched_sample_e3.parquet`), cell-clustered errors. Hazards as registered: dry or heat (`MAIN_SHOCK`), and wet winter. Families: all agreement land, management-only.
- **Read, 14 rows:** Rt and senescence date × both hazards × both families (8); Rs, Rc, RRs × dry or heat × both families (6).
- **Not read, 6 rows:** Rs, Rc, RRs after wet winters. Wet shocks fall mostly in 2021 and 2024, so the seasons after them are mostly 2022 and 2025, the main dry seasons. "Calm" here means only not wet, and the season shares are printed. A recovery cannot be separated from the next shock.

**Seasons and strata, deciding version:**
- **Rt and senescence:** 2017–2025, strata ERA5 cell × season × CROME crop, as H1.
- **Rs, Rc, RRs:** 2017–2026, strata ERA5 cell × season, because 2025 carries most of the dry-or-heat weight, 2026 is the only season after it, and CROME 2026 doesn't exist. Without 2026, recovery rests mainly on 2023, a low-coverage season.

**Reported beside, not deciding:** the other season-and-strata version (for Rc and RRs, 2017–2025 strata use crop in t × cereal or not in t − 1, because these depend on both seasons' crops); the "6 of 8" X; X2's matched sample without embeddings, given the matching sensitivity of 5 November.

## Reading, fixed in advance
- **Placebo:** entry two seasons early, using only true pre-entry seasons, as in W3-H and Part F; the same contrast on each row. If either side of a placebo contrast is empty, it is "not available".
- **Cushion indicated:** the deciding 95% interval lies above zero and the placebo interval includes zero. **Cost indicated:** the same, below zero. Senescence rows say "later" and "earlier", not cushion or cost. Rc is never labelled by itself.
- **Few shocks:** as W3-B1 section 1: season-clustered interval with t(G − 1), and permutation of shock seasons with 1,999 draws, seed 20261106. For recovery rows both the season and the season before follow the permuted map. A row is **robust to few shocks** only if the season-clustered interval excludes zero and permutation p is below 0.05.
- **Multiple tests:** Holm over the 14 read rows, on cell-clustered p-values, reported beside. No threshold for practical size is set for ratios; intervals are shown as percent of the field's normal for Rt and Rs.
- **No row changes a registered reading.** These are NDVI ratios and not yield, so they can't show an economic gain.

## Correction to be made alongside this analysis
While preparing this protocol, counts showed `senesc_k` in `s2_parcel_year.parquet` uses −1 for "no date" (14–50% of field-seasons by year), and `wp3_did.load()` doesn't exclude it. So the exploratory row **"Secondary outcome: Senescence timing (half-months)", −0.172, in `wp3_results.md` averaged −1 codes as dates and is wrong**, including in its baseline. No other analysis uses this variable. Found by a count of codes and not by any new estimate. **Fix:** treat −1 as missing in `load()`; rerun that row alone, on its registered sample, strata and discrete definition; put the corrected value beside the old one in `wp3_results.md` and in the record. The rest of `wp3_results.md` is unaffected.

## Known before this registration
All registered results and their placebos. In particular: H1, H2 (+0.035, interval includes zero); exploratory seasonal integral z-score +0.120 (+0.049, +0.191) on X2's sample; 2025 carries 83–87% of dry-or-heat weight and 2024 85–92% of wet; dropping those seasons removes the harvest contrasts; matching sensitivity. Coverage by year was counted without splitting by agreement. So Rt on X is not blind: it is close to a rescaled version of the known integral row.

## Output
`wp3_elms_effect/src/w3_b1_resilience_indices.py`; `wp3_elms_effect/results/w3_b1_resilience_indices.md`, `.json` (aggregates only).

## Record
| Date | Change | Reason |
|---|---|---|
| 2026-11-06 | Registered by public commit before any statistic above was computed | Project lead: start #8 while E3b runs |
| 2026-11-06 | **Run** ([w3_b1_resilience_indices.md](w3_b1_resilience_indices.md)). No season-long cushion shown. Rt dry or heat +0.29% of normal all land, interval includes zero; management-only +0.61%, labelled cushion indicated, not robust to few shocks. Senescence date: none. Rs management-only +1.27 (+0.54, +1.99) meets its labels but isn't readable as recovery, see next row. **Implementation:** the first run stopped before any estimate on fields with a non-positive peak NDVI; these now count as no date. **Departure from the reasoning here:** 2026 carries about 1.5% of recovery weight, being mostly a shock season, so the reason given for including it did not hold and the 2025 shock's recovery isn't measured. **Correction made:** senescence row of `wp3_results.md`, −0.172 (old coding reproduced) to −0.012 (−0.034, +0.011); `wp3_did.load()` fixed; registered readings unchanged | Registered checks |
| 2026-11-06 | **Post-hoc, specified after seeing the results, on Rs after dry or heat** ([`src/w3_b1_resilience_posthoc.py`](../src/w3_b1_resilience_posthoc.py), [json](w3_b1_resilience_posthoc.json)): season weights on both sides, wet-shock share, leave one season out. Calm-after-calm is 91% season 2024 on management-only land, and 92% of that side lies in wet-shock cells against 38% on the other. Without 2024 +0.65 (−1.06, +2.37); without wet-shock cells +0.43 (−1.35, +2.20). The labels stand as registered, and the row is reported as not readable as recovery. Frozen H2 uses the same contrast on its own sample; whether it shares this weighting hasn't been checked | Only row labelled cushion and robust |
