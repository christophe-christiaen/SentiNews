"""Paper 2, the long-baseline test: with each field's normal from 16 seasons (MODIS 2001-2016) instead of 4, is
there any real season-to-season carry-over at field level? Design written on 12 October 2026, before any MODIS
parcel value was looked at.

Stress index S = mean of the July and peak NDVI z-scores against the field's own 2001-2016 seasons (same windows as
the Sentinel-2 index), clipped to +-6. Shocks: dry or heat shock for the field's ERA5-Land cell (unchanged).
Tests, all with cell x season effects and errors clustered by ERA5 cell:
  T1 S_t on S_t-1; T2 the same in shock seasons; T3 rebound S_t+1 - S_t on debt D_t-1 controlling S_t.
Versions: as in the earlier tests (pooled); field fixed effects; Anderson-Hsiao (dS_t-1 instrumented by S_t-2);
season-shuffling placebo; T2 leaving out one shock season at a time; all of it for 2002-2026 and for 2017-2026 (the
Sentinel-2 era, for direct comparison). Calibration: simulation of this design (16-season normal, 26 seasons) with
known carry-over, as in baseline_artefact_sim.py.
Limitation: MODIS pixels are 250 m (about 6 ha); small fields share pixels and their values mix neighbours.

Input   shared/data/modis_parcels/modis_<square>.csv; shared/data/weather/{cell_year_shocks,parcel_era5_cell}.parquet
Output  wp2_resilience/results/modis_long_baseline_check.md, .json
"""
import glob, json, os
import numpy as np, pandas as pd
import within_field_check as wf
import parcel_resilience as pr

D = pr.D
RES = os.path.join(pr.ROOT, 'wp2_resilience', 'results')
RNG = np.random.default_rng(16)
BASE = (2001, 2016)


def load():
    m = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(os.path.join(D, 'modis_parcels', 'modis_*.csv')))], ignore_index=True)
    m = m.drop_duplicates('parcref')
    long = []
    for k in ('july', 'peak'):
        x = m.melt(id_vars='parcref', value_vars=[c for c in m.columns if c.startswith(k + '_')], var_name='v', value_name=k)
        x['year'] = x.v.str[-4:].astype(int); long.append(x[['parcref', 'year', k]].set_index(['parcref', 'year']))
    p = pd.concat(long, axis=1).reset_index()
    base = p[p.year.between(*BASE)].groupby('parcref')[['july', 'peak']].agg(['mean', 'std'])
    for k in ('july', 'peak'):
        mu, sd = base[(k, 'mean')].reindex(p.parcref).values, base[(k, 'std')].reindex(p.parcref).values
        p[k + '_z'] = (p[k] - mu) / np.where(sd > 1e-4, sd, np.nan)
    p['S'] = p[['july_z', 'peak_z']].mean(axis=1).clip(-6, 6)
    cell = pd.read_parquet(os.path.join(D, 'weather', 'parcel_era5_cell.parquet'))[['parcref', 'cell_id_data']]
    sh = pd.read_parquet(os.path.join(D, 'weather', 'cell_year_shocks.parquet'))[['cell_id', 'year', 'dry_shock', 'heat_shock']]
    sh['shock'] = sh.dry_shock | sh.heat_shock
    p = p.merge(cell, on='parcref').merge(sh[['cell_id', 'year', 'shock']].rename(columns={'cell_id': 'cell_id_data'}),
                                          on=['cell_id_data', 'year'], how='left')
    p['shock'] = p.shock.fillna(False).astype(bool)
    p = p.sort_values(['parcref', 'year']).reset_index(drop=True)
    p = wf.lags(p)
    p['D'] = pr.add_debt(p[['parcref', 'S']], 0.5); p['D_l1'] = p.groupby('parcref').D.shift(1)
    return p


def run(p, label, out):
    a = p.dropna(subset=['S', 'S_l1', 'cell_id_data'])
    w = pr.within(a, ['S', 'S_l1'], 'cy'); out[f'{label} | T1 | pooled'] = wf.ols(w.S, w[['S_l1']], a.cell_id_data)
    s = a[a.shock]
    w = pr.within(s, ['S', 'S_l1'], 'cy'); out[f'{label} | T2 | pooled'] = wf.ols(w.S, w[['S_l1']], s.cell_id_data)
    w = wf.demean2(a, ['S', 'S_l1']); out[f'{label} | T1 | field fixed effects'] = wf.ols(w.S, w[['S_l1']], a.cell_id_data)
    w = wf.demean2(s, ['S', 'S_l1']); out[f'{label} | T2 | field fixed effects'] = wf.ols(w.S, w[['S_l1']], s.cell_id_data)
    q = p.assign(dS=p.S - p.S_l1, dS_l1=p.S_l1 - p.S_l2)
    for test, sel in (('T1', None), ('T2', 'shock')):
        b = q.dropna(subset=['dS', 'dS_l1', 'S_l2', 'cell_id_data'])
        if sel:
            b = b[b[sel]]
        w = pr.within(b, ['dS', 'dS_l1', 'S_l2'], 'cy')
        out[f'{label} | {test} | Anderson-Hsiao'] = wf.iv(w.dS, w.dS_l1, w.S_l2, b.cell_id_data)
    r = p[p.shock & (p.shock_next == False)].dropna(subset=['S', 'S_next', 'D_l1', 'cell_id_data']).copy()
    r['rebound'] = r.S_next - r.S
    w = pr.within(r, ['rebound', 'D_l1', 'S'], 'cy'); out[f'{label} | T3 | pooled'] = wf.ols(w.rebound, w[['D_l1', 'S']], r.cell_id_data)
    for y in sorted(s.year.unique()):
        if (s.year == y).mean() > 0.05:
            q2 = s[s.year != y]
            w = pr.within(q2, ['S', 'S_l1'], 'cy'); out[f'{label} | T2 | pooled, without {y}'] = wf.ols(w.S, w[['S_l1']], q2.cell_id_data)
    sh = p[['parcref', 'year', 'S', 'cell_id_data', 'shock']].copy()
    sh['S'] = sh.groupby('parcref').S.transform(lambda v: RNG.permutation(v.values))
    sh = wf.lags(sh)
    a = sh.dropna(subset=['S', 'S_l1', 'cell_id_data'])
    w = pr.within(a, ['S', 'S_l1'], 'cy'); out[f'{label} | T1 | shuffled seasons (placebo)'] = wf.ols(w.S, w[['S_l1']], a.cell_id_data)


def simulate(rho, reps=20, fields=20000, seasons=26, n_base=16, cells=200):
    est = {'pooled': [], 'field FE': [], 'Anderson-Hsiao': []}
    for _ in range(reps):
        a = RNG.normal(0, 1, fields)[:, None]; cell = RNG.integers(0, cells, fields)
        c = RNG.normal(0, 0.8, (cells, seasons))[cell]
        e = np.zeros((fields, seasons)); prev = RNG.normal(0, 1, fields)
        for t in range(seasons):
            prev = rho * prev + np.sqrt(1 - rho ** 2) * RNG.normal(0, 1, fields); e[:, t] = prev
        y = a + c + e
        S = (y - y[:, :n_base].mean(1, keepdims=True)) / y[:, :n_base].std(1, ddof=1, keepdims=True)
        p = pd.DataFrame({'parcref': np.repeat(np.arange(fields), seasons), 'year': np.tile(np.arange(seasons), fields),
                          'S': S.ravel(), 'cell_id_data': np.repeat(cell, seasons), 'shock': False})
        p = wf.lags(p)
        a1 = p.dropna(subset=['S_l1'])
        w = pr.within(a1, ['S', 'S_l1'], 'cy'); est['pooled'].append((w.S * w.S_l1).sum() / (w.S_l1 ** 2).sum())
        w = wf.demean2(a1, ['S', 'S_l1']); est['field FE'].append((w.S * w.S_l1).sum() / (w.S_l1 ** 2).sum())
        b = p.assign(dS=p.S - p.S_l1, dl=p.S_l1 - p.S_l2).dropna(subset=['dS', 'dl', 'S_l2'])
        w = pr.within(b, ['dS', 'dl', 'S_l2'], 'cy'); est['Anderson-Hsiao'].append((w.S_l2 * w.dS).sum() / (w.S_l2 * w.dl).sum())
    return {k: float(np.mean(v)) for k, v in est.items()}


def main():
    p = load()
    print('parcel-seasons', len(p), 'parcels', p.parcref.nunique(), flush=True)
    out = {}
    run(p[p.year >= 2002], '2002-2026', out)
    print('full period done', flush=True)
    run(p[p.year >= 2017].copy(), '2017-2026', out)
    sim = {str(r): simulate(r) for r in (0.0, 0.1, 0.2)}
    json.dump({'tests': out, 'simulation': sim}, open(os.path.join(RES, 'modis_long_baseline_check.json'), 'w'), indent=1)
    L = ['# Paper 2 long-baseline test: MODIS field normals from 16 seasons (2001–2016)', '',
         'Design fixed before any MODIS parcel value was looked at (see the script docstring). Cell × season effects; '
         'errors clustered by ERA5 cell. MODIS pixels are 250 m, so small fields share pixels.', '',
         '| Period | test | version | coefficient | SE | p | n |', '|---|---|---|---|---|---|---|']
    for k, v in out.items():
        a, t, b = k.split(' | ')
        L.append(f"| {a} | {t} | {b} | {v['coef']:+.3f} | {v['se']:.3f} | {v['p']:.3g} | {v['n']:,} |")
    L += ['', '**Simulation of this design** (16-season normal, 26 seasons; mean of 20 runs, T1):', '',
          '| true carry-over ρ | pooled | field fixed effects | Anderson–Hsiao |', '|---|---|---|---|'] + \
         [f"| {r} | {v['pooled']:+.3f} | {v['field FE']:+.3f} | {v['Anderson-Hsiao']:+.3f} |" for r, v in sim.items()]
    open(os.path.join(RES, 'modis_long_baseline_check.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
