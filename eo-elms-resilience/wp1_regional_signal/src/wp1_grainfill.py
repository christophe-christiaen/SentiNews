"""WP1 addendum A: grain-fill features (wp1_regional_signal/results/protocol.md, written before they were computed).

Adds June (mid-July cutoff) or June-July (end of August) weather anomalies against each cell's 1991-2020 normal, the
April-June water balance, and Sentinel-2 canopy decline after the peak; scores them with the same leave-one-year-out
rules as wp1_nowcast.py and reports the error in dry-spring years. Re-issues the 2026 nowcast only where the
leave-one-year-out R2 improves.

Output  wp1_regional_signal/results/wp1_grainfill.md, wp1_grainfill.json, wp1_nowcast_2026_grainfill.csv
"""
import json, os, time
import numpy as np, pandas as pd
import wp1_nowcast as w

GF9 = ['t_jun', 'wb_jun', 'sm_jun', 'wb_amj', 'drop_ndvi_9', 'drop_ndmi_9']
GF12 = GF9 + ['t_jul', 'wb_jul', 'sm_jul', 'hot_days_28', 'hot_days_30', 'drop_ndvi_late', 'drop_ndmi_late', 'senesc_k']
log = w.log


def cell_weather():
    m = pd.read_parquet(os.path.join(w.D, 'weather', 'era5land_monthly.parquet'))
    m['wb'] = m.precip_mm - m.pet_mm
    norm = m[m.year.between(1991, 2020)].groupby(['cell_id', 'month'])
    mu, sd = norm[['t2m_c', 'wb', 'swvl2']].mean(), norm[['t2m_c', 'wb', 'swvl2']].std()
    m = m.join(mu, on=['cell_id', 'month'], rsuffix='_mu').join(sd, on=['cell_id', 'month'], rsuffix='_sd')
    out = {}
    for mon, tag in [(6, 'jun'), (7, 'jul')]:
        x = m[m.month == mon].set_index(['cell_id', 'year'])
        out[f't_{tag}'] = x.t2m_c - x.t2m_c_mu
        out[f'wb_{tag}'] = x.wb - x.wb_mu
        out[f'sm_{tag}'] = (x.swvl2 - x.swvl2_mu) / x.swvl2_sd
    amj = m[m.month.between(4, 6)].groupby(['cell_id', 'year']).agg(wb=('wb', 'sum'), mu=('wb_mu', 'sum'))
    out['wb_amj'] = amj.wb - amj.mu
    h = pd.read_parquet(os.path.join(w.D, 'weather', 'era5land_heatdays.parquet')).set_index(['cell_id', 'year'])
    out['hot_days_28'], out['hot_days_30'] = h.hot_days_28, h.hot_days_30
    return pd.DataFrame(out).reset_index().rename(columns={'cell_id': 'cell_id_data'})


def parcel_gf(s2):
    nd = lambda i, ks: s2[[f'{i}_p{k:02d}' for k in ks]]
    peak_v, peak_m = nd('ndvi', range(4, 10)).max(axis=1), nd('ndmi', range(4, 10)).max(axis=1)
    return pd.DataFrame({'drop_ndvi_9': peak_v - s2.ndvi_p09, 'drop_ndmi_9': peak_m - s2.ndmi_p09,
                         'drop_ndvi_late': peak_v - nd('ndvi', (10, 11)).mean(axis=1),
                         'drop_ndmi_late': peak_m - nd('ndmi', (10, 11)).mean(axis=1)}, index=s2.index)


def gf_region(s2, crop_col, cw):
    d = s2[s2[crop_col].isin(w.CROPS)]
    d = d.join(parcel_gf(d)).merge(cw, on=['cell_id_data', 'year'], how='left')
    g = d.groupby([crop_col, 'region', 'year'])
    eo = ['drop_ndvi_9', 'drop_ndmi_9', 'drop_ndvi_late', 'drop_ndmi_late', 'senesc_k']
    wx = [c for c in GF12 if c not in eo and c not in w.WEATHER]     # hot_days_28 already comes with the base features
    f = g[eo].median().join(g[wx].mean()).join(g.dry_shock.mean().rename('dry_share'))
    f.index = f.index.set_names(['crop', 'region', 'year'])
    return f.reset_index()


_base_predict = w.predict


def predict(model, train, test, kmax):
    if model.startswith('s2+weather+gf'):
        cols = w.eo_cols(kmax) + w.WEATHER + (GF9 if kmax <= 9 else GF12)
        ytr = (train.yield_t_ha - train.groupby('region').yield_t_ha.transform('mean')).values
        a, b = w.anomalies(train, test, cols)
        sc, m, _ = w.fit_ridge(a.values, ytr, train.year.values)
        return m.predict(sc.transform(b.values))
    return _base_predict(model, train, test, kmax)


w.predict = predict          # loyo() and jackknife_plus() in wp1_nowcast look this name up at call time


def main():
    y = w.yields()
    s2 = w.panel()
    extra = pd.read_parquet(os.path.join(w.D, 's2', 's2_parcel_year.parquet'), columns=['parcref', 'year', 'senesc_k', 'dry_shock'])
    s2 = s2.merge(extra, on=['parcref', 'year'], how='left')
    cw = cell_weather()
    base = w.region_features(s2, 'crop')
    feats = base.merge(gf_region(s2, 'crop', cw), on=['crop', 'region', 'year'], how='left')
    out = {'skill': {}, 'dry_years': {}, 'by_year_error_england': {}}
    resid = {}
    for crop in w.CROPS:
        df = feats[feats.crop == crop].merge(y[y.crop == crop], on=['crop', 'region', 'year'])
        df = df[df.year.isin(w.YEARS)].reset_index(drop=True)
        dry = sorted(int(v) for v, s in (df.groupby('year').dry_share.mean() >= 0.5).items() if s) if crop == 'wheat' else out['dry_years']['wheat']
        out['dry_years'][crop] = dry
        out['skill'][crop] = {}
        for cut, k in [('mid-July', 9), ('end of August', 12)]:
            for model in ('s2+weather', 's2+weather+gf'):
                r = w.loyo(df, model, k)
                sc = w.scores(r)
                e = r.groupby('year')[['obs', 'pred']].mean()
                err = (e.pred - e.obs)
                sc['mean_error_dry_years'] = float(err.reindex(dry).mean())
                sc['mean_abs_error_dry_years'] = float(err.reindex(dry).abs().mean())
                sc['mean_abs_error_other_years'] = float(err.drop(dry, errors='ignore').abs().mean())
                out['skill'][crop][f'{model} | {cut}'] = sc
                out['by_year_error_england'][f'{crop} | {model} | {cut}'] = err.round(3).to_dict()
                resid[(crop, model, cut)] = r
                log(crop, model, cut, 'R2 %.3f' % sc['r2'], 'dry-year error %+.2f' % sc['mean_error_dry_years'])
    # 2026: re-issue only where R2 improves
    check, preds = w.classify_2026(s2)
    rows = []
    for crop in w.CROPS:
        df = feats[feats.crop == crop].merge(y[y.crop == crop], on=['crop', 'region', 'year'])
        df = df[df.year.isin(w.YEARS)].reset_index(drop=True)
        for cut, k in [('mid-July', 9), ('end of August', 12)]:
            s_new, s_old = out['skill'][crop][f's2+weather+gf | {cut}']['r2'], out['skill'][crop][f's2+weather | {cut}']['r2']
            if s_new <= s_old:
                continue
            s = s2.loc[preds[k].index].assign(crop_pred=preds[k].values)
            t = w.region_features(s, 'crop_pred').merge(gf_region(s, 'crop_pred', cw), on=['crop', 'region', 'year'], how='left')
            t = t[(t.crop == crop) & t.region.isin(df.region.unique())].reset_index(drop=True)
            mid, lo80, hi80 = w.jackknife_plus(df, t, 's2+weather+gf', k, 0.9)
            avg = df.groupby('region').yield_t_ha.mean().reindex(t.region).values
            for j in range(len(t)):
                rows.append(dict(crop=crop, cutoff=cut, region=t.region[j], nowcast_t_ha=round(mid[j], 2), lo80=round(lo80[j], 2),
                                 hi80=round(hi80[j], 2), mean_2017_2025=round(avg[j], 2)))
    nc = pd.DataFrame(rows)
    nc.to_csv(os.path.join(w.RES, 'wp1_nowcast_2026_grainfill.csv'), index=False)
    out['written'] = time.strftime('%Y-%m-%d %H:%M')
    json.dump(out, open(os.path.join(w.RES, 'wp1_grainfill.json'), 'w'), indent=1)
    report(out, nc)


def report(o, nc):
    L = ['# WP1 addendum A: grain-fill features', '',
         'Protocol addendum A ([protocol.md](protocol.md)), written before the features were computed. Same '
         'leave-one-year-out scoring as [wp1_results.md](wp1_results.md). Error = predicted minus Defra, England mean '
         'of the regional anomalies (t/ha); positive = over-predicted.', '',
         f"Dry-spring years (at least half of the wheat region-years in a dry shock): {', '.join(map(str, o['dry_years']['wheat']))}.", '']
    for crop, s in o['skill'].items():
        L += [f'## {crop.capitalize()}', '', '| Model | cutoff | R² | England R² | mean error, dry years | mean abs. error, dry years | mean abs. error, other years |',
              '|---|---|---|---|---|---|---|']
        for k, v in s.items():
            m, c = k.split(' | ')
            L.append(f"| {m} | {c} | {v['r2']:+.2f} | {v['r2_england']:+.2f} | {v['mean_error_dry_years']:+.2f} | "
                     f"{v['mean_abs_error_dry_years']:.2f} | {v['mean_abs_error_other_years']:.2f} |")
        L.append('')
    L += ['## England error by year, wheat (predicted minus Defra, t/ha)', '',
          '| Year | first run, mid-July | grain fill, mid-July | first run, end of August | grain fill, end of August |', '|---|---|---|---|---|']
    e = o['by_year_error_england']
    for yv in w.YEARS:
        g = lambda k: e[k].get(yv, e[k].get(str(yv)))
        L.append(f"| {yv} | {g('wheat | s2+weather | mid-July'):+.2f} | {g('wheat | s2+weather+gf | mid-July'):+.2f} | "
                 f"{g('wheat | s2+weather | end of August'):+.2f} | {g('wheat | s2+weather+gf | end of August'):+.2f} |")
    L += ['', f"## 2026 nowcast re-issued where R² improved (written {o['written']})", '']
    if nc.empty:
        L.append('No crop and cutoff improved; the first nowcast (commit 8427362) stands.')
    else:
        L += ['| Crop | cutoff | region | nowcast (t/ha) | 80% interval | 2017–2025 mean |', '|---|---|---|---|---|---|'] + \
             [f'| {r.crop} | {r.cutoff} | {r.region} | {r.nowcast_t_ha:.2f} | {r.lo80:.2f}–{r.hi80:.2f} | {r.mean_2017_2025:.2f} |' for r in nc.itertuples()]
        L += ['', 'Means over regions: ' + '; '.join(f"{c} {cu}: {g.nowcast_t_ha.mean():.2f} (mean {g.mean_2017_2025.mean():.2f})"
                                                    for (c, cu), g in nc.groupby(['crop', 'cutoff']))]
    open(os.path.join(w.RES, 'wp1_grainfill.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
