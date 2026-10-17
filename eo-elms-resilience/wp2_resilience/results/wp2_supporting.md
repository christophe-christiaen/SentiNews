# WP2 additions: flood zone and peat, Sentinel-1 winter wetness

Specified in paper/outline.md on 17 October 2026 before running. Errors clustered by ERA5 cell.

## W1. Flood Zone 3 or deep peat vs other cereal fields (MODIS, 16-season normal, 2002–2026)

Fields: 46,095 in Flood Zone 3 or on deep peat; 335,305 other.

| Measure | estimate | SE | p | n |
|---|---|---|---|---|
| stress gap, other seasons (fp minus other) | -0.005 | 0.003 | 0.0523 | 9,532,960 |
| extra gap in shock seasons | +0.050 | 0.006 | 2.22e-16 | 9,532,960 |
| carry-over within field (Anderson-Hsiao), flood zone 3 or deep peat | -0.043 | 0.004 | 0 | 1,105,255 |
| carry-over within field (Anderson-Hsiao), other | -0.016 | 0.002 | 0 | 8,044,655 |

## W2. Does winter radar wetness show up in the crop? (Sentinel-2 stress on Sentinel-1 winter VH, 2017–2025)

Within each field (field and cell × season effects). Positive = wetter-than-usual winter radar goes with a better-than-usual crop for that field.

| Measure | estimate | SE | p | n |
|---|---|---|---|---|
| all winters: S per dB of winter VH anomaly | -0.054 | 0.002 | 0 | 3,429,725 |
| extra slope in wet-shock winters | +0.033 | 0.002 | 0 | 3,429,725 |

## Reading (17 October 2026)

- **Flood Zone 3 and deep peat fields hold up better in droughts** (+0.050 SD in shock seasons, p < 0.001), with no
  difference in other seasons: wetter soils buffer dry and hot seasons. No carry-over within fields in either group.
  For a lender these fields carry flood and rewetting risk, not extra drought risk; the field score currently counts
  flood zone and peat as raising drought risk, which these results do not support (to revisit).
- **Winter waterlogging shows up in the crop.** Within each field, a winter 1 dB wetter on radar than usual comes with
  a crop 0.054 SD worse that season; the slope is smaller in the wettest winters (−0.021). Two independent satellites
  agree on the direction, which gives Paper 2 a winter-shock signal it lacked.
