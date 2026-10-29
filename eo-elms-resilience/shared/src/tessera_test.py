"""Test of the TESSERA national extraction (W3-T), run before any national run: one 50 km square of cereal parcels,
years 2017-2020 and 2025. Measures year coverage, the share of points without a value, time, and bytes fetched
(size of a fresh cache folder). Needs the Python >= 3.12 environment (.venv-tessera) with geotessera.

Input   data/raw/tessera_test/points.csv (parcref, lon, lat)
Output  data/raw/tessera_test/tessera_<year>.parquet; data/raw/tessera_test/report.json
"""
import json, os, sys, time
import numpy as np, pandas as pd
from geotessera import GeoTesseraZarr

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'raw', 'tessera_test')
CACHE = os.path.join(D, 'cache')
YEARS = [int(y) for y in sys.argv[1:]] or [2017, 2018, 2019, 2020, 2025]


def du(p):
    return sum(os.path.getsize(os.path.join(a, f)) for a, _, fs in os.walk(p) for f in fs) if os.path.exists(p) else 0


def main():
    pts = pd.read_csv(os.path.join(D, 'points.csv'))
    gt = GeoTesseraZarr(cache_dir=CACHE)
    rep = {'points': len(pts), 'store': 'v1.1-dclimate (default)', 'years': {}}
    for y in YEARS:
        b0, t0 = du(CACHE), time.time()
        try:
            v = gt.sample_points(list(zip(pts.lon, pts.lat)), y)
        except Exception as e:
            rep['years'][y] = {'error': f'{type(e).__name__}: {str(e)[:200]}'}
            print(y, 'error', rep['years'][y]['error'], flush=True); continue
        nan = float(np.isnan(v).any(axis=1).mean())
        out = pd.DataFrame(v.astype(np.float16), columns=[f'T{i:03d}' for i in range(v.shape[1])]).assign(parcref=pts.parcref.values)
        out.to_parquet(os.path.join(D, f'tessera_{y}.parquet'), index=False)
        rep['years'][y] = {'dims': int(v.shape[1]), 'share_missing': round(nan, 4), 'seconds': round(time.time() - t0, 1),
                           'mb_fetched': round((du(CACHE) - b0) / 1e6, 1)}
        if nan > 0.5:
            st = gt.probe(float(pts.lon.iloc[0]), float(pts.lat.iloc[0]), y)[1]
            rep['years'][y]['probe_status_first_point'] = st
        print(y, rep['years'][y], flush=True)
    json.dump(rep, open(os.path.join(D, 'report.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
