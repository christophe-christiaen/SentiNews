"""First look at the embedding demo (6 sites x 2019/2025): can frozen AlphaEarth / TESSERA embeddings
(1) tell grassland from arable SFI land, (2) pick out herbal leys, and (3) does 2019->2025 change differ by action?

Validation is leave-one-site-out (spatially held out). Scheme points are parcel points from the live layers,
so labels are declared actions, not verified ones. Writes results/embedding_probe/.
"""
import json, os
import numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import balanced_accuracy_score, roc_auc_score
import statsmodels.formula.api as smf

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
EMB = os.path.join(ROOT, 'shared', 'data', 'embeddings')
OUT = os.path.join(ROOT, 'wp3_elms_effect', 'results', 'embedding_probe')
BACKENDS = {'AlphaEarth (20 m, 64-d)': 'alphaearth_ov1', 'TESSERA (10 m, 128-d)': 'tessera'}

GROUPS = {  # SFI action families (codes after stripping the _26 suffix and the C prefix of SFI24 "C" variants)
    'Herbal leys': ['SAM3', 'CSAM3'],
    'Low-input / legume grassland': ['LIG1', 'LIG2', 'CLIG3', 'NUM2', 'CNUM2'],
    'Arable actions': ['IPM3', 'IPM4', 'CIPM3', 'CIPM4', 'SAM2', 'CSAM2', 'SOH1', 'SOH3', 'AHL2', 'AHL3', 'PRF1'],
    'Hedgerows and boundaries': ['HRW1', 'HRW2', 'HRW3', 'CHRW1', 'CHRW2', 'CHRW3', 'BND1', 'BND2'],
    'Whole-farm soil plan': ['SAM1', 'CSAM1'],
}
CODE2GROUP = {c: g for g, cs in GROUPS.items() for c in cs}


def load(backend, year):
    d = pd.read_parquet(os.path.join(EMB, backend, f'samples_{year}.parquet'))
    cols = [c for c in d.columns if c[0] in 'AT' and c[1:].isdigit()]
    d['group'] = d.code.astype('string').str.replace('_26', '', regex=False).map(CODE2GROUP)
    d.loc[d.source == 'control', 'group'] = 'Random pixels'
    d.loc[d.source == 'es_options', 'group'] = 'ES options (2009-14)'
    d.loc[d.source == 'cs_options', 'group'] = 'CS options (2021-25)'
    d['siteid'] = d.region + ' ' + d.site.astype(str)
    return d, cols


def loso_probe(d, cols, pos, neg):
    """Binary linear probe, leave-one-site-out. One row per point location and label."""
    sub = d[d.group.isin(pos + neg)].copy()
    sub['yy'] = sub.group.isin(pos).astype(int)
    sub = sub.drop_duplicates(['x', 'y', 'yy'])
    sub = sub[~sub.duplicated(['x', 'y'], keep=False)]  # drop locations carrying both labels
    pred = pd.Series(np.nan, index=sub.index)
    for s in sub.siteid.unique():
        tr, te = sub.siteid != s, sub.siteid == s
        if sub.yy[tr].nunique() < 2 or te.sum() == 0:
            continue
        m = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, C=0.1, class_weight='balanced'))
        m.fit(sub.loc[tr, cols].astype('float32'), sub.yy[tr])
        pred[te] = m.predict_proba(sub.loc[te, cols].astype('float32'))[:, 1]
    ok = pred.notna()
    y, p = sub.yy[ok], pred[ok]
    return dict(n_pos=int(y.sum()), n_neg=int((1 - y).sum()), auc=round(roc_auc_score(y, p), 3),
                bal_acc=round(balanced_accuracy_score(y, p > 0.5), 3))


def change(backend):
    a, cols = load(backend, 2019)
    b, _ = load(backend, 2025)
    key = ['source', 'code', 'x', 'y', 'siteid']
    a = a.drop_duplicates(key); b = b.drop_duplicates(key)
    m = a[key + ['group', 'start_year'] + cols].merge(b[key + cols], on=key, suffixes=('_19', '_25'))
    A = m[[c + '_19' for c in cols]].astype('float64').values
    B = m[[c + '_25' for c in cols]].astype('float64').values
    cos = (A * B).sum(1) / (np.linalg.norm(A, axis=1) * np.linalg.norm(B, axis=1))
    m['dist'] = 1 - cos
    # controls are re-drawn per run, so match them across years by location only if they coincide; otherwise
    # use each year's random pixels as a separate baseline (below)
    return m[key + ['group', 'start_year', 'dist']]


def main():
    os.makedirs(OUT, exist_ok=True)
    res = {'probes': [], 'change': {}, 'change_reg': {}}
    tasks = [
        ('Grassland vs arable SFI land', ['Low-input / legume grassland'], ['Arable actions']),
        ('Herbal leys vs arable SFI land', ['Herbal leys'], ['Arable actions']),
        ('Herbal leys vs other grassland SFI land', ['Herbal leys'], ['Low-input / legume grassland']),
        ('Scheme parcels vs random pixels', ['CS options (2021-25)', 'ES options (2009-14)'] + list(GROUPS), ['Random pixels']),
    ]
    changes = {}
    for name, be in BACKENDS.items():
        for y in (2019, 2025):
            d, cols = load(be, y)
            for t, pos, neg in tasks:
                r = loso_probe(d, cols, pos, neg)
                res['probes'].append(dict(backend=name, year=y, task=t, **r))
                print(name, y, t, r, flush=True)
        c = change(be)
        changes[name] = c
        g = c.groupby('group').dist.agg(['mean', 'count']).round(4)
        res['change'][name] = g.to_dict(orient='index')
        # within-site comparison against the whole-farm soil plan group (no land change expected), site fixed effects
        cc = c[c.group.isin(list(GROUPS) + ['CS options (2021-25)', 'ES options (2009-14)'])].copy()
        cc['rel'] = cc.dist / c.dist.mean()
        fit = smf.ols("rel ~ C(group, Treatment('Whole-farm soil plan')) + C(siteid)", cc).fit(cov_type='HC1')
        res['change_reg'][name] = {k.split('[T.')[1].rstrip(']'): dict(coef=round(v, 3), p=round(fit.pvalues[k], 4))
                                   for k, v in fit.params.items() if 'group' in k}
        print(name, res['change_reg'][name], flush=True)

    # agreement between the two models on per-point change
    k = ['source', 'code', 'x', 'y']
    j = changes[list(BACKENDS)[0]].merge(changes[list(BACKENDS)[1]], on=k, suffixes=('_ae', '_ts'))
    res['change_agreement'] = dict(n=len(j), spearman=round(j.dist_ae.corr(j.dist_ts, method='spearman'), 3))
    print(res['change_agreement'])
    json.dump(res, open(os.path.join(OUT, 'embedding_probe.json'), 'w'), indent=1)

    lines = ['# Embedding demo: first probes (6 sites, 2019 and 2025)', '',
             'Leave-one-site-out linear probes on frozen embeddings. Labels are declared SFI actions from the live layers.', '',
             '| Task | Model | Year | n (pos / neg) | AUC | Balanced acc. |', '|---|---|---|---|---|---|']
    for p in res['probes']:
        lines.append(f"| {p['task']} | {p['backend']} | {p['year']} | {p['n_pos']} / {p['n_neg']} | {p['auc']} | {p['bal_acc']} |")
    lines += ['', '## 2019 → 2025 change (cosine distance), mean by group', '',
              '| Group | ' + ' | '.join(BACKENDS) + ' |', '|---|' + '---|' * len(BACKENDS)]
    groups = sorted(set().union(*[res['change'][b].keys() for b in BACKENDS]))
    for g in groups:
        lines.append(f'| {g} | ' + ' | '.join(
            f"{res['change'][b][g]['mean']:.3f} (n={res['change'][b][g]['count']})" if g in res['change'][b] else '–'
            for b in BACKENDS) + ' |')
    lines += ['', 'Relative change vs whole-farm soil plan points, site fixed effects (1.0 = mean change):', '',
              '| Group | ' + ' | '.join(BACKENDS) + ' |', '|---|' + '---|' * len(BACKENDS)]
    for g in res['change_reg'][list(BACKENDS)[0]]:
        lines.append(f'| {g} | ' + ' | '.join(
            f"{res['change_reg'][b][g]['coef']:+.3f} (p={res['change_reg'][b][g]['p']:.3g})" for b in BACKENDS) + ' |')
    lines += ['', f"Per-point change, AlphaEarth vs TESSERA: Spearman {res['change_agreement']['spearman']} "
              f"(n={res['change_agreement']['n']})."]
    open(os.path.join(OUT, 'embedding_probe.md'), 'w').write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()
