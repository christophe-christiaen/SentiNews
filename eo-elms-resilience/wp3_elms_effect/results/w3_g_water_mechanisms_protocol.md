# Addendum 7: flood and drought by water mechanism, alone and together

**Status: registered 2 November 2026 by public commit, before the group assignment was linked to any outcome and
before any contrast below was estimated.** Builds on the
WP3 decisions record ([preregistration.md](preregistration.md): section 5 shocks, H1 contrast, section 7 matching,
frozen-plan estimator), W3-S ([w3_s_option_stacks_protocol.md](w3_s_option_stacks_protocol.md): crosswalk, stacks,
selection designs, additivity), addendum 6 ([w3_z_addendum6_hazards_protocol.md](w3_z_addendum6_hazards_protocol.md):
wet shock, inundation layer, establishment and recovery outcomes) and W3-H
([w3_h_harvest_protocol.md](w3_h_harvest_protocol.md)). Exploratory; it does not change H1–H3. Changes after
registration go in the record at the end.

## Why
W3-S groups options by what they look like on the ground (land management, linear features, water). Addendum 6 tests
families against the wet shock one at a time. Neither asks the policy question by how an option should act on water.
An option can only change four things:
1. how much rain soaks in;
2. how fast runoff moves;
3. how much water is stored;
4. how much water the vegetation uses.

The same option can help in a flood and hurt in a drought. Options are also meant to work in sequence down a slope:
less runoff starts on covered soil, strips and hedges catch what does run off, and storage holds the rest. This
addendum asks:
1. **Alone:** does each water-mechanism group cushion fields in wet seasons, in dry seasons, or both?
2. **Together:** do source and pathway groups on the same field add up, and is the sum more than additive in wet
   seasons, as the sequence argument predicts?
3. **Trade-off:** does any group that helps in wet seasons cost in dry ones (above all, soil cover in a dry spring)?
4. **Where:** are effects larger on fields that were prone to waterlogging or bare soil before entry?
5. **When:** do quick-acting groups show effects from the first season and slow ones only later?

It measures field-level resilience (greenness, establishment, recovery, harvest), not river flows or catchment flood
peaks. Catchment effects are outside what this design can show, and the write-up says so.

## Mechanism groups, fixed from the W3-S crosswalk before any outcome
Each W3-S family is assigned to one group by the rules below, from the crosswalk's codes and descriptions only. The
assignment is committed publicly with this addendum's registration, after the W3-S crosswalk is committed and before
either is linked to any outcome.

| Group | Mechanism | Families (W3-S / W3-4 names) |
|---|---|---|
| **S, source** | Soil cover and structure: more infiltration, less surface evaporation | cover crops, winter cover, no-till / direct drill, herbal and multi-species leys, SFI soil health actions (SOH) |
| **P, pathway** | Rough, permeable ground or barriers that catch overland flow | buffer strips (SW1, SW3, SW4, WT2), in-field grass strips, beetle banks, riparian strips, hedgerow management and creation, walls and banks |
| **K, storage** | Water held on the land | ponds, wet grassland, floodplain and wetland options |
| **V, conversion** | Permanent cover replacing arable: lasting change in infiltration and water use | arable reversion, low-input and species-rich grassland, field corners, in-field trees, woodland, agroforestry, orchards |
| **N, no water mechanism** | Negative control | nutrient management, IPM, seasonal livestock removal, other management-only actions |

- A family that fits two groups goes to the one whose mechanism its description names first. Such cases are flagged in
  a note column.
- Families that W3-S marks "not testable" stay out.
- Single-group combinations and stacks are built exactly as in W3-S Part B (the field's set of groups present), on the
  declared and the verified versions.

## Hazards (weather and water only, never from the crop)
- **Wet:** addendum 6's wet shock (October–March rainfall at least 30% above the 1991–2020 normal, per ERA5-Land cell
  and season). Secondary: addendum 6's observed inundation layer, only if it passes addendum 6's checks.
- **Dry:** section 5's dry shock (March–July). Severe dry shock as a secondary version.
- **Dry spring (new, for test 3):** March–April rainfall at least 30% below the 1991–2020 normal, per cell and season.
- Heat shock is not used: it is not a water mechanism.

## Outcomes
These are the same outcomes as addendum 6 Part F and H1, with no new outcome definitions:
- **establishment:** February–March share of clear dates with NDVI above 0.3;
- **summer:** July NDVI z-score (NDMI on grassland);
- **recovery:** first half-month back within 1 SD after an inundated season;
- **economic:** W3-H harvest index for crops passing its Defra gate, in t/ha and £/ha.

## Tests
All use the W3-S Part C estimator and frames:
- shock × group indicators against matched never-treated fields (section 7 matching with E3 AlphaEarth components, by
  stack);
- strata: ERA5 cell × season; SE clustered by ERA5 cell;
- seasons 2017–2026; before-entry placebo 2017–2020;
- cereal and grassland frames separate.

1. **Alone (T1).** The effect of each group alone in wet-shock seasons, and separately in dry-shock seasons, against
   non-shock seasons. Fields with only that group are used. Group N is the negative control: its interval should
   include zero for both hazards.
2. **Together (T2).** For S+P, S+K, P+K and S+P+K, additivity δ = effect(stack) − sum of single-group effects, by
   bootstrap over ERA5 cells, for wet and dry hazards separately. The sequence prediction is δ > 0 for S+P in wet
   seasons.
3. **Trade-off (T3).** For each group: the difference between its wet-season effect and its dry-season effect.
   Separately, the effect of S in dry-spring seasons on establishment and July NDVI. A cost shows up as a negative
   effect.
4. **Where (T4).** T1 and T2 split by pre-entry susceptibility tercile. Susceptibility is computed for all fields,
   whatever their agreement status, from 2017–2020 only:
   - **(a) waterlogging propensity:** mean winter Sentinel-1 VH anomaly from the E2 panel;
   - **(b) bare-soil exposure:** share of clear December–February Sentinel-2 dates with NDVI below 0.2;
   - **(c) slope:** mean slope from an open terrain model, verified before use (see decisions).

   The prediction is a larger effect in the top tercile, tested as top minus bottom tercile.
5. **When (T5).** T1 by seasons since entry: 1, 2, and 3 or more. The prediction is that S and P show effects from
   season 1 and V only from season 3.

## Selection
This uses the same three designs as W3-S: matched against never-treated, within agreements, and within farms if the
grouping is usable. Any reading requires two things:
- the result holds in design 2;
- the before-entry placebo interval includes zero.

Water options are placed where land is wet, so the Flood Zone 3 and deep-peat stratification is reported for every
result (as in addendum 6), along with T4's pre-entry susceptibility.

## Reading, fixed in advance
- **Cushion "indicated":** effect positive with a 95% interval above zero, placebo interval including zero, and holding
  in design 2. **Cost "indicated":** the same, with the interval below zero.
- **Additivity:**
  - more than additive if δ's interval is above zero;
  - less than additive if it is below zero;
  - additive if the stack is indicated and δ's interval includes zero.
- **Trade-off:** indicated if the wet-minus-dry difference has an interval excluding zero and one of the two effects
  is itself indicated.
- **T4 and T5 are descriptive.** Their contrasts are reported with intervals but do not count as findings on their own.
- **Minimum detectable effects** are reported before each estimate. Any cell (group or stack × hazard × frame) with an
  MDE above 0.10 SD is reported as underpowered and not read. K and stacks containing K are expected to fall here.
- **Negative control:** if group N shows an indicated cushion or cost for either hazard, every reading is marked as
  possibly confounded by selection.
- Exploratory, with no multiple-testing correction. The number of contrasts estimated is reported next to the number
  indicated.

## Expectations stated now, not used in the rules
- S and P are indicated for wet seasons on the cereal frame; V on both frames once it has been in place 3+ seasons.
- S+P is roughly additive, not clearly more than additive, because fields rarely line up along the same flow path.
- S shows no clear dry-spring cost in the national average but may in the top bare-soil tercile.
- K is underpowered.
- N is null.

## Compute and data
- No new imagery. Outcomes, matching and Sentinel-1/-2 panels come from H1, E2, addendum 6 and W3-H.
- Susceptibility (a) and (b) are computed from existing pre-entry panels.
- Slope needs one open terrain model for England. Its licence is checked, and its download asked for, before use.
- Requires the W3-S crosswalk to be committed first.

Per-parcel data stay out of the public repository. The group assignment (codes only) and aggregates are public.

## Output
- `wp3_elms_effect/results/w3_g_groups.csv`: family to group, with notes.
- `w3_g_water_mechanisms.md` and `.json`: aggregates only.

## Decisions before registration (settled 2 November 2026)
1. **Group assignment:** the five groups and the assignment rule above, as drafted.
2. **Slope:** T4(c) included. Slope comes from one open terrain model for England. Before it is downloaded, its licence
   is checked and the download is approved by the project lead. If no open model passes, T4(c) is dropped and the
   record says so.
3. **Dry-spring hazard:** added as defined (March–April rainfall at least 30% below the 1991–2020 normal), from weather
   only.
4. **Order:** this runs after W3-S Part A (crosswalk committed) and addendum 6 Part F, and reuses their outputs.

## Record
| Date | Change | Reason |
|---|---|---|
| 2026-11-02 | Draft written; no outcome read for any contrast | Project lead: test ELMs actions as flood and drought mitigants, independently and together |
| 2026-11-02 | Decisions settled (groups and rule as drafted; slope included, subject to licence and download approval; dry-spring hazard added; runs after W3-S Part A and addendum 6 Part F); registered by public commit | Project lead's decisions |
| 2026-11-02 | **Group assignment built from the committed W3-S crosswalk, approved by the project lead and committed before it is linked to any outcome** ([`src/w3_g_groups.py`](../src/w3_g_groups.py); [w3_g_groups.csv](w3_g_groups.csv)). 32 families: S 4 (37 codes), P 5 (121), K 6 (61), V 7 (120), N 10 (145). Readings of the table: (1) in-field flower and bird-food plots, not listed, go to S (soil cover named first); (2) "woodland" under V is read as woodland creation; woodland management (existing woodland, no change in cover) goes to N; (3) organic, moorland grazing, rush pastures, historic grassland, lowland heath (mostly management of existing heath) and other land go to N, as their descriptions name no water mechanism; (4) area strips stay in P although they include overwinter stubble and low-input cereal (AHW6–8, AHW10) as registered in W3-4 and W3-1, flagged | Assignment step; project lead's approval |
