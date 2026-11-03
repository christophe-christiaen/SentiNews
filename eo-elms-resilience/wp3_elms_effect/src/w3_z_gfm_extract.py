"""Addendum 6 Part F, layer 2: GFM observed flooding per parcel and winter (protocol: w3_z_addendum6_hazards_protocol.md,
Part F and the record row of 3 November 2026, which fixes the rules below before any pixel was read at a parcel).

Source: Copernicus EMS Global Flood Monitoring, EODC STAC collection GFM (ensemble_flood_extent, exclusion_mask; Equi7
EU020M T3 tiles, 20 m). Images are streamed and discarded; only per-parcel results are kept (private).
Contains modified Copernicus Emergency Management Service information 2015-2026.

Rules:
1. Winters October-March, labelled by the March year (2016-2026).
2. One observation per parcel per UTC acquisition day: the day's frames are merged per pixel (observed if any frame
   observes it; flooded if any frame flags it).
3. A pixel is observed if ensemble_flood_extent != 255 and (exclusion_mask == 0 or the pixel is flooded); any non-zero
   exclusion_mask value (1-254) is excluded; flooded means ensemble_flood_extent == 1.
4. Point version: the pixel holding the parcel point.
5. Outline version (UKFields-matched parcels): observed on a day if >= 50% of the outline's pixels are observed; flooded
   if flooded pixels are >= 10% of its pixels. Each outline is read in the tile holding its parcel point.
6. Kept per parcel-season: observed days, flooded days, flood dates.

Output (private): wp3_elms_effect/data/gfm/{tile}_{season}.parquet (counts) and {tile}_{season}_events.parquet (flood
days); merged by w3_z_gfm_merge.py. Resumable: finished tile-seasons are skipped.
Run: python w3_z_gfm_extract.py [--seasons 2016-2026] [--tiles E039N021T3,...] [--days-in-flight 5]
"""
import os, sys, json, time, argparse, urllib.request, threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import numpy as np, pandas as pd, geopandas as gpd, rasterio
from rasterio.features import rasterize
from pyproj import Transformer

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
PAR = os.path.join(ROOT, 'shared', 'data', 'parcels')
OUT = os.path.join(ROOT, 'wp3_elms_effect', 'data', 'gfm')   # private
STAC = 'https://stac.eodc.eu/api/v1/search'
BBOX = [-5.8, 49.9, 1.8, 55.8]
ASSETS = ('ensemble_flood_extent', 'exclusion_mask')
OL_OBS, OL_FLOOD = 0.5, 0.1
GDAL = dict(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR', GDAL_HTTP_MULTIRANGE='YES', GDAL_HTTP_MERGE_CONSECUTIVE_RANGES='YES',
            GDAL_HTTP_MAX_RETRY='6', GDAL_HTTP_RETRY_DELAY='3', CPL_VSIL_CURL_CACHE_SIZE='0')
log = lambda *a: print(time.strftime('%m-%d %H:%M:%S'), *a, flush=True)


def items(season):
    """All GFM items over England for the winter ending in March of `season` (cached, private)."""
    f = os.path.join(OUT, 'items', f'{season}.json')
    if os.path.exists(f):
        return json.load(open(f))
    body = {'collections': ['GFM'], 'bbox': BBOX, 'limit': 500,
            'datetime': f'{season - 1}-10-01T00:00:00Z/{season}-03-31T23:59:59Z'}
    url, out = STAC, []
    while url:
        r = urllib.request.Request(url, data=json.dumps(body).encode(), headers={'Content-Type': 'application/json'})
        d = json.load(urllib.request.urlopen(r, timeout=300))
        out += [dict(id=x['id'], tile=x['id'].rsplit('_', 1)[-1], datetime=x['properties']['datetime'],
                     **{a: x['assets'][a]['href'] for a in ASSETS}) for x in d['features'] if all(a in x['assets'] for a in ASSETS)]
        nxt = [l for l in d.get('links', []) if l.get('rel') == 'next']
        url, body = (nxt[0]['href'], nxt[0].get('body', body)) if nxt else (None, None)
    os.makedirs(os.path.dirname(f), exist_ok=True)
    json.dump(out, open(f, 'w'))
    return out


def read(href):
    for k in range(5):
        try:
            with rasterio.Env(**GDAL), rasterio.open('/vsicurl/' + href) as s:
                return s.read(1), s.transform, s.crs
        except Exception as e:
            log('retry', k, href.rsplit('/', 1)[-1], repr(e)[:120]); time.sleep(10 * (k + 1))
    raise RuntimeError('unreadable ' + href)


class Tile:
    """Parcel points and outline labels on one tile's 15000 x 15000 grid."""

    def __init__(self, name, href, P, U):
        with rasterio.Env(**GDAL), rasterio.open('/vsicurl/' + href) as s:
            self.tr, self.crs, self.shape = s.transform, s.crs, s.shape
        tf = Transformer.from_crs('EPSG:27700', self.crs, always_xy=True)
        X, Y = tf.transform(P.x.values, P.y.values)
        c = np.floor((X - self.tr.c) / self.tr.a).astype(np.int64); r = np.floor((Y - self.tr.f) / self.tr.e).astype(np.int64)
        inside = (r >= 0) & (r < self.shape[0]) & (c >= 0) & (c < self.shape[1])
        self.pi = np.flatnonzero(inside)                  # parcel row numbers in this tile
        self.flat = r[inside] * self.shape[1] + c[inside]
        u = U[U.prow.isin(self.pi)].to_crs(self.crs)
        self.ol_prow = u.prow.values                      # outline k (label k+1) -> parcel row
        self.label = rasterize(zip(u.geometry.values, np.arange(1, len(u) + 1)), out_shape=self.shape,
                               transform=self.tr, fill=0, dtype='int32').ravel() if len(u) else None
        self.ol_npix = np.bincount(self.label, minlength=len(u) + 1)[1:] if len(u) else np.zeros(0)
        log(name, 'parcels', len(self.pi), 'outlines', len(u), 'outlines with no pixel', int((self.ol_npix == 0).sum()))


def day(tile, frames):
    obs = np.zeros(tile.shape[0] * tile.shape[1], bool); fl = np.zeros_like(obs)
    for it in frames:
        f = read(it['ensemble_flood_extent'])[0].ravel(); x = read(it['exclusion_mask'])[0].ravel()
        flood = f == 1
        obs |= (f != 255) & ((x == 0) | flood); fl |= flood
        del f, x, flood
    res = dict(pt_obs=obs[tile.flat], pt_fl=fl[tile.flat])
    if tile.label is not None:
        K = len(tile.ol_npix) + 1
        o = np.bincount(tile.label[obs], minlength=K)[1:]; w = np.bincount(tile.label[fl], minlength=K)[1:]
        n = np.maximum(tile.ol_npix, 1)
        res.update(ol_obs=(tile.ol_npix > 0) & (o >= OL_OBS * n), ol_fl=(tile.ol_npix > 0) & (w >= OL_FLOOD * n), ol_frac=w / n)
    return res


def run(tname, season, its, tile, P, nflight):
    out = os.path.join(OUT, f'{tname}_{season}.parquet')
    if os.path.exists(out):
        return
    byday = defaultdict(list)
    for it in its:
        byday[it['datetime'][:10]].append(it)
    n = len(tile.pi); k = len(tile.ol_npix)
    acc = dict(pt_obs=np.zeros(n, np.int16), pt_fl=np.zeros(n, np.int16), ol_obs=np.zeros(k, np.int16), ol_fl=np.zeros(k, np.int16))
    ev, lock, t0 = [], threading.Lock(), time.time()

    def one(d):
        r = day(tile, byday[d])
        with lock:
            for key in acc:
                if key in r: acc[key] += r[key]
            for i in np.flatnonzero(r['pt_fl']):
                ev.append((int(tile.pi[i]), d, 'point', 1.0))
            if 'ol_fl' in r:
                for i in np.flatnonzero(r['ol_fl']):
                    ev.append((int(tile.ol_prow[i]), d, 'outline', float(r['ol_frac'][i])))

    with ThreadPoolExecutor(nflight) as ex:
        list(ex.map(one, sorted(byday)))
    c = pd.DataFrame({'prow': tile.pi, 'pt_obs_days': acc['pt_obs'], 'pt_flood_days': acc['pt_fl']})
    o = pd.DataFrame({'prow': tile.ol_prow, 'ol_obs_days': acc['ol_obs'], 'ol_flood_days': acc['ol_fl']})
    c = c.merge(o, on='prow', how='left').assign(season=season, tile=tname, days=len(byday), frames=len(its))
    c['parcref'] = P.parcref.values[c.prow.values]
    e = pd.DataFrame(ev, columns=['prow', 'date', 'version', 'flood_frac'])
    e['parcref'] = P.parcref.values[e.prow.values] if len(e) else []
    e.assign(season=season, tile=tname).to_parquet(out.replace('.parquet', '_events.parquet'), index=False)
    c.to_parquet(out, index=False)   # written last: marks the tile-season done
    log(tname, season, 'days', len(byday), 'frames', len(its), 'flood events', len(e), f'{(time.time() - t0) / 60:.1f} min')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seasons', default='2016-2026'); ap.add_argument('--tiles', default='')
    ap.add_argument('--days-in-flight', type=int, default=5)
    a = ap.parse_args()
    s0, s1 = map(int, a.seasons.split('-')) if '-' in a.seasons else (int(a.seasons),) * 2
    os.makedirs(OUT, exist_ok=True)
    P = pd.read_parquet(os.path.join(PAR, 'parcel_panel.parquet'), columns=['parcref', 'x', 'y']).reset_index(drop=True)
    m = pd.read_parquet(os.path.join(PAR, 'ukfields_england_match.parquet'), columns=['parcref', 'ukfields_id', 'matched'])
    m = m[m.matched == True].merge(P[['parcref']].reset_index().rename(columns={'index': 'prow'}), on='parcref')
    U = gpd.read_parquet(os.path.join(PAR, 'ukfields.parquet'), columns=['id', 'geometry']).merge(
        m[['ukfields_id', 'prow']], left_on='id', right_on='ukfields_id')[['prow', 'geometry']]
    log('parcels', len(P), 'outlines', len(U))
    S = {s: items(s) for s in range(s0, s1 + 1)}
    for s in S:
        log('season', s, 'frames', len(S[s]))
    names = sorted({i['tile'] for v in S.values() for i in v})
    if a.tiles:
        names = [t for t in names if t in a.tiles.split(',')]
    for t in names:
        todo = [s for s in S if not os.path.exists(os.path.join(OUT, f'{t}_{s}.parquet'))]
        if not todo:
            continue
        tile = Tile(t, next(i for v in S.values() for i in v if i['tile'] == t)['ensemble_flood_extent'], P, U)
        if len(tile.pi) == 0:
            for s in todo:   # tile holds no English parcel: mark done
                pd.DataFrame(columns=['prow']).to_parquet(os.path.join(OUT, f'{t}_{s}.parquet'))
            continue
        for s in todo:
            run(t, s, [i for i in S[s] if i['tile'] == t], tile, P, a.days_in_flight)
        del tile


if __name__ == '__main__':
    main()
