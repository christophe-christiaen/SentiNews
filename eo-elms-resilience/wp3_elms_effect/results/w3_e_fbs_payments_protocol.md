# W3-E: economic context from published Farm Business Survey aggregates (descriptive)

**Status: written 20 November 2026, before any ratio below was computed.** Descriptive context for the ELMs evaluation;
no test, no link to fields. Changes go in the record at the end.

## Question
How has the payment side of farm income changed through the move from direct payments to agri-environment payments,
and how large are payments relative to farm income and output? This sets the economic scale against which the
programme's physical results (detection of actions, harvest contrasts) are read.

## Data
Four datasheets downloaded by the project lead from the Farm Business Survey data dashboard (England, Defra), real
prices, £ per hectare, survey years 2005/06–2024/25, with the published 95% confidence intervals. Licence: "FBS data is
provided under the Open Government Licence v3.0, unless stated otherwise" (dashboard, checked 20 November 2026);
attribution: Farm Business Survey, Defra, © Crown copyright. Stored in `shared/data/fbs/`:
- `fbs_direct_payments_per_ha_by_type.csv`: direct payment income, by farm type;
- `fbs_agrienv_payments_per_ha_by_type.csv`: agri-environment payments (gross), by farm type;
- `fbs_farm_business_income_per_ha_by_type.csv`: farm business income, by farm type;
- `fbs_output_per_ha_by_region.csv`: agricultural output, by region (only the "All" row is used).

## Rules fixed now
1. **Typology:** where a survey year is published under two farm-type classifications (2009/10, 2012/13, 2017/18,
   2022/23), the newer classification is used; the differences in the overlap years are reported.
2. **Quantities**, for "All" farms and each farm type:
   - combined payments = direct payments + agri-environment payments;
   - payment share = combined payments ÷ farm business income (a ratio of published means, not the mean of farm
     ratios; shown only where income is positive);
   - change in each payment series from 2019/20 (last year before direct payments began to be reduced) to 2024/25;
   - for "All" farms only, agri-environment payments ÷ agricultural output.
3. **Farm types in the narrative:** cereals, general cropping, dairy, LFA grazing livestock, lowland grazing livestock,
   mixed. Horticulture, pigs and poultry are tabulated but not discussed (little land, very wide intervals).
4. **Scale comparison, illustrative only:** a harvest difference of 0.04 t/ha (the size of the AlphaEarth matching shift
   in W3-B1) is converted at assumed grain prices of £150–250/t, stated as an assumption, not a sourced price.
5. **Uncertainty:** published intervals are carried for single series; no interval is computed for ratios (the
   survey's covariances are not published), and ratios are labelled as point values.

## Limits stated with the result
Averages over all farms of a type, including non-participants; agri-environment payments are gross (costs of the
actions sit inside farm business income); no link to scheme fields or to the programme's samples; farm-level analysis
needs the FBS microdata (Block 2).

## Output
`wp3_elms_effect/results/w3_e_fbs_payments.md`, `.json`; a section in the team report.

## Record
| Date | Change | Reason |
|---|---|---|
| 2026-11-20 | Written before any ratio was computed (the four datasheets had been read on screen, and some point values were quoted in conversation) | Project lead: add the FBS economic context to the team report |
| 2026-11-20 | Run ([w3_e_fbs_payments.md](w3_e_fbs_payments.md)). All farms 2019/20 → 2024/25: direct payments 221 → 81, agri-environment 51 → 159, combined 272 → 240 £/ha (−12%); payments ÷ income 74% → 56% (lowest 34% in 2022/23, 63% in 2023/24); agri-environment ÷ output 2.5% → 7.2%. 2024/25 payments ÷ income: cereals 107%, LFA grazing 100%, mixed 75%, lowland grazing 74%, general cropping 47%, dairy 25%. Classification overlaps change All-farm values by at most £28/ha (income, 2009/10) and £7/ha (payments) | Rules above |
