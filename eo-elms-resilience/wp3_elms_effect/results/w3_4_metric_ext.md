# W3-4 addendum: the metric with TESSERA and Presto

Protocol: [w3_4_metric_protocol.md](w3_4_metric_protocol.md) and its addendum of 18 October 2026, written before extraction. Pre-entry record 2018–2019 for both (TESSERA has no 2017); I₀ from 2020 (Presto: season October 2019–September 2020). I = AUC(pre + post) − AUC(pre); I₀ = AUC(pre + 2020) − AUC(pre) (2020 is before every entry); I* = I − I₀. G = AUC(post) − AUC(pre) (Paper 3). Comparison A: never-treated land; B: management-only scheme land. Leave-one-region-out; 95% intervals from a paired bootstrap of parcels within held-out regions.

## TESSERA (pre = 2018–2019)

| Family | comp. | AUC pre | AUC post | G | I | I₀ | **I*** (95% CI) | I* range over regions |
|---|---|---|---|---|---|---|---|---|
| Herbal leys | A | 0.68 | 0.86 | +0.173 | +0.174 | +0.009 | **+0.165** (+0.157 to +0.174) | +0.102 to +0.212 |
| Herbal leys | B | 0.64 | 0.84 | +0.203 | +0.206 | +0.016 | **+0.190** (+0.181 to +0.199) | +0.159 to +0.216 |
| Cover crops | A | 0.70 | 0.77 | +0.073 | +0.080 | +0.011 | **+0.068** (+0.063 to +0.074) | +0.040 to +0.089 |
| Cover crops | B | 0.56 | 0.64 | +0.088 | +0.091 | +0.004 | **+0.087** (+0.080 to +0.094) | +0.050 to +0.143 |
| No-till | A | 0.78 | 0.87 | +0.099 | +0.102 | +0.024 | **+0.079** (+0.072 to +0.084) | +0.068 to +0.107 |
| No-till | B | 0.69 | 0.82 | +0.132 | +0.136 | +0.036 | **+0.100** (+0.092 to +0.107) | +0.077 to +0.166 |
| In-field flower and bird-food plots | A | 0.66 | 0.77 | +0.116 | +0.120 | +0.007 | **+0.113** (+0.107 to +0.119) | +0.096 to +0.125 |
| In-field flower and bird-food plots | B | 0.57 | 0.68 | +0.110 | +0.109 | +0.005 | **+0.104** (+0.097 to +0.111) | +0.094 to +0.124 |
| Margins and corners | A | 0.69 | 0.71 | +0.019 | +0.032 | +0.005 | **+0.027** (+0.022 to +0.032) | -0.013 to +0.041 |
| Margins and corners | B | 0.56 | 0.56 | +0.003 | +0.011 | +0.006 | **+0.005** (-0.001 to +0.011) | -0.021 to +0.045 |
| Grassland options | A | 0.64 | 0.75 | +0.108 | +0.111 | +0.016 | **+0.095** (+0.083 to +0.108) | +0.055 to +0.144 |
| Grassland options | B | 0.72 | 0.81 | +0.093 | +0.097 | +0.015 | **+0.082** (+0.072 to +0.093) | +0.061 to +0.111 |
| Buffer strips (control) | A | 0.69 | 0.71 | +0.024 | +0.031 | +0.011 | **+0.020** (+0.015 to +0.025) | +0.012 to +0.033 |
| Buffer strips (control) | B | 0.55 | 0.56 | +0.007 | +0.010 | -0.000 | **+0.011** (+0.005 to +0.018) | -0.016 to +0.021 |
| Management only (control) | A | 0.66 | 0.69 | +0.035 | +0.041 | +0.006 | **+0.034** (+0.029 to +0.040) | +0.018 to +0.062 |

**Reading (TESSERA, rules fixed in advance)**

- Calibration (negative controls vs never-treated, I* within ±0.02): Buffer strips (control) +0.020; Management only (control) +0.034 → **fails calibration**.
- Detectable beyond selection (I* 95% CI above 0.02, comparison B): Herbal leys, Cover crops, No-till, In-field flower and bird-food plots, Grassland options.
- Paper 3 rule (AUC ≥ 0.70 and G ≥ 0.10, comparison B): Herbal leys, No-till.
- Selection-invariance (|I*(A) − I*(B)| vs |AUC post(A) − AUC post(B)|): Herbal leys 0.025 vs 0.013; Cover crops 0.019 vs 0.128; No-till 0.021 vs 0.057; In-field flower and bird-food plots 0.009 vs 0.095; Margins and corners 0.023 vs 0.144; Grassland options 0.013 vs 0.063 → **invariant** (all below 0.03).

## Presto (seasons October–September; pre = 2018–2019)

| Family | comp. | AUC pre | AUC post | G | I | I₀ | **I*** (95% CI) | I* range over regions |
|---|---|---|---|---|---|---|---|---|
| Herbal leys | A | 0.65 | 0.80 | +0.153 | +0.172 | +0.019 | **+0.152** (+0.144 to +0.161) | +0.115 to +0.193 |
| Herbal leys | B | 0.61 | 0.79 | +0.181 | +0.192 | +0.021 | **+0.171** (+0.163 to +0.181) | +0.139 to +0.213 |
| Cover crops | A | 0.68 | 0.73 | +0.050 | +0.061 | +0.008 | **+0.053** (+0.048 to +0.058) | +0.027 to +0.085 |
| Cover crops | B | 0.55 | 0.60 | +0.058 | +0.060 | +0.003 | **+0.057** (+0.049 to +0.064) | +0.033 to +0.081 |
| No-till | A | 0.72 | 0.81 | +0.091 | +0.099 | +0.025 | **+0.073** (+0.067 to +0.081) | +0.021 to +0.088 |
| No-till | B | 0.64 | 0.75 | +0.115 | +0.126 | +0.035 | **+0.091** (+0.082 to +0.100) | +0.069 to +0.134 |
| In-field flower and bird-food plots | A | 0.63 | 0.71 | +0.075 | +0.088 | +0.005 | **+0.082** (+0.076 to +0.089) | +0.062 to +0.100 |
| In-field flower and bird-food plots | B | 0.55 | 0.63 | +0.087 | +0.084 | +0.012 | **+0.072** (+0.064 to +0.078) | +0.058 to +0.087 |
| Margins and corners | A | 0.66 | 0.67 | +0.004 | +0.019 | +0.004 | **+0.014** (+0.009 to +0.020) | -0.041 to +0.022 |
| Margins and corners | B | 0.53 | 0.54 | +0.012 | +0.015 | +0.006 | **+0.009** (+0.003 to +0.016) | +0.001 to +0.078 |
| Grassland options | A | 0.64 | 0.71 | +0.073 | +0.083 | +0.009 | **+0.074** (+0.061 to +0.086) | +0.034 to +0.142 |
| Grassland options | B | 0.72 | 0.78 | +0.067 | +0.080 | +0.012 | **+0.068** (+0.057 to +0.079) | +0.037 to +0.106 |
| Buffer strips (control) | A | 0.66 | 0.67 | +0.010 | +0.024 | +0.014 | **+0.010** (+0.005 to +0.015) | -0.007 to +0.029 |
| Buffer strips (control) | B | 0.53 | 0.55 | +0.012 | +0.013 | +0.005 | **+0.008** (+0.001 to +0.015) | -0.008 to +0.078 |
| Management only (control) | A | 0.64 | 0.65 | +0.013 | +0.027 | +0.010 | **+0.017** (+0.011 to +0.022) | -0.007 to +0.041 |

**Reading (Presto, rules fixed in advance)**

- Calibration (negative controls vs never-treated, I* within ±0.02): Buffer strips (control) +0.010; Management only (control) +0.017 → **valid**.
- Detectable beyond selection (I* 95% CI above 0.02, comparison B): Herbal leys, Cover crops, No-till, In-field flower and bird-food plots, Grassland options.
- Paper 3 rule (AUC ≥ 0.70 and G ≥ 0.10, comparison B): Herbal leys, No-till.
- Selection-invariance (|I*(A) − I*(B)| vs |AUC post(A) − AUC post(B)|): Herbal leys 0.019 vs 0.012; Cover crops 0.004 vs 0.121; No-till 0.017 vs 0.062; In-field flower and bird-food plots 0.011 vs 0.075; Margins and corners 0.006 vs 0.124; Grassland options 0.006 vs 0.069 → **invariant** (all below 0.03).

