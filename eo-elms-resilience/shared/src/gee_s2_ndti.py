"""Addendum 5, section 2 (wp3_elms_effect/results/w3_x_addendum5_products_protocol.md): Sentinel-2 tillage index
NDTI = (B11 - B12) / (B11 + B12) for the sample parcels of the ΔAI run (record of 19 November 2026).

Same recipe as gee_s2_parcels.py: Cloud Score+ (cs_cdf >= 0.60) and SCL vegetation or bare soil, medians, 15 m buffer
around the parcel point, parallel interactive requests as gee_s2_interactive.py.
  year Y: ndti_p01..p12 = half-months 1-15 March ... 16-31 August of Y; ndti_w01..w05 = October, November, December of
  Y-1, January, February of Y (monthly); n_* = clear scenes per period.
Years 2018, 2019, 2020, 2025.

Usage   python gee_s2_ndti.py --project PROJECT --parcels PARCELS.parquet [--workers 8]
Output  shared/data/s2/gee_local_ndti/ndti_<square>_<year>.csv (per-parcel; not published)
"""
import argparse, os, time
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd, ee
import gee_s2_parcels as g
from gee_s2_interactive import init_ee

OUT = os.path.join(g.D, 's2', 'gee_local_ndti')
YEARS = [2018, 2019, 2020, 2025]
CHUNK = 800
WIN = [(-1, 10), (-1, 11), (-1, 12), (0, 1), (0, 2)]          # (year offset, month)
COLS = (['parcref'] + [f'ndti_p{k:02d}' for k in range(1, 13)] + [f'ndti_w{k:02d}' for k in range(1, 6)]
        + [f'n_p{k:02d}' for k in range(1, 13)] + [f'n_w{k:02d}' for k in range(1, 6)])


def stack(region, year):
    cs = ee.ImageCollection('GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED')
    col = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED').filterBounds(region)
           .filterDate(f'{year - 1}-10-01', f'{year}-09-01').linkCollection(cs, ['cs_cdf']))

    def prep(img):
        scl = img.select('SCL')
        ok = img.select('cs_cdf').gte(g.CS_MIN).And(scl.eq(4).Or(scl.eq(5)))
        return (ee.Image.cat(img.normalizedDifference(['B11', 'B12']).rename('ndti'), ee.Image(1).rename('n'))
                .updateMask(ok).copyProperties(img, ['system:time_start']))
    col = col.map(prep)
    empty = ee.Image.constant(0).rename('ndti').updateMask(0)

    def period(start, end, tag):
        sub = col.filterDate(start, end)
        med = ee.Image(ee.Algorithms.If(sub.size().gt(0), sub.select('ndti').median(), empty))
        cnt = ee.Image(ee.Algorithms.If(sub.size().gt(0), sub.select('n').count(), ee.Image.constant(0).rename('n')))
        return [med.rename(f'ndti_{tag}'), cnt.rename(f'n_{tag}')]
    bands = []
    for k, (mo, d0, d1) in enumerate(g.PERIODS, 1):
        start = ee.Date.fromYMD(year, mo, d0)
        end = ee.Date.fromYMD(year, mo, 16) if d1 == 15 else ee.Date.fromYMD(year, mo, 1).advance(1, 'month')
        bands += period(start, end, f'p{k:02d}')
    for k, (dy, mo) in enumerate(WIN, 1):
        start = ee.Date.fromYMD(year + dy, mo, 1)
        bands += period(start, start.advance(1, 'month'), f'w{k:02d}')
    return ee.Image.cat(bands)


def one_chunk(sub, year, tries=10):
    msg = ''
    for k in range(tries):
        try:
            pts = g.fc_for(sub).map(lambda f: f.buffer(15))
            fc = stack(pts.geometry().bounds(), year).reduceRegions(collection=pts, reducer=ee.Reducer.mean(), scale=10, tileScale=4)
            return pd.DataFrame([f['properties'] for f in fc.getInfo()['features']]).reindex(columns=COLS)
        except Exception as e:
            msg = str(e); busy = any(w in msg.lower() for w in ('too many', 'concurrency', 'quota'))
            time.sleep(min(30 * (k + 1), 180) if busy else 5 * (k + 1))
    raise RuntimeError(f'chunk failed after {tries} tries: {msg[:100]}')


def square_year(t, sq, year, pool):
    dst = os.path.join(OUT, f'ndti_{sq}_{year}.csv')
    if os.path.exists(dst):
        return sq, year, 'exists', 0
    sub = t[t.sq == sq].reset_index(drop=True)
    futs = [pool.submit(one_chunk, sub.iloc[i:i + CHUNK], year) for i in range(0, len(sub), CHUNK)]
    res = pd.concat([f.result() for f in futs], ignore_index=True)
    res.to_csv(dst + '.tmp', index=False); os.replace(dst + '.tmp', dst)
    return sq, year, 'done', len(res)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--project', required=True); ap.add_argument('--parcels', required=True)
    ap.add_argument('--workers', type=int, default=8); ap.add_argument('--parallel-squares', type=int, default=6)
    ap.add_argument('--only', help='one square_year, e.g. 10_8_2019 (test)')
    a = ap.parse_args()
    init_ee(a.project); os.makedirs(OUT, exist_ok=True)
    t = pd.read_parquet(a.parcels)
    t['sq'] = (t.x // g.SQUARE_M).astype(int).astype(str) + '_' + (t.y // g.SQUARE_M).astype(int).astype(str)
    jobs = [(sq, y) for sq in sorted(t.sq.unique()) for y in YEARS]
    if a.only:
        sq, y = a.only.rsplit('_', 1); jobs = [(sq, int(y))]
    print(f'{len(jobs)} square-years, {len(t):,} parcels', flush=True); t0 = time.time()
    with ThreadPoolExecutor(a.workers) as pool, ThreadPoolExecutor(a.parallel_squares) as outer:
        futs = [outer.submit(square_year, t, sq, y, pool) for sq, y in jobs]
        for n, f in enumerate(as_completed(futs), 1):
            try:
                sq, y, state, rows = f.result()
                print(f'  {n}/{len(jobs)} ndti_{sq}_{y}: {state} {rows} ({(time.time() - t0) / 60:.1f} min)', flush=True)
            except Exception as e:
                print(f'  {n}/{len(jobs)} failed: {str(e)[:120]}', flush=True)


if __name__ == '__main__':
    main()
