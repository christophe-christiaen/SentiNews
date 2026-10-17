# Paper 2 outline: resilience of England's cereal land, field by field

*Draft outline, 12 October 2026. Status markers: ✅ done (result in the repo), 🔶 partly done, ⬜ to do.*

## Working titles
- **Unrecovered land is hit harder: field-scale drought legacies across England's cereal land from Sentinel-2**
- Stress debt from space: measuring how droughts compound at 380,000 fields

## The pitch (one paragraph)
Droughts are usually studied one at a time. But fields do not reset between seasons: land that has not recovered
from one shock may meet the next one weaker. We measure this at field scale for every cereal field in England
(381,400 fields, 2017–2026), using Sentinel-2 crop condition and shocks defined from weather alone (ERA5-Land). Three
findings: stress carries into the next season, unrecovered land is hit harder by the next shock, and accumulated
"stress debt" slows the rebound. A 50-site MODIS pilot (2001–2026) gives the long view. We release the field-level
panel and code, and show how the measures become a field resilience score that anticipates next season's hardest-hit
fields.

## Contributions
1. **Measurement:** field-scale resistance, recovery and stress debt for a whole country's cereal land, with shocks
   defined independently of the crop. ✅
2. **Evidence that shocks compound:** legacy, hit-harder and debt effects, comparing fields in the same weather cell
   and season, robust to crop rotation. ✅ (subject to check A below)
3. **Method (the ML contribution for ML venues):** a counterfactual model of each field's no-shock trajectory, so
   resistance and recovery are measured against what the field would have done, not against a fixed baseline. ⬜
4. **Use:** a transparent field score, back-tested on later seasons (lift 1.56 in the top 20%). ✅

## Analyses needed before writing (in order)
- **A. Within-field check (critical).** Each field's normal comes from only four seasons (2017–2020). An error in
  that normal shifts every later season the same way, which alone creates apparent persistence. Re-estimate T1–T3
  (a) with field fixed effects (and the Nickell-bias correction for a 10-season panel), (b) with the normal estimated
  from years that are excluded from the test, (c) on shuffled seasons as a placebo. If the effects shrink a lot, the
  headline changes. ✅ **Run 12 Oct: the effects do not survive** (T1, T2 ≈ 0 with split normals and Anderson–Hsiao;
  see results/within_field_check.md). The paper cannot claim that shocks compound at field level on 2017–2026 data;
  see "Reframing" below.
- **B. Counterfactual model (contribution 3).** Predict each field's expected greenness from weather and its own
  history, trained on calm seasons; test on 2018, 2020, 2022, 2025, 2026. Compare resistance and recovery measured
  this way against the z-score version. ⬜
- **C. Debt half-life from the data** instead of assuming 0.5 (currently checked at 0.3 and 0.7 only). 🔶
- **D. Winter shocks with Sentinel-1** (re-extraction per orbit running, 12 Oct). 🔶
- **E. Early vs late droughts** (the 2022 pattern), using heat timing. ⬜
- **F. External validation:** do field shock maps match drought declarations, Environment Agency flood records or
  Defra regional yield losses? (WP1 gives the yield link.) ⬜

## Sections

**1. Introduction.** Compound and consecutive droughts; why legacy effects matter for food supply, farm finance and
policy; gap: field-scale, whole-country, shock defined independently of the response.

**2. Related work.** Drought legacy effects in ecosystems and crops; EO resilience indicators (resistance, recovery,
critical slowing down); consecutive extremes; counterfactual / baseline approaches in EO; agricultural risk scoring.
*(Literature review still to do; key papers to be collected and checked, nothing cited yet.)*

**3. Data.** Sentinel-2 L2A (Cloud Score+), half-monthly NDVI / NDRE / NDMI, March–August, 2017–2026; RPA parcel
points; CROME 2016–2025; ERA5-Land monthly and daily (1991–2026); Environment Agency flood zones; Natural England
peat; MODIS pilot sites. ✅

**4. Methods.**
- 4.1 Stress index and shocks (S = mean of July and peak NDVI z-scores; dry and heat shocks from weather). ✅
- 4.2 Resilience measures: resistance, recovery, stress debt (D_t = λ D_{t−1} + min(S_t, 0)), typology. ✅
- 4.3 Tests T1–T3 within cell × season, clustered by ERA5 cell; crop-rotation control within cell × season × crop. ✅
- 4.4 Within-field identification (check A). ⬜
- 4.5 Counterfactual model (B). ⬜

**5. Results.**
- 5.1 Where and when cereal land was stressed, 2017–2026 (national timeline; 2025–26 back-to-back). ✅
- 5.2 Shocks compound: T1 +0.20, T2 +0.21, T3 +0.18; with crop rotation controlled +0.22, +0.20, +0.11. ✅
- 5.3 Typology: 35% of fields under repeated stress; regional pattern (East Midlands and Lincolnshire deepest). ✅
- 5.4 Field scale vs regions: the pilot overstated "hit harder" (+0.35 regional vs +0.21 field). ✅
- 5.5 Counterfactual resilience and winter shocks (B, D). ⬜
- 5.6 From measures to a score: back-test 2020–2025. ✅

**6. Discussion.** What compounding means for lenders and policy; limits: point sampling at field centres, a recent
baseline that includes droughts (2018, 2020), cereal land only, crop stress as a proxy for yield and income.

**7. Data and code availability.** Field-level panel (no personal data; RPA parcel references are public), code in
christophe-christiaen/SentiNews.

## Figures and tables
| # | Content | Status |
|---|---|---|
| Fig 1 | Study area: cereal fields, ERA5 cells, flood and peat | ✅ maps exist (stage0) |
| Fig 2 | National timeline of stress, shocks and debt, 2017–2026 | 🔶 numbers exist, figure to draw |
| Fig 3 | Maps: repeated stress and debt 2026 | ✅ wp2_resilience_types_debt.png |
| Fig 4 | T1–T3 coefficients: main, crop-controlled, within-field, pilot | 🔶 needs check A |
| Fig 5 | Typology shares by region | 🔶 table exists |
| Fig 6 | Counterfactual vs observed for example fields and 2025–26 | ⬜ |
| Tab 1 | Data sources | ⬜ easy |
| Tab 2 | Robustness: carry-over 0.3 / 0.5 / 0.7, rotation, within-field, thresholds | 🔶 |

## Venue
- **Science route:** ISPRS Journal of Photogrammetry and Remote Sensing, or Remote Sensing of Environment: full
  paper, no counterfactual model strictly needed if check A holds.
- **ML route:** ACM SIGSPATIAL or a workshop (ICLR ML4RS): needs contribution 3 (the counterfactual model) to be
  more than a measurement paper.
- Recommendation: write the science version first; the ML version follows once B exists. *(Deadlines for 2027 not
  checked.)*

## Suggested order of work
1. Check A (a day). 2. Fig 2, Fig 4, Tab 1. 3. Literature review. 4. Draft sections 1, 3, 4, 5.1–5.4, 6.
5. Counterfactual model (B) and Sentinel-1 (D) for the ML version.

## Reframing after check A (12 October 2026)
The compounding claims (contribution 2, section 5.2) are withdrawn for the field-level data. Options:
1. **A longer baseline:** rebuild the field normal from MODIS 2001–2016 (or Landsat) at field or 250 m scale and
   retest; this is the only way to tell lasting decline from noise in a four-season normal.
2. **A methods paper about exactly this:** short-baseline anomalies create spurious drought "legacies"; we show it at
   380,000 fields with split normals, dynamic-panel estimators and placebos. Useful and publishable, and it applies to
   much of the EO resilience literature.
3. **Persistent under-performance as the measure:** which fields sit below their normal for years, and does that
   predict anything external (yields, land-use change, scheme entry, finance)?
Recommendation: 2, with 1 as its key test.

## Analyses added 17 October 2026 (specified before running)
- **W1, flood zone and peat (supporting datasets on slide 41):** on the MODIS long-baseline panel (16-season normal,
  2002–2026), compare fields in Flood Zone 3 or on deep peat with other fields, within ERA5 cell × season: (a) stress in
  shock seasons (resistance) and in other seasons; (b) the within-field carry-over (Anderson–Hsiao) estimated
  separately for the two groups.
- **W2, Sentinel-1 winter wetness → crop condition:** on Sentinel-2 seasons 2017–2025, regress each field's stress
  index on its winter radar wetness anomaly (VH, per-orbit panel), with field and cell × season effects, overall and in
  wet-shock winters; errors clustered by ERA5 cell. Tests whether winter waterlogging, seen independently by radar,
  shows up in the following crop.
- **W3, land-use change from embeddings (specified 17 October 2026, before running):** each field's embedding shift =
  Euclidean distance between its mean AlphaEarth embedding 2017–2019 and 2023–2025 (multi-year means smooth out
  rotation); "changed" = the top 5% nationally. (a) Validation: how often changed fields left cereals in CROME (cereal in
  at least 2 of 3 years 2017–2019 and at most 1 of 3 in 2023–2025) compared with other fields. (b) Does the lasting
  offset (each field's mean Sentinel-2 stress 2021–2025 against its 2017–2020 normal) grow with the shift? Correlation
  and mean offset, changed vs other. (c) The Sentinel-2 pooled legacy test and its season-shuffling placebo (the
  lasting-difference component, +0.08) with changed fields excluded, against all fields.
