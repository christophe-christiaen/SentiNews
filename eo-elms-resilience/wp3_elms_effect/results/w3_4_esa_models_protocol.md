# W3-4 addendum 3: further geospatial foundation models in the detection comparison

**Status: registered 30 October 2026 by public commit, before any chip or tile was extracted for the comparison (only
the pilots below, which read no labels, were run).** Builds on [w3_4_metric_protocol.md](w3_4_metric_protocol.md) (metric, checks, reading rules) and
[w3_4_model_comparison_protocol.md](w3_4_model_comparison_protocol.md) (paired bootstrap, Holm). Changes after
registration go in the record at the end.

## Why
The project is funded by ESA. The model comparison so far (AlphaEarth, TESSERA, Presto against plain Sentinel-2 indices)
found the selection trap model-agnostic and AI adding at most 0.02–0.03 beyond selection. This addendum asks whether
the same holds for ESA's own foundation model and for the encoder family behind ESA Φ-lab's Major TOM embeddings.

## What was checked before drafting (30 October 2026)
- **Major TOM precomputed embeddings cannot be used.** They are computed on Major TOM Core, which the dataset card
  calls "a global monotemporal dataset": its metadata hold one product per grid cell (columns grid_cell, timestamp,
  centre_lat, centre_lon, …), with dates from 2016 to 2023. The design needs the same field in 2018–2019, 2020 and 2025,
  so no field has the required years, and there is nothing after 2023.
- **TerraMind-1.0** (IBM, ESA Φ-lab, Forschungszentrum Jülich), licence Apache-2.0 (model card); inputs include
  S2L2A (12 bands) and S1GRD (2 bands); examples use 224 × 224 pixel tiles; the backbone returns 16 × 16-pixel patch
  embeddings (196 × 768 for base).
- **Galileo** (Tseng et al., 2025): repository licence MIT for the code; the weights' licence is not stated on the
  repository page and must be confirmed before registration. Inputs are space-time, space, time and static arrays
  (`space_time_x: [B, H, W, T, bands]`), so it can take pixel time series like Presto; whether H = W = 1 is supported
  must be confirmed in a pilot before registration.
- **OlmoEarth-v1-Base** (Ai2): ViT-Base, 89M parameters, for Sentinel-1, Sentinel-2 and Landsat images or image time
  series; embeddings computed with Ai2's rslearn, which reads public Sentinel-1/2 and Landsat archives (AWS, Microsoft
  Planetary Computer) without credentials. Licence: **OlmoEarth Artifact License**, free use, modification and
  distribution with use restrictions (no military or defence uses; no extractive industries) that must be passed on with
  any distributed derivative. Research on farm schemes is permitted; released embeddings (e.g. in a benchmark) would
  carry those restrictions. Ranked first among 13 models in Ai2's own fine-tuning benchmark (18 tasks); that ranking
  is for fine-tuning, not frozen embeddings, and is the developer's comparison.
- **Secondary models, licences checked:** Prithvi-EO-2.0-300M-TL (NASA, IBM; Apache-2.0; Harmonized Landsat
  Sentinel-2, 30 m), Copernicus-FM ViT-Base (weights CC-BY-4.0; code Apache-2.0), Clay v1.5 (Apache-2.0).
- **SSL4EO-S12** (the self-supervised encoder family used for Major TOM's Sentinel-2 embedding expansion): code
  Apache-2.0, dataset and weights CC-BY-4.0 (repository); Sentinel-2 checkpoints take **L1C** (13 bands); ViT-S/16
  checkpoints exist for MoCo-v3, DINO, MAE and data2vec.

- **DINOv3, satellite version** (Siméoni et al., 2025, arXiv:2508.10104; checked 30 October 2026 on the Hugging Face
  model card `facebook/dinov3-vitl16-pretrain-sat493m` and the GitHub repository): ViT-L/16, about 300M parameters,
  1,024-d embeddings, 16-pixel patches, distilled from a 7B satellite model; trained on SAT-493M, 493 million 512 × 512
  Maxar **RGB** images at **0.6 m**. Satellite normalisation mean (0.430, 0.411, 0.296), std (0.213, 0.156, 0.143).
  Licence: the **DINOv3 License** (Meta), a custom use-restricted agreement covering code and weights: royalty-free use,
  reproduction, modification and distribution, a copy of the agreement with any redistributed materials, acknowledgement
  in publications, no uses under ITAR or prohibited by trade controls (military, nuclear, espionage), California law.
  Weights are **gated**: the project lead must request access and accept the agreement (not done by the assistant).
  Fit for this study: colour only and trained at 0.6 m, about 17 times finer than Sentinel-2's 10 m, so on our chips a
  16-pixel patch covers 160 m instead of about 10 m; a scale mismatch to be stated with any result.

## Models (four new primary feature families, four secondary)
- **TM: TerraMind-1.0-base**, inputs S2L2A (12 bands) + S1GRD (VV, VH), modality embeddings averaged (the default
  `merge_method='mean'`).
- **SS: SSL4EO-S12 ViT-S/16, DINO checkpoint**, input Sentinel-2 L2A (12 bands, B10 filled; see Open decision 6).
- **GA: Galileo** (base model), run on the **same monthly point inputs as Presto** (Sentinel-1 VV/VH, Sentinel-2 bands,
  weather and terrain, farm seasons October–September), so no image chips are needed; pooled over all tokens as in its
  released embedding code. Single-pixel input (patch size 1) confirmed in the Galileo pilot (Open decision 5).
- **OE: OlmoEarth-v1-Base**, monthly Sentinel-1, Sentinel-2 and Landsat mosaics over the farm season (October–September),
  as in Ai2's embedding tutorial, materialised with rslearn. **Window (Open decision 4): 64 × 64 pixels at 10 m, centred
  on the parcel point, patch size 8**; the field embedding is the mean of the 2 × 2 patch tokens at the window centre
  (a 160 m × 160 m neighbourhood, half the 320 m used for TM and SS, because a 64-pixel window with 4-pixel patches does
  not fit in the memory of the pilot GPU). The difference in neighbourhood is stated with every OE result.
- **Secondary (reported, not tested):** Prithvi-EO-2.0 (6 HLS bands, 30 m, three dates per year), Copernicus-FM
  (Sentinel-2 L2A with its spectral metadata), Clay v1.5 (Sentinel-2) and DINOv3 satellite ViT-L/16 (Sentinel-2 true
  colour, scaled as for SAT-493M; trained at 0.6 m, so the scale mismatch is reported with its result), each with the same composites, chip, field
  embedding and metric; their I* and checks are reported beside the primary models, outside the Holm family.
- **Field embedding (TM, SS):** the chip is centred on the RPA parcel point; the field embedding is the mean of the 2 × 2
  patch tokens at the chip centre (a 320 m × 320 m neighbourhood), the image-model analogue of the point sampling used
  for every other family. No fine-tuning.

## Imagery (fixed before extraction)
- **Season composite per year:** median of clear observations 15 April–31 July (Sentinel-2: clouds, shadows and cirrus removed
  with the L2A scene classification layer, classes 3, 8, 9 and 10; Cloud Score+ is an Earth Engine product and is not used;
  L2A for every model; Sentinel-1 IW GRD VV/VH, dB, all orbits). Years 2018, 2019 (pre), 2020 (I₀), 2025 (post).
- **Chip size:** 224 × 224 pixels at 10 m (the size the models were trained on).
- **Source:** public archives as shared tiles in the project lead's Drive (Open decision 1).

## Sample (image chips are costly, so a fixed subsample)
- From each family's W3-4 comparison sample (same seeds), draw at most **3,000 positives** (seed 30) and their
  region-matched comparison parcels, for comparison B and, for the two negative controls, comparison A. Expected size:
  about 40,000 unique parcels × 4 years.
- **All feature families are re-scored on this same subsample** (AlphaEarth, TESSERA, Presto, Sentinel-2 indices, TM,
  SS, GA, OE and the secondary models), so every comparison is on identical parcels and years. GA, which needs no chips, is also run on the full
  W3-4 sample and reported there beside the earlier four.

## Metric, checks and tests (unchanged rules)
- I* as in W3-4 (pre = mean of 2018–2019; I₀ = 2020; post = 2025); calibration (both negative controls within ±0.02
  against never-treated land); selection invariance (|I*(A) − I*(B)| < 0.03); detectability (95% interval above 0.02).
- **Tests (primary models only):** for each of the six option families, each new primary model (TM, SS, GA, OE) against
  each of the four existing families and the new models against each other (22 pairs × 6 = 132 tests), paired bootstrap
  of I* differences (1,000 resamples within held-out regions), Holm over the 132.

## Reading, fixed in advance
- **Same trap:** TM, SS, GA or OE falls into the selection trap if, against never-treated land, both negative controls reach
  AUC ≥ 0.60 (they cannot be seen, so any such score is selection). Calibration of I* is reported separately with the
  existing ±0.02 rule.
- **Same answer:** each new model gives the same answer if its detectable families equal the five found so far.
- **Better than the no-AI baseline:** each new model beats the plain indices for a family if the difference is positive with
  Holm-adjusted p < 0.05, and the lead is not established if the model fails calibration.
- **Expectation stated now, not used in the rules:** neither ESA-linked model changes the conclusion; TerraMind, which
  sees radar and optical together, may do best on no-till.

## Decisions before registration (all settled)
1. **Imagery source: decided (30 October 2026), public archives as shared tiles in the project lead's Drive.**
   Sentinel-2 L2A and L1C (for SS), Sentinel-1 GRD and Harmonized Landsat Sentinel-2 (for Prithvi) are read from public
   archives without credentials (Microsoft Planetary Computer, or the AWS open-data buckets where Planetary Computer
   lacks a product). For each 50 km square and year, the season composite (Imagery, above) is computed once per sensor
   as a tile, stored in a dedicated folder in the project lead's Google Drive (`EO-ELMs_foundation_models/tiles/`), and
   every model's chips are cut from those tiles, so all models see identical pixels. Only embeddings are kept on the
   project machine. Earth Engine is not used for this addendum: the project went over its noncommercial quota on
   30 October 2026. Per-field downloads are not used: the OlmoEarth pilot showed them too slow (over two hours for 200
   fields and two seasons). Monthly mosaics for OlmoEarth are built from the same archives into the same folder.
2. **Sample size: decided (30 October 2026), 3,000 positives per family.** 3,000 positives per family keeps the extraction near 40,000 parcels × 4 years of 224 × 224 chips
   (about 110 GB of raw imagery, processed in streams, embeddings only kept); a smaller sample widens the intervals.
3. **Checkpoint for SS: decided (30 October 2026), the DINO ViT-S/16 checkpoint.**
4. **OlmoEarth window: decided (30 October 2026), 64 × 64 pixels with patch size 8** (OE, above). In the pilot both
   64 × 64 (patch 8) and 16 × 16 (patch 4) windows embedded all 200 parcels in both seasons; the larger window
   separated fields more (random-pair cosine 0.914 against 0.938, same-field 0.973 for both) at about 7 times the
   embedding time. Monthly mosaics as in the pilot (Ai2's tutorial settings). **Compute
   environment (pilot, 30 October):** OlmoEarth needs PyTorch ≥ 2.9 (it imports `torch.distributed.fsdp.fully_shard` and
   `torch.distributed.tensor`); the project machine is an Intel Mac, for which PyTorch stops at 2.2.2, so OlmoEarth (and
   probably TerraMind through TerraTorch) must run on Linux (e.g. Google Colab with the project Drive, or a cloud VM).
6. **Sentinel-2 input for SS: decided (30 October 2026), L2A with the gap stated.** SSL4EO-S12 checkpoints were trained
   on L1C (13 bands, top of atmosphere), which is not available from the public archives without credentials. SS is run
   on the same L2A tiles as the other models, using the 12 L2A bands and filling the missing cirrus band B10 with its
   SSL4EO-S12 training mean, with the checkpoint's own normalisation. The input mismatch (surface reflectance instead of
   top of atmosphere; B10 filled) is stated with every SS result, and a weak SS result is not read as evidence against
   the model.
5. **Galileo: decided by its pilot (30 October 2026), single-pixel input.** Weight licence (now confirmed: MIT on the model card) and single-pixel support, confirmed in a pilot on one 50 km square before registration
   (no outcome is looked at in the pilot).

## Output
`wp3_elms_effect/results/w3_4_esa_models.md`, `.json` (aggregates only).

## Record
| Date | Change | Reason |
|---|---|---|
| 2026-10-30 | Draft written; Major TOM precomputed embeddings excluded (one image per grid cell, 2016–2023) | Project lead's request to include ESA models |
| 2026-10-30 | Galileo added to the draft | Project lead's request |
| 2026-10-30 | OlmoEarth-v1-Base added as primary; Prithvi-EO-2.0, Copernicus-FM and Clay v1.5 as secondary (reported, not tested); licences checked on the model cards | Project lead's request after Ai2's benchmark chart |
| 2026-10-30 | OlmoEarth pilot stopped before any weights or imagery were downloaded: the encoder cannot be built on the project machine's PyTorch 2.2.2 | Compute environment |
| 2026-10-30 | Galileo pilot (square 10_2, seasons 2018 and 2025, 2,806 parcels, no labels read; `shared/src/galileo_pilot.py`): base encoder runs on single-pixel monthly inputs (patch size 1), 768-d embeddings, no non-finite values, 136 ms per parcel on the project CPU; same-field cosine across seasons median 0.989 against 0.983 for random pairs (mean-pooled tokens are highly similar, as usual; classifiers standardise features). Single-pixel input adopted for GA | Pilot |
| 2026-10-30 | OlmoEarth pilot prepared as a Colab notebook in the project lead's Drive (`EO-ELMs_foundation_models/olmoearth_pilot.ipynb`, 200 parcel points from square 10_2, seasons 2018 and 2025, Sentinel-1/2 from Planetary Computer, 64 × 64 and 16 × 16 pixel windows) | Compute environment |
| 2026-10-30 | Project lead's decision: models trained only on web photos (e.g. DINOv2, CLIP, SigLIP) are excluded; DINOv3's satellite-trained version is to be added as a satellite image model (colour only). Its checkpoint, input bands and licence are to be verified on the model card before registration, and its role (primary or secondary) decided then | Project lead's decision on the model families |
| 2026-10-30 | DINOv3 satellite model card and licence checked (above). Proposed: secondary (reported, not tested), because it sees colour only and was trained at 0.6 m; access to be requested by the project lead | Check before registration |
| 2026-10-30 | DINOv3 satellite version added as secondary (reported, not tested) | Project lead's decision |
| 2026-10-30 | Open decisions 2 and 3 settled: 3,000 positives per family; SSL4EO-S12 DINO ViT-S/16 checkpoint | Project lead's decisions |
| 2026-10-30 | Open decision 1 settled: public archives as shared tiles in the project lead's Drive; Earth Engine not used (quota) | Project lead's decision |
| 2026-10-30 | Consequences of decision 1: the L2A cloud mask changes from Cloud Score+ (Earth Engine only) to the scene classification layer; a new open decision 6 on the L1C source for SSL4EO-S12 | Follows from the imagery source |
| 2026-10-30 | Open decision 6 settled: SS runs on L2A (B10 filled with its training mean), the gap stated with every SS result | Project lead's decision |
| 2026-10-30 | OlmoEarth pilot run on Colab (T4 GPU, PyTorch 2.9.1; no labels read). Windows 15 min; imagery search 5.5 min; monthly Sentinel-1/2 mosaics from Planetary Computer for 800 windows took 2 h 43 min (12 s per window, 1.1 GB). 16 × 16 pixel windows, patch 4: 200 of 200 parcels in both seasons, 768-d, no non-finite values, 129 s for 400 windows; same-field cosine across seasons median 0.973 against 0.938 for random pairs. 64 × 64 windows, patch 4: out of GPU memory at batch 8 (54 GiB requested) and at batch 1 (6.75 GiB); rerun with patch 8 under way. Per-window downloads are too slow for the full run, which supports shared tiles (decision 1) | Pilot |
| 2026-10-30 | OlmoEarth pilot, 64 × 64 windows rerun with patch 8 and batch 1 (cell added to the notebook): 200 of 200 parcels in both seasons, 768-d, no non-finite values, 889 s for 400 windows (about 7 times the 16 × 16 run); same-field cosine across seasons median 0.973 against 0.914 for random pairs (16 × 16, patch 4: 0.973 against 0.938). Both window sizes work on a T4; open decision 4 (window) goes to the project lead | Pilot |
| 2026-10-30 | Open decision 4 settled: OlmoEarth 64 × 64 windows, patch size 8, field embedding = mean of the 2 × 2 centre patch tokens (160 m); all decisions settled; addendum registered by public commit | Project lead's decision |
