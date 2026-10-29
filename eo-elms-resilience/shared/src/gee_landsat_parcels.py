"""Landsat 30 m NDVI at every cereal parcel point, 2001-2026, for a field-level long baseline (W2-1;
wp2_resilience/results/w2_1_landsat_protocol.md, written before any Landsat value was extracted).

Landsat 5, 7, 8, 9 Collection 2 Level-2 surface reflectance; QA_PIXEL fill, dilated cloud, cloud, shadow and snow masked;
SR = DN * 0.0000275 - 0.2. Per season Y: july_Y = median of clear NDVI 1 July-15 August; peak_Y = maximum of clear NDVI
15 April-15 July. Also Landsat 7 alone (l7july_Y, l7peak_Y, 2001-2023) for the sensitivity check. Value at the 30 m
pixel containing the parcel point. No cross-sensor coefficients (cell x season effects absorb season-wide offsets).

Output: shared/data/landsat_parcels/landsat_<square>.csv
Usage:  python gee_landsat_parcels.py --project ee-natusjatkachenko03 [--workers 4 --parallel-squares 3 --only 10_8]
"""
import argparse, os, time
from concurrent.futures import ThreadPoolExecutor
import pandas as pd, ee
import gee_s2_parcels as g
from gee_s1_interactive import init_ee

OUT = os.path.join(g.D, 'landsat_parcels')
CHUNK = 1000
YEARS = range(2001, 2027)
L7_YEARS = range(2001, 2024)
COLS = ['parcref'] + [f'{k}_{y}' for y in YEARS for k in ('july', 'peak')] + [f'l7{k}_{y}' for y in L7_YEARS for k in ('july', 'peak')]


def prep(red, nir):
    def f(im):
        qa = im.select('QA_PIXEL')
        bad = (1 << 0) | (1 << 1) | (1 << 3) | (1 << 4) | (1 << 5)   # fill, dilated cloud, cloud, shadow, snow
        ok = qa.bitwiseAnd(bad).eq(0)
        sr = im.select([red, nir]).multiply(0.0000275).add(-0.2)
        return sr.normalizedDifference([nir, red]).rename('NDVI').updateMask(ok).copyProperties(im, ['system:time_start'])
    return f


def collections():
    c = lambda name, red, nir: ee.ImageCollection(f'LANDSAT/{name}/C02/T1_L2').map(prep(red, nir))
    l7 = c('LE07', 'SR_B3', 'SR_B4')
    allc = c('LT05', 'SR_B3', 'SR_B4').merge(l7).merge(c('LC08', 'SR_B4', 'SR_B5')).merge(c('LC09', 'SR_B4', 'SR_B5'))
    return allc, l7


def season_bands(col, years, prefix):
    empty = ee.Image.constant(0).rename('NDVI').updateMask(0)
    out = []
    for y in years:
        jul = col.filterDate(f'{y}-07-01', f'{y}-08-16')
        pk = col.filterDate(f'{y}-04-15', f'{y}-07-16')
        out.append(ee.Image(ee.Algorithms.If(jul.size().gt(0), jul.median(), empty)).rename(f'{prefix}july_{y}'))
        out.append(ee.Image(ee.Algorithms.If(pk.size().gt(0), pk.max(), empty)).rename(f'{prefix}peak_{y}'))
    return out


IMG = None


def one_chunk(sub, tries=10):
    msg = ''
    for k in range(tries):
        try:
            fc = IMG.reduceRegions(collection=g.fc_for(sub), reducer=ee.Reducer.first(), scale=30, tileScale=8)
            return pd.DataFrame([f['properties'] for f in fc.getInfo()['features']]).reindex(columns=COLS)
        except Exception as e:
            msg = str(e)
            busy = 'too many' in msg.lower() or 'concurrency' in msg.lower() or 'quota' in msg.lower()
            time.sleep(min(30 * (k + 1), 180) if busy else 5 * (k + 1))
    raise RuntimeError(f'chunk failed after {tries} tries: {msg[:100]}')


def square(t, sq, pool):
    dst = os.path.join(OUT, f'landsat_{sq}.csv')
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
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--parallel-squares', type=int, default=3)
    ap.add_argument('--only', help='one square, e.g. 10_8 (test)')
    a = ap.parse_args()
    init_ee(a.project)
    allc, l7 = collections()
    IMG = ee.Image.cat(season_bands(allc, YEARS, '') + season_bands(l7, L7_YEARS, 'l7'))
    os.makedirs(OUT, exist_ok=True)
    t = g.chunks()
    jobs = [a.only] if a.only else sorted(t.sq.unique())
    print(f'{len(jobs)} squares to fetch, {a.workers} parallel requests', flush=True)
    t0 = time.time()
    with ThreadPoolExecutor(a.workers) as pool, ThreadPoolExecutor(a.parallel_squares) as outer:
        futs = [outer.submit(square, t, sq, pool) for sq in jobs]
        for n, f in enumerate(futs, 1):
            try:
                sq, state, rows = f.result()
                print(f'  {n}/{len(jobs)} landsat_{sq}: {state} {rows} parcels ({(time.time() - t0) / 60:.1f} min)', flush=True)
            except Exception as e:
                print(f'  {n}/{len(jobs)} failed: {str(e)[:120]}', flush=True)


if __name__ == '__main__':
    main()
