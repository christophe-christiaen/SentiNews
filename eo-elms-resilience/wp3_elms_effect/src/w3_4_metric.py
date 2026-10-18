"""W3-4 (wp3_elms_effect/results/w3_4_metric_protocol.md, written before any model): a placebo-adjusted detection
metric. Same families, comparisons, sampling and leave-one-region-out model as option_detection.py.

  I  = AUC(pre + post) - AUC(pre)        incremental detection (primary)
  I0 = AUC(pre + 2020) - AUC(pre)        placebo increment (2020 is before every entry)
  I* = I - I0                            selection-corrected detection
Feature families: AlphaEarth (64-d); Sentinel-2 half-monthly NDVI/NDRE/NDMI (36). Paired bootstrap of parcels within
held-out regions (500) for intervals.

Output  wp3_elms_effect/results/w3_4_metric.md, .json
"""
import json, os
import numpy as np, pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
import option_detection as od

RES = od.RES
B = 500
RNG = np.random.default_rng(4)


def s2_years(years, keep):
    s = pd.read_parquet(os.path.join(od.D, 's2', 's2_parcel_year.parquet'), columns=['parcref', 'year'] + od.S2)
    s = s[s.year.isin(years) & s.parcref.isin(keep)]
    return s.groupby('parcref')[od.S2].mean()


def loro_pred(df, X):
    pred = np.full(len(df), np.nan)
    for r in sorted(df.region.unique()):
        te = (df.region == r).values
        if df.y[te].nunique() < 2 or df.y[~te].nunique() < 2:
            continue
        m = HistGradientBoostingClassifier(max_iter=200, random_state=0).fit(X[~te], df.y[~te])
        pred[te] = m.predict_proba(X[te])[:, 1]
    return pred


def boot_idx(df):
    """Paired bootstrap indices: resample parcels within each held-out region."""
    groups = [np.where(df.region.values == r)[0] for r in df.region.unique()]
    for _ in range(B):
        yield np.concatenate([RNG.choice(g, len(g)) for g in groups])


def assess(df, preds):
    y = df.y.values
    ok = np.all([np.isfinite(p) for p in preds.values()], axis=0)
    auc = {k: float(roc_auc_score(y[ok], p[ok])) for k, p in preds.items()}
    d = lambda a: {'I': a['pre+post'] - a['pre'], 'I0': a['pre+2020'] - a['pre'], 'G': a['post'] - a['pre']}
    point = d(auc); point['I*'] = point['I'] - point['I0']
    idx_ok = np.where(ok)[0]; sub = df.iloc[idx_ok].reset_index(drop=True)
    draws = {k: [] for k in ('I', 'I0', 'G', 'I*', 'post')}
    for ix in boot_idx(sub):
        yy = y[idx_ok][ix]
        if yy.min() == yy.max():
            continue
        a = {k: roc_auc_score(yy, p[idx_ok][ix]) for k, p in preds.items()}
        v = d(a); v['I*'] = v['I'] - v['I0']; v['post'] = a['post']
        for k in draws:
            draws[k].append(v[k])
    ci = {k: [float(np.quantile(v, 0.025)), float(np.quantile(v, 0.975))] for k, v in draws.items()}
    reg = {}
    for r in sorted(sub.region.unique()):
        m = (sub.region == r).values
        if sub.y[m].nunique() == 2:
            a = {k: roc_auc_score(sub.y[m], p[idx_ok][m]) for k, p in preds.items()}
            reg[r] = (a['pre+post'] - a['pre']) - (a['pre+2020'] - a['pre'])
    return dict(auc=auc, **point, ci=ci, n=int(ok.sum()), Istar_region_range=[float(min(reg.values())), float(max(reg.values()))])


def main():
    agr, never, mgmt = od.load()
    keep = set(agr.parcref) | set(never.parcref)
    od.log = print
    print('loading features', flush=True)
    feats = {'AlphaEarth': {'pre': od.emb_year([2017, 2018, 2019], keep), 'y2020': od.emb_year([2020], keep), 'post': od.emb_year([2025], keep)},
             'Sentinel-2': {'pre': s2_years([2017, 2018, 2019], keep), 'y2020': s2_years([2020], keep), 'post': s2_years([2025], keep)}}
    out = {}
    for fam, cs in od.FAMILIES.items():
        cs = set(cs)
        pos = agr[agr.codes.map(lambda c: len(c & cs) > 0)]
        comps = {'A': never}
        if fam != 'Management only (control)':
            comps['B'] = mgmt[~mgmt.parcref.isin(pos.parcref)]
        for clab, comp in comps.items():
            df = od.sample(pos, comp).reset_index(drop=True)
            for flab, F in feats.items():
                g = lambda k: F[k].reindex(df.parcref).values
                sets = {'pre': g('pre'), 'post': g('post'), 'pre+post': np.hstack([g('pre'), g('post')]),
                        'pre+2020': np.hstack([g('pre'), g('y2020')]), 'change': g('post') - g('pre')}
                preds = {k: loro_pred(df, X) for k, X in sets.items()}
                r = assess(df, {k: v for k, v in preds.items() if k != 'change'})
                ok = np.isfinite(preds['change'])
                r['auc_change'] = float(roc_auc_score(df.y.values[ok], preds['change'][ok]))
                out[f'{fam} | {clab} | {flab}'] = r
                print(fam, clab, flab, {k: round(r[k], 3) for k in ('I', 'I0', 'I*', 'G')}, flush=True)
    json.dump(out, open(os.path.join(RES, 'w3_4_metric.json'), 'w'), indent=1, default=float)
    report(out)


def report(out):
    fams = list(od.FAMILIES)
    ctrl = ['Buffer strips (control)', 'Management only (control)']
    L = ['# W3-4: a placebo-adjusted detection metric', '',
         'Protocol: [w3_4_metric_protocol.md](w3_4_metric_protocol.md), written before any model. I = AUC(pre + post) − '
         'AUC(pre); I₀ = AUC(pre + 2020) − AUC(pre) (2020 is before every entry); I* = I − I₀. G = AUC(post) − AUC(pre) '
         '(Paper 3). Comparison A: never-treated land; B: management-only scheme land. Leave-one-region-out; 95% intervals '
         'from a paired bootstrap of parcels within held-out regions.', '']
    for flab in ('AlphaEarth', 'Sentinel-2'):
        L += [f'## {flab}', '', '| Family | comp. | AUC pre | AUC post | G | I | I₀ | **I*** (95% CI) | I* range over regions |', '|---|---|---|---|---|---|---|---|---|']
        for fam in fams:
            for c in ('A', 'B'):
                k = f'{fam} | {c} | {flab}'
                if k not in out:
                    continue
                r = out[k]
                L.append(f"| {fam} | {c} | {r['auc']['pre']:.2f} | {r['auc']['post']:.2f} | {r['G']:+.3f} | {r['I']:+.3f} | {r['I0']:+.3f} | "
                         f"**{r['I*']:+.3f}** ({r['ci']['I*'][0]:+.3f} to {r['ci']['I*'][1]:+.3f}) | {r['Istar_region_range'][0]:+.3f} to {r['Istar_region_range'][1]:+.3f} |")
        # reading
        cal = {c: out[f'{c} | A | {flab}']['I*'] for c in ctrl}
        valid = all(abs(v) <= 0.02 for v in cal.values())
        det = [f for f in fams if f not in ctrl and f'{f} | B | {flab}' in out and out[f'{f} | B | {flab}']['ci']['I*'][0] > 0.02]
        inv = {f: (abs(out[f'{f} | A | {flab}']['I*'] - out[f'{f} | B | {flab}']['I*']), abs(out[f'{f} | A | {flab}']['auc']['post'] - out[f'{f} | B | {flab}']['auc']['post']))
               for f in fams if f not in ctrl and f'{f} | B | {flab}' in out}
        invariant = all(a < 0.03 for a, _ in inv.values())
        p3 = [f for f in fams if f not in ctrl and f'{f} | B | {flab}' in out and out[f'{f} | B | {flab}']['auc']['post'] >= 0.70 and out[f'{f} | B | {flab}']['G'] >= 0.10]
        L += ['', f'**Reading ({flab}, rules fixed in advance)**', '',
              f"- Calibration (negative controls vs never-treated, I* within ±0.02): " + '; '.join(f'{c} {v:+.3f}' for c, v in cal.items())
              + (' → **valid**.' if valid else ' → **fails calibration**.'),
              f"- Detectable beyond selection (I* 95% CI above 0.02, comparison B): {', '.join(det) if det else 'none'}.",
              f"- Paper 3 rule (AUC ≥ 0.70 and G ≥ 0.10, comparison B): {', '.join(p3) if p3 else 'none'}.",
              '- Selection-invariance (|I*(A) − I*(B)| vs |AUC post(A) − AUC post(B)|): '
              + '; '.join(f'{f} {a:.3f} vs {b:.3f}' for f, (a, b) in inv.items())
              + (' → **invariant** (all below 0.03).' if invariant else ' → **not invariant** for every family.'), '']
    open(os.path.join(RES, 'w3_4_metric.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
