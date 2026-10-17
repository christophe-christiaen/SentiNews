"""U1 weather (wp2_resilience/results/u1_grassland_protocol.md): ERA5-Land for the grassland sample's cells that the
cereal run did not cover, and the grassland parcel -> cell map. Same variables and processing as fetch_era5land.py;
cereal files are not changed.

Output  shared/data/weather/era5land_monthly_grass.parquet, era5land_heatdays_grass.parquet (new cells only)
        shared/data/weather/grass_era5_cell.parquet (parcref, cell_id, cell_id_data)
        shared/data/weather/cell_year_shocks_grass.parquet (shocks for every grassland cell, same definitions)
Usage   python fetch_era5land_grass.py --project ee-natusjatkachenko03
"""
import argparse, os
import numpy as np, pandas as pd, ee
from pyproj import Transformer
import fetch_era5land as f
import build_s2_panel as b

W = f.OUT


def grass_cells():
    g = pd.read_parquet(os.path.join(f.D, 'parcels', 'grass_sample.parquet'))
    lon, lat = Transformer.from_crs(27700, 4326, always_xy=True).transform(g.x.values, g.y.values)
    ci, cj = np.round(lon / 0.1).astype(int), np.round(lat / 0.1).astype(int)
    return g.assign(cell_id=[f'{i}_{j}' for i, j in zip(ci, cj)], clon=ci * 0.1, clat=cj * 0.1)


def main(project):
    ee.Initialize(project=project)
    g = grass_cells()
    have = set(pd.read_parquet(os.path.join(W, 'era5land_monthly.parquet'), columns=['cell_id']).cell_id)
    c = g[~g.cell_id.isin(have)].groupby('cell_id').agg(lon=('clon', 'first'), lat=('clat', 'first')).reset_index()
    print(f'{len(c)} new cells for {(~g.cell_id.isin(have)).sum():,} grassland parcels', flush=True)
    fc = ee.FeatureCollection([ee.Feature(ee.Geometry.Point([r.lon, r.lat]), {'cell_id': r.cell_id}) for r in c.itertuples()])
    mon, heat = [], []
    for y in f.YEARS:
        col = ee.ImageCollection('ECMWF/ERA5_LAND/MONTHLY_AGGR').filterDate(f'{y}-01-01', f'{y + 1}-01-01').select(list(f.MONTHLY))
        if col.size().getInfo() == 0:
            continue
        d = f.with_retry(lambda: f.sample(col.toBands(), fc))
        if d.empty:
            continue
        long = d.melt(id_vars='cell_id', var_name='band', value_name='v')
        long['month'] = long.band.str[4:6].astype(int); long['var'] = long.band.str[7:].map(f.MONTHLY)
        w = long.pivot_table(index=['cell_id', 'month'], columns='var', values='v').reset_index(); w['year'] = y
        w['precip_mm'] *= 1000; w['pet_mm'] *= -1000; w['t2m_c'] -= 273.15
        mon.append(w)
        daily = ee.ImageCollection('ECMWF/ERA5_LAND/DAILY_AGGR').filterDate(f'{y}-06-01', f'{y}-09-01').select('temperature_2m_max')
        hd = ee.Image.cat(daily.map(lambda i: i.gte(301.15)).sum().rename('hot_days_28'), daily.map(lambda i: i.gte(303.15)).sum().rename('hot_days_30'))
        h = f.with_retry(lambda: f.sample(hd, fc)); h['year'] = y; heat.append(h)
        print(f'  {y}: {len(w):,} cell-months', flush=True)
    mon, heat = pd.concat(mon, ignore_index=True), pd.concat(heat, ignore_index=True)
    mon.to_parquet(os.path.join(W, 'era5land_monthly_grass.parquet'), index=False)
    heat.to_parquet(os.path.join(W, 'era5land_heatdays_grass.parquet'), index=False)
    # cells ERA5-Land masks as sea borrow the nearest cell with data (as for cereals)
    from scipy.spatial import cKDTree
    valid = sorted(have | set(mon.cell_id)); xy = lambda ids: np.array([[int(a) for a in s.split('_')] for s in ids])
    miss = sorted(set(g.cell_id) - set(valid)); rep = {}
    if miss:
        _, i = cKDTree(xy(valid)).query(xy(miss)); rep = dict(zip(miss, [valid[k] for k in i]))
    g['cell_id_data'] = g.cell_id.map(lambda s: rep.get(s, s))
    g[['parcref', 'cell_id', 'cell_id_data']].to_parquet(os.path.join(W, 'grass_era5_cell.parquet'), index=False)
    m = pd.concat([pd.read_parquet(os.path.join(W, 'era5land_monthly.parquet')), mon], ignore_index=True)
    h = pd.concat([pd.read_parquet(os.path.join(W, 'era5land_heatdays.parquet')), heat], ignore_index=True)
    s = b.shocks(m, h, os.path.join(W, 'cell_year_shocks_grass.parquet'))
    s = s[s.cell_id.isin(set(g.cell_id_data))]; s.to_parquet(os.path.join(W, 'cell_year_shocks_grass.parquet'), index=False)
    print(f'{len(miss)} sea-masked cells borrow a neighbour; shocks for {s.cell_id.nunique()} grassland cells', flush=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--project', required=True)
    main(ap.parse_args().project)
