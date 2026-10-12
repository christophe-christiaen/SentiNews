# WP1 results: Sentinel-2 regional yield nowcast

Run of [protocol.md](protocol.md) (written before any yield comparison). Leave-one-year-out over 2017–2025, 8 English Defra regions; R² of the yield anomaly against each region's training-year mean. Aggregates only.

## Wheat (72 region-years; median 16,993 parcels per region-year)

| Model | cutoff | R² | RMSE (t/ha) | r | England R² | England r |
|---|---|---|---|---|---|---|
| s2 | mid-May | +0.55 | 0.55 | +0.74 | +0.70 | +0.84 |
| s2+weather | mid-May | +0.46 | 0.61 | +0.68 | +0.56 | +0.75 |
| s2 | mid-June | +0.50 | 0.58 | +0.73 | +0.66 | +0.83 |
| s2+weather | mid-June | +0.45 | 0.61 | +0.71 | +0.62 | +0.81 |
| pilot | mid-July | +0.45 | 0.61 | +0.67 | +0.61 | +0.78 |
| weather | mid-July | -0.05 | 0.84 | +0.17 | +0.02 | +0.25 |
| s2 | mid-July | +0.53 | 0.56 | +0.75 | +0.74 | +0.86 |
| s2+weather | mid-July | +0.64 | 0.49 | +0.82 | +0.78 | +0.90 |
| modis | mid-July | +0.44 | 0.61 | +0.67 | +0.61 | +0.80 |
| s2 | end of August | +0.49 | 0.59 | +0.72 | +0.73 | +0.86 |
| s2+weather | end of August | +0.60 | 0.52 | +0.79 | +0.80 | +0.90 |

## Winter barley (72 region-years; median 4,199 parcels per region-year)

| Model | cutoff | R² | RMSE (t/ha) | r | England R² | England r |
|---|---|---|---|---|---|---|
| s2 | mid-May | +0.31 | 0.63 | +0.57 | +0.50 | +0.72 |
| s2+weather | mid-May | +0.43 | 0.57 | +0.66 | +0.62 | +0.80 |
| s2 | mid-June | +0.32 | 0.62 | +0.57 | +0.60 | +0.84 |
| s2+weather | mid-June | +0.49 | 0.54 | +0.71 | +0.77 | +0.91 |
| pilot | mid-July | +0.47 | 0.55 | +0.68 | +0.63 | +0.80 |
| weather | mid-July | +0.13 | 0.70 | +0.40 | +0.31 | +0.56 |
| s2 | mid-July | +0.29 | 0.63 | +0.55 | +0.57 | +0.79 |
| s2+weather | mid-July | +0.52 | 0.52 | +0.73 | +0.81 | +0.95 |
| s2 | end of August | +0.48 | 0.55 | +0.69 | +0.74 | +0.88 |
| s2+weather | end of August | +0.61 | 0.47 | +0.79 | +0.86 | +0.94 |

## Spring barley (72 region-years; median 6,173 parcels per region-year)

| Model | cutoff | R² | RMSE (t/ha) | r | England R² | England r |
|---|---|---|---|---|---|---|
| s2 | mid-May | -0.15 | 0.69 | +0.16 | -0.10 | +0.11 |
| s2+weather | mid-May | +0.04 | 0.63 | +0.32 | +0.16 | +0.42 |
| s2 | mid-June | +0.10 | 0.61 | +0.40 | +0.18 | +0.45 |
| s2+weather | mid-June | +0.37 | 0.51 | +0.61 | +0.57 | +0.77 |
| pilot | mid-July | +0.21 | 0.57 | +0.47 | +0.31 | +0.56 |
| weather | mid-July | -0.18 | 0.70 | -0.15 | -0.13 | -0.10 |
| s2 | mid-July | +0.52 | 0.45 | +0.72 | +0.76 | +0.88 |
| s2+weather | mid-July | +0.51 | 0.45 | +0.72 | +0.74 | +0.89 |
| s2 | end of August | +0.49 | 0.46 | +0.71 | +0.79 | +0.89 |
| s2+weather | end of August | +0.49 | 0.46 | +0.70 | +0.74 | +0.87 |

## Interval coverage (mid-July, nested leave-one-year-out)

| Crop, model | 80% | 90% |
|---|---|---|
| wheat | s2 | 81% | 86% |
| wheat | s2+weather | 79% | 89% |
| winter barley | s2 | 79% | 89% |
| winter barley | s2+weather | 79% | 89% |
| spring barley | s2 | 79% | 90% |
| spring barley | s2+weather | 78% | 89% |

## Crop classifier check (trained 2017–2024, tested on CROME 2025)

| Cutoff | accuracy | wheat P / R | winter barley P / R | spring barley P / R |
|---|---|---|---|---|
| k ≤ 9 | 0.828 | 0.94 / 0.86 | 0.75 / 0.60 | 0.46 / 0.75 |
| k ≤ 12 | 0.824 | 0.93 / 0.85 | 0.75 / 0.60 | 0.45 / 0.75 |

## 2026 nowcast (written 2026-10-11 21:15, before any official 2026 regional figure was looked at)

| Crop | cutoff | region | nowcast (t/ha) | 80% interval | 90% interval | 2017–2025 mean |
|---|---|---|---|---|---|---|
| wheat | mid-July | East Midlands | 8.09 | 7.27–9.17 | 7.12–9.37 | 7.72 |
| wheat | mid-July | Eastern | 8.47 | 7.47–9.61 | 7.30–9.79 | 8.11 |
| wheat | mid-July | North East | 8.51 | 7.75–9.30 | 7.58–9.39 | 8.02 |
| wheat | mid-July | North West and Merseyside | 5.97 | 5.37–7.03 | 5.22–7.07 | 5.94 |
| wheat | mid-July | South East and London | 8.54 | 7.69–9.62 | 7.44–9.82 | 7.99 |
| wheat | mid-July | South West | 8.15 | 7.35–9.21 | 7.10–9.40 | 7.63 |
| wheat | mid-July | West Midlands | 8.12 | 7.12–9.20 | 6.87–9.39 | 7.30 |
| wheat | mid-July | Yorkshire & The Humber | 8.71 | 7.83–9.58 | 7.76–9.68 | 8.07 |
| wheat | end of August | East Midlands | 8.05 | 7.05–9.12 | 6.93–9.29 | 7.72 |
| wheat | end of August | Eastern | 8.15 | 7.16–9.53 | 6.98–9.93 | 8.11 |
| wheat | end of August | North East | 8.55 | 7.52–9.30 | 7.47–9.36 | 8.02 |
| wheat | end of August | North West and Merseyside | 6.26 | 5.30–7.06 | 5.22–7.13 | 5.94 |
| wheat | end of August | South East and London | 8.32 | 7.35–9.50 | 7.12–9.76 | 7.99 |
| wheat | end of August | South West | 8.06 | 7.11–9.17 | 6.87–9.32 | 7.63 |
| wheat | end of August | West Midlands | 7.83 | 6.87–8.98 | 6.63–9.32 | 7.30 |
| wheat | end of August | Yorkshire & The Humber | 8.62 | 7.64–9.51 | 7.55–9.64 | 8.07 |
| winter barley | mid-July | East Midlands | 7.27 | 6.38–8.22 | 6.11–8.38 | 6.57 |
| winter barley | mid-July | Eastern | 7.42 | 6.50–8.26 | 6.23–8.46 | 6.89 |
| winter barley | mid-July | North East | 7.51 | 6.46–8.51 | 6.29–8.74 | 6.91 |
| winter barley | mid-July | North West and Merseyside | 6.44 | 5.60–7.37 | 5.28–7.65 | 6.12 |
| winter barley | mid-July | South East and London | 7.31 | 6.48–8.51 | 6.26–8.69 | 6.66 |
| winter barley | mid-July | South West | 7.34 | 6.45–8.39 | 6.21–8.63 | 6.85 |
| winter barley | mid-July | West Midlands | 7.21 | 6.16–8.16 | 5.92–8.46 | 6.37 |
| winter barley | mid-July | Yorkshire & The Humber | 8.02 | 7.00–8.92 | 6.85–9.11 | 7.17 |
| winter barley | end of August | East Midlands | 7.20 | 6.38–7.99 | 6.20–8.13 | 6.57 |
| winter barley | end of August | Eastern | 7.39 | 6.55–8.16 | 6.32–8.23 | 6.89 |
| winter barley | end of August | North East | 7.41 | 6.59–8.21 | 6.37–8.32 | 6.91 |
| winter barley | end of August | North West and Merseyside | 6.69 | 5.88–7.47 | 5.72–7.61 | 6.12 |
| winter barley | end of August | South East and London | 7.19 | 6.25–7.96 | 6.13–8.03 | 6.66 |
| winter barley | end of August | South West | 7.38 | 6.47–8.13 | 6.30–8.20 | 6.85 |
| winter barley | end of August | West Midlands | 7.21 | 6.34–8.00 | 6.13–8.07 | 6.37 |
| winter barley | end of August | Yorkshire & The Humber | 8.03 | 7.23–8.84 | 7.01–8.97 | 7.17 |
| spring barley | mid-July | East Midlands | 5.54 | 4.79–6.26 | 4.62–6.39 | 5.59 |
| spring barley | mid-July | Eastern | 4.99 | 4.26–5.72 | 4.06–5.85 | 5.64 |
| spring barley | mid-July | North East | 6.26 | 5.52–6.94 | 5.39–7.19 | 5.73 |
| spring barley | mid-July | North West and Merseyside | 4.19 | 3.46–4.90 | 3.42–5.28 | 4.19 |
| spring barley | mid-July | South East and London | 5.25 | 4.57–5.95 | 4.31–6.07 | 5.68 |
| spring barley | mid-July | South West | 5.27 | 4.54–5.99 | 4.38–6.20 | 5.36 |
| spring barley | mid-July | West Midlands | 4.84 | 4.13–5.48 | 4.06–5.83 | 4.94 |
| spring barley | mid-July | Yorkshire & The Humber | 6.05 | 5.28–6.73 | 5.19–7.01 | 5.68 |
| spring barley | end of August | East Midlands | 5.43 | 4.67–6.12 | 4.42–6.21 | 5.59 |
| spring barley | end of August | Eastern | 5.00 | 4.35–5.72 | 4.07–5.97 | 5.64 |
| spring barley | end of August | North East | 6.05 | 5.19–6.71 | 4.97–6.84 | 5.73 |
| spring barley | end of August | North West and Merseyside | 4.14 | 3.44–4.85 | 3.24–5.06 | 4.19 |
| spring barley | end of August | South East and London | 5.20 | 4.54–5.92 | 4.25–6.11 | 5.68 |
| spring barley | end of August | South West | 5.19 | 4.50–5.88 | 4.23–6.05 | 5.36 |
| spring barley | end of August | West Midlands | 4.65 | 3.93–5.34 | 3.71–5.43 | 4.94 |
| spring barley | end of August | Yorkshire & The Humber | 5.97 | 5.22–6.66 | 4.97–6.77 | 5.68 |

## Reading the 2026 nowcast (diagnostic run after the nowcast was written)

- **The crop mask is not the issue.** Using the classifier's wheat fields instead of CROME's in 2025 changes the
  prediction by +0.03 t/ha (7.40 vs 7.37); the classifier's fields are as green as CROME's within 0.004 NDVI.
- ~~Dry springs are the model's blind spot.~~ **Corrected 12 October 2026:** trained on 2017–2024, the model put
  England's 2025 wheat at 7.37 t/ha against Defra's 6.97. But the other dry-spring years go the other way: 2018,
  2020 and 2022 were *under*-predicted (by 0.25, 0.34 and 0.44 t/ha), and the mean error over the four dry-spring
  years is −0.15 t/ha. There is no consistent dry-year bias. The claim that the pilot missed 2022 "in the same way"
  was not checked and is withdrawn.
- **Reading 2026.** The nowcast puts wheat about 0.4–0.5 t/ha and winter barley about 0.6 t/ha above the 2017–2025
  mean. Over 2017–2025 single-year England errors ran from −0.44 to +0.41 t/ha, so 2026 could be near the mean as
  easily as above it; the 80% intervals (calibrated over all years) are the honest summary.
- **Grain-fill features (addendum A, [wp1_grainfill.md](wp1_grainfill.md)):** they did not help wheat or winter
  barley (wheat R² 0.64 → 0.56 at mid-July) and left the 2025 error unchanged (+0.44). They helped spring barley
  (0.51 → 0.57), whose 2026 nowcast is re-issued under the addendum's rule.
