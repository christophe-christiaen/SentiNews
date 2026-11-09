# W3-B1 checks on H1 and H2

Protocol: [w3_b1_h1h2_checks_protocol.md](w3_b1_h1h2_checks_protocol.md). Exploratory labels beside the confirmatory tests; their registered readings are unchanged. Both reproduced first: H1 +0.082, H2 +0.035.

**In short: H1's cushion appears only on the field z-score.** On raw July NDVI, on a ratio to the field's normal and on a z-score with a shared scale, it is near zero, and on one of them below zero. **H2's comparison side is almost entirely the wet 2024 season,** and without wet-shock cells H2 is too imprecise to say anything. The harvest results are in t/ha and don't use this scaling.

## Check 1: H2's comparison seasons

Labels: **comparison side dominated by wet seasons: yes; H2 depends on wet seasons: yes,** on both samples.

| | X2 sample (frozen) | E3 sample |
|---|---:|---:|
| H2 | +0.035 (-0.012, +0.081) | +0.024 (-0.023, +0.071) |
| Without wet-shock cells, both sides | -0.028 (-0.164, +0.109) | -0.002 (-0.166, +0.161) |
| Share in wet-shock cells: after a shock / after calm | 33% / 94% | 33% / 94% |

Season weights, X2 sample. After a shock: 2021 15%, 2022 0%, 2023 67%, 2024 18%. After calm: 2021 1%, 2022 2%, 2023 2%, 2024 93%, 2025 2%.

Leave one season out, X2 sample: without 2021 +0.040 (-0.009, +0.090); without 2022 +0.035 (-0.012, +0.082); without 2023 -0.026 (-0.099, +0.047); without 2024 +0.000 (-0.127, +0.128); without 2025 +0.039 (-0.007, +0.086).

**Reading:** H2 compares calm seasons after a dry or heat shock (mostly 2023) with calm seasons after calm ones, which are 93% season 2024, almost all in wet-shock cells. Taking out the wet cells leaves an interval about three times as wide, -0.028 (-0.164, +0.109). H2's registered "no evidence" stands, but the design couldn't have shown recovery cleanly: it has, in effect, one comparison season and that season was a wet shock.

## Check 2: H1 under other scalings

Each outcome on its own scale, with estimate ÷ SE. The frozen z-score divides by each field's own 2017–2020 SD.

| Outcome | Sample | Frozen z | Raw (NDVI units) | Ratio, % of normal | Pooled-SD z | z capped at ±5 | Label |
|---|---|---:|---:|---:|---:|---:|---|
| July NDVI | X2 sample (frozen) | +0.082 (+0.049, +0.115), t +4.9 | -0.0014 (-0.0044, +0.0016), t -0.9 | -0.68 (-1.34, -0.03), t -2.0 | -0.011 (-0.029, +0.006), t -1.3 | +0.074 (+0.050, +0.099), t +6.0 | depends on scaling |
| July NDVI | E3 sample | +0.087 (+0.050, +0.123), t +4.6 | +0.0024 (-0.0007, +0.0055), t +1.5 | +0.19 (-0.48, +0.86), t +0.5 | +0.011 (-0.007, +0.029), t +1.2 | +0.065 (+0.039, +0.090), t +5.0 | depends on scaling |
| Seasonal integral | X2 sample (frozen) | +0.120 (+0.049, +0.191), t +3.3 | +0.0170 (-0.0013, +0.0353), t +1.8 | +0.34 (-0.06, +0.74), t +1.7 | +0.019 (-0.003, +0.040), t +1.7 | +0.075 (+0.044, +0.106), t +4.8 | depends on scaling |
| Seasonal integral | E3 sample | +0.083 (+0.007, +0.159), t +2.1 | +0.0184 (+0.0000, +0.0369), t +2.0 | +0.38 (-0.02, +0.79), t +1.9 | +0.020 (-0.001, +0.042), t +1.9 | +0.064 (+0.033, +0.096), t +4.0 | depends on scaling |

Diagnostics, all fields: July NDVI field SD at the 0.02 floor 1.4%; July z beyond ±5 in 3.5%–4.7% of field-seasons from 2021. The rebuilt z-score matches the stored one to 1e-5.

**Reading: H1 depends on scaling.**
- On the frozen sample, raw July NDVI gives −0.0014 (−0.0044, +0.0016), the shared-scale z −0.011 (−0.029, +0.006), and the ratio −0.68% (−1.34, −0.03), the opposite sign. On the E3 sample all three are near zero with intervals including it.
- **Capping at ±5 keeps the result** (+0.074), so it isn't a few extreme fields. It comes from dividing each field by its own SD across the bulk of fields: the z-score weights steady fields up and variable fields down.
- **A possible mechanism, not tested:** if agreement fields had more variable baselines than their matches, the same NDVI drop in a shock season would be a smaller z drop for them, which would read as a cushion. A balance check on baseline SD would test this.
- The seasonal integral behaves the same way: +0.120 as a z-score, +0.017 (−0.001, +0.035) raw. This explains the 6 November discrepancy.
- **What stands:** the registered H1 reading, as registered, on the registered outcome. **What doesn't:** reading H1 as agreement land holding more of its greenness in absolute or relative terms. No scaling other than the field z-score shows that.

## Limits
- Both checks use the frozen estimator and samples, so the failed H1 placebo, the few-shocks result and trend sensitivity still apply.
- NDVI isn't yield; the harvest index (t/ha) isn't affected by this scaling.
