# W3-4 seasonal cover-crop test: does a winter view see cover crops better?

**Written 30 October 2026, before any winter feature or winter embedding was computed, and before the Presto inputs
for season 2026 were extracted.** Builds on [w3_4_metric_protocol.md](w3_4_metric_protocol.md) (metric, sample,
leave-one-region-out models, calibration and selection-invariance checks) and
[w3_4_model_comparison_protocol.md](w3_4_model_comparison_protocol.md) (paired bootstrap, Holm correction). What is
already known: in the model comparison, full-season Presto gave cover crops I* +0.057, the plain Sentinel-2 indices
(March–August) +0.054, TESSERA +0.087 (calibration failed) and AlphaEarth +0.072. Changes after this date go in the
record at the end.

## Question
The cover-crop family was detected by every model, but weakly, and the expectation that Presto would do best on it
was not borne out. Every model so far used a whole-year or March–August record, while a winter cover crop is on the
ground in winter. Does a view of the winter months alone detect winter cover crops better beyond selection, with AI
(Presto) and without (plain radar and optical values)?

## What the options require (checked 30 October 2026)
- **SAM2 (SFI 2023) and CSAM2 (SFI 2024), multi-species winter cover crop:** "well-established over the winter
  months", "usually from early December until late February", present between harvesting a cash crop and establishing
  the next; may be destroyed before the end of winter only for an early-sown spring crop, at most 6 weeks before it is
  sown (gov.uk, CSAM2 page, last updated 17 June 2026).
- **SOH3, multi-species summer-sown cover crop:** established "during the summer months (usually between June and
  August)", kept until the next main crop is sown (gov.uk, SOH3 page).
- **SOH2, multi-species spring-sown cover crop:** spring-sown. The gov.uk action page has been withdrawn (HTTP 410);
  the name is from the SFI 2024 actions document. No requirement dates are relied on.

The W3-4 cover-crop family (SAM2, CSAM2, SOH2, SOH3) therefore mixes timings. This test splits it:
- **Winter cover (primary):** SAM2, CSAM2.
- **Spring- and summer-sown cover (secondary, descriptive):** SOH2, SOH3.

The other families, the negative controls and the comparison groups are unchanged.

## Design
- **Labels and parcels:** the W3-4 sample (fixed seeds), the same agreement snapshot (SFI option data dated 4 November
  2025), comparison B (management-only scheme land) primary, A (never-treated land) for the checks.
- **Winter window:** December, January, February (Presto input months m03, m04, m05; month 1 = October).
- **Records (I* as in W3-4):**
  - pre-entry = mean over the winters of seasons 2018 and 2019 (December 2017–February 2018, December 2018–February
    2019);
  - I₀ = winter of season 2020 (December 2019–February 2020);
  - **post (primary) = winter of season 2026 (December 2025–February 2026)**, the first winter in which every
    agreement in the November 2025 snapshot was live;
  - post (secondary) = winter of season 2025 (December 2024–February 2025), as in W3-4.
- **Versions (four):**
  - **V1 Presto, full season (AI, reference):** the existing 128-value Presto embedding, October–September.
  - **V2 Presto, winter (AI):** the same pretrained encoder given only the three winter months (start month December),
    same normalisation and masking as `presto_embed.py`.
  - **V3 Winter values, radar and optical (no AI):** per winter month, Sentinel-2 NDVI and NDMI (from B4, B8, B11) and
    Sentinel-1 VV, VH and VH − VV, from the same Presto input files: 15 values, missing months left missing.
  - **V4 Winter radar only (no AI):** Sentinel-1 VV, VH, VH − VV per winter month: 9 values.
- **Model, metric and uncertainty:** as in W3-4 (gradient-boosted classifiers, leave-one-region-out, I* = [AUC(pre +
  post) − AUC(pre)] − [AUC(pre + I₀) − AUC(pre)]); paired bootstrap of I* differences, 1,000 resamples of parcels within
  held-out regions, the same resample for all versions.

## Tests (winter cover, comparison B, primary post; Holm over the four)
- **T-a, does the winter window help Presto?** V2 − V1.
- **T-b, does AI add in winter?** V2 − V3.
- **T-c, winter values without AI against full-season Presto:** V3 − V1.
- **T-d, is radar alone enough?** V4 − V3.

## Reading, fixed in advance
- **Validity first.** Each version must pass the W3-4 checks on the primary post winter: negative controls against
  never-treated land within ±0.02, and |I*(A) − I*(B)| < 0.03 for winter cover. A version that fails is reported, but a
  test in which it comes out ahead is read as "not established" (as for TESSERA).
- **Detection:** winter cover is detected by a version if its I* 95% interval lies above 0.02.
- **T-a, T-b, T-c:** the first version is better if the difference is positive with Holm-adjusted p < 0.05; worse if
  negative with p < 0.05; otherwise "no difference shown".
- **T-d:** "radar alone is enough" if the 95% interval of V4 − V3 lies within ±0.02; "optical adds" if V4 − V3 < 0 with
  Holm-adjusted p < 0.05; otherwise inconclusive.
- **Secondary, reported with the same rules but not counted in the primary reading:**
  - post = winter of season 2025;
  - post = winter of season 2025, restricted to parcels whose CROME 2025 crop is spring-sown, in both groups (a
    winter cover crop precedes a spring crop, so this compares like rotations). Spring-sown = the CROME 2024 lookup codes
    described as "Spring …" (AC01, AC16, AC19, AC24, AC30, AC32, AC34, AC36, LG03, LG07) plus Maize (AC17), Beet (AC03)
    and Potato (AC44): 13 codes. No CROME map exists yet for 2026, so the primary test cannot be
    restricted this way;
  - the spring- and summer-sown family (SOH2, SOH3), all versions, descriptively.
- **Expectations stated before the result, not used in the rules:** V2 beats V1 for winter cover by at least 0.02;
  V3 is close to V2; radar alone is weaker than radar and optical; the winter window helps SOH2 and SOH3 less than
  winter cover.

## Known risks, stated in advance
- **Sentinel-1 in winter 2025/26.** WP2 found Sentinel-1 reads dark that winter despite record-wet soils, most likely
  standing water ([s1_orbit_panel_quality.md](../../shared/results/s1_orbit_panel_quality.md)). It is used as it is in
  the primary test. If V4 fails the calibration check on that winter but passes it on the winter of season 2025, the
  radar result is read from the secondary test and the reason is recorded.
- **Radar values** in the Presto inputs are means over all orbits without angle normalisation, so a change in which
  satellites flew can shift a winter; the I₀ correction and the region-held-out models absorb shifts common to both
  groups, not ones that differ between them.
- **Winter cereals** are green in winter too; cover crops are told apart from bare or stubble fields, not from winter
  crops. The spring-crop restriction is the check on this.
- **Labels** are declared, not verified.

## Data still to obtain
Presto inputs for season 2026 (October 2025–September 2026) at the W3-4 parcels, with `presto_inputs.py --seasons 2026`
(about 75 minutes, judging by the previous run); then V1 for season 2026 and V2 for seasons 2018, 2019, 2020, 2025 and
2026. No new download outside Earth Engine.

## Output
`wp3_elms_effect/results/w3_4_cover_seasonal.md`, `.json` (aggregates only).

## Record
| Date | Change | Reason |
|---|---|---|
| 2026-10-30 | Protocol written, before any winter feature, winter embedding or season-2026 input existed | Next step after the model comparison: cover crops with a seasonal Presto and Sentinel-1 view |
| 2026-10-30 | Results ([w3_4_cover_seasonal.md](w3_4_cover_seasonal.md)). Reading under the rules above: on the primary post winter (2025/26, comparison B) only **V2, Presto winter, passes both checks** (controls +0.007, +0.006; |A − B| 0.019) and **detects winter cover**, I* +0.068 (+0.060 to +0.076). V1 passes calibration but misses selection invariance narrowly (|A − B| 0.031); V3 and V4 fail calibration (controls up to +0.024). All four detect winter cover. T-a, T-b and T-c are **not established** (in each the leading version, V1 or V3, fails a check). T-d: V4 − V3 −0.006 (−0.013 to +0.002), inside ±0.02. Because V4 fails calibration on winter 2025/26 but passes on the winter of season 2025, the radar result is read from the secondary test as the known-risks rule requires: V4 − V3 +0.011 (+0.002 to +0.018), **radar alone is enough**; reason: the dark Sentinel-1 winter of 2025/26 recorded by WP2. Secondary (not counted): on the winter of season 2025 all versions are valid but only V1 (+0.057) and V4 (+0.032) detect winter cover; restricted to spring crops, V1–V3 are valid and all detect it, and V2 is below V1 (Holm p 0.008). Expectations: V2 beating V1 was wrong (V1 is higher wherever it is valid); the winter window helping spring- and summer-sown cover less was right | Pre-set rules applied |
