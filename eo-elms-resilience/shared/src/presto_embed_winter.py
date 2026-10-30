"""Presto embeddings from the winter months alone (W3-4 seasonal cover-crop test,
wp3_elms_effect/results/w3_4_cover_seasonal_protocol.md, written before any winter embedding was computed).

Same pretrained encoder, normalisation, masking and batching as presto_embed.py, but only the three winter steps of
each farm season: December, January, February (input months m03..m05; start month December = 11).

Input   shared/data/presto/inputs/i_<square>_<season>.parquet; shared/data/parcels/wp3_detection_parcels.parquet
Output  shared/data/embeddings/presto_winter/w_<square>_<season>.parquet (parcref, W000..W127 float16)
Usage   python presto_embed_winter.py [--seasons 2018 2019 2020 2025 2026]
"""
import argparse, glob, os, re
import numpy as np, pandas as pd, torch
import presto_embed as pe
from presto_embed import Presto, prt, ROOT, GROUPS

OUT = os.path.join(ROOT, 'shared', 'data', 'embeddings', 'presto_winter')
MONTHS = [3, 4, 5]          # December, January, February
START = 11                  # December, 0-indexed calendar month


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--seasons', nargs='*', type=int, default=[2018, 2019, 2020, 2025, 2026])
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    ll_all = pd.read_parquet(os.path.join(ROOT, 'shared', 'data', 'parcels', 'wp3_detection_parcels.parquet')).set_index('parcref')[['lat', 'lon']]
    model = Presto.construct()
    model.load_state_dict(torch.load(os.path.join(ROOT, 'third_party', 'presto', 'data', 'default_model.pt'), map_location='cpu'))
    enc = model.encoder.eval()
    for f in sorted(glob.glob(os.path.join(ROOT, 'shared', 'data', 'presto', 'inputs', 'i_*.parquet'))):
        sq, season = re.search(r'i_(\d+_\d+)_(\d{4})\.parquet$', f).groups()
        dst = os.path.join(OUT, f'w_{sq}_{season}.parquet')
        if int(season) not in a.seasons or os.path.exists(dst):
            continue
        d = pd.read_parquet(f)
        x, mask = prt.tensor(d, MONTHS)
        ll = torch.tensor(ll_all.reindex(d.parcref).values, dtype=torch.float32)
        dw = torch.full((len(d), len(MONTHS)), 9, dtype=torch.long)
        cnt = sum(mask[:, :, b0:b1].amax(dim=2).sum(dim=1) for b0, b1 in GROUPS) + mask[:, 0, 14:16].amax(dim=1)
        e = np.full((len(d), 128), np.nan, np.float32)
        with torch.no_grad():
            for c in torch.unique(cnt):
                ix = torch.where(cnt == c)[0]
                for i in range(0, len(ix), 2048):
                    j = ix[i:i + 2048]
                    e[j.numpy()] = enc(x[j], dynamic_world=dw[j], latlons=ll[j], mask=mask[j], month=START, eval_task=True).numpy()
        pd.DataFrame(e.astype(np.float16), columns=[f'W{i:03d}' for i in range(128)]).assign(parcref=d.parcref.values).to_parquet(dst, index=False)
        print(sq, season, len(d), 'masked share', round(float(mask.mean()), 3), flush=True)


if __name__ == '__main__':
    main()
