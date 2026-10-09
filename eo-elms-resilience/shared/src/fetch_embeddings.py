"""Fetch geospatial embeddings for pilot windows and sample them at scheme locations.

Backends
  alphaearth  AlphaEarth Foundations annual embeddings (Google DeepMind; CC BY 4.0), 64-d, 10 m, 2017-2025,
              read directly from the public Source Cooperative S3 bucket (no credentials).
  tessera     TESSERA v1.1 annual embeddings (Cambridge; CC0), 128-d, 10 m, from the Zarr store on Source Cooperative
              via geotessera >= 0.11 (Python >= 3.12; pip install git+https://github.com/ucam-eo/geotessera).
  earthengine AlphaEarth via Google Earth Engine (server-side sampling; needs `earthengine authenticate`).
              Recommended for national scale: only the sampled values are downloaded.

For each site-year the AlphaEarth backend reads the 6 x 6 km window once and writes:
  shared/data/embeddings/<backend>/window_means.csv     mean embedding per site-year (WP1/WP2 context)
  shared/data/embeddings/<backend>/samples_<year>.parquet  embeddings at scheme points + random controls (WP3)
  shared/data/embeddings/<backend>/rasters/...           optional int8 GeoTIFF of the window (--save-rasters)

Notes on the AlphaEarth files: band-interleaved COGs in 1024 x 1024 blocks, stored bottom-up (rows run north), int8
with -128 = no data. De-quantise with ((v / 127.5) ** 2) * sign(v). A 10 m window costs up to 256 block requests
(~100 MB); --overview 1 reads the 20 m overview (~4x less), 2 = 40 m. Attribution: "The AlphaEarth Foundations
Satellite Embedding dataset is produced by Google and Google DeepMind."
"""
import argparse, json, os, sys, time
from concurrent.futures import ThreadPoolExecutor
import numpy as np, pandas as pd
import rasterio
from rasterio.windows import Window
from pyproj import Transformer

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'src'))
from sites import SITES, KM  # noqa: E402

OUT = os.path.join(ROOT, 'shared', 'data', 'embeddings')
SCHEMES = os.path.join(ROOT, 'shared', 'data', 'schemes', 'pilot')
AEF_INDEX_URL = 'https://data.source.coop/tge-labs/aef/v1/annual/aef_index.parquet'
AEF_HTTP = 'https://s3.us-west-2.amazonaws.com/us-west-2.opendata.source.coop/'   # faster than the data.source.coop proxy
POINT_LAYERS = dict(cs_options='OPTION_CODE', es_options='OPTCODE', sfi_actions='option_code')
GDAL_ENV = dict(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR', CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tiff',
                GDAL_HTTP_MULTIRANGE='YES', GDAL_HTTP_MERGE_CONSECUTIVE_RANGES='YES', GDAL_HTTP_MAX_RETRY='5',
                GDAL_HTTP_RETRY_DELAY='2', VSI_CACHE='TRUE')
to_bng = Transformer.from_crs(4326, 27700, always_xy=True)


def dequantise(a):
    v = a.astype(np.float32)
    e = ((v / 127.5) ** 2) * np.sign(v)
    e[:, a[0] == -128] = np.nan
    return e


def site_window_bng(lat, lon):
    x, y = to_bng.transform(lon, lat)
    return x, y, (x - KM * 1000, y - KM * 1000, x + KM * 1000, y + KM * 1000)


def scheme_points(region, site):
    """Option/action points inside a pilot window (from fetch_schemes.py --pilot), in EPSG:27700."""
    rows = []
    for layer, code in POINT_LAYERS.items():
        fn = os.path.join(SCHEMES, f'{layer}.geojson')
        if not os.path.exists(fn):
            continue
        for f in json.load(open(fn))['features']:
            p = f['properties']
            if p.get('region') == region and p.get('site') == site and f.get('geometry'):
                x, y = f['geometry']['coordinates'][:2]
                rows.append(dict(source=layer, code=p.get(code), x=x, y=y,
                                 start=p.get('STARTDATE') or p.get('STARTDAT') or p.get('contract_start')))
    df = pd.DataFrame(rows)
    if not df.empty:
        df['start_year'] = start_year(df.pop('start'))
    return df


def start_year(s):
    """Scheme start dates come as 'YYYYMMDD' (CS), epoch ms (ES) or ISO strings (SFI); return the year."""
    s = s.astype(str)
    num = pd.to_numeric(s, errors='coerce')
    ms = pd.to_datetime(num.where(num > 1e11), unit='ms', errors='coerce')
    ymd = pd.to_datetime(s.where(s.str.fullmatch(r'\d{8}')), format='%Y%m%d', errors='coerce')
    iso = pd.to_datetime(s.where(s.str.contains('-')), errors='coerce', utc=True).dt.tz_localize(None)
    return ms.fillna(ymd).fillna(iso).dt.year.astype('Int64')


class AlphaEarth:
    def __init__(self, overview=0):
        fn = os.path.join(OUT, 'aef_index.parquet')
        if not os.path.exists(fn):
            os.makedirs(OUT, exist_ok=True)
            import urllib.request; urllib.request.urlretrieve(AEF_INDEX_URL, fn)
        cols = ['path', 'year', 'crs', 'wgs84_west', 'wgs84_south', 'wgs84_east', 'wgs84_north']
        self.idx = pd.read_parquet(fn, columns=cols)
        self.idx = self.idx[(self.idx.wgs84_east > -9) & (self.idx.wgs84_west < 3) & (self.idx.wgs84_north > 49) & (self.idx.wgs84_south < 61)]
        self.overview = overview

    def files_for(self, lat, lon, year, pad=0.06):
        """Files overlapping the window (~0.06 degrees covers 6 km plus margin), the one holding the centre first."""
        i = self.idx
        f = i[(i.year == year) & (i.wgs84_west <= lon + pad) & (i.wgs84_east >= lon - pad) &
              (i.wgs84_south <= lat + pad) & (i.wgs84_north >= lat - pad)].copy()
        f['centre'] = (f.wgs84_west <= lon) & (f.wgs84_east >= lon) & (f.wgs84_south <= lat) & (f.wgs84_north >= lat)
        return f.sort_values('centre', ascending=False)

    def read_window(self, lat, lon, year):
        """List of pieces (embeddings float32 [64, H, W] north-up, grid dict, crs), one per file overlapping the window."""
        f = self.files_for(lat, lon, year)
        pieces = [p for p in (self._read_piece(row, lat, lon) for _, row in f.iterrows()) if p is not None]
        return pieces or None

    def _read_piece(self, row, lat, lon):
        url = '/vsicurl/' + AEF_HTTP + row.path.split('s3://us-west-2.opendata.source.coop/')[-1]
        kw = {'overview_level': self.overview - 1} if self.overview > 0 else {}
        with rasterio.Env(**GDAL_ENV), rasterio.open(url, **kw) as src:
            T = src.transform
            tr = Transformer.from_crs(4326, src.crs, always_xy=True); cx, cy = tr.transform(lon, lat)
            half = KM * 1000 * 1.1   # 10% margin: the UTM square must cover the (slightly rotated) BNG window
            c0 = int(np.floor((cx - half - T.c) / T.a)); r0 = int(np.floor((cy - half - T.f) / T.e))  # bottom-up: T.e > 0
            n = int(round(2 * half / T.a))
            c1, r1 = min(c0 + n, src.width), min(r0 + n, src.height)
            c0, r0 = max(c0, 0), max(r0, 0); w, h = c1 - c0, r1 - r0
            if w <= 0 or h <= 0:
                return None
            a = src.read(window=Window(c0, r0, w, h))[:, ::-1, :]                  # flip to north-up
            geo = dict(x0=T.c + c0 * T.a, y_top=T.f + (r0 + h) * T.e, res=T.a)    # north-up grid origin
            return dequantise(a), geo, src.crs

    @staticmethod
    def sample(emb, geo, crs, pts_bng):
        """Embedding vectors at BNG points (nearest pixel); NaN rows for points outside the window."""
        if len(pts_bng) == 0:
            return np.empty((0, emb.shape[0]), np.float32)
        tr = Transformer.from_crs(27700, crs, always_xy=True)
        xs, ys = tr.transform(pts_bng[:, 0], pts_bng[:, 1])
        cols = np.floor((np.asarray(xs) - geo['x0']) / geo['res']).astype(int)
        rows = np.floor((geo['y_top'] - np.asarray(ys)) / geo['res']).astype(int)
        ok = (rows >= 0) & (rows < emb.shape[1]) & (cols >= 0) & (cols < emb.shape[2])
        out = np.full((len(xs), emb.shape[0]), np.nan, np.float32)
        out[ok] = emb[:, rows[ok], cols[ok]].T
        return out


def run_alphaearth(sites, years, overview, workers, n_controls, save_rasters):
    ae = AlphaEarth(overview)
    d = os.path.join(OUT, 'alphaearth' + (f'_ov{overview}' if overview else '')); os.makedirs(d, exist_ok=True)
    rng = np.random.default_rng(0)
    means, samples = [], {y: [] for y in years}

    def job(task):
        region, site, year = task
        lat, lon = SITES[region][site]
        t = time.time()
        pieces = ae.read_window(lat, lon, year)
        if pieces is None:
            return task, None, None, time.time() - t
        x, y, (x0, y0, x1, y1) = site_window_bng(lat, lon)
        pts = scheme_points(region, site)
        ctrl = pd.DataFrame(dict(source='control', code=None, start_year=pd.array([pd.NA] * n_controls, dtype='Int64'),
                                 x=rng.uniform(x0, x1, n_controls), y=rng.uniform(y0, y1, n_controls)))
        pts = pd.concat([pts, ctrl], ignore_index=True)
        vec = None
        for emb, geo, crs in pieces:   # first piece with a valid value wins
            v = AlphaEarth.sample(emb, geo, crs, pts[['x', 'y']].to_numpy())
            vec = v if vec is None else np.where(np.isnan(vec), v, vec)
        tab = pd.concat([pts.assign(region=region, site=site, year=year).reset_index(drop=True),
                         pd.DataFrame(vec.astype(np.float16), columns=[f'A{i:02d}' for i in range(vec.shape[1])])], axis=1)
        tab = tab[~np.isnan(vec).any(axis=1)]
        m = np.nanmean(np.concatenate([e.reshape(e.shape[0], -1) for e, _, _ in pieces], axis=1), axis=1)
        emb, geo, crs = pieces[0]   # raster export writes the main piece only
        if save_rasters:
            from rasterio.transform import from_origin
            q = np.where(np.isnan(emb), -128, np.round(np.sign(emb) * np.sqrt(np.abs(emb)) * 127.5)).astype(np.int8)
            fn = os.path.join(d, 'rasters', f'{region.replace(" ", "_").replace("&", "and")}_{site}_{year}.tif'); os.makedirs(os.path.dirname(fn), exist_ok=True)
            with rasterio.open(fn, 'w', driver='GTiff', height=q.shape[1], width=q.shape[2], count=q.shape[0], dtype='int8',
                               crs=crs, transform=from_origin(geo['x0'], geo['y_top'], geo['res'], geo['res']), nodata=-128,
                               compress='zstd', tiled=True) as dst:
                dst.write(q)
        return task, tab, m, time.time() - t

    done = lambda r, s_, y: os.path.exists(os.path.join(d, 'parts', f'{r.replace(" ", "_").replace("&", "and")}_{s_}_{y}.parquet'))
    tasks = [(r, s_, y) for (r, s_) in sites for y in years if not done(r, s_, y)]
    with ThreadPoolExecutor(workers) as ex:
        for (region, site, year), tab, m, secs in ex.map(job, tasks):
            if tab is None:
                print(f'  no AlphaEarth tile for {region} {site} {year}'); continue
            part = os.path.join(d, 'parts', f'{region.replace(" ", "_").replace("&", "and")}_{site}_{year}.parquet')
            os.makedirs(os.path.dirname(part), exist_ok=True); tab.astype({'code': 'string'}).to_parquet(part, index=False)
            samples[year].append(part)
            means.append(dict(region=region, site=site, year=year, **{f'A{i:02d}': v for i, v in enumerate(m)}))
            print(f'  {region} {site} {year}: {len(tab)} samples ({(tab.source != "control").sum()} scheme points), {secs:.0f}s', flush=True)
    import glob
    for y in years:   # combine all part files for the year (including earlier runs)
        parts = sorted(glob.glob(os.path.join(d, 'parts', f'*_{y}.parquet')))
        if parts:
            pd.concat([pd.read_parquet(p) for p in parts], ignore_index=True).to_parquet(os.path.join(d, f'samples_{y}.parquet'), index=False)
    fn = os.path.join(d, 'window_means.csv')
    old = pd.read_csv(fn) if os.path.exists(fn) else pd.DataFrame()
    new = pd.DataFrame(means)
    if not old.empty:
        old = old.merge(new[['region', 'site', 'year']], how='left', indicator=True).query('_merge == "left_only"').drop(columns='_merge')
    pd.concat([old, new], ignore_index=True).sort_values(['region', 'site', 'year']).to_csv(fn, index=False)
    print(f'wrote {os.path.relpath(d, ROOT)}')


def run_tessera(sites, years, workers=2, n_controls=500):
    """TESSERA v1.1 (dclimate variant) from its Zarr store on Source Cooperative, via geotessera >= 0.11
    (needs Python >= 3.12). Reads each 6 x 6 km window once (only the chunks it needs) and samples the same
    scheme points + random controls as the AlphaEarth backend. Pin one dataset: variants are not comparable."""
    from geotessera import GeoTesseraZarr
    from geotessera.registry import zarr_store_url
    store = zarr_store_url('v1.1')
    gt = GeoTesseraZarr(store, cache_dir=os.path.join(OUT, 'tessera', 'zarr_cache'))
    d = os.path.join(OUT, 'tessera'); os.makedirs(os.path.join(d, 'parts'), exist_ok=True)
    wgs = Transformer.from_crs(27700, 4326, always_xy=True)
    tag = lambda r, s_, y: f'{r.replace(" ", "_").replace("&", "and")}_{s_}_{y}'
    means = []

    def job(task):
        try:
            return _job(task)
        except Exception as e:  # e.g. a year the store does not cover
            print(f'  tessera {task}: failed ({type(e).__name__}: {str(e)[:120]})', flush=True)
            return task, 0, 0, None, 0.0

    def _job(task):
        region, site, year = task
        t = time.time(); lat, lon = SITES[region][site]
        _, _, (x0, y0, x1, y1) = site_window_bng(lat, lon)
        xs, ys = zip(*[wgs.transform(a, b) for a in (x0, x1) for b in (y0, y1)])
        mosaic, T, crs = gt.read_region((min(xs), min(ys), max(xs), max(ys)), year)      # (H, W, 128), north-up UTM
        emb = np.moveaxis(mosaic, -1, 0).astype(np.float32)
        geo = dict(x0=T.c, y_top=T.f, res=T.a)
        rng = np.random.default_rng(site * 10000 + year)
        pts = scheme_points(region, site)
        ctrl = pd.DataFrame(dict(source='control', code=None, start_year=pd.array([pd.NA] * n_controls, dtype='Int64'),
                                 x=rng.uniform(x0, x1, n_controls), y=rng.uniform(y0, y1, n_controls)))
        pts = pd.concat([pts, ctrl], ignore_index=True)
        vec = None
        for emb, geo, crs in pieces:   # first piece with a valid value wins
            v = AlphaEarth.sample(emb, geo, crs, pts[['x', 'y']].to_numpy())
            vec = v if vec is None else np.where(np.isnan(vec), v, vec)
        tab = pd.concat([pts.assign(region=region, site=site, year=year).reset_index(drop=True),
                         pd.DataFrame(vec.astype(np.float16), columns=[f'T{i:03d}' for i in range(vec.shape[1])])], axis=1)
        tab = tab[~np.isnan(vec).any(axis=1)]
        tab.astype({'code': 'string'}).to_parquet(os.path.join(d, 'parts', tag(region, site, year) + '.parquet'), index=False)
        return task, len(tab), int((tab.source != 'control').sum()), np.nanmean(emb.reshape(emb.shape[0], -1), axis=1), time.time() - t

    tasks = [(r, s_, y) for (r, s_) in sites for y in years if not os.path.exists(os.path.join(d, 'parts', tag(r, s_, y) + '.parquet'))]
    with ThreadPoolExecutor(workers) as ex:
        for (region, site, year), n, ns, m, secs in ex.map(job, tasks):
            if m is None:
                continue
            means.append(dict(region=region, site=site, year=year, **{f'T{i:03d}': v for i, v in enumerate(m)}))
            print(f'  tessera {region} {site} {year}: {n} samples ({ns} scheme points), {secs:.0f}s', flush=True)
    import glob
    for y in years:
        parts = sorted(glob.glob(os.path.join(d, 'parts', f'*_{y}.parquet')))
        if parts:
            pd.concat([pd.read_parquet(p) for p in parts], ignore_index=True).to_parquet(os.path.join(d, f'samples_{y}.parquet'), index=False)
    if means:
        fn = os.path.join(d, 'window_means.csv'); new = pd.DataFrame(means)
        old = pd.read_csv(fn) if os.path.exists(fn) else pd.DataFrame(columns=new.columns)
        pd.concat([old, new]).drop_duplicates(['region', 'site', 'year'], keep='last').sort_values(['region', 'site', 'year']).to_csv(fn, index=False)
    print(f'wrote {os.path.relpath(d, ROOT)} (dataset: {store})')


def run_earthengine(sites, years, project):
    """AlphaEarth via Earth Engine: sample scheme points server-side (needs an authenticated EE project)."""
    import ee
    ee.Initialize(project=project)
    col = ee.ImageCollection('GOOGLE/SATELLITE_EMBEDDING/V1/ANNUAL')
    wgs = Transformer.from_crs(27700, 4326, always_xy=True)
    d = os.path.join(OUT, 'alphaearth_ee'); os.makedirs(d, exist_ok=True)
    for year in years:
        img = col.filterDate(f'{year}-01-01', f'{year + 1}-01-01').mosaic()
        rows = []
        for region, site in sites:
            pts = scheme_points(region, site)
            lo, la = wgs.transform(pts.x.to_numpy(), pts.y.to_numpy())
            fc = ee.FeatureCollection([ee.Feature(ee.Geometry.Point([float(a), float(b)]), {'i': int(k)}) for k, (a, b) in enumerate(zip(lo, la))])
            got = img.sampleRegions(collection=fc, scale=10, geometries=False).getInfo()['features']
            for g in got:
                r = pts.iloc[g['properties'].pop('i')].to_dict(); r.update(region=region, site=site, year=year, **g['properties']); rows.append(r)
        pd.DataFrame(rows).to_parquet(os.path.join(d, f'samples_{year}.parquet'), index=False)


def pick_sites(arg):
    if arg == 'all':
        return [(r, i) for r, pts in SITES.items() for i in range(len(pts))]
    if arg.startswith('top'):
        inv = pd.read_csv(os.path.join(SCHEMES, 'site_inventory.csv'))
        return list(inv.head(int(arg[3:]))[['region', 'site']].itertuples(index=False, name=None))
    return [(r.split(':')[0], int(r.split(':')[1])) for r in arg.split(',')]   # "South West:4,North East:3"


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--backend', choices=['alphaearth', 'tessera', 'earthengine'], default='alphaearth')
    ap.add_argument('--sites', default='top6', help='"all", "topN" (most scheme points) or "Region:site,..."')
    ap.add_argument('--years', default='2020,2025', help='comma list, e.g. 2017,2018,...,2025')
    ap.add_argument('--overview', type=int, default=0, help='AlphaEarth: 0 = 10 m, 1 = 20 m, 2 = 40 m')
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--controls', type=int, default=500, help='random control pixels per window')
    ap.add_argument('--save-rasters', action='store_true')
    ap.add_argument('--ee-project', default=None)
    a = ap.parse_args()
    sites, years = pick_sites(a.sites), [int(y) for y in a.years.split(',')]
    print(f'{a.backend}: {len(sites)} sites x {len(years)} years')
    if a.backend == 'alphaearth':
        run_alphaearth(sites, years, a.overview, a.workers, a.controls, a.save_rasters)
    elif a.backend == 'tessera':
        run_tessera(sites, years, a.workers, a.controls)
    else:
        run_earthengine(sites, years, a.ee_project)
