# W2-1b protocol: why does the Landsat 7-only version disagree?

**Written 30 October 2026, before any of the analyses below was run.** It follows up the sensitivity flag in
[w2_1_landsat_protocol.md](w2_1_landsat_protocol.md) (R4). Changes after this date go in the record at the end.

## Question
With a long normal (2001–2016), the all-sensor Landsat test gives Anderson–Hsiao T1 −0.020 (2002–2026; 381,400 fields),
confirming MODIS. Landsat 7 alone gives −0.083 (2002–2023; 353,008 fields), so the sensor mix was flagged as a limit.
Is the gap due to (a) a different sample and period, (b) noisier measurements, (c) sparse data (missing windows, fewer
baseline seasons), or (d) the normal overlapping the test seasons, rather than to anything in the sensor itself?

## Data
Existing per-parcel Landsat values (`shared/data/landsat_parcels/`, extracted under W2-1); no new download. Stress S, the
normal, the shocks, the lags and the estimators exactly as in W2-1 (`w2_1_landsat.py`, `modis_long_baseline_check.run`).
"All-sensor" = S from all Landsat sensors, "L7" = S from Landsat 7 alone, both with normal 2001–2016 and at least 8 clear
baseline seasons unless stated.

## Diagnostics (all report T1, T2 with pooled, field fixed effects and Anderson–Hsiao; the reading uses Anderson–Hsiao T1)
- **D1 · same fields, same seasons.** All-sensor S restricted to the L7 fields and years 2002–2023, and set to missing
  wherever L7 S is missing, so both versions have identical field-seasons. Isolates sensor from sample and period.
- **D2 · added noise.** The excess noise of L7 is estimated on the D1 field-seasons as
  σ² = var(S_L7 − field mean) − var(S_all − field mean). If σ² > 0, Gaussian noise N(0, σ²) (seed 30) is added to the D1
  all-sensor S (then clipped to ±6) and the tests rerun. If σ² ≤ 0, D2 is reported as not applicable.
- **D3a · complete windows.** L7 restricted to field-seasons in which both the July and the peak window have a clear
  Landsat 7 value (S is otherwise the value of one window).
- **D3b · longer baseline.** L7 with at least 12 (instead of 8) clear baseline seasons for the normal.
- **D4 · tests outside the normal.** L7 tests on 2017–2023 only, the seasons outside the 2001–2016 normal (a z-score
  normal that includes the tested seasons forces the field's z-scores in that period to sum to zero, which makes
  seasons look negatively related; the effect is larger when the normal has fewer seasons).
- Descriptive: clear baseline seasons per field and share of field-seasons with both windows, L7 and all-sensor.

## Reading, fixed in advance (reference values: all-sensor −0.020, L7 −0.083, Anderson–Hsiao T1)
- **R1 · sample and period are not the cause** if D1 lies within ±0.05 of −0.020.
- **R2 · noise of L7's size reproduces the gap** if D2 lies within ±0.03 of −0.083.
- **R3 · a data-density cause removes the gap** for each of D3a, D3b, D4 whose estimate lies within ±0.05 of −0.020.
- **Conclusion:** the flag is attributed to Landsat 7's data, not to the sensor or to carry-over, if R1 holds and R2 or
  at least one R3 holds; the cause is named by which ones hold. Otherwise the limit stands as stated in W2-1.
- **Expectation stated now, not used in the rules:** D1 near −0.02; D4 or D3b closes most of the gap.

## Output
`wp2_resilience/results/w2_1b_landsat7.md`, `.json` (aggregates only). Script `wp2_resilience/src/w2_1b_landsat7.py`.

## Record
| Date | Change | Reason |
|---|---|---|
| 2026-10-30 | Protocol written, before any diagnostic was run | Follow-up of the W2-1 sensor-mix flag |
| 2026-10-30 | Run ([w2_1b_landsat7.md](w2_1b_landsat7.md)). R1 yes: on identical field-seasons the all-sensor data give −0.032, so sample and period are not the cause. R2 no: noise of Landsat 7's excess variance (0.45) moves the all-sensor estimate only to −0.017. R3: restricting Landsat 7 to seasons with both windows gives −0.026 (yes); 12+ baseline seasons −0.093 (no); tests 2017–2023 −0.096 (no). Conclusion under the rules: the flag is attributed to Landsat 7's data, specifically to seasons in which S rests on one window instead of two (only 37% of Landsat 7 field-seasons have both windows, against 75% for all sensors), not to the sensor or to carry-over. Caveats: the both-windows subset is small (64,102 Anderson–Hsiao observations) and selected for good coverage; the expectation (D4 or D3b closes the gap) was wrong, and the D4 placebo is itself +0.086, as for the all-sensor 2017–2026 version | Result |
