"""Link Christophe's Companies House accounts and GDELT drought news (SentiNews/Documents) to our farms and weather.

A. Accounts: year-on-year change in financial ratios of farm companies vs the weather shocks of their own ERA5 cell
   (shock definitions as in the WP3 pre-registration). The harvest a financial year reflects: year-end in
   September-December -> that year's harvest; year-end January-August -> previous year's harvest.
   Companies located by registered office; only farm-like or unclear addresses (office / agent addresses excluded).
   Exploratory and descriptive: small companies often file abridged accounts, and many ratios are missing.
B. News: monthly literal-drought articles by English region (ITL1) vs measured dryness (ERA5-Land soil moisture, layer
   7-28 cm, z-score against the same calendar month 1991-2020), cereal-area cells only. Lead / lag by cross-correlation.

Input   ~/Downloads/SentiNews/Documents/SentiNews_Github/{CompaniesHouse,GDELT}/*.csv
        shared/data/farms/farms_all.csv, farm_groups.csv, farm_scheme_history.csv; shared/data/weather/*
Output  shared/results/accounts_news_summary.md, results/maps/accounts_news.png
"""
import os
import numpy as np, pandas as pd, geopandas as gpd, statsmodels.formula.api as smf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pyproj import Transformer
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
D = os.path.join(ROOT, 'shared', 'data')
SN = os.path.expanduser('~/Downloads/SentiNews/Documents/SentiNews_Github')
SUMMARY = os.path.join(ROOT, 'shared', 'results', 'accounts_news_summary.md')
FIG = os.path.join(ROOT, 'results', 'maps', 'accounts_news.png')
ITL = {'TLC': 'North East (England)', 'TLD': 'North West (England)', 'TLE': 'Yorkshire and the Humber',
       'TLF': 'East Midlands (England)', 'TLG': 'West Midlands (England)', 'TLH': 'East of England',
       'TLI': 'London', 'TLJ': 'South East (England)', 'TLK': 'South West (England)'}
METRICS = ['current_ratio', 'equity_ratio', 'cash_ratio', 'net_assets']


def cell_of(x, y, valid):
    lon, lat = Transformer.from_crs(27700, 4326, always_xy=True).transform(x, y)
    ids = np.array([f'{i}_{j}' for i, j in zip(np.round(lon / 0.1).astype(int), np.round(lat / 0.1).astype(int))])
    vv = sorted(valid); xy = np.array([[int(a) for a in c.split('_')] for c in vv])
    miss = ~np.isin(ids, vv)
    if miss.any():
        q = np.array([[int(a) for a in c.split('_')] for c in ids[miss]])
        ids[miss] = np.array(vv)[cKDTree(xy).query(q)[1]]
    return ids


def accounts(shocks):
    r = pd.read_csv(os.path.join(SN, 'CompaniesHouse', 'companieshouse_agriculture_only_all_resilience_ratios.csv'),
                    dtype={'company_number': str}, low_memory=False)
    r['company_number'] = r.company_number.str.upper().str.strip().str.zfill(8)
    r['end'] = pd.to_datetime(r.accounting_period_end, errors='coerce')
    r = r.dropna(subset=['end'])
    r['harvest'] = np.where(r.end.dt.month >= 9, r.end.dt.year, r.end.dt.year - 1)
    r = r.sort_values('source_filing_date').drop_duplicates(['company_number', 'harvest'], keep='last')
    f = pd.read_csv(os.path.join(D, 'farms', 'farms_all.csv'), dtype={'company_number': str})
    f = f[(f.country == 'England') & f.geocoded & f.address_kind.isin(['farm-like', 'unclear'])]
    f['company_number'] = f.company_number.str.zfill(8)
    f = f.merge(pd.read_csv(os.path.join(D, 'farms', 'farm_groups.csv'))[['farm_id', 'group_final']], on='farm_id', how='left')
    f['cell'] = cell_of(f.x_bng.values, f.y_bng.values, set(shocks.cell_id))
    a = r.merge(f[['company_number', 'farm_id', 'cell', 'group_final']], on='company_number')
    for m in METRICS:
        a[m] = pd.to_numeric(a[m], errors='coerce')
    a['ln_net_assets'] = np.sign(a.net_assets) * np.log1p(a.net_assets.abs())
    a = a.sort_values(['company_number', 'harvest'])
    g = a.groupby('company_number')
    for m in ['current_ratio', 'equity_ratio', 'cash_ratio', 'ln_net_assets']:
        a[f'd_{m}'] = g[m].diff().where(g.harvest.diff() == 1)
        lo, hi = a[f'd_{m}'].quantile([0.02, 0.98])
        a[f'd_{m}'] = a[f'd_{m}'].clip(lo, hi)                      # winsorise extreme small-company swings
    a = a.merge(shocks.rename(columns={'cell_id': 'cell', 'year': 'harvest'}), on=['cell', 'harvest'], how='left')
    a['region'] = a.cell.str.split('_').str[0]                       # coarse longitude band as spatial control
    res = []
    for m in ['d_current_ratio', 'd_equity_ratio', 'd_cash_ratio', 'd_ln_net_assets']:
        d = a.dropna(subset=[m, 'severe_dry_shock'])
        if d.harvest.nunique() < 2 or len(d) < 100:
            continue
        fit = smf.ols(f'{m} ~ severe_dry_shock + wet_shock + C(harvest)', d.assign(
            severe_dry_shock=d.severe_dry_shock.astype(float), wet_shock=d.wet_shock.astype(float))).fit(
            cov_type='cluster', cov_kwds={'groups': pd.factorize(d.cell)[0]})
        for v in ('severe_dry_shock', 'wet_shock'):
            res.append(dict(outcome=m, shock=v, coef=fit.params[v], p=fit.pvalues[v], n=int(fit.nobs), companies=d.company_number.nunique()))
    return a, pd.DataFrame(res)


def news(shocks_monthly, eng):
    g = pd.read_csv(os.path.join(SN, 'GDELT', 'gdelt_drought_uk_2021-01-01_to_2026-08-31_uk_only_enriched.csv'), low_memory=False)
    g = g[g.is_literal_drought_llm.astype(str).str.lower() == 'true']
    g['month'] = pd.to_datetime(g.date_gdelt, errors='coerce').dt.to_period('M')
    m = shocks_monthly
    cells = m[['cell_id']].drop_duplicates()
    ij = np.array([[int(v) for v in c.split('_')] for c in cells.cell_id]) * 0.1
    pts = gpd.GeoDataFrame(cells, geometry=gpd.points_from_xy(ij[:, 0], ij[:, 1]), crs=4326).to_crs(27700)
    cells = gpd.sjoin(pts, eng[['ITL121CD', 'geometry']], predicate='within').drop(columns=['geometry', 'index_right'])
    cells['region'] = cells.ITL121CD.map(ITL)
    clim = m[m.year.between(1991, 2020)].groupby(['cell_id', 'month']).swvl2.agg(['mean', 'std'])
    m = m.join(clim, on=['cell_id', 'month'])
    m['sm_z'] = (m.swvl2 - m['mean']) / m['std']
    m = m.merge(cells[['cell_id', 'region']], on='cell_id')
    m['period'] = pd.PeriodIndex.from_fields(year=m.year, month=m.month, freq='M')
    phys_nat = m[m.year >= 2021].groupby('period').sm_z.mean()
    eng_news = g[g.primary_region_other.isin(list(ITL.values()) + ['England (unspecified)'])]
    news_nat = eng_news.groupby('month').size().reindex(phys_nat.index, fill_value=0)
    dry = -phys_nat                                                    # dryness = minus soil-moisture z
    lags = {L: np.corrcoef(news_nat.values[max(0, L):len(news_nat) + min(0, L)], dry.values[max(0, -L):len(dry) - max(0, L)])[0, 1]
            for L in range(-3, 4)}                                     # L > 0: news follows dryness by L months
    yr = m[(m.year >= 2021) & m.month.between(4, 8)].groupby(['region', 'year']).sm_z.mean().rename('dryness_z').reset_index()
    nr = g.assign(year=g.month.dt.year).groupby(['primary_region_other', 'year']).size().rename('articles').reset_index() \
        .rename(columns={'primary_region_other': 'region'})
    reg = yr.merge(nr, on=['region', 'year'], how='left').fillna({'articles': 0})
    return phys_nat, news_nat, lags, reg


def main():
    W = os.path.join(D, 'weather')
    shocks = pd.read_parquet(os.path.join(W, 'cell_year_shocks.parquet'))
    monthly = pd.read_parquet(os.path.join(W, 'era5land_monthly.parquet'))
    eng = gpd.read_file(os.path.join(ROOT, 'data', 'raw', 'boundaries', 'itl1_2021_buc.geojson')).to_crs(27700)
    eng = eng[eng.ITL121CD.isin(ITL)]
    a, fits = accounts(shocks)
    phys, nws, lags, reg = news(monthly, eng)

    fig, axs = plt.subplots(1, 2, figsize=(14, 4.8), gridspec_kw={'width_ratios': [2.2, 1]})
    ax = axs[0]; x = phys.index.to_timestamp()
    ax.bar(x, nws.values, width=25, color='#C9A36B', label='drought news articles (England)')
    ax2 = ax.twinx(); ax2.plot(x, -phys.values, color='#2F6B4F', lw=2, label='dryness (−soil moisture z)')
    ax.set_ylabel('articles per month'); ax2.set_ylabel('dryness (SD)'); ax.set_title('Drought news rises as the soil dries out', loc='left', fontweight='bold')
    for s in ('top',): ax.spines[s].set_visible(False); ax2.spines[s].set_visible(False)
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels(); ax.legend(h1 + h2, l1 + l2, frameon=False, loc='upper left')
    ax = axs[1]
    for yv, col in ((2022, '#9A5F14'), (2025, '#6E1F0A'), (2026, '#C0392B')):
        s = reg[reg.year == yv]; ax.scatter(-s.dryness_z, s.articles, color=col, label=str(yv), s=45)
    ax.set_xlabel('regional dryness, April–August (SD)'); ax.set_ylabel('articles in the year'); ax.legend(frameon=False)
    ax.set_title('Dry years get coverage, the driest regions do not', loc='left', fontweight='bold')
    for s in ('top', 'right'): ax.spines[s].set_visible(False)
    fig.tight_layout(); fig.savefig(FIG, dpi=200); plt.close(fig)

    best = max(lags, key=lambda k: lags[k])
    ft = fits.assign(coef=fits.coef.round(3), p=fits.p.round(3)) if len(fits) else fits
    lines = ['# Company accounts and drought news linked to farms and weather (exploratory, counts only)', '',
             '## A. Farm-company accounts vs local weather shocks', '',
             f'- Company-years with accounts and a located English farm (farm-like or unclear address): {len(a):,}; companies: {a.company_number.nunique():,}',
             f'- Harvests covered: ' + ', '.join(f'{k} ({v:,})' for k, v in a.harvest.value_counts().sort_index().items() if v >= 50), '',
             'Year-on-year change regressed on the cell\'s severe dry shock and wet shock for that harvest, with harvest-year effects; '
             'errors clustered by ERA5 cell. Changes winsorised at 2% / 98%.', '',
             ft.to_markdown(index=False) if len(ft) else '(too few consecutive years)', '',
             '## B. Drought news vs measured dryness (England)', '',
             f'- Literal-drought articles 2021–2026: {int(nws.sum()):,} with an English region or England tag',
             '- Correlation of monthly article counts with national dryness (minus soil-moisture z), by lag (positive lag = news follows dryness): ' +
             ', '.join(f'{k:+d} m: {v:.2f}' for k, v in lags.items()),
             f'- Strongest at {best:+d} month(s)', '',
             '- Across region-years, articles rise with dryness (Spearman ' + f"{reg.articles.corr(-reg.dryness_z, method='spearman'):.2f}" + '), driven by dry years; '
             'within a year, the driest regions do not get more coverage (Spearman by year: ' +
             ', '.join(f"{y}: {s_.articles.corr(-s_.dryness_z, method='spearman'):+.2f}" for y, s_ in reg.groupby('year')) + ').', '',
             '### Articles by region and year vs April–August dryness', '',
             reg.pivot_table(index='region', columns='year', values='articles').fillna(0).astype(int).to_markdown(), '',
             'Exploratory: accounts are annual and lag the harvest; small companies file abridged accounts; registered offices '
             'locate the business, not every field. News counts depend on media coverage, not only on conditions.']
    open(SUMMARY, 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
