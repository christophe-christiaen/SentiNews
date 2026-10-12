"""Sentinel-1 parcel x season panel from the per-orbit, angle-normalised extraction (gee_s1_orbit.py). Quality summary
only (no scheme-group comparisons).

Months m01 = October ... m11 = August of season Y (October Y-1 to August Y); winter = December-February (m03-m05).
For each parcel, orbit direction (asc / desc) and month, the anomaly is gamma0 minus the parcel's own mean for that
direction and month over all seasons, so changes in which satellites flew (1A + 1B to Dec 2021, 1A alone, 1A + 1C from
2025) do not look like changes in the soil. Winter anomaly = mean of the available direction-month anomalies.
Robustness: the same using only months where every pass came from Sentinel-1A.
Season 2026: Sentinel-1C passes read darker than 1A over these fields (first build: a very wet winter came out
-0.35 dB), so 2026 uses the Sentinel-1A-only extraction (shared/data/s1/gee_orbit_1A/) wherever it exists; every
other season mixes only 1A and 1B (to 2021) or is 1A alone (2022-2025).

Checks: within each ERA5 cell, across seasons, does the winter VV anomaly follow (a) October-March rainfall anomaly
and (b) December-February topsoil moisture (ERA5-Land swvl1) anomaly? The blended first run gave r = 0.10 for (a).

Input   shared/data/s1/gee_orbit/s1o_<square>_<season>.csv; shared/data/weather/*
Output  shared/data/s1/s1_orbit_parcel_season.parquet; shared/results/s1_orbit_panel_quality.md
"""
import glob, os, re
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
D = os.path.join(ROOT, 'shared', 'data')
SRC = os.path.join(D, 's1', 'gee_orbit')
SRC_1A = os.path.join(D, 's1', 'gee_orbit_1A')
OUT = os.path.join(D, 's1', 's1_orbit_parcel_season.parquet')
SUMMARY = os.path.join(ROOT, 'shared', 'results', 's1_orbit_panel_quality.md')
WINTER = (3, 4, 5)
DIRS = ('asc', 'desc')


def load():
    files = {}
    for src, tag in ((SRC, 'all passes'), (SRC_1A, 'Sentinel-1A only')):
        for f in sorted(glob.glob(os.path.join(src, 's1o_*.csv'))):
            m = re.search(r's1o_(\d+_\d+)_(\d{4})\.csv$', f)
            if m and (tag == 'all passes' or int(m.group(2)) == 2026):
                files[(m.group(1), int(m.group(2)))] = (f, tag)        # 1A-only replaces 2026 where present
    parts = []
    for (sq, y), (f, tag) in sorted(files.items()):
        d = pd.read_csv(f); d['square'], d['season'], d['source'] = sq, y, tag; parts.append(d)
    p = pd.concat(parts, ignore_index=True).drop_duplicates(['parcref', 'season'])
    num = [c for c in p.columns if re.match(r'(vv|vh|n|a)_(asc|desc)_m\d\d$', c)]
    p[num] = p[num].apply(pd.to_numeric, errors='coerce').astype('float32')
    return p, len(parts)


def anomalies(p):
    g = p.groupby('parcref')
    out = {}
    for pol in ('vv', 'vh'):
        an, an_a = [], []
        for d in DIRS:
            for k in WINTER:
                c = f'{pol}_{d}_m{k:02d}'
                a = p[c] - g[c].transform('mean')
                an.append(a)
                only_a = p[f'a_{d}_m{k:02d}'] >= 0.999
                ca = p[c].where(only_a)
                an_a.append(ca - ca.groupby(p.parcref).transform('mean'))
        out[f'winter_{pol}_anom'] = pd.concat(an, axis=1).mean(axis=1)
        out[f'winter_{pol}_anom_1A'] = pd.concat(an_a, axis=1).mean(axis=1)
    out['winter_passes'] = p[[f'n_{d}_m{k:02d}' for d in DIRS for k in WINTER]].sum(axis=1)
    out['winter_share_1A'] = p[[f'a_{d}_m{k:02d}' for d in DIRS for k in WINTER]].mean(axis=1)
    return pd.DataFrame(out).astype('float32')


def weather():
    W = os.path.join(D, 'weather')
    s = pd.read_parquet(os.path.join(W, 'cell_year_shocks.parquet'))[['cell_id', 'year', 'winter_anom_pct', 'wet_shock']]
    m = pd.read_parquet(os.path.join(W, 'era5land_monthly.parquet'))[['cell_id', 'year', 'month', 'swvl1']]
    m['season'] = np.where(m.month == 12, m.year + 1, m.year)
    w = m[m.month.isin([12, 1, 2])].groupby(['cell_id', 'season']).swvl1.mean().rename('sm_djf').reset_index()
    base = w[w.season.between(1992, 2020)].groupby('cell_id').sm_djf.agg(['mean', 'std'])
    w = w.join(base, on='cell_id')
    w['sm_djf_z'] = (w.sm_djf - w['mean']) / w['std']
    s = s.rename(columns={'year': 'season'}).merge(w[['cell_id', 'season', 'sm_djf_z']], on=['cell_id', 'season'], how='left')
    return s.rename(columns={'cell_id': 'cell_id_data'})


def within_cell_r(df, x, y):
    cs = df.groupby(['cell_id_data', 'season']).agg(a=(x, 'mean'), b=(y, 'first')).dropna()
    cs = cs - cs.groupby(level='cell_id_data').transform('mean')
    return float(cs.a.corr(cs.b)), len(cs)


def main():
    p, nfiles = load()
    src = p.groupby('season').source.agg(lambda v: ', '.join(sorted(set(v))))
    p = pd.concat([p[['parcref', 'square', 'season']], anomalies(p)], axis=1)
    cell = pd.read_parquet(os.path.join(D, 'weather', 'parcel_era5_cell.parquet'))[['parcref', 'cell_id_data']]
    p = p.merge(cell, on='parcref', how='left').merge(weather(), on=['cell_id_data', 'season'], how='left')
    p.to_parquet(OUT, index=False)
    checks = {(x, y): within_cell_r(p, x, y) for x in ('winter_vv_anom', 'winter_vv_anom_1A', 'winter_vh_anom')
              for y in ('winter_anom_pct', 'sm_djf_z')}
    q = p.groupby('season').agg(parcels=('parcref', 'size'), passes=('winter_passes', 'median'), a=('winter_share_1A', 'mean'),
                                vv=('winter_vv_anom', 'median'), vv1a=('winter_vv_anom_1A', 'median'),
                                rain=('winter_anom_pct', 'median'), sm=('sm_djf_z', 'median'), wet=('wet_shock', 'mean'))
    name = {'winter_anom_pct': 'Oct–Mar rainfall anomaly', 'sm_djf_z': 'Dec–Feb topsoil moisture (ERA5-Land)'}
    L = ['# Sentinel-1 per-orbit panel: data quality (no scheme-group comparisons)', '',
         f'- Square-season files: {nfiles} (of 790); parcel-seasons: {len(p):,}; parcels: {p.parcref.nunique():,}',
         '- Gamma0 (angle-normalised), anomalies within parcel × orbit direction × month; winter = December–February.',
         '- Season 2026 from Sentinel-1A passes only (' + src.get(2026, 'n/a') + '); 1C passes read darker than 1A.', '',
         '## Does radar winter brightness follow the weather? (within each ERA5 cell, across seasons)', '',
         '| Radar measure | weather measure | correlation | cell-seasons |', '|---|---|---|---|'] + \
        [f'| {x} | {name[y]} | {r:+.2f} | {n:,} |' for (x, y), (r, n) in checks.items()] + \
        ['', 'First run (all passes blended, no angle or orbit handling): r = +0.10 with October–March rainfall.', '',
         '## By season', '',
         '| Season | parcels | median winter passes | share of passes from 1A | median VV anomaly (dB) | same, 1A-only months | median rain vs normal (%) | median topsoil moisture z | % parcels in wet shock |',
         '|---|---|---|---|---|---|---|---|---|'] + \
        [f'| {y} | {int(r.parcels):,} | {r.passes:.0f} | {r.a:.0%} | {r.vv:+.2f} | {r.vv1a:+.2f} | {r.rain:+.0f} | {r.sm:+.2f} | {100 * r.wet:.0f} |'
         for y, r in q.iterrows()]
    open(SUMMARY, 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
