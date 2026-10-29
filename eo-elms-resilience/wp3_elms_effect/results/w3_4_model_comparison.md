# W3-4 model comparison: which AI embedding sees which option, and does any beat the plain indices?

Protocol: [w3_4_model_comparison_protocol.md](w3_4_model_comparison_protocol.md), written 29 October 2026 before any rerun result was read. Three AI embeddings (AlphaEarth, TESSERA, Presto) and one no-AI baseline (plain Sentinel-2 vegetation indices, the kind of satellite data the embeddings are learned from). Common years: pre = 2018–2019, I₀ = 2020, post = 2025 (Presto: farm seasons). I* = selection-corrected detection; options against management-only scheme land, controls against never-treated land. Paired bootstrap (1,000), Holm over all 36 tests.

## Selection-corrected detection I* (95% interval)

| Option | AlphaEarth (AI) | TESSERA (AI) | Presto (AI) | Sentinel-2 indices (no AI, baseline) | verdict (rule fixed in advance) |
|---|---|---|---|---|---|
| Herbal leys | +0.186 (+0.177 to +0.194) | +0.190 (+0.181 to +0.199) | +0.171 (+0.163 to +0.180) | +0.171 (+0.162 to +0.181) | no single best; leading group: AlphaEarth (AI), TESSERA (AI) |
| Cover crops | +0.072 (+0.066 to +0.079) | +0.087 (+0.080 to +0.094) | +0.057 (+0.050 to +0.064) | +0.054 (+0.046 to +0.061) | best suited: TESSERA (AI) |
| No-till | +0.098 (+0.090 to +0.107) | +0.100 (+0.092 to +0.107) | +0.091 (+0.083 to +0.099) | +0.091 (+0.082 to +0.100) | no single best; leading group: AlphaEarth (AI), Sentinel-2 indices (no AI, baseline), TESSERA (AI), Presto (AI) |
| In-field flower and bird-food plots | +0.085 (+0.079 to +0.093) | +0.104 (+0.096 to +0.111) | +0.072 (+0.065 to +0.079) | +0.076 (+0.068 to +0.083) | best suited: TESSERA (AI) |
| Margins and corners | +0.005 (-0.001 to +0.011) | +0.005 (-0.002 to +0.011) | +0.009 (+0.002 to +0.015) | +0.012 (+0.004 to +0.019) | not detectable by any model |
| Grassland options | +0.077 (+0.067 to +0.087) | +0.082 (+0.072 to +0.093) | +0.068 (+0.057 to +0.079) | +0.069 (+0.057 to +0.081) | no single best; leading group: AlphaEarth (AI), Sentinel-2 indices (no AI, baseline), TESSERA (AI), Presto (AI) |
| Buffer strips (control) | +0.019 (+0.015 to +0.023) | +0.020 (+0.015 to +0.024) | +0.010 (+0.005 to +0.015) | -0.001 (-0.007 to +0.004) | control (reported, not tested) |
| Management only (control) | +0.015 (+0.011 to +0.019) | +0.034 (+0.029 to +0.040) | +0.017 (+0.011 to +0.022) | +0.005 (-0.001 to +0.011) | control (reported, not tested) |

## Question 1: which AI embedding suits which option (AI vs AI)

| Option | pair | difference in I* (95% CI) | p (Holm, over 36) |
|---|---|---|---|
| Herbal leys | AlphaEarth (AI) vs TESSERA (AI) | -0.004 (-0.012 to +0.004) | 1 |
| Herbal leys | AlphaEarth (AI) vs Presto (AI) | +0.014 (+0.006 to +0.023) | 0.052 |
| Herbal leys | TESSERA (AI) vs Presto (AI) | +0.019 (+0.010 to +0.027) | 0 |
| Cover crops | AlphaEarth (AI) vs TESSERA (AI) | -0.015 (-0.022 to -0.006) | 0 |
| Cover crops | AlphaEarth (AI) vs Presto (AI) | +0.016 (+0.008 to +0.024) | 0.1 |
| Cover crops | TESSERA (AI) vs Presto (AI) | +0.031 (+0.022 to +0.039) | 0 |
| No-till | AlphaEarth (AI) vs TESSERA (AI) | -0.001 (-0.010 to +0.008) | 1 |
| No-till | AlphaEarth (AI) vs Presto (AI) | +0.008 (-0.002 to +0.018) | 1 |
| No-till | TESSERA (AI) vs Presto (AI) | +0.009 (-0.001 to +0.017) | 1 |
| In-field flower and bird-food plots | AlphaEarth (AI) vs TESSERA (AI) | -0.018 (-0.026 to -0.011) | 0 |
| In-field flower and bird-food plots | AlphaEarth (AI) vs Presto (AI) | +0.014 (+0.006 to +0.022) | 0 |
| In-field flower and bird-food plots | TESSERA (AI) vs Presto (AI) | +0.032 (+0.025 to +0.039) | 0 |
| Margins and corners | AlphaEarth (AI) vs TESSERA (AI) | +0.001 (-0.008 to +0.008) | 1 |
| Margins and corners | AlphaEarth (AI) vs Presto (AI) | -0.003 (-0.012 to +0.005) | 1 |
| Margins and corners | TESSERA (AI) vs Presto (AI) | -0.004 (-0.012 to +0.004) | 1 |
| Grassland options | AlphaEarth (AI) vs TESSERA (AI) | -0.005 (-0.016 to +0.006) | 1 |
| Grassland options | AlphaEarth (AI) vs Presto (AI) | +0.009 (-0.002 to +0.020) | 1 |
| Grassland options | TESSERA (AI) vs Presto (AI) | +0.014 (+0.004 to +0.025) | 0.368 |

## Question 2: does an AI embedding beat the plain indices (AI vs no-AI baseline)

| Option | pair | difference in I* (95% CI) | p (Holm, over 36) |
|---|---|---|---|
| Herbal leys | AlphaEarth (AI) vs Sentinel-2 indices (no AI, baseline) | +0.015 (+0.006 to +0.024) | 0.1 |
| Herbal leys | TESSERA (AI) vs Sentinel-2 indices (no AI, baseline) | +0.019 (+0.010 to +0.028) | 0 |
| Herbal leys | Presto (AI) vs Sentinel-2 indices (no AI, baseline) | +0.000 (-0.008 to +0.010) | 1 |
| Cover crops | AlphaEarth (AI) vs Sentinel-2 indices (no AI, baseline) | +0.019 (+0.009 to +0.028) | 0 |
| Cover crops | TESSERA (AI) vs Sentinel-2 indices (no AI, baseline) | +0.034 (+0.024 to +0.044) | 0 |
| Cover crops | Presto (AI) vs Sentinel-2 indices (no AI, baseline) | +0.003 (-0.007 to +0.012) | 1 |
| No-till | AlphaEarth (AI) vs Sentinel-2 indices (no AI, baseline) | +0.007 (-0.003 to +0.018) | 1 |
| No-till | TESSERA (AI) vs Sentinel-2 indices (no AI, baseline) | +0.008 (-0.001 to +0.018) | 1 |
| No-till | Presto (AI) vs Sentinel-2 indices (no AI, baseline) | -0.000 (-0.011 to +0.010) | 1 |
| In-field flower and bird-food plots | AlphaEarth (AI) vs Sentinel-2 indices (no AI, baseline) | +0.010 (+0.001 to +0.018) | 0.528 |
| In-field flower and bird-food plots | TESSERA (AI) vs Sentinel-2 indices (no AI, baseline) | +0.028 (+0.020 to +0.036) | 0 |
| In-field flower and bird-food plots | Presto (AI) vs Sentinel-2 indices (no AI, baseline) | -0.004 (-0.012 to +0.004) | 1 |
| Margins and corners | AlphaEarth (AI) vs Sentinel-2 indices (no AI, baseline) | -0.006 (-0.015 to +0.002) | 1 |
| Margins and corners | TESSERA (AI) vs Sentinel-2 indices (no AI, baseline) | -0.007 (-0.015 to +0.002) | 1 |
| Margins and corners | Presto (AI) vs Sentinel-2 indices (no AI, baseline) | -0.003 (-0.012 to +0.007) | 1 |
| Grassland options | AlphaEarth (AI) vs Sentinel-2 indices (no AI, baseline) | +0.008 (-0.005 to +0.021) | 1 |
| Grassland options | TESSERA (AI) vs Sentinel-2 indices (no AI, baseline) | +0.013 (+0.001 to +0.027) | 0.84 |
| Grassland options | Presto (AI) vs Sentinel-2 indices (no AI, baseline) | -0.001 (-0.013 to +0.011) | 1 |

## How well a single field can be classified: AUC with the 2025 record (descriptive)

| Option | AlphaEarth (AI) | TESSERA (AI) | Presto (AI) | Sentinel-2 indices (no AI, baseline) |
|---|---|---|---|---|
| Herbal leys | 0.83 | 0.84 | 0.79 | 0.79 |
| Cover crops | 0.64 | 0.64 | 0.60 | 0.59 |
| No-till | 0.77 | 0.82 | 0.75 | 0.72 |
| In-field flower and bird-food plots | 0.66 | 0.68 | 0.63 | 0.63 |
| Margins and corners | 0.57 | 0.56 | 0.54 | 0.53 |
| Grassland options | 0.81 | 0.81 | 0.78 | 0.78 |
| Buffer strips (control) | 0.73 | 0.71 | 0.67 | 0.63 |
| Management only (control) | 0.69 | 0.69 | 0.65 | 0.63 |
