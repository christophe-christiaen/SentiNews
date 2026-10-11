"""Stranding-risk layers at parcel level: Environment Agency flood zones and Natural England peaty soils.

  Flood Map for Planning - Flood Zones 2 and 3 (rivers and sea), Environment Agency, OGL v3
      Defra DSP file 'Flood_Map_for_Planning_Flood_Zones.gdb.zip' (signed, resumable link)
      Zone 3: >= 1% annual chance from rivers or >= 0.5% from the sea; Zone 2: 0.1-1% (rivers) / 0.1-0.5% (sea)
  Peaty Soils Location (England), Natural England with BGS and NSRI: deep peat / shallow peat / soils with peaty pockets
      ArcGIS FeatureServer (9,028 polygons)
Each RPA parcel point gets its flood zone (3, 2 or none) and peat class (or none).

Output  shared/data/reference/risk/flood_zones.gdb, peaty_soils.gpkg
        shared/data/parcels/parcel_risk.parquet          parcref, flood_zone, peat_class
        shared/results/parcel_risk_summary.md            counts only
"""
import glob, os, subprocess, zipfile
import pandas as pd, geopandas as gpd, pyogrio, requests
from fetch_schemes import arcgis_features, NE

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
D = os.path.join(ROOT, 'shared', 'data')
R = os.path.join(D, 'reference', 'risk')
SUMMARY = os.path.join(ROOT, 'shared', 'results', 'parcel_risk_summary.md')
FLOOD_FS, FLOOD_FILE = '455d2eb3-3065-4d20-871b-c4d5dee23f67', 'Flood_Map_for_Planning_Flood_Zones.gdb.zip'
SIGN = 'https://environment.data.gov.uk/file-management-open/data-sets/{}/files/{}/download-url'


def fetch_flood():
    z = os.path.join(R, FLOOD_FILE)
    for _ in range(20):
        url = requests.get(SIGN.format(FLOOD_FS, FLOOD_FILE), timeout=60).json()['url']
        real = int(requests.head(url, timeout=60).headers['Content-Length'])
        if os.path.exists(z) and os.path.getsize(z) >= real:
            break
        subprocess.run(['curl', '-sS', '-C', '-', '--speed-time', '300', '--speed-limit', '500', '-o', z, url])
    gdb = os.path.join(R, 'flood_zones.gdb')
    if not os.path.exists(gdb):
        with zipfile.ZipFile(z) as zf:
            zf.extractall(gdb)
    inner = [p for p in glob.glob(os.path.join(gdb, '**', '*.gdb'), recursive=True)]
    return inner[0] if inner else gdb


def fetch_peat():
    f = os.path.join(R, 'peaty_soils.gpkg')
    if not os.path.exists(f):
        feats = list(arcgis_features(f'{NE}/Peaty_Soils_Location/FeatureServer/1', geometry=True, page=2000))
        gpd.GeoDataFrame.from_features(feats, crs=27700)[['PCLASSDESC', 'geometry']].to_file(f, driver='GPKG')
    return gpd.read_file(f)


def main():
    os.makedirs(R, exist_ok=True)
    p = pd.read_parquet(os.path.join(D, 'parcels', 'parcel_panel.parquet'), columns=['parcref', 'x', 'y', 'cereal_land', 'parcel_group'])
    pts = gpd.GeoDataFrame(p[['parcref']], geometry=gpd.points_from_xy(p.x, p.y), crs=27700)

    peat = fetch_peat()
    j = gpd.sjoin(pts, peat, predicate='within', how='left')
    p['peat_class'] = j.groupby(level=0).PCLASSDESC.first().reindex(p.index)

    gdb = fetch_flood()
    layer = pyogrio.list_layers(gdb)[0][0]
    info = pyogrio.read_info(gdb, layer=layer)
    zcol = next((c for c in info['fields'] if c.lower() in ('flood_zone', 'floodzone', 'zone', 'type')), info['fields'][0])
    fz = pyogrio.read_dataframe(gdb, layer=layer, columns=[zcol]).to_crs(27700)
    fz['zone'] = fz[zcol].astype(str).str.extract(r'(\d)')[0].astype(float)
    j = gpd.sjoin(pts, fz[['zone', 'geometry']], predicate='within', how='left')
    p['flood_zone'] = j.groupby(level=0).zone.max().reindex(p.index).astype('Int64')   # 3 beats 2 where they overlap

    p[['parcref', 'flood_zone', 'peat_class']].to_parquet(os.path.join(D, 'parcels', 'parcel_risk.parquet'), index=False)
    c = p[p.cereal_land]
    tab = lambda s: s.value_counts(dropna=False).rename_axis('').to_frame('cereal parcels').to_markdown()
    lines = ['# Stage 0 · Stranding-risk layers at parcel level (counts only)', '',
             f'- Flood layer field used: `{zcol}` ({len(fz):,} polygons); peat polygons: {len(peat):,}', '',
             '## Cereal-land parcels by flood zone', '', tab(c.flood_zone.astype('string').fillna('none')), '',
             '## Cereal-land parcels by peat class', '', tab(c.peat_class.fillna('none')), '',
             '## Flood zone 3 or deep peat, by scheme group (cereal land)', '',
             pd.crosstab(c.parcel_group, [(c.flood_zone == 3).fillna(False).map({True: 'zone 3', False: 'not zone 3'})]).to_markdown(), '',
             pd.crosstab(c.parcel_group, c.peat_class.fillna('none')).to_markdown()]
    open(SUMMARY, 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
