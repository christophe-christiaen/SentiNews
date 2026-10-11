"""ERA5-Land weather at the cells containing cereal parcels, via Earth Engine (shock exposure, independent of crops).

ERA5-Land is on a 0.1 degree grid (~9 km), so parcels are mapped to their grid cell and each cell's series is fetched
once. Monthly values 1991-2025 (1991-2020 gives the climate normal for anomalies), plus summer heat-day counts.

Monthly (ECMWF/ERA5_LAND/MONTHLY_AGGR):
  precip_mm        total precipitation
  t2m_c            mean 2 m air temperature
  pet_mm           potential evaporation (positive = water demand)
  swvl1, swvl2     volumetric soil water, 0-7 cm and 7-28 cm (m3/m3): direct drought / waterlogging signal
Summer (ECMWF/ERA5_LAND/DAILY_AGGR, June-August): hot_days_28, hot_days_30 = days with daily max >= 28 / 30 C

Output  shared/data/weather/era5land_monthly.parquet    cell_id, year, month, variables
        shared/data/weather/era5land_heatdays.parquet   cell_id, year, hot_days_28, hot_days_30
        shared/data/weather/parcel_era5_cell.parquet    parcref -> cell_id (cereal parcels)
Usage   python fetch_era5land.py --project ee-natusjatkachenko03 [--years 2026]   # --years updates only those years
"""
import argparse, os, time
import numpy as np, pandas as pd, ee
from pyproj import Transformer

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
D = os.path.join(ROOT, 'shared', 'data')
OUT = os.path.join(D, 'weather')
YEARS = range(1991, 2027)          # 2026: months available so far (ERA5-Land lags ~1 week)
MONTHLY = {'total_precipitation_sum': 'precip_mm', 'temperature_2m': 't2m_c', 'potential_evaporation_sum': 'pet_mm',
           'volumetric_soil_water_layer_1': 'swvl1', 'volumetric_soil_water_layer_2': 'swvl2'}


def cells():
    t = pd.read_parquet(os.path.join(D, 'parcels', 'parcel_panel.parquet'), columns=['parcref', 'x', 'y', 'cereal_land'])
    t = t[t.cereal_land]
    lon, lat = Transformer.from_crs(27700, 4326, always_xy=True).transform(t.x.values, t.y.values)
    ci, cj = np.round(lon / 0.1).astype(int), np.round(lat / 0.1).astype(int)       # ERA5-Land grid centres at k * 0.1
    t = t.assign(cell_id=[f'{i}_{j}' for i, j in zip(ci, cj)], clon=ci * 0.1, clat=cj * 0.1)
    os.makedirs(OUT, exist_ok=True)
    t[['parcref', 'cell_id']].to_parquet(os.path.join(OUT, 'parcel_era5_cell.parquet'), index=False)
    c = t.groupby('cell_id').agg(lon=('clon', 'first'), lat=('clat', 'first'), parcels=('parcref', 'size')).reset_index()
    return c


def link_coastal(valid):
    """Cells that ERA5-Land masks as sea (coastal parcels) borrow the nearest cell with data: cell_id_data."""
    from scipy.spatial import cKDTree
    f = os.path.join(OUT, 'parcel_era5_cell.parquet'); p = pd.read_parquet(f)
    xy = lambda ids: np.array([[int(a) for a in c.split('_')] for c in ids])
    valid = sorted(valid); miss = sorted(set(p.cell_id) - set(valid))
    rep = {}
    if miss:
        _, i = cKDTree(xy(valid)).query(xy(miss)); rep = dict(zip(miss, [valid[k] for k in i]))
    p['cell_id_data'] = p.cell_id.map(lambda c: rep.get(c, c))
    p.to_parquet(f, index=False)
    print(f'{len(miss)} coastal cells without data; {p.cell_id.isin(miss).sum():,} parcels use the nearest cell', flush=True)


def sample(img, fc, scale=11132):
    rows = img.sampleRegions(collection=fc, scale=scale, geometries=False).getInfo()['features']
    return pd.DataFrame([r['properties'] for r in rows])


def with_retry(f, tries=5):
    for k in range(tries):
        try:
            return f()
        except Exception as e:
            print(f'  retry ({type(e).__name__}: {str(e)[:80]})', flush=True); time.sleep(20 * (k + 1))
    raise RuntimeError('Earth Engine request failed')


def main(project, years=None):
    ee.Initialize(project=project)
    c = cells()
    print(f'{len(c):,} ERA5-Land cells cover the cereal parcels', flush=True)
    fc = ee.FeatureCollection([ee.Feature(ee.Geometry.Point([r.lon, r.lat]), {'cell_id': r.cell_id}) for r in c.itertuples()])
    mon, heat = [], []
    mfile, hfile = os.path.join(OUT, 'era5land_monthly.parquet'), os.path.join(OUT, 'era5land_heatdays.parquet')
    for y in (years or YEARS):
        col = ee.ImageCollection('ECMWF/ERA5_LAND/MONTHLY_AGGR').filterDate(f'{y}-01-01', f'{y + 1}-01-01').select(list(MONTHLY))
        if col.size().getInfo() == 0:
            print(f'  {y}: no data yet', flush=True); continue
        stack = col.toBands()                                   # bands like 202201_total_precipitation_sum
        d = with_retry(lambda: sample(stack, fc))
        long = d.melt(id_vars='cell_id', var_name='band', value_name='v')
        long['month'] = long.band.str[4:6].astype(int)
        long['var'] = long.band.str[7:].map(MONTHLY)
        w = long.pivot_table(index=['cell_id', 'month'], columns='var', values='v').reset_index()
        w['year'] = y
        w['precip_mm'] *= 1000; w['pet_mm'] *= -1000; w['t2m_c'] -= 273.15
        mon.append(w)
        daily = ee.ImageCollection('ECMWF/ERA5_LAND/DAILY_AGGR').filterDate(f'{y}-06-01', f'{y}-09-01').select('temperature_2m_max')
        hd = ee.Image.cat(daily.map(lambda i: i.gte(301.15)).sum().rename('hot_days_28'),
                          daily.map(lambda i: i.gte(303.15)).sum().rename('hot_days_30'))
        h = with_retry(lambda: sample(hd, fc)); h['year'] = y
        heat.append(h)
        print(f'  {y}: {len(w):,} cell-months', flush=True)
    mon, heat = pd.concat(mon, ignore_index=True), pd.concat(heat, ignore_index=True)
    if years and os.path.exists(mfile):           # update: replace only the requested years
        old_m, old_h = pd.read_parquet(mfile), pd.read_parquet(hfile)
        mon = pd.concat([old_m[~old_m.year.isin(years)], mon], ignore_index=True)
        heat = pd.concat([old_h[~old_h.year.isin(years)], heat], ignore_index=True)
    mon.sort_values(['cell_id', 'year', 'month']).to_parquet(mfile, index=False)
    heat.sort_values(['cell_id', 'year']).to_parquet(hfile, index=False)
    link_coastal(set(mon.cell_id))
    print(f'wrote {os.path.relpath(mfile, ROOT)}, {os.path.relpath(hfile, ROOT)}', flush=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--project', required=True)
    ap.add_argument('--years', nargs='*', type=int)
    a = ap.parse_args()
    main(a.project, a.years)
