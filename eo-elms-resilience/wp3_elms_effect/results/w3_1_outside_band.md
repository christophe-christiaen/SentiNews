# W3-1: existing woody edge outside the field outline (LiDAR VOM)

Record row of 1 November 2026 (a deviation, fixed before any value was computed): ring 0–25 m outside the UKFields outline minus other UKFields polygons; share of ring pixels above 1 m. Aggregates only.

- Sampled fields 34,106; with a ring 33,776; usable (≥ 200 valid ring pixels) 33,761.

| Family | role | n | outside share (mean) | median | outside mean height (m) | inside-band share |
|---|---|---|---|---|---|---|
| area_strips | A | 2,967 | 0.084 | 0.066 | 0.65 | 0.0040 |
| area_strips | B | 2,966 | 0.080 | 0.060 | 0.64 | 0.0034 |
| area_strips | positive | 2,978 | 0.080 | 0.063 | 0.64 | 0.0031 |
| hedge_management | A | 2,961 | 0.083 | 0.064 | 0.64 | 0.0041 |
| hedge_management | B | 2,973 | 0.075 | 0.058 | 0.59 | 0.0029 |
| hedge_management | positive | 2,960 | 0.083 | 0.066 | 0.64 | 0.0031 |
| management_only | A | 2,957 | 0.082 | 0.063 | 0.63 | 0.0036 |
| management_only | positive | 2,969 | 0.075 | 0.054 | 0.60 | 0.0033 |
| new_hedges | A | 2,969 | 0.086 | 0.067 | 0.67 | 0.0038 |
| new_hedges | B | 2,977 | 0.078 | 0.058 | 0.62 | 0.0030 |
| new_hedges | positive | 2,985 | 0.071 | 0.053 | 0.58 | 0.0025 |
| walls_banks | A | 365 | 0.084 | 0.066 | 0.66 | 0.0040 |
| walls_banks | B | 367 | 0.074 | 0.057 | 0.59 | 0.0023 |
| walls_banks | positive | 367 | 0.065 | 0.038 | 0.54 | 0.0034 |

**Registered check** (hedge management minus never-treated A; difference in mean outside share, 95% bootstrap interval):

- vs A: -0.0002 (-0.0038 to +0.0034; n 2,960 / 2,961) → **failed**
- vs management-only B: +0.0072 (+0.0035 to +0.0110; n 2,960 / 2,969)
- vs A, pre-2021 surveys only: +0.0008 (-0.0032 to +0.0047; n 2,493 / 2,518)

Each family against its own comparison A:

- new_hedges: -0.0150 (-0.0187 to -0.0114; n 2,985 / 2,969)
- area_strips: -0.0041 (-0.0077 to -0.0004; n 2,978 / 2,967)
- hedge_management: -0.0002 (-0.0037 to +0.0036; n 2,960 / 2,961)
- walls_banks: -0.0192 (-0.0295 to -0.0084; n 367 / 365)
