"""U1 (wp2_resilience/results/u1_grassland_protocol.md, written 18 October 2026 before extraction): the short-baseline
tests and the field score on a 100,000-parcel sample of England's permanent grassland.

Input   shared/data/s2/gee_local_grass/s2_<square>_<year>.csv; shared/data/modis_parcels_grass/modis_<square>.csv
        shared/data/weather/{grass_era5_cell,cell_year_shocks_grass}.parquet; shared/data/parcels/grass_sample.parquet
Output  wp2_resilience/results/u1_grassland.md, .json (aggregates only)
"""
import glob, json, os, re, sys
import numpy as np, pandas as pd
import within_field_check as wf
import parcel_resilience as pr
import modis_long_baseline_check as mlb

ROOT = pr.ROOT
D = os.path.join(ROOT, 'shared', 'data')
RES = os.path.join(ROOT, 'wp2_resilience', 'results')
sys.path.insert(0, os.path.join(ROOT, 'shared', 'src')); sys.path.insert(0, os.path.join(ROOT, 'src'))
import build_s2_panel as b
import lender_score as ls

SHOCKS = os.path.join(D, 'weather', 'cell_year_shocks_grass.parquet')
REGION = {'North East (England)': 'North East', 'North West (England)': 'North West', 'East Midlands (England)': 'East Midlands',
          'West Midlands (England)': 'West Midlands', 'South East (England)': 'South East', 'South West (England)': 'South West',
          'East': 'East of England', 'Yorkshire and The Humber': 'Yorkshire and the Humber', 'London': 'London'}


def regions():
    import geopandas as gpd
    g = pd.read_parquet(os.path.join(D, 'parcels', 'grass_sample.parquet'))
    pts = gpd.GeoDataFrame(g, geometry=gpd.points_from_xy(g.x, g.y), crs=27700)
    itl = gpd.read_file(os.path.join(ROOT, 'data', 'raw', 'boundaries', 'itl1_2021_buc.geojson')).to_crs(27700)
    j = gpd.sjoin(pts, itl[['ITL121NM', 'geometry']], how='left', predicate='within')
    j = j.drop_duplicates('parcref')
    return pd.DataFrame({'parcref': j.parcref.values, 'region': j.ITL121NM.map(REGION).values, 'x': j.x.values, 'y': j.y.values})


def weather():
    cell = pd.read_parquet(os.path.join(D, 'weather', 'grass_era5_cell.parquet'))[['parcref', 'cell_id_data']]
    sh = pd.read_parquet(SHOCKS)[['cell_id', 'year', 'dry_shock', 'heat_shock']]
    sh['shock'] = sh.dry_shock.fillna(False).astype(bool) | sh.heat_shock.fillna(False).astype(bool)
    return cell, sh.rename(columns={'cell_id': 'cell_id_data'})[['cell_id_data', 'year', 'shock']]


def s2_panel():
    got = {}
    for f in glob.glob(os.path.join(D, 's2', 'gee_local_grass', 's2_*.csv')):
        m = re.search(r's2_(\d+_\d+)_(\d{4})\.csv$', f)
        got[(m.group(1), int(m.group(2)))] = f
    p = b.anomalies(b.metrics(b.load(got)))
    # secondary outcome: March-August mean of the half-monthly NDVI medians (>= 8 of 12), z against 2017-2020
    nd = p[[f'ndvi_p{k:02d}' for k in range(1, 13)]]
    p['ndvi_season'] = nd.mean(axis=1).where(nd.notna().sum(axis=1) >= 8)
    base = p[p.year.between(*b.BASE)].groupby('parcref').ndvi_season.agg(['mean', 'std', 'count'])
    base = base[base['count'] >= 2]
    p['ndvi_season_z'] = (p.ndvi_season - p.parcref.map(base['mean'])) / p.parcref.map(base['std'].clip(lower=0.02))
    p['S'] = p[['ndvi_july_z', 'ndvi_peak_z']].mean(axis=1).clip(-6, 6)
    p['S_season'] = p.ndvi_season_z.clip(-6, 6)
    return p[['parcref', 'year', 'S', 'S_season']], len(got)


def modis_S(base):
    m = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(os.path.join(D, 'modis_parcels_grass', 'modis_*.csv')))],
                  ignore_index=True).drop_duplicates('parcref')
    long = []
    for k in ('july', 'peak'):
        x = m.melt(id_vars='parcref', value_vars=[c for c in m.columns if c.startswith(k + '_')], var_name='v', value_name=k)
        x['year'] = x.v.str[-4:].astype(int); long.append(x[['parcref', 'year', k]].set_index(['parcref', 'year']))
    p = pd.concat(long, axis=1).reset_index()
    st = p[p.year.between(*base)].groupby('parcref')[['july', 'peak']].agg(['mean', 'std'])
    z = []
    for k in ('july', 'peak'):
        mu, sd = st[(k, 'mean')].reindex(p.parcref).values, st[(k, 'std')].reindex(p.parcref).values
        z.append((p[k].values - mu) / np.where(sd > 1e-4, sd, np.nan))
    return p[['parcref', 'year']].assign(S=np.clip(np.nanmean(np.vstack(z), axis=0), -6, 6))


def prep(s, cell, sh):
    """Panel for the WP2 tests: weather, lags and stress debt, as in modis_long_baseline_check.load."""
    p = s.merge(cell, on='parcref').merge(sh, on=['cell_id_data', 'year'], how='left')
    p['shock'] = p.shock.fillna(False).astype(bool)
    p = p.sort_values(['parcref', 'year']).reset_index(drop=True)
    p = wf.lags(p)
    p['D'] = pr.add_debt(p[['parcref', 'S']], 0.5); p['D_l1'] = p.groupby('parcref').D.shift(1)
    return p


def main():
    cell, sh = weather()
    reg = regions()
    s2, nfiles = s2_panel()
    mod_long, mod_short = modis_S((2001, 2016)), modis_S((2017, 2020))
    print('S2 square-years', nfiles, 'parcels', s2.parcref.nunique(), 'MODIS parcels', mod_long.parcref.nunique(), flush=True)
    tests = {}
    mlb.run(prep(s2[['parcref', 'year', 'S']], cell, sh), 'Sentinel-2 · short normal · 2017-2026', tests)
    mlb.run(prep(s2[['parcref', 'year', 'S_season']].rename(columns={'S_season': 'S'}), cell, sh), 'Sentinel-2 · short normal · season mean (secondary)', tests)
    pm = prep(mod_long, cell, sh)
    mlb.run(pm[pm.year >= 2002].copy(), 'MODIS · long normal · 2002-2026', tests)
    mlb.run(prep(mod_long[mod_long.year >= 2017], cell, sh), 'MODIS · long normal · 2017-2026', tests)
    print('WP2 tests done', flush=True)

    # field score: X1 design on grass
    s2w = s2[s2.year.between(2017, 2026)].merge(cell, on='parcref').merge(sh, on=['cell_id_data', 'year'], how='left')
    s2w['shock'] = s2w.shock.fillna(False).astype(bool)
    common = set(s2w.parcref) & set(mod_long.parcref)
    frame = s2w[s2w.parcref.isin(common)][['parcref', 'year', 'cell_id_data', 'shock', 'S']]
    versions = {'V0 · Sentinel-2, normal 2017–2020': frame}
    for lab, src in (('V1 · MODIS, normal 2017–2020', mod_short), ('V2 · MODIS, normal 2001–2016', mod_long)):
        versions[lab] = frame.drop(columns='S').merge(src, on=['parcref', 'year'], how='left')
    score, byyear = {}, {}
    for lab, f in versions.items():
        p = ls.features(f.copy(), reg=reg, shocks_file=SHOCKS)
        bt, _ = ls.backtest(p)
        summ = bt.groupby('model').mean(numeric_only=True).drop(columns='year')
        score[lab] = summ[['hit_next_auc', 'hit_next_lift', 'hit_next_base_rate', 'worst_next_auc']].round(4).to_dict('index')
        byyear[lab] = bt[bt.model == 'Transparent score (no fitting)'].set_index('year').hit_next_auc.round(4).to_dict()

    g = lambda k: tests[k]['coef']
    S2 = 'Sentinel-2 · short normal · 2017-2026'
    r1 = dict(pooled_minus_AH=round(g(f'{S2} | T1 | pooled') - g(f'{S2} | T1 | Anderson-Hsiao'), 4),
              placebo=round(g(f'{S2} | T1 | shuffled seasons (placebo)'), 4), placebo_p=tests[f'{S2} | T1 | shuffled seasons (placebo)']['p'])
    r1['replicates'] = bool(r1['pooled_minus_AH'] >= 0.05 and r1['placebo'] > 0 and r1['placebo_p'] < 0.01)
    ah = {k: v['coef'] for k, v in tests.items() if 'Anderson-Hsiao' in k and 'secondary' not in k}
    r2 = dict(anderson_hsiao=ah, no_material_carryover=bool(all(abs(v) <= 0.05 for v in ah.values())))
    tr = 'Transparent score (no fitting)'
    v1, v2 = score['V1 · MODIS, normal 2017–2020'][tr]['hit_next_auc'], score['V2 · MODIS, normal 2001–2016'][tr]['hit_next_auc']
    r3 = dict(v2_auc=v2, v1_minus_v2=round(v1 - v2, 4), usable=bool(v2 >= 0.60), robust=bool(v1 - v2 < 0.03))
    out = dict(sample=dict(s2_parcels=int(s2.parcref.nunique()), modis_parcels=int(mod_long.parcref.nunique()), common=len(common),
                           by_region=reg.region.value_counts(dropna=False).to_dict()),
               tests=tests, score=score, score_by_year=byyear, R1=r1, R2=r2, R3=r3)
    json.dump(out, open(os.path.join(RES, 'u1_grassland.json'), 'w'), indent=1, default=float)
    report(out)


def report(o):
    L = ['# U1: short-baseline tests and the field score on England\'s grassland', '',
         'Protocol: [u1_grassland_protocol.md](u1_grassland_protocol.md), written before extraction. Random sample of 100,000 '
         'permanent-grassland parcels (CROME PG01 in ≥ 80% of years, never cereal). Cell × season effects; errors clustered by '
         f"ERA5 cell. Parcels with Sentinel-2 values: {o['sample']['s2_parcels']:,}; with MODIS: {o['sample']['modis_parcels']:,}.", '',
         '## WP2 tests', '', '| Data | test | version | coefficient | SE | p | n |', '|---|---|---|---|---|---|---|']
    for k, v in o['tests'].items():
        a, t, c = k.split(' | ')
        if 'without' in c:
            continue
        L.append(f"| {a} | {t} | {c} | {v['coef']:+.3f} | {v['se']:.3f} | {v['p']:.3g} | {v['n']:,} |")
    L += ['', '## Field score (X1 design)', '', '| Version | model | AUC, hit hard next season | lift (top 20%) | base rate |', '|---|---|---|---|---|']
    for lab, r in o['score'].items():
        for m, v in r.items():
            L.append(f"| {lab} | {m} | {v['hit_next_auc']:.3f} | {v['hit_next_lift']:.2f} | {v['hit_next_base_rate']:.1%} |")
    L += ['', '| Season | ' + ' | '.join(o['score_by_year']) + ' |', '|---' * (len(o['score_by_year']) + 1) + '|']
    for y in sorted(next(iter(o['score_by_year'].values()))):
        L.append(f'| {y} | ' + ' | '.join(f"{o['score_by_year'][k][y]:.3f}" for k in o['score_by_year']) + ' |')
    r1, r2, r3 = o['R1'], o['R2'], o['R3']
    L += ['', '## Reading (rules fixed in advance)', '',
          f"- **R1, artefact on grass:** pooled − Anderson–Hsiao (T1, Sentinel-2) = {r1['pooled_minus_AH']:+.3f}; shuffled placebo "
          f"{r1['placebo']:+.3f} (p = {r1['placebo_p']:.2g}). " + ('**Replicates.**' if r1['replicates'] else '**Does not replicate.**'),
          '- **R2, carry-over on grass:** Anderson–Hsiao ' + '; '.join(f"{k.split(' | ')[0]} {k.split(' | ')[1]} {v:+.3f}" for k, v in r2['anderson_hsiao'].items())
          + '. ' + ('**No material carry-over** (all within ±0.05).' if r2['no_material_carryover'] else '**Not all within ±0.05**: reported as evidence of carry-over, with its sign.'),
          f"- **R3, field score on grass:** transparent-score AUC with the long normal {r3['v2_auc']:.3f} "
          + ('(usable, ≥ 0.60)' if r3['usable'] else '(below 0.60: not usable)') + f"; V1 − V2 = {r3['v1_minus_v2']:+.3f} "
          + ('(robust).' if r3['robust'] else '(not robust: the short normal inflates it).'),
          '', 'Limits: cutting and grazing move grass NDVI independently of weather (the season-mean outcome is the check); MODIS '
          'pixels mix neighbouring fields; a sample, not all grassland.']
    open(os.path.join(RES, 'u1_grassland.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
