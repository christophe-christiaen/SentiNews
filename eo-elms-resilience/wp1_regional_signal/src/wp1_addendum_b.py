"""WP1 protocol addendum B (written 14 October 2026, before this ran): monthly Sentinel-2 features, weather clipped
to the training range, damage-only signs on weather, a compound-drought term, bounded ridge regression. Scored by
leave-one-year-out 2017-2025 against the first-run Sentinel-2 + weather model. 2026 is shown as an illustration only:
Defra's 2026 figures were known when the addendum was written, so 2026 is not a test.

Output  wp1_regional_signal/results/wp1_addendum_b.md, wp1_addendum_b.json
"""
import json, os
import numpy as np, pandas as pd
from scipy.optimize import lsq_linear
from sklearn.preprocessing import StandardScaler
import wp1_nowcast as w

RES = w.RES
ALPHAS = [1, 3, 10, 30, 100, 300, 1000]
DRY = [2018, 2020, 2022, 2025]
MONTHS = {'Mar': (1, 2), 'Apr': (3, 4), 'May': (5, 6), 'Jun': (7, 8), 'Jul': (9, 10), 'Aug': (11, 12)}
WX = w.WEATHER + ['compound']
SIGN = {'hot_days_28': (-np.inf, 0), 'spring_anom_pct': (0, np.inf), 'soil_moist_z': (0, np.inf),
        'winter_anom_pct': (-np.inf, 0), 'compound': (-np.inf, 0)}


def monthly(f, kmax):
    out = f[['crop', 'region', 'year', 'parcels'] + w.WEATHER].copy()
    for i in w.IDX:
        for m, (k1, k2) in MONTHS.items():
            ks = [k for k in (k1, k2) if k <= kmax]
            if ks:
                out[f'{i}_{m}'] = f[[f'{i}_p{k:02d}' for k in ks]].mean(axis=1)
    out['compound'] = np.maximum(0, -f.spring_anom_pct / 20) * np.maximum(0, -f.soil_moist_z)
    return out


def eo_monthly(df):
    return [c for c in df.columns if c.split('_')[0] in w.IDX and c.split('_')[-1] in MONTHS]


def design(train, test, cols):
    a, b = w.anomalies(train, test, cols)
    for c in WX:                                    # no extrapolation: clip weather to the fold's training range
        lo, hi = a[c].min(), a[c].max(); a[c] = a[c].clip(lo, hi); b[c] = b[c].clip(lo, hi)
    sc = StandardScaler().fit(a.values)
    A, B = sc.transform(a.values), sc.transform(b.values)
    lb = np.array([SIGN.get(c, (-np.inf, np.inf))[0] for c in cols]); ub = np.array([SIGN.get(c, (-np.inf, np.inf))[1] for c in cols])
    return A, B, lb, ub


def bounded_ridge(X, y, alpha, lb, ub):
    n, p = X.shape
    Aug = np.vstack([X, np.sqrt(alpha) * np.eye(p)]); yy = np.concatenate([y - y.mean(), np.zeros(p)])
    r = lsq_linear(Aug, yy, bounds=(lb, ub))
    return r.x, y.mean()


def fit_predict(train, test, cols):
    ytr = (train.yield_t_ha - train.groupby('region').yield_t_ha.transform('mean')).values
    A, B, lb, ub = design(train, test, cols)
    yrs = train.year.values; best, err = ALPHAS[0], np.inf
    for al in ALPHAS:
        e = 0.0
        for g in np.unique(yrs):
            m = yrs == g
            tr, te = train[~m], train[m]
            Ai, Bi, lbi, ubi = design(tr, te, cols)
            yi = (tr.yield_t_ha - tr.groupby('region').yield_t_ha.transform('mean')).values
            b, c0 = bounded_ridge(Ai, yi, al, lbi, ubi)
            obs = te.yield_t_ha.values - tr.groupby('region').yield_t_ha.mean().reindex(te.region).values
            e += ((Bi @ b + c0 - obs) ** 2).sum()
        if e < err:
            best, err = al, e
    b, c0 = bounded_ridge(A, ytr, best, lb, ub)
    return B @ b + c0, dict(zip(cols, b)), best


def loyo(df, cols):
    rows = []
    for yv in w.YEARS:
        tr, te = df[df.year != yv], df[df.year == yv]
        p, _, _ = fit_predict(tr, te, cols)
        obs = te.yield_t_ha.values - tr.groupby('region').yield_t_ha.mean().reindex(te.region).values
        rows.append(pd.DataFrame({'region': te.region.values, 'year': yv, 'obs': obs, 'pred': p}))
    return pd.concat(rows, ignore_index=True)


def dry_scores(r):
    e = r.groupby('year')[['obs', 'pred']].mean(); err = e.pred - e.obs
    return dict(mean_error_dry=float(err.reindex(DRY).mean()), mae_dry=float(err.reindex(DRY).abs().mean()),
                error_2025=float(err.get(2025, np.nan)), by_year={int(k): round(float(v), 3) for k, v in err.items()})


def main():
    y = w.yields(); s2 = w.panel()
    feats = w.region_features(s2, 'crop')
    out = {'skill': {}, 'coefficients_full_fit': {}, 'illustration_2026': {}}
    for crop in w.CROPS:
        base = feats[feats.crop == crop].merge(y[y.crop == crop], on=['crop', 'region', 'year'])
        base = base[base.year.isin(w.YEARS)].reset_index(drop=True)
        for cut, k in [('mid-July', 9), ('end of August', 12)]:
            r0 = w.loyo(base, 's2+weather', k)
            mf = monthly(base, k).merge(base[['region', 'year', 'yield_t_ha']], on=['region', 'year'])
            cols = eo_monthly(mf) + WX
            r1 = loyo(mf, cols)
            s0, s1 = w.scores(r0) | dry_scores(r0), w.scores(r1) | dry_scores(r1)
            adopt = (s1['r2'] >= s0['r2'] - 0.02) and (s1['mae_dry'] < s0['mae_dry'])
            out['skill'][f'{crop} | {cut}'] = {'first run': s0, 'addendum B': s1, 'adopt for 2027': bool(adopt)}
            _, coef, al = fit_predict(mf, mf.iloc[:1], cols)
            out['coefficients_full_fit'][f'{crop} | {cut}'] = {'alpha': al, **{c: round(v, 3) for c, v in coef.items() if c in WX}}
            w.log(crop, cut, 'R2 %.3f -> %.3f' % (s0['r2'], s1['r2']), 'dry MAE %.2f -> %.2f' % (s0['mae_dry'], s1['mae_dry']), 'adopt', adopt)
    # 2026 illustration (not a test)
    check, preds = w.classify_2026(s2)
    sc = pd.read_csv(os.path.join(RES, 'wp1_score_2026.csv'))
    act = sc[sc.version.str.startswith('first')].drop_duplicates(['crop', 'region']).set_index(['crop', 'region']).actual
    for crop in w.CROPS:
        base = feats[feats.crop == crop].merge(y[y.crop == crop], on=['crop', 'region', 'year'])
        base = base[base.year.isin(w.YEARS)].reset_index(drop=True)
        for cut, k in [('mid-July', 9), ('end of August', 12)]:
            s = s2.loc[preds[k].index].assign(crop_pred=preds[k].values)
            t = w.region_features(s, 'crop_pred'); t = t[(t.crop == crop) & t.region.isin(base.region.unique())].reset_index(drop=True)
            mf = monthly(base, k).merge(base[['region', 'year', 'yield_t_ha']], on=['region', 'year'])
            mt = monthly(t, k)
            p, _, _ = fit_predict(mf, mt, eo_monthly(mf) + WX)
            nc = p + mf.groupby('region').yield_t_ha.mean().reindex(mt.region).values
            a = act.reindex(pd.MultiIndex.from_arrays([[crop] * len(mt), mt.region])).values
            out['illustration_2026'][f'{crop} | {cut}'] = {'nowcast_mean': float(np.mean(nc)), 'defra_mean': float(np.nanmean(a)),
                                                           'mean_error': float(np.nanmean(nc - a))}
    json.dump(out, open(os.path.join(RES, 'wp1_addendum_b.json'), 'w'), indent=1)
    first = json.load(open(os.path.join(RES, 'wp1_score_2026.csv'.replace('.csv', '.csv')), 'r')) if False else None
    L = ['# WP1 addendum B: no extrapolation, damage-only weather, compound drought', '',
         'Protocol addendum B ([protocol.md](protocol.md)), written 14 October 2026 before this ran. Leave-one-year-out over '
         '2017–2025, same scoring as the first run. Dry-spring years: 2018, 2020, 2022, 2025. Error = predicted minus Defra '
         '(England mean of regional anomalies, t/ha).', '',
         '| Crop | cutoff | R² first run | R² addendum B | dry-year mean error (first → B) | dry-year mean abs. error (first → B) | 2025 error (first → B) | adopt for 2027 |',
         '|---|---|---|---|---|---|---|---|']
    for k, v in out['skill'].items():
        c, cu = k.split(' | '); a, b = v['first run'], v['addendum B']
        L.append(f"| {c} | {cu} | {a['r2']:+.2f} | {b['r2']:+.2f} | {a['mean_error_dry']:+.2f} → {b['mean_error_dry']:+.2f} | "
                 f"{a['mae_dry']:.2f} → {b['mae_dry']:.2f} | {a['error_2025']:+.2f} → {b['error_2025']:+.2f} | {'yes' if v['adopt for 2027'] else 'no'} |")
    L += ['', '## Wheat, England error by year (mid-July)', '', '| Year | first run | addendum B |', '|---|---|---|']
    a, b = out['skill']['wheat | mid-July']['first run']['by_year'], out['skill']['wheat | mid-July']['addendum B']['by_year']
    L += [f'| {yv} | {a[yv]:+.2f} | {b[yv]:+.2f} |' for yv in sorted(a)]
    L += ['', '## Weather coefficients in the full fit (standardised, sign-constrained)', '', '| Crop, cutoff | penalty | ' + ' | '.join(WX) + ' |',
          '|---|---|' + '---|' * len(WX)] + \
         [f"| {k} | {v['alpha']} | " + ' | '.join(f"{v[c]:+.3f}" for c in WX) + ' |' for k, v in out['coefficients_full_fit'].items()]
    L += ['', '## 2026, illustration only (Defra known when the addendum was written; not a test)', '',
          '| Crop, cutoff | addendum B, mean of regions | Defra, mean of regions | error | first nowcast error |', '|---|---|---|---|---|']
    first_err = sc[sc.version.str.startswith('first')].groupby(['crop', 'cutoff']).error.mean()
    for k, v in out['illustration_2026'].items():
        c, cu = k.split(' | ')
        L.append(f"| {k} | {v['nowcast_mean']:.2f} | {v['defra_mean']:.2f} | {v['mean_error']:+.2f} | {first_err.get((c, cu), np.nan):+.2f} |")
    open(os.path.join(RES, 'wp1_addendum_b.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
