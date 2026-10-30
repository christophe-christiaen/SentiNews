# W3-4 seasonal cover-crop test: a winter view of winter cover crops

Protocol: [w3_4_cover_seasonal_protocol.md](w3_4_cover_seasonal_protocol.md), written before any winter feature, winter embedding or season-2026 input existed. Winter = December–February. I* = [AUC(pre + post) − AUC(pre)] − [AUC(pre + 2020) − AUC(pre)]; pre = winters/seasons 2018–2019; 95% intervals from 1,000 paired bootstrap resamples within held-out regions.

## Primary · post 2026

| Family | comparison | n | Presto, full season (AI) | Presto, winter (AI) | Winter radar and optical (no AI) | Winter radar only (no AI) |
|---|---|---|---|---|---|---|
| Winter cover | B | 30,000 | +0.120 (+0.113 to +0.127) | +0.068 (+0.060 to +0.076) | +0.083 (+0.074 to +0.091) | +0.077 (+0.069 to +0.086) |
| Winter cover | A | 30,000 | +0.089 (+0.083 to +0.095) | +0.049 (+0.043 to +0.055) | +0.077 (+0.070 to +0.084) | +0.072 (+0.065 to +0.080) |
| Spring- and summer-sown cover | B | 10,464 | +0.095 (+0.083 to +0.107) | +0.032 (+0.020 to +0.044) | +0.062 (+0.047 to +0.076) | +0.063 (+0.049 to +0.077) |
| Buffer strips (control) | A | 30,000 | +0.016 (+0.011 to +0.021) | +0.007 (+0.001 to +0.012) | +0.019 (+0.013 to +0.026) | +0.024 (+0.018 to +0.031) |
| Management only (control) | A | 30,000 | +0.019 (+0.013 to +0.024) | +0.006 (+0.000 to +0.011) | +0.024 (+0.017 to +0.030) | +0.020 (+0.013 to +0.027) |

| Version | controls vs never-treated | calibration (±0.02) | |I*(A) − I*(B)| | selection-invariant (< 0.03) | winter cover detected |
|---|---|---|---|---|---|
| Presto, full season (AI) | +0.016, +0.019 | pass | 0.031 | **no** | yes |
| Presto, winter (AI) | +0.007, +0.006 | pass | 0.019 | yes | yes |
| Winter radar and optical (no AI) | +0.019, +0.024 | **fail** | 0.006 | yes | yes |
| Winter radar only (no AI) | +0.024, +0.020 | **fail** | 0.005 | yes | yes |

| Test | difference in I* | 95% interval | p | Holm p | reading |
|---|---|---|---|---|---|
| T-a: Presto, winter (AI) − Presto, full season (AI) | -0.052 | -0.061 to -0.044 | 0 | 0 | V2 worse (not established: the leading version fails a validity check) |
| T-b: Presto, winter (AI) − Winter radar and optical (no AI) | -0.015 | -0.024 to -0.006 | 0 | 0 | V2 worse (not established: the leading version fails a validity check) |
| T-c: Winter radar and optical (no AI) − Presto, full season (AI) | -0.037 | -0.047 to -0.028 | 0 | 0 | V3 worse (not established: the leading version fails a validity check) |
| T-d: Winter radar only (no AI) − Winter radar and optical (no AI) | -0.006 | -0.013 to +0.002 | 0.14 | 0.14 | radar alone is enough |

## Secondary · post 2025

| Family | comparison | n | Presto, full season (AI) | Presto, winter (AI) | Winter radar and optical (no AI) | Winter radar only (no AI) |
|---|---|---|---|---|---|---|
| Winter cover | B | 30,000 | +0.057 (+0.049 to +0.064) | +0.011 (+0.004 to +0.017) | +0.021 (+0.013 to +0.029) | +0.032 (+0.024 to +0.040) |
| Winter cover | A | 30,000 | +0.058 (+0.053 to +0.063) | +0.022 (+0.016 to +0.027) | +0.037 (+0.030 to +0.044) | +0.040 (+0.033 to +0.048) |
| Spring- and summer-sown cover | B | 10,464 | +0.059 (+0.047 to +0.071) | +0.013 (+0.000 to +0.024) | +0.026 (+0.014 to +0.040) | +0.035 (+0.022 to +0.048) |
| Buffer strips (control) | A | 30,000 | +0.010 (+0.005 to +0.015) | +0.006 (+0.001 to +0.011) | +0.009 (+0.003 to +0.016) | +0.009 (+0.003 to +0.015) |
| Management only (control) | A | 30,000 | +0.017 (+0.011 to +0.023) | +0.001 (-0.005 to +0.007) | +0.013 (+0.007 to +0.020) | +0.016 (+0.009 to +0.023) |

| Version | controls vs never-treated | calibration (±0.02) | |I*(A) − I*(B)| | selection-invariant (< 0.03) | winter cover detected |
|---|---|---|---|---|---|
| Presto, full season (AI) | +0.010, +0.017 | pass | 0.001 | yes | yes |
| Presto, winter (AI) | +0.006, +0.001 | pass | 0.011 | yes | no |
| Winter radar and optical (no AI) | +0.009, +0.013 | pass | 0.016 | yes | no |
| Winter radar only (no AI) | +0.009, +0.016 | pass | 0.009 | yes | yes |

| Test | difference in I* | 95% interval | p | Holm p | reading |
|---|---|---|---|---|---|
| T-a: Presto, winter (AI) − Presto, full season (AI) | -0.046 | -0.055 to -0.038 | 0 | 0 | V2 worse |
| T-b: Presto, winter (AI) − Winter radar and optical (no AI) | -0.010 | -0.020 to -0.002 | 0.018 | 0.018 | V2 worse |
| T-c: Winter radar and optical (no AI) − Presto, full season (AI) | -0.036 | -0.045 to -0.026 | 0 | 0 | V3 worse |
| T-d: Winter radar only (no AI) − Winter radar and optical (no AI) | +0.011 | +0.002 to +0.018 | 0.004 | 0.008 | radar alone is enough |

## Secondary · post 2025 · spring crops 2025

| Family | comparison | n | Presto, full season (AI) | Presto, winter (AI) | Winter radar and optical (no AI) | Winter radar only (no AI) |
|---|---|---|---|---|---|---|
| Winter cover | B | 8,938 | +0.072 (+0.058 to +0.086) | +0.047 (+0.033 to +0.060) | +0.054 (+0.038 to +0.068) | +0.045 (+0.031 to +0.061) |
| Winter cover | A | 8,938 | +0.071 (+0.060 to +0.082) | +0.062 (+0.050 to +0.073) | +0.070 (+0.057 to +0.085) | +0.064 (+0.052 to +0.079) |
| Spring- and summer-sown cover | B | 1,624 | +0.110 (+0.078 to +0.141) | +0.050 (+0.019 to +0.081) | +0.058 (+0.024 to +0.090) | +0.007 (-0.024 to +0.039) |
| Buffer strips (control) | A | 16,780 | +0.014 (+0.007 to +0.022) | +0.006 (-0.001 to +0.012) | +0.012 (+0.003 to +0.021) | +0.022 (+0.014 to +0.031) |
| Management only (control) | A | 29,887 | +0.012 (+0.007 to +0.019) | +0.010 (+0.005 to +0.016) | +0.012 (+0.005 to +0.019) | +0.025 (+0.018 to +0.032) |

| Version | controls vs never-treated | calibration (±0.02) | |I*(A) − I*(B)| | selection-invariant (< 0.03) | winter cover detected |
|---|---|---|---|---|---|
| Presto, full season (AI) | +0.014, +0.012 | pass | 0.001 | yes | yes |
| Presto, winter (AI) | +0.006, +0.010 | pass | 0.015 | yes | yes |
| Winter radar and optical (no AI) | +0.012, +0.012 | pass | 0.016 | yes | yes |
| Winter radar only (no AI) | +0.022, +0.025 | **fail** | 0.019 | yes | yes |

| Test | difference in I* | 95% interval | p | Holm p | reading |
|---|---|---|---|---|---|
| T-a: Presto, winter (AI) − Presto, full season (AI) | -0.026 | -0.043 to -0.008 | 0.002 | 0.008 | V2 worse |
| T-b: Presto, winter (AI) − Winter radar and optical (no AI) | -0.007 | -0.025 to +0.011 | 0.424 | 0.548 | no difference shown |
| T-c: Winter radar and optical (no AI) − Presto, full season (AI) | -0.018 | -0.036 to -0.000 | 0.046 | 0.138 | no difference shown |
| T-d: Winter radar only (no AI) − Winter radar and optical (no AI) | -0.009 | -0.025 to +0.008 | 0.274 | 0.548 | inconclusive |

Primary reading = the first section (post winter 2025/26, all cereal land, comparison B). The other sections are secondary and do not change it. Spring-sown crops = 13 CROME codes listed in the protocol. Labels are declared, not verified.
