# Stage 0 · Payment register check (counts only)

- Payment register: 307,860 payment rows, 47,331 payees, years 23/24, 24/25; schemes: Sustainable Farming Incentive (223,700), Countryside Stewardship (75,241), Farming Investment Fund (8,771), Landscape Recovery (112), Farming Resilience Fund (34), New Entrants Pilot (2)
- English companies matched to a payee in the same postcode district: 2,486 of 10,897 (22.8%; exact 2,291, fuzzy 195)
- Of those, with SFI or CS payments: 2,397

## Final analysis groups

|                           |   farms |
|:--------------------------|--------:|
| uncertain                 |    3717 |
| excluded (office address) |    2865 |
| agreement                 |    2261 |
| no agreement              |    2054 |

- **agreement**: paid SFI or CS in the payment register (spatial-only links are uncertain); **no agreement**: not in the register and no agreement assigned within 1 km; **uncertain**: the rest (left out of both groups, incl. spatial-only links); office addresses excluded because the point does not locate the farm.
- Evidence for the agreement group: register+spatial 1,225, register 1,036

## Spatial group vs payment register

| group                     |   not in register |   paid SFI/CS |   All |
|:--------------------------|------------------:|--------------:|------:|
| agreement                 |              2111 |          1225 |  3336 |
| excluded (office address) |              2729 |           136 |  2865 |
| no agreement              |              2054 |           429 |  2483 |
| uncertain                 |              1606 |           607 |  2213 |
| All                       |              8500 |          2397 | 10897 |

- Share of the **agreement** group confirmed by SFI/CS payments: 37%
- Share of the **no agreement** group that does receive SFI/CS payments (misclassed controls): 17%

Caveats: the register covers only recent financial years and payments of GBP 1,250 or more, and a business may be paid under a trading or partner name, so "not in register" does not prove there is no agreement. ES (pre-2016) agreements are not in this register.
