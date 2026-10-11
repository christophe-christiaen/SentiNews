"""Stage 0 (option 1): parcel-level treatment table. Every registered land parcel in England, whoever farms it
(company, sole trader, partnership), with the agri-environment options on it and when they started.

Join keys
  CS options, ES options (live + ELMS_all history): PARCREF = RPA parcel reference (e.g. ST64690578), exact join
  SFI actions: no parcel reference is published, so each action point is snapped to the nearest parcel point;
               snaps further than SNAP_M are kept as 'uncertain'
Only area-based options (unit = hectares) count as land management on the parcel; per-metre (hedgerows, walls) and
per-item / whole-farm options (soil plans, assessments) are recorded separately and do not make a parcel 'treated'.

Groups (parcel_group)
  agreement     an area-based CS or SFI option on the parcel (start year = earliest such option)
  legacy ES     only Environmental Stewardship options (2006-2014 starts), no CS / SFI
  no agreement  no option of any kind in any source (live layers or ES history)
  uncertain     only non-area options, or an SFI action snapped from more than SNAP_M away
Caveat: the live layers omit CS agreements that have already ended, and the ES history is truncated, so some
'no agreement' parcels had an agreement in the past. Use start years and the ES flag to restrict comparisons.

Input   shared/data/schemes/national/{rpa_parcel_points,cs_options,es_options,sfi_actions}.csv
        shared/data/schemes/history/es_options_history.parquet
        shared/data/schemes/snapshots/cs_agreements_2024_03/*.shp   legacy Countryside Stewardship Scheme (CSS,
            1991-2004 agreements, all ended 2014; polygons): parcels inside get css_legacy = True
Output  shared/data/parcels/parcel_schemes.parquet     one row per parcel (no personal data)
        shared/results/parcel_schemes_summary.md       counts only (safe to commit)
"""
import glob, os, re
import numpy as np, pandas as pd
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
D = os.path.join(ROOT, 'shared', 'data')
NAT = os.path.join(D, 'schemes', 'national')
OUT = os.path.join(D, 'parcels')
SUMMARY = os.path.join(ROOT, 'shared', 'results', 'parcel_schemes_summary.md')
SNAP_M = 50
PARCREF = re.compile(r'^[A-Z]{2}\d{8}$')
HA = {'HA', 'HECTARES', 'HECTARE'}


def ts(s):
    s = pd.Series(s)
    if pd.api.types.is_datetime64_any_dtype(s):
        return s
    num = pd.to_numeric(s, errors='coerce')
    out = pd.to_datetime(num.where(num > 1e11), unit='ms', errors='coerce')
    ymd = pd.to_datetime(s.where(num.between(19000101, 21001231)).astype('string').str[:8], format='%Y%m%d', errors='coerce')
    iso = pd.to_datetime(s.where(num.isna()), errors='coerce', utc=True).dt.tz_localize(None)
    return out.fillna(ymd).fillna(iso)


def options():
    """One row per option on a parcel: parcref, family, code, start/end year, area-based flag."""
    rows = []
    cs = pd.read_csv(os.path.join(NAT, 'cs_options.csv'), dtype=str,
                     usecols=['PARCREF', 'OPTION_CODE', 'STARTDATE', 'ENDDATE', 'UNIT_OF_MEASURE'])
    rows.append(pd.DataFrame({'parcref': cs.PARCREF, 'fam': 'CS', 'code': cs.OPTION_CODE, 'start': ts(cs.STARTDATE),
                              'end': ts(cs.ENDDATE), 'area_based': cs.UNIT_OF_MEASURE.str.upper().isin(HA)}))
    es = pd.read_csv(os.path.join(NAT, 'es_options.csv'), dtype=str, usecols=['PARCREF', 'OPTCODE', 'STARTDAT', 'ENDDATE', 'UOM'])
    rows.append(pd.DataFrame({'parcref': es.PARCREF, 'fam': 'ES', 'code': es.OPTCODE, 'start': ts(es.STARTDAT),
                              'end': ts(es.ENDDATE), 'area_based': es.UOM.str.upper().isin(HA)}))
    h = pd.read_parquet(os.path.join(D, 'schemes', 'history', 'es_options_history.parquet'),
                        columns=['parcref', 'optcode', 'startdat', 'enddate', 'uom'])
    rows.append(pd.DataFrame({'parcref': h.parcref, 'fam': 'ES', 'code': h.optcode, 'start': h.startdat, 'end': h.enddate,
                              'area_based': h.uom.str.upper().isin(HA)}))
    o = pd.concat(rows, ignore_index=True)
    o['parcref'] = o.parcref.str.strip().str.upper()
    return o[o.parcref.str.match(PARCREF, na=False)]


def sfi_snapped(parcels):
    s = pd.read_csv(os.path.join(NAT, 'sfi_actions.csv'), dtype=str,
                    usecols=['option_code', 'contract_start', 'contract_end', 'uom_desc', 'x_bng', 'y_bng'])
    s['x'], s['y'] = pd.to_numeric(s.x_bng, errors='coerce'), pd.to_numeric(s.y_bng, errors='coerce')
    s = s[s.x.notna() & s.y.notna()]
    dist, idx = cKDTree(parcels[['x', 'y']].values).query(s[['x', 'y']].values, k=1)
    return pd.DataFrame({'parcref': parcels.parcref.values[idx], 'fam': 'SFI', 'code': s.option_code.values,
                         'start': ts(s.contract_start).values, 'end': ts(s.contract_end).values,
                         'area_based': s.uom_desc.str.upper().isin(HA).values, 'snap_m': dist.round(1)})


def main():
    p = pd.read_csv(os.path.join(NAT, 'rpa_parcel_points.csv'), dtype=str, usecols=['parcel_reference', 'x_bng', 'y_bng'])
    p = p.rename(columns={'parcel_reference': 'parcref'})
    p['x'], p['y'] = pd.to_numeric(p.x_bng, errors='coerce'), pd.to_numeric(p.y_bng, errors='coerce')
    p = p.dropna(subset=['x', 'y']).drop_duplicates('parcref')[['parcref', 'x', 'y']].reset_index(drop=True)

    o = options(); o['snap_m'] = 0.0
    sfi = sfi_snapped(p)
    allo = pd.concat([o, sfi], ignore_index=True)
    allo['start_year'] = allo.start.dt.year
    in_parcels = allo.parcref.isin(p.parcref)
    good = allo.snap_m <= SNAP_M

    t = p.set_index('parcref')
    for fam in ('CS', 'ES', 'SFI'):
        a = allo[(allo.fam == fam) & in_parcels]
        land = a[a.area_based & good]
        t[f'{fam}_land_first_start'] = land.groupby('parcref').start_year.min()
        t[f'{fam}_land_codes'] = land.groupby('parcref').code.agg(lambda s: ';'.join(sorted(set(s.dropna()))))
        t[f'{fam}_any'] = t.index.isin(a.parcref)
    t['nonarea_or_far_only'] = t.index.isin(allo[in_parcels].parcref)
    treated = t[['CS_land_first_start', 'SFI_land_first_start']].notna().any(axis=1)
    es_land = t.ES_land_first_start.notna()
    t['entry_year'] = t[['CS_land_first_start', 'SFI_land_first_start']].min(axis=1).astype('Int64')
    t['css_legacy'] = False
    css = glob.glob(os.path.join(D, 'schemes', 'snapshots', 'cs_agreements_2024_03', '*.shp'))
    if css:
        import geopandas as gpd
        poly = gpd.read_file(css[0])[['geometry']]
        pts = gpd.GeoDataFrame(index=t.index, geometry=gpd.points_from_xy(t.x, t.y), crs=27700)
        hit = gpd.sjoin(pts, poly.to_crs(27700), predicate='within', how='inner').index.unique()
        t.loc[hit, 'css_legacy'] = True
    t['parcel_group'] = np.select(
        [treated, es_land, ~t.nonarea_or_far_only],
        ['agreement', 'legacy ES', 'no agreement'], 'uncertain')
    t = t.drop(columns=['nonarea_or_far_only']).reset_index()
    os.makedirs(OUT, exist_ok=True)
    t.to_parquet(os.path.join(OUT, 'parcel_schemes.parquet'), index=False)

    snap = sfi.snap_m
    cnt = lambda s: s.value_counts().sort_index().rename_axis('').to_frame('parcels').to_markdown()
    lines = ['# Stage 0 · Parcel-level scheme table (counts only)', '',
             f'- RPA parcels (England): {len(p):,}',
             f'- Option records: CS {(allo.fam == "CS").sum():,}, ES {(allo.fam == "ES").sum():,} (live + history), '
             f'SFI {(allo.fam == "SFI").sum():,}; CS/ES parcel references found in the parcel register: '
             f'{allo[allo.fam != "SFI"].parcref.isin(p.parcref).mean():.1%}',
             f'- SFI snapping: median {snap.median():.0f} m; within {SNAP_M} m: {(snap <= SNAP_M).mean():.1%}', '',
             '## Parcel groups', '', cnt(t.parcel_group), '',
             f'- Parcels inside legacy Countryside Stewardship Scheme agreements (CSS, ended 2014): {t.css_legacy.sum():,} '
             f'(of which in the no agreement group: {(t.css_legacy & (t.parcel_group == "no agreement")).sum():,})', '',
             '## Entry year of agreement parcels (earliest area-based CS / SFI option)', '', cnt(t.entry_year.dropna()), '',
             'agreement = area-based CS or SFI option on the parcel; legacy ES = ES options only; no agreement = no option '
             'in any source; uncertain = only per-metre / per-item options, or SFI snapped from > 50 m. The live layers '
             'omit ended CS agreements and the ES history is truncated, so a few "no agreement" parcels were in a scheme '
             'earlier.']
    os.makedirs(os.path.dirname(SUMMARY), exist_ok=True)
    open(SUMMARY, 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
