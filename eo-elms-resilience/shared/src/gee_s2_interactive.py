"""Faster route for the Sentinel-2 parcel extraction: direct (interactive) Earth Engine requests in parallel threads,
instead of the batch export queue (which runs ~1 task at a time for noncommercial projects).

Same computation as gee_s2_parcels.py (same s2_stack: Cloud Score+ / SCL mask, half-monthly medians, 15 m buffer), but
each square x year is split into chunks of CHUNK parcels requested with getInfo(); results are written locally:
  shared/data/s2/gee_local/s2_<square>_<year>.csv     (same columns as the Drive exports)
Square-years already exported to Drive (COMPLETED batch tasks) are skipped unless --all.
Usage: python gee_s2_interactive.py --project ee-natusjatkachenko03 [--workers 8] [--only 10_8_2022]
"""
import argparse, os, time
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd, ee
import gee_s2_parcels as g

OUT = os.path.join(g.D, 's2', 'gee_local')
CHUNK = 800
COLS = ['parcref'] + [f'{v}_p{k:02d}' for k in range(1, 13) for v in ('ndvi', 'ndre', 'ndmi', 'n')]


def one_chunk(sub, year, tries=10):
    for k in range(tries):
        try:
            pts = g.fc_for(sub).map(lambda f: f.buffer(15))
            img = g.s2_stack(pts.geometry().bounds(), year)
            fc = img.reduceRegions(collection=pts, reducer=ee.Reducer.mean(), scale=10, tileScale=4)
            rows = [f['properties'] for f in fc.getInfo()['features']]
            return pd.DataFrame(rows).reindex(columns=COLS)
        except Exception as e:
            msg = str(e)
            busy = 'too many' in msg.lower() or 'concurrency' in msg.lower() or 'quota' in msg.lower()
            time.sleep(min(30 * (k + 1), 180) if busy else 5 * (k + 1))   # restricted-mode projects: back off
    raise RuntimeError(f'chunk failed after {tries} tries: {msg[:100]}')


def square_year(t, sq, year, pool):
    dst = os.path.join(OUT, f's2_{sq}_{year}.csv')
    if os.path.exists(dst):
        return sq, year, 'exists', 0
    sub = t[t.sq == sq].reset_index(drop=True)
    parts = [sub.iloc[i:i + CHUNK] for i in range(0, len(sub), CHUNK)]
    futs = [pool.submit(one_chunk, p, year) for p in parts]
    res = pd.concat([f.result() for f in futs], ignore_index=True)
    res.to_csv(dst + '.tmp', index=False); os.replace(dst + '.tmp', dst)
    return sq, year, 'done', len(res)


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
    ap.add_argument('--workers', type=int, default=8)
    ap.add_argument('--only', help='one square_year, e.g. 10_8_2022 (test)')
    ap.add_argument('--all', action='store_true', help='also redo square-years already exported to Drive')
    ap.add_argument('--parallel-squares', type=int, default=6, help='square-years in flight at once (keeps all request slots busy)')
    ap.add_argument('--set', default='cereal', choices=['cereal', 'grass'])
    a = ap.parse_args()
    global OUT
    if a.set == 'grass':
        OUT = os.path.join(g.D, 's2', 'gee_local_grass')
    init_ee(a.project)
    os.makedirs(OUT, exist_ok=True)
    t = g.chunks(a.set)
    jobs = [(sq, y) for sq in sorted(t.sq.unique()) for y in g.YEARS]
    if a.only:
        sq, y = a.only.rsplit('_', 1); jobs = [(sq, int(y))]
    elif not a.all and a.set == 'cereal':
        done = set()
        for task in ee.data.getTaskList():
            if task['description'].startswith('s2_') and task['state'] == 'COMPLETED':
                done.add(task['description'])
        jobs = [(sq, y) for sq, y in jobs if f's2_{sq}_{y}' not in done]
    print(f'{len(jobs)} square-years to fetch, {a.workers} parallel requests', flush=True)
    t0 = time.time()
    with ThreadPoolExecutor(a.workers) as pool, ThreadPoolExecutor(a.parallel_squares) as outer:
        futs = [outer.submit(square_year, t, sq, y, pool) for sq, y in jobs]
        for n, f in enumerate(as_completed(futs), 1):
            try:
                sq, y, state, rows = f.result()
                print(f'  {n}/{len(jobs)} s2_{sq}_{y}: {state} {rows} parcels ({(time.time() - t0) / 60:.1f} min)', flush=True)
            except Exception as e:
                print(f'  {n}/{len(jobs)} failed: {str(e)[:120]}', flush=True)


if __name__ == '__main__':
    main()
