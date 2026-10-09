"""Countryside Stewardship (CS) agri-environment coverage around each English site.
Source: Natural England / RPA 'Countryside Stewardship Scheme Management Areas (England)'
ArcGIS FeatureServer (Open Government Licence). Polygons are clipped to each
site's 6 x 6 km window (EPSG:27700) and summarised by agreement start year."""
import json, os, requests, pandas as pd
from pyproj import Transformer
from shapely.geometry import shape, box
from shapely.ops import unary_union
from sites import SITES, ENGLAND, KM
URL = ('https://services.arcgis.com/JJzESW51TqeY9uat/arcgis/rest/services/'
       'Countryside_Stewardship_Scheme_2016_Management_Areas_England/FeatureServer/1/query')
ROOT = os.path.join(os.path.dirname(__file__), '..')
tr = Transformer.from_crs(4326, 27700, always_xy=True)
rows, summ = [], []
for reg in ENGLAND:
    for i, (lat, lon) in enumerate(SITES[reg]):
        x, y = tr.transform(lon, lat)
        win = box(x - KM*1000, y - KM*1000, x + KM*1000, y + KM*1000)
        feats, off = [], 0
        while True:
            r = requests.get(URL, params=dict(where='1=1', geometry=json.dumps(dict(
                xmin=win.bounds[0], ymin=win.bounds[1], xmax=win.bounds[2], ymax=win.bounds[3],
                spatialReference={'wkid': 27700})), geometryType='esriGeometryEnvelope',
                spatialRel='esriSpatialRelIntersects', outFields='STARTDATE,CS_TYPE,STATUS',
                outSR=27700, f='geojson', resultOffset=off, resultRecordCount=1000), timeout=120).json()
            feats += r.get('features', [])
            if len(r.get('features', [])) < 1000: break
            off += 1000
        geoms = []
        for f in feats:
            try: g = shape(f['geometry']).buffer(0).intersection(win)
            except Exception: continue
            p = f['properties']
            if any(k in str(p.get('CS_TYPE')) for k in ('Capital', 'Woodland', 'Tree Health')):
                continue  # keep land-management agreements only (MT/HT/offers)
            yr = pd.to_datetime(p.get('STARTDATE'), unit='ms', errors='coerce') if isinstance(p.get('STARTDATE'), (int, float)) \
                else pd.to_datetime(p.get('STARTDATE'), errors='coerce', dayfirst=True)
            geoms.append((getattr(yr, 'year', None), g))
            rows.append(dict(region=reg, site=i, ha=g.area/1e4, start_year=getattr(yr, 'year', None),
                             cs_type=p.get('CS_TYPE'), status=p.get('STATUS')))
        area = (2*KM*1000)**2
        u = lambda gs: unary_union(gs).area / area if gs else 0.0
        summ.append(dict(region=reg, site=i, n_polys=len(geoms),
                         cs_share_all=u([g for _, g in geoms]),
                                                  cs_share_by2021=u([g for y, g in geoms if y and y <= 2021])))
        print(reg, i, len(feats), round(summ[-1]['cs_share_all'], 3), flush=True)
df = pd.DataFrame(rows)
df.to_csv(os.path.join(ROOT, 'data/processed/cs_polygons_clipped.csv'), index=False)
sm = pd.DataFrame(summ)
sm.to_csv(os.path.join(ROOT, 'data/processed/cs_share_by_site.csv'), index=False)
print(sm.groupby('region')[['cs_share_all', 'cs_share_by2021']].mean().round(3))
