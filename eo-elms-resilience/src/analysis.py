"""Pilot tests of whether an EO (MODIS NDVI) signal exists for UK agricultural
outcomes, resilience and agri-environment coverage.  Writes results/*.csv|json.

H1  Yield signal   : region-year peak cropland NDVI anomaly vs Defra wheat-yield anomaly
                     (8 English regions + Scotland + Wales, 2001-2025, both detrended per region).
H1b Lead time      : same, using only composites available by ~1 July ('early').
H1c Cross-section  : add year fixed effects -> does EO explain *which* regions do worse in a
                     given year, beyond the national weather/price shock?
H2  Income signal  : Defra TIFF per ha & crop output per ha (ITL1, 2010-2025) on NDVI, region+year FE.
H3  Shock profile  : NDVI resistance in drought years 2018, 2022, 2025 and rebound next season.
H4  AES link       : site-level Countryside Stewardship share vs 2022/2025 drought NDVI anomaly.
Everything is exploratory pilot evidence (small n); inference uses region-clustered or
leave-one-year-out designs where possible."""
import json, os, warnings, numpy as np, pandas as pd, statsmodels.formula.api as smf
from scipy import stats
warnings.filterwarnings('ignore')
ROOT = os.path.join(os.path.dirname(__file__), '..')
RAW, PROC, RES = [os.path.join(ROOT, p) for p in ('data/raw', 'data/processed', 'results')]
out = {}

# ---------- EO panel ----------
nd = pd.read_csv(f'{PROC}/ndvi_site_year.csv')
nd = nd[nd.year <= 2025]  # pilot results as presented; 2026 is used in cumulative.py
crop = nd[nd.cover == 'crop'].groupby(['region', 'year'])[['peak', 'early', 'july', 'peak_cv']].mean().reset_index()

def detrend(df, col, by='region'):
    def f(g):
        b = np.polyfit(g.year, g[col], 1); return g[col] - np.polyval(b, g.year)
    return df.groupby(by, group_keys=False).apply(f)

# ---------- Defra regional wheat yields ----------
w = pd.read_excel(f'{RAW}/cops.ods', sheet_name='Regional_wheat', engine='odf', header=None)
import re
yrs = [float(str(v)[:4]) if re.fullmatch(r'(19|20)\d\d(\.0)?(\(\d\))?', str(v).strip()) else np.nan
       for v in w.iloc[17, 1:]]  # e.g. '2022(1)' -> 2022
yl = []
for r in range(18, 31):
    name = w.iloc[r, 0]
    for c, y in enumerate(yrs, start=1):
        if isinstance(y, (int, float)) and not pd.isna(y):
            v = pd.to_numeric(w.iloc[r, c], errors='coerce'); yl.append(dict(region=name, year=int(y), wheat_t_ha=v))
yl = pd.DataFrame(yl).dropna()
d = crop.merge(yl, on=['region', 'year'])
for c in ['peak', 'early', 'july', 'wheat_t_ha']:
    d[c + '_a'] = detrend(d, c)
d.to_csv(f'{PROC}/panel_yield.csv', index=False)

def fe_fit(formula, data, cluster='region'):
    m = smf.ols(formula, data).fit(cov_type='cluster', cov_kwds={'groups': pd.factorize(data[cluster])[0]})
    return m

res = {}
for met in ['peak', 'early', 'july']:
    r, p = stats.pearsonr(d[met + '_a'], d.wheat_t_ha_a)
    m = fe_fit(f'wheat_t_ha_a ~ {met}_a + C(region)', d)
    mY = fe_fit(f'wheat_t_ha_a ~ {met}_a + C(region) + C(year)', d)
    # leave-one-year-out out-of-sample skill (pooled slope, region-detrended anomalies)
    pred = []
    for y in sorted(d.year.unique()):
        tr, te = d[d.year != y], d[d.year == y]
        b = np.polyfit(tr[met + '_a'], tr.wheat_t_ha_a, 1)
        pred.append(pd.DataFrame(dict(obs=te.wheat_t_ha_a, pred=np.polyval(b, te[met + '_a']))))
    pr = pd.concat(pred)
    r2_oos = 1 - ((pr.obs - pr.pred) ** 2).sum() / ((pr.obs - pr.obs.mean()) ** 2).sum()
    res[met] = dict(n=len(d), r=r, p=p, r2=r ** 2, slope_t_ha_per_0p1ndvi=m.params[f'{met}_a'] / 10,
                    p_cluster=m.pvalues[f'{met}_a'], slope_yearFE=mY.params[f'{met}_a'] / 10,
                    p_yearFE=mY.pvalues[f'{met}_a'], r2_loyo_oos=r2_oos,
                    p_cluster_year=fe_fit(f'wheat_t_ha_a ~ {met}_a + C(region)', d, cluster='year').pvalues[f'{met}_a'],
                    p_yearFE_ols=smf.ols(f'wheat_t_ha_a ~ {met}_a + C(region) + C(year)', d).fit().pvalues[f'{met}_a'])
out['H1_yield'] = res
# per-region correlation (primary metric)
out['H1_by_region'] = {g: dict(n=len(x), r=stats.pearsonr(x.peak_a, x.wheat_t_ha_a)[0])
                       for g, x in d.groupby('region') if len(x) > 8}
# national-level (England) time series
eng = d[~d.region.isin(['Scotland', 'Wales'])].groupby('year')[['peak_a', 'early_a', 'wheat_t_ha_a']].mean()
out['H1_national'] = {k: dict(r=stats.pearsonr(eng[k], eng.wheat_t_ha_a)[0], n=len(eng)) for k in ['peak_a', 'early_a']}
eng.to_csv(f'{RES}/england_yield_vs_ndvi.csv')

# ---------- Defra TIFF per ha (ITL1) ----------
t = pd.read_excel(f'{RAW}/tiff_itl1_ha.ods', sheet_name='ITL1_Per_Ha', engine='odf', header=None)
name_map = {'North East': 'North East', 'North West': 'North West and Merseyside',
            'Yorkshire and The Humber': 'Yorkshire & The Humber', 'East Midlands': 'East Midlands',
            'West Midlands': 'West Midlands', 'East of England': 'Eastern',
            'London and the South East': 'South East and London', 'South West': 'South West'}
tl, cur, years = [], None, None
for _, r in t.iterrows():
    lab = str(r[0])
    if ' - TL' in lab: cur = name_map.get(lab.split(' - ')[0].strip())
    elif lab == 'Type': years = [int(v) if isinstance(v, (int, float)) and not pd.isna(v) else None for v in r[1:]]
    elif cur and years and lab.strip() in ('Total crop output', 'Total income from farming', 'Output at market prices'):
        for y, v in zip(years, r[1:]):
            if y: tl.append(dict(region=cur, year=y, var=lab.strip(), val=pd.to_numeric(v, errors='coerce')))
tl = pd.DataFrame(tl).pivot_table(index=['region', 'year'], columns='var', values='val').reset_index()
tl.columns = ['region', 'year', 'output_ha', 'crop_output_ha', 'tiff_ha']
e = tl.merge(crop, on=['region', 'year']).dropna()
e['peak_a'] = detrend(e, 'peak'); e['early_a'] = detrend(e, 'early')
e['ltiff'] = np.log(e.tiff_ha); e['lcrop'] = np.log(e.crop_output_ha)
h2 = {}
for y in ['ltiff', 'lcrop']:
    for met in ['peak_a', 'early_a']:
        m = fe_fit(f'{y} ~ {met} + C(region) + C(year)', e)
        mo = smf.ols(f'{y} ~ {met} + C(region) + C(year)', e).fit()
        h2[f'{y}~{met}'] = dict(n=len(e), coef_pct_per_0p1ndvi=100 * m.params[met] / 10, p_cluster_region=m.pvalues[met],
                                p_ols=mo.pvalues[met])
out['H2_income'] = h2
e.to_csv(f'{PROC}/panel_income.csv', index=False)

# ---------- H3 shock profiles ----------
allc = nd.groupby(['region', 'year', 'cover'])['peak'].mean().reset_index()
allc['z'] = allc.groupby(['region', 'cover']).peak.transform(
    lambda s: (s - s[(allc.loc[s.index, 'year'] <= 2020)].mean()) / s[(allc.loc[s.index, 'year'] <= 2020)].std())
jul = nd.groupby(['region', 'year', 'cover'])['july'].mean().reset_index()
jul['z'] = jul.groupby(['region', 'cover']).july.transform(lambda s: (s - s.mean()) / s.std())
shock = []
for (reg, cov), g in jul.groupby(['region', 'cover']):
    g = g.set_index('year').z
    for sy in [2018, 2022, 2025]:
        if sy in g:
            shock.append(dict(region=reg, cover=cov, shock_year=sy, july_z=g[sy], next_z=g.get(sy + 1, np.nan)))
shock = pd.DataFrame(shock)
shock.to_csv(f'{RES}/shock_profiles.csv', index=False)
out['H3_mean_july_z'] = {f'{k[0]}_{k[1]}': v for k, v in shock.groupby(['shock_year', 'cover'])[['july_z', 'next_z']].mean().round(2).T.to_dict().items()}

# ---------- H4 AES ----------
cs = pd.read_csv(f'{PROC}/cs_share_by_site.csv')
sitej = nd.copy()
sitej['z'] = sitej.groupby(['region', 'site', 'cover']).july.transform(lambda s: (s - s.mean()) / s.std())
sy = sitej[sitej.year.isin([2018, 2022, 2025])].groupby(['region', 'site', 'year']).z.mean().unstack()
sy.columns = [f'july_z_{c}' for c in sy.columns]
a = cs.merge(sy.reset_index(), on=['region', 'site'])
h4 = {}
for col, share in [('july_z_2025', 'cs_share_all'), ('july_z_2022', 'cs_share_by2021')]:
    r, p = stats.spearmanr(a[share], a[col])
    m = smf.ols(f'{col} ~ {share} + C(region)', a).fit()
    h4[f'{col}~{share}'] = dict(n=len(a), spearman=r, p=p, coef_region_fe=m.params[share], p_region_fe=m.pvalues[share])
out['H4_aes'] = h4
a.to_csv(f'{PROC}/site_aes_drought.csv', index=False)

json.dump(out, open(f'{RES}/pilot_results.json', 'w'), indent=2, default=float)
print(json.dumps(out, indent=1, default=lambda x: round(float(x), 3)))
