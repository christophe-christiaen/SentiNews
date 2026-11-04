"""Addendum 6 Part F establishment: February-March clear, green and water dates per cereal parcel, by direct Earth Engine
requests (protocol: wp3_elms_effect/results/w3_z_addendum6_hazards_protocol.md, record row of 4 November 2026).

Same mask, 15 m buffer and scale as gee_s2_parcels.py. Each UTC day's scenes are mosaicked into one date; per pixel it
counts clear dates, clear dates with NDVI above 0.3 and water dates (scene class 6); values are means over the buffer.
Output: shared/data/s2/gee_local_estab/s2e_<square>_<year>.csv   parcref, clear, high, water (private; re-runs skip done)
Usage: python gee_s2_establishment.py --project <earth-engine-project> [--workers 8] [--only 10_8_2020]
"""
import argparse, os, time
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd, ee
import gee_s2_parcels as g
from gee_s2_interactive import init_ee

OUT = os.path.join(g.D, 's2', 'gee_local_estab')
CHUNK = 800
YEARS = range(2018, 2027)
COLS = ['parcref', 'clear', 'high', 'water']


def stack(region, year):
    t0 = ee.Date.fromYMD(year, 2, 1); t1 = ee.Date.fromYMD(year, 4, 1)
    cs = ee.ImageCollection('GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED')
    col = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED').filterBounds(region).filterDate(t0, t1).linkCollection(cs, ['cs_cdf'])

    def prep(img):
        scl = img.select('SCL'); good = img.select('cs_cdf').gte(g.CS_MIN)
        ndvi = img.normalizedDifference(['B8', 'B4']).rename('ndvi').updateMask(good.And(scl.eq(4).Or(scl.eq(5))))
        water = ee.Image(1).rename('w').updateMask(good.And(scl.eq(6)))
        return ee.Image.cat(ndvi, water).copyProperties(img, ['system:time_start'])
    col = col.map(prep)

    def daily(k):
        d = t0.advance(ee.Number(k), 'day')
        sub = col.filterDate(d, d.advance(1, 'day'))
        none = ee.Image.constant([0, 0]).rename(['ndvi', 'w']).updateMask(0)
        m = ee.Image(ee.Algorithms.If(sub.size().gt(0), sub.mosaic(), none))
        n = m.select('ndvi')
        return ee.Image.cat(n.mask().gt(0).unmask(0).rename('clear').toInt(), n.gt(0.3).unmask(0).rename('high').toInt(),
                            m.select('w').mask().gt(0).unmask(0).rename('water').toInt())
    days = ee.List.sequence(0, t1.difference(t0, 'day').subtract(1))
    return ee.ImageCollection(days.map(daily)).sum()


def one_chunk(sub, year, tries=10):
    for k in range(tries):
        try:
            pts = g.fc_for(sub).map(lambda f: f.buffer(15))
            fc = stack(pts.geometry().bounds(), year).reduceRegions(collection=pts, reducer=ee.Reducer.mean(), scale=10, tileScale=4)
            return pd.DataFrame([f['properties'] for f in fc.getInfo()['features']]).reindex(columns=COLS)
        except Exception as e:
            msg = str(e)
            busy = 'too many' in msg.lower() or 'concurrency' in msg.lower() or 'quota' in msg.lower()
            time.sleep(min(30 * (k + 1), 180) if busy else 5 * (k + 1))
    raise RuntimeError(f'chunk failed after {tries} tries: {msg[:100]}')


def square_year(t, sq, year, pool):
    dst = os.path.join(OUT, f's2e_{sq}_{year}.csv')
    if os.path.exists(dst):
        return sq, year, 'exists', 0
    sub = t[t.sq == sq].reset_index(drop=True)
    futs = [pool.submit(one_chunk, sub.iloc[i:i + CHUNK], year) for i in range(0, len(sub), CHUNK)]
    res = pd.concat([f.result() for f in futs], ignore_index=True)
    assert len(res) == len(sub), (sq, year, len(res), len(sub))
    res.to_csv(dst + '.tmp', index=False); os.replace(dst + '.tmp', dst)
    return sq, year, 'done', len(res)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--project', required=True); ap.add_argument('--workers', type=int, default=8)
    ap.add_argument('--parallel-squares', type=int, default=6); ap.add_argument('--only')
    a = ap.parse_args()
    init_ee(a.project); os.makedirs(OUT, exist_ok=True)
    t = g.chunks('cereal')
    jobs = [(sq, y) for sq in sorted(t.sq.unique()) for y in YEARS]
    if a.only:
        sq, y = a.only.rsplit('_', 1); jobs = [(sq, int(y))]
    print(f'{len(jobs)} square-years, {len(t)} parcels', flush=True); t0 = time.time(); bad = 0
    with ThreadPoolExecutor(a.workers) as pool, ThreadPoolExecutor(a.parallel_squares) as outer:
        futs = [outer.submit(square_year, t, sq, y, pool) for sq, y in jobs]
        for n, f in enumerate(as_completed(futs), 1):
            try:
                sq, y, state, rows = f.result()
                print(f'{n}/{len(jobs)} {sq}_{y}: {state} {rows} ({(time.time() - t0) / 60:.1f} min)', flush=True)
            except Exception as e:
                bad += 1; print(f'{n}/{len(jobs)} FAILED: {str(e)[:150]}', flush=True)
    print('finished; failed square-years:', bad, flush=True)


if __name__ == '__main__':
    main()
