"""Sentinel-2 L2A crop-stress indices at cereal parcels, from Microsoft Planetary Computer (no login needed).

For each Sentinel-2 tile x year, every scene from March to August is checked against its scene-classification layer
(SCL) at the parcel points; scenes where too few parcels are clear are skipped before any reflectance is downloaded.
For the rest, five bands are read and three indices computed at each clear parcel point:
  NDVI = (B08 - B04) / (B08 + B04)      greenness / canopy            (10 m, mean of the 3 x 3 pixels around the point)
  NDRE = (B8A - B05) / (B8A + B05)      red-edge: chlorophyll, N stress (20 m, pixel at the point)
  NDMI = (B8A - B11) / (B8A + B11)      canopy water: drought stress    (20 m, pixel at the point)
Clear = SCL class 4 (vegetation) or 5 (bare soil). Reflectance offset: scenes from processing baseline 04.00 on carry
a +1000 offset, removed here.

Parcels: cereal land (cereal in >= half of CROME 2016-2025) from parcels/parcel_panel.parquet; points are RPA parcel
points (inside the parcel). Output, one file per tile-year (re-runs skip finished ones):
  shared/data/s2/parcels/<tile>/<year>.parquet   parcref, date, ndvi, ndre, ndmi, scl
Usage: python extract_s2_parcels.py --tiles 30UXD --years 2022
"""
import argparse, os, time
import numpy as np, pandas as pd
import planetary_computer as pc, pystac_client, rasterio
from pyproj import Transformer
from rasterio.windows import Window

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
D = os.path.join(ROOT, 'shared', 'data')
OUT = os.path.join(D, 's2', 'parcels')
STAC = 'https://planetarycomputer.microsoft.com/api/stac/v1'
MIN_CLEAR = 0.15          # skip a scene if fewer than this share of the tile's parcels are clear
TILE_M = 109_800          # Sentinel-2 tile size (m)
os.environ.setdefault('GDAL_DISABLE_READDIR_ON_OPEN', 'EMPTY_DIR')
os.environ.setdefault('GDAL_HTTP_MULTIRANGE', 'YES')
os.environ.setdefault('GDAL_HTTP_MERGE_CONSECUTIVE_RANGES', 'YES')


def parcels():
    t = pd.read_parquet(os.path.join(D, 'parcels', 'parcel_panel.parquet'), columns=['parcref', 'x', 'y', 'cereal_land'])
    return t[t.cereal_land].drop(columns='cereal_land').reset_index(drop=True)


def read_at(href, rows, cols, size=1, offset=0.0):
    """Read the band once (whole tile, one request stream) and return values at pixel (row, col); size 3 = 3x3 mean."""
    with rasterio.open(href) as src:
        a = src.read(1).astype('float32')
    a = a - offset
    if size == 1:
        return a[rows, cols]
    pad = np.pad(a, 1, mode='edge')
    acc = sum(pad[rows + 1 + dr, cols + 1 + dc] for dr in (-1, 0, 1) for dc in (-1, 0, 1))
    return acc / 9.0


def run_tile_year(cat, tile, year, pts):
    dst = os.path.join(OUT, tile, f'{year}.parquet')
    if os.path.exists(dst):
        print(f'{tile} {year}: done already', flush=True); return
    items = list(cat.search(collections=['sentinel-2-l2a'], query={'s2:mgrs_tile': {'eq': tile}, 'eo:cloud_cover': {'lt': 80}},
                            datetime=f'{year}-03-01/{year}-08-31').items())
    if not items:
        print(f'{tile} {year}: no scenes', flush=True); return
    epsg = int(str(items[0].properties.get('proj:epsg') or items[0].properties['proj:code']).split(':')[-1])
    with rasterio.open(items[0].assets['SCL'].href) as s:
        x0, y1 = s.transform.c, s.transform.f
    tx, ty = Transformer.from_crs(27700, epsg, always_xy=True).transform(pts.x.values, pts.y.values)
    inside = (tx > x0 + 15) & (tx < x0 + TILE_M - 15) & (ty < y1 - 15) & (ty > y1 - TILE_M + 15)
    p = pts[inside].reset_index(drop=True); tx, ty = tx[inside], ty[inside]
    r10, c10 = ((y1 - ty) // 10).astype(int), ((tx - x0) // 10).astype(int)
    r20, c20 = ((y1 - ty) // 20).astype(int), ((tx - x0) // 20).astype(int)
    print(f'{tile} {year}: {len(items)} scenes, {len(p):,} cereal parcels in tile', flush=True)
    out, t0, used = [], time.time(), 0
    for it in sorted(items, key=lambda i: i.datetime):
        try:
            scl = read_at(it.assets['SCL'].href, r20, c20)
            clear = np.isin(scl, (4, 5))
            if clear.mean() < MIN_CLEAR:
                continue
            off = 1000.0 if str(it.properties.get('s2:processing_baseline', '0')) >= '04.00' else 0.0
            b = {k: read_at(it.assets[k].href, r20, c20, offset=off)[clear] for k in ('B05', 'B8A', 'B11')}
            for k in ('B04', 'B08'):
                b[k] = read_at(it.assets[k].href, r10, c10, size=3, offset=off)[clear]
            nd = lambda a, c: np.clip((a - c) / np.maximum(a + c, 1e-6), -1, 1).astype('float32')
            out.append(pd.DataFrame({'parcref': p.parcref.values[clear], 'date': pd.Timestamp(it.datetime.date()),
                                     'ndvi': nd(b['B08'], b['B04']), 'ndre': nd(b['B8A'], b['B05']),
                                     'ndmi': nd(b['B8A'], b['B11']), 'scl': scl[clear].astype('int8')}))
            used += 1
        except Exception as e:                       # one bad scene must not stop the tile
            print(f'  {it.id}: skipped ({type(e).__name__})', flush=True)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    res = pd.concat(out, ignore_index=True) if out else pd.DataFrame(columns=['parcref', 'date', 'ndvi', 'ndre', 'ndmi', 'scl'])
    res.to_parquet(dst, index=False)
    print(f'{tile} {year}: {used} clear scenes of {len(items)}, {len(res):,} observations, '
          f'{(time.time() - t0) / 60:.1f} min -> {os.path.relpath(dst, ROOT)}', flush=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--tiles', nargs='+', required=True)
    ap.add_argument('--years', nargs='+', type=int, required=True)
    a = ap.parse_args()
    cat = pystac_client.Client.open(STAC, modifier=pc.sign_inplace)
    pts = parcels()
    for tile in a.tiles:
        for year in a.years:
            run_tile_year(cat, tile, year, pts)
