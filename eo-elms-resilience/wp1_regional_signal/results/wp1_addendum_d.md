# WP1 addendum D: AlphaEarth embeddings

Protocol addendum D ([protocol.md](protocol.md)), written 17 October 2026 before running. Leave-one-year-out over 2018–2025 (2017 has no previous-year embedding). D2 uses the season's own embedding, which includes months after harvest: it is an after-season comparison, **not a nowcast**.

| Crop, cutoff | first run | D1 + previous-year embedding | D2 own-year alone (after season) | D2 + own-year (after season) | D1 dry-year MAE (first → D1) | adopt D1 |
|---|---|---|---|---|---|---|
| wheat | mid-July | +0.69 | +0.57 | -0.02 | +0.68 | 0.29 → 0.36 | no |
| wheat | end of August | +0.61 | +0.64 | -0.02 | +0.59 | 0.31 → 0.35 | no |
| winter barley | mid-July | +0.60 | +0.54 | +0.26 | +0.56 | 0.13 → 0.17 | no |
| winter barley | end of August | +0.65 | +0.60 | +0.26 | +0.62 | 0.15 → 0.15 | no |
| spring barley | mid-July | +0.54 | -0.02 | -0.03 | +0.51 | 0.30 → 0.58 | no |
| spring barley | end of August | +0.51 | +0.05 | -0.03 | +0.51 | 0.31 → 0.54 | no |

R² of the yield anomaly, out of sample. Embeddings: region median over the season's crop fields, 5 principal components fitted on each fold's training years.

## Reading (17 October 2026)

- **Not adopted for any crop.** The previous-year embedding lowers skill everywhere (wheat mid-July 0.69 → 0.57;
  spring barley collapses to about zero), and dry-year errors rise: five extra features on 64 region-years mostly
  add noise.
- **Even after the season, embeddings carry little year-to-year yield information at regional level.** The season's
  own embedding alone gives R² about zero for wheat and spring barley (0.26 for winter barley), and adding it to
  Sentinel-2 + weather does not help either. AlphaEarth is built to describe what land is and how it is used, which
  changes little from one year to the next; the year-to-year swings that drive yield anomalies are better seen in
  Sentinel-2 indices and weather.
- Embeddings stay useful where land differs, not where years differ: matching fields (WP3 E3) and, next, detecting
  land-use change (WP2) and scheme options (Paper 3).
