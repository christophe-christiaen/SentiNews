"""Field resilience score for lenders: which cereal parcels are likely to be hit hard next season, with reasons, and
a stranding watch-list. Built only from information available at the scoring date, back-tested on later seasons.

Design (fixed before the back-test was run)
  Unit         cereal-land parcel (381,400), scored as of the end of each season t (after the August images)
  Features     (known at t)  stress S_t; stress debt D_t (WP2: D_t = 0.5 D_{t-1} + min(S_t, 0)); mean S in past shock
               seasons (resistance); mean S in calm seasons after a shock (recovery); share of past seasons with
               S <= -1; volatility of S; share of dry or heat shocks in the parcel's ERA5 cell over the last 10
               seasons (ERA5-Land, independent of the crop). Flood zone and peat were removed from the score on
               17 October 2026 (they lower, not raise, drought stress); they stay in the watch-list as exposure.
  Targets      at t+1: (A) hit hard, S_{t+1} <= -1; (B) among the worst 20% of its region at t+1;
               (C) depth of the next hit: S_{t+1} when t+1 is a shock season for the parcel's cell
  Models       baseline: region only; baseline: current stress only (the pilot outreach rule); transparent score
               (equal-weight average of percentile ranks, no fitting); fitted score (logistic regression, standardised)
  Back-test    rolling origin: score as of t = 2020..2025, trained only on as-of seasons before t; plus leave-one-
               region-out for the fitted score. Metrics: AUC, precision and lift in the top 20%, Spearman with (C)
  Output       2026 score (0-100 national percentile), band, two main reasons per parcel, from whichever of the
               transparent and fitted scores did better in the back-test (decided after the back-test: the transparent
               score, AUC 0.63 vs 0.57, better in 5 of 6 seasons);
               watch-list = high or very high risk and Flood Zone 3 or deep peat
Limits: the target is crop stress seen from space, not a financial outcome; linking to arrears and overdraft use needs
the bank's data (step 4 of the score design). The score is for prompting a conversation, not an automated decision.

Input   shared/data/s2/s2_parcel_year.parquet; shared/data/parcels/parcel_risk.parquet;
        shared/data/weather/cell_year_shocks.parquet; wp2_resilience/results/parcel_resilience.parquet (region, x, y)
Output  results/lender/lender_score_backtest.md, lender_score.json (aggregates; safe to commit)
        results/maps/lender_score.png
        data/lender/parcel_score_2026.parquet (per parcel; gitignored, not published)
"""
import json, os, time
import numpy as np, pandas as pd
from scipy.stats import spearmanr
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
D = os.path.join(ROOT, 'shared', 'data')
OUT = os.path.join(ROOT, 'results', 'lender')
PRIV = os.path.join(ROOT, 'data', 'lender')
LAM, FLAG = 0.5, 0.2
FEATS = ['S', 'D', 'resist', 'recov', 'hit_share', 'vol', 'shock_freq']
# Flood zone and peat are not in the crop-stress score: on the MODIS long-baseline panel these fields hold up *better*
# in drought and heat seasons (wp2_resilience/results/wp2_supporting.md, W1). They measure flood and rewetting
# exposure, which is kept for the stranding watch-list (high crop-stress score and Flood Zone 3 or deep peat).
EXPOSURE = ['fz3', 'fz2', 'deep_peat', 'peat']
NAMES = {'S': 'stressed this season', 'D': 'lasting below-normal level', 'resist': 'held up poorly in past shocks',
         'recov': 'slow to recover after past shocks', 'hit_share': 'often hit hard', 'vol': 'unstable season to season',
         'fz3': 'Flood Zone 3', 'fz2': 'Flood Zone 2', 'deep_peat': 'deep peat', 'peat': 'shallow peat',
         'shock_freq': 'frequent weather shocks locally'}
# direction: +1 = higher value means more risk (used for the transparent score and reasons)
SIGN = {'S': -1, 'D': -1, 'resist': -1, 'recov': -1, 'hit_share': 1, 'vol': 1, 'fz3': 1, 'fz2': 1, 'deep_peat': 1,
        'peat': 1, 'shock_freq': 1}
log = lambda *a: print(time.strftime('%H:%M:%S'), *a, flush=True)


def build():
    p = pd.read_parquet(os.path.join(D, 's2', 's2_parcel_year.parquet'),
                        columns=['parcref', 'year', 'ndvi_july_z', 'ndvi_peak_z', 'cell_id_data', 'dry_shock', 'heat_shock'])
    p['S'] = p[['ndvi_july_z', 'ndvi_peak_z']].mean(axis=1).clip(-6, 6)
    p['shock'] = p.dry_shock.fillna(False).astype(bool) | p.heat_shock.fillna(False).astype(bool)
    return features(p)


def features(p):
    """History features and next-season targets from a panel with parcref, year, S, shock, cell_id_data."""
    p = p.sort_values(['parcref', 'year']).reset_index(drop=True)
    # stress debt
    s = p.S.fillna(0).values; first = p.parcref.values != np.roll(p.parcref.values, 1)
    d = np.zeros(len(p)); prev = 0.0
    for i in range(len(p)):
        prev = (0.0 if first[i] else prev) * LAM + min(s[i], 0.0); d[i] = prev
    p['D'] = d
    g = p.groupby('parcref', sort=False)
    cum = lambda v: v.fillna(0).groupby(p.parcref, sort=False).cumsum()
    cnt = lambda v: v.notna().astype(int).groupby(p.parcref, sort=False).cumsum()
    sh = p.S.where(p.shock)
    p['resist'] = cum(sh) / cnt(sh).replace(0, np.nan)
    rec = p.S.where(g.shock.shift(1).fillna(False).astype(bool) & ~p.shock)
    p['recov'] = cum(rec) / cnt(rec).replace(0, np.nan)
    n = cnt(p.S).replace(0, np.nan)
    p['hit_share'] = cum((p.S <= -1).astype(float).where(p.S.notna())) / n
    m1, m2 = cum(p.S) / n, cum(p.S ** 2) / n
    p['vol'] = np.sqrt((m2 - m1 ** 2).clip(lower=0) * n / (n - 1).replace(0, np.nan))
    # local shock frequency over the last 10 seasons (weather only)
    w = pd.read_parquet(os.path.join(D, 'weather', 'cell_year_shocks.parquet'))[['cell_id', 'year', 'dry_shock', 'heat_shock']]
    w['sh'] = (w.dry_shock | w.heat_shock).astype(float)
    w = w.sort_values(['cell_id', 'year'])
    w['shock_freq'] = w.groupby('cell_id').sh.transform(lambda v: v.rolling(10, min_periods=5).mean())
    p = p.merge(w[['cell_id', 'year', 'shock_freq']].rename(columns={'cell_id': 'cell_id_data'}), on=['cell_id_data', 'year'], how='left')
    r = pd.read_parquet(os.path.join(D, 'parcels', 'parcel_risk.parquet'))
    r['fz3'] = (r.flood_zone.fillna(0).astype(int) == 3).astype(float)
    r['fz2'] = (r.flood_zone.fillna(0).astype(int) == 2).astype(float)
    pc = r.peat_class.fillna('').str.lower()
    r['deep_peat'] = pc.str.contains('deep').astype(float)
    r['peat'] = (pc.str.len().gt(0) & ~pc.str.contains('deep')).astype(float)
    reg = pd.read_parquet(os.path.join(ROOT, 'wp2_resilience', 'results', 'parcel_resilience.parquet'), columns=['parcref', 'region', 'x', 'y'])
    p = p.merge(r[['parcref', 'fz3', 'fz2', 'deep_peat', 'peat']], on='parcref', how='left').merge(reg, on='parcref', how='left')
    p = p.sort_values(['parcref', 'year']).reset_index(drop=True)
    g = p.groupby('parcref', sort=False)
    p['S_next'] = g.S.shift(-1)
    p['shock_next'] = g.shock.shift(-1)
    p['hit_next'] = (p.S_next <= -1).where(p.S_next.notna())
    p['worst_next'] = (p.groupby(['region', 'year']).S_next.rank(pct=True) <= FLAG).where(p.S_next.notna())
    return p


def fill(X, ref):
    """Missing history (e.g. no past shock yet) -> median of the training rows."""
    return X.fillna(ref.median())


def ranks(X, ref):
    """Mid-rank percentile of each feature against the reference rows, oriented so higher = more risk. Ties (e.g. all
    parcels outside a flood zone, or filled-in medians) share the middle rank, so a common value sits near 0.5."""
    out = pd.DataFrame(index=X.index)
    for c in FEATS:
        v = SIGN[c] * X[c].values; r = np.sort(SIGN[c] * ref[c].values)
        out[c] = (np.searchsorted(r, v, side='left') + np.searchsorted(r, v, side='right')) / (2 * len(r))
    return out


def transparent(X, ref):
    """Equal-weight average of the oriented mid-rank percentiles."""
    return ranks(X, ref).mean(axis=1).values


def fit(train):
    sc = StandardScaler().fit(train[FEATS])
    m = LogisticRegression(max_iter=1000, C=1.0).fit(sc.transform(train[FEATS]), train.hit_next.astype(int))
    return sc, m


def metrics(score, df):
    out = {}
    for t in ('hit_next', 'worst_next'):
        ok = df[t].notna().values
        y = df[t].values[ok].astype(bool); s = score[ok]
        top = s >= np.quantile(s, 1 - FLAG)
        out[t] = dict(auc=float(roc_auc_score(y, s)), precision_top20=float(y[top].mean()), base_rate=float(y.mean()),
                      lift=float(y[top].mean() / y.mean()), recall_top20=float(top[y].mean()))
    c = df.shock_next.fillna(False).astype(bool).values & df.S_next.notna().values
    out['depth_next_hit_spearman'] = float(spearmanr(-score[c], df.S_next.values[c]).correlation) if c.sum() > 100 else None
    return out


def backtest(p):
    rows, coefs = [], []
    for t in range(2020, 2026):
        tr = p[(p.year >= 2018) & (p.year < t) & p.hit_next.notna()]
        te = p[(p.year == t) & p.hit_next.notna()].copy()
        trX, teX = fill(tr[FEATS], tr[FEATS]), fill(te[FEATS], tr[FEATS])
        sc, m = fit(tr.assign(**{c: trX[c] for c in FEATS}))
        reg_rate = tr.groupby('region').hit_next.mean()
        scores = {'Region only (baseline)': reg_rate.reindex(te.region).fillna(tr.hit_next.mean()).values,
                  'Current stress only (pilot rule)': -te.S.fillna(te.S.median()).values,
                  'Transparent score (no fitting)': transparent(teX, trX),
                  'Fitted score (logistic)': m.predict_proba(sc.transform(teX))[:, 1]}
        for name, s in scores.items():
            rows.append(dict(year=t, model=name, **{f'{k}_{kk}': vv for k, v in metrics(s, te).items()
                                                    for kk, vv in (v.items() if isinstance(v, dict) else [('', v)])}))
        coefs.append(dict(zip(FEATS, m.coef_[0])))
        log('as of', t, {r['model'][:12]: round(r['hit_next_auc'], 3) for r in rows[-4:]})
    return pd.DataFrame(rows), pd.DataFrame(coefs).mean()


def leave_region_out(p):
    out = {}
    d = p[(p.year >= 2018) & (p.year <= 2025) & p.hit_next.notna() & p.region.notna()]
    for r in sorted(d.region.unique()):
        tr, te = d[d.region != r], d[d.region == r]
        trX, teX = fill(tr[FEATS], tr[FEATS]), fill(te[FEATS], tr[FEATS])
        sc, m = fit(tr.assign(**{c: trX[c] for c in FEATS}))
        out[r] = float(roc_auc_score(te.hit_next.astype(bool), m.predict_proba(sc.transform(teX))[:, 1]))
    return out


def score_2026(p):
    tr = p[(p.year >= 2018) & (p.year <= 2025) & p.hit_next.notna()]
    trX = fill(tr[FEATS], tr[FEATS])
    sc, m = fit(tr.assign(**{c: trX[c] for c in FEATS}))
    now = p[p.year == 2026].copy()
    X = fill(now[FEATS], tr[FEATS])
    R = ranks(X, trX)
    now['risk'] = R.mean(axis=1).values
    now['score'] = (now.risk.rank(pct=True) * 100).round(1)
    now['band'] = pd.cut(now.score, [-1, 50, 75, 90, 100.1], labels=['low', 'medium', 'high', 'very high'])
    top = np.argsort(-(R.values - 0.5), axis=1)[:, :2]
    now['reason_1'] = [NAMES[FEATS[i]] for i in top[:, 0]]
    now['reason_2'] = [NAMES[FEATS[i]] for i in top[:, 1]]
    now['watch'] = now.band.isin(['high', 'very high']) & ((now.fz3 == 1) | (now.deep_peat == 1))
    return now, dict(zip(FEATS, m.coef_[0]))


def main():
    p = build()
    log('parcel-seasons', len(p))
    chk = p[(p.year >= 2018) & (p.year <= 2025) & p.hit_next.notna()].assign(fp=lambda d: ((d.fz3 == 1) | (d.deep_peat == 1)))
    fp_check = chk.groupby('fp').hit_next.mean().rename({True: 'Flood Zone 3 or deep peat', False: 'other'}).to_dict()
    bt, coef_avg = backtest(p)
    lro = leave_region_out(p)
    log('leave-region-out', {k: round(v, 3) for k, v in lro.items()})
    now, coef = score_2026(p)
    os.makedirs(PRIV, exist_ok=True); os.makedirs(OUT, exist_ok=True)
    now[['parcref', 'region', 'x', 'y', 'score', 'band', 'reason_1', 'reason_2', 'watch', 'fz3', 'deep_peat', 'D', 'S']].to_parquet(
        os.path.join(PRIV, 'parcel_score_2026.parquet'), index=False)
    summ = bt.groupby('model').mean(numeric_only=True).drop(columns='year')
    out = {'flood_peat_check_hit_next_rate': fp_check, 'score_used_2026': 'transparent (equal-weight mid-rank percentiles)', 'backtest_mean_2020_2025': summ.round(4).to_dict('index'), 'backtest_by_year': bt.round(4).to_dict('records'),
           'leave_region_out_auc': lro, 'coefficients_2026_model': coef,
           'bands_2026': now.band.value_counts().sort_index().to_dict(),
           'reasons_2026_high_or_very_high': now[now.band.isin(['high', 'very high'])].reason_1.value_counts().to_dict(),
           'watchlist_2026': {'parcels': int(now.watch.sum()), 'by_region': now[now.watch].region.value_counts().to_dict()},
           'high_or_very_high_by_region': now.assign(h=now.band.isin(['high', 'very high'])).groupby('region').h.mean().round(3).to_dict()}
    json.dump(out, open(os.path.join(OUT, 'lender_score.json'), 'w'), indent=1, default=float)
    report(out, summ, bt)
    figure(now, summ)
    log('done')


def report(o, summ, bt):
    L = ['# Field resilience score: back-test and 2026 scores', '',
         'Design fixed before the back-test (see the docstring of `src/lender_score.py`). Scores use only information '
         'available at the end of each season; the back-test scores seasons 2020–2025 with models trained on earlier '
         'seasons only and checks them against the next season. **The target is crop stress seen from space, not a '
         'financial outcome**; linking to arrears needs the bank\'s data. Aggregates only.', '',
         '## Back-test, mean over scoring seasons 2020–2025', '',
         '| Model | hit hard next season: AUC | precision in top 20% | lift | recall | worst 20% of region next season: AUC | lift | depth of next hit: Spearman |',
         '|---|---|---|---|---|---|---|---|']
    for m, r in summ.iterrows():
        sp = r.get('depth_next_hit_spearman_')
        L.append(f"| {m} | {r.hit_next_auc:.3f} | {r.hit_next_precision_top20:.1%} | {r.hit_next_lift:.2f} | {r.hit_next_recall_top20:.1%} | "
                 f"{r.worst_next_auc:.3f} | {r.worst_next_lift:.2f} | {sp:+.3f} |")
    base = summ.hit_next_base_rate.iloc[0]
    L += ['', f'Base rate of a hard hit next season: {base:.1%} (varies with the weather of each season).', '',
          '## By scoring season (AUC, hit hard next season)', '',
          bt.pivot(index='year', columns='model', values='hit_next_auc').round(3).to_markdown(), '',
          '## Fitted score held out by region (AUC, trained on the other regions)', '',
          '| Region | AUC |', '|---|---|'] + [f'| {k} | {v:.3f} |' for k, v in o['leave_region_out_auc'].items()]
    fc = o['flood_peat_check_hit_next_rate']
    L += ['', f"**Flood zone and peat are not in the score** (changed 17 October 2026). In the back-test data, fields in Flood "
          f"Zone 3 or on deep peat were hit hard the next season {fc['Flood Zone 3 or deep peat']:.1%} of the time, other "
          f"fields {fc['other']:.1%}; on the MODIS long panel they hold up better in drought seasons (WP2, W1). They stay "
          'in the stranding watch-list as flood and rewetting exposure.']
    L += ['', '**The 2026 scores use the transparent score**, which did better than the fitted one in the back-test (chosen '
          'after the back-test). Its weights are equal by design; the fitted coefficients below are for information.',
          '', '## What drives the fitted score (standardised coefficients, 2026 model)', '', '| Feature | coefficient |', '|---|---|'] + \
         [f'| {NAMES[k]} | {v:+.3f} |' for k, v in sorted(o['coefficients_2026_model'].items(), key=lambda kv: -abs(kv[1]))]
    L += ['', '## 2026 scores', '', '| Band (national percentile) | parcels |', '|---|---|'] + \
         [f'| {k} | {v:,} |' for k, v in o['bands_2026'].items()] + \
         ['', 'Main reason, high and very high bands:', '', '| Reason | parcels |', '|---|---|'] + \
         [f'| {k} | {v:,} |' for k, v in o['reasons_2026_high_or_very_high'].items()] + \
         ['', 'Share of parcels high or very high, by region:', '', '| Region | share |', '|---|---|'] + \
         [f'| {k} | {v:.0%} |' for k, v in sorted(o['high_or_very_high_by_region'].items(), key=lambda kv: -kv[1])] + \
         ['', f"**Stranding watch-list** (high or very high, and Flood Zone 3 or deep peat): {o['watchlist_2026']['parcels']:,} parcels.", '',
          '| Region | parcels |', '|---|---|'] + [f'| {k} | {v:,} |' for k, v in o['watchlist_2026']['by_region'].items()]
    open(os.path.join(OUT, 'lender_score_backtest.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


def figure(now, summ):
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import geopandas as gpd
    from matplotlib.colors import LinearSegmentedColormap
    DARK, BODY, GREEN, OCHRE, RULE, BG = '#1C2620', '#4A554E', '#2F6B4F', '#9A5F14', '#D6D0C2', '#F6F4EE'
    fig, ax = plt.subplots(1, 2, figsize=(15, 7.4), gridspec_kw={'width_ratios': [1, 1.05]})
    fig.patch.set_facecolor(BG)
    a = ax[0]; a.set_facecolor(BG); a.spines[['top', 'right']].set_visible(False); a.spines[['left', 'bottom']].set_color(RULE)
    order = ['Region only (baseline)', 'Current stress only (pilot rule)', 'Transparent score (no fitting)', 'Fitted score (logistic)']
    cols = ['#8C8C8C', OCHRE, '#5B7F95', GREEN]
    a.barh(range(4), [summ.loc[m, 'hit_next_lift'] for m in order], color=cols)
    for i, m in enumerate(order):
        a.text(summ.loc[m, 'hit_next_lift'] + 0.03, i, f"lift {summ.loc[m, 'hit_next_lift']:.2f} · AUC {summ.loc[m, 'hit_next_auc']:.2f}",
               va='center', fontsize=11, color=DARK)
    a.set_yticks(range(4), order, fontsize=11.5, color=DARK); a.invert_yaxis(); a.axvline(1, color=BODY, lw=0.8)
    a.set_xlim(0, max(summ.hit_next_lift) * 1.45)
    a.set_xlabel('share of next season\'s hard hits in the flagged 20%, vs random', color=BODY, fontsize=11)
    a.set_title('Back-test 2020–2025: flag 20% of fields;\nhow many of next season\'s hard hits are among them?', loc='left', fontsize=13, fontweight='bold', color=DARK)
    b = ax[1]; b.set_facecolor(BG); b.axis('off')
    eng = gpd.read_file(os.path.join(ROOT, 'data', 'raw', 'boundaries', 'itl1_2021_buc.geojson')).to_crs(27700)
    eng = eng[eng.ITL121CD.str.match(r'TL[C-K]')]
    eng.boundary.plot(ax=b, color='#9AA39D', lw=0.6)
    h = now.assign(hx=(now.x // 5000).astype(int), hy=(now.y // 5000).astype(int), hi=now.band.isin(['high', 'very high']))
    gr = h.groupby(['hx', 'hy']).agg(share=('hi', 'mean'), n=('hi', 'size')).reset_index()
    gr = gr[gr.n >= 20]
    cmap = LinearSegmentedColormap.from_list('r', ['#EFE8D6', '#D9B26B', '#9A5F14', '#5A3208'])
    sca = b.scatter(gr.hx * 5000 + 2500, gr.hy * 5000 + 2500, c=gr.share, cmap=cmap, s=9, marker='s', vmin=0, vmax=0.6)
    w = now[now.watch]
    b.scatter(w.x, w.y, s=0.25, color='#1C2620', alpha=0.35, lw=0)
    b.set_aspect('equal')
    b.set_title('2026: share of fields high or very high (5 km)\ndots: watch-list (also Flood Zone 3 or deep peat)',
                loc='left', fontsize=13, fontweight='bold', color=DARK)
    cb = fig.colorbar(sca, ax=b, fraction=0.03, pad=0.01); cb.ax.tick_params(labelsize=10, colors=BODY)
    cb.ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    fig.tight_layout()
    fig.savefig(os.path.join(ROOT, 'results', 'maps', 'lender_score.png'), dpi=170, facecolor=BG)


if __name__ == '__main__':
    main()
