"""Addendum 6 Part F, layers 2 and 3: merge the GFM tile-seasons and validate against EA Recorded Flood Outlines
(protocol: w3_z_addendum6_hazards_protocol.md, Part F and the record rows of 3 November 2026).

Registered validation: the share of GFM-flooded parcel-seasons whose parcel point lies inside an EA Recorded Flood
Outline of the same event. Same event: an outline starting in the same October-March winter; stricter: a GFM flood
day between the outline's start date and 7 days after its end date. Point and outline versions of GFM are reported.
Context (added by record row before running): the same share among observed, never-flooded parcel-seasons; and
GFM's observed share and flooded share among parcel-seasons inside a same-winter outline.

Output: wp3_elms_effect/data/w3_z_gfm_parcel_season.parquet, w3_z_gfm_events.parquet (private);
        wp3_elms_effect/results/w3_z_gfm_validation.md and .json (aggregates only; public).
Contains modified Copernicus Emergency Management Service information 2015-2026. EA data: Open Government Licence.
"""
import os, glob, json
import numpy as np, pandas as pd, geopandas as gpd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
GFM = os.path.join(ROOT, 'wp3_elms_effect', 'data', 'gfm')
DATA = os.path.join(ROOT, 'wp3_elms_effect', 'data')
RES = os.path.join(ROOT, 'wp3_elms_effect', 'results')
RFO = os.path.join(ROOT, 'shared', 'data', 'reference', 'risk', 'recorded_flood_outlines', 'Recorded_Flood_Outlines.gpkg')
SEASONS = range(2016, 2027)
LAG = pd.Timedelta(days=7)


def merge():
    c = pd.concat([pd.read_parquet(f) for f in sorted(glob.glob(os.path.join(GFM, 'E*T3_20??.parquet')))], ignore_index=True)
    c = c[c.prow.notna()].copy(); c['season'] = c.season.astype(int)
    e = pd.concat([pd.read_parquet(f) for f in sorted(glob.glob(os.path.join(GFM, 'E*T3_20??_events.parquet')))], ignore_index=True)
    e['date'] = pd.to_datetime(e.date)
    assert not c.duplicated(['parcref', 'season']).any(), 'a parcel-season appears in two tiles'
    c.to_parquet(os.path.join(DATA, 'w3_z_gfm_parcel_season.parquet'), index=False)
    e.to_parquet(os.path.join(DATA, 'w3_z_gfm_events.parquet'), index=False)
    return c, e


def ea_hits():
    """(parcref, season, start, end) for each parcel point inside an EA outline starting in an October-March winter."""
    o = gpd.read_file(RFO, columns=['rec_out_id', 'start_date', 'end_date'])
    o['season'] = np.where(o.start_date.dt.month >= 10, o.start_date.dt.year + 1, o.start_date.dt.year)
    o = o[o.start_date.dt.month.isin([10, 11, 12, 1, 2, 3]) & o.season.isin(SEASONS)]
    o['end_date'] = o.end_date.fillna(o.start_date)
    P = pd.read_parquet(os.path.join(ROOT, 'shared', 'data', 'parcels', 'parcel_panel.parquet'), columns=['parcref', 'x', 'y'])
    P = gpd.GeoDataFrame(P[['parcref']], geometry=gpd.points_from_xy(P.x, P.y), crs='EPSG:27700')
    h = gpd.sjoin(P, o.to_crs('EPSG:27700'), predicate='within')[['parcref', 'season', 'start_date', 'end_date']]
    return h, o


def main():
    c, e = merge()
    h, o = ea_hits()
    inside = h[['parcref', 'season']].drop_duplicates().assign(ea=True)
    c = c.merge(inside, on=['parcref', 'season'], how='left'); c['ea'] = c.ea.fillna(False).astype(bool)
    # stricter: a GFM flood day within [start, end + 7 days] of an outline containing the parcel
    s = e.merge(h, on=['parcref', 'season'])
    s = s[(s.date >= s.start_date) & (s.date <= s.end_date + LAG)][['parcref', 'season', 'version']].drop_duplicates()
    rows = []
    for ver, obs, fl in (('point', 'pt_obs_days', 'pt_flood_days'), ('outline', 'ol_obs_days', 'ol_flood_days')):
        d = c[c[obs].notna()] if ver == 'outline' else c
        strict = s[s.version == ver].assign(strict=True)
        d = d.merge(strict[['parcref', 'season', 'strict']], on=['parcref', 'season'], how='left')
        d['strict'] = d.strict.fillna(False).astype(bool)
        for season, g in list(d.groupby('season')) + [('all', d)]:
            ob, fd = g[obs] > 0, g[fl] > 0
            rows.append(dict(version=ver, season=season, parcel_seasons=len(g), observed_share=ob.mean(),
                             median_observed_days=float(g.loc[ob, obs].median()) if ob.any() else np.nan,
                             flooded=int(fd.sum()), flooded_share_of_observed=fd.sum() / max(ob.sum(), 1),
                             flooded_in_ea_same_winter=g.loc[fd, 'ea'].mean() if fd.any() else np.nan,
                             flooded_in_ea_strict=g.loc[fd, 'strict'].mean() if fd.any() else np.nan,
                             context_unflooded_observed_in_ea=g.loc[ob & ~fd, 'ea'].mean() if (ob & ~fd).any() else np.nan,
                             context_ea_parcels=int(g.ea.sum()),
                             context_ea_observed_share=ob[g.ea].mean() if g.ea.any() else np.nan,
                             context_ea_flooded_share_of_observed=fd[g.ea & ob].mean() if (g.ea & ob).any() else np.nan))
    R = pd.DataFrame(rows)
    ea_n = o.groupby('season').size().reindex(SEASONS, fill_value=0)
    json.dump(dict(rows=R.to_dict('records'), ea_outlines_per_winter=ea_n.to_dict(),
                   ea_outlines_with_parcels=int(h.groupby('season').size().sum())),
              open(os.path.join(RES, 'w3_z_gfm_validation.json'), 'w'), indent=1, default=float)
    fmt = lambda x, p=1: '' if pd.isna(x) else f'{100 * x:.{p}f}%'
    L = ['# Addendum 6 Part F: GFM observed flooding and its validation against EA Recorded Flood Outlines', '',
         'Protocol: [w3_z_addendum6_hazards_protocol.md](w3_z_addendum6_hazards_protocol.md), Part F and the record rows of '
         '3 November 2026. Winters are October–March, labelled by the March year. Aggregates only.', '',
         'Contains modified Copernicus Emergency Management Service information 2015–2026. EA Recorded Flood Outlines: '
         'Open Government Licence; a missing outline does not mean an area did not flood.', '']
    for ver in ('point', 'outline'):
        L += [f'## {ver.capitalize()} version', '',
              '| Winter | Parcel-seasons | Observed ≥1 day | Median observed days | Flooded ≥1 day | Flooded, of observed | '
              'Flooded inside same-winter EA outline | Stricter (date within outline + 7 d) | Context: observed, never flooded, inside EA outline | '
              'Context: EA-outline parcels observed | Context: EA-outline parcels flooded, of observed |',
              '|---|---|---|---|---|---|---|---|---|---|---|']
        for r in R[R.version == ver].itertuples():
            L.append(f'| {r.season} | {r.parcel_seasons:,} | {fmt(r.observed_share)} | {r.median_observed_days:.0f} | {r.flooded:,} | '
                     f'{fmt(r.flooded_share_of_observed, 2)} | {fmt(r.flooded_in_ea_same_winter)} | {fmt(r.flooded_in_ea_strict)} | '
                     f'{fmt(r.context_unflooded_observed_in_ea, 2)} | {fmt(r.context_ea_observed_share)} | '
                     f'{fmt(r.context_ea_flooded_share_of_observed)} |')
        L.append('')
    L += ['## EA outlines starting in each winter', '', '| Winter | Outlines |', '|---|---|'] + \
         [f'| {k} | {v:,} |' for k, v in ea_n.items()] + ['']
    open(os.path.join(RES, 'w3_z_gfm_validation.md'), 'w').write('\n'.join(L))
    print(R[R.season == 'all'].T)


if __name__ == '__main__':
    main()
