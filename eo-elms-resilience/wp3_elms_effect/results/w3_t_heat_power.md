# W3-T Stage 1: power of the heat contrasts

Protocol: [w3_t_heat_only_protocol.md](w3_t_heat_only_protocol.md). **No estimate has been computed for reading or written here.** Minimum detectable effect (MDE) = 2.8 × SE, for 80% power at 5% two-sided. A row is read only if its MDE is within 0.10 SD or 0.10 t/ha and each side has at least 30 weather cells. E3 matched sample; strata ERA5 cell × season; SE clustered by ERA5 cell. "Hazard" is hot and dry (T1) or hot, not dry (T2); "other" is dry, not hot (T1) or calm (T2). Parcel-seasons are after entry.

## July NDVI (SD)

| Contrast | Family | Hazard side: parcel-seasons, cells | Other side: parcel-seasons, cells | Seasons on hazard side | SE | MDE | Placebo SE | Readable |
|---|---|---|---|---|---:|---:|---:|---|
| T1 heat on top of drought | All agreement land | 158,138, 992 | 124,790, 930 | 2022: 21,105, 2025: 87,054, 2026: 49,979 | 0.026 | 0.072 | none | yes |
| T1 heat on top of drought | Management-only | 108,833, 957 | 91,757, 899 | 2022: 12,000, 2025: 63,520, 2026: 33,313 | 0.030 | 0.083 | none | yes |
| T1 heat on top of drought | Cover crops | 9,769, 719 | 11,431, 706 | 2022: 1,064, 2025: 5,997, 2026: 2,708 | 0.068 | 0.191 | none | no |
| T1 heat on top of drought | No-till | 2,366, 288 | 1,122, 198 | 2022: 345, 2025: 1,407, 2026: 614 | 0.138 | 0.385 | none | no |
| T2 literal heat-only | All agreement land | 4,164, 129 | 37,401, 1171 | 2022: 4,163, 2026: 1 | 0.058 | 0.161 | 0.034 | no |
| T2 literal heat-only | Management-only | 2,336, 113 | 21,531, 1035 | 2022: 2,336 | 0.076 | 0.212 | 0.044 | no |
| T2 literal heat-only | Cover crops | 197, 51 | 2,039, 466 | 2022: 197 | 0.176 | 0.494 | 0.109 | no |
| T2 literal heat-only | No-till | 78, 24 | 572, 166 | 2022: 78 | 0.250 | 0.699 | 0.164 | no |

## Harvest index (t/ha)

| Contrast | Family | Hazard side: parcel-seasons, cells | Other side: parcel-seasons, cells | Seasons on hazard side | SE | MDE | Placebo SE | Readable |
|---|---|---|---|---|---:|---:|---:|---|
| T1 heat on top of drought | All agreement land | 41,780, 846 | 42,676, 868 | 2022: 8,214, 2025: 33,566 | 0.022 | 0.062 | none | yes |
| T1 heat on top of drought | Management-only | 29,525, 790 | 32,074, 847 | 2022: 4,635, 2025: 24,890 | 0.026 | 0.073 | none | yes |
| T1 heat on top of drought | Cover crops | 2,936, 507 | 4,628, 593 | 2022: 393, 2025: 2,543 | 0.054 | 0.152 | none | no |
| T1 heat on top of drought | No-till | 674, 176 | 481, 143 | 2022: 141, 2025: 533 | 0.133 | 0.371 | none | no |
| T2 literal heat-only | All agreement land | 1,708, 118 | 19,315, 1135 | 2022: 1,708 | 0.036 | 0.102 | 0.055 | no |
| T2 literal heat-only | Management-only | 914, 104 | 11,013, 1017 | 2022: 914 | 0.047 | 0.131 | 0.068 | no |
| T2 literal heat-only | Cover crops | 64, 25 | 1,066, 397 | 2022: 64 | 0.155 | 0.435 | 0.166 | no |
| T2 literal heat-only | No-till | 38, 13 | 323, 131 | 2022: 38 | 0.191 | 0.534 | 0.518 | no |
