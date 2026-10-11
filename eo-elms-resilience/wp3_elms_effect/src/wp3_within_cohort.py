"""WP3 within-cohort comparison (decisions record, 11 October 2026; specified after the first results, before running).

Each contrast is formed inside each entry cohort (or cohort x season, as a check), so the cohort's base-season offset
cancels, then cohorts are combined with weights proportional to their parcel-seasons in the contrast. Base season g-1
for every season; after entry (main), before entry (event times -4 to -2) and after minus before.

Input   as wp3_did.py, plus wp3_elms_effect/data/matched_sample.parquet
Output  wp3_elms_effect/results/wp3_within_cohort.md, wp3_within_cohort.json
"""
import json, os
import numpy as np, pandas as pd
import wp3_did as w

PRE = [-4, -3, -2]


def within(E, pos, neg, by):
    """Sum over groups (cohort, or cohort x season) of pi_g * (mean over pos_g - mean over neg_g)."""
    TR = E.TR; nT = TR.nT.values
    keys = pd.MultiIndex.from_frame(TR[by]) if len(by) > 1 else pd.Index(TR[by[0]])
    codes, uniq = pd.factorize(keys)
    wv = np.zeros(len(TR)); parts = []
    for k in range(len(uniq)):
        m = codes == k
        p, n = pos & m, neg & m
        if nT[p].sum() and nT[n].sum():
            parts.append((p, n, nT[p].sum() + nT[n].sum()))
    tot = sum(x[2] for x in parts)
    for p, n, s in parts:
        wv[p] += s / tot / nT[p].sum(); wv[n] -= s / tot / nT[n].sum()
    return wv, len(parts)


def vectors(E, h, by):
    TR = E.TR
    sh, pv, e = TR.shock.values, TR.prev.values, TR.e.values
    B, A = (TR.fam == 'B').values, (TR.fam == 'A').values
    out = []
    for win in (np.isin(e, PRE), e >= 0):
        if h == 'H1':
            v, k = within(E, win & sh, win & ~sh, by)
        elif h == 'H2':
            v, k = within(E, win & ~sh & pv, win & ~sh & ~pv, by)
        else:
            vb, k1 = within(E, win & B & sh, win & B & ~sh, by)
            va, k2 = within(E, win & A & sh, win & A & ~sh, by)
            v, k = vb - va, min(k1, k2)
        out.append((v, k))
    (a, ka), (b, kb) = out
    return [a, b, b - a], (ka, kb)


def run(d, M, by, label, **kw):
    E1 = d.est('ndvi_july_z', pmask=M, universal=True, **kw)
    E2 = d.est('ndvi_peak_z', pmask=M, universal=True, **kw)
    res = {}
    for h, E in [('H1', E1), ('H2', E2), ('H3', E1)]:
        W, groups = vectors(E, h, by)
        th, V, G, _ = E.run(W)
        res[h] = {k: w.row(f'{h} {k}', th, V, i, G, int(E.TR.nT.values[W[i] != 0].sum()))
                  for i, k in enumerate(['before entry', 'after entry', 'after minus before'])}
        res[h]['groups'] = {'before': groups[0], 'after': groups[1]}
    w.log(label, {h: (round(res[h]['after entry']['est'], 3), round(res[h]['before entry']['est'], 3)) for h in res})
    return res


def main():
    d = w.Data()
    ms = pd.read_parquet(os.path.join(w.W3, 'data', 'matched_sample.parquet'))
    assert (ms.parcref.values == d.t.parcref.values).all()
    M = ms.in_matched_sample.values
    t = d.t
    main_ = run(d, M, ['g'], 'within cohort')
    hs = ('H1', 'H2', 'H3')
    for r, a in zip([main_[h]['after entry'] for h in hs], w.holm([main_[h]['after entry']['p'] for h in hs])):
        r['p_holm'] = float(a)
    for r, a in zip([main_[h]['after minus before'] for h in hs], w.holm([main_[h]['after minus before']['p'] for h in hs])):
        r['p_holm'] = float(a)
    checks = {'Within cohort x season': run(d, M, ['g', 't'], 'within cohort x season'),
              'Excluding 2017': run(d, M, ['g'], 'excl 2017', seasons=range(2018, 2026)),
              'Excluding Flood Zone 3 and deep peat': run(d, M & ~t.fz3.values & ~t.deep_peat.values, ['g'], 'excl fz3/peat'),
              '2026 version (cell x season strata, no crop)': run(d, M, ['g'], '2026', use_crop=False, seasons=range(2017, 2027)),
              'Unmatched full sample': run(d, None, ['g'], 'unmatched')}
    json.dump({'main': main_, 'checks': checks}, open(os.path.join(w.RES, 'wp3_within_cohort.json'), 'w'), indent=1, default=float)
    names = {'H1': 'H1 July NDVI, shock minus non-shock', 'H2': 'H2 peak NDVI, calm-after-shock minus calm-after-calm',
             'H3': 'H3 H1 contrast, family B minus family A'}
    c = lambda r: f"{r['est']:+.3f} ({r['se']:.3f})"
    L = ['# WP3 within-cohort comparison', '',
         'Specified in the decisions record **after the first results were seen, before this was run**; the last estimator '
         'version for this Sentinel-2 round. Read with [wp3_results.md](wp3_results.md) and '
         '[wp3_trend_adjusted.md](wp3_trend_adjusted.md).', '',
         'Each contrast is formed inside each entry cohort, so the cohort\'s base-season gap cancels, then cohorts are '
         'combined by their parcel-seasons. "Before entry" (2–4 seasons before) works as a placebo and should be near zero. '
         'Matched sample, cell × season × crop strata, SE clustered by ERA5 cell; estimate (SE).', '',
         '| Test | before entry | **after entry** | p (Holm) | after minus before | p (Holm) | cohorts (before / after) |',
         '|---|---|---|---|---|---|---|']
    for h in hs:
        r = main_[h]
        L.append(f"| {names[h]} | {c(r['before entry'])} | **{c(r['after entry'])}** | {r['after entry']['p_holm']:.3f} | "
                 f"{c(r['after minus before'])} | {r['after minus before']['p_holm']:.3f} | "
                 f"{r['groups']['before']} / {r['groups']['after']} |")
    L += ['', '## Checks: after entry; before entry in brackets', '', '| Check | H1 | H2 | H3 |', '|---|---|---|---|']
    for k, v in checks.items():
        L.append(f"| {k} | " + ' | '.join(f"{v[h]['after entry']['est']:+.3f} ± {1.96 * v[h]['after entry']['se']:.3f} "
                                          f"[{v[h]['before entry']['est']:+.3f}]" for h in hs) + ' |')
    open(os.path.join(w.RES, 'wp3_within_cohort.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
