"""Test of Presto inference on parcel points (W1-6 / W3-2): pretrained Presto (MIT; third_party/presto, weights
data/default_model.pt) applied to 12 monthly steps of S1, S2, ERA5-Land and SRTM inputs, normalised as in Presto's
pipeline; missing months masked; Dynamic World unknown (class 9). Encoder output (eval_task=True) = 128-d embedding.
Also an in-season version: months January-July only (mid-July cutoff for WP1).

Needs .venv-presto (torch 2.2.2). Input data/raw/presto_test/inputs_<year>.csv, data/raw/tessera_test/points.csv
Output data/raw/presto_test/presto_<year>_{full,jan_jul}.parquet; timing printed
"""
import os, sys, time
import numpy as np, pandas as pd, torch

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'third_party', 'presto'))
from single_file_presto import Presto  # noqa: E402

S2B = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B11', 'B12']
ORDER = ['VV', 'VH'] + S2B + ['temperature_2m', 'total_precipitation', 'elevation', 'slope', 'NDVI']
ADD = {'VV': 25.0, 'VH': 25.0, 'temperature_2m': -272.15}
DIV = {'VV': 25.0, 'VH': 25.0, 'temperature_2m': 35.0, 'total_precipitation': 0.03, 'elevation': 2000.0, 'slope': 50.0, 'NDVI': 1.0}


def tensor(d, months):
    n, T = len(d), len(months)
    x = np.zeros((n, T, len(ORDER)), np.float32); mask = np.zeros_like(x)
    for t, m in enumerate(months):
        for j, b in enumerate(ORDER):
            if b in ('elevation', 'slope'):
                v = d[b].values
            elif b == 'NDVI':
                b8, b4 = d[f'B8_m{m:02d}'].values, d[f'B4_m{m:02d}'].values
                v = np.where((b8 + b4) > 0, (b8 - b4) / (b8 + b4), np.nan)
            else:
                v = d[f'{b}_m{m:02d}'].values.astype(float)
            v = (v + ADD.get(b, 0.0)) / DIV.get(b, 1e4)
            bad = ~np.isfinite(v)
            x[:, t, j] = np.where(bad, 0, v); mask[:, t, j] = bad
    return torch.tensor(x), torch.tensor(mask)


def main(year=2022):
    d = pd.read_csv(os.path.join(ROOT, 'data', 'raw', 'presto_test', f'inputs_{year}.csv'))
    pts = pd.read_csv(os.path.join(ROOT, 'data', 'raw', 'tessera_test', 'points.csv')).set_index('parcref').reindex(d.parcref)
    model = Presto.construct()
    model.load_state_dict(torch.load(os.path.join(ROOT, 'third_party', 'presto', 'data', 'default_model.pt'), map_location='cpu'))
    enc = model.encoder.eval()
    ll = torch.tensor(pts[['lat', 'lon']].values, dtype=torch.float32)
    for lab, months in (('full', list(range(1, 13))), ('jan_jul', list(range(1, 8)))):
        x, mask = tensor(d, months)
        dw = torch.full((len(d), len(months)), 9, dtype=torch.long)
        # Presto needs the same number of masked tokens within a batch: a token (band group x month; SRTM once) is
        # masked if any of its bands is missing, so batch fields by their masked-token count
        groups = [(0, 2), (2, 5), (5, 8), (8, 9), (9, 10), (10, 12), (12, 14), (16, 17)]
        cnt = sum(mask[:, :, a:b].amax(dim=2).sum(dim=1) for a, b in groups) + mask[:, 0, 14:16].amax(dim=1)
        t0, e = time.time(), np.full((len(d), 128), np.nan, np.float32)
        with torch.no_grad():
            for c in torch.unique(cnt):
                ix = torch.where(cnt == c)[0]
                for i in range(0, len(ix), 2048):
                    j = ix[i:i + 2048]
                    e[j.numpy()] = enc(x[j], dynamic_world=dw[j], latlons=ll[j], mask=mask[j], month=0, eval_task=True).numpy()
        pd.DataFrame(e, columns=[f'P{i:03d}' for i in range(e.shape[1])]).assign(parcref=d.parcref.values).to_parquet(
            os.path.join(ROOT, 'data', 'raw', 'presto_test', f'presto_{year}_{lab}.parquet'), index=False)
        print(f'{lab}: {len(d):,} parcels -> {e.shape[1]}-d in {time.time() - t0:.1f} s; masked share {float(mask.mean()):.2f}; '
              f'embedding finite {np.isfinite(e).all()}', flush=True)


if __name__ == '__main__':
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 2022)
