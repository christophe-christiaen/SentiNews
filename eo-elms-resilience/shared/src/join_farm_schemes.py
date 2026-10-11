"""Stage 0: link agri-environment agreements (ES, CS, SFI) to the farm list.

There is no shared identifier between Companies House and the scheme data, so the link is spatial:
  1. options are grouped into agreements (ES: AGREF, CS: CONTRACT_ID, SFI: app_id); each agreement is located at its
     holding point (ES, where published) or at the median of its parcel points (CS, SFI);
  2. each agreement is assigned to the NEAREST farm within LINK_M metres (one farm per agreement, so neighbouring
     farms do not share an agreement); farms with office-like or agent addresses are not linked (their point is not
     the farm);
  3. separately, every farm gets the scheme intensity around it (options and agreements within RING_M), which does
     not depend on ownership and is robust to the link problem;
  4. analysis groups: 'agreement' (strong link), 'no agreement' (nothing assigned), 'uncertain' (candidate link only,
     kept out of both arms). Most farms are expected to have no agreement; no link is forced.

Input   shared/data/farms/farms_england.csv
        shared/data/schemes/national/{es_options,cs_options,sfi_actions}.csv     (live agreements to 2026)
        shared/data/schemes/history/es_options_history.parquet                   (ELMS_all.csv, ES 2006-2014 starts)
Output  shared/data/farms/agreements.parquet           one row per agreement: scheme, dates, location, options
        shared/data/farms/farm_scheme_links.csv         farm x agreement candidate links with distance and class
        shared/data/farms/farm_schemes.csv              one row per farm: linked agreements and local intensity
        shared/results/farm_schemes_summary.md          counts only (safe to commit)
"""
import os
import numpy as np, pandas as pd
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
D = os.path.join(ROOT, 'shared', 'data')
NAT = os.path.join(D, 'schemes', 'national')
OUT = os.path.join(D, 'farms')
SUMMARY = os.path.join(ROOT, 'shared', 'results', 'farm_schemes_summary.md')
LINK_M = 1000          # an agreement is linked to the nearest eligible farm within this distance
STRONG_M = 500         # links this close are 'strong' (agreement group); chosen cutoff
RING_M = 1000          # radius for local scheme intensity
LINKABLE = {'farm-like', 'unclear'}


def ts(s):
    """Dates arrive as epoch ms (ES), YYYYMMDD (CS), ISO (SFI) or m/d/Y (ELMS_all)."""
    s = pd.Series(s)
    if pd.api.types.is_datetime64_any_dtype(s):
        return s
    num = pd.to_numeric(s, errors='coerce')
    out = pd.to_datetime(num.where(num > 1e11), unit='ms', errors='coerce')
    ymd = pd.to_datetime(s.where(num.between(19000101, 21001231)).astype('string').str[:8], format='%Y%m%d', errors='coerce')
    iso = pd.to_datetime(s.where(num.isna()), errors='coerce', utc=True).dt.tz_localize(None)
    return out.fillna(ymd).fillna(iso)


def agg_agreements(d, key, scheme, start, end, code, x, y, hx=None, hy=None, area=None, source=''):
    d = d.copy()
    d['_start'], d['_end'] = ts(d[start]), ts(d[end])
    for c in (x, y) + ((hx, hy) if hx else ()):
        d[c] = pd.to_numeric(d[c], errors='coerce'); d.loc[d[c] <= 0, c] = np.nan
    g = d.groupby(key)
    a = pd.DataFrame({
        'scheme_family': source, 'scheme': g[scheme].first(),
        'start': g['_start'].min(), 'end': g['_end'].max(), 'n_options': g.size(),
        'option_codes': g[code].agg(lambda s: ';'.join(sorted(set(map(str, s.dropna())))[:60])),
        'parcel_x': g[x].median(), 'parcel_y': g[y].median()})
    if area:
        a['option_area_ha'] = g[area].apply(lambda s: pd.to_numeric(s, errors='coerce').sum())
    if hx:
        a['hold_x'], a['hold_y'] = g[hx].median(), g[hy].median()
    a.index.name = 'agreement_id'
    a = a.reset_index()
    a['agreement_id'] = source + ':' + a.agreement_id.astype(str)
    a['x'] = a.get('hold_x', a.parcel_x).fillna(a.parcel_x) if 'hold_x' in a else a.parcel_x
    a['y'] = a.get('hold_y', a.parcel_y).fillna(a.parcel_y) if 'hold_y' in a else a.parcel_y
    a['location'] = np.where(a.get('hold_x', pd.Series(np.nan, index=a.index)).notna(), 'holding', 'parcel median')
    return a


def load_agreements():
    parts = []
    hist = pd.read_parquet(os.path.join(D, 'schemes', 'history', 'es_options_history.parquet'))
    parts.append(agg_agreements(hist, 'agref', 'scheme', 'startdat', 'enddate', 'optcode', 'parcelx', 'parcely',
                                'holdx', 'holdy', 'areaha', source='ES'))
    fn = os.path.join(NAT, 'es_options.csv')
    if os.path.exists(fn):
        es = pd.read_csv(fn, dtype=str, low_memory=False)
        es_x = 'PARCELX' if 'PARCELX' in es else 'x_bng'
        a = agg_agreements(es, 'AGREF', 'SCHEME', 'STARTDAT', 'ENDDATE', 'OPTCODE', es_x, es_x.replace('X', 'Y'),
                           'HOLDX', 'HOLDY', 'AREAHA', source='ES')
        parts.append(a[~a.agreement_id.isin(parts[0].agreement_id)])     # history first; national adds the rest
    fn = os.path.join(NAT, 'cs_options.csv')
    if os.path.exists(fn):
        cs = pd.read_csv(fn, dtype=str, low_memory=False)
        parts.append(agg_agreements(cs, 'CONTRACT_ID', 'CS_TYPE', 'STARTDATE', 'ENDDATE', 'OPTION_CODE', 'x_bng', 'y_bng',
                                    area='SUM_GIS_HA', source='CS'))
    fn = os.path.join(NAT, 'sfi_actions.csv')
    if os.path.exists(fn):
        sfi = pd.read_csv(fn, dtype=str, low_memory=False)
        parts.append(agg_agreements(sfi, 'app_id', 'scheme', 'contract_start', 'contract_end', 'option_code', 'x_bng',
                                    'y_bng', area='area', source='SFI'))
    a = pd.concat(parts, ignore_index=True)
    a = a[a.x.notna() & a.y.notna()]
    a['start_year'] = a.start.dt.year.astype('Int64'); a['end_year'] = a.end.dt.year.astype('Int64')
    return a


def option_points():
    """All option points (for local intensity): scheme family, x, y, start year."""
    pts = []
    h = pd.read_parquet(os.path.join(D, 'schemes', 'history', 'es_options_history.parquet'), columns=['parcelx', 'parcely', 'startdat'])
    pts.append(pd.DataFrame({'fam': 'ES', 'x': h.parcelx, 'y': h.parcely, 'start': h.startdat}))
    for fam, fn, x, y, st in (('ES', 'es_options.csv', 'PARCELX', 'PARCELY', 'STARTDAT'), ('CS', 'cs_options.csv', 'x_bng', 'y_bng', 'STARTDATE'),
                              ('SFI', 'sfi_actions.csv', 'x_bng', 'y_bng', 'contract_start')):
        p = os.path.join(NAT, fn)
        if os.path.exists(p):
            d = pd.read_csv(p, usecols=lambda c: c in (x, y, st), dtype=str)
            pts.append(pd.DataFrame({'fam': fam, 'x': pd.to_numeric(d[x], errors='coerce'), 'y': pd.to_numeric(d[y], errors='coerce'),
                                     'start': ts(d[st])}))
    p = pd.concat(pts, ignore_index=True)
    return p[(p.x > 0) & (p.y > 0)]


def main():
    farms = pd.read_csv(os.path.join(OUT, 'farms_england.csv'))
    ag = load_agreements()
    ag.to_parquet(os.path.join(OUT, 'agreements.parquet'), index=False)

    # 1. agreement -> nearest linkable farm
    lf = farms[farms.address_kind.isin(LINKABLE)].reset_index(drop=True)
    tree = cKDTree(lf[['x_bng', 'y_bng']].values)
    dist, idx = tree.query(ag[['x', 'y']].values, k=1, distance_upper_bound=LINK_M)
    ok = np.isfinite(dist)
    links = ag.loc[ok, ['agreement_id', 'scheme_family', 'scheme', 'start_year', 'end_year', 'n_options', 'option_codes', 'location']].copy()
    links.insert(0, 'farm_id', lf.farm_id.values[idx[ok]])
    links['distance_m'] = dist[ok].round(0)
    links['link_class'] = np.where(links.distance_m <= STRONG_M, 'strong', 'candidate')
    links.sort_values(['farm_id', 'start_year']).to_csv(os.path.join(OUT, 'farm_scheme_links.csv'), index=False)

    # 2. per-farm summary of linked agreements
    f = farms[['farm_id', 'company_name', 'postcode', 'x_bng', 'y_bng', 'address_kind', 'cereals', 'mixed_farming']].copy()
    f['linkable'] = f.address_kind.isin(LINKABLE)
    for fam in ('ES', 'CS', 'SFI'):
        l = links[links.scheme_family == fam].groupby('farm_id')
        s = pd.DataFrame({f'{fam}_agreements': l.size(), f'{fam}_first_start': l.start_year.min(),
                          f'{fam}_last_end': l.end_year.max(), f'{fam}_nearest_m': l.distance_m.min()})
        f = f.merge(s, left_on='farm_id', right_index=True, how='left')
        f[f'{fam}_agreements'] = f[f'{fam}_agreements'].fillna(0).astype(int)
    f['any_agreement'] = f[['ES_agreements', 'CS_agreements', 'SFI_agreements']].sum(axis=1) > 0
    f['first_entry_year'] = f[['ES_first_start', 'CS_first_start', 'SFI_first_start']].min(axis=1).astype('Int64')
    best = links.groupby('farm_id').distance_m.min()
    f['link_class'] = np.select([f.farm_id.map(best) <= STRONG_M, f.farm_id.map(best).notna()], ['strong', 'candidate'], 'none')
    f.loc[~f.linkable, 'link_class'] = 'not linked (office address)'
    # analysis groups: no link is forced; uncertain farms are kept out of both arms of the comparison
    f['group'] = f.link_class.map({'strong': 'agreement', 'none': 'no agreement', 'candidate': 'uncertain'}) \
        .fillna('excluded (office address)')

    # 3. local scheme intensity (all farms, ownership-free)
    pts = option_points()
    for fam in ('ES', 'CS', 'SFI'):
        p = pts[pts.fam == fam]
        if len(p) == 0:
            continue
        t = cKDTree(p[['x', 'y']].values)
        nb = t.query_ball_point(f[['x_bng', 'y_bng']].values, r=RING_M)
        f[f'{fam}_options_within_1km'] = [len(i) for i in nb]
        sy = p.start.dt.year.values
        f[f'{fam}_first_start_within_1km'] = [int(np.nanmin(sy[i])) if len(i) and np.isfinite(sy[i]).any() else pd.NA for i in nb]
    f.to_csv(os.path.join(OUT, 'farm_schemes.csv'), index=False)

    # summary (counts only)
    lk = f[f.linkable]
    t = lambda s: s.value_counts().sort_index().rename_axis('').to_frame('').to_markdown()
    lines = ['# Stage 0 · Farms linked to agri-environment agreements (counts only)', '',
             f'- Agreements located: {len(ag):,} (' + ', '.join(f'{k} {v:,}' for k, v in ag.scheme_family.value_counts().items()) + ')',
             f'- English farms: {len(f):,}; linkable (farm-like or unclear address): {len(lk):,}',
             f'- Linkable farms with at least one agreement within {LINK_M} m (nearest-farm assignment): '
             f'{lk.any_agreement.sum():,} ({lk.any_agreement.mean():.0%}); strong links (≤{STRONG_M} m): '
             f'{(lk.link_class == "strong").sum():,}', '',
             '## Analysis groups (agreement vs no agreement)', '', t(f.group), '',
             f'- **agreement**: an agreement located within {STRONG_M} m of the farm and nearer to it than to any other listed '
             'farm; **no agreement**: no agreement assigned within 1 km; **uncertain** (an agreement 500 m–1 km away) and '
             'office addresses are left out of both groups.',
             '- By scheme (linkable farms with ≥1 linked agreement): ' + ', '.join(
                 f'{fam} {(lk[f"{fam}_agreements"] > 0).sum():,}' for fam in ('ES', 'CS', 'SFI')),
             f'- Farms with any scheme option within {RING_M} m (all farms): ' + ', '.join(
                 f'{fam} {(f[f"{fam}_options_within_1km"] > 0).mean():.0%}' for fam in ('ES', 'CS', 'SFI') if f'{fam}_options_within_1km' in f), '',
             '## First entry year of linked farms (earliest agreement start)', '', t(lk.first_entry_year.dropna()), '',
             '## Linked agreements by scheme family and start year', '',
             links.pivot_table(index='start_year', columns='scheme_family', values='agreement_id', aggfunc='count',
                               fill_value=0).to_markdown(), '',
             'Links are spatial: an agreement is assigned to the nearest listed farm within 1 km. Many agreement holders '
             'are not in the Companies House list (sole traders, partnerships), so a candidate link can belong to a '
             'neighbour. Treat strong links as likely and candidate links as plausible; validate a sample by hand.']
    os.makedirs(os.path.dirname(SUMMARY), exist_ok=True)
    open(SUMMARY, 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
