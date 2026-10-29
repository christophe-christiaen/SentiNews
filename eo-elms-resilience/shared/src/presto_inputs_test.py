"""Test of the Presto input extraction (W1-6 / W3-2), run before any national run: monthly inputs in Presto's band
order for one 50 km square of cereal parcels and one year, sampled at parcel points (15 m buffer mean).

Per month (12): Sentinel-1 GRD VV, VH (mean, dB); Sentinel-2 SR B2, B3, B4, B5, B6, B7, B8, B8A, B11, B12 (median,
Cloud Score+ cs_cdf >= 0.6); ERA5-Land monthly temperature_2m (K) and total_precipitation_sum (m). Static: SRTM
elevation and slope. NDVI is computed later from B8 and B4. Normalisation follows Presto's pipeline later.

Input   data/raw/tessera_test/points.csv (same square as the TESSERA test)
Output  data/raw/presto_test/inputs_<year>.csv; timing printed
Usage   python presto_inputs_test.py --project ee-natusjatkachenko03 --year 2022
"""
import argparse, os, time
from concurrent.futures import ThreadPoolExecutor
import pandas as pd, ee

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
OUT = os.path.join(ROOT, 'data', 'raw', 'presto_test')
S2B = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B11', 'B12']
CHUNK = 500


def stack(year, region):
    cs = ee.ImageCollection('GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED')
    s2 = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED').filterBounds(region).filterDate(f'{year}-01-01', f'{year + 1}-01-01')
          .linkCollection(cs, ['cs_cdf']).map(lambda i: i.select(S2B).updateMask(i.select('cs_cdf').gte(0.6))
                                                   .copyProperties(i, ['system:time_start'])))
    s1 = (ee.ImageCollection('COPERNICUS/S1_GRD').filterBounds(region).filterDate(f'{year}-01-01', f'{year + 1}-01-01')
          .filter(ee.Filter.eq('instrumentMode', 'IW'))
          .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
          .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH')).select(['VV', 'VH']))
    era = ee.ImageCollection('ECMWF/ERA5_LAND/MONTHLY_AGGR').filterDate(f'{year}-01-01', f'{year + 1}-01-01').select(['temperature_2m', 'total_precipitation_sum'])
    bands = []
    for m in range(1, 13):
        a, b = ee.Date.fromYMD(year, m, 1), ee.Date.fromYMD(year, m, 1).advance(1, 'month')
        e1 = ee.Image.constant([0, 0]).rename(['VV', 'VH']).updateMask(0)
        e2 = ee.Image.constant([0] * len(S2B)).rename(S2B).updateMask(0)
        c1, c2 = s1.filterDate(a, b), s2.filterDate(a, b)
        i1 = ee.Image(ee.Algorithms.If(c1.size().gt(0), c1.mean(), e1))
        i2 = ee.Image(ee.Algorithms.If(c2.size().gt(0), c2.median(), e2))
        i3 = era.filterDate(a, b).first()
        bands.append(ee.Image.cat(i1, i2, i3).rename([f'{x}_m{m:02d}' for x in ['VV', 'VH'] + S2B + ['temperature_2m', 'total_precipitation']]))
    dem = ee.Image('USGS/SRTMGL1_003')
    return ee.Image.cat(bands + [dem.rename('elevation'), ee.Terrain.slope(dem).rename('slope')])


def chunk(pts, year, tries=10):
    for k in range(tries):
        try:
            fc = ee.FeatureCollection([ee.Feature(ee.Geometry.Point([float(a), float(b)]).buffer(15), {'parcref': p})
                                       for p, a, b in zip(pts.parcref, pts.lon, pts.lat)])
            img = stack(year, fc.geometry().bounds())
            rows = img.reduceRegions(collection=fc, reducer=ee.Reducer.mean(), scale=10, tileScale=4).getInfo()['features']
            return pd.DataFrame([r['properties'] for r in rows])
        except Exception as e:
            msg = str(e); time.sleep(min(30 * (k + 1), 180))
    raise RuntimeError(msg[:150])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--project', required=True); ap.add_argument('--year', type=int, default=2022)
    ap.add_argument('--workers', type=int, default=6); a = ap.parse_args()
    ee.Initialize(project=a.project); os.makedirs(OUT, exist_ok=True)
    pts = pd.read_csv(os.path.join(ROOT, 'data', 'raw', 'tessera_test', 'points.csv'))
    t0 = time.time()
    with ThreadPoolExecutor(a.workers) as ex:
        res = list(ex.map(lambda i: chunk(pts.iloc[i:i + CHUNK], a.year), range(0, len(pts), CHUNK)))
    d = pd.concat(res, ignore_index=True)
    d.to_csv(os.path.join(OUT, f'inputs_{a.year}.csv'), index=False)
    s2cols = [c for c in d.columns if c.startswith('B4_m')]
    print(f'{len(d):,} parcels, {d.shape[1] - 1} columns, {(time.time() - t0) / 60:.1f} min; '
          f'months with S2 per parcel (median): {d[s2cols].notna().sum(axis=1).median():.0f} of 12', flush=True)


if __name__ == '__main__':
    main()
