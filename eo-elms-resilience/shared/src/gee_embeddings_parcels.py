"""National AlphaEarth embeddings per cereal parcel point, 2017-2025 (GOOGLE/SATELLITE_EMBEDDING/V1/ANNUAL, 64 bands
A00-A63 at 10 m; each year's embedding summarises that year's satellite record for the pixel).

Value at the 10 m pixel containing the parcel point (the same point as the Sentinel-2 extraction). Uses:
  WP3  embedding version of the matching (pre-registration, section 7); detecting options on the field (Paper 3)
  WP1  farming-system context per region; WP2  year-to-year change of a field's embedding = change of land use

Output: shared/data/embeddings/parcels/aef_<square>_<year>.parquet (parcref, A00..A63 as float32)
Usage:  python gee_embeddings_parcels.py --project ee-natusjatkachenko03 [--workers 12 --parallel-squares 5 --only 9_2_2024]
"""
import argparse, os, time
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd, ee
import gee_s2_parcels as g
from gee_s1_interactive import init_ee

OUT = os.path.join(g.D, 'embeddings', 'parcels')
CHUNK = 600
YEARS = range(2017, 2026)
BANDS = [f'A{i:02d}' for i in range(64)]


def image(year):
    return (ee.ImageCollection('GOOGLE/SATELLITE_EMBEDDING/V1/ANNUAL')
            .filterDate(f'{year}-01-01', f'{year + 1}-01-01').mosaic().select(BANDS))


def one_chunk(sub, year, tries=10):
    msg = ''
    for k in range(tries):
        try:
            fc = image(year).reduceRegions(collection=g.fc_for(sub), reducer=ee.Reducer.first(), scale=10, tileScale=4)
            return pd.DataFrame([f['properties'] for f in fc.getInfo()['features']]).reindex(columns=['parcref'] + BANDS)
        except Exception as e:
            msg = str(e)
            busy = 'too many' in msg.lower() or 'concurrency' in msg.lower() or 'quota' in msg.lower()
            time.sleep(min(30 * (k + 1), 180) if busy else 5 * (k + 1))
    raise RuntimeError(f'chunk failed after {tries} tries: {msg[:100]}')


def square_year(t, sq, year, pool):
    dst = os.path.join(OUT, f'aef_{sq}_{year}.parquet')
    if os.path.exists(dst):
        return sq, year, 'exists', 0
    sub = t[t.sq == sq].reset_index(drop=True)
    futs = [pool.submit(one_chunk, sub.iloc[i:i + CHUNK], year) for i in range(0, len(sub), CHUNK)]
    res = pd.concat([f.result() for f in futs], ignore_index=True)
    res[BANDS] = res[BANDS].astype('float32')
    res.to_parquet(dst + '.tmp', index=False); os.replace(dst + '.tmp', dst)
    return sq, year, 'done', len(res)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--project', required=True)
    ap.add_argument('--workers', type=int, default=12)
    ap.add_argument('--parallel-squares', type=int, default=5)
    ap.add_argument('--only', help='one square_year, e.g. 9_2_2024 (test)')
    a = ap.parse_args()
    init_ee(a.project)
    os.makedirs(OUT, exist_ok=True)
    t = g.chunks()
    jobs = [(sq, y) for sq in sorted(t.sq.unique()) for y in YEARS]
    if a.only:
        sq, y = a.only.rsplit('_', 1); jobs = [(sq, int(y))]
    print(f'{len(jobs)} square-years to fetch, {a.workers} parallel requests', flush=True)
    t0 = time.time()
    with ThreadPoolExecutor(a.workers) as pool, ThreadPoolExecutor(a.parallel_squares) as outer:
        futs = [outer.submit(square_year, t, sq, y, pool) for sq, y in jobs]
        for n, f in enumerate(as_completed(futs), 1):
            try:
                sq, y, state, rows = f.result()
                print(f'  {n}/{len(jobs)} aef_{sq}_{y}: {state} {rows} parcels ({(time.time() - t0) / 60:.1f} min)', flush=True)
            except Exception as e:
                print(f'  {n}/{len(jobs)} failed: {str(e)[:120]}', flush=True)


if __name__ == '__main__':
    main()
