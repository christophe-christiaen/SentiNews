# U3: the WP1 nowcast in Scotland and Northern Ireland

Protocol: [u3_protocol.md](u3_protocol.md), written before extraction (with its record). Fields: UKFields sample (Scotland 113,518, Northern Ireland 56,208); crops classified with a model trained on England. Aggregates only.

## Validation gate (classified vs official crop area)

| Nation · crop | years within ×1.5 | median ratio | regional Spearman | passed |
|---|---|---|---|---|
| Northern Ireland | spring barley | 3/9 | 0.58 | – | no |
| Northern Ireland | wheat | 8/9 | 0.94 | – | yes |
| Northern Ireland | winter barley | 2/9 | 0.56 | – | no |
| Scotland | spring barley | 3/8 | 0.63 | 0.80 | no |
| Scotland | wheat | 8/8 | 0.84 | 1.00 | yes |
| Scotland | winter barley | 4/8 | 0.65 | 0.40 | no |

## Skill (out-of-sample R² of the yield anomaly; RMSE t/ha)

| Crop | design | model | cutoff | R² | RMSE | r | n |
|---|---|---|---|---|---|---|---|
| wheat | D1 transfer | pilot | mid-July | +0.05 | 0.87 | 0.31 | 41 |
| wheat | D2 local | pilot | mid-July | +0.04 | 0.88 | 0.22 | 41 |
| wheat | D3 pooled UK | pilot | mid-July | +0.06 | 0.87 | 0.29 | 41 |
| wheat | D1 transfer | weather | mid-July | -0.22 | 0.99 | -0.05 | 41 |
| wheat | D2 local | weather | mid-July | -0.13 | 0.96 | -0.78 | 41 |
| wheat | D3 pooled UK | weather | mid-July | -0.23 | 1.00 | -0.29 | 41 |
| wheat | D1 transfer | s2 | mid-July | +0.28 | 0.76 | 0.54 | 41 |
| wheat | D2 local | s2 | mid-July | -0.27 | 1.01 | 0.11 | 41 |
| wheat | D3 pooled UK | s2 | mid-July | +0.08 | 0.86 | 0.38 | 41 |
| wheat | D1 transfer | s2+weather | mid-July | +0.22 | 0.79 | 0.49 | 41 |
| wheat | D2 local | s2+weather | mid-July | -0.17 | 0.97 | 0.11 | 41 |
| wheat | D3 pooled UK | s2+weather | mid-July | +0.06 | 0.87 | 0.35 | 41 |
| wheat | D1 transfer | s2 | end of August | +0.10 | 0.85 | 0.39 | 41 |
| wheat | D2 local | s2 | end of August | -0.42 | 1.07 | 0.08 | 41 |
| wheat | D3 pooled UK | s2 | end of August | -0.10 | 0.94 | 0.28 | 41 |
| wheat | D1 transfer | s2+weather | end of August | +0.07 | 0.87 | 0.33 | 41 |
| wheat | D2 local | s2+weather | end of August | -0.26 | 1.01 | 0.08 | 41 |
| wheat | D3 pooled UK | s2+weather | end of August | -0.15 | 0.96 | 0.21 | 41 |
| winter barley | failed the validation gate in both nations | | | | | | |
| spring barley | failed the validation gate in both nations | | | | | | |

## Sensitivity (Sentinel-2 + weather, mid-July)

| Crop | design | all years | without 2020, 2022 | without 2025 |
|---|---|---|---|---|
| wheat | D1 transfer | +0.22 | +0.23 | +0.17 |
| wheat | D2 local | -0.17 | -0.19 | -0.25 |
| wheat | D3 pooled UK | +0.06 | +0.08 | -0.05 |

80% interval coverage (nested, Sentinel-2 + weather, mid-July): wheat | D1 transfer 78%; wheat | D2 local 78%; wheat | D3 pooled UK 80%

## Reading (rules fixed in advance)

- **wheat:** D1 R² +0.22 → **does not generalise** (< 0.30); D3 − D1 = -0.16 → local data do not add ≥ 0.10.
- **spring barley:** failed the validation gate in both nations

## 2026 nowcast (blind; committed before any official 2026 Scottish or NI yield was looked at)

| Crop | cutoff | design | region | fields | nowcast (t/ha) | 80% interval | mean of scored years |
|---|---|---|---|---|---|---|---|
| wheat | mid-July | D1 transfer | Eastern Scotland | 1,950 | 8.70 | 7.83–9.57 | 8.70 |
| wheat | mid-July | D1 transfer | Highlands and Islands | 392 | 7.86 | 6.99–8.73 | 8.18 |
| wheat | mid-July | D1 transfer | North Eastern Scotland | 867 | 8.77 | 7.90–9.65 | 8.94 |
| wheat | mid-July | D1 transfer | Northern Ireland | 786 | 6.45 | 5.57–7.32 | 7.44 |
| wheat | mid-July | D1 transfer | Southern Scotland | 1,270 | 8.28 | 7.40–9.15 | 8.44 |
| wheat | end of August | D1 transfer | Eastern Scotland | 1,938 | 9.05 | 8.16–9.95 | 8.70 |
| wheat | end of August | D1 transfer | Highlands and Islands | 275 | 8.90 | 8.01–9.79 | 8.18 |
| wheat | end of August | D1 transfer | North Eastern Scotland | 836 | 9.29 | 8.40–10.18 | 8.94 |
| wheat | end of August | D1 transfer | Northern Ireland | 716 | 7.22 | 6.32–8.11 | 7.44 |
| wheat | end of August | D1 transfer | Southern Scotland | 1,213 | 8.76 | 7.87–9.66 | 8.44 |

Nowcast written 2026-10-18 16:10. Limits: crops classified, not declared; UKFields boundaries are automatic (2021) and unofficial; Scottish regional yields are survey estimates (2020 and 2022 by a different method).
