"""National Sentinel-1 extraction for cereal parcels on Earth Engine (direct requests, like gee_s2_interactive.py).

Season Y runs from October Y-1 to August Y: 22 half-monthly periods (p01 = 1-15 October ... p22 = 16-31 August),
seasons 2017-2026. COPERNICUS/S1_GRD, IW mode, VV + VH, 10 m (backscatter in dB, calibrated and orthorectified).
Per period: median VV and VH over all passes (both orbit directions) and the number of passes; values are means over a
20 m buffer around the parcel point (radar speckle needs a slightly larger footprint than optical).
Uses (see shared/results/s1_waterlogging_test.md): winter soil-wetness anomaly, cloud gap-filling in May-July,
field operations (ploughing, cover crops, harvest). Not a flood detector at this scale.
Orbit mix changes over time (Sentinel-1B lost in December 2021): anomalies are built afterwards against each parcel's
own normal for the same period of the year, and the pass count is kept for checks.

Output: shared/data/s1/gee_local/s1_<square>_<season>.csv
Usage:  python gee_s1_interactive.py --project ee-natusjatkachenko03 [--workers 12 --parallel-squares 5 --only 10_8_2024]
"""
import argparse, os, time
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd, ee
import gee_s2_parcels as g

OUT = os.path.join(g.D, 's1', 'gee_local')
CHUNK = 800
SEASONS = range(2017, 2027)
PERIODS = [((y_off, m), d0, d1) for y_off, months in ((-1, range(10, 13)), (0, range(1, 9))) for m in months
           for d0, d1 in ((1, 15), (16, 31))]
COLS = ['parcref'] + [f'{v}_p{k:02d}' for k in range(1, 23) for v in ('vv', 'vh', 'n')]


def s1_stack(region, season):
    col = (ee.ImageCollection('COPERNICUS/S1_GRD').filterBounds(region)
           .filter(ee.Filter.eq('instrumentMode', 'IW'))
           .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
           .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'))
           .filterDate(f'{season - 1}-10-01', f'{season}-09-01').select(['VV', 'VH']))
    bands = []
    for k, ((y_off, m), d0, d1) in enumerate(PERIODS, 1):
        y = season + y_off
        start = ee.Date.fromYMD(y, m, d0)
        end = ee.Date.fromYMD(y, m, 16) if d1 == 15 else ee.Date.fromYMD(y, m, 1).advance(1, 'month')
        sub = col.filterDate(start, end)
        empty = ee.Image.constant([0, 0]).rename(['VV', 'VH']).updateMask(0)
        med = ee.Image(ee.Algorithms.If(sub.size().gt(0), sub.median(), empty))
        cnt = ee.Image(ee.Algorithms.If(sub.size().gt(0), sub.select('VV').count(), ee.Image.constant(0)))
        bands += [med.select('VV').rename(f'vv_p{k:02d}'), med.select('VH').rename(f'vh_p{k:02d}'), ee.Image(cnt).rename(f'n_p{k:02d}')]
    return ee.Image.cat(bands)


def one_chunk(sub, season, tries=10):
    msg = ''
    for k in range(tries):
        try:
            pts = g.fc_for(sub).map(lambda f: f.buffer(20))
            img = s1_stack(pts.geometry().bounds(), season)
            fc = img.reduceRegions(collection=pts, reducer=ee.Reducer.mean(), scale=10, tileScale=4)
            return pd.DataFrame([f['properties'] for f in fc.getInfo()['features']]).reindex(columns=COLS)
        except Exception as e:
            msg = str(e)
            busy = 'too many' in msg.lower() or 'concurrency' in msg.lower() or 'quota' in msg.lower()
            time.sleep(min(30 * (k + 1), 180) if busy else 5 * (k + 1))
    raise RuntimeError(f'chunk failed after {tries} tries: {msg[:100]}')


def square_season(t, sq, season, pool):
    dst = os.path.join(OUT, f's1_{sq}_{season}.csv')
    if os.path.exists(dst):
        return sq, season, 'exists', 0
    sub = t[t.sq == sq].reset_index(drop=True)
    futs = [pool.submit(one_chunk, sub.iloc[i:i + CHUNK], season) for i in range(0, len(sub), CHUNK)]
    res = pd.concat([f.result() for f in futs], ignore_index=True)
    res.to_csv(dst + '.tmp', index=False); os.replace(dst + '.tmp', dst)
    return sq, season, 'done', len(res)


def init_ee(project, tries=20):
    for k in range(tries):                              # restricted-mode projects: login can be refused while busy
        try:
            ee.Initialize(project=project); return
        except Exception as e:
            if k == tries - 1: raise
            time.sleep(30)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--project', required=True)
    ap.add_argument('--workers', type=int, default=12)
    ap.add_argument('--parallel-squares', type=int, default=5)
    ap.add_argument('--only', help='one square_season, e.g. 10_8_2024 (test)')
    a = ap.parse_args()
    init_ee(a.project)
    os.makedirs(OUT, exist_ok=True)
    t = g.chunks()
    jobs = [(sq, y) for sq in sorted(t.sq.unique()) for y in SEASONS]
    if a.only:
        sq, y = a.only.rsplit('_', 1); jobs = [(sq, int(y))]
    print(f'{len(jobs)} square-seasons to fetch, {a.workers} parallel requests', flush=True)
    t0 = time.time()
    with ThreadPoolExecutor(a.workers) as pool, ThreadPoolExecutor(a.parallel_squares) as outer:
        futs = [outer.submit(square_season, t, sq, y, pool) for sq, y in jobs]
        for n, f in enumerate(as_completed(futs), 1):
            try:
                sq, y, state, rows = f.result()
                print(f'  {n}/{len(jobs)} s1_{sq}_{y}: {state} {rows} parcels ({(time.time() - t0) / 60:.1f} min)', flush=True)
            except Exception as e:
                print(f'  {n}/{len(jobs)} failed: {str(e)[:120]}', flush=True)


if __name__ == '__main__':
    main()
