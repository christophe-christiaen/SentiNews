"""Sentinel-1 test: is winter waterlogging visible at cereal parcels? (Planetary Computer, no Earth Engine)

Area: cereal parcels of the Sentinel-2 test tile (30UXD, Lincolnshire / Leicestershire). Winters (October-March):
2019-20 and 2023-24 (very wet), 2021-22 (drier). Every Sentinel-1 RTC pass (terrain-corrected gamma0) is read at the
40 m overview over the tile; at each parcel point VV and VH backscatter (dB) are taken.
'Water-like' = VV < WATER_DB (smooth open water / saturated bare soil reflects the radar away from the satellite).
A good waterlogging signal should be more frequent in the wet winters and in Flood Zone 3. Saturated (not flooded) soil
raises backscatter instead, so the median VV per winter is reported as well.

Output  shared/data/s1/s1_test_30UXD.parquet          parcref, date, orbit, vv_db, vh_db
        shared/results/s1_waterlogging_test.md        counts only (no scheme-group comparisons)
"""
import os, time
import numpy as np, pandas as pd
import planetary_computer as pc, pystac_client, rasterio
from rasterio.windows import from_bounds
from pyproj import Transformer

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
D = os.path.join(ROOT, 'shared', 'data')
SUMMARY = os.path.join(ROOT, 'shared', 'results', 's1_waterlogging_test.md')
WINTERS = {'2019-20 (wet)': ('2019-10-01', '2020-03-31'), '2021-22 (drier)': ('2021-10-01', '2022-03-31'),
           '2023-24 (wet)': ('2023-10-01', '2024-03-31')}
WATER_DB = -17.0
OVERVIEW = 1          # 0 = 20 m, 1 = 40 m


def parcels():
    t = pd.read_parquet(os.path.join(D, 's2', 'parcels', '30UXD', '2022.parquet'), columns=['parcref']).drop_duplicates()
    p = pd.read_parquet(os.path.join(D, 'parcels', 'parcel_panel.parquet'), columns=['parcref', 'x', 'y'])
    r = pd.read_parquet(os.path.join(D, 'parcels', 'parcel_risk.parquet'), columns=['parcref', 'flood_zone'])
    return t.merge(p, on='parcref').merge(r, on='parcref')


def sample(href, xs, ys, epsg_cache={}):
    with rasterio.open(href, overview_level=OVERVIEW) as src:
        key = src.crs.to_wkt()                       # RTC files carry WKT without an EPSG code
        if key not in epsg_cache:
            epsg_cache[key] = Transformer.from_crs('EPSG:27700', src.crs.to_wkt(), always_xy=True)
        tx, ty = epsg_cache[key].transform(xs, ys)
        win = from_bounds(tx.min() - 100, ty.min() - 100, tx.max() + 100, ty.max() + 100, src.transform).round_offsets().round_lengths()
        a = src.read(1, window=win, boundless=True, fill_value=np.nan)
        wt = src.window_transform(win)
        r, c = rasterio.transform.rowcol(wt, tx, ty)
        r, c = np.asarray(r), np.asarray(c)
        ok = (r >= 0) & (r < a.shape[0]) & (c >= 0) & (c < a.shape[1])
        v = np.full(len(xs), np.nan, dtype='float32'); v[ok] = a[r[ok], c[ok]]
    v[(v <= 0) | ~np.isfinite(v)] = np.nan
    return 10 * np.log10(v)


def main():
    cat = pystac_client.Client.open('https://planetarycomputer.microsoft.com/api/stac/v1', modifier=pc.sign_inplace)
    p = parcels()
    lon, lat = Transformer.from_crs(27700, 4326, always_xy=True).transform(p.x.values, p.y.values)
    bbox = [float(lon.min()), float(lat.min()), float(lon.max()), float(lat.max())]
    out = []
    for w, (a, b) in WINTERS.items():
        items = list(cat.search(collections=['sentinel-1-rtc'], bbox=bbox, datetime=f'{a}/{b}').items())
        print(f'{w}: {len(items)} passes', flush=True); t0 = time.time()
        for it in sorted(items, key=lambda i: i.datetime):
            try:
                vv = sample(it.assets['vv'].href, p.x.values, p.y.values)
                vh = sample(it.assets['vh'].href, p.x.values, p.y.values)
            except Exception as e:
                print(f'  {it.id}: skipped ({type(e).__name__})', flush=True); continue
            ok = np.isfinite(vv)
            out.append(pd.DataFrame({'parcref': p.parcref.values[ok], 'winter': w, 'date': pd.Timestamp(it.datetime.date()),
                                     'orbit': it.properties.get('sat:relative_orbit'), 'vv_db': vv[ok], 'vh_db': vh[ok]}))
        print(f'  {w}: done in {(time.time() - t0) / 60:.1f} min', flush=True)
    s = pd.concat(out, ignore_index=True)
    os.makedirs(os.path.join(D, 's1'), exist_ok=True)
    s.to_parquet(os.path.join(D, 's1', 's1_test_30UXD.parquet'), index=False)
    summarise(s, p)


def summarise(s, p):
    s['water'] = s.vv_db < WATER_DB
    s = s.merge(p[['parcref', 'flood_zone']], on='parcref', how='left')
    s['fz3'] = s.flood_zone.eq(3).fillna(False)
    per = s.groupby(['winter', 'parcref', 'fz3']).water.mean().reset_index()       # share of passes water-like
    med = s.groupby(['winter', 'parcref', 'fz3']).vv_db.median().reset_index()
    per = per.merge(med, on=['winter', 'parcref', 'fz3'])
    tab = per.groupby(['winter', 'fz3']).agg(water_share=('water', 'mean'), water_20=('water', lambda x: (x >= 0.2).mean()),
                                             vv_median_db=('vv_db', 'median'), parcels=('water', 'size')).round(3)
    tab.columns = ['mean share of passes water-like', 'parcels water-like in >=20% of passes', 'median VV (dB)', 'parcels']
    monthly = s.assign(m=s.date.dt.to_period('M').astype(str)).groupby(['winter', 'm']).water.mean().round(3)
    lines = ['# Sentinel-1 waterlogging test, tile 30UXD (counts only)', '',
             f'- Cereal parcels: {p.parcref.nunique():,}; passes read: {s.date.nunique()} dates; observations: {len(s):,}',
             f'- Water-like = VV backscatter below {WATER_DB} dB (40 m overview of Sentinel-1 RTC gamma0)', '',
             '## By winter and flood zone', '', tab.reset_index().assign(fz3=lambda d: d.fz3.map({True: 'Flood Zone 3', False: 'other'})).to_markdown(index=False), '',
             '## Share of parcel observations water-like, by month', '', monthly.reset_index().to_markdown(index=False)]
    open(SUMMARY, 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    import sys
    if '--summary' in sys.argv:                  # rebuild the summary from the saved passes
        summarise(pd.read_parquet(os.path.join(D, 's1', 's1_test_30UXD.parquet')), parcels())
    else:
        main()
