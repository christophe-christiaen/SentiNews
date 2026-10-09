"""Cross-sensor check of the recent shock sequence: Terra (MOD13Q1) vs Aqua (MYD13Q1).
Both sensors are processed identically (same sites, windows, land-cover masks and metrics)
and z-scored against their own 2016-2021 mean and SD, so only year-to-year anomalies are compared.
If Terra's orbit drift had biased recent years, the Terra-minus-Aqua gap would trend over time."""
import glob, json, os, re, numpy as np, pandas as pd
from scipy import stats
ROOT = os.path.join(os.path.dirname(__file__), '..'); RAW = f'{ROOT}/data/raw'
OUT = f'{ROOT}/results/cumulative'
def load(fn):
    j = json.load(open(fn)); n, m = int(j['nrows']), int(j['ncols'])
    return n, m, [(int(s['modis_date'][5:]), np.array(s['data'], float).reshape(n, m)) for s in j['subset']]
def metrics(fn, lc):
    n, m, comps = load(fn)
    if not comps: return None
    ln, lm = lc.shape; lcg = lc[np.ix_(np.arange(n) * ln // n, np.arange(m) * lm // m)]
    doy = np.array([d for d, _ in comps]); cube = np.stack([a for _, a in comps]) * 1e-4; cube[cube < -0.2] = np.nan
    def stat(lo, hi, k):
        sel = cube[(doy >= lo) & (doy <= hi)]
        if len(sel) < k: return np.full((n, m), np.nan)
        s = np.sort(np.nan_to_num(sel, nan=-1), axis=0)[-k:]; s[s < -0.5] = np.nan; return np.nanmean(s, axis=0)
    pk, jl = stat(113, 193, 3), stat(177, 217, 1)
    out = {}
    for cover, cls in dict(crop=(12, 14), grass=(10,)).items():
        mask = np.isin(lcg, cls)
        if mask.sum() >= 20: out[cover] = (np.nanmedian(pk[mask]), np.nanmedian(jl[mask]))
    return out
rows = []
for lc_fn in glob.glob(f'{RAW}/modis/MCD12Q1_LC_Type1_*.json'):
    tag, site = re.match(r'.*LC_Type1_(.+)_(\d+)_2019_1\.json', lc_fn).groups()
    lc = load(lc_fn)[2][0][1]
    for y in range(2016, 2027):
        for sensor, fn in (('Terra', f'{RAW}/modis/MOD13Q1_250m_16_days_NDVI_{tag}_{site}_{y}_81.json'),
                           ('Aqua', f'{RAW}/modis_aqua/MYD13Q1_NDVI_{tag}_{site}_{y}.json')):
            if not os.path.exists(fn): continue
            for cover, (pk, jl) in (metrics(fn, lc) or {}).items():
                rows.append(dict(region=tag.replace('_', ' ').replace(' and The', ' & The'), site=int(site), year=y, sensor=sensor, cover=cover, peak=pk, july=jl))
d = pd.DataFrame(rows)
for c in ('peak', 'july'):
    d[c + '_z'] = d.groupby(['region', 'site', 'cover', 'sensor'])[c].transform(
        lambda s: (s - s[d.loc[s.index, 'year'] <= 2021].mean()) / s[d.loc[s.index, 'year'] <= 2021].std())
d['S'] = d[['peak_z', 'july_z']].mean(axis=1)
site = d.groupby(['region', 'site', 'year', 'sensor']).S.mean().unstack('sensor').dropna()
reg = site.groupby(['region', 'year']).mean()
r_reg = stats.pearsonr(reg.Terra, reg.Aqua)[0]
gap = (site.Terra - site.Aqua).groupby('year').mean()
slope = stats.linregress(gap.index, gap.values)
yr = reg.groupby('year').mean().round(2)
res = dict(n_site_years=len(site), r_region_year=r_reg, r_site_year=stats.pearsonr(site.Terra, site.Aqua)[0],
           gap_trend_per_year=slope.slope, gap_trend_p=slope.pvalue, gap_by_year=gap.round(2).to_dict(),
           national_by_year={int(y): dict(Terra=r.Terra, Aqua=r.Aqua) for y, r in yr.iterrows()},
           shock_2025_26_both=bool((yr.loc[[2025, 2026]] < -1).all().all()))
json.dump(res, open(f'{OUT}/crosscheck_aqua.json', 'w'), indent=2, default=float)
reg.reset_index().to_csv(f'{OUT}/crosscheck_region_terra_aqua.csv', index=False)
print(json.dumps(res, indent=1, default=lambda x: round(float(x), 3)))

# ---- same check, cropland and grassland separately (site x cover series; regions with >= 2 sites) ----
sc = d.groupby(['region', 'site', 'cover', 'year', 'sensor']).S.mean().unstack('sensor').dropna().reset_index()
by = {}
for cov, g in sc.groupby('cover'):
    nsite = g.groupby('region').site.nunique(); keep = nsite[nsite >= 2].index
    rg = g[g.region.isin(keep)].groupby(['region', 'year'])[['Terra', 'Aqua']].mean()
    gap_c = (g.Terra - g.Aqua).groupby(g.year).mean(); sl = stats.linregress(gap_c.index, gap_c.values)
    nat = g.groupby('year')[['Terra', 'Aqua']].mean().round(2)
    by[cov] = dict(n_series=int(g.groupby(['region', 'site']).ngroups), n_regions=len(keep),
                   r_region_year=stats.pearsonr(rg.Terra, rg.Aqua)[0], r_site_year=stats.pearsonr(g.Terra, g.Aqua)[0],
                   gap_trend_per_year=sl.slope, gap_trend_p=sl.pvalue,
                   national_by_year={int(y): dict(Terra=r.Terra, Aqua=r.Aqua) for y, r in nat.iterrows()},
                   shock_2025_26_both=bool((nat.loc[[2025, 2026]] < -1).all().all()),
                   region_2022_2026={rgn: {s: [round(v, 1) for v in rg.loc[rgn].loc[2022:2026, s]] for s in ('Terra', 'Aqua')} for rgn in keep})
    rg.reset_index().assign(cover=cov).to_csv(f'{OUT}/crosscheck_region_terra_aqua_{cov}.csv', index=False)
json.dump(by, open(f'{OUT}/crosscheck_aqua_by_cover.json', 'w'), indent=2, default=float)
for cov, v in by.items():
    print(cov, {k: (round(x, 3) if isinstance(x, float) else x) for k, x in v.items() if k not in ('national_by_year', 'region_2022_2026')})
    print('  national', {y: (round(a['Terra'], 2), round(a['Aqua'], 2)) for y, a in v['national_by_year'].items() if y >= 2018})
    for rgn, s in v['region_2022_2026'].items(): print('  ', rgn, 'T', s['Terra'], 'A', s['Aqua'])
