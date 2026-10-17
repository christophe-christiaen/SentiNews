"""WP2 W3 (paper/outline.md, specified 17 October 2026 before running): land-use change from AlphaEarth embeddings.

shift = distance between each field's mean embedding 2017-2019 and 2023-2025; changed = top 5% nationally.
(a) validation against CROME (left cereals); (b) does the lasting Sentinel-2 offset grow with the shift?
(c) pooled legacy test and season-shuffling placebo with changed fields excluded.

Output  wp2_resilience/results/wp2_landuse_change.md, .json
"""
import glob, json, os
import numpy as np, pandas as pd
import parcel_resilience as pr
import within_field_check as wf

RES = os.path.join(pr.ROOT, 'wp2_resilience', 'results')
BANDS = [f'A{i:02d}' for i in range(64)]
RNG = np.random.default_rng(3)


def mean_embedding(years):
    acc = None
    for y in years:
        d = pd.concat([pd.read_parquet(f) for f in sorted(glob.glob(os.path.join(pr.D, 'embeddings', 'parcels', f'aef_*_{y}.parquet')))],
                      ignore_index=True).drop_duplicates('parcref').set_index('parcref')[BANDS]
        acc = d if acc is None else acc.add(d, fill_value=np.nan)
    return acc / len(years)


def legacy(p):
    a = p.dropna(subset=['S', 'S_l1', 'cell_id_data'])
    w = pr.within(a, ['S', 'S_l1'], 'cy')
    return wf.ols(w.S, w[['S_l1']], a.cell_id_data)


def main():
    e1, e2 = mean_embedding([2017, 2018, 2019]), mean_embedding([2023, 2024, 2025])
    common = e1.index.intersection(e2.index)
    shift = pd.Series(np.linalg.norm(e2.loc[common].values - e1.loc[common].values, axis=1), index=common, name='shift').dropna()
    thr = shift.quantile(0.95)
    pan = pd.read_parquet(os.path.join(pr.D, 'parcels', 'parcel_panel.parquet'),
                          columns=['parcref'] + [f'cereal_{y}' for y in (2017, 2018, 2019, 2023, 2024, 2025)])
    pan = pan.set_index('parcref').reindex(shift.index)
    early = pan[[f'cereal_{y}' for y in (2017, 2018, 2019)]].fillna(False).astype(int).sum(axis=1)
    late = pan[[f'cereal_{y}' for y in (2023, 2024, 2025)]].fillna(False).astype(int).sum(axis=1)
    left = (early >= 2) & (late <= 1)
    changed = shift >= thr
    out = {'fields': int(len(shift)), 'threshold': float(thr), 'changed': int(changed.sum()),
           'left_cereals_rate_changed': float(left[changed].mean()), 'left_cereals_rate_other': float(left[~changed].mean())}

    p = pr.load()
    p = wf.lags(p)
    base = p[p.year <= 2020].groupby('parcref').S.mean()
    off = p[p.year.between(2021, 2025)].groupby('parcref').S.mean().rename('offset')
    f = pd.concat([shift, off], axis=1).dropna()
    f['changed'] = f['shift'] >= thr
    out['corr_shift_abs_offset'] = float(np.corrcoef(f['shift'], f.offset.abs())[0, 1])
    out['corr_shift_offset'] = float(np.corrcoef(f['shift'], f.offset)[0, 1])
    out['mean_offset_changed'] = float(f.offset[f.changed].mean()); out['mean_offset_other'] = float(f.offset[~f.changed].mean())
    out['mean_abs_offset_changed'] = float(f.offset[f.changed].abs().mean()); out['mean_abs_offset_other'] = float(f.offset[~f.changed].abs().mean())

    ch = set(f.index[f.changed])
    res = {}
    for lab, q in (('all fields', p), ('changed fields excluded', p[~p.parcref.isin(ch)])):
        res[lab] = {'legacy (pooled)': legacy(q)}
        sh = q[['parcref', 'year', 'S', 'cell_id_data', 'shock']].copy()
        sh['S'] = sh.groupby('parcref').S.transform(lambda v: RNG.permutation(v.values))
        res[lab]['season-shuffled placebo'] = legacy(wf.lags(sh))
        print(lab, {k: round(v['coef'], 3) for k, v in res[lab].items()}, flush=True)
    out['tests'] = res
    json.dump(out, open(os.path.join(RES, 'wp2_landuse_change.json'), 'w'), indent=1, default=float)
    L = ['# WP2 W3: land-use change from embeddings', '',
         'Specified in paper/outline.md on 17 October 2026 before running. Shift = distance between each field\'s mean '
         'AlphaEarth embedding 2017–2019 and 2023–2025; "changed" = top 5% nationally.', '',
         f"- Fields: {out['fields']:,}; changed: {out['changed']:,} (shift ≥ {out['threshold']:.3f}).",
         f"- **(a) Validation:** left cereals in CROME (cereal ≥ 2 of 3 years 2017–19, ≤ 1 of 3 in 2023–25): "
         f"{out['left_cereals_rate_changed']:.1%} of changed fields vs {out['left_cereals_rate_other']:.1%} of others.",
         f"- **(b) Lasting offset** (mean Sentinel-2 stress 2021–2025 against the 2017–2020 normal): correlation with the "
         f"shift {out['corr_shift_offset']:+.2f} (with its size {out['corr_shift_abs_offset']:+.2f}); mean offset "
         f"{out['mean_offset_changed']:+.2f} for changed fields vs {out['mean_offset_other']:+.2f} for others "
         f"(size {out['mean_abs_offset_changed']:.2f} vs {out['mean_abs_offset_other']:.2f}).", '',
         '**(c) Legacy test with and without changed fields** (cell × season effects, clustered by ERA5 cell):', '',
         '| Sample | pooled legacy | season-shuffled placebo |', '|---|---|---|'] + \
        [f"| {k} | {v['legacy (pooled)']['coef']:+.3f} | {v['season-shuffled placebo']['coef']:+.3f} |" for k, v in res.items()]
    open(os.path.join(RES, 'wp2_landuse_change.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
