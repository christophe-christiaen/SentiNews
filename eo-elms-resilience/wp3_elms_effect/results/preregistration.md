# WP3 pre-registration: do agri-environment agreements buffer cereal land against weather shocks?

**Status: FROZEN on 11 October 2026**, before any Sentinel-2 or MODIS outcome had been compared between agreement and
non-agreement land. The frozen version is the git commit recorded at the end of this file (repository
christophe-christiaen/SentiNews); every later change goes in the decisions record with date and reason.

## 1. What has and has not been looked at

Seen before writing this plan:
- Counts of parcels by scheme group, entry year, flood zone and peat class (no outcomes).
- ERA5-Land weather by year, nationally and by cell (exposure only, not crop response).
- Sentinel-2 for one test tile (30UXD, 2022), **pooled over all cereal parcels, not split by scheme group**; and
  Earth Engine output checks (coverage, value ranges) on a few squares, again not split by group.
- Pilot results at 50 MODIS sites (site-level CS share showed no link to drought response).
- After the first draft, before freezing: the national Sentinel-2 panel (381,400 cereal parcels, 2017–2026) and the
  WP2 resilience analysis on it (stress, shocks, recovery, typology, regional summaries), **pooled over all parcels and
  never split by agreement status**; the Sentinel-1 waterlogging test on one tile (pooled; split only by flood zone);
  company accounts and drought news linked to weather (not split by agreement status).

Not seen: any Sentinel-2 or MODIS outcome by agreement status at parcel level.

## 2. Question and hypotheses

Does land under an area-based Countryside Stewardship (CS) or Sustainable Farming Incentive (SFI) option respond
differently to weather shocks than comparable cereal land outside any agreement?

- **H1 (resistance):** in shock seasons, agreement parcels show a smaller drop in crop condition than matched
  non-agreement parcels.
- **H2 (recovery):** in the season after a shock, agreement parcels return closer to their own normal.
- **H3 (type of action):** the buffering effect in H1 is larger for parcels with land-use change options (herbal leys,
  grassland, buffers, wildflower and winter bird food; family B in section 4) than for parcels with management options
  only (soil, nutrient and pest management; family A).

All three are two-sided tests; the expected sign is positive (buffering), but a negative effect (agreements on more
fragile land, or yield-reducing options) is equally reportable.

## 3. Units and sample

- **Unit:** RPA land parcel (parcel point), England.
- **Population:** cereal land = cereal in at least half of the CROME years 2016–2025 (381,400 parcels).
- **Excluded before analysis:** parcels with only per-metre / per-item options or SFI actions snapped from > 50 m
  ("uncertain"); parcels with only legacy ES options; parcels inside legacy Countryside Stewardship Scheme agreements
  (ended 2014); agreement parcels entering before 2021 (658; too few for their own cohort).
- **Analysis sample:** 247,441 agreement parcels entering 2021–2026, and 89,690 cereal parcels never in any scheme
  record (never-treated). Not-yet-treated parcels also serve as controls (section 5).

## 4. Treatment

- **Entry year E:** earliest start of an area-based CS or SFI option on the parcel (from the live scheme layers,
  downloaded October 2026). A parcel counts as treated from the **first full growing season** under the agreement:
  season E if the contract starts on or before 1 March of year E, otherwise season E+1.
- **Cohorts:** 2021 (10,716), 2022 (23,824), 2023 (24,736), 2024 (141,580), 2025 (35,694), 2026 (10,891).
- **Option families** (for H3 and heterogeneity): **A, management** = SFI soil, nutrient and pest management (SAM1,
  SAM2, NUM, IPM, CSAM1, CSAM2, CIPM, PRF); **B, land-use change on the parcel** = herbal leys, grassland, buffers,
  wildflower and winter bird food (SAM3, CSAM3, LIG, CLIG, AHL, CAHL, CS AB / GS / SW options); C = CS other.
  A parcel belongs to B if any area-based option on it is in B, otherwise to A if any is in A, otherwise to C.
  H3 compares the H1 effect for B against A (C is reported but not tested).

## 5. Shocks (defined from weather only, never from the crop)

ERA5-Land, 0.1° cells, normal = 1991–2020. For each cell and season:
- **Dry shock:** March–July rainfall at least 20% below normal, **or** June–July root-zone soil moisture (ERA5-Land layer 2,
  7–28 cm) at least 1 SD below its 1991–2020 mean. (About 1 cell-year in 6 under the 1991–2020 climate.)
- **Severe dry shock:** March–July rainfall at least 30% below normal, or June–July soil moisture at least 1.5 SD below.
- **Heat shock:** 5 or more days at or above 28 °C in June–August.
- **Wet shock:** October–March rainfall at least 30% above normal (waterlogging; secondary, see section 9).

The shock indicator varies by cell and year, so the design uses local exposure, not national averages.

## 6. Outcomes (Sentinel-2, half-monthly medians per parcel, March–August, 2017–2026)

Each outcome is standardised against the parcel's own **pre-entry** years (2017–2020 for every parcel, so the same
baseline window applies to treated and control parcels):
- **Primary, H1:** July NDVI anomaly (mean of half-months 9–10, 1–31 July) in the shock season.
- **Primary, H2:** peak-season NDVI anomaly (maximum over half-months 4–9, mid-April to mid-July) in the season after
  a shock, **only when that following season is not itself a shock season for the parcel's cell**. Back-to-back shocks
  (e.g. 2025 then 2026) are excluded from H2 and reported as compound shocks in the exploratory analyses.
- **Secondary:** July NDMI anomaly (canopy water); July NDRE anomaly (chlorophyll); senescence timing (first
  half-month after the peak with NDVI below 50% of the peak); seasonal integral (sum of NDVI, half-months 3–10).

A parcel-season is missing for an outcome if it has no clear observation in the half-months that outcome uses.
No imputation for the primary outcomes.

## 7. Estimation

- **Main estimator:** staggered-adoption difference-in-differences with heterogeneity-robust estimation
  (Callaway–Sant'Anna group-time effects, never-treated and not-yet-treated controls), with the outcome's shock-season
  response as the dependent variable. Effects are aggregated by event time (−4 to +3) and overall.
- **Equivalent regression form (for presentation):**
  Y_it = α_i + λ_{cell×year} + β·D_it + γ·(D_it × Shock_ct) + ε_it,
  where D_it = 1 once the parcel is under its first full season of agreement; γ is the buffering effect (H1).
  Cell × year effects absorb all common local weather; γ is identified from treated vs untreated parcels facing the
  same shock in the same cell.
- **Crop rotation (main specification):** effects are absorbed within **cell × season × crop** (CROME crop of that
  season), so parcels are compared only with parcels growing the same crop in the same weather cell and season. CROME
  covers 2016–2025, so the main specification uses seasons 2017–2025. The 2026 season (no CROME yet) is analysed in a
  pre-specified secondary version with cell × season effects only, reported alongside, and the main specification is
  re-run when CROME 2026 is published.
- **Matching (before estimation):** each treated parcel is matched (nearest neighbour on a propensity score, then
  checked for balance) to untreated parcels in the same ITL1 region on: the pre-entry Sentinel-2 trajectory
  (2017–2020 half-monthly NDVI means), cereal share and crop sequence in CROME 2016–2020, flood zone, peat class, and
  scheme intensity within 1 km. Balance target: standardised mean differences below 0.1. Embeddings (AlphaEarth,
  pre-entry year) are added as a robustness version of the matching.
- **Inference:** standard errors clustered by ERA5 cell (about 9 km), the level at which shocks vary; spatial block
  bootstrap (50 km blocks) as a check.
- **Multiple testing:** H1, H2 and H3 are the three confirmatory tests, Holm-adjusted at 5%. Everything else is exploratory
  and labelled as such.

## 8. Checks decided in advance

1. **Pre-trends:** event-time coefficients for −4 to −1 jointly near zero; if not, report and use the matched sample
   with trend adjustment.
2. **Placebo entry:** assign each cohort a fake entry two seasons earlier; the effect should vanish.
3. **Synthetic effect:** inject a known +0.2 SD shock-season effect into a random set of control parcels and recover it.
4. **Data quality:** results excluding 2017 (thin Sentinel-2 coverage) and with CROME 2020 left out of the cereal-land
   definition (2020 classification doubtful).
5. **Shock thresholds:** dry shock rainfall at −15% / −25% / −30% and soil moisture at −0.75 / −1.25 SD; rainfall-only and soil-moisture-only versions; heat shock at 3 / 5 / 8 days.
6. **Spatial scale:** repeat on 5 km hexagon averages to check the parcel-point result is not a footprint artefact.
7. **Flood and peat:** repeat excluding parcels in Flood Zone 3 or on deep peat (agreement land is slightly less exposed
   to both: Flood Zone 3 11.0% vs 13.3%, deep peat 3.2% vs 4.3%).

## 9. Heterogeneity and secondary analyses (exploratory)

By option family C and finer option codes; by entry cohort; by region (ITL1); on flood zone 3 or deep peat vs elsewhere; wet shocks
(waterlogging) once Sentinel-1 is added. Business-level analysis (Companies House farms confirmed by payments) is a
separate, smaller descriptive check.

## 10. Known limitations, stated in advance

- Scheme layers are live snapshots: agreements that ended before October 2026 are not visible, so some "never-entered"
  parcels may have had earlier agreements. The CAP 2020/21 payment data suggest this is rare among matched companies.
- Entry is chosen by farmers, so selection on unobservables remains possible; the pre-trend test and matching on
  pre-entry trajectories are the main protections.
- SFI actions carry no parcel reference and are snapped to the nearest parcel point (93% within 50 m).
- Parcel points sample the parcel centre (15 m buffer), not the whole field.

## 11. Decisions record

| Date | Change | Reason |
|---|---|---|
| 2026-10-11 | Draft written | Before any group comparison of outcomes |
| 2026-10-11 | Dry shock widened to include June–July soil moisture | The rainfall-only rule flagged 9% of cells in 2018, a known summer drought; soil moisture flags 93%. Decided from weather data only, before any outcome comparison |
| 2026-10-11 | Review before freezing: (1) section 1 lists the pooled national analyses run since the draft; (2) H2 only when the following season is not a shock; (3) crop rotation absorbed within cell × season × crop in the main specification, 2026 in a secondary version; (4) H3 (land-use change vs management actions) made confirmatory, Holm over three tests; (5) check excluding Flood Zone 3 and deep peat | Agreed with the project lead after section-by-section review; no outcome by agreement status had been seen |
| 2026-10-11 | Implementation readings of the frozen text, fixed before any estimate was computed: (a) "shock" in H1 and H3 = dry shock or heat shock (wet shock stays secondary); (b) H2 compares agreement effects on peak NDVI in calm seasons that follow a shock with those in calm seasons that follow a calm season; (c) option codes ending "_26" are the 2026 versions of the same action, and CNUM is the 2024 SFI version of NUM (family A); SOH (soil health) actions are not on either list, so they go to C as written, with an exploratory version that counts them as A; (d) cluster-robust variance computed from each estimate's linear influence function, with stratum means and a common effect per cohort × season × shock × family fitted; the 50 km check is a wild (Rademacher) block bootstrap on the same influence function; (e) the embedding version of the matching waits for the national AlphaEarth extraction; (f) the 5 km hexagon check compares hexagon × cohort averages within cell × season (crop cannot be held fixed at hexagon level) | Wording needed a concrete reading to be computed; decided before any outcome by agreement status was seen |
| 2026-10-11 | **Decided after the first results were seen.** Trend adjustment (section 8, check 1) run because the pre-trend test and the placebo failed (event times −4 to −1: p < 0.001 for the effect, p = 0.049 for the shock contrast; placebo H1 +0.079). Method: each confirmatory contrast is re-estimated with one fixed base season (g − 1) and computed separately for seasons before entry (event times −4 to −2) and after entry; the adjusted estimate is the after-entry contrast minus the before-entry contrast for the same parcels (a triple difference), with the same matched sample, strata, clustering and Holm correction over H1–H3. Reported alongside the frozen-plan estimates, never instead of them | The plan names "trend adjustment" as the fallback but not its form; this form removes differences in shock response that existed before entry. Agreed with the project lead after seeing the first results |
| 2026-10-11 | **Post hoc diagnostic, after the trend-adjusted results.** Placebo split by contract start (before / after 1 March) and re-run without the season just before entry (results in wp3_trend_adjusted.md). Late starts do not explain the failed placebo; the H1 contrast depends on the base season. No further estimator changes made; any further version will be specified here before it is run | Keep the record of every analysis run after the results were seen |
| 2026-10-11 | **Specified after the results were seen, before it was run.** Within-cohort comparison, to remove each cohort's base-season offset. For each entry cohort with both kinds of season, the H1 contrast (shock minus non-shock seasons), the H2 contrast (calm-after-shock minus calm-after-calm) and the H3 contrast (B minus A, each within cohort) are computed from that cohort's own seasons only; cohorts are combined with weights proportional to their parcel-seasons in the contrast. Base season g − 1 for every season. Reported: after entry (main), before entry (event times −4 to −2, should be near zero) and after minus before. Check: the same within cohort × season (shocked vs not-shocked cells in the same season). Same matched sample, strata, ERA5-cell clustering and Holm over H1–H3. Whatever the outcome, this is the last estimator version for this Sentinel-2 round | The trend-adjusted and placebo results disagreed because the contrast pooled cohorts with different base seasons |
| 2026-10-17 | **Exploratory additions, specified before running.** (E1) MODIS history 2002–2016: in the matched sample, the shock-season minus non-shock-season difference between future agreement land and never-treated land, within ERA5 cell × season, years before any agreement (a long pre-period placebo for H1; MODIS 250 m stress index against each field's 2001–2016 normal). (E2) Sentinel-1 waterlogging (section 9): winter VH anomaly (per-orbit, angle-normalised panel, seasons 2017–2025; 2026 excluded as unreliable), the H1-type contrast with wet winters (October–March rainfall ≥ 30% above normal) in place of dry/heat shocks, same estimator, strata, matched sample and clustering. (E3) Embeddings: the matching repeated with AlphaEarth pre-entry embeddings (section 7), once the national extraction is complete. All exploratory, no multiple-testing correction | Using the supporting datasets listed for WP3 |
| 2026-10-17 | **E3 detailed before any embedding was used.** Pre-entry embedding = each field's mean AlphaEarth embedding over 2017–2020 (before every cohort's first full season; the same window as the outcome baseline). Its first 10 principal components (fitted on all sample fields) are added to the section 7 propensity covariates; matching otherwise unchanged (logistic per ITL1 region, nearest neighbour on the logit, caliper 0.2 SD, with replacement). Balance reported for all covariates including the 10 components. H1–H3 re-estimated on the new matched sample with the frozen-plan estimator and with the within-cohort design; reported next to the original matched sample. Exploratory | Makes E3 concrete before the data are used |
| 2026-10-17 | **Exploratory E4, specified before running: effects of the two options visible from space** (Paper 3: herbal leys SAM3/CSAM3 and no-till SOH1 detected; management-only actions not visible). The H1 contrast (shock minus non-shock effect on July NDVI) estimated separately for agreement fields with herbal leys, with no-till (if both, counted as herbal leys), and with management-only actions, against never-treated fields, on the embedding-matched sample (E3) with the frozen-plan estimator; **key test: herbal leys minus management-only, and no-till minus management-only** (both groups chose to join; only one changed the field visibly). Also the within-cohort version with its before-entry placebo. Exploratory, no multiple-testing correction | Effects on actions verified from space rather than declared |
| 2026-10-18 | **Exploratory X2, specified before running: the frozen-plan test with long-baseline normals.** Question: does the failed placebo (H1 +0.079 with entry two seasons early) and the failed pre-trend test come from the short normal? Pre-entry seasons include the 2017–2020 baseline seasons, whose deviations from their own mean sum to zero, which can create a mechanical pre/post gap. Design: frozen-plan estimator, matched sample, main shock definition and seasons unchanged; only the outcome changes. V0 Sentinel-2 July NDVI z (the frozen outcome, recomputed); V1 MODIS July NDVI z against each field's 2017–2020 seasons; V2 MODIS July NDVI z against its 2001–2016 seasons (MODIS July = mean of July composites, 250 m pixel at the parcel point). Statistics per version: H1, its components, the placebo H1 (entry two seasons early), the event-study pre-trend Wald tests (event times −4 to −1). **Reading, fixed in advance:** the baseline mechanism is supported if, from V1 to V2, the placebo H1 shrinks by at least half and its 95% interval includes zero, or the pre-trend Wald test on the effect moves from p < 0.05 to p ≥ 0.05; otherwise the placebo failure is read as selection, not the baseline. V2's H1 is reported as the long-baseline estimate, exploratory, beside the frozen estimate, never instead of it. Limits: MODIS pixels mix neighbouring fields; a 2001–2016 normal can drift by 2017–2026 | Venue plan: the cheapest robustness check in the programme |
| 2026-10-30 | **Further analyses registered before any of their data were extracted, each with its own protocol:** E3b, matching on OlmoEarth embeddings ([wp3_e3b_olmoearth_matching_protocol.md](wp3_e3b_olmoearth_matching_protocol.md)); W3-H, the harvest (economic resilience; field index gated on Defra regional yields) ([w3_h_harvest_protocol.md](w3_h_harvest_protocol.md)); wet grassland and fen ([w3_4_wet_grassland_protocol.md](w3_4_wet_grassland_protocol.md)); linear features ([w3_1_linear_features_protocol.md](w3_1_linear_features_protocol.md)); ponds ([w3_w_ponds_protocol.md](w3_w_ponds_protocol.md)). All exploratory, no multiple-testing correction across them | Project lead's requests: the three ELMs option groups, EO products with and without AI, physical and economic resilience |
| 2026-10-30 | **W3-S registered before the option crosswalk was built:** every option code placed in a group and family (none dropped silently), and how combinations of options within a field add up to physical and economic resilience ([w3_s_option_stacks_protocol.md](w3_s_option_stacks_protocol.md)). Wet grassland and linear-feature protocols changed before any extraction to keep fen and reedbed, cereal-land water buffers, and stone walls and banks | Project lead: keep every option; test combinations |
| 2026-10-30 | **Addendum 5 registered before any of its features were extracted** ([w3_x_addendum5_products_protocol.md](w3_x_addendum5_products_protocol.md)): precomputed OlmoEarth v1.3 embeddings as a further product in every option-group analysis (gated on England coverage of 2017–2020, checked monthly); a Sentinel-2 tillage index (NDTI); ΔAI, what each embedding adds on top of all no-AI products; per-pixel change features for ponds; a LiDAR hedge check found infeasible before any download. Changes no existing rule | Review of EO products by the project lead |

---

**Frozen version:** commit `b0f232b67dbb6d32630dae55778e7c08ff5750e3` in christophe-christiaen/SentiNews
(`eo-elms-resilience/wp3_elms_effect/results/preregistration.md`), 11 October 2026. The text above this line is
identical to that commit except for rows added to the decisions record (section 11) after it.
