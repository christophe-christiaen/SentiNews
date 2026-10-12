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

## Reading (12 October 2026)

- **No season-to-season legacy once each field's own level is removed.** With the two normals taken from disjoint
  seasons, T1 and T2 fall from +0.20 to −0.01; the Anderson–Hsiao estimate with a strong instrument (first-stage
  r −0.62) is −0.006 for T1 and +0.005 for T2. Field fixed effects agree for T1 (−0.013). The S(t−3) instrument is
  far too weak (r 0.01) to say anything and is ignored.
- **So the published +0.20 / +0.21 / +0.18 are not evidence that shocks compound.** They come from fields sitting
  persistently above or below their 2017–2020 normal in later seasons. Shuffling the season order still gives +0.08
  (stable differences); the rest comes from the post-2020 seasons sharing the same offset, which the four-season
  normal cannot separate from a real lasting shift in the field.
- **T3 (debt slows rebound) does not survive either:** +0.11 of +0.18 appears with shuffled seasons, and with field
  fixed effects the sign reverses (−0.34, partly the short-panel bias).
- **What remains true:** fields differ persistently in how they sit against their own normal, and that persistence is
  what makes the field score predictive in its back-test (which is out-of-sample and stands as measured). Whether
  the lasting offsets are real decline or noise in a four-season normal needs a longer baseline (MODIS 2001–2016, or
  Landsat) to settle.
- **The pilot** used a 15-season normal (2001–2015) and regional averages, so it is less exposed, but it was not
  tested this way and should not be cited as confirmation until it is.