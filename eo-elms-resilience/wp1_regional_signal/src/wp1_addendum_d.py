"""WP1 protocol addendum D (written 17 October 2026, before running): AlphaEarth embeddings.
  D1 nowcast-valid: previous-year embedding of the season's crop fields (region median, 5 PCs fitted per fold)
     added to the first-run Sentinel-2 + weather model, seasons 2018-2025
  D2 after-season, not a nowcast: the season's own embedding, alone and added to Sentinel-2 + weather
Leave-one-year-out; adoption rule for D1 in the protocol.

Output  wp1_regional_signal/results/wp1_addendum_d.md, wp1_addendum_d.json
"""
import glob, json, os
import numpy as np, pandas as pd
from sklearn.decomposition import PCA
import wp1_nowcast as w

RES, D = w.RES, w.D
BANDS = [f'A{i:02d}' for i in range(64)]
YEARS = list(range(2018, 2026))
DRY = [2018, 2020, 2022, 2025]
NPC = 5


def embeddings_by_year():
    out = {}
    for y in range(2017, 2026):
        parts = [pd.read_parquet(f) for f in sorted(glob.glob(os.path.join(D, 'embeddings', 'parcels', f'aef_*_{y}.parquet')))]
        out[y] = pd.concat(parts, ignore_index=True).drop_duplicates('parcref').set_index('parcref')
    return out


def region_embeddings(s2, emb, lag):
    rows = []
    for y in YEARS:
        e = emb[y - lag]
        x = s2[(s2.year == y) & s2.crop.isin(w.CROPS)][['parcref', 'crop', 'region']]
        x = x.join(e, on='parcref').dropna(subset=['A00'])
        g = x.groupby(['crop', 'region'])[BANDS].median().reset_index(); g['year'] = y
        rows.append(g)
    return pd.concat(rows, ignore_index=True)


def loyo(df, cols, use_emb):
    rows = []
    for yv in YEARS:
        tr, te = df[df.year != yv].copy(), df[df.year == yv].copy()
        c = list(cols)
        if use_emb:
            pca = PCA(n_components=NPC, random_state=0).fit(tr[BANDS].values)
            for k, (a, b) in enumerate(zip(pca.transform(tr[BANDS].values).T, pca.transform(te[BANDS].values).T)):
                tr[f'pc{k}'], te[f'pc{k}'] = a, b
            c += [f'pc{k}' for k in range(NPC)]
        a, b = w.anomalies(tr, te, c)
        ytr = (tr.yield_t_ha - tr.groupby('region').yield_t_ha.transform('mean')).values
        sc, m, _ = w.fit_ridge(a.values, ytr, tr.year.values)
        obs = te.yield_t_ha.values - tr.groupby('region').yield_t_ha.mean().reindex(te.region).values
        rows.append(pd.DataFrame({'region': te.region.values, 'year': yv, 'obs': obs, 'pred': m.predict(sc.transform(b.values))}))
    return pd.concat(rows, ignore_index=True)


def score(r):
    s = w.scores(r)
    e = r.groupby('year')[['obs', 'pred']].mean(); err = e.pred - e.obs
    s['mae_dry'] = float(err.reindex(DRY).abs().mean())
    return s


def main():
    y = w.yields(); s2 = w.panel()
    feats = w.region_features(s2, 'crop')
    emb = embeddings_by_year()
    prev, same = region_embeddings(s2, emb, 1), region_embeddings(s2, emb, 0)
    out = {}
    for crop in w.CROPS:
        base = feats[feats.crop == crop].merge(y[y.crop == crop], on=['crop', 'region', 'year'])
        base = base[base.year.isin(YEARS)].reset_index(drop=True)
        bp = base.merge(prev, on=['crop', 'region', 'year'])
        bs = base.merge(same, on=['crop', 'region', 'year'])
        for cut, k in [('mid-July', 9), ('end of August', 12)]:
            first = w.eo_cols(k) + w.WEATHER
            res = {'first run (2018–2025)': score(loyo(bp, first, False)),
                   'D1 + previous-year embedding': score(loyo(bp, first, True)),
                   'D2 own-year embedding alone (after season)': score(loyo(bs, [], True)),
                   'D2 + own-year embedding (after season)': score(loyo(bs, first, True))}
            r0, r1 = res['first run (2018–2025)'], res['D1 + previous-year embedding']
            res['D1 adopt'] = bool(r1['r2'] >= r0['r2'] + 0.02 and r1['mae_dry'] <= r0['mae_dry'])
            out[f'{crop} | {cut}'] = res
            w.log(crop, cut, {kk: round(v['r2'], 3) for kk, v in res.items() if isinstance(v, dict)}, 'adopt D1', res['D1 adopt'])
    json.dump(out, open(os.path.join(RES, 'wp1_addendum_d.json'), 'w'), indent=1, default=float)
    L = ['# WP1 addendum D: AlphaEarth embeddings', '',
         'Protocol addendum D ([protocol.md](protocol.md)), written 17 October 2026 before running. Leave-one-year-out over '
         '2018–2025 (2017 has no previous-year embedding). D2 uses the season\'s own embedding, which includes months '
         'after harvest: it is an after-season comparison, **not a nowcast**.', '',
         '| Crop, cutoff | first run | D1 + previous-year embedding | D2 own-year alone (after season) | D2 + own-year (after season) | D1 dry-year MAE (first → D1) | adopt D1 |',
         '|---|---|---|---|---|---|---|']
    for k, r in out.items():
        a, b = r['first run (2018–2025)'], r['D1 + previous-year embedding']
        L.append(f"| {k} | {a['r2']:+.2f} | {b['r2']:+.2f} | {r['D2 own-year embedding alone (after season)']['r2']:+.2f} | "
                 f"{r['D2 + own-year embedding (after season)']['r2']:+.2f} | {a['mae_dry']:.2f} → {b['mae_dry']:.2f} | {'yes' if r['D1 adopt'] else 'no'} |")
    L += ['', 'R² of the yield anomaly, out of sample. Embeddings: region median over the season\'s crop fields, 5 principal '
          'components fitted on each fold\'s training years.']
    open(os.path.join(RES, 'wp1_addendum_d.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
