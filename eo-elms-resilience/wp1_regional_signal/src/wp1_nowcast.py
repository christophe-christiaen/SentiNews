"""WP1: Sentinel-2 regional yield nowcast, following wp1_regional_signal/results/protocol.md (written before any
yield comparison).

Region-year features from the parcels CROME puts in each crop; leave-one-year-out (LOYO) skill for five models at four
cutoffs; jackknife+ intervals; a 2026 nowcast using crop masks predicted from the Sentinel-2 profiles.

Input   shared/data/s2/s2_parcel_year.parquet; shared/data/parcels/parcel_panel.parquet;
        wp2_resilience/results/parcel_resilience.parquet (ITL1 region per parcel);
        shared/data/weather/{cell_year_shocks,parcel_era5_cell}.parquet; data/raw/cops.ods; data/processed/panel_yield.csv
Output  wp1_regional_signal/results/wp1_results.md, wp1_results.json, wp1_nowcast_2026.csv
        results/maps/wp1_nowcast.png
        wp1_regional_signal/data/region_features.parquet (gitignored)
"""
import json, os, re, time
import numpy as np, pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
D = os.path.join(ROOT, 'shared', 'data')
W1 = os.path.join(ROOT, 'wp1_regional_signal')
RES = os.path.join(W1, 'results')
YEARS = list(range(2017, 2026))
NOW = 2026
IDX = ('ndvi', 'ndre', 'ndmi')
CUTS = {'mid-May': 5, 'mid-June': 7, 'mid-July': 9, 'end of August': 12}
CROPS = {'wheat': ({'AC66', 'AC32'}, 'Regional_wheat'), 'winter barley': ({'AC63'}, 'Regional_winter_barley'),
         'spring barley': ({'AC01'}, 'Regional_spring_barley')}
DEFRA = {'North East': 'North East', 'North West': 'North West and Merseyside', 'Yorkshire and the Humber': 'Yorkshire & The Humber',
         'East Midlands': 'East Midlands', 'West Midlands': 'West Midlands', 'East of England': 'Eastern',
         'London': 'South East and London', 'South East': 'South East and London', 'South West': 'South West'}
REGIONS = sorted(set(DEFRA.values()))
WEATHER = ['spring_anom_pct', 'soil_moist_z', 'hot_days_28', 'winter_anom_pct']
ALPHAS = [0.1, 0.3, 1, 3, 10, 30, 100, 300, 1000]
log = lambda *a: print(time.strftime('%H:%M:%S'), *a, flush=True)


# ---------------------------------------------------------------- data
def yields():
    out = []
    x = pd.ExcelFile(os.path.join(ROOT, 'data', 'raw', 'cops.ods'), engine='odf')
    for crop, (_, sheet) in CROPS.items():
        w = pd.read_excel(x, sheet, header=None)
        hr = next(i for i in range(len(w)) if str(w.iloc[i, 0]).strip().startswith('Yields'))
        yrs = [int(str(v)[:4]) if re.fullmatch(r'(19|20)\d\d(\.0)?(\(\d\))?', str(v).strip()) else None for v in w.iloc[hr, 1:]]
        for r in range(hr + 1, len(w)):
            name = str(w.iloc[r, 0]).strip()
            if name in ('nan', '') or name.lower().startswith('tonnes'):
                break
            if name not in REGIONS:
                continue
            for c, y in enumerate(yrs, start=1):
                if y:
                    v = pd.to_numeric(w.iloc[r, c], errors='coerce')
                    if pd.notna(v):
                        out.append(dict(crop=crop, region=name, year=y, yield_t_ha=float(v)))
    return pd.DataFrame(out)


def panel():
    cols = ['parcref', 'year'] + [f'{i}_p{k:02d}' for k in range(1, 13) for i in IDX]
    s2 = pd.read_parquet(os.path.join(D, 's2', 's2_parcel_year.parquet'), columns=cols)
    reg = pd.read_parquet(os.path.join(ROOT, 'wp2_resilience', 'results', 'parcel_resilience.parquet'), columns=['parcref', 'region'])
    reg['region'] = reg.region.map(DEFRA)
    crops = pd.read_parquet(os.path.join(D, 'parcels', 'parcel_panel.parquet'), columns=['parcref'] + [f'crop_{y}' for y in YEARS])
    crops = crops.melt(id_vars='parcref', var_name='year', value_name='lucode')
    crops['year'] = crops.year.str[-4:].astype(int)
    cell = pd.read_parquet(os.path.join(D, 'weather', 'parcel_era5_cell.parquet'))[['parcref', 'cell_id_data']]
    s2 = s2.merge(reg, on='parcref', how='inner').merge(crops, on=['parcref', 'year'], how='left').merge(cell, on='parcref', how='left')
    lab = pd.Series('other', index=s2.index)
    for crop, (codes, _) in CROPS.items():
        lab[s2.lucode.isin(codes)] = crop
    s2['crop'] = lab.where(s2.year < NOW)
    return s2


def classify_2026(s2):
    """Crop masks for 2026 from Sentinel-2 profiles: one classifier per cutoff (k <= 9 for the mid-July nowcast,
    k <= 12 for end of August), trained on 2017-2024, checked on 2025."""
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.metrics import classification_report
    rng = np.random.default_rng(11)
    check, preds = {}, {}
    for kmax in (9, 12):
        X = [f'{i}_p{k:02d}' for k in range(1, kmax + 1) for i in IDX]
        tr = s2[(s2.year <= 2024)]
        tr = tr.iloc[rng.choice(len(tr), min(600_000, len(tr)), replace=False)]
        m = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.1, random_state=11).fit(tr[X], tr.crop)
        te = s2[s2.year == 2025]
        rep = classification_report(te.crop, m.predict(te[X]), output_dict=True, zero_division=0)
        check[kmax] = {c: {k: round(rep[c][k], 3) for k in ('precision', 'recall')} for c in list(CROPS) + ['other']}
        check[kmax]['accuracy'] = round(rep['accuracy'], 3)
        now = s2.year == NOW
        preds[kmax] = pd.Series(m.predict(s2.loc[now, X]), index=s2.index[now])
        log('classifier k<=%d: 2025 accuracy %.3f' % (kmax, rep['accuracy']))
    return check, preds


def region_features(s2, crop_col):
    """Median of each index per half-month, region-mean weather, parcel count; per region x season x crop."""
    shocks = pd.read_parquet(os.path.join(D, 'weather', 'cell_year_shocks.parquet'))[['cell_id', 'year'] + WEATHER]
    d = s2[s2[crop_col].isin(CROPS)].merge(shocks.rename(columns={'cell_id': 'cell_id_data'}), on=['cell_id_data', 'year'], how='left')
    vals = [f'{i}_p{k:02d}' for k in range(1, 13) for i in IDX]
    g = d.groupby([crop_col, 'region', 'year'])
    f = g[vals].median().join(g[WEATHER].mean()).join(g.size().rename('parcels'))
    f.index = f.index.set_names(['crop', 'region', 'year'])
    return f.reset_index()


# ---------------------------------------------------------------- models
def eo_cols(kmax):
    return [f'{i}_p{k:02d}' for k in range(1, kmax + 1) for i in IDX]


def anomalies(train, test, cols):
    """Subtract each region's training-year mean; missing values -> 0 (the training mean)."""
    mu = train.groupby('region')[cols].mean()
    a = lambda d: (d[cols] - mu.reindex(d.region).values).fillna(0.0)
    return a(train), a(test)


def fit_ridge(Xtr, ytr, groups):
    """Ridge with the penalty chosen by inner leave-one-year-out on the training years."""
    sc = StandardScaler().fit(Xtr)
    Z = sc.transform(Xtr)
    best, err = ALPHAS[0], np.inf
    for a in ALPHAS:
        e = 0.0
        for g in np.unique(groups):
            m = groups == g
            e += ((Ridge(alpha=a).fit(Z[~m], ytr[~m]).predict(Z[m]) - ytr[m]) ** 2).sum()
        if e < err:
            best, err = a, e
    return sc, Ridge(alpha=best).fit(Z, ytr), best


def predict(model, train, test, kmax):
    """One fold: returns predicted yield anomaly for test rows."""
    ytr = (train.yield_t_ha - train.groupby('region').yield_t_ha.transform('mean')).values
    if model == 'pilot':
        tr = train.assign(peak=train[[f'ndvi_p{k:02d}' for k in range(4, 10)]].max(axis=1))
        te = test.assign(peak=test[[f'ndvi_p{k:02d}' for k in range(4, 10)]].max(axis=1))
        a, b = anomalies(tr, te, ['peak'])
        slope = np.polyfit(a.peak.values, ytr, 1)
        return np.polyval(slope, b.peak.values)
    if model == 'modis':
        a, b = anomalies(train, test, ['modis_peak'])
        return np.polyval(np.polyfit(a.modis_peak.values, ytr, 1), b.modis_peak.values)
    cols = {'weather': WEATHER, 's2': eo_cols(kmax), 's2+weather': eo_cols(kmax) + WEATHER}[model]
    a, b = anomalies(train, test, cols)
    sc, m, _ = fit_ridge(a.values, ytr, train.year.values)
    return m.predict(sc.transform(b.values))


def loyo(df, model, kmax):
    rows = []
    for y in YEARS:
        tr, te = df[df.year != y], df[df.year == y]
        if te.empty:
            continue
        p = predict(model, tr, te, kmax)
        obs = te.yield_t_ha.values - tr.groupby('region').yield_t_ha.mean().reindex(te.region).values
        rows.append(pd.DataFrame({'region': te.region.values, 'year': y, 'obs': obs, 'pred': p}))
    return pd.concat(rows, ignore_index=True)


def scores(r):
    r2 = lambda o, p: 1 - ((o - p) ** 2).sum() / ((o - o.mean()) ** 2).sum()
    e = r.groupby('year')[['obs', 'pred']].mean()
    return dict(r2=float(r2(r.obs, r.pred)), rmse=float(np.sqrt(((r.obs - r.pred) ** 2).mean())),
                r=float(np.corrcoef(r.obs, r.pred)[0, 1]), r2_england=float(r2(e.obs, e.pred)),
                r_england=float(np.corrcoef(e.obs, e.pred)[0, 1]), n=int(len(r)))


def coverage(r, level):
    """Nested check of the interval width: for each held-out year, the width comes from the other years' residuals."""
    hit = []
    for y in YEARS:
        res = (r.obs - r.pred)[r.year != y].abs()
        q = np.quantile(res, level)
        cur = r[r.year == y]
        hit += list(((cur.obs - cur.pred).abs() <= q).values)
    return float(np.mean(hit))


def jackknife_plus(df, test, model, kmax, level):
    """Jackknife+ interval for each test row from the LOYO fold models and their residuals."""
    lo, hi, mid = [], [], []
    folds = []
    for y in YEARS:
        tr, ho = df[df.year != y], df[df.year == y]
        res = np.abs(ho.yield_t_ha.values - tr.groupby('region').yield_t_ha.mean().reindex(ho.region).values - predict(model, tr, ho, kmax))
        folds.append((predict(model, tr, test, kmax) + tr.groupby('region').yield_t_ha.mean().reindex(test.region).values, res))
    for j in range(len(test)):
        lows = np.concatenate([f[0][j] - f[1] for f in folds]); highs = np.concatenate([f[0][j] + f[1] for f in folds])
        lo.append(np.quantile(lows, 1 - level)); hi.append(np.quantile(highs, level))
    full = predict(model, df, test, kmax) + df.groupby('region').yield_t_ha.mean().reindex(test.region).values
    return full, np.array(lo), np.array(hi)


# ---------------------------------------------------------------- main
def main():
    y = yields()
    log('yields', y.groupby('crop').size().to_dict())
    s2 = panel()
    log('parcel-seasons', len(s2))
    check, preds = classify_2026(s2)
    feats = region_features(s2, 'crop')
    now = {}
    for kmax, p in preds.items():
        s = s2.loc[p.index].assign(crop_pred=p.values)
        now[kmax] = region_features(s, 'crop_pred')
    os.makedirs(os.path.join(W1, 'data'), exist_ok=True)
    feats.to_parquet(os.path.join(W1, 'data', 'region_features.parquet'), index=False)
    modis = pd.read_csv(os.path.join(ROOT, 'data', 'processed', 'panel_yield.csv'))[['region', 'year', 'peak']].rename(columns={'peak': 'modis_peak'})

    out = {'classifier_2025_check': check, 'skill': {}, 'coverage': {}}
    resid = {}
    for crop in CROPS:
        df = feats[feats.crop == crop].merge(y[y.crop == crop], on=['crop', 'region', 'year'])
        df = df[df.year.isin(YEARS)].merge(modis, on=['region', 'year'], how='left').reset_index(drop=True)
        out['skill'][crop] = {'region_years': int(len(df)), 'parcels_per_region_year_median': int(df.parcels.median())}
        for cut, k in CUTS.items():
            for model in ['pilot', 'weather', 's2', 's2+weather'] + (['modis'] if crop == 'wheat' and cut == 'mid-July' else []):
                if model in ('pilot', 'weather', 'modis') and cut != 'mid-July':
                    continue
                r = loyo(df, model, k)
                out['skill'][crop][f'{model} | {cut}'] = scores(r)
                resid[(crop, model, cut)] = r
                log(crop, model, cut, round(out['skill'][crop][f'{model} | {cut}']['r2'], 3))
        for model in ('s2', 's2+weather'):
            r = resid[(crop, model, 'mid-July')]
            out['coverage'][f'{crop} | {model}'] = {'80%': coverage(r, 0.8), '90%': coverage(r, 0.9)}

    # 2026 nowcast (wheat, all three crops reported), best of s2 / s2+weather chosen by mid-July LOYO R2 on 2017-2025
    rows = []
    for crop in CROPS:
        df = feats[feats.crop == crop].merge(y[y.crop == crop], on=['crop', 'region', 'year'])
        df = df[df.year.isin(YEARS)].reset_index(drop=True)
        best = max(('s2', 's2+weather'), key=lambda m: out['skill'][crop][f'{m} | mid-July']['r2'])
        for cut, k in [('mid-July', 9), ('end of August', 12)]:
            t = now[k][(now[k].crop == crop) & (now[k].region.isin(df.region.unique()))].reset_index(drop=True)
            mid, lo80, hi80 = jackknife_plus(df, t, best, k, 0.9)       # 80% central = 10%..90%
            _, lo90, hi90 = jackknife_plus(df, t, best, k, 0.95)
            avg = df.groupby('region').yield_t_ha.mean().reindex(t.region).values
            for j in range(len(t)):
                rows.append(dict(crop=crop, cutoff=cut, model=best, region=t.region[j], parcels=int(t.parcels[j]),
                                 nowcast_t_ha=round(mid[j], 2), lo80=round(lo80[j], 2), hi80=round(hi80[j], 2),
                                 lo90=round(lo90[j], 2), hi90=round(hi90[j], 2), mean_2017_2025=round(avg[j], 2)))
    nc = pd.DataFrame(rows)
    nc.to_csv(os.path.join(RES, 'wp1_nowcast_2026.csv'), index=False)
    out['nowcast_written'] = time.strftime('%Y-%m-%d %H:%M')
    json.dump(out, open(os.path.join(RES, 'wp1_results.json'), 'w'), indent=1)
    report(out, nc)
    figure(out, nc, resid)
    log('done')


def report(o, nc):
    L = ['# WP1 results: Sentinel-2 regional yield nowcast', '',
         'Run of [protocol.md](protocol.md) (written before any yield comparison). Leave-one-year-out over 2017–2025, 8 '
         'English Defra regions; R² of the yield anomaly against each region\'s training-year mean. Aggregates only.', '']
    for crop, s in o['skill'].items():
        L += [f'## {crop.capitalize()} ({s["region_years"]} region-years; median {s["parcels_per_region_year_median"]:,} parcels per region-year)', '',
              '| Model | cutoff | R² | RMSE (t/ha) | r | England R² | England r |', '|---|---|---|---|---|---|---|']
        for k, v in s.items():
            if '|' in k:
                m, c = k.split(' | ')
                L.append(f'| {m} | {c} | {v["r2"]:+.2f} | {v["rmse"]:.2f} | {v["r"]:+.2f} | {v["r2_england"]:+.2f} | {v["r_england"]:+.2f} |')
        L.append('')
    L += ['## Interval coverage (mid-July, nested leave-one-year-out)', '', '| Crop, model | 80% | 90% |', '|---|---|---|'] + \
         [f'| {k} | {v["80%"]:.0%} | {v["90%"]:.0%} |' for k, v in o['coverage'].items()]
    L += ['', '## Crop classifier check (trained 2017–2024, tested on CROME 2025)', '',
          '| Cutoff | accuracy | wheat P / R | winter barley P / R | spring barley P / R |', '|---|---|---|---|---|']
    for k, v in o['classifier_2025_check'].items():
        L.append(f"| k ≤ {k} | {v['accuracy']:.3f} | " + ' | '.join(f"{v[c]['precision']:.2f} / {v[c]['recall']:.2f}" for c in CROPS) + ' |')
    w = nc[(nc.crop == 'wheat')]
    L += ['', f'## 2026 nowcast (written {o["nowcast_written"]}, before any official 2026 regional figure was looked at)', '',
          '| Crop | cutoff | region | nowcast (t/ha) | 80% interval | 90% interval | 2017–2025 mean |', '|---|---|---|---|---|---|---|'] + \
         [f'| {r.crop} | {r.cutoff} | {r.region} | {r.nowcast_t_ha:.2f} | {r.lo80:.2f}–{r.hi80:.2f} | {r.lo90:.2f}–{r.hi90:.2f} | {r.mean_2017_2025:.2f} |'
          for r in nc.itertuples()]
    open(os.path.join(RES, 'wp1_results.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


def figure(o, nc, resid):
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    DARK, BODY, GREEN, OCHRE, BLUE, RULE, BG = '#1C2620', '#4A554E', '#2F6B4F', '#9A5F14', '#5B7F95', '#D6D0C2', '#F6F4EE'
    fig, ax = plt.subplots(1, 3, figsize=(17, 6.4), gridspec_kw={'width_ratios': [1, 1, 1.15]})
    fig.patch.set_facecolor(BG)
    for x in ax:
        x.set_facecolor(BG); x.spines[['top', 'right']].set_visible(False); x.spines[['left', 'bottom']].set_color(RULE)
        x.tick_params(colors=BODY, labelsize=11)
    s = o['skill']['wheat']; cuts = list(CUTS)
    for m, col, lab in [('s2', GREEN, 'Sentinel-2'), ('s2+weather', BLUE, 'Sentinel-2 + weather')]:
        ax[0].plot(range(4), [s[f'{m} | {c}']['r2'] for c in cuts], 'o-', color=col, lw=2.5, ms=8, label=lab)
    for m, col, lab, ls in [('pilot', OCHRE, 'Sentinel-2 peak NDVI only (pilot-style)', '--'), ('modis', DARK, 'MODIS pilot, same years', ':'),
                            ('weather', '#8C8C8C', 'Weather only (whole season)', '-.')]:
        ax[0].axhline(s[f'{m} | mid-July']['r2'], color=col, ls=ls, lw=1.6, label=lab)
    ax[0].axhline(0, color=BODY, lw=0.8)
    ax[0].set_xticks(range(4), cuts); ax[0].set_ylabel('out-of-sample R², yield anomaly', color=BODY, fontsize=11)
    ax[0].set_title('Wheat: skill by date of the last image', loc='left', fontsize=13.5, fontweight='bold', color=DARK)
    ax[0].legend(frameon=False, fontsize=9.5, loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=2)
    ax[0].set_ylim(-0.1, 0.75)
    best = max(('s2', 's2+weather'), key=lambda m: s[f'{m} | mid-July']['r2'])
    r = resid[('wheat', best, 'mid-July')]
    ax[1].scatter(r.obs, r.pred, s=40, color=GREEN, alpha=0.8, edgecolor='white', lw=0.5)
    lim = [min(r.obs.min(), r.pred.min()) - 0.2, max(r.obs.max(), r.pred.max()) + 0.2]
    ax[1].plot(lim, lim, color=RULE, lw=1.2)
    for yy in (2018, 2020, 2022, 2025):
        q = r[r.year == yy]
        ax[1].annotate(str(yy), (q.obs.mean(), q.pred.mean()), fontsize=10, color=OCHRE, ha='center', va='bottom', xytext=(0, 6), textcoords='offset points')
    ax[1].set_xlabel('Defra yield anomaly (t/ha)', color=BODY, fontsize=11); ax[1].set_ylabel('predicted by mid-July (t/ha)', color=BODY, fontsize=11)
    ax[1].set_title(f'Wheat, held-out years (R² {s[best + " | mid-July"]["r2"]:.2f})', loc='left', fontsize=13.5, fontweight='bold', color=DARK)
    w = nc[(nc.crop == 'wheat') & (nc.cutoff == 'end of August')].sort_values('nowcast_t_ha')
    yy = np.arange(len(w))
    ax[2].hlines(yy, w.lo80, w.hi80, color=GREEN, lw=6, alpha=0.35)
    ax[2].plot(w.nowcast_t_ha, yy, 'o', color=GREEN, ms=9, label='2026 nowcast (80% interval)')
    ax[2].plot(w.mean_2017_2025, yy, '|', color=OCHRE, ms=16, mew=2.5, label='2017–2025 mean')
    ax[2].set_yticks(yy, w.region, fontsize=10.5, color=DARK)
    ax[2].set_xlabel('wheat yield, t/ha', color=BODY, fontsize=11)
    ax[2].set_title('2026 wheat nowcast by region', loc='left', fontsize=13.5, fontweight='bold', color=DARK)
    ax[2].legend(frameon=False, fontsize=9.5, loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=2)
    fig.tight_layout(w_pad=2.5)
    fig.savefig(os.path.join(ROOT, 'results', 'maps', 'wp1_nowcast.png'), dpi=170, facecolor=BG)


if __name__ == '__main__':
    main()
