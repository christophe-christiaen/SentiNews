# Company accounts and drought news linked to farms and weather (exploratory, counts only)

## A. Farm-company accounts vs local weather shocks

- Company-years with accounts and a located English farm (farm-like or unclear address): 9,368; companies: 2,407
- Harvests covered: 2020 (65), 2021 (1,445), 2022 (2,299), 2023 (2,380), 2024 (2,379), 2025 (779)

Year-on-year change regressed on the cell's severe dry shock and wet shock for that harvest, with harvest-year effects; errors clustered by ERA5 cell. Changes winsorised at 2% / 98%.

| outcome         | shock            |   coef |     p |    n |   companies |
|:----------------|:-----------------|-------:|------:|-----:|------------:|
| d_current_ratio | severe_dry_shock | -0.2   | 0.577 | 6172 |        2256 |
| d_current_ratio | wet_shock        | -0.119 | 0.617 | 6172 |        2256 |
| d_equity_ratio  | severe_dry_shock | -0.013 | 0.07  | 5484 |        2067 |
| d_equity_ratio  | wet_shock        | -0.006 | 0.226 | 5484 |        2067 |
| d_cash_ratio    | severe_dry_shock |  0.045 | 0.856 | 4496 |        1710 |
| d_cash_ratio    | wet_shock        | -0.242 | 0.169 | 4496 |        1710 |
| d_ln_net_assets | severe_dry_shock | -0.039 | 0.13  | 6047 |        2215 |
| d_ln_net_assets | wet_shock        |  0.005 | 0.83  | 6047 |        2215 |

## B. Drought news vs measured dryness (England)

- Literal-drought articles 2021–2026: 2,586 with an English region or England tag
- Correlation of monthly article counts with national dryness (minus soil-moisture z), by lag (positive lag = news follows dryness): -3 m: -0.08, -2 m: 0.06, -1 m: 0.24, +0 m: 0.50, +1 m: 0.40, +2 m: 0.35, +3 m: 0.39
- Strongest at +0 month(s)

- Across region-years, articles rise with dryness (Spearman 0.66), driven by dry years; within a year, the driest regions do not get more coverage (Spearman by year: 2021: +0.01, 2022: +0.13, 2023: -0.02, 2024: +0.17, 2025: -0.48, 2026: -0.02).

### Articles by region and year vs April–August dryness

| region                   |   2021 |   2022 |   2023 |   2024 |   2025 |   2026 |
|:-------------------------|-------:|-------:|-------:|-------:|-------:|-------:|
| East Midlands (England)  |      3 |     85 |     19 |     12 |     52 |     68 |
| East of England          |     20 |    100 |     63 |     20 |     75 |    167 |
| London                   |      2 |     36 |     19 |     16 |     26 |     62 |
| North East (England)     |      1 |     12 |      4 |      2 |     19 |      7 |
| North West (England)     |     20 |     35 |     19 |     13 |     92 |     71 |
| South East (England)     |      3 |     51 |     24 |     17 |     60 |     85 |
| South West (England)     |      2 |     34 |     20 |      5 |     48 |     52 |
| West Midlands (England)  |      3 |     20 |      8 |      6 |     25 |     54 |
| Yorkshire and the Humber |      6 |     66 |      9 |      4 |     75 |     37 |

Exploratory: accounts are annual and lag the harvest; small companies file abridged accounts; registered offices locate the business, not every field. News counts depend on media coverage, not only on conditions.
