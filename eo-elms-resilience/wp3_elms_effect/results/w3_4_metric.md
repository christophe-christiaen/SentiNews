# W3-4: a placebo-adjusted detection metric

Protocol: [w3_4_metric_protocol.md](w3_4_metric_protocol.md), written before any model. I = AUC(pre + post) − AUC(pre); I₀ = AUC(pre + 2020) − AUC(pre) (2020 is before every entry); I* = I − I₀. G = AUC(post) − AUC(pre) (Paper 3). Comparison A: never-treated land; B: management-only scheme land. Leave-one-region-out; 95% intervals from a paired bootstrap of parcels within held-out regions.

## AlphaEarth

| Family | comp. | AUC pre | AUC post | G | I | I₀ | **I*** (95% CI) | I* range over regions |
|---|---|---|---|---|---|---|---|---|
| Herbal leys | A | 0.70 | 0.86 | +0.158 | +0.161 | +0.010 | **+0.151** (+0.144 to +0.159) | +0.085 to +0.179 |
| Herbal leys | B | 0.65 | 0.83 | +0.185 | +0.191 | +0.009 | **+0.182** (+0.173 to +0.189) | +0.134 to +0.205 |
| Cover crops | A | 0.72 | 0.77 | +0.048 | +0.055 | +0.002 | **+0.052** (+0.048 to +0.057) | +0.035 to +0.069 |
| Cover crops | B | 0.57 | 0.64 | +0.076 | +0.073 | +0.003 | **+0.071** (+0.063 to +0.077) | +0.031 to +0.097 |
| No-till | A | 0.77 | 0.85 | +0.083 | +0.085 | +0.012 | **+0.073** (+0.067 to +0.079) | +0.049 to +0.089 |
| No-till | B | 0.64 | 0.77 | +0.126 | +0.124 | +0.037 | **+0.088** (+0.080 to +0.097) | +0.072 to +0.106 |
| In-field flower and bird-food plots | A | 0.67 | 0.75 | +0.079 | +0.088 | +0.003 | **+0.085** (+0.079 to +0.090) | +0.069 to +0.098 |
| In-field flower and bird-food plots | B | 0.56 | 0.66 | +0.105 | +0.107 | +0.018 | **+0.089** (+0.082 to +0.096) | +0.060 to +0.113 |
| Margins and corners | A | 0.71 | 0.71 | -0.001 | +0.016 | +0.003 | **+0.012** (+0.009 to +0.016) | -0.044 to +0.034 |
| Margins and corners | B | 0.56 | 0.57 | +0.009 | +0.013 | +0.014 | **-0.000** (-0.007 to +0.006) | -0.046 to +0.013 |
| Grassland options | A | 0.65 | 0.75 | +0.097 | +0.106 | +0.005 | **+0.101** (+0.088 to +0.113) | +0.072 to +0.181 |
| Grassland options | B | 0.73 | 0.81 | +0.078 | +0.085 | +0.006 | **+0.078** (+0.067 to +0.089) | +0.058 to +0.106 |
| Buffer strips (control) | A | 0.72 | 0.73 | +0.009 | +0.020 | +0.004 | **+0.016** (+0.013 to +0.020) | +0.000 to +0.020 |
| Buffer strips (control) | B | 0.56 | 0.57 | +0.002 | +0.007 | +0.006 | **+0.001** (-0.004 to +0.007) | -0.025 to +0.008 |
| Management only (control) | A | 0.68 | 0.69 | +0.008 | +0.018 | -0.000 | **+0.018** (+0.014 to +0.023) | +0.011 to +0.035 |

**Reading (AlphaEarth, rules fixed in advance)**

- Calibration (negative controls vs never-treated, I* within ±0.02): Buffer strips (control) +0.016; Management only (control) +0.018 → **valid**.
- Detectable beyond selection (I* 95% CI above 0.02, comparison B): Herbal leys, Cover crops, No-till, In-field flower and bird-food plots, Grassland options.
- Paper 3 rule (AUC ≥ 0.70 and G ≥ 0.10, comparison B): Herbal leys, No-till.
- Selection-invariance (|I*(A) − I*(B)| vs |AUC post(A) − AUC post(B)|): Herbal leys 0.031 vs 0.023; Cover crops 0.018 vs 0.126; No-till 0.015 vs 0.078; In-field flower and bird-food plots 0.004 vs 0.092; Margins and corners 0.013 vs 0.144; Grassland options 0.023 vs 0.058 → **not invariant** for every family.

## Sentinel-2

| Family | comp. | AUC pre | AUC post | G | I | I₀ | **I*** (95% CI) | I* range over regions |
|---|---|---|---|---|---|---|---|---|
| Herbal leys | A | 0.58 | 0.78 | +0.197 | +0.209 | +0.035 | **+0.173** (+0.165 to +0.183) | +0.140 to +0.216 |
| Herbal leys | B | 0.59 | 0.79 | +0.191 | +0.196 | +0.026 | **+0.171** (+0.161 to +0.180) | +0.134 to +0.208 |
| Cover crops | A | 0.65 | 0.70 | +0.045 | +0.053 | +0.015 | **+0.038** (+0.032 to +0.043) | +0.001 to +0.058 |
| Cover crops | B | 0.53 | 0.59 | +0.064 | +0.060 | +0.001 | **+0.059** (+0.051 to +0.067) | +0.031 to +0.093 |
| No-till | A | 0.66 | 0.78 | +0.120 | +0.121 | +0.044 | **+0.077** (+0.068 to +0.086) | -0.035 to +0.092 |
| No-till | B | 0.57 | 0.72 | +0.155 | +0.149 | +0.052 | **+0.097** (+0.087 to +0.106) | +0.065 to +0.146 |
| In-field flower and bird-food plots | A | 0.62 | 0.70 | +0.085 | +0.088 | +0.007 | **+0.081** (+0.075 to +0.087) | +0.056 to +0.099 |
| In-field flower and bird-food plots | B | 0.54 | 0.63 | +0.095 | +0.091 | +0.017 | **+0.075** (+0.068 to +0.082) | +0.047 to +0.093 |
| Margins and corners | A | 0.64 | 0.63 | -0.014 | +0.015 | +0.010 | **+0.006** (+0.001 to +0.011) | -0.020 to +0.021 |
| Margins and corners | B | 0.53 | 0.53 | +0.001 | +0.011 | +0.006 | **+0.005** (-0.001 to +0.013) | -0.017 to +0.043 |
| Grassland options | A | 0.59 | 0.70 | +0.105 | +0.112 | +0.020 | **+0.092** (+0.078 to +0.107) | +0.066 to +0.123 |
| Grassland options | B | 0.69 | 0.78 | +0.086 | +0.093 | +0.028 | **+0.065** (+0.054 to +0.076) | +0.034 to +0.108 |
| Buffer strips (control) | A | 0.65 | 0.63 | -0.013 | +0.014 | +0.016 | **-0.002** (-0.008 to +0.003) | -0.021 to +0.018 |
| Buffer strips (control) | B | 0.53 | 0.52 | -0.003 | +0.006 | +0.007 | **-0.001** (-0.008 to +0.006) | -0.055 to +0.160 |
| Management only (control) | A | 0.63 | 0.63 | +0.005 | +0.016 | +0.009 | **+0.007** (+0.001 to +0.012) | -0.016 to +0.029 |

**Reading (Sentinel-2, rules fixed in advance)**

- Calibration (negative controls vs never-treated, I* within ±0.02): Buffer strips (control) -0.002; Management only (control) +0.007 → **valid**.
- Detectable beyond selection (I* 95% CI above 0.02, comparison B): Herbal leys, Cover crops, No-till, In-field flower and bird-food plots, Grassland options.
- Paper 3 rule (AUC ≥ 0.70 and G ≥ 0.10, comparison B): Herbal leys, No-till.
- Selection-invariance (|I*(A) − I*(B)| vs |AUC post(A) − AUC post(B)|): Herbal leys 0.003 vs 0.009; Cover crops 0.021 vs 0.106; No-till 0.020 vs 0.059; In-field flower and bird-food plots 0.006 vs 0.072; Margins and corners 0.000 vs 0.102; Grassland options 0.027 vs 0.080 → **invariant** (all below 0.03).

