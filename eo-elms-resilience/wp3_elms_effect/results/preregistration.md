# WP3 pre-registration: do agri-environment agreements buffer cereal land against weather shocks?

**Status:** draft for review, written on 11 October 2026, **before any Sentinel-2 outcome has been compared between
agreement and non-agreement land**. Once agreed, this file is frozen (git commit hash recorded below); every later change
goes in the deviations log at the end, with date and reason.

## 1. What has and has not been looked at

Seen before writing this plan:
- Counts of parcels by scheme group, entry year, flood zone and peat class (no outcomes).
- ERA5-Land weather by year, nationally and by cell (exposure only, not crop response).
- Sentinel-2 for one test tile (30UXD, 2022), **pooled over all cereal parcels, not split by scheme group**; and
  Earth Engine output checks (coverage, value ranges) on a few squares, again not split by group.
- Pilot results at 50 MODIS sites (site-level CS share showed no link to drought response).

Not seen: any Sentinel-2 or MODIS outcome by agreement status at parcel level.

## 2. Question and hypotheses

Does land under an area-based Countryside Stewardship (CS) or Sustainable Farming Incentive (SFI) option respond
differently to weather shocks than comparable cereal land outside any agreement?

- **H1 (resistance):** in shock seasons, agreement parcels show a smaller drop in crop condition than matched
  non-agreement parcels.
- **H2 (recovery):** in the season after a shock, agreement parcels return closer to their own normal.

Both are two-sided tests; the expected sign is positive (buffering), but a negative effect (agreements on more
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
- **Option families** (for heterogeneity only): SFI soil, nutrient and pest management (SAM, NUM, IPM, CSAM, CIPM);
  land-use change on the parcel (herbal leys, grassland, buffers, wildflower and winter bird food: SAM3, CSAM3, LIG,
  CLIG, AHL, CAHL, CS AB / GS / SW options); CS other.

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
  a shock.
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
- **Matching (before estimation):** each treated parcel is matched (nearest neighbour on a propensity score, then
  checked for balance) to untreated parcels in the same ITL1 region on: the pre-entry Sentinel-2 trajectory
  (2017–2020 half-monthly NDVI means), cereal share and crop sequence in CROME 2016–2020, flood zone, peat class, and
  scheme intensity within 1 km. Balance target: standardised mean differences below 0.1. Embeddings (AlphaEarth,
  pre-entry year) are added as a robustness version of the matching.
- **Inference:** standard errors clustered by ERA5 cell (about 9 km), the level at which shocks vary; spatial block
  bootstrap (50 km blocks) as a check.
- **Multiple testing:** H1 and H2 are the two confirmatory tests, Holm-adjusted at 5%. Everything else is exploratory
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

## 9. Heterogeneity and secondary analyses (exploratory)

By option family; by entry cohort; by region (ITL1); on flood zone 3 or deep peat vs elsewhere; wet shocks
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
