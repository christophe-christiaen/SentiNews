# W3-B1 baseline-variability check on H1

Protocol: [w3_b1_baseline_sd_protocol.md](w3_b1_baseline_sd_protocol.md). Exploratory; H1's registered reading is unchanged. H1 reproduced first: +0.082.

**Label: scaling artefact supported, on both samples.** Agreement fields had more variable July NDVI before entry than the fields they are compared with. NDVI falls sharply in shock seasons, so the same fall becomes a smaller z-score fall for them. Once fields are compared only with others of similar baseline variability, H1 disappears.

| | X2 sample (frozen) | E3 sample |
|---|---:|---:|
| 1. Baseline SD, agreement vs comparison, log difference within cell | +0.105 (+0.099, +0.111) | +0.059 (+0.052, +0.065) |
| As a ratio of SDs | 1.11 | 1.06 |
| Median baseline SD, agreement / comparison | 0.182 / 0.167 | 0.182 / 0.174 |
| Share at the 0.02 floor, agreement / comparison | 1.3% / 1.5% | 1.3% / 1.4% |
| 2. Comparison fields, raw July NDVI change, shock minus other seasons | -0.167 (-0.173, -0.161) | -0.169 (-0.175, -0.163) |
| H1, frozen z-score | +0.082 (+0.049, +0.115) | +0.087 (+0.050, +0.123) |
| 3. H1 with strata by baseline-SD tercile | -0.010 (-0.042, +0.021) | +0.021 (-0.012, +0.055) |

Tercile cuts of baseline SD over all fields: 0.135 and 0.216. Fields with an SD of exactly 0, dropped from part 1: 0.

## Reading

- **All three conditions hold.** Agreement fields' baseline SD is 11% higher on the frozen sample and 6% higher on the E3 sample. July NDVI falls by about 0.17 in shock seasons. A fall of 0.17 divided by an SD about 11% larger is a z-score fall smaller by about 0.1 SD, the size of H1.
- **With strata by baseline-SD tercile, H1 is −0.010 (−0.042, +0.021) on the frozen sample** and +0.021 (−0.012, +0.055) on the E3 sample. Terciles are coarse, so some of the mechanism may remain even there.
- **So H1's positive z-score result is best explained by how the outcome is scaled, not by agreement land holding its greenness.** This agrees with the raw, ratio and shared-scale results of the same day, all near zero.
- **This does not show agreements have no effect.** It shows the registered H1 can't be read as evidence of one. H1 already failed its placebo; whether the placebo reflects the same scaling hasn't been tested.
- **Why matching missed it:** it balanced each field's mean half-month NDVI, not its variability. The E3 sample, matched also on embeddings, roughly halves the gap, but not enough.
- **Other z-score outcomes:** the July NDMI, NDRE, peak and integral rows, the frozen H2 and H3, and Part F's July z-score rows share the scaling and should be read with the same caution. The harvest index (t/ha) does not.
