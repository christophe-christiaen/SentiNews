"""Crop Map of England (CROME, RPA) 2017-2024 -> crop code at every RPA parcel point, one table per year.

CROME classifies a national grid of ~4 ha hexagons each year (LUCODE, e.g. AC66 winter wheat, PG01 grass). Each
parcel gets the crop of the hexagon whose centre is nearest its parcel point (= the containing hexagon on a regular
grid). Downloads are ~1.4-2.8 GB per year from Defra's file server (~0.2 MB/s, no resume), so each year is
downloaded, sampled, and its large files deleted before the next one; finished years are skipped on re-run.

Output  shared/data/parcels/crome/parcel_crop_<year>.parquet   parcref, lucode, cereal flag
        shared/data/reference/crome/CROME_LUCODE_LOOKUP_2024.xlsx
Usage   python fetch_crome.py [--years 2017 2018 ...]
        python fetch_crome.py --gdb path/to/Crop_Map_of_England_CROME_2024.gdb --years 2024   # already downloaded
"""
import argparse, glob, os, shutil, subprocess, time, zipfile
import numpy as np, pandas as pd, pyogrio, requests
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
D = os.path.join(ROOT, 'shared', 'data')
WORK = os.path.join(D, 'reference', 'crome', 'tmp')
OUT = os.path.join(D, 'parcels', 'crome')
PARCELS = os.path.join(D, 'schemes', 'national', 'rpa_parcel_points.csv')
N_PARCELS = 2_686_103
API = 'https://environment.data.gov.uk/backend/catalog/api/file-management/data-sets/{}?isSystemManaged=true'
DL = 'https://environment.data.gov.uk/api/file/download?fileDataSetId={}&fileName={}'
FILESETS = {2017: '63826b94-669a-4094-a206-470d399df3c8', 2018: 'c369347b-53d4-4f92-821e-273089d773de',
            2019: '1aaba8cc-9d93-480e-a29a-7a92324cc5b8', 2020: '41adeeb3-89f1-4a86-8982-c2d27b5f3e6f',
            2021: 'f447e4c3-4783-4e83-b9e4-61694f439d82', 2022: '9eff03a0-55ce-44fd-b29b-9735f8d71e8d',
            2023: '4f8fbd8e-ccec-4fbb-b346-575b58afb38a', 2024: '2c6afc6a-ece4-4656-ac30-0ebaeb0459a3'}
CEREALS = {'AC01', 'AC19', 'AC24', 'AC30', 'AC32', 'AC63', 'AC65', 'AC66', 'AC68', 'AC69'}   # barley, oats, rye, triticale, wheat


def gdb_file(fs):
    files = requests.get(API.format(fs), timeout=60).json()['files']
    f = next(f for f in files if f['name'].endswith('.gdb.zip'))
    return f['name'], f['size']


def download(year, tries=6):
    fs = FILESETS[year]; name, size = gdb_file(fs)
    path = os.path.join(WORK, name)
    for k in range(tries):
        t = time.time()
        r = subprocess.run(['curl', '-sS', '-L', '--fail', '--retry', '3', '--retry-all-errors', '--speed-time', '600',
                            '--speed-limit', '1000', '-o', path, DL.format(fs, name)])
        got = os.path.getsize(path) if os.path.exists(path) else 0
        print(f'  {year}: try {k + 1}: {got / 1e9:.2f} of {size / 1e9:.2f} GB in {(time.time() - t) / 60:.0f} min', flush=True)
        if r.returncode == 0 and zipfile.is_zipfile(path):
            return path
        time.sleep(60)
    raise RuntimeError(f'download failed: {year}')


def wait_for_parcels():
    while True:
        if os.path.exists(PARCELS):
            with open(PARCELS, 'rb') as fh:
                n = sum(1 for _ in fh) - 1
            if n >= N_PARCELS:
                return
        print('  waiting for the parcel points download to finish', flush=True)
        time.sleep(600)


def hex_centres(gdb):
    """lucode + hexagon centre for every feature in every layer, read in chunks to bound memory."""
    out = []
    for layer, _ in pyogrio.list_layers(gdb):
        n = pyogrio.read_info(gdb, layer=layer)['features']
        cols = [c for c in pyogrio.read_info(gdb, layer=layer)['fields'] if c.lower() == 'lucode']
        for skip in range(0, n, 2_000_000):
            g = pyogrio.read_dataframe(gdb, layer=layer, columns=cols, skip_features=skip, max_features=2_000_000)
            if g.crs is not None and g.crs.to_epsg() != 27700:
                g = g.to_crs(27700)
            c = g.geometry.centroid
            out.append(pd.DataFrame({'lucode': g[cols[0]].astype(str).str.strip().values,
                                     'x': c.x.values.astype('float32'), 'y': c.y.values.astype('float32')}))
    h = pd.concat(out, ignore_index=True)
    ok = np.isfinite(h.x) & np.isfinite(h.y)        # a few 2025 features have empty geometry
    if (~ok).any():
        print(f'  skipped {(~ok).sum():,} hexagons without geometry', flush=True)
    return h[ok].reset_index(drop=True)


def main(years, gdb_path=None):
    os.makedirs(WORK, exist_ok=True); os.makedirs(OUT, exist_ok=True)
    for year in years:
        dst = os.path.join(OUT, f'parcel_crop_{year}.parquet')
        if os.path.exists(dst):
            print(f'{year}: done already', flush=True); continue
        print(f'== {year} {time.strftime("%H:%M")}', flush=True)
        if gdb_path:
            h = hex_centres(gdb_path)
        else:
            z = download(year)
            ex = os.path.join(WORK, f'x{year}')
            with zipfile.ZipFile(z) as zf:
                zf.extractall(ex)
            os.remove(z)
            gdb = next(p for p in glob.glob(os.path.join(ex, '**', '*.gdb'), recursive=True))
            h = hex_centres(gdb)
            shutil.rmtree(ex)
        wait_for_parcels()
        p = pd.read_csv(PARCELS, dtype=str, usecols=['parcel_reference', 'x_bng', 'y_bng']).dropna()
        p = p.drop_duplicates('parcel_reference')
        xy = np.c_[p.x_bng.astype(float), p.y_bng.astype(float)]
        dist, idx = cKDTree(h[['x', 'y']].values).query(xy, k=1, distance_upper_bound=200)
        ok = np.isfinite(dist)
        lu = np.where(ok, h.lucode.values[np.minimum(idx, len(h) - 1)], None)
        t = pd.DataFrame({'parcref': p.parcel_reference.values, 'year': year, 'lucode': lu})
        t['cereal'] = t.lucode.isin(CEREALS)
        t.to_parquet(dst, index=False)
        print(f'{year}: {len(h):,} hexagons; parcels with a crop code {ok.mean():.1%}; cereal {t.cereal.mean():.1%} '
              f'-> {os.path.relpath(dst, ROOT)}', flush=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--years', nargs='*', type=int, default=sorted(FILESETS))
    ap.add_argument('--gdb', help='use an already downloaded and unzipped CROME .gdb (give one year in --years)')
    a = ap.parse_args()
    main(a.years, a.gdb)
