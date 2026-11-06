# W3-B1 resilience indices

Protocol: [w3_b1_resilience_indices_protocol.md](w3_b1_resilience_indices_protocol.md). Exploratory; no registered reading changes. Post-hoc check: [w3_b1_resilience_posthoc.json](w3_b1_resilience_posthoc.json).

**In short: nothing here shows agreements cushioning crop condition over the whole season.** Resistance is under 1% of a field's normal season. The one recovery row that earns its registered labels is mostly a comparison with a wet-winter season, so it can't be read as recovery. The earlier senescence result was a coding error and is gone.

## Results

Contrasts are treated × after entry × hazard, E3 matched sample, deciding version. Rt, Rs, Rc and RRs are in points of a ratio ×100, so Rt and Rs read as percent of the field's 2017–2020 normal. Senescence is in half-months, 1 is about 15 days.

| Index | Hazard | Family | Estimate (95%) | Placebo (95%) | Registered reading | Holm p | Permutation p | Robust to few shocks |
|---|---|---|---:|---:|---|---:|---:|---|
| Rt | Dry or heat | All agreement land | +0.288 (-0.045, +0.622) | -0.248 (-1.183, +0.686) | none indicated | 0.565 | 0.564 | no |
| Senescence date | Dry or heat | All agreement land | +0.005 (-0.017, +0.026) | -0.017 (-0.064, +0.031) | none indicated | 1.000 | 0.655 | no |
| Rt | Dry or heat | Management-only | +0.607 (+0.215, +0.999) | +0.126 (-1.107, +1.359) | cushion indicated | 0.027 | 0.327 | no |
| Senescence date | Dry or heat | Management-only | +0.009 (-0.018, +0.036) | -0.034 (-0.089, +0.021) | none indicated | 1.000 | 0.448 | no |
| Rt | Wet winter | All agreement land | -0.561 (-0.902, -0.220) | -0.866 (-1.602, -0.131) | cost, placebo fails or is missing | 0.015 | 0.189 | no |
| Senescence date | Wet winter | All agreement land | -0.001 (-0.023, +0.021) | -0.037 (-0.071, -0.003) | none indicated | 1.000 | 0.896 | no |
| Rt | Wet winter | Management-only | -0.833 (-1.241, -0.425) | -1.270 (-2.242, -0.299) | cost, placebo fails or is missing | 0.001 | 0.147 | no |
| Senescence date | Wet winter | Management-only | -0.007 (-0.035, +0.020) | -0.065 (-0.106, -0.024) | none indicated | 1.000 | 0.642 | no |
| Rs | Dry or heat | All agreement land | +0.590 (-0.003, +1.182) | +1.548 (-0.533, +3.628) | none indicated | 0.408 | 0.255 | no |
| Rc | Dry or heat | All agreement land | +1.226 (-0.305, +2.757) | +2.979 (-2.567, +8.526) | not labelled alone | 0.582 | 0.511 | no |
| RRs | Dry or heat | All agreement land | +0.942 (-0.115, +2.000) | +2.089 (-2.431, +6.610) | none indicated | 0.565 | 0.332 | no |
| Rs | Dry or heat | Management-only | +1.268 (+0.543, +1.992) | +2.365 (-0.452, +5.181) | cushion indicated | 0.008 | 0.035 | yes |
| Rc | Dry or heat | Management-only | +2.013 (+0.281, +3.746) | +6.762 (-0.615, +14.138) | not labelled alone | 0.205 | 0.340 | no |
| RRs | Dry or heat | Management-only | +1.632 (+0.398, +2.867) | +4.722 (-1.087, +10.532) | cushion indicated | 0.095 | 0.168 | no |

### Not read: recovery after wet winters

As predicted, 85–90% of the weight is on 2025 and 9–14% on 2022, the main dry seasons. Placebos weren't available.

| Index | Family | Estimate (95%) |
|---|---|---:|
| Rs | All agreement land | -0.032 (-0.504, +0.441) |
| Rc | All agreement land | +0.922 (-0.311, +2.156) |
| RRs | All agreement land | +0.485 (-0.307, +1.278) |
| Rs | Management-only | -0.175 (-0.729, +0.378) |
| Rc | Management-only | +0.850 (-0.585, +2.285) |
| RRs | Management-only | +0.440 (-0.501, +1.382) |

### Beside the deciding version

| Index | Hazard | Family | Other seasons and strata | X2 sample, no embeddings | X with 6 of 8 half-months | Date exists, points |
|---|---|---|---:|---:|---:|---:|
| Rt | Dry or heat | All agreement land | +0.019 (-0.355, +0.394) | +0.182 (-0.144, +0.509) | +0.176 (-0.225, +0.578) | n/a |
| Senescence date | Dry or heat | All agreement land | +0.039 (+0.013, +0.065) | +0.005 (-0.017, +0.026) | n/a | +0.039 (-0.607, +0.685) |
| Rt | Dry or heat | Management-only | +0.164 (-0.282, +0.610) | +0.496 (+0.108, +0.885) | +0.355 (-0.136, +0.847) | n/a |
| Senescence date | Dry or heat | Management-only | +0.041 (+0.008, +0.074) | +0.009 (-0.018, +0.036) | n/a | +0.062 (-0.695, +0.819) |
| Rt | Wet winter | All agreement land | -0.146 (-0.526, +0.235) | -0.546 (-0.885, -0.206) | -0.568 (-1.004, -0.132) | n/a |
| Senescence date | Wet winter | All agreement land | +0.030 (+0.007, +0.054) | -0.004 (-0.026, +0.018) | n/a | +0.121 (-0.527, +0.769) |
| Rt | Wet winter | Management-only | -0.351 (-0.792, +0.090) | -0.808 (-1.211, -0.406) | -0.680 (-1.218, -0.142) | n/a |
| Senescence date | Wet winter | Management-only | +0.030 (+0.003, +0.057) | -0.009 (-0.037, +0.018) | n/a | +0.272 (-0.497, +1.042) |
| Rs | Dry or heat | All agreement land | +0.717 (+0.236, +1.198) | +0.746 (+0.152, +1.339) | +0.501 (-0.232, +1.233) | n/a |
| Rc | Dry or heat | All agreement land | +1.145 (-0.220, +2.510) | +1.297 (-0.239, +2.834) | +1.461 (-0.958, +3.880) | n/a |
| RRs | Dry or heat | All agreement land | +1.013 (+0.105, +1.921) | +1.114 (+0.052, +2.175) | +1.299 (-0.232, +2.830) | n/a |
| Rs | Dry or heat | Management-only | +1.060 (+0.460, +1.660) | +1.420 (+0.695, +2.145) | +1.104 (+0.157, +2.050) | n/a |
| Rc | Dry or heat | Management-only | +1.055 (-0.544, +2.654) | +1.973 (+0.231, +3.716) | +2.289 (-0.411, +4.989) | n/a |
| RRs | Dry or heat | Management-only | +1.041 (-0.074, +2.156) | +1.734 (+0.494, +2.974) | +2.027 (+0.171, +3.884) | n/a |

## Reading

- **Resistance:** dry or heat, all land, +0.29% of normal, interval includes zero. Management-only +0.61% gets the registered "cushion indicated", but it isn't robust to few shocks (permutation p 0.327) and falls to +0.16% in the 2017–2026 version without crop strata. Wet-winter rows read below zero, but their placebos fail, so no cost is read.
- **Recovery rests on few seasons.** 2026 carries about 1.5% of the weight, because it is mostly a shock season itself. The protocol's reason for adding 2026 did not hold: **recovery from the 2025 shock isn't measured here.** Recovery after dry or heat is mainly 2023 (61% all land), with 2021 and 2024 next.
- **The management-only Rs row, +1.27 (+0.54, +1.99), meets its registered labels: cushion indicated, Holm 0.008, permutation 0.035, robust to few shocks. It should not be read as recovery.** The post-hoc check, specified after seeing this, shows the calm-after-calm side is 91% season 2024, and 92% of that side is in wet-shock cells, against 38% on the other side. Agreement land does worse in wet seasons, so the contrast largely picks up that. Without 2024: +0.652 (-1.064, +2.368). Without wet-shock cells on both sides: +0.425 (-1.350, +2.201). All land likewise: without 2024 -0.659 (-1.995, +0.678). Its placebo (+2.36) is also larger than the estimate and passes only by being wide. Season clustering understates uncertainty when one season dominates (W3-B1 section 1). Frozen H2 uses the same contrast on its own sample and seasons, so it may share this weighting; that hasn't been checked.
- **RRs management-only,** +1.63, is labelled "cushion indicated" by the same rule, with the same problem, and is not robust to few shocks. **Rc** is not labelled alone.
- **Senescence date: no shift in shock seasons,** with intervals within ±0.04 half-months, about half a day, in the deciding version, on the 39–74% of field-seasons with a date from 2018. No selection flag. The 2017–2026 version without crop strata gives +0.03 to +0.04 half-months, under a day, so crop mix may matter here.
- **Not settled:** the ratio Rt on X2's sample is +0.18% (−0.14, +0.51), while the earlier z-score of the seasonal integral was +0.120 SD (+0.049, +0.191). Definitions differ (gap-filling, ratio against z-score, whose SD comes from 2–4 seasons with a floor of 0.02). This wasn't tested. H1 uses a z-score too, so **whether H1 depends on that scaling is worth a registered check.**
- **Limits:** NDVI ratios aren't yield. Coverage is uneven: X is usable for 38% of 2017 and 71% of 2023. The fixed normal mixes crops; crop strata cover only season t. The placebo seasons 2017–2020 overlap the normal.

## Correction: exploratory senescence row in wp3_results.md

The old row averaged the −1 "no date" code (12%–49% of field-seasons by year) as dates. Reproduced before correcting: -0.172 (-0.237, -0.108). **Corrected, same sample, strata and discrete definition: -0.012 (-0.034, +0.011) half-months.** So the apparent earlier senescence came from the coding. The seasonal integral row reproduced at +0.120 (+0.049, +0.191); it isn't affected. `wp3_did.load()` is fixed.
