"""Post hoc diagnosis of the 2026 nowcast miss (scored in results/wp1_score_2026.md). Nothing here changes the
nowcast; any fix it suggests goes into the protocol as a new addendum before it is tested.

Checks (wheat, mid-July model = Sentinel-2 + weather ridge, the model used for the 2026 nowcast):
  1 Data quality: clear observations per field and fields per region, 2026 vs 2017-2025
  2 Crop mask: 2026 fields from the classifier vs CROME-mask years; classifier share by region vs Defra wheat area change
  3 Extrapolation: 2026 features against the 2017-2025 range, by region (how many SD outside)
  4 Drivers: ridge contributions (coefficient x standardised anomaly) by feature group for 2026, and for 2025 held out
  5 Dry years: spring (March-May) and early-summer (June-July) water balance and heat, England-mean error by season

Output  wp1_regional_signal/results/wp1_diagnose_2026.md
"""
import os
import numpy as np, pandas as pd
import wp1_nowcast as w

RES = w.RES


def groups(cols):
    g = {}
    for c in cols:
        if c in w.WEATHER:
            g[c] = 'weather: ' + c
        else:
            i, k = c.split('_p'); k = int(k)
            phase = 'Mar–Apr (k1–4)' if k <= 4 else ('May–Jun (k5–8)' if k <= 8 else 'early Jul (k9)')
            g[c] = f'{i.upper()} {phase}'
    return g


def main():
    y = w.yields()
    s2 = w.panel()
    extra = pd.read_parquet(os.path.join(w.D, 's2', 's2_parcel_year.parquet'), columns=['parcref', 'year', 'clear_looks'])
    s2 = s2.merge(extra, on=['parcref', 'year'], how='left')
    check, preds = w.classify_2026(s2)
    feats = w.region_features(s2, 'crop')
    s = s2.loc[preds[9].index].assign(crop_pred=preds[9].values)
    f26 = w.region_features(s, 'crop_pred')
    L = ['# Diagnosing the 2026 nowcast miss (post hoc; the nowcast is unchanged)', '']

    # 1 data quality
    q = s2.groupby('year').clear_looks.median()
    L += ['## 1. Data quality', '', 'Median clear Sentinel-2 observations per field, March–August: ' +
          ', '.join(f'{yr}: {v:.0f}' for yr, v in q.items()) + '.', '']

    # 2 mask
    wheat = feats[feats.crop == 'wheat'].pivot(index='region', columns='year', values='parcels')
    w26 = f26[f26.crop == 'wheat'].set_index('region').parcels
    m = pd.DataFrame({'CROME wheat fields 2025': wheat[2025], 'classifier wheat fields 2026': w26})
    m['change'] = m['classifier wheat fields 2026'] / m['CROME wheat fields 2025'] - 1
    L += ['## 2. Crop mask (wheat fields in the panel)', '', m.round(3).to_markdown(), '',
          'Defra (June survey): wheat area in England −1.8% in 2026. Classifier check on 2025: wheat precision '
          f"{check[9]['wheat']['precision']:.2f}, recall {check[9]['wheat']['recall']:.2f}.", '']

    # 3 extrapolation + 4 drivers
    df = feats[feats.crop == 'wheat'].merge(y[y.crop == 'wheat'], on=['crop', 'region', 'year'])
    df = df[df.year.isin(w.YEARS)].reset_index(drop=True)
    t26 = f26[(f26.crop == 'wheat') & f26.region.isin(df.region.unique())].reset_index(drop=True)
    cols = w.eo_cols(9) + w.WEATHER
    a, b = w.anomalies(df, t26, cols)
    sd = a.std()
    z = (b / sd.replace(0, np.nan)).set_index(t26.region)
    ext = pd.DataFrame({'features beyond ±2 SD of 2017–2025': (z.abs() > 2).sum(axis=1),
                        'largest |z|': z.abs().max(axis=1).round(1), 'feature': z.abs().idxmax(axis=1)})
    L += ['## 3. Was 2026 outside the training range? (wheat, anomalies vs 2017–2025)', '', ext.to_markdown(), '']

    ytr = (df.yield_t_ha - df.groupby('region').yield_t_ha.transform('mean')).values
    sc, mdl, alpha = w.fit_ridge(a.values, ytr, df.year.values)
    contrib = pd.DataFrame(sc.transform(b.values) * mdl.coef_, columns=cols, index=t26.region)
    gmap = groups(cols)
    c26 = contrib.T.groupby(gmap).sum().T
    act = pd.read_csv(os.path.join(RES, 'wp1_score_2026.csv'))
    act = act[(act.crop == 'wheat') & (act.cutoff == 'mid-July') & (act.version.str.startswith('first'))].set_index('region')
    top = c26.mean().sort_values(key=abs, ascending=False)
    L += ['## 4. What pushed the 2026 wheat prediction (ridge contributions, t/ha, mean over regions)', '',
          f'Ridge penalty {alpha}. Positive = pushed the prediction above the region\'s 2017–2025 mean.', '',
          '| Feature group | contribution |', '|---|---|'] + [f'| {k} | {v:+.2f} |' for k, v in top.head(10).items()] + \
         ['', f'Sum of contributions (predicted anomaly), mean over regions: {contrib.sum(axis=1).mean():+.2f} t/ha; '
          f'actual anomaly: {(act.actual - act.mean_2017_2025).mean():+.2f} t/ha.', '']
    # same for 2025, held out
    tr, te = df[df.year != 2025], df[df.year == 2025].reset_index(drop=True)
    a5, b5 = w.anomalies(tr, te, cols)
    ytr5 = (tr.yield_t_ha - tr.groupby('region').yield_t_ha.transform('mean')).values
    sc5, m5, _ = w.fit_ridge(a5.values, ytr5, tr.year.values)
    c25 = pd.DataFrame(sc5.transform(b5.values) * m5.coef_, columns=cols, index=te.region).T.groupby(gmap).sum().T
    both = pd.DataFrame({'2025 (held out)': c25.mean(), '2026': c26.mean()})
    both = both.loc[both.abs().max(axis=1).sort_values(ascending=False).index[:8]]
    L += ['Same, 2025 (model trained without 2025) next to 2026:', '', both.round(2).to_markdown(), '']

    # 5 dry years
    mo = pd.read_parquet(os.path.join(w.D, 'weather', 'era5land_monthly.parquet'))
    cells = s2[s2.crop == 'wheat'].cell_id_data.unique()
    mo = mo[mo.cell_id.isin(cells)]
    mo['wb'] = mo.precip_mm - mo.pet_mm
    norm = mo[mo.year.between(1991, 2020)].groupby('month')[['wb', 't2m_c']].mean()
    yr = mo[mo.year.between(2017, 2026)]
    def season(months, col):
        x = yr[yr.month.isin(months)].groupby('year')[col].mean() - norm.loc[months, col].mean()
        return x * (len(months) if col == 'wb' else 1)
    hd = pd.read_parquet(os.path.join(w.D, 'weather', 'era5land_heatdays.parquet'))
    hd = hd[hd.cell_id.isin(cells)].groupby('year').hot_days_28.mean()
    import json
    err = json.load(open(os.path.join(RES, 'wp1_grainfill.json')))['by_year_error_england']['wheat | s2+weather | mid-July']
    err = {int(k): v for k, v in err.items()}
    err[2026] = float((act.nowcast_t_ha - act.actual).mean())
    dy = pd.DataFrame({'Mar–May water balance vs normal (mm)': season([3, 4, 5], 'wb'),
                       'Jun–Jul water balance vs normal (mm)': season([6, 7], 'wb'),
                       'Jun–Jul temperature vs normal (°C)': season([6, 7], 't2m_c'),
                       'days ≥ 28 °C (Jun–Aug)': hd.reindex(range(2017, 2027)),
                       'England error, wheat (t/ha)': pd.Series(err)}).round(2)
    L += ['## 5. Dry years compared (wheat areas; error = predicted minus Defra; 2017–2025 held out, 2026 the nowcast)', '',
          dy.to_markdown(), '']
    open(os.path.join(RES, 'wp1_diagnose_2026.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
