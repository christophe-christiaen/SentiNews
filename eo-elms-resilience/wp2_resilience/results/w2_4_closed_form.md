# W2-4: a closed form for the short-baseline artefact

Protocol: [w2_4_closed_form_protocol.md](w2_4_closed_form_protocol.md), written before this run. Fields with no carry-over, z-scored against their first n seasons over T seasons; legacy test pooled within cell × season. 200 Monte Carlo replications per row (40,000 fields, 400 cells).

β(n, T) = [(T − n − 1)K − (n − 1)] / [n(n − 1) + (T − n − 1)(n + 1)K], K = (n − 1)/(n − 3) with the SD estimated, K = 1 without scaling; infinite K for n ≤ 3 (no stable value).

| Version | T | n | formula | MC mean (SE) | MC median | 10–90% of runs | accepted |
|---|---|---|---|---|---|---|---|
| estimated SD, cell shocks (WP2 design) | 10 | 2 | +0.333 | +0.303 (0.018) | +0.298 | -0.002 to +0.653 | – |
| estimated SD, cell shocks (WP2 design) | 10 | 3 | +0.250 | +0.234 (0.009) | +0.230 | +0.127 to +0.349 | – |
| estimated SD, cell shocks (WP2 design) | 10 | 4 | +0.138 | +0.142 (0.001) | +0.141 | +0.121 to +0.166 | – |
| estimated SD, cell shocks (WP2 design) | 10 | 5 | +0.059 | +0.063 (0.001) | +0.063 | +0.054 to +0.072 | – |
| estimated SD, cell shocks (WP2 design) | 10 | 6 | +0.000 | +0.002 (0.000) | +0.002 | -0.002 to +0.007 | yes |
| estimated SD, cell shocks (WP2 design) | 10 | 8 | -0.082 | -0.081 (0.000) | -0.081 | -0.084 to -0.078 | yes |
| estimated SD, cell shocks (WP2 design) | 10 | 2 | +0.333 | +0.275 (0.022) | +0.298 | -0.139 to +0.637 | – |
| estimated SD, cell shocks (WP2 design) | 10 | 3 | +0.250 | +0.240 (0.008) | +0.241 | +0.130 to +0.351 | – |
| estimated SD, cell shocks (WP2 design) | 10 | 4 | +0.138 | +0.144 (0.001) | +0.142 | +0.120 to +0.164 | – |
| estimated SD, cell shocks (WP2 design) | 11 | 5 | +0.075 | +0.078 (0.001) | +0.078 | +0.070 to +0.087 | – |
| estimated SD, cell shocks (WP2 design) | 12 | 6 | +0.038 | +0.040 (0.000) | +0.039 | +0.035 to +0.045 | yes |
| estimated SD, cell shocks (WP2 design) | 14 | 8 | +0.000 | +0.001 (0.000) | +0.001 | -0.002 to +0.004 | yes |
| estimated SD, cell shocks (WP2 design) | 16 | 10 | -0.016 | -0.016 (0.000) | -0.016 | -0.018 to -0.014 | yes |
| estimated SD, cell shocks (WP2 design) | 21 | 15 | -0.027 | -0.027 (0.000) | -0.027 | -0.029 to -0.025 | yes |
| estimated SD, no cell shocks | 10 | 2 | +0.333 | +0.291 (0.019) | +0.303 | -0.109 to +0.619 | – |
| estimated SD, no cell shocks | 10 | 3 | +0.250 | +0.231 (0.009) | +0.229 | +0.136 to +0.356 | – |
| estimated SD, no cell shocks | 10 | 4 | +0.138 | +0.136 (0.001) | +0.136 | +0.121 to +0.152 | – |
| estimated SD, no cell shocks | 10 | 5 | +0.059 | +0.057 (0.001) | +0.059 | +0.052 to +0.065 | – |
| estimated SD, no cell shocks | 10 | 6 | +0.000 | -0.000 (0.000) | -0.000 | -0.004 to +0.004 | yes |
| estimated SD, no cell shocks | 10 | 8 | -0.082 | -0.081 (0.000) | -0.081 | -0.084 to -0.079 | **no** |
| estimated SD, no cell shocks | 10 | 2 | +0.333 | +0.237 (0.021) | +0.259 | -0.128 to +0.602 | – |
| estimated SD, no cell shocks | 10 | 3 | +0.250 | +0.239 (0.009) | +0.236 | +0.112 to +0.360 | – |
| estimated SD, no cell shocks | 10 | 4 | +0.138 | +0.138 (0.002) | +0.137 | +0.120 to +0.153 | – |
| estimated SD, no cell shocks | 11 | 5 | +0.075 | +0.075 (0.000) | +0.074 | +0.069 to +0.081 | – |
| estimated SD, no cell shocks | 12 | 6 | +0.038 | +0.038 (0.000) | +0.037 | +0.034 to +0.041 | yes |
| estimated SD, no cell shocks | 14 | 8 | +0.000 | -0.000 (0.000) | -0.000 | -0.003 to +0.002 | **no** |
| estimated SD, no cell shocks | 16 | 10 | -0.016 | -0.016 (0.000) | -0.016 | -0.018 to -0.014 | yes |
| estimated SD, no cell shocks | 21 | 15 | -0.027 | -0.027 (0.000) | -0.027 | -0.028 to -0.025 | yes |
| mean removed, not scaled (= known SD), no cell shocks | 10 | 2 | +0.261 | +0.261 (0.000) | +0.261 | +0.258 to +0.264 | yes |
| mean removed, not scaled (= known SD), no cell shocks | 10 | 3 | +0.133 | +0.133 (0.000) | +0.133 | +0.131 to +0.137 | yes |
| mean removed, not scaled (= known SD), no cell shocks | 10 | 4 | +0.054 | +0.054 (0.000) | +0.054 | +0.051 to +0.057 | yes |
| mean removed, not scaled (= known SD), no cell shocks | 10 | 5 | +0.000 | -0.000 (0.000) | -0.000 | -0.003 to +0.002 | yes |
| mean removed, not scaled (= known SD), no cell shocks | 10 | 6 | -0.039 | -0.039 (0.000) | -0.040 | -0.042 to -0.037 | yes |
| mean removed, not scaled (= known SD), no cell shocks | 10 | 8 | -0.092 | -0.092 (0.000) | -0.092 | -0.094 to -0.090 | yes |
| mean removed, not scaled (= known SD), no cell shocks | 10 | 2 | +0.261 | +0.261 (0.000) | +0.261 | +0.258 to +0.264 | yes |
| mean removed, not scaled (= known SD), no cell shocks | 10 | 3 | +0.133 | +0.133 (0.000) | +0.133 | +0.131 to +0.136 | yes |
| mean removed, not scaled (= known SD), no cell shocks | 10 | 4 | +0.054 | +0.054 (0.000) | +0.054 | +0.052 to +0.057 | yes |
| mean removed, not scaled (= known SD), no cell shocks | 11 | 5 | +0.020 | +0.020 (0.000) | +0.020 | +0.017 to +0.022 | yes |
| mean removed, not scaled (= known SD), no cell shocks | 12 | 6 | +0.000 | -0.000 (0.000) | +0.000 | -0.002 to +0.002 | yes |
| mean removed, not scaled (= known SD), no cell shocks | 14 | 8 | -0.020 | -0.020 (0.000) | -0.020 | -0.022 to -0.018 | yes |
| mean removed, not scaled (= known SD), no cell shocks | 16 | 10 | -0.028 | -0.028 (0.000) | -0.028 | -0.029 to -0.026 | yes |
| mean removed, not scaled (= known SD), no cell shocks | 21 | 15 | -0.031 | -0.031 (0.000) | -0.031 | -0.033 to -0.030 | yes |

**Acceptance (rules fixed in advance):** 24 of 26 checks passed. Failed: estimated SD, no cell shocks | T = 10 | 8, estimated SD, no cell shocks | T = max(10, n + 6) | 8.

Rows marked "–" are reported, not tested: n = 4, 5 have infinite variance (E[1/s⁴] diverges), n ≤ 3 has no stable value.
