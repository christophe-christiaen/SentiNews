# Stage 0 · Parcel crop history (counts only)

- CROME years: 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025; parcels: 2,686,103
- Parcels in cereals in at least half of the observed years (cereal land): 381,400 (14.2%)

## Cereal land by scheme group

| parcel_group   |          parcels |   cereal land |   share |
|:---------------|-----------------:|--------------:|--------:|
| agreement      |      1.03133e+06 |        252656 |   0.245 |
| legacy ES      | 148207           |          7455 |   0.05  |
| no agreement   |      1.35006e+06 |         90447 |   0.067 |
| uncertain      | 156507           |         30842 |   0.197 |

## Agreement parcels on cereal land, by entry year

|   entry_year |   parcels |
|-------------:|----------:|
|         2017 |       106 |
|         2018 |       177 |
|         2019 |       254 |
|         2020 |       125 |
|         2021 |     10893 |
|         2022 |     24214 |
|         2023 |     25178 |
|         2024 |    144284 |
|         2025 |     36425 |
|         2026 |     11000 |

## Share of parcels in cereals each year

|      |   cereal share of parcels |
|-----:|--------------------------:|
| 2016 |                     0.153 |
| 2017 |                     0.129 |
| 2018 |                     0.147 |
| 2019 |                     0.118 |
| 2020 |                     0.192 |
| 2021 |                     0.126 |
| 2022 |                     0.12  |
| 2023 |                     0.123 |
| 2024 |                     0.121 |
| 2025 |                     0.105 |

- Agreement parcels that were mostly cereal before entry (cereal_pre_entry >= 0.5): 256,639
- Cereal land in the drought years: 2018 394,924 parcels, 2022 323,270 parcels

Data notes
- CROME 2020 shows a higher cereal share (19%) than other years although England's cereal area fell in 2020; the
  national and county layers in the file agree exactly, so this comes from RPA's classification. Treat 2020 as lower
  confidence (e.g. leave it out of the cereal_land definition in sensitivity checks).
- 2018-2020 files hold each map twice (national + county layers, identical); 2025 has 24,967 hexagons without geometry,
  which were skipped. Every parcel received a crop code in every year.
