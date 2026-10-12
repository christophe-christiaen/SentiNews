# Scoring the 2026 nowcast against Defra's provisional figures

Nowcast written 11 October 2026 (commit 8427362) **without looking at** Defra's provisional 2026 estimates; note those were **already published on 8 October 2026**, three days earlier, so this is a blind forecast, not a forecast made before publication. Defra figures from UK-cops-webseries_261008.ods.

## Summary (8 English regions)

|                                                                       |   mean error |   mean abs. error |   in 80% interval |   in 90% interval |   direction vs mean right |   nowcast, mean of regions |   actual, mean of regions |
|:----------------------------------------------------------------------|-------------:|------------------:|------------------:|------------------:|--------------------------:|---------------------------:|--------------------------:|
| ('first nowcast (11 Oct)', 'spring barley', 'end of August')          |         0.67 |              0.72 |              0.5  |              0.62 |                      0.62 |                       5.2  |                      4.54 |
| ('first nowcast (11 Oct)', 'spring barley', 'mid-July')               |         0.76 |              0.81 |              0.38 |              0.5  |                      0.62 |                       5.3  |                      4.54 |
| ('first nowcast (11 Oct)', 'wheat', 'end of August')                  |         0.8  |              0.87 |              0.5  |              0.62 |                      0.38 |                       7.98 |                      7.18 |
| ('first nowcast (11 Oct)', 'wheat', 'mid-July')                       |         0.89 |              1.03 |              0.5  |              0.5  |                      0.38 |                       8.07 |                      7.18 |
| ('first nowcast (11 Oct)', 'winter barley', 'end of August')          |         0.79 |              0.8  |              0.62 |              0.62 |                      0.5  |                       7.31 |                      6.52 |
| ('first nowcast (11 Oct)', 'winter barley', 'mid-July')               |         0.79 |              0.79 |              0.62 |              0.75 |                      0.5  |                       7.32 |                      6.52 |
| ('spring barley re-issue (12 Oct)', 'spring barley', 'end of August') |         0.63 |              0.68 |              0.62 |            nan    |                      0.62 |                       5.16 |                      4.54 |
| ('spring barley re-issue (12 Oct)', 'spring barley', 'mid-July')      |         0.78 |              0.82 |              0.38 |            nan    |                      0.75 |                       5.32 |                      4.54 |

England (Defra, area-weighted): wheat 7.19 t/ha, winter barley 6.59 t/ha, spring barley 4.59 t/ha.

## By region

| Version | crop | cutoff | region | nowcast | 80% interval | Defra 2026 | error |
|---|---|---|---|---|---|---|---|
| first nowcast (11 Oct) | wheat | mid-July | East Midlands | 8.09 | 7.27–9.17 | 7.41 | +0.68 |
| first nowcast (11 Oct) | wheat | mid-July | Eastern | 8.47 | 7.47–9.61 | 7.03 | +1.44 |
| first nowcast (11 Oct) | wheat | mid-July | North East | 8.51 | 7.75–9.30 | 8.40 | +0.11 |
| first nowcast (11 Oct) | wheat | mid-July | North West and Merseyside | 5.97 | 5.37–7.03 | 6.54 | -0.57 |
| first nowcast (11 Oct) | wheat | mid-July | South East and London | 8.54 | 7.69–9.62 | 6.71 | +1.83 |
| first nowcast (11 Oct) | wheat | mid-July | South West | 8.15 | 7.35–9.21 | 6.61 | +1.54 |
| first nowcast (11 Oct) | wheat | mid-July | West Midlands | 8.12 | 7.12–9.20 | 6.57 | +1.55 |
| first nowcast (11 Oct) | wheat | mid-July | Yorkshire & The Humber | 8.71 | 7.83–9.58 | 8.20 | +0.51 |
| first nowcast (11 Oct) | wheat | end of August | East Midlands | 8.05 | 7.05–9.12 | 7.41 | +0.64 |
| first nowcast (11 Oct) | wheat | end of August | Eastern | 8.15 | 7.16–9.53 | 7.03 | +1.12 |
| first nowcast (11 Oct) | wheat | end of August | North East | 8.55 | 7.52–9.30 | 8.40 | +0.15 |
| first nowcast (11 Oct) | wheat | end of August | North West and Merseyside | 6.26 | 5.30–7.06 | 6.54 | -0.28 |
| first nowcast (11 Oct) | wheat | end of August | South East and London | 8.32 | 7.35–9.50 | 6.71 | +1.61 |
| first nowcast (11 Oct) | wheat | end of August | South West | 8.06 | 7.11–9.17 | 6.61 | +1.45 |
| first nowcast (11 Oct) | wheat | end of August | West Midlands | 7.83 | 6.87–8.98 | 6.57 | +1.26 |
| first nowcast (11 Oct) | wheat | end of August | Yorkshire & The Humber | 8.62 | 7.64–9.51 | 8.20 | +0.42 |
| first nowcast (11 Oct) | winter barley | mid-July | East Midlands | 7.27 | 6.38–8.22 | 7.03 | +0.24 |
| first nowcast (11 Oct) | winter barley | mid-July | Eastern | 7.42 | 6.50–8.26 | 6.05 | +1.37 |
| first nowcast (11 Oct) | winter barley | mid-July | North East | 7.51 | 6.46–8.51 | 7.47 | +0.04 |
| first nowcast (11 Oct) | winter barley | mid-July | North West and Merseyside | 6.44 | 5.60–7.37 | 5.57 | +0.87 |
| first nowcast (11 Oct) | winter barley | mid-July | South East and London | 7.31 | 6.48–8.51 | 5.70 | +1.61 |
| first nowcast (11 Oct) | winter barley | mid-July | South West | 7.34 | 6.45–8.39 | 6.53 | +0.81 |
| first nowcast (11 Oct) | winter barley | mid-July | West Midlands | 7.21 | 6.16–8.16 | 6.54 | +0.67 |
| first nowcast (11 Oct) | winter barley | mid-July | Yorkshire & The Humber | 8.02 | 7.00–8.92 | 7.31 | +0.71 |
| first nowcast (11 Oct) | winter barley | end of August | East Midlands | 7.20 | 6.38–7.99 | 7.03 | +0.17 |
| first nowcast (11 Oct) | winter barley | end of August | Eastern | 7.39 | 6.55–8.16 | 6.05 | +1.34 |
| first nowcast (11 Oct) | winter barley | end of August | North East | 7.41 | 6.59–8.21 | 7.47 | -0.06 |
| first nowcast (11 Oct) | winter barley | end of August | North West and Merseyside | 6.69 | 5.88–7.47 | 5.57 | +1.12 |
| first nowcast (11 Oct) | winter barley | end of August | South East and London | 7.19 | 6.25–7.96 | 5.70 | +1.49 |
| first nowcast (11 Oct) | winter barley | end of August | South West | 7.38 | 6.47–8.13 | 6.53 | +0.85 |
| first nowcast (11 Oct) | winter barley | end of August | West Midlands | 7.21 | 6.34–8.00 | 6.54 | +0.67 |
| first nowcast (11 Oct) | winter barley | end of August | Yorkshire & The Humber | 8.03 | 7.23–8.84 | 7.31 | +0.72 |
| first nowcast (11 Oct) | spring barley | mid-July | East Midlands | 5.54 | 4.79–6.26 | 4.74 | +0.80 |
| first nowcast (11 Oct) | spring barley | mid-July | Eastern | 4.99 | 4.26–5.72 | 4.75 | +0.24 |
| first nowcast (11 Oct) | spring barley | mid-July | North East | 6.26 | 5.52–6.94 | 4.65 | +1.61 |
| first nowcast (11 Oct) | spring barley | mid-July | North West and Merseyside | 4.19 | 3.46–4.90 | 4.36 | -0.17 |
| first nowcast (11 Oct) | spring barley | mid-July | South East and London | 5.25 | 4.57–5.95 | 4.25 | +1.00 |
| first nowcast (11 Oct) | spring barley | mid-July | South West | 5.27 | 4.54–5.99 | 4.14 | +1.13 |
| first nowcast (11 Oct) | spring barley | mid-July | West Midlands | 4.84 | 4.13–5.48 | 3.87 | +0.97 |
| first nowcast (11 Oct) | spring barley | mid-July | Yorkshire & The Humber | 6.05 | 5.28–6.73 | 5.52 | +0.53 |
| first nowcast (11 Oct) | spring barley | end of August | East Midlands | 5.43 | 4.67–6.12 | 4.74 | +0.69 |
| first nowcast (11 Oct) | spring barley | end of August | Eastern | 5.00 | 4.35–5.72 | 4.75 | +0.25 |
| first nowcast (11 Oct) | spring barley | end of August | North East | 6.05 | 5.19–6.71 | 4.65 | +1.40 |
| first nowcast (11 Oct) | spring barley | end of August | North West and Merseyside | 4.14 | 3.44–4.85 | 4.36 | -0.22 |
| first nowcast (11 Oct) | spring barley | end of August | South East and London | 5.20 | 4.54–5.92 | 4.25 | +0.95 |
| first nowcast (11 Oct) | spring barley | end of August | South West | 5.19 | 4.50–5.88 | 4.14 | +1.05 |
| first nowcast (11 Oct) | spring barley | end of August | West Midlands | 4.65 | 3.93–5.34 | 3.87 | +0.78 |
| first nowcast (11 Oct) | spring barley | end of August | Yorkshire & The Humber | 5.97 | 5.22–6.66 | 5.52 | +0.45 |
| spring barley re-issue (12 Oct) | spring barley | mid-July | East Midlands | 5.56 | 4.83–6.24 | 4.74 | +0.82 |
| spring barley re-issue (12 Oct) | spring barley | mid-July | Eastern | 4.93 | 4.25–5.68 | 4.75 | +0.18 |
| spring barley re-issue (12 Oct) | spring barley | mid-July | North East | 6.37 | 5.66–7.02 | 4.65 | +1.72 |
| spring barley re-issue (12 Oct) | spring barley | mid-July | North West and Merseyside | 4.21 | 3.56–4.91 | 4.36 | -0.15 |
| spring barley re-issue (12 Oct) | spring barley | mid-July | South East and London | 5.16 | 4.47–5.93 | 4.25 | +0.91 |
| spring barley re-issue (12 Oct) | spring barley | mid-July | South West | 5.24 | 4.54–5.99 | 4.14 | +1.10 |
| spring barley re-issue (12 Oct) | spring barley | mid-July | West Midlands | 4.86 | 4.16–5.53 | 3.87 | +0.99 |
| spring barley re-issue (12 Oct) | spring barley | mid-July | Yorkshire & The Humber | 6.23 | 5.47–6.89 | 5.52 | +0.71 |
| spring barley re-issue (12 Oct) | spring barley | end of August | East Midlands | 5.36 | 4.57–6.02 | 4.74 | +0.62 |
| spring barley re-issue (12 Oct) | spring barley | end of August | Eastern | 4.90 | 4.18–5.62 | 4.75 | +0.15 |
| spring barley re-issue (12 Oct) | spring barley | end of August | North East | 6.11 | 5.28–6.75 | 4.65 | +1.46 |
| spring barley re-issue (12 Oct) | spring barley | end of August | North West and Merseyside | 4.17 | 3.44–4.80 | 4.36 | -0.19 |
| spring barley re-issue (12 Oct) | spring barley | end of August | South East and London | 5.01 | 4.28–5.72 | 4.25 | +0.76 |
| spring barley re-issue (12 Oct) | spring barley | end of August | South West | 5.11 | 4.38–5.86 | 4.14 | +0.97 |
| spring barley re-issue (12 Oct) | spring barley | end of August | West Midlands | 4.56 | 3.77–5.22 | 3.87 | +0.69 |
| spring barley re-issue (12 Oct) | spring barley | end of August | Yorkshire & The Humber | 6.09 | 5.24–6.83 | 5.52 | +0.57 |
