"""Income test split by land cover: Defra regional accounts per hectare (ITL1 England, 2010-2025)
vs cropland and grassland NDVI. Same method as analysis.py (H2): NDVI detrended per region within the
2010-2025 panel, log outcome, region + year fixed effects; p-values from OLS and from region-clustered errors
(few clusters, so treat clustered p with caution). Grassland uses regions with >= 2 grassland sites.
Outcomes: Total Income from Farming (TIFF), total crop output, total livestock output (all GBP per ha)."""
import json, os, warnings, numpy as np, pandas as pd, statsmodels.formula.api as smf
warnings.filterwarnings('ignore')
ROOT = os.path.join(os.path.dirname(__file__), '..'); RAW, PROC = f'{ROOT}/data/raw', f'{ROOT}/data/processed'
OUT = f'{ROOT}/results/income_by_cover'; os.makedirs(OUT, exist_ok=True)
nd = pd.read_csv(f'{PROC}/ndvi_site_year.csv'); nd = nd[nd.year <= 2025]
nsite = nd.groupby(['region', 'cover']).site.nunique()
t = pd.read_excel(f'{RAW}/tiff_itl1_ha.ods', sheet_name='ITL1_Per_Ha', engine='odf', header=None)
name_map = {'North East': 'North East', 'North West': 'North West and Merseyside', 'Yorkshire and The Humber': 'Yorkshire & The Humber',
            'East Midlands': 'East Midlands', 'West Midlands': 'West Midlands', 'East of England': 'Eastern',
            'London and the South East': 'South East and London', 'South West': 'South West'}
VARS = {'Total income from farming': 'tiff', 'Total crop output': 'crop_out', 'Total livestock output': 'livestock_out'}
rows, cur, ys = [], None, None
for _, r in t.iterrows():
    lab = str(r[0]).strip()
    if ' - TL' in lab: cur = name_map.get(lab.split(' - ')[0].strip())
    elif lab == 'Type': ys = [int(v) if isinstance(v, (int, float)) and not pd.isna(v) else None for v in r[1:]]
    elif cur and ys and lab in VARS:
        rows += [dict(region=cur, year=y, var=VARS[lab], val=pd.to_numeric(v, errors='coerce')) for y, v in zip(ys, r[1:]) if y]
acc = pd.DataFrame(rows).pivot_table(index=['region', 'year'], columns='var', values='val').reset_index()
def detrend(df, col):
    return df.groupby('region', group_keys=False).apply(lambda g: g[col] - np.polyval(np.polyfit(g.year, g[col], 1), g.year))
panel = {}
for cov in ('crop', 'grass'):
    g = nd[nd.cover == cov].groupby(['region', 'year'])[['peak', 'early']].mean().reset_index()
    g = g[[nsite.get((r, cov), 0) >= 2 for r in g.region]]
    e = acc.merge(g, on=['region', 'year']).dropna()
    e['peak_a'] = detrend(e, 'peak'); e['early_a'] = detrend(e, 'early')
    panel[cov] = e
def fit(f, d, term):
    m = smf.ols(f, d).fit(); mc = smf.ols(f, d).fit(cov_type='cluster', cov_kwds={'groups': pd.factorize(d.region)[0]})
    return dict(n=int(m.nobs), regions=int(d.region.nunique()), pct_per_0p1=round(100 * m.params[term] / 10, 1),
                p_ols=round(m.pvalues[term], 3), p_cluster_region=round(mc.pvalues[term], 3))
res = {}
for cov, e in panel.items():
    for out in ('tiff', 'crop_out', 'livestock_out'):
        d = e.assign(y=np.log(e[out]))
        for met in ('peak_a', 'early_a'):
            res[f'{out}~{cov}_{met}'] = fit(f'y ~ {met} + C(region) + C(year)', d, met)
# both land covers in one model (regions with both)
both = panel['crop'][['region', 'year', 'tiff', 'crop_out', 'livestock_out', 'peak_a']].merge(
    panel['grass'][['region', 'year', 'peak_a']], on=['region', 'year'], suffixes=('_crop', '_grass'))
for out in ('tiff', 'crop_out', 'livestock_out'):
    d = both.assign(y=np.log(both[out]))
    m = smf.ols('y ~ peak_a_crop + peak_a_grass + C(region) + C(year)', d).fit()
    res[f'{out}~both'] = dict(n=int(m.nobs), regions=int(d.region.nunique()),
                              crop=dict(pct_per_0p1=round(10 * m.params['peak_a_crop'], 1), p=round(m.pvalues['peak_a_crop'], 3)),
                              grass=dict(pct_per_0p1=round(10 * m.params['peak_a_grass'], 1), p=round(m.pvalues['peak_a_grass'], 3)))
json.dump(res, open(f'{OUT}/income_by_cover.json', 'w'), indent=2, default=float)
for k, v in res.items(): print(k, v)
