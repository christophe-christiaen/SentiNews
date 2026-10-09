"""Countryside Stewardship (CS) coverage vs drought response, cropland and grassland separately.

Outcome: site x land-cover stress index (cumulative.py definition, 2001-2015 baseline) in drought years,
and the rebound the year after 2022. Exposure: share of the site's 6 x 6 km window under CS land-management
agreements (fetch_aes.py): agreements started by 2021 for the 2022 tests, all live agreements for 2025-26.
English sites only (CS is England's scheme). Spearman rank correlation and OLS with region fixed effects.
CS share is measured for the whole window, not separately for its cropland and grassland."""
import json, os, warnings, numpy as np, pandas as pd, statsmodels.formula.api as smf
from scipy import stats
warnings.filterwarnings('ignore')
from cumulative import BASE
ROOT = os.path.join(os.path.dirname(__file__), '..'); OUT = f'{ROOT}/results/cumulative'
nd = pd.read_csv(f'{ROOT}/data/processed/ndvi_site_year.csv')
for col in ('peak', 'july'):
    nd[col + '_z'] = nd.groupby(['region', 'site', 'cover'], group_keys=False).apply(
        lambda g: (g[col] - g[g.year <= BASE][col].mean()) / g[g.year <= BASE][col].std())
nd['S'] = nd[['peak_z', 'july_z']].mean(axis=1)
w = nd.pivot_table(index=['region', 'site', 'cover'], columns='year', values='S').reset_index()
w['rebound_2023'] = w[2023] - w[2022]
cs = pd.read_csv(f'{ROOT}/data/processed/cs_share_by_site.csv')
d = w.merge(cs, on=['region', 'site'])
tests = [('drought 2022', 2022, 'cs_share_by2021'), ('rebound 2023', 'rebound_2023', 'cs_share_by2021'),
         ('drought 2025', 2025, 'cs_share_all'), ('drought 2026', 2026, 'cs_share_all')]
res = {}
for cov in ('combined', 'crop', 'grass'):
    if cov == 'combined':
        x = d.groupby(['region', 'site']).agg({**{c: 'mean' for c in (2022, 2025, 2026, 'rebound_2023')}, 'cs_share_all': 'first', 'cs_share_by2021': 'first'}).reset_index()
    else:
        x = d[d.cover == cov]
    res[cov] = {'n_sites': int(len(x))}
    for name, y, share in tests:
        e = x[['region', share]].assign(y=x[y]).dropna()
        rho, p = stats.spearmanr(e[share], e.y)
        m = smf.ols(f'y ~ {share} + C(region)', e).fit()
        res[cov][name] = dict(n=len(e), spearman=round(rho, 2), p=round(p, 3),
                              coef_per_10pct=round(m.params[share] / 10, 3), p_region_fe=round(m.pvalues[share], 3))
json.dump(res, open(f'{OUT}/cs_by_cover.json', 'w'), indent=2, default=float)
for cov, r in res.items():
    print(cov, r['n_sites'], {k: (v['spearman'], v['p'], v['coef_per_10pct'], v['p_region_fe']) for k, v in r.items() if k != 'n_sites'})
