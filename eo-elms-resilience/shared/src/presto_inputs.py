"""National Presto inputs at the WP3 detection parcels (W3-4 addendum, 18 October 2026). Farm season S = October of
S-1 to September of S (12 monthly steps, month index 1 = October). Same bands and masking as presto_inputs_test.py:
S1 VV, VH (mean); S2 B2-B12 (median, Cloud Score+ >= 0.6); ERA5-Land temperature_2m, total_precipitation_sum;
SRTM elevation, slope; 15 m buffer mean at the parcel point. One file per 50 km square and season (resumable).

Input   shared/data/parcels/wp3_detection_parcels.parquet
Output  shared/data/presto/inputs/i_<square>_<season>.parquet
Usage   python presto_inputs.py --project ee-natusjatkachenko03 [--seasons 2025 2019 2018 2020]
"""
import argparse, os, time
from concurrent.futures import ThreadPoolExecutor
import pandas as pd, ee
import presto_inputs_test as t

ROOT = t.ROOT
OUT = os.path.join(ROOT, 'shared', 'data', 'presto', 'inputs')
CHUNK = 500


def stack(season, region):
    """12 months October(season-1) .. September(season); band names <band>_m01 (October) .. _m12 (September)."""
    S2B = t.S2B
    start = ee.Date.fromYMD(season - 1, 10, 1)
    cs = ee.ImageCollection('GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED')
    s2 = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED').filterBounds(region).filterDate(start, start.advance(12, 'month'))
          .linkCollection(cs, ['cs_cdf']).map(lambda i: i.select(S2B).updateMask(i.select('cs_cdf').gte(0.6)).copyProperties(i, ['system:time_start'])))
    s1 = (ee.ImageCollection('COPERNICUS/S1_GRD').filterBounds(region).filterDate(start, start.advance(12, 'month'))
          .filter(ee.Filter.eq('instrumentMode', 'IW'))
          .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
          .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH')).select(['VV', 'VH']))
    era = ee.ImageCollection('ECMWF/ERA5_LAND/MONTHLY_AGGR').select(['temperature_2m', 'total_precipitation_sum'])
    bands = []
    for m in range(12):
        a = start.advance(m, 'month'); b = a.advance(1, 'month')
        e1 = ee.Image.constant([0, 0]).rename(['VV', 'VH']).updateMask(0)
        e2 = ee.Image.constant([0] * len(S2B)).rename(S2B).updateMask(0)
        c1, c2 = s1.filterDate(a, b), s2.filterDate(a, b)
        i1 = ee.Image(ee.Algorithms.If(c1.size().gt(0), c1.mean(), e1))
        i2 = ee.Image(ee.Algorithms.If(c2.size().gt(0), c2.median(), e2))
        i3 = era.filterDate(a, b).first()
        bands.append(ee.Image.cat(i1, i2, i3).rename([f'{x}_m{m + 1:02d}' for x in ['VV', 'VH'] + S2B + ['temperature_2m', 'total_precipitation']]))
    dem = ee.Image('USGS/SRTMGL1_003')
    return ee.Image.cat(bands + [dem.rename('elevation'), ee.Terrain.slope(dem).rename('slope')])


def chunk(pts, season, tries=10):
    msg = ''
    for k in range(tries):
        try:
            fc = ee.FeatureCollection([ee.Feature(ee.Geometry.Point([float(a), float(b)]).buffer(15), {'parcref': p})
                                       for p, a, b in zip(pts.parcref, pts.lon, pts.lat)])
            rows = stack(season, fc.geometry().bounds()).reduceRegions(collection=fc, reducer=ee.Reducer.mean(), scale=10, tileScale=4).getInfo()['features']
            return pd.DataFrame([r['properties'] for r in rows])
        except Exception as e:
            msg = str(e); time.sleep(min(30 * (k + 1), 180))
    raise RuntimeError(msg[:150])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--project', required=True)
    ap.add_argument('--seasons', nargs='*', type=int, default=[2025, 2019, 2018, 2020]); ap.add_argument('--workers', type=int, default=6)
    a = ap.parse_args()
    for k in range(20):
        try:
            ee.Initialize(project=a.project); break
        except Exception:
            time.sleep(30)
    os.makedirs(OUT, exist_ok=True)
    p = pd.read_parquet(os.path.join(ROOT, 'shared', 'data', 'parcels', 'wp3_detection_parcels.parquet'))
    jobs = [(s, sq) for s in a.seasons for sq in sorted(p.sq.unique())]
    t0 = time.time()
    with ThreadPoolExecutor(a.workers) as ex:
        for n, (s, sq) in enumerate(jobs, 1):
            dst = os.path.join(OUT, f'i_{sq}_{s}.parquet')
            if os.path.exists(dst):
                continue
            sub = p[p.sq == sq].reset_index(drop=True)
            try:
                d = pd.concat(list(ex.map(lambda i: chunk(sub.iloc[i:i + CHUNK], s), range(0, len(sub), CHUNK))), ignore_index=True)
            except Exception as e:
                print(f'  {sq} {s}: failed ({str(e)[:100]})', flush=True); continue
            d.to_parquet(dst + '.tmp', index=False); os.replace(dst + '.tmp', dst)
            print(f'  {n}/{len(jobs)} {sq} season {s}: {len(d):,} parcels ({(time.time() - t0) / 60:.0f} min)', flush=True)


if __name__ == '__main__':
    main()
