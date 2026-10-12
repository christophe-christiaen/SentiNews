# Pilot re-check: do the compounding effects survive within each site?

50 MODIS sites, 2001–2026, each site's normal 2001–2015; national shock years 2018, 2022, 2025, 2026. Errors clustered by site. Same diagnostics as the field-level check (wp2_resilience/results/within_field_check.md).

| Test | version | coefficient | SE | p | n | note |
|---|---|---|---|---|---|---|
| T1 | as reported (year effects) | +0.121 | 0.039 | 0.00194 | 1,250 |  |
| T2 | as reported (year effects) | +0.349 | 0.094 | 0.00019 | 200 |  |
| T1 | site fixed effects | +0.049 | 0.034 | 0.146 | 1,250 |  |
| T2 | site fixed effects | -0.118 | 0.085 | 0.167 | 200 |  |
| T1 | within each site (Anderson-Hsiao) | -0.020 | 0.035 | 0.564 | 1,200 | first-stage r -0.67 |
| T2 | within each site (Anderson-Hsiao) | -0.240 | 0.137 | 0.081 | 200 | first-stage r -0.62 |
| T3 | as reported (year effects) | +0.312 | 0.147 | 0.0342 | 150 |  |
| T3 | site fixed effects | -0.141 | 0.180 | 0.432 | 150 |  |

**Season-shuffling placebo** (200 shuffles of each site's seasons; what lasting site differences alone give, as-reported test): T1 +0.004 (SD 0.027); T2 +0.005 (SD 0.080); T3 +0.012 (SD 0.092)

**Simulation of this design** (50 sites, 26 seasons, 15-season normal, year effects; 300 runs; mean (SD) of the T1 estimate):

| true carry-over ρ | as reported (pooled) | site fixed effects | Anderson–Hsiao |
|---|---|---|---|
| 0.0 | -0.003 (0.032) | -0.035 (0.031) | -0.003 (0.045) |
| 0.1 | +0.090 (0.033) | +0.055 (0.031) | +0.094 (0.049) |
| 0.2 | +0.182 (0.035) | +0.144 (0.032) | +0.185 (0.047) |
| 0.3 | +0.273 (0.032) | +0.232 (0.029) | +0.268 (0.051) |

**Extra checks** (run after the table above, same day): with **region × year effects** (sites compared only with
sites in the same region and year), T1 +0.104 (SE 0.041), T2 +0.300 (0.091), T3 +0.216 (0.105). **T2 leaving out one
shock year at a time:** without 2018 +0.479, without 2022 +0.340, without 2025 +0.411, **without 2026 +0.003 (0.135)**.

## Reading (12 October 2026)

- **No short-baseline artefact in the pilot.** With a 15-season normal the as-reported test is almost unbiased in
  simulation (−0.003 when there is no carry-over), and shuffling each site's seasons gives about zero (T1 +0.004,
  T2 +0.005). This is unlike the field-level Sentinel-2 data, where a 4-season normal created most of the effect.
- **Not regional weather either.** Comparing sites only within their region and year leaves T1, T2 and T3 positive.
- **"Unrecovered land is hit harder" (T2, +0.35) rests on a single event.** It comes entirely from 2026: sites that were
  stressed in 2025 were hit hardest in 2026. Without 2026 the effect is zero (+0.003), and within each site it is
  negative (site fixed effects −0.12; Anderson–Hsiao −0.24, p = 0.08). One back-to-back drought cannot separate a
  land legacy from sites that are simply dry two years running for local reasons (weather below region scale, soils).
  **Not confirmed as a general effect.**
- **Legacy (T1, +0.12): modest and uncertain.** Robust to region × year effects (+0.10); site fixed effects (+0.049)
  match a true carry-over of about 0.1 in simulation, but Anderson–Hsiao (−0.020, SE 0.035) points to about zero. At
  most about 0.1.
- **Debt slows rebound (T3, +0.31):** weaker with region × year effects (+0.22) and negative with site fixed effects
  (−0.14, n = 150). Not confirmed.
