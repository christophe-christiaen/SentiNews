"""X1 (results/lender/lender_baseline_protocol.md, protocol written 17 October 2026 before running): how much of the lender score's
back-tested skill comes from the 4-season normal shared by its features and its target?

Versions, on parcels with both Sentinel-2 and MODIS values, panel 2017-2026 in all three:
  V0 Sentinel-2, normal 2017-2020 (the published score)
  V1 MODIS, normal 2017-2020
  V2 MODIS, normal 2001-2016
Same features, targets, models and rolling-origin back-test as src/lender_score.py; only the stress index changes.
Reading (fixed in advance): V1 - V2 in AUC of the transparent score (hit hard next season) is the part due to the short
normal; if >= 0.03 the deck's figures are described as inflated and replaced by long-baseline figures.

Output  results/lender/lender_baseline_check.md, .json (aggregates only)
"""
import glob, json, os
import numpy as np, pandas as pd
import lender_score as ls

MODEL = 'Transparent score (no fitting)'


def modis_S(base):
    m = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(os.path.join(ls.D, 'modis_parcels', 'modis_*.csv')))],
                  ignore_index=True).drop_duplicates('parcref')
    long = []
    for k in ('july', 'peak'):
        x = m.melt(id_vars='parcref', value_vars=[c for c in m.columns if c.startswith(k + '_')], var_name='v', value_name=k)
        x['year'] = x.v.str[-4:].astype(int); long.append(x[['parcref', 'year', k]].set_index(['parcref', 'year']))
    p = pd.concat(long, axis=1).reset_index()
    out = {}
    for lab, (a, b) in base.items():
        st = p[p.year.between(a, b)].groupby('parcref')[['july', 'peak']].agg(['mean', 'std'])
        z = []
        for k in ('july', 'peak'):
            mu, sd = st[(k, 'mean')].reindex(p.parcref).values, st[(k, 'std')].reindex(p.parcref).values
            z.append((p[k].values - mu) / np.where(sd > 1e-4, sd, np.nan))
        out[lab] = p[['parcref', 'year']].assign(S=np.clip(np.nanmean(np.vstack(z), axis=0), -6, 6))
    return out


def main():
    s2 = pd.read_parquet(os.path.join(ls.D, 's2', 's2_parcel_year.parquet'),
                         columns=['parcref', 'year', 'ndvi_july_z', 'ndvi_peak_z', 'cell_id_data', 'dry_shock', 'heat_shock'])
    s2['S'] = s2[['ndvi_july_z', 'ndvi_peak_z']].mean(axis=1).clip(-6, 6)
    s2['shock'] = s2.dry_shock.fillna(False).astype(bool) | s2.heat_shock.fillna(False).astype(bool)
    s2 = s2[s2.year.between(2017, 2026)]
    mod = modis_S({'V1': (2017, 2020), 'V2': (2001, 2016)})
    common = set(s2.parcref) & set(mod['V2'].parcref)
    ls.log('common parcels', len(common))
    frame = s2[s2.parcref.isin(common)][['parcref', 'year', 'cell_id_data', 'shock', 'S']]
    versions = {'V0 · Sentinel-2, normal 2017–2020': frame}
    for k, lab in (('V1', 'V1 · MODIS, normal 2017–2020'), ('V2', 'V2 · MODIS, normal 2001–2016')):
        versions[lab] = frame.drop(columns='S').merge(mod[k], on=['parcref', 'year'], how='left')
    out, byyear = {}, {}
    for lab, f in versions.items():
        ls.log(lab)
        p = ls.features(f.copy())
        bt, _ = ls.backtest(p)
        summ = bt.groupby('model').mean(numeric_only=True).drop(columns='year')
        out[lab] = summ[['hit_next_auc', 'hit_next_lift', 'hit_next_base_rate', 'worst_next_auc', 'worst_next_lift']].round(4).to_dict('index')
        byyear[lab] = bt[bt.model == MODEL].set_index('year').hit_next_auc.round(4).to_dict()
    v1, v2 = out['V1 · MODIS, normal 2017–2020'][MODEL]['hit_next_auc'], out['V2 · MODIS, normal 2001–2016'][MODEL]['hit_next_auc']
    verdict = dict(v1_minus_v2=round(v1 - v2, 4), inflated=bool(v1 - v2 >= 0.03))
    json.dump({'parcels': len(common), 'summary': out, 'transparent_auc_by_year': byyear, 'verdict': verdict},
              open(os.path.join(ls.OUT, 'lender_baseline_check.json'), 'w'), indent=1, default=float)
    L = ['# Lender score under a long baseline (X1)', '',
         'Protocol in [lender_baseline_protocol.md](lender_baseline_protocol.md), written before running. Same features, '
         'targets and rolling-origin back-test (scoring seasons 2020–2025) as the published score; only the stress index '
         f'changes. {len(common):,} parcels with both Sentinel-2 and MODIS values; panel 2017–2026 in every version.', '',
         '## Mean over scoring seasons 2020–2025', '',
         '| Version | model | hit hard next season: AUC | lift (top 20%) | base rate | worst 20% of region: AUC |', '|---|---|---|---|---|---|']
    for lab, r in out.items():
        for m in ('Region only (baseline)', 'Current stress only (pilot rule)', MODEL, 'Fitted score (logistic)'):
            v = r[m]
            L.append(f"| {lab} | {m} | {v['hit_next_auc']:.3f} | {v['hit_next_lift']:.2f} | {v['hit_next_base_rate']:.1%} | {v['worst_next_auc']:.3f} |")
    L += ['', '## Transparent score by scoring season (AUC, hit hard next season)', '',
          '| Season | ' + ' | '.join(byyear) + ' |', '|---' * (len(byyear) + 1) + '|']
    for y in sorted(next(iter(byyear.values()))):
        L.append(f'| {y} | ' + ' | '.join(f'{byyear[k][y]:.3f}' for k in byyear) + ' |')
    L += ['', f"**Reading (fixed in advance):** V1 − V2 = {verdict['v1_minus_v2']:+.3f} AUC for the transparent score; "
          + ('at least 0.03, so the short normal inflates the published back-test.' if verdict['inflated'] else
             'below 0.03, so the short normal does not materially inflate the published back-test.'),
          '', 'Limits: MODIS pixels are 250 m and mix neighbouring fields; a 2001–2016 normal can drift by 2017–2026, so V2 '
          'is free of the in-panel shared error, not of every baseline effect.']
    open(os.path.join(ls.OUT, 'lender_baseline_check.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
