"""WP3 trend-adjusted confirmatory tests (pre-registration section 8, check 1; method in the decisions record, decided
after the first results were seen because the pre-trend test and the placebo failed).

Each contrast is estimated with one fixed base season (g - 1), separately before entry (event times -4 to -2) and
after entry (event time >= 0), on the same matched sample and strata as wp3_did.py. Adjusted = after minus before
(a triple difference), cluster-robust by ERA5 cell through the same influence functions; Holm over H1-H3.

Input   as wp3_did.py, plus wp3_elms_effect/data/matched_sample.parquet
Output  wp3_elms_effect/results/wp3_trend_adjusted.md, wp3_trend_adjusted.json
"""
import json, os
import numpy as np, pandas as pd
import wp3_did as w

PRE = [-4, -3, -2]


def sets(TR):
    post = (TR.e >= 0).values
    pre = TR.e.isin(PRE).values
    return pre, post


def contrasts(E, y):
    """Weight vectors: [pre, post, adjusted] for the hypothesis contrast on this outcome."""
    TR = E.TR; pre, post = sets(TR)
    sh, pv = TR.shock.values, TR.prev.values
    if y == 'H2':
        f = lambda m: E.weights(m & ~sh & pv, m & ~sh & ~pv)
    elif y == 'H1':
        f = lambda m: E.weights(m & sh, m & ~sh)
    else:                                   # H3: B contrast minus A contrast
        B, A = (TR.fam == 'B').values, (TR.fam == 'A').values
        f = lambda m: E.weights(m & B & sh, m & B & ~sh) - E.weights(m & A & sh, m & A & ~sh)
    a, b = f(pre), f(post)
    return [a, b, b - a]


def run(d, M, label, **kw):
    E1 = d.est('ndvi_july_z', pmask=M, universal=True, **kw)
    E2 = d.est('ndvi_peak_z', pmask=M, universal=True, **kw)
    out = {}
    for h, E in [('H1', E1), ('H2', E2), ('H3', E1)]:
        W = contrasts(E, h)
        th, V, G, _ = E.run(W)
        pre, post = sets(E.TR)
        out[h] = {k: w.row(f'{h} {k}', th, V, i, G, int(E.TR.nT.values[(W[i] != 0)].sum()))
                  for i, k in enumerate(['before entry', 'after entry', 'adjusted'])}
        if label == 'main':
            _, Vb, Gb, Ib = E.run(W, clusters=d.block50[E.TR.cell.values])
            r = w.RNG.choice([-1.0, 1.0], size=(1999, Ib.shape[0]))
            out[h]['adjusted']['se_block50'] = float(np.std(r @ Ib[:, 2]))
    w.log(label, {h: round(out[h]['adjusted']['est'], 3) for h in out})
    return out


def main():
    d = w.Data()
    ms = pd.read_parquet(os.path.join(w.W3, 'data', 'matched_sample.parquet'))
    assert (ms.parcref.values == d.t.parcref.values).all()
    M = ms.in_matched_sample.values
    main_ = run(d, M, 'main')
    for r, a in zip([main_[h]['adjusted'] for h in ('H1', 'H2', 'H3')],
                    w.holm([main_[h]['adjusted']['p'] for h in ('H1', 'H2', 'H3')])):
        r['p_holm'] = float(a)
    t = d.t
    checks = {
        'Excluding 2017': run(d, M, 'excl 2017', seasons=range(2018, 2026)),
        'Excluding Flood Zone 3 and deep peat': run(d, M & ~t.fz3.values & ~t.deep_peat.values, 'excl fz3/peat'),
        '2026 version (cell x season strata, no crop)': run(d, M, '2026', use_crop=False, seasons=range(2017, 2027)),
        'Unmatched full sample': run(d, None, 'unmatched'),
        'Shock: rain only': run(d, M, 'rain only', shock={**w.MAIN_SHOCK, 'rain_only': True}),
        'Shock: soil moisture only': run(d, M, 'soil only', shock={**w.MAIN_SHOCK, 'soil_only': True}),
    }
    json.dump({'main': main_, 'checks': checks}, open(os.path.join(w.RES, 'wp3_trend_adjusted.json'), 'w'), indent=1, default=float)
    names = {'H1': 'H1 July NDVI, shock minus non-shock', 'H2': 'H2 peak NDVI, calm-after-shock minus calm-after-calm',
             'H3': 'H3 H1 contrast, family B minus family A'}
    L = ['# WP3 trend-adjusted results', '',
         'Fallback named in the pre-registration (section 8, check 1) after the pre-trend test and placebo failed; method '
         'fixed in the decisions record **after the first results were seen**. Read alongside '
         '[wp3_results.md](wp3_results.md), not instead of it.', '',
         'Each contrast uses one base season (the season before entry) and is computed before entry (seasons 2–4 before) '
         'and after entry. Adjusted = after minus before: the change in how agreement land responds to shocks, net of '
         'any difference that was already there. Matched sample, cell × season × crop strata, SE clustered by ERA5 cell.', '',
         '## Confirmatory tests, trend-adjusted (Holm over three)', '',
         '| Test | before entry | after entry | **adjusted** | SE | 95% CI | p | p (Holm) |', '|---|---|---|---|---|---|---|---|']
    for h in ('H1', 'H2', 'H3'):
        a, b, c = (main_[h][k] for k in ('before entry', 'after entry', 'adjusted'))
        L.append(f"| {names[h]} | {a['est']:+.3f} ({a['se']:.3f}) | {b['est']:+.3f} ({b['se']:.3f}) | **{c['est']:+.3f}** | "
                 f"{c['se']:.3f} | [{c['lo']:+.3f}, {c['hi']:+.3f}] | {c['p']:.3f} | {c['p_holm']:.3f} |")
    L += ['', '50 km wild block bootstrap SE of the adjusted estimates: ' +
          ', '.join(f"{h} {main_[h]['adjusted']['se_block50']:.3f}" for h in ('H1', 'H2', 'H3')) + '.', '',
          '## Checks (adjusted estimate, SE in brackets)', '', '| Check | H1 | H2 | H3 |', '|---|---|---|---|']
    for k, v in checks.items():
        L.append(f"| {k} | " + ' | '.join(f"{v[h]['adjusted']['est']:+.3f} ({v[h]['adjusted']['se']:.3f})" for h in ('H1', 'H2', 'H3')) + ' |')
    open(os.path.join(w.RES, 'wp3_trend_adjusted.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
