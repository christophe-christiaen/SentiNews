# W3-S protocol: every ELMs option, and how combinations within a field add up to resilience

**Status: registered 30 October 2026 by public commit, before the option crosswalk was built or linked to any outcome
or EO feature.** Builds on the WP3 decisions record ([preregistration.md](preregistration.md):
H1 contrast, section 7 matching, frozen-plan estimator, shocks), W3-4 ([w3_4_metric_protocol.md](w3_4_metric_protocol.md)),
and the option-group protocols registered on 30 October 2026: wet grassland
([w3_4_wet_grassland_protocol.md](w3_4_wet_grassland_protocol.md)), linear features
([w3_1_linear_features_protocol.md](w3_1_linear_features_protocol.md)), ponds ([w3_w_ponds_protocol.md](w3_w_ponds_protocol.md))
and the harvest ([w3_h_harvest_protocol.md](w3_h_harvest_protocol.md)). Exploratory. Changes after registration go
in the record at the end.

## Why
The programme asks whether EO can help policy on the physical and economic resilience of UK farming. Farmers rarely
take one option: a field may carry a herbal ley, a new hedge on its boundary and a pond. Policy pays for each option
separately but hopes they add up. Two questions:
1. **Coverage:** can every option be placed in a group and a family, so that nothing is dropped silently?
2. **Stacking:** within the same field, do options from different groups add up in resilience, both physical
   (greenness and moisture in shocks) and economic (harvest)? Do they add up exactly, or by more or less than the sum
   of their single effects?

## Part A: every option, in a crosswalk fixed before any outcome
- **Scope:** every option or action code in the national layers with entries 2021–2024: Countryside Stewardship
  options, SFI actions, and Environmental Stewardship options still live.
- **Crosswalk:** each code is assigned, from its official description and unit alone, to:
  - **a group:** land management, linear features, ponds and water, or other;
  - **a family:** the existing W3-4 families, the three option-group protocols, or a new family;
  - **an expectation:** visible from 10 m data, not visible (a negative control), or not testable from space.
- **Not testable:** capital items, buildings and features unrelated to land cover, such as fencing, gates, farm
  buildings, deer and squirrel control, and payment supplements. Each is listed with its reason, and fields where such
  codes are the only ones are counted.
- **New families:** codes with at least 1,000 parcels that fit no existing family become families of their own and are
  tested under the W3-4 rules on the appropriate frame. Candidates seen in the counts include:
  - low-input permanent grassland (GS2, GS5);
  - species-rich grassland (GS6, GS7, GS13, GS14);
  - organic land (OT, OR);
  - field corners out of management (GS1);
  - beetle banks (AB3, linear);
  - riparian strips (SW11, linear and water);
  - in-field trees (BE1, BE2);
  - traditional orchards (BE4);
  - lowland heathland (LH1);
  - seasonal livestock removal (SW9, SW10; not visible).

  The crosswalk is built from code, description and unit only. It is committed publicly in its own commit before any
  outcome or feature is linked to it, and is not changed afterwards except through the record.
- **Small codes are kept, not dropped:** a code with fewer than 1,000 parcels joins the nearest existing family of the
  same group and expectation. If none fits, it joins an "other" family for its group (for example "other water").
- **Coding:** one coder (no second coder is available). The crosswalk is drafted from the descriptions and reviewed by
  the project lead, and every assignment that is not obvious is flagged in a note column. No agreement statistic is
  reported; this is stated as a limit.

## Part B: stacks within a field
- **Unit:** a field (RPA parcel) entering agreements in 2021–2024. SFI actions are snapped as in the decisions record.
- **Stack:** the set of groups present on the field: land management (L), linear (I), water (W). The seven non-empty
  combinations are L, I, W, L+I, L+W, I+W and L+I+W. The number of distinct families is a secondary dose measure.
  - **Counts** (Countryside Stewardship only, rough coding, entry 2021–2024; checked 30 October 2026):
    - I 177,689; L 149,919; L+I 60,211; W 7,118;
    - L+W 2,488; I+W 2,171; L+I+W 916.
  - Snapped SFI hedgerow actions add many I and L+I fields.
- **Frames:** cereal land (W3-4 frame) and grassland (U1 definition), analysed separately.
- **Declared and verified versions:**
  - Primary: stacks from declared options.
  - Secondary: stacks built only from families that pass W3-4 detection beyond selection on that frame (verified
    stacks). This is the policy-relevant version for payment by results.

## Part C: does resilience add up?
- **Physical:** WP3's H1 contrast (shock minus non-shock seasons, July NDVI z-score; NDMI on grassland) in one model.
  The regressors are shock × each group indicator, plus shock × each pairwise and the three-way group interaction.
  The comparison is matched never-treated fields (section 7 matching with E3 AlphaEarth components, done separately
  for each stack). Strata are ERA5 cell × season; SE clustered by ERA5 cell; seasons 2017–2026; before-entry placebo
  2017–2020.
- **Economic:** the same model with W3-H's field harvest index as the outcome, on cereal land, for crops that pass W3-H's
  Defra gate. Reported in t/ha and £/ha.
- **Additivity:** for each pair, δ = effect(pair) − [effect(first alone) + effect(second alone)], and the same for the
  triple, by bootstrap over ERA5 cells.
- **Dose:** the H1 contrast by the number of groups (0, 1, 2, 3) and by the number of families.

## Selection into stacks
Farms that stack options may differ from farms that do not. Three designs, all reported:
1. **Matched against never-treated** (above).
2. **Within agreements:** stacks compared with single-group fields of agreement holders only. Every field's farmer
   chose to join, so this removes joining as a difference.
3. **Within farms:** if the farm grouping (`shared/data/farms`) can group fields into holdings, fields of the same
   holding with different stacks are compared (holding × season fixed effects). This removes farm-level differences.
   It is not run if the grouping is unusable.

The before-entry placebo is run for every design. A stack effect is read only if it survives design 2.

## Reading, fixed in advance
- A stack **adds up** if its effect is positive with a 95% interval above zero and its additivity term's interval
  includes zero.
- It is **more than additive** if the additivity term is positive with an interval above zero, and **less than
  additive** if the term is negative with an interval below zero.
- Anything else is "not shown".
- Each reading needs the before-entry placebo's interval to include zero, and the result to hold in design 2.
- **Minimum detectable effects:** for stacks with fewer than 5,000 fields (W, L+W, I+W, L+I+W), the MDE is reported
  before the estimate. If it exceeds 0.10 SD, the result is reported as underpowered and not read.
- **Expectation stated now, not used in the rules:**
  - L+I adds up roughly additively.
  - Stacks with water are underpowered.
  - The verified-stack version is stronger than the declared one.

## Compute and data
- Part A uses only scheme metadata (descriptions and units), no outcomes.
- Part B and Part C reuse the features and outcomes extracted under the option-group, W3-4 and W3-H protocols. Stack
  analysis needs no new imagery beyond theirs.

Per-parcel data stay out of the public repository; the crosswalk (codes only) is public.

## Output
`wp3_elms_effect/results/w3_s_crosswalk.csv` (codes, groups, families, expectations); `w3_s_option_stacks.md`,
`.json` (aggregates only).

## Decisions before registration (settled 30 October 2026)
1. **Second coder:** none available; one coder, reviewed by the project lead (Part A).
2. **New-family threshold:** 1,000 parcels (default; the project lead had no preference). Smaller codes are pooled, not dropped (Part A). With about 1,000 positives, the I* interval is roughly twice as wide as for the 3,000-positive families, so only larger effects can count as detected.
3. **Environmental Stewardship:** ES options still live in 2021–2024 are included.

## Record
| Date | Change | Reason |
|---|---|---|
| 2026-10-30 | Draft written, before the crosswalk was linked to any outcome or feature | Project lead's request: keep every option and test how combinations within a field add up |
| 2026-10-30 | Decisions settled (one coder reviewed by the project lead; threshold 1,000 with smaller codes pooled; ES included); registered by public commit | Project lead's decisions |
