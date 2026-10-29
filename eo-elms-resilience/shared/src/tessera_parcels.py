"""National TESSERA v1.1 extraction at the WP3 detection parcels (W3-4 addendum, 18 October 2026): years 2018,
2019, 2020, 2025 (2017 is missing in the store). One file per 50 km square and year, so a stopped run resumes.
Needs .venv-tessera (Python >= 3.12, geotessera >= 0.11).

Input   shared/data/parcels/wp3_detection_parcels.csv (parcref, lon, lat, sq)
Output  shared/data/embeddings/tessera_parcels/t_<square>_<year>.parquet (parcref, T000..T127 as float16)
Usage   python tessera_parcels.py [years...]
"""
import os, sys, time
import numpy as np, pandas as pd
from geotessera import GeoTesseraZarr

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
OUT = os.path.join(ROOT, 'shared', 'data', 'embeddings', 'tessera_parcels')
YEARS = [int(y) for y in sys.argv[1:]] or [2025, 2019, 2018, 2020]


def main():
    os.makedirs(OUT, exist_ok=True)
    p = pd.read_csv(os.path.join(ROOT, 'shared', 'data', 'parcels', 'wp3_detection_parcels.csv'))
    gt = GeoTesseraZarr()
    jobs = [(y, sq) for y in YEARS for sq in sorted(p.sq.unique())]
    t0 = time.time()
    for n, (y, sq) in enumerate(jobs, 1):
        dst = os.path.join(OUT, f't_{sq}_{y}.parquet')
        if os.path.exists(dst):
            continue
        s = p[p.sq == sq]
        for k in range(5):
            try:
                v = gt.sample_points(list(zip(s.lon, s.lat)), y); break
            except Exception as e:
                print(f'  {sq} {y}: retry {k + 1} ({str(e)[:80]})', flush=True); time.sleep(60 * (k + 1))
        else:
            print(f'  {sq} {y}: failed', flush=True); continue
        out = pd.DataFrame(v.astype(np.float16), columns=[f'T{i:03d}' for i in range(v.shape[1])]).assign(parcref=s.parcref.values)
        out.to_parquet(dst + '.tmp', index=False); os.replace(dst + '.tmp', dst)
        print(f'  {n}/{len(jobs)} {sq} {y}: {len(s):,} parcels, missing {np.isnan(v).any(axis=1).mean():.3f} '
              f'({(time.time() - t0) / 60:.0f} min)', flush=True)


if __name__ == '__main__':
    main()
