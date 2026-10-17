"""MODIS NDVI per cereal parcel point, 2001-2026, for a long field-level baseline (Paper 2: the Sentinel-2 normal
has only four seasons, which creates false persistence; MODIS gives sixteen, 2001-2016).

MODIS/061/MOD13Q1 (250 m, 16-day composites), NDVI scaled by 0.0001, kept where SummaryQA <= 1 (good or marginal).
Per season Y: july_Y = mean of composites starting in July; peak_Y = maximum of composites starting 15 April -
15 July (the same windows as the Sentinel-2 stress index). Value at the 250 m pixel containing the parcel point (many
small parcels share a pixel: a limitation, stated in the results).

Output: shared/data/modis_parcels/modis_<square>.csv (parcref, july_2001..2026, peak_2001..2026)
Usage:  python gee_modis_parcels.py --project ee-natusjatkachenko03 [--workers 12 --parallel-squares 5 --only 10_8]
"""
import argparse, os, time
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd, ee
import gee_s2_parcels as g
from gee_s1_interactive import init_ee

OUT = os.path.join(g.D, 'modis_parcels')
CHUNK = 1500
YEARS = range(2001, 2027)
COLS = ['parcref'] + [f'{k}_{y}' for y in YEARS for k in ('july', 'peak')]


def stack():
    col = ee.ImageCollection('MODIS/061/MOD13Q1').select(['NDVI', 'SummaryQA'])
    good = col.map(lambda im: im.select('NDVI').multiply(0.0001).updateMask(im.select('SummaryQA').lte(1))
                   .copyProperties(im, ['system:time_start']))
    bands = []
    empty = ee.Image.constant(0).rename('NDVI').updateMask(0)
    for y in YEARS:
        jul = good.filterDate(f'{y}-07-01', f'{y}-08-01')
        pk = good.filterDate(f'{y}-04-15', f'{y}-07-16')
        bands.append(ee.Image(ee.Algorithms.If(jul.size().gt(0), jul.mean(), empty)).rename(f'july_{y}'))
        bands.append(ee.Image(ee.Algorithms.If(pk.size().gt(0), pk.max(), empty)).rename(f'peak_{y}'))
    return ee.Image.cat(bands)


IMG = None


def one_chunk(sub, tries=10):
    msg = ''
    for k in range(tries):
        try:
            fc = IMG.reduceRegions(collection=g.fc_for(sub), reducer=ee.Reducer.first(), scale=250, tileScale=4)
            return pd.DataFrame([f['properties'] for f in fc.getInfo()['features']]).reindex(columns=COLS)
        except Exception as e:
            msg = str(e)
            busy = 'too many' in msg.lower() or 'concurrency' in msg.lower() or 'quota' in msg.lower()
            time.sleep(min(30 * (k + 1), 180) if busy else 5 * (k + 1))
    raise RuntimeError(f'chunk failed after {tries} tries: {msg[:100]}')


def square(t, sq, pool):
    dst = os.path.join(OUT, f'modis_{sq}.csv')
    if os.path.exists(dst):
        return sq, 'exists', 0
    sub = t[t.sq == sq].reset_index(drop=True)
    futs = [pool.submit(one_chunk, sub.iloc[i:i + CHUNK]) for i in range(0, len(sub), CHUNK)]
    res = pd.concat([f.result() for f in futs], ignore_index=True)
    res.to_csv(dst + '.tmp', index=False); os.replace(dst + '.tmp', dst)
    return sq, 'done', len(res)


def main():
    global IMG
    ap = argparse.ArgumentParser()
    ap.add_argument('--project', required=True)
    ap.add_argument('--workers', type=int, default=12)
    ap.add_argument('--parallel-squares', type=int, default=5)
    ap.add_argument('--only', help='one square, e.g. 10_8 (test)')
    ap.add_argument('--set', default='cereal', choices=['cereal', 'grass'])
    a = ap.parse_args()
    global OUT
    if a.set == 'grass':
        OUT = os.path.join(g.D, 'modis_parcels_grass')
    init_ee(a.project)
    IMG = stack()
    os.makedirs(OUT, exist_ok=True)
    t = g.chunks(a.set)
    jobs = [a.only] if a.only else sorted(t.sq.unique())
    print(f'{len(jobs)} squares to fetch, {a.workers} parallel requests', flush=True)
    t0 = time.time()
    with ThreadPoolExecutor(a.workers) as pool, ThreadPoolExecutor(a.parallel_squares) as outer:
        futs = [outer.submit(square, t, sq, pool) for sq in jobs]
        for n, f in enumerate(as_completed(futs), 1):
            try:
                sq, state, rows = f.result()
                print(f'  {n}/{len(jobs)} modis_{sq}: {state} {rows} parcels ({(time.time() - t0) / 60:.1f} min)', flush=True)
            except Exception as e:
                print(f'  {n}/{len(jobs)} failed: {str(e)[:120]}', flush=True)


if __name__ == '__main__':
    main()
