"""Galileo pilot for W3-4 addendum 3 (draft protocol wp3_elms_effect/results/w3_4_esa_models_protocol.md, open decision 4):
does the released Galileo base encoder (MIT, code and weights) run on single-pixel monthly inputs (H = W = 1,
patch size 1) built from the existing Presto input files, and are the embeddings well formed? One 50 km square, two
seasons; no labels or outcomes are read.

Inputs per parcel and farm-season month (October..September): Sentinel-1 VV/VH (dB), Sentinel-2 B2..B12 incl. B8A
(DN), NDVI, ERA5-Land 2 m temperature (K) and precipitation (m), SRTM elevation and slope, parcel lat/lon; missing
months masked per band group. Normalised with Galileo's pre-training statistics. Embedding = mean of unmasked tokens.

Output  shared/results/galileo_pilot.md (written by hand from the printed checks)
Usage   .venv-presto/bin/python galileo_pilot.py [--square 10_2 --seasons 2018 2025]
"""
import argparse, os, sys, time
import numpy as np, pandas as pd, torch

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
G = os.path.join(ROOT, 'third_party', 'galileo')
sys.path.insert(0, G)
from unittest.mock import MagicMock
for _ in range(40):          # Galileo's data package imports its training-data stack; stub what is missing (not used here)
    try:
        from src.data.utils import construct_galileo_input   # noqa: E402
        break
    except ModuleNotFoundError as _e:
        _stub = __import__('types').ModuleType(_e.name); _stub.__spec__ = __import__('importlib.machinery').machinery.ModuleSpec(_e.name, None)
        _stub.__getattr__ = lambda attr: MagicMock(); sys.modules[_e.name] = _stub
        for _k in [k for k in sys.modules if k.startswith('src')]:
            del sys.modules[_k]


import single_file_galileo as sg  # noqa: E402
from src.data.dataset import Normalizer  # noqa: E402
from src.data.utils import PRETRAINING_NORMALIZING_DICT  # noqa: E402
NORM = Normalizer(normalizing_dicts=PRETRAINING_NORMALIZING_DICT, std=True)

S2 = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B11', 'B12']
NDVI = sg.SPACE_TIME_BANDS.index('NDVI'); NDVI_G = list(sg.SPACE_TIME_BANDS_GROUPS_IDX).index('NDVI')
NDVI_MU, NDVI_SD = 0.2892116502999044, 0.2720939024500081          # Galileo pre-training statistics
MONTHS = [(9 + k) % 12 for k in range(12)]                          # Oct..Sep as 0-indexed calendar months


def inputs(d, ll):
    g = lambda b: np.stack([d[f'{b}_m{m:02d}'].values for m in range(1, 13)], 1).astype(np.float32)   # [N, 12]
    s1 = np.stack([g('VV'), g('VH')], -1); s2 = np.stack([g(b) for b in S2], -1)
    era = np.stack([g('temperature_2m'), g('total_precipitation')], -1)
    srtm = d[['elevation', 'slope']].values.astype(np.float32)
    nd = (s2[..., 6] - s2[..., 2]) / (s2[..., 6] + s2[..., 2])
    out = []
    for i in range(len(d)):
        a, b, e = s1[i], s2[i], era[i]
        mo = construct_galileo_input(s1=torch.tensor(np.nan_to_num(a))[None, None], s2=torch.tensor(np.nan_to_num(b))[None, None],
                                     srtm=torch.tensor(srtm[i])[None, None],
                                     latlon=torch.tensor(ll[i]), months=torch.tensor(MONTHS), normalize=True)
        stx, stm = mo.space_time_x.clone(), mo.space_time_mask.clone()
        stx[0, 0, :, NDVI] = torch.tensor(np.nan_to_num((nd[i] - NDVI_MU) / NDVI_SD)); stm[0, 0, :, NDVI_G] = 0
        for grp, bad in (('S1', np.isnan(a).any(1)), ('S2', np.isnan(b).any(1))):     # mask missing months per group
            for gi, key in enumerate(sg.SPACE_TIME_BANDS_GROUPS_IDX):
                if grp in key or (grp == 'S2' and key == 'NDVI'):
                    stm[0, 0, torch.tensor(bad), gi] = 1
        # ERA5 filled here (the helper's timestep check rejects [T, D] time inputs), normalised with Galileo's own normaliser
        tx = np.zeros((12, len(sg.TIME_BANDS)), np.float32); tx[:, :2] = np.nan_to_num(e)
        tx = torch.from_numpy(NORM(tx)).float(); tm = mo.time_mask.clone()
        era_g = [gi for gi, key in enumerate(sg.TIME_BAND_GROUPS_IDX) if 'ERA5' in key]
        tm[:, era_g] = 0; tm[torch.tensor(np.isnan(e).any(1))][:, era_g] = 1
        tm[torch.tensor(np.isnan(e).any(1)).nonzero().flatten()[:, None], torch.tensor(era_g)] = 1
        out.append((stx, mo.space_x, tx, mo.static_x, stm, mo.space_mask, tm, mo.static_mask, mo.months))
    return [torch.stack([o[k] for o in out]).float() for k in range(8)] + [torch.stack([o[8] for o in out]).long()]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--square', default='10_2'); ap.add_argument('--seasons', nargs='*', type=int, default=[2018, 2025])
    a = ap.parse_args()
    enc = sg.Encoder.load_from_folder(__import__('pathlib').Path(G, 'data', 'models', 'base'), torch.device('cpu')).eval()
    ll_all = pd.read_parquet(os.path.join(ROOT, 'shared', 'data', 'parcels', 'wp3_detection_parcels.parquet')).set_index('parcref')[['lat', 'lon']]
    E = {}
    for s in a.seasons:
        d = pd.read_parquet(os.path.join(ROOT, 'shared', 'data', 'presto', 'inputs', f'i_{a.square}_{s}.parquet'))
        x = inputs(d, ll_all.reindex(d.parcref).values.astype(np.float32))
        t0 = time.time(); embs = []
        with torch.no_grad():
            for i in range(0, len(d), 256):
                b = [t[i:i + 256] for t in x]
                o = enc(*b[:8], b[8], patch_size=1)
                embs.append(sg.Encoder.average_tokens(*o[:8]))
        e = torch.cat(embs).numpy(); E[s] = pd.DataFrame(e, index=d.parcref.values)
        print(f'season {s}: {len(d)} parcels, embedding dim {e.shape[1]}, non-finite {np.mean(~np.isfinite(e)):.4f}, '
              f'masked S2 months {np.mean(x[4][..., 1].numpy()):.3f}, per-dimension SD median {np.median(e.std(0)):.3f}, '
              f'{(time.time() - t0) / len(d) * 1000:.1f} ms/parcel', flush=True)
    if len(E) == 2:
        s0, s1 = a.seasons
        A, B = E[s0].align(E[s1], join='inner', axis=0)
        cos = lambda u, v: (u * v).sum(1) / np.linalg.norm(u, axis=1) / np.linalg.norm(v, axis=1)
        same = cos(A.values, B.values); rnd = cos(A.values, B.values[np.random.default_rng(0).permutation(len(B))])
        print(f'cosine {s0} vs {s1}: same field median {np.median(same):.3f}; random pairs median {np.median(rnd):.3f}')


if __name__ == '__main__':
    main()
