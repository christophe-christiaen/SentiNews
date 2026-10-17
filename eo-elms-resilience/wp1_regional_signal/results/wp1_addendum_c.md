# WP1 addendum C: supporting datasets

Protocol addendum C ([protocol.md](protocol.md)), written 17 October 2026 before running. Leave-one-year-out; R² of the yield anomaly; dry-spring years 2018, 2020, 2022, 2025.

## C1. MODIS long record (its own model; cereal-land parcel points, 2001–2025)

| Crop | years | R², all years | England R², all years | R², 2017–2025 only | dry-year MAE (t/ha) |
|---|---|---|---|---|---|
| wheat | 2001–2025 | +0.26 | +0.43 | +0.34 | 0.46 |
| winter barley | 2001–2025 | +0.29 | +0.47 | +0.31 | 0.33 |
| spring barley | 2001–2025 | +0.17 | +0.32 | +0.19 | 0.21 |

Sentinel-2 + weather, first run (2017–2025): wheat 0.64, winter barley 0.52, spring barley 0.51 (mid-July).

## C2 and C3 (added to the first-run Sentinel-2 + weather model, 2017–2025)

| Crop, cutoff | model | R² | England R² | dry-year MAE | adopt |
|---|---|---|---|---|---|
| wheat | mid-July | first run | +0.64 | +0.78 | 0.36 | – |
| wheat | mid-July | C2 + Sentinel-1 | +0.69 | +0.83 | 0.38 | no |
| wheat | mid-July | C3 + schemes, flood/peat | +0.79 | +0.97 | 0.10 | yes |
| wheat | end of August | first run | +0.60 | +0.80 | 0.31 | – |
| wheat | end of August | C2 + Sentinel-1 | +0.48 | +0.66 | 0.53 | no |
| wheat | end of August | C3 + schemes, flood/peat | +0.70 | +0.95 | 0.11 | yes |
| winter barley | mid-July | first run | +0.52 | +0.81 | 0.16 | – |
| winter barley | mid-July | C2 + Sentinel-1 | +0.56 | +0.81 | 0.14 | yes |
| winter barley | mid-July | C3 + schemes, flood/peat | +0.30 | +0.50 | 0.23 | no |
| winter barley | end of August | first run | +0.61 | +0.86 | 0.20 | – |
| winter barley | end of August | C2 + Sentinel-1 | +0.62 | +0.86 | 0.14 | no |
| winter barley | end of August | C3 + schemes, flood/peat | +0.58 | +0.81 | 0.24 | no |
| spring barley | mid-July | first run | +0.51 | +0.74 | 0.30 | – |
| spring barley | mid-July | C2 + Sentinel-1 | +0.53 | +0.74 | 0.32 | no |
| spring barley | mid-July | C3 + schemes, flood/peat | +0.46 | +0.65 | 0.32 | no |
| spring barley | end of August | first run | +0.49 | +0.74 | 0.32 | – |
| spring barley | end of August | C2 + Sentinel-1 | +0.28 | +0.57 | 0.37 | no |
| spring barley | end of August | C3 + schemes, flood/peat | +0.45 | +0.66 | 0.34 | no |

## Reading (17 October 2026)

- **C1, MODIS long record: weaker, even with 25 seasons.** Wheat R² 0.26 over 2001–2025 and 0.34 on 2017–2025, against
  0.64 for Sentinel-2 + weather on the same years. A longer record does not make up for 250 m pixels at cereal-land
  points (no crop map before 2016). MODIS stays the long-history tool (WP2), not the yield model.
- **C2, Sentinel-1 in spring: adopted for winter barley at mid-July only** (R² 0.52 → 0.56, dry-year error 0.16 →
  0.14). For wheat at mid-July R² rises (0.64 → 0.69) but the dry-year error does not fall, so it is not adopted; at
  end of August Sentinel-1 makes wheat and spring barley worse.
- **C3, schemes, flood and peat: rule says adopt for wheat; overridden, not adopted.** Wheat R² 0.64 → 0.79 (England
  0.97) comes entirely from the agreement share, which is zero until 2020 and jumps to 0.55–0.64 in 2024–2025, the two
  poor wheat years (6.91, 6.97 t/ha). A post hoc check: a plain year trend adds nothing (0.65), flood/peat × wet winter
  adds nothing (0.61), and for barley the same variable makes the model worse. With nine seasons any variable that is
  high only in 2024–25 "explains" those years; this is a coincidence of timing, not an effect of the schemes, and
  adopting it would build that coincidence into every future forecast. The override is logged in the protocol.
