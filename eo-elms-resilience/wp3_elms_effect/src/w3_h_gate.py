"""W3-H Steps 1 and 2: field harvest index and its gate against Defra, following w3_h_harvest_protocol.md.

The WP1 first-run model (ridge, Sentinel-2 + weather, end of August) is fitted on region x season medians without the
held-out season, then applied to each field's own indices and its cell's weather. The index is aggregated to region x
season by median and scored against Defra's regional anomalies. Step 3 is not run here.

Input   as wp1_nowcast.panel(); data/raw/cops.ods
Output  wp3_elms_effect/results/w3_h_harvest.md, w3_h_harvest.json (aggregates only)
        wp3_elms_effect/data/w3_h_field_index.parquet (per field and season, gitignored)
"""
import json, os, sys, time
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'wp1_regional_signal', 'src'))
from wp1_nowcast import CROPS, D, WEATHER, YEARS, anomalies, eo_cols, fit_ridge, panel, region_features, yields

W3 = os.path.join(ROOT, 'wp3_elms_effect')
KMAX = 12  # end of August
DRY = (2018, 2020, 2022, 2025)
R2_MIN, RATIO_MAX = 0.40, 1.5
log = lambda *a: print(time.strftime('%H:%M:%S'), *a, flush=True)


def r2(o, p):
    return float(1 - ((o - p) ** 2).sum() / ((o - o.mean()) ** 2).sum())


def field_frame(s2):
    shocks = pd.read_parquet(os.path.join(D, 'weather', 'cell_year_shocks.parquet'))[['cell_id', 'year'] + WEATHER]
    d = s2[s2.crop.isin(CROPS) & s2.region.notna()].merge(shocks.rename(columns={'cell_id': 'cell_id_data'}), on=['cell_id_data', 'year'], how='left')
    return d


def run_crop(crop, feats, fields):
    """Leave-one-year-out: returns field index, and region x season rows with Defra's anomaly."""
    cols = eo_cols(KMAX) + WEATHER
    df, fld = feats[feats.crop == crop], fields[fields.crop == crop]
    out, rows, alphas = [], [], {}
    for y in YEARS:
        tr, te, f = df[df.year != y], df[df.year == y], fld[fld.year == y]
        if te.empty:
            continue
        mu = tr.groupby('region').yield_t_ha.mean()
        ytr = (tr.yield_t_ha - tr.groupby('region').yield_t_ha.transform('mean')).values
        a, b = anomalies(tr, te, cols)
        sc, m, alphas[y] = fit_ridge(a.values, ytr, tr.year.values)
        _, af = anomalies(tr, f, cols)
        idx = m.predict(sc.transform(af.values))
        out.append(pd.DataFrame({'parcref': f.parcref.values, 'year': y, 'crop': crop, 'region': f.region.values, 'index_t_ha': idx,
                                 'missing_share': f[eo_cols(KMAX)].isna().mean(axis=1).values}))
        med = pd.Series(idx, index=f.region.values).groupby(level=0)
        rows.append(pd.DataFrame({'region': te.region.values, 'year': y, 'obs': te.yield_t_ha.values - mu.reindex(te.region).values,
                                  'pred': med.median().reindex(te.region).values, 'pred_wp1': m.predict(sc.transform(b.values)),
                                  'field_sd': med.std().reindex(te.region).values, 'fields': med.size().reindex(te.region).values}))
    return pd.concat(out, ignore_index=True), pd.concat(rows, ignore_index=True), alphas


def score(r):
    e = (r.pred - r.obs).abs()
    dry = r.year.isin(DRY)
    mae_dry, mae_oth = float(e[dry].mean()), float(e[~dry].mean())
    eng = r.groupby('year')[['obs', 'pred']].mean()
    s = dict(r2=r2(r.obs, r.pred), r=float(np.corrcoef(r.obs, r.pred)[0, 1]), mae_dry=mae_dry, mae_other=mae_oth, ratio=mae_dry / mae_oth,
             r2_wp1_reproduced=r2(r.obs, r.pred_wp1), r2_england=r2(eng.obs, eng.pred), bias_dry=float((r.pred - r.obs)[dry].mean()),
             bias_other=float((r.pred - r.obs)[~dry].mean()), n=int(len(r)))
    s['pass_r2'], s['pass_dry'] = bool(s['r2'] >= R2_MIN), bool(s['ratio'] <= RATIO_MAX)
    s['pass'] = s['pass_r2'] and s['pass_dry']
    return s


def main():
    y = yields()
    s2 = panel()
    log('parcel-seasons', len(s2))
    feats = region_features(s2, 'crop').merge(y, on=['crop', 'region', 'year'])
    fields = field_frame(s2)
    del s2
    log('field-seasons', fields.crop.value_counts().to_dict())
    res, seasons, idx = {}, {}, []
    for crop in CROPS:
        f, r, alphas = run_crop(crop, feats, fields)
        idx.append(f)
        res[crop] = score(r)
        res[crop].update(field_seasons=int(len(f)), missing_share=float(f.missing_share.mean()), median_field_sd=float(r.field_sd.median()),
                         alphas={str(k): v for k, v in alphas.items()})
        seasons[crop] = r.groupby('year')[['obs', 'pred']].mean().round(3).reset_index().to_dict('records')
        log(crop, {k: round(v, 3) if isinstance(v, float) else v for k, v in res[crop].items() if k != 'alphas'})
    os.makedirs(os.path.join(W3, 'data'), exist_ok=True)
    pd.concat(idx, ignore_index=True).to_parquet(os.path.join(W3, 'data', 'w3_h_field_index.parquet'), index=False)
    with open(os.path.join(W3, 'results', 'w3_h_harvest.json'), 'w') as fh:
        json.dump(dict(gate=res, seasons=seasons, dry_seasons=list(DRY), r2_min=R2_MIN, ratio_max=RATIO_MAX), fh, indent=1)
    L = ['# W3-H results: field harvest index and its gate against Defra', '',
         'Run of [w3_h_harvest_protocol.md](w3_h_harvest_protocol.md), Steps 1 and 2. Leave-one-year-out, 2017–2025, 8 English Defra regions. '
         f'A crop passes if R² is at least {R2_MIN} and dry-spring error is no more than {RATIO_MAX} times that of other seasons. Aggregates only.', '',
         '## Gate', '', '| Crop | Field-seasons | R² | r | MAE dry (t/ha) | MAE other (t/ha) | Ratio | Gate |', '|---|---:|---:|---:|---:|---:|---:|---|']
    for c, s in res.items():
        L.append(f"| {c} | {s['field_seasons']:,} | {s['r2']:+.2f} | {s['r']:+.2f} | {s['mae_dry']:.2f} | {s['mae_other']:.2f} | {s['ratio']:.2f} | {'pass' if s['pass'] else 'FAIL'} |")
    L += ['', '## Context, not part of the gate', '', '| Crop | R², WP1 region-median prediction | R², England mean | Bias dry (t/ha) | Bias other (t/ha) | Half-months missing per field | Field SD within region-season (t/ha) |', '|---|---:|---:|---:|---:|---:|---:|']
    for c, s in res.items():
        L.append(f"| {c} | {s['r2_wp1_reproduced']:+.2f} | {s['r2_england']:+.2f} | {s['bias_dry']:+.2f} | {s['bias_other']:+.2f} | {s['missing_share']:.0%} | {s['median_field_sd']:.2f} |")
    L += ['', '## England mean by season (t/ha)', '', '| Season | ' + ' | '.join(f'{c}: Defra, index' for c in res) + ' |', '|---|' + '---:|' * len(res)]
    for k, yr in enumerate(YEARS):
        L.append(f"| {yr}{' (dry)' if yr in DRY else ''} | " + ' | '.join(f"{seasons[c][k]['obs']:+.2f}, {seasons[c][k]['pred']:+.2f}" for c in res) + ' |')
    L += ['', '**Stated limit:** Defra\'s regional figures cannot show whether the index ranks fields correctly within a region.']
    with open(os.path.join(W3, 'results', 'w3_h_harvest.md'), 'w') as fh:
        fh.write('\n'.join(L) + '\n')
    log('done')


if __name__ == '__main__':
    main()
