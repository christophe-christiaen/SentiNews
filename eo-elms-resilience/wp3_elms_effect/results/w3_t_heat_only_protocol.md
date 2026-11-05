# W3-T protocol: heat apart from drought

**Status: registered 5 November 2026 by public commit, before any heat-only or heat-on-drought contrast was computed.
Exploratory; not co-primary with H1.** Builds on the WP3 decisions record ([preregistration.md](preregistration.md)),
W3-H ([w3_h_harvest_protocol.md](w3_h_harvest_protocol.md)) and Addendum 6 Part F
([w3_z_addendum6_hazards_protocol.md](w3_z_addendum6_hazards_protocol.md)). Changes after registration go in the record at the end.

## Why
The registered shock pools dry and hot seasons, because they usually strike together, so no WP3 result says whether
agreement land copes with heat itself. Heat is also why the blind 2026 harvest forecast missed. Separately, the
wet-winter harvest contrast of 5 November showed that seasons have to be kept apart: after entry, dry or heat seasons
are mostly 2022 and 2025 and wet ones 2021 and 2024, so those two contrasts largely compare the same seasons with the
sign reversed.

## What the seasons allow (weather only, computed before this registration)
Share of E3-matched fields and number of ERA5 cells, with wet-shock cell-seasons removed:

| Season | Hot, not dry | Hot and dry | Dry, not hot | Calm | Fields after entry |
|---|---:|---:|---:|---:|---:|
| 2018 | 1% (37 cells) | 25% (307) | 71% (1,194) | 4% | before entry |
| 2019 | 32% (389) | 0% | 0% | 68% | before entry |
| 2020 | 0% | 0% | 3% (50) | 7% | before entry |
| 2021 | 0% | 0% | 1% (74) | 26% | 10,713 |
| 2022 | 11% (143) | 62% (918) | 22% (353) | 6% | 34,521 |
| 2023 | 0% | 0% | 9% (221) | 83% | 51,764 |
| 2024 | 0% | 0% | 0% | 1% | 109,425 |
| 2025 | 0% | 45% (585) | 54% (972) | 1% | 219,338 |
| 2026 | 0% (3) | 22% (373) | 6% (114) | 2% | 236,555 |

After entry, hot-not-dry fields exist in effect in one season: 2022, 143 cells, 4,235 treated fields. A literal
heat-only contrast therefore cannot separate heat from whatever else happened in 2022. Heat on top of drought has hot
and dry-only cells side by side in three seasons.

## Definitions
As frozen: **heat** is 5 or more days at or above 28 °C in June–August per ERA5-Land cell; **dry** is March–July rain at
least 20% below the 1991–2020 normal, or soil moisture at least 1 SD below. Every contrast drops wet-shock cell-seasons
from both sides, so that wet winters cannot enter as the comparison.
- **Hot, not dry;** **hot and dry;** **dry, not hot;** **calm** (not hot, not dry, not wet).

## Contrasts
All on the E3 matched sample, strata ERA5 cell × season, SE clustered by ERA5 cell, frozen-plan estimator, before-entry
placebo with entry two seasons early on seasons up to 2020.
- **T1, heat on top of drought (the main test):** agreement effect in hot-and-dry cell-seasons minus dry-not-hot cell-seasons.
  Placebo rests on 2018.
- **T2, literal heat-only:** agreement effect in hot-not-dry cell-seasons minus calm cell-seasons. Placebo rests on 2019.

**Outcomes:** July NDVI z-score (SD), seasons 2017–2026; W3-H field harvest index (t/ha), seasons 2017–2025, with 2026
added after Defra's final figures on 10 December 2026.

**Families:** all agreement land, management-only, cover crops, no-till, as in W3-H Step 3. Members as in Part F (any code
of the family). So 16 deciding rows; no multiple-testing correction.

## Stage 1: power, reported before any estimate
The script first writes only parcel-seasons, contributing cells, contributing seasons and standard errors, with no
estimate, for every deciding row. The project lead sees this before Stage 2 runs.
- **Minimum detectable effect (MDE):** 2.8 × SE, for 80% power at 5% two-sided.
- **Limits, fixed now:** 0.10 SD for July NDVI, about the size of H1 (+0.082); 0.10 t/ha for the harvest index, the size W3-H expected.
- A row over its limit is reported as **underpowered, not read**, whatever its estimate.
- **Fewer than 30 contributing cells:** clustered SEs are unreliable, so the row is also not read.

## Stage 2: reading, fixed in advance
For a row within its limits:
- **Holds better under heat** if the interval is above zero and the placebo interval includes zero.
- **Heat cost indicated** if the interval is below zero and the placebo interval includes zero. This condition is applied
  to both directions, unlike W3-H's "holds worse", because the wet-winter contrast showed a below-zero interval can be
  entirely a before-entry gap.
- Otherwise **not shown**.
- **T2 can never be stronger than "one season":** any result is labelled as resting on 2022 alone, and cannot on its own
  be read as a heat effect.

## Reported, does not decide
- **T1 within each season:** hot-and-dry minus dry-not-hot inside 2022, 2025 and 2026 separately, and pooled weighted by
  treated fields in hot cells. This removes the differences between seasons but keeps those between hot and less hot areas.
- Within cohort and its before-entry version; never-treated controls only; strata with CROME crop.
- **Thresholds:** heat at 3 and 8 days, as in the frozen sensitivity list.
- **Each crop separately,** same crop in both seasons, for the harvest index.
- **£/ha:** W3-H's rule, feed wheat mean 2021–2025, £204/t, with the range across price series; revenue only.

## Index check, reported with the results, does not change the reading
Per crop, error against Defra in hot region-seasons (at least half the region's cereal-frame fields in heat cells)
against other region-seasons, with the bias and W3-H's 1.5 limit as a yardstick. A crop over 1.5 is stated as a limit on
the result. The harvest model has never been trained on record heat, as the 2026 forecast showed.

## Stated limits
- **Timing:** the heat window runs June–August, so August heat cannot affect July NDVI. The harvest index runs to the end of August.
- **Geography:** hot cells are not random; heat falls mostly in the south and east. Strata remove differences between
  cells in level, but not a different agreement effect in those areas for other reasons.
- **Index, not yield:** weather mostly cancels between fields in one cell, so the index rests largely on Sentinel-2 and
  can't be assumed to see heat damage to grain filling.
- **Short after-entry history:** most treated fields entered in 2024 or later, so 2025 and 2026 carry most of T1.

## Known before this registration
H1 and its placebos; W3-H's dry-or-heat result (+0.039 t/ha, not robust); the wet-winter harvest result; the 2026
forecast's miss in record heat; the seasonal shares of heat and drought; the table above. So this is not blind to which
seasons dominate. No contrast splitting hot from dry-only cells has been computed. The earlier sensitivity to heat
thresholds (+0.084 at 3 days, +0.082 at 8 days) varied the pooled shock and did not separate them.

## Output
`wp3_elms_effect/src/w3_t_heat_only.py`; `wp3_elms_effect/results/w3_t_heat_only.md`, `.json` (aggregates only). No new data
are needed.

## Record
| Date | Change | Reason |
|---|---|---|
| 2026-11-05 | Registered by public commit before any contrast was computed. Not run; Stage 1 goes to the project lead first | Project lead: register the heat-only test |
| 2026-11-05 | **Stage 1 run, no estimate read or written** ([w3_t_heat_power.md](w3_t_heat_power.md)). 4 of 16 rows are readable: T1, all agreement land and management-only, on July NDVI (MDE 0.072, 0.083) and harvest index (0.062, 0.073). All T2 rows are unreadable (all land 0.161 and 0.102), as are cover crops and no-till. **Error in this protocol, found by Stage 1:** T1's placebo was stated to rest on 2018, but it can't be computed as written. The earliest entry is 2021, so entry two seasons early reaches only 2019 and 2020, which have no hot-and-dry cells outside wet shocks. T2's placebo works, resting on 2019. A before-entry check on event times −4 to −2, seasons to 2020, does reach 2018 (hazard side 2018 only, cohorts 2021–2022): SE and MDE, July all land 0.039 and 0.108, harvest all land 0.030 and 0.085, management-only 0.050 and 0.141, 0.041 and 0.114. No change is made here. The project lead decides what replaces the T1 placebo before Stage 2 runs | Stage 1 reported before any estimate |
| 2026-11-05 | **Deviation, fixed before any estimate was computed: T1's before-entry check.** Replaces the placebo that can't be computed. One base season (g − 1), event times −4 to −2, seasons to 2020, hot and dry minus dry, not hot; it rests on 2018 and cohorts 2021–2022 on the hot side. T1's reading uses its interval in place of the placebo's. **Fixed in advance:** if the check's own MDE is over the row's limit, any reading carries the label "weak before-entry check" (July all land 0.108, management-only 0.141; harvest management-only 0.114; harvest all land 0.085 is within). T2 keeps its registered placebo. The 4 readable rows, and the fact that T2 can't be read, stay as Stage 1 found. Stage 2 now runs | Project lead chose the before-entry check |
