"""Presto embeddings for the national WP3 inputs (W3-4 addendum): pretrained Presto encoder, 12 monthly steps of a
farm season (October..September, so the start month passed to Presto is October = 9), normalised and masked as in
presto_run_test.py, fields batched by masked-token count. Needs .venv-presto (torch 2.2.2).

Input   shared/data/presto/inputs/i_<square>_<season>.parquet; shared/data/parcels/wp3_detection_parcels.parquet
Output  shared/data/embeddings/presto_parcels/p_<square>_<season>.parquet (parcref, P000..P127 float16)
"""
import glob, os, re, sys
import numpy as np, pandas as pd, torch

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'third_party', 'presto')); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from single_file_presto import Presto  # noqa: E402
import presto_run_test as prt  # noqa: E402

OUT = os.path.join(ROOT, 'shared', 'data', 'embeddings', 'presto_parcels')
GROUPS = [(0, 2), (2, 5), (5, 8), (8, 9), (9, 10), (10, 12), (12, 14), (16, 17)]


def main():
    os.makedirs(OUT, exist_ok=True)
    ll_all = pd.read_parquet(os.path.join(ROOT, 'shared', 'data', 'parcels', 'wp3_detection_parcels.parquet')).set_index('parcref')[['lat', 'lon']]
    model = Presto.construct()
    model.load_state_dict(torch.load(os.path.join(ROOT, 'third_party', 'presto', 'data', 'default_model.pt'), map_location='cpu'))
    enc = model.encoder.eval()
    for f in sorted(glob.glob(os.path.join(ROOT, 'shared', 'data', 'presto', 'inputs', 'i_*.parquet'))):
        sq, season = re.search(r'i_(\d+_\d+)_(\d{4})\.parquet$', f).groups()
        dst = os.path.join(OUT, f'p_{sq}_{season}.parquet')
        if os.path.exists(dst):
            continue
        d = pd.read_parquet(f)
        x, mask = prt.tensor(d, list(range(1, 13)))
        ll = torch.tensor(ll_all.reindex(d.parcref).values, dtype=torch.float32)
        dw = torch.full((len(d), 12), 9, dtype=torch.long)
        cnt = sum(mask[:, :, a:b].amax(dim=2).sum(dim=1) for a, b in GROUPS) + mask[:, 0, 14:16].amax(dim=1)
        e = np.full((len(d), 128), np.nan, np.float32)
        with torch.no_grad():
            for c in torch.unique(cnt):
                ix = torch.where(cnt == c)[0]
                for i in range(0, len(ix), 2048):
                    j = ix[i:i + 2048]
                    e[j.numpy()] = enc(x[j], dynamic_world=dw[j], latlons=ll[j], mask=mask[j], month=9, eval_task=True).numpy()
        pd.DataFrame(e.astype(np.float16), columns=[f'P{i:03d}' for i in range(128)]).assign(parcref=d.parcref.values).to_parquet(dst, index=False)
        print(sq, season, len(d), 'masked share', round(float(mask.mean()), 3), flush=True)


if __name__ == '__main__':
    main()
