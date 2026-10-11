"""WP2: resilience of England's cereal land to weather shocks, per parcel, 2017-2026 (Sentinel-2 + ERA5-Land).

No scheme-group comparisons here (those belong to WP3 and its pre-registration).

Stress index S (per parcel-season) = mean of the July-NDVI and peak-NDVI z-scores against the parcel's own 2017-2020
seasons (as in the pilot: peak + July). Stress debt D_t = LAM * D_{t-1} + min(S_t, 0).
Shock seasons are defined from weather for the parcel's ERA5 cell (dry or heat shock, pre-registration section 5).
  resistance  = S in a shock season (higher = held up better)
  recovery    = S in the season after a shock season that is itself not a shock season
Typology (2018-2026, crop response, same rules as the pilot): persistent (3+ consecutive seasons S < -0.5 including
one <= -1), back-to-back (S <= -1 in consecutive seasons), slow (2-season episode), bounced back, little affected;
headline class: repeated stress = persistent or back-to-back.

Tests (parcel level, cell x season effects absorbed by demeaning, errors clustered by ERA5 cell):
  T1 legacy            S_t on S_{t-1}
  T2 hit harder        S_t on S_{t-1}, shock seasons only
  T3 debt slows rebound (S_{t+1} - S_t) on D_{t-1}, controlling S_t, shock seasons followed by a non-shock season
Output: wp2_resilience/results/parcel_resilience.parquet, wp2_resilience_summary.md, maps in results/maps/
"""
import os
import numpy as np, pandas as pd, geopandas as gpd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
D = os.path.join(ROOT, 'shared', 'data')
OUT = os.path.join(ROOT, 'wp2_resilience', 'results')
MAPS = os.path.join(ROOT, 'results', 'maps')
SHOCK, RECOV, LAM = -1.0, -0.5, 0.5
ENG = ['TLC', 'TLD', 'TLE', 'TLF', 'TLG', 'TLH', 'TLI', 'TLJ', 'TLK']
ITL = {'TLC': 'North East', 'TLD': 'North West', 'TLE': 'Yorkshire and the Humber', 'TLF': 'East Midlands',
       'TLG': 'West Midlands', 'TLH': 'East of England', 'TLI': 'London', 'TLJ': 'South East', 'TLK': 'South West'}


def load():
    p = pd.read_parquet(os.path.join(D, 's2', 's2_parcel_year.parquet'),
                        columns=['parcref', 'year', 'ndvi_july_z', 'ndvi_peak_z', 'cell_id_data', 'dry_shock', 'heat_shock'])
    p['S'] = p[['ndvi_july_z', 'ndvi_peak_z']].mean(axis=1).clip(-6, 6).astype('float32')
    p['shock'] = (p.dry_shock.fillna(False) | p.heat_shock.fillna(False))
    p = p.sort_values(['parcref', 'year']).reset_index(drop=True)
    return p


def add_debt(p, lam):
    s = p.S.fillna(0).values; first = (p.parcref.values != np.roll(p.parcref.values, 1))
    d = np.zeros(len(p), dtype='float32'); prev = 0.0
    for i in range(len(p)):
        prev = (0.0 if first[i] else prev) * lam + min(s[i], 0.0)
        d[i] = prev
    return d


def typology(g):
    """g: S values 2018-2026 in season order for one parcel (numpy)."""
    below, run, runs = g < RECOV, 0, []
    for i, b in enumerate(below):
        if b:
            run += 1
        else:
            if run: runs.append((i - run, run))
            run = 0
    if run: runs.append((len(g) - run, run))
    eps = [(st, L) for st, L in runs if (g[st:st + L] <= SHOCK).any()]
    shock_idx = np.where(g <= SHOCK)[0]
    if any(L >= 3 for _, L in eps): return 'Persistent stress'
    if len(shock_idx) and np.any(np.diff(shock_idx) == 1): return 'Back-to-back hits'
    if any(L == 2 for _, L in eps): return 'Slow recovery'
    if eps: return 'Bounced back'
    return 'Little affected'


def within(df, cols, group):
    """Demean columns within group (absorbs cell x season effects)."""
    m = df.groupby(group)[cols].transform('mean')
    return df[cols] - m


def ols_cluster(y, X, cl):
    """OLS without intercept on demeaned data; cluster-robust SE by cl."""
    X = np.asarray(X, float); y = np.asarray(y, float)
    XtX_inv = np.linalg.inv(X.T @ X); b = XtX_inv @ X.T @ y; e = y - X @ b
    codes = pd.factorize(cl)[0]; G = codes.max() + 1
    S = np.zeros((G, X.shape[1])); np.add.at(S, codes, X * e[:, None])
    V = XtX_inv @ (S.T @ S) @ XtX_inv * G / (G - 1)
    se = np.sqrt(np.diag(V)); from scipy.stats import norm
    return b, se, 2 * (1 - norm.cdf(np.abs(b / se))), G


def tests(p, lam):
    p = p.copy(); p['D'] = add_debt(p, lam)
    g = p.groupby('parcref')
    p['S_lag'] = g.S.shift(1); p['D_lag'] = g.D.shift(1); p['S_next'] = g.S.shift(-1)
    p['shock_next'] = g.shock.shift(-1)
    p['cy'] = p.cell_id_data.astype(str) + '_' + p.year.astype(str)
    out = {}
    a = p.dropna(subset=['S', 'S_lag', 'cell_id_data'])
    w = within(a, ['S', 'S_lag'], 'cy'); b, se, pv, G = ols_cluster(w.S, w[['S_lag']], a.cell_id_data)
    out['T1_legacy'] = dict(coef=b[0], se=se[0], p=pv[0], n=len(a), clusters=G)
    s = a[a.shock]
    w = within(s, ['S', 'S_lag'], 'cy'); b, se, pv, G = ols_cluster(w.S, w[['S_lag']], s.cell_id_data)
    out['T2_hit_harder'] = dict(coef=b[0], se=se[0], p=pv[0], n=len(s), clusters=G)
    r = p[p.shock & (p.shock_next == False)].dropna(subset=['S', 'S_next', 'D_lag', 'cell_id_data']).copy()
    r['rebound'] = r.S_next - r.S
    w = within(r, ['rebound', 'D_lag', 'S'], 'cy'); b, se, pv, G = ols_cluster(w.rebound, w[['D_lag', 'S']], r.cell_id_data)
    out['T3_debt_slows_rebound'] = dict(coef=b[0], se=se[0], p=pv[0], n=len(r), clusters=G)
    return out, p


def maps(res, eng):
    fig, axs = plt.subplots(1, 2, figsize=(13, 7.6))
    for ax, (col, title, sub, cmap, vmin, vmax, fmt) in zip(axs, [
        ('repeated', 'Repeated stress, 2018–2026', 'Share of cereal parcels with persistent stress or back-to-back hits',
         LinearSegmentedColormap.from_list('r', ['#EFE7D6', '#D7A869', '#9A5F14', '#5E3A0C']), 0, 1, lambda v, _: f'{v:.0%}'),
        ('debt_2026', 'Stress debt in 2026', 'Accumulated shortfall carried into 2026 (median, SD units; darker = deeper)',
         LinearSegmentedColormap.from_list('d', ['#3B2306', '#7A4A12', '#C98A3E', '#ECD9B5', '#F7F1E4']), -2.5, 0, None)]):
        eng.plot(ax=ax, facecolor='#ECE9E1', edgecolor='none', zorder=0)
        h = ax.hexbin(res.x, res.y, C=res[col].astype(float), gridsize=106, extent=(130_000, 660_000, 0, 670_000), cmap=cmap,
                      vmin=vmin, vmax=vmax, mincnt=5, linewidths=0, reduce_C_function=np.median if col == 'debt_2026' else np.mean, zorder=2)
        eng.boundary.plot(ax=ax, color='white', linewidth=0.8, zorder=3)
        ax.set_xlim(130_000, 660_000); ax.set_ylim(0, 670_000); ax.set_aspect('equal'); ax.axis('off')
        ax.set_title(title, loc='left', fontsize=15, fontweight='bold'); ax.text(0, 1.0, sub, transform=ax.transAxes, fontsize=10.5, color='#4A554E', va='top')
        cb = fig.colorbar(h, ax=ax, orientation='horizontal', fraction=0.035, pad=0.01, shrink=0.75, format=fmt)
        cb.outline.set_visible(False); cb.ax.tick_params(labelsize=9, colors='#4A554E', length=0)
    fig.text(0.01, 0.01, f'Sentinel-2 L2A (Earth Engine), {len(res):,} cereal-land parcels; stress = July and peak NDVI vs the parcel\'s 2017–2020 seasons. '
             '5 km hexagons, fewer than 5 parcels hidden.', fontsize=8.5, color='#4A554E')
    fig.patch.set_facecolor('#F6F4EE')
    for a in axs: a.set_facecolor('#F6F4EE')
    f = os.path.join(MAPS, 'wp2_resilience_types_debt.png'); fig.savefig(f, dpi=200, bbox_inches='tight', facecolor='#F6F4EE'); plt.close(fig)
    return f


def main():
    os.makedirs(OUT, exist_ok=True)
    p = load()
    base, p = tests(p, LAM)
    sens = {lam: tests(load(), lam)[0]['T3_debt_slows_rebound'] for lam in (0.3, 0.7)}

    seasons = p[p.year >= 2018]
    typ = seasons.groupby('parcref').S.apply(lambda s: typology(s.fillna(0).values)).rename('typology')
    shock_s = p[p.shock & (p.year >= 2018)]
    res = pd.DataFrame({'typology': typ,
                        'resistance': shock_s.groupby('parcref').S.mean(),
                        'shocks_2018_2026': shock_s.groupby('parcref').size(),
                        'debt_2026': p[p.year == 2026].set_index('parcref').D}).reset_index()
    rec = p[p.shock & (p.shock_next == False)].dropna(subset=['S_next'])
    res = res.merge(rec.groupby('parcref').S_next.mean().rename('recovery'), on='parcref', how='left')
    res['repeated'] = res.typology.isin(['Persistent stress', 'Back-to-back hits'])
    xy = pd.read_parquet(os.path.join(D, 'parcels', 'parcel_panel.parquet'), columns=['parcref', 'x', 'y'])
    res = res.merge(xy, on='parcref')
    eng = gpd.read_file(os.path.join(ROOT, 'data', 'raw', 'boundaries', 'itl1_2021_buc.geojson')).to_crs(27700)
    eng = eng[eng.ITL121CD.isin(ENG)]
    pts = gpd.GeoDataFrame(res[['parcref']], geometry=gpd.points_from_xy(res.x, res.y), crs=27700)
    res['region'] = gpd.sjoin(pts, eng[['ITL121CD', 'geometry']], predicate='within', how='left').groupby(level=0).ITL121CD.first().map(ITL).values
    res.to_parquet(os.path.join(OUT, 'parcel_resilience.parquet'), index=False)
    f = maps(res, eng)

    yearly = p.groupby('year').agg(S=('S', 'median'), shock=('shock', 'mean'), D=('D', 'median'))
    reg = res.groupby('region').agg(parcels=('parcref', 'size'), repeated=('repeated', 'mean'), resistance=('resistance', 'median'),
                                    recovery=('recovery', 'median'), debt_2026=('debt_2026', 'median')).sort_values('debt_2026')
    fmt = lambda d: f"{d['coef']:+.3f} (SE {d['se']:.3f}, p {'<0.001' if d['p'] < 0.001 else f'{d[chr(112)]:.3f}'}; n {d['n']:,}, cells {d['clusters']:,})"
    lines = ['# WP2 · Parcel-level resilience of England\'s cereal land, 2017–2026 (no scheme-group comparisons)', '',
             f'- Parcels: {len(res):,}; parcel-seasons: {len(p):,}. Stress index S = mean of July and peak NDVI z-scores vs each parcel\'s 2017–2020 seasons.',
             '- Shock seasons from ERA5-Land (dry or heat shock for the parcel\'s cell, pre-registration definitions).', '',
             '## Tests (cell × season effects absorbed; errors clustered by ERA5 cell)', '',
             f'- **T1 legacy** (S_t on S_t−1): {fmt(base["T1_legacy"])}',
             f'- **T2 unrecovered land is hit harder** (shock seasons): {fmt(base["T2_hit_harder"])}',
             f'- **T3 stress debt slows rebound** (carry-over 0.5): {fmt(base["T3_debt_slows_rebound"])}',
             '- T3 with carry-over 0.3: ' + fmt(sens[0.3]) + '; 0.7: ' + fmt(sens[0.7]), '',
             'Pilot comparison (50 MODIS sites): T1 +0.12, T2 +0.35, T3 0.31 (suggestive, threshold-dependent).', '',
             '## Resilience types, 2018–2026 (share of cereal parcels)', '',
             res.typology.value_counts(normalize=True).round(3).rename_axis('').to_frame('share').to_markdown(), '',
             f'- **Repeated stress** (persistent or back-to-back): {res.repeated.mean():.1%} of cereal parcels', '',
             '## By region', '', reg.round(3).to_markdown(), '',
             '## National medians by season', '', yearly.round(3).to_markdown(), '',
             f'Map: {os.path.relpath(f, ROOT)}. Caveats: the 2017–2020 baseline contains the 2018 and 2020 droughts, so z-scores are relative '
             'to a recent, not a drought-free, normal; 2017 has thin coverage; parcel points sample the field centre (15 m).']
    open(os.path.join(OUT, 'wp2_resilience_summary.md'), 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
