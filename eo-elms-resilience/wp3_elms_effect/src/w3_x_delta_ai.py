"""Addendum 5, section 3 (wp3_elms_effect/results/w3_x_addendum5_products_protocol.md, run plan of 19 November 2026,
fixed before any statistic): what an AI embedding adds on top of all no-AI products for land-management detection.

  N        = Sentinel-2 indices (+ NDTI when --ndti) + Sentinel-1 VV/VH (22 half-months, farm seasons)
  dAI(E)   = I*(N + E) - I*(N), E in AlphaEarth, TESSERA, Presto
Frame of w3_4_model_comparison.py: families, samples, pre 2018-2019, I0 2020, post 2025, leave-one-region-out, seed 29,
1,000 paired resamples of parcels within held-out regions (registered); 10 km blocks reported beside (#9).

Usage   python w3_x_delta_ai.py --parcels OUT.parquet       write the sample parcel list (for the NDTI extraction)
        python w3_x_delta_ai.py [--ndti] CACHE_DIR           run (interim without --ndti; registered with it)
Output  wp3_elms_effect/results/w3_x_delta_ai[_interim].md, .json (aggregates only)
"""
import argparse, glob, itertools, json, os, pickle
import numpy as np, pandas as pd
from sklearn.metrics import roc_auc_score
import option_detection as od
import w3_4_metric as m
import w3_4_model_comparison as mc

RES = mc.RES
B = 1000
EMB = ['AlphaEarth', 'TESSERA', 'Presto']
S1DIR = os.path.join(od.D, 's1', 'gee_local')
NDTI = os.path.join(od.D, 's2', 'gee_local_ndti')


def samples():
    agr, never, mgmt = od.load()
    out = {}
    for fam, cs in od.FAMILIES.items():
        cs = set(cs)
        pos = agr[agr.codes.map(lambda c: len(c & cs) > 0)]
        comps = {'A': never} if fam in mc.CONTROLS else {'B': mgmt[~mgmt.parcref.isin(pos.parcref)], 'A': never}
        for k, comp in comps.items():
            out[(fam, k)] = od.sample(pos, comp).reset_index(drop=True)
    return out, set(agr.parcref) | set(never.parcref)


def s1_seasons(seasons, keep):
    cols = [f'{b}_p{k:02d}' for k in range(1, 23) for b in ('vv', 'vh')]
    parts = []
    for s in seasons:
        for f in glob.glob(os.path.join(S1DIR, f's1_*_{s}.csv')):
            d = pd.read_csv(f, usecols=['parcref'] + cols)
            parts.append(d[d.parcref.isin(keep)])
    return pd.concat(parts).groupby('parcref')[cols].mean()


def ndti_years(years, keep):
    parts = [pd.read_csv(f) for y in years for f in glob.glob(os.path.join(NDTI, f'ndti_*_{y}.csv'))]
    d = pd.concat(parts); d = d[d.parcref.isin(keep)]
    cols = [c for c in d.columns if c.startswith('ndti_')]
    return d.groupby('parcref')[cols].mean()


def features(keep, with_ndti):
    E = mc.features(keep)                                   # AlphaEarth, Sentinel-2, TESSERA, Presto as published
    N = {}
    for k, yrs, seas in (('pre', [2018, 2019], [2018, 2019]), ('y2020', [2020], [2020]), ('post', [2025], [2025])):
        parts = [E['Sentinel-2'][k], s1_seasons(seas, keep)]
        if with_ndti:
            parts.append(ndti_years(yrs, keep))
        N[k] = pd.concat(parts, axis=1)
    return N, {e: E[e] for e in EMB}


def preds(df, N, Em, cache, key):
    f = os.path.join(cache, f'dai_{key}.pkl')
    if os.path.exists(f):
        return pickle.load(open(f, 'rb'))
    P = {}
    for name in ['N'] + EMB:
        def g(k):
            X = N[k].reindex(df.parcref).values
            return X if name == 'N' else np.hstack([X, Em[name][k].reindex(df.parcref).values])
        sets = {'pre': g('pre'), 'pre+post': np.hstack([g('pre'), g('post')]), 'pre+2020': np.hstack([g('pre'), g('y2020')])}
        P[name] = {k: m.loro_pred(df, X) for k, X in sets.items()}
    pickle.dump(P, open(f, 'wb'))
    return P


def istar(y, p, ix):
    a = {k: roc_auc_score(y[ix], v[ix]) for k, v in p.items()}
    return (a['pre+post'] - a['pre']) - (a['pre+2020'] - a['pre'])


def groups_parcel(df, idx):
    reg = df.region.values[idx]
    return [[np.array([i]) for i in idx[reg == r]] for r in np.unique(reg)]


def groups_block(df, idx, xy, size=10_000):
    reg = df.region.values[idx]
    p = df.parcref.values[idx]
    key = pd.Series(reg).astype(str) + '|' + (xy.loc[p, 'x'].values // size).astype(int).astype(str) + '_' + (xy.loc[p, 'y'].values // size).astype(int).astype(str)
    out = []
    for r in np.unique(reg):
        mk = reg == r
        out.append([idx[mk][g] for g in pd.Series(np.arange(mk.sum())).groupby(key.values[mk]).indices.values()])
    return out


def draws(y, P, groups):
    rng = np.random.default_rng(29)
    D = {n: [] for n in P}
    for _ in range(B):
        ix = np.concatenate([np.concatenate([g[i] for i in rng.integers(0, len(g), len(g))]) for g in groups])
        if y[ix].min() == y[ix].max():
            continue
        for n in P:
            D[n].append(istar(y, P[n], ix))
    return {n: np.array(v) for n, v in D.items()}


def assess(df, P, xy):
    y = df.y.values
    ok = np.all([np.isfinite(v) for mp in P.values() for v in mp.values()], axis=0); idx = np.where(ok)[0]
    point = {n: istar(y, P[n], idx) for n in P}
    out = {'n': int(len(idx)), 'Istar': point}
    for lab, G in (('parcel', groups_parcel(df, idx)), ('block_10km', groups_block(df, idx, xy))):
        D = draws(y, P, G)
        r = {'Istar_ci': {n: [float(np.quantile(D[n], .025)), float(np.quantile(D[n], .975))] for n in P}, 'dAI': {}}
        ps = []
        for e in EMB:
            d = D[e] - D['N']
            ps.append(float(min(1.0, 2 * min((d <= 0).mean(), (d >= 0).mean()))))
        order = np.argsort(ps); adj = np.empty(3); run = 0.0
        for rank, i in enumerate(order):
            run = max(run, (3 - rank) * ps[i]); adj[i] = min(1.0, run)
        for rank, i in enumerate(order):
            e = EMB[i]; d = D[e] - D['N']; a = 0.05 / (3 - rank)
            r['dAI'][e] = dict(est=point[e] - point['N'], p=ps[i], p_holm=float(adj[i]),
                               ci_holm=[float(np.quantile(d, a / 2)), float(np.quantile(d, 1 - a / 2))], level=1 - a)
        out[lab] = r
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('cache', nargs='?'); ap.add_argument('--ndti', action='store_true')
    ap.add_argument('--parcels'); a = ap.parse_args()
    S, keep = samples()
    if a.parcels:
        pp = pd.concat([d[['parcref']] for d in S.values()]).drop_duplicates()
        xy = pd.read_parquet(os.path.join(od.D, 'parcels', 'parcel_panel.parquet'), columns=['parcref', 'x', 'y'])
        pp.merge(xy, on='parcref').drop_duplicates('parcref').to_parquet(a.parcels, index=False)
        print(len(pp), 'sample parcels written'); return
    os.makedirs(a.cache, exist_ok=True)
    tag = '' if a.ndti else '_interim'
    keep_s = set(pd.concat([d.parcref for d in S.values()]))
    N, Em = features(keep_s, a.ndti)
    print('features', {k: v.shape for k, v in N.items()}, flush=True)
    xy = pd.read_parquet(os.path.join(od.D, 'parcels', 'parcel_panel.parquet'), columns=['parcref', 'x', 'y']).drop_duplicates('parcref').set_index('parcref')
    res = {}
    for (fam, comp), df in S.items():
        P = preds(df, N, Em, a.cache, f'{tag}_{fam}_{comp}'.replace(' ', '_'))
        res[f'{fam} | {comp}'] = assess(df, P, xy)
        print(fam, comp, {n: round(v, 3) for n, v in res[f'{fam} | {comp}']['Istar'].items()}, flush=True)
    prods = ['N'] + EMB
    calib = {n: {c: res[f'{c} | A']['Istar'][n] for c in mc.CONTROLS} for n in prods}
    passes = {n: all(abs(v) <= 0.02 for v in calib[n].values()) for n in prods}
    read = {}
    for f in mc.OPTIONS:
        rb, ra = res[f'{f} | B'], res[f'{f} | A']
        inv = {n: abs(ra['Istar'][n] - rb['Istar'][n]) for n in prods}
        read[f] = {e: dict(adds=bool(rb['parcel']['dAI'][e]['ci_holm'][0] > 0 and passes[e] and inv[e] < 0.03),
                           ci_above_zero=bool(rb['parcel']['dAI'][e]['ci_holm'][0] > 0), calibrated=passes[e], invariance=inv[e])
                   for e in EMB}
        read[f]['N_invariance'] = inv['N']
    json.dump({'with_ndti': a.ndti, 'results': res, 'calibration': calib, 'calibration_pass': passes, 'reading': read},
              open(os.path.join(RES, f'w3_x_delta_ai{tag}.json'), 'w'), indent=1, default=float)
    report(res, calib, passes, read, a.ndti, tag)


def report(res, calib, passes, read, ndti, tag):
    s = lambda v: f'{v:+.3f}'
    nn = 'Sentinel-2 indices + NDTI + Sentinel-1' if ndti else 'Sentinel-2 indices + Sentinel-1 (**interim: no NDTI**)'
    L = [f'# Addendum 5 · ΔAI: what AI embeddings add on top of the no-AI products{" (interim)" if not ndti else ""}', '',
         f'Run plan in the record of [w3_x_addendum5_products_protocol.md](w3_x_addendum5_products_protocol.md) (19 November 2026, '
         f'fixed before any statistic). N = {nn}. ΔAI(E) = I*(N + E) − I*(N), comparison B (management-only scheme land). '
         'Paired bootstrap of parcels within held-out regions (registered), Holm over the three embeddings within each family; '
         '10 km block intervals (#9) beside. E **adds to the indices** if the Holm-adjusted interval lies above zero, N + E '
         'passes calibration (both controls within ±0.02 against never-treated land) and invariance (|I*(A) − I*(B)| < 0.03).', '']
    if not ndti:
        L += ['**Interim.** NDTI is still being extracted. The registered reading is the run with NDTI; this one is labelled interim.', '']
    L += ['## Calibration (controls against never-treated land, I*)', '', '| Product | Buffer strips | Management only | passes ±0.02 |', '|---|---|---|---|']
    for n in calib:
        L.append(f"| {'N' if n == 'N' else 'N + ' + n} | {s(calib[n]['Buffer strips (control)'])} | {s(calib[n]['Management only (control)'])} | {'yes' if passes[n] else 'no'} |")
    L += ['', '## ΔAI by option family (comparison B)', '',
          '| Family | I*(N) | Embedding | ΔAI | Holm-adjusted interval (parcels) | p (Holm) | 10 km block interval | invariance | Reading |', '|---|---|---|---|---|---|---|---|---|']
    for f in mc.OPTIONS:
        r = res[f'{f} | B']
        for e in EMB:
            d, db = r['parcel']['dAI'][e], r['block_10km']['dAI'][e]
            rd = read[f][e]
            verdict = '**adds to the indices**' if rd['adds'] else ('adds nothing shown' if not rd['ci_above_zero'] else
                      'interval above zero, but ' + ('fails calibration' if not rd['calibrated'] else 'fails invariance'))
            L.append(f"| {f} | {s(r['Istar']['N'])} | {e} | {s(d['est'])} | {s(d['ci_holm'][0])} to {s(d['ci_holm'][1])} | {d['p_holm']:.3f} | "
                     f"{s(db['ci_holm'][0])} to {s(db['ci_holm'][1])} | {rd['invariance']:.3f} | {verdict} |")
    L += ['', f"Invariance of N alone: " + '; '.join(f"{f} {read[f]['N_invariance']:.3f}" for f in mc.OPTIONS) + '.']
    open(os.path.join(RES, f'w3_x_delta_ai{tag}.md'), 'w').write('\n'.join(L) + '\n')


if __name__ == '__main__':
    main()
