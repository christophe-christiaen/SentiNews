"""WP1 protocol addendum C (written 17 October 2026, before running): supporting datasets.
  C1 MODIS long record (2001-2025, cereal-land parcel points) + weather, its own model
  C2 first-run Sentinel-2 + weather model + monthly Sentinel-1 cross-ratio (VH - VV) in spring
  C3 first-run model + share of the crop's fields under agreement + (Flood Zone 3 / deep peat share x wet winter)
Leave-one-year-out; adoption rule in the protocol. 2026 not used.

Output  wp1_regional_signal/results/wp1_addendum_c.md, wp1_addendum_c.json
"""
import glob, json, os, re
import numpy as np, pandas as pd
import wp1_nowcast as w

RES, D = w.RES, w.D
DRY = [2018, 2020, 2022, 2025]
S1_MONTHS = {9: [6, 7, 8, 9], 12: [6, 7, 8, 9, 10, 11]}       # m06 = March ... m11 = August


def loyo(df, cols, years):
    rows = []
    for yv in years:
        tr, te = df[(df.year != yv) & df.year.isin(years)], df[df.year == yv]
        if te.empty:
            continue
        a, b = w.anomalies(tr, te, cols)
        ytr = (tr.yield_t_ha - tr.groupby('region').yield_t_ha.transform('mean')).values
        sc, m, _ = w.fit_ridge(a.values, ytr, tr.year.values)
        obs = te.yield_t_ha.values - tr.groupby('region').yield_t_ha.mean().reindex(te.region).values
        rows.append(pd.DataFrame({'region': te.region.values, 'year': yv, 'obs': obs, 'pred': m.predict(sc.transform(b.values))}))
    return pd.concat(rows, ignore_index=True)


def score(r):
    s = w.scores(r)
    e = r.groupby('year')[['obs', 'pred']].mean(); err = e.pred - e.obs
    s['mae_dry'] = float(err.reindex(DRY).abs().mean()); s['mean_error_dry'] = float(err.reindex(DRY).mean())
    return s


def region_weather(par):
    sh = pd.read_parquet(os.path.join(D, 'weather', 'cell_year_shocks.parquet'))[['cell_id', 'year'] + w.WEATHER + ['wet_shock']]
    cell = pd.read_parquet(os.path.join(D, 'weather', 'parcel_era5_cell.parquet'))[['parcref', 'cell_id_data']]
    x = par[['parcref', 'region']].merge(cell, on='parcref')
    cr = x.groupby(['region', 'cell_id_data']).size().rename('n').reset_index()
    m = cr.merge(sh.rename(columns={'cell_id': 'cell_id_data'}), on='cell_id_data')
    cols = w.WEATHER + ['wet_shock']
    m[cols] = m[cols].astype(float).mul(m.n, axis=0)
    g = m.groupby(['region', 'year'])
    return (g[cols].sum().div(g.n.sum(), axis=0)).reset_index()


def c1(y, regions):
    files = sorted(glob.glob(os.path.join(D, 'modis_parcels', 'modis_*.csv')))
    m = pd.concat([pd.read_csv(f) for f in files], ignore_index=True).drop_duplicates('parcref').merge(regions, on='parcref')
    rows = []
    for yv in range(2001, 2026):
        g = m.groupby('region')[[f'july_{yv}', f'peak_{yv}']].median()
        g.columns = ['modis_july', 'modis_peak']; g['year'] = yv; rows.append(g.reset_index())
    f = pd.concat(rows).merge(region_weather(regions), on=['region', 'year'], how='left')
    out = {}
    for crop in w.CROPS:
        df = f.merge(y[y.crop == crop], on=['region', 'year'])
        yrs = sorted(df.year.unique())
        r = loyo(df, ['modis_july', 'modis_peak'] + w.WEATHER, yrs)
        out[crop] = {'years': f'{min(yrs)}–{max(yrs)}', 'all years': score(r), '2017–2025 only': score(r[r.year >= 2017])}
        w.log('C1', crop, round(out[crop]['all years']['r2'], 3), round(out[crop]['2017–2025 only']['r2'], 3))
    return out


def s1_features(s2):
    need = sorted({k for v in S1_MONTHS.values() for k in v})
    cols = ['parcref'] + [f'{p}_{d}_m{k:02d}' for k in need for d in ('asc', 'desc') for p in ('vv', 'vh')]
    parts = []
    for f in sorted(glob.glob(os.path.join(D, 's1', 'gee_orbit', 's1o_*.csv'))):
        yv = int(re.search(r'_(\d{4})\.csv$', f).group(1))
        if yv > 2025:
            continue
        x = pd.read_csv(f, usecols=cols); x['year'] = yv
        for k in need:
            x[f'cr_m{k:02d}'] = pd.concat([x[f'vh_{d}_m{k:02d}'] - x[f'vv_{d}_m{k:02d}'] for d in ('asc', 'desc')], axis=1).mean(axis=1)
        parts.append(x[['parcref', 'year'] + [f'cr_m{k:02d}' for k in need]])
    s1 = pd.concat(parts, ignore_index=True)
    x = s2[['parcref', 'year', 'region', 'crop']].merge(s1, on=['parcref', 'year'])
    return x[x.crop.isin(w.CROPS)].groupby(['crop', 'region', 'year'])[[c for c in s1.columns if c.startswith('cr_')]].median().reset_index()


def c3_features(s2):
    pan = pd.read_parquet(os.path.join(D, 'parcels', 'parcel_panel.parquet'), columns=['parcref', 'parcel_group', 'entry_year'])
    risk = pd.read_parquet(os.path.join(D, 'parcels', 'parcel_risk.parquet'))
    risk['fp'] = ((risk.flood_zone.fillna(0).astype(int) == 3) | risk.peat_class.fillna('').str.lower().str.contains('deep')).astype(float)
    x = s2[['parcref', 'year', 'region', 'crop']].merge(pan, on='parcref').merge(risk[['parcref', 'fp']], on='parcref')
    x = x[x.crop.isin(w.CROPS)]
    x['agr'] = ((x.parcel_group == 'agreement') & (x.entry_year.astype(float) <= x.year)).astype(float)
    g = x.groupby(['crop', 'region', 'year'])[['agr', 'fp']].mean().reset_index()
    wx = region_weather(x[['parcref', 'region']].drop_duplicates('parcref'))
    g = g.merge(wx[['region', 'year', 'wet_shock']], on=['region', 'year'], how='left')
    g['fp_wet'] = g.fp * g.wet_shock
    return g[['crop', 'region', 'year', 'agr', 'fp_wet']]


def main():
    y = w.yields(); s2 = w.panel()
    regions = s2[['parcref', 'region']].drop_duplicates('parcref')
    feats = w.region_features(s2, 'crop')
    out = {'C1_modis_long': c1(y, regions), 'C2_C3': {}}
    s1f, c3f = s1_features(s2), c3_features(s2)
    for crop in w.CROPS:
        base = feats[feats.crop == crop].merge(y[y.crop == crop], on=['crop', 'region', 'year'])
        base = base[base.year.isin(w.YEARS)].merge(s1f, on=['crop', 'region', 'year'], how='left').merge(c3f, on=['crop', 'region', 'year'], how='left')
        for cut, k in [('mid-July', 9), ('end of August', 12)]:
            first = w.eo_cols(k) + w.WEATHER
            s0 = score(loyo(base, first, w.YEARS))
            res = {'first run': s0}
            for lab, extra in [('C2 + Sentinel-1', [f'cr_m{m:02d}' for m in S1_MONTHS[k]]), ('C3 + schemes, flood/peat', ['agr', 'fp_wet'])]:
                s = score(loyo(base, first + extra, w.YEARS))
                s['adopt'] = bool(s['r2'] >= s0['r2'] + 0.02 and s['mae_dry'] <= s0['mae_dry'])
                res[lab] = s
            out['C2_C3'][f'{crop} | {cut}'] = res
            w.log(crop, cut, {kk: round(v['r2'], 3) for kk, v in res.items()})
    json.dump(out, open(os.path.join(RES, 'wp1_addendum_c.json'), 'w'), indent=1, default=float)
    L = ['# WP1 addendum C: supporting datasets', '',
         'Protocol addendum C ([protocol.md](protocol.md)), written 17 October 2026 before running. Leave-one-year-out; '
         'R² of the yield anomaly; dry-spring years 2018, 2020, 2022, 2025.', '',
         '## C1. MODIS long record (its own model; cereal-land parcel points, 2001–2025)', '',
         '| Crop | years | R², all years | England R², all years | R², 2017–2025 only | dry-year MAE (t/ha) |', '|---|---|---|---|---|---|']
    for c, v in out['C1_modis_long'].items():
        L.append(f"| {c} | {v['years']} | {v['all years']['r2']:+.2f} | {v['all years']['r2_england']:+.2f} | {v['2017–2025 only']['r2']:+.2f} | {v['all years']['mae_dry']:.2f} |")
    L += ['', 'Sentinel-2 + weather, first run (2017–2025): wheat 0.64, winter barley 0.52, spring barley 0.51 (mid-July).', '',
          '## C2 and C3 (added to the first-run Sentinel-2 + weather model, 2017–2025)', '',
          '| Crop, cutoff | model | R² | England R² | dry-year MAE | adopt |', '|---|---|---|---|---|---|']
    for k, res in out['C2_C3'].items():
        for lab, s in res.items():
            L.append(f"| {k} | {lab} | {s['r2']:+.2f} | {s['r2_england']:+.2f} | {s['mae_dry']:.2f} | {('yes' if s.get('adopt') else 'no') if lab != 'first run' else '–'} |")
    open(os.path.join(RES, 'wp1_addendum_c.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
