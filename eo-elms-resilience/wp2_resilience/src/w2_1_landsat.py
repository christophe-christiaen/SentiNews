"""W2-1 (wp2_resilience/results/w2_1_landsat_protocol.md, written before any Landsat value was extracted): the WP2
carry-over tests with Landsat 30 m field-centre NDVI. Same tests and estimators as modis_long_baseline_check.py.

Versions: L-long (normal 2001-2016; tests 2002-2026 and 2017-2026); L-short (normal 2017-2020; tests 2017-2026);
L7 only (normal 2001-2016; tests 2002-2023). A field needs >= 8 clear baseline seasons (long) or >= 3 (short).

Input   shared/data/landsat_parcels/landsat_<square>.csv; weather as in the MODIS test
Output  wp2_resilience/results/w2_1_landsat.md, .json
"""
import glob, json, os
import numpy as np, pandas as pd
import within_field_check as wf
import parcel_resilience as pr
import modis_long_baseline_check as mlb

D, RES = pr.D, os.path.join(pr.ROOT, 'wp2_resilience', 'results')


def load(base, prefix='', min_seasons=8, years=range(2001, 2027)):
    m = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(os.path.join(D, 'landsat_parcels', 'landsat_*.csv')))], ignore_index=True)
    m = m.drop_duplicates('parcref')
    long = []
    for k in ('july', 'peak'):
        cols = [f'{prefix}{k}_{y}' for y in years if f'{prefix}{k}_{y}' in m.columns]
        x = m.melt(id_vars='parcref', value_vars=cols, var_name='v', value_name=k)
        x['year'] = x.v.str[-4:].astype(int); long.append(x[['parcref', 'year', k]].set_index(['parcref', 'year']))
    p = pd.concat(long, axis=1).reset_index()
    b = p[p.year.between(*base)]
    st = b.groupby('parcref')[['july', 'peak']].agg(['mean', 'std', 'count'])
    for k in ('july', 'peak'):
        ok = st[(k, 'count')] >= min_seasons
        mu = st[(k, 'mean')].where(ok).reindex(p.parcref).values
        sd = st[(k, 'std')].where(ok).reindex(p.parcref).values
        p[k + '_z'] = (p[k] - mu) / np.where(sd > 1e-4, sd, np.nan)
    p['S'] = p[['july_z', 'peak_z']].mean(axis=1).clip(-6, 6)
    cell = pd.read_parquet(os.path.join(D, 'weather', 'parcel_era5_cell.parquet'))[['parcref', 'cell_id_data']]
    sh = pd.read_parquet(os.path.join(D, 'weather', 'cell_year_shocks.parquet'))[['cell_id', 'year', 'dry_shock', 'heat_shock']]
    sh['shock'] = sh.dry_shock | sh.heat_shock
    p = p.merge(cell, on='parcref').merge(sh[['cell_id', 'year', 'shock']].rename(columns={'cell_id': 'cell_id_data'}), on=['cell_id_data', 'year'], how='left')
    p['shock'] = p.shock.fillna(False).astype(bool)
    p = p.sort_values(['parcref', 'year']).reset_index(drop=True)
    p = wf.lags(p)
    p['D'] = pr.add_debt(p[['parcref', 'S']], 0.5); p['D_l1'] = p.groupby('parcref').D.shift(1)
    return p


def main():
    out = {}
    pl = load((2001, 2016))
    print('L-long parcels with a usable normal:', pl.dropna(subset=['S']).parcref.nunique(), flush=True)
    mlb.run(pl[pl.year >= 2002].copy(), 'L-long · 2002-2026', out)
    mlb.run(pl[pl.year >= 2017].copy(), 'L-long · 2017-2026', out)
    ps = load((2017, 2020), min_seasons=3)
    mlb.run(ps[ps.year >= 2017].copy(), 'L-short · 2017-2026', out)
    p7 = load((2001, 2016), prefix='l7', years=range(2001, 2024))
    mlb.run(p7[p7.year >= 2002].copy(), 'L7 only · 2002-2023', out)
    modis = json.load(open(os.path.join(RES, 'modis_long_baseline_check.json')))['tests']
    g = lambda k: out[k]['coef']
    ah = {t: g(f'L-long · 2002-2026 | {t} | Anderson-Hsiao') for t in ('T1', 'T2')}
    r1 = dict(anderson_hsiao=ah, confirms_modis=bool(all(abs(v) <= 0.05 for v in ah.values())))
    s = 'L-short · 2017-2026'
    r2 = dict(pooled_minus_AH=g(f'{s} | T1 | pooled') - g(f'{s} | T1 | Anderson-Hsiao'), placebo=g(f'{s} | T1 | shuffled seasons (placebo)'),
              placebo_p=out[f'{s} | T1 | shuffled seasons (placebo)']['p'])
    r2['artefact_replicates'] = bool(r2['pooled_minus_AH'] >= 0.05 and r2['placebo'] > 0 and r2['placebo_p'] < 0.01)
    mod_ah = modis['2002-2026 | T1 | Anderson-Hsiao']['coef']
    r3 = dict(landsat_AH_T1=ah['T1'], modis_AH_T1=mod_ah, pixel_mixing_mattered=bool(abs(ah['T1'] - mod_ah) > 0.05))
    l7 = g('L7 only · 2002-2023 | T1 | Anderson-Hsiao')
    r4 = dict(l7_AH_T1=l7, sensor_mix_flagged=bool(abs(l7 - ah['T1']) > 0.05))
    out_all = {'tests': out, 'reading': {'R1': r1, 'R2': r2, 'R3': r3, 'R4': r4},
               'parcels': {'long': int(pl.dropna(subset=['S']).parcref.nunique()), 'short': int(ps.dropna(subset=['S']).parcref.nunique()),
                           'l7': int(p7.dropna(subset=['S']).parcref.nunique())}}
    json.dump(out_all, open(os.path.join(RES, 'w2_1_landsat.json'), 'w'), indent=1, default=float)
    L = ['# W2-1: the carry-over tests with a Landsat 30 m long baseline', '',
         'Protocol: [w2_1_landsat_protocol.md](w2_1_landsat_protocol.md), written before any Landsat value was extracted. '
         'Field-centre 30 m pixel; Landsat 5, 7, 8, 9 (no cross-sensor coefficients; cell × season effects); errors clustered by '
         f"ERA5 cell. Parcels with a usable normal: long {out_all['parcels']['long']:,}, short {out_all['parcels']['short']:,}, "
         f"Landsat 7 only {out_all['parcels']['l7']:,}.", '',
         '| Version | test | estimator | coefficient | SE | p | n |', '|---|---|---|---|---|---|---|']
    for k, v in out.items():
        a, t, c = k.split(' | ')
        if 'without' in c:
            continue
        L.append(f"| {a} | {t} | {c} | {v['coef']:+.3f} | {v['se']:.3f} | {v['p']:.3g} | {v['n']:,} |")
    L += ['', '## Reading (rules fixed in advance)', '',
          f"- **Confirms MODIS** (Anderson–Hsiao T1 and T2 within ±0.05, long normal): T1 {ah['T1']:+.3f}, T2 {ah['T2']:+.3f} → "
          + ('**yes**.' if r1['confirms_modis'] else '**no**: reported as carry-over.'),
          f"- **Artefact on Landsat** (short normal): pooled − Anderson–Hsiao = {r2['pooled_minus_AH']:+.3f}; placebo {r2['placebo']:+.3f} "
          f"(p = {r2['placebo_p']:.2g}) → " + ('**replicates**.' if r2['artefact_replicates'] else '**does not replicate**.'),
          f"- **Pixel mixing**: Landsat Anderson–Hsiao T1 {ah['T1']:+.3f} vs MODIS {mod_ah:+.3f} → "
          + ('**mattered** (differ by more than 0.05).' if r3['pixel_mixing_mattered'] else 'did not matter (within 0.05).'),
          f"- **Sensor mix (sensitivity)**: Landsat 7 only T1 {l7:+.3f} → " + ('**flagged** as a limit.' if r4['sensor_mix_flagged'] else 'not flagged.'),
          '', 'Limits: Landsat 7 alone is patchy in cloudy western summers (2–3 overpasses in the window); 30 m field-centre pixels '
          'can still touch field edges in small fields.']
    open(os.path.join(RES, 'w2_1_landsat.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
