# W3-M protocol: selection-invariant detection (SID)

**Status: registered 19 November 2026 by public commit, before any SID feature, model or statistic was computed. Exploratory.** Changes after registration go in the record at the end.

## Why
I\* fixes the *measurement* of detection: it subtracts what a pre-entry year adds. But it is a metric, not a detector.
- **The deployment problem:** an inspector checking a field has no management-only comparison group. The realistic comparison is land never in a scheme (comparison A).
- **What goes wrong there:** a standard detector scores about AUC 0.7 against A even for actions it can't see, because land that joins was already different ([option_detection.md](option_detection.md); [w3_4_model_comparison.md](w3_4_model_comparison.md)).
- **What SID tries:** build detectors whose scores carry no pre-entry selection, so that they can be used against never-enrolled land directly. Paper B lists the three variants below as pending (planned as W3-M).

## Frame (fixed)
These are the same as the four-model comparison, so results line up with I\*, ΔAI and #9:
- **Labels and samples:** option families, sampling, and comparisons B (management-only scheme land) and A (never-treated).
- **Years:** pre-entry record = mean of 2018–2019; placebo year 2020 (before every entry); post = 2025.
- **Evaluation:** leave one region out, eight regions, held-out scores pooled.
- **Products, all four primary:** Sentinel-2 indices (no AI), AlphaEarth, TESSERA and Presto (AI). Each detector gets a label for each product.
- **Reference detector (STD):** gradient-boosted trees on X_post, as published.

## The three detectors
1. **SID-Δ (within-field change).** Features X_post − X_pre. Stable field traits cancel. Gradient-boosted trees, settings as STD.
2. **SID-R (residualised).** Within each training fold only, a multi-output ridge regression predicts X_post from X_pre, cross-fitted over five inner folds by 10 km block. Penalty chosen by inner-fold prediction error; no labels are used. The detector is trained on the residuals X_post − X̂_post. The held-out region's residuals use the training-fold regression. Same tree settings.
3. **SID-A (adversarial).**
   - **Network:** a small network (two layers of 64 units, ReLU, float32) encodes a field's record z = f(X).
   - **Two heads:**
     - a detection head g(z_post), trained to predict enrolment from the post record;
     - an adversary a(z_pre), trained through gradient reversal to predict enrolment from the **pre-entry** record encoded by the **same** encoder.
   - **Why it works:** before entry no action exists, so any enrolment signal in f(X_pre) is selection. The encoder is pushed to drop features that carry it.
   - **Training:** loss = BCE(g(f(X_post)), y) − λ · BCE(a(f(X_pre)), y). Adam, learning rate 1e-3, 60 epochs, batch 512, seeds 0–4, scores averaged.
   - **Choosing λ:** from {0.3, 1, 3} by inner leave-one-region-out within the training regions, maximising AUC(post) − AUC(pre) on the inner held-out region. Negative controls are never used to choose λ.

## What is measured, for each detector, product and family
- **Against never-treated land (A), the target use:** held-out AUC on X_post, called **D**.
- **Pre-entry placebo:** the same detector with X_post replaced by the 2020 record, called **D₀**. Nothing existed in 2020, so a selection-free detector should give D₀ ≈ 0.5.
- **Against management-only land (B):** D reported beside, for comparison with I\*.
- **Intervals:** 1,000 resamples of 10 km blocks within held-out regions, seed 29 (as in #9). The parcel bootstrap is reported beside.

## Reading, fixed in advance
- **Detects (family):** D − 0.5 has a 95% interval lower end above 0.02 (comparison A).
- **Calibrated (detector):**
  - both negative controls (buffer strips, management only) have D within 0.5 ± 0.02 against A;
  - and every family's placebo D₀ is within 0.5 ± 0.02.
- **Label per detector and product:**
  - **SID works:** calibrated, and at least 4 of the 5 families that I\* detects (herbal leys, no-till, cover crops, in-field plots, grassland options) are detected.
  - **Partial:** not calibrated, but both controls' distance from 0.5 is at most half of STD's. Or calibrated, with fewer than 4 families detected. The parts that hold are stated.
  - **Fails:** anything else.
- **Paper B rule (consolidation plan):** SID enters Paper B only if some detector is "works" or "partial" on at least one product. Otherwise it is reported as tried and dropped. With 3 detectors × 4 products there are 12 labels, all reported. One "works" among twelve is read as a lead to confirm, not as a finding.
- **Expected and stated, not used in the rules:**
  - STD fails: its controls are at about 0.70 against A.
  - SID-Δ removes most of the selection but keeps some, because land that joins may also be on a different trend.
  - SID-A is the strongest, and the most sensitive to λ.

## Limits
- SID removes selection that **shows in the pre-entry record**. Selection on things a satellite never sees, such as the farmer's intent, is untouched. The placebo D₀ can't test for it.
- Change-based detectors are also sensitive to anything else that changed between 2018–2019 and 2025, such as crop rotation. The placebo year tests this only in part.
- Labels are declared, not verified, and fields are sampled at a point. Edge options remain out of reach.
- This is exploratory. One programme and one country.

## Known before this draft
- **Published:** STD AUCs against A and B (option detection) and all I\* results (four-model comparison, #9).
- **ΔAI:** the interim run is in progress. Its log has printed point estimates of I\* for N and N + each embedding for herbal leys (against B and A), and these were seen. Cover crops' lines had printed but their values were not read. No ΔAI interval or reading has been computed.
- **Not computed:** no SID feature, model or statistic.

## Output
`wp3_elms_effect/src/w3_m_sid.py`; `wp3_elms_effect/results/w3_m_sid.md`, `.json` (aggregates only).

## Record
| Date | Change | Reason |
|---|---|---|
| 2026-11-19 | Draft written from Paper B's pending section 4 and W3-M in the publication plan | Project lead: draft the SID protocol |
| 2026-11-19 | Registered with all four products primary (the draft had Sentinel-2 and AlphaEarth primary); the Paper B rule and the note on twelve labels adjusted to match | Project lead: register now with all four products |
