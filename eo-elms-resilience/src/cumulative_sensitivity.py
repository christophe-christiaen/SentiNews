"""Sensitivity of the cumulative-shock results to the chosen thresholds (pilot, MODIS, 50 sites).

Grid: shock threshold S <= {-0.75, -1.0, -1.25}; recovery threshold S >= {-0.25, -0.5, -0.75} (must be above the shock
threshold); stress-debt carry-over {0.3, 0.5, 0.7}. Baseline = (-1.0, -0.5, 0.5), the values used in the deck.
For each setting: site typology counts and the share of sites (and regions) keeping their baseline type; the
'unrecovered land is hit harder' test (T2, depends on which years count as national shocks) and the 'debt slows
rebound' test (T3, depends on shocks and carry-over). T1 (legacy) does not depend on the thresholds.
Output: results/cumulative/sensitivity.csv, sensitivity.md
"""
import itertools, os
import numpy as np, pandas as pd, statsmodels.formula.api as smf
import cumulative as cu

OUT = cu.OUT
SHOCKS, RECOVS, LAMS = (-0.75, -1.0, -1.25), (-0.25, -0.5, -0.75), (0.3, 0.5, 0.7)
BASE = (-1.0, -0.5, 0.5)


def run(site, reg, shock, recov, lam):
    cu.SHOCK, cu.RECOV, cu.LAM = shock, recov, lam
    site = site.copy(); reg = reg.copy()
    site['D'] = site.sort_values('year').groupby(['region', 'site']).S.transform(lambda s: cu.debt(s.values))
    reg['D'] = reg.sort_values('year').groupby('region').S.transform(lambda s: cu.debt(s.values))
    st = {(r, i): cu.profile(g)[2] for (r, i), g in site.groupby(['region', 'site'])}
    rt = {r: cu.profile(g)[2] for r, g in reg.groupby('region')}
    p = site.sort_values(['region', 'site', 'year']).copy()
    p['uid'] = p.region + '_' + p.site.astype(str)
    p['S_lag'] = p.groupby('uid').S.shift(1); p['D_lag'] = p.groupby('uid').D.shift(1); p['S_next'] = p.groupby('uid').S.shift(-1)
    p = p.dropna(subset=['S_lag'])
    nat = p.groupby('year').S.mean(); sy = [int(y) for y in nat[nat <= shock].index]
    cl = lambda d: dict(cov_type='cluster', cov_kwds={'groups': pd.factorize(d.uid)[0]})
    out = dict(shock=shock, recov=recov, lam=lam, shock_years=' '.join(map(str, sy)))
    q = p[p.year.isin(sy)]
    if len(sy) >= 2:
        m2 = smf.ols('S ~ S_lag + C(year)', q).fit(**cl(q)); out.update(T2=m2.params['S_lag'], T2_p=m2.pvalues['S_lag'], T2_n=int(m2.nobs))
        r_ = q.dropna(subset=['S_next', 'D_lag']).copy(); r_['rebound'] = r_.S_next - r_.S
        if r_.year.nunique() >= 2:
            m3 = smf.ols('rebound ~ D_lag + S + C(year)', r_).fit(**cl(r_)); out.update(T3=m3.params['D_lag'], T3_p=m3.pvalues['D_lag'], T3_n=int(m3.nobs))
    return out, st, rt


def main():
    nd = pd.read_csv(os.path.join(cu.ROOT, 'data/processed/ndvi_site_year.csv'))
    site = cu.stress_index(nd).sort_values(['region', 'site', 'year'])
    reg = site.groupby(['region', 'year']).S.mean().reset_index()
    _, st0, rt0 = run(site, reg, *BASE)
    rows = []
    for shock, recov, lam in itertools.product(SHOCKS, RECOVS, LAMS):
        if recov <= shock:
            continue
        o, st, rt = run(site, reg, shock, recov, lam)
        types = pd.Series(st).value_counts()
        o.update({f'n_{k}': int(types.get(k, 0)) for k in ('Persistent stress', 'Back-to-back hits', 'Slow recovery', 'Bounced back', 'Little affected')})
        o['sites_same_type'] = np.mean([st[k] == st0[k] for k in st0])
        o['regions_same_type'] = np.mean([rt[k] == rt0[k] for k in rt0])
        o['baseline'] = (shock, recov, lam) == BASE
        rows.append(o)
    d = pd.DataFrame(rows)
    d.to_csv(os.path.join(OUT, 'sensitivity.csv'), index=False)
    cu.SHOCK, cu.RECOV, cu.LAM = BASE      # restore
    f = lambda v, p: '' if pd.isna(v) else f'{v:+.2f} ({"p<0.001" if p < 0.001 else f"p={p:.3f}"})'
    t = d.assign(T2s=[f(a, b) for a, b in zip(d.T2, d.T2_p)], T3s=[f(a, b) for a, b in zip(d.get('T3'), d.get('T3_p'))],
                 same=(d.sites_same_type * 100).round(0).astype(int).astype(str) + '%')
    cols = ['shock', 'recov', 'lam', 'shock_years', 'T2s', 'T3s', 'n_Persistent stress', 'n_Back-to-back hits', 'n_Slow recovery',
            'n_Bounced back', 'n_Little affected', 'same']
    lines = ['# Sensitivity of the cumulative-shock results to thresholds (pilot, 50 sites)', '',
             'Baseline (used in the deck): shock S <= -1.0, recovered S >= -0.5, debt carry-over 0.5.', '',
             f'- "Unrecovered land is hit harder" (T2) positive and p < 0.05 in {int(((d.T2 > 0) & (d.T2_p < 0.05)).sum())} of {len(d)} settings; '
             f'range {d.T2.min():+.2f} to {d.T2.max():+.2f}',
             f'- "Debt slows rebound" (T3) positive and p < 0.05 in {int(((d.T3 > 0) & (d.T3_p < 0.05)).sum())} of {int(d.T3.notna().sum())} settings; '
             f'positive in {int((d.T3 > 0).sum())}; range {d.T3.min():+.2f} to {d.T3.max():+.2f}',
             f'- Sites keeping their baseline resilience type: median {d.sites_same_type.median():.0%} '
             f'(range {d.sites_same_type.min():.0%}-{d.sites_same_type.max():.0%}); regions: median {d.regions_same_type.median():.0%}', '',
             t[cols].rename(columns={'T2s': 'T2 hit harder', 'T3s': 'T3 debt slows rebound', 'same': 'sites same type',
                                     'n_Persistent stress': 'persistent', 'n_Back-to-back hits': 'back-to-back', 'n_Slow recovery': 'slow',
                                     'n_Bounced back': 'bounced', 'n_Little affected': 'little'}).to_markdown(index=False)]
    open(os.path.join(OUT, 'sensitivity.md'), 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
