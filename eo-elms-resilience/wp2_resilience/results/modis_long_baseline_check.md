# Paper 2 long-baseline test: MODIS field normals from 16 seasons (2001–2016)

Design fixed before any MODIS parcel value was looked at (see the script docstring). Cell × season effects; errors clustered by ERA5 cell. MODIS pixels are 250 m, so small fields share pixels.

| Period | test | version | coefficient | SE | p | n |
|---|---|---|---|---|---|---|
| 2002-2026 | T1 | pooled | +0.058 | 0.002 | 0 | 9,531,916 |
| 2002-2026 | T2 | pooled | +0.120 | 0.003 | 0 | 3,222,559 |
| 2002-2026 | T1 | field fixed effects | +0.011 | 0.002 | 3.54e-08 | 9,531,916 |
| 2002-2026 | T2 | field fixed effects | +0.020 | 0.002 | 0 | 3,222,559 |
| 2002-2026 | T1 | Anderson-Hsiao | -0.019 | 0.002 | 0 | 9,149,910 |
| 2002-2026 | T2 | Anderson-Hsiao | -0.012 | 0.002 | 5.65e-11 | 3,216,824 |
| 2002-2026 | T3 | pooled | +0.120 | 0.003 | 0 | 1,840,327 |
| 2002-2026 | T2 | pooled, without 2006 | +0.129 | 0.003 | 0 | 3,037,169 |
| 2002-2026 | T2 | pooled, without 2010 | +0.135 | 0.003 | 0 | 2,866,012 |
| 2002-2026 | T2 | pooled, without 2011 | +0.133 | 0.003 | 0 | 2,866,954 |
| 2002-2026 | T2 | pooled, without 2018 | +0.124 | 0.003 | 0 | 2,855,605 |
| 2002-2026 | T2 | pooled, without 2020 | +0.115 | 0.003 | 0 | 2,909,803 |
| 2002-2026 | T2 | pooled, without 2022 | +0.115 | 0.003 | 0 | 2,864,348 |
| 2002-2026 | T2 | pooled, without 2025 | +0.107 | 0.003 | 0 | 2,845,997 |
| 2002-2026 | T2 | pooled, without 2026 | +0.084 | 0.002 | 0 | 2,847,592 |
| 2002-2026 | T1 | shuffled seasons (placebo) | -0.000 | 0.000 | 0.977 | 9,150,620 |
| 2017-2026 | T1 | pooled | +0.167 | 0.003 | 0 | 3,812,787 |
| 2017-2026 | T2 | pooled | +0.186 | 0.003 | 0 | 1,967,543 |
| 2017-2026 | T1 | field fixed effects | -0.076 | 0.002 | 0 | 3,812,787 |
| 2017-2026 | T2 | field fixed effects | -0.039 | 0.002 | 0 | 1,967,543 |
| 2017-2026 | T1 | Anderson-Hsiao | -0.004 | 0.002 | 0.0264 | 3,812,472 |
| 2017-2026 | T2 | Anderson-Hsiao | -0.004 | 0.002 | 0.0565 | 1,967,392 |
| 2017-2026 | T3 | pooled | +0.204 | 0.003 | 0 | 930,993 |
| 2017-2026 | T2 | pooled, without 2018 | +0.206 | 0.003 | 0 | 1,600,589 |
| 2017-2026 | T2 | pooled, without 2019 | +0.191 | 0.003 | 0 | 1,847,813 |
| 2017-2026 | T2 | pooled, without 2020 | +0.189 | 0.003 | 0 | 1,654,787 |
| 2017-2026 | T2 | pooled, without 2022 | +0.191 | 0.003 | 0 | 1,609,332 |
| 2017-2026 | T2 | pooled, without 2025 | +0.188 | 0.003 | 0 | 1,590,981 |
| 2017-2026 | T2 | pooled, without 2026 | +0.152 | 0.003 | 0 | 1,592,576 |
| 2017-2026 | T1 | shuffled seasons (placebo) | +0.074 | 0.002 | 0 | 3,431,535 |

**Simulation of this design** (16-season normal, 26 seasons; mean of 20 runs, T1):

| true carry-over ρ | pooled | field fixed effects | Anderson–Hsiao |
|---|---|---|---|
| 0.0 | -0.011 | -0.038 | -0.002 |
| 0.1 | +0.082 | +0.053 | +0.091 |
| 0.2 | +0.176 | +0.144 | +0.184 |

## Reading (12 October 2026)

- **With a 16-season normal, season-to-season carry-over at field level is small or absent.** Over 2002–2026, T1 is
  +0.058 pooled, +0.011 with field fixed effects and −0.019 within each field (Anderson–Hsiao); against the simulated
  values for this design (no carry-over: −0.011, −0.038, −0.002; true 0.1: +0.082, +0.053, +0.091) the true
  carry-over is at most about 0.05–0.07 and the within-field estimate points to about zero. Shuffling seasons gives
  0.000: lasting field differences do not drive the pooled figure here.
- **"Hit harder" (T2) is not a single-event artefact in this longer record** (pooled +0.12, between +0.08 and +0.14
  leaving out each shock season in turn), but within each field it is small or absent (+0.020 fixed effects, whose
  no-effect value is about −0.04; −0.012 Anderson–Hsiao).
- **Testing only seasons after the baseline brings the artefact back.** On 2017–2026 alone, every season lies after
  the 2001–2016 normal: pooled T1 and T2 rise to +0.17 and +0.19, shuffling gives +0.07, and within each field the
  estimates are about zero (−0.004). This is the Sentinel-2 pattern reproduced with a different sensor and a long
  normal: what matters is not only the baseline length but whether the tested seasons share the baseline's error and
  any lasting change since it was set.
- Limitation: MODIS pixels are 250 m (about 6 ha), so small neighbouring fields share values; that blurs field
  differences but cannot create season-to-season carry-over within a field.
