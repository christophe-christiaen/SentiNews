# W3-4: a placebo-adjusted detection metric

> **Deviation D1 (1 November 2026):** comparison A (never-treated) with parcels found in older Natural England option snapshots removed. Registered results: [w3_4_metric.md](w3_4_metric.md). Comparison B is unchanged.

Protocol: [w3_4_metric_protocol.md](w3_4_metric_protocol.md), written before any model. I = AUC(pre + post) − AUC(pre); I₀ = AUC(pre + 2020) − AUC(pre) (2020 is before every entry); I* = I − I₀. G = AUC(post) − AUC(pre) (Paper 3). Comparison A: never-treated land; B: management-only scheme land. Leave-one-region-out; 95% intervals from a paired bootstrap of parcels within held-out regions.

## AlphaEarth

| Family | comp. | AUC pre | AUC post | G | I | I₀ | **I*** (95% CI) | I* range over regions |
|---|---|---|---|---|---|---|---|---|
| Herbal leys | A | 0.72 | 0.86 | +0.141 | +0.145 | +0.002 | **+0.142** (+0.135 to +0.149) | +0.071 to +0.158 |
| Herbal leys | B | 0.65 | 0.83 | +0.185 | +0.191 | +0.009 | **+0.182** (+0.173 to +0.189) | +0.134 to +0.205 |
| Cover crops | A | 0.73 | 0.78 | +0.047 | +0.057 | +0.006 | **+0.051** (+0.047 to +0.055) | +0.030 to +0.071 |
| Cover crops | B | 0.57 | 0.64 | +0.076 | +0.073 | +0.003 | **+0.071** (+0.063 to +0.077) | +0.031 to +0.097 |
| No-till | A | 0.78 | 0.86 | +0.082 | +0.086 | +0.019 | **+0.068** (+0.062 to +0.073) | +0.048 to +0.074 |
| No-till | B | 0.64 | 0.77 | +0.126 | +0.124 | +0.037 | **+0.088** (+0.080 to +0.097) | +0.072 to +0.106 |
| In-field flower and bird-food plots | A | 0.69 | 0.77 | +0.080 | +0.092 | +0.006 | **+0.085** (+0.080 to +0.091) | +0.072 to +0.133 |
| In-field flower and bird-food plots | B | 0.56 | 0.66 | +0.105 | +0.107 | +0.018 | **+0.089** (+0.082 to +0.096) | +0.060 to +0.113 |
| Margins and corners | A | 0.73 | 0.73 | +0.002 | +0.015 | +0.004 | **+0.010** (+0.007 to +0.014) | -0.003 to +0.027 |
| Margins and corners | B | 0.56 | 0.57 | +0.009 | +0.013 | +0.014 | **-0.000** (-0.007 to +0.006) | -0.046 to +0.013 |
| Grassland options | A | 0.65 | 0.74 | +0.090 | +0.098 | +0.010 | **+0.089** (+0.077 to +0.100) | +0.059 to +0.125 |
| Grassland options | B | 0.73 | 0.81 | +0.078 | +0.085 | +0.006 | **+0.078** (+0.067 to +0.089) | +0.058 to +0.106 |
| Buffer strips (control) | A | 0.74 | 0.74 | +0.004 | +0.016 | +0.003 | **+0.014** (+0.010 to +0.017) | +0.000 to +0.027 |
| Buffer strips (control) | B | 0.56 | 0.57 | +0.002 | +0.007 | +0.006 | **+0.001** (-0.004 to +0.007) | -0.025 to +0.008 |
| Management only (control) | A | 0.70 | 0.71 | +0.008 | +0.018 | +0.001 | **+0.017** (+0.013 to +0.021) | +0.011 to +0.026 |

**Reading (AlphaEarth, rules fixed in advance)**

- Calibration (negative controls vs never-treated, I* within ±0.02): Buffer strips (control) +0.014; Management only (control) +0.017 → **valid**.
- Detectable beyond selection (I* 95% CI above 0.02, comparison B): Herbal leys, Cover crops, No-till, In-field flower and bird-food plots, Grassland options.
- Paper 3 rule (AUC ≥ 0.70 and G ≥ 0.10, comparison B): Herbal leys, No-till.
- Selection-invariance (|I*(A) − I*(B)| vs |AUC post(A) − AUC post(B)|): Herbal leys 0.040 vs 0.024; Cover crops 0.020 vs 0.140; No-till 0.020 vs 0.090; In-field flower and bird-food plots 0.004 vs 0.107; Margins and corners 0.011 vs 0.166; Grassland options 0.010 vs 0.065 → **not invariant** for every family.

## Sentinel-2

| Family | comp. | AUC pre | AUC post | G | I | I₀ | **I*** (95% CI) | I* range over regions |
|---|---|---|---|---|---|---|---|---|
| Herbal leys | A | 0.59 | 0.78 | +0.188 | +0.203 | +0.037 | **+0.166** (+0.157 to +0.175) | +0.116 to +0.191 |
| Herbal leys | B | 0.59 | 0.79 | +0.191 | +0.196 | +0.026 | **+0.171** (+0.161 to +0.180) | +0.134 to +0.208 |
| Cover crops | A | 0.67 | 0.70 | +0.035 | +0.050 | +0.014 | **+0.036** (+0.030 to +0.042) | +0.022 to +0.060 |
| Cover crops | B | 0.53 | 0.59 | +0.064 | +0.060 | +0.001 | **+0.059** (+0.051 to +0.067) | +0.031 to +0.093 |
| No-till | A | 0.68 | 0.79 | +0.108 | +0.118 | +0.044 | **+0.074** (+0.067 to +0.082) | +0.011 to +0.080 |
| No-till | B | 0.57 | 0.72 | +0.155 | +0.149 | +0.052 | **+0.097** (+0.087 to +0.106) | +0.065 to +0.146 |
| In-field flower and bird-food plots | A | 0.63 | 0.71 | +0.075 | +0.083 | +0.009 | **+0.074** (+0.068 to +0.080) | +0.039 to +0.089 |
| In-field flower and bird-food plots | B | 0.54 | 0.63 | +0.095 | +0.091 | +0.017 | **+0.075** (+0.068 to +0.082) | +0.047 to +0.093 |
| Margins and corners | A | 0.66 | 0.64 | -0.023 | +0.013 | +0.006 | **+0.006** (+0.001 to +0.012) | -0.020 to +0.015 |
| Margins and corners | B | 0.53 | 0.53 | +0.001 | +0.011 | +0.006 | **+0.005** (-0.001 to +0.013) | -0.017 to +0.043 |
| Grassland options | A | 0.59 | 0.69 | +0.102 | +0.105 | +0.014 | **+0.091** (+0.077 to +0.106) | +0.060 to +0.140 |
| Grassland options | B | 0.69 | 0.78 | +0.086 | +0.093 | +0.028 | **+0.065** (+0.054 to +0.076) | +0.034 to +0.108 |
| Buffer strips (control) | A | 0.66 | 0.64 | -0.019 | +0.012 | +0.012 | **-0.001** (-0.006 to +0.004) | -0.030 to +0.020 |
| Buffer strips (control) | B | 0.53 | 0.52 | -0.003 | +0.006 | +0.007 | **-0.001** (-0.008 to +0.006) | -0.055 to +0.160 |
| Management only (control) | A | 0.64 | 0.64 | +0.000 | +0.017 | +0.006 | **+0.011** (+0.005 to +0.016) | -0.011 to +0.029 |

**Reading (Sentinel-2, rules fixed in advance)**

- Calibration (negative controls vs never-treated, I* within ±0.02): Buffer strips (control) -0.001; Management only (control) +0.011 → **valid**.
- Detectable beyond selection (I* 95% CI above 0.02, comparison B): Herbal leys, Cover crops, No-till, In-field flower and bird-food plots, Grassland options.
- Paper 3 rule (AUC ≥ 0.70 and G ≥ 0.10, comparison B): Herbal leys, No-till.
- Selection-invariance (|I*(A) − I*(B)| vs |AUC post(A) − AUC post(B)|): Herbal leys 0.005 vs 0.009; Cover crops 0.023 vs 0.111; No-till 0.023 vs 0.066; In-field flower and bird-food plots 0.001 vs 0.077; Margins and corners 0.001 vs 0.109; Grassland options 0.026 vs 0.084 → **invariant** (all below 0.03).

