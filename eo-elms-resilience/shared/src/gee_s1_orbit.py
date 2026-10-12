"""Sentinel-1 re-extraction per orbit direction, angle-normalised (fixes the satellite-mix problem in
shared/results/s1_panel_quality.md: the blended run tracked winter rainfall at r = 0.10 only).

Season Y = October Y-1 to August Y, 11 monthly periods (m01 = October ... m11 = August), seasons 2017-2026.
Per period and orbit direction (asc / desc): median gamma0 VV and VH in dB, where gamma0 = sigma0 / cos(incidence
angle), i.e. sigma0_dB - 10 log10(cos theta); the pass count; and the share of passes from Sentinel-1A (the rest are
1B before 2022 and 1C from 2025). Mean over a 20 m buffer around the parcel point, as before.
Anomalies are then built within parcel x direction x month, so a change in which satellites flew no longer looks
like a change in soil wetness.

Output: shared/data/s1/gee_orbit/s1o_<square>_<season>.csv
        with --platform A: shared/data/s1/gee_orbit_1A/ (Sentinel-1A passes only; used for 2026, when Sentinel-1C
        passes read darker than 1A over these fields, see shared/results/s1_orbit_panel_quality.md)
Usage:  python gee_s1_orbit.py --project ee-natusjatkachenko03 [--workers 12 --parallel-squares 5 --only 10_8_2024]
        python gee_s1_orbit.py --project ee-natusjatkachenko03 --platform A --seasons 2026
"""
import argparse, math, os, time
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd, ee
import gee_s2_parcels as g
from gee_s1_interactive import init_ee

OUT = os.path.join(g.D, 's1', 'gee_orbit')
CHUNK = 800
SEASONS = range(2017, 2027)
MONTHS = [(-1, 10), (-1, 11), (-1, 12)] + [(0, m) for m in range(1, 9)]
DIRS = {'asc': 'ASCENDING', 'desc': 'DESCENDING'}
COLS = ['parcref'] + [f'{v}_{d}_m{k:02d}' for k in range(1, 12) for d in DIRS for v in ('vv', 'vh', 'n', 'a')]


def gamma0(img):
    cosang = img.select('angle').multiply(math.pi / 180).cos().log10().multiply(10)
    out = img.select(['VV', 'VH']).subtract(cosang)
    is_a = ee.Image.constant(ee.Number(ee.Algorithms.If(ee.String(img.get('platform_number')).equals('A'), 1, 0)))
    return out.addBands(is_a.rename('A').toFloat()).copyProperties(img, ['system:time_start'])


PLATFORM = None


def stack(region, season):
    base = (ee.ImageCollection('COPERNICUS/S1_GRD').filterBounds(region)
            .filter(ee.Filter.eq('instrumentMode', 'IW'))
            .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
            .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'))
            .filterDate(f'{season - 1}-10-01', f'{season}-09-01'))
    if PLATFORM:
        base = base.filter(ee.Filter.eq('platform_number', PLATFORM))
    bands = []
    empty = ee.Image.constant([0, 0, 0]).rename(['VV', 'VH', 'A']).updateMask(0)
    for d, name in DIRS.items():
        col = base.filter(ee.Filter.eq('orbitProperties_pass', name)).map(gamma0)
        for k, (y_off, m) in enumerate(MONTHS, 1):
            start = ee.Date.fromYMD(season + y_off, m, 1)
            sub = col.filterDate(start, start.advance(1, 'month'))
            has = sub.size().gt(0)
            med = ee.Image(ee.Algorithms.If(has, sub.select(['VV', 'VH']).median().addBands(sub.select('A').mean()), empty))
            cnt = ee.Image(ee.Algorithms.If(has, sub.select('VV').count(), ee.Image.constant(0)))
            bands += [med.select('VV').rename(f'vv_{d}_m{k:02d}'), med.select('VH').rename(f'vh_{d}_m{k:02d}'),
                      ee.Image(cnt).rename(f'n_{d}_m{k:02d}'), med.select('A').rename(f'a_{d}_m{k:02d}')]
    return ee.Image.cat(bands)


def one_chunk(sub, season, tries=10):
    msg = ''
    for k in range(tries):
        try:
            pts = g.fc_for(sub).map(lambda f: f.buffer(20))
            img = stack(pts.geometry().bounds(), season)
            fc = img.reduceRegions(collection=pts, reducer=ee.Reducer.mean(), scale=10, tileScale=4)
            return pd.DataFrame([f['properties'] for f in fc.getInfo()['features']]).reindex(columns=COLS)
        except Exception as e:
            msg = str(e)
            busy = 'too many' in msg.lower() or 'concurrency' in msg.lower() or 'quota' in msg.lower()
            time.sleep(min(30 * (k + 1), 180) if busy else 5 * (k + 1))
    raise RuntimeError(f'chunk failed after {tries} tries: {msg[:100]}')


def square_season(t, sq, season, pool):
    dst = os.path.join(OUT, f's1o_{sq}_{season}.csv')
    if os.path.exists(dst):
        return sq, season, 'exists', 0
    sub = t[t.sq == sq].reset_index(drop=True)
    futs = [pool.submit(one_chunk, sub.iloc[i:i + CHUNK], season) for i in range(0, len(sub), CHUNK)]
    res = pd.concat([f.result() for f in futs], ignore_index=True)
    res.to_csv(dst + '.tmp', index=False); os.replace(dst + '.tmp', dst)
    return sq, season, 'done', len(res)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--project', required=True)
    ap.add_argument('--workers', type=int, default=12)
    ap.add_argument('--parallel-squares', type=int, default=5)
    ap.add_argument('--only', help='one square_season, e.g. 10_8_2024 (test)')
    ap.add_argument('--platform', choices=['A'], help='keep only passes from this satellite')
    ap.add_argument('--seasons', type=int, nargs='+', help='only these seasons')
    a = ap.parse_args()
    global OUT, PLATFORM
    if a.platform:
        PLATFORM = a.platform; OUT = os.path.join(g.D, 's1', f'gee_orbit_1{a.platform}')
    init_ee(a.project)
    os.makedirs(OUT, exist_ok=True)
    t = g.chunks()
    jobs = [(sq, y) for sq in sorted(t.sq.unique()) for y in (a.seasons or SEASONS)]
    if a.only:
        sq, y = a.only.rsplit('_', 1); jobs = [(sq, int(y))]
    print(f'{len(jobs)} square-seasons to fetch, {a.workers} parallel requests', flush=True)
    t0 = time.time()
    with ThreadPoolExecutor(a.workers) as pool, ThreadPoolExecutor(a.parallel_squares) as outer:
        futs = [outer.submit(square_season, t, sq, y, pool) for sq, y in jobs]
        for n, f in enumerate(as_completed(futs), 1):
            try:
                sq, y, state, rows = f.result()
                print(f'  {n}/{len(jobs)} s1o_{sq}_{y}: {state} {rows} parcels ({(time.time() - t0) / 60:.1f} min)', flush=True)
            except Exception as e:
                print(f'  {n}/{len(jobs)} failed: {str(e)[:120]}', flush=True)


if __name__ == '__main__':
    main()
