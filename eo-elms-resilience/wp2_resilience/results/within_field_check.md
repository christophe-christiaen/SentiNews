# WP2 check A: is the compounding real, or an artefact of the field normal?

Each field's normal comes from four seasons (2017–2020); an error in it shifts every season the same way and can look like persistence. The versions below remove that possibility in different ways. Cell × season effects absorbed; errors clustered by ERA5 cell.

| Test | version | coefficient | SE | p | n | note |
|---|---|---|---|---|---|---|
| T1 | original | +0.199 | 0.002 | 0 | 3,429,308 |  |
| T2 | original | +0.210 | 0.002 | 0 | 1,965,095 |  |
| T1 | split normal | -0.011 | 0.001 | 0 | 3,429,371 |  |
| T2 | split normal | -0.010 | 0.001 | 0 | 1,965,100 |  |
| T1 | field FE (lower bound) | -0.013 | 0.002 | 3.55e-15 | 3,429,308 |  |
| T2 | field FE (lower bound) | +0.070 | 0.002 | 0 | 1,965,095 |  |
| T1 | Anderson-Hsiao, z = S(t-2) | -0.006 | 0.002 | 0.0022 | 3,047,498 | first-stage r -0.62 |
| T2 | Anderson-Hsiao, z = S(t-2) | +0.005 | 0.003 | 0.0732 | 1,599,798 | first-stage r -0.60 |
| T1 | Anderson-Hsiao, z = S(t-3) | +3.246 | 0.425 | 2.2e-14 | 2,666,089 | first-stage r 0.01 |
| T2 | Anderson-Hsiao, z = S(t-3) | +0.222 | 0.084 | 0.00793 | 1,478,384 | first-stage r 0.02 |
| T1 | shuffled seasons (placebo) | +0.079 | 0.001 | 0 | 3,427,436 |  |
| T2 | shuffled seasons (placebo) | +0.078 | 0.001 | 0 | 1,965,139 |  |
| T3 | original | +0.176 | 0.004 | 0 | 931,183 |  |
| T3 | field FE (lower bound) | -0.335 | 0.011 | 0 | 926,264 |  |
| T3 | shuffled seasons (placebo) | +0.110 | 0.002 | 0 | 929,720 |  |

## Reading (12 October 2026, revised after the simulation the same day)

- **Calibration by simulation** (`src/baseline_artefact_sim.py`, fields with a known carry-over ρ, z-scored against
  their first four seasons as here): the Anderson–Hsiao estimate is attenuated in this setting: true ρ 0, 0.1, 0.2,
  0.3 give −0.02, +0.07, +0.13, +0.20 (+0.08 for ρ 0.2 with added measurement noise); field fixed effects give
  −0.06, +0.03, +0.08, +0.16.
- **T1 (stress carries over): at most a small carry-over.** Anderson–Hsiao −0.006 sits between the simulated ρ = 0
  and ρ = 0.1, and field fixed effects (−0.013) imply ρ ≈ 0.05. The published +0.20 is far outside this range.
- **T2 (unrecovered land hit harder): unresolved, but much smaller than published.** Anderson–Hsiao gives +0.005,
  while field fixed effects give +0.070, above the ≈ −0.06 they show with no carry-over; taken at face value that
  points to a small effect (up to about 0.1). The published +0.21 is not supported either way.
- **The short baseline explains most of the published figure.** With no carry-over at all, a four-season normal over
  ten seasons produces about +0.13 in the same test (simulation). The rest is consistent with lasting differences
  between fields (shuffled seasons: +0.08).
- **The "split normal" version is not valid evidence** and is withdrawn: in the simulation it returns +0.04 when the
  true carry-over is 0.2, so its −0.01 says little. It stays in the table for the record.
- **T3 (debt slows rebound) is not supported:** +0.11 of +0.18 appears with shuffled seasons, and field fixed effects
  reverse its sign.
- **What remains true:** fields differ in a lasting way against their own normal, which is what makes the field score
  predictive in its back-test (out-of-sample, stands as measured). A longer baseline (MODIS 2001–2016, or Landsat)
  is needed to tell real lasting decline from noise in a four-season normal.
- **The pilot** used a 15-season normal and regional averages; the simulated artefact for that set-up is small, but
  the pilot was not tested this way and is not confirmed.
