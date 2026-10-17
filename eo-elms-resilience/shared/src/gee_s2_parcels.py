"""National Sentinel-2 crop-stress extraction for cereal parcels on Google Earth Engine (exports to Google Drive).

Parcels: cereal land from parcels/parcel_panel.parquet (381k RPA parcel points), grouped into 50 km BNG squares; one
export task per square x year (2017-2026), each sent with its points (no asset upload needed).

Per task, in Earth Engine:
  COPERNICUS/S2_SR_HARMONIZED, March-August, linked to Cloud Score+ (GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED);
  a pixel is used when cs_cdf >= CS_MIN and SCL is vegetation (4) or bare soil (5);
  indices NDVI (B8, B4), NDRE (B8A, B5), NDMI (B8A, B11); half-monthly medians, 12 periods (p01 = 1-15 Mar ... p12 =
  16-31 Aug) plus the number of clear looks per period (n01..n12); values are means over a 15 m buffer (~3 x 3 pixels).
Output: Drive folder DRIVE_FOLDER, one CSV per task: parcref, ndvi_p01..p12, ndre_p01..p12, ndmi_p01..p12, n_p01..p12

Usage
  python gee_s2_parcels.py --project ee-natusjatkachenko03 --test            # one square, 2022, waits for the result
  python gee_s2_parcels.py --project ee-natusjatkachenko03 --submit          # all squares x years (skips submitted)
  python gee_s2_parcels.py --project ee-natusjatkachenko03 --status
"""
import argparse, json, os, time
import numpy as np, pandas as pd, ee

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
D = os.path.join(ROOT, 'shared', 'data')
LOG = os.path.join(D, 's2', 'gee_tasks.json')
DRIVE_FOLDER = 'eo_elms_s2_parcels'
YEARS = range(2017, 2027)
SQUARE_M = 50_000
CS_MIN = 0.60
PERIODS = [(m, d0, d1) for m in range(3, 9) for d0, d1 in ((1, 15), (16, 31))]


def chunks(which='cereal'):
    if which == 'grass':                                   # U1 sample (wp2_resilience/results/u1_grassland_protocol.md)
        t = pd.read_parquet(os.path.join(D, 'parcels', 'grass_sample.parquet'), columns=['parcref', 'x', 'y'])
    else:
        t = pd.read_parquet(os.path.join(D, 'parcels', 'parcel_panel.parquet'), columns=['parcref', 'x', 'y', 'cereal_land'])
        t = t[t.cereal_land].copy()
    t['sq'] = (t.x // SQUARE_M).astype(int).astype(str) + '_' + (t.y // SQUARE_M).astype(int).astype(str)
    return t


def fc_for(t):
    from pyproj import Transformer
    lon, lat = Transformer.from_crs(27700, 4326, always_xy=True).transform(t.x.values, t.y.values)
    return ee.FeatureCollection([ee.Feature(ee.Geometry.Point([float(a), float(b)]), {'parcref': p})
                                 for p, a, b in zip(t.parcref.values, lon, lat)])


def s2_stack(region, year):
    cs = ee.ImageCollection('GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED')
    col = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED').filterBounds(region)
           .filterDate(f'{year}-03-01', f'{year}-09-01').linkCollection(cs, ['cs_cdf']))

    def prep(img):
        scl = img.select('SCL')
        ok = img.select('cs_cdf').gte(CS_MIN).And(scl.eq(4).Or(scl.eq(5)))
        nd = lambda a, b: img.normalizedDifference([a, b])
        return (ee.Image.cat(nd('B8', 'B4').rename('ndvi'), nd('B8A', 'B5').rename('ndre'), nd('B8A', 'B11').rename('ndmi'),
                             ee.Image(1).rename('n')).updateMask(ok).copyProperties(img, ['system:time_start']))
    col = col.map(prep)
    bands = []
    for k, (m, d0, d1) in enumerate(PERIODS, 1):
        start = ee.Date.fromYMD(year, m, d0)
        end = ee.Date.fromYMD(year, m, 16) if d1 == 15 else ee.Date.fromYMD(year, m, 1).advance(1, 'month')
        sub = col.filterDate(start, end)
        # a period with no scenes (e.g. early 2017) gives masked bands instead of an image without bands
        empty = ee.Image.constant([0, 0, 0]).rename(['ndvi', 'ndre', 'ndmi']).updateMask(0)
        med = ee.Image(ee.Algorithms.If(sub.size().gt(0), sub.select(['ndvi', 'ndre', 'ndmi']).median(), empty))
        cnt = ee.Image(ee.Algorithms.If(sub.size().gt(0), sub.select('n').count(), ee.Image.constant(0).rename('n')))
        bands += [med.select('ndvi').rename(f'ndvi_p{k:02d}'), med.select('ndre').rename(f'ndre_p{k:02d}'),
                  med.select('ndmi').rename(f'ndmi_p{k:02d}'), cnt.rename(f'n_p{k:02d}')]
    return ee.Image.cat(bands)


def task_for(t, sq, year):
    pts = fc_for(t).map(lambda f: f.buffer(15))
    img = s2_stack(pts.geometry().bounds(), year)
    out = img.reduceRegions(collection=pts, reducer=ee.Reducer.mean(), scale=10, tileScale=4)
    sel = ['parcref'] + [f'{v}_p{k:02d}' for k in range(1, 13) for v in ('ndvi', 'ndre', 'ndmi', 'n')]
    name = f's2_{sq}_{year}'
    return ee.batch.Export.table.toDrive(collection=out, description=name, folder=DRIVE_FOLDER, fileNamePrefix=name,
                                         fileFormat='CSV', selectors=sel), name


def load_log():
    return json.load(open(LOG)) if os.path.exists(LOG) else {}


def save_log(log):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    json.dump(log, open(LOG, 'w'), indent=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--project', required=True)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--test', action='store_true'); g.add_argument('--submit', action='store_true'); g.add_argument('--status', action='store_true')
    a = ap.parse_args()
    ee.Initialize(project=a.project)
    log = load_log()
    if a.status:
        tasks = {}
        for t in ee.data.getTaskList():                   # newest first: keep the latest attempt per task name
            if t['description'].startswith('s2_'):
                tasks.setdefault(t['description'], t['state'])
        for k in log:
            log[k]['state'] = tasks.get(k, log[k].get('state'))
        save_log(log)
        print(pd.Series([v['state'] for v in log.values()]).value_counts().to_string())
        return
    t = chunks()
    if a.test:
        sq = t.groupby('sq').size().sort_values().index[len(t.sq.unique()) // 2]   # a mid-sized square
        task, name = task_for(t[t.sq == sq], sq, 2022)
        task.start(); t0 = time.time()
        print(f'test {name}: {int((t.sq == sq).sum()):,} parcels', flush=True)
        while task.status()['state'] in ('READY', 'RUNNING'):
            time.sleep(30)
        print(task.status()['state'], f'{(time.time() - t0) / 60:.1f} min', task.status().get('error_message', ''), flush=True)
        log[name] = {'state': task.status()['state'], 'parcels': int((t.sq == sq).sum())}; save_log(log)
        return
    sizes = t.groupby('sq').size()
    print(f'{len(sizes)} squares x {len(YEARS)} years; parcels per square: median {int(sizes.median())}, max {int(sizes.max())}')
    n = 0
    for sq in sizes.index:
        sub = t[t.sq == sq]
        for y in YEARS:
            name = f's2_{sq}_{y}'
            if log.get(name, {}).get('state') in ('READY', 'RUNNING', 'COMPLETED'):
                continue
            task, _ = task_for(sub, sq, y)
            for k in range(5):
                try:
                    task.start(); break
                except Exception as e:
                    print(f'  {name}: retry ({str(e)[:80]})', flush=True); time.sleep(30 * (k + 1))
            log[name] = {'state': 'READY', 'parcels': len(sub)}; n += 1
            if n % 25 == 0:
                save_log(log); print(f'  submitted {n}', flush=True)
    save_log(log)
    print(f'submitted {n} tasks to Drive folder {DRIVE_FOLDER}', flush=True)


if __name__ == '__main__':
    main()
