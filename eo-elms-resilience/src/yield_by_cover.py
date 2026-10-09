"""Yield signal split by land cover (2001-2025, the pilot years).

1. Wheat-yield anomaly vs cropland and vs grassland peak-NDVI anomaly, per region and pooled
   (regions with >= 2 sites of that land cover; both series detrended per region).
2. Horse race in regions that have both: yield ~ crop NDVI + grass NDVI (+ region FE, + year FE).
   If cropland carries the signal, grass adds little once crop is in.
(Income and livestock output by land cover: see income_by_cover.py.)
"""
import json, os, re, warnings, numpy as np, pandas as pd, statsmodels.formula.api as smf
from scipy import stats
warnings.filterwarnings('ignore')
ROOT = os.path.join(os.path.dirname(__file__), '..'); RAW, PROC, RES = (os.path.join(ROOT, p) for p in ('data/raw', 'data/processed', 'results'))
nd = pd.read_csv(f'{PROC}/ndvi_site_year.csv'); nd = nd[nd.year <= 2025]
nsite = nd.groupby(['region', 'cover']).site.nunique()
ok = lambda r, c: nsite.get((r, c), 0) >= 2
reg = nd.groupby(['region', 'cover', 'year'])[['peak', 'early']].mean().reset_index()
reg = reg[[ok(r, c) for r, c in zip(reg.region, reg.cover)]]
def detrend(df, col):
    return df.groupby('region', group_keys=False).apply(lambda g: g[col] - np.polyval(np.polyfit(g.year, g[col], 1), g.year))
w = pd.read_excel(f'{RAW}/cops.ods', sheet_name='Regional_wheat', engine='odf', header=None)
yrs = [float(str(v)[:4]) if re.fullmatch(r'(19|20)\d\d(\.0)?(\(\d\))?', str(v).strip()) else np.nan for v in w.iloc[17, 1:]]
yl = pd.DataFrame([dict(region=w.iloc[r, 0], year=int(y), wheat=pd.to_numeric(w.iloc[r, c], errors='coerce'))
                   for r in range(18, 31) for c, y in enumerate(yrs, start=1) if not pd.isna(y)]).dropna()
out = {}
panels = {}
for cov in ('crop', 'grass'):
    d = reg[reg.cover == cov].merge(yl, on=['region', 'year'])
    d['ndvi_a'] = detrend(d, 'peak'); d['early_a'] = detrend(d, 'early'); d['wheat_a'] = detrend(d, 'wheat')
    panels[cov] = d
    r, p = stats.pearsonr(d.ndvi_a, d.wheat_a)
    pred = []
    for y in sorted(d.year.unique()):
        tr, te = d[d.year != y], d[d.year == y]; b = np.polyfit(tr.ndvi_a, tr.wheat_a, 1)
        pred.append(pd.DataFrame(dict(obs=te.wheat_a, pred=np.polyval(b, te.ndvi_a))))
    pr = pd.concat(pred); r2 = 1 - ((pr.obs - pr.pred) ** 2).sum() / ((pr.obs - pr.obs.mean()) ** 2).sum()
    m = smf.ols('wheat_a ~ ndvi_a + C(region) + C(year)', d).fit()
    out[cov] = dict(n=len(d), regions=int(d.region.nunique()), r=r, p=p, r2_loyo=r2,
                    yearFE_slope_t_per_0p1=m.params['ndvi_a'] / 10, yearFE_p=m.pvalues['ndvi_a'],
                    by_region={g: round(stats.pearsonr(x.ndvi_a, x.wheat_a)[0], 2) for g, x in d.groupby('region')})
# early warning: the same tests using only composites available by mid-July ('early' metric)
for cov in ('crop', 'grass'):
    d = panels[cov]
    r, p = stats.pearsonr(d.early_a, d.wheat_a)
    pred = []
    for y in sorted(d.year.unique()):
        tr, te = d[d.year != y], d[d.year == y]; b = np.polyfit(tr.early_a, tr.wheat_a, 1)
        pred.append(pd.DataFrame(dict(obs=te.wheat_a, pred=np.polyval(b, te.early_a))))
    pr = pd.concat(pred); r2 = 1 - ((pr.obs - pr.pred) ** 2).sum() / ((pr.obs - pr.obs.mean()) ** 2).sum()
    m = smf.ols('wheat_a ~ early_a + C(region) + C(year)', d).fit()
    out[cov]['early'] = dict(n=len(d), r=r, p=p, r2_loyo=r2, yearFE_slope_t_per_0p1=m.params['early_a'] / 10, yearFE_p=m.pvalues['early_a'])
eb = panels['crop'][['region', 'year', 'early_a', 'wheat_a']].merge(panels['grass'][['region', 'year', 'early_a']], on=['region', 'year'], suffixes=('_crop', '_grass'))
m = smf.ols('wheat_a ~ early_a_crop + early_a_grass + C(year)', eb).fit()
out['horse_race_early'] = dict(n=int(m.nobs), crop=dict(coef=m.params['early_a_crop'] / 10, p=m.pvalues['early_a_crop']),
                               grass=dict(coef=m.params['early_a_grass'] / 10, p=m.pvalues['early_a_grass']))
# horse race in regions with both covers
both = panels['crop'][['region', 'year', 'ndvi_a', 'wheat_a']].merge(
    panels['grass'][['region', 'year', 'ndvi_a']], on=['region', 'year'], suffixes=('_crop', '_grass'))
h = {}
for name, f in [('crop_only', 'wheat_a ~ ndvi_a_crop'), ('grass_only', 'wheat_a ~ ndvi_a_grass'), ('both', 'wheat_a ~ ndvi_a_crop + ndvi_a_grass'),
                ('both_yearFE', 'wheat_a ~ ndvi_a_crop + ndvi_a_grass + C(year)')]:
    m = smf.ols(f, both).fit()
    h[name] = dict(n=int(m.nobs), r2=m.rsquared, **{k: dict(coef=m.params[k] / 10, p=m.pvalues[k]) for k in ('ndvi_a_crop', 'ndvi_a_grass') if k in m.params})
h['regions'] = sorted(both.region.unique())
out['horse_race'] = h
os.makedirs(f'{RES}/yield_by_cover', exist_ok=True)
json.dump(out, open(f'{RES}/yield_by_cover/yield_by_cover.json', 'w'), indent=2, default=float)
for cov in ('crop', 'grass'): panels[cov].to_csv(f'{RES}/yield_by_cover/panel_{cov}.csv', index=False)
print(json.dumps(out, indent=1, default=lambda x: round(float(x), 3)))

# map: correlation with wheat yield by region, cropland vs grassland
import matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt, matplotlib.patheffects as pe
from matplotlib.colors import LinearSegmentedColormap, Normalize
from cumulative_maps import draw, cbar, geoms, xy, INK, MUTED, SURF
SEQ = LinearSegmentedColormap.from_list('seq', ['#E6EFE8', '#9CC3A9', '#4F8A69', '#1E4D36']); norm = Normalize(0, 0.8)
fig, axs = plt.subplots(1, 2, figsize=(13, 9.5), facecolor=SURF)
for ax, cov in zip(axs, ('crop', 'grass')):
    rr = out[cov]['by_region']
    draw(ax, lambda r: SEQ(norm(rr[r])) if r in rr else '#E4E1DA')
    for reg_name, g in geoms:
        if reg_name in rr and (reg_name != 'South East and London' or g.area > 5e9):
            c = g.representative_point()
            ax.text(c.x, c.y, f'{rr[reg_name]:.2f}', ha='center', va='center', fontsize=11, weight='bold', color=INK,
                    path_effects=[pe.withStroke(linewidth=4, foreground='white')])
    s = nd[nd.cover == cov][['region', 'site']].drop_duplicates().merge(xy, on=['region', 'site'])
    ax.scatter(s.x, s.y, s=10, c=INK, marker='s', alpha=.45)
    o = out[cov]
    ax.set_title(f'{"Cropland" if cov == "crop" else "Grassland"} · r = {o["r"]:.2f}, out-of-sample R² = {o["r2_loyo"]:.2f}', loc='left', fontsize=13)
cbar(fig, axs, SEQ, norm, 'Correlation: NDVI anomaly vs wheat-yield anomaly, 2001–2025')
fig.suptitle('Where greenness tracks wheat yield: cropland vs grassland', x=0.02, ha='left', fontsize=15)
fig.text(0.02, 0.01, 'Squares: sites with that land cover. Regions shown where ≥ 2 sites have it (grey = n/a). Yields: Defra cereal survey; MODIS MOD13Q1; ONS ITL1 2021.', fontsize=8, color=MUTED)
fig.savefig(f'{ROOT}/results/maps/map2_yield_signal_by_cover.png', dpi=160, bbox_inches='tight'); plt.close(fig)
