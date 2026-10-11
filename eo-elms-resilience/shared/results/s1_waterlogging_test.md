# Sentinel-1 waterlogging test, tile 30UXD (counts only)

- Cereal parcels: 58,513; passes read: 389 dates; observations: 17,127,452
- Water-like = VV backscatter below -17.0 dB (40 m overview of Sentinel-1 RTC gamma0)

## By winter and flood zone

| winter          | fz3          |   mean share of passes water-like |   parcels water-like in >=20% of passes |   median VV (dB) |   parcels |
|:----------------|:-------------|----------------------------------:|----------------------------------------:|-----------------:|----------:|
| 2019-20 (wet)   | other        |                             0     |                                   0     |           -7.529 |     44855 |
| 2019-20 (wet)   | Flood Zone 3 |                             0.001 |                                   0     |           -6.457 |     13658 |
| 2021-22 (drier) | other        |                             0     |                                   0     |           -8.755 |     44855 |
| 2021-22 (drier) | Flood Zone 3 |                             0     |                                   0     |           -7.975 |     13658 |
| 2023-24 (wet)   | other        |                             0     |                                   0     |           -8.427 |     44855 |
| 2023-24 (wet)   | Flood Zone 3 |                             0.003 |                                   0.003 |           -7.527 |     13658 |

## Share of parcel observations water-like, by month

| winter          | m       |   water |
|:----------------|:--------|--------:|
| 2019-20 (wet)   | 2019-10 |   0     |
| 2019-20 (wet)   | 2019-11 |   0     |
| 2019-20 (wet)   | 2019-12 |   0     |
| 2019-20 (wet)   | 2020-01 |   0     |
| 2019-20 (wet)   | 2020-02 |   0     |
| 2019-20 (wet)   | 2020-03 |   0     |
| 2021-22 (drier) | 2021-10 |   0     |
| 2021-22 (drier) | 2021-11 |   0     |
| 2021-22 (drier) | 2021-12 |   0     |
| 2021-22 (drier) | 2022-01 |   0     |
| 2021-22 (drier) | 2022-02 |   0     |
| 2021-22 (drier) | 2022-03 |   0     |
| 2023-24 (wet)   | 2023-10 |   0.001 |
| 2023-24 (wet)   | 2023-11 |   0     |
| 2023-24 (wet)   | 2023-12 |   0     |
| 2023-24 (wet)   | 2024-01 |   0.002 |
| 2023-24 (wet)   | 2024-02 |   0.001 |
| 2023-24 (wet)   | 2024-03 |   0     |

## Orbit-normalised check

Each observation compared with the same parcel's median for the same orbit and calendar month (over the three winters):

| Winter | Flood zone | mean anomaly (dB) | share of drops >= 3 dB | share of rises >= 2 dB |
|---|---|---|---|---|
| 2019-20 (wet) | other | +0.24 | 0.015 | 0.082 |
| 2019-20 (wet) | Flood Zone 3 | +0.21 | 0.023 | 0.086 |
| 2021-22 (drier) | other | -0.78 | 0.141 | 0.086 |
| 2021-22 (drier) | Flood Zone 3 | -0.89 | 0.190 | 0.110 |
| 2023-24 (wet) | other | -0.39 | 0.121 | 0.130 |
| 2023-24 (wet) | Flood Zone 3 | -0.53 | 0.169 | 0.158 |

Reading: wet-soil brightening shows (2019-20 about 1 dB brighter than 2021-22 after removing orbit and month effects),
but standing water is not detectable at 40 m point level, and sudden drops are more common in the drier winter (field
operations and crop changes, not water). Flood Zone 3 parcels are more variable in every winter.
Conclusion: Sentinel-1 is usable as a winter soil-wetness anomaly (needs a longer per-parcel baseline, 2017-2026, and
full 10-20 m resolution), not as a flood detector. Flood zones and ERA5 wet shocks already cover flood exposure.
