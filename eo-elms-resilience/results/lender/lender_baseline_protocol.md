# Protocol X1: lender score under a long baseline

**Written 17 October 2026, before the check was run.** The protocol and its result are committed together; the order (protocol, then run) is recorded in the project's internal plan record.


**Question.** How much of the lender score's back-tested skill comes from the 4-season normal shared by its features
and its target?

**Design.** Same features, targets, models, rolling-origin back-test (scoring seasons 2020–2025, training on earlier
seasons from 2018) and metrics as `src/lender_score.py`. Only the stress index S changes. Parcels with both Sentinel-2
and MODIS values; panel restricted to 2017–2026 in all versions, so history features cover the same seasons.
- **V0:** Sentinel-2, normal 2017–2020 (the published score, on the common parcels).
- **V1:** MODIS, normal 2017–2020 (same sensor as V2, short normal).
- **V2:** MODIS, normal 2001–2016 (16 seasons, entirely before the panel).
Shocks, weather features and regions unchanged. MODIS S uses the July and peak windows of the WP2 long-baseline
check, clipped to ±6; targets use the same thresholds (hit hard = S ≤ −1; worst 20% of region).

**Reading, fixed in advance.** The V1 − V2 difference in AUC (transparent score, hit hard next season) is the part
of the skill due to the short normal; V2 is the skill that does not depend on it. If V1 − V2 ≥ 0.03, the deck's
numbers are described as inflated by the short baseline and replaced by V2-type numbers where possible. The by-year
pattern is compared across versions: if the rise from 2020 to 2025 is much weaker in V2, "gets better with history"
is withdrawn. Limits: MODIS pixels are 250 m and mix neighbouring fields; a 2001–2016 normal can drift by 2017–2026
(WP2 found a post-baseline artefact), so V2 is not artefact-free, only free of the in-panel shared error.

Output [lender_baseline_check.md](lender_baseline_check.md), `.json`.
