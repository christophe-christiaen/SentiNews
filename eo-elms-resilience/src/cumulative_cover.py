"""Cumulative-shock tests controlling for land cover (cropland vs grassland).

The main analysis (cumulative.py) averages each site's crop and grass stress index, so a region's
land-cover mix could drive its results (e.g. grass-dominated North West). Here the unit is
site x cover x year:
  * year FE are replaced by cover x year FE (grass and crop react differently to the same weather);
  * interactions with a grass dummy test whether persistence / shock / rebound effects differ;
  * every test is re-run on crop-only and grass-only samples;
  * regional typology is recomputed from crop-only and grass-only indices.
"""
import json, os, warnings, numpy as np, pandas as pd, statsmodels.formula.api as smf
warnings.filterwarnings('ignore')
from cumulative import BASE, SHOCK, RECOV, debt, profile
ROOT = os.path.join(os.path.dirname(__file__), '..'); OUT = os.path.join(ROOT, 'results', 'cumulative')

nd = pd.read_csv(os.path.join(ROOT, 'data/processed/ndvi_site_year.csv'))
for col in ('peak', 'july'):
    nd[col + '_z'] = nd.groupby(['region', 'site', 'cover'], group_keys=False).apply(
        lambda g: (g[col] - g[g.year <= BASE][col].mean()) / g[g.year <= BASE][col].std())
nd['S'] = nd[['peak_z', 'july_z']].mean(axis=1)
p = nd[['region', 'site', 'cover', 'year', 'S', 'npix']].sort_values(['region', 'site', 'cover', 'year']).copy()
p['uid'] = p.region + '_' + p.site.astype(str); p['ucov'] = p.uid + '_' + p.cover
p['D'] = p.groupby('ucov').S.transform(lambda s: debt(s.values))
p['S_lag'] = p.groupby('ucov').S.shift(1); p['D_lag'] = p.groupby('ucov').D.shift(1); p['S_next'] = p.groupby('ucov').S.shift(-1)
p['grass'] = (p.cover == 'grass').astype(int)
p = p.dropna(subset=['S_lag'])
nat = p.groupby('year').S.mean(); shock_years = [int(y) for y in nat[nat <= SHOCK].index]

def fit(f, d):
    return smf.ols(f, d).fit(cov_type='cluster', cov_kwds={'groups': pd.factorize(d.uid)[0]})
def row(m, term):
    return dict(n=int(m.nobs), coef=round(m.params[term], 3), p=round(m.pvalues[term], 4))
res = {'national_shock_years': shock_years, 'n_site_covers': int(p.ucov.nunique()),
       'covers': p.groupby('cover').ucov.nunique().to_dict()}
FE = 'C(cover):C(year)'
samples = {'pooled (cover x year FE)': p, 'crop only': p[p.cover == 'crop'], 'grass only': p[p.cover == 'grass']}
for name, d in samples.items():
    fe = FE if name.startswith('pooled') else 'C(year)'
    q = d[d.year.isin(shock_years)]
    r = q.dropna(subset=['S_next', 'D_lag']).copy(); r['rebound'] = r.S_next - r.S
    res[name] = dict(T1_legacy=row(fit(f'S ~ S_lag + {fe}', d), 'S_lag'),
                     T2_hit_harder=row(fit(f'S ~ S_lag + {fe}', q), 'S_lag'),
                     T3_debt_slows_rebound=row(fit(f'rebound ~ D_lag + S + {fe}', r), 'D_lag'),
                     mean_rebound_after_shock=round(r.rebound.mean(), 2))
# do effects differ for grass? (interactions, pooled, cover x year FE)
q = p[p.year.isin(shock_years)]
r = q.dropna(subset=['S_next', 'D_lag']).copy(); r['rebound'] = r.S_next - r.S
res['grass_difference'] = dict(T1=row(fit(f'S ~ S_lag * grass + {FE}', p), 'S_lag:grass'),
                               T2=row(fit(f'S ~ S_lag * grass + {FE}', q), 'S_lag:grass'),
                               T3=row(fit(f'rebound ~ D_lag * grass + S + {FE}', r), 'D_lag:grass'))
# regional typology by cover
typ = {}
for cov in ('crop', 'grass'):
    reg = p[p.cover == cov].groupby(['region', 'year']).S.mean().reset_index()
    full = nd[nd.cover == cov].groupby(['region', 'year']).S.mean().reset_index()   # include 2001 for profile()
    for rgn, g in full.groupby('region'):
        if p[(p.cover == cov) & (p.region == rgn)].uid.nunique() < 2: continue   # need >= 2 sites
        typ.setdefault(rgn, {})[cov] = profile(g)[2]
main = pd.read_csv(os.path.join(OUT, 'region_typology.csv')).set_index('region').typology
for rgn in main.index: typ.setdefault(rgn, {})['combined (main)'] = main[rgn]
res['region_typology_by_cover'] = typ
# land-cover mix per region (share of masked pixels that are grass)
mix = nd[nd.year == 2020].groupby(['region', 'cover']).npix.sum().unstack().fillna(0)
res['grass_share'] = (mix.grass / mix.sum(axis=1)).round(2).to_dict()
# T4 by cover: lag-1 autocorrelation of the region index, 2002-13 vs 2014-26 (regions with >= 2 sites)
ar = {}
for cov in ('crop', 'grass'):
    full = nd[nd.cover == cov].groupby(['region', 'year']).S.mean()
    for rgn in full.index.get_level_values(0).unique():
        if nd[(nd.cover == cov) & (nd.region == rgn)].site.nunique() < 2: continue
        g = full.loc[rgn]
        ar.setdefault(cov, {})[rgn] = dict(early=round(g.loc[2002:2013].autocorr(1), 2), late=round(g.loc[2014:2026].autocorr(1), 2))
res['T4_AR1_by_cover'] = {c: dict(regions=v, rose=sum(x['late'] > x['early'] for x in v.values()), n=len(v),
                                  mean_early=round(np.mean([x['early'] for x in v.values()]), 2),
                                  mean_late=round(np.mean([x['late'] for x in v.values()]), 2)) for c, v in ar.items()}
json.dump(res, open(os.path.join(OUT, 'cumulative_by_cover.json'), 'w'), indent=2, default=float)
print(json.dumps(res, indent=1, default=float))
