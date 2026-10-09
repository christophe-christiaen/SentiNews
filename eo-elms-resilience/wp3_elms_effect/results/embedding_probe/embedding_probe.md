# Embedding demo: first probes (6 sites, 2019 and 2025)

Leave-one-site-out linear probes on frozen embeddings. Labels are declared SFI actions from the live layers.

| Task | Model | Year | n (pos / neg) | AUC | Balanced acc. |
|---|---|---|---|---|---|
| Grassland vs arable SFI land | AlphaEarth (20 m, 64-d) | 2019 | 753 / 547 | 0.921 | 0.888 |
| Herbal leys vs arable SFI land | AlphaEarth (20 m, 64-d) | 2019 | 388 / 546 | 0.9 | 0.846 |
| Herbal leys vs other grassland SFI land | AlphaEarth (20 m, 64-d) | 2019 | 394 / 758 | 0.572 | 0.548 |
| Scheme parcels vs random pixels | AlphaEarth (20 m, 64-d) | 2019 | 3912 / 2981 | 0.639 | 0.6 |
| Grassland vs arable SFI land | AlphaEarth (20 m, 64-d) | 2025 | 753 / 547 | 0.969 | 0.925 |
| Herbal leys vs arable SFI land | AlphaEarth (20 m, 64-d) | 2025 | 388 / 546 | 0.944 | 0.91 |
| Herbal leys vs other grassland SFI land | AlphaEarth (20 m, 64-d) | 2025 | 394 / 758 | 0.617 | 0.571 |
| Scheme parcels vs random pixels | AlphaEarth (20 m, 64-d) | 2025 | 3912 / 2982 | 0.657 | 0.617 |
| Grassland vs arable SFI land | TESSERA (10 m, 128-d) | 2019 | 748 / 544 | 0.931 | 0.881 |
| Herbal leys vs arable SFI land | TESSERA (10 m, 128-d) | 2019 | 385 / 543 | 0.888 | 0.819 |
| Herbal leys vs other grassland SFI land | TESSERA (10 m, 128-d) | 2019 | 391 / 753 | 0.581 | 0.572 |
| Scheme parcels vs random pixels | TESSERA (10 m, 128-d) | 2019 | 3895 / 2951 | 0.635 | 0.597 |
| Grassland vs arable SFI land | TESSERA (10 m, 128-d) | 2025 | 757 / 550 | 0.941 | 0.902 |
| Herbal leys vs arable SFI land | TESSERA (10 m, 128-d) | 2025 | 388 / 549 | 0.93 | 0.902 |
| Herbal leys vs other grassland SFI land | TESSERA (10 m, 128-d) | 2025 | 394 / 762 | 0.583 | 0.563 |
| Scheme parcels vs random pixels | TESSERA (10 m, 128-d) | 2025 | 3931 / 3000 | 0.651 | 0.61 |

## 2019 → 2025 change (cosine distance), mean by group

| Group | AlphaEarth (20 m, 64-d) | TESSERA (10 m, 128-d) |
|---|---|---|
| Arable actions | 0.113 (n=949) | 0.278 (n=941) |
| CS options (2021-25) | 0.065 (n=1967) | 0.165 (n=1982) |
| ES options (2009-14) | 0.064 (n=1038) | 0.182 (n=1030) |
| Hedgerows and boundaries | 0.070 (n=2994) | 0.175 (n=2969) |
| Herbal leys | 0.062 (n=395) | 0.163 (n=392) |
| Low-input / legume grassland | 0.052 (n=760) | 0.141 (n=755) |
| Whole-farm soil plan | 0.073 (n=1887) | 0.187 (n=1887) |

Relative change vs whole-farm soil plan points, site fixed effects (1.0 = mean change):

| Group | AlphaEarth (20 m, 64-d) | TESSERA (10 m, 128-d) |
|---|---|---|
| Arable actions | +0.417 (p=0) | +0.313 (p=0) |
| CS options (2021-25) | -0.100 (p=0.0006) | -0.086 (p=0) |
| ES options (2009-14) | -0.310 (p=0) | -0.277 (p=0) |
| Hedgerows and boundaries | -0.041 (p=0.123) | -0.041 (p=0.0122) |
| Herbal leys | -0.099 (p=0.0273) | -0.081 (p=0.0048) |
| Low-input / legume grassland | -0.206 (p=0) | -0.190 (p=0) |

Per-point change, AlphaEarth vs TESSERA: Spearman 0.797 (n=10183).
