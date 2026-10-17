# Paper 3: detecting agri-environment options from satellite records

Run of [detection_protocol.md](detection_protocol.md) (written before any model). Leave-one-region-out AUC (0.5 = chance); placebo = the 2017–2019 embedding, before any option existed; detection gain = 2025 embedding minus placebo. "Detected" = AUC ≥ 0.70 against comparison B and gain ≥ 0.10.

| Family | parcels | comparison | embedding 2025 | Sentinel-2 2025 | both | placebo 2017–19 | detection gain |
|---|---|---|---|---|---|---|---|
| Herbal leys | 7,935 | A: vs never-treated land | 0.86 (0.85–0.88) | 0.78 | 0.86 | 0.70 | +0.16 |
| Herbal leys | 7,935 | B: vs management-only scheme land | 0.83 (0.82–0.86) | 0.79 | 0.84 | 0.65 | +0.19 |
| Cover crops | 23,136 | A: vs never-treated land | 0.77 (0.72–0.81) | 0.70 | 0.77 | 0.72 | +0.05 |
| Cover crops | 23,136 | B: vs management-only scheme land | 0.64 (0.61–0.68) | 0.59 | 0.64 | 0.57 | +0.08 |
| No-till | 7,770 | A: vs never-treated land | 0.85 (0.76–0.89) | 0.78 | 0.85 | 0.77 | +0.08 |
| No-till | 7,770 | B: vs management-only scheme land | 0.77 (0.70–0.83) | 0.72 | 0.78 | 0.64 | +0.13 |
| In-field flower and bird-food plots | 17,121 | A: vs never-treated land | 0.75 (0.72–0.78) | 0.70 | 0.76 | 0.67 | +0.08 |
| In-field flower and bird-food plots | 17,121 | B: vs management-only scheme land | 0.66 (0.64–0.72) | 0.63 | 0.66 | 0.56 | +0.11 |
| Margins and corners | 45,667 | A: vs never-treated land | 0.71 (0.60–0.74) | 0.63 | 0.71 | 0.71 | -0.00 |
| Margins and corners | 45,667 | B: vs management-only scheme land | 0.57 (0.54–0.60) | 0.53 | 0.56 | 0.56 | +0.01 |
| Grassland options | 3,331 | A: vs never-treated land | 0.75 (0.71–0.78) | 0.70 | 0.75 | 0.65 | +0.10 |
| Grassland options | 3,331 | B: vs management-only scheme land | 0.81 (0.75–0.84) | 0.78 | 0.81 | 0.73 | +0.08 |
| Buffer strips (control) | 47,105 | A: vs never-treated land | 0.73 (0.61–0.76) | 0.63 | 0.72 | 0.72 | +0.01 |
| Buffer strips (control) | 47,105 | B: vs management-only scheme land | 0.57 (0.55–0.59) | 0.52 | 0.55 | 0.56 | +0.00 |
| Management only (control) | 164,990 | A: vs never-treated land | 0.69 (0.63–0.72) | 0.63 | 0.69 | 0.68 | +0.01 |

## Verdict (rule fixed in advance)

| Family | detected |
|---|---|
| Herbal leys | yes |
| Cover crops | no |
| No-till | yes |
| In-field flower and bird-food plots | no |
| Margins and corners | no |
| Grassland options | no |
| Buffer strips (control) | no |
| Management only (control) | – |
