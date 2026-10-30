"""Match England's RPA parcel points to UKFields polygons (W3-1 record, 30 October 2026).

Rule: a parcel takes the UKFields polygon that contains its RPA parcel point, if that polygon contains no other RPA
parcel point and the point lies more than 20 m inside the polygon boundary; otherwise it is excluded.
Reads geometry and scheme codes only; no outcome or EO feature. Writes the per-parcel match (private) and aggregate
counts (public).
Usage: python match_ukfields_england.py
"""
import json
from pathlib import Path
import geopandas as gpd, numpy as np, pandas as pd
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / 'shared' / 'data'
OUT_P = D / 'parcels' / 'ukfields_england_match.parquet'
OUT_J = ROOT / 'wp3_elms_effect' / 'results' / 'ukfields_england_match.json'

# W3-1 families (protocol, Families; record of 30 October 2026) and the controls; entry 2021-2024
FAM = {'new_hedges': ['BN11', 'BN7'],
       'area_strips': ['SW1', 'SW3', 'AHW6', 'AHW7', 'AHW8', 'AHW9', 'AHW10', 'AHW11', 'AHL3', 'AHL4', 'CAHL3', 'CAHL4', 'AB8'],
       'hedge_management': ['BE3', 'BN5', 'BN6', 'HRW1', 'HRW2', 'HRW3', 'CHRW1', 'CHRW2', 'CHRW3'],
       'walls_banks': ['BN12', 'BN13', 'BN14', 'BN1', 'BN2', 'BN3', 'BN4']}

pts = pd.read_csv(D / 'schemes' / 'national' / 'rpa_parcel_points.csv', usecols=['parcel_reference', 'x_bng', 'y_bng'])
pts = pts.dropna(subset=['x_bng', 'y_bng']).drop_duplicates('parcel_reference').rename(columns={'parcel_reference': 'parcref'})
P = gpd.GeoDataFrame(pts, geometry=gpd.points_from_xy(pts.x_bng, pts.y_bng), crs=27700)
U = gpd.read_parquet(D / 'parcels' / 'ukfields.parquet')[['id', 'area', 'geometry']].to_crs(27700)
bad = ~U.geometry.is_valid
U.loc[bad, 'geometry'] = U.loc[bad].geometry.make_valid()

j = gpd.sjoin(P, U, how='left', predicate='within').drop(columns='index_right')
j = j[~j.index.duplicated(keep='first')]                          # overlapping polygons: first hit
n_in = j.groupby('id').size()
j['pts_in_poly'] = j['id'].map(n_in)
has = j['id'].notna()
geo = U.set_index('id').geometry
j.loc[has, 'dist_edge_m'] = geo.loc[j.loc[has, 'id']].boundary.distance(j.loc[has].geometry, align=False).values
j['reason'] = np.select([~has, j.pts_in_poly > 1, j.dist_edge_m <= 20], ['no_polygon', 'shared_polygon', 'near_edge'], 'matched')
j['matched'] = j.reason == 'matched'

# families: CS by PARCREF; SFI snapped to the nearest parcel point (decisions record)
cs = pd.read_csv(D / 'schemes' / 'national' / 'cs_options.csv', usecols=['PARCREF', 'OPTION_CODE', 'STARTDATE'])
cs = cs[pd.to_datetime(cs.STARTDATE.astype(str), format='%Y%m%d', errors='coerce').dt.year.between(2021, 2024)]
sfi = pd.read_csv(D / 'schemes' / 'national' / 'sfi_actions.csv', usecols=['option_code', 'contract_start', 'x_bng', 'y_bng'])
sfi = sfi[pd.to_datetime(sfi.contract_start, errors='coerce').dt.year.between(2021, 2024)].dropna(subset=['x_bng', 'y_bng'])
_, k = cKDTree(pts[['x_bng', 'y_bng']].values).query(sfi[['x_bng', 'y_bng']].values)
sfi['parcref'] = pts.parcref.values[k]
codes = pd.concat([cs.rename(columns={'PARCREF': 'parcref', 'OPTION_CODE': 'code'})[['parcref', 'code']],
                   sfi.rename(columns={'option_code': 'code'})[['parcref', 'code']]])
for f, cc in FAM.items():
    j[f] = j.parcref.isin(codes.loc[codes.code.isin(cc), 'parcref'])

panel = pd.read_parquet(D / 'parcels' / 'parcel_panel.parquet', columns=['parcref', 'parcel_group', 'cereal_land'])
j = j.merge(panel, on='parcref', how='left')
j['never_treated'] = j.parcel_group.eq('no agreement')

j[['parcref', 'id', 'area', 'pts_in_poly', 'dist_edge_m', 'reason', 'matched', 'cereal_land', 'parcel_group', *FAM]].rename(
    columns={'id': 'ukfields_id', 'area': 'ukfields_area_ha'}).to_parquet(OUT_P, index=False)


def summ(m):
    return dict(parcels=int(m.sum()), matched=int((m & j.matched).sum()),
                share_matched=round(float((m & j.matched).sum() / max(m.sum(), 1)), 3),
                excluded=j.loc[m, 'reason'].value_counts().reindex(['no_polygon', 'shared_polygon', 'near_edge'], fill_value=0).astype(int).to_dict())


cer = j.cereal_land.fillna(False).astype(bool)
res = {'rule': 'polygon containing the RPA point; no other RPA point inside; point > 20 m from the boundary',
       'ukfields_polygons': int(len(U)), 'all_parcels': summ(pd.Series(True, index=j.index)), 'cereal_frame': summ(cer),
       'cereal_frame_by_family': {f: summ(cer & j[f]) for f in FAM},
       'cereal_frame_never_treated': summ(cer & j.never_treated),
       'all_land_by_family': {f: summ(j[f]) for f in FAM}}
OUT_J.write_text(json.dumps(res, indent=1))
print(json.dumps(res, indent=1))
