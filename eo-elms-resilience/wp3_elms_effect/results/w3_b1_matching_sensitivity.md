# W3-B1 matching sensitivity

Protocol: [w3_b1_matching_sensitivity_protocol.md](w3_b1_matching_sensitivity_protocol.md). Labels beside registered results; no registered reading changes. Exploratory. Baseline matching reproduced both saved samples exactly, and the estimates reproduced the published ones.

## Summary

k1 and k2: how many times stronger than the strongest observed factor an unobserved one must be to take the estimate to zero. The label uses the smaller.

| Result | Estimate | S, largest group shift | k1 | Largest δ × γ | k2 | Label | Placebo |
|---|---:|---:|---:|---:|---:|---|---|
| A: H1 July NDVI, frozen | +0.082 | 0.017 | 4.72 | 0.015 | 5.63 | strong | +0.079, fails |
| B: H1 July NDVI, E3 sample | +0.087 | 0.013 | 6.54 | 0.027 | 3.17 | strong | +0.080, fails |
| C: dry or heat harvest, All agreement land | +0.039 | 0.040 | 0.97 | 0.030 | 1.30 | fragile | -0.081, passes narrowly |
| C: dry or heat harvest, Management-only | +0.041 | 0.041 | 1.00 | 0.030 | 1.37 | fragile | -0.095, passes narrowly |
| D: wet-winter harvest, All agreement land | -0.040 | 0.027 | 1.47 | 0.014 | 2.83 | moderate | -0.128, fails |
| D: wet-winter harvest, Management-only | -0.050 | 0.030 | 1.65 | 0.014 | 3.52 | moderate | -0.139, fails |
| D: wet-winter harvest, Buffer strips | -0.068 | 0.018 | 3.76 | 0.019 | 3.60 | strong | -0.162, fails |

## Check 1: shift when a group is left out of the matching

| Result | NDVI trajectory | Crop history | Flood zone | Peat class | Scheme intensity, 1 km | Embedding components | No matching |
|---|---:|---:|---:|---:|---:|---:|---:|
| A: H1 July NDVI, frozen | +0.015 | +0.017 | +0.011 | +0.008 | +0.014 |  | +0.029 |
| B: H1 July NDVI, E3 sample | -0.013 | -0.004 | -0.006 | -0.003 | +0.005 | -0.004 | +0.025 |
| C: dry or heat harvest, All agreement land | -0.004 | -0.007 | -0.000 | -0.002 | -0.006 | -0.040 | -0.070 |
| C: dry or heat harvest, Management-only | -0.004 | -0.007 | -0.000 | -0.002 | -0.007 | -0.041 | -0.069 |
| D: wet-winter harvest, All agreement land | +0.002 | +0.007 | +0.000 | +0.001 | +0.005 | +0.027 | +0.037 |
| D: wet-winter harvest, Management-only | +0.004 | +0.007 | -0.000 | +0.001 | +0.006 | +0.030 | +0.041 |
| D: wet-winter harvest, Buffer strips | -0.001 | +0.006 | +0.000 | -0.001 | +0.004 | +0.018 | +0.028 |

## Check 2: strongest observed covariates

δ before matching, for the result's family; γ per SD in never-treated matched fields, 2021–2025. Marginal slopes, so not additive.

| Result | Largest δ × γ: covariate (δ, γ) | Largest δ: covariate (δ, γ) | Largest γ: covariate (δ, γ) | γ needed at largest δ | δ needed at largest γ | Bias to pass the 0.10 limit |
|---|---|---|---|---:|---:|---:|
| A: H1 July NDVI, frozen | ndvi_p11 (-0.33, +0.044) | scheme_1km (+0.81, +0.003) | crop_2018_AC67 (+0.08, +0.079) | 0.101 | 1.04 | 0.018 |
| B: H1 July NDVI, E3 sample | emb_pc1 (+0.46, +0.059) | scheme_1km (+0.81, -0.003) | emb_pc8 (-0.15, +0.099) | 0.106 | 0.87 | 0.013 |
| C: dry or heat harvest, All agreement land | emb_pc1 (+0.46, -0.064) | scheme_1km (+0.81, +0.025) | emb_pc7 (+0.30, -0.092) | 0.047 | 0.42 | 0.061 |
| C: dry or heat harvest, Management-only | emb_pc1 (+0.47, -0.064) | scheme_1km (+0.87, +0.025) | emb_pc7 (+0.30, -0.092) | 0.047 | 0.45 | 0.059 |
| D: wet-winter harvest, All agreement land | emb_pc1 (+0.46, -0.031) | scheme_1km (+0.81, +0.008) | emb_pc6 (+0.08, +0.058) | 0.049 | 0.69 | 0.060 |
| D: wet-winter harvest, Management-only | emb_pc1 (+0.47, -0.031) | scheme_1km (+0.87, +0.008) | emb_pc6 (+0.07, +0.058) | 0.058 | 0.87 | 0.050 |
| D: wet-winter harvest, Buffer strips | emb_pc1 (+0.62, -0.031) | scheme_1km (+0.88, +0.008) | emb_pc6 (+0.18, +0.058) | 0.077 | 1.17 | 0.032 |

**Check on the method:** embeddings in the frozen sample predicted a shift of -0.0012; the realised change from A to B was +0.0045. Both small, opposite signs, one data point.

## Reading

- **The harvest results depend on the embeddings.** Without them in the matching, dry-or-heat harvest goes from +0.039 to -0.001 on all land and +0.041 to 0.000 on management-only; wet harvest from -0.040 to -0.013. No other group moves any row by more than 0.017.
- **That is what makes dry-or-heat harvest fragile,** both rows just under k = 1 (0.97 and 0.998). The label is close to its boundary, and the substance is not: the embeddings are the difference between a small gain and none.
- **Direction.** Embedding matching removes an imbalance that pushes the harvest contrast down, so this is not evidence against the gain by itself: matching on the embeddings may be correcting a real bias. It does mean that the gain rests on one matching choice.
- **H1 is strong here, and that does not clear it.** H1 barely depends on matching, but its placebo fails at about the size of the estimate (+0.079, +0.080), so differences of the needed size already exist, in a form matching does not remove.
- **Wet buffer strips are strong, wet all land and management-only moderate, all with failed placebos.**
- **Equivalence:** the bias needed to push dry-or-heat harvest past 0.10 t/ha (0.061, 0.059) is about 1.5 times S, so a factor as strong as the strongest observed would not on its own do it, in either direction, from this estimate.
- **Not covered:** the few-shocks spread and HonestDiD are separate. Both checks consider one factor at a time.
