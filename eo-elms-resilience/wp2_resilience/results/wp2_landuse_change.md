# WP2 W3: land-use change from embeddings

Specified in paper/outline.md on 17 October 2026 before running. Shift = distance between each field's mean AlphaEarth embedding 2017–2019 and 2023–2025; "changed" = top 5% nationally.

- Fields: 381,400; changed: 19,070 (shift ≥ 0.461).
- **(a) Validation:** left cereals in CROME (cereal ≥ 2 of 3 years 2017–19, ≤ 1 of 3 in 2023–25): 65.4% of changed fields vs 17.4% of others.
- **(b) Lasting offset** (mean Sentinel-2 stress 2021–2025 against the 2017–2020 normal): correlation with the shift -0.09 (with its size +0.18); mean offset -0.42 for changed fields vs -0.30 for others (size 1.05 vs 0.68).

**(c) Legacy test with and without changed fields** (cell × season effects, clustered by ERA5 cell):

| Sample | pooled legacy | season-shuffled placebo |
|---|---|---|
| all fields | +0.199 | +0.079 |
| changed fields excluded | +0.178 | +0.071 |

## Reading (17 October 2026)

- **Embeddings detect real land-use change.** Of the 5% of fields whose embedding shifted most, 65% left cereals in
  the crop map, against 17% of other fields (3.8 times as often). Multi-year means keep ordinary rotation out.
- **Changed fields drift further from their normal** (lasting offset 1.05 vs 0.68 SD), so part of the "lasting
  differences between fields" behind the WP2 correction is real change of use, not noise.
- **But only a small part.** Leaving the changed 5% out moves the pooled legacy test from +0.199 to +0.178 and the
  season-shuffled placebo from +0.079 to +0.071: about a tenth. The rest is consistent with the short four-season
  normal, as found in the within-field check and the MODIS long-baseline test.
- For Paper 2: embeddings give an independent way to separate land-use change from measurement artefact, and they
  confirm the correction rather than overturn it.
