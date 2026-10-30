"""WP1 protocol addendum E (written 29 October 2026; clarifications recorded 30 October 2026, before any degree-day value
was fetched): E1 heat as degree-days above 30 C; E2 sign-constrained weather inside the fit (as addendum B, with the
degree-day term in place of hot days); E3 an out-of-range flag (coefficient-weighted distance to the nearest training
region-season); E4 distance-weighted conformal 80% intervals. Judged on 2017-2025 against the model in use for each crop
and cutoff; 2026 is a fair test of the flag only (inputs, no yields), and the E2/E4 nowcast for 2026 is an illustration.

Input   shared/data/weather/era5land_degreedays.parquet (fetch_era5land_degreedays.py) and the WP1 inputs
Output  wp1_regional_signal/results/wp1_addendum_e.md, wp1_addendum_e.json
"""
import json, os
import numpy as np, pandas as pd
from sklearn.preprocessing import StandardScaler
import wp1_nowcast as w
import wp1_addendum_b as ab
import wp1_addendum_c as ac

RES, D = w.RES, w.D
EXTREME = [2018, 2022, 2025]
OTHER = [2017, 2019, 2020, 2021, 2023, 2024]
LEVEL = 0.80
WX = ['spring_anom_pct', 'soil_moist_z', 'dd30', 'winter_anom_pct', 'compound']
SIGN = {'dd30': (-np.inf, 0), 'spring_anom_pct': (0, np.inf), 'soil_moist_z': (0, np.inf),
        'winter_anom_pct': (-np.inf, 0), 'compound': (-np.inf, 0)}
DD = {9: 'dd30_jul15', 12: 'dd30_aug31'}
CUTS = [('mid-July', 9), ('end of August', 12)]


# ---------------------------------------------------------------- data
def region_dd(s2, crop_col):
    dd = pd.read_parquet(os.path.join(D, 'weather', 'era5land_degreedays.parquet')).rename(columns={'cell_id': 'cell_id_data'})
    d = s2[s2[crop_col].isin(w.CROPS)][[crop_col, 'region', 'year', 'cell_id_data']].merge(dd, on=['cell_id_data', 'year'], how='left')
    return d.groupby([crop_col, 'region', 'year'])[list(DD.values())].mean().rename_axis(['crop', 'region', 'year']).reset_index()


def e_features(f, k, dd):
    """Addendum B's monthly Sentinel-2 features and weather, with degree-days to the cutoff in place of hot days."""
    m = ab.monthly(f, k).merge(dd[['crop', 'region', 'year', DD[k]]], on=['crop', 'region', 'year'], how='left')
    return m.rename(columns={DD[k]: 'dd30'}).drop(columns=['hot_days_28'])


# ---------------------------------------------------------------- E2: sign-constrained ridge (as addendum B)
def design(train, test, cols):
    a, b = w.anomalies(train, test, cols)
    for c in WX:
        lo, hi = a[c].min(), a[c].max(); a[c] = a[c].clip(lo, hi); b[c] = b[c].clip(lo, hi)
    sc = StandardScaler().fit(a.values)
    lb = np.array([SIGN.get(c, (-np.inf, np.inf))[0] for c in cols]); ub = np.array([SIGN.get(c, (-np.inf, np.inf))[1] for c in cols])
    return sc.transform(a.values), sc.transform(b.values), lb, ub


def anom(tr, te):
    return te.yield_t_ha.values - tr.groupby('region').yield_t_ha.mean().reindex(te.region).values


def fit(train, cols):
    """Penalty by inner leave-one-year-out; returns a predictor working in the training design space."""
    yrs = train.year.values; best, err = ab.ALPHAS[0], np.inf
    for al in ab.ALPHAS:
        e = 0.0
        for g in np.unique(yrs):
            tr, te = train[yrs != g], train[yrs == g]
            A, B, lb, ub = design(tr, te, cols)
            b, c0 = ab.bounded_ridge(A, anom(tr, tr), al, lb, ub)
            e += ((B @ b + c0 - anom(tr, te)) ** 2).sum()
        if e < err:
            best, err = al, e
    A, _, lb, ub = design(train, train.iloc[:1], cols)
    b, c0 = ab.bounded_ridge(A, anom(train, train), best, lb, ub)
    return dict(b=b, c0=c0, alpha=best, A=A, train=train, cols=cols)


def predict(m, test):
    _, B, _, _ = design(m['train'], test, m['cols'])
    return B @ m['b'] + m['c0'], B


# ---------------------------------------------------------------- E3 and E4 helpers
def wdist(X, Y, wt):
    """Coefficient-weighted Euclidean distances between rows of X and rows of Y."""
    Xw, Yw = X * wt, Y * wt
    return np.sqrt(((Xw[:, None, :] - Yw[None, :, :]) ** 2).sum(-1))


def di(m, B):
    wt = np.abs(m['b']); dtr = wdist(m['A'], m['A'], wt)
    scale = dtr[np.triu_indices(len(dtr), 1)].mean()
    return wdist(B, m['A'], wt).min(1) / scale


def wquantile(res, wts, level):
    """Weighted conformal quantile with the test point's own weight (1) placed at +infinity."""
    o = np.argsort(res); r, p = res[o], wts[o] / (wts.sum() + 1.0)
    c = np.cumsum(p); i = np.searchsorted(c, level)
    return r[i] if i < len(r) else np.inf


def inner(train, cols):
    """Inner leave-one-year-out within the training years: out-of-fold residuals and DIs of the training region-seasons."""
    res, dis = np.full(len(train), np.nan), np.full(len(train), np.nan)
    yrs = train.year.values
    for g in np.unique(yrs):
        tr, te = train[yrs != g], train[yrs == g]
        m = fit(tr, cols); p, B = predict(m, te)
        res[yrs == g] = anom(tr, te) - p
        dis[yrs == g] = di(m, B)
    return res, dis


def threshold(dis):
    q1, q3 = np.quantile(dis, [0.25, 0.75])
    return q3 + 1.5 * (q3 - q1)


def run_e(df, cols):
    """Leave-one-year-out over 2017-2025 with E2 predictions, E3 flags and E4 intervals per held-out region-season."""
    rows = []
    for yv in w.YEARS:
        tr, te = df[df.year != yv].reset_index(drop=True), df[df.year == yv].reset_index(drop=True)
        m = fit(tr, cols); p, B = predict(m, te)
        res, dis = inner(tr, cols)
        thr = threshold(dis)
        wt = np.abs(m['b']); dtr = wdist(m['A'], m['A'], wt); h = np.median(dtr[np.triu_indices(len(dtr), 1)])
        dte = wdist(B, m['A'], wt)
        q_w = [wquantile(np.abs(res), np.exp(-dte[i] ** 2 / (2 * h ** 2)), LEVEL) for i in range(len(te))]
        q_u = wquantile(np.abs(res), np.ones(len(res)), LEVEL)
        obs = anom(tr, te)
        rows.append(pd.DataFrame({'region': te.region, 'year': yv, 'obs': obs, 'pred': p, 'di': di(m, B), 'thr': thr,
                                  'q_w': q_w, 'q_u': q_u}))
    return pd.concat(rows, ignore_index=True)


def eng_err(r, years):
    e = r.groupby('year')[['obs', 'pred']].mean(); err = e.pred - e.obs
    return float(err.reindex(years).abs().mean())


# ---------------------------------------------------------------- current models (the comparison)
def current(crop, cut, k, base, mf_b):
    if crop == 'spring barley':
        return ab.loyo(mf_b, ab.eo_monthly(mf_b) + ab.WX), 'addendum B'
    if crop == 'winter barley' and cut == 'mid-July':
        return ac.loyo(base, w.eo_cols(k) + w.WEATHER + [f'cr_m{m:02d}' for m in ac.S1_MONTHS[k]], w.YEARS), 'first run + Sentinel-1 (C2)'
    return w.loyo(base, 's2+weather', k), 'first run'


def main():
    y = w.yields(); s2 = w.panel()
    feats = w.region_features(s2, 'crop'); dd = region_dd(s2, 'crop'); s1f = ac.s1_features(s2)
    out = {'skill': {}, 'flag': {}, 'intervals': {}, 'coefficients_full_fit': {}, 'flag_2026': {}, 'illustration_2026': {}}
    keep = {}
    for crop in w.CROPS:
        base = feats[feats.crop == crop].merge(y[y.crop == crop], on=['crop', 'region', 'year'])
        base = base[base.year.isin(w.YEARS)].merge(s1f, on=['crop', 'region', 'year'], how='left').reset_index(drop=True)
        for cut, k in CUTS:
            key = f'{crop} | {cut}'
            mf_b = ab.monthly(base, k).merge(base[['region', 'year', 'yield_t_ha']], on=['region', 'year'])
            r0, lab = current(crop, cut, k, base, mf_b)
            mf = e_features(base, k, dd).merge(base[['region', 'year', 'yield_t_ha']], on=['region', 'year'])
            cols = ab.eo_monthly(mf) + WX
            r1 = run_e(mf, cols)
            s0, s1 = w.scores(r0), w.scores(r1)
            x0, x1 = eng_err(r0, EXTREME), eng_err(r1, EXTREME)
            adopt = bool(s1['r2'] >= s0['r2'] - 0.02 and x1 < x0)
            out['skill'][key] = {'current model': lab, 'current': s0 | {'extreme_mae': x0, 'dry_mae': eng_err(r0, ab.DRY)},
                                 'E1+E2': s1 | {'extreme_mae': x1, 'dry_mae': eng_err(r1, ab.DRY)}, 'adopt E1+E2': adopt}
            r1['flag'] = r1.di > r1.thr
            fs = r1.groupby('year').flag.mean()
            ext = {int(yv): float(fs[yv]) for yv in EXTREME}
            n_ext = sum(v >= 0.5 for v in ext.values()); oth = float(r1[r1.year.isin(OTHER)].flag.mean())
            out['flag'][key] = {'share_flagged_by_year': {int(a): round(float(b), 3) for a, b in fs.items()}, 'extreme_seasons_flagged': n_ext,
                                'other_region_seasons_flagged': oth, 'adopt E3': bool(n_ext >= 2 and oth <= 0.10)}
            hit = lambda q: ((r1.obs - r1.pred).abs() <= q)
            cw, cu = hit(r1.q_w), hit(r1.q_u)
            ex = r1.year.isin(EXTREME)
            out['intervals'][key] = {'coverage_weighted': float(cw.mean()), 'coverage_unweighted': float(cu.mean()),
                                     'extreme_weighted': float(cw[ex].mean()), 'extreme_unweighted': float(cu[ex].mean()),
                                     'mean_halfwidth_weighted': float(np.mean(np.minimum(r1.q_w, 5))), 'mean_halfwidth_unweighted': float(r1.q_u.mean())}
            iv = out['intervals'][key]
            iv['adopt E4'] = bool(0.75 <= iv['coverage_weighted'] <= 0.90 and iv['extreme_weighted'] > iv['extreme_unweighted'])
            m = fit(mf, cols)
            out['coefficients_full_fit'][key] = {'alpha': m['alpha'], **{c: round(float(v), 3) for c, v in zip(cols, m['b']) if c in WX}}
            keep[key] = (mf, cols, m)
            w.log(key, 'R2 %.3f -> %.3f' % (s0['r2'], s1['r2']), 'extreme MAE %.2f -> %.2f' % (x0, x1), 'E2', adopt,
                  'E3 ext %d other %.2f' % (n_ext, oth), 'E4 cov %.2f ext %.2f vs %.2f' % (iv['coverage_weighted'], iv['extreme_weighted'], iv['extreme_unweighted']))
    # 2026: the flag (inputs only, a fair test) and the E2/E4 nowcast (illustration: Defra's provisional figures are known)
    check, preds = w.classify_2026(s2)
    sc = pd.read_csv(os.path.join(RES, 'wp1_score_2026.csv'))
    act = sc[sc.version.str.startswith('first')].drop_duplicates(['crop', 'region']).set_index(['crop', 'region']).actual
    for crop in w.CROPS:
        for cut, k in CUTS:
            key = f'{crop} | {cut}'
            mf, cols, m = keep[key]
            s = s2.loc[preds[k].index].assign(crop_pred=preds[k].values)
            t = w.region_features(s, 'crop_pred'); t = t[(t.crop == crop) & t.region.isin(mf.region.unique())].reset_index(drop=True)
            mt = e_features(t, k, region_dd(s, 'crop_pred'))
            p, B = predict(m, mt)
            res, dis = inner(mf, cols)
            flags = di(m, B) > threshold(dis)
            out['flag_2026'][key] = {'regions_flagged': int(flags.sum()), 'regions': int(len(flags)), 'share': float(flags.mean()),
                                     'flag_worked (at least half)': bool(flags.mean() >= 0.5),
                                     'by_region': dict(zip(mt.region, [bool(f) for f in flags]))}
            wt = np.abs(m['b']); dtr = wdist(m['A'], m['A'], wt); h = np.median(dtr[np.triu_indices(len(dtr), 1)])
            dte = wdist(B, m['A'], wt)
            q = np.array([wquantile(np.abs(res), np.exp(-dte[i] ** 2 / (2 * h ** 2)), LEVEL) for i in range(len(mt))])
            nc = p + mf.groupby('region').yield_t_ha.mean().reindex(mt.region).values
            a = act.reindex(pd.MultiIndex.from_arrays([[crop] * len(mt), mt.region])).values
            inside = np.abs(nc - a) <= q
            out['illustration_2026'][key] = {'nowcast_mean': float(np.mean(nc)), 'defra_provisional_mean': float(np.nanmean(a)),
                                             'mean_error': float(np.nanmean(nc - a)), 'inside_80pct': int(np.nansum(inside)), 'regions': int(len(mt)),
                                             'infinite_intervals': int(np.isinf(q).sum())}
    json.dump(out, open(os.path.join(RES, 'wp1_addendum_e.json'), 'w'), indent=1)
    report(out)


def report(out):
    f2 = lambda v: f'{v:+.2f}'
    L = ['# WP1 addendum E: degree-days, sign-constrained weather, an out-of-range flag and shift-aware intervals', '',
         'Protocol addendum E ([protocol.md](protocol.md)), written 29 October 2026, with clarifications recorded 30 October 2026 '
         'before any degree-day value was fetched. Leave-one-year-out 2017–2025. Extreme seasons: 2018, 2022, 2025. Errors are '
         'England-level (mean over regions of predicted minus Defra anomaly, t/ha).', '',
         '## E1 + E2 against the model in use', '',
         '| Crop · cutoff | model in use | R² in use | R² E | England R² in use → E | extreme-season MAE in use → E | dry-spring MAE in use → E | adopt |',
         '|---|---|---|---|---|---|---|---|']
    for k, v in out['skill'].items():
        a, b = v['current'], v['E1+E2']
        L.append(f"| {k} | {v['current model']} | {f2(a['r2'])} | {f2(b['r2'])} | {f2(a['r2_england'])} → {f2(b['r2_england'])} | "
                 f"{a['extreme_mae']:.2f} → {b['extreme_mae']:.2f} | {a['dry_mae']:.2f} → {b['dry_mae']:.2f} | {'**yes**' if v['adopt E1+E2'] else 'no'} |")
    L += ['', 'Rule: adopted if R² is at most 0.02 below the model in use and the extreme-season error is lower.', '',
          '## E3, out-of-range flag (leave-one-year-out)', '',
          '| Crop · cutoff | share of regions flagged: 2018 / 2022 / 2025 | extreme seasons flagged (≥ half of regions) | other region-seasons flagged | adopt |',
          '|---|---|---|---|---|']
    for k, v in out['flag'].items():
        s = v['share_flagged_by_year']
        L.append(f"| {k} | {s[2018]:.2f} / {s[2022]:.2f} / {s[2025]:.2f} | {v['extreme_seasons_flagged']} of 3 | {v['other_region_seasons_flagged']:.0%} | "
                 f"{'**yes**' if v['adopt E3'] else 'no'} |")
    L += ['', 'Rule: adopted if at least two of the three extreme seasons and at most one in ten other region-seasons are flagged.', '',
          '## E4, distance-weighted 80% intervals (leave-one-year-out, nested)', '',
          '| Crop · cutoff | coverage weighted | coverage unweighted | extreme seasons: weighted vs unweighted | mean half-width weighted / unweighted (t/ha) | adopt |',
          '|---|---|---|---|---|---|']
    for k, v in out['intervals'].items():
        L.append(f"| {k} | {v['coverage_weighted']:.0%} | {v['coverage_unweighted']:.0%} | {v['extreme_weighted']:.0%} vs {v['extreme_unweighted']:.0%} | "
                 f"{v['mean_halfwidth_weighted']:.2f} / {v['mean_halfwidth_unweighted']:.2f} | {'**yes**' if v['adopt E4'] else 'no'} |")
    L += ['', 'Rule: adopted if weighted coverage is 75–90% and higher than the unweighted intervals in the extreme seasons.', '',
          '## Weather coefficients in the full fit (standardised; signs constrained)', '',
          '| Crop · cutoff | penalty | ' + ' | '.join(WX) + ' |', '|---|---|' + '---|' * len(WX)]
    L += [f"| {k} | {v['alpha']} | " + ' | '.join(f"{v[c]:+.3f}" for c in WX) + ' |' for k, v in out['coefficients_full_fit'].items()]
    L += ['', '## 2026: the out-of-range flag (a fair test: inputs only)', '',
          '| Crop · cutoff | regions flagged | flag worked (≥ half) |', '|---|---|---|']
    for k, v in out['flag_2026'].items():
        L.append(f"| {k} | {v['regions_flagged']} of {v['regions']} | {'**yes**' if v['flag_worked (at least half)'] else 'no'} |")
    L += ['', '## 2026 nowcast with E2 and E4 (illustration only: Defra’s provisional figures were known when E was written)', '',
          '| Crop · cutoff | nowcast, mean of regions | Defra provisional | error | regions inside the 80% interval |', '|---|---|---|---|---|']
    for k, v in out['illustration_2026'].items():
        L.append(f"| {k} | {v['nowcast_mean']:.2f} | {v['defra_provisional_mean']:.2f} | {f2(v['mean_error'])} | {v['inside_80pct']} of {v['regions']} |")
    L += ['', 'Limits: eight regions and nine seasons per crop; degree-days at the weather-cell centre, averaged over the crop’s '
          'parcels; the confirmatory test is the 2027 harvest; Defra’s final 2026 figures (10 December 2026) will replace the '
          'provisional ones in the illustration.']
    open(os.path.join(RES, 'wp1_addendum_e.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
