# Addendum 5 (cross-protocol): precomputed OlmoEarth v1.3, a tillage index, what AI adds to the indices, per-pixel change for ponds, and a LiDAR hedge check

**Status: registered 30 October 2026 by public commit, before any feature named here was extracted for any parcel.** Applies to
the detection parts of W3-4 ([w3_4_metric_protocol.md](w3_4_metric_protocol.md),
[w3_4_model_comparison_protocol.md](w3_4_model_comparison_protocol.md)), the wet grassland addendum 4
([w3_4_wet_grassland_protocol.md](w3_4_wet_grassland_protocol.md)), linear features
([w3_1_linear_features_protocol.md](w3_1_linear_features_protocol.md)) and ponds
([w3_w_ponds_protocol.md](w3_w_ponds_protocol.md)). It changes none of their rules. It adds products, one test and one
validation layer. Exploratory; changes after registration go in the record at the end.

## Why
On 30 October 2026 the project lead reviewed suggestions from a general-purpose AI assistant on EO products for ELMs
options. Five survived checking against primary sources and the programme's own results; the rest were dropped
(MODIS for field-level detection, too coarse; SAVI and EVI, largely redundant with NDVI; Landsat for pond baselines,
a 0.05 ha pond is smaller than one 30 m pixel; and unsupported claims about label efficiency). The W3-4 land-management
results (18 and 29 October) were known when this addendum was written, so everything here applied to those families
is exploratory and does not revise their readings.

## 1. OlmoEarth v1.3 precomputed embeddings (product OE13)
- **Source:** Ai2, *OlmoEarth v1.3 Embeddings*, Source Cooperative (`olmoearth/olmoearth-v1-3-embeddings`), released
  22 October 2026. One vector per 10 m pixel per **calendar year**, 128 dimensions stored as int8 (the first 64 are a
  complete embedding on their own), from OlmoEarth-v1.3-Base on twelve 30-day mosaics each of Sentinel-1, Sentinel-2
  and Landsat 8/9. Read by ranged requests; no imagery and no GPU needed.
- **Licence:** OlmoEarth Artifact License. Free use, with two use restrictions (no military or extractive uses), a duty
  to cite Ai2, and a duty to pass the restrictions on with any derivative. Any shared output built on OE13 (including
  the bank report) states this.
- **Coverage, checked 30 October 2026** from the public provenance tables only
  ([`src/check_olmoearth13_coverage.py`](../src/check_olmoearth13_coverage.py); 20.48 km windows whose centre falls in
  an England box, 826 in a complete year):

  | Year | 2017 | 2018 | 2019 | 2020 | 2021–2025 |
  |---|---|---|---|---|---|
  | Windows written | 0 | 0 | 458 | 826 | 826 each |

  Ai2 states that 2017–2020 are being backfilled "in the coming weeks".
- **Years:** calendar years, as for AlphaEarth: pre-entry = mean of 2017–2019, I₀ = 2020, post = 2025.
- **Gate:** OE13 is extracted for an analysis only when the check above shows every England window written for all the
  years that analysis needs (2017–2020 and 2025 for detection). The check is rerun on the first working day of each
  month and its output is logged in the record. Until then OE13 is not used, not even in part.
- **Width:** 64 dimensions (primary, the same size as AlphaEarth); 128 as a sensitivity check.
- **Sampling:** exactly as AlphaEarth in each protocol: the parcel point (land management, wet grassland), edge band and
  interior (linear features), and whole field pooled by mean and 95th percentile (ponds).
- **Relation to addendum 3's OE:** addendum 3 runs OlmoEarth-v1-Base ourselves on farm-season mosaics. OE13 is a
  different model version, input set and year definition, so it is a separate product. The two are compared
  descriptively (correlation of their first principal components at the same parcels, 2025).
- **Family:** AI, precomputed. The model sees a neighbourhood of pixels, so OE13 is not a pure single-pixel product.

## 2. A tillage index from Sentinel-2 (product S2T)
- **Index:** NDTI = (B11 − B12) / (B11 + B12), the two Sentinel-2 shortwave-infrared bands at 20 m. Crop residue absorbs
  near 2100 nm, so NDTI separates residue from bare soil, which the greenness and moisture indices do not target.
- **Features:** half-monthly NDTI March–August (as the existing indices) and monthly October–February (stubble and
  winter cover), with the same cloud masking. **S2T** = the existing Sentinel-2 indices plus NDTI.
- **Families:** no-till and cover crops (primary); all other land-management families reported. Frame, comparisons and
  I* rules as in W3-4.
- **Reading:** S2T is reported beside S2. A gain counts only through the W3-4 paired comparison (Holm over the families
  tested here). The published S2 readings stand whatever S2T shows.
- **Stated limit:** published studies of NDTI are mostly outside the UK and report saturation at high residue cover.
  Citations are verified before any is included.

## 3. What AI adds to the indices (ΔAI)
The W3-4 comparison set one product against another. Policy needs a sharper question: **given the open, no-AI
indices, does an embedding add anything?**
- **No-AI set N:** all no-AI products of the protocol, concatenated: S2T and Sentinel-1 for land management; S2W and
  Sentinel-1 for wet grassland; S2, S2 texture and Sentinel-1 (each in the version being tested) for linear features;
  the water counts for ponds. Using all of them avoids choosing a "best" no-AI product after seeing results.
- **ΔAI(E) = I*(N + E) − I*(N)** for each embedding E (AlphaEarth, TESSERA, Presto, Galileo; OE13 and addendum 3's
  models when available), same parcels, folds and model as the protocol.
- **Test:** paired bootstrap over the protocol's bootstrap units; Holm over embeddings within each family.
- **Reading:** E **adds to the indices** for a family if ΔAI's Holm-adjusted 95% interval lies above zero and N + E
  itself passes the protocol's calibration and invariance checks. Otherwise "adds nothing shown". ΔAI is reported in
  I* units next to I*(N), so the size of the gain is plain.

## 4. Per-pixel change for ponds (W3-W)
A new pond is a sudden local change in a few pixels. A pooled post-entry embedding may miss it even at the 95th
percentile (it needs water in about 1 pixel in 20).
- **Feature:** for every pixel in the field polygon, the cosine distance between its embedding in year t and its mean
  embedding over the pre-entry years. The field's change features are the 95th percentile and the maximum of these
  distances, and the number of pixels above a threshold.
- **Threshold, fixed before extraction:** the 99th percentile of the 2019-versus-2017–2018 per-pixel distances in
  comparison-A fields of the same ITL1 region (all before any entry).
- **Use in I*:** post = change features for 2025; I₀ = the same for 2020; pre = the pooled pre-entry embedding, as in
  W3-W. Products: AlphaEarth, TESSERA (pre-entry 2018–2019, since 2017 is missing), OE13 once its gate opens.
- **Reading:** as W3-W; the key test (best AI against the best water count) is repeated with the change features.

## 5. LiDAR check on hedges (W3-1, descriptive)
New hedges are expected to be invisible at 10 m. Airborne LiDAR at 1 m can show woody structure.
- **Source:** the Environment Agency National LIDAR Programme: 1 m first-return surface and terrain models in 5 km
  Ordnance Survey tiles, Open Government Licence. Its index catalogue (updated 12 September 2025) was checked on
  30 October 2026: 6,574 tile surveys over 5,700 tiles, last flight dates 2016–2022 (2022: 532 tiles).
- **Feasibility, checked before any download:** of 33,592 new-hedge parcels (BN11, BN7, entry 2021–2024), 33,509 lie
  in a surveyed tile. Only 370 were surveyed more than a year after their agreement started, and whips that young are
  usually under 1 m. **The before-and-after design below therefore cannot be run on this programme**; it is kept only
  for a later national survey. Nothing is downloaded for it.
- A hedgerow map from UKCEH is used only if its licence allows.
- **Measure:** in the 20 m edge band of W3-1, the share of band length with surface-minus-terrain height above 1 m.
- **Design (descriptive):** for new-hedge fields (BN11, BN7) and their comparison fields, compare that share where the
  tile was surveyed after the planting year with where it was surveyed before. This gives an upper bound on what any
  satellite product could see, as the pond eye check does. No causal or detection reading.

## Expectations stated now, not used in the rules
- OE13 behaves like AlphaEarth: the same five land-management families.
- NDTI raises no-till I* modestly.
- ΔAI is near zero for herbal leys and no-till, and largest for cover crops.
- Change features beat pooled embeddings for ponds of 0.05 ha or more.
- LiDAR shows new hedges in a minority of fields surveyed after planting.

## Compute and data
- **OE13:** ranged reads of 64 int8 values per pixel for the sampled pixels, from the parcel points and polygons already
  in use. Small, no GPU.
- **NDTI:** two more bands from the Sentinel-2 extraction already planned (shared tiles).
- **ΔAI:** model refits only.
- **Change features:** from per-pixel embeddings already extracted for W3-W.
- **LiDAR:** tiles over new-hedge and comparison fields only, after approval.

Per-parcel data stay out of the public repository.

## Output
`wp3_elms_effect/results/w3_x_addendum5.md`, `.json` (aggregates only); coverage-check outputs in the record below.

## Decisions before registration (settled 30 October 2026: recommendations adopted)
1. **Registration:** register this draft as written, or change any part first. **Decided:** registered as written, with the LiDAR feasibility result below.
2. **E3b and OE13:** E3b's pre-entry window needs 2017–2019, which OE13 lacks for England today. Options:
   - (a) E3b unchanged (16 × 16 run with the bridge check);
   - (b) also add a matched sample on OE13 over the **full** E3 sample (no subsample, no GPU) once 2017–2019 are
     complete, as a secondary check, with a record entry in E3b before it is built.

   Recommended: (b), because it removes E3b's main limit, the 20,000-field subsample. **Decided:** (b); a matching
   record entry is made in E3b.
3. **OE13 waiting limit:** if 2017–2019 are still incomplete by 31 March 2027, either keep waiting or drop OE13 from the
   detection analyses (it would then be reported as not run). Recommended: keep waiting, with the monthly check.
   **Decided:** keep waiting; the check runs monthly as a scheduled task.
4. **LiDAR:** whether to verify the Environment Agency source now (metadata only), with any download still to be
   approved separately. **Decided:** verify, and download to the project Google Drive (about 10 GB approved).
   Verification showed the design cannot run (section 5), so no download was made; how LiDAR might still be used is
   left to the project lead.

## Record
| Date | Change | Reason |
|---|---|---|
| 2026-10-30 | Draft written, before any feature named here was extracted. OE13 coverage check (provenance tables only): England windows written 2017 0/826, 2018 0, 2019 458, 2020–2025 826 each | Project lead: adopt the five useful suggestions from a review of EO products |
| 2026-10-30 | Decisions settled (above). LiDAR feasibility checked from the index catalogue before any download: 370 of 33,592 new-hedge parcels surveyed more than a year after entry, so section 5 is not run and nothing is downloaded. Registered by public commit | Project lead's decisions |
