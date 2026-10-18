"""U3 fields (wp1_regional_signal/results/u3_protocol.md): random samples of UKFields polygons (Bancroft and Wilkins 2024,
CC BY 4.0) in Scotland (120,000) and Northern Ireland (60,000), as centroid points with polygon area. Sampling uses
the dataset's own uniform `random` property below a fixed threshold, so the draw is reproducible.

Output  shared/data/parcels/ukfields_sample.parquet (parcref = 'UKF_<fid>', nation, x, y (BNG), area_m2, frac)
Usage   python build_ukfields_sample.py --project ee-natusjatkachenko03
"""
import argparse, json, os, time
import numpy as np, pandas as pd, geopandas as gpd, ee
from concurrent.futures import ThreadPoolExecutor
from pyproj import Transformer

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
OUT = os.path.join(ROOT, 'shared', 'data', 'parcels', 'ukfields_sample.parquet')
TARGET = {'Scotland': (120_000, 297_644), 'Northern Ireland': (60_000, 117_344)}   # sample, fields in nation
SLICES = 300


MIN_M2 = 5000                                    # fields under 0.5 ha excluded (protocol record, 18 October 2026)
ITL1 = os.path.join(ROOT, 'data', 'raw', 'boundaries', 'itl1_2021_buc.geojson')


def bbox(name):
    itl = gpd.read_file(ITL1).to_crs(4326)
    x0, y0, x1, y1 = itl[itl.ITL121NM == name].total_bounds
    return ee.Geometry.Rectangle([x0 - 0.02, y0 - 0.02, x1 + 0.02, y1 + 0.02])


def fetch(fc, lo, hi, tries=20):
    sub = fc.filter(ee.Filter.And(ee.Filter.gte('random', lo), ee.Filter.lt('random', hi)))
    sub = sub.map(lambda f: ee.Feature(f.geometry().centroid(1), {'fid': f.get('fid'), 'area': f.geometry().area(1)}))
    for k in range(tries):
        try:
            rows = sub.getInfo()['features']
            return pd.DataFrame([{'fid': r['properties'].get('fid', 'id' + str(r.get('id'))), 'area_m2': r['properties'].get('area'),
                                  'lon': r['geometry']['coordinates'][0], 'lat': r['geometry']['coordinates'][1]} for r in rows])
        except Exception as e:
            print(f'  slice {lo:.5f}: retry {k + 1} ({str(e)[:90]})', flush=True)
            time.sleep(min(15 * (k + 1), 120))
    raise RuntimeError(f'slice {lo}-{hi} failed')


def main(project):
    ee.Initialize(project=project)
    allfc = ee.FeatureCollection('projects/sat-io/open-datasets/UK-FIELDS')
    parts = []
    for nation, (n, total) in TARGET.items():
        frac = n / total
        fc = allfc.filterBounds(bbox(nation))
        edges = np.linspace(0, frac, SLICES + 1)
        with ThreadPoolExecutor(4) as pool:
            res = list(pool.map(lambda i: fetch(fc, float(edges[i]), float(edges[i + 1])), range(SLICES)))
        d = pd.concat(res, ignore_index=True).drop_duplicates('fid')
        pts = gpd.GeoDataFrame(d, geometry=gpd.points_from_xy(d.lon, d.lat), crs=4326)
        itl = gpd.read_file(ITL1).to_crs(4326)
        d = d[pts.within(itl[itl.ITL121NM == nation].geometry.iloc[0]).values]
        n_all = len(d); d = d[d.area_m2 >= MIN_M2].copy()
        d['nation'], d['frac'] = nation, frac
        parts.append(d); print(nation, n_all, 'fields in the nation;', len(d), 'of at least 0.5 ha', flush=True)
    d = pd.concat(parts, ignore_index=True)
    d['x'], d['y'] = Transformer.from_crs(4326, 27700, always_xy=True).transform(d.lon.values, d.lat.values)
    d['parcref'] = 'UKF_' + d.fid.astype(str)
    d[['parcref', 'nation', 'x', 'y', 'lon', 'lat', 'area_m2', 'frac']].to_parquet(OUT, index=False)
    print(d.groupby('nation').area_m2.describe().round(0))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--project', required=True)
    main(ap.parse_args().project)
