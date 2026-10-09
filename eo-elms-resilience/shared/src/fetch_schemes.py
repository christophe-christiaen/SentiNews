"""Fetch agri-environment scheme layers (Countryside Stewardship, Environmental Stewardship, SFI).

Sources (all OGL v3):
  Natural England / RPA ArcGIS FeatureServer  - CS options, CS management areas, ES options, ES agreements
  Defra Data Services Platform OGC API        - SFI actions, SFI agreement areas

Usage
  python fetch_schemes.py --pilot              # clip every layer to the 40 English pilot windows (6 x 6 km)
  python fetch_schemes.py --national cs_options # whole-England attribute table (no geometry) for one layer

Output: shared/data/schemes/pilot/<layer>.geojson (EPSG:27700, with region/site columns)
        shared/data/schemes/national/<layer>.csv
Personal / organisation name fields are dropped at download (not needed for the analysis).
All layers are live snapshots: agreements that have ended are not included.
"""
import argparse, csv, json, os, sys, time
import requests
from pyproj import Transformer
from shapely.geometry import box, shape, mapping
from shapely.ops import transform as stransform

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'src'))
from sites import SITES, ENGLAND, KM  # noqa: E402

OUT = os.path.join(ROOT, 'shared', 'data', 'schemes')
NE = 'https://services.arcgis.com/JJzESW51TqeY9uat/arcgis/rest/services'
DSP = 'https://environment.data.gov.uk/geoservices/datasets'
DROP = {'ORG_NAME', 'CUSTNAME', 'TOWN', 'GlobalID'}   # names are not needed; GlobalID is noise

LAYERS = {
    # Countryside Stewardship 2016+ options: one point per option per parcel, with option code and dates
    'cs_options': dict(kind='arcgis', url=f'{NE}/Countryside_Stewardship_Scheme_2016_Options_England/FeatureServer/1',
                       date_fields=['STARTDATE', 'ENDDATE'], code_field='OPTION_CODE'),
    # Countryside Stewardship agreement polygons (management areas)
    'cs_management_areas': dict(kind='arcgis', url=f'{NE}/Countryside_Stewardship_Scheme_2016_Management_Areas_England/FeatureServer/1',
                                date_fields=['STARTDATE', 'ENDDATE'], clip=True),
    # Environmental Stewardship (ELS/HLS) options still live: pre-2016 scheme history
    'es_options': dict(kind='arcgis', url=f'{NE}/Environmental_Stewardship_Scheme_Options/FeatureServer/0',
                       date_fields=['STARTDAT', 'ENDDATE'], code_field='OPTCODE'),
    'es_agreements': dict(kind='arcgis', url=f'{NE}/Environmental_Stewardship_Scheme_Agreements_England_2024/FeatureServer/0',
                          date_fields=['STARTDAT', 'ENDDATE'], clip=True),
    # Sustainable Farming Incentive actions: one point per action per parcel
    'sfi_actions': dict(kind='ogc', url=f'{DSP}/58cc85ab-a955-4b37-9c42-eee8532cbd01/ogc/features/v1/collections/'
                                        'Sustainable_Farming_Incentive_Scheme_Actions_England/items',
                        date_fields=['contract_start', 'contract_end'], code_field='option_code'),
    'sfi_agreement_areas': dict(kind='ogc', url=f'{DSP}/0f799be5-20c3-4e03-8f43-3cf549724a03/ogc/features/v1/collections/'
                                                'Sustainable_Farming_Incentive_Scheme_Agreement_Areas_England/items',
                                date_fields=['contract_start', 'contract_end'], clip=True),
}

S = requests.Session()
to_bng = Transformer.from_crs(4326, 27700, always_xy=True)
to_wgs = Transformer.from_crs(27700, 4326, always_xy=True)


def get(url, params, tries=6):
    for k in range(tries):
        try:
            r = S.get(url, params=params, timeout=180)
            if r.status_code == 200:
                return r.json()
        except (requests.RequestException, ValueError):
            pass
        time.sleep(2 * (k + 1))
    raise RuntimeError(f'failed: {url} {params}')


def arcgis_features(url, bbox_bng=None, geometry=True, page=1000):
    """Page through an ArcGIS FeatureServer layer; returns GeoJSON features in EPSG:27700."""
    off = 0
    while True:
        p = dict(where='1=1', outFields='*', f='geojson' if geometry else 'json', resultOffset=off,
                 resultRecordCount=page, returnGeometry=str(geometry).lower(), outSR=27700)
        if bbox_bng:
            p.update(geometry=json.dumps(dict(xmin=bbox_bng[0], ymin=bbox_bng[1], xmax=bbox_bng[2], ymax=bbox_bng[3],
                                              spatialReference={'wkid': 27700})),
                     geometryType='esriGeometryEnvelope', inSR=27700, spatialRel='esriSpatialRelIntersects')
        d = get(f'{url}/query', p)
        feats = d.get('features', [])
        for f in feats:
            if not geometry:  # esri json -> plain properties
                f = dict(type='Feature', properties=f['attributes'], geometry=None)
            yield f
        if len(feats) < page and not d.get('exceededTransferLimit'):
            break
        off += len(feats)


def ogc_features(url, bbox_bng=None, limit=1000):
    """Page through an OGC API Features collection (WGS84); returns features reprojected to EPSG:27700."""
    p = dict(f='json', limit=limit)
    if bbox_bng:
        xs, ys = zip(*[to_wgs.transform(bx, by) for bx in (bbox_bng[0], bbox_bng[2]) for by in (bbox_bng[1], bbox_bng[3])])
        p['bbox'] = f'{min(xs)},{min(ys)},{max(xs)},{max(ys)}'   # WGS84 box enclosing the BNG window
    nxt, params = url, p
    while nxt:
        d = get(nxt, params)
        for f in d.get('features', []):
            if f.get('geometry'):
                f['geometry'] = mapping(stransform(to_bng.transform, shape(f['geometry'])))
            yield f
        nxt = next((l['href'] for l in d.get('links', []) if l.get('rel') == 'next'), None)
        params = None  # the next link already carries the query


def clean(props):
    return {k: v for k, v in props.items() if k not in DROP}


def fetch_pilot(layers):
    os.makedirs(os.path.join(OUT, 'pilot'), exist_ok=True)
    summary = []
    for name in layers:
        cfg = LAYERS[name]; feats = []
        for reg in ENGLAND:
            for i, (lat, lon) in enumerate(SITES[reg]):
                x, y = to_bng.transform(lon, lat)
                win = box(x - KM * 1000, y - KM * 1000, x + KM * 1000, y + KM * 1000)
                src = arcgis_features(cfg['url'], win.bounds) if cfg['kind'] == 'arcgis' else ogc_features(cfg['url'], win.bounds)
                n = 0
                for f in src:
                    g = shape(f['geometry']) if f.get('geometry') else None
                    if g is None or not g.intersects(win):
                        continue
                    if cfg.get('clip'):
                        g = g.buffer(0).intersection(win)
                        if g.is_empty:
                            continue
                    props = clean(f['properties']); props.update(region=reg, site=i)
                    if cfg.get('clip'):
                        props['clipped_ha'] = round(g.area / 1e4, 3)
                    feats.append(dict(type='Feature', properties=props, geometry=mapping(g))); n += 1
                summary.append(dict(layer=name, region=reg, site=i, features=n))
        fn = os.path.join(OUT, 'pilot', f'{name}.geojson')
        json.dump(dict(type='FeatureCollection', crs=dict(type='name', properties=dict(name='EPSG:27700')), features=feats),
                  open(fn, 'w'))
        print(f'{name}: {len(feats)} features -> {os.path.relpath(fn, ROOT)}', flush=True)
    with open(os.path.join(OUT, 'pilot', 'feature_counts.csv'), 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=['layer', 'region', 'site', 'features']); w.writeheader(); w.writerows(summary)


def fetch_national(name):
    """Whole-England attribute table (no geometry, but point layers keep their coordinates as columns)."""
    os.makedirs(os.path.join(OUT, 'national'), exist_ok=True)
    cfg = LAYERS[name]; fn = os.path.join(OUT, 'national', f'{name}.csv'); n = 0
    src = arcgis_features(cfg['url'], geometry=False, page=2000) if cfg['kind'] == 'arcgis' else ogc_features(cfg['url'], limit=10000)
    with open(fn, 'w', newline='') as fh:
        w = None
        for f in src:
            props = clean(f['properties'])
            if cfg['kind'] == 'ogc' and f.get('geometry') and f['geometry']['type'] == 'Point':
                props['x_bng'], props['y_bng'] = f['geometry']['coordinates'][:2]
            if w is None:
                w = csv.DictWriter(fh, fieldnames=list(props), extrasaction='ignore'); w.writeheader()
            w.writerow(props); n += 1
            if n % 100000 == 0:
                print(f'  {name}: {n}', flush=True)
    print(f'{name}: {n} rows -> {os.path.relpath(fn, ROOT)}')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--pilot', action='store_true', help='clip all layers to the English pilot windows')
    ap.add_argument('--layers', nargs='*', default=list(LAYERS), choices=list(LAYERS))
    ap.add_argument('--national', choices=list(LAYERS), help='download one layer for all of England (attributes)')
    a = ap.parse_args()
    if a.pilot:
        fetch_pilot(a.layers)
    if a.national:
        fetch_national(a.national)
    if not (a.pilot or a.national):
        ap.print_help()
